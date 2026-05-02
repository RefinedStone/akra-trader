import type {
  ProviderProvenanceAnalyticsWorkspaceQuery,
  ProviderProvenanceDashboardLayout,
  ProviderProvenanceWorkspaceFocus,
} from "./providerProvenanceAnalytics";
import type { ProviderProvenanceExportJobEntry } from "./providerProvenanceExports";

export type ProviderProvenanceScheduledReportEntry = {
  report_id: string;
  name: string;
  description: string;
  preset_id?: string | null;
  view_id?: string | null;
  cadence: "daily" | "weekly";
  status: "scheduled" | "paused";
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
  created_at: string;
  updated_at: string;
  next_run_at?: string | null;
  last_run_at?: string | null;
  last_export_job_id?: string | null;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
};

export type ProviderProvenanceScheduledReportListPayload = {
  items: ProviderProvenanceScheduledReportEntry[];
  total: number;
};

export type ProviderProvenanceScheduledReportAuditRecord = {
  audit_id: string;
  report_id: string;
  action: string;
  recorded_at: string;
  expires_at?: string | null;
  source_tab_id?: string | null;
  source_tab_label?: string | null;
  export_job_id?: string | null;
  detail: string;
};

export type ProviderProvenanceScheduledReportHistoryPayload = {
  report: ProviderProvenanceScheduledReportEntry;
  history: ProviderProvenanceScheduledReportAuditRecord[];
};

export type ProviderProvenanceScheduledReportRunResult = {
  report: ProviderProvenanceScheduledReportEntry;
  export_job: ProviderProvenanceExportJobEntry;
};

export type ProviderProvenanceScheduledReportRunDuePayload = {
  generated_at: string;
  due_before: string;
  executed_count: number;
  items: ProviderProvenanceScheduledReportRunResult[];
};

// Runtime placeholders for generated barrel compatibility.
export const ProviderProvenanceScheduledReportEntry = undefined;
export const ProviderProvenanceScheduledReportListPayload = undefined;
export const ProviderProvenanceScheduledReportAuditRecord = undefined;
export const ProviderProvenanceScheduledReportHistoryPayload = undefined;
export const ProviderProvenanceScheduledReportRunResult = undefined;
export const ProviderProvenanceScheduledReportRunDuePayload = undefined;
