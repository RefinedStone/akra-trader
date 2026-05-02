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

import { formatTimestamp, encodeComparisonScoreLinkToken, buildComparisonRunListLineSubFocusKey, buildComparisonRunListOrderPreviewSubFocusKey, buildComparisonRunListDataSymbolSubFocusKey, buildComparisonProvenanceArtifactSummaryHoverKey, buildComparisonProvenanceArtifactSectionLineHoverKey, benchmarkArtifactSummaryLabels, benchmarkArtifactSectionLabels, formatBenchmarkArtifactSummaryLabel, formatBenchmarkArtifactSummaryValue, formatBenchmarkArtifactSectionLabel, formatBenchmarkArtifactInlineValue, formatBenchmarkArtifactSectionValue, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord, getCollectionQueryStringArray, getCollectionQueryRecordArray, getRunSurfaceCollectionQuerySchemas, getRunSurfaceCollectionQueryParameterDomains, getRunSurfaceCollectionQueryExpressionAuthoring, getCollectionQuerySchemaId, resolveCollectionQueryPath, resolveCollectionQueryTemplateValues, coerceCollectionQueryBuilderValue, formatCollectionQueryBuilderValue } from "./modelArtifacts";
import { HydratedRunSurfaceCollectionQueryBuilderState, RunSurfaceCollectionQueryBuilderClauseState, RunSurfaceCollectionQueryBuilderPredicateRefState, RunSurfaceCollectionQueryBuilderGroupState, RunSurfaceCollectionQueryBuilderChildState, RunSurfaceCollectionQueryBuilderPredicateState, RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState, RunSurfaceCollectionQueryBuilderPredicateTemplateState, RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT, RUN_SURFACE_COLLECTION_RUNTIME_MISSING, RunSurfaceCollectionQueryRuntimePathToken, RunSurfaceCollectionQueryRuntimeCollectionItem, formatRunSurfaceCollectionQueryRuntimePathSegment, formatRunSurfaceCollectionQueryRuntimePath, normalizeRunSurfaceCollectionQueryRuntimeCollectionItems, resolveRunSurfaceCollectionQueryRuntimeCollectionItems, resolveRunSurfaceCollectionQueryRuntimeValuePath, normalizeRunSurfaceCollectionQueryRuntimeNumericValue, normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue, toRunSurfaceCollectionQueryRuntimeIterableValues, evaluateRunSurfaceCollectionQueryRuntimeCondition, evaluateRunSurfaceCollectionQueryRuntimeQuantifierOutcome, buildRunSurfaceCollectionQueryRuntimeCandidateSamples, buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey, normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSymbolVariants, collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts } from "./modelRuntimeCore";
import { collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts, normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey, buildRunSurfaceCollectionQueryRuntimeCandidateReplayId, collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries, scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch, doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys, buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems, buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause, buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection } from "./modelRuntimeArtifacts";
import { normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot, areRunSurfaceCollectionQueryBuilderReplayIntentsEqual, readRunSurfaceCollectionQueryBuilderReplayIntentStorageState, loadRunSurfaceCollectionQueryBuilderReplayIntent, readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, isDefaultRunSurfaceCollectionQueryBuilderReplayIntent, encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl, buildRunSurfaceCollectionQueryBuilderReplayIntentUrl, applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId, buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId, normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs, buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry, buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys, formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue, encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload } from "./modelReplayIntent";
import { loadRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases, pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases, mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts, areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual, readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, persistRunSurfaceCollectionQueryBuilderReplayIntent, buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId, buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId, limitPredicateRefReplayApplySyncAuditEntries, mergePredicateRefReplayApplySyncAuditEntries, limitPredicateRefReplayApplyConflictEntries, serializeComparablePredicateRefReplayApplyHistoryEntry, arePredicateRefReplayApplyHistoryEntriesEquivalent, serializeComparablePredicateRefReplayApplyHistoryRow, formatPredicateRefReplayApplyHistorySnapshotValue, formatPredicateRefReplayApplyHistorySelectionKeyLabel, formatPredicateRefReplayApplyHistoryRowSummary, clonePredicateRefReplayApplyHistoryEntry, buildPredicateRefReplayApplyConflictResolutionPreview, buildPredicateRefReplayApplyConflictMergedEntry } from "./modelReplayStorage";
import { buildPredicateRefReplayApplyConflictReview, normalizePredicateRefReplayApplySyncAuditEntry, normalizePredicateRefReplayApplyConflictEntry, loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts, persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts, normalizeReplayApplySnapshotRecord, normalizePredicateRefReplayApplyHistoryEntry, parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue, loadRunSurfaceCollectionQueryBuilderReplayApplyHistory, serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory, persistRunSurfaceCollectionQueryBuilderReplayApplyHistory, mergePredicateRefReplayApplyHistoryEntries } from "./modelReplayApply";
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export type PredicateRefReplayApplyHistoryRow = {
  changesCurrent: boolean;
  currentBundleLabel: string;
  currentStatus: string;
  groupKey: string;
  groupLabel: string;
  matchesSimulation: boolean;
  promotedBundleKey: string;
  promotedBundleLabel: string;
  simulatedBundleLabel: string;
  simulatedStatus: string;
};

export type PredicateRefReplayApplyHistoryEntry = {
  appliedAt: string;
  approvedCount: number;
  changedCurrentCount: number;
  id: string;
  matchesSimulationCount: number;
  rollbackSnapshot: {
    draftBindingsByParameterKey: Record<string, string | null>;
    groupSelectionsBySelectionKey: Record<string, string | null>;
  };
  rows: PredicateRefReplayApplyHistoryRow[];
  sourceTabId?: string | null;
  sourceTabLabel?: string | null;
  templateId: string;
  templateLabel: string;
  lastRestoredAt?: string | null;
  lastRestoredByTabId?: string | null;
  lastRestoredByTabLabel?: string | null;
};

export type PredicateRefReplayApplyHistoryTabIdentity = {
  label: string;
  tabId: string;
};

export type PredicateRefReplayApplySyncMode = "live" | "audit_only" | "mute_remote";
export type PredicateRefReplayApplySyncAuditFilter = "all" | "local" | "remote" | "apply" | "restore" | "conflict";
export type PredicateRefReplayApplyConflictPolicy = "prefer_local" | "prefer_remote" | "require_review";

export type PredicateRefReplayApplyConflictEntry = {
  conflictId: string;
  detectedAt: string;
  entryId: string;
  localEntry: PredicateRefReplayApplyHistoryEntry;
  remoteEntry: PredicateRefReplayApplyHistoryEntry;
  sourceTabId: string;
  sourceTabLabel: string;
  templateId: string;
  templateLabel: string;
};

export type PredicateRefReplayApplyConflictDiffItem = {
  decisionKey: string;
  editable: boolean;
  key: string;
  label: string;
  localValue: string;
  remoteValue: string;
  relatedGroupKey?: string | null;
  section: "summary" | "row" | "selection_snapshot" | "binding_snapshot";
};

export type PredicateRefReplayApplyConflictResolutionPreview = {
  effect: string;
  entry: PredicateRefReplayApplyHistoryEntry;
  matchesLocal: boolean;
  matchesRemote: boolean;
  resolution: "local" | "remote" | "merged";
  rowSummaries: string[];
  snapshotSummary: string;
  title: string;
};

export type PredicateRefReplayApplyConflictReview = {
  bindingSnapshotDiffs: PredicateRefReplayApplyConflictDiffItem[];
  conflict: PredicateRefReplayApplyConflictEntry;
  localPreview: PredicateRefReplayApplyConflictResolutionPreview;
  remotePreview: PredicateRefReplayApplyConflictResolutionPreview;
  rowDiffs: PredicateRefReplayApplyConflictDiffItem[];
  selectionSnapshotDiffs: PredicateRefReplayApplyConflictDiffItem[];
  summaryDiffs: PredicateRefReplayApplyConflictDiffItem[];
  totalDiffCount: number;
};

export type PredicateRefReplayApplyConflictDraftReview = PredicateRefReplayApplyConflictReview & {
  editableDiffCount: number;
  hasMixedSelection: boolean;
  hasRemoteSelection: boolean;
  mergedEntry: PredicateRefReplayApplyHistoryEntry;
  mergedPreview: PredicateRefReplayApplyConflictResolutionPreview;
  selectedRemoteCount: number;
  selectedSources: Record<string, "local" | "remote">;
};

export type PredicateRefReplayApplySyncAuditEntry = {
  at: string;
  auditId: string;
  detail: string;
  entryId: string;
  kind:
    | "local_apply"
    | "local_restore"
    | "remote_apply"
    | "remote_restore"
    | "conflict_detected"
    | "conflict_resolved";
  sourceTabId: string;
  sourceTabLabel: string;
  templateId: string;
  templateLabel: string;
};

export type PredicateRefReplayApplySyncAuditTrailState = {
  entries: PredicateRefReplayApplySyncAuditEntry[];
  tabId: string;
  version: number;
};

export type PredicateRefReplayApplySyncGovernanceState = {
  auditFilter: PredicateRefReplayApplySyncAuditFilter;
  conflictPolicy: PredicateRefReplayApplyConflictPolicy;
  syncMode: PredicateRefReplayApplySyncMode;
  tabId: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayIntentState = {
  previewSelection: {
    diffItemKey: string | null;
    groupKey: string | null;
    traceKey: string | null;
  };
  replayActionTypeFilter: "all" | "manual_anchor" | "dependency_selection" | "direct_auto_selection" | "conflict_blocked" | "idle";
  replayEdgeFilter: "all" | string;
  replayGroupFilter: "all" | string;
  replayIndex: number;
  replayScope: "all" | string;
  templateId: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayIntentStorageState = {
  intentsByTemplateId: Record<string, RunSurfaceCollectionQueryBuilderReplayIntentSnapshot>;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayIntentBrowserState = {
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
  templateId: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkShareMode = "portable" | "indirect";

export type RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry = {
  aliasId: string;
  createdAt: string;
  createdByTabId: string;
  createdByTabLabel: string;
  expiresAt: string | null;
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  resolutionSource: "local" | "server";
  revokedAt: string | null;
  revokedByTabId: string | null;
  revokedByTabLabel: string | null;
  signature: string | null;
  templateKey: string;
  templateLabel: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkAliasState = {
  aliases: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[];
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry = {
  action: "copy" | "share" | "revoke";
  aliasId: string | null;
  at: string;
  id: string;
  linkLength: number;
  mode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  sourceTabId: string;
  sourceTabLabel: string;
  status: "success" | "cancelled" | "failed";
  templateKey: string;
  templateLabel: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkAuditState = {
  entries: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[];
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode = "live" | "opt_out" | "review";

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot = {
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  syncMode: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey =
  | "shareMode"
  | "redactionPolicy"
  | "retentionPolicy"
  | "syncMode";

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry = {
  at: string;
  detail: string;
  diffKeys: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey[];
  fromState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
  id: string;
  kind:
    | "local_change"
    | "remote_sync"
    | "remote_ignored"
    | "conflict_detected"
    | "conflict_resolved_local"
    | "conflict_resolved_remote"
    | "cross_device_export"
    | "cross_device_import";
  remoteSourceTabId: string | null;
  remoteSourceTabLabel: string | null;
  sourceTabId: string;
  sourceTabLabel: string;
  toState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState = {
  entries: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[];
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState = {
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  reviewedConflictKeys: string[];
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  syncMode: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState = {
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  sourceTabId: string;
  sourceTabLabel: string;
  updatedAt: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload = {
  exportedAt: string;
  governance: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
  sourceTabId: string;
  sourceTabLabel: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource = {
  detail?: string;
  kind: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry["kind"];
  remoteSourceTabId?: string | null;
  remoteSourceTabLabel?: string | null;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry = {
  conflictKey: string;
  detectedAt: string;
  localRedactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  localRetentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  localShareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  remoteRedactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  remoteRetentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  remoteShareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  sourceTabId: string;
  sourceTabLabel: string;
  updatedAt: string;
};

export type PredicateRefReplayApplyConflictState = {
  conflicts: PredicateRefReplayApplyConflictEntry[];
  tabId: string;
  version: number;
};

export type HydratedRunSurfaceCollectionQueryBuilderExpressionState = {
  mode: "single" | "grouped";
  draftClause: HydratedRunSurfaceCollectionQueryBuilderState | null;
  groupLogic: "and" | "or";
  rootNegated: boolean;
  expressionChildren: RunSurfaceCollectionQueryBuilderChildState[];
  predicates: RunSurfaceCollectionQueryBuilderPredicateState[];
  predicateTemplates: RunSurfaceCollectionQueryBuilderPredicateTemplateState[];
};

export type RunSurfaceCollectionQueryBuilderEditorTarget =
  | { kind: "draft" }
  | { kind: "expression_clause"; childId: string }
  | { kind: "predicate"; predicateId: string }
  | { kind: "template"; templateId: string };

export const RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID = "root";

export function buildRunSurfaceCollectionQueryBuilderEntityId(prefix: string) {
  return `${prefix}:${Math.random().toString(36).slice(2, 10)}`;
}

export function buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-tab-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(tabId: string) {
  return `Tab ${tabId.replace(/[^a-z0-9]/gi, "").slice(0, 4).toUpperCase() || "REPL"}`;
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity(): PredicateRefReplayApplyHistoryTabIdentity {
  const fallbackTabId = buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId();
  if (typeof window === "undefined") {
    return {
      tabId: fallbackTabId,
      label: formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(fallbackTabId),
    };
  }
  try {
    const existingTabId =
      window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY)?.trim();
    const tabId = existingTabId || fallbackTabId;
    if (!existingTabId) {
      window.sessionStorage.setItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY, tabId);
    }
    return {
      tabId,
      label: formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(tabId),
    };
  } catch {
    return {
      tabId: fallbackTabId,
      label: formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(fallbackTabId),
    };
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState(
  tabId: string,
): {
  auditFilter: PredicateRefReplayApplySyncAuditFilter;
  conflictPolicy: PredicateRefReplayApplyConflictPolicy;
  syncMode: PredicateRefReplayApplySyncMode;
} {
  if (typeof window === "undefined") {
    return {
      auditFilter: "all",
      conflictPolicy: "require_review",
      syncMode: "live",
    };
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY);
    if (!raw) {
      return {
        auditFilter: "all",
        conflictPolicy: "require_review",
        syncMode: "live",
      };
    }
    const parsed = JSON.parse(raw) as Partial<PredicateRefReplayApplySyncGovernanceState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION
      || parsed.tabId !== tabId
    ) {
      return {
        auditFilter: "all",
        conflictPolicy: "require_review",
        syncMode: "live",
      };
    }
    return {
      auditFilter:
        parsed.auditFilter === "local"
        || parsed.auditFilter === "remote"
        || parsed.auditFilter === "apply"
        || parsed.auditFilter === "conflict"
        || parsed.auditFilter === "restore"
          ? parsed.auditFilter
          : "all",
      conflictPolicy:
        parsed.conflictPolicy === "prefer_local"
        || parsed.conflictPolicy === "prefer_remote"
          ? parsed.conflictPolicy
          : "require_review",
      syncMode:
        parsed.syncMode === "audit_only" || parsed.syncMode === "mute_remote"
          ? parsed.syncMode
          : "live",
    };
  } catch {
    return {
      auditFilter: "all",
      conflictPolicy: "require_review",
      syncMode: "live",
    };
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState(
  tabId: string,
  state: {
    auditFilter: PredicateRefReplayApplySyncAuditFilter;
    conflictPolicy: PredicateRefReplayApplyConflictPolicy;
    syncMode: PredicateRefReplayApplySyncMode;
  },
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: PredicateRefReplayApplySyncGovernanceState = {
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION,
      tabId,
      auditFilter: state.auditFilter,
      conflictPolicy: state.conflictPolicy,
      syncMode: state.syncMode,
    };
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

// Runtime placeholders for generated barrel compatibility.
export const PredicateRefReplayApplyHistoryRow = undefined;
export const PredicateRefReplayApplyHistoryEntry = undefined;
export const PredicateRefReplayApplyHistoryTabIdentity = undefined;
export const PredicateRefReplayApplySyncMode = undefined;
export const PredicateRefReplayApplySyncAuditFilter = undefined;
export const PredicateRefReplayApplyConflictPolicy = undefined;
export const PredicateRefReplayApplyConflictEntry = undefined;
export const PredicateRefReplayApplyConflictDiffItem = undefined;
export const PredicateRefReplayApplyConflictResolutionPreview = undefined;
export const PredicateRefReplayApplyConflictReview = undefined;
export const PredicateRefReplayApplyConflictDraftReview = undefined;
export const PredicateRefReplayApplySyncAuditEntry = undefined;
export const PredicateRefReplayApplySyncAuditTrailState = undefined;
export const PredicateRefReplayApplySyncGovernanceState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayIntentState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayIntentStorageState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayIntentBrowserState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkShareMode = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkAliasState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkAuditState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource = undefined;
export const RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry = undefined;
export const PredicateRefReplayApplyConflictState = undefined;
export const HydratedRunSurfaceCollectionQueryBuilderExpressionState = undefined;
export const RunSurfaceCollectionQueryBuilderEditorTarget = undefined;
