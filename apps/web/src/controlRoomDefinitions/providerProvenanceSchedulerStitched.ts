import type {
  ProviderProvenanceAnalyticsWorkspaceQuery,
  ProviderProvenanceSchedulerNarrativeGovernanceQueueView,
  ProviderProvenanceWorkspaceFocus,
} from "./providerProvenanceAnalytics";

export type ProviderProvenanceSchedulerStitchedReportViewEntry = {
  view_id: string;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  occurrence_limit: number;
  history_limit: number;
  drilldown_history_limit: number;
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

export type ProviderProvenanceSchedulerStitchedReportViewListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportViewEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerStitchedReportViewRevisionEntry = {
  revision_id: string;
  view_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  occurrence_limit: number;
  history_limit: number;
  drilldown_history_limit: number;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload = {
  view: ProviderProvenanceSchedulerStitchedReportViewEntry;
  history: ProviderProvenanceSchedulerStitchedReportViewRevisionEntry[];
};

export type ProviderProvenanceSchedulerStitchedReportViewAuditRecord = {
  audit_id: string;
  view_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  status: "active" | "deleted" | string;
  occurrence_limit: number;
  history_limit: number;
  drilldown_history_limit: number;
  filter_summary: string;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportViewAuditListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportViewAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry = {
  registry_id: string;
  name: string;
  description: string;
  queue_view: ProviderProvenanceSchedulerNarrativeGovernanceQueueView;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  default_policy_catalog_id?: string | null;
  default_policy_catalog_name?: string | null;
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

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry = {
  revision_id: string;
  registry_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  queue_view: ProviderProvenanceSchedulerNarrativeGovernanceQueueView;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  default_policy_catalog_id?: string | null;
  default_policy_catalog_name?: string | null;
  status: "active" | "deleted" | string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload = {
  registry: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry;
  history: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry[];
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord = {
  audit_id: string;
  registry_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  description: string;
  queue_view: ProviderProvenanceSchedulerNarrativeGovernanceQueueView;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  default_policy_catalog_id?: string | null;
  default_policy_catalog_name?: string | null;
  status: "active" | "deleted" | string;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord[];
  total: number;
};
