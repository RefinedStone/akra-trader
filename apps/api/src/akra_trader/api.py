from __future__ import annotations

from datetime import UTC
from datetime import datetime
import inspect
import json
from numbers import Number
import re
from types import UnionType
from typing import Any
from typing import Union
from typing import get_args
from typing import get_origin

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from pydantic import BaseModel
from pydantic import Field

from akra_trader.application import list_standalone_surface_runtime_bindings
from akra_trader.application import StandaloneSurfaceFilterCondition
from akra_trader.application import TradingApplication
from akra_trader.application import execute_standalone_surface_binding
from akra_trader.application import serialize_collection_path_spec
from akra_trader.application import serialize_standalone_filter_param_spec
from akra_trader.application import StandaloneSurfaceFilterParamSpec
from akra_trader.application import StandaloneSurfaceSortTerm
from akra_trader.application import StandaloneSurfaceRuntimeBinding
from akra_trader.application import StandaloneSurfaceFilterExpressionNode
from akra_trader.application import StandaloneSurfaceCollectionPathSpec
from akra_trader.bootstrap import Container


class StrategyRegistrationRequest(BaseModel):
  strategy_id: str
  module_path: str
  class_name: str


class ExperimentPresetRequest(BaseModel):
  name: str
  preset_id: str | None = None
  description: str = ""
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] = Field(default_factory=list)
  parameters: dict[str, Any] = Field(default_factory=dict)
  benchmark_family: str | None = None


class ExperimentPresetLifecycleActionRequest(BaseModel):
  action: str
  actor: str = "operator"
  reason: str = "manual_preset_lifecycle_action"


class ExperimentPresetUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] | None = None
  parameters: dict[str, Any] | None = None
  benchmark_family: str | None = None
  actor: str = "operator"
  reason: str = "manual_preset_edit"


class ExperimentPresetRevisionRestoreRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_preset_revision_restore"


class BacktestRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  parameters: dict[str, Any] = Field(default_factory=dict)
  start_at: datetime | None = None
  end_at: datetime | None = None
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class SandboxRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class LiveRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  operator_reason: str = "guarded_live_launch"
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class GuardedLiveActionRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_operator_action"


class GuardedLiveOrderReplaceRequest(GuardedLiveActionRequest):
  price: float = Field(gt=0)
  quantity: float | None = Field(default=None, gt=0)


class ExternalIncidentSyncRequest(BaseModel):
  provider: str
  event_kind: str
  actor: str = "external"
  detail: str = "external_incident_sync"
  alert_id: str | None = None
  external_reference: str | None = None
  workflow_reference: str | None = None
  occurred_at: datetime | None = None
  escalation_level: int | None = Field(default=None, ge=1)
  payload: dict[str, Any] = Field(default_factory=dict)


class ReplayLinkAliasCreateRequest(BaseModel):
  template_key: str
  template_label: str | None = None
  intent: dict[str, Any]
  redaction_policy: str = "full"
  retention_policy: str = "30d"
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class ReplayLinkAliasRevokeRequest(BaseModel):
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class ReplayLinkAliasAuditPruneRequest(BaseModel):
  prune_mode: str = "expired"
  alias_id: str | None = None
  template_key: str | None = None
  action: str | None = None
  retention_policy: str | None = None
  source_tab_id: str | None = None
  search: str | None = None
  recorded_before: datetime | None = None
  include_manual: bool = False


class ReplayLinkAliasAuditExportJobCreateRequest(BaseModel):
  format: str = "json"
  alias_id: str | None = None
  template_key: str | None = None
  action: str | None = None
  retention_policy: str | None = None
  source_tab_id: str | None = None
  search: str | None = None
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None


class ReplayLinkAliasAuditExportJobPruneRequest(BaseModel):
  prune_mode: str = "expired"
  template_key: str | None = None
  format: str | None = None
  status: str | None = None
  requested_by_tab_id: str | None = None
  search: str | None = None
  created_before: datetime | None = None


class OperatorProviderProvenanceExportJobCreateRequest(BaseModel):
  content: str
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None


class OperatorProviderProvenanceExportJobEscalateRequest(BaseModel):
  actor: str = "operator"
  reason: str = "scheduler_health_review"
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  delivery_targets: list[str] = Field(default_factory=list)


class OperatorProviderProvenanceExportJobPolicyRequest(BaseModel):
  actor: str = "operator"
  routing_policy_id: str = "default"
  approval_policy_id: str = "auto"
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  delivery_targets: list[str] = Field(default_factory=list)


class OperatorProviderProvenanceExportJobApprovalRequest(BaseModel):
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerHistoricalExportRequest(BaseModel):
  alert_category: str
  detected_at: datetime
  resolved_at: datetime | None = None
  narrative_mode: str = "matched_status"
  format: str = "json"
  history_limit: int = 25
  drilldown_history_limit: int = 24


class OperatorProviderProvenanceAnalyticsPresetCreateRequest(BaseModel):
  name: str
  description: str = ""
  query: dict[str, Any] = Field(default_factory=dict)
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceDashboardViewCreateRequest(BaseModel):
  name: str
  description: str = ""
  query: dict[str, Any] = Field(default_factory=dict)
  layout: dict[str, Any] = Field(default_factory=dict)
  preset_id: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeTemplateCreateRequest(BaseModel):
  name: str
  description: str = ""
  query: dict[str, Any] = Field(default_factory=dict)
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeTemplateUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  query: dict[str, Any] | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_template_updated"


class OperatorProviderProvenanceSchedulerNarrativeTemplateDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_template_deleted"


class OperatorProviderProvenanceSchedulerNarrativeTemplateBulkGovernanceRequest(BaseModel):
  action: str
  template_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None


class OperatorProviderProvenanceSchedulerNarrativeTemplateRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_template_revision_restored"


class OperatorProviderProvenanceSchedulerNarrativeRegistryCreateRequest(BaseModel):
  name: str
  description: str = ""
  query: dict[str, Any] = Field(default_factory=dict)
  layout: dict[str, Any] = Field(default_factory=dict)
  template_id: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeRegistryUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  query: dict[str, Any] | None = None
  layout: dict[str, Any] | None = None
  template_id: str | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_registry_updated"


class OperatorProviderProvenanceSchedulerNarrativeRegistryDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_registry_deleted"


class OperatorProviderProvenanceSchedulerNarrativeRegistryBulkGovernanceRequest(BaseModel):
  action: str
  registry_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  layout_patch: dict[str, Any] | None = None
  template_id: str | None = None
  clear_template_link: bool = False


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateCreateRequest(BaseModel):
  name: str
  description: str = ""
  item_type_scope: str = "any"
  action_scope: str = "any"
  approval_lane: str = "general"
  approval_priority: str = "normal"
  guidance: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  item_type_scope: str | None = None
  action_scope: str | None = None
  approval_lane: str | None = None
  approval_priority: str | None = None
  guidance: str | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_template_updated"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_template_deleted"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_template_revision_restored"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogCreateRequest(BaseModel):
  name: str
  description: str = ""
  policy_template_ids: list[str] = Field(default_factory=list)
  default_policy_template_id: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  policy_template_ids: list[str] | None = None
  default_policy_template_id: str | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_catalog_updated"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_catalog_deleted"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkGovernanceRequest(BaseModel):
  action: str
  catalog_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_policy_template_id: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_catalog_revision_restored"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRequest(BaseModel):
  item_type: str
  action: str = "update"
  item_ids: list[str] = Field(default_factory=list)
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  layout_patch: dict[str, Any] | None = None
  template_id: str | None = None
  clear_template_link: bool = False


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyCaptureRequest(BaseModel):
  hierarchy_steps: list[OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRequest] = (
    Field(default_factory=list)
  )
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_captured"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_catalog_staged"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePlanCreateRequest(BaseModel):
  item_type: str
  item_ids: list[str] = Field(default_factory=list)
  action: str
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  layout_patch: dict[str, Any] | None = None
  template_id: str | None = None
  clear_template_link: bool = False
  policy_template_id: str | None = None
  policy_catalog_id: str | None = None
  approval_lane: str | None = None
  approval_priority: str | None = None
  hierarchy_key: str | None = None
  hierarchy_name: str | None = None
  hierarchy_position: int | None = None
  hierarchy_total: int | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernancePlanApprovalRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  note: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernancePlanApplyRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernancePlanBatchActionRequest(BaseModel):
  action: str
  plan_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  note: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernancePlanRollbackRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  note: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeRegistryRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_registry_revision_restored"


class OperatorProviderProvenanceScheduledReportCreateRequest(BaseModel):
  name: str
  description: str = ""
  query: dict[str, Any] = Field(default_factory=dict)
  layout: dict[str, Any] = Field(default_factory=dict)
  preset_id: str | None = None
  view_id: str | None = None
  cadence: str = "daily"
  status: str = "scheduled"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceScheduledReportRunRequest(BaseModel):
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceScheduledReportRunDueRequest(BaseModel):
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  due_before: datetime | None = None
  limit: int = Field(default=25, ge=1, le=100)


REQUEST_PAYLOAD_MODELS: dict[str, tuple[type[BaseModel], dict[str, Any]]] = {
  "replay_link_alias_create": (ReplayLinkAliasCreateRequest, {}),
  "replay_link_alias_revoke": (ReplayLinkAliasRevokeRequest, {}),
  "replay_link_audit_prune": (ReplayLinkAliasAuditPruneRequest, {}),
  "replay_link_audit_export_job_create": (ReplayLinkAliasAuditExportJobCreateRequest, {}),
  "replay_link_audit_export_job_prune": (ReplayLinkAliasAuditExportJobPruneRequest, {}),
  "operator_provider_provenance_export_job_create": (OperatorProviderProvenanceExportJobCreateRequest, {}),
  "operator_provider_provenance_export_job_policy": (OperatorProviderProvenanceExportJobPolicyRequest, {}),
  "operator_provider_provenance_export_job_approval": (OperatorProviderProvenanceExportJobApprovalRequest, {}),
  "operator_provider_provenance_export_job_escalate": (OperatorProviderProvenanceExportJobEscalateRequest, {}),
  "operator_provider_provenance_analytics_preset_create": (OperatorProviderProvenanceAnalyticsPresetCreateRequest, {}),
  "operator_provider_provenance_dashboard_view_create": (OperatorProviderProvenanceDashboardViewCreateRequest, {}),
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


def _build_header_alias(header_key: str) -> str:
  return "-".join(part.capitalize() for part in header_key.split("_"))


def _build_query_default(spec: StandaloneSurfaceFilterParamSpec) -> Any:
  kwargs: dict[str, Any] = {}
  if spec.constraints is not None:
    constraint_values = (
      ("min_length", spec.constraints.min_length),
      ("max_length", spec.constraints.max_length),
      ("ge", spec.constraints.ge),
      ("le", spec.constraints.le),
      ("pattern", spec.constraints.pattern),
    )
    for key, value in constraint_values:
      if value is not None:
        kwargs[key] = value
  if spec.openapi is not None:
    openapi_values = (
      ("alias", spec.openapi.alias),
      ("title", spec.openapi.title),
      ("description", spec.openapi.description),
    )
    for key, value in openapi_values:
      if value is not None:
        kwargs[key] = value
    if spec.openapi.examples:
      kwargs["examples"] = list(spec.openapi.examples)
    if spec.openapi.deprecated:
      kwargs["deprecated"] = True
  if spec.default_factory is not None:
    return Query(default_factory=spec.default_factory, **kwargs)
  return Query(default=spec.default, **kwargs)


def _build_sort_query_default(binding: StandaloneSurfaceRuntimeBinding) -> Any:
  examples = [
    f"{field.key}:{field.default_direction}"
    for field in binding.sort_field_specs
  ]
  return Query(
    default_factory=list,
    title="Sort",
    description="Sort fields in `<field>` or `<field>:<direction>` format.",
    examples=examples,
  )


def _build_filter_expression_query_default() -> Any:
  return Query(
    default=None,
    title="Filter expression",
    description=(
      "JSON boolean expression tree using `logic`, `conditions`, `children`, and optional `negated` fields."
    ),
    examples=[
      (
        '{"logic":"or","children":['
        '{"logic":"and","conditions":[{"key":"total_return_pct","operator":"ge","value":20},'
        '{"key":"trade_count","operator":"ge","value":2}]},'
        '{"logic":"and","conditions":[{"key":"trade_count","operator":"ge","value":5},'
        '{"key":"total_return_pct","operator":"ge","value":15}]}]}'
      ),
    ],
  )


def _build_route_openapi_extra(binding: StandaloneSurfaceRuntimeBinding) -> dict[str, Any] | None:
  if not binding.filter_param_specs and not binding.sort_field_specs:
    return None
  return {
    "x-akra-query-schema": {
      "grouped_filters": {
        "param_pattern": "group__<group_key>__<filter_key>__<operator>",
        "semantics": "Ungrouped filters are ANDed together. Grouped filters are ANDed within a group and ORed across groups.",
      },
      "expression_trees": {
        "param": "filter_expr",
        "format": "json",
        "supports_negation": True,
        "logic_values": ["and", "or"],
        "predicate_refs": {
          "registry_field": "predicates",
          "reference_field": "predicate_ref",
        },
        "predicate_templates": {
          "registry_field": "predicate_templates",
          "template_field": "template",
          "parameters_field": "parameters",
          "bindings_field": "bindings",
          "binding_reference_shape": {
            "binding": "<parameter_name>",
          },
        },
        "quantified_conditions": {
          "field": "quantifier",
          "values": ["any", "all", "none"],
          "semantics": "Applies the condition across list-valued candidates.",
        },
        "collection_nodes": {
          "field": "collection",
          "shape": {
            "path": "<collection path>",
            "path_template": "<collection path template>",
            "bindings": {
              "<parameter_key>": "<value or binding reference>",
            },
            "quantifier": "any|all|none",
          },
          "semantics": "Evaluates the node against collection elements, flattening nested collection-of-collection paths, and folds the results with the declared quantifier. Parameterized collection schemas can bind a declared `path_template` through `bindings`.",
        },
        "collection_schemas": [
          serialize_collection_path_spec(binding, spec)
          for spec in binding.collection_path_specs
        ],
        "condition_shape": {
          "key": "<filter_key>",
          "operator": "<operator>",
          "value": "<typed value>",
          "quantifier": "any|all|none",
        },
        "node_shape": {
          "logic": "and|or",
          "conditions": ["<condition>", "..."],
          "children": ["<node>", "..."],
          "negated": "boolean",
          "predicate_ref": "<named predicate>",
          "collection": {
            "path": "<collection path>",
            "quantifier": "any|all|none",
          },
        },
      },
      "filters": [
        serialize_standalone_filter_param_spec(spec)
        for spec in binding.filter_param_specs
      ],
      "sort_fields": [
        {
          "key": field.key,
          "label": field.label,
          "description": field.description,
          "default_direction": field.default_direction,
          "value_type": field.value_type,
          "value_path": list(field.value_path),
        }
        for field in binding.sort_field_specs
      ],
    }
  }


def _describe_filter_value_type(annotation: Any) -> str:
  resolved_annotation = _resolve_filter_scalar_annotation(annotation)
  origin = get_origin(annotation)
  if origin in {list, tuple}:
    return f"list[{_describe_filter_value_type(resolved_annotation)}]"
  if resolved_annotation is int:
    return "integer"
  if resolved_annotation is float:
    return "number"
  if resolved_annotation is datetime:
    return "datetime"
  return "string"


def _resolve_filter_scalar_annotation(annotation: Any) -> Any:
  origin = get_origin(annotation)
  if origin in {list, tuple}:
    args = tuple(arg for arg in get_args(annotation) if arg is not Ellipsis)
    if args:
      return _resolve_filter_scalar_annotation(args[0])
  if origin in {UnionType, Union}:
    args = tuple(arg for arg in get_args(annotation) if arg is not type(None))
    if len(args) == 1:
      return _resolve_filter_scalar_annotation(args[0])
  return annotation


def _coerce_filter_scalar_value(annotation: Any, raw_value: str) -> Any:
  resolved_annotation = _resolve_filter_scalar_annotation(annotation)
  if raw_value is None:
    return None
  if resolved_annotation is int:
    if isinstance(raw_value, bool):
      raise ValueError("Boolean values are not valid integers for this filter.")
    return int(raw_value)
  if resolved_annotation is float:
    if isinstance(raw_value, bool):
      raise ValueError("Boolean values are not valid numbers for this filter.")
    return float(raw_value)
  if resolved_annotation is datetime:
    if isinstance(raw_value, datetime):
      parsed = raw_value
    else:
      normalized_value = str(raw_value).replace("Z", "+00:00")
      parsed = datetime.fromisoformat(normalized_value)
    if parsed.tzinfo is None:
      return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
  if isinstance(raw_value, str):
    return raw_value
  return str(raw_value)


def _validate_filter_query_value(
  spec: StandaloneSurfaceFilterParamSpec,
  value: Any,
) -> None:
  if value is None or spec.constraints is None:
    return
  if isinstance(value, (list, tuple, set)):
    for item in value:
      _validate_filter_query_value(spec, item)
    return
  if isinstance(value, str):
    if spec.constraints.min_length is not None and len(value) < spec.constraints.min_length:
      raise ValueError(f"Filter value for {spec.key} is shorter than {spec.constraints.min_length}.")
    if spec.constraints.max_length is not None and len(value) > spec.constraints.max_length:
      raise ValueError(f"Filter value for {spec.key} is longer than {spec.constraints.max_length}.")
    if spec.constraints.pattern is not None and re.fullmatch(spec.constraints.pattern, value) is None:
      raise ValueError(f"Filter value for {spec.key} does not match the required pattern.")
    return
  if isinstance(value, Number) and not isinstance(value, bool):
    if spec.constraints.ge is not None and value < spec.constraints.ge:
      raise ValueError(f"Filter value for {spec.key} must be >= {spec.constraints.ge}.")
    if spec.constraints.le is not None and value > spec.constraints.le:
      raise ValueError(f"Filter value for {spec.key} must be <= {spec.constraints.le}.")


def _coerce_filter_query_values(
  spec: StandaloneSurfaceFilterParamSpec,
  *,
  value_shape: str,
  values: list[str],
) -> Any:
  if value_shape == "list":
    coerced_values = [
      _coerce_filter_scalar_value(spec.annotation, raw_value)
      for raw_value in values
    ]
    _validate_filter_query_value(spec, coerced_values)
    return coerced_values
  if not values:
    return None
  coerced_value = _coerce_filter_scalar_value(spec.annotation, values[-1])
  _validate_filter_query_value(spec, coerced_value)
  return coerced_value


def _coerce_filter_expression_value(
  spec: StandaloneSurfaceFilterParamSpec,
  *,
  value_shape: str,
  raw_value: Any,
) -> Any:
  if value_shape == "list":
    raw_values = list(raw_value) if isinstance(raw_value, (list, tuple, set)) else [raw_value]
    coerced_values = [
      _coerce_filter_scalar_value(spec.annotation, value)
      for value in raw_values
    ]
    _validate_filter_query_value(spec, coerced_values)
    return coerced_values
  coerced_value = _coerce_filter_scalar_value(spec.annotation, raw_value)
  _validate_filter_query_value(spec, coerced_value)
  return coerced_value


def _parse_runtime_filter_expression_binding_reference(raw_value: Any) -> str | None:
  if not isinstance(raw_value, dict):
    return None
  if tuple(raw_value.keys()) != ("binding",):
    return None
  binding_key = raw_value.get("binding")
  if not isinstance(binding_key, str) or not binding_key:
    raise ValueError("Filter expression binding references must declare a non-empty `binding` key.")
  return binding_key


def _resolve_runtime_filter_expression_binding_value(
  raw_value: Any,
  *,
  active_template_bindings: dict[str, Any] | None = None,
  active_template_parameter_names: set[str] | None = None,
) -> Any:
  if isinstance(raw_value, list):
    return [
      _resolve_runtime_filter_expression_binding_value(
        item,
        active_template_bindings=active_template_bindings,
        active_template_parameter_names=active_template_parameter_names,
      )
      for item in raw_value
    ]
  if isinstance(raw_value, tuple):
    return tuple(
      _resolve_runtime_filter_expression_binding_value(
        item,
        active_template_bindings=active_template_bindings,
        active_template_parameter_names=active_template_parameter_names,
      )
      for item in raw_value
    )
  binding_key = _parse_runtime_filter_expression_binding_reference(raw_value)
  if binding_key is None:
    return raw_value
  if active_template_parameter_names is None or binding_key not in active_template_parameter_names:
    raise ValueError(f"Unknown filter expression binding reference: {binding_key}")
  if active_template_bindings is None or binding_key not in active_template_bindings:
    raise ValueError(f"Missing bound value for filter expression parameter: {binding_key}")
  return active_template_bindings[binding_key]


def _parse_runtime_filter_expression_condition(
  raw_condition: Any,
  *,
  filter_specs_by_key: dict[str, StandaloneSurfaceFilterParamSpec],
  allowed_filter_keys: set[str] | None = None,
  active_template_bindings: dict[str, Any] | None = None,
  active_template_parameter_names: set[str] | None = None,
) -> StandaloneSurfaceFilterCondition:
  if not isinstance(raw_condition, dict):
    raise ValueError("Filter expression conditions must be objects.")
  filter_key = raw_condition.get("key")
  if not isinstance(filter_key, str) or not filter_key:
    raise ValueError("Filter expression conditions must declare a filter key.")
  if allowed_filter_keys is not None and filter_key not in allowed_filter_keys:
    raise ValueError(f"Filter key {filter_key} is not allowed in this collection expression scope.")
  spec = filter_specs_by_key.get(filter_key)
  if spec is None:
    raise ValueError(f"Unsupported filter key in filter expression: {filter_key}")
  operator_key = raw_condition.get("operator")
  if not isinstance(operator_key, str) or not operator_key:
    if spec.operators:
      operator_key = spec.operators[0].key
    else:
      operator_key = "eq"
  operator_specs = {
    operator.key: operator
    for operator in spec.operators
  }
  operator_spec = operator_specs.get(operator_key)
  if operator_spec is None:
    raise ValueError(f"Unsupported filter operator for {filter_key}: {operator_key}")
  if "value" not in raw_condition:
    raise ValueError(f"Filter expression conditions must declare a value for {filter_key}.")
  quantifier = raw_condition.get("quantifier")
  if quantifier is not None:
    if not isinstance(quantifier, str) or quantifier not in {"any", "all", "none"}:
      raise ValueError("Filter expression quantifier must be one of `any`, `all`, or `none`.")
  return StandaloneSurfaceFilterCondition(
    key=filter_key,
    operator=operator_key,
    value=_coerce_filter_expression_value(
      spec,
      value_shape=operator_spec.value_shape,
      raw_value=_resolve_runtime_filter_expression_binding_value(
        raw_condition["value"],
        active_template_bindings=active_template_bindings,
        active_template_parameter_names=active_template_parameter_names,
      ),
    ),
    quantifier=quantifier,
  )


def _normalize_collection_schema_path(raw_path: Any) -> tuple[str, ...]:
  if isinstance(raw_path, str):
    return tuple(
      segment
      for segment in raw_path.split(".")
      if segment
    )
  if isinstance(raw_path, list) and all(isinstance(segment, str) and segment for segment in raw_path):
    return tuple(raw_path)
  raise ValueError("Filter expression collection paths must be a dotted string or list of path segments.")


def _parse_runtime_filter_expression_template_parameters(
  raw_parameters: Any,
) -> tuple[set[str], dict[str, Any]]:
  if raw_parameters is None:
    return (set(), {})
  if isinstance(raw_parameters, list):
    if not all(isinstance(parameter_key, str) and parameter_key for parameter_key in raw_parameters):
      raise ValueError("Filter expression predicate template parameters must be non-empty strings.")
    return (set(raw_parameters), {})
  if isinstance(raw_parameters, dict):
    parameter_names: set[str] = set()
    parameter_defaults: dict[str, Any] = {}
    for parameter_key, raw_parameter in raw_parameters.items():
      if not isinstance(parameter_key, str) or not parameter_key:
        raise ValueError("Filter expression predicate template parameter keys must be non-empty strings.")
      parameter_names.add(parameter_key)
      if isinstance(raw_parameter, dict) and "default" in raw_parameter:
        parameter_defaults[parameter_key] = raw_parameter["default"]
    return (parameter_names, parameter_defaults)
  raise ValueError("Filter expression predicate template parameters must be a list or object map.")


def _resolve_collection_template_bindings(
  collection_spec: StandaloneSurfaceCollectionPathSpec,
  *,
  raw_bindings: Any,
  active_template_bindings: dict[str, Any] | None = None,
  active_template_parameter_names: set[str] | None = None,
) -> tuple[str, ...]:
  if not isinstance(raw_bindings, dict):
    raise ValueError("Filter expression collection template bindings must be an object map.")
  allowed_keys = {
    parameter.key
    for parameter in collection_spec.parameters
  }
  if set(raw_bindings) - allowed_keys:
    unsupported_keys = ", ".join(sorted(set(raw_bindings) - allowed_keys))
    raise ValueError(f"Unsupported filter expression collection binding keys: {unsupported_keys}")
  resolved_bindings: dict[str, str] = {}
  for parameter in collection_spec.parameters:
    if parameter.key not in raw_bindings:
      raise ValueError(
        f"Missing filter expression collection binding for parameter `{parameter.key}`."
      )
    resolved_value = _resolve_runtime_filter_expression_binding_value(
      raw_bindings[parameter.key],
      active_template_bindings=active_template_bindings,
      active_template_parameter_names=active_template_parameter_names,
    )
    if not isinstance(resolved_value, str) or not resolved_value:
      raise ValueError(
        f"Filter expression collection binding `{parameter.key}` must resolve to a non-empty string."
      )
    resolved_bindings[parameter.key] = resolved_value
  resolved_path: list[str] = []
  for segment in collection_spec.path_template or collection_spec.path:
    if segment.startswith("{") and segment.endswith("}") and len(segment) > 2:
      parameter_key = segment[1:-1]
      if parameter_key not in resolved_bindings:
        raise ValueError(
          f"Missing filter expression collection binding for template parameter `{parameter_key}`."
        )
      resolved_path.append(resolved_bindings[parameter_key])
      continue
    resolved_path.append(segment)
  return tuple(resolved_path)


def _resolve_collection_path_schema(
  collection_path: tuple[str, ...],
  *,
  collection_specs_by_path: dict[tuple[str, ...], StandaloneSurfaceCollectionPathSpec],
) -> StandaloneSurfaceCollectionPathSpec:
  collection_spec = collection_specs_by_path.get(collection_path)
  if collection_spec is None:
    raise ValueError(
      "Unsupported filter expression collection path: "
      + ".".join(collection_path)
    )
  return collection_spec


def _resolve_collection_template_schema(
  collection_path_template: tuple[str, ...],
  *,
  collection_specs_by_template: dict[tuple[str, ...], StandaloneSurfaceCollectionPathSpec],
) -> StandaloneSurfaceCollectionPathSpec:
  collection_spec = collection_specs_by_template.get(collection_path_template)
  if collection_spec is None:
    raise ValueError(
      "Unsupported filter expression collection path template: "
      + ".".join(collection_path_template)
    )
  return collection_spec


def _parse_runtime_filter_expression_node(
  raw_node: Any,
  *,
  filter_specs_by_key: dict[str, StandaloneSurfaceFilterParamSpec],
  predicate_registry: dict[str, Any],
  predicate_template_registry: dict[str, Any],
  collection_specs_by_path: dict[tuple[str, ...], StandaloneSurfaceCollectionPathSpec],
  collection_specs_by_template: dict[tuple[str, ...], StandaloneSurfaceCollectionPathSpec],
  active_predicate_refs: tuple[str, ...] = (),
  active_collection_filter_keys: set[str] | None = None,
  active_template_bindings: dict[str, Any] | None = None,
  active_template_parameter_names: set[str] | None = None,
) -> StandaloneSurfaceFilterExpressionNode:
  if not isinstance(raw_node, dict):
    raise ValueError("Filter expression nodes must be objects.")
  predicate_ref = raw_node.get("predicate_ref")
  if predicate_ref is not None:
    if not isinstance(predicate_ref, str) or not predicate_ref:
      raise ValueError("Filter expression predicate references must be non-empty strings.")
    if predicate_ref in active_predicate_refs:
      raise ValueError(f"Cyclic filter predicate reference detected for {predicate_ref}.")
    referenced_node = predicate_registry.get(predicate_ref)
    if referenced_node is None:
      raw_template = predicate_template_registry.get(predicate_ref)
      if raw_template is None:
        raise ValueError(f"Unknown filter predicate reference: {predicate_ref}")
      if not isinstance(raw_template, dict):
        raise ValueError("Filter expression predicate templates must be object definitions.")
      parameter_names, parameter_defaults = _parse_runtime_filter_expression_template_parameters(
        raw_template.get("parameters"),
      )
      raw_template_bindings = raw_node.get("bindings")
      if raw_template_bindings is not None and not isinstance(raw_template_bindings, dict):
        raise ValueError("Filter expression predicate template bindings must be an object map.")
      resolved_template_bindings: dict[str, Any] = {}
      for parameter_name in parameter_names:
        if isinstance(raw_template_bindings, dict) and parameter_name in raw_template_bindings:
          resolved_template_bindings[parameter_name] = _resolve_runtime_filter_expression_binding_value(
            raw_template_bindings[parameter_name],
            active_template_bindings=active_template_bindings,
            active_template_parameter_names=active_template_parameter_names,
          )
          continue
        if parameter_name in parameter_defaults:
          resolved_template_bindings[parameter_name] = parameter_defaults[parameter_name]
          continue
        raise ValueError(
          f"Missing filter expression predicate template binding for `{parameter_name}`."
        )
      if isinstance(raw_template_bindings, dict):
        unsupported_binding_keys = set(raw_template_bindings) - parameter_names
        if unsupported_binding_keys:
          unsupported_keys = ", ".join(sorted(unsupported_binding_keys))
          raise ValueError(
            f"Unsupported filter expression predicate template binding keys: {unsupported_keys}"
          )
      referenced_node = raw_template.get("template")
      if referenced_node is None:
        raise ValueError("Filter expression predicate templates must declare a `template` node.")
      resolved = _parse_runtime_filter_expression_node(
        referenced_node,
        filter_specs_by_key=filter_specs_by_key,
        predicate_registry=predicate_registry,
        predicate_template_registry=predicate_template_registry,
        collection_specs_by_path=collection_specs_by_path,
        collection_specs_by_template=collection_specs_by_template,
        active_predicate_refs=(*active_predicate_refs, predicate_ref),
        active_collection_filter_keys=active_collection_filter_keys,
        active_template_bindings=resolved_template_bindings,
        active_template_parameter_names=parameter_names,
      )
      if bool(raw_node.get("negated", False)):
        return StandaloneSurfaceFilterExpressionNode(
          logic=resolved.logic,
          conditions=resolved.conditions,
          children=resolved.children,
          negated=not resolved.negated,
          collection_path=resolved.collection_path,
          collection_quantifier=resolved.collection_quantifier,
          collection_path_strict=resolved.collection_path_strict,
        )
      return resolved
    if "bindings" in raw_node:
      raise ValueError("Filter expression predicate bindings are only supported for predicate templates.")
    resolved = _parse_runtime_filter_expression_node(
      referenced_node,
      filter_specs_by_key=filter_specs_by_key,
      predicate_registry=predicate_registry,
      predicate_template_registry=predicate_template_registry,
      collection_specs_by_path=collection_specs_by_path,
      collection_specs_by_template=collection_specs_by_template,
      active_predicate_refs=(*active_predicate_refs, predicate_ref),
      active_collection_filter_keys=active_collection_filter_keys,
      active_template_bindings=active_template_bindings,
      active_template_parameter_names=active_template_parameter_names,
    )
    if bool(raw_node.get("negated", False)):
      return StandaloneSurfaceFilterExpressionNode(
        logic=resolved.logic,
        conditions=resolved.conditions,
        children=resolved.children,
        negated=not resolved.negated,
        collection_path=resolved.collection_path,
        collection_quantifier=resolved.collection_quantifier,
        collection_path_strict=resolved.collection_path_strict,
      )
    return resolved
  logic = raw_node.get("logic", "and")
  if not isinstance(logic, str) or logic.lower() not in {"and", "or"}:
    raise ValueError("Filter expression logic must be either `and` or `or`.")
  collection_path: tuple[str, ...] = ()
  collection_quantifier: str | None = None
  collection_path_strict = False
  node_allowed_filter_keys = active_collection_filter_keys
  raw_collection = raw_node.get("collection")
  if raw_collection is not None:
    if not isinstance(raw_collection, dict):
      raise ValueError("Filter expression collection nodes must declare an object `collection` field.")
    if raw_collection.get("path") is not None and raw_collection.get("path_template") is not None:
      raise ValueError("Filter expression collection nodes must not declare both `path` and `path_template`.")
    if raw_collection.get("path_template") is not None:
      collection_path_template = _normalize_collection_schema_path(raw_collection.get("path_template"))
      collection_spec = _resolve_collection_template_schema(
        collection_path_template,
        collection_specs_by_template=collection_specs_by_template,
      )
      collection_path = _resolve_collection_template_bindings(
        collection_spec,
        raw_bindings=raw_collection.get("bindings"),
        active_template_bindings=active_template_bindings,
        active_template_parameter_names=active_template_parameter_names,
      )
      collection_path_strict = True
    else:
      collection_path = _normalize_collection_schema_path(raw_collection.get("path"))
      collection_spec = _resolve_collection_path_schema(
        collection_path,
        collection_specs_by_path=collection_specs_by_path,
      )
    node_allowed_filter_keys = set(collection_spec.filter_keys)
    raw_collection_quantifier = raw_collection.get("quantifier")
    if not isinstance(raw_collection_quantifier, str) or raw_collection_quantifier not in {"any", "all", "none"}:
      raise ValueError("Filter expression collection quantifier must be one of `any`, `all`, or `none`.")
    collection_quantifier = raw_collection_quantifier
  raw_conditions = raw_node.get("conditions", [])
  if not isinstance(raw_conditions, list):
    raise ValueError("Filter expression `conditions` must be a list.")
  raw_children = raw_node.get("children", [])
  if not isinstance(raw_children, list):
    raise ValueError("Filter expression `children` must be a list.")
  conditions = tuple(
    _parse_runtime_filter_expression_condition(
      raw_condition,
      filter_specs_by_key=filter_specs_by_key,
      allowed_filter_keys=node_allowed_filter_keys,
      active_template_bindings=active_template_bindings,
      active_template_parameter_names=active_template_parameter_names,
    )
    for raw_condition in raw_conditions
  )
  children = tuple(
    _parse_runtime_filter_expression_node(
      raw_child,
      filter_specs_by_key=filter_specs_by_key,
      predicate_registry=predicate_registry,
      predicate_template_registry=predicate_template_registry,
      collection_specs_by_path=collection_specs_by_path,
      collection_specs_by_template=collection_specs_by_template,
      active_predicate_refs=active_predicate_refs,
      active_collection_filter_keys=node_allowed_filter_keys,
      active_template_bindings=active_template_bindings,
      active_template_parameter_names=active_template_parameter_names,
    )
    for raw_child in raw_children
  )
  if not conditions and not children:
    raise ValueError("Filter expression nodes must declare conditions or children.")
  return StandaloneSurfaceFilterExpressionNode(
    logic=logic.lower(),
    conditions=conditions,
    children=children,
    negated=bool(raw_node.get("negated", False)),
    collection_path=collection_path,
    collection_quantifier=collection_quantifier,
    collection_path_strict=collection_path_strict,
  )


def _build_runtime_filter_expression(
  binding: StandaloneSurfaceRuntimeBinding,
  *,
  raw_expression: str | None,
) -> StandaloneSurfaceFilterExpressionNode | None:
  if not raw_expression:
    return None
  try:
    parsed_expression = json.loads(raw_expression)
  except json.JSONDecodeError as exc:
    raise ValueError("Filter expression must be valid JSON.") from exc
  collection_specs_by_path = {
    spec.path: spec
    for spec in binding.collection_path_specs
  }
  collection_specs_by_template = {
    (spec.path_template or spec.path): spec
    for spec in binding.collection_path_specs
  }
  predicate_registry: dict[str, Any] = {}
  predicate_template_registry: dict[str, Any] = {}
  root_expression = parsed_expression
  if isinstance(parsed_expression, dict) and "predicates" in parsed_expression:
    raw_predicates = parsed_expression.get("predicates")
    if not isinstance(raw_predicates, dict):
      raise ValueError("Filter expression `predicates` must be an object map.")
    predicate_registry = raw_predicates
  if isinstance(parsed_expression, dict) and "predicate_templates" in parsed_expression:
    raw_predicate_templates = parsed_expression.get("predicate_templates")
    if not isinstance(raw_predicate_templates, dict):
      raise ValueError("Filter expression `predicate_templates` must be an object map.")
    predicate_template_registry = raw_predicate_templates
  if isinstance(parsed_expression, dict) and "root" in parsed_expression:
    root_expression = parsed_expression["root"]
  elif isinstance(parsed_expression, dict) and ("predicates" in parsed_expression or "predicate_templates" in parsed_expression):
    root_expression = {
      key: value
      for key, value in parsed_expression.items()
      if key not in {"predicates", "predicate_templates"}
    }
  return _parse_runtime_filter_expression_node(
    root_expression,
    filter_specs_by_key={
      spec.key: spec
      for spec in binding.filter_param_specs
    },
    predicate_registry=predicate_registry,
    predicate_template_registry=predicate_template_registry,
    collection_specs_by_path=collection_specs_by_path,
    collection_specs_by_template=collection_specs_by_template,
  )


def _parse_grouped_filter_query_key(
  raw_key: str,
  *,
  alias: str,
  default_operator: str,
  supported_operators: dict[str, Any],
) -> tuple[str, str] | None:
  if not raw_key.startswith("group__"):
    return None
  parts = raw_key.split("__")
  if len(parts) < 3:
    return None
  _, group_key, *remainder = parts
  if not group_key or not remainder:
    return None
  operator_key = default_operator
  alias_key = "__".join(remainder)
  if remainder[-1] in supported_operators:
    operator_key = remainder[-1]
    alias_key = "__".join(remainder[:-1])
  if alias_key != alias:
    return None
  return group_key, operator_key


def _has_meaningful_filter_value(value: Any) -> bool:
  if value is None:
    return False
  if isinstance(value, str):
    return bool(value)
  if isinstance(value, (list, tuple, set, dict)):
    return bool(value)
  return True


def _build_runtime_query_filters(
  binding: StandaloneSurfaceRuntimeBinding,
  *,
  kwargs: dict[str, Any],
  request: Request | None,
) -> dict[str, Any] | None:
  if not binding.filter_param_specs and not binding.sort_field_specs:
    return None
  filters = {
    spec.key: kwargs[spec.key]
    for spec in binding.filter_param_specs
    if spec.query_exposed
  }
  filter_expression = _build_runtime_filter_expression(
    binding,
    raw_expression=kwargs.get("filter_expr"),
  )
  if filter_expression is not None:
    filters["__filter_expression__"] = filter_expression
  conditions: list[StandaloneSurfaceFilterCondition] = []
  if request is not None:
    query_params = request.query_params
    for spec in binding.filter_param_specs:
      if not spec.query_exposed:
        continue
      alias = spec.openapi.alias if spec.openapi and spec.openapi.alias else spec.key
      supported_operators = {
        operator.key: operator
        for operator in spec.operators
      }
      default_operator = spec.operators[0].key if spec.operators else "eq"
      base_value = kwargs[spec.key]
      if _has_meaningful_filter_value(base_value):
        conditions.append(
          StandaloneSurfaceFilterCondition(
            key=spec.key,
            operator=default_operator,
            value=base_value,
          )
        )
      for raw_key in query_params.keys():
        grouped = _parse_grouped_filter_query_key(
          raw_key,
          alias=alias,
          default_operator=default_operator,
          supported_operators=supported_operators,
        )
        if grouped is not None:
          group_key, operator_key = grouped
          operator_spec = supported_operators[operator_key]
          conditions.append(
            StandaloneSurfaceFilterCondition(
              key=spec.key,
              operator=operator_key,
              value=_coerce_filter_query_values(
                spec,
                value_shape=operator_spec.value_shape,
                values=query_params.getlist(raw_key),
              ),
              group=group_key,
            )
          )
          continue
        if not raw_key.startswith(f"{alias}__"):
          continue
        operator_key = raw_key.split("__", 1)[1]
        if operator_key not in supported_operators:
          raise ValueError(f"Unsupported filter operator for {spec.key}: {operator_key}")
        operator_spec = supported_operators[operator_key]
        conditions.append(
          StandaloneSurfaceFilterCondition(
            key=spec.key,
            operator=operator_key,
            value=_coerce_filter_query_values(
              spec,
              value_shape=operator_spec.value_shape,
              values=query_params.getlist(raw_key),
            ),
          )
        )
    if conditions:
      filters["__filter_conditions__"] = tuple(conditions)
    if binding.sort_field_specs:
      sort_terms: list[StandaloneSurfaceSortTerm] = []
      allowed_sort_fields = {
        field.key: field
        for field in binding.sort_field_specs
      }
      for raw_sort in kwargs.get("sort", ()):
        field_key, separator, direction = raw_sort.partition(":")
        if field_key not in allowed_sort_fields:
          raise ValueError(f"Unsupported sort field: {field_key}")
        if not separator:
          direction = allowed_sort_fields[field_key].default_direction
        normalized_direction = direction.lower()
        if normalized_direction not in {"asc", "desc"}:
          raise ValueError(f"Unsupported sort direction for {field_key}: {direction}")
        sort_terms.append(
          StandaloneSurfaceSortTerm(
            key=field_key,
            direction=normalized_direction,
          )
        )
      if sort_terms:
        filters["__sort_terms__"] = tuple(sort_terms)
  return filters


def create_router(container: Container) -> APIRouter:
  router = APIRouter()

  def get_app() -> TradingApplication:
    return container.app

  def dispatch_standalone_binding(
    *,
    binding: StandaloneSurfaceRuntimeBinding,
    app: TradingApplication,
    run_id: str | None = None,
    filters: dict[str, Any] | None = None,
    request_payload: dict[str, Any] | None = None,
    path_params: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        run_id=run_id,
        filters=filters,
        request_payload=request_payload,
        path_params=path_params,
        headers=headers,
      )
    except PermissionError as exc:
      raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  def build_standalone_surface_route_handler(binding: StandaloneSurfaceRuntimeBinding):
    def handle_surface(**kwargs: Any) -> dict[str, Any]:
      request_payload = None
      if binding.request_payload_kind is not None:
        request_model = kwargs["request"]
        _, dump_kwargs = REQUEST_PAYLOAD_MODELS[binding.request_payload_kind]
        request_payload = request_model.model_dump(**dump_kwargs)
      request_context = kwargs.get("request")
      try:
        filters = _build_runtime_query_filters(
          binding,
          kwargs=kwargs,
          request=request_context,
        )
      except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
      return dispatch_standalone_binding(
        binding=binding,
        app=kwargs["app"],
        run_id=kwargs.get("run_id"),
        filters=filters,
        path_params=(
          {key: kwargs[key] for key in binding.path_param_keys}
          if binding.path_param_keys
          else None
        ),
        headers=(
          {key: kwargs.get(key) for key in binding.header_keys}
          if binding.header_keys
          else None
        ),
        request_payload=request_payload,
      )

    parameters: list[inspect.Parameter] = []
    if binding.scope == "run":
      parameters.append(
        inspect.Parameter(
          "run_id",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str,
        )
      )
    for path_param_key in binding.path_param_keys:
      parameters.append(
        inspect.Parameter(
          path_param_key,
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str,
        )
      )
    if binding.filter_param_specs or binding.sort_field_specs:
      parameters.append(
        inspect.Parameter(
          "request",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=Request,
        )
      )
    if binding.filter_param_specs:
      parameters.append(
        inspect.Parameter(
          "filter_expr",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str | None,
          default=_build_filter_expression_query_default(),
        )
      )
    for filter_spec in binding.filter_param_specs:
      if not filter_spec.query_exposed:
        continue
      parameters.append(
        inspect.Parameter(
          filter_spec.key,
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=filter_spec.annotation,
          default=_build_query_default(filter_spec),
        )
      )
    if binding.sort_field_specs:
      parameters.append(
        inspect.Parameter(
          "sort",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=list[str],
          default=_build_sort_query_default(binding),
        )
      )
    if binding.request_payload_kind is not None:
      request_model, _ = REQUEST_PAYLOAD_MODELS[binding.request_payload_kind]
      parameters.append(
        inspect.Parameter(
          "request",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=request_model,
        )
      )
    for header_key in binding.header_keys:
      parameters.append(
        inspect.Parameter(
          header_key,
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str | None,
          default=Header(default=None, alias=_build_header_alias(header_key)),
        )
      )
    parameters.append(
      inspect.Parameter(
        "app",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=TradingApplication,
        default=Depends(get_app),
      )
    )

    handle_surface.__name__ = binding.route_name
    handle_surface.__signature__ = inspect.Signature(
      parameters=parameters,
      return_annotation=Any,
    )
    return handle_surface
  for binding in list_standalone_surface_runtime_bindings(get_app().get_run_surface_capabilities()):
    router.add_api_route(
      binding.route_path,
      build_standalone_surface_route_handler(binding),
      methods=list(binding.methods),
      name=binding.route_name,
      summary=binding.response_title,
      openapi_extra=_build_route_openapi_extra(binding),
    )

  def reconstruct_operator_provider_provenance_scheduler_health_export(
    request: OperatorProviderProvenanceSchedulerHistoricalExportRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.reconstruct_provider_provenance_scheduler_health_export(
        alert_category=request.alert_category,
        detected_at=request.detected_at,
        resolved_at=request.resolved_at,
        narrative_mode=request.narrative_mode,
        export_format=request.format,
        history_limit=request.history_limit,
        drilldown_history_limit=request.drilldown_history_limit,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-health/reconstruct-export",
    reconstruct_operator_provider_provenance_scheduler_health_export,
    methods=["POST"],
    name="reconstruct_operator_provider_provenance_scheduler_health_export",
    summary="Reconstruct provider provenance scheduler health export for a historical alert row",
  )

  return router


def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)
