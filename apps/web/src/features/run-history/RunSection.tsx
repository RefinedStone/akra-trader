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

function formatRelativeTimestampLabel(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) {
    return formatTimestamp(value);
  }
  const relative = formatComparisonTooltipConflictSessionRelativeTime(timestamp, new Date());
  return relative ? `${relative} · ${formatTimestamp(value)}` : formatTimestamp(value);
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

function instrumentGapRowKey(instrument: MarketDataStatus["instruments"][number]) {
  return `${instrument.instrument_id}:${instrument.timeframe}`;
}

function buildComparisonHistorySyncAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `compare-sync-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
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

function RunComparisonPanel({
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

const ComparisonTooltipBubble = forwardRef<
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

function ComparisonTooltipTuningPanel({
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

function ComparisonTooltipTuningField({
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

function formatComparisonTooltipConflictSessionSummary(
  summary: Omit<ComparisonTooltipConflictSessionSummary, "label">,
) {
  if (summary.session_count === 1) {
    return summary.preset_name;
  }
  return `${summary.preset_name} (${summary.session_count} saved sessions)`;
}

function formatComparisonTooltipConflictSessionSummarySession(
  session: Omit<ComparisonTooltipConflictSessionSummarySession, "label">,
  index: number,
  totalSessions: number,
) {
  if (totalSessions === 1) {
    return "Saved session";
  }
  return `Saved session ${index + 1}`;
}

function formatComparisonTooltipConflictSessionMetadata(
  session: ComparisonTooltipConflictSessionUiState,
  hash: string | null,
  referenceNowMs: number,
) {
  const metadata: string[] = [];
  metadata.push(
    formatComparisonTooltipConflictSessionUpdatedAtLabel(session.updated_at, referenceNowMs),
  );
  metadata.push(
    session.show_unchanged_conflict_rows ? "unchanged rows visible" : "unchanged rows hidden",
  );

  const groupStates = Object.values(session.collapsed_unchanged_groups);
  const collapsedCount = groupStates.filter(Boolean).length;
  const expandedCount = groupStates.length - collapsedCount;

  if (!groupStates.length) {
    metadata.push("default group layout");
    return metadata;
  }

  if (expandedCount && collapsedCount) {
    metadata.push(`${expandedCount} expanded, ${collapsedCount} collapsed`);
    return metadata;
  }
  if (expandedCount) {
    metadata.push(`${expandedCount} expanded group${expandedCount === 1 ? "" : "s"}`);
  } else {
    metadata.push(`${collapsedCount} collapsed group${collapsedCount === 1 ? "" : "s"}`);
  }
  if (hash) {
    metadata.push(`ID ${hash.slice(0, 8)}`);
  }
  return metadata;
}

function parseComparisonTooltipConflictSessionUpdatedAt(value: string | null) {
  if (!value) {
    return 0;
  }
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) ? timestamp : 0;
}

function formatComparisonTooltipConflictSessionUpdatedAtLabel(
  value: string | null,
  referenceNowMs: number,
) {
  const timestamp = parseComparisonTooltipConflictSessionUpdatedAt(value);
  if (!timestamp) {
    return "updated time unavailable";
  }
  const date = new Date(timestamp);
  const now = new Date(referenceNowMs);
  const absoluteLabel = new Intl.DateTimeFormat(undefined, {
    ...(date.getFullYear() === now.getFullYear() ? {} : { year: "numeric" }),
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    month: "short",
  }).format(date);
  const relativeLabel = formatComparisonTooltipConflictSessionRelativeTime(timestamp, now);
  return relativeLabel
    ? `updated ${relativeLabel} · ${absoluteLabel}`
    : `updated ${absoluteLabel}`;
}

export function formatComparisonTooltipConflictSessionRelativeTime(
  timestamp: number,
  now: Date,
) {
  const elapsedMs = timestamp - now.getTime();
  const absElapsedMs = Math.abs(elapsedMs);
  const minuteMs = 60 * 1000;
  const hourMs = 60 * minuteMs;
  const dayMs = 24 * hourMs;
  const weekMs = 7 * dayMs;
  const monthMs = 30 * dayMs;
  const yearMs = 365 * dayMs;

  const formatRelative = (value: number, unit: Intl.RelativeTimeFormatUnit) =>
    new Intl.RelativeTimeFormat(undefined, { numeric: "auto", style: "short" }).format(
      value,
      unit,
    );

  if (absElapsedMs < minuteMs) {
    return formatRelative(Math.round(elapsedMs / 1000), "second");
  }
  if (absElapsedMs < hourMs) {
    return formatRelative(Math.round(elapsedMs / minuteMs), "minute");
  }
  if (absElapsedMs < dayMs) {
    return formatRelative(Math.round(elapsedMs / hourMs), "hour");
  }
  if (absElapsedMs < weekMs) {
    return formatRelative(Math.round(elapsedMs / dayMs), "day");
  }
  if (absElapsedMs < monthMs) {
    return formatRelative(Math.round(elapsedMs / weekMs), "week");
  }
  if (absElapsedMs < yearMs) {
    return formatRelative(Math.round(elapsedMs / monthMs), "month");
  }
  return formatRelative(Math.round(elapsedMs / yearMs), "year");
}

function getComparisonTooltipConflictSessionRelativeTimeRefreshMs(
  timestamps: number[],
  referenceNowMs: number,
) {
  if (!timestamps.length) {
    return null;
  }

  const youngestAgeMs = timestamps.reduce((youngest, timestamp) => {
    const ageMs = Math.abs(referenceNowMs - timestamp);
    return Math.min(youngest, ageMs);
  }, Number.POSITIVE_INFINITY);

  const minuteMs = 60 * 1000;
  const hourMs = 60 * minuteMs;
  const dayMs = 24 * hourMs;
  const weekMs = 7 * dayMs;
  const monthMs = 30 * dayMs;

  if (youngestAgeMs < minuteMs) {
    return 5 * 1000;
  }
  if (youngestAgeMs < hourMs) {
    return minuteMs;
  }
  if (youngestAgeMs < dayMs) {
    return 5 * minuteMs;
  }
  if (youngestAgeMs < weekMs) {
    return hourMs;
  }
  if (youngestAgeMs < monthMs) {
    return 6 * hourMs;
  }
  return dayMs;
}

function hashComparisonTooltipConflictSessionRaw(value: string) {
  let hash = 5381;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 33) ^ value.charCodeAt(index);
  }
  return (hash >>> 0).toString(36);
}

export function formatComparisonTooltipTuningValue(value: number) {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(2).replace(/\.?0+$/, "");
}

function formatComparisonTooltipTuningDelta(existingValue: number, incomingValue: number) {
  const delta = incomingValue - existingValue;
  if (delta === 0) {
    return {
      direction: "same" as const,
      label: "match",
    };
  }
  return {
    direction: delta > 0 ? ("higher" as const) : ("lower" as const),
    label: `${delta > 0 ? "higher " : "lower "}${delta > 0 ? "+" : ""}${formatComparisonTooltipTuningValue(delta)}`,
  };
}

function formatComparisonTooltipPresetConflictGroupSummary(
  rows: ComparisonTooltipPresetConflictPreviewRow[],
) {
  const changedCount = rows.filter((row) => row.changed).length;
  const higherCount = rows.filter((row) => row.delta_direction === "higher").length;
  const lowerCount = rows.filter((row) => row.delta_direction === "lower").length;
  const sameCount = rows.filter((row) => row.delta_direction === "same").length;

  if (!changedCount) {
    return `${sameCount} match${sameCount === 1 ? "" : "es"}`;
  }

  const parts = [`${changedCount} changed`];
  if (higherCount) {
    parts.push(`${higherCount} higher`);
  }
  if (lowerCount) {
    parts.push(`${lowerCount} lower`);
  }
  if (sameCount) {
    parts.push(`${sameCount} match${sameCount === 1 ? "" : "es"}`);
  }
  return parts.join(" · ");
}

function formatComparisonTooltipPresetImportFeedback(
  resolution: ComparisonTooltipPresetImportResolution,
  options?: { verb?: "Imported" | "Loaded" },
) {
  const verb = options?.verb ?? "Imported";
  if (!resolution.conflicted) {
    return `${verb} preset "${resolution.final_preset_name}" into the current tuning bundle.`;
  }
  if (resolution.renamed) {
    return `${verb} preset "${resolution.imported_preset_name}" as "${resolution.final_preset_name}" because that name already existed.`;
  }
  return `${verb} preset "${resolution.final_preset_name}" and overwrote the existing preset with the same name.`;
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

function ReferenceRunProvenanceSummary({
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

function RunStrategySnapshot({
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

function RunRuntimeSessionSummary({
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

function RunOrderLifecycleSummary({
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

function RunOrderActionControls({
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

function RunMarketDataLineage({
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

function formatTimestamp(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value;
}

function formatProviderRecoverySchema(providerRecovery: {
  provider_schema_kind?: string | null;
  pagerduty: {
    incident_id?: string | null;
    incident_key?: string | null;
    incident_status: string;
    urgency?: string | null;
    service_summary?: string | null;
    escalation_policy_summary?: string | null;
    last_status_change_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      responder_phase: string;
      urgency_phase: string;
      last_transition_at?: string | null;
    };
  };
  opsgenie: {
    alert_id?: string | null;
    alias?: string | null;
    alert_status: string;
    priority?: string | null;
    owner?: string | null;
    teams: string[];
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      acknowledgment_phase: string;
      ownership_phase: string;
      visibility_phase: string;
      last_transition_at?: string | null;
    };
  };
  incidentio: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    mode?: string | null;
    visibility?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      assignment_phase: string;
      visibility_phase: string;
      severity_phase: string;
      last_transition_at?: string | null;
    };
  };
  firehydrant: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    priority?: string | null;
    team?: string | null;
    runbook?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      priority_phase: string;
      last_transition_at?: string | null;
    };
  };
  rootly: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity_id?: string | null;
    private?: boolean | null;
    slug?: string | null;
    url?: string | null;
    acknowledged_at?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      acknowledgment_phase: string;
      visibility_phase: string;
      severity_phase: string;
      last_transition_at?: string | null;
    };
  };
  blameless: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    commander?: string | null;
    visibility?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      command_phase: string;
      visibility_phase: string;
      severity_phase: string;
      last_transition_at?: string | null;
    };
  };
  xmatters: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    assignee?: string | null;
    response_plan?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      response_plan_phase: string;
      last_transition_at?: string | null;
    };
  };
  servicenow: {
    incident_number?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    assigned_to?: string | null;
    assignment_group?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      assignment_phase: string;
      priority_phase: string;
      group_phase: string;
      last_transition_at?: string | null;
    };
  };
  squadcast: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    escalation_policy?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  bigpanda: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    team?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      team_phase: string;
      last_transition_at?: string | null;
    };
  };
  grafana_oncall: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    escalation_chain?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  splunk_oncall: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    routing_key?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      routing_phase: string;
      last_transition_at?: string | null;
    };
  };
  jira_service_management: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    assignee?: string | null;
    service_project?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      assignment_phase: string;
      priority_phase: string;
      project_phase: string;
      last_transition_at?: string | null;
    };
  };
  pagertree: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    urgency?: string | null;
    assignee?: string | null;
    team?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      urgency_phase: string;
      team_phase: string;
      last_transition_at?: string | null;
    };
  };
  alertops: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    owner?: string | null;
    service?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      service_phase: string;
      last_transition_at?: string | null;
    };
  };
  signl4: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    team?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      team_phase: string;
      last_transition_at?: string | null;
    };
  };
  ilert: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  betterstack: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  onpage: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  allquiet: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  moogsoft: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  spikesh: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  dutycalls: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  incidenthub: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  resolver: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  openduty: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  cabot: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  haloitsm: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  incidentmanagerio: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  oneuptime: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  squzy: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  crisescontrol: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  freshservice: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  freshdesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  happyfox: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  zendesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  zohodesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  helpscout: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  kayako: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  intercom: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  front: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  servicedeskplus: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  sysaid: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  bmchelix: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  solarwindsservicedesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  topdesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  invgateservicedesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  opsramp: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  zenduty: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    service?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      service_phase: string;
      last_transition_at?: string | null;
    };
  };
}) {
  if (providerRecovery.provider_schema_kind === "pagerduty") {
    const details = [
      providerRecovery.pagerduty.incident_id ? `incident ${providerRecovery.pagerduty.incident_id}` : null,
      providerRecovery.pagerduty.incident_status !== "unknown"
        ? `status ${providerRecovery.pagerduty.incident_status}`
        : null,
      providerRecovery.pagerduty.urgency ? `urgency ${providerRecovery.pagerduty.urgency}` : null,
      providerRecovery.pagerduty.service_summary ? `service ${providerRecovery.pagerduty.service_summary}` : null,
      providerRecovery.pagerduty.escalation_policy_summary
        ? `policy ${providerRecovery.pagerduty.escalation_policy_summary}`
        : null,
      providerRecovery.pagerduty.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.pagerduty.phase_graph.incident_phase}`
        : null,
      providerRecovery.pagerduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.pagerduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.pagerduty.phase_graph.responder_phase !== "unknown"
        ? `responder ${providerRecovery.pagerduty.phase_graph.responder_phase}`
        : null,
      providerRecovery.pagerduty.last_status_change_at
        ? `changed ${formatTimestamp(providerRecovery.pagerduty.last_status_change_at)}`
        : null,
      providerRecovery.pagerduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.pagerduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `PagerDuty schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "opsgenie") {
    const details = [
      providerRecovery.opsgenie.alert_id ? `alert ${providerRecovery.opsgenie.alert_id}` : null,
      providerRecovery.opsgenie.alert_status !== "unknown"
        ? `status ${providerRecovery.opsgenie.alert_status}`
        : null,
      providerRecovery.opsgenie.priority ? `priority ${providerRecovery.opsgenie.priority}` : null,
      providerRecovery.opsgenie.owner ? `owner ${providerRecovery.opsgenie.owner}` : null,
      providerRecovery.opsgenie.teams.length
        ? `teams ${providerRecovery.opsgenie.teams.join(", ")}`
        : null,
      providerRecovery.opsgenie.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.opsgenie.phase_graph.alert_phase}`
        : null,
      providerRecovery.opsgenie.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.opsgenie.phase_graph.workflow_phase}`
        : null,
      providerRecovery.opsgenie.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.opsgenie.phase_graph.ownership_phase}`
        : null,
      providerRecovery.opsgenie.updated_at
        ? `updated ${formatTimestamp(providerRecovery.opsgenie.updated_at)}`
        : null,
      providerRecovery.opsgenie.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.opsgenie.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Opsgenie schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidentio") {
    const details = [
      providerRecovery.incidentio.incident_id ? `incident ${providerRecovery.incidentio.incident_id}` : null,
      providerRecovery.incidentio.incident_status !== "unknown"
        ? `status ${providerRecovery.incidentio.incident_status}`
        : null,
      providerRecovery.incidentio.severity ? `severity ${providerRecovery.incidentio.severity}` : null,
      providerRecovery.incidentio.assignee ? `assignee ${providerRecovery.incidentio.assignee}` : null,
      providerRecovery.incidentio.visibility ? `visibility ${providerRecovery.incidentio.visibility}` : null,
      providerRecovery.incidentio.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.incidentio.phase_graph.incident_phase}`
        : null,
      providerRecovery.incidentio.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidentio.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidentio.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.incidentio.phase_graph.assignment_phase}`
        : null,
      providerRecovery.incidentio.updated_at
        ? `updated ${formatTimestamp(providerRecovery.incidentio.updated_at)}`
        : null,
      providerRecovery.incidentio.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidentio.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `incident.io schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "firehydrant") {
    const details = [
      providerRecovery.firehydrant.incident_id
        ? `incident ${providerRecovery.firehydrant.incident_id}`
        : null,
      providerRecovery.firehydrant.incident_status !== "unknown"
        ? `status ${providerRecovery.firehydrant.incident_status}`
        : null,
      providerRecovery.firehydrant.severity ? `severity ${providerRecovery.firehydrant.severity}` : null,
      providerRecovery.firehydrant.priority ? `priority ${providerRecovery.firehydrant.priority}` : null,
      providerRecovery.firehydrant.team ? `team ${providerRecovery.firehydrant.team}` : null,
      providerRecovery.firehydrant.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.firehydrant.phase_graph.incident_phase}`
        : null,
      providerRecovery.firehydrant.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.firehydrant.phase_graph.workflow_phase}`
        : null,
      providerRecovery.firehydrant.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.firehydrant.phase_graph.ownership_phase}`
        : null,
      providerRecovery.firehydrant.updated_at
        ? `updated ${formatTimestamp(providerRecovery.firehydrant.updated_at)}`
        : null,
      providerRecovery.firehydrant.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.firehydrant.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `FireHydrant schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "rootly") {
    const details = [
      providerRecovery.rootly.incident_id ? `incident ${providerRecovery.rootly.incident_id}` : null,
      providerRecovery.rootly.incident_status !== "unknown"
        ? `status ${providerRecovery.rootly.incident_status}`
        : null,
      providerRecovery.rootly.severity_id ? `severity ${providerRecovery.rootly.severity_id}` : null,
      providerRecovery.rootly.private === true
        ? "private"
        : providerRecovery.rootly.private === false
          ? "public"
          : null,
      providerRecovery.rootly.slug ? `slug ${providerRecovery.rootly.slug}` : null,
      providerRecovery.rootly.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.rootly.phase_graph.incident_phase}`
        : null,
      providerRecovery.rootly.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.rootly.phase_graph.workflow_phase}`
        : null,
      providerRecovery.rootly.phase_graph.acknowledgment_phase !== "unknown"
        ? `ack ${providerRecovery.rootly.phase_graph.acknowledgment_phase}`
        : null,
      providerRecovery.rootly.updated_at
        ? `updated ${formatTimestamp(providerRecovery.rootly.updated_at)}`
        : null,
      providerRecovery.rootly.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.rootly.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Rootly schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "blameless") {
    const details = [
      providerRecovery.blameless.incident_id ? `incident ${providerRecovery.blameless.incident_id}` : null,
      providerRecovery.blameless.incident_status !== "unknown"
        ? `status ${providerRecovery.blameless.incident_status}`
        : null,
      providerRecovery.blameless.severity ? `severity ${providerRecovery.blameless.severity}` : null,
      providerRecovery.blameless.commander ? `commander ${providerRecovery.blameless.commander}` : null,
      providerRecovery.blameless.visibility ? `visibility ${providerRecovery.blameless.visibility}` : null,
      providerRecovery.blameless.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.blameless.phase_graph.incident_phase}`
        : null,
      providerRecovery.blameless.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.blameless.phase_graph.workflow_phase}`
        : null,
      providerRecovery.blameless.phase_graph.command_phase !== "unknown"
        ? `command ${providerRecovery.blameless.phase_graph.command_phase}`
        : null,
      providerRecovery.blameless.updated_at
        ? `updated ${formatTimestamp(providerRecovery.blameless.updated_at)}`
        : null,
      providerRecovery.blameless.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.blameless.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Blameless schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "xmatters") {
    const details = [
      providerRecovery.xmatters.incident_id ? `incident ${providerRecovery.xmatters.incident_id}` : null,
      providerRecovery.xmatters.incident_status !== "unknown"
        ? `status ${providerRecovery.xmatters.incident_status}`
        : null,
      providerRecovery.xmatters.priority ? `priority ${providerRecovery.xmatters.priority}` : null,
      providerRecovery.xmatters.assignee ? `assignee ${providerRecovery.xmatters.assignee}` : null,
      providerRecovery.xmatters.response_plan
        ? `response plan ${providerRecovery.xmatters.response_plan}`
        : null,
      providerRecovery.xmatters.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.xmatters.phase_graph.incident_phase}`
        : null,
      providerRecovery.xmatters.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.xmatters.phase_graph.workflow_phase}`
        : null,
      providerRecovery.xmatters.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.xmatters.phase_graph.ownership_phase}`
        : null,
      providerRecovery.xmatters.updated_at
        ? `updated ${formatTimestamp(providerRecovery.xmatters.updated_at)}`
        : null,
      providerRecovery.xmatters.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.xmatters.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `xMatters schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "servicenow") {
    const details = [
      providerRecovery.servicenow.incident_number
        ? `incident ${providerRecovery.servicenow.incident_number}`
        : null,
      providerRecovery.servicenow.incident_status !== "unknown"
        ? `status ${providerRecovery.servicenow.incident_status}`
        : null,
      providerRecovery.servicenow.priority ? `priority ${providerRecovery.servicenow.priority}` : null,
      providerRecovery.servicenow.assigned_to
        ? `assigned to ${providerRecovery.servicenow.assigned_to}`
        : null,
      providerRecovery.servicenow.assignment_group
        ? `group ${providerRecovery.servicenow.assignment_group}`
        : null,
      providerRecovery.servicenow.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.servicenow.phase_graph.incident_phase}`
        : null,
      providerRecovery.servicenow.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.servicenow.phase_graph.workflow_phase}`
        : null,
      providerRecovery.servicenow.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.servicenow.phase_graph.assignment_phase}`
        : null,
      providerRecovery.servicenow.updated_at
        ? `updated ${formatTimestamp(providerRecovery.servicenow.updated_at)}`
        : null,
      providerRecovery.servicenow.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.servicenow.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `ServiceNow schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "squadcast") {
    const details = [
      providerRecovery.squadcast.incident_id ? `incident ${providerRecovery.squadcast.incident_id}` : null,
      providerRecovery.squadcast.incident_status !== "unknown"
        ? `status ${providerRecovery.squadcast.incident_status}`
        : null,
      providerRecovery.squadcast.severity ? `severity ${providerRecovery.squadcast.severity}` : null,
      providerRecovery.squadcast.assignee ? `assignee ${providerRecovery.squadcast.assignee}` : null,
      providerRecovery.squadcast.escalation_policy
        ? `policy ${providerRecovery.squadcast.escalation_policy}`
        : null,
      providerRecovery.squadcast.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.squadcast.phase_graph.incident_phase}`
        : null,
      providerRecovery.squadcast.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.squadcast.phase_graph.workflow_phase}`
        : null,
      providerRecovery.squadcast.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.squadcast.phase_graph.ownership_phase}`
        : null,
      providerRecovery.squadcast.updated_at
        ? `updated ${formatTimestamp(providerRecovery.squadcast.updated_at)}`
        : null,
      providerRecovery.squadcast.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.squadcast.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Squadcast schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "bigpanda") {
    const details = [
      providerRecovery.bigpanda.incident_id ? `incident ${providerRecovery.bigpanda.incident_id}` : null,
      providerRecovery.bigpanda.incident_status !== "unknown"
        ? `status ${providerRecovery.bigpanda.incident_status}`
        : null,
      providerRecovery.bigpanda.severity ? `severity ${providerRecovery.bigpanda.severity}` : null,
      providerRecovery.bigpanda.assignee ? `assignee ${providerRecovery.bigpanda.assignee}` : null,
      providerRecovery.bigpanda.team ? `team ${providerRecovery.bigpanda.team}` : null,
      providerRecovery.bigpanda.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.bigpanda.phase_graph.incident_phase}`
        : null,
      providerRecovery.bigpanda.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.bigpanda.phase_graph.workflow_phase}`
        : null,
      providerRecovery.bigpanda.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.bigpanda.phase_graph.ownership_phase}`
        : null,
      providerRecovery.bigpanda.updated_at
        ? `updated ${formatTimestamp(providerRecovery.bigpanda.updated_at)}`
        : null,
      providerRecovery.bigpanda.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.bigpanda.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `BigPanda schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "grafana_oncall") {
    const details = [
      providerRecovery.grafana_oncall.incident_id
        ? `incident ${providerRecovery.grafana_oncall.incident_id}`
        : null,
      providerRecovery.grafana_oncall.incident_status !== "unknown"
        ? `status ${providerRecovery.grafana_oncall.incident_status}`
        : null,
      providerRecovery.grafana_oncall.severity
        ? `severity ${providerRecovery.grafana_oncall.severity}`
        : null,
      providerRecovery.grafana_oncall.assignee
        ? `assignee ${providerRecovery.grafana_oncall.assignee}`
        : null,
      providerRecovery.grafana_oncall.escalation_chain
        ? `chain ${providerRecovery.grafana_oncall.escalation_chain}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.grafana_oncall.phase_graph.incident_phase}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.grafana_oncall.phase_graph.workflow_phase}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.grafana_oncall.phase_graph.ownership_phase}`
        : null,
      providerRecovery.grafana_oncall.updated_at
        ? `updated ${formatTimestamp(providerRecovery.grafana_oncall.updated_at)}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.grafana_oncall.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Grafana OnCall schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "splunk_oncall") {
    const details = [
      providerRecovery.splunk_oncall.incident_id
        ? `incident ${providerRecovery.splunk_oncall.incident_id}`
        : null,
      providerRecovery.splunk_oncall.incident_status !== "unknown"
        ? `status ${providerRecovery.splunk_oncall.incident_status}`
        : null,
      providerRecovery.splunk_oncall.severity
        ? `severity ${providerRecovery.splunk_oncall.severity}`
        : null,
      providerRecovery.splunk_oncall.assignee
        ? `assignee ${providerRecovery.splunk_oncall.assignee}`
        : null,
      providerRecovery.splunk_oncall.routing_key
        ? `routing ${providerRecovery.splunk_oncall.routing_key}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.splunk_oncall.phase_graph.incident_phase}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.splunk_oncall.phase_graph.workflow_phase}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.splunk_oncall.phase_graph.ownership_phase}`
        : null,
      providerRecovery.splunk_oncall.updated_at
        ? `updated ${formatTimestamp(providerRecovery.splunk_oncall.updated_at)}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.splunk_oncall.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Splunk On-Call schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "jira_service_management") {
    const details = [
      providerRecovery.jira_service_management.incident_id
        ? `incident ${providerRecovery.jira_service_management.incident_id}`
        : null,
      providerRecovery.jira_service_management.incident_status !== "unknown"
        ? `status ${providerRecovery.jira_service_management.incident_status}`
        : null,
      providerRecovery.jira_service_management.priority
        ? `priority ${providerRecovery.jira_service_management.priority}`
        : null,
      providerRecovery.jira_service_management.assignee
        ? `assignee ${providerRecovery.jira_service_management.assignee}`
        : null,
      providerRecovery.jira_service_management.service_project
        ? `project ${providerRecovery.jira_service_management.service_project}`
        : null,
      providerRecovery.jira_service_management.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.jira_service_management.phase_graph.incident_phase}`
        : null,
      providerRecovery.jira_service_management.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.jira_service_management.phase_graph.workflow_phase}`
        : null,
      providerRecovery.jira_service_management.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.jira_service_management.phase_graph.assignment_phase}`
        : null,
      providerRecovery.jira_service_management.updated_at
        ? `updated ${formatTimestamp(providerRecovery.jira_service_management.updated_at)}`
        : null,
      providerRecovery.jira_service_management.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.jira_service_management.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `Jira Service Management schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "pagertree") {
    const details = [
      providerRecovery.pagertree.incident_id ? `incident ${providerRecovery.pagertree.incident_id}` : null,
      providerRecovery.pagertree.incident_status !== "unknown"
        ? `status ${providerRecovery.pagertree.incident_status}`
        : null,
      providerRecovery.pagertree.urgency ? `urgency ${providerRecovery.pagertree.urgency}` : null,
      providerRecovery.pagertree.assignee ? `assignee ${providerRecovery.pagertree.assignee}` : null,
      providerRecovery.pagertree.team ? `team ${providerRecovery.pagertree.team}` : null,
      providerRecovery.pagertree.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.pagertree.phase_graph.incident_phase}`
        : null,
      providerRecovery.pagertree.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.pagertree.phase_graph.workflow_phase}`
        : null,
      providerRecovery.pagertree.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.pagertree.phase_graph.ownership_phase}`
        : null,
      providerRecovery.pagertree.updated_at
        ? `updated ${formatTimestamp(providerRecovery.pagertree.updated_at)}`
        : null,
      providerRecovery.pagertree.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.pagertree.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `PagerTree schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "alertops") {
    const details = [
      providerRecovery.alertops.incident_id ? `incident ${providerRecovery.alertops.incident_id}` : null,
      providerRecovery.alertops.incident_status !== "unknown"
        ? `status ${providerRecovery.alertops.incident_status}`
        : null,
      providerRecovery.alertops.priority ? `priority ${providerRecovery.alertops.priority}` : null,
      providerRecovery.alertops.owner ? `owner ${providerRecovery.alertops.owner}` : null,
      providerRecovery.alertops.service ? `service ${providerRecovery.alertops.service}` : null,
      providerRecovery.alertops.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.alertops.phase_graph.incident_phase}`
        : null,
      providerRecovery.alertops.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.alertops.phase_graph.workflow_phase}`
        : null,
      providerRecovery.alertops.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.alertops.phase_graph.ownership_phase}`
        : null,
      providerRecovery.alertops.updated_at
        ? `updated ${formatTimestamp(providerRecovery.alertops.updated_at)}`
        : null,
      providerRecovery.alertops.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.alertops.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `AlertOps schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "signl4") {
    const details = [
      providerRecovery.signl4.alert_id ? `alert ${providerRecovery.signl4.alert_id}` : null,
      providerRecovery.signl4.alert_status !== "unknown"
        ? `status ${providerRecovery.signl4.alert_status}`
        : null,
      providerRecovery.signl4.priority ? `priority ${providerRecovery.signl4.priority}` : null,
      providerRecovery.signl4.team ? `team ${providerRecovery.signl4.team}` : null,
      providerRecovery.signl4.assignee ? `assignee ${providerRecovery.signl4.assignee}` : null,
      providerRecovery.signl4.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.signl4.phase_graph.alert_phase}`
        : null,
      providerRecovery.signl4.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.signl4.phase_graph.workflow_phase}`
        : null,
      providerRecovery.signl4.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.signl4.phase_graph.ownership_phase}`
        : null,
      providerRecovery.signl4.phase_graph.priority_phase !== "unknown"
        ? `priority phase ${providerRecovery.signl4.phase_graph.priority_phase}`
        : null,
      providerRecovery.signl4.phase_graph.team_phase !== "unknown"
        ? `team phase ${providerRecovery.signl4.phase_graph.team_phase}`
        : null,
      providerRecovery.signl4.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.signl4.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `SIGNL4 schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "ilert") {
    const details = [
      providerRecovery.ilert.alert_id ? `alert ${providerRecovery.ilert.alert_id}` : null,
      providerRecovery.ilert.alert_status !== "unknown"
        ? `status ${providerRecovery.ilert.alert_status}`
        : null,
      providerRecovery.ilert.priority ? `priority ${providerRecovery.ilert.priority}` : null,
      providerRecovery.ilert.escalation_policy
        ? `policy ${providerRecovery.ilert.escalation_policy}`
        : null,
      providerRecovery.ilert.assignee ? `assignee ${providerRecovery.ilert.assignee}` : null,
      providerRecovery.ilert.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.ilert.phase_graph.alert_phase}`
        : null,
      providerRecovery.ilert.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.ilert.phase_graph.workflow_phase}`
        : null,
      providerRecovery.ilert.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.ilert.phase_graph.ownership_phase}`
        : null,
      providerRecovery.ilert.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.ilert.phase_graph.escalation_phase}`
        : null,
      providerRecovery.ilert.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.ilert.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `iLert schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "betterstack") {
    const details = [
      providerRecovery.betterstack.alert_id ? `alert ${providerRecovery.betterstack.alert_id}` : null,
      providerRecovery.betterstack.alert_status !== "unknown"
        ? `status ${providerRecovery.betterstack.alert_status}`
        : null,
      providerRecovery.betterstack.priority
        ? `priority ${providerRecovery.betterstack.priority}`
        : null,
      providerRecovery.betterstack.escalation_policy
        ? `policy ${providerRecovery.betterstack.escalation_policy}`
        : null,
      providerRecovery.betterstack.assignee
        ? `assignee ${providerRecovery.betterstack.assignee}`
        : null,
      providerRecovery.betterstack.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.betterstack.phase_graph.alert_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.betterstack.phase_graph.workflow_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.betterstack.phase_graph.ownership_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.betterstack.phase_graph.escalation_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.betterstack.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Better Stack schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "onpage") {
    const details = [
      providerRecovery.onpage.alert_id ? `alert ${providerRecovery.onpage.alert_id}` : null,
      providerRecovery.onpage.alert_status !== "unknown"
        ? `status ${providerRecovery.onpage.alert_status}`
        : null,
      providerRecovery.onpage.priority ? `priority ${providerRecovery.onpage.priority}` : null,
      providerRecovery.onpage.escalation_policy
        ? `policy ${providerRecovery.onpage.escalation_policy}`
        : null,
      providerRecovery.onpage.assignee ? `assignee ${providerRecovery.onpage.assignee}` : null,
      providerRecovery.onpage.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.onpage.phase_graph.alert_phase}`
        : null,
      providerRecovery.onpage.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.onpage.phase_graph.workflow_phase}`
        : null,
      providerRecovery.onpage.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.onpage.phase_graph.ownership_phase}`
        : null,
      providerRecovery.onpage.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.onpage.phase_graph.escalation_phase}`
        : null,
      providerRecovery.onpage.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.onpage.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OnPage schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "allquiet") {
    const details = [
      providerRecovery.allquiet.alert_id ? `alert ${providerRecovery.allquiet.alert_id}` : null,
      providerRecovery.allquiet.alert_status !== "unknown"
        ? `status ${providerRecovery.allquiet.alert_status}`
        : null,
      providerRecovery.allquiet.priority ? `priority ${providerRecovery.allquiet.priority}` : null,
      providerRecovery.allquiet.escalation_policy
        ? `policy ${providerRecovery.allquiet.escalation_policy}`
        : null,
      providerRecovery.allquiet.assignee ? `assignee ${providerRecovery.allquiet.assignee}` : null,
      providerRecovery.allquiet.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.allquiet.phase_graph.alert_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.allquiet.phase_graph.workflow_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.allquiet.phase_graph.ownership_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.allquiet.phase_graph.escalation_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.allquiet.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `All Quiet schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "moogsoft") {
    const details = [
      providerRecovery.moogsoft.alert_id ? `alert ${providerRecovery.moogsoft.alert_id}` : null,
      providerRecovery.moogsoft.alert_status !== "unknown"
        ? `status ${providerRecovery.moogsoft.alert_status}`
        : null,
      providerRecovery.moogsoft.priority ? `priority ${providerRecovery.moogsoft.priority}` : null,
      providerRecovery.moogsoft.escalation_policy
        ? `policy ${providerRecovery.moogsoft.escalation_policy}`
        : null,
      providerRecovery.moogsoft.assignee ? `assignee ${providerRecovery.moogsoft.assignee}` : null,
      providerRecovery.moogsoft.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.moogsoft.phase_graph.alert_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.moogsoft.phase_graph.workflow_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.moogsoft.phase_graph.ownership_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.moogsoft.phase_graph.escalation_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.moogsoft.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Moogsoft schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "spikesh") {
    const details = [
      providerRecovery.spikesh.alert_id ? `alert ${providerRecovery.spikesh.alert_id}` : null,
      providerRecovery.spikesh.alert_status !== "unknown"
        ? `status ${providerRecovery.spikesh.alert_status}`
        : null,
      providerRecovery.spikesh.priority ? `priority ${providerRecovery.spikesh.priority}` : null,
      providerRecovery.spikesh.escalation_policy
        ? `policy ${providerRecovery.spikesh.escalation_policy}`
        : null,
      providerRecovery.spikesh.assignee ? `assignee ${providerRecovery.spikesh.assignee}` : null,
      providerRecovery.spikesh.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.spikesh.phase_graph.alert_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.spikesh.phase_graph.workflow_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.spikesh.phase_graph.ownership_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.spikesh.phase_graph.escalation_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.spikesh.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Spike.sh schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "dutycalls") {
    const details = [
      providerRecovery.dutycalls.alert_id ? `alert ${providerRecovery.dutycalls.alert_id}` : null,
      providerRecovery.dutycalls.alert_status !== "unknown"
        ? `status ${providerRecovery.dutycalls.alert_status}`
        : null,
      providerRecovery.dutycalls.priority ? `priority ${providerRecovery.dutycalls.priority}` : null,
      providerRecovery.dutycalls.escalation_policy
        ? `policy ${providerRecovery.dutycalls.escalation_policy}`
        : null,
      providerRecovery.dutycalls.assignee ? `assignee ${providerRecovery.dutycalls.assignee}` : null,
      providerRecovery.dutycalls.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.dutycalls.phase_graph.alert_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.dutycalls.phase_graph.workflow_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.dutycalls.phase_graph.ownership_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.dutycalls.phase_graph.escalation_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.dutycalls.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `DutyCalls schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidenthub") {
    const details = [
      providerRecovery.incidenthub.alert_id ? `alert ${providerRecovery.incidenthub.alert_id}` : null,
      providerRecovery.incidenthub.alert_status !== "unknown"
        ? `status ${providerRecovery.incidenthub.alert_status}`
        : null,
      providerRecovery.incidenthub.priority ? `priority ${providerRecovery.incidenthub.priority}` : null,
      providerRecovery.incidenthub.escalation_policy
        ? `policy ${providerRecovery.incidenthub.escalation_policy}`
        : null,
      providerRecovery.incidenthub.assignee ? `assignee ${providerRecovery.incidenthub.assignee}` : null,
      providerRecovery.incidenthub.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.incidenthub.phase_graph.alert_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidenthub.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.incidenthub.phase_graph.ownership_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.incidenthub.phase_graph.escalation_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidenthub.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `IncidentHub schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "resolver") {
    const details = [
      providerRecovery.resolver.alert_id ? `alert ${providerRecovery.resolver.alert_id}` : null,
      providerRecovery.resolver.alert_status !== "unknown"
        ? `status ${providerRecovery.resolver.alert_status}`
        : null,
      providerRecovery.resolver.priority ? `priority ${providerRecovery.resolver.priority}` : null,
      providerRecovery.resolver.escalation_policy
        ? `policy ${providerRecovery.resolver.escalation_policy}`
        : null,
      providerRecovery.resolver.assignee ? `assignee ${providerRecovery.resolver.assignee}` : null,
      providerRecovery.resolver.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.resolver.phase_graph.alert_phase}`
        : null,
      providerRecovery.resolver.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.resolver.phase_graph.workflow_phase}`
        : null,
      providerRecovery.resolver.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.resolver.phase_graph.ownership_phase}`
        : null,
      providerRecovery.resolver.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.resolver.phase_graph.escalation_phase}`
        : null,
      providerRecovery.resolver.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.resolver.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Resolver schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "openduty") {
    const details = [
      providerRecovery.openduty.alert_id ? `alert ${providerRecovery.openduty.alert_id}` : null,
      providerRecovery.openduty.alert_status !== "unknown"
        ? `status ${providerRecovery.openduty.alert_status}`
        : null,
      providerRecovery.openduty.priority ? `priority ${providerRecovery.openduty.priority}` : null,
      providerRecovery.openduty.escalation_policy
        ? `policy ${providerRecovery.openduty.escalation_policy}`
        : null,
      providerRecovery.openduty.assignee ? `assignee ${providerRecovery.openduty.assignee}` : null,
      providerRecovery.openduty.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.openduty.phase_graph.alert_phase}`
        : null,
      providerRecovery.openduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.openduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.openduty.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.openduty.phase_graph.ownership_phase}`
        : null,
      providerRecovery.openduty.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.openduty.phase_graph.escalation_phase}`
        : null,
      providerRecovery.openduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.openduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OpenDuty schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "cabot") {
    const details = [
      providerRecovery.cabot.alert_id ? `alert ${providerRecovery.cabot.alert_id}` : null,
      providerRecovery.cabot.alert_status !== "unknown"
        ? `status ${providerRecovery.cabot.alert_status}`
        : null,
      providerRecovery.cabot.priority ? `priority ${providerRecovery.cabot.priority}` : null,
      providerRecovery.cabot.escalation_policy
        ? `policy ${providerRecovery.cabot.escalation_policy}`
        : null,
      providerRecovery.cabot.assignee ? `assignee ${providerRecovery.cabot.assignee}` : null,
      providerRecovery.cabot.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.cabot.phase_graph.alert_phase}`
        : null,
      providerRecovery.cabot.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.cabot.phase_graph.workflow_phase}`
        : null,
      providerRecovery.cabot.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.cabot.phase_graph.ownership_phase}`
        : null,
      providerRecovery.cabot.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.cabot.phase_graph.escalation_phase}`
        : null,
      providerRecovery.cabot.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.cabot.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Cabot schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "haloitsm") {
    const details = [
      providerRecovery.haloitsm.alert_id ? `alert ${providerRecovery.haloitsm.alert_id}` : null,
      providerRecovery.haloitsm.alert_status !== "unknown"
        ? `status ${providerRecovery.haloitsm.alert_status}`
        : null,
      providerRecovery.haloitsm.priority ? `priority ${providerRecovery.haloitsm.priority}` : null,
      providerRecovery.haloitsm.escalation_policy
        ? `policy ${providerRecovery.haloitsm.escalation_policy}`
        : null,
      providerRecovery.haloitsm.assignee ? `assignee ${providerRecovery.haloitsm.assignee}` : null,
      providerRecovery.haloitsm.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.haloitsm.phase_graph.alert_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.haloitsm.phase_graph.workflow_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.haloitsm.phase_graph.ownership_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.haloitsm.phase_graph.escalation_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.haloitsm.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `HaloITSM schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidentmanagerio") {
    const details = [
      providerRecovery.incidentmanagerio.alert_id
        ? `alert ${providerRecovery.incidentmanagerio.alert_id}`
        : null,
      providerRecovery.incidentmanagerio.alert_status !== "unknown"
        ? `status ${providerRecovery.incidentmanagerio.alert_status}`
        : null,
      providerRecovery.incidentmanagerio.priority
        ? `priority ${providerRecovery.incidentmanagerio.priority}`
        : null,
      providerRecovery.incidentmanagerio.escalation_policy
        ? `policy ${providerRecovery.incidentmanagerio.escalation_policy}`
        : null,
      providerRecovery.incidentmanagerio.assignee
        ? `assignee ${providerRecovery.incidentmanagerio.assignee}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.incidentmanagerio.phase_graph.alert_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidentmanagerio.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.incidentmanagerio.phase_graph.ownership_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.incidentmanagerio.phase_graph.escalation_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidentmanagerio.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `incidentmanager.io schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "oneuptime") {
    const details = [
      providerRecovery.oneuptime.alert_id ? `alert ${providerRecovery.oneuptime.alert_id}` : null,
      providerRecovery.oneuptime.alert_status !== "unknown"
        ? `status ${providerRecovery.oneuptime.alert_status}`
        : null,
      providerRecovery.oneuptime.priority ? `priority ${providerRecovery.oneuptime.priority}` : null,
      providerRecovery.oneuptime.escalation_policy
        ? `policy ${providerRecovery.oneuptime.escalation_policy}`
        : null,
      providerRecovery.oneuptime.assignee ? `assignee ${providerRecovery.oneuptime.assignee}` : null,
      providerRecovery.oneuptime.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.oneuptime.phase_graph.alert_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.oneuptime.phase_graph.workflow_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.oneuptime.phase_graph.ownership_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.oneuptime.phase_graph.escalation_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.oneuptime.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OneUptime schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "squzy") {
    const details = [
      providerRecovery.squzy.alert_id ? `alert ${providerRecovery.squzy.alert_id}` : null,
      providerRecovery.squzy.alert_status !== "unknown"
        ? `status ${providerRecovery.squzy.alert_status}`
        : null,
      providerRecovery.squzy.priority ? `priority ${providerRecovery.squzy.priority}` : null,
      providerRecovery.squzy.escalation_policy
        ? `policy ${providerRecovery.squzy.escalation_policy}`
        : null,
      providerRecovery.squzy.assignee ? `assignee ${providerRecovery.squzy.assignee}` : null,
      providerRecovery.squzy.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.squzy.phase_graph.alert_phase}`
        : null,
      providerRecovery.squzy.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.squzy.phase_graph.workflow_phase}`
        : null,
      providerRecovery.squzy.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.squzy.phase_graph.ownership_phase}`
        : null,
      providerRecovery.squzy.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.squzy.phase_graph.escalation_phase}`
        : null,
      providerRecovery.squzy.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.squzy.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Squzy schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "crisescontrol") {
    const details = [
      providerRecovery.crisescontrol.alert_id
        ? `alert ${providerRecovery.crisescontrol.alert_id}`
        : null,
      providerRecovery.crisescontrol.alert_status !== "unknown"
        ? `status ${providerRecovery.crisescontrol.alert_status}`
        : null,
      providerRecovery.crisescontrol.priority
        ? `priority ${providerRecovery.crisescontrol.priority}`
        : null,
      providerRecovery.crisescontrol.escalation_policy
        ? `policy ${providerRecovery.crisescontrol.escalation_policy}`
        : null,
      providerRecovery.crisescontrol.assignee
        ? `assignee ${providerRecovery.crisescontrol.assignee}`
        : null,
      providerRecovery.crisescontrol.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.crisescontrol.phase_graph.alert_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.crisescontrol.phase_graph.workflow_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.crisescontrol.phase_graph.ownership_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.crisescontrol.phase_graph.escalation_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.crisescontrol.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Crises Control schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "freshservice") {
    const details = [
      providerRecovery.freshservice.alert_id
        ? `alert ${providerRecovery.freshservice.alert_id}`
        : null,
      providerRecovery.freshservice.alert_status !== "unknown"
        ? `status ${providerRecovery.freshservice.alert_status}`
        : null,
      providerRecovery.freshservice.priority
        ? `priority ${providerRecovery.freshservice.priority}`
        : null,
      providerRecovery.freshservice.escalation_policy
        ? `policy ${providerRecovery.freshservice.escalation_policy}`
        : null,
      providerRecovery.freshservice.assignee
        ? `assignee ${providerRecovery.freshservice.assignee}`
        : null,
      providerRecovery.freshservice.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.freshservice.phase_graph.alert_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.freshservice.phase_graph.workflow_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.freshservice.phase_graph.ownership_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.freshservice.phase_graph.escalation_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.freshservice.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Freshservice schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "freshdesk") {
    const details = [
      providerRecovery.freshdesk.alert_id
        ? `alert ${providerRecovery.freshdesk.alert_id}`
        : null,
      providerRecovery.freshdesk.alert_status !== "unknown"
        ? `status ${providerRecovery.freshdesk.alert_status}`
        : null,
      providerRecovery.freshdesk.priority
        ? `priority ${providerRecovery.freshdesk.priority}`
        : null,
      providerRecovery.freshdesk.escalation_policy
        ? `policy ${providerRecovery.freshdesk.escalation_policy}`
        : null,
      providerRecovery.freshdesk.assignee
        ? `assignee ${providerRecovery.freshdesk.assignee}`
        : null,
      providerRecovery.freshdesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.freshdesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.freshdesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.freshdesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.freshdesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.freshdesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Freshdesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "happyfox") {
    const details = [
      providerRecovery.happyfox.alert_id
        ? `alert ${providerRecovery.happyfox.alert_id}`
        : null,
      providerRecovery.happyfox.alert_status !== "unknown"
        ? `status ${providerRecovery.happyfox.alert_status}`
        : null,
      providerRecovery.happyfox.priority
        ? `priority ${providerRecovery.happyfox.priority}`
        : null,
      providerRecovery.happyfox.escalation_policy
        ? `policy ${providerRecovery.happyfox.escalation_policy}`
        : null,
      providerRecovery.happyfox.assignee
        ? `assignee ${providerRecovery.happyfox.assignee}`
        : null,
      providerRecovery.happyfox.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.happyfox.phase_graph.alert_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.happyfox.phase_graph.workflow_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.happyfox.phase_graph.ownership_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.happyfox.phase_graph.escalation_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.happyfox.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `HappyFox schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zendesk") {
    const details = [
      providerRecovery.zendesk.alert_id
        ? `alert ${providerRecovery.zendesk.alert_id}`
        : null,
      providerRecovery.zendesk.alert_status !== "unknown"
        ? `status ${providerRecovery.zendesk.alert_status}`
        : null,
      providerRecovery.zendesk.priority
        ? `priority ${providerRecovery.zendesk.priority}`
        : null,
      providerRecovery.zendesk.escalation_policy
        ? `policy ${providerRecovery.zendesk.escalation_policy}`
        : null,
      providerRecovery.zendesk.assignee
        ? `assignee ${providerRecovery.zendesk.assignee}`
        : null,
      providerRecovery.zendesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.zendesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zendesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zendesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.zendesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zendesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zendesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zohodesk") {
    const details = [
      providerRecovery.zohodesk.alert_id
        ? `alert ${providerRecovery.zohodesk.alert_id}`
        : null,
      providerRecovery.zohodesk.alert_status !== "unknown"
        ? `status ${providerRecovery.zohodesk.alert_status}`
        : null,
      providerRecovery.zohodesk.priority
        ? `priority ${providerRecovery.zohodesk.priority}`
        : null,
      providerRecovery.zohodesk.escalation_policy
        ? `policy ${providerRecovery.zohodesk.escalation_policy}`
        : null,
      providerRecovery.zohodesk.assignee
        ? `assignee ${providerRecovery.zohodesk.assignee}`
        : null,
      providerRecovery.zohodesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.zohodesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zohodesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zohodesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.zohodesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zohodesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zoho Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "helpscout") {
    const details = [
      providerRecovery.helpscout.alert_id
        ? `alert ${providerRecovery.helpscout.alert_id}`
        : null,
      providerRecovery.helpscout.alert_status !== "unknown"
        ? `status ${providerRecovery.helpscout.alert_status}`
        : null,
      providerRecovery.helpscout.priority
        ? `priority ${providerRecovery.helpscout.priority}`
        : null,
      providerRecovery.helpscout.escalation_policy
        ? `policy ${providerRecovery.helpscout.escalation_policy}`
        : null,
      providerRecovery.helpscout.assignee
        ? `assignee ${providerRecovery.helpscout.assignee}`
        : null,
      providerRecovery.helpscout.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.helpscout.phase_graph.alert_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.helpscout.phase_graph.workflow_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.helpscout.phase_graph.ownership_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.helpscout.phase_graph.escalation_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.helpscout.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Help Scout schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "kayako") {
    const details = [
      providerRecovery.kayako.alert_id
        ? `case ${providerRecovery.kayako.alert_id}`
        : null,
      providerRecovery.kayako.alert_status !== "unknown"
        ? `status ${providerRecovery.kayako.alert_status}`
        : null,
      providerRecovery.kayako.priority
        ? `priority ${providerRecovery.kayako.priority}`
        : null,
      providerRecovery.kayako.escalation_policy
        ? `policy ${providerRecovery.kayako.escalation_policy}`
        : null,
      providerRecovery.kayako.assignee
        ? `assignee ${providerRecovery.kayako.assignee}`
        : null,
      providerRecovery.kayako.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.kayako.phase_graph.alert_phase}`
        : null,
      providerRecovery.kayako.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.kayako.phase_graph.workflow_phase}`
        : null,
      providerRecovery.kayako.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.kayako.phase_graph.ownership_phase}`
        : null,
      providerRecovery.kayako.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.kayako.phase_graph.escalation_phase}`
        : null,
      providerRecovery.kayako.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.kayako.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Kayako schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "intercom") {
    const details = [
      providerRecovery.intercom.alert_id
        ? `conversation ${providerRecovery.intercom.alert_id}`
        : null,
      providerRecovery.intercom.alert_status !== "unknown"
        ? `status ${providerRecovery.intercom.alert_status}`
        : null,
      providerRecovery.intercom.priority
        ? `priority ${providerRecovery.intercom.priority}`
        : null,
      providerRecovery.intercom.escalation_policy
        ? `policy ${providerRecovery.intercom.escalation_policy}`
        : null,
      providerRecovery.intercom.assignee
        ? `assignee ${providerRecovery.intercom.assignee}`
        : null,
      providerRecovery.intercom.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.intercom.phase_graph.alert_phase}`
        : null,
      providerRecovery.intercom.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.intercom.phase_graph.workflow_phase}`
        : null,
      providerRecovery.intercom.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.intercom.phase_graph.ownership_phase}`
        : null,
      providerRecovery.intercom.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.intercom.phase_graph.escalation_phase}`
        : null,
      providerRecovery.intercom.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.intercom.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Intercom schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "front") {
    const details = [
      providerRecovery.front.alert_id
        ? `conversation ${providerRecovery.front.alert_id}`
        : null,
      providerRecovery.front.alert_status !== "unknown"
        ? `status ${providerRecovery.front.alert_status}`
        : null,
      providerRecovery.front.priority
        ? `priority ${providerRecovery.front.priority}`
        : null,
      providerRecovery.front.escalation_policy
        ? `policy ${providerRecovery.front.escalation_policy}`
        : null,
      providerRecovery.front.assignee
        ? `assignee ${providerRecovery.front.assignee}`
        : null,
      providerRecovery.front.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.front.phase_graph.alert_phase}`
        : null,
      providerRecovery.front.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.front.phase_graph.workflow_phase}`
        : null,
      providerRecovery.front.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.front.phase_graph.ownership_phase}`
        : null,
      providerRecovery.front.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.front.phase_graph.escalation_phase}`
        : null,
      providerRecovery.front.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.front.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Front schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "servicedeskplus") {
    const details = [
      providerRecovery.servicedeskplus.alert_id
        ? `alert ${providerRecovery.servicedeskplus.alert_id}`
        : null,
      providerRecovery.servicedeskplus.alert_status !== "unknown"
        ? `status ${providerRecovery.servicedeskplus.alert_status}`
        : null,
      providerRecovery.servicedeskplus.priority
        ? `priority ${providerRecovery.servicedeskplus.priority}`
        : null,
      providerRecovery.servicedeskplus.escalation_policy
        ? `policy ${providerRecovery.servicedeskplus.escalation_policy}`
        : null,
      providerRecovery.servicedeskplus.assignee
        ? `assignee ${providerRecovery.servicedeskplus.assignee}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.servicedeskplus.phase_graph.alert_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.servicedeskplus.phase_graph.workflow_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.servicedeskplus.phase_graph.ownership_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.servicedeskplus.phase_graph.escalation_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.servicedeskplus.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `ManageEngine ServiceDesk Plus schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "sysaid") {
    const details = [
      providerRecovery.sysaid.alert_id ? `alert ${providerRecovery.sysaid.alert_id}` : null,
      providerRecovery.sysaid.alert_status !== "unknown"
        ? `status ${providerRecovery.sysaid.alert_status}`
        : null,
      providerRecovery.sysaid.priority ? `priority ${providerRecovery.sysaid.priority}` : null,
      providerRecovery.sysaid.escalation_policy
        ? `policy ${providerRecovery.sysaid.escalation_policy}`
        : null,
      providerRecovery.sysaid.assignee ? `assignee ${providerRecovery.sysaid.assignee}` : null,
      providerRecovery.sysaid.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.sysaid.phase_graph.alert_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.sysaid.phase_graph.workflow_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.sysaid.phase_graph.ownership_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.sysaid.phase_graph.escalation_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.sysaid.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `SysAid schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "bmchelix") {
    const details = [
      providerRecovery.bmchelix.alert_id ? `alert ${providerRecovery.bmchelix.alert_id}` : null,
      providerRecovery.bmchelix.alert_status !== "unknown"
        ? `status ${providerRecovery.bmchelix.alert_status}`
        : null,
      providerRecovery.bmchelix.priority ? `priority ${providerRecovery.bmchelix.priority}` : null,
      providerRecovery.bmchelix.escalation_policy
        ? `policy ${providerRecovery.bmchelix.escalation_policy}`
        : null,
      providerRecovery.bmchelix.assignee ? `assignee ${providerRecovery.bmchelix.assignee}` : null,
      providerRecovery.bmchelix.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.bmchelix.phase_graph.alert_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.bmchelix.phase_graph.workflow_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.bmchelix.phase_graph.ownership_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.bmchelix.phase_graph.escalation_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.bmchelix.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `BMC Helix schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "solarwindsservicedesk") {
    const details = [
      providerRecovery.solarwindsservicedesk.alert_id
        ? `alert ${providerRecovery.solarwindsservicedesk.alert_id}`
        : null,
      providerRecovery.solarwindsservicedesk.alert_status !== "unknown"
        ? `status ${providerRecovery.solarwindsservicedesk.alert_status}`
        : null,
      providerRecovery.solarwindsservicedesk.priority
        ? `priority ${providerRecovery.solarwindsservicedesk.priority}`
        : null,
      providerRecovery.solarwindsservicedesk.escalation_policy
        ? `policy ${providerRecovery.solarwindsservicedesk.escalation_policy}`
        : null,
      providerRecovery.solarwindsservicedesk.assignee
        ? `assignee ${providerRecovery.solarwindsservicedesk.assignee}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.solarwindsservicedesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.solarwindsservicedesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.solarwindsservicedesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.solarwindsservicedesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.solarwindsservicedesk.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `SolarWinds Service Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "topdesk") {
    const details = [
      providerRecovery.topdesk.alert_id ? `alert ${providerRecovery.topdesk.alert_id}` : null,
      providerRecovery.topdesk.alert_status !== "unknown"
        ? `status ${providerRecovery.topdesk.alert_status}`
        : null,
      providerRecovery.topdesk.priority ? `priority ${providerRecovery.topdesk.priority}` : null,
      providerRecovery.topdesk.escalation_policy
        ? `policy ${providerRecovery.topdesk.escalation_policy}`
        : null,
      providerRecovery.topdesk.assignee ? `assignee ${providerRecovery.topdesk.assignee}` : null,
      providerRecovery.topdesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.topdesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.topdesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.topdesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.topdesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.topdesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `TOPdesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "invgateservicedesk") {
    const details = [
      providerRecovery.invgateservicedesk.alert_id
        ? `alert ${providerRecovery.invgateservicedesk.alert_id}`
        : null,
      providerRecovery.invgateservicedesk.alert_status !== "unknown"
        ? `status ${providerRecovery.invgateservicedesk.alert_status}`
        : null,
      providerRecovery.invgateservicedesk.priority
        ? `priority ${providerRecovery.invgateservicedesk.priority}`
        : null,
      providerRecovery.invgateservicedesk.escalation_policy
        ? `policy ${providerRecovery.invgateservicedesk.escalation_policy}`
        : null,
      providerRecovery.invgateservicedesk.assignee
        ? `assignee ${providerRecovery.invgateservicedesk.assignee}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.invgateservicedesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.invgateservicedesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.invgateservicedesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.invgateservicedesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.invgateservicedesk.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `InvGate Service Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "opsramp") {
    const details = [
      providerRecovery.opsramp.alert_id ? `alert ${providerRecovery.opsramp.alert_id}` : null,
      providerRecovery.opsramp.alert_status !== "unknown"
        ? `status ${providerRecovery.opsramp.alert_status}`
        : null,
      providerRecovery.opsramp.priority ? `priority ${providerRecovery.opsramp.priority}` : null,
      providerRecovery.opsramp.escalation_policy
        ? `policy ${providerRecovery.opsramp.escalation_policy}`
        : null,
      providerRecovery.opsramp.assignee ? `assignee ${providerRecovery.opsramp.assignee}` : null,
      providerRecovery.opsramp.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.opsramp.phase_graph.alert_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.opsramp.phase_graph.workflow_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.opsramp.phase_graph.ownership_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.opsramp.phase_graph.escalation_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.opsramp.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OpsRamp schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zenduty") {
    const details = [
      providerRecovery.zenduty.incident_id ? `incident ${providerRecovery.zenduty.incident_id}` : null,
      providerRecovery.zenduty.incident_status !== "unknown"
        ? `status ${providerRecovery.zenduty.incident_status}`
        : null,
      providerRecovery.zenduty.severity ? `severity ${providerRecovery.zenduty.severity}` : null,
      providerRecovery.zenduty.assignee ? `assignee ${providerRecovery.zenduty.assignee}` : null,
      providerRecovery.zenduty.service ? `service ${providerRecovery.zenduty.service}` : null,
      providerRecovery.zenduty.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.zenduty.phase_graph.incident_phase}`
        : null,
      providerRecovery.zenduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zenduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zenduty.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zenduty.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zenduty.updated_at
        ? `updated ${formatTimestamp(providerRecovery.zenduty.updated_at)}`
        : null,
      providerRecovery.zenduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zenduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zenduty schema: ${details.join(" / ")}` : null;
  }
  return null;
}

function formatProviderRecoveryTelemetry(providerRecovery: {
  telemetry: {
    source: string;
    state: string;
    progress_percent?: number | null;
    attempt_count: number;
    current_step?: string | null;
    last_message?: string | null;
    last_error?: string | null;
    external_run_id?: string | null;
    updated_at?: string | null;
  };
}) {
  const details = [
    providerRecovery.telemetry.source !== "unknown"
      ? `source ${providerRecovery.telemetry.source}`
      : null,
    providerRecovery.telemetry.state !== "unknown"
      ? `state ${providerRecovery.telemetry.state}`
      : null,
    providerRecovery.telemetry.progress_percent != null
      ? `progress ${providerRecovery.telemetry.progress_percent}%`
      : null,
    providerRecovery.telemetry.attempt_count
      ? `attempts ${providerRecovery.telemetry.attempt_count}`
      : null,
    providerRecovery.telemetry.current_step
      ? `step ${providerRecovery.telemetry.current_step}`
      : null,
    providerRecovery.telemetry.external_run_id
      ? `run ${providerRecovery.telemetry.external_run_id}`
      : null,
    providerRecovery.telemetry.updated_at
      ? `updated ${formatTimestamp(providerRecovery.telemetry.updated_at)}`
      : null,
    providerRecovery.telemetry.last_error
      ? `error ${providerRecovery.telemetry.last_error}`
      : providerRecovery.telemetry.last_message
        ? `message ${providerRecovery.telemetry.last_message}`
        : null,
  ].filter(Boolean);
  return details.length ? `Recovery telemetry: ${details.join(" / ")}` : null;
}

function shortenIdentifier(value: string, maxLength = 18) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3)}...`;
}

function truncateLabel(value: string, maxLength = 56) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3)}...`;
}

function formatRange(start?: string | null, end?: string | null) {
  if (!start && !end) {
    return "open-ended";
  }
  return `${formatTimestamp(start)} -> ${formatTimestamp(end)}`;
}

const benchmarkArtifactSummaryOrder = [
  "strategy_name",
  "run_id",
  "exchange",
  "stake_currency",
  "timeframe",
  "timerange",
  "generated_at",
  "backtest_start_at",
  "backtest_end_at",
  "pair_count",
  "trade_count",
  "profit_total_pct",
  "profit_total_abs",
  "max_drawdown_pct",
  "market_change_pct",
  "manifest_count",
  "snapshot_count",
] as const;

const benchmarkArtifactSummaryLabels: Record<string, string> = {
  headline: "Headline",
  market_context: "Market read",
  portfolio_context: "Portfolio read",
  signal_context: "Signal read",
  rejection_context: "Rejections",
  exit_context: "Exit read",
  pair_context: "Pair read",
  strategy_name: "Strategy",
  run_id: "Run ID",
  exchange: "Exchange",
  stake_currency: "Stake",
  timeframe: "TF",
  timerange: "Timerange",
  generated_at: "Generated",
  backtest_start_at: "Backtest start",
  backtest_end_at: "Backtest end",
  pair_count: "Pairs",
  trade_count: "Trades",
  profit_total_pct: "Total return",
  profit_total_abs: "Total PnL",
  max_drawdown_pct: "Max DD",
  market_change_pct: "Market move",
  manifest_count: "Manifests",
  snapshot_count: "Snapshots",
  timeframe_detail: "TF detail",
  notes: "Notes",
  win_rate_pct: "Win rate",
  date: "Date",
  duration: "Duration",
  drawdown_start: "DD start",
  drawdown_end: "DD end",
  start_balance: "Start balance",
  end_balance: "End balance",
  high_balance: "High balance",
  low_balance: "Low balance",
  sharpe: "Sharpe",
  sortino: "Sortino",
  calmar: "Calmar",
  member_count: "Members",
  entry_preview: "Entries",
  market_change_export_count: "Market exports",
  wallet_export_count: "Wallet exports",
  signal_export_count: "Signal exports",
  rejected_export_count: "Rejected exports",
  exited_export_count: "Exited exports",
  strategy_source_count: "Strategy sources",
  strategy_param_count: "Strategy params",
  result_json_entry: "Result JSON",
  config_json_entry: "Config JSON",
  strategy: "Strategy",
  trading_mode: "Trading mode",
  margin_mode: "Margin mode",
  max_open_trades: "Max open trades",
  export: "Export",
  source_files: "Source files",
  parameter_files: "Parameter files",
  strategy_names: "Strategy names",
  parameter_keys: "Parameter keys",
  entry: "Entry",
  row_count: "Rows",
  total_row_count: "Total rows",
  frame_count: "Frames",
  column_count: "Columns",
  columns: "Column list",
  date_start: "Start",
  date_end: "End",
  export_count: "Exports",
  strategies: "Strategies",
  currencies: "Currencies",
  currency_count: "Currency count",
  entries: "Entries",
  unreadable_entries: "Unreadable",
  inspection_status: "Inspection",
  pair_change_preview: "Pair moves",
  best_pair: "Best pair",
  best_pair_change_pct: "Best pair move",
  worst_pair: "Worst pair",
  worst_pair_change_pct: "Worst pair move",
  positive_pair_count: "Positive pairs",
  negative_pair_count: "Negative pairs",
  start_value: "Start value",
  end_value: "End value",
  change_pct: "Change",
  total_quote_start: "Quote start",
  total_quote_end: "Quote end",
  total_quote_high: "Quote high",
  total_quote_low: "Quote low",
  currency_quote_preview: "Currency quote preview",
  latest_balance: "Latest balance",
  latest_quote_value: "Latest quote value",
  strategy_row_preview: "Strategy rows",
  pair_row_preview: "Pair rows",
  semantic_columns: "Semantic columns",
  enter_tag_counts: "Entry tag counts",
  reason_counts: "Reason counts",
  exit_reason_counts: "Exit reason counts",
};

const benchmarkArtifactSectionOrder = [
  "benchmark_story",
  "zip_contents",
  "zip_config",
  "zip_strategy_bundle",
  "zip_market_change",
  "zip_wallet_exports",
  "zip_signal_exports",
  "zip_rejected_exports",
  "zip_exited_exports",
  "metadata",
  "strategy_comparison",
  "pair_metrics",
  "pair_extremes",
  "enter_tag_metrics",
  "exit_reason_metrics",
  "mixed_tag_metrics",
  "left_open_metrics",
  "periodic_breakdown",
  "daily_profit",
  "wallet_stats",
] as const;

const benchmarkArtifactSectionLabels: Record<string, string> = {
  benchmark_story: "Benchmark narrative",
  zip_contents: "Zip contents",
  zip_config: "Embedded config",
  zip_strategy_bundle: "Strategy bundle",
  zip_market_change: "Market change export",
  zip_wallet_exports: "Wallet exports",
  zip_signal_exports: "Signal exports",
  zip_rejected_exports: "Rejected exports",
  zip_exited_exports: "Exited exports",
  metadata: "Metadata",
  strategy_comparison: "Strategy comparison",
  pair_metrics: "Pair metrics",
  pair_extremes: "Pair extremes",
  enter_tag_metrics: "Entry tags",
  exit_reason_metrics: "Exit reasons",
  mixed_tag_metrics: "Mixed tags",
  left_open_metrics: "Left open",
  periodic_breakdown: "Periodic breakdown",
  daily_profit: "Daily profit",
  wallet_stats: "Wallet stats",
};

function formatBenchmarkArtifactSummaryEntries(summary: Record<string, unknown>) {
  return Object.entries(summary)
    .map(([key, value]) => [key, formatBenchmarkArtifactSummaryValue(key, value)] as const)
    .filter(([, value]) => value !== null)
    .sort(([leftKey], [rightKey]) => {
      const leftIndex = benchmarkArtifactSummarySortIndex(leftKey);
      const rightIndex = benchmarkArtifactSummarySortIndex(rightKey);
      if (leftIndex === rightIndex) {
        return leftKey.localeCompare(rightKey);
      }
      return leftIndex - rightIndex;
    });
}

function benchmarkArtifactSummarySortIndex(key: string) {
  const index = benchmarkArtifactSummaryOrder.indexOf(key as (typeof benchmarkArtifactSummaryOrder)[number]);
  if (index >= 0) {
    return index;
  }
  return benchmarkArtifactSummaryOrder.length + 100;
}

function formatBenchmarkArtifactSummaryLabel(key: string) {
  return benchmarkArtifactSummaryLabels[key] ?? key.replaceAll("_", " ");
}

function formatBenchmarkArtifactSummaryValue(key: string, value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (typeof value === "boolean") {
    return value ? "yes" : "no";
  }
  if (typeof value === "number") {
    if (key.endsWith("_pct")) {
      return `${value}%`;
    }
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function formatBenchmarkArtifactSectionEntries(sections: Record<string, Record<string, unknown>>) {
  return Object.entries(sections)
    .map(([key, section]) => [key, formatBenchmarkArtifactSectionLines(section)] as const)
    .filter(([, lines]) => lines.length > 0)
    .sort(([leftKey], [rightKey]) => {
      const leftIndex = benchmarkArtifactSectionSortIndex(leftKey);
      const rightIndex = benchmarkArtifactSectionSortIndex(rightKey);
      if (leftIndex === rightIndex) {
        return leftKey.localeCompare(rightKey);
      }
      return leftIndex - rightIndex;
    });
}

function benchmarkArtifactSectionSortIndex(key: string) {
  const index = benchmarkArtifactSectionOrder.indexOf(key as (typeof benchmarkArtifactSectionOrder)[number]);
  if (index >= 0) {
    return index;
  }
  return benchmarkArtifactSectionOrder.length + 100;
}

function formatBenchmarkArtifactSectionLabel(key: string) {
  return benchmarkArtifactSectionLabels[key] ?? key.replaceAll("_", " ");
}

function formatBenchmarkArtifactSectionLines(section: Record<string, unknown>) {
  return Object.entries(section)
    .map(([key, value]) => {
      const inlineValue = formatBenchmarkArtifactSectionValue(value);
      if (inlineValue === null) {
        return null;
      }
      return `${formatBenchmarkArtifactSummaryLabel(key)}: ${inlineValue}`;
    })
    .filter((line): line is string => line !== null);
}

function formatBenchmarkArtifactSectionValue(value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (Array.isArray(value)) {
    if (!value.length) {
      return null;
    }
    const preview = value.slice(0, 3).map((item) => formatBenchmarkArtifactInlineValue(item)).join(" | ");
    if (value.length > 3) {
      return `${preview} | +${value.length - 3} more`;
    }
    return preview;
  }
  if (typeof value === "object") {
    return formatBenchmarkArtifactInlineValue(value);
  }
  return String(value);
}

function formatBenchmarkArtifactInlineValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "n/a";
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatBenchmarkArtifactInlineValue(item)).join(", ");
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .filter(([key]) => !key.startsWith("__"))
      .map(([key, nestedValue]) => {
        const formattedValue = formatBenchmarkArtifactSummaryValue(key, nestedValue);
        if (formattedValue === null) {
          return null;
        }
        return `${formatBenchmarkArtifactSummaryLabel(key)}=${formattedValue}`;
      })
      .filter((entry): entry is string => entry !== null)
      .join(", ");
  }
  return String(value);
}
