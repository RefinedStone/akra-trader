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


class ProviderProvenanceSearchModerationFeedbackRecordsMixin:
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
