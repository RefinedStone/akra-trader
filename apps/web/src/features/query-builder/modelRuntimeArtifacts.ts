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
import { PredicateRefReplayApplyHistoryRow, PredicateRefReplayApplyHistoryEntry, PredicateRefReplayApplyHistoryTabIdentity, PredicateRefReplayApplySyncMode, PredicateRefReplayApplySyncAuditFilter, PredicateRefReplayApplyConflictPolicy, PredicateRefReplayApplyConflictEntry, PredicateRefReplayApplyConflictDiffItem, PredicateRefReplayApplyConflictResolutionPreview, PredicateRefReplayApplyConflictReview, PredicateRefReplayApplyConflictDraftReview, PredicateRefReplayApplySyncAuditEntry, PredicateRefReplayApplySyncAuditTrailState, PredicateRefReplayApplySyncGovernanceState, RunSurfaceCollectionQueryBuilderReplayIntentState, RunSurfaceCollectionQueryBuilderReplayIntentStorageState, RunSurfaceCollectionQueryBuilderReplayIntentBrowserState, RunSurfaceCollectionQueryBuilderReplayLinkShareMode, RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry, RunSurfaceCollectionQueryBuilderReplayLinkAliasState, RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource, RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry, PredicateRefReplayApplyConflictState, HydratedRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderEditorTarget, RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID, buildRunSurfaceCollectionQueryBuilderEntityId, buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId, formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel, loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity, loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState } from "./modelReplayState";
import { normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot, areRunSurfaceCollectionQueryBuilderReplayIntentsEqual, readRunSurfaceCollectionQueryBuilderReplayIntentStorageState, loadRunSurfaceCollectionQueryBuilderReplayIntent, readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState, isDefaultRunSurfaceCollectionQueryBuilderReplayIntent, encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl, buildRunSurfaceCollectionQueryBuilderReplayIntentUrl, applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId, buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId, normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs, buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry, buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret, hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature, buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken, extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot, getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys, formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue, encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload } from "./modelReplayIntent";
import { loadRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAliases, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState, mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases, pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases, mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail, mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys, buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey, limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts, areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual, readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState, persistRunSurfaceCollectionQueryBuilderReplayIntent, buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId, buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId, limitPredicateRefReplayApplySyncAuditEntries, mergePredicateRefReplayApplySyncAuditEntries, limitPredicateRefReplayApplyConflictEntries, serializeComparablePredicateRefReplayApplyHistoryEntry, arePredicateRefReplayApplyHistoryEntriesEquivalent, serializeComparablePredicateRefReplayApplyHistoryRow, formatPredicateRefReplayApplyHistorySnapshotValue, formatPredicateRefReplayApplyHistorySelectionKeyLabel, formatPredicateRefReplayApplyHistoryRowSummary, clonePredicateRefReplayApplyHistoryEntry, buildPredicateRefReplayApplyConflictResolutionPreview, buildPredicateRefReplayApplyConflictMergedEntry } from "./modelReplayStorage";
import { buildPredicateRefReplayApplyConflictReview, normalizePredicateRefReplayApplySyncAuditEntry, normalizePredicateRefReplayApplyConflictEntry, loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail, loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts, persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts, normalizeReplayApplySnapshotRecord, normalizePredicateRefReplayApplyHistoryEntry, parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue, loadRunSurfaceCollectionQueryBuilderReplayApplyHistory, serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory, persistRunSurfaceCollectionQueryBuilderReplayApplyHistory, mergePredicateRefReplayApplyHistoryEntries } from "./modelReplayApply";
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";
import { updateRunSurfaceCollectionQueryBuilderGroup, updateRunSurfaceCollectionQueryBuilderClause, removeRunSurfaceCollectionQueryBuilderChild, replaceRunSurfaceCollectionQueryBuilderPredicateRefs, removeRunSurfaceCollectionQueryBuilderPredicateRefs, collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause, collectRunSurfaceCollectionQueryBuilderTemplateParameters, parseRunSurfaceCollectionQueryBuilderExpressionState, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateSample, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection, RunSurfaceCollectionQueryBuilderClauseDiffItem, RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem, RunSurfaceCollectionQueryRuntimeQuantifierOutcome, RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./modelBuilderTree";

export function collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((entry) => (typeof entry === "string"
      ? normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(entry)
      : ""))
    .filter(Boolean);
}

export function normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(value: string | null | undefined) {
  if (!value) {
    return "";
  }
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  return trimmed.includes(":")
    ? trimmed.split(":").slice(1).join(":").trim()
    : trimmed;
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateReplayId(params: {
  candidateValueRaw: unknown;
  resolvedParameterValues: Record<string, string>;
  resolvedPath: string[];
}) {
  const { candidateValueRaw, resolvedParameterValues, resolvedPath } = params;
  if (
    resolvedPath[0] !== "provenance"
    || resolvedPath[1] !== "market_data_by_symbol"
    || resolvedPath[3] !== "issues"
    || typeof candidateValueRaw !== "string"
  ) {
    return null;
  }
  const canonicalSymbol = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(
    resolvedParameterValues.symbol_key?.trim() || resolvedPath[2] || "",
  );
  const canonicalValue = String(candidateValueRaw).trim();
  const normalizedValue = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
    canonicalValue,
  );
  if (!canonicalSymbol || !normalizedValue) {
    return null;
  }
  return JSON.stringify(["market_data_issue", canonicalSymbol, canonicalValue]);
}

export function collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((entry) => {
      if (!entry || typeof entry !== "object") {
        return null;
      }
      const record = entry as Record<string, unknown>;
      return {
        bindingKind:
          typeof record.binding_kind === "string" ? record.binding_kind : null,
        candidateId:
          typeof record.candidate_id === "string" ? record.candidate_id : null,
        runtimeCandidateId:
          typeof record.runtime_candidate_id === "string" ? record.runtime_candidate_id : null,
        candidatePathTemplate:
          typeof record.candidate_path_template === "string" ? record.candidate_path_template : null,
        candidateValue:
          typeof record.candidate_value === "string" ? record.candidate_value : null,
        symbolKey:
          typeof record.symbol_key === "string" ? record.symbol_key : null,
      };
    })
    .filter((entry): entry is {
      bindingKind: string | null;
      candidateId: string | null;
      runtimeCandidateId: string | null;
      candidatePathTemplate: string | null;
      candidateValue: string | null;
      symbolKey: string | null;
    } => entry !== null);
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries(
  artifact: BenchmarkArtifact,
) {
  return Object.entries(artifact.summary)
    .map(([summaryKey, rawValue]) => {
      const metadataEntry = artifact.source_locations?.summary?.[summaryKey];
      const labelKey =
        typeof metadataEntry?.label_key === "string" && metadataEntry.label_key.trim()
          ? metadataEntry.label_key
          : summaryKey;
      const candidateBindings =
        collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings(
          metadataEntry?.candidate_bindings,
        );
      const visibleText = formatBenchmarkArtifactSummaryValue(summaryKey, rawValue);
      if (!visibleText) {
        return null;
      }
      const searchableTexts = [
        ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts(
          metadataEntry?.searchable_texts,
        ),
        normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(visibleText),
        normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
          formatBenchmarkArtifactSummaryLabel(labelKey),
        ),
        ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(rawValue),
      ].filter(Boolean);
      return {
        candidateBindings,
        hoverKey: buildComparisonProvenanceArtifactSummaryHoverKey(artifact.path, summaryKey),
        kind: "summary" as const,
        labelKey,
        searchableTexts: Array.from(new Set(searchableTexts)),
        visibleText,
      };
    })
    .filter((entry): entry is {
      candidateBindings: Array<{
        bindingKind: string | null;
        candidateId: string | null;
        runtimeCandidateId: string | null;
        candidatePathTemplate: string | null;
        candidateValue: string | null;
        symbolKey: string | null;
      }>;
      hoverKey: string;
      kind: "summary";
      labelKey: string;
      searchableTexts: string[];
      visibleText: string;
    } => entry !== null);
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries(
  artifact: BenchmarkArtifact,
) {
  return Object.entries(artifact.sections ?? {})
    .flatMap(([sectionKey, sectionValue]) => {
      if (!sectionValue || typeof sectionValue !== "object" || Array.isArray(sectionValue)) {
        return [];
      }
      const metadataEntries = artifact.source_locations?.sections?.[sectionKey];
      if (Array.isArray(metadataEntries) && metadataEntries.length) {
        const structuredEntries = metadataEntries
          .map((metadataEntry, fallbackLineIndex) => {
            const lineKey =
              typeof metadataEntry?.line_key === "string" && metadataEntry.line_key.trim()
                ? metadataEntry.line_key
                : "";
            if (!lineKey) {
              return null;
            }
            const rawValue = (sectionValue as Record<string, unknown>)[lineKey];
            const inlineValue = formatBenchmarkArtifactSectionValue(rawValue);
            if (inlineValue === null) {
              return null;
            }
            const lineIndex =
              typeof metadataEntry?.line_index === "number"
                ? metadataEntry.line_index
                : fallbackLineIndex;
            const candidateBindings =
              collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings(
                metadataEntry?.candidate_bindings,
              );
            const visibleText = `${formatBenchmarkArtifactSummaryLabel(lineKey)}: ${inlineValue}`;
            const searchableTexts = [
              ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts(
                metadataEntry?.searchable_texts,
              ),
              normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(visibleText),
              normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
                formatBenchmarkArtifactSectionLabel(sectionKey),
              ),
              normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
                formatBenchmarkArtifactSummaryLabel(lineKey),
              ),
              ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(rawValue),
            ].filter(Boolean);
            return {
              candidateBindings,
              hoverKey: buildComparisonProvenanceArtifactSectionLineHoverKey(
                artifact.path,
                sectionKey,
                lineIndex,
              ),
              kind: "section_line" as const,
              labelKey: lineKey,
              searchableTexts: Array.from(new Set(searchableTexts)),
              sectionKey,
              visibleText,
            };
          })
          .filter((entry): entry is {
            candidateBindings: Array<{
              bindingKind: string | null;
              candidateId: string | null;
              runtimeCandidateId: string | null;
              candidatePathTemplate: string | null;
              candidateValue: string | null;
              symbolKey: string | null;
            }>;
            hoverKey: string;
            kind: "section_line";
            labelKey: string;
            searchableTexts: string[];
            sectionKey: string;
            visibleText: string;
          } => entry !== null);
        if (structuredEntries.length) {
          return structuredEntries;
        }
      }
      const sectionEntries = Object.entries(sectionValue)
        .map(([lineKey, rawValue]) => {
          const inlineValue = formatBenchmarkArtifactSectionValue(rawValue);
          if (inlineValue === null) {
            return null;
          }
          const visibleText = `${formatBenchmarkArtifactSummaryLabel(lineKey)}: ${inlineValue}`;
          const searchableTexts = [
            normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(visibleText),
            normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
              formatBenchmarkArtifactSectionLabel(sectionKey),
            ),
            normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
              formatBenchmarkArtifactSummaryLabel(lineKey),
            ),
            ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(rawValue),
          ].filter(Boolean);
          return {
            candidateBindings: [] as Array<{
              bindingKind: string | null;
              candidateId: string | null;
              runtimeCandidateId: string | null;
              candidatePathTemplate: string | null;
              candidateValue: string | null;
              symbolKey: string | null;
            }>,
            kind: "section_line" as const,
            labelKey: lineKey,
            searchableTexts,
            sectionKey,
            visibleText,
          };
        })
        .filter((entry): entry is {
          candidateBindings: Array<{
            bindingKind: string | null;
            candidateId: string | null;
            runtimeCandidateId: string | null;
            candidatePathTemplate: string | null;
            candidateValue: string | null;
            symbolKey: string | null;
          }>;
          kind: "section_line";
          labelKey: string;
          searchableTexts: string[];
          sectionKey: string;
          visibleText: string;
        } => entry !== null);
      return sectionEntries.map((entry, lineIndex) => ({
        ...entry,
        hoverKey: buildComparisonProvenanceArtifactSectionLineHoverKey(
          artifact.path,
          sectionKey,
          lineIndex,
        ),
      }));
    });
}

export function scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch(params: {
  candidateValue: string;
  entry: {
    candidateBindings?: Array<{
      bindingKind: string | null;
      candidateId: string | null;
      runtimeCandidateId: string | null;
      candidatePathTemplate: string | null;
      candidateValue: string | null;
      symbolKey: string | null;
    }>;
    kind: "section_line" | "summary";
    labelKey: string;
    searchableTexts: string[];
    sectionKey?: string;
    visibleText: string;
  };
  symbolVariants: string[];
}) {
  const { candidateValue, entry, symbolVariants } = params;
  const normalizedCandidateValue =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(candidateValue);
  if (!normalizedCandidateValue) {
    return null;
  }
  const normalizedVisibleText =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(entry.visibleText);
  const issueMatchesVisibleText = normalizedVisibleText.includes(normalizedCandidateValue);
  const issueMatchesSearchableText = entry.searchableTexts.some((text) =>
    text.includes(normalizedCandidateValue)
  );
  if (!issueMatchesVisibleText && !issueMatchesSearchableText) {
    return null;
  }
  const symbolMatchesVisibleText =
    !symbolVariants.length
    || symbolVariants.some((variant) => normalizedVisibleText.includes(variant));
  const symbolMatchesSearchableText =
    !symbolVariants.length
    || entry.searchableTexts.some((text) =>
      symbolVariants.some((variant) => text.includes(variant))
    );
  if (!symbolMatchesVisibleText && !symbolMatchesSearchableText) {
    return null;
  }
  let score = 0;
  score += issueMatchesVisibleText ? 6 : 3;
  score += symbolMatchesVisibleText ? 4 : 2;
  if (entry.kind === "section_line") {
    score += 3;
  }
  const normalizedSectionKey = entry.sectionKey
    ? normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(entry.sectionKey)
    : "";
  const normalizedLabelKey = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
    entry.labelKey,
  );
  if (/issue|context|signal|market|pair/.test(normalizedSectionKey)) {
    score += 2;
  }
  if (/issue|pair|symbol|headline|context|label/.test(normalizedLabelKey)) {
    score += 1;
  }
  return score;
}

export function doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch(params: {
    binding: {
      bindingKind: string | null;
      candidateId: string | null;
      runtimeCandidateId: string | null;
      candidatePathTemplate: string | null;
      candidateValue: string | null;
      symbolKey: string | null;
    };
  candidateReplayId: string | null;
  candidateValue: string;
  resolvedPath: string[];
  symbolKey: string;
}) {
  const { binding, candidateReplayId, candidateValue, resolvedPath, symbolKey } = params;
  if (binding.bindingKind !== "market_data_issue") {
    return false;
  }
  if (binding.runtimeCandidateId && candidateReplayId) {
    return binding.runtimeCandidateId === candidateReplayId;
  }
  if (binding.candidateId && candidateReplayId) {
    return binding.candidateId === candidateReplayId;
  }
  if (binding.candidatePathTemplate !== "provenance.market_data_by_symbol.{symbol_key}.issues") {
    return false;
  }
  if (
    resolvedPath[0] !== "provenance"
    || resolvedPath[1] !== "market_data_by_symbol"
    || resolvedPath[3] !== "issues"
  ) {
    return false;
  }
  const normalizedBindingSymbol =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(binding.symbolKey);
  const normalizedCandidateSymbol =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(symbolKey || resolvedPath[2] || "");
  if (!normalizedBindingSymbol || !normalizedCandidateSymbol || normalizedBindingSymbol !== normalizedCandidateSymbol) {
    return false;
  }
  if (!binding.candidateValue) {
    return true;
  }
  return (
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(binding.candidateValue)
    === normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(candidateValue)
  );
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys(params: {
  candidateValueRaw: unknown;
  resolvedParameterValues: Record<string, string>;
  resolvedPath: string[];
  run: Run;
}) {
  const { candidateValueRaw, resolvedParameterValues, resolvedPath, run } = params;
  if (
    resolvedPath[0] !== "provenance"
    || resolvedPath[1] !== "market_data_by_symbol"
    || resolvedPath[3] !== "issues"
    || typeof candidateValueRaw !== "string"
  ) {
    return [];
  }
  const candidateValue = candidateValueRaw.trim();
  if (!candidateValue) {
    return [];
  }
  const candidateReplayId = buildRunSurfaceCollectionQueryRuntimeCandidateReplayId({
    candidateValueRaw,
    resolvedParameterValues,
    resolvedPath,
  });
  const symbolKey = resolvedParameterValues.symbol_key?.trim() || resolvedPath[2] || "";
  const symbolVariants =
    buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSymbolVariants(symbolKey);
  const scoredMatches = run.provenance.benchmark_artifacts.flatMap((artifact) => {
    const artifactEntries = [
      ...buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries(artifact),
      ...buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries(artifact),
    ];
    const directValueMatches = artifactEntries.flatMap((entry) => {
      const hasExactBinding = (entry.candidateBindings ?? []).some((binding) =>
        doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch({
          binding,
          candidateReplayId,
          candidateValue,
          resolvedPath,
          symbolKey,
        }) && binding.candidateValue !== null
      );
      return hasExactBinding ? [entry.hoverKey] : [];
    });
    if (directValueMatches.length) {
      return Array.from(new Set(directValueMatches)).map((hoverKey) => ({
        hoverKey,
        score: Number.MAX_SAFE_INTEGER,
      }));
    }
    const directScopedEntries = artifactEntries.filter((entry) =>
      (entry.candidateBindings ?? []).some((binding) =>
        doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch({
          binding,
          candidateReplayId,
          candidateValue,
          resolvedPath,
          symbolKey,
        })
      )
    );
    if (directScopedEntries.length) {
      return directScopedEntries.flatMap((entry) => {
        const score = scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch({
          candidateValue,
          entry,
          symbolVariants,
        });
        return score === null ? [{ hoverKey: entry.hoverKey, score: 1000 }] : [{ hoverKey: entry.hoverKey, score: 1000 + score }];
      });
    }
    return artifactEntries.flatMap((entry) => {
      const score = scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch({
        candidateValue,
        entry,
        symbolVariants,
      });
      return score === null ? [] : [{ hoverKey: entry.hoverKey, score }];
    });
  });
  if (!scoredMatches.length) {
    return [];
  }
  const bestScore = scoredMatches.reduce((maximum, entry) => Math.max(maximum, entry.score), 0);
  return Array.from(
    new Set(
      scoredMatches
        .filter((entry) => entry.score === bestScore)
        .map((entry) => entry.hoverKey),
    ),
  );
}

export function buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems(
  original: RunSurfaceCollectionQueryRuntimeCandidateTrace,
  preview: RunSurfaceCollectionQueryRuntimeCandidateTrace,
) {
  const originalByKey = new Map(
    original.allValues.map((sample) => [buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample), sample] as const),
  );
  const previewByKey = new Map(
    preview.allValues.map((sample) => [buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample), sample] as const),
  );
  const allKeys = Array.from(new Set([
    ...originalByKey.keys(),
    ...previewByKey.keys(),
  ])).sort((left, right) => left.localeCompare(right));
  return allKeys.reduce<RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem[]>((accumulator, key) => {
    const originalSample = originalByKey.get(key) ?? null;
    const previewSample = previewByKey.get(key) ?? null;
    if (
      originalSample
      && previewSample
      && originalSample.result === previewSample.result
      && originalSample.candidateValue === previewSample.candidateValue
    ) {
      return accumulator;
    }
    const runId = previewSample?.runId ?? originalSample?.runId ?? "run";
    const pathLabel = previewSample?.candidatePath ?? originalSample?.candidatePath ?? key;
    accumulator.push({
      detail:
        `${originalSample
          ? `${originalSample.candidateValue} (${originalSample.result ? "matched" : "not matched"})`
          : "missing"} -> ${previewSample
          ? `${previewSample.candidateValue} (${previewSample.result ? "matched" : "not matched"})`
          : "missing"}`,
      key,
      runId: `${runId} · ${pathLabel}`,
    });
    return accumulator;
  }, []);
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause(params: {
  bindingContextByKey?: Record<string, string> | null;
  clause: HydratedRunSurfaceCollectionQueryBuilderState;
  contracts: RunSurfaceCollectionQueryContract[];
  detailSuffix?: string | null;
  location: string;
  runs: Run[];
}) {
  const {
    bindingContextByKey = null,
    clause,
    contracts,
    detailSuffix = null,
    location,
    runs,
  } = params;
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
  const resolvedParameterValues = Object.fromEntries(
    activeSchema.parameters.map((parameter) => {
      const bindingKey = clause.parameterBindingKeys[parameter.key]?.trim() ?? "";
      return [
        parameter.key,
        bindingKey
          ? (bindingContextByKey?.[bindingKey] ?? clause.parameterValues[parameter.key] ?? "")
          : (clause.parameterValues[parameter.key] ?? ""),
      ] as const;
    }),
  );
  const resolvedCandidatePath = resolveCollectionQueryPath(activeSchema.pathTemplate, resolvedParameterValues);
  const candidatePath = resolvedCandidatePath.length
    ? `${resolvedCandidatePath.join(".")}[*]`
    : `${clause.schemaId || "collection"}[*]`;
  const candidateAccessor = field.valueRoot
    ? `${activeSchema.itemKind} value`
    : `${activeSchema.itemKind}.${field.valuePath.join(".") || field.key}`;
  const comparedValueOperand = coerceCollectionQueryBuilderValue(
    clause.valueBindingKey
      ? (bindingContextByKey?.[clause.valueBindingKey] ?? clause.builderValue)
      : clause.builderValue,
    field.valueType,
  );
  const comparedValue = clause.valueBindingKey
    ? (
        formatCollectionQueryBuilderValue(comparedValueOperand, field.valueType)
        || `$${clause.valueBindingKey}`
      )
    : (clause.builderValue || "(blank)");
  const concreteRuntimeSamples = buildRunSurfaceCollectionQueryRuntimeCandidateSamples({
    comparedValueLabel: comparedValue,
    comparedValueOperand,
    field,
    operatorKey: clause.operatorKey,
    quantifier: clause.quantifier,
    resolvedParameterValues,
    runs,
    schema: activeSchema,
  });
  return {
    allValues: concreteRuntimeSamples.allValues,
    bindingContextByKey,
    candidateAccessor,
    candidatePath,
    comparedValue,
    detail:
      `${clause.quantifier.toUpperCase()} evaluates ${candidateAccessor} from ${candidatePath} `
      + `${operator.label ?? clause.operatorKey} ${comparedValue}. `
      + (
        concreteRuntimeSamples.sampleTotalCount
          ? `Concrete payload replay: ${concreteRuntimeSamples.sampleMatchCount}/${concreteRuntimeSamples.sampleTotalCount} candidate values matched across ${runs.length} run payloads. `
          : runs.length
            ? "Concrete payload replay found no candidate values across the current run payloads. "
            : "No run payloads are attached to replay concrete candidate values. "
      )
      + (detailSuffix ?? ""),
    editorClause: clause,
    location,
    quantifier: clause.quantifier,
    result: concreteRuntimeSamples.sampleMatchCount > 0,
    runOutcomes: concreteRuntimeSamples.runOutcomes,
    sampleMatchCount: concreteRuntimeSamples.sampleMatchCount,
    sampleTotalCount: concreteRuntimeSamples.sampleTotalCount,
    sampleTruncated: concreteRuntimeSamples.sampleTruncated,
    sampleValues: concreteRuntimeSamples.sampleValues,
  } satisfies RunSurfaceCollectionQueryRuntimeCandidateTrace;
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection(params: {
  candidateTrace: RunSurfaceCollectionQueryRuntimeCandidateTrace;
  contracts: RunSurfaceCollectionQueryContract[];
  drillthroughKey: string;
  editorClauseState: HydratedRunSurfaceCollectionQueryBuilderState | null;
  pinnedRuntimeCandidateClauseDiffItems: RunSurfaceCollectionQueryBuilderClauseDiffItem[];
  pinnedRuntimeCandidateClauseOriginKey: string | null;
  runtimeRuns: Run[];
}) {
  const {
    candidateTrace,
    contracts,
    drillthroughKey,
    editorClauseState,
    pinnedRuntimeCandidateClauseDiffItems,
    pinnedRuntimeCandidateClauseOriginKey,
    runtimeRuns,
  } = params;
  const tracePinnedFromClauseDraft = pinnedRuntimeCandidateClauseOriginKey === drillthroughKey;
  const traceClauseDiffItems =
    tracePinnedFromClauseDraft
      ? pinnedRuntimeCandidateClauseDiffItems
      : [];
  const traceReevaluationPreview =
    tracePinnedFromClauseDraft
    && traceClauseDiffItems.length
    && candidateTrace.editorClause
    && editorClauseState
      ? buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause({
          bindingContextByKey: candidateTrace.bindingContextByKey,
          clause: editorClauseState,
          contracts,
          detailSuffix: "Draft preview replays the current clause editor state against the same runtime binding context.",
          location: `${candidateTrace.location}:draft_preview`,
          runs: runtimeRuns,
        })
      : null;
  const traceReevaluationPreviewDiffItems =
    traceReevaluationPreview
      ? buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems(
          candidateTrace,
          traceReevaluationPreview,
        )
      : [];
  return {
    tracePinnedFromClauseDraft,
    traceClauseDiffItems,
    traceReevaluationPreview,
    traceReevaluationPreviewDiffItems,
  };
}
