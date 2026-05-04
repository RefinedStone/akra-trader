// @ts-nocheck
import { RuntimeDataIncidentTriagePanel } from "./RuntimeDataIncidentTriagePanel";
export function RuntimeOperatorPanel({ model }: { model: any }) {
  const {
    operatorVisibility, operatorSummary, formatTimestamp, PanelDisclosure, activeMarketInstrument,
    focusedMarketWorkflowSummary, marketStatus, marketDataWorkflowLoading, marketDataWorkflowError, formatWorkflowToken,
    autoLinkedMarketInstrumentLink, focusedMultiSymbolPrimaryLink, incidentFocusedInstruments, buildMarketDataInstrumentFocusKey, activeMarketInstrumentKey,
    handleMarketInstrumentFocus, resolveMarketDataSymbol, copyFocusedMarketWorkflowExport, focusedMarketProviderProvenanceCount, filteredFocusedMarketProviderProvenanceEvents,
    marketDataWorkflowExportFeedback, marketDataLineageHistory, shortenIdentifier, formatRange, marketDataIngestionJobs,
    truncateLabel, focusedMarketIncidentHistory, resetMarketDataProvenanceExportFilter, marketDataProvenanceExportHistory, clearMarketDataProvenanceExportHistory,
    setMarketDataProvenanceExportFilter, marketDataProvenanceExportFilter, ALL_FILTER_VALUE, marketDataProvenanceExportProviderOptions, marketDataProvenanceExportVendorFieldOptions,
    normalizeMarketDataProvenanceExportSort, formatMarketDataProvenanceExportFilterSummary, copySavedMarketDataProvenanceExport, restoreMarketDataProvenanceExportFilter, sharedProviderProvenanceExports,
    sharedProviderProvenanceExportsLoading, sharedProviderProvenanceExportsError, copySharedProviderProvenanceExport, loadSharedProviderProvenanceExportHistory, selectedSharedProviderProvenanceExportJobId,
    selectedSharedProviderProvenanceExportHistory, setProviderProvenanceAnalyticsQuery, providerProvenanceAnalyticsQuery, providerProvenanceAnalytics, formatProviderProvenanceAnalyticsQuerySummary,
    providerProvenanceDashboardLayout, setProviderProvenanceDashboardLayout, providerProvenanceWorkspaceFeedback, setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft, providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft,
    saveProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, editingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId, resetProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft, providerProvenanceSchedulerNarrativeGovernancePolicyTemplates, toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelections,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries, setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft, saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    editingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId, resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft, providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesLoading, providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesError, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIdSet,
    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelection, providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType, setProviderProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId, setProviderProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId, setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId, editProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, removeProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate, toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory, providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryLoading, providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryError, setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId, setProviderProvenanceWorkspaceFeedback,
    restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryRevision, setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter, providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter, loadProviderProvenanceWorkspaceRegistry, providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsLoading,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError, providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs, toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelections, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries, setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft, runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction,
    providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsLoading, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIdSet, toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelection, formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary,
    applyProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyForCatalog, stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy, editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, removeProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryLoading, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError,
    setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId, setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryRevision, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps,
    toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelections, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds, setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft, providerProvenanceSchedulerNarrativeTemplates,
    runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet, toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelection, formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary,
    editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep, setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepId, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep, setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft,
    saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep, resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions, stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft, restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersion,
    setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft, editingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, saveProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateFromStep,
    resetProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, toggleAllProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelections, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds, setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft, runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction, stageSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesLoading,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesError, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIdSet, toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelection, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId, setSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId,
    editProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory, stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateQueuePlan, applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateToCatalogs, removeProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryLoading, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryError, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory, setEditingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId, restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryRevision,
    setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsLoading, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits,
    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsLoading, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsError, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits,
    setProviderProvenancePresetDraft, providerProvenancePresetDraft, saveCurrentProviderProvenancePreset, providerProvenanceAnalyticsPresetsLoading, providerProvenanceAnalyticsPresetsError,
    providerProvenanceAnalyticsPresets, applyProviderProvenanceWorkspaceQuery, setProviderProvenanceViewDraft, providerProvenanceViewDraft, saveCurrentProviderProvenanceDashboardView,
    providerProvenanceDashboardViewsLoading, providerProvenanceDashboardViewsError, providerProvenanceDashboardViews, formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary, setProviderProvenanceSchedulerNarrativeTemplateDraft,
    providerProvenanceSchedulerNarrativeTemplateDraft, saveCurrentProviderProvenanceSchedulerNarrativeTemplate, editingProviderProvenanceSchedulerNarrativeTemplateId, resetProviderProvenanceSchedulerNarrativeTemplateDraft, selectedProviderProvenanceSchedulerNarrativeTemplateIds,
    selectedProviderProvenanceSchedulerNarrativeTemplateEntries, providerProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId, toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections, providerProvenanceSchedulerNarrativeTemplateBulkAction, runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance,
    setProviderProvenanceSchedulerNarrativeTemplateBulkDraft, providerProvenanceSchedulerNarrativeTemplateBulkDraft, KEEP_CURRENT_BULK_GOVERNANCE_VALUE, providerProvenanceSchedulerNarrativeTemplatesLoading, providerProvenanceSchedulerNarrativeTemplatesError,
    selectedProviderProvenanceSchedulerNarrativeTemplateIdSet, toggleProviderProvenanceSchedulerNarrativeTemplateSelection, setProviderProvenanceSchedulerNarrativeRegistryDraft, editProviderProvenanceSchedulerNarrativeTemplate, removeProviderProvenanceSchedulerNarrativeTemplate,
    toggleProviderProvenanceSchedulerNarrativeTemplateHistory, selectedProviderProvenanceSchedulerNarrativeTemplateId, selectedProviderProvenanceSchedulerNarrativeTemplateHistory, providerProvenanceSchedulerNarrativeTemplateHistoryLoading, providerProvenanceSchedulerNarrativeTemplateHistoryError,
    restoreProviderProvenanceSchedulerNarrativeTemplateHistoryRevision, providerProvenanceSchedulerNarrativeRegistryDraft, saveCurrentProviderProvenanceSchedulerNarrativeRegistryEntry, editingProviderProvenanceSchedulerNarrativeRegistryId, resetProviderProvenanceSchedulerNarrativeRegistryDraft,
    providerProvenanceSchedulerNarrativeRegistryEntries, selectedProviderProvenanceSchedulerNarrativeRegistryIds, selectedProviderProvenanceSchedulerNarrativeRegistryEntries, providerProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId, toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections,
    providerProvenanceSchedulerNarrativeRegistryBulkAction, runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance, setProviderProvenanceSchedulerNarrativeRegistryBulkDraft, providerProvenanceSchedulerNarrativeRegistryBulkDraft, CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE,
    providerProvenanceSchedulerNarrativeRegistryEntriesLoading, providerProvenanceSchedulerNarrativeRegistryEntriesError, selectedProviderProvenanceSchedulerNarrativeRegistryIdSet, toggleProviderProvenanceSchedulerNarrativeRegistrySelection, providerProvenanceSchedulerNarrativeTemplateNameMap,
    editProviderProvenanceSchedulerNarrativeRegistryEntry, removeProviderProvenanceSchedulerNarrativeRegistry, toggleProviderProvenanceSchedulerNarrativeRegistryHistory, selectedProviderProvenanceSchedulerNarrativeRegistryId, selectedProviderProvenanceSchedulerNarrativeRegistryHistory,
    providerProvenanceSchedulerNarrativeRegistryHistoryLoading, providerProvenanceSchedulerNarrativeRegistryHistoryError, restoreProviderProvenanceSchedulerNarrativeRegistryHistoryRevision, providerProvenanceSchedulerNarrativeGovernanceQueueSummary, filteredProviderProvenanceSchedulerNarrativeGovernancePlans,
    selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans, toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections, providerProvenanceSchedulerNarrativeGovernanceBatchAction, runProviderProvenanceSchedulerNarrativeGovernancePlanBatch, setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter,
    providerProvenanceSchedulerNarrativeGovernanceQueueFilter, providerProvenanceSchedulerNarrativeGovernancePlans, normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort, DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT, providerProvenanceSchedulerNarrativeGovernancePlansLoading,
    providerProvenanceSchedulerNarrativeGovernancePlansError, selectedProviderProvenanceSchedulerNarrativeGovernancePlanId, selectedProviderProvenanceSchedulerNarrativeGovernancePlanIdSet, toggleProviderProvenanceSchedulerNarrativeGovernancePlanSelection, getProviderProvenanceSchedulerNarrativeGovernanceQueueState,
    formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition, formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary, setSelectedProviderProvenanceSchedulerNarrativeGovernancePlanId, selectedProviderProvenanceSchedulerNarrativeGovernancePlan, providerProvenanceSchedulerNarrativeGovernancePlanAction,
    approveProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan, applyProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan, rollbackProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan, formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue, formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback,
    setProviderProvenanceReportDraft, providerProvenanceReportDraft, createCurrentProviderProvenanceScheduledReport, runDueSharedProviderProvenanceScheduledReports, providerProvenanceScheduledReportsLoading,
    providerProvenanceScheduledReportsError, providerProvenanceScheduledReports, runSharedProviderProvenanceScheduledReport, copyProviderProvenanceExportJobById, toggleProviderProvenanceScheduledReportHistory,
    selectedProviderProvenanceScheduledReportId, selectedProviderProvenanceScheduledReportHistory, providerProvenanceScheduledReportHistoryLoading, providerProvenanceScheduledReportHistoryError, providerProvenanceSchedulerAnalyticsLoading,
    providerProvenanceSchedulerAnalytics, providerProvenanceSchedulerAnalyticsError, providerProvenanceSchedulerHistoryError, providerProvenanceSchedulerCurrent, providerProvenanceSchedulerAutomationRef,
    copyProviderProvenanceSchedulerHealthJsonExport, shareProviderProvenanceSchedulerHealthExport, downloadProviderProvenanceSchedulerHealthCsv, providerProvenanceSchedulerDrilldownBucketKey, setProviderProvenanceSchedulerDrilldownBucketKey,
    formatSchedulerLagSeconds, resolveProviderProvenanceSeriesBarWidth, providerProvenanceSchedulerLagBarMax, providerProvenanceSchedulerDrillDown, providerProvenanceSchedulerHistory,
    providerProvenanceSchedulerHistoryOffset, setProviderProvenanceSchedulerHistoryOffset, providerProvenanceSchedulerHistoryLoading, providerProvenanceSchedulerRecentHistory, providerProvenanceSchedulerAlertHistory,
    formatProviderProvenanceSchedulerNarrativeFacet, setProviderProvenanceSchedulerAlertHistoryOffset, providerProvenanceSchedulerAlertCategoryOptions, providerProvenanceSchedulerAlertStatusOptions, providerProvenanceSchedulerAlertNarrativeFacetOptions,
    ProviderProvenanceSchedulerOccurrenceNarrativeFacet, providerProvenanceSchedulerAlertTimelineItems, copyProviderProvenanceSchedulerStitchedNarrativeReport, downloadProviderProvenanceSchedulerStitchedNarrativeCsv, shareProviderProvenanceSchedulerStitchedNarrativeReport,
    stageProviderProvenanceSchedulerNarrativeDrafts, providerProvenanceSchedulerAlertHistoryOffset, setProviderProvenanceSchedulerSearchDashboardFilter, providerProvenanceSchedulerSearchDashboardFilter, setSelectedProviderProvenanceSchedulerSearchFeedbackIds,
    providerProvenanceSchedulerSearchDashboard, selectedProviderProvenanceSchedulerSearchFeedbackIds, providerProvenanceSchedulerSearchFeedbackModerationPendingId, moderateProviderProvenanceSchedulerSearchFeedbackEntry, moderateProviderProvenanceSchedulerSearchFeedbackSelection,
    setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft, providerProvenanceSchedulerSearchModerationPolicyCatalogDraft, providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading, createProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry, editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId,
    resetProviderProvenanceSchedulerSearchModerationPolicyCatalogEditor, selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds, providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction, runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance, setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft,
    providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft, providerProvenanceSchedulerSearchModerationPolicyCatalogs, toggleAllProviderProvenanceSchedulerSearchModerationPolicyCatalogSelections, toggleProviderProvenanceSchedulerSearchModerationPolicyCatalogSelection, editProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry,
    deleteProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry, selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId, selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory, setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId, setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory,
    setProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryError, loadProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory, providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryLoading, providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError, restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryRevision,
    setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter, providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter, providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading, providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError, providerProvenanceSchedulerSearchModerationPolicyCatalogAudits,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft, providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading, createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry, editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId,
    resetProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEditor, selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction, runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance, setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies, toggleAllProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelections, toggleProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelection, editProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry,
    deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry, selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId, selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory, setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId, setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory,
    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError, loadProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory, setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryLoading, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError,
    restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryRevision, setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits, setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesLoading, createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies, applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDefaults, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft, setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId, stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaSelection, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter, setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError, approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry, applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry, providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft, providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId,
    stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceSelection, providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter, setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter, providerProvenanceSchedulerSearchModerationCatalogGovernancePlans, approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan,
    applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan, providerProvenanceSchedulerSearchModerationStageDraft, setProviderProvenanceSchedulerSearchModerationStageDraft, providerProvenanceSchedulerSearchModerationPlanPendingId, stageProviderProvenanceSchedulerSearchModerationSelection,
    providerProvenanceSchedulerSearchModerationQueueFilter, setProviderProvenanceSchedulerSearchModerationQueueFilter, providerProvenanceSchedulerSearchModerationPlans, approveProviderProvenanceSchedulerSearchModerationQueuePlan, applyProviderProvenanceSchedulerSearchModerationQueuePlan,
    providerProvenanceSchedulerSearchDashboardLoading, providerProvenanceSchedulerSearchDashboardError, providerProvenanceSchedulerSearchModerationPlansLoading, providerProvenanceSchedulerSearchModerationCatalogGovernancePlansLoading, providerProvenanceSchedulerSearchModerationPolicyCatalogsError,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError, providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError, providerProvenanceSchedulerSearchModerationPlansError, providerProvenanceSchedulerAlertRetrievalClusters, providerProvenanceSchedulerAlertHistoryLoading,
    providerProvenanceSchedulerAlertHistoryError, formatProviderProvenanceSchedulerTimelineSummary, getOperatorAlertOccurrenceKey, formatProviderProvenanceSchedulerSearchMatchSummary, formatProviderProvenanceSchedulerRetrievalClusterSummary,
    providerProvenanceSchedulerSearchFeedbackPendingOccurrenceKey, submitProviderProvenanceSchedulerSearchFeedback, triggerProviderProvenanceSchedulerAlertExportWorkflow, setProviderProvenanceSchedulerStitchedReportViewDraft, providerProvenanceSchedulerStitchedReportViewDraft,
    saveCurrentProviderProvenanceSchedulerStitchedReportView, editingProviderProvenanceSchedulerStitchedReportViewId, resetProviderProvenanceSchedulerStitchedReportViewDraft, providerProvenanceSchedulerStitchedReportViews, selectedProviderProvenanceSchedulerStitchedReportViewIds,
    selectedProviderProvenanceSchedulerStitchedReportViewEntries, toggleAllProviderProvenanceSchedulerStitchedReportViewSelections, providerProvenanceSchedulerStitchedReportViewBulkAction, runProviderProvenanceSchedulerStitchedReportViewBulkGovernance, setProviderProvenanceSchedulerStitchedReportViewBulkDraft,
    providerProvenanceSchedulerStitchedReportViewBulkDraft, providerProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId, providerProvenanceSchedulerStitchedReportViewsLoading, providerProvenanceSchedulerStitchedReportViewsError, selectedProviderProvenanceSchedulerStitchedReportViewIdSet,
    toggleProviderProvenanceSchedulerStitchedReportViewSelection, applyProviderProvenanceSchedulerStitchedReportView, editProviderProvenanceSchedulerStitchedReportView, deleteProviderProvenanceSchedulerStitchedReportViewEntry, toggleProviderProvenanceSchedulerStitchedReportViewHistory,
    selectedProviderProvenanceSchedulerStitchedReportViewId, selectedProviderProvenanceSchedulerStitchedReportViewHistory, copyProviderProvenanceSchedulerStitchedNarrativeReportView, downloadProviderProvenanceSchedulerStitchedNarrativeCsvView, shareProviderProvenanceSchedulerStitchedNarrativeReportView,
    providerProvenanceSchedulerStitchedReportViewHistoryLoading, providerProvenanceSchedulerStitchedReportViewHistoryError, restoreProviderProvenanceSchedulerStitchedReportViewHistoryRevision, setProviderProvenanceSchedulerStitchedReportViewAuditFilter, providerProvenanceSchedulerStitchedReportViewAuditFilter,
    providerProvenanceSchedulerStitchedReportViewAuditsLoading, providerProvenanceSchedulerStitchedReportViewAuditsError, providerProvenanceSchedulerStitchedReportViewAudits, providerProvenanceSchedulerStitchedReportGovernanceQueueSummary, setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter,
    providerProvenanceSchedulerStitchedReportGovernanceQueueFilter, providerProvenanceSchedulerStitchedReportGovernancePlans, providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs, providerProvenanceSchedulerStitchedReportGovernancePlansLoading, providerProvenanceSchedulerStitchedReportGovernancePlansError,
    reviewProviderProvenanceSchedulerStitchedReportGovernancePlanInSharedQueue, approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry, applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry, rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry, setProviderProvenanceSchedulerStitchedReportGovernanceCatalogSearch,
    providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch, applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog, openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface, providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary, setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter, providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans, providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates, providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs, providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError, reviewProviderProvenanceSchedulerStitchedReportGovernanceRegistryPlanInSharedQueue, setProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch, providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch, applyProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalog,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft, providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft, saveCurrentProviderProvenanceSchedulerStitchedReportGovernanceRegistry, editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId, resetProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft,
    setProviderProvenanceSchedulerStitchedReportGovernanceRegistrySearch, providerProvenanceSchedulerStitchedReportGovernanceRegistrySearch, providerProvenanceSchedulerStitchedReportGovernanceRegistries, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId, toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections, providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction, runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance, setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft, providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading, providerProvenanceSchedulerStitchedReportGovernanceRegistriesError, filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIdSet,
    toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelection, applyProviderProvenanceSchedulerStitchedReportGovernanceRegistry, editProviderProvenanceSchedulerStitchedReportGovernanceRegistry, toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryId,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory, deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry, setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter, providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter, providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading,
    providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError, providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits, providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryLoading, providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError, restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistoryRevision,
    providerProvenanceSchedulerExports, providerProvenanceSchedulerExportsLoading, providerProvenanceSchedulerExportsError, copySharedProviderProvenanceSchedulerExport, loadProviderProvenanceSchedulerExportHistory,
    escalateSharedProviderProvenanceSchedulerExport, selectedProviderProvenanceSchedulerExportJobId, selectedProviderProvenanceSchedulerExportEntry, setProviderProvenanceSchedulerExportPolicyDraft, providerProvenanceSchedulerExportPolicyDraft,
    updateSharedProviderProvenanceSchedulerExportPolicy, approveSharedProviderProvenanceSchedulerExport, providerProvenanceSchedulerExportHistoryLoading, providerProvenanceSchedulerExportHistoryError, selectedProviderProvenanceSchedulerExportHistory,
    providerProvenanceAnalyticsLoading, providerProvenanceAnalyticsError, providerProvenanceDriftBarMax, formatProviderDriftIntensity, providerProvenanceBurnUpBarMax,
    focusMarketInstrumentFromProviderExport, sharedProviderProvenanceExportHistoryLoading, sharedProviderProvenanceExportHistoryError, linkedOperatorAlertById, formatLinkedMarketPrimaryFocusNote,
    isProviderProvenanceSchedulerAlertCategory, linkedOperatorIncidentEventById, summarizeProviderRecoveryMarketContextProvenance, formatParameterMap, formatProviderRecoveryTelemetry,
    formatProviderRecoverySchema, linkedOperatorAlertHistoryByOccurrenceId, providerProvenanceSchedulerAlertHistoryTimelineByCategory
  } = model;

  return (
              <section className="panel panel-wide">
          <p className="kicker">Operator trust</p>
          <h2>Runtime alerts and audit</h2>
          {operatorVisibility ? (
            <div className="status-grid">
              {operatorSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Active alerts</span>
                    <strong>{operatorSummary.alertCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Critical</span>
                    <strong>{operatorSummary.criticalCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Warnings</span>
                    <strong>{operatorSummary.warningCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest audit</span>
                    <strong>{formatTimestamp(operatorSummary.latestAuditAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Alert history</span>
                    <strong>{operatorSummary.historyCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Incidents</span>
                    <strong>{operatorSummary.incidentCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Deliveries</span>
                    <strong>{operatorSummary.deliveryCount}</strong>
                  </div>
                </>
              ) : null}
              <RuntimeDataIncidentTriagePanel model={model} />
              <PanelDisclosure
                defaultOpen={true}
                summary={`${operatorVisibility.alerts.length} active alerts · ${operatorVisibility.audit_events.length} recent audit events.`}
                title="Active alerts and audit"
              >
                <div className="status-grid-two-column">
                  <div>
                    <h3>Active alerts</h3>
                    {operatorVisibility.alerts.length ? (
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Severity</th>
                            <th>Category</th>
                            <th>Summary</th>
                            <th>Detected</th>
                            <th>Run</th>
                          </tr>
                        </thead>
                        <tbody>
                          {operatorVisibility.alerts.map((alert) => {
                            const linkedInstrument = linkedOperatorAlertById.get(alert.alert_id) ?? null;
                            const primaryFocusNote = formatLinkedMarketPrimaryFocusNote(linkedInstrument);
                            return (
                              <tr key={alert.alert_id}>
                                <td>{alert.severity}</td>
                                <td>{alert.category}</td>
                                <td>
                                  <strong>{alert.summary}</strong>
                                  <p className="run-lineage-symbol-copy">{alert.detail}</p>
                                  <p className="run-lineage-symbol-copy">
                                    Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                                  </p>
                                  {isProviderProvenanceSchedulerAlertCategory(alert.category) ? (
                                    <div className="market-data-provenance-history-actions">
                                      <button
                                        className="ghost-button"
                                        onClick={() => {
                                          void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                                            sourceLabel: alert.summary,
                                          });
                                        }}
                                        type="button"
                                      >
                                        Start export workflow
                                      </button>
                                      <button
                                        className="ghost-button"
                                        onClick={() => {
                                          void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                                            escalate: true,
                                            sourceLabel: alert.summary,
                                          });
                                        }}
                                        type="button"
                                      >
                                        Escalate snapshot
                                      </button>
                                    </div>
                                  ) : null}
                                  {linkedInstrument ? (
                                    <>
                                      <button
                                        className="market-data-inline-focus-button"
                                        onClick={() => {
                                          void handleMarketInstrumentFocus(linkedInstrument.instrument);
                                        }}
                                        type="button"
                                      >
                                        Focus triage: {linkedInstrument.symbol} · {linkedInstrument.timeframe}
                                      </button>
                                      {primaryFocusNote ? (
                                        <p className="market-data-inline-focus-note">
                                          {primaryFocusNote}
                                        </p>
                                      ) : null}
                                    </>
                                  ) : null}
                                </td>
                                <td>{formatTimestamp(alert.detected_at)}</td>
                                <td>{alert.run_id ?? "n/a"}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    ) : (
                      <p className="empty-state">No active runtime alerts.</p>
                    )}
                  </div>
                  <div>
                    <h3>Recent audit</h3>
                    {operatorVisibility.audit_events.length ? (
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
                          {operatorVisibility.audit_events.slice(0, 8).map((event) => (
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
                      <p className="empty-state">No runtime audit events recorded.</p>
                    )}
                  </div>
                </div>
              </PanelDisclosure>
              <PanelDisclosure
                defaultOpen={false}
                summary={`${operatorVisibility.incident_events.length} persisted incident events with delivery and remediation metadata.`}
                title="Incident events"
              >
                {operatorVisibility.incident_events.length ? (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>When</th>
                        <th>Kind</th>
                        <th>Severity</th>
                        <th>Summary</th>
                      </tr>
                    </thead>
                    <tbody>
                      {operatorVisibility.incident_events.slice(0, 8).map((event) => {
                        const linkedInstrument = linkedOperatorIncidentEventById.get(event.event_id) ?? null;
                        const primaryFocusNote = formatLinkedMarketPrimaryFocusNote(linkedInstrument);
                        const providerRecoveryProvenanceSummary =
                          summarizeProviderRecoveryMarketContextProvenance(
                            event.remediation.provider_recovery,
                          )?.summary ?? null;
                        return (
                          <tr key={`incident-${event.event_id}`}>
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
                                {event.provider_workflow_reference ? ` (${event.provider_workflow_reference})` : ""}
                                {event.provider_workflow_last_attempted_at
                                  ? ` at ${formatTimestamp(event.provider_workflow_last_attempted_at)}`
                                  : ""}
                              </p>
                              {linkedInstrument ? (
                                <>
                                  <button
                                    className="market-data-inline-focus-button"
                                    onClick={() => {
                                      void handleMarketInstrumentFocus(linkedInstrument.instrument);
                                    }}
                                    type="button"
                                  >
                                    Focus triage: {linkedInstrument.symbol} · {linkedInstrument.timeframe}
                                  </button>
                                  {primaryFocusNote ? (
                                    <p className="market-data-inline-focus-note">
                                      {primaryFocusNote}
                                    </p>
                                  ) : null}
                                </>
                              ) : null}
                              {event.remediation.state !== "not_applicable" ? (
                                <>
                                  <p className="run-lineage-symbol-copy">
                                    Remediation: {event.remediation.state}
                                    {event.remediation.summary ? ` / ${event.remediation.summary}` : ""}
                                    {event.remediation.runbook ? ` (${event.remediation.runbook})` : ""}
                                    {event.remediation.requested_by ? ` by ${event.remediation.requested_by}` : ""}
                                    {event.remediation.last_attempted_at
                                      ? ` at ${formatTimestamp(event.remediation.last_attempted_at)}`
                                      : ""}
                                  </p>
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
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                ) : (
                  <p className="empty-state">No persisted incident events recorded.</p>
                )}
              </PanelDisclosure>
              <PanelDisclosure
                defaultOpen={false}
                summary={`${operatorVisibility.alert_history.length} historical alert rows.`}
                title="Alert history"
              >
                {operatorVisibility.alert_history.length ? (
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
                      {operatorVisibility.alert_history.slice(0, 8).map((alert) => {
                        const occurrenceKey = getOperatorAlertOccurrenceKey(alert);
                        const linkedInstrument =
                          linkedOperatorAlertHistoryByOccurrenceId.get(occurrenceKey) ?? null;
                        const primaryFocusNote = formatLinkedMarketPrimaryFocusNote(linkedInstrument);
                        const timelineSummary = formatProviderProvenanceSchedulerTimelineSummary(alert);
                        const categoryTimeline =
                          providerProvenanceSchedulerAlertHistoryTimelineByCategory.get(alert.category) ?? [];
                        const timelinePreview = categoryTimeline
                          .map((entry) => {
                            const isCurrent = getOperatorAlertOccurrenceKey(entry.alert) === occurrenceKey;
                            const marker = `#${entry.alert.timeline_position ?? 1}${isCurrent ? "*" : ""}`;
                            const windowEnd = entry.alert.resolved_at ?? "active";
                            return `${marker} ${formatTimestamp(entry.alert.detected_at)} → ${formatTimestamp(windowEnd)}`;
                          })
                          .join(" · ");
                        return (
                          <tr key={`history-${occurrenceKey}`}>
                            <td>{alert.status}</td>
                            <td>{alert.severity}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                              {timelineSummary ? (
                                <p className="market-data-inline-focus-note">{timelineSummary}</p>
                              ) : null}
                              {alert.status === "resolved"
                              && isProviderProvenanceSchedulerAlertCategory(alert.category)
                              && categoryTimeline.length > 1 ? (
                                <p className="market-data-inline-focus-note">
                                  Timeline: {timelinePreview}
                                </p>
                              ) : null}
                              {isProviderProvenanceSchedulerAlertCategory(alert.category) ? (
                                <div className="market-data-provenance-history-actions">
                                  <button
                                    className="ghost-button"
                                    onClick={() => {
                                      void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                                        sourceLabel: `${alert.summary} history row`,
                                      });
                                    }}
                                    type="button"
                                  >
                                    {alert.status === "resolved" ? "Reconstruct narrative export" : "Start current workflow"}
                                  </button>
                                  <button
                                    className="ghost-button"
                                    onClick={() => {
                                      void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                                        escalate: true,
                                        sourceLabel: `${alert.summary} history row`,
                                      });
                                    }}
                                    type="button"
                                  >
                                    {alert.status === "resolved" ? "Escalate narrative export" : "Escalate current snapshot"}
                                  </button>
                                </div>
                              ) : null}
                              {linkedInstrument ? (
                                <>
                                  <button
                                    className="market-data-inline-focus-button"
                                    onClick={() => {
                                      void handleMarketInstrumentFocus(linkedInstrument.instrument);
                                    }}
                                    type="button"
                                  >
                                    Focus triage: {linkedInstrument.symbol} · {linkedInstrument.timeframe}
                                  </button>
                                  {primaryFocusNote ? (
                                    <p className="market-data-inline-focus-note">
                                      {primaryFocusNote}
                                    </p>
                                  ) : null}
                                </>
                              ) : null}
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                            <td>{formatTimestamp(alert.resolved_at ?? null)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                ) : (
                  <p className="empty-state">No persisted live-path alert history recorded.</p>
                )}
              </PanelDisclosure>
              <PanelDisclosure
                defaultOpen={false}
                summary={`${operatorVisibility.delivery_history.length} outbound delivery attempts.`}
                title="Delivery history"
              >
                {operatorVisibility.delivery_history.length ? (
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
                      {operatorVisibility.delivery_history.slice(0, 8).map((record, index) => (
                        <tr key={`delivery-${record.delivery_id}-${index}`}>
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
                  <p className="empty-state">No outbound delivery attempts recorded.</p>
                )}
              </PanelDisclosure>
            </div>
          ) : (
            <p>No operator visibility loaded.</p>
          )}
              </section>
  );
}
