import {
  CSSProperties,
  FormEvent,
  KeyboardEvent,
  MouseEvent,
  PointerEvent,
  ReactNode,
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION,
  AKRA_TOUCH_FEEDBACK_EVENT_NAME,
  AkraTouchFeedbackDetail,
  AkraTouchFeedbackEnvelope,
  triggerAkraTouchFeedbackBridge,
} from "../../touchFeedback";
import {
  formatComparisonTooltipConflictSessionRelativeTime,
  formatRelativeTimestampLabel,
} from "../comparisonTooltipFormatters";
export {
  formatComparisonTooltipConflictSessionRelativeTime,
  formatRelativeTimestampLabel,
};
import {
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  fetchJson,
  getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
} from "../../controlRoomApi";
import {
  ALL_FILTER_VALUE,
  COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM,
  COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM,
  COMPARISON_FOCUS_DETAIL_SEARCH_PARAM,
  COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM,
  COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM,
  COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM,
  COMPARISON_FOCUS_SECTION_SEARCH_PARAM,
  COMPARISON_FOCUS_SOURCE_SEARCH_PARAM,
  COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS,
  REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM,
  REPLAY_INTENT_ALIAS_SEARCH_PARAM,
  REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM,
  REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM,
  REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM,
  REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM,
  REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM,
  REPLAY_INTENT_SCOPE_SEARCH_PARAM,
  REPLAY_INTENT_SEARCH_PARAM,
  REPLAY_INTENT_STEP_SEARCH_PARAM,
  REPLAY_INTENT_TEMPLATE_SEARCH_PARAM,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY,
} from "../../controlRoomDefinitions";
import type {
  BenchmarkArtifact,
  ComparisonScoreSection,
  ParameterSchema,
  ProvenanceArtifactLineDetailView,
  ProvenanceArtifactLineMicroView,
  Run,
  RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
  RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload,
  RunSurfaceCollectionQueryContract,
  RunSurfaceCollectionQueryElementField,
  RunSurfaceCollectionQueryExpressionAuthoring,
  RunSurfaceCollectionQueryParameterDomainDescriptor,
  RunSurfaceCollectionQuerySchema,
} from "../../controlRoomDefinitions";

import { HydratedRunSurfaceCollectionQueryBuilderState, RunSurfaceCollectionQueryBuilderClauseState, RunSurfaceCollectionQueryBuilderPredicateRefState, RunSurfaceCollectionQueryBuilderGroupState, RunSurfaceCollectionQueryBuilderChildState, RunSurfaceCollectionQueryBuilderPredicateState, RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState, RunSurfaceCollectionQueryBuilderPredicateTemplateState, RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT, RUN_SURFACE_COLLECTION_RUNTIME_MISSING, RunSurfaceCollectionQueryRuntimePathToken, RunSurfaceCollectionQueryRuntimeCollectionItem, formatRunSurfaceCollectionQueryRuntimePathSegment, formatRunSurfaceCollectionQueryRuntimePath, normalizeRunSurfaceCollectionQueryRuntimeCollectionItems, resolveRunSurfaceCollectionQueryRuntimeCollectionItems, resolveRunSurfaceCollectionQueryRuntimeValuePath, normalizeRunSurfaceCollectionQueryRuntimeNumericValue, normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue, toRunSurfaceCollectionQueryRuntimeIterableValues, evaluateRunSurfaceCollectionQueryRuntimeCondition, evaluateRunSurfaceCollectionQueryRuntimeQuantifierOutcome, buildRunSurfaceCollectionQueryRuntimeCandidateSamples, buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey, normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSymbolVariants, collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts } from "./modelRuntimeCore";
import { collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts, normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey, buildRunSurfaceCollectionQueryRuntimeCandidateReplayId, collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries, scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch, doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys, buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems, buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause, buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection } from "./modelRuntimeArtifacts";
import { PredicateRefReplayApplyHistoryRow, PredicateRefReplayApplyHistoryEntry, PredicateRefReplayApplyHistoryTabIdentity, PredicateRefReplayApplySyncMode, PredicateRefReplayApplySyncAuditFilter, PredicateRefReplayApplyConflictPolicy, PredicateRefReplayApplyConflictEntry, PredicateRefReplayApplyConflictDiffItem, PredicateRefReplayApplyConflictResolutionPreview, PredicateRefReplayApplyConflictReview, PredicateRefReplayApplyConflictDraftReview, PredicateRefReplayApplySyncAuditEntry, PredicateRefReplayApplySyncAuditTrailState, PredicateRefReplayApplySyncGovernanceState, RunSurfaceCollectionQueryBuilderReplayIntentState, RunSurfaceCollectionQueryBuilderReplayIntentStorageState, RunSurfaceCollectionQueryBuilderReplayIntentBrowserState, RunSurfaceCollectionQueryBuilderReplayLinkShareMode, RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry, RunSurfaceCollectionQueryBuilderReplayLinkAliasState, RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry, PredicateRefReplayApplyConflictState, HydratedRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderEditorTarget, RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID, buildRunSurfaceCollectionQueryBuilderEntityId, buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId, formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel, loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity, loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState } from "./modelReplayState";
import { normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot, areRunSurfaceCollectionQueryBuilderReplayIntentsEqual, readRunSurfaceCollectionQueryBuilderReplayIntentStorageState, loadRunSurfaceCollectionQueryBuilderReplayIntent, readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, isDefaultRunSurfaceCollectionQueryBuilderReplayIntent, encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl, buildRunSurfaceCollectionQueryBuilderReplayIntentUrl, applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId, buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId, normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs, buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry, buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys, formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue, encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload } from "./modelReplayIntent";
import { loadRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases, pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases, mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts, areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual, readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, persistRunSurfaceCollectionQueryBuilderReplayIntent, buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId, buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId, limitPredicateRefReplayApplySyncAuditEntries, mergePredicateRefReplayApplySyncAuditEntries, limitPredicateRefReplayApplyConflictEntries, serializeComparablePredicateRefReplayApplyHistoryEntry, arePredicateRefReplayApplyHistoryEntriesEquivalent, serializeComparablePredicateRefReplayApplyHistoryRow, formatPredicateRefReplayApplyHistorySnapshotValue, formatPredicateRefReplayApplyHistorySelectionKeyLabel, formatPredicateRefReplayApplyHistoryRowSummary, clonePredicateRefReplayApplyHistoryEntry, buildPredicateRefReplayApplyConflictResolutionPreview, buildPredicateRefReplayApplyConflictMergedEntry } from "./modelReplayStorage";
import { buildPredicateRefReplayApplyConflictReview, normalizePredicateRefReplayApplySyncAuditEntry, normalizePredicateRefReplayApplyConflictEntry, loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts, persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts, normalizeReplayApplySnapshotRecord, normalizePredicateRefReplayApplyHistoryEntry, parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue, loadRunSurfaceCollectionQueryBuilderReplayApplyHistory, serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory, persistRunSurfaceCollectionQueryBuilderReplayApplyHistory, mergePredicateRefReplayApplyHistoryEntries } from "./modelReplayApply";
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export function formatTimestamp(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value;
}

export function encodeComparisonScoreLinkToken(value: string) {
  return encodeURIComponent(value);
}

export function buildComparisonRunListLineSubFocusKey(key: string) {
  return `run-list-line:${encodeComparisonScoreLinkToken(key)}`;
}

export function buildComparisonRunListOrderPreviewSubFocusKey(orderId: string, fieldKey: string) {
  return buildComparisonRunListLineSubFocusKey(
    `order_preview:${encodeComparisonScoreLinkToken(orderId)}:${fieldKey}`,
  );
}

export function buildComparisonRunListDataSymbolSubFocusKey(symbol: string, fieldKey: string) {
  return buildComparisonRunListLineSubFocusKey(
    `data_symbol:${encodeComparisonScoreLinkToken(symbol)}:${fieldKey}`,
  );
}

export function buildComparisonProvenanceArtifactSummaryHoverKey(path: string, summaryKey: string) {
  return `provenance-artifact-summary:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(summaryKey)}`;
}

export function buildComparisonProvenanceArtifactSectionLineHoverKey(
  path: string,
  sectionKey: string,
  lineIndex: number,
) {
  return `provenance-artifact-section-line:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(
    sectionKey,
  )}:${lineIndex}`;
}

export const benchmarkArtifactSummaryLabels: Record<string, string> = {
  headline: "Headline",
  market_context: "Market read",
  portfolio_context: "Portfolio read",
  signal_context: "Signal read",
  rejection_context: "Rejections",
  exit_context: "Exit read",
  pair_context: "Pair read",
  strategy_name: "Strategy",
  run_id: "Run ID",
  exchange: "Exchange",
  stake_currency: "Stake",
  timeframe: "TF",
  timerange: "Timerange",
  generated_at: "Generated",
  backtest_start_at: "Backtest start",
  backtest_end_at: "Backtest end",
  pair_count: "Pairs",
  trade_count: "Trades",
  profit_total_pct: "Total return",
  profit_total_abs: "Total PnL",
  max_drawdown_pct: "Max DD",
  market_change_pct: "Market move",
  manifest_count: "Manifests",
  snapshot_count: "Snapshots",
  timeframe_detail: "TF detail",
  notes: "Notes",
  win_rate_pct: "Win rate",
  date: "Date",
  duration: "Duration",
  drawdown_start: "DD start",
  drawdown_end: "DD end",
  start_balance: "Start balance",
  end_balance: "End balance",
  high_balance: "High balance",
  low_balance: "Low balance",
  sharpe: "Sharpe",
  sortino: "Sortino",
  calmar: "Calmar",
  member_count: "Members",
  entry_preview: "Entries",
  market_change_export_count: "Market exports",
  wallet_export_count: "Wallet exports",
  signal_export_count: "Signal exports",
  rejected_export_count: "Rejected exports",
  exited_export_count: "Exited exports",
  strategy_source_count: "Strategy sources",
  strategy_param_count: "Strategy params",
  result_json_entry: "Result JSON",
  config_json_entry: "Config JSON",
  strategy: "Strategy",
  trading_mode: "Trading mode",
  margin_mode: "Margin mode",
  max_open_trades: "Max open trades",
  export: "Export",
  source_files: "Source files",
  parameter_files: "Parameter files",
  strategy_names: "Strategy names",
  parameter_keys: "Parameter keys",
  entry: "Entry",
  row_count: "Rows",
  total_row_count: "Total rows",
  frame_count: "Frames",
  column_count: "Columns",
  columns: "Column list",
  date_start: "Start",
  date_end: "End",
  export_count: "Exports",
  strategies: "Strategies",
  currencies: "Currencies",
  currency_count: "Currency count",
  entries: "Entries",
  unreadable_entries: "Unreadable",
  inspection_status: "Inspection",
  pair_change_preview: "Pair moves",
  best_pair: "Best pair",
  best_pair_change_pct: "Best pair move",
  worst_pair: "Worst pair",
  worst_pair_change_pct: "Worst pair move",
  positive_pair_count: "Positive pairs",
  negative_pair_count: "Negative pairs",
  start_value: "Start value",
  end_value: "End value",
  change_pct: "Change",
  total_quote_start: "Quote start",
  total_quote_end: "Quote end",
  total_quote_high: "Quote high",
  total_quote_low: "Quote low",
  currency_quote_preview: "Currency quote preview",
  latest_balance: "Latest balance",
  latest_quote_value: "Latest quote value",
  strategy_row_preview: "Strategy rows",
  pair_row_preview: "Pair rows",
  semantic_columns: "Semantic columns",
  enter_tag_counts: "Entry tag counts",
  reason_counts: "Reason counts",
  exit_reason_counts: "Exit reason counts",
};

export const benchmarkArtifactSectionLabels: Record<string, string> = {
  benchmark_story: "Benchmark narrative",
  zip_contents: "Zip contents",
  zip_config: "Embedded config",
  zip_strategy_bundle: "Strategy bundle",
  zip_market_change: "Market change export",
  zip_wallet_exports: "Wallet exports",
  zip_signal_exports: "Signal exports",
  zip_rejected_exports: "Rejected exports",
  zip_exited_exports: "Exited exports",
  metadata: "Metadata",
  strategy_comparison: "Strategy comparison",
  pair_metrics: "Pair metrics",
  pair_extremes: "Pair extremes",
  enter_tag_metrics: "Entry tags",
  exit_reason_metrics: "Exit reasons",
  mixed_tag_metrics: "Mixed tags",
  left_open_metrics: "Left open",
  periodic_breakdown: "Periodic breakdown",
  daily_profit: "Daily profit",
  wallet_stats: "Wallet stats",
};

export function formatBenchmarkArtifactSummaryLabel(key: string) {
  return benchmarkArtifactSummaryLabels[key] ?? key.replaceAll("_", " ");
}

export function formatBenchmarkArtifactSummaryValue(key: string, value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (typeof value === "boolean") {
    return value ? "yes" : "no";
  }
  if (typeof value === "number") {
    if (key.endsWith("_pct")) {
      return `${value}%`;
    }
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export function formatBenchmarkArtifactSectionLabel(key: string) {
  return benchmarkArtifactSectionLabels[key] ?? key.replaceAll("_", " ");
}

export function formatBenchmarkArtifactInlineValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "n/a";
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatBenchmarkArtifactInlineValue(item)).join(", ");
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .filter(([key]) => !key.startsWith("__"))
      .map(([key, nestedValue]) => {
        const formattedValue = formatBenchmarkArtifactSummaryValue(key, nestedValue);
        if (formattedValue === null) {
          return null;
        }
        return `${formatBenchmarkArtifactSummaryLabel(key)}: ${formattedValue}`;
      })
      .filter((entry): entry is string => entry !== null)
      .join(" · ");
  }
  return String(value);
}

export function formatBenchmarkArtifactSectionValue(value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (Array.isArray(value)) {
    if (!value.length) {
      return null;
    }
    const preview = value.slice(0, 3).map((item) => formatBenchmarkArtifactInlineValue(item)).join(" | ");
    if (value.length > 3) {
      return `${preview} | +${value.length - 3} more`;
    }
    return preview;
  }
  if (typeof value === "object") {
    return formatBenchmarkArtifactInlineValue(value);
  }
  return String(value);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord(
  record: RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload,
): RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry {
  return {
    aliasId: record.alias_id,
    createdAt: record.created_at,
    createdByTabId: record.created_by_tab_id ?? "",
    createdByTabLabel: record.created_by_tab_label ?? "Server",
    expiresAt: record.expires_at,
    intent:
      normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(record.intent)
      ?? normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot({})!,
    redactionPolicy: record.redaction_policy,
    resolutionSource: "server",
    revokedAt: record.revoked_at,
    revokedByTabId: record.revoked_by_tab_id,
    revokedByTabLabel: record.revoked_by_tab_label,
    signature: record.signature,
    templateKey: record.template_key,
    templateLabel: record.template_label,
  };
}

export function getCollectionQueryStringArray(value: unknown) {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

export function getCollectionQueryRecordArray(value: unknown) {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
    : [];
}

export function getRunSurfaceCollectionQuerySchemas(
  contract: RunSurfaceCollectionQueryContract | null | undefined,
): RunSurfaceCollectionQuerySchema[] {
  if (!contract) {
    return [];
  }
  return getCollectionQueryRecordArray(contract.schema_detail.collection_schemas).map((schema) => ({
    path: getCollectionQueryStringArray(schema.path),
    pathTemplate: getCollectionQueryStringArray(schema.path_template),
    label: typeof schema.label === "string" ? schema.label : "Collection",
    collectionKind: typeof schema.collection_kind === "string" ? schema.collection_kind : "collection",
    itemKind: typeof schema.item_kind === "string" ? schema.item_kind : "item",
    filterKeys: getCollectionQueryStringArray(schema.filter_keys),
    description: typeof schema.description === "string" ? schema.description : "",
    parameters: getCollectionQueryRecordArray(schema.parameters).map((parameter) => {
      const domainRecord =
        typeof parameter.domain === "object" && parameter.domain !== null
          ? (parameter.domain as Record<string, unknown>)
          : null;
      const enumSourceRecord =
        domainRecord && typeof domainRecord.enum_source === "object" && domainRecord.enum_source !== null
          ? (domainRecord.enum_source as Record<string, unknown>)
          : null;
      return {
        key: typeof parameter.key === "string" ? parameter.key : "",
        kind: typeof parameter.kind === "string" ? parameter.kind : "",
        description: typeof parameter.description === "string" ? parameter.description : "",
        examples: getCollectionQueryStringArray(parameter.examples),
        domain: domainRecord
          ? {
              key: typeof domainRecord.key === "string" ? domainRecord.key : null,
              source: typeof domainRecord.source === "string" ? domainRecord.source : null,
              values: getCollectionQueryStringArray(domainRecord.values),
              enumSource: enumSourceRecord
                ? {
                    kind: typeof enumSourceRecord.kind === "string" ? enumSourceRecord.kind : null,
                    surfaceKey:
                      typeof enumSourceRecord.surface_key === "string" ? enumSourceRecord.surface_key : null,
                    path: getCollectionQueryStringArray(enumSourceRecord.path),
                  }
                : null,
            }
          : null,
      };
    }),
    elementSchema: getCollectionQueryRecordArray(schema.element_schema).map((field) => ({
      key: typeof field.key === "string" ? field.key : "",
      queryExposed: field.query_exposed === true,
      valueType: typeof field.value_type === "string" ? field.value_type : "string",
      valuePath: getCollectionQueryStringArray(field.value_path),
      valueRoot: field.value_root === true,
      title: typeof field.title === "string" ? field.title : null,
      description: typeof field.description === "string" ? field.description : null,
      operators: getCollectionQueryRecordArray(field.operators).map((operator) => ({
        key: typeof operator.key === "string" ? operator.key : "",
        label: typeof operator.label === "string" ? operator.label : "",
        description: typeof operator.description === "string" ? operator.description : "",
        valueShape: typeof operator.value_shape === "string" ? operator.value_shape : "scalar",
      })),
    })),
  }));
}

export function getRunSurfaceCollectionQueryParameterDomains(
  contract: RunSurfaceCollectionQueryContract | null | undefined,
): RunSurfaceCollectionQueryParameterDomainDescriptor[] {
  if (!contract) {
    return [];
  }
  return getCollectionQueryRecordArray(contract.schema_detail.parameter_domains).map((parameterDomain) => {
    const domainRecord =
      typeof parameterDomain.domain === "object" && parameterDomain.domain !== null
        ? (parameterDomain.domain as Record<string, unknown>)
        : null;
    const enumSourceRecord =
      domainRecord && typeof domainRecord.enum_source === "object" && domainRecord.enum_source !== null
        ? (domainRecord.enum_source as Record<string, unknown>)
        : null;
    return {
      parameterKey: typeof parameterDomain.parameter_key === "string" ? parameterDomain.parameter_key : "",
      parameterKind: typeof parameterDomain.parameter_kind === "string" ? parameterDomain.parameter_kind : "",
      collectionLabel: typeof parameterDomain.collection_label === "string" ? parameterDomain.collection_label : "",
      collectionPath: getCollectionQueryStringArray(parameterDomain.collection_path),
      collectionPathTemplate: getCollectionQueryStringArray(parameterDomain.collection_path_template),
      surfaceKey: typeof parameterDomain.surface_key === "string" ? parameterDomain.surface_key : "",
      domain: domainRecord
        ? {
            key: typeof domainRecord.key === "string" ? domainRecord.key : null,
            source: typeof domainRecord.source === "string" ? domainRecord.source : null,
            values: getCollectionQueryStringArray(domainRecord.values),
            enumSource: enumSourceRecord
              ? {
                  kind: typeof enumSourceRecord.kind === "string" ? enumSourceRecord.kind : null,
                  surfaceKey:
                    typeof enumSourceRecord.surface_key === "string" ? enumSourceRecord.surface_key : null,
                  path: getCollectionQueryStringArray(enumSourceRecord.path),
                }
              : null,
          }
        : null,
    };
  });
}

export function getRunSurfaceCollectionQueryExpressionAuthoring(
  contract: RunSurfaceCollectionQueryContract | null | undefined,
): RunSurfaceCollectionQueryExpressionAuthoring {
  const authoringRecord =
    contract && typeof contract.schema_detail.expression_authoring === "object"
      ? (contract.schema_detail.expression_authoring as Record<string, unknown>)
      : null;
  const predicateRefsRecord =
    authoringRecord && typeof authoringRecord.predicate_refs === "object"
      ? (authoringRecord.predicate_refs as Record<string, unknown>)
      : null;
  const predicateTemplatesRecord =
    authoringRecord && typeof authoringRecord.predicate_templates === "object"
      ? (authoringRecord.predicate_templates as Record<string, unknown>)
      : null;
  const bindingReferenceShapeRecord =
    predicateTemplatesRecord && typeof predicateTemplatesRecord.binding_reference_shape === "object"
      ? (predicateTemplatesRecord.binding_reference_shape as Record<string, unknown>)
      : null;
  const collectionNodesRecord =
    authoringRecord && typeof authoringRecord.collection_nodes === "object"
      ? (authoringRecord.collection_nodes as Record<string, unknown>)
      : null;
  const collectionShapeRecord =
    collectionNodesRecord && typeof collectionNodesRecord.shape === "object"
      ? (collectionNodesRecord.shape as Record<string, unknown>)
      : null;
  return {
    predicateRefs: {
      registryField:
        predicateRefsRecord && typeof predicateRefsRecord.registry_field === "string"
          ? predicateRefsRecord.registry_field
          : "predicates",
      referenceField:
        predicateRefsRecord && typeof predicateRefsRecord.reference_field === "string"
          ? predicateRefsRecord.reference_field
          : "predicate_ref",
    },
    predicateTemplates: {
      registryField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.registry_field === "string"
          ? predicateTemplatesRecord.registry_field
          : "predicate_templates",
      templateField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.template_field === "string"
          ? predicateTemplatesRecord.template_field
          : "template",
      parametersField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.parameters_field === "string"
          ? predicateTemplatesRecord.parameters_field
          : "parameters",
      bindingsField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.bindings_field === "string"
          ? predicateTemplatesRecord.bindings_field
          : "bindings",
      bindingReferenceField:
        bindingReferenceShapeRecord && typeof bindingReferenceShapeRecord.binding === "string"
          ? "binding"
          : "binding",
    },
    collectionNodes: {
      field:
        collectionNodesRecord && typeof collectionNodesRecord.field === "string"
          ? collectionNodesRecord.field
          : "collection",
      pathField:
        collectionShapeRecord && typeof collectionShapeRecord.path === "string"
          ? "path"
          : "path",
      pathTemplateField:
        collectionShapeRecord && typeof collectionShapeRecord.path_template === "string"
          ? "path_template"
          : "path_template",
      bindingsField:
        collectionShapeRecord && typeof collectionShapeRecord.bindings === "object"
          ? "bindings"
          : "bindings",
      quantifierField:
        collectionShapeRecord && typeof collectionShapeRecord.quantifier === "string"
          ? "quantifier"
          : "quantifier",
    },
  };
}

export function getCollectionQuerySchemaId(schema: RunSurfaceCollectionQuerySchema) {
  return schema.pathTemplate.join(".");
}

export function resolveCollectionQueryPath(
  template: string[],
  parameterValues: Record<string, string>,
) {
  return template.map((segment) => {
    const match = segment.match(/^\{(.+)\}$/);
    if (!match) {
      return segment;
    }
    return parameterValues[match[1]] || segment;
  });
}

export function resolveCollectionQueryTemplateValues(
  template: string[],
  resolvedPath: string[],
) {
  if (template.length !== resolvedPath.length) {
    return null;
  }
  const values: Record<string, string> = {};
  for (let index = 0; index < template.length; index += 1) {
    const templateSegment = template[index];
    const resolvedSegment = resolvedPath[index];
    const match = templateSegment.match(/^\{(.+)\}$/);
    if (match) {
      values[match[1]] = resolvedSegment;
      continue;
    }
    if (templateSegment !== resolvedSegment) {
      return null;
    }
  }
  return values;
}

export function coerceCollectionQueryBuilderValue(rawValue: string, valueType: string) {
  if (valueType === "integer") {
    const parsed = Number.parseInt(rawValue, 10);
    return Number.isNaN(parsed) ? rawValue : parsed;
  }
  if (valueType === "number") {
    const parsed = Number.parseFloat(rawValue);
    return Number.isNaN(parsed) ? rawValue : parsed;
  }
  if (valueType.startsWith("list[")) {
    return rawValue
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return rawValue;
}

export function formatCollectionQueryBuilderValue(rawValue: unknown, valueType: string) {
  if (rawValue === null || rawValue === undefined) {
    return "";
  }
  if (valueType.startsWith("list[")) {
    if (Array.isArray(rawValue)) {
      return rawValue.map((value) => String(value)).join(", ");
    }
    return String(rawValue);
  }
  if (typeof rawValue === "string") {
    return rawValue;
  }
  if (typeof rawValue === "number" || typeof rawValue === "boolean") {
    return String(rawValue);
  }
  try {
    return JSON.stringify(rawValue);
  } catch {
    return String(rawValue);
  }
}
