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


class ProviderProvenanceSearchModerationFeedbackAnalyticsMixin:
  @staticmethod
  def _normalize_provider_provenance_scheduler_search_feedback_signal(
    signal: str | None,
  ) -> str | None:
    if not isinstance(signal, str):
      return None
    normalized = signal.strip().lower().replace("-", "_")
    if normalized in {"relevant", "positive", "helpful", "up"}:
      return "relevant"
    if normalized in {"not_relevant", "negative", "unhelpful", "down"}:
      return "not_relevant"
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_feedback_moderation_status(
    status: str | None,
  ) -> str | None:
    if not isinstance(status, str):
      return None
    normalized = status.strip().lower().replace("-", "_")
    if normalized in {"pending", "approved", "rejected"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_governance_view(
    view: str | None,
  ) -> str | None:
    if not isinstance(view, str):
      return None
    normalized = view.strip().lower().replace("-", "_")
    if normalized in {
      "all_feedback",
      "pending_queue",
      "stale_pending",
      "high_score_pending",
      "moderated",
      "conflicting_queries",
    }:
      return normalized
    return None

  @staticmethod
  def _build_provider_provenance_scheduler_search_query_feature_set(
    parsed_query: Mapping[str, Any],
  ) -> tuple[str, ...]:
    features: list[str] = []
    for term in parsed_query.get("terms", ()) or ():
      if isinstance(term, str) and term.strip():
        features.append(f"term:{term.strip().lower()}")
    for phrase in parsed_query.get("phrases", ()) or ():
      if isinstance(phrase, str) and phrase.strip():
        features.append(f"phrase:{phrase.strip().lower()}")
    for concept in parsed_query.get("semantic_concepts", ()) or ():
      if isinstance(concept, str) and concept.strip():
        features.append(f"concept:{concept.strip().lower()}")
    for operator in parsed_query.get("operators", ()) or ():
      raw_value = operator.get("raw") if isinstance(operator, Mapping) else None
      if isinstance(raw_value, str) and raw_value.strip():
        features.append(f"operator:{raw_value.strip().lower()}")
    return tuple(dict.fromkeys(features))

  def _build_provider_provenance_scheduler_search_tuning_profile(
    self,
    *,
    search_query: str,
    parsed_query: Mapping[str, Any],
  ) -> dict[str, Any]:
    normalized_query = search_query.strip().lower()
    query_features = set(
      self._build_provider_provenance_scheduler_search_query_feature_set(parsed_query)
    )
    feedback_records = self._list_provider_provenance_scheduler_search_feedback_records()
    field_adjustments: dict[str, float] = {}
    semantic_adjustments: dict[str, float] = {}
    operator_adjustments: dict[str, float] = {}
    channel_adjustments = {"lexical": 0.0, "semantic": 0.0, "operator": 0.0}
    contributing_records: list[ProviderProvenanceSchedulerSearchFeedbackRecord] = []

    for record in feedback_records:
      signal = self._normalize_provider_provenance_scheduler_search_feedback_signal(record.signal)
      moderation_status = self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
        record.moderation_status
      )
      if signal is None or moderation_status != "approved":
        continue
      record_query = record.query.strip().lower()
      record_features = {
        *(f"term:{term.strip().lower()}" for term in record.query_terms if isinstance(term, str) and term.strip()),
        *(f"phrase:{phrase.strip().lower()}" for phrase in record.query_phrases if isinstance(phrase, str) and phrase.strip()),
        *(f"concept:{concept.strip().lower()}" for concept in record.query_semantic_concepts if isinstance(concept, str) and concept.strip()),
        *(f"operator:{operator.strip().lower()}" for operator in record.parsed_operators if isinstance(operator, str) and operator.strip()),
      }
      overlap_count = len(query_features.intersection(record_features))
      feature_count = max(len(query_features), 1)
      overlap_ratio = overlap_count / feature_count
      if record_query == normalized_query:
        overlap_ratio = 1.0
      if overlap_ratio <= 0.0:
        continue
      direction = 1.0 if signal == "relevant" else -1.0
      weight = direction * max(0.35, min(overlap_ratio, 1.0))
      contributing_records.append(record)
      for field_name in record.matched_fields:
        if isinstance(field_name, str) and field_name.strip():
          field_adjustments[field_name] = field_adjustments.get(field_name, 0.0) + (weight * 14.0)
      for concept in record.semantic_concepts:
        if isinstance(concept, str) and concept.strip():
          semantic_adjustments[concept] = semantic_adjustments.get(concept, 0.0) + (weight * 18.0)
      for operator_hit in record.operator_hits:
        if isinstance(operator_hit, str) and operator_hit.strip():
          operator_adjustments[operator_hit] = operator_adjustments.get(operator_hit, 0.0) + (weight * 20.0)
      channel_adjustments["lexical"] += weight * (
        1.0 + min(max(record.lexical_score, 0), 500) / 250.0
      )
      channel_adjustments["semantic"] += weight * (
        1.0 + min(max(record.semantic_score, 0), 500) / 250.0
      )
      channel_adjustments["operator"] += weight * (
        1.0 + min(max(record.operator_score, 0), 500) / 250.0
      )

    relevant_count = sum(
      1
      for record in contributing_records
      if self._normalize_provider_provenance_scheduler_search_feedback_signal(record.signal) == "relevant"
    )
    not_relevant_count = sum(
      1
      for record in contributing_records
      if self._normalize_provider_provenance_scheduler_search_feedback_signal(record.signal) == "not_relevant"
    )

    def _clamp_adjustment(value: float, *, limit: int = 40) -> int:
      return int(max(-limit, min(round(value), limit)))

    normalized_field_adjustments = {
      field_name: _clamp_adjustment(score)
      for field_name, score in field_adjustments.items()
      if _clamp_adjustment(score) != 0
    }
    normalized_semantic_adjustments = {
      concept: _clamp_adjustment(score)
      for concept, score in semantic_adjustments.items()
      if _clamp_adjustment(score) != 0
    }
    normalized_operator_adjustments = {
      operator: _clamp_adjustment(score, limit=48)
      for operator, score in operator_adjustments.items()
      if _clamp_adjustment(score, limit=48) != 0
    }
    normalized_channel_adjustments = {
      channel: _clamp_adjustment(score, limit=16)
      for channel, score in channel_adjustments.items()
    }
    tuned_feature_count = (
      len(normalized_field_adjustments)
      + len(normalized_semantic_adjustments)
      + len(normalized_operator_adjustments)
    )
    return {
      "version": (
        "tfidf_field_weight_feedback_v2"
        if contributing_records
        else "tfidf_field_weight_v1"
      ),
      "active": bool(contributing_records),
      "feedback_signal_count": len(contributing_records),
      "relevant_feedback_count": relevant_count,
      "not_relevant_feedback_count": not_relevant_count,
      "field_adjustments": normalized_field_adjustments,
      "semantic_adjustments": normalized_semantic_adjustments,
      "operator_adjustments": normalized_operator_adjustments,
      "channel_adjustments": normalized_channel_adjustments,
      "tuned_feature_count": tuned_feature_count,
    }

  def _record_provider_provenance_scheduler_search_query_analytics(
    self,
    *,
    recorded_at: datetime,
    search_query: str,
    category: str | None,
    status: str | None,
    narrative_facet: str | None,
    parsed_query: Mapping[str, Any],
    matched_rows: tuple[Mapping[str, Any], ...],
    indexed_occurrence_count: int,
    indexed_term_count: int,
    persistence_mode: str,
    relevance_model: str,
    top_cluster_label: str | None,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    record = ProviderProvenanceSchedulerSearchQueryAnalyticsRecord(
      query_id=uuid4().hex[:12],
      recorded_at=recorded_at,
      query=search_query,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="90d",
        recorded_at=recorded_at,
      ),
      category=category,
      status=status,
      narrative_facet=narrative_facet,
      persistence_mode=persistence_mode,
      relevance_model=relevance_model,
      token_count=len(parsed_query.get("terms", ())) + len(parsed_query.get("phrases", ())),
      operator_count=len(parsed_query.get("operators", ())),
      boolean_operator_count=int(parsed_query.get("boolean_operator_count", 0)),
      semantic_concept_count=len(parsed_query.get("semantic_concepts", ())),
      matched_occurrences=len(matched_rows),
      top_score=max(
        (int(row.get("search_match", {}).get("score", 0)) for row in matched_rows),
        default=0,
      ),
      indexed_occurrence_count=indexed_occurrence_count,
      indexed_term_count=indexed_term_count,
      query_terms=tuple(parsed_query.get("terms", ())),
      query_phrases=tuple(parsed_query.get("phrases", ())),
      query_semantic_concepts=tuple(parsed_query.get("semantic_concepts", ())),
      parsed_operators=tuple(
        operator.get("raw")
        for operator in parsed_query.get("operators", ())
        if isinstance(operator.get("raw"), str)
      ),
      matched_occurrence_ids=tuple(
        row["alert"].occurrence_id
        for row in matched_rows
        if isinstance(row.get("alert"), OperatorAlert)
        and isinstance(row["alert"].occurrence_id, str)
      ),
      top_cluster_label=top_cluster_label,
    )
    return self._save_provider_provenance_scheduler_search_query_analytics_record(record)

  def _build_provider_provenance_scheduler_search_analytics_summary(
    self,
    *,
    query_record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
    search_query: str,
    tuning_profile: Mapping[str, Any],
  ) -> dict[str, Any]:
    normalized_query = search_query.strip().lower()
    recent_query_records = tuple(
      record
      for record in self._list_provider_provenance_scheduler_search_query_analytics_records()
      if record.query.strip().lower() == normalized_query
    )
    feedback_records = tuple(
      record
      for record in self._list_provider_provenance_scheduler_search_feedback_records()
      if record.query.strip().lower() == normalized_query
    )
    pending_feedback_count = sum(
      1
      for record in feedback_records
      if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
        record.moderation_status
      ) == "pending"
    )
    approved_feedback_count = sum(
      1
      for record in feedback_records
      if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
        record.moderation_status
      ) == "approved"
    )
    rejected_feedback_count = sum(
      1
      for record in feedback_records
      if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
        record.moderation_status
      ) == "rejected"
    )
    relevant_feedback_count = sum(
      1
      for record in feedback_records
      if self._normalize_provider_provenance_scheduler_search_feedback_signal(record.signal) == "relevant"
    )
    not_relevant_feedback_count = sum(
      1
      for record in feedback_records
      if self._normalize_provider_provenance_scheduler_search_feedback_signal(record.signal) == "not_relevant"
    )
    feedback_count = len(feedback_records)
    helpful_feedback_ratio_pct = (
      int(round((relevant_feedback_count / feedback_count) * 100))
      if feedback_count > 0
      else 0
    )
    return {
      "query_id": query_record.query_id,
      "recorded_at": query_record.recorded_at,
      "recent_query_count": len(recent_query_records),
      "feedback_count": feedback_count,
      "pending_feedback_count": pending_feedback_count,
      "approved_feedback_count": approved_feedback_count,
      "rejected_feedback_count": rejected_feedback_count,
      "relevant_feedback_count": relevant_feedback_count,
      "not_relevant_feedback_count": not_relevant_feedback_count,
      "helpful_feedback_ratio_pct": helpful_feedback_ratio_pct,
      "learned_relevance_active": bool(tuning_profile.get("active")),
      "tuning_profile_version": tuning_profile.get("version"),
      "tuned_feature_count": int(tuning_profile.get("tuned_feature_count", 0)),
      "channel_adjustments": {
        "lexical": int(tuning_profile.get("channel_adjustments", {}).get("lexical", 0)),
        "semantic": int(tuning_profile.get("channel_adjustments", {}).get("semantic", 0)),
        "operator": int(tuning_profile.get("channel_adjustments", {}).get("operator", 0)),
      },
      "top_field_adjustments": tuple(
        {
          "field": field_name,
          "score": score,
        }
        for field_name, score in sorted(
          (tuning_profile.get("field_adjustments", {}) or {}).items(),
          key=lambda item: (-abs(int(item[1])), item[0]),
        )[:5]
      ),
      "top_semantic_adjustments": tuple(
        {
          "concept": concept,
          "score": score,
        }
        for concept, score in sorted(
          (tuning_profile.get("semantic_adjustments", {}) or {}).items(),
          key=lambda item: (-abs(int(item[1])), item[0]),
        )[:5]
      ),
      "top_operator_adjustments": tuple(
        {
          "operator": operator_hit,
          "score": score,
        }
        for operator_hit, score in sorted(
          (tuning_profile.get("operator_adjustments", {}) or {}).items(),
          key=lambda item: (-abs(int(item[1])), item[0]),
        )[:5]
      ),
      "recent_queries": tuple(
        {
          "query_id": record.query_id,
          "recorded_at": record.recorded_at,
          "query": record.query,
          "matched_occurrences": record.matched_occurrences,
          "top_score": record.top_score,
          "relevance_model": record.relevance_model,
        }
        for record in recent_query_records[:5]
      ),
      "recent_feedback": tuple(
        {
          "feedback_id": record.feedback_id,
          "recorded_at": record.recorded_at,
          "occurrence_id": record.occurrence_id,
          "signal": record.signal,
          "moderation_status": record.moderation_status,
          "matched_fields": tuple(record.matched_fields),
          "semantic_concepts": tuple(record.semantic_concepts),
          "operator_hits": tuple(record.operator_hits),
          "note": record.note,
          "moderation_note": record.moderation_note,
        }
        for record in feedback_records[:5]
      ),
    }
