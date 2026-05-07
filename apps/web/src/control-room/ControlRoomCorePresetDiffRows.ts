// @ts-nocheck

import { CSSProperties, FormEvent, KeyboardEvent, MouseEvent, PointerEvent, ReactNode, forwardRef, useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState, AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION, AKRA_TOUCH_FEEDBACK_EVENT_NAME, AkraTouchFeedbackDetail, AkraTouchFeedbackEnvelope, triggerAkraTouchFeedbackBridge, WorkspaceShell, buildControlWorkspaceDescriptors, ControlWorkspaceDescriptor, ControlStripMetric, useWorkspaceRoute, WorkspaceRouteContent, buildRunHistoryWorkspacePanels, LiveOrderReplacementDraft, RunHistoryWorkspaceSectionProps, RunOrderControls, getRunListBoundaryContractSnapshot, getRunListBoundarySurfaceLabel, getRunSurfaceCapabilityFamily, getRunSurfaceCapabilityFamilyOrder, getRunSurfaceCapabilityGroupOrder, getRunSurfaceCapabilitySchemaContract, getRunSurfaceCollectionQueryContracts, getRunSurfaceSharedContracts, getRunSurfaceSubresourceContracts, RunListComparisonBoundaryNote, shouldEnableStrategyProvenanceSemantics, shouldEnableRunListMetricDrillBack, shouldEnableRunSnapshotSemantics, shouldEnableStrategyCatalogSchemaHints, shouldHydratePresetParameterDefaults, shouldRenderOrderActionBoundaryNote, shouldRenderWorkflowControlBoundaryNote, RunSurfaceCollectionQueryBuilder, formatComparisonTooltipTuningDelta, formatComparisonTooltipTuningValue, formatRelativeTimestampLabel, RunSection, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateSample, applyProviderProvenanceSchedulerStitchedReportGovernancePlan, applyProviderProvenanceSchedulerNarrativeGovernancePlan, approveProviderProvenanceSchedulerStitchedReportGovernancePlan, approveProviderProvenanceSchedulerNarrativeGovernancePlan, createProviderProvenanceAnalyticsPreset, createProviderProvenanceDashboardView, createProviderProvenanceExportJob, createProviderProvenanceSchedulerStitchedReportGovernanceRegistry, createProviderProvenanceSchedulerStitchedReportGovernancePlan, createProviderProvenanceSchedulerStitchedReportView, createProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy, createProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, createProviderProvenanceSchedulerNarrativeGovernancePlan, createProviderProvenanceSchedulerNarrativeRegistryEntry, createProviderProvenanceSchedulerNarrativeTemplate, createProviderProvenanceScheduledReport, approveProviderProvenanceExportJob, applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, deleteProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, deleteProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, deleteProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, deleteProviderProvenanceSchedulerNarrativeRegistryEntry, deleteProviderProvenanceSchedulerStitchedReportView, deleteProviderProvenanceSchedulerNarrativeTemplate, createProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob, downloadProviderProvenanceExportJob, downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob, escalateProviderProvenanceExportJob, exportProviderProvenanceSchedulerHealth, exportProviderProvenanceSchedulerStitchedNarrativeReport, reconstructProviderProvenanceSchedulerHealthExport, exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, fetchJson, getProviderProvenanceExportAnalytics, getProviderProvenanceExportJobHistory, getProviderProvenanceSchedulerHealthAnalytics, getProviderProvenanceScheduledReportHistory, getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory, listProviderProvenanceAnalyticsPresets, listProviderProvenanceDashboardViews, listProviderProvenanceSchedulerStitchedReportViews, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisions, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogs, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisions, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplates, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisions, listProviderProvenanceSchedulerNarrativeGovernancePlans, listProviderProvenanceSchedulerNarrativeRegistryEntries, listProviderProvenanceSchedulerNarrativeRegistryRevisions, listProviderProvenanceSchedulerNarrativeTemplates, listProviderProvenanceSchedulerNarrativeTemplateRevisions, listProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogs, listProviderProvenanceSchedulerStitchedReportGovernancePolicyTemplates, listProviderProvenanceSchedulerStitchedReportGovernancePlans, rollbackProviderProvenanceSchedulerStitchedReportGovernancePlan, rollbackProviderProvenanceSchedulerNarrativeGovernancePlan, listMarketDataIngestionJobs, listMarketDataLineageHistory, listProviderProvenanceExportJobs, listProviderProvenanceSchedulerAlertHistory, listProviderProvenanceSchedulerHealthHistory, listProviderProvenanceSchedulerStitchedReportGovernanceRegistries, listProviderProvenanceSchedulerStitchedReportGovernanceRegistryAudits, listProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisions, listProviderProvenanceSchedulerStitchedReportViewAudits, listProviderProvenanceSchedulerStitchedReportViewRevisions, getProviderProvenanceSchedulerSearchDashboard, bulkGovernProviderProvenanceSchedulerSearchModerationPolicyCatalogs, bulkGovernProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies, createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicy, createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, listProviderProvenanceSchedulerSearchModerationPolicyCatalogs, listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies, listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisions, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePlans, listProviderProvenanceSchedulerSearchModerationPolicyCatalogAudits, listProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisions, listProviderProvenanceSchedulerSearchModerationPlans, listProviderProvenanceScheduledReports, listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs, listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, approveProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, approveProviderProvenanceSchedulerSearchModerationPlan, applyProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, applyProviderProvenanceSchedulerSearchModerationPlan, createProviderProvenanceSchedulerSearchModerationPolicyCatalog, deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, deleteProviderProvenanceSchedulerSearchModerationPolicyCatalog, moderateProviderProvenanceSchedulerSearchFeedbackBatch, moderateProviderProvenanceSchedulerSearchFeedback, pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs, pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, recordProviderProvenanceSchedulerSearchFeedback, resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRevision, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevision, restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevision, restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogRevision, restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevision, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevision, restoreProviderProvenanceSchedulerNarrativeRegistryRevision, restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevision, restoreProviderProvenanceSchedulerStitchedReportViewRevision, restoreProviderProvenanceSchedulerNarrativeTemplateRevision, revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, runProviderProvenanceSchedulerNarrativeGovernancePlanBatchAction, runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkGovernance, runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkGovernance, runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkGovernance, stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, stageProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, stageProviderProvenanceSchedulerSearchModerationPlan, updateProviderProvenanceSchedulerSearchModerationPolicyCatalog, updateProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, runDueProviderProvenanceScheduledReports, runProviderProvenanceScheduledReport, updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep, updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, updateProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, updateProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, updateProviderProvenanceSchedulerNarrativeRegistryEntry, updateProviderProvenanceSchedulerStitchedReportGovernanceRegistry, updateProviderProvenanceSchedulerStitchedReportView, updateProviderProvenanceSchedulerNarrativeTemplate, updateProviderProvenanceExportJobPolicy, deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistry, ALL_FILTER_VALUE, apiBase, COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM, COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM, COMPARISON_FOCUS_DETAIL_SEARCH_PARAM, COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM, COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM, COMPARISON_FOCUS_SECTION_SEARCH_PARAM, COMPARISON_FOCUS_SOURCE_SEARCH_PARAM, COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM, COMPARISON_HISTORY_BROWSER_STATE_KEY, COMPARISON_HISTORY_BROWSER_STATE_VERSION, COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY, COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION, COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS, COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS, COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS, COMPARISON_HISTORY_TAB_ID_SESSION_KEY, COMPARISON_INTENT_SEARCH_PARAM, COMPARISON_RUN_ID_SEARCH_PARAM, COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY, COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION, COMPARISON_TOOLTIP_TUNING_GROUPS, COMPARISON_TOOLTIP_TUNING_LABELS, COMPARISON_TOOLTIP_TUNING_SHARE_PARAM, COMPARISON_TOOLTIP_TUNING_STORAGE_KEY, COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION, COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD, CONTROL_ROOM_UI_STATE_STORAGE_KEY, CONTROL_ROOM_UI_STATE_VERSION, DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY, DEFAULT_COMPARISON_TOOLTIP_TUNING, DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE, LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY, MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY, MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION, MAX_COMPARISON_HISTORY_PANEL_ENTRIES, MAX_COMPARISON_HISTORY_SYNC_AUDIT_ENTRIES, MAX_COMPARISON_RUNS, MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS, MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES, MAX_VISIBLE_GAP_WINDOWS, PRESET_PROFILE_AGGRESSIVENESS_RANKS, PRESET_PROFILE_CONFIDENCE_RANKS, PRESET_PROFILE_SPEED_RANKS, PRESET_TIMEFRAME_UNIT_TO_MINUTES, REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM, REPLAY_INTENT_ALIAS_SEARCH_PARAM, REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM, REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM, REPLAY_INTENT_SCOPE_SEARCH_PARAM, REPLAY_INTENT_SEARCH_PARAM, REPLAY_INTENT_STEP_SEARCH_PARAM, REPLAY_INTENT_TEMPLATE_SEARCH_PARAM, RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY, SHOW_COMPARISON_TOOLTIP_TUNING_PANEL, TOUCH_GAP_WINDOW_SWEEP_HOLD_MS, TOUCH_GAP_WINDOW_SWEEP_MOVE_TOLERANCE_PX, BenchmarkArtifact, ParameterSchema, ComparisonCueKind, ComparisonHistoryBrowserState, ComparisonHistoryPanelEntry, ComparisonHistoryPanelState, ComparisonHistoryPanelSyncState, ComparisonHistoryStepDescriptor, ComparisonHistorySyncAuditEntry, ComparisonHistorySyncAuditFilter, ComparisonHistorySyncAuditKind, ComparisonHistorySyncAuditTrailState, ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource, ComparisonHistorySyncConflictReview, ComparisonHistorySyncConflictReviewGroup, ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncPreferenceReview, ComparisonHistorySyncPreferenceReviewRow, ComparisonHistorySyncPreferenceState, ComparisonHistorySyncWorkspaceRecommendationOverview, ComparisonHistorySyncWorkspaceReview, ComparisonHistorySyncWorkspaceReviewRow, ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncWorkspaceSemanticSignal, ComparisonHistorySyncWorkspaceSignalDetailNestedKey, ComparisonHistorySyncWorkspaceSignalDetailSubviewKey, ComparisonHistorySyncWorkspaceSignalMicroInteractionKey, ComparisonHistorySyncWorkspaceSignalMicroViewKey, ComparisonHistorySyncWorkspaceState, ComparisonHistoryTabIdentity, ComparisonHistoryWriteMode, ComparisonIntent, ComparisonScoreDrillBackOptions, ComparisonScoreLinkedRunRole, ComparisonScoreLinkSource, ComparisonScoreLinkTarget, ComparisonScoreSection, ComparisonTooltipConflictSessionSummary, ComparisonTooltipConflictSessionSummarySession, ComparisonTooltipConflictSessionUiState, ComparisonTooltipConflictUiStateV1, ComparisonTooltipInteractionOptions, ComparisonTooltipLayout, ComparisonTooltipPendingPresetImportConflict, ComparisonTooltipPresetConflictPreviewGroup, ComparisonTooltipPresetConflictPreviewRow, ComparisonTooltipPresetImportConflictPolicy, ComparisonTooltipPresetImportResolution, ComparisonTooltipTargetProps, ComparisonTooltipTuning, ComparisonTooltipTuningPresetStateV1, ComparisonTooltipTuningShareImport, ComparisonTooltipTuningSinglePresetShareV1, ControlRoomComparisonHistoryPanelUiState, ControlRoomComparisonSelectionState, ControlRoomUiStateV1, ControlRoomUiStateV2, ControlRoomUiStateV3, ControlRoomUiStateV4, ExpandedGapWindowSelections, ExperimentPreset, ExperimentPresetRevision, GapWindowDragSelectionState, GuardedLiveStatus, MarketDataIngestionJobRecord, MarketDataProvenanceExportFilterState, MarketDataProvenanceExportHistoryEntry, MarketDataProvenanceExportSort, MarketDataProvenanceExportStateV1, MarketDataLineageHistoryRecord, MarketDataStatus, OperatorAlertMarketContextProvenance, OperatorAlertPrimaryFocus, OperatorVisibility, PendingTouchGapWindowSweepState, PresetDraftConflict, PresetRevisionDiff, PresetRevisionFilterState, PresetStructuredDiffDeltaValue, PresetStructuredDiffGroup, PresetStructuredDiffRow, ProviderProvenanceAnalyticsPresetEntry, ProviderProvenanceDashboardLayout, ProviderProvenanceDashboardViewEntry, ProviderProvenanceExportAnalyticsPayload, ProviderProvenanceExportJobEntry, ProviderProvenanceExportJobEscalationResult, ProviderProvenanceExportJobHistoryPayload, ProviderProvenanceExportJobPolicyResult, ProviderProvenanceSchedulerAlertHistoryPayload, ProviderProvenanceSchedulerHealthExportPayload, ProviderProvenanceSchedulerHealthAnalyticsPayload, ProviderProvenanceSchedulerHealthHistoryPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ProviderProvenanceSchedulerSearchModerationPlanListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload, ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult, ProviderProvenanceSchedulerSearchDashboardPayload, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload, ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ProviderProvenanceSchedulerStitchedReportViewEntry, ProviderProvenanceSchedulerStitchedReportViewRevisionEntry, ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload, ProviderProvenanceSchedulerNarrativeBulkGovernanceResult, ProviderProvenanceSchedulerNarrativeGovernancePlan, ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult, ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ProviderProvenanceSchedulerNarrativeGovernanceQueueView, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload, ProviderProvenanceSchedulerNarrativeRegistryEntry, ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry, ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload, ProviderProvenanceSchedulerNarrativeTemplateEntry, ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload, ProviderProvenanceScheduledReportEntry, ProviderProvenanceScheduledReportHistoryPayload, ProvenanceArtifactLineDetailView, ProvenanceArtifactLineMicroView, Run, RunComparison, RunHistoryFilter, RunHistorySurfaceKey, RunListBoundaryContract, RunListBoundaryEligibility, RunListBoundaryGroupKey, RunListBoundarySurfaceId, RunSurfaceCapabilities, RunSurfaceCapabilityFamily, RunSurfaceCapabilityFamilyContract, RunSurfaceCapabilityFamilyKey, RunSurfaceCapabilitySchemaContract, RunSurfaceCapabilitySurfaceKey, RunSurfaceCollectionQueryBuilderReplayIntentSnapshot, RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload, RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy, RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload, RunSurfaceCollectionQueryContract, RunSurfaceCollectionQueryElementField, RunSurfaceCollectionQueryExpressionAuthoring, RunSurfaceCollectionQueryParameterDomainDescriptor, RunSurfaceCollectionQuerySchema, RunSurfaceSharedContract, RunSurfaceSubresourceContract, SavedRunHistoryFilterPreset, SavedRunHistoryFilterPresetStateV1, Strategy, TouchGapWindowActivationFeedbackState, TouchGapWindowHoldProgressState } from "./ControlRoomCoreHelpersContext";
import { defaultRunForm, defaultPresetForm, defaultPresetRevisionFilter, defaultMarketDataProvenanceExportFilterState, ProviderProvenanceAnalyticsScope, ProviderProvenanceSchedulerOccurrenceNarrativeFacet, ProviderProvenanceAnalyticsQueryState, ProviderProvenanceSchedulerSearchDashboardFilterState, ProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft, ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilterState, ProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilterState, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft, ProviderProvenanceSchedulerSearchModerationQueueFilterState, ProviderProvenanceSchedulerSearchModerationStageDraft, ProviderProvenanceSchedulerExportPolicyDraft, OperatorVisibilityAlertEntry, defaultProviderProvenanceAnalyticsQueryState, defaultProviderProvenanceSchedulerSearchDashboardFilterState, defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft, defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter, defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft, defaultProviderProvenanceSchedulerSearchModerationQueueFilterState, defaultProviderProvenanceSchedulerSearchModerationStageDraft, normalizeProviderProvenanceSchedulerRoutingPolicyDraftValue, normalizeProviderProvenanceSchedulerApprovalPolicyDraftValue, buildProviderProvenanceSchedulerExportPolicyDraft, getProviderProvenanceSchedulerNarrativeGovernanceQueuePriorityRank, getProviderProvenanceSchedulerNarrativeGovernanceQueueState, formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary, formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary, formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition, isProviderProvenanceSchedulerAlertCategory, getOperatorAlertOccurrenceKey, formatProviderProvenanceSchedulerTimelineSummary, formatProviderProvenanceSchedulerSearchMatchSummary, formatProviderProvenanceSchedulerRetrievalClusterSummary, buildProviderProvenanceSchedulerAlertWorkflowReason } from "./ControlRoomCoreDefaults";
import { defaultProviderProvenanceDashboardLayout, DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT, defaultProviderProvenanceWorkspaceDraft, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraftState, defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraftState, defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft, KEEP_CURRENT_BULK_GOVERNANCE_VALUE, CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE, ProviderProvenanceSchedulerNarrativeBulkToggleValue, ProviderProvenanceSchedulerNarrativeTemplateBulkDraftState, defaultProviderProvenanceSchedulerNarrativeTemplateBulkDraft, ProviderProvenanceSchedulerStitchedReportViewBulkDraftState, defaultProviderProvenanceSchedulerStitchedReportViewBulkDraft, ProviderProvenanceSchedulerNarrativeRegistryDraftState, defaultProviderProvenanceSchedulerNarrativeRegistryDraft, ProviderProvenanceSchedulerNarrativeRegistryBulkDraftState, defaultProviderProvenanceSchedulerNarrativeRegistryBulkDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraftState, defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraftState, defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersionEntry, ProviderProvenanceSchedulerNarrativeGovernanceQueueFilterState, defaultProviderProvenanceSchedulerNarrativeGovernanceQueueFilter, ProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterState, defaultProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilterState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilterState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilterState, defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter, ProviderProvenanceSchedulerStitchedReportViewAuditFilterState, defaultProviderProvenanceSchedulerStitchedReportViewAuditFilter, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilterState, defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter, ProviderProvenanceReportDraftState, defaultProviderProvenanceReportDraft } from "./ControlRoomCoreProviderDrafts";

export function buildPresetFormFromPreset(preset: ExperimentPreset) {
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

export function buildCurrentPresetRevisionSnapshot(preset: ExperimentPreset): ExperimentPresetRevision {
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

export function buildEmptyPresetRevisionSnapshot(): ExperimentPresetRevision {
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

export function formatPresetStructuredDiffDisplayValue(value: string) {
  return value || "none";
}

export function isPresetStructuredDiffObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function isPresetStructuredDiffScalar(value: unknown) {
  return value === null || ["boolean", "number", "string"].includes(typeof value);
}

export function arePresetStructuredDiffValuesEquivalent(left: unknown, right: unknown) {
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

export function matchesPresetParameterSchemaType(value: unknown, expectedType?: string) {
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

export function joinPresetStructuredDiffHints(...parts: Array<string | undefined>) {
  return parts.filter((part): part is string => Boolean(part)).join(" · ") || undefined;
}

export function tokenizePresetParameterPath(pathSegments: string[]) {
  return pathSegments
    .flatMap((segment) => segment.toLowerCase().match(/[a-z0-9]+/g) ?? [])
    .filter((token) => !/^\d+$/.test(token));
}

export function parsePresetTimeframeToMinutes(value: unknown) {
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

export function buildPresetRankedStringDelta(
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

export function buildPresetParameterStrategyContext(
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

export function buildPresetParameterDomainContext(
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

export function formatPresetParameterSchemaHint(schemaEntry?: ParameterSchema[string]) {
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

export function getPresetParameterSchemaEntry(
  parameterSchema: ParameterSchema | undefined,
  pathSegments: string[],
) {
  const rootSegment = pathSegments.find((segment) => !segment.startsWith("["));
  if (!rootSegment) {
    return undefined;
  }
  return parameterSchema?.[rootSegment];
}

export function buildPresetStructuredDiffDelta(
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
