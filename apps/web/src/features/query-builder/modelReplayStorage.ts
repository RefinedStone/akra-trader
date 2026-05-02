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
import { PredicateRefReplayApplyHistoryRow, PredicateRefReplayApplyHistoryEntry, PredicateRefReplayApplyHistoryTabIdentity, PredicateRefReplayApplySyncMode, PredicateRefReplayApplySyncAuditFilter, PredicateRefReplayApplyConflictPolicy, PredicateRefReplayApplyConflictEntry, PredicateRefReplayApplyConflictDiffItem, PredicateRefReplayApplyConflictResolutionPreview, PredicateRefReplayApplyConflictReview, PredicateRefReplayApplyConflictDraftReview, PredicateRefReplayApplySyncAuditEntry, PredicateRefReplayApplySyncAuditTrailState, PredicateRefReplayApplySyncGovernanceState, RunSurfaceCollectionQueryBuilderReplayIntentState, RunSurfaceCollectionQueryBuilderReplayIntentStorageState, RunSurfaceCollectionQueryBuilderReplayIntentBrowserState, RunSurfaceCollectionQueryBuilderReplayLinkShareMode, RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry, RunSurfaceCollectionQueryBuilderReplayLinkAliasState, RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry, PredicateRefReplayApplyConflictState, HydratedRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderEditorTarget, RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID, buildRunSurfaceCollectionQueryBuilderEntityId, buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId, formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel, loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity, loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState } from "./modelReplayState";
import { normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot, areRunSurfaceCollectionQueryBuilderReplayIntentsEqual, readRunSurfaceCollectionQueryBuilderReplayIntentStorageState, loadRunSurfaceCollectionQueryBuilderReplayIntent, readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, isDefaultRunSurfaceCollectionQueryBuilderReplayIntent, encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl, buildRunSurfaceCollectionQueryBuilderReplayIntentUrl, applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId, buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId, normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs, buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry, buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys, formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue, encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload } from "./modelReplayIntent";
import { buildPredicateRefReplayApplyConflictReview, normalizePredicateRefReplayApplySyncAuditEntry, normalizePredicateRefReplayApplyConflictEntry, loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts, persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts, normalizeReplayApplySnapshotRecord, normalizePredicateRefReplayApplyHistoryEntry, parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue, loadRunSurfaceCollectionQueryBuilderReplayApplyHistory, serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory, persistRunSurfaceCollectionQueryBuilderReplayApplyHistory, mergePredicateRefReplayApplyHistoryEntries } from "./modelReplayApply";
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAliases() {
  return loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue(
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY),
  );
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue(
  raw: string | null | undefined,
) {
  if (typeof window === "undefined") {
    return [] as RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[];
  }
  try {
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkAliasState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION
      || !Array.isArray(parsed.aliases)
    ) {
      return [];
    }
    return parsed.aliases.filter((entry): entry is RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry =>
      Boolean(
        entry
        && typeof entry.aliasId === "string"
        && typeof entry.createdAt === "string"
        && (typeof entry.expiresAt === "string" || entry.expiresAt === null || entry.expiresAt === undefined)
        && (typeof entry.signature === "string" || entry.signature === null || entry.signature === undefined)
        && typeof entry.templateKey === "string"
        && typeof entry.templateLabel === "string",
      ),
    ).map((entry): RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry => ({
      ...entry,
      expiresAt: typeof entry.expiresAt === "string" ? entry.expiresAt : null,
      resolutionSource: entry.resolutionSource === "server" ? "server" : "local",
      revokedAt: typeof entry.revokedAt === "string" ? entry.revokedAt : null,
      revokedByTabId: typeof entry.revokedByTabId === "string" ? entry.revokedByTabId : null,
      revokedByTabLabel: typeof entry.revokedByTabLabel === "string" ? entry.revokedByTabLabel : null,
      signature: typeof entry.signature === "string" ? entry.signature : null,
    })).filter((entry) =>
      !entry.expiresAt || Date.parse(entry.expiresAt) > Date.now(),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkAliases(
  aliases: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY,
      JSON.stringify({
        aliases: aliases.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkAliasState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail() {
  return loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue(
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY),
  );
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue(
  raw: string | null | undefined,
) {
  if (typeof window === "undefined") {
    return [] as RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[];
  }
  try {
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkAuditState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return parsed.entries.filter((entry): entry is RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry =>
      Boolean(
        entry
        && typeof entry.id === "string"
        && typeof entry.at === "string"
        && typeof entry.templateKey === "string"
        && typeof entry.templateLabel === "string",
      ),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY,
      JSON.stringify({
        entries: entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkAuditState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail() {
  return loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue(
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY),
  );
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue(
  raw: string | null | undefined,
) {
  if (typeof window === "undefined") {
    return [] as RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[];
  }
  try {
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return parsed.entries.filter((entry): entry is RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry =>
      Boolean(
        entry
        && typeof entry.id === "string"
        && typeof entry.at === "string"
        && typeof entry.kind === "string"
        && typeof entry.sourceTabId === "string"
        && typeof entry.sourceTabLabel === "string"
        && Array.isArray(entry.diffKeys),
      ),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY,
      JSON.stringify({
        entries: entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState() {
  const defaultState = {
    redactionPolicy: "full" as const,
    reviewedConflictKeys: [] as string[],
    retentionPolicy: "30d" as const,
    shareMode: "portable" as const,
    syncMode: "live" as const,
  };
  if (typeof window === "undefined") {
    return defaultState;
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY);
    if (!raw) {
      return defaultState;
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState> | null;
    return {
      redactionPolicy:
        parsed?.redactionPolicy === "omit_preview" || parsed?.redactionPolicy === "summary_only"
          ? parsed.redactionPolicy
          : defaultState.redactionPolicy,
      reviewedConflictKeys: Array.isArray(parsed?.reviewedConflictKeys)
        ? parsed.reviewedConflictKeys
          .filter((value): value is string => typeof value === "string")
          .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS)
        : defaultState.reviewedConflictKeys,
      retentionPolicy: normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
        parsed?.retentionPolicy,
      ),
      shareMode:
        parsed?.shareMode === "indirect"
          ? "indirect"
          : defaultState.shareMode,
      syncMode:
        parsed?.syncMode === "opt_out" || parsed?.syncMode === "review"
          ? parsed.syncMode
          : defaultState.syncMode,
    } as const;
  } catch {
    return defaultState;
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState(
  state: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    reviewedConflictKeys: string[];
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
    syncMode: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode;
  },
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY,
      JSON.stringify({
        ...state,
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState),
    );
  } catch {
    return;
  }
}

export function mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(
  current: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
  incoming: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
) {
  const byId = new Map<string, RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry>();
  [...incoming, ...current].forEach((entry) => {
    const existing = byId.get(entry.aliasId);
    if (!existing || existing.createdAt < entry.createdAt) {
      byId.set(entry.aliasId, entry);
    }
  });
  return Array.from(byId.values())
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES);
}

export function pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases(
  aliases: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  const cutoffMs = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  const nowMs = Date.now();
  return aliases.filter((entry) => {
    if (entry.expiresAt && Date.parse(entry.expiresAt) <= nowMs) {
      return false;
    }
    if (cutoffMs === null) {
      return true;
    }
    const createdAtMs = Date.parse(entry.createdAt);
    if (!Number.isFinite(createdAtMs)) {
      return false;
    }
    return nowMs - createdAtMs <= cutoffMs;
  });
}

export function mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
  current: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
  incoming: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
) {
  const seen = new Set<string>();
  return [...incoming, ...current]
    .filter((entry) => {
      if (seen.has(entry.id)) {
        return false;
      }
      seen.add(entry.id);
      return true;
    })
    .sort((left, right) => right.at.localeCompare(left.at))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES);
}

export function pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  const cutoffMs = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  if (cutoffMs === null) {
    return entries;
  }
  const nowMs = Date.now();
  return entries.filter((entry) => {
    const entryMs = Date.parse(entry.at);
    return Number.isFinite(entryMs) && nowMs - entryMs <= cutoffMs;
  });
}

export function mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
  current: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
  incoming: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
) {
  const seen = new Set<string>();
  return [...incoming, ...current]
    .filter((entry) => {
      if (seen.has(entry.id)) {
        return false;
      }
      seen.add(entry.id);
      return true;
    })
    .sort((left, right) => right.at.localeCompare(left.at))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES);
}

export function pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  const cutoffMs = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  if (cutoffMs === null) {
    return entries;
  }
  const nowMs = Date.now();
  return entries.filter((entry) => {
    const entryMs = Date.parse(entry.at);
    return Number.isFinite(entryMs) && nowMs - entryMs <= cutoffMs;
  });
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState(
  state: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
    sourceTabId: string;
    sourceTabLabel: string;
  },
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY,
      JSON.stringify({
        ...state,
        updatedAt: new Date().toISOString(),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState),
    );
  } catch {
    return;
  }
}

export function limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys(keys: string[]) {
  const seen = new Set<string>();
  return keys.filter((key) => {
    if (!key || seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  }).slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey(
  state: Pick<
    RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState,
    "redactionPolicy" | "retentionPolicy" | "shareMode" | "sourceTabId" | "updatedAt"
  >,
) {
  return [
    state.sourceTabId,
    state.updatedAt,
    state.shareMode,
    state.redactionPolicy,
    state.retentionPolicy,
  ].join(":");
}

export function limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts(
  conflicts: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry[],
) {
  return conflicts.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES);
}

export function areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual(
  left: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  },
  right: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  },
) {
  return (
    left.redactionPolicy === right.redactionPolicy
    && left.retentionPolicy === right.retentionPolicy
    && left.shareMode === right.shareMode
  );
}

export function readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState(
  raw: string | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState | null {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION
      || typeof parsed.sourceTabId !== "string"
      || typeof parsed.sourceTabLabel !== "string"
      || typeof parsed.updatedAt !== "string"
    ) {
      return null;
    }
    return {
      redactionPolicy:
        parsed.redactionPolicy === "omit_preview" || parsed.redactionPolicy === "summary_only"
          ? parsed.redactionPolicy
          : "full",
      retentionPolicy: normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
        parsed.retentionPolicy,
      ),
      shareMode: parsed.shareMode === "indirect" ? "indirect" : "portable",
      sourceTabId: parsed.sourceTabId,
      sourceTabLabel: parsed.sourceTabLabel,
      updatedAt: parsed.updatedAt,
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION,
    };
  } catch {
    return null;
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayIntent(
  state: Omit<RunSurfaceCollectionQueryBuilderReplayIntentState, "version">,
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const currentState =
      readRunSurfaceCollectionQueryBuilderReplayIntentStorageState(
        window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY),
      )
      ?? {
        intentsByTemplateId: {},
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
      };
    const nextIntent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(state);
    if (!nextIntent) {
      return;
    }
    const currentIntent = currentState.intentsByTemplateId[state.templateId] ?? null;
    if (areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(currentIntent, nextIntent)) {
      return;
    }
    const nextState: RunSurfaceCollectionQueryBuilderReplayIntentStorageState = {
      intentsByTemplateId: {
        ...currentState.intentsByTemplateId,
        [state.templateId]: nextIntent,
      },
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
    };
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

export function buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-audit-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-conflict-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function limitPredicateRefReplayApplySyncAuditEntries(entries: PredicateRefReplayApplySyncAuditEntry[]) {
  return entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES);
}

export function mergePredicateRefReplayApplySyncAuditEntries(
  currentEntries: PredicateRefReplayApplySyncAuditEntry[],
  incomingEntries: PredicateRefReplayApplySyncAuditEntry[],
) {
  const seen = new Set<string>();
  const merged = [...incomingEntries, ...currentEntries].filter((entry) => {
    const dedupeKey = `${entry.entryId}:${entry.kind}:${entry.at}:${entry.sourceTabId}`;
    if (seen.has(dedupeKey)) {
      return false;
    }
    seen.add(dedupeKey);
    return true;
  });
  return limitPredicateRefReplayApplySyncAuditEntries(merged);
}

export function limitPredicateRefReplayApplyConflictEntries(
  entries: PredicateRefReplayApplyConflictEntry[],
) {
  return entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES);
}

export function serializeComparablePredicateRefReplayApplyHistoryEntry(entry: PredicateRefReplayApplyHistoryEntry) {
  return JSON.stringify({
    appliedAt: entry.appliedAt,
    approvedCount: entry.approvedCount,
    changedCurrentCount: entry.changedCurrentCount,
    id: entry.id,
    lastRestoredAt: entry.lastRestoredAt ?? null,
    lastRestoredByTabId: entry.lastRestoredByTabId ?? null,
    matchesSimulationCount: entry.matchesSimulationCount,
    rollbackSnapshot: entry.rollbackSnapshot,
    rows: entry.rows,
    sourceTabId: entry.sourceTabId ?? null,
    templateId: entry.templateId,
    templateLabel: entry.templateLabel,
  });
}

export function arePredicateRefReplayApplyHistoryEntriesEquivalent(
  left: PredicateRefReplayApplyHistoryEntry,
  right: PredicateRefReplayApplyHistoryEntry,
) {
  return serializeComparablePredicateRefReplayApplyHistoryEntry(left)
    === serializeComparablePredicateRefReplayApplyHistoryEntry(right);
}

export function serializeComparablePredicateRefReplayApplyHistoryRow(row?: PredicateRefReplayApplyHistoryRow | null) {
  if (!row) {
    return "";
  }
  return JSON.stringify(row);
}

export function formatPredicateRefReplayApplyHistorySnapshotValue(value?: string | null) {
  if (value === null || value === undefined) {
    return "clear";
  }
  return value || '""';
}

export function formatPredicateRefReplayApplyHistorySelectionKeyLabel(selectionKey: string) {
  const parts = selectionKey.split(":").filter(Boolean);
  return parts.length ? parts[parts.length - 1] : selectionKey;
}

export function formatPredicateRefReplayApplyHistoryRowSummary(row?: PredicateRefReplayApplyHistoryRow | null) {
  if (!row) {
    return "No replay row in this version.";
  }
  return `${row.currentStatus} · ${row.currentBundleLabel} → ${row.promotedBundleLabel} · simulated ${row.simulatedStatus} · ${row.simulatedBundleLabel}`;
}

export function clonePredicateRefReplayApplyHistoryEntry(
  entry: PredicateRefReplayApplyHistoryEntry,
): PredicateRefReplayApplyHistoryEntry {
  return {
    ...entry,
    rollbackSnapshot: {
      draftBindingsByParameterKey: { ...entry.rollbackSnapshot.draftBindingsByParameterKey },
      groupSelectionsBySelectionKey: { ...entry.rollbackSnapshot.groupSelectionsBySelectionKey },
    },
    rows: entry.rows.map((row) => ({ ...row })),
  };
}

export function buildPredicateRefReplayApplyConflictResolutionPreview(
  conflict: PredicateRefReplayApplyConflictEntry,
  entry: PredicateRefReplayApplyHistoryEntry,
  resolution: "local" | "remote" | "merged",
  effect: string,
): PredicateRefReplayApplyConflictResolutionPreview {
  const rollbackGroupCount = Object.keys(entry.rollbackSnapshot.groupSelectionsBySelectionKey).length;
  const rollbackBindingCount = Object.keys(entry.rollbackSnapshot.draftBindingsByParameterKey).length;
  return {
    resolution,
    entry,
    title:
      resolution === "local"
        ? "Keep local version"
        : resolution === "remote"
          ? "Apply remote version"
          : "Apply reviewed merge",
    effect,
    snapshotSummary: `${rollbackGroupCount} rollback groups · ${rollbackBindingCount} rollback bindings`,
    rowSummaries: entry.rows.slice(0, 3).map(
      (row) => `${row.groupLabel}: ${row.currentBundleLabel} → ${row.promotedBundleLabel}`,
    ),
    matchesLocal: arePredicateRefReplayApplyHistoryEntriesEquivalent(entry, conflict.localEntry),
    matchesRemote: arePredicateRefReplayApplyHistoryEntriesEquivalent(entry, conflict.remoteEntry),
  };
}

export function buildPredicateRefReplayApplyConflictMergedEntry(
  conflict: PredicateRefReplayApplyConflictEntry,
  selectedSources: Record<string, "local" | "remote">,
) {
  const mergedEntry = clonePredicateRefReplayApplyHistoryEntry(conflict.localEntry);
  const getSelectedSource = (decisionKey: string) => selectedSources[decisionKey] ?? "local";
  const applyScalar = <K extends keyof PredicateRefReplayApplyHistoryEntry>(
    decisionKey: string,
    fieldKey: K,
  ) => {
    if (getSelectedSource(decisionKey) === "remote") {
      mergedEntry[fieldKey] = conflict.remoteEntry[fieldKey];
    }
  };
  applyScalar("summary:applied_at", "appliedAt");
  if (getSelectedSource("summary:source_tab") === "remote") {
    mergedEntry.sourceTabId = conflict.remoteEntry.sourceTabId ?? null;
    mergedEntry.sourceTabLabel = conflict.remoteEntry.sourceTabLabel ?? null;
  }
  if (getSelectedSource("summary:last_restored_at") === "remote") {
    mergedEntry.lastRestoredAt = conflict.remoteEntry.lastRestoredAt ?? null;
  }
  if (getSelectedSource("summary:last_restored_by") === "remote") {
    mergedEntry.lastRestoredByTabId = conflict.remoteEntry.lastRestoredByTabId ?? null;
    mergedEntry.lastRestoredByTabLabel = conflict.remoteEntry.lastRestoredByTabLabel ?? null;
  }

  const rowGroupKeys = Array.from(
    new Set([
      ...conflict.localEntry.rows.map((row) => row.groupKey),
      ...conflict.remoteEntry.rows.map((row) => row.groupKey),
    ]),
  );
  const mergedRows = rowGroupKeys.flatMap((groupKey) => {
    const source = getSelectedSource(`row:${groupKey}`);
    const sourceRow = (
      source === "remote"
        ? conflict.remoteEntry.rows.find((row) => row.groupKey === groupKey)
        : conflict.localEntry.rows.find((row) => row.groupKey === groupKey)
    ) ?? null;
    return sourceRow ? [{ ...sourceRow }] : [];
  });
  mergedEntry.rows = mergedRows.sort((left, right) => left.groupKey.localeCompare(right.groupKey));
  mergedEntry.approvedCount = mergedEntry.rows.length;
  mergedEntry.changedCurrentCount = mergedEntry.rows.filter((row) => row.changesCurrent).length;
  mergedEntry.matchesSimulationCount = mergedEntry.rows.filter((row) => row.matchesSimulation).length;

  const applySnapshotRecord = (
    decisionKey: string,
    snapshotKey: string,
    fieldKey: "groupSelectionsBySelectionKey" | "draftBindingsByParameterKey",
  ) => {
    const sourceRecord = (
      getSelectedSource(decisionKey) === "remote"
        ? conflict.remoteEntry.rollbackSnapshot[fieldKey]
        : conflict.localEntry.rollbackSnapshot[fieldKey]
    );
    if (Object.prototype.hasOwnProperty.call(sourceRecord, snapshotKey)) {
      mergedEntry.rollbackSnapshot[fieldKey][snapshotKey] = sourceRecord[snapshotKey] ?? null;
      return;
    }
    delete mergedEntry.rollbackSnapshot[fieldKey][snapshotKey];
  };
  Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
    ]),
  ).forEach((selectionKey) => {
    applySnapshotRecord(
      `selection_snapshot:${selectionKey}`,
      selectionKey,
      "groupSelectionsBySelectionKey",
    );
  });
  Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.draftBindingsByParameterKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.draftBindingsByParameterKey),
    ]),
  ).forEach((parameterKey) => {
    applySnapshotRecord(
      `binding_snapshot:${parameterKey}`,
      parameterKey,
      "draftBindingsByParameterKey",
    );
  });
  return mergedEntry;
}
