export type ProviderProvenanceAnalyticsWorkspaceQuery = {
  focus_scope: "current_focus" | "all_focuses";
  focus_key?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  provider_label?: string | null;
  vendor_field?: string | null;
  market_data_provider?: string | null;
  venue?: string | null;
  requested_by_tab_id?: string | null;
  status?: string | null;
  scheduler_alert_category?: string | null;
  scheduler_alert_status?: string | null;
  scheduler_alert_narrative_facet?: string | null;
  search?: string | null;
  result_limit: number;
  window_days: number;
};

export type ProviderProvenanceDashboardLayout = {
  highlight_panel:
    | "overview"
    | "drift"
    | "burn_up"
    | "rollups"
    | "recent_exports"
    | "scheduler_alerts";
  show_rollups: boolean;
  show_time_series: boolean;
  show_recent_exports: boolean;
  governance_queue_view?: ProviderProvenanceSchedulerNarrativeGovernanceQueueView | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceQueueView = {
  queue_state?: "pending_approval" | "ready_to_apply" | "completed" | string | null;
  item_type?: "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string | null;
  approval_lane?: string | null;
  approval_priority?: string | null;
  policy_template_id?: string | null;
  policy_catalog_id?: string | null;
  source_hierarchy_step_template_id?: string | null;
  source_hierarchy_step_template_name?: string | null;
  search?: string | null;
  sort?: string | null;
};

export type ProviderProvenanceWorkspaceFocus = {
  provider?: string | null;
  venue?: string | null;
  instrument_id?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  provider_provenance_incident_count?: number;
};

export type ProviderProvenanceAnalyticsPresetEntry = {
  preset_id: string;
  name: string;
  description: string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  created_at: string;
  updated_at: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
};

export type ProviderProvenanceAnalyticsPresetListPayload = {
  items: ProviderProvenanceAnalyticsPresetEntry[];
  total: number;
};

export type ProviderProvenanceDashboardViewEntry = {
  view_id: string;
  name: string;
  description: string;
  preset_id?: string | null;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
  created_at: string;
  updated_at: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
};

export type ProviderProvenanceDashboardViewListPayload = {
  items: ProviderProvenanceDashboardViewEntry[];
  total: number;
};
