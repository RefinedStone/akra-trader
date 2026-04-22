from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any
from uuid import uuid4

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord


def normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status(
  status: str | None,
) -> str:
  if not isinstance(status, str):
    return "active"
  normalized = status.strip().lower().replace("-", "_")
  return "deleted" if normalized == "deleted" else "active"


def build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
  app: Any,
  *,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  action: str,
  reason: str,
  recorded_at: datetime,
  source_revision_id: str | None = None,
  actor_tab_id: str | None = None,
  actor_tab_label: str | None = None,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
  revision_count = sum(
    1
    for revision in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records()
    if revision.governance_policy_id == record.governance_policy_id
  )
  return ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord(
    revision_id=f"{record.governance_policy_id}:r{revision_count + 1:04d}",
    governance_policy_id=record.governance_policy_id,
    action=action,
    reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
    name=record.name,
    description=record.description,
    scheduler_key=record.scheduler_key,
    status=normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status(
      record.status
    ),
    action_scope=record.action_scope,
    require_approval_note=bool(record.require_approval_note),
    guidance=record.guidance,
    name_prefix=record.name_prefix,
    name_suffix=record.name_suffix,
    description_append=record.description_append,
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


def build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail(
  *,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  action: str,
) -> str:
  moderation_summary = (
    f"{record.default_moderation_status} @ {record.minimum_score}+"
    if record.minimum_score > 0
    else record.default_moderation_status
  )
  governance_summary = (
    f"{record.governance_view} / {record.window_days}d / stale {record.stale_pending_hours}h"
  )
  scope_summary = f"{record.action_scope} actions"
  if action == "created":
    return (
      f"Created moderation governance policy {record.name} for {scope_summary}; "
      f"{moderation_summary}; view {governance_summary}."
    )
  if action == "updated":
    return (
      f"Updated moderation governance policy {record.name}; "
      f"{scope_summary}; {moderation_summary}; view {governance_summary}."
    )
  if action == "deleted":
    return f"Deleted moderation governance policy {record.name}."
  if action == "restored":
    return f"Restored moderation governance policy {record.name}."
  if action == "bulk_updated":
    return f"Bulk-updated moderation governance policy {record.name}."
  if action == "bulk_deleted":
    return f"Bulk-deleted moderation governance policy {record.name}."
  if action == "bulk_restored":
    return f"Bulk-restored moderation governance policy {record.name}."
  return f"Recorded moderation governance policy action {action} for {record.name}."


def record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
  app: Any,
  *,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  action: str,
  reason: str,
  recorded_at: datetime,
  source_revision_id: str | None = None,
  actor_tab_id: str | None = None,
  actor_tab_label: str | None = None,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
  revision = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
      app,
      record=record,
      action=action,
      reason=reason,
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  )
  saved = app._save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    replace(
      record,
      status=normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status(
        record.status
      ),
      current_revision_id=revision.revision_id,
      revision_count=int(record.revision_count or 0) + 1,
    )
  )
  app._save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord(
      audit_id=uuid4().hex[:12],
      governance_policy_id=saved.governance_policy_id,
      action=action,
      recorded_at=recorded_at,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      detail=build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail(
        record=saved,
        action=action,
      ),
      scheduler_key=saved.scheduler_key,
      revision_id=revision.revision_id,
      source_revision_id=source_revision_id,
      name=saved.name,
      status=saved.status,
      action_scope=saved.action_scope,
      require_approval_note=saved.require_approval_note,
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
