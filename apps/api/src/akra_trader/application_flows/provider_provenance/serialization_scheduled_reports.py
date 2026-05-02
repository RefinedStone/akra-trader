from __future__ import annotations

from copy import deepcopy
from datetime import UTC
from datetime import datetime
from typing import Any

from akra_trader.application_flows.provider_provenance.mixins import ProviderProvenanceCompatibilityMixin
from akra_trader.domain.models import *  # noqa: F403

__all__ = (
  "serialize_provider_provenance_scheduled_report_record",
  "serialize_provider_provenance_scheduler_health",
  "serialize_provider_provenance_scheduler_health_record",
  "serialize_provider_provenance_scheduler_health_history",
  "serialize_operator_alert",
  "serialize_provider_provenance_scheduler_alert_history",
  "serialize_provider_provenance_scheduled_report_list",
  "serialize_provider_provenance_scheduled_report_audit_record",
  "serialize_provider_provenance_scheduled_report_history",
  "serialize_provider_provenance_scheduled_report_run_result",
  "serialize_provider_provenance_scheduled_report_run_due_result",
)

def serialize_provider_provenance_scheduled_report_record(
  record: ProviderProvenanceScheduledReportRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  normalized_layout = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_dashboard_layout_payload(
    record.layout
  )
  return {
    "report_id": record.report_id,
    "name": record.name,
    "description": record.description,
    "preset_id": record.preset_id,
    "view_id": record.view_id,
    "cadence": record.cadence,
    "status": record.status,
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "layout": deepcopy(normalized_layout),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "next_run_at": record.next_run_at.isoformat() if record.next_run_at is not None else None,
    "last_run_at": record.last_run_at.isoformat() if record.last_run_at is not None else None,
    "last_export_job_id": record.last_export_job_id,
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
  }

def serialize_provider_provenance_scheduler_health(
  record: ProviderProvenanceSchedulerHealth,
) -> dict[str, Any]:
  return {
    "generated_at": record.generated_at.isoformat(),
    "enabled": record.enabled,
    "status": record.status,
    "summary": record.summary,
    "interval_seconds": record.interval_seconds,
    "batch_limit": record.batch_limit,
    "last_cycle_started_at": (
      record.last_cycle_started_at.isoformat()
      if record.last_cycle_started_at is not None
      else None
    ),
    "last_cycle_finished_at": (
      record.last_cycle_finished_at.isoformat()
      if record.last_cycle_finished_at is not None
      else None
    ),
    "last_success_at": record.last_success_at.isoformat() if record.last_success_at is not None else None,
    "last_failure_at": record.last_failure_at.isoformat() if record.last_failure_at is not None else None,
    "last_error": record.last_error,
    "cycle_count": record.cycle_count,
    "success_count": record.success_count,
    "failure_count": record.failure_count,
    "consecutive_failure_count": record.consecutive_failure_count,
    "last_executed_count": record.last_executed_count,
    "total_executed_count": record.total_executed_count,
    "due_report_count": record.due_report_count,
    "oldest_due_at": record.oldest_due_at.isoformat() if record.oldest_due_at is not None else None,
    "max_due_lag_seconds": record.max_due_lag_seconds,
    "active_alert_key": record.active_alert_key,
    "alert_workflow_job_id": record.alert_workflow_job_id,
    "alert_workflow_triggered_at": (
      record.alert_workflow_triggered_at.isoformat()
      if record.alert_workflow_triggered_at is not None
      else None
    ),
    "alert_workflow_state": record.alert_workflow_state,
    "alert_workflow_summary": record.alert_workflow_summary,
    "issues": list(record.issues),
  }

def serialize_provider_provenance_scheduler_health_record(
  record: ProviderProvenanceSchedulerHealthRecord,
) -> dict[str, Any]:
  return {
    "record_id": record.record_id,
    "scheduler_key": record.scheduler_key,
    "recorded_at": record.recorded_at.isoformat(),
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "enabled": record.enabled,
    "status": record.status,
    "summary": record.summary,
    "interval_seconds": record.interval_seconds,
    "batch_limit": record.batch_limit,
    "last_cycle_started_at": (
      record.last_cycle_started_at.isoformat()
      if record.last_cycle_started_at is not None
      else None
    ),
    "last_cycle_finished_at": (
      record.last_cycle_finished_at.isoformat()
      if record.last_cycle_finished_at is not None
      else None
    ),
    "last_success_at": record.last_success_at.isoformat() if record.last_success_at is not None else None,
    "last_failure_at": record.last_failure_at.isoformat() if record.last_failure_at is not None else None,
    "last_error": record.last_error,
    "cycle_count": record.cycle_count,
    "success_count": record.success_count,
    "failure_count": record.failure_count,
    "consecutive_failure_count": record.consecutive_failure_count,
    "last_executed_count": record.last_executed_count,
    "total_executed_count": record.total_executed_count,
    "due_report_count": record.due_report_count,
    "oldest_due_at": record.oldest_due_at.isoformat() if record.oldest_due_at is not None else None,
    "max_due_lag_seconds": record.max_due_lag_seconds,
    "active_alert_key": record.active_alert_key,
    "alert_workflow_job_id": record.alert_workflow_job_id,
    "alert_workflow_triggered_at": (
      record.alert_workflow_triggered_at.isoformat()
      if record.alert_workflow_triggered_at is not None
      else None
    ),
    "alert_workflow_state": record.alert_workflow_state,
    "alert_workflow_summary": record.alert_workflow_summary,
    "source_tab_id": record.source_tab_id,
    "source_tab_label": record.source_tab_label,
    "issues": list(record.issues),
  }

def serialize_provider_provenance_scheduler_health_history(
  current: ProviderProvenanceSchedulerHealth,
  payload: dict[str, Any],
) -> dict[str, Any]:
  items = payload.get("items", ())
  query = payload.get("query", {})
  return {
    "generated_at": current.generated_at.isoformat(),
    "query": {
      "status": query.get("status"),
      "limit": int(query.get("limit", 25)),
      "offset": int(query.get("offset", 0)),
    },
    "current": serialize_provider_provenance_scheduler_health(current),
    "items": [
      serialize_provider_provenance_scheduler_health_record(record)
      for record in items
    ],
    "total": int(payload.get("total", 0)),
    "returned": int(payload.get("returned", 0)),
    "has_more": bool(payload.get("has_more", False)),
    "next_offset": payload.get("next_offset"),
    "previous_offset": payload.get("previous_offset"),
  }

def serialize_operator_alert(
  alert: OperatorAlert,
) -> dict[str, Any]:
  return {
    "alert_id": alert.alert_id,
    "severity": alert.severity,
    "category": alert.category,
    "summary": alert.summary,
    "detail": alert.detail,
    "detected_at": alert.detected_at.isoformat(),
    "run_id": alert.run_id,
    "session_id": alert.session_id,
    "symbol": alert.symbol,
    "symbols": list(alert.symbols),
    "timeframe": alert.timeframe,
    "primary_focus": ProviderProvenanceCompatibilityMixin._serialize_operator_alert_primary_focus_payload(
      alert.primary_focus,
    ),
    "occurrence_id": alert.occurrence_id,
    "timeline_key": alert.timeline_key,
    "timeline_position": alert.timeline_position,
    "timeline_total": alert.timeline_total,
    "status": alert.status,
    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else None,
    "source": alert.source,
    "delivery_targets": list(alert.delivery_targets),
  }

def serialize_provider_provenance_scheduler_alert_history(
  payload: dict[str, Any],
) -> dict[str, Any]:
  items = payload.get("items", ())
  query = payload.get("query", {})
  summary = payload.get("summary", {})
  generated_at = payload.get("generated_at")
  return {
    "generated_at": (
      generated_at.isoformat()
      if isinstance(generated_at, datetime)
      else datetime.now(tz=UTC).isoformat()
    ),
    "query": {
      "category": query.get("category"),
      "status": query.get("status"),
      "narrative_facet": query.get("narrative_facet"),
      "search": query.get("search"),
      "limit": int(query.get("limit", 25)),
      "offset": int(query.get("offset", 0)),
    },
    "available_filters": {
      "categories": list(payload.get("available_filters", {}).get("categories", ())),
      "statuses": list(payload.get("available_filters", {}).get("statuses", ())),
      "narrative_facets": list(
        payload.get("available_filters", {}).get("narrative_facets", ())
      ),
    },
    "summary": {
      "total_occurrences": int(summary.get("total_occurrences", 0)),
      "active_count": int(summary.get("active_count", 0)),
      "resolved_count": int(summary.get("resolved_count", 0)),
      "by_category": [
        {
          "category": entry.get("category"),
          "total": int(entry.get("total", 0)),
          "active_count": int(entry.get("active_count", 0)),
          "resolved_count": int(entry.get("resolved_count", 0)),
        }
        for entry in summary.get("by_category", ())
      ],
    },
    "search_summary": (
      {
        "query_id": payload.get("search_summary", {}).get("query_id"),
        "query": payload.get("search_summary", {}).get("query"),
        "mode": payload.get("search_summary", {}).get("mode"),
        "token_count": int(payload.get("search_summary", {}).get("token_count", 0)),
        "matched_occurrences": int(payload.get("search_summary", {}).get("matched_occurrences", 0)),
        "top_score": int(payload.get("search_summary", {}).get("top_score", 0)),
        "max_term_coverage_pct": int(
          payload.get("search_summary", {}).get("max_term_coverage_pct", 0)
        ),
        "phrase_match_count": int(payload.get("search_summary", {}).get("phrase_match_count", 0)),
        "operator_count": int(payload.get("search_summary", {}).get("operator_count", 0)),
        "semantic_concept_count": int(
          payload.get("search_summary", {}).get("semantic_concept_count", 0)
        ),
        "negated_term_count": int(payload.get("search_summary", {}).get("negated_term_count", 0)),
        "boolean_operator_count": int(
          payload.get("search_summary", {}).get("boolean_operator_count", 0)
        ),
        "indexed_occurrence_count": int(
          payload.get("search_summary", {}).get("indexed_occurrence_count", 0)
        ),
        "indexed_term_count": int(payload.get("search_summary", {}).get("indexed_term_count", 0)),
        "persistence_mode": payload.get("search_summary", {}).get("persistence_mode"),
        "relevance_model": payload.get("search_summary", {}).get("relevance_model"),
        "retrieval_cluster_mode": payload.get("search_summary", {}).get("retrieval_cluster_mode"),
        "retrieval_cluster_count": int(
          payload.get("search_summary", {}).get("retrieval_cluster_count", 0)
        ),
        "top_cluster_label": payload.get("search_summary", {}).get("top_cluster_label"),
        "parsed_terms": list(payload.get("search_summary", {}).get("parsed_terms", ())),
        "parsed_phrases": list(payload.get("search_summary", {}).get("parsed_phrases", ())),
        "parsed_operators": list(payload.get("search_summary", {}).get("parsed_operators", ())),
        "semantic_concepts": list(payload.get("search_summary", {}).get("semantic_concepts", ())),
        "query_plan": list(payload.get("search_summary", {}).get("query_plan", ())),
      }
      if isinstance(payload.get("search_summary"), dict)
      else None
    ),
    "search_analytics": (
      {
        "query_id": payload.get("search_analytics", {}).get("query_id"),
        "recorded_at": (
          payload.get("search_analytics", {}).get("recorded_at").isoformat()
          if isinstance(payload.get("search_analytics", {}).get("recorded_at"), datetime)
          else payload.get("search_analytics", {}).get("recorded_at")
        ),
        "recent_query_count": int(payload.get("search_analytics", {}).get("recent_query_count", 0)),
        "feedback_count": int(payload.get("search_analytics", {}).get("feedback_count", 0)),
        "pending_feedback_count": int(
          payload.get("search_analytics", {}).get("pending_feedback_count", 0)
        ),
        "approved_feedback_count": int(
          payload.get("search_analytics", {}).get("approved_feedback_count", 0)
        ),
        "rejected_feedback_count": int(
          payload.get("search_analytics", {}).get("rejected_feedback_count", 0)
        ),
        "relevant_feedback_count": int(
          payload.get("search_analytics", {}).get("relevant_feedback_count", 0)
        ),
        "not_relevant_feedback_count": int(
          payload.get("search_analytics", {}).get("not_relevant_feedback_count", 0)
        ),
        "helpful_feedback_ratio_pct": int(
          payload.get("search_analytics", {}).get("helpful_feedback_ratio_pct", 0)
        ),
        "learned_relevance_active": bool(
          payload.get("search_analytics", {}).get("learned_relevance_active", False)
        ),
        "tuning_profile_version": payload.get("search_analytics", {}).get("tuning_profile_version"),
        "tuned_feature_count": int(payload.get("search_analytics", {}).get("tuned_feature_count", 0)),
        "channel_adjustments": {
          "lexical": int(
            payload.get("search_analytics", {}).get("channel_adjustments", {}).get("lexical", 0)
          ),
          "semantic": int(
            payload.get("search_analytics", {}).get("channel_adjustments", {}).get("semantic", 0)
          ),
          "operator": int(
            payload.get("search_analytics", {}).get("channel_adjustments", {}).get("operator", 0)
          ),
        },
        "top_field_adjustments": [
          {
            "field": entry.get("field"),
            "score": int(entry.get("score", 0)),
          }
          for entry in payload.get("search_analytics", {}).get("top_field_adjustments", ())
          if isinstance(entry, dict)
        ],
        "top_semantic_adjustments": [
          {
            "concept": entry.get("concept"),
            "score": int(entry.get("score", 0)),
          }
          for entry in payload.get("search_analytics", {}).get("top_semantic_adjustments", ())
          if isinstance(entry, dict)
        ],
        "top_operator_adjustments": [
          {
            "operator": entry.get("operator"),
            "score": int(entry.get("score", 0)),
          }
          for entry in payload.get("search_analytics", {}).get("top_operator_adjustments", ())
          if isinstance(entry, dict)
        ],
        "recent_queries": [
          {
            "query_id": entry.get("query_id"),
            "recorded_at": (
              entry.get("recorded_at").isoformat()
              if isinstance(entry.get("recorded_at"), datetime)
              else entry.get("recorded_at")
            ),
            "query": entry.get("query"),
            "matched_occurrences": int(entry.get("matched_occurrences", 0)),
            "top_score": int(entry.get("top_score", 0)),
            "relevance_model": entry.get("relevance_model"),
          }
          for entry in payload.get("search_analytics", {}).get("recent_queries", ())
          if isinstance(entry, dict)
        ],
        "recent_feedback": [
          {
            "feedback_id": entry.get("feedback_id"),
            "recorded_at": (
              entry.get("recorded_at").isoformat()
              if isinstance(entry.get("recorded_at"), datetime)
              else entry.get("recorded_at")
            ),
            "occurrence_id": entry.get("occurrence_id"),
            "signal": entry.get("signal"),
            "moderation_status": entry.get("moderation_status"),
            "matched_fields": list(entry.get("matched_fields", ())),
            "semantic_concepts": list(entry.get("semantic_concepts", ())),
            "operator_hits": list(entry.get("operator_hits", ())),
            "note": entry.get("note"),
            "moderation_note": entry.get("moderation_note"),
          }
          for entry in payload.get("search_analytics", {}).get("recent_feedback", ())
          if isinstance(entry, dict)
        ],
      }
      if isinstance(payload.get("search_analytics"), dict)
      else None
    ),
    "retrieval_clusters": [
      {
        "cluster_id": entry.get("cluster_id"),
        "rank": int(entry.get("rank", 0)),
        "label": entry.get("label"),
        "summary": entry.get("summary"),
        "occurrence_count": int(entry.get("occurrence_count", 0)),
        "top_score": int(entry.get("top_score", 0)),
        "average_score": int(entry.get("average_score", 0)),
        "average_similarity_pct": int(entry.get("average_similarity_pct", 0)),
        "semantic_concepts": list(entry.get("semantic_concepts", ())),
        "vector_terms": list(entry.get("vector_terms", ())),
        "categories": list(entry.get("categories", ())),
        "statuses": list(entry.get("statuses", ())),
        "narrative_facets": list(entry.get("narrative_facets", ())),
        "top_occurrence_id": entry.get("top_occurrence_id"),
        "top_occurrence_summary": entry.get("top_occurrence_summary"),
        "occurrence_ids": list(entry.get("occurrence_ids", ())),
      }
      for entry in payload.get("retrieval_clusters", ())
      if isinstance(entry, dict)
    ],
    "items": [
      {
        **serialize_operator_alert(
          item.get("alert") if isinstance(item, dict) else item
        ),
        "narrative": {
          "facet": (
            item.get("narrative", {}).get("facet")
            if isinstance(item, dict)
            else None
          ),
          "facet_flags": list(
            item.get("narrative", {}).get("facet_flags", ())
            if isinstance(item, dict)
            else ()
          ),
          "narrative_mode": (
            item.get("narrative", {}).get("narrative_mode")
            if isinstance(item, dict)
            else None
          ),
          "can_reconstruct_narrative": bool(
            item.get("narrative", {}).get("can_reconstruct_narrative", False)
            if isinstance(item, dict)
            else False
          ),
          "has_post_resolution_history": bool(
            item.get("narrative", {}).get("has_post_resolution_history", False)
            if isinstance(item, dict)
            else False
          ),
          "occurrence_record_count": int(
            item.get("narrative", {}).get("occurrence_record_count", 0)
            if isinstance(item, dict)
            else 0
          ),
          "post_resolution_record_count": int(
            item.get("narrative", {}).get("post_resolution_record_count", 0)
            if isinstance(item, dict)
            else 0
          ),
          "status_sequence": list(
            item.get("narrative", {}).get("status_sequence", ())
            if isinstance(item, dict)
            else ()
          ),
          "post_resolution_status_sequence": list(
            item.get("narrative", {}).get("post_resolution_status_sequence", ())
            if isinstance(item, dict)
            else ()
          ),
          "narrative_window_ended_at": (
            item.get("narrative", {}).get("narrative_window_ended_at").isoformat()
            if isinstance(item, dict)
            and isinstance(item.get("narrative", {}).get("narrative_window_ended_at"), datetime)
            else None
          ),
          "next_occurrence_detected_at": (
            item.get("narrative", {}).get("next_occurrence_detected_at").isoformat()
            if isinstance(item, dict)
            and isinstance(item.get("narrative", {}).get("next_occurrence_detected_at"), datetime)
            else None
          ),
        },
        "search_match": (
          {
            "score": int(item.get("search_match", {}).get("score", 0)),
            "matched_terms": list(item.get("search_match", {}).get("matched_terms", ())),
            "matched_phrases": list(item.get("search_match", {}).get("matched_phrases", ())),
            "matched_fields": list(item.get("search_match", {}).get("matched_fields", ())),
            "term_coverage_pct": int(item.get("search_match", {}).get("term_coverage_pct", 0)),
            "phrase_match": bool(item.get("search_match", {}).get("phrase_match", False)),
            "exact_match": bool(item.get("search_match", {}).get("exact_match", False)),
            "highlights": list(item.get("search_match", {}).get("highlights", ())),
            "semantic_concepts": list(item.get("search_match", {}).get("semantic_concepts", ())),
            "operator_hits": list(item.get("search_match", {}).get("operator_hits", ())),
            "lexical_score": int(item.get("search_match", {}).get("lexical_score", 0)),
            "semantic_score": int(item.get("search_match", {}).get("semantic_score", 0)),
            "operator_score": int(item.get("search_match", {}).get("operator_score", 0)),
            "learned_score": int(item.get("search_match", {}).get("learned_score", 0)),
            "feedback_signal_count": int(
              item.get("search_match", {}).get("feedback_signal_count", 0)
            ),
            "tuning_signals": list(item.get("search_match", {}).get("tuning_signals", ())),
            "relevance_model": item.get("search_match", {}).get("relevance_model"),
            "ranking_reason": item.get("search_match", {}).get("ranking_reason"),
          }
          if isinstance(item, dict) and isinstance(item.get("search_match"), dict)
          else None
        ),
        "retrieval_cluster": (
          {
            "cluster_id": item.get("retrieval_cluster", {}).get("cluster_id"),
            "rank": int(item.get("retrieval_cluster", {}).get("rank", 0)),
            "label": item.get("retrieval_cluster", {}).get("label"),
            "similarity_pct": int(item.get("retrieval_cluster", {}).get("similarity_pct", 0)),
            "semantic_concepts": list(
              item.get("retrieval_cluster", {}).get("semantic_concepts", ())
            ),
            "vector_terms": list(
              item.get("retrieval_cluster", {}).get("vector_terms", ())
            ),
          }
          if isinstance(item, dict) and isinstance(item.get("retrieval_cluster"), dict)
          else None
        ),
      }
      for item in items
    ],
    "total": int(payload.get("total", 0)),
    "returned": int(payload.get("returned", 0)),
    "has_more": bool(payload.get("has_more", False)),
    "next_offset": payload.get("next_offset"),
    "previous_offset": payload.get("previous_offset"),
  }

def serialize_provider_provenance_scheduled_report_list(
  records: tuple[ProviderProvenanceScheduledReportRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduled_report_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduled_report_audit_record(
  record: ProviderProvenanceScheduledReportAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "report_id": record.report_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "source_tab_id": record.source_tab_id,
    "source_tab_label": record.source_tab_label,
    "export_job_id": record.export_job_id,
    "detail": record.detail,
  }

def serialize_provider_provenance_scheduled_report_history(
  record: ProviderProvenanceScheduledReportRecord,
  audit_records: tuple[ProviderProvenanceScheduledReportAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "report": serialize_provider_provenance_scheduled_report_record(record),
    "history": [
      serialize_provider_provenance_scheduled_report_audit_record(audit_record)
      for audit_record in audit_records
    ],
  }

def serialize_provider_provenance_scheduled_report_run_result(
  payload: dict[str, Any],
) -> dict[str, Any]:
  report = payload.get("report")
  export_job = payload.get("export_job")
  if not isinstance(report, ProviderProvenanceScheduledReportRecord):
    raise ValueError("Provider provenance scheduled report result is missing the report record.")
  if not isinstance(export_job, ProviderProvenanceExportJobRecord):
    raise ValueError("Provider provenance scheduled report result is missing the export job record.")
  return {
    "report": serialize_provider_provenance_scheduled_report_record(report),
    "export_job": serialize_provider_provenance_export_job_record(export_job),
  }

def serialize_provider_provenance_scheduled_report_run_due_result(
  payload: dict[str, Any],
) -> dict[str, Any]:
  items = payload.get("items")
  return {
    "generated_at": payload.get("generated_at"),
    "due_before": payload.get("due_before"),
    "executed_count": int(payload.get("executed_count", 0)),
    "items": [
      serialize_provider_provenance_scheduled_report_run_result(item)
      for item in items
      if isinstance(item, dict)
    ],
  }
