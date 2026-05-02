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
import { loadRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases, pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases, mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts, areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual, readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, persistRunSurfaceCollectionQueryBuilderReplayIntent, buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId, buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId, limitPredicateRefReplayApplySyncAuditEntries, mergePredicateRefReplayApplySyncAuditEntries, limitPredicateRefReplayApplyConflictEntries, serializeComparablePredicateRefReplayApplyHistoryEntry, arePredicateRefReplayApplyHistoryEntriesEquivalent, serializeComparablePredicateRefReplayApplyHistoryRow, formatPredicateRefReplayApplyHistorySnapshotValue, formatPredicateRefReplayApplyHistorySelectionKeyLabel, formatPredicateRefReplayApplyHistoryRowSummary, clonePredicateRefReplayApplyHistoryEntry, buildPredicateRefReplayApplyConflictResolutionPreview, buildPredicateRefReplayApplyConflictMergedEntry } from "./modelReplayStorage";
import { buildPredicateRefReplayApplyConflictReview, normalizePredicateRefReplayApplySyncAuditEntry, normalizePredicateRefReplayApplyConflictEntry, loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts, persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts, normalizeReplayApplySnapshotRecord, normalizePredicateRefReplayApplyHistoryEntry, parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue, loadRunSurfaceCollectionQueryBuilderReplayApplyHistory, serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory, persistRunSurfaceCollectionQueryBuilderReplayApplyHistory, mergePredicateRefReplayApplyHistoryEntries } from "./modelReplayApply";
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export function normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(
  parsed: Partial<RunSurfaceCollectionQueryBuilderReplayIntentSnapshot> | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null {
  if (!parsed) {
    return null;
  }
  return {
    previewSelection: {
      diffItemKey: typeof parsed.previewSelection?.diffItemKey === "string"
        ? parsed.previewSelection.diffItemKey
        : null,
      groupKey: typeof parsed.previewSelection?.groupKey === "string"
        ? parsed.previewSelection.groupKey
        : null,
      traceKey: typeof parsed.previewSelection?.traceKey === "string"
        ? parsed.previewSelection.traceKey
        : null,
    },
    replayActionTypeFilter:
      parsed.replayActionTypeFilter === "manual_anchor"
      || parsed.replayActionTypeFilter === "dependency_selection"
      || parsed.replayActionTypeFilter === "direct_auto_selection"
      || parsed.replayActionTypeFilter === "conflict_blocked"
      || parsed.replayActionTypeFilter === "idle"
        ? parsed.replayActionTypeFilter
        : "all",
    replayEdgeFilter:
      parsed.replayEdgeFilter === "all"
      || typeof parsed.replayEdgeFilter === "string"
        ? parsed.replayEdgeFilter
        : "all",
    replayGroupFilter:
      parsed.replayGroupFilter === "all"
      || typeof parsed.replayGroupFilter === "string"
        ? parsed.replayGroupFilter
        : "all",
    replayIndex:
      typeof parsed.replayIndex === "number" && Number.isFinite(parsed.replayIndex)
        ? Math.max(0, Math.floor(parsed.replayIndex))
        : 0,
    replayScope:
      parsed.replayScope === "all"
      || typeof parsed.replayScope === "string"
        ? parsed.replayScope
        : "all",
  };
}

export function areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(
  left: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null,
  right: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null,
) {
  if (left === right) {
    return true;
  }
  if (!left || !right) {
    return false;
  }
  return JSON.stringify(left) === JSON.stringify(right);
}

export function readRunSurfaceCollectionQueryBuilderReplayIntentStorageState(
  raw: string | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayIntentStorageState | null {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as
      | Partial<RunSurfaceCollectionQueryBuilderReplayIntentStorageState>
      | Partial<RunSurfaceCollectionQueryBuilderReplayIntentState>
      | null;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return null;
    }
    const parsedStorageState = parsed as Partial<RunSurfaceCollectionQueryBuilderReplayIntentStorageState>;
    if (
      parsedStorageState.version === RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION
      && parsedStorageState.intentsByTemplateId
      && typeof parsedStorageState.intentsByTemplateId === "object"
      && !Array.isArray(parsedStorageState.intentsByTemplateId)
    ) {
      const intentsByTemplateId = Object.entries(parsedStorageState.intentsByTemplateId).reduce<Record<string, RunSurfaceCollectionQueryBuilderReplayIntentSnapshot>>(
        (acc, [templateId, candidate]) => {
          const normalized = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(
            candidate as Partial<RunSurfaceCollectionQueryBuilderReplayIntentSnapshot>,
          );
          if (normalized) {
            acc[templateId] = normalized;
          }
          return acc;
        },
        {},
      );
      return {
        intentsByTemplateId,
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
      };
    }
    if (
      parsed.version === 1
      && typeof (parsed as Partial<RunSurfaceCollectionQueryBuilderReplayIntentState>).templateId === "string"
    ) {
      const legacy = parsed as Partial<RunSurfaceCollectionQueryBuilderReplayIntentState>;
      const normalized = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(legacy);
      if (!normalized) {
        return null;
      }
      return {
        intentsByTemplateId: {
          [legacy.templateId as string]: normalized,
        },
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
      };
    }
    return null;
  } catch {
    return null;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayIntent(
  templateId: string | null | undefined,
  rawOverride?: string | null,
): RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null {
  if (!templateId) {
    return null;
  }
  const raw =
    typeof rawOverride === "string" || rawOverride === null
      ? rawOverride
      : (typeof window === "undefined"
        ? null
        : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY));
  const parsedState = readRunSurfaceCollectionQueryBuilderReplayIntentStorageState(raw);
  if (!parsedState) {
    return null;
  }
  return parsedState.intentsByTemplateId[templateId] ?? null;
}

export function readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(
  value: unknown,
): RunSurfaceCollectionQueryBuilderReplayIntentBrowserState | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const candidate = (value as Record<string, unknown>)[RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY];
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) {
    return null;
  }
  const parsed = candidate as Partial<RunSurfaceCollectionQueryBuilderReplayIntentBrowserState>;
  if (
    parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION
    || typeof parsed.templateId !== "string"
  ) {
    return null;
  }
  const normalizedIntent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(parsed.intent);
  if (!normalizedIntent) {
    return null;
  }
  return {
    intent: normalizedIntent,
    templateId: parsed.templateId,
    version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
  };
}

export function buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(
  currentState: unknown,
  templateId: string,
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
) {
  const nextState =
    currentState && typeof currentState === "object" && !Array.isArray(currentState)
      ? { ...(currentState as Record<string, unknown>) }
      : {};
  nextState[RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY] = {
    intent,
    templateId,
    version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
  } satisfies RunSurfaceCollectionQueryBuilderReplayIntentBrowserState;
  return nextState;
}

export function isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null | undefined,
) {
  if (!intent) {
    return true;
  }
  return (
    intent.replayScope === "all"
    && intent.replayIndex === 0
    && intent.replayGroupFilter === "all"
    && intent.replayActionTypeFilter === "all"
    && intent.replayEdgeFilter === "all"
    && intent.previewSelection.groupKey === null
    && intent.previewSelection.traceKey === null
    && intent.previewSelection.diffItemKey === null
  );
}

export function encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
  templateKey: string,
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
) {
  if (isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(intent)) {
    return null;
  }
  const payload: Record<string, string | number> = {
    t: templateKey,
  };
  if (intent.replayScope !== "all") {
    payload.s = intent.replayScope;
  }
  if (intent.replayIndex > 0) {
    payload.i = intent.replayIndex;
  }
  if (intent.replayGroupFilter !== "all") {
    payload.g = intent.replayGroupFilter;
  }
  if (intent.replayActionTypeFilter !== "all") {
    payload.a = intent.replayActionTypeFilter;
  }
  if (intent.replayEdgeFilter !== "all") {
    payload.e = intent.replayEdgeFilter;
  }
  if (intent.previewSelection.groupKey) {
    payload.pg = intent.previewSelection.groupKey;
  }
  if (intent.previewSelection.traceKey) {
    payload.pt = intent.previewSelection.traceKey;
  }
  if (intent.previewSelection.diffItemKey) {
    payload.pd = intent.previewSelection.diffItemKey;
  }
  try {
    const json = JSON.stringify(payload);
    if (typeof TextEncoder !== "undefined" && typeof btoa === "function") {
      const bytes = new TextEncoder().encode(json);
      let binary = "";
      bytes.forEach((byte) => {
        binary += String.fromCharCode(byte);
      });
      return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
    if (typeof btoa === "function") {
      return btoa(json).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
  } catch {
    return null;
  }
  return null;
}

export function decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(value: string | null | undefined): {
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null;
  templateKey: string | null;
} | null {
  const compactValue = value?.trim() ?? "";
  if (!compactValue) {
    return null;
  }
  try {
    if (typeof atob !== "function") {
      return null;
    }
    const paddedValue = compactValue.replace(/-/g, "+").replace(/_/g, "/");
    const normalizedValue = `${paddedValue}${"===".slice((paddedValue.length + 3) % 4)}`;
    const binary = atob(normalizedValue);
    const json =
      typeof TextDecoder !== "undefined"
        ? new TextDecoder().decode(Uint8Array.from(binary, (char) => char.charCodeAt(0)))
        : binary;
    const parsed = JSON.parse(json) as Partial<Record<"t" | "s" | "i" | "g" | "a" | "e" | "pg" | "pt" | "pd", string | number>> | null;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed) || typeof parsed.t !== "string") {
      return null;
    }
    const replayActionTypeFilter =
      parsed.a === "all"
      || parsed.a === "manual_anchor"
      || parsed.a === "dependency_selection"
      || parsed.a === "direct_auto_selection"
      || parsed.a === "conflict_blocked"
      || parsed.a === "idle"
        ? parsed.a
        : undefined;
    return {
      intent: normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot({
        previewSelection: {
          diffItemKey: typeof parsed.pd === "string" ? parsed.pd : null,
          groupKey: typeof parsed.pg === "string" ? parsed.pg : null,
          traceKey: typeof parsed.pt === "string" ? parsed.pt : null,
        },
        replayActionTypeFilter,
        replayEdgeFilter: typeof parsed.e === "string" ? parsed.e : undefined,
        replayGroupFilter: typeof parsed.g === "string" ? parsed.g : undefined,
        replayIndex: typeof parsed.i === "number" ? parsed.i : undefined,
        replayScope: typeof parsed.s === "string" ? parsed.s : undefined,
      }),
      templateKey: parsed.t.trim() || null,
    };
  } catch {
    return null;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl(): {
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null;
  templateKey: string | null;
} | null {
  if (typeof window === "undefined") {
    return null;
  }
  const params = new URL(window.location.href).searchParams;
  const aliasToken = parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
    params.get(REPLAY_INTENT_ALIAS_SEARCH_PARAM),
  );
  if (aliasToken?.aliasId) {
    const aliasEntry =
      loadRunSurfaceCollectionQueryBuilderReplayLinkAliases().find((entry) => entry.aliasId === aliasToken.aliasId)
      ?? null;
    if (aliasEntry && aliasEntry.resolutionSource !== "server" && !aliasEntry.revokedAt) {
      const recomputedSignature = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature(
        aliasEntry,
        loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret(),
      );
      const signatureMatches =
        aliasEntry.signature
          ? aliasToken.signature === aliasEntry.signature && aliasEntry.signature === recomputedSignature
          : !aliasToken.signature;
      if (signatureMatches) {
        return {
          intent: aliasEntry.intent,
          templateKey: aliasEntry.templateKey,
        };
      }
    }
  }
  const compactIntent = decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
    params.get(REPLAY_INTENT_SEARCH_PARAM),
  );
  if (compactIntent) {
    return compactIntent;
  }
  const templateKey = params.get(REPLAY_INTENT_TEMPLATE_SEARCH_PARAM)?.trim() ?? "";
  const hasReplayParam = [
    REPLAY_INTENT_TEMPLATE_SEARCH_PARAM,
    REPLAY_INTENT_SCOPE_SEARCH_PARAM,
    REPLAY_INTENT_STEP_SEARCH_PARAM,
    REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM,
    REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM,
    REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM,
    REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM,
    REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM,
    REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM,
  ].some((key) => params.has(key));
  if (!hasReplayParam) {
    return null;
  }
  const replayActionTypeFilterRaw = params.get(REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM)?.trim() ?? "";
  const replayActionTypeFilter:
    RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayActionTypeFilter"]
    | undefined =
      replayActionTypeFilterRaw === "all"
      || replayActionTypeFilterRaw === "manual_anchor"
      || replayActionTypeFilterRaw === "dependency_selection"
      || replayActionTypeFilterRaw === "direct_auto_selection"
      || replayActionTypeFilterRaw === "conflict_blocked"
      || replayActionTypeFilterRaw === "idle"
        ? replayActionTypeFilterRaw
        : undefined;
  const intent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot({
    previewSelection: {
      diffItemKey: params.get(REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM)?.trim() ?? null,
      groupKey: params.get(REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM)?.trim() ?? null,
      traceKey: params.get(REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM)?.trim() ?? null,
    },
    replayActionTypeFilter,
    replayEdgeFilter: params.get(REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM)?.trim() ?? undefined,
    replayGroupFilter: params.get(REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM)?.trim() ?? undefined,
    replayIndex: (() => {
      const raw = params.get(REPLAY_INTENT_STEP_SEARCH_PARAM);
      if (raw === null) {
        return undefined;
      }
      const parsed = Number(raw);
      return Number.isFinite(parsed) ? parsed : undefined;
    })(),
    replayScope: params.get(REPLAY_INTENT_SCOPE_SEARCH_PARAM)?.trim() ?? undefined,
  });
  return {
    intent,
    templateKey: templateKey || null,
  };
}

export function buildRunSurfaceCollectionQueryBuilderReplayIntentUrl(
  templateKey: string | null | undefined,
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null,
  baseHref?: string,
  options?: {
    aliasId?: string | null;
    forceTemplateKey?: boolean;
  },
) {
  const url =
    typeof window !== "undefined"
      ? new URL(baseHref ?? window.location.href)
      : new URL(baseHref ?? "http://localhost/");
  const params = url.searchParams;
  params.delete(REPLAY_INTENT_ALIAS_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_TEMPLATE_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_SCOPE_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_STEP_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM);
  if (options?.aliasId?.trim()) {
    params.set(REPLAY_INTENT_ALIAS_SEARCH_PARAM, options.aliasId.trim());
    const nextSearch = params.toString();
    return `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash}`;
  }
  const normalizedIntent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(intent);
  const normalizedTemplateKey = templateKey?.trim() ?? "";
  const shouldEmitTemplateIntent =
    normalizedTemplateKey
    && normalizedIntent
    && (
      options?.forceTemplateKey
      || !isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(normalizedIntent)
    );
  if (shouldEmitTemplateIntent) {
    const compactValue = encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
      normalizedTemplateKey,
      normalizedIntent,
    );
    if (compactValue && !options?.forceTemplateKey) {
      params.set(REPLAY_INTENT_SEARCH_PARAM, compactValue);
    } else {
      params.set(REPLAY_INTENT_TEMPLATE_SEARCH_PARAM, normalizedTemplateKey);
      if (normalizedIntent.replayScope !== "all") {
        params.set(REPLAY_INTENT_SCOPE_SEARCH_PARAM, normalizedIntent.replayScope);
      }
      if (normalizedIntent.replayIndex > 0) {
        params.set(REPLAY_INTENT_STEP_SEARCH_PARAM, String(normalizedIntent.replayIndex));
      }
      if (normalizedIntent.replayGroupFilter !== "all") {
        params.set(REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM, normalizedIntent.replayGroupFilter);
      }
      if (normalizedIntent.replayActionTypeFilter !== "all") {
        params.set(REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM, normalizedIntent.replayActionTypeFilter);
      }
      if (normalizedIntent.replayEdgeFilter !== "all") {
        params.set(REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM, normalizedIntent.replayEdgeFilter);
      }
      if (normalizedIntent.previewSelection.groupKey) {
        params.set(REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM, normalizedIntent.previewSelection.groupKey);
      }
      if (normalizedIntent.previewSelection.traceKey) {
        params.set(REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM, normalizedIntent.previewSelection.traceKey);
      }
      if (normalizedIntent.previewSelection.diffItemKey) {
        params.set(REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM, normalizedIntent.previewSelection.diffItemKey);
      }
    }
  }
  const nextSearch = params.toString();
  return `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash}`;
}

export function applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy(
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
  policy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
): RunSurfaceCollectionQueryBuilderReplayIntentSnapshot {
  if (policy === "full") {
    return intent;
  }
  if (policy === "omit_preview") {
    return {
      ...intent,
      previewSelection: {
        diffItemKey: null,
        groupKey: null,
        traceKey: null,
      },
    };
  }
  return {
    previewSelection: {
      diffItemKey: null,
      groupKey: null,
      traceKey: null,
    },
    replayActionTypeFilter: intent.replayActionTypeFilter,
    replayEdgeFilter: "all",
    replayGroupFilter: intent.replayGroupFilter,
    replayIndex: 0,
    replayScope: intent.replayScope,
  };
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId() {
  const randomSegment = Math.random().toString(36).slice(2, 10);
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID().replace(/-/g, "").slice(0, 10);
  }
  return `rl${randomSegment}`.slice(0, 10);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-link-audit-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
  value: unknown,
): RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy {
  return value === "1d" || value === "7d" || value === "manual" ? value : "30d";
}

export function getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  switch (retentionPolicy) {
    case "1d":
      return 24 * 60 * 60 * 1000;
    case "7d":
      return 7 * 24 * 60 * 60 * 1000;
    case "30d":
      return 30 * 24 * 60 * 60 * 1000;
    case "manual":
    default:
      return null;
  }
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry(
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  createdAt: string,
) {
  const duration = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  if (!duration) {
    return null;
  }
  const createdAtMs = Date.parse(createdAt);
  if (!Number.isFinite(createdAtMs)) {
    return null;
  }
  return new Date(createdAtMs + duration).toISOString();
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-link-secret-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret() {
  if (typeof window === "undefined") {
    return "replay-link-secret";
  }
  try {
    const existingSecret =
      window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY)?.trim();
    if (existingSecret) {
      return existingSecret;
    }
    const nextSecret = buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret();
    window.localStorage.setItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY, nextSecret);
    return nextSecret;
  } catch {
    return "replay-link-secret";
  }
}

export function hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment(input: string) {
  let hash = 2166136261;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }
  return (hash >>> 0).toString(36);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload(
  entry: Pick<
    RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
    "aliasId" | "createdAt" | "expiresAt" | "intent" | "redactionPolicy" | "templateKey"
  >,
) {
  return JSON.stringify({
    a: entry.aliasId,
    c: entry.createdAt,
    e: entry.expiresAt,
    i: entry.intent,
    r: entry.redactionPolicy,
    t: entry.templateKey,
  });
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature(
  entry: Pick<
    RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
    "aliasId" | "createdAt" | "expiresAt" | "intent" | "redactionPolicy" | "templateKey"
  >,
  signingSecret: string,
) {
  const payload = `${signingSecret}:${buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload(entry)}`;
  const primary = hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment(payload);
  const secondary = hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment(
    payload.split("").reverse().join(""),
  );
  return `${primary}${secondary}`.slice(0, 18);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
  aliasId: string,
  signature: string | null | undefined,
) {
  return signature?.trim() ? `${aliasId}.${signature.trim()}` : aliasId;
}

export function parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
  value: string | null | undefined,
) {
  const token = value?.trim() ?? "";
  if (!token) {
    return null;
  }
  const lastSeparatorIndex = token.lastIndexOf(".");
  if (lastSeparatorIndex <= 0) {
    return {
      aliasId: token,
      signature: null,
    };
  }
  return {
    aliasId: token.slice(0, lastSeparatorIndex),
    signature: token.slice(lastSeparatorIndex + 1) || null,
  };
}

export function extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl() {
  if (typeof window === "undefined") {
    return null;
  }
  return parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
    new URL(window.location.href).searchParams.get(REPLAY_INTENT_ALIAS_SEARCH_PARAM),
  );
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-link-governance-audit-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot(
  state: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
) {
  return {
    redactionPolicy: state.redactionPolicy,
    retentionPolicy: state.retentionPolicy,
    shareMode: state.shareMode,
    syncMode: state.syncMode,
  } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
}

export function getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(
  fromState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  toState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
) {
  const diffKeys: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey[] = [];
  if (fromState.shareMode !== toState.shareMode) {
    diffKeys.push("shareMode");
  }
  if (fromState.redactionPolicy !== toState.redactionPolicy) {
    diffKeys.push("redactionPolicy");
  }
  if (fromState.retentionPolicy !== toState.retentionPolicy) {
    diffKeys.push("retentionPolicy");
  }
  if (fromState.syncMode !== toState.syncMode) {
    diffKeys.push("syncMode");
  }
  return diffKeys;
}

export function formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue(
  fieldKey: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey,
  state: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
) {
  switch (fieldKey) {
    case "shareMode":
      return state.shareMode === "indirect" ? "Local alias link" : "Portable deep link";
    case "redactionPolicy":
      return state.redactionPolicy.replaceAll("_", " ");
    case "retentionPolicy":
      return state.retentionPolicy === "manual"
        ? "Keep until cleared"
        : state.retentionPolicy === "1d"
          ? "1 day"
          : state.retentionPolicy === "7d"
            ? "7 days"
            : "30 days";
    case "syncMode":
      return state.syncMode === "opt_out"
        ? "Ignore remote changes"
        : state.syncMode === "review"
          ? "Review remote changes"
          : "Live sync";
    default:
      return "n/a";
  }
}

export function encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload(
  payload: RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
) {
  try {
    const json = JSON.stringify(payload);
    if (typeof TextEncoder !== "undefined" && typeof btoa === "function") {
      const bytes = new TextEncoder().encode(json);
      let binary = "";
      bytes.forEach((byte) => {
        binary += String.fromCharCode(byte);
      });
      return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
    if (typeof btoa === "function") {
      return btoa(json).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
  } catch {
    return null;
  }
  return null;
}

export function decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload(
  value: string | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload | null {
  const compactValue = value?.trim() ?? "";
  if (!compactValue || typeof atob !== "function") {
    return null;
  }
  try {
    const paddedValue = compactValue.replace(/-/g, "+").replace(/_/g, "/");
    const normalizedValue = `${paddedValue}${"===".slice((paddedValue.length + 3) % 4)}`;
    const binary = atob(normalizedValue);
    const json =
      typeof TextDecoder !== "undefined"
        ? new TextDecoder().decode(Uint8Array.from(binary, (char) => char.charCodeAt(0)))
        : binary;
    const parsed = JSON.parse(json) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION
      || !parsed.governance
      || typeof parsed.sourceTabId !== "string"
      || typeof parsed.sourceTabLabel !== "string"
      || typeof parsed.exportedAt !== "string"
    ) {
      return null;
    }
    return {
      exportedAt: parsed.exportedAt,
      governance: {
        redactionPolicy:
          parsed.governance.redactionPolicy === "omit_preview"
          || parsed.governance.redactionPolicy === "summary_only"
            ? parsed.governance.redactionPolicy
            : "full",
        retentionPolicy: normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
          parsed.governance.retentionPolicy,
        ),
        shareMode: parsed.governance.shareMode === "indirect" ? "indirect" : "portable",
        syncMode:
          parsed.governance.syncMode === "opt_out" || parsed.governance.syncMode === "review"
            ? parsed.governance.syncMode
            : "live",
      },
      sourceTabId: parsed.sourceTabId,
      sourceTabLabel: parsed.sourceTabLabel,
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION,
    };
  } catch {
    return null;
  }
}
