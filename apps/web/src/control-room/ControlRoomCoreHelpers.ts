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
} from "../touchFeedback";
import { WorkspaceShell } from "../app/WorkspaceShell";
import { buildControlWorkspaceDescriptors, ControlWorkspaceDescriptor, ControlStripMetric } from "../app/workspaces";
import { useWorkspaceRoute } from "../app/useWorkspaceRoute";
import { WorkspaceRouteContent } from "../routes/WorkspaceRouteContent";
import {
  buildRunHistoryWorkspacePanels,
  type LiveOrderReplacementDraft,
  type RunHistoryWorkspaceSectionProps,
  type RunOrderControls,
} from "../routes/runHistoryWorkspacePanels";
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
} from "../runSurfaceCapabilities";
import { RunSurfaceCollectionQueryBuilder } from "../features/query-builder";
import {
  formatComparisonTooltipTuningDelta,
  formatComparisonTooltipTuningValue,
  formatRelativeTimestampLabel,
} from "../features/comparisonTooltipFormatters";
import { RunSection } from "../features/run-history/RunSection";
import type {
  RunSurfaceCollectionQueryBuilderApplyPayload,
  RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
  RunSurfaceCollectionQueryRuntimeCandidateSample,
} from "../features/query-builder";
import {
  applyProviderProvenanceSchedulerStitchedReportGovernancePlan,
  applyProviderProvenanceSchedulerNarrativeGovernancePlan,
  approveProviderProvenanceSchedulerStitchedReportGovernancePlan,
  approveProviderProvenanceSchedulerNarrativeGovernancePlan,
  createProviderProvenanceAnalyticsPreset,
  createProviderProvenanceDashboardView,
  createProviderProvenanceExportJob,
  createProviderProvenanceSchedulerStitchedReportGovernanceRegistry,
  createProviderProvenanceSchedulerStitchedReportGovernancePlan,
  createProviderProvenanceSchedulerStitchedReportView,
  createProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
  captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy,
  createProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
  createProviderProvenanceSchedulerNarrativeGovernancePlan,
  createProviderProvenanceSchedulerNarrativeRegistryEntry,
  createProviderProvenanceSchedulerNarrativeTemplate,
  createProviderProvenanceScheduledReport,
  approveProviderProvenanceExportJob,
  applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
  deleteProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
  deleteProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
  deleteProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
  deleteProviderProvenanceSchedulerNarrativeRegistryEntry,
  deleteProviderProvenanceSchedulerStitchedReportView,
  deleteProviderProvenanceSchedulerNarrativeTemplate,
  createProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  downloadProviderProvenanceExportJob,
  downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  escalateProviderProvenanceExportJob,
  exportProviderProvenanceSchedulerHealth,
  exportProviderProvenanceSchedulerStitchedNarrativeReport,
  reconstructProviderProvenanceSchedulerHealthExport,
  exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  fetchJson,
  getProviderProvenanceExportAnalytics,
  getProviderProvenanceExportJobHistory,
  getProviderProvenanceSchedulerHealthAnalytics,
  getProviderProvenanceScheduledReportHistory,
  getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
  listProviderProvenanceAnalyticsPresets,
  listProviderProvenanceDashboardViews,
  listProviderProvenanceSchedulerStitchedReportViews,
  listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits,
  listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates,
  listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisions,
  listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits,
  listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogs,
  listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisions,
  listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits,
  listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplates,
  listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisions,
  listProviderProvenanceSchedulerNarrativeGovernancePlans,
  listProviderProvenanceSchedulerNarrativeRegistryEntries,
  listProviderProvenanceSchedulerNarrativeRegistryRevisions,
  listProviderProvenanceSchedulerNarrativeTemplates,
  listProviderProvenanceSchedulerNarrativeTemplateRevisions,
  listProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogs,
  listProviderProvenanceSchedulerStitchedReportGovernancePolicyTemplates,
  listProviderProvenanceSchedulerStitchedReportGovernancePlans,
  rollbackProviderProvenanceSchedulerStitchedReportGovernancePlan,
  rollbackProviderProvenanceSchedulerNarrativeGovernancePlan,
  listMarketDataIngestionJobs,
  listMarketDataLineageHistory,
  listProviderProvenanceExportJobs,
  listProviderProvenanceSchedulerAlertHistory,
  listProviderProvenanceSchedulerHealthHistory,
  listProviderProvenanceSchedulerStitchedReportGovernanceRegistries,
  listProviderProvenanceSchedulerStitchedReportGovernanceRegistryAudits,
  listProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisions,
  listProviderProvenanceSchedulerStitchedReportViewAudits,
  listProviderProvenanceSchedulerStitchedReportViewRevisions,
  getProviderProvenanceSchedulerSearchDashboard,
  bulkGovernProviderProvenanceSchedulerSearchModerationPolicyCatalogs,
  bulkGovernProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies,
  createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicy,
  createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy,
  listProviderProvenanceSchedulerSearchModerationPolicyCatalogs,
  listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies,
  listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans,
  listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits,
  listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies,
  listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisions,
  listProviderProvenanceSchedulerSearchModerationCatalogGovernancePlans,
  listProviderProvenanceSchedulerSearchModerationPolicyCatalogAudits,
  listProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisions,
  listProviderProvenanceSchedulerSearchModerationPlans,
  listProviderProvenanceScheduledReports,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  approveProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan,
  approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan,
  approveProviderProvenanceSchedulerSearchModerationPlan,
  applyProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan,
  applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan,
  applyProviderProvenanceSchedulerSearchModerationPlan,
  createProviderProvenanceSchedulerSearchModerationPolicyCatalog,
  deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy,
  deleteProviderProvenanceSchedulerSearchModerationPolicyCatalog,
  moderateProviderProvenanceSchedulerSearchFeedbackBatch,
  moderateProviderProvenanceSchedulerSearchFeedback,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  recordProviderProvenanceSchedulerSearchFeedback,
  resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRevision,
  restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevision,
  restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevision,
  restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogRevision,
  restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevision,
  restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevision,
  restoreProviderProvenanceSchedulerNarrativeRegistryRevision,
  restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevision,
  restoreProviderProvenanceSchedulerStitchedReportViewRevision,
  restoreProviderProvenanceSchedulerNarrativeTemplateRevision,
  revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  runProviderProvenanceSchedulerNarrativeGovernancePlanBatchAction,
  runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkGovernance,
  runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkGovernance,
  runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkGovernance,
  stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan,
  stageProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan,
  stageProviderProvenanceSchedulerSearchModerationPlan,
  updateProviderProvenanceSchedulerSearchModerationPolicyCatalog,
  updateProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy,
  stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates,
  stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
  stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
  runDueProviderProvenanceScheduledReports,
  runProviderProvenanceScheduledReport,
  updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
  updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
  updateProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
  updateProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
  updateProviderProvenanceSchedulerNarrativeRegistryEntry,
  updateProviderProvenanceSchedulerStitchedReportGovernanceRegistry,
  updateProviderProvenanceSchedulerStitchedReportView,
  updateProviderProvenanceSchedulerNarrativeTemplate,
  updateProviderProvenanceExportJobPolicy,
  deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistry,
} from "../controlRoomApi";


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
} from "../controlRoomDefinitions";
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
} from "../controlRoomDefinitions";


const defaultRunForm = {
  strategy_id: "ma_cross_v1",
  symbol: "BTC/USDT",
  timeframe: "5m",
  initial_cash: 10000,
  fee_rate: 0.001,
  slippage_bps: 3,
  tags_text: "",
  preset_id: "",
  benchmark_family: "",
};

const defaultPresetForm = {
  name: "",
  preset_id: "",
  description: "",
  strategy_id: "",
  timeframe: "5m",
  benchmark_family: "",
  tags_text: "",
  parameters_text: "",
};

const defaultPresetRevisionFilter: PresetRevisionFilterState = {
  action: "all",
  query: "",
};

const defaultMarketDataProvenanceExportFilterState: MarketDataProvenanceExportFilterState = {
  provider: ALL_FILTER_VALUE,
  vendor_field: ALL_FILTER_VALUE,
  search_query: "",
  sort: "newest",
};

type ProviderProvenanceAnalyticsScope = "current_focus" | "all_focuses";
type ProviderProvenanceSchedulerOccurrenceNarrativeFacet =
  | "all_occurrences"
  | "resolved_narratives"
  | "post_resolution_recovery"
  | "recurring_occurrences";

type ProviderProvenanceAnalyticsQueryState = {
  scope: ProviderProvenanceAnalyticsScope;
  provider_label: string;
  vendor_field: string;
  market_data_provider: string;
  requested_by_tab_id: string;
  scheduler_alert_category: string;
  scheduler_alert_status: string;
  scheduler_alert_narrative_facet: ProviderProvenanceSchedulerOccurrenceNarrativeFacet;
  search_query: string;
  window_days: number;
};

type ProviderProvenanceSchedulerSearchDashboardFilterState = {
  search: string;
  moderation_status: string;
  signal: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
};

type ProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft = {
  name: string;
  description: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
};

type ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilterState = {
  catalog_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

type ProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft = {
  name: string;
  description: string;
  action_scope: string;
  require_approval_note: boolean;
  guidance: string;
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilterState = {
  governance_policy_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
  action_scope: string;
  require_approval_note: boolean;
  guidance: string;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft = {
  name: string;
  description: string;
  action_scope: string;
  require_approval_note: boolean;
  guidance: string;
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  policy_action_scope: string;
  policy_require_approval_note: boolean;
  policy_guidance: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState = {
  queue_state: string;
  meta_policy_id: string;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft = {
  action: string;
  meta_policy_id: string;
  note: string;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState = {
  queue_state: string;
  governance_policy_id: string;
};

type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft = {
  action: string;
  governance_policy_id: string;
  note: string;
};

type ProviderProvenanceSchedulerSearchModerationQueueFilterState = {
  queue_state: string;
  policy_catalog_id: string;
};

type ProviderProvenanceSchedulerSearchModerationStageDraft = {
  policy_catalog_id: string;
  moderation_status: string;
  note: string;
};

type ProviderProvenanceSchedulerExportPolicyDraft = {
  job_id: string | null;
  routing_policy_id: string;
  approval_policy_id: string;
  delivery_targets: string[];
  approval_note: string;
};

type OperatorVisibilityAlertEntry =
  | OperatorVisibility["alerts"][number]
  | OperatorVisibility["alert_history"][number];

const defaultProviderProvenanceAnalyticsQueryState: ProviderProvenanceAnalyticsQueryState = {
  scope: "current_focus",
  provider_label: ALL_FILTER_VALUE,
  vendor_field: ALL_FILTER_VALUE,
  market_data_provider: ALL_FILTER_VALUE,
  requested_by_tab_id: ALL_FILTER_VALUE,
  scheduler_alert_category: ALL_FILTER_VALUE,
  scheduler_alert_status: ALL_FILTER_VALUE,
  scheduler_alert_narrative_facet: "all_occurrences",
  search_query: "",
  window_days: 14,
};

const defaultProviderProvenanceSchedulerSearchDashboardFilterState: ProviderProvenanceSchedulerSearchDashboardFilterState = {
  search: "",
  moderation_status: ALL_FILTER_VALUE,
  signal: ALL_FILTER_VALUE,
  governance_view: "all_feedback",
  window_days: 30,
  stale_pending_hours: 24,
};

const defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft: ProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft = {
  name: "",
  description: "",
  default_moderation_status: "approved",
  governance_view: "pending_queue",
  window_days: 30,
  stale_pending_hours: 24,
  minimum_score: 0,
  require_note: false,
};

const defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilterState = {
  catalog_id: "",
  action: ALL_FILTER_VALUE,
  actor_tab_id: "",
  search: "",
};

const defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft: ProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft = {
  name_prefix: "",
  name_suffix: "",
  description_append: "",
  default_moderation_status: "approved",
  governance_view: "pending_queue",
  window_days: 30,
  stale_pending_hours: 24,
  minimum_score: 0,
  require_note: false,
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft = {
  name: "",
  description: "",
  action_scope: "any",
  require_approval_note: false,
  guidance: "",
  name_prefix: "",
  name_suffix: "",
  description_append: "",
  default_moderation_status: "approved",
  governance_view: "pending_queue",
  window_days: 30,
  stale_pending_hours: 24,
  minimum_score: 0,
  require_note: false,
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilterState = {
  governance_policy_id: "",
  action: ALL_FILTER_VALUE,
  actor_tab_id: "",
  search: "",
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft = {
  name_prefix: "",
  name_suffix: "",
  description_append: "",
  default_moderation_status: "approved",
  governance_view: "pending_queue",
  window_days: 30,
  stale_pending_hours: 24,
  minimum_score: 0,
  require_note: false,
  action_scope: "any",
  require_approval_note: false,
  guidance: "",
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft = {
  name: "",
  description: "",
  action_scope: "any",
  require_approval_note: false,
  guidance: "",
  name_prefix: "",
  name_suffix: "",
  description_append: "",
  policy_action_scope: "any",
  policy_require_approval_note: false,
  policy_guidance: "",
  default_moderation_status: "approved",
  governance_view: "pending_queue",
  window_days: 30,
  stale_pending_hours: 24,
  minimum_score: 0,
  require_note: false,
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState = {
  queue_state: "pending_approval",
  meta_policy_id: ALL_FILTER_VALUE,
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft = {
  action: "update",
  meta_policy_id: ALL_FILTER_VALUE,
  note: "",
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState = {
  queue_state: "pending_approval",
  governance_policy_id: ALL_FILTER_VALUE,
};

const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft = {
  action: "update",
  governance_policy_id: ALL_FILTER_VALUE,
  note: "",
};

const defaultProviderProvenanceSchedulerSearchModerationQueueFilterState: ProviderProvenanceSchedulerSearchModerationQueueFilterState = {
  queue_state: "pending_approval",
  policy_catalog_id: ALL_FILTER_VALUE,
};

const defaultProviderProvenanceSchedulerSearchModerationStageDraft: ProviderProvenanceSchedulerSearchModerationStageDraft = {
  policy_catalog_id: ALL_FILTER_VALUE,
  moderation_status: "approved",
  note: "",
};

function normalizeProviderProvenanceSchedulerRoutingPolicyDraftValue(policyId?: string | null) {
  if (
    policyId === "all_targets"
    || policyId === "chatops_only"
    || policyId === "paging_only"
    || policyId === "custom"
  ) {
    return policyId;
  }
  return "default";
}

function normalizeProviderProvenanceSchedulerApprovalPolicyDraftValue(policyId?: string | null) {
  return policyId === "manual_required" ? "manual_required" : "auto";
}

function buildProviderProvenanceSchedulerExportPolicyDraft(
  entry: ProviderProvenanceExportJobEntry | null,
): ProviderProvenanceSchedulerExportPolicyDraft {
  return {
    job_id: entry?.job_id ?? null,
    routing_policy_id: normalizeProviderProvenanceSchedulerRoutingPolicyDraftValue(entry?.routing_policy_id),
    approval_policy_id: normalizeProviderProvenanceSchedulerApprovalPolicyDraftValue(entry?.approval_policy_id),
    delivery_targets: entry?.routing_targets?.length
      ? [...entry.routing_targets]
      : [...(entry?.available_delivery_targets ?? [])],
    approval_note: entry?.approval_note?.trim() ?? "",
  };
}

function getProviderProvenanceSchedulerNarrativeGovernanceQueuePriorityRank(
  priority?: string | null,
) {
  switch (priority) {
    case "critical":
      return 3;
    case "high":
      return 2;
    case "normal":
      return 1;
    default:
      return 0;
  }
}

function getProviderProvenanceSchedulerNarrativeGovernanceQueueState(
  plan: Pick<ProviderProvenanceSchedulerNarrativeGovernancePlan, "queue_state" | "status">,
) {
  if (plan.queue_state?.trim()) {
    return plan.queue_state;
  }
  if (plan.status === "previewed") {
    return "pending_approval";
  }
  if (plan.status === "approved") {
    return "ready_to_apply";
  }
  return "completed";
}

function formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(
  steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[],
) {
  if (!steps.length) {
    return "No reusable hierarchy captured.";
  }
  return `${steps.length} step(s): ${steps
    .map((step) => `${formatWorkflowToken(step.item_type)} ${step.item_ids.length}`)
    .join(" · ")}`;
}

function formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep,
) {
  const patchLabels = [
    step.name_prefix ? "name prefix" : null,
    step.name_suffix ? "name suffix" : null,
    step.description_append ? "description" : null,
    Object.keys(step.query_patch ?? {}).length ? "query" : null,
    Object.keys(step.layout_patch ?? {}).length ? "layout" : null,
    step.template_id ? "template link" : null,
    step.clear_template_link ? "clear template link" : null,
  ].filter((value): value is string => Boolean(value));
  const targetSummary = step.item_names.length
    ? step.item_names.join(", ")
    : `${step.item_ids.length} target(s)`;
  const templateSummary = step.source_template_name
    ? ` · template ${step.source_template_name}`
    : step.source_template_id
      ? ` · template ${step.source_template_id}`
      : "";
  return `${formatWorkflowToken(step.item_type)} · ${targetSummary}${templateSummary}${patchLabels.length ? ` · ${patchLabels.join(", ")}` : ""}`;
}

function formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(
  plan: Pick<
    ProviderProvenanceSchedulerNarrativeGovernancePlan,
    "hierarchy_position" | "hierarchy_total" | "hierarchy_name"
  >,
) {
  if (!plan.hierarchy_total) {
    return null;
  }
  const label = `${plan.hierarchy_position ?? 1} of ${plan.hierarchy_total}`;
  return plan.hierarchy_name ? `${plan.hierarchy_name} · ${label}` : label;
}

function isProviderProvenanceSchedulerAlertCategory(category?: string | null) {
  return category === "scheduler_lag" || category === "scheduler_failure";
}

function getOperatorAlertOccurrenceKey(
  alert: Pick<
    OperatorVisibilityAlertEntry,
    "occurrence_id" | "alert_id" | "status" | "detected_at" | "resolved_at"
  >,
) {
  return alert.occurrence_id ?? `${alert.alert_id}:${alert.status}:${alert.detected_at}:${alert.resolved_at ?? "active"}`;
}

function formatProviderProvenanceSchedulerTimelineSummary(
  alert: Pick<
    OperatorVisibilityAlertEntry,
    "category" | "status" | "timeline_position" | "timeline_total"
  >,
) {
  if (!isProviderProvenanceSchedulerAlertCategory(alert.category) || !alert.timeline_total) {
    return null;
  }
  const occurrenceLabel = `Occurrence ${alert.timeline_position ?? 1} of ${alert.timeline_total}`;
  const categoryLabel = formatWorkflowToken(alert.category);
  return alert.status === "resolved"
    ? `${occurrenceLabel} in the ${categoryLabel} timeline.`
    : `${occurrenceLabel} is the current ${categoryLabel} occurrence.`;
}

function formatProviderProvenanceSchedulerSearchMatchSummary(
  searchMatch:
    | ProviderProvenanceSchedulerAlertHistoryPayload["items"][number]["search_match"]
    | null
    | undefined,
) {
  if (!searchMatch) {
    return null;
  }
  const operatorSummary = searchMatch.operator_hits.length
    ? ` · ops ${searchMatch.operator_hits.length}`
    : "";
  const semanticSummary = searchMatch.semantic_concepts.length
    ? ` · semantic ${searchMatch.semantic_concepts.join(", ")}`
    : "";
  return `Search score ${searchMatch.score} · ${searchMatch.term_coverage_pct}% coverage · ${searchMatch.matched_fields.join(", ") || "ranked fields"}${operatorSummary}${semanticSummary}`;
}

function formatProviderProvenanceSchedulerRetrievalClusterSummary(
  cluster:
    | ProviderProvenanceSchedulerAlertHistoryPayload["retrieval_clusters"][number]
    | ProviderProvenanceSchedulerAlertHistoryPayload["items"][number]["retrieval_cluster"]
    | null
    | undefined,
) {
  if (!cluster) {
    return null;
  }
  const label = cluster.label ?? "Cross-occurrence cluster";
  const rank = typeof cluster.rank === "number" && cluster.rank > 0 ? `Cluster ${cluster.rank}` : "Cluster";
  const similarity = "similarity_pct" in cluster ? ` · similarity ${cluster.similarity_pct}%` : "";
  return `${rank} · ${label}${similarity}`;
}

function buildProviderProvenanceSchedulerAlertWorkflowReason(
  alert: OperatorVisibilityAlertEntry,
  mode: "workflow" | "escalation",
  source: "current" | "historical" = "current",
) {
  const category = alert.category === "scheduler_failure" ? "scheduler_failure" : "scheduler_lag";
  const suffix = source === "historical" ? "historical_alert_row" : "alert_triggered";
  return mode === "escalation"
    ? `${category}_${suffix}`
    : `${category}_alert_workflow`;
}

const defaultProviderProvenanceDashboardLayout: ProviderProvenanceDashboardLayout = {
  highlight_panel: "overview",
  show_rollups: true,
  show_time_series: true,
  show_recent_exports: true,
};

const DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT = "queue_priority";

const defaultProviderProvenanceWorkspaceDraft = {
  name: "",
  description: "",
};

type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraftState = {
  name: string;
  description: string;
  default_policy_template_id: string;
  default_policy_catalog_id: string;
};

const defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft:
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraftState = {
    name: "",
    description: "",
    default_policy_template_id: "",
    default_policy_catalog_id: "",
  };

type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraftState = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  queue_state: string;
  approval_lane: string;
  approval_priority: string;
  search: string;
  sort: string;
  default_policy_template_id: string;
  default_policy_catalog_id: string;
};

const defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft:
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraftState = {
    name_prefix: "",
    name_suffix: "",
    description_append: "",
    queue_state: "__keep_current__",
    approval_lane: "__keep_current__",
    approval_priority: "__keep_current__",
    search: "__keep_current__",
    sort: "__keep_current__",
    default_policy_template_id: "__keep_current__",
    default_policy_catalog_id: "__keep_current__",
  };

const KEEP_CURRENT_BULK_GOVERNANCE_VALUE = "__keep_current__";
const CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE = "__clear_template_link__";

type ProviderProvenanceSchedulerNarrativeBulkToggleValue =
  | typeof KEEP_CURRENT_BULK_GOVERNANCE_VALUE
  | "enable"
  | "disable";

type ProviderProvenanceSchedulerNarrativeTemplateBulkDraftState = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  scheduler_alert_category: string;
  scheduler_alert_status: string;
  scheduler_alert_narrative_facet:
    | typeof KEEP_CURRENT_BULK_GOVERNANCE_VALUE
    | ProviderProvenanceSchedulerOccurrenceNarrativeFacet;
  window_days: string;
  result_limit: string;
};

const defaultProviderProvenanceSchedulerNarrativeTemplateBulkDraft: ProviderProvenanceSchedulerNarrativeTemplateBulkDraftState = {
  name_prefix: "",
  name_suffix: "",
  description_append: "",
  scheduler_alert_category: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  scheduler_alert_status: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  scheduler_alert_narrative_facet: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  window_days: "",
  result_limit: "",
};

type ProviderProvenanceSchedulerStitchedReportViewBulkDraftState = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  scheduler_alert_category: string;
  scheduler_alert_status: string;
  scheduler_alert_narrative_facet:
    | typeof KEEP_CURRENT_BULK_GOVERNANCE_VALUE
    | ProviderProvenanceSchedulerOccurrenceNarrativeFacet;
  window_days: string;
  result_limit: string;
  occurrence_limit: string;
  history_limit: string;
  drilldown_history_limit: string;
};

const defaultProviderProvenanceSchedulerStitchedReportViewBulkDraft:
  ProviderProvenanceSchedulerStitchedReportViewBulkDraftState = {
    name_prefix: "",
    name_suffix: "",
    description_append: "",
    scheduler_alert_category: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
    scheduler_alert_status: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
    scheduler_alert_narrative_facet: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
    window_days: "",
    result_limit: "",
    occurrence_limit: "",
    history_limit: "",
    drilldown_history_limit: "",
  };

type ProviderProvenanceSchedulerNarrativeRegistryDraftState = {
  name: string;
  description: string;
  template_id: string;
};

const defaultProviderProvenanceSchedulerNarrativeRegistryDraft: ProviderProvenanceSchedulerNarrativeRegistryDraftState = {
  name: "",
  description: "",
  template_id: "",
};

type ProviderProvenanceSchedulerNarrativeRegistryBulkDraftState = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  scheduler_alert_category: string;
  scheduler_alert_status: string;
  scheduler_alert_narrative_facet:
    | typeof KEEP_CURRENT_BULK_GOVERNANCE_VALUE
    | ProviderProvenanceSchedulerOccurrenceNarrativeFacet;
  window_days: string;
  result_limit: string;
  template_id: string;
  show_rollups: ProviderProvenanceSchedulerNarrativeBulkToggleValue;
  show_time_series: ProviderProvenanceSchedulerNarrativeBulkToggleValue;
  show_recent_exports: ProviderProvenanceSchedulerNarrativeBulkToggleValue;
};

const defaultProviderProvenanceSchedulerNarrativeRegistryBulkDraft: ProviderProvenanceSchedulerNarrativeRegistryBulkDraftState = {
  name_prefix: "",
  name_suffix: "",
  description_append: "",
  scheduler_alert_category: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  scheduler_alert_status: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  scheduler_alert_narrative_facet: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  window_days: "",
  result_limit: "",
  template_id: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  show_rollups: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  show_time_series: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  show_recent_exports: KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
};

type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraftState = {
  name: string;
  description: string;
  item_type_scope:
    | "any"
    | "template"
    | "registry"
    | "stitched_report_view"
    | "stitched_report_governance_registry";
  action_scope: "any" | "delete" | "restore" | "update";
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical";
  guidance: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft:
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraftState = {
    name: "",
    description: "",
    item_type_scope: "any",
    action_scope: "any",
    approval_lane: "general",
    approval_priority: "normal",
    guidance: "",
  };

type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraftState = {
  name: string;
  description: string;
  default_policy_template_id: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft:
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraftState = {
    name: "",
    description: "",
    default_policy_template_id: "",
  };

type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraftState = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  default_policy_template_id: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft:
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraftState = {
    name_prefix: "",
    name_suffix: "",
  description_append: "",
  default_policy_template_id: "",
  };

type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraftState = {
  item_ids_text: string;
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  query_patch: string;
  layout_patch: string;
  template_id: string;
  clear_template_link: boolean;
};

const defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft:
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraftState = {
    item_ids_text: "",
    name_prefix: "",
    name_suffix: "",
    description_append: "",
    query_patch: "",
    layout_patch: "",
    template_id: "",
    clear_template_link: false,
  };

type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraftState = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  query_patch: string;
  layout_patch: string;
  template_id: string;
  clear_template_link: boolean;
};

const defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft:
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraftState = {
    name_prefix: "",
    name_suffix: "",
    description_append: "",
    query_patch: "",
    layout_patch: "",
    template_id: "",
    clear_template_link: false,
  };

type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraftState = {
  name: string;
  description: string;
  item_ids_text: string;
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  query_patch: string;
  layout_patch: string;
  template_id: string;
  clear_template_link: boolean;
  governance_policy_template_id: string;
  governance_policy_catalog_id: string;
  governance_approval_lane: string;
  governance_approval_priority: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft:
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraftState = {
    name: "",
    description: "",
    item_ids_text: "",
    name_prefix: "",
    name_suffix: "",
    description_append: "",
  query_patch: "",
  layout_patch: "",
  template_id: "",
  clear_template_link: false,
  governance_policy_template_id: "",
  governance_policy_catalog_id: "",
  governance_approval_lane: "",
  governance_approval_priority: "",
};

type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraftState = {
  name_prefix: string;
  name_suffix: string;
  description_append: string;
  item_ids_text: string;
  step_name_prefix: string;
  step_name_suffix: string;
  step_description_append: string;
  query_patch: string;
  layout_patch: string;
  template_id: string;
  clear_template_link: boolean;
};

const defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft:
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraftState = {
    name_prefix: "",
    name_suffix: "",
    description_append: "",
    item_ids_text: "",
    step_name_prefix: "",
    step_name_suffix: "",
    step_description_append: "",
    query_patch: "",
    layout_patch: "",
    template_id: "",
    clear_template_link: false,
  };

type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersionEntry = {
  revision: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry;
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep;
  position: number;
  total: number;
};

type ProviderProvenanceSchedulerNarrativeGovernanceQueueFilterState = {
  queue_state: typeof ALL_FILTER_VALUE | "pending_approval" | "ready_to_apply" | "completed";
  item_type:
    | typeof ALL_FILTER_VALUE
    | "template"
    | "registry"
    | "stitched_report_view"
    | "stitched_report_governance_registry";
  approval_lane: string;
  approval_priority: string;
  policy_template_id: string;
  policy_catalog_id: string;
  source_hierarchy_step_template_id: string;
  search: string;
  sort: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernanceQueueFilter:
  ProviderProvenanceSchedulerNarrativeGovernanceQueueFilterState = {
    queue_state: ALL_FILTER_VALUE,
  item_type: ALL_FILTER_VALUE,
  approval_lane: ALL_FILTER_VALUE,
  approval_priority: ALL_FILTER_VALUE,
  policy_template_id: ALL_FILTER_VALUE,
  policy_catalog_id: ALL_FILTER_VALUE,
  source_hierarchy_step_template_id: ALL_FILTER_VALUE,
  search: "",
  sort: DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT,
};

type ProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterState = {
  queue_state: typeof ALL_FILTER_VALUE | "pending_approval" | "ready_to_apply" | "completed";
  approval_lane: string;
  approval_priority: string;
  policy_template_id: string;
  policy_catalog_id: string;
  search: string;
  sort: string;
};

const defaultProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter:
  ProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterState = {
    queue_state: ALL_FILTER_VALUE,
    approval_lane: ALL_FILTER_VALUE,
    approval_priority: ALL_FILTER_VALUE,
    policy_template_id: ALL_FILTER_VALUE,
    policy_catalog_id: ALL_FILTER_VALUE,
    search: "",
    sort: DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT,
  };

type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilterState = {
  policy_template_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter:
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilterState = {
    policy_template_id: "",
    action: ALL_FILTER_VALUE,
    actor_tab_id: "",
    search: "",
  };

type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilterState = {
  catalog_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter:
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilterState = {
    catalog_id: "",
    action: ALL_FILTER_VALUE,
    actor_tab_id: "",
    search: "",
  };

type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilterState = {
  hierarchy_step_template_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

const defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter:
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilterState = {
    hierarchy_step_template_id: "",
    action: ALL_FILTER_VALUE,
    actor_tab_id: "",
    search: "",
  };

type ProviderProvenanceSchedulerStitchedReportViewAuditFilterState = {
  view_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

const defaultProviderProvenanceSchedulerStitchedReportViewAuditFilter:
  ProviderProvenanceSchedulerStitchedReportViewAuditFilterState = {
    view_id: "",
    action: ALL_FILTER_VALUE,
    actor_tab_id: "",
    search: "",
  };

type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilterState = {
  registry_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

const defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter:
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilterState = {
    registry_id: "",
    action: ALL_FILTER_VALUE,
    actor_tab_id: "",
    search: "",
  };

type ProviderProvenanceReportDraftState = {
  name: string;
  description: string;
  preset_id: string;
  view_id: string;
  cadence: "daily" | "weekly";
  status: "scheduled" | "paused";
};

const defaultProviderProvenanceReportDraft: ProviderProvenanceReportDraftState = {
  name: "",
  description: "",
  preset_id: "",
  view_id: "",
  cadence: "daily",
  status: "scheduled",
};

function buildPresetFormFromPreset(preset: ExperimentPreset) {
  return {
    name: preset.name,
    preset_id: preset.preset_id,
    description: preset.description,
    strategy_id: preset.strategy_id ?? "",
    timeframe: preset.timeframe ?? "",
    benchmark_family: preset.benchmark_family ?? "",
    tags_text: preset.tags.join(", "),
    parameters_text: Object.keys(preset.parameters).length
      ? JSON.stringify(preset.parameters, null, 2)
      : "",
  };
}

function buildCurrentPresetRevisionSnapshot(preset: ExperimentPreset): ExperimentPresetRevision {
  return {
    revision_id: `${preset.preset_id}:current`,
    actor: preset.lifecycle.updated_by,
    reason: preset.lifecycle.last_action,
    created_at: preset.updated_at,
    action: "current",
    source_revision_id: null,
    name: preset.name,
    description: preset.description,
    strategy_id: preset.strategy_id ?? null,
    timeframe: preset.timeframe ?? null,
    benchmark_family: preset.benchmark_family ?? null,
    tags: [...preset.tags],
    parameters: { ...preset.parameters },
  };
}

function buildEmptyPresetRevisionSnapshot(): ExperimentPresetRevision {
  return {
    revision_id: "empty",
    actor: "",
    reason: "",
    created_at: "",
    action: "empty",
    source_revision_id: null,
    name: "",
    description: "",
    strategy_id: null,
    timeframe: null,
    benchmark_family: null,
    tags: [],
    parameters: {},
  };
}

function formatPresetStructuredDiffDisplayValue(value: string) {
  return value || "none";
}

function isPresetStructuredDiffObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isPresetStructuredDiffScalar(value: unknown) {
  return value === null || ["boolean", "number", "string"].includes(typeof value);
}

function arePresetStructuredDiffValuesEquivalent(left: unknown, right: unknown) {
  if (left === right) {
    return true;
  }
  if (
    typeof left === "number" &&
    Number.isNaN(left) &&
    typeof right === "number" &&
    Number.isNaN(right)
  ) {
    return true;
  }
  if (
    (Array.isArray(left) || isPresetStructuredDiffObject(left)) &&
    (Array.isArray(right) || isPresetStructuredDiffObject(right))
  ) {
    return JSON.stringify(left) === JSON.stringify(right);
  }
  return false;
}

function matchesPresetParameterSchemaType(value: unknown, expectedType?: string) {
  if (value === undefined || !expectedType) {
    return true;
  }
  switch (expectedType) {
    case "integer":
      return typeof value === "number" && Number.isInteger(value);
    case "number":
      return typeof value === "number" && Number.isFinite(value);
    case "boolean":
      return typeof value === "boolean";
    case "string":
      return typeof value === "string";
    case "array":
      return Array.isArray(value);
    case "object":
      return isPresetStructuredDiffObject(value);
    default:
      return true;
  }
}

function joinPresetStructuredDiffHints(...parts: Array<string | undefined>) {
  return parts.filter((part): part is string => Boolean(part)).join(" · ") || undefined;
}

function tokenizePresetParameterPath(pathSegments: string[]) {
  return pathSegments
    .flatMap((segment) => segment.toLowerCase().match(/[a-z0-9]+/g) ?? [])
    .filter((token) => !/^\d+$/.test(token));
}

function parsePresetTimeframeToMinutes(value: unknown) {
  if (typeof value !== "string") {
    return null;
  }
  const match = value.trim().match(/^(\d+)([mhdw])$/i);
  if (!match) {
    return null;
  }
  const amount = Number(match[1]);
  const unit = PRESET_TIMEFRAME_UNIT_TO_MINUTES[match[2].toLowerCase()];
  if (!Number.isFinite(amount) || !unit) {
    return null;
  }
  return amount * unit;
}

function buildPresetRankedStringDelta(
  existingRaw: unknown,
  incomingRaw: unknown,
  ranks: Record<string, number>,
  higherLabel: string,
  lowerLabel: string,
): PresetStructuredDiffDeltaValue | undefined {
  if (typeof existingRaw !== "string" || typeof incomingRaw !== "string") {
    return undefined;
  }
  const existingRank = ranks[existingRaw.trim().toLowerCase()];
  const incomingRank = ranks[incomingRaw.trim().toLowerCase()];
  if (existingRank === undefined || incomingRank === undefined || existingRank === incomingRank) {
    return undefined;
  }
  return {
    direction: incomingRank > existingRank ? "higher" : "lower",
    label: incomingRank > existingRank ? higherLabel : lowerLabel,
  };
}

function buildPresetParameterStrategyContext(
  existingRaw: unknown,
  incomingRaw: unknown,
  schemaEntry?: ParameterSchema[string],
): {
  delta?: PresetStructuredDiffDeltaValue;
  hint?: string;
} {
  if (!schemaEntry) {
    return {
      delta: undefined,
      hint: undefined,
    };
  }
  const hint =
    typeof schemaEntry.semantic_hint === "string" && schemaEntry.semantic_hint.trim()
      ? `Strategy: ${schemaEntry.semantic_hint.trim()}`
      : undefined;
  const higherLabel =
    typeof schemaEntry.delta_higher_label === "string" && schemaEntry.delta_higher_label.trim()
      ? schemaEntry.delta_higher_label.trim()
      : undefined;
  const lowerLabel =
    typeof schemaEntry.delta_lower_label === "string" && schemaEntry.delta_lower_label.trim()
      ? schemaEntry.delta_lower_label.trim()
      : undefined;
  if (!higherLabel || !lowerLabel) {
    return {
      delta: undefined,
      hint,
    };
  }
  if (
    typeof existingRaw === "number" &&
    Number.isFinite(existingRaw) &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw) &&
    existingRaw !== incomingRaw
  ) {
    return {
      delta: {
        direction: incomingRaw > existingRaw ? "higher" : "lower",
        label: incomingRaw > existingRaw ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  if (typeof existingRaw === "boolean" && typeof incomingRaw === "boolean" && existingRaw !== incomingRaw) {
    return {
      delta: {
        direction: incomingRaw ? "higher" : "lower",
        label: incomingRaw ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  const existingTimeframe = parsePresetTimeframeToMinutes(existingRaw);
  const incomingTimeframe = parsePresetTimeframeToMinutes(incomingRaw);
  if (
    existingTimeframe !== null &&
    incomingTimeframe !== null &&
    existingTimeframe !== incomingTimeframe
  ) {
    return {
      delta: {
        direction: incomingTimeframe > existingTimeframe ? "higher" : "lower",
        label: incomingTimeframe > existingTimeframe ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  if (
    typeof existingRaw === "string" &&
    typeof incomingRaw === "string" &&
    schemaEntry.semantic_ranks
  ) {
    return {
      delta: buildPresetRankedStringDelta(
        existingRaw,
        incomingRaw,
        schemaEntry.semantic_ranks,
        higherLabel,
        lowerLabel,
      ),
      hint,
    };
  }
  return {
    delta: undefined,
    hint,
  };
}

function buildPresetParameterDomainContext(
  pathSegments: string[],
  existingRaw: unknown,
  incomingRaw: unknown,
  schemaEntry?: ParameterSchema[string],
): {
  delta?: PresetStructuredDiffDeltaValue;
  hint?: string;
} {
  const tokens = tokenizePresetParameterPath(pathSegments);
  const tokenSet = new Set(tokens);
  const timeframeExisting = parsePresetTimeframeToMinutes(existingRaw);
  const timeframeIncoming = parsePresetTimeframeToMinutes(incomingRaw);
  const existingNumeric = typeof existingRaw === "number" && Number.isFinite(existingRaw);
  const incomingNumeric = typeof incomingRaw === "number" && Number.isFinite(incomingRaw);
  const hasNumericPair = existingNumeric && incomingNumeric;
  const hasTimeframeCue =
    schemaEntry?.unit === "timeframe" ||
    tokenSet.has("timeframe") ||
    tokenSet.has("interval") ||
    tokenSet.has("cadence") ||
    timeframeExisting !== null ||
    timeframeIncoming !== null;
  if (hasTimeframeCue) {
    return {
      delta:
        timeframeExisting !== null &&
        timeframeIncoming !== null &&
        timeframeExisting !== timeframeIncoming
          ? {
              direction: timeframeIncoming > timeframeExisting ? ("higher" as const) : ("lower" as const),
              label: timeframeIncoming > timeframeExisting ? "slower cadence" : "faster cadence",
            }
          : undefined,
      hint: "Domain: timeframe cadence",
    };
  }

  if (tokenSet.has("stop") && tokenSet.has("loss")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "wider stop" : "tighter stop",
          }
        : undefined,
      hint: "Domain: stop-loss guardrail",
    };
  }
  if ((tokenSet.has("take") && tokenSet.has("profit")) || tokenSet.has("target") || tokenSet.has("tp")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "farther target" : "closer target",
          }
        : undefined,
      hint: "Domain: profit target",
    };
  }
  if (
    tokenSet.has("window") ||
    tokenSet.has("lookback") ||
    tokenSet.has("period") ||
    tokenSet.has("bars") ||
    tokenSet.has("bar") ||
    tokenSet.has("length")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "longer lookback" : "shorter lookback",
          }
        : undefined,
      hint: "Domain: lookback window",
    };
  }
  if (tokenSet.has("threshold") || tokenSet.has("trigger")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "stricter threshold" : "looser threshold",
          }
        : undefined,
      hint: "Domain: decision threshold",
    };
  }
  if (tokenSet.has("confidence")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "higher confidence gate" : "lower confidence gate",
          }
        : undefined,
      hint: "Domain: confidence gate",
    };
  }
  if (
    tokenSet.has("position") ||
    tokenSet.has("allocation") ||
    tokenSet.has("exposure") ||
    tokenSet.has("leverage") ||
    tokenSet.has("size") ||
    tokenSet.has("notional")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "higher exposure cap" : "lower exposure cap",
          }
        : undefined,
      hint: "Domain: sizing / exposure",
    };
  }
  if (
    tokenSet.has("risk") ||
    tokenSet.has("drawdown") ||
    tokenSet.has("loss") ||
    tokenSet.has("fraction") ||
    tokenSet.has("ratio") ||
    tokenSet.has("pct") ||
    tokenSet.has("percent")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "larger risk budget" : "smaller risk budget",
          }
        : undefined,
      hint: "Domain: risk / ratio budget",
    };
  }

  if (tokenSet.has("profile") || tokenSet.has("mode") || tokenSet.has("style") || tokenSet.has("regime")) {
    return {
      delta:
        typeof existingRaw === "string" && typeof incomingRaw === "string"
          ? buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_AGGRESSIVENESS_RANKS,
              "more aggressive profile",
              "more conservative profile",
            ) ??
            buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_SPEED_RANKS,
              "faster profile",
              "slower profile",
            ) ??
            buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_CONFIDENCE_RANKS,
              "higher confidence profile",
              "lower confidence profile",
            )
          : undefined,
      hint: "Domain: categorical profile",
    };
  }

  if (Array.isArray(schemaEntry?.enum) && schemaEntry.enum.length) {
    return {
      delta: undefined,
      hint: "Domain: categorical selection",
    };
  }

  if (
    tokenSet.has("allow") ||
    tokenSet.has("enable") ||
    tokenSet.has("disable") ||
    tokenSet.has("reduce") ||
    tokenSet.has("exit")
  ) {
    return {
      delta: undefined,
      hint: "Domain: execution guardrail",
    };
  }

  return {
    delta: undefined,
    hint: undefined,
  };
}

function formatPresetParameterSchemaHint(schemaEntry?: ParameterSchema[string]) {
  if (!schemaEntry) {
    return undefined;
  }
  const parts: string[] = [];
  if (schemaEntry.type) {
    parts.push(schemaEntry.type);
  }
  if (schemaEntry.default !== undefined) {
    parts.push(`default ${formatParameterValue(schemaEntry.default)}`);
  }
  if (Array.isArray(schemaEntry.enum) && schemaEntry.enum.length) {
    parts.push(`options ${schemaEntry.enum.map((value) => formatParameterValue(value)).join("/")}`);
  }
  if (typeof schemaEntry.minimum === "number") {
    parts.push(`min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`);
  }
  if (typeof schemaEntry.maximum === "number") {
    parts.push(`max ${formatComparisonTooltipTuningValue(schemaEntry.maximum)}`);
  }
  if (schemaEntry.unit) {
    parts.push(`unit ${schemaEntry.unit}`);
  }
  if (!parts.length) {
    return undefined;
  }
  return `Schema: ${parts.join(" · ")}`;
}

function getPresetParameterSchemaEntry(
  parameterSchema: ParameterSchema | undefined,
  pathSegments: string[],
) {
  const rootSegment = pathSegments.find((segment) => !segment.startsWith("["));
  if (!rootSegment) {
    return undefined;
  }
  return parameterSchema?.[rootSegment];
}

function buildPresetStructuredDiffDelta(
  existingValue: string,
  incomingValue: string,
  existingRaw: unknown = existingValue,
  incomingRaw: unknown = incomingValue,
  schemaEntry?: ParameterSchema[string],
  domainDelta?: PresetStructuredDiffDeltaValue,
) {
  if (existingValue === incomingValue) {
    return {
      direction: "same" as const,
      label: "match",
    };
  }
  if (schemaEntry?.type) {
    const existingMatchesType = matchesPresetParameterSchemaType(existingRaw, schemaEntry.type);
    const incomingMatchesType = matchesPresetParameterSchemaType(incomingRaw, schemaEntry.type);
    if (incomingRaw !== undefined && !incomingMatchesType) {
      return {
        direction: "lower" as const,
        label: `expected ${schemaEntry.type}`,
      };
    }
    if (existingRaw !== undefined && !existingMatchesType && incomingMatchesType) {
      return {
        direction: "higher" as const,
        label: `matches ${schemaEntry.type}`,
      };
    }
  }
  if (schemaEntry?.default !== undefined) {
    const existingIsDefault = arePresetStructuredDiffValuesEquivalent(existingRaw, schemaEntry.default);
    const incomingIsDefault = arePresetStructuredDiffValuesEquivalent(incomingRaw, schemaEntry.default);
    if (existingRaw === undefined && incomingIsDefault) {
      return {
        direction: "same" as const,
        label: `explicit default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (!existingIsDefault && incomingIsDefault) {
      return {
        direction: "same" as const,
        label: `back to default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (existingIsDefault && !incomingIsDefault) {
      return {
        direction:
          domainDelta?.direction ??
          (typeof incomingRaw === "number" &&
          typeof schemaEntry.default === "number" &&
          Number.isFinite(incomingRaw) &&
          Number.isFinite(schemaEntry.default)
            ? incomingRaw >= schemaEntry.default
              ? ("higher" as const)
              : ("lower" as const)
            : ("higher" as const)),
        label: domainDelta
          ? `${domainDelta.label} vs default ${formatParameterValue(schemaEntry.default)}`
          : `override default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (incomingRaw === undefined && !existingIsDefault) {
      return {
        direction: "lower" as const,
        label: "cleared override",
      };
    }
  }
  if (
    typeof schemaEntry?.minimum === "number" &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw)
  ) {
    const existingMeetsMinimum =
      typeof existingRaw === "number" &&
      Number.isFinite(existingRaw) &&
      existingRaw >= schemaEntry.minimum;
    if (incomingRaw < schemaEntry.minimum) {
      return {
        direction: "lower" as const,
        label: `below min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`,
      };
    }
    if (!existingMeetsMinimum && incomingRaw >= schemaEntry.minimum) {
      return {
        direction: "higher" as const,
        label: `meets min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`,
      };
    }
  }
  if (!existingValue && incomingValue) {
    return {
      direction: "higher" as const,
      label: "added",
    };
  }
  if (existingValue && !incomingValue) {
    return {
      direction: "lower" as const,
      label: "removed",
    };
  }
  if (domainDelta) {
    return domainDelta;
  }
  if (
    typeof existingRaw === "number" &&
    Number.isFinite(existingRaw) &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw)
  ) {
    return formatComparisonTooltipTuningDelta(existingRaw, incomingRaw);
  }
  if (typeof existingRaw === "boolean" && typeof incomingRaw === "boolean") {
    return {
      direction: incomingRaw ? ("higher" as const) : ("lower" as const),
      label: incomingRaw ? "enabled" : "disabled",
    };
  }
  if (
    Array.isArray(existingRaw) &&
    Array.isArray(incomingRaw) &&
    existingRaw.every(isPresetStructuredDiffScalar) &&
    incomingRaw.every(isPresetStructuredDiffScalar)
  ) {
    const existingItems = existingRaw.map((item) => formatParameterValue(item));
    const incomingItems = incomingRaw.map((item) => formatParameterValue(item));
    const addedItems = incomingItems.filter((item) => !existingItems.includes(item));
    const removedItems = existingItems.filter((item) => !incomingItems.includes(item));
    if (addedItems.length && !removedItems.length) {
      return {
        direction: "higher" as const,
        label: `${addedItems.length} added`,
      };
    }
    if (removedItems.length && !addedItems.length) {
      return {
        direction: "lower" as const,
        label: `${removedItems.length} removed`,
      };
    }
    if (addedItems.length || removedItems.length) {
      return {
        direction: addedItems.length >= removedItems.length ? ("higher" as const) : ("lower" as const),
        label: `${addedItems.length} added · ${removedItems.length} removed`,
      };
    }
  }
  return {
    direction: "higher" as const,
    label: "changed",
  };
}

function summarizePresetStructuredDiffGroup(group: PresetStructuredDiffGroup) {
  if (!group.changed_count) {
    return `${group.same_count} unchanged`;
  }
  const parts = [`${group.changed_count} changed`];
  if (group.higher_count) {
    parts.push(`${group.higher_count} higher/add`);
  }
  if (group.lower_count) {
    parts.push(`${group.lower_count} lower/remove`);
  }
  if (group.same_count) {
    parts.push(`${group.same_count} unchanged`);
  }
  return parts.join(" · ");
}

function groupPresetStructuredDiffRows(rows: PresetStructuredDiffRow[]) {
  const groups = rows.reduce<Record<string, PresetStructuredDiffGroup>>((accumulator, row) => {
    const existing = accumulator[row.group_key] ?? {
      changed_count: 0,
      higher_count: 0,
      key: row.group_key,
      label: row.group_label,
      lower_count: 0,
      rows: [],
      same_count: 0,
      summary_label: "",
    };
    existing.rows.push(row);
    if (row.changed) {
      existing.changed_count += 1;
      if (row.delta_direction === "higher") {
        existing.higher_count += 1;
      } else if (row.delta_direction === "lower") {
        existing.lower_count += 1;
      }
    } else {
      existing.same_count += 1;
    }
    accumulator[row.group_key] = existing;
    return accumulator;
  }, {});
  return Object.values(groups)
    .map((group) => ({
      ...group,
      rows: group.rows.sort((left, right) => left.label.localeCompare(right.label)),
      summary_label: summarizePresetStructuredDiffGroup(group),
    }))
    .sort((left, right) => {
      const leftOrder = left.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      return leftOrder - rightOrder || left.label.localeCompare(right.label);
    });
}

function buildPresetStructuredDiffRows(
  existing: ExperimentPresetRevision,
  incoming: ExperimentPresetRevision,
  parameterSchema?: ParameterSchema,
) {
  const rows: PresetStructuredDiffRow[] = [];
  const pushRow = (
    key: string,
    label: string,
    existingValue: string,
    incomingValue: string,
    groupKey: string,
    groupLabel: string,
    groupOrder: number,
    existingRaw: unknown = existingValue,
    incomingRaw: unknown = incomingValue,
    semanticHint?: string,
    schemaEntry?: ParameterSchema[string],
    domainDelta?: PresetStructuredDiffDeltaValue,
  ) => {
    const delta = buildPresetStructuredDiffDelta(
      existingValue,
      incomingValue,
      existingRaw,
      incomingRaw,
      schemaEntry,
      domainDelta,
    );
    rows.push({
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: formatPresetStructuredDiffDisplayValue(existingValue),
      group_key: groupKey,
      group_label: groupLabel,
      group_order: groupOrder,
      incoming_value: formatPresetStructuredDiffDisplayValue(incomingValue),
      key,
      label,
      semantic_hint: semanticHint,
    });
  };
  const formatParameterPathLabel = (segments: string[]) =>
    segments.reduce((label, segment) => {
      if (!label) {
        return segment;
      }
      if (segment.startsWith("[")) {
        return `${label}${segment}`;
      }
      return `${label}.${segment}`;
    }, "");
  const pushParameterRow = (
    pathSegments: string[],
    existingParameter: unknown,
    incomingParameter: unknown,
  ) => {
    const label = formatParameterPathLabel(pathSegments) || "Parameter bundle";
    const existingValue = existingParameter === undefined ? "" : formatParameterValue(existingParameter);
    const incomingValue = incomingParameter === undefined ? "" : formatParameterValue(incomingParameter);
    const schemaEntry = getPresetParameterSchemaEntry(parameterSchema, pathSegments);
    const strategyContext = buildPresetParameterStrategyContext(
      existingParameter,
      incomingParameter,
      schemaEntry,
    );
    const domainContext = buildPresetParameterDomainContext(
      pathSegments,
      existingParameter,
      incomingParameter,
      schemaEntry,
    );
    pushRow(
      `parameter:${label}`,
      label,
      existingValue,
      incomingValue,
      "parameters",
      "Parameters",
      3,
      existingParameter,
      incomingParameter,
      joinPresetStructuredDiffHints(
        formatPresetParameterSchemaHint(schemaEntry),
        strategyContext.hint,
        domainContext.hint,
      ),
      schemaEntry,
      strategyContext.delta ?? domainContext.delta,
    );
  };
  const appendParameterRows = (
    existingParameter: unknown,
    incomingParameter: unknown,
    pathSegments: string[] = [],
  ) => {
    if (isPresetStructuredDiffObject(existingParameter) && incomingParameter === undefined) {
      appendParameterRows(existingParameter, {}, pathSegments);
      return;
    }
    if (existingParameter === undefined && isPresetStructuredDiffObject(incomingParameter)) {
      appendParameterRows({}, incomingParameter, pathSegments);
      return;
    }
    if (Array.isArray(existingParameter) && incomingParameter === undefined) {
      if (existingParameter.every(isPresetStructuredDiffScalar)) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
      } else {
        appendParameterRows(existingParameter, [], pathSegments);
      }
      return;
    }
    if (existingParameter === undefined && Array.isArray(incomingParameter)) {
      if (incomingParameter.every(isPresetStructuredDiffScalar)) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
      } else {
        appendParameterRows([], incomingParameter, pathSegments);
      }
      return;
    }
    if (
      Array.isArray(existingParameter) &&
      Array.isArray(incomingParameter) &&
      existingParameter.every(isPresetStructuredDiffScalar) &&
      incomingParameter.every(isPresetStructuredDiffScalar)
    ) {
      pushParameterRow(pathSegments, existingParameter, incomingParameter);
      return;
    }
    if (Array.isArray(existingParameter) && Array.isArray(incomingParameter)) {
      const length = Math.max(existingParameter.length, incomingParameter.length);
      for (let index = 0; index < length; index += 1) {
        appendParameterRows(existingParameter[index], incomingParameter[index], [...pathSegments, `[${index}]`]);
      }
      return;
    }
    if (isPresetStructuredDiffObject(existingParameter) && isPresetStructuredDiffObject(incomingParameter)) {
      const keys = Array.from(
        new Set([...Object.keys(existingParameter), ...Object.keys(incomingParameter)]),
      ).sort();
      if (!keys.length) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
        return;
      }
      keys.forEach((key) => {
        appendParameterRows(existingParameter[key], incomingParameter[key], [...pathSegments, key]);
      });
      return;
    }
    pushParameterRow(pathSegments, existingParameter, incomingParameter);
  };

  pushRow("name", "Name", existing.name, incoming.name, "identity", "Identity", 0);
  pushRow(
    "description",
    "Description",
    existing.description,
    incoming.description,
    "identity",
    "Identity",
    0,
  );
  pushRow(
    "strategy",
    "Strategy",
    existing.strategy_id ?? "",
    incoming.strategy_id ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "timeframe",
    "Timeframe",
    existing.timeframe ?? "",
    incoming.timeframe ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "benchmark_family",
    "Benchmark family",
    existing.benchmark_family ?? "",
    incoming.benchmark_family ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "tags",
    "Tags",
    existing.tags.join(", "),
    incoming.tags.join(", "),
    "metadata",
    "Metadata",
    2,
  );

  const parameterKeys = Array.from(
    new Set([...Object.keys(existing.parameters), ...Object.keys(incoming.parameters)]),
  ).sort();
  if (!parameterKeys.length) {
    pushRow("parameters", "Parameter bundle", "", "", "parameters", "Parameters", 3);
  } else {
    parameterKeys.forEach((key) => {
      appendParameterRows(existing.parameters[key], incoming.parameters[key], [key]);
    });
  }
  return rows;
}

function describePresetRevisionDiff(
  revision: ExperimentPresetRevision,
  reference: ExperimentPresetRevision | null,
  basisLabel: string,
  parameterSchema?: ParameterSchema,
): PresetRevisionDiff {
  const rows = buildPresetStructuredDiffRows(
    reference ?? buildEmptyPresetRevisionSnapshot(),
    revision,
    parameterSchema,
  );
  const changedGroups = groupPresetStructuredDiffRows(rows.filter((row) => row.changed));
  const unchangedGroups = groupPresetStructuredDiffRows(rows.filter((row) => !row.changed));
  const searchTexts = rows.map(
    (row) =>
      `${row.label} ${row.semantic_hint ?? ""} ${row.existing_value} ${row.incoming_value} ${row.delta_label}`,
  );
  const changeCount = changedGroups.reduce((total, group) => total + group.changed_count, 0);

  return {
    basisLabel,
    changeCount,
    changedGroups,
    unchangedGroups,
    searchTexts,
    summary: changeCount
      ? `${changeCount} change${changeCount === 1 ? "" : "s"} vs ${basisLabel}.`
      : `Matches ${basisLabel}.`,
  };
}

function describePresetDraftConflict(
  preset: ExperimentPreset,
  form: typeof defaultPresetForm,
  parameterSchema?: ParameterSchema,
): PresetDraftConflict {
  const savedForm = buildPresetFormFromPreset(preset);
  let normalizedDraftParameters = form.parameters_text.trim();
  let parsedDraftParameters: Record<string, unknown> = {};
  let hasInvalidParameters = false;
  if (normalizedDraftParameters) {
    try {
      parsedDraftParameters = parseJsonObjectInput(form.parameters_text);
      normalizedDraftParameters = JSON.stringify(parsedDraftParameters, null, 2);
    } catch {
      hasInvalidParameters = true;
    }
  }
  const rows: PresetStructuredDiffRow[] = [];
  const pushRow = (
    key: string,
    label: string,
    existingValue: string,
    incomingValue: string,
    groupKey: string,
    groupLabel: string,
    groupOrder: number,
  ) => {
    const delta = buildPresetStructuredDiffDelta(existingValue, incomingValue);
    rows.push({
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: formatPresetStructuredDiffDisplayValue(existingValue),
      group_key: groupKey,
      group_label: groupLabel,
      group_order: groupOrder,
      incoming_value: formatPresetStructuredDiffDisplayValue(incomingValue),
      key,
      label,
    });
  };
  pushRow("name", "Name", savedForm.name, form.name, "identity", "Draft fields", 0);
  pushRow(
    "description",
    "Description",
    savedForm.description,
    form.description,
    "identity",
    "Draft fields",
    0,
  );
  pushRow("strategy", "Strategy", savedForm.strategy_id, form.strategy_id, "scope", "Scope", 1);
  pushRow(
    "timeframe",
    "Timeframe",
    savedForm.timeframe.trim(),
    form.timeframe.trim(),
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "benchmark_family",
    "Benchmark family",
    savedForm.benchmark_family.trim(),
    form.benchmark_family.trim(),
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "tags",
    "Tags",
    parseExperimentTags(savedForm.tags_text).join(", "),
    parseExperimentTags(form.tags_text).join(", "),
    "metadata",
    "Metadata",
    2,
  );
  if (hasInvalidParameters) {
    pushRow(
      "parameters_json",
      "Parameters JSON (invalid draft)",
      savedForm.parameters_text.trim(),
      normalizedDraftParameters,
      "parameters",
      "Parameters",
      3,
    );
  } else {
    const revisionRows = buildPresetStructuredDiffRows(
      buildCurrentPresetRevisionSnapshot(preset),
      {
        ...buildCurrentPresetRevisionSnapshot(preset),
        name: form.name,
        description: form.description,
        strategy_id: form.strategy_id || null,
        timeframe: form.timeframe.trim() || null,
        benchmark_family: form.benchmark_family.trim() || null,
        tags: parseExperimentTags(form.tags_text),
        parameters: parsedDraftParameters,
      },
      parameterSchema,
    );
    rows.push(...revisionRows.filter((row) => row.group_key === "parameters"));
  }
  const groups = groupPresetStructuredDiffRows(rows.filter((row) => row.changed));
  const changeCount = groups.reduce((total, group) => total + group.changed_count, 0);
  return {
    changeCount,
    groups,
    hasInvalidParameters,
    summary: changeCount
      ? `${changeCount} unsaved draft field${changeCount === 1 ? "" : "s"} differ from the saved bundle.`
      : "Current draft matches the saved bundle.",
  };
}

function matchesPresetRevisionFilter(
  revision: ExperimentPresetRevision,
  diff: PresetRevisionDiff,
  filter: PresetRevisionFilterState,
) {
  if (filter.action !== "all" && revision.action !== filter.action) {
    return false;
  }
  const query = filter.query.trim().toLowerCase();
  if (!query) {
    return true;
  }
  const searchable = [
    revision.revision_id,
    revision.actor,
    revision.reason,
    revision.action,
    revision.name,
    revision.description,
    revision.strategy_id ?? "",
    revision.timeframe ?? "",
    revision.benchmark_family ?? "",
    revision.tags.join(" "),
    Object.keys(revision.parameters).join(" "),
    diff.summary,
    ...diff.searchTexts,
  ]
    .join(" ")
    .toLowerCase();
  return searchable.includes(query);
}

const defaultRunHistoryFilter: RunHistoryFilter = {
  strategy_id: ALL_FILTER_VALUE,
  strategy_version: ALL_FILTER_VALUE,
  preset_id: "",
  benchmark_family: "",
  tag: "",
  dataset_identity: "",
  filter_expr: "",
  collection_query_label: "",
};

function sanitizeRunHistoryFilter(filter: RunHistoryFilter): RunHistoryFilter {
  return {
    strategy_id: filter.strategy_id || ALL_FILTER_VALUE,
    strategy_version: filter.strategy_version || ALL_FILTER_VALUE,
    preset_id: filter.preset_id.trim(),
    benchmark_family: filter.benchmark_family.trim(),
    tag: filter.tag.trim(),
    dataset_identity: filter.dataset_identity.trim(),
    filter_expr: filter.filter_expr.trim(),
    collection_query_label: filter.collection_query_label.trim(),
  };
}

function cloneRunHistoryFilter(filter: RunHistoryFilter): RunHistoryFilter {
  return sanitizeRunHistoryFilter({ ...filter });
}

function hasRunHistoryFilterCriteria(filter: RunHistoryFilter) {
  const candidate = sanitizeRunHistoryFilter(filter);
  return Boolean(
    candidate.strategy_id !== ALL_FILTER_VALUE
    || candidate.strategy_version !== ALL_FILTER_VALUE
    || candidate.preset_id
    || candidate.benchmark_family
    || candidate.tag
    || candidate.dataset_identity
    || candidate.filter_expr,
  );
}

function areRunHistoryFiltersEquivalent(left: RunHistoryFilter, right: RunHistoryFilter) {
  const normalizedLeft = sanitizeRunHistoryFilter(left);
  const normalizedRight = sanitizeRunHistoryFilter(right);
  return (
    normalizedLeft.strategy_id === normalizedRight.strategy_id
    && normalizedLeft.strategy_version === normalizedRight.strategy_version
    && normalizedLeft.preset_id === normalizedRight.preset_id
    && normalizedLeft.benchmark_family === normalizedRight.benchmark_family
    && normalizedLeft.tag === normalizedRight.tag
    && normalizedLeft.dataset_identity === normalizedRight.dataset_identity
    && normalizedLeft.filter_expr === normalizedRight.filter_expr
  );
}

function buildRunHistorySavedFilterStorageKey(surfaceKey: RunHistorySurfaceKey) {
  return `${RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX}:${surfaceKey}`;
}

function normalizeSavedRunHistoryFilterPreset(value: unknown): SavedRunHistoryFilterPreset | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<SavedRunHistoryFilterPreset>;
  if (
    typeof candidate.filter_id !== "string"
    || typeof candidate.label !== "string"
    || typeof candidate.created_at !== "string"
    || typeof candidate.updated_at !== "string"
    || !candidate.filter
    || typeof candidate.filter !== "object"
  ) {
    return null;
  }
  const filterCandidate = candidate.filter as Partial<RunHistoryFilter>;
  return {
    filter_id: candidate.filter_id,
    label: candidate.label,
    created_at: candidate.created_at,
    updated_at: candidate.updated_at,
    filter: sanitizeRunHistoryFilter({
      ...defaultRunHistoryFilter,
      strategy_id:
        typeof filterCandidate.strategy_id === "string"
          ? filterCandidate.strategy_id
          : defaultRunHistoryFilter.strategy_id,
      strategy_version:
        typeof filterCandidate.strategy_version === "string"
          ? filterCandidate.strategy_version
          : defaultRunHistoryFilter.strategy_version,
      preset_id:
        typeof filterCandidate.preset_id === "string"
          ? filterCandidate.preset_id
          : defaultRunHistoryFilter.preset_id,
      benchmark_family:
        typeof filterCandidate.benchmark_family === "string"
          ? filterCandidate.benchmark_family
          : defaultRunHistoryFilter.benchmark_family,
      tag: typeof filterCandidate.tag === "string" ? filterCandidate.tag : defaultRunHistoryFilter.tag,
      dataset_identity:
        typeof filterCandidate.dataset_identity === "string"
          ? filterCandidate.dataset_identity
          : defaultRunHistoryFilter.dataset_identity,
      filter_expr:
        typeof filterCandidate.filter_expr === "string"
          ? filterCandidate.filter_expr
          : defaultRunHistoryFilter.filter_expr,
      collection_query_label:
        typeof filterCandidate.collection_query_label === "string"
          ? filterCandidate.collection_query_label
          : defaultRunHistoryFilter.collection_query_label,
    }),
  };
}

function loadSavedRunHistoryFilterPresets(surfaceKey: RunHistorySurfaceKey): SavedRunHistoryFilterPreset[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(buildRunHistorySavedFilterStorageKey(surfaceKey));
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<SavedRunHistoryFilterPresetStateV1> | null;
    if (parsed?.version !== 1 || !Array.isArray(parsed.filters)) {
      return [];
    }
    return parsed.filters
      .map((entry) => normalizeSavedRunHistoryFilterPreset(entry))
      .filter((entry): entry is SavedRunHistoryFilterPreset => entry !== null);
  } catch {
    return [];
  }
}

function persistSavedRunHistoryFilterPresets(
  surfaceKey: RunHistorySurfaceKey,
  presets: SavedRunHistoryFilterPreset[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      buildRunHistorySavedFilterStorageKey(surfaceKey),
      JSON.stringify({
        version: 1,
        filters: presets.map((entry) => ({
          ...entry,
          filter: sanitizeRunHistoryFilter(entry.filter),
        })),
      } satisfies SavedRunHistoryFilterPresetStateV1),
    );
  } catch {
    // Ignore localStorage failures for saved run-history filters.
  }
}

function describeRunHistoryFilter(filter: RunHistoryFilter, presets: ExperimentPreset[], strategies: Strategy[]) {
  const candidate = sanitizeRunHistoryFilter(filter);
  const parts: string[] = [];
  if (candidate.strategy_id !== ALL_FILTER_VALUE) {
    const strategy = strategies.find((item) => item.strategy_id === candidate.strategy_id);
    parts.push(`Strategy ${strategy?.name ?? candidate.strategy_id}`);
  }
  if (candidate.strategy_version !== ALL_FILTER_VALUE) {
    parts.push(`Version ${candidate.strategy_version}`);
  }
  if (candidate.preset_id) {
    const preset = presets.find((item) => item.preset_id === candidate.preset_id);
    parts.push(`Preset ${preset?.name ?? candidate.preset_id}`);
  }
  if (candidate.benchmark_family) {
    parts.push(`Benchmark ${candidate.benchmark_family}`);
  }
  if (candidate.tag) {
    parts.push(`Tag ${candidate.tag}`);
  }
  if (candidate.dataset_identity) {
    parts.push(`Dataset ${candidate.dataset_identity}`);
  }
  if (candidate.filter_expr) {
    parts.push(
      candidate.collection_query_label
        ? `Collection ${candidate.collection_query_label}`
        : "Collection expression",
    );
  }
  return parts;
}

const DEFAULT_COMPARISON_INTENT: ComparisonIntent = "benchmark_validation";
const comparisonIntentOptions: ComparisonIntent[] = [
  "benchmark_validation",
  "execution_regression",
  "strategy_tuning",
];

function parseExperimentTags(value: string) {
  return Array.from(
    new Set(
      value
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
    ),
  );
}

function parseJsonObjectInput(value: string) {
  const trimmed = value.trim();
  if (!trimmed) {
    return {};
  }
  const parsed = JSON.parse(trimmed) as unknown;
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("Parameter bundle must be a JSON object.");
  }
  return parsed as Record<string, unknown>;
}

function formatPresetLifecycleStage(stage: string) {
  return stage.replaceAll("_", " ");
}

function buildRunSubmissionPayload(form: typeof defaultRunForm, extras: Record<string, unknown> = {}) {
  const presetId = form.preset_id.trim();
  const benchmarkFamily = form.benchmark_family.trim();
  return {
    strategy_id: form.strategy_id,
    symbol: form.symbol,
    timeframe: form.timeframe,
    initial_cash: form.initial_cash,
    fee_rate: form.fee_rate,
    slippage_bps: form.slippage_bps,
    parameters: {},
    tags: parseExperimentTags(form.tags_text),
    preset_id: presetId || null,
    benchmark_family: benchmarkFamily || null,
    ...extras,
  };
}

function normalizeRunFormPreset(
  current: typeof defaultRunForm,
  presets: ExperimentPreset[],
) {
  if (!current.preset_id) {
    return current;
  }
  const matchingPreset = presets.find((preset) => preset.preset_id === current.preset_id);
  if (
    matchingPreset &&
    matchingPreset.lifecycle.stage !== "archived" &&
    (!matchingPreset.strategy_id || matchingPreset.strategy_id === current.strategy_id) &&
    (!matchingPreset.timeframe || matchingPreset.timeframe === current.timeframe)
  ) {
    return current;
  }
  return {
    ...current,
    preset_id: "",
  };
}

function resolveMarketDataSymbol(instrumentId: string) {
  const separatorIndex = instrumentId.indexOf(":");
  return separatorIndex >= 0 ? instrumentId.slice(separatorIndex + 1) : instrumentId;
}

function buildMarketDataInstrumentFocusKey(
  instrument: MarketDataStatus["instruments"][number],
) {
  return `${instrument.instrument_id}|${instrument.timeframe}`;
}

function isMarketDataInstrumentAtRisk(
  instrument: MarketDataStatus["instruments"][number],
) {
  return (
    instrument.sync_status !== "synced"
    || instrument.failure_count_24h > 0
    || (instrument.lag_seconds ?? 0) > 0
    || instrument.backfill_gap_windows.length > 0
    || instrument.issues.length > 0
  );
}

function resolvePreferredMarketDataInstrument(
  marketStatus: MarketDataStatus,
  preferredKey: string | null,
) {
  if (preferredKey) {
    const preferredInstrument = marketStatus.instruments.find(
      (instrument) => buildMarketDataInstrumentFocusKey(instrument) === preferredKey,
    );
    if (preferredInstrument) {
      return preferredInstrument;
    }
  }
  return (
    marketStatus.instruments.find((instrument) => isMarketDataInstrumentAtRisk(instrument))
    ?? marketStatus.instruments[0]
    ?? null
  );
}

function formatWorkflowToken(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value.replaceAll("_", " ");
}

type LinkedMarketInstrumentContext = {
  instrument: MarketDataStatus["instruments"][number];
  focusKey: string;
  symbol: string;
  timeframe: string;
  matchReason: string;
  candidateCount: number;
  candidateLabels: string[];
  primaryFocusPolicy: string;
  primaryFocusReason: string;
};

type MarketDataLinkableAlertRecord = {
  alert_id?: string | null;
  category?: string | null;
  summary: string;
  detail: string;
  run_id?: string | null;
  session_id?: string | null;
  symbol?: string | null;
  symbols?: string[];
  timeframe?: string | null;
  primary_focus?: OperatorAlertPrimaryFocus | null;
  source?: string | null;
  provider_recovery_symbols?: string[];
  provider_recovery_timeframe?: string | null;
};

type MarketDataIncidentHistoryEntry = {
  entryId: string;
  occurredAt: string;
  sourceLabel: string;
  statusLabel: string;
  summary: string;
  detail: string;
  tone: "critical" | "warning" | "neutral";
};

type ProviderRecoveryMarketContextSummary = {
  summary: string;
  fieldSummaries: string[];
};

type MarketDataProviderProvenanceEventRecord = {
  event: OperatorVisibility["incident_events"][number];
  link: LinkedMarketInstrumentContext | null;
  provider: string;
  vendorField: string;
  provenanceSummary: string;
  fieldSummaries: string[];
  severityRank: number;
  occurredAtMs: number;
  searchText: string;
};

type MarketDataPrimaryFocusSelection = {
  instrument: MarketDataStatus["instruments"][number];
  candidateCount: number;
  candidateLabels: string[];
  primaryFocusPolicy: string;
  primaryFocusReason: string;
};

function formatMarketContextFieldProvenance(
  label: string,
  provenance?: OperatorAlertMarketContextProvenance["symbol"] | null,
) {
  if (!provenance) {
    return null;
  }
  const scope = provenance.scope?.trim() || null;
  const path = provenance.path?.trim() || null;
  if (!scope && !path) {
    return null;
  }
  return `${label} ${scope && path ? `${scope} -> ${path}` : scope ?? path}`;
}

function summarizeProviderRecoveryMarketContextProvenance(providerRecovery: {
  provider?: string | null;
  market_context_provenance?: OperatorAlertMarketContextProvenance | null;
}): ProviderRecoveryMarketContextSummary | null {
  const provenance = providerRecovery.market_context_provenance;
  if (!provenance) {
    return null;
  }
  const fieldSummaries = [
    formatMarketContextFieldProvenance("symbol", provenance.symbol),
    formatMarketContextFieldProvenance("symbols", provenance.symbols),
    formatMarketContextFieldProvenance("timeframe", provenance.timeframe),
    formatMarketContextFieldProvenance("primary focus", provenance.primary_focus),
  ].filter((value): value is string => Boolean(value));
  const summaryLead = [
    provenance.provider?.trim() || providerRecovery.provider?.trim() || null,
    provenance.vendor_field?.trim() ? `via ${provenance.vendor_field.trim()}` : null,
  ].filter(Boolean);
  const parts = [
    summaryLead.length ? summaryLead.join(" ") : null,
    ...fieldSummaries,
  ].filter((value): value is string => Boolean(value));
  if (!parts.length) {
    return null;
  }
  return {
    summary: `Market-context provenance: ${parts.join(" / ")}`,
    fieldSummaries,
  };
}

function serializeLinkedMarketInstrumentContext(link: LinkedMarketInstrumentContext | null) {
  if (!link) {
    return null;
  }
  return {
    symbol: link.symbol,
    timeframe: link.timeframe,
    match_reason: link.matchReason,
    candidate_count: link.candidateCount,
    candidate_labels: link.candidateLabels,
    primary_focus_policy: link.primaryFocusPolicy,
    primary_focus_reason: link.primaryFocusReason,
  };
}

function getOperatorSeverityRank(severity: string) {
  switch (severity) {
    case "critical":
      return 3;
    case "warning":
      return 2;
    case "info":
      return 1;
    default:
      return 0;
  }
}

function normalizeMarketDataProvenanceExportSort(
  value: unknown,
): MarketDataProvenanceExportSort {
  return value === "oldest" || value === "provider" || value === "severity" || value === "newest"
    ? value
    : defaultMarketDataProvenanceExportFilterState.sort;
}

function normalizeMarketDataProvenanceExportFilterState(
  value: unknown,
): MarketDataProvenanceExportFilterState {
  if (!value || typeof value !== "object") {
    return { ...defaultMarketDataProvenanceExportFilterState };
  }
  const candidate = value as Partial<MarketDataProvenanceExportFilterState>;
  return {
    provider:
      typeof candidate.provider === "string" && candidate.provider.trim().length
        ? candidate.provider
        : defaultMarketDataProvenanceExportFilterState.provider,
    vendor_field:
      typeof candidate.vendor_field === "string" && candidate.vendor_field.trim().length
        ? candidate.vendor_field
        : defaultMarketDataProvenanceExportFilterState.vendor_field,
    search_query:
      typeof candidate.search_query === "string"
        ? candidate.search_query
        : defaultMarketDataProvenanceExportFilterState.search_query,
    sort: normalizeMarketDataProvenanceExportSort(candidate.sort),
  };
}

function normalizeMarketDataProvenanceExportHistoryEntry(
  value: unknown,
): MarketDataProvenanceExportHistoryEntry | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<MarketDataProvenanceExportHistoryEntry>;
  if (
    typeof candidate.export_id !== "string"
    || typeof candidate.exported_at !== "string"
    || typeof candidate.focus_key !== "string"
    || typeof candidate.focus_label !== "string"
    || typeof candidate.symbol !== "string"
    || typeof candidate.timeframe !== "string"
    || typeof candidate.provider !== "string"
    || typeof candidate.venue !== "string"
    || typeof candidate.result_count !== "number"
    || typeof candidate.provider_provenance_count !== "number"
    || !Array.isArray(candidate.provider_labels)
    || typeof candidate.content !== "string"
  ) {
    return null;
  }
  return {
    export_id: candidate.export_id,
    exported_at: candidate.exported_at,
    focus_key: candidate.focus_key,
    focus_label: candidate.focus_label,
    symbol: candidate.symbol,
    timeframe: candidate.timeframe,
    provider: candidate.provider,
    venue: candidate.venue,
    result_count: candidate.result_count,
    provider_provenance_count: candidate.provider_provenance_count,
    provider_labels: candidate.provider_labels.filter((label): label is string => typeof label === "string"),
    filter: normalizeMarketDataProvenanceExportFilterState(candidate.filter),
    content: candidate.content,
  };
}

function loadPersistedMarketDataProvenanceExportState(): {
  activeFilter: MarketDataProvenanceExportFilterState;
  history: MarketDataProvenanceExportHistoryEntry[];
} {
  if (typeof window === "undefined") {
    return {
      activeFilter: { ...defaultMarketDataProvenanceExportFilterState },
      history: [],
    };
  }
  try {
    const raw = window.localStorage.getItem(MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY);
    if (!raw) {
      return {
        activeFilter: { ...defaultMarketDataProvenanceExportFilterState },
        history: [],
      };
    }
    const parsed = JSON.parse(raw) as Partial<MarketDataProvenanceExportStateV1> | null;
    if (parsed?.version !== MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION) {
      return {
        activeFilter: { ...defaultMarketDataProvenanceExportFilterState },
        history: [],
      };
    }
    return {
      activeFilter: normalizeMarketDataProvenanceExportFilterState(parsed.active_filter),
      history: Array.isArray(parsed.history)
        ? parsed.history
            .map((entry) => normalizeMarketDataProvenanceExportHistoryEntry(entry))
            .filter((entry): entry is MarketDataProvenanceExportHistoryEntry => entry !== null)
            .slice(0, MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES)
        : [],
    };
  } catch {
    return {
      activeFilter: { ...defaultMarketDataProvenanceExportFilterState },
      history: [],
    };
  }
}

function persistMarketDataProvenanceExportState(state: {
  activeFilter: MarketDataProvenanceExportFilterState;
  history: MarketDataProvenanceExportHistoryEntry[];
}) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: MarketDataProvenanceExportStateV1 = {
      version: MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION,
      active_filter: normalizeMarketDataProvenanceExportFilterState(state.activeFilter),
      history: state.history.slice(0, MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES),
    };
    window.localStorage.setItem(
      MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    // Ignore localStorage failures for provider provenance export state.
  }
}

function formatMarketDataProvenanceExportFilterSummary(
  filter: MarketDataProvenanceExportFilterState,
) {
  const parts = [
    filter.provider !== ALL_FILTER_VALUE ? `provider ${filter.provider}` : null,
    filter.vendor_field !== ALL_FILTER_VALUE ? `vendor field ${filter.vendor_field}` : null,
    filter.search_query.trim() ? `search ${filter.search_query.trim()}` : null,
    filter.sort !== "newest" ? `sort ${filter.sort}` : null,
  ].filter((value): value is string => Boolean(value));
  return parts.length ? parts.join(" / ") : "All providers · newest first";
}

function formatProviderProvenanceAnalyticsQuerySummary(
  query: ProviderProvenanceAnalyticsQueryState,
) {
  const parts = [
    query.scope === "all_focuses" ? "all focuses" : "current focus",
    `${query.window_days}d window`,
    query.provider_label !== ALL_FILTER_VALUE ? `provider ${query.provider_label}` : null,
    query.vendor_field !== ALL_FILTER_VALUE ? `vendor field ${query.vendor_field}` : null,
    query.market_data_provider !== ALL_FILTER_VALUE ? `market data ${query.market_data_provider}` : null,
    query.requested_by_tab_id !== ALL_FILTER_VALUE ? `requester ${query.requested_by_tab_id}` : null,
    query.scheduler_alert_category !== ALL_FILTER_VALUE
      ? `scheduler category ${query.scheduler_alert_category}`
      : null,
    query.scheduler_alert_status !== ALL_FILTER_VALUE
      ? `scheduler status ${query.scheduler_alert_status}`
      : null,
    query.scheduler_alert_narrative_facet !== "all_occurrences"
      ? `scheduler ${formatProviderProvenanceSchedulerNarrativeFacet(query.scheduler_alert_narrative_facet)}`
      : null,
    query.search_query.trim() ? `search ${query.search_query.trim()}` : null,
  ].filter((value): value is string => Boolean(value));
  return parts.join(" / ");
}

function normalizeProviderProvenanceDashboardLayoutState(
  layout: Partial<ProviderProvenanceDashboardLayout> | null | undefined,
): ProviderProvenanceDashboardLayout {
  const normalizedGovernanceQueueView = normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueView(
    layout?.governance_queue_view,
  );
  return {
    highlight_panel:
      layout?.highlight_panel === "drift"
      || layout?.highlight_panel === "burn_up"
      || layout?.highlight_panel === "rollups"
      || layout?.highlight_panel === "scheduler_alerts"
      || layout?.highlight_panel === "recent_exports"
        ? layout.highlight_panel
        : "overview",
    show_rollups: layout?.show_rollups !== false,
    show_time_series: layout?.show_time_series !== false,
    show_recent_exports: layout?.show_recent_exports !== false,
    ...(normalizedGovernanceQueueView
      ? {
          governance_queue_view: normalizedGovernanceQueueView,
        }
      : {}),
  };
}

function normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
  value: string | null | undefined,
) {
  return value === "updated_desc"
    || value === "updated_asc"
    || value === "created_desc"
    || value === "created_asc"
    || value === "source_template_asc"
    || value === "source_template_desc"
    || value === DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT
    ? value
    : DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT;
}

function normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueView(
  queueView: Partial<ProviderProvenanceSchedulerNarrativeGovernanceQueueView> | null | undefined,
): ProviderProvenanceSchedulerNarrativeGovernanceQueueView | null {
  const normalized: ProviderProvenanceSchedulerNarrativeGovernanceQueueView = {};
  if (
    queueView?.queue_state === "pending_approval"
    || queueView?.queue_state === "ready_to_apply"
    || queueView?.queue_state === "completed"
  ) {
    normalized.queue_state = queueView.queue_state;
  }
  if (
    queueView?.item_type === "template"
    || queueView?.item_type === "registry"
    || queueView?.item_type === "stitched_report_view"
    || queueView?.item_type === "stitched_report_governance_registry"
  ) {
    normalized.item_type = queueView.item_type;
  }
  if (typeof queueView?.approval_lane === "string" && queueView.approval_lane.trim()) {
    normalized.approval_lane = queueView.approval_lane.trim();
  }
  if (typeof queueView?.approval_priority === "string" && queueView.approval_priority.trim()) {
    normalized.approval_priority = queueView.approval_priority.trim();
  }
  if (typeof queueView?.policy_template_id === "string") {
    normalized.policy_template_id = queueView.policy_template_id.trim();
  }
  if (typeof queueView?.policy_catalog_id === "string") {
    normalized.policy_catalog_id = queueView.policy_catalog_id.trim();
  }
  if (typeof queueView?.source_hierarchy_step_template_id === "string") {
    normalized.source_hierarchy_step_template_id = queueView.source_hierarchy_step_template_id.trim();
  }
  if (
    typeof queueView?.source_hierarchy_step_template_name === "string"
    && queueView.source_hierarchy_step_template_name.trim()
  ) {
    normalized.source_hierarchy_step_template_name = queueView.source_hierarchy_step_template_name.trim();
  }
  if (typeof queueView?.search === "string" && queueView.search.trim()) {
    normalized.search = queueView.search.trim();
  }
  const normalizedSort = normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
    queueView?.sort,
  );
  if (Object.keys(normalized).length || normalizedSort !== DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT) {
    normalized.sort = normalizedSort;
  }
  return Object.keys(normalized).length ? normalized : null;
}

function buildProviderProvenanceSchedulerNarrativeGovernanceQueueFilterStateFromView(
  queueView: Partial<ProviderProvenanceSchedulerNarrativeGovernanceQueueView> | null | undefined,
): ProviderProvenanceSchedulerNarrativeGovernanceQueueFilterState {
  const normalized = normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueView(queueView);
  return {
    queue_state:
      normalized?.queue_state === "pending_approval"
      || normalized?.queue_state === "ready_to_apply"
      || normalized?.queue_state === "completed"
        ? normalized.queue_state
        : ALL_FILTER_VALUE,
    item_type:
      normalized?.item_type === "template"
      || normalized?.item_type === "registry"
      || normalized?.item_type === "stitched_report_view"
      || normalized?.item_type === "stitched_report_governance_registry"
        ? normalized.item_type
        : ALL_FILTER_VALUE,
    approval_lane: normalized?.approval_lane ?? ALL_FILTER_VALUE,
    approval_priority: normalized?.approval_priority ?? ALL_FILTER_VALUE,
    policy_template_id:
      typeof normalized?.policy_template_id === "string"
        ? normalized.policy_template_id
        : ALL_FILTER_VALUE,
    policy_catalog_id:
      typeof normalized?.policy_catalog_id === "string"
        ? normalized.policy_catalog_id
        : ALL_FILTER_VALUE,
    source_hierarchy_step_template_id:
      typeof normalized?.source_hierarchy_step_template_id === "string"
        ? normalized.source_hierarchy_step_template_id
        : ALL_FILTER_VALUE,
    search: normalized?.search ?? "",
    sort:
      normalized?.sort ?? DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT,
  };
}

function buildProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterStateFromView(
  queueView: Partial<ProviderProvenanceSchedulerNarrativeGovernanceQueueView> | null | undefined,
): ProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterState {
  const normalized = normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueView(queueView);
  return {
    queue_state:
      normalized?.queue_state === "pending_approval"
      || normalized?.queue_state === "ready_to_apply"
      || normalized?.queue_state === "completed"
        ? normalized.queue_state
        : ALL_FILTER_VALUE,
    approval_lane: normalized?.approval_lane ?? ALL_FILTER_VALUE,
    approval_priority: normalized?.approval_priority ?? ALL_FILTER_VALUE,
    policy_template_id:
      typeof normalized?.policy_template_id === "string"
        ? normalized.policy_template_id
        : ALL_FILTER_VALUE,
    policy_catalog_id:
      typeof normalized?.policy_catalog_id === "string"
        ? normalized.policy_catalog_id
        : ALL_FILTER_VALUE,
    search: normalized?.search ?? "",
    sort:
      normalized?.sort ?? DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT,
  };
}

function buildProviderProvenanceSchedulerNarrativeGovernanceQueueViewPayload(
  filter: ProviderProvenanceSchedulerNarrativeGovernanceQueueFilterState,
  sourceTemplateNameMap: Map<string, string>,
): ProviderProvenanceSchedulerNarrativeGovernanceQueueView | null {
  const normalized: ProviderProvenanceSchedulerNarrativeGovernanceQueueView = {};
  if (filter.queue_state !== ALL_FILTER_VALUE) {
    normalized.queue_state = filter.queue_state;
  }
  if (filter.item_type !== ALL_FILTER_VALUE) {
    normalized.item_type = filter.item_type;
  }
  if (filter.approval_lane !== ALL_FILTER_VALUE) {
    normalized.approval_lane = filter.approval_lane;
  }
  if (filter.approval_priority !== ALL_FILTER_VALUE) {
    normalized.approval_priority = filter.approval_priority;
  }
  if (filter.policy_template_id !== ALL_FILTER_VALUE) {
    normalized.policy_template_id = filter.policy_template_id;
  }
  if (filter.policy_catalog_id !== ALL_FILTER_VALUE) {
    normalized.policy_catalog_id = filter.policy_catalog_id;
  }
  if (filter.source_hierarchy_step_template_id !== ALL_FILTER_VALUE) {
    normalized.source_hierarchy_step_template_id = filter.source_hierarchy_step_template_id;
    if (filter.source_hierarchy_step_template_id) {
      normalized.source_hierarchy_step_template_name =
        sourceTemplateNameMap.get(filter.source_hierarchy_step_template_id)
        ?? filter.source_hierarchy_step_template_id;
    }
  }
  if (filter.search.trim()) {
    normalized.search = filter.search.trim();
  }
  const normalizedSort = normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
    filter.sort,
  );
  if (Object.keys(normalized).length || normalizedSort !== DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT) {
    normalized.sort = normalizedSort;
  }
  return normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueView(normalized);
}

function buildProviderProvenanceSchedulerStitchedReportGovernanceQueueViewPayload(
  filter: ProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterState,
): ProviderProvenanceSchedulerNarrativeGovernanceQueueView | null {
  return buildProviderProvenanceSchedulerNarrativeGovernanceQueueViewPayload(
    {
      queue_state: filter.queue_state,
      item_type: "stitched_report_view",
      approval_lane: filter.approval_lane,
      approval_priority: filter.approval_priority,
      policy_template_id: filter.policy_template_id,
      policy_catalog_id: filter.policy_catalog_id,
      source_hierarchy_step_template_id: ALL_FILTER_VALUE,
      search: filter.search,
      sort: filter.sort,
    },
    new Map<string, string>(),
  );
}

function buildProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkQueueViewPatch(
  draft: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraftState,
): ProviderProvenanceSchedulerNarrativeGovernanceQueueView | null {
  const patch: Record<string, unknown> = {
    item_type: "stitched_report_view",
  };
  if (draft.queue_state !== KEEP_CURRENT_BULK_GOVERNANCE_VALUE) {
    patch.queue_state = draft.queue_state === ALL_FILTER_VALUE ? "" : draft.queue_state;
  }
  if (draft.approval_lane !== KEEP_CURRENT_BULK_GOVERNANCE_VALUE) {
    patch.approval_lane = draft.approval_lane === ALL_FILTER_VALUE ? "" : draft.approval_lane;
  }
  if (draft.approval_priority !== KEEP_CURRENT_BULK_GOVERNANCE_VALUE) {
    patch.approval_priority = draft.approval_priority === ALL_FILTER_VALUE ? "" : draft.approval_priority;
  }
  if (draft.search !== KEEP_CURRENT_BULK_GOVERNANCE_VALUE) {
    patch.search = draft.search;
  }
  if (draft.sort !== KEEP_CURRENT_BULK_GOVERNANCE_VALUE) {
    patch.sort = draft.sort;
  }
  return Object.keys(patch).length > 1
    ? (patch as ProviderProvenanceSchedulerNarrativeGovernanceQueueView)
    : null;
}

function formatProviderProvenanceSchedulerNarrativeGovernanceQueueSortLabel(sort: string) {
  if (sort === "updated_desc") {
    return "updated ↓";
  }
  if (sort === "updated_asc") {
    return "updated ↑";
  }
  if (sort === "created_desc") {
    return "created ↓";
  }
  if (sort === "created_asc") {
    return "created ↑";
  }
  if (sort === "source_template_asc") {
    return "source template A-Z";
  }
  if (sort === "source_template_desc") {
    return "source template Z-A";
  }
  return "queue priority";
}

function providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
  itemTypeScope: string | null | undefined,
  itemType: "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry",
) {
  return itemTypeScope === "any" || itemTypeScope === itemType;
}

function formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
  queueView: Partial<ProviderProvenanceSchedulerNarrativeGovernanceQueueView> | null | undefined,
) {
  const normalized = normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueView(queueView);
  if (!normalized) {
    return null;
  }
  const tokens: string[] = [];
  if (normalized.queue_state) {
    tokens.push(`queue ${formatWorkflowToken(normalized.queue_state)}`);
  }
  if (normalized.item_type) {
    tokens.push(formatWorkflowToken(normalized.item_type));
  }
  if (normalized.source_hierarchy_step_template_name || normalized.source_hierarchy_step_template_id !== undefined) {
    tokens.push(
      normalized.source_hierarchy_step_template_name
      ?? (normalized.source_hierarchy_step_template_id === "" ? "no source template" : normalized.source_hierarchy_step_template_id ?? "all source templates"),
    );
  }
  if (normalized.search) {
    tokens.push(`search "${normalized.search}"`);
  }
  tokens.push(`sort ${formatProviderProvenanceSchedulerNarrativeGovernanceQueueSortLabel(normalized.sort ?? DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT)}`);
  return tokens.join(" · ");
}

function buildProviderProvenanceAnalyticsWorkspaceQuery(
  query: ProviderProvenanceAnalyticsQueryState,
  instrument: MarketDataStatus["instruments"][number] | null,
) {
  return {
    focus_scope: query.scope,
    ...(query.scope === "current_focus" && instrument
      ? {
          focus_key: buildMarketDataInstrumentFocusKey(instrument),
          symbol: resolveMarketDataSymbol(instrument.instrument_id),
          timeframe: instrument.timeframe,
        }
      : {}),
    ...(query.provider_label !== ALL_FILTER_VALUE ? { provider_label: query.provider_label } : {}),
    ...(query.vendor_field !== ALL_FILTER_VALUE ? { vendor_field: query.vendor_field } : {}),
    ...(query.market_data_provider !== ALL_FILTER_VALUE ? { market_data_provider: query.market_data_provider } : {}),
    ...(query.requested_by_tab_id !== ALL_FILTER_VALUE ? { requested_by_tab_id: query.requested_by_tab_id } : {}),
    ...(query.scheduler_alert_category !== ALL_FILTER_VALUE
      ? { scheduler_alert_category: query.scheduler_alert_category }
      : {}),
    ...(query.scheduler_alert_status !== ALL_FILTER_VALUE
      ? { scheduler_alert_status: query.scheduler_alert_status }
      : {}),
    ...(query.scheduler_alert_narrative_facet !== "all_occurrences"
      ? { scheduler_alert_narrative_facet: query.scheduler_alert_narrative_facet }
      : {}),
    ...(query.search_query.trim() ? { search: query.search_query.trim() } : {}),
    result_limit: 12,
    window_days: query.window_days,
  };
}

function buildProviderProvenanceAnalyticsQueryStateFromWorkspaceQuery(
  query: ProviderProvenanceAnalyticsPresetEntry["query"]
    | ProviderProvenanceDashboardViewEntry["query"]
    | ProviderProvenanceSchedulerStitchedReportViewEntry["query"]
    | ProviderProvenanceSchedulerNarrativeTemplateEntry["query"]
    | ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry["query"]
    | ProviderProvenanceSchedulerNarrativeRegistryEntry["query"]
    | ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry["query"]
    | ProviderProvenanceScheduledReportEntry["query"],
): ProviderProvenanceAnalyticsQueryState {
  return {
    scope: query.focus_scope,
    provider_label: query.provider_label ?? ALL_FILTER_VALUE,
    vendor_field: query.vendor_field ?? ALL_FILTER_VALUE,
    market_data_provider: query.market_data_provider ?? ALL_FILTER_VALUE,
    requested_by_tab_id: query.requested_by_tab_id ?? ALL_FILTER_VALUE,
    scheduler_alert_category: query.scheduler_alert_category ?? ALL_FILTER_VALUE,
    scheduler_alert_status: query.scheduler_alert_status ?? ALL_FILTER_VALUE,
    scheduler_alert_narrative_facet:
      query.scheduler_alert_narrative_facet === "resolved_narratives"
      || query.scheduler_alert_narrative_facet === "post_resolution_recovery"
      || query.scheduler_alert_narrative_facet === "recurring_occurrences"
        ? query.scheduler_alert_narrative_facet
        : "all_occurrences",
    search_query: query.search ?? "",
    window_days:
      typeof query.window_days === "number" && Number.isFinite(query.window_days)
        ? Math.max(3, Math.min(Math.round(query.window_days), 90))
        : 14,
  };
}

function formatProviderProvenanceSchedulerNarrativeFacet(
  facet: ProviderProvenanceSchedulerOccurrenceNarrativeFacet | string,
) {
  if (facet === "resolved_narratives" || facet === "resolved_narrative") {
    return "resolved narratives";
  }
  if (facet === "post_resolution_recovery") {
    return "post-resolution recovery";
  }
  if (facet === "recurring_occurrences" || facet === "recurring_occurrence") {
    return "recurring occurrences";
  }
  if (facet === "current_snapshot") {
    return "current snapshot";
  }
  return "all occurrences";
}

function resolveProviderProvenanceSeriesBarWidth(value: number, maxValue: number) {
  if (maxValue <= 0 || value <= 0) {
    return "0%";
  }
  return `${Math.max((value / maxValue) * 100, 8)}%`;
}

function formatProviderDriftIntensity(value: number) {
  return `${value.toFixed(2)} incidents/export`;
}

function formatSchedulerLagSeconds(value: number) {
  if (value <= 0) {
    return "0s";
  }
  if (value < 60) {
    return `${Math.round(value)}s`;
  }
  const minutes = value / 60;
  if (minutes < 60) {
    return `${minutes.toFixed(minutes >= 10 ? 0 : 1)}m`;
  }
  const hours = minutes / 60;
  if (hours < 24) {
    return `${hours.toFixed(hours >= 10 ? 0 : 1)}h`;
  }
  const days = hours / 24;
  return `${days.toFixed(days >= 10 ? 0 : 1)}d`;
}

function downloadTextExport(payload: ProviderProvenanceSchedulerHealthExportPayload) {
  const blob = new Blob([payload.content], { type: payload.content_type });
  const objectUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = payload.filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(objectUrl);
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeMarketSymbol(value: string) {
  return value.trim().toUpperCase();
}

function buildMarketSymbolSearchVariants(symbol: string) {
  const normalized = normalizeMarketSymbol(symbol);
  return Array.from(new Set([normalized, normalized.replaceAll("/", ""), normalized.replaceAll("-", "")])).filter(
    (variant) => variant.length > 0,
  );
}

function matchesMarketSymbolInText(text: string, symbol: string) {
  const upperText = text.toUpperCase();
  return buildMarketSymbolSearchVariants(symbol).some((variant) => upperText.includes(variant));
}

function dedupeMarketDataInstruments(
  candidates: MarketDataStatus["instruments"][number][],
) {
  return Array.from(
    new Map(
      candidates.map((instrument) => [buildMarketDataInstrumentFocusKey(instrument), instrument]),
    ).values(),
  );
}

function formatMarketDataInstrumentLabel(
  instrument: MarketDataStatus["instruments"][number],
) {
  return `${resolveMarketDataSymbol(instrument.instrument_id)} · ${instrument.timeframe}`;
}

function getMarketDataInstrumentSyncSeverityRank(syncStatus: string) {
  switch (syncStatus) {
    case "error":
      return 4;
    case "stale":
      return 3;
    case "lagging":
      return 2;
    case "syncing":
      return 1;
    case "synced":
      return 0;
    default:
      return syncStatus !== "synced" ? 1 : 0;
  }
}

function getMarketDataInstrumentRiskScore(
  instrument: MarketDataStatus["instruments"][number],
) {
  return (
    getMarketDataInstrumentSyncSeverityRank(instrument.sync_status) * 1000
    + Math.min(instrument.failure_count_24h, 99) * 100
    + instrument.backfill_gap_windows.length * 40
    + instrument.issues.length * 35
    + ((instrument.backfill_contiguous_missing_candles ?? 0) > 0 ? 20 : 0)
    + (instrument.backfill_target_candles !== null && instrument.backfill_complete === false ? 10 : 0)
    + Math.min(Math.ceil((instrument.lag_seconds ?? 0) / 60), 15)
  );
}

function buildLiveMarketDataPreference(args: {
  guardedLive: GuardedLiveStatus | null;
  liveRuns: Run[];
}) {
  const { guardedLive, liveRuns } = args;
  const exactKeys = new Set<string>();
  const symbolSet = new Set<string>();
  const register = (symbol?: string | null, timeframe?: string | null) => {
    if (!symbol) {
      return;
    }
    const normalizedSymbol = normalizeMarketSymbol(symbol);
    symbolSet.add(normalizedSymbol);
    if (timeframe) {
      exactKeys.add(`${normalizedSymbol}|${timeframe}`);
    }
  };

  liveRuns.forEach((run) => {
    run.config.symbols.forEach((symbol) => {
      register(symbol, run.config.timeframe);
    });
  });

  register(guardedLive?.session_handoff.symbol, guardedLive?.session_handoff.kline_snapshot?.timeframe ?? null);
  register(guardedLive?.ownership.symbol);
  register(guardedLive?.order_book.symbol);
  register(guardedLive?.session_restore.symbol);

  return { exactKeys, symbolSet };
}

function getMarketDataInstrumentLiveRelevance(
  instrument: MarketDataStatus["instruments"][number],
  livePreference: ReturnType<typeof buildLiveMarketDataPreference>,
) {
  const symbol = normalizeMarketSymbol(resolveMarketDataSymbol(instrument.instrument_id));
  if (livePreference.exactKeys.has(`${symbol}|${instrument.timeframe}`)) {
    return 2;
  }
  if (livePreference.symbolSet.has(symbol)) {
    return 1;
  }
  return 0;
}

function selectPrimaryMarketDataInstrument(args: {
  candidates: MarketDataStatus["instruments"][number][],
  guardedLive: GuardedLiveStatus | null;
  liveRuns: Run[];
  symbolOrder?: string[];
}) {
  const { candidates, guardedLive, liveRuns, symbolOrder = [] } = args;
  const deduped = dedupeMarketDataInstruments(candidates);
  if (!deduped.length) {
    return null;
  }

  const livePreference = buildLiveMarketDataPreference({ guardedLive, liveRuns });
  const symbolOrderBySymbol = new Map<string, number>();
  symbolOrder.forEach((symbol, index) => {
    const normalizedSymbol = normalizeMarketSymbol(symbol);
    if (!symbolOrderBySymbol.has(normalizedSymbol)) {
      symbolOrderBySymbol.set(normalizedSymbol, index);
    }
  });

  const rankedCandidates = deduped
    .map((instrument) => {
      const normalizedSymbol = normalizeMarketSymbol(resolveMarketDataSymbol(instrument.instrument_id));
      return {
        instrument,
        label: formatMarketDataInstrumentLabel(instrument),
        riskScore: getMarketDataInstrumentRiskScore(instrument),
        liveRelevance: getMarketDataInstrumentLiveRelevance(instrument, livePreference),
        payloadOrder: symbolOrderBySymbol.get(normalizedSymbol) ?? Number.MAX_SAFE_INTEGER,
        lexicalKey: `${normalizedSymbol}|${instrument.timeframe}|${instrument.instrument_id}`,
      };
    })
    .sort(
      (left, right) =>
        right.riskScore - left.riskScore
        || right.liveRelevance - left.liveRelevance
        || left.payloadOrder - right.payloadOrder
        || left.lexicalKey.localeCompare(right.lexicalKey),
    );

  const primary = rankedCandidates[0];
  const nextCandidate = rankedCandidates[1] ?? null;
  let primaryFocusReason = "Only one matching market-data instrument was linked.";
  if (nextCandidate) {
    if (primary.riskScore !== nextCandidate.riskScore) {
      primaryFocusReason = `Selected the highest-risk market-data candidate from ${rankedCandidates.length} linked instruments.`;
    } else if (primary.liveRelevance !== nextCandidate.liveRelevance) {
      primaryFocusReason =
        primary.liveRelevance === 2
          ? "Risk tied, so the exact live symbol/timeframe candidate became the primary triage focus."
          : "Risk tied, so the active live symbol candidate became the primary triage focus.";
    } else if (
      primary.payloadOrder !== nextCandidate.payloadOrder
      && primary.payloadOrder !== Number.MAX_SAFE_INTEGER
    ) {
      primaryFocusReason = "Risk and live relevance tied, so payload symbol order broke the tie.";
    } else {
      primaryFocusReason = "Risk, live relevance, and payload order tied, so lexical ordering kept focus stable.";
    }
  }

  return {
    instrument: primary.instrument,
    candidateCount: rankedCandidates.length,
    candidateLabels: rankedCandidates.map((candidate) => candidate.label),
    primaryFocusPolicy: "risk -> live -> payload order -> lexical",
    primaryFocusReason,
  } satisfies MarketDataPrimaryFocusSelection;
}

function extractMatchingMarketTimeframe(
  text: string,
  marketStatus: MarketDataStatus,
) {
  const knownTimeframes = Array.from(
    new Set(marketStatus.instruments.map((instrument) => instrument.timeframe)),
  ).sort((left, right) => right.length - left.length);
  return (
    knownTimeframes.find((timeframe) =>
      new RegExp(`(^|[^A-Za-z0-9])${escapeRegExp(timeframe)}($|[^A-Za-z0-9])`, "i").test(text),
    )
    ?? null
  );
}

function extractMatchingMarketSymbols(
  text: string,
  marketStatus: MarketDataStatus,
) {
  const knownSymbols = Array.from(
    new Set(marketStatus.instruments.map((instrument) => resolveMarketDataSymbol(instrument.instrument_id))),
  );
  return knownSymbols.filter((symbol) => matchesMarketSymbolInText(text, symbol));
}

function buildLinkedMarketInstrumentContext(
  selection: MarketDataPrimaryFocusSelection,
  matchReason: string,
): LinkedMarketInstrumentContext {
  const { instrument } = selection;
  return {
    instrument,
    focusKey: buildMarketDataInstrumentFocusKey(instrument),
    symbol: resolveMarketDataSymbol(instrument.instrument_id),
    timeframe: instrument.timeframe,
    matchReason,
    candidateCount: selection.candidateCount,
    candidateLabels: selection.candidateLabels,
    primaryFocusPolicy: selection.primaryFocusPolicy,
    primaryFocusReason: selection.primaryFocusReason,
  };
}

function buildLinkedMarketInstrumentContextFromPayload(args: {
  instrument: MarketDataStatus["instruments"][number];
  primaryFocus: OperatorAlertPrimaryFocus;
  matchReason: string;
}): LinkedMarketInstrumentContext {
  const { instrument, primaryFocus, matchReason } = args;
  const candidateSymbols = Array.from(
    new Set(
      primaryFocus.candidate_symbols
        .map((symbol) => normalizeMarketSymbol(symbol))
        .filter((symbol) => symbol.length > 0),
    ),
  );
  const candidateTimeframe = primaryFocus.timeframe?.trim() || instrument.timeframe;
  return {
    instrument,
    focusKey: buildMarketDataInstrumentFocusKey(instrument),
    symbol: resolveMarketDataSymbol(instrument.instrument_id),
    timeframe: instrument.timeframe,
    matchReason,
    candidateCount: primaryFocus.candidate_count || candidateSymbols.length || 1,
    candidateLabels: (candidateSymbols.length ? candidateSymbols : [resolveMarketDataSymbol(instrument.instrument_id)])
      .map((symbol) => `${symbol} · ${candidateTimeframe}`),
    primaryFocusPolicy: primaryFocus.policy || "payload_primary_focus",
    primaryFocusReason: primaryFocus.reason?.trim() || "Backend supplied explicit primary-focus metadata.",
  };
}

function formatLinkedMarketPrimaryFocusNote(
  link: LinkedMarketInstrumentContext | null,
) {
  if (!link || link.candidateCount <= 1) {
    return null;
  }
  return `Primary focus policy (${link.primaryFocusPolicy}): ${link.primaryFocusReason} Candidate order: ${link.candidateLabels.join(", ")}.`;
}

function resolveInstrumentsBySymbolsAndTimeframe(args: {
  marketStatus: MarketDataStatus;
  symbols: string[];
  timeframe?: string | null;
}) {
  const { marketStatus, symbols, timeframe } = args;
  const symbolSet = new Set(symbols.map((symbol) => normalizeMarketSymbol(symbol)));
  return marketStatus.instruments.filter((instrument) => {
    if (!symbolSet.has(normalizeMarketSymbol(resolveMarketDataSymbol(instrument.instrument_id)))) {
      return false;
    }
    return timeframe ? instrument.timeframe === timeframe : true;
  });
}

function resolveMarketDataInstrumentLink(args: {
  guardedLive: GuardedLiveStatus | null;
  liveRuns: Run[];
  marketStatus: MarketDataStatus | null;
  record: MarketDataLinkableAlertRecord;
  runById: Map<string, Run>;
}) {
  const { guardedLive, liveRuns, marketStatus, record, runById } = args;
  if (!marketStatus) {
    return null;
  }

  const category = record.category?.trim() ?? "";
  const payloadPrimaryFocus = record.primary_focus ?? null;
  const payloadPrimaryFocusSymbol = payloadPrimaryFocus?.symbol?.trim() || null;
  const payloadPrimaryFocusTimeframe = payloadPrimaryFocus?.timeframe?.trim() || null;
  if (payloadPrimaryFocus && payloadPrimaryFocusSymbol) {
    const primaryFocusInstrument = resolveInstrumentsBySymbolsAndTimeframe({
      marketStatus,
      symbols: [payloadPrimaryFocusSymbol],
      timeframe: payloadPrimaryFocusTimeframe,
    })[0];
    if (primaryFocusInstrument) {
      return buildLinkedMarketInstrumentContextFromPayload({
        instrument: primaryFocusInstrument,
        primaryFocus: payloadPrimaryFocus,
        matchReason: "payload_primary_focus",
      });
    }
  }
  const explicitSymbols = Array.from(
    new Set(
      [record.symbol ?? null, ...(record.symbols ?? [])]
        .filter((symbol): symbol is string => typeof symbol === "string" && symbol.trim().length > 0)
        .map((symbol) => normalizeMarketSymbol(symbol)),
    ),
  );
  const explicitTimeframe = record.timeframe?.trim() || null;
  if (explicitSymbols.length) {
    const explicitSelection = selectPrimaryMarketDataInstrument({
      candidates: resolveInstrumentsBySymbolsAndTimeframe({
        marketStatus,
        symbols: explicitSymbols,
        timeframe: explicitTimeframe,
      }),
      guardedLive,
      liveRuns,
      symbolOrder: explicitSymbols,
    });
    if (explicitSelection) {
      return buildLinkedMarketInstrumentContext(explicitSelection, "payload_market_context");
    }
  }
  const run = record.run_id ? runById.get(record.run_id) : undefined;
  if (run) {
    const runSelection = selectPrimaryMarketDataInstrument({
      candidates: resolveInstrumentsBySymbolsAndTimeframe({
        marketStatus,
        symbols: run.config.symbols,
        timeframe: run.config.timeframe,
      }),
      guardedLive,
      liveRuns,
      symbolOrder: run.config.symbols,
    });
    if (runSelection) {
      return buildLinkedMarketInstrumentContext(runSelection, "run_context");
    }
  }

  if (record.provider_recovery_symbols?.length) {
    const providerRecoverySelection = selectPrimaryMarketDataInstrument({
      candidates: resolveInstrumentsBySymbolsAndTimeframe({
        marketStatus,
        symbols: record.provider_recovery_symbols,
        timeframe: record.provider_recovery_timeframe,
      }),
      guardedLive,
      liveRuns,
      symbolOrder: record.provider_recovery_symbols,
    });
    if (providerRecoverySelection) {
      return buildLinkedMarketInstrumentContext(providerRecoverySelection, "provider_recovery");
    }
  }

  const combinedText = `${record.summary} ${record.detail}`.trim();
  const matchedSymbols = extractMatchingMarketSymbols(combinedText, marketStatus);
  const guardedLiveTimeframe = guardedLive?.session_handoff.kline_snapshot?.timeframe ?? null;
  const guardedLiveSymbol =
    guardedLive?.session_handoff.symbol
    ?? guardedLive?.ownership.symbol
    ?? guardedLive?.order_book.symbol
    ?? guardedLive?.session_restore.symbol
    ?? null;
  const matchedTimeframe =
    explicitTimeframe
    ?? extractMatchingMarketTimeframe(combinedText, marketStatus)
    ?? guardedLiveTimeframe;

  if (matchedSymbols.length && matchedTimeframe) {
    const exactSelection = selectPrimaryMarketDataInstrument({
      candidates: resolveInstrumentsBySymbolsAndTimeframe({
        marketStatus,
        symbols: matchedSymbols,
        timeframe: matchedTimeframe,
      }),
      guardedLive,
      liveRuns,
      symbolOrder: matchedSymbols,
    });
    if (exactSelection) {
      return buildLinkedMarketInstrumentContext(exactSelection, "symbol_timeframe_match");
    }
  }

  if (record.source === "guarded_live" && guardedLiveSymbol && matchedTimeframe) {
    const guardedLiveSelection = selectPrimaryMarketDataInstrument({
      candidates: resolveInstrumentsBySymbolsAndTimeframe({
        marketStatus,
        symbols: [guardedLiveSymbol],
        timeframe: matchedTimeframe,
      }),
      guardedLive,
      liveRuns,
      symbolOrder: [guardedLiveSymbol],
    });
    if (guardedLiveSelection) {
      return buildLinkedMarketInstrumentContext(guardedLiveSelection, "guarded_live_context");
    }
  }

  if (matchedSymbols.length) {
    const symbolSelection = selectPrimaryMarketDataInstrument({
      candidates: resolveInstrumentsBySymbolsAndTimeframe({
        marketStatus,
        symbols: matchedSymbols,
      }),
      guardedLive,
      liveRuns,
      symbolOrder: matchedSymbols,
    });
    if (symbolSelection) {
      return buildLinkedMarketInstrumentContext(symbolSelection, "symbol_match");
    }
  }

  const isMarketDataRecord =
    category.startsWith("market_data_")
    || combinedText.toLowerCase().includes("market-data");
  if (isMarketDataRecord && matchedTimeframe) {
    const liveSymbolSet = new Set(
      liveRuns.flatMap((liveRun) => liveRun.config.symbols.map((symbol) => normalizeMarketSymbol(symbol))),
    );
    let timeframeCandidates = marketStatus.instruments.filter(
      (instrument) => instrument.timeframe === matchedTimeframe,
    );
    if (liveSymbolSet.size > 0) {
      const liveScopedCandidates = timeframeCandidates.filter((instrument) =>
        liveSymbolSet.has(normalizeMarketSymbol(resolveMarketDataSymbol(instrument.instrument_id))),
      );
      if (liveScopedCandidates.length) {
        timeframeCandidates = liveScopedCandidates;
      }
    }
    const timeframeSelection = selectPrimaryMarketDataInstrument({
      candidates: timeframeCandidates,
      guardedLive,
      liveRuns,
      symbolOrder: liveRuns.flatMap((liveRun) => liveRun.config.symbols),
    });
    if (timeframeSelection) {
      return buildLinkedMarketInstrumentContext(timeframeSelection, "timeframe_market_data_match");
    }
  }

  if (record.source === "guarded_live" && guardedLiveSymbol) {
    const guardedLiveSelection = selectPrimaryMarketDataInstrument({
      candidates: resolveInstrumentsBySymbolsAndTimeframe({
        marketStatus,
        symbols: [guardedLiveSymbol],
        timeframe: guardedLiveTimeframe,
      }),
      guardedLive,
      liveRuns,
      symbolOrder: [guardedLiveSymbol],
    });
    if (guardedLiveSelection) {
      return buildLinkedMarketInstrumentContext(guardedLiveSelection, "guarded_live_symbol");
    }
  }

  return null;
}

function getAlertLinkPriority(alert: Pick<OperatorVisibility["alerts"][number], "category" | "severity" | "detected_at">) {
  const categoryRank = alert.category.startsWith("market_data_") ? 2 : alert.category === "worker_failure" ? 1 : 0;
  const severityRank = alert.severity === "critical" ? 2 : alert.severity === "warning" ? 1 : 0;
  const detectedAt = Date.parse(alert.detected_at);
  return {
    categoryRank,
    severityRank,
    detectedAt: Number.isFinite(detectedAt) ? detectedAt : Number.NEGATIVE_INFINITY,
  };
}

function compareAlertLinkPriority(
  left: Pick<OperatorVisibility["alerts"][number], "category" | "severity" | "detected_at">,
  right: Pick<OperatorVisibility["alerts"][number], "category" | "severity" | "detected_at">,
) {
  const leftPriority = getAlertLinkPriority(left);
  const rightPriority = getAlertLinkPriority(right);
  return (
    rightPriority.categoryRank - leftPriority.categoryRank
    || rightPriority.severityRank - leftPriority.severityRank
    || rightPriority.detectedAt - leftPriority.detectedAt
  );
}

function resolveAutoLinkedMarketInstrument(args: {
  guardedLive: GuardedLiveStatus | null;
  liveRuns: Run[];
  marketStatus: MarketDataStatus | null;
  operatorVisibility: OperatorVisibility | null;
  runById: Map<string, Run>;
}) {
  const { guardedLive, liveRuns, marketStatus, operatorVisibility, runById } = args;
  if (!marketStatus || !operatorVisibility) {
    return null;
  }
  const linkedAlerts = operatorVisibility.alerts
    .map((alert) => ({
      alert,
      link: resolveMarketDataInstrumentLink({
        guardedLive,
        liveRuns,
        marketStatus,
        record: alert,
        runById,
      }),
    }))
    .filter(
      (entry): entry is {
        alert: OperatorVisibility["alerts"][number];
        link: LinkedMarketInstrumentContext;
      } => entry.link !== null,
    )
    .sort((left, right) => compareAlertLinkPriority(left.alert, right.alert));
  return linkedAlerts[0]?.link ?? null;
}


function formatParameterMap(values: Record<string, unknown>) {
  const entries = Object.entries(values);
  if (!entries.length) {
    return "none";
  }
  return entries
    .map(([name, value]) => `${name}=${formatParameterValue(value)}`)
    .join(", ");
}

function formatParameterValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.map((item) => formatParameterValue(item)).join("|");
  }
  if (value && typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export {
  defaultRunForm,
  defaultPresetForm,
  defaultPresetRevisionFilter,
  defaultMarketDataProvenanceExportFilterState,
  defaultProviderProvenanceAnalyticsQueryState,
  defaultProviderProvenanceSchedulerSearchDashboardFilterState,
  defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft,
  defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter,
  defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState,
  defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft,
  defaultProviderProvenanceSchedulerSearchModerationQueueFilterState,
  defaultProviderProvenanceSchedulerSearchModerationStageDraft,
  normalizeProviderProvenanceSchedulerRoutingPolicyDraftValue,
  normalizeProviderProvenanceSchedulerApprovalPolicyDraftValue,
  buildProviderProvenanceSchedulerExportPolicyDraft,
  getProviderProvenanceSchedulerNarrativeGovernanceQueuePriorityRank,
  getProviderProvenanceSchedulerNarrativeGovernanceQueueState,
  formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary,
  formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary,
  formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition,
  isProviderProvenanceSchedulerAlertCategory,
  getOperatorAlertOccurrenceKey,
  formatProviderProvenanceSchedulerTimelineSummary,
  formatProviderProvenanceSchedulerSearchMatchSummary,
  formatProviderProvenanceSchedulerRetrievalClusterSummary,
  buildProviderProvenanceSchedulerAlertWorkflowReason,
  defaultProviderProvenanceDashboardLayout,
  DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT,
  defaultProviderProvenanceWorkspaceDraft,
  defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft,
  defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft,
  KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
  CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE,
  defaultProviderProvenanceSchedulerNarrativeTemplateBulkDraft,
  defaultProviderProvenanceSchedulerStitchedReportViewBulkDraft,
  defaultProviderProvenanceSchedulerNarrativeRegistryDraft,
  defaultProviderProvenanceSchedulerNarrativeRegistryBulkDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft,
  defaultProviderProvenanceSchedulerNarrativeGovernanceQueueFilter,
  defaultProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter,
  defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter,
  defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter,
  defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter,
  defaultProviderProvenanceSchedulerStitchedReportViewAuditFilter,
  defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter,
  defaultProviderProvenanceReportDraft,
  buildPresetFormFromPreset,
  buildCurrentPresetRevisionSnapshot,
  buildEmptyPresetRevisionSnapshot,
  formatPresetStructuredDiffDisplayValue,
  isPresetStructuredDiffObject,
  isPresetStructuredDiffScalar,
  arePresetStructuredDiffValuesEquivalent,
  matchesPresetParameterSchemaType,
  joinPresetStructuredDiffHints,
  tokenizePresetParameterPath,
  parsePresetTimeframeToMinutes,
  buildPresetRankedStringDelta,
  buildPresetParameterStrategyContext,
  buildPresetParameterDomainContext,
  formatPresetParameterSchemaHint,
  getPresetParameterSchemaEntry,
  buildPresetStructuredDiffDelta,
  summarizePresetStructuredDiffGroup,
  groupPresetStructuredDiffRows,
  buildPresetStructuredDiffRows,
  describePresetRevisionDiff,
  describePresetDraftConflict,
  matchesPresetRevisionFilter,
  defaultRunHistoryFilter,
  sanitizeRunHistoryFilter,
  cloneRunHistoryFilter,
  hasRunHistoryFilterCriteria,
  areRunHistoryFiltersEquivalent,
  buildRunHistorySavedFilterStorageKey,
  normalizeSavedRunHistoryFilterPreset,
  loadSavedRunHistoryFilterPresets,
  persistSavedRunHistoryFilterPresets,
  describeRunHistoryFilter,
  DEFAULT_COMPARISON_INTENT,
  comparisonIntentOptions,
  parseExperimentTags,
  parseJsonObjectInput,
  formatPresetLifecycleStage,
  buildRunSubmissionPayload,
  normalizeRunFormPreset,
  resolveMarketDataSymbol,
  buildMarketDataInstrumentFocusKey,
  isMarketDataInstrumentAtRisk,
  resolvePreferredMarketDataInstrument,
  formatWorkflowToken,
  formatMarketContextFieldProvenance,
  summarizeProviderRecoveryMarketContextProvenance,
  serializeLinkedMarketInstrumentContext,
  getOperatorSeverityRank,
  normalizeMarketDataProvenanceExportSort,
  normalizeMarketDataProvenanceExportFilterState,
  normalizeMarketDataProvenanceExportHistoryEntry,
  loadPersistedMarketDataProvenanceExportState,
  persistMarketDataProvenanceExportState,
  formatMarketDataProvenanceExportFilterSummary,
  formatProviderProvenanceAnalyticsQuerySummary,
  normalizeProviderProvenanceDashboardLayoutState,
  normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort,
  normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueView,
  buildProviderProvenanceSchedulerNarrativeGovernanceQueueFilterStateFromView,
  buildProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterStateFromView,
  buildProviderProvenanceSchedulerNarrativeGovernanceQueueViewPayload,
  buildProviderProvenanceSchedulerStitchedReportGovernanceQueueViewPayload,
  buildProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkQueueViewPatch,
  formatProviderProvenanceSchedulerNarrativeGovernanceQueueSortLabel,
  providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType,
  formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary,
  buildProviderProvenanceAnalyticsWorkspaceQuery,
  buildProviderProvenanceAnalyticsQueryStateFromWorkspaceQuery,
  formatProviderProvenanceSchedulerNarrativeFacet,
  resolveProviderProvenanceSeriesBarWidth,
  formatProviderDriftIntensity,
  formatSchedulerLagSeconds,
  downloadTextExport,
  escapeRegExp,
  normalizeMarketSymbol,
  buildMarketSymbolSearchVariants,
  matchesMarketSymbolInText,
  dedupeMarketDataInstruments,
  formatMarketDataInstrumentLabel,
  getMarketDataInstrumentSyncSeverityRank,
  getMarketDataInstrumentRiskScore,
  buildLiveMarketDataPreference,
  getMarketDataInstrumentLiveRelevance,
  selectPrimaryMarketDataInstrument,
  extractMatchingMarketTimeframe,
  extractMatchingMarketSymbols,
  buildLinkedMarketInstrumentContext,
  buildLinkedMarketInstrumentContextFromPayload,
  formatLinkedMarketPrimaryFocusNote,
  resolveInstrumentsBySymbolsAndTimeframe,
  resolveMarketDataInstrumentLink,
  getAlertLinkPriority,
  compareAlertLinkPriority,
  resolveAutoLinkedMarketInstrument,
  formatParameterMap,
  formatParameterValue
};
export type {
  ProviderProvenanceAnalyticsScope,
  ProviderProvenanceSchedulerOccurrenceNarrativeFacet,
  ProviderProvenanceAnalyticsQueryState,
  ProviderProvenanceSchedulerSearchDashboardFilterState,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilterState,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilterState,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft,
  ProviderProvenanceSchedulerSearchModerationQueueFilterState,
  ProviderProvenanceSchedulerSearchModerationStageDraft,
  ProviderProvenanceSchedulerExportPolicyDraft,
  OperatorVisibilityAlertEntry,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraftState,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraftState,
  ProviderProvenanceSchedulerNarrativeBulkToggleValue,
  ProviderProvenanceSchedulerNarrativeTemplateBulkDraftState,
  ProviderProvenanceSchedulerStitchedReportViewBulkDraftState,
  ProviderProvenanceSchedulerNarrativeRegistryDraftState,
  ProviderProvenanceSchedulerNarrativeRegistryBulkDraftState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraftState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraftState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraftState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraftState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraftState,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraftState,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraftState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersionEntry,
  ProviderProvenanceSchedulerNarrativeGovernanceQueueFilterState,
  ProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilterState,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilterState,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilterState,
  ProviderProvenanceSchedulerStitchedReportViewAuditFilterState,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilterState,
  ProviderProvenanceReportDraftState,
  LinkedMarketInstrumentContext,
  MarketDataLinkableAlertRecord,
  MarketDataIncidentHistoryEntry,
  ProviderRecoveryMarketContextSummary,
  MarketDataProviderProvenanceEventRecord,
  MarketDataPrimaryFocusSelection
};
