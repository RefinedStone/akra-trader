from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

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
