from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

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
