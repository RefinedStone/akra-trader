export type ProviderProvenanceExportJobEntry = {
  job_id: string;
  export_scope: string;
  export_format: string;
  filename: string;
  content_type: string;
  status: string;
  created_at: string;
  completed_at?: string | null;
  exported_at?: string | null;
  expires_at?: string | null;
  focus_key?: string | null;
  focus_label?: string | null;
  market_data_provider?: string | null;
  venue?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  result_count: number;
  provider_provenance_count: number;
  provider_labels: string[];
  vendor_fields: string[];
  filter_summary?: string | null;
  filters: Record<string, unknown>;
  requested_by_tab_id?: string | null;
  requested_by_tab_label?: string | null;
  available_delivery_targets: string[];
  routing_policy_id?: string | null;
  routing_policy_summary?: string | null;
  routing_targets: string[];
  approval_policy_id?: string | null;
  approval_required: boolean;
  approval_state: string;
  approval_summary?: string | null;
  approved_at?: string | null;
  approved_by?: string | null;
  approval_note?: string | null;
  escalation_count: number;
  last_escalated_at?: string | null;
  last_escalated_by?: string | null;
  last_escalation_reason?: string | null;
  last_delivery_targets: string[];
  last_delivery_status?: string | null;
  last_delivery_summary?: string | null;
  artifact_id?: string | null;
  content_length: number;
  content?: string;
};

export type ProviderProvenanceExportJobAuditRecord = {
  audit_id: string;
  job_id: string;
  action: string;
  recorded_at: string;
  expires_at?: string | null;
  export_scope?: string | null;
  export_format?: string | null;
  focus_key?: string | null;
  focus_label?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  market_data_provider?: string | null;
  requested_by_tab_id?: string | null;
  requested_by_tab_label?: string | null;
  source_tab_id?: string | null;
  source_tab_label?: string | null;
  routing_policy_id?: string | null;
  routing_targets: string[];
  approval_policy_id?: string | null;
  approval_required: boolean;
  approval_state?: string | null;
  approval_summary?: string | null;
  approved_by?: string | null;
  delivery_targets: string[];
  delivery_status?: string | null;
  delivery_summary?: string | null;
  detail: string;
};

export type ProviderProvenanceExportJobListPayload = {
  items: ProviderProvenanceExportJobEntry[];
  total: number;
};

export type ProviderProvenanceExportJobHistoryPayload = {
  job: ProviderProvenanceExportJobEntry;
  history: ProviderProvenanceExportJobAuditRecord[];
};

export type ProviderProvenanceExportJobEscalationResult = {
  export_job: ProviderProvenanceExportJobEntry;
  audit_record: ProviderProvenanceExportJobAuditRecord;
  delivery_history: {
    delivery_id: string;
    incident_event_id: string;
    alert_id: string;
    incident_kind: string;
    target: string;
    status: string;
    attempted_at: string;
    detail: string;
    attempt_number: number;
    next_retry_at?: string | null;
    phase: string;
    provider_action?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    source: string;
  }[];
};

export type ProviderProvenanceExportJobPolicyResult = {
  export_job: ProviderProvenanceExportJobEntry;
  audit_record: ProviderProvenanceExportJobAuditRecord;
};

export type ProviderProvenanceExportAnalyticsRollupEntry = {
  key: string;
  label: string;
  export_count: number;
  result_count: number;
  provider_provenance_count: number;
  download_count: number;
  focus_count: number;
  requested_by_tab_count: number;
  provider_labels: string[];
  vendor_fields: string[];
  last_exported_at?: string | null;
  last_downloaded_at?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  market_data_provider?: string | null;
  venue?: string | null;
};

export type ProviderProvenanceExportDriftSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  export_count: number;
  result_count: number;
  provider_provenance_count: number;
  focus_count: number;
  provider_label_count: number;
  provider_labels: string[];
  vendor_fields: string[];
  drift_intensity: number;
};

export type ProviderProvenanceExportBurnUpSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  export_count: number;
  result_count: number;
  provider_provenance_count: number;
  download_count: number;
  cumulative_export_count: number;
  cumulative_result_count: number;
  cumulative_provider_provenance_count: number;
  cumulative_download_count: number;
};

export type ProviderProvenanceExportTimeSeriesPayload = {
  bucket_size: string;
  window_days: number;
  window_started_at: string;
  window_ended_at: string;
  provider_drift: {
    series: ProviderProvenanceExportDriftSeriesEntry[];
    summary: {
      peak_bucket_key?: string | null;
      peak_bucket_label?: string | null;
      peak_export_count: number;
      peak_provider_provenance_count: number;
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      latest_export_count: number;
      latest_provider_provenance_count: number;
    };
  };
  export_burn_up: {
    series: ProviderProvenanceExportBurnUpSeriesEntry[];
    summary: {
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      cumulative_export_count: number;
      cumulative_result_count: number;
      cumulative_provider_provenance_count: number;
      cumulative_download_count: number;
    };
  };
};

export type ProviderProvenanceExportAnalyticsPayload = {
  generated_at: string;
  query: {
    focus_key?: string | null;
    symbol?: string | null;
    timeframe?: string | null;
    provider_label?: string | null;
    vendor_field?: string | null;
    market_data_provider?: string | null;
    venue?: string | null;
    requested_by_tab_id?: string | null;
    status?: string | null;
    search?: string | null;
    result_limit: number;
    window_days: number;
  };
  totals: {
    export_count: number;
    result_count: number;
    provider_provenance_count: number;
    download_count: number;
    unique_focus_count: number;
    provider_label_count: number;
    vendor_field_count: number;
    market_data_provider_count: number;
    requester_count: number;
  };
  available_filters: {
    provider_labels: string[];
    vendor_fields: string[];
    market_data_providers: string[];
    venues: string[];
    timeframes: string[];
    requested_by_tab_ids: string[];
    statuses: string[];
  };
  rollups: {
    providers: ProviderProvenanceExportAnalyticsRollupEntry[];
    vendor_fields: ProviderProvenanceExportAnalyticsRollupEntry[];
    focuses: ProviderProvenanceExportAnalyticsRollupEntry[];
    requesters: ProviderProvenanceExportAnalyticsRollupEntry[];
  };
  time_series: ProviderProvenanceExportTimeSeriesPayload;
  recent_exports: ProviderProvenanceExportJobEntry[];
};
