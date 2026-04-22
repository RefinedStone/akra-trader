from __future__ import annotations

from dataclasses import replace
from typing import Any
from typing import Iterable
from uuid import uuid4

from akra_trader.domain.models import (
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem,
)
from akra_trader.domain.models import (
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
)
from akra_trader.domain.models import (
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
)


def create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy(
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
  normalized_name = app._normalize_provider_provenance_workspace_name(
    name,
    field_name="scheduler search moderation governance meta policy name",
  )
  normalized_action_scope = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
      action_scope
    )
  )
  normalized_policy_action_scope = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
      policy_action_scope
    )
    if isinstance(policy_action_scope, str) and policy_action_scope.strip()
    else None
  )
  normalized_default_status = (
    app._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      default_moderation_status
    )
    if default_moderation_status is not None
    else None
  )
  normalized_governance_view = (
    app._normalize_provider_provenance_scheduler_search_governance_view(governance_view)
    if governance_view is not None
    else None
  )
  if normalized_action_scope is None:
    raise ValueError("Scheduler search moderation governance meta policies require a valid action scope.")
  if default_moderation_status is not None and normalized_default_status is None:
    raise ValueError("Invalid default moderation status for scheduler search moderation governance meta policy.")
  if governance_view is not None and normalized_governance_view is None:
    raise ValueError("Invalid governance view for scheduler search moderation governance meta policy.")
  current_time = app._clock()
  record = ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord(
    meta_policy_id=uuid4().hex[:12],
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
    policy_action_scope=normalized_policy_action_scope,
    policy_require_approval_note=policy_require_approval_note,
    policy_guidance=(
      policy_guidance.strip()
      if isinstance(policy_guidance, str) and policy_guidance.strip()
      else None
    ),
    default_moderation_status=normalized_default_status,
    governance_view=normalized_governance_view,
    window_days=(
      max(7, min(int(window_days), 180))
      if window_days is not None
      else None
    ),
    stale_pending_hours=(
      max(1, min(int(stale_pending_hours), 24 * 30))
      if stale_pending_hours is not None
      else None
    ),
    minimum_score=(max(int(minimum_score), 0) if minimum_score is not None else None),
    require_note=require_note if require_note is not None else None,
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
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    record
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    saved
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies(
  app: Any,
  *,
  action_scope: str | None = None,
  search: str | None = None,
  limit: int = 50,
) -> dict[str, Any]:
  normalized_action_scope = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
      action_scope
    )
    if isinstance(action_scope, str) and action_scope.strip()
    else None
  )
  normalized_search = search.strip().lower() if isinstance(search, str) and search.strip() else None
  normalized_limit = max(1, min(int(limit), 200))
  items: list[dict[str, Any]] = []
  for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records():
    if normalized_action_scope is not None and record.action_scope != normalized_action_scope:
      continue
    if normalized_search is not None:
      haystack = " ".join(
        value
        for value in (
          record.name,
          record.description,
          record.guidance or "",
          record.policy_guidance or "",
        )
        if value
      ).lower()
      if normalized_search not in haystack:
        continue
    items.append(
      app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
        record
      )
    )
    if len(items) >= normalized_limit:
      break
  return {
    "generated_at": app._clock(),
    "query": {
      "action_scope": normalized_action_scope,
      "search": normalized_search,
      "limit": normalized_limit,
    },
    "available_filters": {
      "action_scopes": ("any", "update", "delete", "restore"),
    },
    "total": len(items),
    "items": tuple(items),
  }


def stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
  app: Any,
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
  normalized_ids = app._normalize_provider_provenance_scheduler_narrative_bulk_ids(
    governance_policy_ids
  )
  if not normalized_ids:
    raise ValueError("Select one or more moderation governance policies to stage.")
  normalized_action = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
      action
    )
  )
  if normalized_action is None:
    raise ValueError("Unsupported moderation governance policy action.")
  resolved_meta_policy = None
  if isinstance(meta_policy_id, str) and meta_policy_id.strip():
    resolved_meta_policy = (
      app._get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
        meta_policy_id
      )
    )
    if resolved_meta_policy.status != "active":
      raise ValueError("Selected moderation governance meta policy must be active.")
    if (
      resolved_meta_policy.action_scope != "any"
      and resolved_meta_policy.action_scope != normalized_action
    ):
      raise ValueError("Selected moderation governance meta policy does not support this action.")
  resolved_name_prefix = app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
    name_prefix if name_prefix is not None else (resolved_meta_policy.name_prefix if resolved_meta_policy else None),
    preserve_outer_spacing=True,
  )
  resolved_name_suffix = app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
    name_suffix if name_suffix is not None else (resolved_meta_policy.name_suffix if resolved_meta_policy else None),
    preserve_outer_spacing=True,
  )
  resolved_description_append = app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
    description_append
    if description_append is not None
    else (resolved_meta_policy.description_append if resolved_meta_policy else None)
  )
  resolved_policy_action_scope = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
      action_scope
      if action_scope is not None
      else (resolved_meta_policy.policy_action_scope if resolved_meta_policy else None)
    )
    if (
      action_scope is not None
      or (resolved_meta_policy is not None and resolved_meta_policy.policy_action_scope is not None)
    )
    else None
  )
  resolved_policy_require_approval_note = (
    require_approval_note
    if require_approval_note is not None
    else (resolved_meta_policy.policy_require_approval_note if resolved_meta_policy else None)
  )
  resolved_policy_guidance = (
    guidance.strip()
    if isinstance(guidance, str) and guidance.strip()
    else (
      resolved_meta_policy.policy_guidance
      if guidance is None and resolved_meta_policy is not None
      else None
    )
  )
  resolved_default_status = (
    app._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      default_moderation_status
      if default_moderation_status is not None
      else (resolved_meta_policy.default_moderation_status if resolved_meta_policy else None)
    )
    if (
      default_moderation_status is not None
      or (resolved_meta_policy is not None and resolved_meta_policy.default_moderation_status is not None)
    )
    else None
  )
  resolved_governance_view = (
    app._normalize_provider_provenance_scheduler_search_governance_view(
      governance_view
      if governance_view is not None
      else (resolved_meta_policy.governance_view if resolved_meta_policy else None)
    )
    if (
      governance_view is not None
      or (resolved_meta_policy is not None and resolved_meta_policy.governance_view is not None)
    )
    else None
  )
  resolved_window_days = (
    max(7, min(int(window_days), 180))
    if window_days is not None
    else (resolved_meta_policy.window_days if resolved_meta_policy is not None else None)
  )
  resolved_stale_pending_hours = (
    max(1, min(int(stale_pending_hours), 24 * 30))
    if stale_pending_hours is not None
    else (
      resolved_meta_policy.stale_pending_hours if resolved_meta_policy is not None else None
    )
  )
  resolved_minimum_score = (
    max(int(minimum_score), 0)
    if minimum_score is not None
    else (resolved_meta_policy.minimum_score if resolved_meta_policy is not None else None)
  )
  resolved_require_note = (
    require_note
    if require_note is not None
    else (resolved_meta_policy.require_note if resolved_meta_policy is not None else None)
  )
  if normalized_action == "update" and all(
    value is None
    for value in (
      resolved_name_prefix,
      resolved_name_suffix,
      resolved_description_append,
      resolved_policy_action_scope,
      resolved_policy_require_approval_note,
      resolved_policy_guidance,
      resolved_default_status,
      resolved_governance_view,
      resolved_window_days,
      resolved_stale_pending_hours,
      resolved_minimum_score,
      resolved_require_note,
    )
  ):
    raise ValueError("Provide at least one moderation governance policy change before staging an update plan.")
  current_time = app._clock()
  preview_items: list[
    ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem
  ] = []
  changed_count = 0
  for governance_policy_id in normalized_ids:
    current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      governance_policy_id
    )
    current_snapshot = app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      current
    )
    proposed_snapshot = dict(current_snapshot)
    message: str | None = None
    outcome = "changed"
    if normalized_action == "delete":
      if current.status == "deleted":
        outcome = "skipped"
        message = "Governance policy is already deleted."
      else:
        proposed_snapshot["status"] = "deleted"
    elif normalized_action == "restore":
      if current.status != "deleted":
        outcome = "skipped"
        message = "Governance policy is already active."
      else:
        proposed_snapshot["status"] = "active"
        proposed_snapshot["deleted_at"] = None
        proposed_snapshot["deleted_by_tab_id"] = None
        proposed_snapshot["deleted_by_tab_label"] = None
    else:
      if current.status == "deleted":
        outcome = "skipped"
        message = "Restore the governance policy before editing it."
      else:
        if resolved_name_prefix is not None or resolved_name_suffix is not None:
          proposed_snapshot["name"] = (
            f"{resolved_name_prefix or ''}{current.name}{resolved_name_suffix or ''}"
          )
        if resolved_description_append is not None:
          proposed_snapshot["description"] = (
            f"{current.description}{resolved_description_append}"
          )
        if resolved_policy_action_scope is not None:
          proposed_snapshot["action_scope"] = resolved_policy_action_scope
        if resolved_policy_require_approval_note is not None:
          proposed_snapshot["require_approval_note"] = resolved_policy_require_approval_note
        if resolved_policy_guidance is not None:
          proposed_snapshot["guidance"] = resolved_policy_guidance
        if resolved_default_status is not None:
          proposed_snapshot["default_moderation_status"] = resolved_default_status
        if resolved_governance_view is not None:
          proposed_snapshot["governance_view"] = resolved_governance_view
        if resolved_window_days is not None:
          proposed_snapshot["window_days"] = resolved_window_days
        if resolved_stale_pending_hours is not None:
          proposed_snapshot["stale_pending_hours"] = resolved_stale_pending_hours
        if resolved_minimum_score is not None:
          proposed_snapshot["minimum_score"] = resolved_minimum_score
        if resolved_require_note is not None:
          proposed_snapshot["require_note"] = resolved_require_note
    field_diffs = {
      field_name: {
        "before": current_snapshot.get(field_name),
        "after": proposed_snapshot.get(field_name),
      }
      for field_name in proposed_snapshot
      if current_snapshot.get(field_name) != proposed_snapshot.get(field_name)
    }
    changed_fields = tuple(field_diffs.keys())
    if outcome == "changed" and not changed_fields:
      outcome = "skipped"
      message = "No governance policy changes were staged."
    if outcome == "changed":
      changed_count += 1
    preview_items.append(
      ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem(
        governance_policy_id=current.governance_policy_id,
        governance_policy_name=current.name,
        action=normalized_action,
        current_status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome=outcome,
        message=message,
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    )
  if changed_count == 0:
    raise ValueError("No selected moderation governance policies produced a staged change.")
  plan_record = ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord(
    plan_id=uuid4().hex[:12],
    created_at=current_time,
    updated_at=current_time,
    action=normalized_action,
    status="previewed",
    queue_state="pending_approval",
    meta_policy_id=resolved_meta_policy.meta_policy_id if resolved_meta_policy is not None else None,
    meta_policy_name=resolved_meta_policy.name if resolved_meta_policy is not None else None,
    require_approval_note=(
      resolved_meta_policy.require_approval_note if resolved_meta_policy is not None else False
    ),
    guidance=resolved_meta_policy.guidance if resolved_meta_policy is not None else None,
    requested_governance_policy_ids=normalized_ids,
    preview_items=tuple(preview_items),
    name_prefix=resolved_name_prefix,
    name_suffix=resolved_name_suffix,
    description_append=resolved_description_append,
    policy_action_scope=resolved_policy_action_scope,
    policy_require_approval_note=resolved_policy_require_approval_note,
    policy_guidance=resolved_policy_guidance,
    default_moderation_status=resolved_default_status,
    governance_view=resolved_governance_view,
    window_days=resolved_window_days,
    stale_pending_hours=resolved_stale_pending_hours,
    minimum_score=resolved_minimum_score,
    require_note=resolved_require_note,
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
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    plan_record
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    saved
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans(
  app: Any,
  *,
  queue_state: str | None = None,
  meta_policy_id: str | None = None,
) -> dict[str, Any]:
  normalized_queue_state = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_queue_state(
      queue_state
    )
    if isinstance(queue_state, str) and queue_state.strip()
    else None
  )
  normalized_meta_policy_id = (
    meta_policy_id.strip()
    if isinstance(meta_policy_id, str) and meta_policy_id.strip()
    else None
  )
  records = tuple(
    record
    for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records()
    if (
      (normalized_queue_state is None or record.queue_state == normalized_queue_state)
      and (
        normalized_meta_policy_id is None
        or (record.meta_policy_id or "") == normalized_meta_policy_id
      )
    )
  )
  meta_policies = app._list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records()
  return {
    "generated_at": app._clock(),
    "query": {
      "queue_state": normalized_queue_state,
      "meta_policy_id": normalized_meta_policy_id,
    },
    "available_filters": {
      "queue_states": ("pending_approval", "ready_to_apply", "completed"),
      "meta_policies": tuple(
        {
          "meta_policy_id": policy.meta_policy_id,
          "name": policy.name,
          "action_scope": policy.action_scope,
        }
        for policy in meta_policies
      ),
    },
    "summary": {
      "total": len(records),
      "pending_approval_count": sum(1 for record in records if record.queue_state == "pending_approval"),
      "ready_to_apply_count": sum(1 for record in records if record.queue_state == "ready_to_apply"),
      "completed_count": sum(1 for record in records if record.queue_state == "completed"),
    },
    "items": tuple(
      app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
        record
      )
      for record in records
    ),
  }


def approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
  app: Any,
  *,
  plan_id: str,
  actor: str = "operator",
  note: str | None = None,
  source_tab_id: str | None = None,
  source_tab_label: str | None = None,
) -> dict[str, Any]:
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    plan_id
  )
  if current.status == "applied":
    raise RuntimeError("Applied moderation governance meta plans cannot be approved again.")
  normalized_note = note.strip() if isinstance(note, str) and note.strip() else None
  if current.require_approval_note and normalized_note is None:
    raise ValueError("This moderation governance meta plan requires an approval note.")
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    replace(
      current,
      status="approved",
      queue_state="ready_to_apply",
      updated_at=app._clock(),
      approved_at=app._clock(),
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
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    saved
  )


def apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
  app: Any,
  *,
  plan_id: str,
  actor: str = "operator",
  note: str | None = None,
  source_tab_id: str | None = None,
  source_tab_label: str | None = None,
) -> dict[str, Any]:
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    plan_id
  )
  if current.status != "approved":
    raise RuntimeError("Approve the moderation governance meta plan before applying it.")
  results: list[dict[str, Any]] = []
  applied_count = 0
  skipped_count = 0
  failed_count = 0
  for preview in current.preview_items:
    if preview.outcome != "changed":
      skipped_count += 1
      results.append(
        {
          "governance_policy_id": preview.governance_policy_id,
          "governance_policy_name": preview.governance_policy_name,
          "outcome": "skipped",
          "message": preview.message or "Preview item did not produce a change.",
        }
      )
      continue
    try:
      if current.action == "delete":
        updated = app.delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
          preview.governance_policy_id,
          actor_tab_id=source_tab_id,
          actor_tab_label=source_tab_label,
          reason="scheduler_search_moderation_catalog_governance_meta_plan_applied",
        )
      elif current.action == "restore":
        revision_id = preview.rollback_revision_id
        if not revision_id:
          raise RuntimeError("Restore preview is missing the rollback revision.")
        updated = app.restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
          preview.governance_policy_id,
          revision_id,
          actor_tab_id=source_tab_id,
          actor_tab_label=source_tab_label,
          reason="scheduler_search_moderation_catalog_governance_meta_plan_applied",
        )
      else:
        updated = app.update_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
          preview.governance_policy_id,
          name=(
            f"{current.name_prefix or ''}{preview.current_snapshot.get('name', preview.governance_policy_name)}{current.name_suffix or ''}"
            if current.name_prefix is not None or current.name_suffix is not None
            else None
          ),
          description=(
            f"{preview.current_snapshot.get('description', '')}{current.description_append}"
            if current.description_append is not None
            else None
          ),
          action_scope=current.policy_action_scope,
          require_approval_note=current.policy_require_approval_note,
          guidance=current.policy_guidance,
          default_moderation_status=current.default_moderation_status,
          governance_view=current.governance_view,
          window_days=current.window_days,
          stale_pending_hours=current.stale_pending_hours,
          minimum_score=current.minimum_score,
          require_note=current.require_note,
          actor_tab_id=source_tab_id,
          actor_tab_label=source_tab_label,
          reason="scheduler_search_moderation_catalog_governance_meta_plan_applied",
        )
      applied_count += 1
      results.append(
        {
          "governance_policy_id": preview.governance_policy_id,
          "governance_policy_name": str(updated.get("name", preview.governance_policy_name)),
          "outcome": "applied",
          "status": updated.get("status"),
          "current_revision_id": updated.get("current_revision_id"),
        }
      )
    except (LookupError, RuntimeError, ValueError) as exc:
      failed_count += 1
      results.append(
        {
          "governance_policy_id": preview.governance_policy_id,
          "governance_policy_name": preview.governance_policy_name,
          "outcome": "failed",
          "message": str(exc),
        }
      )
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    replace(
      current,
      status="applied",
      queue_state="completed",
      updated_at=app._clock(),
      applied_at=app._clock(),
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
      applied_result={
        "requested_count": len(current.requested_governance_policy_ids),
        "applied_count": applied_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "results": tuple(results),
      },
    )
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    saved
  )
