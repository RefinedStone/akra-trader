from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from akra_trader.api_request_models_core import *
from akra_trader.api_request_models_search import *
from akra_trader.api_request_models_narrative import *
from akra_trader.api_request_models_scheduled import *

REQUEST_PAYLOAD_MODELS: dict[str, tuple[type[BaseModel], dict[str, Any]]] = {
  "replay_link_alias_create": (ReplayLinkAliasCreateRequest, {}),
  "replay_link_alias_revoke": (ReplayLinkAliasRevokeRequest, {}),
  "replay_link_audit_prune": (ReplayLinkAliasAuditPruneRequest, {}),
  "replay_link_audit_export_job_create": (ReplayLinkAliasAuditExportJobCreateRequest, {}),
  "replay_link_audit_export_job_prune": (ReplayLinkAliasAuditExportJobPruneRequest, {}),
  "market_data_lineage_evidence_retention_prune": (MarketDataLineageEvidenceRetentionPruneRequest, {}),
  "market_data_lineage_drill_evidence_pack_export": (
    MarketDataLineageDrillEvidencePackExportRequest,
    {},
  ),
  "operator_provider_provenance_export_job_create": (OperatorProviderProvenanceExportJobCreateRequest, {}),
  "operator_provider_provenance_export_job_policy": (OperatorProviderProvenanceExportJobPolicyRequest, {}),
  "operator_provider_provenance_export_job_approval": (OperatorProviderProvenanceExportJobApprovalRequest, {}),
  "operator_provider_provenance_export_job_escalate": (OperatorProviderProvenanceExportJobEscalateRequest, {}),
  "operator_provider_provenance_analytics_preset_create": (OperatorProviderProvenanceAnalyticsPresetCreateRequest, {}),
  "operator_provider_provenance_dashboard_view_create": (OperatorProviderProvenanceDashboardViewCreateRequest, {}),
  "operator_provider_provenance_scheduler_stitched_report_view_create": (
    OperatorProviderProvenanceSchedulerStitchedReportViewCreateRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_stitched_report_view_update": (
    OperatorProviderProvenanceSchedulerStitchedReportViewUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_stitched_report_view_delete": (
    OperatorProviderProvenanceSchedulerStitchedReportViewDeleteRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_stitched_report_view_bulk_governance": (
    OperatorProviderProvenanceSchedulerStitchedReportViewBulkGovernanceRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_stitched_report_view_revision_restore": (
    OperatorProviderProvenanceSchedulerStitchedReportViewRevisionRestoreRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_stitched_report_governance_registry_create": (
    OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryCreateRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_stitched_report_governance_registry_update": (
    OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_stitched_report_governance_registry_delete": (
    OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryDeleteRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore": (
    OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRestoreRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance": (
    OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernanceRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_template_create": (
    OperatorProviderProvenanceSchedulerNarrativeTemplateCreateRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_template_update": (
    OperatorProviderProvenanceSchedulerNarrativeTemplateUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_template_delete": (
    OperatorProviderProvenanceSchedulerNarrativeTemplateDeleteRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_template_bulk_governance": (
    OperatorProviderProvenanceSchedulerNarrativeTemplateBulkGovernanceRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_template_revision_restore": (
    OperatorProviderProvenanceSchedulerNarrativeTemplateRevisionRestoreRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_registry_create": (
    OperatorProviderProvenanceSchedulerNarrativeRegistryCreateRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_registry_update": (
    OperatorProviderProvenanceSchedulerNarrativeRegistryUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_registry_delete": (
    OperatorProviderProvenanceSchedulerNarrativeRegistryDeleteRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_registry_bulk_governance": (
    OperatorProviderProvenanceSchedulerNarrativeRegistryBulkGovernanceRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_template_create": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateCreateRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_template_update": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_template_delete": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDeleteRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRestoreRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogCreateRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDeleteRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkGovernanceRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRestoreRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyCaptureRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRestoreRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkGovernanceRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateCreateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateUpdateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDeleteRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkGovernanceRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRestoreRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateApplyRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateStageRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage": (
    OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBatchStageRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageRequest,
    {},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_plan_create": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePlanCreateRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_plan_approve": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePlanApprovalRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_plan_apply": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePlanApplyRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_plan_batch_action": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePlanBatchActionRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_governance_plan_rollback": (
    OperatorProviderProvenanceSchedulerNarrativeGovernancePlanRollbackRequest,
    {"exclude_unset": True},
  ),
  "operator_provider_provenance_scheduler_narrative_registry_revision_restore": (
    OperatorProviderProvenanceSchedulerNarrativeRegistryRevisionRestoreRequest,
    {},
  ),
  "operator_provider_provenance_scheduled_report_create": (OperatorProviderProvenanceScheduledReportCreateRequest, {}),
  "operator_provider_provenance_scheduled_report_run": (OperatorProviderProvenanceScheduledReportRunRequest, {}),
  "operator_provider_provenance_scheduled_report_run_due": (OperatorProviderProvenanceScheduledReportRunDueRequest, {}),
  "preset_create": (ExperimentPresetRequest, {}),
  "preset_update": (ExperimentPresetUpdateRequest, {"exclude_unset": True}),
  "preset_revision_restore": (ExperimentPresetRevisionRestoreRequest, {}),
  "preset_lifecycle_action": (ExperimentPresetLifecycleActionRequest, {}),
  "strategy_register": (StrategyRegistrationRequest, {}),
  "backtest_launch": (BacktestRequest, {}),
  "sandbox_launch": (SandboxRunRequest, {}),
  "paper_launch": (SandboxRunRequest, {}),
  "live_launch": (LiveRunRequest, {}),
  "external_incident_sync": (ExternalIncidentSyncRequest, {}),
  "guarded_live_action": (GuardedLiveActionRequest, {}),
  "guarded_live_order_replace": (GuardedLiveOrderReplaceRequest, {}),
}
