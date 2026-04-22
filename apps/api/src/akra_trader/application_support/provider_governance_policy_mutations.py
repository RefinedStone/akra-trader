from __future__ import annotations

from dataclasses import replace
from typing import Any
from uuid import uuid4

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord


def create_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
  app: Any,
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
  normalized_name = app._normalize_provider_provenance_workspace_name(
    name,
    field_name="scheduler search moderation catalog governance policy name",
  )
  normalized_action_scope = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action_scope(
      action_scope
    )
  )
  normalized_default_status = (
    app._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      default_moderation_status
    )
  )
  normalized_governance_view = (
    app._normalize_provider_provenance_scheduler_search_governance_view(governance_view)
  )
  if (
    normalized_action_scope is None
    or normalized_default_status is None
    or normalized_governance_view is None
  ):
    raise ValueError(
      "Scheduler search moderation catalog governance policies require a valid name, action scope, moderation status, and governance view."
    )
  current_time = app._clock()
  record = ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord(
    governance_policy_id=uuid4().hex[:12],
    created_at=current_time,
    updated_at=current_time,
    name=normalized_name,
    description=description.strip() if isinstance(description, str) else "",
    action_scope=normalized_action_scope,
    require_approval_note=bool(require_approval_note),
    guidance=guidance.strip() if isinstance(guidance, str) and guidance.strip() else None,
    name_prefix=app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    ),
    name_suffix=app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    ),
    description_append=app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    ),
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
  saved = app._record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    record=record,
    action="created",
    reason="scheduler_search_moderation_catalog_governance_policy_created",
    recorded_at=current_time,
    actor_tab_id=created_by_tab_id,
    actor_tab_label=created_by_tab_label,
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    saved
  )


def update_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
  app: Any,
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
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    governance_policy_id
  )
  if current.status == "deleted":
    raise RuntimeError(
      "Deleted moderation governance policies must be restored from revision history before editing."
    )
  updated_name = (
    app._normalize_provider_provenance_workspace_name(
      name,
      field_name="scheduler search moderation catalog governance policy name",
    )
    if isinstance(name, str)
    else current.name
  )
  updated_description = (
    description.strip() if isinstance(description, str) else current.description
  )
  updated_action_scope = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action_scope(
      action_scope
    )
    if action_scope is not None
    else current.action_scope
  )
  updated_default_status = (
    app._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      default_moderation_status
    )
    if default_moderation_status is not None
    else current.default_moderation_status
  )
  updated_governance_view = (
    app._normalize_provider_provenance_scheduler_search_governance_view(governance_view)
    if governance_view is not None
    else current.governance_view
  )
  if (
    updated_action_scope is None
    or updated_default_status is None
    or updated_governance_view is None
  ):
    raise ValueError(
      "Governance policy update requires a valid action scope, moderation status, and governance view."
    )
  updated_record = replace(
    current,
    updated_at=app._clock(),
    name=updated_name,
    description=updated_description,
    action_scope=updated_action_scope,
    require_approval_note=(
      bool(require_approval_note)
      if require_approval_note is not None
      else current.require_approval_note
    ),
    guidance=(
      guidance.strip() if isinstance(guidance, str) and guidance.strip() else None
      if guidance is not None
      else current.guidance
    ),
    name_prefix=(
      app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        name_prefix,
        preserve_outer_spacing=True,
      )
      if name_prefix is not None
      else current.name_prefix
    ),
    name_suffix=(
      app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        name_suffix,
        preserve_outer_spacing=True,
      )
      if name_suffix is not None
      else current.name_suffix
    ),
    description_append=(
      app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        description_append
      )
      if description_append is not None
      else current.description_append
    ),
    default_moderation_status=updated_default_status,
    governance_view=updated_governance_view,
    window_days=(
      max(7, min(int(window_days), 180))
      if window_days is not None
      else current.window_days
    ),
    stale_pending_hours=(
      max(1, min(int(stale_pending_hours), 24 * 30))
      if stale_pending_hours is not None
      else current.stale_pending_hours
    ),
    minimum_score=(
      max(int(minimum_score), 0)
      if minimum_score is not None
      else current.minimum_score
    ),
    require_note=bool(require_note) if require_note is not None else current.require_note,
  )
  saved = app._record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    record=updated_record,
    action="updated",
    reason=reason,
    recorded_at=updated_record.updated_at,
    source_revision_id=current.current_revision_id,
    actor_tab_id=actor_tab_id,
    actor_tab_label=actor_tab_label,
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    saved
  )


def delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
  app: Any,
  governance_policy_id: str,
  *,
  actor_tab_id: str | None = None,
  actor_tab_label: str | None = None,
  reason: str = "scheduler_search_moderation_catalog_governance_policy_deleted",
) -> dict[str, Any]:
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    governance_policy_id
  )
  if current.status == "deleted":
    raise RuntimeError("Scheduler search moderation catalog governance policy is already deleted.")
  current_time = app._clock()
  saved = app._record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    record=replace(
      current,
      updated_at=current_time,
      status="deleted",
      deleted_at=current_time,
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
    ),
    action="deleted",
    reason=reason,
    recorded_at=current_time,
    source_revision_id=current.current_revision_id,
    actor_tab_id=actor_tab_id,
    actor_tab_label=actor_tab_label,
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    saved
  )


def restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
  app: Any,
  governance_policy_id: str,
  revision_id: str,
  *,
  actor_tab_id: str | None = None,
  actor_tab_label: str | None = None,
  reason: str = "scheduler_search_moderation_catalog_governance_policy_revision_restored",
) -> dict[str, Any]:
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    governance_policy_id
  )
  revision = app._load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    revision_id
  )
  if revision is None or revision.governance_policy_id != current.governance_policy_id:
    raise LookupError("Scheduler search moderation catalog governance policy revision not found.")
  current_time = app._clock()
  restored_record = ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord(
    governance_policy_id=current.governance_policy_id,
    created_at=current.created_at,
    updated_at=current_time,
    name=revision.name,
    description=revision.description,
    scheduler_key=revision.scheduler_key,
    status="active",
    action_scope=revision.action_scope,
    require_approval_note=revision.require_approval_note,
    guidance=revision.guidance,
    name_prefix=revision.name_prefix,
    name_suffix=revision.name_suffix,
    description_append=revision.description_append,
    default_moderation_status=revision.default_moderation_status,
    governance_view=revision.governance_view,
    window_days=revision.window_days,
    stale_pending_hours=revision.stale_pending_hours,
    minimum_score=revision.minimum_score,
    require_note=revision.require_note,
    current_revision_id=current.current_revision_id,
    revision_count=current.revision_count,
    created_by_tab_id=current.created_by_tab_id,
    created_by_tab_label=current.created_by_tab_label,
    deleted_at=None,
    deleted_by_tab_id=None,
    deleted_by_tab_label=None,
  )
  saved = app._record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    record=restored_record,
    action="restored",
    reason=reason,
    recorded_at=current_time,
    source_revision_id=revision.revision_id,
    actor_tab_id=actor_tab_id,
    actor_tab_label=actor_tab_label,
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    saved
  )
