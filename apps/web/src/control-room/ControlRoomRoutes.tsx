// @ts-nocheck
import { RuntimeOperatorPanel } from "./RuntimeOperatorPanel";

export function ControlRoomRoutes({ model }: { model: any }) {
  const {
    WorkspaceShell,
    activeWorkspace,
    activeWorkspaceDescriptor,
    apiBase,
    controlStripMetrics,
    navigateToWorkspace,
    loadAll,
    statusText,
    workspaceDescriptors,
    WorkspaceRouteContent,
    RunSurfaceCapabilityDiscoveryPanel,
    runSurfaceCapabilities,
    StrategyColumn,
    strategyGroups,
    RunForm,
    backtestForm,
    setBacktestForm,
    strategies,
    presets,
    handleBacktestSubmit,
    PresetCatalogPanel,
    presetForm,
    setPresetForm,
    editingPresetId,
    expandedPresetRevisionIds,
    beginPresetEdit,
    resetPresetEditor,
    applyPresetLifecycleAction,
    restorePresetRevision,
    handlePresetSubmit,
    togglePresetRevisions,
    ReferenceCatalog,
    references,
    runHistoryWorkspacePanels,
    sandboxForm,
    setSandboxForm,
    handleSandboxSubmit,
    marketStatus,
    failureSummary,
    formatTimestamp,
    backfillSummary,
    formatCompletion,
    activeMarketInstrument,
    focusedMarketWorkflowSummary,
    formatWorkflowToken,
    PanelDisclosure,
    buildMarketDataInstrumentFocusKey,
    activeMarketInstrumentKey,
    handleMarketInstrumentFocus,
    isMarketDataInstrumentAtRisk,
    BackfillCountStatus,
    instrumentGapRowKey,
    buildGapWindowKey,
    expandedGapRows,
    BackfillQualityStatus,
    activeGapWindowPickerRowKey,
    setExpandedGapWindowSelections,
    resolveGapWindowSelectionList,
    isSameGapWindowSelectionList,
    setActiveGapWindowPickerRowKey,
    setExpandedGapRows,
    toggleExpandedGapRow,
    expandedGapWindowSelections,
    SyncCheckpointStatus,
    SyncFailureStatus,
    operatorVisibility,
    operatorSummary,
    marketDataWorkflowLoading,
    marketDataWorkflowError,
    autoLinkedMarketInstrumentLink,
    focusedMultiSymbolPrimaryLink,
    incidentFocusedInstruments,
    resolveMarketDataSymbol,
    copyFocusedMarketWorkflowExport,
    focusedMarketProviderProvenanceCount,
    filteredFocusedMarketProviderProvenanceEvents,
    marketDataWorkflowExportFeedback,
    marketDataLineageHistory,
    shortenIdentifier,
    formatRange,
    marketDataIngestionJobs,
    truncateLabel,
    focusedMarketIncidentHistory,
    resetMarketDataProvenanceExportFilter,
    marketDataProvenanceExportHistory,
    clearMarketDataProvenanceExportHistory,
    setMarketDataProvenanceExportFilter,
    marketDataProvenanceExportFilter,
    ALL_FILTER_VALUE,
    marketDataProvenanceExportProviderOptions,
    marketDataProvenanceExportVendorFieldOptions,
    normalizeMarketDataProvenanceExportSort,
    formatMarketDataProvenanceExportFilterSummary,
    copySavedMarketDataProvenanceExport,
    restoreMarketDataProvenanceExportFilter,
    sharedProviderProvenanceExports,
    sharedProviderProvenanceExportsLoading,
    sharedProviderProvenanceExportsError,
    copySharedProviderProvenanceExport,
    loadSharedProviderProvenanceExportHistory,
    selectedSharedProviderProvenanceExportJobId,
    selectedSharedProviderProvenanceExportHistory,
    setProviderProvenanceAnalyticsQuery,
    providerProvenanceAnalyticsQuery,
    providerProvenanceAnalytics,
    formatProviderProvenanceAnalyticsQuerySummary,
    providerProvenanceDashboardLayout,
    setProviderProvenanceDashboardLayout,
    providerProvenanceWorkspaceFeedback,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft,
    saveProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
    editingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId,
    resetProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplates,
    toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelections,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft,
    saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    editingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId,
    resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesLoading,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesError,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIdSet,
    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelection,
    providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType,
    setProviderProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId,
    setProviderProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId,
    setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId,
    editProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
    removeProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryLoading,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryError,
    setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId,
    setProviderProvenanceWorkspaceFeedback,
    restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryRevision,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter,
    loadProviderProvenanceWorkspaceRegistry,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsLoading,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs,
    toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelections,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft,
    runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsLoading,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIdSet,
    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelection,
    formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary,
    applyProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyForCatalog,
    stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy,
    editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    removeProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryLoading,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError,
    setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId,
    setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds,
    restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryRevision,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps,
    toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelections,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft,
    providerProvenanceSchedulerNarrativeTemplates,
    runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet,
    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelection,
    formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary,
    editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
    setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepId,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft,
    saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
    resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions,
    stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft,
    restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersion,
    setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft,
    editingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId,
    selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
    saveProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateFromStep,
    resetProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates,
    toggleAllProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelections,
    selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds,
    setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft,
    runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction,
    stageSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesLoading,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesError,
    selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIdSet,
    toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelection,
    selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId,
    setSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId,
    editProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
    toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory,
    stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateQueuePlan,
    applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateToCatalogs,
    removeProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryLoading,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryError,
    selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory,
    setEditingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId,
    restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryRevision,
    setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsLoading,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsLoading,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsError,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits,
    setProviderProvenancePresetDraft,
    providerProvenancePresetDraft,
    saveCurrentProviderProvenancePreset,
    providerProvenanceAnalyticsPresetsLoading,
    providerProvenanceAnalyticsPresetsError,
    providerProvenanceAnalyticsPresets,
    applyProviderProvenanceWorkspaceQuery,
    setProviderProvenanceViewDraft,
    providerProvenanceViewDraft,
    saveCurrentProviderProvenanceDashboardView,
    providerProvenanceDashboardViewsLoading,
    providerProvenanceDashboardViewsError,
    providerProvenanceDashboardViews,
    formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary,
    setProviderProvenanceSchedulerNarrativeTemplateDraft,
    providerProvenanceSchedulerNarrativeTemplateDraft,
    saveCurrentProviderProvenanceSchedulerNarrativeTemplate,
    editingProviderProvenanceSchedulerNarrativeTemplateId,
    resetProviderProvenanceSchedulerNarrativeTemplateDraft,
    selectedProviderProvenanceSchedulerNarrativeTemplateIds,
    selectedProviderProvenanceSchedulerNarrativeTemplateEntries,
    providerProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId,
    toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections,
    providerProvenanceSchedulerNarrativeTemplateBulkAction,
    runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance,
    setProviderProvenanceSchedulerNarrativeTemplateBulkDraft,
    providerProvenanceSchedulerNarrativeTemplateBulkDraft,
    KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
    providerProvenanceSchedulerNarrativeTemplatesLoading,
    providerProvenanceSchedulerNarrativeTemplatesError,
    selectedProviderProvenanceSchedulerNarrativeTemplateIdSet,
    toggleProviderProvenanceSchedulerNarrativeTemplateSelection,
    setProviderProvenanceSchedulerNarrativeRegistryDraft,
    editProviderProvenanceSchedulerNarrativeTemplate,
    removeProviderProvenanceSchedulerNarrativeTemplate,
    toggleProviderProvenanceSchedulerNarrativeTemplateHistory,
    selectedProviderProvenanceSchedulerNarrativeTemplateId,
    selectedProviderProvenanceSchedulerNarrativeTemplateHistory,
    providerProvenanceSchedulerNarrativeTemplateHistoryLoading,
    providerProvenanceSchedulerNarrativeTemplateHistoryError,
    restoreProviderProvenanceSchedulerNarrativeTemplateHistoryRevision,
    providerProvenanceSchedulerNarrativeRegistryDraft,
    saveCurrentProviderProvenanceSchedulerNarrativeRegistryEntry,
    editingProviderProvenanceSchedulerNarrativeRegistryId,
    resetProviderProvenanceSchedulerNarrativeRegistryDraft,
    providerProvenanceSchedulerNarrativeRegistryEntries,
    selectedProviderProvenanceSchedulerNarrativeRegistryIds,
    selectedProviderProvenanceSchedulerNarrativeRegistryEntries,
    providerProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId,
    toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections,
    providerProvenanceSchedulerNarrativeRegistryBulkAction,
    runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance,
    setProviderProvenanceSchedulerNarrativeRegistryBulkDraft,
    providerProvenanceSchedulerNarrativeRegistryBulkDraft,
    CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE,
    providerProvenanceSchedulerNarrativeRegistryEntriesLoading,
    providerProvenanceSchedulerNarrativeRegistryEntriesError,
    selectedProviderProvenanceSchedulerNarrativeRegistryIdSet,
    toggleProviderProvenanceSchedulerNarrativeRegistrySelection,
    providerProvenanceSchedulerNarrativeTemplateNameMap,
    editProviderProvenanceSchedulerNarrativeRegistryEntry,
    removeProviderProvenanceSchedulerNarrativeRegistry,
    toggleProviderProvenanceSchedulerNarrativeRegistryHistory,
    selectedProviderProvenanceSchedulerNarrativeRegistryId,
    selectedProviderProvenanceSchedulerNarrativeRegistryHistory,
    providerProvenanceSchedulerNarrativeRegistryHistoryLoading,
    providerProvenanceSchedulerNarrativeRegistryHistoryError,
    restoreProviderProvenanceSchedulerNarrativeRegistryHistoryRevision,
    providerProvenanceSchedulerNarrativeGovernanceQueueSummary,
    filteredProviderProvenanceSchedulerNarrativeGovernancePlans,
    selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans,
    toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections,
    providerProvenanceSchedulerNarrativeGovernanceBatchAction,
    runProviderProvenanceSchedulerNarrativeGovernancePlanBatch,
    setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter,
    providerProvenanceSchedulerNarrativeGovernanceQueueFilter,
    providerProvenanceSchedulerNarrativeGovernancePlans,
    normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort,
    DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT,
    providerProvenanceSchedulerNarrativeGovernancePlansLoading,
    providerProvenanceSchedulerNarrativeGovernancePlansError,
    selectedProviderProvenanceSchedulerNarrativeGovernancePlanId,
    selectedProviderProvenanceSchedulerNarrativeGovernancePlanIdSet,
    toggleProviderProvenanceSchedulerNarrativeGovernancePlanSelection,
    getProviderProvenanceSchedulerNarrativeGovernanceQueueState,
    formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition,
    formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary,
    setSelectedProviderProvenanceSchedulerNarrativeGovernancePlanId,
    selectedProviderProvenanceSchedulerNarrativeGovernancePlan,
    providerProvenanceSchedulerNarrativeGovernancePlanAction,
    approveProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan,
    applyProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan,
    rollbackProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan,
    formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue,
    formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback,
    setProviderProvenanceReportDraft,
    providerProvenanceReportDraft,
    createCurrentProviderProvenanceScheduledReport,
    runDueSharedProviderProvenanceScheduledReports,
    providerProvenanceScheduledReportsLoading,
    providerProvenanceScheduledReportsError,
    providerProvenanceScheduledReports,
    runSharedProviderProvenanceScheduledReport,
    copyProviderProvenanceExportJobById,
    toggleProviderProvenanceScheduledReportHistory,
    selectedProviderProvenanceScheduledReportId,
    selectedProviderProvenanceScheduledReportHistory,
    providerProvenanceScheduledReportHistoryLoading,
    providerProvenanceScheduledReportHistoryError,
    providerProvenanceSchedulerAnalyticsLoading,
    providerProvenanceSchedulerAnalytics,
    providerProvenanceSchedulerAnalyticsError,
    providerProvenanceSchedulerHistoryError,
    providerProvenanceSchedulerCurrent,
    providerProvenanceSchedulerAutomationRef,
    copyProviderProvenanceSchedulerHealthJsonExport,
    shareProviderProvenanceSchedulerHealthExport,
    downloadProviderProvenanceSchedulerHealthCsv,
    providerProvenanceSchedulerDrilldownBucketKey,
    setProviderProvenanceSchedulerDrilldownBucketKey,
    formatSchedulerLagSeconds,
    resolveProviderProvenanceSeriesBarWidth,
    providerProvenanceSchedulerLagBarMax,
    providerProvenanceSchedulerDrillDown,
    providerProvenanceSchedulerHistory,
    providerProvenanceSchedulerHistoryOffset,
    setProviderProvenanceSchedulerHistoryOffset,
    providerProvenanceSchedulerHistoryLoading,
    providerProvenanceSchedulerRecentHistory,
    providerProvenanceSchedulerAlertHistory,
    formatProviderProvenanceSchedulerNarrativeFacet,
    setProviderProvenanceSchedulerAlertHistoryOffset,
    providerProvenanceSchedulerAlertCategoryOptions,
    providerProvenanceSchedulerAlertStatusOptions,
    providerProvenanceSchedulerAlertNarrativeFacetOptions,
    ProviderProvenanceSchedulerOccurrenceNarrativeFacet,
    providerProvenanceSchedulerAlertTimelineItems,
    copyProviderProvenanceSchedulerStitchedNarrativeReport,
    downloadProviderProvenanceSchedulerStitchedNarrativeCsv,
    shareProviderProvenanceSchedulerStitchedNarrativeReport,
    stageProviderProvenanceSchedulerNarrativeDrafts,
    providerProvenanceSchedulerAlertHistoryOffset,
    setProviderProvenanceSchedulerSearchDashboardFilter,
    providerProvenanceSchedulerSearchDashboardFilter,
    setSelectedProviderProvenanceSchedulerSearchFeedbackIds,
    providerProvenanceSchedulerSearchDashboard,
    selectedProviderProvenanceSchedulerSearchFeedbackIds,
    providerProvenanceSchedulerSearchFeedbackModerationPendingId,
    moderateProviderProvenanceSchedulerSearchFeedbackEntry,
    moderateProviderProvenanceSchedulerSearchFeedbackSelection,
    setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft,
    providerProvenanceSchedulerSearchModerationPolicyCatalogDraft,
    providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading,
    createProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry,
    editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId,
    resetProviderProvenanceSchedulerSearchModerationPolicyCatalogEditor,
    selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds,
    providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction,
    runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance,
    setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft,
    providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft,
    providerProvenanceSchedulerSearchModerationPolicyCatalogs,
    toggleAllProviderProvenanceSchedulerSearchModerationPolicyCatalogSelections,
    toggleProviderProvenanceSchedulerSearchModerationPolicyCatalogSelection,
    editProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry,
    deleteProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry,
    selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId,
    selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory,
    setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId,
    setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory,
    setProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryError,
    loadProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory,
    providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryLoading,
    providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError,
    restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryRevision,
    setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAudits,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading,
    createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry,
    editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId,
    resetProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEditor,
    selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction,
    runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies,
    toggleAllProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelections,
    toggleProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelection,
    editProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry,
    deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry,
    selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId,
    selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory,
    setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId,
    setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError,
    loadProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryLoading,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError,
    restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryRevision,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesLoading,
    createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies,
    applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDefaults,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId,
    stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaSelection,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError,
    approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry,
    applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId,
    stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceSelection,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePlans,
    approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan,
    applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan,
    providerProvenanceSchedulerSearchModerationStageDraft,
    setProviderProvenanceSchedulerSearchModerationStageDraft,
    providerProvenanceSchedulerSearchModerationPlanPendingId,
    stageProviderProvenanceSchedulerSearchModerationSelection,
    providerProvenanceSchedulerSearchModerationQueueFilter,
    setProviderProvenanceSchedulerSearchModerationQueueFilter,
    providerProvenanceSchedulerSearchModerationPlans,
    approveProviderProvenanceSchedulerSearchModerationQueuePlan,
    applyProviderProvenanceSchedulerSearchModerationQueuePlan,
    providerProvenanceSchedulerSearchDashboardLoading,
    providerProvenanceSchedulerSearchDashboardError,
    providerProvenanceSchedulerSearchModerationPlansLoading,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePlansLoading,
    providerProvenanceSchedulerSearchModerationPolicyCatalogsError,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError,
    providerProvenanceSchedulerSearchModerationPlansError,
    providerProvenanceSchedulerAlertRetrievalClusters,
    providerProvenanceSchedulerAlertHistoryLoading,
    providerProvenanceSchedulerAlertHistoryError,
    formatProviderProvenanceSchedulerTimelineSummary,
    getOperatorAlertOccurrenceKey,
    formatProviderProvenanceSchedulerSearchMatchSummary,
    formatProviderProvenanceSchedulerRetrievalClusterSummary,
    providerProvenanceSchedulerSearchFeedbackPendingOccurrenceKey,
    submitProviderProvenanceSchedulerSearchFeedback,
    triggerProviderProvenanceSchedulerAlertExportWorkflow,
    setProviderProvenanceSchedulerStitchedReportViewDraft,
    providerProvenanceSchedulerStitchedReportViewDraft,
    saveCurrentProviderProvenanceSchedulerStitchedReportView,
    editingProviderProvenanceSchedulerStitchedReportViewId,
    resetProviderProvenanceSchedulerStitchedReportViewDraft,
    providerProvenanceSchedulerStitchedReportViews,
    selectedProviderProvenanceSchedulerStitchedReportViewIds,
    selectedProviderProvenanceSchedulerStitchedReportViewEntries,
    toggleAllProviderProvenanceSchedulerStitchedReportViewSelections,
    providerProvenanceSchedulerStitchedReportViewBulkAction,
    runProviderProvenanceSchedulerStitchedReportViewBulkGovernance,
    setProviderProvenanceSchedulerStitchedReportViewBulkDraft,
    providerProvenanceSchedulerStitchedReportViewBulkDraft,
    providerProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId,
    providerProvenanceSchedulerStitchedReportViewsLoading,
    providerProvenanceSchedulerStitchedReportViewsError,
    selectedProviderProvenanceSchedulerStitchedReportViewIdSet,
    toggleProviderProvenanceSchedulerStitchedReportViewSelection,
    applyProviderProvenanceSchedulerStitchedReportView,
    editProviderProvenanceSchedulerStitchedReportView,
    deleteProviderProvenanceSchedulerStitchedReportViewEntry,
    toggleProviderProvenanceSchedulerStitchedReportViewHistory,
    selectedProviderProvenanceSchedulerStitchedReportViewId,
    selectedProviderProvenanceSchedulerStitchedReportViewHistory,
    copyProviderProvenanceSchedulerStitchedNarrativeReportView,
    downloadProviderProvenanceSchedulerStitchedNarrativeCsvView,
    shareProviderProvenanceSchedulerStitchedNarrativeReportView,
    providerProvenanceSchedulerStitchedReportViewHistoryLoading,
    providerProvenanceSchedulerStitchedReportViewHistoryError,
    restoreProviderProvenanceSchedulerStitchedReportViewHistoryRevision,
    setProviderProvenanceSchedulerStitchedReportViewAuditFilter,
    providerProvenanceSchedulerStitchedReportViewAuditFilter,
    providerProvenanceSchedulerStitchedReportViewAuditsLoading,
    providerProvenanceSchedulerStitchedReportViewAuditsError,
    providerProvenanceSchedulerStitchedReportViewAudits,
    providerProvenanceSchedulerStitchedReportGovernanceQueueSummary,
    setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter,
    providerProvenanceSchedulerStitchedReportGovernanceQueueFilter,
    providerProvenanceSchedulerStitchedReportGovernancePlans,
    providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs,
    providerProvenanceSchedulerStitchedReportGovernancePlansLoading,
    providerProvenanceSchedulerStitchedReportGovernancePlansError,
    reviewProviderProvenanceSchedulerStitchedReportGovernancePlanInSharedQueue,
    approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry,
    applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry,
    rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry,
    setProviderProvenanceSchedulerStitchedReportGovernanceCatalogSearch,
    providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch,
    applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog,
    openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans,
    providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError,
    reviewProviderProvenanceSchedulerStitchedReportGovernanceRegistryPlanInSharedQueue,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch,
    applyProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalog,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft,
    saveCurrentProviderProvenanceSchedulerStitchedReportGovernanceRegistry,
    editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId,
    resetProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistrySearch,
    providerProvenanceSchedulerStitchedReportGovernanceRegistrySearch,
    providerProvenanceSchedulerStitchedReportGovernanceRegistries,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId,
    toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction,
    runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft,
    providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading,
    providerProvenanceSchedulerStitchedReportGovernanceRegistriesError,
    filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIdSet,
    toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelection,
    applyProviderProvenanceSchedulerStitchedReportGovernanceRegistry,
    editProviderProvenanceSchedulerStitchedReportGovernanceRegistry,
    toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryId,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory,
    deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryLoading,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError,
    restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistoryRevision,
    providerProvenanceSchedulerExports,
    providerProvenanceSchedulerExportsLoading,
    providerProvenanceSchedulerExportsError,
    copySharedProviderProvenanceSchedulerExport,
    loadProviderProvenanceSchedulerExportHistory,
    escalateSharedProviderProvenanceSchedulerExport,
    selectedProviderProvenanceSchedulerExportJobId,
    selectedProviderProvenanceSchedulerExportEntry,
    setProviderProvenanceSchedulerExportPolicyDraft,
    providerProvenanceSchedulerExportPolicyDraft,
    updateSharedProviderProvenanceSchedulerExportPolicy,
    approveSharedProviderProvenanceSchedulerExport,
    providerProvenanceSchedulerExportHistoryLoading,
    providerProvenanceSchedulerExportHistoryError,
    selectedProviderProvenanceSchedulerExportHistory,
    providerProvenanceAnalyticsLoading,
    providerProvenanceAnalyticsError,
    providerProvenanceDriftBarMax,
    formatProviderDriftIntensity,
    providerProvenanceBurnUpBarMax,
    focusMarketInstrumentFromProviderExport,
    sharedProviderProvenanceExportHistoryLoading,
    sharedProviderProvenanceExportHistoryError,
    linkedOperatorAlertById,
    formatLinkedMarketPrimaryFocusNote,
    isProviderProvenanceSchedulerAlertCategory,
    linkedOperatorIncidentEventById,
    summarizeProviderRecoveryMarketContextProvenance,
    formatParameterMap,
    formatProviderRecoveryTelemetry,
    formatProviderRecoverySchema,
    linkedOperatorAlertHistoryByOccurrenceId,
    providerProvenanceSchedulerAlertHistoryTimelineByCategory,
    liveForm,
    setLiveForm,
    handleLiveSubmit,
    guardedLive,
    guardedLiveSummary,
    setGuardedLiveReason,
    guardedLiveReason,
    runGuardedLiveReconciliation,
    recoverGuardedLiveRuntime,
    resumeGuardedLiveRun,
    engageGuardedLiveKillSwitch,
    releaseGuardedLiveKillSwitch,
    formatFixedNumber,
    activeGuardedLiveAlertIds,
    remediateGuardedLiveIncident,
    acknowledgeGuardedLiveIncident,
    escalateGuardedLiveIncident,
  } = model;

  return (
    <WorkspaceShell
      activeWorkspace={activeWorkspace}
      activeWorkspaceDescriptor={activeWorkspaceDescriptor}
      apiBase={apiBase}
      controlStripMetrics={controlStripMetrics}
      onNavigate={navigateToWorkspace}
      onRefresh={() => void loadAll()}
      statusText={statusText}
      workspaceDescriptors={workspaceDescriptors}
    >
      <WorkspaceRouteContent
        activeWorkspace={activeWorkspace}
        routes={{
          overview: {
            catalogPanel: (
              <section className="panel panel-wide">
                <div className="section-heading">
                  <div>
                    <p className="kicker">Strategy catalog</p>
                    <h2>Runtime tiers</h2>
                  </div>
                  <button className="ghost-button" onClick={() => void loadAll()}>
                    Refresh
                  </button>
                </div>

                <RunSurfaceCapabilityDiscoveryPanel capabilities={runSurfaceCapabilities} />

                <div className="strategy-columns">
                  <StrategyColumn
                    title="Native"
                    strategies={strategyGroups.native}
                    accent="amber"
                    runSurfaceCapabilities={runSurfaceCapabilities}
                  />
                  <StrategyColumn
                    title="NFI References"
                    strategies={strategyGroups.reference}
                    accent="cyan"
                    runSurfaceCapabilities={runSurfaceCapabilities}
                  />
                  <StrategyColumn
                    title="Future LLM"
                    strategies={strategyGroups.future}
                    accent="ember"
                    runSurfaceCapabilities={runSurfaceCapabilities}
                  />
                </div>
              </section>
            ),
          },
          research: {
            launchPanel: (
              <section className="panel">
                <p className="kicker">Backtest</p>
                <h2>Launch a run</h2>
                <RunForm
                  form={backtestForm}
                  setForm={setBacktestForm}
                  strategies={strategies}
                  presets={presets}
                  onSubmit={handleBacktestSubmit}
                />
              </section>
            ),
            presetPanel: (
              <section className="panel panel-wide">
                <p className="kicker">Experiment OS</p>
                <h2>Scenario presets</h2>
                <PresetCatalogPanel
                  form={presetForm}
                  presets={presets}
                  runSurfaceCapabilities={runSurfaceCapabilities}
                  setForm={setPresetForm}
                  strategies={strategies}
                  editingPresetId={editingPresetId}
                  expandedPresetRevisionIds={expandedPresetRevisionIds}
                  onEditPreset={beginPresetEdit}
                  onResetEditor={resetPresetEditor}
                  onLifecycleAction={applyPresetLifecycleAction}
                  onRestoreRevision={restorePresetRevision}
                  onSubmit={handlePresetSubmit}
                  onToggleRevisions={togglePresetRevisions}
                />
              </section>
            ),
            referencePanel: (
              <section className="panel panel-wide">
                <p className="kicker">Reference lane</p>
                <h2>Third-party references</h2>
                <ReferenceCatalog references={references} />
              </section>
            ),
            ...runHistoryWorkspacePanels.research,
          },
          runtime: {
            launchPanel: (
              <section className="panel">
                <p className="kicker">Sandbox</p>
                <h2>Start sandbox worker</h2>
                <RunForm
                  form={sandboxForm}
                  setForm={setSandboxForm}
                  strategies={strategies.filter((strategy) => strategy.runtime === "native")}
                  presets={presets}
                  onSubmit={handleSandboxSubmit}
                />
              </section>
            ),
            marketDataPanel: (
              <section className="panel panel-wide">
          <p className="kicker">Data plane</p>
          <h2>Market data status</h2>
          {marketStatus ? (
            <div className="status-grid">
              <div className="metric-tile">
                <span>Provider</span>
                <strong>{marketStatus.provider}</strong>
              </div>
              <div className="metric-tile">
                <span>Venue</span>
                <strong>{marketStatus.venue}</strong>
              </div>
              <div className="metric-tile">
                <span>Tracked symbols</span>
                <strong>{marketStatus.instruments.length}</strong>
              </div>
              {failureSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Failures 24h</span>
                    <strong>{failureSummary.failureCount24h}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Affected instruments</span>
                    <strong>{failureSummary.affectedInstrumentCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest failure</span>
                    <strong>{formatTimestamp(failureSummary.lastFailureAt)}</strong>
                  </div>
                </>
              ) : null}
              {backfillSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Backfill count</span>
                    <strong>{formatCompletion(backfillSummary.completionRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Count complete</span>
                    <strong>
                      {backfillSummary.completeCount} / {backfillSummary.instrumentCount}
                    </strong>
                  </div>
                  <div className="metric-tile">
                    <span>Contiguous quality</span>
                    <strong>{formatCompletion(backfillSummary.contiguousQualityRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Gap-free spans</span>
                    <strong>
                      {backfillSummary.contiguousInstrumentCount > 0
                        ? `${backfillSummary.contiguousCompleteCount} / ${backfillSummary.contiguousInstrumentCount}`
                        : "n/a"}
                    </strong>
                  </div>
                </>
              ) : null}
              {activeMarketInstrument && focusedMarketWorkflowSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Triage focus</span>
                    <strong>{focusedMarketWorkflowSummary.focusLabel}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Focused sync</span>
                    <strong>{activeMarketInstrument.sync_status}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Lineage claim</span>
                    <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage?.validation_claim)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest ingestion</span>
                    <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestJob?.status)}</strong>
                  </div>
                </>
              ) : null}
              <PanelDisclosure
                defaultOpen={false}
                summary={`${
                  marketStatus.instruments.length
                } instruments across ${marketStatus.provider} / ${marketStatus.venue}.${activeMarketInstrument ? ` Focused triage: ${activeMarketInstrument.instrument_id} ${activeMarketInstrument.timeframe}.` : ""}`}
                title="Instrument sync ledger"
              >
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Instrument</th>
                      <th>Timeframe</th>
                      <th>Sync</th>
                      <th>Candles</th>
                      <th>Target</th>
                      <th>Count</th>
                      <th>Quality</th>
                      <th>Lag</th>
                      <th>Latest</th>
                      <th>Checkpoint</th>
                      <th>Failures</th>
                      <th>Issues</th>
                    </tr>
                  </thead>
                  <tbody>
                    {marketStatus.instruments.map((instrument) => {
                      const isFocusedInstrument =
                        buildMarketDataInstrumentFocusKey(instrument) === activeMarketInstrumentKey;
                      return (
                      <tr
                        className={isFocusedInstrument ? "market-data-instrument-row is-active" : "market-data-instrument-row"}
                        key={instrument.instrument_id}
                      >
                        <td>
                          <button
                            className={`market-data-instrument-button ${isFocusedInstrument ? "is-active" : ""}`.trim()}
                            onClick={() => {
                              void handleMarketInstrumentFocus(instrument);
                            }}
                            type="button"
                          >
                            <strong>{instrument.instrument_id}</strong>
                            <span>{isMarketDataInstrumentAtRisk(instrument) ? "review" : "clear"}</span>
                          </button>
                        </td>
                        <td>{instrument.timeframe}</td>
                        <td>{instrument.sync_status}</td>
                        <td>{instrument.candle_count}</td>
                        <td>{instrument.backfill_target_candles ?? "n/a"}</td>
                        <td>
                          <BackfillCountStatus instrument={instrument} />
                        </td>
                        <td>
                          {(() => {
                            const rowKey = instrumentGapRowKey(instrument);
                            const gapWindowKeys = instrument.backfill_gap_windows.map((gapWindow) =>
                              buildGapWindowKey(gapWindow),
                            );
                            const expanded = Boolean(expandedGapRows[rowKey]);
                            return (
                              <BackfillQualityStatus
                                expanded={expanded}
                                gapWindowPickerOpen={activeGapWindowPickerRowKey === rowKey}
                                instrument={instrument}
                                onChangeGapWindowSelections={(nextSelectedGapWindowKeys) => {
                                  setExpandedGapWindowSelections((current) => {
                                    const nextSelectedWindows = gapWindowKeys.filter((candidate) =>
                                      nextSelectedGapWindowKeys.includes(candidate),
                                    );
                                    if (!nextSelectedWindows.length) {
                                      return current;
                                    }
                                    const currentSelectedWindows = resolveGapWindowSelectionList(
                                      gapWindowKeys,
                                      current[rowKey] ?? null,
                                    );
                                    if (isSameGapWindowSelectionList(currentSelectedWindows, nextSelectedWindows)) {
                                      return current;
                                    }
                                    return {
                                      ...current,
                                      [rowKey]: nextSelectedWindows,
                                    };
                                  });
                                }}
                                onSelectAllGapWindows={() => {
                                  if (!gapWindowKeys.length) {
                                    return;
                                  }
                                  setExpandedGapWindowSelections((current) => ({
                                    ...current,
                                    [rowKey]: gapWindowKeys,
                                  }));
                                }}
                                onToggle={() => {
                                  const nextExpanded = !expanded;
                                  if (!nextExpanded && activeGapWindowPickerRowKey === rowKey) {
                                    setActiveGapWindowPickerRowKey(null);
                                  }
                                  setExpandedGapRows((current) => toggleExpandedGapRow(current, rowKey));
                                  setExpandedGapWindowSelections((current) => {
                                    if (current[rowKey]?.length) {
                                      return current;
                                    }
                                    return gapWindowKeys.length
                                      ? { ...current, [rowKey]: gapWindowKeys }
                                      : current;
                                  });
                                }}
                                onToggleGapWindowPicker={() => {
                                  if (!gapWindowKeys.length) {
                                    return;
                                  }
                                  if (!expanded) {
                                    setExpandedGapRows((current) =>
                                      current[rowKey] ? current : { ...current, [rowKey]: true },
                                    );
                                  }
                                  setExpandedGapWindowSelections((current) => {
                                    if (current[rowKey]?.length) {
                                      return current;
                                    }
                                    return { ...current, [rowKey]: gapWindowKeys };
                                  });
                                  setActiveGapWindowPickerRowKey((current) =>
                                    current === rowKey ? null : rowKey,
                                  );
                                }}
                                selectedGapWindowKeys={expandedGapWindowSelections[rowKey] ?? null}
                              />
                            );
                          })()}
                        </td>
                        <td>{instrument.lag_seconds ?? "n/a"}</td>
                        <td>{instrument.last_timestamp ?? "n/a"}</td>
                        <td>
                          <SyncCheckpointStatus instrument={instrument} />
                        </td>
                        <td>
                          <SyncFailureStatus instrument={instrument} />
                        </td>
                        <td>{instrument.issues.length ? instrument.issues.join(", ") : "ok"}</td>
                      </tr>
                    );})}
                  </tbody>
                </table>
              </PanelDisclosure>
            </div>
          ) : (
            <p>No data status loaded.</p>
          )}
              </section>
            ),
            operatorPanel: <RuntimeOperatorPanel model={model} />,
            ...runHistoryWorkspacePanels.runtime,
          },
          live: {
            launchPanel: (
              <section className="panel">
                <p className="kicker">Guarded live</p>
                <h2>Start live worker</h2>
                <RunForm
                  form={liveForm}
                  setForm={setLiveForm}
                  strategies={strategies.filter((strategy) => strategy.runtime === "native")}
                  presets={presets}
                  onSubmit={handleLiveSubmit}
                />
              </section>
            ),
            controlPanel: (
              <section className="panel panel-wide">
          <p className="kicker">Guarded live</p>
          <h2>Kill switch and reconciliation</h2>
          {guardedLive ? (
            <div className="status-grid">
              {guardedLiveSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Candidacy</span>
                    <strong>{guardedLive.candidacy_status}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Kill switch</span>
                    <strong>{guardedLive.kill_switch.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Runtime alerts</span>
                    <strong>{guardedLive.active_runtime_alert_count}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Venue verification</span>
                    <strong>{guardedLive.reconciliation.venue_snapshot?.verification_state ?? "n/a"}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Last reconciliation</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestReconciliationAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Last recovery</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestRecoveryAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Blockers</span>
                    <strong>{guardedLiveSummary.blockerCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Live owner</span>
                    <strong>{guardedLive.ownership.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Order-book sync</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestOrderSyncAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Session restore</span>
                    <strong>{guardedLive.session_restore.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Session handoff</span>
                    <strong>{guardedLive.session_handoff.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest audit</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestAuditAt)}</strong>
                  </div>
                </>
              ) : null}
              <div className="control-action-row">
                <label className="control-action-field">
                  <span>Operator reason</span>
                  <input
                    onChange={(event) => setGuardedLiveReason(event.target.value)}
                    placeholder="operator_safety_drill"
                    type="text"
                    value={guardedLiveReason}
                  />
                </label>
                <button className="ghost-button" onClick={() => void runGuardedLiveReconciliation()} type="button">
                  Run reconciliation
                </button>
                <button className="ghost-button" onClick={() => void recoverGuardedLiveRuntime()} type="button">
                  Recover runtime state
                </button>
                <button className="ghost-button" onClick={() => void resumeGuardedLiveRun()} type="button">
                  Resume live owner
                </button>
                <button className="ghost-button" onClick={() => void engageGuardedLiveKillSwitch()} type="button">
                  Engage kill switch
                </button>
                <button className="ghost-button" onClick={() => void releaseGuardedLiveKillSwitch()} type="button">
                  Release kill switch
                </button>
              </div>
              <div className="panel-disclosure-grid">
                <PanelDisclosure
                  defaultOpen={true}
                  summary={`${guardedLive.kill_switch.state} kill switch · ${guardedLive.blockers.length} blockers · owner ${guardedLive.ownership.state}.`}
                  title="Control guardrails"
                >
                  <div className="panel-disclosure-stack">
                  <h3>Current guardrails</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Kill switch</th>
                        <td>{guardedLive.kill_switch.state}</td>
                      </tr>
                      <tr>
                        <th>Updated by</th>
                        <td>{guardedLive.kill_switch.updated_by}</td>
                      </tr>
                      <tr>
                        <th>Updated at</th>
                        <td>{formatTimestamp(guardedLive.kill_switch.updated_at)}</td>
                      </tr>
                      <tr>
                        <th>Reason</th>
                        <td>{guardedLive.kill_switch.reason}</td>
                      </tr>
                      <tr>
                        <th>Running sandbox</th>
                        <td>{guardedLive.running_sandbox_count}</td>
                      </tr>
                      <tr>
                        <th>Running paper</th>
                        <td>{guardedLive.running_paper_count}</td>
                      </tr>
                      <tr>
                        <th>Running live</th>
                        <td>{guardedLive.running_live_count}</td>
                      </tr>
                      <tr>
                        <th>Owner state</th>
                        <td>{guardedLive.ownership.state}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.ownership.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.ownership.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner symbol</th>
                        <td>{guardedLive.ownership.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Claimed at</th>
                        <td>{formatTimestamp(guardedLive.ownership.claimed_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last resume</th>
                        <td>{formatTimestamp(guardedLive.ownership.last_resumed_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last order sync</th>
                        <td>{formatTimestamp(guardedLive.ownership.last_order_sync_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Restore state</th>
                        <td>{guardedLive.session_restore.state}</td>
                      </tr>
                      <tr>
                        <th>Restore source</th>
                        <td>{guardedLive.session_restore.source}</td>
                      </tr>
                      <tr>
                        <th>Restored at</th>
                        <td>{formatTimestamp(guardedLiveSummary?.latestSessionRestoreAt ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Handoff state</th>
                        <td>{guardedLive.session_handoff.state}</td>
                      </tr>
                      <tr>
                        <th>Handoff transport</th>
                        <td>{guardedLive.session_handoff.transport}</td>
                      </tr>
                      <tr>
                        <th>Last handoff sync</th>
                        <td>{formatTimestamp(guardedLiveSummary?.latestSessionHandoffAt ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Reconciliation scope</th>
                        <td>{guardedLive.reconciliation.scope}</td>
                      </tr>
                      <tr>
                        <th>Venue snapshot</th>
                        <td>
                          {guardedLive.reconciliation.venue_snapshot
                            ? `${guardedLive.reconciliation.venue_snapshot.provider} / ${guardedLive.reconciliation.venue_snapshot.venue}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Venue verified</th>
                        <td>{guardedLive.reconciliation.venue_snapshot?.verification_state ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Venue captured</th>
                        <td>{formatTimestamp(guardedLive.reconciliation.venue_snapshot?.captured_at ?? null)}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Candidate blockers</h3>
                  {guardedLive.blockers.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Blocker</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.blockers.map((blocker) => (
                          <tr key={blocker}>
                            <td>{blocker}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live blockers recorded.</p>
                  )}
                  </div>
                </PanelDisclosure>
                <PanelDisclosure
                  defaultOpen={false}
                  summary={`${guardedLive.reconciliation.findings.length} findings · ${guardedLive.incident_events.length} incidents · ${guardedLive.order_book.open_orders.length} durable orders.`}
                  title="Venue state, recovery, and incidents"
                >
                  <div className="panel-disclosure-stack panel-disclosure-scroll">
                  <h3>Reconciliation findings</h3>
                  {guardedLive.reconciliation.findings.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Severity</th>
                          <th>Finding</th>
                          <th>Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.findings.map((finding) => (
                          <tr key={`${finding.kind}-${finding.summary}`}>
                            <td>{finding.severity}</td>
                            <td>{finding.kind}</td>
                            <td>
                              <strong>{finding.summary}</strong>
                              <p className="run-lineage-symbol-copy">{finding.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">{guardedLive.reconciliation.summary}</p>
                  )}
                  <h3>Venue snapshot</h3>
                  {guardedLive.reconciliation.venue_snapshot ? (
                    <table className="data-table">
                      <tbody>
                        <tr>
                          <th>Provider</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.provider}</td>
                        </tr>
                        <tr>
                          <th>Venue</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.venue}</td>
                        </tr>
                        <tr>
                          <th>State</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.verification_state}</td>
                        </tr>
                        <tr>
                          <th>Captured</th>
                          <td>{formatTimestamp(guardedLive.reconciliation.venue_snapshot.captured_at ?? null)}</td>
                        </tr>
                        <tr>
                          <th>Issues</th>
                          <td>
                            {guardedLive.reconciliation.venue_snapshot.issues.length
                              ? guardedLive.reconciliation.venue_snapshot.issues.join(", ")
                              : "none"}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue snapshot recorded yet.</p>
                  )}
                  <h3>Internal exposures</h3>
                  {guardedLive.reconciliation.internal_snapshot?.exposures?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Run</th>
                          <th>Mode</th>
                          <th>Instrument</th>
                          <th>Quantity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.internal_snapshot.exposures.map((exposure) => (
                          <tr key={`${exposure.run_id}-${exposure.instrument_id}`}>
                            <td>{exposure.run_id}</td>
                            <td>{exposure.mode}</td>
                            <td>{exposure.instrument_id}</td>
                            <td>{exposure.quantity.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No internal open exposures recorded.</p>
                  )}
                  <h3>Venue balances</h3>
                  {guardedLive.reconciliation.venue_snapshot?.balances?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Asset</th>
                          <th>Total</th>
                          <th>Free</th>
                          <th>Used</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.venue_snapshot.balances.map((balance) => (
                          <tr key={balance.asset}>
                            <td>{balance.asset}</td>
                            <td>{balance.total.toFixed(8)}</td>
                            <td>{balance.free === null || balance.free === undefined ? "n/a" : balance.free.toFixed(8)}</td>
                            <td>{balance.used === null || balance.used === undefined ? "n/a" : balance.used.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue balances captured.</p>
                  )}
                  <h3>Venue open orders</h3>
                  {guardedLive.reconciliation.venue_snapshot?.open_orders?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.venue_snapshot.open_orders.map((order) => (
                          <tr key={order.order_id}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue open orders captured.</p>
                  )}
                  <h3>Recovered runtime</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Recovery state</th>
                        <td>{guardedLive.recovery.state}</td>
                      </tr>
                      <tr>
                        <th>Recovered at</th>
                        <td>{formatTimestamp(guardedLive.recovery.recovered_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Recovered by</th>
                        <td>{guardedLive.recovery.recovered_by ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Source snapshot</th>
                        <td>{formatTimestamp(guardedLive.recovery.source_snapshot_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Source state</th>
                        <td>{guardedLive.recovery.source_verification_state}</td>
                      </tr>
                      <tr>
                        <th>Summary</th>
                        <td>{guardedLive.recovery.summary}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.recovery.issues.length ? guardedLive.recovery.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Recovered exposures</h3>
                  {guardedLive.recovery.exposures.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Instrument</th>
                          <th>Asset</th>
                          <th>Quantity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.recovery.exposures.map((exposure) => (
                          <tr key={`${exposure.instrument_id}-${exposure.asset}`}>
                            <td>{exposure.instrument_id}</td>
                            <td>{exposure.asset}</td>
                            <td>{exposure.quantity.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No recovered venue exposures recorded.</p>
                  )}
                  <h3>Recovered open orders</h3>
                  {guardedLive.recovery.open_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.recovery.open_orders.map((order) => (
                          <tr key={order.order_id}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No recovered venue orders recorded.</p>
                  )}
                  <h3>Venue-native session restore</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>State</th>
                        <td>{guardedLive.session_restore.state}</td>
                      </tr>
                      <tr>
                        <th>Source</th>
                        <td>{guardedLive.session_restore.source}</td>
                      </tr>
                      <tr>
                        <th>Restored at</th>
                        <td>{formatTimestamp(guardedLive.session_restore.restored_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Venue</th>
                        <td>{guardedLive.session_restore.venue ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Symbol</th>
                        <td>{guardedLive.session_restore.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.session_restore.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.session_restore.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.session_restore.issues.length ? guardedLive.session_restore.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  {guardedLive.session_restore.synced_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Status</th>
                          <th>Filled</th>
                          <th>Remaining</th>
                          <th>Updated</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.session_restore.synced_orders.map((order) => (
                          <tr key={`restored-${order.order_id}`}>
                            <td>{order.order_id}</td>
                            <td>{order.status}</td>
                            <td>{(order.filled_amount ?? 0).toFixed(8)}</td>
                            <td>{(order.remaining_amount ?? 0).toFixed(8)}</td>
                            <td>{formatTimestamp(order.updated_at ?? null)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue-native session lifecycle rows restored yet.</p>
                  )}
                  <h3>Venue-native session stream</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>State</th>
                        <td>{guardedLive.session_handoff.state}</td>
                      </tr>
                      <tr>
                        <th>Source</th>
                        <td>{guardedLive.session_handoff.source}</td>
                      </tr>
                      <tr>
                        <th>Transport</th>
                        <td>{guardedLive.session_handoff.transport}</td>
                      </tr>
                      <tr>
                        <th>Stream started at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.handed_off_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Released at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.released_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last stream sync</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_sync_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Supervision</th>
                        <td>{guardedLive.session_handoff.supervision_state}</td>
                      </tr>
                      <tr>
                        <th>Failovers</th>
                        <td>{guardedLive.session_handoff.failover_count}</td>
                      </tr>
                      <tr>
                        <th>Last failover</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_failover_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Coverage</th>
                        <td>{guardedLive.session_handoff.coverage.length ? guardedLive.session_handoff.coverage.join(", ") : "none"}</td>
                      </tr>
                      <tr>
                        <th>Order book state</th>
                        <td>{guardedLive.session_handoff.order_book_state}</td>
                      </tr>
                      <tr>
                        <th>Last depth update ID</th>
                        <td>{guardedLive.session_handoff.order_book_last_update_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Depth gap count</th>
                        <td>{guardedLive.session_handoff.order_book_gap_count}</td>
                      </tr>
                      <tr>
                        <th>Rebuild count</th>
                        <td>{guardedLive.session_handoff.order_book_rebuild_count}</td>
                      </tr>
                      <tr>
                        <th>Last rebuilt at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.order_book_last_rebuilt_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Bid levels</th>
                        <td>{guardedLive.session_handoff.order_book_bid_level_count}</td>
                      </tr>
                      <tr>
                        <th>Ask levels</th>
                        <td>{guardedLive.session_handoff.order_book_ask_level_count}</td>
                      </tr>
                      <tr>
                        <th>Channel restore</th>
                        <td>{guardedLive.session_handoff.channel_restore_state}</td>
                      </tr>
                      <tr>
                        <th>Channel restore count</th>
                        <td>{guardedLive.session_handoff.channel_restore_count}</td>
                      </tr>
                      <tr>
                        <th>Last channel restore</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.channel_last_restored_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Channel continuation</th>
                        <td>{guardedLive.session_handoff.channel_continuation_state}</td>
                      </tr>
                      <tr>
                        <th>Continuation count</th>
                        <td>{guardedLive.session_handoff.channel_continuation_count}</td>
                      </tr>
                      <tr>
                        <th>Last continued at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.channel_last_continued_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Best bid</th>
                        <td>
                          {guardedLive.session_handoff.order_book_best_bid_price != null
                            ? `${guardedLive.session_handoff.order_book_best_bid_price.toFixed(8)}`
                              + ` @ ${guardedLive.session_handoff.order_book_best_bid_quantity?.toFixed(8) ?? "n/a"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Best ask</th>
                        <td>
                          {guardedLive.session_handoff.order_book_best_ask_price != null
                            ? `${guardedLive.session_handoff.order_book_best_ask_price.toFixed(8)}`
                              + ` @ ${guardedLive.session_handoff.order_book_best_ask_quantity?.toFixed(8) ?? "n/a"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Last market event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_market_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last aggregate trade</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_aggregate_trade_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last mini ticker</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_mini_ticker_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last depth update</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_depth_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last kline update</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_kline_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last account event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_account_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last balance event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_balance_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last order-list event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_order_list_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last trade tick</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_trade_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last book ticker</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_book_ticker_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Venue session</th>
                        <td>{guardedLive.session_handoff.venue_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Cursor</th>
                        <td>{guardedLive.session_handoff.cursor ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Active orders</th>
                        <td>{guardedLive.session_handoff.active_order_count}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.session_handoff.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.session_handoff.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.session_handoff.issues.length ? guardedLive.session_handoff.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Recovered venue order book</h3>
                  {guardedLive.session_handoff.order_book_bids.length
                    || guardedLive.session_handoff.order_book_asks.length ? (
                      <div className="status-grid-two-column">
                        <section>
                          <h4>Recovered bids</h4>
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>Price</th>
                                <th>Quantity</th>
                              </tr>
                            </thead>
                            <tbody>
                              {guardedLive.session_handoff.order_book_bids.slice(0, 5).map((level) => (
                                <tr key={`handoff-bid-${level.price}`}>
                                  <td>{level.price.toFixed(8)}</td>
                                  <td>{level.quantity.toFixed(8)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </section>
                        <section>
                          <h4>Recovered asks</h4>
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>Price</th>
                                <th>Quantity</th>
                              </tr>
                            </thead>
                            <tbody>
                              {guardedLive.session_handoff.order_book_asks.slice(0, 5).map((level) => (
                                <tr key={`handoff-ask-${level.price}`}>
                                  <td>{level.price.toFixed(8)}</td>
                                  <td>{level.quantity.toFixed(8)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </section>
                      </div>
                    ) : (
                      <p className="empty-state">No recovered venue order-book levels recorded.</p>
                    )}
                  <h3>Recovered market channels</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Trade tick</th>
                        <td>
                          {guardedLive.session_handoff.trade_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.trade_snapshot.price)} @ ${formatFixedNumber(guardedLive.session_handoff.trade_snapshot.quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Aggregate trade</th>
                        <td>
                          {guardedLive.session_handoff.aggregate_trade_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.aggregate_trade_snapshot.price)} @ ${formatFixedNumber(guardedLive.session_handoff.aggregate_trade_snapshot.quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Book ticker</th>
                        <td>
                          {guardedLive.session_handoff.book_ticker_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.bid_price)} @ ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.bid_quantity)} / ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.ask_price)} @ ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.ask_quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Mini ticker</th>
                        <td>
                          {guardedLive.session_handoff.mini_ticker_snapshot
                            ? `open ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.open_price)}, close ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.close_price)}, high ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.high_price)}, low ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.low_price)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Mini ticker volume</th>
                        <td>
                          {guardedLive.session_handoff.mini_ticker_snapshot
                            ? `base ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.base_volume)}, quote ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.quote_volume)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Kline snapshot</th>
                        <td>
                          {guardedLive.session_handoff.kline_snapshot
                            ? `${guardedLive.session_handoff.kline_snapshot.timeframe ?? "n/a"} | o ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.open_price)}, h ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.high_price)}, l ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.low_price)}, c ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.close_price)}, v ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.volume)}, closed ${guardedLive.session_handoff.kline_snapshot.closed ? "yes" : "no"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Trade snapshot time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.trade_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Aggregate trade time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.aggregate_trade_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Book ticker time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.book_ticker_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Mini ticker time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.mini_ticker_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Kline open / close</th>
                        <td>
                          {guardedLive.session_handoff.kline_snapshot
                            ? `${formatTimestamp(guardedLive.session_handoff.kline_snapshot.open_at ?? null)} -> ${formatTimestamp(guardedLive.session_handoff.kline_snapshot.close_at ?? null)}`
                            : "n/a"}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Durable order book</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Sync state</th>
                        <td>{guardedLive.order_book.state}</td>
                      </tr>
                      <tr>
                        <th>Synced at</th>
                        <td>{formatTimestamp(guardedLive.order_book.synced_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.order_book.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.order_book.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Symbol</th>
                        <td>{guardedLive.order_book.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.order_book.issues.length ? guardedLive.order_book.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  {guardedLive.order_book.open_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.order_book.open_orders.map((order) => (
                          <tr key={`durable-${order.order_id}`}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No durable guarded-live open orders recorded.</p>
                  )}
                  <h3>Guarded-live alerts</h3>
                  {guardedLive.active_alerts.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Severity</th>
                          <th>Category</th>
                          <th>Summary</th>
                          <th>Detected</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.active_alerts.map((alert) => (
                          <tr key={`guarded-live-alert-${alert.alert_id}`}>
                            <td>{alert.severity}</td>
                            <td>{alert.category}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No active guarded-live alerts.</p>
                  )}
                  <h3>Guarded-live alert history</h3>
                  {guardedLive.alert_history.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Status</th>
                          <th>Severity</th>
                          <th>Summary</th>
                          <th>Detected</th>
                          <th>Resolved</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.alert_history.slice(0, 8).map((alert) => (
                          <tr key={`guarded-live-alert-history-${alert.alert_id}`}>
                            <td>{alert.status}</td>
                            <td>{alert.severity}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                            <td>{formatTimestamp(alert.resolved_at ?? null)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live alert history recorded.</p>
                  )}
                  <h3>Guarded-live incidents</h3>
                  {guardedLive.incident_events.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Kind</th>
                          <th>Severity</th>
                          <th>Summary</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.incident_events.slice(0, 8).map((event) => {
                          const providerRecoveryProvenanceSummary =
                            summarizeProviderRecoveryMarketContextProvenance(
                              event.remediation.provider_recovery,
                            )?.summary ?? null;
                          return (
                          <tr key={`guarded-live-incident-${event.event_id}`}>
                            <td>{formatTimestamp(event.timestamp)}</td>
                            <td>{event.kind}</td>
                            <td>{event.severity}</td>
                            <td>
                              <strong>{event.summary}</strong>
                              <p className="run-lineage-symbol-copy">{event.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {event.delivery_state}
                                {event.delivery_targets.length ? ` via ${event.delivery_targets.join(", ")}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Ack: {event.acknowledgment_state}
                                {event.acknowledged_by ? ` by ${event.acknowledged_by}` : ""}
                                {event.acknowledged_at ? ` at ${formatTimestamp(event.acknowledged_at)}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Escalation: level {event.escalation_level} / {event.escalation_state}
                                {event.last_escalated_by ? ` by ${event.last_escalated_by}` : ""}
                                {event.last_escalated_at ? ` at ${formatTimestamp(event.last_escalated_at)}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Next escalation: {formatTimestamp(event.next_escalation_at ?? null)}
                                {event.escalation_targets.length ? ` via ${event.escalation_targets.join(", ")}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                External: {event.external_status}
                                {event.external_provider ? ` via ${event.external_provider}` : ""}
                                {event.external_reference ? ` (${event.external_reference})` : ""}
                                {event.external_last_synced_at
                                  ? ` at ${formatTimestamp(event.external_last_synced_at)}`
                                  : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Paging: {event.paging_status}
                                {event.paging_policy_id ? ` via ${event.paging_policy_id}` : ""}
                                {event.paging_provider ? ` (${event.paging_provider})` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Provider workflow: {event.provider_workflow_state}
                                {event.provider_workflow_action ? ` / ${event.provider_workflow_action}` : ""}
                                {event.provider_workflow_reference
                                  ? ` (${event.provider_workflow_reference})`
                                  : ""}
                                {event.provider_workflow_last_attempted_at
                                  ? ` at ${formatTimestamp(event.provider_workflow_last_attempted_at)}`
                                  : ""}
                              </p>
                              {event.remediation.state !== "not_applicable" ? (
                                <>
                                  <p className="run-lineage-symbol-copy">
                                    Remediation: {event.remediation.state}
                                    {event.remediation.summary ? ` / ${event.remediation.summary}` : ""}
                                    {event.remediation.runbook ? ` (${event.remediation.runbook})` : ""}
                                    {event.remediation.requested_by
                                      ? ` by ${event.remediation.requested_by}`
                                      : ""}
                                    {event.remediation.last_attempted_at
                                      ? ` at ${formatTimestamp(event.remediation.last_attempted_at)}`
                                      : ""}
                                  </p>
                                  {event.remediation.detail ? (
                                    <p className="run-lineage-symbol-copy">
                                      Remediation detail: {event.remediation.detail}
                                    </p>
                                  ) : null}
                                  {Object.keys(event.remediation.provider_payload).length ? (
                                    <p className="run-lineage-symbol-copy">
                                      Provider recovery payload: {formatParameterMap(event.remediation.provider_payload)}
                                      {event.remediation.provider_payload_updated_at
                                        ? ` at ${formatTimestamp(event.remediation.provider_payload_updated_at)}`
                                        : ""}
                                    </p>
                                  ) : null}
                                  {event.remediation.provider_recovery.lifecycle_state !== "not_synced" ? (
                                    <>
                                      <p className="run-lineage-symbol-copy">
                                        Provider recovery: {event.remediation.provider_recovery.lifecycle_state}
                                        {event.remediation.provider_recovery.job_id
                                          ? ` / job ${event.remediation.provider_recovery.job_id}`
                                          : ""}
                                        {event.remediation.provider_recovery.channels.length
                                          ? ` / channels ${event.remediation.provider_recovery.channels.join(", ")}`
                                          : ""}
                                        {event.remediation.provider_recovery.symbols.length
                                          ? ` / symbols ${event.remediation.provider_recovery.symbols.join(", ")}`
                                          : ""}
                                        {event.remediation.provider_recovery.timeframe
                                          ? ` / ${event.remediation.provider_recovery.timeframe}`
                                          : ""}
                                        {event.remediation.provider_recovery.verification.state !== "unknown"
                                          ? ` / verification ${event.remediation.provider_recovery.verification.state}`
                                          : ""}
                                        {event.remediation.provider_recovery.updated_at
                                          ? ` at ${formatTimestamp(event.remediation.provider_recovery.updated_at)}`
                                          : ""}
                                      </p>
                                      <p className="run-lineage-symbol-copy">
                                        Recovery machine: {event.remediation.provider_recovery.status_machine.state}
                                        {` / workflow ${event.remediation.provider_recovery.status_machine.workflow_state}`}
                                        {event.remediation.provider_recovery.status_machine.workflow_action
                                          ? ` (${event.remediation.provider_recovery.status_machine.workflow_action})`
                                          : ""}
                                        {` / job ${event.remediation.provider_recovery.status_machine.job_state}`}
                                        {` / sync ${event.remediation.provider_recovery.status_machine.sync_state}`}
                                        {event.remediation.provider_recovery.status_machine.attempt_number
                                          ? ` / attempt ${event.remediation.provider_recovery.status_machine.attempt_number}`
                                          : ""}
                                        {event.remediation.provider_recovery.status_machine.last_event_kind
                                          ? ` / event ${event.remediation.provider_recovery.status_machine.last_event_kind}`
                                          : ""}
                                        {event.remediation.provider_recovery.status_machine.last_event_at
                                          ? ` at ${formatTimestamp(event.remediation.provider_recovery.status_machine.last_event_at)}`
                                          : ""}
                                      </p>
                                      {formatProviderRecoveryTelemetry(event.remediation.provider_recovery) ? (
                                        <p className="run-lineage-symbol-copy">
                                          {formatProviderRecoveryTelemetry(event.remediation.provider_recovery)}
                                        </p>
                                      ) : null}
                                      {formatProviderRecoverySchema(event.remediation.provider_recovery) ? (
                                        <p className="run-lineage-symbol-copy">
                                          {formatProviderRecoverySchema(event.remediation.provider_recovery)}
                                        </p>
                                      ) : null}
                                      {providerRecoveryProvenanceSummary ? (
                                        <p className="run-lineage-symbol-copy market-data-provider-provenance-copy">
                                          {providerRecoveryProvenanceSummary}
                                        </p>
                                      ) : null}
                                    </>
                                  ) : null}
                                </>
                              ) : null}
                              {event.acknowledgment_reason ? (
                                <p className="run-lineage-symbol-copy">
                                  Ack reason: {event.acknowledgment_reason}
                                </p>
                              ) : null}
                              {event.escalation_reason ? (
                                <p className="run-lineage-symbol-copy">
                                  Escalation reason: {event.escalation_reason}
                                </p>
                              ) : null}
                            </td>
                            <td>
                              {event.kind === "incident_opened" && activeGuardedLiveAlertIds.has(event.alert_id) ? (
                                <>
                                  {event.remediation.state !== "not_applicable" ? (
                                    <button
                                      className="ghost-button"
                                      onClick={() => void remediateGuardedLiveIncident(event.event_id)}
                                      type="button"
                                    >
                                      Request remediation
                                    </button>
                                  ) : null}
                                  <button
                                    className="ghost-button"
                                    disabled={event.acknowledgment_state === "acknowledged"}
                                    onClick={() => void acknowledgeGuardedLiveIncident(event.event_id)}
                                    type="button"
                                  >
                                    Acknowledge
                                  </button>
                                  <button
                                    className="ghost-button"
                                    onClick={() => void escalateGuardedLiveIncident(event.event_id)}
                                    type="button"
                                  >
                                    Escalate
                                  </button>
                                </>
                              ) : (
                                <span className="run-lineage-symbol-copy">No action</span>
                              )}
                            </td>
                          </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live incident events recorded.</p>
                  )}
                  <h3>Guarded-live delivery history</h3>
                  {guardedLive.delivery_history.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Target</th>
                          <th>Status</th>
                          <th>Attempt</th>
                          <th>Next retry</th>
                          <th>Detail</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.delivery_history.slice(0, 8).map((record) => (
                          <tr key={`guarded-live-delivery-${record.delivery_id}`}>
                            <td>{formatTimestamp(record.attempted_at)}</td>
                            <td>{record.target}</td>
                            <td>{record.status}</td>
                            <td>{record.attempt_number}</td>
                            <td>{formatTimestamp(record.next_retry_at ?? null)}</td>
                            <td>
                              <strong>{record.incident_kind}</strong>
                              <p className="run-lineage-symbol-copy">Phase: {record.phase}</p>
                              {record.provider_action ? (
                                <p className="run-lineage-symbol-copy">
                                  Provider action: {record.provider_action}
                                </p>
                              ) : null}
                              <p className="run-lineage-symbol-copy">
                                External: {record.external_provider ?? "n/a"}
                                {record.external_reference ? ` (${record.external_reference})` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">{record.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live outbound delivery attempts recorded.</p>
                  )}
                  <h3>Guarded-live audit</h3>
                  {guardedLive.audit_events.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Actor</th>
                          <th>Kind</th>
                          <th>Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.audit_events.slice(0, 8).map((event) => (
                          <tr key={event.event_id}>
                            <td>{formatTimestamp(event.timestamp)}</td>
                            <td>{event.actor}</td>
                            <td>{event.kind}</td>
                            <td>
                              <strong>{event.summary}</strong>
                              <p className="run-lineage-symbol-copy">{event.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live audit events recorded.</p>
                  )}
                  </div>
                </PanelDisclosure>
              </div>
            </div>
          ) : (
            <p>No guarded-live status loaded.</p>
          )}
              </section>
            ),
            ...runHistoryWorkspacePanels.live,
          },
        }}
      />
    </WorkspaceShell>
  );
}
