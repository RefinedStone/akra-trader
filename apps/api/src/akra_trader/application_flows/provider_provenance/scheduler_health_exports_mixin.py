from __future__ import annotations

import csv
from copy import deepcopy
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import io
import json
import math
import re
from typing import Any
from typing import Iterable
from typing import Mapping

from akra_trader.domain.models import *  # noqa: F403


def _serialize_stitched_scheduler_narrative_json_value(value: Any) -> str:
  if isinstance(value, datetime):
    return value.isoformat()
  raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


class ProviderProvenanceSchedulerHealthExportsMixin:
  def export_replay_intent_alias_audits(
    self,
    *,
    export_format: str = "json",
    alias_id: str | None = None,
    template_key: str | None = None,
    action: str | None = None,
    retention_policy: str | None = None,
    source_tab_id: str | None = None,
    search: str | None = None,
  ) -> dict[str, Any]:
    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported replay alias audit export format")
    audit_records = self.list_replay_intent_alias_audits(
      alias_id=alias_id,
      template_key=template_key,
      action=action,
      retention_policy=retention_policy,
      source_tab_id=source_tab_id,
      search=search,
      limit=None,
    )
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_replay_intent_alias_audit_record,
    )

    serialized_items = [
      serialize_replay_intent_alias_audit_record(record)
      for record in audit_records
    ]
    exported_at = self._clock().isoformat()
    normalized_template_key = template_key.strip() if isinstance(template_key, str) and template_key.strip() else "all"
    base_filename = f"replay-alias-audits-{normalized_template_key}"
    if normalized_format == "json":
      content = json.dumps(
        {
          "exported_at": exported_at,
          "filters": {
            "alias_id": alias_id,
            "template_key": template_key,
            "action": action,
            "retention_policy": retention_policy,
            "source_tab_id": source_tab_id,
            "search": search,
          },
          "total": len(serialized_items),
          "items": serialized_items,
        },
        indent=2,
        sort_keys=True,
      )
      return {
        "content": content,
        "content_type": "application/json",
        "exported_at": exported_at,
        "filename": f"{base_filename}.json",
        "format": "json",
        "record_count": len(serialized_items),
      }
    buffer = io.StringIO()
    fieldnames = (
      "audit_id",
      "alias_id",
      "action",
      "template_key",
      "template_label",
      "redaction_policy",
      "retention_policy",
      "source_tab_id",
      "source_tab_label",
      "detail",
      "recorded_at",
      "expires_at",
      "alias_created_at",
      "alias_expires_at",
      "alias_revoked_at",
    )
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for item in serialized_items:
      writer.writerow({fieldname: item.get(fieldname) for fieldname in fieldnames})
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": exported_at,
      "filename": f"{base_filename}.csv",
      "format": "csv",
      "record_count": len(serialized_items),
    }

  def download_replay_intent_alias_audit_export_job(
    self,
    job_id: str,
  ) -> dict[str, Any]:
    record = self.get_replay_intent_alias_audit_export_job(job_id)
    artifact_content = record.content
    if record.artifact_id:
      artifact_record = self.get_replay_intent_alias_audit_export_artifact(record.artifact_id)
      artifact_content = artifact_record.content
    self._record_replay_intent_alias_audit_export_job_event(record=record, action="downloaded")
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_replay_intent_alias_audit_export_job_record,
    )

    return serialize_replay_intent_alias_audit_export_job_record(
      record,
      include_content=True,
      content=artifact_content,
    )

  def get_provider_provenance_export_analytics(
    self,
    *,
    focus_key: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    provider_label: str | None = None,
    vendor_field: str | None = None,
    market_data_provider: str | None = None,
    venue: str | None = None,
    requested_by_tab_id: str | None = None,
    status: str | None = None,
    search: str | None = None,
    result_limit: int = 12,
    window_days: int = 14,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_export_job_record,
    )

    self._prune_provider_provenance_export_artifact_records()
    self._prune_provider_provenance_export_job_records()
    self._prune_provider_provenance_export_job_audit_records()
    records = self._filter_provider_provenance_export_job_records(
      focus_key=focus_key,
      symbol=symbol,
      timeframe=timeframe,
      provider_label=provider_label,
      vendor_field=vendor_field,
      market_data_provider=market_data_provider,
      venue=venue,
      requested_by_tab_id=requested_by_tab_id,
      status=status,
      search=search,
    )
    normalized_result_limit = max(1, min(result_limit, 50))
    matching_job_ids = {record.job_id for record in records}
    audit_records = tuple(
      audit_record
      for audit_record in self._list_provider_provenance_export_job_audit_records()
      if audit_record.job_id in matching_job_ids
    )
    download_stats_by_job: dict[str, dict[str, Any]] = {}
    for audit_record in audit_records:
      if audit_record.action != "downloaded":
        continue
      job_stats = download_stats_by_job.setdefault(
        audit_record.job_id,
        {"download_count": 0, "last_downloaded_at": None},
      )
      job_stats["download_count"] += 1
      last_downloaded_at = job_stats["last_downloaded_at"]
      if (
        last_downloaded_at is None
        or audit_record.recorded_at > last_downloaded_at
      ):
        job_stats["last_downloaded_at"] = audit_record.recorded_at

    def build_rollup_entry(
      *,
      key: str,
      label: str,
      records_for_rollup: list[ProviderProvenanceExportJobRecord],
      extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
      download_count = sum(
        int(download_stats_by_job.get(record.job_id, {}).get("download_count", 0))
        for record in records_for_rollup
      )
      download_timestamps = [
        download_stats_by_job[record.job_id]["last_downloaded_at"]
        for record in records_for_rollup
        if record.job_id in download_stats_by_job
        and download_stats_by_job[record.job_id].get("last_downloaded_at") is not None
      ]
      exported_timestamps = [
        record.exported_at or record.created_at
        for record in records_for_rollup
      ]
      provider_labels_for_rollup = self._normalize_provider_provenance_export_strings(
        provider
        for record in records_for_rollup
        for provider in record.provider_labels
      )
      vendor_fields_for_rollup = self._normalize_provider_provenance_export_strings(
        field
        for record in records_for_rollup
        for field in record.vendor_fields
      )
      payload = {
        "key": key,
        "label": label,
        "export_count": len(records_for_rollup),
        "result_count": sum(record.result_count for record in records_for_rollup),
        "provider_provenance_count": sum(
          record.provider_provenance_count
          for record in records_for_rollup
        ),
        "download_count": download_count,
        "focus_count": len({
          record.focus_key
          for record in records_for_rollup
          if isinstance(record.focus_key, str) and record.focus_key
        }),
        "requested_by_tab_count": len({
          record.requested_by_tab_id
          for record in records_for_rollup
          if isinstance(record.requested_by_tab_id, str) and record.requested_by_tab_id
        }),
        "provider_labels": list(provider_labels_for_rollup),
        "vendor_fields": list(vendor_fields_for_rollup),
        "last_exported_at": max(exported_timestamps).isoformat() if exported_timestamps else None,
        "last_downloaded_at": max(download_timestamps).isoformat() if download_timestamps else None,
      }
      if extra:
        payload.update(extra)
      return payload

    provider_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    vendor_field_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    focus_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    requester_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    for record in records:
      for provider in record.provider_labels:
        provider_rollups.setdefault(provider, []).append(record)
      for field_name in record.vendor_fields:
        vendor_field_rollups.setdefault(field_name, []).append(record)
      focus_rollups.setdefault(record.focus_key or "unknown_focus", []).append(record)
      requester_rollups.setdefault(
        record.requested_by_tab_id or "unknown_requester",
        [],
      ).append(record)

    focus_items = [
      build_rollup_entry(
        key=focus_key_value,
        label=records_for_rollup[0].focus_label or focus_key_value,
        records_for_rollup=records_for_rollup,
        extra={
          "symbol": records_for_rollup[0].symbol,
          "timeframe": records_for_rollup[0].timeframe,
          "market_data_provider": records_for_rollup[0].market_data_provider,
          "venue": records_for_rollup[0].venue,
        },
      )
      for focus_key_value, records_for_rollup in focus_rollups.items()
    ]
    provider_items = [
      build_rollup_entry(
        key=provider_value,
        label=provider_value,
        records_for_rollup=records_for_rollup,
      )
      for provider_value, records_for_rollup in provider_rollups.items()
    ]
    vendor_field_items = [
      build_rollup_entry(
        key=field_value,
        label=field_value,
        records_for_rollup=records_for_rollup,
      )
      for field_value, records_for_rollup in vendor_field_rollups.items()
    ]
    requester_items = [
      build_rollup_entry(
        key=requester_value,
        label=(
          records_for_rollup[0].requested_by_tab_label
          or records_for_rollup[0].requested_by_tab_id
          or requester_value
        ),
        records_for_rollup=records_for_rollup,
      )
      for requester_value, records_for_rollup in requester_rollups.items()
    ]

    def sort_rollup_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
      return sorted(
        items,
        key=lambda item: (
          int(item["provider_provenance_count"]),
          int(item["export_count"]),
          item["label"],
        ),
        reverse=True,
      )

    all_provider_labels = self._normalize_provider_provenance_export_strings(
      provider
      for record in records
      for provider in record.provider_labels
    )
    all_vendor_fields = self._normalize_provider_provenance_export_strings(
      field
      for record in records
      for field in record.vendor_fields
    )
    all_market_data_providers = self._normalize_provider_provenance_export_strings(
      record.market_data_provider
      for record in records
    )
    all_venues = self._normalize_provider_provenance_export_strings(record.venue for record in records)
    all_timeframes = self._normalize_provider_provenance_export_strings(record.timeframe for record in records)
    all_requested_by_tab_ids = self._normalize_provider_provenance_export_strings(
      record.requested_by_tab_id
      for record in records
    )
    all_statuses = self._normalize_provider_provenance_export_strings(record.status for record in records)

    recent_exports = list(records[:normalized_result_limit])
    time_series = self._build_provider_provenance_export_time_series(
      records=records,
      audit_records=audit_records,
      window_days=window_days,
      now=self._clock(),
    )
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_export_job_record,
    )

    return {
      "generated_at": self._clock().isoformat(),
      "query": {
        "focus_key": focus_key,
        "symbol": symbol,
        "timeframe": timeframe,
        "provider_label": provider_label,
        "vendor_field": vendor_field,
        "market_data_provider": market_data_provider,
        "venue": venue,
        "requested_by_tab_id": requested_by_tab_id,
        "status": status,
        "search": search,
        "result_limit": normalized_result_limit,
        "window_days": time_series["window_days"],
      },
      "totals": {
        "export_count": len(records),
        "result_count": sum(record.result_count for record in records),
        "provider_provenance_count": sum(
          record.provider_provenance_count
          for record in records
        ),
        "download_count": sum(
          int(job_stats.get("download_count", 0))
          for job_stats in download_stats_by_job.values()
        ),
        "unique_focus_count": len({
          record.focus_key
          for record in records
          if isinstance(record.focus_key, str) and record.focus_key
        }),
        "provider_label_count": len(all_provider_labels),
        "vendor_field_count": len(all_vendor_fields),
        "market_data_provider_count": len(all_market_data_providers),
        "requester_count": len(all_requested_by_tab_ids),
      },
      "available_filters": {
        "provider_labels": list(all_provider_labels),
        "vendor_fields": list(all_vendor_fields),
        "market_data_providers": list(all_market_data_providers),
        "venues": list(all_venues),
        "timeframes": list(all_timeframes),
        "requested_by_tab_ids": list(all_requested_by_tab_ids),
        "statuses": list(all_statuses),
      },
      "rollups": {
        "providers": sort_rollup_items(provider_items)[:5],
        "vendor_fields": sort_rollup_items(vendor_field_items)[:5],
        "focuses": sort_rollup_items(focus_items)[:6],
        "requesters": sort_rollup_items(requester_items)[:5],
      },
      "time_series": time_series,
      "recent_exports": [
        serialize_provider_provenance_export_job_record(record)
        for record in recent_exports
      ],
    }

  def download_provider_provenance_export_job(
    self,
    job_id: str,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    record = self.get_provider_provenance_export_job(job_id)
    artifact_content = record.content
    if record.artifact_id:
      artifact_record = self.get_provider_provenance_export_artifact(record.artifact_id)
      artifact_content = artifact_record.content
    self._record_provider_provenance_export_job_event(
      record=record,
      action="downloaded",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_export_job_record,
    )

    return serialize_provider_provenance_export_job_record(
      record,
      include_content=True,
      content=artifact_content,
    )

  @classmethod
  def _build_provider_provenance_scheduler_health_hourly_drill_down(
    cls,
    *,
    records: tuple[ProviderProvenanceSchedulerHealthRecord, ...],
    bucket_key: str | None,
    history_limit: int,
  ) -> dict[str, Any] | None:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health_record,
    )

    bucket_start = cls._resolve_provider_provenance_scheduler_bucket_start(bucket_key)
    if bucket_start is None:
      return None
    bucket_end = bucket_start + timedelta(days=1)
    selected_records = tuple(
      sorted(
        (
          record
          for record in records
          if bucket_start <= cls._normalize_provider_provenance_export_bucket_start(record.recorded_at)
          < bucket_end
        ),
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )
    normalized_history_limit = max(1, min(history_limit, 100))
    health_status_series: list[dict[str, Any]] = []
    lag_trend_series: list[dict[str, Any]] = []

    for hour_offset in range(24):
      hour_start = bucket_start + timedelta(hours=hour_offset)
      hour_end = hour_start + timedelta(hours=1)
      hour_records = tuple(
        sorted(
          (
            record
            for record in selected_records
            if hour_start <= (record.recorded_at.astimezone(UTC) if record.recorded_at.tzinfo is not None else record.recorded_at.replace(tzinfo=UTC))
            < hour_end
          ),
          key=lambda record: (record.recorded_at, record.record_id),
        )
      )
      counts_by_status = {
        "healthy": 0,
        "lagging": 0,
        "failed": 0,
        "disabled": 0,
        "starting": 0,
      }
      for record in hour_records:
        counts_by_status[record.status] = counts_by_status.get(record.status, 0) + 1
      dominant_status, dominant_count = max(
        counts_by_status.items(),
        key=lambda item: (item[1], item[0]),
      )
      latest_record = hour_records[-1] if hour_records else None
      lag_values = [max(record.max_due_lag_seconds, 0) for record in hour_records]
      due_counts = [max(record.due_report_count, 0) for record in hour_records]
      bucket_hour_key = hour_start.isoformat()
      bucket_hour_label = hour_start.strftime("%H:00")
      executed_report_count = sum(record.last_executed_count for record in hour_records)
      failure_count = sum(1 for record in hour_records if record.status == "failed")
      health_status_series.append(
        {
          "bucket_key": bucket_hour_key,
          "bucket_label": bucket_hour_label,
          "started_at": hour_start.isoformat(),
          "ended_at": hour_end.isoformat(),
          "cycle_count": len(hour_records),
          "healthy_count": counts_by_status["healthy"],
          "lagging_count": counts_by_status["lagging"],
          "failed_count": counts_by_status["failed"],
          "disabled_count": counts_by_status["disabled"],
          "starting_count": counts_by_status["starting"],
          "dominant_status": dominant_status if dominant_count > 0 else "no_data",
          "dominant_count": dominant_count,
          "latest_status": latest_record.status if latest_record is not None else "no_data",
          "latest_summary": latest_record.summary if latest_record is not None else "",
          "executed_report_count": executed_report_count,
        }
      )
      lag_trend_series.append(
        {
          "bucket_key": bucket_hour_key,
          "bucket_label": bucket_hour_label,
          "started_at": hour_start.isoformat(),
          "ended_at": hour_end.isoformat(),
          "cycle_count": len(hour_records),
          "peak_lag_seconds": max(lag_values) if lag_values else 0,
          "latest_lag_seconds": lag_values[-1] if lag_values else 0,
          "average_lag_seconds": round(sum(lag_values) / len(lag_values), 1) if lag_values else 0.0,
          "peak_due_report_count": max(due_counts) if due_counts else 0,
          "latest_due_report_count": due_counts[-1] if due_counts else 0,
          "failure_count": failure_count,
          "executed_report_count": executed_report_count,
        }
      )

    peak_cycle_bucket = max(
      health_status_series,
      key=lambda item: (
        int(item["cycle_count"]),
        int(item["failed_count"]),
        item["bucket_key"],
      ),
      default=None,
    )
    peak_lag_bucket = max(
      lag_trend_series,
      key=lambda item: (
        int(item["peak_lag_seconds"]),
        int(item["peak_due_report_count"]),
        item["bucket_key"],
      ),
      default=None,
    )
    latest_health_bucket = health_status_series[-1] if health_status_series else None
    latest_lag_bucket = lag_trend_series[-1] if lag_trend_series else None

    return {
      "bucket_key": bucket_start.date().isoformat(),
      "bucket_label": bucket_start.strftime("%b %d"),
      "bucket_size": "hour",
      "window_started_at": bucket_start.isoformat(),
      "window_ended_at": bucket_end.isoformat(),
      "total_record_count": len(selected_records),
      "history_limit": normalized_history_limit,
      "history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in selected_records[:normalized_history_limit]
      ],
      "health_status": {
        "series": health_status_series,
        "summary": {
          "peak_cycle_bucket_key": peak_cycle_bucket["bucket_key"] if peak_cycle_bucket is not None else None,
          "peak_cycle_bucket_label": peak_cycle_bucket["bucket_label"] if peak_cycle_bucket is not None else None,
          "peak_cycle_count": int(peak_cycle_bucket["cycle_count"]) if peak_cycle_bucket is not None else 0,
          "latest_bucket_key": latest_health_bucket["bucket_key"] if latest_health_bucket is not None else None,
          "latest_bucket_label": latest_health_bucket["bucket_label"] if latest_health_bucket is not None else None,
          "latest_status": latest_health_bucket["latest_status"] if latest_health_bucket is not None else "no_data",
          "latest_cycle_count": int(latest_health_bucket["cycle_count"]) if latest_health_bucket is not None else 0,
        },
      },
      "lag_trend": {
        "series": lag_trend_series,
        "summary": {
          "peak_lag_bucket_key": peak_lag_bucket["bucket_key"] if peak_lag_bucket is not None else None,
          "peak_lag_bucket_label": peak_lag_bucket["bucket_label"] if peak_lag_bucket is not None else None,
          "peak_lag_seconds": int(peak_lag_bucket["peak_lag_seconds"]) if peak_lag_bucket is not None else 0,
          "latest_bucket_key": latest_lag_bucket["bucket_key"] if latest_lag_bucket is not None else None,
          "latest_bucket_label": latest_lag_bucket["bucket_label"] if latest_lag_bucket is not None else None,
          "latest_lag_seconds": int(latest_lag_bucket["latest_lag_seconds"]) if latest_lag_bucket is not None else 0,
          "latest_due_report_count": int(latest_lag_bucket["latest_due_report_count"]) if latest_lag_bucket is not None else 0,
          "latest_failure_count": int(latest_lag_bucket["failure_count"]) if latest_lag_bucket is not None else 0,
        },
      },
    }

  def get_provider_provenance_scheduler_health_analytics(
    self,
    *,
    status: str | None = None,
    window_days: int = 14,
    history_limit: int = 12,
    drilldown_bucket_key: str | None = None,
    drilldown_history_limit: int = 24,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_record,
    )

    self._prune_provider_provenance_scheduler_health_records()
    normalized_status = self._normalize_provider_provenance_scheduler_health_status(status)
    records = tuple(
      record
      for record in self._list_provider_provenance_scheduler_health_records()
      if normalized_status is None or record.status == normalized_status
    )
    normalized_history_limit = max(1, min(history_limit, 50))
    time_series = self._build_provider_provenance_scheduler_health_time_series(
      records=records,
      window_days=window_days,
      now=self._clock(),
    )
    drill_down = self._build_provider_provenance_scheduler_health_hourly_drill_down(
      records=records,
      bucket_key=drilldown_bucket_key,
      history_limit=drilldown_history_limit,
    )
    all_statuses = tuple(
      sorted(
        {
          record.status
          for record in self._list_provider_provenance_scheduler_health_records()
          if isinstance(record.status, str) and record.status
        }
      )
    )
    current_snapshot = self.get_provider_provenance_scheduler_health()
    return {
      "generated_at": self._clock().isoformat(),
      "query": {
        "status": normalized_status,
        "window_days": time_series["window_days"],
        "history_limit": normalized_history_limit,
        "drilldown_bucket_key": (
          drill_down["bucket_key"]
          if isinstance(drill_down, dict)
          else None
        ),
        "drilldown_history_limit": max(1, min(drilldown_history_limit, 100)),
      },
      "current": serialize_provider_provenance_scheduler_health(current_snapshot),
      "totals": {
        "record_count": len(records),
        "healthy_count": sum(1 for record in records if record.status == "healthy"),
        "lagging_count": sum(1 for record in records if record.status == "lagging"),
        "failed_count": sum(1 for record in records if record.status == "failed"),
        "disabled_count": sum(1 for record in records if record.status == "disabled"),
        "starting_count": sum(1 for record in records if record.status == "starting"),
        "executed_report_count": sum(record.last_executed_count for record in records),
        "peak_lag_seconds": max((record.max_due_lag_seconds for record in records), default=0),
        "peak_due_report_count": max((record.due_report_count for record in records), default=0),
      },
      "available_filters": {
        "statuses": list(all_statuses),
      },
      "time_series": time_series,
      "drill_down": drill_down,
      "recent_history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in records[:normalized_history_limit]
      ],
    }
