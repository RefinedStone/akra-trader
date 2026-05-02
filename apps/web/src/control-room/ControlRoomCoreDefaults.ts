// @ts-nocheck

import { CSSProperties, FormEvent, KeyboardEvent, MouseEvent, PointerEvent, ReactNode, forwardRef, useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState, AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION, AKRA_TOUCH_FEEDBACK_EVENT_NAME, AkraTouchFeedbackDetail, AkraTouchFeedbackEnvelope, triggerAkraTouchFeedbackBridge, WorkspaceShell, buildControlWorkspaceDescriptors, ControlWorkspaceDescriptor, ControlStripMetric, useWorkspaceRoute, WorkspaceRouteContent, buildRunHistoryWorkspacePanels, LiveOrderReplacementDraft, RunHistoryWorkspaceSectionProps, RunOrderControls, getRunListBoundaryContractSnapshot, getRunListBoundarySurfaceLabel, getRunSurfaceCapabilityFamily, getRunSurfaceCapabilityFamilyOrder, getRunSurfaceCapabilityGroupOrder, getRunSurfaceCapabilitySchemaContract, getRunSurfaceCollectionQueryContracts, getRunSurfaceSharedContracts, getRunSurfaceSubresourceContracts, RunListComparisonBoundaryNote, shouldEnableReferenceProvenanceSemantics, shouldEnableRunListMetricDrillBack, shouldEnableRunSnapshotSemantics, shouldEnableStrategyCatalogSchemaHints, shouldHydratePresetParameterDefaults, shouldRenderOrderActionBoundaryNote, shouldRenderWorkflowControlBoundaryNote, RunSurfaceCollectionQueryBuilder, formatComparisonTooltipTuningDelta, formatComparisonTooltipTuningValue, formatRelativeTimestampLabel, RunSection, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateSample, applyProviderProvenanceSchedulerStitchedReportGovernancePlan, applyProviderProvenanceSchedulerNarrativeGovernancePlan, approveProviderProvenanceSchedulerStitchedReportGovernancePlan, approveProviderProvenanceSchedulerNarrativeGovernancePlan, createProviderProvenanceAnalyticsPreset, createProviderProvenanceDashboardView, createProviderProvenanceExportJob, createProviderProvenanceSchedulerStitchedReportGovernanceRegistry, createProviderProvenanceSchedulerStitchedReportGovernancePlan, createProviderProvenanceSchedulerStitchedReportView, createProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy, createProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, createProviderProvenanceSchedulerNarrativeGovernancePlan, createProviderProvenanceSchedulerNarrativeRegistryEntry, createProviderProvenanceSchedulerNarrativeTemplate, createProviderProvenanceScheduledReport, approveProviderProvenanceExportJob, applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, deleteProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, deleteProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, deleteProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, deleteProviderProvenanceSchedulerNarrativeRegistryEntry, deleteProviderProvenanceSchedulerStitchedReportView, deleteProviderProvenanceSchedulerNarrativeTemplate, createProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob, downloadProviderProvenanceExportJob, downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob, escalateProviderProvenanceExportJob, exportProviderProvenanceSchedulerHealth, exportProviderProvenanceSchedulerStitchedNarrativeReport, reconstructProviderProvenanceSchedulerHealthExport, exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, fetchJson, getProviderProvenanceExportAnalytics, getProviderProvenanceExportJobHistory, getProviderProvenanceSchedulerHealthAnalytics, getProviderProvenanceScheduledReportHistory, getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory, listProviderProvenanceAnalyticsPresets, listProviderProvenanceDashboardViews, listProviderProvenanceSchedulerStitchedReportViews, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisions, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogs, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisions, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplates, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisions, listProviderProvenanceSchedulerNarrativeGovernancePlans, listProviderProvenanceSchedulerNarrativeRegistryEntries, listProviderProvenanceSchedulerNarrativeRegistryRevisions, listProviderProvenanceSchedulerNarrativeTemplates, listProviderProvenanceSchedulerNarrativeTemplateRevisions, listProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogs, listProviderProvenanceSchedulerStitchedReportGovernancePolicyTemplates, listProviderProvenanceSchedulerStitchedReportGovernancePlans, rollbackProviderProvenanceSchedulerStitchedReportGovernancePlan, rollbackProviderProvenanceSchedulerNarrativeGovernancePlan, listMarketDataIngestionJobs, listMarketDataLineageHistory, listProviderProvenanceExportJobs, listProviderProvenanceSchedulerAlertHistory, listProviderProvenanceSchedulerHealthHistory, listProviderProvenanceSchedulerStitchedReportGovernanceRegistries, listProviderProvenanceSchedulerStitchedReportGovernanceRegistryAudits, listProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisions, listProviderProvenanceSchedulerStitchedReportViewAudits, listProviderProvenanceSchedulerStitchedReportViewRevisions, getProviderProvenanceSchedulerSearchDashboard, bulkGovernProviderProvenanceSchedulerSearchModerationPolicyCatalogs, bulkGovernProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies, createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicy, createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, listProviderProvenanceSchedulerSearchModerationPolicyCatalogs, listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies, listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisions, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePlans, listProviderProvenanceSchedulerSearchModerationPolicyCatalogAudits, listProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisions, listProviderProvenanceSchedulerSearchModerationPlans, listProviderProvenanceScheduledReports, listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs, listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, approveProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, approveProviderProvenanceSchedulerSearchModerationPlan, applyProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, applyProviderProvenanceSchedulerSearchModerationPlan, createProviderProvenanceSchedulerSearchModerationPolicyCatalog, deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, deleteProviderProvenanceSchedulerSearchModerationPolicyCatalog, moderateProviderProvenanceSchedulerSearchFeedbackBatch, moderateProviderProvenanceSchedulerSearchFeedback, pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs, pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, recordProviderProvenanceSchedulerSearchFeedback, resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRevision, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevision, restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevision, restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogRevision, restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevision, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevision, restoreProviderProvenanceSchedulerNarrativeRegistryRevision, restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevision, restoreProviderProvenanceSchedulerStitchedReportViewRevision, restoreProviderProvenanceSchedulerNarrativeTemplateRevision, revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, runProviderProvenanceSchedulerNarrativeGovernancePlanBatchAction, runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkGovernance, runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkGovernance, runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkGovernance, stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, stageProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, stageProviderProvenanceSchedulerSearchModerationPlan, updateProviderProvenanceSchedulerSearchModerationPolicyCatalog, updateProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, runDueProviderProvenanceScheduledReports, runProviderProvenanceScheduledReport, updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep, updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, updateProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, updateProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, updateProviderProvenanceSchedulerNarrativeRegistryEntry, updateProviderProvenanceSchedulerStitchedReportGovernanceRegistry, updateProviderProvenanceSchedulerStitchedReportView, updateProviderProvenanceSchedulerNarrativeTemplate, updateProviderProvenanceExportJobPolicy, deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistry, ALL_FILTER_VALUE, apiBase, COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM, COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM, COMPARISON_FOCUS_DETAIL_SEARCH_PARAM, COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM, COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM, COMPARISON_FOCUS_SECTION_SEARCH_PARAM, COMPARISON_FOCUS_SOURCE_SEARCH_PARAM, COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM, COMPARISON_HISTORY_BROWSER_STATE_KEY, COMPARISON_HISTORY_BROWSER_STATE_VERSION, COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY, COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION, COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS, COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS, COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS, COMPARISON_HISTORY_TAB_ID_SESSION_KEY, COMPARISON_INTENT_SEARCH_PARAM, COMPARISON_RUN_ID_SEARCH_PARAM, COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY, COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION, COMPARISON_TOOLTIP_TUNING_GROUPS, COMPARISON_TOOLTIP_TUNING_LABELS, COMPARISON_TOOLTIP_TUNING_SHARE_PARAM, COMPARISON_TOOLTIP_TUNING_STORAGE_KEY, COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION, COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD, CONTROL_ROOM_UI_STATE_STORAGE_KEY, CONTROL_ROOM_UI_STATE_VERSION, DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY, DEFAULT_COMPARISON_TOOLTIP_TUNING, DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE, LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY, MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY, MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION, MAX_COMPARISON_HISTORY_PANEL_ENTRIES, MAX_COMPARISON_HISTORY_SYNC_AUDIT_ENTRIES, MAX_COMPARISON_RUNS, MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS, MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES, MAX_VISIBLE_GAP_WINDOWS, PRESET_PROFILE_AGGRESSIVENESS_RANKS, PRESET_PROFILE_CONFIDENCE_RANKS, PRESET_PROFILE_SPEED_RANKS, PRESET_TIMEFRAME_UNIT_TO_MINUTES, REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM, REPLAY_INTENT_ALIAS_SEARCH_PARAM, REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM, REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM, REPLAY_INTENT_SCOPE_SEARCH_PARAM, REPLAY_INTENT_SEARCH_PARAM, REPLAY_INTENT_STEP_SEARCH_PARAM, REPLAY_INTENT_TEMPLATE_SEARCH_PARAM, RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY, SHOW_COMPARISON_TOOLTIP_TUNING_PANEL, TOUCH_GAP_WINDOW_SWEEP_HOLD_MS, TOUCH_GAP_WINDOW_SWEEP_MOVE_TOLERANCE_PX, BenchmarkArtifact, ParameterSchema, ComparisonCueKind, ComparisonHistoryBrowserState, ComparisonHistoryPanelEntry, ComparisonHistoryPanelState, ComparisonHistoryPanelSyncState, ComparisonHistoryStepDescriptor, ComparisonHistorySyncAuditEntry, ComparisonHistorySyncAuditFilter, ComparisonHistorySyncAuditKind, ComparisonHistorySyncAuditTrailState, ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource, ComparisonHistorySyncConflictReview, ComparisonHistorySyncConflictReviewGroup, ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncPreferenceReview, ComparisonHistorySyncPreferenceReviewRow, ComparisonHistorySyncPreferenceState, ComparisonHistorySyncWorkspaceRecommendationOverview, ComparisonHistorySyncWorkspaceReview, ComparisonHistorySyncWorkspaceReviewRow, ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncWorkspaceSemanticSignal, ComparisonHistorySyncWorkspaceSignalDetailNestedKey, ComparisonHistorySyncWorkspaceSignalDetailSubviewKey, ComparisonHistorySyncWorkspaceSignalMicroInteractionKey, ComparisonHistorySyncWorkspaceSignalMicroViewKey, ComparisonHistorySyncWorkspaceState, ComparisonHistoryTabIdentity, ComparisonHistoryWriteMode, ComparisonIntent, ComparisonScoreDrillBackOptions, ComparisonScoreLinkedRunRole, ComparisonScoreLinkSource, ComparisonScoreLinkTarget, ComparisonScoreSection, ComparisonTooltipConflictSessionSummary, ComparisonTooltipConflictSessionSummarySession, ComparisonTooltipConflictSessionUiState, ComparisonTooltipConflictUiStateV1, ComparisonTooltipInteractionOptions, ComparisonTooltipLayout, ComparisonTooltipPendingPresetImportConflict, ComparisonTooltipPresetConflictPreviewGroup, ComparisonTooltipPresetConflictPreviewRow, ComparisonTooltipPresetImportConflictPolicy, ComparisonTooltipPresetImportResolution, ComparisonTooltipTargetProps, ComparisonTooltipTuning, ComparisonTooltipTuningPresetStateV1, ComparisonTooltipTuningShareImport, ComparisonTooltipTuningSinglePresetShareV1, ControlRoomComparisonHistoryPanelUiState, ControlRoomComparisonSelectionState, ControlRoomUiStateV1, ControlRoomUiStateV2, ControlRoomUiStateV3, ControlRoomUiStateV4, ExpandedGapWindowSelections, ExperimentPreset, ExperimentPresetRevision, GapWindowDragSelectionState, GuardedLiveStatus, MarketDataIngestionJobRecord, MarketDataProvenanceExportFilterState, MarketDataProvenanceExportHistoryEntry, MarketDataProvenanceExportSort, MarketDataProvenanceExportStateV1, MarketDataLineageHistoryRecord, MarketDataStatus, OperatorAlertMarketContextProvenance, OperatorAlertPrimaryFocus, OperatorVisibility, PendingTouchGapWindowSweepState, PresetDraftConflict, PresetRevisionDiff, PresetRevisionFilterState, PresetStructuredDiffDeltaValue, PresetStructuredDiffGroup, PresetStructuredDiffRow, ProviderProvenanceAnalyticsPresetEntry, ProviderProvenanceDashboardLayout, ProviderProvenanceDashboardViewEntry, ProviderProvenanceExportAnalyticsPayload, ProviderProvenanceExportJobEntry, ProviderProvenanceExportJobEscalationResult, ProviderProvenanceExportJobHistoryPayload, ProviderProvenanceExportJobPolicyResult, ProviderProvenanceSchedulerAlertHistoryPayload, ProviderProvenanceSchedulerHealthExportPayload, ProviderProvenanceSchedulerHealthAnalyticsPayload, ProviderProvenanceSchedulerHealthHistoryPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ProviderProvenanceSchedulerSearchModerationPlanListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload, ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult, ProviderProvenanceSchedulerSearchDashboardPayload, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload, ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ProviderProvenanceSchedulerStitchedReportViewEntry, ProviderProvenanceSchedulerStitchedReportViewRevisionEntry, ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload, ProviderProvenanceSchedulerNarrativeBulkGovernanceResult, ProviderProvenanceSchedulerNarrativeGovernancePlan, ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult, ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ProviderProvenanceSchedulerNarrativeGovernanceQueueView, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload, ProviderProvenanceSchedulerNarrativeRegistryEntry, ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry, ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload, ProviderProvenanceSchedulerNarrativeTemplateEntry, ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload, ProviderProvenanceScheduledReportEntry, ProviderProvenanceScheduledReportHistoryPayload, ProvenanceArtifactLineDetailView, ProvenanceArtifactLineMicroView, ReferenceSource, Run, RunComparison, RunHistoryFilter, RunHistorySurfaceKey, RunListBoundaryContract, RunListBoundaryEligibility, RunListBoundaryGroupKey, RunListBoundarySurfaceId, RunSurfaceCapabilities, RunSurfaceCapabilityFamily, RunSurfaceCapabilityFamilyContract, RunSurfaceCapabilityFamilyKey, RunSurfaceCapabilitySchemaContract, RunSurfaceCapabilitySurfaceKey, RunSurfaceCollectionQueryBuilderReplayIntentSnapshot, RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload, RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy, RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload, RunSurfaceCollectionQueryContract, RunSurfaceCollectionQueryElementField, RunSurfaceCollectionQueryExpressionAuthoring, RunSurfaceCollectionQueryParameterDomainDescriptor, RunSurfaceCollectionQuerySchema, RunSurfaceSharedContract, RunSurfaceSubresourceContract, SavedRunHistoryFilterPreset, SavedRunHistoryFilterPresetStateV1, Strategy, TouchGapWindowActivationFeedbackState, TouchGapWindowHoldProgressState } from "./ControlRoomCoreHelpersContext";

export const defaultRunForm = {
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

export const defaultPresetForm = {
  name: "",
  preset_id: "",
  description: "",
  strategy_id: "",
  timeframe: "5m",
  benchmark_family: "",
  tags_text: "",
  parameters_text: "",
};

export const defaultPresetRevisionFilter: PresetRevisionFilterState = {
  action: "all",
  query: "",
};

export const defaultMarketDataProvenanceExportFilterState: MarketDataProvenanceExportFilterState = {
  provider: ALL_FILTER_VALUE,
  vendor_field: ALL_FILTER_VALUE,
  search_query: "",
  sort: "newest",
};

export type ProviderProvenanceAnalyticsScope = "current_focus" | "all_focuses";
export type ProviderProvenanceSchedulerOccurrenceNarrativeFacet =
  | "all_occurrences"
  | "resolved_narratives"
  | "post_resolution_recovery"
  | "recurring_occurrences";

export type ProviderProvenanceAnalyticsQueryState = {
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

export type ProviderProvenanceSchedulerSearchDashboardFilterState = {
  search: string;
  moderation_status: string;
  signal: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft = {
  name: string;
  description: string;
  default_moderation_status: string;
  governance_view: string;
  window_days: number;
  stale_pending_hours: number;
  minimum_score: number;
  require_note: boolean;
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilterState = {
  catalog_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

export type ProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft = {
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

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft = {
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

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilterState = {
  governance_policy_id: string;
  action: string;
  actor_tab_id: string;
  search: string;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft = {
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

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft = {
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

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState = {
  queue_state: string;
  meta_policy_id: string;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft = {
  action: string;
  meta_policy_id: string;
  note: string;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState = {
  queue_state: string;
  governance_policy_id: string;
};

export type ProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft = {
  action: string;
  governance_policy_id: string;
  note: string;
};

export type ProviderProvenanceSchedulerSearchModerationQueueFilterState = {
  queue_state: string;
  policy_catalog_id: string;
};

export type ProviderProvenanceSchedulerSearchModerationStageDraft = {
  policy_catalog_id: string;
  moderation_status: string;
  note: string;
};

export type ProviderProvenanceSchedulerExportPolicyDraft = {
  job_id: string | null;
  routing_policy_id: string;
  approval_policy_id: string;
  delivery_targets: string[];
  approval_note: string;
};

export type OperatorVisibilityAlertEntry =
  | OperatorVisibility["alerts"][number]
  | OperatorVisibility["alert_history"][number];

export const defaultProviderProvenanceAnalyticsQueryState: ProviderProvenanceAnalyticsQueryState = {
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

export const defaultProviderProvenanceSchedulerSearchDashboardFilterState: ProviderProvenanceSchedulerSearchDashboardFilterState = {
  search: "",
  moderation_status: ALL_FILTER_VALUE,
  signal: ALL_FILTER_VALUE,
  governance_view: "all_feedback",
  window_days: 30,
  stale_pending_hours: 24,
};

export const defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft: ProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft = {
  name: "",
  description: "",
  default_moderation_status: "approved",
  governance_view: "pending_queue",
  window_days: 30,
  stale_pending_hours: 24,
  minimum_score: 0,
  require_note: false,
};

export const defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilterState = {
  catalog_id: "",
  action: ALL_FILTER_VALUE,
  actor_tab_id: "",
  search: "",
};

export const defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft: ProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft = {
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

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft = {
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

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilterState = {
  governance_policy_id: "",
  action: ALL_FILTER_VALUE,
  actor_tab_id: "",
  search: "",
};

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft = {
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

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft = {
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

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState = {
  queue_state: "pending_approval",
  meta_policy_id: ALL_FILTER_VALUE,
};

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft = {
  action: "update",
  meta_policy_id: ALL_FILTER_VALUE,
  note: "",
};

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState = {
  queue_state: "pending_approval",
  governance_policy_id: ALL_FILTER_VALUE,
};

export const defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft = {
  action: "update",
  governance_policy_id: ALL_FILTER_VALUE,
  note: "",
};

export const defaultProviderProvenanceSchedulerSearchModerationQueueFilterState: ProviderProvenanceSchedulerSearchModerationQueueFilterState = {
  queue_state: "pending_approval",
  policy_catalog_id: ALL_FILTER_VALUE,
};

export const defaultProviderProvenanceSchedulerSearchModerationStageDraft: ProviderProvenanceSchedulerSearchModerationStageDraft = {
  policy_catalog_id: ALL_FILTER_VALUE,
  moderation_status: "approved",
  note: "",
};

export function normalizeProviderProvenanceSchedulerRoutingPolicyDraftValue(policyId?: string | null) {
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

export function normalizeProviderProvenanceSchedulerApprovalPolicyDraftValue(policyId?: string | null) {
  return policyId === "manual_required" ? "manual_required" : "auto";
}

export function buildProviderProvenanceSchedulerExportPolicyDraft(
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

export function getProviderProvenanceSchedulerNarrativeGovernanceQueuePriorityRank(
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

export function getProviderProvenanceSchedulerNarrativeGovernanceQueueState(
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

export function formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(
  steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[],
) {
  if (!steps.length) {
    return "No reusable hierarchy captured.";
  }
  return `${steps.length} step(s): ${steps
    .map((step) => `${formatWorkflowToken(step.item_type)} ${step.item_ids.length}`)
    .join(" · ")}`;
}

export function formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(
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

export function formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(
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

export function isProviderProvenanceSchedulerAlertCategory(category?: string | null) {
  return category === "scheduler_lag" || category === "scheduler_failure";
}

export function getOperatorAlertOccurrenceKey(
  alert: Pick<
    OperatorVisibilityAlertEntry,
    "occurrence_id" | "alert_id" | "status" | "detected_at" | "resolved_at"
  >,
) {
  return alert.occurrence_id ?? `${alert.alert_id}:${alert.status}:${alert.detected_at}:${alert.resolved_at ?? "active"}`;
}

export function formatProviderProvenanceSchedulerTimelineSummary(
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

export function formatProviderProvenanceSchedulerSearchMatchSummary(
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

export function formatProviderProvenanceSchedulerRetrievalClusterSummary(
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

export function buildProviderProvenanceSchedulerAlertWorkflowReason(
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
