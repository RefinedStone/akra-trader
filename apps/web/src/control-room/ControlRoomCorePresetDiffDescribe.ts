// @ts-nocheck

import { CSSProperties, FormEvent, KeyboardEvent, MouseEvent, PointerEvent, ReactNode, forwardRef, useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState, AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION, AKRA_TOUCH_FEEDBACK_EVENT_NAME, AkraTouchFeedbackDetail, AkraTouchFeedbackEnvelope, triggerAkraTouchFeedbackBridge, WorkspaceShell, buildControlWorkspaceDescriptors, ControlWorkspaceDescriptor, ControlStripMetric, useWorkspaceRoute, WorkspaceRouteContent, buildRunHistoryWorkspacePanels, LiveOrderReplacementDraft, RunHistoryWorkspaceSectionProps, RunOrderControls, getRunListBoundaryContractSnapshot, getRunListBoundarySurfaceLabel, getRunSurfaceCapabilityFamily, getRunSurfaceCapabilityFamilyOrder, getRunSurfaceCapabilityGroupOrder, getRunSurfaceCapabilitySchemaContract, getRunSurfaceCollectionQueryContracts, getRunSurfaceSharedContracts, getRunSurfaceSubresourceContracts, RunListComparisonBoundaryNote, shouldEnableReferenceProvenanceSemantics, shouldEnableRunListMetricDrillBack, shouldEnableRunSnapshotSemantics, shouldEnableStrategyCatalogSchemaHints, shouldHydratePresetParameterDefaults, shouldRenderOrderActionBoundaryNote, shouldRenderWorkflowControlBoundaryNote, RunSurfaceCollectionQueryBuilder, formatComparisonTooltipTuningDelta, formatComparisonTooltipTuningValue, formatRelativeTimestampLabel, RunSection, RunSurfaceCollectionQueryBuilderApplyPayload, RunSurfaceCollectionQueryRuntimeCandidateContextSelection, RunSurfaceCollectionQueryRuntimeCandidateSample, applyProviderProvenanceSchedulerStitchedReportGovernancePlan, applyProviderProvenanceSchedulerNarrativeGovernancePlan, approveProviderProvenanceSchedulerStitchedReportGovernancePlan, approveProviderProvenanceSchedulerNarrativeGovernancePlan, createProviderProvenanceAnalyticsPreset, createProviderProvenanceDashboardView, createProviderProvenanceExportJob, createProviderProvenanceSchedulerStitchedReportGovernanceRegistry, createProviderProvenanceSchedulerStitchedReportGovernancePlan, createProviderProvenanceSchedulerStitchedReportView, createProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy, createProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, createProviderProvenanceSchedulerNarrativeGovernancePlan, createProviderProvenanceSchedulerNarrativeRegistryEntry, createProviderProvenanceSchedulerNarrativeTemplate, createProviderProvenanceScheduledReport, approveProviderProvenanceExportJob, applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, deleteProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, deleteProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, deleteProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, deleteProviderProvenanceSchedulerNarrativeRegistryEntry, deleteProviderProvenanceSchedulerStitchedReportView, deleteProviderProvenanceSchedulerNarrativeTemplate, createProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob, downloadProviderProvenanceExportJob, downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob, escalateProviderProvenanceExportJob, exportProviderProvenanceSchedulerHealth, exportProviderProvenanceSchedulerStitchedNarrativeReport, reconstructProviderProvenanceSchedulerHealthExport, exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, fetchJson, getProviderProvenanceExportAnalytics, getProviderProvenanceExportJobHistory, getProviderProvenanceSchedulerHealthAnalytics, getProviderProvenanceScheduledReportHistory, getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory, listProviderProvenanceAnalyticsPresets, listProviderProvenanceDashboardViews, listProviderProvenanceSchedulerStitchedReportViews, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisions, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogs, listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisions, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplates, listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisions, listProviderProvenanceSchedulerNarrativeGovernancePlans, listProviderProvenanceSchedulerNarrativeRegistryEntries, listProviderProvenanceSchedulerNarrativeRegistryRevisions, listProviderProvenanceSchedulerNarrativeTemplates, listProviderProvenanceSchedulerNarrativeTemplateRevisions, listProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogs, listProviderProvenanceSchedulerStitchedReportGovernancePolicyTemplates, listProviderProvenanceSchedulerStitchedReportGovernancePlans, rollbackProviderProvenanceSchedulerStitchedReportGovernancePlan, rollbackProviderProvenanceSchedulerNarrativeGovernancePlan, listMarketDataIngestionJobs, listMarketDataLineageHistory, listProviderProvenanceExportJobs, listProviderProvenanceSchedulerAlertHistory, listProviderProvenanceSchedulerHealthHistory, listProviderProvenanceSchedulerStitchedReportGovernanceRegistries, listProviderProvenanceSchedulerStitchedReportGovernanceRegistryAudits, listProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisions, listProviderProvenanceSchedulerStitchedReportViewAudits, listProviderProvenanceSchedulerStitchedReportViewRevisions, getProviderProvenanceSchedulerSearchDashboard, bulkGovernProviderProvenanceSchedulerSearchModerationPolicyCatalogs, bulkGovernProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies, createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicy, createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, listProviderProvenanceSchedulerSearchModerationPolicyCatalogs, listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies, listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisions, listProviderProvenanceSchedulerSearchModerationCatalogGovernancePlans, listProviderProvenanceSchedulerSearchModerationPolicyCatalogAudits, listProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisions, listProviderProvenanceSchedulerSearchModerationPlans, listProviderProvenanceScheduledReports, listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs, listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, approveProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, approveProviderProvenanceSchedulerSearchModerationPlan, applyProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, applyProviderProvenanceSchedulerSearchModerationPlan, createProviderProvenanceSchedulerSearchModerationPolicyCatalog, deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, deleteProviderProvenanceSchedulerSearchModerationPolicyCatalog, moderateProviderProvenanceSchedulerSearchFeedbackBatch, moderateProviderProvenanceSchedulerSearchFeedback, pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs, pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits, recordProviderProvenanceSchedulerSearchFeedback, resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRevision, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevision, restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevision, restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogRevision, restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevision, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevision, restoreProviderProvenanceSchedulerNarrativeRegistryRevision, restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevision, restoreProviderProvenanceSchedulerStitchedReportViewRevision, restoreProviderProvenanceSchedulerNarrativeTemplateRevision, revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias, runProviderProvenanceSchedulerNarrativeGovernancePlanBatchAction, runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkGovernance, runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkGovernance, runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkGovernance, stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan, stageProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan, stageProviderProvenanceSchedulerSearchModerationPlan, updateProviderProvenanceSchedulerSearchModerationPolicyCatalog, updateProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy, stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, runDueProviderProvenanceScheduledReports, runProviderProvenanceScheduledReport, updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep, updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, updateProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, updateProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, updateProviderProvenanceSchedulerNarrativeRegistryEntry, updateProviderProvenanceSchedulerStitchedReportGovernanceRegistry, updateProviderProvenanceSchedulerStitchedReportView, updateProviderProvenanceSchedulerNarrativeTemplate, updateProviderProvenanceExportJobPolicy, deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistry, ALL_FILTER_VALUE, apiBase, COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM, COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM, COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM, COMPARISON_FOCUS_DETAIL_SEARCH_PARAM, COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM, COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM, COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM, COMPARISON_FOCUS_SECTION_SEARCH_PARAM, COMPARISON_FOCUS_SOURCE_SEARCH_PARAM, COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM, COMPARISON_HISTORY_BROWSER_STATE_KEY, COMPARISON_HISTORY_BROWSER_STATE_VERSION, COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY, COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION, COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS, COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS, COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS, COMPARISON_HISTORY_TAB_ID_SESSION_KEY, COMPARISON_INTENT_SEARCH_PARAM, COMPARISON_RUN_ID_SEARCH_PARAM, COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY, COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION, COMPARISON_TOOLTIP_TUNING_GROUPS, COMPARISON_TOOLTIP_TUNING_LABELS, COMPARISON_TOOLTIP_TUNING_SHARE_PARAM, COMPARISON_TOOLTIP_TUNING_STORAGE_KEY, COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION, COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD, CONTROL_ROOM_UI_STATE_STORAGE_KEY, CONTROL_ROOM_UI_STATE_VERSION, DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY, DEFAULT_COMPARISON_TOOLTIP_TUNING, DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE, LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY, MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY, MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION, MAX_COMPARISON_HISTORY_PANEL_ENTRIES, MAX_COMPARISON_HISTORY_SYNC_AUDIT_ENTRIES, MAX_COMPARISON_RUNS, MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS, MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES, MAX_VISIBLE_GAP_WINDOWS, PRESET_PROFILE_AGGRESSIVENESS_RANKS, PRESET_PROFILE_CONFIDENCE_RANKS, PRESET_PROFILE_SPEED_RANKS, PRESET_TIMEFRAME_UNIT_TO_MINUTES, REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM, REPLAY_INTENT_ALIAS_SEARCH_PARAM, REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM, REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM, REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM, REPLAY_INTENT_SCOPE_SEARCH_PARAM, REPLAY_INTENT_SEARCH_PARAM, REPLAY_INTENT_STEP_SEARCH_PARAM, REPLAY_INTENT_TEMPLATE_SEARCH_PARAM, RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION, RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY, SHOW_COMPARISON_TOOLTIP_TUNING_PANEL, TOUCH_GAP_WINDOW_SWEEP_HOLD_MS, TOUCH_GAP_WINDOW_SWEEP_MOVE_TOLERANCE_PX, BenchmarkArtifact, ParameterSchema, ComparisonCueKind, ComparisonHistoryBrowserState, ComparisonHistoryPanelEntry, ComparisonHistoryPanelState, ComparisonHistoryPanelSyncState, ComparisonHistoryStepDescriptor, ComparisonHistorySyncAuditEntry, ComparisonHistorySyncAuditFilter, ComparisonHistorySyncAuditKind, ComparisonHistorySyncAuditTrailState, ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource, ComparisonHistorySyncConflictReview, ComparisonHistorySyncConflictReviewGroup, ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncPreferenceReview, ComparisonHistorySyncPreferenceReviewRow, ComparisonHistorySyncPreferenceState, ComparisonHistorySyncWorkspaceRecommendationOverview, ComparisonHistorySyncWorkspaceReview, ComparisonHistorySyncWorkspaceReviewRow, ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncWorkspaceSemanticSignal, ComparisonHistorySyncWorkspaceSignalDetailNestedKey, ComparisonHistorySyncWorkspaceSignalDetailSubviewKey, ComparisonHistorySyncWorkspaceSignalMicroInteractionKey, ComparisonHistorySyncWorkspaceSignalMicroViewKey, ComparisonHistorySyncWorkspaceState, ComparisonHistoryTabIdentity, ComparisonHistoryWriteMode, ComparisonIntent, ComparisonScoreDrillBackOptions, ComparisonScoreLinkedRunRole, ComparisonScoreLinkSource, ComparisonScoreLinkTarget, ComparisonScoreSection, ComparisonTooltipConflictSessionSummary, ComparisonTooltipConflictSessionSummarySession, ComparisonTooltipConflictSessionUiState, ComparisonTooltipConflictUiStateV1, ComparisonTooltipInteractionOptions, ComparisonTooltipLayout, ComparisonTooltipPendingPresetImportConflict, ComparisonTooltipPresetConflictPreviewGroup, ComparisonTooltipPresetConflictPreviewRow, ComparisonTooltipPresetImportConflictPolicy, ComparisonTooltipPresetImportResolution, ComparisonTooltipTargetProps, ComparisonTooltipTuning, ComparisonTooltipTuningPresetStateV1, ComparisonTooltipTuningShareImport, ComparisonTooltipTuningSinglePresetShareV1, ControlRoomComparisonHistoryPanelUiState, ControlRoomComparisonSelectionState, ControlRoomUiStateV1, ControlRoomUiStateV2, ControlRoomUiStateV3, ControlRoomUiStateV4, ExpandedGapWindowSelections, ExperimentPreset, ExperimentPresetRevision, GapWindowDragSelectionState, GuardedLiveStatus, MarketDataIngestionJobRecord, MarketDataProvenanceExportFilterState, MarketDataProvenanceExportHistoryEntry, MarketDataProvenanceExportSort, MarketDataProvenanceExportStateV1, MarketDataLineageHistoryRecord, MarketDataStatus, OperatorAlertMarketContextProvenance, OperatorAlertPrimaryFocus, OperatorVisibility, PendingTouchGapWindowSweepState, PresetDraftConflict, PresetRevisionDiff, PresetRevisionFilterState, PresetStructuredDiffDeltaValue, PresetStructuredDiffGroup, PresetStructuredDiffRow, ProviderProvenanceAnalyticsPresetEntry, ProviderProvenanceDashboardLayout, ProviderProvenanceDashboardViewEntry, ProviderProvenanceExportAnalyticsPayload, ProviderProvenanceExportJobEntry, ProviderProvenanceExportJobEscalationResult, ProviderProvenanceExportJobHistoryPayload, ProviderProvenanceExportJobPolicyResult, ProviderProvenanceSchedulerAlertHistoryPayload, ProviderProvenanceSchedulerHealthExportPayload, ProviderProvenanceSchedulerHealthAnalyticsPayload, ProviderProvenanceSchedulerHealthHistoryPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ProviderProvenanceSchedulerSearchModerationPlanListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload, ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload, ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult, ProviderProvenanceSchedulerSearchDashboardPayload, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload, ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ProviderProvenanceSchedulerStitchedReportViewEntry, ProviderProvenanceSchedulerStitchedReportViewRevisionEntry, ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload, ProviderProvenanceSchedulerNarrativeBulkGovernanceResult, ProviderProvenanceSchedulerNarrativeGovernancePlan, ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult, ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ProviderProvenanceSchedulerNarrativeGovernanceQueueView, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload, ProviderProvenanceSchedulerNarrativeRegistryEntry, ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry, ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload, ProviderProvenanceSchedulerNarrativeTemplateEntry, ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry, ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload, ProviderProvenanceScheduledReportEntry, ProviderProvenanceScheduledReportHistoryPayload, ProvenanceArtifactLineDetailView, ProvenanceArtifactLineMicroView, ReferenceSource, Run, RunComparison, RunHistoryFilter, RunHistorySurfaceKey, RunListBoundaryContract, RunListBoundaryEligibility, RunListBoundaryGroupKey, RunListBoundarySurfaceId, RunSurfaceCapabilities, RunSurfaceCapabilityFamily, RunSurfaceCapabilityFamilyContract, RunSurfaceCapabilityFamilyKey, RunSurfaceCapabilitySchemaContract, RunSurfaceCapabilitySurfaceKey, RunSurfaceCollectionQueryBuilderReplayIntentSnapshot, RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload, RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy, RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload, RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload, RunSurfaceCollectionQueryContract, RunSurfaceCollectionQueryElementField, RunSurfaceCollectionQueryExpressionAuthoring, RunSurfaceCollectionQueryParameterDomainDescriptor, RunSurfaceCollectionQuerySchema, RunSurfaceSharedContract, RunSurfaceSubresourceContract, SavedRunHistoryFilterPreset, SavedRunHistoryFilterPresetStateV1, Strategy, TouchGapWindowActivationFeedbackState, TouchGapWindowHoldProgressState } from "./ControlRoomCoreHelpersContext";
import { defaultRunForm, defaultPresetForm, defaultPresetRevisionFilter, defaultMarketDataProvenanceExportFilterState, ProviderProvenanceAnalyticsScope, ProviderProvenanceSchedulerOccurrenceNarrativeFacet, ProviderProvenanceAnalyticsQueryState, ProviderProvenanceSchedulerSearchDashboardFilterState, ProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft, ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilterState, ProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilterState, ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState, ProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft, ProviderProvenanceSchedulerSearchModerationQueueFilterState, ProviderProvenanceSchedulerSearchModerationStageDraft, ProviderProvenanceSchedulerExportPolicyDraft, OperatorVisibilityAlertEntry, defaultProviderProvenanceAnalyticsQueryState, defaultProviderProvenanceSchedulerSearchDashboardFilterState, defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft, defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter, defaultProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilterState, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilterState, defaultProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft, defaultProviderProvenanceSchedulerSearchModerationQueueFilterState, defaultProviderProvenanceSchedulerSearchModerationStageDraft, normalizeProviderProvenanceSchedulerRoutingPolicyDraftValue, normalizeProviderProvenanceSchedulerApprovalPolicyDraftValue, buildProviderProvenanceSchedulerExportPolicyDraft, getProviderProvenanceSchedulerNarrativeGovernanceQueuePriorityRank, getProviderProvenanceSchedulerNarrativeGovernanceQueueState, formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary, formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary, formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition, isProviderProvenanceSchedulerAlertCategory, getOperatorAlertOccurrenceKey, formatProviderProvenanceSchedulerTimelineSummary, formatProviderProvenanceSchedulerSearchMatchSummary, formatProviderProvenanceSchedulerRetrievalClusterSummary, buildProviderProvenanceSchedulerAlertWorkflowReason } from "./ControlRoomCoreDefaults";
import { defaultProviderProvenanceDashboardLayout, DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT, defaultProviderProvenanceWorkspaceDraft, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraftState, defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraftState, defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft, KEEP_CURRENT_BULK_GOVERNANCE_VALUE, CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE, ProviderProvenanceSchedulerNarrativeBulkToggleValue, ProviderProvenanceSchedulerNarrativeTemplateBulkDraftState, defaultProviderProvenanceSchedulerNarrativeTemplateBulkDraft, ProviderProvenanceSchedulerStitchedReportViewBulkDraftState, defaultProviderProvenanceSchedulerStitchedReportViewBulkDraft, ProviderProvenanceSchedulerNarrativeRegistryDraftState, defaultProviderProvenanceSchedulerNarrativeRegistryDraft, ProviderProvenanceSchedulerNarrativeRegistryBulkDraftState, defaultProviderProvenanceSchedulerNarrativeRegistryBulkDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraftState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraftState, defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraftState, defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersionEntry, ProviderProvenanceSchedulerNarrativeGovernanceQueueFilterState, defaultProviderProvenanceSchedulerNarrativeGovernanceQueueFilter, ProviderProvenanceSchedulerStitchedReportGovernanceQueueFilterState, defaultProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter, ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilterState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter, ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilterState, defaultProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter, ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilterState, defaultProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter, ProviderProvenanceSchedulerStitchedReportViewAuditFilterState, defaultProviderProvenanceSchedulerStitchedReportViewAuditFilter, ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilterState, defaultProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter, ProviderProvenanceReportDraftState, defaultProviderProvenanceReportDraft } from "./ControlRoomCoreProviderDrafts";

import { buildPresetFormFromPreset, buildCurrentPresetRevisionSnapshot, buildEmptyPresetRevisionSnapshot, formatPresetStructuredDiffDisplayValue, isPresetStructuredDiffObject, isPresetStructuredDiffScalar, arePresetStructuredDiffValuesEquivalent, matchesPresetParameterSchemaType, joinPresetStructuredDiffHints, tokenizePresetParameterPath, parsePresetTimeframeToMinutes, buildPresetRankedStringDelta, buildPresetParameterStrategyContext, buildPresetParameterDomainContext, formatPresetParameterSchemaHint, getPresetParameterSchemaEntry, buildPresetStructuredDiffDelta } from "./ControlRoomCorePresetDiffRows";
export function summarizePresetStructuredDiffGroup(group: PresetStructuredDiffGroup) {
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

export function groupPresetStructuredDiffRows(rows: PresetStructuredDiffRow[]) {
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

export function buildPresetStructuredDiffRows(
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

export function describePresetRevisionDiff(
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

export function describePresetDraftConflict(
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

export function matchesPresetRevisionFilter(
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
