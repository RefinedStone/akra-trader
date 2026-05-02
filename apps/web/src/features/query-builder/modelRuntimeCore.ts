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
import { collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts, normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey, buildRunSurfaceCollectionQueryRuntimeCandidateReplayId, collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries, scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch, doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch, buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys, buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems, buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause, buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection } from "./modelRuntimeArtifacts";
import { PredicateRefReplayApplyHistoryRow, PredicateRefReplayApplyHistoryEntry, PredicateRefReplayApplyHistoryTabIdentity, PredicateRefReplayApplySyncMode, PredicateRefReplayApplySyncAuditFilter, PredicateRefReplayApplyConflictPolicy, PredicateRefReplayApplyConflictEntry, PredicateRefReplayApplyConflictDiffItem, PredicateRefReplayApplyConflictResolutionPreview, PredicateRefReplayApplyConflictReview, PredicateRefReplayApplyConflictDraftReview, PredicateRefReplayApplySyncAuditEntry, PredicateRefReplayApplySyncAuditTrailState, PredicateRefReplayApplySyncGovernanceState, RunSurfaceCollectionQueryBuilderReplayIntentState, RunSurfaceCollectionQueryBuilderReplayIntentStorageState, RunSurfaceCollectionQueryBuilderReplayIntentBrowserState, RunSurfaceCollectionQueryBuilderReplayLinkShareMode, RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry, RunSurfaceCollectionQueryBuilderReplayLinkAliasState, RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry, PredicateRefReplayApplyConflictState, HydratedRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderEditorTarget, RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID, buildRunSurfaceCollectionQueryBuilderEntityId, buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId, formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel, loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity, loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState } from "./modelReplayState";
import { normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot, areRunSurfaceCollectionQueryBuilderReplayIntentsEqual, readRunSurfaceCollectionQueryBuilderReplayIntentStorageState, loadRunSurfaceCollectionQueryBuilderReplayIntent, readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, isDefaultRunSurfaceCollectionQueryBuilderReplayIntent, encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl, buildRunSurfaceCollectionQueryBuilderReplayIntentUrl, applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId, buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId, normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs, buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry, buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys, formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue, encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload } from "./modelReplayIntent";
import { loadRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases, pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases, mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts, areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual, readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, persistRunSurfaceCollectionQueryBuilderReplayIntent, buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId, buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId, limitPredicateRefReplayApplySyncAuditEntries, mergePredicateRefReplayApplySyncAuditEntries, limitPredicateRefReplayApplyConflictEntries, serializeComparablePredicateRefReplayApplyHistoryEntry, arePredicateRefReplayApplyHistoryEntriesEquivalent, serializeComparablePredicateRefReplayApplyHistoryRow, formatPredicateRefReplayApplyHistorySnapshotValue, formatPredicateRefReplayApplyHistorySelectionKeyLabel, formatPredicateRefReplayApplyHistoryRowSummary, clonePredicateRefReplayApplyHistoryEntry, buildPredicateRefReplayApplyConflictResolutionPreview, buildPredicateRefReplayApplyConflictMergedEntry } from "./modelReplayStorage";
import { buildPredicateRefReplayApplyConflictReview, normalizePredicateRefReplayApplySyncAuditEntry, normalizePredicateRefReplayApplyConflictEntry, loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts, persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts, normalizeReplayApplySnapshotRecord, normalizePredicateRefReplayApplyHistoryEntry, parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue, loadRunSurfaceCollectionQueryBuilderReplayApplyHistory, serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory, persistRunSurfaceCollectionQueryBuilderReplayApplyHistory, mergePredicateRefReplayApplyHistoryEntries } from "./modelReplayApply";
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export type HydratedRunSurfaceCollectionQueryBuilderState = {
  contractKey: string;
  schemaId: string;
  parameterValues: Record<string, string>;
  parameterBindingKeys: Record<string, string>;
  quantifier: "any" | "all" | "none";
  fieldKey: string;
  operatorKey: string;
  builderValue: string;
  valueBindingKey: string;
  negated: boolean;
};

export type RunSurfaceCollectionQueryBuilderClauseState = {
  id: string;
  kind: "clause";
  clause: HydratedRunSurfaceCollectionQueryBuilderState;
};

export type RunSurfaceCollectionQueryBuilderPredicateRefState = {
  id: string;
  kind: "predicate_ref";
  predicateKey: string;
  bindings: Record<string, string>;
  negated: boolean;
};

export type RunSurfaceCollectionQueryBuilderGroupState = {
  id: string;
  kind: "group";
  logic: "and" | "or";
  negated: boolean;
  children: RunSurfaceCollectionQueryBuilderChildState[];
};

export type RunSurfaceCollectionQueryBuilderChildState =
  | RunSurfaceCollectionQueryBuilderClauseState
  | RunSurfaceCollectionQueryBuilderPredicateRefState
  | {
      id: string;
      kind: "group";
      logic: "and" | "or";
      negated: boolean;
      children: RunSurfaceCollectionQueryBuilderChildState[];
    };

export type RunSurfaceCollectionQueryBuilderPredicateState = {
  id: string;
  key: string;
  node: RunSurfaceCollectionQueryBuilderChildState;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState = {
  key: string;
  label: string;
  customLabel: string;
  groupName: string;
  helpNote: string;
  valueType: string;
  description: string | null;
  options: string[];
  defaultValue: string;
  bindingPreset: string;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState = {
  key: string;
  label: string;
  helpNote: string;
  collapsedByDefault: boolean;
  visibilityRule: "always" | "manual" | "binding_active" | "value_active";
  coordinationPolicy: "manual_source_priority" | "highest_source_priority" | "sticky_auto_selection" | "manual_resolution";
  presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState = {
  key: string;
  groupKey: string;
  bundleKey: string;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState = {
  key: string;
  label: string;
  helpNote: string;
  priority: number;
  autoSelectRule: "manual" | "always" | "binding_active" | "value_active";
  dependencies: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState[];
  parameterValues: Record<string, string>;
  parameterBindingPresets: Record<string, string>;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateState = {
  id: string;
  key: string;
  parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
  parameterGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[];
  node: RunSurfaceCollectionQueryBuilderChildState;
};

export const RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT = 5;
export const RUN_SURFACE_COLLECTION_RUNTIME_MISSING = Symbol("run-surface-collection-runtime-missing");

export type RunSurfaceCollectionQueryRuntimePathToken = string | number;

export type RunSurfaceCollectionQueryRuntimeCollectionItem = {
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[];
  value: unknown;
};

export function formatRunSurfaceCollectionQueryRuntimePathSegment(segment: RunSurfaceCollectionQueryRuntimePathToken) {
  if (typeof segment === "number") {
    return `[${segment}]`;
  }
  return /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(segment)
    ? `.${segment}`
    : `[${JSON.stringify(segment)}]`;
}

export function formatRunSurfaceCollectionQueryRuntimePath(
  rootLabel: string,
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[],
) {
  return `${rootLabel}${pathTokens.map(formatRunSurfaceCollectionQueryRuntimePathSegment).join("")}`;
}

export function normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(
  value: unknown,
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[],
): RunSurfaceCollectionQueryRuntimeCollectionItem[] {
  if (value === null || value === undefined) {
    return [];
  }
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(
      item,
      [...pathTokens, index],
    ));
  }
  if (value instanceof Set) {
    return Array.from(value).flatMap((item, index) => normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(
      item,
      [...pathTokens, index],
    ));
  }
  if (typeof value === "object") {
    return [{ pathTokens, value }];
  }
  return [{ pathTokens, value }];
}

export function resolveRunSurfaceCollectionQueryRuntimeCollectionItems(
  current: unknown,
  path: string[],
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[] = [],
): RunSurfaceCollectionQueryRuntimeCollectionItem[] {
  if (current === null || current === undefined) {
    return [];
  }
  if (!path.length) {
    return normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(current, pathTokens);
  }
  const [segment, ...tail] = path;
  if (Array.isArray(current)) {
    return current.flatMap((item, index) =>
      resolveRunSurfaceCollectionQueryRuntimeCollectionItems(item, path, [...pathTokens, index]));
  }
  if (current instanceof Set) {
    return Array.from(current).flatMap((item, index) =>
      resolveRunSurfaceCollectionQueryRuntimeCollectionItems(item, path, [...pathTokens, index]));
  }
  if (typeof current !== "object") {
    return [];
  }
  const record = current as Record<string, unknown>;
  if (!(segment in record)) {
    return [];
  }
  return resolveRunSurfaceCollectionQueryRuntimeCollectionItems(
    record[segment],
    tail,
    [...pathTokens, segment],
  );
}

export function resolveRunSurfaceCollectionQueryRuntimeValuePath(
  current: unknown,
  path: string[],
): unknown | typeof RUN_SURFACE_COLLECTION_RUNTIME_MISSING {
  let value = current;
  const resolvedPath = path.length ? path : [];
  for (const segment of resolvedPath) {
    if (value === null || value === undefined) {
      return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
    }
    if (Array.isArray(value)) {
      const parsedIndex = Number.parseInt(segment, 10);
      if (Number.isNaN(parsedIndex) || parsedIndex < 0 || parsedIndex >= value.length) {
        return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
      }
      value = value[parsedIndex];
      continue;
    }
    if (typeof value !== "object") {
      return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
    }
    const record = value as Record<string, unknown>;
    if (!(segment in record)) {
      return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
    }
    value = record[segment];
  }
  return value;
}

export function normalizeRunSurfaceCollectionQueryRuntimeNumericValue(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number.parseFloat(value);
    return Number.isNaN(parsed) ? null : parsed;
  }
  return null;
}

export function normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue(value: unknown) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return value;
  }
  if (typeof value !== "string" && typeof value !== "number") {
    return null;
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function toRunSurfaceCollectionQueryRuntimeIterableValues(value: unknown) {
  if (Array.isArray(value)) {
    return value;
  }
  if (value instanceof Set) {
    return Array.from(value);
  }
  if (value === null || value === undefined) {
    return [];
  }
  if (typeof value === "string") {
    return Array.from(value);
  }
  return [value];
}

export function evaluateRunSurfaceCollectionQueryRuntimeCondition(
  candidateValue: unknown,
  operator: string,
  operand: unknown,
) {
  if (operator === "eq") {
    return candidateValue === operand;
  }
  if (operator === "prefix") {
    return typeof candidateValue === "string"
      && typeof operand === "string"
      && candidateValue.startsWith(operand);
  }
  if (operator === "contains_all") {
    const candidateValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(candidateValue));
    const operandValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(operand));
    return Array.from(operandValues).every((value) => candidateValues.has(value));
  }
  if (operator === "contains_any") {
    const candidateValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(candidateValue));
    const operandValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(operand));
    return Array.from(operandValues).some((value) => candidateValues.has(value));
  }
  if (operator === "include") {
    return toRunSurfaceCollectionQueryRuntimeIterableValues(operand).includes(candidateValue);
  }
  if (operator === "gt" || operator === "ge" || operator === "lt" || operator === "le") {
    const candidateDatetime = normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue(candidateValue);
    const operandDatetime = normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue(operand);
    if (candidateDatetime && operandDatetime) {
      if (operator === "gt") {
        return candidateDatetime > operandDatetime;
      }
      if (operator === "ge") {
        return candidateDatetime >= operandDatetime;
      }
      if (operator === "lt") {
        return candidateDatetime < operandDatetime;
      }
      return candidateDatetime <= operandDatetime;
    }
    const candidateNumber = normalizeRunSurfaceCollectionQueryRuntimeNumericValue(candidateValue);
    const operandNumber = normalizeRunSurfaceCollectionQueryRuntimeNumericValue(operand);
    if (candidateNumber === null || operandNumber === null) {
      return false;
    }
    if (operator === "gt") {
      return candidateNumber > operandNumber;
    }
    if (operator === "ge") {
      return candidateNumber >= operandNumber;
    }
    if (operator === "lt") {
      return candidateNumber < operandNumber;
    }
    return candidateNumber <= operandNumber;
  }
  return false;
}

export function evaluateRunSurfaceCollectionQueryRuntimeQuantifierOutcome(
  quantifier: "any" | "all" | "none",
  candidateCount: number,
  matchedCount: number,
) {
  if (quantifier === "any") {
    return matchedCount > 0;
  }
  if (quantifier === "all") {
    return candidateCount > 0 && matchedCount === candidateCount;
  }
  return matchedCount === 0;
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateSamples(params: {
  comparedValueLabel: string;
  comparedValueOperand: unknown;
  field: RunSurfaceCollectionQueryElementField | null;
  quantifier: "any" | "all" | "none";
  resolvedParameterValues: Record<string, string>;
  runs: Run[];
  schema: RunSurfaceCollectionQuerySchema | null;
  operatorKey: string;
}) {
  const {
    comparedValueLabel,
    comparedValueOperand,
    field,
    operatorKey,
    quantifier,
    resolvedParameterValues,
    runs,
    schema,
  } = params;
  if (!schema || !field || !runs.length) {
    return {
      allValues: [] as RunSurfaceCollectionQueryRuntimeCandidateSample[],
      runOutcomes: [] as RunSurfaceCollectionQueryRuntimeQuantifierOutcome[],
      sampleValues: [] as RunSurfaceCollectionQueryRuntimeCandidateSample[],
      sampleMatchCount: 0,
      sampleTotalCount: 0,
      sampleTruncated: false,
    };
  }
  const resolvedPath = resolveCollectionQueryPath(schema.pathTemplate, resolvedParameterValues);
  const accessorPath = field.valueRoot ? [] : (field.valuePath.length ? field.valuePath : [field.key]);
  const accessorLabel = field.valueRoot
    ? `${schema.itemKind} value`
    : `${schema.itemKind}.${accessorPath.join(".") || field.key}`;
  const allValues: RunSurfaceCollectionQueryRuntimeCandidateSample[] = [];
  const runOutcomes: RunSurfaceCollectionQueryRuntimeQuantifierOutcome[] = [];
  let sampleTotalCount = 0;
  let sampleMatchCount = 0;
  runs.forEach((run) => {
    const collectionItems = resolveRunSurfaceCollectionQueryRuntimeCollectionItems(run, resolvedPath);
    let runCandidateCount = 0;
    let runMatchedCount = 0;
    collectionItems.forEach((collectionItem) => {
      runCandidateCount += 1;
      sampleTotalCount += 1;
      const candidateValueRaw = field.valueRoot
        ? collectionItem.value
        : resolveRunSurfaceCollectionQueryRuntimeValuePath(collectionItem.value, accessorPath);
      const candidatePath = formatRunSurfaceCollectionQueryRuntimePath(
        `run:${run.config.run_id}`,
        collectionItem.pathTokens,
      );
      const result = candidateValueRaw === RUN_SURFACE_COLLECTION_RUNTIME_MISSING
        ? false
        : evaluateRunSurfaceCollectionQueryRuntimeCondition(
            candidateValueRaw,
            operatorKey,
            comparedValueOperand,
          );
      if (result) {
        runMatchedCount += 1;
        sampleMatchCount += 1;
      }
      const candidateValue = candidateValueRaw === RUN_SURFACE_COLLECTION_RUNTIME_MISSING
        ? `Missing ${accessorLabel}`
        : formatCollectionQueryBuilderValue(candidateValueRaw, field.valueType);
      const runContextArtifactHoverKeys = buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys({
        candidateValueRaw,
        resolvedParameterValues,
        resolvedPath,
        run,
      });
      const candidateReplayId = buildRunSurfaceCollectionQueryRuntimeCandidateReplayId({
        candidateValueRaw,
        resolvedParameterValues,
        resolvedPath,
      });
      const orderRecord =
        collectionItem.value && typeof collectionItem.value === "object" && !Array.isArray(collectionItem.value)
          ? (collectionItem.value as Record<string, unknown>)
          : null;
      const orderId = typeof orderRecord?.order_id === "string" ? orderRecord.order_id : null;
      const symbolKey =
        resolvedPath[0] === "provenance"
        && resolvedPath[1] === "market_data_by_symbol"
        && resolvedPath[3] === "issues"
          ? (resolvedParameterValues.symbol_key?.trim() || resolvedPath[2] || "")
          : "";
      const runContext =
        resolvedPath[0] === "orders" && orderId
          ? {
              componentKey: "trade_count",
              label: `Order ${orderId}`,
              section: "metrics" as const,
              subFocusKey: buildComparisonRunListOrderPreviewSubFocusKey(orderId, "instrument"),
            }
          : symbolKey
            ? {
                componentKey: "provenance_richness",
                label: `Data lineage ${symbolKey}`,
                section: "context" as const,
                subFocusKey: buildComparisonRunListDataSymbolSubFocusKey(symbolKey, "issues"),
              }
            : null;
      allValues.push({
        candidatePath,
        candidateReplayId,
        candidateValue,
        detail: candidateValueRaw === RUN_SURFACE_COLLECTION_RUNTIME_MISSING
          ? `${candidatePath} has no ${accessorLabel} value in the current run payload.`
          : `${candidatePath} resolved ${accessorLabel} to ${candidateValue} and ${
            result ? "matched" : "did not match"
          } ${comparedValueLabel}.`,
        result,
        runId: run.config.run_id,
        runContextArtifactHoverKeys,
        runContextComponentKey: runContext?.componentKey ?? null,
        runContextLabel: runContext?.label ?? null,
        runContextSection: runContext?.section ?? null,
        runContextSubFocusKey: runContext?.subFocusKey ?? null,
      });
    });
    const quantifierResult = evaluateRunSurfaceCollectionQueryRuntimeQuantifierOutcome(
      quantifier,
      runCandidateCount,
      runMatchedCount,
    );
    runOutcomes.push({
      candidateCount: runCandidateCount,
      detail: runCandidateCount
        ? `${quantifier.toUpperCase()} resolved to ${quantifierResult ? "true" : "false"} from ${runMatchedCount}/${runCandidateCount} matching candidates in run ${run.config.run_id}.`
        : `${quantifier.toUpperCase()} resolved to ${quantifierResult ? "true" : "false"} because run ${run.config.run_id} had no concrete candidates on ${resolvedPath.join(".") || schema.label}.`,
      matchedCount: runMatchedCount,
      result: quantifierResult,
      runId: run.config.run_id,
    });
  });
  return {
    allValues,
    runOutcomes,
    sampleValues: allValues.slice(0, RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT),
    sampleMatchCount,
    sampleTotalCount,
    sampleTruncated: allValues.length > RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT,
  };
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(
  sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
) {
  return `${sample.runId}:${sample.candidatePath}`;
}

export function normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().replace(/\s+/g, " ");
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSymbolVariants(symbolKey: string) {
  const trimmed = symbolKey.trim();
  if (!trimmed) {
    return [];
  }
  const bareSymbol = trimmed.includes(":")
    ? trimmed.split(":").slice(1).join(":")
    : trimmed;
  const rawVariants = new Set<string>([
    trimmed,
    trimmed.replace(":", " "),
    bareSymbol,
    bareSymbol.replace("/", "-"),
    bareSymbol.replace("/", " "),
    bareSymbol.replace("/", ""),
  ]);
  return Array.from(rawVariants)
    .map((value) => normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(value))
    .filter(Boolean);
}

export function collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(value: unknown): string[] {
  const collected = new Set<string>();
  const isMetadataKey = (key: string) => key.startsWith("__");
  const visit = (candidate: unknown) => {
    if (candidate === null || candidate === undefined || candidate === "") {
      return;
    }
    if (typeof candidate === "string" || typeof candidate === "number" || typeof candidate === "boolean") {
      const normalized = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(String(candidate));
      if (normalized) {
        collected.add(normalized);
      }
      return;
    }
    if (Array.isArray(candidate)) {
      candidate.forEach((item) => visit(item));
      return;
    }
    if (typeof candidate === "object") {
      Object.entries(candidate as Record<string, unknown>).forEach(([key, nestedValue]) => {
        if (isMetadataKey(key)) {
          return;
        }
        const formattedKey = formatBenchmarkArtifactSummaryLabel(key);
        const normalizedKey = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(formattedKey);
        if (normalizedKey) {
          collected.add(normalizedKey);
        }
        if (
          typeof nestedValue === "string"
          || typeof nestedValue === "number"
          || typeof nestedValue === "boolean"
        ) {
          const joined = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
            `${formattedKey} ${nestedValue}`,
          );
          if (joined) {
            collected.add(joined);
          }
        }
        visit(nestedValue);
      });
    }
  };
  visit(value);
  return Array.from(collected);
}
