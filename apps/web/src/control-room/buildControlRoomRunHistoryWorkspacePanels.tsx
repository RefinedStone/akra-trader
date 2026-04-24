// @ts-nocheck
import { RunSection } from "../features/run-history/RunSection";
import {
  buildRunHistoryWorkspacePanels,
  type RunHistoryWorkspaceSectionProps,
} from "../routes/runHistoryWorkspacePanels";

export function buildControlRoomRunHistoryWorkspacePanels(model: any) {
  const {
    activeWorkspaceOverviewRowId,
    backtestRunFilter,
    backtests,
    cancelLiveOrder,
    clearComparisonRuns,
    collapsedWorkspaceScoreSignalNestedSubviewIds,
    collapsedWorkspaceScoreSignalSubviewIds,
    comparisonHistoryAuditFilter,
    comparisonHistoryPanel,
    comparisonHistoryPanelOpen,
    comparisonHistorySearchQuery,
    comparisonHistorySharedSyncState,
    comparisonHistoryShowPinnedOnly,
    comparisonHistoryShowResolvedAuditEntries,
    comparisonHistoryStep,
    comparisonHistorySyncAuditTrail,
    comparisonHistoryTabIdentity,
    comparisonIntent,
    expandedHistoryConflictReviewIds,
    expandedWorkspaceScoreDetailIds,
    expandedWorkspaceScoreSignalDetailIds,
    focusedWorkspaceScoreDetailSignalKeys,
    focusedWorkspaceScoreDetailSources,
    focusedWorkspaceScoreSignalMicroInteractions,
    focusedWorkspaceScoreSignalMicroViews,
    getLiveOrderReplacementDraft,
    handleApplyComparisonHistoryConflictResolution,
    handleApplyComparisonHistoryPreferenceResolution,
    handleApplyComparisonHistoryWorkspaceResolution,
    handleComparisonIntentChange,
    handleNavigateComparisonHistoryEntry,
    handleNavigateComparisonHistoryRelative,
    handleSelectedComparisonScoreLinkChange,
    handleSetComparisonHistoryConflictFieldSource,
    handleSetComparisonHistoryConflictFieldSourceAll,
    handleSetComparisonHistoryPreferenceFieldSource,
    handleSetComparisonHistoryPreferenceFieldSourceAll,
    handleSetComparisonHistoryWorkspaceFieldSource,
    handleSetComparisonHistoryWorkspaceFieldSourceAll,
    handleToggleComparisonHistoryEntryPinned,
    handleTrimComparisonHistoryEntries,
    handleUseComparisonHistoryWorkspaceRankedSources,
    hoveredWorkspaceScoreSignalMicroTargets,
    latestWorkspaceSyncState,
    liveRunFilter,
    liveRuns,
    paperRunFilter,
    paperRuns,
    presets,
    replaceLiveOrder,
    rerunBacktest,
    rerunPaper,
    rerunSandbox,
    runComparison,
    runComparisonError,
    runComparisonLoading,
    runSurfaceCapabilities,
    sandboxRunFilter,
    sandboxRuns,
    scrubbedWorkspaceScoreSignalMicroSteps,
    selectBenchmarkPair,
    selectedComparisonRunIds,
    selectedComparisonScoreLink,
    selectedWorkspaceScoreSignalMicroNotePages,
    setActiveWorkspaceOverviewRowId,
    setBacktestRunFilter,
    setCollapsedWorkspaceScoreSignalNestedSubviewIds,
    setCollapsedWorkspaceScoreSignalSubviewIds,
    setComparisonHistoryAuditFilter,
    setComparisonHistoryPanelOpen,
    setComparisonHistorySearchQuery,
    setComparisonHistoryShowPinnedOnly,
    setComparisonHistoryShowResolvedAuditEntries,
    setExpandedHistoryConflictReviewIds,
    setExpandedWorkspaceScoreDetailIds,
    setExpandedWorkspaceScoreSignalDetailIds,
    setFocusedWorkspaceScoreDetailSignalKeys,
    setFocusedWorkspaceScoreDetailSources,
    setFocusedWorkspaceScoreSignalMicroInteractions,
    setFocusedWorkspaceScoreSignalMicroViews,
    setHoveredWorkspaceScoreSignalMicroTargets,
    setLiveOrderReplacementDraft,
    setLiveRunFilter,
    setPaperRunFilter,
    setSandboxRunFilter,
    setScrubbedWorkspaceScoreSignalMicroSteps,
    setSelectedWorkspaceScoreSignalMicroNotePages,
    stopLiveRun,
    stopPaperRun,
    stopSandboxRun,
    strategies,
    toggleComparisonRun,
    visibleComparisonHistoryActiveIndex,
    visibleComparisonHistoryEntries,
  } = model;

  return buildRunHistoryWorkspacePanels({
    renderRunSection: (props: RunHistoryWorkspaceSectionProps) => <RunSection {...props} />,
    research: {
      runs: backtests,
      presets,
      runSurfaceCapabilities,
      strategies,
      filter: backtestRunFilter,
      setFilter: setBacktestRunFilter,
      comparison: {
        selectedRunIds: selectedComparisonRunIds,
        comparisonIntent,
        latestWorkspaceSyncState,
        expandedHistoryConflictReviewIds,
        expandedWorkspaceScoreDetailIds,
        focusedWorkspaceScoreDetailSources,
        focusedWorkspaceScoreDetailSignalKeys,
        expandedWorkspaceScoreSignalDetailIds,
        collapsedWorkspaceScoreSignalSubviewIds,
        collapsedWorkspaceScoreSignalNestedSubviewIds,
        focusedWorkspaceScoreSignalMicroViews,
        focusedWorkspaceScoreSignalMicroInteractions,
        hoveredWorkspaceScoreSignalMicroTargets,
        scrubbedWorkspaceScoreSignalMicroSteps,
        selectedWorkspaceScoreSignalMicroNotePages,
        activeWorkspaceOverviewRowId,
        historyStep: comparisonHistoryStep,
        historyTabIdentity: comparisonHistoryTabIdentity,
        historySharedSync: comparisonHistorySharedSyncState,
        historySyncAuditTrail: comparisonHistorySyncAuditTrail,
        historyEntries: comparisonHistoryPanel.entries,
        visibleHistoryEntries: visibleComparisonHistoryEntries,
        activeHistoryEntryId: comparisonHistoryPanel.activeEntryId,
        historyBrowserOpen: comparisonHistoryPanelOpen,
        historySearchQuery: comparisonHistorySearchQuery,
        showPinnedHistoryOnly: comparisonHistoryShowPinnedOnly,
        historyAuditFilter: comparisonHistoryAuditFilter,
        showResolvedHistoryAudits: comparisonHistoryShowResolvedAuditEntries,
        canNavigateHistoryBackward: visibleComparisonHistoryActiveIndex > 0,
        canNavigateHistoryForward:
          visibleComparisonHistoryActiveIndex >= 0 &&
          visibleComparisonHistoryActiveIndex < visibleComparisonHistoryEntries.length - 1,
        selectedScoreLink: selectedComparisonScoreLink,
        payload: runComparison,
        loading: runComparisonLoading,
        error: runComparisonError,
        onChangeComparisonIntent: handleComparisonIntentChange,
        onChangeSelectedScoreLink: handleSelectedComparisonScoreLinkChange,
        onToggleHistoryBrowser: () => setComparisonHistoryPanelOpen((current: any) => !current),
        onChangeHistorySearchQuery: setComparisonHistorySearchQuery,
        onChangeShowPinnedHistoryOnly: setComparisonHistoryShowPinnedOnly,
        onChangeHistoryAuditFilter: setComparisonHistoryAuditFilter,
        onChangeShowResolvedHistoryAudits: setComparisonHistoryShowResolvedAuditEntries,
        onToggleHistoryConflictReview: (auditId) =>
          setExpandedHistoryConflictReviewIds((current: any) => ({
            ...current,
            [auditId]: !current[auditId],
          })),
        onToggleWorkspaceScoreDetail: (scoreDetailKey) =>
          setExpandedWorkspaceScoreDetailIds((current: any) => ({
            ...current,
            [scoreDetailKey]: !current[scoreDetailKey],
          })),
        onChangeFocusedWorkspaceScoreDetailSource: (scoreDetailKey, source) =>
          setFocusedWorkspaceScoreDetailSources((current: any) =>
            current[scoreDetailKey] === source
              ? current
              : {
                  ...current,
                  [scoreDetailKey]: source,
                },
          ),
        onChangeFocusedWorkspaceScoreDetailSignalKey: (scoreDetailKey, signalKey) =>
          setFocusedWorkspaceScoreDetailSignalKeys((current: any) => {
            if (!signalKey) {
              if (!(scoreDetailKey in current)) {
                return current;
              }
              const next = { ...current };
              delete next[scoreDetailKey];
              return next;
            }
            if (current[scoreDetailKey] === signalKey) {
              return current;
            }
            return {
              ...current,
              [scoreDetailKey]: signalKey,
            };
          }),
        onToggleWorkspaceScoreSignalDetail: (scoreDetailKey) =>
          setExpandedWorkspaceScoreSignalDetailIds((current: any) => ({
            ...current,
            [scoreDetailKey]: !current[scoreDetailKey],
          })),
        onToggleWorkspaceScoreSignalSubview: (subviewId) =>
          setCollapsedWorkspaceScoreSignalSubviewIds((current: any) => ({
            ...current,
            [subviewId]: !current[subviewId],
          })),
        onToggleWorkspaceScoreSignalNestedSubview: (subviewId) =>
          setCollapsedWorkspaceScoreSignalNestedSubviewIds((current: any) => ({
            ...current,
            [subviewId]: !current[subviewId],
          })),
        onChangeWorkspaceScoreSignalMicroView: (subviewId, value) =>
          setFocusedWorkspaceScoreSignalMicroViews((current: any) =>
            current[subviewId] === value
              ? current
              : {
                  ...current,
                  [subviewId]: value,
                },
          ),
        onChangeWorkspaceScoreSignalMicroInteraction: (interactionId, value) =>
          setFocusedWorkspaceScoreSignalMicroInteractions((current: any) =>
            current[interactionId] === value
              ? current
              : {
                  ...current,
                  [interactionId]: value,
                },
          ),
        onChangeWorkspaceScoreSignalMicroHoverTarget: (interactionId, value) =>
          setHoveredWorkspaceScoreSignalMicroTargets((current: any) =>
            current[interactionId] === value
              ? current
              : {
                  ...current,
                  [interactionId]: value,
                },
          ),
        onChangeWorkspaceScoreSignalMicroScrubStep: (interactionId, value) =>
          setScrubbedWorkspaceScoreSignalMicroSteps((current: any) =>
            current[interactionId] === value
              ? current
              : {
                  ...current,
                  [interactionId]: value,
                },
          ),
        onChangeWorkspaceScoreSignalMicroNotePage: (interactionId, value) =>
          setSelectedWorkspaceScoreSignalMicroNotePages((current: any) =>
            current[interactionId] === value
              ? current
              : {
                  ...current,
                  [interactionId]: value,
                },
          ),
        onChangeActiveWorkspaceOverviewRowId: setActiveWorkspaceOverviewRowId,
        onNavigateHistoryEntry: handleNavigateComparisonHistoryEntry,
        onNavigateHistoryRelative: handleNavigateComparisonHistoryRelative,
        onToggleHistoryEntryPinned: handleToggleComparisonHistoryEntryPinned,
        onTrimHistoryEntries: handleTrimComparisonHistoryEntries,
        onSetHistoryConflictFieldSource: handleSetComparisonHistoryConflictFieldSource,
        onSetHistoryConflictFieldSourceAll: handleSetComparisonHistoryConflictFieldSourceAll,
        onApplyHistoryConflictResolution: handleApplyComparisonHistoryConflictResolution,
        onSetHistoryPreferenceFieldSource: handleSetComparisonHistoryPreferenceFieldSource,
        onSetHistoryPreferenceFieldSourceAll: handleSetComparisonHistoryPreferenceFieldSourceAll,
        onApplyHistoryPreferenceResolution: handleApplyComparisonHistoryPreferenceResolution,
        onSetHistoryWorkspaceFieldSource: handleSetComparisonHistoryWorkspaceFieldSource,
        onSetHistoryWorkspaceFieldSourceAll: handleSetComparisonHistoryWorkspaceFieldSourceAll,
        onUseHistoryWorkspaceRankedSources: handleUseComparisonHistoryWorkspaceRankedSources,
        onApplyHistoryWorkspaceResolution: handleApplyComparisonHistoryWorkspaceResolution,
        onToggleRunSelection: toggleComparisonRun,
        onClearSelection: clearComparisonRuns,
        onSelectBenchmarkPair: selectBenchmarkPair,
      },
      rerunActions: [
        {
          availabilityKey: "rerun_backtest",
          label: "Rerun backtest",
          onRerun: rerunBacktest,
        },
        {
          availabilityKey: "rerun_sandbox",
          label: "Start sandbox worker",
          onRerun: rerunSandbox,
        },
        {
          availabilityKey: "rerun_paper",
          label: "Start paper session",
          onRerun: rerunPaper,
        },
      ],
    },
    runtime: {
      sandbox: {
        runs: sandboxRuns,
        presets,
        runSurfaceCapabilities,
        strategies,
        filter: sandboxRunFilter,
        setFilter: setSandboxRunFilter,
        rerunActions: [
          {
            availabilityKey: "rerun_sandbox",
            label: "Restore sandbox worker",
            onRerun: rerunSandbox,
          },
          {
            availabilityKey: "rerun_paper",
            label: "Start paper session",
            onRerun: rerunPaper,
          },
        ],
        onStop: stopSandboxRun,
      },
      paper: {
        runs: paperRuns,
        presets,
        runSurfaceCapabilities,
        strategies,
        filter: paperRunFilter,
        setFilter: setPaperRunFilter,
        rerunActions: [
          {
            availabilityKey: "rerun_sandbox",
            label: "Start sandbox worker",
            onRerun: rerunSandbox,
          },
          {
            availabilityKey: "rerun_paper",
            label: "Start paper session",
            onRerun: rerunPaper,
          },
        ],
        onStop: stopPaperRun,
      },
    },
    live: {
      runs: liveRuns,
      presets,
      runSurfaceCapabilities,
      strategies,
      filter: liveRunFilter,
      setFilter: setLiveRunFilter,
      onStop: stopLiveRun,
      getOrderControls: (run) => ({
        getReplacementDraft: (_orderId, order) =>
          getLiveOrderReplacementDraft(run.config.run_id, order),
        onChangeReplacementDraft: (orderId, draft) =>
          setLiveOrderReplacementDraft(run.config.run_id, orderId, draft),
        onCancelOrder: (orderId) => cancelLiveOrder(run.config.run_id, orderId),
        onReplaceOrder: (orderId, draft) =>
          replaceLiveOrder(run.config.run_id, orderId, draft),
      }),
    },
  });
}
