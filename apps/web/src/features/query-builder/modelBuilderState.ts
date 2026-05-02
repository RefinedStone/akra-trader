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
import { loadRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases, pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases, mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts, areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual, readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, persistRunSurfaceCollectionQueryBuilderReplayIntent, buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId, buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId, limitPredicateRefReplayApplySyncAuditEntries, mergePredicateRefReplayApplySyncAuditEntries, limitPredicateRefReplayApplyConflictEntries, serializeComparablePredicateRefReplayApplyHistoryEntry, arePredicateRefReplayApplyHistoryEntriesEquivalent, serializeComparablePredicateRefReplayApplyHistoryRow, formatPredicateRefReplayApplyHistorySnapshotValue, formatPredicateRefReplayApplyHistorySelectionKeyLabel, formatPredicateRefReplayApplyHistoryRowSummary, clonePredicateRefReplayApplyHistoryEntry, buildPredicateRefReplayApplyConflictResolutionPreview, buildPredicateRefReplayApplyConflictMergedEntry } from "./modelReplayStorage";
import { buildPredicateRefReplayApplyConflictReview, normalizePredicateRefReplayApplySyncAuditEntry, normalizePredicateRefReplayApplyConflictEntry, loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts, persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts, normalizeReplayApplySnapshotRecord, normalizePredicateRefReplayApplyHistoryEntry, parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue, loadRunSurfaceCollectionQueryBuilderReplayApplyHistory, serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory, persistRunSurfaceCollectionQueryBuilderReplayApplyHistory, mergePredicateRefReplayApplyHistoryEntries } from "./modelReplayApply";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export function isRunSurfaceCollectionQueryBindingReferenceValue(value: string) {
  return value.startsWith("$") && value.length > 1;
}

export function toRunSurfaceCollectionQueryBindingReferenceValue(bindingKey: string) {
  return bindingKey ? `$${bindingKey}` : "";
}

export function fromRunSurfaceCollectionQueryBindingReferenceValue(value: string) {
  return isRunSurfaceCollectionQueryBindingReferenceValue(value) ? value.slice(1) : "";
}

export function mergeRunSurfaceCollectionQueryBuilderTemplateParameters(
  inferredParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[],
  existingParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[] = [],
) {
  const inferredParameterMap = new Map(
    inferredParameters.map((parameter) => [parameter.key, parameter] as const),
  );
  const existingParameterMap = new Map(
    existingParameters.map((parameter) => [parameter.key, parameter] as const),
  );
  const orderedKeys = [
    ...existingParameters
      .map((parameter) => parameter.key)
      .filter((key) => inferredParameterMap.has(key)),
    ...inferredParameters
      .map((parameter) => parameter.key)
      .filter((key) => !existingParameterMap.has(key)),
  ];
  return orderedKeys.flatMap((key) => {
    const parameter = inferredParameterMap.get(key);
    if (!parameter) {
      return [];
    }
    const existing = existingParameterMap.get(key);
    return [
      existing
        ? {
            ...parameter,
            customLabel: existing.customLabel,
            groupName: existing.groupName,
            helpNote: existing.helpNote,
            defaultValue: existing.defaultValue,
            bindingPreset: existing.bindingPreset,
          }
        : parameter,
    ];
  });
}

export function normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey(groupName: string) {
  const trimmedGroupName = groupName.trim();
  if (!trimmedGroupName) {
    return "__ungrouped__";
  }
  const normalizedKey = trimmedGroupName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalizedKey || "__ungrouped__";
}

export function mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
  parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[],
  existingGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[] = [],
) {
  const existingGroupMap = new Map(existingGroups.map((group) => [group.key, group] as const));
  const derivedGroups = new Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState>();
  parameters.forEach((parameter) => {
    const trimmedGroupName = parameter.groupName.trim();
    const groupKey = normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey(trimmedGroupName);
    if (derivedGroups.has(groupKey)) {
      return;
    }
    const existingGroup = existingGroupMap.get(groupKey);
    derivedGroups.set(groupKey, {
      key: groupKey,
      label: existingGroup?.label || trimmedGroupName || "Ungrouped parameters",
      helpNote: existingGroup?.helpNote ?? "",
      collapsedByDefault: existingGroup?.collapsedByDefault ?? false,
      visibilityRule: existingGroup?.visibilityRule ?? "always",
      coordinationPolicy: existingGroup?.coordinationPolicy ?? "manual_source_priority",
      presetBundles: existingGroup?.presetBundles ?? [],
    });
  });
  return Array.from(derivedGroups.values());
}

export function groupRunSurfaceCollectionQueryBuilderTemplateParameters(
  parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[],
  groupMetadata: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[] = [],
) {
  const mergedGroups = mergeRunSurfaceCollectionQueryBuilderTemplateGroups(parameters, groupMetadata);
  const mergedGroupMap = new Map(mergedGroups.map((group) => [group.key, group] as const));
  const groups = new Map<
    string,
    {
      key: string;
      label: string;
      helpNote: string;
      collapsedByDefault: boolean;
      visibilityRule: "always" | "manual" | "binding_active" | "value_active";
      coordinationPolicy: "manual_source_priority" | "highest_source_priority" | "sticky_auto_selection" | "manual_resolution";
      presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
      parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
    }
  >();
  parameters.forEach((parameter) => {
    const normalizedLabel = parameter.groupName.trim();
    const key = normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey(normalizedLabel);
    const group = mergedGroupMap.get(key);
    const label = group?.label || normalizedLabel || "Ungrouped parameters";
    const existing = groups.get(key);
    if (existing) {
      existing.parameters.push(parameter);
      return;
    }
    groups.set(key, {
      key,
      label,
      helpNote: group?.helpNote ?? "",
      collapsedByDefault: group?.collapsedByDefault ?? false,
      visibilityRule: group?.visibilityRule ?? "always",
      coordinationPolicy: group?.coordinationPolicy ?? "manual_source_priority",
      presetBundles: group?.presetBundles ?? [],
      parameters: [parameter],
    });
  });
  return Array.from(groups.values());
}

export function sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles(
  bundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[],
) {
  return [...bundles].sort((left, right) => {
    if (right.priority !== left.priority) {
      return right.priority - left.priority;
    }
    const labelComparison = left.label.localeCompare(right.label);
    if (labelComparison !== 0) {
      return labelComparison;
    }
    return left.key.localeCompare(right.key);
  });
}

export function formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(
  policy: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"],
) {
  if (policy === "manual_source_priority") {
    return "prefer manual source";
  }
  if (policy === "highest_source_priority") {
    return "highest source priority";
  }
  if (policy === "sticky_auto_selection") {
    return "keep current auto choice";
  }
  return "manual resolution";
}

export function cloneRunSurfaceCollectionQueryBuilderChildState(
  child: RunSurfaceCollectionQueryBuilderChildState,
): RunSurfaceCollectionQueryBuilderChildState {
  if (child.kind === "clause") {
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause: {
        ...child.clause,
        parameterValues: { ...child.clause.parameterValues },
        parameterBindingKeys: { ...child.clause.parameterBindingKeys },
        valueBindingKey: child.clause.valueBindingKey,
      },
    };
  }
  if (child.kind === "predicate_ref") {
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate-ref"),
      kind: "predicate_ref",
      predicateKey: child.predicateKey,
      bindings: { ...child.bindings },
      negated: child.negated,
    };
  }
  return {
    id: buildRunSurfaceCollectionQueryBuilderEntityId("group"),
    kind: "group",
    logic: child.logic,
    negated: child.negated,
    children: child.children.map((nestedChild) => cloneRunSurfaceCollectionQueryBuilderChildState(nestedChild)),
  };
}

export function parseRunSurfaceCollectionQueryBuilderClauseState(
  rawNode: unknown,
  contracts: RunSurfaceCollectionQueryContract[],
): HydratedRunSurfaceCollectionQueryBuilderState | null {
  try {
    if (!rawNode || typeof rawNode !== "object" || Array.isArray(rawNode)) {
      return null;
    }
    const record = rawNode as Record<string, unknown>;
    const collectionRecord =
      record.collection && typeof record.collection === "object" && !Array.isArray(record.collection)
        ? (record.collection as Record<string, unknown>)
        : null;
    const conditionRecords = Array.isArray(record.conditions)
      ? record.conditions.filter(
          (condition): condition is Record<string, unknown> =>
            Boolean(condition) && typeof condition === "object" && !Array.isArray(condition),
        )
      : [];
    const childRecords = Array.isArray(record.children)
      ? record.children.filter((child) => Boolean(child))
      : [];
    if (!collectionRecord || conditionRecords.length !== 1 || childRecords.length) {
      return null;
    }
    const resolvedPath = getCollectionQueryStringArray(collectionRecord.path);
    const rawPathTemplate = getCollectionQueryStringArray(collectionRecord.path_template);
    const rawBindings =
      collectionRecord.bindings && typeof collectionRecord.bindings === "object" && !Array.isArray(collectionRecord.bindings)
        ? (collectionRecord.bindings as Record<string, unknown>)
        : null;
    const quantifier =
      collectionRecord.quantifier === "all"
      || collectionRecord.quantifier === "none"
      || collectionRecord.quantifier === "any"
        ? collectionRecord.quantifier
        : "any";
    const condition = conditionRecords[0];
    const fieldKey = typeof condition.key === "string" ? condition.key : "";
    const operatorKey = typeof condition.operator === "string" ? condition.operator : "";
    if ((!resolvedPath.length && !rawPathTemplate.length) || !fieldKey || !operatorKey) {
      return null;
    }
    for (const contract of contracts) {
      const schemas = getRunSurfaceCollectionQuerySchemas(contract);
      for (const schema of schemas) {
        const parameterValues = rawPathTemplate.length
          ? (
              getCollectionQuerySchemaId(schema) === rawPathTemplate.join(".")
                ? schema.parameters.reduce<Record<string, string>>((accumulator, parameter) => {
                    const rawBindingValue = rawBindings?.[parameter.key];
                    if (rawBindingValue && typeof rawBindingValue === "object" && !Array.isArray(rawBindingValue)) {
                      return accumulator;
                    }
                    if (typeof rawBindingValue === "string") {
                      accumulator[parameter.key] = rawBindingValue;
                      return accumulator;
                    }
                    const optionValues = parameter.domain?.values.length
                      ? parameter.domain.values
                      : parameter.examples;
                    if (optionValues[0]) {
                      accumulator[parameter.key] = optionValues[0];
                    }
                    return accumulator;
                  }, {})
                : null
            )
          : resolveCollectionQueryTemplateValues(schema.pathTemplate, resolvedPath);
        if (!parameterValues) {
          continue;
        }
        const field = schema.elementSchema.find((candidate) => candidate.key === fieldKey);
        if (!field) {
          continue;
        }
        const operator = field.operators.find((candidate) => candidate.key === operatorKey);
        if (!operator) {
          continue;
        }
        const parameterBindingKeys = schema.parameters.reduce<Record<string, string>>((accumulator, parameter) => {
          const rawBindingValue = rawBindings?.[parameter.key];
          if (
            rawBindingValue
            && typeof rawBindingValue === "object"
            && !Array.isArray(rawBindingValue)
            && typeof (rawBindingValue as Record<string, unknown>).binding === "string"
          ) {
            accumulator[parameter.key] = (rawBindingValue as Record<string, string>).binding;
          }
          return accumulator;
        }, {});
        const valueBindingKey =
          condition.value
          && typeof condition.value === "object"
          && !Array.isArray(condition.value)
          && typeof (condition.value as Record<string, unknown>).binding === "string"
            ? (condition.value as Record<string, string>).binding
            : "";
        return {
          contractKey: contract.contract_key,
          schemaId: getCollectionQuerySchemaId(schema),
          parameterValues,
          parameterBindingKeys,
          quantifier,
          fieldKey,
          operatorKey,
          builderValue: valueBindingKey ? "" : formatCollectionQueryBuilderValue(condition.value, field.valueType),
          valueBindingKey,
          negated: record.negated === true,
        };
      }
    }
  } catch {
    return null;
  }
  return null;
}

export function buildRunSurfaceCollectionQueryBuilderDefaultClauseState(
  contracts: RunSurfaceCollectionQueryContract[],
  preferredContractKey?: string | null,
): HydratedRunSurfaceCollectionQueryBuilderState | null {
  const activeContract =
    contracts.find((contract) => contract.contract_key === preferredContractKey) ?? contracts[0] ?? null;
  if (!activeContract) {
    return null;
  }
  const schema = getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  if (!schema) {
    return null;
  }
  const parameterValues = schema.parameters.reduce<Record<string, string>>((accumulator, parameter) => {
    const optionValues = parameter.domain?.values.length ? parameter.domain.values : parameter.examples;
    if (optionValues[0]) {
      accumulator[parameter.key] = optionValues[0];
    }
    return accumulator;
  }, {});
  const field = schema.elementSchema[0] ?? null;
  const operator = field?.operators[0] ?? null;
  if (!field || !operator) {
    return null;
  }
  return {
    contractKey: activeContract.contract_key,
    schemaId: getCollectionQuerySchemaId(schema),
    parameterValues,
    parameterBindingKeys: {},
    quantifier: "any",
    fieldKey: field.key,
    operatorKey: operator.key,
    builderValue: "",
    valueBindingKey: "",
    negated: false,
  };
}

export function buildRunSurfaceCollectionQueryBuilderNodeFromClause(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  const activeContract =
    contracts.find((contract) => contract.contract_key === clause.contractKey) ?? contracts[0] ?? null;
  const activeSchema =
    getRunSurfaceCollectionQuerySchemas(activeContract).find(
      (schema) => getCollectionQuerySchemaId(schema) === clause.schemaId,
    ) ?? getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  if (!activeContract || !activeSchema) {
    return null;
  }
  const field =
    activeSchema.elementSchema.find((candidate) => candidate.key === clause.fieldKey)
    ?? activeSchema.elementSchema[0]
    ?? null;
  const operator =
    field?.operators.find((candidate) => candidate.key === clause.operatorKey)
    ?? field?.operators[0]
    ?? null;
  if (!field || !operator) {
    return null;
  }
  const hasTemplateBindings = Object.values(clause.parameterBindingKeys).some(Boolean);
  const collectionNode = hasTemplateBindings
    ? {
        path_template: activeSchema.pathTemplate,
        bindings: activeSchema.parameters.reduce<Record<string, unknown>>((accumulator, parameter) => {
          const bindingKey = clause.parameterBindingKeys[parameter.key]?.trim();
          if (bindingKey) {
            accumulator[parameter.key] = { binding: bindingKey };
            return accumulator;
          }
          const literalValue = clause.parameterValues[parameter.key];
          if (literalValue) {
            accumulator[parameter.key] = literalValue;
          }
          return accumulator;
        }, {}),
        quantifier: clause.quantifier,
      }
    : {
        path: resolveCollectionQueryPath(activeSchema.pathTemplate, clause.parameterValues),
        quantifier: clause.quantifier,
      };
  return {
    ...(clause.negated ? { negated: true } : {}),
    collection: collectionNode,
    conditions: [
      {
        key: field.key,
        operator: operator.key,
        value: clause.valueBindingKey
          ? { binding: clause.valueBindingKey }
          : coerceCollectionQueryBuilderValue(clause.builderValue, field.valueType),
      },
    ],
  };
}

export function formatRunSurfaceCollectionQueryBuilderClauseSummary(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  const activeContract =
    contracts.find((contract) => contract.contract_key === clause.contractKey) ?? contracts[0] ?? null;
  const activeSchema =
    getRunSurfaceCollectionQuerySchemas(activeContract).find(
      (schema) => getCollectionQuerySchemaId(schema) === clause.schemaId,
    ) ?? getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  const field = activeSchema?.elementSchema.find((candidate) => candidate.key === clause.fieldKey) ?? null;
  const operator = field?.operators.find((candidate) => candidate.key === clause.operatorKey) ?? null;
  const path = activeSchema
    ? (
        Object.values(clause.parameterBindingKeys).some(Boolean)
          ? `${activeSchema.pathTemplate.join(".")} (bound)`
          : resolveCollectionQueryPath(activeSchema.pathTemplate, clause.parameterValues).join(".")
      )
    : clause.schemaId;
  const qualifier = clause.negated ? "not " : "";
  const valueSuffix = clause.valueBindingKey ? ` · value via $${clause.valueBindingKey}` : "";
  return `${qualifier}${clause.quantifier} ${field?.title ?? field?.key ?? clause.fieldKey} ${operator?.label ?? operator?.key ?? clause.operatorKey} @ ${path}${valueSuffix}`;
}

export function areRunSurfaceCollectionQueryBuilderRecordValuesEqual(
  left: Record<string, string>,
  right: Record<string, string>,
) {
  const leftEntries = Object.entries(left).sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey));
  const rightEntries = Object.entries(right).sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey));
  if (leftEntries.length !== rightEntries.length) {
    return false;
  }
  return leftEntries.every(([leftKey, leftValue], index) => {
    const [rightKey, rightValue] = rightEntries[index] ?? [];
    return leftKey === rightKey && leftValue === rightValue;
  });
}

export function areHydratedRunSurfaceCollectionQueryBuilderStatesEqual(
  left: HydratedRunSurfaceCollectionQueryBuilderState | null,
  right: HydratedRunSurfaceCollectionQueryBuilderState | null,
) {
  if (!left || !right) {
    return false;
  }
  return (
    left.contractKey === right.contractKey
    && left.schemaId === right.schemaId
    && left.quantifier === right.quantifier
    && left.fieldKey === right.fieldKey
    && left.operatorKey === right.operatorKey
    && left.builderValue === right.builderValue
    && left.valueBindingKey === right.valueBindingKey
    && left.negated === right.negated
    && areRunSurfaceCollectionQueryBuilderRecordValuesEqual(left.parameterValues, right.parameterValues)
    && areRunSurfaceCollectionQueryBuilderRecordValuesEqual(left.parameterBindingKeys, right.parameterBindingKeys)
  );
}

export function doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext(
  sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
  selection: RunSurfaceCollectionQueryRuntimeCandidateContextSelection | null,
) {
  if (!selection || sample.runId !== selection.runId) {
    return false;
  }
  if (selection.artifactHoverKey) {
    return sample.runContextArtifactHoverKeys.includes(selection.artifactHoverKey);
  }
  if (selection.subFocusKey) {
    return sample.runContextSubFocusKey === selection.subFocusKey;
  }
  if (selection.componentKey) {
    return (
      sample.runContextComponentKey === selection.componentKey
      && sample.runContextSection === selection.section
    );
  }
  return false;
}

export function isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface(
  left: Pick<
    RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
    "componentKey" | "runId" | "section" | "subFocusKey"
  > | null,
  right: Pick<
    RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
    "componentKey" | "runId" | "section" | "subFocusKey"
  > | null,
) {
  if (!left || !right) {
    return false;
  }
  return (
    left.runId === right.runId
    && left.section === right.section
    && left.componentKey === right.componentKey
    && left.subFocusKey === right.subFocusKey
  );
}

export function formatRunSurfaceCollectionQueryBuilderClauseParameterSource(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  parameterKey: string,
) {
  const bindingKey = clause.parameterBindingKeys[parameterKey]?.trim() ?? "";
  if (bindingKey) {
    return `$${bindingKey}`;
  }
  return clause.parameterValues[parameterKey] || "(blank)";
}

export function formatRunSurfaceCollectionQueryBuilderClauseValueSource(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
) {
  return clause.valueBindingKey.trim()
    ? `$${clause.valueBindingKey.trim()}`
    : (clause.builderValue || "(blank)");
}

export function buildRunSurfaceCollectionQueryBuilderClauseDiffItems(
  original: HydratedRunSurfaceCollectionQueryBuilderState | null,
  draft: HydratedRunSurfaceCollectionQueryBuilderState | null,
): RunSurfaceCollectionQueryBuilderClauseDiffItem[] {
  if (!original || !draft) {
    return [];
  }
  const items: RunSurfaceCollectionQueryBuilderClauseDiffItem[] = [];
  if (original.contractKey !== draft.contractKey) {
    items.push({
      detail: `${original.contractKey} -> ${draft.contractKey}`,
      key: "contract",
      label: "Contract",
    });
  }
  if (original.schemaId !== draft.schemaId) {
    items.push({
      detail: `${original.schemaId} -> ${draft.schemaId}`,
      key: "schema",
      label: "Collection",
    });
  }
  if (original.quantifier !== draft.quantifier) {
    items.push({
      detail: `${original.quantifier.toUpperCase()} -> ${draft.quantifier.toUpperCase()}`,
      key: "quantifier",
      label: "Quantifier",
    });
  }
  if (original.fieldKey !== draft.fieldKey) {
    items.push({
      detail: `${original.fieldKey} -> ${draft.fieldKey}`,
      key: "field",
      label: "Field",
    });
  }
  if (original.operatorKey !== draft.operatorKey) {
    items.push({
      detail: `${original.operatorKey} -> ${draft.operatorKey}`,
      key: "operator",
      label: "Operator",
    });
  }
  if (original.negated !== draft.negated) {
    items.push({
      detail: `${original.negated ? "negated" : "plain"} -> ${draft.negated ? "negated" : "plain"}`,
      key: "negated",
      label: "Negation",
    });
  }
  const originalValue = formatRunSurfaceCollectionQueryBuilderClauseValueSource(original);
  const draftValue = formatRunSurfaceCollectionQueryBuilderClauseValueSource(draft);
  if (originalValue !== draftValue) {
    items.push({
      detail: `${originalValue} -> ${draftValue}`,
      key: "value",
      label: "Value",
    });
  }
  const parameterKeys = Array.from(
    new Set([
      ...Object.keys(original.parameterValues),
      ...Object.keys(draft.parameterValues),
      ...Object.keys(original.parameterBindingKeys),
      ...Object.keys(draft.parameterBindingKeys),
    ]),
  ).sort((left, right) => left.localeCompare(right));
  parameterKeys.forEach((parameterKey) => {
    const originalSource = formatRunSurfaceCollectionQueryBuilderClauseParameterSource(original, parameterKey);
    const draftSource = formatRunSurfaceCollectionQueryBuilderClauseParameterSource(draft, parameterKey);
    if (originalSource === draftSource) {
      return;
    }
    items.push({
      detail: `${originalSource} -> ${draftSource}`,
      key: `parameter:${parameterKey}`,
      label: `Path ${parameterKey}`,
    });
  });
  return items;
}

export function formatRunSurfaceCollectionQueryBuilderChildSummary(
  child: RunSurfaceCollectionQueryBuilderChildState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  if (child.kind === "clause") {
    return formatRunSurfaceCollectionQueryBuilderClauseSummary(child.clause, contracts);
  }
  if (child.kind === "predicate_ref") {
    const bindingSummary = Object.keys(child.bindings).length
      ? ` · ${Object.entries(child.bindings)
          .map(([key, value]) => `${key}=${value}`)
          .join(", ")}`
      : "";
    return `${child.negated ? "not " : ""}predicate ${child.predicateKey}${bindingSummary}`;
  }
  const counts = countRunSurfaceCollectionQueryBuilderChildren(child.children);
  return `${child.negated ? "not " : ""}${child.logic.toUpperCase()} subgroup · ${counts.clauses} clause${counts.clauses === 1 ? "" : "s"} · ${counts.predicateRefs} predicate ref${counts.predicateRefs === 1 ? "" : "s"} · ${counts.groups} nested group${counts.groups === 1 ? "" : "s"}`;
}

export function parseRunSurfaceCollectionQueryBuilderChildState(
  rawNode: unknown,
  contracts: RunSurfaceCollectionQueryContract[],
): RunSurfaceCollectionQueryBuilderChildState | null {
  if (!rawNode || typeof rawNode !== "object" || Array.isArray(rawNode)) {
    return null;
  }
  const childRecord = rawNode as Record<string, unknown>;
  if (typeof childRecord.predicate_ref === "string" && childRecord.predicate_ref) {
    const rawBindings =
      childRecord.bindings && typeof childRecord.bindings === "object" && !Array.isArray(childRecord.bindings)
        ? (childRecord.bindings as Record<string, unknown>)
        : null;
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate-ref"),
      kind: "predicate_ref",
      predicateKey: childRecord.predicate_ref,
      bindings: rawBindings
        ? Object.fromEntries(
            Object.entries(rawBindings).flatMap(([key, value]) => {
              if (typeof value === "string") {
                return [[key, value]];
              }
              if (
                value
                && typeof value === "object"
                && !Array.isArray(value)
                && typeof (value as Record<string, unknown>).binding === "string"
              ) {
                return [[key, toRunSurfaceCollectionQueryBindingReferenceValue((value as Record<string, string>).binding)]];
              }
              return [];
            }),
          )
        : {},
      negated: childRecord.negated === true,
    };
  }
  const clause = parseRunSurfaceCollectionQueryBuilderClauseState(childRecord, contracts);
  if (clause) {
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause,
    };
  }
  const rawChildren = Array.isArray(childRecord.children) ? childRecord.children : [];
  const children = rawChildren.reduce<RunSurfaceCollectionQueryBuilderChildState[]>(
    (accumulator, rawChild) => {
      const parsedChild = parseRunSurfaceCollectionQueryBuilderChildState(rawChild, contracts);
      if (parsedChild) {
        accumulator.push(parsedChild);
      }
      return accumulator;
    },
    [],
  );
  if (!children.length) {
    return null;
  }
  return {
    id: buildRunSurfaceCollectionQueryBuilderEntityId("group"),
    kind: "group",
    logic: childRecord.logic === "or" || childRecord.logic === "and" ? childRecord.logic : "and",
    negated: childRecord.negated === true,
    children,
  };
}

export function buildRunSurfaceCollectionQueryBuilderNodeFromChild(
  child: RunSurfaceCollectionQueryBuilderChildState,
  contracts: RunSurfaceCollectionQueryContract[],
  expressionAuthoring: RunSurfaceCollectionQueryExpressionAuthoring,
  predicateTemplates: RunSurfaceCollectionQueryBuilderPredicateTemplateState[],
): Record<string, unknown> | null {
  if (child.kind === "predicate_ref") {
    const node: Record<string, unknown> = child.negated
      ? { [expressionAuthoring.predicateRefs.referenceField]: child.predicateKey, negated: true }
      : { [expressionAuthoring.predicateRefs.referenceField]: child.predicateKey };
    const referencedTemplate = predicateTemplates.find((template) => template.key === child.predicateKey) ?? null;
    if (referencedTemplate && Object.keys(child.bindings).length) {
      node[expressionAuthoring.predicateTemplates.bindingsField] = Object.fromEntries(
        referencedTemplate.parameters.flatMap((parameter) => {
          const value = child.bindings[parameter.key];
          if (!value) {
            return [];
          }
          return [[
            parameter.key,
            isRunSurfaceCollectionQueryBindingReferenceValue(value)
              ? { [expressionAuthoring.predicateTemplates.bindingReferenceField]: fromRunSurfaceCollectionQueryBindingReferenceValue(value) }
              : coerceCollectionQueryBuilderValue(value, parameter.valueType),
          ]];
        }),
      );
    }
    return node;
  }
  if (child.kind === "clause") {
    return buildRunSurfaceCollectionQueryBuilderNodeFromClause(child.clause, contracts);
  }
  const childNodes = child.children.reduce<Record<string, unknown>[]>((accumulator, nestedChild) => {
    const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
      nestedChild,
      contracts,
      expressionAuthoring,
      predicateTemplates,
    );
    if (node) {
      accumulator.push(node);
    }
    return accumulator;
  }, []);
  if (!childNodes.length) {
    return null;
  }
  return {
    ...(child.negated ? { negated: true } : {}),
    logic: child.logic,
    children: childNodes,
  };
}

export function countRunSurfaceCollectionQueryBuilderChildren(children: RunSurfaceCollectionQueryBuilderChildState[]) {
  return children.reduce(
    (accumulator, child) => {
      if (child.kind === "clause") {
        accumulator.clauses += 1;
        return accumulator;
      }
      if (child.kind === "predicate_ref") {
        accumulator.predicateRefs += 1;
        return accumulator;
      }
      accumulator.groups += 1;
      const nestedCounts = countRunSurfaceCollectionQueryBuilderChildren(child.children);
      accumulator.clauses += nestedCounts.clauses;
      accumulator.predicateRefs += nestedCounts.predicateRefs;
      accumulator.groups += nestedCounts.groups;
      return accumulator;
    },
    { clauses: 0, predicateRefs: 0, groups: 0 },
  );
}

export function findRunSurfaceCollectionQueryBuilderGroup(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  groupId: string,
): RunSurfaceCollectionQueryBuilderGroupState | null {
  for (const child of children) {
    if (child.kind !== "group") {
      continue;
    }
    if (child.id === groupId) {
      return child;
    }
    const nested = findRunSurfaceCollectionQueryBuilderGroup(child.children, groupId);
    if (nested) {
      return nested;
    }
  }
  return null;
}

export function addRunSurfaceCollectionQueryBuilderChildToGroup(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  groupId: string,
  childToAdd: RunSurfaceCollectionQueryBuilderChildState,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind !== "group") {
      return child;
    }
    if (child.id === groupId) {
      return {
        ...child,
        children: [...child.children, childToAdd],
      };
    }
    return {
      ...child,
      children: addRunSurfaceCollectionQueryBuilderChildToGroup(child.children, groupId, childToAdd),
    };
  });
}
