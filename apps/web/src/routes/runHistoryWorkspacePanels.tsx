import type { ReactNode } from "react";

import type {
  ComparisonHistoryPanelEntry,
  ComparisonHistoryPanelSyncState,
  ComparisonHistoryStepDescriptor,
  ComparisonHistorySyncAuditEntry,
  ComparisonHistorySyncAuditFilter,
  ComparisonHistorySyncConflictFieldKey,
  ComparisonHistorySyncConflictFieldSource,
  ComparisonHistorySyncPreferenceFieldKey,
  ComparisonHistorySyncWorkspaceReviewSelectionKey,
  ComparisonHistorySyncWorkspaceSignalMicroInteractionKey,
  ComparisonHistorySyncWorkspaceSignalMicroViewKey,
  ComparisonHistorySyncWorkspaceState,
  ComparisonHistoryTabIdentity,
  ComparisonHistoryWriteMode,
  ComparisonIntent,
  ComparisonScoreLinkTarget,
  ExperimentPreset,
  Run,
  RunComparison,
  RunHistoryFilter,
  RunHistorySurfaceKey,
  RunSurfaceCapabilities,
  Strategy,
} from "../controlRoomDefinitions";

export type RunSectionComparisonControls = {
  selectedRunIds: string[];
  comparisonIntent: ComparisonIntent;
  latestWorkspaceSyncState: ComparisonHistorySyncWorkspaceState;
  expandedHistoryConflictReviewIds: Record<string, boolean>;
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
  historyStep: ComparisonHistoryStepDescriptor;
  historyTabIdentity: ComparisonHistoryTabIdentity;
  historySharedSync: ComparisonHistoryPanelSyncState | null;
  historySyncAuditTrail: ComparisonHistorySyncAuditEntry[];
  historyEntries: ComparisonHistoryPanelEntry[];
  visibleHistoryEntries: ComparisonHistoryPanelEntry[];
  activeHistoryEntryId: string | null;
  historyBrowserOpen: boolean;
  historySearchQuery: string;
  showPinnedHistoryOnly: boolean;
  historyAuditFilter: ComparisonHistorySyncAuditFilter;
  showResolvedHistoryAudits: boolean;
  canNavigateHistoryBackward: boolean;
  canNavigateHistoryForward: boolean;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
  payload: RunComparison | null;
  loading: boolean;
  error: string | null;
  onChangeComparisonIntent: (intent: ComparisonIntent) => void;
  onChangeSelectedScoreLink: (
    value: ComparisonScoreLinkTarget | null,
    historyMode?: ComparisonHistoryWriteMode,
  ) => void;
  onToggleHistoryBrowser: () => void;
  onChangeHistorySearchQuery: (value: string) => void;
  onChangeShowPinnedHistoryOnly: (value: boolean) => void;
  onChangeHistoryAuditFilter: (value: ComparisonHistorySyncAuditFilter) => void;
  onChangeShowResolvedHistoryAudits: (value: boolean) => void;
  onToggleHistoryConflictReview: (auditId: string) => void;
  onToggleWorkspaceScoreDetail: (scoreDetailKey: string) => void;
  onChangeFocusedWorkspaceScoreDetailSource: (
    scoreDetailKey: string,
    source: ComparisonHistorySyncConflictFieldSource,
  ) => void;
  onChangeFocusedWorkspaceScoreDetailSignalKey: (
    scoreDetailKey: string,
    signalKey: string | null,
  ) => void;
  onToggleWorkspaceScoreSignalDetail: (scoreDetailKey: string) => void;
  onToggleWorkspaceScoreSignalSubview: (subviewId: string) => void;
  onToggleWorkspaceScoreSignalNestedSubview: (subviewId: string) => void;
  onChangeWorkspaceScoreSignalMicroView: (
    subviewId: string,
    value: ComparisonHistorySyncWorkspaceSignalMicroViewKey,
  ) => void;
  onChangeWorkspaceScoreSignalMicroInteraction: (
    interactionId: string,
    value: ComparisonHistorySyncWorkspaceSignalMicroInteractionKey,
  ) => void;
  onChangeWorkspaceScoreSignalMicroHoverTarget: (interactionId: string, value: string) => void;
  onChangeWorkspaceScoreSignalMicroScrubStep: (interactionId: string, value: number) => void;
  onChangeWorkspaceScoreSignalMicroNotePage: (interactionId: string, value: number) => void;
  onChangeActiveWorkspaceOverviewRowId: (value: string | null) => void;
  onNavigateHistoryEntry: (entryId: string) => void;
  onNavigateHistoryRelative: (delta: number) => void;
  onToggleHistoryEntryPinned: (entryId: string) => void;
  onTrimHistoryEntries: () => void;
  onSetHistoryConflictFieldSource: (
    auditId: string,
    fieldKey: ComparisonHistorySyncConflictFieldKey,
    source: ComparisonHistorySyncConflictFieldSource,
  ) => void;
  onSetHistoryConflictFieldSourceAll: (
    auditId: string,
    source: ComparisonHistorySyncConflictFieldSource,
  ) => void;
  onApplyHistoryConflictResolution: (auditId: string) => void;
  onSetHistoryPreferenceFieldSource: (
    auditId: string,
    fieldKey: ComparisonHistorySyncPreferenceFieldKey,
    source: ComparisonHistorySyncConflictFieldSource,
  ) => void;
  onSetHistoryPreferenceFieldSourceAll: (
    auditId: string,
    source: ComparisonHistorySyncConflictFieldSource,
  ) => void;
  onApplyHistoryPreferenceResolution: (auditId: string) => void;
  onSetHistoryWorkspaceFieldSource: (
    auditId: string,
    fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey,
    source: ComparisonHistorySyncConflictFieldSource,
  ) => void;
  onSetHistoryWorkspaceFieldSourceAll: (
    auditId: string,
    source: ComparisonHistorySyncConflictFieldSource,
  ) => void;
  onUseHistoryWorkspaceRankedSources: (auditId: string) => void;
  onApplyHistoryWorkspaceResolution: (auditId: string) => void;
  onToggleRunSelection: (runId: string) => void;
  onClearSelection: () => void;
  onSelectBenchmarkPair: () => void;
};

export type RunSectionRerunAction = {
  availabilityKey: keyof NonNullable<Run["action_availability"]>;
  label: string;
  onRerun: (rerunBoundaryId: string) => Promise<void>;
};

export type LiveOrderReplacementDraft = {
  price: string;
  quantity: string;
};

export type RunOrderControls = {
  getReplacementDraft: (orderId: string, order: Run["orders"][number]) => LiveOrderReplacementDraft;
  onChangeReplacementDraft: (orderId: string, draft: LiveOrderReplacementDraft) => void;
  onCancelOrder: (orderId: string) => Promise<void>;
  onReplaceOrder: (orderId: string, draft: LiveOrderReplacementDraft) => Promise<void>;
};

export type RunHistoryWorkspaceSectionProps = {
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
};

type RunHistoryWorkspacePanelInput = Omit<RunHistoryWorkspaceSectionProps, "surfaceKey" | "title"> & {
  title?: string;
};

export type BuildRunHistoryWorkspacePanelsInput = {
  renderRunSection: (props: RunHistoryWorkspaceSectionProps) => ReactNode;
  research: RunHistoryWorkspacePanelInput;
  runtime: {
    sandbox: RunHistoryWorkspacePanelInput;
    paper: RunHistoryWorkspacePanelInput;
  };
  live: RunHistoryWorkspacePanelInput;
};

export type RunHistoryWorkspacePanels = {
  research: {
    runsPanel: ReactNode;
  };
  runtime: {
    sandboxRunsPanel: ReactNode;
    paperRunsPanel: ReactNode;
  };
  live: {
    runsPanel: ReactNode;
  };
};

export function buildRunHistoryWorkspacePanels({
  live,
  renderRunSection,
  research,
  runtime,
}: BuildRunHistoryWorkspacePanelsInput): RunHistoryWorkspacePanels {
  return {
    research: {
      runsPanel: renderRunSection({
        ...research,
        surfaceKey: "backtest",
        title: research.title ?? "최근 Backtest",
      }),
    },
    runtime: {
      sandboxRunsPanel: renderRunSection({
        ...runtime.sandbox,
        surfaceKey: "sandbox",
        title: runtime.sandbox.title ?? "Sandbox Run",
      }),
      paperRunsPanel: renderRunSection({
        ...runtime.paper,
        surfaceKey: "paper",
        title: runtime.paper.title ?? "Paper Run",
      }),
    },
    live: {
      runsPanel: renderRunSection({
        ...live,
        surfaceKey: "live",
        title: live.title ?? "Guarded Live Run",
      }),
    },
  };
}

// Runtime placeholders for generated barrel compatibility.
export const RunSectionComparisonControls = undefined;
export const RunSectionRerunAction = undefined;
export const LiveOrderReplacementDraft = undefined;
export const RunOrderControls = undefined;
export const RunHistoryWorkspaceSectionProps = undefined;
export const BuildRunHistoryWorkspacePanelsInput = undefined;
export const RunHistoryWorkspacePanels = undefined;
