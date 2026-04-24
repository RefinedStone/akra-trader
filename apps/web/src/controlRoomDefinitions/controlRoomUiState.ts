import type { ComparisonIntent, ComparisonScoreLinkTarget } from "./comparisonCore";

export const MAX_COMPARISON_HISTORY_PANEL_ENTRIES = 12;
export const MAX_COMPARISON_HISTORY_SYNC_AUDIT_ENTRIES = 8;
export const CONTROL_ROOM_UI_STATE_STORAGE_KEY = "akra-trader-control-room-ui-state";
export const CONTROL_ROOM_UI_STATE_VERSION = 4;
export const COMPARISON_HISTORY_BROWSER_STATE_KEY = "akraTraderComparisonHistory";
export const COMPARISON_HISTORY_BROWSER_STATE_VERSION = 1;
export const COMPARISON_HISTORY_TAB_ID_SESSION_KEY = "akra-trader-comparison-history-tab-id";
export const COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY = "akra-trader-comparison-history-sync-audit";
export const COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION = 1;
export const LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY = "akra-trader-gap-window-expansion";

export type ComparisonHistorySyncWorkspaceSemanticSignal = {
  label: string;
  weight: number;
};

export type ExpandedGapWindowSelections = Record<string, string[]>;
export type GapWindowDragSelectionState = {
  anchorGapWindowKey: string;
  baselineSelectedGapWindowKeys: string[];
  latestGapWindowKey: string;
  pointerId: number;
  targetSelected: boolean;
};
export type PendingTouchGapWindowSweepState = {
  anchorGapWindowKey: string;
  baselineSelectedGapWindowKeys: string[];
  latestGapWindowKey: string;
  pointerId: number;
  startClientX: number;
  startClientY: number;
  targetSelected: boolean;
};
export type TouchGapWindowHoldProgressState = {
  anchorGapWindowKey: string;
  targetSelected: boolean;
};
export type TouchGapWindowActivationFeedbackState = {
  activationId: number;
  anchorGapWindowKey: string;
};

export type ControlRoomUiStateV1 = {
  version: 1;
  expandedGapRows: Record<string, boolean>;
};

export type ControlRoomComparisonSelectionState = {
  selectedRunIds: string[];
  intent: ComparisonIntent;
  scoreLink: ComparisonScoreLinkTarget | null;
};

export type ComparisonHistoryStepDescriptor = {
  label: string;
  summary: string;
  title: string;
};

export type ComparisonHistoryBrowserState = {
  version: typeof COMPARISON_HISTORY_BROWSER_STATE_VERSION;
  entryId: string;
  stepIndex: number;
  label: string;
  summary: string;
  title: string;
  selection: ControlRoomComparisonSelectionState;
};

export type ComparisonHistoryPanelEntry = {
  entryId: string;
  stepIndex: number;
  label: string;
  summary: string;
  title: string;
  url: string;
  hidden: boolean;
  pinned: boolean;
  recordedAt: string;
  selection: ControlRoomComparisonSelectionState;
};

export type ComparisonHistoryTabIdentity = {
  tabId: string;
  label: string;
};

export type ComparisonHistoryPanelSyncState = {
  tabId: string;
  tabLabel: string;
  updatedAt: string;
};

export type ComparisonHistorySyncAuditKind = "merge" | "conflict" | "preferences" | "workspace";
export type ComparisonHistorySyncConflictFieldSource = "local" | "remote";
export type ComparisonHistorySyncConflictFieldKey =
  | "stepIndex"
  | "label"
  | "summary"
  | "title"
  | "url"
  | "hidden"
  | "pinned"
  | "selection.intent"
  | "selection.selectedRunIds"
  | "selection.scoreLink";
export type ComparisonHistorySyncWorkspaceFieldKey =
  | "comparisonSelection.intent"
  | "comparisonSelection.selectedRunIds"
  | "comparisonSelection.scoreLink"
  | "expandedGapRows";
export type ComparisonHistorySyncWorkspaceReviewSelectionKey =
  | ComparisonHistorySyncWorkspaceFieldKey
  | `expandedGapRows:${string}`
  | `expandedGapWindows|${string}|${string}`;
export type ComparisonHistorySyncWorkspaceSignalDetailSubviewKey =
  | "interpretation"
  | "lanePosition"
  | "recommendationContext";
export type ComparisonHistorySyncWorkspaceSignalDetailNestedKey =
  | "laneSemantics"
  | "recommendationEffect"
  | "rankContext"
  | "weightShare"
  | "selectionAlignment"
  | "resolutionBasis";
export type ComparisonHistorySyncWorkspaceSignalMicroViewKey =
  | "summary"
  | "trace"
  | "recommendation"
  | "alternative"
  | "position"
  | "score"
  | "share"
  | "impact"
  | "selection"
  | "lane"
  | "gap"
  | "reason";
export type ComparisonHistorySyncWorkspaceSignalMicroInteractionKey =
  | "lane"
  | "polarity"
  | "signal"
  | "source"
  | "support"
  | "tradeoff"
  | "rank"
  | "score"
  | "share"
  | "impact"
  | "selected"
  | "focusedLane"
  | "gap"
  | "reason";
export type ComparisonHistorySyncAuditFilter =
  | "all"
  | "conflicts"
  | "preferences"
  | "workspace"
  | "merges";
export type ComparisonHistorySyncPreferenceFieldKey =
  | "open"
  | "searchQuery"
  | "showPinnedOnly"
  | "auditFilter"
  | "showResolvedAuditEntries";

export type ComparisonHistorySyncConflictReview = {
  entryId: string;
  entryLabel: string;
  localEntry: ComparisonHistoryPanelEntry;
  remoteEntry: ComparisonHistoryPanelEntry;
  selectedSources: Partial<
    Record<ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource>
  >;
  resolvedAt?: string | null;
  resolutionSummary?: string | null;
};

export type ComparisonHistorySyncPreferenceState = {
  open: boolean;
  searchQuery: string;
  showPinnedOnly: boolean;
  auditFilter: ComparisonHistorySyncAuditFilter;
  showResolvedAuditEntries: boolean;
};

export type ComparisonHistorySyncPreferenceReview = {
  localState: ComparisonHistorySyncPreferenceState;
  remoteState: ComparisonHistorySyncPreferenceState;
  selectedSources: Partial<
    Record<ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncConflictFieldSource>
  >;
  resolvedAt?: string | null;
  resolutionSummary?: string | null;
};

export type ComparisonHistorySyncWorkspaceState = {
  comparisonSelection: ControlRoomComparisonSelectionState;
  expandedGapRows: Record<string, boolean>;
  expandedGapWindowSelections: ExpandedGapWindowSelections;
};

export type ComparisonHistorySyncWorkspaceReview = {
  localState: ComparisonHistorySyncWorkspaceState;
  remoteState: ComparisonHistorySyncWorkspaceState;
  selectedSources: Partial<
    Record<ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncConflictFieldSource>
  >;
  resolvedAt?: string | null;
  resolutionSummary?: string | null;
};

export type ComparisonHistorySyncAuditEntry = {
  auditId: string;
  kind: ComparisonHistorySyncAuditKind;
  summary: string;
  detail: string;
  recordedAt: string;
  sourceTabId: string;
  sourceTabLabel: string;
  conflictReview?: ComparisonHistorySyncConflictReview | null;
  preferenceReview?: ComparisonHistorySyncPreferenceReview | null;
  workspaceReview?: ComparisonHistorySyncWorkspaceReview | null;
};

export type ComparisonHistorySyncAuditTrailState = {
  version: typeof COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION;
  tabId: string;
  entries: ComparisonHistorySyncAuditEntry[];
};

export type ComparisonHistoryPanelState = {
  entries: ComparisonHistoryPanelEntry[];
  activeEntryId: string | null;
};

export type ControlRoomComparisonHistoryPanelUiState = {
  panel: ComparisonHistoryPanelState;
  open: boolean;
  searchQuery: string;
  showPinnedOnly: boolean;
  auditFilter: ComparisonHistorySyncAuditFilter;
  showResolvedAuditEntries: boolean;
  expandedConflictReviewIds: Record<string, boolean>;
  expandedWorkspaceScoreDetailIds: Record<string, boolean>;
  focusedWorkspaceScoreDetailSources: Record<string, ComparisonHistorySyncConflictFieldSource>;
  focusedWorkspaceScoreDetailSignalKeys: Record<string, string>;
  expandedWorkspaceScoreSignalDetailIds: Record<string, boolean>;
  collapsedWorkspaceScoreSignalSubviewIds: Record<string, boolean>;
  collapsedWorkspaceScoreSignalNestedSubviewIds: Record<string, boolean>;
  focusedWorkspaceScoreSignalMicroViews: Record<string, ComparisonHistorySyncWorkspaceSignalMicroViewKey>;
  focusedWorkspaceScoreSignalMicroInteractions: Record<string, ComparisonHistorySyncWorkspaceSignalMicroInteractionKey>;
  hoveredWorkspaceScoreSignalMicroTargets: Record<string, string>;
  scrubbedWorkspaceScoreSignalMicroSteps: Record<string, number>;
  selectedWorkspaceScoreSignalMicroNotePages: Record<string, number>;
  activeWorkspaceOverviewRowId: string | null;
  sync: ComparisonHistoryPanelSyncState | null;
};

export type ComparisonHistorySyncConflictReviewRow = {
  fieldKey: ComparisonHistorySyncConflictFieldKey;
  groupKey: string;
  groupLabel: string;
  label: string;
  localValue: string;
  remoteValue: string;
  selectedSource: ComparisonHistorySyncConflictFieldSource;
};

export type ComparisonHistorySyncConflictReviewGroup = {
  key: string;
  label: string;
  rows: ComparisonHistorySyncConflictReviewRow[];
  summaryLabel: string;
};

export type ComparisonHistorySyncPreferenceReviewRow = {
  fieldKey: ComparisonHistorySyncPreferenceFieldKey;
  label: string;
  localValue: string;
  remoteValue: string;
  selectedSource: ComparisonHistorySyncConflictFieldSource;
};

export type ComparisonHistorySyncWorkspaceReviewRow = {
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey;
  hasLatestLocalDrift: boolean;
  label: string;
  localHint?: string | null;
  localScore: number;
  localSignals: ComparisonHistorySyncWorkspaceSemanticSignal[];
  localValue: string;
  remoteScore: number;
  remoteSignals: ComparisonHistorySyncWorkspaceSemanticSignal[];
  remoteValue: string;
  recommendedSource: ComparisonHistorySyncConflictFieldSource;
  recommendationReason: string;
  recommendationStrength: number;
  semanticRank: number;
  selectedSource: ComparisonHistorySyncConflictFieldSource;
};

export type ComparisonHistorySyncWorkspaceRecommendationOverview = {
  totalFieldCount: number;
  localCount: number;
  remoteCount: number;
  latestLocalDriftCount: number;
  rankedDiffCount: number;
  strongest: ComparisonHistorySyncWorkspaceReviewRow | null;
  topLocal: ComparisonHistorySyncWorkspaceReviewRow[];
  topRemote: ComparisonHistorySyncWorkspaceReviewRow[];
};

export type ControlRoomUiStateV2 = {
  version: 2;
  expandedGapRows: Record<string, boolean>;
  comparisonSelection: ControlRoomComparisonSelectionState;
};

export type ControlRoomUiStateV3 = {
  version: 3;
  expandedGapRows: Record<string, boolean>;
  comparisonSelection: ControlRoomComparisonSelectionState;
  comparisonHistoryPanel: ControlRoomComparisonHistoryPanelUiState;
};

export type ControlRoomUiStateV4 = {
  version: typeof CONTROL_ROOM_UI_STATE_VERSION;
  expandedGapRows: Record<string, boolean>;
  expandedGapWindowSelections: ExpandedGapWindowSelections;
  comparisonSelection: ControlRoomComparisonSelectionState;
  comparisonHistoryPanel: ControlRoomComparisonHistoryPanelUiState;
};

export const COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS: Array<{
  fieldKey: ComparisonHistorySyncConflictFieldKey;
  groupKey: string;
  groupLabel: string;
  label: string;
}> = [
  { fieldKey: "stepIndex", groupKey: "timeline", groupLabel: "Timeline", label: "Step order" },
  { fieldKey: "url", groupKey: "timeline", groupLabel: "Timeline", label: "Deep link" },
  { fieldKey: "label", groupKey: "copy", groupLabel: "Copy", label: "Step label" },
  { fieldKey: "summary", groupKey: "copy", groupLabel: "Copy", label: "Step summary" },
  { fieldKey: "title", groupKey: "copy", groupLabel: "Copy", label: "Document title" },
  { fieldKey: "hidden", groupKey: "flags", groupLabel: "Flags", label: "Visibility" },
  { fieldKey: "pinned", groupKey: "flags", groupLabel: "Flags", label: "Pinned state" },
  { fieldKey: "selection.intent", groupKey: "selection", groupLabel: "Selection", label: "Intent" },
  {
    fieldKey: "selection.selectedRunIds",
    groupKey: "selection",
    groupLabel: "Selection",
    label: "Selected runs",
  },
  {
    fieldKey: "selection.scoreLink",
    groupKey: "selection",
    groupLabel: "Selection",
    label: "Focused score component",
  },
];

export const COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS: Array<{
  fieldKey: ComparisonHistorySyncPreferenceFieldKey;
  label: string;
}> = [
  { fieldKey: "open", label: "Browser visibility" },
  { fieldKey: "searchQuery", label: "Search filter" },
  { fieldKey: "showPinnedOnly", label: "Pinned-only mode" },
  { fieldKey: "auditFilter", label: "Audit list filter" },
  { fieldKey: "showResolvedAuditEntries", label: "Resolved audit visibility" },
];

export const COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS: Array<{
  fieldKey: ComparisonHistorySyncWorkspaceFieldKey;
  label: string;
}> = [
  { fieldKey: "comparisonSelection.intent", label: "Comparison intent" },
  { fieldKey: "comparisonSelection.selectedRunIds", label: "Selected runs" },
  { fieldKey: "comparisonSelection.scoreLink", label: "Focused score component" },
  { fieldKey: "expandedGapRows", label: "Expanded gap windows" },
];
