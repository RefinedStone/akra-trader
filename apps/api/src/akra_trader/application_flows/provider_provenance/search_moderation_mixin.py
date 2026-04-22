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


class ProviderProvenanceSearchModerationMixin:
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

  def record_provider_provenance_scheduler_alert_search_feedback(
    self,
    *,
    query_id: str,
    query: str,
    occurrence_id: str,
    signal: str,
    matched_fields: tuple[str, ...] | list[str] = (),
    semantic_concepts: tuple[str, ...] | list[str] = (),
    operator_hits: tuple[str, ...] | list[str] = (),
    lexical_score: int = 0,
    semantic_score: int = 0,
    operator_score: int = 0,
    score: int = 0,
    ranking_reason: str | None = None,
    note: str | None = None,
    actor: str = "operator",
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    normalized_signal = self._normalize_provider_provenance_scheduler_search_feedback_signal(signal)
    if normalized_signal is None:
      raise ValueError("Scheduler search feedback signal must be relevant or not_relevant.")
    normalized_query_id = query_id.strip() if isinstance(query_id, str) and query_id.strip() else None
    normalized_query = query.strip() if isinstance(query, str) and query.strip() else None
    normalized_occurrence_id = (
      occurrence_id.strip()
      if isinstance(occurrence_id, str) and occurrence_id.strip()
      else None
    )
    if normalized_query_id is None or normalized_query is None or normalized_occurrence_id is None:
      raise ValueError("Scheduler search feedback requires query_id, query, and occurrence_id.")
    analytics_record = next(
      (
        record
        for record in self._list_provider_provenance_scheduler_search_query_analytics_records()
        if record.query_id == normalized_query_id
      ),
      None,
    )
    feedback_record = ProviderProvenanceSchedulerSearchFeedbackRecord(
      feedback_id=uuid4().hex[:12],
      recorded_at=self._clock(),
      query_id=normalized_query_id,
      query=normalized_query,
      occurrence_id=normalized_occurrence_id,
      signal=normalized_signal,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="90d",
        recorded_at=self._clock(),
      ),
      actor=actor.strip() if isinstance(actor, str) and actor.strip() else "operator",
      note=note.strip() if isinstance(note, str) and note.strip() else None,
      category=analytics_record.category if analytics_record is not None else None,
      status=analytics_record.status if analytics_record is not None else None,
      narrative_facet=analytics_record.narrative_facet if analytics_record is not None else None,
      query_terms=analytics_record.query_terms if analytics_record is not None else (),
      query_phrases=analytics_record.query_phrases if analytics_record is not None else (),
      query_semantic_concepts=(
        analytics_record.query_semantic_concepts if analytics_record is not None else ()
      ),
      parsed_operators=analytics_record.parsed_operators if analytics_record is not None else (),
      matched_fields=tuple(
        value.strip()
        for value in matched_fields
        if isinstance(value, str) and value.strip()
      ),
      semantic_concepts=tuple(
        value.strip()
        for value in semantic_concepts
        if isinstance(value, str) and value.strip()
      ),
      operator_hits=tuple(
        value.strip()
        for value in operator_hits
        if isinstance(value, str) and value.strip()
      ),
      lexical_score=max(int(lexical_score), 0),
      semantic_score=max(int(semantic_score), 0),
      operator_score=max(int(operator_score), 0),
      score=max(int(score), 0),
      ranking_reason=(
        ranking_reason.strip()
        if isinstance(ranking_reason, str) and ranking_reason.strip()
        else None
      ),
      source_tab_id=(
        source_tab_id.strip()
        if isinstance(source_tab_id, str) and source_tab_id.strip()
        else None
      ),
      source_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
      moderation_status="pending",
    )
    saved_feedback = self._save_provider_provenance_scheduler_search_feedback_record(
      feedback_record
    )
    feedback_records = tuple(
      record
      for record in self._list_provider_provenance_scheduler_search_feedback_records()
      if record.query.strip().lower() == normalized_query.lower()
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
    total_feedback_count = len(feedback_records)
    return {
      "feedback_id": saved_feedback.feedback_id,
      "query_id": saved_feedback.query_id,
      "query": saved_feedback.query,
      "occurrence_id": saved_feedback.occurrence_id,
      "signal": saved_feedback.signal,
      "moderation_status": saved_feedback.moderation_status,
      "feedback_count": total_feedback_count,
      "pending_feedback_count": sum(
        1
        for record in feedback_records
        if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
          record.moderation_status
        ) == "pending"
      ),
      "approved_feedback_count": sum(
        1
        for record in feedback_records
        if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
          record.moderation_status
        ) == "approved"
      ),
      "rejected_feedback_count": sum(
        1
        for record in feedback_records
        if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
          record.moderation_status
        ) == "rejected"
      ),
      "relevant_feedback_count": relevant_feedback_count,
      "not_relevant_feedback_count": not_relevant_feedback_count,
      "helpful_feedback_ratio_pct": (
        int(round((relevant_feedback_count / total_feedback_count) * 100))
        if total_feedback_count > 0
        else 0
      ),
      "learned_relevance_hint": (
        "Feedback captured and queued for moderation before it influences learned ranking."
        if total_feedback_count > 0
        else "Feedback recorded."
      ),
    }

  def moderate_provider_provenance_scheduler_search_feedback(
    self,
    *,
    feedback_id: str,
    moderation_status: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    normalized_feedback_id = (
      feedback_id.strip() if isinstance(feedback_id, str) and feedback_id.strip() else None
    )
    normalized_status = self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      moderation_status
    )
    if normalized_feedback_id is None or normalized_status is None:
      raise ValueError("Scheduler search feedback moderation requires feedback_id and a valid status.")
    current_record = next(
      (
        record
        for record in self._list_provider_provenance_scheduler_search_feedback_records()
        if record.feedback_id == normalized_feedback_id
      ),
      None,
    )
    if current_record is None:
      raise LookupError(f"Scheduler search feedback {normalized_feedback_id} was not found.")
    moderated_at = self._clock()
    updated_record = replace(
      current_record,
      moderation_status=normalized_status,
      moderation_note=note.strip() if isinstance(note, str) and note.strip() else None,
      moderated_at=moderated_at,
      moderated_by=actor.strip() if isinstance(actor, str) and actor.strip() else "operator",
      moderated_by_tab_id=(
        source_tab_id.strip()
        if isinstance(source_tab_id, str) and source_tab_id.strip()
        else None
      ),
      moderated_by_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
    )
    saved_record = self._save_provider_provenance_scheduler_search_feedback_record(updated_record)
    sibling_feedback = tuple(
      record
      for record in self._list_provider_provenance_scheduler_search_feedback_records()
      if record.query.strip().lower() == saved_record.query.strip().lower()
    )
    return {
      "feedback_id": saved_record.feedback_id,
      "query_id": saved_record.query_id,
      "occurrence_id": saved_record.occurrence_id,
      "moderation_status": saved_record.moderation_status,
      "moderated_at": saved_record.moderated_at,
      "moderated_by": saved_record.moderated_by,
      "moderation_note": saved_record.moderation_note,
      "pending_feedback_count": sum(
        1
        for record in sibling_feedback
        if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
          record.moderation_status
        ) == "pending"
      ),
      "approved_feedback_count": sum(
        1
        for record in sibling_feedback
        if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
          record.moderation_status
        ) == "approved"
      ),
      "rejected_feedback_count": sum(
        1
        for record in sibling_feedback
        if self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
          record.moderation_status
        ) == "rejected"
      ),
      "learned_relevance_hint": (
        "Approved feedback will now contribute to learned scheduler ranking."
        if normalized_status == "approved"
        else "Rejected feedback is excluded from learned scheduler ranking."
      ),
    }

  def moderate_provider_provenance_scheduler_search_feedback_batch(
    self,
    *,
    feedback_ids: tuple[str, ...] | list[str],
    moderation_status: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    normalized_status = self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      moderation_status
    )
    if normalized_status is None:
      raise ValueError("Scheduler search feedback batch moderation requires a valid status.")
    normalized_feedback_ids = tuple(
      dict.fromkeys(
        feedback_id.strip()
        for feedback_id in feedback_ids
        if isinstance(feedback_id, str) and feedback_id.strip()
      )
    )
    if not normalized_feedback_ids:
      raise ValueError("Scheduler search feedback batch moderation requires at least one feedback id.")
    results: list[dict[str, Any]] = []
    for feedback_id in normalized_feedback_ids:
      try:
        moderation_result = self.moderate_provider_provenance_scheduler_search_feedback(
          feedback_id=feedback_id,
          moderation_status=normalized_status,
          actor=actor,
          note=note,
          source_tab_id=source_tab_id,
          source_tab_label=source_tab_label,
        )
      except LookupError as exc:
        results.append(
          {
            "feedback_id": feedback_id,
            "outcome": "missing",
            "message": str(exc),
          }
        )
        continue
      results.append(
        {
          "feedback_id": feedback_id,
          "outcome": "updated",
          "moderation_status": moderation_result.get("moderation_status"),
          "moderated_at": moderation_result.get("moderated_at"),
          "moderated_by": moderation_result.get("moderated_by"),
        }
      )
    succeeded_count = sum(1 for item in results if item.get("outcome") == "updated")
    missing_count = sum(1 for item in results if item.get("outcome") == "missing")
    return {
      "moderation_status": normalized_status,
      "requested_count": len(normalized_feedback_ids),
      "updated_count": succeeded_count,
      "missing_count": missing_count,
      "results": tuple(results),
      "learned_relevance_hint": (
        "Approved feedback will now contribute to learned scheduler ranking."
        if normalized_status == "approved"
        else "Rejected feedback is excluded from learned scheduler ranking."
      ),
    }

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

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_plan_status(
    status: str | None,
  ) -> str | None:
    if not isinstance(status, str):
      return None
    normalized = status.strip().lower().replace("-", "_")
    if normalized in {"previewed", "approved", "applied"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_plan_queue_state(
    queue_state: str | None,
  ) -> str | None:
    if not isinstance(queue_state, str):
      return None
    normalized = queue_state.strip().lower().replace("-", "_")
    if normalized in {"pending_approval", "ready_to_apply", "completed"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
    action: str | None,
  ) -> str | None:
    if not isinstance(action, str):
      return None
    normalized = action.strip().lower().replace("-", "_")
    if normalized in {"update", "delete", "restore"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action_scope(
    action_scope: str | None,
  ) -> str | None:
    if not isinstance(action_scope, str):
      return None
    normalized = action_scope.strip().lower().replace("-", "_")
    if normalized in {"any", "update", "delete", "restore"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_status(
    status: str | None,
  ) -> str | None:
    if not isinstance(status, str):
      return None
    normalized = status.strip().lower().replace("-", "_")
    if normalized in {"previewed", "approved", "applied"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_queue_state(
    queue_state: str | None,
  ) -> str | None:
    if not isinstance(queue_state, str):
      return None
    normalized = queue_state.strip().lower().replace("-", "_")
    if normalized in {"pending_approval", "ready_to_apply", "completed"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status(
    status: str | None,
  ) -> str:
    return normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status_support(
      status
    )

  def _build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    return build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support(
      self,
      record=record,
      action=action,
      reason=reason,
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  @staticmethod
  def _build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail(
    *,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    action: str,
  ) -> str:
    return build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail_support(
      record=record,
      action=action,
    )

  def _record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support(
      self,
      record=record,
      action=action,
      reason=reason,
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
    status: str | None,
  ) -> str:
    if not isinstance(status, str):
      return "active"
    normalized = status.strip().lower().replace("-", "_")
    return "deleted" if normalized == "deleted" else "active"

  def _build_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()
      if revision.catalog_id == record.catalog_id
    )
    return ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord(
      revision_id=f"{record.catalog_id}:r{revision_count + 1:04d}",
      catalog_id=record.catalog_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      scheduler_key=record.scheduler_key,
      status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
        record.status
      ),
      default_moderation_status=record.default_moderation_status,
      governance_view=record.governance_view,
      window_days=record.window_days,
      stale_pending_hours=record.stale_pending_hours,
      minimum_score=record.minimum_score,
      require_note=record.require_note,
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  @staticmethod
  def _build_provider_provenance_scheduler_search_moderation_policy_catalog_audit_detail(
    *,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    action: str,
  ) -> str:
    default_summary = (
      f"{record.default_moderation_status} @ {record.minimum_score}+"
      if record.minimum_score > 0
      else record.default_moderation_status
    )
    governance_summary = (
      f"{record.governance_view} / {record.window_days}d / stale {record.stale_pending_hours}h"
    )
    if action == "created":
      return (
        f"Created moderation policy catalog {record.name} with {default_summary}; "
        f"view {governance_summary}; note {'required' if record.require_note else 'optional'}."
      )
    if action == "updated":
      return (
        f"Updated moderation policy catalog {record.name}; "
        f"{default_summary}; view {governance_summary}."
      )
    if action == "deleted":
      return f"Deleted moderation policy catalog {record.name}."
    if action == "restored":
      return f"Restored moderation policy catalog {record.name}."
    if action == "bulk_updated":
      return f"Bulk-updated moderation policy catalog {record.name}."
    if action == "bulk_deleted":
      return f"Bulk-deleted moderation policy catalog {record.name}."
    if action == "bulk_restored":
      return f"Bulk-restored moderation policy catalog {record.name}."
    return f"Recorded moderation policy catalog action {action} for {record.name}."

  def _record_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    revision = self._save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
      self._build_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    saved = self._save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
      replace(
        record,
        status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
          record.status
        ),
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
      ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord(
        audit_id=uuid4().hex[:12],
        catalog_id=saved.catalog_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_search_moderation_policy_catalog_audit_detail(
          record=saved,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        scheduler_key=saved.scheduler_key,
        name=saved.name,
        status=saved.status,
        default_moderation_status=saved.default_moderation_status,
        governance_view=saved.governance_view,
        window_days=saved.window_days,
        stale_pending_hours=saved.stale_pending_hours,
        minimum_score=saved.minimum_score,
        require_note=saved.require_note,
        actor_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        actor_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
      )
    )
    return saved

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> dict[str, Any]:
    return {
      "catalog_id": record.catalog_id,
      "created_at": record.created_at,
      "updated_at": record.updated_at,
      "scheduler_key": record.scheduler_key,
      "name": record.name,
      "description": record.description,
      "status": record.status,
      "default_moderation_status": record.default_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "current_revision_id": record.current_revision_id,
      "revision_count": record.revision_count,
      "created_by_tab_id": record.created_by_tab_id,
      "created_by_tab_label": record.created_by_tab_label,
      "deleted_at": record.deleted_at,
      "deleted_by_tab_id": record.deleted_by_tab_id,
      "deleted_by_tab_label": record.deleted_by_tab_label,
    }

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> dict[str, Any]:
    return {
      "revision_id": record.revision_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "reason": record.reason,
      "name": record.name,
      "description": record.description,
      "scheduler_key": record.scheduler_key,
      "status": record.status,
      "default_moderation_status": record.default_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "recorded_at": record.recorded_at,
      "source_revision_id": record.source_revision_id,
      "recorded_by_tab_id": record.recorded_by_tab_id,
      "recorded_by_tab_label": record.recorded_by_tab_label,
    }

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> dict[str, Any]:
    return {
      "audit_id": record.audit_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "recorded_at": record.recorded_at,
      "reason": record.reason,
      "detail": record.detail,
      "revision_id": record.revision_id,
      "source_revision_id": record.source_revision_id,
      "scheduler_key": record.scheduler_key,
      "name": record.name,
      "status": record.status,
      "default_moderation_status": record.default_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "actor_tab_id": record.actor_tab_id,
      "actor_tab_label": record.actor_tab_label,
    }

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_plan_preview_item(
    item: ProviderProvenanceSchedulerSearchModerationPlanPreviewItem,
  ) -> dict[str, Any]:
    return {
      "feedback_id": item.feedback_id,
      "occurrence_id": item.occurrence_id,
      "query": item.query,
      "signal": item.signal,
      "current_moderation_status": item.current_moderation_status,
      "proposed_moderation_status": item.proposed_moderation_status,
      "score": item.score,
      "age_hours": item.age_hours,
      "stale_pending": item.stale_pending,
      "high_score_pending": item.high_score_pending,
      "query_run_count": item.query_run_count,
      "eligible": item.eligible,
      "reason_tags": tuple(item.reason_tags),
      "matched_fields": tuple(item.matched_fields),
      "semantic_concepts": tuple(item.semantic_concepts),
      "operator_hits": tuple(item.operator_hits),
      "note": item.note,
      "ranking_reason": item.ranking_reason,
    }

  def _serialize_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> dict[str, Any]:
    return {
      "plan_id": record.plan_id,
      "created_at": record.created_at,
      "updated_at": record.updated_at,
      "scheduler_key": record.scheduler_key,
      "status": record.status,
      "queue_state": record.queue_state,
      "policy_catalog_id": record.policy_catalog_id,
      "policy_catalog_name": record.policy_catalog_name,
      "proposed_moderation_status": record.proposed_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "requested_feedback_ids": tuple(record.requested_feedback_ids),
      "feedback_ids": tuple(record.feedback_ids),
      "missing_feedback_ids": tuple(record.missing_feedback_ids),
      "preview_count": len(record.preview_items),
      "preview_items": tuple(
        self._serialize_provider_provenance_scheduler_search_moderation_plan_preview_item(item)
        for item in record.preview_items
      ),
      "created_by": record.created_by,
      "created_by_tab_id": record.created_by_tab_id,
      "created_by_tab_label": record.created_by_tab_label,
      "approved_at": record.approved_at,
      "approved_by": record.approved_by,
      "approved_by_tab_id": record.approved_by_tab_id,
      "approved_by_tab_label": record.approved_by_tab_label,
      "approval_note": record.approval_note,
      "applied_at": record.applied_at,
      "applied_by": record.applied_by,
      "applied_by_tab_id": record.applied_by_tab_id,
      "applied_by_tab_label": record.applied_by_tab_label,
      "apply_note": record.apply_note,
      "applied_result": record.applied_result,
    }

  def _get_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    normalized_catalog_id = catalog_id.strip() if isinstance(catalog_id, str) else ""
    for record in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_records():
      if record.catalog_id == normalized_catalog_id:
        return replace(
          record,
          status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
            record.status
          ),
        )
    raise LookupError("Scheduler search moderation policy catalog not found.")

  def _load_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord | None:
    normalized_revision_id = revision_id.strip() if isinstance(revision_id, str) else ""
    if not normalized_revision_id:
      return None
    for revision in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records():
      if revision.revision_id == normalized_revision_id:
        return revision
    return None

  def _get_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    normalized_plan_id = plan_id.strip() if isinstance(plan_id, str) else ""
    for record in self._list_provider_provenance_scheduler_search_moderation_plan_records():
      if record.plan_id == normalized_plan_id:
        return record
    raise LookupError("Scheduler search moderation plan not found.")

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item(
    item: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item_support(
      item
    )

  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support(
      record
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    governance_policy_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support(
      self,
      governance_policy_id,
    )

  def _load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord | None:
    return load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support(
      self,
      revision_id,
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support(
      self,
      plan_id,
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item(
    item: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item_support(
      item
    )

  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support(
      record
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    meta_policy_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support(
      self,
      meta_policy_id,
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support(
      self,
      plan_id,
    )

  def create_provider_provenance_scheduler_search_moderation_policy_catalog(
    self,
    *,
    name: str,
    description: str = "",
    default_moderation_status: str = "approved",
    governance_view: str = "pending_queue",
    window_days: int = 30,
    stale_pending_hours: int = 24,
    minimum_score: int = 0,
    require_note: bool = False,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> dict[str, Any]:
    normalized_name = self._normalize_provider_provenance_workspace_name(
      name,
      field_name="scheduler search moderation policy catalog name",
    )
    normalized_default_status = self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      default_moderation_status
    )
    normalized_governance_view = self._normalize_provider_provenance_scheduler_search_governance_view(
      governance_view
    )
    if normalized_default_status is None or normalized_governance_view is None:
      raise ValueError("Scheduler search moderation policy catalogs require a name, moderation status, and governance view.")
    current_time = self._clock()
    record = ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord(
      catalog_id=uuid4().hex[:12],
      created_at=current_time,
      updated_at=current_time,
      name=normalized_name,
      description=description.strip() if isinstance(description, str) else "",
      default_moderation_status=normalized_default_status,
      governance_view=normalized_governance_view,
      window_days=max(7, min(int(window_days), 180)),
      stale_pending_hours=max(1, min(int(stale_pending_hours), 24 * 30)),
      minimum_score=max(int(minimum_score), 0),
      require_note=bool(require_note),
      created_by_tab_id=(
        created_by_tab_id.strip()
        if isinstance(created_by_tab_id, str) and created_by_tab_id.strip()
        else None
      ),
      created_by_tab_label=(
        created_by_tab_label.strip()
        if isinstance(created_by_tab_label, str) and created_by_tab_label.strip()
        else None
      ),
    )
    saved = self._record_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
      record=record,
      action="created",
      reason="scheduler_search_moderation_policy_catalog_created",
      recorded_at=current_time,
      actor_tab_id=created_by_tab_id,
      actor_tab_label=created_by_tab_label,
    )
    return self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(saved)

  def list_provider_provenance_scheduler_search_moderation_policy_catalogs(
    self,
  ) -> dict[str, Any]:
    records = self._list_provider_provenance_scheduler_search_moderation_policy_catalog_records()
    return {
      "generated_at": self._clock(),
      "total": len(records),
      "items": tuple(
        self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(
          replace(
            record,
            status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
              record.status
            ),
          )
        )
        for record in records
      ),
    }

  def update_provider_provenance_scheduler_search_moderation_policy_catalog(
    self,
    catalog_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    default_moderation_status: str | None = None,
    governance_view: str | None = None,
    window_days: int | None = None,
    stale_pending_hours: int | None = None,
    minimum_score: int | None = None,
    require_note: bool | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_search_moderation_policy_catalog_updated",
  ) -> dict[str, Any]:
    current = self._get_provider_provenance_scheduler_search_moderation_policy_catalog_record(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler search moderation policy catalogs must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler search moderation policy catalog name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = (
      description.strip() if isinstance(description, str) else current.description
    )
    updated_default_status = (
      self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
        default_moderation_status
      )
      if default_moderation_status is not None
      else current.default_moderation_status
    )
    updated_governance_view = (
      self._normalize_provider_provenance_scheduler_search_governance_view(governance_view)
      if governance_view is not None
      else current.governance_view
    )
    if updated_default_status is None or updated_governance_view is None:
      raise ValueError("Scheduler search moderation policy catalogs require a valid moderation status and governance view.")
    updated_window_days = (
      max(7, min(int(window_days), 180))
      if window_days is not None
      else current.window_days
    )
    updated_stale_pending_hours = (
      max(1, min(int(stale_pending_hours), 24 * 30))
      if stale_pending_hours is not None
      else current.stale_pending_hours
    )
    updated_minimum_score = (
      max(int(minimum_score), 0)
      if minimum_score is not None
      else current.minimum_score
    )
    updated_require_note = (
      bool(require_note)
      if require_note is not None
      else current.require_note
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_default_status == current.default_moderation_status
      and updated_governance_view == current.governance_view
      and updated_window_days == current.window_days
      and updated_stale_pending_hours == current.stale_pending_hours
      and updated_minimum_score == current.minimum_score
      and updated_require_note == current.require_note
    ):
      return self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(
        current
      )
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      default_moderation_status=updated_default_status,
      governance_view=updated_governance_view,
      window_days=updated_window_days,
      stale_pending_hours=updated_stale_pending_hours,
      minimum_score=updated_minimum_score,
      require_note=updated_require_note,
      updated_at=self._clock(),
    )
    saved = self._record_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
    return self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(saved)

  def delete_provider_provenance_scheduler_search_moderation_policy_catalog(
    self,
    catalog_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_search_moderation_policy_catalog_deleted",
  ) -> dict[str, Any]:
    current = self._get_provider_provenance_scheduler_search_moderation_policy_catalog_record(catalog_id)
    if current.status == "deleted":
      return self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(
        current
      )
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    saved = self._record_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
    return self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(saved)

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_revisions(
    self,
    catalog_id: str,
  ) -> dict[str, Any]:
    current = self._get_provider_provenance_scheduler_search_moderation_policy_catalog_record(catalog_id)
    revisions = tuple(
      self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
        replace(
          revision,
          status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
            revision.status
          ),
        )
      )
      for revision in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()
      if revision.catalog_id == current.catalog_id
    )
    return {
      "catalog": self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(
        current
      ),
      "history": revisions,
    }

  def restore_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
    self,
    catalog_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_search_moderation_policy_catalog_revision_restored",
  ) -> dict[str, Any]:
    current = self._get_provider_provenance_scheduler_search_moderation_policy_catalog_record(catalog_id)
    revision = self._load_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
      revision_id
    )
    if revision is None or revision.catalog_id != current.catalog_id:
      raise LookupError("Scheduler search moderation policy catalog revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      status="active",
      default_moderation_status=revision.default_moderation_status,
      governance_view=revision.governance_view,
      window_days=revision.window_days,
      stale_pending_hours=revision.stale_pending_hours,
      minimum_score=revision.minimum_score,
      require_note=revision.require_note,
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    saved = self._record_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
    return self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(saved)

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_audits(
    self,
    *,
    catalog_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> dict[str, Any]:
    normalized_catalog_id = catalog_id.strip() if isinstance(catalog_id, str) and catalog_id.strip() else None
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip() if isinstance(actor_tab_id, str) and actor_tab_id.strip() else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[dict[str, Any]] = []
    for audit in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records():
      if normalized_catalog_id is not None and audit.catalog_id != normalized_catalog_id:
        continue
      if normalized_action is not None and audit.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and audit.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          audit.audit_id,
          audit.catalog_id,
          audit.action,
          audit.reason,
          audit.detail,
          audit.revision_id,
          audit.source_revision_id,
          audit.name,
          audit.status,
          audit.default_moderation_status,
          audit.governance_view,
          audit.actor_tab_id,
          audit.actor_tab_label,
        ),
        search=search,
      ):
        continue
      filtered.append(
        self._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
          replace(
            audit,
            status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
              audit.status
            ),
          )
        )
      )
    return {
      "items": tuple(filtered[:normalized_limit]),
      "total": len(filtered),
    }

  def bulk_govern_provider_provenance_scheduler_search_moderation_policy_catalogs(
    self,
    *,
    catalog_ids: Iterable[str],
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    default_moderation_status: str | None = None,
    governance_view: str | None = None,
    window_days: int | None = None,
    stale_pending_hours: int | None = None,
    minimum_score: int | None = None,
    require_note: bool | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler search moderation policy catalog bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(catalog_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    normalized_default_status = (
      self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
        default_moderation_status
      )
      if default_moderation_status is not None
      else None
    )
    normalized_governance_view = (
      self._normalize_provider_provenance_scheduler_search_governance_view(governance_view)
      if governance_view is not None
      else None
    )
    if default_moderation_status is not None and normalized_default_status is None:
      raise ValueError("Bulk moderation policy catalog update requires a valid default moderation status.")
    if governance_view is not None and normalized_governance_view is None:
      raise ValueError("Bulk moderation policy catalog update requires a valid governance view.")
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and normalized_default_status is None
      and normalized_governance_view is None
      and window_days is None
      and stale_pending_hours is None
      and minimum_score is None
      and require_note is None
    ):
      raise ValueError("No scheduler search moderation policy catalog bulk update fields were provided.")
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_search_moderation_policy_catalog_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_search_moderation_policy_catalog_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_search_moderation_policy_catalog_bulk_updated"
        )
      )
    )
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for catalog_id_item in normalized_ids:
      try:
        current = self._get_provider_provenance_scheduler_search_moderation_policy_catalog_record(
          catalog_id_item
        )
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_search_moderation_policy_catalog(
            current.catalog_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is already active.",
              )
            )
            continue
          revision_id = current.current_revision_id
          if not revision_id:
            raise LookupError("Deleted moderation policy catalog does not have a current revision to restore.")
          updated = self.restore_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
            current.catalog_id,
            revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Restore the catalog before editing it.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_search_moderation_policy_catalog(
            current.catalog_id,
            name=(
              f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
              if normalized_name_prefix is not None or normalized_name_suffix is not None
              else None
            ),
            description=(
              f"{current.description}{normalized_description_append}"
              if normalized_description_append is not None
              else None
            ),
            default_moderation_status=normalized_default_status,
            governance_view=normalized_governance_view,
            window_days=window_days,
            stale_pending_hours=stale_pending_hours,
            minimum_score=minimum_score,
            require_note=require_note,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        updated_status = str(updated.get("status", current.status))
        updated_revision_id = updated.get("current_revision_id")
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=current.catalog_id,
            item_name=str(updated.get("name", current.name)),
            outcome="applied",
            status=updated_status,
            current_revision_id=updated_revision_id if isinstance(updated_revision_id, str) else None,
            message=(
              "Catalog deleted."
              if normalized_action == "delete"
              else ("Catalog restored." if normalized_action == "restore" else "Catalog updated.")
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=catalog_id_item,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="scheduler_search_moderation_policy_catalog",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def stage_provider_provenance_scheduler_search_moderation_plan(
    self,
    *,
    feedback_ids: tuple[str, ...] | list[str],
    policy_catalog_id: str | None = None,
    moderation_status: str | None = None,
    actor: str = "operator",
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    normalized_feedback_ids = tuple(
      dict.fromkeys(
        feedback_id.strip()
        for feedback_id in feedback_ids
        if isinstance(feedback_id, str) and feedback_id.strip()
      )
    )
    if not normalized_feedback_ids:
      raise ValueError("Select at least one scheduler search feedback item to stage.")
    resolved_catalog = None
    if isinstance(policy_catalog_id, str) and policy_catalog_id.strip():
      resolved_catalog = self._get_provider_provenance_scheduler_search_moderation_policy_catalog_record(
        policy_catalog_id
      )
      if resolved_catalog.status != "active":
        raise ValueError("Selected scheduler search moderation policy catalog must be active.")
    normalized_status = self._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      moderation_status
    ) or (
      resolved_catalog.default_moderation_status if resolved_catalog is not None else "approved"
    )
    if normalized_status is None:
      raise ValueError("Scheduler search moderation plans require a valid moderation status.")
    normalized_governance_view = (
      resolved_catalog.governance_view if resolved_catalog is not None else "pending_queue"
    )
    normalized_window_days = (
      resolved_catalog.window_days if resolved_catalog is not None else 30
    )
    normalized_stale_pending_hours = (
      resolved_catalog.stale_pending_hours if resolved_catalog is not None else 24
    )
    minimum_score = resolved_catalog.minimum_score if resolved_catalog is not None else 0
    require_note = resolved_catalog.require_note if resolved_catalog is not None else False
    current_time = self._clock()
    feedback_lookup = {
      record.feedback_id: record
      for record in self._list_provider_provenance_scheduler_search_feedback_records()
    }
    analytics_window_started_at = current_time - timedelta(days=normalized_window_days)
    analytics_lookup: dict[str, int] = {}
    for record in self._list_provider_provenance_scheduler_search_query_analytics_records():
      if record.recorded_at < analytics_window_started_at:
        continue
      query_key = record.query.strip().lower()
      analytics_lookup[query_key] = analytics_lookup.get(query_key, 0) + 1
    stale_pending_cutoff_seconds = normalized_stale_pending_hours * 3600
    high_score_pending_threshold = 150
    preview_items: list[ProviderProvenanceSchedulerSearchModerationPlanPreviewItem] = []
    eligible_feedback_ids: list[str] = []
    missing_feedback_ids: list[str] = []
    for feedback_id in normalized_feedback_ids:
      record = feedback_lookup.get(feedback_id)
      if record is None:
        missing_feedback_ids.append(feedback_id)
        continue
      age_hours = int(max((current_time - record.recorded_at).total_seconds(), 0.0) // 3600)
      stale_pending = (
        record.moderation_status == "pending"
        and max((current_time - record.recorded_at).total_seconds(), 0.0) >= stale_pending_cutoff_seconds
      )
      high_score_pending = (
        record.moderation_status == "pending"
        and int(record.score) >= high_score_pending_threshold
      )
      eligible = int(record.score) >= int(minimum_score)
      reason_tags: list[str] = []
      if stale_pending:
        reason_tags.append("stale_pending")
      if high_score_pending:
        reason_tags.append("high_score_pending")
      if not eligible:
        reason_tags.append("below_minimum_score")
      preview_items.append(
        ProviderProvenanceSchedulerSearchModerationPlanPreviewItem(
          feedback_id=record.feedback_id,
          occurrence_id=record.occurrence_id,
          query=record.query,
          signal=record.signal,
          current_moderation_status=record.moderation_status,
          proposed_moderation_status=normalized_status,
          score=int(record.score),
          age_hours=age_hours,
          stale_pending=stale_pending,
          high_score_pending=high_score_pending,
          query_run_count=analytics_lookup.get(record.query.strip().lower(), 0),
          eligible=eligible,
          reason_tags=tuple(reason_tags),
          matched_fields=tuple(record.matched_fields),
          semantic_concepts=tuple(record.semantic_concepts),
          operator_hits=tuple(record.operator_hits),
          note=record.note,
          ranking_reason=record.ranking_reason,
        )
      )
      if eligible:
        eligible_feedback_ids.append(record.feedback_id)
    if not eligible_feedback_ids:
      raise ValueError("No selected scheduler search feedback items satisfy the staged moderation policy.")
    plan_record = ProviderProvenanceSchedulerSearchModerationPlanRecord(
      plan_id=uuid4().hex[:12],
      created_at=current_time,
      updated_at=current_time,
      status="previewed",
      queue_state="pending_approval",
      policy_catalog_id=resolved_catalog.catalog_id if resolved_catalog is not None else None,
      policy_catalog_name=resolved_catalog.name if resolved_catalog is not None else None,
      proposed_moderation_status=normalized_status,
      governance_view=normalized_governance_view,
      window_days=normalized_window_days,
      stale_pending_hours=normalized_stale_pending_hours,
      minimum_score=int(minimum_score),
      require_note=bool(require_note),
      requested_feedback_ids=normalized_feedback_ids,
      feedback_ids=tuple(eligible_feedback_ids),
      missing_feedback_ids=tuple(missing_feedback_ids),
      preview_items=tuple(preview_items),
      created_by=actor.strip() if isinstance(actor, str) and actor.strip() else "operator",
      created_by_tab_id=(
        source_tab_id.strip()
        if isinstance(source_tab_id, str) and source_tab_id.strip()
        else None
      ),
      created_by_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
    )
    saved = self._save_provider_provenance_scheduler_search_moderation_plan_record(plan_record)
    return self._serialize_provider_provenance_scheduler_search_moderation_plan_record(saved)

  def list_provider_provenance_scheduler_search_moderation_plans(
    self,
    *,
    queue_state: str | None = None,
    policy_catalog_id: str | None = None,
  ) -> dict[str, Any]:
    records = self._list_provider_provenance_scheduler_search_moderation_plan_records()
    normalized_queue_state = (
      self._normalize_provider_provenance_scheduler_search_moderation_plan_queue_state(
        queue_state
      )
      if isinstance(queue_state, str) and queue_state.strip()
      else None
    )
    normalized_policy_catalog_id = (
      policy_catalog_id.strip()
      if isinstance(policy_catalog_id, str) and policy_catalog_id.strip()
      else None
    )
    filtered_records = tuple(
      record
      for record in records
      if (
        (normalized_queue_state is None or record.queue_state == normalized_queue_state)
        and (
          normalized_policy_catalog_id is None
          or (record.policy_catalog_id or "") == normalized_policy_catalog_id
        )
      )
    )
    policy_catalogs = self._list_provider_provenance_scheduler_search_moderation_policy_catalog_records()
    return {
      "generated_at": self._clock(),
      "query": {
        "queue_state": normalized_queue_state,
        "policy_catalog_id": normalized_policy_catalog_id,
      },
      "available_filters": {
        "queue_states": ("pending_approval", "ready_to_apply", "completed"),
        "policy_catalogs": tuple(
          {
            "catalog_id": catalog.catalog_id,
            "name": catalog.name,
          }
          for catalog in policy_catalogs
        ),
      },
      "summary": {
        "total": len(filtered_records),
        "pending_approval_count": sum(
          1 for record in filtered_records if record.queue_state == "pending_approval"
        ),
        "ready_to_apply_count": sum(
          1 for record in filtered_records if record.queue_state == "ready_to_apply"
        ),
        "completed_count": sum(
          1 for record in filtered_records if record.queue_state == "completed"
        ),
      },
      "items": tuple(
        self._serialize_provider_provenance_scheduler_search_moderation_plan_record(record)
        for record in filtered_records
      ),
    }

  def approve_provider_provenance_scheduler_search_moderation_plan(
    self,
    *,
    plan_id: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    current = self._get_provider_provenance_scheduler_search_moderation_plan_record(plan_id)
    if current.status == "applied":
      raise RuntimeError("Applied scheduler search moderation plans cannot be approved again.")
    normalized_note = note.strip() if isinstance(note, str) and note.strip() else None
    if current.require_note and normalized_note is None:
      raise ValueError("This scheduler search moderation plan requires an approval note.")
    saved = self._save_provider_provenance_scheduler_search_moderation_plan_record(
      replace(
        current,
        status="approved",
        queue_state="ready_to_apply",
        updated_at=self._clock(),
        approved_at=self._clock(),
        approved_by=actor.strip() if isinstance(actor, str) and actor.strip() else "operator",
        approved_by_tab_id=(
          source_tab_id.strip()
          if isinstance(source_tab_id, str) and source_tab_id.strip()
          else None
        ),
        approved_by_tab_label=(
          source_tab_label.strip()
          if isinstance(source_tab_label, str) and source_tab_label.strip()
          else None
        ),
        approval_note=normalized_note,
      )
    )
    return self._serialize_provider_provenance_scheduler_search_moderation_plan_record(saved)

  def apply_provider_provenance_scheduler_search_moderation_plan(
    self,
    *,
    plan_id: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    current = self._get_provider_provenance_scheduler_search_moderation_plan_record(plan_id)
    if current.status != "approved":
      raise RuntimeError("Approve the scheduler search moderation plan before applying it.")
    moderation_note = current.approval_note
    if moderation_note is None and isinstance(note, str) and note.strip():
      moderation_note = note.strip()
    batch_result = self.moderate_provider_provenance_scheduler_search_feedback_batch(
      feedback_ids=tuple(current.feedback_ids),
      moderation_status=current.proposed_moderation_status,
      actor=actor,
      note=moderation_note,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
    saved = self._save_provider_provenance_scheduler_search_moderation_plan_record(
      replace(
        current,
        status="applied",
        queue_state="completed",
        updated_at=self._clock(),
        applied_at=self._clock(),
        applied_by=actor.strip() if isinstance(actor, str) and actor.strip() else "operator",
        applied_by_tab_id=(
          source_tab_id.strip()
          if isinstance(source_tab_id, str) and source_tab_id.strip()
          else None
        ),
        applied_by_tab_label=(
          source_tab_label.strip()
          if isinstance(source_tab_label, str) and source_tab_label.strip()
          else None
        ),
        apply_note=note.strip() if isinstance(note, str) and note.strip() else None,
        applied_result=batch_result,
      )
    )
    return self._serialize_provider_provenance_scheduler_search_moderation_plan_record(saved)

  def create_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    self,
    *,
    name: str,
    description: str = "",
    action_scope: str = "any",
    require_approval_note: bool = False,
    guidance: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    default_moderation_status: str = "approved",
    governance_view: str = "pending_queue",
    window_days: int = 30,
    stale_pending_hours: int = 24,
    minimum_score: int = 0,
    require_note: bool = False,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return create_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support(
      self,
      name=name,
      description=description,
      action_scope=action_scope,
      require_approval_note=require_approval_note,
      guidance=guidance,
      name_prefix=name_prefix,
      name_suffix=name_suffix,
      description_append=description_append,
      default_moderation_status=default_moderation_status,
      governance_view=governance_view,
      window_days=window_days,
      stale_pending_hours=stale_pending_hours,
      minimum_score=minimum_score,
      require_note=require_note,
      created_by_tab_id=created_by_tab_id,
      created_by_tab_label=created_by_tab_label,
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
    self,
    *,
    action_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> dict[str, Any]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policies_support(
      self,
      action_scope=action_scope,
      search=search,
      limit=limit,
    )

  def update_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    self,
    governance_policy_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    action_scope: str | None = None,
    require_approval_note: bool | None = None,
    guidance: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    default_moderation_status: str | None = None,
    governance_view: str | None = None,
    window_days: int | None = None,
    stale_pending_hours: int | None = None,
    minimum_score: int | None = None,
    require_note: bool | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_search_moderation_catalog_governance_policy_updated",
  ) -> dict[str, Any]:
    return update_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support(
      self,
      governance_policy_id,
      name=name,
      description=description,
      action_scope=action_scope,
      require_approval_note=require_approval_note,
      guidance=guidance,
      name_prefix=name_prefix,
      name_suffix=name_suffix,
      description_append=description_append,
      default_moderation_status=default_moderation_status,
      governance_view=governance_view,
      window_days=window_days,
      stale_pending_hours=stale_pending_hours,
      minimum_score=minimum_score,
      require_note=require_note,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
      reason=reason,
    )

  def delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    self,
    governance_policy_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_search_moderation_catalog_governance_policy_deleted",
  ) -> dict[str, Any]:
    return delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support(
      self,
      governance_policy_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
      reason=reason,
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions(
    self,
    governance_policy_id: str,
  ) -> dict[str, Any]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_support(
      self,
      governance_policy_id,
    )

  def restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    self,
    governance_policy_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_search_moderation_catalog_governance_policy_revision_restored",
  ) -> dict[str, Any]:
    return restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support(
      self,
      governance_policy_id,
      revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
      reason=reason,
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits(
    self,
    *,
    governance_policy_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> dict[str, Any]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_support(
      self,
      governance_policy_id=governance_policy_id,
      action=action,
      actor_tab_id=actor_tab_id,
      search=search,
      limit=limit,
    )

  def bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
    self,
    *,
    governance_policy_ids: Iterable[str],
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    default_moderation_status: str | None = None,
    governance_view: str | None = None,
    window_days: int | None = None,
    stale_pending_hours: int | None = None,
    minimum_score: int | None = None,
    require_note: bool | None = None,
    action_scope: str | None = None,
    require_approval_note: bool | None = None,
    guidance: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    return bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies_support(
      self,
      governance_policy_ids=governance_policy_ids,
      action=action,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
      reason=reason,
      name_prefix=name_prefix,
      name_suffix=name_suffix,
      description_append=description_append,
      default_moderation_status=default_moderation_status,
      governance_view=governance_view,
      window_days=window_days,
      stale_pending_hours=stale_pending_hours,
      minimum_score=minimum_score,
      require_note=require_note,
      action_scope=action_scope,
      require_approval_note=require_approval_note,
      guidance=guidance,
    )

  def stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    self,
    *,
    catalog_ids: Iterable[str],
    action: str,
    governance_policy_id: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    default_moderation_status: str | None = None,
    governance_view: str | None = None,
    window_days: int | None = None,
    stale_pending_hours: int | None = None,
    minimum_score: int | None = None,
    require_note: bool | None = None,
    actor: str = "operator",
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support(
      self,
      catalog_ids=catalog_ids,
      action=action,
      governance_policy_id=governance_policy_id,
      name_prefix=name_prefix,
      name_suffix=name_suffix,
      description_append=description_append,
      default_moderation_status=default_moderation_status,
      governance_view=governance_view,
      window_days=window_days,
      stale_pending_hours=stale_pending_hours,
      minimum_score=minimum_score,
      require_note=require_note,
      actor=actor,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_plans(
    self,
    *,
    queue_state: str | None = None,
    governance_policy_id: str | None = None,
  ) -> dict[str, Any]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_plans_support(
      self,
      queue_state=queue_state,
      governance_policy_id=governance_policy_id,
    )

  def approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    self,
    *,
    plan_id: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support(
      self,
      plan_id=plan_id,
      actor=actor,
      note=note,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )

  def apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    self,
    *,
    plan_id: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support(
      self,
      plan_id=plan_id,
      actor=actor,
      note=note,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )

  def create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy(
    self,
    *,
    name: str,
    description: str = "",
    action_scope: str = "any",
    require_approval_note: bool = False,
    guidance: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    policy_action_scope: str | None = None,
    policy_require_approval_note: bool | None = None,
    policy_guidance: str | None = None,
    default_moderation_status: str | None = None,
    governance_view: str | None = None,
    window_days: int | None = None,
    stale_pending_hours: int | None = None,
    minimum_score: int | None = None,
    require_note: bool | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_support(
      self,
      name=name,
      description=description,
      action_scope=action_scope,
      require_approval_note=require_approval_note,
      guidance=guidance,
      name_prefix=name_prefix,
      name_suffix=name_suffix,
      description_append=description_append,
      policy_action_scope=policy_action_scope,
      policy_require_approval_note=policy_require_approval_note,
      policy_guidance=policy_guidance,
      default_moderation_status=default_moderation_status,
      governance_view=governance_view,
      window_days=window_days,
      stale_pending_hours=stale_pending_hours,
      minimum_score=minimum_score,
      require_note=require_note,
      created_by_tab_id=created_by_tab_id,
      created_by_tab_label=created_by_tab_label,
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies(
    self,
    *,
    action_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> dict[str, Any]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_support(
      self,
      action_scope=action_scope,
      search=search,
      limit=limit,
    )

  def stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    self,
    *,
    governance_policy_ids: Iterable[str],
    action: str,
    meta_policy_id: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    action_scope: str | None = None,
    require_approval_note: bool | None = None,
    guidance: str | None = None,
    default_moderation_status: str | None = None,
    governance_view: str | None = None,
    window_days: int | None = None,
    stale_pending_hours: int | None = None,
    minimum_score: int | None = None,
    require_note: bool | None = None,
    actor: str = "operator",
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support(
      self,
      governance_policy_ids=governance_policy_ids,
      action=action,
      meta_policy_id=meta_policy_id,
      name_prefix=name_prefix,
      name_suffix=name_suffix,
      description_append=description_append,
      action_scope=action_scope,
      require_approval_note=require_approval_note,
      guidance=guidance,
      default_moderation_status=default_moderation_status,
      governance_view=governance_view,
      window_days=window_days,
      stale_pending_hours=stale_pending_hours,
      minimum_score=minimum_score,
      require_note=require_note,
      actor=actor,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans(
    self,
    *,
    queue_state: str | None = None,
    meta_policy_id: str | None = None,
  ) -> dict[str, Any]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_support(
      self,
      queue_state=queue_state,
      meta_policy_id=meta_policy_id,
    )

  def approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    self,
    *,
    plan_id: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support(
      self,
      plan_id=plan_id,
      actor=actor,
      note=note,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )

  def apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    self,
    *,
    plan_id: str,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    return apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support(
      self,
      plan_id=plan_id,
      actor=actor,
      note=note,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
