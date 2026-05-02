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
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export function buildPredicateRefReplayApplyConflictReview(
  conflict: PredicateRefReplayApplyConflictEntry,
  localTabLabel: string,
  parameterGroupKeyByParameterKey: Record<string, string> = {},
): PredicateRefReplayApplyConflictReview {
  const summaryDiffs: PredicateRefReplayApplyConflictDiffItem[] = [];
  const pushSummaryDiff = (
    key: string,
    label: string,
    localValue: string,
    remoteValue: string,
    editable = false,
  ) => {
    if (localValue === remoteValue) {
      return;
    }
    summaryDiffs.push({
      decisionKey: `summary:${key}`,
      editable,
      key,
      label,
      localValue,
      remoteValue,
      section: "summary",
    });
  };
  pushSummaryDiff(
    "applied_at",
    "Applied at",
    formatRelativeTimestampLabel(conflict.localEntry.appliedAt),
    formatRelativeTimestampLabel(conflict.remoteEntry.appliedAt),
    true,
  );
  pushSummaryDiff(
    "approved_count",
    "Approved rows",
    String(conflict.localEntry.approvedCount),
    String(conflict.remoteEntry.approvedCount),
  );
  pushSummaryDiff(
    "changed_current_count",
    "Changed current",
    String(conflict.localEntry.changedCurrentCount),
    String(conflict.remoteEntry.changedCurrentCount),
  );
  pushSummaryDiff(
    "matches_simulation_count",
    "Matched simulated",
    String(conflict.localEntry.matchesSimulationCount),
    String(conflict.remoteEntry.matchesSimulationCount),
  );
  pushSummaryDiff(
    "source_tab",
    "Applied by",
    conflict.localEntry.sourceTabLabel ?? localTabLabel,
    conflict.remoteEntry.sourceTabLabel ?? conflict.sourceTabLabel,
    true,
  );
  pushSummaryDiff(
    "last_restored_at",
    "Last restored",
    formatRelativeTimestampLabel(conflict.localEntry.lastRestoredAt),
    formatRelativeTimestampLabel(conflict.remoteEntry.lastRestoredAt),
    true,
  );
  pushSummaryDiff(
    "last_restored_by",
    "Restored by",
    conflict.localEntry.lastRestoredByTabLabel ?? "Not restored",
    conflict.remoteEntry.lastRestoredByTabLabel ?? "Not restored",
    true,
  );

  const rowDiffs = Array.from(
    new Set([
      ...conflict.localEntry.rows.map((row) => row.groupKey),
      ...conflict.remoteEntry.rows.map((row) => row.groupKey),
    ]),
  )
    .sort((left, right) => left.localeCompare(right))
    .flatMap((groupKey) => {
      const localRow = conflict.localEntry.rows.find((row) => row.groupKey === groupKey) ?? null;
      const remoteRow = conflict.remoteEntry.rows.find((row) => row.groupKey === groupKey) ?? null;
      if (serializeComparablePredicateRefReplayApplyHistoryRow(localRow) === serializeComparablePredicateRefReplayApplyHistoryRow(remoteRow)) {
        return [];
      }
      return [{
        decisionKey: `row:${groupKey}`,
        editable: true,
        key: groupKey,
        label: localRow?.groupLabel ?? remoteRow?.groupLabel ?? groupKey,
        localValue: formatPredicateRefReplayApplyHistoryRowSummary(localRow),
        remoteValue: formatPredicateRefReplayApplyHistoryRowSummary(remoteRow),
        relatedGroupKey: groupKey,
        section: "row",
      } satisfies PredicateRefReplayApplyConflictDiffItem];
    });

  const selectionSnapshotDiffs = Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
    ]),
  )
    .sort((left, right) => left.localeCompare(right))
    .flatMap((selectionKey) => {
      const localValue = conflict.localEntry.rollbackSnapshot.groupSelectionsBySelectionKey[selectionKey] ?? null;
      const remoteValue = conflict.remoteEntry.rollbackSnapshot.groupSelectionsBySelectionKey[selectionKey] ?? null;
      if (localValue === remoteValue) {
        return [];
      }
      const relatedGroupKey = selectionKey.split(":").filter(Boolean).pop() ?? null;
      return [{
        decisionKey: `selection_snapshot:${selectionKey}`,
        editable: true,
        key: selectionKey,
        label: formatPredicateRefReplayApplyHistorySelectionKeyLabel(selectionKey),
        localValue: formatPredicateRefReplayApplyHistorySnapshotValue(localValue),
        remoteValue: formatPredicateRefReplayApplyHistorySnapshotValue(remoteValue),
        relatedGroupKey,
        section: "selection_snapshot",
      } satisfies PredicateRefReplayApplyConflictDiffItem];
    });

  const bindingSnapshotDiffs = Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.draftBindingsByParameterKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.draftBindingsByParameterKey),
    ]),
  )
    .sort((left, right) => left.localeCompare(right))
    .flatMap((parameterKey) => {
      const localValue = conflict.localEntry.rollbackSnapshot.draftBindingsByParameterKey[parameterKey] ?? null;
      const remoteValue = conflict.remoteEntry.rollbackSnapshot.draftBindingsByParameterKey[parameterKey] ?? null;
      if (localValue === remoteValue) {
        return [];
      }
      return [{
        decisionKey: `binding_snapshot:${parameterKey}`,
        editable: true,
        key: parameterKey,
        label: parameterKey,
        localValue: formatPredicateRefReplayApplyHistorySnapshotValue(localValue),
        remoteValue: formatPredicateRefReplayApplyHistorySnapshotValue(remoteValue),
        relatedGroupKey: parameterGroupKeyByParameterKey[parameterKey] ?? null,
        section: "binding_snapshot",
      } satisfies PredicateRefReplayApplyConflictDiffItem];
    });

  const totalDiffCount = summaryDiffs.length
    + rowDiffs.length
    + selectionSnapshotDiffs.length
    + bindingSnapshotDiffs.length;
  return {
    conflict,
    summaryDiffs,
    rowDiffs,
    selectionSnapshotDiffs,
    bindingSnapshotDiffs,
    totalDiffCount,
    localPreview: buildPredicateRefReplayApplyConflictResolutionPreview(
      conflict,
      conflict.localEntry,
      "local",
      `Keeps the currently active entry in this tab and ignores ${totalDiffCount} remote field-level differences.`,
    ),
    remotePreview: buildPredicateRefReplayApplyConflictResolutionPreview(
      conflict,
      conflict.remoteEntry,
      "remote",
      `Replaces the active entry with ${conflict.sourceTabLabel}'s version across ${totalDiffCount} differing fields in this tab.`,
    ),
  };
}

export function normalizePredicateRefReplayApplySyncAuditEntry(value: unknown): PredicateRefReplayApplySyncAuditEntry | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const record = value as Record<string, unknown>;
  if (
    typeof record.auditId !== "string"
    || typeof record.at !== "string"
    || typeof record.detail !== "string"
    || typeof record.entryId !== "string"
    || typeof record.kind !== "string"
    || typeof record.sourceTabId !== "string"
    || typeof record.sourceTabLabel !== "string"
    || typeof record.templateId !== "string"
    || typeof record.templateLabel !== "string"
  ) {
    return null;
  }
  if (
    ![
      "local_apply",
      "local_restore",
      "remote_apply",
      "remote_restore",
      "conflict_detected",
      "conflict_resolved",
    ].includes(record.kind)
  ) {
    return null;
  }
  return {
    at: record.at,
    auditId: record.auditId,
    detail: record.detail,
    entryId: record.entryId,
    kind: record.kind,
    sourceTabId: record.sourceTabId,
    sourceTabLabel: record.sourceTabLabel,
    templateId: record.templateId,
    templateLabel: record.templateLabel,
  } as PredicateRefReplayApplySyncAuditEntry;
}

export function normalizePredicateRefReplayApplyConflictEntry(value: unknown): PredicateRefReplayApplyConflictEntry | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const record = value as Record<string, unknown>;
  if (
    typeof record.conflictId !== "string"
    || typeof record.detectedAt !== "string"
    || typeof record.entryId !== "string"
    || typeof record.sourceTabId !== "string"
    || typeof record.sourceTabLabel !== "string"
    || typeof record.templateId !== "string"
    || typeof record.templateLabel !== "string"
  ) {
    return null;
  }
  const localEntry = normalizePredicateRefReplayApplyHistoryEntry(record.localEntry);
  const remoteEntry = normalizePredicateRefReplayApplyHistoryEntry(record.remoteEntry);
  if (!localEntry || !remoteEntry) {
    return null;
  }
  return {
    conflictId: record.conflictId,
    detectedAt: record.detectedAt,
    entryId: record.entryId,
    localEntry,
    remoteEntry,
    sourceTabId: record.sourceTabId,
    sourceTabLabel: record.sourceTabLabel,
    templateId: record.templateId,
    templateLabel: record.templateLabel,
  };
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail(
  tabId: string,
): PredicateRefReplayApplySyncAuditEntry[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<PredicateRefReplayApplySyncAuditTrailState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION
      || typeof parsed.tabId !== "string"
      || parsed.tabId !== tabId
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return limitPredicateRefReplayApplySyncAuditEntries(
      parsed.entries
        .map((entry) => normalizePredicateRefReplayApplySyncAuditEntry(entry))
        .filter((entry): entry is PredicateRefReplayApplySyncAuditEntry => entry !== null),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail(
  tabId: string,
  entries: PredicateRefReplayApplySyncAuditEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: PredicateRefReplayApplySyncAuditTrailState = {
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION,
      tabId,
      entries: limitPredicateRefReplayApplySyncAuditEntries(entries),
    };
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts(
  tabId: string,
): PredicateRefReplayApplyConflictEntry[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<PredicateRefReplayApplyConflictState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION
      || typeof parsed.tabId !== "string"
      || parsed.tabId !== tabId
      || !Array.isArray(parsed.conflicts)
    ) {
      return [];
    }
    return limitPredicateRefReplayApplyConflictEntries(
      parsed.conflicts
        .map((entry) => normalizePredicateRefReplayApplyConflictEntry(entry))
        .filter((entry): entry is PredicateRefReplayApplyConflictEntry => entry !== null),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts(
  tabId: string,
  conflicts: PredicateRefReplayApplyConflictEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: PredicateRefReplayApplyConflictState = {
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION,
      tabId,
      conflicts: limitPredicateRefReplayApplyConflictEntries(conflicts),
    };
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

export function normalizeReplayApplySnapshotRecord(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value).flatMap(([key, entryValue]) =>
      typeof key === "string" && (typeof entryValue === "string" || entryValue === null)
        ? [[key, entryValue] as const]
        : [],
    ),
  );
}

export function normalizePredicateRefReplayApplyHistoryEntry(value: unknown): PredicateRefReplayApplyHistoryEntry | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const record = value as Record<string, unknown>;
  if (
    typeof record.id !== "string"
    || typeof record.appliedAt !== "string"
    || typeof record.templateId !== "string"
    || typeof record.templateLabel !== "string"
    || typeof record.approvedCount !== "number"
    || typeof record.changedCurrentCount !== "number"
    || typeof record.matchesSimulationCount !== "number"
    || !Array.isArray(record.rows)
  ) {
    return null;
  }
  const rows = record.rows.flatMap((rowValue) => {
    if (!rowValue || typeof rowValue !== "object" || Array.isArray(rowValue)) {
      return [];
    }
    const rowRecord = rowValue as Record<string, unknown>;
    if (
      typeof rowRecord.groupKey !== "string"
      || typeof rowRecord.groupLabel !== "string"
      || typeof rowRecord.currentBundleLabel !== "string"
      || typeof rowRecord.currentStatus !== "string"
      || typeof rowRecord.simulatedBundleLabel !== "string"
      || typeof rowRecord.simulatedStatus !== "string"
      || typeof rowRecord.promotedBundleKey !== "string"
      || typeof rowRecord.promotedBundleLabel !== "string"
      || typeof rowRecord.matchesSimulation !== "boolean"
      || typeof rowRecord.changesCurrent !== "boolean"
    ) {
      return [];
    }
    return [{
      changesCurrent: rowRecord.changesCurrent,
      currentBundleLabel: rowRecord.currentBundleLabel,
      currentStatus: rowRecord.currentStatus,
      groupKey: rowRecord.groupKey,
      groupLabel: rowRecord.groupLabel,
      matchesSimulation: rowRecord.matchesSimulation,
      promotedBundleKey: rowRecord.promotedBundleKey,
      promotedBundleLabel: rowRecord.promotedBundleLabel,
      simulatedBundleLabel: rowRecord.simulatedBundleLabel,
      simulatedStatus: rowRecord.simulatedStatus,
    } satisfies PredicateRefReplayApplyHistoryRow];
  });
  if (!rows.length) {
    return null;
  }
  const rollbackSnapshot =
    record.rollbackSnapshot && typeof record.rollbackSnapshot === "object" && !Array.isArray(record.rollbackSnapshot)
      ? (record.rollbackSnapshot as Record<string, unknown>)
      : {};
  return {
    appliedAt: record.appliedAt,
    approvedCount: record.approvedCount,
    changedCurrentCount: record.changedCurrentCount,
    id: record.id,
    matchesSimulationCount: record.matchesSimulationCount,
    rollbackSnapshot: {
      draftBindingsByParameterKey: normalizeReplayApplySnapshotRecord(rollbackSnapshot.draftBindingsByParameterKey),
      groupSelectionsBySelectionKey: normalizeReplayApplySnapshotRecord(rollbackSnapshot.groupSelectionsBySelectionKey),
    },
    rows,
    sourceTabId:
      typeof record.sourceTabId === "string" || record.sourceTabId === null
        ? record.sourceTabId
        : null,
    sourceTabLabel:
      typeof record.sourceTabLabel === "string" || record.sourceTabLabel === null
        ? record.sourceTabLabel
        : null,
    templateId: record.templateId,
    templateLabel: record.templateLabel,
    lastRestoredAt:
      typeof record.lastRestoredAt === "string" || record.lastRestoredAt === null
        ? record.lastRestoredAt
        : null,
    lastRestoredByTabId:
      typeof record.lastRestoredByTabId === "string" || record.lastRestoredByTabId === null
        ? record.lastRestoredByTabId
        : null,
    lastRestoredByTabLabel:
      typeof record.lastRestoredByTabLabel === "string" || record.lastRestoredByTabLabel === null
        ? record.lastRestoredByTabLabel
        : null,
  };
}

export function parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue(raw: string | null) {
  if (!raw) {
    return [] as PredicateRefReplayApplyHistoryEntry[];
  }
  try {
    const parsed = JSON.parse(raw);
    if (
      !parsed
      || typeof parsed !== "object"
      || Array.isArray(parsed)
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return parsed.entries
      .map((entry: unknown) => normalizePredicateRefReplayApplyHistoryEntry(entry))
      .filter((entry: PredicateRefReplayApplyHistoryEntry | null): entry is PredicateRefReplayApplyHistoryEntry => Boolean(entry))
      .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES);
  } catch {
    return [];
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplyHistory() {
  if (typeof window === "undefined") {
    return [] as PredicateRefReplayApplyHistoryEntry[];
  }
  return parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue(
    window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY),
  );
}

export function serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(
  entries: PredicateRefReplayApplyHistoryEntry[],
) {
  return JSON.stringify({
    version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION,
    entries: entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES),
  });
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplyHistory(
  entries: PredicateRefReplayApplyHistoryEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY,
      serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(entries),
    );
  } catch {
    return;
  }
}

export function mergePredicateRefReplayApplyHistoryEntries(
  currentEntries: PredicateRefReplayApplyHistoryEntry[],
  incomingEntries: PredicateRefReplayApplyHistoryEntry[],
) {
  const entryById = new Map(
    currentEntries.map((entry) => [entry.id, entry] as const),
  );
  incomingEntries.forEach((incomingEntry) => {
    const currentEntry = entryById.get(incomingEntry.id);
    if (!currentEntry) {
      entryById.set(incomingEntry.id, incomingEntry);
      return;
    }
    const currentRestoredAt = currentEntry.lastRestoredAt ? Date.parse(currentEntry.lastRestoredAt) : Number.NEGATIVE_INFINITY;
    const incomingRestoredAt = incomingEntry.lastRestoredAt ? Date.parse(incomingEntry.lastRestoredAt) : Number.NEGATIVE_INFINITY;
    if (incomingRestoredAt > currentRestoredAt) {
      entryById.set(incomingEntry.id, incomingEntry);
      return;
    }
    if (incomingRestoredAt < currentRestoredAt) {
      entryById.set(incomingEntry.id, currentEntry);
      return;
    }
    const currentAppliedAt = Date.parse(currentEntry.appliedAt);
    const incomingAppliedAt = Date.parse(incomingEntry.appliedAt);
    entryById.set(
      incomingEntry.id,
      incomingAppliedAt >= currentAppliedAt ? incomingEntry : currentEntry,
    );
  });
  return Array.from(entryById.values())
    .sort((left, right) => Date.parse(right.appliedAt) - Date.parse(left.appliedAt))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES);
}
