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


class OperatorProviderProvenanceSchedulerNarrativeReportRequest(BaseModel):
  alert_category: str | None = None
  status: str | None = None
  narrative_facet: str | None = None
  search: str | None = None
  offset: int = 0
  occurrence_limit: int = 8
  format: str = "json"
  history_limit: int = 25
  drilldown_history_limit: int = 24


class OperatorProviderProvenanceSchedulerSearchFeedbackRequest(BaseModel):
  query_id: str
  query: str
  occurrence_id: str
  signal: str
  matched_fields: list[str] = Field(default_factory=list)
  semantic_concepts: list[str] = Field(default_factory=list)
  operator_hits: list[str] = Field(default_factory=list)
  lexical_score: int = 0
  semantic_score: int = 0
  operator_score: int = 0
  score: int = 0
  ranking_reason: str | None = None
  note: str | None = None
  actor: str = "operator"
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchFeedbackModerationRequest(BaseModel):
  moderation_status: str
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchFeedbackBatchModerationRequest(BaseModel):
  feedback_ids: list[str] = Field(default_factory=list)
  moderation_status: str
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogCreateRequest(BaseModel):
  name: str
  description: str = ""
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernanceRequest(BaseModel):
  action: str
  catalog_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPlanStageRequest(BaseModel):
  feedback_ids: list[str] = Field(default_factory=list)
  policy_catalog_id: str | None = None
  moderation_status: str | None = None
  actor: str = "operator"
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPlanApprovalRequest(BaseModel):
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationPlanApplyRequest(BaseModel):
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyCreateRequest(BaseModel):
  name: str
  description: str = ""
  action_scope: str = "any"
  require_approval_note: bool = False
  guidance: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  action_scope: str | None = None
  require_approval_note: bool | None = None
  guidance: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernanceRequest(BaseModel):
  action: str
  governance_policy_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  action_scope: str | None = None
  require_approval_note: bool | None = None
  guidance: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanStageRequest(BaseModel):
  catalog_ids: list[str] = Field(default_factory=list)
  action: str
  governance_policy_id: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  actor: str = "operator"
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanApprovalRequest(BaseModel):
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanApplyRequest(BaseModel):
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyCreateRequest(BaseModel):
  name: str
  description: str = ""
  action_scope: str = "any"
  require_approval_note: bool = False
  guidance: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  policy_action_scope: str | None = None
  policy_require_approval_note: bool | None = None
  policy_guidance: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanStageRequest(BaseModel):
  governance_policy_ids: list[str] = Field(default_factory=list)
  action: str
  meta_policy_id: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  action_scope: str | None = None
  require_approval_note: bool | None = None
  guidance: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  actor: str = "operator"
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanApprovalRequest(BaseModel):
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanApplyRequest(BaseModel):
  actor: str = "operator"
  note: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None


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


class OperatorProviderProvenanceSchedulerStitchedReportViewCreateRequest(BaseModel):
  name: str
  description: str = ""
  query: dict[str, Any] = Field(default_factory=dict)
  occurrence_limit: int = 8
  history_limit: int = 12
  drilldown_history_limit: int = 12
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerStitchedReportViewUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  query: dict[str, Any] | None = None
  occurrence_limit: int | None = None
  history_limit: int | None = None
  drilldown_history_limit: int | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_stitched_report_view_updated"


class OperatorProviderProvenanceSchedulerStitchedReportViewDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_stitched_report_view_deleted"


class OperatorProviderProvenanceSchedulerStitchedReportViewBulkGovernanceRequest(BaseModel):
  action: str
  view_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  occurrence_limit: int | None = None
  history_limit: int | None = None
  drilldown_history_limit: int | None = None


class OperatorProviderProvenanceSchedulerStitchedReportViewRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_stitched_report_view_revision_restored"


class OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryCreateRequest(BaseModel):
  name: str
  description: str = ""
  queue_view: dict[str, Any] = Field(default_factory=dict)
  default_policy_template_id: str | None = None
  default_policy_catalog_id: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  queue_view: dict[str, Any] | None = None
  default_policy_template_id: str | None = None
  default_policy_catalog_id: str | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_stitched_report_governance_registry_updated"


class OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryDeleteRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_stitched_report_governance_registry_deleted"


class OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRestoreRequest(BaseModel):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_stitched_report_governance_registry_revision_restored"


class OperatorProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernanceRequest(BaseModel):
  action: str
  registry_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  queue_view_patch: dict[str, Any] | None = None
  default_policy_template_id: str | None = None
  default_policy_catalog_id: str | None = None


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
  step_id: str | None = None
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


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepUpdateRequest(
  BaseModel
):
  item_ids: list[str] | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  layout_patch: dict[str, Any] | None = None
  template_id: str | None = None
  clear_template_link: bool | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_step_updated"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRestoreRequest(
  BaseModel
):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_step_restored"


class OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkGovernanceRequest(
  BaseModel
):
  action: str
  step_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  layout_patch: dict[str, Any] | None = None
  template_id: str | None = None
  clear_template_link: bool | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateCreateRequest(
  BaseModel
):
  name: str
  description: str = ""
  step: OperatorProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRequest | None = None
  origin_catalog_id: str | None = None
  origin_step_id: str | None = None
  governance_policy_template_id: str | None = None
  governance_policy_catalog_id: str | None = None
  governance_approval_lane: str | None = None
  governance_approval_priority: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateApplyRequest(
  BaseModel
):
  catalog_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateStageRequest(
  BaseModel
):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_hierarchy_step_template_staged"


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBatchStageRequest(
  BaseModel
):
  hierarchy_step_template_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_hierarchy_step_templates_staged"


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateUpdateRequest(
  BaseModel
):
  name: str | None = None
  description: str | None = None
  item_ids: list[str] | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  layout_patch: dict[str, Any] | None = None
  template_id: str | None = None
  clear_template_link: bool | None = None
  governance_policy_template_id: str | None = None
  governance_policy_catalog_id: str | None = None
  governance_approval_lane: str | None = None
  governance_approval_priority: str | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_hierarchy_step_template_updated"


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDeleteRequest(
  BaseModel
):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_hierarchy_step_template_deleted"


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRestoreRequest(
  BaseModel
):
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str = "scheduler_narrative_governance_hierarchy_step_template_revision_restored"


class OperatorProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkGovernanceRequest(
  BaseModel
):
  action: str
  hierarchy_step_template_ids: list[str] = Field(default_factory=list)
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None
  reason: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  item_ids: list[str] | None = None
  step_name_prefix: str | None = None
  step_name_suffix: str | None = None
  step_description_append: str | None = None
  query_patch: dict[str, Any] | None = None
  layout_patch: dict[str, Any] | None = None
  template_id: str | None = None
  clear_template_link: bool | None = None


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
  queue_view_patch: dict[str, Any] | None = None
  default_policy_template_id: str | None = None
  default_policy_catalog_id: str | None = None
  occurrence_limit: int | None = None
  history_limit: int | None = None
  drilldown_history_limit: int | None = None
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

  def export_operator_provider_provenance_scheduler_stitched_narrative_report(
    request: OperatorProviderProvenanceSchedulerNarrativeReportRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.export_provider_provenance_scheduler_stitched_narrative_report(
        category=request.alert_category,
        status=request.status,
        narrative_facet=request.narrative_facet,
        search=request.search,
        offset=request.offset,
        occurrence_limit=request.occurrence_limit,
        export_format=request.format,
        history_limit=request.history_limit,
        drilldown_history_limit=request.drilldown_history_limit,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-alerts/report-export",
    export_operator_provider_provenance_scheduler_stitched_narrative_report,
    methods=["POST"],
    name="export_operator_provider_provenance_scheduler_stitched_narrative_report",
    summary="Export a stitched multi-occurrence scheduler narrative report",
  )

  def record_operator_provider_provenance_scheduler_search_feedback(
    request: OperatorProviderProvenanceSchedulerSearchFeedbackRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.record_provider_provenance_scheduler_alert_search_feedback(
        query_id=request.query_id,
        query=request.query,
        occurrence_id=request.occurrence_id,
        signal=request.signal,
        matched_fields=tuple(request.matched_fields),
        semantic_concepts=tuple(request.semantic_concepts),
        operator_hits=tuple(request.operator_hits),
        lexical_score=request.lexical_score,
        semantic_score=request.semantic_score,
        operator_score=request.operator_score,
        score=request.score,
        ranking_reason=request.ranking_reason,
        note=request.note,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-alerts/search-feedback",
    record_operator_provider_provenance_scheduler_search_feedback,
    methods=["POST"],
    name="record_operator_provider_provenance_scheduler_search_feedback",
    summary="Record operator feedback for scheduler search ranking",
  )

  def get_operator_provider_provenance_scheduler_search_dashboard(
    search: str | None = None,
    moderation_status: str | None = None,
    signal: str | None = None,
    governance_view: str | None = None,
    window_days: int = 30,
    stale_pending_hours: int = 24,
    query_limit: int = 12,
    feedback_limit: int = 20,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.get_provider_provenance_scheduler_search_dashboard(
        search=search,
        moderation_status=moderation_status,
        signal=signal,
        governance_view=governance_view,
        window_days=window_days,
        stale_pending_hours=stale_pending_hours,
        query_limit=query_limit,
        feedback_limit=feedback_limit,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/dashboard",
    get_operator_provider_provenance_scheduler_search_dashboard,
    methods=["GET"],
    name="get_operator_provider_provenance_scheduler_search_dashboard",
    summary="List scheduler query analytics and feedback moderation data",
  )

  def moderate_operator_provider_provenance_scheduler_search_feedback(
    feedback_id: str,
    request: OperatorProviderProvenanceSchedulerSearchFeedbackModerationRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.moderate_provider_provenance_scheduler_search_feedback(
        feedback_id=feedback_id,
        moderation_status=request.moderation_status,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/feedback/{feedback_id}/moderate",
    moderate_operator_provider_provenance_scheduler_search_feedback,
    methods=["POST"],
    name="moderate_operator_provider_provenance_scheduler_search_feedback",
    summary="Moderate scheduler search feedback before it influences ranking",
  )

  def moderate_operator_provider_provenance_scheduler_search_feedback_batch(
    request: OperatorProviderProvenanceSchedulerSearchFeedbackBatchModerationRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.moderate_provider_provenance_scheduler_search_feedback_batch(
        feedback_ids=tuple(request.feedback_ids),
        moderation_status=request.moderation_status,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/feedback/batch-moderate",
    moderate_operator_provider_provenance_scheduler_search_feedback_batch,
    methods=["POST"],
    name="moderate_operator_provider_provenance_scheduler_search_feedback_batch",
    summary="Moderate scheduler search feedback in batch",
  )

  def create_operator_provider_provenance_scheduler_search_moderation_policy_catalog(
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.create_provider_provenance_scheduler_search_moderation_policy_catalog(
        name=request.name,
        description=request.description,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        created_by_tab_id=request.created_by_tab_id,
        created_by_tab_label=request.created_by_tab_label,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs",
    create_operator_provider_provenance_scheduler_search_moderation_policy_catalog,
    methods=["POST"],
    name="create_operator_provider_provenance_scheduler_search_moderation_policy_catalog",
    summary="Create a reusable moderation policy catalog for scheduler search governance",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_policy_catalogs(
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_policy_catalogs()

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs",
    list_operator_provider_provenance_scheduler_search_moderation_policy_catalogs,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_policy_catalogs",
    summary="List scheduler search moderation policy catalogs",
  )

  def update_operator_provider_provenance_scheduler_search_moderation_policy_catalog(
    catalog_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogUpdateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.update_provider_provenance_scheduler_search_moderation_policy_catalog(
        catalog_id,
        name=request.name,
        description=request.description,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_policy_catalog_updated"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}",
    update_operator_provider_provenance_scheduler_search_moderation_policy_catalog,
    methods=["PATCH"],
    name="update_operator_provider_provenance_scheduler_search_moderation_policy_catalog",
    summary="Update a scheduler search moderation policy catalog",
  )

  def delete_operator_provider_provenance_scheduler_search_moderation_policy_catalog(
    catalog_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogDeleteRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.delete_provider_provenance_scheduler_search_moderation_policy_catalog(
        catalog_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_policy_catalog_deleted"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}/delete",
    delete_operator_provider_provenance_scheduler_search_moderation_policy_catalog,
    methods=["POST"],
    name="delete_operator_provider_provenance_scheduler_search_moderation_policy_catalog",
    summary="Delete a scheduler search moderation policy catalog",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revisions(
    catalog_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.list_provider_provenance_scheduler_search_moderation_policy_catalog_revisions(
        catalog_id
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}/revisions",
    list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revisions,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
    summary="List scheduler search moderation policy catalog revisions",
  )

  def restore_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
    catalog_id: str,
    revision_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRestoreRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.restore_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
        catalog_id,
        revision_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_policy_catalog_revision_restored"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}/revisions/{revision_id}/restore",
    restore_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revision,
    methods=["POST"],
    name="restore_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revision",
    summary="Restore a scheduler search moderation policy catalog revision",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_audits(
    catalog_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_policy_catalog_audits(
      catalog_id=catalog_id,
      action=action,
      actor_tab_id=actor_tab_id,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/audits",
    list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_audits,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_audits",
    summary="List scheduler search moderation policy catalog audit records",
  )

  def bulk_govern_operator_provider_provenance_scheduler_search_moderation_policy_catalogs(
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernanceRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      result = app.bulk_govern_provider_provenance_scheduler_search_moderation_policy_catalogs(
        catalog_ids=request.catalog_ids,
        action=request.action,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=request.reason,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
      "item_type": result.item_type,
      "action": result.action,
      "reason": result.reason,
      "requested_count": result.requested_count,
      "applied_count": result.applied_count,
      "skipped_count": result.skipped_count,
      "failed_count": result.failed_count,
      "results": tuple(
        {
          "item_id": entry.item_id,
          "item_name": entry.item_name,
          "outcome": entry.outcome,
          "status": entry.status,
          "current_revision_id": entry.current_revision_id,
          "message": entry.message,
        }
        for entry in result.results
      ),
    }

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/bulk-governance",
    bulk_govern_operator_provider_provenance_scheduler_search_moderation_policy_catalogs,
    methods=["POST"],
    name="bulk_govern_operator_provider_provenance_scheduler_search_moderation_policy_catalogs",
    summary="Bulk govern scheduler search moderation policy catalogs",
  )

  def stage_operator_provider_provenance_scheduler_search_moderation_plan(
    request: OperatorProviderProvenanceSchedulerSearchModerationPlanStageRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.stage_provider_provenance_scheduler_search_moderation_plan(
        feedback_ids=tuple(request.feedback_ids),
        policy_catalog_id=request.policy_catalog_id,
        moderation_status=request.moderation_status,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans",
    stage_operator_provider_provenance_scheduler_search_moderation_plan,
    methods=["POST"],
    name="stage_operator_provider_provenance_scheduler_search_moderation_plan",
    summary="Stage scheduler search moderation feedback into an approval queue plan",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_plans(
    queue_state: str | None = None,
    policy_catalog_id: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_plans(
      queue_state=queue_state,
      policy_catalog_id=policy_catalog_id,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans",
    list_operator_provider_provenance_scheduler_search_moderation_plans,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_plans",
    summary="List staged scheduler search moderation approval queue plans",
  )

  def approve_operator_provider_provenance_scheduler_search_moderation_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPlanApprovalRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.approve_provider_provenance_scheduler_search_moderation_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans/{plan_id}/approve",
    approve_operator_provider_provenance_scheduler_search_moderation_plan,
    methods=["POST"],
    name="approve_operator_provider_provenance_scheduler_search_moderation_plan",
    summary="Approve a staged scheduler search moderation plan",
  )

  def apply_operator_provider_provenance_scheduler_search_moderation_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPlanApplyRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.apply_provider_provenance_scheduler_search_moderation_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans/{plan_id}/apply",
    apply_operator_provider_provenance_scheduler_search_moderation_plan,
    methods=["POST"],
    name="apply_operator_provider_provenance_scheduler_search_moderation_plan",
    summary="Apply an approved scheduler search moderation plan",
  )

  def create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.create_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
        name=request.name,
        description=request.description,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        created_by_tab_id=request.created_by_tab_id,
        created_by_tab_label=request.created_by_tab_label,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies",
    create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy,
    methods=["POST"],
    name="create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy",
    summary="Create a reusable governance policy for moderation policy catalogs",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
    action_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
      action_scope=action_scope,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies",
    summary="List reusable governance policies for moderation policy catalogs",
  )

  def update_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    governance_policy_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyUpdateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.update_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
        governance_policy_id,
        name=request.name,
        description=request.description,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_catalog_governance_policy_updated"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}",
    update_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy,
    methods=["PATCH"],
    name="update_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy",
    summary="Update a reusable governance policy for moderation policy catalogs",
  )

  def delete_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    governance_policy_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDeleteRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
        governance_policy_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_catalog_governance_policy_deleted"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}/delete",
    delete_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy,
    methods=["POST"],
    name="delete_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy",
    summary="Delete a reusable governance policy for moderation policy catalogs",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions(
    governance_policy_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions(
        governance_policy_id
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}/revisions",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
    summary="List moderation catalog governance policy revisions",
  )

  def restore_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    governance_policy_id: str,
    revision_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRestoreRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
        governance_policy_id,
        revision_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_catalog_governance_policy_revision_restored"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}/revisions/{revision_id}/restore",
    restore_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision,
    methods=["POST"],
    name="restore_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision",
    summary="Restore a moderation catalog governance policy revision",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits(
    governance_policy_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits(
      governance_policy_id=governance_policy_id,
      action=action,
      actor_tab_id=actor_tab_id,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/audits",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
    summary="List moderation catalog governance policy audit records",
  )

  def bulk_govern_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernanceRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      result = app.bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
        governance_policy_ids=request.governance_policy_ids,
        action=request.action,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=request.reason,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
      "item_type": result.item_type,
      "action": result.action,
      "reason": result.reason,
      "requested_count": result.requested_count,
      "applied_count": result.applied_count,
      "skipped_count": result.skipped_count,
      "failed_count": result.failed_count,
      "results": tuple(
        {
          "item_id": entry.item_id,
          "item_name": entry.item_name,
          "outcome": entry.outcome,
          "status": entry.status,
          "current_revision_id": entry.current_revision_id,
          "message": entry.message,
        }
        for entry in result.results
      ),
    }

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/bulk-governance",
    bulk_govern_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies,
    methods=["POST"],
    name="bulk_govern_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies",
    summary="Bulk govern moderation catalog governance policies",
  )

  def stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanStageRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
        catalog_ids=request.catalog_ids,
        action=request.action,
        governance_policy_id=request.governance_policy_id,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans",
    stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan,
    methods=["POST"],
    name="stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan",
    summary="Stage moderation policy catalog governance changes into an approval queue plan",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plans(
    queue_state: str | None = None,
    governance_policy_id: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_plans(
      queue_state=queue_state,
      governance_policy_id=governance_policy_id,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plans,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plans",
    summary="List staged moderation policy catalog governance plans",
  )

  def approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanApprovalRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans/{plan_id}/approve",
    approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan,
    methods=["POST"],
    name="approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan",
    summary="Approve a staged moderation policy catalog governance plan",
  )

  def apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanApplyRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans/{plan_id}/apply",
    apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan,
    methods=["POST"],
    name="apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan",
    summary="Apply an approved moderation policy catalog governance plan",
  )

  def create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy(
        name=request.name,
        description=request.description,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        policy_action_scope=request.policy_action_scope,
        policy_require_approval_note=request.policy_require_approval_note,
        policy_guidance=request.policy_guidance,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        created_by_tab_id=request.created_by_tab_id,
        created_by_tab_label=request.created_by_tab_label,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-policies",
    create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy,
    methods=["POST"],
    name="create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy",
    summary="Create a reusable meta policy for moderation governance policies",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies(
    action_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies(
      action_scope=action_scope,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-policies",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
    summary="List reusable meta policies for moderation governance policies",
  )

  def stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanStageRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
        governance_policy_ids=request.governance_policy_ids,
        action=request.action,
        meta_policy_id=request.meta_policy_id,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans",
    stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan,
    methods=["POST"],
    name="stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan",
    summary="Stage moderation governance policy changes into an approval queue plan",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans(
    queue_state: str | None = None,
    meta_policy_id: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans(
      queue_state=queue_state,
      meta_policy_id=meta_policy_id,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
    summary="List staged moderation governance policy plans",
  )

  def approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanApprovalRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans/{plan_id}/approve",
    approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan,
    methods=["POST"],
    name="approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan",
    summary="Approve a staged moderation governance policy plan",
  )

  def apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanApplyRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans/{plan_id}/apply",
    apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan,
    methods=["POST"],
    name="apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan",
    summary="Apply an approved moderation governance policy plan",
  )

  return router


def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)
