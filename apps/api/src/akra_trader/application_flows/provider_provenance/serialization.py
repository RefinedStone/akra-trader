from __future__ import annotations

from copy import deepcopy
from datetime import UTC
from datetime import datetime
from typing import Any

from akra_trader.application_flows.provider_provenance.mixins import ProviderProvenanceCompatibilityMixin
from akra_trader.domain.models import *  # noqa: F403


def serialize_replay_intent_alias_record(record: ReplayIntentAliasRecord) -> dict[str, Any]:
  return {
    "alias_id": record.alias_id,
    "alias_token": ProviderProvenanceCompatibilityMixin._build_replay_intent_alias_token(
      record.alias_id,
      record.signature,
    ),
    "created_at": record.created_at.isoformat(),
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "intent": deepcopy(record.intent),
    "redaction_policy": record.redaction_policy,
    "retention_policy": record.retention_policy,
    "resolution_source": "server",
    "revoked_at": record.revoked_at.isoformat() if record.revoked_at is not None else None,
    "revoked_by_tab_id": record.revoked_by_tab_id,
    "revoked_by_tab_label": record.revoked_by_tab_label,
    "signature": record.signature,
    "template_key": record.template_key,
    "template_label": record.template_label,
  }

def serialize_replay_intent_alias_audit_record(record: ReplayIntentAliasAuditRecord) -> dict[str, Any]:
  return {
    "action": record.action,
    "alias_created_at": (
      record.alias_created_at.isoformat() if record.alias_created_at is not None else None
    ),
    "alias_expires_at": (
      record.alias_expires_at.isoformat() if record.alias_expires_at is not None else None
    ),
    "alias_id": record.alias_id,
    "alias_revoked_at": (
      record.alias_revoked_at.isoformat() if record.alias_revoked_at is not None else None
    ),
    "audit_id": record.audit_id,
    "detail": record.detail,
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "recorded_at": record.recorded_at.isoformat(),
    "redaction_policy": record.redaction_policy,
    "retention_policy": record.retention_policy,
    "source_tab_id": record.source_tab_id,
    "source_tab_label": record.source_tab_label,
    "template_key": record.template_key,
    "template_label": record.template_label,
  }

def serialize_replay_intent_alias_history(
  record: ReplayIntentAliasRecord,
  audit_records: tuple[ReplayIntentAliasAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "alias": serialize_replay_intent_alias_record(record),
    "history": [
      serialize_replay_intent_alias_audit_record(audit_record)
      for audit_record in audit_records
    ],
  }

def serialize_replay_intent_alias_audit_list(
  audit_records: tuple[ReplayIntentAliasAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_replay_intent_alias_audit_record(audit_record)
      for audit_record in audit_records
    ],
    "total": len(audit_records),
  }

def serialize_replay_intent_alias_audit_export_job_record(
  record: ReplayIntentAliasAuditExportJobRecord,
  *,
  include_content: bool = False,
  content: str | None = None,
) -> dict[str, Any]:
  payload = {
    "job_id": record.job_id,
    "export_format": record.export_format,
    "filename": record.filename,
    "content_type": record.content_type,
    "record_count": record.record_count,
    "status": record.status,
    "created_at": record.created_at.isoformat(),
    "completed_at": record.completed_at.isoformat() if record.completed_at is not None else None,
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "template_key": record.template_key,
    "requested_by_tab_id": record.requested_by_tab_id,
    "requested_by_tab_label": record.requested_by_tab_label,
    "filters": deepcopy(record.filters),
    "artifact_id": record.artifact_id,
    "content_length": record.content_length,
  }
  if include_content:
    payload["content"] = content if content is not None else record.content
  return payload

def serialize_replay_intent_alias_audit_export_job_audit_record(
  record: ReplayIntentAliasAuditExportJobAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "job_id": record.job_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "template_key": record.template_key,
    "export_format": record.export_format,
    "source_tab_id": record.source_tab_id,
    "source_tab_label": record.source_tab_label,
    "detail": record.detail,
  }

def serialize_replay_intent_alias_audit_export_job_list(
  records: tuple[ReplayIntentAliasAuditExportJobRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_replay_intent_alias_audit_export_job_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_replay_intent_alias_audit_export_job_history(
  record: ReplayIntentAliasAuditExportJobRecord,
  audit_records: tuple[ReplayIntentAliasAuditExportJobAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "job": serialize_replay_intent_alias_audit_export_job_record(record),
    "history": [
      serialize_replay_intent_alias_audit_export_job_audit_record(audit_record)
      for audit_record in audit_records
    ],
  }

def serialize_provider_provenance_export_job_record(
  record: ProviderProvenanceExportJobRecord,
  *,
  include_content: bool = False,
  content: str | None = None,
) -> dict[str, Any]:
  payload = {
    "job_id": record.job_id,
    "export_scope": record.export_scope,
    "export_format": record.export_format,
    "filename": record.filename,
    "content_type": record.content_type,
    "status": record.status,
    "created_at": record.created_at.isoformat(),
    "completed_at": record.completed_at.isoformat() if record.completed_at is not None else None,
    "exported_at": record.exported_at.isoformat() if record.exported_at is not None else None,
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "focus_key": record.focus_key,
    "focus_label": record.focus_label,
    "market_data_provider": record.market_data_provider,
    "venue": record.venue,
    "symbol": record.symbol,
    "timeframe": record.timeframe,
    "result_count": record.result_count,
    "provider_provenance_count": record.provider_provenance_count,
    "provider_labels": list(record.provider_labels),
    "vendor_fields": list(record.vendor_fields),
    "filter_summary": record.filter_summary,
    "filters": deepcopy(record.filters),
    "requested_by_tab_id": record.requested_by_tab_id,
    "requested_by_tab_label": record.requested_by_tab_label,
    "available_delivery_targets": list(record.available_delivery_targets),
    "routing_policy_id": record.routing_policy_id,
    "routing_policy_summary": record.routing_policy_summary,
    "routing_targets": list(record.routing_targets),
    "approval_policy_id": record.approval_policy_id,
    "approval_required": record.approval_required,
    "approval_state": record.approval_state,
    "approval_summary": record.approval_summary,
    "approved_at": record.approved_at.isoformat() if record.approved_at is not None else None,
    "approved_by": record.approved_by,
    "approval_note": record.approval_note,
    "escalation_count": record.escalation_count,
    "last_escalated_at": record.last_escalated_at.isoformat() if record.last_escalated_at is not None else None,
    "last_escalated_by": record.last_escalated_by,
    "last_escalation_reason": record.last_escalation_reason,
    "last_delivery_targets": list(record.last_delivery_targets),
    "last_delivery_status": record.last_delivery_status,
    "last_delivery_summary": record.last_delivery_summary,
    "artifact_id": record.artifact_id,
    "content_length": record.content_length,
  }
  if include_content:
    payload["content"] = content if content is not None else record.content
  return payload

def serialize_provider_provenance_export_job_audit_record(
  record: ProviderProvenanceExportJobAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "job_id": record.job_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "export_scope": record.export_scope,
    "export_format": record.export_format,
    "focus_key": record.focus_key,
    "focus_label": record.focus_label,
    "symbol": record.symbol,
    "timeframe": record.timeframe,
    "market_data_provider": record.market_data_provider,
    "requested_by_tab_id": record.requested_by_tab_id,
    "requested_by_tab_label": record.requested_by_tab_label,
    "source_tab_id": record.source_tab_id,
    "source_tab_label": record.source_tab_label,
    "routing_policy_id": record.routing_policy_id,
    "routing_targets": list(record.routing_targets),
    "approval_policy_id": record.approval_policy_id,
    "approval_required": record.approval_required,
    "approval_state": record.approval_state,
    "approval_summary": record.approval_summary,
    "approved_by": record.approved_by,
    "delivery_targets": list(record.delivery_targets),
    "delivery_status": record.delivery_status,
    "delivery_summary": record.delivery_summary,
    "detail": record.detail,
  }

def serialize_operator_incident_delivery_record(
  record: OperatorIncidentDelivery,
) -> dict[str, Any]:
  return {
    "delivery_id": record.delivery_id,
    "incident_event_id": record.incident_event_id,
    "alert_id": record.alert_id,
    "incident_kind": record.incident_kind,
    "target": record.target,
    "status": record.status,
    "attempted_at": record.attempted_at.isoformat(),
    "detail": record.detail,
    "attempt_number": record.attempt_number,
    "next_retry_at": record.next_retry_at.isoformat() if record.next_retry_at is not None else None,
    "phase": record.phase,
    "provider_action": record.provider_action,
    "external_provider": record.external_provider,
    "external_reference": record.external_reference,
    "source": record.source,
  }

def serialize_provider_provenance_export_job_escalation_result(
  record: ProviderProvenanceExportJobRecord,
  audit_record: ProviderProvenanceExportJobAuditRecord,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
) -> dict[str, Any]:
  return {
    "export_job": serialize_provider_provenance_export_job_record(record),
    "audit_record": serialize_provider_provenance_export_job_audit_record(audit_record),
    "delivery_history": [
      serialize_operator_incident_delivery_record(delivery_record)
      for delivery_record in delivery_history
    ],
  }

def serialize_provider_provenance_export_job_policy_result(
  record: ProviderProvenanceExportJobRecord,
  audit_record: ProviderProvenanceExportJobAuditRecord,
) -> dict[str, Any]:
  return {
    "export_job": serialize_provider_provenance_export_job_record(record),
    "audit_record": serialize_provider_provenance_export_job_audit_record(audit_record),
  }

def serialize_provider_provenance_export_job_list(
  records: tuple[ProviderProvenanceExportJobRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_export_job_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_export_job_history(
  record: ProviderProvenanceExportJobRecord,
  audit_records: tuple[ProviderProvenanceExportJobAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "job": serialize_provider_provenance_export_job_record(record),
    "history": [
      serialize_provider_provenance_export_job_audit_record(audit_record)
      for audit_record in audit_records
    ],
  }

def serialize_provider_provenance_analytics_preset_record(
  record: ProviderProvenanceAnalyticsPresetRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  return {
    "preset_id": record.preset_id,
    "name": record.name,
    "description": record.description,
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
  }

def serialize_provider_provenance_analytics_preset_list(
  records: tuple[ProviderProvenanceAnalyticsPresetRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_analytics_preset_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_dashboard_view_record(
  record: ProviderProvenanceDashboardViewRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  normalized_layout = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_dashboard_layout_payload(
    record.layout
  )
  return {
    "view_id": record.view_id,
    "name": record.name,
    "description": record.description,
    "preset_id": record.preset_id,
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "layout": deepcopy(normalized_layout),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
  }

def serialize_provider_provenance_dashboard_view_list(
  records: tuple[ProviderProvenanceDashboardViewRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_dashboard_view_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_stitched_report_view_record(
  record: ProviderProvenanceSchedulerStitchedReportViewRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  return {
    "view_id": record.view_id,
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
    "occurrence_limit": int(record.occurrence_limit),
    "history_limit": int(record.history_limit),
    "drilldown_history_limit": int(record.drilldown_history_limit),
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

def serialize_provider_provenance_scheduler_stitched_report_view_list(
  records: tuple[ProviderProvenanceSchedulerStitchedReportViewRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_stitched_report_view_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_stitched_report_view_revision_record(
  record: ProviderProvenanceSchedulerStitchedReportViewRevisionRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  return {
    "revision_id": record.revision_id,
    "view_id": record.view_id,
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
    "occurrence_limit": int(record.occurrence_limit),
    "history_limit": int(record.history_limit),
    "drilldown_history_limit": int(record.drilldown_history_limit),
    "recorded_at": record.recorded_at.isoformat(),
    "recorded_by_tab_id": record.recorded_by_tab_id,
    "recorded_by_tab_label": record.recorded_by_tab_label,
  }

def serialize_provider_provenance_scheduler_stitched_report_view_revision_list(
  record: ProviderProvenanceSchedulerStitchedReportViewRecord,
  revisions: tuple[ProviderProvenanceSchedulerStitchedReportViewRevisionRecord, ...],
) -> dict[str, Any]:
  return {
    "view": serialize_provider_provenance_scheduler_stitched_report_view_record(record),
    "history": [
      serialize_provider_provenance_scheduler_stitched_report_view_revision_record(revision)
      for revision in revisions
    ],
  }

def serialize_provider_provenance_scheduler_stitched_report_view_audit_record(
  record: ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "view_id": record.view_id,
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
    "occurrence_limit": int(record.occurrence_limit),
    "history_limit": int(record.history_limit),
    "drilldown_history_limit": int(record.drilldown_history_limit),
    "filter_summary": record.filter_summary,
    "actor_tab_id": record.actor_tab_id,
    "actor_tab_label": record.actor_tab_label,
  }

def serialize_provider_provenance_scheduler_stitched_report_view_audit_list(
  records: tuple[ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_stitched_report_view_audit_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(
  record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
) -> dict[str, Any]:
  normalized_queue_view = (
    ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
      record.queue_view
    )
  )
  if isinstance(normalized_queue_view, dict):
    normalized_queue_view["item_type"] = "stitched_report_view"
  else:
    normalized_queue_view = {"item_type": "stitched_report_view"}
  return {
    "registry_id": record.registry_id,
    "name": record.name,
    "description": record.description,
    "queue_view": deepcopy(normalized_queue_view),
    "default_policy_template_id": record.default_policy_template_id,
    "default_policy_template_name": record.default_policy_template_name,
    "default_policy_catalog_id": record.default_policy_catalog_id,
    "default_policy_catalog_name": record.default_policy_catalog_name,
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

def serialize_provider_provenance_scheduler_stitched_report_governance_registry_list(
  records: tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
  record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord,
) -> dict[str, Any]:
  normalized_queue_view = (
    ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
      record.queue_view
    )
  )
  if isinstance(normalized_queue_view, dict):
    normalized_queue_view["item_type"] = "stitched_report_view"
  else:
    normalized_queue_view = {"item_type": "stitched_report_view"}
  return {
    "revision_id": record.revision_id,
    "registry_id": record.registry_id,
    "action": record.action,
    "reason": record.reason,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "description": record.description,
    "queue_view": deepcopy(normalized_queue_view),
    "default_policy_template_id": record.default_policy_template_id,
    "default_policy_template_name": record.default_policy_template_name,
    "default_policy_catalog_id": record.default_policy_catalog_id,
    "default_policy_catalog_name": record.default_policy_catalog_name,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "recorded_at": record.recorded_at.isoformat(),
    "recorded_by_tab_id": record.recorded_by_tab_id,
    "recorded_by_tab_label": record.recorded_by_tab_label,
  }

def serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_list(
  record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
  revisions: tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord, ...],
) -> dict[str, Any]:
  return {
    "registry": serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(
      record
    ),
    "history": [
      serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
        revision
      )
      for revision in revisions
    ],
  }

def serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(
  record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
) -> dict[str, Any]:
  normalized_queue_view = (
    ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
      record.queue_view
    )
  )
  if isinstance(normalized_queue_view, dict):
    normalized_queue_view["item_type"] = "stitched_report_view"
  else:
    normalized_queue_view = {"item_type": "stitched_report_view"}
  return {
    "audit_id": record.audit_id,
    "registry_id": record.registry_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "reason": record.reason,
    "detail": record.detail,
    "revision_id": record.revision_id,
    "source_revision_id": record.source_revision_id,
    "name": record.name,
    "description": record.description,
    "queue_view": deepcopy(normalized_queue_view),
    "default_policy_template_id": record.default_policy_template_id,
    "default_policy_template_name": record.default_policy_template_name,
    "default_policy_catalog_id": record.default_policy_catalog_id,
    "default_policy_catalog_name": record.default_policy_catalog_name,
    "status": ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_record_status(
      record.status
    ),
    "actor_tab_id": record.actor_tab_id,
    "actor_tab_label": record.actor_tab_label,
  }

def serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_list(
  records: tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(record)
      for record in records
    ],
    "total": len(records),
  }

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

def serialize_provider_provenance_scheduled_report_record(
  record: ProviderProvenanceScheduledReportRecord,
) -> dict[str, Any]:
  normalized_query = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_analytics_query_payload(
    record.query
  )
  normalized_layout = ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_dashboard_layout_payload(
    record.layout
  )
  return {
    "report_id": record.report_id,
    "name": record.name,
    "description": record.description,
    "preset_id": record.preset_id,
    "view_id": record.view_id,
    "cadence": record.cadence,
    "status": record.status,
    "query": deepcopy(normalized_query),
    "focus": ProviderProvenanceCompatibilityMixin._build_provider_provenance_workspace_focus_payload(normalized_query),
    "filter_summary": ProviderProvenanceCompatibilityMixin._build_provider_provenance_analytics_filter_summary(
      normalized_query
    ),
    "layout": deepcopy(normalized_layout),
    "created_at": record.created_at.isoformat(),
    "updated_at": record.updated_at.isoformat(),
    "next_run_at": record.next_run_at.isoformat() if record.next_run_at is not None else None,
    "last_run_at": record.last_run_at.isoformat() if record.last_run_at is not None else None,
    "last_export_job_id": record.last_export_job_id,
    "created_by_tab_id": record.created_by_tab_id,
    "created_by_tab_label": record.created_by_tab_label,
  }

def serialize_provider_provenance_scheduler_health(
  record: ProviderProvenanceSchedulerHealth,
) -> dict[str, Any]:
  return {
    "generated_at": record.generated_at.isoformat(),
    "enabled": record.enabled,
    "status": record.status,
    "summary": record.summary,
    "interval_seconds": record.interval_seconds,
    "batch_limit": record.batch_limit,
    "last_cycle_started_at": (
      record.last_cycle_started_at.isoformat()
      if record.last_cycle_started_at is not None
      else None
    ),
    "last_cycle_finished_at": (
      record.last_cycle_finished_at.isoformat()
      if record.last_cycle_finished_at is not None
      else None
    ),
    "last_success_at": record.last_success_at.isoformat() if record.last_success_at is not None else None,
    "last_failure_at": record.last_failure_at.isoformat() if record.last_failure_at is not None else None,
    "last_error": record.last_error,
    "cycle_count": record.cycle_count,
    "success_count": record.success_count,
    "failure_count": record.failure_count,
    "consecutive_failure_count": record.consecutive_failure_count,
    "last_executed_count": record.last_executed_count,
    "total_executed_count": record.total_executed_count,
    "due_report_count": record.due_report_count,
    "oldest_due_at": record.oldest_due_at.isoformat() if record.oldest_due_at is not None else None,
    "max_due_lag_seconds": record.max_due_lag_seconds,
    "active_alert_key": record.active_alert_key,
    "alert_workflow_job_id": record.alert_workflow_job_id,
    "alert_workflow_triggered_at": (
      record.alert_workflow_triggered_at.isoformat()
      if record.alert_workflow_triggered_at is not None
      else None
    ),
    "alert_workflow_state": record.alert_workflow_state,
    "alert_workflow_summary": record.alert_workflow_summary,
    "issues": list(record.issues),
  }

def serialize_provider_provenance_scheduler_health_record(
  record: ProviderProvenanceSchedulerHealthRecord,
) -> dict[str, Any]:
  return {
    "record_id": record.record_id,
    "scheduler_key": record.scheduler_key,
    "recorded_at": record.recorded_at.isoformat(),
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "enabled": record.enabled,
    "status": record.status,
    "summary": record.summary,
    "interval_seconds": record.interval_seconds,
    "batch_limit": record.batch_limit,
    "last_cycle_started_at": (
      record.last_cycle_started_at.isoformat()
      if record.last_cycle_started_at is not None
      else None
    ),
    "last_cycle_finished_at": (
      record.last_cycle_finished_at.isoformat()
      if record.last_cycle_finished_at is not None
      else None
    ),
    "last_success_at": record.last_success_at.isoformat() if record.last_success_at is not None else None,
    "last_failure_at": record.last_failure_at.isoformat() if record.last_failure_at is not None else None,
    "last_error": record.last_error,
    "cycle_count": record.cycle_count,
    "success_count": record.success_count,
    "failure_count": record.failure_count,
    "consecutive_failure_count": record.consecutive_failure_count,
    "last_executed_count": record.last_executed_count,
    "total_executed_count": record.total_executed_count,
    "due_report_count": record.due_report_count,
    "oldest_due_at": record.oldest_due_at.isoformat() if record.oldest_due_at is not None else None,
    "max_due_lag_seconds": record.max_due_lag_seconds,
    "active_alert_key": record.active_alert_key,
    "alert_workflow_job_id": record.alert_workflow_job_id,
    "alert_workflow_triggered_at": (
      record.alert_workflow_triggered_at.isoformat()
      if record.alert_workflow_triggered_at is not None
      else None
    ),
    "alert_workflow_state": record.alert_workflow_state,
    "alert_workflow_summary": record.alert_workflow_summary,
    "source_tab_id": record.source_tab_id,
    "source_tab_label": record.source_tab_label,
    "issues": list(record.issues),
  }

def serialize_provider_provenance_scheduler_health_history(
  current: ProviderProvenanceSchedulerHealth,
  payload: dict[str, Any],
) -> dict[str, Any]:
  items = payload.get("items", ())
  query = payload.get("query", {})
  return {
    "generated_at": current.generated_at.isoformat(),
    "query": {
      "status": query.get("status"),
      "limit": int(query.get("limit", 25)),
      "offset": int(query.get("offset", 0)),
    },
    "current": serialize_provider_provenance_scheduler_health(current),
    "items": [
      serialize_provider_provenance_scheduler_health_record(record)
      for record in items
    ],
    "total": int(payload.get("total", 0)),
    "returned": int(payload.get("returned", 0)),
    "has_more": bool(payload.get("has_more", False)),
    "next_offset": payload.get("next_offset"),
    "previous_offset": payload.get("previous_offset"),
  }

def serialize_operator_alert(
  alert: OperatorAlert,
) -> dict[str, Any]:
  return {
    "alert_id": alert.alert_id,
    "severity": alert.severity,
    "category": alert.category,
    "summary": alert.summary,
    "detail": alert.detail,
    "detected_at": alert.detected_at.isoformat(),
    "run_id": alert.run_id,
    "session_id": alert.session_id,
    "symbol": alert.symbol,
    "symbols": list(alert.symbols),
    "timeframe": alert.timeframe,
    "primary_focus": ProviderProvenanceCompatibilityMixin._serialize_operator_alert_primary_focus_payload(
      alert.primary_focus,
    ),
    "occurrence_id": alert.occurrence_id,
    "timeline_key": alert.timeline_key,
    "timeline_position": alert.timeline_position,
    "timeline_total": alert.timeline_total,
    "status": alert.status,
    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else None,
    "source": alert.source,
    "delivery_targets": list(alert.delivery_targets),
  }

def serialize_provider_provenance_scheduler_alert_history(
  payload: dict[str, Any],
) -> dict[str, Any]:
  items = payload.get("items", ())
  query = payload.get("query", {})
  summary = payload.get("summary", {})
  generated_at = payload.get("generated_at")
  return {
    "generated_at": (
      generated_at.isoformat()
      if isinstance(generated_at, datetime)
      else datetime.now(tz=UTC).isoformat()
    ),
    "query": {
      "category": query.get("category"),
      "status": query.get("status"),
      "narrative_facet": query.get("narrative_facet"),
      "search": query.get("search"),
      "limit": int(query.get("limit", 25)),
      "offset": int(query.get("offset", 0)),
    },
    "available_filters": {
      "categories": list(payload.get("available_filters", {}).get("categories", ())),
      "statuses": list(payload.get("available_filters", {}).get("statuses", ())),
      "narrative_facets": list(
        payload.get("available_filters", {}).get("narrative_facets", ())
      ),
    },
    "summary": {
      "total_occurrences": int(summary.get("total_occurrences", 0)),
      "active_count": int(summary.get("active_count", 0)),
      "resolved_count": int(summary.get("resolved_count", 0)),
      "by_category": [
        {
          "category": entry.get("category"),
          "total": int(entry.get("total", 0)),
          "active_count": int(entry.get("active_count", 0)),
          "resolved_count": int(entry.get("resolved_count", 0)),
        }
        for entry in summary.get("by_category", ())
      ],
    },
    "search_summary": (
      {
        "query_id": payload.get("search_summary", {}).get("query_id"),
        "query": payload.get("search_summary", {}).get("query"),
        "mode": payload.get("search_summary", {}).get("mode"),
        "token_count": int(payload.get("search_summary", {}).get("token_count", 0)),
        "matched_occurrences": int(payload.get("search_summary", {}).get("matched_occurrences", 0)),
        "top_score": int(payload.get("search_summary", {}).get("top_score", 0)),
        "max_term_coverage_pct": int(
          payload.get("search_summary", {}).get("max_term_coverage_pct", 0)
        ),
        "phrase_match_count": int(payload.get("search_summary", {}).get("phrase_match_count", 0)),
        "operator_count": int(payload.get("search_summary", {}).get("operator_count", 0)),
        "semantic_concept_count": int(
          payload.get("search_summary", {}).get("semantic_concept_count", 0)
        ),
        "negated_term_count": int(payload.get("search_summary", {}).get("negated_term_count", 0)),
        "boolean_operator_count": int(
          payload.get("search_summary", {}).get("boolean_operator_count", 0)
        ),
        "indexed_occurrence_count": int(
          payload.get("search_summary", {}).get("indexed_occurrence_count", 0)
        ),
        "indexed_term_count": int(payload.get("search_summary", {}).get("indexed_term_count", 0)),
        "persistence_mode": payload.get("search_summary", {}).get("persistence_mode"),
        "relevance_model": payload.get("search_summary", {}).get("relevance_model"),
        "retrieval_cluster_mode": payload.get("search_summary", {}).get("retrieval_cluster_mode"),
        "retrieval_cluster_count": int(
          payload.get("search_summary", {}).get("retrieval_cluster_count", 0)
        ),
        "top_cluster_label": payload.get("search_summary", {}).get("top_cluster_label"),
        "parsed_terms": list(payload.get("search_summary", {}).get("parsed_terms", ())),
        "parsed_phrases": list(payload.get("search_summary", {}).get("parsed_phrases", ())),
        "parsed_operators": list(payload.get("search_summary", {}).get("parsed_operators", ())),
        "semantic_concepts": list(payload.get("search_summary", {}).get("semantic_concepts", ())),
        "query_plan": list(payload.get("search_summary", {}).get("query_plan", ())),
      }
      if isinstance(payload.get("search_summary"), dict)
      else None
    ),
    "search_analytics": (
      {
        "query_id": payload.get("search_analytics", {}).get("query_id"),
        "recorded_at": (
          payload.get("search_analytics", {}).get("recorded_at").isoformat()
          if isinstance(payload.get("search_analytics", {}).get("recorded_at"), datetime)
          else payload.get("search_analytics", {}).get("recorded_at")
        ),
        "recent_query_count": int(payload.get("search_analytics", {}).get("recent_query_count", 0)),
        "feedback_count": int(payload.get("search_analytics", {}).get("feedback_count", 0)),
        "pending_feedback_count": int(
          payload.get("search_analytics", {}).get("pending_feedback_count", 0)
        ),
        "approved_feedback_count": int(
          payload.get("search_analytics", {}).get("approved_feedback_count", 0)
        ),
        "rejected_feedback_count": int(
          payload.get("search_analytics", {}).get("rejected_feedback_count", 0)
        ),
        "relevant_feedback_count": int(
          payload.get("search_analytics", {}).get("relevant_feedback_count", 0)
        ),
        "not_relevant_feedback_count": int(
          payload.get("search_analytics", {}).get("not_relevant_feedback_count", 0)
        ),
        "helpful_feedback_ratio_pct": int(
          payload.get("search_analytics", {}).get("helpful_feedback_ratio_pct", 0)
        ),
        "learned_relevance_active": bool(
          payload.get("search_analytics", {}).get("learned_relevance_active", False)
        ),
        "tuning_profile_version": payload.get("search_analytics", {}).get("tuning_profile_version"),
        "tuned_feature_count": int(payload.get("search_analytics", {}).get("tuned_feature_count", 0)),
        "channel_adjustments": {
          "lexical": int(
            payload.get("search_analytics", {}).get("channel_adjustments", {}).get("lexical", 0)
          ),
          "semantic": int(
            payload.get("search_analytics", {}).get("channel_adjustments", {}).get("semantic", 0)
          ),
          "operator": int(
            payload.get("search_analytics", {}).get("channel_adjustments", {}).get("operator", 0)
          ),
        },
        "top_field_adjustments": [
          {
            "field": entry.get("field"),
            "score": int(entry.get("score", 0)),
          }
          for entry in payload.get("search_analytics", {}).get("top_field_adjustments", ())
          if isinstance(entry, dict)
        ],
        "top_semantic_adjustments": [
          {
            "concept": entry.get("concept"),
            "score": int(entry.get("score", 0)),
          }
          for entry in payload.get("search_analytics", {}).get("top_semantic_adjustments", ())
          if isinstance(entry, dict)
        ],
        "top_operator_adjustments": [
          {
            "operator": entry.get("operator"),
            "score": int(entry.get("score", 0)),
          }
          for entry in payload.get("search_analytics", {}).get("top_operator_adjustments", ())
          if isinstance(entry, dict)
        ],
        "recent_queries": [
          {
            "query_id": entry.get("query_id"),
            "recorded_at": (
              entry.get("recorded_at").isoformat()
              if isinstance(entry.get("recorded_at"), datetime)
              else entry.get("recorded_at")
            ),
            "query": entry.get("query"),
            "matched_occurrences": int(entry.get("matched_occurrences", 0)),
            "top_score": int(entry.get("top_score", 0)),
            "relevance_model": entry.get("relevance_model"),
          }
          for entry in payload.get("search_analytics", {}).get("recent_queries", ())
          if isinstance(entry, dict)
        ],
        "recent_feedback": [
          {
            "feedback_id": entry.get("feedback_id"),
            "recorded_at": (
              entry.get("recorded_at").isoformat()
              if isinstance(entry.get("recorded_at"), datetime)
              else entry.get("recorded_at")
            ),
            "occurrence_id": entry.get("occurrence_id"),
            "signal": entry.get("signal"),
            "moderation_status": entry.get("moderation_status"),
            "matched_fields": list(entry.get("matched_fields", ())),
            "semantic_concepts": list(entry.get("semantic_concepts", ())),
            "operator_hits": list(entry.get("operator_hits", ())),
            "note": entry.get("note"),
            "moderation_note": entry.get("moderation_note"),
          }
          for entry in payload.get("search_analytics", {}).get("recent_feedback", ())
          if isinstance(entry, dict)
        ],
      }
      if isinstance(payload.get("search_analytics"), dict)
      else None
    ),
    "retrieval_clusters": [
      {
        "cluster_id": entry.get("cluster_id"),
        "rank": int(entry.get("rank", 0)),
        "label": entry.get("label"),
        "summary": entry.get("summary"),
        "occurrence_count": int(entry.get("occurrence_count", 0)),
        "top_score": int(entry.get("top_score", 0)),
        "average_score": int(entry.get("average_score", 0)),
        "average_similarity_pct": int(entry.get("average_similarity_pct", 0)),
        "semantic_concepts": list(entry.get("semantic_concepts", ())),
        "vector_terms": list(entry.get("vector_terms", ())),
        "categories": list(entry.get("categories", ())),
        "statuses": list(entry.get("statuses", ())),
        "narrative_facets": list(entry.get("narrative_facets", ())),
        "top_occurrence_id": entry.get("top_occurrence_id"),
        "top_occurrence_summary": entry.get("top_occurrence_summary"),
        "occurrence_ids": list(entry.get("occurrence_ids", ())),
      }
      for entry in payload.get("retrieval_clusters", ())
      if isinstance(entry, dict)
    ],
    "items": [
      {
        **serialize_operator_alert(
          item.get("alert") if isinstance(item, dict) else item
        ),
        "narrative": {
          "facet": (
            item.get("narrative", {}).get("facet")
            if isinstance(item, dict)
            else None
          ),
          "facet_flags": list(
            item.get("narrative", {}).get("facet_flags", ())
            if isinstance(item, dict)
            else ()
          ),
          "narrative_mode": (
            item.get("narrative", {}).get("narrative_mode")
            if isinstance(item, dict)
            else None
          ),
          "can_reconstruct_narrative": bool(
            item.get("narrative", {}).get("can_reconstruct_narrative", False)
            if isinstance(item, dict)
            else False
          ),
          "has_post_resolution_history": bool(
            item.get("narrative", {}).get("has_post_resolution_history", False)
            if isinstance(item, dict)
            else False
          ),
          "occurrence_record_count": int(
            item.get("narrative", {}).get("occurrence_record_count", 0)
            if isinstance(item, dict)
            else 0
          ),
          "post_resolution_record_count": int(
            item.get("narrative", {}).get("post_resolution_record_count", 0)
            if isinstance(item, dict)
            else 0
          ),
          "status_sequence": list(
            item.get("narrative", {}).get("status_sequence", ())
            if isinstance(item, dict)
            else ()
          ),
          "post_resolution_status_sequence": list(
            item.get("narrative", {}).get("post_resolution_status_sequence", ())
            if isinstance(item, dict)
            else ()
          ),
          "narrative_window_ended_at": (
            item.get("narrative", {}).get("narrative_window_ended_at").isoformat()
            if isinstance(item, dict)
            and isinstance(item.get("narrative", {}).get("narrative_window_ended_at"), datetime)
            else None
          ),
          "next_occurrence_detected_at": (
            item.get("narrative", {}).get("next_occurrence_detected_at").isoformat()
            if isinstance(item, dict)
            and isinstance(item.get("narrative", {}).get("next_occurrence_detected_at"), datetime)
            else None
          ),
        },
        "search_match": (
          {
            "score": int(item.get("search_match", {}).get("score", 0)),
            "matched_terms": list(item.get("search_match", {}).get("matched_terms", ())),
            "matched_phrases": list(item.get("search_match", {}).get("matched_phrases", ())),
            "matched_fields": list(item.get("search_match", {}).get("matched_fields", ())),
            "term_coverage_pct": int(item.get("search_match", {}).get("term_coverage_pct", 0)),
            "phrase_match": bool(item.get("search_match", {}).get("phrase_match", False)),
            "exact_match": bool(item.get("search_match", {}).get("exact_match", False)),
            "highlights": list(item.get("search_match", {}).get("highlights", ())),
            "semantic_concepts": list(item.get("search_match", {}).get("semantic_concepts", ())),
            "operator_hits": list(item.get("search_match", {}).get("operator_hits", ())),
            "lexical_score": int(item.get("search_match", {}).get("lexical_score", 0)),
            "semantic_score": int(item.get("search_match", {}).get("semantic_score", 0)),
            "operator_score": int(item.get("search_match", {}).get("operator_score", 0)),
            "learned_score": int(item.get("search_match", {}).get("learned_score", 0)),
            "feedback_signal_count": int(
              item.get("search_match", {}).get("feedback_signal_count", 0)
            ),
            "tuning_signals": list(item.get("search_match", {}).get("tuning_signals", ())),
            "relevance_model": item.get("search_match", {}).get("relevance_model"),
            "ranking_reason": item.get("search_match", {}).get("ranking_reason"),
          }
          if isinstance(item, dict) and isinstance(item.get("search_match"), dict)
          else None
        ),
        "retrieval_cluster": (
          {
            "cluster_id": item.get("retrieval_cluster", {}).get("cluster_id"),
            "rank": int(item.get("retrieval_cluster", {}).get("rank", 0)),
            "label": item.get("retrieval_cluster", {}).get("label"),
            "similarity_pct": int(item.get("retrieval_cluster", {}).get("similarity_pct", 0)),
            "semantic_concepts": list(
              item.get("retrieval_cluster", {}).get("semantic_concepts", ())
            ),
            "vector_terms": list(
              item.get("retrieval_cluster", {}).get("vector_terms", ())
            ),
          }
          if isinstance(item, dict) and isinstance(item.get("retrieval_cluster"), dict)
          else None
        ),
      }
      for item in items
    ],
    "total": int(payload.get("total", 0)),
    "returned": int(payload.get("returned", 0)),
    "has_more": bool(payload.get("has_more", False)),
    "next_offset": payload.get("next_offset"),
    "previous_offset": payload.get("previous_offset"),
  }

def serialize_provider_provenance_scheduled_report_list(
  records: tuple[ProviderProvenanceScheduledReportRecord, ...],
) -> dict[str, Any]:
  return {
    "items": [
      serialize_provider_provenance_scheduled_report_record(record)
      for record in records
    ],
    "total": len(records),
  }

def serialize_provider_provenance_scheduled_report_audit_record(
  record: ProviderProvenanceScheduledReportAuditRecord,
) -> dict[str, Any]:
  return {
    "audit_id": record.audit_id,
    "report_id": record.report_id,
    "action": record.action,
    "recorded_at": record.recorded_at.isoformat(),
    "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
    "source_tab_id": record.source_tab_id,
    "source_tab_label": record.source_tab_label,
    "export_job_id": record.export_job_id,
    "detail": record.detail,
  }

def serialize_provider_provenance_scheduled_report_history(
  record: ProviderProvenanceScheduledReportRecord,
  audit_records: tuple[ProviderProvenanceScheduledReportAuditRecord, ...],
) -> dict[str, Any]:
  return {
    "report": serialize_provider_provenance_scheduled_report_record(record),
    "history": [
      serialize_provider_provenance_scheduled_report_audit_record(audit_record)
      for audit_record in audit_records
    ],
  }

def serialize_provider_provenance_scheduled_report_run_result(
  payload: dict[str, Any],
) -> dict[str, Any]:
  report = payload.get("report")
  export_job = payload.get("export_job")
  if not isinstance(report, ProviderProvenanceScheduledReportRecord):
    raise ValueError("Provider provenance scheduled report result is missing the report record.")
  if not isinstance(export_job, ProviderProvenanceExportJobRecord):
    raise ValueError("Provider provenance scheduled report result is missing the export job record.")
  return {
    "report": serialize_provider_provenance_scheduled_report_record(report),
    "export_job": serialize_provider_provenance_export_job_record(export_job),
  }

def serialize_provider_provenance_scheduled_report_run_due_result(
  payload: dict[str, Any],
) -> dict[str, Any]:
  items = payload.get("items")
  return {
    "generated_at": payload.get("generated_at"),
    "due_before": payload.get("due_before"),
    "executed_count": int(payload.get("executed_count", 0)),
    "items": [
      serialize_provider_provenance_scheduled_report_run_result(item)
      for item in items
      if isinstance(item, dict)
    ],
  }

