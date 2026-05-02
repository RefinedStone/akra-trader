import type {
  ProviderProvenanceAnalyticsWorkspaceQuery,
  ProviderProvenanceDashboardLayout,
  ProviderProvenanceWorkspaceFocus,
} from "./providerProvenanceAnalytics";

export type ProviderProvenanceSchedulerNarrativeTemplateEntry = {
  template_id: string;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
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

export type ProviderProvenanceSchedulerNarrativeTemplateListPayload = {
  items: ProviderProvenanceSchedulerNarrativeTemplateEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry = {
  revision_id: string;
  template_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload = {
  template: ProviderProvenanceSchedulerNarrativeTemplateEntry;
  history: ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult = {
  item_id: string;
  item_name?: string | null;
  outcome: "applied" | "skipped" | "failed" | string;
  status?: "active" | "deleted" | string | null;
  current_revision_id?: string | null;
  message?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeBulkGovernanceResult = {
  item_type: "template" | "registry" | "stitched_report_view" | string;
  action: "delete" | "restore" | string;
  reason: string;
  requested_count: number;
  applied_count: number;
  skipped_count: number;
  failed_count: number;
  results: ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult[];
};

export type ProviderProvenanceSchedulerNarrativeRegistryEntry = {
  registry_id: string;
  name: string;
  description: string;
  template_id?: string | null;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
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

export type ProviderProvenanceSchedulerNarrativeRegistryListPayload = {
  items: ProviderProvenanceSchedulerNarrativeRegistryEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry = {
  revision_id: string;
  registry_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  template_id?: string | null;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload = {
  registry: ProviderProvenanceSchedulerNarrativeRegistryEntry;
  history: ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry[];
};

// Runtime placeholders for generated barrel compatibility.
export const ProviderProvenanceSchedulerNarrativeTemplateEntry = undefined;
export const ProviderProvenanceSchedulerNarrativeTemplateListPayload = undefined;
export const ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry = undefined;
export const ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload = undefined;
export const ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult = undefined;
export const ProviderProvenanceSchedulerNarrativeBulkGovernanceResult = undefined;
export const ProviderProvenanceSchedulerNarrativeRegistryEntry = undefined;
export const ProviderProvenanceSchedulerNarrativeRegistryListPayload = undefined;
export const ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry = undefined;
export const ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload = undefined;
