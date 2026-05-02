import type { OperatorAlertEntry } from "./operatorVisibility";

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

// Runtime placeholders for generated barrel compatibility.
export const ProviderProvenanceSchedulerHealthSnapshot = undefined;
export const ProviderProvenanceSchedulerHealthHistoryEntry = undefined;
export const ProviderProvenanceSchedulerHealthHistoryPayload = undefined;
export const ProviderProvenanceSchedulerAlertHistoryPayload = undefined;
export const ProviderProvenanceSchedulerHealthStatusSeriesEntry = undefined;
export const ProviderProvenanceSchedulerLagTrendSeriesEntry = undefined;
export const ProviderProvenanceSchedulerHealthTimeSeriesPayload = undefined;
export const ProviderProvenanceSchedulerHealthAnalyticsPayload = undefined;
export const ProviderProvenanceSchedulerHealthExportPayload = undefined;
