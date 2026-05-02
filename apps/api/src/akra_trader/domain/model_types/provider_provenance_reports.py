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
