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


class ProviderProvenanceSchedulerHealthReconstructionMixin:
  def _build_provider_provenance_scheduler_occurrence_reconstruction_context(
    self,
    *,
    alert_category: str,
    detected_at: datetime,
    resolved_at: datetime | None = None,
    narrative_mode: str = "matched_status",
    history_limit: int = 25,
    drilldown_history_limit: int = 24,
    all_records: tuple[ProviderProvenanceSchedulerHealthRecord, ...] | None = None,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_category = self._normalize_provider_provenance_scheduler_alert_category(alert_category)
    normalized_narrative_mode = self._normalize_provider_provenance_scheduler_narrative_mode(
      narrative_mode,
    )
    target_status = "failed" if normalized_category == "scheduler_failure" else "lagging"
    detected_at_utc = self._normalize_provider_provenance_scheduler_export_datetime(
      detected_at,
      field_name="detected_at",
    )
    resolved_at_utc = (
      self._normalize_provider_provenance_scheduler_export_datetime(
        resolved_at,
        field_name="resolved_at",
      )
      if resolved_at is not None
      else None
    )
    if resolved_at_utc is not None and resolved_at_utc < detected_at_utc:
      raise ValueError("resolved_at must be on or after detected_at for scheduler export reconstruction.")
    if normalized_narrative_mode == "mixed_status_post_resolution" and resolved_at_utc is None:
      raise ValueError("mixed_status_post_resolution requires a resolved scheduler alert row.")
    if all_records is None:
      self._prune_provider_provenance_scheduler_health_records()
      ordered_records = tuple(
        sorted(
          self._list_provider_provenance_scheduler_health_records(),
          key=lambda record: (record.recorded_at, record.record_id),
        )
      )
    else:
      ordered_records = tuple(
        sorted(
          all_records,
          key=lambda record: (record.recorded_at, record.record_id),
        )
      )
    occurrence_window_end = resolved_at_utc or max(
      (record.recorded_at for record in ordered_records),
      default=detected_at_utc,
    )
    occurrence_records = tuple(
      record
      for record in ordered_records
      if detected_at_utc <= record.recorded_at <= occurrence_window_end
    )
    matching_records = tuple(
      record
      for record in occurrence_records
      if record.status == target_status
    )
    if not matching_records:
      raise LookupError("No scheduler health history could be reconstructed for the selected alert row.")
    latest_matching_record = max(
      matching_records,
      key=lambda record: (record.recorded_at, record.record_id),
    )
    current_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
      latest_matching_record,
    )
    normalized_history_limit = max(1, min(history_limit, 200))
    normalized_drilldown_history_limit = max(1, min(drilldown_history_limit, 100))
    occurrence_window_days = max(
      3,
      min(
        int((occurrence_window_end.date() - detected_at_utc.date()).days) + 1,
        90,
      ),
    )
    occurrence_drilldown_bucket_key = latest_matching_record.recorded_at.date().isoformat()
    recent_matching_records = tuple(
      sorted(
        matching_records,
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )
    selected_occurrence_history_payload = {
      "query": {
        "status": target_status,
        "limit": normalized_history_limit,
        "offset": 0,
      },
      "items": recent_matching_records[:normalized_history_limit],
      "total": len(matching_records),
      "returned": min(len(matching_records), normalized_history_limit),
      "has_more": len(matching_records) > normalized_history_limit,
      "next_offset": normalized_history_limit if len(matching_records) > normalized_history_limit else None,
      "previous_offset": None,
    }
    selected_occurrence_payload = {
      "status": target_status,
      "current": serialize_provider_provenance_scheduler_health(current_snapshot),
      "history_page": serialize_provider_provenance_scheduler_health_history(
        current_snapshot,
        selected_occurrence_history_payload,
      ),
      "record_count": len(matching_records),
      "window_record_count": len(occurrence_records),
    }

    export_records = matching_records
    export_status: str | None = target_status
    export_window_end = occurrence_window_end
    export_snapshot = current_snapshot
    export_window_days = occurrence_window_days
    export_drilldown_bucket_key = occurrence_drilldown_bucket_key
    next_occurrence_detected_at: datetime | None = None
    mixed_status_narrative_payload: dict[str, Any] | None = None
    post_resolution_records: tuple[ProviderProvenanceSchedulerHealthRecord, ...] = ()

    if normalized_narrative_mode == "mixed_status_post_resolution":
      next_target_status_record = next(
        (
          record
          for record in ordered_records
          if record.recorded_at > resolved_at_utc
          and record.status == target_status
        ),
        None,
      )
      next_occurrence_detected_at = (
        next_target_status_record.recorded_at
        if next_target_status_record is not None
        else None
      )
      export_records = tuple(
        record
        for record in ordered_records
        if detected_at_utc <= record.recorded_at
        and (
          next_occurrence_detected_at is None
          or record.recorded_at < next_occurrence_detected_at
        )
      )
      latest_export_record = max(
        export_records,
        key=lambda record: (record.recorded_at, record.record_id),
      )
      export_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
        latest_export_record,
      )
      export_status = None
      export_window_end = latest_export_record.recorded_at
      export_window_days = max(
        3,
        min(
          int((export_window_end.date() - detected_at_utc.date()).days) + 1,
          90,
        ),
      )
      export_drilldown_bucket_key = latest_export_record.recorded_at.date().isoformat()
      post_resolution_records = tuple(
        record
        for record in export_records
        if resolved_at_utc is not None and record.recorded_at >= resolved_at_utc
      )
      recent_post_resolution_records = tuple(
        sorted(
          post_resolution_records,
          key=lambda record: (record.recorded_at, record.record_id),
          reverse=True,
        )
      )
      post_resolution_history_payload = {
        "query": {
          "status": None,
          "limit": normalized_history_limit,
          "offset": 0,
        },
        "items": recent_post_resolution_records[:normalized_history_limit],
        "total": len(post_resolution_records),
        "returned": min(len(post_resolution_records), normalized_history_limit),
        "has_more": len(post_resolution_records) > normalized_history_limit,
        "next_offset": (
          normalized_history_limit
          if len(post_resolution_records) > normalized_history_limit
          else None
        ),
        "previous_offset": None,
      }
      mixed_status_narrative_payload = {
        "mode": "mixed_status_post_resolution",
        "window_started_at": detected_at_utc.isoformat(),
        "window_ended_at": export_window_end.isoformat(),
        "resolution_at": resolved_at_utc.isoformat(),
        "next_occurrence_detected_at": (
          next_occurrence_detected_at.isoformat()
          if next_occurrence_detected_at is not None
          else None
        ),
        "available_statuses": list(
          sorted(
            {
              record.status
              for record in export_records
              if isinstance(record.status, str) and record.status
            }
          )
        ),
        "latest_status": latest_export_record.status,
        "latest_summary": latest_export_record.summary,
        "current": serialize_provider_provenance_scheduler_health(export_snapshot),
        "selected_occurrence": selected_occurrence_payload,
        "status_sequence": list(
          self._build_provider_provenance_scheduler_status_narrative_segments(
            records=export_records,
            resolution_at=resolved_at_utc,
          )
        ),
        "post_resolution_history": serialize_provider_provenance_scheduler_health_history(
          export_snapshot,
          post_resolution_history_payload,
        ),
      }

    time_series = self._build_provider_provenance_scheduler_health_time_series(
      records=export_records,
      window_days=export_window_days,
      now=export_window_end,
    )
    drill_down = self._build_provider_provenance_scheduler_health_hourly_drill_down(
      records=export_records,
      bucket_key=export_drilldown_bucket_key,
      history_limit=normalized_drilldown_history_limit,
    )
    all_statuses = tuple(sorted({record.status for record in export_records if record.status}))
    history_payload = {
      "query": {
        "status": export_status,
        "limit": normalized_history_limit,
        "offset": 0,
      },
      "items": tuple(
        sorted(
          export_records,
          key=lambda record: (record.recorded_at, record.record_id),
          reverse=True,
        )
      )[:normalized_history_limit],
      "total": len(export_records),
      "returned": min(len(export_records), normalized_history_limit),
      "has_more": len(export_records) > normalized_history_limit,
      "next_offset": normalized_history_limit if len(export_records) > normalized_history_limit else None,
      "previous_offset": None,
    }
    analytics_payload = {
      "query": {
        "status": export_status,
        "window_days": time_series["window_days"],
        "history_limit": min(normalized_history_limit, 50),
        "drilldown_bucket_key": (
          drill_down["bucket_key"]
          if isinstance(drill_down, dict)
          else None
        ),
        "drilldown_history_limit": normalized_drilldown_history_limit,
        "reconstruction_mode": "resolved_alert_row",
        "narrative_mode": normalized_narrative_mode,
        "alert_category": normalized_category,
        "occurrence_status": target_status,
        "alert_detected_at": detected_at_utc.isoformat(),
        "alert_resolved_at": occurrence_window_end.isoformat(),
        "narrative_window_ended_at": export_window_end.isoformat(),
        "next_occurrence_detected_at": (
          next_occurrence_detected_at.isoformat()
          if next_occurrence_detected_at is not None
          else None
        ),
      },
      "current": serialize_provider_provenance_scheduler_health(export_snapshot),
      "totals": {
        "record_count": len(export_records),
        "healthy_count": sum(1 for record in export_records if record.status == "healthy"),
        "lagging_count": sum(1 for record in export_records if record.status == "lagging"),
        "failed_count": sum(1 for record in export_records if record.status == "failed"),
        "disabled_count": sum(1 for record in export_records if record.status == "disabled"),
        "starting_count": sum(1 for record in export_records if record.status == "starting"),
        "executed_report_count": sum(record.last_executed_count for record in export_records),
        "peak_lag_seconds": max((record.max_due_lag_seconds for record in export_records), default=0),
        "peak_due_report_count": max((record.due_report_count for record in export_records), default=0),
      },
      "available_filters": {
        "statuses": list(all_statuses),
      },
      "time_series": time_series,
      "drill_down": drill_down,
      "recent_history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in history_payload["items"][:min(normalized_history_limit, 50)]
      ],
    }
    reconstruction_payload = {
      "mode": "resolved_alert_row",
      "narrative_mode": normalized_narrative_mode,
      "alert_category": normalized_category,
      "alert_status": target_status,
      "alert_detected_at": detected_at_utc.isoformat(),
      "alert_resolved_at": occurrence_window_end.isoformat(),
      "matched_record_count": len(matching_records),
      "occurrence_window_record_count": len(occurrence_records),
      "window_record_count": len(export_records),
      "current_record_id": (
        history_payload["items"][0].record_id
        if history_payload["items"]
        else latest_matching_record.record_id
      ),
      "latest_window_status": (
        history_payload["items"][0].status
        if history_payload["items"]
        else target_status
      ),
      "next_occurrence_detected_at": (
        next_occurrence_detected_at.isoformat()
        if next_occurrence_detected_at is not None
        else None
      ),
      "selected_occurrence_record_count": len(matching_records),
    }
    return {
      "normalized_category": normalized_category,
      "normalized_narrative_mode": normalized_narrative_mode,
      "target_status": target_status,
      "detected_at": detected_at_utc,
      "resolved_at": resolved_at_utc,
      "occurrence_window_end": occurrence_window_end,
      "occurrence_records": occurrence_records,
      "matching_records": matching_records,
      "selected_occurrence_payload": selected_occurrence_payload,
      "export_records": export_records,
      "export_status": export_status,
      "export_window_end": export_window_end,
      "export_snapshot": export_snapshot,
      "next_occurrence_detected_at": next_occurrence_detected_at,
      "mixed_status_narrative_payload": mixed_status_narrative_payload,
      "post_resolution_records": post_resolution_records,
      "history_payload": history_payload,
      "analytics_payload": analytics_payload,
      "reconstruction_payload": reconstruction_payload,
    }

  def reconstruct_provider_provenance_scheduler_health_export(
    self,
    *,
    alert_category: str,
    detected_at: datetime,
    resolved_at: datetime | None = None,
    narrative_mode: str = "matched_status",
    export_format: str = "json",
    history_limit: int = 25,
    drilldown_history_limit: int = 24,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported provider provenance scheduler health export format.")
    context = self._build_provider_provenance_scheduler_occurrence_reconstruction_context(
      alert_category=alert_category,
      detected_at=detected_at,
      resolved_at=resolved_at,
      narrative_mode=narrative_mode,
      history_limit=history_limit,
      drilldown_history_limit=drilldown_history_limit,
    )
    normalized_category = context["normalized_category"]
    normalized_narrative_mode = context["normalized_narrative_mode"]
    resolved_at_utc = context["resolved_at"]
    history_payload = context["history_payload"]
    export_snapshot = context["export_snapshot"]
    reconstruction_payload = context["reconstruction_payload"]
    analytics_payload = {
      "generated_at": self._clock().isoformat(),
      **context["analytics_payload"],
    }
    mixed_status_narrative_payload = context["mixed_status_narrative_payload"]
    selected_occurrence_payload = context["selected_occurrence_payload"]
    if normalized_format == "json":
      payload: dict[str, Any] = {
        "export_scope": "provider_provenance_scheduler_health",
        "exported_at": analytics_payload["generated_at"],
        "query": analytics_payload["query"],
        "reconstruction": reconstruction_payload,
        "current": analytics_payload["current"],
        "history_page": serialize_provider_provenance_scheduler_health_history(
          export_snapshot,
          history_payload,
        ),
        "analytics": analytics_payload,
      }
      if mixed_status_narrative_payload is not None:
        payload["mixed_status_narrative"] = mixed_status_narrative_payload
        payload["selected_occurrence"] = selected_occurrence_payload
      content = json.dumps(payload, indent=2, sort_keys=True)
      return {
        "content": content,
        "content_type": "application/json; charset=utf-8",
        "exported_at": analytics_payload["generated_at"],
        "filename": f"provider-provenance-scheduler-history-{normalized_category}.json",
        "format": "json",
        "record_count": history_payload["returned"],
        "total_count": history_payload["total"],
      }
    buffer = io.StringIO()
    fieldnames = (
      "record_id",
      "recorded_at",
      "status",
      "summary",
      "cycle_count",
      "last_executed_count",
      "total_executed_count",
      "due_report_count",
      "max_due_lag_seconds",
      "last_error",
      "source_tab_id",
      "source_tab_label",
      "narrative_phase",
      "issues",
    )
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for item in history_payload["items"]:
      serialized = serialize_provider_provenance_scheduler_health_record(item)
      writer.writerow(
        {
          "record_id": serialized["record_id"],
          "recorded_at": serialized["recorded_at"],
          "status": serialized["status"],
          "summary": serialized["summary"],
          "cycle_count": serialized["cycle_count"],
          "last_executed_count": serialized["last_executed_count"],
          "total_executed_count": serialized["total_executed_count"],
          "due_report_count": serialized["due_report_count"],
          "max_due_lag_seconds": serialized["max_due_lag_seconds"],
          "last_error": serialized["last_error"],
          "source_tab_id": serialized["source_tab_id"],
          "source_tab_label": serialized["source_tab_label"],
          "narrative_phase": (
            self._build_provider_provenance_scheduler_narrative_phase(
              record=item,
              resolution_at=resolved_at_utc,
            )
            if normalized_narrative_mode == "mixed_status_post_resolution"
            else ""
          ),
          "issues": " | ".join(serialized["issues"]),
        }
      )
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": analytics_payload["generated_at"],
      "filename": f"provider-provenance-scheduler-history-{normalized_category}.csv",
      "format": "csv",
      "record_count": history_payload["returned"],
      "total_count": history_payload["total"],
    }
