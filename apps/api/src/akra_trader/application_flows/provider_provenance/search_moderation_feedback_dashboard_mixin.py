from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Iterable
from typing import Mapping
from uuid import uuid4

from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan as apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
)
from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan as approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
)
from akra_trader.application_support.provider_governance_bulk_policy_orchestration import (
  bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies as bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies_support,
)
from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_plans as list_provider_provenance_scheduler_search_moderation_catalog_governance_plans_support,
)
from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan as stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy as create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans as list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies as list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  create_provider_provenance_scheduler_search_moderation_catalog_governance_policy as create_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy as delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision as restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  update_provider_provenance_scheduler_search_moderation_catalog_governance_policy as update_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support,
)
from akra_trader.application_support.provider_governance_policy_reads import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policies as list_provider_provenance_scheduler_search_moderation_catalog_governance_policies_support,
)
from akra_trader.application_support.provider_governance_policy_reads import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits as list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_support,
)
from akra_trader.application_support.provider_governance_policy_reads import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions as list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record as load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail as build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision as build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status as normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision as record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support,
)
from akra_trader.domain.models import *  # noqa: F403


class ProviderProvenanceSearchModerationDashboardMixin:
  def get_provider_provenance_scheduler_search_dashboard(
    self,
    *,
    search: str | None = None,
    moderation_status: str | None = None,
    signal: str | None = None,
    governance_view: str | None = None,
    window_days: int = 30,
    stale_pending_hours: int = 24,
    query_limit: int = 12,
    feedback_limit: int = 20,
  ) -> dict[str, Any]:
    self._prune_provider_provenance_scheduler_search_query_analytics_records()
    self._prune_provider_provenance_scheduler_search_feedback_records()
    current_time = self._clock()
    normalized_search = search.strip().lower() if isinstance(search, str) and search.strip() else None
    normalized_moderation_status = self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      moderation_status
    )
    normalized_signal = self._normalize_provider_provenance_scheduler_search_feedback_signal(signal)
    normalized_governance_view = self._normalize_provider_provenance_scheduler_search_governance_view(
      governance_view
    ) or "all_feedback"
    normalized_window_days = max(7, min(window_days, 180))
    normalized_stale_pending_hours = max(1, min(stale_pending_hours, 24 * 30))
    normalized_query_limit = max(1, min(query_limit, 50))
    normalized_feedback_limit = max(1, min(feedback_limit, 100))
    stale_pending_cutoff_seconds = normalized_stale_pending_hours * 3600
    high_score_pending_threshold = 150
    window_started_at = current_time - timedelta(days=normalized_window_days)

    analytics_records = tuple(
      record
      for record in self._list_provider_provenance_scheduler_search_query_analytics_records()
      if record.recorded_at >= window_started_at
    )
    feedback_records = tuple(
      record
      for record in self._list_provider_provenance_scheduler_search_feedback_records()
      if record.recorded_at >= window_started_at
    )

    def _matches_search(record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord | ProviderProvenanceSchedulerSearchFeedbackRecord) -> bool:
      if normalized_search is None:
        return True
      haystacks: list[str] = []
      if isinstance(record.query, str):
        haystacks.append(record.query.lower())
      if isinstance(record, ProviderProvenanceSchedulerSearchFeedbackRecord):
        haystacks.extend(
          value.lower()
          for value in (
            record.occurrence_id,
            record.actor,
            record.note,
            record.moderation_note,
            record.moderated_by,
            *record.matched_fields,
            *record.semantic_concepts,
            *record.operator_hits,
          )
          if isinstance(value, str) and value.strip()
        )
      else:
        haystacks.extend(
          value.lower()
          for value in (
            *record.query_terms,
            *record.query_phrases,
            *record.query_semantic_concepts,
            *record.parsed_operators,
          )
          if isinstance(value, str) and value.strip()
        )
      return any(normalized_search in value for value in haystacks)

    filtered_analytics = tuple(record for record in analytics_records if _matches_search(record))
    feedback_by_query_key: dict[str, list[ProviderProvenanceSchedulerSearchFeedbackRecord]] = {}
    for feedback_record in feedback_records:
      feedback_by_query_key.setdefault(feedback_record.query.strip().lower(), []).append(feedback_record)

    conflicting_query_keys = {
      query_key
      for query_key, grouped_records in feedback_by_query_key.items()
      if {
        self._normalize_provider_provenance_scheduler_search_feedback_signal(record.signal)
        for record in grouped_records
      } >= {"relevant", "not_relevant"}
    }

    def _is_stale_pending(record: ProviderProvenanceSchedulerSearchFeedbackRecord) -> bool:
      if record.moderation_status != "pending":
        return False
      age_seconds = max((current_time - record.recorded_at).total_seconds(), 0.0)
      return age_seconds >= stale_pending_cutoff_seconds

    def _is_high_score_pending(record: ProviderProvenanceSchedulerSearchFeedbackRecord) -> bool:
      return record.moderation_status == "pending" and int(record.score) >= high_score_pending_threshold

    prefiltered_feedback = tuple(
      record
      for record in feedback_records
      if _matches_search(record)
      and (normalized_moderation_status is None or record.moderation_status == normalized_moderation_status)
      and (normalized_signal is None or record.signal == normalized_signal)
    )
    filtered_feedback = tuple(
      record
      for record in prefiltered_feedback
      if (
        normalized_governance_view == "all_feedback"
        or (
          normalized_governance_view == "pending_queue"
          and record.moderation_status == "pending"
        )
        or (
          normalized_governance_view == "stale_pending"
          and _is_stale_pending(record)
        )
        or (
          normalized_governance_view == "high_score_pending"
          and _is_high_score_pending(record)
        )
        or (
          normalized_governance_view == "moderated"
          and record.moderation_status in {"approved", "rejected"}
        )
        or (
          normalized_governance_view == "conflicting_queries"
          and record.query.strip().lower() in conflicting_query_keys
        )
      )
    )

    query_rollups: dict[str, dict[str, Any]] = {}
    filtered_feedback_by_query: dict[str, list[ProviderProvenanceSchedulerSearchFeedbackRecord]] = {}
    for feedback_record in filtered_feedback:
      filtered_feedback_by_query.setdefault(feedback_record.query.strip().lower(), []).append(feedback_record)
    for analytics_record in filtered_analytics:
      query_key = analytics_record.query.strip().lower()
      rollup = query_rollups.setdefault(
        query_key,
        {
          "query": analytics_record.query,
          "query_ids": [],
          "search_count": 0,
          "last_recorded_at": analytics_record.recorded_at,
          "top_score": 0,
          "matched_occurrences_total": 0,
          "semantic_concepts": set(),
          "parsed_operators": set(),
          "relevance_models": set(),
        },
      )
      rollup["query_ids"].append(analytics_record.query_id)
      rollup["search_count"] += 1
      rollup["last_recorded_at"] = max(rollup["last_recorded_at"], analytics_record.recorded_at)
      rollup["top_score"] = max(rollup["top_score"], analytics_record.top_score)
      rollup["matched_occurrences_total"] += analytics_record.matched_occurrences
      rollup["semantic_concepts"].update(analytics_record.query_semantic_concepts)
      rollup["parsed_operators"].update(analytics_record.parsed_operators)
      if isinstance(analytics_record.relevance_model, str) and analytics_record.relevance_model.strip():
        rollup["relevance_models"].add(analytics_record.relevance_model.strip())

    top_queries = []
    for query_key, rollup in sorted(
      query_rollups.items(),
      key=lambda item: (
        item[1]["search_count"],
        item[1]["top_score"],
        item[1]["last_recorded_at"],
        ),
      reverse=True,
    )[:normalized_query_limit]:
      related_feedback = filtered_feedback_by_query.get(query_key, [])
      top_queries.append(
        {
          "query": rollup["query"],
          "query_ids": tuple(rollup["query_ids"]),
          "search_count": int(rollup["search_count"]),
          "last_recorded_at": rollup["last_recorded_at"],
          "top_score": int(rollup["top_score"]),
          "matched_occurrences_total": int(rollup["matched_occurrences_total"]),
          "feedback_count": len(related_feedback),
          "pending_feedback_count": sum(1 for record in related_feedback if record.moderation_status == "pending"),
          "approved_feedback_count": sum(1 for record in related_feedback if record.moderation_status == "approved"),
          "rejected_feedback_count": sum(1 for record in related_feedback if record.moderation_status == "rejected"),
          "semantic_concepts": tuple(sorted(rollup["semantic_concepts"])),
          "parsed_operators": tuple(sorted(rollup["parsed_operators"])),
          "relevance_models": tuple(sorted(rollup["relevance_models"])),
        }
      )

    actor_rollups: dict[str, dict[str, Any]] = {}
    moderator_rollups: dict[str, dict[str, Any]] = {}
    for record in filtered_feedback:
      actor_key = record.actor.strip() if isinstance(record.actor, str) and record.actor.strip() else "operator"
      actor_rollup = actor_rollups.setdefault(
        actor_key,
        {
          "actor": actor_key,
          "feedback_count": 0,
          "pending_feedback_count": 0,
          "approved_feedback_count": 0,
          "rejected_feedback_count": 0,
          "relevant_feedback_count": 0,
          "not_relevant_feedback_count": 0,
        },
      )
      actor_rollup["feedback_count"] += 1
      actor_rollup[f"{record.moderation_status}_feedback_count"] += 1
      actor_rollup[f"{record.signal}_feedback_count"] += 1
      if isinstance(record.moderated_by, str) and record.moderated_by.strip():
        moderator_key = record.moderated_by.strip()
        moderator_rollup = moderator_rollups.setdefault(
          moderator_key,
          {
            "moderated_by": moderator_key,
            "feedback_count": 0,
            "approved_feedback_count": 0,
            "rejected_feedback_count": 0,
            "pending_feedback_count": 0,
            "last_moderated_at": record.moderated_at,
          },
        )
        moderator_rollup["feedback_count"] += 1
        moderator_rollup[f"{record.moderation_status}_feedback_count"] += 1
        if isinstance(record.moderated_at, datetime):
          current_latest = moderator_rollup.get("last_moderated_at")
          moderator_rollup["last_moderated_at"] = (
            max(current_latest, record.moderated_at)
            if isinstance(current_latest, datetime)
            else record.moderated_at
          )

    bucket_anchor_candidates = [current_time]
    bucket_anchor_candidates.extend(record.recorded_at for record in filtered_feedback)
    bucket_anchor_candidates.extend(record.recorded_at for record in filtered_analytics)
    window_anchor = self._normalize_provider_provenance_export_bucket_start(max(bucket_anchor_candidates))
    time_series_started_at = window_anchor - timedelta(days=normalized_window_days - 1)
    time_series: list[dict[str, Any]] = []
    for offset in range(normalized_window_days):
      bucket_start = time_series_started_at + timedelta(days=offset)
      bucket_end = bucket_start + timedelta(days=1)
      bucket_queries = tuple(
        record
        for record in filtered_analytics
        if bucket_start <= self._normalize_provider_provenance_export_bucket_start(record.recorded_at) < bucket_end
      )
      bucket_feedback = tuple(
        record
        for record in filtered_feedback
        if bucket_start <= self._normalize_provider_provenance_export_bucket_start(record.recorded_at) < bucket_end
      )
      bucket_moderated = tuple(
        record
        for record in filtered_feedback
        if isinstance(record.moderated_at, datetime)
        and bucket_start <= self._normalize_provider_provenance_export_bucket_start(record.moderated_at) < bucket_end
      )
      time_series.append(
        {
          "bucket_key": bucket_start.date().isoformat(),
          "bucket_label": bucket_start.strftime("%b %d"),
          "started_at": bucket_start.isoformat(),
          "ended_at": bucket_end.isoformat(),
          "query_count": len(bucket_queries),
          "feedback_count": len(bucket_feedback),
          "pending_feedback_count": sum(1 for record in bucket_feedback if record.moderation_status == "pending"),
          "approved_feedback_count": sum(1 for record in bucket_feedback if record.moderation_status == "approved"),
          "rejected_feedback_count": sum(1 for record in bucket_feedback if record.moderation_status == "rejected"),
          "moderated_feedback_count": len(bucket_moderated),
          "relevant_feedback_count": sum(1 for record in bucket_feedback if record.signal == "relevant"),
          "not_relevant_feedback_count": sum(1 for record in bucket_feedback if record.signal == "not_relevant"),
          "top_score": max((record.top_score for record in bucket_queries), default=0),
          "stale_pending_count": sum(1 for record in bucket_feedback if _is_stale_pending(record)),
        }
      )

    recent_feedback = tuple(
      {
        "feedback_id": record.feedback_id,
        "recorded_at": record.recorded_at,
        "query_id": record.query_id,
        "query": record.query,
        "occurrence_id": record.occurrence_id,
        "signal": record.signal,
        "actor": record.actor,
        "note": record.note,
        "moderation_status": record.moderation_status,
        "moderation_note": record.moderation_note,
        "moderated_at": record.moderated_at,
        "moderated_by": record.moderated_by,
        "matched_fields": tuple(record.matched_fields),
        "semantic_concepts": tuple(record.semantic_concepts),
        "operator_hits": tuple(record.operator_hits),
        "score": record.score,
        "age_hours": int(max((current_time - record.recorded_at).total_seconds(), 0.0) // 3600),
        "stale_pending": _is_stale_pending(record),
        "high_score_pending": _is_high_score_pending(record),
        "query_run_count": len(
          tuple(
            analytics_record
            for analytics_record in filtered_analytics
            if analytics_record.query.strip().lower() == record.query.strip().lower()
          )
        ),
      }
      for record in sorted(
        filtered_feedback,
        key=lambda record: (
          0 if record.moderation_status == "pending" else 1,
          0 if _is_stale_pending(record) else 1,
          -int(record.score),
          record.recorded_at,
        ),
      )[:normalized_feedback_limit]
    )

    return {
      "generated_at": current_time,
      "query": {
        "search": normalized_search,
        "moderation_status": normalized_moderation_status,
        "signal": normalized_signal,
        "governance_view": normalized_governance_view,
        "window_days": normalized_window_days,
        "stale_pending_hours": normalized_stale_pending_hours,
        "query_limit": normalized_query_limit,
        "feedback_limit": normalized_feedback_limit,
      },
      "available_filters": {
        "moderation_statuses": ("pending", "approved", "rejected"),
        "signals": ("relevant", "not_relevant"),
        "governance_views": (
          "all_feedback",
          "pending_queue",
          "stale_pending",
          "high_score_pending",
          "moderated",
          "conflicting_queries",
        ),
      },
      "summary": {
        "query_count": len(filtered_analytics),
        "distinct_query_count": len(query_rollups),
        "feedback_count": len(filtered_feedback),
        "pending_feedback_count": sum(1 for record in filtered_feedback if record.moderation_status == "pending"),
        "approved_feedback_count": sum(1 for record in filtered_feedback if record.moderation_status == "approved"),
        "rejected_feedback_count": sum(1 for record in filtered_feedback if record.moderation_status == "rejected"),
        "relevant_feedback_count": sum(1 for record in filtered_feedback if record.signal == "relevant"),
        "not_relevant_feedback_count": sum(1 for record in filtered_feedback if record.signal == "not_relevant"),
      },
      "quality_dashboard": {
        "window_days": normalized_window_days,
        "window_started_at": window_started_at,
        "window_ended_at": current_time,
        "time_series": tuple(time_series),
        "actor_rollups": tuple(
          {
            "actor": actor_key,
            "feedback_count": int(entry["feedback_count"]),
            "pending_feedback_count": int(entry["pending_feedback_count"]),
            "approved_feedback_count": int(entry["approved_feedback_count"]),
            "rejected_feedback_count": int(entry["rejected_feedback_count"]),
            "relevant_feedback_count": int(entry["relevant_feedback_count"]),
            "not_relevant_feedback_count": int(entry["not_relevant_feedback_count"]),
          }
          for actor_key, entry in sorted(
            actor_rollups.items(),
            key=lambda item: (item[1]["feedback_count"], item[0]),
            reverse=True,
          )
        ),
        "moderator_rollups": tuple(
          {
            "moderated_by": moderator_key,
            "feedback_count": int(entry["feedback_count"]),
            "approved_feedback_count": int(entry["approved_feedback_count"]),
            "rejected_feedback_count": int(entry["rejected_feedback_count"]),
            "pending_feedback_count": int(entry["pending_feedback_count"]),
            "last_moderated_at": (
              entry["last_moderated_at"]
              if isinstance(entry.get("last_moderated_at"), datetime)
              else None
            ),
          }
          for moderator_key, entry in sorted(
            moderator_rollups.items(),
            key=lambda item: (item[1]["feedback_count"], item[0]),
            reverse=True,
          )
        ),
      },
      "moderation_governance": {
        "governance_view": normalized_governance_view,
        "stale_pending_hours": normalized_stale_pending_hours,
        "high_score_pending_threshold": high_score_pending_threshold,
        "pending_feedback_count": sum(1 for record in filtered_feedback if record.moderation_status == "pending"),
        "stale_pending_count": sum(1 for record in filtered_feedback if _is_stale_pending(record)),
        "high_score_pending_count": sum(1 for record in filtered_feedback if _is_high_score_pending(record)),
        "moderated_feedback_count": sum(
          1 for record in filtered_feedback if record.moderation_status in {"approved", "rejected"}
        ),
        "conflicting_query_count": sum(
          1 for query_key in query_rollups if query_key in conflicting_query_keys
        ),
        "approval_rate_pct": (
          int(
            round(
              (
                sum(1 for record in filtered_feedback if record.moderation_status == "approved")
                / max(
                    sum(
                      1
                      for record in filtered_feedback
                      if record.moderation_status in {"approved", "rejected"}
                    ),
                    1,
                  )
              )
              * 100
            )
          )
          if any(record.moderation_status in {"approved", "rejected"} for record in filtered_feedback)
          else 0
        ),
      },
      "top_queries": tuple(top_queries),
      "feedback_items": recent_feedback,
    }
