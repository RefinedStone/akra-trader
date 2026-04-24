import type { ProviderProvenanceSchedulerNarrativeBulkGovernanceResult } from "./providerProvenanceSchedulerNarrativeAssets";

export type ProviderProvenanceSchedulerNarrativeGovernancePreviewItem = {
  item_id: string;
  item_name?: string | null;
  status?: "active" | "deleted" | string | null;
  current_revision_id?: string | null;
  apply_revision_id?: string | null;
  rollback_revision_id?: string | null;
  outcome: "changed" | "skipped" | "failed" | string;
  message?: string | null;
  changed_fields: string[];
  field_diffs: Record<string, { before?: unknown; after?: unknown }>;
  current_snapshot: Record<string, unknown>;
  proposed_snapshot: Record<string, unknown>;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate = {
  policy_template_id: string;
  name: string;
  description: string;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  status: "active" | "deleted" | string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry = {
  revision_id: string;
  policy_template_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  status: "active" | "deleted" | string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload = {
  policy_template: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate;
  history: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord = {
  audit_id: string;
  policy_template_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  status: "active" | "deleted" | string;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog = {
  catalog_id: string;
  name: string;
  description: string;
  policy_template_ids: string[];
  policy_template_names: string[];
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  hierarchy_steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[];
  status: "active" | "deleted" | string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry = {
  revision_id: string;
  catalog_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  policy_template_ids: string[];
  policy_template_names: string[];
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  hierarchy_steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[];
  status: "active" | "deleted" | string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload = {
  current: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog;
  history: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord = {
  audit_id: string;
  catalog_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  status: "active" | "deleted" | string;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  policy_template_ids: string[];
  policy_template_names: string[];
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  hierarchy_steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[];
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate = {
  hierarchy_step_template_id: string;
  name: string;
  description: string;
  item_type: "template" | "registry" | string;
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep;
  origin_catalog_id?: string | null;
  origin_catalog_name?: string | null;
  origin_step_id?: string | null;
  governance_policy_template_id?: string | null;
  governance_policy_template_name?: string | null;
  governance_policy_catalog_id?: string | null;
  governance_policy_catalog_name?: string | null;
  governance_approval_lane?: string | null;
  governance_approval_priority?: string | null;
  governance_policy_guidance?: string | null;
  status: "active" | "deleted" | string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry = {
  revision_id: string;
  hierarchy_step_template_id: string;
  action: string;
  reason: string;
  name: string;
  description: string;
  item_type: "template" | "registry" | string;
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep;
  origin_catalog_id?: string | null;
  origin_catalog_name?: string | null;
  origin_step_id?: string | null;
  governance_policy_template_id?: string | null;
  governance_policy_template_name?: string | null;
  governance_policy_catalog_id?: string | null;
  governance_policy_catalog_name?: string | null;
  governance_approval_lane?: string | null;
  governance_approval_priority?: string | null;
  governance_policy_guidance?: string | null;
  status: "active" | "deleted" | string;
  recorded_at: string;
  source_revision_id?: string | null;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload = {
  current: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate;
  history: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord = {
  audit_id: string;
  hierarchy_step_template_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  description: string;
  item_type: "template" | "registry" | string;
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep;
  origin_catalog_id?: string | null;
  origin_catalog_name?: string | null;
  origin_step_id?: string | null;
  governance_policy_template_id?: string | null;
  governance_policy_template_name?: string | null;
  governance_policy_catalog_id?: string | null;
  governance_policy_catalog_name?: string | null;
  governance_approval_lane?: string | null;
  governance_approval_priority?: string | null;
  governance_policy_guidance?: string | null;
  status: "active" | "deleted" | string;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep = {
  step_id?: string | null;
  source_template_id?: string | null;
  source_template_name?: string | null;
  item_type: "template" | "registry" | string;
  action: "update" | string;
  item_ids: string[];
  item_names: string[];
  name_prefix?: string | null;
  name_suffix?: string | null;
  description_append?: string | null;
  query_patch: Record<string, unknown>;
  layout_patch: Record<string, unknown>;
  template_id?: string | null;
  clear_template_link: boolean;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlan = {
  plan_id: string;
  item_type: "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action: "delete" | "restore" | "update" | "rollback" | string;
  reason: string;
  status: "previewed" | "approved" | "applied" | "rolled_back" | string;
  queue_state: "pending_approval" | "ready_to_apply" | "completed" | string;
  policy_template_id?: string | null;
  policy_template_name?: string | null;
  policy_catalog_id?: string | null;
  policy_catalog_name?: string | null;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  policy_guidance?: string | null;
  source_hierarchy_step_template_id?: string | null;
  source_hierarchy_step_template_name?: string | null;
  hierarchy_key?: string | null;
  hierarchy_name?: string | null;
  hierarchy_position?: number | null;
  hierarchy_total?: number | null;
  request_payload: Record<string, unknown>;
  target_ids: string[];
  preview_requested_count: number;
  preview_changed_count: number;
  preview_skipped_count: number;
  preview_failed_count: number;
  preview_items: ProviderProvenanceSchedulerNarrativeGovernancePreviewItem[];
  rollback_ready_count: number;
  rollback_summary: string;
  created_at: string;
  updated_at: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  approved_at?: string | null;
  approved_by_tab_id?: string | null;
  approved_by_tab_label?: string | null;
  approval_note?: string | null;
  applied_at?: string | null;
  applied_by_tab_id?: string | null;
  applied_by_tab_label?: string | null;
  applied_result?: ProviderProvenanceSchedulerNarrativeBulkGovernanceResult | null;
  rolled_back_at?: string | null;
  rolled_back_by_tab_id?: string | null;
  rolled_back_by_tab_label?: string | null;
  rollback_note?: string | null;
  rollback_result?: ProviderProvenanceSchedulerNarrativeBulkGovernanceResult | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePlan[];
  total: number;
  pending_approval_count: number;
  ready_to_apply_count: number;
  completed_count: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult = {
  plan_id: string;
  action: string;
  outcome: "succeeded" | "skipped" | "failed" | string;
  status?: string | null;
  queue_state?: string | null;
  message?: string | null;
  plan?: ProviderProvenanceSchedulerNarrativeGovernancePlan | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult = {
  action: string;
  requested_count: number;
  succeeded_count: number;
  skipped_count: number;
  failed_count: number;
  results: ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult[];
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult = {
  catalog_id: string;
  catalog_name: string;
  hierarchy_key: string;
  hierarchy_name: string;
  plan_count: number;
  summary: string;
  plans: ProviderProvenanceSchedulerNarrativeGovernancePlan[];
};
