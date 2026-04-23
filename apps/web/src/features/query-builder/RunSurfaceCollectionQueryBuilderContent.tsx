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
import { QueryBuilderReplayGovernanceSection } from "./QueryBuilderReplayGovernanceSection";
import {
  RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID,
  RUN_SURFACE_COLLECTION_RUNTIME_MISSING,
  RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT,
  addRunSurfaceCollectionQueryBuilderChildToGroup,
  applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy,
  areHydratedRunSurfaceCollectionQueryBuilderStatesEqual,
  arePredicateRefReplayApplyHistoryEntriesEquivalent,
  areRunSurfaceCollectionQueryBuilderRecordValuesEqual,
  areRunSurfaceCollectionQueryBuilderReplayIntentsEqual,
  areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual,
  benchmarkArtifactSectionLabels,
  benchmarkArtifactSummaryLabels,
  buildComparisonProvenanceArtifactSectionLineHoverKey,
  buildComparisonProvenanceArtifactSummaryHoverKey,
  buildComparisonRunListDataSymbolSubFocusKey,
  buildComparisonRunListLineSubFocusKey,
  buildComparisonRunListOrderPreviewSubFocusKey,
  buildPredicateRefReplayApplyConflictMergedEntry,
  buildPredicateRefReplayApplyConflictResolutionPreview,
  buildPredicateRefReplayApplyConflictReview,
  buildRunSurfaceCollectionQueryBuilderClauseDiffItems,
  buildRunSurfaceCollectionQueryBuilderDefaultClauseState,
  buildRunSurfaceCollectionQueryBuilderEntityId,
  buildRunSurfaceCollectionQueryBuilderNodeFromChild,
  buildRunSurfaceCollectionQueryBuilderNodeFromClause,
  buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId,
  buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId,
  buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId,
  buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState,
  buildRunSurfaceCollectionQueryBuilderReplayIntentUrl,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId,
  buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret,
  buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys,
  buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries,
  buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries,
  buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSymbolVariants,
  buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection,
  buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems,
  buildRunSurfaceCollectionQueryRuntimeCandidateReplayId,
  buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey,
  buildRunSurfaceCollectionQueryRuntimeCandidateSamples,
  buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause,
  clonePredicateRefReplayApplyHistoryEntry,
  cloneRunSurfaceCollectionQueryBuilderChildState,
  coerceCollectionQueryBuilderValue,
  collectRunSurfaceCollectionQueryBuilderTemplateParameters,
  collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause,
  collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings,
  collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts,
  collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts,
  countRunSurfaceCollectionQueryBuilderChildren,
  decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue,
  decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
  doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch,
  doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext,
  encodeComparisonScoreLinkToken,
  encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue,
  encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
  evaluateRunSurfaceCollectionQueryRuntimeCondition,
  evaluateRunSurfaceCollectionQueryRuntimeQuantifierOutcome,
  extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl,
  findRunSurfaceCollectionQueryBuilderGroup,
  formatBenchmarkArtifactInlineValue,
  formatBenchmarkArtifactSectionLabel,
  formatBenchmarkArtifactSectionValue,
  formatBenchmarkArtifactSummaryLabel,
  formatBenchmarkArtifactSummaryValue,
  formatCollectionQueryBuilderValue,
  formatComparisonTooltipConflictSessionRelativeTime,
  formatPredicateRefReplayApplyHistoryRowSummary,
  formatPredicateRefReplayApplyHistorySelectionKeyLabel,
  formatPredicateRefReplayApplyHistorySnapshotValue,
  formatRelativeTimestampLabel,
  formatRunSurfaceCollectionQueryBuilderChildSummary,
  formatRunSurfaceCollectionQueryBuilderClauseParameterSource,
  formatRunSurfaceCollectionQueryBuilderClauseSummary,
  formatRunSurfaceCollectionQueryBuilderClauseValueSource,
  formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel,
  formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel,
  formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue,
  formatRunSurfaceCollectionQueryRuntimePath,
  formatRunSurfaceCollectionQueryRuntimePathSegment,
  formatTimestamp,
  fromRunSurfaceCollectionQueryBindingReferenceValue,
  getCollectionQueryRecordArray,
  getCollectionQuerySchemaId,
  getCollectionQueryStringArray,
  getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys,
  getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs,
  getRunSurfaceCollectionQueryExpressionAuthoring,
  getRunSurfaceCollectionQueryParameterDomains,
  getRunSurfaceCollectionQuerySchemas,
  groupRunSurfaceCollectionQueryBuilderTemplateParameters,
  hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment,
  isDefaultRunSurfaceCollectionQueryBuilderReplayIntent,
  isRunSurfaceCollectionQueryBindingReferenceValue,
  isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface,
  limitPredicateRefReplayApplyConflictEntries,
  limitPredicateRefReplayApplySyncAuditEntries,
  limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts,
  limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys,
  loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts,
  loadRunSurfaceCollectionQueryBuilderReplayApplyHistory,
  loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity,
  loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail,
  loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState,
  loadRunSurfaceCollectionQueryBuilderReplayIntent,
  loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState,
  loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret,
  mergePredicateRefReplayApplyHistoryEntries,
  mergePredicateRefReplayApplySyncAuditEntries,
  mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  mergeRunSurfaceCollectionQueryBuilderTemplateGroups,
  mergeRunSurfaceCollectionQueryBuilderTemplateParameters,
  normalizePredicateRefReplayApplyConflictEntry,
  normalizePredicateRefReplayApplyHistoryEntry,
  normalizePredicateRefReplayApplySyncAuditEntry,
  normalizeReplayApplySnapshotRecord,
  normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
  normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey,
  normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey,
  normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText,
  normalizeRunSurfaceCollectionQueryRuntimeCollectionItems,
  normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue,
  normalizeRunSurfaceCollectionQueryRuntimeNumericValue,
  parseRunSurfaceCollectionQueryBuilderChildState,
  parseRunSurfaceCollectionQueryBuilderClauseState,
  parseRunSurfaceCollectionQueryBuilderExpressionState,
  parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue,
  parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken,
  persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts,
  persistRunSurfaceCollectionQueryBuilderReplayApplyHistory,
  persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail,
  persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState,
  persistRunSurfaceCollectionQueryBuilderReplayIntent,
  persistRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState,
  persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState,
  pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState,
  readRunSurfaceCollectionQueryBuilderReplayIntentStorageState,
  readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState,
  removeRunSurfaceCollectionQueryBuilderChild,
  removeRunSurfaceCollectionQueryBuilderPredicateRefs,
  replaceRunSurfaceCollectionQueryBuilderPredicateRefs,
  resolveCollectionQueryPath,
  resolveCollectionQueryTemplateValues,
  resolveRunSurfaceCollectionQueryRuntimeCollectionItems,
  resolveRunSurfaceCollectionQueryRuntimeValuePath,
  scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch,
  serializeComparablePredicateRefReplayApplyHistoryEntry,
  serializeComparablePredicateRefReplayApplyHistoryRow,
  serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory,
  sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles,
  toRunSurfaceCollectionQueryBindingReferenceValue,
  toRunSurfaceCollectionQueryRuntimeIterableValues,
  updateRunSurfaceCollectionQueryBuilderClause,
  updateRunSurfaceCollectionQueryBuilderGroup,
} from "./model";
import type {
  HydratedRunSurfaceCollectionQueryBuilderExpressionState,
  HydratedRunSurfaceCollectionQueryBuilderState,
  PredicateRefReplayApplyConflictDiffItem,
  PredicateRefReplayApplyConflictDraftReview,
  PredicateRefReplayApplyConflictEntry,
  PredicateRefReplayApplyConflictPolicy,
  PredicateRefReplayApplyConflictResolutionPreview,
  PredicateRefReplayApplyConflictReview,
  PredicateRefReplayApplyConflictState,
  PredicateRefReplayApplyHistoryEntry,
  PredicateRefReplayApplyHistoryRow,
  PredicateRefReplayApplyHistoryTabIdentity,
  PredicateRefReplayApplySyncAuditEntry,
  PredicateRefReplayApplySyncAuditFilter,
  PredicateRefReplayApplySyncAuditTrailState,
  PredicateRefReplayApplySyncGovernanceState,
  PredicateRefReplayApplySyncMode,
  RunSurfaceCollectionQueryBuilderApplyPayload,
  RunSurfaceCollectionQueryBuilderChildState,
  RunSurfaceCollectionQueryBuilderClauseDiffItem,
  RunSurfaceCollectionQueryBuilderClauseState,
  RunSurfaceCollectionQueryBuilderEditorTarget,
  RunSurfaceCollectionQueryBuilderGroupState,
  RunSurfaceCollectionQueryBuilderPredicateRefState,
  RunSurfaceCollectionQueryBuilderPredicateState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
  RunSurfaceCollectionQueryBuilderReplayIntentBrowserState,
  RunSurfaceCollectionQueryBuilderReplayIntentState,
  RunSurfaceCollectionQueryBuilderReplayIntentStorageState,
  RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkAliasState,
  RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkAuditState,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState,
  RunSurfaceCollectionQueryBuilderReplayLinkShareMode,
  RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection,
  RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
  RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem,
  RunSurfaceCollectionQueryRuntimeCandidateSample,
  RunSurfaceCollectionQueryRuntimeCandidateTrace,
  RunSurfaceCollectionQueryRuntimeCollectionItem,
  RunSurfaceCollectionQueryRuntimePathToken,
  RunSurfaceCollectionQueryRuntimeQuantifierOutcome,
} from "./model";
import { useQueryBuilderAuthoringState } from "./useQueryBuilderAuthoringState";
import { useQueryBuilderReplayIntentFlow } from "./useQueryBuilderReplayIntentFlow";

export function RunSurfaceCollectionQueryBuilder({
  contracts,
  compact = false,
  activeExpression,
  activeExpressionLabel,
  applyLabel = "Apply expression",
  runtimeRuns = [],
  activeRuntimeCandidateRunContext = null,
  onApplyExpression,
  onClearExpression,
  onFocusRuntimeCandidateRunContext,
}: {
  contracts: RunSurfaceCollectionQueryContract[];
  compact?: boolean;
  activeExpression?: string | null;
  activeExpressionLabel?: string | null;
  applyLabel?: string;
  runtimeRuns?: Run[];
  activeRuntimeCandidateRunContext?: RunSurfaceCollectionQueryRuntimeCandidateContextSelection | null;
  onApplyExpression?: (payload: RunSurfaceCollectionQueryBuilderApplyPayload) => void;
  onClearExpression?: (() => void) | null;
  onFocusRuntimeCandidateRunContext?: ((
    sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
    options?: { artifactHoverKey?: string | null },
  ) => void) | null;
}) {
  const {
    activeContract,
    activeContractKey,
    activeField,
    activeFieldKey,
    activeOperator,
    activeOperatorKey,
    activeSchema,
    activeSchemaId,
    builderValue,
    bundleCoordinationSimulationApprovalDecisionsByGroupKey,
    bundleCoordinationSimulationApprovalDiffOnly,
    bundleCoordinationSimulationApprovalOpen,
    bundleCoordinationSimulationFinalSummaryOpen,
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationPromotionDecisionsByGroupKey,
    bundleCoordinationSimulationReplayActionTypeFilter,
    bundleCoordinationSimulationReplayEdgeFilter,
    bundleCoordinationSimulationReplayGroupFilter,
    bundleCoordinationSimulationReplayIndex,
    bundleCoordinationSimulationScope,
    editorNegated,
    editorTarget,
    expressionAuthoring,
    expressionChildren,
    expressionMode,
    groupLogic,
    lastHydratedExpressionRef,
    parameterBindingKeys,
    parameterDomains,
    parameterValues,
    pendingHydratedState,
    predicateDraftKey,
    predicateRefDraftBindings,
    predicateRefDraftKey,
    predicateRefGroupAutoBundleSelections,
    predicateRefGroupBundleSelections,
    predicateTemplates,
    predicates,
    quantifier,
    rootNegated,
    selectedGroupId,
    setActiveContractKey,
    setActiveFieldKey,
    setActiveOperatorKey,
    setActiveSchemaId,
    setBuilderValue,
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey,
    setBundleCoordinationSimulationApprovalDiffOnly,
    setBundleCoordinationSimulationApprovalOpen,
    setBundleCoordinationSimulationFinalSummaryOpen,
    setBundleCoordinationSimulationPolicy,
    setBundleCoordinationSimulationPromotionDecisionsByGroupKey,
    setBundleCoordinationSimulationReplayActionTypeFilter,
    setBundleCoordinationSimulationReplayEdgeFilter,
    setBundleCoordinationSimulationReplayGroupFilter,
    setBundleCoordinationSimulationReplayIndex,
    setBundleCoordinationSimulationScope,
    setEditorNegated,
    setEditorTarget,
    setExpressionChildren,
    setExpressionMode,
    setGroupLogic,
    setParameterBindingKeys,
    setParameterValues,
    setPendingHydratedState,
    setPredicateDraftKey,
    setPredicateRefDraftBindings,
    setPredicateRefDraftKey,
    setPredicateRefGroupAutoBundleSelections,
    setPredicateRefGroupBundleSelections,
    setPredicateTemplates,
    setPredicates,
    setQuantifier,
    setRootNegated,
    setSelectedGroupId,
    setTemplateDraftAuthoringTarget,
    setTemplateDraftKey,
    setTemplateGroupExpansionByKey,
    setTemplateParameterDraftBindingPresetsByContext,
    setTemplateParameterDraftDefaultsByContext,
    setTemplateParameterDraftGroupsByContext,
    setTemplateParameterDraftHelpNotesByContext,
    setTemplateParameterDraftLabelsByContext,
    setTemplateParameterDraftOrderByContext,
    setTemplateParameterGroupDraftMetadataByContext,
    templateDraftAuthoringTarget,
    templateDraftKey,
    templateGroupExpansionByKey,
    templateParameterDraftBindingPresetsByContext,
    templateParameterDraftDefaultsByContext,
    templateParameterDraftGroupsByContext,
    templateParameterDraftHelpNotesByContext,
    templateParameterDraftLabelsByContext,
    templateParameterDraftOrderByContext,
    templateParameterGroupDraftMetadataByContext,
  } = useQueryBuilderAuthoringState(contracts);
  const bundleCoordinationSimulationPanelRef = useRef<HTMLDivElement | null>(null);
  const predicateRefReplayApplyHistoryTabIdentity = useMemo(
    () => loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity(),
    [],
  );
  const [predicateRefReplayApplyHistory, setPredicateRefReplayApplyHistory] =
    useState<PredicateRefReplayApplyHistoryEntry[]>(() => loadRunSurfaceCollectionQueryBuilderReplayApplyHistory());
  const predicateRefReplayApplyHistoryRef = useRef<PredicateRefReplayApplyHistoryEntry[]>([]);
  const initialPredicateRefReplayApplyGovernanceState = useMemo(
    () => loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState(
      predicateRefReplayApplyHistoryTabIdentity.tabId,
    ),
    [predicateRefReplayApplyHistoryTabIdentity.tabId],
  );
  const [predicateRefReplayApplySyncMode, setPredicateRefReplayApplySyncMode] =
    useState<PredicateRefReplayApplySyncMode>(initialPredicateRefReplayApplyGovernanceState.syncMode);
  const predicateRefReplayApplySyncModeRef = useRef<PredicateRefReplayApplySyncMode>(
    initialPredicateRefReplayApplyGovernanceState.syncMode,
  );
  const [predicateRefReplayApplyConflictPolicy, setPredicateRefReplayApplyConflictPolicy] =
    useState<PredicateRefReplayApplyConflictPolicy>(initialPredicateRefReplayApplyGovernanceState.conflictPolicy);
  const predicateRefReplayApplyConflictPolicyRef = useRef<PredicateRefReplayApplyConflictPolicy>(
    initialPredicateRefReplayApplyGovernanceState.conflictPolicy,
  );
  const [predicateRefReplayApplySyncAuditFilter, setPredicateRefReplayApplySyncAuditFilter] =
    useState<PredicateRefReplayApplySyncAuditFilter>(initialPredicateRefReplayApplyGovernanceState.auditFilter);
  const lastPersistedPredicateRefReplayApplyHistoryRef = useRef<string | null>(
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY),
  );
  const [predicateRefReplayApplySyncAuditTrail, setPredicateRefReplayApplySyncAuditTrail] =
    useState<PredicateRefReplayApplySyncAuditEntry[]>(() =>
      loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail(
        predicateRefReplayApplyHistoryTabIdentity.tabId,
      ));
  const [predicateRefReplayApplyConflicts, setPredicateRefReplayApplyConflicts] =
    useState<PredicateRefReplayApplyConflictEntry[]>(() =>
      loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts(
        predicateRefReplayApplyHistoryTabIdentity.tabId,
      ));
  const [predicateRefReplayApplyConflictDraftSourcesById, setPredicateRefReplayApplyConflictDraftSourcesById] =
    useState<Record<string, Record<string, "local" | "remote">>>({});
  const [predicateRefReplayApplyConflictSimulationConflictId, setPredicateRefReplayApplyConflictSimulationConflictId] =
    useState<string | null>(null);
  const [predicateRefReplayApplyConflictFocusedDecision, setPredicateRefReplayApplyConflictFocusedDecision] =
    useState<{ conflictId: string; decisionKey: string } | null>(null);
  const predicateRefReplayApplyConflictRowRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const collectionSchemas = useMemo(
    () => getRunSurfaceCollectionQuerySchemas(activeContract),
    [activeContract],
  );
  const [valueBindingKey, setValueBindingKey] = useState("");
  const [runtimeCandidateTraceDrillthroughByKey, setRuntimeCandidateTraceDrillthroughByKey] =
    useState<Record<string, boolean>>({});
  const [pinnedRuntimeCandidateClauseOriginKey, setPinnedRuntimeCandidateClauseOriginKey] =
    useState<string | null>(null);
  const [persistedRuntimeCandidateArtifactSelection, setPersistedRuntimeCandidateArtifactSelection] =
    useState<RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection | null>(null);
  const [focusedRuntimeCandidateSampleKey, setFocusedRuntimeCandidateSampleKey] =
    useState<string | null>(null);
  const [clauseReevaluationPreviewSelection, setClauseReevaluationPreviewSelection] =
    useState<{ diffItemKey: string | null; groupKey: string | null; traceKey: string | null }>({
      diffItemKey: null,
      groupKey: null,
      traceKey: null,
    });
  const builderEditorCardRef = useRef<HTMLDivElement | null>(null);
  const clauseReevaluationPreviewTraceRefs = useRef(new Map<string, HTMLDivElement>());
  const clauseReevaluationPreviewDiffItemRefs = useRef(new Map<string, HTMLDivElement>());

  useEffect(() => {
    if (!contracts.length) {
      setActiveContractKey("");
      return;
    }
    if (!contracts.some((contract) => contract.contract_key === activeContractKey)) {
      setActiveContractKey(contracts[0].contract_key);
    }
  }, [activeContractKey, contracts]);

  useEffect(() => {
    if (!activeSchema) {
      setActiveSchemaId("");
      return;
    }
    const schemaId = getCollectionQuerySchemaId(activeSchema);
    if (!collectionSchemas.some((schema) => getCollectionQuerySchemaId(schema) === activeSchemaId)) {
      setActiveSchemaId(schemaId);
    }
  }, [activeSchema, activeSchemaId, collectionSchemas]);

  useEffect(() => {
    if (!activeSchema) {
      setParameterValues({});
      return;
    }
    setParameterValues((current) => {
      const next: Record<string, string> = {};
      activeSchema.parameters.forEach((parameter) => {
        const optionValues = parameter.domain?.values.length
          ? parameter.domain.values
          : parameter.examples;
        if (current[parameter.key] && optionValues.includes(current[parameter.key])) {
          next[parameter.key] = current[parameter.key];
          return;
        }
        if (optionValues[0]) {
          next[parameter.key] = optionValues[0];
          return;
        }
        if (current[parameter.key]) {
          next[parameter.key] = current[parameter.key];
        }
      });
      return next;
    });
  }, [activeSchema]);

  useEffect(() => {
    if (!activeSchema) {
      setParameterBindingKeys({});
      return;
    }
    setParameterBindingKeys((current) =>
      Object.fromEntries(
        activeSchema.parameters
          .map((parameter) => [parameter.key, current[parameter.key] ?? ""] as const)
          .filter(([, value]) => value),
      ),
    );
  }, [activeSchema]);

  useEffect(() => {
    if (!activeField) {
      setActiveFieldKey("");
      return;
    }
    if (!activeSchema?.elementSchema.some((field) => field.key === activeFieldKey)) {
      setActiveFieldKey(activeField.key);
    }
  }, [activeField, activeFieldKey, activeSchema]);

  useEffect(() => {
    if (!activeOperator) {
      setActiveOperatorKey("");
      return;
    }
    if (!activeField?.operators.some((operator) => operator.key === activeOperatorKey)) {
      setActiveOperatorKey(activeOperator.key);
    }
  }, [activeField, activeOperator, activeOperatorKey]);

  useEffect(() => {
    const normalizedExpression = activeExpression?.trim() ?? "";
    if (!normalizedExpression) {
      lastHydratedExpressionRef.current = null;
      setPendingHydratedState(null);
      return;
    }
    if (normalizedExpression === lastHydratedExpressionRef.current) {
      return;
    }
    const hydratedState = parseRunSurfaceCollectionQueryBuilderExpressionState(normalizedExpression, contracts);
    if (!hydratedState) {
      lastHydratedExpressionRef.current = normalizedExpression;
      setPendingHydratedState(null);
      return;
    }
    lastHydratedExpressionRef.current = normalizedExpression;
    setExpressionMode(hydratedState.mode);
    setGroupLogic(hydratedState.groupLogic);
    setRootNegated(hydratedState.rootNegated);
    setExpressionChildren(hydratedState.expressionChildren);
    setPredicates(hydratedState.predicates);
    setPredicateTemplates(hydratedState.predicateTemplates);
    setSelectedGroupId(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID);
    setEditorTarget({ kind: "draft" });
    setPredicateDraftKey("");
    setTemplateDraftKey("");
    setPredicateRefDraftKey(
      hydratedState.predicates[0]?.key
      ?? hydratedState.predicateTemplates[0]?.key
      ?? "",
    );
    setPredicateRefDraftBindings({});
    if (hydratedState.draftClause) {
      setActiveContractKey(hydratedState.draftClause.contractKey);
      setPendingHydratedState(hydratedState.draftClause);
    } else {
      setPendingHydratedState(null);
    }
  }, [activeExpression, contracts]);

  useEffect(() => {
    if (!pendingHydratedState) {
      return;
    }
    if (activeContract?.contract_key !== pendingHydratedState.contractKey) {
      return;
    }
    if (activeSchemaId !== pendingHydratedState.schemaId) {
      setActiveSchemaId(pendingHydratedState.schemaId);
      return;
    }
    setParameterValues((current) => {
      const keys = new Set([
        ...Object.keys(current),
        ...Object.keys(pendingHydratedState.parameterValues),
      ]);
      let changed = false;
      const next: Record<string, string> = {};
      keys.forEach((key) => {
        const nextValue = pendingHydratedState.parameterValues[key] ?? "";
        next[key] = nextValue;
        if ((current[key] ?? "") !== nextValue) {
          changed = true;
        }
      });
      return changed ? next : current;
    });
    setQuantifier(pendingHydratedState.quantifier);
    setActiveFieldKey(pendingHydratedState.fieldKey);
    setActiveOperatorKey(pendingHydratedState.operatorKey);
    setBuilderValue(pendingHydratedState.builderValue);
    setParameterBindingKeys({ ...pendingHydratedState.parameterBindingKeys });
    setValueBindingKey(pendingHydratedState.valueBindingKey);
    setEditorNegated(pendingHydratedState.negated);
    setPendingHydratedState(null);
  }, [activeContract?.contract_key, activeSchemaId, pendingHydratedState]);

  useEffect(() => {
    const availablePredicateKeys = [...predicates.map((predicate) => predicate.key), ...predicateTemplates.map((template) => template.key)];
    if (!availablePredicateKeys.length) {
      setPredicateRefDraftKey("");
      setPredicateRefDraftBindings({});
      return;
    }
    if (!availablePredicateKeys.includes(predicateRefDraftKey)) {
      setPredicateRefDraftKey(availablePredicateKeys[0]);
    }
  }, [predicateRefDraftKey, predicateTemplates, predicates]);

  useEffect(() => {
    const activeTemplate =
      predicateTemplates.find((template) => template.key === predicateRefDraftKey) ?? null;
    if (!activeTemplate) {
      setPredicateRefDraftBindings({});
      return;
    }
    setPredicateRefDraftBindings((current) =>
      Object.fromEntries(
        activeTemplate.parameters.map((parameter) => [
          parameter.key,
          current[parameter.key]
          ?? (
            parameter.bindingPreset.trim()
              ? toRunSurfaceCollectionQueryBindingReferenceValue(parameter.bindingPreset.trim())
              : ""
          ),
        ]),
      ),
    );
  }, [predicateRefDraftKey, predicateTemplates]);

  useEffect(() => {
    if (expressionMode !== "grouped") {
      return;
    }
    if (
      selectedGroupId !== RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
      && !findRunSurfaceCollectionQueryBuilderGroup(expressionChildren, selectedGroupId)
    ) {
      setSelectedGroupId(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID);
    }
  }, [expressionChildren, expressionMode, selectedGroupId]);

  useEffect(() => {
    if (expressionMode === "grouped" && !expressionChildren.length) {
      setSelectedGroupId(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID);
    }
  }, [expressionChildren.length, expressionMode]);

  const resolvedCollectionPath = useMemo(
    () => (activeSchema ? resolveCollectionQueryPath(activeSchema.pathTemplate, parameterValues) : []),
    [activeSchema, parameterValues],
  );

  const coercedBuilderValue = useMemo(
    () => (activeField ? coerceCollectionQueryBuilderValue(builderValue, activeField.valueType) : builderValue),
    [activeField, builderValue],
  );

  const editorClauseState = useMemo<HydratedRunSurfaceCollectionQueryBuilderState | null>(() => {
    if (!activeSchema || !activeField || !activeOperator) {
      return null;
    }
    return {
      contractKey: activeContract?.contract_key ?? "",
      schemaId: getCollectionQuerySchemaId(activeSchema),
      parameterValues,
      parameterBindingKeys,
      quantifier,
      fieldKey: activeField.key,
      operatorKey: activeOperator.key,
      builderValue,
      valueBindingKey,
      negated: editorNegated,
    };
  }, [
    activeContract?.contract_key,
    activeField,
    activeOperator,
    activeSchema,
    builderValue,
    editorNegated,
    parameterBindingKeys,
    parameterValues,
    quantifier,
    valueBindingKey,
  ]);

  const setEditorFromClause = (clause: HydratedRunSurfaceCollectionQueryBuilderState) => {
    setActiveContractKey(clause.contractKey);
    setPendingHydratedState(clause);
  };

  const focusRuntimeCandidateClauseEditor = useCallback(
    (
      clause: HydratedRunSurfaceCollectionQueryBuilderState | null,
      originTraceKey?: string | null,
      previewGroupKey?: string | null,
    ) => {
      if (!clause) {
        return;
      }
      setEditorTarget({ kind: "draft" });
      setPredicateDraftKey("");
      setTemplateDraftKey("");
      setPinnedRuntimeCandidateClauseOriginKey(originTraceKey ?? null);
      setClauseReevaluationPreviewSelection({
        diffItemKey: null,
        groupKey: previewGroupKey ?? null,
        traceKey: originTraceKey ?? null,
      });
      setEditorFromClause(clause);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          builderEditorCardRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        });
      });
    },
    [],
  );

  const buildRuntimeCandidateTraceDrillthroughKey = useCallback(
    (
      scope: "focused_chain" | "active_replay",
      stepIndex: number,
      trace: RunSurfaceCollectionQueryRuntimeCandidateTrace,
    ) => `${scope}:${stepIndex}:${trace.location}:${trace.candidatePath}:${trace.candidateAccessor}`,
    [],
  );
  const doesRuntimeCandidateSampleMatchActiveContext = useCallback(
    (sample: RunSurfaceCollectionQueryRuntimeCandidateSample) =>
      doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext(
        sample,
        activeRuntimeCandidateRunContext,
      ),
    [activeRuntimeCandidateRunContext],
  );
  const doesRuntimeCandidateTraceMatchEditorClause = useCallback(
    (trace: RunSurfaceCollectionQueryRuntimeCandidateTrace) =>
      areHydratedRunSurfaceCollectionQueryBuilderStatesEqual(trace.editorClause, editorClauseState),
    [editorClauseState],
  );
  const doesRuntimeCandidateSampleMatchFocusedKey = useCallback(
    (sample: RunSurfaceCollectionQueryRuntimeCandidateSample) =>
      focusedRuntimeCandidateSampleKey === buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
    [focusedRuntimeCandidateSampleKey],
  );
  const doesRuntimeCandidateSampleMatchPersistedArtifactSelection = useCallback(
    (sample: RunSurfaceCollectionQueryRuntimeCandidateSample) =>
      persistedRuntimeCandidateArtifactSelection?.sampleKeys.includes(
        buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
      ) ?? false,
    [persistedRuntimeCandidateArtifactSelection],
  );

  const expressionLabel = useMemo(() => {
    if (!activeSchema || !activeField || !activeOperator) {
      return "";
    }
    const templateMarkers = [
      ...Object.values(parameterBindingKeys).filter(Boolean).map((bindingKey) => `$${bindingKey}`),
      ...(valueBindingKey ? [`$${valueBindingKey}`] : []),
    ];
    return `${editorNegated ? "not " : ""}${activeSchema.label} · ${quantifier} ${activeField.title ?? activeField.key} ${activeOperator.label || activeOperator.key}${templateMarkers.length ? ` · binds ${templateMarkers.join(", ")}` : ""}`;
  }, [activeField, activeOperator, activeSchema, editorNegated, parameterBindingKeys, quantifier, valueBindingKey]);

  const singleExpressionPreview = useMemo(() => {
    if (!editorClauseState) {
      return "";
    }
    const node = buildRunSurfaceCollectionQueryBuilderNodeFromClause(editorClauseState, contracts);
    return node ? JSON.stringify(node, null, 2) : "";
  }, [contracts, editorClauseState]);

  const groupedExpressionPreview = useMemo(() => {
    const predicateRegistry = Object.fromEntries(
      predicates.flatMap((predicate) => {
        const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
          predicate.node,
          contracts,
          expressionAuthoring,
          predicateTemplates,
        );
        return node ? [[predicate.key, node]] : [];
      }),
    );
    const predicateTemplateRegistry = Object.fromEntries(
      predicateTemplates.flatMap((template) => {
        const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
          template.node,
          contracts,
          expressionAuthoring,
          predicateTemplates,
        );
        if (!node) {
          return [];
        }
        const serializedParameters = template.parameters.some(
          (parameter) =>
            parameter.defaultValue.trim()
            || parameter.customLabel.trim()
            || parameter.groupName.trim()
            || parameter.helpNote.trim()
            || parameter.bindingPreset.trim(),
        )
          ? Object.fromEntries(
              template.parameters.map((parameter) => [
                parameter.key,
                {
                  ...(parameter.defaultValue.trim()
                    ? {
                        default: coerceCollectionQueryBuilderValue(
                          parameter.defaultValue,
                          parameter.valueType,
                        ),
                      }
                    : {}),
                  ...(parameter.customLabel.trim()
                    ? { label: parameter.customLabel.trim() }
                    : {}),
                  ...(parameter.groupName.trim()
                    ? { group: parameter.groupName.trim() }
                    : {}),
                  ...(parameter.helpNote.trim()
                    ? { help_note: parameter.helpNote.trim() }
                    : {}),
                  ...(parameter.bindingPreset.trim()
                    ? { binding_preset: parameter.bindingPreset.trim() }
                    : {}),
                },
              ]),
            )
          : template.parameters.map((parameter) => parameter.key);
        const serializedParameterGroups = template.parameterGroups.length
          ? Object.fromEntries(
              template.parameterGroups.map((group) => [
                group.key,
                {
                  label: group.label,
                  ...(group.helpNote.trim()
                    ? { help_note: group.helpNote.trim() }
                    : {}),
                  ...(group.collapsedByDefault ? { collapsed: true } : {}),
                  ...(group.visibilityRule !== "always"
                    ? { visibility_rule: group.visibilityRule }
                    : {}),
                  ...(group.coordinationPolicy !== "manual_source_priority"
                    ? { coordination_policy: group.coordinationPolicy }
                    : {}),
                  ...(group.presetBundles.length
                    ? {
                        preset_bundles: Object.fromEntries(
                          group.presetBundles.map((bundle) => [
                            bundle.key,
                            {
                              label: bundle.label,
                              ...(bundle.helpNote.trim()
                                ? { help_note: bundle.helpNote.trim() }
                                : {}),
                              ...(bundle.priority
                                ? { priority: bundle.priority }
                                : {}),
                              ...(bundle.autoSelectRule !== "manual"
                                ? { auto_select_rule: bundle.autoSelectRule }
                                : {}),
                              ...(bundle.dependencies.length
                                ? {
                                    depends_on: Object.fromEntries(
                                      bundle.dependencies.flatMap((dependency) =>
                                        dependency.groupKey.trim() && dependency.bundleKey.trim()
                                          ? [[dependency.key, {
                                              group_key: dependency.groupKey.trim(),
                                              bundle_key: dependency.bundleKey.trim(),
                                            }]]
                                          : [],
                                      ),
                                    ),
                                  }
                                : {}),
                              ...(Object.keys(bundle.parameterValues).length
                                ? {
                                    values: Object.fromEntries(
                                      Object.entries(bundle.parameterValues).map(([parameterKey, value]) => [
                                        parameterKey,
                                        coerceCollectionQueryBuilderValue(value, "string"),
                                      ]),
                                    ),
                                  }
                                : {}),
                              ...(Object.keys(bundle.parameterBindingPresets).length
                                ? {
                                    binding_presets: Object.fromEntries(
                                      Object.entries(bundle.parameterBindingPresets).flatMap(([parameterKey, value]) =>
                                        value.trim() ? [[parameterKey, value.trim()]] : [],
                                      ),
                                    ),
                                  }
                                : {}),
                            },
                          ]),
                        ),
                      }
                    : {}),
                },
              ]),
            )
          : undefined;
        return [[template.key, {
          [expressionAuthoring.predicateTemplates.templateField]: node,
          [expressionAuthoring.predicateTemplates.parametersField]: serializedParameters,
          ...(serializedParameterGroups
            ? { parameter_groups: serializedParameterGroups }
            : {}),
        }]];
      }),
    );
    const rootChildren = expressionChildren.reduce<Record<string, unknown>[]>((accumulator, child) => {
      const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
        child,
        contracts,
        expressionAuthoring,
        predicateTemplates,
      );
      if (node) {
        accumulator.push(node);
      }
      return accumulator;
    }, []);
    if (!rootChildren.length) {
      return "";
    }
    const rootNode = {
      ...(rootNegated ? { negated: true } : {}),
      logic: groupLogic,
      children: rootChildren,
    };
    const payload = (
      Object.keys(predicateRegistry).length
      || Object.keys(predicateTemplateRegistry).length
    )
      ? {
          ...(Object.keys(predicateRegistry).length
            ? { [expressionAuthoring.predicateRefs.registryField]: predicateRegistry }
            : {}),
          ...(Object.keys(predicateTemplateRegistry).length
            ? { [expressionAuthoring.predicateTemplates.registryField]: predicateTemplateRegistry }
            : {}),
          root: rootNode,
        }
      : rootNode;
    return JSON.stringify(payload, null, 2);
  }, [contracts, expressionAuthoring, expressionChildren, groupLogic, predicateTemplates, predicates, rootNegated]);

  const filterExpressionPreview = expressionMode === "grouped" ? groupedExpressionPreview : singleExpressionPreview;

  const activeEditorTargetLabel = useMemo(() => {
    if (editorTarget.kind === "expression_clause") {
      return "Editing expression clause";
    }
    if (editorTarget.kind === "predicate") {
      const predicate = predicates.find((entry) => entry.id === editorTarget.predicateId);
      return predicate ? `Editing predicate ${predicate.key}` : "Editing predicate";
    }
    if (editorTarget.kind === "template") {
      const template = predicateTemplates.find((entry) => entry.id === editorTarget.templateId);
      return template ? `Editing template ${template.key}` : "Editing template";
    }
    return expressionMode === "grouped" ? "Draft clause" : "Single-node clause";
  }, [editorTarget, expressionMode, predicateTemplates, predicates]);

  const groupedExpressionLabel = useMemo(() => {
    const counts = countRunSurfaceCollectionQueryBuilderChildren(expressionChildren);
    const parts = [`${rootNegated ? "NOT " : ""}${groupLogic.toUpperCase()} expression`];
    if (counts.clauses) {
      parts.push(`${counts.clauses} clause${counts.clauses === 1 ? "" : "s"}`);
    }
    if (counts.predicateRefs) {
      parts.push(`${counts.predicateRefs} predicate ref${counts.predicateRefs === 1 ? "" : "s"}`);
    }
    if (counts.groups) {
      parts.push(`${counts.groups} subgroup${counts.groups === 1 ? "" : "s"}`);
    }
    if (predicates.length) {
      parts.push(`${predicates.length} predicate definition${predicates.length === 1 ? "" : "s"}`);
    }
    if (predicateTemplates.length) {
      parts.push(`${predicateTemplates.length} template${predicateTemplates.length === 1 ? "" : "s"}`);
    }
    return parts.join(" · ");
  }, [expressionChildren, groupLogic, predicateTemplates.length, predicates.length, rootNegated]);

  const canApplyExpression = expressionMode === "grouped"
    ? Boolean(groupedExpressionPreview)
    : (builderValue.trim().length > 0 || Boolean(valueBindingKey.trim())) && Boolean(singleExpressionPreview);

  const applyCurrentExpression = () => {
    if (!onApplyExpression || !filterExpressionPreview) {
      return;
    }
    onApplyExpression({
      expression: filterExpressionPreview,
      expressionLabel: expressionMode === "grouped" ? groupedExpressionLabel : expressionLabel,
      resolvedPath: resolvedCollectionPath,
      quantifier,
      fieldKey: activeField?.key ?? "",
      operatorKey: activeOperator?.key ?? "",
    });
  };

  const addClauseToExpression = () => {
    if (!editorClauseState) {
      return;
    }
    const nextChild: RunSurfaceCollectionQueryBuilderClauseState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause: editorClauseState,
    };
    setExpressionChildren((current) =>
      selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        ? [...current, nextChild]
        : addRunSurfaceCollectionQueryBuilderChildToGroup(current, selectedGroupId, nextChild),
    );
    setExpressionMode("grouped");
    setEditorTarget({ kind: "draft" });
  };

  const addGroupToExpression = () => {
    const nextGroup: RunSurfaceCollectionQueryBuilderGroupState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("group"),
      kind: "group",
      logic: "and",
      negated: false,
      children: [],
    };
    setExpressionChildren((current) =>
      selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        ? [...current, nextGroup]
        : addRunSurfaceCollectionQueryBuilderChildToGroup(current, selectedGroupId, nextGroup),
    );
    setExpressionMode("grouped");
    setSelectedGroupId(nextGroup.id);
  };

  const saveSelectedSubtreeAsPredicate = () => {
    const trimmedKey = predicateDraftKey.trim();
    if (!trimmedKey || predicateKeyConflict || !selectedSubtreeNode) {
      return;
    }
    if (editorTarget.kind === "predicate") {
      const previousPredicate = predicates.find((predicate) => predicate.id === editorTarget.predicateId) ?? null;
      setPredicates((current) =>
        current.map((predicate) =>
          predicate.id === editorTarget.predicateId
            ? {
                ...predicate,
                key: trimmedKey,
                node: cloneRunSurfaceCollectionQueryBuilderChildState(selectedSubtreeNode),
              }
            : predicate,
        ),
      );
      if (previousPredicate && previousPredicate.key !== trimmedKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(current, previousPredicate.key, trimmedKey),
        );
      }
      return;
    }
    setPredicates((current) => [
      ...current,
      {
        id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate"),
        key: trimmedKey,
        node: cloneRunSurfaceCollectionQueryBuilderChildState(selectedSubtreeNode),
      },
    ]);
    setPredicateDraftKey("");
  };

  const buildTemplateStateFromNode = (
    key: string,
    node: RunSurfaceCollectionQueryBuilderChildState,
    existingParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[] = [],
    existingParameterGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[] = [],
  ): RunSurfaceCollectionQueryBuilderPredicateTemplateState => {
    const mergedParameters = mergeRunSurfaceCollectionQueryBuilderTemplateParameters(
      collectRunSurfaceCollectionQueryBuilderTemplateParameters(node, contracts, predicateTemplates),
      existingParameters,
    );
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("template"),
      key,
      parameters: mergedParameters,
      parameterGroups: mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
        mergedParameters,
        existingParameterGroups,
      ),
      node: cloneRunSurfaceCollectionQueryBuilderChildState(node),
    };
  };

  const saveSelectedSubtreeAsTemplate = () => {
    const trimmedKey = templateDraftKey.trim();
    if (!trimmedKey || templateKeyConflict || !selectedSubtreeNode) {
      return;
    }
    const nextTemplate = buildTemplateStateFromNode(
      trimmedKey,
      selectedSubtreeNode,
      subtreeEditableTemplateParameters,
      subtreeEditableTemplateParameterGroups,
    );
    if (editorTarget.kind === "template") {
      const previousTemplate = predicateTemplates.find((template) => template.id === editorTarget.templateId) ?? null;
      setPredicateTemplates((current) =>
        current.map((template) =>
          template.id === editorTarget.templateId
            ? {
                ...nextTemplate,
                id: template.id,
              }
            : template,
        ),
      );
      if (previousTemplate && previousTemplate.key !== trimmedKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(current, previousTemplate.key, trimmedKey),
        );
      }
      return;
    }
    setPredicateTemplates((current) => [...current, nextTemplate]);
    setTemplateDraftKey("");
  };

  const updateSelectedExpressionTarget = () => {
    if (!editorClauseState) {
      return;
    }
    if (editorTarget.kind === "expression_clause") {
      setExpressionChildren((current) =>
        updateRunSurfaceCollectionQueryBuilderClause(current, editorTarget.childId, editorClauseState),
      );
      return;
    }
    if (editorTarget.kind === "predicate") {
      setPredicates((current) =>
        current.map((predicate) =>
          predicate.id === editorTarget.predicateId
            ? {
                ...predicate,
                node: {
                  id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
                  kind: "clause",
                  clause: editorClauseState,
                },
              }
            : predicate,
        ),
      );
      return;
    }
    if (editorTarget.kind === "template") {
      setPredicateTemplates((current) =>
        current.map((template) =>
          template.id === editorTarget.templateId
            ? {
                ...buildTemplateStateFromNode(template.key, {
                  id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
                  kind: "clause",
                  clause: editorClauseState,
                }, clauseEditableTemplateParameters, clauseEditableTemplateParameterGroups),
                id: template.id,
              }
            : template,
        ),
      );
    }
  };

  const savePredicateFromEditor = () => {
    if (!editorClauseState) {
      return;
    }
    const trimmedKey = predicateDraftKey.trim();
    if (!trimmedKey) {
      return;
    }
    if (editorTarget.kind === "predicate") {
      const previousPredicate = predicates.find((predicate) => predicate.id === editorTarget.predicateId) ?? null;
      setPredicates((current) =>
        current.map((predicate) =>
          predicate.id === editorTarget.predicateId
            ? {
                ...predicate,
                key: trimmedKey,
                node: {
                  id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
                  kind: "clause",
                  clause: editorClauseState,
                },
              }
            : predicate,
        ),
      );
      if (previousPredicate && previousPredicate.key !== trimmedKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(current, previousPredicate.key, trimmedKey),
        );
      }
      return;
    }
    setPredicates((current) => [
      ...current,
      {
        id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate"),
        key: trimmedKey,
        node: {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
          kind: "clause",
          clause: editorClauseState,
        },
      },
    ]);
    setPredicateDraftKey("");
  };

  const saveTemplateFromEditor = () => {
    if (!editorClauseState) {
      return;
    }
    const trimmedKey = templateDraftKey.trim();
    if (!trimmedKey || templateKeyConflict) {
      return;
    }
    const nextNode: RunSurfaceCollectionQueryBuilderClauseState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause: editorClauseState,
    };
    if (editorTarget.kind === "template") {
      const previousTemplate = predicateTemplates.find((template) => template.id === editorTarget.templateId) ?? null;
      setPredicateTemplates((current) =>
        current.map((template) =>
          template.id === editorTarget.templateId
            ? {
                ...buildTemplateStateFromNode(
                  trimmedKey,
                  nextNode,
                  clauseEditableTemplateParameters,
                  clauseEditableTemplateParameterGroups,
                ),
                id: template.id,
              }
            : template,
        ),
      );
      if (previousTemplate && previousTemplate.key !== trimmedKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(current, previousTemplate.key, trimmedKey),
        );
      }
      return;
    }
    setPredicateTemplates((current) => [
      ...current,
      buildTemplateStateFromNode(
        trimmedKey,
        nextNode,
        clauseEditableTemplateParameters,
        clauseEditableTemplateParameterGroups,
      ),
    ]);
    setTemplateDraftKey("");
  };

  const addPredicateRefToExpression = () => {
    if (!predicateRefDraftKey) {
      return;
    }
    const referencedTemplate =
      predicateTemplates.find((template) => template.key === predicateRefDraftKey) ?? null;
    const nextChild: RunSurfaceCollectionQueryBuilderPredicateRefState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate-ref"),
      kind: "predicate_ref",
      predicateKey: predicateRefDraftKey,
      bindings: referencedTemplate
        ? Object.fromEntries(
            referencedTemplate.parameters.flatMap((parameter) => {
              const value = (
                predicateRefDraftBindings[parameter.key]?.trim()
                || (
                  parameter.bindingPreset.trim()
                    ? toRunSurfaceCollectionQueryBindingReferenceValue(parameter.bindingPreset.trim())
                    : ""
                )
              );
              return value ? [[parameter.key, value]] : [];
            }),
          )
        : {},
      negated: false,
    };
    setExpressionChildren((current) =>
      selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        ? [...current, nextChild]
        : addRunSurfaceCollectionQueryBuilderChildToGroup(current, selectedGroupId, nextChild),
    );
    setExpressionMode("grouped");
  };

  const removeExpressionChild = (childId: string) => {
    setExpressionChildren((current) => removeRunSurfaceCollectionQueryBuilderChild(current, childId));
    if (editorTarget.kind === "expression_clause" && editorTarget.childId === childId) {
      setEditorTarget({ kind: "draft" });
    }
    if (selectedGroupId === childId) {
      setSelectedGroupId(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID);
    }
  };

  const removePredicate = (predicateId: string) => {
    const predicate = predicates.find((entry) => entry.id === predicateId);
    setPredicates((current) => current.filter((entry) => entry.id !== predicateId));
    if (predicate) {
      setExpressionChildren((current) =>
        removeRunSurfaceCollectionQueryBuilderPredicateRefs(current, predicate.key),
      );
    }
    if (editorTarget.kind === "predicate" && editorTarget.predicateId === predicateId) {
      setEditorTarget({ kind: "draft" });
    }
  };

  const removeTemplate = (templateId: string) => {
    const template = predicateTemplates.find((entry) => entry.id === templateId);
    setPredicateTemplates((current) => current.filter((entry) => entry.id !== templateId));
    if (template) {
      setExpressionChildren((current) =>
        removeRunSurfaceCollectionQueryBuilderPredicateRefs(current, template.key),
      );
    }
    if (editorTarget.kind === "template" && editorTarget.templateId === templateId) {
      setEditorTarget({ kind: "draft" });
    }
  };

  const togglePredicateRefNegation = (childId: string) => {
    const toggleChildren = (
      children: RunSurfaceCollectionQueryBuilderChildState[],
    ): RunSurfaceCollectionQueryBuilderChildState[] =>
      children.map((child) => {
        if (child.kind === "predicate_ref" && child.id === childId) {
          return {
            ...child,
            negated: !child.negated,
          };
        }
        if (child.kind === "group") {
          return {
            ...child,
            children: toggleChildren(child.children),
          };
        }
        return child;
      });
    setExpressionChildren((current) => toggleChildren(current));
  };

  const selectedPredicate =
    editorTarget.kind === "predicate"
      ? predicates.find((predicate) => predicate.id === editorTarget.predicateId) ?? null
      : null;
  const selectedTemplate =
    editorTarget.kind === "template"
      ? predicateTemplates.find((template) => template.id === editorTarget.templateId) ?? null
      : null;
  const selectedRefTemplate =
    predicateTemplates.find((template) => template.key === predicateRefDraftKey) ?? null;
  const selectedRefTemplateParameterGroups = useMemo(
    () => (
      selectedRefTemplate
        ? groupRunSurfaceCollectionQueryBuilderTemplateParameters(
            selectedRefTemplate.parameters,
            selectedRefTemplate.parameterGroups,
          )
        : []
    ),
    [selectedRefTemplate],
  );
  const {
    applyRunSurfaceCollectionQueryBuilderReplayIntent,
    currentRunSurfaceCollectionQueryBuilderReplayIntent,
    lastHydratedReplayIntentTemplateIdRef,
    replayGovernanceSectionProps,
    replayIntentUrlTemplateKey,
    setReplayIntentUrlTemplateKey,
  } = useQueryBuilderReplayIntentFlow({
    bundleCoordinationSimulationReplayActionTypeFilter,
    bundleCoordinationSimulationReplayEdgeFilter,
    bundleCoordinationSimulationReplayGroupFilter,
    bundleCoordinationSimulationReplayIndex,
    bundleCoordinationSimulationScope,
    clauseReevaluationPreviewSelection,
    predicateRefReplayApplyHistoryTabIdentity,
    selectedRefTemplate,
    setBundleCoordinationSimulationReplayActionTypeFilter,
    setBundleCoordinationSimulationReplayEdgeFilter,
    setBundleCoordinationSimulationReplayGroupFilter,
    setBundleCoordinationSimulationReplayIndex,
    setBundleCoordinationSimulationScope,
    setClauseReevaluationPreviewSelection,
    setPredicateRefDraftKey,
  });
  useEffect(() => {
    if (!replayIntentUrlTemplateKey) {
      return;
    }
    const matchingTemplate =
      predicateTemplates.find((template) => template.key === replayIntentUrlTemplateKey) ?? null;
    if (!matchingTemplate || matchingTemplate.key === predicateRefDraftKey) {
      return;
    }
    setPredicateRefDraftKey(matchingTemplate.key);
  }, [predicateRefDraftKey, predicateTemplates, replayIntentUrlTemplateKey]);
  const selectedRefTemplateReplayApplyHistory = useMemo(
    () => (
      selectedRefTemplate
        ? predicateRefReplayApplyHistory.filter((entry) => entry.templateId === selectedRefTemplate.id)
        : []
    ),
    [predicateRefReplayApplyHistory, selectedRefTemplate],
  );
  const latestSelectedRefTemplateReplayApplyEntry = useMemo(
    () => selectedRefTemplateReplayApplyHistory[0] ?? null,
    [selectedRefTemplateReplayApplyHistory],
  );
  const selectedRefTemplateReplayApplySyncAuditTrail = useMemo(
    () => (
      selectedRefTemplate
        ? predicateRefReplayApplySyncAuditTrail.filter((entry) => entry.templateId === selectedRefTemplate.id)
        : predicateRefReplayApplySyncAuditTrail
    ),
    [predicateRefReplayApplySyncAuditTrail, selectedRefTemplate],
  );
  const visibleSelectedRefTemplateReplayApplySyncAuditTrail = useMemo(
    () => selectedRefTemplateReplayApplySyncAuditTrail.filter((entry) => {
      if (predicateRefReplayApplySyncAuditFilter === "local") {
        return entry.sourceTabId === predicateRefReplayApplyHistoryTabIdentity.tabId;
      }
      if (predicateRefReplayApplySyncAuditFilter === "remote") {
        return entry.sourceTabId !== predicateRefReplayApplyHistoryTabIdentity.tabId;
      }
      if (predicateRefReplayApplySyncAuditFilter === "apply") {
        return entry.kind.endsWith("_apply");
      }
      if (predicateRefReplayApplySyncAuditFilter === "restore") {
        return entry.kind.endsWith("_restore");
      }
      if (predicateRefReplayApplySyncAuditFilter === "conflict") {
        return entry.kind.includes("conflict");
      }
      return true;
    }),
    [
      predicateRefReplayApplyHistoryTabIdentity.tabId,
      predicateRefReplayApplySyncAuditFilter,
      selectedRefTemplateReplayApplySyncAuditTrail,
    ],
  );
  const selectedRefTemplateReplayApplyConflicts = useMemo(
    () => (
      selectedRefTemplate
        ? predicateRefReplayApplyConflicts.filter((entry) => entry.templateId === selectedRefTemplate.id)
        : predicateRefReplayApplyConflicts
    ),
    [predicateRefReplayApplyConflicts, selectedRefTemplate],
  );
  const selectedRefTemplateReplayApplyConflictReviews = useMemo<PredicateRefReplayApplyConflictDraftReview[]>(
    () => {
      const parameterGroupKeyByParameterKey = Object.fromEntries(
        selectedRefTemplateParameterGroups.flatMap((group) =>
          group.parameters.map((parameter) => [parameter.key, group.key] as const)),
      );
      return selectedRefTemplateReplayApplyConflicts.map((conflict) => {
        const review = buildPredicateRefReplayApplyConflictReview(
          conflict,
          predicateRefReplayApplyHistoryTabIdentity.label,
          parameterGroupKeyByParameterKey,
        );
        const editableItems = [
          ...review.summaryDiffs,
          ...review.rowDiffs,
          ...review.selectionSnapshotDiffs,
          ...review.bindingSnapshotDiffs,
        ].filter((item) => item.editable);
        const storedDraftSources = predicateRefReplayApplyConflictDraftSourcesById[conflict.conflictId] ?? {};
        const selectedSources = Object.fromEntries(
          editableItems.map((item) => [item.decisionKey, storedDraftSources[item.decisionKey] ?? "local"]),
        ) as Record<string, "local" | "remote">;
        const mergedEntry = buildPredicateRefReplayApplyConflictMergedEntry(conflict, selectedSources);
        const selectedRemoteCount = Object.values(selectedSources).filter((source) => source === "remote").length;
        const hasRemoteSelection = selectedRemoteCount > 0;
        const hasMixedSelection = hasRemoteSelection && selectedRemoteCount < editableItems.length;
        const mergedPreview = buildPredicateRefReplayApplyConflictResolutionPreview(
          conflict,
          mergedEntry,
          "merged",
          hasRemoteSelection
            ? hasMixedSelection
              ? `Applies a partial reviewed merge with ${selectedRemoteCount} remote field selections and ${editableItems.length - selectedRemoteCount} local field selections.`
              : `Applies the fully reviewed remote version across all ${editableItems.length} editable field differences.`
            : "Keeps the local version because no remote field selections are currently staged.",
        );
        return {
          ...review,
          editableDiffCount: editableItems.length,
          hasMixedSelection,
          hasRemoteSelection,
          mergedEntry,
          mergedPreview,
          selectedRemoteCount,
          selectedSources,
        };
      });
    },
    [
      predicateRefReplayApplyConflictDraftSourcesById,
      predicateRefReplayApplyHistoryTabIdentity.label,
      selectedRefTemplateParameterGroups,
      selectedRefTemplateReplayApplyConflicts,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationReview = useMemo(
    () => (
      predicateRefReplayApplyConflictSimulationConflictId
        ? selectedRefTemplateReplayApplyConflictReviews.find(
            (review) => review.conflict.conflictId === predicateRefReplayApplyConflictSimulationConflictId,
          ) ?? null
        : null
    ),
    [
      predicateRefReplayApplyConflictSimulationConflictId,
      selectedRefTemplateReplayApplyConflictReviews,
    ],
  );
  useEffect(() => {
    predicateRefReplayApplyHistoryRef.current = predicateRefReplayApplyHistory;
  }, [predicateRefReplayApplyHistory]);
  useEffect(() => {
    predicateRefReplayApplySyncModeRef.current = predicateRefReplayApplySyncMode;
  }, [predicateRefReplayApplySyncMode]);
  useEffect(() => {
    predicateRefReplayApplyConflictPolicyRef.current = predicateRefReplayApplyConflictPolicy;
  }, [predicateRefReplayApplyConflictPolicy]);
  const appendPredicateRefReplayApplySyncAuditEntry = useCallback(
    (entry: PredicateRefReplayApplySyncAuditEntry) => {
      setPredicateRefReplayApplySyncAuditTrail((current) =>
        mergePredicateRefReplayApplySyncAuditEntries(current, [entry]),
      );
    },
    [],
  );
  const setPredicateRefReplayApplyConflictDraftSource = useCallback(
    (
      conflictId: string,
      decisionKey: string,
      source: "local" | "remote",
    ) => {
      setPredicateRefReplayApplyConflictDraftSourcesById((current) => ({
        ...current,
        [conflictId]: {
          ...(current[conflictId] ?? {}),
          [decisionKey]: source,
        },
      }));
    },
    [],
  );
  const setPredicateRefReplayApplyConflictFocusedDecisionState = useCallback(
    (conflictId: string, decisionKey: string) => {
      setPredicateRefReplayApplyConflictFocusedDecision({ conflictId, decisionKey });
    },
    [],
  );
  const resetPredicateRefReplayApplyConflictDraftSource = useCallback((conflictId: string) => {
    setPredicateRefReplayApplyConflictDraftSourcesById((current) => {
      if (!current[conflictId]) {
        return current;
      }
      const next = { ...current };
      delete next[conflictId];
      return next;
    });
  }, []);
  const focusPredicateRefReplayApplyConflictDecision = useCallback(
    (conflictId: string, decisionKey: string) => {
      setPredicateRefReplayApplyConflictFocusedDecisionState(conflictId, decisionKey);
      const refKey = `${conflictId}:${decisionKey}`;
      requestAnimationFrame(() => {
        const node = predicateRefReplayApplyConflictRowRefs.current[refKey];
        if (!node) {
          return;
        }
        node.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
        node.focus({
          preventScroll: true,
        });
      });
    },
    [setPredicateRefReplayApplyConflictFocusedDecisionState],
  );
  const togglePredicateRefReplayApplyConflictSimulationFieldPickSource = useCallback(
    (decisionKey: string) => {
      if (!activePredicateRefReplayApplyConflictSimulationReview) {
        return;
      }
      setPredicateRefReplayApplyConflictFocusedDecisionState(
        activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId,
        decisionKey,
      );
      const currentSource =
        activePredicateRefReplayApplyConflictSimulationReview.selectedSources[decisionKey] ?? "local";
      setPredicateRefReplayApplyConflictDraftSource(
        activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId,
        decisionKey,
        currentSource === "remote" ? "local" : "remote",
      );
    },
    [
      activePredicateRefReplayApplyConflictSimulationReview,
      setPredicateRefReplayApplyConflictFocusedDecisionState,
      setPredicateRefReplayApplyConflictDraftSource,
    ],
  );
  const resolvePredicateRefReplayApplyConflict = useCallback(
    (
      conflict: PredicateRefReplayApplyConflictEntry,
      resolution: "local" | "remote" | "merged",
      mergedEntry?: PredicateRefReplayApplyHistoryEntry | null,
    ) => {
      if (resolution !== "local") {
        const nextEntry = resolution === "remote" ? conflict.remoteEntry : mergedEntry ?? conflict.localEntry;
        setPredicateRefReplayApplyHistory((current) => {
          const next = mergePredicateRefReplayApplyHistoryEntries(
            current.filter((entry) => entry.id !== conflict.entryId),
            [nextEntry],
          );
          predicateRefReplayApplyHistoryRef.current = next;
          return next;
        });
      }
      setPredicateRefReplayApplyConflictDraftSourcesById((current) => {
        if (!current[conflict.conflictId]) {
          return current;
        }
        const next = { ...current };
        delete next[conflict.conflictId];
        return next;
      });
      setPredicateRefReplayApplyConflicts((current) =>
        current.filter((entry) => entry.conflictId !== conflict.conflictId),
      );
      appendPredicateRefReplayApplySyncAuditEntry({
        at: new Date().toISOString(),
        auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
        detail:
          resolution === "remote"
            ? `${predicateRefReplayApplyHistoryTabIdentity.label} accepted the remote replay history override from ${conflict.sourceTabLabel}.`
            : resolution === "merged"
              ? `${predicateRefReplayApplyHistoryTabIdentity.label} applied a reviewed replay history merge against ${conflict.sourceTabLabel}.`
            : `${predicateRefReplayApplyHistoryTabIdentity.label} kept the local replay history version over ${conflict.sourceTabLabel}.`,
        entryId: conflict.entryId,
        kind: "conflict_resolved",
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        templateId: conflict.templateId,
        templateLabel: conflict.templateLabel,
      });
    },
    [
      appendPredicateRefReplayApplySyncAuditEntry,
      predicateRefReplayApplyHistoryTabIdentity.label,
      predicateRefReplayApplyHistoryTabIdentity.tabId,
    ],
  );
  useEffect(() => {
    setPredicateRefReplayApplyConflictDraftSourcesById((current) => {
      const activeConflictIds = new Set(predicateRefReplayApplyConflicts.map((entry) => entry.conflictId));
      let changed = false;
      const next = Object.fromEntries(
        Object.entries(current).filter(([conflictId]) => {
          const keep = activeConflictIds.has(conflictId);
          if (!keep) {
            changed = true;
          }
          return keep;
        }),
      );
      return changed ? next : current;
    });
  }, [predicateRefReplayApplyConflicts]);
  useEffect(() => {
    if (!predicateRefReplayApplyConflictFocusedDecision) {
      return;
    }
    const stillExists = selectedRefTemplateReplayApplyConflictReviews.some((review) =>
      review.conflict.conflictId === predicateRefReplayApplyConflictFocusedDecision.conflictId
      && [
        ...review.summaryDiffs,
        ...review.rowDiffs,
        ...review.selectionSnapshotDiffs,
        ...review.bindingSnapshotDiffs,
      ].some((item) => item.decisionKey === predicateRefReplayApplyConflictFocusedDecision.decisionKey));
    if (!stillExists) {
      setPredicateRefReplayApplyConflictFocusedDecision(null);
    }
  }, [
    predicateRefReplayApplyConflictFocusedDecision,
    selectedRefTemplateReplayApplyConflictReviews,
  ]);
  useEffect(() => {
    const conflictedEntryIds = new Set(
      predicateRefReplayApplyConflicts.map((entry: PredicateRefReplayApplyConflictEntry) => entry.entryId),
    );
    const persistedEntries = loadRunSurfaceCollectionQueryBuilderReplayApplyHistory();
    const persistedById = new Map<string, PredicateRefReplayApplyHistoryEntry>(
      persistedEntries.map((entry: PredicateRefReplayApplyHistoryEntry) => [entry.id, entry] as const),
    );
    predicateRefReplayApplyHistory.forEach((entry: PredicateRefReplayApplyHistoryEntry) => {
      if (conflictedEntryIds.has(entry.id)) {
        return;
      }
      persistedById.set(entry.id, entry);
    });
    const mergedEntries = Array.from(persistedById.values())
      .sort((left, right) => Date.parse(right.appliedAt) - Date.parse(left.appliedAt))
      .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES);
    const serialized = serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(mergedEntries);
    if (serialized === lastPersistedPredicateRefReplayApplyHistoryRef.current) {
      return;
    }
    persistRunSurfaceCollectionQueryBuilderReplayApplyHistory(mergedEntries);
    lastPersistedPredicateRefReplayApplyHistoryRef.current = serialized;
  }, [predicateRefReplayApplyConflicts, predicateRefReplayApplyHistory]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail(
      predicateRefReplayApplyHistoryTabIdentity.tabId,
      predicateRefReplayApplySyncAuditTrail,
    );
  }, [predicateRefReplayApplyHistoryTabIdentity.tabId, predicateRefReplayApplySyncAuditTrail]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState(
      predicateRefReplayApplyHistoryTabIdentity.tabId,
      {
        auditFilter: predicateRefReplayApplySyncAuditFilter,
        conflictPolicy: predicateRefReplayApplyConflictPolicy,
        syncMode: predicateRefReplayApplySyncMode,
      },
    );
  }, [
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    predicateRefReplayApplySyncAuditFilter,
    predicateRefReplayApplyConflictPolicy,
    predicateRefReplayApplySyncMode,
  ]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts(
      predicateRefReplayApplyHistoryTabIdentity.tabId,
      predicateRefReplayApplyConflicts,
    );
  }, [predicateRefReplayApplyConflicts, predicateRefReplayApplyHistoryTabIdentity.tabId]);
  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    const handleStorage = (event: StorageEvent) => {
      if (event.key !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY) {
        return;
      }
      const remoteEntries = parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue(event.newValue);
      const currentEntries = predicateRefReplayApplyHistoryRef.current;
      const currentEntryById = new Map(
        currentEntries.map((entry: PredicateRefReplayApplyHistoryEntry) => [entry.id, entry] as const),
      );
      const remoteConflicts = remoteEntries.flatMap((remoteEntry: PredicateRefReplayApplyHistoryEntry) => {
        const currentEntry = currentEntryById.get(remoteEntry.id) ?? null;
        if (currentEntry && !arePredicateRefReplayApplyHistoryEntriesEquivalent(currentEntry, remoteEntry)) {
          return [{
            conflictId: buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId(),
            detectedAt: new Date().toISOString(),
            entryId: remoteEntry.id,
            localEntry: currentEntry,
            remoteEntry,
            sourceTabId: remoteEntry.lastRestoredByTabId ?? remoteEntry.sourceTabId ?? "unknown",
            sourceTabLabel: remoteEntry.lastRestoredByTabLabel ?? remoteEntry.sourceTabLabel ?? "Remote tab",
            templateId: remoteEntry.templateId,
            templateLabel: remoteEntry.templateLabel,
          } satisfies PredicateRefReplayApplyConflictEntry];
        }
        return [];
      });
      const conflictingEntryIds = new Set(
        remoteConflicts.map((entry: PredicateRefReplayApplyConflictEntry) => entry.entryId),
      );
      const nonConflictingRemoteEntries = remoteEntries.filter(
        (entry: PredicateRefReplayApplyHistoryEntry) => !conflictingEntryIds.has(entry.id),
      );
      const mergedEntries = mergePredicateRefReplayApplyHistoryEntries(currentEntries, nonConflictingRemoteEntries);
      const currentSerialized = serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(currentEntries);
      const mergedSerialized = serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(mergedEntries);
      const nextAuditEntries = [
        ...nonConflictingRemoteEntries.flatMap((remoteEntry: PredicateRefReplayApplyHistoryEntry) => {
          const currentEntry = currentEntryById.get(remoteEntry.id) ?? null;
          if (!currentEntry) {
            return [{
              at: remoteEntry.appliedAt,
              auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
              detail:
                predicateRefReplayApplySyncModeRef.current === "audit_only"
                  ? `${remoteEntry.sourceTabLabel ?? "Remote tab"} applied ${remoteEntry.approvedCount} replay rows, but this tab is in audit-only mode.`
                  : `${remoteEntry.sourceTabLabel ?? "Remote tab"} applied ${remoteEntry.approvedCount} replay rows.`,
              entryId: remoteEntry.id,
              kind: "remote_apply",
              sourceTabId: remoteEntry.sourceTabId ?? "unknown",
              sourceTabLabel: remoteEntry.sourceTabLabel ?? "Remote tab",
              templateId: remoteEntry.templateId,
              templateLabel: remoteEntry.templateLabel,
            } satisfies PredicateRefReplayApplySyncAuditEntry];
          }
          const currentRestoredAt = currentEntry.lastRestoredAt ? Date.parse(currentEntry.lastRestoredAt) : Number.NEGATIVE_INFINITY;
          const remoteRestoredAt = remoteEntry.lastRestoredAt ? Date.parse(remoteEntry.lastRestoredAt) : Number.NEGATIVE_INFINITY;
          if (remoteRestoredAt > currentRestoredAt && remoteEntry.lastRestoredAt) {
            return [{
              at: remoteEntry.lastRestoredAt,
              auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
              detail:
                predicateRefReplayApplySyncModeRef.current === "audit_only"
                  ? `${remoteEntry.lastRestoredByTabLabel ?? remoteEntry.sourceTabLabel ?? "Remote tab"} restored a replay snapshot, but this tab is in audit-only mode.`
                  : `${remoteEntry.lastRestoredByTabLabel ?? remoteEntry.sourceTabLabel ?? "Remote tab"} restored a replay snapshot.`,
              entryId: remoteEntry.id,
              kind: "remote_restore",
              sourceTabId:
                remoteEntry.lastRestoredByTabId ?? remoteEntry.sourceTabId ?? "unknown",
              sourceTabLabel:
                remoteEntry.lastRestoredByTabLabel ?? remoteEntry.sourceTabLabel ?? "Remote tab",
              templateId: remoteEntry.templateId,
              templateLabel: remoteEntry.templateLabel,
            } satisfies PredicateRefReplayApplySyncAuditEntry];
          }
          return [];
        }),
        ...remoteConflicts.map((conflict: PredicateRefReplayApplyConflictEntry) => ({
          at: conflict.detectedAt,
          auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
          detail:
            predicateRefReplayApplyConflictPolicyRef.current === "prefer_remote"
              ? `${conflict.sourceTabLabel} collided with a local replay override and policy chose remote.`
              : predicateRefReplayApplyConflictPolicyRef.current === "prefer_local"
                ? `${conflict.sourceTabLabel} collided with a local replay override and policy kept local.`
                : `${conflict.sourceTabLabel} collided with a local replay override and is waiting for review.`,
          entryId: conflict.entryId,
          kind: "conflict_detected",
          sourceTabId: conflict.sourceTabId,
          sourceTabLabel: conflict.sourceTabLabel,
          templateId: conflict.templateId,
          templateLabel: conflict.templateLabel,
        } satisfies PredicateRefReplayApplySyncAuditEntry)),
      ];
      if (predicateRefReplayApplySyncModeRef.current === "mute_remote") {
        return;
      }
      if (nextAuditEntries.length) {
        setPredicateRefReplayApplySyncAuditTrail((current) =>
          mergePredicateRefReplayApplySyncAuditEntries(current, nextAuditEntries),
        );
      }
      if (remoteConflicts.length) {
        if (predicateRefReplayApplyConflictPolicyRef.current === "require_review") {
          setPredicateRefReplayApplyConflicts((current) => {
            const nextByEntryId = new Map(
              current.map((entry: PredicateRefReplayApplyConflictEntry) => [entry.entryId, entry] as const),
            );
            remoteConflicts.forEach((conflict: PredicateRefReplayApplyConflictEntry) => {
              nextByEntryId.set(conflict.entryId, conflict);
            });
            return limitPredicateRefReplayApplyConflictEntries(Array.from(nextByEntryId.values()));
          });
        } else if (predicateRefReplayApplyConflictPolicyRef.current === "prefer_remote") {
          setPredicateRefReplayApplyConflicts((current) =>
            current.filter((entry: PredicateRefReplayApplyConflictEntry) =>
              !remoteConflicts.some((conflict: PredicateRefReplayApplyConflictEntry) => conflict.entryId === entry.entryId),
            ),
          );
          const resolvedEntries = mergePredicateRefReplayApplyHistoryEntries(
            mergedEntries,
            remoteConflicts.map((conflict: PredicateRefReplayApplyConflictEntry) => conflict.remoteEntry),
          );
          const resolvedSerialized = serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(resolvedEntries);
          predicateRefReplayApplyHistoryRef.current = resolvedEntries;
          setPredicateRefReplayApplyHistory(resolvedEntries);
          lastPersistedPredicateRefReplayApplyHistoryRef.current = resolvedSerialized;
          return;
        } else {
          setPredicateRefReplayApplyConflicts((current) =>
            current.filter((entry: PredicateRefReplayApplyConflictEntry) =>
              !remoteConflicts.some((conflict: PredicateRefReplayApplyConflictEntry) => conflict.entryId === entry.entryId),
            ),
          );
        }
      }
      if (
        predicateRefReplayApplySyncModeRef.current === "audit_only"
        || mergedSerialized === currentSerialized
      ) {
        return;
      }
      predicateRefReplayApplyHistoryRef.current = mergedEntries;
      setPredicateRefReplayApplyHistory(mergedEntries);
      lastPersistedPredicateRefReplayApplyHistoryRef.current = mergedSerialized;
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);
  useEffect(() => {
    if (predicateRefReplayApplySyncMode !== "live") {
      return;
    }
    const storageEntries = loadRunSurfaceCollectionQueryBuilderReplayApplyHistory();
    setPredicateRefReplayApplyHistory((current) => {
      const currentEntryById = new Map(
        current.map((entry: PredicateRefReplayApplyHistoryEntry) => [entry.id, entry] as const),
      );
      const storageConflicts = storageEntries.flatMap((entry: PredicateRefReplayApplyHistoryEntry) => {
        const currentEntry = currentEntryById.get(entry.id) ?? null;
        if (!currentEntry || arePredicateRefReplayApplyHistoryEntriesEquivalent(currentEntry, entry)) {
          return [];
        }
        return [{
          conflictId: buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId(),
          detectedAt: new Date().toISOString(),
          entryId: entry.id,
          localEntry: currentEntry,
          remoteEntry: entry,
          sourceTabId: entry.lastRestoredByTabId ?? entry.sourceTabId ?? "unknown",
          sourceTabLabel: entry.lastRestoredByTabLabel ?? entry.sourceTabLabel ?? "Remote tab",
          templateId: entry.templateId,
          templateLabel: entry.templateLabel,
        } satisfies PredicateRefReplayApplyConflictEntry];
      });
      if (storageConflicts.length && predicateRefReplayApplyConflictPolicyRef.current === "require_review") {
        setPredicateRefReplayApplyConflicts((currentConflicts) => {
          const nextByEntryId = new Map(
            currentConflicts.map((entry: PredicateRefReplayApplyConflictEntry) => [entry.entryId, entry] as const),
          );
          storageConflicts.forEach((conflict: PredicateRefReplayApplyConflictEntry) => {
            nextByEntryId.set(conflict.entryId, conflict);
          });
          return limitPredicateRefReplayApplyConflictEntries(Array.from(nextByEntryId.values()));
        });
      }
      const nonConflictingStorageEntries = storageEntries.filter((entry: PredicateRefReplayApplyHistoryEntry) =>
        !storageConflicts.some((conflict: PredicateRefReplayApplyConflictEntry) => conflict.entryId === entry.id),
      );
      const mergedEntries = mergePredicateRefReplayApplyHistoryEntries(current, nonConflictingStorageEntries);
      const resolvedEntries =
        storageConflicts.length && predicateRefReplayApplyConflictPolicyRef.current === "prefer_remote"
          ? mergePredicateRefReplayApplyHistoryEntries(
              mergedEntries,
              storageConflicts.map((conflict: PredicateRefReplayApplyConflictEntry) => conflict.remoteEntry),
            )
          : mergedEntries;
      predicateRefReplayApplyHistoryRef.current = resolvedEntries;
      return serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(resolvedEntries)
        === serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(current)
        ? current
        : resolvedEntries;
    });
  }, [predicateRefReplayApplySyncMode]);
  useEffect(() => {
    if (
      predicateRefReplayApplyConflictPolicy === "require_review"
      || !predicateRefReplayApplyConflicts.length
    ) {
      return;
    }
    const nextConflicts = [...predicateRefReplayApplyConflicts];
    setPredicateRefReplayApplyConflicts([]);
    if (predicateRefReplayApplyConflictPolicy === "prefer_remote") {
      setPredicateRefReplayApplyHistory((current) => {
        const resolvedEntries = mergePredicateRefReplayApplyHistoryEntries(
          current.filter((entry) => !nextConflicts.some((conflict) => conflict.entryId === entry.id)),
          nextConflicts.map((conflict) => conflict.remoteEntry),
        );
        predicateRefReplayApplyHistoryRef.current = resolvedEntries;
        return resolvedEntries;
      });
    }
    setPredicateRefReplayApplySyncAuditTrail((current) =>
      mergePredicateRefReplayApplySyncAuditEntries(
        current,
        nextConflicts.map((conflict) => ({
          at: new Date().toISOString(),
          auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
          detail:
            predicateRefReplayApplyConflictPolicy === "prefer_remote"
              ? `${predicateRefReplayApplyHistoryTabIdentity.label} auto-resolved a pending collision in favor of remote.`
              : `${predicateRefReplayApplyHistoryTabIdentity.label} auto-resolved a pending collision in favor of local.`,
          entryId: conflict.entryId,
          kind: "conflict_resolved",
          sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
          sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
          templateId: conflict.templateId,
          templateLabel: conflict.templateLabel,
        })),
      ),
    );
  }, [
    predicateRefReplayApplyConflictPolicy,
    predicateRefReplayApplyConflicts,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
  ]);
  const simulatedCoordinationGroups = useMemo<ReturnType<typeof groupRunSurfaceCollectionQueryBuilderTemplateParameters>>(
    () => selectedRefTemplateParameterGroups.filter((group) => group.presetBundles.length),
    [selectedRefTemplateParameterGroups],
  );
  useEffect(() => {
    if (!simulatedCoordinationGroups.length) {
      setBundleCoordinationSimulationScope("all");
      setBundleCoordinationSimulationPolicy("current");
      return;
    }
    if (
      bundleCoordinationSimulationScope !== "all"
      && !simulatedCoordinationGroups.some((group) => group.key === bundleCoordinationSimulationScope)
    ) {
      setBundleCoordinationSimulationScope("all");
    }
  }, [
    bundleCoordinationSimulationScope,
    simulatedCoordinationGroups,
  ]);
  useEffect(() => {
    setBundleCoordinationSimulationReplayIndex(0);
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    predicateRefDraftBindings,
    predicateRefGroupBundleSelections,
    predicateRefGroupAutoBundleSelections,
    selectedRefTemplate?.id,
  ]);
  useEffect(() => {
    setBundleCoordinationSimulationReplayActionTypeFilter("all");
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    selectedRefTemplate?.id,
  ]);
  useEffect(() => {
    setBundleCoordinationSimulationReplayEdgeFilter("all");
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    selectedRefTemplate?.id,
  ]);
  useEffect(() => {
    if (!simulatedCoordinationGroups.length) {
      setBundleCoordinationSimulationReplayGroupFilter("all");
      return;
    }
    if (
      bundleCoordinationSimulationReplayGroupFilter !== "all"
      && !simulatedCoordinationGroups.some((group) => group.key === bundleCoordinationSimulationReplayGroupFilter)
    ) {
      setBundleCoordinationSimulationReplayGroupFilter("all");
    }
  }, [
    bundleCoordinationSimulationReplayGroupFilter,
    simulatedCoordinationGroups,
  ]);
  const getSortedTemplateGroupPresetBundles = useCallback(
    (bundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[]) =>
      sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles(bundles),
    [],
  );
  const activePredicateRefReplayApplyConflictSimulationBundleOverrides = useMemo(() => {
    if (!selectedRefTemplate || !activePredicateRefReplayApplyConflictSimulationReview) {
      return {
        bindingOverridesByParameterKey: {} as Record<string, string | null>,
        groupLabelsByKey: {} as Record<string, string>,
        selectionOverridesBySelectionKey: {} as Record<string, string | null>,
      };
    }
    const selectionOverridesBySelectionKey: Record<string, string | null> = {};
    const bindingOverridesByParameterKey: Record<string, string | null> = {};
    const groupLabelsByKey: Record<string, string> = {};
    activePredicateRefReplayApplyConflictSimulationReview.mergedEntry.rows.forEach((row) => {
      const group = selectedRefTemplateParameterGroups.find((candidate) => candidate.key === row.groupKey) ?? null;
      if (!group) {
        return;
      }
      groupLabelsByKey[group.key] = group.label;
      selectionOverridesBySelectionKey[`${selectedRefTemplate.id}:${group.key}`] = row.promotedBundleKey;
      group.parameters.forEach((parameter) => {
        bindingOverridesByParameterKey[parameter.key] = null;
      });
      const bundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find(
          (candidate) => candidate.key === row.promotedBundleKey,
        ) ?? null;
      if (!bundle) {
        return;
      }
      group.parameters.forEach((parameter) => {
        const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim();
        if (bindingPreset) {
          bindingOverridesByParameterKey[parameter.key] =
            toRunSurfaceCollectionQueryBindingReferenceValue(bindingPreset);
          return;
        }
        const parameterValue = bundle.parameterValues[parameter.key];
        if (parameterValue?.trim()) {
          bindingOverridesByParameterKey[parameter.key] = parameterValue;
        }
      });
    });
    return {
      bindingOverridesByParameterKey,
      groupLabelsByKey,
      selectionOverridesBySelectionKey,
    };
  }, [
    activePredicateRefReplayApplyConflictSimulationReview,
    getSortedTemplateGroupPresetBundles,
    selectedRefTemplate,
    selectedRefTemplateParameterGroups,
  ]);
  const activePredicateRefReplayApplyConflictSimulationGroupKeys = useMemo(
    () => Object.keys(activePredicateRefReplayApplyConflictSimulationBundleOverrides.groupLabelsByKey),
    [activePredicateRefReplayApplyConflictSimulationBundleOverrides.groupLabelsByKey],
  );
  const activePredicateRefReplayApplyConflictSimulationDiffItems = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationReview
        ? [
            ...activePredicateRefReplayApplyConflictSimulationReview.summaryDiffs,
            ...activePredicateRefReplayApplyConflictSimulationReview.rowDiffs,
            ...activePredicateRefReplayApplyConflictSimulationReview.selectionSnapshotDiffs,
            ...activePredicateRefReplayApplyConflictSimulationReview.bindingSnapshotDiffs,
          ]
        : []
    ),
    [activePredicateRefReplayApplyConflictSimulationReview],
  );
  const activePredicateRefReplayApplyConflictSimulationDiffItemByDecisionKey = useMemo(
    () => Object.fromEntries(
      activePredicateRefReplayApplyConflictSimulationDiffItems.map((item) => [item.decisionKey, item] as const),
    ),
    [activePredicateRefReplayApplyConflictSimulationDiffItems],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedItem = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationReview
      && predicateRefReplayApplyConflictFocusedDecision?.conflictId
        === activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId
        ? (
            activePredicateRefReplayApplyConflictSimulationDiffItemByDecisionKey[
              predicateRefReplayApplyConflictFocusedDecision.decisionKey
            ] ?? null
          )
        : null
    ),
    [
      activePredicateRefReplayApplyConflictSimulationDiffItemByDecisionKey,
      activePredicateRefReplayApplyConflictSimulationReview,
      predicateRefReplayApplyConflictFocusedDecision,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFieldPicks = useMemo(() => {
    if (!activePredicateRefReplayApplyConflictSimulationReview) {
      return {
        byGroupKey: {} as Record<string, Array<{
          decisionKey: string;
          key: string;
          label: string;
          section: PredicateRefReplayApplyConflictDiffItem["section"];
          source: "local" | "remote";
        }>>,
        global: [] as Array<{
          decisionKey: string;
          key: string;
          label: string;
          section: PredicateRefReplayApplyConflictDiffItem["section"];
          source: "local" | "remote";
        }>,
      };
    }
    const parameterGroupKeyByParameterKey = Object.fromEntries(
      selectedRefTemplateParameterGroups.flatMap((group) =>
        group.parameters.map((parameter) => [parameter.key, group.key] as const)),
    );
    const allItems = [
      ...activePredicateRefReplayApplyConflictSimulationReview.summaryDiffs,
      ...activePredicateRefReplayApplyConflictSimulationReview.rowDiffs,
      ...activePredicateRefReplayApplyConflictSimulationReview.selectionSnapshotDiffs,
      ...activePredicateRefReplayApplyConflictSimulationReview.bindingSnapshotDiffs,
    ].filter((item) => item.editable);
    const byGroupKey: Record<string, Array<{
      decisionKey: string;
      key: string;
      label: string;
      section: PredicateRefReplayApplyConflictDiffItem["section"];
      source: "local" | "remote";
    }>> = {};
    const global: Array<{
      decisionKey: string;
      key: string;
      label: string;
      section: PredicateRefReplayApplyConflictDiffItem["section"];
      source: "local" | "remote";
    }> = [];
    allItems.forEach((item) => {
      const source = activePredicateRefReplayApplyConflictSimulationReview.selectedSources[item.decisionKey] ?? "local";
      const relatedGroupKey = item.relatedGroupKey ?? parameterGroupKeyByParameterKey[item.key] ?? null;
      const annotation = {
        decisionKey: item.decisionKey,
        key: item.key,
        label: item.label,
        section: item.section,
        source,
      };
      if (relatedGroupKey) {
        byGroupKey[relatedGroupKey] = [...(byGroupKey[relatedGroupKey] ?? []), annotation];
        return;
      }
      global.push(annotation);
    });
    return {
      byGroupKey,
      global,
    };
  }, [
    activePredicateRefReplayApplyConflictSimulationReview,
    selectedRefTemplateParameterGroups,
  ]);
  const activePredicateRefReplayApplyConflictSimulationFocusedGroupKey = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationFocusedItem?.relatedGroupKey
      && simulatedCoordinationGroups.some(
        (group) => group.key === activePredicateRefReplayApplyConflictSimulationFocusedItem.relatedGroupKey,
      )
        ? activePredicateRefReplayApplyConflictSimulationFocusedItem.relatedGroupKey
        : null
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedItem,
      simulatedCoordinationGroups,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
      ?? clauseReevaluationPreviewSelection.groupKey
      ?? (
        bundleCoordinationSimulationReplayGroupFilter !== "all"
          ? bundleCoordinationSimulationReplayGroupFilter
          : null
      )
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
      bundleCoordinationSimulationReplayGroupFilter,
      clauseReevaluationPreviewSelection.groupKey,
    ],
  );
  const doesTemplateGroupMatchVisibilityRule = useCallback(
    (
      group: {
        visibilityRule: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["visibilityRule"];
        coordinationPolicy: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"];
        parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
      },
      bindings: Record<string, string>,
    ) => {
      if (group.visibilityRule === "always") {
        return true;
      }
      if (group.visibilityRule === "manual") {
        return false;
      }
      if (group.visibilityRule === "binding_active") {
        return group.parameters.some((parameter) => {
          const currentValue = bindings[parameter.key]?.trim() ?? "";
          return Boolean(fromRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
            || Boolean(parameter.bindingPreset.trim());
        });
      }
      return group.parameters.some((parameter) => {
        const currentValue = bindings[parameter.key]?.trim() ?? "";
        return Boolean(currentValue && !isRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
          || Boolean(parameter.defaultValue.trim());
      });
    },
    [],
  );
  const doesTemplateGroupBundleMatchAutoSelectRule = useCallback(
    (
      group: {
        parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
      },
      bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
      bindings: Record<string, string>,
    ) => {
      if (bundle.autoSelectRule === "manual") {
        return false;
      }
      if (bundle.autoSelectRule === "always") {
        return true;
      }
      if (bundle.autoSelectRule === "binding_active") {
        return group.parameters.some((parameter) => {
          const currentValue = bindings[parameter.key]?.trim() ?? "";
          return Boolean(fromRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
            || Boolean(parameter.bindingPreset.trim())
            || Boolean(bundle.parameterBindingPresets[parameter.key]?.trim());
        });
      }
      return group.parameters.some((parameter) => {
        const currentValue = bindings[parameter.key]?.trim() ?? "";
        return Boolean(currentValue && !isRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
          || Boolean(parameter.defaultValue.trim())
          || Boolean(bundle.parameterValues[parameter.key]?.trim());
      });
    },
    [],
  );
  const isTemplateGroupExpanded = useCallback(
    (viewKey: string, collapsedByDefault: boolean) => (
      templateGroupExpansionByKey[viewKey] ?? !collapsedByDefault
    ),
    [templateGroupExpansionByKey],
  );
  const toggleTemplateGroupExpanded = useCallback((viewKey: string, collapsedByDefault: boolean) => {
    setTemplateGroupExpansionByKey((current) => ({
      ...current,
      [viewKey]: !(current[viewKey] ?? !collapsedByDefault),
    }));
  }, []);
  const applyPredicateRefGroupPresetBundle = useCallback(
    (
      templateId: string,
      group: {
        key: string;
        parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
      },
      bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState | null,
    ) => {
      const selectionKey = `${templateId}:${group.key}`;
      setPredicateRefGroupBundleSelections((current) => ({
        ...current,
        [selectionKey]: bundle?.key ?? "",
      }));
      setPredicateRefDraftBindings((current) => {
        const next = { ...current };
        group.parameters.forEach((parameter) => {
          delete next[parameter.key];
        });
        if (!bundle) {
          return next;
        }
        group.parameters.forEach((parameter) => {
          const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim();
          if (bindingPreset) {
            next[parameter.key] = toRunSurfaceCollectionQueryBindingReferenceValue(bindingPreset);
            return;
          }
          const parameterValue = bundle.parameterValues[parameter.key];
          if (parameterValue?.trim()) {
            next[parameter.key] = parameterValue;
          }
        });
        return next;
      });
    },
    [],
  );
  const applyPredicateRefGroupPresetBundles = useCallback(
    (
      templateId: string,
      selections: Array<{
        group: {
          key: string;
          parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
        };
        bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState | null;
      }>,
    ) => {
      if (!selections.length) {
        return;
      }
      setPredicateRefGroupBundleSelections((current) => {
        const next = { ...current };
        selections.forEach(({ group, bundle }) => {
          next[`${templateId}:${group.key}`] = bundle?.key ?? "";
        });
        return next;
      });
      setPredicateRefDraftBindings((current) => {
        const next = { ...current };
        selections.forEach(({ group, bundle }) => {
          group.parameters.forEach((parameter) => {
            delete next[parameter.key];
          });
          if (!bundle) {
            return;
          }
          group.parameters.forEach((parameter) => {
            const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim();
            if (bindingPreset) {
              next[parameter.key] = toRunSurfaceCollectionQueryBindingReferenceValue(bindingPreset);
              return;
            }
            const parameterValue = bundle.parameterValues[parameter.key];
            if (parameterValue?.trim()) {
              next[parameter.key] = parameterValue;
            }
          });
        });
        return next;
      });
    },
    [],
  );
  const restorePredicateRefReplayApplyHistoryEntry = useCallback(
    (entry: PredicateRefReplayApplyHistoryEntry) => {
      setPredicateRefGroupBundleSelections((current) => {
        const next = { ...current };
        Object.entries(entry.rollbackSnapshot.groupSelectionsBySelectionKey).forEach(([selectionKey, bundleKey]) => {
          if (bundleKey?.trim()) {
            next[selectionKey] = bundleKey;
            return;
          }
          delete next[selectionKey];
        });
        return next;
      });
      setPredicateRefDraftBindings((current) => {
        const next = { ...current };
        Object.entries(entry.rollbackSnapshot.draftBindingsByParameterKey).forEach(([parameterKey, value]) => {
          if (value?.trim()) {
            next[parameterKey] = value;
            return;
          }
          delete next[parameterKey];
        });
        return next;
      });
      setPredicateRefReplayApplyHistory((current) =>
        current.map((item) =>
          item.id === entry.id
            ? {
                ...item,
                lastRestoredAt: new Date().toISOString(),
                lastRestoredByTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
                lastRestoredByTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
              }
            : item,
        ),
      );
      appendPredicateRefReplayApplySyncAuditEntry({
        at: new Date().toISOString(),
        auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
        detail: `${predicateRefReplayApplyHistoryTabIdentity.label} restored the replay snapshot for ${entry.templateLabel}.`,
        entryId: entry.id,
        kind: "local_restore",
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        templateId: entry.templateId,
        templateLabel: entry.templateLabel,
      });
    },
    [
      appendPredicateRefReplayApplySyncAuditEntry,
      predicateRefReplayApplyHistoryTabIdentity.label,
      predicateRefReplayApplyHistoryTabIdentity.tabId,
    ],
  );
  const computeCoordinatedPredicateRefGroupBundleState = useCallback((
    overrides: {
      draftBindingOverridesByParameterKey?: Record<string, string | null>;
      manualSelectionOverridesBySelectionKey?: Record<string, string | null>;
      policyOverridesByGroupKey?: Record<
        string,
        RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"]
      >;
    } = {},
  ) => {
    const policyOverridesByGroupKey = overrides.policyOverridesByGroupKey ?? {};
    type AggregatedDependencyRequest = {
      bundleKey: string;
      bundleLabel: string;
      targetPriority: number;
      hasManualSource: boolean;
      maxSourcePriority: number;
      sourceLabels: string[];
    };
    type PolicyTraceStep = {
      key: string;
      title: string;
      detail: string;
      tone: "info" | "success" | "warning" | "muted";
    };
    type PolicyTrace = {
      summary: string;
      statusLabel: string;
      tone: PolicyTraceStep["tone"];
      steps: PolicyTraceStep[];
    };
    type GlobalPolicyTrace = PolicyTrace & {
      counts: {
        groupCount: number;
        manualCount: number;
        autoCount: number;
        blockedCount: number;
        conflictCount: number;
        dependencyRequestCount: number;
        unmetDependencyCount: number;
      };
    };
    type SolverReplayAction = {
      dependencyEdges: Array<{
        key: string;
        label: string;
        sourceGroupKey: string;
        sourceGroupLabel: string;
        sourceBundleKey: string;
        sourceBundleLabel: string;
        targetGroupKey: string;
        targetGroupLabel: string;
        targetBundleKey: string;
        targetBundleLabel: string;
      }>;
      groupKey: string;
      groupLabel: string;
      type: "manual_anchor" | "dependency_selection" | "direct_auto_selection" | "conflict_blocked" | "idle";
      detail: string;
    };
    type SolverReplayStep = {
      key: string;
      title: string;
      summary: string;
      actions: SolverReplayAction[];
      resolvedSelectionsByGroupKey: Record<string, string>;
      autoSelectionsByGroupKey: Record<string, string>;
    };
    if (!selectedRefTemplate) {
      return {
        autoSelectionsBySelectionKey: {} as Record<string, string>,
        resolvedSelectionsByGroupKey: {} as Record<string, string>,
        dependencyRequestsByGroupKey: {} as Record<string, Array<{
          bundleKey: string;
          sourceGroupKey: string;
          sourceGroupLabel: string;
          sourceBundleKey: string;
          sourceBundleLabel: string;
          sourcePriority: number;
          manualSource: boolean;
        }>>,
        unmetDependenciesByGroupKey: {} as Record<string, Array<{
          key: string;
          groupKey: string;
          groupLabel: string;
          bundleKey: string;
          bundleLabel: string;
        }>>,
        conflictRequestsByGroupKey: {} as Record<string, Array<{
          bundleKey: string;
          bundleLabel: string;
          targetPriority: number;
          hasManualSource: boolean;
          maxSourcePriority: number;
          sourceLabels: string[];
        }>>,
        policyTraceByGroupKey: {} as Record<string, PolicyTrace>,
        globalPolicyTrace: {
          summary: "No predicate template is selected.",
          statusLabel: "Idle",
          tone: "muted" as const,
          steps: [],
          counts: {
            groupCount: 0,
            manualCount: 0,
            autoCount: 0,
            blockedCount: 0,
            conflictCount: 0,
            dependencyRequestCount: 0,
            unmetDependencyCount: 0,
          },
        } as GlobalPolicyTrace,
        solverReplay: [] as SolverReplayStep[],
      };
    }
    type DependencyRequest = {
      bundleKey: string;
      bundleLabel: string;
      targetPriority: number;
      sourceGroupKey: string;
      sourceGroupLabel: string;
      sourceBundleKey: string;
      sourceBundleLabel: string;
      sourcePriority: number;
      manualSource: boolean;
    };
    const groupMap = new Map(
      selectedRefTemplateParameterGroups.map((group) => [group.key, group] as const),
    );
    const effectiveDraftBindings = { ...predicateRefDraftBindings };
    Object.entries(overrides.draftBindingOverridesByParameterKey ?? {}).forEach(([parameterKey, value]) => {
      if (value?.trim()) {
        effectiveDraftBindings[parameterKey] = value;
        return;
      }
      delete effectiveDraftBindings[parameterKey];
    });
    const effectiveManualSelectionsBySelectionKey = { ...predicateRefGroupBundleSelections };
    Object.entries(overrides.manualSelectionOverridesBySelectionKey ?? {}).forEach(([selectionKey, bundleKey]) => {
      if (bundleKey?.trim()) {
        effectiveManualSelectionsBySelectionKey[selectionKey] = bundleKey;
        return;
      }
      delete effectiveManualSelectionsBySelectionKey[selectionKey];
    });
    const getGroupBundle = (
      groupKey: string,
      bundleKey: string,
    ) =>
      getSortedTemplateGroupPresetBundles(groupMap.get(groupKey)?.presetBundles ?? []).find(
        (bundle) => bundle.key === bundleKey,
      ) ?? null;
    const getCoordinationPolicy = (
      group: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
    ) => policyOverridesByGroupKey[group.key] ?? group.coordinationPolicy;
    const buildDependencyEdges = (
      requests: DependencyRequest[],
      targetGroupKey: string,
    ) => Object.values(
      requests.reduce<Record<string, SolverReplayAction["dependencyEdges"][number]>>((accumulator, request) => {
        const targetGroup = groupMap.get(targetGroupKey);
        const edgeKey = `${request.sourceGroupKey}:${request.sourceBundleKey}->${targetGroupKey}:${request.bundleKey}`;
        if (accumulator[edgeKey]) {
          return accumulator;
        }
        accumulator[edgeKey] = {
          key: edgeKey,
          label: `${request.sourceGroupLabel} → ${request.sourceBundleLabel} => ${targetGroup?.label ?? targetGroupKey} → ${request.bundleLabel}`,
          sourceGroupKey: request.sourceGroupKey,
          sourceGroupLabel: request.sourceGroupLabel,
          sourceBundleKey: request.sourceBundleKey,
          sourceBundleLabel: request.sourceBundleLabel,
          targetGroupKey,
          targetGroupLabel: targetGroup?.label ?? targetGroupKey,
          targetBundleKey: request.bundleKey,
          targetBundleLabel: request.bundleLabel,
        };
        return accumulator;
      }, {}),
    );
    const buildDependencyRequests = (
      resolvedSelectionsByGroupKey: Record<string, string>,
      includePredictedAutoCandidates = false,
    ) => {
      const requestsByGroupKey: Record<string, DependencyRequest[]> = {};
      const appendRequestsFromBundle = (
        sourceGroupKey: string,
        sourceBundleKey: string,
        manualSource: boolean,
      ) => {
        const sourceGroup = groupMap.get(sourceGroupKey);
        const sourceBundle = getGroupBundle(sourceGroupKey, sourceBundleKey);
        if (!sourceGroup || !sourceBundle) {
          return;
        }
        sourceBundle.dependencies.forEach((dependency) => {
          const targetBundle = getGroupBundle(dependency.groupKey, dependency.bundleKey);
          if (!targetBundle) {
            return;
          }
          requestsByGroupKey[dependency.groupKey] = [
            ...(requestsByGroupKey[dependency.groupKey] ?? []),
            {
              bundleKey: dependency.bundleKey,
              bundleLabel: targetBundle.label,
              targetPriority: targetBundle.priority,
              sourceGroupKey,
              sourceGroupLabel: sourceGroup.label,
              sourceBundleKey,
              sourceBundleLabel: sourceBundle.label,
              sourcePriority: sourceBundle.priority,
              manualSource,
            },
          ];
        });
      };
      Object.entries(resolvedSelectionsByGroupKey).forEach(([sourceGroupKey, sourceBundleKey]) => {
        appendRequestsFromBundle(
          sourceGroupKey,
          sourceBundleKey,
          Boolean(effectiveManualSelectionsBySelectionKey[`${selectedRefTemplate.id}:${sourceGroupKey}`]),
        );
      });
      if (includePredictedAutoCandidates) {
        selectedRefTemplateParameterGroups.forEach((group) => {
          if (resolvedSelectionsByGroupKey[group.key]) {
            return;
          }
          const predictedAutoBundle = getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) =>
            doesTemplateGroupBundleMatchAutoSelectRule(group, bundle, effectiveDraftBindings),
          );
          if (!predictedAutoBundle) {
            return;
          }
          appendRequestsFromBundle(group.key, predictedAutoBundle.key, false);
        });
      }
      return requestsByGroupKey;
    };
    const aggregateDependencyRequests = (requests: DependencyRequest[]) =>
      Object.values(
        requests.reduce<Record<string, AggregatedDependencyRequest>>((accumulator, request) => {
          const existing = accumulator[request.bundleKey];
          const sourceLabel = `${request.sourceGroupLabel} → ${request.sourceBundleLabel}`;
          if (existing) {
            existing.hasManualSource = existing.hasManualSource || request.manualSource;
            existing.maxSourcePriority = Math.max(existing.maxSourcePriority, request.sourcePriority);
            if (!existing.sourceLabels.includes(sourceLabel)) {
              existing.sourceLabels.push(sourceLabel);
            }
            return accumulator;
          }
          accumulator[request.bundleKey] = {
            bundleKey: request.bundleKey,
            bundleLabel: request.bundleLabel,
            targetPriority: request.targetPriority,
            hasManualSource: request.manualSource,
            maxSourcePriority: request.sourcePriority,
            sourceLabels: [sourceLabel],
          };
          return accumulator;
        }, {}),
      );
    const sortAggregatedDependencyRequests = (
      summaries: AggregatedDependencyRequest[],
      policy: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"],
      stickyBundleKey: string,
    ) => [...summaries].sort((left, right) => {
      if (policy === "sticky_auto_selection") {
        if (left.bundleKey === stickyBundleKey || right.bundleKey === stickyBundleKey) {
          return Number(right.bundleKey === stickyBundleKey) - Number(left.bundleKey === stickyBundleKey);
        }
      }
      if (policy === "manual_source_priority") {
        if (Number(right.hasManualSource) !== Number(left.hasManualSource)) {
          return Number(right.hasManualSource) - Number(left.hasManualSource);
        }
      }
      if (right.maxSourcePriority !== left.maxSourcePriority) {
        return right.maxSourcePriority - left.maxSourcePriority;
      }
      if (right.targetPriority !== left.targetPriority) {
        return right.targetPriority - left.targetPriority;
      }
      return left.bundleLabel.localeCompare(right.bundleLabel);
    });
    const manualSelectionsByGroupKey = Object.fromEntries(
      selectedRefTemplateParameterGroups.flatMap((group) => {
        const selectionKey = `${selectedRefTemplate.id}:${group.key}`;
        const manualBundleKey = effectiveManualSelectionsBySelectionKey[selectionKey] ?? "";
        return getGroupBundle(group.key, manualBundleKey)
          ? [[group.key, manualBundleKey]]
          : [];
      }),
    );
    const resolvedSelectionsByGroupKey = { ...manualSelectionsByGroupKey };
    const autoSelectionsByGroupKey: Record<string, string> = {};
    const solverReplay: SolverReplayStep[] = [{
      key: "seed",
      title: "Manual seed",
      summary: Object.keys(manualSelectionsByGroupKey).length
        ? `Seeded the solver with ${Object.keys(manualSelectionsByGroupKey).length} manual bundle selection${Object.keys(manualSelectionsByGroupKey).length === 1 ? "" : "s"}.`
        : "No manual bundle anchors were present when the solver started.",
      actions: selectedRefTemplateParameterGroups.flatMap((group) => {
        const manualBundleKey = manualSelectionsByGroupKey[group.key];
        const manualBundle = manualBundleKey ? getGroupBundle(group.key, manualBundleKey) : null;
        return manualBundle
          ? [{
              dependencyEdges: [],
              groupKey: group.key,
              groupLabel: group.label,
              type: "manual_anchor" as const,
              detail: `${manualBundle.label} is pinned manually before coordination begins.`,
            }]
          : [];
      }),
      resolvedSelectionsByGroupKey: { ...resolvedSelectionsByGroupKey },
      autoSelectionsByGroupKey: {},
    }];
    let iterationIndex = 0;
    let changed = true;
    while (changed) {
      changed = false;
      const dependencyRequestsByGroupKey = buildDependencyRequests(resolvedSelectionsByGroupKey, true);
      const iterationActions: SolverReplayAction[] = [];
      selectedRefTemplateParameterGroups.forEach((group) => {
        if (resolvedSelectionsByGroupKey[group.key]) {
          return;
        }
        const coordinationPolicy = getCoordinationPolicy(group);
        const dependencyRequests = dependencyRequestsByGroupKey[group.key] ?? [];
        const aggregatedDependencyRequests = aggregateDependencyRequests(dependencyRequests);
        const stickyBundleKey = predicateRefGroupAutoBundleSelections[`${selectedRefTemplate.id}:${group.key}`] ?? "";
        const sortedDependencyRequests = sortAggregatedDependencyRequests(
          aggregatedDependencyRequests,
          coordinationPolicy,
          stickyBundleKey,
        );
        if (sortedDependencyRequests.length > 1 && coordinationPolicy === "manual_resolution") {
          iterationActions.push({
            dependencyEdges: buildDependencyEdges(dependencyRequests, group.key),
            groupKey: group.key,
            groupLabel: group.label,
            type: "conflict_blocked",
            detail: `${sortedDependencyRequests.map((request) => request.bundleLabel).join(", ")} conflict under manual resolution, so this group stays unresolved.`,
          });
          return;
        }
        const dependencyDrivenBundle = sortedDependencyRequests[0] ?? null;
        if (dependencyDrivenBundle) {
          resolvedSelectionsByGroupKey[group.key] = dependencyDrivenBundle.bundleKey;
          autoSelectionsByGroupKey[group.key] = dependencyDrivenBundle.bundleKey;
          iterationActions.push({
            dependencyEdges: buildDependencyEdges(
              dependencyRequests.filter((request) => request.bundleKey === dependencyDrivenBundle.bundleKey),
              group.key,
            ),
            groupKey: group.key,
            groupLabel: group.label,
            type: "dependency_selection",
            detail: `${dependencyDrivenBundle.bundleLabel} won from ${dependencyDrivenBundle.sourceLabels.join(", ")} under ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(coordinationPolicy)}.`,
          });
          changed = true;
          return;
        }
        const directAutoBundle = getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) =>
          doesTemplateGroupBundleMatchAutoSelectRule(group, bundle, effectiveDraftBindings)
          && bundle.dependencies.every((dependency) =>
            resolvedSelectionsByGroupKey[dependency.groupKey] === dependency.bundleKey,
          ),
        );
        if (directAutoBundle) {
          resolvedSelectionsByGroupKey[group.key] = directAutoBundle.key;
          autoSelectionsByGroupKey[group.key] = directAutoBundle.key;
          const directAutoDependencyEdges = directAutoBundle.dependencies.flatMap((dependency) => {
            const sourceBundleKey = resolvedSelectionsByGroupKey[dependency.groupKey];
            const sourceGroup = groupMap.get(dependency.groupKey);
            const sourceBundle = getGroupBundle(dependency.groupKey, sourceBundleKey);
            if (!sourceGroup || !sourceBundle) {
              return [];
            }
            return [{
              key: `${dependency.groupKey}:${sourceBundleKey}->${group.key}:${directAutoBundle.key}`,
              label: `${sourceGroup.label} → ${sourceBundle.label} => ${group.label} → ${directAutoBundle.label}`,
              sourceGroupKey: dependency.groupKey,
              sourceGroupLabel: sourceGroup.label,
              sourceBundleKey,
              sourceBundleLabel: sourceBundle.label,
              targetGroupKey: group.key,
              targetGroupLabel: group.label,
              targetBundleKey: directAutoBundle.key,
              targetBundleLabel: directAutoBundle.label,
            }];
          });
          iterationActions.push({
            dependencyEdges: directAutoDependencyEdges,
            groupKey: group.key,
            groupLabel: group.label,
            type: "direct_auto_selection",
            detail: `${directAutoBundle.label} matched ${directAutoBundle.autoSelectRule.replaceAll("_", " ")} and all dependencies were already satisfied.`,
          });
          changed = true;
          return;
        }
        if (dependencyRequestsByGroupKey[group.key]?.length || aggregatedDependencyRequests.length) {
          return;
        }
        iterationActions.push({
          dependencyEdges: [],
          groupKey: group.key,
          groupLabel: group.label,
          type: "idle",
          detail: "No dependency request or valid auto-select candidate changed this group in this pass.",
        });
      });
      solverReplay.push({
        key: `iteration:${iterationIndex}`,
        title: `Iteration ${iterationIndex + 1}`,
        summary: iterationActions.length
          ? `${iterationActions.filter((action) => action.type !== "idle").length || iterationActions.length} coordination event${(iterationActions.filter((action) => action.type !== "idle").length || iterationActions.length) === 1 ? "" : "s"} recorded in this pass.`
          : "No further changes were produced in this pass.",
        actions: iterationActions,
        resolvedSelectionsByGroupKey: { ...resolvedSelectionsByGroupKey },
        autoSelectionsByGroupKey: { ...autoSelectionsByGroupKey },
      });
      iterationIndex += 1;
    }
    const dependencyRequestsByGroupKey = buildDependencyRequests(resolvedSelectionsByGroupKey);
    const conflictRequestsByGroupKey = Object.fromEntries(
      selectedRefTemplateParameterGroups.flatMap((group) => {
        const coordinationPolicy = getCoordinationPolicy(group);
        const aggregatedDependencyRequests = aggregateDependencyRequests(
          dependencyRequestsByGroupKey[group.key] ?? [],
        );
        return aggregatedDependencyRequests.length > 1
          ? [[group.key, sortAggregatedDependencyRequests(
              aggregatedDependencyRequests,
              coordinationPolicy,
              predicateRefGroupAutoBundleSelections[`${selectedRefTemplate.id}:${group.key}`] ?? "",
            )]]
          : [];
      }),
    );
    const unmetDependenciesByGroupKey = Object.fromEntries(
      Object.entries(resolvedSelectionsByGroupKey).flatMap(([groupKey, bundleKey]) => {
        const bundle = getGroupBundle(groupKey, bundleKey);
        if (!bundle) {
          return [];
        }
        const unmetDependencies = bundle.dependencies.flatMap((dependency) => {
          if (resolvedSelectionsByGroupKey[dependency.groupKey] === dependency.bundleKey) {
            return [];
          }
          const targetGroup = groupMap.get(dependency.groupKey);
          const targetBundle = getGroupBundle(dependency.groupKey, dependency.bundleKey);
          return [{
            key: dependency.key,
            groupKey: dependency.groupKey,
            groupLabel: targetGroup?.label ?? dependency.groupKey,
            bundleKey: dependency.bundleKey,
            bundleLabel: targetBundle?.label ?? dependency.bundleKey,
          }];
        });
        return unmetDependencies.length
          ? [[groupKey, unmetDependencies]]
          : [];
      }),
    );
    const policyTraceEntries: Array<[string, PolicyTrace]> = [];
    const globalManualGroups: string[] = [];
    const globalDependencyGroups: string[] = [];
    const globalAutoGroups: string[] = [];
    const globalBlockedGroups: string[] = [];
    const globalConflictGroups: string[] = [];
    const globalIdleGroups: string[] = [];
    selectedRefTemplateParameterGroups.forEach((group) => {
        const selectionKey = `${selectedRefTemplate.id}:${group.key}`;
        const coordinationPolicy = getCoordinationPolicy(group);
        const manualBundleKey = manualSelectionsByGroupKey[group.key] ?? "";
        const manualBundle = getGroupBundle(group.key, manualBundleKey);
        const resolvedBundleKey = resolvedSelectionsByGroupKey[group.key] ?? "";
        const resolvedBundle = getGroupBundle(group.key, resolvedBundleKey);
        const stickyBundleKey = predicateRefGroupAutoBundleSelections[selectionKey] ?? "";
        const dependencyRequests = dependencyRequestsByGroupKey[group.key] ?? [];
        const aggregatedDependencyRequests = sortAggregatedDependencyRequests(
          aggregateDependencyRequests(dependencyRequests),
          coordinationPolicy,
          stickyBundleKey,
        );
        const matchingAutoBundles = getSortedTemplateGroupPresetBundles(group.presetBundles).flatMap((bundle) => {
          if (!doesTemplateGroupBundleMatchAutoSelectRule(group, bundle, effectiveDraftBindings)) {
            return [];
          }
          const unmetDependencies = bundle.dependencies.flatMap((dependency) => {
            if (resolvedSelectionsByGroupKey[dependency.groupKey] === dependency.bundleKey) {
              return [];
            }
            const targetGroup = groupMap.get(dependency.groupKey);
            const targetBundle = getGroupBundle(dependency.groupKey, dependency.bundleKey);
            return [
              `${targetGroup?.label ?? dependency.groupKey} → ${targetBundle?.label ?? dependency.bundleKey}`,
            ];
          });
          return [{
            bundle,
            unmetDependencies,
          }];
        });
        const selectedByDependency = Boolean(
          resolvedBundleKey && aggregatedDependencyRequests.some((request) => request.bundleKey === resolvedBundleKey),
        );
        const selectedAutoBundleEntry =
          matchingAutoBundles.find(({ bundle }) => bundle.key === resolvedBundleKey)
          ?? null;
        const blockedAutoBundles = matchingAutoBundles.filter(
          ({ unmetDependencies }) => unmetDependencies.length > 0,
        );
        const unmetDependencies = unmetDependenciesByGroupKey[group.key] ?? [];
        let statusLabel = "Idle";
        let tone: PolicyTrace["tone"] = "muted";
        let summary = "No coordinated bundle is active for this group right now.";
        if (manualBundle) {
          statusLabel = "Manual";
          tone = "success";
          summary = `${manualBundle.label} is pinned manually and overrides auto coordination for this group.`;
        } else if (resolvedBundle && selectedByDependency) {
          statusLabel = "Resolved";
          tone = "success";
          summary = `${resolvedBundle.label} was selected from incoming dependency requests.`;
        } else if (resolvedBundle && selectedAutoBundleEntry) {
          statusLabel = "Auto";
          tone = "success";
          summary = `${resolvedBundle.label} auto-selected via ${selectedAutoBundleEntry.bundle.autoSelectRule.replaceAll("_", " ")}.`;
        } else if (
          aggregatedDependencyRequests.length > 1
          && coordinationPolicy === "manual_resolution"
        ) {
          statusLabel = "Blocked";
          tone = "warning";
          summary = "Conflicting dependency requests require manual resolution before this group can choose a bundle.";
        } else if (blockedAutoBundles.length) {
          statusLabel = "Blocked";
          tone = "warning";
          summary = "Auto-select candidates are currently blocked by unresolved dependencies.";
        } else if (aggregatedDependencyRequests.length) {
          statusLabel = "Pending";
          tone = "info";
          summary = "Dependency requests are present, but this group is still waiting for a coordinated decision.";
        }
        const policyDetailParts = [
          `Uses ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(coordinationPolicy)}.`,
        ];
        if (coordinationPolicy === "sticky_auto_selection" && stickyBundleKey) {
          const stickyBundle = getGroupBundle(group.key, stickyBundleKey);
          if (stickyBundle) {
            policyDetailParts.push(`Current sticky preference is ${stickyBundle.label}.`);
          }
        }
        const steps: PolicyTraceStep[] = [{
          key: `${group.key}:policy`,
          title: "Coordination policy",
          detail: policyDetailParts.join(" "),
          tone: "info",
        }];
        if (manualBundle) {
          steps.push({
            key: `${group.key}:manual`,
            title: "Manual override",
            detail: `${manualBundle.label} is manually selected, so dependency and auto-selection rules are treated as advisory until you clear the override.`,
            tone: "success",
          });
        }
        if (aggregatedDependencyRequests.length) {
          steps.push({
            key: `${group.key}:requests`,
            title: aggregatedDependencyRequests.length > 1
              ? "Incoming dependency requests"
              : "Incoming dependency request",
            detail: aggregatedDependencyRequests
              .map((request) => {
                const detailParts = [
                  `from ${request.sourceLabels.join(", ")}`,
                  `target P${request.targetPriority}`,
                  `source P${request.maxSourcePriority}`,
                ];
                if (request.hasManualSource) {
                  detailParts.push("includes manual source");
                }
                return `${request.bundleLabel} (${detailParts.join(" · ")})`;
              })
              .join("; "),
            tone: aggregatedDependencyRequests.length > 1 ? "warning" : "info",
          });
        }
        if (aggregatedDependencyRequests.length > 1) {
          if (coordinationPolicy === "manual_resolution" && !manualBundle && !resolvedBundle) {
            steps.push({
              key: `${group.key}:conflict`,
              title: "Conflict resolution",
              detail: "Multiple bundles were requested for this group, and the current policy requires an explicit manual choice before coordination can continue.",
              tone: "warning",
            });
          } else if (resolvedBundle) {
            steps.push({
              key: `${group.key}:conflict`,
              title: "Conflict resolution",
              detail: `${resolvedBundle.label} won the conflict under ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(coordinationPolicy)}.`,
              tone: "success",
            });
          }
        } else if (!manualBundle && resolvedBundle && selectedByDependency && aggregatedDependencyRequests[0]) {
          steps.push({
            key: `${group.key}:dependency-selection`,
            title: "Dependency-driven selection",
            detail: `${resolvedBundle.label} satisfied the active request from ${aggregatedDependencyRequests[0].sourceLabels.join(", ")}.`,
            tone: "success",
          });
        }
        if (!manualBundle && resolvedBundle && selectedAutoBundleEntry && !selectedByDependency) {
          steps.push({
            key: `${group.key}:auto-selection`,
            title: "Direct auto-selection",
            detail: `${resolvedBundle.label} matched ${selectedAutoBundleEntry.bundle.autoSelectRule.replaceAll("_", " ")} with priority P${selectedAutoBundleEntry.bundle.priority}.`,
            tone: "success",
          });
        }
        if (blockedAutoBundles.length) {
          steps.push({
            key: `${group.key}:blocked-auto`,
            title: "Blocked auto candidates",
            detail: blockedAutoBundles
              .map(
                ({ bundle, unmetDependencies: bundleUnmetDependencies }) =>
                  `${bundle.label} (${bundle.autoSelectRule.replaceAll("_", " ")}) is waiting on ${bundleUnmetDependencies.join(", ")}`,
              )
              .join("; "),
            tone: "warning",
          });
        }
        if (unmetDependencies.length) {
          steps.push({
            key: `${group.key}:unmet`,
            title: "Unmet dependencies",
            detail: `Waiting on ${unmetDependencies
              .map((dependency) => `${dependency.groupLabel} → ${dependency.bundleLabel}`)
              .join(", ")}.`,
            tone: "warning",
          });
        }
        if (tone === "muted" && steps.length === 1) {
          steps.push({
            key: `${group.key}:idle`,
            title: "Idle state",
            detail: "No incoming dependency requests or matching auto-select rules are currently activating this group.",
            tone: "muted",
          });
        }
        if (manualBundle) {
          globalManualGroups.push(group.label);
        } else if (resolvedBundle && selectedByDependency) {
          globalDependencyGroups.push(`${group.label} → ${resolvedBundle.label}`);
        } else if (resolvedBundle && selectedAutoBundleEntry) {
          globalAutoGroups.push(`${group.label} → ${resolvedBundle.label}`);
        } else if (tone === "warning") {
          globalBlockedGroups.push(group.label);
        } else if (tone === "muted") {
          globalIdleGroups.push(group.label);
        }
        if (aggregatedDependencyRequests.length > 1) {
          globalConflictGroups.push(group.label);
        }
        policyTraceEntries.push([group.key, {
          summary,
          statusLabel,
          tone,
          steps,
        }]);
      });
    const policyTraceByGroupKey = Object.fromEntries(policyTraceEntries);
    const globalPolicyTraceSteps: PolicyTraceStep[] = [];
    if (globalManualGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:manual",
        title: "Manual anchors",
        detail: `${globalManualGroups.join(", ")} currently pin their bundle choices manually, anchoring the coordination graph.`,
        tone: "success",
      });
    }
    if (globalDependencyGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:dependencies",
        title: "Dependency-driven chain",
        detail: globalDependencyGroups.join("; "),
        tone: "info",
      });
    }
    if (globalAutoGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:auto",
        title: "Direct auto selections",
        detail: globalAutoGroups.join("; "),
        tone: "success",
      });
    }
    if (globalConflictGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:conflicts",
        title: "Conflict hotspots",
        detail: `${globalConflictGroups.join(", ")} received competing bundle requests during coordination.`,
        tone: "warning",
      });
    }
    if (globalBlockedGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:blocked",
        title: "Blocked groups",
        detail: `${globalBlockedGroups.join(", ")} are blocked by unresolved dependencies or manual-resolution requirements.`,
        tone: "warning",
      });
    }
    if (globalIdleGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:idle",
        title: "Idle groups",
        detail: `${globalIdleGroups.join(", ")} are not currently activated by dependency or auto-selection rules.`,
        tone: "muted",
      });
    }
    const globalPolicyTrace: GlobalPolicyTrace = {
      summary: globalBlockedGroups.length
        ? `Coordination currently has ${globalBlockedGroups.length} blocked group${globalBlockedGroups.length === 1 ? "" : "s"} across ${selectedRefTemplateParameterGroups.length} template group${selectedRefTemplateParameterGroups.length === 1 ? "" : "s"}.`
        : globalDependencyGroups.length || globalAutoGroups.length || globalManualGroups.length
          ? `Coordination resolved ${Object.keys(resolvedSelectionsByGroupKey).length} group bundle${Object.keys(resolvedSelectionsByGroupKey).length === 1 ? "" : "s"} across the current dependency graph.`
          : "No coordination activity is currently running across this template graph.",
      statusLabel: globalBlockedGroups.length
        ? "Blocked"
        : globalDependencyGroups.length || globalAutoGroups.length || globalManualGroups.length
          ? "Active"
          : "Idle",
      tone: globalBlockedGroups.length
        ? "warning"
        : globalDependencyGroups.length || globalAutoGroups.length || globalManualGroups.length
          ? "info"
          : "muted",
      steps: globalPolicyTraceSteps,
      counts: {
        groupCount: selectedRefTemplateParameterGroups.length,
        manualCount: globalManualGroups.length,
        autoCount: globalDependencyGroups.length + globalAutoGroups.length,
        blockedCount: globalBlockedGroups.length,
        conflictCount: globalConflictGroups.length,
        dependencyRequestCount: Object.values(dependencyRequestsByGroupKey).reduce(
          (total, requests) => total + requests.length,
          0,
        ),
        unmetDependencyCount: Object.values(unmetDependenciesByGroupKey).reduce(
          (total, dependencies) => total + dependencies.length,
          0,
        ),
      },
    };
    return {
      autoSelectionsBySelectionKey: Object.fromEntries(
        Object.entries(autoSelectionsByGroupKey).map(([groupKey, bundleKey]) => [
          `${selectedRefTemplate.id}:${groupKey}`,
          bundleKey,
        ]),
      ),
      resolvedSelectionsByGroupKey,
      dependencyRequestsByGroupKey,
      unmetDependenciesByGroupKey,
      conflictRequestsByGroupKey,
      policyTraceByGroupKey,
      globalPolicyTrace,
      solverReplay,
    };
  }, [
    doesTemplateGroupBundleMatchAutoSelectRule,
    getSortedTemplateGroupPresetBundles,
    predicateRefDraftBindings,
    predicateRefGroupAutoBundleSelections,
    predicateRefGroupBundleSelections,
    selectedRefTemplate,
    selectedRefTemplateParameterGroups,
  ]);
  const coordinatedPredicateRefGroupBundleState = useMemo(
    () => computeCoordinatedPredicateRefGroupBundleState(),
    [computeCoordinatedPredicateRefGroupBundleState],
  );
  const bundleCoordinationSimulationPolicyOverrides = useMemo(() => {
    if (
      bundleCoordinationSimulationPolicy === "current"
      || !simulatedCoordinationGroups.length
    ) {
      return {};
    }
    if (bundleCoordinationSimulationScope === "all") {
      return Object.fromEntries(
        simulatedCoordinationGroups.map((group) => [group.key, bundleCoordinationSimulationPolicy]),
      );
    }
    return simulatedCoordinationGroups.some((group) => group.key === bundleCoordinationSimulationScope)
      ? { [bundleCoordinationSimulationScope]: bundleCoordinationSimulationPolicy }
      : {};
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    simulatedCoordinationGroups,
  ]);
  const hasActivePredicateRefReplayApplyConflictSimulationOverride = useMemo(
    () => Boolean(
      activePredicateRefReplayApplyConflictSimulationReview
      && (
        Object.keys(activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey).length
        || Object.keys(activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey).length
      )
    ),
    [
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey,
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey,
      activePredicateRefReplayApplyConflictSimulationReview,
    ],
  );
  const simulatedPredicateRefGroupBundleState = useMemo(
    () => (
      Object.keys(bundleCoordinationSimulationPolicyOverrides).length
      || hasActivePredicateRefReplayApplyConflictSimulationOverride
        ? computeCoordinatedPredicateRefGroupBundleState({
            draftBindingOverridesByParameterKey:
              activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey,
            manualSelectionOverridesBySelectionKey:
              activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey,
            policyOverridesByGroupKey: bundleCoordinationSimulationPolicyOverrides,
          })
        : null
    ),
    [
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey,
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey,
      bundleCoordinationSimulationPolicyOverrides,
      computeCoordinatedPredicateRefGroupBundleState,
      hasActivePredicateRefReplayApplyConflictSimulationOverride,
    ],
  );
  const simulatedPredicateRefSolverReplay = simulatedPredicateRefGroupBundleState?.solverReplay ?? [];
  const activeSimulatedPredicateRefSolverReplayIndex = simulatedPredicateRefSolverReplay.length
    ? Math.min(bundleCoordinationSimulationReplayIndex, simulatedPredicateRefSolverReplay.length - 1)
    : 0;
  const activeSimulatedPredicateRefSolverReplayStep = simulatedPredicateRefSolverReplay.length
    ? simulatedPredicateRefSolverReplay[activeSimulatedPredicateRefSolverReplayIndex]
    : null;
  const availableSimulatedPredicateRefSolverReplayActionTypes = useMemo(
    () => Array.from(
      new Set(
        simulatedPredicateRefSolverReplay.flatMap((step) => step.actions.map((action) => action.type)),
      ),
    ),
    [simulatedPredicateRefSolverReplay],
  );
  const availableSimulatedPredicateRefSolverReplayEdges = useMemo(
    () => Object.values(
      simulatedPredicateRefSolverReplay.reduce<Record<string, {
        key: string;
        label: string;
        sourceGroupKey: string;
        sourceGroupLabel: string;
        sourceBundleKey: string;
        sourceBundleLabel: string;
        targetGroupKey: string;
        targetGroupLabel: string;
        targetBundleKey: string;
        targetBundleLabel: string;
      }>>((accumulator, step) => {
        step.actions.forEach((action) => {
          action.dependencyEdges.forEach((edge) => {
            accumulator[edge.key] = edge;
          });
        });
        return accumulator;
      }, {}),
    ),
    [simulatedPredicateRefSolverReplay],
  );
  const activeSimulatedPredicateRefSolverReplayFilteredActions = useMemo(
    () => (
      activeSimulatedPredicateRefSolverReplayStep
        ? (
            activeSimulatedPredicateRefSolverReplayStep.actions.filter((action) => {
              if (
                bundleCoordinationSimulationReplayGroupFilter !== "all"
                && action.groupKey !== bundleCoordinationSimulationReplayGroupFilter
              ) {
                return false;
              }
              if (
                bundleCoordinationSimulationReplayActionTypeFilter !== "all"
                && action.type !== bundleCoordinationSimulationReplayActionTypeFilter
              ) {
                return false;
              }
              if (
                bundleCoordinationSimulationReplayEdgeFilter !== "all"
                && !action.dependencyEdges.some((edge) => edge.key === bundleCoordinationSimulationReplayEdgeFilter)
              ) {
                return false;
              }
              return true;
            })
          )
        : []
    ),
    [
      bundleCoordinationSimulationReplayActionTypeFilter,
      bundleCoordinationSimulationReplayEdgeFilter,
      activeSimulatedPredicateRefSolverReplayStep,
      bundleCoordinationSimulationReplayGroupFilter,
    ],
  );
  const activeSimulatedPredicateRefSolverReplayFilteredGroup = useMemo(
    () => (
      bundleCoordinationSimulationReplayGroupFilter === "all"
        ? null
        : simulatedCoordinationGroups.find((group) => group.key === bundleCoordinationSimulationReplayGroupFilter)
          ?? null
    ),
    [
      bundleCoordinationSimulationReplayGroupFilter,
      simulatedCoordinationGroups,
    ],
  );
  const activeSimulatedPredicateRefSolverReplayFilteredEdge = useMemo(
    () => (
      bundleCoordinationSimulationReplayEdgeFilter === "all"
        ? null
        : availableSimulatedPredicateRefSolverReplayEdges.find((edge) => edge.key === bundleCoordinationSimulationReplayEdgeFilter)
          ?? null
    ),
    [
      availableSimulatedPredicateRefSolverReplayEdges,
      bundleCoordinationSimulationReplayEdgeFilter,
    ],
  );
  const simulatedPredicateRefSolverReplayAttributionByGroupKey = useMemo(
    () => Object.fromEntries(
      simulatedCoordinationGroups.map((group) => {
        const selectedRefTemplateKey = selectedRefTemplate?.key ?? "template";
        const findGroupBundle = (groupKey: string, bundleKey: string) => {
          const targetGroup = simulatedCoordinationGroups.find((candidate) => candidate.key === groupKey);
          return targetGroup?.presetBundles.find((bundle) => bundle.key === bundleKey) ?? null;
        };
        const formatResolvedBundleLabel = (bundleKey: string) => {
          if (!bundleKey) {
            return "Unresolved";
          }
          return (
            getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) => bundle.key === bundleKey)?.label
            ?? bundleKey
          );
        };
        const buildEdgeRoleLabel = (
          edges: Array<{
            key: string;
            label: string;
            sourceGroupKey: string;
            targetGroupKey: string;
          }>,
        ) => {
          const hasSourceEdge = edges.some((edge) => edge.sourceGroupKey === group.key);
          const hasTargetEdge = edges.some((edge) => edge.targetGroupKey === group.key);
          if (hasSourceEdge && hasTargetEdge) {
            return "Bridge edge";
          }
          if (hasSourceEdge) {
            return "Outbound dependency edge";
          }
          if (hasTargetEdge) {
            return "Inbound dependency edge";
          }
          return "Related dependency edge";
        };
        const buildDependencySourceLocation = (
          edge: {
            sourceGroupKey: string;
            sourceBundleKey: string;
            targetGroupKey: string;
            targetBundleKey: string;
          },
        ) => {
          const sourceBundle = findGroupBundle(edge.sourceGroupKey, edge.sourceBundleKey);
          const dependencyIndex = sourceBundle?.dependencies.findIndex(
            (dependency) =>
              dependency.groupKey === edge.targetGroupKey && dependency.bundleKey === edge.targetBundleKey,
          ) ?? -1;
          return dependencyIndex >= 0
            ? `${selectedRefTemplateKey}.parameter_groups.${edge.sourceGroupKey}.preset_bundles.${edge.sourceBundleKey}.dependencies[${dependencyIndex}]`
            : `${selectedRefTemplateKey}.parameter_groups.${edge.sourceGroupKey}.preset_bundles.${edge.sourceBundleKey}.dependencies`;
        };
        let previousBundleKey = "";
        const chain: Array<{
          causalLabel: string;
          detail: string;
          edgeLabels: string[];
          edgeSourceLocations: string[];
          edgeRoleLabel: string | null;
          kind: "selection_change" | "group_action" | "dependency_edge";
          stateTransitionLabel: string | null;
          stepIndex: number;
          stepLabel: string;
          type: string | null;
        }> = [];
        for (let stepIndex = 0; stepIndex < simulatedPredicateRefSolverReplay.length; stepIndex += 1) {
          const step = simulatedPredicateRefSolverReplay[stepIndex];
          const resolvedBundleKey = step.resolvedSelectionsByGroupKey[group.key] ?? "";
          const matchingActions = step.actions.filter((action) =>
            action.groupKey === group.key
            || action.dependencyEdges.some((edge) =>
              edge.sourceGroupKey === group.key || edge.targetGroupKey === group.key));
          const directAction = matchingActions.find((action) => action.groupKey === group.key);
          const edgeAction = matchingActions.find((action) =>
            action.dependencyEdges.some((edge) =>
              edge.sourceGroupKey === group.key || edge.targetGroupKey === group.key));
          const relatedEdges = (directAction ?? edgeAction)?.dependencyEdges.filter((edge) =>
            edge.sourceGroupKey === group.key || edge.targetGroupKey === group.key) ?? [];
          const edgeRoleLabel = relatedEdges.length ? buildEdgeRoleLabel(relatedEdges) : null;
          const selectionChanged = resolvedBundleKey !== previousBundleKey;
          if (selectionChanged) {
            const previousBundleLabel = formatResolvedBundleLabel(previousBundleKey);
            const nextBundleLabel = formatResolvedBundleLabel(resolvedBundleKey);
            chain.push({
              causalLabel: "State transition",
              detail: resolvedBundleKey
                ? `${group.label} switched from ${previousBundleLabel} to ${nextBundleLabel} during ${step.title.toLowerCase()}.`
                : `${group.label} became unresolved during ${step.title.toLowerCase()}.`,
              edgeLabels: relatedEdges.map((edge) => edge.label),
              edgeSourceLocations: relatedEdges.map((edge) => buildDependencySourceLocation(edge)),
              edgeRoleLabel,
              kind: "selection_change",
              stateTransitionLabel: `${previousBundleLabel} -> ${nextBundleLabel}`,
              stepIndex,
              stepLabel: `Replay step ${stepIndex + 1}`,
              type: directAction?.type ?? edgeAction?.type ?? null,
            });
          } else if (directAction) {
            chain.push({
              causalLabel: edgeRoleLabel ? `${edgeRoleLabel} action` : "Group action",
              detail: directAction.detail,
              edgeLabels: relatedEdges.map((edge) => edge.label),
              edgeSourceLocations: relatedEdges.map((edge) => buildDependencySourceLocation(edge)),
              edgeRoleLabel,
              kind: "group_action",
              stateTransitionLabel: null,
              stepIndex,
              stepLabel: `Replay step ${stepIndex + 1}`,
              type: directAction.type,
            });
          } else if (edgeAction) {
            const edgeLabels = relatedEdges.map((edge) => edge.label);
            chain.push({
              causalLabel: edgeRoleLabel ?? "Dependency edge",
              detail: edgeLabels.length
                ? `${group.label} participates in ${edgeLabels.join(", ")} during ${step.title.toLowerCase()}.`
                : edgeAction.detail,
              edgeLabels,
              edgeSourceLocations: relatedEdges.map((edge) => buildDependencySourceLocation(edge)),
              edgeRoleLabel,
              kind: "dependency_edge",
              stateTransitionLabel: null,
              stepIndex,
              stepLabel: `Replay step ${stepIndex + 1}`,
              type: edgeAction.type,
            });
          }
          previousBundleKey = resolvedBundleKey;
        }
        const firstAttribution = chain[0] ?? null;
        return [group.key, {
          chain,
          chainSummary:
            chain.length > 1
              ? `${chain.length} replay steps · ${chain[0]?.causalLabel ?? chain[0]?.stepLabel ?? "Replay"} → ${chain[chain.length - 1]?.causalLabel ?? chain[chain.length - 1]?.stepLabel ?? "Replay"}`
              : chain.length === 1
                ? `1 replay step · ${chain[0]?.causalLabel ?? chain[0]?.stepLabel ?? "Replay"}`
                : "No replay attribution",
          detail: firstAttribution?.detail ?? null,
          stepIndex: firstAttribution?.stepIndex ?? -1,
          stepLabel: firstAttribution?.stepLabel ?? "No replay attribution",
          type: firstAttribution?.type ?? null,
        }] as const;
      }),
    ),
    [
      getSortedTemplateGroupPresetBundles,
      selectedRefTemplate,
      simulatedCoordinationGroups,
      simulatedPredicateRefSolverReplay,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChain = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
        ? (
            simulatedPredicateRefSolverReplayAttributionByGroupKey[
              activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
            ]?.chain ?? []
          )
        : []
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
      simulatedPredicateRefSolverReplayAttributionByGroupKey,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChainStepIndexSet = useMemo(
    () => new Set(
      activePredicateRefReplayApplyConflictSimulationFocusedChain.map((entry) => entry.stepIndex),
    ),
    [activePredicateRefReplayApplyConflictSimulationFocusedChain],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChainPosition = useMemo(
    () => activePredicateRefReplayApplyConflictSimulationFocusedChain.findIndex(
      (entry) => entry.stepIndex === activeSimulatedPredicateRefSolverReplayIndex,
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedChain,
      activeSimulatedPredicateRefSolverReplayIndex,
    ],
  );
  const selectedRefTemplateParameterGroupByKey = useMemo(
    () => Object.fromEntries(
      selectedRefTemplateParameterGroups.map((group) => [group.key, group] as const),
    ),
    [selectedRefTemplateParameterGroups],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedParameter = useMemo(
    () => {
      if (
        !activePredicateRefReplayApplyConflictSimulationFocusedItem
        || activePredicateRefReplayApplyConflictSimulationFocusedItem.section !== "binding_snapshot"
      ) {
        return null;
      }
      const parameterGroup =
        activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
          ? selectedRefTemplateParameterGroupByKey[activePredicateRefReplayApplyConflictSimulationFocusedGroupKey] ?? null
          : null;
      return parameterGroup?.parameters.find(
        (parameter) => parameter.key === activePredicateRefReplayApplyConflictSimulationFocusedItem.key,
      ) ?? null;
    },
    [
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
      activePredicateRefReplayApplyConflictSimulationFocusedItem,
      selectedRefTemplateParameterGroupByKey,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations = useMemo(
    () => {
      if (
        !selectedRefTemplate
        || !contracts.length
        || !activePredicateRefReplayApplyConflictSimulationReview
        || !activePredicateRefReplayApplyConflictSimulationFocusedItem
        || !activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
      ) {
        return [];
      }
      const collectTemplateClauseSourceLocations = (
        child: RunSurfaceCollectionQueryBuilderChildState,
        targetBindingKey: string,
        pathSegments: string[],
      ): Array<{ location: string; detail: string }> => {
        if (child.kind === "clause") {
          const matches: string[] = [];
          Object.entries(child.clause.parameterBindingKeys).forEach(([parameterKey, bindingKey]) => {
            if (bindingKey === targetBindingKey) {
              matches.push(`collection path binding ${parameterKey} -> $${targetBindingKey}`);
            }
          });
          if (child.clause.valueBindingKey === targetBindingKey) {
            matches.push(`condition value binding -> $${targetBindingKey}`);
          }
          if (!matches.length) {
            return [];
          }
          return [{
            location: `${selectedRefTemplate.key}.node.${pathSegments.join(".")}`,
            detail: `${matches.join(" · ")} · ${formatRunSurfaceCollectionQueryBuilderClauseSummary(child.clause, contracts)}`,
          }];
        }
        if (child.kind === "predicate_ref") {
          const matchingBindings = Object.entries(child.bindings)
            .flatMap(([bindingKey, value]) => {
              const referenceKey = fromRunSurfaceCollectionQueryBindingReferenceValue(value);
              return referenceKey === targetBindingKey
                ? [`predicate ref ${child.predicateKey} binds ${bindingKey} -> $${targetBindingKey}`]
                : [];
            });
          return matchingBindings.length
            ? [{
                location: `${selectedRefTemplate.key}.node.${pathSegments.join(".")}`,
                detail: matchingBindings.join(" · "),
              }]
            : [];
        }
        return child.children.flatMap((nestedChild, index) =>
          collectTemplateClauseSourceLocations(
            nestedChild,
            targetBindingKey,
            [
              ...pathSegments,
              nestedChild.kind === "clause"
                ? `clause_${index + 1}`
                : nestedChild.kind === "predicate_ref"
                  ? `predicate_ref_${index + 1}`
                  : `group_${index + 1}`,
            ],
          ));
      };
      const collectTemplateEvaluationProvenance = (
        child: RunSurfaceCollectionQueryBuilderChildState,
        targetBindingKeys: string[],
        bindingContextByKey: Record<string, string>,
        pathSegments: string[],
        templateKey: string,
        visitedTemplateKeys: string[],
      ): {
        matchedPredicateBranches: Array<{ location: string; detail: string }>;
        parameterComparisons: Array<{ location: string; detail: string }>;
        runtimeCandidateTraces: RunSurfaceCollectionQueryRuntimeCandidateTrace[];
        shortCircuitTraces: Array<{ location: string; detail: string }>;
        truthTableRows: Array<{ detail: string; expression: string; location: string; result: boolean }>;
        result: boolean;
      } => {
        const buildChildPathSegment = (
          nestedChild: RunSurfaceCollectionQueryBuilderChildState,
          index: number,
        ) => (
          nestedChild.kind === "clause"
            ? `clause_${index + 1}`
            : nestedChild.kind === "predicate_ref"
              ? `predicate_ref_${index + 1}`
              : `group_${index + 1}`
        );
        if (child.kind === "clause") {
          const clauseLocation = `${templateKey}.node.${pathSegments.join(".")}`;
          const activeContract =
            contracts.find((contract) => contract.contract_key === child.clause.contractKey) ?? null;
          const activeSchema =
            getRunSurfaceCollectionQuerySchemas(activeContract).find(
              (schema) => getCollectionQuerySchemaId(schema) === child.clause.schemaId,
            ) ?? null;
          const field = contracts
            .flatMap((contract) => getRunSurfaceCollectionQuerySchemas(contract))
            .flatMap((schema) => schema.elementSchema)
            .find((candidate) => candidate.key === child.clause.fieldKey) ?? null;
          const operator = field?.operators.find((candidate) => candidate.key === child.clause.operatorKey) ?? null;
          const matchedPathBindings = Object.entries(child.clause.parameterBindingKeys)
            .filter(([, bindingKey]) => targetBindingKeys.includes(bindingKey));
          const matchedValueBinding = targetBindingKeys.includes(child.clause.valueBindingKey);
          const comparisonNotes = [
            ...matchedPathBindings.map(([parameterKey, bindingKey]) =>
              `${parameterKey} reads $${bindingKey} = ${bindingContextByKey[bindingKey] ?? "$" + bindingKey}`),
            ...(
              matchedValueBinding
                ? [
                    `value operand uses $${child.clause.valueBindingKey} = ${
                      bindingContextByKey[child.clause.valueBindingKey] ?? "$" + child.clause.valueBindingKey
                    }`,
                  ]
                : []
            ),
          ];
          const directMatch = matchedPathBindings.length > 0 || matchedValueBinding;
          const parameterComparisons = [
            ...matchedPathBindings.map(([parameterKey, bindingKey]) => ({
              location: clauseLocation,
              detail:
                `${field?.title ?? child.clause.fieldKey} reads collection path segment ${parameterKey} from $${bindingKey} `
                + `(${bindingContextByKey[bindingKey] ?? "$" + bindingKey}). `
                + `Clause comparison: ${formatRunSurfaceCollectionQueryBuilderClauseSummary(child.clause, contracts)}.`,
            })),
            ...(
              matchedValueBinding
                ? [{
                    location: clauseLocation,
                    detail:
                      `${field?.title ?? child.clause.fieldKey} ${operator?.label ?? child.clause.operatorKey} compares against `
                      + `$${child.clause.valueBindingKey} (${bindingContextByKey[child.clause.valueBindingKey] ?? "$" + child.clause.valueBindingKey}). `
                      + `Clause comparison: ${formatRunSurfaceCollectionQueryBuilderClauseSummary(child.clause, contracts)}.`,
                  }]
                : []
            ),
          ];
          const resolvedParameterValues = activeSchema
            ? Object.fromEntries(
                activeSchema.parameters.map((parameter) => {
                  const bindingKey = child.clause.parameterBindingKeys[parameter.key]?.trim() ?? "";
                  return [
                    parameter.key,
                    bindingKey
                      ? (bindingContextByKey[bindingKey] ?? `$${bindingKey}`)
                      : (child.clause.parameterValues[parameter.key] ?? ""),
                  ] as const;
                }),
              )
            : child.clause.parameterValues;
          const resolvedCandidatePath = activeSchema
            ? resolveCollectionQueryPath(activeSchema.pathTemplate, resolvedParameterValues)
            : [];
          const candidatePath = resolvedCandidatePath.length
            ? `${resolvedCandidatePath.join(".")}[*]`
            : `${child.clause.schemaId || "collection"}[*]`;
          const candidateAccessor = field
            ? (
                field.valueRoot
                  ? `${activeSchema?.itemKind ?? "candidate"} value`
                  : `${activeSchema?.itemKind ?? "candidate"}.${field.valuePath.join(".") || field.key}`
              )
            : "candidate value";
          const comparedValueOperand = field
            ? coerceCollectionQueryBuilderValue(
                child.clause.valueBindingKey
                  ? (bindingContextByKey[child.clause.valueBindingKey] ?? "")
                  : child.clause.builderValue,
                field.valueType,
              )
            : child.clause.builderValue;
          const comparedValue = child.clause.valueBindingKey
            ? (
                formatCollectionQueryBuilderValue(comparedValueOperand, field?.valueType ?? "string")
                || `$${child.clause.valueBindingKey}`
              )
            : (child.clause.builderValue || "(blank)");
          const concreteRuntimeSamples = buildRunSurfaceCollectionQueryRuntimeCandidateSamples({
            comparedValueLabel: comparedValue,
            comparedValueOperand,
            field,
            operatorKey: child.clause.operatorKey,
            quantifier: child.clause.quantifier,
            resolvedParameterValues,
            runs: runtimeRuns,
            schema: activeSchema,
          });
          const runtimeCandidateTraces = [{
            allValues: concreteRuntimeSamples.allValues,
            bindingContextByKey,
            candidateAccessor,
            candidatePath,
            comparedValue,
            detail:
              `${child.clause.quantifier.toUpperCase()} evaluates ${candidateAccessor} from ${candidatePath} `
              + `${operator?.label ?? child.clause.operatorKey} ${comparedValue}. `
              + (
                concreteRuntimeSamples.sampleTotalCount
                  ? `Concrete payload replay: ${concreteRuntimeSamples.sampleMatchCount}/${concreteRuntimeSamples.sampleTotalCount} candidate values matched across ${runtimeRuns.length} run payloads. `
                  : runtimeRuns.length
                    ? "Concrete payload replay found no candidate values across the current run payloads. "
                    : "No run payloads are attached to replay concrete candidate values. "
              )
              + (comparisonNotes.length
                ? `Resolved inputs: ${comparisonNotes.join(" · ")}`
                : "No reviewed binding reached the candidate inputs for this clause."),
            editorClause: child.clause,
            location: clauseLocation,
            quantifier: child.clause.quantifier,
            result: directMatch,
            runOutcomes: concreteRuntimeSamples.runOutcomes,
            sampleMatchCount: concreteRuntimeSamples.sampleMatchCount,
            sampleTotalCount: concreteRuntimeSamples.sampleTotalCount,
            sampleTruncated: concreteRuntimeSamples.sampleTruncated,
            sampleValues: concreteRuntimeSamples.sampleValues,
          }];
          return {
            matchedPredicateBranches: [],
            parameterComparisons,
            runtimeCandidateTraces,
            shortCircuitTraces: [],
            truthTableRows: [{
              location: clauseLocation,
              expression: formatRunSurfaceCollectionQueryBuilderClauseSummary(child.clause, contracts),
              result: directMatch,
              detail: directMatch
                ? `Reviewed binding participates in this clause. ${comparisonNotes.join(" · ")}`
                : "Reviewed binding does not participate in this clause evaluation path.",
            }],
            result: directMatch,
          };
        }
        if (child.kind === "predicate_ref") {
          const predicateLocation = `${templateKey}.node.${pathSegments.join(".")}`;
          const matchedParameterBindings = Object.entries(child.bindings)
            .flatMap(([bindingKey, value]) => {
              const referenceKey = fromRunSurfaceCollectionQueryBindingReferenceValue(value);
              return targetBindingKeys.includes(referenceKey)
                ? [[bindingKey, referenceKey] as const]
                : [];
            });
          if (!matchedParameterBindings.length) {
            return {
              matchedPredicateBranches: [],
              parameterComparisons: [],
              runtimeCandidateTraces: [{
                allValues: [],
                candidateAccessor: child.predicateKey,
                candidatePath: predicateLocation,
                comparedValue: "No matching binding",
                detail: "Predicate reference has no reviewed binding flowing into its runtime parameters.",
                editorClause: null,
                location: predicateLocation,
                quantifier: "any",
                result: false,
                runOutcomes: [],
                sampleMatchCount: 0,
                sampleTotalCount: 0,
                sampleTruncated: false,
                sampleValues: [],
              }],
              shortCircuitTraces: [],
              truthTableRows: [{
                location: predicateLocation,
                expression: formatRunSurfaceCollectionQueryBuilderChildSummary(child, contracts),
                result: false,
                detail: "Reviewed binding does not flow into this predicate reference.",
              }],
              result: false,
            };
          }
          const matchedPredicateBranches = [{
            location: predicateLocation,
            detail:
              `${child.predicateKey} activates because ${matchedParameterBindings
                .map(([bindingKey, referenceKey]) =>
                  `${bindingKey} -> $${referenceKey} (${bindingContextByKey[referenceKey] ?? "$" + referenceKey})`)
                .join(" · ")}.`,
          }];
          const nestedBindingContextByKey = Object.fromEntries(
            matchedParameterBindings.map(([bindingKey, referenceKey]) => [
              bindingKey,
              bindingContextByKey[referenceKey] ?? `$${referenceKey}`,
            ]),
          );
          if (visitedTemplateKeys.includes(child.predicateKey)) {
            return {
              matchedPredicateBranches,
              parameterComparisons: [],
              runtimeCandidateTraces: [{
                allValues: [],
                candidateAccessor: child.predicateKey,
                candidatePath: predicateLocation,
                comparedValue: "Cycle guard",
                detail: "Predicate reference matched but nested runtime candidate replay stopped at a cycle guard.",
                editorClause: null,
                location: predicateLocation,
                quantifier: "any",
                result: true,
                runOutcomes: [],
                sampleMatchCount: 0,
                sampleTotalCount: 0,
                sampleTruncated: false,
                sampleValues: [],
              }],
              shortCircuitTraces: [{
                location: predicateLocation,
                detail: `Stopped recursion at ${child.predicateKey} to avoid a predicate template cycle.`,
              }],
              truthTableRows: [{
                location: predicateLocation,
                expression: formatRunSurfaceCollectionQueryBuilderChildSummary(child, contracts),
                result: true,
                detail: "Predicate reference matched, but nested template replay stopped at a cycle guard.",
              }],
              result: true,
            };
          }
          const referencedTemplate = predicateTemplates.find((template) => template.key === child.predicateKey) ?? null;
          if (!referencedTemplate) {
            return {
              matchedPredicateBranches,
              parameterComparisons: [],
              runtimeCandidateTraces: [{
                allValues: [],
                candidateAccessor: child.predicateKey,
                candidatePath: predicateLocation,
                comparedValue: "Template missing",
                detail: "Predicate reference matched and no nested template definition was available for runtime candidate replay.",
                editorClause: null,
                location: predicateLocation,
                quantifier: "any",
                result: true,
                runOutcomes: [],
                sampleMatchCount: 0,
                sampleTotalCount: 0,
                sampleTruncated: false,
                sampleValues: [],
              }],
              shortCircuitTraces: [],
              truthTableRows: [{
                location: predicateLocation,
                expression: formatRunSurfaceCollectionQueryBuilderChildSummary(child, contracts),
                result: true,
                detail: "Predicate reference matched and no local template definition was needed for further evaluation.",
              }],
              result: true,
            };
          }
          const nestedEvaluation = collectTemplateEvaluationProvenance(
            referencedTemplate.node,
            matchedParameterBindings.map(([bindingKey]) => bindingKey),
            nestedBindingContextByKey,
            ["root"],
            `${selectedRefTemplate.key}.predicate_templates.${child.predicateKey}.template`,
            [...visitedTemplateKeys, child.predicateKey],
          );
          const predicateResult = child.negated ? !nestedEvaluation.result : nestedEvaluation.result;
          return {
            matchedPredicateBranches: [
              ...matchedPredicateBranches,
              ...nestedEvaluation.matchedPredicateBranches,
            ],
            parameterComparisons: nestedEvaluation.parameterComparisons,
            runtimeCandidateTraces: [
              {
                allValues: [],
                candidateAccessor: child.predicateKey,
                candidatePath: predicateLocation,
                comparedValue: matchedParameterBindings
                  .map(([bindingKey, referenceKey]) =>
                    `${bindingKey}=${bindingContextByKey[referenceKey] ?? `$${referenceKey}`}`)
                  .join(" · "),
                detail:
                  `${child.predicateKey} receives runtime bindings ${matchedParameterBindings
                    .map(([bindingKey, referenceKey]) =>
                      `${bindingKey} <- $${referenceKey} (${bindingContextByKey[referenceKey] ?? "$" + referenceKey})`)
                    .join(" · ")}.`,
                editorClause: null,
                location: predicateLocation,
                quantifier: "any",
                result: predicateResult,
                runOutcomes: [],
                sampleMatchCount: 0,
                sampleTotalCount: 0,
                sampleTruncated: false,
                sampleValues: [],
              },
              ...nestedEvaluation.runtimeCandidateTraces,
            ],
            shortCircuitTraces: nestedEvaluation.shortCircuitTraces,
            truthTableRows: [
              {
                location: predicateLocation,
                expression: formatRunSurfaceCollectionQueryBuilderChildSummary(child, contracts),
                result: predicateResult,
                detail:
                  `${child.predicateKey} ${child.negated ? "negates and " : ""}reuses ${matchedParameterBindings
                    .map(([bindingKey, referenceKey]) =>
                      `${bindingKey} <- $${referenceKey} (${bindingContextByKey[referenceKey] ?? "$" + referenceKey})`)
                    .join(" · ")}.`,
              },
              ...nestedEvaluation.truthTableRows,
            ],
            result: predicateResult,
          };
        }
        const evaluatedChildren: Array<{
          child: RunSurfaceCollectionQueryBuilderChildState;
          evaluation: {
            matchedPredicateBranches: Array<{ location: string; detail: string }>;
            parameterComparisons: Array<{ location: string; detail: string }>;
            runtimeCandidateTraces: RunSurfaceCollectionQueryRuntimeCandidateTrace[];
            shortCircuitTraces: Array<{ location: string; detail: string }>;
            truthTableRows: Array<{ detail: string; expression: string; location: string; result: boolean }>;
            result: boolean;
          };
          index: number;
          pathSegment: string;
        }> = [];
        const skippedChildren: Array<{ child: RunSurfaceCollectionQueryBuilderChildState; index: number; pathSegment: string }> = [];
        const baseGroupResult = child.logic === "and";
        let groupResult = baseGroupResult;
        let stopReason: string | null = null;
        child.children.forEach((nestedChild, index) => {
          const pathSegment = buildChildPathSegment(nestedChild, index);
          if (stopReason) {
            skippedChildren.push({ child: nestedChild, index, pathSegment });
            return;
          }
          const nestedEvaluation = collectTemplateEvaluationProvenance(
            nestedChild,
            targetBindingKeys,
            bindingContextByKey,
            [...pathSegments, pathSegment],
            templateKey,
            visitedTemplateKeys,
          );
          evaluatedChildren.push({
            child: nestedChild,
            evaluation: nestedEvaluation,
            index,
            pathSegment,
          });
          if (child.logic === "and") {
            groupResult = groupResult && nestedEvaluation.result;
            if (!nestedEvaluation.result) {
              stopReason = `${formatRunSurfaceCollectionQueryBuilderChildSummary(nestedChild, contracts)} returned false inside AND`;
            }
            return;
          }
          groupResult = groupResult || nestedEvaluation.result;
          if (nestedEvaluation.result) {
            stopReason = `${formatRunSurfaceCollectionQueryBuilderChildSummary(nestedChild, contracts)} returned true inside OR`;
          }
        });
        const resolvedGroupResult = child.negated ? !groupResult : groupResult;
        return evaluatedChildren.reduce<{
          matchedPredicateBranches: Array<{ location: string; detail: string }>;
          parameterComparisons: Array<{ location: string; detail: string }>;
          runtimeCandidateTraces: RunSurfaceCollectionQueryRuntimeCandidateTrace[];
          shortCircuitTraces: Array<{ location: string; detail: string }>;
          truthTableRows: Array<{ detail: string; expression: string; location: string; result: boolean }>;
          result: boolean;
        }>((accumulator, nestedChild) => {
          return {
            matchedPredicateBranches: [
              ...accumulator.matchedPredicateBranches,
              ...nestedChild.evaluation.matchedPredicateBranches,
            ],
            parameterComparisons: [
              ...accumulator.parameterComparisons,
              ...nestedChild.evaluation.parameterComparisons,
            ],
            runtimeCandidateTraces: [
              ...accumulator.runtimeCandidateTraces,
              ...nestedChild.evaluation.runtimeCandidateTraces,
            ],
            shortCircuitTraces: [
              ...accumulator.shortCircuitTraces,
              ...nestedChild.evaluation.shortCircuitTraces,
            ],
            truthTableRows: [
              ...accumulator.truthTableRows,
              ...nestedChild.evaluation.truthTableRows,
            ],
            result: resolvedGroupResult,
          };
        }, {
          matchedPredicateBranches: [],
          parameterComparisons: [],
          runtimeCandidateTraces: [{
            allValues: [],
            candidateAccessor: `${child.logic.toUpperCase()} subgroup`,
            candidatePath: `${templateKey}.node.${pathSegments.join(".")}`,
            comparedValue: stopReason ?? "all child branches evaluated",
            detail:
              `${child.logic.toUpperCase()} subgroup ${child.negated ? "negates " : ""}combines child runtime candidate rows. `
              + (stopReason ? `Resolution stopped early because ${stopReason}.` : "Every child candidate row was evaluated."),
            editorClause: null,
            location: `${templateKey}.node.${pathSegments.join(".")}`,
            quantifier: "any",
            result: resolvedGroupResult,
            runOutcomes: [],
            sampleMatchCount: 0,
            sampleTotalCount: 0,
            sampleTruncated: false,
            sampleValues: [],
          }],
          shortCircuitTraces: [
            ...skippedChildren.map((skippedChild) => ({
              location: `${templateKey}.node.${[...pathSegments, skippedChild.pathSegment].join(".")}`,
              detail:
                `Skipped ${formatRunSurfaceCollectionQueryBuilderChildSummary(skippedChild.child, contracts)} because `
                + `${stopReason ?? `${child.logic.toUpperCase()} subgroup already resolved`}.`,
            })),
          ],
          truthTableRows: [{
            location: `${templateKey}.node.${pathSegments.join(".")}`,
            expression: formatRunSurfaceCollectionQueryBuilderChildSummary(child, contracts),
            result: resolvedGroupResult,
            detail:
              `${child.logic.toUpperCase()} subgroup ${child.negated ? "negates " : ""}evaluated to ${
                resolvedGroupResult ? "true" : "false"
              }. ${stopReason ? `Short-circuit: ${stopReason}.` : "Every child branch was evaluated."}`,
          }],
          result: resolvedGroupResult,
        });
      };
      const group =
        selectedRefTemplateParameterGroupByKey[activePredicateRefReplayApplyConflictSimulationFocusedGroupKey] ?? null;
      if (!group) {
        return [];
      }
      const selectedSource =
        activePredicateRefReplayApplyConflictSimulationReview.selectedSources[
          activePredicateRefReplayApplyConflictSimulationFocusedItem.decisionKey
        ] ?? "local";
      const reviewedValue = selectedSource === "remote"
        ? activePredicateRefReplayApplyConflictSimulationFocusedItem.remoteValue
        : activePredicateRefReplayApplyConflictSimulationFocusedItem.localValue;
      const reviewedParameter = activePredicateRefReplayApplyConflictSimulationFocusedParameter;
      const clauseSourceLocations = reviewedParameter
        ? collectTemplateClauseSourceLocations(selectedRefTemplate.node, reviewedParameter.key, ["root"])
        : [];
      const evaluationProvenance = reviewedParameter
        ? collectTemplateEvaluationProvenance(
            selectedRefTemplate.node,
            [reviewedParameter.key],
            { [reviewedParameter.key]: reviewedValue },
            ["root"],
            selectedRefTemplate.key,
            [selectedRefTemplate.key],
          )
        : {
            matchedPredicateBranches: [],
            parameterComparisons: [],
            runtimeCandidateTraces: [],
            shortCircuitTraces: [],
            truthTableRows: [],
            result: false,
          };
      const effectiveCoordinationPolicy =
        bundleCoordinationSimulationPolicyOverrides[group.key] ?? group.coordinationPolicy;
      return activePredicateRefReplayApplyConflictSimulationFocusedChain.map((entry) => {
        const step = simulatedPredicateRefSolverReplay[entry.stepIndex] ?? null;
        const bundleKey = step?.resolvedSelectionsByGroupKey[group.key] ?? "";
        const bundle =
          getSortedTemplateGroupPresetBundles(group.presetBundles).find((candidate) => candidate.key === bundleKey)
          ?? null;
        const parameterReasons: Array<{ label: string; detail: string }> = [{
          label: "Reviewed pick",
          detail: `${activePredicateRefReplayApplyConflictSimulationFocusedItem.label} keeps the ${selectedSource} value (${reviewedValue}).`,
        }];
        if (reviewedParameter) {
          const currentBindingValue =
            activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey[
              reviewedParameter.key
            ] ?? "";
          const reasonParts = [
            `${reviewedParameter.customLabel.trim() || reviewedParameter.label} is a ${reviewedParameter.valueType} parameter.`,
          ];
          if (currentBindingValue) {
            reasonParts.push(
              isRunSurfaceCollectionQueryBindingReferenceValue(currentBindingValue)
                ? `Current draft binds it to $${fromRunSurfaceCollectionQueryBindingReferenceValue(currentBindingValue)}.`
                : `Current draft value is ${currentBindingValue}.`,
            );
          } else if (reviewedParameter.defaultValue.trim()) {
            reasonParts.push(`Template default is ${reviewedParameter.defaultValue}.`);
          }
          if (reviewedParameter.bindingPreset.trim()) {
            reasonParts.push(`Suggested binding preset is $${reviewedParameter.bindingPreset}.`);
          }
          if (reviewedParameter.helpNote.trim()) {
            reasonParts.push(reviewedParameter.helpNote.trim());
          }
          parameterReasons.push({
            label: reviewedParameter.customLabel.trim() || reviewedParameter.label,
            detail: reasonParts.join(" "),
          });
        }
        const bundleParameterReasons = bundle
          ? group.parameters.flatMap((parameter) => {
              const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim() ?? "";
              const parameterValue = bundle.parameterValues[parameter.key]?.trim() ?? "";
              if (!bindingPreset && !parameterValue) {
                return [];
              }
              return [{
                label: parameter.customLabel.trim() || parameter.label,
                detail: bindingPreset
                  ? `${bundle.label} binds ${parameter.customLabel.trim() || parameter.label} to $${bindingPreset}.`
                  : `${bundle.label} fixes ${parameter.customLabel.trim() || parameter.label} to ${parameterValue}.`,
              }];
            }).slice(0, 3)
          : [];
        parameterReasons.push(...bundleParameterReasons);
        if (!bundleParameterReasons.length && group.helpNote.trim()) {
          parameterReasons.push({
            label: group.label,
            detail: group.helpNote.trim(),
          });
        }
        const bindingSourceLocations: Array<{ location: string; detail: string }> = [{
          location: `${selectedRefTemplate.key}.parameter_groups.${group.key}.coordination_policy`,
          detail: `Uses ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(effectiveCoordinationPolicy)} for ${group.label}.`,
        }];
        if (reviewedParameter) {
          bindingSourceLocations.push({
            location: `${selectedRefTemplate.key}.parameters.${reviewedParameter.key}`,
            detail: `${reviewedParameter.customLabel.trim() || reviewedParameter.label} · ${reviewedParameter.valueType}`,
          });
          if (reviewedParameter.defaultValue.trim()) {
            bindingSourceLocations.push({
              location: `${selectedRefTemplate.key}.parameters.${reviewedParameter.key}.default_value`,
              detail: `Default ${reviewedParameter.defaultValue}`,
            });
          }
          if (reviewedParameter.bindingPreset.trim()) {
            bindingSourceLocations.push({
              location: `${selectedRefTemplate.key}.parameters.${reviewedParameter.key}.binding_preset`,
              detail: `Preset $${reviewedParameter.bindingPreset}`,
            });
          }
        }
        let bundleRuleTitle = bundle?.label ?? "No resolved bundle";
        let bundleRuleDetail = entry.detail;
        if (bundle) {
          bindingSourceLocations.push({
            location: `${selectedRefTemplate.key}.parameter_groups.${group.key}.preset_bundles.${bundle.key}`,
            detail: `${bundle.label} · priority P${bundle.priority}`,
          });
          if (entry.type === "manual_anchor") {
            bundleRuleDetail = `${entry.detail} ${bundle.label} stays pinned manually for ${group.label}.`;
          } else if (entry.type === "dependency_selection") {
            bundleRuleDetail = `${entry.detail} ${bundle.label} resolves under ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(effectiveCoordinationPolicy)} at priority P${bundle.priority}.`;
          } else if (entry.type === "direct_auto_selection") {
            bundleRuleDetail = `${entry.detail} ${bundle.label} matches ${bundle.autoSelectRule.replaceAll("_", " ")} at priority P${bundle.priority}.`;
          } else if (entry.type === "conflict_blocked") {
            bundleRuleDetail = `${entry.detail} ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(effectiveCoordinationPolicy)} blocks automatic bundle resolution.`;
          } else if (bundle.helpNote.trim()) {
            bundleRuleDetail = `${entry.detail} ${bundle.helpNote.trim()}`;
          }
          if (bundle.autoSelectRule !== "manual") {
            bindingSourceLocations.push({
              location: `${selectedRefTemplate.key}.parameter_groups.${group.key}.preset_bundles.${bundle.key}.auto_select_rule`,
              detail: `Auto rule ${bundle.autoSelectRule.replaceAll("_", " ")}`,
            });
          }
          if (reviewedParameter) {
            const bundleBindingPreset = bundle.parameterBindingPresets[reviewedParameter.key]?.trim();
            const bundleParameterValue = bundle.parameterValues[reviewedParameter.key]?.trim();
            if (bundleBindingPreset) {
              bindingSourceLocations.push({
                location: `${selectedRefTemplate.key}.parameter_groups.${group.key}.preset_bundles.${bundle.key}.parameter_binding_presets.${reviewedParameter.key}`,
                detail: `Binds ${reviewedParameter.customLabel.trim() || reviewedParameter.label} to $${bundleBindingPreset}`,
              });
            }
            if (bundleParameterValue) {
              bindingSourceLocations.push({
                location: `${selectedRefTemplate.key}.parameter_groups.${group.key}.preset_bundles.${bundle.key}.parameter_values.${reviewedParameter.key}`,
                detail: `Sets ${reviewedParameter.customLabel.trim() || reviewedParameter.label} to ${bundleParameterValue}`,
              });
            }
          }
        } else if (entry.kind === "selection_change") {
          bundleRuleTitle = "State transition";
        }
        bindingSourceLocations.push(
          ...entry.edgeSourceLocations.map((location) => ({
            location,
            detail: "Dependency edge source location",
          })),
        );
        return {
          ...entry,
          bundleRuleDetail,
          bundleRuleTitle,
          clauseSourceLocations,
          bindingSourceLocations,
          matchedPredicateBranches: evaluationProvenance.matchedPredicateBranches,
          parameterReasons,
          parameterComparisons: evaluationProvenance.parameterComparisons,
          runtimeCandidateTraces: evaluationProvenance.runtimeCandidateTraces,
          shortCircuitTraces: evaluationProvenance.shortCircuitTraces,
          truthTableRows: evaluationProvenance.truthTableRows,
        };
      });
    },
    [
      contracts,
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey,
      activePredicateRefReplayApplyConflictSimulationFocusedChain,
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
      activePredicateRefReplayApplyConflictSimulationFocusedItem,
      activePredicateRefReplayApplyConflictSimulationFocusedParameter,
      activePredicateRefReplayApplyConflictSimulationReview,
      bundleCoordinationSimulationPolicyOverrides,
      getSortedTemplateGroupPresetBundles,
      predicateTemplates,
      runtimeRuns,
      selectedRefTemplate,
      selectedRefTemplateParameterGroupByKey,
      simulatedPredicateRefSolverReplay,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChainEntry = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationFocusedChainPosition >= 0
        ? activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations[
            activePredicateRefReplayApplyConflictSimulationFocusedChainPosition
          ] ?? null
        : null
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations,
      activePredicateRefReplayApplyConflictSimulationFocusedChainPosition,
    ],
  );
  const runtimeCandidateTraceByKey = useMemo(() => {
    const entries = new Map<string, RunSurfaceCollectionQueryRuntimeCandidateTrace>();
    activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations.forEach((entry) => {
      entry.runtimeCandidateTraces.forEach((trace) => {
        entries.set(buildRuntimeCandidateTraceDrillthroughKey("focused_chain", entry.stepIndex, trace), trace);
      });
    });
    if (activePredicateRefReplayApplyConflictSimulationFocusedChainEntry) {
      activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.runtimeCandidateTraces.forEach((trace) => {
        entries.set(
          buildRuntimeCandidateTraceDrillthroughKey(
            "active_replay",
            activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.stepIndex,
            trace,
          ),
          trace,
        );
      });
    }
    return entries;
  }, [
    activePredicateRefReplayApplyConflictSimulationFocusedChainEntry,
    activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations,
    buildRuntimeCandidateTraceDrillthroughKey,
  ]);
  const pinnedRuntimeCandidateOriginTrace = useMemo(
    () => (
      pinnedRuntimeCandidateClauseOriginKey
        ? runtimeCandidateTraceByKey.get(pinnedRuntimeCandidateClauseOriginKey) ?? null
        : null
    ),
    [pinnedRuntimeCandidateClauseOriginKey, runtimeCandidateTraceByKey],
  );
  const allRuntimeCandidateSamples = useMemo(
    () => Array.from(runtimeCandidateTraceByKey.values()).flatMap((trace) => trace.allValues),
    [runtimeCandidateTraceByKey],
  );
  const runtimeCandidateSampleByKey = useMemo(
    () => new Map(
      allRuntimeCandidateSamples.map((sample) => [
        buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
        sample,
      ] as const),
    ),
    [allRuntimeCandidateSamples],
  );
  const activeRuntimeCandidateMatchKeys = useMemo(
    () => Array.from(
      new Set(
        allRuntimeCandidateSamples
          .filter(doesRuntimeCandidateSampleMatchActiveContext)
          .map((sample) => buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample)),
      ),
    ),
    [allRuntimeCandidateSamples, doesRuntimeCandidateSampleMatchActiveContext],
  );
  const effectivePersistedRuntimeCandidateArtifactSelection = useMemo(
    () => (
      activeRuntimeCandidateRunContext
      && !activeRuntimeCandidateRunContext.artifactHoverKey
      && isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface(
        activeRuntimeCandidateRunContext,
        persistedRuntimeCandidateArtifactSelection,
      )
        ? persistedRuntimeCandidateArtifactSelection
        : null
    ),
    [activeRuntimeCandidateRunContext, persistedRuntimeCandidateArtifactSelection],
  );
  const effectiveRuntimeCandidateSelectionKeys = useMemo(
    () => (
      activeRuntimeCandidateRunContext?.artifactHoverKey
        ? activeRuntimeCandidateMatchKeys
        : (effectivePersistedRuntimeCandidateArtifactSelection?.sampleKeys ?? activeRuntimeCandidateMatchKeys)
    ),
    [
      activeRuntimeCandidateMatchKeys,
      activeRuntimeCandidateRunContext?.artifactHoverKey,
      effectivePersistedRuntimeCandidateArtifactSelection,
    ],
  );
  const resolveRuntimeCandidateSampleArtifactHoverKey = useCallback(
    (sample: RunSurfaceCollectionQueryRuntimeCandidateSample) => {
      if (
        activeRuntimeCandidateRunContext?.artifactHoverKey
        && sample.runContextArtifactHoverKeys.includes(activeRuntimeCandidateRunContext.artifactHoverKey)
      ) {
        return activeRuntimeCandidateRunContext.artifactHoverKey;
      }
      if (
        effectivePersistedRuntimeCandidateArtifactSelection?.artifactHoverKey
        && sample.runContextArtifactHoverKeys.includes(
          effectivePersistedRuntimeCandidateArtifactSelection.artifactHoverKey,
        )
      ) {
        return effectivePersistedRuntimeCandidateArtifactSelection.artifactHoverKey;
      }
      return sample.runContextArtifactHoverKeys[0] ?? null;
    },
    [activeRuntimeCandidateRunContext, effectivePersistedRuntimeCandidateArtifactSelection],
  );
  const pinnedRuntimeCandidateClauseDiffItems = useMemo(
    () => buildRunSurfaceCollectionQueryBuilderClauseDiffItems(
      pinnedRuntimeCandidateOriginTrace?.editorClause ?? null,
      editorClauseState,
    ),
    [editorClauseState, pinnedRuntimeCandidateOriginTrace],
  );
  useEffect(() => {
    if (!activeRuntimeCandidateRunContext) {
      setPersistedRuntimeCandidateArtifactSelection(null);
      return;
    }
    if (activeRuntimeCandidateRunContext.artifactHoverKey) {
      const artifactHoverKey = activeRuntimeCandidateRunContext.artifactHoverKey;
      if (activeRuntimeCandidateMatchKeys.length) {
        setPersistedRuntimeCandidateArtifactSelection((current) => {
          if (
            current
            && current.artifactHoverKey === artifactHoverKey
            && isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface(
              current,
              activeRuntimeCandidateRunContext,
            )
            && current.sampleKeys.length === activeRuntimeCandidateMatchKeys.length
            && current.sampleKeys.every((key, index) => key === activeRuntimeCandidateMatchKeys[index])
          ) {
            return current;
          }
          return {
            artifactHoverKey,
            componentKey: activeRuntimeCandidateRunContext.componentKey,
            runId: activeRuntimeCandidateRunContext.runId,
            sampleKeys: activeRuntimeCandidateMatchKeys,
            section: activeRuntimeCandidateRunContext.section,
            subFocusKey: activeRuntimeCandidateRunContext.subFocusKey,
          };
        });
      } else {
        setPersistedRuntimeCandidateArtifactSelection((current) =>
          current
          && current.artifactHoverKey === artifactHoverKey
          && isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface(
            current,
            activeRuntimeCandidateRunContext,
          )
            ? null
            : current,
        );
      }
      return;
    }
    setPersistedRuntimeCandidateArtifactSelection((current) =>
      current
      && isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface(
        current,
        activeRuntimeCandidateRunContext,
      )
        ? current
        : null,
    );
  }, [
    activeRuntimeCandidateMatchKeys,
    activeRuntimeCandidateRunContext,
  ]);
  useEffect(() => {
    if (effectiveRuntimeCandidateSelectionKeys.length === 1) {
      if (effectiveRuntimeCandidateSelectionKeys[0] !== focusedRuntimeCandidateSampleKey) {
        setFocusedRuntimeCandidateSampleKey(effectiveRuntimeCandidateSelectionKeys[0]);
      }
      return;
    }
    if (
      focusedRuntimeCandidateSampleKey
      && !effectiveRuntimeCandidateSelectionKeys.includes(focusedRuntimeCandidateSampleKey)
    ) {
      setFocusedRuntimeCandidateSampleKey(null);
    }
  }, [
    effectiveRuntimeCandidateSelectionKeys,
    focusedRuntimeCandidateSampleKey,
  ]);
  useEffect(() => {
    if (!focusedRuntimeCandidateSampleKey) {
      return;
    }
    const stillExists = allRuntimeCandidateSamples.some(
      (sample) => buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample) === focusedRuntimeCandidateSampleKey,
    );
    if (!stillExists) {
      setFocusedRuntimeCandidateSampleKey(null);
    }
  }, [allRuntimeCandidateSamples, focusedRuntimeCandidateSampleKey]);
  useEffect(() => {
    if (
      pinnedRuntimeCandidateClauseOriginKey
      && !runtimeCandidateTraceByKey.has(pinnedRuntimeCandidateClauseOriginKey)
    ) {
      setPinnedRuntimeCandidateClauseOriginKey(null);
    }
  }, [pinnedRuntimeCandidateClauseOriginKey, runtimeCandidateTraceByKey]);
  useEffect(() => {
    if (
      !persistedRuntimeCandidateArtifactSelection
      || persistedRuntimeCandidateArtifactSelection.sampleKeys.some((key) =>
        allRuntimeCandidateSamples.some(
          (sample) => buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample) === key,
        ))
    ) {
      return;
    }
    setPersistedRuntimeCandidateArtifactSelection(null);
  }, [allRuntimeCandidateSamples, persistedRuntimeCandidateArtifactSelection]);
  const linkedRuntimeCandidateTraceKeys = useMemo(() => {
    const keys = new Set<string>();
    if (pinnedRuntimeCandidateClauseOriginKey && editorClauseState) {
      keys.add(pinnedRuntimeCandidateClauseOriginKey);
    }
    activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations.forEach((entry) => {
      entry.runtimeCandidateTraces.forEach((trace) => {
        if (
          (focusedRuntimeCandidateSampleKey && trace.allValues.some(doesRuntimeCandidateSampleMatchFocusedKey))
          || (
          (activeRuntimeCandidateRunContext && trace.allValues.some(doesRuntimeCandidateSampleMatchActiveContext))
          || (effectivePersistedRuntimeCandidateArtifactSelection
            && trace.allValues.some(doesRuntimeCandidateSampleMatchPersistedArtifactSelection))
          || doesRuntimeCandidateTraceMatchEditorClause(trace)
          )
        ) {
          keys.add(buildRuntimeCandidateTraceDrillthroughKey("focused_chain", entry.stepIndex, trace));
        }
      });
    });
    if (activePredicateRefReplayApplyConflictSimulationFocusedChainEntry) {
      activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.runtimeCandidateTraces.forEach((trace) => {
        if (
          (focusedRuntimeCandidateSampleKey && trace.allValues.some(doesRuntimeCandidateSampleMatchFocusedKey))
          || (
          (activeRuntimeCandidateRunContext && trace.allValues.some(doesRuntimeCandidateSampleMatchActiveContext))
          || (effectivePersistedRuntimeCandidateArtifactSelection
            && trace.allValues.some(doesRuntimeCandidateSampleMatchPersistedArtifactSelection))
          || doesRuntimeCandidateTraceMatchEditorClause(trace)
          )
        ) {
          keys.add(
            buildRuntimeCandidateTraceDrillthroughKey(
              "active_replay",
              activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.stepIndex,
              trace,
            ),
          );
        }
      });
    }
    return Array.from(keys);
  }, [
    activePredicateRefReplayApplyConflictSimulationFocusedChainEntry,
    activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations,
    activeRuntimeCandidateRunContext,
    buildRuntimeCandidateTraceDrillthroughKey,
    effectivePersistedRuntimeCandidateArtifactSelection,
    editorClauseState,
    doesRuntimeCandidateSampleMatchActiveContext,
    doesRuntimeCandidateSampleMatchFocusedKey,
    doesRuntimeCandidateSampleMatchPersistedArtifactSelection,
    doesRuntimeCandidateTraceMatchEditorClause,
    focusedRuntimeCandidateSampleKey,
    pinnedRuntimeCandidateClauseOriginKey,
  ]);
  useEffect(() => {
    if (!linkedRuntimeCandidateTraceKeys.length) {
      return;
    }
    setRuntimeCandidateTraceDrillthroughByKey((current) => {
      let changed = false;
      const next = { ...current };
      linkedRuntimeCandidateTraceKeys.forEach((key) => {
        if (!next[key]) {
          next[key] = true;
          changed = true;
        }
      });
      return changed ? next : current;
    });
  }, [linkedRuntimeCandidateTraceKeys]);
  useEffect(() => {
    if (
      !predicateRefReplayApplyConflictSimulationConflictId
      || activePredicateRefReplayApplyConflictSimulationReview
    ) {
      return;
    }
    setPredicateRefReplayApplyConflictSimulationConflictId(null);
  }, [
    activePredicateRefReplayApplyConflictSimulationReview,
    predicateRefReplayApplyConflictSimulationConflictId,
  ]);
  const focusReplayApplyConflictSimulationTrace = useCallback(
    (
      groupKey: string,
      conflictId?: string | null,
    ) => {
      if (!simulatedCoordinationGroups.some((group) => group.key === groupKey)) {
        return;
      }
      setPredicateRefReplayApplyConflictSimulationConflictId(conflictId ?? null);
      setBundleCoordinationSimulationScope(groupKey);
      setBundleCoordinationSimulationReplayGroupFilter(groupKey);
      setBundleCoordinationSimulationReplayActionTypeFilter("all");
      setBundleCoordinationSimulationReplayEdgeFilter("all");
      setBundleCoordinationSimulationPolicy((current) => current === "current" ? "manual_resolution" : current);
      const matchingReplayStepIndex =
        simulatedPredicateRefSolverReplayAttributionByGroupKey[groupKey]?.stepIndex
        ?? simulatedPredicateRefSolverReplay.findIndex((step) =>
          step.actions.some((action) => action.groupKey === groupKey));
      setBundleCoordinationSimulationReplayIndex(matchingReplayStepIndex >= 0 ? matchingReplayStepIndex : 0);
      bundleCoordinationSimulationPanelRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    },
    [
      simulatedCoordinationGroups,
      simulatedPredicateRefSolverReplay,
      simulatedPredicateRefSolverReplayAttributionByGroupKey,
    ],
  );
  const focusRuntimeCandidateReplayTrace = useCallback((params: {
    diffItemKey?: string | null;
    groupKey?: string | null;
    sampleKey?: string | null;
    stepIndex: number;
    traceKey: string;
  }) => {
    const { diffItemKey = null, groupKey = null, sampleKey = null, stepIndex, traceKey } = params;
    if (groupKey) {
      setBundleCoordinationSimulationReplayGroupFilter(groupKey);
    }
    setBundleCoordinationSimulationReplayIndex(stepIndex >= 0 ? stepIndex : 0);
    setRuntimeCandidateTraceDrillthroughByKey((current) => ({
      ...current,
      [traceKey]: true,
    }));
    setClauseReevaluationPreviewSelection({
      diffItemKey,
      groupKey,
      traceKey,
    });
    if (sampleKey) {
      setFocusedRuntimeCandidateSampleKey(sampleKey);
      const sample = runtimeCandidateSampleByKey.get(sampleKey) ?? null;
      if (
        sample
        && onFocusRuntimeCandidateRunContext
        && sample.runContextSection
        && sample.runContextComponentKey
      ) {
        onFocusRuntimeCandidateRunContext(sample, {
          artifactHoverKey: resolveRuntimeCandidateSampleArtifactHoverKey(sample),
        });
      }
    }
    bundleCoordinationSimulationPanelRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }, [
    onFocusRuntimeCandidateRunContext,
    resolveRuntimeCandidateSampleArtifactHoverKey,
    runtimeCandidateSampleByKey,
  ]);
  useEffect(() => {
    if (!activePredicateRefReplayApplyConflictSimulationGroupKeys.length) {
      return;
    }
    const primaryGroupKey = activePredicateRefReplayApplyConflictSimulationGroupKeys[0];
    if (
      bundleCoordinationSimulationScope === "all"
      || !activePredicateRefReplayApplyConflictSimulationGroupKeys.includes(bundleCoordinationSimulationScope)
    ) {
      setBundleCoordinationSimulationScope(primaryGroupKey);
    }
    if (
      bundleCoordinationSimulationReplayGroupFilter === "all"
      || !activePredicateRefReplayApplyConflictSimulationGroupKeys.includes(bundleCoordinationSimulationReplayGroupFilter)
    ) {
      setBundleCoordinationSimulationReplayGroupFilter(primaryGroupKey);
    }
    const matchingReplayStepIndex = simulatedPredicateRefSolverReplay.findIndex((step) =>
      step.actions.some((action) =>
        activePredicateRefReplayApplyConflictSimulationGroupKeys.includes(action.groupKey)));
    if (
      matchingReplayStepIndex >= 0
      && !activeSimulatedPredicateRefSolverReplayStep?.actions.some((action) =>
        activePredicateRefReplayApplyConflictSimulationGroupKeys.includes(action.groupKey))
    ) {
      setBundleCoordinationSimulationReplayIndex(matchingReplayStepIndex);
    }
  }, [
    activePredicateRefReplayApplyConflictSimulationGroupKeys,
    activeSimulatedPredicateRefSolverReplayStep,
    bundleCoordinationSimulationReplayGroupFilter,
    bundleCoordinationSimulationScope,
    simulatedPredicateRefSolverReplay,
  ]);
  const activePredicateRefReplayApplyConflictSimulationSelectionSignature = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationReview
        ? JSON.stringify(
            Object.entries(activePredicateRefReplayApplyConflictSimulationReview.selectedSources)
              .sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey)),
          )
        : ""
    ),
    [activePredicateRefReplayApplyConflictSimulationReview],
  );
  useEffect(() => {
    if (
      !activePredicateRefReplayApplyConflictSimulationReview
      || !simulatedPredicateRefSolverReplay.length
    ) {
      return;
    }
    const preferredGroupKey = activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey
      ?? (
        bundleCoordinationSimulationReplayGroupFilter !== "all"
        && simulatedCoordinationGroups.some((group) => group.key === bundleCoordinationSimulationReplayGroupFilter)
          ? bundleCoordinationSimulationReplayGroupFilter
          : activePredicateRefReplayApplyConflictSimulationGroupKeys[0] ?? null
      );
    if (!preferredGroupKey) {
      return;
    }
    if (bundleCoordinationSimulationReplayGroupFilter !== preferredGroupKey) {
      setBundleCoordinationSimulationReplayGroupFilter(preferredGroupKey);
    }
    if (activePredicateRefReplayApplyConflictSimulationFocusedGroupKey) {
      if (bundleCoordinationSimulationReplayActionTypeFilter !== "all") {
        setBundleCoordinationSimulationReplayActionTypeFilter("all");
      }
      if (bundleCoordinationSimulationReplayEdgeFilter !== "all") {
        setBundleCoordinationSimulationReplayEdgeFilter("all");
      }
    }
    const attributedReplayStep = simulatedPredicateRefSolverReplayAttributionByGroupKey[preferredGroupKey] ?? null;
    const chainStepIndices = attributedReplayStep?.chain.map((entry) => entry.stepIndex) ?? [];
    const nextIndex = chainStepIndices.length
      ? (
          chainStepIndices.includes(activeSimulatedPredicateRefSolverReplayIndex)
            ? activeSimulatedPredicateRefSolverReplayIndex
            : chainStepIndices[0]
        )
      : (
          attributedReplayStep?.stepIndex ?? simulatedPredicateRefSolverReplay.findIndex((step) =>
            step.actions.some((action) => action.groupKey === preferredGroupKey))
        );
    if (nextIndex < 0) {
      return;
    }
    if (nextIndex === activeSimulatedPredicateRefSolverReplayIndex) {
      return;
    }
    setBundleCoordinationSimulationReplayIndex(nextIndex >= 0 ? nextIndex : 0);
  }, [
    activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey,
    activePredicateRefReplayApplyConflictSimulationGroupKeys,
    activePredicateRefReplayApplyConflictSimulationReview,
    activePredicateRefReplayApplyConflictSimulationSelectionSignature,
    activeSimulatedPredicateRefSolverReplayIndex,
    bundleCoordinationSimulationReplayActionTypeFilter,
    bundleCoordinationSimulationReplayEdgeFilter,
    bundleCoordinationSimulationReplayGroupFilter,
    simulatedCoordinationGroups,
    simulatedPredicateRefSolverReplayAttributionByGroupKey,
    simulatedPredicateRefSolverReplay,
  ]);
  useEffect(() => {
    setBundleCoordinationSimulationPromotionDecisionsByGroupKey({});
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey({});
    setBundleCoordinationSimulationApprovalOpen(false);
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    bundleCoordinationSimulationReplayGroupFilter,
    bundleCoordinationSimulationReplayActionTypeFilter,
    bundleCoordinationSimulationReplayEdgeFilter,
    activeSimulatedPredicateRefSolverReplayIndex,
    selectedRefTemplate?.id,
  ]);
  const simulatedPredicateRefReplayPromotionDraft = useMemo(() => {
    type PromotionGroup = ReturnType<typeof groupRunSurfaceCollectionQueryBuilderTemplateParameters>[number];
    const targetSelections = new Map<string, {
      group: PromotionGroup;
      bundlesByKey: Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState>;
    }>();
    activeSimulatedPredicateRefSolverReplayFilteredActions.forEach((action) => {
      action.dependencyEdges.forEach((edge) => {
        if (
          bundleCoordinationSimulationReplayEdgeFilter !== "all"
          && edge.key !== bundleCoordinationSimulationReplayEdgeFilter
        ) {
          return;
        }
        const group = simulatedCoordinationGroups.find((candidate) => candidate.key === edge.targetGroupKey);
        if (!group) {
          return;
        }
        const bundle =
          getSortedTemplateGroupPresetBundles(group.presetBundles).find(
            (candidate) => candidate.key === edge.targetBundleKey,
          ) ?? null;
        if (!bundle) {
          return;
        }
        const existing = targetSelections.get(group.key);
        if (existing) {
          existing.bundlesByKey.set(bundle.key, bundle);
          return;
        }
        targetSelections.set(group.key, {
          group,
          bundlesByKey: new Map([[bundle.key, bundle]]),
        });
      });
    });
    const promotableSelections: Array<{
      group: PromotionGroup;
      bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState;
    }> = [];
    const conflicts: Array<{
      groupLabel: string;
      bundleLabels: string[];
    }> = [];
    targetSelections.forEach(({ group, bundlesByKey }) => {
      const bundles = Array.from(bundlesByKey.values());
      if (bundles.length === 1) {
        promotableSelections.push({
          group,
          bundle: bundles[0],
        });
        return;
      }
      conflicts.push({
        groupLabel: group.label,
        bundleLabels: bundles.map((bundle) => bundle.label),
      });
    });
    return {
      promotableSelections,
      conflicts,
    };
  }, [
    activeSimulatedPredicateRefSolverReplayFilteredActions,
    bundleCoordinationSimulationReplayEdgeFilter,
    getSortedTemplateGroupPresetBundles,
    simulatedCoordinationGroups,
  ]);
  const simulatedPredicateRefReplayPromotionPreviewRows = useMemo(
    () => simulatedPredicateRefReplayPromotionDraft.promotableSelections.map(({ group, bundle }) => {
      const currentBundleKey =
        coordinatedPredicateRefGroupBundleState.resolvedSelectionsByGroupKey[group.key] ?? "";
      const simulatedBundleKey =
        simulatedPredicateRefGroupBundleState?.resolvedSelectionsByGroupKey[group.key] ?? "";
      const currentBundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find((candidate) => candidate.key === currentBundleKey)
        ?? null;
      const simulatedBundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find((candidate) => candidate.key === simulatedBundleKey)
        ?? null;
      const currentStatus =
        coordinatedPredicateRefGroupBundleState.policyTraceByGroupKey[group.key]?.statusLabel ?? "Idle";
      const simulatedStatus =
        simulatedPredicateRefGroupBundleState?.policyTraceByGroupKey[group.key]?.statusLabel ?? "Idle";
      return {
        group,
        promotedBundle: bundle,
        currentBundleLabel: currentBundle?.label ?? "No bundle",
        simulatedBundleLabel: simulatedBundle?.label ?? "No bundle",
        currentStatus,
        simulatedStatus,
        matchesSimulation: simulatedBundle?.key === bundle.key,
        changesCurrent: currentBundle?.key !== bundle.key,
      };
    }),
    [
      coordinatedPredicateRefGroupBundleState.policyTraceByGroupKey,
      coordinatedPredicateRefGroupBundleState.resolvedSelectionsByGroupKey,
      getSortedTemplateGroupPresetBundles,
      simulatedPredicateRefGroupBundleState,
      simulatedPredicateRefReplayPromotionDraft.promotableSelections,
    ],
  );
  const stagedSimulatedPredicateRefReplayPromotionSelections = useMemo(
    () => simulatedPredicateRefReplayPromotionPreviewRows.filter((row) =>
      bundleCoordinationSimulationPromotionDecisionsByGroupKey[row.group.key] ?? true,
    ),
    [
      bundleCoordinationSimulationPromotionDecisionsByGroupKey,
      simulatedPredicateRefReplayPromotionPreviewRows,
    ],
  );
  const visibleSimulatedPredicateRefReplayApprovalRows = useMemo(
    () => (
      bundleCoordinationSimulationApprovalDiffOnly
        ? stagedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
            row.changesCurrent || !row.matchesSimulation,
          )
        : stagedSimulatedPredicateRefReplayPromotionSelections
    ),
    [
      bundleCoordinationSimulationApprovalDiffOnly,
      stagedSimulatedPredicateRefReplayPromotionSelections,
    ],
  );
  const approvedSimulatedPredicateRefReplayPromotionSelections = useMemo(
    () => stagedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
      bundleCoordinationSimulationApprovalDecisionsByGroupKey[row.group.key] ?? true,
    ),
    [
      bundleCoordinationSimulationApprovalDecisionsByGroupKey,
      stagedSimulatedPredicateRefReplayPromotionSelections,
    ],
  );
  const approvedSimulatedPredicateRefReplayPromotionSummary = useMemo(() => ({
    total: approvedSimulatedPredicateRefReplayPromotionSelections.length,
    changesCurrentCount: approvedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
      row.changesCurrent,
    ).length,
    matchesSimulationCount: approvedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
      row.matchesSimulation,
    ).length,
  }), [approvedSimulatedPredicateRefReplayPromotionSelections]);
  useEffect(() => {
    if (
      !bundleCoordinationSimulationApprovalOpen
      || !selectedRefTemplate
      || !approvedSimulatedPredicateRefReplayPromotionSelections.length
    ) {
      setBundleCoordinationSimulationFinalSummaryOpen(false);
    }
  }, [
    approvedSimulatedPredicateRefReplayPromotionSelections,
    bundleCoordinationSimulationApprovalOpen,
    selectedRefTemplate,
  ]);
  useEffect(() => {
    if (
      bundleCoordinationSimulationReplayActionTypeFilter !== "all"
      && !availableSimulatedPredicateRefSolverReplayActionTypes.includes(bundleCoordinationSimulationReplayActionTypeFilter)
    ) {
      setBundleCoordinationSimulationReplayActionTypeFilter("all");
    }
  }, [
    availableSimulatedPredicateRefSolverReplayActionTypes,
    bundleCoordinationSimulationReplayActionTypeFilter,
  ]);
  useEffect(() => {
    if (
      bundleCoordinationSimulationReplayEdgeFilter !== "all"
      && !availableSimulatedPredicateRefSolverReplayEdges.some((edge) => edge.key === bundleCoordinationSimulationReplayEdgeFilter)
    ) {
      setBundleCoordinationSimulationReplayEdgeFilter("all");
    }
  }, [
    availableSimulatedPredicateRefSolverReplayEdges,
    bundleCoordinationSimulationReplayEdgeFilter,
  ]);
  const simulatedPredicateRefGroupClauseReevaluationProjectionByGroupKey = useMemo(() => {
    if (!activePredicateRefReplayApplyConflictSimulationFocusedGroupKey) {
      return {} as Record<string, {
        changedCandidateCount: number;
        previewTraceCount: number;
        projectedTraces: Array<{
          candidateAccessor: string;
          candidatePath: string;
          changedCandidateCount: number;
          diffItems: RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem[];
          editorClause: HydratedRunSurfaceCollectionQueryBuilderState | null;
          focusableDiffSampleKeysByItemKey: Record<string, string | null>;
          focusableSampleKeys: string[];
          groupKey: string;
          drillthroughKey: string;
          key: string;
          matchedCandidateLabel: string;
          matchedRunLabel: string;
          primarySampleKey: string | null;
          stepIndex: number;
          stepLabel: string;
        }>;
        tracesWithChangesCount: number;
      }>;
    }
    const projectedTraces = activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations.flatMap((entry) =>
      entry.runtimeCandidateTraces.flatMap((candidateTrace) => {
        const drillthroughKey = buildRuntimeCandidateTraceDrillthroughKey(
          "focused_chain",
          entry.stepIndex,
          candidateTrace,
        );
        const {
          traceReevaluationPreview,
          traceReevaluationPreviewDiffItems,
        } = buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection({
          candidateTrace,
          contracts,
          drillthroughKey,
          editorClauseState,
          pinnedRuntimeCandidateClauseDiffItems,
          pinnedRuntimeCandidateClauseOriginKey,
          runtimeRuns,
        });
        if (!traceReevaluationPreview) {
          return [];
        }
        const matchedRunCount = traceReevaluationPreview.runOutcomes.filter((outcome) => outcome.result).length;
        const originalSamplesByKey = new Map(
          candidateTrace.allValues.map((sample) => [
            buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
            sample,
          ] as const),
        );
        return [{
          candidateAccessor: candidateTrace.candidateAccessor,
          candidatePath: candidateTrace.candidatePath,
          changedCandidateCount: traceReevaluationPreviewDiffItems.length,
          diffItems: traceReevaluationPreviewDiffItems,
          editorClause: candidateTrace.editorClause,
          focusableDiffSampleKeysByItemKey: Object.fromEntries(
            traceReevaluationPreviewDiffItems.map((item) => [
              item.key,
              originalSamplesByKey.has(item.key) ? item.key : null,
            ] as const),
          ),
          focusableSampleKeys: Array.from(
            new Set(
              traceReevaluationPreviewDiffItems.flatMap((item) =>
                originalSamplesByKey.has(item.key) ? [item.key] : []),
            ),
          ),
          groupKey: activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
          drillthroughKey,
          key: `${drillthroughKey}:simulation_projection`,
          matchedCandidateLabel:
            `${traceReevaluationPreview.sampleMatchCount}/${traceReevaluationPreview.sampleTotalCount} matched`,
          matchedRunLabel:
            `${matchedRunCount}/${traceReevaluationPreview.runOutcomes.length} runs true`,
          primarySampleKey:
            traceReevaluationPreviewDiffItems.find((item) => originalSamplesByKey.has(item.key))?.key
            ?? (
              candidateTrace.allValues[0]
                ? buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(candidateTrace.allValues[0])
                : null
            ),
          stepIndex: entry.stepIndex,
          stepLabel: entry.stepLabel,
        }];
      }),
    );
    if (!projectedTraces.length) {
      return {} as Record<string, {
        changedCandidateCount: number;
        previewTraceCount: number;
        projectedTraces: Array<{
          candidateAccessor: string;
          candidatePath: string;
          changedCandidateCount: number;
          diffItems: RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem[];
          editorClause: HydratedRunSurfaceCollectionQueryBuilderState | null;
          focusableDiffSampleKeysByItemKey: Record<string, string | null>;
          focusableSampleKeys: string[];
          groupKey: string;
          drillthroughKey: string;
          key: string;
          matchedCandidateLabel: string;
          matchedRunLabel: string;
          primarySampleKey: string | null;
          stepIndex: number;
          stepLabel: string;
        }>;
        tracesWithChangesCount: number;
      }>;
    }
    return {
      [activePredicateRefReplayApplyConflictSimulationFocusedGroupKey]: {
        changedCandidateCount: projectedTraces.reduce(
          (total, trace) => total + trace.changedCandidateCount,
          0,
        ),
        previewTraceCount: projectedTraces.length,
        projectedTraces,
        tracesWithChangesCount: projectedTraces.filter((trace) => trace.changedCandidateCount > 0).length,
      },
    };
  }, [
    activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations,
    activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
    buildRuntimeCandidateTraceDrillthroughKey,
    contracts,
    editorClauseState,
    pinnedRuntimeCandidateClauseDiffItems,
    pinnedRuntimeCandidateClauseOriginKey,
    runtimeRuns,
  ]);
  const simulatedPredicateRefGroupBundleDiffs = useMemo(() => {
    if (!simulatedPredicateRefGroupBundleState) {
      return [];
    }
    return simulatedCoordinationGroups.flatMap((group) => {
      const replayAttribution = simulatedPredicateRefSolverReplayAttributionByGroupKey[group.key] ?? null;
      const currentTrace =
        coordinatedPredicateRefGroupBundleState.policyTraceByGroupKey[group.key] ?? null;
      const simulatedTrace =
        simulatedPredicateRefGroupBundleState.policyTraceByGroupKey[group.key] ?? null;
      const currentBundleKey =
        coordinatedPredicateRefGroupBundleState.resolvedSelectionsByGroupKey[group.key] ?? "";
      const simulatedBundleKey =
        simulatedPredicateRefGroupBundleState.resolvedSelectionsByGroupKey[group.key] ?? "";
      if (
        currentBundleKey === simulatedBundleKey
        && currentTrace?.statusLabel === simulatedTrace?.statusLabel
      ) {
        return [];
      }
      const currentBundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) => bundle.key === currentBundleKey)
        ?? null;
      const simulatedBundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) => bundle.key === simulatedBundleKey)
        ?? null;
      return [{
        attributedReplayDetail: replayAttribution?.detail ?? null,
        attributedReplayStepIndex: replayAttribution?.stepIndex ?? -1,
        attributedReplayStepLabel: replayAttribution?.stepLabel ?? "No replay attribution",
        attributedReplayType: replayAttribution?.type ?? null,
        clauseReevaluationProjection:
          simulatedPredicateRefGroupClauseReevaluationProjectionByGroupKey[group.key] ?? null,
        groupKey: group.key,
        groupLabel: group.label,
        currentStatus: currentTrace?.statusLabel ?? "Idle",
        simulatedStatus: simulatedTrace?.statusLabel ?? "Idle",
        currentBundleLabel: currentBundle?.label ?? "No bundle",
        simulatedBundleLabel: simulatedBundle?.label ?? "No bundle",
      }];
    });
  }, [
    coordinatedPredicateRefGroupBundleState.policyTraceByGroupKey,
    coordinatedPredicateRefGroupBundleState.resolvedSelectionsByGroupKey,
    getSortedTemplateGroupPresetBundles,
    simulatedCoordinationGroups,
    simulatedPredicateRefGroupClauseReevaluationProjectionByGroupKey,
    simulatedPredicateRefGroupBundleState,
    simulatedPredicateRefSolverReplayAttributionByGroupKey,
  ]);
  useEffect(() => {
    const projectedTraces = Object.values(simulatedPredicateRefGroupClauseReevaluationProjectionByGroupKey)
      .flatMap((projection) => projection.projectedTraces);
    if (!projectedTraces.length) {
      if (clauseReevaluationPreviewSelection.traceKey || clauseReevaluationPreviewSelection.diffItemKey) {
        setClauseReevaluationPreviewSelection({
          diffItemKey: null,
          groupKey: null,
          traceKey: null,
        });
      }
      return;
    }
    const currentTrace = clauseReevaluationPreviewSelection.traceKey
      ? projectedTraces.find((trace) => trace.drillthroughKey === clauseReevaluationPreviewSelection.traceKey) ?? null
      : null;
    const currentSelectionIsValid = Boolean(
      currentTrace
      && (
        !clauseReevaluationPreviewSelection.diffItemKey
        || currentTrace.diffItems.some((item) => item.key === clauseReevaluationPreviewSelection.diffItemKey)
      ),
    );
    const findSelectionForSampleKey = (sampleKey: string | null) => {
      if (!sampleKey) {
        return null;
      }
      for (const trace of projectedTraces) {
        const matchingDiffItem = trace.diffItems.find((item) =>
          trace.focusableDiffSampleKeysByItemKey[item.key] === sampleKey) ?? null;
        if (matchingDiffItem) {
          return {
            diffItemKey: matchingDiffItem.key,
            groupKey: trace.groupKey,
            traceKey: trace.drillthroughKey,
          } as const;
        }
        if (
          trace.primarySampleKey === sampleKey
          || trace.focusableSampleKeys.includes(sampleKey)
        ) {
          return {
            diffItemKey: null,
            groupKey: trace.groupKey,
            traceKey: trace.drillthroughKey,
          } as const;
        }
      }
      return null;
    };
    const findSelectionForSampleKeys = (sampleKeys: string[]) => {
      if (!sampleKeys.length) {
        return null;
      }
      const scoredTraces = projectedTraces
        .map((trace) => {
          const matchingDiffItem = trace.diffItems.find((item) => {
            const sampleKey = trace.focusableDiffSampleKeysByItemKey[item.key];
            return sampleKey ? sampleKeys.includes(sampleKey) : false;
          }) ?? null;
          const overlapCount = sampleKeys.filter((sampleKey) =>
            trace.primarySampleKey === sampleKey || trace.focusableSampleKeys.includes(sampleKey)).length;
          return {
            matchingDiffItem,
            overlapCount,
            trace,
          };
        })
        .filter((entry) => entry.matchingDiffItem || entry.overlapCount > 0)
        .sort((left, right) => {
          if (left.overlapCount !== right.overlapCount) {
            return right.overlapCount - left.overlapCount;
          }
          if (Boolean(left.matchingDiffItem) !== Boolean(right.matchingDiffItem)) {
            return left.matchingDiffItem ? -1 : 1;
          }
          return left.trace.stepIndex - right.trace.stepIndex;
        });
      const bestMatch = scoredTraces[0] ?? null;
      if (!bestMatch) {
        return null;
      }
      return {
        diffItemKey: bestMatch.matchingDiffItem?.key ?? null,
        groupKey: bestMatch.trace.groupKey,
        traceKey: bestMatch.trace.drillthroughKey,
      } as const;
    };
    const editorMatchedSelection =
      projectedTraces.find((trace) =>
        areHydratedRunSurfaceCollectionQueryBuilderStatesEqual(trace.editorClause, editorClauseState),
      )
      ?? null;
    const nextSelection =
      findSelectionForSampleKey(focusedRuntimeCandidateSampleKey)
      ?? findSelectionForSampleKeys(effectiveRuntimeCandidateSelectionKeys)
      ?? (
        pinnedRuntimeCandidateClauseOriginKey
          ? {
            diffItemKey: null,
            groupKey: pinnedRuntimeCandidateClauseOriginKey === currentTrace?.drillthroughKey ? currentTrace?.groupKey ?? null : null,
            traceKey: pinnedRuntimeCandidateClauseOriginKey,
          } as const
          : null
      );
    const resolvedSelection =
      nextSelection
      ?? (
        currentSelectionIsValid
          ? clauseReevaluationPreviewSelection
          : null
      )
      ?? (
        editorMatchedSelection
          ? {
              diffItemKey: null,
              groupKey: editorMatchedSelection.groupKey,
              traceKey: editorMatchedSelection.drillthroughKey,
            } as const
          : null
      )
      ?? {
        diffItemKey: null,
        groupKey: projectedTraces[0].groupKey,
        traceKey: projectedTraces[0].drillthroughKey,
    } as const;
    if (
      resolvedSelection.groupKey !== clauseReevaluationPreviewSelection.groupKey
      ||
      resolvedSelection.traceKey !== clauseReevaluationPreviewSelection.traceKey
      || resolvedSelection.diffItemKey !== clauseReevaluationPreviewSelection.diffItemKey
    ) {
      setClauseReevaluationPreviewSelection(resolvedSelection);
    }
  }, [
    clauseReevaluationPreviewSelection,
    editorClauseState,
    effectiveRuntimeCandidateSelectionKeys,
    focusedRuntimeCandidateSampleKey,
    pinnedRuntimeCandidateClauseOriginKey,
    simulatedPredicateRefGroupClauseReevaluationProjectionByGroupKey,
  ]);
  useEffect(() => {
    if (!clauseReevaluationPreviewSelection.traceKey) {
      return;
    }
    const scrollTarget =
      (
        clauseReevaluationPreviewSelection.diffItemKey
          ? clauseReevaluationPreviewDiffItemRefs.current.get(
              `${clauseReevaluationPreviewSelection.traceKey}:${clauseReevaluationPreviewSelection.diffItemKey}`,
            ) ?? null
          : null
      )
      ?? clauseReevaluationPreviewTraceRefs.current.get(clauseReevaluationPreviewSelection.traceKey)
      ?? null;
    if (!scrollTarget) {
      return;
    }
    requestAnimationFrame(() => {
      scrollTarget.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    });
  }, [
    clauseReevaluationPreviewSelection,
    simulatedPredicateRefGroupClauseReevaluationProjectionByGroupKey,
  ]);
  useEffect(() => {
    const templateId = selectedRefTemplate?.id ?? null;
    const templateKey = selectedRefTemplate?.key ?? null;
    if (!templateId) {
      lastHydratedReplayIntentTemplateIdRef.current = null;
      return;
    }
    if (lastHydratedReplayIntentTemplateIdRef.current === templateId) {
      return;
    }
    lastHydratedReplayIntentTemplateIdRef.current = templateId;
    const urlIntentState = loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl();
    const browserIntentState =
      typeof window === "undefined"
        ? null
        : readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(window.history.state);
    const nextIntent =
      urlIntentState?.templateKey === templateKey
        ? urlIntentState.intent
        : browserIntentState?.templateId === templateId
          ? browserIntentState.intent
          : loadRunSurfaceCollectionQueryBuilderReplayIntent(templateId);
    applyRunSurfaceCollectionQueryBuilderReplayIntent(nextIntent);
  }, [applyRunSurfaceCollectionQueryBuilderReplayIntent, selectedRefTemplate?.id, selectedRefTemplate?.key]);
  useEffect(() => {
    const templateId = selectedRefTemplate?.id ?? null;
    const templateKey = selectedRefTemplate?.key ?? null;
    if (!templateId) {
      return;
    }
    persistRunSurfaceCollectionQueryBuilderReplayIntent({
      ...currentRunSurfaceCollectionQueryBuilderReplayIntent,
      templateId,
    });
    if (typeof window === "undefined") {
      return;
    }
    const nextUrl = buildRunSurfaceCollectionQueryBuilderReplayIntentUrl(
      templateKey,
      currentRunSurfaceCollectionQueryBuilderReplayIntent,
    );
    const currentBrowserState = readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(window.history.state);
    const needsBrowserUpdate =
      currentBrowserState?.templateId !== templateId
      || !areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(
        currentBrowserState?.intent ?? null,
        currentRunSurfaceCollectionQueryBuilderReplayIntent,
      );
    const currentUrl = buildRunSurfaceCollectionQueryBuilderReplayIntentUrl(
      loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl()?.templateKey ?? null,
      loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl()?.intent ?? null,
    );
    if (!needsBrowserUpdate && currentUrl === nextUrl) {
      return;
    }
    setReplayIntentUrlTemplateKey(
      isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(currentRunSurfaceCollectionQueryBuilderReplayIntent)
        ? null
        : (templateKey ?? null),
    );
    const nextHistoryState = buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(
      window.history.state,
      templateId,
      currentRunSurfaceCollectionQueryBuilderReplayIntent,
    );
    window.history.replaceState(
      nextHistoryState,
      typeof document !== "undefined" ? document.title : "",
      nextUrl,
    );
  }, [
    currentRunSurfaceCollectionQueryBuilderReplayIntent,
    selectedRefTemplate?.id,
    selectedRefTemplate?.key,
  ]);
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const handleStorage = (event: StorageEvent) => {
      if (event.key !== RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY) {
        return;
      }
      const templateId = selectedRefTemplate?.id ?? null;
      if (!templateId) {
        return;
      }
      if (event.newValue === null) {
        if (!areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(
          null,
          currentRunSurfaceCollectionQueryBuilderReplayIntent,
        )) {
          applyRunSurfaceCollectionQueryBuilderReplayIntent(null);
        }
        return;
      }
      const parsedState = readRunSurfaceCollectionQueryBuilderReplayIntentStorageState(event.newValue);
      if (!parsedState || !(templateId in parsedState.intentsByTemplateId)) {
        return;
      }
      const remoteIntent = parsedState.intentsByTemplateId[templateId] ?? null;
      if (areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(
        remoteIntent,
        currentRunSurfaceCollectionQueryBuilderReplayIntent,
      )) {
        return;
      }
      applyRunSurfaceCollectionQueryBuilderReplayIntent(remoteIntent);
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, [
    applyRunSurfaceCollectionQueryBuilderReplayIntent,
    currentRunSurfaceCollectionQueryBuilderReplayIntent,
    selectedRefTemplate?.id,
  ]);
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const handlePopState = (event: PopStateEvent) => {
      const urlIntentState = loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl();
      setReplayIntentUrlTemplateKey(urlIntentState?.templateKey ?? null);
      const templateId = selectedRefTemplate?.id ?? null;
      const templateKey = selectedRefTemplate?.key ?? null;
      if (urlIntentState?.templateKey && urlIntentState.templateKey !== templateKey) {
        setPredicateRefDraftKey(urlIntentState.templateKey);
        return;
      }
      if (!templateId) {
        return;
      }
      const browserState = readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(event.state);
      const nextIntent =
        urlIntentState?.templateKey === templateKey
          ? urlIntentState.intent
          : (
              browserState && browserState.templateId === templateId
                ? browserState.intent
                : null
            );
      if (!nextIntent) {
        if (!isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(currentRunSurfaceCollectionQueryBuilderReplayIntent)) {
          applyRunSurfaceCollectionQueryBuilderReplayIntent(null);
        }
        return;
      }
      if (areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(
        nextIntent,
        currentRunSurfaceCollectionQueryBuilderReplayIntent,
      )) {
        return;
      }
      applyRunSurfaceCollectionQueryBuilderReplayIntent(nextIntent);
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [
    applyRunSurfaceCollectionQueryBuilderReplayIntent,
    currentRunSurfaceCollectionQueryBuilderReplayIntent,
    selectedRefTemplate?.id,
    selectedRefTemplate?.key,
  ]);
  useEffect(() => {
    if (!selectedRefTemplate) {
      setPredicateRefGroupAutoBundleSelections({});
      return;
    }
    const activeSelectionKeys = new Set(
      selectedRefTemplateParameterGroups.map((group) => `${selectedRefTemplate.id}:${group.key}`),
    );
    const pendingUpdates = selectedRefTemplateParameterGroups.flatMap((group) => {
      const selectionKey = `${selectedRefTemplate.id}:${group.key}`;
      if (predicateRefGroupBundleSelections[selectionKey]) {
        return [];
      }
      const nextAutoBundleKey = coordinatedPredicateRefGroupBundleState.autoSelectionsBySelectionKey[selectionKey] ?? "";
      const nextAutoBundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) => bundle.key === nextAutoBundleKey)
        ?? null;
      const currentAutoBundleKey = predicateRefGroupAutoBundleSelections[selectionKey] ?? "";
      if ((nextAutoBundle?.key ?? "") === currentAutoBundleKey) {
        return [];
      }
      return [{
        selectionKey,
        group,
        bundle: nextAutoBundle,
      }];
    });
    const needsSelectionCleanup =
      pendingUpdates.length > 0
      || Object.keys(predicateRefGroupAutoBundleSelections).some((selectionKey) =>
        !activeSelectionKeys.has(selectionKey) || Boolean(predicateRefGroupBundleSelections[selectionKey]),
      );
    if (!needsSelectionCleanup) {
      return;
    }
    if (pendingUpdates.length) {
      setPredicateRefDraftBindings((current) => {
        const next = { ...current };
        pendingUpdates.forEach(({ group, bundle }) => {
          group.parameters.forEach((parameter) => {
            delete next[parameter.key];
          });
          if (!bundle) {
            return;
          }
          group.parameters.forEach((parameter) => {
            const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim();
            if (bindingPreset) {
              next[parameter.key] = toRunSurfaceCollectionQueryBindingReferenceValue(bindingPreset);
              return;
            }
            const parameterValue = bundle.parameterValues[parameter.key];
            if (parameterValue?.trim()) {
              next[parameter.key] = parameterValue;
            }
          });
        });
        return next;
      });
    }
    setPredicateRefGroupAutoBundleSelections((current) => {
      const next: Record<string, string> = {};
      activeSelectionKeys.forEach((selectionKey) => {
        if (predicateRefGroupBundleSelections[selectionKey]) {
          return;
        }
        const pendingUpdate = pendingUpdates.find((entry) => entry.selectionKey === selectionKey);
        if (pendingUpdate) {
          if (pendingUpdate.bundle?.key) {
            next[selectionKey] = pendingUpdate.bundle.key;
          }
          return;
        }
        const currentAutoKey = current[selectionKey] ?? "";
        if (
          currentAutoKey
          && coordinatedPredicateRefGroupBundleState.autoSelectionsBySelectionKey[selectionKey] === currentAutoKey
        ) {
          next[selectionKey] = currentAutoKey;
          return;
        }
        const derivedAutoKey = coordinatedPredicateRefGroupBundleState.autoSelectionsBySelectionKey[selectionKey] ?? "";
        if (derivedAutoKey) {
          next[selectionKey] = derivedAutoKey;
        }
      });
      return next;
    });
  }, [
    coordinatedPredicateRefGroupBundleState.autoSelectionsBySelectionKey,
    predicateRefGroupAutoBundleSelections,
    predicateRefGroupBundleSelections,
    getSortedTemplateGroupPresetBundles,
    selectedRefTemplate,
    selectedRefTemplateParameterGroups,
  ]);
  const canAddPredicateRef = Boolean(
    predicateRefDraftKey
    && (
      !selectedRefTemplate
      || selectedRefTemplate.parameters.every(
        (parameter) =>
          Boolean(predicateRefDraftBindings[parameter.key]?.trim())
          || Boolean(parameter.bindingPreset.trim())
          || Boolean(parameter.defaultValue.trim()),
      )
    ),
  );
  const selectedPredicateSupportsClauseEditing = selectedPredicate?.node.kind === "clause";
  const selectedTemplateSupportsClauseEditing = selectedTemplate?.node.kind === "clause";
  const trimmedPredicateDraftKey = predicateDraftKey.trim();
  const predicateKeyConflict = Boolean(
    trimmedPredicateDraftKey
    && [...predicates, ...predicateTemplates].some((entry) =>
      entry.key === trimmedPredicateDraftKey
      && !(editorTarget.kind === "predicate" && "id" in entry && entry.id === editorTarget.predicateId),
    ),
  );
  const trimmedTemplateDraftKey = templateDraftKey.trim();
  const templateKeyConflict = Boolean(
    trimmedTemplateDraftKey
    && [...predicates, ...predicateTemplates].some((entry) =>
      entry.key === trimmedTemplateDraftKey
      && !(editorTarget.kind === "template" && "id" in entry && entry.id === editorTarget.templateId),
    ),
  );
  const predicateSaveLabel = editorTarget.kind === "predicate" ? "Update predicate" : "Save as predicate";
  const subtreePromotionLabel = editorTarget.kind === "predicate" ? "Overwrite from target subtree" : "Promote target subtree";
  const templateSaveLabel = editorTarget.kind === "template" ? "Update template" : "Save as template";
  const templatePromotionLabel = editorTarget.kind === "template" ? "Overwrite template subtree" : "Promote subtree as template";
  const selectedGroup = useMemo(
    () =>
      selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        ? null
        : findRunSurfaceCollectionQueryBuilderGroup(expressionChildren, selectedGroupId),
    [expressionChildren, selectedGroupId],
  );
  const selectedSubtreeNode = useMemo<RunSurfaceCollectionQueryBuilderChildState | null>(() => {
    if (expressionMode !== "grouped" || !expressionChildren.length) {
      return null;
    }
    if (selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID) {
      return {
        id: buildRunSurfaceCollectionQueryBuilderEntityId("group"),
        kind: "group",
        logic: groupLogic,
        negated: rootNegated,
        children: expressionChildren.map((child) => cloneRunSurfaceCollectionQueryBuilderChildState(child)),
      };
    }
    return selectedGroup ? cloneRunSurfaceCollectionQueryBuilderChildState(selectedGroup) : null;
  }, [expressionChildren, expressionMode, groupLogic, rootNegated, selectedGroup, selectedGroupId]);
  const selectedGroupLabel =
    selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
      ? "root group"
      : selectedGroup
        ? `${selectedGroup.logic.toUpperCase()} subgroup`
        : "root group";
  const clauseTemplateParameterBaseParameters = useMemo(
    () => {
      if (!editorClauseState) {
        return [];
      }
      const inferredParameters = Array.from(
        collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause(editorClauseState, contracts).values(),
      );
      return (
        editorTarget.kind === "template"
        && selectedTemplate
        && selectedTemplateSupportsClauseEditing
      )
        ? mergeRunSurfaceCollectionQueryBuilderTemplateParameters(
            inferredParameters,
            selectedTemplate.parameters,
          )
        : inferredParameters;
    },
    [contracts, editorClauseState, editorTarget.kind, selectedTemplate, selectedTemplateSupportsClauseEditing],
  );
  const subtreeTemplateParameterBaseParameters = useMemo(
    () => (
      editorTarget.kind === "template"
      && selectedTemplate
      && !selectedTemplateSupportsClauseEditing
        ? mergeRunSurfaceCollectionQueryBuilderTemplateParameters(
            collectRunSurfaceCollectionQueryBuilderTemplateParameters(
              selectedTemplate.node,
              contracts,
              predicateTemplates,
            ),
            selectedTemplate.parameters,
          )
        : []
    ),
    [
      contracts,
      editorTarget.kind,
      predicateTemplates,
      selectedTemplate,
      selectedTemplateSupportsClauseEditing,
    ],
  );
  const unsavedSubtreeTemplateParameterBaseParameters = useMemo(
    () =>
      expressionMode === "grouped" && selectedSubtreeNode
        ? collectRunSurfaceCollectionQueryBuilderTemplateParameters(
            selectedSubtreeNode,
            contracts,
            predicateTemplates,
          )
        : [],
    [contracts, expressionMode, predicateTemplates, selectedSubtreeNode],
  );
  const clauseTemplateParameterBaseGroups = useMemo(
    () =>
      mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
        clauseTemplateParameterBaseParameters,
        editorTarget.kind === "template"
        && selectedTemplate
        && selectedTemplateSupportsClauseEditing
          ? selectedTemplate.parameterGroups
          : [],
      ),
    [
      clauseTemplateParameterBaseParameters,
      editorTarget.kind,
      selectedTemplate,
      selectedTemplateSupportsClauseEditing,
    ],
  );
  const subtreeTemplateParameterBaseGroups = useMemo(
    () =>
      mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
        subtreeTemplateParameterBaseParameters,
        editorTarget.kind === "template"
        && selectedTemplate
        && !selectedTemplateSupportsClauseEditing
          ? selectedTemplate.parameterGroups
          : [],
      ),
    [
      editorTarget.kind,
      selectedTemplate,
      selectedTemplateSupportsClauseEditing,
      subtreeTemplateParameterBaseParameters,
    ],
  );
  const unsavedSubtreeTemplateParameterBaseGroups = useMemo(
    () =>
      mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
        unsavedSubtreeTemplateParameterBaseParameters,
      ),
    [unsavedSubtreeTemplateParameterBaseParameters],
  );
  const clauseTemplateParameterContextKey = useMemo(
    () => (
      editorTarget.kind === "template"
      && selectedTemplate
      && selectedTemplateSupportsClauseEditing
        ? `template:${selectedTemplate.id}`
        : "template-draft:clause"
    ),
    [editorTarget.kind, selectedTemplate, selectedTemplateSupportsClauseEditing],
  );
  const subtreeTemplateParameterContextKey = useMemo(
    () => (
      editorTarget.kind === "template"
      && selectedTemplate
      && !selectedTemplateSupportsClauseEditing
        ? `template:${selectedTemplate.id}`
        : `template-draft:subtree:${selectedGroupId}`
    ),
    [editorTarget.kind, selectedGroupId, selectedTemplate, selectedTemplateSupportsClauseEditing],
  );
  const templateParameterEditorContextKey = useMemo(
    () => (
      templateDraftAuthoringTarget === "subtree"
        ? subtreeTemplateParameterContextKey
        : clauseTemplateParameterContextKey
    ),
    [
      clauseTemplateParameterContextKey,
      subtreeTemplateParameterContextKey,
      templateDraftAuthoringTarget,
    ],
  );
  const applyTemplateParameterDraftDefaults = useCallback(
    (
      baseParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[],
      contextKey: string,
    ) => {
      const labelOverrides = templateParameterDraftLabelsByContext[contextKey] ?? {};
      const groupOverrides = templateParameterDraftGroupsByContext[contextKey] ?? {};
      const helpNoteOverrides = templateParameterDraftHelpNotesByContext[contextKey] ?? {};
      const bindingPresetOverrides = templateParameterDraftBindingPresetsByContext[contextKey] ?? {};
      const order = templateParameterDraftOrderByContext[contextKey] ?? [];
      const parameterMap = new Map(
        baseParameters.map((parameter) => [parameter.key, parameter] as const),
      );
      const orderedKeys = [
        ...order.filter((key) => parameterMap.has(key)),
        ...baseParameters
          .map((parameter) => parameter.key)
          .filter((key) => !order.includes(key)),
      ];
      return orderedKeys.flatMap((key) => {
        const parameter = parameterMap.get(key);
        if (!parameter) {
          return [];
        }
        return [{
          ...parameter,
          label: labelOverrides[key]?.trim() || parameter.label,
          customLabel: labelOverrides[key] ?? parameter.customLabel ?? "",
          groupName: groupOverrides[key] ?? parameter.groupName ?? "",
          helpNote: helpNoteOverrides[key] ?? parameter.helpNote ?? "",
          defaultValue:
            templateParameterDraftDefaultsByContext[contextKey]?.[key]
            ?? parameter.defaultValue
            ?? "",
          bindingPreset:
            bindingPresetOverrides[key]
            ?? parameter.bindingPreset
            ?? "",
        }];
      });
    },
    [
      templateParameterDraftBindingPresetsByContext,
      templateParameterDraftDefaultsByContext,
      templateParameterDraftGroupsByContext,
      templateParameterDraftHelpNotesByContext,
      templateParameterDraftLabelsByContext,
      templateParameterDraftOrderByContext,
    ],
  );
  const applyTemplateParameterGroupDraftMetadata = useCallback(
    (
      baseGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[],
      contextKey: string,
    ) =>
      baseGroups.map((group) => {
        const groupOverride = templateParameterGroupDraftMetadataByContext[contextKey]?.[group.key];
        return {
          ...group,
          label: groupOverride?.label?.trim() || group.label,
          helpNote: groupOverride?.helpNote ?? group.helpNote,
          collapsedByDefault: groupOverride?.collapsedByDefault ?? group.collapsedByDefault,
          visibilityRule: groupOverride?.visibilityRule ?? group.visibilityRule,
          coordinationPolicy: groupOverride?.coordinationPolicy ?? group.coordinationPolicy,
          presetBundles: groupOverride?.presetBundles ?? group.presetBundles,
        };
      }),
    [templateParameterGroupDraftMetadataByContext],
  );
  const clauseEditableTemplateParameters = useMemo<RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[]>(
    () => applyTemplateParameterDraftDefaults(
      clauseTemplateParameterBaseParameters,
      clauseTemplateParameterContextKey,
    ),
    [
      applyTemplateParameterDraftDefaults,
      clauseTemplateParameterBaseParameters,
      clauseTemplateParameterContextKey,
    ],
  );
  const subtreeEditableTemplateParameters = useMemo<RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[]>(
    () =>
      applyTemplateParameterDraftDefaults(
        editorTarget.kind === "template" && !selectedTemplateSupportsClauseEditing
          ? subtreeTemplateParameterBaseParameters
          : unsavedSubtreeTemplateParameterBaseParameters,
        subtreeTemplateParameterContextKey,
      ),
    [
      applyTemplateParameterDraftDefaults,
      editorTarget.kind,
      selectedTemplateSupportsClauseEditing,
      subtreeTemplateParameterBaseParameters,
      subtreeTemplateParameterContextKey,
      unsavedSubtreeTemplateParameterBaseParameters,
    ],
  );
  const clauseEditableTemplateParameterGroups = useMemo(
    () =>
      applyTemplateParameterGroupDraftMetadata(
        clauseTemplateParameterBaseGroups,
        clauseTemplateParameterContextKey,
      ),
    [
      applyTemplateParameterGroupDraftMetadata,
      clauseTemplateParameterBaseGroups,
      clauseTemplateParameterContextKey,
    ],
  );
  const subtreeEditableTemplateParameterGroups = useMemo(
    () =>
      applyTemplateParameterGroupDraftMetadata(
        editorTarget.kind === "template" && !selectedTemplateSupportsClauseEditing
          ? subtreeTemplateParameterBaseGroups
          : unsavedSubtreeTemplateParameterBaseGroups,
        subtreeTemplateParameterContextKey,
      ),
    [
      applyTemplateParameterGroupDraftMetadata,
      editorTarget.kind,
      selectedTemplateSupportsClauseEditing,
      subtreeTemplateParameterBaseGroups,
      subtreeTemplateParameterContextKey,
      unsavedSubtreeTemplateParameterBaseGroups,
    ],
  );
  const templateParameterEditorBaseParameters = useMemo(
    () => (
      templateDraftAuthoringTarget === "subtree"
        ? (
            editorTarget.kind === "template" && !selectedTemplateSupportsClauseEditing
              ? subtreeTemplateParameterBaseParameters
              : unsavedSubtreeTemplateParameterBaseParameters
          )
        : clauseTemplateParameterBaseParameters
    ),
    [
      clauseTemplateParameterBaseParameters,
      editorTarget.kind,
      selectedTemplateSupportsClauseEditing,
      subtreeTemplateParameterBaseParameters,
      templateDraftAuthoringTarget,
      unsavedSubtreeTemplateParameterBaseParameters,
    ],
  );
  const templateParameterEditorBaseGroups = useMemo(
    () => (
      templateDraftAuthoringTarget === "subtree"
        ? (
            editorTarget.kind === "template" && !selectedTemplateSupportsClauseEditing
              ? subtreeTemplateParameterBaseGroups
              : unsavedSubtreeTemplateParameterBaseGroups
          )
        : clauseTemplateParameterBaseGroups
    ),
    [
      clauseTemplateParameterBaseGroups,
      editorTarget.kind,
      selectedTemplateSupportsClauseEditing,
      subtreeTemplateParameterBaseGroups,
      templateDraftAuthoringTarget,
      unsavedSubtreeTemplateParameterBaseGroups,
    ],
  );
  useEffect(() => {
    if (editorTarget.kind === "template") {
      setTemplateDraftAuthoringTarget(selectedTemplateSupportsClauseEditing ? "clause" : "subtree");
      return;
    }
    if (expressionMode !== "grouped" || !selectedSubtreeNode) {
      setTemplateDraftAuthoringTarget("clause");
    }
  }, [
    editorTarget.kind,
    expressionMode,
    selectedSubtreeNode,
    selectedTemplateSupportsClauseEditing,
  ]);
  const editableTemplateParameters = useMemo<RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[]>(
    () => (
      templateDraftAuthoringTarget === "subtree"
        ? subtreeEditableTemplateParameters
        : clauseEditableTemplateParameters
    ),
    [
      clauseEditableTemplateParameters,
      subtreeEditableTemplateParameters,
      templateDraftAuthoringTarget,
    ],
  );
  const editableTemplateParameterGroupMetadata = useMemo(
    () => (
      templateDraftAuthoringTarget === "subtree"
        ? subtreeEditableTemplateParameterGroups
        : clauseEditableTemplateParameterGroups
    ),
    [
      clauseEditableTemplateParameterGroups,
      subtreeEditableTemplateParameterGroups,
      templateDraftAuthoringTarget,
    ],
  );
  const editableTemplateParameterKeys = useMemo(
    () => editableTemplateParameters.map((parameter) => parameter.key),
    [editableTemplateParameters],
  );
  const editableTemplateParameterIndexMap = useMemo(
    () =>
      new Map(
        editableTemplateParameters.map((parameter, index) => [parameter.key, index] as const),
      ),
    [editableTemplateParameters],
  );
  const editableTemplateParameterGroups = useMemo(
    () => groupRunSurfaceCollectionQueryBuilderTemplateParameters(
      editableTemplateParameters,
      editableTemplateParameterGroupMetadata,
    ),
    [editableTemplateParameterGroupMetadata, editableTemplateParameters],
  );
  const canAuthorSubtreeTemplateDefaults = Boolean(
    expressionMode === "grouped"
    && selectedSubtreeNode
    && editorTarget.kind !== "template",
  );
  const hasTemplateParameterAuthoringContext = Boolean(
    templateParameterEditorBaseParameters.length || templateParameterEditorBaseGroups.length,
  );
  const updateTemplateParameterDraftDefault = useCallback(
    (contextKey: string, parameterKey: string, value: string) => {
      setTemplateParameterDraftDefaultsByContext((current) => ({
        ...current,
        [contextKey]: {
          ...(current[contextKey] ?? {}),
          [parameterKey]: value,
        },
      }));
    },
    [],
  );
  const updateTemplateParameterDraftLabel = useCallback(
    (contextKey: string, parameterKey: string, value: string) => {
      setTemplateParameterDraftLabelsByContext((current) => ({
        ...current,
        [contextKey]: {
          ...(current[contextKey] ?? {}),
          [parameterKey]: value,
        },
      }));
    },
    [],
  );
  const updateTemplateParameterDraftGroup = useCallback(
    (contextKey: string, parameterKey: string, value: string) => {
      setTemplateParameterDraftGroupsByContext((current) => ({
        ...current,
        [contextKey]: {
          ...(current[contextKey] ?? {}),
          [parameterKey]: value,
        },
      }));
    },
    [],
  );
  const updateTemplateParameterDraftHelpNote = useCallback(
    (contextKey: string, parameterKey: string, value: string) => {
      setTemplateParameterDraftHelpNotesByContext((current) => ({
        ...current,
        [contextKey]: {
          ...(current[contextKey] ?? {}),
          [parameterKey]: value,
        },
      }));
    },
    [],
  );
  const updateTemplateParameterGroupDraftMetadata = useCallback(
    (
      contextKey: string,
      groupKey: string,
      updater: (
        group: Omit<RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState, "key">,
      ) => Omit<RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState, "key">,
    ) => {
      setTemplateParameterGroupDraftMetadataByContext((current) => {
        const currentContext = current[contextKey] ?? {};
        const currentGroup = currentContext[groupKey] ?? {
          label: groupKey === "__ungrouped__" ? "Ungrouped parameters" : groupKey,
          helpNote: "",
          collapsedByDefault: false,
          visibilityRule: "always",
          coordinationPolicy: "manual_source_priority",
          presetBundles: [],
        };
        return {
          ...current,
          [contextKey]: {
            ...currentContext,
            [groupKey]: updater(currentGroup),
          },
        };
      });
    },
    [],
  );
  const renameTemplateParameterGroup = useCallback(
    (
      contextKey: string,
      group: {
        key: string;
        label: string;
        helpNote: string;
        collapsedByDefault: boolean;
        visibilityRule: "always" | "manual" | "binding_active" | "value_active";
        coordinationPolicy: "manual_source_priority" | "highest_source_priority" | "sticky_auto_selection" | "manual_resolution";
        presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
        parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
      },
      nextLabel: string,
    ) => {
      const normalizedLabel = nextLabel.trim();
      const nextGroupKey = normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey(normalizedLabel);
      setTemplateParameterDraftGroupsByContext((current) => ({
        ...current,
        [contextKey]: {
          ...(current[contextKey] ?? {}),
          ...Object.fromEntries(
            group.parameters.map((parameter) => [parameter.key, normalizedLabel]),
          ),
        },
      }));
      setTemplateParameterGroupDraftMetadataByContext((current) => {
        const currentContext = { ...(current[contextKey] ?? {}) };
        const existingGroup = currentContext[group.key] ?? {
          label: group.label,
          helpNote: group.helpNote,
          collapsedByDefault: group.collapsedByDefault,
          visibilityRule: group.visibilityRule,
          coordinationPolicy: group.coordinationPolicy,
          presetBundles: group.presetBundles,
        };
        delete currentContext[group.key];
        currentContext[nextGroupKey] = {
          ...existingGroup,
          label: normalizedLabel || "Ungrouped parameters",
        };
        Object.keys(currentContext).forEach((currentGroupKey) => {
          currentContext[currentGroupKey] = {
            ...currentContext[currentGroupKey],
            presetBundles: currentContext[currentGroupKey].presetBundles.map((bundle) => ({
              ...bundle,
              dependencies: bundle.dependencies.map((dependency) =>
                dependency.groupKey === group.key
                  ? {
                      ...dependency,
                      groupKey: nextGroupKey,
                    }
                  : dependency,
              ),
            })),
          };
        });
        return {
          ...current,
          [contextKey]: currentContext,
        };
      });
    },
    [],
  );
  const appendTemplateParameterGroupPresetBundle = useCallback(
    (
      contextKey: string,
      group: {
        key: string;
        label: string;
      },
    ) => {
      updateTemplateParameterGroupDraftMetadata(
        contextKey,
        group.key,
        (currentGroup) => ({
          ...currentGroup,
          label: currentGroup.label || group.label,
          presetBundles: [
            ...(currentGroup.presetBundles ?? []),
            {
              key: `bundle_${(currentGroup.presetBundles?.length ?? 0) + 1}`,
              label: `${group.label} preset ${(currentGroup.presetBundles?.length ?? 0) + 1}`,
              helpNote: "",
              priority: 0,
              autoSelectRule: "manual",
              dependencies: [],
              parameterValues: {},
              parameterBindingPresets: {},
            },
          ],
        }),
      );
    },
    [updateTemplateParameterGroupDraftMetadata],
  );
  const renameTemplateParameterGroupPresetBundleKey = useCallback(
    (
      contextKey: string,
      groupKey: string,
      bundleKey: string,
      nextKey: string,
    ) => {
      const normalizedNextKey = nextKey.trim();
      setTemplateParameterGroupDraftMetadataByContext((current) => {
        const currentContext = { ...(current[contextKey] ?? {}) };
        const updatedContext: Record<
          string,
          Omit<RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState, "key">
        > = {};
        Object.entries(currentContext).forEach(([currentGroupKey, currentGroup]) => {
          updatedContext[currentGroupKey] = {
            ...currentGroup,
            presetBundles: currentGroup.presetBundles.map((currentBundle) => {
              if (currentGroupKey === groupKey && currentBundle.key === bundleKey) {
                return {
                  ...currentBundle,
                  key: nextKey,
                };
              }
              if (!normalizedNextKey || normalizedNextKey === bundleKey) {
                return currentBundle;
              }
              return {
                ...currentBundle,
                dependencies: currentBundle.dependencies.map((dependency) =>
                  dependency.groupKey === groupKey && dependency.bundleKey === bundleKey
                    ? {
                        ...dependency,
                        bundleKey: normalizedNextKey,
                      }
                    : dependency,
                ),
              };
            }),
          };
        });
        return {
          ...current,
          [contextKey]: updatedContext,
        };
      });
    },
    [],
  );
  const updateTemplateParameterGroupPresetBundle = useCallback(
    (
      contextKey: string,
      groupKey: string,
      bundleKey: string,
      updater: (
        bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
      ) => RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
    ) => {
      updateTemplateParameterGroupDraftMetadata(
        contextKey,
        groupKey,
        (currentGroup) => ({
          ...currentGroup,
          presetBundles: (currentGroup.presetBundles ?? []).map((bundle) =>
            bundle.key === bundleKey ? updater(bundle) : bundle,
          ),
        }),
      );
    },
    [updateTemplateParameterGroupDraftMetadata],
  );
  const appendTemplateParameterGroupPresetBundleDependency = useCallback(
    (
      contextKey: string,
      groupKey: string,
      bundleKey: string,
      availableGroups: Array<{
        key: string;
        presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
      }>,
    ) => {
      const targetGroup =
        availableGroups.find((candidate) => candidate.key !== groupKey && candidate.presetBundles.length)
        ?? availableGroups.find((candidate) => candidate.key !== groupKey)
        ?? null;
      if (!targetGroup) {
        return;
      }
      const targetBundleKey = targetGroup.presetBundles[0]?.key ?? "";
      updateTemplateParameterGroupPresetBundle(
        contextKey,
        groupKey,
        bundleKey,
        (currentBundle) => ({
          ...currentBundle,
          dependencies: [
            ...currentBundle.dependencies,
            {
              key: `dependency_${currentBundle.dependencies.length + 1}`,
              groupKey: targetGroup.key,
              bundleKey: targetBundleKey,
            },
          ],
        }),
      );
    },
    [updateTemplateParameterGroupPresetBundle],
  );
  const updateTemplateParameterGroupPresetBundleDependency = useCallback(
    (
      contextKey: string,
      groupKey: string,
      bundleKey: string,
      dependencyKey: string,
      updater: (
        dependency: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState,
      ) => RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState,
    ) => {
      updateTemplateParameterGroupPresetBundle(
        contextKey,
        groupKey,
        bundleKey,
        (currentBundle) => ({
          ...currentBundle,
          dependencies: currentBundle.dependencies.map((dependency) =>
            dependency.key === dependencyKey ? updater(dependency) : dependency,
          ),
        }),
      );
    },
    [updateTemplateParameterGroupPresetBundle],
  );
  const removeTemplateParameterGroupPresetBundleDependency = useCallback(
    (
      contextKey: string,
      groupKey: string,
      bundleKey: string,
      dependencyKey: string,
    ) => {
      updateTemplateParameterGroupPresetBundle(
        contextKey,
        groupKey,
        bundleKey,
        (currentBundle) => ({
          ...currentBundle,
          dependencies: currentBundle.dependencies.filter((dependency) => dependency.key !== dependencyKey),
        }),
      );
    },
    [updateTemplateParameterGroupPresetBundle],
  );
  const removeTemplateParameterGroupPresetBundle = useCallback(
    (contextKey: string, groupKey: string, bundleKey: string) => {
      updateTemplateParameterGroupDraftMetadata(
        contextKey,
        groupKey,
        (currentGroup) => ({
          ...currentGroup,
          presetBundles: (currentGroup.presetBundles ?? []).filter((bundle) => bundle.key !== bundleKey),
        }),
      );
    },
    [updateTemplateParameterGroupDraftMetadata],
  );
  const updateTemplateParameterDraftBindingPreset = useCallback(
    (contextKey: string, parameterKey: string, value: string) => {
      setTemplateParameterDraftBindingPresetsByContext((current) => ({
        ...current,
        [contextKey]: {
          ...(current[contextKey] ?? {}),
          [parameterKey]: value,
        },
      }));
    },
    [],
  );
  const moveTemplateParameterDraftOrder = useCallback(
    (contextKey: string, parameterKey: string, direction: "up" | "down", visibleKeys: string[]) => {
      setTemplateParameterDraftOrderByContext((current) => {
        const existingOrder = current[contextKey] ?? visibleKeys;
        const nextOrder = [
          ...existingOrder.filter((key) => visibleKeys.includes(key)),
          ...visibleKeys.filter((key) => !existingOrder.includes(key)),
        ];
        const currentIndex = nextOrder.indexOf(parameterKey);
        if (currentIndex === -1) {
          return current;
        }
        const targetIndex = direction === "up" ? currentIndex - 1 : currentIndex + 1;
        if (targetIndex < 0 || targetIndex >= nextOrder.length) {
          return current;
        }
        const reordered = [...nextOrder];
        const [item] = reordered.splice(currentIndex, 1);
        reordered.splice(targetIndex, 0, item);
        return {
          ...current,
          [contextKey]: reordered,
        };
      });
    },
    [],
  );
  const nestedTemplateBindingParameters = useMemo<RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[]>(
    () => {
      if (editorTarget.kind === "template") {
        return editableTemplateParameters;
      }
      if (
        expressionMode === "grouped"
        && selectedGroupId !== RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        && selectedSubtreeNode
      ) {
        return collectRunSurfaceCollectionQueryBuilderTemplateParameters(
          selectedSubtreeNode,
          contracts,
          predicateTemplates,
        );
      }
      return clauseTemplateParameterBaseParameters;
    },
    [
      clauseTemplateParameterBaseParameters,
      contracts,
      editableTemplateParameters,
      editorTarget.kind,
      expressionMode,
      predicateTemplates,
      selectedGroupId,
      selectedSubtreeNode,
    ],
  );
  const nestedTemplateBindingParameterKeys = useMemo(
    () => nestedTemplateBindingParameters.map((parameter) => parameter.key),
    [nestedTemplateBindingParameters],
  );

  const updateGroupSettings = (
    groupId: string,
    updater: (group: RunSurfaceCollectionQueryBuilderGroupState) => RunSurfaceCollectionQueryBuilderGroupState,
  ) => {
    setExpressionChildren((current) => updateRunSurfaceCollectionQueryBuilderGroup(current, groupId, updater));
  };

  const renderExpressionChild = (
    child: RunSurfaceCollectionQueryBuilderChildState,
    depth = 0,
  ): ReactNode => {
    if (child.kind === "clause") {
      const isActiveClause = editorTarget.kind === "expression_clause" && editorTarget.childId === child.id;
      return (
        <div
          className={`run-surface-query-builder-domain-card ${isActiveClause ? "is-active" : ""}`.trim()}
          key={child.id}
        >
          <div className="run-surface-query-builder-card-head">
            <strong>Clause</strong>
            <span>{child.clause.quantifier}</span>
          </div>
          <p className="run-note">{formatRunSurfaceCollectionQueryBuilderClauseSummary(child.clause, contracts)}</p>
          <div className="run-surface-query-builder-actions">
            <button
              className="ghost-button"
              onClick={() => {
                setEditorTarget({ kind: "expression_clause", childId: child.id });
                setPredicateDraftKey("");
                setTemplateDraftKey("");
                setEditorFromClause(child.clause);
              }}
              type="button"
            >
              Edit clause
            </button>
            <button
              className="ghost-button"
              onClick={() => removeExpressionChild(child.id)}
              type="button"
            >
              Remove
            </button>
          </div>
        </div>
      );
    }
    if (child.kind === "predicate_ref") {
      const referencedTemplate =
        predicateTemplates.find((template) => template.key === child.predicateKey) ?? null;
      return (
        <div className="run-surface-query-builder-domain-card" key={child.id}>
          <div className="run-surface-query-builder-card-head">
            <strong>Predicate ref</strong>
            <span>{referencedTemplate ? "template" : child.negated ? "negated" : "linked"}</span>
          </div>
          <p className="run-note">{formatRunSurfaceCollectionQueryBuilderChildSummary(child, contracts)}</p>
          <div className="run-surface-query-builder-actions">
            <button
              className="ghost-button"
              onClick={() => togglePredicateRefNegation(child.id)}
              type="button"
            >
              {child.negated ? "Clear negation" : "Negate ref"}
            </button>
            <button
              className="ghost-button"
              onClick={() => removeExpressionChild(child.id)}
              type="button"
            >
              Remove
            </button>
          </div>
        </div>
      );
    }
    const isSelectedGroup = selectedGroupId === child.id;
    return (
      <div
        className={`run-surface-query-builder-group-card ${isSelectedGroup ? "is-selected" : ""}`.trim()}
        key={child.id}
        style={{ "--query-group-depth": depth } as CSSProperties}
      >
        <div className="run-surface-query-builder-card-head">
          <strong>Subgroup</strong>
          <span>{child.logic.toUpperCase()}</span>
        </div>
        <div className="run-surface-query-builder-inline-grid">
          <label className="run-surface-query-builder-control">
            <span>Logic</span>
            <select
              onChange={(event) =>
                updateGroupSettings(child.id, (group) => ({
                  ...group,
                  logic: event.target.value as "and" | "or",
                }))}
              value={child.logic}
            >
              <option value="and">and</option>
              <option value="or">or</option>
            </select>
          </label>
          <label className="run-surface-query-builder-checkbox">
            <input
              checked={child.negated}
              onChange={(event) =>
                updateGroupSettings(child.id, (group) => ({
                  ...group,
                  negated: event.target.checked,
                }))}
              type="checkbox"
            />
            <span>Negated</span>
          </label>
        </div>
        <div className="run-surface-query-builder-actions">
          <button
            className={`ghost-button ${isSelectedGroup ? "is-active" : ""}`.trim()}
            onClick={() => setSelectedGroupId(child.id)}
            type="button"
          >
            {isSelectedGroup ? "Targeting this group" : "Target this group"}
          </button>
          <button
            className="ghost-button"
            onClick={() => removeExpressionChild(child.id)}
            type="button"
          >
            Remove group
          </button>
        </div>
        <div className="run-surface-query-builder-tree">
          {child.children.length ? (
            child.children.map((nestedChild) => renderExpressionChild(nestedChild, depth + 1))
          ) : (
            <p className="run-note">Add clauses, predicate refs, or more subgroups into this subtree.</p>
          )}
        </div>
      </div>
    );
  };

  if (!contracts.length || !activeContract || !activeSchema) {
    return null;
  }

  return (
    <div className={`run-surface-query-builder ${compact ? "compact" : ""}`.trim()}>
      <div className="run-surface-query-builder-head">
        <div>
          <span>Collection query builder</span>
          <strong>{activeContract.title}</strong>
        </div>
        {contracts.length > 1 ? (
          <label className="run-surface-query-builder-control">
            <span>Contract</span>
            <select
              value={activeContract.contract_key}
              onChange={(event) => setActiveContractKey(event.target.value)}
            >
              {contracts.map((contract) => (
                <option key={contract.contract_key} value={contract.contract_key}>
                  {contract.title}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <span className="meta-pill subtle">{activeContract.contract_key}</span>
        )}
      </div>
      <p className="run-note">{activeContract.summary}</p>
      <div className="run-surface-query-builder-grid">
        <div className="run-surface-query-builder-card" ref={builderEditorCardRef}>
          <div className="run-surface-query-builder-card-head">
            <strong>Builder</strong>
            <span>{activeEditorTargetLabel}</span>
          </div>
          <div className="run-surface-query-builder-mode-row">
            <button
              className={`run-surface-query-builder-mode-button ${expressionMode === "single" ? "is-active" : ""}`.trim()}
              onClick={() => {
                setExpressionMode("single");
                setEditorTarget({ kind: "draft" });
              }}
              type="button"
            >
              Single node
            </button>
            <button
              className={`run-surface-query-builder-mode-button ${expressionMode === "grouped" ? "is-active" : ""}`.trim()}
              onClick={() => {
                setExpressionMode("grouped");
                setSelectedGroupId(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID);
              }}
              type="button"
            >
              Grouped expression
            </button>
          </div>
          <p className="run-note">
            {expressionMode === "grouped"
              ? `${groupedExpressionLabel} · targeting ${selectedGroupLabel}`
              : expressionLabel || "Build a single collection node and apply it directly."}
          </p>
          <div className="run-surface-query-builder-form">
            <label className="run-surface-query-builder-control">
              <span>Collection path</span>
              <select
                value={getCollectionQuerySchemaId(activeSchema)}
                onChange={(event) => setActiveSchemaId(event.target.value)}
              >
                {collectionSchemas.map((schema) => (
                  <option key={getCollectionQuerySchemaId(schema)} value={getCollectionQuerySchemaId(schema)}>
                    {schema.label}
                  </option>
                ))}
              </select>
            </label>
            {activeSchema.parameters.length ? (
              <div className="run-surface-query-builder-parameter-grid">
                {activeSchema.parameters.map((parameter) => {
                  const optionValues = Array.from(
                    new Set([
                      ...(parameter.domain?.values.length ? parameter.domain.values : parameter.examples),
                      parameterValues[parameter.key] ?? "",
                    ].filter(Boolean)),
                  );
                  const enumSource = parameter.domain?.enumSource;
                  const bindingKey = parameterBindingKeys[parameter.key] ?? "";
                  return (
                    <label className="run-surface-query-builder-control" key={parameter.key}>
                      <span>{parameter.key}</span>
                      <select
                        disabled={Boolean(bindingKey)}
                        value={parameterValues[parameter.key] ?? ""}
                        onChange={(event) =>
                          setParameterValues((current) => ({
                            ...current,
                            [parameter.key]: event.target.value,
                          }))}
                      >
                        {optionValues.map((value) => (
                          <option key={value} value={value}>
                            {value}
                          </option>
                        ))}
                      </select>
                      <label className="run-surface-query-builder-checkbox">
                        <input
                          checked={Boolean(bindingKey)}
                          onChange={(event) =>
                            setParameterBindingKeys((current) => ({
                              ...current,
                              [parameter.key]: event.target.checked
                                ? current[parameter.key] || `${parameter.key}_binding`
                                : "",
                            }))}
                          type="checkbox"
                        />
                        <span>Bind path segment</span>
                      </label>
                      {bindingKey ? (
                        <input
                          type="text"
                          value={bindingKey}
                          onChange={(event) =>
                            setParameterBindingKeys((current) => ({
                              ...current,
                              [parameter.key]: event.target.value,
                            }))}
                          placeholder={`${parameter.key}_binding`}
                        />
                      ) : null}
                      <small>
                        {parameter.description}
                        {enumSource
                          ? ` Enum source: ${enumSource.kind ?? "enum"} @ ${(enumSource.path ?? []).join(".")}`
                          : ""}
                      </small>
                    </label>
                  );
                })}
              </div>
            ) : null}
            <div className="run-surface-query-builder-inline-grid">
              <label className="run-surface-query-builder-control">
                <span>Quantifier</span>
                <select
                  value={quantifier}
                  onChange={(event) => setQuantifier(event.target.value as "any" | "all" | "none")}
                >
                  <option value="any">any</option>
                  <option value="all">all</option>
                  <option value="none">none</option>
                </select>
              </label>
              <label className="run-surface-query-builder-control">
                <span>Field</span>
                <select
                  value={activeField?.key ?? ""}
                  onChange={(event) => setActiveFieldKey(event.target.value)}
                >
                  {activeSchema.elementSchema.map((field) => (
                    <option key={field.key} value={field.key}>
                      {field.key}
                    </option>
                  ))}
                </select>
              </label>
              <label className="run-surface-query-builder-control">
                <span>Operator</span>
                <select
                  value={activeOperator?.key ?? ""}
                  onChange={(event) => setActiveOperatorKey(event.target.value)}
                >
                  {(activeField?.operators ?? []).map((operator) => (
                    <option key={operator.key} value={operator.key}>
                      {operator.key}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label className="run-surface-query-builder-checkbox">
              <input
                checked={editorNegated}
                onChange={(event) => setEditorNegated(event.target.checked)}
                type="checkbox"
              />
              <span>Negate current clause</span>
            </label>
            <label className="run-surface-query-builder-control">
              <span>Value</span>
              <input
                disabled={Boolean(valueBindingKey)}
                type="text"
                value={builderValue}
                onChange={(event) => setBuilderValue(event.target.value)}
                placeholder={activeField?.valueType === "string" ? "type a value" : activeField?.valueType}
              />
              <label className="run-surface-query-builder-checkbox">
                <input
                  checked={Boolean(valueBindingKey)}
                  onChange={(event) => setValueBindingKey(event.target.checked ? "value_binding" : "")}
                  type="checkbox"
                />
                <span>Bind value as template parameter</span>
              </label>
              {valueBindingKey ? (
                <input
                  type="text"
                  value={valueBindingKey}
                  onChange={(event) => setValueBindingKey(event.target.value)}
                  placeholder="value_binding"
                />
              ) : null}
              <small>
                {activeField?.description ?? "Typed from collection element schema."}
              </small>
            </label>
          </div>
          <div className="run-surface-query-builder-actions">
            {expressionMode === "grouped" ? (
              <>
                <button
                  className="ghost-button"
                  disabled={!editorClauseState || (editorTarget.kind === "predicate" && !selectedPredicateSupportsClauseEditing)}
                  onClick={
                    editorTarget.kind === "draft"
                      ? addClauseToExpression
                      : updateSelectedExpressionTarget
                  }
                  type="button"
                >
                  {editorTarget.kind === "draft"
                    ? `Add clause to ${selectedGroupLabel}`
                    : `Update ${editorTarget.kind === "predicate" ? "predicate" : "selected clause"}`}
                </button>
                <button
                  className="ghost-button"
                  onClick={addGroupToExpression}
                  type="button"
                >
                  Add subgroup to {selectedGroupLabel}
                </button>
                {editorTarget.kind !== "draft" ? (
                  <button
                    className="ghost-button"
                    onClick={() => {
                      setEditorTarget({ kind: "draft" });
                      setPredicateDraftKey("");
                      setTemplateDraftKey("");
                    }}
                    type="button"
                  >
                    Return to draft
                  </button>
                ) : null}
              </>
            ) : null}
          </div>
          {expressionMode === "grouped" ? (
            <div className="run-surface-query-builder-section">
              <div className="run-surface-query-builder-card-head">
                <strong>Predicate registry</strong>
                <span>{predicates.length + predicateTemplates.length} saved</span>
              </div>
              <div className="run-surface-query-builder-inline-grid">
                <label className="run-surface-query-builder-control">
                  <span>Predicate key</span>
                  <input
                    onChange={(event) => setPredicateDraftKey(event.target.value)}
                    placeholder="high-return-orders"
                    value={predicateDraftKey}
                  />
                  <small>
                    {predicateKeyConflict
                      ? "Choose a unique predicate key."
                      : selectedPredicate
                        ? selectedPredicate.node.kind === "clause"
                          ? `Editing predicate ${selectedPredicate.key}.`
                          : `Updating subtree predicate ${selectedPredicate.key}.`
                        : "Save the current clause or target subtree as a reusable predicate."}
                  </small>
                </label>
                <label className="run-surface-query-builder-control">
                  <span>Template key</span>
                  <input
                    onChange={(event) => setTemplateDraftKey(event.target.value)}
                    placeholder="order-threshold-template"
                    value={templateDraftKey}
                  />
                  <small>
                    {templateKeyConflict
                      ? "Choose a unique template key."
                      : selectedTemplate
                        ? selectedTemplate.node.kind === "clause"
                          ? `Editing template ${selectedTemplate.key}.`
                          : `Updating subtree template ${selectedTemplate.key}.`
                        : "Save bound clauses or subtrees as reusable parameterized templates."}
                  </small>
                </label>
                <label className="run-surface-query-builder-control">
                  <span>Insert ref</span>
                  <select
                    onChange={(event) => setPredicateRefDraftKey(event.target.value)}
                    value={predicateRefDraftKey}
                  >
                    {[...predicates, ...predicateTemplates].length ? (
                      [...predicates, ...predicateTemplates].map((predicate) => (
                        <option key={predicate.id} value={predicate.key}>
                          {predicate.key}
                        </option>
                      ))
                    ) : (
                      <option value="">No predicates saved</option>
                    )}
                  </select>
                  <small>
                    Add a reusable {expressionAuthoring.predicateRefs.referenceField} into the selected group.
                  </small>
                </label>
              </div>
              {hasTemplateParameterAuthoringContext && (Boolean(trimmedTemplateDraftKey) || editorTarget.kind === "template") ? (
                <div className="run-surface-query-builder-section">
                  <div className="run-surface-query-builder-card-head">
                    <strong>Template parameter defaults</strong>
                    <span>{editableTemplateParameters.length}</span>
                  </div>
                  {canAuthorSubtreeTemplateDefaults ? (
                    <div className="run-surface-query-builder-mode-row">
                      <button
                        className={`run-surface-query-builder-mode-button ${templateDraftAuthoringTarget === "clause" ? "is-active" : ""}`.trim()}
                        onClick={() => setTemplateDraftAuthoringTarget("clause")}
                        type="button"
                      >
                        Clause draft defaults
                      </button>
                      <button
                        className={`run-surface-query-builder-mode-button ${templateDraftAuthoringTarget === "subtree" ? "is-active" : ""}`.trim()}
                        onClick={() => setTemplateDraftAuthoringTarget("subtree")}
                        type="button"
                      >
                        Selected subtree defaults
                      </button>
                    </div>
                  ) : null}
                  <p className="run-note">
                    {templateDraftAuthoringTarget === "subtree"
                      ? `Editing unsaved defaults for ${selectedGroupLabel}. Saving a clause template will keep using clause draft defaults.`
                      : "Editing clause-level template defaults for save/update flows."}
                  </p>
                  <div className="run-surface-query-builder-domain-list">
                    {editableTemplateParameterGroups.map((parameterGroup) => (
                      <div
                        className="run-surface-query-builder-section"
                        key={`template-parameter-group:${parameterGroup.key}`}
                      >
                        <div className="run-surface-query-builder-card-head">
                          <strong>{parameterGroup.label}</strong>
                          <span>{parameterGroup.parameters.length}</span>
                        </div>
                        <div className="run-surface-query-builder-parameter-grid">
                          <label className="run-surface-query-builder-control">
                            <span>Group label</span>
                            <input
                              type="text"
                              value={parameterGroup.label}
                              onChange={(event) =>
                                renameTemplateParameterGroup(
                                  templateParameterEditorContextKey,
                                  parameterGroup,
                                  event.target.value,
                                )}
                              placeholder="Ungrouped parameters"
                            />
                          </label>
                          <label className="run-surface-query-builder-control">
                            <span>Group help note</span>
                            <textarea
                              onChange={(event) =>
                                updateTemplateParameterGroupDraftMetadata(
                                  templateParameterEditorContextKey,
                                  parameterGroup.key,
                                  (group) => ({
                                    ...group,
                                    label: group.label || parameterGroup.label,
                                    helpNote: event.target.value,
                                  }),
                                )}
                              placeholder="Optional note shared across this parameter group"
                              rows={3}
                              value={parameterGroup.helpNote}
                            />
                          </label>
                          <label className="run-surface-query-builder-control">
                            <span>Visibility rule</span>
                            <select
                              onChange={(event) =>
                                updateTemplateParameterGroupDraftMetadata(
                                  templateParameterEditorContextKey,
                                  parameterGroup.key,
                                  (group) => ({
                                    ...group,
                                    label: group.label || parameterGroup.label,
                                    visibilityRule: event.target.value as RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["visibilityRule"],
                                  }),
                                )}
                              value={parameterGroup.visibilityRule}
                            >
                              <option value="always">Always show</option>
                              <option value="manual">Show on manual reveal</option>
                              <option value="binding_active">Show when binding is active</option>
                              <option value="value_active">Show when value/default is active</option>
                            </select>
                          </label>
                          <label className="run-surface-query-builder-control">
                            <span>Conflict policy</span>
                            <select
                              onChange={(event) =>
                                updateTemplateParameterGroupDraftMetadata(
                                  templateParameterEditorContextKey,
                                  parameterGroup.key,
                                  (group) => ({
                                    ...group,
                                    label: group.label || parameterGroup.label,
                                    coordinationPolicy: event.target.value as RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"],
                                  }),
                                )}
                              value={parameterGroup.coordinationPolicy}
                            >
                              <option value="manual_source_priority">Prefer manual source</option>
                              <option value="highest_source_priority">Highest source priority</option>
                              <option value="sticky_auto_selection">Keep current auto choice</option>
                              <option value="manual_resolution">Require manual resolution</option>
                            </select>
                          </label>
                          <label className="run-surface-query-builder-checkbox">
                            <input
                              checked={parameterGroup.collapsedByDefault}
                              onChange={(event) =>
                                updateTemplateParameterGroupDraftMetadata(
                                  templateParameterEditorContextKey,
                                  parameterGroup.key,
                                  (group) => ({
                                    ...group,
                                    label: group.label || parameterGroup.label,
                                    collapsedByDefault: event.target.checked,
                                  }),
                                )}
                              type="checkbox"
                            />
                            <span>Collapse this group by default in template consumers</span>
                          </label>
                        </div>
                        {parameterGroup.helpNote.trim() ? (
                          <p className="run-note">{parameterGroup.helpNote}</p>
                        ) : null}
                        <div className="run-surface-query-builder-actions">
                          <button
                            className="ghost-button"
                            onClick={() =>
                              appendTemplateParameterGroupPresetBundle(
                                templateParameterEditorContextKey,
                                parameterGroup,
                              )}
                            type="button"
                          >
                            Add preset bundle
                          </button>
                        </div>
                        {parameterGroup.presetBundles.length ? (
                          <div className="run-surface-query-builder-domain-list">
                            {getSortedTemplateGroupPresetBundles(parameterGroup.presetBundles).map((bundle) => {
                              const dependencyTargetGroups = editableTemplateParameterGroups.filter(
                                (candidateGroup) => candidateGroup.key !== parameterGroup.key,
                              );
                              return (
                                <div
                                  className="run-surface-query-builder-domain-card"
                                  key={`${parameterGroup.key}:bundle:${bundle.key}`}
                                >
                                <div className="run-surface-query-builder-card-head">
                                  <strong>{bundle.label}</strong>
                                  <span>{bundle.key}</span>
                                </div>
                                <div className="run-surface-query-builder-actions">
                                  <button
                                    className="ghost-button"
                                    onClick={() =>
                                      removeTemplateParameterGroupPresetBundle(
                                        templateParameterEditorContextKey,
                                        parameterGroup.key,
                                        bundle.key,
                                      )}
                                    type="button"
                                  >
                                    Remove bundle
                                  </button>
                                </div>
                                <div className="run-surface-query-builder-parameter-grid">
                                  <label className="run-surface-query-builder-control">
                                    <span>Bundle key</span>
                                    <input
                                      type="text"
                                      value={bundle.key}
                                      onChange={(event) =>
                                        renameTemplateParameterGroupPresetBundleKey(
                                          templateParameterEditorContextKey,
                                          parameterGroup.key,
                                          bundle.key,
                                          event.target.value,
                                        )
                                      }
                                      placeholder="focus_on_bindings"
                                    />
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Bundle label</span>
                                    <input
                                      type="text"
                                      value={bundle.label}
                                      onChange={(event) =>
                                        updateTemplateParameterGroupPresetBundle(
                                          templateParameterEditorContextKey,
                                          parameterGroup.key,
                                          bundle.key,
                                          (currentBundle) => ({
                                            ...currentBundle,
                                            label: event.target.value,
                                          }),
                                        )}
                                      placeholder="Focus on bindings"
                                    />
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Bundle help note</span>
                                    <textarea
                                      onChange={(event) =>
                                        updateTemplateParameterGroupPresetBundle(
                                          templateParameterEditorContextKey,
                                          parameterGroup.key,
                                          bundle.key,
                                          (currentBundle) => ({
                                            ...currentBundle,
                                            helpNote: event.target.value,
                                          }),
                                        )}
                                      placeholder="Optional note for when this bundle should be used"
                                      rows={2}
                                      value={bundle.helpNote}
                                    />
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Bundle priority</span>
                                    <input
                                      type="number"
                                      value={bundle.priority}
                                      onChange={(event) =>
                                        updateTemplateParameterGroupPresetBundle(
                                          templateParameterEditorContextKey,
                                          parameterGroup.key,
                                          bundle.key,
                                          (currentBundle) => ({
                                            ...currentBundle,
                                            priority: Number.isFinite(Number(event.target.value))
                                              ? Number(event.target.value)
                                              : 0,
                                          }),
                                        )}
                                      placeholder="0"
                                    />
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Auto-select</span>
                                    <select
                                      value={bundle.autoSelectRule}
                                      onChange={(event) =>
                                        updateTemplateParameterGroupPresetBundle(
                                          templateParameterEditorContextKey,
                                          parameterGroup.key,
                                          bundle.key,
                                          (currentBundle) => ({
                                            ...currentBundle,
                                            autoSelectRule: event.target.value as RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState["autoSelectRule"],
                                          }),
                                        )
                                      }
                                    >
                                      <option value="manual">Manual only</option>
                                      <option value="always">Always</option>
                                      <option value="binding_active">When bindings are active</option>
                                      <option value="value_active">When values are active</option>
                                    </select>
                                  </label>
                                </div>
                                <div className="run-surface-query-builder-section">
                                  <div className="run-surface-query-builder-card-head">
                                    <strong>Bundle dependencies</strong>
                                    <span>{bundle.dependencies.length}</span>
                                  </div>
                                  <div className="run-surface-query-builder-actions">
                                    <button
                                      className="ghost-button"
                                      disabled={!dependencyTargetGroups.length}
                                      onClick={() =>
                                        appendTemplateParameterGroupPresetBundleDependency(
                                          templateParameterEditorContextKey,
                                          parameterGroup.key,
                                          bundle.key,
                                          editableTemplateParameterGroups,
                                        )
                                      }
                                      type="button"
                                    >
                                      Add dependency
                                    </button>
                                  </div>
                                  {bundle.dependencies.length ? (
                                    <div className="run-surface-query-builder-domain-list">
                                      {bundle.dependencies.map((dependency) => {
                                        const targetGroup =
                                          editableTemplateParameterGroups.find(
                                            (candidateGroup) => candidateGroup.key === dependency.groupKey,
                                          ) ?? null;
                                        const targetBundles = targetGroup
                                          ? getSortedTemplateGroupPresetBundles(targetGroup.presetBundles)
                                          : [];
                                        return (
                                          <div
                                            className="run-surface-query-builder-domain-card"
                                            key={`${bundle.key}:dependency:${dependency.key}`}
                                          >
                                            <div className="run-surface-query-builder-card-head">
                                              <strong>{targetGroup?.label ?? dependency.groupKey}</strong>
                                              <span>{dependency.bundleKey}</span>
                                            </div>
                                            <div className="run-surface-query-builder-actions">
                                              <button
                                                className="ghost-button"
                                                onClick={() =>
                                                  removeTemplateParameterGroupPresetBundleDependency(
                                                    templateParameterEditorContextKey,
                                                    parameterGroup.key,
                                                    bundle.key,
                                                    dependency.key,
                                                  )
                                                }
                                                type="button"
                                              >
                                                Remove dependency
                                              </button>
                                            </div>
                                            <div className="run-surface-query-builder-parameter-grid">
                                              <label className="run-surface-query-builder-control">
                                                <span>Required group</span>
                                                <select
                                                  value={dependency.groupKey}
                                                  onChange={(event) => {
                                                    const nextGroupKey = event.target.value;
                                                    const nextGroup =
                                                      editableTemplateParameterGroups.find(
                                                        (candidateGroup) => candidateGroup.key === nextGroupKey,
                                                      ) ?? null;
                                                    updateTemplateParameterGroupPresetBundleDependency(
                                                      templateParameterEditorContextKey,
                                                      parameterGroup.key,
                                                      bundle.key,
                                                      dependency.key,
                                                      (currentDependency) => ({
                                                        ...currentDependency,
                                                        groupKey: nextGroupKey,
                                                        bundleKey:
                                                          nextGroup?.presetBundles[0]?.key
                                                          ?? currentDependency.bundleKey,
                                                      }),
                                                    );
                                                  }}
                                                >
                                                  {dependencyTargetGroups.map((candidateGroup) => (
                                                    <option
                                                      key={`${bundle.key}:dependency-group:${candidateGroup.key}`}
                                                      value={candidateGroup.key}
                                                    >
                                                      {candidateGroup.label}
                                                    </option>
                                                  ))}
                                                </select>
                                              </label>
                                              <label className="run-surface-query-builder-control">
                                                <span>Required bundle</span>
                                                <select
                                                  value={dependency.bundleKey}
                                                  onChange={(event) =>
                                                    updateTemplateParameterGroupPresetBundleDependency(
                                                      templateParameterEditorContextKey,
                                                      parameterGroup.key,
                                                      bundle.key,
                                                      dependency.key,
                                                      (currentDependency) => ({
                                                        ...currentDependency,
                                                        bundleKey: event.target.value,
                                                      }),
                                                    )
                                                  }
                                                >
                                                  {targetBundles.length ? (
                                                    targetBundles.map((targetBundle) => (
                                                      <option
                                                        key={`${bundle.key}:dependency-bundle:${dependency.key}:${targetBundle.key}`}
                                                        value={targetBundle.key}
                                                      >
                                                        {targetBundle.label}
                                                      </option>
                                                    ))
                                                  ) : (
                                                    <option value={dependency.bundleKey}>
                                                      {dependency.bundleKey || "No target bundle"}
                                                    </option>
                                                  )}
                                                </select>
                                              </label>
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  ) : (
                                    <p className="run-note">
                                      {dependencyTargetGroups.length
                                        ? "This bundle can auto-select required bundles in other groups before it applies."
                                        : "Add another parameter group to author cross-group bundle dependencies."}
                                    </p>
                                  )}
                                </div>
                                <div className="run-surface-query-builder-parameter-grid">
                                  {parameterGroup.parameters.map((parameter) => {
                                    const bundleValue = bundle.parameterValues[parameter.key] ?? "";
                                    const bundleBindingPreset = bundle.parameterBindingPresets[parameter.key] ?? "";
                                    return (
                                      <div
                                        className="run-surface-query-builder-domain-card"
                                        key={`${bundle.key}:${parameter.key}`}
                                      >
                                        <div className="run-surface-query-builder-card-head">
                                          <strong>{parameter.customLabel.trim() || parameter.label}</strong>
                                          <span>{parameter.key}</span>
                                        </div>
                                        <div className="run-surface-query-builder-parameter-grid">
                                          <label className="run-surface-query-builder-control">
                                            <span>Bundle value</span>
                                            {parameter.options.length ? (
                                              <select
                                                value={bundleValue}
                                                onChange={(event) =>
                                                  updateTemplateParameterGroupPresetBundle(
                                                    templateParameterEditorContextKey,
                                                    parameterGroup.key,
                                                    bundle.key,
                                                    (currentBundle) => ({
                                                      ...currentBundle,
                                                      parameterValues: {
                                                        ...currentBundle.parameterValues,
                                                        [parameter.key]: event.target.value,
                                                      },
                                                    }),
                                                  )}
                                              >
                                                <option value="">No bundle value</option>
                                                {Array.from(
                                                  new Set([
                                                    ...parameter.options,
                                                    bundleValue,
                                                  ].filter(Boolean)),
                                                ).map((value) => (
                                                  <option key={`${bundle.key}:${parameter.key}:value:${value}`} value={value}>
                                                    {value}
                                                  </option>
                                                ))}
                                              </select>
                                            ) : (
                                              <input
                                                type="text"
                                                value={bundleValue}
                                                onChange={(event) =>
                                                  updateTemplateParameterGroupPresetBundle(
                                                    templateParameterEditorContextKey,
                                                    parameterGroup.key,
                                                    bundle.key,
                                                    (currentBundle) => ({
                                                      ...currentBundle,
                                                      parameterValues: {
                                                        ...currentBundle.parameterValues,
                                                        [parameter.key]: event.target.value,
                                                      },
                                                    }),
                                                  )}
                                                placeholder={`Preset value (${parameter.valueType})`}
                                              />
                                            )}
                                          </label>
                                          <label className="run-surface-query-builder-control">
                                            <span>Bundle binding preset</span>
                                            <input
                                              type="text"
                                              value={bundleBindingPreset}
                                              onChange={(event) =>
                                                updateTemplateParameterGroupPresetBundle(
                                                  templateParameterEditorContextKey,
                                                  parameterGroup.key,
                                                  bundle.key,
                                                  (currentBundle) => ({
                                                    ...currentBundle,
                                                    parameterBindingPresets: {
                                                      ...currentBundle.parameterBindingPresets,
                                                      [parameter.key]: event.target.value,
                                                    },
                                                  }),
                                                )}
                                              placeholder="outer_template_parameter"
                                            />
                                          </label>
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : null}
                        <div className="run-surface-query-builder-parameter-grid">
                          {parameterGroup.parameters.map((parameter) => {
                            const parameterIndex = editableTemplateParameterIndexMap.get(parameter.key) ?? 0;
                            const presetBindingOptions = Array.from(
                              new Set([
                                ...nestedTemplateBindingParameterKeys.filter((key) => key !== parameter.key),
                                parameter.bindingPreset,
                              ].filter(Boolean)),
                            );
                            return (
                              <div className="run-surface-query-builder-domain-card" key={`template-parameter:${parameter.key}`}>
                                <div className="run-surface-query-builder-card-head">
                                  <strong>{parameter.customLabel.trim() || parameter.label}</strong>
                                  <span>{parameter.key}</span>
                                </div>
                                <div className="run-surface-query-builder-actions">
                                  <button
                                    className="ghost-button"
                                    disabled={parameterIndex === 0}
                                    onClick={() =>
                                      moveTemplateParameterDraftOrder(
                                        templateParameterEditorContextKey,
                                        parameter.key,
                                        "up",
                                        editableTemplateParameterKeys,
                                      )}
                                    type="button"
                                  >
                                    Move up
                                  </button>
                                  <button
                                    className="ghost-button"
                                    disabled={parameterIndex === editableTemplateParameters.length - 1}
                                    onClick={() =>
                                      moveTemplateParameterDraftOrder(
                                        templateParameterEditorContextKey,
                                        parameter.key,
                                        "down",
                                        editableTemplateParameterKeys,
                                      )}
                                    type="button"
                                  >
                                    Move down
                                  </button>
                                </div>
                                <div className="run-surface-query-builder-parameter-grid">
                                  <label className="run-surface-query-builder-control">
                                    <span>Custom label</span>
                                    <input
                                      type="text"
                                      value={parameter.customLabel}
                                      onChange={(event) =>
                                        updateTemplateParameterDraftLabel(
                                          templateParameterEditorContextKey,
                                          parameter.key,
                                          event.target.value,
                                        )}
                                      placeholder={parameter.label}
                                    />
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Assign group</span>
                                    <input
                                      type="text"
                                      value={parameter.groupName}
                                      onChange={(event) =>
                                        updateTemplateParameterDraftGroup(
                                          templateParameterEditorContextKey,
                                          parameter.key,
                                          event.target.value,
                                        )}
                                      placeholder="Ungrouped parameters"
                                    />
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Default value</span>
                                    {parameter.options.length ? (
                                      <select
                                        value={parameter.defaultValue}
                                        onChange={(event) =>
                                          updateTemplateParameterDraftDefault(
                                            templateParameterEditorContextKey,
                                            parameter.key,
                                            event.target.value,
                                          )}
                                      >
                                        <option value="">No default</option>
                                        {Array.from(
                                          new Set([
                                            ...parameter.options,
                                            parameter.defaultValue,
                                          ].filter(Boolean)),
                                        ).map((value) => (
                                          <option key={`${parameter.key}:default:${value}`} value={value}>
                                            {value}
                                          </option>
                                        ))}
                                      </select>
                                    ) : (
                                      <input
                                        type="text"
                                        value={parameter.defaultValue}
                                        onChange={(event) =>
                                          updateTemplateParameterDraftDefault(
                                            templateParameterEditorContextKey,
                                            parameter.key,
                                            event.target.value,
                                          )}
                                        placeholder={`Optional default (${parameter.valueType})`}
                                      />
                                    )}
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Nested binding preset</span>
                                    {presetBindingOptions.length ? (
                                      <select
                                        value={parameter.bindingPreset}
                                        onChange={(event) =>
                                          updateTemplateParameterDraftBindingPreset(
                                            templateParameterEditorContextKey,
                                            parameter.key,
                                            event.target.value,
                                          )}
                                      >
                                        <option value="">No preset</option>
                                        {presetBindingOptions.map((value) => (
                                          <option key={`${parameter.key}:preset:${value}`} value={value}>
                                            {value}
                                          </option>
                                        ))}
                                      </select>
                                    ) : (
                                      <input
                                        type="text"
                                        value={parameter.bindingPreset}
                                        onChange={(event) =>
                                          updateTemplateParameterDraftBindingPreset(
                                            templateParameterEditorContextKey,
                                            parameter.key,
                                            event.target.value,
                                          )}
                                        placeholder="outer_template_parameter"
                                      />
                                    )}
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Help note</span>
                                    <textarea
                                      onChange={(event) =>
                                        updateTemplateParameterDraftHelpNote(
                                          templateParameterEditorContextKey,
                                          parameter.key,
                                          event.target.value,
                                        )}
                                      placeholder="Optional authoring note for predicate/template users"
                                      rows={3}
                                      value={parameter.helpNote}
                                    />
                                  </label>
                                </div>
                                <small className="run-note">
                                  {parameter.description ?? parameter.label} · {parameter.valueType}
                                  {parameter.groupName.trim() ? ` · group ${parameter.groupName}` : ""}
                                  {parameter.bindingPreset.trim() ? ` · preset $${parameter.bindingPreset}` : ""}
                                </small>
                                {parameter.helpNote.trim() ? (
                                  <p className="run-note">{parameter.helpNote}</p>
                                ) : null}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
              {selectedRefTemplate?.parameters.length ? (
                <div className="run-surface-query-builder-domain-list">
                  {simulatedCoordinationGroups.length ? (
                    <div className="run-surface-query-builder-trace-grid">
                      <div className="run-surface-query-builder-trace-panel is-global">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Coordination graph explanation</strong>
                          <span className={`run-surface-query-builder-trace-status is-${coordinatedPredicateRefGroupBundleState.globalPolicyTrace.tone}`}>
                            {coordinatedPredicateRefGroupBundleState.globalPolicyTrace.statusLabel}
                          </span>
                        </div>
                        <p className="run-note">{coordinatedPredicateRefGroupBundleState.globalPolicyTrace.summary}</p>
                        <div className="run-surface-query-builder-trace-chip-list">
                          <span className="run-surface-query-builder-trace-chip">
                            {`${coordinatedPredicateRefGroupBundleState.globalPolicyTrace.counts.groupCount} groups`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {`${coordinatedPredicateRefGroupBundleState.globalPolicyTrace.counts.manualCount} manual`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {`${coordinatedPredicateRefGroupBundleState.globalPolicyTrace.counts.autoCount} auto`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {`${coordinatedPredicateRefGroupBundleState.globalPolicyTrace.counts.conflictCount} conflicts`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {`${coordinatedPredicateRefGroupBundleState.globalPolicyTrace.counts.unmetDependencyCount} unmet deps`}
                          </span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {coordinatedPredicateRefGroupBundleState.globalPolicyTrace.steps.map((step) => (
                            <div
                              className={`run-surface-query-builder-trace-step is-${step.tone}`}
                              key={step.key}
                            >
                              <strong>{step.title}</strong>
                              <p>{step.detail}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="run-surface-query-builder-trace-panel is-global" ref={bundleCoordinationSimulationPanelRef}>
                        <div className="run-surface-query-builder-card-head">
                          <strong>Policy simulation</strong>
                          <span className={`run-surface-query-builder-trace-status is-${simulatedPredicateRefGroupBundleState?.globalPolicyTrace.tone ?? "muted"}`}>
                            {simulatedPredicateRefGroupBundleState?.globalPolicyTrace.statusLabel ?? "Current"}
                          </span>
                        </div>
                          <QueryBuilderReplayGovernanceSection {...replayGovernanceSectionProps} />
                        <div className="run-surface-query-builder-inline-grid">
                          <label className="run-surface-query-builder-control">
                            <span>Simulation scope</span>
                            <select
                              value={bundleCoordinationSimulationScope}
                              onChange={(event) => setBundleCoordinationSimulationScope(event.target.value)}
                            >
                              <option value="all">All groups</option>
                              {simulatedCoordinationGroups.map((group) => (
                                <option key={`simulation-scope:${group.key}`} value={group.key}>
                                  {group.label}
                                </option>
                              ))}
                            </select>
                          </label>
                          <label className="run-surface-query-builder-control">
                            <span>Simulated policy</span>
                            <select
                              value={bundleCoordinationSimulationPolicy}
                              onChange={(event) =>
                                setBundleCoordinationSimulationPolicy(
                                  event.target.value as RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"] | "current",
                                )}
                            >
                              <option value="current">Current behavior</option>
                              <option value="manual_source_priority">Prefer manual source</option>
                              <option value="highest_source_priority">Highest source priority</option>
                              <option value="sticky_auto_selection">Keep current auto choice</option>
                              <option value="manual_resolution">Require manual resolution</option>
                            </select>
                          </label>
                        </div>
                        {activePredicateRefReplayApplyConflictSimulationReview ? (
                          <div className="run-surface-query-builder-trace-panel is-nested">
                            <div className="run-surface-query-builder-card-head">
                              <strong>Collision review override</strong>
                              <span>{activePredicateRefReplayApplyConflictSimulationReview.conflict.templateLabel}</span>
                            </div>
                            <div className="run-surface-query-builder-trace-chip-list">
                              <span className="run-surface-query-builder-trace-chip is-active">
                                {`${activePredicateRefReplayApplyConflictSimulationReview.selectedRemoteCount} remote field picks`}
                              </span>
                              <span className="run-surface-query-builder-trace-chip">
                                {`${activePredicateRefReplayApplyConflictSimulationGroupKeys.length} override groups`}
                              </span>
                              <span className="run-surface-query-builder-trace-chip">
                                {activePredicateRefReplayApplyConflictSimulationReview.hasMixedSelection
                                  ? "Partial merge replay"
                                  : activePredicateRefReplayApplyConflictSimulationReview.hasRemoteSelection
                                    ? "Full remote replay"
                                    : "Local replay baseline"}
                              </span>
                            </div>
                            <p className="run-note">
                              {`Simulation is currently replaying the reviewed collision draft for ${activePredicateRefReplayApplyConflictSimulationReview.conflict.sourceTabLabel} across ${activePredicateRefReplayApplyConflictSimulationGroupKeys
                                .map((groupKey) =>
                                  activePredicateRefReplayApplyConflictSimulationBundleOverrides.groupLabelsByKey[groupKey] ?? groupKey)
                                .join(", ") || "no groups"}.`}
                            </p>
                            {activePredicateRefReplayApplyConflictSimulationFieldPicks.global.length ? (
                              <div className="run-surface-query-builder-trace-chip-list">
                                {activePredicateRefReplayApplyConflictSimulationFieldPicks.global.slice(0, 4).map((pick) => (
                                  <span className="run-surface-query-builder-trace-chip-list" key={`collision-override-global-pick:${pick.decisionKey}`}>
                                    <button
                                      className={`run-surface-query-builder-trace-chip${
                                        pick.source === "remote" ? " is-active" : ""
                                      }`}
                                      onClick={() =>
                                        togglePredicateRefReplayApplyConflictSimulationFieldPickSource(
                                          pick.decisionKey,
                                        )}
                                      type="button"
                                    >
                                      {`${pick.label} · ${pick.source === "remote" ? "remote" : "local"}`}
                                    </button>
                                    <button
                                      className={`run-surface-query-builder-trace-chip${
                                        predicateRefReplayApplyConflictFocusedDecision?.conflictId
                                          === activePredicateRefReplayApplyConflictSimulationReview?.conflict.conflictId
                                        && predicateRefReplayApplyConflictFocusedDecision?.decisionKey === pick.decisionKey
                                          ? " is-active"
                                          : ""
                                      }`}
                                      onClick={() =>
                                        activePredicateRefReplayApplyConflictSimulationReview
                                          ? focusPredicateRefReplayApplyConflictDecision(
                                              activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId,
                                              pick.decisionKey,
                                            )
                                          : undefined}
                                      type="button"
                                    >
                                      Review field
                                    </button>
                                  </span>
                                ))}
                                {activePredicateRefReplayApplyConflictSimulationFieldPicks.global.length > 4 ? (
                                  <span className="run-surface-query-builder-trace-chip">
                                    {`+${activePredicateRefReplayApplyConflictSimulationFieldPicks.global.length - 4} more reviewed picks`}
                                  </span>
                                ) : null}
                              </div>
                            ) : null}
                            {activePredicateRefReplayApplyConflictSimulationFocusedItem
                            && activePredicateRefReplayApplyConflictSimulationFocusedChain.length ? (
                              <div className="run-surface-query-builder-trace-panel is-nested">
                                <div className="run-surface-query-builder-card-head">
                                  <strong>Reviewed field causal chain</strong>
                                  <span>{activePredicateRefReplayApplyConflictSimulationFocusedChain.length === 1
                                    ? "1 replay step"
                                    : `${activePredicateRefReplayApplyConflictSimulationFocusedChain.length} replay steps`}</span>
                                </div>
                                <p className="run-note">
                                  {`${activePredicateRefReplayApplyConflictSimulationFocusedItem.label} propagates through ${activePredicateRefReplayApplyConflictSimulationFocusedGroupKey ?? "the replay graph"} across the steps below.`}
                                </p>
                                <div className="run-surface-query-builder-trace-chip-list">
                                  {activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations.map((entry, index) => (
                                    <button
                                      className={`run-surface-query-builder-trace-chip${
                                        entry.stepIndex === activeSimulatedPredicateRefSolverReplayIndex
                                          ? " is-active"
                                          : ""
                                      }`}
                                      key={`focused-causal-chain:${entry.stepIndex}:${index}`}
                                      onClick={() => setBundleCoordinationSimulationReplayIndex(entry.stepIndex)}
                                      type="button"
                                    >
                                      {`${entry.stepLabel}${entry.type ? ` · ${entry.type.replaceAll("_", " ")}` : ""}`}
                                    </button>
                                  ))}
                                </div>
                                <div className="run-surface-query-builder-trace-list">
                                  {activePredicateRefReplayApplyConflictSimulationFocusedChainExplanations.map((entry, index) => (
                                    <div
                                      className={`run-surface-query-builder-trace-step is-${
                                        entry.stepIndex === activeSimulatedPredicateRefSolverReplayIndex
                                          ? "success"
                                          : entry.kind === "dependency_edge"
                                            ? "info"
                                            : entry.kind === "selection_change"
                                              ? "warning"
                                              : "info"
                                      }`}
                                      key={`focused-causal-step:${entry.stepIndex}:${index}`}
                                      >
                                      <strong>{`${entry.stepLabel}${entry.type ? ` · ${entry.type.replaceAll("_", " ")}` : ""}`}</strong>
                                      <div className="run-surface-query-builder-trace-chip-list">
                                        <span className="run-surface-query-builder-trace-chip is-active">
                                          {entry.causalLabel}
                                        </span>
                                        {entry.stateTransitionLabel ? (
                                          <span className="run-surface-query-builder-trace-chip">
                                            {entry.stateTransitionLabel}
                                          </span>
                                        ) : null}
                                        {entry.edgeRoleLabel ? (
                                          <span className="run-surface-query-builder-trace-chip">
                                            {entry.edgeRoleLabel}
                                          </span>
                                        ) : null}
                                      </div>
                                      <p>{entry.detail}</p>
                                      <div className="run-surface-query-builder-trace-panel is-nested">
                                        <div className="run-surface-query-builder-card-head">
                                          <strong>Bundle rule explanation</strong>
                                          <span>{entry.bundleRuleTitle}</span>
                                        </div>
                                        <p className="run-note">{entry.bundleRuleDetail}</p>
                                      </div>
                                      {entry.edgeLabels.length ? (
                                        <div className="run-surface-query-builder-trace-chip-list">
                                          {entry.edgeLabels.map((edgeLabel) => (
                                            <span
                                              className="run-surface-query-builder-trace-chip"
                                              key={`focused-causal-edge:${entry.stepIndex}:${edgeLabel}`}
                                            >
                                              {edgeLabel}
                                            </span>
                                          ))}
                                        </div>
                                      ) : null}
                                      {entry.parameterReasons.length ? (
                                        <div className="run-surface-query-builder-trace-panel is-nested">
                                          <div className="run-surface-query-builder-card-head">
                                            <strong>Parameter-level predicate reasons</strong>
                                            <span>{entry.parameterReasons.length}</span>
                                          </div>
                                          <div className="run-surface-query-builder-trace-list">
                                            {entry.parameterReasons.map((reason) => (
                                              <div
                                                className="run-surface-query-builder-trace-step is-info"
                                                key={`focused-causal-reason:${entry.stepIndex}:${reason.label}`}
                                              >
                                                <strong>{reason.label}</strong>
                                                <p>{reason.detail}</p>
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      ) : null}
                                      {entry.clauseSourceLocations.length || entry.bindingSourceLocations.length ? (
                                        <div className="run-surface-query-builder-trace-panel is-nested">
                                          <div className="run-surface-query-builder-card-head">
                                            <strong>Explanation provenance</strong>
                                            <span>{`${entry.clauseSourceLocations.length + entry.bindingSourceLocations.length} locations`}</span>
                                          </div>
                                          {entry.clauseSourceLocations.length ? (
                                            <div className="run-surface-query-builder-trace-panel is-nested">
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>Template clause locations</strong>
                                                <span>{entry.clauseSourceLocations.length}</span>
                                              </div>
                                              <div className="run-surface-query-builder-trace-list">
                                                {entry.clauseSourceLocations.map((sourceLocation) => (
                                                  <div
                                                    className="run-surface-query-builder-trace-step is-info"
                                                    key={`focused-causal-clause:${entry.stepIndex}:${sourceLocation.location}`}
                                                  >
                                                    <strong>{sourceLocation.location}</strong>
                                                    <p>{sourceLocation.detail}</p>
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          ) : null}
                                          {entry.bindingSourceLocations.length ? (
                                            <div className="run-surface-query-builder-trace-panel is-nested">
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>Binding source locations</strong>
                                                <span>{entry.bindingSourceLocations.length}</span>
                                              </div>
                                              <div className="run-surface-query-builder-trace-list">
                                                {entry.bindingSourceLocations.map((sourceLocation) => (
                                                  <div
                                                    className="run-surface-query-builder-trace-step is-info"
                                                    key={`focused-causal-binding:${entry.stepIndex}:${sourceLocation.location}`}
                                                  >
                                                    <strong>{sourceLocation.location}</strong>
                                                    <p>{sourceLocation.detail}</p>
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          ) : null}
                                        </div>
                                      ) : null}
                                      {entry.matchedPredicateBranches.length || entry.parameterComparisons.length ? (
                                        <div className="run-surface-query-builder-trace-panel is-nested">
                                          <div className="run-surface-query-builder-card-head">
                                            <strong>Evaluation-level provenance</strong>
                                            <span>{`${entry.matchedPredicateBranches.length + entry.parameterComparisons.length} matches`}</span>
                                          </div>
                                          {entry.runtimeCandidateTraces.length ? (
                                            <div className="run-surface-query-builder-trace-panel is-nested">
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>Runtime candidate traces</strong>
                                                <span>{entry.runtimeCandidateTraces.length}</span>
                                              </div>
                                              <div className="run-surface-query-builder-trace-list">
                                                {entry.runtimeCandidateTraces.map((candidateTrace) => {
                                                  const drillthroughKey = buildRuntimeCandidateTraceDrillthroughKey(
                                                    "focused_chain",
                                                    entry.stepIndex,
                                                    candidateTrace,
                                                  );
                                                  const drillthroughOpen = runtimeCandidateTraceDrillthroughByKey[drillthroughKey] ?? false;
                                                  const traceLinkedFromRunContext =
                                                    Boolean(activeRuntimeCandidateRunContext)
                                                    && candidateTrace.allValues.some(doesRuntimeCandidateSampleMatchActiveContext);
                                                  const traceLinkedFromArtifactSelection =
                                                    Boolean(effectivePersistedRuntimeCandidateArtifactSelection)
                                                    && candidateTrace.allValues.some(
                                                      doesRuntimeCandidateSampleMatchPersistedArtifactSelection,
                                                    );
                                                  const traceLinkedFromClauseEditor =
                                                    doesRuntimeCandidateTraceMatchEditorClause(candidateTrace);
                                                  const traceFocusedSampleCount =
                                                    focusedRuntimeCandidateSampleKey
                                                      ? candidateTrace.allValues.filter(doesRuntimeCandidateSampleMatchFocusedKey).length
                                                      : 0;
                                                  const tracePinnedSampleCount =
                                                    activeRuntimeCandidateRunContext
                                                      ? candidateTrace.allValues.filter(doesRuntimeCandidateSampleMatchActiveContext).length
                                                      : 0;
                                                  const traceArtifactSelectionSampleCount =
                                                    effectivePersistedRuntimeCandidateArtifactSelection
                                                      ? candidateTrace.allValues.filter(
                                                          doesRuntimeCandidateSampleMatchPersistedArtifactSelection,
                                                        ).length
                                                      : 0;
                                                  const {
                                                    traceClauseDiffItems,
                                                    tracePinnedFromClauseDraft,
                                                    traceReevaluationPreview,
                                                    traceReevaluationPreviewDiffItems,
                                                  } = buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection({
                                                    candidateTrace,
                                                    contracts,
                                                    drillthroughKey,
                                                    editorClauseState,
                                                    pinnedRuntimeCandidateClauseDiffItems,
                                                    pinnedRuntimeCandidateClauseOriginKey,
                                                    runtimeRuns,
                                                  });
                                                  const displayedSamples = (
                                                    drillthroughOpen ? candidateTrace.allValues : candidateTrace.sampleValues
                                                  ).slice().sort((left, right) => {
                                                    const leftFocused = doesRuntimeCandidateSampleMatchFocusedKey(left);
                                                    const rightFocused = doesRuntimeCandidateSampleMatchFocusedKey(right);
                                                    if (leftFocused !== rightFocused) {
                                                      return leftFocused ? -1 : 1;
                                                    }
                                                    const leftArtifactSelected =
                                                      doesRuntimeCandidateSampleMatchPersistedArtifactSelection(left);
                                                    const rightArtifactSelected =
                                                      doesRuntimeCandidateSampleMatchPersistedArtifactSelection(right);
                                                    if (leftArtifactSelected !== rightArtifactSelected) {
                                                      return leftArtifactSelected ? -1 : 1;
                                                    }
                                                    const leftPinned = doesRuntimeCandidateSampleMatchActiveContext(left);
                                                    const rightPinned = doesRuntimeCandidateSampleMatchActiveContext(right);
                                                    if (leftPinned === rightPinned) {
                                                      return left.candidatePath.localeCompare(right.candidatePath);
                                                    }
                                                    return leftPinned ? -1 : 1;
                                                  });
                                                  return (
                                                    <div
                                                      className={`run-surface-query-builder-trace-step is-${candidateTrace.result ? "success" : "muted"} ${
                                                        traceLinkedFromRunContext
                                                        || traceLinkedFromArtifactSelection
                                                        || traceLinkedFromClauseEditor
                                                        || tracePinnedFromClauseDraft
                                                          ? "is-linked"
                                                          : ""
                                                      }`.trim()}
                                                      key={`focused-causal-candidate:${entry.stepIndex}:${candidateTrace.location}:${candidateTrace.candidatePath}:${candidateTrace.candidateAccessor}`}
                                                    >
                                                      <strong>{candidateTrace.candidateAccessor}</strong>
                                                      <p>{candidateTrace.detail}</p>
                                                      <div className="run-surface-query-builder-trace-chip-list">
                                                        <span className="run-surface-query-builder-trace-chip">
                                                          {candidateTrace.candidatePath}
                                                        </span>
                                                        <span className="run-surface-query-builder-trace-chip">
                                                          {candidateTrace.comparedValue}
                                                        </span>
                                                        <span className="run-surface-query-builder-trace-chip">
                                                          {`${candidateTrace.quantifier.toUpperCase()} quantifier`}
                                                        </span>
                                                        <span className={`run-surface-query-builder-trace-chip${candidateTrace.result ? " is-active" : ""}`}>
                                                          {candidateTrace.result ? "matched" : "not matched"}
                                                        </span>
                                                        {traceLinkedFromRunContext ? (
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            Linked from run context
                                                          </span>
                                                        ) : null}
                                                        {traceLinkedFromArtifactSelection ? (
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            Artifact replay selection
                                                          </span>
                                                        ) : null}
                                                        {traceLinkedFromClauseEditor ? (
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            Linked from clause editor
                                                          </span>
                                                        ) : null}
                                                        {traceFocusedSampleCount ? (
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            {`${traceFocusedSampleCount} focused candidates`}
                                                          </span>
                                                        ) : null}
                                                        {tracePinnedFromClauseDraft ? (
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            Pinned draft origin
                                                          </span>
                                                        ) : null}
                                                        {tracePinnedSampleCount ? (
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            {`${tracePinnedSampleCount} pinned candidates`}
                                                          </span>
                                                        ) : null}
                                                        {traceArtifactSelectionSampleCount ? (
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            {`${traceArtifactSelectionSampleCount} artifact-selected`}
                                                          </span>
                                                        ) : null}
                                                      </div>
                                                      {candidateTrace.editorClause ? (
                                                        <div className="run-surface-query-builder-actions">
                                                          <button
                                                            className="ghost-button"
                                                            onClick={() =>
                                                              focusRuntimeCandidateClauseEditor(
                                                                candidateTrace.editorClause,
                                                                drillthroughKey,
                                                                activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
                                                              )
                                                            }
                                                            type="button"
                                                          >
                                                            Load clause into editor
                                                          </button>
                                                        </div>
                                                      ) : null}
                                                      {traceClauseDiffItems.length ? (
                                                        <div className="run-surface-query-builder-trace-panel is-nested">
                                                          <div className="run-surface-query-builder-card-head">
                                                            <strong>Clause draft diff</strong>
                                                            <span>{traceClauseDiffItems.length}</span>
                                                          </div>
                                                          <div className="run-surface-query-builder-trace-list">
                                                            {traceClauseDiffItems.slice(0, 6).map((item) => (
                                                              <div
                                                                className="run-surface-query-builder-trace-step is-warning"
                                                                key={`focused-causal-candidate-diff:${entry.stepIndex}:${drillthroughKey}:${item.key}`}
                                                              >
                                                                <strong>{item.label}</strong>
                                                                <p>{item.detail}</p>
                                                              </div>
                                                            ))}
                                                          </div>
                                                        </div>
                                                      ) : null}
                                                      {traceReevaluationPreview ? (
                                                        <div className="run-surface-query-builder-trace-panel is-nested">
                                                          <div className="run-surface-query-builder-card-head">
                                                            <strong>Clause re-evaluation preview</strong>
                                                            <span>{`${traceReevaluationPreview.sampleMatchCount}/${traceReevaluationPreview.sampleTotalCount} matched`}</span>
                                                          </div>
                                                          <div className="run-surface-query-builder-trace-chip-list">
                                                            <span className="run-surface-query-builder-trace-chip is-active">
                                                              {`${traceReevaluationPreview.runOutcomes.filter((outcome) => outcome.result).length}/${traceReevaluationPreview.runOutcomes.length} runs true`}
                                                            </span>
                                                            <span className="run-surface-query-builder-trace-chip">
                                                              {`${traceReevaluationPreviewDiffItems.length} changed candidates`}
                                                            </span>
                                                          </div>
                                                          {traceReevaluationPreviewDiffItems.length ? (
                                                            <div className="run-surface-query-builder-trace-list">
                                                              {traceReevaluationPreviewDiffItems.slice(0, 6).map((item) => (
                                                                <div
                                                                  className="run-surface-query-builder-trace-step is-info"
                                                                  key={`focused-causal-candidate-preview:${entry.stepIndex}:${drillthroughKey}:${item.key}`}
                                                                >
                                                                  <strong>{item.runId}</strong>
                                                                  <p>{item.detail}</p>
                                                                </div>
                                                              ))}
                                                            </div>
                                                          ) : (
                                                            <p className="run-note">
                                                              The current clause draft keeps the same concrete candidate outcomes for this trace.
                                                            </p>
                                                          )}
                                                        </div>
                                                      ) : null}
                                                      {candidateTrace.runOutcomes.length ? (
                                                        <div className="run-surface-query-builder-trace-panel is-nested">
                                                          <div className="run-surface-query-builder-card-head">
                                                            <strong>Quantifier outcomes</strong>
                                                            <span>{`${candidateTrace.runOutcomes.filter((outcome) => outcome.result).length}/${candidateTrace.runOutcomes.length} runs true`}</span>
                                                          </div>
                                                          <div className="run-surface-query-builder-trace-list">
                                                            {candidateTrace.runOutcomes.map((outcome) => (
                                                              <div
                                                                className={`run-surface-query-builder-trace-step is-${outcome.result ? "success" : "muted"}`}
                                                                key={`focused-causal-quantifier:${entry.stepIndex}:${candidateTrace.location}:${outcome.runId}`}
                                                              >
                                                                <strong>{outcome.runId}</strong>
                                                                <p>{outcome.detail}</p>
                                                                <div className="run-surface-query-builder-trace-chip-list">
                                                                  <span className="run-surface-query-builder-trace-chip">
                                                                    {`${outcome.matchedCount}/${outcome.candidateCount} matched`}
                                                                  </span>
                                                                  <span className={`run-surface-query-builder-trace-chip${outcome.result ? " is-active" : ""}`}>
                                                                    {outcome.result ? "quantifier true" : "quantifier false"}
                                                                  </span>
                                                                </div>
                                                              </div>
                                                            ))}
                                                          </div>
                                                        </div>
                                                      ) : null}
                                                      {candidateTrace.sampleTotalCount ? (
                                                        <div className="run-surface-query-builder-trace-panel is-nested">
                                                          <div className="run-surface-query-builder-card-head">
                                                            <strong>Concrete payload values</strong>
                                                            <span>{`${candidateTrace.sampleMatchCount}/${candidateTrace.sampleTotalCount} matched`}</span>
                                                          </div>
                                                          <div className="run-surface-query-builder-trace-list">
                                                            {displayedSamples.map((sample) => {
                                                              const sampleLinkedFromRunContext =
                                                                doesRuntimeCandidateSampleMatchActiveContext(sample);
                                                              const sampleLinkedFromArtifactSelection =
                                                                doesRuntimeCandidateSampleMatchPersistedArtifactSelection(sample);
                                                              const sampleFocused =
                                                                doesRuntimeCandidateSampleMatchFocusedKey(sample);
                                                              return (
                                                                <div
                                                                  className={`run-surface-query-builder-trace-step is-${sample.result ? "success" : "muted"} ${
                                                                    sampleLinkedFromRunContext
                                                                    || sampleLinkedFromArtifactSelection
                                                                    || sampleFocused
                                                                      ? "is-linked"
                                                                      : ""
                                                                  }`.trim()}
                                                                  key={`focused-causal-candidate-sample:${entry.stepIndex}:${candidateTrace.location}:${sample.runId}:${sample.candidatePath}`}
                                                                >
                                                                  <strong>{sample.candidatePath}</strong>
                                                                  <p>{sample.detail}</p>
                                                                  <div className="run-surface-query-builder-trace-chip-list">
                                                                    <span className="run-surface-query-builder-trace-chip">
                                                                      {sample.candidateValue}
                                                                    </span>
                                                                    <span className={`run-surface-query-builder-trace-chip${sample.result ? " is-active" : ""}`}>
                                                                      {sample.result ? "matched" : "not matched"}
                                                                    </span>
                                                                    {sampleLinkedFromRunContext ? (
                                                                      <span className="run-surface-query-builder-trace-chip is-active">
                                                                        Linked from run context
                                                                      </span>
                                                                    ) : null}
                                                                    {sampleLinkedFromArtifactSelection ? (
                                                                      <span className="run-surface-query-builder-trace-chip is-active">
                                                                        Artifact replay selection
                                                                      </span>
                                                                    ) : null}
                                                                    {sampleFocused ? (
                                                                      <span className="run-surface-query-builder-trace-chip is-active">
                                                                        Focused candidate
                                                                      </span>
                                                                    ) : null}
                                                                  </div>
                                                                  {onFocusRuntimeCandidateRunContext && sample.runContextSection && sample.runContextComponentKey ? (
                                                                    <div className="run-surface-query-builder-actions">
                                                                      <button
                                                                        className="ghost-button"
                                                                        onClick={() => {
                                                                          setFocusedRuntimeCandidateSampleKey(
                                                                            buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
                                                                          );
                                                                          onFocusRuntimeCandidateRunContext(sample, {
                                                                            artifactHoverKey:
                                                                              resolveRuntimeCandidateSampleArtifactHoverKey(sample),
                                                                          });
                                                                        }}
                                                                        type="button"
                                                                      >
                                                                        {sample.runContextLabel
                                                                          ? `Open ${sample.runContextLabel}`
                                                                          : "Open run context"}
                                                                      </button>
                                                                    </div>
                                                                  ) : null}
                                                                </div>
                                                              );
                                                            })}
                                                          </div>
                                                          {candidateTrace.sampleTruncated ? (
                                                            <div className="run-surface-query-builder-actions">
                                                              <button
                                                                className={`ghost-button${drillthroughOpen ? " is-active" : ""}`}
                                                                onClick={() =>
                                                                  setRuntimeCandidateTraceDrillthroughByKey((current) => ({
                                                                    ...current,
                                                                    [drillthroughKey]: !drillthroughOpen,
                                                                  }))}
                                                                type="button"
                                                              >
                                                                {drillthroughOpen
                                                                  ? `Collapse to ${candidateTrace.sampleValues.length} sample candidates`
                                                                  : `Drill through all ${candidateTrace.sampleTotalCount} candidates`}
                                                              </button>
                                                            </div>
                                                          ) : null}
                                                        </div>
                                                      ) : null}
                                                    </div>
                                                  );
                                                })}
                                              </div>
                                            </div>
                                          ) : null}
                                          {entry.truthTableRows.length ? (
                                            <div className="run-surface-query-builder-trace-panel is-nested">
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>Step truth table</strong>
                                                <span>{entry.truthTableRows.length}</span>
                                              </div>
                                              <div className="run-surface-query-builder-trace-list">
                                                {entry.truthTableRows.map((row) => (
                                                  <div
                                                    className={`run-surface-query-builder-trace-step is-${row.result ? "success" : "muted"}`}
                                                    key={`focused-causal-truth:${entry.stepIndex}:${row.location}:${row.expression}`}
                                                  >
                                                    <strong>{row.expression}</strong>
                                                    <p>{row.detail}</p>
                                                    <div className="run-surface-query-builder-trace-chip-list">
                                                      <span className={`run-surface-query-builder-trace-chip${row.result ? " is-active" : ""}`}>
                                                        {row.result ? "true" : "false"}
                                                      </span>
                                                      <span className="run-surface-query-builder-trace-chip">
                                                        {row.location}
                                                      </span>
                                                    </div>
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          ) : null}
                                          {entry.shortCircuitTraces.length ? (
                                            <div className="run-surface-query-builder-trace-panel is-nested">
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>Short-circuit trace</strong>
                                                <span>{entry.shortCircuitTraces.length}</span>
                                              </div>
                                              <div className="run-surface-query-builder-trace-list">
                                                {entry.shortCircuitTraces.map((trace) => (
                                                  <div
                                                    className="run-surface-query-builder-trace-step is-warning"
                                                    key={`focused-causal-short-circuit:${entry.stepIndex}:${trace.location}:${trace.detail}`}
                                                  >
                                                    <strong>{trace.location}</strong>
                                                    <p>{trace.detail}</p>
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          ) : null}
                                          {entry.matchedPredicateBranches.length ? (
                                            <div className="run-surface-query-builder-trace-panel is-nested">
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>Matched predicate branches</strong>
                                                <span>{entry.matchedPredicateBranches.length}</span>
                                              </div>
                                              <div className="run-surface-query-builder-trace-list">
                                                {entry.matchedPredicateBranches.map((match) => (
                                                  <div
                                                    className="run-surface-query-builder-trace-step is-success"
                                                    key={`focused-causal-branch:${entry.stepIndex}:${match.location}:${match.detail}`}
                                                  >
                                                    <strong>{match.location}</strong>
                                                    <p>{match.detail}</p>
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          ) : null}
                                          {entry.parameterComparisons.length ? (
                                            <div className="run-surface-query-builder-trace-panel is-nested">
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>Parameter comparisons</strong>
                                                <span>{entry.parameterComparisons.length}</span>
                                              </div>
                                              <div className="run-surface-query-builder-trace-list">
                                                {entry.parameterComparisons.map((comparison) => (
                                                  <div
                                                    className="run-surface-query-builder-trace-step is-info"
                                                    key={`focused-causal-comparison:${entry.stepIndex}:${comparison.location}:${comparison.detail}`}
                                                  >
                                                    <strong>{comparison.location}</strong>
                                                    <p>{comparison.detail}</p>
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          ) : null}
                                        </div>
                                      ) : null}
                                      <div className="run-surface-query-builder-actions">
                                        <button
                                          className="ghost-button"
                                          onClick={() => setBundleCoordinationSimulationReplayIndex(entry.stepIndex)}
                                          type="button"
                                        >
                                          Focus replay step
                                        </button>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ) : null}
                            <div className="run-surface-query-builder-actions">
                              <button
                                className="ghost-button"
                                onClick={() => setPredicateRefReplayApplyConflictSimulationConflictId(null)}
                                type="button"
                              >
                                Clear review override
                              </button>
                            </div>
                          </div>
                        ) : null}
                        <p className="run-note">
                          {simulatedPredicateRefGroupBundleState
                            ? (
                                activePredicateRefReplayApplyConflictSimulationReview
                                  ? "Simulating the currently reviewed collision merge on top of the selected coordination policy."
                                  : bundleCoordinationSimulationScope === "all"
                                    ? "Simulating this policy across the whole coordination graph."
                                    : `Simulating this policy for ${simulatedCoordinationGroups.find((group) => group.key === bundleCoordinationSimulationScope)?.label ?? "the selected group"} while leaving other groups unchanged.`
                              )
                            : "Pick a policy to see how the coordination graph would change without altering the current live selections."}
                        </p>
                        {simulatedPredicateRefGroupBundleState ? (
                          <>
                            <p className="run-note">{simulatedPredicateRefGroupBundleState.globalPolicyTrace.summary}</p>
                            <div className="run-surface-query-builder-trace-chip-list">
                              <span className="run-surface-query-builder-trace-chip">
                                {`${simulatedPredicateRefGroupBundleDiffs.length} changed groups`}
                              </span>
                              <span className="run-surface-query-builder-trace-chip">
                                {`${simulatedPredicateRefGroupBundleState.globalPolicyTrace.counts.conflictCount} simulated conflicts`}
                              </span>
                              <span className="run-surface-query-builder-trace-chip">
                                {`${simulatedPredicateRefGroupBundleState.globalPolicyTrace.counts.unmetDependencyCount} simulated unmet deps`}
                              </span>
                            </div>
                            {simulatedPredicateRefGroupBundleDiffs.length ? (
                              <div className="run-surface-query-builder-trace-list">
                                {simulatedPredicateRefGroupBundleDiffs.map((diff) => (
                                  <div
                                    className={`run-surface-query-builder-trace-step is-${
                                      activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey === diff.groupKey
                                        ? "success"
                                        : "info"
                                    }`}
                                    key={`simulation-diff:${diff.groupKey}`}
                                  >
                                    <strong>{diff.groupLabel}</strong>
                                    <p>
                                      {`${diff.currentStatus} · ${diff.currentBundleLabel} → ${diff.simulatedStatus} · ${diff.simulatedBundleLabel}`}
                                    </p>
                                    {diff.attributedReplayStepIndex >= 0 ? (
                                      <div className="run-surface-query-builder-trace-chip-list">
                                        <span className={`run-surface-query-builder-trace-chip${
                                          predicateRefReplayApplyConflictFocusedDecision?.conflictId
                                            === activePredicateRefReplayApplyConflictSimulationReview?.conflict.conflictId
                                          && activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey === diff.groupKey
                                            ? " is-active"
                                            : ""
                                        }`}>
                                          {diff.attributedReplayStepLabel}
                                        </span>
                                        {diff.attributedReplayType ? (
                                          <span className="run-surface-query-builder-trace-chip">
                                            {diff.attributedReplayType.replaceAll("_", " ")}
                                          </span>
                                        ) : null}
                                        <span className="run-surface-query-builder-trace-chip">
                                          {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey]?.chain[0]?.causalLabel
                                            ?? "Replay attribution"}
                                        </span>
                                        {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey]?.chain[0]?.stateTransitionLabel ? (
                                          <span className="run-surface-query-builder-trace-chip">
                                            {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey]?.chain[0]?.stateTransitionLabel}
                                          </span>
                                        ) : null}
                                        {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey]?.chain[0]?.edgeRoleLabel ? (
                                          <span className="run-surface-query-builder-trace-chip">
                                            {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey]?.chain[0]?.edgeRoleLabel}
                                          </span>
                                        ) : null}
                                        <span className="run-surface-query-builder-trace-chip">
                                          {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey]?.chainSummary
                                            ?? "No replay attribution"}
                                        </span>
                                      </div>
                                    ) : null}
                                    {diff.attributedReplayDetail ? (
                                      <p className="run-note">{diff.attributedReplayDetail}</p>
                                    ) : null}
                                    {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey]?.chain.length ? (
                                      <div className="run-surface-query-builder-trace-chip-list">
                                        {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey].chain
                                          .slice(0, 4)
                                          .map((entry, index) => (
                                            <button
                                              className={`run-surface-query-builder-trace-chip${
                                                entry.stepIndex === activeSimulatedPredicateRefSolverReplayIndex
                                                  ? " is-active"
                                                  : ""
                                              }`}
                                              key={`simulation-diff-chain:${diff.groupKey}:${entry.stepIndex}:${index}`}
                                              onClick={() => setBundleCoordinationSimulationReplayIndex(entry.stepIndex)}
                                              type="button"
                                            >
                                              {`${entry.stepLabel} · ${entry.causalLabel}`}
                                            </button>
                                          ))}
                                        {simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey].chain.length > 4 ? (
                                          <span className="run-surface-query-builder-trace-chip">
                                            {`+${
                                              simulatedPredicateRefSolverReplayAttributionByGroupKey[diff.groupKey].chain.length - 4
                                            } more chain steps`}
                                          </span>
                                        ) : null}
                                      </div>
                                    ) : null}
                                    {diff.clauseReevaluationProjection ? (
                                      <div className="run-surface-query-builder-trace-panel is-nested">
                                        <div className="run-surface-query-builder-card-head">
                                          <strong>Clause re-evaluation preview</strong>
                                          <span>{`${diff.clauseReevaluationProjection.previewTraceCount} traces`}</span>
                                        </div>
                                        <div className="run-surface-query-builder-trace-chip-list">
                                          <span className="run-surface-query-builder-trace-chip is-active">
                                            {`${diff.clauseReevaluationProjection.tracesWithChangesCount}/${diff.clauseReevaluationProjection.previewTraceCount} traces changed`}
                                          </span>
                                          <span className="run-surface-query-builder-trace-chip">
                                            {`${diff.clauseReevaluationProjection.changedCandidateCount} changed candidates`}
                                          </span>
                                          <span className="run-surface-query-builder-trace-chip is-active">
                                            Linked from clause draft
                                          </span>
                                        </div>
                                        <div className="run-surface-query-builder-trace-list">
                                          {diff.clauseReevaluationProjection.projectedTraces.slice(0, 3).map((trace) => (
                                            <div
                                              className={`run-surface-query-builder-trace-step is-info${
                                                clauseReevaluationPreviewSelection.traceKey === trace.drillthroughKey
                                                  ? " is-linked"
                                                  : ""
                                              }`}
                                              key={`simulation-diff-preview:${diff.groupKey}:${trace.key}`}
                                              ref={(node) => {
                                                if (node) {
                                                  clauseReevaluationPreviewTraceRefs.current.set(trace.drillthroughKey, node);
                                                  return;
                                                }
                                                clauseReevaluationPreviewTraceRefs.current.delete(trace.drillthroughKey);
                                              }}
                                            >
                                              <strong>{`${trace.stepLabel} · ${trace.candidateAccessor}`}</strong>
                                              <p>{trace.candidatePath}</p>
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                <button
                                                  className={`run-surface-query-builder-trace-chip${
                                                    trace.stepIndex === activeSimulatedPredicateRefSolverReplayIndex
                                                      ? " is-active"
                                                      : ""
                                                  }`}
                                                  onClick={() => setBundleCoordinationSimulationReplayIndex(trace.stepIndex)}
                                                  type="button"
                                                >
                                                  {trace.stepLabel}
                                                </button>
                                                <span className="run-surface-query-builder-trace-chip">
                                                  {trace.matchedCandidateLabel}
                                                </span>
                                                <span className="run-surface-query-builder-trace-chip">
                                                  {trace.matchedRunLabel}
                                                </span>
                                                <span className={`run-surface-query-builder-trace-chip${
                                                  trace.changedCandidateCount ? " is-active" : ""
                                                }`}>
                                                  {`${trace.changedCandidateCount} changed candidates`}
                                                </span>
                                                {clauseReevaluationPreviewSelection.traceKey === trace.drillthroughKey ? (
                                                  <span className="run-surface-query-builder-trace-chip is-active">
                                                    Linked preview trace
                                                  </span>
                                                ) : null}
                                              </div>
                                              <div className="run-surface-query-builder-actions">
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    focusRuntimeCandidateReplayTrace({
                                                      diffItemKey: null,
                                                      groupKey: trace.groupKey,
                                                      sampleKey: trace.primarySampleKey,
                                                      stepIndex: trace.stepIndex,
                                                      traceKey: trace.drillthroughKey,
                                                    })}
                                                  type="button"
                                                >
                                                  Focus candidate drill-through
                                                </button>
                                                {trace.editorClause ? (
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      setClauseReevaluationPreviewSelection({
                                                        diffItemKey: null,
                                                        groupKey: trace.groupKey,
                                                        traceKey: trace.drillthroughKey,
                                                      });
                                                      focusRuntimeCandidateClauseEditor(
                                                        trace.editorClause,
                                                        trace.drillthroughKey,
                                                        trace.groupKey,
                                                      );
                                                    }}
                                                    type="button"
                                                  >
                                                    Load clause into editor
                                                  </button>
                                                ) : null}
                                              </div>
                                              {trace.diffItems.length ? (
                                                <div className="run-surface-query-builder-trace-list">
                                                  {trace.diffItems.slice(0, 3).map((item) => (
                                                    <div
                                                      className={`run-surface-query-builder-trace-step is-info${
                                                        clauseReevaluationPreviewSelection.traceKey === trace.drillthroughKey
                                                        && clauseReevaluationPreviewSelection.diffItemKey === item.key
                                                          ? " is-linked"
                                                          : ""
                                                      }`}
                                                      key={`simulation-diff-preview-item:${diff.groupKey}:${trace.key}:${item.key}`}
                                                      ref={(node) => {
                                                        const refKey = `${trace.drillthroughKey}:${item.key}`;
                                                        if (node) {
                                                          clauseReevaluationPreviewDiffItemRefs.current.set(refKey, node);
                                                          return;
                                                        }
                                                        clauseReevaluationPreviewDiffItemRefs.current.delete(refKey);
                                                      }}
                                                    >
                                                      <strong>{item.runId}</strong>
                                                      <p>{item.detail}</p>
                                                      {clauseReevaluationPreviewSelection.traceKey === trace.drillthroughKey
                                                      && clauseReevaluationPreviewSelection.diffItemKey === item.key ? (
                                                        <div className="run-surface-query-builder-trace-chip-list">
                                                          <span className="run-surface-query-builder-trace-chip is-active">
                                                            Linked preview diff
                                                          </span>
                                                        </div>
                                                      ) : null}
                                                      <div className="run-surface-query-builder-actions">
                                                        {trace.focusableDiffSampleKeysByItemKey[item.key] ? (
                                                          <button
                                                            className="ghost-button"
                                                            onClick={() =>
                                                              focusRuntimeCandidateReplayTrace({
                                                                diffItemKey: item.key,
                                                                groupKey: trace.groupKey,
                                                                sampleKey: trace.focusableDiffSampleKeysByItemKey[item.key],
                                                                stepIndex: trace.stepIndex,
                                                                traceKey: trace.drillthroughKey,
                                                              })}
                                                            type="button"
                                                          >
                                                            Focus candidate
                                                          </button>
                                                        ) : null}
                                                        {trace.editorClause ? (
                                                          <button
                                                            className="ghost-button"
                                                            onClick={() => {
                                                              setClauseReevaluationPreviewSelection({
                                                                diffItemKey: item.key,
                                                                groupKey: trace.groupKey,
                                                                traceKey: trace.drillthroughKey,
                                                              });
                                                              focusRuntimeCandidateClauseEditor(
                                                                trace.editorClause,
                                                                trace.drillthroughKey,
                                                                trace.groupKey,
                                                              );
                                                            }}
                                                            type="button"
                                                          >
                                                            Focus clause editor
                                                          </button>
                                                        ) : null}
                                                      </div>
                                                    </div>
                                                  ))}
                                                </div>
                                              ) : (
                                                <p className="run-note">
                                                  The current clause draft keeps the same concrete candidate outcomes for this replay trace.
                                                </p>
                                              )}
                                            </div>
                                          ))}
                                        </div>
                                        {diff.clauseReevaluationProjection.projectedTraces.length > 3 ? (
                                          <p className="run-note">
                                            {`+${
                                              diff.clauseReevaluationProjection.projectedTraces.length - 3
                                            } more projected traces`}
                                          </p>
                                        ) : null}
                                      </div>
                                    ) : null}
                                    {activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[diff.groupKey]?.length ? (
                                      <div className="run-surface-query-builder-trace-chip-list">
                                        {activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[diff.groupKey]
                                          .slice(0, 4)
                                          .map((pick) => (
                                            <span
                                              className="run-surface-query-builder-trace-chip-list"
                                              key={`simulation-diff-pick:${diff.groupKey}:${pick.decisionKey}`}
                                            >
                                              <button
                                                className={`run-surface-query-builder-trace-chip${
                                                  pick.source === "remote" ? " is-active" : ""
                                                }`}
                                                onClick={() =>
                                                  togglePredicateRefReplayApplyConflictSimulationFieldPickSource(
                                                    pick.decisionKey,
                                                  )}
                                                type="button"
                                              >
                                                {`${pick.label} · ${pick.source === "remote" ? "remote" : "local"}`}
                                              </button>
                                              <button
                                                className={`run-surface-query-builder-trace-chip${
                                                  predicateRefReplayApplyConflictFocusedDecision?.conflictId
                                                    === activePredicateRefReplayApplyConflictSimulationReview?.conflict.conflictId
                                                  && predicateRefReplayApplyConflictFocusedDecision?.decisionKey === pick.decisionKey
                                                    ? " is-active"
                                                    : ""
                                                }`}
                                                onClick={() =>
                                                  activePredicateRefReplayApplyConflictSimulationReview
                                                    ? focusPredicateRefReplayApplyConflictDecision(
                                                        activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId,
                                                        pick.decisionKey,
                                                      )
                                                    : undefined}
                                                type="button"
                                              >
                                                Review field
                                              </button>
                                            </span>
                                          ))}
                                        {activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[diff.groupKey].length > 4 ? (
                                          <span className="run-surface-query-builder-trace-chip">
                                            {`+${
                                              activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[diff.groupKey].length - 4
                                            } more reviewed picks`}
                                          </span>
                                        ) : null}
                                      </div>
                                    ) : null}
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="run-note">
                                This policy would not change the currently resolved bundle choices for the simulated scope.
                              </p>
                            )}
                            {simulatedPredicateRefSolverReplay.length ? (
                              <div className="run-surface-query-builder-trace-panel is-nested">
                                <div className="run-surface-query-builder-card-head">
                                  <strong>Solver explanation replay</strong>
                                  <span className="run-surface-query-builder-trace-status is-info">
                                    {`${activeSimulatedPredicateRefSolverReplayIndex + 1}/${simulatedPredicateRefSolverReplay.length}`}
                                  </span>
                                </div>
                                {activePredicateRefReplayApplyConflictSimulationFocusedChain.length ? (
                                  <div className="run-surface-query-builder-trace-chip-list">
                                    <span className="run-surface-query-builder-trace-chip is-active">
                                      {`${activePredicateRefReplayApplyConflictSimulationFocusedChain.length} causal replay steps`}
                                    </span>
                                    <span className={`run-surface-query-builder-trace-chip${
                                      activePredicateRefReplayApplyConflictSimulationFocusedChainPosition >= 0
                                        ? " is-active"
                                        : ""
                                    }`}>
                                      {activePredicateRefReplayApplyConflictSimulationFocusedChainPosition >= 0
                                        ? `Focused chain step ${activePredicateRefReplayApplyConflictSimulationFocusedChainPosition + 1}/${activePredicateRefReplayApplyConflictSimulationFocusedChain.length}`
                                        : "Current replay step is outside the focused reviewed field chain"}
                                    </span>
                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry?.causalLabel ? (
                                      <span className="run-surface-query-builder-trace-chip is-active">
                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.causalLabel}
                                      </span>
                                    ) : null}
                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry?.stateTransitionLabel ? (
                                      <span className="run-surface-query-builder-trace-chip">
                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.stateTransitionLabel}
                                      </span>
                                    ) : null}
                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry?.edgeRoleLabel ? (
                                      <span className="run-surface-query-builder-trace-chip">
                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.edgeRoleLabel}
                                      </span>
                                    ) : null}
                                  </div>
                                ) : null}
                                <div className="run-surface-query-builder-actions">
                                  <button
                                    className="ghost-button"
                                    disabled={activeSimulatedPredicateRefSolverReplayIndex <= 0}
                                    onClick={() =>
                                      setBundleCoordinationSimulationReplayIndex((current) => Math.max(0, current - 1))}
                                    type="button"
                                  >
                                    Previous step
                                  </button>
                                  <button
                                    className="ghost-button"
                                    disabled={activeSimulatedPredicateRefSolverReplayIndex >= simulatedPredicateRefSolverReplay.length - 1}
                                    onClick={() =>
                                      setBundleCoordinationSimulationReplayIndex((current) =>
                                        Math.min(simulatedPredicateRefSolverReplay.length - 1, current + 1))}
                                    type="button"
                                  >
                                    Next step
                                  </button>
                                </div>
                                <div className="run-surface-query-builder-inline-grid">
                                  <label className="run-surface-query-builder-control">
                                    <span>Replay group filter</span>
                                    <select
                                      value={bundleCoordinationSimulationReplayGroupFilter}
                                      onChange={(event) =>
                                        setBundleCoordinationSimulationReplayGroupFilter(event.target.value)}
                                    >
                                      <option value="all">All groups</option>
                                      {simulatedCoordinationGroups.map((group) => (
                                        <option key={`solver-filter:${group.key}`} value={group.key}>
                                          {group.label}
                                        </option>
                                        ))}
                                    </select>
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Action type filter</span>
                                    <select
                                      value={bundleCoordinationSimulationReplayActionTypeFilter}
                                      onChange={(event) =>
                                        setBundleCoordinationSimulationReplayActionTypeFilter(
                                          event.target.value as "all" | "manual_anchor" | "dependency_selection" | "direct_auto_selection" | "conflict_blocked" | "idle",
                                        )}
                                    >
                                      <option value="all">All actions</option>
                                      {availableSimulatedPredicateRefSolverReplayActionTypes.map((actionType) => (
                                        <option key={`solver-action:${actionType}`} value={actionType}>
                                          {actionType.replaceAll("_", " ")}
                                        </option>
                                      ))}
                                    </select>
                                  </label>
                                  <label className="run-surface-query-builder-control">
                                    <span>Dependency edge filter</span>
                                    <select
                                      value={bundleCoordinationSimulationReplayEdgeFilter}
                                      onChange={(event) =>
                                        setBundleCoordinationSimulationReplayEdgeFilter(event.target.value)}
                                    >
                                      <option value="all">All dependency edges</option>
                                      {availableSimulatedPredicateRefSolverReplayEdges.map((edge) => (
                                        <option key={`solver-edge:${edge.key}`} value={edge.key}>
                                          {edge.label}
                                        </option>
                                      ))}
                                    </select>
                                  </label>
                                </div>
                                <div className="run-surface-query-builder-actions">
                                  <button
                                    className="ghost-button"
                                    disabled={
                                      !stagedSimulatedPredicateRefReplayPromotionSelections.length
                                      || simulatedPredicateRefReplayPromotionDraft.conflicts.length > 0
                                    }
                                    onClick={() => {
                                      if (!stagedSimulatedPredicateRefReplayPromotionSelections.length) {
                                        return;
                                      }
                                      setBundleCoordinationSimulationApprovalDecisionsByGroupKey(
                                        Object.fromEntries(
                                          stagedSimulatedPredicateRefReplayPromotionSelections.map((row) => [
                                            row.group.key,
                                            true,
                                          ]),
                                        ),
                                      );
                                      setBundleCoordinationSimulationFinalSummaryOpen(false);
                                      setBundleCoordinationSimulationApprovalOpen(true);
                                    }}
                                    type="button"
                                  >
                                    Review staged replay draft
                                  </button>
                                </div>
                                <input
                                  className="run-surface-query-builder-trace-slider"
                                  max={Math.max(0, simulatedPredicateRefSolverReplay.length - 1)}
                                  min={0}
                                  onChange={(event) => setBundleCoordinationSimulationReplayIndex(Number(event.target.value))}
                                  type="range"
                                  value={activeSimulatedPredicateRefSolverReplayIndex}
                                />
                                {activeSimulatedPredicateRefSolverReplayStep ? (
                                  <>
                                    <p className="run-note">
                                      <strong>{activeSimulatedPredicateRefSolverReplayStep.title}</strong>
                                      {` · ${activeSimulatedPredicateRefSolverReplayStep.summary}`}
                                    </p>
                                    {activeSimulatedPredicateRefSolverReplayFilteredGroup ? (
                                      <p className="run-note">
                                        {`Filtering replay actions to ${activeSimulatedPredicateRefSolverReplayFilteredGroup.label}.`}
                                      </p>
                                    ) : null}
                                    {bundleCoordinationSimulationReplayActionTypeFilter !== "all" ? (
                                      <p className="run-note">
                                        {`Showing only ${bundleCoordinationSimulationReplayActionTypeFilter.replaceAll("_", " ")} actions in this replay step.`}
                                      </p>
                                    ) : null}
                                    {activeSimulatedPredicateRefSolverReplayFilteredEdge ? (
                                      <p className="run-note">
                                        {`Tracing dependency edge ${activeSimulatedPredicateRefSolverReplayFilteredEdge.label} across replay steps.`}
                                      </p>
                                    ) : null}
                                    {activeSimulatedPredicateRefSolverReplayFilteredActions.length ? (
                                      <p className="run-note">
                                        {`Reviewed collision field picks are annotated on any replay group touched by the current simulation override.`}
                                      </p>
                                    ) : null}
                                    {simulatedPredicateRefReplayPromotionPreviewRows.length ? (
                                      <p className="run-note">
                                        {`Staged promotion currently applies ${stagedSimulatedPredicateRefReplayPromotionSelections
                                          .map((entry) => `${entry.group.label} → ${entry.promotedBundle.label}`)
                                          .join(", ") || "no groups"} from the filtered replay edge set.`}
                                      </p>
                                    ) : null}
                                    {simulatedPredicateRefReplayPromotionDraft.conflicts.length ? (
                                      <p className="run-note">
                                        {`Promotion is blocked by conflicting target bundles in ${simulatedPredicateRefReplayPromotionDraft.conflicts
                                          .map((conflict) => `${conflict.groupLabel} (${conflict.bundleLabels.join(", ")})`)
                                          .join("; ")}.`}
                                      </p>
                                    ) : null}
                                    {simulatedPredicateRefReplayPromotionPreviewRows.length ? (
                                      <div className="run-surface-query-builder-trace-list">
                                        {simulatedPredicateRefReplayPromotionPreviewRows.map((row) => {
                                          const isSelected =
                                            bundleCoordinationSimulationPromotionDecisionsByGroupKey[row.group.key] ?? true;
                                          return (
                                            <div
                                              className={`run-surface-query-builder-trace-step is-${
                                                row.matchesSimulation
                                                  ? "success"
                                                  : row.changesCurrent
                                                    ? "info"
                                                    : "muted"
                                              }`}
                                              key={`promotion-preview:${row.group.key}`}
                                            >
                                              <strong>{row.group.label}</strong>
                                              <p>
                                                {`${row.currentStatus} · ${row.currentBundleLabel} → ${row.simulatedStatus} · ${row.simulatedBundleLabel} → draft ${row.promotedBundle.label}`}
                                              </p>
                                              <div className="run-surface-query-builder-actions">
                                                <button
                                                  className={`ghost-button${isSelected ? " is-active" : ""}`}
                                                  onClick={() =>
                                                    setBundleCoordinationSimulationPromotionDecisionsByGroupKey((current) => ({
                                                      ...current,
                                                      [row.group.key]: !(current[row.group.key] ?? true),
                                                    }))}
                                                  type="button"
                                                >
                                                  {isSelected ? "Staged for apply" : "Skipped"}
                                                </button>
                                              </div>
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                <span className={`run-surface-query-builder-trace-chip${row.matchesSimulation ? " is-active" : ""}`}>
                                                  {row.matchesSimulation ? "Matches simulated bundle" : "Differs from simulated bundle"}
                                                </span>
                                                <span className={`run-surface-query-builder-trace-chip${row.changesCurrent ? " is-active" : ""}`}>
                                                  {row.changesCurrent ? "Changes current resolution" : "Keeps current resolution"}
                                                </span>
                                              </div>
                                            </div>
                                          );
                                        })}
                                      </div>
                                    ) : null}
                                    {bundleCoordinationSimulationApprovalOpen ? (
                                      <div className="run-surface-query-builder-trace-panel is-nested">
                                        <div className="run-surface-query-builder-card-head">
                                          <strong>Replay apply approval</strong>
                                          <span className="run-surface-query-builder-trace-status is-info">
                                            {`${approvedSimulatedPredicateRefReplayPromotionSelections.length}/${stagedSimulatedPredicateRefReplayPromotionSelections.length} approved`}
                                          </span>
                                        </div>
                                        <div className="run-surface-query-builder-actions">
                                          <button
                                            className="ghost-button"
                                            onClick={() => setBundleCoordinationSimulationApprovalOpen(false)}
                                            type="button"
                                          >
                                            Close review
                                          </button>
                                          <button
                                            className="ghost-button"
                                            disabled={
                                              !selectedRefTemplate
                                              || !approvedSimulatedPredicateRefReplayPromotionSelections.length
                                            }
                                            onClick={() => {
                                              if (!selectedRefTemplate || !approvedSimulatedPredicateRefReplayPromotionSelections.length) {
                                                return;
                                              }
                                              setBundleCoordinationSimulationFinalSummaryOpen(true);
                                            }}
                                            type="button"
                                          >
                                            Review final summary
                                          </button>
                                        </div>
                                        <label className="run-surface-query-builder-checkbox">
                                          <input
                                            checked={bundleCoordinationSimulationApprovalDiffOnly}
                                            onChange={(event) =>
                                              setBundleCoordinationSimulationApprovalDiffOnly(event.target.checked)}
                                            type="checkbox"
                                          />
                                          <span>Diff-only confirmation</span>
                                        </label>
                                        <p className="run-note">
                                          Review the three-way comparison before apply:
                                          current live resolution, simulated policy outcome, and promoted replay draft.
                                        </p>
                                        {visibleSimulatedPredicateRefReplayApprovalRows.length ? (
                                          <div className="run-surface-query-builder-trace-list">
                                            {visibleSimulatedPredicateRefReplayApprovalRows.map((row) => {
                                              const isApproved =
                                                bundleCoordinationSimulationApprovalDecisionsByGroupKey[row.group.key] ?? true;
                                              return (
                                                <div
                                                  className={`run-surface-query-builder-trace-step is-${
                                                    row.matchesSimulation
                                                      ? "success"
                                                      : row.changesCurrent
                                                        ? "info"
                                                        : "muted"
                                                  }`}
                                                  key={`approval-preview:${row.group.key}`}
                                                >
                                                  <strong>{row.group.label}</strong>
                                                  <div className="run-surface-query-builder-trace-chip-list">
                                                    <span className="run-surface-query-builder-trace-chip">
                                                      {`Current · ${row.currentStatus} · ${row.currentBundleLabel}`}
                                                    </span>
                                                    <span className="run-surface-query-builder-trace-chip">
                                                      {`Simulated · ${row.simulatedStatus} · ${row.simulatedBundleLabel}`}
                                                    </span>
                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                      {`Draft · ${row.promotedBundle.label}`}
                                                    </span>
                                                  </div>
                                                  <div className="run-surface-query-builder-actions">
                                                    <button
                                                      className={`ghost-button${isApproved ? " is-active" : ""}`}
                                                      onClick={() =>
                                                        setBundleCoordinationSimulationApprovalDecisionsByGroupKey((current) => ({
                                                          ...current,
                                                          [row.group.key]: !(current[row.group.key] ?? true),
                                                        }))}
                                                      type="button"
                                                    >
                                                      {isApproved ? "Approved" : "Rejected"}
                                                    </button>
                                                  </div>
                                                </div>
                                              );
                                            })}
                                          </div>
                                        ) : (
                                          <div className="run-surface-query-builder-trace-step is-muted">
                                            <strong>No approval rows</strong>
                                            <p>
                                              {bundleCoordinationSimulationApprovalDiffOnly
                                                ? "Diff-only confirmation is hiding rows that do not differ from the current or simulated state."
                                                : "There are no staged replay rows available for approval."}
                                            </p>
                                          </div>
                                        )}
                                      </div>
                                    ) : null}
                                    {bundleCoordinationSimulationFinalSummaryOpen ? (
                                      <div
                                        aria-modal="true"
                                        className="run-surface-query-builder-modal-backdrop"
                                        onClick={() => setBundleCoordinationSimulationFinalSummaryOpen(false)}
                                        role="dialog"
                                      >
                                        <div
                                          className="run-surface-query-builder-modal"
                                          onClick={(event) => event.stopPropagation()}
                                        >
                                          <div className="run-surface-query-builder-card-head">
                                            <strong>Final replay apply summary</strong>
                                            <span>{`${approvedSimulatedPredicateRefReplayPromotionSummary.total} approved rows`}</span>
                                          </div>
                                          <p className="run-note">
                                            Confirm the exact replay draft changes before they become live manual overrides.
                                            This final summary always shows every approved row, even if diff-only confirmation hid some rows in review.
                                          </p>
                                          <div className="run-surface-query-builder-trace-chip-list">
                                            <span className="run-surface-query-builder-trace-chip is-active">
                                              {`${approvedSimulatedPredicateRefReplayPromotionSummary.changesCurrentCount} change current`}
                                            </span>
                                            <span className="run-surface-query-builder-trace-chip">
                                              {`${approvedSimulatedPredicateRefReplayPromotionSummary.matchesSimulationCount} match simulated`}
                                            </span>
                                            <span className="run-surface-query-builder-trace-chip">
                                              {`${Math.max(
                                                0,
                                                approvedSimulatedPredicateRefReplayPromotionSummary.total
                                                  - approvedSimulatedPredicateRefReplayPromotionSummary.matchesSimulationCount,
                                              )} diverge from simulated`}
                                            </span>
                                          </div>
                                          <div className="run-surface-query-builder-trace-list">
                                            {approvedSimulatedPredicateRefReplayPromotionSelections.map((row) => (
                                              <div
                                                className={`run-surface-query-builder-trace-step is-${
                                                  row.matchesSimulation
                                                    ? "success"
                                                    : row.changesCurrent
                                                      ? "info"
                                                      : "muted"
                                                }`}
                                                key={`final-approval-preview:${row.group.key}`}
                                              >
                                                <strong>{row.group.label}</strong>
                                                <div className="run-surface-query-builder-trace-chip-list">
                                                  <span className="run-surface-query-builder-trace-chip">
                                                    {`Current · ${row.currentStatus} · ${row.currentBundleLabel}`}
                                                  </span>
                                                  <span className="run-surface-query-builder-trace-chip">
                                                    {`Simulated · ${row.simulatedStatus} · ${row.simulatedBundleLabel}`}
                                                  </span>
                                                  <span className="run-surface-query-builder-trace-chip is-active">
                                                    {`Draft · ${row.promotedBundle.label}`}
                                                  </span>
                                                </div>
                                              </div>
                                            ))}
                                          </div>
                                          <div className="run-surface-query-builder-modal-actions">
                                            <button
                                              className="ghost-button"
                                              onClick={() => setBundleCoordinationSimulationFinalSummaryOpen(false)}
                                              type="button"
                                            >
                                              Back to approval
                                            </button>
                                            <button
                                              className="ghost-button"
                                              disabled={
                                                !selectedRefTemplate
                                                || !approvedSimulatedPredicateRefReplayPromotionSelections.length
                                              }
                                              onClick={() => {
                                                if (!selectedRefTemplate || !approvedSimulatedPredicateRefReplayPromotionSelections.length) {
                                                  return;
                                                }
                                                const appliedAt = new Date().toISOString();
                                                const historyEntry: PredicateRefReplayApplyHistoryEntry = {
                                                  appliedAt,
                                                  approvedCount: approvedSimulatedPredicateRefReplayPromotionSummary.total,
                                                  changedCurrentCount:
                                                    approvedSimulatedPredicateRefReplayPromotionSummary.changesCurrentCount,
                                                  id: `replay-apply:${selectedRefTemplate.id}:${appliedAt}`,
                                                  matchesSimulationCount:
                                                    approvedSimulatedPredicateRefReplayPromotionSummary.matchesSimulationCount,
                                                  rollbackSnapshot: {
                                                    draftBindingsByParameterKey: Object.fromEntries(
                                                      approvedSimulatedPredicateRefReplayPromotionSelections.flatMap((row) =>
                                                        row.group.parameters.map((parameter) => ([
                                                          parameter.key,
                                                          predicateRefDraftBindings[parameter.key] ?? null,
                                                        ])),
                                                      ),
                                                    ),
                                                    groupSelectionsBySelectionKey: Object.fromEntries(
                                                      approvedSimulatedPredicateRefReplayPromotionSelections.map((row) => {
                                                        const selectionKey = `${selectedRefTemplate.id}:${row.group.key}`;
                                                        return [
                                                          selectionKey,
                                                          predicateRefGroupBundleSelections[selectionKey] ?? null,
                                                        ];
                                                      }),
                                                    ),
                                                  },
                                                  rows: approvedSimulatedPredicateRefReplayPromotionSelections.map((row) => ({
                                                    changesCurrent: row.changesCurrent,
                                                    currentBundleLabel: row.currentBundleLabel,
                                                    currentStatus: row.currentStatus,
                                                    groupKey: row.group.key,
                                                    groupLabel: row.group.label,
                                                    matchesSimulation: row.matchesSimulation,
                                                    promotedBundleKey: row.promotedBundle.key,
                                                    promotedBundleLabel: row.promotedBundle.label,
                                                    simulatedBundleLabel: row.simulatedBundleLabel,
                                                    simulatedStatus: row.simulatedStatus,
                                                  })),
                                                  sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
                                                  sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
                                                  templateId: selectedRefTemplate.id,
                                                  templateLabel: selectedRefTemplate.key,
                                                };
                                                setPredicateRefReplayApplyHistory((current) => [
                                                  historyEntry,
                                                  ...current,
                                                ].slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES));
                                                appendPredicateRefReplayApplySyncAuditEntry({
                                                  at: appliedAt,
                                                  auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
                                                  detail: `${predicateRefReplayApplyHistoryTabIdentity.label} applied ${historyEntry.approvedCount} approved replay rows.`,
                                                  entryId: historyEntry.id,
                                                  kind: "local_apply",
                                                  sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
                                                  sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
                                                  templateId: historyEntry.templateId,
                                                  templateLabel: historyEntry.templateLabel,
                                                });
                                                applyPredicateRefGroupPresetBundles(
                                                  selectedRefTemplate.id,
                                                  approvedSimulatedPredicateRefReplayPromotionSelections.map((row) => ({
                                                    group: row.group,
                                                    bundle: row.promotedBundle,
                                                  })),
                                                );
                                                setBundleCoordinationSimulationFinalSummaryOpen(false);
                                                setBundleCoordinationSimulationApprovalOpen(false);
                                              }}
                                              type="button"
                                            >
                                              Apply approved replay draft
                                            </button>
                                          </div>
                                        </div>
                                      </div>
                                    ) : null}
                                    {selectedRefTemplate ? (
                                      <div className="run-surface-query-builder-trace-panel is-nested">
                                        <div className="run-surface-query-builder-card-head">
                                          <strong>Replay apply history</strong>
                                          <span>{`${selectedRefTemplateReplayApplyHistory.length} entries`}</span>
                                        </div>
                                        <div className="run-surface-query-builder-inline-grid">
                                          <label className="run-surface-query-builder-control">
                                            <span>Remote sync mode</span>
                                            <select
                                              value={predicateRefReplayApplySyncMode}
                                              onChange={(event) =>
                                                setPredicateRefReplayApplySyncMode(
                                                  event.target.value as PredicateRefReplayApplySyncMode,
                                                )}
                                            >
                                              <option value="live">Live merge</option>
                                              <option value="audit_only">Audit only</option>
                                              <option value="mute_remote">Mute remote</option>
                                            </select>
                                            <small>
                                              {predicateRefReplayApplySyncMode === "live"
                                                ? "Apply and restore events from other tabs merge into this tab."
                                                : predicateRefReplayApplySyncMode === "audit_only"
                                                  ? "Remote tab events are logged but do not change this tab history."
                                              : "Remote tab replay history updates are ignored in this tab."}
                                            </small>
                                          </label>
                                          <label className="run-surface-query-builder-control">
                                            <span>Conflict policy</span>
                                            <select
                                              value={predicateRefReplayApplyConflictPolicy}
                                              onChange={(event) =>
                                                setPredicateRefReplayApplyConflictPolicy(
                                                  event.target.value as PredicateRefReplayApplyConflictPolicy,
                                                )}
                                            >
                                              <option value="require_review">Require review</option>
                                              <option value="prefer_local">Prefer local</option>
                                              <option value="prefer_remote">Prefer remote</option>
                                            </select>
                                            <small>
                                              {predicateRefReplayApplyConflictPolicy === "require_review"
                                                ? "Override collisions stay pending until you explicitly resolve them."
                                                : predicateRefReplayApplyConflictPolicy === "prefer_local"
                                                  ? "Conflicting remote overrides are logged but local history wins."
                                                  : "Conflicting remote overrides replace local history automatically."}
                                            </small>
                                          </label>
                                          <label className="run-surface-query-builder-control">
                                            <span>Audit filter</span>
                                            <select
                                              value={predicateRefReplayApplySyncAuditFilter}
                                              onChange={(event) =>
                                                setPredicateRefReplayApplySyncAuditFilter(
                                                  event.target.value as PredicateRefReplayApplySyncAuditFilter,
                                                )}
                                            >
                                              <option value="all">All audit events</option>
                                              <option value="local">Local only</option>
                                              <option value="remote">Remote only</option>
                                              <option value="apply">Apply only</option>
                                              <option value="restore">Restore only</option>
                                              <option value="conflict">Conflict only</option>
                                            </select>
                                            <small>
                                              {visibleSelectedRefTemplateReplayApplySyncAuditTrail.length
                                                ? `${visibleSelectedRefTemplateReplayApplySyncAuditTrail.length} audit events match the current filter.`
                                                : "No audit events match the current filter."}
                                            </small>
                                          </label>
                                        </div>
                                        <div className="run-surface-query-builder-trace-chip-list">
                                          <span className="run-surface-query-builder-trace-chip is-active">
                                            {`Current tab · ${predicateRefReplayApplyHistoryTabIdentity.label}`}
                                          </span>
                                          <span className="run-surface-query-builder-trace-chip">
                                            {selectedRefTemplateReplayApplySyncAuditTrail.length
                                              ? `${selectedRefTemplateReplayApplySyncAuditTrail.length} sync audit events`
                                              : "No sync audit events yet"}
                                          </span>
                                        </div>
                                        <p className="run-note">
                                          Each confirmed replay apply stores a rollback snapshot of the affected manual bundle
                                          selections and draft bindings for this template.
                                        </p>
                                        {selectedRefTemplateReplayApplyConflicts.length ? (
                                          <div className="run-surface-query-builder-trace-panel is-nested">
                                            <div className="run-surface-query-builder-card-head">
                                              <strong>Pending override collisions</strong>
                                              <span>{`${selectedRefTemplateReplayApplyConflicts.length} pending`}</span>
                                            </div>
                                            <p className="run-note">
                                              Remote replay history updates collided with a local override for the same entry id.
                                              Resolve each collision to decide which version stays active in this tab.
                                            </p>
                                            <div className="run-surface-query-builder-trace-list">
                                              {selectedRefTemplateReplayApplyConflictReviews.map((review) => (
                                                <div
                                                  className="run-surface-query-builder-trace-step is-warning"
                                                  key={review.conflict.conflictId}
                                                >
                                                  <strong>{review.conflict.templateLabel}</strong>
                                                  <p>
                                                    {`Detected ${formatRelativeTimestampLabel(review.conflict.detectedAt)} from ${review.conflict.sourceTabLabel}.`}
                                                  </p>
                                                  <div className="run-surface-query-builder-trace-chip-list">
                                                    <span className="run-surface-query-builder-trace-chip">
                                                      {`Local · ${review.conflict.localEntry.approvedCount} rows · ${review.conflict.localEntry.sourceTabLabel ?? predicateRefReplayApplyHistoryTabIdentity.label}`}
                                                    </span>
                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                      {`Remote · ${review.conflict.remoteEntry.approvedCount} rows · ${review.conflict.sourceTabLabel}`}
                                                    </span>
                                                    <span className="run-surface-query-builder-trace-chip">
                                                      {`${review.totalDiffCount} differing fields`}
                                                    </span>
                                                  </div>
                                                  <div className="run-surface-query-builder-trace-chip-list">
                                                    {review.conflict.remoteEntry.rows.map((row) => (
                                                      <span className="run-surface-query-builder-trace-chip" key={`${review.conflict.conflictId}:${row.groupKey}`}>
                                                        {`${row.groupLabel}: ${row.promotedBundleLabel}`}
                                                      </span>
                                                    ))}
                                                  </div>
                                                  <div className="run-surface-query-builder-trace-panel is-nested">
                                                    <div className="run-surface-query-builder-card-head">
                                                      <strong>Field-level diff</strong>
                                                      <span>{`${review.totalDiffCount} changed fields`}</span>
                                                    </div>
                                                    <div className="run-surface-query-builder-trace-chip-list">
                                                      {review.summaryDiffs.length ? (
                                                        <span className="run-surface-query-builder-trace-chip">
                                                          {`${review.summaryDiffs.length} summary`}
                                                        </span>
                                                      ) : null}
                                                      {review.rowDiffs.length ? (
                                                        <span className="run-surface-query-builder-trace-chip">
                                                          {`${review.rowDiffs.length} replay rows`}
                                                        </span>
                                                      ) : null}
                                                      {review.selectionSnapshotDiffs.length ? (
                                                        <span className="run-surface-query-builder-trace-chip">
                                                          {`${review.selectionSnapshotDiffs.length} rollback groups`}
                                                        </span>
                                                      ) : null}
                                                      {review.bindingSnapshotDiffs.length ? (
                                                        <span className="run-surface-query-builder-trace-chip">
                                                          {`${review.bindingSnapshotDiffs.length} draft bindings`}
                                                        </span>
                                                      ) : null}
                                                    </div>
                                                    {[
                                                      {
                                                        key: "summary",
                                                        label: "Summary fields",
                                                        items: review.summaryDiffs,
                                                      },
                                                      {
                                                        key: "rows",
                                                        label: "Replay rows",
                                                        items: review.rowDiffs,
                                                      },
                                                      {
                                                        key: "selection",
                                                        label: "Rollback groups",
                                                        items: review.selectionSnapshotDiffs,
                                                      },
                                                      {
                                                        key: "binding",
                                                        label: "Draft bindings",
                                                        items: review.bindingSnapshotDiffs,
                                                      },
                                                    ].map((section) =>
                                                      section.items.length ? (
                                                        <div className="run-surface-query-builder-trace-panel is-nested" key={`${review.conflict.conflictId}:${section.key}`}>
                                                          <div className="run-surface-query-builder-card-head">
                                                            <strong>{section.label}</strong>
                                                            <span>{`${section.items.length} changed`}</span>
                                                          </div>
                                                          <div className="run-surface-query-builder-trace-list">
                                                            {section.items.map((item) => {
                                                              const selectedSource = item.editable
                                                                ? review.selectedSources[item.decisionKey] ?? "local"
                                                                : null;
                                                              const canTrace =
                                                                item.relatedGroupKey
                                                                && simulatedCoordinationGroups.some(
                                                                  (group) => group.key === item.relatedGroupKey,
                                                                );
                                                              const isFocusedDecision =
                                                                predicateRefReplayApplyConflictFocusedDecision?.conflictId
                                                                  === review.conflict.conflictId
                                                                && predicateRefReplayApplyConflictFocusedDecision?.decisionKey
                                                                  === item.decisionKey;
                                                              return (
                                                                <div
                                                                  className={`run-surface-query-builder-trace-step is-${
                                                                    item.editable
                                                                      ? selectedSource === "remote"
                                                                        ? "warning"
                                                                        : "info"
                                                                      : "muted"
                                                                  }`}
                                                                  ref={(node) => {
                                                                    predicateRefReplayApplyConflictRowRefs.current[
                                                                      `${review.conflict.conflictId}:${item.decisionKey}`
                                                                    ] = node;
                                                                  }}
                                                                  key={`${review.conflict.conflictId}:${section.key}:${item.key}`}
                                                                  onClick={() =>
                                                                    setPredicateRefReplayApplyConflictFocusedDecisionState(
                                                                      review.conflict.conflictId,
                                                                      item.decisionKey,
                                                                    )}
                                                                  onFocusCapture={() =>
                                                                    setPredicateRefReplayApplyConflictFocusedDecisionState(
                                                                      review.conflict.conflictId,
                                                                      item.decisionKey,
                                                                    )}
                                                                  tabIndex={-1}
                                                                >
                                                                  <strong>{item.label}</strong>
                                                                  <div className="run-surface-query-builder-trace-chip-list">
                                                                    <span className={`run-surface-query-builder-trace-chip${
                                                                      selectedSource === "local" ? " is-active" : ""
                                                                    }`}>
                                                                      {`Local · ${item.localValue}`}
                                                                    </span>
                                                                    <span className={`run-surface-query-builder-trace-chip${
                                                                      selectedSource === "remote" ? " is-active" : ""
                                                                    }`}>
                                                                      {`Remote · ${item.remoteValue}`}
                                                                    </span>
                                                                    {!item.editable ? (
                                                                      <span className="run-surface-query-builder-trace-chip">
                                                                        Derived
                                                                      </span>
                                                                    ) : null}
                                                                    {isFocusedDecision ? (
                                                                      <span className="run-surface-query-builder-trace-chip is-active">
                                                                        Linked from replay
                                                                      </span>
                                                                    ) : null}
                                                                  </div>
                                                                  <div className="run-surface-query-builder-actions">
                                                                    {item.editable ? (
                                                                      <>
                                                                        <button
                                                                          className={`ghost-button${selectedSource === "local" ? " is-active" : ""}`}
                                                                          onClick={() => {
                                                                            setPredicateRefReplayApplyConflictFocusedDecisionState(
                                                                              review.conflict.conflictId,
                                                                              item.decisionKey,
                                                                            );
                                                                            setPredicateRefReplayApplyConflictDraftSource(
                                                                              review.conflict.conflictId,
                                                                              item.decisionKey,
                                                                              "local",
                                                                            );
                                                                          }}
                                                                          type="button"
                                                                        >
                                                                          Keep local field
                                                                        </button>
                                                                        <button
                                                                          className={`ghost-button${selectedSource === "remote" ? " is-active" : ""}`}
                                                                          onClick={() => {
                                                                            setPredicateRefReplayApplyConflictFocusedDecisionState(
                                                                              review.conflict.conflictId,
                                                                              item.decisionKey,
                                                                            );
                                                                            setPredicateRefReplayApplyConflictDraftSource(
                                                                              review.conflict.conflictId,
                                                                              item.decisionKey,
                                                                              "remote",
                                                                            );
                                                                          }}
                                                                          type="button"
                                                                        >
                                                                          Accept remote field
                                                                        </button>
                                                                      </>
                                                                    ) : null}
                                                                    {canTrace ? (
                                                                        <button
                                                                          className="ghost-button"
                                                                          onClick={() =>
                                                                            focusReplayApplyConflictSimulationTrace(
                                                                              item.relatedGroupKey ?? "",
                                                                              review.conflict.conflictId,
                                                                            )}
                                                                          type="button"
                                                                        >
                                                                          Trace in simulation
                                                                        </button>
                                                                    ) : null}
                                                                  </div>
                                                                  {!item.editable && section.key === "summary" ? (
                                                                    <p className="run-note">
                                                                      Derived summary counts follow the replay row selection that survives resolution.
                                                                    </p>
                                                                  ) : null}
                                                                </div>
                                                              );
                                                            })}
                                                          </div>
                                                        </div>
                                                      ) : null,
                                                    )}
                                                  </div>
                                                  <div className="run-surface-query-builder-trace-panel is-nested">
                                                    <div className="run-surface-query-builder-card-head">
                                                      <strong>What-if review</strong>
                                                      <span>Local, merged, and remote outcome</span>
                                                    </div>
                                                    <div className="run-surface-query-builder-trace-chip-list">
                                                      <span className="run-surface-query-builder-trace-chip">
                                                        {`${review.editableDiffCount} editable fields`}
                                                      </span>
                                                      <span className={`run-surface-query-builder-trace-chip${
                                                        review.hasRemoteSelection ? " is-active" : ""
                                                      }`}>
                                                        {`${review.selectedRemoteCount} remote selections`}
                                                      </span>
                                                      <span className={`run-surface-query-builder-trace-chip${
                                                        review.hasMixedSelection ? " is-active" : ""
                                                      }`}>
                                                        {review.hasMixedSelection ? "Partial merge staged" : "No partial merge staged"}
                                                      </span>
                                                    </div>
                                                    <div className="run-surface-query-builder-trace-list">
                                                      {[review.localPreview, review.mergedPreview, review.remotePreview].map((preview) => (
                                                        <div
                                                          className={`run-surface-query-builder-trace-step is-${
                                                            preview.resolution === "local" ? "info" : "warning"
                                                          }`}
                                                          key={`${review.conflict.conflictId}:${preview.resolution}`}
                                                        >
                                                          <strong>{preview.title}</strong>
                                                          <p>{preview.effect}</p>
                                                          <div className="run-surface-query-builder-trace-chip-list">
                                                            <span className="run-surface-query-builder-trace-chip">
                                                              {`${preview.entry.approvedCount} approved rows`}
                                                            </span>
                                                            <span className="run-surface-query-builder-trace-chip">
                                                              {`${preview.entry.changedCurrentCount} changed current`}
                                                            </span>
                                                            <span className="run-surface-query-builder-trace-chip">
                                                              {`${preview.entry.matchesSimulationCount} matched simulated`}
                                                            </span>
                                                            <span className="run-surface-query-builder-trace-chip">
                                                              {preview.snapshotSummary}
                                                            </span>
                                                            {preview.matchesLocal ? (
                                                              <span className="run-surface-query-builder-trace-chip">
                                                                Matches local
                                                              </span>
                                                            ) : null}
                                                            {preview.matchesRemote ? (
                                                              <span className="run-surface-query-builder-trace-chip">
                                                                Matches remote
                                                              </span>
                                                            ) : null}
                                                          </div>
                                                          <div className="run-surface-query-builder-trace-chip-list">
                                                            {preview.rowSummaries.length ? (
                                                              preview.rowSummaries.map((summary, index) => (
                                                                <span
                                                                  className="run-surface-query-builder-trace-chip"
                                                                  key={`${review.conflict.conflictId}:${preview.resolution}:row:${index}`}
                                                                >
                                                                  {summary}
                                                                </span>
                                                              ))
                                                            ) : (
                                                              <span className="run-surface-query-builder-trace-chip">
                                                                No replay rows recorded
                                                              </span>
                                                            )}
                                                          </div>
                                                          <div className="run-surface-query-builder-actions">
                                                            {preview.resolution === "merged" ? (
                                                              <>
                                                                <button
                                                                  className={`ghost-button${
                                                                    predicateRefReplayApplyConflictSimulationConflictId === review.conflict.conflictId
                                                                      ? " is-active"
                                                                      : ""
                                                                  }`}
                                                                  onClick={() => {
                                                                    setPredicateRefReplayApplyConflictSimulationConflictId(
                                                                      review.conflict.conflictId,
                                                                    );
                                                                    const firstGroupKey =
                                                                      review.mergedEntry.rows[0]?.groupKey ?? "";
                                                                    if (firstGroupKey) {
                                                                      focusReplayApplyConflictSimulationTrace(
                                                                        firstGroupKey,
                                                                        review.conflict.conflictId,
                                                                      );
                                                                      return;
                                                                    }
                                                                    bundleCoordinationSimulationPanelRef.current?.scrollIntoView({
                                                                      behavior: "smooth",
                                                                      block: "start",
                                                                    });
                                                                  }}
                                                                  type="button"
                                                                >
                                                                  {predicateRefReplayApplyConflictSimulationConflictId === review.conflict.conflictId
                                                                    ? "Simulation override active"
                                                                    : "Run reviewed merge in simulation"}
                                                                </button>
                                                                <button
                                                                  className="ghost-button"
                                                                  disabled={!review.hasRemoteSelection}
                                                                  onClick={() =>
                                                                    resolvePredicateRefReplayApplyConflict(
                                                                      review.conflict,
                                                                      "merged",
                                                                      review.mergedEntry,
                                                                    )}
                                                                  type="button"
                                                                >
                                                                  Apply reviewed merge
                                                                </button>
                                                                <button
                                                                  className="ghost-button"
                                                                  disabled={!review.hasRemoteSelection}
                                                                  onClick={() =>
                                                                    resetPredicateRefReplayApplyConflictDraftSource(
                                                                      review.conflict.conflictId,
                                                                    )}
                                                                  type="button"
                                                                >
                                                                  Reset merge draft
                                                                </button>
                                                              </>
                                                            ) : (
                                                              <button
                                                                className="ghost-button"
                                                                onClick={() =>
                                                                  resolvePredicateRefReplayApplyConflict(
                                                                    review.conflict,
                                                                    preview.resolution,
                                                                  )}
                                                                type="button"
                                                              >
                                                                {preview.title}
                                                              </button>
                                                            )}
                                                          </div>
                                                        </div>
                                                      ))}
                                                    </div>
                                                  </div>
                                                </div>
                                              ))}
                                            </div>
                                          </div>
                                        ) : null}
                                        {selectedRefTemplateReplayApplySyncAuditTrail.length ? (
                                          <div className="run-surface-query-builder-trace-panel is-nested">
                                            <div className="run-surface-query-builder-card-head">
                                              <strong>Sync audit trail</strong>
                                              <span>{`Session scoped · ${predicateRefReplayApplyHistoryTabIdentity.label}`}</span>
                                            </div>
                                            {visibleSelectedRefTemplateReplayApplySyncAuditTrail.length ? (
                                              <div className="run-surface-query-builder-trace-list">
                                                {visibleSelectedRefTemplateReplayApplySyncAuditTrail.map((auditEntry) => (
                                                  <div
                                                    className={`run-surface-query-builder-trace-step is-${
                                                      auditEntry.kind.includes("restore") ? "warning" : "info"
                                                    }`}
                                                    key={auditEntry.auditId}
                                                  >
                                                    <strong>{auditEntry.templateLabel}</strong>
                                                    <p>{auditEntry.detail}</p>
                                                    <div className="run-surface-query-builder-trace-chip-list">
                                                      <span className="run-surface-query-builder-trace-chip is-active">
                                                        {auditEntry.kind.replaceAll("_", " ")}
                                                      </span>
                                                      <span className="run-surface-query-builder-trace-chip">
                                                        {auditEntry.sourceTabLabel}
                                                      </span>
                                                      <span className="run-surface-query-builder-trace-chip">
                                                        {formatRelativeTimestampLabel(auditEntry.at)}
                                                      </span>
                                                    </div>
                                                  </div>
                                                ))}
                                              </div>
                                            ) : (
                                              <div className="run-surface-query-builder-trace-step is-muted">
                                                <strong>No matching sync audit events</strong>
                                                <p>
                                                  {predicateRefReplayApplySyncMode === "mute_remote"
                                                    ? "Remote sync is muted in this tab, so only local audit events can appear."
                                                    : "Change the audit filter to inspect a different replay history sync slice."}
                                                </p>
                                              </div>
                                            )}
                                          </div>
                                        ) : null}
                                        {latestSelectedRefTemplateReplayApplyEntry ? (
                                          <div className="run-surface-query-builder-actions">
                                            <button
                                              className="ghost-button"
                                              onClick={() =>
                                                restorePredicateRefReplayApplyHistoryEntry(
                                                  latestSelectedRefTemplateReplayApplyEntry,
                                                )}
                                              type="button"
                                            >
                                              Roll back latest replay apply
                                            </button>
                                          </div>
                                        ) : null}
                                        <div className="run-surface-query-builder-trace-list">
                                          {selectedRefTemplateReplayApplyHistory.map((entry) => (
                                            <div
                                              className={`run-surface-query-builder-trace-step is-${
                                                entry.lastRestoredAt ? "muted" : "info"
                                              }`}
                                              key={entry.id}
                                            >
                                              <strong>{entry.templateLabel}</strong>
                                              <p>
                                                {`${entry.approvedCount} approved rows · ${entry.changedCurrentCount} changed current · ${entry.matchesSimulationCount} matched simulated · ${formatRelativeTimestampLabel(entry.appliedAt)}`}
                                              </p>
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                {entry.sourceTabLabel ? (
                                                  <span className="run-surface-query-builder-trace-chip is-active">
                                                    {`Applied by ${entry.sourceTabLabel}`}
                                                  </span>
                                                ) : null}
                                                {entry.lastRestoredByTabLabel ? (
                                                  <span className="run-surface-query-builder-trace-chip">
                                                    {`Restored by ${entry.lastRestoredByTabLabel}`}
                                                  </span>
                                                ) : null}
                                              </div>
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                {entry.rows.map((row) => (
                                                  <span
                                                    className={`run-surface-query-builder-trace-chip${
                                                      row.matchesSimulation ? " is-active" : ""
                                                    }`}
                                                    key={`${entry.id}:${row.groupKey}`}
                                                  >
                                                    {`${row.groupLabel}: ${row.currentBundleLabel} → ${row.promotedBundleLabel}`}
                                                  </span>
                                                ))}
                                              </div>
                                              <div className="run-surface-query-builder-actions">
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => restorePredicateRefReplayApplyHistoryEntry(entry)}
                                                  type="button"
                                                >
                                                  Restore snapshot
                                                </button>
                                              </div>
                                              <p className="run-note">
                                                {entry.lastRestoredAt
                                                  ? `Last restored ${formatRelativeTimestampLabel(entry.lastRestoredAt)}${entry.lastRestoredByTabLabel ? ` by ${entry.lastRestoredByTabLabel}` : ""}.`
                                                  : "Snapshot available for rollback."}
                                              </p>
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    ) : null}
                                    <div className="run-surface-query-builder-trace-chip-list">
                                      {simulatedCoordinationGroups.map((group) => {
                                        const resolvedBundleKey =
                                          activeSimulatedPredicateRefSolverReplayStep.resolvedSelectionsByGroupKey[group.key] ?? "";
                                        const resolvedBundle =
                                          getSortedTemplateGroupPresetBundles(group.presetBundles).find(
                                            (bundle) => bundle.key === resolvedBundleKey,
                                          ) ?? null;
                                        return (
                                          <span
                                            className={`run-surface-query-builder-trace-chip${
                                              activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey === group.key
                                              || bundleCoordinationSimulationReplayGroupFilter === "all"
                                              || bundleCoordinationSimulationReplayGroupFilter === group.key
                                                ? " is-active"
                                                : " is-muted"
                                            }`}
                                            key={`solver-replay:${group.key}`}
                                          >
                                            {`${group.label}: ${resolvedBundle?.label ?? "unresolved"}${
                                              activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[group.key]?.length
                                                ? ` · ${
                                                    activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[group.key].length
                                                  } reviewed picks`
                                                : ""
                                            }`}
                                          </span>
                                        );
                                      })}
                                    </div>
                                    {activeSimulatedPredicateRefSolverReplayFilteredEdge ? (
                                      <div className="run-surface-query-builder-trace-chip-list">
                                        <span className="run-surface-query-builder-trace-chip is-active">
                                          {`Source: ${activeSimulatedPredicateRefSolverReplayFilteredEdge.sourceGroupLabel} → ${activeSimulatedPredicateRefSolverReplayFilteredEdge.sourceBundleLabel}`}
                                        </span>
                                        <span className="run-surface-query-builder-trace-chip is-active">
                                          {`Target: ${activeSimulatedPredicateRefSolverReplayFilteredEdge.targetGroupLabel} → ${activeSimulatedPredicateRefSolverReplayFilteredEdge.targetBundleLabel}`}
                                        </span>
                                      </div>
                                    ) : null}
                                    <div className="run-surface-query-builder-trace-list">
                                      {activeSimulatedPredicateRefSolverReplayFilteredActions.length ? (
                                        activeSimulatedPredicateRefSolverReplayFilteredActions.map((action) => (
                                          <div
                                            className={`run-surface-query-builder-trace-step is-${
                                              activePredicateRefReplayApplyConflictSimulationFocusedChainStepIndexSet.has(
                                                activeSimulatedPredicateRefSolverReplayIndex,
                                              )
                                              && activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey === action.groupKey
                                                ? "success"
                                                : action.type === "conflict_blocked"
                                                ? "warning"
                                                : action.type === "idle"
                                                  ? "muted"
                                                  : "success"
                                            }`}
                                            key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:${action.type}`}
                                          >
                                            <strong>{`${action.groupLabel} · ${action.type.replaceAll("_", " ")}`}</strong>
                                            <p>{action.detail}</p>
                                            {activePredicateRefReplayApplyConflictSimulationFocusedChainStepIndexSet.has(
                                              activeSimulatedPredicateRefSolverReplayIndex,
                                            ) ? (
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                <span className="run-surface-query-builder-trace-chip is-active">
                                                  {`Causal chain step ${
                                                    activePredicateRefReplayApplyConflictSimulationFocusedChainPosition + 1
                                                  }/${activePredicateRefReplayApplyConflictSimulationFocusedChain.length}`}
                                                </span>
                                                {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry?.causalLabel ? (
                                                  <span className="run-surface-query-builder-trace-chip is-active">
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.causalLabel}
                                                  </span>
                                                ) : null}
                                                {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry?.stateTransitionLabel ? (
                                                  <span className="run-surface-query-builder-trace-chip">
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.stateTransitionLabel}
                                                  </span>
                                                ) : null}
                                                {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry?.edgeRoleLabel ? (
                                                  <span className="run-surface-query-builder-trace-chip">
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.edgeRoleLabel}
                                                  </span>
                                                ) : null}
                                              </div>
                                            ) : null}
                                            {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry
                                            && activePredicateRefReplayApplyConflictSimulationFocusedChainStepIndexSet.has(
                                              activeSimulatedPredicateRefSolverReplayIndex,
                                            ) ? (
                                              <div className="run-surface-query-builder-trace-panel is-nested">
                                                <div className="run-surface-query-builder-card-head">
                                                  <strong>Bundle rule explanation</strong>
                                                  <span>{activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.bundleRuleTitle}</span>
                                                </div>
                                                <p className="run-note">
                                                  {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.bundleRuleDetail}
                                                </p>
                                                {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.parameterReasons.length ? (
                                                  <div className="run-surface-query-builder-trace-list">
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.parameterReasons
                                                      .slice(0, 3)
                                                      .map((reason) => (
                                                        <div
                                                          className="run-surface-query-builder-trace-step is-info"
                                                          key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-reason:${reason.label}`}
                                                        >
                                                          <strong>{reason.label}</strong>
                                                          <p>{reason.detail}</p>
                                                        </div>
                                                      ))}
                                                  </div>
                                                ) : null}
                                                {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.clauseSourceLocations.length
                                                || activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.bindingSourceLocations.length ? (
                                                  <div className="run-surface-query-builder-trace-panel is-nested">
                                                    <div className="run-surface-query-builder-card-head">
                                                      <strong>Explanation provenance</strong>
                                                      <span>Active replay step</span>
                                                    </div>
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.clauseSourceLocations.length ? (
                                                      <div className="run-surface-query-builder-trace-list">
                                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.clauseSourceLocations
                                                          .slice(0, 2)
                                                          .map((sourceLocation) => (
                                                            <div
                                                              className="run-surface-query-builder-trace-step is-info"
                                                              key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-clause:${sourceLocation.location}`}
                                                            >
                                                              <strong>{sourceLocation.location}</strong>
                                                              <p>{sourceLocation.detail}</p>
                                                            </div>
                                                          ))}
                                                      </div>
                                                    ) : null}
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.bindingSourceLocations.length ? (
                                                      <div className="run-surface-query-builder-trace-list">
                                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.bindingSourceLocations
                                                          .slice(0, 3)
                                                          .map((sourceLocation) => (
                                                            <div
                                                              className="run-surface-query-builder-trace-step is-info"
                                                              key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-binding:${sourceLocation.location}`}
                                                            >
                                                              <strong>{sourceLocation.location}</strong>
                                                              <p>{sourceLocation.detail}</p>
                                                            </div>
                                                          ))}
                                                      </div>
                                                    ) : null}
                                                  </div>
                                                ) : null}
                                                {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.runtimeCandidateTraces.length
                                                || activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.truthTableRows.length
                                                || activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.shortCircuitTraces.length
                                                || activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.matchedPredicateBranches.length
                                                || activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.parameterComparisons.length ? (
                                                  <div className="run-surface-query-builder-trace-panel is-nested">
                                                    <div className="run-surface-query-builder-card-head">
                                                      <strong>Evaluation-level provenance</strong>
                                                      <span>Active replay step</span>
                                                    </div>
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.runtimeCandidateTraces.length ? (
                                                      <div className="run-surface-query-builder-trace-list">
                                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.runtimeCandidateTraces
                                                          .slice(0, 3)
                                                          .map((candidateTrace) => {
                                                            const drillthroughKey = buildRuntimeCandidateTraceDrillthroughKey(
                                                              "active_replay",
                                                              activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.stepIndex,
                                                              candidateTrace,
                                                            );
                                                            const drillthroughOpen = runtimeCandidateTraceDrillthroughByKey[drillthroughKey] ?? false;
                                                            const traceLinkedFromRunContext =
                                                              Boolean(activeRuntimeCandidateRunContext)
                                                              && candidateTrace.allValues.some(doesRuntimeCandidateSampleMatchActiveContext);
                                                            const traceLinkedFromArtifactSelection =
                                                              Boolean(effectivePersistedRuntimeCandidateArtifactSelection)
                                                              && candidateTrace.allValues.some(
                                                                doesRuntimeCandidateSampleMatchPersistedArtifactSelection,
                                                              );
                                                            const traceLinkedFromClauseEditor =
                                                              doesRuntimeCandidateTraceMatchEditorClause(candidateTrace);
                                                            const traceFocusedSampleCount =
                                                              focusedRuntimeCandidateSampleKey
                                                                ? candidateTrace.allValues.filter(doesRuntimeCandidateSampleMatchFocusedKey).length
                                                                : 0;
                                                            const tracePinnedSampleCount =
                                                              activeRuntimeCandidateRunContext
                                                                ? candidateTrace.allValues.filter(doesRuntimeCandidateSampleMatchActiveContext).length
                                                                : 0;
                                                            const traceArtifactSelectionSampleCount =
                                                              effectivePersistedRuntimeCandidateArtifactSelection
                                                                ? candidateTrace.allValues.filter(
                                                                    doesRuntimeCandidateSampleMatchPersistedArtifactSelection,
                                                                  ).length
                                                                : 0;
                                                            const {
                                                              traceClauseDiffItems,
                                                              tracePinnedFromClauseDraft,
                                                              traceReevaluationPreview,
                                                              traceReevaluationPreviewDiffItems,
                                                            } = buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection({
                                                              candidateTrace,
                                                              contracts,
                                                              drillthroughKey,
                                                              editorClauseState,
                                                              pinnedRuntimeCandidateClauseDiffItems,
                                                              pinnedRuntimeCandidateClauseOriginKey,
                                                              runtimeRuns,
                                                            });
                                                            const previewSamples = drillthroughOpen
                                                              ? candidateTrace.allValues
                                                              : candidateTrace.sampleValues.slice(0, 2);
                                                            const orderedPreviewSamples = previewSamples.slice().sort((left, right) => {
                                                              const leftFocused = doesRuntimeCandidateSampleMatchFocusedKey(left);
                                                              const rightFocused = doesRuntimeCandidateSampleMatchFocusedKey(right);
                                                              if (leftFocused !== rightFocused) {
                                                                return leftFocused ? -1 : 1;
                                                              }
                                                              const leftArtifactSelected =
                                                                doesRuntimeCandidateSampleMatchPersistedArtifactSelection(left);
                                                              const rightArtifactSelected =
                                                                doesRuntimeCandidateSampleMatchPersistedArtifactSelection(right);
                                                              if (leftArtifactSelected !== rightArtifactSelected) {
                                                                return leftArtifactSelected ? -1 : 1;
                                                              }
                                                              const leftPinned = doesRuntimeCandidateSampleMatchActiveContext(left);
                                                              const rightPinned = doesRuntimeCandidateSampleMatchActiveContext(right);
                                                              if (leftPinned === rightPinned) {
                                                                return left.candidatePath.localeCompare(right.candidatePath);
                                                              }
                                                              return leftPinned ? -1 : 1;
                                                            });
                                                            return (
                                                              <div
                                                                className={`run-surface-query-builder-trace-step is-${candidateTrace.result ? "success" : "muted"} ${
                                                                  traceLinkedFromRunContext
                                                                  || traceLinkedFromArtifactSelection
                                                                  || traceLinkedFromClauseEditor
                                                                  || tracePinnedFromClauseDraft
                                                                    ? "is-linked"
                                                                    : ""
                                                                }`.trim()}
                                                                key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-candidate:${candidateTrace.location}:${candidateTrace.candidatePath}:${candidateTrace.candidateAccessor}`}
                                                              >
                                                                <strong>{candidateTrace.candidateAccessor}</strong>
                                                                <p>{candidateTrace.detail}</p>
                                                                <div className="run-surface-query-builder-trace-chip-list">
                                                                  <span className="run-surface-query-builder-trace-chip">
                                                                    {`${candidateTrace.quantifier.toUpperCase()} quantifier`}
                                                                  </span>
                                                                  <span className="run-surface-query-builder-trace-chip">
                                                                    {`${candidateTrace.sampleMatchCount}/${candidateTrace.sampleTotalCount} matched`}
                                                                  </span>
                                                                  {candidateTrace.runOutcomes.slice(0, 2).map((outcome) => (
                                                                    <span
                                                                      className={`run-surface-query-builder-trace-chip${outcome.result ? " is-active" : ""}`}
                                                                      key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-candidate-outcome:${candidateTrace.location}:${outcome.runId}`}
                                                                    >
                                                                      {`${outcome.runId} · ${outcome.result ? "true" : "false"}`}
                                                                    </span>
                                                                  ))}
                                                                  {candidateTrace.runOutcomes.length > 2 ? (
                                                                    <span className="run-surface-query-builder-trace-chip">
                                                                      {`+${candidateTrace.runOutcomes.length - 2} runs`}
                                                                    </span>
                                                                  ) : null}
                                                                  {traceLinkedFromRunContext ? (
                                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                                      Linked from run context
                                                                    </span>
                                                                  ) : null}
                                                                  {traceLinkedFromArtifactSelection ? (
                                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                                      Artifact replay selection
                                                                    </span>
                                                                  ) : null}
                                                                  {traceLinkedFromClauseEditor ? (
                                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                                      Linked from clause editor
                                                                    </span>
                                                                  ) : null}
                                                                  {traceFocusedSampleCount ? (
                                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                                      {`${traceFocusedSampleCount} focused candidates`}
                                                                    </span>
                                                                  ) : null}
                                                                  {tracePinnedFromClauseDraft ? (
                                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                                      Pinned draft origin
                                                                    </span>
                                                                  ) : null}
                                                                  {tracePinnedSampleCount ? (
                                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                                      {`${tracePinnedSampleCount} pinned candidates`}
                                                                    </span>
                                                                  ) : null}
                                                                  {traceArtifactSelectionSampleCount ? (
                                                                    <span className="run-surface-query-builder-trace-chip is-active">
                                                                      {`${traceArtifactSelectionSampleCount} artifact-selected`}
                                                                    </span>
                                                                  ) : null}
                                                                </div>
                                                                {candidateTrace.editorClause ? (
                                                                  <div className="run-surface-query-builder-actions">
                                                                    <button
                                                                      className="ghost-button"
                                                                      onClick={() =>
                                                                        focusRuntimeCandidateClauseEditor(
                                                                          candidateTrace.editorClause,
                                                                          drillthroughKey,
                                                                          action.groupKey,
                                                                        )
                                                                      }
                                                                      type="button"
                                                                    >
                                                                      Load clause into editor
                                                                    </button>
                                                                  </div>
                                                                ) : null}
                                                                {traceClauseDiffItems.length ? (
                                                                  <div className="run-surface-query-builder-trace-panel is-nested">
                                                                    <div className="run-surface-query-builder-card-head">
                                                                      <strong>Clause draft diff</strong>
                                                                      <span>{traceClauseDiffItems.length}</span>
                                                                    </div>
                                                                    <div className="run-surface-query-builder-trace-list">
                                                                      {traceClauseDiffItems.slice(0, 6).map((item) => (
                                                                        <div
                                                                          className="run-surface-query-builder-trace-step is-warning"
                                                                          key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-candidate-diff:${drillthroughKey}:${item.key}`}
                                                                        >
                                                                          <strong>{item.label}</strong>
                                                                          <p>{item.detail}</p>
                                                                        </div>
                                                                      ))}
                                                                    </div>
                                                                  </div>
                                                                ) : null}
                                                                {traceReevaluationPreview ? (
                                                                  <div className="run-surface-query-builder-trace-panel is-nested">
                                                                    <div className="run-surface-query-builder-card-head">
                                                                      <strong>Clause re-evaluation preview</strong>
                                                                      <span>{`${traceReevaluationPreview.sampleMatchCount}/${traceReevaluationPreview.sampleTotalCount} matched`}</span>
                                                                    </div>
                                                                    <div className="run-surface-query-builder-trace-chip-list">
                                                                      <span className="run-surface-query-builder-trace-chip is-active">
                                                                        {`${traceReevaluationPreview.runOutcomes.filter((outcome) => outcome.result).length}/${traceReevaluationPreview.runOutcomes.length} runs true`}
                                                                      </span>
                                                                      <span className="run-surface-query-builder-trace-chip">
                                                                        {`${traceReevaluationPreviewDiffItems.length} changed candidates`}
                                                                      </span>
                                                                    </div>
                                                                    {traceReevaluationPreviewDiffItems.length ? (
                                                                      <div className="run-surface-query-builder-trace-list">
                                                                        {traceReevaluationPreviewDiffItems.slice(0, 4).map((item) => (
                                                                          <div
                                                                            className="run-surface-query-builder-trace-step is-info"
                                                                            key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-candidate-preview:${drillthroughKey}:${item.key}`}
                                                                          >
                                                                            <strong>{item.runId}</strong>
                                                                            <p>{item.detail}</p>
                                                                          </div>
                                                                        ))}
                                                                      </div>
                                                                    ) : (
                                                                      <p className="run-note">
                                                                        The current clause draft keeps the same concrete candidate outcomes for this replay step.
                                                                      </p>
                                                                    )}
                                                                  </div>
                                                                ) : null}
                                                                {previewSamples.length ? (
                                                                  <div className="run-surface-query-builder-trace-chip-list">
                                                                    {orderedPreviewSamples.map((sample) => {
                                                                      const sampleLinkedFromRunContext =
                                                                        doesRuntimeCandidateSampleMatchActiveContext(sample);
                                                                      const sampleLinkedFromArtifactSelection =
                                                                        doesRuntimeCandidateSampleMatchPersistedArtifactSelection(sample);
                                                                      const sampleFocused =
                                                                        doesRuntimeCandidateSampleMatchFocusedKey(sample);
                                                                      return (
                                                                        <span
                                                                          className={`run-surface-query-builder-trace-chip${
                                                                            sample.result
                                                                            || sampleLinkedFromRunContext
                                                                            || sampleLinkedFromArtifactSelection
                                                                            || sampleFocused
                                                                              ? " is-active"
                                                                              : ""
                                                                          }`}
                                                                          key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-candidate-sample:${sample.runId}:${sample.candidatePath}`}
                                                                        >
                                                                          {`${sample.candidatePath} · ${sample.candidateValue}${
                                                                            sampleFocused
                                                                              ? " · focused"
                                                                              : sampleLinkedFromArtifactSelection
                                                                                ? " · artifact-selected"
                                                                              : sampleLinkedFromRunContext
                                                                                ? " · linked"
                                                                                : ""
                                                                          }`}
                                                                        </span>
                                                                      );
                                                                    })}
                                                                    {candidateTrace.sampleTruncated && !drillthroughOpen ? (
                                                                      <button
                                                                        className="ghost-button"
                                                                        onClick={() =>
                                                                          setRuntimeCandidateTraceDrillthroughByKey((current) => ({
                                                                            ...current,
                                                                            [drillthroughKey]: true,
                                                                          }))}
                                                                        type="button"
                                                                      >
                                                                        {`Drill through ${candidateTrace.sampleTotalCount} candidates`}
                                                                      </button>
                                                                    ) : null}
                                                                    {candidateTrace.sampleTruncated && drillthroughOpen ? (
                                                                      <button
                                                                        className="ghost-button is-active"
                                                                        onClick={() =>
                                                                          setRuntimeCandidateTraceDrillthroughByKey((current) => ({
                                                                            ...current,
                                                                            [drillthroughKey]: false,
                                                                          }))}
                                                                        type="button"
                                                                      >
                                                                        Collapse drill-through
                                                                      </button>
                                                                    ) : null}
                                                                  </div>
                                                                ) : null}
                                                                {drillthroughOpen && previewSamples.length ? (
                                                                  <div className="run-surface-query-builder-trace-panel is-nested">
                                                                    <div className="run-surface-query-builder-card-head">
                                                                      <strong>Concrete payload drill-through</strong>
                                                                      <span>{previewSamples.length}</span>
                                                                    </div>
                                                                    <div className="run-surface-query-builder-trace-list">
                                                                      {orderedPreviewSamples.map((sample) => {
                                                                        const sampleLinkedFromRunContext =
                                                                          doesRuntimeCandidateSampleMatchActiveContext(sample);
                                                                        const sampleLinkedFromArtifactSelection =
                                                                          doesRuntimeCandidateSampleMatchPersistedArtifactSelection(sample);
                                                                        const sampleFocused =
                                                                          doesRuntimeCandidateSampleMatchFocusedKey(sample);
                                                                        return (
                                                                          <div
                                                                            className={`run-surface-query-builder-trace-step is-${sample.result ? "success" : "muted"} ${
                                                                              sampleLinkedFromRunContext
                                                                              || sampleLinkedFromArtifactSelection
                                                                              || sampleFocused
                                                                                ? "is-linked"
                                                                                : ""
                                                                            }`.trim()}
                                                                            key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-candidate-detail:${sample.runId}:${sample.candidatePath}`}
                                                                          >
                                                                            <strong>{sample.candidatePath}</strong>
                                                                            <p>{sample.detail}</p>
                                                                            <div className="run-surface-query-builder-trace-chip-list">
                                                                              <span className="run-surface-query-builder-trace-chip">
                                                                                {sample.candidateValue}
                                                                              </span>
                                                                              <span className={`run-surface-query-builder-trace-chip${sample.result ? " is-active" : ""}`}>
                                                                                {sample.result ? "matched" : "not matched"}
                                                                              </span>
                                                                              {sampleLinkedFromRunContext ? (
                                                                                <span className="run-surface-query-builder-trace-chip is-active">
                                                                                  Linked from run context
                                                                                </span>
                                                                              ) : null}
                                                                              {sampleLinkedFromArtifactSelection ? (
                                                                                <span className="run-surface-query-builder-trace-chip is-active">
                                                                                  Artifact replay selection
                                                                                </span>
                                                                              ) : null}
                                                                              {sampleFocused ? (
                                                                                <span className="run-surface-query-builder-trace-chip is-active">
                                                                                  Focused candidate
                                                                                </span>
                                                                              ) : null}
                                                                            </div>
                                                                            {onFocusRuntimeCandidateRunContext && sample.runContextSection && sample.runContextComponentKey ? (
                                                                              <div className="run-surface-query-builder-actions">
                                                                                <button
                                                                                  className="ghost-button"
                                                                                  onClick={() => {
                                                                                    setFocusedRuntimeCandidateSampleKey(
                                                                                      buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
                                                                                    );
                                                                                    onFocusRuntimeCandidateRunContext(sample, {
                                                                                      artifactHoverKey:
                                                                                        resolveRuntimeCandidateSampleArtifactHoverKey(sample),
                                                                                    });
                                                                                  }}
                                                                                  type="button"
                                                                                >
                                                                                  {sample.runContextLabel
                                                                                    ? `Open ${sample.runContextLabel}`
                                                                                    : "Open run context"}
                                                                                </button>
                                                                              </div>
                                                                            ) : null}
                                                                          </div>
                                                                        );
                                                                      })}
                                                                    </div>
                                                                  </div>
                                                                ) : null}
                                                              </div>
                                                            );
                                                          })}
                                                      </div>
                                                    ) : null}
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.truthTableRows.length ? (
                                                      <div className="run-surface-query-builder-trace-list">
                                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.truthTableRows
                                                          .slice(0, 3)
                                                          .map((row) => (
                                                            <div
                                                              className={`run-surface-query-builder-trace-step is-${row.result ? "success" : "muted"}`}
                                                              key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-truth:${row.location}:${row.expression}`}
                                                            >
                                                              <strong>{row.expression}</strong>
                                                              <p>{row.detail}</p>
                                                            </div>
                                                          ))}
                                                      </div>
                                                    ) : null}
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.shortCircuitTraces.length ? (
                                                      <div className="run-surface-query-builder-trace-list">
                                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.shortCircuitTraces
                                                          .slice(0, 2)
                                                          .map((trace) => (
                                                            <div
                                                              className="run-surface-query-builder-trace-step is-warning"
                                                              key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-short-circuit:${trace.location}:${trace.detail}`}
                                                            >
                                                              <strong>{trace.location}</strong>
                                                              <p>{trace.detail}</p>
                                                            </div>
                                                          ))}
                                                      </div>
                                                    ) : null}
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.matchedPredicateBranches.length ? (
                                                      <div className="run-surface-query-builder-trace-list">
                                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.matchedPredicateBranches
                                                          .slice(0, 2)
                                                          .map((match) => (
                                                            <div
                                                              className="run-surface-query-builder-trace-step is-success"
                                                              key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-branch:${match.location}:${match.detail}`}
                                                            >
                                                              <strong>{match.location}</strong>
                                                              <p>{match.detail}</p>
                                                            </div>
                                                          ))}
                                                      </div>
                                                    ) : null}
                                                    {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.parameterComparisons.length ? (
                                                      <div className="run-surface-query-builder-trace-list">
                                                        {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.parameterComparisons
                                                          .slice(0, 3)
                                                          .map((comparison) => (
                                                            <div
                                                              className="run-surface-query-builder-trace-step is-info"
                                                              key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-comparison:${comparison.location}:${comparison.detail}`}
                                                            >
                                                              <strong>{comparison.location}</strong>
                                                              <p>{comparison.detail}</p>
                                                            </div>
                                                          ))}
                                                      </div>
                                                    ) : null}
                                                  </div>
                                                ) : null}
                                              </div>
                                            ) : null}
                                            {action.dependencyEdges.length ? (
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                {action.dependencyEdges.map((edge) => (
                                                  <span
                                                    className={`run-surface-query-builder-trace-chip${
                                                      bundleCoordinationSimulationReplayEdgeFilter === "all"
                                                      || bundleCoordinationSimulationReplayEdgeFilter === edge.key
                                                        ? " is-active"
                                                        : ""
                                                    }`}
                                                    key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:${edge.key}`}
                                                  >
                                                    {edge.label}
                                                  </span>
                                                ))}
                                              </div>
                                            ) : null}
                                            {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry?.edgeLabels.length
                                            && activePredicateRefReplayApplyConflictSimulationFocusedChainStepIndexSet.has(
                                              activeSimulatedPredicateRefSolverReplayIndex,
                                            ) ? (
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                {activePredicateRefReplayApplyConflictSimulationFocusedChainEntry.edgeLabels.map((edgeLabel) => (
                                                  <span
                                                    className="run-surface-query-builder-trace-chip"
                                                    key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:causal-edge:${edgeLabel}`}
                                                  >
                                                    {edgeLabel}
                                                  </span>
                                                ))}
                                              </div>
                                            ) : null}
                                            {activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[action.groupKey]?.length ? (
                                              <div className="run-surface-query-builder-trace-chip-list">
                                                {activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[action.groupKey]
                                                  .slice(0, 4)
                                                  .map((pick) => (
                                                    <span
                                                      className="run-surface-query-builder-trace-chip-list"
                                                      key={`${activeSimulatedPredicateRefSolverReplayStep.key}:${action.groupKey}:review-pick:${pick.decisionKey}`}
                                                    >
                                                      <button
                                                        className={`run-surface-query-builder-trace-chip${
                                                          pick.source === "remote" ? " is-active" : ""
                                                        }`}
                                                        onClick={() =>
                                                          togglePredicateRefReplayApplyConflictSimulationFieldPickSource(
                                                            pick.decisionKey,
                                                          )}
                                                        type="button"
                                                      >
                                                        {`${pick.label} · ${pick.source === "remote" ? "remote" : "local"}`}
                                                      </button>
                                                      <button
                                                        className={`run-surface-query-builder-trace-chip${
                                                          predicateRefReplayApplyConflictFocusedDecision?.conflictId
                                                            === activePredicateRefReplayApplyConflictSimulationReview?.conflict.conflictId
                                                          && predicateRefReplayApplyConflictFocusedDecision?.decisionKey === pick.decisionKey
                                                            ? " is-active"
                                                            : ""
                                                        }`}
                                                        onClick={() =>
                                                          activePredicateRefReplayApplyConflictSimulationReview
                                                            ? focusPredicateRefReplayApplyConflictDecision(
                                                                activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId,
                                                                pick.decisionKey,
                                                              )
                                                            : undefined}
                                                        type="button"
                                                      >
                                                        Review field
                                                      </button>
                                                    </span>
                                                  ))}
                                                {activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[action.groupKey].length > 4 ? (
                                                  <span className="run-surface-query-builder-trace-chip">
                                                    {`+${
                                                      activePredicateRefReplayApplyConflictSimulationFieldPicks.byGroupKey[action.groupKey].length - 4
                                                    } more reviewed picks`}
                                                  </span>
                                                ) : null}
                                              </div>
                                            ) : null}
                                          </div>
                                        ))
                                      ) : (
                                        <div className="run-surface-query-builder-trace-step is-muted">
                                          <strong>No matching actions</strong>
                                          <p>
                                            {activeSimulatedPredicateRefSolverReplayFilteredGroup
                                              ? (
                                                  bundleCoordinationSimulationReplayActionTypeFilter !== "all"
                                                    ? (
                                                        bundleCoordinationSimulationReplayEdgeFilter !== "all"
                                                          ? `This replay step did not produce any ${bundleCoordinationSimulationReplayActionTypeFilter.replaceAll("_", " ")} actions for ${activeSimulatedPredicateRefSolverReplayFilteredGroup.label} on the selected dependency edge.`
                                                          : `This replay step did not produce any ${bundleCoordinationSimulationReplayActionTypeFilter.replaceAll("_", " ")} actions for ${activeSimulatedPredicateRefSolverReplayFilteredGroup.label}.`
                                                      )
                                                    : (
                                                        bundleCoordinationSimulationReplayEdgeFilter !== "all"
                                                          ? `This replay step did not produce any coordination actions for ${activeSimulatedPredicateRefSolverReplayFilteredGroup.label} on the selected dependency edge.`
                                                          : `This replay step did not produce any coordination actions for ${activeSimulatedPredicateRefSolverReplayFilteredGroup.label}.`
                                                      )
                                                )
                                              : (
                                                  bundleCoordinationSimulationReplayActionTypeFilter !== "all"
                                                    ? (
                                                        bundleCoordinationSimulationReplayEdgeFilter !== "all"
                                                          ? `This replay step did not produce any ${bundleCoordinationSimulationReplayActionTypeFilter.replaceAll("_", " ")} actions on the selected dependency edge.`
                                                          : `This replay step did not produce any ${bundleCoordinationSimulationReplayActionTypeFilter.replaceAll("_", " ")} actions.`
                                                      )
                                                    : (
                                                        bundleCoordinationSimulationReplayEdgeFilter !== "all"
                                                          ? "This replay step did not produce any actions on the selected dependency edge."
                                                          : "This replay step did not produce any new coordination actions."
                                                      )
                                                )}
                                          </p>
                                        </div>
                                      )}
                                    </div>
                                  </>
                                ) : null}
                              </div>
                            ) : null}
                            <div className="run-surface-query-builder-trace-list">
                              {simulatedPredicateRefGroupBundleState.globalPolicyTrace.steps.map((step) => (
                                <div
                                  className={`run-surface-query-builder-trace-step is-${step.tone}`}
                                  key={`simulation-step:${step.key}`}
                                >
                                  <strong>{step.title}</strong>
                                  <p>{step.detail}</p>
                                </div>
                              ))}
                            </div>
                          </>
                        ) : null}
                      </div>
                    </div>
                  ) : null}
                  {selectedRefTemplateParameterGroups.map((parameterGroup) => {
                    const groupViewKey = `ref:${selectedRefTemplate.id}:${parameterGroup.key}`;
                    const isExpanded = isTemplateGroupExpanded(groupViewKey, parameterGroup.collapsedByDefault);
                    const sortedPresetBundles = getSortedTemplateGroupPresetBundles(parameterGroup.presetBundles);
                    const matchesVisibilityRule = doesTemplateGroupMatchVisibilityRule(
                      parameterGroup,
                      predicateRefDraftBindings,
                    );
                    const hasManualReveal = Boolean(templateGroupExpansionByKey[groupViewKey]);
                    const isGroupContentVisible = matchesVisibilityRule
                      ? isExpanded
                      : hasManualReveal;
                    const selectionKey = `${selectedRefTemplate.id}:${parameterGroup.key}`;
                    const selectedBundleKey = predicateRefGroupBundleSelections[selectionKey] ?? "";
                    const autoSelectedBundleKey = predicateRefGroupAutoBundleSelections[selectionKey] ?? "";
                    const effectiveBundleKey = selectedBundleKey || autoSelectedBundleKey;
                    const effectiveBundle = sortedPresetBundles.find((bundle) => bundle.key === effectiveBundleKey) ?? null;
                    const dependencyRequests =
                      coordinatedPredicateRefGroupBundleState.dependencyRequestsByGroupKey[parameterGroup.key] ?? [];
                    const conflictRequests =
                      coordinatedPredicateRefGroupBundleState.conflictRequestsByGroupKey[parameterGroup.key] ?? [];
                    const unmetDependencies =
                      coordinatedPredicateRefGroupBundleState.unmetDependenciesByGroupKey[parameterGroup.key] ?? [];
                    const policyTrace =
                      coordinatedPredicateRefGroupBundleState.policyTraceByGroupKey[parameterGroup.key] ?? null;
                    return (
                      <div className="run-surface-query-builder-section" key={groupViewKey}>
                        <div className="run-surface-query-builder-card-head">
                          <strong>{parameterGroup.label}</strong>
                          <span>{parameterGroup.parameters.length}</span>
                        </div>
                        <div className="run-surface-query-builder-actions">
                          <button
                            className="ghost-button"
                            onClick={() =>
                              toggleTemplateGroupExpanded(groupViewKey, parameterGroup.collapsedByDefault)}
                            type="button"
                          >
                            {isExpanded ? "Collapse group" : matchesVisibilityRule ? "Expand group" : "Reveal group"}
                          </button>
                        </div>
                        <p className="run-note">
                          {parameterGroup.collapsedByDefault
                            ? "Collapsed by default when this template is inserted."
                            : "Expanded by default when this template is inserted."}
                          {parameterGroup.visibilityRule !== "always"
                            ? ` · visibility ${parameterGroup.visibilityRule.replaceAll("_", " ")}`
                            : ""}
                          {` · conflict ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(parameterGroup.coordinationPolicy)}`}
                        </p>
                        {parameterGroup.helpNote.trim() ? (
                          <p className="run-note">{parameterGroup.helpNote}</p>
                        ) : null}
                        {dependencyRequests.length ? (
                          <p className="run-note">
                            Required by{" "}
                            {dependencyRequests
                              .map((request) => `${request.sourceGroupLabel} → ${request.sourceBundleLabel}`)
                              .join(", ")}
                            .
                          </p>
                        ) : null}
                        {conflictRequests.length ? (
                          <p className="run-note">
                            Conflict between{" "}
                            {conflictRequests.map((request) => request.bundleLabel).join(", ")}
                            {parameterGroup.coordinationPolicy === "manual_resolution"
                              ? " · waiting for manual selection."
                              : ` · resolved with ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(parameterGroup.coordinationPolicy)}.`}
                          </p>
                        ) : null}
                        {parameterGroup.presetBundles.length ? (
                          <div className="run-surface-query-builder-inline-grid">
                            <label className="run-surface-query-builder-control">
                              <span>Preset bundle</span>
                              <select
                                value={selectedBundleKey}
                                onChange={(event) => {
                                  const nextBundle =
                                    sortedPresetBundles.find((bundle) => bundle.key === event.target.value)
                                    ?? null;
                                  applyPredicateRefGroupPresetBundle(selectedRefTemplate.id, parameterGroup, nextBundle);
                                }}
                              >
                                <option value="">
                                  {autoSelectedBundleKey
                                    ? `Use auto-selected bundle (${effectiveBundle?.label ?? autoSelectedBundleKey})`
                                    : "No bundle"}
                                </option>
                                {sortedPresetBundles.map((bundle) => (
                                  <option key={`${parameterGroup.key}:${bundle.key}`} value={bundle.key}>
                                    {`${bundle.label}${bundle.priority ? ` · P${bundle.priority}` : ""}`}
                                  </option>
                                ))}
                              </select>
                              <small>
                                {selectedBundleKey
                                  ? (
                                      effectiveBundle?.helpNote
                                      || "Manual bundle override is active for this group."
                                    )
                                  : autoSelectedBundleKey
                                    ? (
                                        effectiveBundle?.helpNote
                                        || (
                                          dependencyRequests.length
                                            ? `Auto-selected to satisfy ${dependencyRequests[0]?.sourceGroupLabel ?? "group"} dependency at priority ${effectiveBundle?.priority ?? 0}.`
                                            : `Auto-selected by ${effectiveBundle?.autoSelectRule.replaceAll("_", " ") ?? "priority"} at priority ${effectiveBundle?.priority ?? 0}.`
                                        )
                                      )
                                    : "Apply a preset bundle to prefill bindings and literal values for this group."}
                              </small>
                            </label>
                          </div>
                        ) : null}
                        {unmetDependencies.length ? (
                          <p className="run-note">
                            Waiting on{" "}
                            {unmetDependencies
                              .map((dependency) => `${dependency.groupLabel} → ${dependency.bundleLabel}`)
                              .join(", ")}
                            .
                          </p>
                        ) : null}
                        {parameterGroup.presetBundles.length && policyTrace ? (
                          <div className="run-surface-query-builder-trace-panel">
                            <div className="run-surface-query-builder-card-head">
                              <strong>Policy explanation trace</strong>
                              <span className={`run-surface-query-builder-trace-status is-${policyTrace.tone}`}>
                                {policyTrace.statusLabel}
                              </span>
                            </div>
                            <p className="run-note">{policyTrace.summary}</p>
                            <div className="run-surface-query-builder-trace-list">
                              {policyTrace.steps.map((step) => (
                                <div
                                  className={`run-surface-query-builder-trace-step is-${step.tone}`}
                                  key={step.key}
                                >
                                  <strong>{step.title}</strong>
                                  <p>{step.detail}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : null}
                        {isGroupContentVisible ? (
                          <div className="run-surface-query-builder-parameter-grid">
                            {parameterGroup.parameters.map((parameter) => {
                              const rawBindingValue = predicateRefDraftBindings[parameter.key] ?? "";
                              const bindingReferenceKey = fromRunSurfaceCollectionQueryBindingReferenceValue(rawBindingValue);
                              const usesBindingReference = Boolean(bindingReferenceKey);
                              const bindingReferenceOptions = Array.from(
                                new Set([
                                  ...nestedTemplateBindingParameterKeys,
                                  bindingReferenceKey,
                                ].filter(Boolean)),
                              );
                              const literalOptions = Array.from(
                                new Set([
                                  ...parameter.options,
                                  rawBindingValue,
                                ].filter((value) => value && !isRunSurfaceCollectionQueryBindingReferenceValue(value))),
                              );
                              return (
                                <label className="run-surface-query-builder-control" key={`${selectedRefTemplate.id}:${parameter.key}`}>
                                  <span>{parameter.customLabel.trim() || parameter.label}</span>
                                  <label className="run-surface-query-builder-checkbox">
                                    <input
                                      checked={usesBindingReference}
                                      onChange={(event) =>
                                        setPredicateRefDraftBindings((current) => ({
                                          ...current,
                                          [parameter.key]: event.target.checked
                                            ? toRunSurfaceCollectionQueryBindingReferenceValue(
                                                bindingReferenceOptions[0] ?? parameter.key,
                                              )
                                            : "",
                                        }))}
                                      type="checkbox"
                                    />
                                    <span>Bind to outer template parameter</span>
                                  </label>
                                  {usesBindingReference ? (
                                    bindingReferenceOptions.length ? (
                                      <select
                                        value={bindingReferenceKey}
                                        onChange={(event) =>
                                          setPredicateRefDraftBindings((current) => ({
                                            ...current,
                                            [parameter.key]: toRunSurfaceCollectionQueryBindingReferenceValue(event.target.value),
                                          }))}
                                      >
                                        {bindingReferenceOptions.map((value) => (
                                          <option key={`${parameter.key}:binding:${value}`} value={value}>
                                            {value}
                                          </option>
                                        ))}
                                      </select>
                                    ) : (
                                      <input
                                        type="text"
                                        value={bindingReferenceKey}
                                        onChange={(event) =>
                                          setPredicateRefDraftBindings((current) => ({
                                            ...current,
                                            [parameter.key]: toRunSurfaceCollectionQueryBindingReferenceValue(event.target.value),
                                          }))}
                                        placeholder="outer_template_parameter"
                                      />
                                    )
                                  ) : parameter.options.length ? (
                                    <select
                                      value={rawBindingValue}
                                      onChange={(event) =>
                                        setPredicateRefDraftBindings((current) => ({
                                          ...current,
                                          [parameter.key]: event.target.value,
                                        }))}
                                    >
                                      {parameter.defaultValue.trim() ? (
                                        <option value="">Use template default</option>
                                      ) : null}
                                      {literalOptions.map((value) => (
                                        <option key={`${parameter.key}:${value}`} value={value}>
                                          {value}
                                        </option>
                                      ))}
                                    </select>
                                  ) : (
                                    <input
                                      type="text"
                                      value={rawBindingValue}
                                      onChange={(event) =>
                                        setPredicateRefDraftBindings((current) => ({
                                          ...current,
                                          [parameter.key]: event.target.value,
                                        }))}
                                      placeholder={
                                        parameter.defaultValue.trim()
                                          ? `${parameter.valueType} (blank uses default)`
                                          : parameter.valueType
                                      }
                                    />
                                  )}
                                  <small>
                                    {parameter.key} · {parameter.description ?? parameter.label} · {parameter.valueType}
                                    {parameter.groupName.trim() ? ` · group ${parameter.groupName}` : ""}
                                    {parameter.defaultValue.trim() ? ` · default ${parameter.defaultValue}` : ""}
                                    {parameter.bindingPreset.trim() ? ` · preset $${parameter.bindingPreset}` : ""}
                                    {usesBindingReference ? " · nested template binding" : ""}
                                  </small>
                                  {parameter.helpNote.trim() ? (
                                    <small>{parameter.helpNote}</small>
                                  ) : null}
                                </label>
                              );
                            })}
                          </div>
                        ) : null}
                      </div>
                    );
                  })}
                </div>
              ) : null}
              <div className="run-surface-query-builder-actions">
                <button
                  className="ghost-button"
                  disabled={!editorClauseState || !trimmedPredicateDraftKey || predicateKeyConflict || (editorTarget.kind === "predicate" && !selectedPredicateSupportsClauseEditing)}
                  onClick={savePredicateFromEditor}
                  type="button"
                >
                  {predicateSaveLabel}
                </button>
                <button
                  className="ghost-button"
                  disabled={!selectedSubtreeNode || !trimmedPredicateDraftKey || predicateKeyConflict}
                  onClick={saveSelectedSubtreeAsPredicate}
                  type="button"
                >
                  {subtreePromotionLabel}
                </button>
                <button
                  className="ghost-button"
                  disabled={
                    !editorClauseState
                    || !trimmedTemplateDraftKey
                    || templateKeyConflict
                    || (editorTarget.kind === "template" && !selectedTemplateSupportsClauseEditing)
                  }
                  onClick={saveTemplateFromEditor}
                  type="button"
                >
                  {templateSaveLabel}
                </button>
                <button
                  className="ghost-button"
                  disabled={!selectedSubtreeNode || !trimmedTemplateDraftKey || templateKeyConflict}
                  onClick={saveSelectedSubtreeAsTemplate}
                  type="button"
                >
                  {templatePromotionLabel}
                </button>
                <button
                  className="ghost-button"
                  disabled={!canAddPredicateRef}
                  onClick={addPredicateRefToExpression}
                  type="button"
                >
                  Add predicate ref
                </button>
              </div>
            </div>
          ) : null}
        </div>
        <div className="run-surface-query-builder-card">
          <div className="run-surface-query-builder-card-head">
            <strong>{expressionMode === "grouped" ? "Expression structure" : "Resolved metadata"}</strong>
            <span>{activeSchema.itemKind}</span>
          </div>
          {expressionMode === "grouped" ? (
            <>
              <div
                className={`run-surface-query-builder-group-card ${selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID ? "is-selected" : ""}`.trim()}
              >
                <div className="run-surface-query-builder-card-head">
                  <strong>Root group</strong>
                  <span>{groupLogic.toUpperCase()}</span>
                </div>
                <div className="run-surface-query-builder-inline-grid">
                  <label className="run-surface-query-builder-control">
                    <span>Root logic</span>
                    <select
                      onChange={(event) => setGroupLogic(event.target.value as "and" | "or")}
                      value={groupLogic}
                    >
                      <option value="and">and</option>
                      <option value="or">or</option>
                    </select>
                  </label>
                  <label className="run-surface-query-builder-checkbox">
                    <input
                      checked={rootNegated}
                      onChange={(event) => setRootNegated(event.target.checked)}
                      type="checkbox"
                    />
                    <span>Root negated</span>
                  </label>
                </div>
                <div className="run-surface-query-builder-actions">
                  <button
                    className={`ghost-button ${selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID ? "is-active" : ""}`.trim()}
                    onClick={() => setSelectedGroupId(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID)}
                    type="button"
                  >
                    {selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID ? "Targeting root group" : "Target root group"}
                  </button>
                </div>
                <div className="run-surface-query-builder-tree">
                  {expressionChildren.length ? (
                    expressionChildren.map((child) => renderExpressionChild(child))
                  ) : (
                    <p className="run-note">
                      Add clauses, predicate refs, or subgroups to build a nested boolean expression tree.
                    </p>
                  )}
                </div>
              </div>
              <div className="run-surface-query-builder-section">
                <div className="run-surface-query-builder-card-head">
                  <strong>Predicate registry</strong>
                  <span>{predicates.length}</span>
                </div>
                {predicates.length ? (
                  <div className="run-surface-query-builder-domain-list">
                    {predicates.map((predicate) => (
                      (() => {
                        const clauseNode = predicate.node.kind === "clause" ? predicate.node : null;
                        const isClausePredicate = Boolean(clauseNode);
                        return (
                          <div
                            className={`run-surface-query-builder-domain-card ${editorTarget.kind === "predicate" && editorTarget.predicateId === predicate.id ? "is-active" : ""}`.trim()}
                            key={predicate.id}
                          >
                            <div className="run-surface-query-builder-card-head">
                              <strong>{predicate.key}</strong>
                              <span>{isClausePredicate ? "predicate" : "subtree predicate"}</span>
                            </div>
                            <p className="run-note">
                              {formatRunSurfaceCollectionQueryBuilderChildSummary(predicate.node, contracts)}
                            </p>
                            <div className="run-surface-query-builder-actions">
                              {isClausePredicate ? (
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    setEditorTarget({ kind: "predicate", predicateId: predicate.id });
                                    setPredicateDraftKey(predicate.key);
                                    setTemplateDraftKey("");
                                    if (clauseNode) {
                                      setEditorFromClause(clauseNode.clause);
                                    }
                                  }}
                                  type="button"
                                >
                                  Edit predicate
                                </button>
                              ) : (
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    setEditorTarget({ kind: "predicate", predicateId: predicate.id });
                                    setPredicateDraftKey(predicate.key);
                                    setTemplateDraftKey("");
                                  }}
                                  type="button"
                                >
                                  Select subtree predicate
                                </button>
                              )}
                              <button
                                className="ghost-button"
                                onClick={() => removePredicate(predicate.id)}
                                type="button"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        );
                      })()
                    ))}
                  </div>
                ) : (
                  <p className="run-note">
                    Save a clause as a predicate to reuse it inside grouped expressions.
                  </p>
                )}
              </div>
              <div className="run-surface-query-builder-section">
                <div className="run-surface-query-builder-card-head">
                  <strong>Template registry</strong>
                  <span>{predicateTemplates.length}</span>
                </div>
                {predicateTemplates.length ? (
                  <div className="run-surface-query-builder-domain-list">
                    {predicateTemplates.map((template) => (
                      (() => {
                        const clauseNode = template.node.kind === "clause" ? template.node : null;
                        const isClauseTemplate = Boolean(clauseNode);
                        return (
                          <div
                            className={`run-surface-query-builder-domain-card ${editorTarget.kind === "template" && editorTarget.templateId === template.id ? "is-active" : ""}`.trim()}
                            key={template.id}
                          >
                            <div className="run-surface-query-builder-card-head">
                              <strong>{template.key}</strong>
                              <span>{isClauseTemplate ? "template" : "subtree template"}</span>
                            </div>
                            <p className="run-note">
                              {formatRunSurfaceCollectionQueryBuilderChildSummary(template.node, contracts)}
                            </p>
                            {template.parameters.length ? (
                              <div className="run-surface-query-builder-domain-list">
                                {groupRunSurfaceCollectionQueryBuilderTemplateParameters(
                                  template.parameters,
                                  template.parameterGroups,
                                ).map((parameterGroup) => {
                                  const groupViewKey = `registry:${template.id}:${parameterGroup.key}`;
                                  const isExpanded = isTemplateGroupExpanded(groupViewKey, parameterGroup.collapsedByDefault);
                                  return (
                                    <div
                                      className="run-surface-query-builder-section"
                                      key={`${template.id}:group:${parameterGroup.key}`}
                                    >
                                      <div className="run-surface-query-builder-card-head">
                                        <strong>{parameterGroup.label}</strong>
                                        <span>{parameterGroup.parameters.length}</span>
                                      </div>
                                      <div className="run-surface-query-builder-actions">
                                        <button
                                          className="ghost-button"
                                          onClick={() =>
                                            toggleTemplateGroupExpanded(groupViewKey, parameterGroup.collapsedByDefault)}
                                          type="button"
                                        >
                                          {isExpanded ? "Collapse group" : "Expand group"}
                                        </button>
                                      </div>
                                      <p className="run-note">
                                        {parameterGroup.collapsedByDefault
                                          ? "Collapsed by default in template consumers."
                                          : "Expanded by default in template consumers."}
                                        {parameterGroup.visibilityRule !== "always"
                                          ? ` · visibility ${parameterGroup.visibilityRule.replaceAll("_", " ")}`
                                          : ""}
                                        {` · conflict ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(parameterGroup.coordinationPolicy)}`}
                                      </p>
                                      {parameterGroup.helpNote.trim() ? (
                                        <p className="run-note">{parameterGroup.helpNote}</p>
                                      ) : null}
                                      {parameterGroup.presetBundles.length ? (
                                        <div className="run-surface-query-builder-domain-list">
                                          {getSortedTemplateGroupPresetBundles(parameterGroup.presetBundles).map((bundle) => (
                                            <div
                                              className="run-surface-query-builder-domain-card"
                                              key={`${template.id}:${parameterGroup.key}:bundle:${bundle.key}`}
                                            >
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>{bundle.label}</strong>
                                                <span>{bundle.key}</span>
                                              </div>
                                              <div className="run-surface-family-chip-row">
                                                <span className="run-surface-family-chip">
                                                  {`P${bundle.priority}`}
                                                </span>
                                                <span className="run-surface-family-chip">
                                                  {bundle.autoSelectRule === "manual"
                                                    ? "manual only"
                                                    : `auto ${bundle.autoSelectRule.replaceAll("_", " ")}`}
                                                </span>
                                                {bundle.dependencies.length ? (
                                                  <span className="run-surface-family-chip">
                                                    {`${bundle.dependencies.length} dependenc${bundle.dependencies.length === 1 ? "y" : "ies"}`}
                                                  </span>
                                                ) : null}
                                                {Object.keys(bundle.parameterValues).length ? (
                                                  <span className="run-surface-family-chip">
                                                    {`${Object.keys(bundle.parameterValues).length} preset value${Object.keys(bundle.parameterValues).length === 1 ? "" : "s"}`}
                                                  </span>
                                                ) : null}
                                                {Object.keys(bundle.parameterBindingPresets).length ? (
                                                  <span className="run-surface-family-chip">
                                                    {`${Object.keys(bundle.parameterBindingPresets).length} binding preset${Object.keys(bundle.parameterBindingPresets).length === 1 ? "" : "s"}`}
                                                  </span>
                                                ) : null}
                                              </div>
                                              {bundle.helpNote.trim() ? (
                                                <p className="run-note">{bundle.helpNote}</p>
                                              ) : null}
                                              {bundle.dependencies.length ? (
                                                <p className="run-note">
                                                  Requires{" "}
                                                  {bundle.dependencies
                                                    .map((dependency) => `${dependency.groupKey} → ${dependency.bundleKey}`)
                                                    .join(", ")}
                                                  .
                                                </p>
                                              ) : null}
                                            </div>
                                          ))}
                                        </div>
                                      ) : null}
                                      {isExpanded ? (
                                        <div className="run-surface-query-builder-domain-list">
                                          {parameterGroup.parameters.map((parameter) => (
                                            <div
                                              className="run-surface-query-builder-domain-card"
                                              key={`${template.id}:${parameter.key}`}
                                            >
                                              <div className="run-surface-query-builder-card-head">
                                                <strong>{parameter.customLabel.trim() || parameter.key}</strong>
                                                <span>{parameter.key}</span>
                                              </div>
                                              <div className="run-surface-family-chip-row">
                                                <span className="run-surface-family-chip">{parameter.valueType}</span>
                                                {parameter.defaultValue.trim() ? (
                                                  <span className="run-surface-family-chip">
                                                    {`default ${parameter.defaultValue}`}
                                                  </span>
                                                ) : null}
                                                {parameter.bindingPreset.trim() ? (
                                                  <span className="run-surface-family-chip">
                                                    {`preset $${parameter.bindingPreset}`}
                                                  </span>
                                                ) : null}
                                              </div>
                                              <p className="run-note">
                                                {parameter.description ?? parameter.label}
                                              </p>
                                              {parameter.helpNote.trim() ? (
                                                <p className="run-note">{parameter.helpNote}</p>
                                              ) : null}
                                            </div>
                                          ))}
                                        </div>
                                      ) : null}
                                    </div>
                                  );
                                })}
                              </div>
                            ) : null}
                            <div className="run-surface-query-builder-actions">
                              {isClauseTemplate ? (
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    setEditorTarget({ kind: "template", templateId: template.id });
                                    setTemplateDraftKey(template.key);
                                    setPredicateDraftKey("");
                                    if (clauseNode) {
                                      setEditorFromClause(clauseNode.clause);
                                    }
                                  }}
                                  type="button"
                                >
                                  Edit template
                                </button>
                              ) : (
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    setEditorTarget({ kind: "template", templateId: template.id });
                                    setTemplateDraftKey(template.key);
                                    setPredicateDraftKey("");
                                  }}
                                  type="button"
                                >
                                  Select subtree template
                                </button>
                              )}
                              <button
                                className="ghost-button"
                                onClick={() => removeTemplate(template.id)}
                                type="button"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        );
                      })()
                    ))}
                  </div>
                ) : (
                  <p className="run-note">
                    Bind clause values or collection path segments, then save them as reusable predicate templates.
                  </p>
                )}
              </div>
            </>
          ) : null}
          <p className="run-note">
            Resolved path: <code>{resolvedCollectionPath.join(".")}</code>
          </p>
          {parameterDomains.length ? (
            <div className="run-surface-query-builder-domain-list">
              {parameterDomains.map((parameterDomain) => (
                <div className="run-surface-query-builder-domain-card" key={`${parameterDomain.surfaceKey}:${parameterDomain.parameterKey}`}>
                  <strong>{parameterDomain.parameterKey}</strong>
                  <p className="run-note">
                    {parameterDomain.collectionLabel} · {parameterDomain.parameterKind}
                  </p>
                  {parameterDomain.domain?.source ? (
                    <p className="run-note">Domain source: {parameterDomain.domain.source}</p>
                  ) : null}
                  {parameterDomain.domain?.enumSource ? (
                    <p className="run-note">
                      Enum source: {parameterDomain.domain.enumSource.kind ?? "enum"} @ {parameterDomain.domain.enumSource.path.join(".")}
                    </p>
                  ) : null}
                  <div className="run-surface-family-chip-row">
                    {parameterDomain.domain?.values.map((value) => (
                      <span className="run-surface-family-chip" key={`${parameterDomain.parameterKey}:${value}`}>
                        {value}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="run-note">No parameter domains are declared for this collection path.</p>
          )}
          {(onApplyExpression || onClearExpression) ? (
            <div className="run-surface-query-builder-actions">
              {onApplyExpression ? (
                <button
                  className="ghost-button"
                  disabled={!canApplyExpression}
                  onClick={applyCurrentExpression}
                  type="button"
                >
                  {applyLabel}
                </button>
              ) : null}
              {onClearExpression ? (
                <button className="ghost-button" onClick={onClearExpression} type="button">
                  Clear active filter
                </button>
              ) : null}
            </div>
          ) : null}
          {activeExpression ? (
            <div className="run-surface-query-builder-active-state">
              <div className="run-surface-query-builder-card-head">
                <strong>Active filter</strong>
                <span>{activeExpressionLabel ?? "collection expression"}</span>
              </div>
              <pre className="run-surface-query-builder-preview">{activeExpression}</pre>
            </div>
          ) : null}
          <div className="run-surface-query-builder-active-state">
            <div className="run-surface-query-builder-card-head">
              <strong>Builder preview</strong>
              <span>{expressionMode === "grouped" ? groupedExpressionLabel : expressionLabel || "single expression"}</span>
            </div>
            <pre className="run-surface-query-builder-preview">{filterExpressionPreview || "{}"}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
