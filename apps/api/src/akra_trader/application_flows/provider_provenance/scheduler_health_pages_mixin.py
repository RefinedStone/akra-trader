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


class ProviderProvenanceSchedulerHealthPagesMixin:
  def list_provider_provenance_scheduler_health_history(
    self,
    *,
    status: str | None = None,
    limit: int = 25,
    offset: int = 0,
  ) -> tuple[ProviderProvenanceSchedulerHealthRecord, ...]:
    self._prune_provider_provenance_scheduler_health_records()
    normalized_status = self._normalize_provider_provenance_scheduler_health_status(status)
    normalized_limit = max(1, min(limit, 200))
    normalized_offset = max(offset, 0)
    records = [
      record
      for record in self._list_provider_provenance_scheduler_health_records()
      if normalized_status is None or record.status == normalized_status
    ]
    return tuple(records[normalized_offset:normalized_offset + normalized_limit])

  def get_provider_provenance_scheduler_health_history_page(
    self,
    *,
    status: str | None = None,
    limit: int = 25,
    offset: int = 0,
  ) -> dict[str, Any]:
    self._prune_provider_provenance_scheduler_health_records()
    normalized_status = self._normalize_provider_provenance_scheduler_health_status(status)
    normalized_limit = max(1, min(limit, 200))
    normalized_offset = max(offset, 0)
    records = [
      record
      for record in self._list_provider_provenance_scheduler_health_records()
      if normalized_status is None or record.status == normalized_status
    ]
    total = len(records)
    items = records[normalized_offset:normalized_offset + normalized_limit]
    next_offset = (
      normalized_offset + len(items)
      if normalized_offset + len(items) < total
      else None
    )
    previous_offset = (
      max(normalized_offset - normalized_limit, 0)
      if normalized_offset > 0 and total > 0
      else None
    )
    return {
      "query": {
        "status": normalized_status,
        "limit": normalized_limit,
        "offset": normalized_offset,
      },
      "items": tuple(items),
      "total": total,
      "returned": len(items),
      "has_more": next_offset is not None,
      "next_offset": next_offset,
      "previous_offset": previous_offset,
    }

  def get_provider_provenance_scheduler_alert_history_page(
    self,
    *,
    category: str | None = None,
    status: str | None = None,
    narrative_facet: str | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
  ) -> dict[str, Any]:
    current_time = self._clock()
    history_rows = self._build_provider_provenance_scheduler_alert_occurrence_rows(
      current_time=current_time,
    )
    history = tuple(row["alert"] for row in history_rows)
    normalized_category = self._normalize_provider_provenance_scheduler_alert_history_category(category)
    normalized_status = self._normalize_provider_provenance_scheduler_alert_history_status(status)
    normalized_narrative_facet = self._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
      narrative_facet
    )
    normalized_search = search.strip() if isinstance(search, str) and search.strip() else None
    normalized_limit = max(1, min(limit, 200))
    normalized_offset = max(offset, 0)
    eligible_history: list[dict[str, Any]] = []
    for row in history_rows:
      if normalized_category is not None and row["alert"].category != normalized_category:
        continue
      if normalized_status is not None and row["alert"].status != normalized_status:
        continue
      if (
        normalized_narrative_facet is not None
        and normalized_narrative_facet != "all_occurrences"
        and not (
          (
            normalized_narrative_facet == "resolved_narratives"
            and bool(row["narrative"].get("can_reconstruct_narrative"))
          )
          or (
            normalized_narrative_facet == "post_resolution_recovery"
            and bool(row["narrative"].get("has_post_resolution_history"))
          )
          or (
            normalized_narrative_facet == "recurring_occurrences"
            and "recurring_occurrence" in row["narrative"].get("facet_flags", ())
          )
        )
      ):
        continue
      eligible_history.append(row)
    filtered_history: list[dict[str, Any]] = []
    retrieval_clusters: tuple[dict[str, Any], ...] = ()
    search_analytics = None
    parsed_search = (
      self._parse_provider_provenance_scheduler_alert_search_query(normalized_search)
      if normalized_search is not None
      else None
    )
    if normalized_search is not None:
      search_projection_lookup = self._build_provider_provenance_scheduler_search_projection_lookup(
        record_ids=(
          record.record_id
          for row in eligible_history
          for record in row.get("narrative_records", ()) or ()
          if isinstance(record, ProviderProvenanceSchedulerHealthRecord)
        )
      )
      search_index = self._build_provider_provenance_scheduler_alert_occurrence_search_index(
        rows=tuple(eligible_history),
        search_projection_lookup=search_projection_lookup,
      )
      tuning_profile = self._build_provider_provenance_scheduler_search_tuning_profile(
        search_query=normalized_search,
        parsed_query=parsed_search or {},
      )
      matched_document_ids = self._evaluate_provider_provenance_scheduler_alert_search_query(
        index=search_index,
        parsed_query=parsed_search or {},
      )
      for matched_document_id in matched_document_ids:
        if not (0 <= matched_document_id < len(eligible_history)):
          continue
        row = eligible_history[matched_document_id]
        document = search_index.get("documents", ())[matched_document_id]
        search_match = self._score_provider_provenance_scheduler_alert_occurrence_search_match(
          row=row,
          parsed_query=parsed_search or {},
          index=search_index,
          document=document,
          tuning_profile=tuning_profile,
        )
        if search_match is None:
          continue
        filtered_history.append(
          {
            **row,
            "search_match": search_match,
            "_search_document_id": matched_document_id,
          }
        )
    else:
      filtered_history = [{**row, "search_match": None} for row in eligible_history]
    if normalized_search is not None:
      filtered_history = sorted(
        filtered_history,
        key=lambda row: (
          row.get("search_match", {}).get("score", 0),
          row.get("search_match", {}).get("term_coverage_pct", 0),
          1 if row.get("search_match", {}).get("exact_match") else 0,
          1 if row.get("search_match", {}).get("phrase_match") else 0,
          row["alert"].resolved_at or row["alert"].detected_at,
          row["alert"].detected_at,
        ),
        reverse=True,
      )
      clustered_history, retrieval_clusters = self._cluster_provider_provenance_scheduler_alert_occurrence_search_results(
        rows=tuple(filtered_history),
        index=search_index,
      )
      filtered_history = list(clustered_history)
    total = len(filtered_history)
    items = filtered_history[normalized_offset:normalized_offset + normalized_limit]
    next_offset = (
      normalized_offset + len(items)
      if normalized_offset + len(items) < total
      else None
    )
    previous_offset = (
      max(normalized_offset - normalized_limit, 0)
      if normalized_offset > 0 and total > 0
      else None
    )
    categories = tuple(
      category_key
      for category_key in ("scheduler_lag", "scheduler_failure")
      if any(alert.category == category_key for alert in history)
    ) or ("scheduler_lag", "scheduler_failure")
    statuses = tuple(
      status_key
      for status_key in ("active", "resolved")
      if any(alert.status == status_key for alert in history)
    ) or ("active", "resolved")
    summary_by_category = tuple(
      {
        "category": category_key,
        "total": sum(1 for alert in history if alert.category == category_key),
        "active_count": sum(
          1
          for alert in history
          if alert.category == category_key and alert.status == "active"
        ),
        "resolved_count": sum(
          1
          for alert in history
          if alert.category == category_key and alert.status == "resolved"
        ),
      }
      for category_key in categories
    )
    search_summary = None
    if normalized_search is not None:
      persistence_modes = tuple(
        dict.fromkeys(
          str(document.get("persistence_mode"))
          for document in search_index.get("documents", ())
          if isinstance(document.get("persistence_mode"), str)
          and document.get("persistence_mode") != "ephemeral_occurrence_projection"
        )
      )
      search_summary = {
        "query": normalized_search,
        "mode": "persistent_full_text_boolean_semantic_ranking",
        "token_count": len(parsed_search.get("terms", ())) + len(parsed_search.get("phrases", ())),
        "matched_occurrences": total,
        "top_score": max(
          (int(row.get("search_match", {}).get("score", 0)) for row in filtered_history),
          default=0,
        ),
        "max_term_coverage_pct": max(
          (
            int(row.get("search_match", {}).get("term_coverage_pct", 0))
            for row in filtered_history
          ),
          default=0,
        ),
        "phrase_match_count": sum(
          1 for row in filtered_history if bool(row.get("search_match", {}).get("phrase_match"))
        ),
        "operator_count": len(parsed_search.get("operators", ())),
        "semantic_concept_count": len(parsed_search.get("semantic_concepts", ())),
        "negated_term_count": len(parsed_search.get("excluded_terms", ()))
        + len(parsed_search.get("excluded_phrases", ()))
        + sum(1 for operator in parsed_search.get("operators", ()) if operator.get("negated")),
        "boolean_operator_count": int(parsed_search.get("boolean_operator_count", 0)),
        "indexed_occurrence_count": len(eligible_history),
        "indexed_term_count": int(search_index.get("indexed_term_count", 0)),
        "persistence_mode": (
          persistence_modes[0]
          if persistence_modes
          else "ephemeral_occurrence_projection"
        ),
        "relevance_model": tuning_profile.get("version", "tfidf_field_weight_v1"),
        "parsed_terms": tuple(parsed_search.get("terms", ())),
        "parsed_phrases": tuple(parsed_search.get("phrases", ())),
        "parsed_operators": tuple(
          operator.get("raw")
          for operator in parsed_search.get("operators", ())
          if isinstance(operator.get("raw"), str)
        ),
        "semantic_concepts": tuple(parsed_search.get("semantic_concepts", ())),
        "query_plan": tuple(parsed_search.get("query_plan", ())),
        "retrieval_cluster_mode": "cross_occurrence_semantic_vector_cluster_v1",
        "retrieval_cluster_count": len(retrieval_clusters),
        "top_cluster_label": (
          retrieval_clusters[0].get("label")
          if retrieval_clusters
          else None
        ),
      }
      analytics_record = self._record_provider_provenance_scheduler_search_query_analytics(
        recorded_at=current_time,
        search_query=normalized_search,
        category=normalized_category,
        status=normalized_status,
        narrative_facet=normalized_narrative_facet or "all_occurrences",
        parsed_query=parsed_search or {},
        matched_rows=tuple(filtered_history),
        indexed_occurrence_count=len(eligible_history),
        indexed_term_count=int(search_index.get("indexed_term_count", 0)),
        persistence_mode=search_summary["persistence_mode"],
        relevance_model=search_summary["relevance_model"],
        top_cluster_label=search_summary["top_cluster_label"],
      )
      search_summary["query_id"] = analytics_record.query_id
      search_analytics = self._build_provider_provenance_scheduler_search_analytics_summary(
        query_record=analytics_record,
        search_query=normalized_search,
        tuning_profile=tuning_profile,
      )
    return {
      "generated_at": current_time,
      "query": {
        "category": normalized_category,
        "status": normalized_status,
        "narrative_facet": normalized_narrative_facet or "all_occurrences",
        "search": normalized_search,
        "limit": normalized_limit,
        "offset": normalized_offset,
      },
      "available_filters": {
        "categories": categories,
        "statuses": statuses,
        "narrative_facets": (
          "all_occurrences",
          "resolved_narratives",
          "post_resolution_recovery",
          "recurring_occurrences",
        ),
      },
      "summary": {
        "total_occurrences": len(history),
        "active_count": sum(1 for alert in history if alert.status == "active"),
        "resolved_count": sum(1 for alert in history if alert.status == "resolved"),
        "by_category": summary_by_category,
      },
      "search_summary": search_summary,
      "search_analytics": search_analytics,
      "retrieval_clusters": retrieval_clusters,
      "items": tuple(items),
      "total": total,
      "returned": len(items),
      "has_more": next_offset is not None,
      "next_offset": next_offset,
      "previous_offset": previous_offset,
    }

  @classmethod
  def _resolve_provider_provenance_scheduler_bucket_start(
    cls,
    bucket_key: str | None,
  ) -> datetime | None:
    if not isinstance(bucket_key, str) or not bucket_key.strip():
      return None
    normalized = bucket_key.strip()
    try:
      parsed = datetime.fromisoformat(normalized)
    except ValueError:
      return None
    parsed = parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    return parsed.replace(hour=0, minute=0, second=0, microsecond=0)

  @classmethod
  def _build_provider_provenance_scheduler_health_time_series(
    cls,
    *,
    records: tuple[ProviderProvenanceSchedulerHealthRecord, ...],
    window_days: int,
    now: datetime,
  ) -> dict[str, Any]:
    normalized_window_days = max(3, min(window_days, 90))
    anchor_candidates = [now]
    anchor_candidates.extend(record.recorded_at for record in records)
    window_anchor = cls._normalize_provider_provenance_export_bucket_start(max(anchor_candidates))
    window_started_at = window_anchor - timedelta(days=normalized_window_days - 1)
    window_ended_at = window_anchor + timedelta(days=1)

    record_buckets: dict[datetime, list[ProviderProvenanceSchedulerHealthRecord]] = {}
    for record in records:
      bucket_start = cls._normalize_provider_provenance_export_bucket_start(record.recorded_at)
      if not (window_started_at <= bucket_start < window_ended_at):
        continue
      record_buckets.setdefault(bucket_start, []).append(record)

    health_status_series: list[dict[str, Any]] = []
    lag_trend_series: list[dict[str, Any]] = []

    for offset in range(normalized_window_days):
      bucket_start = window_started_at + timedelta(days=offset)
      bucket_end = bucket_start + timedelta(days=1)
      bucket_records = sorted(
        record_buckets.get(bucket_start, []),
        key=lambda record: (record.recorded_at, record.record_id),
      )
      counts_by_status = {
        "healthy": 0,
        "lagging": 0,
        "failed": 0,
        "disabled": 0,
        "starting": 0,
      }
      for record in bucket_records:
        counts_by_status[record.status] = counts_by_status.get(record.status, 0) + 1
      dominant_status, dominant_count = max(
        counts_by_status.items(),
        key=lambda item: (item[1], item[0]),
      )
      latest_record = bucket_records[-1] if bucket_records else None
      cycle_count = len(bucket_records)
      executed_report_count = sum(record.last_executed_count for record in bucket_records)
      failure_count = sum(1 for record in bucket_records if record.status == "failed")
      lag_values = [max(record.max_due_lag_seconds, 0) for record in bucket_records]
      due_counts = [max(record.due_report_count, 0) for record in bucket_records]
      bucket_key = bucket_start.date().isoformat()
      bucket_label = bucket_start.strftime("%b %d")

      health_status_series.append(
        {
          "bucket_key": bucket_key,
          "bucket_label": bucket_label,
          "started_at": bucket_start.isoformat(),
          "ended_at": bucket_end.isoformat(),
          "cycle_count": cycle_count,
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
          "bucket_key": bucket_key,
          "bucket_label": bucket_label,
          "started_at": bucket_start.isoformat(),
          "ended_at": bucket_end.isoformat(),
          "cycle_count": cycle_count,
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
      "bucket_size": "day",
      "window_days": normalized_window_days,
      "window_started_at": window_started_at.isoformat(),
      "window_ended_at": window_ended_at.isoformat(),
      "health_status": {
        "series": health_status_series,
        "summary": {
          "peak_cycle_bucket_key": peak_cycle_bucket["bucket_key"] if peak_cycle_bucket is not None else None,
          "peak_cycle_bucket_label": (
            peak_cycle_bucket["bucket_label"]
            if peak_cycle_bucket is not None
            else None
          ),
          "peak_cycle_count": int(peak_cycle_bucket["cycle_count"]) if peak_cycle_bucket is not None else 0,
          "latest_bucket_key": latest_health_bucket["bucket_key"] if latest_health_bucket is not None else None,
          "latest_bucket_label": (
            latest_health_bucket["bucket_label"]
            if latest_health_bucket is not None
            else None
          ),
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
          "latest_due_report_count": (
            int(latest_lag_bucket["latest_due_report_count"])
            if latest_lag_bucket is not None
            else 0
          ),
          "latest_failure_count": int(latest_lag_bucket["failure_count"]) if latest_lag_bucket is not None else 0,
        },
      },
    }

  @staticmethod
  def _normalize_provider_provenance_scheduler_alert_category(
    category: str,
  ) -> str:
    normalized_category = category.strip().lower() if isinstance(category, str) else ""
    if normalized_category not in {"scheduler_lag", "scheduler_failure"}:
      raise ValueError("Unsupported scheduler alert category for historical export reconstruction.")
    return normalized_category

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_mode(
    narrative_mode: str | None,
  ) -> str:
    if not isinstance(narrative_mode, str):
      return "matched_status"
    normalized_mode = narrative_mode.strip().lower()
    if normalized_mode in {"matched_status", "mixed_status_post_resolution"}:
      return normalized_mode
    raise ValueError("Unsupported scheduler historical export narrative mode.")

  @staticmethod
  def _normalize_provider_provenance_scheduler_export_datetime(
    value: datetime,
    *,
    field_name: str,
  ) -> datetime:
    if not isinstance(value, datetime):
      raise ValueError(f"{field_name} is required for scheduler export reconstruction.")
    return value.astimezone(UTC) if value.tzinfo is not None else value.replace(tzinfo=UTC)

  @staticmethod
  def _provider_provenance_scheduler_health_snapshot_from_record(
    record: ProviderProvenanceSchedulerHealthRecord,
  ) -> ProviderProvenanceSchedulerHealth:
    return ProviderProvenanceSchedulerHealth(
      generated_at=record.recorded_at,
      enabled=record.enabled,
      status=record.status,
      summary=record.summary,
      interval_seconds=record.interval_seconds,
      batch_limit=record.batch_limit,
      last_cycle_started_at=record.last_cycle_started_at,
      last_cycle_finished_at=record.last_cycle_finished_at,
      last_success_at=record.last_success_at,
      last_failure_at=record.last_failure_at,
      last_error=record.last_error,
      cycle_count=record.cycle_count,
      success_count=record.success_count,
      failure_count=record.failure_count,
      consecutive_failure_count=record.consecutive_failure_count,
      last_executed_count=record.last_executed_count,
      total_executed_count=record.total_executed_count,
      due_report_count=record.due_report_count,
      oldest_due_at=record.oldest_due_at,
      max_due_lag_seconds=record.max_due_lag_seconds,
      active_alert_key=record.active_alert_key,
      alert_workflow_job_id=record.alert_workflow_job_id,
      alert_workflow_triggered_at=record.alert_workflow_triggered_at,
      alert_workflow_state=record.alert_workflow_state,
      alert_workflow_summary=record.alert_workflow_summary,
      issues=record.issues,
    )

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_phase(
    *,
    record: ProviderProvenanceSchedulerHealthRecord,
    resolution_at: datetime | None,
  ) -> str:
    if resolution_at is not None and record.recorded_at >= resolution_at:
      return "post_resolution"
    return "occurrence"

  @classmethod
  def _build_provider_provenance_scheduler_status_narrative_segments(
    cls,
    *,
    records: tuple[ProviderProvenanceSchedulerHealthRecord, ...],
    resolution_at: datetime | None,
  ) -> tuple[dict[str, Any], ...]:
    if not records:
      return ()
    ordered_records = tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    segments: list[dict[str, Any]] = []
    start_index = 0
    while start_index < len(ordered_records):
      end_index = start_index
      while (
        end_index + 1 < len(ordered_records)
        and ordered_records[end_index + 1].status == ordered_records[start_index].status
      ):
        end_index += 1
      segment_records = ordered_records[start_index:end_index + 1]
      latest_record = segment_records[-1]
      segments.append(
        {
          "status": latest_record.status,
          "phase": cls._build_provider_provenance_scheduler_narrative_phase(
            record=segment_records[0],
            resolution_at=resolution_at,
          ),
          "started_at": segment_records[0].recorded_at.isoformat(),
          "ended_at": latest_record.recorded_at.isoformat(),
          "record_count": len(segment_records),
          "latest_record_id": latest_record.record_id,
          "latest_summary": latest_record.summary,
          "peak_lag_seconds": max(
            (record.max_due_lag_seconds for record in segment_records),
            default=0,
          ),
          "peak_due_report_count": max(
            (record.due_report_count for record in segment_records),
            default=0,
          ),
        }
      )
      start_index = end_index + 1
    return tuple(segments)

  def _build_provider_provenance_scheduler_operator_alert(
    self,
    *,
    health: ProviderProvenanceSchedulerHealth,
    current_time: datetime,
  ) -> OperatorAlert | None:
    if health.status == "lagging":
      severity = (
        "critical"
        if health.max_due_lag_seconds >= self._provider_provenance_scheduler_critical_lag_seconds()
        else "warning"
      )
      return OperatorAlert(
        alert_id="provider-provenance:scheduler-lag",
        severity=severity,
        category="scheduler_lag",
        summary="Provider provenance report scheduler is lagging.",
        detail=(
          f"{health.due_report_count} due report(s) remain. "
          f"Oldest due at {health.oldest_due_at.isoformat() if health.oldest_due_at is not None else 'n/a'} "
          f"with {health.max_due_lag_seconds}s lag. "
          f"Last successful cycle: {health.last_success_at.isoformat() if health.last_success_at is not None else 'n/a'}."
        ),
        detected_at=health.oldest_due_at or health.generated_at,
        source="runtime",
      )
    if health.status == "failed":
      detected_at = (
        health.last_failure_at
        or health.last_cycle_finished_at
        or health.last_cycle_started_at
        or current_time
      )
      return OperatorAlert(
        alert_id="provider-provenance:scheduler-failure",
        severity="critical",
        category="scheduler_failure",
        summary="Provider provenance report scheduler is failing.",
        detail=(
          f"{health.summary} Last success: "
          f"{health.last_success_at.isoformat() if health.last_success_at is not None else 'n/a'}. "
          f"Last error: {health.last_error or 'n/a'}."
        ),
        detected_at=detected_at,
        source="runtime",
      )
    return None

  def _build_provider_provenance_scheduler_alert_history(
    self,
    *,
    current_time: datetime,
  ) -> tuple[OperatorAlert, ...]:
    return tuple(
      row["alert"]
      for row in self._build_provider_provenance_scheduler_alert_occurrence_rows(
        current_time=current_time,
      )
    )

  def _collect_provider_provenance_scheduler_operator_visibility(
    self,
    *,
    current_time: datetime,
  ) -> tuple[ProviderProvenanceSchedulerHealth, list[OperatorAlert], list[OperatorAuditEvent]]:
    health = self.get_provider_provenance_scheduler_health()
    alerts: list[OperatorAlert] = []
    audit_events: list[OperatorAuditEvent] = []
    active_alert = self._build_provider_provenance_scheduler_operator_alert(
      health=health,
      current_time=current_time,
    )

    if active_alert is not None and health.status == "lagging":
      alerts.append(active_alert)
      audit_events.append(
        OperatorAuditEvent(
          event_id=f"audit:provider_provenance_scheduler_lagging:{health.generated_at.isoformat()}",
          timestamp=health.generated_at,
          actor="system",
          kind="provider_provenance_scheduler_lagging",
          summary="Provider provenance report scheduler lag detected.",
          detail=health.summary,
          source="runtime",
        )
      )
    elif active_alert is not None and health.status == "failed":
      detected_at = active_alert.detected_at
      alerts.append(active_alert)
      audit_events.append(
        OperatorAuditEvent(
          event_id=f"audit:provider_provenance_scheduler_failed:{detected_at.isoformat()}",
          timestamp=detected_at,
          actor="system",
          kind="provider_provenance_scheduler_failed",
          summary="Provider provenance report scheduler failure detected.",
          detail=health.summary + (f" Error: {health.last_error}." if health.last_error else ""),
          source="runtime",
        )
      )

    return health, alerts, audit_events
