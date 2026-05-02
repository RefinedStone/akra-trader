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


class ProviderProvenanceSearchModerationGovernanceMixin:
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
