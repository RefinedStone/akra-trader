from __future__ import annotations

from copy import deepcopy
from datetime import UTC
from datetime import datetime
from typing import Any

from akra_trader.application_flows.provider_provenance.mixins import ProviderProvenanceCompatibilityMixin
from akra_trader.domain.models import *  # noqa: F403

__all__ = (
  "serialize_provider_provenance_scheduler_narrative_template_record",
  "serialize_provider_provenance_scheduler_narrative_template_list",
  "serialize_provider_provenance_scheduler_narrative_template_revision_record",
  "serialize_provider_provenance_scheduler_narrative_template_revision_list",
  "serialize_provider_provenance_scheduler_narrative_bulk_governance_result",
  "serialize_provider_provenance_scheduler_narrative_governance_preview_item",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_template_record",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_template_list",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_record",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_list",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_record",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_list",
  "serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record",
  "serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list",
  "serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record",
  "serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list",
  "serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record",
  "serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list",
  "serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_list",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list",
  "serialize_provider_provenance_scheduler_narrative_governance_plan_record",
  "serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_result",
  "serialize_provider_provenance_scheduler_narrative_governance_plan_list",
  "serialize_provider_provenance_scheduler_narrative_governance_plan_batch_result",
  "serialize_provider_provenance_scheduler_narrative_registry_record",
  "serialize_provider_provenance_scheduler_narrative_registry_list",
  "serialize_provider_provenance_scheduler_narrative_registry_revision_record",
  "serialize_provider_provenance_scheduler_narrative_registry_revision_list",
)

def serialize_provider_provenance_scheduler_narrative_template_record(
  record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  return {
    "template_id": record.template_id,
    "name": record.name,
    "description": record.description,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "current_revision_id": record.current_revision_id,
    "revision_count": int(record.revision_count),
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
    "deleted_at": record.deleted_at.isoformat() if record.deleted_at else None,
    "deleted_by_tab_id": record.deleted_by_tab_id,
    "deleted_by_tab_label": record.deleted_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_template_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeTemplateRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_template_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_template_revision_record(
  record: ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  return {
    "revision_id": record.revision_id,
    "template_id": record.template_id,
    "action": record.action,
    "reason": record.reason,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "description": record.description,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "recorded_at": record.recorded_at.isoformat(),
    "recorded_by_tab_id": record.recorded_by_tab_id,
    "recorded_by_tab_label": record.recorded_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_template_revision_list(
  record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
  revisions: tuple[ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord, ...],
) -> dict[str, Any]:
  return {
    "template": serialize_provider_provenance_scheduler_narrative_template_record(record),
    "history": [
      serialize_provider_provenance_scheduler_narrative_template_revision_record(revision)
      for revision in revisions
    ],
  }

def serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
  record: ProviderProvenanceSchedulerNarrativeBulkGovernanceResult,
) -> dict[str, Any]:
  return {
    "item_type": record.item_type,
    "action": record.action,
    "reason": record.reason,
    "requested_count": record.requested_count,
    "applied_count": record.applied_count,
    "skipped_count": record.skipped_count,
    "failed_count": record.failed_count,
    "results": [
      {
        "item_id": item.item_id,
        "item_name": item.item_name,
        "outcome": item.outcome,
        "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
          item.status
        )
        if item.status is not None
        else None,
        "current_revision_id": item.current_revision_id,
        "message": item.message,
      }
      for item in record.results
    ],
  }

def serialize_provider_provenance_scheduler_narrative_governance_preview_item(
  record: ProviderProvenanceSchedulerNarrativeGovernancePreviewItem,
) -> dict[str, Any]:
  return {
    "item_id": record.item_id,
    "item_name": record.item_name,
    "status": (
      ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
        record.status
      )
      if record.status is not None
      else None
    ),
    "current_revision_id": record.current_revision_id,
    "apply_revision_id": record.apply_revision_id,
    "rollback_revision_id": record.rollback_revision_id,
    "outcome": record.outcome,
    "message": record.message,
    "changed_fields": list(record.changed_fields),
    "field_diffs": deepcopy(record.field_diffs),
    "current_snapshot": deepcopy(record.current_snapshot),
    "proposed_snapshot": deepcopy(record.proposed_snapshot),
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(
  record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
) -> dict[str, Any]:
  return {
    "policy_template_id": record.policy_template_id,
    "name": record.name,
    "description": record.description,
    "item_type_scope": record.item_type_scope,
    "action_scope": record.action_scope,
    "approval_lane": record.approval_lane,
    "approval_priority": record.approval_priority,
    "guidance": record.guidance,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "current_revision_id": record.current_revision_id,
    "revision_count": int(record.revision_count),
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
    "deleted_at": record.deleted_at.isoformat() if record.deleted_at else None,
    "deleted_by_tab_id": record.deleted_by_tab_id,
    "deleted_by_tab_label": record.deleted_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_template_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
  record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
) -> dict[str, Any]:
  return {
    "revision_id": record.revision_id,
    "policy_template_id": record.policy_template_id,
    "action": record.action,
    "reason": record.reason,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "description": record.description,
    "item_type_scope": record.item_type_scope,
    "action_scope": record.action_scope,
    "approval_lane": record.approval_lane,
    "approval_priority": record.approval_priority,
    "guidance": record.guidance,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "recorded_at": record.recorded_at.isoformat(),
    "recorded_by_tab_id": record.recorded_by_tab_id,
    "recorded_by_tab_label": record.recorded_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_list(
  record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  revisions: tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...],
) -> dict[str, Any]:
  return {
    "policy_template": serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(
      record
    ),
    "history": [
      serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
        revision
      )
      for revision in revisions
    ],
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
  record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "policy_template_id": record.policy_template_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "reason": record.reason,
    "detail": record.detail,
    "revision_id": record.revision_id,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "item_type_scope": record.item_type_scope,
    "action_scope": record.action_scope,
    "approval_lane": record.approval_lane,
    "approval_priority": record.approval_priority,
    "guidance": record.guidance,
    "actor_tab_id": record.actor_tab_id,
    "actor_tab_label": record.actor_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
        record
      )
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
  record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
) -> dict[str, Any]:
  return {
    "hierarchy_step_template_id": record.hierarchy_step_template_id,
    "name": record.name,
    "description": record.description,
    "item_type": record.item_type,
    "step": serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step(
      record.step
    ),
    "origin_catalog_id": record.origin_catalog_id,
    "origin_catalog_name": record.origin_catalog_name,
    "origin_step_id": record.origin_step_id,
    "governance_policy_template_id": record.governance_policy_template_id,
    "governance_policy_template_name": record.governance_policy_template_name,
    "governance_policy_catalog_id": record.governance_policy_catalog_id,
    "governance_policy_catalog_name": record.governance_policy_catalog_name,
    "governance_approval_lane": record.governance_approval_lane,
    "governance_approval_priority": record.governance_approval_priority,
    "governance_policy_guidance": record.governance_policy_guidance,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "current_revision_id": record.current_revision_id,
    "revision_count": record.revision_count,
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
    "deleted_at": record.deleted_at.isoformat() if record.deleted_at is not None else None,
    "deleted_by_tab_id": record.deleted_by_tab_id,
    "deleted_by_tab_label": record.deleted_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
        record
      )
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
  revision: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord,
) -> dict[str, Any]:
  return {
    "revision_id": revision.revision_id,
    "hierarchy_step_template_id": revision.hierarchy_step_template_id,
    "action": revision.action,
    "reason": revision.reason,
    "name": revision.name,
    "description": revision.description,
    "item_type": revision.item_type,
    "step": serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step(
      revision.step
    ),
    "origin_catalog_id": revision.origin_catalog_id,
    "origin_catalog_name": revision.origin_catalog_name,
    "origin_step_id": revision.origin_step_id,
    "governance_policy_template_id": revision.governance_policy_template_id,
    "governance_policy_template_name": revision.governance_policy_template_name,
    "governance_policy_catalog_id": revision.governance_policy_catalog_id,
    "governance_policy_catalog_name": revision.governance_policy_catalog_name,
    "governance_approval_lane": revision.governance_approval_lane,
    "governance_approval_priority": revision.governance_approval_priority,
    "governance_policy_guidance": revision.governance_policy_guidance,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      revision.status
    ),
    "recorded_at": revision.recorded_at.isoformat(),
    "source_revision_id": revision.source_revision_id,
    "recorded_by_tab_id": revision.recorded_by_tab_id,
    "recorded_by_tab_label": revision.recorded_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list(
  record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
  revisions: tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord, ...],
) -> dict[str, Any]:
  return {
    "current": serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      record
    ),
    "history": [
      serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
        revision
      )
      for revision in revisions
    ],
  }

def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
  record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "hierarchy_step_template_id": record.hierarchy_step_template_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "reason": record.reason,
    "detail": record.detail,
    "revision_id": record.revision_id,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "description": record.description,
    "item_type": record.item_type,
    "step": serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step(record.step),
    "origin_catalog_id": record.origin_catalog_id,
    "origin_catalog_name": record.origin_catalog_name,
    "origin_step_id": record.origin_step_id,
    "governance_policy_template_id": record.governance_policy_template_id,
    "governance_policy_template_name": record.governance_policy_template_name,
    "governance_policy_catalog_id": record.governance_policy_catalog_id,
    "governance_policy_catalog_name": record.governance_policy_catalog_name,
    "governance_approval_lane": record.governance_approval_lane,
    "governance_approval_priority": record.governance_approval_priority,
    "governance_policy_guidance": record.governance_policy_guidance,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "actor_tab_id": record.actor_tab_id,
    "actor_tab_label": record.actor_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
        record
      )
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step(
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep,
) -> dict[str, Any]:
  return {
    "step_id": step.step_id,
    "source_template_id": step.source_template_id,
    "source_template_name": step.source_template_name,
    "item_type": step.item_type,
    "action": step.action,
    "item_ids": list(step.item_ids),
    "item_names": list(step.item_names),
    "name_prefix": step.name_prefix,
    "name_suffix": step.name_suffix,
    "description_append": step.description_append,
    "query_patch": deepcopy(step.query_patch),
    "layout_patch": deepcopy(step.layout_patch),
    "template_id": step.template_id,
    "clear_template_link": step.clear_template_link,
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
  record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
) -> dict[str, Any]:
  return {
    "catalog_id": record.catalog_id,
    "name": record.name,
    "description": record.description,
    "policy_template_ids": list(record.policy_template_ids),
    "policy_template_names": list(record.policy_template_names),
    "default_policy_template_id": record.default_policy_template_id,
    "default_policy_template_name": record.default_policy_template_name,
    "item_type_scope": record.item_type_scope,
    "action_scope": record.action_scope,
    "approval_lane": record.approval_lane,
    "approval_priority": record.approval_priority,
    "guidance": record.guidance,
    "hierarchy_steps": [
      serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step(step)
      for step in record.hierarchy_steps
    ],
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "current_revision_id": record.current_revision_id,
    "revision_count": record.revision_count,
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
    "deleted_at": record.deleted_at.isoformat() if record.deleted_at is not None else None,
    "deleted_by_tab_id": record.deleted_by_tab_id,
    "deleted_by_tab_label": record.deleted_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
  revision: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
) -> dict[str, Any]:
  return {
    "revision_id": revision.revision_id,
    "catalog_id": revision.catalog_id,
    "action": revision.action,
    "reason": revision.reason,
    "name": revision.name,
    "description": revision.description,
    "policy_template_ids": list(revision.policy_template_ids),
    "policy_template_names": list(revision.policy_template_names),
    "default_policy_template_id": revision.default_policy_template_id,
    "default_policy_template_name": revision.default_policy_template_name,
    "item_type_scope": revision.item_type_scope,
    "action_scope": revision.action_scope,
    "approval_lane": revision.approval_lane,
    "approval_priority": revision.approval_priority,
    "guidance": revision.guidance,
    "hierarchy_steps": [
      serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step(step)
      for step in revision.hierarchy_steps
    ],
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      revision.status
    ),
    "recorded_at": revision.recorded_at.isoformat(),
    "source_revision_id": revision.source_revision_id,
    "recorded_by_tab_id": revision.recorded_by_tab_id,
    "recorded_by_tab_label": revision.recorded_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list(
  record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  revisions: tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...],
) -> dict[str, Any]:
  return {
    "current": serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record),
    "history": [
      serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
        revision
      )
      for revision in revisions
    ],
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
  record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "catalog_id": record.catalog_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "reason": record.reason,
    "detail": record.detail,
    "revision_id": record.revision_id,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "default_policy_template_id": record.default_policy_template_id,
    "default_policy_template_name": record.default_policy_template_name,
    "policy_template_ids": list(record.policy_template_ids),
    "policy_template_names": list(record.policy_template_names),
    "item_type_scope": record.item_type_scope,
    "action_scope": record.action_scope,
    "approval_lane": record.approval_lane,
    "approval_priority": record.approval_priority,
    "guidance": record.guidance,
    "hierarchy_steps": [
      serialize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_step(step)
      for step in record.hierarchy_steps
    ],
    "actor_tab_id": record.actor_tab_id,
    "actor_tab_label": record.actor_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
        record
      )
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_governance_plan_record(
  record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
) -> dict[str, Any]:
  return {
    "plan_id": record.plan_id,
    "item_type": record.item_type,
    "action": record.action,
    "reason": record.reason,
    "status": record.status,
    "queue_state": ProviderProvenanceCompatibilityMixin._build_provider_provenance_scheduler_narrative_governance_queue_state(
      record.status
    ),
    "policy_template_id": record.policy_template_id,
    "policy_template_name": record.policy_template_name,
    "policy_catalog_id": record.policy_catalog_id,
    "policy_catalog_name": record.policy_catalog_name,
    "approval_lane": record.approval_lane,
    "approval_priority": record.approval_priority,
    "policy_guidance": record.policy_guidance,
    "source_hierarchy_step_template_id": record.source_hierarchy_step_template_id,
    "source_hierarchy_step_template_name": record.source_hierarchy_step_template_name,
    "hierarchy_key": record.hierarchy_key,
    "hierarchy_name": record.hierarchy_name,
    "hierarchy_position": record.hierarchy_position,
    "hierarchy_total": record.hierarchy_total,
    "request_payload": deepcopy(record.request_payload),
    "target_ids": list(record.target_ids),
    "preview_requested_count": record.preview_requested_count,
    "preview_changed_count": record.preview_changed_count,
    "preview_skipped_count": record.preview_skipped_count,
    "preview_failed_count": record.preview_failed_count,
    "preview_items": [
      serialize_provider_provenance_scheduler_narrative_governance_preview_item(item)
      for item in record.preview_items
    ],
    "rollback_ready_count": record.rollback_ready_count,
    "rollback_summary": record.rollback_summary,
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
    "approved_at": record.approved_at.isoformat() if record.approved_at is not None else None,
    "approved_by_tab_id": record.approved_by_tab_id,
    "approved_by_tab_label": record.approved_by_tab_label,
    "approval_note": record.approval_note,
    "applied_at": record.applied_at.isoformat() if record.applied_at is not None else None,
    "applied_by_tab_id": record.applied_by_tab_id,
    "applied_by_tab_label": record.applied_by_tab_label,
    "applied_result": (
      serialize_provider_provenance_scheduler_narrative_bulk_governance_result(record.applied_result)
      if record.applied_result is not None
      else None
    ),
    "rolled_back_at": record.rolled_back_at.isoformat() if record.rolled_back_at is not None else None,
    "rolled_back_by_tab_id": record.rolled_back_by_tab_id,
    "rolled_back_by_tab_label": record.rolled_back_by_tab_label,
    "rollback_note": record.rollback_note,
    "rollback_result": (
      serialize_provider_provenance_scheduler_narrative_bulk_governance_result(record.rollback_result)
      if record.rollback_result is not None
      else None
    ),
  }

def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_result(
  result: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult,
) -> dict[str, Any]:
  return {
    "catalog_id": result.catalog_id,
    "catalog_name": result.catalog_name,
    "hierarchy_key": result.hierarchy_key,
    "hierarchy_name": result.hierarchy_name,
    "plan_count": result.plan_count,
    "summary": result.summary,
    "plans": [
      serialize_provider_provenance_scheduler_narrative_governance_plan_record(plan)
      for plan in result.plans
    ],
  }

def serialize_provider_provenance_scheduler_narrative_governance_plan_list(
  result: ProviderProvenanceSchedulerNarrativeGovernancePlanListResult,
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_governance_plan_record(record)
      for record in result.items
    ],
    "total": result.total,
    "pending_approval_count": result.pending_approval_count,
    "ready_to_apply_count": result.ready_to_apply_count,
    "completed_count": result.completed_count,
  }

def serialize_provider_provenance_scheduler_narrative_governance_plan_batch_result(
  record: ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult,
) -> dict[str, Any]:
  return {
    "action": record.action,
    "requested_count": record.requested_count,
    "succeeded_count": record.succeeded_count,
    "skipped_count": record.skipped_count,
    "failed_count": record.failed_count,
    "results": [
      {
        "plan_id": result.plan_id,
        "action": result.action,
        "outcome": result.outcome,
        "status": result.status,
        "queue_state": result.queue_state,
        "message": result.message,
        "plan": (
          serialize_provider_provenance_scheduler_narrative_governance_plan_record(result.plan)
          if result.plan is not None
          else None
        ),
      }
      for result in record.results
    ],
  }

def serialize_provider_provenance_scheduler_narrative_registry_record(
  record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  normalized_layout = (
    ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
      record.layout
    )
  )
  return {
    "registry_id": record.registry_id,
    "name": record.name,
    "description": record.description,
    "template_id": record.template_id,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "layout": deepcopy(normalized_layout),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "current_revision_id": record.current_revision_id,
    "revision_count": int(record.revision_count),
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
    "deleted_at": record.deleted_at.isoformat() if record.deleted_at else None,
    "deleted_by_tab_id": record.deleted_by_tab_id,
    "deleted_by_tab_label": record.deleted_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_registry_list(
  records: tuple[ProviderProvenanceSchedulerNarrativeRegistryRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_narrative_registry_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_narrative_registry_revision_record(
  record: ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  normalized_layout = (
    ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
      record.layout
    )
  )
  return {
    "revision_id": record.revision_id,
    "registry_id": record.registry_id,
    "action": record.action,
    "reason": record.reason,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "description": record.description,
    "template_id": record.template_id,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "layout": deepcopy(normalized_layout),
    "recorded_at": record.recorded_at.isoformat(),
    "recorded_by_tab_id": record.recorded_by_tab_id,
    "recorded_by_tab_label": record.recorded_by_tab_label,
  }

def serialize_provider_provenance_scheduler_narrative_registry_revision_list(
  record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
  revisions: tuple[ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord, ...],
) -> dict[str, Any]:
  return {
    "registry": serialize_provider_provenance_scheduler_narrative_registry_record(record),
    "history": [
      serialize_provider_provenance_scheduler_narrative_registry_revision_record(revision)
      for revision in revisions
    ],
  }
