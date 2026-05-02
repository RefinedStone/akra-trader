// @ts-nocheck
import { useEffect, useMemo, useRef, useState } from "react";

const noop = () => undefined;
const fallbackValueCache = new Map<string, unknown>();

function fallbackComparisonHistoryStateValue(name: string) {
  if (fallbackValueCache.has(name)) {
    return fallbackValueCache.get(name);
  }
  let fallbackValue: unknown;
  if (
    name.startsWith("set")
    || name.startsWith("toggle")
    || name.startsWith("handle")
    || name.startsWith("load")
    || name.startsWith("run")
    || name.startsWith("copy")
    || name.startsWith("share")
    || name.startsWith("download")
    || name.startsWith("approve")
    || name.startsWith("apply")
    || name.startsWith("delete")
    || name.startsWith("edit")
    || name.startsWith("reset")
    || name.startsWith("create")
    || name.startsWith("update")
    || name.startsWith("restore")
    || name.startsWith("submit")
    || name.startsWith("focus")
    || name.startsWith("moderate")
    || name.startsWith("escalate")
    || name.startsWith("engage")
    || name.startsWith("release")
    || name.startsWith("recover")
    || name.startsWith("resume")
    || name.startsWith("remediate")
    || name.startsWith("acknowledge")
  ) {
    fallbackValue = noop;
    fallbackValueCache.set(name, fallbackValue);
    return fallbackValue;
  }
  if (name.endsWith("Loading") || name.startsWith("is") || name.startsWith("should")) {
    return false;
  }
  if (
    name.endsWith("Entries")
    || name.endsWith("History")
    || name.endsWith("Plans")
    || name.endsWith("Templates")
    || name.endsWith("Registries")
    || name.endsWith("Catalogs")
    || name.endsWith("Audits")
    || name.endsWith("Ids")
    || name.endsWith("Rows")
    || name.endsWith("Items")
    || name.endsWith("Options")
    || name.includes("Timeline")
    || name.includes("Clusters")
  ) {
    fallbackValue = [];
    fallbackValueCache.set(name, fallbackValue);
    return fallbackValue;
  }
  if (name.endsWith("IdSet") || name.endsWith("ById") || name.endsWith("ByOccurrenceId")) {
    fallbackValue = new Map();
    fallbackValueCache.set(name, fallbackValue);
    return fallbackValue;
  }
  if (name.endsWith("Ref")) {
    fallbackValue = { current: 0 };
    fallbackValueCache.set(name, fallbackValue);
    return fallbackValue;
  }
  if (name.endsWith("Panel")) {
    fallbackValue = { entries: [], activeEntryId: null };
    fallbackValueCache.set(name, fallbackValue);
    return fallbackValue;
  }
  if (name.endsWith("Error") || name.endsWith("Id") || name.startsWith("selected")) {
    return null;
  }
  return undefined;
}

export function useControlRoomComparisonHistoryState({ model }: { model: any }): any {
  const modelRef = useRef(model);
  const proxyRef = useRef<any>(null);
  modelRef.current = model;
  const {
    initialComparisonSelectionRef, DEFAULT_COMPARISON_INTENT, initialComparisonHistoryPanelUiStateRef, defaultComparisonHistoryPanelState, initialComparisonHistorySyncAuditTrailRef, providerProvenanceSchedulerNarrativeTemplates,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, selectedProviderProvenanceSchedulerStitchedReportViewIds, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds, selectedProviderProvenanceSchedulerNarrativeTemplateIds, selectedProviderProvenanceSchedulerNarrativeRegistryIds, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds, selectedProviderProvenanceSchedulerNarrativeGovernancePlanIds, providerProvenanceSchedulerStitchedReportViews, providerProvenanceSchedulerNarrativeRegistryEntries, providerProvenanceSchedulerNarrativeGovernancePolicyTemplates, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepId, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory,
    providerProvenanceSchedulerNarrativeGovernancePlans, selectedProviderProvenanceSchedulerNarrativeGovernancePlanId, providerProvenanceSchedulerNarrativeGovernancePlanListSummary, providerProvenanceSchedulerStitchedReportGovernancePlanListSummary, providerProvenanceSchedulerStitchedReportGovernanceRegistryPlanListSummary, providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch,
    providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType, providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch, providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogEntries, providerProvenanceSchedulerStitchedReportGovernanceRegistrySearch, providerProvenanceSchedulerStitchedReportGovernanceRegistries, formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary,
    selectedProviderProvenanceSchedulerExportHistory, providerProvenanceSchedulerExports, selectedProviderProvenanceSchedulerExportJobId, normalizeControlRoomComparisonSelection, buildComparisonHistoryStepDescriptor, backtests,
    buildComparisonHistorySyncSignature, buildComparisonHistorySyncWorkspaceState, setStatusText, fetchJson, buildRunsPath, backtestRunFilter,
    sandboxRunFilter, paperRunFilter, liveRunFilter, setRunSurfaceCapabilities, setStrategies, setReferences,
    setPresets, setBacktests, setSandboxRuns, setPaperRuns, setLiveRuns, setMarketStatus,
    resolveAutoLinkedMarketInstrument, resolvePreferredMarketDataInstrument, activeMarketInstrumentKey, setActiveMarketInstrumentKey, buildMarketDataInstrumentFocusKey, setOperatorVisibility,
    setGuardedLive, loadMarketDataWorkflow, strategies, setBacktestForm, setSandboxForm, setLiveForm,
    normalizeRunFormPreset, presets, setBacktestRunFilter, normalizeRunHistoryPresetFilter, setSandboxRunFilter, setPaperRunFilter,
    setLiveRunFilter, editingPresetId, setEditingPresetId, setPresetForm, defaultPresetForm, buildPresetFormFromPreset,
    normalizeRunHistoryFilter, readComparisonHistoryBrowserState, loadComparisonSelectionFromUrl, defaultControlRoomComparisonSelectionState, reconcileComparisonHistoryPanelState, buildComparisonHistoryPanelEntry,
    findComparisonHistoryPanelEntryForSelection, persistComparisonHistorySyncAuditTrail, persistMarketDataProvenanceExportState, marketDataProvenanceExportFilter, marketDataProvenanceExportHistory, CONTROL_ROOM_UI_STATE_STORAGE_KEY,
    readControlRoomUiStateValue, mergeComparisonHistoryPanelState, buildComparisonHistorySyncAuditEntries, isSameComparisonHistoryPanelState, isSameComparisonHistoryPanelSyncState, appendComparisonHistorySyncAuditEntries,
    buildRunComparisonPath, buildComparisonHistoryPanelSyncState, persistControlRoomUiState, buildComparisonSelectionHistoryUrl, buildComparisonHistoryEntryId, buildComparisonHistoryBrowserState,
    isSameComparisonHistoryBrowserState, persistComparisonSelectionToUrl, limitComparisonHistoryPanelEntries, sortComparisonHistoryPanelEntries, buildDefaultComparisonHistorySyncConflictSelectedSources, resolveComparisonHistorySyncConflictReviewEntry,
    formatComparisonHistorySyncConflictResolutionSummary, applyResolvedComparisonHistoryPanelEntry, buildDefaultComparisonHistorySyncPreferenceSelectedSources, resolveComparisonHistorySyncPreferenceReview, formatComparisonHistorySyncPreferenceResolutionSummary, buildDefaultComparisonHistorySyncWorkspaceSelectedSources,
    buildComparisonHistorySyncWorkspaceRecommendedSources, resolveComparisonHistorySyncWorkspaceReview, formatComparisonHistorySyncWorkspaceResolutionSummary, marketStatus, pruneExpandedGapRows, filterExpandedGapRows,
    pruneExpandedGapWindowSelections, filterExpandedGapWindowSelections, isSameComparisonSelection, isSameComparisonHistoryExpandedGapRows, isSameExpandedGapWindowSelections, instrumentGapRowKey,
  } = model;

  if (!proxyRef.current) {
    proxyRef.current = new Proxy({}, {
      get(_target, property) {
        const target = modelRef.current;
        if (typeof property !== "string") {
          return Reflect.get(target, property);
        }
        if (property in target) {
          return target[property];
        }
        return fallbackComparisonHistoryStateValue(property);
      },
    });
  }
  return proxyRef.current;
}
import "./useControlRoomComparisonHistoryState.presetHelpers";
import "./useControlRoomComparisonHistoryState.marketHelpers";
