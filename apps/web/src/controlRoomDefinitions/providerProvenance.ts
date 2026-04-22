import type { OperatorAlertEntry } from "../controlRoomDefinitions";

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

export type ProviderProvenanceSchedulerHealthSnapshot = {
  generated_at: string;
  enabled: boolean;
  status: string;
  summary: string;
  interval_seconds: number;
  batch_limit: number;
  last_cycle_started_at?: string | null;
  last_cycle_finished_at?: string | null;
  last_success_at?: string | null;
  last_failure_at?: string | null;
  last_error?: string | null;
  cycle_count: number;
  success_count: number;
  failure_count: number;
  consecutive_failure_count: number;
  last_executed_count: number;
  total_executed_count: number;
  due_report_count: number;
  oldest_due_at?: string | null;
  max_due_lag_seconds: number;
  issues: string[];
};

export type ProviderProvenanceSchedulerHealthHistoryEntry = {
  record_id: string;
  scheduler_key: string;
  recorded_at: string;
  expires_at?: string | null;
  enabled: boolean;
  status: string;
  summary: string;
  interval_seconds: number;
  batch_limit: number;
  last_cycle_started_at?: string | null;
  last_cycle_finished_at?: string | null;
  last_success_at?: string | null;
  last_failure_at?: string | null;
  last_error?: string | null;
  cycle_count: number;
  success_count: number;
  failure_count: number;
  consecutive_failure_count: number;
  last_executed_count: number;
  total_executed_count: number;
  due_report_count: number;
  oldest_due_at?: string | null;
  max_due_lag_seconds: number;
  source_tab_id?: string | null;
  source_tab_label?: string | null;
  issues: string[];
};

export type ProviderProvenanceSchedulerHealthHistoryPayload = {
  generated_at: string;
  query: {
    status?: string | null;
    limit: number;
    offset: number;
  };
  current: ProviderProvenanceSchedulerHealthSnapshot;
  items: ProviderProvenanceSchedulerHealthHistoryEntry[];
  total: number;
  returned: number;
  has_more: boolean;
  next_offset?: number | null;
  previous_offset?: number | null;
};

export type ProviderProvenanceSchedulerAlertHistoryPayload = {
  generated_at: string;
  query: {
    category?: string | null;
    status?: string | null;
    narrative_facet?: string | null;
    search?: string | null;
    limit: number;
    offset: number;
  };
  available_filters: {
    categories: string[];
    statuses: string[];
    narrative_facets: string[];
  };
  summary: {
    total_occurrences: number;
    active_count: number;
    resolved_count: number;
    by_category: {
      category: string;
      total: number;
      active_count: number;
      resolved_count: number;
    }[];
  };
  retrieval_clusters: {
    cluster_id?: string | null;
    rank: number;
    label?: string | null;
    summary?: string | null;
    occurrence_count: number;
    top_score: number;
    average_score: number;
    average_similarity_pct: number;
    semantic_concepts: string[];
    vector_terms: string[];
    categories: string[];
    statuses: string[];
    narrative_facets: string[];
    top_occurrence_id?: string | null;
    top_occurrence_summary?: string | null;
    occurrence_ids: string[];
  }[];
  search_summary?: {
    query_id?: string | null;
    query?: string | null;
    mode?: string | null;
    token_count: number;
    matched_occurrences: number;
    top_score: number;
    max_term_coverage_pct: number;
    phrase_match_count: number;
    operator_count: number;
    semantic_concept_count: number;
    negated_term_count: number;
    boolean_operator_count: number;
    indexed_occurrence_count: number;
    indexed_term_count: number;
    persistence_mode?: string | null;
    relevance_model?: string | null;
    retrieval_cluster_mode?: string | null;
    retrieval_cluster_count: number;
    top_cluster_label?: string | null;
    parsed_terms: string[];
    parsed_phrases: string[];
    parsed_operators: string[];
    semantic_concepts: string[];
    query_plan: string[];
  } | null;
  search_analytics?: {
    query_id: string;
    recorded_at: string;
    recent_query_count: number;
    feedback_count: number;
    pending_feedback_count: number;
    approved_feedback_count: number;
    rejected_feedback_count: number;
    relevant_feedback_count: number;
    not_relevant_feedback_count: number;
    helpful_feedback_ratio_pct: number;
    learned_relevance_active: boolean;
    tuning_profile_version?: string | null;
    tuned_feature_count: number;
    channel_adjustments: {
      lexical: number;
      semantic: number;
      operator: number;
    };
    top_field_adjustments: {
      field: string;
      score: number;
    }[];
    top_semantic_adjustments: {
      concept: string;
      score: number;
    }[];
    top_operator_adjustments: {
      operator: string;
      score: number;
    }[];
    recent_queries: {
      query_id: string;
      recorded_at: string;
      query: string;
      matched_occurrences: number;
      top_score: number;
      relevance_model?: string | null;
    }[];
    recent_feedback: {
      feedback_id: string;
      recorded_at: string;
      occurrence_id: string;
      signal: string;
      moderation_status: string;
      matched_fields: string[];
      semantic_concepts: string[];
      operator_hits: string[];
      note?: string | null;
      moderation_note?: string | null;
    }[];
  } | null;
  items: (OperatorAlertEntry & {
    narrative: {
      facet?: string | null;
      facet_flags: string[];
      narrative_mode?: string | null;
      can_reconstruct_narrative: boolean;
      has_post_resolution_history: boolean;
      occurrence_record_count: number;
      post_resolution_record_count: number;
      status_sequence: string[];
      post_resolution_status_sequence: string[];
      narrative_window_ended_at?: string | null;
      next_occurrence_detected_at?: string | null;
    };
    search_match?: {
      score: number;
      matched_terms: string[];
      matched_phrases: string[];
      matched_fields: string[];
      term_coverage_pct: number;
      phrase_match: boolean;
      exact_match: boolean;
      highlights: string[];
      semantic_concepts: string[];
      operator_hits: string[];
      lexical_score: number;
      semantic_score: number;
      operator_score: number;
      learned_score: number;
      feedback_signal_count: number;
      tuning_signals: string[];
      relevance_model?: string | null;
      ranking_reason?: string | null;
    } | null;
    retrieval_cluster?: {
      cluster_id?: string | null;
      rank: number;
      label?: string | null;
      similarity_pct: number;
      semantic_concepts: string[];
      vector_terms: string[];
    } | null;
  })[];
  total: number;
  returned: number;
  has_more: boolean;
  next_offset?: number | null;
  previous_offset?: number | null;
};

export type ProviderProvenanceSchedulerSearchFeedbackResult = {
  feedback_id: string;
  query_id: string;
  query: string;
  occurrence_id: string;
  signal: string;
  moderation_status: string;
  feedback_count: number;
  pending_feedback_count: number;
  approved_feedback_count: number;
  rejected_feedback_count: number;
  relevant_feedback_count: number;
  not_relevant_feedback_count: number;
  helpful_feedback_ratio_pct: number;
  learned_relevance_hint?: string | null;
};

export type ProviderProvenanceSchedulerSearchFeedbackModerationResult = {
  feedback_id: string;
  query_id: string;
  occurrence_id: string;
  moderation_status: string;
  moderated_at?: string | null;
  moderated_by?: string | null;
  moderation_note?: string | null;
  pending_feedback_count: number;
  approved_feedback_count: number;
  rejected_feedback_count: number;
  learned_relevance_hint?: string | null;
};

export type ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult = {
  moderation_status: string;
  requested_count: number;
  updated_count: number;
  missing_count: number;
  results: {
    feedback_id: string;
    outcome: string;
    moderation_status?: string | null;
    moderated_at?: string | null;
    moderated_by?: string | null;
    message?: string | null;
  }[];
  learned_relevance_hint?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry = {
  catalog_id: string;
  created_at: string;
  updated_at: string;
  scheduler_key: string;
  name: string;
  description: string;
  status: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload = {
  generated_at: string;
  total: number;
  items: ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry[];
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionEntry = {
  revision_id: string;
  catalog_id: string;
  action: string;
  reason: string;
  name: string;
  description: string;
  scheduler_key: string;
  status: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  recorded_at: string;
  source_revision_id?: string | null;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload = {
  catalog: ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry;
  history: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionEntry[];
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord = {
  audit_id: string;
  catalog_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  scheduler_key: string;
  name: string;
  status: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditListPayload = {
  items: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerSearchModerationPlanPreviewItem = {
  feedback_id: string;
  occurrence_id: string;
  query: string;
  signal: string;
  current_moderation_status: string;
  proposed_moderation_status: string;
  score: number;
  age_hours: number;
  stale_pending: boolean;
  high_score_pending: boolean;
  query_run_count: number;
  eligible: boolean;
  reason_tags: string[];
  matched_fields: string[];
  semantic_concepts: string[];
  operator_hits: string[];
  note?: string | null;
  ranking_reason?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationPlanEntry = {
  plan_id: string;
  created_at: string;
  updated_at: string;
  scheduler_key: string;
  status: string;
  queue_state: string;
  policy_catalog_id?: string | null;
  policy_catalog_name?: string | null;
  proposed_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  requested_feedback_ids: string[];
  feedback_ids: string[];
  missing_feedback_ids: string[];
  preview_count: number;
  preview_items: ProviderProvenanceSchedulerSearchModerationPlanPreviewItem[];
  created_by: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  approved_at?: string | null;
  approved_by?: string | null;
  approved_by_tab_id?: string | null;
  approved_by_tab_label?: string | null;
  approval_note?: string | null;
  applied_at?: string | null;
  applied_by?: string | null;
  applied_by_tab_id?: string | null;
  applied_by_tab_label?: string | null;
  apply_note?: string | null;
  applied_result?: ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult | null;
};

export type ProviderProvenanceSchedulerSearchModerationPlanListPayload = {
  generated_at: string;
  query: {
    queue_state?: string | null;
    policy_catalog_id?: string | null;
  };
  available_filters: {
    queue_states: string[];
    policy_catalogs: {
      catalog_id: string;
      name: string;
    }[];
  };
  summary: {
    total: number;
    pending_approval_count: number;
    ready_to_apply_count: number;
    completed_count: number;
  };
  items: ProviderProvenanceSchedulerSearchModerationPlanEntry[];
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry = {
  governance_policy_id: string;
  created_at: string;
  updated_at: string;
  scheduler_key: string;
  name: string;
  description: string;
  status: string;
  action_scope: string;
  require_approval_note: boolean;
  guidance?: string | null;
  name_prefix?: string | null;
  name_suffix?: string | null;
  description_append?: string | null;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload = {
  generated_at: string;
  query: {
    action_scope?: string | null;
    search?: string | null;
    limit: number;
  };
  available_filters: {
    action_scopes: string[];
  };
  total: number;
  items: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry[];
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionEntry = {
  revision_id: string;
  governance_policy_id: string;
  action: string;
  reason: string;
  name: string;
  description: string;
  scheduler_key: string;
  status: string;
  action_scope: string;
  require_approval_note: boolean;
  guidance?: string | null;
  name_prefix?: string | null;
  name_suffix?: string | null;
  description_append?: string | null;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  recorded_at: string;
  source_revision_id?: string | null;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload = {
  policy: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry;
  history: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionEntry[];
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord = {
  audit_id: string;
  governance_policy_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  scheduler_key: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  status: string;
  action_scope: string;
  require_approval_note: boolean;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload = {
  items: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem = {
  catalog_id: string;
  catalog_name: string;
  action: string;
  current_status: string;
  current_revision_id?: string | null;
  rollback_revision_id?: string | null;
  outcome: string;
  message?: string | null;
  changed_fields: string[];
  field_diffs: Record<string, { before: unknown; after: unknown }>;
  current_snapshot: Record<string, unknown>;
  proposed_snapshot: Record<string, unknown>;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanEntry = {
  plan_id: string;
  created_at: string;
  updated_at: string;
  scheduler_key: string;
  action: string;
  status: string;
  queue_state: string;
  governance_policy_id?: string | null;
  governance_policy_name?: string | null;
  require_approval_note: boolean;
  guidance?: string | null;
  requested_catalog_ids: string[];
  preview_count: number;
  preview_items: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem[];
  name_prefix?: string | null;
  name_suffix?: string | null;
  description_append?: string | null;
  default_moderation_status?: string | null;
  governance_view?: string | null;
  window_days?: number | null;
  stale_pending_hours?: number | null;
  minimum_score?: number | null;
  require_note?: boolean | null;
  created_by: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  approved_at?: string | null;
  approved_by?: string | null;
  approved_by_tab_id?: string | null;
  approved_by_tab_label?: string | null;
  approval_note?: string | null;
  applied_at?: string | null;
  applied_by?: string | null;
  applied_by_tab_id?: string | null;
  applied_by_tab_label?: string | null;
  apply_note?: string | null;
  applied_result?: {
    requested_count: number;
    applied_count: number;
    skipped_count: number;
    failed_count: number;
    results: Array<Record<string, unknown>>;
  } | null;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload = {
  generated_at: string;
  query: {
    queue_state?: string | null;
    governance_policy_id?: string | null;
  };
  available_filters: {
    queue_states: string[];
    governance_policies: {
      governance_policy_id: string;
      name: string;
      action_scope: string;
    }[];
  };
  summary: {
    total: number;
    pending_approval_count: number;
    ready_to_apply_count: number;
    completed_count: number;
  };
  items: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanEntry[];
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry = {
  meta_policy_id: string;
  created_at: string;
  updated_at: string;
  scheduler_key: string;
  status: string;
  name: string;
  description: string;
  action_scope: string;
  require_approval_note: boolean;
  guidance?: string | null;
  name_prefix?: string | null;
  name_suffix?: string | null;
  description_append?: string | null;
  policy_action_scope?: string | null;
  policy_require_approval_note?: boolean | null;
  policy_guidance?: string | null;
  default_moderation_status?: string | null;
  governance_view?: string | null;
  window_days?: number | null;
  stale_pending_hours?: number | null;
  minimum_score?: number | null;
  require_note?: boolean | null;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload = {
  generated_at: string;
  query: {
    action_scope?: string | null;
    search?: string | null;
    limit: number;
  };
  available_filters: {
    action_scopes: string[];
  };
  total: number;
  items: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry[];
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem = {
  governance_policy_id: string;
  governance_policy_name: string;
  action: string;
  current_status: string;
  current_revision_id?: string | null;
  rollback_revision_id?: string | null;
  outcome: string;
  message?: string | null;
  changed_fields: string[];
  field_diffs: Record<string, { before: unknown; after: unknown }>;
  current_snapshot: Record<string, unknown>;
  proposed_snapshot: Record<string, unknown>;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry = {
  plan_id: string;
  created_at: string;
  updated_at: string;
  scheduler_key: string;
  action: string;
  status: string;
  queue_state: string;
  meta_policy_id?: string | null;
  meta_policy_name?: string | null;
  require_approval_note: boolean;
  guidance?: string | null;
  requested_governance_policy_ids: string[];
  preview_count: number;
  preview_items: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem[];
  name_prefix?: string | null;
  name_suffix?: string | null;
  description_append?: string | null;
  policy_action_scope?: string | null;
  policy_require_approval_note?: boolean | null;
  policy_guidance?: string | null;
  default_moderation_status?: string | null;
  governance_view?: string | null;
  window_days?: number | null;
  stale_pending_hours?: number | null;
  minimum_score?: number | null;
  require_note?: boolean | null;
  created_by: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  approved_at?: string | null;
  approved_by?: string | null;
  approved_by_tab_id?: string | null;
  approved_by_tab_label?: string | null;
  approval_note?: string | null;
  applied_at?: string | null;
  applied_by?: string | null;
  applied_by_tab_id?: string | null;
  applied_by_tab_label?: string | null;
  apply_note?: string | null;
  applied_result?: {
    requested_count: number;
    applied_count: number;
    skipped_count: number;
    failed_count: number;
    results: Array<Record<string, unknown>>;
  } | null;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload = {
  generated_at: string;
  query: {
    queue_state?: string | null;
    meta_policy_id?: string | null;
  };
  available_filters: {
    queue_states: string[];
    meta_policies: {
      meta_policy_id: string;
      name: string;
      action_scope: string;
    }[];
  };
  summary: {
    total: number;
    pending_approval_count: number;
    ready_to_apply_count: number;
    completed_count: number;
  };
  items: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry[];
};

export type ProviderProvenanceSchedulerSearchDashboardPayload = {
  generated_at: string;
  query: {
    search?: string | null;
    moderation_status?: string | null;
    signal?: string | null;
    governance_view?: string | null;
    window_days: number;
    stale_pending_hours: number;
    query_limit: number;
    feedback_limit: number;
  };
  available_filters: {
    moderation_statuses: string[];
    signals: string[];
    governance_views: string[];
  };
  summary: {
    query_count: number;
    distinct_query_count: number;
    feedback_count: number;
    pending_feedback_count: number;
    approved_feedback_count: number;
    rejected_feedback_count: number;
    relevant_feedback_count: number;
    not_relevant_feedback_count: number;
  };
  quality_dashboard: {
    window_days: number;
    window_started_at: string;
    window_ended_at: string;
    time_series: {
      bucket_key: string;
      bucket_label: string;
      started_at: string;
      ended_at: string;
      query_count: number;
      feedback_count: number;
      pending_feedback_count: number;
      approved_feedback_count: number;
      rejected_feedback_count: number;
      moderated_feedback_count: number;
      relevant_feedback_count: number;
      not_relevant_feedback_count: number;
      top_score: number;
      stale_pending_count: number;
    }[];
    actor_rollups: {
      actor: string;
      feedback_count: number;
      pending_feedback_count: number;
      approved_feedback_count: number;
      rejected_feedback_count: number;
      relevant_feedback_count: number;
      not_relevant_feedback_count: number;
    }[];
    moderator_rollups: {
      moderated_by: string;
      feedback_count: number;
      approved_feedback_count: number;
      rejected_feedback_count: number;
      pending_feedback_count: number;
      last_moderated_at?: string | null;
    }[];
  };
  moderation_governance: {
    governance_view: string;
    stale_pending_hours: number;
    high_score_pending_threshold: number;
    pending_feedback_count: number;
    stale_pending_count: number;
    high_score_pending_count: number;
    moderated_feedback_count: number;
    conflicting_query_count: number;
    approval_rate_pct: number;
  };
  top_queries: {
    query: string;
    query_ids: string[];
    search_count: number;
    last_recorded_at: string;
    top_score: number;
    matched_occurrences_total: number;
    feedback_count: number;
    pending_feedback_count: number;
    approved_feedback_count: number;
    rejected_feedback_count: number;
    semantic_concepts: string[];
    parsed_operators: string[];
    relevance_models: string[];
  }[];
  feedback_items: {
    feedback_id: string;
    recorded_at: string;
    query_id: string;
    query: string;
    occurrence_id: string;
    signal: string;
    actor?: string | null;
    note?: string | null;
    moderation_status: string;
    moderation_note?: string | null;
    moderated_at?: string | null;
    moderated_by?: string | null;
    matched_fields: string[];
    semantic_concepts: string[];
    operator_hits: string[];
    score: number;
    age_hours: number;
    stale_pending: boolean;
    high_score_pending: boolean;
    query_run_count: number;
  }[];
};

export type ProviderProvenanceSchedulerHealthStatusSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  cycle_count: number;
  healthy_count: number;
  lagging_count: number;
  failed_count: number;
  disabled_count: number;
  starting_count: number;
  dominant_status: string;
  dominant_count: number;
  latest_status: string;
  latest_summary: string;
  executed_report_count: number;
};

export type ProviderProvenanceSchedulerLagTrendSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  cycle_count: number;
  peak_lag_seconds: number;
  latest_lag_seconds: number;
  average_lag_seconds: number;
  peak_due_report_count: number;
  latest_due_report_count: number;
  failure_count: number;
  executed_report_count: number;
};

export type ProviderProvenanceSchedulerHealthTimeSeriesPayload = {
  bucket_size: string;
  window_days: number;
  window_started_at: string;
  window_ended_at: string;
  health_status: {
    series: ProviderProvenanceSchedulerHealthStatusSeriesEntry[];
    summary: {
      peak_cycle_bucket_key?: string | null;
      peak_cycle_bucket_label?: string | null;
      peak_cycle_count: number;
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      latest_status: string;
      latest_cycle_count: number;
    };
  };
  lag_trend: {
    series: ProviderProvenanceSchedulerLagTrendSeriesEntry[];
    summary: {
      peak_lag_bucket_key?: string | null;
      peak_lag_bucket_label?: string | null;
      peak_lag_seconds: number;
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      latest_lag_seconds: number;
      latest_due_report_count: number;
      latest_failure_count: number;
    };
  };
};

export type ProviderProvenanceSchedulerHealthAnalyticsPayload = {
  generated_at: string;
  query: {
    status?: string | null;
    window_days: number;
    history_limit: number;
    drilldown_bucket_key?: string | null;
    drilldown_history_limit: number;
  };
  current: ProviderProvenanceSchedulerHealthSnapshot;
  totals: {
    record_count: number;
    healthy_count: number;
    lagging_count: number;
    failed_count: number;
    disabled_count: number;
    starting_count: number;
    executed_report_count: number;
    peak_lag_seconds: number;
    peak_due_report_count: number;
  };
  available_filters: {
    statuses: string[];
  };
  time_series: ProviderProvenanceSchedulerHealthTimeSeriesPayload;
  drill_down?: {
    bucket_key: string;
    bucket_label: string;
    bucket_size: "hour";
    window_started_at: string;
    window_ended_at: string;
    total_record_count: number;
    history_limit: number;
    history: ProviderProvenanceSchedulerHealthHistoryEntry[];
    health_status: ProviderProvenanceSchedulerHealthTimeSeriesPayload["health_status"];
    lag_trend: ProviderProvenanceSchedulerHealthTimeSeriesPayload["lag_trend"];
  } | null;
  recent_history: ProviderProvenanceSchedulerHealthHistoryEntry[];
};

export type ProviderProvenanceSchedulerHealthExportPayload = {
  content: string;
  content_type: string;
  exported_at: string;
  filename: string;
  format: "json" | "csv";
  record_count: number;
  total_count: number;
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
