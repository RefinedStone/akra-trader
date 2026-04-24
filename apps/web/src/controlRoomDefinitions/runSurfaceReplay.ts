export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY = "akra-trader-run-surface-replay-history";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY = "akra-trader-run-surface-replay-intent";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION = 2;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY = "akra-trader-run-surface-replay-intent";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY = "akra-trader-run-surface-replay-link-aliases";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY = "akra-trader-run-surface-replay-link-audit";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY = "akra-trader-run-surface-replay-link-signing-secret";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY = "akra-trader-run-surface-replay-link-governance-audit";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY = "akra-trader-run-surface-replay-link-governance";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY = "akra-trader-run-surface-replay-link-governance-sync";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION = 1;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES = 12;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES = 24;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES = 24;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES = 24;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES = 8;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS = 24;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY = "akra-trader-run-surface-replay-history-tab-id";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY = "akra-trader-run-surface-replay-history-sync-audit";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION = 1;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES = 8;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY = "akra-trader-run-surface-replay-history-governance";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY = "akra-trader-run-surface-replay-history-conflicts";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION = 1;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES = 8;
export const REPLAY_INTENT_TEMPLATE_SEARCH_PARAM = "replay_template";
export const REPLAY_INTENT_SEARCH_PARAM = "replay_intent";
export const REPLAY_INTENT_ALIAS_SEARCH_PARAM = "replay_link";
export const REPLAY_INTENT_SCOPE_SEARCH_PARAM = "replay_scope";
export const REPLAY_INTENT_STEP_SEARCH_PARAM = "replay_step";
export const REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM = "replay_group";
export const REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM = "replay_action";
export const REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM = "replay_edge";
export const REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM = "replay_preview_group";
export const REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM = "replay_preview_trace";
export const REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM = "replay_preview_diff";

export type RunSurfaceCollectionQueryBuilderReplayIntentSnapshot = {
  previewSelection: {
    diffItemKey: string | null;
    groupKey: string | null;
    traceKey: string | null;
  };
  replayActionTypeFilter:
    | "all"
    | "manual_anchor"
    | "dependency_selection"
    | "direct_auto_selection"
    | "conflict_blocked"
    | "idle";
  replayEdgeFilter: "all" | string;
  replayGroupFilter: "all" | string;
  replayIndex: number;
  replayScope: "all" | string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy =
  "full"
  | "omit_preview"
  | "summary_only";

export type RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy =
  "1d"
  | "7d"
  | "30d"
  | "manual";

export type RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload = {
  alias_id: string;
  alias_token: string;
  created_at: string;
  created_by_tab_id: string | null;
  created_by_tab_label: string | null;
  expires_at: string | null;
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
  redaction_policy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  resolution_source: "server";
  revoked_at: string | null;
  revoked_by_tab_id: string | null;
  revoked_by_tab_label: string | null;
  signature: string | null;
  template_key: string;
  template_label: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry = {
  action: string;
  alias_created_at: string | null;
  alias_expires_at: string | null;
  alias_id: string;
  alias_revoked_at: string | null;
  audit_id: string;
  detail: string;
  expires_at: string | null;
  recorded_at: string;
  redaction_policy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  retention_policy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  source_tab_id: string | null;
  source_tab_label: string | null;
  template_key: string;
  template_label: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload = {
  items: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry[];
  total: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload = {
  deleted_count: number;
  matched_audit_ids?: string[];
  mode: "expired" | "matched" | string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry = {
  artifact_id: string | null;
  completed_at: string | null;
  content_type: string;
  created_at: string;
  content_length: number;
  expires_at: string | null;
  export_format: "json" | "csv" | string;
  filename: string;
  filters: Record<string, unknown>;
  job_id: string;
  record_count: number;
  requested_by_tab_id: string | null;
  requested_by_tab_label: string | null;
  status: string;
  template_key: string | null;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload = {
  items: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry[];
  total: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload =
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry & {
    content: string;
  };

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry = {
  action: string;
  audit_id: string;
  detail: string;
  expires_at: string | null;
  export_format: string | null;
  job_id: string;
  recorded_at: string;
  source_tab_id: string | null;
  source_tab_label: string | null;
  template_key: string | null;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload = {
  history: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry[];
  job: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload = {
  deleted_artifact_count: number;
  deleted_artifact_ids?: string[];
  deleted_history_count: number;
  deleted_job_count: number;
  deleted_job_ids?: string[];
  mode: "expired" | "matched" | string;
};
