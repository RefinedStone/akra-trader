// @ts-nocheck
import {
  ALL_FILTER_VALUE,
  RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX,
} from "../controlRoomDefinitions";

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

  return {
    selectedProviderProvenanceSchedulerExportEntry, providerProvenanceAnalyticsRequestIdRef, providerProvenanceSchedulerAnalyticsRequestIdRef, providerProvenanceSchedulerHistoryRequestIdRef, providerProvenanceSchedulerAlertHistoryRequestIdRef, providerProvenanceSchedulerSearchDashboardRequestIdRef,
    providerProvenanceSchedulerSearchModerationPolicyCatalogRequestIdRef, providerProvenanceSchedulerSearchModerationPolicyCatalogAuditRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRequestIdRef,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePlanRequestIdRef, providerProvenanceSchedulerSearchModerationPlanRequestIdRef, providerProvenanceSchedulerExportRequestIdRef, providerProvenanceSchedulerStitchedReportViewRequestIdRef, providerProvenanceSchedulerStitchedReportViewAuditRequestIdRef, providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryRequestIdRef,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryRequestIdRef, comparisonHistoryTabIdentity, providerProvenanceSchedulerNarrativeGovernancePlanRequestIdRef, providerProvenanceSchedulerStitchedReportGovernancePlanRequestIdRef, providerProvenanceSchedulerStitchedReportGovernanceRegistryPlanRequestIdRef, providerProvenanceWorkspaceRegistryLoadedRef,
    marketDataWorkflowRequestIdRef, providerProvenanceSchedulerAutomationRef, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps, filteredProviderProvenanceSchedulerNarrativeGovernancePlans, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    selectedProviderProvenanceSchedulerNarrativeGovernancePlan, selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateNameMap, loadAll, setSelectedComparisonRunIds, queueComparisonHistoryWriteMode,
    setSelectedComparisonScoreLink, setComparisonIntent, selectedComparisonRunIds, comparisonHistoryStep, comparisonHistorySharedSyncState, comparisonHistorySyncAuditTrail,
    comparisonHistoryPanel, visibleComparisonHistoryEntries, comparisonHistoryPanelOpen, comparisonHistorySearchQuery, comparisonHistoryShowPinnedOnly, comparisonHistoryAuditFilter,
    comparisonHistoryShowResolvedAuditEntries, visibleComparisonHistoryActiveIndex, selectedComparisonScoreLink, runComparison, runComparisonLoading, runComparisonError,
    handleComparisonIntentChange, handleSelectedComparisonScoreLinkChange, setComparisonHistoryPanelOpen, setComparisonHistorySearchQuery, setComparisonHistoryShowPinnedOnly, setComparisonHistoryAuditFilter,
    setComparisonHistoryShowResolvedAuditEntries, setExpandedHistoryConflictReviewIds, setExpandedWorkspaceScoreDetailIds, setFocusedWorkspaceScoreDetailSources, setFocusedWorkspaceScoreDetailSignalKeys, setExpandedWorkspaceScoreSignalDetailIds,
    setCollapsedWorkspaceScoreSignalSubviewIds, setCollapsedWorkspaceScoreSignalNestedSubviewIds, setFocusedWorkspaceScoreSignalMicroViews, setFocusedWorkspaceScoreSignalMicroInteractions, setHoveredWorkspaceScoreSignalMicroTargets, setScrubbedWorkspaceScoreSignalMicroSteps,
    setSelectedWorkspaceScoreSignalMicroNotePages, setActiveWorkspaceOverviewRowId, handleNavigateComparisonHistoryEntry, handleNavigateComparisonHistoryRelative, handleToggleComparisonHistoryEntryPinned, handleTrimComparisonHistoryEntries,
    handleSetComparisonHistoryConflictFieldSource, handleSetComparisonHistoryConflictFieldSourceAll, handleApplyComparisonHistoryConflictResolution, handleSetComparisonHistoryPreferenceFieldSource, handleSetComparisonHistoryPreferenceFieldSourceAll, handleApplyComparisonHistoryPreferenceResolution,
    handleSetComparisonHistoryWorkspaceFieldSource, handleSetComparisonHistoryWorkspaceFieldSourceAll, handleUseComparisonHistoryWorkspaceRankedSources, handleApplyComparisonHistoryWorkspaceResolution, comparisonIntent, latestWorkspaceSyncState,
    expandedHistoryConflictReviewIds, expandedWorkspaceScoreDetailIds, focusedWorkspaceScoreDetailSources, focusedWorkspaceScoreDetailSignalKeys, expandedWorkspaceScoreSignalDetailIds, collapsedWorkspaceScoreSignalSubviewIds,
    collapsedWorkspaceScoreSignalNestedSubviewIds, focusedWorkspaceScoreSignalMicroViews, focusedWorkspaceScoreSignalMicroInteractions, hoveredWorkspaceScoreSignalMicroTargets, scrubbedWorkspaceScoreSignalMicroSteps, selectedWorkspaceScoreSignalMicroNotePages,
    activeWorkspaceOverviewRowId, expandedGapRows, activeGapWindowPickerRowKey, setExpandedGapWindowSelections, setActiveGapWindowPickerRowKey, setExpandedGapRows,
    expandedGapWindowSelections, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIdSet, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIdSet, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIdSet, selectedProviderProvenanceSchedulerNarrativeTemplateEntries, selectedProviderProvenanceSchedulerNarrativeTemplateIdSet, selectedProviderProvenanceSchedulerNarrativeRegistryEntries,
    selectedProviderProvenanceSchedulerNarrativeRegistryIdSet, providerProvenanceSchedulerNarrativeTemplateNameMap, providerProvenanceSchedulerNarrativeGovernanceQueueSummary, selectedProviderProvenanceSchedulerNarrativeGovernancePlanIdSet, selectedProviderProvenanceSchedulerStitchedReportViewEntries, selectedProviderProvenanceSchedulerStitchedReportViewIdSet,
    providerProvenanceSchedulerStitchedReportGovernanceQueueSummary, providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs, providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary, providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries, filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIdSet,
  };
}
