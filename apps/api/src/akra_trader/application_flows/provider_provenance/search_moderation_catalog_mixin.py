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


class ProviderProvenanceSearchModerationCatalogMixin:
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
