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


import {
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
  resolveAutoLinkedMarketInstrument
} from "./ControlRoomCoreHelpers";
import {
  formatTimestamp,
  formatProviderRecoverySchema,
  formatProviderRecoveryTelemetry,
  shortenIdentifier,
  truncateLabel,
  formatRange,
  benchmarkArtifactSummaryOrder,
  benchmarkArtifactSummaryLabels,
  benchmarkArtifactSectionOrder,
  benchmarkArtifactSectionLabels,
  formatBenchmarkArtifactSummaryEntries,
  benchmarkArtifactSummarySortIndex,
  formatBenchmarkArtifactSummaryLabel,
  formatBenchmarkArtifactSummaryValue,
  formatBenchmarkArtifactSectionEntries,
  benchmarkArtifactSectionSortIndex,
  formatBenchmarkArtifactSectionLabel,
  formatBenchmarkArtifactSectionLines,
  formatBenchmarkArtifactSectionValue,
  formatBenchmarkArtifactInlineValue
} from "./ControlRoomFormattingHelpers";
import type {
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
} from "./ControlRoomCoreHelpers";

function PanelDisclosure({
  children,
  defaultOpen = false,
  summary,
  title,
}: {
  children: ReactNode;
  defaultOpen?: boolean;
  summary?: string;
  title: string;
}) {
  const bodyId = useId();
  const [open, setOpen] = useState(defaultOpen);

  return (
    <details
      className={`panel-disclosure ${open ? "is-open" : ""}`.trim()}
      onToggle={(event) => setOpen(event.currentTarget.open)}
      open={open}
    >
      <summary aria-controls={bodyId} className="panel-disclosure-summary">
        <div className="panel-disclosure-summary-copy">
          <strong>{title}</strong>
          {summary ? <p>{summary}</p> : null}
        </div>
        <span className="panel-disclosure-state">{open ? "Collapse" : "Expand"}</span>
      </summary>
      <div className="panel-disclosure-body" id={bodyId}>
        {children}
      </div>
    </details>
  );
}

function BackfillCountStatus({
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  if (instrument.backfill_target_candles === null) {
    return <span>n/a</span>;
  }
  return (
    <div className="progress-stack">
      <strong>{formatCompletion(instrument.backfill_completion_ratio)}</strong>
      <span>
        {Math.min(instrument.candle_count, instrument.backfill_target_candles)} /{" "}
        {instrument.backfill_target_candles}
        {instrument.backfill_complete ? " ready" : ""}
      </span>
      <div className="progress-track" aria-hidden="true">
        <span
          style={{
            width: `${Math.round((instrument.backfill_completion_ratio ?? 0) * 100)}%`,
          }}
        />
      </div>
    </div>
  );
}

function BackfillQualityStatus({
  expanded,
  gapWindowPickerOpen,
  instrument,
  onChangeGapWindowSelections,
  onToggle,
  onSelectAllGapWindows,
  onToggleGapWindowPicker,
  selectedGapWindowKeys,
}: {
  expanded: boolean;
  gapWindowPickerOpen: boolean;
  instrument: MarketDataStatus["instruments"][number];
  onChangeGapWindowSelections?: (gapWindowKeys: string[]) => void;
  onToggle: () => void;
  onSelectAllGapWindows?: () => void;
  onToggleGapWindowPicker?: () => void;
  selectedGapWindowKeys?: string[] | null;
}) {
  const [rangeAnchorGapWindowKey, setRangeAnchorGapWindowKey] = useState<string | null>(null);
  const [dragSelectionState, setDragSelectionState] = useState<GapWindowDragSelectionState | null>(null);
  const [touchSweepHoldProgressState, setTouchSweepHoldProgressState] =
    useState<TouchGapWindowHoldProgressState | null>(null);
  const [touchSweepActivationFeedbackState, setTouchSweepActivationFeedbackState] =
    useState<TouchGapWindowActivationFeedbackState | null>(null);
  const gapWindowPickerListRef = useRef<HTMLDivElement | null>(null);
  const pendingTouchSweepStateRef = useRef<PendingTouchGapWindowSweepState | null>(null);
  const touchSweepHoldTimeoutRef = useRef<number | null>(null);
  const touchSweepActivationFeedbackTimeoutRef = useRef<number | null>(null);
  const touchSweepActivationFeedbackIdRef = useRef(0);
  const orderedGapWindowKeys = instrument.backfill_gap_windows.map((gapWindow) =>
    buildGapWindowKey(gapWindow),
  );
  const clearTouchSweepHoldTimeout = () => {
    if (touchSweepHoldTimeoutRef.current !== null) {
      window.clearTimeout(touchSweepHoldTimeoutRef.current);
      touchSweepHoldTimeoutRef.current = null;
    }
  };
  const clearTouchSweepActivationFeedbackTimeout = () => {
    if (touchSweepActivationFeedbackTimeoutRef.current !== null) {
      window.clearTimeout(touchSweepActivationFeedbackTimeoutRef.current);
      touchSweepActivationFeedbackTimeoutRef.current = null;
    }
  };
  useEffect(() => {
    if (!rangeAnchorGapWindowKey) {
      return;
    }
    if (!orderedGapWindowKeys.includes(rangeAnchorGapWindowKey)) {
      setRangeAnchorGapWindowKey(null);
    }
  }, [orderedGapWindowKeys, rangeAnchorGapWindowKey]);
  useEffect(() => {
    if (
      touchSweepHoldProgressState
      && !orderedGapWindowKeys.includes(touchSweepHoldProgressState.anchorGapWindowKey)
    ) {
      setTouchSweepHoldProgressState(null);
    }
  }, [orderedGapWindowKeys, touchSweepHoldProgressState]);
  useEffect(() => {
    if (!dragSelectionState) {
      return;
    }
    if (
      !orderedGapWindowKeys.includes(dragSelectionState.anchorGapWindowKey)
      || !orderedGapWindowKeys.includes(dragSelectionState.latestGapWindowKey)
    ) {
      setDragSelectionState(null);
    }
  }, [dragSelectionState, orderedGapWindowKeys]);
  useEffect(() => {
    if (!gapWindowPickerOpen && dragSelectionState) {
      setDragSelectionState(null);
    }
  }, [dragSelectionState, gapWindowPickerOpen]);
  useEffect(() => {
    if (gapWindowPickerOpen) {
      return;
    }
    clearTouchSweepHoldTimeout();
    pendingTouchSweepStateRef.current = null;
    setTouchSweepHoldProgressState(null);
    clearTouchSweepActivationFeedbackTimeout();
    setTouchSweepActivationFeedbackState(null);
  }, [gapWindowPickerOpen]);
  useEffect(() => {
    if (!dragSelectionState) {
      return;
    }
    const finishDragSelection = () => {
      setRangeAnchorGapWindowKey(dragSelectionState.latestGapWindowKey);
      setDragSelectionState(null);
    };
    window.addEventListener("pointerup", finishDragSelection);
    window.addEventListener("pointercancel", finishDragSelection);
    return () => {
      window.removeEventListener("pointerup", finishDragSelection);
      window.removeEventListener("pointercancel", finishDragSelection);
    };
  }, [dragSelectionState]);
  useEffect(() => () => {
    clearTouchSweepHoldTimeout();
    clearTouchSweepActivationFeedbackTimeout();
  }, []);
  if (instrument.backfill_contiguous_completion_ratio === null) {
    return <span>n/a</span>;
  }
  const resolvedSelectedGapWindowKeys = resolveGapWindowSelectionList(
    orderedGapWindowKeys,
    selectedGapWindowKeys,
  );
  const visibleGapWindowKeys = new Set(resolvedSelectedGapWindowKeys);
  const hasGapWindowSubset =
    resolvedSelectedGapWindowKeys.length < instrument.backfill_gap_windows.length;
  const selectedGapWindows = resolvedSelectedGapWindowKeys.length
    ? instrument.backfill_gap_windows.filter((gap) => visibleGapWindowKeys.has(buildGapWindowKey(gap)))
    : instrument.backfill_gap_windows;
  const canToggleGapWindows = instrument.backfill_gap_windows.length > MAX_VISIBLE_GAP_WINDOWS;
  const canPickGapWindows = instrument.backfill_gap_windows.length > 1;
  const showExactGapLines =
    expanded
    || hasGapWindowSubset
    || instrument.backfill_gap_windows.length <= MAX_VISIBLE_GAP_WINDOWS;
  const gapLines = showExactGapLines
    ? formatGapWindows(selectedGapWindows)
    : summarizeGapWindows(instrument.backfill_gap_windows);
  const selectedGapWindowCount = selectedGapWindows.length;
  const selectedGapWindowMissingCandles = selectedGapWindows.reduce(
    (total, gapWindow) => total + gapWindow.missing_candles,
    0,
  );
  const rangeAnchorLabel = rangeAnchorGapWindowKey
    ? formatGapWindowKeyLabel(rangeAnchorGapWindowKey)
    : null;
  const touchSweepHoldLabel = touchSweepHoldProgressState
    ? formatGapWindowKeyLabel(touchSweepHoldProgressState.anchorGapWindowKey)
    : null;
  const touchSweepHoldProgressStyle = {
    "--gap-window-touch-hold-duration": `${TOUCH_GAP_WINDOW_SWEEP_HOLD_MS}ms`,
  } as CSSProperties;
  const triggerTouchSweepActivationFeedback = (anchorGapWindowKey: string) => {
    const touchFeedbackDetail: AkraTouchFeedbackDetail = {
      anchorGapWindowKey,
      effect: "impact",
      impactStyle: "light",
      source: "gap-window-picker-sweep-activation",
      trigger: "touch-hold",
    };
    const touchFeedbackEnvelope: AkraTouchFeedbackEnvelope = {
      detail: touchFeedbackDetail,
      type: AKRA_TOUCH_FEEDBACK_EVENT_NAME,
      version: AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION,
    };
    triggerAkraTouchFeedbackBridge(touchFeedbackEnvelope);
    const nextActivationId = touchSweepActivationFeedbackIdRef.current + 1;
    touchSweepActivationFeedbackIdRef.current = nextActivationId;
    clearTouchSweepActivationFeedbackTimeout();
    setTouchSweepActivationFeedbackState({
      activationId: nextActivationId,
      anchorGapWindowKey,
    });
    touchSweepActivationFeedbackTimeoutRef.current = window.setTimeout(() => {
      setTouchSweepActivationFeedbackState((current) =>
        current?.activationId === nextActivationId ? null : current,
      );
      touchSweepActivationFeedbackTimeoutRef.current = null;
    }, 320);
  };
  const applyGapWindowSelectionChange = ({
    anchorGapWindowKey,
    selectedGapWindowKeys,
    targetGapWindowKey,
    targetSelected,
  }: {
    anchorGapWindowKey?: string | null;
    selectedGapWindowKeys?: string[] | null;
    targetGapWindowKey: string;
    targetSelected: boolean;
  }) => {
    const nextSelectedGapWindowKeys = buildGapWindowSelectionUpdate({
      orderedGapWindowKeys,
      rangeAnchorGapWindowKey: anchorGapWindowKey,
      selectedGapWindowKeys,
      targetGapWindowKey,
      targetSelected,
    });
    onChangeGapWindowSelections?.(nextSelectedGapWindowKeys);
    return nextSelectedGapWindowKeys;
  };
  const updateActiveGapWindowSweepTarget = ({
    anchorGapWindowKey,
    baselineSelectedGapWindowKeys,
    latestGapWindowKey,
    pointerId,
    targetSelected,
  }: GapWindowDragSelectionState) => {
    applyGapWindowSelectionChange({
      anchorGapWindowKey,
      selectedGapWindowKeys: baselineSelectedGapWindowKeys,
      targetGapWindowKey: latestGapWindowKey,
      targetSelected,
    });
    setDragSelectionState({
      anchorGapWindowKey,
      baselineSelectedGapWindowKeys,
      latestGapWindowKey,
      pointerId,
      targetSelected,
    });
  };
  const resolveGapWindowKeyFromPointerPoint = (clientX: number, clientY: number) => {
    const pointerTarget = document.elementFromPoint(clientX, clientY);
    if (!(pointerTarget instanceof HTMLElement)) {
      return null;
    }
    const option = pointerTarget.closest<HTMLElement>("[data-gap-window-key]");
    if (!option || !gapWindowPickerListRef.current?.contains(option)) {
      return null;
    }
    return option.dataset.gapWindowKey ?? null;
  };
  const handleGapWindowPointerDown = (
    event: PointerEvent<HTMLLabelElement>,
    gapWindowKey: string,
    checked: boolean,
  ) => {
    if (event.button !== 0) {
      return;
    }
    if (event.pointerType === "touch") {
      clearTouchSweepHoldTimeout();
      pendingTouchSweepStateRef.current = {
        anchorGapWindowKey: gapWindowKey,
        baselineSelectedGapWindowKeys: resolvedSelectedGapWindowKeys,
        latestGapWindowKey: gapWindowKey,
        pointerId: event.pointerId,
        startClientX: event.clientX,
        startClientY: event.clientY,
        targetSelected: !checked,
      };
      setTouchSweepHoldProgressState({
        anchorGapWindowKey: gapWindowKey,
        targetSelected: !checked,
      });
      event.currentTarget.setPointerCapture(event.pointerId);
      touchSweepHoldTimeoutRef.current = window.setTimeout(() => {
        const pendingTouchSweepState = pendingTouchSweepStateRef.current;
        if (
          !pendingTouchSweepState
          || pendingTouchSweepState.pointerId !== event.pointerId
        ) {
          return;
        }
        setTouchSweepHoldProgressState(null);
        triggerTouchSweepActivationFeedback(pendingTouchSweepState.anchorGapWindowKey);
        setRangeAnchorGapWindowKey(pendingTouchSweepState.anchorGapWindowKey);
        updateActiveGapWindowSweepTarget({
          anchorGapWindowKey: pendingTouchSweepState.anchorGapWindowKey,
          baselineSelectedGapWindowKeys: pendingTouchSweepState.baselineSelectedGapWindowKeys,
          latestGapWindowKey: pendingTouchSweepState.anchorGapWindowKey,
          pointerId: pendingTouchSweepState.pointerId,
          targetSelected: pendingTouchSweepState.targetSelected,
        });
      }, TOUCH_GAP_WINDOW_SWEEP_HOLD_MS);
      return;
    }
    event.preventDefault();
    applyGapWindowSelectionChange({
      selectedGapWindowKeys: resolvedSelectedGapWindowKeys,
      targetGapWindowKey: gapWindowKey,
      targetSelected: !checked,
    });
    setRangeAnchorGapWindowKey(gapWindowKey);
    setDragSelectionState({
      anchorGapWindowKey: gapWindowKey,
      baselineSelectedGapWindowKeys: resolvedSelectedGapWindowKeys,
      latestGapWindowKey: gapWindowKey,
      pointerId: event.pointerId,
      targetSelected: !checked,
    });
  };
  const handleGapWindowPointerEnter = (
    event: PointerEvent<HTMLLabelElement>,
    gapWindowKey: string,
  ) => {
    if (
      !dragSelectionState
      || event.pointerId !== dragSelectionState.pointerId
      || event.buttons === 0
      || dragSelectionState.latestGapWindowKey === gapWindowKey
    ) {
      return;
    }
    updateActiveGapWindowSweepTarget({
      ...dragSelectionState,
      latestGapWindowKey: gapWindowKey,
    });
  };
  const handleTouchGapWindowPointerMove = (
    event: PointerEvent<HTMLLabelElement>,
  ) => {
    const pendingTouchSweepState = pendingTouchSweepStateRef.current;
    if (
      event.pointerType !== "touch"
      || !pendingTouchSweepState
      || pendingTouchSweepState.pointerId !== event.pointerId
    ) {
      return;
    }
    const deltaX = event.clientX - pendingTouchSweepState.startClientX;
    const deltaY = event.clientY - pendingTouchSweepState.startClientY;
    const pointerTravel = Math.hypot(deltaX, deltaY);
    if (!dragSelectionState) {
      if (pointerTravel > TOUCH_GAP_WINDOW_SWEEP_MOVE_TOLERANCE_PX) {
        clearTouchSweepHoldTimeout();
        pendingTouchSweepStateRef.current = null;
        setTouchSweepHoldProgressState(null);
        if (event.currentTarget.hasPointerCapture(event.pointerId)) {
          event.currentTarget.releasePointerCapture(event.pointerId);
        }
      }
      return;
    }
    event.preventDefault();
    const hoveredGapWindowKey =
      resolveGapWindowKeyFromPointerPoint(event.clientX, event.clientY)
      ?? pendingTouchSweepState.anchorGapWindowKey;
    if (hoveredGapWindowKey === dragSelectionState.latestGapWindowKey) {
      return;
    }
    pendingTouchSweepStateRef.current = {
      ...pendingTouchSweepState,
      latestGapWindowKey: hoveredGapWindowKey,
    };
    updateActiveGapWindowSweepTarget({
      anchorGapWindowKey: pendingTouchSweepState.anchorGapWindowKey,
      baselineSelectedGapWindowKeys: pendingTouchSweepState.baselineSelectedGapWindowKeys,
      latestGapWindowKey: hoveredGapWindowKey,
      pointerId: pendingTouchSweepState.pointerId,
      targetSelected: pendingTouchSweepState.targetSelected,
    });
  };
  const handleTouchGapWindowPointerEnd = (
    event: PointerEvent<HTMLLabelElement>,
  ) => {
    const pendingTouchSweepState = pendingTouchSweepStateRef.current;
    if (
      event.pointerType !== "touch"
      || !pendingTouchSweepState
      || pendingTouchSweepState.pointerId !== event.pointerId
    ) {
      return;
    }
    clearTouchSweepHoldTimeout();
    setTouchSweepHoldProgressState(null);
    if (!dragSelectionState) {
      applyGapWindowSelectionChange({
        selectedGapWindowKeys: pendingTouchSweepState.baselineSelectedGapWindowKeys,
        targetGapWindowKey: pendingTouchSweepState.anchorGapWindowKey,
        targetSelected: pendingTouchSweepState.targetSelected,
      });
      setRangeAnchorGapWindowKey(pendingTouchSweepState.anchorGapWindowKey);
    } else {
      setRangeAnchorGapWindowKey(dragSelectionState.latestGapWindowKey);
      setDragSelectionState(null);
    }
    pendingTouchSweepStateRef.current = null;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };
  const handleGapWindowKeyboardToggle = (
    event: KeyboardEvent<HTMLInputElement>,
    gapWindowKey: string,
    checked: boolean,
  ) => {
    if (event.key !== " " && event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    applyGapWindowSelectionChange({
      anchorGapWindowKey: event.shiftKey ? rangeAnchorGapWindowKey : null,
      selectedGapWindowKeys: resolvedSelectedGapWindowKeys,
      targetGapWindowKey: gapWindowKey,
      targetSelected: !checked,
    });
    setRangeAnchorGapWindowKey(gapWindowKey);
  };
  return (
    <div className="progress-stack">
      <strong>{formatCompletion(instrument.backfill_contiguous_completion_ratio)}</strong>
      <span>
        {instrument.backfill_contiguous_complete
          ? "gap-free"
          : `gaps: ${instrument.backfill_contiguous_missing_candles ?? 0}`}
      </span>
      {gapLines.length ? (
        <div className="progress-detail-list">
          {gapLines.map((line) => (
            <span
              className={line.kind === "summary" ? "progress-detail-summary" : undefined}
              key={line.key}
            >
              {line.label}
            </span>
          ))}
        </div>
      ) : null}
      {hasGapWindowSubset ? (
        <span>
          {`${expanded ? "Review subset" : "Focused subset"}: ${selectedGapWindowCount} / ${
            instrument.backfill_gap_windows.length
          } gaps`}
        </span>
      ) : null}
      {canToggleGapWindows || canPickGapWindows ? (
        <div className="progress-action-row">
          {canToggleGapWindows ? (
            <button
              className="progress-toggle"
              onClick={onToggle}
              type="button"
            >
              {expanded
                ? "Collapse gap detail"
                : `Expand ${instrument.backfill_gap_windows.length}-gap detail`}
            </button>
          ) : null}
          {canPickGapWindows && onToggleGapWindowPicker ? (
            <button
              className="progress-toggle"
              onClick={onToggleGapWindowPicker}
              type="button"
            >
              {gapWindowPickerOpen
                ? "Hide gap picker"
                : hasGapWindowSubset
                  ? "Refine focused gaps"
                  : "Pick visible gaps"}
            </button>
          ) : null}
          {gapWindowPickerOpen && hasGapWindowSubset && onSelectAllGapWindows ? (
            <button
              className="progress-toggle"
              onClick={onSelectAllGapWindows}
              type="button"
            >
              Show full range
            </button>
          ) : null}
        </div>
      ) : null}
      {gapWindowPickerOpen && canPickGapWindows ? (
        <div
          className={`gap-window-picker ${dragSelectionState ? "is-sweeping" : ""} ${
            touchSweepActivationFeedbackState ? "has-touch-feedback" : ""
          }`}
        >
          <div className="gap-window-picker-head">
            <span className="gap-window-picker-title">Visible gap windows</span>
            <span className="gap-window-picker-summary">
              {`${selectedGapWindowCount} / ${instrument.backfill_gap_windows.length} selected · ${selectedGapWindowMissingCandles} missing candles`}
            </span>
          </div>
          <span className="gap-window-picker-anchor">
            {dragSelectionState
              ? `Sweep ${dragSelectionState.targetSelected ? "select" : "hide"} mode from ${formatGapWindowKeyLabel(
                  dragSelectionState.anchorGapWindowKey,
                )}.`
              : touchSweepHoldLabel
                ? `Hold to ${
                    touchSweepHoldProgressState?.targetSelected ? "sweep select" : "sweep hide"
                  } from ${touchSweepHoldLabel}.`
              : rangeAnchorLabel
                ? `Range anchor: ${rangeAnchorLabel}. Shift-click another gap to apply the full range.`
                : "Tip: click a gap to set the range anchor, then shift-click or drag across gaps to apply a range."}
          </span>
          {touchSweepHoldProgressState ? (
            <div
              className="gap-window-picker-hold-progress"
              style={touchSweepHoldProgressStyle}
            >
              <span className="gap-window-picker-hold-progress-bar" />
            </div>
          ) : null}
          <div
            className="gap-window-picker-list"
            ref={gapWindowPickerListRef}
          >
            {instrument.backfill_gap_windows.map((gapWindow) => {
              const gapWindowKey = buildGapWindowKey(gapWindow);
              const checked = visibleGapWindowKeys.has(gapWindowKey);
              return (
                <label
                  className={`gap-window-picker-option ${checked ? "is-active" : ""} ${
                    rangeAnchorGapWindowKey === gapWindowKey ? "is-anchor" : ""
                  } ${
                    dragSelectionState?.latestGapWindowKey === gapWindowKey ? "is-sweep-target" : ""
                  } ${
                    touchSweepActivationFeedbackState?.anchorGapWindowKey === gapWindowKey
                      ? "has-touch-feedback"
                      : ""
                  }`}
                  data-gap-window-key={gapWindowKey}
                  key={gapWindowKey}
                  onPointerDown={(event) =>
                    handleGapWindowPointerDown(event, gapWindowKey, checked)
                  }
                  onPointerEnter={(event) =>
                    handleGapWindowPointerEnter(event, gapWindowKey)
                  }
                  onPointerMove={handleTouchGapWindowPointerMove}
                  onPointerUp={handleTouchGapWindowPointerEnd}
                  onPointerCancel={handleTouchGapWindowPointerEnd}
                >
                  <input
                    checked={checked}
                    disabled={checked && selectedGapWindowCount === 1}
                    onClick={(event) => {
                      event.preventDefault();
                    }}
                    onKeyDown={(event) =>
                      handleGapWindowKeyboardToggle(event, gapWindowKey, checked)
                    }
                    readOnly
                    type="checkbox"
                  />
                  <span className="gap-window-picker-option-copy">
                    <span className="gap-window-picker-option-label">
                      {formatGapWindowKeyLabel(gapWindowKey)}
                    </span>
                    <span className="gap-window-picker-option-meta">
                      {`${gapWindow.missing_candles} missing candles`}
                    </span>
                  </span>
                </label>
              );
            })}
          </div>
          <span className="gap-window-picker-footnote">
            Keep at least one gap window visible for review.
          </span>
        </div>
      ) : null}
      <div className="progress-track" aria-hidden="true">
        <span
          style={{
            width: `${Math.round((instrument.backfill_contiguous_completion_ratio ?? 0) * 100)}%`,
          }}
        />
      </div>
    </div>
  );
}

function SyncCheckpointStatus({
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  const checkpoint = instrument.sync_checkpoint;
  if (!checkpoint) {
    return <span>n/a</span>;
  }
  return (
    <div className="progress-stack">
      <strong title={checkpoint.checkpoint_id}>{shortenIdentifier(checkpoint.checkpoint_id)}</strong>
      <span>
        {checkpoint.candle_count} candles
        {checkpoint.contiguous_missing_candles > 0
          ? ` / gaps ${checkpoint.contiguous_missing_candles}`
          : " / gap-free"}
      </span>
      <span>{formatTimestamp(checkpoint.recorded_at)}</span>
    </div>
  );
}

function SyncFailureStatus({
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  if (instrument.failure_count_24h === 0 && instrument.recent_failures.length === 0) {
    return <span>clear</span>;
  }
  const latestFailure = instrument.recent_failures[0];
  return (
    <div className="progress-stack">
      <strong>{instrument.failure_count_24h} in 24h</strong>
      <span>
        {latestFailure
          ? `${latestFailure.operation} @ ${formatTimestamp(latestFailure.failed_at)}`
          : "history unavailable"}
      </span>
      {latestFailure ? (
        <span title={latestFailure.error}>{truncateLabel(latestFailure.error, 56)}</span>
      ) : null}
    </div>
  );
}

function formatCompletion(value: number | null) {
  if (value === null) {
    return "n/a";
  }
  return `${Math.round(value * 100)}%`;
}

function summarizeGapWindows(
  gapWindows: MarketDataStatus["instruments"][number]["backfill_gap_windows"],
) {
  if (gapWindows.length <= MAX_VISIBLE_GAP_WINDOWS) {
    return formatGapWindows(gapWindows);
  }

  const recentWindows = gapWindows.slice(-(MAX_VISIBLE_GAP_WINDOWS - 1));
  const collapsedWindows = gapWindows.slice(0, -(MAX_VISIBLE_GAP_WINDOWS - 1));
  const collapsedMissing = collapsedWindows.reduce(
    (total, gap) => total + gap.missing_candles,
    0,
  );
  const lastCollapsedWindow = collapsedWindows[collapsedWindows.length - 1];

  return [
    {
      key: `summary-${collapsedWindows[0].start_at}-${lastCollapsedWindow.end_at}`,
      kind: "summary" as const,
      label:
        `${collapsedWindows.length} older windows | ` +
        `${formatRange(collapsedWindows[0].start_at, lastCollapsedWindow.end_at)} | ` +
        `${collapsedMissing} missing`,
    },
    ...formatGapWindows(recentWindows),
  ];
}

function formatGapWindows(
  gapWindows: MarketDataStatus["instruments"][number]["backfill_gap_windows"],
) {
  return gapWindows.map((gap) => ({
    key: buildGapWindowKey(gap),
    kind: "exact" as const,
    label: `${formatRange(gap.start_at, gap.end_at)} (${gap.missing_candles})`,
  }));
}

function buildLegacyGapWindowKey(
  gapWindow: MarketDataStatus["instruments"][number]["backfill_gap_windows"][number],
) {
  return `${gapWindow.start_at}|${gapWindow.end_at}|${gapWindow.missing_candles}`;
}

function buildGapWindowKey(
  gapWindow: MarketDataStatus["instruments"][number]["backfill_gap_windows"][number],
) {
  return gapWindow.gap_window_id || buildLegacyGapWindowKey(gapWindow);
}

function parseGapWindowKey(key: string) {
  if (key.startsWith("gw|")) {
    const [, occurrenceIndexRaw, startAt, endAt, missingCandlesRaw] = key.split("|");
    const occurrenceIndex = Number(occurrenceIndexRaw);
    const missingCandles = Number(missingCandlesRaw);
    return {
      startAt: startAt || null,
      endAt: endAt || null,
      missingCandles: Number.isFinite(missingCandles) ? missingCandles : null,
      occurrenceIndex: Number.isFinite(occurrenceIndex) ? occurrenceIndex : null,
    };
  }
  const [startAt, endAt, missingCandlesRaw] = key.split("|");
  const missingCandles = Number(missingCandlesRaw);
  return {
    startAt: startAt || null,
    endAt: endAt || null,
    missingCandles: Number.isFinite(missingCandles) ? missingCandles : null,
    occurrenceIndex: null,
  };
}

function formatGapWindowKeyLabel(key: string) {
  const parsed = parseGapWindowKey(key);
  return `${formatRange(parsed.startAt, parsed.endAt)} (${parsed.missingCandles ?? "n/a"})${
    parsed.occurrenceIndex !== null ? ` · slot ${parsed.occurrenceIndex + 1}` : ""
  }`;
}

function normalizeExpandedGapWindowSelectionList(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return [...new Set(value.filter((candidate): candidate is string => typeof candidate === "string" && candidate.trim().length > 0))].sort();
}

function resolveGapWindowSelectionList(
  orderedGapWindowKeys: string[],
  selectedGapWindowKeys?: string[] | null,
) {
  if (!orderedGapWindowKeys.length) {
    return [];
  }
  const allowedGapWindowKeys = new Set(orderedGapWindowKeys);
  const normalizedGapWindowKeys = normalizeExpandedGapWindowSelectionList(
    selectedGapWindowKeys,
  ).filter((gapWindowKey) => allowedGapWindowKeys.has(gapWindowKey));
  if (!normalizedGapWindowKeys.length) {
    return orderedGapWindowKeys;
  }
  const normalizedSelection = new Set(normalizedGapWindowKeys);
  return orderedGapWindowKeys.filter((gapWindowKey) => normalizedSelection.has(gapWindowKey));
}

function buildGapWindowSelectionUpdate({
  orderedGapWindowKeys,
  rangeAnchorGapWindowKey,
  selectedGapWindowKeys,
  targetGapWindowKey,
  targetSelected,
}: {
  orderedGapWindowKeys: string[];
  rangeAnchorGapWindowKey?: string | null;
  selectedGapWindowKeys?: string[] | null;
  targetGapWindowKey: string;
  targetSelected: boolean;
}) {
  const currentSelection = resolveGapWindowSelectionList(
    orderedGapWindowKeys,
    selectedGapWindowKeys,
  );
  const targetGapWindowIndex = orderedGapWindowKeys.indexOf(targetGapWindowKey);
  if (targetGapWindowIndex < 0) {
    return currentSelection;
  }
  const anchorGapWindowIndex = rangeAnchorGapWindowKey
    ? orderedGapWindowKeys.indexOf(rangeAnchorGapWindowKey)
    : -1;
  const rangeGapWindowKeys =
    anchorGapWindowIndex >= 0 && anchorGapWindowIndex !== targetGapWindowIndex
      ? orderedGapWindowKeys.slice(
          Math.min(anchorGapWindowIndex, targetGapWindowIndex),
          Math.max(anchorGapWindowIndex, targetGapWindowIndex) + 1,
        )
      : [targetGapWindowKey];
  const nextSelection = new Set(currentSelection);
  if (targetSelected) {
    rangeGapWindowKeys.forEach((gapWindowKey) => nextSelection.add(gapWindowKey));
  } else {
    rangeGapWindowKeys.forEach((gapWindowKey) => nextSelection.delete(gapWindowKey));
    if (!nextSelection.size) {
      return currentSelection;
    }
  }
  return orderedGapWindowKeys.filter((gapWindowKey) => nextSelection.has(gapWindowKey));
}

function isSameGapWindowSelectionList(left: string[], right: string[]) {
  return (
    left.length === right.length
    && left.every((gapWindowKey, index) => gapWindowKey === right[index])
  );
}

function filterExpandedGapWindowSelections(value: unknown): ExpandedGapWindowSelections {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value as Record<string, unknown>)
      .map(([rowKey, selectedWindows]) => [rowKey, normalizeExpandedGapWindowSelectionList(selectedWindows)] as const)
      .filter(([, selectedWindows]) => selectedWindows.length > 0),
  );
}

function buildGapWindowSelectionLookup(marketStatus: MarketDataStatus) {
  return Object.fromEntries(
    marketStatus.instruments.map((instrument) => [
      instrumentGapRowKey(instrument),
      Object.fromEntries(
        instrument.backfill_gap_windows.flatMap((gapWindow) => {
          const stableKey = buildGapWindowKey(gapWindow);
          const legacyKey = buildLegacyGapWindowKey(gapWindow);
          return [
            [stableKey, stableKey],
            [legacyKey, stableKey],
          ];
        }),
      ),
    ]),
  ) as Record<string, Record<string, string>>;
}

function instrumentGapRowKey(instrument: MarketDataStatus["instruments"][number]) {
  return `${instrument.instrument_id}:${instrument.timeframe}`;
}

function toggleExpandedGapRow(current: Record<string, boolean>, key: string) {
  if (current[key]) {
    const next = { ...current };
    delete next[key];
    return next;
  }
  return { ...current, [key]: true };
}

function pruneExpandedGapRows(
  current: Record<string, boolean>,
  marketStatus: MarketDataStatus,
) {
  const activeKeys = new Set(
    marketStatus.instruments
      .filter((instrument) => instrument.backfill_gap_windows.length > MAX_VISIBLE_GAP_WINDOWS)
      .map((instrument) => instrumentGapRowKey(instrument)),
  );
  const next = Object.fromEntries(
    Object.entries(current).filter(([key, expanded]) => expanded && activeKeys.has(key)),
  );
  const currentKeys = Object.keys(current);
  const nextKeys = Object.keys(next);
  if (
    currentKeys.length === nextKeys.length &&
    currentKeys.every((key) => next[key] === current[key])
  ) {
    return current;
  }
  return next;
}

function pruneExpandedGapWindowSelections(
  current: ExpandedGapWindowSelections,
  marketStatus: MarketDataStatus,
) {
  const activeSelections = buildGapWindowSelectionLookup(marketStatus);
  const next = Object.fromEntries(
    Object.entries(filterExpandedGapWindowSelections(current)).flatMap(([rowKey, selectedWindows]) => {
      const activeWindowAliases = activeSelections[rowKey] ?? {};
      const activeWindows = new Set(Object.values(activeWindowAliases));
      if (!Object.keys(activeWindowAliases).length) {
        return [];
      }
      const nextSelectedWindows = [...new Set(
        selectedWindows
          .map((windowKey) => activeWindowAliases[windowKey] ?? "")
          .filter((windowKey) => activeWindows.has(windowKey)),
      )].sort();
      return nextSelectedWindows.length ? [[rowKey, nextSelectedWindows]] : [];
    }),
  );
  const currentEntries = Object.entries(filterExpandedGapWindowSelections(current));
  const nextEntries = Object.entries(next);
  if (
    currentEntries.length === nextEntries.length
    && currentEntries.every(([rowKey, selectedWindows], index) => {
      const [nextRowKey, nextSelectedWindows] = nextEntries[index] ?? [];
      return (
        rowKey === nextRowKey
        && selectedWindows.length === (nextSelectedWindows?.length ?? 0)
        && selectedWindows.every((windowKey, windowIndex) => windowKey === nextSelectedWindows?.[windowIndex])
      );
    })
  ) {
    return current;
  }
  return next;
}

function loadExpandedGapRows() {
  const persistedState = loadControlRoomUiState();
  if (persistedState) {
    return persistedState.expandedGapRows;
  }
  return loadLegacyExpandedGapRows();
}

function loadExpandedGapWindowSelections() {
  return loadControlRoomUiState()?.expandedGapWindowSelections ?? {};
}

function defaultControlRoomComparisonSelectionState(): ControlRoomComparisonSelectionState {
  return {
    selectedRunIds: [],
    intent: DEFAULT_COMPARISON_INTENT,
    scoreLink: null,
  };
}

function loadPersistedComparisonSelection(): ControlRoomComparisonSelectionState {
  const urlSelection = loadComparisonSelectionFromUrl();
  if (urlSelection) {
    return urlSelection;
  }
  return loadControlRoomUiState()?.comparisonSelection ?? defaultControlRoomComparisonSelectionState();
}

function defaultComparisonHistoryPanelState(): ComparisonHistoryPanelState {
  return {
    entries: [],
    activeEntryId: null,
  };
}

function defaultComparisonHistoryPanelUiState(): ControlRoomComparisonHistoryPanelUiState {
  return {
    open: false,
    panel: defaultComparisonHistoryPanelState(),
    searchQuery: "",
    showPinnedOnly: false,
    auditFilter: "all",
    showResolvedAuditEntries: true,
    expandedConflictReviewIds: {},
    expandedWorkspaceScoreDetailIds: {},
    focusedWorkspaceScoreDetailSources: {},
    focusedWorkspaceScoreDetailSignalKeys: {},
    expandedWorkspaceScoreSignalDetailIds: {},
    collapsedWorkspaceScoreSignalSubviewIds: {},
    collapsedWorkspaceScoreSignalNestedSubviewIds: {},
    focusedWorkspaceScoreSignalMicroViews: {},
    focusedWorkspaceScoreSignalMicroInteractions: {},
    hoveredWorkspaceScoreSignalMicroTargets: {},
    scrubbedWorkspaceScoreSignalMicroSteps: {},
    selectedWorkspaceScoreSignalMicroNotePages: {},
    activeWorkspaceOverviewRowId: null,
    sync: null,
  };
}

function loadPersistedComparisonHistoryPanelUiState(): ControlRoomComparisonHistoryPanelUiState {
  return loadControlRoomUiState()?.comparisonHistoryPanel ?? defaultComparisonHistoryPanelUiState();
}

function loadControlRoomUiState(): ControlRoomUiStateV4 | null {
  if (typeof window === "undefined") {
    return null;
  }
  return readControlRoomUiStateValue(window.localStorage.getItem(CONTROL_ROOM_UI_STATE_STORAGE_KEY));
}

function readControlRoomUiStateValue(raw: string | null): ControlRoomUiStateV4 | null {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw);
    if (isControlRoomUiStateV4(parsed)) {
      return {
        version: parsed.version,
        expandedGapRows: filterExpandedGapRows(parsed.expandedGapRows),
        expandedGapWindowSelections: filterExpandedGapWindowSelections(parsed.expandedGapWindowSelections),
        comparisonSelection: normalizeControlRoomComparisonSelection(parsed.comparisonSelection),
        comparisonHistoryPanel: normalizeComparisonHistoryPanelUiState(parsed.comparisonHistoryPanel),
      };
    }
    if (isControlRoomUiStateV3(parsed)) {
      return {
        version: CONTROL_ROOM_UI_STATE_VERSION,
        expandedGapRows: filterExpandedGapRows(parsed.expandedGapRows),
        expandedGapWindowSelections: {},
        comparisonSelection: normalizeControlRoomComparisonSelection(parsed.comparisonSelection),
        comparisonHistoryPanel: normalizeComparisonHistoryPanelUiState(parsed.comparisonHistoryPanel),
      };
    }
    if (isControlRoomUiStateV2(parsed)) {
      return {
        version: CONTROL_ROOM_UI_STATE_VERSION,
        expandedGapRows: filterExpandedGapRows(parsed.expandedGapRows),
        expandedGapWindowSelections: {},
        comparisonSelection: normalizeControlRoomComparisonSelection(parsed.comparisonSelection),
        comparisonHistoryPanel: defaultComparisonHistoryPanelUiState(),
      };
    }
    if (!isControlRoomUiStateV1(parsed)) {
      return null;
    }
    return {
      version: CONTROL_ROOM_UI_STATE_VERSION,
      expandedGapRows: filterExpandedGapRows(parsed.expandedGapRows),
      expandedGapWindowSelections: {},
      comparisonSelection: defaultControlRoomComparisonSelectionState(),
      comparisonHistoryPanel: defaultComparisonHistoryPanelUiState(),
    };
  } catch {
    return null;
  }
}

function persistControlRoomUiState(state: {
  comparisonSelection: ControlRoomComparisonSelectionState;
  comparisonHistoryPanel: ControlRoomComparisonHistoryPanelUiState;
  expandedGapRows: Record<string, boolean>;
  expandedGapWindowSelections: ExpandedGapWindowSelections;
}) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: ControlRoomUiStateV4 = {
      version: CONTROL_ROOM_UI_STATE_VERSION,
      comparisonSelection: normalizeControlRoomComparisonSelection(state.comparisonSelection),
      comparisonHistoryPanel: normalizeComparisonHistoryPanelUiState(state.comparisonHistoryPanel),
      expandedGapRows: filterExpandedGapRows(state.expandedGapRows),
      expandedGapWindowSelections: filterExpandedGapWindowSelections(state.expandedGapWindowSelections),
    };
    window.localStorage.setItem(
      CONTROL_ROOM_UI_STATE_STORAGE_KEY,
      JSON.stringify(nextState),
    );
    window.localStorage.removeItem(LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY);
  } catch {
    return;
  }
}

function loadComparisonHistorySyncAuditTrail(
  tabId: string,
): ComparisonHistorySyncAuditEntry[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.sessionStorage.getItem(COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<ComparisonHistorySyncAuditTrailState> | null;
    if (
      !parsed
      || parsed.version !== COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION
      || typeof parsed.tabId !== "string"
      || parsed.tabId !== tabId
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return limitComparisonHistorySyncAuditEntries(
      parsed.entries
        .map((entry) => normalizeComparisonHistorySyncAuditEntry(entry))
        .filter((entry): entry is ComparisonHistorySyncAuditEntry => entry !== null),
    );
  } catch {
    return [];
  }
}

function persistComparisonHistorySyncAuditTrail(
  tabId: string,
  entries: ComparisonHistorySyncAuditEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: ComparisonHistorySyncAuditTrailState = {
      version: COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION,
      tabId,
      entries: limitComparisonHistorySyncAuditEntries(entries),
    };
    window.sessionStorage.setItem(COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY, JSON.stringify(nextState));
  } catch {
    return;
  }
}

function loadComparisonSelectionFromUrl(): ControlRoomComparisonSelectionState | null {
  if (typeof window === "undefined") {
    return null;
  }
  const params = new URLSearchParams(window.location.search);
  const hasComparisonParams = [
    COMPARISON_RUN_ID_SEARCH_PARAM,
    COMPARISON_INTENT_SEARCH_PARAM,
    COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM,
    COMPARISON_FOCUS_SECTION_SEARCH_PARAM,
    COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM,
    COMPARISON_FOCUS_SOURCE_SEARCH_PARAM,
    COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM,
    COMPARISON_FOCUS_DETAIL_SEARCH_PARAM,
    COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM,
    COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM,
    COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM,
  ].some((key) => params.has(key));
  if (!hasComparisonParams) {
    return null;
  }
  const selectedRunIds = normalizeComparisonRunIdList(params.getAll(COMPARISON_RUN_ID_SEARCH_PARAM));
  const intent = normalizeComparisonIntent(params.get(COMPARISON_INTENT_SEARCH_PARAM));
  const focusRunId = params.get(COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM)?.trim() ?? "";
  const focusSection = normalizeComparisonScoreSection(
    params.get(COMPARISON_FOCUS_SECTION_SEARCH_PARAM),
  );
  const focusComponent = params.get(COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM)?.trim() ?? "";
  const focusSource = normalizeComparisonScoreLinkSource(
    params.get(COMPARISON_FOCUS_SOURCE_SEARCH_PARAM),
  ) ?? "drillback";
  const focusOriginRunId = params.get(COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM)?.trim() ?? "";
  const focusDetail = normalizeComparisonScoreLinkSubFocusKey(
    params.get(COMPARISON_FOCUS_DETAIL_SEARCH_PARAM),
  );
  const focusExpanded = normalizeComparisonScoreLinkExpandedState(
    params.get(COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM),
  );
  const focusArtifactExpanded = normalizeComparisonScoreLinkExpandedState(
    params.get(COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM),
  );
  const focusArtifactLineExpanded = normalizeComparisonScoreLinkExpandedState(
    params.get(COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM),
  );
  const focusArtifactLineView = normalizeComparisonScoreLinkArtifactLineDetailView(
    params.get(COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM),
  );
  const focusArtifactLineMicroView = normalizeComparisonScoreLinkArtifactLineMicroView(
    params.get(COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM),
  );
  const focusArtifactLineNotePage = normalizeComparisonScoreLinkArtifactLineNotePage(
    params.get(COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM),
  );
  const focusArtifactLineHoverKey = normalizeComparisonScoreLinkArtifactLineDetailHoverKey(
    params.get(COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM),
  );
  const focusArtifactLineScrubStep = normalizeComparisonScoreLinkArtifactLineScrubStep(
    params.get(COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM),
  );
  const focusTooltipKey = normalizeComparisonScoreLinkTooltipKey(
    params.get(COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM),
  );
  const focusArtifactHoverKey = normalizeComparisonScoreLinkArtifactHoverKey(
    params.get(COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM),
  );

  return {
    intent,
    scoreLink:
      focusRunId && focusSection && focusComponent
        ? {
            componentKey: focusComponent,
            detailExpanded: focusExpanded,
            artifactDetailExpanded: focusArtifactExpanded,
            artifactLineDetailExpanded: focusArtifactLineExpanded,
            artifactLineDetailView: focusArtifactLineView,
            artifactLineMicroView: focusArtifactLineMicroView,
            artifactLineNotePage: focusArtifactLineNotePage,
            artifactLineDetailHoverKey: focusArtifactLineHoverKey,
            artifactLineDetailScrubStep: focusArtifactLineScrubStep,
            narrativeRunId: focusRunId,
            originRunId: focusOriginRunId || null,
            section: focusSection,
            source: focusSource,
            subFocusKey: focusDetail,
            tooltipKey: focusTooltipKey,
            artifactHoverKey: focusArtifactHoverKey,
          }
        : null,
    selectedRunIds,
  };
}

function buildComparisonSelectionHistoryUrl(
  selection: ControlRoomComparisonSelectionState,
  baseHref?: string,
) {
  const url =
    typeof window !== "undefined"
      ? new URL(baseHref ?? window.location.href)
      : new URL(baseHref ?? "http://localhost/");
  const params = url.searchParams;
  params.delete(COMPARISON_RUN_ID_SEARCH_PARAM);
  params.delete(COMPARISON_INTENT_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_SECTION_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_SOURCE_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_DETAIL_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM);

  const normalizedSelection = normalizeControlRoomComparisonSelection(selection);
  normalizedSelection.selectedRunIds.forEach((runId) => params.append(COMPARISON_RUN_ID_SEARCH_PARAM, runId));
  if (normalizedSelection.intent !== DEFAULT_COMPARISON_INTENT || normalizedSelection.selectedRunIds.length) {
    params.set(COMPARISON_INTENT_SEARCH_PARAM, normalizedSelection.intent);
  }
  if (normalizedSelection.scoreLink && normalizedSelection.selectedRunIds.length) {
    params.set(COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM, normalizedSelection.scoreLink.narrativeRunId);
    params.set(COMPARISON_FOCUS_SECTION_SEARCH_PARAM, normalizedSelection.scoreLink.section);
    params.set(COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM, normalizedSelection.scoreLink.componentKey);
    params.set(COMPARISON_FOCUS_SOURCE_SEARCH_PARAM, normalizedSelection.scoreLink.source);
    if (normalizedSelection.scoreLink.originRunId) {
      params.set(COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM, normalizedSelection.scoreLink.originRunId);
    }
    if (normalizedSelection.scoreLink.subFocusKey) {
      params.set(COMPARISON_FOCUS_DETAIL_SEARCH_PARAM, normalizedSelection.scoreLink.subFocusKey);
    }
    if (normalizedSelection.scoreLink.detailExpanded !== null) {
      params.set(
        COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM,
        normalizedSelection.scoreLink.detailExpanded ? "1" : "0",
      );
    }
    if (normalizedSelection.scoreLink.artifactDetailExpanded !== null) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM,
        normalizedSelection.scoreLink.artifactDetailExpanded ? "1" : "0",
      );
    }
    if (normalizedSelection.scoreLink.artifactLineDetailExpanded !== null) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM,
        normalizedSelection.scoreLink.artifactLineDetailExpanded ? "1" : "0",
      );
    }
    if (normalizedSelection.scoreLink.artifactLineDetailView) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM,
        normalizedSelection.scoreLink.artifactLineDetailView,
      );
    }
    if (normalizedSelection.scoreLink.artifactLineMicroView) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM,
        normalizedSelection.scoreLink.artifactLineMicroView,
      );
    }
    if (normalizedSelection.scoreLink.artifactLineNotePage !== null) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM,
        String(normalizedSelection.scoreLink.artifactLineNotePage),
      );
    }
    if (normalizedSelection.scoreLink.artifactLineDetailHoverKey) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM,
        normalizedSelection.scoreLink.artifactLineDetailHoverKey,
      );
    }
    if (normalizedSelection.scoreLink.artifactLineDetailScrubStep !== null) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM,
        String(normalizedSelection.scoreLink.artifactLineDetailScrubStep),
      );
    }
    if (normalizedSelection.scoreLink.tooltipKey) {
      params.set(COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM, normalizedSelection.scoreLink.tooltipKey);
    }
    if (normalizedSelection.scoreLink.artifactHoverKey) {
      params.set(
        COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM,
        normalizedSelection.scoreLink.artifactHoverKey,
      );
    }
  }
  const nextSearch = params.toString();
  return `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash}`;
}

function readComparisonHistoryBrowserState(value: unknown): ComparisonHistoryBrowserState | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const candidate = (value as Record<string, unknown>)[COMPARISON_HISTORY_BROWSER_STATE_KEY];
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) {
    return null;
  }
  const parsed = candidate as Partial<ComparisonHistoryBrowserState>;
  if (
    parsed.version !== COMPARISON_HISTORY_BROWSER_STATE_VERSION
    || typeof parsed.entryId !== "string"
    || typeof parsed.stepIndex !== "number"
    || typeof parsed.label !== "string"
    || typeof parsed.summary !== "string"
    || typeof parsed.title !== "string"
  ) {
    return null;
  }
  return {
    version: parsed.version,
    entryId: parsed.entryId,
    stepIndex: parsed.stepIndex,
    label: parsed.label,
    summary: parsed.summary,
    title: parsed.title,
    selection: normalizeControlRoomComparisonSelection(parsed.selection),
  };
}

function buildComparisonHistoryBrowserState(
  currentState: unknown,
  selection: ControlRoomComparisonSelectionState,
  step: ComparisonHistoryStepDescriptor,
  entryId: string,
  stepIndex: number,
) {
  const nextState =
    currentState && typeof currentState === "object" && !Array.isArray(currentState)
      ? { ...(currentState as Record<string, unknown>) }
      : {};
  nextState[COMPARISON_HISTORY_BROWSER_STATE_KEY] = {
    version: COMPARISON_HISTORY_BROWSER_STATE_VERSION,
    entryId,
    stepIndex,
    label: step.label,
    summary: step.summary,
    title: step.title,
    selection: normalizeControlRoomComparisonSelection(selection),
  } satisfies ComparisonHistoryBrowserState;
  return nextState;
}

function isSameComparisonHistoryBrowserState(
  left: ComparisonHistoryBrowserState | null,
  right: ComparisonHistoryBrowserState | null,
) {
  if (left === right) {
    return true;
  }
  if (!left || !right) {
    return false;
  }
  return (
    left.label === right.label
    && left.summary === right.summary
    && left.title === right.title
    && left.stepIndex === right.stepIndex
    && isSameComparisonSelection(left.selection, right.selection)
  );
}

function persistComparisonSelectionToUrl(
  selection: ControlRoomComparisonSelectionState,
  step: ComparisonHistoryStepDescriptor,
  entryId: string,
  stepIndex: number,
  mode: Exclude<ComparisonHistoryWriteMode, "skip"> = "replace",
) {
  if (typeof window === "undefined") {
    return;
  }
  const nextUrl = buildComparisonSelectionHistoryUrl(selection);
  const nextState = buildComparisonHistoryBrowserState(
    window.history.state,
    selection,
    step,
    entryId,
    stepIndex,
  );
  if (typeof document !== "undefined") {
    document.title = step.title;
  }
  if (mode === "push") {
    window.history.pushState(nextState, step.title, nextUrl);
    return;
  }
  window.history.replaceState(nextState, step.title, nextUrl);
}

function buildComparisonHistoryEntryId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `compare-step-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function buildComparisonHistoryTabId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `compare-tab-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function formatComparisonHistoryTabLabel(tabId: string) {
  return `Tab ${tabId.replace(/[^a-z0-9]/gi, "").slice(0, 4).toUpperCase() || "SYNC"}`;
}

function loadComparisonHistoryTabIdentity(): ComparisonHistoryTabIdentity {
  const fallbackTabId = buildComparisonHistoryTabId();
  if (typeof window === "undefined") {
    return {
      tabId: fallbackTabId,
      label: formatComparisonHistoryTabLabel(fallbackTabId),
    };
  }
  try {
    const existingTabId = window.sessionStorage.getItem(COMPARISON_HISTORY_TAB_ID_SESSION_KEY)?.trim();
    const tabId = existingTabId || fallbackTabId;
    if (!existingTabId) {
      window.sessionStorage.setItem(COMPARISON_HISTORY_TAB_ID_SESSION_KEY, tabId);
    }
    return {
      tabId,
      label: formatComparisonHistoryTabLabel(tabId),
    };
  } catch {
    return {
      tabId: fallbackTabId,
      label: formatComparisonHistoryTabLabel(fallbackTabId),
    };
  }
}

function buildComparisonHistoryPanelSyncState(
  tabIdentity: ComparisonHistoryTabIdentity,
  updatedAt = new Date().toISOString(),
): ComparisonHistoryPanelSyncState {
  return {
    tabId: tabIdentity.tabId,
    tabLabel: tabIdentity.label,
    updatedAt,
  };
}

function buildComparisonHistorySyncSignature(state: {
  comparisonSelection: ControlRoomComparisonSelectionState;
  comparisonHistoryPanel: ComparisonHistoryPanelState;
  expandedGapRows: Record<string, boolean>;
  expandedGapWindowSelections: ExpandedGapWindowSelections;
  historyBrowserOpen: boolean;
  historySearchQuery: string;
  showPinnedHistoryOnly: boolean;
  auditFilter: ComparisonHistorySyncAuditFilter;
  showResolvedAuditEntries: boolean;
}) {
  return JSON.stringify({
    comparisonSelection: normalizeControlRoomComparisonSelection(state.comparisonSelection),
    comparisonHistoryPanel: normalizeComparisonHistoryPanelState(state.comparisonHistoryPanel),
    expandedGapRowKeys: listComparisonHistoryExpandedGapRowKeys(state.expandedGapRows),
    expandedGapWindowSelections: filterExpandedGapWindowSelections(state.expandedGapWindowSelections),
    historyBrowserOpen: state.historyBrowserOpen,
    historySearchQuery: state.historySearchQuery.trim(),
    showPinnedHistoryOnly: state.showPinnedHistoryOnly,
    auditFilter: state.auditFilter,
    showResolvedAuditEntries: state.showResolvedAuditEntries,
  });
}

function buildComparisonHistorySyncAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `compare-sync-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function buildComparisonHistoryPanelEntry(
  browserState: ComparisonHistoryBrowserState,
  url: string,
): ComparisonHistoryPanelEntry {
  const now = new Date().toISOString();
  return {
    entryId: browserState.entryId,
    stepIndex: browserState.stepIndex,
    label: browserState.label,
    summary: browserState.summary,
    title: browserState.title,
    url,
    hidden: false,
    pinned: false,
    recordedAt: now,
    selection: normalizeControlRoomComparisonSelection(browserState.selection),
  };
}

function findComparisonHistoryPanelEntryForSelection(
  panel: ComparisonHistoryPanelState,
  selection: ControlRoomComparisonSelectionState,
) {
  const matchingEntries = panel.entries.filter((entry) =>
    !entry.hidden && isSameComparisonSelection(entry.selection, selection),
  );
  if (!matchingEntries.length) {
    return null;
  }
  if (panel.activeEntryId) {
    const activeMatch = matchingEntries.find((entry) => entry.entryId === panel.activeEntryId);
    if (activeMatch) {
      return activeMatch;
    }
  }
  return matchingEntries[matchingEntries.length - 1] ?? null;
}

function mergeComparisonHistoryPanelState(
  local: ComparisonHistoryPanelState,
  remote: ComparisonHistoryPanelState,
  selection: ControlRoomComparisonSelectionState,
): ComparisonHistoryPanelState {
  const mergedEntries = mergeComparisonHistoryPanelEntries(local.entries, remote.entries);
  const selectionMatch = findComparisonHistoryPanelEntryForSelection(
    {
      entries: mergedEntries,
      activeEntryId: local.activeEntryId,
    },
    selection,
  );
  if (selectionMatch) {
    return {
      entries: mergedEntries,
      activeEntryId: selectionMatch.entryId,
    };
  }
  if (local.activeEntryId && mergedEntries.some((entry) => entry.entryId === local.activeEntryId)) {
    return {
      entries: mergedEntries,
      activeEntryId: local.activeEntryId,
    };
  }
  if (remote.activeEntryId && mergedEntries.some((entry) => entry.entryId === remote.activeEntryId)) {
    return {
      entries: mergedEntries,
      activeEntryId: remote.activeEntryId,
    };
  }
  return {
    entries: mergedEntries,
    activeEntryId: mergedEntries[mergedEntries.length - 1]?.entryId ?? null,
  };
}

function mergeComparisonHistoryPanelEntries(
  localEntries: ComparisonHistoryPanelEntry[],
  remoteEntries: ComparisonHistoryPanelEntry[],
) {
  const mergedEntries = new Map<string, ComparisonHistoryPanelEntry>();
  localEntries.forEach((entry) => {
    mergedEntries.set(entry.entryId, entry);
  });
  remoteEntries.forEach((entry) => {
    mergedEntries.set(entry.entryId, entry);
  });
  return limitComparisonHistoryPanelEntries(
    sortComparisonHistoryPanelEntries([...mergedEntries.values()]),
  );
}

function reconcileComparisonHistoryPanelState(
  current: ComparisonHistoryPanelState,
  entry: ComparisonHistoryPanelEntry,
  mode: "push" | "replace" | "activate",
): ComparisonHistoryPanelState {
  const existingIndex = current.entries.findIndex((candidate) => candidate.entryId === entry.entryId);
  const existingEntry = existingIndex >= 0 ? current.entries[existingIndex] : null;
  const mergedEntry = existingEntry
    ? {
        ...entry,
        pinned: existingEntry.pinned,
        recordedAt: existingEntry.recordedAt,
      }
    : entry;

  if (mode === "activate") {
    if (existingIndex >= 0) {
      return {
        entries: sortComparisonHistoryPanelEntries(
          current.entries.map((candidate, index) => (index === existingIndex ? mergedEntry : candidate)),
        ),
        activeEntryId: mergedEntry.entryId,
      };
    }
    return {
      entries: limitComparisonHistoryPanelEntries(
        sortComparisonHistoryPanelEntries([...current.entries, mergedEntry]),
      ),
      activeEntryId: mergedEntry.entryId,
    };
  }

  if (mode === "push") {
    const activeStepIndex = current.activeEntryId
      ? current.entries.find((candidate) => candidate.entryId === current.activeEntryId)?.stepIndex ?? -1
      : -1;
    const baseEntries = current.entries.filter((candidate) => candidate.stepIndex <= activeStepIndex);
    const nextEntries = [...baseEntries.filter((candidate) => candidate.entryId !== mergedEntry.entryId), mergedEntry];
    return {
      entries: limitComparisonHistoryPanelEntries(sortComparisonHistoryPanelEntries(nextEntries)),
      activeEntryId: mergedEntry.entryId,
    };
  }

  if (existingIndex >= 0) {
    return {
      entries: sortComparisonHistoryPanelEntries(
        current.entries.map((candidate, index) => (index === existingIndex ? mergedEntry : candidate)),
      ),
      activeEntryId: mergedEntry.entryId,
    };
  }

  const activeIndex = current.activeEntryId
    ? current.entries.findIndex((candidate) => candidate.entryId === current.activeEntryId)
    : -1;
  if (activeIndex >= 0) {
    return {
      entries: sortComparisonHistoryPanelEntries(
        current.entries.map((candidate, index) => (index === activeIndex ? mergedEntry : candidate)),
      ),
      activeEntryId: mergedEntry.entryId,
    };
  }

  return {
    entries: [mergedEntry],
    activeEntryId: mergedEntry.entryId,
  };
}

function sortComparisonHistoryPanelEntries(entries: ComparisonHistoryPanelEntry[]) {
  return [...entries].sort((left, right) => left.stepIndex - right.stepIndex);
}

function limitComparisonHistoryPanelEntries(entries: ComparisonHistoryPanelEntry[]) {
  if (entries.length <= MAX_COMPARISON_HISTORY_PANEL_ENTRIES) {
    return entries;
  }
  const visibleEntries = entries.filter((entry) => !entry.hidden);
  const hiddenEntries = entries.filter((entry) => entry.hidden);
  const pinnedEntries = visibleEntries.filter((entry) => entry.pinned);
  if (pinnedEntries.length >= MAX_COMPARISON_HISTORY_PANEL_ENTRIES) {
    return sortComparisonHistoryPanelEntries(
      pinnedEntries.slice(-MAX_COMPARISON_HISTORY_PANEL_ENTRIES),
    );
  }
  const unpinnedEntries = visibleEntries.filter((entry) => !entry.pinned);
  return sortComparisonHistoryPanelEntries([
    ...pinnedEntries,
    ...unpinnedEntries.slice(-(MAX_COMPARISON_HISTORY_PANEL_ENTRIES - pinnedEntries.length)),
    ...hiddenEntries.slice(-MAX_COMPARISON_HISTORY_PANEL_ENTRIES),
  ]).slice(-MAX_COMPARISON_HISTORY_PANEL_ENTRIES);
}

function normalizeComparisonHistoryPanelUiState(
  value: Partial<ControlRoomComparisonHistoryPanelUiState> | null | undefined,
): ControlRoomComparisonHistoryPanelUiState {
  return {
    open: value?.open === true,
    panel: normalizeComparisonHistoryPanelState(value?.panel),
    searchQuery: typeof value?.searchQuery === "string" ? value.searchQuery : "",
    showPinnedOnly: value?.showPinnedOnly === true,
    auditFilter: normalizeComparisonHistorySyncAuditFilter(value?.auditFilter),
    showResolvedAuditEntries: value?.showResolvedAuditEntries !== false,
    expandedConflictReviewIds:
      value?.expandedConflictReviewIds && typeof value.expandedConflictReviewIds === "object"
        ? Object.entries(value.expandedConflictReviewIds).reduce<Record<string, boolean>>(
            (accumulator, [key, candidate]) => {
              if (candidate === true) {
                accumulator[key] = true;
              }
              return accumulator;
            },
            {},
          )
        : {},
    expandedWorkspaceScoreDetailIds:
      value?.expandedWorkspaceScoreDetailIds && typeof value.expandedWorkspaceScoreDetailIds === "object"
        ? Object.entries(value.expandedWorkspaceScoreDetailIds).reduce<Record<string, boolean>>(
            (accumulator, [key, candidate]) => {
              if (candidate === true) {
                accumulator[key] = true;
              }
              return accumulator;
            },
            {},
          )
        : {},
    focusedWorkspaceScoreDetailSources:
      value?.focusedWorkspaceScoreDetailSources
      && typeof value.focusedWorkspaceScoreDetailSources === "object"
        ? Object.entries(value.focusedWorkspaceScoreDetailSources).reduce<
            Record<string, ComparisonHistorySyncConflictFieldSource>
          >((accumulator, [key, candidate]) => {
            if (candidate === "local" || candidate === "remote") {
              accumulator[key] = candidate;
            }
            return accumulator;
          }, {})
        : {},
    focusedWorkspaceScoreDetailSignalKeys:
      value?.focusedWorkspaceScoreDetailSignalKeys
      && typeof value.focusedWorkspaceScoreDetailSignalKeys === "object"
        ? Object.entries(value.focusedWorkspaceScoreDetailSignalKeys).reduce<Record<string, string>>(
            (accumulator, [key, candidate]) => {
              if (typeof candidate === "string" && candidate.trim()) {
                accumulator[key] = candidate;
              }
              return accumulator;
            },
            {},
          )
        : {},
    expandedWorkspaceScoreSignalDetailIds:
      value?.expandedWorkspaceScoreSignalDetailIds
      && typeof value.expandedWorkspaceScoreSignalDetailIds === "object"
        ? Object.entries(value.expandedWorkspaceScoreSignalDetailIds).reduce<Record<string, boolean>>(
            (accumulator, [key, candidate]) => {
              if (candidate === true) {
                accumulator[key] = true;
              }
              return accumulator;
            },
            {},
          )
        : {},
    collapsedWorkspaceScoreSignalSubviewIds:
      value?.collapsedWorkspaceScoreSignalSubviewIds
      && typeof value.collapsedWorkspaceScoreSignalSubviewIds === "object"
        ? Object.entries(value.collapsedWorkspaceScoreSignalSubviewIds).reduce<Record<string, boolean>>(
            (accumulator, [key, candidate]) => {
              if (candidate === true) {
                accumulator[key] = true;
              }
              return accumulator;
            },
            {},
          )
        : {},
    collapsedWorkspaceScoreSignalNestedSubviewIds:
      value?.collapsedWorkspaceScoreSignalNestedSubviewIds
      && typeof value.collapsedWorkspaceScoreSignalNestedSubviewIds === "object"
        ? Object.entries(value.collapsedWorkspaceScoreSignalNestedSubviewIds).reduce<Record<string, boolean>>(
            (accumulator, [key, candidate]) => {
              if (candidate === true) {
                accumulator[key] = true;
              }
              return accumulator;
            },
            {},
          )
        : {},
    focusedWorkspaceScoreSignalMicroViews:
      value?.focusedWorkspaceScoreSignalMicroViews
      && typeof value.focusedWorkspaceScoreSignalMicroViews === "object"
        ? Object.entries(value.focusedWorkspaceScoreSignalMicroViews).reduce<
            Record<string, ComparisonHistorySyncWorkspaceSignalMicroViewKey>
          >((accumulator, [key, candidate]) => {
            if (
              candidate === "summary"
              || candidate === "trace"
              || candidate === "recommendation"
              || candidate === "alternative"
              || candidate === "position"
              || candidate === "score"
              || candidate === "share"
              || candidate === "impact"
              || candidate === "selection"
              || candidate === "lane"
              || candidate === "gap"
              || candidate === "reason"
            ) {
              accumulator[key] = candidate;
            }
            return accumulator;
          }, {})
        : {},
    focusedWorkspaceScoreSignalMicroInteractions:
      value?.focusedWorkspaceScoreSignalMicroInteractions
      && typeof value.focusedWorkspaceScoreSignalMicroInteractions === "object"
        ? Object.entries(value.focusedWorkspaceScoreSignalMicroInteractions).reduce<
            Record<string, ComparisonHistorySyncWorkspaceSignalMicroInteractionKey>
          >((accumulator, [key, candidate]) => {
            if (
              candidate === "lane"
              || candidate === "polarity"
              || candidate === "signal"
              || candidate === "source"
              || candidate === "support"
              || candidate === "tradeoff"
              || candidate === "rank"
              || candidate === "score"
              || candidate === "share"
              || candidate === "impact"
              || candidate === "selected"
              || candidate === "focusedLane"
              || candidate === "gap"
              || candidate === "reason"
            ) {
              accumulator[key] = candidate;
            }
            return accumulator;
          }, {})
        : {},
    hoveredWorkspaceScoreSignalMicroTargets:
      value?.hoveredWorkspaceScoreSignalMicroTargets
      && typeof value.hoveredWorkspaceScoreSignalMicroTargets === "object"
        ? Object.entries(value.hoveredWorkspaceScoreSignalMicroTargets).reduce<Record<string, string>>(
            (accumulator, [key, candidate]) => {
              if (typeof candidate === "string" && candidate.trim()) {
                accumulator[key] = candidate;
              }
              return accumulator;
            },
            {},
          )
        : {},
    scrubbedWorkspaceScoreSignalMicroSteps:
      value?.scrubbedWorkspaceScoreSignalMicroSteps
      && typeof value.scrubbedWorkspaceScoreSignalMicroSteps === "object"
        ? Object.entries(value.scrubbedWorkspaceScoreSignalMicroSteps).reduce<Record<string, number>>(
            (accumulator, [key, candidate]) => {
              if (typeof candidate === "number" && Number.isInteger(candidate) && candidate >= 0) {
                accumulator[key] = candidate;
              }
              return accumulator;
            },
            {},
          )
        : {},
    selectedWorkspaceScoreSignalMicroNotePages:
      value?.selectedWorkspaceScoreSignalMicroNotePages
      && typeof value.selectedWorkspaceScoreSignalMicroNotePages === "object"
        ? Object.entries(value.selectedWorkspaceScoreSignalMicroNotePages).reduce<Record<string, number>>(
            (accumulator, [key, candidate]) => {
              if (typeof candidate === "number" && Number.isInteger(candidate) && candidate >= 0) {
                accumulator[key] = candidate;
              }
              return accumulator;
            },
            {},
          )
        : {},
    activeWorkspaceOverviewRowId:
      typeof value?.activeWorkspaceOverviewRowId === "string"
        ? value.activeWorkspaceOverviewRowId.trim() || null
        : null,
    sync: normalizeComparisonHistoryPanelSyncState(value?.sync),
  };
}

function normalizeComparisonHistorySyncAuditFilter(value: unknown): ComparisonHistorySyncAuditFilter {
  return value === "conflicts" || value === "preferences" || value === "workspace" || value === "merges"
    ? value
    : "all";
}

function normalizeComparisonHistoryPanelSyncState(
  value: Partial<ComparisonHistoryPanelSyncState> | null | undefined,
): ComparisonHistoryPanelSyncState | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const tabId = typeof value.tabId === "string" ? value.tabId.trim() : "";
  const tabLabel = typeof value.tabLabel === "string" ? value.tabLabel.trim() : "";
  const updatedAt = typeof value.updatedAt === "string" ? value.updatedAt : "";
  if (!tabId || !tabLabel || !updatedAt) {
    return null;
  }
  return {
    tabId,
    tabLabel,
    updatedAt,
  };
}

function normalizeComparisonHistoryPanelState(
  value: Partial<ComparisonHistoryPanelState> | null | undefined,
): ComparisonHistoryPanelState {
  const entries = limitComparisonHistoryPanelEntries(
    sortComparisonHistoryPanelEntries(
      Array.isArray(value?.entries)
        ? value.entries
            .map((entry) => normalizeComparisonHistoryPanelEntry(entry))
            .filter((entry): entry is ComparisonHistoryPanelEntry => entry !== null)
        : [],
    ),
  );
  const activeEntryId =
    typeof value?.activeEntryId === "string" && entries.some((entry) => entry.entryId === value.activeEntryId)
      ? value.activeEntryId
      : entries[entries.length - 1]?.entryId ?? null;
  return {
    entries,
    activeEntryId,
  };
}

function normalizeComparisonHistoryPanelEntry(value: unknown): ComparisonHistoryPanelEntry | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonHistoryPanelEntry>;
  const entryId = typeof candidate.entryId === "string" ? candidate.entryId.trim() : "";
  const label = typeof candidate.label === "string" ? candidate.label : "";
  const summary = typeof candidate.summary === "string" ? candidate.summary : "";
  const title = typeof candidate.title === "string" ? candidate.title : "";
  const url = typeof candidate.url === "string" ? candidate.url : "";
  const recordedAt = typeof candidate.recordedAt === "string" ? candidate.recordedAt : "";
  if (
    !entryId
    || !label
    || !summary
    || !title
    || !url
    || !recordedAt
    || typeof candidate.stepIndex !== "number"
    || !Number.isFinite(candidate.stepIndex)
  ) {
    return null;
  }
  return {
    entryId,
    stepIndex: candidate.stepIndex,
    label,
    summary,
    title,
    url,
    hidden: candidate.hidden === true,
    pinned: candidate.pinned === true,
    recordedAt,
    selection: normalizeControlRoomComparisonSelection(candidate.selection),
  };
}

function normalizeComparisonHistorySyncAuditEntry(
  value: unknown,
): ComparisonHistorySyncAuditEntry | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonHistorySyncAuditEntry>;
  const auditId = typeof candidate.auditId === "string" ? candidate.auditId.trim() : "";
  const kind = candidate.kind;
  const summary = typeof candidate.summary === "string" ? candidate.summary : "";
  const detail = typeof candidate.detail === "string" ? candidate.detail : "";
  const recordedAt = typeof candidate.recordedAt === "string" ? candidate.recordedAt : "";
  const sourceTabId = typeof candidate.sourceTabId === "string" ? candidate.sourceTabId.trim() : "";
  const sourceTabLabel =
    typeof candidate.sourceTabLabel === "string" ? candidate.sourceTabLabel.trim() : "";
  if (
    !auditId
    || (kind !== "merge" && kind !== "conflict" && kind !== "preferences" && kind !== "workspace")
    || !summary
    || !detail
    || !recordedAt
    || !sourceTabId
    || !sourceTabLabel
  ) {
    return null;
  }
  return {
    auditId,
    kind,
    summary,
    detail,
    recordedAt,
    sourceTabId,
    sourceTabLabel,
    conflictReview: normalizeComparisonHistorySyncConflictReview(candidate.conflictReview),
    preferenceReview: normalizeComparisonHistorySyncPreferenceReview(candidate.preferenceReview),
    workspaceReview: normalizeComparisonHistorySyncWorkspaceReview(candidate.workspaceReview),
  };
}

function normalizeComparisonHistorySyncConflictReview(
  value: unknown,
): ComparisonHistorySyncConflictReview | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonHistorySyncConflictReview>;
  const entryId = typeof candidate.entryId === "string" ? candidate.entryId.trim() : "";
  const entryLabel = typeof candidate.entryLabel === "string" ? candidate.entryLabel : "";
  const localEntry = normalizeComparisonHistoryPanelEntry(candidate.localEntry);
  const remoteEntry = normalizeComparisonHistoryPanelEntry(candidate.remoteEntry);
  if (!entryId || !entryLabel || !localEntry || !remoteEntry) {
    return null;
  }
  const selectedSources = normalizeComparisonHistorySyncConflictSelectedSources(candidate.selectedSources);
  return {
    entryId,
    entryLabel,
    localEntry,
    remoteEntry,
    selectedSources,
    resolvedAt: typeof candidate.resolvedAt === "string" ? candidate.resolvedAt : null,
    resolutionSummary:
      typeof candidate.resolutionSummary === "string" ? candidate.resolutionSummary : null,
  };
}

function normalizeComparisonHistorySyncConflictSelectedSources(
  value: unknown,
): Partial<Record<ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource>> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS.reduce<
    Partial<Record<ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource>>
  >((accumulator, definition) => {
    const candidate = (value as Record<string, unknown>)[definition.fieldKey];
    if (candidate === "local" || candidate === "remote") {
      accumulator[definition.fieldKey] = candidate;
    }
    return accumulator;
  }, {});
}

function normalizeComparisonHistorySyncPreferenceReview(
  value: unknown,
): ComparisonHistorySyncPreferenceReview | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonHistorySyncPreferenceReview>;
  const localState = normalizeComparisonHistorySyncPreferenceState(candidate.localState);
  const remoteState = normalizeComparisonHistorySyncPreferenceState(candidate.remoteState);
  if (!localState || !remoteState) {
    return null;
  }
  return {
    localState,
    remoteState,
    selectedSources: normalizeComparisonHistorySyncPreferenceSelectedSources(candidate.selectedSources),
    resolvedAt: typeof candidate.resolvedAt === "string" ? candidate.resolvedAt : null,
    resolutionSummary:
      typeof candidate.resolutionSummary === "string" ? candidate.resolutionSummary : null,
  };
}

function normalizeComparisonHistorySyncWorkspaceReview(
  value: unknown,
): ComparisonHistorySyncWorkspaceReview | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonHistorySyncWorkspaceReview>;
  const localState = normalizeComparisonHistorySyncWorkspaceState(candidate.localState);
  const remoteState = normalizeComparisonHistorySyncWorkspaceState(candidate.remoteState);
  if (!localState || !remoteState) {
    return null;
  }
  return {
    localState,
    remoteState,
    selectedSources: normalizeComparisonHistorySyncWorkspaceSelectedSources(candidate.selectedSources),
    resolvedAt: typeof candidate.resolvedAt === "string" ? candidate.resolvedAt : null,
    resolutionSummary:
      typeof candidate.resolutionSummary === "string" ? candidate.resolutionSummary : null,
  };
}

function normalizeComparisonHistorySyncPreferenceState(
  value: unknown,
): ComparisonHistorySyncPreferenceState | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonHistorySyncPreferenceState>;
  return {
    open: candidate.open === true,
    searchQuery: typeof candidate.searchQuery === "string" ? candidate.searchQuery : "",
    showPinnedOnly: candidate.showPinnedOnly === true,
    auditFilter: normalizeComparisonHistorySyncAuditFilter(candidate.auditFilter),
    showResolvedAuditEntries: candidate.showResolvedAuditEntries !== false,
  };
}

function normalizeComparisonHistorySyncWorkspaceState(
  value: unknown,
): ComparisonHistorySyncWorkspaceState | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonHistorySyncWorkspaceState>;
  return {
    comparisonSelection: normalizeControlRoomComparisonSelection(candidate.comparisonSelection),
    expandedGapRows: filterExpandedGapRows(candidate.expandedGapRows),
    expandedGapWindowSelections: filterExpandedGapWindowSelections(candidate.expandedGapWindowSelections),
  };
}

function normalizeComparisonHistorySyncPreferenceSelectedSources(
  value: unknown,
): Partial<Record<ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncConflictFieldSource>> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS.reduce<
    Partial<Record<ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncConflictFieldSource>>
  >((accumulator, definition) => {
    const candidate = (value as Record<string, unknown>)[definition.fieldKey];
    if (candidate === "local" || candidate === "remote") {
      accumulator[definition.fieldKey] = candidate;
    }
    return accumulator;
  }, {});
}

function normalizeComparisonHistorySyncWorkspaceSelectedSources(
  value: unknown,
): Partial<Record<ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncConflictFieldSource>> {
  if (!value || typeof value !== "object") {
    return {};
  }
  const selectedSources = COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS.reduce<
    Partial<Record<ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncConflictFieldSource>>
  >((accumulator, definition) => {
    const candidate = (value as Record<string, unknown>)[definition.fieldKey];
    if (candidate === "local" || candidate === "remote") {
      accumulator[definition.fieldKey] = candidate;
    }
    return accumulator;
  }, {});
  Object.entries(value as Record<string, unknown>).forEach(([key, candidate]) => {
    if (!key.startsWith("expandedGapRows:") && !key.startsWith("expandedGapWindows|")) {
      return;
    }
    if (candidate === "local" || candidate === "remote") {
      selectedSources[key as ComparisonHistorySyncWorkspaceReviewSelectionKey] = candidate;
    }
  });
  return selectedSources;
}

function limitComparisonHistorySyncAuditEntries(entries: ComparisonHistorySyncAuditEntry[]) {
  return entries.slice(-MAX_COMPARISON_HISTORY_SYNC_AUDIT_ENTRIES);
}

function appendComparisonHistorySyncAuditEntries(
  currentEntries: ComparisonHistorySyncAuditEntry[],
  nextEntries: ComparisonHistorySyncAuditEntry[],
) {
  if (!nextEntries.length) {
    return currentEntries;
  }
  return limitComparisonHistorySyncAuditEntries([
    ...currentEntries,
    ...nextEntries,
  ]);
}

function isSameComparisonHistoryPanelState(
  left: ComparisonHistoryPanelState,
  right: ComparisonHistoryPanelState,
) {
  return (
    left.activeEntryId === right.activeEntryId
    && left.entries.length === right.entries.length
    && left.entries.every((entry, index) =>
      isSameComparisonHistoryPanelEntry(entry, right.entries[index]),
    )
  );
}

function isSameComparisonHistoryPanelSyncState(
  left: ComparisonHistoryPanelSyncState | null,
  right: ComparisonHistoryPanelSyncState | null,
) {
  if (!left || !right) {
    return left === right;
  }
  return (
    left.tabId === right.tabId
    && left.tabLabel === right.tabLabel
    && left.updatedAt === right.updatedAt
  );
}

function isSameComparisonHistoryPanelEntry(
  left: ComparisonHistoryPanelEntry,
  right: ComparisonHistoryPanelEntry | undefined,
) {
  if (!right) {
    return false;
  }
  return (
    left.entryId === right.entryId
    && left.stepIndex === right.stepIndex
    && left.label === right.label
    && left.summary === right.summary
    && left.title === right.title
    && left.url === right.url
    && left.hidden === right.hidden
    && left.pinned === right.pinned
    && left.recordedAt === right.recordedAt
    && isSameComparisonSelection(left.selection, right.selection)
  );
}

function getComparisonHistoryPanelEntryChangedFields(
  localEntry: ComparisonHistoryPanelEntry,
  remoteEntry: ComparisonHistoryPanelEntry,
) {
  const fields: string[] = [];
  if (localEntry.stepIndex !== remoteEntry.stepIndex) {
    fields.push("step");
  }
  if (localEntry.label !== remoteEntry.label) {
    fields.push("label");
  }
  if (localEntry.summary !== remoteEntry.summary) {
    fields.push("summary");
  }
  if (localEntry.title !== remoteEntry.title) {
    fields.push("title");
  }
  if (localEntry.url !== remoteEntry.url) {
    fields.push("link");
  }
  if (localEntry.hidden !== remoteEntry.hidden) {
    fields.push(remoteEntry.hidden ? "cleared" : "restored");
  }
  if (localEntry.pinned !== remoteEntry.pinned) {
    fields.push(remoteEntry.pinned ? "pinned" : "unpinned");
  }
  if (!isSameComparisonSelection(localEntry.selection, remoteEntry.selection)) {
    fields.push("selection");
  }
  return fields;
}

function formatComparisonHistorySyncConflictScoreLinkValue(
  scoreLink: ControlRoomComparisonSelectionState["scoreLink"],
) {
  if (!scoreLink) {
    return "No focus";
  }
  return `${truncateLabel(scoreLink.narrativeRunId, 18)} · ${formatComparisonScoreComponentLabel(
    scoreLink.section,
    scoreLink.componentKey,
  )}`;
}

function formatComparisonHistorySyncConflictRunSelectionValue(selectedRunIds: string[]) {
  if (!selectedRunIds.length) {
    return "No runs selected";
  }
  const sample = selectedRunIds.slice(0, 2).map((runId) => truncateLabel(runId, 18)).join(", ");
  return selectedRunIds.length > 2
    ? `${selectedRunIds.length} runs · ${sample} +${selectedRunIds.length - 2}`
    : `${selectedRunIds.length} run${selectedRunIds.length === 1 ? "" : "s"} · ${sample}`;
}

function formatComparisonHistorySyncConflictFieldValue(
  fieldKey: ComparisonHistorySyncConflictFieldKey,
  entry: ComparisonHistoryPanelEntry,
) {
  switch (fieldKey) {
    case "stepIndex":
      return `Step ${entry.stepIndex + 1}`;
    case "label":
      return entry.label;
    case "summary":
      return entry.summary;
    case "title":
      return entry.title;
    case "url":
      return entry.url;
    case "hidden":
      return entry.hidden ? "Cleared" : "Visible";
    case "pinned":
      return entry.pinned ? "Pinned" : "Not pinned";
    case "selection.intent":
      return formatComparisonIntentLabel(entry.selection.intent);
    case "selection.selectedRunIds":
      return formatComparisonHistorySyncConflictRunSelectionValue(entry.selection.selectedRunIds);
    case "selection.scoreLink":
      return formatComparisonHistorySyncConflictScoreLinkValue(entry.selection.scoreLink);
    default:
      return "n/a";
  }
}

function hasComparisonHistorySyncConflictFieldDifference(
  fieldKey: ComparisonHistorySyncConflictFieldKey,
  localEntry: ComparisonHistoryPanelEntry,
  remoteEntry: ComparisonHistoryPanelEntry,
) {
  switch (fieldKey) {
    case "stepIndex":
      return localEntry.stepIndex !== remoteEntry.stepIndex;
    case "label":
      return localEntry.label !== remoteEntry.label;
    case "summary":
      return localEntry.summary !== remoteEntry.summary;
    case "title":
      return localEntry.title !== remoteEntry.title;
    case "url":
      return localEntry.url !== remoteEntry.url;
    case "hidden":
      return localEntry.hidden !== remoteEntry.hidden;
    case "pinned":
      return localEntry.pinned !== remoteEntry.pinned;
    case "selection.intent":
      return localEntry.selection.intent !== remoteEntry.selection.intent;
    case "selection.selectedRunIds":
      return !(
        localEntry.selection.selectedRunIds.length === remoteEntry.selection.selectedRunIds.length
        && localEntry.selection.selectedRunIds.every(
          (runId, index) => runId === remoteEntry.selection.selectedRunIds[index],
        )
      );
    case "selection.scoreLink":
      return !(
        localEntry.selection.scoreLink?.narrativeRunId === remoteEntry.selection.scoreLink?.narrativeRunId
        && localEntry.selection.scoreLink?.section === remoteEntry.selection.scoreLink?.section
        && localEntry.selection.scoreLink?.componentKey === remoteEntry.selection.scoreLink?.componentKey
      );
    default:
      return false;
  }
}

function buildDefaultComparisonHistorySyncConflictSelectedSources(
  localEntry: ComparisonHistoryPanelEntry,
  remoteEntry: ComparisonHistoryPanelEntry,
) {
  return COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS.reduce<
    Partial<Record<ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource>>
  >((accumulator, definition) => {
    if (hasComparisonHistorySyncConflictFieldDifference(definition.fieldKey, localEntry, remoteEntry)) {
      accumulator[definition.fieldKey] = "remote";
    }
    return accumulator;
  }, {});
}

function buildComparisonHistorySyncConflictReview(
  localEntry: ComparisonHistoryPanelEntry,
  remoteEntry: ComparisonHistoryPanelEntry,
): ComparisonHistorySyncConflictReview {
  return {
    entryId: remoteEntry.entryId,
    entryLabel: remoteEntry.label,
    localEntry,
    remoteEntry,
    selectedSources: buildDefaultComparisonHistorySyncConflictSelectedSources(localEntry, remoteEntry),
    resolvedAt: null,
    resolutionSummary: null,
  };
}

function buildComparisonHistorySyncConflictReviewGroups(
  review: ComparisonHistorySyncConflictReview,
): ComparisonHistorySyncConflictReviewGroup[] {
  const groupedRows = new Map<string, ComparisonHistorySyncConflictReviewGroup>();
  COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS.forEach((definition) => {
    const localValue = formatComparisonHistorySyncConflictFieldValue(definition.fieldKey, review.localEntry);
    const remoteValue = formatComparisonHistorySyncConflictFieldValue(definition.fieldKey, review.remoteEntry);
    if (!hasComparisonHistorySyncConflictFieldDifference(definition.fieldKey, review.localEntry, review.remoteEntry)) {
      return;
    }
    const group = groupedRows.get(definition.groupKey) ?? {
      key: definition.groupKey,
      label: definition.groupLabel,
      rows: [],
      summaryLabel: "",
    };
    group.rows.push({
      fieldKey: definition.fieldKey,
      groupKey: definition.groupKey,
      groupLabel: definition.groupLabel,
      label: definition.label,
      localValue,
      remoteValue,
      selectedSource: review.selectedSources[definition.fieldKey] ?? "remote",
    });
    groupedRows.set(definition.groupKey, group);
  });
  return [...groupedRows.values()].map((group) => {
    const localCount = group.rows.filter((row) => row.selectedSource === "local").length;
    const remoteCount = group.rows.length - localCount;
    return {
      ...group,
      summaryLabel: `${group.rows.length} field${group.rows.length === 1 ? "" : "s"} · ${localCount} local / ${remoteCount} remote`,
    };
  });
}

function summarizeComparisonHistoryPanelEntryConflict(
  entry: ComparisonHistoryPanelEntry,
  fields: string[],
) {
  return `${entry.label}: ${fields.join(", ")}`;
}

function formatComparisonHistorySyncConflictResolutionSummary(
  review: ComparisonHistorySyncConflictReview,
) {
  const selectedFields = Object.entries(review.selectedSources) as Array<
    [ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource]
  >;
  if (!selectedFields.length) {
    return "Kept remote values for all fields.";
  }
  const localFields = selectedFields
    .filter(([, source]) => source === "local")
    .map(([fieldKey]) =>
      COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS.find((definition) => definition.fieldKey === fieldKey)?.label
      ?? fieldKey,
    );
  const remoteFields = selectedFields
    .filter(([, source]) => source === "remote")
    .map(([fieldKey]) =>
      COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS.find((definition) => definition.fieldKey === fieldKey)?.label
      ?? fieldKey,
    );
  const parts: string[] = [];
  if (localFields.length) {
    parts.push(`Local: ${localFields.join(", ")}`);
  }
  if (remoteFields.length) {
    parts.push(`Remote: ${remoteFields.join(", ")}`);
  }
  return parts.join(" · ");
}

function resolveComparisonHistorySyncConflictReviewEntry(
  review: ComparisonHistorySyncConflictReview,
) {
  const resolvedEntry: ComparisonHistoryPanelEntry = {
    ...review.remoteEntry,
    selection: {
      ...review.remoteEntry.selection,
      selectedRunIds: [...review.remoteEntry.selection.selectedRunIds],
      scoreLink: review.remoteEntry.selection.scoreLink
        ? { ...review.remoteEntry.selection.scoreLink }
        : null,
    },
  };
  const selectedSources = review.selectedSources;
  if (selectedSources.stepIndex === "local") {
    resolvedEntry.stepIndex = review.localEntry.stepIndex;
  }
  if (selectedSources.label === "local") {
    resolvedEntry.label = review.localEntry.label;
  }
  if (selectedSources.summary === "local") {
    resolvedEntry.summary = review.localEntry.summary;
  }
  if (selectedSources.title === "local") {
    resolvedEntry.title = review.localEntry.title;
  }
  if (selectedSources.url === "local") {
    resolvedEntry.url = review.localEntry.url;
  }
  if (selectedSources.hidden === "local") {
    resolvedEntry.hidden = review.localEntry.hidden;
  }
  if (selectedSources.pinned === "local") {
    resolvedEntry.pinned = review.localEntry.pinned;
  }
  if (selectedSources["selection.intent"] === "local") {
    resolvedEntry.selection.intent = review.localEntry.selection.intent;
  }
  if (selectedSources["selection.selectedRunIds"] === "local") {
    resolvedEntry.selection.selectedRunIds = [...review.localEntry.selection.selectedRunIds];
  }
  if (selectedSources["selection.scoreLink"] === "local") {
    resolvedEntry.selection.scoreLink = review.localEntry.selection.scoreLink
      ? { ...review.localEntry.selection.scoreLink }
      : null;
  }
  return resolvedEntry;
}

function applyResolvedComparisonHistoryPanelEntry(
  current: ComparisonHistoryPanelState,
  resolvedEntry: ComparisonHistoryPanelEntry,
): ComparisonHistoryPanelState {
  const currentEntry = current.entries.find((entry) => entry.entryId === resolvedEntry.entryId) ?? null;
  const nextResolvedEntry = currentEntry
    ? {
        ...resolvedEntry,
        recordedAt: currentEntry.recordedAt,
      }
    : resolvedEntry;
  const entryExists = Boolean(currentEntry);
  const nextEntries = sortComparisonHistoryPanelEntries(
    entryExists
      ? current.entries.map((entry) => (entry.entryId === nextResolvedEntry.entryId ? nextResolvedEntry : entry))
      : [...current.entries, nextResolvedEntry],
  );
  const visibleEntries = nextEntries.filter((entry) => !entry.hidden);
  const nextActiveEntryId =
    current.activeEntryId === nextResolvedEntry.entryId && nextResolvedEntry.hidden
      ? visibleEntries[visibleEntries.length - 1]?.entryId ?? null
      : current.activeEntryId && nextEntries.some((entry) => entry.entryId === current.activeEntryId)
        ? current.activeEntryId
        : visibleEntries[visibleEntries.length - 1]?.entryId ?? null;
  return {
    entries: limitComparisonHistoryPanelEntries(nextEntries),
    activeEntryId: nextActiveEntryId,
  };
}

function summarizeComparisonHistorySyncPreferenceChanges(state: {
  localOpen: boolean;
  remoteOpen: boolean;
  localSearchQuery: string;
  remoteSearchQuery: string;
  localShowPinnedOnly: boolean;
  remoteShowPinnedOnly: boolean;
  localAuditFilter: ComparisonHistorySyncAuditFilter;
  remoteAuditFilter: ComparisonHistorySyncAuditFilter;
  localShowResolvedAuditEntries: boolean;
  remoteShowResolvedAuditEntries: boolean;
}) {
  const changes: string[] = [];
  if (state.localOpen !== state.remoteOpen) {
    changes.push(state.remoteOpen ? "opened history browser" : "closed history browser");
  }
  if (state.localSearchQuery !== state.remoteSearchQuery) {
    changes.push(
      state.remoteSearchQuery.trim()
        ? `search '${state.remoteSearchQuery.trim()}'`
        : "cleared search",
    );
  }
  if (state.localShowPinnedOnly !== state.remoteShowPinnedOnly) {
    changes.push(state.remoteShowPinnedOnly ? "enabled pinned-only" : "disabled pinned-only");
  }
  if (state.localAuditFilter !== state.remoteAuditFilter) {
    changes.push(`audit filter '${state.remoteAuditFilter}'`);
  }
  if (state.localShowResolvedAuditEntries !== state.remoteShowResolvedAuditEntries) {
    changes.push(
      state.remoteShowResolvedAuditEntries ? "showing resolved audits" : "hiding resolved audits",
    );
  }
  return changes;
}

function buildComparisonHistorySyncPreferenceState(state: {
  open: boolean;
  searchQuery: string;
  showPinnedOnly: boolean;
  auditFilter: ComparisonHistorySyncAuditFilter;
  showResolvedAuditEntries: boolean;
}): ComparisonHistorySyncPreferenceState {
  return {
    open: state.open,
    searchQuery: state.searchQuery,
    showPinnedOnly: state.showPinnedOnly,
    auditFilter: state.auditFilter,
    showResolvedAuditEntries: state.showResolvedAuditEntries,
  };
}

function formatComparisonHistorySyncPreferenceFieldValue(
  fieldKey: ComparisonHistorySyncPreferenceFieldKey,
  state: ComparisonHistorySyncPreferenceState,
) {
  switch (fieldKey) {
    case "open":
      return state.open ? "Browser open" : "Browser closed";
    case "searchQuery":
      return state.searchQuery.trim() ? `Search '${state.searchQuery.trim()}'` : "No search";
    case "showPinnedOnly":
      return state.showPinnedOnly ? "Pinned only" : "All steps";
    case "auditFilter":
      return state.auditFilter === "all" ? "All audit events" : `${state.auditFilter} only`;
    case "showResolvedAuditEntries":
      return state.showResolvedAuditEntries ? "Resolved audits shown" : "Resolved audits hidden";
    default:
      return "n/a";
  }
}

function hasComparisonHistorySyncPreferenceFieldDifference(
  fieldKey: ComparisonHistorySyncPreferenceFieldKey,
  localState: ComparisonHistorySyncPreferenceState,
  remoteState: ComparisonHistorySyncPreferenceState,
) {
  switch (fieldKey) {
    case "open":
      return localState.open !== remoteState.open;
    case "searchQuery":
      return localState.searchQuery !== remoteState.searchQuery;
    case "showPinnedOnly":
      return localState.showPinnedOnly !== remoteState.showPinnedOnly;
    case "auditFilter":
      return localState.auditFilter !== remoteState.auditFilter;
    case "showResolvedAuditEntries":
      return localState.showResolvedAuditEntries !== remoteState.showResolvedAuditEntries;
    default:
      return false;
  }
}

function buildDefaultComparisonHistorySyncPreferenceSelectedSources(
  localState: ComparisonHistorySyncPreferenceState,
  remoteState: ComparisonHistorySyncPreferenceState,
) {
  return COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS.reduce<
    Partial<Record<ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncConflictFieldSource>>
  >((accumulator, definition) => {
    if (hasComparisonHistorySyncPreferenceFieldDifference(definition.fieldKey, localState, remoteState)) {
      accumulator[definition.fieldKey] = "remote";
    }
    return accumulator;
  }, {});
}

function buildComparisonHistorySyncPreferenceReview(state: {
  localOpen: boolean;
  remoteOpen: boolean;
  localSearchQuery: string;
  remoteSearchQuery: string;
  localShowPinnedOnly: boolean;
  remoteShowPinnedOnly: boolean;
  localAuditFilter: ComparisonHistorySyncAuditFilter;
  remoteAuditFilter: ComparisonHistorySyncAuditFilter;
  localShowResolvedAuditEntries: boolean;
  remoteShowResolvedAuditEntries: boolean;
}): ComparisonHistorySyncPreferenceReview {
  const localState = buildComparisonHistorySyncPreferenceState({
    open: state.localOpen,
    searchQuery: state.localSearchQuery,
    showPinnedOnly: state.localShowPinnedOnly,
    auditFilter: state.localAuditFilter,
    showResolvedAuditEntries: state.localShowResolvedAuditEntries,
  });
  const remoteState = buildComparisonHistorySyncPreferenceState({
    open: state.remoteOpen,
    searchQuery: state.remoteSearchQuery,
    showPinnedOnly: state.remoteShowPinnedOnly,
    auditFilter: state.remoteAuditFilter,
    showResolvedAuditEntries: state.remoteShowResolvedAuditEntries,
  });
  return {
    localState,
    remoteState,
    selectedSources: buildDefaultComparisonHistorySyncPreferenceSelectedSources(localState, remoteState),
    resolvedAt: null,
    resolutionSummary: null,
  };
}

function buildComparisonHistorySyncPreferenceReviewRows(
  review: ComparisonHistorySyncPreferenceReview,
): ComparisonHistorySyncPreferenceReviewRow[] {
  return COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS.flatMap((definition) => {
    if (
      !hasComparisonHistorySyncPreferenceFieldDifference(
        definition.fieldKey,
        review.localState,
        review.remoteState,
      )
    ) {
      return [];
    }
    return [{
      fieldKey: definition.fieldKey,
      label: definition.label,
      localValue: formatComparisonHistorySyncPreferenceFieldValue(definition.fieldKey, review.localState),
      remoteValue: formatComparisonHistorySyncPreferenceFieldValue(definition.fieldKey, review.remoteState),
      selectedSource: review.selectedSources[definition.fieldKey] ?? "remote",
    }];
  });
}

function formatComparisonHistorySyncPreferenceResolutionSummary(
  review: ComparisonHistorySyncPreferenceReview,
) {
  const selectedFields = Object.entries(review.selectedSources) as Array<
    [ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncConflictFieldSource]
  >;
  if (!selectedFields.length) {
    return "Kept remote browser values for all fields.";
  }
  const localFields = selectedFields
    .filter(([, source]) => source === "local")
    .map(([fieldKey]) =>
      COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS.find(
        (definition) => definition.fieldKey === fieldKey,
      )?.label ?? fieldKey,
    );
  const remoteFields = selectedFields
    .filter(([, source]) => source === "remote")
    .map(([fieldKey]) =>
      COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS.find(
        (definition) => definition.fieldKey === fieldKey,
      )?.label ?? fieldKey,
    );
  const parts: string[] = [];
  if (localFields.length) {
    parts.push(`Local: ${localFields.join(", ")}`);
  }
  if (remoteFields.length) {
    parts.push(`Remote: ${remoteFields.join(", ")}`);
  }
  return parts.join(" · ");
}

function resolveComparisonHistorySyncPreferenceReview(
  review: ComparisonHistorySyncPreferenceReview,
): ComparisonHistorySyncPreferenceState {
  return {
    open: review.selectedSources.open === "local" ? review.localState.open : review.remoteState.open,
    searchQuery:
      review.selectedSources.searchQuery === "local"
        ? review.localState.searchQuery
        : review.remoteState.searchQuery,
    showPinnedOnly:
      review.selectedSources.showPinnedOnly === "local"
        ? review.localState.showPinnedOnly
        : review.remoteState.showPinnedOnly,
    auditFilter:
      review.selectedSources.auditFilter === "local"
        ? review.localState.auditFilter
        : review.remoteState.auditFilter,
    showResolvedAuditEntries:
      review.selectedSources.showResolvedAuditEntries === "local"
        ? review.localState.showResolvedAuditEntries
        : review.remoteState.showResolvedAuditEntries,
  };
}

function listComparisonHistoryExpandedGapRowKeys(expandedGapRows: Record<string, boolean>) {
  return Object.keys(filterExpandedGapRows(expandedGapRows)).sort();
}

function listComparisonHistoryExpandedGapRowDiffKeys(
  localExpandedGapRows: Record<string, boolean>,
  remoteExpandedGapRows: Record<string, boolean>,
) {
  const keys = new Set([
    ...listComparisonHistoryExpandedGapRowKeys(localExpandedGapRows),
    ...listComparisonHistoryExpandedGapRowKeys(remoteExpandedGapRows),
  ]);
  return [...keys].sort().filter(
    (key) => Boolean(localExpandedGapRows[key]) !== Boolean(remoteExpandedGapRows[key]),
  );
}

function buildComparisonHistoryExpandedGapRowSelectionKey(
  key: string,
): ComparisonHistorySyncWorkspaceReviewSelectionKey {
  return `expandedGapRows:${key}`;
}

function parseComparisonHistoryExpandedGapRowSelectionKey(
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
) {
  return fieldKey.startsWith("expandedGapRows:") ? fieldKey.slice("expandedGapRows:".length) : null;
}

function buildComparisonHistoryExpandedGapWindowSelectionKey(
  rowKey: string,
  windowKey: string,
): ComparisonHistorySyncWorkspaceReviewSelectionKey {
  return `expandedGapWindows|${encodeURIComponent(rowKey)}|${encodeURIComponent(windowKey)}`;
}

function parseComparisonHistoryExpandedGapWindowSelectionKey(
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
) {
  if (!fieldKey.startsWith("expandedGapWindows|")) {
    return null;
  }
  const [, encodedRowKey = "", encodedWindowKey = ""] = fieldKey.split("|");
  return {
    rowKey: decodeURIComponent(encodedRowKey),
    windowKey: decodeURIComponent(encodedWindowKey),
  };
}

function listComparisonHistoryExpandedGapWindowDiffKeys(
  localExpandedGapWindowSelections: ExpandedGapWindowSelections,
  remoteExpandedGapWindowSelections: ExpandedGapWindowSelections,
  rowKey: string,
) {
  const keys = new Set([
    ...(localExpandedGapWindowSelections[rowKey] ?? []),
    ...(remoteExpandedGapWindowSelections[rowKey] ?? []),
  ]);
  return [...keys].sort().filter(
    (windowKey) =>
      (localExpandedGapWindowSelections[rowKey] ?? []).includes(windowKey)
      !== (remoteExpandedGapWindowSelections[rowKey] ?? []).includes(windowKey),
  );
}

function isSameComparisonHistoryExpandedGapRows(
  left: Record<string, boolean>,
  right: Record<string, boolean>,
) {
  const leftKeys = listComparisonHistoryExpandedGapRowKeys(left);
  const rightKeys = listComparisonHistoryExpandedGapRowKeys(right);
  return (
    leftKeys.length === rightKeys.length
    && leftKeys.every((key, index) => key === rightKeys[index])
  );
}

function isSameExpandedGapWindowSelections(
  left: ExpandedGapWindowSelections,
  right: ExpandedGapWindowSelections,
) {
  const normalizedLeft = filterExpandedGapWindowSelections(left);
  const normalizedRight = filterExpandedGapWindowSelections(right);
  const leftEntries = Object.entries(normalizedLeft).sort(([leftKey], [rightKey]) =>
    leftKey.localeCompare(rightKey),
  );
  const rightEntries = Object.entries(normalizedRight).sort(([leftKey], [rightKey]) =>
    leftKey.localeCompare(rightKey),
  );
  return (
    leftEntries.length === rightEntries.length
    && leftEntries.every(([rowKey, selectedWindows], index) => {
      const [rightRowKey, rightSelectedWindows] = rightEntries[index] ?? [];
      return (
        rowKey === rightRowKey
        && selectedWindows.length === (rightSelectedWindows?.length ?? 0)
        && selectedWindows.every((windowKey, windowIndex) => windowKey === rightSelectedWindows?.[windowIndex])
      );
    })
  );
}

function formatComparisonHistoryExpandedGapRowKey(key: string) {
  const separatorIndex = key.lastIndexOf(":");
  if (separatorIndex <= 0) {
    return key;
  }
  return `${key.slice(0, separatorIndex)} / ${key.slice(separatorIndex + 1)}`;
}

function formatComparisonHistoryExpandedGapRowsValue(expandedGapRows: Record<string, boolean>) {
  const keys = listComparisonHistoryExpandedGapRowKeys(expandedGapRows);
  if (!keys.length) {
    return "No expanded gap windows";
  }
  const sample = keys
    .slice(0, 2)
    .map((key) => formatComparisonHistoryExpandedGapRowKey(key))
    .join(", ");
  return keys.length > 2
    ? `${keys.length} expanded · ${sample} +${keys.length - 2}`
    : `${keys.length} expanded · ${sample}`;
}

function formatComparisonHistoryExpandedGapRowsDiffValue(
  localExpandedGapRows: Record<string, boolean>,
  remoteExpandedGapRows: Record<string, boolean>,
) {
  const diffKeys = listComparisonHistoryExpandedGapRowDiffKeys(
    localExpandedGapRows,
    remoteExpandedGapRows,
  );
  if (!diffKeys.length) {
    return "No changed gap windows";
  }
  const sample = diffKeys
    .slice(0, 2)
    .map((key) => formatComparisonHistoryExpandedGapRowKey(key))
    .join(", ");
  return diffKeys.length > 2
    ? `${diffKeys.length} changed · ${sample} +${diffKeys.length - 2}`
    : `${diffKeys.length} changed · ${sample}`;
}

function formatComparisonHistorySyncWorkspaceSelectionKeyLabel(
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
) {
  const expandedGapWindowSelection = parseComparisonHistoryExpandedGapWindowSelectionKey(fieldKey);
  if (expandedGapWindowSelection) {
    return `Gap window · ${formatComparisonHistoryExpandedGapRowKey(expandedGapWindowSelection.rowKey)} · ${formatGapWindowKeyLabel(expandedGapWindowSelection.windowKey)}`;
  }
  const expandedGapRowKey = parseComparisonHistoryExpandedGapRowSelectionKey(fieldKey);
  if (expandedGapRowKey) {
    return `Expanded gap row · ${formatComparisonHistoryExpandedGapRowKey(expandedGapRowKey)}`;
  }
  return COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS.find(
    (definition) => definition.fieldKey === fieldKey,
  )?.label ?? fieldKey;
}

function rankComparisonHistorySyncWorkspaceSelectionKey(
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
) {
  if (fieldKey === "comparisonSelection.selectedRunIds") {
    return 500;
  }
  if (fieldKey === "comparisonSelection.scoreLink") {
    return 450;
  }
  if (fieldKey === "comparisonSelection.intent") {
    return 400;
  }
  if (fieldKey.startsWith("expandedGapRows:")) {
    return 300;
  }
  if (fieldKey === "expandedGapRows") {
    return 280;
  }
  if (fieldKey.startsWith("expandedGapWindows|")) {
    return 200;
  }
  return 100;
}

type ComparisonHistorySyncWorkspaceSemanticRanking = {
  localScore: number;
  localSignals: ComparisonHistorySyncWorkspaceSemanticSignal[];
  remoteScore: number;
  remoteSignals: ComparisonHistorySyncWorkspaceSemanticSignal[];
  recommendedSource: ComparisonHistorySyncConflictFieldSource;
  recommendationReason: string;
  recommendationStrength: number;
};

function listComparisonHistorySyncWorkspaceDiffSelectionKeys(
  localState: ComparisonHistorySyncWorkspaceState,
  remoteState: ComparisonHistorySyncWorkspaceState,
) {
  const fieldKeys: ComparisonHistorySyncWorkspaceReviewSelectionKey[] =
    COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS.flatMap((definition) => {
      if (
        definition.fieldKey === "expandedGapRows"
        || !hasComparisonHistorySyncWorkspaceFieldDifference(
          definition.fieldKey,
          localState,
          remoteState,
        )
      ) {
        return [];
      }
      return [definition.fieldKey];
    });
  const expandedGapRowKeys = listComparisonHistoryExpandedGapRowDiffKeys(
    localState.expandedGapRows,
    remoteState.expandedGapRows,
  ).map((key) => buildComparisonHistoryExpandedGapRowSelectionKey(key));
  const expandedGapWindowKeys = [...new Set([
    ...Object.keys(localState.expandedGapWindowSelections),
    ...Object.keys(remoteState.expandedGapWindowSelections),
  ])].flatMap((rowKey) =>
    listComparisonHistoryExpandedGapWindowDiffKeys(
      localState.expandedGapWindowSelections,
      remoteState.expandedGapWindowSelections,
      rowKey,
    ).map((windowKey) => buildComparisonHistoryExpandedGapWindowSelectionKey(rowKey, windowKey)),
  );
  return fieldKeys.concat(expandedGapRowKeys, expandedGapWindowKeys);
}

function resolveComparisonHistorySyncWorkspaceFieldSource(
  review: ComparisonHistorySyncWorkspaceReview,
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
): ComparisonHistorySyncConflictFieldSource {
  const expandedGapWindowSelection = parseComparisonHistoryExpandedGapWindowSelectionKey(fieldKey);
  if (expandedGapWindowSelection) {
    return (
      review.selectedSources[fieldKey]
      ?? review.selectedSources[
        buildComparisonHistoryExpandedGapRowSelectionKey(expandedGapWindowSelection.rowKey)
      ]
      ?? review.selectedSources.expandedGapRows
      ?? "remote"
    );
  }
  const expandedGapRowKey = parseComparisonHistoryExpandedGapRowSelectionKey(fieldKey);
  if (expandedGapRowKey) {
    return (
      review.selectedSources[fieldKey]
      ?? review.selectedSources.expandedGapRows
      ?? "remote"
    );
  }
  return review.selectedSources[fieldKey] ?? "remote";
}

function listComparisonHistorySyncWorkspaceConflictSelectionKeys(
  review: ComparisonHistorySyncWorkspaceReview,
) {
  return listComparisonHistorySyncWorkspaceDiffSelectionKeys(review.localState, review.remoteState);
}

function scoreComparisonHistorySyncWorkspaceCandidateSource(params: {
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey;
  source: ComparisonHistorySyncConflictFieldSource;
  auditLocalState: ComparisonHistorySyncWorkspaceState;
  effectiveLocalState: ComparisonHistorySyncWorkspaceState;
  remoteState: ComparisonHistorySyncWorkspaceState;
}) {
  const {
    fieldKey,
    source,
    auditLocalState,
    effectiveLocalState,
    remoteState,
  } = params;
  const candidateState = source === "local" ? effectiveLocalState : remoteState;
  const alternateState = source === "local" ? remoteState : effectiveLocalState;
  const signals: ComparisonHistorySyncWorkspaceSemanticSignal[] = [];
  const pushSignal = (condition: boolean, weight: number, label: string) => {
    if (condition) {
      signals.push({ label, weight });
    }
  };
  const hasLatestLocalDrift =
    source === "local"
    && hasComparisonHistorySyncWorkspaceFieldDifference(fieldKey, auditLocalState, effectiveLocalState);
  const selection = candidateState.comparisonSelection;
  const alternateSelection = alternateState.comparisonSelection;
  if (source === "remote") {
    pushSignal(true, 8, "Keeps the latest shared sync snapshot");
  }
  pushSignal(
    hasLatestLocalDrift,
    92,
    "Preserves current local drift recorded after the audit snapshot",
  );
  switch (fieldKey) {
    case "comparisonSelection.selectedRunIds":
      pushSignal(
        selection.selectedRunIds.length >= 2,
        18,
        `Keeps ${selection.selectedRunIds.length} comparison runs active`,
      );
      pushSignal(
        Boolean(selection.scoreLink),
        44,
        "Keeps the focused score component attached to the selected runs",
      );
      pushSignal(
        !selection.scoreLink && Boolean(alternateSelection.scoreLink),
        -28,
        "Drops the focused score component",
      );
      pushSignal(
        selection.selectedRunIds.length > alternateSelection.selectedRunIds.length,
        10,
        "Retains the broader comparison set",
      );
      break;
    case "comparisonSelection.scoreLink":
      pushSignal(Boolean(selection.scoreLink), 54, "Preserves an actionable score focus");
      pushSignal(
        !selection.scoreLink && Boolean(alternateSelection.scoreLink),
        -28,
        "Drops the focused score component",
      );
      pushSignal(
        Boolean(selection.scoreLink)
          && selection.selectedRunIds.includes(selection.scoreLink?.narrativeRunId ?? ""),
        24,
        "Focus stays attached to the active comparison run set",
      );
      pushSignal(
        Boolean(selection.scoreLink)
          && selection.scoreLink?.narrativeRunId !== alternateSelection.scoreLink?.narrativeRunId,
        10,
        `Keeps focus on ${truncateLabel(selection.scoreLink?.narrativeRunId ?? "", 16)}`,
      );
      break;
    case "comparisonSelection.intent":
      pushSignal(
        selection.selectedRunIds.length >= 2,
        18,
        "Keeps intent aligned with an active comparison run set",
      );
      pushSignal(Boolean(selection.scoreLink), 12, "Intent stays anchored to the active score focus");
      pushSignal(
        selection.intent !== alternateSelection.intent,
        10,
        `Keeps ${formatComparisonIntentLabel(selection.intent)} as the active compare lens`,
      );
      break;
    default: {
      const expandedGapWindowSelection = parseComparisonHistoryExpandedGapWindowSelectionKey(fieldKey);
      if (expandedGapWindowSelection) {
        const selectedWindows = candidateState.expandedGapWindowSelections[
          expandedGapWindowSelection.rowKey
        ] ?? [];
        const visible = selectedWindows.includes(expandedGapWindowSelection.windowKey);
        const parentExpanded = Boolean(candidateState.expandedGapRows[expandedGapWindowSelection.rowKey]);
        pushSignal(visible, 32, "Keeps this gap window visible");
        pushSignal(parentExpanded, 22, "Parent gap row stays expanded");
        pushSignal(visible && !parentExpanded, -26, "This gap window would sit under a collapsed row");
        pushSignal(
          visible && selectedWindows.length > 1,
          12,
          `Preserves a ${selectedWindows.length}-window inspection subset`,
        );
        break;
      }
      const expandedGapRowKey = parseComparisonHistoryExpandedGapRowSelectionKey(fieldKey);
      if (expandedGapRowKey) {
        const selectedWindows = candidateState.expandedGapWindowSelections[expandedGapRowKey] ?? [];
        const expanded = Boolean(candidateState.expandedGapRows[expandedGapRowKey]);
        pushSignal(
          expanded && selectedWindows.length > 0,
          40,
          `Keeps ${selectedWindows.length} gap window${selectedWindows.length === 1 ? "" : "s"} reachable`,
        );
        pushSignal(expanded && selectedWindows.length === 0, 14, "Keeps the gap row expanded for inspection");
        pushSignal(
          !expanded && selectedWindows.length > 0,
          -22,
          "Collapses a row that still has a visible gap subset",
        );
        pushSignal(
          selectedWindows.length > (alternateState.expandedGapWindowSelections[expandedGapRowKey]?.length ?? 0),
          10,
          "Retains the richer gap inspection subset",
        );
      }
      break;
    }
  }
  return {
    score: signals.reduce((total, signal) => total + signal.weight, 0),
    signals,
  };
}

function sortComparisonHistorySyncWorkspaceSemanticSignals(
  signals: ComparisonHistorySyncWorkspaceSemanticSignal[],
) {
  return [...signals].sort((left, right) => (
    Math.abs(right.weight) - Math.abs(left.weight)
    || right.weight - left.weight
    || left.label.localeCompare(right.label)
  ));
}

function rankComparisonHistorySyncWorkspaceFieldSemantics(params: {
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey;
  auditLocalState: ComparisonHistorySyncWorkspaceState;
  effectiveLocalState: ComparisonHistorySyncWorkspaceState;
  remoteState: ComparisonHistorySyncWorkspaceState;
}): ComparisonHistorySyncWorkspaceSemanticRanking {
  const local = scoreComparisonHistorySyncWorkspaceCandidateSource({
    ...params,
    source: "local",
  });
  const remote = scoreComparisonHistorySyncWorkspaceCandidateSource({
    ...params,
    source: "remote",
  });
  const recommendedSource = local.score > remote.score ? "local" : "remote";
  const recommendedSignals = (recommendedSource === "local" ? local : remote).signals
    .filter((signal) => signal.weight > 0)
    .sort((left, right) => right.weight - left.weight);
  const recommendationReason = recommendedSignals.length
    ? recommendedSignals.slice(0, 2).map((signal) => signal.label).join(" · ")
    : recommendedSource === "local"
      ? "Keeps the current local workspace branch"
      : "Keeps the latest shared sync snapshot";
  return {
    localScore: local.score,
    localSignals: sortComparisonHistorySyncWorkspaceSemanticSignals(local.signals),
    remoteScore: remote.score,
    remoteSignals: sortComparisonHistorySyncWorkspaceSemanticSignals(remote.signals),
    recommendedSource,
    recommendationReason,
    recommendationStrength: Math.abs(local.score - remote.score),
  };
}

function buildComparisonHistorySyncWorkspaceRecommendedSources(
  localState: ComparisonHistorySyncWorkspaceState,
  remoteState: ComparisonHistorySyncWorkspaceState,
  latestLocalState?: ComparisonHistorySyncWorkspaceState,
) {
  const effectiveLocalState = latestLocalState ?? localState;
  return listComparisonHistorySyncWorkspaceDiffSelectionKeys(localState, remoteState).reduce<
    Partial<Record<ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncConflictFieldSource>>
  >((accumulator, fieldKey) => {
    accumulator[fieldKey] = rankComparisonHistorySyncWorkspaceFieldSemantics({
      fieldKey,
      auditLocalState: localState,
      effectiveLocalState,
      remoteState,
    }).recommendedSource;
    return accumulator;
  }, {});
}

function summarizeComparisonHistorySyncWorkspaceChanges(state: {
  localComparisonSelection: ControlRoomComparisonSelectionState;
  remoteComparisonSelection: ControlRoomComparisonSelectionState;
  localExpandedGapRows: Record<string, boolean>;
  remoteExpandedGapRows: Record<string, boolean>;
  localExpandedGapWindowSelections: ExpandedGapWindowSelections;
  remoteExpandedGapWindowSelections: ExpandedGapWindowSelections;
}) {
  const changes: string[] = [];
  if (state.localComparisonSelection.intent !== state.remoteComparisonSelection.intent) {
    changes.push(`intent ${formatComparisonIntentLabel(state.remoteComparisonSelection.intent)}`);
  }
  if (
    state.localComparisonSelection.selectedRunIds.length
      !== state.remoteComparisonSelection.selectedRunIds.length
    || state.localComparisonSelection.selectedRunIds.some(
      (runId, index) => runId !== state.remoteComparisonSelection.selectedRunIds[index],
    )
  ) {
    changes.push(
      `selection ${formatComparisonHistorySyncConflictRunSelectionValue(
        state.remoteComparisonSelection.selectedRunIds,
      )}`,
    );
  }
  if (
    state.localComparisonSelection.scoreLink?.narrativeRunId
      !== state.remoteComparisonSelection.scoreLink?.narrativeRunId
    || state.localComparisonSelection.scoreLink?.section
      !== state.remoteComparisonSelection.scoreLink?.section
    || state.localComparisonSelection.scoreLink?.componentKey
      !== state.remoteComparisonSelection.scoreLink?.componentKey
  ) {
    changes.push(
      `focus ${formatComparisonHistorySyncConflictScoreLinkValue(
        state.remoteComparisonSelection.scoreLink,
      )}`,
    );
  }
  if (!isSameComparisonHistoryExpandedGapRows(state.localExpandedGapRows, state.remoteExpandedGapRows)) {
    changes.push(
      `gap rows ${formatComparisonHistoryExpandedGapRowsDiffValue(
        state.localExpandedGapRows,
        state.remoteExpandedGapRows,
      )}`,
    );
  }
  const changedGapWindowCount = Object.keys(filterExpandedGapWindowSelections(state.localExpandedGapWindowSelections))
    .reduce((total, rowKey) => {
      const localSelectedWindows = state.localExpandedGapWindowSelections[rowKey] ?? [];
      const remoteSelectedWindows = state.remoteExpandedGapWindowSelections[rowKey] ?? [];
      const changedWindows = new Set([...localSelectedWindows, ...remoteSelectedWindows]);
      return total + [...changedWindows].filter(
        (windowKey) => localSelectedWindows.includes(windowKey) !== remoteSelectedWindows.includes(windowKey),
      ).length;
    }, 0)
    + Object.keys(filterExpandedGapWindowSelections(state.remoteExpandedGapWindowSelections))
      .filter((rowKey) => !(rowKey in state.localExpandedGapWindowSelections))
      .reduce(
        (total, rowKey) => total + (state.remoteExpandedGapWindowSelections[rowKey]?.length ?? 0),
        0,
      );
  if (changedGapWindowCount > 0) {
    changes.push(`${changedGapWindowCount} gap-window selections changed`);
  }
  return changes;
}

function buildComparisonHistorySyncWorkspaceState(state: {
  comparisonSelection: ControlRoomComparisonSelectionState;
  expandedGapRows: Record<string, boolean>;
  expandedGapWindowSelections: ExpandedGapWindowSelections;
}): ComparisonHistorySyncWorkspaceState {
  return {
    comparisonSelection: normalizeControlRoomComparisonSelection(state.comparisonSelection),
    expandedGapRows: filterExpandedGapRows(state.expandedGapRows),
    expandedGapWindowSelections: filterExpandedGapWindowSelections(state.expandedGapWindowSelections),
  };
}

function formatComparisonHistorySyncWorkspaceFieldValue(
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
  state: ComparisonHistorySyncWorkspaceState,
) {
  const expandedGapWindowSelection = parseComparisonHistoryExpandedGapWindowSelectionKey(fieldKey);
  if (expandedGapWindowSelection) {
    return (state.expandedGapWindowSelections[expandedGapWindowSelection.rowKey] ?? []).includes(
      expandedGapWindowSelection.windowKey,
    )
      ? "Visible"
      : "Hidden";
  }
  const expandedGapRowKey = parseComparisonHistoryExpandedGapRowSelectionKey(fieldKey);
  if (expandedGapRowKey) {
    return state.expandedGapRows[expandedGapRowKey] ? "Expanded" : "Collapsed";
  }
  switch (fieldKey) {
    case "comparisonSelection.intent":
      return formatComparisonIntentLabel(state.comparisonSelection.intent);
    case "comparisonSelection.selectedRunIds":
      return formatComparisonHistorySyncConflictRunSelectionValue(state.comparisonSelection.selectedRunIds);
    case "comparisonSelection.scoreLink":
      return formatComparisonHistorySyncConflictScoreLinkValue(state.comparisonSelection.scoreLink);
    case "expandedGapRows":
      return formatComparisonHistoryExpandedGapRowsValue(state.expandedGapRows);
    default:
      return "n/a";
  }
}

function hasComparisonHistorySyncWorkspaceFieldDifference(
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
  localState: ComparisonHistorySyncWorkspaceState,
  remoteState: ComparisonHistorySyncWorkspaceState,
) {
  const expandedGapWindowSelection = parseComparisonHistoryExpandedGapWindowSelectionKey(fieldKey);
  if (expandedGapWindowSelection) {
    return (localState.expandedGapWindowSelections[expandedGapWindowSelection.rowKey] ?? []).includes(
      expandedGapWindowSelection.windowKey,
    )
      !== (remoteState.expandedGapWindowSelections[expandedGapWindowSelection.rowKey] ?? []).includes(
        expandedGapWindowSelection.windowKey,
      );
  }
  const expandedGapRowKey = parseComparisonHistoryExpandedGapRowSelectionKey(fieldKey);
  if (expandedGapRowKey) {
    return Boolean(localState.expandedGapRows[expandedGapRowKey])
      !== Boolean(remoteState.expandedGapRows[expandedGapRowKey]);
  }
  switch (fieldKey) {
    case "comparisonSelection.intent":
      return localState.comparisonSelection.intent !== remoteState.comparisonSelection.intent;
    case "comparisonSelection.selectedRunIds":
      return !(
        localState.comparisonSelection.selectedRunIds.length
          === remoteState.comparisonSelection.selectedRunIds.length
        && localState.comparisonSelection.selectedRunIds.every(
          (runId, index) => runId === remoteState.comparisonSelection.selectedRunIds[index],
        )
      );
    case "comparisonSelection.scoreLink":
      return !(
        localState.comparisonSelection.scoreLink?.narrativeRunId
          === remoteState.comparisonSelection.scoreLink?.narrativeRunId
        && localState.comparisonSelection.scoreLink?.section
          === remoteState.comparisonSelection.scoreLink?.section
        && localState.comparisonSelection.scoreLink?.componentKey
          === remoteState.comparisonSelection.scoreLink?.componentKey
      );
    case "expandedGapRows":
      return !isSameComparisonHistoryExpandedGapRows(
        localState.expandedGapRows,
        remoteState.expandedGapRows,
      );
    default:
      return false;
  }
}

function buildDefaultComparisonHistorySyncWorkspaceSelectedSources(
  localState: ComparisonHistorySyncWorkspaceState,
  remoteState: ComparisonHistorySyncWorkspaceState,
) {
  return buildComparisonHistorySyncWorkspaceRecommendedSources(localState, remoteState);
}

function buildComparisonHistorySyncWorkspaceReview(state: {
  localComparisonSelection: ControlRoomComparisonSelectionState;
  remoteComparisonSelection: ControlRoomComparisonSelectionState;
  localExpandedGapRows: Record<string, boolean>;
  remoteExpandedGapRows: Record<string, boolean>;
  localExpandedGapWindowSelections: ExpandedGapWindowSelections;
  remoteExpandedGapWindowSelections: ExpandedGapWindowSelections;
}): ComparisonHistorySyncWorkspaceReview {
  const localState = buildComparisonHistorySyncWorkspaceState({
    comparisonSelection: state.localComparisonSelection,
    expandedGapRows: state.localExpandedGapRows,
    expandedGapWindowSelections: state.localExpandedGapWindowSelections,
  });
  const remoteState = buildComparisonHistorySyncWorkspaceState({
    comparisonSelection: state.remoteComparisonSelection,
    expandedGapRows: state.remoteExpandedGapRows,
    expandedGapWindowSelections: state.remoteExpandedGapWindowSelections,
  });
  return {
    localState,
    remoteState,
    selectedSources: buildDefaultComparisonHistorySyncWorkspaceSelectedSources(localState, remoteState),
    resolvedAt: null,
    resolutionSummary: null,
  };
}

function buildComparisonHistorySyncWorkspaceReviewRows(
  review: ComparisonHistorySyncWorkspaceReview,
  latestLocalState?: ComparisonHistorySyncWorkspaceState,
): ComparisonHistorySyncWorkspaceReviewRow[] {
  const effectiveLocalState = latestLocalState ?? review.localState;
  const rows: ComparisonHistorySyncWorkspaceReviewRow[] = [];
  const pushWorkspaceRow = (
    fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
    label: string,
  ) => {
    const localSnapshotValue = formatComparisonHistorySyncWorkspaceFieldValue(fieldKey, review.localState);
    const localValue = formatComparisonHistorySyncWorkspaceFieldValue(fieldKey, effectiveLocalState);
    const hasLatestLocalDrift =
      Boolean(latestLocalState)
      && hasComparisonHistorySyncWorkspaceFieldDifference(fieldKey, review.localState, effectiveLocalState);
    const semanticRanking = rankComparisonHistorySyncWorkspaceFieldSemantics({
      fieldKey,
      auditLocalState: review.localState,
      effectiveLocalState,
      remoteState: review.remoteState,
    });
    rows.push({
      fieldKey,
      hasLatestLocalDrift,
      label,
      localHint: hasLatestLocalDrift ? `Audit snapshot: ${localSnapshotValue}` : null,
      localScore: semanticRanking.localScore,
      localSignals: semanticRanking.localSignals,
      localValue,
      remoteScore: semanticRanking.remoteScore,
      remoteSignals: semanticRanking.remoteSignals,
      remoteValue: formatComparisonHistorySyncWorkspaceFieldValue(fieldKey, review.remoteState),
      recommendedSource: semanticRanking.recommendedSource,
      recommendationReason: semanticRanking.recommendationReason,
      recommendationStrength: semanticRanking.recommendationStrength,
      semanticRank: rankComparisonHistorySyncWorkspaceSelectionKey(fieldKey)
        + semanticRanking.recommendationStrength,
      selectedSource: resolveComparisonHistorySyncWorkspaceFieldSource(review, fieldKey),
    });
  };
  COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS.forEach((definition) => {
    if (
      definition.fieldKey === "expandedGapRows"
      || !hasComparisonHistorySyncWorkspaceFieldDifference(
        definition.fieldKey,
        review.localState,
        review.remoteState,
      )
    ) {
      return;
    }
    pushWorkspaceRow(definition.fieldKey, definition.label);
  });
  listComparisonHistoryExpandedGapRowDiffKeys(
    review.localState.expandedGapRows,
    review.remoteState.expandedGapRows,
  ).forEach((key) => {
    const fieldKey = buildComparisonHistoryExpandedGapRowSelectionKey(key);
    pushWorkspaceRow(fieldKey, formatComparisonHistorySyncWorkspaceSelectionKeyLabel(fieldKey));
  });
  [...new Set([
    ...Object.keys(review.localState.expandedGapWindowSelections),
    ...Object.keys(review.remoteState.expandedGapWindowSelections),
  ])].forEach((rowKey) => {
    listComparisonHistoryExpandedGapWindowDiffKeys(
      review.localState.expandedGapWindowSelections,
      review.remoteState.expandedGapWindowSelections,
      rowKey,
    ).forEach((windowKey) => {
      const fieldKey = buildComparisonHistoryExpandedGapWindowSelectionKey(rowKey, windowKey);
      pushWorkspaceRow(fieldKey, formatComparisonHistorySyncWorkspaceSelectionKeyLabel(fieldKey));
    });
  });
  return rows.sort((left, right) => (
    Number(right.hasLatestLocalDrift) - Number(left.hasLatestLocalDrift)
    || right.recommendationStrength - left.recommendationStrength
    || right.semanticRank - left.semanticRank
    || left.label.localeCompare(right.label)
  ));
}

function buildComparisonHistorySyncWorkspaceRecommendationOverview(
  rows: ComparisonHistorySyncWorkspaceReviewRow[],
): ComparisonHistorySyncWorkspaceRecommendationOverview {
  const rankedRows = [...rows].sort((left, right) => (
    right.recommendationStrength - left.recommendationStrength
    || Number(right.hasLatestLocalDrift) - Number(left.hasLatestLocalDrift)
    || right.semanticRank - left.semanticRank
    || left.label.localeCompare(right.label)
  ));
  const topLocal = rankedRows
    .filter((row) => row.recommendedSource === "local")
    .slice(0, 2);
  const topRemote = rankedRows
    .filter((row) => row.recommendedSource === "remote")
    .slice(0, 2);
  return {
    totalFieldCount: rows.length,
    localCount: rows.filter((row) => row.recommendedSource === "local").length,
    remoteCount: rows.filter((row) => row.recommendedSource === "remote").length,
    latestLocalDriftCount: rows.filter((row) => row.hasLatestLocalDrift).length,
    rankedDiffCount: rows.filter((row) => row.selectedSource !== row.recommendedSource).length,
    strongest: rankedRows[0] ?? null,
    topLocal,
    topRemote,
  };
}

function formatComparisonHistorySyncWorkspaceResolutionSummary(
  review: ComparisonHistorySyncWorkspaceReview,
  latestLocalState?: ComparisonHistorySyncWorkspaceState,
) {
  const selectedFields = Object.entries(review.selectedSources) as Array<
    [ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncConflictFieldSource]
  >;
  const localFields = selectedFields
    .filter(([, source]) => source === "local")
    .map(([fieldKey]) => formatComparisonHistorySyncWorkspaceSelectionKeyLabel(fieldKey));
  const remoteFields = selectedFields
    .filter(([, source]) => source === "remote")
    .map(([fieldKey]) => formatComparisonHistorySyncWorkspaceSelectionKeyLabel(fieldKey));
  const parts: string[] = [];
  if (!selectedFields.length) {
    parts.push("Kept remote workspace values for all fields.");
  }
  if (localFields.length) {
    parts.push(`Local: ${localFields.join(", ")}`);
  }
  if (remoteFields.length) {
    parts.push(`Remote: ${remoteFields.join(", ")}`);
  }
  if (latestLocalState) {
    const latestLocalDriftCount = listComparisonHistorySyncWorkspaceConflictSelectionKeys(review)
      .filter((fieldKey) =>
        resolveComparisonHistorySyncWorkspaceFieldSource(review, fieldKey) === "local"
        && hasComparisonHistorySyncWorkspaceFieldDifference(fieldKey, review.localState, latestLocalState),
      ).length;
    if (latestLocalDriftCount > 0) {
      parts.push(
        `Latest local drift kept for ${latestLocalDriftCount} field${latestLocalDriftCount === 1 ? "" : "s"}`,
      );
    }
    parts.push("3-way merge keeps current local workspace outside remote-selected fields");
  }
  return parts.join(" · ");
}

function resolveComparisonHistorySyncWorkspaceReview(
  review: ComparisonHistorySyncWorkspaceReview,
  latestLocalState?: ComparisonHistorySyncWorkspaceState,
): ComparisonHistorySyncWorkspaceState {
  const effectiveLocalState = latestLocalState ?? review.localState;
  const resolvedSelection = normalizeControlRoomComparisonSelection(effectiveLocalState.comparisonSelection);
  if (resolveComparisonHistorySyncWorkspaceFieldSource(review, "comparisonSelection.intent") === "remote") {
    resolvedSelection.intent = review.remoteState.comparisonSelection.intent;
  }
  if (
    resolveComparisonHistorySyncWorkspaceFieldSource(review, "comparisonSelection.selectedRunIds")
    === "remote"
  ) {
    resolvedSelection.selectedRunIds = [...review.remoteState.comparisonSelection.selectedRunIds];
  }
  if (resolveComparisonHistorySyncWorkspaceFieldSource(review, "comparisonSelection.scoreLink") === "remote") {
    resolvedSelection.scoreLink = review.remoteState.comparisonSelection.scoreLink
      ? { ...review.remoteState.comparisonSelection.scoreLink }
      : null;
  }
  const auditLocalExpandedGapRows = filterExpandedGapRows(review.localState.expandedGapRows);
  const localExpandedGapRows = filterExpandedGapRows(effectiveLocalState.expandedGapRows);
  const remoteExpandedGapRows = filterExpandedGapRows(review.remoteState.expandedGapRows);
  const auditLocalExpandedGapWindowSelections = filterExpandedGapWindowSelections(
    review.localState.expandedGapWindowSelections,
  );
  const localExpandedGapWindowSelections = filterExpandedGapWindowSelections(
    effectiveLocalState.expandedGapWindowSelections,
  );
  const remoteExpandedGapWindowSelections = filterExpandedGapWindowSelections(
    review.remoteState.expandedGapWindowSelections,
  );
  const resolvedExpandedGapRows = { ...localExpandedGapRows };
  const resolvedExpandedGapWindowSelections = { ...localExpandedGapWindowSelections };
  listComparisonHistoryExpandedGapRowDiffKeys(
    auditLocalExpandedGapRows,
    remoteExpandedGapRows,
  ).forEach((key) => {
    const fieldKey = buildComparisonHistoryExpandedGapRowSelectionKey(key);
    if (resolveComparisonHistorySyncWorkspaceFieldSource(review, fieldKey) !== "remote") {
      return;
    }
    if (remoteExpandedGapRows[key]) {
      resolvedExpandedGapRows[key] = true;
      return;
    }
    delete resolvedExpandedGapRows[key];
  });
  new Set([
    ...Object.keys(auditLocalExpandedGapWindowSelections),
    ...Object.keys(remoteExpandedGapWindowSelections),
  ]).forEach((rowKey) => {
    listComparisonHistoryExpandedGapWindowDiffKeys(
      auditLocalExpandedGapWindowSelections,
      remoteExpandedGapWindowSelections,
      rowKey,
    ).forEach((windowKey) => {
      const fieldKey = buildComparisonHistoryExpandedGapWindowSelectionKey(rowKey, windowKey);
      if (resolveComparisonHistorySyncWorkspaceFieldSource(review, fieldKey) !== "remote") {
        return;
      }
      const nextSelections = new Set(resolvedExpandedGapWindowSelections[rowKey] ?? []);
      if ((remoteExpandedGapWindowSelections[rowKey] ?? []).includes(windowKey)) {
        nextSelections.add(windowKey);
      } else {
        nextSelections.delete(windowKey);
      }
      if (nextSelections.size) {
        resolvedExpandedGapWindowSelections[rowKey] = [...nextSelections].sort();
        return;
      }
      delete resolvedExpandedGapWindowSelections[rowKey];
    });
    if (!resolvedExpandedGapWindowSelections[rowKey]?.length) {
      delete resolvedExpandedGapWindowSelections[rowKey];
    }
  });
  return {
    comparisonSelection: normalizeControlRoomComparisonSelection(resolvedSelection),
    expandedGapRows: resolvedExpandedGapRows,
    expandedGapWindowSelections: resolvedExpandedGapWindowSelections,
  };
}

function buildComparisonHistorySyncAuditEntries(state: {
  localPanel: ComparisonHistoryPanelState;
  remotePanel: ComparisonHistoryPanelState;
  localComparisonSelection: ControlRoomComparisonSelectionState;
  remoteComparisonSelection: ControlRoomComparisonSelectionState;
  localExpandedGapRows: Record<string, boolean>;
  remoteExpandedGapRows: Record<string, boolean>;
  localExpandedGapWindowSelections: ExpandedGapWindowSelections;
  remoteExpandedGapWindowSelections: ExpandedGapWindowSelections;
  localOpen: boolean;
  remoteOpen: boolean;
  localSearchQuery: string;
  remoteSearchQuery: string;
  localShowPinnedOnly: boolean;
  remoteShowPinnedOnly: boolean;
  localAuditFilter: ComparisonHistorySyncAuditFilter;
  remoteAuditFilter: ComparisonHistorySyncAuditFilter;
  localShowResolvedAuditEntries: boolean;
  remoteShowResolvedAuditEntries: boolean;
  remoteSync: ComparisonHistoryPanelSyncState | null;
}): ComparisonHistorySyncAuditEntry[] {
  const sourceTabId = state.remoteSync?.tabId ?? "unknown";
  const sourceTabLabel = state.remoteSync?.tabLabel ?? "Remote tab";
  const recordedAt = new Date().toISOString();
  const localEntriesById = new Map(
    state.localPanel.entries.map((entry) => [entry.entryId, entry]),
  );
  const remoteAdditions = state.remotePanel.entries.filter(
    (entry) => !entry.hidden && !localEntriesById.has(entry.entryId),
  );
  const conflictingEntries = state.remotePanel.entries.flatMap((remoteEntry) => {
    const localEntry = localEntriesById.get(remoteEntry.entryId);
    if (!localEntry) {
      return [];
    }
    const fields = getComparisonHistoryPanelEntryChangedFields(localEntry, remoteEntry);
    return fields.length ? [{ localEntry, remoteEntry, fields }] : [];
  });
  const preferenceChanges = summarizeComparisonHistorySyncPreferenceChanges({
    localOpen: state.localOpen,
    remoteOpen: state.remoteOpen,
    localSearchQuery: state.localSearchQuery,
    remoteSearchQuery: state.remoteSearchQuery,
    localShowPinnedOnly: state.localShowPinnedOnly,
    remoteShowPinnedOnly: state.remoteShowPinnedOnly,
    localAuditFilter: state.localAuditFilter,
    remoteAuditFilter: state.remoteAuditFilter,
    localShowResolvedAuditEntries: state.localShowResolvedAuditEntries,
    remoteShowResolvedAuditEntries: state.remoteShowResolvedAuditEntries,
  });
  const workspaceChanges = summarizeComparisonHistorySyncWorkspaceChanges({
    localComparisonSelection: state.localComparisonSelection,
    remoteComparisonSelection: state.remoteComparisonSelection,
    localExpandedGapRows: state.localExpandedGapRows,
    remoteExpandedGapRows: state.remoteExpandedGapRows,
    localExpandedGapWindowSelections: state.localExpandedGapWindowSelections,
    remoteExpandedGapWindowSelections: state.remoteExpandedGapWindowSelections,
  });
  const nextEntries: ComparisonHistorySyncAuditEntry[] = [];
  if (remoteAdditions.length) {
    const labels = remoteAdditions
      .slice(0, 2)
      .map((entry) => entry.label)
      .join(" · ");
    const remainderCount = Math.max(remoteAdditions.length - 2, 0);
    nextEntries.push({
      auditId: buildComparisonHistorySyncAuditId(),
      kind: "merge",
      summary: `Merged ${remoteAdditions.length} step${remoteAdditions.length === 1 ? "" : "s"} from ${sourceTabLabel}`,
      detail: remainderCount > 0 ? `${labels} +${remainderCount} more` : labels,
      recordedAt,
      sourceTabId,
      sourceTabLabel,
    });
  }
  conflictingEntries.forEach(({ localEntry, remoteEntry, fields }) => {
    nextEntries.push({
      auditId: buildComparisonHistorySyncAuditId(),
      kind: "conflict",
      summary: `Review conflict on ${remoteEntry.label}`,
      detail: summarizeComparisonHistoryPanelEntryConflict(remoteEntry, fields),
      recordedAt,
      sourceTabId,
      sourceTabLabel,
      conflictReview: buildComparisonHistorySyncConflictReview(localEntry, remoteEntry),
    });
  });
  if (workspaceChanges.length) {
    nextEntries.push({
      auditId: buildComparisonHistorySyncAuditId(),
      kind: "workspace",
      summary: `Review workspace state from ${sourceTabLabel}`,
      detail: workspaceChanges.join(" · "),
      recordedAt,
      sourceTabId,
      sourceTabLabel,
      workspaceReview: buildComparisonHistorySyncWorkspaceReview({
        localComparisonSelection: state.localComparisonSelection,
        remoteComparisonSelection: state.remoteComparisonSelection,
        localExpandedGapRows: state.localExpandedGapRows,
        remoteExpandedGapRows: state.remoteExpandedGapRows,
        localExpandedGapWindowSelections: state.localExpandedGapWindowSelections,
        remoteExpandedGapWindowSelections: state.remoteExpandedGapWindowSelections,
      }),
    });
  }
  if (preferenceChanges.length) {
    nextEntries.push({
      auditId: buildComparisonHistorySyncAuditId(),
      kind: "preferences",
      summary: `Review browser state from ${sourceTabLabel}`,
      detail: preferenceChanges.join(" · "),
      recordedAt,
      sourceTabId,
      sourceTabLabel,
      preferenceReview: buildComparisonHistorySyncPreferenceReview({
        localOpen: state.localOpen,
        remoteOpen: state.remoteOpen,
        localSearchQuery: state.localSearchQuery,
        remoteSearchQuery: state.remoteSearchQuery,
        localShowPinnedOnly: state.localShowPinnedOnly,
        remoteShowPinnedOnly: state.remoteShowPinnedOnly,
        localAuditFilter: state.localAuditFilter,
        remoteAuditFilter: state.remoteAuditFilter,
        localShowResolvedAuditEntries: state.localShowResolvedAuditEntries,
        remoteShowResolvedAuditEntries: state.remoteShowResolvedAuditEntries,
      }),
    });
  }
  return nextEntries;
}

function loadLegacyExpandedGapRows() {
  if (typeof window === "undefined") {
    return {};
  }
  try {
    const raw = window.localStorage.getItem(LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return {};
    }
    return filterExpandedGapRows(parsed);
  } catch {
    return {};
  }
}

function filterExpandedGapRows(value: unknown) {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value).filter((entry): entry is [string, boolean] => entry[1] === true),
  );
}

function normalizeControlRoomComparisonSelection(
  value: Partial<ControlRoomComparisonSelectionState> | null | undefined,
): ControlRoomComparisonSelectionState {
  const selectedRunIds = normalizeComparisonRunIdList(value?.selectedRunIds);
  const scoreLink = normalizeComparisonScoreLinkTarget(value?.scoreLink);
  return {
    intent: normalizeComparisonIntent(value?.intent),
    selectedRunIds,
    scoreLink:
      scoreLink && selectedRunIds.includes(scoreLink.narrativeRunId)
        ? {
            ...scoreLink,
            detailExpanded: scoreLink.detailExpanded,
            artifactDetailExpanded: scoreLink.artifactDetailExpanded,
            artifactLineDetailExpanded: scoreLink.artifactLineDetailExpanded,
            artifactLineDetailView: scoreLink.artifactLineDetailView,
            artifactLineMicroView: scoreLink.artifactLineMicroView,
            artifactLineNotePage: scoreLink.artifactLineNotePage,
            artifactLineDetailHoverKey: scoreLink.artifactLineDetailHoverKey,
            artifactLineDetailScrubStep: scoreLink.artifactLineDetailScrubStep,
            originRunId:
              scoreLink.originRunId && selectedRunIds.includes(scoreLink.originRunId)
                ? scoreLink.originRunId
                : null,
            subFocusKey: scoreLink.subFocusKey,
            tooltipKey: scoreLink.tooltipKey,
            artifactHoverKey: scoreLink.artifactHoverKey,
          }
        : null,
  };
}

function isSameComparisonSelection(
  left: Partial<ControlRoomComparisonSelectionState> | null | undefined,
  right: Partial<ControlRoomComparisonSelectionState> | null | undefined,
) {
  const normalizedLeft = normalizeControlRoomComparisonSelection(left);
  const normalizedRight = normalizeControlRoomComparisonSelection(right);
  return (
    normalizedLeft.intent === normalizedRight.intent
    && normalizedLeft.selectedRunIds.length === normalizedRight.selectedRunIds.length
    && normalizedLeft.selectedRunIds.every((runId, index) => runId === normalizedRight.selectedRunIds[index])
    && (
      (normalizedLeft.scoreLink === null && normalizedRight.scoreLink === null)
      || (
        normalizedLeft.scoreLink !== null
        && normalizedRight.scoreLink !== null
        && normalizedLeft.scoreLink.narrativeRunId === normalizedRight.scoreLink.narrativeRunId
        && normalizedLeft.scoreLink.section === normalizedRight.scoreLink.section
        && normalizedLeft.scoreLink.componentKey === normalizedRight.scoreLink.componentKey
        && normalizedLeft.scoreLink.source === normalizedRight.scoreLink.source
        && normalizedLeft.scoreLink.originRunId === normalizedRight.scoreLink.originRunId
        && normalizedLeft.scoreLink.subFocusKey === normalizedRight.scoreLink.subFocusKey
        && normalizedLeft.scoreLink.detailExpanded === normalizedRight.scoreLink.detailExpanded
        && normalizedLeft.scoreLink.artifactDetailExpanded === normalizedRight.scoreLink.artifactDetailExpanded
        && normalizedLeft.scoreLink.artifactLineDetailExpanded === normalizedRight.scoreLink.artifactLineDetailExpanded
        && normalizedLeft.scoreLink.artifactLineDetailView === normalizedRight.scoreLink.artifactLineDetailView
        && normalizedLeft.scoreLink.artifactLineMicroView === normalizedRight.scoreLink.artifactLineMicroView
        && normalizedLeft.scoreLink.artifactLineNotePage === normalizedRight.scoreLink.artifactLineNotePage
        && normalizedLeft.scoreLink.artifactLineDetailHoverKey === normalizedRight.scoreLink.artifactLineDetailHoverKey
        && normalizedLeft.scoreLink.artifactLineDetailScrubStep === normalizedRight.scoreLink.artifactLineDetailScrubStep
        && normalizedLeft.scoreLink.tooltipKey === normalizedRight.scoreLink.tooltipKey
        && normalizedLeft.scoreLink.artifactHoverKey === normalizedRight.scoreLink.artifactHoverKey
      )
    )
  );
}

function formatComparisonHistoryPanelEntryMeta(entry: ComparisonHistoryPanelEntry) {
  const parts = [
    formatComparisonIntentLabel(entry.selection.intent),
    `${entry.selection.selectedRunIds.length} run${entry.selection.selectedRunIds.length === 1 ? "" : "s"}`,
    `Saved ${formatTimestamp(entry.recordedAt)}`,
  ];
  if (entry.selection.scoreLink) {
    parts.push(
      formatComparisonScoreComponentLabel(
        entry.selection.scoreLink.section,
        entry.selection.scoreLink.componentKey,
      ),
    );
    parts.push(formatComparisonScoreLinkSourceLabel(entry.selection.scoreLink.source));
    const subFocusLabel = formatComparisonScoreLinkSubFocusLabel(entry.selection.scoreLink.subFocusKey);
    if (subFocusLabel) {
      parts.push(subFocusLabel);
    }
    const tooltipLabel = formatComparisonScoreLinkTooltipLabel(entry.selection.scoreLink.tooltipKey);
    if (tooltipLabel) {
      parts.push(tooltipLabel);
    }
    const artifactHoverLabel = formatComparisonScoreLinkArtifactHoverLabel(
      entry.selection.scoreLink.artifactHoverKey,
    );
    const artifactLineViewLabel = formatComparisonScoreLinkArtifactLineDetailViewLabel(
      entry.selection.scoreLink.artifactLineDetailView,
    );
    const artifactLineMicroViewLabel = formatComparisonScoreLinkArtifactLineMicroViewLabel(
      entry.selection.scoreLink.artifactLineMicroView,
    );
    const artifactLineDetailHoverLabel = formatComparisonScoreLinkArtifactLineDetailHoverLabel(
      entry.selection.scoreLink.artifactLineDetailHoverKey,
    );
    if (artifactHoverLabel) {
      parts.push(artifactHoverLabel);
    }
    if (entry.selection.scoreLink.detailExpanded === true) {
      parts.push("details open");
    } else if (entry.selection.scoreLink.detailExpanded === false) {
      parts.push("details hidden");
    }
    if (entry.selection.scoreLink.artifactDetailExpanded === true) {
      parts.push("artifact details open");
    } else if (entry.selection.scoreLink.artifactDetailExpanded === false) {
      parts.push("artifact details hidden");
    }
    if (entry.selection.scoreLink.artifactLineDetailExpanded === true) {
      parts.push("line detail open");
    } else if (entry.selection.scoreLink.artifactLineDetailExpanded === false) {
      parts.push("line detail hidden");
    }
    if (entry.selection.scoreLink.artifactLineDetailExpanded === true && artifactLineViewLabel) {
      parts.push(artifactLineViewLabel);
    }
    if (entry.selection.scoreLink.artifactLineDetailExpanded === true && artifactLineMicroViewLabel) {
      parts.push(artifactLineMicroViewLabel);
    }
    if (
      entry.selection.scoreLink.artifactLineDetailExpanded === true
      && entry.selection.scoreLink.artifactLineMicroView === "note"
      && entry.selection.scoreLink.artifactLineNotePage !== null
    ) {
      parts.push(`note ${entry.selection.scoreLink.artifactLineNotePage + 1}`);
    }
    if (entry.selection.scoreLink.artifactLineDetailExpanded === true && artifactLineDetailHoverLabel) {
      parts.push(artifactLineDetailHoverLabel);
    }
    if (
      entry.selection.scoreLink.artifactLineDetailExpanded === true
      && entry.selection.scoreLink.artifactLineDetailScrubStep !== null
    ) {
      parts.push(`scrub ${entry.selection.scoreLink.artifactLineDetailScrubStep + 1}`);
    }
  }
  if (entry.pinned) {
    parts.push("Pinned");
  }
  return parts.join(" / ");
}

function matchesComparisonHistoryPanelEntry(entry: ComparisonHistoryPanelEntry, query: string) {
  const haystack = [
    entry.label,
    entry.summary,
    entry.title,
    entry.url,
    formatComparisonHistoryPanelEntryMeta(entry),
  ].join(" ").toLowerCase();
  return haystack.includes(query);
}

function formatComparisonHistorySyncAuditKindLabel(kind: ComparisonHistorySyncAuditKind) {
  switch (kind) {
    case "merge":
      return "Merge";
    case "conflict":
      return "Conflict";
    case "preferences":
      return "Browser";
    case "workspace":
      return "Workspace";
    default:
      return kind;
  }
}

function buildComparisonHistoryStepDescriptor(
  selection: ControlRoomComparisonSelectionState,
  runs: Run[],
  comparison: RunComparison | null,
): ComparisonHistoryStepDescriptor {
  const normalizedSelection = normalizeControlRoomComparisonSelection(selection);
  const intentLabel = formatComparisonIntentLabel(normalizedSelection.intent);
  const selectedRuns = normalizedSelection.selectedRunIds.map((runId) => ({
    runId,
    label: resolveComparisonHistoryRunLabel(runId, runs, comparison),
  }));
  const baselineRunId =
    comparison?.baseline_run_id && normalizedSelection.selectedRunIds.includes(comparison.baseline_run_id)
      ? comparison.baseline_run_id
      : selectedRuns[0]?.runId ?? null;
  const baselineLabel = baselineRunId
    ? resolveComparisonHistoryRunLabel(baselineRunId, runs, comparison)
    : null;
  const comparisonTargets = selectedRuns.filter((candidate) => candidate.runId !== baselineRunId);
  const primaryNarrative = comparison?.narratives.find((candidate) => candidate.is_primary) ?? comparison?.narratives[0] ?? null;

  if (normalizedSelection.scoreLink) {
    const componentLabel = formatComparisonScoreComponentLabel(
      normalizedSelection.scoreLink.section,
      normalizedSelection.scoreLink.componentKey,
    );
    const sourceLabel = formatComparisonScoreLinkSourceLabel(normalizedSelection.scoreLink.source);
    const subFocusLabel = formatComparisonScoreLinkSubFocusLabel(normalizedSelection.scoreLink.subFocusKey);
    const tooltipLabel = formatComparisonScoreLinkTooltipLabel(normalizedSelection.scoreLink.tooltipKey);
    const artifactHoverLabel = formatComparisonScoreLinkArtifactHoverLabel(
      normalizedSelection.scoreLink.artifactHoverKey,
    );
    const artifactLineViewLabel = formatComparisonScoreLinkArtifactLineDetailViewLabel(
      normalizedSelection.scoreLink.artifactLineDetailView,
    );
    const artifactLineMicroViewLabel = formatComparisonScoreLinkArtifactLineMicroViewLabel(
      normalizedSelection.scoreLink.artifactLineMicroView,
    );
    const artifactLineDetailHoverLabel = formatComparisonScoreLinkArtifactLineDetailHoverLabel(
      normalizedSelection.scoreLink.artifactLineDetailHoverKey,
    );
    const focusRunLabel = resolveComparisonHistoryRunLabel(
      normalizedSelection.scoreLink.narrativeRunId,
      runs,
      comparison,
    );
    const originRunLabel =
      normalizedSelection.scoreLink.originRunId
        ? resolveComparisonHistoryRunLabel(
            normalizedSelection.scoreLink.originRunId,
            runs,
            comparison,
          )
        : null;
    const focusNarrative = comparison?.narratives.find(
      (candidate) => candidate.run_id === normalizedSelection.scoreLink?.narrativeRunId,
    ) ?? null;
    const label = `${truncateLabel(componentLabel, 20)} ${truncateLabel(sourceLabel, 12)} focus`;
    const summary = [
      `${componentLabel} is pinned to ${focusRunLabel} via ${sourceLabel}.`,
      normalizedSelection.selectedRunIds.length > 1
        ? `${intentLabel} across ${normalizedSelection.selectedRunIds.length} runs.`
        : `${intentLabel} with one staged run.`,
      subFocusLabel ? `Detail ${subFocusLabel}.` : null,
      tooltipLabel ? `Tooltip ${tooltipLabel}.` : null,
      artifactHoverLabel ? `Inspecting ${artifactHoverLabel}.` : null,
      normalizedSelection.scoreLink.detailExpanded === true ? "Score details open." : null,
      normalizedSelection.scoreLink.detailExpanded === false ? "Score details hidden." : null,
      normalizedSelection.scoreLink.artifactDetailExpanded === true ? "Artifact details open." : null,
      normalizedSelection.scoreLink.artifactDetailExpanded === false ? "Artifact details hidden." : null,
      normalizedSelection.scoreLink.artifactLineDetailExpanded === true ? "Line detail open." : null,
      normalizedSelection.scoreLink.artifactLineDetailExpanded === false ? "Line detail hidden." : null,
      normalizedSelection.scoreLink.artifactLineDetailExpanded === true && artifactLineViewLabel
        ? `${artifactLineViewLabel}.`
        : null,
      normalizedSelection.scoreLink.artifactLineDetailExpanded === true && artifactLineMicroViewLabel
        ? `${artifactLineMicroViewLabel}.`
        : null,
      normalizedSelection.scoreLink.artifactLineDetailExpanded === true
      && normalizedSelection.scoreLink.artifactLineMicroView === "note"
      && normalizedSelection.scoreLink.artifactLineNotePage !== null
        ? `Note ${normalizedSelection.scoreLink.artifactLineNotePage + 1}.`
        : null,
      normalizedSelection.scoreLink.artifactLineDetailExpanded === true && artifactLineDetailHoverLabel
        ? `Inspecting ${artifactLineDetailHoverLabel}.`
        : null,
      normalizedSelection.scoreLink.artifactLineDetailExpanded === true
      && normalizedSelection.scoreLink.artifactLineDetailScrubStep !== null
        ? `Scrub ${normalizedSelection.scoreLink.artifactLineDetailScrubStep + 1}.`
        : null,
      originRunLabel && originRunLabel !== focusRunLabel
        ? `Origin run ${originRunLabel}.`
        : null,
      baselineLabel && baselineRunId !== normalizedSelection.scoreLink.narrativeRunId
        ? `Baseline ${baselineLabel}.`
        : null,
      focusNarrative?.title ? `Story: ${truncateLabel(focusNarrative.title, 104)}.` : null,
    ]
      .filter(Boolean)
      .join(" ");
    return {
      label,
      summary,
      title: `Compare: ${label} | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
    };
  }

  if (!selectedRuns.length) {
    return {
      label: "Comparison cleared",
      summary: `No runs selected. ${intentLabel} is ready for the next comparison step.`,
      title: `Compare: cleared | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
    };
  }

  if (selectedRuns.length === 1) {
    const onlyRun = selectedRuns[0];
    const label = `${truncateLabel(onlyRun.label, 28)} staged`;
    return {
      label,
      summary: `${onlyRun.label} is staged for ${intentLabel.toLowerCase()}. Select one more run to open comparison insights.`,
      title: `Compare: ${label} | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
    };
  }

  const comparisonLabel =
    baselineLabel && comparisonTargets[0]
      ? `${truncateLabel(baselineLabel, 18)} vs ${truncateLabel(comparisonTargets[0].label, 18)}${
          comparisonTargets.length > 1 ? ` +${comparisonTargets.length - 1}` : ""
        }`
      : `${truncateLabel(selectedRuns[0].label, 18)} +${selectedRuns.length - 1}`;
  const summary = [
    baselineLabel
      ? `Baseline ${baselineLabel}${comparisonTargets[0] ? ` against ${comparisonTargets[0].label}` : ""}${
          comparisonTargets.length > 1 ? ` and ${comparisonTargets.length - 1} more runs` : ""
        }.`
      : `Tracking ${selectedRuns.length} runs.`,
    `${intentLabel} is active.`,
    primaryNarrative?.title ? `Top insight: ${truncateLabel(primaryNarrative.title, 104)}.` : null,
  ]
    .filter(Boolean)
    .join(" ");
  return {
    label: comparisonLabel,
    summary,
    title: `Compare: ${comparisonLabel} | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
  };
}

function resolveComparisonHistoryRunLabel(
  runId: string,
  runs: Run[],
  comparison: RunComparison | null,
) {
  const comparisonRun = comparison?.runs.find((candidate) => candidate.run_id === runId);
  if (comparisonRun) {
    return (
      comparisonRun.reference?.title
      ?? comparisonRun.strategy_name
      ?? comparisonRun.strategy_id
      ?? shortenIdentifier(runId)
    );
  }
  const run = runs.find((candidate) => candidate.config.run_id === runId);
  if (!run) {
    return shortenIdentifier(runId);
  }
  return (
    run.provenance.reference?.title
    ?? run.provenance.strategy?.name
    ?? run.config.strategy_id
    ?? shortenIdentifier(runId)
  );
}

function normalizeComparisonRunIdList(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return Array.from(
    new Set(
      value
        .map((item) => String(item).trim())
        .filter(Boolean),
    ),
  ).slice(0, MAX_COMPARISON_RUNS);
}

function normalizeComparisonIntent(value: unknown): ComparisonIntent {
  return comparisonIntentOptions.includes(value as ComparisonIntent)
    ? (value as ComparisonIntent)
    : DEFAULT_COMPARISON_INTENT;
}

function normalizeComparisonScoreSection(value: unknown): ComparisonScoreSection | null {
  return value === "metrics" || value === "semantics" || value === "context"
    ? value
    : null;
}

function normalizeComparisonScoreLinkSource(value: unknown): ComparisonScoreLinkSource | null {
  if (
    value === "metric"
    || value === "drillback"
    || value === "overview"
    || value === "provenance"
    || value === "run_card"
    || value === "run_list"
  ) {
    return value;
  }
  if (value === "narrative") {
    return "drillback";
  }
  return null;
}

function normalizeComparisonScoreLinkSubFocusKey(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function normalizeComparisonScoreLinkExpandedState(value: unknown) {
  if (value === true || value === false) {
    return value;
  }
  if (value === "1" || value === "true") {
    return true;
  }
  if (value === "0" || value === "false") {
    return false;
  }
  return null;
}

function normalizeComparisonScoreLinkTooltipKey(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function normalizeComparisonScoreLinkArtifactLineDetailView(
  value: unknown,
): ProvenanceArtifactLineDetailView | null {
  return value === "stats" || value === "context" ? value : null;
}

function normalizeComparisonScoreLinkArtifactLineMicroView(
  value: unknown,
): ProvenanceArtifactLineMicroView | null {
  return value === "structure" || value === "signal" || value === "note" ? value : null;
}

function normalizeComparisonScoreLinkArtifactLineNotePage(value: unknown) {
  if (typeof value === "number" && Number.isInteger(value) && value >= 0) {
    return value;
  }
  if (typeof value === "string" && value.trim()) {
    const parsed = Number.parseInt(value, 10);
    return Number.isInteger(parsed) && parsed >= 0 ? parsed : null;
  }
  return null;
}

function normalizeComparisonScoreLinkArtifactLineDetailHoverKey(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function normalizeComparisonScoreLinkArtifactLineScrubStep(value: unknown) {
  if (typeof value === "number" && Number.isInteger(value) && value >= 0) {
    return value;
  }
  if (typeof value === "string" && value.trim()) {
    const parsed = Number.parseInt(value, 10);
    return Number.isInteger(parsed) && parsed >= 0 ? parsed : null;
  }
  return null;
}

function normalizeComparisonScoreLinkArtifactHoverKey(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function normalizeComparisonScoreLinkTarget(value: unknown): ComparisonScoreLinkTarget | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonScoreLinkTarget>;
  const narrativeRunId =
    typeof candidate.narrativeRunId === "string" ? candidate.narrativeRunId.trim() : "";
  const componentKey = typeof candidate.componentKey === "string" ? candidate.componentKey.trim() : "";
  const section = normalizeComparisonScoreSection(candidate.section);
  const source = normalizeComparisonScoreLinkSource(candidate.source) ?? "drillback";
  const originRunId =
    typeof candidate.originRunId === "string" && candidate.originRunId.trim()
      ? candidate.originRunId.trim()
      : null;
  const subFocusKey = normalizeComparisonScoreLinkSubFocusKey(candidate.subFocusKey);
  const detailExpanded = normalizeComparisonScoreLinkExpandedState(candidate.detailExpanded);
  const artifactDetailExpanded = normalizeComparisonScoreLinkExpandedState(
    candidate.artifactDetailExpanded,
  );
  const artifactLineDetailExpanded = normalizeComparisonScoreLinkExpandedState(
    candidate.artifactLineDetailExpanded,
  );
  const artifactLineDetailView = normalizeComparisonScoreLinkArtifactLineDetailView(
    candidate.artifactLineDetailView,
  );
  const artifactLineMicroView = normalizeComparisonScoreLinkArtifactLineMicroView(
    candidate.artifactLineMicroView,
  );
  const artifactLineNotePage = normalizeComparisonScoreLinkArtifactLineNotePage(
    candidate.artifactLineNotePage,
  );
  const artifactLineDetailHoverKey = normalizeComparisonScoreLinkArtifactLineDetailHoverKey(
    candidate.artifactLineDetailHoverKey,
  );
  const artifactLineDetailScrubStep = normalizeComparisonScoreLinkArtifactLineScrubStep(
    candidate.artifactLineDetailScrubStep,
  );
  const tooltipKey = normalizeComparisonScoreLinkTooltipKey(candidate.tooltipKey);
  const artifactHoverKey = normalizeComparisonScoreLinkArtifactHoverKey(candidate.artifactHoverKey);
  if (!narrativeRunId || !componentKey || !section) {
    return null;
  }
  return {
    componentKey,
    detailExpanded,
    artifactDetailExpanded,
    artifactLineDetailExpanded,
    artifactLineDetailView,
    artifactLineMicroView,
    artifactLineNotePage,
    artifactLineDetailHoverKey,
    artifactLineDetailScrubStep,
    narrativeRunId,
    originRunId,
    section,
    source,
    subFocusKey,
    tooltipKey,
    artifactHoverKey,
  };
}

function isControlRoomUiStateV1(value: unknown): value is ControlRoomUiStateV1 {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ControlRoomUiStateV1>;
  return (
    candidate.version === 1 &&
    candidate.expandedGapRows !== undefined
  );
}

function isControlRoomUiStateV2(value: unknown): value is ControlRoomUiStateV2 {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ControlRoomUiStateV2>;
  return (
    candidate.version === 2 &&
    candidate.expandedGapRows !== undefined &&
    candidate.comparisonSelection !== undefined
  );
}

function isControlRoomUiStateV3(value: unknown): value is ControlRoomUiStateV3 {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ControlRoomUiStateV3>;
  return (
    candidate.version === 3 &&
    candidate.expandedGapRows !== undefined &&
    candidate.comparisonSelection !== undefined &&
    candidate.comparisonHistoryPanel !== undefined
  );
}

function isControlRoomUiStateV4(value: unknown): value is ControlRoomUiStateV4 {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ControlRoomUiStateV4>;
  return (
    candidate.version === CONTROL_ROOM_UI_STATE_VERSION &&
    candidate.expandedGapRows !== undefined &&
    candidate.expandedGapWindowSelections !== undefined &&
    candidate.comparisonSelection !== undefined &&
    candidate.comparisonHistoryPanel !== undefined
  );
}

function buildRunsPath(mode: string, filter: RunHistoryFilter) {
  const params = new URLSearchParams({ mode });
  const sanitizedFilter = sanitizeRunHistoryFilter(filter);
  if (sanitizedFilter.strategy_id !== ALL_FILTER_VALUE) {
    params.set("strategy_id", sanitizedFilter.strategy_id);
  }
  if (sanitizedFilter.strategy_version !== ALL_FILTER_VALUE) {
    params.set("strategy_version", sanitizedFilter.strategy_version);
  }
  if (sanitizedFilter.preset_id) {
    params.set("preset_id", sanitizedFilter.preset_id);
  }
  if (sanitizedFilter.benchmark_family) {
    params.set("benchmark_family", sanitizedFilter.benchmark_family);
  }
  if (sanitizedFilter.tag) {
    parseExperimentTags(sanitizedFilter.tag).forEach((tag) => params.append("tag", tag));
  }
  if (sanitizedFilter.dataset_identity) {
    params.set("dataset_identity", sanitizedFilter.dataset_identity);
  }
  if (sanitizedFilter.filter_expr) {
    params.set("filter_expr", sanitizedFilter.filter_expr);
  }
  return `/runs?${params.toString()}`;
}

function buildRunComparisonPath(runIds: string[], intent: ComparisonIntent) {
  const params = new URLSearchParams();
  runIds.forEach((runId) => params.append("run_id", runId));
  params.set("intent", intent);
  return `/runs/compare?${params.toString()}`;
}

function normalizeRunHistoryFilter(current: RunHistoryFilter, strategies: Strategy[]) {
  const sanitizedCurrent = sanitizeRunHistoryFilter(current);
  const availableStrategyIds = new Set(strategies.map((strategy) => strategy.strategy_id));
  if (
    sanitizedCurrent.strategy_id !== ALL_FILTER_VALUE &&
    !availableStrategyIds.has(sanitizedCurrent.strategy_id)
  ) {
    return {
      ...defaultRunHistoryFilter,
      preset_id: sanitizedCurrent.preset_id,
      benchmark_family: sanitizedCurrent.benchmark_family,
      tag: sanitizedCurrent.tag,
      dataset_identity: sanitizedCurrent.dataset_identity,
      filter_expr: sanitizedCurrent.filter_expr,
      collection_query_label: sanitizedCurrent.collection_query_label,
    };
  }
  const availableVersions = getStrategyVersionOptions(strategies, sanitizedCurrent.strategy_id);
  if (
    sanitizedCurrent.strategy_version !== ALL_FILTER_VALUE &&
    !availableVersions.includes(sanitizedCurrent.strategy_version)
  ) {
    return { ...sanitizedCurrent, strategy_version: ALL_FILTER_VALUE };
  }
  return sanitizedCurrent;
}

function normalizeRunHistoryPresetFilter(
  current: RunHistoryFilter,
  presets: ExperimentPreset[],
) {
  const sanitizedCurrent = sanitizeRunHistoryFilter(current);
  if (!sanitizedCurrent.preset_id) {
    return sanitizedCurrent;
  }
  const matchingPreset = presets.find((preset) => preset.preset_id === sanitizedCurrent.preset_id);
  if (
    matchingPreset &&
    (
      sanitizedCurrent.strategy_id === ALL_FILTER_VALUE ||
      !matchingPreset.strategy_id ||
      matchingPreset.strategy_id === sanitizedCurrent.strategy_id
    )
  ) {
    return sanitizedCurrent;
  }
  return {
    ...sanitizedCurrent,
    preset_id: "",
  };
}

function getStrategyVersionOptions(strategies: Strategy[], strategyId: string) {
  const scopedStrategies =
    strategyId === ALL_FILTER_VALUE
      ? strategies
      : strategies.filter((strategy) => strategy.strategy_id === strategyId);
  return Array.from(
    new Set(
      scopedStrategies.flatMap((strategy) =>
        strategy.version_lineage.length ? strategy.version_lineage : [strategy.version],
      ),
    ),
  ).sort();
}

function pickLatestBenchmarkRun(runs: Run[], lane: string) {
  return (
    runs.find((run) => run.provenance.lane === lane && run.status === "completed") ??
    runs.find((run) => run.provenance.lane === lane) ??
    null
  );
}

function StrategyColumn({
  title,
  strategies,
  accent,
  runSurfaceCapabilities,
}: {
  title: string;
  strategies: Strategy[];
  accent: string;
  runSurfaceCapabilities: RunSurfaceCapabilities | null;
}) {
  const schemaHintsEnabled = shouldEnableStrategyCatalogSchemaHints(runSurfaceCapabilities);
  return (
    <div className={`strategy-column ${accent}`}>
      <h3>{title}</h3>
      {strategies.length ? (
        strategies.map((strategy) => (
          <article className="strategy-card" key={strategy.strategy_id}>
            <div className="strategy-head">
              <div>
                <strong>{strategy.name}</strong>
                <div className="strategy-badges">
                  <span className="meta-pill">{formatLaneLabel(strategy.runtime)}</span>
                  <span className="meta-pill subtle">{strategy.lifecycle.stage}</span>
                  <span className="meta-pill subtle">{strategy.version}</span>
                </div>
              </div>
              <span>{formatVersionLineage(strategy.version_lineage, strategy.version)}</span>
            </div>
            <p>{strategy.description}</p>
            {schemaHintsEnabled && strategy.catalog_semantics.execution_model ? (
              <p className="run-note">{strategy.catalog_semantics.execution_model}</p>
            ) : null}
            <dl>
              <div>
                <dt>ID</dt>
                <dd>{strategy.strategy_id}</dd>
              </div>
              <div>
                <dt>Timeframes</dt>
                <dd>{strategy.supported_timeframes.join(", ")}</dd>
              </div>
              <div>
                <dt>Assets</dt>
                <dd>{strategy.asset_types.join(", ")}</dd>
              </div>
              {schemaHintsEnabled ? (
                <div>
                  <dt>Defaults</dt>
                  <dd>{formatParameterMap(extractDefaultParameters(strategy.parameter_schema))}</dd>
                </div>
              ) : null}
              {schemaHintsEnabled && strategy.catalog_semantics.parameter_contract ? (
                <div>
                  <dt>Parameter contract</dt>
                  <dd>{strategy.catalog_semantics.parameter_contract}</dd>
                </div>
              ) : null}
              {schemaHintsEnabled && strategy.catalog_semantics.source_descriptor ? (
                <div>
                  <dt>Source</dt>
                  <dd>{strategy.catalog_semantics.source_descriptor}</dd>
                </div>
              ) : null}
              {strategy.reference_path ? (
                <div>
                  <dt>Reference</dt>
                  <dd>{strategy.reference_path}</dd>
                </div>
              ) : null}
              {strategy.reference_id ? (
                <div>
                  <dt>Reference ID</dt>
                  <dd>{strategy.reference_id}</dd>
                </div>
              ) : null}
              {strategy.lifecycle.registered_at ? (
                <div>
                  <dt>Registered</dt>
                  <dd>{formatTimestamp(strategy.lifecycle.registered_at)}</dd>
                </div>
              ) : null}
              {schemaHintsEnabled && strategy.catalog_semantics.operator_notes.length ? (
                <div>
                  <dt>Operator notes</dt>
                  <dd>{strategy.catalog_semantics.operator_notes.join(" | ")}</dd>
                </div>
              ) : null}
            </dl>
          </article>
        ))
      ) : (
        <p className="empty-state">No strategies registered.</p>
      )}
    </div>
  );
}

function ReferenceCatalog({ references }: { references: ReferenceSource[] }) {
  return references.length ? (
    <div className="run-list">
      {references.map((reference) => (
        <article className="run-card" key={reference.reference_id}>
          <div className="run-card-head">
            <div>
              <strong>{reference.title}</strong>
              <span>{reference.reference_id}</span>
            </div>
            <div className="run-status completed">{reference.integration_mode}</div>
          </div>
          <div className="run-metrics">
            <Metric label="License" value={reference.license} />
            <Metric label="Runtime" value={reference.runtime ?? "n/a"} />
          </div>
          <p className="run-note">{reference.summary}</p>
        </article>
      ))}
    </div>
  ) : (
    <p className="empty-state">No references registered.</p>
  );
}

function PresetStructuredDiffPreview({
  changedGroups,
  emptyMessage,
  leftColumnLabel,
  rightColumnLabel,
  title,
  unchangedGroups,
}: {
  changedGroups: PresetStructuredDiffGroup[];
  emptyMessage: string;
  leftColumnLabel: string;
  rightColumnLabel: string;
  title: string;
  unchangedGroups: PresetStructuredDiffGroup[];
}) {
  const [showUnchangedGroups, setShowUnchangedGroups] = useState(false);
  const unchangedRowCount = unchangedGroups.reduce((total, group) => total + group.rows.length, 0);
  const renderGroupRows = (group: PresetStructuredDiffGroup) =>
    group.rows.map((row) => (
      <div
        className={`comparison-dev-conflict-preview-row ${row.changed ? "is-changed" : ""}`}
        key={row.key}
      >
        <span className="comparison-dev-conflict-preview-label-group">
          <span className="comparison-dev-conflict-preview-label">{row.label}</span>
          {row.semantic_hint ? (
            <span className="comparison-dev-conflict-preview-hint">{row.semantic_hint}</span>
          ) : null}
          <span className={`comparison-dev-conflict-delta comparison-dev-conflict-delta-${row.delta_direction}`}>
            {row.delta_label}
          </span>
        </span>
        <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-existing">
          {row.existing_value}
        </span>
        <span
          className={`comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-incoming comparison-dev-conflict-preview-value-${
            row.changed ? row.delta_direction : "same"
          }`}
        >
          {row.incoming_value}
        </span>
      </div>
    ));

  return (
    <div className="comparison-dev-session-summary">
      <p className="comparison-dev-session-summary-title">{title}</p>
      <div className="comparison-dev-conflict-preview">
        <div className="comparison-dev-conflict-preview-row comparison-dev-conflict-preview-head">
          <span>Field</span>
          <span>{leftColumnLabel}</span>
          <span>{rightColumnLabel}</span>
        </div>
        {changedGroups.length ? (
          changedGroups.map((group) => (
            <div className="comparison-dev-conflict-preview-group" key={group.key}>
              <div className="comparison-dev-conflict-preview-group-title">
                <span>{group.label}</span>
                <span className="comparison-dev-conflict-preview-group-meta">
                  <span className="comparison-dev-conflict-preview-group-summary">{group.summary_label}</span>
                </span>
              </div>
              {renderGroupRows(group)}
            </div>
          ))
        ) : (
          <p className="empty-state">{emptyMessage}</p>
        )}
        {unchangedRowCount ? (
          <button
            className="comparison-dev-conflict-toggle"
            onClick={() => setShowUnchangedGroups((current) => !current)}
            type="button"
          >
            {showUnchangedGroups
              ? `Hide ${unchangedRowCount} unchanged field${unchangedRowCount === 1 ? "" : "s"}`
              : `Show ${unchangedRowCount} unchanged field${unchangedRowCount === 1 ? "" : "s"}`}
          </button>
        ) : null}
        {showUnchangedGroups
          ? unchangedGroups.map((group) => (
              <div className="comparison-dev-conflict-preview-group" key={group.key}>
                <div className="comparison-dev-conflict-preview-group-title">
                  <span>{group.label}</span>
                  <span className="comparison-dev-conflict-preview-group-meta">
                    <span className="comparison-dev-conflict-preview-group-summary">{group.summary_label}</span>
                  </span>
                </div>
                {renderGroupRows(group)}
              </div>
            ))
          : null}
      </div>
    </div>
  );
}

function PresetCatalogPanel({
  form,
  presets,
  runSurfaceCapabilities,
  setForm,
  strategies,
  editingPresetId,
  expandedPresetRevisionIds,
  onEditPreset,
  onResetEditor,
  onLifecycleAction,
  onRestoreRevision,
  onSubmit,
  onToggleRevisions,
}: {
  form: typeof defaultPresetForm;
  presets: ExperimentPreset[];
  runSurfaceCapabilities: RunSurfaceCapabilities | null;
  setForm: (updater: (value: typeof defaultPresetForm) => typeof defaultPresetForm) => void;
  strategies: Strategy[];
  editingPresetId: string | null;
  expandedPresetRevisionIds: Record<string, boolean>;
  onEditPreset: (preset: ExperimentPreset) => void;
  onResetEditor: () => void;
  onLifecycleAction: (presetId: string, action: "promote" | "archive" | "restore") => Promise<void> | void;
  onRestoreRevision: (presetId: string, revisionId: string) => Promise<void> | void;
  onSubmit: (event: FormEvent) => Promise<void> | void;
  onToggleRevisions: (presetId: string) => void;
}) {
  const isEditing = editingPresetId !== null;
  const findStrategyParameterSchema = (strategyId?: string | null) =>
    strategies.find((strategy) => strategy.strategy_id === strategyId)?.parameter_schema;
  const presetParameterDefaultsEnabled = shouldHydratePresetParameterDefaults(runSurfaceCapabilities);
  const selectedStrategyParameterSchema = findStrategyParameterSchema(form.strategy_id);
  const selectedStrategyDefaultParameters = selectedStrategyParameterSchema
    ? extractDefaultParameters(selectedStrategyParameterSchema)
    : {};
  const selectedStrategyDefaultParametersJson = Object.keys(selectedStrategyDefaultParameters).length
    ? JSON.stringify(selectedStrategyDefaultParameters, null, 2)
    : "";
  const [revisionFiltersByPreset, setRevisionFiltersByPreset] = useState<
    Record<string, PresetRevisionFilterState>
  >({});
  const [expandedRevisionDiffIds, setExpandedRevisionDiffIds] = useState<Record<string, boolean>>({});
  const [restoreDraftConflictAcknowledgements, setRestoreDraftConflictAcknowledgements] = useState<
    Record<string, boolean>
  >({});
  const [pendingRestoreTarget, setPendingRestoreTarget] = useState<{
    presetId: string;
    revisionId: string;
  } | null>(null);
  const lastAutoHydratedStrategyId = useRef<string | null>(null);

  useEffect(() => {
    const strategyId = form.strategy_id || null;
    const strategyChanged = lastAutoHydratedStrategyId.current !== strategyId;
    lastAutoHydratedStrategyId.current = strategyId;
    if (!strategyChanged || !presetParameterDefaultsEnabled || !strategyId) {
      return;
    }
    if (!selectedStrategyDefaultParametersJson) {
      return;
    }
    if (form.parameters_text.trim()) {
      return;
    }
    setForm((current) => {
      if ((current.strategy_id || null) !== strategyId || current.parameters_text.trim()) {
        return current;
      }
      return {
        ...current,
        parameters_text: selectedStrategyDefaultParametersJson,
      };
    });
  }, [
    form.parameters_text,
    form.strategy_id,
    presetParameterDefaultsEnabled,
    selectedStrategyDefaultParametersJson,
    setForm,
  ]);

  async function confirmRevisionRestore(presetId: string, revisionId: string) {
    await onRestoreRevision(presetId, revisionId);
    setRestoreDraftConflictAcknowledgements((current) => {
      const next = { ...current };
      delete next[`${presetId}:${revisionId}`];
      return next;
    });
    setPendingRestoreTarget((current) =>
      current?.presetId === presetId && current?.revisionId === revisionId ? null : current,
    );
  }

  return (
    <>
      <RunSurfaceCapabilityDiscoveryPanel capabilities={runSurfaceCapabilities} compact />
      <form className="run-form" onSubmit={onSubmit}>
        <label>
          Name
          <input
            placeholder="Core 5m"
            value={form.name}
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
          />
        </label>
        <label>
          Preset ID
          <input
            disabled={isEditing}
            placeholder="core_5m"
            value={form.preset_id}
            onChange={(event) => setForm((current) => ({ ...current, preset_id: event.target.value }))}
          />
        </label>
        <label>
          Strategy
          <select
            value={form.strategy_id}
            onChange={(event) => setForm((current) => ({ ...current, strategy_id: event.target.value }))}
          >
            <option value="">Any strategy</option>
            {strategies.map((strategy) => (
              <option key={strategy.strategy_id} value={strategy.strategy_id}>
                {strategy.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Timeframe
          <input
            placeholder="5m"
            value={form.timeframe}
            onChange={(event) => setForm((current) => ({ ...current, timeframe: event.target.value }))}
          />
        </label>
        <label>
          Benchmark family
          <input
            placeholder="native_validation"
            value={form.benchmark_family}
            onChange={(event) =>
              setForm((current) => ({ ...current, benchmark_family: event.target.value }))
            }
          />
        </label>
        <label>
          Tags
          <input
            placeholder="baseline, momentum"
            value={form.tags_text}
            onChange={(event) => setForm((current) => ({ ...current, tags_text: event.target.value }))}
          />
        </label>
        <label>
          Description
          <input
            placeholder="Reusable backtest baseline"
            value={form.description}
            onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
          />
        </label>
        <label>
          Parameters JSON
          <textarea
            placeholder={selectedStrategyDefaultParametersJson || '{"short_window": 5, "long_window": 13}'}
            rows={4}
            value={form.parameters_text}
            onChange={(event) =>
              setForm((current) => ({ ...current, parameters_text: event.target.value }))
            }
          />
        </label>
        {presetParameterDefaultsEnabled && selectedStrategyDefaultParametersJson ? (
          <p className="run-note">
            Empty parameter bundles auto-hydrate from the selected strategy schema contract.
          </p>
        ) : null}
        {isEditing ? (
          <p className="run-note">
            Editing {editingPresetId}. Preset IDs are immutable, so this form updates the current bundle and records a
            new revision.
          </p>
        ) : null}
        <div className="run-actions">
          <button type="submit">{isEditing ? "Save revision" : "Save preset"}</button>
          {isEditing ? (
            <button className="ghost-button" onClick={onResetEditor} type="button">
              New preset
            </button>
          ) : null}
        </div>
      </form>

      {presets.length ? (
        <div className="run-list">
          {presets.map((preset) => (
            <article className="run-card" key={preset.preset_id}>
              {(() => {
                const revisions = [...preset.revisions].reverse();
                const latestRevisionId = revisions[0]?.revision_id;
                const revisionsExpanded = Boolean(expandedPresetRevisionIds[preset.preset_id]);
                const revisionFilter = revisionFiltersByPreset[preset.preset_id] ?? defaultPresetRevisionFilter;
                const draftConflict =
                  editingPresetId === preset.preset_id
                    ? describePresetDraftConflict(
                        preset,
                        form,
                        findStrategyParameterSchema(form.strategy_id || preset.strategy_id),
                      )
                    : null;
                const visibleRevisionEntries = revisions
                  .map((revision, index) => {
                    const diffReference =
                      revision.revision_id === latestRevisionId
                        ? revisions[index + 1] ?? null
                        : buildCurrentPresetRevisionSnapshot(preset);
                    const diffBasisLabel =
                      revision.revision_id === latestRevisionId
                        ? revisions[index + 1]
                          ? "previous snapshot"
                          : "initial revision"
                        : "current bundle";
                    const diff = describePresetRevisionDiff(
                      revision,
                      diffReference,
                      diffBasisLabel,
                      findStrategyParameterSchema(revision.strategy_id ?? preset.strategy_id),
                    );
                    return { diff, revision };
                  })
                  .filter(({ diff, revision }) => matchesPresetRevisionFilter(revision, diff, revisionFilter));
                return (
                  <>
                    <div className="run-card-head">
                      <div>
                        <strong>{preset.name}</strong>
                        <span>{preset.preset_id}</span>
                      </div>
                      <div className={`run-status ${preset.lifecycle.stage === "archived" ? "failed" : "completed"}`}>
                        {formatPresetLifecycleStage(preset.lifecycle.stage)}
                      </div>
                    </div>
                    <div className="run-metrics">
                      <Metric label="Strategy" value={preset.strategy_id ?? "any"} />
                      <Metric label="Timeframe" value={preset.timeframe ?? "any"} />
                      <Metric label="Params" value={formatParameterMap(preset.parameters)} />
                      <Metric label="Revisions" value={String(preset.revisions.length)} />
                      <Metric label="Updated" value={formatTimestamp(preset.updated_at)} />
                    </div>
                    <ExperimentMetadataPills
                      benchmarkFamily={preset.benchmark_family}
                      presetId={preset.preset_id}
                      tags={preset.tags}
                    />
                    <p className="run-note">
                      Lifecycle: {formatPresetLifecycleStage(preset.lifecycle.stage)} via{" "}
                      {preset.lifecycle.last_action} by {preset.lifecycle.updated_by} at{" "}
                      {formatTimestamp(preset.lifecycle.updated_at)}.
                    </p>
                    {preset.description ? <p className="run-note">{preset.description}</p> : null}
                    <div className="run-actions">
                      <button className="ghost-button" onClick={() => onEditPreset(preset)} type="button">
                        {editingPresetId === preset.preset_id ? "Editing bundle" : "Edit bundle"}
                      </button>
                      <button
                        className="ghost-button"
                        onClick={() => onToggleRevisions(preset.preset_id)}
                        type="button"
                      >
                        {revisionsExpanded ? "Hide revisions" : `Show revisions (${preset.revisions.length})`}
                      </button>
                      {preset.lifecycle.stage !== "archived" ? (
                        <>
                          {preset.lifecycle.stage !== "live_candidate" ? (
                            <button
                              className="ghost-button"
                              onClick={() => void onLifecycleAction(preset.preset_id, "promote")}
                              type="button"
                            >
                              Promote
                            </button>
                          ) : null}
                          <button
                            className="ghost-button danger"
                            onClick={() => void onLifecycleAction(preset.preset_id, "archive")}
                            type="button"
                          >
                            Archive
                          </button>
                        </>
                      ) : (
                        <button
                          className="ghost-button"
                          onClick={() => void onLifecycleAction(preset.preset_id, "restore")}
                          type="button"
                        >
                          Restore to draft
                        </button>
                      )}
                    </div>
                    {revisionsExpanded ? (
                      <>
                        <div className="run-form">
                          <label>
                            Search revisions
                            <input
                              placeholder="actor, reason, parameter, tag"
                              value={revisionFilter.query}
                              onChange={(event) =>
                                setRevisionFiltersByPreset((current) => ({
                                  ...current,
                                  [preset.preset_id]: {
                                    ...(current[preset.preset_id] ?? defaultPresetRevisionFilter),
                                    query: event.target.value,
                                  },
                                }))
                              }
                            />
                          </label>
                          <label>
                            Action
                            <select
                              value={revisionFilter.action}
                              onChange={(event) =>
                                setRevisionFiltersByPreset((current) => ({
                                  ...current,
                                  [preset.preset_id]: {
                                    ...(current[preset.preset_id] ?? defaultPresetRevisionFilter),
                                    action: event.target.value,
                                  },
                                }))
                              }
                            >
                              <option value="all">All actions</option>
                              <option value="created">Created</option>
                              <option value="updated">Updated</option>
                              <option value="restored">Restored</option>
                              <option value="migrated">Migrated</option>
                            </select>
                          </label>
                        </div>
                        <p className="run-note">
                          Showing {visibleRevisionEntries.length} of {revisions.length} revision
                          {revisions.length === 1 ? "" : "s"}.
                        </p>
                        {visibleRevisionEntries.length ? (
                          <div className="run-list">
                            {visibleRevisionEntries.map(({ revision, diff }) => {
                              const diffExpanded = Boolean(expandedRevisionDiffIds[revision.revision_id]);
                              const confirmingRestore =
                                pendingRestoreTarget?.presetId === preset.preset_id &&
                                pendingRestoreTarget?.revisionId === revision.revision_id;
                              const acknowledgementKey = `${preset.preset_id}:${revision.revision_id}`;
                              const hasDraftConflict = Boolean(draftConflict && draftConflict.changeCount);
                              const draftConflictAcknowledged = Boolean(
                                restoreDraftConflictAcknowledgements[acknowledgementKey],
                              );
                              return (
                                <article className="run-card" key={revision.revision_id}>
                                  <div className="run-card-head">
                                    <div>
                                      <strong>{revision.revision_id}</strong>
                                      <span>{revision.action}</span>
                                    </div>
                                    <div
                                      className={`run-status ${
                                        revision.revision_id === latestRevisionId ? "completed" : "pending"
                                      }`}
                                    >
                                      {revision.revision_id === latestRevisionId ? "current bundle" : "snapshot"}
                                    </div>
                                  </div>
                                  <div className="run-metrics">
                                    <Metric label="Actor" value={revision.actor} />
                                    <Metric label="Recorded" value={formatRelativeTimestampLabel(revision.created_at)} />
                                    <Metric label="Strategy" value={revision.strategy_id ?? "any"} />
                                    <Metric label="Diff" value={`${diff.changeCount} change${diff.changeCount === 1 ? "" : "s"}`} />
                                  </div>
                                  <ExperimentMetadataPills
                                    benchmarkFamily={revision.benchmark_family}
                                    tags={revision.tags}
                                  />
                                  <p className="run-note">
                                    Reason: {revision.reason}. {diff.summary}
                                    {revision.source_revision_id ? ` Restored from ${revision.source_revision_id}.` : ""}
                                  </p>
                                  {revision.description ? <p className="run-note">{revision.description}</p> : null}
                                  <div className="run-actions">
                                    <button
                                      className="ghost-button"
                                      onClick={() =>
                                        setExpandedRevisionDiffIds((current) => ({
                                          ...current,
                                          [revision.revision_id]: !current[revision.revision_id],
                                        }))
                                      }
                                      type="button"
                                    >
                                      {diffExpanded ? "Hide diff" : `Show diff vs ${diff.basisLabel}`}
                                    </button>
                                    {revision.revision_id !== latestRevisionId ? (
                                      <button
                                        className="ghost-button"
                                        onClick={() => {
                                          setPendingRestoreTarget({
                                            presetId: preset.preset_id,
                                            revisionId: revision.revision_id,
                                          });
                                          setRestoreDraftConflictAcknowledgements((current) => ({
                                            ...current,
                                            [acknowledgementKey]: false,
                                          }));
                                        }}
                                        type="button"
                                      >
                                        Restore bundle
                                      </button>
                                    ) : null}
                                  </div>
                                  {diffExpanded ? (
                                    <PresetStructuredDiffPreview
                                      changedGroups={diff.changedGroups}
                                      emptyMessage={diff.summary}
                                      leftColumnLabel={diff.basisLabel}
                                      rightColumnLabel="Revision snapshot"
                                      title={`Diff vs ${diff.basisLabel}`}
                                      unchangedGroups={diff.unchangedGroups}
                                    />
                                  ) : null}
                                  {confirmingRestore ? (
                                    <div className="comparison-dev-confirm-card">
                                      <p className="comparison-dev-feedback">
                                        Restore {revision.revision_id} into {preset.preset_id}? This will create a new
                                        current revision from the selected snapshot.
                                      </p>
                                      <p className="run-note">{diff.summary}</p>
                                      <PresetStructuredDiffPreview
                                        changedGroups={diff.changedGroups}
                                        emptyMessage={diff.summary}
                                        leftColumnLabel="Current bundle"
                                        rightColumnLabel="Restore target"
                                        title="Restore impact"
                                        unchangedGroups={diff.unchangedGroups}
                                      />
                                      {hasDraftConflict && draftConflict ? (
                                        <>
                                          <p className="comparison-dev-feedback">
                                            {draftConflict.summary}
                                            {draftConflict.hasInvalidParameters
                                              ? " The current draft also contains invalid parameter JSON."
                                              : ""}
                                          </p>
                                          <PresetStructuredDiffPreview
                                            changedGroups={draftConflict.groups}
                                            emptyMessage={draftConflict.summary}
                                            leftColumnLabel="Saved bundle"
                                            rightColumnLabel="Current draft"
                                            title="Unsaved draft conflict"
                                            unchangedGroups={[]}
                                          />
                                          <label className="run-note">
                                            <input
                                              checked={draftConflictAcknowledged}
                                              onChange={(event) =>
                                                setRestoreDraftConflictAcknowledgements((current) => ({
                                                  ...current,
                                                  [acknowledgementKey]: event.target.checked,
                                                }))
                                              }
                                              type="checkbox"
                                            />{" "}
                                            I understand this restore will discard the unsaved draft for{" "}
                                            {preset.preset_id}.
                                          </label>
                                        </>
                                      ) : null}
                                      <div className="comparison-dev-actions comparison-dev-actions-inline">
                                        <button
                                          className="ghost-button comparison-dev-reset"
                                          disabled={hasDraftConflict && !draftConflictAcknowledged}
                                          onClick={() => void confirmRevisionRestore(preset.preset_id, revision.revision_id)}
                                          type="button"
                                        >
                                          {hasDraftConflict ? "Discard draft and restore" : "Confirm restore"}
                                        </button>
                                        <button
                                          className="ghost-button comparison-dev-reset"
                                          onClick={() => {
                                            setPendingRestoreTarget(null);
                                            setRestoreDraftConflictAcknowledgements((current) => {
                                              const next = { ...current };
                                              delete next[acknowledgementKey];
                                              return next;
                                            });
                                          }}
                                          type="button"
                                        >
                                          Cancel
                                        </button>
                                      </div>
                                    </div>
                                  ) : null}
                                </article>
                              );
                            })}
                          </div>
                        ) : (
                          <p className="empty-state">No revisions match the current filter.</p>
                        )}
                      </>
                    ) : null}
                  </>
                );
              })()}
            </article>
          ))}
        </div>
      ) : (
        <p className="empty-state">No durable presets saved yet.</p>
      )}
    </>
  );
}

function RunForm({
  form,
  setForm,
  strategies,
  presets,
  onSubmit,
}: {
  form: typeof defaultRunForm;
  setForm: (updater: (value: typeof defaultRunForm) => typeof defaultRunForm) => void;
  strategies: Strategy[];
  presets: ExperimentPreset[];
  onSubmit: (event: FormEvent) => Promise<void> | void;
}) {
  const availablePresets = presets.filter(
    (preset) =>
      preset.lifecycle.stage !== "archived" &&
      (!preset.strategy_id || preset.strategy_id === form.strategy_id) &&
      (!preset.timeframe || preset.timeframe === form.timeframe),
  );
  const selectedPreset = availablePresets.find((preset) => preset.preset_id === form.preset_id) ?? null;

  return (
    <form className="run-form" onSubmit={onSubmit}>
      <label>
        Strategy
        <select
          value={form.strategy_id}
          onChange={(event) => setForm((current) => ({ ...current, strategy_id: event.target.value }))}
        >
          {strategies.map((strategy) => (
            <option key={strategy.strategy_id} value={strategy.strategy_id}>
              {strategy.name} / {strategy.runtime}
            </option>
          ))}
        </select>
      </label>
      <label>
        Symbol
        <input
          value={form.symbol}
          onChange={(event) => setForm((current) => ({ ...current, symbol: event.target.value }))}
        />
      </label>
      <label>
        Timeframe
        <input
          value={form.timeframe}
          onChange={(event) => setForm((current) => ({ ...current, timeframe: event.target.value }))}
        />
      </label>
      <label>
        Initial cash
        <input
          type="number"
          value={form.initial_cash}
          onChange={(event) => setForm((current) => ({ ...current, initial_cash: Number(event.target.value) }))}
        />
      </label>
      <label>
        Fee rate
        <input
          type="number"
          step="0.0001"
          value={form.fee_rate}
          onChange={(event) => setForm((current) => ({ ...current, fee_rate: Number(event.target.value) }))}
        />
      </label>
      <label>
        Slippage (bps)
        <input
          type="number"
          value={form.slippage_bps}
          onChange={(event) => setForm((current) => ({ ...current, slippage_bps: Number(event.target.value) }))}
        />
      </label>
      <label>
        Preset
        <select
          value={form.preset_id}
          onChange={(event) => setForm((current) => ({ ...current, preset_id: event.target.value }))}
        >
          <option value="">No preset</option>
          {availablePresets.map((preset) => (
            <option key={preset.preset_id} value={preset.preset_id}>
              {preset.name} ({preset.preset_id})
            </option>
          ))}
        </select>
      </label>
      <label>
        Benchmark family
        <input
          placeholder={selectedPreset?.benchmark_family ?? "native_vs_nfi"}
          value={form.benchmark_family}
          onChange={(event) =>
            setForm((current) => ({ ...current, benchmark_family: event.target.value }))
          }
        />
      </label>
      <label>
        Tags
        <input
          placeholder="baseline, momentum"
          value={form.tags_text}
          onChange={(event) => setForm((current) => ({ ...current, tags_text: event.target.value }))}
        />
      </label>
      {selectedPreset ? (
        <div className="run-note">
          Preset stage: {formatPresetLifecycleStage(selectedPreset.lifecycle.stage)}. Parameters:{" "}
          {formatParameterMap(selectedPreset.parameters)}.
        </div>
      ) : null}
      <button type="submit">Submit</button>
    </form>
  );
}

function ExperimentMetadataPills({
  benchmarkFamily,
  datasetIdentity,
  interactionSource = "run_list",
  linkedScore,
  onDrillBackScoreLink,
  panelRunId,
  presetId,
  registerSubFocusRef,
  tags,
}: {
  benchmarkFamily?: string | null;
  datasetIdentity?: string | null;
  interactionSource?: ComparisonScoreLinkSource;
  linkedScore?: (ComparisonScoreLinkTarget & { role: ComparisonScoreLinkedRunRole }) | null;
  onDrillBackScoreLink?: (
    section: ComparisonScoreSection,
    componentKey: string,
    options?: ComparisonScoreDrillBackOptions,
  ) => void;
  panelRunId?: string;
  presetId?: string | null;
  registerSubFocusRef?: (runId: string, subFocusKey: string) => (node: HTMLElement | null) => void;
  tags: string[];
}) {
  if (!tags.length && !presetId && !benchmarkFamily && !datasetIdentity) {
    return null;
  }
  const activeRunListSubFocusKey =
    linkedScore?.source === interactionSource
      ? linkedScore.subFocusKey
      : null;
  const renderPill = (
    label: string,
    title: string | undefined,
    componentKey: string,
    subFocusKey: string,
    highlighted: boolean,
  ) => {
    const isPressed =
      linkedScore?.section === "context"
      && linkedScore.componentKey === componentKey
      && activeRunListSubFocusKey === subFocusKey;
    const className = `meta-pill subtle comparison-run-card-pill-button ${
      highlighted ? "comparison-linked-badge" : ""
    } ${
      isPressed ? "comparison-linked-badge-origin comparison-linked-subfocus" : ""
    }`.trim();
    if (!onDrillBackScoreLink || !panelRunId) {
      return (
        <span className={className} title={title}>
          {label}
        </span>
      );
    }
    return (
      <button
        aria-pressed={isPressed}
        className={className}
        onClick={() =>
          onDrillBackScoreLink("context", componentKey, {
            subFocusKey,
          })
        }
        ref={(node) => registerSubFocusRef?.(panelRunId, subFocusKey)(node)}
        title={title}
        type="button"
      >
        {label}
      </button>
    );
  };
  const highlightProvenance =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore ?? null, ["provenance_richness"], "context");
  const highlightBenchmarkStory =
    Boolean(linkedScore)
    && isComparisonScoreLinkMatch(linkedScore ?? null, ["benchmark_story_bonus"], "context");
  return (
    <div className="strategy-badges">
      {presetId ? (
        renderPill(
          `preset ${presetId}`,
          presetId,
          "provenance_richness",
          buildComparisonRunListLineSubFocusKey("experiment_preset"),
          highlightProvenance,
        )
      ) : null}
      {benchmarkFamily ? (
        renderPill(
          `benchmark ${benchmarkFamily}`,
          benchmarkFamily,
          "benchmark_story_bonus",
          buildComparisonRunListLineSubFocusKey("experiment_benchmark"),
          highlightBenchmarkStory,
        )
      ) : null}
      {datasetIdentity ? (
        renderPill(
          `dataset ${shortenIdentifier(datasetIdentity)}`,
          datasetIdentity,
          "provenance_richness",
          buildComparisonRunListLineSubFocusKey("experiment_dataset"),
          highlightProvenance,
        )
      ) : null}
      {tags.map((tag) => (
        <span key={tag}>
          {renderPill(
            `#${tag}`,
            tag,
            "benchmark_story_bonus",
            buildComparisonRunListLineSubFocusKey(`experiment_tag:${tag}`),
            highlightBenchmarkStory,
          )}
        </span>
      ))}
    </div>
  );
}

type RunListBoundarySurfaceContract = {
  eligibility: RunListBoundaryEligibility;
  group: RunListBoundaryGroupKey;
  label: string;
};

type RunListBoundaryGroupContract = {
  copy: string;
  eligibility: RunListBoundaryEligibility;
  surface_ids: RunListBoundarySurfaceId[];
  title: string;
};

function RunSurfaceCapabilityDiscoveryPanel({
  capabilities,
  compact = false,
}: {
  capabilities: RunSurfaceCapabilities | null;
  compact?: boolean;
}) {
  const contract = getRunListBoundaryContractSnapshot(capabilities?.comparison_eligibility_contract ?? null);
  const schemaContract = getRunSurfaceCapabilitySchemaContract(capabilities);
  const sharedContracts = getRunSurfaceSharedContracts(capabilities);
  const orderedFamilies = getRunSurfaceCapabilityFamilyOrder(capabilities)
    .map((familyKey) => getRunSurfaceCapabilityFamily(capabilities, familyKey))
    .filter((family): family is NonNullable<typeof family> => family !== null);
  const orderedGroups = getRunSurfaceCapabilityGroupOrder(capabilities).filter(
    (groupKey): groupKey is RunListBoundaryGroupKey => groupKey in contract.groups,
  );
  const schemaTitle = schemaContract?.title ?? "Run-surface capability contract";
  const schemaSummary =
    schemaContract?.summary
    ?? "Shared capability surface for comparison boundaries, strategy schema discovery, collection query discovery, provenance semantics, operational run controls, machine-readable policy enforcement, and surface-level enforcement rules.";
  const schemaVersion = schemaContract?.version ?? "run-surface-capabilities.v14";
  const runSubresourceSharedContracts = getRunSurfaceSubresourceContracts(capabilities);
  const collectionQueryContracts = getRunSurfaceCollectionQueryContracts(capabilities);

  return (
    <section className={`run-surface-capability-panel ${compact ? "compact" : ""}`.trim()}>
      <div className="run-surface-capability-head">
        <div>
          <p className="kicker">{compact ? "Schema discovery" : "Shared UI contract"}</p>
          <h3>{schemaTitle}</h3>
          <p className="run-note">{schemaSummary}</p>
        </div>
        <span className="meta-pill subtle">{schemaVersion}</span>
      </div>
      {collectionQueryContracts.length ? (
        <RunSurfaceCollectionQueryBuilder contracts={collectionQueryContracts} compact={compact} runtimeRuns={[]} />
      ) : null}
      {sharedContracts.length ? (
        <div className="run-surface-family-section">
          <span>Shared contracts</span>
          <div className="run-surface-family-rule-grid">
            {sharedContracts.map((sharedContract) => (
              <div className="run-surface-family-rule-card" key={sharedContract.contract_key}>
                <div className="run-surface-family-rule-head">
                  <strong>{sharedContract.title}</strong>
                  <span className="meta-pill subtle">{sharedContract.contract_kind}</span>
                </div>
                <p className="run-note">{sharedContract.summary}</p>
                <p className="run-note">
                  Source: {sharedContract.source_of_truth}
                </p>
                {sharedContract.discovery_flow ? (
                  <p className="run-note">
                    Discovery flow: {sharedContract.discovery_flow}
                  </p>
                ) : null}
                {sharedContract.version ? (
                  <p className="run-note">
                    Version: {sharedContract.version}
                  </p>
                ) : null}
                {sharedContract.policy ? (
                  <p className="run-note">
                    Policy: {sharedContract.policy.policy_key} · {sharedContract.policy.policy_mode}
                  </p>
                ) : null}
                {sharedContract.enforcement ? (
                  <p className="run-note">
                    Enforcement: {sharedContract.enforcement.level}
                  </p>
                ) : null}
                {sharedContract.ui_surfaces?.length ? (
                  <div className="run-surface-family-chip-row">
                    {sharedContract.ui_surfaces.map((surface) => (
                      <span
                        className="run-surface-family-chip"
                        key={`${sharedContract.contract_key}:ui:${surface}`}
                      >
                        {surface}
                      </span>
                    ))}
                  </div>
                ) : null}
                {sharedContract.schema_sources?.length ? (
                  <div className="run-surface-family-chip-row">
                    {sharedContract.schema_sources.map((source) => (
                      <span
                        className="run-surface-family-chip"
                        key={`${sharedContract.contract_key}:schema:${source}`}
                      >
                        {source}
                      </span>
                    ))}
                  </div>
                ) : null}
                {sharedContract.related_family_keys.length ? (
                  <div className="run-surface-family-chip-row">
                    {sharedContract.related_family_keys.map((familyKey) => (
                      <span className="run-surface-family-chip" key={`${sharedContract.contract_key}:${familyKey}`}>
                        {familyKey}
                      </span>
                    ))}
                  </div>
                ) : null}
                {sharedContract.member_keys.length ? (
                  <div className="run-surface-family-chip-row">
                    {sharedContract.member_keys.map((memberKey) => (
                      <span className="run-surface-family-chip" key={`${sharedContract.contract_key}:${memberKey}`}>
                        {memberKey}
                      </span>
                    ))}
                  </div>
                ) : null}
                {sharedContract.surface_rules?.length ? (
                  <div className="run-surface-family-chip-row">
                    {sharedContract.surface_rules.map((rule) => (
                      <span
                        className="run-surface-family-chip"
                        key={`${sharedContract.contract_key}:rule:${rule.rule_key}`}
                      >
                        {rule.surface_key}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {runSubresourceSharedContracts.length ? (
        <div className="run-surface-family-section">
          <span>Run subresource contracts</span>
          <div className="run-surface-family-rule-grid">
            {runSubresourceSharedContracts.map((sharedContract) => {
              const bodyKey =
                typeof sharedContract.schema_detail.body_key === "string"
                  ? sharedContract.schema_detail.body_key
                  : "unknown";
              const routeName =
                typeof sharedContract.schema_detail.route_name === "string"
                  ? sharedContract.schema_detail.route_name
                  : sharedContract.contract_key;
              const routePath =
                typeof sharedContract.schema_detail.route_path === "string"
                  ? sharedContract.schema_detail.route_path
                  : "unknown";
              const subresourceKey = sharedContract.contract_key.replace("subresource:", "");
              return (
                <div className="run-surface-family-rule-card" key={sharedContract.contract_key}>
                  <div className="run-surface-family-rule-head">
                    <strong>{sharedContract.title}</strong>
                    <span className="meta-pill subtle">{routeName}</span>
                  </div>
                  <p className="run-note">
                    Path: {routePath}
                  </p>
                  <p className="run-note">
                    Subresource: {subresourceKey} · Body: {bodyKey}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
      <div className="run-surface-family-grid">
        {orderedFamilies.map((family) => (
          <article className="run-surface-family-card" key={family.contract_key}>
            <div className="run-surface-family-head">
              <strong>{family.title}</strong>
              <span className="meta-pill subtle">{family.related_family_keys[0] ?? family.contract_key}</span>
            </div>
            <p className="run-note">{family.summary}</p>
            <p className="run-note">
              Discovery flow: {family.discovery_flow}
            </p>
            <div className="run-surface-family-section">
              <span>Shared UI</span>
              <div className="run-surface-family-chip-row">
                {family.ui_surfaces.map((surface) => (
                  <span className="run-surface-family-chip" key={surface}>
                    {surface}
                  </span>
                ))}
              </div>
            </div>
            <div className="run-surface-family-section">
              <span>Schema sources</span>
              <div className="run-surface-family-chip-row">
                {family.schema_sources.map((source) => (
                  <span className="run-surface-family-chip" key={source}>
                    {source}
                  </span>
                ))}
              </div>
            </div>
            <div className="run-surface-family-policy-grid">
              <div className="run-surface-family-section">
                <span>Policy</span>
                <div className="run-surface-family-policy-copy">
                  <strong>{family.policy.policy_key}</strong>
                  <p className="run-note">
                    Mode: {family.policy.policy_mode} · Source: {family.policy.source_of_truth}
                  </p>
                </div>
                <div className="run-surface-family-chip-row">
                  {family.policy.applies_to.map((target) => (
                    <span className="run-surface-family-chip" key={target}>
                      {target}
                    </span>
                  ))}
                </div>
              </div>
              <div className="run-surface-family-section">
                <span>Enforcement</span>
                <div className="run-surface-family-policy-copy">
                  <strong>{family.enforcement.level}</strong>
                  <p className="run-note">
                    Source: {family.enforcement.source_of_truth}
                  </p>
                  <p className="run-note">
                    Fallback: {family.enforcement.fallback_behavior}
                  </p>
                </div>
                <div className="run-surface-family-chip-row">
                  {family.enforcement.enforcement_points.map((point) => (
                    <span className="run-surface-family-chip" key={point}>
                      {point}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <div className="run-surface-family-section">
              <span>Surface rules</span>
              <div className="run-surface-family-rule-grid">
                {family.surface_rules.map((rule) => (
                  <div className="run-surface-family-rule-card" key={rule.rule_key}>
                    <div className="run-surface-family-rule-head">
                      <strong>{rule.surface_label}</strong>
                      <span className="meta-pill subtle">{rule.level}</span>
                    </div>
                    <p className="run-note">
                      Mode: {rule.enforcement_mode}
                    </p>
                    <p className="run-note">
                      Point: {rule.enforcement_point}
                    </p>
                    <p className="run-note">
                      Source: {rule.source_of_truth}
                    </p>
                    <p className="run-note">
                      Fallback: {rule.fallback_behavior}
                    </p>
                    <div className="run-surface-family-chip-row">
                      <span className="run-surface-family-chip">{rule.surface_key}</span>
                      <span className="run-surface-family-chip">{rule.rule_key}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>
      <div className="run-surface-capability-grid">
        {orderedGroups.map((groupKey) => (
          <RunListComparisonBoundaryNote contract={contract} groupKey={groupKey} key={groupKey} />
        ))}
      </div>
    </section>
  );
}

function Metric({
  buttonRef,
  className,
  interactivePressed,
  label,
  onClick,
  value,
}: {
  buttonRef?: (node: HTMLButtonElement | null) => void;
  className?: string;
  interactivePressed?: boolean;
  label: string;
  onClick?: () => void;
  value: string;
}) {
  const resolvedClassName = `metric-tile ${className ?? ""}`.trim();
  if (!onClick) {
    return (
      <div className={resolvedClassName}>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    );
  }
  return (
    <button
      aria-pressed={interactivePressed}
      className={`${resolvedClassName} comparison-run-summary-metric-button ${
        interactivePressed ? "comparison-linked-panel-origin comparison-linked-subfocus is-active" : ""
      }`.trim()}
      onClick={onClick}
      ref={buttonRef}
      type="button"
    >
      <span>{label}</span>
      <strong>{value}</strong>
    </button>
  );
}

function formatMetric(value?: number, suffix = "") {
  if (value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

function formatLineagePosture(value?: string | null) {
  if (!value) {
    return "unresolved";
  }
  return value.replace(/-/g, " ");
}

function formatLineageIndicator(value?: string | null) {
  if (!value) {
    return "review";
  }
  return value;
}

function formatComparisonScoreValue(value: number) {
  return value.toFixed(2).replace(/\.?0+$/, "");
}

function buildComparisonScoreHighlights(
  section: "metrics" | "semantics" | "context",
  components: Record<string, { score: number; [key: string]: unknown }>,
) {
  return Object.entries(components)
    .filter(([, component]) => component.score > 0)
    .sort((left, right) => right[1].score - left[1].score)
    .slice(0, 3)
    .map(([key, component]) => formatComparisonScoreHighlight(section, key, component));
}

function buildComparisonScoreDetailRows(
  section: "metrics" | "semantics" | "context",
  components: Record<string, { score: number; [key: string]: unknown }>,
) {
  return Object.entries(components)
    .sort((left, right) => {
      if (right[1].score !== left[1].score) {
        return right[1].score - left[1].score;
      }
      return formatComparisonScoreComponentLabel(section, left[0]).localeCompare(
        formatComparisonScoreComponentLabel(section, right[0]),
      );
    })
    .map(([key, component]) => ({
      key,
      label: formatComparisonScoreComponentLabel(section, key),
      score: component.score,
      details: buildComparisonScoreComponentDetails(section, key, component),
    }));
}

function formatComparisonScoreHighlight(
  section: "metrics" | "semantics" | "context",
  key: string,
  component: { score: number; [key: string]: unknown },
) {
  const label = formatComparisonScoreComponentLabel(section, key);
  const detail = formatComparisonScoreComponentDetail(section, key, component);
  const score = formatComparisonScoreValue(component.score);
  return detail ? `${label} ${score} (${detail})` : `${label} ${score}`;
}

function formatComparisonScoreComponentLabel(
  section: "metrics" | "semantics" | "context",
  key: string,
) {
  const labels: Record<string, string> = {
    total_return_pct: "Return delta",
    max_drawdown_pct: "Drawdown delta",
    win_rate_pct: "Win-rate delta",
    trade_count: "Trade-flow delta",
    strategy_kind: "Strategy kind",
    execution_model: "Execution model",
    source_descriptor: "Source descriptor",
    parameter_contract: "Parameter contract",
    vocabulary: "Vocabulary richness",
    provenance_richness: "Provenance richness",
    native_reference_bonus: "Native/reference bonus",
    reference_bonus: "Reference bonus",
    status_bonus: "Status split",
    benchmark_story_bonus: "Benchmark story",
    reference_floor: "Reference floor",
  };
  return labels[key] ?? `${section} ${key.replace(/_/g, " ")}`;
}

function formatComparisonScoreLinkSourceLabel(source: ComparisonScoreLinkSource) {
  switch (source) {
    case "metric":
      return "metric table";
    case "overview":
      return "overview card";
    case "provenance":
      return "provenance panel";
    case "run_card":
      return "run card";
    case "run_list":
      return "run list";
    case "drillback":
    default:
      return "drill-back";
  }
}

function encodeComparisonScoreLinkToken(value: string) {
  return encodeURIComponent(value);
}

function decodeComparisonScoreLinkToken(value: string) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function buildComparisonProvenanceLineSubFocusKey(key: string) {
  return `provenance-line:${encodeComparisonScoreLinkToken(key)}`;
}

function buildComparisonRunCardLineSubFocusKey(key: string) {
  return `run-card-line:${encodeComparisonScoreLinkToken(key)}`;
}

function buildComparisonRunListLineSubFocusKey(key: string) {
  return `run-list-line:${encodeComparisonScoreLinkToken(key)}`;
}

function buildComparisonRunListOrderPreviewSubFocusKey(orderId: string, fieldKey: string) {
  return buildComparisonRunListLineSubFocusKey(
    `order_preview:${encodeComparisonScoreLinkToken(orderId)}:${fieldKey}`,
  );
}

function buildComparisonRunListDataSymbolSubFocusKey(symbol: string, fieldKey: string) {
  return buildComparisonRunListLineSubFocusKey(
    `data_symbol:${encodeComparisonScoreLinkToken(symbol)}:${fieldKey}`,
  );
}

function buildComparisonProvenanceArtifactSubFocusKey(path: string) {
  return `provenance-artifact:${encodeComparisonScoreLinkToken(path)}`;
}

function buildComparisonProvenanceArtifactSectionSubFocusKey(path: string, sectionKey: string) {
  return `provenance-artifact-section:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(sectionKey)}`;
}

function buildComparisonProvenanceArtifactSummaryHoverKey(path: string, summaryKey: string) {
  return `provenance-artifact-summary:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(summaryKey)}`;
}

function buildComparisonProvenanceArtifactSectionLineHoverKey(
  path: string,
  sectionKey: string,
  lineIndex: number,
) {
  return `provenance-artifact-section-line:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(
    sectionKey,
  )}:${lineIndex}`;
}

function buildComparisonProvenanceArtifactLineDetailHoverKey(
  path: string,
  sectionKey: string,
  lineIndex: number,
  targetKey: string,
) {
  return `provenance-artifact-line-detail:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(
    sectionKey,
  )}:${lineIndex}:${encodeComparisonScoreLinkToken(targetKey)}`;
}

function buildComparisonMetricTooltipKey(metricKey: string, runId: string) {
  return `metric-tooltip:${encodeComparisonScoreLinkToken(metricKey)}:${encodeComparisonScoreLinkToken(runId)}`;
}

function formatComparisonScoreLinkSubFocusLabel(subFocusKey: string | null) {
  if (!subFocusKey) {
    return null;
  }
  const semanticLineLabels: Record<string, string> = {
    data_boundary: "Boundary state",
    experiment_benchmark: "Benchmark family",
    experiment_dataset: "Dataset identity",
    experiment_preset: "Preset",
    data_candles: "Candles",
    data_lineage_action: "Lineage action",
    data_lineage_assessment: "Lineage assessment",
    data_lineage: "Data lineage",
    data_lineage_posture: "Lineage posture",
    data_dataset_identity: "Dataset identity",
    data_effective_window: "Effective window",
    data_issues: "Issues",
    data_last_sync: "Last sync",
    data_provider: "Provider",
    data_requested_window: "Requested window",
    data_repro: "Reproducibility",
    data_rerun_boundary: "Rerun boundary",
    data_rerun_source: "Rerun source",
    data_rerun_status: "Rerun status",
    data_rerun_target: "Rerun target",
    data_rerun_validation: "Validation summary",
    data_sync: "Sync status",
    data_sync_checkpoint: "Sync checkpoint",
    data_timeframe: "Timeframe",
    execution_model: "Execution model",
    max_drawdown_pct: "Drawdown",
    operator_notes: "Operator notes",
    order_canceled: "Canceled orders",
    order_filled: "Filled orders",
    order_open: "Open orders",
    order_partial: "Partial fills",
    order_rejected: "Rejected orders",
    order_sync: "Order sync",
    parameter_contract: "Parameter contract",
    provenance_richness: "Artifact inventory",
    reference_note: "Reference note",
    runtime_heartbeat: "Heartbeat",
    runtime_last_heartbeat: "Last heartbeat",
    runtime_last_processed_candle: "Last processed candle",
    runtime_last_recovery: "Last recovery",
    runtime_last_seen_candle: "Last seen candle",
    runtime_primed_bars: "Primed bars",
    runtime_recoveries: "Recoveries",
    runtime_recovery_reason: "Recovery reason",
    runtime_session: "Runtime session",
    runtime_started: "Started",
    runtime_state: "Lifecycle state",
    runtime_ticks: "Processed ticks",
    semantic_source: "Semantic source",
    status: "Status",
    source_descriptor: "Source descriptor",
    strategy_entrypoint: "Entrypoint",
    strategy_registered: "Registered",
    strategy_requested_params: "Requested params",
    strategy_resolved_params: "Resolved params",
    strategy_kind: "Semantic kind",
    strategy_supported_timeframes: "Supported timeframes",
    strategy_version_lineage: "Version lineage",
    total_return_pct: "Return",
    trade_count: "Trade flow",
    vocabulary: "Vocabulary",
    working_directory: "Working dir",
    win_rate_pct: "Win rate",
  };
  if (subFocusKey.startsWith("provenance-line:")) {
    const lineKey = decodeComparisonScoreLinkToken(subFocusKey.slice("provenance-line:".length));
    const labels: Record<string, string> = {
      ...semanticLineLabels,
      command: "Command",
      homepage: "Homepage",
      reference_id: "Reference ID",
    };
    return labels[lineKey] ?? lineKey.replace(/_/g, " ");
  }
  if (subFocusKey.startsWith("run-card-line:")) {
    const lineKey = decodeComparisonScoreLinkToken(subFocusKey.slice("run-card-line:".length));
    return semanticLineLabels[lineKey] ?? lineKey.replace(/_/g, " ");
  }
  if (subFocusKey.startsWith("run-list-line:")) {
    const lineKey = decodeComparisonScoreLinkToken(subFocusKey.slice("run-list-line:".length));
    if (lineKey.startsWith("experiment_tag:")) {
      return `Experiment tag #${lineKey.slice("experiment_tag:".length)}`;
    }
    if (lineKey.startsWith("order_preview:")) {
      const [, encodedOrderId = "", fieldKey = "detail"] = lineKey.split(":");
      const orderId = decodeComparisonScoreLinkToken(encodedOrderId);
      const orderFieldLabels: Record<string, string> = {
        avg_fill: "Avg fill",
        filled: "Filled",
        instrument: "Instrument",
        qty: "Quantity",
        remain: "Remaining",
        side: "Side",
        synced: "Synced",
        updated: "Updated",
      };
      return `${shortenIdentifier(orderId)} / ${orderFieldLabels[fieldKey] ?? fieldKey.replace(/_/g, " ")}`;
    }
    if (lineKey.startsWith("data_symbol:")) {
      const [, encodedSymbol = "", fieldKey = "detail"] = lineKey.split(":");
      const symbol = decodeComparisonScoreLinkToken(encodedSymbol);
      const dataSymbolLabels: Record<string, string> = {
        candles: "Candles",
        dataset_identity: "Dataset identity",
        issues: "Issues",
        last_sync: "Last sync",
        provider: "Provider",
        repro: "Reproducibility",
        sync: "Sync status",
        sync_checkpoint: "Sync checkpoint",
        window: "Window",
      };
      return `${symbol} / ${dataSymbolLabels[fieldKey] ?? fieldKey.replace(/_/g, " ")}`;
    }
    return semanticLineLabels[lineKey] ?? lineKey.replace(/_/g, " ");
  }
  if (subFocusKey.startsWith("provenance-artifact-section:")) {
    const [, encodedPath = "", encodedSection = ""] = subFocusKey.split(":");
    const path = decodeComparisonScoreLinkToken(encodedPath);
    const sectionKey = decodeComparisonScoreLinkToken(encodedSection);
    return `${shortenIdentifier(path)} / ${formatBenchmarkArtifactSectionLabel(sectionKey)}`;
  }
  if (subFocusKey.startsWith("provenance-artifact:")) {
    const path = decodeComparisonScoreLinkToken(subFocusKey.slice("provenance-artifact:".length));
    return shortenIdentifier(path);
  }
  return subFocusKey;
}

function formatComparisonScoreLinkTooltipLabel(tooltipKey: string | null) {
  if (!tooltipKey) {
    return null;
  }
  if (tooltipKey.startsWith("metric-tooltip:")) {
    const [, encodedMetricKey = "", encodedRunId = ""] = tooltipKey.split(":");
    return `${formatComparisonScoreComponentLabel("metrics", decodeComparisonScoreLinkToken(encodedMetricKey))} tooltip on ${shortenIdentifier(
      decodeComparisonScoreLinkToken(encodedRunId),
    )}`;
  }
  return tooltipKey;
}

function formatComparisonScoreLinkArtifactHoverLabel(artifactHoverKey: string | null) {
  if (!artifactHoverKey) {
    return null;
  }
  if (artifactHoverKey.startsWith("provenance-artifact-summary:")) {
    const [, encodedPath = "", encodedSummary = ""] = artifactHoverKey.split(":");
    const path = decodeComparisonScoreLinkToken(encodedPath);
    const summaryKey = decodeComparisonScoreLinkToken(encodedSummary);
    return `${shortenIdentifier(path)} / ${formatBenchmarkArtifactSummaryLabel(summaryKey)}`;
  }
  if (artifactHoverKey.startsWith("provenance-artifact-section-line:")) {
    const [, encodedPath = "", encodedSection = "", lineIndex = "0"] = artifactHoverKey.split(":");
    const path = decodeComparisonScoreLinkToken(encodedPath);
    const sectionKey = decodeComparisonScoreLinkToken(encodedSection);
    const numericLineIndex = Number.parseInt(lineIndex, 10);
    return `${shortenIdentifier(path)} / ${formatBenchmarkArtifactSectionLabel(sectionKey)} / line ${
      Number.isFinite(numericLineIndex) ? numericLineIndex + 1 : "?"
    }`;
  }
  return artifactHoverKey;
}

function formatComparisonScoreLinkArtifactLineDetailViewLabel(
  artifactLineDetailView: ProvenanceArtifactLineDetailView | null,
) {
  if (artifactLineDetailView === "stats") {
    return "stats lens";
  }
  if (artifactLineDetailView === "context") {
    return "context lens";
  }
  return null;
}

function formatComparisonScoreLinkArtifactLineMicroViewLabel(
  artifactLineMicroView: ProvenanceArtifactLineMicroView | null,
) {
  if (artifactLineMicroView === "structure") {
    return "structure micro-view";
  }
  if (artifactLineMicroView === "signal") {
    return "signal micro-view";
  }
  if (artifactLineMicroView === "note") {
    return "note micro-view";
  }
  return null;
}

function formatComparisonScoreLinkArtifactLineDetailHoverLabel(
  artifactLineDetailHoverKey: string | null,
) {
  if (!artifactLineDetailHoverKey) {
    return null;
  }
  if (artifactLineDetailHoverKey.startsWith("provenance-artifact-line-detail:")) {
    const [, encodedPath = "", encodedSection = "", lineIndex = "0", encodedTarget = ""] =
      artifactLineDetailHoverKey.split(":");
    const path = decodeComparisonScoreLinkToken(encodedPath);
    const sectionKey = decodeComparisonScoreLinkToken(encodedSection);
    const targetKey = decodeComparisonScoreLinkToken(encodedTarget);
    const numericLineIndex = Number.parseInt(lineIndex, 10);
    return `${shortenIdentifier(path)} / ${formatBenchmarkArtifactSectionLabel(sectionKey)} / line ${
      Number.isFinite(numericLineIndex) ? numericLineIndex + 1 : "?"
    } / ${targetKey.replace(/_/g, " ")}`;
  }
  return artifactLineDetailHoverKey;
}

function formatComparisonScoreComponentDetail(
  section: "metrics" | "semantics" | "context",
  key: string,
  component: { score: number; [key: string]: unknown },
) {
  if (section === "metrics" && typeof component.delta === "number") {
    return `delta ${formatComparisonScoreSignedValue(component.delta)}`;
  }
  if (section === "semantics" && key === "vocabulary") {
    const changedKeys = Array.isArray(component.changed_keys) ? component.changed_keys.length : 0;
    if (changedKeys > 0) {
      return `${changedKeys} changed key${changedKeys === 1 ? "" : "s"}`;
    }
  }
  if (
    section === "semantics"
    && key === "provenance_richness"
    && typeof component.units === "number"
  ) {
    return `${formatComparisonScoreValue(component.units)} units`;
  }
  if (typeof component.applied === "boolean") {
    return component.applied ? "applied" : "inactive";
  }
  return "";
}

function buildComparisonScoreComponentDetails(
  section: "metrics" | "semantics" | "context",
  key: string,
  component: { score: number; [key: string]: unknown },
) {
  const details: string[] = [];
  if (section === "metrics") {
    if (typeof component.delta === "number") {
      details.push(`Delta ${formatComparisonScoreSignedValue(component.delta)}`);
    }
    if (typeof component.effective_delta === "number") {
      details.push(`Effective ${formatComparisonScoreValue(component.effective_delta)}`);
    }
    if (typeof component.weight === "number") {
      details.push(`Weight ${formatComparisonScoreValue(component.weight)}`);
    }
    return details;
  }

  if (section === "semantics" && key === "vocabulary") {
    const changedKeys = Array.isArray(component.changed_keys)
      ? component.changed_keys.map((item) => String(item))
      : [];
    if (changedKeys.length) {
      details.push(`Changed keys: ${changedKeys.join(", ")}`);
    }
    if (typeof component.schema_richness_delta === "number") {
      details.push(`Schema delta ${formatComparisonScoreValue(component.schema_richness_delta)}`);
    }
  }

  if (section === "semantics" && key === "provenance_richness") {
    if (typeof component.baseline_units === "number" && typeof component.target_units === "number") {
      details.push(
        `Units ${formatComparisonScoreValue(component.baseline_units)} -> ${formatComparisonScoreValue(component.target_units)}`,
      );
    }
  }

  if ("baseline" in component || "target" in component) {
    const baseline = formatComparisonScoreComponentRawValue(component.baseline);
    const target = formatComparisonScoreComponentRawValue(component.target);
    if (baseline || target) {
      details.push(`Baseline ${baseline || "n/a"} -> Target ${target || "n/a"}`);
    }
  }

  if (typeof component.units === "number") {
    details.push(`Units ${formatComparisonScoreValue(component.units)}`);
  }
  if (typeof component.capped_units === "number") {
    details.push(`Capped ${formatComparisonScoreValue(component.capped_units)}`);
  }
  if (typeof component.weight === "number") {
    details.push(`Weight ${formatComparisonScoreValue(component.weight)}`);
  }
  if (typeof component.applied === "boolean") {
    details.push(component.applied ? "Applied" : "Inactive");
  }
  return details;
}

function formatComparisonScoreComponentRawValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "";
  }
  if (typeof value === "number") {
    return formatComparisonScoreValue(value);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (Array.isArray(value)) {
    return value
      .map((item): string => formatComparisonScoreComponentRawValue(item))
      .filter(Boolean)
      .join(", ");
  }
  return String(value);
}

function formatComparisonScoreSignedValue(value: number) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${formatComparisonScoreValue(value)}`;
}

function getComparisonScoreLinkedRunRole(
  selection: ComparisonScoreLinkTarget | null,
  baselineRunId: string,
  runId: string,
): ComparisonScoreLinkedRunRole | null {
  if (!selection) {
    return null;
  }
  if (runId === selection.narrativeRunId) {
    return "target";
  }
  if (runId === baselineRunId) {
    return "baseline";
  }
  return null;
}

function isSameComparisonScoreLinkTarget(
  left: ComparisonScoreLinkTarget | null,
  right: ComparisonScoreLinkTarget | null,
) {
  if (left === right) {
    return true;
  }
  if (!left || !right) {
    return false;
  }
  return (
    left.detailExpanded === right.detailExpanded
    && left.artifactDetailExpanded === right.artifactDetailExpanded
    && left.artifactLineDetailExpanded === right.artifactLineDetailExpanded
    && left.artifactLineDetailView === right.artifactLineDetailView
    && left.artifactLineMicroView === right.artifactLineMicroView
    && left.artifactLineNotePage === right.artifactLineNotePage
    && left.artifactLineDetailHoverKey === right.artifactLineDetailHoverKey
    && left.artifactLineDetailScrubStep === right.artifactLineDetailScrubStep
    && left.narrativeRunId === right.narrativeRunId
    && left.section === right.section
    && left.componentKey === right.componentKey
    && left.source === right.source
    && left.originRunId === right.originRunId
    && left.subFocusKey === right.subFocusKey
    && left.tooltipKey === right.tooltipKey
    && left.artifactHoverKey === right.artifactHoverKey
  );
}

function isSameComparisonScoreLinkSurface(
  left: ComparisonScoreLinkTarget | null,
  right: ComparisonScoreLinkTarget | null,
) {
  if (left === right) {
    return true;
  }
  if (!left || !right) {
    return false;
  }
  return (
    left.narrativeRunId === right.narrativeRunId
    && left.section === right.section
    && left.componentKey === right.componentKey
    && left.source === right.source
    && left.originRunId === right.originRunId
    && left.subFocusKey === right.subFocusKey
  );
}

function resolveComparisonScoreDrillBackTarget(
  comparison: RunComparison,
  selection: ComparisonScoreLinkTarget | null,
  runId: string,
  section: ComparisonScoreSection,
  componentKey: string,
): ComparisonScoreLinkTarget | null {
  const narrativeSupportsComponent = (narrative: RunComparison["narratives"][number]) =>
    Object.prototype.hasOwnProperty.call(narrative.score_breakdown[section].components, componentKey);

  if (runId !== comparison.baseline_run_id) {
    const directNarrative = comparison.narratives.find(
      (narrative) => narrative.run_id === runId && narrativeSupportsComponent(narrative),
    );
    return directNarrative
      ? {
          componentKey,
          detailExpanded: null,
          artifactDetailExpanded: null,
          artifactLineDetailExpanded: null,
          artifactLineDetailView: null,
          artifactLineMicroView: null,
          artifactLineNotePage: null,
          artifactLineDetailHoverKey: null,
          artifactLineDetailScrubStep: null,
          narrativeRunId: directNarrative.run_id,
          originRunId: null,
          section,
          source: "drillback",
          subFocusKey: null,
          tooltipKey: null,
          artifactHoverKey: null,
        }
      : null;
  }

  const selectedNarrative =
    selection
      ? comparison.narratives.find(
          (narrative) =>
            narrative.run_id === selection.narrativeRunId && narrativeSupportsComponent(narrative),
        ) ?? null
      : null;
  const primaryNarrative =
    comparison.narratives.find(
      (narrative) => narrative.is_primary && narrativeSupportsComponent(narrative),
    ) ?? null;
  const fallbackNarrative = comparison.narratives.find(narrativeSupportsComponent) ?? null;
  const resolvedNarrative = selectedNarrative ?? primaryNarrative ?? fallbackNarrative;

  return resolvedNarrative
    ? {
        componentKey,
        detailExpanded: null,
        artifactDetailExpanded: null,
        artifactLineDetailExpanded: null,
        artifactLineDetailView: null,
        artifactLineMicroView: null,
        artifactLineNotePage: null,
        artifactLineDetailHoverKey: null,
        artifactLineDetailScrubStep: null,
        narrativeRunId: resolvedNarrative.run_id,
        originRunId: null,
        section,
        source: "drillback",
        subFocusKey: null,
        tooltipKey: null,
        artifactHoverKey: null,
      }
    : null;
}

function isComparisonScoreLinkMatch(
  selection: ComparisonScoreLinkTarget | null,
  componentKeys: string[],
  section?: ComparisonScoreSection,
) {
  return Boolean(
    selection
    && (!section || selection.section === section)
    && componentKeys.includes(selection.componentKey),
  );
}

function formatEditableNumber(value: number) {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(8).replace(/\.?0+$/, "");
}

function formatFixedNumber(value?: number | null) {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return value.toFixed(8);
}

function buildLiveOrderDraftKey(runId: string, orderId: string) {
  return `${runId}:${orderId}`;
}

function formatComparisonMetric(value: number | null | undefined, unit: string) {
  if (value === null || value === undefined) {
    return "n/a";
  }
  if (unit === "pct") {
    return `${value}%`;
  }
  return String(value);
}

function formatComparisonDelta(value: number | null | undefined, unit: string) {
  if (value === null || value === undefined) {
    return "delta n/a";
  }
  const prefix = value > 0 ? "+" : "";
  if (unit === "pct") {
    return `${prefix}${value}% vs baseline`;
  }
  return `${prefix}${value} vs baseline`;
}

function formatComparisonNarrativeLabel(value: string) {
  switch (value) {
    case "native_vs_reference":
      return "Native vs reference";
    case "reference_vs_reference":
      return "Reference vs reference";
    case "native_vs_native":
      return "Native vs native";
    default:
      return "Run divergence";
  }
}

function formatComparisonIntentLabel(value: ComparisonIntent) {
  switch (value) {
    case "benchmark_validation":
      return "Benchmark validation";
    case "execution_regression":
      return "Execution regression";
    case "strategy_tuning":
      return "Strategy tuning";
    default:
      return value;
  }
}

function formatComparisonIntentLegend(value: ComparisonIntent) {
  switch (value) {
    case "benchmark_validation":
      return "Benchmark drift cues";
    case "execution_regression":
      return "Regression risk cues";
    case "strategy_tuning":
      return "Tuning edge cues";
    default:
      return value;
  }
}

function formatComparisonIntentTooltip(value: ComparisonIntent) {
  switch (value) {
    case "benchmark_validation":
      return "Benchmark validation emphasizes drift from the reference benchmark. Cyan cues point to where native results confirm or diverge from the benchmark.";
    case "execution_regression":
      return "Execution regression emphasizes operational drift and regression risk. Ember cues point to where behavior degraded or recovered versus the control run.";
    case "strategy_tuning":
      return "Strategy tuning emphasizes optimization edge and tradeoffs. Green cues point to where parameter changes improved or hurt the candidate run.";
    default:
      return value;
  }
}

function formatComparisonCueTooltip(
  intent: ComparisonIntent,
  cue: ComparisonCueKind,
  metricLabel?: string,
) {
  switch (cue) {
    case "mode":
      return formatComparisonIntentTooltip(intent);
    case "baseline":
      switch (intent) {
        case "benchmark_validation":
          return "This baseline run anchors benchmark validation. Read the other runs as benchmark drift versus this control.";
        case "execution_regression":
          return "This baseline run is the control execution. Read the other runs as regression or recovery against it.";
        case "strategy_tuning":
          return "This baseline run is the incumbent tuning point. Read the other runs as edge or penalty against it.";
        default:
          return "This run is the comparison baseline.";
      }
    case "best":
      switch (intent) {
        case "benchmark_validation":
          return `${metricLabel ?? "This metric"} is highlighted because it shows the strongest observed outcome here. In validation mode, treat it as benchmark evidence rather than an automatic winner.`;
        case "execution_regression":
          return `${metricLabel ?? "This metric"} is highlighted because it shows the strongest observed outcome here. In regression mode, use it to spot recovered or degraded execution behavior quickly.`;
        case "strategy_tuning":
          return `${metricLabel ?? "This metric"} is highlighted because it shows the strongest observed outcome here. In tuning mode, use it to spot candidate improvements and tradeoffs quickly.`;
        default:
          return `${metricLabel ?? "This metric"} is highlighted because it is the strongest observed outcome in this row.`;
      }
    case "insight":
      switch (intent) {
        case "benchmark_validation":
          return "The featured insight summarizes the most important benchmark drift to inspect first.";
        case "execution_regression":
          return "The featured insight summarizes the sharpest regression signal to inspect first.";
        case "strategy_tuning":
          return "The featured insight summarizes the most actionable tuning edge or penalty first.";
        default:
          return "This is the primary comparison insight.";
      }
    default:
      return formatComparisonIntentTooltip(intent);
  }
}

function buildComparisonCellTooltip(
  intent: ComparisonIntent,
  metricLabel: string,
  isBaseline: boolean,
  isBest: boolean,
) {
  const messages: string[] = [];

  if (isBaseline) {
    messages.push(formatComparisonCueTooltip(intent, "baseline"));
  }

  if (isBest) {
    messages.push(formatComparisonCueTooltip(intent, "best", metricLabel));
  }

  return messages.join(" ");
}

function getComparisonIntentClassName(value: ComparisonIntent) {
  return `comparison-intent-${value.replaceAll("_", "-")}`;
}

function formatLaneLabel(runtime: string) {
  switch (runtime) {
    case "freqtrade_reference":
      return "reference";
    case "decision_engine":
      return "decision";
    default:
      return runtime;
  }
}

function formatVersionLineage(versionLineage: string[], fallbackVersion: string) {
  const values = versionLineage.length ? versionLineage : [fallbackVersion];
  return values.join(" -> ");
}

function extractDefaultParameters(schema: ParameterSchema) {
  return Object.fromEntries(
    Object.entries(schema)
      .filter(([, definition]) => definition.default !== undefined)
      .map(([name, definition]) => [name, definition.default]),
  );
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

function summarizeRunNotes(notes: string[]) {
  if (!notes.length) {
    return "No notes recorded.";
  }
  if (notes.length === 1) {
    return notes[0];
  }
  return `${notes[0]} | Final: ${notes[notes.length - 1]} | ${notes.length} notes`;
}

export {
  PanelDisclosure,
  BackfillCountStatus,
  BackfillQualityStatus,
  SyncCheckpointStatus,
  SyncFailureStatus,
  formatCompletion,
  summarizeGapWindows,
  formatGapWindows,
  buildLegacyGapWindowKey,
  buildGapWindowKey,
  parseGapWindowKey,
  formatGapWindowKeyLabel,
  normalizeExpandedGapWindowSelectionList,
  resolveGapWindowSelectionList,
  buildGapWindowSelectionUpdate,
  isSameGapWindowSelectionList,
  filterExpandedGapWindowSelections,
  buildGapWindowSelectionLookup,
  instrumentGapRowKey,
  toggleExpandedGapRow,
  pruneExpandedGapRows,
  pruneExpandedGapWindowSelections,
  loadExpandedGapRows,
  loadExpandedGapWindowSelections,
  defaultControlRoomComparisonSelectionState,
  loadPersistedComparisonSelection,
  defaultComparisonHistoryPanelState,
  defaultComparisonHistoryPanelUiState,
  loadPersistedComparisonHistoryPanelUiState,
  loadControlRoomUiState,
  readControlRoomUiStateValue,
  persistControlRoomUiState,
  loadComparisonHistorySyncAuditTrail,
  persistComparisonHistorySyncAuditTrail,
  loadComparisonSelectionFromUrl,
  buildComparisonSelectionHistoryUrl,
  readComparisonHistoryBrowserState,
  buildComparisonHistoryBrowserState,
  isSameComparisonHistoryBrowserState,
  persistComparisonSelectionToUrl,
  buildComparisonHistoryEntryId,
  buildComparisonHistoryTabId,
  formatComparisonHistoryTabLabel,
  loadComparisonHistoryTabIdentity,
  buildComparisonHistoryPanelSyncState,
  buildComparisonHistorySyncSignature,
  buildComparisonHistorySyncAuditId,
  buildComparisonHistoryPanelEntry,
  findComparisonHistoryPanelEntryForSelection,
  mergeComparisonHistoryPanelState,
  mergeComparisonHistoryPanelEntries,
  reconcileComparisonHistoryPanelState,
  sortComparisonHistoryPanelEntries,
  limitComparisonHistoryPanelEntries,
  normalizeComparisonHistoryPanelUiState,
  normalizeComparisonHistorySyncAuditFilter,
  normalizeComparisonHistoryPanelSyncState,
  normalizeComparisonHistoryPanelState,
  normalizeComparisonHistoryPanelEntry,
  normalizeComparisonHistorySyncAuditEntry,
  normalizeComparisonHistorySyncConflictReview,
  normalizeComparisonHistorySyncConflictSelectedSources,
  normalizeComparisonHistorySyncPreferenceReview,
  normalizeComparisonHistorySyncWorkspaceReview,
  normalizeComparisonHistorySyncPreferenceState,
  normalizeComparisonHistorySyncWorkspaceState,
  normalizeComparisonHistorySyncPreferenceSelectedSources,
  normalizeComparisonHistorySyncWorkspaceSelectedSources,
  limitComparisonHistorySyncAuditEntries,
  appendComparisonHistorySyncAuditEntries,
  isSameComparisonHistoryPanelState,
  isSameComparisonHistoryPanelSyncState,
  isSameComparisonHistoryPanelEntry,
  getComparisonHistoryPanelEntryChangedFields,
  formatComparisonHistorySyncConflictScoreLinkValue,
  formatComparisonHistorySyncConflictRunSelectionValue,
  formatComparisonHistorySyncConflictFieldValue,
  hasComparisonHistorySyncConflictFieldDifference,
  buildDefaultComparisonHistorySyncConflictSelectedSources,
  buildComparisonHistorySyncConflictReview,
  buildComparisonHistorySyncConflictReviewGroups,
  summarizeComparisonHistoryPanelEntryConflict,
  formatComparisonHistorySyncConflictResolutionSummary,
  resolveComparisonHistorySyncConflictReviewEntry,
  applyResolvedComparisonHistoryPanelEntry,
  summarizeComparisonHistorySyncPreferenceChanges,
  buildComparisonHistorySyncPreferenceState,
  formatComparisonHistorySyncPreferenceFieldValue,
  hasComparisonHistorySyncPreferenceFieldDifference,
  buildDefaultComparisonHistorySyncPreferenceSelectedSources,
  buildComparisonHistorySyncPreferenceReview,
  buildComparisonHistorySyncPreferenceReviewRows,
  formatComparisonHistorySyncPreferenceResolutionSummary,
  resolveComparisonHistorySyncPreferenceReview,
  listComparisonHistoryExpandedGapRowKeys,
  listComparisonHistoryExpandedGapRowDiffKeys,
  buildComparisonHistoryExpandedGapRowSelectionKey,
  parseComparisonHistoryExpandedGapRowSelectionKey,
  buildComparisonHistoryExpandedGapWindowSelectionKey,
  parseComparisonHistoryExpandedGapWindowSelectionKey,
  listComparisonHistoryExpandedGapWindowDiffKeys,
  isSameComparisonHistoryExpandedGapRows,
  isSameExpandedGapWindowSelections,
  formatComparisonHistoryExpandedGapRowKey,
  formatComparisonHistoryExpandedGapRowsValue,
  formatComparisonHistoryExpandedGapRowsDiffValue,
  formatComparisonHistorySyncWorkspaceSelectionKeyLabel,
  rankComparisonHistorySyncWorkspaceSelectionKey,
  listComparisonHistorySyncWorkspaceDiffSelectionKeys,
  resolveComparisonHistorySyncWorkspaceFieldSource,
  listComparisonHistorySyncWorkspaceConflictSelectionKeys,
  scoreComparisonHistorySyncWorkspaceCandidateSource,
  sortComparisonHistorySyncWorkspaceSemanticSignals,
  rankComparisonHistorySyncWorkspaceFieldSemantics,
  buildComparisonHistorySyncWorkspaceRecommendedSources,
  summarizeComparisonHistorySyncWorkspaceChanges,
  buildComparisonHistorySyncWorkspaceState,
  formatComparisonHistorySyncWorkspaceFieldValue,
  hasComparisonHistorySyncWorkspaceFieldDifference,
  buildDefaultComparisonHistorySyncWorkspaceSelectedSources,
  buildComparisonHistorySyncWorkspaceReview,
  buildComparisonHistorySyncWorkspaceReviewRows,
  buildComparisonHistorySyncWorkspaceRecommendationOverview,
  formatComparisonHistorySyncWorkspaceResolutionSummary,
  resolveComparisonHistorySyncWorkspaceReview,
  buildComparisonHistorySyncAuditEntries,
  loadLegacyExpandedGapRows,
  filterExpandedGapRows,
  normalizeControlRoomComparisonSelection,
  isSameComparisonSelection,
  formatComparisonHistoryPanelEntryMeta,
  matchesComparisonHistoryPanelEntry,
  formatComparisonHistorySyncAuditKindLabel,
  buildComparisonHistoryStepDescriptor,
  resolveComparisonHistoryRunLabel,
  normalizeComparisonRunIdList,
  normalizeComparisonIntent,
  normalizeComparisonScoreSection,
  normalizeComparisonScoreLinkSource,
  normalizeComparisonScoreLinkSubFocusKey,
  normalizeComparisonScoreLinkExpandedState,
  normalizeComparisonScoreLinkTooltipKey,
  normalizeComparisonScoreLinkArtifactLineDetailView,
  normalizeComparisonScoreLinkArtifactLineMicroView,
  normalizeComparisonScoreLinkArtifactLineNotePage,
  normalizeComparisonScoreLinkArtifactLineDetailHoverKey,
  normalizeComparisonScoreLinkArtifactLineScrubStep,
  normalizeComparisonScoreLinkArtifactHoverKey,
  normalizeComparisonScoreLinkTarget,
  isControlRoomUiStateV1,
  isControlRoomUiStateV2,
  isControlRoomUiStateV3,
  isControlRoomUiStateV4,
  buildRunsPath,
  buildRunComparisonPath,
  normalizeRunHistoryFilter,
  defaultRunHistoryFilter,
  sanitizeRunHistoryFilter,
  cloneRunHistoryFilter,
  hasRunHistoryFilterCriteria,
  areRunHistoryFiltersEquivalent,
  buildRunHistorySavedFilterStorageKey,
  normalizeRunHistoryPresetFilter,
  loadSavedRunHistoryFilterPresets,
  persistSavedRunHistoryFilterPresets,
  describeRunHistoryFilter,
  DEFAULT_COMPARISON_INTENT,
  comparisonIntentOptions,
  getStrategyVersionOptions,
  pickLatestBenchmarkRun,
  StrategyColumn,
  ReferenceCatalog,
  PresetStructuredDiffPreview,
  PresetCatalogPanel,
  RunForm,
  ExperimentMetadataPills,
  RunSurfaceCapabilityDiscoveryPanel,
  Metric,
  formatMetric,
  formatLineagePosture,
  formatLineageIndicator,
  formatComparisonScoreValue,
  buildComparisonScoreHighlights,
  buildComparisonScoreDetailRows,
  formatComparisonScoreHighlight,
  formatComparisonScoreComponentLabel,
  formatComparisonScoreLinkSourceLabel,
  encodeComparisonScoreLinkToken,
  decodeComparisonScoreLinkToken,
  buildComparisonProvenanceLineSubFocusKey,
  buildComparisonRunCardLineSubFocusKey,
  buildComparisonRunListLineSubFocusKey,
  buildComparisonRunListOrderPreviewSubFocusKey,
  buildComparisonRunListDataSymbolSubFocusKey,
  buildComparisonProvenanceArtifactSubFocusKey,
  buildComparisonProvenanceArtifactSectionSubFocusKey,
  buildComparisonProvenanceArtifactSummaryHoverKey,
  buildComparisonProvenanceArtifactSectionLineHoverKey,
  buildComparisonProvenanceArtifactLineDetailHoverKey,
  buildComparisonMetricTooltipKey,
  formatComparisonScoreLinkSubFocusLabel,
  formatComparisonScoreLinkTooltipLabel,
  formatComparisonScoreLinkArtifactHoverLabel,
  formatComparisonScoreLinkArtifactLineDetailViewLabel,
  formatComparisonScoreLinkArtifactLineMicroViewLabel,
  formatComparisonScoreLinkArtifactLineDetailHoverLabel,
  formatComparisonScoreComponentDetail,
  buildComparisonScoreComponentDetails,
  formatComparisonScoreComponentRawValue,
  formatComparisonScoreSignedValue,
  getComparisonScoreLinkedRunRole,
  isSameComparisonScoreLinkTarget,
  isSameComparisonScoreLinkSurface,
  resolveComparisonScoreDrillBackTarget,
  isComparisonScoreLinkMatch,
  formatEditableNumber,
  formatFixedNumber,
  buildLiveOrderDraftKey,
  formatComparisonMetric,
  formatComparisonDelta,
  formatComparisonNarrativeLabel,
  formatComparisonIntentLabel,
  formatComparisonIntentLegend,
  formatComparisonIntentTooltip,
  formatComparisonCueTooltip,
  buildComparisonCellTooltip,
  getComparisonIntentClassName,
  formatLaneLabel,
  formatVersionLineage,
  extractDefaultParameters,
  formatParameterMap,
  formatParameterValue,
  summarizeRunNotes,
  formatTimestamp,
  formatProviderRecoverySchema,
  formatProviderRecoveryTelemetry,
  shortenIdentifier,
  truncateLabel,
  formatRange,
  benchmarkArtifactSummaryOrder,
  benchmarkArtifactSummaryLabels,
  benchmarkArtifactSectionOrder,
  benchmarkArtifactSectionLabels,
  formatBenchmarkArtifactSummaryEntries,
  benchmarkArtifactSummarySortIndex,
  formatBenchmarkArtifactSummaryLabel,
  formatBenchmarkArtifactSummaryValue,
  formatBenchmarkArtifactSectionEntries,
  benchmarkArtifactSectionSortIndex,
  formatBenchmarkArtifactSectionLabel,
  formatBenchmarkArtifactSectionLines,
  formatBenchmarkArtifactSectionValue,
  formatBenchmarkArtifactInlineValue
};
export type {
  ComparisonHistorySyncWorkspaceSemanticRanking,
  RunListBoundarySurfaceContract,
  RunListBoundaryGroupContract
};
