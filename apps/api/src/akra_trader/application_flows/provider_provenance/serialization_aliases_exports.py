from __future__ import annotations

from copy import deepcopy
from datetime import UTC
from datetime import datetime
from typing import Any

from akra_trader.application_flows.provider_provenance.mixins import ProviderProvenanceCompatibilityMixin
from akra_trader.domain.models import *  # noqa: F403

__all__ = (
  "serialize_replay_intent_alias_record",
  "serialize_replay_intent_alias_audit_record",
  "serialize_replay_intent_alias_history",
  "serialize_replay_intent_alias_audit_list",
  "serialize_replay_intent_alias_audit_export_job_record",
  "serialize_replay_intent_alias_audit_export_job_audit_record",
  "serialize_replay_intent_alias_audit_export_job_list",
  "serialize_replay_intent_alias_audit_export_job_history",
  "serialize_provider_provenance_export_job_record",
  "serialize_provider_provenance_export_job_audit_record",
  "serialize_operator_incident_delivery_record",
  "serialize_provider_provenance_export_job_escalation_result",
  "serialize_provider_provenance_export_job_policy_result",
  "serialize_provider_provenance_export_job_list",
  "serialize_provider_provenance_export_job_history",
  "serialize_provider_provenance_analytics_preset_record",
  "serialize_provider_provenance_analytics_preset_list",
  "serialize_provider_provenance_dashboard_view_record",
  "serialize_provider_provenance_dashboard_view_list",
  "serialize_provider_provenance_scheduler_stitched_report_view_record",
  "serialize_provider_provenance_scheduler_stitched_report_view_list",
  "serialize_provider_provenance_scheduler_stitched_report_view_revision_record",
  "serialize_provider_provenance_scheduler_stitched_report_view_revision_list",
  "serialize_provider_provenance_scheduler_stitched_report_view_audit_record",
  "serialize_provider_provenance_scheduler_stitched_report_view_audit_list",
  "serialize_provider_provenance_scheduler_stitched_report_governance_registry_record",
  "serialize_provider_provenance_scheduler_stitched_report_governance_registry_list",
  "serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_record",
  "serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_list",
  "serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_record",
  "serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_list",
)

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
