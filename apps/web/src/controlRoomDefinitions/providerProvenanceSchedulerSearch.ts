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

// Runtime placeholders for generated barrel compatibility.
export const ProviderProvenanceSchedulerSearchFeedbackResult = undefined;
export const ProviderProvenanceSchedulerSearchFeedbackModerationResult = undefined;
export const ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult = undefined;
export const ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord = undefined;
export const ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationPlanPreviewItem = undefined;
export const ProviderProvenanceSchedulerSearchModerationPlanEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationPlanListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry = undefined;
export const ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload = undefined;
export const ProviderProvenanceSchedulerSearchDashboardPayload = undefined;
