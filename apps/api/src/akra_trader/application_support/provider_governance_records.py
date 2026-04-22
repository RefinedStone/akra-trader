from __future__ import annotations

from dataclasses import replace
from typing import Any

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
) -> dict[str, Any]:
  return {
    "governance_policy_id": record.governance_policy_id,
    "created_at": record.created_at,
    "updated_at": record.updated_at,
    "scheduler_key": record.scheduler_key,
    "name": record.name,
    "description": record.description,
    "status": record.status,
    "action_scope": record.action_scope,
    "require_approval_note": record.require_approval_note,
    "guidance": record.guidance,
    "name_prefix": record.name_prefix,
    "name_suffix": record.name_suffix,
    "description_append": record.description_append,
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


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
) -> dict[str, Any]:
  return {
    "revision_id": record.revision_id,
    "governance_policy_id": record.governance_policy_id,
    "action": record.action,
    "reason": record.reason,
    "name": record.name,
    "description": record.description,
    "scheduler_key": record.scheduler_key,
    "status": record.status,
    "action_scope": record.action_scope,
    "require_approval_note": record.require_approval_note,
    "guidance": record.guidance,
    "name_prefix": record.name_prefix,
    "name_suffix": record.name_suffix,
    "description_append": record.description_append,
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


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "governance_policy_id": record.governance_policy_id,
    "action": record.action,
    "recorded_at": record.recorded_at,
    "reason": record.reason,
    "detail": record.detail,
    "scheduler_key": record.scheduler_key,
    "revision_id": record.revision_id,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "status": record.status,
    "action_scope": record.action_scope,
    "require_approval_note": record.require_approval_note,
    "default_moderation_status": record.default_moderation_status,
    "governance_view": record.governance_view,
    "window_days": record.window_days,
    "stale_pending_hours": record.stale_pending_hours,
    "minimum_score": record.minimum_score,
    "require_note": record.require_note,
    "actor_tab_id": record.actor_tab_id,
    "actor_tab_label": record.actor_tab_label,
  }


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item(
  item: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem,
) -> dict[str, Any]:
  return {
    "catalog_id": item.catalog_id,
    "catalog_name": item.catalog_name,
    "action": item.action,
    "current_status": item.current_status,
    "current_revision_id": item.current_revision_id,
    "rollback_revision_id": item.rollback_revision_id,
    "outcome": item.outcome,
    "message": item.message,
    "changed_fields": tuple(item.changed_fields),
    "field_diffs": item.field_diffs,
    "current_snapshot": item.current_snapshot,
    "proposed_snapshot": item.proposed_snapshot,
  }


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
) -> dict[str, Any]:
  return {
    "plan_id": record.plan_id,
    "created_at": record.created_at,
    "updated_at": record.updated_at,
    "scheduler_key": record.scheduler_key,
    "action": record.action,
    "status": record.status,
    "queue_state": record.queue_state,
    "governance_policy_id": record.governance_policy_id,
    "governance_policy_name": record.governance_policy_name,
    "require_approval_note": record.require_approval_note,
    "guidance": record.guidance,
    "requested_catalog_ids": tuple(record.requested_catalog_ids),
    "preview_count": len(record.preview_items),
    "preview_items": tuple(
      serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item(
        item
      )
      for item in record.preview_items
    ),
    "name_prefix": record.name_prefix,
    "name_suffix": record.name_suffix,
    "description_append": record.description_append,
    "default_moderation_status": record.default_moderation_status,
    "governance_view": record.governance_view,
    "window_days": record.window_days,
    "stale_pending_hours": record.stale_pending_hours,
    "minimum_score": record.minimum_score,
    "require_note": record.require_note,
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


def get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
  app: Any,
  governance_policy_id: str,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
  normalized_policy_id = (
    governance_policy_id.strip()
    if isinstance(governance_policy_id, str)
    else ""
  )
  for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records():
    if record.governance_policy_id == normalized_policy_id:
      return replace(
        record,
        status=app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status(
          record.status
        ),
      )
  raise LookupError("Scheduler search moderation catalog governance policy not found.")


def load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
  app: Any,
  revision_id: str,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord | None:
  normalized_revision_id = revision_id.strip() if isinstance(revision_id, str) else ""
  if not normalized_revision_id:
    return None
  for revision in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records():
    if revision.revision_id == normalized_revision_id:
      return revision
  return None


def get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
  app: Any,
  plan_id: str,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
  normalized_plan_id = plan_id.strip() if isinstance(plan_id, str) else ""
  for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records():
    if record.plan_id == normalized_plan_id:
      return record
  raise LookupError("Scheduler search moderation catalog governance plan not found.")


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
) -> dict[str, Any]:
  return {
    "meta_policy_id": record.meta_policy_id,
    "created_at": record.created_at,
    "updated_at": record.updated_at,
    "scheduler_key": record.scheduler_key,
    "status": record.status,
    "name": record.name,
    "description": record.description,
    "action_scope": record.action_scope,
    "require_approval_note": record.require_approval_note,
    "guidance": record.guidance,
    "name_prefix": record.name_prefix,
    "name_suffix": record.name_suffix,
    "description_append": record.description_append,
    "policy_action_scope": record.policy_action_scope,
    "policy_require_approval_note": record.policy_require_approval_note,
    "policy_guidance": record.policy_guidance,
    "default_moderation_status": record.default_moderation_status,
    "governance_view": record.governance_view,
    "window_days": record.window_days,
    "stale_pending_hours": record.stale_pending_hours,
    "minimum_score": record.minimum_score,
    "require_note": record.require_note,
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
  }


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item(
  item: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem,
) -> dict[str, Any]:
  return {
    "governance_policy_id": item.governance_policy_id,
    "governance_policy_name": item.governance_policy_name,
    "action": item.action,
    "current_status": item.current_status,
    "current_revision_id": item.current_revision_id,
    "rollback_revision_id": item.rollback_revision_id,
    "outcome": item.outcome,
    "message": item.message,
    "changed_fields": tuple(item.changed_fields),
    "field_diffs": item.field_diffs,
    "current_snapshot": item.current_snapshot,
    "proposed_snapshot": item.proposed_snapshot,
  }


def serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
) -> dict[str, Any]:
  return {
    "plan_id": record.plan_id,
    "created_at": record.created_at,
    "updated_at": record.updated_at,
    "scheduler_key": record.scheduler_key,
    "action": record.action,
    "status": record.status,
    "queue_state": record.queue_state,
    "meta_policy_id": record.meta_policy_id,
    "meta_policy_name": record.meta_policy_name,
    "require_approval_note": record.require_approval_note,
    "guidance": record.guidance,
    "requested_governance_policy_ids": tuple(record.requested_governance_policy_ids),
    "preview_count": len(record.preview_items),
    "preview_items": tuple(
      serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item(
        item
      )
      for item in record.preview_items
    ),
    "name_prefix": record.name_prefix,
    "name_suffix": record.name_suffix,
    "description_append": record.description_append,
    "policy_action_scope": record.policy_action_scope,
    "policy_require_approval_note": record.policy_require_approval_note,
    "policy_guidance": record.policy_guidance,
    "default_moderation_status": record.default_moderation_status,
    "governance_view": record.governance_view,
    "window_days": record.window_days,
    "stale_pending_hours": record.stale_pending_hours,
    "minimum_score": record.minimum_score,
    "require_note": record.require_note,
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


def get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
  app: Any,
  meta_policy_id: str,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
  normalized_meta_policy_id = meta_policy_id.strip() if isinstance(meta_policy_id, str) else ""
  for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records():
    if record.meta_policy_id == normalized_meta_policy_id:
      return record
  raise LookupError("Scheduler search moderation catalog governance meta policy not found.")


def get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
  app: Any,
  plan_id: str,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
  normalized_plan_id = plan_id.strip() if isinstance(plan_id, str) else ""
  for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records():
    if record.plan_id == normalized_plan_id:
      return record
  raise LookupError("Scheduler search moderation catalog governance meta plan not found.")
