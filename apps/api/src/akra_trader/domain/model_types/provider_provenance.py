from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

@dataclass(frozen=True)
class ReplayIntentAliasRecord:
  alias_id: str
  signature: str
  template_key: str
  template_label: str
  intent: dict[str, Any]
  redaction_policy: str
  retention_policy: str
  created_at: datetime
  expires_at: datetime | None = None
  revoked_at: datetime | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  revoked_by_tab_id: str | None = None
  revoked_by_tab_label: str | None = None


@dataclass(frozen=True)
class ReplayIntentAliasAuditRecord:
  audit_id: str
  alias_id: str
  action: str
  template_key: str
  template_label: str
  redaction_policy: str
  retention_policy: str
  recorded_at: datetime
  expires_at: datetime | None = None
  alias_created_at: datetime | None = None
  alias_expires_at: datetime | None = None
  alias_revoked_at: datetime | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ReplayIntentAliasAuditExportJobRecord:
  job_id: str
  export_format: str
  filename: str
  content_type: str
  record_count: int
  status: str
  created_at: datetime
  completed_at: datetime | None = None
  expires_at: datetime | None = None
  template_key: str | None = None
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None
  filters: dict[str, Any] = field(default_factory=dict)
  artifact_id: str | None = None
  content_length: int = 0
  content: str = ""


@dataclass(frozen=True)
class ReplayIntentAliasAuditExportArtifactRecord:
  artifact_id: str
  job_id: str
  filename: str
  content_type: str
  content: str
  created_at: datetime
  expires_at: datetime | None = None
  byte_length: int = 0


@dataclass(frozen=True)
class ReplayIntentAliasAuditExportJobAuditRecord:
  audit_id: str
  job_id: str
  action: str
  recorded_at: datetime
  expires_at: datetime | None = None
  template_key: str | None = None
  export_format: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ProviderProvenanceExportJobRecord:
  job_id: str
  export_scope: str
  export_format: str
  filename: str
  content_type: str
  status: str
  created_at: datetime
  completed_at: datetime | None = None
  exported_at: datetime | None = None
  expires_at: datetime | None = None
  focus_key: str | None = None
  focus_label: str | None = None
  market_data_provider: str | None = None
  venue: str | None = None
  symbol: str | None = None
  timeframe: str | None = None
  result_count: int = 0
  provider_provenance_count: int = 0
  provider_labels: tuple[str, ...] = ()
  vendor_fields: tuple[str, ...] = ()
  filter_summary: str | None = None
  filters: dict[str, Any] = field(default_factory=dict)
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None
  available_delivery_targets: tuple[str, ...] = ()
  routing_policy_id: str | None = None
  routing_policy_summary: str | None = None
  routing_targets: tuple[str, ...] = ()
  approval_policy_id: str | None = None
  approval_required: bool = False
  approval_state: str = "not_required"
  approval_summary: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approval_note: str | None = None
  escalation_count: int = 0
  last_escalated_at: datetime | None = None
  last_escalated_by: str | None = None
  last_escalation_reason: str | None = None
  last_delivery_targets: tuple[str, ...] = ()
  last_delivery_status: str | None = None
  last_delivery_summary: str | None = None
  artifact_id: str | None = None
  content_length: int = 0
  content: str = ""


@dataclass(frozen=True)
class ProviderProvenanceExportArtifactRecord:
  artifact_id: str
  job_id: str
  filename: str
  content_type: str
  content: str
  created_at: datetime
  expires_at: datetime | None = None
  byte_length: int = 0


@dataclass(frozen=True)
class ProviderProvenanceExportJobAuditRecord:
  audit_id: str
  job_id: str
  action: str
  recorded_at: datetime
  expires_at: datetime | None = None
  export_scope: str | None = None
  export_format: str | None = None
  focus_key: str | None = None
  focus_label: str | None = None
  symbol: str | None = None
  timeframe: str | None = None
  market_data_provider: str | None = None
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  routing_policy_id: str | None = None
  routing_targets: tuple[str, ...] = ()
  approval_policy_id: str | None = None
  approval_required: bool = False
  approval_state: str | None = None
  approval_summary: str | None = None
  approved_by: str | None = None
  delivery_targets: tuple[str, ...] = ()
  delivery_status: str | None = None
  delivery_summary: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ProviderProvenanceAnalyticsPresetRecord:
  preset_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceDashboardViewRecord:
  view_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  layout: dict[str, Any] = field(default_factory=dict)
  preset_id: str | None = None
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerStitchedReportViewRecord:
  view_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  occurrence_limit: int = 8
  history_limit: int = 12
  drilldown_history_limit: int = 12
  status: str = "active"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerStitchedReportViewRevisionRecord:
  revision_id: str
  view_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  occurrence_limit: int = 8
  history_limit: int = 12
  drilldown_history_limit: int = 12
  status: str = "active"
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerStitchedReportViewAuditRecord:
  audit_id: str
  view_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str = ""
  revision_id: str | None = None
  source_revision_id: str | None = None
  name: str = ""
  status: str = "active"
  occurrence_limit: int = 8
  history_limit: int = 12
  drilldown_history_limit: int = 12
  filter_summary: str = ""
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
  registry_id: str
  name: str
  description: str = ""
  queue_view: dict[str, Any] = field(default_factory=dict)
  default_policy_template_id: str | None = None
  default_policy_template_name: str | None = None
  default_policy_catalog_id: str | None = None
  default_policy_catalog_name: str | None = None
  status: str = "active"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord:
  revision_id: str
  registry_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  queue_view: dict[str, Any] = field(default_factory=dict)
  default_policy_template_id: str | None = None
  default_policy_template_name: str | None = None
  default_policy_catalog_id: str | None = None
  default_policy_catalog_name: str | None = None
  status: str = "active"
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord:
  audit_id: str
  registry_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str = ""
  revision_id: str | None = None
  source_revision_id: str | None = None
  name: str = ""
  description: str = ""
  queue_view: dict[str, Any] = field(default_factory=dict)
  default_policy_template_id: str | None = None
  default_policy_template_name: str | None = None
  default_policy_catalog_id: str | None = None
  default_policy_catalog_name: str | None = None
  status: str = "active"
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceScheduledReportRecord:
  report_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  layout: dict[str, Any] = field(default_factory=dict)
  preset_id: str | None = None
  view_id: str | None = None
  cadence: str = "daily"
  status: str = "scheduled"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  next_run_at: datetime | None = None
  last_run_at: datetime | None = None
  last_export_job_id: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeTemplateRecord:
  template_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  status: str = "active"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord:
  revision_id: str
  template_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  status: str = "active"
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeRegistryRecord:
  registry_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  layout: dict[str, Any] = field(default_factory=dict)
  template_id: str | None = None
  status: str = "active"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord:
  revision_id: str
  registry_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  layout: dict[str, Any] = field(default_factory=dict)
  template_id: str | None = None
  status: str = "active"
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult:
  item_id: str
  item_name: str | None = None
  outcome: str = "applied"
  status: str | None = None
  current_revision_id: str | None = None
  message: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
  item_type: str
  action: str
  reason: str
  requested_count: int = 0
  applied_count: int = 0
  skipped_count: int = 0
  failed_count: int = 0
  results: tuple[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult, ...] = ()


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePreviewItem:
  item_id: str
  item_name: str | None = None
  status: str | None = None
  current_revision_id: str | None = None
  apply_revision_id: str | None = None
  rollback_revision_id: str | None = None
  outcome: str = "changed"
  message: str | None = None
  changed_fields: tuple[str, ...] = ()
  field_diffs: dict[str, dict[str, Any]] = field(default_factory=dict)
  current_snapshot: dict[str, Any] = field(default_factory=dict)
  proposed_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
  policy_template_id: str
  name: str
  description: str = ""
  item_type_scope: str = "any"
  action_scope: str = "any"
  approval_lane: str = "general"
  approval_priority: str = "normal"
  guidance: str | None = None
  status: str = "active"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
  revision_id: str
  policy_template_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  item_type_scope: str = "any"
  action_scope: str = "any"
  approval_lane: str = "general"
  approval_priority: str = "normal"
  guidance: str | None = None
  status: str = "active"
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord:
  audit_id: str
  policy_template_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str = ""
  revision_id: str | None = None
  source_revision_id: str | None = None
  name: str = ""
  status: str = "active"
  item_type_scope: str = "any"
  action_scope: str = "any"
  approval_lane: str = "general"
  approval_priority: str = "normal"
  guidance: str | None = None
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
  catalog_id: str
  name: str
  description: str = ""
  policy_template_ids: tuple[str, ...] = ()
  policy_template_names: tuple[str, ...] = ()
  default_policy_template_id: str | None = None
  default_policy_template_name: str | None = None
  item_type_scope: str = "any"
  action_scope: str = "any"
  approval_lane: str = "general"
  approval_priority: str = "normal"
  guidance: str | None = None
  hierarchy_steps: tuple["ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep", ...] = ()
  status: str = "active"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
  revision_id: str
  catalog_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  policy_template_ids: tuple[str, ...] = ()
  policy_template_names: tuple[str, ...] = ()
  default_policy_template_id: str | None = None
  default_policy_template_name: str | None = None
  item_type_scope: str = "any"
  action_scope: str = "any"
  approval_lane: str = "general"
  approval_priority: str = "normal"
  guidance: str | None = None
  hierarchy_steps: tuple["ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep", ...] = ()
  status: str = "active"
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
  audit_id: str
  catalog_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str = ""
  revision_id: str | None = None
  source_revision_id: str | None = None
  name: str = ""
  status: str = "active"
  default_policy_template_id: str | None = None
  default_policy_template_name: str | None = None
  policy_template_ids: tuple[str, ...] = ()
  policy_template_names: tuple[str, ...] = ()
  item_type_scope: str = "any"
  action_scope: str = "any"
  approval_lane: str = "general"
  approval_priority: str = "normal"
  guidance: str | None = None
  hierarchy_steps: tuple["ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep", ...] = ()
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
  hierarchy_step_template_id: str
  name: str
  description: str = ""
  item_type: str = "template"
  step: "ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep" = field(
    default_factory=lambda: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep(
      item_type="template"
    )
  )
  origin_catalog_id: str | None = None
  origin_catalog_name: str | None = None
  origin_step_id: str | None = None
  governance_policy_template_id: str | None = None
  governance_policy_template_name: str | None = None
  governance_policy_catalog_id: str | None = None
  governance_policy_catalog_name: str | None = None
  governance_approval_lane: str = "general"
  governance_approval_priority: str = "normal"
  governance_policy_guidance: str | None = None
  status: str = "active"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord:
  revision_id: str
  hierarchy_step_template_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  item_type: str = "template"
  step: "ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep" = field(
    default_factory=lambda: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep(
      item_type="template"
    )
  )
  origin_catalog_id: str | None = None
  origin_catalog_name: str | None = None
  origin_step_id: str | None = None
  governance_policy_template_id: str | None = None
  governance_policy_template_name: str | None = None
  governance_policy_catalog_id: str | None = None
  governance_policy_catalog_name: str | None = None
  governance_approval_lane: str = "general"
  governance_approval_priority: str = "normal"
  governance_policy_guidance: str | None = None
  status: str = "active"
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord:
  audit_id: str
  hierarchy_step_template_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str = ""
  revision_id: str | None = None
  source_revision_id: str | None = None
  name: str = ""
  description: str = ""
  item_type: str = "template"
  step: "ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep" = field(
    default_factory=lambda: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep(
      item_type="template"
    )
  )
  origin_catalog_id: str | None = None
  origin_catalog_name: str | None = None
  origin_step_id: str | None = None
  governance_policy_template_id: str | None = None
  governance_policy_template_name: str | None = None
  governance_policy_catalog_id: str | None = None
  governance_policy_catalog_name: str | None = None
  governance_approval_lane: str = "general"
  governance_approval_priority: str = "normal"
  governance_policy_guidance: str | None = None
  status: str = "active"
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep:
  item_type: str
  step_id: str | None = None
  source_template_id: str | None = None
  source_template_name: str | None = None
  action: str = "update"
  item_ids: tuple[str, ...] = ()
  item_names: tuple[str, ...] = ()
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  query_patch: dict[str, Any] = field(default_factory=dict)
  layout_patch: dict[str, Any] = field(default_factory=dict)
  template_id: str | None = None
  clear_template_link: bool = False


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
  plan_id: str
  item_type: str
  action: str
  reason: str
  status: str = "previewed"
  source_hierarchy_step_template_id: str | None = None
  source_hierarchy_step_template_name: str | None = None
  policy_template_id: str | None = None
  policy_template_name: str | None = None
  policy_catalog_id: str | None = None
  policy_catalog_name: str | None = None
  approval_lane: str = "general"
  approval_priority: str = "normal"
  policy_guidance: str | None = None
  hierarchy_key: str | None = None
  hierarchy_name: str | None = None
  hierarchy_position: int | None = None
  hierarchy_total: int | None = None
  request_payload: dict[str, Any] = field(default_factory=dict)
  target_ids: tuple[str, ...] = ()
  preview_requested_count: int = 0
  preview_changed_count: int = 0
  preview_skipped_count: int = 0
  preview_failed_count: int = 0
  preview_items: tuple[ProviderProvenanceSchedulerNarrativeGovernancePreviewItem, ...] = ()
  rollback_ready_count: int = 0
  rollback_summary: str = ""
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  approved_at: datetime | None = None
  approved_by_tab_id: str | None = None
  approved_by_tab_label: str | None = None
  approval_note: str | None = None
  applied_at: datetime | None = None
  applied_by_tab_id: str | None = None
  applied_by_tab_label: str | None = None
  applied_result: ProviderProvenanceSchedulerNarrativeBulkGovernanceResult | None = None
  rolled_back_at: datetime | None = None
  rolled_back_by_tab_id: str | None = None
  rolled_back_by_tab_label: str | None = None
  rollback_note: str | None = None
  rollback_result: ProviderProvenanceSchedulerNarrativeBulkGovernanceResult | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult:
  plan_id: str
  action: str
  outcome: str
  status: str | None = None
  queue_state: str | None = None
  message: str | None = None
  plan: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult:
  action: str
  requested_count: int = 0
  succeeded_count: int = 0
  skipped_count: int = 0
  failed_count: int = 0
  results: tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult, ...] = ()


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePlanListResult:
  items: tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...] = ()
  total: int = 0
  pending_approval_count: int = 0
  ready_to_apply_count: int = 0
  completed_count: int = 0


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult:
  catalog_id: str
  catalog_name: str
  hierarchy_key: str
  hierarchy_name: str
  plan_count: int = 0
  summary: str = ""
  plans: tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...] = ()


@dataclass(frozen=True)
class ProviderProvenanceScheduledReportAuditRecord:
  audit_id: str
  report_id: str
  action: str
  recorded_at: datetime
  expires_at: datetime | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  export_job_id: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ProviderProvenanceSchedulerHealth:
  generated_at: datetime
  enabled: bool = True
  status: str = "starting"
  summary: str = ""
  interval_seconds: int = 60
  batch_limit: int = 25
  last_cycle_started_at: datetime | None = None
  last_cycle_finished_at: datetime | None = None
  last_success_at: datetime | None = None
  last_failure_at: datetime | None = None
  last_error: str | None = None
  cycle_count: int = 0
  success_count: int = 0
  failure_count: int = 0
  consecutive_failure_count: int = 0
  last_executed_count: int = 0
  total_executed_count: int = 0
  due_report_count: int = 0
  oldest_due_at: datetime | None = None
  max_due_lag_seconds: int = 0
  active_alert_key: str | None = None
  alert_workflow_job_id: str | None = None
  alert_workflow_triggered_at: datetime | None = None
  alert_workflow_state: str | None = None
  alert_workflow_summary: str | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderProvenanceSchedulerHealthRecord:
  record_id: str
  recorded_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  enabled: bool = True
  status: str = "starting"
  summary: str = ""
  interval_seconds: int = 60
  batch_limit: int = 25
  last_cycle_started_at: datetime | None = None
  last_cycle_finished_at: datetime | None = None
  last_success_at: datetime | None = None
  last_failure_at: datetime | None = None
  last_error: str | None = None
  cycle_count: int = 0
  success_count: int = 0
  failure_count: int = 0
  consecutive_failure_count: int = 0
  last_executed_count: int = 0
  total_executed_count: int = 0
  due_report_count: int = 0
  oldest_due_at: datetime | None = None
  max_due_lag_seconds: int = 0
  active_alert_key: str | None = None
  alert_workflow_job_id: str | None = None
  alert_workflow_triggered_at: datetime | None = None
  alert_workflow_state: str | None = None
  alert_workflow_summary: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  issues: tuple[str, ...] = ()
  search_projection: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchDocumentRecord:
  record_id: str
  recorded_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  index_version: str = "scheduler-search-store.v1"
  lexical_terms: tuple[str, ...] = ()
  semantic_concepts: tuple[str, ...] = ()
  fields: dict[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
  query_id: str
  recorded_at: datetime
  query: str
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  category: str | None = None
  status: str | None = None
  narrative_facet: str | None = None
  persistence_mode: str | None = None
  relevance_model: str | None = None
  token_count: int = 0
  operator_count: int = 0
  boolean_operator_count: int = 0
  semantic_concept_count: int = 0
  matched_occurrences: int = 0
  top_score: int = 0
  indexed_occurrence_count: int = 0
  indexed_term_count: int = 0
  query_terms: tuple[str, ...] = ()
  query_phrases: tuple[str, ...] = ()
  query_semantic_concepts: tuple[str, ...] = ()
  parsed_operators: tuple[str, ...] = ()
  matched_occurrence_ids: tuple[str, ...] = ()
  top_cluster_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchFeedbackRecord:
  feedback_id: str
  recorded_at: datetime
  query_id: str
  query: str
  occurrence_id: str
  signal: str
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  actor: str = "operator"
  note: str | None = None
  category: str | None = None
  status: str | None = None
  narrative_facet: str | None = None
  query_terms: tuple[str, ...] = ()
  query_phrases: tuple[str, ...] = ()
  query_semantic_concepts: tuple[str, ...] = ()
  parsed_operators: tuple[str, ...] = ()
  matched_fields: tuple[str, ...] = ()
  semantic_concepts: tuple[str, ...] = ()
  operator_hits: tuple[str, ...] = ()
  lexical_score: int = 0
  semantic_score: int = 0
  operator_score: int = 0
  score: int = 0
  ranking_reason: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  moderation_status: str = "pending"
  moderation_note: str | None = None
  moderated_at: datetime | None = None
  moderated_by: str | None = None
  moderated_by_tab_id: str | None = None
  moderated_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
  catalog_id: str
  created_at: datetime
  updated_at: datetime
  name: str
  scheduler_key: str = "provider_provenance_reports"
  description: str = ""
  status: str = "active"
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
  revision_id: str
  catalog_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
  audit_id: str
  catalog_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str = ""
  revision_id: str | None = None
  source_revision_id: str | None = None
  scheduler_key: str = "provider_provenance_reports"
  name: str = ""
  status: str = "active"
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPlanPreviewItem:
  feedback_id: str
  occurrence_id: str
  query: str
  signal: str
  current_moderation_status: str
  proposed_moderation_status: str
  score: int = 0
  age_hours: int = 0
  stale_pending: bool = False
  high_score_pending: bool = False
  query_run_count: int = 0
  eligible: bool = True
  reason_tags: tuple[str, ...] = ()
  matched_fields: tuple[str, ...] = ()
  semantic_concepts: tuple[str, ...] = ()
  operator_hits: tuple[str, ...] = ()
  note: str | None = None
  ranking_reason: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPlanRecord:
  plan_id: str
  created_at: datetime
  updated_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  status: str = "previewed"
  queue_state: str = "pending_approval"
  policy_catalog_id: str | None = None
  policy_catalog_name: str | None = None
  proposed_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  requested_feedback_ids: tuple[str, ...] = ()
  feedback_ids: tuple[str, ...] = ()
  missing_feedback_ids: tuple[str, ...] = ()
  preview_items: tuple[ProviderProvenanceSchedulerSearchModerationPlanPreviewItem, ...] = ()
  created_by: str = "operator"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approved_by_tab_id: str | None = None
  approved_by_tab_label: str | None = None
  approval_note: str | None = None
  applied_at: datetime | None = None
  applied_by: str | None = None
  applied_by_tab_id: str | None = None
  applied_by_tab_label: str | None = None
  apply_note: str | None = None
  applied_result: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
  governance_policy_id: str
  created_at: datetime
  updated_at: datetime
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
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
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
  revision_id: str
  governance_policy_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
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
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
  audit_id: str
  governance_policy_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str
  scheduler_key: str = "provider_provenance_reports"
  revision_id: str | None = None
  source_revision_id: str | None = None
  name: str = ""
  status: str = "active"
  action_scope: str = "any"
  require_approval_note: bool = False
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem:
  catalog_id: str
  catalog_name: str
  action: str
  current_status: str
  current_revision_id: str | None = None
  rollback_revision_id: str | None = None
  outcome: str = "changed"
  message: str | None = None
  changed_fields: tuple[str, ...] = ()
  field_diffs: dict[str, dict[str, Any]] = field(default_factory=dict)
  current_snapshot: dict[str, Any] = field(default_factory=dict)
  proposed_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
  plan_id: str
  created_at: datetime
  updated_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  action: str = "update"
  status: str = "previewed"
  queue_state: str = "pending_approval"
  governance_policy_id: str | None = None
  governance_policy_name: str | None = None
  require_approval_note: bool = False
  guidance: str | None = None
  requested_catalog_ids: tuple[str, ...] = ()
  preview_items: tuple[
    ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem,
    ...,
  ] = ()
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  created_by: str = "operator"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approved_by_tab_id: str | None = None
  approved_by_tab_label: str | None = None
  approval_note: str | None = None
  applied_at: datetime | None = None
  applied_by: str | None = None
  applied_by_tab_id: str | None = None
  applied_by_tab_label: str | None = None
  apply_note: str | None = None
  applied_result: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
  meta_policy_id: str
  created_at: datetime
  updated_at: datetime
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
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


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem:
  governance_policy_id: str
  governance_policy_name: str
  action: str
  current_status: str
  current_revision_id: str | None = None
  rollback_revision_id: str | None = None
  outcome: str = "changed"
  message: str | None = None
  changed_fields: tuple[str, ...] = ()
  field_diffs: dict[str, dict[str, Any]] = field(default_factory=dict)
  current_snapshot: dict[str, Any] = field(default_factory=dict)
  proposed_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
  plan_id: str
  created_at: datetime
  updated_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  action: str = "update"
  status: str = "previewed"
  queue_state: str = "pending_approval"
  meta_policy_id: str | None = None
  meta_policy_name: str | None = None
  require_approval_note: bool = False
  guidance: str | None = None
  requested_governance_policy_ids: tuple[str, ...] = ()
  preview_items: tuple[
    ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem,
    ...,
  ] = ()
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
  created_by: str = "operator"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approved_by_tab_id: str | None = None
  approved_by_tab_label: str | None = None
  approval_note: str | None = None
  applied_at: datetime | None = None
  applied_by: str | None = None
  applied_by_tab_id: str | None = None
  applied_by_tab_label: str | None = None
  apply_note: str | None = None
  applied_result: dict[str, Any] | None = None


