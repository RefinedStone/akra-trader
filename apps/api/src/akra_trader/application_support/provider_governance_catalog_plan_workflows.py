from __future__ import annotations

from dataclasses import replace
from typing import Any
from typing import Iterable
from uuid import uuid4

from akra_trader.domain.models import (
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem,
)
from akra_trader.domain.models import (
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
)


def stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
  app: Any,
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
  normalized_ids = app._normalize_provider_provenance_scheduler_narrative_bulk_ids(catalog_ids)
  if not normalized_ids:
    raise ValueError("Select one or more moderation policy catalogs to stage.")
  normalized_action = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
      action
    )
  )
  if normalized_action is None:
    raise ValueError("Unsupported moderation catalog governance action.")
  resolved_policy = None
  if isinstance(governance_policy_id, str) and governance_policy_id.strip():
    resolved_policy = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      governance_policy_id
    )
    if resolved_policy.status != "active":
      raise ValueError("Selected moderation catalog governance policy must be active.")
    if (
      resolved_policy.action_scope != "any"
      and resolved_policy.action_scope != normalized_action
    ):
      raise ValueError("Selected moderation catalog governance policy does not support this action.")
  resolved_name_prefix = app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
    name_prefix if name_prefix is not None else (resolved_policy.name_prefix if resolved_policy else None),
    preserve_outer_spacing=True,
  )
  resolved_name_suffix = app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
    name_suffix if name_suffix is not None else (resolved_policy.name_suffix if resolved_policy else None),
    preserve_outer_spacing=True,
  )
  resolved_description_append = app._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
    description_append
    if description_append is not None
    else (resolved_policy.description_append if resolved_policy else None)
  )
  resolved_default_status = (
    app._normalize_provider_provenance_scheduler_search_feedback_moderation_status(
      default_moderation_status
      if default_moderation_status is not None
      else (resolved_policy.default_moderation_status if resolved_policy else None)
    )
    if (
      default_moderation_status is not None
      or resolved_policy is not None
    )
    else None
  )
  resolved_governance_view = (
    app._normalize_provider_provenance_scheduler_search_governance_view(
      governance_view
      if governance_view is not None
      else (resolved_policy.governance_view if resolved_policy else None)
    )
    if (
      governance_view is not None
      or resolved_policy is not None
    )
    else None
  )
  resolved_window_days = (
    max(7, min(int(window_days), 180))
    if window_days is not None
    else (resolved_policy.window_days if resolved_policy is not None else None)
  )
  resolved_stale_pending_hours = (
    max(1, min(int(stale_pending_hours), 24 * 30))
    if stale_pending_hours is not None
    else (resolved_policy.stale_pending_hours if resolved_policy is not None else None)
  )
  resolved_minimum_score = (
    max(int(minimum_score), 0)
    if minimum_score is not None
    else (resolved_policy.minimum_score if resolved_policy is not None else None)
  )
  resolved_require_note = (
    bool(require_note)
    if require_note is not None
    else (resolved_policy.require_note if resolved_policy is not None else None)
  )
  if normalized_action == "update" and all(
    value is None
    for value in (
      resolved_name_prefix,
      resolved_name_suffix,
      resolved_description_append,
      resolved_default_status,
      resolved_governance_view,
      resolved_window_days,
      resolved_stale_pending_hours,
      resolved_minimum_score,
      resolved_require_note,
    )
  ):
    raise ValueError("Provide at least one moderation policy catalog change before staging an update plan.")
  current_time = app._clock()
  preview_items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem] = []
  changed_count = 0
  for catalog_id in normalized_ids:
    current = app._get_provider_provenance_scheduler_search_moderation_policy_catalog_record(catalog_id)
    current_snapshot = app._serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(
      current
    )
    proposed_snapshot = dict(current_snapshot)
    message: str | None = None
    outcome = "changed"
    if normalized_action == "delete":
      if current.status == "deleted":
        outcome = "skipped"
        message = "Catalog is already deleted."
      else:
        proposed_snapshot["status"] = "deleted"
    elif normalized_action == "restore":
      if current.status != "deleted":
        outcome = "skipped"
        message = "Catalog is already active."
      else:
        proposed_snapshot["status"] = "active"
        proposed_snapshot["deleted_at"] = None
        proposed_snapshot["deleted_by_tab_id"] = None
        proposed_snapshot["deleted_by_tab_label"] = None
    else:
      if current.status == "deleted":
        outcome = "skipped"
        message = "Restore the catalog before editing it."
      else:
        if resolved_name_prefix is not None or resolved_name_suffix is not None:
          proposed_snapshot["name"] = (
            f"{resolved_name_prefix or ''}{current.name}{resolved_name_suffix or ''}"
          )
        if resolved_description_append is not None:
          proposed_snapshot["description"] = f"{current.description}{resolved_description_append}"
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
      message = "No catalog changes were staged."
    if outcome == "changed":
      changed_count += 1
    preview_items.append(
      ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem(
        catalog_id=current.catalog_id,
        catalog_name=current.name,
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
    raise ValueError("No selected moderation policy catalogs produced a staged change.")
  plan_record = ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord(
    plan_id=uuid4().hex[:12],
    created_at=current_time,
    updated_at=current_time,
    action=normalized_action,
    status="previewed",
    queue_state="pending_approval",
    governance_policy_id=resolved_policy.governance_policy_id if resolved_policy is not None else None,
    governance_policy_name=resolved_policy.name if resolved_policy is not None else None,
    require_approval_note=(
      resolved_policy.require_approval_note if resolved_policy is not None else False
    ),
    guidance=resolved_policy.guidance if resolved_policy is not None else None,
    requested_catalog_ids=normalized_ids,
    preview_items=tuple(preview_items),
    name_prefix=resolved_name_prefix,
    name_suffix=resolved_name_suffix,
    description_append=resolved_description_append,
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
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    plan_record
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    saved
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_plans(
  app: Any,
  *,
  queue_state: str | None = None,
  governance_policy_id: str | None = None,
) -> dict[str, Any]:
  normalized_queue_state = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_queue_state(
      queue_state
    )
    if isinstance(queue_state, str) and queue_state.strip()
    else None
  )
  normalized_policy_id = (
    governance_policy_id.strip()
    if isinstance(governance_policy_id, str) and governance_policy_id.strip()
    else None
  )
  records = tuple(
    record
    for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records()
    if (
      (normalized_queue_state is None or record.queue_state == normalized_queue_state)
      and (
        normalized_policy_id is None
        or (record.governance_policy_id or "") == normalized_policy_id
      )
    )
  )
  policies = app._list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records()
  return {
    "generated_at": app._clock(),
    "query": {
      "queue_state": normalized_queue_state,
      "governance_policy_id": normalized_policy_id,
    },
    "available_filters": {
      "queue_states": ("pending_approval", "ready_to_apply", "completed"),
      "governance_policies": tuple(
        {
          "governance_policy_id": policy.governance_policy_id,
          "name": policy.name,
          "action_scope": policy.action_scope,
        }
        for policy in policies
      ),
    },
    "summary": {
      "total": len(records),
      "pending_approval_count": sum(
        1 for record in records if record.queue_state == "pending_approval"
      ),
      "ready_to_apply_count": sum(
        1 for record in records if record.queue_state == "ready_to_apply"
      ),
      "completed_count": sum(
        1 for record in records if record.queue_state == "completed"
      ),
    },
    "items": tuple(
      app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
        record
      )
      for record in records
    ),
  }


def approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
  app: Any,
  *,
  plan_id: str,
  actor: str = "operator",
  note: str | None = None,
  source_tab_id: str | None = None,
  source_tab_label: str | None = None,
) -> dict[str, Any]:
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    plan_id
  )
  if current.status == "applied":
    raise RuntimeError("Applied moderation catalog governance plans cannot be approved again.")
  normalized_note = note.strip() if isinstance(note, str) and note.strip() else None
  if current.require_approval_note and normalized_note is None:
    raise ValueError("This moderation catalog governance plan requires an approval note.")
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
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
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    saved
  )


def apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
  app: Any,
  *,
  plan_id: str,
  actor: str = "operator",
  note: str | None = None,
  source_tab_id: str | None = None,
  source_tab_label: str | None = None,
) -> dict[str, Any]:
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    plan_id
  )
  if current.status != "approved":
    raise RuntimeError("Approve the moderation catalog governance plan before applying it.")
  results: list[dict[str, Any]] = []
  applied_count = 0
  skipped_count = 0
  failed_count = 0
  for preview in current.preview_items:
    if preview.outcome != "changed":
      skipped_count += 1
      results.append(
        {
          "catalog_id": preview.catalog_id,
          "catalog_name": preview.catalog_name,
          "outcome": "skipped",
          "message": preview.message or "Preview item did not produce a change.",
        }
      )
      continue
    try:
      if current.action == "delete":
        updated = app.delete_provider_provenance_scheduler_search_moderation_policy_catalog(
          preview.catalog_id,
          actor_tab_id=source_tab_id,
          actor_tab_label=source_tab_label,
          reason="scheduler_search_moderation_catalog_governance_plan_applied",
        )
      elif current.action == "restore":
        revision_id = preview.rollback_revision_id
        if not revision_id:
          raise RuntimeError("Restore preview is missing the rollback revision.")
        updated = app.restore_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
          preview.catalog_id,
          revision_id,
          actor_tab_id=source_tab_id,
          actor_tab_label=source_tab_label,
          reason="scheduler_search_moderation_catalog_governance_plan_applied",
        )
      else:
        updated = app.update_provider_provenance_scheduler_search_moderation_policy_catalog(
          preview.catalog_id,
          name=(
            f"{current.name_prefix or ''}{preview.current_snapshot.get('name', preview.catalog_name)}{current.name_suffix or ''}"
            if current.name_prefix is not None or current.name_suffix is not None
            else None
          ),
          description=(
            f"{preview.current_snapshot.get('description', '')}{current.description_append}"
            if current.description_append is not None
            else None
          ),
          default_moderation_status=current.default_moderation_status,
          governance_view=current.governance_view,
          window_days=current.window_days,
          stale_pending_hours=current.stale_pending_hours,
          minimum_score=current.minimum_score,
          require_note=current.require_note,
          actor_tab_id=source_tab_id,
          actor_tab_label=source_tab_label,
          reason="scheduler_search_moderation_catalog_governance_plan_applied",
        )
      applied_count += 1
      results.append(
        {
          "catalog_id": preview.catalog_id,
          "catalog_name": str(updated.get("name", preview.catalog_name)),
          "outcome": "applied",
          "status": updated.get("status"),
          "current_revision_id": updated.get("current_revision_id"),
        }
      )
    except (LookupError, RuntimeError, ValueError) as exc:
      failed_count += 1
      results.append(
        {
          "catalog_id": preview.catalog_id,
          "catalog_name": preview.catalog_name,
          "outcome": "failed",
          "message": str(exc),
        }
      )
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
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
        "requested_count": len(current.requested_catalog_ids),
        "applied_count": applied_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "results": tuple(results),
      },
    )
  )
  return app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    saved
  )
