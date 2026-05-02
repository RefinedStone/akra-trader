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
import { isRunSurfaceCollectionQueryBindingReferenceValue, toRunSurfaceCollectionQueryBindingReferenceValue, fromRunSurfaceCollectionQueryBindingReferenceValue, mergeRunSurfaceCollectionQueryBuilderTemplateParameters, normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey, mergeRunSurfaceCollectionQueryBuilderTemplateGroups, groupRunSurfaceCollectionQueryBuilderTemplateParameters, sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles, formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel, cloneRunSurfaceCollectionQueryBuilderChildState, parseRunSurfaceCollectionQueryBuilderClauseState, buildRunSurfaceCollectionQueryBuilderDefaultClauseState, buildRunSurfaceCollectionQueryBuilderNodeFromClause, formatRunSurfaceCollectionQueryBuilderClauseSummary, areRunSurfaceCollectionQueryBuilderRecordValuesEqual, areHydratedRunSurfaceCollectionQueryBuilderStatesEqual, doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext, isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface, formatRunSurfaceCollectionQueryBuilderClauseParameterSource, formatRunSurfaceCollectionQueryBuilderClauseValueSource, buildRunSurfaceCollectionQueryBuilderClauseDiffItems, formatRunSurfaceCollectionQueryBuilderChildSummary, parseRunSurfaceCollectionQueryBuilderChildState, buildRunSurfaceCollectionQueryBuilderNodeFromChild, countRunSurfaceCollectionQueryBuilderChildren, findRunSurfaceCollectionQueryBuilderGroup, addRunSurfaceCollectionQueryBuilderChildToGroup } from "./modelBuilderState";

export function updateRunSurfaceCollectionQueryBuilderGroup(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  groupId: string,
  updater: (group: RunSurfaceCollectionQueryBuilderGroupState) => RunSurfaceCollectionQueryBuilderGroupState,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind !== "group") {
      return child;
    }
    if (child.id === groupId) {
      return updater(child);
    }
    return {
      ...child,
      children: updateRunSurfaceCollectionQueryBuilderGroup(child.children, groupId, updater),
    };
  });
}

export function updateRunSurfaceCollectionQueryBuilderClause(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  childId: string,
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind === "clause" && child.id === childId) {
      return {
        ...child,
        clause,
      };
    }
    if (child.kind === "group") {
      return {
        ...child,
        children: updateRunSurfaceCollectionQueryBuilderClause(child.children, childId, clause),
      };
    }
    return child;
  });
}

export function removeRunSurfaceCollectionQueryBuilderChild(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  childId: string,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.reduce<RunSurfaceCollectionQueryBuilderChildState[]>((accumulator, child) => {
    if (child.id === childId) {
      return accumulator;
    }
    if (child.kind === "group") {
      accumulator.push({
        ...child,
        children: removeRunSurfaceCollectionQueryBuilderChild(child.children, childId),
      });
      return accumulator;
    }
    accumulator.push(child);
    return accumulator;
  }, []);
}

export function replaceRunSurfaceCollectionQueryBuilderPredicateRefs(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  previousKey: string,
  nextKey: string,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind === "predicate_ref") {
      return child.predicateKey === previousKey
        ? {
            ...child,
            predicateKey: nextKey,
          }
        : child;
    }
    if (child.kind === "group") {
      return {
        ...child,
        children: replaceRunSurfaceCollectionQueryBuilderPredicateRefs(child.children, previousKey, nextKey),
      };
    }
    return child;
  });
}

export function removeRunSurfaceCollectionQueryBuilderPredicateRefs(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  predicateKey: string,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.reduce<RunSurfaceCollectionQueryBuilderChildState[]>((accumulator, child) => {
    if (child.kind === "predicate_ref") {
      if (child.predicateKey !== predicateKey) {
        accumulator.push(child);
      }
      return accumulator;
    }
    if (child.kind === "group") {
      accumulator.push({
        ...child,
        children: removeRunSurfaceCollectionQueryBuilderPredicateRefs(child.children, predicateKey),
      });
      return accumulator;
    }
    accumulator.push(child);
    return accumulator;
  }, []);
}

export function collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  const activeContract =
    contracts.find((contract) => contract.contract_key === clause.contractKey) ?? contracts[0] ?? null;
  const activeSchema =
    getRunSurfaceCollectionQuerySchemas(activeContract).find(
      (schema) => getCollectionQuerySchemaId(schema) === clause.schemaId,
    ) ?? getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  const activeField =
    activeSchema?.elementSchema.find((field) => field.key === clause.fieldKey)
    ?? activeSchema?.elementSchema[0]
    ?? null;
  const parameterMap = new Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState>();
  activeSchema?.parameters.forEach((parameter) => {
    const bindingKey = clause.parameterBindingKeys[parameter.key]?.trim();
    if (!bindingKey) {
      return;
    }
    parameterMap.set(bindingKey, {
      key: bindingKey,
      label: `${parameter.key} path binding`,
      customLabel: "",
      groupName: "",
      helpNote: "",
      valueType: "string",
      description: parameter.description || `Collection path binding for ${activeSchema.label}.`,
      options: parameter.domain?.values.length ? parameter.domain.values : parameter.examples,
      defaultValue: "",
      bindingPreset: "",
    });
  });
  if (clause.valueBindingKey.trim()) {
    parameterMap.set(clause.valueBindingKey.trim(), {
      key: clause.valueBindingKey.trim(),
      label: `${activeField?.title ?? activeField?.key ?? clause.fieldKey} value binding`,
      customLabel: "",
      groupName: "",
      helpNote: "",
      valueType: activeField?.valueType ?? "string",
      description: activeField?.description ?? "Bound condition value.",
      options: [],
      defaultValue: "",
      bindingPreset: "",
    });
  }
  return parameterMap;
}

export function collectRunSurfaceCollectionQueryBuilderTemplateParameters(
  child: RunSurfaceCollectionQueryBuilderChildState,
  contracts: RunSurfaceCollectionQueryContract[],
  predicateTemplates: RunSurfaceCollectionQueryBuilderPredicateTemplateState[] = [],
) {
  const parameterMap = new Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState>();
  const collect = (node: RunSurfaceCollectionQueryBuilderChildState) => {
    if (node.kind === "clause") {
      collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause(node.clause, contracts).forEach(
        (parameter, key) => {
          if (!parameterMap.has(key)) {
            parameterMap.set(key, parameter);
          }
        },
      );
      return;
    }
    if (node.kind === "predicate_ref") {
      const referencedTemplate =
        predicateTemplates.find((template) => template.key === node.predicateKey) ?? null;
      Object.entries(node.bindings).forEach(([parameterKey, rawValue]) => {
        const bindingKey = fromRunSurfaceCollectionQueryBindingReferenceValue(rawValue);
        if (!bindingKey || parameterMap.has(bindingKey)) {
          return;
        }
        const referencedParameter =
          referencedTemplate?.parameters.find((parameter) => parameter.key === parameterKey) ?? null;
        parameterMap.set(bindingKey, {
          key: bindingKey,
          label: referencedParameter?.label ?? `${parameterKey} nested binding`,
          customLabel: "",
          groupName: referencedParameter?.groupName ?? "",
          helpNote: referencedParameter?.helpNote ?? "",
          valueType: referencedParameter?.valueType ?? "string",
          description:
            referencedParameter?.description
            ?? `Nested template binding from ${node.predicateKey}.${parameterKey}.`,
          options: referencedParameter?.options ?? [],
          defaultValue: "",
          bindingPreset: "",
        });
      });
      return;
    }
    if (node.kind === "group") {
      node.children.forEach((nestedChild) => collect(nestedChild));
    }
  };
  collect(child);
  return Array.from(parameterMap.values());
}

export function parseRunSurfaceCollectionQueryBuilderExpressionState(
  rawExpression: string | null | undefined,
  contracts: RunSurfaceCollectionQueryContract[],
): HydratedRunSurfaceCollectionQueryBuilderExpressionState | null {
  const trimmedExpression = rawExpression?.trim();
  if (!trimmedExpression) {
    return null;
  }
  try {
    const parsed = JSON.parse(trimmedExpression) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return null;
    }
    const record = parsed as Record<string, unknown>;
    const predicateRegistry =
      typeof record.predicates === "object" && record.predicates !== null && !Array.isArray(record.predicates)
        ? (record.predicates as Record<string, unknown>)
        : {};
    const predicateTemplateRegistry =
      typeof record.predicate_templates === "object" && record.predicate_templates !== null && !Array.isArray(record.predicate_templates)
        ? (record.predicate_templates as Record<string, unknown>)
        : {};
    const rootNode =
      "root" in record
        ? record.root
        : parsed;
    const singleClause = parseRunSurfaceCollectionQueryBuilderClauseState(rootNode, contracts);
    const predicates = Object.entries(predicateRegistry).flatMap(([predicateKey, node]) => {
      const predicateNode = parseRunSurfaceCollectionQueryBuilderChildState(node, contracts);
      if (!predicateNode) {
        return [];
      }
      return [
        {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate"),
          key: predicateKey,
          node: predicateNode,
        } satisfies RunSurfaceCollectionQueryBuilderPredicateState,
      ];
    });
    const predicateTemplates = Object.entries(predicateTemplateRegistry).flatMap(([templateKey, rawTemplate]) => {
      if (!rawTemplate || typeof rawTemplate !== "object" || Array.isArray(rawTemplate)) {
        return [];
      }
      const templateRecord = rawTemplate as Record<string, unknown>;
      const templateNode = parseRunSurfaceCollectionQueryBuilderChildState(templateRecord.template, contracts);
      if (!templateNode) {
        return [];
      }
      const rawParameters = templateRecord.parameters;
      const parameterKeys = Array.isArray(rawParameters)
        ? rawParameters.filter((parameter): parameter is string => typeof parameter === "string" && Boolean(parameter))
        : (
            rawParameters && typeof rawParameters === "object" && !Array.isArray(rawParameters)
              ? Object.keys(rawParameters)
              : []
          );
      const inferredParameters = collectRunSurfaceCollectionQueryBuilderTemplateParameters(templateNode, contracts);
      const inferredParameterMap = new Map(
        inferredParameters.map((parameter) => [parameter.key, parameter] as const),
      );
      const parsedParameters = parameterKeys.map((parameterKey) => {
        const inferredParameter = inferredParameterMap.get(parameterKey);
        const rawParameter =
          rawParameters && typeof rawParameters === "object" && !Array.isArray(rawParameters)
            ? (rawParameters as Record<string, unknown>)[parameterKey]
            : null;
        const rawDefault =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
            ? (rawParameter as Record<string, unknown>).default
            : undefined;
        const rawCustomLabel =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).label === "string"
            ? ((rawParameter as Record<string, string>).label)
            : "";
        const rawBindingPreset =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).binding_preset === "string"
            ? ((rawParameter as Record<string, string>).binding_preset)
            : "";
        const rawGroupName =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).group === "string"
            ? ((rawParameter as Record<string, string>).group)
            : "";
        const rawHelpNote =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).help_note === "string"
            ? ((rawParameter as Record<string, string>).help_note)
            : "";
        const valueType = inferredParameter?.valueType ?? "string";
        return inferredParameter
          ? {
              ...inferredParameter,
              customLabel: rawCustomLabel || inferredParameter.customLabel,
              groupName: rawGroupName || inferredParameter.groupName,
              helpNote: rawHelpNote || inferredParameter.helpNote,
              defaultValue:
                rawDefault === undefined
                  ? inferredParameter.defaultValue
                  : formatCollectionQueryBuilderValue(rawDefault, valueType),
              bindingPreset: rawBindingPreset || inferredParameter.bindingPreset,
            }
          : {
              key: parameterKey,
              label: parameterKey,
              customLabel: rawCustomLabel,
              groupName: rawGroupName,
              helpNote: rawHelpNote,
              valueType,
              description: null,
              options: [],
              defaultValue:
                rawDefault === undefined
                  ? ""
                  : formatCollectionQueryBuilderValue(rawDefault, valueType),
              bindingPreset: rawBindingPreset,
            };
      });
      const rawParameterGroups = templateRecord.parameter_groups;
      const parsedParameterGroups = (
        rawParameterGroups && typeof rawParameterGroups === "object" && !Array.isArray(rawParameterGroups)
          ? Object.entries(rawParameterGroups)
          : []
      ).flatMap(([groupKey, rawGroup]) => {
        if (!rawGroup || typeof rawGroup !== "object" || Array.isArray(rawGroup)) {
          return [];
        }
        const groupRecord = rawGroup as Record<string, unknown>;
        const rawPresetBundles =
          groupRecord.preset_bundles && typeof groupRecord.preset_bundles === "object" && !Array.isArray(groupRecord.preset_bundles)
            ? Object.entries(groupRecord.preset_bundles as Record<string, unknown>)
            : [];
        return [{
          key: groupKey,
          label:
            typeof groupRecord.label === "string" && groupRecord.label.trim()
              ? groupRecord.label.trim()
              : (groupKey === "__ungrouped__" ? "Ungrouped parameters" : groupKey),
          helpNote:
            typeof groupRecord.help_note === "string"
              ? groupRecord.help_note
              : "",
          collapsedByDefault: Boolean(groupRecord.collapsed),
          visibilityRule:
            groupRecord.visibility_rule === "manual"
            || groupRecord.visibility_rule === "binding_active"
            || groupRecord.visibility_rule === "value_active"
              ? groupRecord.visibility_rule
              : "always",
          coordinationPolicy:
            groupRecord.coordination_policy === "highest_source_priority"
            || groupRecord.coordination_policy === "sticky_auto_selection"
            || groupRecord.coordination_policy === "manual_resolution"
              ? groupRecord.coordination_policy
              : "manual_source_priority",
          presetBundles: rawPresetBundles.flatMap(([bundleKey, rawBundle]) => {
            if (!rawBundle || typeof rawBundle !== "object" || Array.isArray(rawBundle)) {
              return [];
            }
            const bundleRecord = rawBundle as Record<string, unknown>;
            const rawValues =
              bundleRecord.values && typeof bundleRecord.values === "object" && !Array.isArray(bundleRecord.values)
                ? (bundleRecord.values as Record<string, unknown>)
                : {};
            const rawBindings =
              bundleRecord.binding_presets && typeof bundleRecord.binding_presets === "object" && !Array.isArray(bundleRecord.binding_presets)
                ? (bundleRecord.binding_presets as Record<string, unknown>)
                : {};
            const rawDependencies =
              bundleRecord.depends_on && typeof bundleRecord.depends_on === "object" && !Array.isArray(bundleRecord.depends_on)
                ? Object.entries(bundleRecord.depends_on as Record<string, unknown>)
                : [];
            return [{
              key: bundleKey,
              label:
                typeof bundleRecord.label === "string" && bundleRecord.label.trim()
                  ? bundleRecord.label.trim()
                  : bundleKey,
              helpNote:
                typeof bundleRecord.help_note === "string"
                  ? bundleRecord.help_note
                  : "",
              priority:
                typeof bundleRecord.priority === "number" && Number.isFinite(bundleRecord.priority)
                  ? bundleRecord.priority
                  : 0,
              autoSelectRule:
                bundleRecord.auto_select_rule === "always"
                || bundleRecord.auto_select_rule === "binding_active"
                || bundleRecord.auto_select_rule === "value_active"
                  ? bundleRecord.auto_select_rule
                  : "manual",
              dependencies: rawDependencies.flatMap(([dependencyKey, rawDependency]) => {
                if (!rawDependency || typeof rawDependency !== "object" || Array.isArray(rawDependency)) {
                  return [];
                }
                const dependencyRecord = rawDependency as Record<string, unknown>;
                const groupKey =
                  typeof dependencyRecord.group_key === "string"
                    ? dependencyRecord.group_key.trim()
                    : "";
                const targetBundleKey =
                  typeof dependencyRecord.bundle_key === "string"
                    ? dependencyRecord.bundle_key.trim()
                    : "";
                if (!groupKey || !targetBundleKey) {
                  return [];
                }
                return [{
                  key: dependencyKey,
                  groupKey,
                  bundleKey: targetBundleKey,
                } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState];
              }),
              parameterValues: Object.fromEntries(
                Object.entries(rawValues).flatMap(([parameterKey, rawValue]) =>
                  rawValue === undefined || rawValue === null
                    ? []
                    : [[parameterKey, formatCollectionQueryBuilderValue(rawValue, "string")]],
                ),
              ),
              parameterBindingPresets: Object.fromEntries(
                Object.entries(rawBindings).flatMap(([parameterKey, rawValue]) =>
                  typeof rawValue === "string" && rawValue.trim()
                    ? [[parameterKey, rawValue.trim()]]
                    : [],
                ),
              ),
            } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState];
          }),
        } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState];
      });
      return [
        {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("template"),
          key: templateKey,
          parameters: parsedParameters,
          parameterGroups: mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
            parsedParameters,
            parsedParameterGroups,
          ),
          node: templateNode,
        } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateState,
      ];
    });
    if (singleClause && !predicates.length && !predicateTemplates.length) {
      return {
        mode: "single",
        draftClause: singleClause,
        groupLogic: "and",
        rootNegated: false,
        expressionChildren: [],
        predicates: [],
        predicateTemplates: [],
      };
    }
    if (!rootNode || typeof rootNode !== "object" || Array.isArray(rootNode)) {
      return null;
    }
    const rootRecord = rootNode as Record<string, unknown>;
    const childNodes = Array.isArray(rootRecord.children) ? rootRecord.children : [];
    let expressionChildren = childNodes.reduce<RunSurfaceCollectionQueryBuilderChildState[]>(
      (accumulator, rawChild) => {
        const parsedChild = parseRunSurfaceCollectionQueryBuilderChildState(rawChild, contracts);
        if (parsedChild) {
          accumulator.push(parsedChild);
        }
        return accumulator;
      },
      [],
    );
    const rootLogic =
      rootRecord.logic === "or" || rootRecord.logic === "and"
        ? rootRecord.logic
        : "and";
    if (!expressionChildren.length && singleClause) {
      expressionChildren = [
        {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
          kind: "clause",
          clause: singleClause,
        },
      ];
    }
    if (!expressionChildren.length) {
      return null;
    }
    const firstClause = expressionChildren.find(
      (child): child is RunSurfaceCollectionQueryBuilderClauseState => child.kind === "clause",
    );
    return {
      mode: "grouped",
      draftClause: firstClause?.clause ?? buildRunSurfaceCollectionQueryBuilderDefaultClauseState(contracts),
      groupLogic: rootLogic,
      rootNegated: rootRecord.negated === true,
      expressionChildren,
      predicates,
      predicateTemplates,
    };
  } catch {
    return null;
  }
}

export type RunSurfaceCollectionQueryBuilderApplyPayload = {
  expression: string;
  expressionLabel: string;
  resolvedPath: string[];
  quantifier: "any" | "all" | "none";
  fieldKey: string;
  operatorKey: string;
};

export type RunSurfaceCollectionQueryRuntimeCandidateSample = {
  candidatePath: string;
  candidateReplayId: string | null;
  candidateValue: string;
  detail: string;
  result: boolean;
  runId: string;
  runContextArtifactHoverKeys: string[];
  runContextComponentKey: string | null;
  runContextLabel: string | null;
  runContextSection: ComparisonScoreSection | null;
  runContextSubFocusKey: string | null;
};

export type RunSurfaceCollectionQueryRuntimeCandidateContextSelection = {
  artifactHoverKey: string | null;
  componentKey: string | null;
  runId: string;
  section: ComparisonScoreSection | null;
  subFocusKey: string | null;
};

export type RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection = {
  artifactHoverKey: string;
  componentKey: string | null;
  runId: string;
  sampleKeys: string[];
  section: ComparisonScoreSection | null;
  subFocusKey: string | null;
};

export type RunSurfaceCollectionQueryBuilderClauseDiffItem = {
  detail: string;
  key: string;
  label: string;
};

export type RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem = {
  detail: string;
  key: string;
  runId: string;
};

export type RunSurfaceCollectionQueryRuntimeQuantifierOutcome = {
  candidateCount: number;
  detail: string;
  matchedCount: number;
  result: boolean;
  runId: string;
};

export type RunSurfaceCollectionQueryRuntimeCandidateTrace = {
  allValues: RunSurfaceCollectionQueryRuntimeCandidateSample[];
  bindingContextByKey?: Record<string, string> | null;
  candidateAccessor: string;
  candidatePath: string;
  comparedValue: string;
  detail: string;
  editorClause: HydratedRunSurfaceCollectionQueryBuilderState | null;
  location: string;
  quantifier: "any" | "all" | "none";
  result: boolean;
  runOutcomes: RunSurfaceCollectionQueryRuntimeQuantifierOutcome[];
  sampleMatchCount: number;
  sampleTotalCount: number;
  sampleTruncated: boolean;
  sampleValues: RunSurfaceCollectionQueryRuntimeCandidateSample[];
};
