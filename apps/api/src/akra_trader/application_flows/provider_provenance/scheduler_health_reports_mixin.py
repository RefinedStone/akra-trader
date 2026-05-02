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


class ProviderProvenanceSchedulerHealthReportsMixin:
  def export_provider_provenance_scheduler_stitched_narrative_report(
    self,
    *,
    category: str | None = None,
    status: str | None = None,
    narrative_facet: str | None = None,
    search: str | None = None,
    offset: int = 0,
    occurrence_limit: int = 8,
    history_limit: int = 25,
    drilldown_history_limit: int = 24,
    export_format: str = "json",
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported provider provenance scheduler stitched narrative export format.")
    normalized_category = self._normalize_provider_provenance_scheduler_alert_history_category(category)
    normalized_status = self._normalize_provider_provenance_scheduler_alert_history_status(status)
    normalized_narrative_facet = self._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
      narrative_facet
    )
    normalized_occurrence_limit = max(1, min(occurrence_limit, 50))
    normalized_offset = max(offset, 0)
    normalized_history_limit = max(1, min(history_limit, 200))
    normalized_drilldown_history_limit = max(1, min(drilldown_history_limit, 100))
    alert_history_payload = self.get_provider_provenance_scheduler_alert_history_page(
      category=normalized_category,
      status=normalized_status,
      narrative_facet=normalized_narrative_facet,
      search=search,
      limit=normalized_occurrence_limit,
      offset=normalized_offset,
    )
    selected_occurrences = tuple(alert_history_payload["items"])
    if not selected_occurrences:
      raise LookupError("No scheduler alert occurrences match the selected stitched narrative report filters.")
    self._prune_provider_provenance_scheduler_health_records()
    all_records = tuple(
      sorted(
        self._list_provider_provenance_scheduler_health_records(),
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    occurrence_payloads: list[dict[str, Any]] = []
    stitched_segments: list[dict[str, Any]] = []
    stitched_records_by_id: dict[str, ProviderProvenanceSchedulerHealthRecord] = {}
    flattened_rows: list[dict[str, Any]] = []
    for occurrence_index, occurrence in enumerate(selected_occurrences, start=1):
      alert = occurrence["alert"]
      narrative = occurrence["narrative"]
      occurrence_context = self._build_provider_provenance_scheduler_occurrence_reconstruction_context(
        alert_category=alert.category,
        detected_at=alert.detected_at,
        resolved_at=alert.resolved_at,
        narrative_mode=(
          narrative.get("narrative_mode")
          if isinstance(narrative.get("narrative_mode"), str)
          else ("mixed_status_post_resolution" if alert.status == "resolved" else "matched_status")
        ),
        history_limit=normalized_history_limit,
        drilldown_history_limit=normalized_drilldown_history_limit,
        all_records=all_records,
      )
      occurrence_records = occurrence_context["export_records"]
      for record in occurrence_records:
        stitched_records_by_id.setdefault(record.record_id, record)
        flattened_rows.append(
          {
            "occurrence": occurrence,
            "context": occurrence_context,
            "record": record,
          }
        )
      occurrence_segments = self._build_provider_provenance_scheduler_status_narrative_segments(
        records=occurrence_records,
        resolution_at=occurrence_context["resolved_at"],
      )
      for segment_index, segment in enumerate(occurrence_segments, start=1):
        stitched_segments.append(
          {
            "stitch_index": len(stitched_segments) + 1,
            "occurrence_index": occurrence_index,
            "segment_index": segment_index,
            "occurrence_id": alert.occurrence_id,
            "category": alert.category,
            "occurrence_status": alert.status,
            "summary": alert.summary,
            "detected_at": alert.detected_at.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else None,
            "narrative_mode": occurrence_context["normalized_narrative_mode"],
            **segment,
          }
        )
      occurrence_payloads.append(
        {
          "occurrence_id": alert.occurrence_id,
          "category": alert.category,
          "status": alert.status,
          "severity": alert.severity,
          "summary": alert.summary,
          "detail": alert.detail,
          "detected_at": alert.detected_at.isoformat(),
          "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else None,
          "timeline_key": alert.timeline_key,
          "timeline_position": alert.timeline_position,
          "timeline_total": alert.timeline_total,
          "delivery_targets": list(alert.delivery_targets),
          "narrative": {
            "facet": narrative.get("facet"),
            "facet_flags": list(narrative.get("facet_flags", ())),
            "narrative_mode": occurrence_context["normalized_narrative_mode"],
            "can_reconstruct_narrative": bool(narrative.get("can_reconstruct_narrative")),
            "has_post_resolution_history": bool(narrative.get("has_post_resolution_history")),
            "occurrence_record_count": int(narrative.get("occurrence_record_count", 0)),
            "post_resolution_record_count": int(narrative.get("post_resolution_record_count", 0)),
            "status_sequence": list(narrative.get("status_sequence", ())),
            "post_resolution_status_sequence": list(
              narrative.get("post_resolution_status_sequence", ())
            ),
            "narrative_window_ended_at": (
              narrative.get("narrative_window_ended_at").isoformat()
              if isinstance(narrative.get("narrative_window_ended_at"), datetime)
              else narrative.get("narrative_window_ended_at")
            ),
            "next_occurrence_detected_at": (
              narrative.get("next_occurrence_detected_at").isoformat()
              if isinstance(narrative.get("next_occurrence_detected_at"), datetime)
              else narrative.get("next_occurrence_detected_at")
            ),
          },
          "search_match": deepcopy(occurrence.get("search_match")),
          "retrieval_cluster": deepcopy(occurrence.get("retrieval_cluster")),
          "window_started_at": occurrence_context["detected_at"].isoformat(),
          "window_ended_at": occurrence_context["export_window_end"].isoformat(),
          "record_count": len(occurrence_records),
          "current": occurrence_context["analytics_payload"]["current"],
          "selected_occurrence": occurrence_context["selected_occurrence_payload"],
          "status_sequence": list(occurrence_segments),
          "next_occurrence_detected_at": (
            occurrence_context["next_occurrence_detected_at"].isoformat()
            if occurrence_context["next_occurrence_detected_at"] is not None
            else None
          ),
          "peak_lag_seconds": max(
            (record.max_due_lag_seconds for record in occurrence_records),
            default=0,
          ),
          "peak_due_report_count": max(
            (record.due_report_count for record in occurrence_records),
            default=0,
          ),
        }
      )
    stitched_records = tuple(
      sorted(
        stitched_records_by_id.values(),
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    latest_stitched_record = max(
      stitched_records,
      key=lambda record: (record.recorded_at, record.record_id),
    )
    stitched_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
      latest_stitched_record,
    )
    stitched_window_started_at = min(
      context["detected_at"] for context in (row["context"] for row in flattened_rows)
    )
    stitched_window_ended_at = latest_stitched_record.recorded_at
    stitched_window_days = max(
      3,
      min(
        int((stitched_window_ended_at.date() - stitched_window_started_at.date()).days) + 1,
        90,
      ),
    )
    stitched_history_payload = {
      "query": {
        "status": None,
        "limit": normalized_history_limit,
        "offset": 0,
      },
      "items": tuple(
        sorted(
          stitched_records,
          key=lambda record: (record.recorded_at, record.record_id),
          reverse=True,
        )
      )[:normalized_history_limit],
      "total": len(stitched_records),
      "returned": min(len(stitched_records), normalized_history_limit),
      "has_more": len(stitched_records) > normalized_history_limit,
      "next_offset": (
        normalized_history_limit if len(stitched_records) > normalized_history_limit else None
      ),
      "previous_offset": None,
    }
    stitched_time_series = self._build_provider_provenance_scheduler_health_time_series(
      records=stitched_records,
      window_days=stitched_window_days,
      now=stitched_window_ended_at,
    )
    stitched_drilldown = self._build_provider_provenance_scheduler_health_hourly_drill_down(
      records=stitched_records,
      bucket_key=latest_stitched_record.recorded_at.date().isoformat(),
      history_limit=normalized_drilldown_history_limit,
    )
    by_category: dict[str, dict[str, Any]] = {}
    for occurrence in occurrence_payloads:
      category_key = occurrence["category"]
      category_entry = by_category.setdefault(
        category_key,
        {
          "category": category_key,
          "occurrence_count": 0,
          "active_count": 0,
          "resolved_count": 0,
          "record_count": 0,
          "peak_lag_seconds": 0,
          "peak_due_report_count": 0,
        },
      )
      category_entry["occurrence_count"] += 1
      category_entry["active_count"] += 1 if occurrence["status"] == "active" else 0
      category_entry["resolved_count"] += 1 if occurrence["status"] == "resolved" else 0
      category_entry["record_count"] += int(occurrence["record_count"])
      category_entry["peak_lag_seconds"] = max(
        category_entry["peak_lag_seconds"],
        int(occurrence["peak_lag_seconds"]),
      )
      category_entry["peak_due_report_count"] = max(
        category_entry["peak_due_report_count"],
        int(occurrence["peak_due_report_count"]),
      )
    exported_at = self._clock().isoformat()
    analytics_payload = {
      "generated_at": exported_at,
      "query": {
        "status": normalized_status,
        "window_days": stitched_time_series["window_days"],
        "history_limit": min(normalized_history_limit, 50),
        "drilldown_bucket_key": (
          stitched_drilldown["bucket_key"]
          if isinstance(stitched_drilldown, dict)
          else None
        ),
        "drilldown_history_limit": normalized_drilldown_history_limit,
        "reconstruction_mode": "stitched_occurrence_report",
        "narrative_mode": "stitched_multi_occurrence",
        "alert_category": normalized_category,
        "narrative_facet": normalized_narrative_facet or "all_occurrences",
        "search": search.strip() if isinstance(search, str) and search.strip() else None,
        "occurrence_limit": normalized_occurrence_limit,
        "occurrence_offset": normalized_offset,
        "selected_occurrence_count": len(occurrence_payloads),
        "stitched_window_started_at": stitched_window_started_at.isoformat(),
        "stitched_window_ended_at": stitched_window_ended_at.isoformat(),
      },
      "current": serialize_provider_provenance_scheduler_health(stitched_snapshot),
      "totals": {
        "record_count": len(stitched_records),
        "healthy_count": sum(1 for record in stitched_records if record.status == "healthy"),
        "lagging_count": sum(1 for record in stitched_records if record.status == "lagging"),
        "failed_count": sum(1 for record in stitched_records if record.status == "failed"),
        "disabled_count": sum(1 for record in stitched_records if record.status == "disabled"),
        "starting_count": sum(1 for record in stitched_records if record.status == "starting"),
        "executed_report_count": sum(record.last_executed_count for record in stitched_records),
        "peak_lag_seconds": max((record.max_due_lag_seconds for record in stitched_records), default=0),
        "peak_due_report_count": max((record.due_report_count for record in stitched_records), default=0),
      },
      "available_filters": {
        "statuses": sorted({record.status for record in stitched_records if record.status}),
        "categories": sorted({occurrence["category"] for occurrence in occurrence_payloads}),
      },
      "time_series": stitched_time_series,
      "drill_down": stitched_drilldown,
      "recent_history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in stitched_history_payload["items"][:min(normalized_history_limit, 50)]
      ],
    }
    stitched_report_payload = {
      "mode": "stitched_multi_occurrence",
      "summary": {
        "occurrence_count": len(occurrence_payloads),
        "active_count": sum(1 for occurrence in occurrence_payloads if occurrence["status"] == "active"),
        "resolved_count": sum(1 for occurrence in occurrence_payloads if occurrence["status"] == "resolved"),
        "segment_count": len(stitched_segments),
        "record_count": len(stitched_records),
        "categories": sorted({occurrence["category"] for occurrence in occurrence_payloads}),
        "statuses": sorted({occurrence["status"] for occurrence in occurrence_payloads}),
        "narrative_facets": sorted(
          {
            occurrence["narrative"]["facet"]
            for occurrence in occurrence_payloads
            if isinstance(occurrence["narrative"]["facet"], str)
            and occurrence["narrative"]["facet"]
          }
        ),
        "stitched_window_started_at": stitched_window_started_at.isoformat(),
        "stitched_window_ended_at": stitched_window_ended_at.isoformat(),
        "peak_lag_seconds": analytics_payload["totals"]["peak_lag_seconds"],
        "peak_due_report_count": analytics_payload["totals"]["peak_due_report_count"],
        "executed_report_count": analytics_payload["totals"]["executed_report_count"],
      },
      "selected_occurrence_page": {
        "query": alert_history_payload["query"],
        "total": alert_history_payload["total"],
        "returned": alert_history_payload["returned"],
        "has_more": alert_history_payload["has_more"],
        "next_offset": alert_history_payload["next_offset"],
        "previous_offset": alert_history_payload["previous_offset"],
      },
      "search_summary": alert_history_payload.get("search_summary"),
      "search_analytics": alert_history_payload.get("search_analytics"),
      "retrieval_clusters": alert_history_payload.get("retrieval_clusters"),
      "occurrences": occurrence_payloads,
      "stitched_status_sequence": stitched_segments,
      "by_category": tuple(by_category[key] for key in sorted(by_category)),
    }
    if normalized_format == "json":
      payload = {
        "export_scope": "provider_provenance_scheduler_health",
        "exported_at": exported_at,
        "query": analytics_payload["query"],
        "current": analytics_payload["current"],
        "history_page": serialize_provider_provenance_scheduler_health_history(
          stitched_snapshot,
          stitched_history_payload,
        ),
        "analytics": analytics_payload,
        "stitched_occurrence_report": stitched_report_payload,
      }
      content = json.dumps(
        payload,
        default=_serialize_stitched_scheduler_narrative_json_value,
        indent=2,
        sort_keys=True,
      )
      category_label = normalized_category or "all"
      return {
        "content": content,
        "content_type": "application/json; charset=utf-8",
        "exported_at": exported_at,
        "filename": f"provider-provenance-scheduler-narrative-report-{category_label}.json",
        "format": "json",
        "record_count": stitched_history_payload["returned"],
        "total_count": stitched_history_payload["total"],
      }
    buffer = io.StringIO()
    fieldnames = (
      "occurrence_id",
      "occurrence_category",
      "occurrence_status",
      "occurrence_detected_at",
      "occurrence_resolved_at",
      "narrative_mode",
      "retrieval_cluster_id",
      "retrieval_cluster_label",
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
    for row in flattened_rows:
      alert = row["occurrence"]["alert"]
      occurrence_context = row["context"]
      record = row["record"]
      retrieval_cluster = row["occurrence"].get("retrieval_cluster", {})
      serialized = serialize_provider_provenance_scheduler_health_record(record)
      writer.writerow(
        {
          "occurrence_id": alert.occurrence_id,
          "occurrence_category": alert.category,
          "occurrence_status": alert.status,
          "occurrence_detected_at": alert.detected_at.isoformat(),
          "occurrence_resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else "",
          "narrative_mode": occurrence_context["normalized_narrative_mode"],
          "retrieval_cluster_id": retrieval_cluster.get("cluster_id", ""),
          "retrieval_cluster_label": retrieval_cluster.get("label", ""),
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
          "narrative_phase": self._build_provider_provenance_scheduler_narrative_phase(
            record=record,
            resolution_at=occurrence_context["resolved_at"],
          ),
          "issues": " | ".join(serialized["issues"]),
        }
      )
    category_label = normalized_category or "all"
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": exported_at,
      "filename": f"provider-provenance-scheduler-narrative-report-{category_label}.csv",
      "format": "csv",
      "record_count": len(flattened_rows),
      "total_count": len(flattened_rows),
    }

  def export_provider_provenance_scheduler_health(
    self,
    *,
    export_format: str = "json",
    status: str | None = None,
    window_days: int = 14,
    history_limit: int = 12,
    drilldown_bucket_key: str | None = None,
    drilldown_history_limit: int = 24,
    offset: int = 0,
    limit: int = 25,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported provider provenance scheduler health export format.")
    analytics_payload = self.get_provider_provenance_scheduler_health_analytics(
      status=status,
      window_days=window_days,
      history_limit=history_limit,
      drilldown_bucket_key=drilldown_bucket_key,
      drilldown_history_limit=drilldown_history_limit,
    )
    history_payload = self.get_provider_provenance_scheduler_health_history_page(
      status=status,
      limit=limit,
      offset=offset,
    )
    current_snapshot = self.get_provider_provenance_scheduler_health()
    exported_at = self._clock().isoformat()
    if normalized_format == "json":
      content = json.dumps(
        {
          "export_scope": "provider_provenance_scheduler_health",
          "exported_at": exported_at,
          "query": {
            "status": self._normalize_provider_provenance_scheduler_health_status(status),
            "window_days": analytics_payload["query"]["window_days"],
            "history_limit": analytics_payload["query"]["history_limit"],
            "drilldown_bucket_key": analytics_payload["query"]["drilldown_bucket_key"],
            "drilldown_history_limit": analytics_payload["query"]["drilldown_history_limit"],
            "offset": history_payload["query"]["offset"],
            "limit": history_payload["query"]["limit"],
          },
          "current": serialize_provider_provenance_scheduler_health(current_snapshot),
          "history_page": serialize_provider_provenance_scheduler_health_history(
            current_snapshot,
            history_payload,
          ),
          "analytics": analytics_payload,
        },
        indent=2,
        sort_keys=True,
      )
      return {
        "content": content,
        "content_type": "application/json; charset=utf-8",
        "exported_at": exported_at,
        "filename": "provider-provenance-scheduler-health.json",
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
          "issues": " | ".join(serialized["issues"]),
        }
      )
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": exported_at,
      "filename": "provider-provenance-scheduler-health.csv",
      "format": "csv",
      "record_count": history_payload["returned"],
      "total_count": history_payload["total"],
    }
