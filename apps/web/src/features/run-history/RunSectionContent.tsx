import {
  CSSProperties,
  KeyboardEvent,
  MouseEvent,
  forwardRef,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  getRunListBoundaryContractSnapshot,
  getRunListBoundarySurfaceLabel,
  getRunSurfaceCapabilityFamily,
  getRunSurfaceCapabilityFamilyOrder,
  getRunSurfaceCapabilityGroupOrder,
  getRunSurfaceCapabilitySchemaContract,
  getRunSurfaceCollectionQueryContracts,
  getRunSurfaceSharedContracts,
  getRunSurfaceSubresourceContracts,
  RunListComparisonBoundaryNote,
  shouldEnableReferenceProvenanceSemantics,
  shouldEnableRunListMetricDrillBack,
  shouldEnableRunSnapshotSemantics,
  shouldEnableStrategyCatalogSchemaHints,
  shouldHydratePresetParameterDefaults,
  shouldRenderOrderActionBoundaryNote,
  shouldRenderWorkflowControlBoundaryNote,
} from "../../runSurfaceCapabilities";
import {
  formatComparisonTooltipConflictSessionMetadata,
  formatComparisonTooltipConflictSessionSummary,
  formatComparisonTooltipConflictSessionSummarySession,
  formatComparisonTooltipPresetConflictGroupSummary,
  formatComparisonTooltipPresetImportFeedback,
  formatComparisonTooltipTuningDelta,
  formatComparisonTooltipTuningValue,
  formatRelativeTimestampLabel,
  getComparisonTooltipConflictSessionRelativeTimeRefreshMs,
  hashComparisonTooltipConflictSessionRaw,
  parseComparisonTooltipConflictSessionUpdatedAt,
} from "../comparisonTooltipFormatters";
import { RunSurfaceCollectionQueryBuilder } from "../query-builder";
import type {
  RunSurfaceCollectionQueryBuilderApplyPayload,
  RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
  RunSurfaceCollectionQueryRuntimeCandidateSample,
} from "../query-builder";
import {
  ALL_FILTER_VALUE,
  apiBase,
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
  COMPARISON_HISTORY_BROWSER_STATE_KEY,
  COMPARISON_HISTORY_BROWSER_STATE_VERSION,
  COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY,
  COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION,
  COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS,
  COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS,
  COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS,
  COMPARISON_HISTORY_TAB_ID_SESSION_KEY,
  COMPARISON_INTENT_SEARCH_PARAM,
  COMPARISON_RUN_ID_SEARCH_PARAM,
  COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY,
  COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION,
  COMPARISON_TOOLTIP_TUNING_GROUPS,
  COMPARISON_TOOLTIP_TUNING_LABELS,
  COMPARISON_TOOLTIP_TUNING_SHARE_PARAM,
  COMPARISON_TOOLTIP_TUNING_STORAGE_KEY,
  COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
  COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD,
  CONTROL_ROOM_UI_STATE_STORAGE_KEY,
  CONTROL_ROOM_UI_STATE_VERSION,
  DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY,
  DEFAULT_COMPARISON_TOOLTIP_TUNING,
  DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE,
  LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY,
  MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY,
  MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION,
  MAX_COMPARISON_HISTORY_PANEL_ENTRIES,
  MAX_COMPARISON_HISTORY_SYNC_AUDIT_ENTRIES,
  MAX_COMPARISON_RUNS,
  MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS,
  MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES,
  MAX_VISIBLE_GAP_WINDOWS,
  PRESET_PROFILE_AGGRESSIVENESS_RANKS,
  PRESET_PROFILE_CONFIDENCE_RANKS,
  PRESET_PROFILE_SPEED_RANKS,
  PRESET_TIMEFRAME_UNIT_TO_MINUTES,
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
  RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX,
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
  SHOW_COMPARISON_TOOLTIP_TUNING_PANEL,
  TOUCH_GAP_WINDOW_SWEEP_HOLD_MS,
  TOUCH_GAP_WINDOW_SWEEP_MOVE_TOLERANCE_PX,
} from "../../controlRoomDefinitions";
import type {
  BenchmarkArtifact,
  ParameterSchema,
  ComparisonCueKind,
  ComparisonHistoryBrowserState,
  ComparisonHistoryPanelEntry,
  ComparisonHistoryPanelState,
  ComparisonHistoryPanelSyncState,
  ComparisonHistoryStepDescriptor,
  ComparisonHistorySyncAuditEntry,
  ComparisonHistorySyncAuditFilter,
  ComparisonHistorySyncAuditKind,
  ComparisonHistorySyncAuditTrailState,
  ComparisonHistorySyncConflictFieldKey,
  ComparisonHistorySyncConflictFieldSource,
  ComparisonHistorySyncConflictReview,
  ComparisonHistorySyncConflictReviewGroup,
  ComparisonHistorySyncPreferenceFieldKey,
  ComparisonHistorySyncPreferenceReview,
  ComparisonHistorySyncPreferenceReviewRow,
  ComparisonHistorySyncPreferenceState,
  ComparisonHistorySyncWorkspaceRecommendationOverview,
  ComparisonHistorySyncWorkspaceReview,
  ComparisonHistorySyncWorkspaceReviewRow,
  ComparisonHistorySyncWorkspaceReviewSelectionKey,
  ComparisonHistorySyncWorkspaceSemanticSignal,
  ComparisonHistorySyncWorkspaceSignalDetailNestedKey,
  ComparisonHistorySyncWorkspaceSignalDetailSubviewKey,
  ComparisonHistorySyncWorkspaceSignalMicroInteractionKey,
  ComparisonHistorySyncWorkspaceSignalMicroViewKey,
  ComparisonHistorySyncWorkspaceState,
  ComparisonHistoryTabIdentity,
  ComparisonHistoryWriteMode,
  ComparisonIntent,
  ComparisonScoreDrillBackOptions,
  ComparisonScoreLinkedRunRole,
  ComparisonScoreLinkSource,
  ComparisonScoreLinkTarget,
  ComparisonScoreSection,
  ComparisonTooltipConflictSessionSummary,
  ComparisonTooltipConflictSessionSummarySession,
  ComparisonTooltipConflictSessionUiState,
  ComparisonTooltipConflictUiStateV1,
  ComparisonTooltipInteractionOptions,
  ComparisonTooltipLayout,
  ComparisonTooltipPendingPresetImportConflict,
  ComparisonTooltipPresetConflictPreviewGroup,
  ComparisonTooltipPresetConflictPreviewRow,
  ComparisonTooltipPresetImportConflictPolicy,
  ComparisonTooltipPresetImportResolution,
  ComparisonTooltipTargetProps,
  ComparisonTooltipTuning,
  ComparisonTooltipTuningPresetStateV1,
  ComparisonTooltipTuningShareImport,
  ComparisonTooltipTuningSinglePresetShareV1,
  ControlRoomComparisonHistoryPanelUiState,
  ControlRoomComparisonSelectionState,
  ControlRoomUiStateV1,
  ControlRoomUiStateV2,
  ControlRoomUiStateV3,
  ControlRoomUiStateV4,
  ExpandedGapWindowSelections,
  ExperimentPreset,
  ExperimentPresetRevision,
  GapWindowDragSelectionState,
  GuardedLiveStatus,
  MarketDataIngestionJobRecord,
  MarketDataProvenanceExportFilterState,
  MarketDataProvenanceExportHistoryEntry,
  MarketDataProvenanceExportSort,
  MarketDataProvenanceExportStateV1,
  MarketDataLineageHistoryRecord,
  MarketDataStatus,
  OperatorAlertMarketContextProvenance,
  OperatorAlertPrimaryFocus,
  OperatorVisibility,
  PendingTouchGapWindowSweepState,
  PresetDraftConflict,
  PresetRevisionDiff,
  PresetRevisionFilterState,
  PresetStructuredDiffDeltaValue,
  PresetStructuredDiffGroup,
  PresetStructuredDiffRow,
  ProviderProvenanceAnalyticsPresetEntry,
  ProviderProvenanceDashboardLayout,
  ProviderProvenanceDashboardViewEntry,
  ProviderProvenanceExportAnalyticsPayload,
  ProviderProvenanceExportJobEntry,
  ProviderProvenanceExportJobEscalationResult,
  ProviderProvenanceExportJobHistoryPayload,
  ProviderProvenanceExportJobPolicyResult,
  ProviderProvenanceSchedulerAlertHistoryPayload,
  ProviderProvenanceSchedulerHealthExportPayload,
  ProviderProvenanceSchedulerHealthAnalyticsPayload,
  ProviderProvenanceSchedulerHealthHistoryPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ProviderProvenanceSchedulerSearchModerationPlanListPayload,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload,
  ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult,
  ProviderProvenanceSchedulerSearchDashboardPayload,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload,
  ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
  ProviderProvenanceSchedulerStitchedReportViewEntry,
  ProviderProvenanceSchedulerStitchedReportViewRevisionEntry,
  ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeBulkGovernanceResult,
  ProviderProvenanceSchedulerNarrativeGovernancePlan,
  ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult,
  ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep,
  ProviderProvenanceSchedulerNarrativeGovernanceQueueView,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeRegistryEntry,
  ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry,
  ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeTemplateEntry,
  ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry,
  ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload,
  ProviderProvenanceScheduledReportEntry,
  ProviderProvenanceScheduledReportHistoryPayload,
  ProvenanceArtifactLineDetailView,
  ProvenanceArtifactLineMicroView,
  ReferenceSource,
  Run,
  RunComparison,
  RunHistoryFilter,
  RunHistorySurfaceKey,
  RunListBoundaryContract,
  RunListBoundaryEligibility,
  RunListBoundaryGroupKey,
  RunListBoundarySurfaceId,
  RunSurfaceCapabilities,
  RunSurfaceCapabilityFamily,
  RunSurfaceCapabilityFamilyContract,
  RunSurfaceCapabilityFamilyKey,
  RunSurfaceCapabilitySchemaContract,
  RunSurfaceCapabilitySurfaceKey,
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
  RunSurfaceSharedContract,
  RunSurfaceSubresourceContract,
  SavedRunHistoryFilterPreset,
  SavedRunHistoryFilterPresetStateV1,
  Strategy,
  TouchGapWindowActivationFeedbackState,
  TouchGapWindowHoldProgressState,
} from "../../controlRoomDefinitions";
import type {
  RunOrderControls,
  RunSectionComparisonControls,
  RunSectionRerunAction,
} from "../../routes/runHistoryWorkspacePanels";
import * as controlRoomViewHelpers from "../../control-room/ControlRoomViewHelpers";

const {
  DEFAULT_COMPARISON_INTENT,
  ExperimentMetadataPills,
  Metric,
  applyResolvedComparisonHistoryPanelEntry,
  areRunHistoryFiltersEquivalent,
  benchmarkArtifactSectionLabels,
  benchmarkArtifactSectionOrder,
  benchmarkArtifactSummaryLabels,
  benchmarkArtifactSummaryOrder,
  buildComparisonCellTooltip,
  buildComparisonHistorySyncWorkspaceRecommendationOverview,
  buildComparisonHistoryExpandedGapRowSelectionKey,
  buildComparisonHistoryExpandedGapWindowSelectionKey,
  buildComparisonHistorySyncAuditEntries,
  buildComparisonHistorySyncAuditId,
  buildComparisonHistorySyncConflictReview,
  buildComparisonHistorySyncConflictReviewGroups,
  buildComparisonHistorySyncPreferenceReview,
  buildComparisonHistorySyncPreferenceReviewRows,
  buildComparisonHistorySyncPreferenceState,
  buildComparisonHistorySyncWorkspaceRecommendedSources,
  buildComparisonHistorySyncWorkspaceReview,
  buildComparisonHistorySyncWorkspaceReviewRows,
  buildComparisonHistorySyncWorkspaceState,
  buildComparisonMetricTooltipKey,
  buildComparisonProvenanceArtifactLineDetailHoverKey,
  buildComparisonProvenanceArtifactSectionLineHoverKey,
  buildComparisonProvenanceArtifactSectionSubFocusKey,
  buildComparisonProvenanceArtifactSubFocusKey,
  buildComparisonProvenanceArtifactSummaryHoverKey,
  buildComparisonProvenanceLineSubFocusKey,
  buildComparisonRunCardLineSubFocusKey,
  buildComparisonRunListDataSymbolSubFocusKey,
  buildComparisonRunListLineSubFocusKey,
  buildComparisonRunListOrderPreviewSubFocusKey,
  buildComparisonScoreDetailRows,
  buildComparisonScoreHighlights,
  buildGapWindowSelectionLookup,
  buildGapWindowSelectionUpdate,
  buildGapWindowKey,
  buildLegacyGapWindowKey,
  buildLiveOrderDraftKey,
  buildRunHistorySavedFilterStorageKey,
  cloneRunHistoryFilter,
  comparisonIntentOptions,
  decodeComparisonScoreLinkToken,
  defaultRunHistoryFilter,
  describeRunHistoryFilter,
  encodeComparisonScoreLinkToken,
  extractDefaultParameters,
  filterExpandedGapRows,
  filterExpandedGapWindowSelections,
  formatBenchmarkArtifactInlineValue,
  formatBenchmarkArtifactSectionEntries,
  formatBenchmarkArtifactSectionLabel,
  formatBenchmarkArtifactSectionLines,
  formatBenchmarkArtifactSectionValue,
  formatBenchmarkArtifactSummaryEntries,
  formatBenchmarkArtifactSummaryLabel,
  formatBenchmarkArtifactSummaryValue,
  formatComparisonCueTooltip,
  formatComparisonDelta,
  formatComparisonHistoryExpandedGapRowKey,
  formatComparisonHistoryExpandedGapRowsDiffValue,
  formatComparisonHistoryExpandedGapRowsValue,
  formatComparisonHistoryPanelEntryMeta,
  formatComparisonHistorySyncAuditKindLabel,
  formatComparisonHistorySyncConflictFieldValue,
  formatComparisonHistorySyncConflictResolutionSummary,
  formatComparisonHistorySyncConflictRunSelectionValue,
  formatComparisonHistorySyncConflictScoreLinkValue,
  formatComparisonHistorySyncPreferenceFieldValue,
  formatComparisonHistorySyncPreferenceResolutionSummary,
  formatComparisonHistorySyncWorkspaceFieldValue,
  formatComparisonHistorySyncWorkspaceResolutionSummary,
  formatComparisonHistorySyncWorkspaceSelectionKeyLabel,
  formatComparisonIntentLabel,
  formatComparisonIntentLegend,
  formatComparisonIntentTooltip,
  formatComparisonMetric,
  formatComparisonNarrativeLabel,
  formatComparisonScoreComponentDetail,
  formatComparisonScoreComponentLabel,
  formatComparisonScoreComponentRawValue,
  formatComparisonScoreHighlight,
  formatComparisonScoreLinkArtifactHoverLabel,
  formatComparisonScoreLinkArtifactLineDetailHoverLabel,
  formatComparisonScoreLinkArtifactLineDetailViewLabel,
  formatComparisonScoreLinkArtifactLineMicroViewLabel,
  formatComparisonScoreLinkSourceLabel,
  formatComparisonScoreLinkSubFocusLabel,
  formatComparisonScoreLinkTooltipLabel,
  formatComparisonScoreSignedValue,
  formatComparisonScoreValue,
  formatEditableNumber,
  formatFixedNumber,
  formatGapWindowKeyLabel,
  formatLaneLabel,
  formatLineageIndicator,
  formatLineagePosture,
  formatMetric,
  formatParameterMap,
  formatParameterValue,
  formatProviderRecoverySchema,
  formatProviderRecoveryTelemetry,
  formatRange,
  formatTimestamp,
  formatVersionLineage,
  getComparisonScoreLinkedRunRole,
  getComparisonIntentClassName,
  getStrategyVersionOptions,
  hasComparisonHistorySyncConflictFieldDifference,
  hasComparisonHistorySyncPreferenceFieldDifference,
  hasComparisonHistorySyncWorkspaceFieldDifference,
  hasRunHistoryFilterCriteria,
  instrumentGapRowKey,
  isComparisonScoreLinkMatch,
  isSameComparisonHistoryExpandedGapRows,
  isSameComparisonScoreLinkSurface,
  isSameComparisonScoreLinkTarget,
  isSameComparisonSelection,
  isSameExpandedGapWindowSelections,
  isSameGapWindowSelectionList,
  limitComparisonHistoryPanelEntries,
  listComparisonHistoryExpandedGapRowDiffKeys,
  listComparisonHistoryExpandedGapRowKeys,
  listComparisonHistoryExpandedGapWindowDiffKeys,
  listComparisonHistorySyncWorkspaceConflictSelectionKeys,
  listComparisonHistorySyncWorkspaceDiffSelectionKeys,
  loadLegacyExpandedGapRows,
  loadSavedRunHistoryFilterPresets,
  matchesComparisonHistoryPanelEntry,
  normalizeComparisonIntent,
  normalizeComparisonRunIdList,
  normalizeComparisonScoreLinkArtifactHoverKey,
  normalizeComparisonScoreLinkArtifactLineDetailHoverKey,
  normalizeComparisonScoreLinkArtifactLineDetailView,
  normalizeComparisonScoreLinkArtifactLineMicroView,
  normalizeComparisonScoreLinkArtifactLineNotePage,
  normalizeComparisonScoreLinkArtifactLineScrubStep,
  normalizeComparisonScoreLinkExpandedState,
  normalizeComparisonScoreLinkSource,
  normalizeComparisonScoreLinkSubFocusKey,
  normalizeComparisonScoreLinkTarget,
  normalizeComparisonScoreLinkTooltipKey,
  normalizeComparisonScoreSection,
  normalizeControlRoomComparisonSelection,
  normalizeExpandedGapWindowSelectionList,
  parseComparisonHistoryExpandedGapRowSelectionKey,
  parseComparisonHistoryExpandedGapWindowSelectionKey,
  parseGapWindowKey,
  persistSavedRunHistoryFilterPresets,
  rankComparisonHistorySyncWorkspaceFieldSemantics,
  rankComparisonHistorySyncWorkspaceSelectionKey,
  resolveComparisonHistorySyncConflictReviewEntry,
  resolveComparisonHistorySyncPreferenceReview,
  resolveComparisonHistorySyncWorkspaceFieldSource,
  resolveComparisonHistorySyncWorkspaceReview,
  resolveComparisonScoreDrillBackTarget,
  resolveGapWindowSelectionList,
  sanitizeRunHistoryFilter,
  scoreComparisonHistorySyncWorkspaceCandidateSource,
  shortenIdentifier,
  sortComparisonHistoryPanelEntries,
  sortComparisonHistorySyncWorkspaceSemanticSignals,
  summarizeComparisonHistoryPanelEntryConflict,
  summarizeComparisonHistorySyncPreferenceChanges,
  summarizeComparisonHistorySyncWorkspaceChanges,
  summarizeRunNotes,
  truncateLabel,
} = controlRoomViewHelpers;

export function RunSection({
  surfaceKey,
  title,
  runs,
  presets,
  runSurfaceCapabilities,
  strategies,
  filter,
  setFilter,
  comparison,
  rerunActions,
  onStop,
  getOrderControls,
}: {
  surfaceKey: RunHistorySurfaceKey;
  title: string;
  runs: Run[];
  presets: ExperimentPreset[];
  runSurfaceCapabilities: RunSurfaceCapabilities | null;
  strategies: Strategy[];
  filter: RunHistoryFilter;
  setFilter: (updater: (value: RunHistoryFilter) => RunHistoryFilter) => void;
  comparison?: RunSectionComparisonControls;
  rerunActions?: RunSectionRerunAction[];
  onStop?: (runId: string) => Promise<void>;
  getOrderControls?: (run: Run) => RunOrderControls | null;
}) {
  const workspaceReviewRowRefs = useRef(new Map<string, HTMLDivElement>());
  const runListCardRefs = useRef(new Map<string, HTMLElement>());
  const runListSubFocusRefs = useRef(new Map<string, HTMLElement>());
  const runListArtifactHoverRefs = useRef(new Map<string, HTMLElement>());
  const [collectionBuilderOpen, setCollectionBuilderOpen] = useState(false);
  const [savedFilterDraftName, setSavedFilterDraftName] = useState("");
  const [savedFilters, setSavedFilters] = useState<SavedRunHistoryFilterPreset[]>(() =>
    loadSavedRunHistoryFilterPresets(surfaceKey),
  );
  const versionOptions = getStrategyVersionOptions(strategies, filter.strategy_id);
  const sharedRunListBoundaryContract = runSurfaceCapabilities?.comparison_eligibility_contract ?? null;
  const collectionQueryContracts = useMemo(
    () => getRunSurfaceCollectionQueryContracts(runSurfaceCapabilities),
    [runSurfaceCapabilities],
  );
  const presetOptions = presets.filter(
    (preset) =>
      !preset.strategy_id ||
      filter.strategy_id === ALL_FILTER_VALUE ||
      preset.strategy_id === filter.strategy_id,
  );
  const filterSummaryParts = useMemo(
    () => describeRunHistoryFilter(filter, presets, strategies),
    [filter, presets, strategies],
  );
  const activeSavedFilterId = useMemo(
    () =>
      savedFilters.find((entry) => areRunHistoryFiltersEquivalent(entry.filter, filter))?.filter_id ?? null,
    [filter, savedFilters],
  );
  useEffect(() => {
    setSavedFilters(loadSavedRunHistoryFilterPresets(surfaceKey));
  }, [surfaceKey]);
  useEffect(() => {
    persistSavedRunHistoryFilterPresets(surfaceKey, savedFilters);
  }, [savedFilters, surfaceKey]);
  const applyCollectionQueryExpression = (payload: RunSurfaceCollectionQueryBuilderApplyPayload) => {
    setFilter((current) => ({
      ...current,
      filter_expr: payload.expression,
      collection_query_label:
        payload.expressionLabel || `${payload.quantifier} ${payload.fieldKey} ${payload.operatorKey}`,
    }));
  };
  const clearCollectionQueryExpression = () => {
    setFilter((current) => ({
      ...current,
      filter_expr: "",
      collection_query_label: "",
    }));
  };
  const saveCurrentFilter = () => {
    const trimmedName = savedFilterDraftName.trim();
    if (!trimmedName || !hasRunHistoryFilterCriteria(filter)) {
      return;
    }
    const snapshot = cloneRunHistoryFilter(filter);
    const now = new Date().toISOString();
    setSavedFilters((current) => {
      const existing = current.find(
        (entry) => entry.label.trim().toLowerCase() === trimmedName.toLowerCase(),
      );
      if (existing) {
        return current.map((entry) =>
          entry.filter_id === existing.filter_id
            ? {
                ...entry,
                filter: snapshot,
                label: trimmedName,
                updated_at: now,
              }
            : entry,
        );
      }
      return [
        {
          filter_id: `${surfaceKey}:${Date.now()}`,
          label: trimmedName,
          filter: snapshot,
          created_at: now,
          updated_at: now,
        },
        ...current,
      ];
    });
    setSavedFilterDraftName("");
  };
  const applySavedFilter = (savedFilter: SavedRunHistoryFilterPreset) => {
    setFilter(() => cloneRunHistoryFilter(savedFilter.filter));
  };
  const deleteSavedFilter = (filterId: string) => {
    setSavedFilters((current) => current.filter((entry) => entry.filter_id !== filterId));
  };
  const historySearchQueryNormalized = comparison?.historySearchQuery.trim().toLowerCase() ?? "";
  const filteredHistoryEntries = comparison
    ? comparison.visibleHistoryEntries.filter((entry) => {
        if (comparison.showPinnedHistoryOnly && !entry.pinned) {
          return false;
        }
        if (!historySearchQueryNormalized) {
          return true;
        }
        return matchesComparisonHistoryPanelEntry(entry, historySearchQueryNormalized);
      })
    : [];
  const activeHistoryEntry = comparison
    ? comparison.visibleHistoryEntries.find((entry) => entry.entryId === comparison.activeHistoryEntryId) ?? null
    : null;
  const pinnedHistoryCount = comparison
    ? comparison.visibleHistoryEntries.filter((entry) => entry.pinned).length
    : 0;
  const filteredHistorySyncAuditEntries = comparison
    ? comparison.historySyncAuditTrail
        .slice()
        .reverse()
        .filter((entry) => {
          if (!comparison.showResolvedHistoryAudits) {
            const resolvedAt =
              entry.conflictReview?.resolvedAt
              ?? entry.preferenceReview?.resolvedAt
              ?? entry.workspaceReview?.resolvedAt
              ?? null;
            if (resolvedAt) {
              return false;
            }
          }
          if (comparison.historyAuditFilter === "conflicts") {
            return entry.kind === "conflict";
          }
          if (comparison.historyAuditFilter === "preferences") {
            return entry.kind === "preferences";
          }
          if (comparison.historyAuditFilter === "workspace") {
            return entry.kind === "workspace";
          }
          if (comparison.historyAuditFilter === "merges") {
            return entry.kind === "merge";
          }
          return true;
        })
    : [];
  const buildWorkspaceReviewRowSelectionId = (
    auditId: string,
    fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
  ) => `${auditId}:${fieldKey}`;
  const buildWorkspaceReviewSignalSelectionId = (
    source: ComparisonHistorySyncConflictFieldSource,
    signal: ComparisonHistorySyncWorkspaceSemanticSignal,
    index: number,
  ) => `${source}:${index}:${signal.label}:${signal.weight}`;
  const buildWorkspaceReviewSignalSubviewSelectionId = (
    scoreDetailKey: string,
    subviewKey: ComparisonHistorySyncWorkspaceSignalDetailSubviewKey,
  ) => `${scoreDetailKey}:${subviewKey}`;
  const buildWorkspaceReviewSignalNestedSubviewSelectionId = (
    scoreDetailKey: string,
    subviewKey: ComparisonHistorySyncWorkspaceSignalDetailSubviewKey,
    nestedKey: ComparisonHistorySyncWorkspaceSignalDetailNestedKey,
  ) => `${scoreDetailKey}:${subviewKey}:${nestedKey}`;
  const buildWorkspaceReviewSignalMicroInteractionSelectionId = (
    nestedSubviewId: string,
    microViewKey: ComparisonHistorySyncWorkspaceSignalMicroViewKey,
  ) => `${nestedSubviewId}:${microViewKey}`;
  const resolveWorkspaceReviewSignalMicroView = (
    nestedSubviewId: string,
    options: ComparisonHistorySyncWorkspaceSignalMicroViewKey[],
  ) => {
    const persistedValue = comparison?.focusedWorkspaceScoreSignalMicroViews[nestedSubviewId];
    if (persistedValue && options.includes(persistedValue)) {
      return persistedValue;
    }
    return options[0];
  };
  const resolveWorkspaceReviewSignalMicroInteraction = (
    interactionId: string,
    options: ComparisonHistorySyncWorkspaceSignalMicroInteractionKey[],
  ) => {
    const persistedValue = comparison?.focusedWorkspaceScoreSignalMicroInteractions[interactionId];
    if (persistedValue && options.includes(persistedValue)) {
      return persistedValue;
    }
    return options[0];
  };
  const resolveWorkspaceReviewSignalMicroHoverTarget = (
    interactionId: string,
    options: string[],
  ) => {
    const persistedValue = comparison?.hoveredWorkspaceScoreSignalMicroTargets[interactionId];
    if (persistedValue && options.includes(persistedValue)) {
      return persistedValue;
    }
    return options[0];
  };
  const resolveWorkspaceReviewSignalMicroScrubStep = (
    interactionId: string,
    stepCount: number,
  ) => {
    const persistedValue = comparison?.scrubbedWorkspaceScoreSignalMicroSteps[interactionId];
    if (typeof persistedValue === "number" && Number.isInteger(persistedValue)) {
      return Math.max(0, Math.min(stepCount - 1, persistedValue));
    }
    return 0;
  };
  const resolveWorkspaceReviewSignalMicroNotePage = (
    interactionId: string,
    noteCount: number,
  ) => {
    const persistedValue = comparison?.selectedWorkspaceScoreSignalMicroNotePages[interactionId];
    if (typeof persistedValue === "number" && Number.isInteger(persistedValue)) {
      return Math.max(0, Math.min(noteCount - 1, persistedValue));
    }
    return 0;
  };
  const registerRunListCardRef = (runId: string) => (node: HTMLElement | null) => {
    if (node) {
      runListCardRefs.current.set(runId, node);
      return;
    }
    runListCardRefs.current.delete(runId);
  };
  const registerRunListSubFocusRef = (runId: string, subFocusKey: string) => (node: HTMLElement | null) => {
    const key = `${runId}:${subFocusKey}`;
    if (node) {
      runListSubFocusRefs.current.set(key, node);
      return;
    }
    runListSubFocusRefs.current.delete(key);
  };
  const registerRunListArtifactHoverRef = (runId: string, artifactHoverKey: string) => (node: HTMLElement | null) => {
    const key = `${runId}:${artifactHoverKey}`;
    if (node) {
      runListArtifactHoverRefs.current.set(key, node);
      return;
    }
    runListArtifactHoverRefs.current.delete(key);
  };
  useEffect(() => {
    const selectedRunListScoreLink =
      comparison?.selectedScoreLink?.source === "run_list"
        ? comparison.selectedScoreLink
        : null;
    if (!selectedRunListScoreLink) {
      return;
    }
    const scrollOptions: ScrollIntoViewOptions = {
      behavior: "smooth",
      block: "nearest",
    };
    if (selectedRunListScoreLink.artifactHoverKey) {
      const artifactHoverTarget = runListArtifactHoverRefs.current.get(
        `${selectedRunListScoreLink.originRunId ?? selectedRunListScoreLink.narrativeRunId}:${selectedRunListScoreLink.artifactHoverKey}`,
      );
      if (artifactHoverTarget) {
        artifactHoverTarget.scrollIntoView(scrollOptions);
        return;
      }
    }
    if (selectedRunListScoreLink.subFocusKey) {
      const subFocusTarget = runListSubFocusRefs.current.get(
        `${selectedRunListScoreLink.originRunId ?? selectedRunListScoreLink.narrativeRunId}:${selectedRunListScoreLink.subFocusKey}`,
      );
      if (subFocusTarget) {
        subFocusTarget.scrollIntoView(scrollOptions);
        return;
      }
    }
    const cardTarget = runListCardRefs.current.get(
      selectedRunListScoreLink.originRunId ?? selectedRunListScoreLink.narrativeRunId,
    );
    cardTarget?.scrollIntoView(scrollOptions);
  }, [comparison?.selectedScoreLink]);
  const activeRunListRuntimeCandidateSelection = useMemo<RunSurfaceCollectionQueryRuntimeCandidateContextSelection | null>(
    () => (
      comparison?.selectedScoreLink?.source === "run_list"
        ? {
            artifactHoverKey: comparison.selectedScoreLink.artifactHoverKey,
            componentKey: comparison.selectedScoreLink.componentKey,
            runId: comparison.selectedScoreLink.originRunId ?? comparison.selectedScoreLink.narrativeRunId,
            section: comparison.selectedScoreLink.section,
            subFocusKey: comparison.selectedScoreLink.subFocusKey,
          }
        : null
    ),
    [comparison?.selectedScoreLink],
  );
  const handleRunListScoreLinkSelection = (
    runId: string,
    section: ComparisonScoreSection,
    componentKey: string,
    options?: ComparisonScoreDrillBackOptions,
  ) => {
    if (!comparison) {
      return;
    }
    const nextSelection: ComparisonScoreLinkTarget = {
      artifactDetailExpanded: options?.artifactDetailExpanded ?? null,
      artifactHoverKey: options?.artifactHoverKey ?? null,
      artifactLineDetailExpanded: options?.artifactLineDetailExpanded ?? null,
      artifactLineDetailHoverKey: options?.artifactLineDetailHoverKey ?? null,
      artifactLineDetailScrubStep: options?.artifactLineDetailScrubStep ?? null,
      artifactLineDetailView: options?.artifactLineDetailView ?? null,
      artifactLineMicroView: options?.artifactLineMicroView ?? null,
      artifactLineNotePage: options?.artifactLineNotePage ?? null,
      componentKey,
      detailExpanded: options?.detailExpanded ?? null,
      narrativeRunId: runId,
      originRunId: runId,
      section,
      source: "run_list" as const,
      subFocusKey: options?.subFocusKey ?? null,
      tooltipKey: options?.tooltipKey ?? null,
    };
    comparison.onChangeSelectedScoreLink(
      isSameComparisonScoreLinkTarget(comparison.selectedScoreLink, nextSelection)
        ? null
        : nextSelection,
      options?.historyMode,
    );
  };
  const focusRunListRuntimeCandidateContext = (
    sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
    options?: { artifactHoverKey?: string | null },
  ) => {
    if (
      comparison
      && sample.runContextSection
      && sample.runContextComponentKey
    ) {
      handleRunListScoreLinkSelection(
        sample.runId,
        sample.runContextSection,
        sample.runContextComponentKey,
        {
          artifactHoverKey: options?.artifactHoverKey ?? null,
          subFocusKey: sample.runContextSubFocusKey,
        },
      );
      return;
    }
    const scrollOptions: ScrollIntoViewOptions = {
      behavior: "smooth",
      block: "nearest",
    };
    if (sample.runContextSubFocusKey) {
      const subFocusTarget = runListSubFocusRefs.current.get(
        `${sample.runId}:${sample.runContextSubFocusKey}`,
      );
      if (subFocusTarget) {
        subFocusTarget.scrollIntoView(scrollOptions);
        return;
      }
    }
    const cardTarget = runListCardRefs.current.get(sample.runId);
    cardTarget?.scrollIntoView(scrollOptions);
  };
  const renderWorkspaceReviewSignalMicroState = (params: {
    interactionId: string;
    hoverOptions: Array<{ key: string; label: string; copy: string }>;
    scrubCopies: string[];
    notePages: Array<{ label: string; copy: string }>;
  }) => {
    const { interactionId, hoverOptions, scrubCopies, notePages } = params;
    if (!comparison || !hoverOptions.length || !scrubCopies.length || !notePages.length) {
      return null;
    }
    const hoverTarget = resolveWorkspaceReviewSignalMicroHoverTarget(
      interactionId,
      hoverOptions.map((option) => option.key),
    );
    const scrubStep = resolveWorkspaceReviewSignalMicroScrubStep(interactionId, scrubCopies.length);
    const notePage = resolveWorkspaceReviewSignalMicroNotePage(interactionId, notePages.length);
    const activeHoverOption = hoverOptions.find((option) => option.key === hoverTarget) ?? hoverOptions[0];
    const activeNotePage = notePages[notePage] ?? notePages[0];
    return (
      <div className="comparison-history-conflict-review-score-detail-ephemeral">
        <div className="comparison-history-conflict-review-score-detail-ephemeral-group">
          <span className="comparison-history-conflict-review-score-detail-ephemeral-label">
            Hover memory
          </span>
          <div className="comparison-history-conflict-review-score-detail-ephemeral-chip-row">
            {hoverOptions.map((option) => (
              <button
                aria-pressed={hoverTarget === option.key}
                className={`comparison-history-conflict-review-score-detail-ephemeral-chip ${
                  hoverTarget === option.key ? "is-active" : ""
                }`}
                key={option.key}
                onClick={() =>
                  comparison.onChangeWorkspaceScoreSignalMicroHoverTarget(interactionId, option.key)
                }
                onFocus={() =>
                  comparison.onChangeWorkspaceScoreSignalMicroHoverTarget(interactionId, option.key)
                }
                onMouseEnter={() =>
                  comparison.onChangeWorkspaceScoreSignalMicroHoverTarget(interactionId, option.key)
                }
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
          <p className="comparison-history-conflict-review-score-detail-ephemeral-copy">
            {activeHoverOption.copy}
          </p>
        </div>
        <div className="comparison-history-conflict-review-score-detail-ephemeral-group">
          <span className="comparison-history-conflict-review-score-detail-ephemeral-label">
            Scrub memory
          </span>
          <div className="comparison-history-conflict-review-score-detail-ephemeral-chip-row">
            {scrubCopies.map((copy, index) => (
              <button
                aria-pressed={scrubStep === index}
                className={`comparison-history-conflict-review-score-detail-ephemeral-chip ${
                  scrubStep === index ? "is-active" : ""
                }`}
                key={`scrub:${index}`}
                onClick={() => comparison.onChangeWorkspaceScoreSignalMicroScrubStep(interactionId, index)}
                type="button"
              >
                Step {index + 1}
              </button>
            ))}
          </div>
          <p className="comparison-history-conflict-review-score-detail-ephemeral-copy">
            {scrubCopies[scrubStep] ?? scrubCopies[0]}
          </p>
        </div>
        <div className="comparison-history-conflict-review-score-detail-ephemeral-group">
          <div className="comparison-history-conflict-review-score-detail-ephemeral-note-head">
            <span className="comparison-history-conflict-review-score-detail-ephemeral-label">
              Note memory
            </span>
            <div className="comparison-history-conflict-review-score-detail-ephemeral-note-actions">
              <button
                className="comparison-history-conflict-review-score-detail-ephemeral-nav"
                disabled={notePage === 0}
                onClick={() => comparison.onChangeWorkspaceScoreSignalMicroNotePage(interactionId, notePage - 1)}
                type="button"
              >
                Prev
              </button>
              <span className="comparison-history-conflict-review-score-detail-ephemeral-note-index">
                {notePage + 1} / {notePages.length}
              </span>
              <button
                className="comparison-history-conflict-review-score-detail-ephemeral-nav"
                disabled={notePage >= notePages.length - 1}
                onClick={() => comparison.onChangeWorkspaceScoreSignalMicroNotePage(interactionId, notePage + 1)}
                type="button"
              >
                Next
              </button>
            </div>
          </div>
          <p className="comparison-history-conflict-review-score-detail-ephemeral-note-title">
            {activeNotePage.label}
          </p>
          <p className="comparison-history-conflict-review-score-detail-ephemeral-copy">
            {activeNotePage.copy}
          </p>
        </div>
      </div>
    );
  };
  const resolveWorkspaceReviewSignalSelectionId = (
    source: ComparisonHistorySyncConflictFieldSource,
    signals: ComparisonHistorySyncWorkspaceSemanticSignal[],
    persistedSignalKey?: string | null,
  ) => {
    const signalKeys = signals.map((signal, index) =>
      buildWorkspaceReviewSignalSelectionId(source, signal, index),
    );
    if (persistedSignalKey && signalKeys.includes(persistedSignalKey)) {
      return persistedSignalKey;
    }
    return signalKeys[0] ?? null;
  };
  const buildWorkspaceReviewSignalDetail = (params: {
    row: ComparisonHistorySyncWorkspaceReviewRow;
    source: ComparisonHistorySyncConflictFieldSource;
    persistedSignalKey?: string | null;
  }) => {
    const { row, source, persistedSignalKey } = params;
    const signals = source === "local" ? row.localSignals : row.remoteSignals;
    const signalKey = resolveWorkspaceReviewSignalSelectionId(source, signals, persistedSignalKey);
    if (!signalKey) {
      return null;
    }
    const signalIndex = signals.findIndex((signal, index) =>
      buildWorkspaceReviewSignalSelectionId(source, signal, index) === signalKey,
    );
    if (signalIndex < 0) {
      return null;
    }
    const signal = signals[signalIndex];
    const totalAbsoluteWeight = signals.reduce((total, candidate) => total + Math.abs(candidate.weight), 0);
    const laneScore = source === "local" ? row.localScore : row.remoteScore;
    const shareOfVisibleWeight = totalAbsoluteWeight > 0
      ? Math.abs(signal.weight) / totalAbsoluteWeight
      : 1;
    const sourceLabel = source === "local"
      ? row.hasLatestLocalDrift
        ? "Local latest"
        : "Local"
      : row.hasLatestLocalDrift
        ? "Remote audit"
        : "Remote";
    const contributionLabel =
      signal.weight > 0
        ? "Adds semantic support to this lane"
        : signal.weight < 0
          ? "Pulls semantic confidence out of this lane"
          : "Neutral semantic signal";
    const recommendationRelationship =
      source === row.recommendedSource
        ? signal.weight >= 0
          ? "Supports the ranked recommendation"
          : "Pushes against the ranked recommendation"
        : signal.weight >= 0
          ? "Supports the non-ranked alternative"
          : "Weakens the non-ranked alternative";
    return {
      contributionLabel,
      laneScore,
      rank: signalIndex + 1,
      recommendationRelationship,
      shareOfVisibleWeight,
      signal,
      signalCount: signals.length,
      signalKey,
      source,
      sourceLabel,
    };
  };
  const activateWorkspaceReviewRow = (
    auditId: string,
    fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
  ) => {
    comparison?.onChangeActiveWorkspaceOverviewRowId(
      buildWorkspaceReviewRowSelectionId(auditId, fieldKey),
    );
  };
  const focusWorkspaceReviewRow = (
    auditId: string,
    fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
    preferredScoreSource?: ComparisonHistorySyncConflictFieldSource,
    preferredSignalKey?: string | null,
  ) => {
    const scoreDetailKey = buildWorkspaceReviewRowSelectionId(auditId, fieldKey);
    comparison?.onChangeActiveWorkspaceOverviewRowId(scoreDetailKey);
    if (
      comparison
      && preferredScoreSource
      && !comparison.focusedWorkspaceScoreDetailSources[scoreDetailKey]
    ) {
      comparison.onChangeFocusedWorkspaceScoreDetailSource(scoreDetailKey, preferredScoreSource);
    }
    if (
      comparison
      && preferredSignalKey
      && !comparison.focusedWorkspaceScoreDetailSignalKeys[scoreDetailKey]
    ) {
      comparison.onChangeFocusedWorkspaceScoreDetailSignalKey(scoreDetailKey, preferredSignalKey);
    }
    if (comparison && !comparison.expandedWorkspaceScoreDetailIds[scoreDetailKey]) {
      comparison.onToggleWorkspaceScoreDetail(scoreDetailKey);
    }
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const row = workspaceReviewRowRefs.current.get(scoreDetailKey);
        if (!row) {
          return;
        }
        row.scrollIntoView({
          block: "center",
          behavior: "smooth",
        });
        row.focus({
          preventScroll: true,
        });
      });
    });
  };

  return (
    <section className="panel panel-wide">
      <div className="section-heading">
        <div>
          <p className="kicker">Execution plane</p>
          <h2>{title}</h2>
        </div>
        <div className="section-controls">
          <div className="filter-bar">
            <label>
              Strategy
              <select
                value={filter.strategy_id}
                onChange={(event) =>
                  setFilter((current) => {
                    const strategyId = event.target.value;
                    const nextVersionOptions = getStrategyVersionOptions(strategies, strategyId);
                    const nextVersion = nextVersionOptions.includes(current.strategy_version)
                      ? current.strategy_version
                      : ALL_FILTER_VALUE;
                    return {
                      ...current,
                      strategy_id: strategyId,
                      strategy_version: nextVersion,
                    };
                  })
                }
              >
                <option value={ALL_FILTER_VALUE}>All strategies</option>
                {strategies.map((strategy) => (
                  <option key={strategy.strategy_id} value={strategy.strategy_id}>
                    {strategy.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Version
              <select
                value={filter.strategy_version}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    strategy_version: event.target.value,
                  }))
                }
              >
                <option value={ALL_FILTER_VALUE}>All versions</option>
                {versionOptions.map((version) => (
                  <option key={version} value={version}>
                    {version}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Preset
              <select
                value={filter.preset_id}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    preset_id: event.target.value,
                  }))
                }
              >
                <option value="">All presets</option>
                {presetOptions.map((preset) => (
                  <option key={preset.preset_id} value={preset.preset_id}>
                    {preset.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Benchmark
              <input
                placeholder="All families"
                value={filter.benchmark_family}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    benchmark_family: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              Tag
              <input
                placeholder="baseline"
                value={filter.tag}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    tag: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              Dataset
              <input
                placeholder="dataset-v1:..."
                value={filter.dataset_identity}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    dataset_identity: event.target.value,
                  }))
                }
              />
            </label>
          </div>
          <div className="run-filter-workbench">
            <div className="run-filter-workbench-head">
              <div className="run-filter-workbench-actions">
                {collectionQueryContracts.length ? (
                  <button
                    className={`ghost-button ${collectionBuilderOpen ? "is-active" : ""}`.trim()}
                    onClick={() => setCollectionBuilderOpen((current) => !current)}
                    type="button"
                  >
                    {collectionBuilderOpen ? "Hide collection builder" : "Collection builder"}
                  </button>
                ) : null}
                {filter.filter_expr ? (
                  <button className="ghost-button" onClick={clearCollectionQueryExpression} type="button">
                    Clear collection filter
                  </button>
                ) : null}
              </div>
              <div className="run-filter-save-row">
                <input
                  className="run-filter-save-input"
                  onChange={(event) => setSavedFilterDraftName(event.target.value)}
                  placeholder="Save current filter as…"
                  value={savedFilterDraftName}
                />
                <button
                  className="ghost-button"
                  disabled={!savedFilterDraftName.trim() || !hasRunHistoryFilterCriteria(filter)}
                  onClick={saveCurrentFilter}
                  type="button"
                >
                  Save filter
                </button>
              </div>
            </div>
            {filterSummaryParts.length ? (
              <div className="run-filter-summary-chip-row">
                {filterSummaryParts.map((part) => (
                  <span className="run-filter-summary-chip" key={part}>
                    {part}
                  </span>
                ))}
              </div>
            ) : (
              <p className="run-note">No active run-history filters. Saved filters can capture both basic filters and collection expressions.</p>
            )}
            {savedFilters.length ? (
              <div className="run-filter-saved-list">
                {savedFilters.map((savedFilter) => {
                  const summary = describeRunHistoryFilter(savedFilter.filter, presets, strategies);
                  const isActive = savedFilter.filter_id === activeSavedFilterId;
                  return (
                    <article
                      className={`run-filter-saved-card ${isActive ? "is-active" : ""}`.trim()}
                      key={savedFilter.filter_id}
                    >
                      <div className="run-filter-saved-card-head">
                        <strong>{savedFilter.label}</strong>
                        <span>{formatRelativeTimestampLabel(savedFilter.updated_at)}</span>
                      </div>
                      <p className="run-note">
                        {summary.length ? summary.join(" · ") : "All runs"}
                      </p>
                      <div className="run-filter-saved-card-actions">
                        <button
                          className={`ghost-button ${isActive ? "is-active" : ""}`.trim()}
                          onClick={() => applySavedFilter(savedFilter)}
                          type="button"
                        >
                          {isActive ? "Applied" : "Apply"}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => deleteSavedFilter(savedFilter.filter_id)}
                          type="button"
                        >
                          Delete
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : null}
            {collectionBuilderOpen && collectionQueryContracts.length ? (
              <RunSurfaceCollectionQueryBuilder
                activeExpression={filter.filter_expr}
                activeExpressionLabel={filter.collection_query_label}
                activeRuntimeCandidateRunContext={activeRunListRuntimeCandidateSelection}
                applyLabel="Apply to run list"
                contracts={collectionQueryContracts}
                onApplyExpression={applyCollectionQueryExpression}
                onClearExpression={filter.filter_expr ? clearCollectionQueryExpression : null}
                onFocusRuntimeCandidateRunContext={focusRunListRuntimeCandidateContext}
                runtimeRuns={runs}
              />
            ) : null}
          </div>
          {comparison ? (
            <div className="comparison-toolbar">
              <div className="comparison-history-step" aria-live="polite">
                <p className="comparison-history-step-label">{comparison.historyStep.label}</p>
                <p className="comparison-history-step-summary">{comparison.historyStep.summary}</p>
              </div>
              <button className="ghost-button" onClick={comparison.onToggleHistoryBrowser} type="button">
                {comparison.historyBrowserOpen
                  ? "Hide history browser"
                  : `History browser (${comparison.visibleHistoryEntries.length})`}
              </button>
              <span>
                Compare {comparison.selectedRunIds.length} / {MAX_COMPARISON_RUNS}
              </span>
              <label className="comparison-intent-field">
                Intent
                <select
                  value={comparison.comparisonIntent}
                  onChange={(event) => comparison.onChangeComparisonIntent(event.target.value as ComparisonIntent)}
                >
                  {comparisonIntentOptions.map((intent) => (
                    <option key={intent} value={intent}>
                      {formatComparisonIntentLabel(intent)}
                    </option>
                  ))}
                </select>
              </label>
              <button className="ghost-button" onClick={comparison.onSelectBenchmarkPair} type="button">
                Benchmark native vs NFI
              </button>
              <button
                className="ghost-button"
                disabled={!comparison.selectedRunIds.length}
                onClick={comparison.onClearSelection}
                type="button"
              >
                Clear compare
              </button>
              {comparison.historyBrowserOpen ? (
                <div className="comparison-history-browser">
                  <div className="comparison-history-browser-head">
                    <div>
                      <p className="comparison-history-browser-title">Comparison history browser</p>
                      <p className="comparison-history-browser-copy">
                        Jump directly to an earlier comparison step from this browser session.
                      </p>
                    </div>
                    <div className="comparison-history-browser-actions">
                      <button
                        className="ghost-button"
                        disabled={!comparison.canNavigateHistoryBackward}
                        onClick={() => comparison.onNavigateHistoryRelative(-1)}
                        type="button"
                      >
                        Back step
                      </button>
                      <button
                        className="ghost-button"
                        disabled={!comparison.canNavigateHistoryForward}
                        onClick={() => comparison.onNavigateHistoryRelative(1)}
                        type="button"
                      >
                        Forward step
                      </button>
                      <button
                        className="ghost-button"
                        disabled={!activeHistoryEntry}
                        onClick={() =>
                          activeHistoryEntry
                            ? comparison.onToggleHistoryEntryPinned(activeHistoryEntry.entryId)
                            : undefined
                        }
                        type="button"
                      >
                        {activeHistoryEntry?.pinned ? "Unpin current" : "Pin current"}
                      </button>
                      <button
                        className="ghost-button"
                        disabled={!comparison.historyEntries.some(
                          (entry) => !entry.hidden && !entry.pinned && entry.entryId !== comparison.activeHistoryEntryId,
                        )}
                        onClick={comparison.onTrimHistoryEntries}
                        type="button"
                      >
                        Clear unpinned
                      </button>
                    </div>
                  </div>
                  <div className="comparison-history-browser-manage">
                    <label className="comparison-history-browser-search">
                      Search steps
                      <input
                        onChange={(event) => comparison.onChangeHistorySearchQuery(event.target.value)}
                        placeholder="intent, label, summary"
                        value={comparison.historySearchQuery}
                      />
                    </label>
                    <button
                      className={`ghost-button ${comparison.showPinnedHistoryOnly ? "is-active" : ""}`}
                      onClick={() =>
                        comparison.onChangeShowPinnedHistoryOnly(!comparison.showPinnedHistoryOnly)
                      }
                      type="button"
                    >
                      {comparison.showPinnedHistoryOnly
                        ? "Showing pinned only"
                        : `Pinned only (${pinnedHistoryCount})`}
                    </button>
                    <label className="comparison-history-browser-search comparison-history-browser-audit-filter">
                      Audit view
                      <select
                        onChange={(event) =>
                          comparison.onChangeHistoryAuditFilter(
                            event.target.value as ComparisonHistorySyncAuditFilter,
                          )
                        }
                        value={comparison.historyAuditFilter}
                      >
                        <option value="all">All audit events</option>
                        <option value="conflicts">Conflicts only</option>
                        <option value="preferences">Browser preferences</option>
                        <option value="workspace">Workspace state</option>
                        <option value="merges">Merges only</option>
                      </select>
                    </label>
                    <button
                      className={`ghost-button ${comparison.showResolvedHistoryAudits ? "is-active" : ""}`}
                      onClick={() =>
                        comparison.onChangeShowResolvedHistoryAudits(!comparison.showResolvedHistoryAudits)
                      }
                      type="button"
                    >
                      {comparison.showResolvedHistoryAudits ? "Showing resolved audits" : "Hiding resolved audits"}
                    </button>
                  </div>
                  <div className="comparison-history-browser-sync">
                    <div className="comparison-history-browser-sync-head">
                      <div className="comparison-history-browser-sync-identity">
                        <span
                          className="comparison-history-browser-entry-badge sync"
                          title={comparison.historyTabIdentity.tabId}
                        >
                          {comparison.historyTabIdentity.label}
                        </span>
                        <p className="comparison-history-browser-copy">
                          This tab owns a local conflict audit trail for cross-tab history sync.
                        </p>
                      </div>
                      <p className="comparison-history-browser-sync-status">
                        {comparison.historySharedSync
                          ? `Last shared update: ${
                              comparison.historySharedSync.tabId === comparison.historyTabIdentity.tabId
                                ? "This tab"
                                : comparison.historySharedSync.tabLabel
                            } · ${formatRelativeTimestampLabel(comparison.historySharedSync.updatedAt)}`
                          : "Last shared update: none yet"}
                      </p>
                    </div>
                    {comparison.historySyncAuditTrail.length ? (
                      filteredHistorySyncAuditEntries.length ? (
                      <div className="comparison-history-browser-audit-list">
                        {filteredHistorySyncAuditEntries.map((entry) => {
                            const conflictReview = entry.conflictReview;
                            const preferenceReview = entry.preferenceReview;
                            const workspaceReview = entry.workspaceReview;
                            const conflictGroups = conflictReview
                              ? buildComparisonHistorySyncConflictReviewGroups(conflictReview)
                              : [];
                            const preferenceRows = preferenceReview
                              ? buildComparisonHistorySyncPreferenceReviewRows(preferenceReview)
                              : [];
                            const workspaceRows = workspaceReview
                              ? buildComparisonHistorySyncWorkspaceReviewRows(
                                  workspaceReview,
                                  comparison.latestWorkspaceSyncState,
                                )
                              : [];
                            const workspaceOverview = workspaceReview
                              ? buildComparisonHistorySyncWorkspaceRecommendationOverview(workspaceRows)
                              : null;
                            const activeWorkspaceOverviewRow = workspaceOverview
                              ? workspaceRows.find(
                                  (row) =>
                                    buildWorkspaceReviewRowSelectionId(entry.auditId, row.fieldKey)
                                      === comparison.activeWorkspaceOverviewRowId,
                                ) ?? null
                              : null;
                            const strongestWorkspaceOverviewRowId =
                              workspaceOverview?.strongest
                                ? buildWorkspaceReviewRowSelectionId(
                                    entry.auditId,
                                    workspaceOverview.strongest.fieldKey,
                                  )
                                : null;
                            const flatReviewRows = preferenceReview ? preferenceRows : workspaceRows;
                            const reviewFieldCount = conflictReview
                              ? conflictGroups.reduce((total, group) => total + group.rows.length, 0)
                              : flatReviewRows.length;
                            const localChoiceCount = conflictReview
                              ? conflictGroups.reduce(
                                  (total, group) =>
                                    total + group.rows.filter((row) => row.selectedSource === "local").length,
                                  0,
                                )
                              : flatReviewRows.filter((row) => row.selectedSource === "local").length;
                            const remoteChoiceCount = reviewFieldCount - localChoiceCount;
                            const reviewExpanded = Boolean(
                              comparison.expandedHistoryConflictReviewIds[entry.auditId],
                            );
                            const reviewResolvedAt =
                              conflictReview?.resolvedAt
                              ?? preferenceReview?.resolvedAt
                              ?? workspaceReview?.resolvedAt
                              ?? null;
                            const reviewResolutionSummary =
                              conflictReview?.resolutionSummary
                              ?? preferenceReview?.resolutionSummary
                              ?? workspaceReview?.resolutionSummary
                              ?? null;
                            return (
                              <article
                                className={`comparison-history-browser-audit ${
                                  reviewResolvedAt ? "is-resolved" : ""
                                }`}
                                key={entry.auditId}
                              >
                                <div className="comparison-history-browser-audit-head">
                                  <span
                                    className={`comparison-history-browser-entry-badge sync-audit ${entry.kind}`}
                                  >
                                    {formatComparisonHistorySyncAuditKindLabel(entry.kind)}
                                  </span>
                                  <strong>{entry.summary}</strong>
                                </div>
                                <p className="comparison-history-browser-entry-summary">{entry.detail}</p>
                                <p className="comparison-history-browser-entry-meta">
                                  {entry.sourceTabLabel} · {formatRelativeTimestampLabel(entry.recordedAt)}
                                </p>
                                {conflictReview || preferenceReview || workspaceReview ? (
                                  <>
                                    <div className="comparison-history-browser-audit-actions">
                                      <button
                                        className="ghost-button"
                                        onClick={() => comparison.onToggleHistoryConflictReview(entry.auditId)}
                                        type="button"
                                      >
                                        {reviewExpanded
                                          ? "Hide field review"
                                          : `Review ${reviewFieldCount} field${reviewFieldCount === 1 ? "" : "s"}`}
                                      </button>
                                      <span
                                        className={`comparison-history-browser-audit-status ${
                                          reviewResolvedAt ? "is-resolved" : "is-pending"
                                        }`}
                                      >
                                        {reviewResolvedAt
                                          ? `Resolved ${formatRelativeTimestampLabel(reviewResolvedAt)}`
                                          : "Pending manual review"}
                                      </span>
                                    </div>
                                    {reviewResolutionSummary ? (
                                      <p className="comparison-history-browser-entry-meta">
                                        {reviewResolutionSummary}
                                      </p>
                                    ) : null}
                                    {reviewExpanded ? (
                                      <div className="comparison-history-browser-conflict-review">
                                        <div className="comparison-history-browser-conflict-actions">
                                          <p className="comparison-history-browser-entry-meta">
                                            {localChoiceCount} local / {remoteChoiceCount} remote selections
                                          </p>
                                          <div className="comparison-history-browser-entry-actions">
                                            {conflictReview ? (
                                              <>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onSetHistoryConflictFieldSourceAll(entry.auditId, "local")
                                                  }
                                                  type="button"
                                                >
                                                  Use local all
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onSetHistoryConflictFieldSourceAll(entry.auditId, "remote")
                                                  }
                                                  type="button"
                                                >
                                                  Use remote all
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onApplyHistoryConflictResolution(entry.auditId)
                                                  }
                                                  type="button"
                                                >
                                                  {conflictReview.resolvedAt ? "Apply updated resolution" : "Apply resolution"}
                                                </button>
                                              </>
                                            ) : preferenceReview ? (
                                              <>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onSetHistoryPreferenceFieldSourceAll(entry.auditId, "local")
                                                  }
                                                  type="button"
                                                >
                                                  Use local all
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onSetHistoryPreferenceFieldSourceAll(entry.auditId, "remote")
                                                  }
                                                  type="button"
                                                >
                                                  Use remote all
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onApplyHistoryPreferenceResolution(entry.auditId)
                                                  }
                                                  type="button"
                                                >
                                                  {preferenceReview.resolvedAt ? "Apply updated resolution" : "Apply resolution"}
                                                </button>
                                              </>
                                            ) : workspaceReview ? (
                                              <>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onSetHistoryWorkspaceFieldSourceAll(entry.auditId, "local")
                                                  }
                                                  type="button"
                                                >
                                                  Use local all
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onSetHistoryWorkspaceFieldSourceAll(entry.auditId, "remote")
                                                  }
                                                  type="button"
                                                >
                                                  Use remote all
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onUseHistoryWorkspaceRankedSources(entry.auditId)
                                                  }
                                                  type="button"
                                                >
                                                  Use ranked picks
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() =>
                                                    comparison.onApplyHistoryWorkspaceResolution(entry.auditId)
                                                  }
                                                  type="button"
                                                >
                                                  {workspaceReview.resolvedAt ? "Apply updated resolution" : "Apply resolution"}
                                                </button>
                                              </>
                                            ) : null}
                                          </div>
                                        </div>
                                        <div className="comparison-dev-conflict-preview comparison-history-conflict-review">
                                          {workspaceOverview ? (
                                            <div className="comparison-history-conflict-review-overview">
                                              {activeWorkspaceOverviewRow ? (
                                                <button
                                                  className="comparison-history-conflict-review-overview-card is-active is-interactive"
                                                  onClick={() =>
                                                    focusWorkspaceReviewRow(
                                                      entry.auditId,
                                                      activeWorkspaceOverviewRow.fieldKey,
                                                      activeWorkspaceOverviewRow.recommendedSource,
                                                      resolveWorkspaceReviewSignalSelectionId(
                                                        activeWorkspaceOverviewRow.recommendedSource,
                                                        activeWorkspaceOverviewRow.recommendedSource === "local"
                                                          ? activeWorkspaceOverviewRow.localSignals
                                                          : activeWorkspaceOverviewRow.remoteSignals,
                                                      ),
                                                    )
                                                  }
                                                  type="button"
                                                >
                                                  <span className="comparison-history-conflict-review-overview-label">
                                                    Active row
                                                  </span>
                                                  <strong>{activeWorkspaceOverviewRow.label}</strong>
                                                  <span className="comparison-history-conflict-review-overview-copy">
                                                    {activeWorkspaceOverviewRow.recommendedSource === "local"
                                                      ? "Local latest"
                                                      : "Remote audit"} selected · {formatComparisonScoreValue(activeWorkspaceOverviewRow.recommendationStrength)} point recommendation gap
                                                  </span>
                                                </button>
                                              ) : null}
                                              <div className="comparison-history-conflict-review-overview-card">
                                                <span className="comparison-history-conflict-review-overview-label">
                                                  Ranked split
                                                </span>
                                                <strong>
                                                  {workspaceOverview.localCount} local latest / {workspaceOverview.remoteCount} remote audit
                                                </strong>
                                                <span className="comparison-history-conflict-review-overview-copy">
                                                  {workspaceOverview.rankedDiffCount > 0
                                                    ? `${workspaceOverview.rankedDiffCount} field${workspaceOverview.rankedDiffCount === 1 ? "" : "s"} currently differ from ranked picks`
                                                    : "Current selections already match ranked picks"}
                                                </span>
                                              </div>
                                              <div className="comparison-history-conflict-review-overview-card">
                                                <span className="comparison-history-conflict-review-overview-label">
                                                  Latest local drift
                                                </span>
                                                <strong>
                                                  {workspaceOverview.latestLocalDriftCount} / {workspaceOverview.totalFieldCount}
                                                </strong>
                                                <span className="comparison-history-conflict-review-overview-copy">
                                                  {workspaceOverview.latestLocalDriftCount > 0
                                                    ? "Fields changed after the audit snapshot"
                                                    : "No field drift since the audit snapshot"}
                                                </span>
                                              </div>
                                              <button
                                                className={`comparison-history-conflict-review-overview-card is-strongest ${
                                                  workspaceOverview.strongest
                                                    ? "is-interactive"
                                                    : ""
                                                } ${
                                                  strongestWorkspaceOverviewRowId === comparison.activeWorkspaceOverviewRowId
                                                    ? "is-active"
                                                    : ""
                                                }`}
                                                disabled={!workspaceOverview.strongest}
                                                onClick={() =>
                                                  workspaceOverview.strongest
                                                    ? focusWorkspaceReviewRow(
                                                        entry.auditId,
                                                        workspaceOverview.strongest.fieldKey,
                                                        workspaceOverview.strongest.recommendedSource,
                                                        resolveWorkspaceReviewSignalSelectionId(
                                                          workspaceOverview.strongest.recommendedSource,
                                                          workspaceOverview.strongest.recommendedSource === "local"
                                                            ? workspaceOverview.strongest.localSignals
                                                            : workspaceOverview.strongest.remoteSignals,
                                                        ),
                                                      )
                                                    : undefined
                                                }
                                                type="button"
                                              >
                                                <span className="comparison-history-conflict-review-overview-label">
                                                  Strongest recommendation
                                                </span>
                                                {workspaceOverview.strongest ? (
                                                  <>
                                                    <strong>
                                                      {workspaceOverview.strongest.label}
                                                    </strong>
                                                    <span className="comparison-history-conflict-review-overview-copy">
                                                      {workspaceOverview.strongest.recommendedSource === "local" ? "Local latest" : "Remote audit"} by {formatComparisonScoreValue(workspaceOverview.strongest.recommendationStrength)} points
                                                    </span>
                                                  </>
                                                ) : (
                                                  <span className="comparison-history-conflict-review-overview-copy">
                                                    No workspace conflicts to rank.
                                                  </span>
                                                )}
                                              </button>
                                              {workspaceOverview.topLocal.length ? (
                                                <div className="comparison-history-conflict-review-overview-lane">
                                                  <span className="comparison-history-conflict-review-overview-lane-label">
                                                    Top local latest picks
                                                  </span>
                                                  <div className="comparison-history-conflict-review-overview-chip-list">
                                                    {workspaceOverview.topLocal.map((row) => {
                                                      const scoreDetailKey = buildWorkspaceReviewRowSelectionId(
                                                        entry.auditId,
                                                        row.fieldKey,
                                                      );
                                                      return (
                                                        <button
                                                          className={`comparison-history-conflict-review-overview-chip is-local ${
                                                            comparison.activeWorkspaceOverviewRowId === scoreDetailKey
                                                              ? "is-active"
                                                              : ""
                                                          }`}
                                                          onClick={() =>
                                                            focusWorkspaceReviewRow(
                                                              entry.auditId,
                                                              row.fieldKey,
                                                              row.recommendedSource,
                                                              resolveWorkspaceReviewSignalSelectionId(
                                                                row.recommendedSource,
                                                                row.recommendedSource === "local"
                                                                  ? row.localSignals
                                                                  : row.remoteSignals,
                                                              ),
                                                            )
                                                          }
                                                          key={`overview-local:${entry.auditId}:${row.fieldKey}`}
                                                          type="button"
                                                        >
                                                          {row.label} · +{formatComparisonScoreValue(row.recommendationStrength)}
                                                        </button>
                                                      );
                                                    })}
                                                  </div>
                                                </div>
                                              ) : null}
                                              {workspaceOverview.topRemote.length ? (
                                                <div className="comparison-history-conflict-review-overview-lane">
                                                  <span className="comparison-history-conflict-review-overview-lane-label">
                                                    Top remote audit picks
                                                  </span>
                                                  <div className="comparison-history-conflict-review-overview-chip-list">
                                                    {workspaceOverview.topRemote.map((row) => {
                                                      const scoreDetailKey = buildWorkspaceReviewRowSelectionId(
                                                        entry.auditId,
                                                        row.fieldKey,
                                                      );
                                                      return (
                                                        <button
                                                          className={`comparison-history-conflict-review-overview-chip is-remote ${
                                                            comparison.activeWorkspaceOverviewRowId === scoreDetailKey
                                                              ? "is-active"
                                                              : ""
                                                          }`}
                                                          onClick={() =>
                                                            focusWorkspaceReviewRow(
                                                              entry.auditId,
                                                              row.fieldKey,
                                                              row.recommendedSource,
                                                              resolveWorkspaceReviewSignalSelectionId(
                                                                row.recommendedSource,
                                                                row.recommendedSource === "local"
                                                                  ? row.localSignals
                                                                  : row.remoteSignals,
                                                              ),
                                                            )
                                                          }
                                                          key={`overview-remote:${entry.auditId}:${row.fieldKey}`}
                                                          type="button"
                                                        >
                                                          {row.label} · +{formatComparisonScoreValue(row.recommendationStrength)}
                                                        </button>
                                                      );
                                                    })}
                                                  </div>
                                                </div>
                                              ) : null}
                                            </div>
                                          ) : null}
                                          <div className="comparison-dev-conflict-preview-row comparison-dev-conflict-preview-head">
                                            <span>
                                              {conflictReview ? "Field" : preferenceReview ? "Preference" : "Workspace field"}
                                            </span>
                                            <span>Keep local</span>
                                            <span>Keep remote</span>
                                          </div>
                                          {conflictReview
                                            ? conflictGroups.map((group) => (
                                                <div className="comparison-dev-conflict-preview-group" key={group.key}>
                                                  <div className="comparison-dev-conflict-preview-group-title">
                                                    <span>{group.label}</span>
                                                    <span className="comparison-dev-conflict-preview-group-meta">
                                                      <span className="comparison-dev-conflict-preview-group-summary">
                                                        {group.summaryLabel}
                                                      </span>
                                                    </span>
                                                  </div>
                                                  {group.rows.map((row) => (
                                                    <div
                                                      className="comparison-history-conflict-review-row"
                                                      key={`${entry.auditId}:${row.fieldKey}`}
                                                    >
                                                      <span className="comparison-dev-conflict-preview-label-group">
                                                        <span className="comparison-dev-conflict-preview-label">
                                                          {row.label}
                                                        </span>
                                                      </span>
                                                      <button
                                                        className={`comparison-history-conflict-review-choice ${
                                                          row.selectedSource === "local" ? "is-selected" : ""
                                                        }`}
                                                        onClick={() =>
                                                          comparison.onSetHistoryConflictFieldSource(
                                                            entry.auditId,
                                                            row.fieldKey,
                                                            "local",
                                                          )
                                                        }
                                                        type="button"
                                                      >
                                                        <span className="comparison-history-conflict-review-choice-label">
                                                          Local
                                                        </span>
                                                        <span className="comparison-history-conflict-review-choice-value">
                                                          {row.localValue}
                                                        </span>
                                                      </button>
                                                      <button
                                                        className={`comparison-history-conflict-review-choice ${
                                                          row.selectedSource === "remote" ? "is-selected" : ""
                                                        }`}
                                                        onClick={() =>
                                                          comparison.onSetHistoryConflictFieldSource(
                                                            entry.auditId,
                                                            row.fieldKey,
                                                            "remote",
                                                          )
                                                        }
                                                        type="button"
                                                      >
                                                        <span className="comparison-history-conflict-review-choice-label">
                                                          Remote
                                                        </span>
                                                        <span className="comparison-history-conflict-review-choice-value">
                                                          {row.remoteValue}
                                                        </span>
                                                      </button>
                                                    </div>
                                                  ))}
                                                </div>
                                              ))
                                            : workspaceReview
                                              ? workspaceRows.map((row) => {
                                                  const scoreDetailKey = buildWorkspaceReviewRowSelectionId(
                                                    entry.auditId,
                                                    row.fieldKey,
                                                  );
                                                  const scoreDetailsExpanded = Boolean(
                                                    comparison.expandedWorkspaceScoreDetailIds[scoreDetailKey],
                                                  );
                                                  const focusedScoreDetailSource =
                                                    comparison.focusedWorkspaceScoreDetailSources[
                                                      scoreDetailKey
                                                    ] ?? row.recommendedSource;
                                                  const focusedScoreDetailSignalKey =
                                                    comparison.focusedWorkspaceScoreDetailSignalKeys[
                                                      scoreDetailKey
                                                    ] ?? null;
                                                  const signalDetailExpanded = Boolean(
                                                    comparison.expandedWorkspaceScoreSignalDetailIds[
                                                      scoreDetailKey
                                                    ],
                                                  );
                                                  const rowActive =
                                                    comparison.activeWorkspaceOverviewRowId === scoreDetailKey;
                                                  const resolvedLocalSignalFocusKey =
                                                    focusedScoreDetailSource === "local"
                                                      ? resolveWorkspaceReviewSignalSelectionId(
                                                          "local",
                                                          row.localSignals,
                                                          focusedScoreDetailSignalKey,
                                                        )
                                                      : null;
                                                  const resolvedRemoteSignalFocusKey =
                                                    focusedScoreDetailSource === "remote"
                                                      ? resolveWorkspaceReviewSignalSelectionId(
                                                          "remote",
                                                          row.remoteSignals,
                                                          focusedScoreDetailSignalKey,
                                                        )
                                                      : null;
                                                  const focusedSignalDetail =
                                                    buildWorkspaceReviewSignalDetail({
                                                      row,
                                                      source: focusedScoreDetailSource,
                                                      persistedSignalKey: focusedScoreDetailSignalKey,
                                                    });
                                                  const interpretationSubviewId =
                                                    buildWorkspaceReviewSignalSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "interpretation",
                                                    );
                                                  const lanePositionSubviewId =
                                                    buildWorkspaceReviewSignalSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "lanePosition",
                                                    );
                                                  const recommendationContextSubviewId =
                                                    buildWorkspaceReviewSignalSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "recommendationContext",
                                                    );
                                                  const interpretationLaneSemanticsNestedId =
                                                    buildWorkspaceReviewSignalNestedSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "interpretation",
                                                      "laneSemantics",
                                                    );
                                                  const interpretationRecommendationEffectNestedId =
                                                    buildWorkspaceReviewSignalNestedSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "interpretation",
                                                      "recommendationEffect",
                                                    );
                                                  const lanePositionRankContextNestedId =
                                                    buildWorkspaceReviewSignalNestedSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "lanePosition",
                                                      "rankContext",
                                                    );
                                                  const lanePositionWeightShareNestedId =
                                                    buildWorkspaceReviewSignalNestedSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "lanePosition",
                                                      "weightShare",
                                                    );
                                                  const recommendationSelectionAlignmentNestedId =
                                                    buildWorkspaceReviewSignalNestedSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "recommendationContext",
                                                      "selectionAlignment",
                                                    );
                                                  const recommendationResolutionBasisNestedId =
                                                    buildWorkspaceReviewSignalNestedSubviewSelectionId(
                                                      scoreDetailKey,
                                                      "recommendationContext",
                                                      "resolutionBasis",
                                                    );
                                                  const interpretationSubviewCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalSubviewIds[
                                                      interpretationSubviewId
                                                    ],
                                                  );
                                                  const lanePositionSubviewCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalSubviewIds[
                                                      lanePositionSubviewId
                                                    ],
                                                  );
                                                  const recommendationContextSubviewCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalSubviewIds[
                                                      recommendationContextSubviewId
                                                    ],
                                                  );
                                                  const interpretationLaneSemanticsNestedCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalNestedSubviewIds[
                                                      interpretationLaneSemanticsNestedId
                                                    ],
                                                  );
                                                  const interpretationRecommendationEffectNestedCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalNestedSubviewIds[
                                                      interpretationRecommendationEffectNestedId
                                                    ],
                                                  );
                                                  const lanePositionRankContextNestedCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalNestedSubviewIds[
                                                      lanePositionRankContextNestedId
                                                    ],
                                                  );
                                                  const lanePositionWeightShareNestedCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalNestedSubviewIds[
                                                      lanePositionWeightShareNestedId
                                                    ],
                                                  );
                                                  const recommendationSelectionAlignmentNestedCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalNestedSubviewIds[
                                                      recommendationSelectionAlignmentNestedId
                                                    ],
                                                  );
                                                  const recommendationResolutionBasisNestedCollapsed = Boolean(
                                                    comparison.collapsedWorkspaceScoreSignalNestedSubviewIds[
                                                      recommendationResolutionBasisNestedId
                                                    ],
                                                  );
                                                  const interpretationLaneSemanticsMicroView =
                                                    resolveWorkspaceReviewSignalMicroView(
                                                      interpretationLaneSemanticsNestedId,
                                                      ["summary", "trace"],
                                                    );
                                                  const interpretationRecommendationEffectMicroView =
                                                    resolveWorkspaceReviewSignalMicroView(
                                                      interpretationRecommendationEffectNestedId,
                                                      ["recommendation", "alternative"],
                                                    );
                                                  const lanePositionRankContextMicroView =
                                                    resolveWorkspaceReviewSignalMicroView(
                                                      lanePositionRankContextNestedId,
                                                      ["position", "score"],
                                                    );
                                                  const lanePositionWeightShareMicroView =
                                                    resolveWorkspaceReviewSignalMicroView(
                                                      lanePositionWeightShareNestedId,
                                                      ["share", "impact"],
                                                    );
                                                  const recommendationSelectionAlignmentMicroView =
                                                    resolveWorkspaceReviewSignalMicroView(
                                                      recommendationSelectionAlignmentNestedId,
                                                      ["selection", "lane"],
                                                    );
                                                  const recommendationResolutionBasisMicroView =
                                                    resolveWorkspaceReviewSignalMicroView(
                                                      recommendationResolutionBasisNestedId,
                                                      ["gap", "reason"],
                                                    );
                                                  const interpretationLaneSemanticsInteractionId =
                                                    buildWorkspaceReviewSignalMicroInteractionSelectionId(
                                                      interpretationLaneSemanticsNestedId,
                                                      interpretationLaneSemanticsMicroView,
                                                    );
                                                  const interpretationRecommendationEffectInteractionId =
                                                    buildWorkspaceReviewSignalMicroInteractionSelectionId(
                                                      interpretationRecommendationEffectNestedId,
                                                      interpretationRecommendationEffectMicroView,
                                                    );
                                                  const lanePositionRankContextInteractionId =
                                                    buildWorkspaceReviewSignalMicroInteractionSelectionId(
                                                      lanePositionRankContextNestedId,
                                                      lanePositionRankContextMicroView,
                                                    );
                                                  const lanePositionWeightShareInteractionId =
                                                    buildWorkspaceReviewSignalMicroInteractionSelectionId(
                                                      lanePositionWeightShareNestedId,
                                                      lanePositionWeightShareMicroView,
                                                    );
                                                  const recommendationSelectionAlignmentInteractionId =
                                                    buildWorkspaceReviewSignalMicroInteractionSelectionId(
                                                      recommendationSelectionAlignmentNestedId,
                                                      recommendationSelectionAlignmentMicroView,
                                                    );
                                                  const recommendationResolutionBasisInteractionId =
                                                    buildWorkspaceReviewSignalMicroInteractionSelectionId(
                                                      recommendationResolutionBasisNestedId,
                                                      recommendationResolutionBasisMicroView,
                                                    );
                                                  const interpretationLaneSemanticsInteraction =
                                                    resolveWorkspaceReviewSignalMicroInteraction(
                                                      interpretationLaneSemanticsInteractionId,
                                                      ["lane", "polarity"],
                                                    );
                                                  const interpretationRecommendationEffectInteraction =
                                                    resolveWorkspaceReviewSignalMicroInteraction(
                                                      interpretationRecommendationEffectInteractionId,
                                                      ["support", "tradeoff"],
                                                    );
                                                  const lanePositionRankContextInteraction =
                                                    resolveWorkspaceReviewSignalMicroInteraction(
                                                      lanePositionRankContextInteractionId,
                                                      ["rank", "score"],
                                                    );
                                                  const lanePositionWeightShareInteraction =
                                                    resolveWorkspaceReviewSignalMicroInteraction(
                                                      lanePositionWeightShareInteractionId,
                                                      ["share", "impact"],
                                                    );
                                                  const recommendationSelectionAlignmentInteraction =
                                                    resolveWorkspaceReviewSignalMicroInteraction(
                                                      recommendationSelectionAlignmentInteractionId,
                                                      ["selected", "focusedLane"],
                                                    );
                                                  const recommendationResolutionBasisInteraction =
                                                    resolveWorkspaceReviewSignalMicroInteraction(
                                                      recommendationResolutionBasisInteractionId,
                                                      ["gap", "reason"],
                                                    );
                                                  const focusScoreDetailSource = (
                                                    source: ComparisonHistorySyncConflictFieldSource,
                                                  ) => {
                                                    activateWorkspaceReviewRow(entry.auditId, row.fieldKey);
                                                    comparison.onChangeFocusedWorkspaceScoreDetailSource(
                                                      scoreDetailKey,
                                                      source,
                                                    );
                                                    comparison.onChangeFocusedWorkspaceScoreDetailSignalKey(
                                                      scoreDetailKey,
                                                      resolveWorkspaceReviewSignalSelectionId(
                                                        source,
                                                        source === "local" ? row.localSignals : row.remoteSignals,
                                                        focusedScoreDetailSignalKey,
                                                      ),
                                                    );
                                                  };
                                                  const focusScoreDetailSignal = (
                                                    source: ComparisonHistorySyncConflictFieldSource,
                                                    signalKey: string,
                                                  ) => {
                                                    activateWorkspaceReviewRow(entry.auditId, row.fieldKey);
                                                    comparison.onChangeFocusedWorkspaceScoreDetailSource(
                                                      scoreDetailKey,
                                                      source,
                                                    );
                                                    comparison.onChangeFocusedWorkspaceScoreDetailSignalKey(
                                                      scoreDetailKey,
                                                      signalKey,
                                                    );
                                                  };
                                                  return (
                                                    <div
                                                      className={`comparison-history-conflict-review-row ${
                                                        rowActive ? "is-active" : ""
                                                      }`}
                                                      key={scoreDetailKey}
                                                      ref={(node) => {
                                                        if (node) {
                                                          workspaceReviewRowRefs.current.set(scoreDetailKey, node);
                                                          return;
                                                        }
                                                        workspaceReviewRowRefs.current.delete(scoreDetailKey);
                                                      }}
                                                      onClick={() => activateWorkspaceReviewRow(entry.auditId, row.fieldKey)}
                                                      onFocusCapture={() =>
                                                        activateWorkspaceReviewRow(entry.auditId, row.fieldKey)
                                                      }
                                                      tabIndex={-1}
                                                    >
                                                      <span className="comparison-dev-conflict-preview-label-group">
                                                        <span className="comparison-dev-conflict-preview-label">
                                                          {row.label}
                                                        </span>
                                                        <span className="comparison-history-conflict-review-recommendation">
                                                          Recommend {row.recommendedSource === "local" ? "local latest" : "remote audit"} · {row.recommendationReason}
                                                        </span>
                                                        <button
                                                          className="comparison-history-conflict-review-toggle"
                                                          onClick={() => {
                                                            activateWorkspaceReviewRow(entry.auditId, row.fieldKey);
                                                            if (
                                                              !scoreDetailsExpanded
                                                              && !comparison.focusedWorkspaceScoreDetailSources[
                                                                scoreDetailKey
                                                              ]
                                                            ) {
                                                              comparison.onChangeFocusedWorkspaceScoreDetailSource(
                                                                scoreDetailKey,
                                                                row.recommendedSource,
                                                              );
                                                            }
                                                            if (
                                                              !scoreDetailsExpanded
                                                              && !comparison.focusedWorkspaceScoreDetailSignalKeys[
                                                                scoreDetailKey
                                                              ]
                                                            ) {
                                                              comparison.onChangeFocusedWorkspaceScoreDetailSignalKey(
                                                                scoreDetailKey,
                                                                resolveWorkspaceReviewSignalSelectionId(
                                                                  row.recommendedSource,
                                                                  row.recommendedSource === "local"
                                                                    ? row.localSignals
                                                                    : row.remoteSignals,
                                                                ),
                                                              );
                                                            }
                                                            comparison.onToggleWorkspaceScoreDetail(scoreDetailKey);
                                                          }}
                                                          type="button"
                                                        >
                                                          {scoreDetailsExpanded ? "Hide score details" : "Show score details"}
                                                        </button>
                                                        {row.hasLatestLocalDrift ? (
                                                          <span className="comparison-dev-conflict-preview-hint">
                                                            Current local drift from audit snapshot
                                                          </span>
                                                        ) : null}
                                                      </span>
                                                      <button
                                                        className={`comparison-history-conflict-review-choice ${
                                                          row.selectedSource === "local" ? "is-selected" : ""
                                                        } ${
                                                          row.recommendedSource === "local" ? "is-recommended" : ""
                                                        }`}
                                                        onClick={() =>
                                                          {
                                                            focusScoreDetailSource("local");
                                                            comparison.onSetHistoryWorkspaceFieldSource(
                                                              entry.auditId,
                                                              row.fieldKey,
                                                              "local",
                                                            );
                                                          }
                                                        }
                                                        type="button"
                                                      >
                                                        <span className="comparison-history-conflict-review-choice-label">
                                                          {row.hasLatestLocalDrift ? "Local latest" : "Local"}
                                                        </span>
                                                        <span className="comparison-history-conflict-review-choice-value">
                                                          {row.localValue}
                                                        </span>
                                                        {row.localHint ? (
                                                          <span className="comparison-history-conflict-review-choice-hint">
                                                            {row.localHint}
                                                          </span>
                                                        ) : null}
                                                      </button>
                                                      <button
                                                        className={`comparison-history-conflict-review-choice ${
                                                          row.selectedSource === "remote" ? "is-selected" : ""
                                                        } ${
                                                          row.recommendedSource === "remote" ? "is-recommended" : ""
                                                        }`}
                                                        onClick={() =>
                                                          {
                                                            focusScoreDetailSource("remote");
                                                            comparison.onSetHistoryWorkspaceFieldSource(
                                                              entry.auditId,
                                                              row.fieldKey,
                                                              "remote",
                                                            );
                                                          }
                                                        }
                                                        type="button"
                                                      >
                                                        <span className="comparison-history-conflict-review-choice-label">
                                                          {row.hasLatestLocalDrift ? "Remote audit" : "Remote"}
                                                        </span>
                                                        <span className="comparison-history-conflict-review-choice-value">
                                                          {row.remoteValue}
                                                        </span>
                                                      </button>
                                                      {scoreDetailsExpanded ? (
                                                        <div className="comparison-history-conflict-review-score-breakdown">
                                                          <div
                                                            className={`comparison-history-conflict-review-score-column ${
                                                              row.recommendedSource === "local" ? "is-recommended" : ""
                                                            } ${
                                                              focusedScoreDetailSource === "local" ? "is-focused" : ""
                                                            }`}
                                                            aria-label={`Focus local latest score details for ${row.label}`}
                                                            aria-pressed={focusedScoreDetailSource === "local"}
                                                            onClick={() => focusScoreDetailSource("local")}
                                                            onFocus={() => focusScoreDetailSource("local")}
                                                            onKeyDown={(event) => {
                                                              if (event.key !== "Enter" && event.key !== " ") {
                                                                return;
                                                              }
                                                              event.preventDefault();
                                                              focusScoreDetailSource("local");
                                                            }}
                                                            role="button"
                                                            tabIndex={0}
                                                          >
                                                            <div className="comparison-history-conflict-review-score-head">
                                                              <span>Local latest</span>
                                                              <strong>
                                                                {formatComparisonScoreSignedValue(row.localScore)}
                                                              </strong>
                                                            </div>
                                                            {row.localSignals.length ? (
                                                              <div className="comparison-history-conflict-review-score-signal-list">
                                                                {row.localSignals.map((signal, index) => {
                                                                  const signalKey = buildWorkspaceReviewSignalSelectionId(
                                                                    "local",
                                                                    signal,
                                                                    index,
                                                                  );
                                                                  return (
                                                                  <div
                                                                    aria-label={`Focus local latest signal ${signal.label}`}
                                                                    aria-pressed={resolvedLocalSignalFocusKey === signalKey}
                                                                    className={`comparison-history-conflict-review-score-signal ${
                                                                      resolvedLocalSignalFocusKey === signalKey
                                                                        ? "is-focused"
                                                                        : ""
                                                                    }`}
                                                                    key={`local:${scoreDetailKey}:${signalKey}`}
                                                                    onClick={(event) => {
                                                                      event.stopPropagation();
                                                                      focusScoreDetailSignal("local", signalKey);
                                                                    }}
                                                                    onFocus={() =>
                                                                      focusScoreDetailSignal("local", signalKey)
                                                                    }
                                                                    onKeyDown={(event) => {
                                                                      if (event.key !== "Enter" && event.key !== " ") {
                                                                        return;
                                                                      }
                                                                      event.preventDefault();
                                                                      event.stopPropagation();
                                                                      focusScoreDetailSignal("local", signalKey);
                                                                    }}
                                                                    role="button"
                                                                    tabIndex={0}
                                                                  >
                                                                    <span>{signal.label}</span>
                                                                    <strong
                                                                      className={`comparison-history-conflict-review-score-signal-weight ${
                                                                        signal.weight >= 0 ? "is-positive" : "is-negative"
                                                                      }`}
                                                                    >
                                                                      {formatComparisonScoreSignedValue(signal.weight)}
                                                                    </strong>
                                                                  </div>
                                                                  );
                                                                })}
                                                              </div>
                                                            ) : (
                                                              <span className="comparison-history-conflict-review-score-empty">
                                                                No local semantic bonus fired.
                                                              </span>
                                                            )}
                                                          </div>
                                                          <div
                                                            className={`comparison-history-conflict-review-score-column ${
                                                              row.recommendedSource === "remote" ? "is-recommended" : ""
                                                            } ${
                                                              focusedScoreDetailSource === "remote" ? "is-focused" : ""
                                                            }`}
                                                            aria-label={`Focus remote audit score details for ${row.label}`}
                                                            aria-pressed={focusedScoreDetailSource === "remote"}
                                                            onClick={() => focusScoreDetailSource("remote")}
                                                            onFocus={() => focusScoreDetailSource("remote")}
                                                            onKeyDown={(event) => {
                                                              if (event.key !== "Enter" && event.key !== " ") {
                                                                return;
                                                              }
                                                              event.preventDefault();
                                                              focusScoreDetailSource("remote");
                                                            }}
                                                            role="button"
                                                            tabIndex={0}
                                                          >
                                                            <div className="comparison-history-conflict-review-score-head">
                                                              <span>Remote audit</span>
                                                              <strong>
                                                                {formatComparisonScoreSignedValue(row.remoteScore)}
                                                              </strong>
                                                            </div>
                                                            {row.remoteSignals.length ? (
                                                              <div className="comparison-history-conflict-review-score-signal-list">
                                                                {row.remoteSignals.map((signal, index) => {
                                                                  const signalKey = buildWorkspaceReviewSignalSelectionId(
                                                                    "remote",
                                                                    signal,
                                                                    index,
                                                                  );
                                                                  return (
                                                                  <div
                                                                    aria-label={`Focus remote audit signal ${signal.label}`}
                                                                    aria-pressed={resolvedRemoteSignalFocusKey === signalKey}
                                                                    className={`comparison-history-conflict-review-score-signal ${
                                                                      resolvedRemoteSignalFocusKey === signalKey
                                                                        ? "is-focused"
                                                                        : ""
                                                                    }`}
                                                                    key={`remote:${scoreDetailKey}:${signalKey}`}
                                                                    onClick={(event) => {
                                                                      event.stopPropagation();
                                                                      focusScoreDetailSignal("remote", signalKey);
                                                                    }}
                                                                    onFocus={() =>
                                                                      focusScoreDetailSignal("remote", signalKey)
                                                                    }
                                                                    onKeyDown={(event) => {
                                                                      if (event.key !== "Enter" && event.key !== " ") {
                                                                        return;
                                                                      }
                                                                      event.preventDefault();
                                                                      event.stopPropagation();
                                                                      focusScoreDetailSignal("remote", signalKey);
                                                                    }}
                                                                    role="button"
                                                                    tabIndex={0}
                                                                  >
                                                                    <span>{signal.label}</span>
                                                                    <strong
                                                                      className={`comparison-history-conflict-review-score-signal-weight ${
                                                                        signal.weight >= 0 ? "is-positive" : "is-negative"
                                                                      }`}
                                                                    >
                                                                      {formatComparisonScoreSignedValue(signal.weight)}
                                                                    </strong>
                                                                  </div>
                                                                  );
                                                                })}
                                                              </div>
                                                            ) : (
                                                              <span className="comparison-history-conflict-review-score-empty">
                                                                No remote semantic bonus fired.
                                                              </span>
                                                            )}
                                                          </div>
                                                          <div className="comparison-history-conflict-review-score-detail-bar">
                                                            <span className="comparison-history-conflict-review-score-detail-summary">
                                                              {focusedSignalDetail
                                                                ? `Focused signal · ${focusedSignalDetail.sourceLabel} · ${focusedSignalDetail.signal.label}`
                                                                : "Focused signal · none selected"}
                                                            </span>
                                                            <button
                                                              className="comparison-history-conflict-review-toggle"
                                                              disabled={!focusedSignalDetail}
                                                              onClick={(event) => {
                                                                event.stopPropagation();
                                                                activateWorkspaceReviewRow(
                                                                  entry.auditId,
                                                                  row.fieldKey,
                                                                );
                                                                comparison.onToggleWorkspaceScoreSignalDetail(
                                                                  scoreDetailKey,
                                                                );
                                                              }}
                                                              type="button"
                                                            >
                                                              {signalDetailExpanded
                                                                ? "Hide signal detail"
                                                                : "Show signal detail"}
                                                            </button>
                                                          </div>
                                                          {signalDetailExpanded ? (
                                                            focusedSignalDetail ? (
                                                              <div className="comparison-history-conflict-review-score-detail">
                                                                <div className="comparison-history-conflict-review-score-detail-head">
                                                                  <div>
                                                                    <span className="comparison-history-conflict-review-score-detail-label">
                                                                      {focusedSignalDetail.sourceLabel}
                                                                    </span>
                                                                    <strong>
                                                                      {focusedSignalDetail.signal.label}
                                                                    </strong>
                                                                  </div>
                                                                  <strong className="comparison-history-conflict-review-score-detail-impact">
                                                                    {formatComparisonScoreSignedValue(
                                                                      focusedSignalDetail.signal.weight,
                                                                    )}
                                                                  </strong>
                                                                </div>
                                                                <div className="comparison-history-conflict-review-score-detail-subviews">
                                                                  <section
                                                                    className={`comparison-history-conflict-review-score-detail-section ${
                                                                      interpretationSubviewCollapsed
                                                                        ? "is-collapsed"
                                                                        : ""
                                                                    }`}
                                                                  >
                                                                    <button
                                                                      className="comparison-history-conflict-review-score-detail-section-head"
                                                                      onClick={() =>
                                                                        comparison.onToggleWorkspaceScoreSignalSubview(
                                                                          interpretationSubviewId,
                                                                        )
                                                                      }
                                                                      type="button"
                                                                    >
                                                                      <span className="comparison-history-conflict-review-score-detail-section-label">
                                                                        Interpretation
                                                                      </span>
                                                                      <span className="comparison-history-conflict-review-score-detail-section-summary">
                                                                        {focusedSignalDetail.contributionLabel}
                                                                      </span>
                                                                    </button>
                                                                    {!interpretationSubviewCollapsed ? (
                                                                      <div className="comparison-history-conflict-review-score-detail-section-body">
                                                                        <div
                                                                          className={`comparison-history-conflict-review-score-detail-nested ${
                                                                            interpretationLaneSemanticsNestedCollapsed
                                                                              ? "is-collapsed"
                                                                              : ""
                                                                          }`}
                                                                        >
                                                                          <button
                                                                            className="comparison-history-conflict-review-score-detail-nested-head"
                                                                            onClick={() =>
                                                                              comparison.onToggleWorkspaceScoreSignalNestedSubview(
                                                                                interpretationLaneSemanticsNestedId,
                                                                              )
                                                                            }
                                                                            type="button"
                                                                          >
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-label">
                                                                              Lane semantics
                                                                            </span>
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-summary">
                                                                              {focusedSignalDetail.sourceLabel} ·{" "}
                                                                              {focusedSignalDetail.signal.weight >= 0
                                                                                ? "Positive signal"
                                                                                : "Negative signal"}
                                                                            </span>
                                                                          </button>
                                                                          {!interpretationLaneSemanticsNestedCollapsed ? (
                                                                            <div className="comparison-history-conflict-review-score-detail-nested-body">
                                                                              <div className="comparison-history-conflict-review-score-detail-microview-row">
                                                                                {([
                                                                                  ["summary", "Summary"],
                                                                                  ["trace", "Signal trace"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      interpretationLaneSemanticsMicroView
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-microview-chip ${
                                                                                      interpretationLaneSemanticsMicroView
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroView(
                                                                                        interpretationLaneSemanticsNestedId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              {interpretationLaneSemanticsMicroView === "summary" ? (
                                                                                <>
                                                                                  <div className="comparison-history-conflict-review-score-detail-chip-row">
                                                                                    <span className="comparison-history-conflict-review-score-detail-chip">
                                                                                      {focusedSignalDetail.sourceLabel}
                                                                                    </span>
                                                                                    <span className="comparison-history-conflict-review-score-detail-chip">
                                                                                      {focusedSignalDetail.signal.weight >= 0
                                                                                        ? "Positive semantic signal"
                                                                                        : "Negative semantic signal"}
                                                                                    </span>
                                                                                  </div>
                                                                                  <p className="comparison-history-conflict-review-score-detail-copy">
                                                                                    {focusedSignalDetail.contributionLabel}.
                                                                                  </p>
                                                                                </>
                                                                              ) : (
                                                                                  <div className="comparison-history-conflict-review-score-detail-grid">
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Focused signal</span>
                                                                                      <strong>{focusedSignalDetail.signal.label}</strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Lane label</span>
                                                                                      <strong>{focusedSignalDetail.sourceLabel}</strong>
                                                                                    </div>
                                                                                  </div>
                                                                              )}
                                                                              <div className="comparison-history-conflict-review-score-detail-inline-row">
                                                                                {([
                                                                                  ["lane", "Lane lens"],
                                                                                  ["polarity", "Polarity lens"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      interpretationLaneSemanticsInteraction
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-inline-chip ${
                                                                                      interpretationLaneSemanticsInteraction
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroInteraction(
                                                                                        interpretationLaneSemanticsInteractionId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <p className="comparison-history-conflict-review-score-detail-inline-copy">
                                                                                {interpretationLaneSemanticsInteraction === "lane"
                                                                                  ? `${focusedSignalDetail.sourceLabel} currently owns this signal inside the active semantic lane.`
                                                                                  : focusedSignalDetail.signal.weight >= 0
                                                                                    ? "The focused signal is adding confidence to the lane rather than draining it."
                                                                                    : "The focused signal is subtracting confidence from the lane rather than supporting it."}
                                                                              </p>
                                                                              {renderWorkspaceReviewSignalMicroState({
                                                                                interactionId: interpretationLaneSemanticsInteractionId,
                                                                                hoverOptions: [
                                                                                  {
                                                                                    key: "lane",
                                                                                    label: "Lane",
                                                                                    copy: `${focusedSignalDetail.sourceLabel} is the lane currently carrying this semantic signal.`,
                                                                                  },
                                                                                  {
                                                                                    key: "signal",
                                                                                    label: "Signal",
                                                                                    copy: `${focusedSignalDetail.signal.label} is the specific semantic phrase now under inspection.`,
                                                                                  },
                                                                                  {
                                                                                    key: "impact",
                                                                                    label: "Impact",
                                                                                    copy: `This signal contributes ${formatComparisonScoreSignedValue(
                                                                                      focusedSignalDetail.signal.weight,
                                                                                    )} to the lane.`,
                                                                                  },
                                                                                ],
                                                                                scrubCopies: [
                                                                                  "Snapshot 1 keeps the lane/source relationship exactly as captured in the current review row.",
                                                                                  "Snapshot 2 follows the signal deeper into the lane to see whether polarity still matches the lane label.",
                                                                                  "Snapshot 3 replays the signal as the dominant semantic phrase in the lane.",
                                                                                ],
                                                                                notePages: [
                                                                                  {
                                                                                    label: "Lane note",
                                                                                    copy: `${focusedSignalDetail.sourceLabel} is the durable owner of this semantic phrase inside the current workspace branch.`,
                                                                                  },
                                                                                  {
                                                                                    label: "Polarity note",
                                                                                    copy: focusedSignalDetail.signal.weight >= 0
                                                                                      ? "Positive polarity means this phrase is strengthening the lane rather than weakening it."
                                                                                      : "Negative polarity means this phrase is reducing confidence in the lane rather than supporting it.",
                                                                                  },
                                                                                ],
                                                                              })}
                                                                            </div>
                                                                          ) : null}
                                                                        </div>
                                                                        <div
                                                                          className={`comparison-history-conflict-review-score-detail-nested ${
                                                                            interpretationRecommendationEffectNestedCollapsed
                                                                              ? "is-collapsed"
                                                                              : ""
                                                                          }`}
                                                                        >
                                                                          <button
                                                                            className="comparison-history-conflict-review-score-detail-nested-head"
                                                                            onClick={() =>
                                                                              comparison.onToggleWorkspaceScoreSignalNestedSubview(
                                                                                interpretationRecommendationEffectNestedId,
                                                                              )
                                                                            }
                                                                            type="button"
                                                                          >
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-label">
                                                                              Recommendation effect
                                                                            </span>
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-summary">
                                                                              {focusedSignalDetail.recommendationRelationship}
                                                                            </span>
                                                                          </button>
                                                                          {!interpretationRecommendationEffectNestedCollapsed ? (
                                                                            <div className="comparison-history-conflict-review-score-detail-nested-body">
                                                                              <div className="comparison-history-conflict-review-score-detail-microview-row">
                                                                                {([
                                                                                  ["recommendation", "Ranked lane"],
                                                                                  ["alternative", "Alternate lane"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      interpretationRecommendationEffectMicroView
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-microview-chip ${
                                                                                      interpretationRecommendationEffectMicroView
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroView(
                                                                                        interpretationRecommendationEffectNestedId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              {interpretationRecommendationEffectMicroView === "recommendation" ? (
                                                                                <p className="comparison-history-conflict-review-score-detail-copy">
                                                                                  {focusedSignalDetail.recommendationRelationship}.
                                                                                </p>
                                                                              ) : (
                                                                                <p className="comparison-history-conflict-review-score-detail-copy">
                                                                                  {focusedSignalDetail.source === row.recommendedSource
                                                                                    ? "This signal currently sits on the ranked lane, so the alternate lane loses this semantic support."
                                                                                    : "This signal currently sits on the alternate lane, showing what the non-ranked branch is still preserving."}
                                                                                </p>
                                                                              )}
                                                                              <div className="comparison-history-conflict-review-score-detail-inline-row">
                                                                                {([
                                                                                  ["support", "Support"],
                                                                                  ["tradeoff", "Trade-off"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      interpretationRecommendationEffectInteraction
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-inline-chip ${
                                                                                      interpretationRecommendationEffectInteraction
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroInteraction(
                                                                                        interpretationRecommendationEffectInteractionId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <p className="comparison-history-conflict-review-score-detail-inline-copy">
                                                                                {interpretationRecommendationEffectInteraction === "support"
                                                                                  ? focusedSignalDetail.recommendationRelationship
                                                                                  : focusedSignalDetail.source === row.recommendedSource
                                                                                    ? "Changing away from the ranked lane would drop this specific semantic support."
                                                                                    : "Keeping the alternate lane preserves this signal even though the overall ranking prefers the other branch."}
                                                                              </p>
                                                                              {renderWorkspaceReviewSignalMicroState({
                                                                                interactionId: interpretationRecommendationEffectInteractionId,
                                                                                hoverOptions: [
                                                                                  {
                                                                                    key: "support",
                                                                                    label: "Support",
                                                                                    copy: focusedSignalDetail.recommendationRelationship,
                                                                                  },
                                                                                  {
                                                                                    key: "tradeoff",
                                                                                    label: "Trade-off",
                                                                                    copy: focusedSignalDetail.source === row.recommendedSource
                                                                                      ? "Leaving the ranked lane would surrender this support."
                                                                                      : "Keeping the alternate lane preserves this phrase even while the score prefers another branch.",
                                                                                  },
                                                                                  {
                                                                                    key: "source",
                                                                                    label: "Source",
                                                                                    copy: `${focusedSignalDetail.sourceLabel} is the branch currently contributing this recommendation effect.`,
                                                                                  },
                                                                                ],
                                                                                scrubCopies: [
                                                                                  "Step 1 reads the recommendation effect in isolation.",
                                                                                  "Step 2 compares what the ranked lane keeps against what the alternate lane gives up.",
                                                                                  "Step 3 emphasizes the branch cost of switching away from the current semantic carrier.",
                                                                                ],
                                                                                notePages: [
                                                                                  {
                                                                                    label: "Support note",
                                                                                    copy: focusedSignalDetail.recommendationRelationship,
                                                                                  },
                                                                                  {
                                                                                    label: "Trade-off note",
                                                                                    copy: focusedSignalDetail.source === row.recommendedSource
                                                                                      ? "This phrase is part of why the ranked lane still wins."
                                                                                      : "This phrase is one of the strongest things the non-ranked lane is still holding onto.",
                                                                                  },
                                                                                ],
                                                                              })}
                                                                            </div>
                                                                          ) : null}
                                                                        </div>
                                                                      </div>
                                                                    ) : null}
                                                                  </section>
                                                                  <section
                                                                    className={`comparison-history-conflict-review-score-detail-section ${
                                                                      lanePositionSubviewCollapsed
                                                                        ? "is-collapsed"
                                                                        : ""
                                                                    }`}
                                                                  >
                                                                    <button
                                                                      className="comparison-history-conflict-review-score-detail-section-head"
                                                                      onClick={() =>
                                                                        comparison.onToggleWorkspaceScoreSignalSubview(
                                                                          lanePositionSubviewId,
                                                                        )
                                                                      }
                                                                      type="button"
                                                                    >
                                                                      <span className="comparison-history-conflict-review-score-detail-section-label">
                                                                        Lane position
                                                                      </span>
                                                                      <span className="comparison-history-conflict-review-score-detail-section-summary">
                                                                        Rank {focusedSignalDetail.rank} /{" "}
                                                                        {focusedSignalDetail.signalCount} ·{" "}
                                                                        {Math.round(
                                                                          focusedSignalDetail.shareOfVisibleWeight * 100,
                                                                        )}
                                                                        % visible share
                                                                      </span>
                                                                    </button>
                                                                    {!lanePositionSubviewCollapsed ? (
                                                                      <div className="comparison-history-conflict-review-score-detail-section-body">
                                                                        <div
                                                                          className={`comparison-history-conflict-review-score-detail-nested ${
                                                                            lanePositionRankContextNestedCollapsed
                                                                              ? "is-collapsed"
                                                                              : ""
                                                                          }`}
                                                                        >
                                                                          <button
                                                                            className="comparison-history-conflict-review-score-detail-nested-head"
                                                                            onClick={() =>
                                                                              comparison.onToggleWorkspaceScoreSignalNestedSubview(
                                                                                lanePositionRankContextNestedId,
                                                                              )
                                                                            }
                                                                            type="button"
                                                                          >
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-label">
                                                                              Rank context
                                                                            </span>
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-summary">
                                                                              Rank {focusedSignalDetail.rank} /{" "}
                                                                              {focusedSignalDetail.signalCount}
                                                                            </span>
                                                                          </button>
                                                                          {!lanePositionRankContextNestedCollapsed ? (
                                                                            <div className="comparison-history-conflict-review-score-detail-nested-body">
                                                                              <div className="comparison-history-conflict-review-score-detail-microview-row">
                                                                                {([
                                                                                  ["position", "Rank view"],
                                                                                  ["score", "Lane score"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      lanePositionRankContextMicroView
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-microview-chip ${
                                                                                      lanePositionRankContextMicroView
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroView(
                                                                                        lanePositionRankContextNestedId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-grid">
                                                                                {lanePositionRankContextMicroView === "position" ? (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Rank</span>
                                                                                      <strong>
                                                                                        {focusedSignalDetail.rank} /{" "}
                                                                                        {focusedSignalDetail.signalCount}
                                                                                      </strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Signals in lane</span>
                                                                                      <strong>{focusedSignalDetail.signalCount}</strong>
                                                                                    </div>
                                                                                  </>
                                                                                ) : (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Lane score</span>
                                                                                      <strong>
                                                                                        {formatComparisonScoreSignedValue(
                                                                                          focusedSignalDetail.laneScore,
                                                                                        )}
                                                                                      </strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Signal impact</span>
                                                                                      <strong>
                                                                                        {formatComparisonScoreSignedValue(
                                                                                          focusedSignalDetail.signal.weight,
                                                                                        )}
                                                                                      </strong>
                                                                                    </div>
                                                                                  </>
                                                                                )}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-inline-row">
                                                                                {([
                                                                                  ["rank", "Rank lens"],
                                                                                  ["score", "Score lens"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      lanePositionRankContextInteraction
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-inline-chip ${
                                                                                      lanePositionRankContextInteraction
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroInteraction(
                                                                                        lanePositionRankContextInteractionId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <p className="comparison-history-conflict-review-score-detail-inline-copy">
                                                                                {lanePositionRankContextInteraction === "rank"
                                                                                  ? `This signal currently ranks ${focusedSignalDetail.rank} out of ${focusedSignalDetail.signalCount} visible signals in its lane.`
                                                                                  : `The lane score ${formatComparisonScoreSignedValue(
                                                                                      focusedSignalDetail.laneScore,
                                                                                    )} is the broader context around this signal's own impact.`}
                                                                              </p>
                                                                              {renderWorkspaceReviewSignalMicroState({
                                                                                interactionId: lanePositionRankContextInteractionId,
                                                                                hoverOptions: [
                                                                                  {
                                                                                    key: "rank",
                                                                                    label: "Rank",
                                                                                    copy: `The signal sits at position ${focusedSignalDetail.rank} of ${focusedSignalDetail.signalCount} in the lane.`,
                                                                                  },
                                                                                  {
                                                                                    key: "score",
                                                                                    label: "Score",
                                                                                    copy: `Lane context is ${formatComparisonScoreSignedValue(
                                                                                      focusedSignalDetail.laneScore,
                                                                                    )} while the signal itself contributes ${formatComparisonScoreSignedValue(
                                                                                      focusedSignalDetail.signal.weight,
                                                                                    )}.`,
                                                                                  },
                                                                                  {
                                                                                    key: "signal",
                                                                                    label: "Signal",
                                                                                    copy: `${focusedSignalDetail.signal.label} is the phrase occupying this rank slot.`,
                                                                                  },
                                                                                ],
                                                                                scrubCopies: [
                                                                                  "Step 1 keeps the current rank ordering as recorded.",
                                                                                  "Step 2 compares rank against the total lane score context.",
                                                                                  "Step 3 treats the signal as if it were the lane headline for quick triage.",
                                                                                ],
                                                                                notePages: [
                                                                                  {
                                                                                    label: "Rank note",
                                                                                    copy: `Rank ${focusedSignalDetail.rank} means there are ${focusedSignalDetail.rank - 1} signals carrying more absolute weight in this lane.`,
                                                                                  },
                                                                                  {
                                                                                    label: "Score note",
                                                                                    copy: "Lane score is broader than any single signal, so rank and score do not always move together.",
                                                                                  },
                                                                                ],
                                                                              })}
                                                                            </div>
                                                                          ) : null}
                                                                        </div>
                                                                        <div
                                                                          className={`comparison-history-conflict-review-score-detail-nested ${
                                                                            lanePositionWeightShareNestedCollapsed
                                                                              ? "is-collapsed"
                                                                              : ""
                                                                          }`}
                                                                        >
                                                                          <button
                                                                            className="comparison-history-conflict-review-score-detail-nested-head"
                                                                            onClick={() =>
                                                                              comparison.onToggleWorkspaceScoreSignalNestedSubview(
                                                                                lanePositionWeightShareNestedId,
                                                                              )
                                                                            }
                                                                            type="button"
                                                                          >
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-label">
                                                                              Weight share
                                                                            </span>
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-summary">
                                                                              {Math.round(
                                                                                focusedSignalDetail.shareOfVisibleWeight
                                                                                  * 100,
                                                                              )}
                                                                              % visible share
                                                                            </span>
                                                                          </button>
                                                                          {!lanePositionWeightShareNestedCollapsed ? (
                                                                            <div className="comparison-history-conflict-review-score-detail-nested-body">
                                                                              <div className="comparison-history-conflict-review-score-detail-microview-row">
                                                                                {([
                                                                                  ["share", "Share"],
                                                                                  ["impact", "Impact"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      lanePositionWeightShareMicroView
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-microview-chip ${
                                                                                      lanePositionWeightShareMicroView
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroView(
                                                                                        lanePositionWeightShareNestedId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-grid">
                                                                                {lanePositionWeightShareMicroView === "share" ? (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Visible weight share</span>
                                                                                      <strong>
                                                                                        {Math.round(
                                                                                          focusedSignalDetail.shareOfVisibleWeight
                                                                                            * 100,
                                                                                        )}
                                                                                        %
                                                                                      </strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Interpretation</span>
                                                                                      <strong>
                                                                                        {focusedSignalDetail.shareOfVisibleWeight >= 0.5
                                                                                          ? "Dominant visible signal"
                                                                                          : "Partial visible share"}
                                                                                      </strong>
                                                                                    </div>
                                                                                  </>
                                                                                ) : (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Signal impact</span>
                                                                                      <strong>
                                                                                        {formatComparisonScoreSignedValue(
                                                                                          focusedSignalDetail.signal.weight,
                                                                                        )}
                                                                                      </strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Impact direction</span>
                                                                                      <strong>
                                                                                        {focusedSignalDetail.signal.weight >= 0
                                                                                          ? "Supports lane confidence"
                                                                                          : "Reduces lane confidence"}
                                                                                      </strong>
                                                                                    </div>
                                                                                  </>
                                                                                )}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-inline-row">
                                                                                {([
                                                                                  ["share", "Share lens"],
                                                                                  ["impact", "Impact lens"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      lanePositionWeightShareInteraction
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-inline-chip ${
                                                                                      lanePositionWeightShareInteraction
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroInteraction(
                                                                                        lanePositionWeightShareInteractionId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <p className="comparison-history-conflict-review-score-detail-inline-copy">
                                                                                {lanePositionWeightShareInteraction === "share"
                                                                                  ? `This signal covers ${Math.round(
                                                                                      focusedSignalDetail.shareOfVisibleWeight
                                                                                        * 100,
                                                                                    )}% of the currently visible signal weight in the lane.`
                                                                                  : `Its direct signed impact is ${formatComparisonScoreSignedValue(
                                                                                      focusedSignalDetail.signal.weight,
                                                                                    )} on the lane.`}
                                                                              </p>
                                                                              {renderWorkspaceReviewSignalMicroState({
                                                                                interactionId: lanePositionWeightShareInteractionId,
                                                                                hoverOptions: [
                                                                                  {
                                                                                    key: "share",
                                                                                    label: "Share",
                                                                                    copy: `${Math.round(
                                                                                      focusedSignalDetail.shareOfVisibleWeight
                                                                                        * 100,
                                                                                    )}% of visible weight currently belongs to this signal.`,
                                                                                  },
                                                                                  {
                                                                                    key: "impact",
                                                                                    label: "Impact",
                                                                                    copy: `Signed impact is ${formatComparisonScoreSignedValue(
                                                                                      focusedSignalDetail.signal.weight,
                                                                                    )} inside the active lane.`,
                                                                                  },
                                                                                  {
                                                                                    key: "source",
                                                                                    label: "Lane",
                                                                                    copy: `${focusedSignalDetail.sourceLabel} is the lane that this weight share belongs to.`,
                                                                                  },
                                                                                ],
                                                                                scrubCopies: [
                                                                                  "Step 1 shows the current visible-share split.",
                                                                                  "Step 2 rebalances attention toward direct impact instead of share.",
                                                                                  "Step 3 treats the signal as the primary visible contributor for this lane.",
                                                                                ],
                                                                                notePages: [
                                                                                  {
                                                                                    label: "Share note",
                                                                                    copy: focusedSignalDetail.shareOfVisibleWeight >= 0.5
                                                                                      ? "This phrase dominates the visible semantic weight in the lane."
                                                                                      : "This phrase matters, but it does not dominate the lane's visible weight.",
                                                                                  },
                                                                                  {
                                                                                    label: "Impact note",
                                                                                    copy: focusedSignalDetail.signal.weight >= 0
                                                                                      ? "Positive impact means the signal is reinforcing the lane."
                                                                                      : "Negative impact means the signal is actively eroding the lane.",
                                                                                  },
                                                                                ],
                                                                              })}
                                                                            </div>
                                                                          ) : null}
                                                                        </div>
                                                                      </div>
                                                                    ) : null}
                                                                  </section>
                                                                  <section
                                                                    className={`comparison-history-conflict-review-score-detail-section ${
                                                                      recommendationContextSubviewCollapsed
                                                                        ? "is-collapsed"
                                                                        : ""
                                                                    }`}
                                                                  >
                                                                    <button
                                                                      className="comparison-history-conflict-review-score-detail-section-head"
                                                                      onClick={() =>
                                                                        comparison.onToggleWorkspaceScoreSignalSubview(
                                                                          recommendationContextSubviewId,
                                                                        )
                                                                      }
                                                                      type="button"
                                                                    >
                                                                      <span className="comparison-history-conflict-review-score-detail-section-label">
                                                                        Recommendation context
                                                                      </span>
                                                                      <span className="comparison-history-conflict-review-score-detail-section-summary">
                                                                        {focusedSignalDetail.source === row.recommendedSource
                                                                          ? "Ranked lane"
                                                                          : "Alternate lane"}{" "}
                                                                        · +{formatComparisonScoreValue(
                                                                          row.recommendationStrength,
                                                                        )} point gap
                                                                      </span>
                                                                    </button>
                                                                    {!recommendationContextSubviewCollapsed ? (
                                                                      <div className="comparison-history-conflict-review-score-detail-section-body">
                                                                        <div
                                                                          className={`comparison-history-conflict-review-score-detail-nested ${
                                                                            recommendationSelectionAlignmentNestedCollapsed
                                                                              ? "is-collapsed"
                                                                              : ""
                                                                          }`}
                                                                        >
                                                                          <button
                                                                            className="comparison-history-conflict-review-score-detail-nested-head"
                                                                            onClick={() =>
                                                                              comparison.onToggleWorkspaceScoreSignalNestedSubview(
                                                                                recommendationSelectionAlignmentNestedId,
                                                                              )
                                                                            }
                                                                            type="button"
                                                                          >
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-label">
                                                                              Selection alignment
                                                                            </span>
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-summary">
                                                                              {focusedSignalDetail.source === row.recommendedSource
                                                                                ? "Focused on ranked lane"
                                                                                : "Focused on alternate lane"}
                                                                            </span>
                                                                          </button>
                                                                          {!recommendationSelectionAlignmentNestedCollapsed ? (
                                                                            <div className="comparison-history-conflict-review-score-detail-nested-body">
                                                                              <div className="comparison-history-conflict-review-score-detail-microview-row">
                                                                                {([
                                                                                  ["selection", "Current selection"],
                                                                                  ["lane", "Ranked lane"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      recommendationSelectionAlignmentMicroView
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-microview-chip ${
                                                                                      recommendationSelectionAlignmentMicroView
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroView(
                                                                                        recommendationSelectionAlignmentNestedId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-grid">
                                                                                {recommendationSelectionAlignmentMicroView === "selection" ? (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Current selection</span>
                                                                                      <strong>
                                                                                        {row.selectedSource === "local"
                                                                                          ? row.hasLatestLocalDrift
                                                                                            ? "Local latest"
                                                                                            : "Local"
                                                                                          : row.hasLatestLocalDrift
                                                                                            ? "Remote audit"
                                                                                            : "Remote"}
                                                                                      </strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Focused signal lane</span>
                                                                                      <strong>{focusedSignalDetail.sourceLabel}</strong>
                                                                                    </div>
                                                                                  </>
                                                                                ) : (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Recommendation lane</span>
                                                                                      <strong>
                                                                                        {focusedSignalDetail.source
                                                                                        === row.recommendedSource
                                                                                          ? "Ranked lane"
                                                                                          : "Alternate lane"}
                                                                                      </strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Alignment</span>
                                                                                      <strong>
                                                                                        {focusedSignalDetail.source === row.recommendedSource
                                                                                          ? "Signal matches ranked lane"
                                                                                          : "Signal is tracing the alternate lane"}
                                                                                      </strong>
                                                                                    </div>
                                                                                  </>
                                                                                )}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-inline-row">
                                                                                {([
                                                                                  ["selected", "Selection lens"],
                                                                                  ["focusedLane", "Focused lane lens"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      recommendationSelectionAlignmentInteraction
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-inline-chip ${
                                                                                      recommendationSelectionAlignmentInteraction
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroInteraction(
                                                                                        recommendationSelectionAlignmentInteractionId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <p className="comparison-history-conflict-review-score-detail-inline-copy">
                                                                                {recommendationSelectionAlignmentInteraction === "selected"
                                                                                  ? "This lens follows the operator's currently chosen source for the row."
                                                                                  : "This lens follows the lane that currently owns the focused signal, even if it is not the chosen row source."}
                                                                              </p>
                                                                              {renderWorkspaceReviewSignalMicroState({
                                                                                interactionId: recommendationSelectionAlignmentInteractionId,
                                                                                hoverOptions: [
                                                                                  {
                                                                                    key: "selected",
                                                                                    label: "Selected",
                                                                                    copy: `Current row selection is ${
                                                                                      row.selectedSource === "local"
                                                                                        ? row.hasLatestLocalDrift
                                                                                          ? "Local latest"
                                                                                          : "Local"
                                                                                        : row.hasLatestLocalDrift
                                                                                          ? "Remote audit"
                                                                                          : "Remote"
                                                                                    }.`,
                                                                                  },
                                                                                  {
                                                                                    key: "focusedLane",
                                                                                    label: "Focused lane",
                                                                                    copy: `Focused signal is currently tied to ${focusedSignalDetail.sourceLabel}.`,
                                                                                  },
                                                                                  {
                                                                                    key: "lane",
                                                                                    label: "Ranked lane",
                                                                                    copy: focusedSignalDetail.source === row.recommendedSource
                                                                                      ? "Focused signal is already on the ranked lane."
                                                                                      : "Focused signal is tracing the alternate lane instead of the ranked lane.",
                                                                                  },
                                                                                ],
                                                                                scrubCopies: [
                                                                                  "Step 1 follows the operator's current row choice.",
                                                                                  "Step 2 follows the lane that currently owns the focused signal.",
                                                                                  "Step 3 compares both against the ranked lane recommendation.",
                                                                                ],
                                                                                notePages: [
                                                                                  {
                                                                                    label: "Selection note",
                                                                                    copy: "Operator choice and signal ownership can diverge when the review explores the non-ranked branch.",
                                                                                  },
                                                                                  {
                                                                                    label: "Alignment note",
                                                                                    copy: focusedSignalDetail.source === row.recommendedSource
                                                                                      ? "Alignment is clean: the focused signal is already on the ranked lane."
                                                                                      : "Alignment is intentionally split: the focused signal is being inspected on the alternate lane.",
                                                                                  },
                                                                                ],
                                                                              })}
                                                                            </div>
                                                                          ) : null}
                                                                        </div>
                                                                        <div
                                                                          className={`comparison-history-conflict-review-score-detail-nested ${
                                                                            recommendationResolutionBasisNestedCollapsed
                                                                              ? "is-collapsed"
                                                                              : ""
                                                                          }`}
                                                                        >
                                                                          <button
                                                                            className="comparison-history-conflict-review-score-detail-nested-head"
                                                                            onClick={() =>
                                                                              comparison.onToggleWorkspaceScoreSignalNestedSubview(
                                                                                recommendationResolutionBasisNestedId,
                                                                              )
                                                                            }
                                                                            type="button"
                                                                          >
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-label">
                                                                              Resolution basis
                                                                            </span>
                                                                            <span className="comparison-history-conflict-review-score-detail-nested-summary">
                                                                              +{formatComparisonScoreValue(
                                                                                row.recommendationStrength,
                                                                              )}{" "}
                                                                              point gap
                                                                            </span>
                                                                          </button>
                                                                          {!recommendationResolutionBasisNestedCollapsed ? (
                                                                            <div className="comparison-history-conflict-review-score-detail-nested-body">
                                                                              <div className="comparison-history-conflict-review-score-detail-microview-row">
                                                                                {([
                                                                                  ["gap", "Gap"],
                                                                                  ["reason", "Reason"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      recommendationResolutionBasisMicroView
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-microview-chip ${
                                                                                      recommendationResolutionBasisMicroView
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroView(
                                                                                        recommendationResolutionBasisNestedId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-grid">
                                                                                {recommendationResolutionBasisMicroView === "gap" ? (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Recommendation gap</span>
                                                                                      <strong>
                                                                                        +{formatComparisonScoreValue(
                                                                                          row.recommendationStrength,
                                                                                        )}
                                                                                      </strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Signal lane</span>
                                                                                      <strong>{focusedSignalDetail.sourceLabel}</strong>
                                                                                    </div>
                                                                                  </>
                                                                                ) : (
                                                                                  <>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Why this lane</span>
                                                                                      <strong>{row.recommendationReason}</strong>
                                                                                    </div>
                                                                                    <div className="comparison-history-conflict-review-score-detail-metric">
                                                                                      <span>Signal relationship</span>
                                                                                      <strong>
                                                                                        {focusedSignalDetail.recommendationRelationship}
                                                                                      </strong>
                                                                                    </div>
                                                                                  </>
                                                                                )}
                                                                              </div>
                                                                              <div className="comparison-history-conflict-review-score-detail-inline-row">
                                                                                {([
                                                                                  ["gap", "Gap lens"],
                                                                                  ["reason", "Reason lens"],
                                                                                ] as const).map(([value, label]) => (
                                                                                  <button
                                                                                    aria-pressed={
                                                                                      recommendationResolutionBasisInteraction
                                                                                      === value
                                                                                    }
                                                                                    className={`comparison-history-conflict-review-score-detail-inline-chip ${
                                                                                      recommendationResolutionBasisInteraction
                                                                                      === value
                                                                                        ? "is-active"
                                                                                        : ""
                                                                                    }`}
                                                                                    key={value}
                                                                                    onClick={() =>
                                                                                      comparison.onChangeWorkspaceScoreSignalMicroInteraction(
                                                                                        recommendationResolutionBasisInteractionId,
                                                                                        value,
                                                                                      )
                                                                                    }
                                                                                    type="button"
                                                                                  >
                                                                                    {label}
                                                                                  </button>
                                                                                ))}
                                                                              </div>
                                                                              <p className="comparison-history-conflict-review-score-detail-inline-copy">
                                                                                {recommendationResolutionBasisInteraction === "gap"
                                                                                  ? `The ranked gap currently stands at +${formatComparisonScoreValue(
                                                                                      row.recommendationStrength,
                                                                                    )} points between the two lanes.`
                                                                                  : `The current recommendation reason is: ${row.recommendationReason}.`}
                                                                              </p>
                                                                              {renderWorkspaceReviewSignalMicroState({
                                                                                interactionId: recommendationResolutionBasisInteractionId,
                                                                                hoverOptions: [
                                                                                  {
                                                                                    key: "gap",
                                                                                    label: "Gap",
                                                                                    copy: `Recommendation gap is +${formatComparisonScoreValue(
                                                                                      row.recommendationStrength,
                                                                                    )} points.`,
                                                                                  },
                                                                                  {
                                                                                    key: "reason",
                                                                                    label: "Reason",
                                                                                    copy: row.recommendationReason,
                                                                                  },
                                                                                  {
                                                                                    key: "signal",
                                                                                    label: "Signal",
                                                                                    copy: `${focusedSignalDetail.signal.label} is one of the phrases informing that gap.`,
                                                                                  },
                                                                                ],
                                                                                scrubCopies: [
                                                                                  "Step 1 shows the current recommendation gap at face value.",
                                                                                  "Step 2 replays why the narrative currently prefers one lane.",
                                                                                  "Step 3 ties the signal back into the final resolution basis.",
                                                                                ],
                                                                                notePages: [
                                                                                  {
                                                                                    label: "Gap note",
                                                                                    copy: "A wider gap usually means this signal is less likely to flip the lane ranking by itself.",
                                                                                  },
                                                                                  {
                                                                                    label: "Reason note",
                                                                                    copy: `Resolution reason currently reads: ${row.recommendationReason}.`,
                                                                                  },
                                                                                ],
                                                                              })}
                                                                            </div>
                                                                          ) : null}
                                                                        </div>
                                                                      </div>
                                                                    ) : null}
                                                                  </section>
                                                                </div>
                                                              </div>
                                                            ) : (
                                                              <span className="comparison-history-conflict-review-score-empty">
                                                                No focused semantic signal available.
                                                              </span>
                                                            )
                                                          ) : null}
                                                        </div>
                                                      ) : null}
                                                    </div>
                                                  );
                                                })
                                            : preferenceRows.map((row) => (
                                                <div
                                                  className="comparison-history-conflict-review-row"
                                                  key={`${entry.auditId}:${row.fieldKey}`}
                                                >
                                                  <span className="comparison-dev-conflict-preview-label-group">
                                                    <span className="comparison-dev-conflict-preview-label">
                                                      {row.label}
                                                    </span>
                                                  </span>
                                                  <button
                                                    className={`comparison-history-conflict-review-choice ${
                                                      row.selectedSource === "local" ? "is-selected" : ""
                                                    }`}
                                                    onClick={() =>
                                                      comparison.onSetHistoryPreferenceFieldSource(
                                                        entry.auditId,
                                                        row.fieldKey,
                                                        "local",
                                                      )
                                                    }
                                                    type="button"
                                                  >
                                                    <span className="comparison-history-conflict-review-choice-label">
                                                      Local
                                                    </span>
                                                    <span className="comparison-history-conflict-review-choice-value">
                                                      {row.localValue}
                                                    </span>
                                                  </button>
                                                  <button
                                                    className={`comparison-history-conflict-review-choice ${
                                                      row.selectedSource === "remote" ? "is-selected" : ""
                                                    }`}
                                                    onClick={() =>
                                                      comparison.onSetHistoryPreferenceFieldSource(
                                                        entry.auditId,
                                                        row.fieldKey,
                                                        "remote",
                                                      )
                                                    }
                                                    type="button"
                                                  >
                                                    <span className="comparison-history-conflict-review-choice-label">
                                                      Remote
                                                    </span>
                                                    <span className="comparison-history-conflict-review-choice-value">
                                                      {row.remoteValue}
                                                    </span>
                                                  </button>
                                                </div>
                                              ))}
                                        </div>
                                      </div>
                                    ) : null}
                                  </>
                                ) : null}
                              </article>
                            );
                        })}
                      </div>
                      ) : (
                        <p className="comparison-history-browser-empty">
                          No sync audit events match the current audit view and resolved-visibility settings.
                        </p>
                      )
                    ) : (
                      <p className="comparison-history-browser-empty">
                        No cross-tab sync events have been observed in this tab yet.
                      </p>
                    )}
                  </div>
                  {!comparison.visibleHistoryEntries.length ? (
                    <p className="comparison-history-browser-empty">
                      The current document session has not recorded comparison steps yet.
                    </p>
                  ) : !filteredHistoryEntries.length ? (
                    <p className="comparison-history-browser-empty">
                      No comparison steps match the current search and filter settings.
                    </p>
                  ) : (
                    <div className="comparison-history-browser-list">
                      {filteredHistoryEntries.map((entry) => {
                        const isActive = entry.entryId === comparison.activeHistoryEntryId;
                        return (
                          <article
                            aria-current={isActive ? "step" : undefined}
                            className={`comparison-history-browser-entry ${isActive ? "is-active" : ""}`}
                            key={entry.entryId}
                          >
                            <div className="comparison-history-browser-entry-head">
                              <span className="comparison-history-browser-entry-order">
                                Step {entry.stepIndex + 1}
                              </span>
                              <span className="comparison-history-browser-entry-label">
                                {entry.label}
                              </span>
                              {entry.pinned ? (
                                <span className="comparison-history-browser-entry-badge pinned">
                                  Pinned
                                </span>
                              ) : null}
                              {isActive ? (
                                <span className="comparison-history-browser-entry-badge">
                                  Current
                                </span>
                              ) : null}
                            </div>
                            <p className="comparison-history-browser-entry-meta">
                              {formatComparisonHistoryPanelEntryMeta(entry)}
                            </p>
                            <p className="comparison-history-browser-entry-summary">
                              {entry.summary}
                            </p>
                            <div className="comparison-history-browser-entry-actions">
                              <button
                                className="ghost-button"
                                disabled={isActive}
                                onClick={() => comparison.onNavigateHistoryEntry(entry.entryId)}
                                type="button"
                              >
                                {isActive ? "Current step" : "Open step"}
                              </button>
                              <button
                                className="ghost-button"
                                onClick={() => comparison.onToggleHistoryEntryPinned(entry.entryId)}
                                type="button"
                              >
                                {entry.pinned ? "Unpin" : "Pin"}
                              </button>
                            </div>
                          </article>
                        );
                      })}
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
      {runs.length ? (
        <div className="run-list">
          {runs.map((run) => {
            const orderControls = getOrderControls ? getOrderControls(run) : null;
            const runListBoundaryContract = sharedRunListBoundaryContract;
            const runSurfaceEnforcement = run.surface_enforcement ?? {};
            const runActionAvailability = run.action_availability;
            const compareSelectionAvailability = runActionAvailability?.compare_select;
            const compareSelectionAllowed = compareSelectionAvailability?.allowed ?? true;
            const runListMetricSurfaceEnabled =
              runSurfaceEnforcement.run_list_metric_tiles?.enabled
              ?? shouldEnableRunListMetricDrillBack(
                "return",
                runSurfaceCapabilities,
                runListBoundaryContract,
              );
            const comparisonLinkedRunRole =
              comparison?.payload
                ? getComparisonScoreLinkedRunRole(
                    comparison.selectedScoreLink,
                    comparison.payload.baseline_run_id,
                    run.config.run_id,
                  )
                : null;
            const runListMetricDrillBackEnabled = (surfaceId: RunListBoundarySurfaceId) =>
              Boolean(comparisonLinkedRunRole)
              && runListMetricSurfaceEnabled
              && shouldEnableRunListMetricDrillBack(
                surfaceId,
                runSurfaceCapabilities,
                runListBoundaryContract,
              );
            const runSnapshotSemanticsEnabled =
              runSurfaceEnforcement.run_strategy_snapshot?.enabled
              ?? shouldEnableRunSnapshotSemantics(runSurfaceCapabilities);
            const referenceProvenanceSemanticsEnabled =
              runSurfaceEnforcement.reference_provenance_panels?.enabled
              ?? shouldEnableReferenceProvenanceSemantics(
                runSurfaceCapabilities,
              );
            const workflowBoundaryEnabled =
              runSurfaceEnforcement.compare_selection_workflow?.enabled
              ?? runSurfaceEnforcement.rerun_and_stop_controls?.enabled
              ?? shouldRenderWorkflowControlBoundaryNote(runSurfaceCapabilities);
            const orderActionBoundaryEnabled =
              runSurfaceEnforcement.order_replace_cancel_actions?.enabled
              ?? shouldRenderOrderActionBoundaryNote(runSurfaceCapabilities);
            const stopAvailability = runActionAvailability?.stop_run;
            const stopAllowed = stopAvailability?.allowed ?? true;
            const linkedRunListSelection =
              comparisonLinkedRunRole && comparison?.selectedScoreLink
                ? {
                    ...comparison.selectedScoreLink,
                    role: comparisonLinkedRunRole,
                  }
                : null;
            const linkedRunListMetricSelection =
              linkedRunListSelection && linkedRunListSelection.section === "metrics"
                ? linkedRunListSelection
                : null;
            const linkedRunListContextSelection =
              linkedRunListSelection && linkedRunListSelection.section === "context"
                ? linkedRunListSelection
                : null;
            const statusSubFocusKey = buildComparisonRunListLineSubFocusKey("status");
            const totalReturnSubFocusKey = buildComparisonRunListLineSubFocusKey("total_return_pct");
            const drawdownSubFocusKey = buildComparisonRunListLineSubFocusKey("max_drawdown_pct");
            const winRateSubFocusKey = buildComparisonRunListLineSubFocusKey("win_rate_pct");
            const tradeCountSubFocusKey = buildComparisonRunListLineSubFocusKey("trade_count");
            const referenceNoteSubFocusKey = buildComparisonRunListLineSubFocusKey("reference_note");
            const isRunListSubFocusOrigin = (subFocusKey: string) =>
              linkedRunListSelection?.source === "run_list"
              && linkedRunListSelection.originRunId === run.config.run_id
              && linkedRunListSelection.subFocusKey === subFocusKey;
            const highlightStatus =
              Boolean(linkedRunListContextSelection)
              && isComparisonScoreLinkMatch(linkedRunListContextSelection, ["status_bonus"], "context");
            const highlightReferenceNote =
              Boolean(linkedRunListContextSelection)
              && isComparisonScoreLinkMatch(linkedRunListContextSelection, [
                "native_reference_bonus",
                "reference_bonus",
                "reference_floor",
              ], "context");
            const highlightReturn =
              Boolean(linkedRunListMetricSelection)
              && isComparisonScoreLinkMatch(linkedRunListMetricSelection, ["total_return_pct"], "metrics");
            const highlightDrawdown =
              Boolean(linkedRunListMetricSelection)
              && isComparisonScoreLinkMatch(linkedRunListMetricSelection, ["max_drawdown_pct"], "metrics");
            const highlightWinRate =
              Boolean(linkedRunListMetricSelection)
              && isComparisonScoreLinkMatch(linkedRunListMetricSelection, ["win_rate_pct"], "metrics");
            const highlightTradeCount =
              Boolean(linkedRunListMetricSelection)
              && isComparisonScoreLinkMatch(linkedRunListMetricSelection, ["trade_count"], "metrics");
            return (
              <article className="run-card" key={run.config.run_id} ref={registerRunListCardRef(run.config.run_id)}>
              <div className="run-card-head">
                <div>
                  <strong>{run.config.strategy_id}</strong>
                  <span>
                    {run.config.symbols.join(", ")} / {run.config.strategy_version}
                  </span>
                </div>
                {comparisonLinkedRunRole ? (
                  <button
                    aria-pressed={isRunListSubFocusOrigin(statusSubFocusKey)}
                    className={`run-status run-status-button ${run.status} ${
                      highlightStatus ? "comparison-linked-badge" : ""
                    } ${
                      isRunListSubFocusOrigin(statusSubFocusKey)
                        ? "comparison-linked-badge-origin comparison-linked-subfocus"
                        : ""
                    }`.trim()}
                    onClick={() =>
                      handleRunListScoreLinkSelection(
                        run.config.run_id,
                        "context",
                        "status_bonus",
                        {
                          subFocusKey: statusSubFocusKey,
                        },
                      )
                    }
                    ref={(node) => registerRunListSubFocusRef(run.config.run_id, statusSubFocusKey)(node)}
                    type="button"
                  >
                    {run.status}
                  </button>
                ) : (
                  <div className={`run-status ${run.status}`}>{run.status}</div>
                )}
              </div>
              {comparison ? (
                <div className="run-list-metric-boundaries">
                  <div className="run-list-metric-boundary">
                    <RunListComparisonBoundaryNote
                      contract={runListBoundaryContract}
                      groupKey="supporting_identity"
                    />
                    <div className="run-metrics">
                      <Metric
                        label={getRunListBoundarySurfaceLabel("mode", runListBoundaryContract)}
                        value={run.config.mode}
                      />
                      <Metric
                        label={getRunListBoundarySurfaceLabel("lane", runListBoundaryContract)}
                        value={run.provenance.lane}
                      />
                      <Metric
                        label={getRunListBoundarySurfaceLabel("lifecycle", runListBoundaryContract)}
                        value={run.provenance.strategy?.lifecycle.stage ?? "n/a"}
                      />
                      <Metric
                        label={getRunListBoundarySurfaceLabel("version", runListBoundaryContract)}
                        value={run.config.strategy_version}
                      />
                    </div>
                  </div>
                  <div className="run-list-metric-boundary">
                    <RunListComparisonBoundaryNote
                      contract={runListBoundaryContract}
                      groupKey="eligible_metrics"
                    />
                    <div className="run-metrics">
                      <Metric
                        buttonRef={
                          runListMetricDrillBackEnabled("return")
                            ? (node) => registerRunListSubFocusRef(run.config.run_id, totalReturnSubFocusKey)(node)
                            : undefined
                        }
                        className={highlightReturn ? "comparison-linked-panel" : ""}
                        interactivePressed={isRunListSubFocusOrigin(totalReturnSubFocusKey)}
                        label={getRunListBoundarySurfaceLabel("return", runListBoundaryContract)}
                        onClick={
                          runListMetricDrillBackEnabled("return")
                            ? () =>
                                handleRunListScoreLinkSelection(
                                  run.config.run_id,
                                  "metrics",
                                  "total_return_pct",
                                  {
                                    subFocusKey: totalReturnSubFocusKey,
                                  },
                                )
                            : undefined
                        }
                        value={formatMetric(run.metrics.total_return_pct, "%")}
                      />
                      <Metric
                        buttonRef={
                          runListMetricDrillBackEnabled("drawdown")
                            ? (node) => registerRunListSubFocusRef(run.config.run_id, drawdownSubFocusKey)(node)
                            : undefined
                        }
                        className={highlightDrawdown ? "comparison-linked-panel" : ""}
                        interactivePressed={isRunListSubFocusOrigin(drawdownSubFocusKey)}
                        label={getRunListBoundarySurfaceLabel("drawdown", runListBoundaryContract)}
                        onClick={
                          runListMetricDrillBackEnabled("drawdown")
                            ? () =>
                                handleRunListScoreLinkSelection(
                                  run.config.run_id,
                                  "metrics",
                                  "max_drawdown_pct",
                                  {
                                    subFocusKey: drawdownSubFocusKey,
                                  },
                                )
                            : undefined
                        }
                        value={formatMetric(run.metrics.max_drawdown_pct, "%")}
                      />
                      <Metric
                        buttonRef={
                          runListMetricDrillBackEnabled("win_rate")
                            ? (node) => registerRunListSubFocusRef(run.config.run_id, winRateSubFocusKey)(node)
                            : undefined
                        }
                        className={highlightWinRate ? "comparison-linked-panel" : ""}
                        interactivePressed={isRunListSubFocusOrigin(winRateSubFocusKey)}
                        label={getRunListBoundarySurfaceLabel("win_rate", runListBoundaryContract)}
                        onClick={
                          runListMetricDrillBackEnabled("win_rate")
                            ? () =>
                                handleRunListScoreLinkSelection(
                                  run.config.run_id,
                                  "metrics",
                                  "win_rate_pct",
                                  {
                                    subFocusKey: winRateSubFocusKey,
                                  },
                                )
                            : undefined
                        }
                        value={formatMetric(run.metrics.win_rate_pct, "%")}
                      />
                      <Metric
                        buttonRef={
                          runListMetricDrillBackEnabled("trades")
                            ? (node) => registerRunListSubFocusRef(run.config.run_id, tradeCountSubFocusKey)(node)
                            : undefined
                        }
                        className={highlightTradeCount ? "comparison-linked-panel" : ""}
                        interactivePressed={isRunListSubFocusOrigin(tradeCountSubFocusKey)}
                        label={getRunListBoundarySurfaceLabel("trades", runListBoundaryContract)}
                        onClick={
                          runListMetricDrillBackEnabled("trades")
                            ? () =>
                                handleRunListScoreLinkSelection(
                                  run.config.run_id,
                                  "metrics",
                                  "trade_count",
                                  {
                                    subFocusKey: tradeCountSubFocusKey,
                                  },
                                )
                            : undefined
                        }
                        value={formatMetric(run.metrics.trade_count)}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="run-metrics">
                  <Metric label={getRunListBoundarySurfaceLabel("mode", runListBoundaryContract)} value={run.config.mode} />
                  <Metric label={getRunListBoundarySurfaceLabel("lane", runListBoundaryContract)} value={run.provenance.lane} />
                  <Metric
                    label={getRunListBoundarySurfaceLabel("lifecycle", runListBoundaryContract)}
                    value={run.provenance.strategy?.lifecycle.stage ?? "n/a"}
                  />
                  <Metric label={getRunListBoundarySurfaceLabel("version", runListBoundaryContract)} value={run.config.strategy_version} />
                  <Metric label={getRunListBoundarySurfaceLabel("return", runListBoundaryContract)} value={formatMetric(run.metrics.total_return_pct, "%")} />
                  <Metric label={getRunListBoundarySurfaceLabel("drawdown", runListBoundaryContract)} value={formatMetric(run.metrics.max_drawdown_pct, "%")} />
                  <Metric label={getRunListBoundarySurfaceLabel("win_rate", runListBoundaryContract)} value={formatMetric(run.metrics.win_rate_pct, "%")} />
                  <Metric label={getRunListBoundarySurfaceLabel("trades", runListBoundaryContract)} value={formatMetric(run.metrics.trade_count)} />
                </div>
              )}
              <ExperimentMetadataPills
                benchmarkFamily={run.provenance.experiment.benchmark_family}
                datasetIdentity={run.provenance.market_data?.dataset_identity}
                linkedScore={linkedRunListContextSelection}
                onDrillBackScoreLink={
                  comparisonLinkedRunRole
                    ? (section, componentKey, options) =>
                        handleRunListScoreLinkSelection(
                          run.config.run_id,
                          section,
                          componentKey,
                          options,
                        )
                    : undefined
                }
                panelRunId={run.config.run_id}
                presetId={run.provenance.experiment.preset_id}
                registerSubFocusRef={registerRunListSubFocusRef}
                tags={run.provenance.experiment.tags}
              />
              {run.provenance.strategy ? (
                <RunStrategySnapshot
                  linkedScore={runSnapshotSemanticsEnabled && linkedRunListSelection && linkedRunListSelection.section === "semantics"
                    ? linkedRunListSelection
                    : null}
                  onDrillBackScoreLink={
                    comparisonLinkedRunRole && runSnapshotSemanticsEnabled
                      ? (section, componentKey, options) =>
                          handleRunListScoreLinkSelection(
                            run.config.run_id,
                            section,
                            componentKey,
                            options,
                          )
                      : undefined
                  }
                  panelRunId={runSnapshotSemanticsEnabled ? run.config.run_id : undefined}
                  registerSubFocusRef={runSnapshotSemanticsEnabled ? registerRunListSubFocusRef : undefined}
                  showSemanticCatalogContext={runSnapshotSemanticsEnabled}
                  strategy={run.provenance.strategy}
                />
              ) : null}
              {comparisonLinkedRunRole && run.provenance.reference_id ? (
                <button
                  aria-pressed={isRunListSubFocusOrigin(referenceNoteSubFocusKey)}
                  className={`run-note comparison-run-card-link ${
                    highlightReferenceNote ? "comparison-linked-copy" : ""
                  } ${
                    isRunListSubFocusOrigin(referenceNoteSubFocusKey)
                      ? "comparison-linked-copy-origin comparison-linked-subfocus"
                      : ""
                  }`.trim()}
                  onClick={() =>
                    handleRunListScoreLinkSelection(
                      run.config.run_id,
                      "context",
                      "reference_bonus",
                      {
                        subFocusKey: referenceNoteSubFocusKey,
                      },
                    )
                  }
                  ref={(node) => registerRunListSubFocusRef(run.config.run_id, referenceNoteSubFocusKey)(node)}
                  type="button"
                >
                  Reference {run.provenance.reference_id} ({run.provenance.reference_version ?? "unknown"})
                </button>
              ) : (
                <p className="run-note">
                  {run.provenance.reference_id
                    ? `Reference ${run.provenance.reference_id} (${run.provenance.reference_version ?? "unknown"})`
                    : run.notes[0] ?? "No notes recorded."}
                </p>
              )}
              {run.provenance.reference ? (
                <ReferenceRunProvenanceSummary
                  artifactPaths={run.provenance.artifact_paths}
                  benchmarkArtifacts={run.provenance.benchmark_artifacts}
                  externalCommand={run.provenance.external_command}
                  interactionSource="run_list"
                  linkedScore={referenceProvenanceSemanticsEnabled && linkedRunListSelection && linkedRunListSelection.section !== "metrics"
                    ? linkedRunListSelection
                    : null}
                  onDrillBackScoreLink={
                    comparisonLinkedRunRole && referenceProvenanceSemanticsEnabled
                      ? (section, componentKey, options) =>
                          handleRunListScoreLinkSelection(
                            run.config.run_id,
                            section,
                            componentKey,
                            options,
                          )
                      : undefined
                  }
                  panelRunId={run.config.run_id}
                  registerArtifactHoverRef={referenceProvenanceSemanticsEnabled ? registerRunListArtifactHoverRef : undefined}
                  registerSubFocusRef={referenceProvenanceSemanticsEnabled ? registerRunListSubFocusRef : undefined}
                  reference={run.provenance.reference}
                  referenceVersion={run.provenance.reference_version}
                  strategySemantics={referenceProvenanceSemanticsEnabled ? run.provenance.strategy?.catalog_semantics : null}
                  workingDirectory={run.provenance.working_directory}
                />
              ) : null}
              {run.provenance.runtime_session ? (
                <RunRuntimeSessionSummary
                  linkedScore={linkedRunListSelection && linkedRunListSelection.section === "context"
                    ? linkedRunListSelection
                    : null}
                  onDrillBackScoreLink={
                    comparisonLinkedRunRole
                      ? (section, componentKey, options) =>
                          handleRunListScoreLinkSelection(
                            run.config.run_id,
                            section,
                            componentKey,
                            options,
                          )
                      : undefined
                  }
                  panelRunId={run.config.run_id}
                  registerSubFocusRef={registerRunListSubFocusRef}
                  runtimeSession={run.provenance.runtime_session}
                />
              ) : null}
              {run.orders.length ? (
                <RunOrderLifecycleSummary
                  eligibilityContract={runListBoundaryContract}
                  linkedScore={linkedRunListMetricSelection}
                  onDrillBackScoreLink={
                    comparisonLinkedRunRole
                      ? (section, componentKey, options) =>
                          handleRunListScoreLinkSelection(
                            run.config.run_id,
                            section,
                            componentKey,
                            options,
                          )
                      : undefined
                  }
                  orderControls={orderControls}
                  orderActionBoundaryEnabled={orderActionBoundaryEnabled}
                  orders={run.orders}
                  panelRunId={run.config.run_id}
                  registerSubFocusRef={registerRunListSubFocusRef}
                />
              ) : null}
              {run.provenance.market_data ? (
                <RunMarketDataLineage
                  linkedScore={linkedRunListSelection && linkedRunListSelection.section === "context"
                    ? linkedRunListSelection
                    : null}
                  lineage={run.provenance.market_data}
                  lineageBySymbol={run.provenance.market_data_by_symbol}
                  lineageSummary={run.provenance.lineage_summary}
                  onDrillBackScoreLink={
                    comparisonLinkedRunRole
                      ? (section, componentKey, options) =>
                          handleRunListScoreLinkSelection(
                            run.config.run_id,
                            section,
                            componentKey,
                            options,
                          )
                      : undefined
                  }
                  panelRunId={run.config.run_id}
                  registerSubFocusRef={registerRunListSubFocusRef}
                  rerunBoundaryId={run.provenance.rerun_boundary_id}
                  rerunBoundaryState={run.provenance.rerun_boundary_state}
                  rerunMatchStatus={run.provenance.rerun_match_status}
                  rerunValidationCategory={run.provenance.rerun_validation_category}
                  rerunValidationSummary={run.provenance.rerun_validation_summary}
                  rerunSourceRunId={run.provenance.rerun_source_run_id}
                  rerunTargetBoundaryId={run.provenance.rerun_target_boundary_id}
                />
              ) : null}
              <div className="run-card-actions">
                {comparison ? (
                  <button
                    className="ghost-button"
                    disabled={!compareSelectionAllowed}
                    onClick={() => comparison.onToggleRunSelection(run.config.run_id)}
                    title={!compareSelectionAllowed ? compareSelectionAvailability?.reason ?? undefined : undefined}
                    type="button"
                  >
                    {comparison.selectedRunIds.includes(run.config.run_id)
                      ? "Remove from compare"
                      : "Add to compare"}
                  </button>
                ) : null}
                {rerunActions && run.provenance.rerun_boundary_id
                  ? rerunActions.map((action) => (
                    <button
                      className="ghost-button"
                      disabled={!runActionAvailability?.[action.availabilityKey]?.allowed}
                      key={action.label}
                      onClick={() => void action.onRerun(run.provenance.rerun_boundary_id!)}
                      title={
                        runActionAvailability?.[action.availabilityKey]?.allowed
                          ? undefined
                          : runActionAvailability?.[action.availabilityKey]?.reason ?? undefined
                      }
                      type="button"
                    >
                      {action.label}
                    </button>
                  ))
                  : null}
                {onStop && run.status === "running" ? (
                    <button
                      className="ghost-button"
                      disabled={!stopAllowed}
                      onClick={() => void onStop(run.config.run_id)}
                      title={!stopAllowed ? stopAvailability?.reason ?? undefined : undefined}
                      type="button"
                    >
                      Stop
                    </button>
                ) : null}
              </div>
              {comparison && workflowBoundaryEnabled ? (
                <RunListComparisonBoundaryNote
                  contract={runListBoundaryContract}
                  groupKey="operational_workflow"
                />
              ) : null}
              </article>
            );
          })}
        </div>
      ) : (
        <p className="empty-state">No runs yet.</p>
      )}
      {comparison ? (
        <RunComparisonPanel
          comparison={comparison.payload}
          error={comparison.error}
          loading={comparison.loading}
          onChangeScoreLink={comparison.onChangeSelectedScoreLink}
          selectedScoreLink={comparison.selectedScoreLink}
          selectedRunIds={comparison.selectedRunIds}
        />
      ) : null}
    </section>
  );
}

export function RunComparisonPanel({
  comparison,
  error,
  loading,
  onChangeScoreLink,
  selectedScoreLink,
  selectedRunIds,
}: {
  comparison: RunComparison | null;
  error: string | null;
  loading: boolean;
  onChangeScoreLink: (
    value: ComparisonScoreLinkTarget | null,
    historyMode?: ComparisonHistoryWriteMode,
  ) => void;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
  selectedRunIds: string[];
}) {
  if (!selectedRunIds.length) {
    return null;
  }

  if (selectedRunIds.length < 2) {
    return (
      <section className="comparison-panel comparison-panel-empty">
        <p className="kicker">Comparison deck</p>
        <p className="empty-state">Select at least two backtests to compare them side by side.</p>
      </section>
    );
  }

  if (loading) {
    return (
      <section className="comparison-panel comparison-panel-empty">
        <p className="kicker">Comparison deck</p>
        <p className="empty-state">Preparing side-by-side benchmark view...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="comparison-panel comparison-panel-empty">
        <p className="kicker">Comparison deck</p>
        <p className="empty-state">Comparison failed: {error}</p>
      </section>
    );
  }

  if (!comparison) {
    return null;
  }

  const [primaryNarrative, ...secondaryNarratives] = comparison.narratives;
  const tooltipScopeId = sanitizeComparisonTooltipId(useId());
  const tooltipTargetRefs = useRef(new Map<string, HTMLElement>());
  const tooltipBubbleRefs = useRef(new Map<string, HTMLSpanElement>());
  const tooltipInteractionIdsRef = useRef(new Map<string, string>());
  const tooltipInteractionKeysRef = useRef(new Map<string, string>());
  const narrativeCardRefs = useRef(new Map<string, HTMLElement>());
  const overviewCardRefs = useRef(new Map<string, HTMLButtonElement>());
  const scoreDetailRowRefs = useRef(new Map<string, HTMLButtonElement>());
  const metricCellRefs = useRef(new Map<string, HTMLElement>());
  const runCardRefs = useRef(new Map<string, HTMLElement>());
  const runCardSubFocusRefs = useRef(new Map<string, HTMLElement>());
  const provenancePanelRefs = useRef(new Map<string, HTMLElement>());
  const provenanceSubFocusRefs = useRef(new Map<string, HTMLElement>());
  const provenanceArtifactHoverRefs = useRef(new Map<string, HTMLElement>());
  const tooltipOpenTimerRef = useRef<number | null>(null);
  const tooltipCloseTimerRef = useRef<number | null>(null);
  const metricPointerSampleRef = useRef<{
    cellHeight: number;
    cellWidth: number;
    metricRowKey: string;
    runColumnKey: string;
    time: number;
    x: number;
    y: number;
  } | null>(null);
  const metricSweepStateRef = useRef<{
    axis: "column_down" | "column_up" | "row";
    contextKey: string;
    until: number;
  } | null>(null);
  const [activeTooltipId, setActiveTooltipId] = useState<string | null>(null);
  const [activeTooltipLayout, setActiveTooltipLayout] = useState<ComparisonTooltipLayout | null>(
    null,
  );
  const [dismissedTooltipId, setDismissedTooltipId] = useState<string | null>(null);
  const [expandedNarrativeScoreBreakdowns, setExpandedNarrativeScoreBreakdowns] = useState<
    Record<string, boolean>
  >({});
  const [tooltipTuning, setTooltipTuning] = useState<ComparisonTooltipTuning>(
    DEFAULT_COMPARISON_TOOLTIP_TUNING,
  );
  const [tooltipTuningPresets, setTooltipTuningPresets] = useState<
    Record<string, ComparisonTooltipTuning>
  >({});
  const [selectedTooltipPresetName, setSelectedTooltipPresetName] = useState("");
  const [tooltipPresetDraftName, setTooltipPresetDraftName] = useState("");
  const [pendingTooltipPresetImportConflict, setPendingTooltipPresetImportConflict] =
    useState<ComparisonTooltipPendingPresetImportConflict | null>(null);
  const [tooltipShareDraft, setTooltipShareDraft] = useState("");
  const [tooltipShareFeedback, setTooltipShareFeedback] = useState<string | null>(null);
  const [hasHydratedTooltipTuningState, setHasHydratedTooltipTuningState] = useState(
    !SHOW_COMPARISON_TOOLTIP_TUNING_PANEL,
  );
  const intentClassName = getComparisonIntentClassName(comparison.intent);
  const intentTooltip = formatComparisonIntentTooltip(comparison.intent);
  const baselineTooltip = formatComparisonCueTooltip(comparison.intent, "baseline");
  const bestTooltip = formatComparisonCueTooltip(comparison.intent, "best");
  const insightTooltip = formatComparisonCueTooltip(comparison.intent, "insight");
  const intentChipTooltipId = buildComparisonTooltipId(tooltipScopeId, "intent-chip");
  const legendModeTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-mode");
  const legendBaselineTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-baseline");
  const legendBestTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-best");
  const legendInsightTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-insight");
  const baselineRunTooltipId = buildComparisonTooltipId(
    tooltipScopeId,
    "baseline-run",
    comparison.baseline_run_id,
  );
  const topInsightTooltipId = buildComparisonTooltipId(tooltipScopeId, "top-insight");
  const featuredNarrativeTooltipId = primaryNarrative
    ? buildComparisonTooltipId(tooltipScopeId, "featured-narrative", primaryNarrative.run_id)
    : undefined;
  const metricTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.metric_hover_close_ms,
    hoverOpenDelayMs: tooltipTuning.metric_hover_open_ms,
  };
  const metricRowSweepTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.row_sweep_close_ms,
    hoverOpenDelayMs: tooltipTuning.row_sweep_open_ms,
  };
  const metricColumnDownSweepTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.column_down_sweep_close_ms,
    hoverOpenDelayMs: tooltipTuning.column_down_sweep_open_ms,
  };
  const metricColumnUpSweepTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.column_up_sweep_close_ms,
    hoverOpenDelayMs: tooltipTuning.column_up_sweep_open_ms,
  };
  const selectedTooltipPreset = selectedTooltipPresetName
    ? tooltipTuningPresets[selectedTooltipPresetName] ?? null
    : null;
  const createTooltipTuningPresetState = (): ComparisonTooltipTuningPresetStateV1 => ({
    current_tuning: { ...tooltipTuning },
    presets: cloneComparisonTooltipPresetMap(tooltipTuningPresets),
    selected_preset_name: selectedTooltipPresetName || null,
    version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
  });
  const tooltipShareUrl = useMemo(
    () => buildComparisonTooltipTuningShareUrl(createTooltipTuningPresetState()),
    [selectedTooltipPresetName, tooltipTuning, tooltipTuningPresets],
  );
  const selectedTooltipPresetShareUrl = useMemo(() => {
    if (!selectedTooltipPresetName || !selectedTooltipPreset) {
      return "";
    }
    return buildComparisonTooltipTuningShareUrl(
      createComparisonTooltipTuningSinglePresetShare(
        selectedTooltipPresetName,
        selectedTooltipPreset,
      ),
    );
  }, [selectedTooltipPreset, selectedTooltipPresetName]);

  const applyTooltipTuningPresetState = (state: ComparisonTooltipTuningPresetStateV1) => {
    setTooltipTuning({ ...state.current_tuning });
    setTooltipTuningPresets(cloneComparisonTooltipPresetMap(state.presets));
    const nextSelectedPresetName = state.selected_preset_name ?? "";
    setSelectedTooltipPresetName(nextSelectedPresetName);
    setTooltipPresetDraftName(nextSelectedPresetName);
    setPendingTooltipPresetImportConflict(null);
  };

  const updateTooltipShareDraft = (value: string) => {
    setTooltipShareDraft(value);
    setPendingTooltipPresetImportConflict(null);
  };

  const applySingleTooltipPresetImport = (
    importedPresetName: string,
    tuning: ComparisonTooltipTuning,
    options?: {
      policy?: ComparisonTooltipPresetImportConflictPolicy;
      renamedPresetName?: string;
      verb?: "Imported" | "Loaded";
    },
  ) => {
    const mergedPreset = mergeComparisonTooltipSinglePresetIntoState(
      createTooltipTuningPresetState(),
      importedPresetName,
      tuning,
      options?.policy ?? "overwrite",
      options?.renamedPresetName,
    );
    applyTooltipTuningPresetState(mergedPreset.state);
    setTooltipShareDraft(
      JSON.stringify(
        createComparisonTooltipTuningSinglePresetShare(
          mergedPreset.resolution.final_preset_name,
          tuning,
        ),
        null,
        2,
      ),
    );
    setTooltipShareFeedback(
      formatComparisonTooltipPresetImportFeedback(mergedPreset.resolution, {
        verb: options?.verb,
      }),
    );
  };

  const beginPendingTooltipPresetImportConflict = (
    importedShare: Extract<ComparisonTooltipTuningShareImport, { kind: "preset" }>,
  ) => {
    setPendingTooltipPresetImportConflict({
      imported_preset_name: importedShare.preset_name,
      proposed_preset_name: createAvailableComparisonTooltipPresetName(
        tooltipTuningPresets,
        importedShare.preset_name,
      ),
      raw: importedShare.raw,
      tuning: importedShare.tuning,
    });
    setTooltipShareDraft(importedShare.raw);
    setTooltipShareFeedback(
      `Preset "${importedShare.preset_name}" already exists. Choose rename, overwrite, or skip.`,
    );
  };

  const updateTooltipTuning = (
    key: keyof ComparisonTooltipTuning,
    rawValue: string,
  ) => {
    const nextValue = Number(rawValue);
    if (!Number.isFinite(nextValue)) {
      return;
    }
    setTooltipTuning((current) => ({
      ...current,
      [key]: nextValue,
    }));
    setSelectedTooltipPresetName("");
    setPendingTooltipPresetImportConflict(null);
  };

  const exportTooltipPresetBundle = () => {
    const nextState = createTooltipTuningPresetState();
    setTooltipShareDraft(JSON.stringify(nextState, null, 2));
    setTooltipShareFeedback(
      `Exported current tuning with ${Object.keys(nextState.presets).length} saved preset(s).`,
    );
    setPendingTooltipPresetImportConflict(null);
  };

  const exportSelectedTooltipPreset = () => {
    if (!selectedTooltipPresetName || !selectedTooltipPreset) {
      setTooltipShareFeedback("Select a saved preset to export a single named preset.");
      return;
    }
    const presetShare = createComparisonTooltipTuningSinglePresetShare(
      selectedTooltipPresetName,
      selectedTooltipPreset,
    );
    setTooltipShareDraft(JSON.stringify(presetShare, null, 2));
    setTooltipShareFeedback(`Exported preset "${selectedTooltipPresetName}".`);
    setPendingTooltipPresetImportConflict(null);
  };

  const importTooltipPresetBundle = () => {
    const importedShare = parseComparisonTooltipTuningShareImport(tooltipShareDraft);
    if (!importedShare) {
      setTooltipShareFeedback(
        "Import failed. Provide valid tooltip tuning JSON for a bundle or named preset.",
      );
      return;
    }
    if (importedShare.kind === "bundle") {
      applyTooltipTuningPresetState(importedShare.state);
      setTooltipShareDraft(importedShare.raw);
      setTooltipShareFeedback(
        `Imported current tuning with ${Object.keys(importedShare.state.presets).length} saved preset(s).`,
      );
      return;
    }
    if (tooltipTuningPresets[importedShare.preset_name]) {
      beginPendingTooltipPresetImportConflict(importedShare);
      return;
    }
    applySingleTooltipPresetImport(importedShare.preset_name, importedShare.tuning, {
      policy: "overwrite",
    });
  };

  const updatePendingTooltipPresetImportName = (value: string) => {
    setPendingTooltipPresetImportConflict((current) =>
      current
        ? {
            ...current,
            proposed_preset_name: value,
          }
        : current,
    );
  };

  const resolvePendingTooltipPresetImportConflict = (
    action: "overwrite" | "rename" | "skip",
  ) => {
    if (!pendingTooltipPresetImportConflict) {
      return;
    }
    if (action === "skip") {
      setPendingTooltipPresetImportConflict(null);
      setTooltipShareFeedback(
        `Skipped importing preset "${pendingTooltipPresetImportConflict.imported_preset_name}".`,
      );
      return;
    }
    if (action === "overwrite") {
      applySingleTooltipPresetImport(
        pendingTooltipPresetImportConflict.imported_preset_name,
        pendingTooltipPresetImportConflict.tuning,
        { policy: "overwrite" },
      );
      return;
    }
    const renamedPresetName = pendingTooltipPresetImportConflict.proposed_preset_name.trim();
    if (!renamedPresetName) {
      setTooltipShareFeedback("Enter a new preset name before importing with rename.");
      return;
    }
    if (tooltipTuningPresets[renamedPresetName]) {
      setTooltipShareFeedback(
        `Preset "${renamedPresetName}" already exists. Choose a different rename target.`,
      );
      return;
    }
    applySingleTooltipPresetImport(
      pendingTooltipPresetImportConflict.imported_preset_name,
      pendingTooltipPresetImportConflict.tuning,
      {
        policy: "rename",
        renamedPresetName,
      },
    );
  };

  const copyTooltipShareUrl = async () => {
    if (!navigator.clipboard?.writeText) {
      setTooltipShareFeedback("Clipboard is unavailable. Copy the share URL from the field.");
      return;
    }
    try {
      await navigator.clipboard.writeText(tooltipShareUrl);
      setTooltipShareFeedback("Copied a share URL for the current tooltip tuning bundle.");
    } catch {
      setTooltipShareFeedback("Clipboard copy failed. Copy the share URL from the field.");
    }
  };

  const copySelectedTooltipPresetShareUrl = async () => {
    if (!selectedTooltipPresetName || !selectedTooltipPresetShareUrl) {
      setTooltipShareFeedback("Select a saved preset to share a single preset URL.");
      return;
    }
    if (!navigator.clipboard?.writeText) {
      setTooltipShareFeedback(
        "Clipboard is unavailable. Copy the selected preset URL from the field.",
      );
      return;
    }
    try {
      await navigator.clipboard.writeText(selectedTooltipPresetShareUrl);
      setTooltipShareFeedback(`Copied a share URL for preset "${selectedTooltipPresetName}".`);
    } catch {
      setTooltipShareFeedback("Clipboard copy failed. Copy the selected preset URL from the field.");
    }
  };

  const saveTooltipPreset = () => {
    const presetName = tooltipPresetDraftName.trim();
    if (!presetName) {
      return;
    }
    setTooltipTuningPresets((current) => ({
      ...current,
      [presetName]: { ...tooltipTuning },
    }));
    setSelectedTooltipPresetName(presetName);
    setTooltipPresetDraftName(presetName);
    setPendingTooltipPresetImportConflict(null);
  };

  const loadTooltipPreset = (presetName: string) => {
    if (!presetName) {
      setSelectedTooltipPresetName("");
      return;
    }
    const preset = tooltipTuningPresets[presetName];
    if (!preset) {
      return;
    }
    setTooltipTuning({ ...preset });
    setSelectedTooltipPresetName(presetName);
    setTooltipPresetDraftName(presetName);
    setPendingTooltipPresetImportConflict(null);
  };

  const deleteTooltipPreset = () => {
    if (!selectedTooltipPresetName) {
      return;
    }
    setTooltipTuningPresets((current) => {
      const next = { ...current };
      delete next[selectedTooltipPresetName];
      return next;
    });
    setSelectedTooltipPresetName("");
    setTooltipPresetDraftName("");
    setPendingTooltipPresetImportConflict(null);
  };

  const resetTooltipTuning = () => {
    setTooltipTuning(DEFAULT_COMPARISON_TOOLTIP_TUNING);
    setSelectedTooltipPresetName("");
    setPendingTooltipPresetImportConflict(null);
  };

  const clearComparisonTooltipOpenTimer = () => {
    if (tooltipOpenTimerRef.current !== null) {
      window.clearTimeout(tooltipOpenTimerRef.current);
      tooltipOpenTimerRef.current = null;
    }
  };

  const clearComparisonTooltipCloseTimer = () => {
    if (tooltipCloseTimerRef.current !== null) {
      window.clearTimeout(tooltipCloseTimerRef.current);
      tooltipCloseTimerRef.current = null;
    }
  };

  const clearComparisonTooltipTimers = () => {
    clearComparisonTooltipOpenTimer();
    clearComparisonTooltipCloseTimer();
  };

  const syncSelectedMetricTooltipState = (tooltipId: string, visible: boolean) => {
    if (!selectedScoreLink || selectedScoreLink.source !== "metric") {
      return;
    }
    const expectedTooltipKey = buildComparisonMetricTooltipKey(
      selectedScoreLink.componentKey,
      selectedScoreLink.originRunId ?? selectedScoreLink.narrativeRunId,
    );
    const interactionKey = tooltipInteractionKeysRef.current.get(tooltipId) ?? null;
    if (interactionKey !== expectedTooltipKey) {
      return;
    }
    const nextTooltipKey = visible ? interactionKey : null;
    if (selectedScoreLink.tooltipKey === nextTooltipKey) {
      return;
    }
    updateSelectedScoreLink(
      {
        ...selectedScoreLink,
        tooltipKey: nextTooltipKey,
      },
      "replace",
    );
  };

  const showComparisonTooltip = (tooltipId: string) => {
    setDismissedTooltipId((current) => (current === tooltipId ? null : current));
    setActiveTooltipId(tooltipId);
    syncSelectedMetricTooltipState(tooltipId, true);
  };

  const hideComparisonTooltip = (tooltipId: string) => {
    setActiveTooltipId((current) => (current === tooltipId ? null : current));
    setDismissedTooltipId((current) => (current === tooltipId ? null : current));
    syncSelectedMetricTooltipState(tooltipId, false);
  };

  const dismissComparisonTooltip = (tooltipId: string) => {
    setActiveTooltipId((current) => (current === tooltipId ? null : current));
    setActiveTooltipLayout((current) => (current?.tooltipId === tooltipId ? null : current));
    setDismissedTooltipId(tooltipId);
    syncSelectedMetricTooltipState(tooltipId, false);
  };

  const scheduleComparisonTooltipShow = (
    tooltipId: string,
    options?: ComparisonTooltipInteractionOptions,
  ) => {
    clearComparisonTooltipCloseTimer();
    const delayMs = options?.hoverOpenDelayMs ?? 0;
    if (delayMs <= 0) {
      clearComparisonTooltipOpenTimer();
      showComparisonTooltip(tooltipId);
      return;
    }
    clearComparisonTooltipOpenTimer();
    tooltipOpenTimerRef.current = window.setTimeout(() => {
      tooltipOpenTimerRef.current = null;
      showComparisonTooltip(tooltipId);
    }, delayMs);
  };

  const scheduleComparisonTooltipHide = (
    tooltipId: string,
    options?: ComparisonTooltipInteractionOptions,
  ) => {
    clearComparisonTooltipOpenTimer();
    const delayMs = options?.hoverCloseDelayMs ?? 0;
    if (delayMs <= 0) {
      clearComparisonTooltipCloseTimer();
      hideComparisonTooltip(tooltipId);
      return;
    }
    clearComparisonTooltipCloseTimer();
    tooltipCloseTimerRef.current = window.setTimeout(() => {
      tooltipCloseTimerRef.current = null;
      hideComparisonTooltip(tooltipId);
    }, delayMs);
  };

  const registerComparisonTooltipTargetRef =
    (tooltipId?: string, interactionKey?: string) => (node: HTMLElement | null) => {
    if (!tooltipId) {
      return;
    }
    if (node) {
      tooltipTargetRefs.current.set(tooltipId, node);
      if (interactionKey) {
        tooltipInteractionIdsRef.current.set(interactionKey, tooltipId);
        tooltipInteractionKeysRef.current.set(tooltipId, interactionKey);
      }
      return;
    }
    tooltipTargetRefs.current.delete(tooltipId);
    if (interactionKey) {
      tooltipInteractionIdsRef.current.delete(interactionKey);
      tooltipInteractionKeysRef.current.delete(tooltipId);
    }
  };

  const registerComparisonTooltipBubbleRef =
    (tooltipId: string) => (node: HTMLSpanElement | null) => {
      if (node) {
        tooltipBubbleRefs.current.set(tooltipId, node);
        return;
      }
      tooltipBubbleRefs.current.delete(tooltipId);
    };

  const registerComparisonNarrativeCardRef =
    (runId: string) => (node: HTMLElement | null) => {
      if (node) {
        narrativeCardRefs.current.set(runId, node);
        return;
      }
      narrativeCardRefs.current.delete(runId);
    };

  const buildComparisonOverviewCardRefKey = (
    narrativeRunId: string,
    section: ComparisonScoreSection,
  ) => `${narrativeRunId}:${section}`;
  const buildComparisonScoreDetailRowRefKey = (
    narrativeRunId: string,
    section: ComparisonScoreSection,
    componentKey: string,
  ) => `${narrativeRunId}:${section}:${componentKey}`;
  const buildComparisonMetricCellRefKey = (runId: string, componentKey: string) => `${runId}:${componentKey}`;
  const buildComparisonRunCardSubFocusRefKey = (runId: string, subFocusKey: string) =>
    `${runId}:${subFocusKey}`;
  const buildComparisonProvenanceSubFocusRefKey = (runId: string, subFocusKey: string) =>
    `${runId}:${subFocusKey}`;
  const buildComparisonProvenanceArtifactHoverRefKey = (
    runId: string,
    artifactHoverKey: string,
  ) => `${runId}:${artifactHoverKey}`;

  const registerComparisonOverviewCardRef =
    (narrativeRunId: string, section: ComparisonScoreSection) =>
    (node: HTMLButtonElement | null) => {
      const key = buildComparisonOverviewCardRefKey(narrativeRunId, section);
      if (node) {
        overviewCardRefs.current.set(key, node);
        return;
      }
      overviewCardRefs.current.delete(key);
    };

  const registerComparisonScoreDetailRowRef =
    (narrativeRunId: string, section: ComparisonScoreSection, componentKey: string) =>
    (node: HTMLButtonElement | null) => {
      const key = buildComparisonScoreDetailRowRefKey(narrativeRunId, section, componentKey);
      if (node) {
        scoreDetailRowRefs.current.set(key, node);
        return;
      }
      scoreDetailRowRefs.current.delete(key);
    };

  const registerComparisonMetricCellRef =
    (runId: string, componentKey: string) => (node: HTMLElement | null) => {
      const key = buildComparisonMetricCellRefKey(runId, componentKey);
      if (node) {
        metricCellRefs.current.set(key, node);
        return;
      }
      metricCellRefs.current.delete(key);
    };

  const registerComparisonRunCardRef = (runId: string) => (node: HTMLElement | null) => {
    if (node) {
      runCardRefs.current.set(runId, node);
      return;
    }
    runCardRefs.current.delete(runId);
  };

  const registerComparisonRunCardSubFocusRef =
    (runId: string, subFocusKey: string) => (node: HTMLElement | null) => {
      const key = buildComparisonRunCardSubFocusRefKey(runId, subFocusKey);
      if (node) {
        runCardSubFocusRefs.current.set(key, node);
        return;
      }
      runCardSubFocusRefs.current.delete(key);
    };

  const registerComparisonProvenancePanelRef = (runId: string) => (node: HTMLElement | null) => {
    if (node) {
      provenancePanelRefs.current.set(runId, node);
      return;
    }
    provenancePanelRefs.current.delete(runId);
  };

  const registerComparisonProvenanceSubFocusRef =
    (runId: string, subFocusKey: string) => (node: HTMLElement | null) => {
      const key = buildComparisonProvenanceSubFocusRefKey(runId, subFocusKey);
      if (node) {
        provenanceSubFocusRefs.current.set(key, node);
        return;
      }
      provenanceSubFocusRefs.current.delete(key);
    };

  const registerComparisonProvenanceArtifactHoverRef =
    (runId: string, artifactHoverKey: string) => (node: HTMLElement | null) => {
      const key = buildComparisonProvenanceArtifactHoverRefKey(runId, artifactHoverKey);
      if (node) {
        provenanceArtifactHoverRefs.current.set(key, node);
        return;
      }
      provenanceArtifactHoverRefs.current.delete(key);
    };

  const updateSelectedScoreLink = (
    nextSelection: ComparisonScoreLinkTarget | null,
    historyMode: ComparisonHistoryWriteMode = nextSelection ? "push" : "replace",
  ) => {
    onChangeScoreLink(nextSelection, historyMode);
  };

  const handleComparisonNarrativeScoreBreakdownExpandedChange = (
    narrativeRunId: string,
    expanded: boolean,
  ) => {
    setExpandedNarrativeScoreBreakdowns((current) =>
      current[narrativeRunId] === expanded
        ? current
        : {
            ...current,
            [narrativeRunId]: expanded,
          },
    );
  };

  const handleComparisonScoreDrillBack = (
    runId: string,
    section: ComparisonScoreSection,
    componentKey: string,
    source: ComparisonScoreLinkSource,
    options?: ComparisonScoreDrillBackOptions,
  ) => {
    const nextSelection = resolveComparisonScoreDrillBackTarget(
      comparison,
      selectedScoreLink,
      runId,
      section,
      componentKey,
    );
    if (!nextSelection) {
      return;
    }
    const resolvedSelection = {
      ...nextSelection,
      detailExpanded:
        options?.detailExpanded !== undefined
          ? options.detailExpanded
          : source === "drillback"
            ? true
            : (expandedNarrativeScoreBreakdowns[nextSelection.narrativeRunId] ?? null),
      artifactDetailExpanded: options?.artifactDetailExpanded ?? null,
      artifactLineDetailExpanded: options?.artifactLineDetailExpanded ?? null,
      artifactLineDetailView: options?.artifactLineDetailView ?? null,
      artifactLineMicroView: options?.artifactLineMicroView ?? null,
      artifactLineNotePage: options?.artifactLineNotePage ?? null,
      artifactLineDetailHoverKey: options?.artifactLineDetailHoverKey ?? null,
      artifactLineDetailScrubStep: options?.artifactLineDetailScrubStep ?? null,
      originRunId: runId,
      source,
      subFocusKey: options?.subFocusKey ?? null,
      tooltipKey: options?.tooltipKey ?? null,
      artifactHoverKey: options?.artifactHoverKey ?? null,
    } satisfies ComparisonScoreLinkTarget;
    updateSelectedScoreLink(
      isSameComparisonScoreLinkSurface(selectedScoreLink, resolvedSelection)
        ? null
        : resolvedSelection,
      options?.historyMode,
    );
  };

  const getComparisonTooltipTargetProps = (
    tooltipId?: string,
    options?: ComparisonTooltipInteractionOptions,
  ): ComparisonTooltipTargetProps | undefined => {
    if (!tooltipId) {
      return undefined;
    }

    return {
      "aria-describedby": dismissedTooltipId === tooltipId ? undefined : tooltipId,
      "data-tooltip-visible":
        activeTooltipId === tooltipId && dismissedTooltipId !== tooltipId ? "true" : "false",
      onBlur: () => {
        clearComparisonTooltipTimers();
        hideComparisonTooltip(tooltipId);
      },
      onFocus: () => {
        clearComparisonTooltipTimers();
        showComparisonTooltip(tooltipId);
      },
      onKeyDown: (event: KeyboardEvent<HTMLElement>) => {
        if (event.key === "Escape") {
          clearComparisonTooltipTimers();
          dismissComparisonTooltip(tooltipId);
          event.stopPropagation();
        }
      },
      onMouseEnter: () => scheduleComparisonTooltipShow(tooltipId, options),
      onMouseLeave: () => scheduleComparisonTooltipHide(tooltipId, options),
    };
  };

  const recordMetricPointerSample = (
    event: MouseEvent<HTMLElement>,
    metricRowKey: string,
    runColumnKey: string,
  ) => {
    const cellRect = event.currentTarget.getBoundingClientRect();
    metricPointerSampleRef.current = {
      cellHeight: cellRect.height,
      cellWidth: cellRect.width,
      metricRowKey,
      runColumnKey,
      time: event.timeStamp,
      x: event.clientX,
      y: event.clientY,
    };
  };

  const resolveMetricTooltipInteraction = (
    event: MouseEvent<HTMLElement>,
    metricRowKey: string,
    runColumnKey: string,
  ) => {
    const cellRect = event.currentTarget.getBoundingClientRect();
    const sample = {
      cellHeight: cellRect.height,
      cellWidth: cellRect.width,
      metricRowKey,
      runColumnKey,
      time: event.timeStamp,
      x: event.clientX,
      y: event.clientY,
    };
    const previousSample = metricPointerSampleRef.current;
    metricPointerSampleRef.current = sample;

    if (!previousSample) {
      return metricTooltipInteraction;
    }

    const deltaTime = Math.max(sample.time - previousSample.time, 1);
    const deltaX = Math.abs(sample.x - previousSample.x);
    const deltaY = Math.abs(sample.y - previousSample.y);
    const signedDeltaY = sample.y - previousSample.y;
    const horizontalVelocity = deltaX / deltaTime;
    const verticalVelocity = deltaY / deltaTime;
    const pointerSpeed = Math.hypot(deltaX, deltaY) / deltaTime;
    const averageCellWidth = (sample.cellWidth + previousSample.cellWidth) / 2;
    const averageCellHeight = (sample.cellHeight + previousSample.cellHeight) / 2;
    const sweepTimeThreshold = getAdaptiveMetricSweepTimeThreshold(pointerSpeed, tooltipTuning);
    const horizontalDistanceThreshold = getAdaptiveMetricSweepDistanceThreshold(
      averageCellWidth,
      pointerSpeed,
      "horizontal",
      tooltipTuning,
    );
    const verticalDistanceThreshold = getAdaptiveMetricSweepDistanceThreshold(
      averageCellHeight,
      pointerSpeed,
      "vertical",
      tooltipTuning,
    );
    const isSameMetricRow = previousSample.metricRowKey === metricRowKey;
    const isSameRunColumn = previousSample.runColumnKey === runColumnKey;
    const isHorizontalSweep =
      isSameMetricRow &&
      deltaTime <= sweepTimeThreshold &&
      deltaX >= horizontalDistanceThreshold &&
      deltaX >= deltaY * 2 &&
      horizontalVelocity >= tooltipTuning.horizontal_velocity_threshold;
    const isVerticalSweep =
      isSameRunColumn &&
      deltaTime <= sweepTimeThreshold &&
      deltaY >= verticalDistanceThreshold &&
      deltaY >= deltaX * 2 &&
      verticalVelocity >= tooltipTuning.vertical_velocity_threshold;
    const columnSweepAxis = signedDeltaY >= 0 ? "column_down" : "column_up";

    if (isHorizontalSweep) {
      metricSweepStateRef.current = {
        axis: "row",
        contextKey: metricRowKey,
        until: sample.time + tooltipTuning.row_sweep_hold_ms,
      };
      return metricRowSweepTooltipInteraction;
    }

    if (isVerticalSweep) {
      metricSweepStateRef.current = {
        axis: columnSweepAxis,
        contextKey: runColumnKey,
        until:
          sample.time +
          (columnSweepAxis === "column_down"
            ? tooltipTuning.column_down_sweep_hold_ms
            : tooltipTuning.column_up_sweep_hold_ms),
      };
      return columnSweepAxis === "column_down"
        ? metricColumnDownSweepTooltipInteraction
        : metricColumnUpSweepTooltipInteraction;
    }

    if (
      metricSweepStateRef.current &&
      sample.time < metricSweepStateRef.current.until
    ) {
      if (
        metricSweepStateRef.current.axis === "row" &&
        metricSweepStateRef.current.contextKey === metricRowKey
      ) {
        return metricRowSweepTooltipInteraction;
      }
      if (
        (metricSweepStateRef.current.axis === "column_down" ||
          metricSweepStateRef.current.axis === "column_up") &&
        metricSweepStateRef.current.contextKey === runColumnKey
      ) {
        return metricSweepStateRef.current.axis === "column_down"
          ? metricColumnDownSweepTooltipInteraction
          : metricColumnUpSweepTooltipInteraction;
      }
    }

    if (
      (!isSameMetricRow && metricSweepStateRef.current?.axis === "row") ||
      (!isSameRunColumn &&
        (metricSweepStateRef.current?.axis === "column_down" ||
          metricSweepStateRef.current?.axis === "column_up"))
    ) {
      metricSweepStateRef.current = null;
    }

    return metricTooltipInteraction;
  };

  const getMetricComparisonTooltipTargetProps = (
    tooltipId?: string,
    metricRowKey?: string,
    runColumnKey?: string,
  ): ComparisonTooltipTargetProps | undefined => {
    const baseProps = getComparisonTooltipTargetProps(tooltipId, metricTooltipInteraction);

    if (!baseProps || !tooltipId || !metricRowKey || !runColumnKey) {
      return baseProps;
    }

    return {
      ...baseProps,
      onMouseEnter: (event: MouseEvent<HTMLElement>) => {
        const interaction = resolveMetricTooltipInteraction(event, metricRowKey, runColumnKey);
        scheduleComparisonTooltipShow(tooltipId, interaction);
      },
      onMouseLeave: (event: MouseEvent<HTMLElement>) => {
        recordMetricPointerSample(event, metricRowKey, runColumnKey);
        scheduleComparisonTooltipHide(tooltipId, metricTooltipInteraction);
      },
      onMouseMove: (event: MouseEvent<HTMLElement>) =>
        recordMetricPointerSample(event, metricRowKey, runColumnKey),
    };
  };

  useEffect(() => clearComparisonTooltipTimers, []);

  useEffect(() => {
    if (!SHOW_COMPARISON_TOOLTIP_TUNING_PANEL) {
      return;
    }
    const storedState = loadComparisonTooltipTuningPresetState();
    const sharedImport = loadComparisonTooltipTuningShareImportFromUrl();
    const appliedImport = sharedImport
      ? applyComparisonTooltipTuningShareImport(
          storedState,
          sharedImport,
          DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY,
        )
      : null;
    applyTooltipTuningPresetState(appliedImport?.state ?? storedState);
    if (sharedImport) {
      if (appliedImport?.kind === "preset" && sharedImport.kind === "preset") {
        setTooltipShareDraft(
          JSON.stringify(
            createComparisonTooltipTuningSinglePresetShare(
              appliedImport.resolution.final_preset_name,
              sharedImport.tuning,
            ),
            null,
            2,
          ),
        );
        setTooltipShareFeedback(
          formatComparisonTooltipPresetImportFeedback(appliedImport.resolution, {
            verb: "Loaded",
          }),
        );
      } else {
        setTooltipShareDraft(sharedImport.raw);
        setTooltipShareFeedback(
          sharedImport.kind === "bundle"
            ? "Loaded tooltip tuning presets from the share URL."
            : `Loaded preset "${sharedImport.preset_name}" from the share URL.`,
        );
      }
    }
    setHasHydratedTooltipTuningState(true);
  }, []);

  useEffect(() => {
    if (!SHOW_COMPARISON_TOOLTIP_TUNING_PANEL || !hasHydratedTooltipTuningState) {
      return;
    }
    persistComparisonTooltipTuningPresetState({
      current_tuning: tooltipTuning,
      presets: tooltipTuningPresets,
      selected_preset_name: selectedTooltipPresetName || null,
      version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
    });
  }, [
    hasHydratedTooltipTuningState,
    selectedTooltipPresetName,
    tooltipTuning,
    tooltipTuningPresets,
  ]);

  useLayoutEffect(() => {
    if (!activeTooltipId) {
      setActiveTooltipLayout(null);
      return;
    }

    const updateTooltipLayout = () => {
      const target = tooltipTargetRefs.current.get(activeTooltipId);
      const bubble = tooltipBubbleRefs.current.get(activeTooltipId);

      if (!target || !bubble) {
        setActiveTooltipLayout(null);
        return;
      }

      const viewportPadding = 16;
      const boundaryPadding = 12;
      const gap = 14;
      const targetRect = target.getBoundingClientRect();
      const boundaryRect = getComparisonTooltipBoundaryRect(target);
      const minLeft = Math.max(
        viewportPadding,
        boundaryRect ? boundaryRect.left + boundaryPadding : viewportPadding,
      );
      const maxRight = Math.min(
        window.innerWidth - viewportPadding,
        boundaryRect ? boundaryRect.right - boundaryPadding : window.innerWidth - viewportPadding,
      );
      const availableWidth = Math.max(180, maxRight - minLeft);
      bubble.style.maxWidth = `${availableWidth}px`;
      const bubbleRect = bubble.getBoundingClientRect();
      const bubbleWidth = Math.min(bubbleRect.width, availableWidth);
      const preferredLeft = targetRect.left + targetRect.width / 2 - bubbleWidth / 2;
      const maxLeft = Math.max(minLeft, maxRight - bubbleWidth);
      const left = clampComparisonNumber(preferredLeft, minLeft, maxLeft);
      const spaceBelow = window.innerHeight - viewportPadding - (targetRect.bottom + gap);
      const spaceAbove = targetRect.top - viewportPadding - gap;
      const side =
        spaceBelow >= bubbleRect.height || spaceBelow >= spaceAbove ? "bottom" : "top";
      const top =
        side === "bottom"
          ? Math.min(targetRect.bottom + gap, window.innerHeight - viewportPadding - bubbleRect.height)
          : Math.max(viewportPadding, targetRect.top - gap - bubbleRect.height);
      const targetCenter = targetRect.left + targetRect.width / 2;
      const arrowLeft = clampComparisonNumber(targetCenter - left, 18, bubbleWidth - 18);

      setActiveTooltipLayout({
        arrowLeft,
        left,
        maxWidth: availableWidth,
        side,
        tooltipId: activeTooltipId,
        top,
      });
    };

    updateTooltipLayout();
    window.addEventListener("resize", updateTooltipLayout);
    window.addEventListener("scroll", updateTooltipLayout, true);
    return () => {
      window.removeEventListener("resize", updateTooltipLayout);
      window.removeEventListener("scroll", updateTooltipLayout, true);
    };
  }, [activeTooltipId]);

  useEffect(() => {
    if (!selectedScoreLink) {
      return;
    }

    const narrative = comparison.narratives.find(
      (candidate) => candidate.run_id === selectedScoreLink.narrativeRunId,
    );
    if (!narrative) {
      updateSelectedScoreLink(null);
      return;
    }

    const sectionBreakdown = narrative.score_breakdown[selectedScoreLink.section];
    if (!(selectedScoreLink.componentKey in sectionBreakdown.components)) {
      updateSelectedScoreLink(null);
    }
  }, [comparison, selectedScoreLink]);

  useEffect(() => {
    const tooltipKey = selectedScoreLink?.tooltipKey;
    if (!tooltipKey) {
      return;
    }
    const tooltipId = tooltipInteractionIdsRef.current.get(tooltipKey);
    if (!tooltipId || tooltipId === activeTooltipId) {
      return;
    }
    showComparisonTooltip(tooltipId);
  }, [activeTooltipId, selectedScoreLink?.tooltipKey]);

  useEffect(() => {
    if (!selectedScoreLink) {
      return;
    }
    const scrollOptions: ScrollIntoViewOptions = {
      behavior: "smooth",
      block: "nearest",
    };
    if (selectedScoreLink.source === "metric") {
      const metricCell = metricCellRefs.current.get(
        buildComparisonMetricCellRefKey(
          selectedScoreLink.originRunId ?? selectedScoreLink.narrativeRunId,
          selectedScoreLink.componentKey,
        ),
      );
      if (metricCell) {
        metricCell.scrollIntoView(scrollOptions);
        return;
      }
    }
    if (selectedScoreLink.source === "overview") {
      const overviewCard = overviewCardRefs.current.get(
        buildComparisonOverviewCardRefKey(
          selectedScoreLink.narrativeRunId,
          selectedScoreLink.section,
        ),
      );
      if (overviewCard) {
        overviewCard.scrollIntoView(scrollOptions);
        return;
      }
    }
    if (selectedScoreLink.source === "drillback") {
      const detailRow = scoreDetailRowRefs.current.get(
        buildComparisonScoreDetailRowRefKey(
          selectedScoreLink.narrativeRunId,
          selectedScoreLink.section,
          selectedScoreLink.componentKey,
        ),
      );
      if (detailRow) {
        detailRow.scrollIntoView(scrollOptions);
        return;
      }
    }
    if (selectedScoreLink.source === "provenance") {
      if (selectedScoreLink.artifactHoverKey) {
        const provenanceArtifactHover = provenanceArtifactHoverRefs.current.get(
          buildComparisonProvenanceArtifactHoverRefKey(
            selectedScoreLink.originRunId ?? selectedScoreLink.narrativeRunId,
            selectedScoreLink.artifactHoverKey,
          ),
        );
        if (provenanceArtifactHover) {
          provenanceArtifactHover.scrollIntoView(scrollOptions);
          return;
        }
      }
      if (selectedScoreLink.subFocusKey) {
        const provenanceSubFocus = provenanceSubFocusRefs.current.get(
          buildComparisonProvenanceSubFocusRefKey(
            selectedScoreLink.originRunId ?? selectedScoreLink.narrativeRunId,
            selectedScoreLink.subFocusKey,
          ),
        );
        if (provenanceSubFocus) {
          provenanceSubFocus.scrollIntoView(scrollOptions);
          return;
        }
      }
      const provenancePanel = provenancePanelRefs.current.get(
        selectedScoreLink.originRunId ?? selectedScoreLink.narrativeRunId,
      );
      if (provenancePanel) {
        provenancePanel.scrollIntoView(scrollOptions);
        return;
      }
    }
    if (selectedScoreLink.source === "run_card") {
      if (selectedScoreLink.subFocusKey) {
        const runCardSubFocus = runCardSubFocusRefs.current.get(
          buildComparisonRunCardSubFocusRefKey(
            selectedScoreLink.originRunId ?? selectedScoreLink.narrativeRunId,
            selectedScoreLink.subFocusKey,
          ),
        );
        if (runCardSubFocus) {
          runCardSubFocus.scrollIntoView(scrollOptions);
          return;
        }
      }
      const runCard = runCardRefs.current.get(
        selectedScoreLink.originRunId ?? selectedScoreLink.narrativeRunId,
      );
      if (runCard) {
        runCard.scrollIntoView(scrollOptions);
        return;
      }
    }
    const narrativeCard = narrativeCardRefs.current.get(selectedScoreLink.narrativeRunId);
    narrativeCard?.scrollIntoView(scrollOptions);
  }, [selectedScoreLink]);

  return (
    <section className={`comparison-panel ${intentClassName}`}>
      <div className="comparison-head">
        <div>
          <p className="kicker comparison-mode-kicker">
            <span aria-hidden="true" className="comparison-intent-icon" />
            <span>Comparison deck</span>
          </p>
          <h3>Native and reference backtests, side by side</h3>
        </div>
        <p className="comparison-baseline">
          <span>Baseline: {comparison.baseline_run_id}</span>
          <span
            className="comparison-intent-chip comparison-cue comparison-tooltip"
            ref={registerComparisonTooltipTargetRef(intentChipTooltipId)}
            tabIndex={0}
            {...getComparisonTooltipTargetProps(intentChipTooltipId)}
          >
            <span aria-hidden="true" className="comparison-intent-icon" />
            <span>{formatComparisonIntentLabel(comparison.intent)}</span>
            <ComparisonTooltipBubble
              id={intentChipTooltipId}
              layout={
                activeTooltipLayout?.tooltipId === intentChipTooltipId ? activeTooltipLayout : null
              }
              ref={registerComparisonTooltipBubbleRef(intentChipTooltipId)}
              text={intentTooltip}
            />
          </span>
        </p>
      </div>
      <div aria-label="Comparison legend" className="comparison-legend">
        <span
          className="comparison-legend-item comparison-legend-item-mode comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendModeTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendModeTooltipId)}
        >
          <span aria-hidden="true" className="comparison-intent-icon" />
          <span>{formatComparisonIntentLegend(comparison.intent)}</span>
          <ComparisonTooltipBubble
            id={legendModeTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendModeTooltipId ? activeTooltipLayout : null
            }
            ref={registerComparisonTooltipBubbleRef(legendModeTooltipId)}
            text={intentTooltip}
          />
        </span>
        <span
          className="comparison-legend-item comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendBaselineTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendBaselineTooltipId)}
        >
          <span aria-hidden="true" className="comparison-legend-swatch baseline" />
          <span>Baseline run</span>
          <ComparisonTooltipBubble
            id={legendBaselineTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendBaselineTooltipId
                ? activeTooltipLayout
                : null
            }
            ref={registerComparisonTooltipBubbleRef(legendBaselineTooltipId)}
            text={baselineTooltip}
          />
        </span>
        <span
          className="comparison-legend-item comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendBestTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendBestTooltipId)}
        >
          <span aria-hidden="true" className="comparison-legend-swatch best" />
          <span>Best metric</span>
          <ComparisonTooltipBubble
            id={legendBestTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendBestTooltipId ? activeTooltipLayout : null
            }
            ref={registerComparisonTooltipBubbleRef(legendBestTooltipId)}
            text={bestTooltip}
          />
        </span>
        <span
          className="comparison-legend-item comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendInsightTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendInsightTooltipId)}
        >
          <span aria-hidden="true" className="comparison-legend-swatch insight" />
          <span>Top insight</span>
          <ComparisonTooltipBubble
            id={legendInsightTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendInsightTooltipId ? activeTooltipLayout : null
            }
            ref={registerComparisonTooltipBubbleRef(legendInsightTooltipId)}
            text={insightTooltip}
          />
        </span>
      </div>
      {SHOW_COMPARISON_TOOLTIP_TUNING_PANEL ? (
        <ComparisonTooltipTuningPanel
          onChangePendingPresetImportName={updatePendingTooltipPresetImportName}
          onChangePresetDraftName={setTooltipPresetDraftName}
          onChangeShareDraft={updateTooltipShareDraft}
          onChangeValue={updateTooltipTuning}
          onCopyShareUrl={copyTooltipShareUrl}
          onCopySelectedPresetShareUrl={copySelectedTooltipPresetShareUrl}
          onDeletePreset={deleteTooltipPreset}
          onExportJson={exportTooltipPresetBundle}
          onExportSelectedPresetJson={exportSelectedTooltipPreset}
          onImportJson={importTooltipPresetBundle}
          onLoadPreset={loadTooltipPreset}
          onResolvePendingPresetImportConflict={resolvePendingTooltipPresetImportConflict}
          onReset={resetTooltipTuning}
          onSavePreset={saveTooltipPreset}
          onSetShareFeedback={setTooltipShareFeedback}
          pendingPresetImportConflict={pendingTooltipPresetImportConflict}
          presetDraftName={tooltipPresetDraftName}
          presets={tooltipTuningPresets}
          shareDraft={tooltipShareDraft}
          shareFeedback={tooltipShareFeedback}
          shareUrl={tooltipShareUrl}
          selectedPresetShareUrl={selectedTooltipPresetShareUrl}
          selectedPresetName={selectedTooltipPresetName}
          tuning={tooltipTuning}
        />
      ) : null}
      <div className="comparison-run-grid">
        {comparison.runs.map((run) => {
          const linkedRunRole = getComparisonScoreLinkedRunRole(
            selectedScoreLink,
            comparison.baseline_run_id,
            run.run_id,
          );
          const linkedSelection = linkedRunRole ? selectedScoreLink : null;
          const highlightStatus =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["status_bonus"], "context");
          const highlightStrategyKind =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["strategy_kind", "vocabulary"], "semantics");
          const highlightExecutionModel =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["execution_model", "vocabulary"], "semantics");
          const highlightParameterContract =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["parameter_contract", "vocabulary"], "semantics");
          const highlightSourceDescriptor =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, [
              "source_descriptor",
              "vocabulary",
              "native_reference_bonus",
              "reference_bonus",
              "reference_floor",
            ]);
          const highlightOperatorNotes =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["vocabulary"], "semantics");
          const highlightReferenceBadge =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, [
              "source_descriptor",
              "provenance_richness",
              "native_reference_bonus",
              "reference_bonus",
              "reference_floor",
              "benchmark_story_bonus",
            ]);
          const semanticKindSubFocusKey = buildComparisonRunCardLineSubFocusKey("strategy_kind");
          const executionModelSubFocusKey = buildComparisonRunCardLineSubFocusKey("execution_model");
          const parameterContractSubFocusKey = buildComparisonRunCardLineSubFocusKey("parameter_contract");
          const semanticSourceSubFocusKey = buildComparisonRunCardLineSubFocusKey("semantic_source");
          const operatorNotesSubFocusKey = buildComparisonRunCardLineSubFocusKey("operator_notes");
          const isRunCardSubFocusOrigin = (subFocusKey: string) =>
            linkedSelection?.source === "run_card"
            && linkedSelection.originRunId === run.run_id
            && linkedSelection.subFocusKey === subFocusKey;
          const baselineTooltipTargetRef =
            run.run_id === comparison.baseline_run_id
              ? registerComparisonTooltipTargetRef(baselineRunTooltipId)
              : undefined;
          const runCardRef = registerComparisonRunCardRef(run.run_id);

          return (
            <article
              className={`comparison-run-card ${
                run.run_id === comparison.baseline_run_id
                  ? "baseline comparison-cue-card comparison-tooltip"
                  : ""
              } ${linkedRunRole ? "is-linked" : ""} ${
                linkedRunRole === "target" ? "is-linked-target" : ""
              } ${linkedRunRole === "baseline" ? "is-linked-baseline" : ""}`.trim()}
              key={run.run_id}
              ref={(node) => {
                runCardRef(node);
                baselineTooltipTargetRef?.(node);
              }}
              tabIndex={run.run_id === comparison.baseline_run_id ? 0 : undefined}
              {...(run.run_id === comparison.baseline_run_id
                ? getComparisonTooltipTargetProps(baselineRunTooltipId)
                : {})}
            >
              <div className="comparison-run-head">
                <strong>{run.strategy_name ?? run.strategy_id}</strong>
                <div className={`run-status ${run.status} ${highlightStatus ? "comparison-linked-badge" : ""}`}>
                  {run.status}
                </div>
              </div>
              <div className="strategy-badges">
                <span className="meta-pill">{run.lane}</span>
                <span className="meta-pill subtle">{run.strategy_version}</span>
                {run.catalog_semantics.strategy_kind ? (
                  <button
                    aria-pressed={isRunCardSubFocusOrigin(semanticKindSubFocusKey)}
                    className={`meta-pill subtle comparison-run-card-pill-button ${
                      highlightStrategyKind ? "comparison-linked-badge" : ""
                    } ${
                      isRunCardSubFocusOrigin(semanticKindSubFocusKey)
                        ? "comparison-linked-badge-origin comparison-linked-subfocus"
                        : ""
                    }`.trim()}
                    onClick={() =>
                      handleComparisonScoreDrillBack(
                        run.run_id,
                        "semantics",
                        "strategy_kind",
                        "run_card",
                        {
                          subFocusKey: semanticKindSubFocusKey,
                        },
                      )
                    }
                    ref={registerComparisonRunCardSubFocusRef(run.run_id, semanticKindSubFocusKey)}
                    type="button"
                  >
                    {run.catalog_semantics.strategy_kind}
                  </button>
                ) : null}
                {run.reference_id ? (
                  <span
                    className={`meta-pill subtle ${highlightReferenceBadge ? "comparison-linked-badge" : ""}`}
                  >
                    {run.reference_id}
                  </span>
                ) : null}
              </div>
              <p className="run-note">
                {run.strategy_id} / {run.symbols.join(", ")} / {run.timeframe}
              </p>
              {run.catalog_semantics.execution_model ? (
                <button
                  aria-pressed={isRunCardSubFocusOrigin(executionModelSubFocusKey)}
                  className={`run-note comparison-run-card-link ${
                    highlightExecutionModel ? "comparison-linked-copy" : ""
                  } ${
                    isRunCardSubFocusOrigin(executionModelSubFocusKey)
                      ? "comparison-linked-copy-origin comparison-linked-subfocus"
                      : ""
                  }`.trim()}
                  onClick={() =>
                    handleComparisonScoreDrillBack(
                      run.run_id,
                      "semantics",
                      "execution_model",
                      "run_card",
                      {
                        subFocusKey: executionModelSubFocusKey,
                      },
                    )
                  }
                  ref={registerComparisonRunCardSubFocusRef(run.run_id, executionModelSubFocusKey)}
                  type="button"
                >
                  Execution model: {run.catalog_semantics.execution_model}
                </button>
              ) : null}
              {run.catalog_semantics.parameter_contract ? (
                <button
                  aria-pressed={isRunCardSubFocusOrigin(parameterContractSubFocusKey)}
                  className={`run-note comparison-run-card-link ${
                    highlightParameterContract ? "comparison-linked-copy" : ""
                  } ${
                    isRunCardSubFocusOrigin(parameterContractSubFocusKey)
                      ? "comparison-linked-copy-origin comparison-linked-subfocus"
                      : ""
                  }`.trim()}
                  onClick={() =>
                    handleComparisonScoreDrillBack(
                      run.run_id,
                      "semantics",
                      "parameter_contract",
                      "run_card",
                      {
                        subFocusKey: parameterContractSubFocusKey,
                      },
                    )
                  }
                  ref={registerComparisonRunCardSubFocusRef(run.run_id, parameterContractSubFocusKey)}
                  type="button"
                >
                  Parameter contract: {run.catalog_semantics.parameter_contract}
                </button>
              ) : null}
              {run.catalog_semantics.source_descriptor ? (
                <button
                  aria-pressed={isRunCardSubFocusOrigin(semanticSourceSubFocusKey)}
                  className={`run-note comparison-run-card-link ${
                    highlightSourceDescriptor ? "comparison-linked-copy" : ""
                  } ${
                    isRunCardSubFocusOrigin(semanticSourceSubFocusKey)
                      ? "comparison-linked-copy-origin comparison-linked-subfocus"
                      : ""
                  }`.trim()}
                  onClick={() =>
                    handleComparisonScoreDrillBack(
                      run.run_id,
                      "semantics",
                      "source_descriptor",
                      "run_card",
                      {
                        subFocusKey: semanticSourceSubFocusKey,
                      },
                    )
                  }
                  ref={registerComparisonRunCardSubFocusRef(run.run_id, semanticSourceSubFocusKey)}
                  type="button"
                >
                  Semantic source: {run.catalog_semantics.source_descriptor}
                </button>
              ) : null}
              {run.catalog_semantics.operator_notes.length ? (
                <button
                  aria-pressed={isRunCardSubFocusOrigin(operatorNotesSubFocusKey)}
                  className={`run-note comparison-run-card-link ${
                    highlightOperatorNotes ? "comparison-linked-copy" : ""
                  } ${
                    isRunCardSubFocusOrigin(operatorNotesSubFocusKey)
                      ? "comparison-linked-copy-origin comparison-linked-subfocus"
                      : ""
                  }`.trim()}
                  onClick={() =>
                    handleComparisonScoreDrillBack(
                      run.run_id,
                      "semantics",
                      "vocabulary",
                      "run_card",
                      {
                        subFocusKey: operatorNotesSubFocusKey,
                      },
                    )
                  }
                  ref={registerComparisonRunCardSubFocusRef(run.run_id, operatorNotesSubFocusKey)}
                  type="button"
                >
                  Operator notes: {run.catalog_semantics.operator_notes.join(" | ")}
                </button>
              ) : null}
              <ExperimentMetadataPills
                benchmarkFamily={run.experiment.benchmark_family}
                datasetIdentity={run.dataset_identity}
                presetId={run.experiment.preset_id}
                tags={run.experiment.tags}
              />
              <p className="run-note">
                Started {formatTimestamp(run.started_at)}
                {run.ended_at ? ` / Ended ${formatTimestamp(run.ended_at)}` : ""}
              </p>
              {run.reference ? (
                <ReferenceRunProvenanceSummary
                  artifactPaths={run.artifact_paths}
                  benchmarkArtifacts={run.benchmark_artifacts}
                  externalCommand={run.external_command}
                  linkedScore={
                    linkedSelection && linkedRunRole && linkedSelection.section !== "metrics"
                      ? {
                          ...linkedSelection,
                          role: linkedRunRole,
                        }
                      : null
                  }
                  onDrillBackScoreLink={(section, componentKey, options) =>
                    handleComparisonScoreDrillBack(
                      run.run_id,
                      section,
                      componentKey,
                      "provenance",
                      options,
                    )
                  }
                  registerArtifactHoverRef={registerComparisonProvenanceArtifactHoverRef}
                  panelRef={registerComparisonProvenancePanelRef(run.run_id)}
                  panelRunId={run.run_id}
                  registerSubFocusRef={registerComparisonProvenanceSubFocusRef}
                  reference={run.reference}
                  referenceVersion={run.reference_version}
                  strategySemantics={run.catalog_semantics}
                  workingDirectory={run.working_directory}
                />
              ) : null}
              {run.run_id === comparison.baseline_run_id ? (
                <ComparisonTooltipBubble
                  id={baselineRunTooltipId}
                  layout={
                    activeTooltipLayout?.tooltipId === baselineRunTooltipId
                      ? activeTooltipLayout
                      : null
                  }
                  ref={registerComparisonTooltipBubbleRef(baselineRunTooltipId)}
                  text={baselineTooltip}
                />
              ) : null}
            </article>
          );
        })}
      </div>
      {primaryNarrative ? (
        <div className="comparison-top-story">
          <p
            className="kicker comparison-top-kicker comparison-cue comparison-tooltip"
            ref={registerComparisonTooltipTargetRef(topInsightTooltipId)}
            tabIndex={0}
            {...getComparisonTooltipTargetProps(topInsightTooltipId)}
          >
            <span aria-hidden="true" className="comparison-legend-swatch insight" />
            <span>Top insight / {formatComparisonIntentLabel(comparison.intent)}</span>
            <ComparisonTooltipBubble
              id={topInsightTooltipId}
              layout={
                activeTooltipLayout?.tooltipId === topInsightTooltipId ? activeTooltipLayout : null
              }
              ref={registerComparisonTooltipBubbleRef(topInsightTooltipId)}
              text={insightTooltip}
            />
          </p>
          <ComparisonNarrativeCard
            activeTooltipLayout={activeTooltipLayout}
            comparison={comparison}
            expandedScoreDetails={expandedNarrativeScoreBreakdowns[primaryNarrative.run_id] ?? false}
            featured
            narrative={primaryNarrative}
            onChangeExpandedScoreDetails={handleComparisonNarrativeScoreBreakdownExpandedChange}
            onSelectScoreLink={updateSelectedScoreLink}
            registerCardRef={registerComparisonNarrativeCardRef}
            registerOverviewCardRef={registerComparisonOverviewCardRef}
            registerScoreDetailRowRef={registerComparisonScoreDetailRowRef}
            registerTooltipBubbleRef={registerComparisonTooltipBubbleRef}
            registerTooltipTargetRef={registerComparisonTooltipTargetRef}
            selectedScoreLink={selectedScoreLink}
            tooltipId={featuredNarrativeTooltipId}
            tooltipTargetProps={
              featuredNarrativeTooltipId
                ? getComparisonTooltipTargetProps(featuredNarrativeTooltipId)
                : undefined
            }
            tooltip={insightTooltip}
          />
        </div>
      ) : null}
      {secondaryNarratives.length ? (
        <div className="comparison-story-grid">
          {secondaryNarratives.map((narrative) => (
            <ComparisonNarrativeCard
              activeTooltipLayout={activeTooltipLayout}
              comparison={comparison}
              expandedScoreDetails={expandedNarrativeScoreBreakdowns[narrative.run_id] ?? false}
              key={`${narrative.baseline_run_id}-${narrative.run_id}`}
              narrative={narrative}
              onChangeExpandedScoreDetails={handleComparisonNarrativeScoreBreakdownExpandedChange}
              onSelectScoreLink={updateSelectedScoreLink}
              registerCardRef={registerComparisonNarrativeCardRef}
              registerOverviewCardRef={registerComparisonOverviewCardRef}
              registerScoreDetailRowRef={registerComparisonScoreDetailRowRef}
              registerTooltipBubbleRef={registerComparisonTooltipBubbleRef}
              registerTooltipTargetRef={registerComparisonTooltipTargetRef}
              selectedScoreLink={selectedScoreLink}
            />
          ))}
        </div>
      ) : null}
      <div className="comparison-table-wrap">
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Metric</th>
              {comparison.runs.map((run) => (
                <th key={run.run_id}>{run.strategy_name ?? run.strategy_id}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparison.metric_rows.map((metricRow) => {
              const metricRowLinked = isComparisonScoreLinkMatch(
                selectedScoreLink,
                [metricRow.key],
                "metrics",
              );

              return (
                <tr className={metricRowLinked ? "comparison-linked-metric-row" : undefined} key={metricRow.key}>
                  <th className={metricRowLinked ? "comparison-linked-metric-label" : undefined}>
                    <span>{metricRow.label}</span>
                    {metricRow.annotation ? (
                      <small className="comparison-metric-annotation">{metricRow.annotation}</small>
                    ) : null}
                  </th>
                  {comparison.runs.map((run) => {
                    const metricDrillBackTarget = resolveComparisonScoreDrillBackTarget(
                      comparison,
                      selectedScoreLink,
                      run.run_id,
                      "metrics",
                      metricRow.key,
                    );
                    const cellTooltip =
                      buildComparisonCellTooltip(
                        comparison.intent,
                        metricRow.label,
                        run.run_id === comparison.baseline_run_id,
                        metricRow.best_run_id === run.run_id,
                      ) || undefined;
                    const metricTooltipKey =
                      cellTooltip ? buildComparisonMetricTooltipKey(metricRow.key, run.run_id) : null;
                    const cellTooltipId = cellTooltip
                      ? buildComparisonTooltipId(tooltipScopeId, "metric", metricRow.key, run.run_id)
                      : undefined;
                    const metricTooltipTargetProps = cellTooltipId
                      ? getMetricComparisonTooltipTargetProps(
                          cellTooltipId,
                          metricRow.key,
                          run.run_id,
                        )
                      : undefined;
                    const linkedRunRole = metricRowLinked
                      ? getComparisonScoreLinkedRunRole(
                          selectedScoreLink,
                          comparison.baseline_run_id,
                          run.run_id,
                        )
                      : null;
                    const metricCellPressed =
                      Boolean(metricDrillBackTarget)
                      && selectedScoreLink?.narrativeRunId === metricDrillBackTarget?.narrativeRunId
                      && selectedScoreLink?.section === "metrics"
                      && selectedScoreLink?.componentKey === metricRow.key;
                    const metricCellIsOrigin =
                      metricCellPressed
                      && selectedScoreLink?.source === "metric"
                      && selectedScoreLink?.originRunId === run.run_id;
                    const cellClassName =
                      [
                        metricRow.best_run_id === run.run_id ? "comparison-best" : "",
                        run.run_id === comparison.baseline_run_id ? "comparison-baseline-cell" : "",
                        cellTooltip ? "comparison-cue comparison-tooltip comparison-cell-cue" : "",
                        metricDrillBackTarget ? "comparison-drillback-target" : "",
                        metricRowLinked ? "comparison-linked-metric-cell" : "",
                        linkedRunRole === "target" ? "comparison-linked-metric-cell-target" : "",
                        linkedRunRole === "baseline" ? "comparison-linked-metric-cell-baseline" : "",
                        metricCellIsOrigin ? "comparison-linked-metric-cell-origin" : "",
                      ]
                        .filter(Boolean)
                        .join(" ") || undefined;
                    const setMetricCellRef = (node: HTMLTableCellElement | null) => {
                      registerComparisonMetricCellRef(run.run_id, metricRow.key)(node);
                      if (cellTooltipId) {
                        registerComparisonTooltipTargetRef(cellTooltipId, metricTooltipKey ?? undefined)(node);
                      }
                    };

                    return (
                      <td
                        {...(metricTooltipTargetProps ?? {})}
                        aria-label={
                          metricDrillBackTarget
                            ? `Trace ${metricRow.label} score component for ${run.strategy_name ?? run.strategy_id}`
                            : undefined
                        }
                        aria-pressed={metricDrillBackTarget ? metricCellPressed : undefined}
                        className={cellClassName}
                        key={`${metricRow.key}-${run.run_id}`}
                        onClick={
                          metricDrillBackTarget
                            ? () =>
                                handleComparisonScoreDrillBack(
                                  run.run_id,
                                  "metrics",
                                  metricRow.key,
                                  "metric",
                                  metricTooltipKey ? { tooltipKey: metricTooltipKey } : undefined,
                                )
                            : undefined
                        }
                        onKeyDown={(event) => {
                          metricTooltipTargetProps?.onKeyDown?.(event);
                          if (
                            event.defaultPrevented
                            || !metricDrillBackTarget
                            || (event.key !== "Enter" && event.key !== " ")
                          ) {
                            return;
                          }
                          event.preventDefault();
                          handleComparisonScoreDrillBack(
                            run.run_id,
                            "metrics",
                            metricRow.key,
                            "metric",
                            metricTooltipKey ? { tooltipKey: metricTooltipKey } : undefined,
                          );
                        }}
                        ref={setMetricCellRef}
                        role={metricDrillBackTarget ? "button" : undefined}
                        tabIndex={metricDrillBackTarget || cellTooltip ? 0 : undefined}
                      >
                        <strong>
                          {formatComparisonMetric(metricRow.values[run.run_id], metricRow.unit)}
                        </strong>
                        <span className="comparison-delta">
                          {run.run_id === comparison.baseline_run_id
                            ? metricRow.delta_annotations[run.run_id] ?? "baseline"
                            : metricRow.delta_annotations[run.run_id] ?? formatComparisonDelta(
                                metricRow.deltas_vs_baseline[run.run_id],
                                metricRow.unit,
                              )}
                        </span>
                        {cellTooltipId && cellTooltip ? (
                          <ComparisonTooltipBubble
                            id={cellTooltipId}
                            layout={
                              activeTooltipLayout?.tooltipId === cellTooltipId
                                ? activeTooltipLayout
                                : null
                            }
                            ref={registerComparisonTooltipBubbleRef(cellTooltipId)}
                            text={cellTooltip}
                          />
                        ) : null}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
            <tr>
              <th>Notes</th>
              {comparison.runs.map((run) => (
                <td key={`notes-${run.run_id}`}>
                  <p className="comparison-note-copy">{summarizeRunNotes(run.notes)}</p>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ComparisonNarrativeCard({
  activeTooltipLayout,
  comparison,
  expandedScoreDetails,
  narrative,
  onChangeExpandedScoreDetails,
  featured = false,
  onSelectScoreLink,
  registerCardRef,
  registerOverviewCardRef,
  registerScoreDetailRowRef,
  registerTooltipBubbleRef,
  registerTooltipTargetRef,
  selectedScoreLink,
  tooltipId,
  tooltipTargetProps,
  tooltip,
}: {
  activeTooltipLayout: ComparisonTooltipLayout | null;
  comparison: RunComparison;
  expandedScoreDetails: boolean;
  narrative: RunComparison["narratives"][number];
  onChangeExpandedScoreDetails: (narrativeRunId: string, expanded: boolean) => void;
  featured?: boolean;
  onSelectScoreLink: (
    value: ComparisonScoreLinkTarget | null,
    historyMode?: ComparisonHistoryWriteMode,
  ) => void;
  registerCardRef: (runId: string) => (node: HTMLElement | null) => void;
  registerOverviewCardRef: (
    narrativeRunId: string,
    section: ComparisonScoreSection,
  ) => (node: HTMLButtonElement | null) => void;
  registerScoreDetailRowRef: (
    narrativeRunId: string,
    section: ComparisonScoreSection,
    componentKey: string,
  ) => (node: HTMLButtonElement | null) => void;
  registerTooltipBubbleRef: (tooltipId: string) => (node: HTMLSpanElement | null) => void;
  registerTooltipTargetRef: (tooltipId?: string) => (node: HTMLElement | null) => void;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
  tooltipId?: string;
  tooltipTargetProps?: ComparisonTooltipTargetProps;
  tooltip?: string;
}) {
  const run = comparison.runs.find((candidate) => candidate.run_id === narrative.run_id);
  const runLabel = run?.reference?.title ?? run?.strategy_name ?? run?.strategy_id ?? narrative.run_id;
  const setCardRef = (node: HTMLElement | null) => {
    registerCardRef(narrative.run_id)(node);
    if (tooltipId) {
      registerTooltipTargetRef(tooltipId)(node);
    }
  };

  return (
    <article
      className={`comparison-story-card ${
        featured ? "featured comparison-cue-card comparison-tooltip" : ""
      } ${selectedScoreLink?.narrativeRunId === narrative.run_id ? "is-linked" : ""}`.trim()}
      ref={setCardRef}
      tabIndex={tooltip ? 0 : undefined}
      {...tooltipTargetProps}
    >
      <div className="comparison-story-head">
        <span>{formatComparisonNarrativeLabel(narrative.comparison_type)}</span>
        <strong>{runLabel}</strong>
      </div>
      <div className="comparison-story-meta">
        <span>#{narrative.rank}</span>
        <span>Score {formatComparisonScoreValue(narrative.insight_score)}</span>
      </div>
      <ComparisonNarrativeScoreBreakdown
        breakdown={narrative.score_breakdown}
        expanded={expandedScoreDetails}
        narrativeRunId={narrative.run_id}
        onChangeExpanded={onChangeExpandedScoreDetails}
        onSelectScoreLink={onSelectScoreLink}
        registerOverviewCardRef={registerOverviewCardRef}
        registerScoreDetailRowRef={registerScoreDetailRowRef}
        selectedScoreLink={selectedScoreLink}
      />
      <p className="comparison-story-title">{narrative.title}</p>
      <p className="comparison-story-summary">{narrative.summary}</p>
      {narrative.bullets.length ? (
        <ul className="comparison-story-list">
          {narrative.bullets.map((bullet) => (
            <li key={`${narrative.run_id}-${bullet}`}>{bullet}</li>
          ))}
        </ul>
      ) : null}
      {tooltipId && tooltip ? (
        <ComparisonTooltipBubble
          id={tooltipId}
          layout={activeTooltipLayout?.tooltipId === tooltipId ? activeTooltipLayout : null}
          ref={registerTooltipBubbleRef(tooltipId)}
          text={tooltip}
        />
      ) : null}
    </article>
  );
}

function ComparisonNarrativeScoreBreakdown({
  breakdown,
  expanded,
  narrativeRunId,
  onChangeExpanded,
  onSelectScoreLink,
  registerOverviewCardRef,
  registerScoreDetailRowRef,
  selectedScoreLink,
}: {
  breakdown: RunComparison["narratives"][number]["score_breakdown"];
  expanded: boolean;
  narrativeRunId: string;
  onChangeExpanded: (narrativeRunId: string, expanded: boolean) => void;
  onSelectScoreLink: (
    value: ComparisonScoreLinkTarget | null,
    historyMode?: ComparisonHistoryWriteMode,
  ) => void;
  registerOverviewCardRef: (
    narrativeRunId: string,
    section: ComparisonScoreSection,
  ) => (node: HTMLButtonElement | null) => void;
  registerScoreDetailRowRef: (
    narrativeRunId: string,
    section: ComparisonScoreSection,
    componentKey: string,
  ) => (node: HTMLButtonElement | null) => void;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
}) {
  const sections: Array<{
    key: ComparisonScoreSection;
    label: string;
    total: number;
    highlights: string[];
    components: Record<string, { score: number; [key: string]: unknown }>;
    detailRows: ReturnType<typeof buildComparisonScoreDetailRows>;
  }> = [
    {
      key: "metrics",
      label: "Metrics",
      total: breakdown.metrics.total,
      highlights: buildComparisonScoreHighlights("metrics", breakdown.metrics.components),
      components: breakdown.metrics.components,
      detailRows: buildComparisonScoreDetailRows("metrics", breakdown.metrics.components),
    },
    {
      key: "semantics",
      label: "Semantics",
      total: breakdown.semantics.total,
      highlights: buildComparisonScoreHighlights("semantics", breakdown.semantics.components),
      components: breakdown.semantics.components,
      detailRows: buildComparisonScoreDetailRows("semantics", breakdown.semantics.components),
    },
    {
      key: "context",
      label: "Context",
      total: breakdown.context.total,
      highlights: buildComparisonScoreHighlights("context", breakdown.context.components),
      components: breakdown.context.components,
      detailRows: buildComparisonScoreDetailRows("context", breakdown.context.components),
    },
  ];
  const activeSelection =
    selectedScoreLink?.narrativeRunId === narrativeRunId ? selectedScoreLink : null;
  const activeSelectionLabel = activeSelection
    ? formatComparisonScoreComponentLabel(activeSelection.section, activeSelection.componentKey)
    : null;
  const activeSelectionSource = activeSelection
    ? formatComparisonScoreLinkSourceLabel(activeSelection.source)
    : null;

  useEffect(() => {
    if (activeSelection) {
      onChangeExpanded(
        narrativeRunId,
        activeSelection.detailExpanded ?? (activeSelection.source === "drillback"),
      );
    }
  }, [activeSelection, narrativeRunId, onChangeExpanded]);

  return (
    <section className="comparison-score-breakdown" aria-label="Narrative score breakdown">
      <div className="comparison-score-breakdown-head">
        <span>Score breakdown</span>
        <strong>{formatComparisonScoreValue(breakdown.total)}</strong>
      </div>
      <div className="comparison-score-breakdown-grid">
        {sections.map((section) => {
          const overviewTarget = section.detailRows[0] ?? null;
          const sectionIsLinked = activeSelection?.section === section.key;
          const sectionIsOrigin = sectionIsLinked && activeSelection?.source === "overview";
          return (
            <button
              aria-pressed={sectionIsOrigin}
              className={`comparison-score-breakdown-card ${
                overviewTarget ? "is-interactive" : ""
              } ${sectionIsLinked ? "is-linked" : ""} ${sectionIsOrigin ? "is-origin" : ""}`.trim()}
              disabled={!overviewTarget}
              key={section.key}
              onClick={() =>
                overviewTarget
                  ? onSelectScoreLink(
                      sectionIsOrigin
                        ? null
                        : {
                            componentKey: overviewTarget.key,
                            detailExpanded: expanded,
                            artifactDetailExpanded: null,
                            artifactLineDetailExpanded: null,
                            artifactLineDetailView: null,
                            artifactLineMicroView: null,
                            artifactLineNotePage: null,
                            artifactLineDetailHoverKey: null,
                            artifactLineDetailScrubStep: null,
                            narrativeRunId,
                            originRunId: null,
                            section: section.key,
                            source: "overview",
                            subFocusKey: null,
                            tooltipKey: null,
                            artifactHoverKey: null,
                          },
                    )
                  : undefined
              }
              ref={registerOverviewCardRef(narrativeRunId, section.key)}
              type="button"
            >
              <div className="comparison-score-breakdown-card-head">
                <span>{section.label}</span>
                <strong>{formatComparisonScoreValue(section.total)}</strong>
              </div>
              <p className="comparison-score-breakdown-copy">
                {section.highlights.length ? section.highlights.join(" / ") : "No active contribution"}
              </p>
              {overviewTarget ? (
                <span className="comparison-score-breakdown-hint">
                  {sectionIsOrigin
                    ? `Overview focus on ${overviewTarget.label}`
                    : `Focus ${overviewTarget.label}`}
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
      {activeSelectionLabel ? (
        <p className="comparison-score-link-copy">
          Tracing {activeSelectionLabel} from {activeSelectionSource} into the run deck, metric table, and provenance panels.
        </p>
      ) : null}
      <button
        aria-expanded={expanded}
        className="comparison-score-breakdown-toggle"
        onClick={() => {
          const nextExpanded = !expanded;
          onChangeExpanded(narrativeRunId, nextExpanded);
          if (activeSelection) {
            onSelectScoreLink(
              {
                ...activeSelection,
                detailExpanded: nextExpanded,
              },
              "replace",
            );
          }
        }}
        type="button"
      >
        {expanded ? "Hide score details" : "Show score details"}
      </button>
      {expanded ? (
        <div className="comparison-score-detail-grid">
          {sections.map((section) => (
            <article className="comparison-score-detail-card" key={section.key}>
              <div className="comparison-score-detail-card-head">
                <span>{section.label}</span>
                <strong>{formatComparisonScoreValue(section.total)}</strong>
              </div>
              <div className="comparison-score-detail-list">
                {section.detailRows.map((row) => {
                  const rowIsLinked =
                    activeSelection?.section === section.key
                    && activeSelection.componentKey === row.key;
                  const rowIsOrigin = rowIsLinked && activeSelection?.source === "drillback";
                  return (
                    <button
                      aria-pressed={rowIsLinked}
                      className={`comparison-score-detail-row ${row.score > 0 ? "is-active" : ""} ${
                        rowIsLinked ? "is-linked" : ""
                      } ${rowIsOrigin ? "is-origin" : ""}`}
                      key={`${section.key}-${row.key}`}
                      ref={registerScoreDetailRowRef(narrativeRunId, section.key, row.key)}
                      onClick={() =>
                        onSelectScoreLink(
                          rowIsOrigin
                            ? null
                            : {
                                componentKey: row.key,
                                detailExpanded: true,
                                artifactDetailExpanded: null,
                                artifactLineDetailExpanded: null,
                                artifactLineDetailView: null,
                                artifactLineMicroView: null,
                                artifactLineNotePage: null,
                                artifactLineDetailHoverKey: null,
                                artifactLineDetailScrubStep: null,
                                narrativeRunId,
                                originRunId: null,
                                section: section.key,
                                source: "drillback",
                                subFocusKey: null,
                                tooltipKey: null,
                                artifactHoverKey: null,
                              },
                          "push",
                        )
                      }
                      type="button"
                    >
                      <div className="comparison-score-detail-row-head">
                        <span>{row.label}</span>
                        <strong>{formatComparisonScoreValue(row.score)}</strong>
                      </div>
                      <p className="comparison-score-detail-row-copy">
                        {row.details.length ? row.details.join(" / ") : "No active contribution"}
                      </p>
                    </button>
                  );
                })}
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}

export const ComparisonTooltipBubble = forwardRef<
  HTMLSpanElement,
  { id: string; layout: ComparisonTooltipLayout | null; text: string }
>(function ComparisonTooltipBubble({ id, layout, text }, ref) {
  const style: CSSProperties & { "--comparison-tooltip-arrow-left"?: string } = {
    left: layout?.left ?? 0,
    maxWidth: layout ? `${layout.maxWidth}px` : undefined,
    top: layout?.top ?? 0,
    "--comparison-tooltip-arrow-left": layout ? `${layout.arrowLeft}px` : undefined,
  };

  return (
    <span
      className="comparison-tooltip-bubble"
      data-tooltip-side={layout?.side ?? "bottom"}
      id={id}
      ref={ref}
      role="tooltip"
      style={style}
    >
      {text}
    </span>
  );
});

export function ComparisonTooltipTuningPanel({
  pendingPresetImportConflict,
  presetDraftName,
  presets,
  shareDraft,
  shareFeedback,
  shareUrl,
  selectedPresetShareUrl,
  selectedPresetName,
  onChangePendingPresetImportName,
  onChangePresetDraftName,
  onChangeShareDraft,
  tuning,
  onChangeValue,
  onCopyShareUrl,
  onCopySelectedPresetShareUrl,
  onDeletePreset,
  onExportJson,
  onExportSelectedPresetJson,
  onImportJson,
  onLoadPreset,
  onResolvePendingPresetImportConflict,
  onReset,
  onSavePreset,
  onSetShareFeedback,
}: {
  pendingPresetImportConflict: ComparisonTooltipPendingPresetImportConflict | null;
  presetDraftName: string;
  presets: Record<string, ComparisonTooltipTuning>;
  shareDraft: string;
  shareFeedback: string | null;
  shareUrl: string;
  selectedPresetShareUrl: string;
  selectedPresetName: string;
  onChangePendingPresetImportName: (value: string) => void;
  onChangePresetDraftName: (value: string) => void;
  onChangeShareDraft: (value: string) => void;
  tuning: ComparisonTooltipTuning;
  onChangeValue: (key: keyof ComparisonTooltipTuning, value: string) => void;
  onCopyShareUrl: () => void;
  onCopySelectedPresetShareUrl: () => void;
  onDeletePreset: () => void;
  onExportJson: () => void;
  onExportSelectedPresetJson: () => void;
  onImportJson: () => void;
  onLoadPreset: (name: string) => void;
  onResolvePendingPresetImportConflict: (action: "overwrite" | "rename" | "skip") => void;
  onReset: () => void;
  onSavePreset: () => void;
  onSetShareFeedback: (value: string | null) => void;
}) {
  const [conflictSessionUiStateMap, setConflictSessionUiStateMap] = useState<
    Record<string, ComparisonTooltipConflictSessionUiState>
  >({});
  const [isConfirmingResetAllConflictViews, setIsConfirmingResetAllConflictViews] =
    useState(false);
  const [showAllSavedConflictSessionSummaries, setShowAllSavedConflictSessionSummaries] =
    useState(false);
  const [expandedSavedConflictSessionSummaryGroups, setExpandedSavedConflictSessionSummaryGroups] =
    useState<Record<string, boolean>>({});
  const [savedConflictSessionSummaryNowMs, setSavedConflictSessionSummaryNowMs] = useState(() =>
    Date.now(),
  );
  const presetNames = Object.keys(presets).sort((left, right) => left.localeCompare(right));
  const conflictExistingPreset = pendingPresetImportConflict
    ? presets[pendingPresetImportConflict.imported_preset_name] ?? null
    : null;
  const conflictSessionKey = pendingPresetImportConflict
    ? buildComparisonTooltipConflictSessionKey(pendingPresetImportConflict)
    : null;
  const conflictPreviewRows =
    pendingPresetImportConflict && conflictExistingPreset
      ? buildComparisonTooltipPresetConflictPreviewRows(
          conflictExistingPreset,
          pendingPresetImportConflict.tuning,
        )
      : [];
  const changedConflictPreviewRows = conflictPreviewRows.filter((row) => row.changed);
  const unchangedConflictPreviewRows = conflictPreviewRows.filter((row) => !row.changed);
  const changedConflictPreviewGroups = groupComparisonTooltipPresetConflictPreviewRows(
    changedConflictPreviewRows,
  );
  const unchangedConflictPreviewGroups = groupComparisonTooltipPresetConflictPreviewRows(
    unchangedConflictPreviewRows,
  );
  const changedConflictPreviewCount = changedConflictPreviewRows.length;
  const unchangedConflictPreviewCount = unchangedConflictPreviewRows.length;
  const currentConflictSessionUiState = conflictSessionKey
    ? conflictSessionUiStateMap[conflictSessionKey] ?? null
    : null;
  const savedConflictSessionCount = Object.keys(conflictSessionUiStateMap).length;
  const savedConflictSessionSummaries = buildComparisonTooltipConflictSessionSummaries(
    conflictSessionUiStateMap,
    conflictSessionKey,
    savedConflictSessionSummaryNowMs,
  );
  const savedConflictSessionSummaryUpdatedAtTimestamps = Object.values(
    conflictSessionUiStateMap,
  ).reduce<number[]>((timestamps, session) => {
    const timestamp = parseComparisonTooltipConflictSessionUpdatedAt(session.updated_at);
    if (timestamp) {
      timestamps.push(timestamp);
    }
    return timestamps;
  }, []);
  const visibleSavedConflictSessionSummaries = savedConflictSessionSummaries.slice(
    0,
    MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES,
  );
  const hiddenSavedConflictSessionSummaryCount = Math.max(
    0,
    savedConflictSessionSummaries.length - visibleSavedConflictSessionSummaries.length,
  );
  const displayedSavedConflictSessionSummaries = showAllSavedConflictSessionSummaries
    ? savedConflictSessionSummaries
    : visibleSavedConflictSessionSummaries;
  const savedConflictSessionSummaryRefreshMs =
    getComparisonTooltipConflictSessionRelativeTimeRefreshMs(
      savedConflictSessionSummaryUpdatedAtTimestamps,
      savedConflictSessionSummaryNowMs,
    );
  const showUnchangedConflictRows =
    currentConflictSessionUiState?.show_unchanged_conflict_rows ?? false;
  const collapsedUnchangedConflictGroups =
    currentConflictSessionUiState?.collapsed_unchanged_groups ?? {};

  useEffect(() => {
    setConflictSessionUiStateMap(loadComparisonTooltipConflictUiState().sessions);
  }, []);

  useEffect(() => {
    persistComparisonTooltipConflictUiState({
      sessions: conflictSessionUiStateMap,
      version: COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION,
    });
  }, [conflictSessionUiStateMap]);

  useEffect(() => {
    if (!savedConflictSessionCount && isConfirmingResetAllConflictViews) {
      setIsConfirmingResetAllConflictViews(false);
    }
  }, [isConfirmingResetAllConflictViews, savedConflictSessionCount]);

  useEffect(() => {
    if (!isConfirmingResetAllConflictViews || !hiddenSavedConflictSessionSummaryCount) {
      setShowAllSavedConflictSessionSummaries(false);
    }
  }, [hiddenSavedConflictSessionSummaryCount, isConfirmingResetAllConflictViews]);

  useEffect(() => {
    if (!isConfirmingResetAllConflictViews) {
      setExpandedSavedConflictSessionSummaryGroups({});
    }
  }, [isConfirmingResetAllConflictViews]);

  useEffect(() => {
    if (!isConfirmingResetAllConflictViews || !savedConflictSessionSummaryRefreshMs) {
      return;
    }
    const timeoutId = window.setTimeout(
      () => setSavedConflictSessionSummaryNowMs(Date.now()),
      savedConflictSessionSummaryRefreshMs,
    );
    return () => window.clearTimeout(timeoutId);
  }, [isConfirmingResetAllConflictViews, savedConflictSessionSummaryRefreshMs]);

  const updateCurrentConflictSessionUiState = (
    updater: (
      current: ComparisonTooltipConflictSessionUiState,
    ) => ComparisonTooltipConflictSessionUiState,
  ) => {
    if (!conflictSessionKey) {
      return;
    }
    setConflictSessionUiStateMap((current) => {
      const nextCurrent = current[conflictSessionKey] ?? {
        collapsed_unchanged_groups: {},
        show_unchanged_conflict_rows: false,
        updated_at: null,
      };
      const nextSession = updater(nextCurrent);
      return {
        ...current,
        [conflictSessionKey]: {
          ...nextSession,
          updated_at: new Date().toISOString(),
        },
      };
    });
  };

  const ensureUnchangedConflictGroupCollapseState = () => {
    updateCurrentConflictSessionUiState((current) => ({
      ...current,
      collapsed_unchanged_groups: seedComparisonTooltipUnchangedConflictGroupCollapseState(
        unchangedConflictPreviewGroups,
        current.collapsed_unchanged_groups,
      ),
    }));
  };

  const toggleShowUnchangedConflictRows = () => {
    if (!showUnchangedConflictRows) {
      ensureUnchangedConflictGroupCollapseState();
    }
    updateCurrentConflictSessionUiState((current) => ({
      ...current,
      show_unchanged_conflict_rows: !current.show_unchanged_conflict_rows,
    }));
  };

  const isUnchangedConflictGroupCollapsed = (
    group: ComparisonTooltipPresetConflictPreviewGroup,
  ) =>
    collapsedUnchangedConflictGroups[group.key] ??
    group.rows.length >= COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD;

  const toggleUnchangedConflictGroupCollapse = (
    group: ComparisonTooltipPresetConflictPreviewGroup,
  ) => {
    updateCurrentConflictSessionUiState((current) => ({
      ...current,
      collapsed_unchanged_groups: {
        ...current.collapsed_unchanged_groups,
        [group.key]:
          !(current.collapsed_unchanged_groups[group.key] ??
            group.rows.length >= COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD),
      },
    }));
  };

  const resetCurrentConflictSessionUiState = () => {
    if (!conflictSessionKey || !currentConflictSessionUiState) {
      onSetShareFeedback("No saved view state exists for the current conflict session.");
      return;
    }
    setConflictSessionUiStateMap((current) => {
      const next = { ...current };
      delete next[conflictSessionKey];
      return next;
    });
    onSetShareFeedback("Reset saved view state for the current conflict session.");
  };

  const requestResetAllConflictSessionUiState = () => {
    if (!savedConflictSessionCount) {
      onSetShareFeedback("No saved conflict-view state exists to reset.");
      return;
    }
    setIsConfirmingResetAllConflictViews(true);
    setShowAllSavedConflictSessionSummaries(false);
    setExpandedSavedConflictSessionSummaryGroups({});
    setSavedConflictSessionSummaryNowMs(Date.now());
    onSetShareFeedback(null);
  };

  const cancelResetAllConflictSessionUiState = () => {
    setIsConfirmingResetAllConflictViews(false);
    onSetShareFeedback("Canceled clearing saved conflict-view state.");
  };

  const resetAllConflictSessionUiState = () => {
    if (!savedConflictSessionCount) {
      onSetShareFeedback("No saved conflict-view state exists to reset.");
      return;
    }
    setConflictSessionUiStateMap({});
    setIsConfirmingResetAllConflictViews(false);
    onSetShareFeedback("Reset all saved conflict-view state.");
  };

  return (
    <details className="comparison-dev-panel">
      <summary className="comparison-dev-summary">
        Dev only: tooltip sweep tuning
      </summary>
      <p className="comparison-dev-copy">
        Tune sweep detection and suppression live while scanning dense comparison cells.
      </p>
      <div className="comparison-dev-preset-bar">
        <label className="comparison-dev-field">
          <span>Preset</span>
          <select
            onChange={(event) => onLoadPreset(event.target.value)}
            value={selectedPresetName}
          >
            <option value="">Draft only</option>
            {presetNames.map((presetName) => (
              <option key={presetName} value={presetName}>
                {presetName}
              </option>
            ))}
          </select>
        </label>
        <label className="comparison-dev-field">
          <span>Preset name</span>
          <input
            onChange={(event) => onChangePresetDraftName(event.target.value)}
            placeholder="session-a"
            type="text"
            value={presetDraftName}
          />
        </label>
        <div className="comparison-dev-actions comparison-dev-actions-inline">
          <button className="ghost-button comparison-dev-reset" onClick={onSavePreset} type="button">
            Save preset
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            disabled={!selectedPresetName}
            onClick={onDeletePreset}
            type="button"
          >
            Delete preset
          </button>
        </div>
      </div>
      <div className="comparison-dev-share-block">
        <label className="comparison-dev-field comparison-dev-share-url-field">
          <span>Bundle share URL</span>
          <input
            onFocus={(event) => event.currentTarget.select()}
            readOnly
            type="text"
            value={shareUrl}
          />
        </label>
        <label className="comparison-dev-field comparison-dev-share-url-field">
          <span>Selected preset share URL</span>
          <input
            onFocus={(event) => event.currentTarget.select()}
            placeholder="Save and select a preset to share it alone."
            readOnly
            type="text"
            value={selectedPresetShareUrl}
          />
        </label>
        <div className="comparison-dev-actions comparison-dev-actions-inline">
          <button
            className="ghost-button comparison-dev-reset"
            onClick={onCopyShareUrl}
            type="button"
          >
            Copy bundle URL
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            disabled={!selectedPresetName}
            onClick={onCopySelectedPresetShareUrl}
            type="button"
          >
            Copy preset URL
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            onClick={onExportJson}
            type="button"
          >
            Export bundle JSON
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            disabled={!selectedPresetName}
            onClick={onExportSelectedPresetJson}
            type="button"
          >
            Export preset JSON
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            onClick={onImportJson}
            type="button"
          >
            Import JSON
          </button>
        </div>
        <label className="comparison-dev-field">
          <span>Bundle or preset JSON</span>
          <textarea
            onChange={(event) => onChangeShareDraft(event.target.value)}
            placeholder='{"current_tuning": {...}, "presets": {...}} or {"preset_name": "session-a", "tuning": {...}}'
            rows={8}
            value={shareDraft}
          />
        </label>
        <div className="comparison-dev-state-controls">
          <p className="comparison-dev-feedback">
            Saved conflict views: {savedConflictSessionCount}
          </p>
          <div className="comparison-dev-actions comparison-dev-actions-inline">
            <button
              className="ghost-button comparison-dev-reset"
              disabled={!currentConflictSessionUiState}
              onClick={resetCurrentConflictSessionUiState}
              type="button"
            >
              Reset current view
            </button>
            <button
              className="ghost-button comparison-dev-reset"
              disabled={!savedConflictSessionCount}
              onClick={requestResetAllConflictSessionUiState}
              type="button"
            >
              Reset all saved views
            </button>
          </div>
          {isConfirmingResetAllConflictViews ? (
            <div className="comparison-dev-confirm-card">
              <p className="comparison-dev-feedback">
                Clear all saved conflict views? This removes {savedConflictSessionCount} remembered
                {" "}
                session{savedConflictSessionCount === 1 ? "" : "s"} for conflict preview layout.
              </p>
              {visibleSavedConflictSessionSummaries.length ? (
                <div className="comparison-dev-session-summary">
                  <p className="comparison-dev-session-summary-title">Sessions queued for clearing</p>
                  <ul className="comparison-dev-session-summary-list">
                    {displayedSavedConflictSessionSummaries.map((summary) => (
                      <li
                        className="comparison-dev-session-summary-group"
                        key={summary.group_key}
                      >
                        <div className="comparison-dev-session-summary-item">
                          <div className="comparison-dev-session-summary-item-copy">
                            <span>{summary.label}</span>
                            {summary.includes_current ? (
                              <span className="comparison-dev-session-summary-badge">current</span>
                            ) : null}
                          </div>
                          <button
                            className="comparison-dev-session-group-toggle"
                            onClick={() =>
                              setExpandedSavedConflictSessionSummaryGroups((current) => ({
                                ...current,
                                [summary.group_key]: !current[summary.group_key],
                              }))
                            }
                            type="button"
                          >
                            {expandedSavedConflictSessionSummaryGroups[summary.group_key]
                              ? "Hide sessions"
                              : `Show ${summary.session_count} session${
                                  summary.session_count === 1 ? "" : "s"
                                }`}
                          </button>
                        </div>
                        {expandedSavedConflictSessionSummaryGroups[summary.group_key] ? (
                          <ul className="comparison-dev-session-detail-list">
                            {summary.sessions.map((session) => (
                              <li
                                className="comparison-dev-session-detail-item"
                                key={session.session_key}
                              >
                                <div className="comparison-dev-session-detail-copy">
                                  <span className="comparison-dev-session-detail-label">
                                    {session.label}
                                  </span>
                                  <span className="comparison-dev-session-detail-meta">
                                    {session.metadata.map((item) => (
                                      <span
                                        className="comparison-dev-session-detail-chip"
                                        key={item}
                                      >
                                        {item}
                                      </span>
                                    ))}
                                  </span>
                                </div>
                                {session.includes_current ? (
                                  <span className="comparison-dev-session-summary-badge">
                                    current
                                  </span>
                                ) : null}
                              </li>
                            ))}
                          </ul>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                  {hiddenSavedConflictSessionSummaryCount ? (
                    <button
                      className="comparison-dev-session-summary-toggle"
                      onClick={() =>
                        setShowAllSavedConflictSessionSummaries((current) => !current)
                      }
                      type="button"
                    >
                      {showAllSavedConflictSessionSummaries
                        ? "Show fewer preset groups"
                        : `Show all ${savedConflictSessionSummaries.length} preset groups`}
                    </button>
                  ) : null}
                </div>
              ) : null}
              <div className="comparison-dev-actions comparison-dev-actions-inline">
                <button
                  className="ghost-button comparison-dev-reset comparison-dev-reset-danger"
                  onClick={resetAllConflictSessionUiState}
                  type="button"
                >
                  Confirm clear all
                </button>
                <button
                  className="ghost-button comparison-dev-reset"
                  onClick={cancelResetAllConflictSessionUiState}
                  type="button"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : null}
        </div>
        {pendingPresetImportConflict ? (
          <div className="comparison-dev-conflict-card">
            <p className="comparison-dev-conflict-title">
              Preset name collision: {pendingPresetImportConflict.imported_preset_name}
            </p>
            <p className="comparison-dev-feedback">
              A preset with that name already exists. Rename the import, overwrite the local
              preset, or skip this import.
            </p>
            {conflictExistingPreset ? (
              <>
                <p className="comparison-dev-feedback">
                  {changedConflictPreviewCount
                    ? `${changedConflictPreviewCount} tuning value(s) differ and ${unchangedConflictPreviewCount} match.`
                    : "Incoming preset matches the existing preset exactly."}
                </p>
                <div className="comparison-dev-conflict-preview">
                  <div className="comparison-dev-conflict-preview-row comparison-dev-conflict-preview-head">
                    <span>Setting</span>
                    <span>Existing</span>
                    <span>Incoming</span>
                  </div>
                  {changedConflictPreviewGroups.map((group) => (
                    <div className="comparison-dev-conflict-preview-group" key={group.key}>
                      <div className="comparison-dev-conflict-preview-group-title">
                        <span>{group.label}</span>
                        <span className="comparison-dev-conflict-preview-group-meta">
                          <span className="comparison-dev-conflict-preview-group-summary">
                            {group.summary_label}
                          </span>
                        </span>
                      </div>
                      {group.rows.map((row) => (
                        <div
                          className={`comparison-dev-conflict-preview-row ${
                            row.changed ? "is-changed" : ""
                          }`}
                          key={row.key}
                        >
                          <span className="comparison-dev-conflict-preview-label-group">
                            <span className="comparison-dev-conflict-preview-label">{row.label}</span>
                            <span
                              className={`comparison-dev-conflict-delta comparison-dev-conflict-delta-${row.delta_direction}`}
                            >
                              {row.delta_label}
                            </span>
                          </span>
                          <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-existing">
                            {formatComparisonTooltipTuningValue(row.existing_value)}
                          </span>
                          <span
                            className={`comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-incoming comparison-dev-conflict-preview-value-${row.delta_direction}`}
                          >
                            {formatComparisonTooltipTuningValue(row.incoming_value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  ))}
                  {unchangedConflictPreviewCount ? (
                    <button
                      className="comparison-dev-conflict-toggle"
                      onClick={toggleShowUnchangedConflictRows}
                      type="button"
                    >
                      {showUnchangedConflictRows
                        ? `Hide ${unchangedConflictPreviewCount} unchanged value(s)`
                        : `Show ${unchangedConflictPreviewCount} unchanged value(s)`}
                    </button>
                  ) : null}
                  {showUnchangedConflictRows
                    ? unchangedConflictPreviewGroups.map((group) => (
                        <div className="comparison-dev-conflict-preview-group" key={group.key}>
                          <div className="comparison-dev-conflict-preview-group-title">
                            <span>{group.label}</span>
                            <span className="comparison-dev-conflict-preview-group-meta">
                              <span className="comparison-dev-conflict-preview-group-summary">
                                {group.summary_label}
                              </span>
                              {group.rows.length >=
                              COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD ? (
                                <button
                                  className="comparison-dev-conflict-preview-group-toggle"
                                  onClick={() => toggleUnchangedConflictGroupCollapse(group)}
                                  type="button"
                                >
                                  {isUnchangedConflictGroupCollapsed(group)
                                    ? "Show rows"
                                    : "Hide rows"}
                                </button>
                              ) : null}
                            </span>
                          </div>
                          {isUnchangedConflictGroupCollapsed(group)
                            ? null
                            : group.rows.map((row) => (
                                <div className="comparison-dev-conflict-preview-row" key={row.key}>
                                  <span className="comparison-dev-conflict-preview-label-group">
                                    <span className="comparison-dev-conflict-preview-label">
                                      {row.label}
                                    </span>
                                    <span
                                      className={`comparison-dev-conflict-delta comparison-dev-conflict-delta-${row.delta_direction}`}
                                    >
                                      {row.delta_label}
                                    </span>
                                  </span>
                                  <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-existing">
                                    {formatComparisonTooltipTuningValue(row.existing_value)}
                                  </span>
                                  <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-incoming comparison-dev-conflict-preview-value-same">
                                    {formatComparisonTooltipTuningValue(row.incoming_value)}
                                  </span>
                                </div>
                              ))}
                        </div>
                      ))
                    : null}
                </div>
              </>
            ) : null}
            <label className="comparison-dev-field">
              <span>Renamed preset</span>
              <input
                onChange={(event) => onChangePendingPresetImportName(event.target.value)}
                type="text"
                value={pendingPresetImportConflict.proposed_preset_name}
              />
            </label>
            <div className="comparison-dev-actions comparison-dev-actions-inline">
              <button
                className="ghost-button comparison-dev-reset"
                onClick={() => onResolvePendingPresetImportConflict("rename")}
                type="button"
              >
                Rename and import
              </button>
              <button
                className="ghost-button comparison-dev-reset"
                onClick={() => onResolvePendingPresetImportConflict("overwrite")}
                type="button"
              >
                Overwrite existing
              </button>
              <button
                className="ghost-button comparison-dev-reset"
                onClick={() => onResolvePendingPresetImportConflict("skip")}
                type="button"
              >
                Skip import
              </button>
            </div>
          </div>
        ) : null}
        {shareFeedback ? <p className="comparison-dev-feedback">{shareFeedback}</p> : null}
      </div>
      <div className="comparison-dev-grid">
        <ComparisonTooltipTuningField
          label="Metric open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="metric_hover_open_ms"
          value={tuning.metric_hover_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Metric close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="metric_hover_close_ms"
          value={tuning.metric_hover_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Row open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="row_sweep_open_ms"
          value={tuning.row_sweep_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Row close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="row_sweep_close_ms"
          value={tuning.row_sweep_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Row hold"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="row_sweep_hold_ms"
          value={tuning.row_sweep_hold_ms}
        />
        <ComparisonTooltipTuningField
          label="Col down open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_down_sweep_open_ms"
          value={tuning.column_down_sweep_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Col down close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_down_sweep_close_ms"
          value={tuning.column_down_sweep_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Col down hold"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_down_sweep_hold_ms"
          value={tuning.column_down_sweep_hold_ms}
        />
        <ComparisonTooltipTuningField
          label="Col up open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_up_sweep_open_ms"
          value={tuning.column_up_sweep_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Col up close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_up_sweep_close_ms"
          value={tuning.column_up_sweep_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Col up hold"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_up_sweep_hold_ms"
          value={tuning.column_up_sweep_hold_ms}
        />
        <ComparisonTooltipTuningField
          label="Time min"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="sweep_time_min_ms"
          value={tuning.sweep_time_min_ms}
        />
        <ComparisonTooltipTuningField
          label="Time max"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="sweep_time_max_ms"
          value={tuning.sweep_time_max_ms}
        />
        <ComparisonTooltipTuningField
          label="Time speed"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="sweep_time_speed_multiplier"
          value={tuning.sweep_time_speed_multiplier}
        />
        <ComparisonTooltipTuningField
          label="Horiz ratio"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="horizontal_distance_ratio"
          value={tuning.horizontal_distance_ratio}
        />
        <ComparisonTooltipTuningField
          label="Horiz velocity"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="horizontal_velocity_threshold"
          value={tuning.horizontal_velocity_threshold}
        />
        <ComparisonTooltipTuningField
          label="Vert ratio"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="vertical_distance_ratio"
          value={tuning.vertical_distance_ratio}
        />
        <ComparisonTooltipTuningField
          label="Vert velocity"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="vertical_velocity_threshold"
          value={tuning.vertical_velocity_threshold}
        />
        <ComparisonTooltipTuningField
          label="Speed base"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_base"
          value={tuning.speed_adjustment_base}
        />
        <ComparisonTooltipTuningField
          label="Speed slope"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_slope"
          value={tuning.speed_adjustment_slope}
        />
        <ComparisonTooltipTuningField
          label="Speed min"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_min"
          value={tuning.speed_adjustment_min}
        />
        <ComparisonTooltipTuningField
          label="Speed max"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_max"
          value={tuning.speed_adjustment_max}
        />
      </div>
      <div className="comparison-dev-actions">
        <button className="ghost-button comparison-dev-reset" onClick={onReset} type="button">
          Reset tuning
        </button>
      </div>
    </details>
  );
}

export function ComparisonTooltipTuningField({
  label,
  onChangeValue,
  step,
  tuningKey,
  value,
}: {
  label: string;
  onChangeValue: (key: keyof ComparisonTooltipTuning, value: string) => void;
  step: string;
  tuningKey: keyof ComparisonTooltipTuning;
  value: number;
}) {
  return (
    <label className="comparison-dev-field">
      <span>{label}</span>
      <input
        min="0"
        onChange={(event) => onChangeValue(tuningKey, event.target.value)}
        step={step}
        type="number"
        value={value}
      />
    </label>
  );
}

function sanitizeComparisonTooltipId(value: string) {
  return value.replace(/[^a-zA-Z0-9_-]+/g, "-");
}

function loadComparisonTooltipTuningPresetState(): ComparisonTooltipTuningPresetStateV1 {
  try {
    const raw = window.localStorage.getItem(COMPARISON_TOOLTIP_TUNING_STORAGE_KEY);
    if (!raw) {
      return createDefaultComparisonTooltipTuningPresetState();
    }
    const parsed = parseComparisonTooltipTuningPresetState(raw, { requireVersion: true });
    if (!parsed) {
      return createDefaultComparisonTooltipTuningPresetState();
    }
    return parsed;
  } catch {
    return createDefaultComparisonTooltipTuningPresetState();
  }
}

function loadComparisonTooltipConflictUiState(): ComparisonTooltipConflictUiStateV1 {
  try {
    const raw = window.localStorage.getItem(COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY);
    if (!raw) {
      return createDefaultComparisonTooltipConflictUiState();
    }
    const parsed = JSON.parse(raw) as Partial<ComparisonTooltipConflictUiStateV1> | null;
    if (!parsed || parsed.version !== COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION) {
      return createDefaultComparisonTooltipConflictUiState();
    }
    return {
      sessions: normalizeComparisonTooltipConflictSessionUiStateMap(parsed.sessions),
      version: COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION,
    };
  } catch {
    return createDefaultComparisonTooltipConflictUiState();
  }
}

function loadComparisonTooltipTuningShareImportFromUrl(): ComparisonTooltipTuningShareImport | null {
  try {
    const url = new URL(window.location.href);
    const sharedValue = url.searchParams.get(COMPARISON_TOOLTIP_TUNING_SHARE_PARAM);
    if (!sharedValue) {
      return null;
    }
    const decoded = decodeComparisonTooltipTuningSharePayload(sharedValue);
    if (!decoded) {
      return null;
    }
    return parseComparisonTooltipTuningShareImport(decoded);
  } catch {
    return null;
  }
}

function persistComparisonTooltipTuningPresetState(
  state: ComparisonTooltipTuningPresetStateV1,
) {
  try {
    window.localStorage.setItem(COMPARISON_TOOLTIP_TUNING_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore localStorage failures in dev-only tuning controls.
  }
}

function persistComparisonTooltipConflictUiState(state: ComparisonTooltipConflictUiStateV1) {
  try {
    window.localStorage.setItem(COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore localStorage failures in dev-only tuning controls.
  }
}

function createDefaultComparisonTooltipTuningPresetState(): ComparisonTooltipTuningPresetStateV1 {
  return {
    current_tuning: { ...DEFAULT_COMPARISON_TOOLTIP_TUNING },
    presets: {},
    selected_preset_name: null,
    version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
  };
}

function createDefaultComparisonTooltipConflictUiState(): ComparisonTooltipConflictUiStateV1 {
  return {
    sessions: {},
    version: COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION,
  };
}

function createComparisonTooltipTuningSinglePresetShare(
  presetName: string,
  tuning: ComparisonTooltipTuning,
): ComparisonTooltipTuningSinglePresetShareV1 {
  return {
    preset_name: presetName,
    tuning: { ...tuning },
    version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
  };
}

function cloneComparisonTooltipPresetMap(
  value: Record<string, ComparisonTooltipTuning>,
): Record<string, ComparisonTooltipTuning> {
  return Object.fromEntries(
    Object.entries(value).map(([key, preset]) => [key, { ...preset }]),
  );
}

function normalizeComparisonTooltipConflictSessionUiStateMap(
  value: unknown,
): Record<string, ComparisonTooltipConflictSessionUiState> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.entries(value).reduce<Record<string, ComparisonTooltipConflictSessionUiState>>(
    (accumulator, [key, session]) => {
      if (!key.trim() || !session || typeof session !== "object") {
        return accumulator;
      }
      const parsed = session as Partial<ComparisonTooltipConflictSessionUiState>;
      accumulator[key] = {
        collapsed_unchanged_groups: normalizeComparisonTooltipBooleanMap(
          parsed.collapsed_unchanged_groups,
        ),
        show_unchanged_conflict_rows: parsed.show_unchanged_conflict_rows === true,
        updated_at:
          typeof parsed.updated_at === "string" && parsed.updated_at.trim()
            ? parsed.updated_at
            : null,
      };
      return accumulator;
    },
    {},
  );
}

function normalizeComparisonTooltipBooleanMap(value: unknown): Record<string, boolean> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.entries(value).reduce<Record<string, boolean>>((accumulator, [key, flag]) => {
    if (!key.trim() || typeof flag !== "boolean") {
      return accumulator;
    }
    accumulator[key] = flag;
    return accumulator;
  }, {});
}

function parseComparisonTooltipTuningPresetState(
  raw: string,
  options?: { requireVersion?: boolean },
): ComparisonTooltipTuningPresetStateV1 | null {
  try {
    const parsed = JSON.parse(raw) as Partial<ComparisonTooltipTuningPresetStateV1> | null;
    if (!parsed) {
      return null;
    }
    if (options?.requireVersion && parsed.version !== COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION) {
      return null;
    }
    if (
      typeof parsed.version === "number" &&
      parsed.version !== COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION
    ) {
      return null;
    }
    if (!("current_tuning" in parsed) && !("presets" in parsed)) {
      return null;
    }
    const presets = normalizeComparisonTooltipPresetMap(parsed.presets);
    const selectedPresetName =
      typeof parsed.selected_preset_name === "string" && presets[parsed.selected_preset_name]
        ? parsed.selected_preset_name
        : null;
    return {
      current_tuning: normalizeComparisonTooltipTuning(parsed.current_tuning),
      presets,
      selected_preset_name: selectedPresetName,
      version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
    };
  } catch {
    return null;
  }
}

function parseComparisonTooltipTuningShareImport(
  raw: string,
): ComparisonTooltipTuningShareImport | null {
  const bundleState = parseComparisonTooltipTuningPresetState(raw);
  if (bundleState) {
    return {
      kind: "bundle",
      raw,
      state: bundleState,
    };
  }
  try {
    const parsed = JSON.parse(raw) as Partial<ComparisonTooltipTuningSinglePresetShareV1> | null;
    if (!parsed) {
      return null;
    }
    if (
      typeof parsed.version === "number" &&
      parsed.version !== COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION
    ) {
      return null;
    }
    if (typeof parsed.preset_name !== "string" || !parsed.preset_name.trim()) {
      return null;
    }
    return {
      kind: "preset",
      preset_name: parsed.preset_name.trim(),
      raw,
      tuning: normalizeComparisonTooltipTuning(parsed.tuning),
    };
  } catch {
    return null;
  }
}

function applyComparisonTooltipTuningShareImport(
  baseState: ComparisonTooltipTuningPresetStateV1,
  importedShare: ComparisonTooltipTuningShareImport,
  presetImportConflictPolicy: ComparisonTooltipPresetImportConflictPolicy,
):
  | {
      kind: "bundle";
      state: ComparisonTooltipTuningPresetStateV1;
    }
  | {
      kind: "preset";
      resolution: ComparisonTooltipPresetImportResolution;
      state: ComparisonTooltipTuningPresetStateV1;
    } {
  if (importedShare.kind === "bundle") {
    return {
      kind: "bundle",
      state: importedShare.state,
    };
  }
  return {
    kind: "preset",
    ...mergeComparisonTooltipSinglePresetIntoState(
      baseState,
      importedShare.preset_name,
      importedShare.tuning,
      presetImportConflictPolicy,
    ),
  };
}

function mergeComparisonTooltipSinglePresetIntoState(
  baseState: ComparisonTooltipTuningPresetStateV1,
  presetName: string,
  tuning: ComparisonTooltipTuning,
  presetImportConflictPolicy: ComparisonTooltipPresetImportConflictPolicy,
  renamedPresetName?: string,
): {
  resolution: ComparisonTooltipPresetImportResolution;
  state: ComparisonTooltipTuningPresetStateV1;
} {
  const importedPresetName = presetName.trim();
  const conflicted = Boolean(baseState.presets[importedPresetName]);
  const requestedPresetName =
    presetImportConflictPolicy === "rename" ? renamedPresetName?.trim() : undefined;
  const finalPresetName =
    presetImportConflictPolicy === "rename"
      ? requestedPresetName && requestedPresetName !== importedPresetName
        ? requestedPresetName
        : conflicted
          ? createAvailableComparisonTooltipPresetName(baseState.presets, importedPresetName)
          : importedPresetName
      : importedPresetName;

  return {
    resolution: {
      conflicted,
      final_preset_name: finalPresetName,
      imported_preset_name: importedPresetName,
      policy: presetImportConflictPolicy,
      renamed: conflicted && finalPresetName !== importedPresetName,
      overwritten: conflicted && finalPresetName === importedPresetName,
    },
    state: {
      current_tuning: { ...tuning },
      presets: {
        ...cloneComparisonTooltipPresetMap(baseState.presets),
        [finalPresetName]: { ...tuning },
      },
      selected_preset_name: finalPresetName,
      version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
    },
  };
}

function createAvailableComparisonTooltipPresetName(
  presets: Record<string, ComparisonTooltipTuning>,
  presetName: string,
) {
  const normalizedBaseName = presetName.trim() || "imported-preset";
  if (!presets[normalizedBaseName]) {
    return normalizedBaseName;
  }
  const firstCandidate = `${normalizedBaseName} (import)`;
  if (!presets[firstCandidate]) {
    return firstCandidate;
  }
  let suffix = 2;
  while (presets[`${normalizedBaseName} (import ${suffix})`]) {
    suffix += 1;
  }
  return `${normalizedBaseName} (import ${suffix})`;
}

function buildComparisonTooltipPresetConflictPreviewRows(
  existingTuning: ComparisonTooltipTuning,
  incomingTuning: ComparisonTooltipTuning,
): ComparisonTooltipPresetConflictPreviewRow[] {
  return (
    Object.keys(DEFAULT_COMPARISON_TOOLTIP_TUNING) as Array<keyof ComparisonTooltipTuning>
  ).map((key) => {
    const existingValue = existingTuning[key];
    const incomingValue = incomingTuning[key];
    const delta = formatComparisonTooltipTuningDelta(existingValue, incomingValue);
    const group = COMPARISON_TOOLTIP_TUNING_GROUPS[key];
    return {
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: existingValue,
      group_key: group.key,
      group_label: group.label,
      group_order: group.order,
      incoming_value: incomingValue,
      key,
      label: COMPARISON_TOOLTIP_TUNING_LABELS[key],
    };
  });
}

function groupComparisonTooltipPresetConflictPreviewRows(
  rows: ComparisonTooltipPresetConflictPreviewRow[],
): ComparisonTooltipPresetConflictPreviewGroup[] {
  const groups = rows.reduce<Map<string, ComparisonTooltipPresetConflictPreviewGroup>>(
    (accumulator, row) => {
      const existingGroup = accumulator.get(row.group_key);
      if (existingGroup) {
        existingGroup.rows.push(row);
        return accumulator;
      }
      accumulator.set(row.group_key, {
        changed_count: 0,
        higher_count: 0,
        key: row.group_key,
        label: row.group_label,
        lower_count: 0,
        rows: [row],
        same_count: 0,
        summary_label: "",
      });
      return accumulator;
    },
    new Map(),
  );

  return [...groups.values()]
    .sort((left, right) => {
      const leftOrder = left.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      return leftOrder - rightOrder || left.label.localeCompare(right.label);
    })
    .map((group) => ({
      ...group,
      changed_count: group.rows.filter((row) => row.changed).length,
      higher_count: group.rows.filter((row) => row.delta_direction === "higher").length,
      lower_count: group.rows.filter((row) => row.delta_direction === "lower").length,
      rows: [...group.rows].sort((left, right) => left.label.localeCompare(right.label)),
      same_count: group.rows.filter((row) => row.delta_direction === "same").length,
      summary_label: formatComparisonTooltipPresetConflictGroupSummary(group.rows),
    }));
}

function seedComparisonTooltipUnchangedConflictGroupCollapseState(
  groups: ComparisonTooltipPresetConflictPreviewGroup[],
  current: Record<string, boolean>,
) {
  return groups.reduce<Record<string, boolean>>((accumulator, group) => {
    if (Object.prototype.hasOwnProperty.call(accumulator, group.key)) {
      return accumulator;
    }
    accumulator[group.key] =
      group.rows.length >= COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD;
    return accumulator;
  }, { ...current });
}

function buildComparisonTooltipConflictSessionKey(
  pendingConflict: ComparisonTooltipPendingPresetImportConflict,
) {
  return `${pendingConflict.imported_preset_name}:${hashComparisonTooltipConflictSessionRaw(
    pendingConflict.raw,
  )}`;
}

function buildComparisonTooltipConflictSessionSummaries(
  sessions: Record<string, ComparisonTooltipConflictSessionUiState>,
  currentConflictSessionKey: string | null,
  referenceNowMs: number,
): ComparisonTooltipConflictSessionSummary[] {
  const groupedSessions = Object.keys(sessions).reduce<
    Record<string, Omit<ComparisonTooltipConflictSessionSummary, "label">>
  >((accumulator, sessionKey) => {
    const parsed = parseComparisonTooltipConflictSessionKey(sessionKey);
    const presetName = parsed.preset_name || "Unnamed preset";
    const current = accumulator[presetName] ?? {
      group_key: presetName,
      includes_current: false,
      preset_name: presetName,
      session_count: 0,
      sessions: [],
    };
    const includesCurrent = sessionKey === currentConflictSessionKey;
    current.includes_current ||= includesCurrent;
    current.session_count += 1;
    current.sessions.push({
      hash: parsed.hash,
      includes_current: includesCurrent,
      label: "",
      metadata: [],
      session_key: sessionKey,
      updated_at: sessions[sessionKey]?.updated_at ?? null,
    });
    accumulator[presetName] = current;
    return accumulator;
  }, {});

  return Object.values(groupedSessions)
    .sort((left, right) => {
      if (left.includes_current !== right.includes_current) {
        return left.includes_current ? -1 : 1;
      }
      if (left.session_count !== right.session_count) {
        return right.session_count - left.session_count;
      }
      return left.preset_name.localeCompare(right.preset_name);
    })
    .map((summary) => ({
      ...summary,
      label: formatComparisonTooltipConflictSessionSummary(summary),
      sessions: [...summary.sessions]
        .sort((left, right) => {
          if (left.includes_current !== right.includes_current) {
            return left.includes_current ? -1 : 1;
          }
          const leftUpdatedAt = parseComparisonTooltipConflictSessionUpdatedAt(left.updated_at);
          const rightUpdatedAt = parseComparisonTooltipConflictSessionUpdatedAt(right.updated_at);
          if (leftUpdatedAt !== rightUpdatedAt) {
            return rightUpdatedAt - leftUpdatedAt;
          }
          return (left.hash ?? "").localeCompare(right.hash ?? "");
        })
        .map((session, index) => ({
          ...session,
          label: formatComparisonTooltipConflictSessionSummarySession(
            session,
            index,
            summary.session_count,
          ),
          metadata: formatComparisonTooltipConflictSessionMetadata(
            sessions[session.session_key],
            session.hash,
            referenceNowMs,
          ),
        })),
    }));
}

function parseComparisonTooltipConflictSessionKey(sessionKey: string) {
  const separatorIndex = sessionKey.lastIndexOf(":");
  if (separatorIndex <= 0 || separatorIndex === sessionKey.length - 1) {
    return {
      hash: null,
      preset_name: sessionKey.trim(),
    };
  }
  return {
    hash: sessionKey.slice(separatorIndex + 1).trim() || null,
    preset_name: sessionKey.slice(0, separatorIndex).trim(),
  };
}

function normalizeComparisonTooltipPresetMap(
  value: unknown,
): Record<string, ComparisonTooltipTuning> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.entries(value).reduce<Record<string, ComparisonTooltipTuning>>(
    (accumulator, [key, preset]) => {
      if (!key.trim()) {
        return accumulator;
      }
      accumulator[key] = normalizeComparisonTooltipTuning(preset);
      return accumulator;
    },
    {},
  );
}

function normalizeComparisonTooltipTuning(value: unknown): ComparisonTooltipTuning {
  if (!value || typeof value !== "object") {
    return { ...DEFAULT_COMPARISON_TOOLTIP_TUNING };
  }
  const parsed = value as Partial<Record<keyof ComparisonTooltipTuning, unknown>>;
  const next = { ...DEFAULT_COMPARISON_TOOLTIP_TUNING };
  (
    Object.keys(DEFAULT_COMPARISON_TOOLTIP_TUNING) as Array<keyof ComparisonTooltipTuning>
  ).forEach((key) => {
    const candidate = parsed[key];
    if (typeof candidate === "number" && Number.isFinite(candidate)) {
      next[key] = candidate;
    }
  });
  return next;
}

function buildComparisonTooltipTuningShareUrl(
  state: ComparisonTooltipTuningPresetStateV1 | ComparisonTooltipTuningSinglePresetShareV1,
) {
  const url = new URL(window.location.href);
  url.searchParams.set(
    COMPARISON_TOOLTIP_TUNING_SHARE_PARAM,
    encodeComparisonTooltipTuningSharePayload(JSON.stringify(state)),
  );
  return url.toString();
}

function encodeComparisonTooltipTuningSharePayload(value: string) {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return window
    .btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function decodeComparisonTooltipTuningSharePayload(value: string) {
  try {
    let normalized = value.replace(/-/g, "+").replace(/_/g, "/");
    while (normalized.length % 4 !== 0) {
      normalized += "=";
    }
    const binary = window.atob(normalized);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  } catch {
    return null;
  }
}

function buildComparisonTooltipId(baseId: string, ...parts: Array<string | null | undefined>) {
  return sanitizeComparisonTooltipId([baseId, ...parts].filter(Boolean).join("-"));
}

function getComparisonTooltipBoundaryRect(target: HTMLElement) {
  return target.closest(".comparison-table-wrap")?.getBoundingClientRect() ?? null;
}

function getAdaptiveMetricSweepTimeThreshold(
  pointerSpeed: number,
  tuning: ComparisonTooltipTuning,
) {
  return clampComparisonNumber(
    tuning.sweep_time_min_ms + pointerSpeed * tuning.sweep_time_speed_multiplier,
    tuning.sweep_time_min_ms,
    tuning.sweep_time_max_ms,
  );
}

function getAdaptiveMetricSweepDistanceThreshold(
  cellSize: number,
  pointerSpeed: number,
  axis: "horizontal" | "vertical",
  tuning: ComparisonTooltipTuning,
) {
  const baseRatio =
    axis === "horizontal" ? tuning.horizontal_distance_ratio : tuning.vertical_distance_ratio;
  const minimum = axis === "horizontal" ? 16 : 12;
  const maximum = axis === "horizontal" ? 44 : 34;
  const baseThreshold = clampComparisonNumber(cellSize * baseRatio, minimum, maximum);
  const speedAdjustment = clampComparisonNumber(
    tuning.speed_adjustment_base - pointerSpeed * tuning.speed_adjustment_slope,
    tuning.speed_adjustment_min,
    tuning.speed_adjustment_max,
  );
  return baseThreshold * speedAdjustment;
}

function clampComparisonNumber(value: number, minimum: number, maximum: number) {
  if (maximum < minimum) {
    return minimum;
  }
  return Math.min(Math.max(value, minimum), maximum);
}

export function ReferenceRunProvenanceSummary({
  artifactPaths,
  benchmarkArtifacts,
  externalCommand,
  interactionSource = "provenance",
  linkedScore,
  onDrillBackScoreLink,
  panelRef,
  panelRunId,
  registerArtifactHoverRef,
  registerSubFocusRef,
  reference,
  referenceVersion,
  strategySemantics,
  workingDirectory,
}: {
  artifactPaths: string[];
  benchmarkArtifacts: BenchmarkArtifact[];
  externalCommand: string[];
  interactionSource?: ComparisonScoreLinkSource;
  linkedScore?: (ComparisonScoreLinkTarget & { role: ComparisonScoreLinkedRunRole }) | null;
  onDrillBackScoreLink?: (
    section: ComparisonScoreSection,
    componentKey: string,
    options?: ComparisonScoreDrillBackOptions,
  ) => void;
  panelRef?: (node: HTMLElement | null) => void;
  panelRunId: string;
  registerArtifactHoverRef?: (
    runId: string,
    artifactHoverKey: string,
  ) => (node: HTMLElement | null) => void;
  registerSubFocusRef?: (
    runId: string,
    subFocusKey: string,
  ) => (node: HTMLElement | null) => void;
  reference: ReferenceSource;
  referenceVersion?: string | null;
  strategySemantics?: {
    strategy_kind: string;
    execution_model: string;
    parameter_contract: string;
    source_descriptor?: string | null;
    operator_notes: string[];
  } | null;
  workingDirectory?: string | null;
}) {
  const linkedScoreSelection = linkedScore ?? null;
  const highlightStrategyKind =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["strategy_kind", "vocabulary"], "semantics");
  const highlightExecutionModel =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["execution_model", "vocabulary"], "semantics");
  const highlightParameterContract =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["parameter_contract", "vocabulary"], "semantics");
  const highlightSourceDescriptor =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, [
      "source_descriptor",
      "vocabulary",
      "native_reference_bonus",
      "reference_bonus",
      "reference_floor",
    ]);
  const highlightReferenceIdentity =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, [
      "source_descriptor",
      "provenance_richness",
      "native_reference_bonus",
      "reference_bonus",
      "reference_floor",
      "benchmark_story_bonus",
    ]);
  const highlightOperatorNotes =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["vocabulary"], "semantics");
  const highlightExecutionContext =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, [
      "provenance_richness",
      "reference_bonus",
      "reference_floor",
      "native_reference_bonus",
      "benchmark_story_bonus",
    ]);
  const highlightArtifacts =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["provenance_richness", "benchmark_story_bonus"]);
  const highlightPanel =
    highlightStrategyKind
    || highlightExecutionModel
    || highlightParameterContract
    || highlightSourceDescriptor
    || highlightReferenceIdentity
    || highlightOperatorNotes
    || highlightExecutionContext
    || highlightArtifacts;
  const isActiveInteractionSource = linkedScoreSelection?.source === interactionSource;
  const highlightOrigin =
    linkedScoreSelection?.source === interactionSource
    && linkedScoreSelection?.originRunId === panelRunId;
  const activeProvenanceSubFocusKey =
    isActiveInteractionSource
      ? linkedScoreSelection.subFocusKey
      : null;
  const activeProvenanceArtifactHoverKey =
    isActiveInteractionSource
      ? linkedScoreSelection.artifactHoverKey
      : null;
  const activeProvenanceArtifactLineDetailExpanded =
    isActiveInteractionSource
      ? linkedScoreSelection.artifactLineDetailExpanded
      : null;
  const activeProvenanceArtifactLineDetailView =
    isActiveInteractionSource
      ? linkedScoreSelection.artifactLineDetailView
      : null;
  const activeProvenanceArtifactLineMicroView =
    isActiveInteractionSource
      ? linkedScoreSelection.artifactLineMicroView
      : null;
  const activeProvenanceArtifactLineNotePage =
    isActiveInteractionSource
      ? linkedScoreSelection.artifactLineNotePage
      : null;
  const activeProvenanceArtifactLineDetailHoverKey =
    isActiveInteractionSource
      ? linkedScoreSelection.artifactLineDetailHoverKey
      : null;
  const activeProvenanceArtifactLineDetailScrubStep =
    isActiveInteractionSource
      ? linkedScoreSelection.artifactLineDetailScrubStep
      : null;
  const renderProvenanceCopyLine = ({
    children,
    componentKey,
    highlighted = false,
    subFocusKey,
    section,
  }: {
    children: string;
    componentKey?: string;
    highlighted?: boolean;
    subFocusKey?: string;
    section?: ComparisonScoreSection;
  }) => {
    const className =
      [
        highlighted ? "comparison-linked-copy" : "",
        subFocusKey && activeProvenanceSubFocusKey === subFocusKey
          ? "comparison-linked-subfocus"
          : "",
        section && componentKey && onDrillBackScoreLink
          ? "reference-provenance-link comparison-drillback-target"
          : "",
      ]
        .filter(Boolean)
        .join(" ") || undefined;
    if (!section || !componentKey || !onDrillBackScoreLink) {
      return <p className={className}>{children}</p>;
    }
    const isPressed =
      linkedScoreSelection?.section === section
      && linkedScoreSelection.componentKey === componentKey
      && (!subFocusKey || !activeProvenanceSubFocusKey || activeProvenanceSubFocusKey === subFocusKey);
    return (
      <button
        aria-label={`Trace ${formatComparisonScoreComponentLabel(section, componentKey)}`}
        aria-pressed={isPressed}
        className={className}
        onClick={() =>
          onDrillBackScoreLink(section, componentKey, {
            artifactDetailExpanded: null,
            artifactLineDetailExpanded: null,
            artifactLineDetailView: null,
            artifactLineMicroView: null,
            artifactLineNotePage: null,
            artifactLineDetailHoverKey: null,
            artifactLineDetailScrubStep: null,
            artifactHoverKey: null,
            subFocusKey: subFocusKey ?? null,
          })
        }
        onKeyDown={(event) => {
          if (event.key !== "Enter" && event.key !== " ") {
            return;
          }
          event.preventDefault();
          onDrillBackScoreLink(section, componentKey, {
            artifactDetailExpanded: null,
            artifactLineDetailExpanded: null,
            artifactLineDetailView: null,
            artifactLineMicroView: null,
            artifactLineNotePage: null,
            artifactLineDetailHoverKey: null,
            artifactLineDetailScrubStep: null,
            artifactHoverKey: null,
            subFocusKey: subFocusKey ?? null,
          });
        }}
        ref={subFocusKey ? registerSubFocusRef?.(panelRunId, subFocusKey) : undefined}
        type="button"
      >
        {children}
      </button>
    );
  };

  return (
    <section
      className={`reference-provenance ${highlightPanel ? "comparison-linked-panel" : ""} ${
        linkedScore?.role === "target" ? "comparison-linked-panel-target" : ""
      } ${linkedScore?.role === "baseline" ? "comparison-linked-panel-baseline" : ""} ${
        highlightOrigin ? "comparison-linked-panel-origin" : ""
      }`.trim()}
      ref={panelRef}
    >
      <div className="reference-provenance-head">
        <span>Reference provenance</span>
        <strong>{reference.integration_mode}</strong>
      </div>
      <div className="reference-provenance-grid">
        <Metric label="Reference" value={reference.title} />
        <Metric label="License" value={reference.license} />
        <Metric label="Version" value={referenceVersion ?? "unknown"} />
        <Metric label="Runtime" value={reference.runtime ?? "n/a"} />
      </div>
      <div className="reference-provenance-copy">
        {renderProvenanceCopyLine({
          children: `ID: ${reference.reference_id}`,
          componentKey: "source_descriptor",
          highlighted: highlightReferenceIdentity,
          subFocusKey: buildComparisonProvenanceLineSubFocusKey("reference_id"),
          section: "semantics",
        })}
        {reference.homepage
          ? renderProvenanceCopyLine({
              children: `Homepage: ${reference.homepage}`,
              componentKey: "source_descriptor",
              highlighted: highlightReferenceIdentity,
              subFocusKey: buildComparisonProvenanceLineSubFocusKey("homepage"),
              section: "semantics",
            })
          : null}
        {strategySemantics?.strategy_kind ? (
          renderProvenanceCopyLine({
            children: `Semantic kind: ${strategySemantics.strategy_kind}`,
            componentKey: "strategy_kind",
            highlighted: highlightStrategyKind,
            subFocusKey: buildComparisonProvenanceLineSubFocusKey("strategy_kind"),
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.execution_model ? (
          renderProvenanceCopyLine({
            children: `Execution model: ${strategySemantics.execution_model}`,
            componentKey: "execution_model",
            highlighted: highlightExecutionModel,
            subFocusKey: buildComparisonProvenanceLineSubFocusKey("execution_model"),
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.parameter_contract ? (
          renderProvenanceCopyLine({
            children: `Parameter contract: ${strategySemantics.parameter_contract}`,
            componentKey: "parameter_contract",
            highlighted: highlightParameterContract,
            subFocusKey: buildComparisonProvenanceLineSubFocusKey("parameter_contract"),
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.source_descriptor ? (
          renderProvenanceCopyLine({
            children: `Semantic source: ${strategySemantics.source_descriptor}`,
            componentKey: "source_descriptor",
            highlighted: highlightSourceDescriptor,
            subFocusKey: buildComparisonProvenanceLineSubFocusKey("semantic_source"),
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.operator_notes?.length ? (
          renderProvenanceCopyLine({
            children: `Operator notes: ${strategySemantics.operator_notes.join(" | ")}`,
            componentKey: "vocabulary",
            highlighted: highlightOperatorNotes,
            subFocusKey: buildComparisonProvenanceLineSubFocusKey("operator_notes"),
            section: "semantics",
          })
        ) : null}
        {workingDirectory
          ? renderProvenanceCopyLine({
              children: `Working dir: ${workingDirectory}`,
              componentKey: "provenance_richness",
              highlighted: highlightExecutionContext,
              subFocusKey: buildComparisonProvenanceLineSubFocusKey("working_directory"),
              section: "context",
            })
          : null}
        {externalCommand.length
          ? renderProvenanceCopyLine({
              children: `Command: ${externalCommand.join(" ")}`,
              componentKey: "provenance_richness",
              highlighted: highlightExecutionContext,
              subFocusKey: buildComparisonProvenanceLineSubFocusKey("command"),
              section: "context",
            })
          : null}
        {benchmarkArtifacts.length ? (
          <div className="reference-artifact-list">
            {benchmarkArtifacts.map((artifact) => {
              const summaryEntries = formatBenchmarkArtifactSummaryEntries(artifact.summary);
              const sectionEntries = formatBenchmarkArtifactSectionEntries(artifact.sections ?? {});
              const artifactComponentKey =
                summaryEntries.length || sectionEntries.length ? "benchmark_story_bonus" : "provenance_richness";
              const artifactSubFocusKey = buildComparisonProvenanceArtifactSubFocusKey(artifact.path);
              const artifactSummaryHoverPrefix = `provenance-artifact-summary:${encodeComparisonScoreLinkToken(
                artifact.path,
              )}:`;
              const artifactSectionLineHoverPrefix = `provenance-artifact-section-line:${encodeComparisonScoreLinkToken(
                artifact.path,
              )}:`;
              const artifactSectionSubFocusPrefix = `provenance-artifact-section:${encodeComparisonScoreLinkToken(
                artifact.path,
              )}:`;
              const artifactIsLinked =
                linkedScoreSelection?.source === interactionSource
                && linkedScoreSelection.section === "context"
                && linkedScoreSelection.componentKey === artifactComponentKey;
              const artifactIsPressed =
                artifactIsLinked
                && (
                  !activeProvenanceSubFocusKey
                  || activeProvenanceSubFocusKey === artifactSubFocusKey
                  || activeProvenanceSubFocusKey.startsWith(artifactSectionSubFocusPrefix)
                );
              const artifactHasSelectedSubFocus =
                activeProvenanceSubFocusKey === artifactSubFocusKey
                || activeProvenanceSubFocusKey?.startsWith(artifactSectionSubFocusPrefix);
              const artifactDetailsExpanded =
                artifactHasSelectedSubFocus
                  ? linkedScoreSelection?.artifactDetailExpanded !== false
                  : true;
              return (
                <article
                  aria-label={`Trace ${formatComparisonScoreComponentLabel("context", artifactComponentKey)}`}
                  aria-pressed={onDrillBackScoreLink ? artifactIsPressed : undefined}
                  className={`reference-artifact-card ${highlightArtifacts ? "is-linked" : ""} ${
                    artifactHasSelectedSubFocus
                      ? "is-subfocus"
                      : ""
                  } ${!artifactDetailsExpanded ? "is-collapsed" : ""} ${
                    activeProvenanceArtifactHoverKey?.startsWith(artifactSummaryHoverPrefix)
                    || activeProvenanceArtifactHoverKey?.startsWith(artifactSectionLineHoverPrefix)
                      ? "has-hover-focus"
                      : ""
                  } ${
                    onDrillBackScoreLink ? "is-drillback comparison-drillback-target" : ""
                  }`.trim()}
                  key={`${artifact.kind}-${artifact.path}`}
                  onClick={
                    onDrillBackScoreLink
                      ? () =>
                          onDrillBackScoreLink("context", artifactComponentKey, {
                            artifactDetailExpanded: artifactHasSelectedSubFocus
                              ? artifactDetailsExpanded
                              : true,
                            artifactLineDetailExpanded: null,
                            artifactLineDetailView: null,
                            artifactLineMicroView: null,
                            artifactLineNotePage: null,
                            artifactLineDetailHoverKey: null,
                            artifactLineDetailScrubStep: null,
                            artifactHoverKey: null,
                            subFocusKey: artifactSubFocusKey,
                          })
                      : undefined
                  }
                  onKeyDown={
                    onDrillBackScoreLink
                      ? (event) => {
                          if (event.key !== "Enter" && event.key !== " ") {
                            return;
                          }
                          event.preventDefault();
                          onDrillBackScoreLink("context", artifactComponentKey, {
                            artifactDetailExpanded: artifactHasSelectedSubFocus
                              ? artifactDetailsExpanded
                              : true,
                            artifactLineDetailExpanded: null,
                            artifactLineDetailView: null,
                            artifactLineMicroView: null,
                            artifactLineNotePage: null,
                            artifactLineDetailHoverKey: null,
                            artifactLineDetailScrubStep: null,
                            artifactHoverKey: null,
                            subFocusKey: artifactSubFocusKey,
                          });
                        }
                      : undefined
                  }
                  ref={registerSubFocusRef?.(panelRunId, artifactSubFocusKey)}
                  role={onDrillBackScoreLink ? "button" : undefined}
                  tabIndex={onDrillBackScoreLink ? 0 : undefined}
                >
                  <div className="reference-artifact-head">
                    <strong>{artifact.label}</strong>
                    <div className="reference-artifact-head-meta">
                      <span>{artifact.kind}</span>
                      {onDrillBackScoreLink && artifactHasSelectedSubFocus && (summaryEntries.length || sectionEntries.length) ? (
                        <button
                          aria-expanded={artifactDetailsExpanded}
                          className="reference-artifact-toggle"
                          onClick={(event) => {
                            event.preventDefault();
                            event.stopPropagation();
                            onDrillBackScoreLink("context", artifactComponentKey, {
                              artifactDetailExpanded: !artifactDetailsExpanded,
                              artifactLineDetailExpanded: null,
                              artifactLineDetailView: null,
                              artifactLineMicroView: null,
                              artifactLineNotePage: null,
                              artifactLineDetailHoverKey: null,
                              artifactLineDetailScrubStep: null,
                              artifactHoverKey: null,
                              historyMode: "replace",
                              subFocusKey: artifactSubFocusKey,
                            });
                          }}
                          type="button"
                        >
                          {artifactDetailsExpanded ? "Hide details" : "Show details"}
                        </button>
                      ) : null}
                    </div>
                  </div>
                  <p>{artifact.path}</p>
                  <p>
                    {artifact.is_directory ? "directory" : "file"}
                    {artifact.format ? ` / ${artifact.format}` : ""}
                    {artifact.exists ? "" : " / missing"}
                  </p>
                  {artifact.summary_source_path && artifact.summary_source_path !== artifact.path ? (
                    <p>Summary source: {artifact.summary_source_path}</p>
                  ) : null}
                  {artifactDetailsExpanded && summaryEntries.length ? (
                    <dl className="reference-artifact-summary">
                      {summaryEntries.map(([key, value]) => {
                        const artifactHoverKey = buildComparisonProvenanceArtifactSummaryHoverKey(
                          artifact.path,
                          key,
                        );
                        const isHovered = activeProvenanceArtifactHoverKey === artifactHoverKey;
                        return (
                          <div
                            className={`reference-artifact-summary-row ${isHovered ? "is-hovered" : ""}`.trim()}
                            key={`${artifact.path}-${key}`}
                            onBlur={() => {
                              if (!onDrillBackScoreLink || activeProvenanceArtifactHoverKey !== artifactHoverKey) {
                                return;
                              }
                              onDrillBackScoreLink("context", artifactComponentKey, {
                                artifactDetailExpanded: true,
                                artifactLineDetailExpanded: null,
                                artifactLineDetailView: null,
                                artifactLineMicroView: null,
                                artifactLineNotePage: null,
                                artifactLineDetailHoverKey: null,
                                artifactLineDetailScrubStep: null,
                                artifactHoverKey: null,
                                historyMode: "replace",
                                subFocusKey: artifactSubFocusKey,
                              });
                            }}
                            onFocus={() => {
                              if (!onDrillBackScoreLink || !artifactHasSelectedSubFocus) {
                                return;
                              }
                              onDrillBackScoreLink("context", artifactComponentKey, {
                                artifactDetailExpanded: true,
                                artifactLineDetailExpanded: null,
                                artifactLineDetailView: null,
                                artifactLineMicroView: null,
                                artifactLineNotePage: null,
                                artifactLineDetailHoverKey: null,
                                artifactLineDetailScrubStep: null,
                                artifactHoverKey,
                                historyMode: "replace",
                                subFocusKey: artifactSubFocusKey,
                              });
                            }}
                            onMouseEnter={() => {
                              if (!onDrillBackScoreLink || !artifactHasSelectedSubFocus) {
                                return;
                              }
                              onDrillBackScoreLink("context", artifactComponentKey, {
                                artifactDetailExpanded: true,
                                artifactLineDetailExpanded: null,
                                artifactLineDetailView: null,
                                artifactLineMicroView: null,
                                artifactLineNotePage: null,
                                artifactLineDetailHoverKey: null,
                                artifactLineDetailScrubStep: null,
                                artifactHoverKey,
                                historyMode: "replace",
                                subFocusKey: artifactSubFocusKey,
                              });
                            }}
                            onMouseLeave={() => {
                              if (!onDrillBackScoreLink || activeProvenanceArtifactHoverKey !== artifactHoverKey) {
                                return;
                              }
                              onDrillBackScoreLink("context", artifactComponentKey, {
                                artifactDetailExpanded: true,
                                artifactLineDetailExpanded: null,
                                artifactLineDetailView: null,
                                artifactLineMicroView: null,
                                artifactLineNotePage: null,
                                artifactLineDetailHoverKey: null,
                                artifactLineDetailScrubStep: null,
                                artifactHoverKey: null,
                                historyMode: "replace",
                                subFocusKey: artifactSubFocusKey,
                              });
                            }}
                            ref={registerArtifactHoverRef?.(panelRunId, artifactHoverKey)}
                            tabIndex={artifactHasSelectedSubFocus ? 0 : undefined}
                          >
                            <dt>{formatBenchmarkArtifactSummaryLabel(key)}</dt>
                            <dd>{value}</dd>
                          </div>
                        );
                      })}
                    </dl>
                  ) : null}
                  {artifactDetailsExpanded && sectionEntries.length ? (
                    <div className="reference-artifact-sections">
                      {sectionEntries.map(([key, lines]) => {
                        const sectionSubFocusKey = buildComparisonProvenanceArtifactSectionSubFocusKey(
                          artifact.path,
                          key,
                        );
                        const sectionLineHoverPrefix = `provenance-artifact-section-line:${encodeComparisonScoreLinkToken(
                          artifact.path,
                        )}:${encodeComparisonScoreLinkToken(key)}:`;
                        const sectionIsPressed =
                          linkedScoreSelection?.section === "context"
                          && linkedScoreSelection.componentKey === artifactComponentKey
                          && activeProvenanceSubFocusKey === sectionSubFocusKey;
                        return (
                        <article
                          className={`reference-artifact-section-card ${
                            activeProvenanceSubFocusKey === sectionSubFocusKey ? "is-subfocus" : ""
                          } ${
                            activeProvenanceArtifactHoverKey?.startsWith(sectionLineHoverPrefix)
                              ? "has-line-focus"
                              : ""
                          }`.trim()}
                          key={`${artifact.path}-${key}`}
                        >
                          <div className="reference-artifact-section-head">
                            {onDrillBackScoreLink ? (
                              <button
                                aria-label={`Trace ${formatBenchmarkArtifactSectionLabel(key)}`}
                                aria-pressed={sectionIsPressed}
                                className="reference-artifact-section-link"
                                onClick={(event) => {
                                  event.stopPropagation();
                                  onDrillBackScoreLink("context", artifactComponentKey, {
                                    artifactDetailExpanded: true,
                                    artifactLineDetailExpanded: null,
                                    artifactLineDetailView: null,
                                    artifactLineMicroView: null,
                                    artifactLineNotePage: null,
                                    artifactLineDetailHoverKey: null,
                                    artifactLineDetailScrubStep: null,
                                    artifactHoverKey: null,
                                    subFocusKey: sectionSubFocusKey,
                                  });
                                }}
                                onKeyDown={(event) => {
                                  if (event.key !== "Enter" && event.key !== " ") {
                                    return;
                                  }
                                  event.preventDefault();
                                  event.stopPropagation();
                                  onDrillBackScoreLink("context", artifactComponentKey, {
                                    artifactDetailExpanded: true,
                                    artifactLineDetailExpanded: null,
                                    artifactLineDetailView: null,
                                    artifactLineMicroView: null,
                                    artifactLineNotePage: null,
                                    artifactLineDetailHoverKey: null,
                                    artifactLineDetailScrubStep: null,
                                    artifactHoverKey: null,
                                    subFocusKey: sectionSubFocusKey,
                                  });
                                }}
                                ref={registerSubFocusRef?.(panelRunId, sectionSubFocusKey)}
                                type="button"
                              >
                                <strong>{formatBenchmarkArtifactSectionLabel(key)}</strong>
                              </button>
                            ) : (
                              <strong>{formatBenchmarkArtifactSectionLabel(key)}</strong>
                            )}
                          </div>
                          <div className="reference-artifact-section-body">
                            {lines.map((line, lineIndex) => {
                              const artifactHoverKey = buildComparisonProvenanceArtifactSectionLineHoverKey(
                                artifact.path,
                                key,
                                lineIndex,
                              );
                              const isLineFocused = activeProvenanceArtifactHoverKey === artifactHoverKey;
                              const lineDetailExpanded =
                                isLineFocused && activeProvenanceArtifactLineDetailExpanded === true;
                              const lineDetailView = activeProvenanceArtifactLineDetailView ?? "stats";
                              const lineMicroView = activeProvenanceArtifactLineMicroView ?? "structure";
                              const trimmedLine = line.trim();
                              const lineWordCount = trimmedLine ? trimmedLine.split(/\s+/).length : 0;
                              const lineDensity = line.length ? (lineWordCount / Math.max(line.length, 1)) * 100 : 0;
                              const previousLine = lineIndex > 0 ? lines[lineIndex - 1] : null;
                              const nextLine = lineIndex < lines.length - 1 ? lines[lineIndex + 1] : null;
                              const linePreview = trimmedLine
                                ? `${trimmedLine.slice(0, 42)}${trimmedLine.length > 42 ? "..." : ""}`
                                : "blank";
                              const previousPreview = previousLine?.trim()
                                ? `${previousLine.trim().slice(0, 36)}${previousLine.trim().length > 36 ? "..." : ""}`
                                : "none";
                              const nextPreview = nextLine?.trim()
                                ? `${nextLine.trim().slice(0, 36)}${nextLine.trim().length > 36 ? "..." : ""}`
                                : "none";
                              const lineDetailHoverPrefix = `provenance-artifact-line-detail:${encodeComparisonScoreLinkToken(
                                artifact.path,
                              )}:${encodeComparisonScoreLinkToken(key)}:${lineIndex}:`;
                              const buildLineDetailSignals = (
                                detailView: ProvenanceArtifactLineDetailView,
                                microView: ProvenanceArtifactLineMicroView,
                              ) => {
                                if (detailView === "stats") {
                                  return [
                                    {
                                      help: `Line ${lineIndex + 1} sits at ${Math.round(((lineIndex + 1) / Math.max(lines.length, 1)) * 100)}% through this section.`,
                                      key: "position",
                                      label: "Position",
                                      value: `L${lineIndex + 1} / ${lines.length}`,
                                    },
                                    microView === "signal"
                                      ? {
                                          help: `Density is ${lineDensity.toFixed(1)} words per 100 characters for this line.`,
                                          key: "density",
                                          label: "Density",
                                          value: `${lineDensity.toFixed(1)} / 100c`,
                                        }
                                      : {
                                          help: `The raw line spans ${line.length} characters across ${lineWordCount} words.`,
                                          key: "length",
                                          label: "Length",
                                          value: `${line.length}c / ${lineWordCount}w`,
                                        },
                                    microView === "note"
                                      ? {
                                          help: `The note lens starts from the current line preview: ${linePreview}.`,
                                          key: "preview",
                                          label: "Preview",
                                          value: linePreview,
                                        }
                                      : {
                                          help: trimmedLine
                                            ? "This line carries content-bearing tokens."
                                            : "This line is spacing-only and keeps structural separation.",
                                          key: "content_state",
                                          label: "State",
                                          value: trimmedLine ? "content-bearing" : "spacing-only",
                                        },
                                  ];
                                }
                                return [
                                  {
                                    help: `Previous sibling line: ${previousLine ?? "none"}`,
                                    key: "previous",
                                    label: "Prev sibling",
                                    value: previousPreview,
                                  },
                                  {
                                    help: `Next sibling line: ${nextLine ?? "none"}`,
                                    key: "next",
                                    label: "Next sibling",
                                    value: nextPreview,
                                  },
                                  microView === "note"
                                    ? {
                                        help: `Current context note is anchored in ${formatBenchmarkArtifactSectionLabel(key)} for ${shortenIdentifier(artifact.path)}.`,
                                        key: "section_anchor",
                                        label: "Section",
                                        value: formatBenchmarkArtifactSectionLabel(key),
                                      }
                                    : {
                                        help: `Path anchor ${shortenIdentifier(artifact.path)} in ${formatBenchmarkArtifactSectionLabel(key)}.`,
                                        key: "path_anchor",
                                        label: "Anchor",
                                        value: shortenIdentifier(artifact.path),
                                      },
                                ];
                              };
                              const resolveLineDetailSignalState = (
                                detailView: ProvenanceArtifactLineDetailView,
                                microView: ProvenanceArtifactLineMicroView,
                                preferredHoverKey: string | null,
                                preferredScrubStep: number | null,
                              ) => {
                                const signals = buildLineDetailSignals(detailView, microView).map((signal, index) => ({
                                  ...signal,
                                  hoverKey: buildComparisonProvenanceArtifactLineDetailHoverKey(
                                    artifact.path,
                                    key,
                                    lineIndex,
                                    signal.key,
                                  ),
                                  index,
                                }));
                                const hoverMatch =
                                  preferredHoverKey && preferredHoverKey.startsWith(lineDetailHoverPrefix)
                                    ? signals.find((signal) => signal.hoverKey === preferredHoverKey) ?? null
                                    : null;
                                const scrubMatch =
                                  preferredScrubStep !== null && preferredScrubStep !== undefined
                                    ? signals[
                                        Math.min(
                                          Math.max(preferredScrubStep, 0),
                                          Math.max(signals.length - 1, 0),
                                        )
                                      ] ?? null
                                    : null;
                                const focused = hoverMatch ?? scrubMatch ?? signals[0] ?? null;
                                return { focused, signals };
                              };
                              const detailNotes =
                                lineDetailView === "stats"
                                  ? [
                                      `Line ${lineIndex + 1} sits at ${Math.round(((lineIndex + 1) / Math.max(lines.length, 1)) * 100)}% through this section.`,
                                      trimmedLine
                                        ? `The line carries ${lineWordCount} words across ${line.length} characters.`
                                        : "The line is blank and only keeps structural spacing.",
                                      trimmedLine
                                        ? `Lead token preview: ${trimmedLine.slice(0, 48)}${trimmedLine.length > 48 ? "..." : ""}`
                                        : "No visible token preview is available for this blank line.",
                                    ]
                                  : [
                                      `Previous sibling: ${previousLine ?? "none"}`,
                                      `Next sibling: ${nextLine ?? "none"}`,
                                      `Section context: ${formatBenchmarkArtifactSectionLabel(key)} in ${shortenIdentifier(artifact.path)}`,
                                    ];
                              const lineNotePage = Math.min(
                                activeProvenanceArtifactLineNotePage ?? 0,
                                Math.max(detailNotes.length - 1, 0),
                              );
                              const resolvedLineDetailSignals = resolveLineDetailSignalState(
                                lineDetailView,
                                lineMicroView,
                                activeProvenanceArtifactLineDetailHoverKey,
                                activeProvenanceArtifactLineDetailScrubStep,
                              );
                              const detailSignals = resolvedLineDetailSignals.signals;
                              const focusedDetailSignal = resolvedLineDetailSignals.focused;
                              const lineDetailHoverKey = focusedDetailSignal?.hoverKey ?? null;
                              const lineDetailScrubStep = focusedDetailSignal?.index ?? null;
                              const buildNextLineDetailSelection = (
                                nextDetailView: ProvenanceArtifactLineDetailView,
                                nextMicroView: ProvenanceArtifactLineMicroView,
                                preferredHoverKey: string | null = lineDetailHoverKey,
                                preferredScrubStep: number | null = lineDetailScrubStep,
                              ) => {
                                const nextSignalState = resolveLineDetailSignalState(
                                  nextDetailView,
                                  nextMicroView,
                                  preferredHoverKey,
                                  preferredScrubStep,
                                );
                                return {
                                  artifactLineDetailHoverKey: nextSignalState.focused?.hoverKey ?? null,
                                  artifactLineDetailScrubStep: nextSignalState.focused?.index ?? null,
                                  artifactLineDetailView: nextDetailView,
                                  artifactLineMicroView: nextMicroView,
                                };
                              };
                              const preserveLineDetailState = isLineFocused
                                ? {
                                    artifactLineDetailExpanded:
                                      activeProvenanceArtifactLineDetailExpanded,
                                    artifactLineDetailView: activeProvenanceArtifactLineDetailView,
                                    artifactLineMicroView: activeProvenanceArtifactLineMicroView,
                                    artifactLineNotePage: activeProvenanceArtifactLineNotePage,
                                    artifactLineDetailHoverKey:
                                      activeProvenanceArtifactLineDetailExpanded === true
                                        ? lineDetailHoverKey
                                        : null,
                                    artifactLineDetailScrubStep:
                                      activeProvenanceArtifactLineDetailExpanded === true
                                        ? lineDetailScrubStep
                                        : null,
                                  }
                                : {
                                    artifactLineDetailExpanded: null,
                                    artifactLineDetailView: null,
                                    artifactLineMicroView: null,
                                    artifactLineNotePage: null,
                                    artifactLineDetailHoverKey: null,
                                    artifactLineDetailScrubStep: null,
                                  };
                              return (
                                <div
                                  className={`reference-artifact-section-line-wrap ${
                                    isLineFocused ? "is-active" : ""
                                  }`.trim()}
                                  key={`${artifact.path}-${key}-${lineIndex}-${line}`}
                                  onBlur={(event) => {
                                    if (
                                      !onDrillBackScoreLink
                                      || activeProvenanceArtifactHoverKey !== artifactHoverKey
                                      || (
                                        event.relatedTarget instanceof Node
                                        && event.currentTarget.contains(event.relatedTarget)
                                      )
                                    ) {
                                      return;
                                    }
                                    onDrillBackScoreLink("context", artifactComponentKey, {
                                      artifactDetailExpanded: true,
                                      artifactLineDetailExpanded:
                                        activeProvenanceArtifactLineDetailExpanded,
                                      artifactLineDetailView: activeProvenanceArtifactLineDetailView,
                                      artifactLineMicroView: activeProvenanceArtifactLineMicroView,
                                      artifactLineNotePage: activeProvenanceArtifactLineNotePage,
                                      artifactLineDetailHoverKey:
                                        activeProvenanceArtifactLineDetailExpanded === true
                                          ? lineDetailHoverKey
                                          : null,
                                      artifactLineDetailScrubStep:
                                        activeProvenanceArtifactLineDetailExpanded === true
                                          ? lineDetailScrubStep
                                          : null,
                                      artifactHoverKey: null,
                                      historyMode: "replace",
                                      subFocusKey: sectionSubFocusKey,
                                    });
                                  }}
                                  onFocus={() => {
                                    if (!onDrillBackScoreLink || activeProvenanceSubFocusKey !== sectionSubFocusKey) {
                                      return;
                                    }
                                    onDrillBackScoreLink("context", artifactComponentKey, {
                                      artifactDetailExpanded: true,
                                      artifactHoverKey,
                                      historyMode: "replace",
                                      subFocusKey: sectionSubFocusKey,
                                      ...preserveLineDetailState,
                                    });
                                  }}
                                  onMouseEnter={() => {
                                    if (!onDrillBackScoreLink || activeProvenanceSubFocusKey !== sectionSubFocusKey) {
                                      return;
                                    }
                                    onDrillBackScoreLink("context", artifactComponentKey, {
                                      artifactDetailExpanded: true,
                                      artifactHoverKey,
                                      historyMode: "replace",
                                      subFocusKey: sectionSubFocusKey,
                                      ...preserveLineDetailState,
                                    });
                                  }}
                                  onMouseLeave={() => {
                                    if (
                                      !onDrillBackScoreLink
                                      || activeProvenanceArtifactHoverKey !== artifactHoverKey
                                    ) {
                                      return;
                                    }
                                    onDrillBackScoreLink("context", artifactComponentKey, {
                                      artifactDetailExpanded: true,
                                      artifactLineDetailExpanded:
                                        activeProvenanceArtifactLineDetailExpanded,
                                      artifactLineDetailView: activeProvenanceArtifactLineDetailView,
                                      artifactLineMicroView: activeProvenanceArtifactLineMicroView,
                                      artifactLineNotePage: activeProvenanceArtifactLineNotePage,
                                      artifactLineDetailHoverKey:
                                        activeProvenanceArtifactLineDetailExpanded === true
                                          ? lineDetailHoverKey
                                          : null,
                                      artifactLineDetailScrubStep:
                                        activeProvenanceArtifactLineDetailExpanded === true
                                          ? lineDetailScrubStep
                                          : null,
                                      artifactHoverKey: null,
                                      historyMode: "replace",
                                      subFocusKey: sectionSubFocusKey,
                                    });
                                  }}
                                  ref={registerArtifactHoverRef?.(panelRunId, artifactHoverKey)}
                                >
                                  <p
                                    className={`reference-artifact-section-line ${
                                      isLineFocused ? "is-hovered" : ""
                                    }`.trim()}
                                    tabIndex={activeProvenanceSubFocusKey === sectionSubFocusKey ? 0 : undefined}
                                  >
                                    {line}
                                  </p>
                                  {isLineFocused ? (
                                    <div className="reference-artifact-section-line-tools">
                                      <button
                                        aria-expanded={lineDetailExpanded}
                                        className="reference-artifact-line-toggle"
                                        onClick={(event) => {
                                          event.preventDefault();
                                          event.stopPropagation();
                                          const nextLineDetailExpanded = !lineDetailExpanded;
                                          const nextLineDetailSelection = buildNextLineDetailSelection(
                                            activeProvenanceArtifactLineDetailView ?? "stats",
                                            activeProvenanceArtifactLineMicroView ?? "structure",
                                          );
                                          onDrillBackScoreLink?.("context", artifactComponentKey, {
                                            artifactDetailExpanded: true,
                                            artifactLineDetailExpanded: nextLineDetailExpanded,
                                            artifactLineDetailView: nextLineDetailSelection.artifactLineDetailView,
                                            artifactLineMicroView: nextLineDetailSelection.artifactLineMicroView,
                                            artifactLineNotePage: nextLineDetailExpanded
                                              ? (activeProvenanceArtifactLineNotePage ?? 0)
                                              : null,
                                            artifactLineDetailHoverKey: nextLineDetailExpanded
                                              ? nextLineDetailSelection.artifactLineDetailHoverKey
                                              : null,
                                            artifactLineDetailScrubStep: nextLineDetailExpanded
                                              ? nextLineDetailSelection.artifactLineDetailScrubStep
                                              : null,
                                            artifactHoverKey,
                                            historyMode: "replace",
                                            subFocusKey: sectionSubFocusKey,
                                          });
                                        }}
                                        type="button"
                                      >
                                        {lineDetailExpanded ? "Hide line detail" : "Show line detail"}
                                      </button>
                                      {lineDetailExpanded ? (
                                        <>
                                          <div className="reference-artifact-line-view-switch">
                                            {(["stats", "context"] as const).map((view) => (
                                              <button
                                                aria-pressed={lineDetailView === view}
                                                className={`reference-artifact-line-view-chip ${
                                                  lineDetailView === view ? "is-active" : ""
                                                }`.trim()}
                                                key={view}
                                                onClick={(event) => {
                                                  event.preventDefault();
                                                  event.stopPropagation();
                                                  const nextLineDetailSelection = buildNextLineDetailSelection(
                                                    view,
                                                    activeProvenanceArtifactLineMicroView ?? "structure",
                                                  );
                                                  onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                    artifactDetailExpanded: true,
                                                    artifactLineDetailExpanded: true,
                                                    artifactLineDetailView: nextLineDetailSelection.artifactLineDetailView,
                                                    artifactLineMicroView: nextLineDetailSelection.artifactLineMicroView,
                                                    artifactLineNotePage: activeProvenanceArtifactLineNotePage ?? 0,
                                                    artifactLineDetailHoverKey:
                                                      nextLineDetailSelection.artifactLineDetailHoverKey,
                                                    artifactLineDetailScrubStep:
                                                      nextLineDetailSelection.artifactLineDetailScrubStep,
                                                    artifactHoverKey,
                                                    historyMode: "replace",
                                                    subFocusKey: sectionSubFocusKey,
                                                  });
                                                }}
                                                type="button"
                                              >
                                                {view === "stats" ? "Stats" : "Context"}
                                              </button>
                                            ))}
                                          </div>
                                          <div className="reference-artifact-line-view-switch">
                                            {(["structure", "signal", "note"] as const).map((view) => (
                                              <button
                                                aria-pressed={lineMicroView === view}
                                                className={`reference-artifact-line-view-chip ${
                                                  lineMicroView === view ? "is-active" : ""
                                                }`.trim()}
                                                key={view}
                                                onClick={(event) => {
                                                  event.preventDefault();
                                                  event.stopPropagation();
                                                  const nextLineDetailSelection = buildNextLineDetailSelection(
                                                    lineDetailView,
                                                    view,
                                                  );
                                                  onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                    artifactDetailExpanded: true,
                                                    artifactLineDetailExpanded: true,
                                                    artifactLineDetailView: nextLineDetailSelection.artifactLineDetailView,
                                                    artifactLineMicroView: nextLineDetailSelection.artifactLineMicroView,
                                                    artifactLineNotePage: lineNotePage,
                                                    artifactLineDetailHoverKey:
                                                      nextLineDetailSelection.artifactLineDetailHoverKey,
                                                    artifactLineDetailScrubStep:
                                                      nextLineDetailSelection.artifactLineDetailScrubStep,
                                                    artifactHoverKey,
                                                    historyMode: "replace",
                                                    subFocusKey: sectionSubFocusKey,
                                                  });
                                                }}
                                                type="button"
                                              >
                                                {view === "structure"
                                                  ? "Structure"
                                                  : view === "signal"
                                                    ? "Signal"
                                                    : "Note"}
                                              </button>
                                            ))}
                                          </div>
                                          <div className="reference-artifact-line-detail">
                                            {detailSignals.length ? (
                                              <>
                                                <div className="reference-artifact-line-scrub">
                                                  <button
                                                    className="reference-artifact-line-note-button"
                                                    disabled={!focusedDetailSignal || lineDetailScrubStep === 0}
                                                    onClick={(event) => {
                                                      if (!focusedDetailSignal || lineDetailScrubStep === null) {
                                                        return;
                                                      }
                                                      event.preventDefault();
                                                      event.stopPropagation();
                                                      const previousSignal =
                                                        detailSignals[Math.max(0, lineDetailScrubStep - 1)] ?? null;
                                                      if (!previousSignal) {
                                                        return;
                                                      }
                                                      onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                        artifactDetailExpanded: true,
                                                        artifactLineDetailExpanded: true,
                                                        artifactLineDetailView: lineDetailView,
                                                        artifactLineMicroView: lineMicroView,
                                                        artifactLineNotePage: lineNotePage,
                                                        artifactLineDetailHoverKey: previousSignal.hoverKey,
                                                        artifactLineDetailScrubStep: previousSignal.index,
                                                        artifactHoverKey,
                                                        historyMode: "replace",
                                                        subFocusKey: sectionSubFocusKey,
                                                      });
                                                    }}
                                                    type="button"
                                                  >
                                                    Prev detail
                                                  </button>
                                                  <span className="reference-artifact-line-scrub-indicator">
                                                    {focusedDetailSignal
                                                      ? `Inspect ${focusedDetailSignal.label} · ${focusedDetailSignal.index + 1} / ${detailSignals.length}`
                                                      : "No detail signals"}
                                                  </span>
                                                  <button
                                                    className="reference-artifact-line-note-button"
                                                    disabled={
                                                      !focusedDetailSignal
                                                      || lineDetailScrubStep === null
                                                      || lineDetailScrubStep >= detailSignals.length - 1
                                                    }
                                                    onClick={(event) => {
                                                      if (!focusedDetailSignal || lineDetailScrubStep === null) {
                                                        return;
                                                      }
                                                      event.preventDefault();
                                                      event.stopPropagation();
                                                      const nextSignal =
                                                        detailSignals[
                                                          Math.min(detailSignals.length - 1, lineDetailScrubStep + 1)
                                                        ] ?? null;
                                                      if (!nextSignal) {
                                                        return;
                                                      }
                                                      onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                        artifactDetailExpanded: true,
                                                        artifactLineDetailExpanded: true,
                                                        artifactLineDetailView: lineDetailView,
                                                        artifactLineMicroView: lineMicroView,
                                                        artifactLineNotePage: lineNotePage,
                                                        artifactLineDetailHoverKey: nextSignal.hoverKey,
                                                        artifactLineDetailScrubStep: nextSignal.index,
                                                        artifactHoverKey,
                                                        historyMode: "replace",
                                                        subFocusKey: sectionSubFocusKey,
                                                      });
                                                    }}
                                                    type="button"
                                                  >
                                                    Next detail
                                                  </button>
                                                </div>
                                                <div className="reference-artifact-line-signal-grid">
                                                  {detailSignals.map((signal) => (
                                                    <button
                                                      aria-pressed={lineDetailHoverKey === signal.hoverKey}
                                                      className={`reference-artifact-line-signal-chip ${
                                                        lineDetailHoverKey === signal.hoverKey ? "is-active" : ""
                                                      }`.trim()}
                                                      key={signal.hoverKey}
                                                      onClick={(event) => {
                                                        event.preventDefault();
                                                        event.stopPropagation();
                                                        onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                          artifactDetailExpanded: true,
                                                          artifactLineDetailExpanded: true,
                                                          artifactLineDetailView: lineDetailView,
                                                          artifactLineMicroView: lineMicroView,
                                                          artifactLineNotePage: lineNotePage,
                                                          artifactLineDetailHoverKey: signal.hoverKey,
                                                          artifactLineDetailScrubStep: signal.index,
                                                          artifactHoverKey,
                                                          historyMode: "replace",
                                                          subFocusKey: sectionSubFocusKey,
                                                        });
                                                      }}
                                                      onFocus={() => {
                                                        onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                          artifactDetailExpanded: true,
                                                          artifactLineDetailExpanded: true,
                                                          artifactLineDetailView: lineDetailView,
                                                          artifactLineMicroView: lineMicroView,
                                                          artifactLineNotePage: lineNotePage,
                                                          artifactLineDetailHoverKey: signal.hoverKey,
                                                          artifactLineDetailScrubStep: signal.index,
                                                          artifactHoverKey,
                                                          historyMode: "replace",
                                                          subFocusKey: sectionSubFocusKey,
                                                        });
                                                      }}
                                                      onMouseEnter={() => {
                                                        onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                          artifactDetailExpanded: true,
                                                          artifactLineDetailExpanded: true,
                                                          artifactLineDetailView: lineDetailView,
                                                          artifactLineMicroView: lineMicroView,
                                                          artifactLineNotePage: lineNotePage,
                                                          artifactLineDetailHoverKey: signal.hoverKey,
                                                          artifactLineDetailScrubStep: signal.index,
                                                          artifactHoverKey,
                                                          historyMode: "replace",
                                                          subFocusKey: sectionSubFocusKey,
                                                        });
                                                      }}
                                                      type="button"
                                                    >
                                                      <strong>{signal.label}</strong>
                                                      <span>{signal.value}</span>
                                                    </button>
                                                  ))}
                                                </div>
                                                {focusedDetailSignal ? (
                                                  <div className="reference-artifact-line-inline-tooltip">
                                                    <span className="reference-artifact-line-inline-tooltip-label">
                                                      Last inspected detail
                                                    </span>
                                                    <strong>{focusedDetailSignal.label}</strong>
                                                    <span>{focusedDetailSignal.help}</span>
                                                  </div>
                                                ) : null}
                                              </>
                                            ) : null}
                                            {lineMicroView === "note" ? (
                                              <>
                                                <div className="reference-artifact-line-note-card">
                                                  <span>{detailNotes[lineNotePage]}</span>
                                                </div>
                                                {detailNotes.length > 1 ? (
                                                  <div className="reference-artifact-line-note-pager">
                                                    <button
                                                      className="reference-artifact-line-note-button"
                                                      disabled={lineNotePage === 0}
                                                      onClick={(event) => {
                                                        event.preventDefault();
                                                        event.stopPropagation();
                                                        onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                          artifactDetailExpanded: true,
                                                          artifactLineDetailExpanded: true,
                                                          artifactLineDetailView: lineDetailView,
                                                          artifactLineMicroView: "note",
                                                          artifactLineNotePage: Math.max(0, lineNotePage - 1),
                                                          artifactLineDetailHoverKey: lineDetailHoverKey,
                                                          artifactLineDetailScrubStep: lineDetailScrubStep,
                                                          artifactHoverKey,
                                                          historyMode: "replace",
                                                          subFocusKey: sectionSubFocusKey,
                                                        });
                                                      }}
                                                      type="button"
                                                    >
                                                      Prev note
                                                    </button>
                                                    <span className="reference-artifact-line-note-indicator">
                                                      {`Note ${lineNotePage + 1} / ${detailNotes.length}`}
                                                    </span>
                                                    <button
                                                      className="reference-artifact-line-note-button"
                                                      disabled={lineNotePage >= detailNotes.length - 1}
                                                      onClick={(event) => {
                                                        event.preventDefault();
                                                        event.stopPropagation();
                                                        onDrillBackScoreLink?.("context", artifactComponentKey, {
                                                          artifactDetailExpanded: true,
                                                          artifactLineDetailExpanded: true,
                                                          artifactLineDetailView: lineDetailView,
                                                          artifactLineMicroView: "note",
                                                          artifactLineNotePage: Math.min(
                                                            detailNotes.length - 1,
                                                            lineNotePage + 1,
                                                          ),
                                                          artifactLineDetailHoverKey: lineDetailHoverKey,
                                                          artifactLineDetailScrubStep: lineDetailScrubStep,
                                                          artifactHoverKey,
                                                          historyMode: "replace",
                                                          subFocusKey: sectionSubFocusKey,
                                                        });
                                                      }}
                                                      type="button"
                                                    >
                                                      Next note
                                                    </button>
                                                  </div>
                                                ) : null}
                                              </>
                                            ) : lineDetailView === "stats" && lineMicroView === "signal" ? (
                                              <>
                                                <span>{`Line density ${lineDensity.toFixed(1)} words / 100 chars`}</span>
                                                <span>{`Trimmed length ${trimmedLine.length} / raw ${line.length}`}</span>
                                                <span>{trimmedLine ? "content-bearing line" : "spacing-only line"}</span>
                                              </>
                                            ) : lineDetailView === "stats" ? (
                                              <>
                                                <span>{`Line ${lineIndex + 1} of ${lines.length}`}</span>
                                                <span>{`${line.length} chars / ${lineWordCount} words`}</span>
                                                <span>{trimmedLine ? "non-empty content" : "blank content"}</span>
                                              </>
                                            ) : lineMicroView === "signal" ? (
                                              <>
                                                <span>{`Prev sibling present: ${previousLine ? "yes" : "no"}`}</span>
                                                <span>{`Next sibling present: ${nextLine ? "yes" : "no"}`}</span>
                                                <span>{`Path anchor ${shortenIdentifier(artifact.path)}`}</span>
                                              </>
                                            ) : (
                                              <>
                                                <span>{`Prev: ${previousLine ?? "none"}`}</span>
                                                <span>{`Next: ${nextLine ?? "none"}`}</span>
                                                <span>{`Section ${formatBenchmarkArtifactSectionLabel(key)}`}</span>
                                              </>
                                            )}
                                          </div>
                                        </>
                                      ) : null}
                                    </div>
                                  ) : null}
                                </div>
                              );
                            })}
                          </div>
                        </article>
                      );})}
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        ) : (
          renderProvenanceCopyLine({
            children: `Artifacts: ${artifactPaths.length ? artifactPaths.join(" | ") : "none recorded"}`,
            componentKey: "provenance_richness",
            highlighted: highlightArtifacts,
            subFocusKey: buildComparisonProvenanceLineSubFocusKey("provenance_richness"),
            section: "context",
          })
        )}
      </div>
    </section>
  );
}

export function RunStrategySnapshot({
  linkedScore,
  onDrillBackScoreLink,
  panelRunId,
  registerSubFocusRef,
  showSemanticCatalogContext = true,
  strategy,
}: {
  linkedScore: (ComparisonScoreLinkTarget & { role: ComparisonScoreLinkedRunRole }) | null;
  onDrillBackScoreLink?: (
    section: ComparisonScoreSection,
    componentKey: string,
    options?: ComparisonScoreDrillBackOptions,
  ) => void;
  panelRunId?: string;
  registerSubFocusRef?: (runId: string, subFocusKey: string) => (node: HTMLElement | null) => void;
  showSemanticCatalogContext?: boolean;
  strategy: NonNullable<Run["provenance"]["strategy"]>;
}) {
  const strategyKindSubFocusKey = buildComparisonRunListLineSubFocusKey("strategy_kind");
  const executionModelSubFocusKey = buildComparisonRunListLineSubFocusKey("execution_model");
  const parameterContractSubFocusKey = buildComparisonRunListLineSubFocusKey("parameter_contract");
  const semanticSourceSubFocusKey = buildComparisonRunListLineSubFocusKey("semantic_source");
  const operatorNotesSubFocusKey = buildComparisonRunListLineSubFocusKey("operator_notes");
  const supportedTimeframesSubFocusKey = buildComparisonRunListLineSubFocusKey("strategy_supported_timeframes");
  const versionLineageSubFocusKey = buildComparisonRunListLineSubFocusKey("strategy_version_lineage");
  const resolvedParamsSubFocusKey = buildComparisonRunListLineSubFocusKey("strategy_resolved_params");
  const requestedParamsSubFocusKey = buildComparisonRunListLineSubFocusKey("strategy_requested_params");
  const strategyEntrypointSubFocusKey = buildComparisonRunListLineSubFocusKey("strategy_entrypoint");
  const strategyRegisteredSubFocusKey = buildComparisonRunListLineSubFocusKey("strategy_registered");
  const activeRunListSubFocusKey =
    linkedScore?.source === "run_list"
      ? linkedScore.subFocusKey
      : null;
  const highlightStrategyKind =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["strategy_kind", "vocabulary"], "semantics");
  const highlightExecutionModel =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["execution_model", "vocabulary"], "semantics");
  const highlightParameterContract =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["parameter_contract", "vocabulary"], "semantics");
  const highlightSourceDescriptor =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["source_descriptor", "vocabulary"], "semantics");
  const highlightOperatorNotes =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["vocabulary"], "semantics");
  const highlightVocabulary = highlightOperatorNotes;
  const highlightPanel =
    highlightStrategyKind
    || highlightExecutionModel
    || highlightParameterContract
    || highlightSourceDescriptor
    || highlightOperatorNotes;
  const highlightOrigin =
    linkedScore?.source === "run_list"
    && linkedScore.originRunId === panelRunId;
  const renderSemanticTile = (
    label: string,
    value: string,
    componentKey: string,
    highlighted: boolean,
    subFocusKey: string,
  ) => {
    const isPressed =
      linkedScore?.section === "semantics"
      && linkedScore.componentKey === componentKey
      && activeRunListSubFocusKey === subFocusKey;
    const className = `metric-tile comparison-run-summary-metric ${
      highlighted ? "comparison-linked-panel" : ""
    } ${isPressed ? "comparison-linked-panel-origin comparison-linked-subfocus is-active" : ""}`.trim();
    if (!onDrillBackScoreLink || !panelRunId) {
      return (
        <div className={className}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      );
    }
    return (
      <button
        aria-pressed={isPressed}
        className={`${className} comparison-run-summary-metric-button`.trim()}
        onClick={() =>
          onDrillBackScoreLink("semantics", componentKey, {
            subFocusKey,
          })
        }
        ref={registerSubFocusRef?.(panelRunId, subFocusKey)}
        type="button"
      >
        <span>{label}</span>
        <strong>{value}</strong>
      </button>
    );
  };
  const renderSemanticLine = (
    children: string,
    componentKey: string,
    highlighted: boolean,
    subFocusKey: string,
  ) => {
    const isPressed =
      linkedScore?.section === "semantics"
      && linkedScore.componentKey === componentKey
      && activeRunListSubFocusKey === subFocusKey;
    const className = `run-strategy-copy-link ${
      highlighted ? "comparison-linked-copy" : ""
    } ${
      isPressed ? "comparison-linked-copy-origin comparison-linked-subfocus" : ""
    }`.trim();
    if (!onDrillBackScoreLink || !panelRunId) {
      return <p className={className}>{children}</p>;
    }
    return (
      <button
        aria-pressed={isPressed}
        className={`${className} comparison-run-card-link comparison-drillback-target`.trim()}
        onClick={() =>
          onDrillBackScoreLink("semantics", componentKey, {
            subFocusKey,
          })
        }
        ref={registerSubFocusRef?.(panelRunId, subFocusKey)}
        type="button"
      >
        {children}
      </button>
    );
  };
  return (
    <section
      className={`run-strategy ${highlightPanel ? "comparison-linked-panel" : ""} ${
        linkedScore?.role === "target" ? "comparison-linked-panel-target" : ""
      } ${linkedScore?.role === "baseline" ? "comparison-linked-panel-baseline" : ""} ${
        highlightOrigin ? "comparison-linked-panel-origin" : ""
      }`.trim()}
    >
      <div className="run-strategy-head">
        <span>Strategy snapshot</span>
        <strong>{formatLaneLabel(strategy.runtime)}</strong>
      </div>
      <div className="run-strategy-grid">
        <Metric label="Version" value={strategy.version} />
        <Metric label="Lifecycle" value={strategy.lifecycle.stage} />
        {showSemanticCatalogContext
          ? renderSemanticTile(
              "Semantic kind",
              strategy.catalog_semantics.strategy_kind,
              "strategy_kind",
              highlightStrategyKind,
              strategyKindSubFocusKey,
            )
          : null}
        <Metric label="Warmup" value={`${strategy.warmup.required_bars} bars`} />
        <Metric label="TFs" value={strategy.warmup.timeframes.join(", ")} />
      </div>
      <div className="run-strategy-copy">
        {renderSemanticLine(
          `Supported timeframes: ${strategy.supported_timeframes.join(", ") || "n/a"}`,
          "vocabulary",
          highlightVocabulary,
          supportedTimeframesSubFocusKey,
        )}
        {renderSemanticLine(
          `Version lineage: ${formatVersionLineage(strategy.version_lineage, strategy.version)}`,
          "vocabulary",
          highlightVocabulary,
          versionLineageSubFocusKey,
        )}
        {showSemanticCatalogContext && strategy.catalog_semantics.execution_model ? (
          renderSemanticLine(
            `Execution model: ${strategy.catalog_semantics.execution_model}`,
            "execution_model",
            highlightExecutionModel,
            executionModelSubFocusKey,
          )
        ) : null}
        {showSemanticCatalogContext && strategy.catalog_semantics.parameter_contract ? (
          renderSemanticLine(
            `Parameter contract: ${strategy.catalog_semantics.parameter_contract}`,
            "parameter_contract",
            highlightParameterContract,
            parameterContractSubFocusKey,
          )
        ) : null}
        {showSemanticCatalogContext && strategy.catalog_semantics.source_descriptor ? (
          renderSemanticLine(
            `Source: ${strategy.catalog_semantics.source_descriptor}`,
            "source_descriptor",
            highlightSourceDescriptor,
            semanticSourceSubFocusKey,
          )
        ) : null}
        {renderSemanticLine(
          `Resolved params: ${formatParameterMap(strategy.parameter_snapshot.resolved)}`,
          "parameter_contract",
          highlightParameterContract,
          resolvedParamsSubFocusKey,
        )}
        {renderSemanticLine(
          `Requested params: ${formatParameterMap(strategy.parameter_snapshot.requested)}`,
          "parameter_contract",
          highlightParameterContract,
          requestedParamsSubFocusKey,
        )}
        {strategy.entrypoint
          ? renderSemanticLine(
              `Entrypoint: ${strategy.entrypoint}`,
              "source_descriptor",
              highlightSourceDescriptor,
              strategyEntrypointSubFocusKey,
            )
          : null}
        {strategy.lifecycle.registered_at ? (
          renderSemanticLine(
            `Registered: ${formatTimestamp(strategy.lifecycle.registered_at)}`,
            "vocabulary",
            highlightVocabulary,
            strategyRegisteredSubFocusKey,
          )
        ) : null}
        {showSemanticCatalogContext && strategy.catalog_semantics.operator_notes.length ? (
          renderSemanticLine(
            `Operator notes: ${strategy.catalog_semantics.operator_notes.join(" | ")}`,
            "vocabulary",
            highlightOperatorNotes,
            operatorNotesSubFocusKey,
          )
        ) : null}
      </div>
    </section>
  );
}

export function RunRuntimeSessionSummary({
  linkedScore,
  onDrillBackScoreLink,
  panelRunId,
  registerSubFocusRef,
  runtimeSession,
}: {
  linkedScore: (ComparisonScoreLinkTarget & { role: ComparisonScoreLinkedRunRole }) | null;
  onDrillBackScoreLink?: (
    section: ComparisonScoreSection,
    componentKey: string,
    options?: ComparisonScoreDrillBackOptions,
  ) => void;
  panelRunId?: string;
  registerSubFocusRef?: (runId: string, subFocusKey: string) => (node: HTMLElement | null) => void;
  runtimeSession: NonNullable<Run["provenance"]["runtime_session"]>;
}) {
  const runtimeSessionSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_session");
  const runtimeStateSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_state");
  const runtimeTicksSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_ticks");
  const runtimeRecoveriesSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_recoveries");
  const runtimeHeartbeatSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_heartbeat");
  const runtimePrimedBarsSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_primed_bars");
  const runtimeStartedSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_started");
  const runtimeLastHeartbeatSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_last_heartbeat");
  const runtimeLastProcessedSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_last_processed_candle");
  const runtimeLastSeenSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_last_seen_candle");
  const runtimeLastRecoverySubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_last_recovery");
  const runtimeRecoveryReasonSubFocusKey = buildComparisonRunListLineSubFocusKey("runtime_recovery_reason");
  const highlightPanel =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["provenance_richness"], "context");
  const isRuntimeSubFocusOrigin = (subFocusKey: string) =>
    linkedScore?.source === "run_list"
    && linkedScore.originRunId === panelRunId
    && linkedScore.subFocusKey === subFocusKey;
  const highlightOrigin =
    linkedScore?.source === "run_list"
    && linkedScore.originRunId === panelRunId
    && Boolean(linkedScore.subFocusKey?.startsWith("run-list-line:runtime_"));
  const renderRuntimeMetric = (label: string, value: string, subFocusKey: string) => {
    if (!onDrillBackScoreLink || !panelRunId) {
      return <Metric label={label} value={value} />;
    }
    return (
      <Metric
        buttonRef={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        className={highlightPanel ? "comparison-linked-panel" : ""}
        interactivePressed={isRuntimeSubFocusOrigin(subFocusKey)}
        label={label}
        onClick={() =>
          onDrillBackScoreLink("context", "provenance_richness", {
            subFocusKey,
          })
        }
        value={value}
      />
    );
  };
  const renderRuntimeLine = (children: string, subFocusKey: string) => {
    if (!onDrillBackScoreLink || !panelRunId) {
      return <p className="run-lineage-copy-link">{children}</p>;
    }
    return (
      <button
        aria-pressed={isRuntimeSubFocusOrigin(subFocusKey)}
        className={`run-lineage-copy-link comparison-run-card-link comparison-drillback-target ${
          highlightPanel ? "comparison-linked-copy" : ""
        } ${isRuntimeSubFocusOrigin(subFocusKey) ? "comparison-linked-copy-origin comparison-linked-subfocus" : ""}`.trim()}
        onClick={() =>
          onDrillBackScoreLink("context", "provenance_richness", {
            subFocusKey,
          })
        }
        ref={registerSubFocusRef?.(panelRunId, subFocusKey)}
        type="button"
      >
        {children}
      </button>
    );
  };
  return (
    <section
      className={`run-lineage ${highlightPanel ? "comparison-linked-panel" : ""} ${
        linkedScore?.role === "target" ? "comparison-linked-panel-target" : ""
      } ${linkedScore?.role === "baseline" ? "comparison-linked-panel-baseline" : ""} ${
        highlightOrigin ? "comparison-linked-panel-origin" : ""
      }`.trim()}
    >
      <div className="run-lineage-head">
        <span>Runtime session</span>
        <strong>{runtimeSession.worker_kind}</strong>
      </div>
      <div className="run-lineage-grid">
        {renderRuntimeMetric("State", runtimeSession.lifecycle_state, runtimeStateSubFocusKey)}
        {renderRuntimeMetric("Ticks", String(runtimeSession.processed_tick_count), runtimeTicksSubFocusKey)}
        {renderRuntimeMetric("Recoveries", String(runtimeSession.recovery_count), runtimeRecoveriesSubFocusKey)}
        {renderRuntimeMetric(
          "Heartbeat",
          `${runtimeSession.heartbeat_interval_seconds}s / ${runtimeSession.heartbeat_timeout_seconds}s`,
          runtimeHeartbeatSubFocusKey,
        )}
        {renderRuntimeMetric("Primed bars", String(runtimeSession.primed_candle_count), runtimePrimedBarsSubFocusKey)}
      </div>
      <div className="run-lineage-copy">
        {renderRuntimeLine(`Session: ${runtimeSession.session_id}`, runtimeSessionSubFocusKey)}
        {renderRuntimeLine(`Started: ${formatTimestamp(runtimeSession.started_at)}`, runtimeStartedSubFocusKey)}
        {renderRuntimeLine(
          `Last heartbeat: ${formatTimestamp(runtimeSession.last_heartbeat_at)}`,
          runtimeLastHeartbeatSubFocusKey,
        )}
        {renderRuntimeLine(
          `Last processed candle: ${formatTimestamp(runtimeSession.last_processed_candle_at)}`,
          runtimeLastProcessedSubFocusKey,
        )}
        {renderRuntimeLine(
          `Last seen candle: ${formatTimestamp(runtimeSession.last_seen_candle_at)}`,
          runtimeLastSeenSubFocusKey,
        )}
        {renderRuntimeLine(
          `Last recovery: ${formatTimestamp(runtimeSession.last_recovered_at)}`,
          runtimeLastRecoverySubFocusKey,
        )}
        {renderRuntimeLine(
          `Recovery reason: ${runtimeSession.last_recovery_reason ?? "none"}`,
          runtimeRecoveryReasonSubFocusKey,
        )}
      </div>
    </section>
  );
}

export function RunOrderLifecycleSummary({
  eligibilityContract,
  linkedScore,
  onDrillBackScoreLink,
  orders,
  orderActionBoundaryEnabled = false,
  orderControls,
  panelRunId,
  registerSubFocusRef,
}: {
  eligibilityContract?: RunListBoundaryContract | null;
  linkedScore: (ComparisonScoreLinkTarget & { role: ComparisonScoreLinkedRunRole }) | null;
  onDrillBackScoreLink?: (
    section: ComparisonScoreSection,
    componentKey: string,
    options?: ComparisonScoreDrillBackOptions,
  ) => void;
  orders: Run["orders"];
  orderActionBoundaryEnabled?: boolean;
  orderControls?: RunOrderControls | null;
  panelRunId?: string;
  registerSubFocusRef?: (runId: string, subFocusKey: string) => (node: HTMLElement | null) => void;
}) {
  const openCount = orders.filter((order) => order.status === "open").length;
  const partialCount = orders.filter((order) => order.status === "partially_filled").length;
  const filledCount = orders.filter((order) => order.status === "filled").length;
  const canceledCount = orders.filter((order) => order.status === "canceled").length;
  const rejectedCount = orders.filter((order) => order.status === "rejected").length;
  const latestSyncAt =
    orders
      .map((order) => order.last_synced_at ?? order.updated_at ?? null)
      .filter((value): value is string => Boolean(value))
      .sort()
      .at(-1) ?? null;
  const previewOrders = [...orders]
    .sort((left, right) => {
      const leftActive = left.status === "open" || left.status === "partially_filled";
      const rightActive = right.status === "open" || right.status === "partially_filled";
      if (leftActive !== rightActive) {
        return leftActive ? -1 : 1;
      }
      const leftTimestamp = left.last_synced_at ?? left.updated_at ?? left.created_at;
      const rightTimestamp = right.last_synced_at ?? right.updated_at ?? right.created_at;
      return rightTimestamp.localeCompare(leftTimestamp);
    })
    .slice(0, 4);
  const highlightPanel =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["trade_count"], "metrics");
  const orderOpenSubFocusKey = buildComparisonRunListLineSubFocusKey("order_open");
  const orderPartialSubFocusKey = buildComparisonRunListLineSubFocusKey("order_partial");
  const orderFilledSubFocusKey = buildComparisonRunListLineSubFocusKey("order_filled");
  const orderCanceledSubFocusKey = buildComparisonRunListLineSubFocusKey("order_canceled");
  const orderRejectedSubFocusKey = buildComparisonRunListLineSubFocusKey("order_rejected");
  const orderSyncSubFocusKey = buildComparisonRunListLineSubFocusKey("order_sync");
  const isOrderSubFocusOrigin = (subFocusKey: string) =>
    linkedScore?.source === "run_list"
    && linkedScore.originRunId === panelRunId
    && linkedScore.subFocusKey === subFocusKey;
  const highlightOrigin = [
    orderOpenSubFocusKey,
    orderPartialSubFocusKey,
    orderFilledSubFocusKey,
    orderCanceledSubFocusKey,
    orderRejectedSubFocusKey,
    orderSyncSubFocusKey,
  ].some(isOrderSubFocusOrigin);
  const renderOrderMetric = (label: string, value: string, subFocusKey: string) => {
    if (!onDrillBackScoreLink || !panelRunId) {
      return <Metric label={label} value={value} />;
    }
    return (
      <Metric
        buttonRef={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        className={highlightPanel ? "comparison-linked-panel" : ""}
        interactivePressed={isOrderSubFocusOrigin(subFocusKey)}
        label={label}
        onClick={() =>
          onDrillBackScoreLink("metrics", "trade_count", {
            subFocusKey,
          })
        }
        value={value}
      />
    );
  };
  const renderOrderCopyLine = (children: string, subFocusKey: string) => {
    if (!onDrillBackScoreLink || !panelRunId) {
      return <p className="run-lineage-copy-link">{children}</p>;
    }
    return (
      <button
        aria-pressed={isOrderSubFocusOrigin(subFocusKey)}
        className={`run-lineage-copy-link comparison-run-card-link comparison-drillback-target ${
          highlightPanel ? "comparison-linked-copy" : ""
        } ${isOrderSubFocusOrigin(subFocusKey) ? "comparison-linked-copy-origin comparison-linked-subfocus" : ""}`.trim()}
        onClick={() =>
          onDrillBackScoreLink("metrics", "trade_count", {
            subFocusKey,
          })
        }
        ref={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        type="button"
      >
        {children}
      </button>
    );
  };
  const renderOrderPreviewMetric = (
    orderId: string,
    label: string,
    value: string,
    fieldKey: string,
  ) => {
    const subFocusKey = buildComparisonRunListOrderPreviewSubFocusKey(orderId, fieldKey);
    if (!onDrillBackScoreLink || !panelRunId) {
      return <Metric label={label} value={value} />;
    }
    return (
      <Metric
        buttonRef={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        className={highlightPanel ? "comparison-linked-panel" : ""}
        interactivePressed={isOrderSubFocusOrigin(subFocusKey)}
        label={label}
        onClick={() =>
          onDrillBackScoreLink("metrics", "trade_count", {
            subFocusKey,
          })
        }
        value={value}
      />
    );
  };
  const renderOrderPreviewLine = (
    orderId: string,
    children: string,
    fieldKey: string,
  ) => {
    const subFocusKey = buildComparisonRunListOrderPreviewSubFocusKey(orderId, fieldKey);
    if (!onDrillBackScoreLink || !panelRunId) {
      return <p className="run-lineage-symbol-copy">{children}</p>;
    }
    return (
      <button
        aria-pressed={isOrderSubFocusOrigin(subFocusKey)}
        className={`run-lineage-symbol-copy run-lineage-symbol-copy-link comparison-run-card-link comparison-drillback-target ${
          highlightPanel ? "comparison-linked-copy" : ""
        } ${isOrderSubFocusOrigin(subFocusKey) ? "comparison-linked-copy-origin comparison-linked-subfocus" : ""}`.trim()}
        onClick={() =>
          onDrillBackScoreLink("metrics", "trade_count", {
            subFocusKey,
          })
        }
        ref={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        type="button"
      >
        {children}
      </button>
    );
  };

  return (
    <section
      className={`run-lineage ${highlightPanel ? "comparison-linked-panel" : ""} ${
        linkedScore?.role === "target" ? "comparison-linked-panel-target" : ""
      } ${linkedScore?.role === "baseline" ? "comparison-linked-panel-baseline" : ""} ${
        highlightOrigin ? "comparison-linked-panel-origin" : ""
      }`.trim()}
    >
      <div className="run-lineage-head">
        <span>Order lifecycle</span>
        <strong>{orders.length} tracked</strong>
      </div>
      <div className="run-lineage-grid">
        {renderOrderMetric("Open", String(openCount), orderOpenSubFocusKey)}
        {renderOrderMetric("Partial", String(partialCount), orderPartialSubFocusKey)}
        {renderOrderMetric("Filled", String(filledCount), orderFilledSubFocusKey)}
        {renderOrderMetric("Canceled", String(canceledCount), orderCanceledSubFocusKey)}
        {renderOrderMetric("Rejected", String(rejectedCount), orderRejectedSubFocusKey)}
      </div>
      <div className="run-lineage-copy">
        {renderOrderCopyLine(`Last order sync: ${formatTimestamp(latestSyncAt)}`, orderSyncSubFocusKey)}
      </div>
      {onDrillBackScoreLink && orderControls && orderActionBoundaryEnabled ? (
        <RunListComparisonBoundaryNote
          contract={eligibilityContract}
          groupKey="operational_order_actions"
        />
      ) : null}
      <div className="run-lineage-symbols">
        {previewOrders.map((order) => (
          <article className="run-lineage-symbol-card" key={order.order_id}>
            <div className="run-lineage-symbol-head">
              <strong>{order.order_id}</strong>
              <span>{order.status}</span>
            </div>
            <div className="run-lineage-symbol-grid">
              {renderOrderPreviewMetric(order.order_id, "Side", order.side, "side")}
              {renderOrderPreviewMetric(order.order_id, "Qty", order.quantity.toFixed(8), "qty")}
              {renderOrderPreviewMetric(order.order_id, "Filled", order.filled_quantity.toFixed(8), "filled")}
              {renderOrderPreviewMetric(
                order.order_id,
                "Remain",
                (order.remaining_quantity ?? Math.max(order.quantity - order.filled_quantity, 0)).toFixed(8),
                "remain",
              )}
            </div>
            {renderOrderPreviewLine(order.order_id, `Instrument: ${order.instrument_id}`, "instrument")}
            {renderOrderPreviewLine(
              order.order_id,
              `Avg fill: ${
                order.average_fill_price === null || order.average_fill_price === undefined
                  ? "n/a"
                  : order.average_fill_price
              }`,
              "avg_fill",
            )}
            {renderOrderPreviewLine(
              order.order_id,
              `Updated: ${formatTimestamp(order.updated_at ?? null)}`,
              "updated",
            )}
            {renderOrderPreviewLine(
              order.order_id,
              `Synced: ${formatTimestamp(order.last_synced_at ?? null)}`,
              "synced",
            )}
            {orderControls && (order.status === "open" || order.status === "partially_filled") ? (
              <RunOrderActionControls
                order={order}
                orderControls={orderControls}
              />
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}

export function RunOrderActionControls({
  order,
  orderControls,
}: {
  order: Run["orders"][number];
  orderControls: RunOrderControls;
}) {
  const remainingQuantity = order.remaining_quantity ?? Math.max(order.quantity - order.filled_quantity, 0);
  const draft = orderControls.getReplacementDraft(order.order_id, order);
  const cancelAvailability = order.action_availability?.cancel;
  const replaceAvailability = order.action_availability?.replace;
  const cancelAllowed = cancelAvailability?.allowed ?? true;
  const replaceAllowed = replaceAvailability?.allowed ?? true;

  return (
    <div className="run-lineage-order-controls">
      <div className="run-lineage-order-fields">
        <label>
          New px
          <input
            disabled={!replaceAllowed}
            min="0"
            onChange={(event) =>
              orderControls.onChangeReplacementDraft(order.order_id, {
                ...draft,
                price: event.target.value,
              })
            }
            title={!replaceAllowed ? replaceAvailability?.reason ?? undefined : undefined}
            step="any"
            type="number"
            value={draft.price}
          />
        </label>
        <label>
          Qty
          <input
            disabled={!replaceAllowed}
            min="0"
            onChange={(event) =>
              orderControls.onChangeReplacementDraft(order.order_id, {
                ...draft,
                quantity: event.target.value,
              })
            }
            placeholder={remainingQuantity.toFixed(8)}
            step="any"
            title={!replaceAllowed ? replaceAvailability?.reason ?? undefined : undefined}
            type="number"
            value={draft.quantity}
          />
        </label>
      </div>
      <div className="run-lineage-order-actions">
        <button
          className="ghost-button"
          disabled={!cancelAllowed}
          onClick={() => void orderControls.onCancelOrder(order.order_id)}
          title={!cancelAllowed ? cancelAvailability?.reason ?? undefined : undefined}
          type="button"
        >
          Cancel order
        </button>
        <button
          className="ghost-button"
          disabled={!replaceAllowed}
          onClick={() => void orderControls.onReplaceOrder(order.order_id, draft)}
          title={!replaceAllowed ? replaceAvailability?.reason ?? undefined : undefined}
          type="button"
        >
          Replace order
        </button>
      </div>
      <p className="run-lineage-symbol-copy">
        Blank qty uses the current remaining amount: {remainingQuantity.toFixed(8)}
      </p>
    </div>
  );
}

export function RunMarketDataLineage({
  linkedScore,
  lineage,
  lineageBySymbol,
  lineageSummary,
  onDrillBackScoreLink,
  panelRunId,
  registerSubFocusRef,
  rerunBoundaryId,
  rerunBoundaryState,
  rerunMatchStatus,
  rerunValidationCategory,
  rerunValidationSummary,
  rerunSourceRunId,
  rerunTargetBoundaryId,
}: {
  linkedScore: (ComparisonScoreLinkTarget & { role: ComparisonScoreLinkedRunRole }) | null;
  lineage: NonNullable<Run["provenance"]["market_data"]>;
  lineageBySymbol?: NonNullable<Run["provenance"]["market_data_by_symbol"]>;
  lineageSummary?: Run["provenance"]["lineage_summary"];
  onDrillBackScoreLink?: (
    section: ComparisonScoreSection,
    componentKey: string,
    options?: ComparisonScoreDrillBackOptions,
  ) => void;
  panelRunId?: string;
  registerSubFocusRef?: (runId: string, subFocusKey: string) => (node: HTMLElement | null) => void;
  rerunBoundaryId?: string | null;
  rerunBoundaryState: string;
  rerunMatchStatus: string;
  rerunValidationCategory: string;
  rerunValidationSummary?: string | null;
  rerunSourceRunId?: string | null;
  rerunTargetBoundaryId?: string | null;
}) {
  const symbolEntries = Object.entries(lineageBySymbol ?? {});
  const dataLineageSubFocusKey = buildComparisonRunListLineSubFocusKey("data_lineage");
  const dataLineageAssessmentSubFocusKey = buildComparisonRunListLineSubFocusKey("data_lineage_assessment");
  const dataLineageActionSubFocusKey = buildComparisonRunListLineSubFocusKey("data_lineage_action");
  const dataLineagePostureSubFocusKey = buildComparisonRunListLineSubFocusKey("data_lineage_posture");
  const dataProviderSubFocusKey = buildComparisonRunListLineSubFocusKey("data_provider");
  const dataSyncSubFocusKey = buildComparisonRunListLineSubFocusKey("data_sync");
  const dataReproSubFocusKey = buildComparisonRunListLineSubFocusKey("data_repro");
  const dataBoundarySubFocusKey = buildComparisonRunListLineSubFocusKey("data_boundary");
  const dataCandlesSubFocusKey = buildComparisonRunListLineSubFocusKey("data_candles");
  const dataTimeframeSubFocusKey = buildComparisonRunListLineSubFocusKey("data_timeframe");
  const dataRequestedWindowSubFocusKey = buildComparisonRunListLineSubFocusKey("data_requested_window");
  const dataEffectiveWindowSubFocusKey = buildComparisonRunListLineSubFocusKey("data_effective_window");
  const dataDatasetSubFocusKey = buildComparisonRunListLineSubFocusKey("data_dataset_identity");
  const dataSyncCheckpointSubFocusKey = buildComparisonRunListLineSubFocusKey("data_sync_checkpoint");
  const dataRerunBoundarySubFocusKey = buildComparisonRunListLineSubFocusKey("data_rerun_boundary");
  const dataRerunStatusSubFocusKey = buildComparisonRunListLineSubFocusKey("data_rerun_status");
  const dataRerunValidationSubFocusKey = buildComparisonRunListLineSubFocusKey("data_rerun_validation");
  const dataRerunSourceSubFocusKey = buildComparisonRunListLineSubFocusKey("data_rerun_source");
  const dataRerunTargetSubFocusKey = buildComparisonRunListLineSubFocusKey("data_rerun_target");
  const dataLastSyncSubFocusKey = buildComparisonRunListLineSubFocusKey("data_last_sync");
  const dataIssuesSubFocusKey = buildComparisonRunListLineSubFocusKey("data_issues");
  const highlightPanel =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore, ["provenance_richness"], "context");
  const isLineageSubFocusOrigin = (subFocusKey: string) =>
    linkedScore?.source === "run_list"
    && linkedScore.originRunId === panelRunId
    && linkedScore.subFocusKey === subFocusKey;
  const highlightOrigin =
    linkedScore?.source === "run_list"
    && linkedScore.originRunId === panelRunId
    && Boolean(
      linkedScore.subFocusKey === dataLineageSubFocusKey
      || linkedScore.subFocusKey?.startsWith("run-list-line:data_"),
    );
  const rerunStatusValue =
    rerunValidationCategory && rerunValidationCategory !== "not_rerun"
      ? `${rerunMatchStatus} / ${rerunValidationCategory}`
      : rerunMatchStatus;
  const lineagePostureLabel = formatLineagePosture(lineageSummary?.posture);
  const lineageStatusLabel = formatLineageIndicator(lineageSummary?.status);
  const renderLineageMetric = (label: string, value: string, subFocusKey: string) => {
    if (!onDrillBackScoreLink || !panelRunId) {
      return <Metric label={label} value={value} />;
    }
    return (
      <Metric
        buttonRef={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        className={highlightPanel ? "comparison-linked-panel" : ""}
        interactivePressed={isLineageSubFocusOrigin(subFocusKey)}
        label={label}
        onClick={() =>
          onDrillBackScoreLink("context", "provenance_richness", {
            subFocusKey,
          })
        }
        value={value}
      />
    );
  };
  const renderLineageLine = (children: string, subFocusKey: string) => {
    if (!onDrillBackScoreLink || !panelRunId) {
      return <p className="run-lineage-copy-link">{children}</p>;
    }
    return (
      <button
        aria-pressed={isLineageSubFocusOrigin(subFocusKey)}
        className={`run-lineage-copy-link comparison-run-card-link comparison-drillback-target ${
          highlightPanel ? "comparison-linked-copy" : ""
        } ${isLineageSubFocusOrigin(subFocusKey) ? "comparison-linked-copy-origin comparison-linked-subfocus" : ""}`.trim()}
        onClick={() =>
          onDrillBackScoreLink("context", "provenance_richness", {
            subFocusKey,
          })
        }
        ref={registerSubFocusRef?.(panelRunId, subFocusKey)}
        type="button"
      >
        {children}
      </button>
    );
  };
  const renderSymbolMetric = (symbol: string, label: string, value: string, fieldKey: string) => {
    const subFocusKey = buildComparisonRunListDataSymbolSubFocusKey(symbol, fieldKey);
    if (!onDrillBackScoreLink || !panelRunId) {
      return <Metric label={label} value={value} />;
    }
    return (
      <Metric
        buttonRef={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        className={highlightPanel ? "comparison-linked-panel" : ""}
        interactivePressed={isLineageSubFocusOrigin(subFocusKey)}
        label={label}
        onClick={() =>
          onDrillBackScoreLink("context", "provenance_richness", {
            subFocusKey,
          })
        }
        value={value}
      />
    );
  };
  const renderSymbolCopy = (symbol: string, children: string, fieldKey: string) => {
    const subFocusKey = buildComparisonRunListDataSymbolSubFocusKey(symbol, fieldKey);
    if (!onDrillBackScoreLink || !panelRunId) {
      return <p className="run-lineage-symbol-copy">{children}</p>;
    }
    return (
      <button
        aria-pressed={isLineageSubFocusOrigin(subFocusKey)}
        className={`run-lineage-symbol-copy run-lineage-symbol-copy-link comparison-run-card-link comparison-drillback-target ${
          highlightPanel ? "comparison-linked-copy" : ""
        } ${isLineageSubFocusOrigin(subFocusKey) ? "comparison-linked-copy-origin comparison-linked-subfocus" : ""}`.trim()}
        onClick={() =>
          onDrillBackScoreLink("context", "provenance_richness", {
            subFocusKey,
          })
        }
        ref={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        type="button"
      >
        {children}
      </button>
    );
  };

  return (
    <section
      className={`run-lineage ${highlightPanel ? "comparison-linked-panel" : ""} ${
        linkedScore?.role === "target" ? "comparison-linked-panel-target" : ""
      } ${linkedScore?.role === "baseline" ? "comparison-linked-panel-baseline" : ""} ${
        highlightOrigin ? "comparison-linked-panel-origin" : ""
      }`.trim()}
    >
      <div className="run-lineage-head">
        <span>Data lineage</span>
        <strong>{lineage.provider}</strong>
      </div>
      {lineageSummary ? (
        <div className={`run-lineage-summary-card is-${lineageSummary.status}`}>
          <div className="run-lineage-summary-head">
            <p className="kicker">Lineage posture</p>
            <span className={`meta-pill run-lineage-summary-pill is-${lineageSummary.status}`}>
              {lineagePostureLabel}
            </span>
          </div>
          <p className="run-lineage-summary-title">{lineageSummary.title}</p>
          <div className="run-lineage-summary-copy">
            {renderLineageLine(
              `Assessment: ${lineageSummary.summary}`,
              dataLineageAssessmentSubFocusKey,
            )}
            {renderLineageLine(
              `Operator action: ${lineageSummary.operator_action}`,
              dataLineageActionSubFocusKey,
            )}
            {renderLineageLine(
              `Posture: ${lineagePostureLabel} / ${lineageStatusLabel}`,
              dataLineagePostureSubFocusKey,
            )}
          </div>
        </div>
      ) : null}
      <div className="run-lineage-grid">
        {renderLineageMetric("Provider", lineage.provider, dataProviderSubFocusKey)}
        {renderLineageMetric("Sync", lineage.sync_status, dataSyncSubFocusKey)}
        {renderLineageMetric("Repro", lineage.reproducibility_state, dataReproSubFocusKey)}
        {renderLineageMetric("Boundary", rerunBoundaryState, dataBoundarySubFocusKey)}
        {renderLineageMetric("Candles", String(lineage.candle_count), dataCandlesSubFocusKey)}
        {renderLineageMetric("Timeframe", lineage.timeframe, dataTimeframeSubFocusKey)}
      </div>
      <div className="run-lineage-copy">
        {renderLineageLine(`${lineage.venue}:${lineage.symbols.join(", ")}`, dataLineageSubFocusKey)}
        {renderLineageLine(
          `Requested window: ${formatRange(lineage.requested_start_at, lineage.requested_end_at)}`,
          dataRequestedWindowSubFocusKey,
        )}
        {renderLineageLine(
          `Effective window: ${formatRange(lineage.effective_start_at, lineage.effective_end_at)}`,
          dataEffectiveWindowSubFocusKey,
        )}
        {renderLineageLine(`Dataset ID: ${lineage.dataset_identity ?? "unavailable"}`, dataDatasetSubFocusKey)}
        {renderLineageLine(`Sync checkpoint: ${lineage.sync_checkpoint_id ?? "unavailable"}`, dataSyncCheckpointSubFocusKey)}
        {renderLineageLine(`Rerun boundary: ${rerunBoundaryId ?? "unavailable"}`, dataRerunBoundarySubFocusKey)}
        {renderLineageLine(`Rerun status: ${rerunStatusValue}`, dataRerunStatusSubFocusKey)}
        {rerunValidationSummary
          ? renderLineageLine(`Validation summary: ${rerunValidationSummary}`, dataRerunValidationSubFocusKey)
          : null}
        {renderLineageLine(`Rerun source: ${rerunSourceRunId ?? "n/a"}`, dataRerunSourceSubFocusKey)}
        {renderLineageLine(`Rerun target: ${rerunTargetBoundaryId ?? "n/a"}`, dataRerunTargetSubFocusKey)}
        {renderLineageLine(`Last sync: ${formatTimestamp(lineage.last_sync_at)}`, dataLastSyncSubFocusKey)}
        {renderLineageLine(
          `Issues: ${lineage.issues.length ? lineage.issues.join(", ") : "none"}`,
          dataIssuesSubFocusKey,
        )}
      </div>
      {symbolEntries.length ? (
        <div className="run-lineage-symbols">
          {symbolEntries.map(([symbol, symbolLineage]) => (
            <article className="run-lineage-symbol-card" key={symbol}>
              <div className="run-lineage-symbol-head">
                <strong>{symbol}</strong>
                <span>{symbolLineage.sync_status}</span>
              </div>
              <div className="run-lineage-symbol-grid">
                {renderSymbolMetric(symbol, "Candles", String(symbolLineage.candle_count), "candles")}
                {renderSymbolMetric(symbol, "Provider", symbolLineage.provider, "provider")}
                {renderSymbolMetric(symbol, "Repro", symbolLineage.reproducibility_state, "repro")}
                {renderSymbolMetric(
                  symbol,
                  "Window",
                  formatRange(symbolLineage.effective_start_at, symbolLineage.effective_end_at),
                  "window",
                )}
              </div>
              {renderSymbolCopy(symbol, `Dataset ID: ${symbolLineage.dataset_identity ?? "unavailable"}`, "dataset_identity")}
              {renderSymbolCopy(symbol, `Sync checkpoint: ${symbolLineage.sync_checkpoint_id ?? "unavailable"}`, "sync_checkpoint")}
              {renderSymbolCopy(symbol, `Last sync: ${formatTimestamp(symbolLineage.last_sync_at)}`, "last_sync")}
              {renderSymbolCopy(
                symbol,
                `Issues: ${symbolLineage.issues.length ? symbolLineage.issues.join(", ") : "none"}`,
                "issues",
              )}
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
