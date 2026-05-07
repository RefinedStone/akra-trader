// @ts-nocheck
import { RunSection } from "../features/run-history/RunSection";
import {
  buildRunHistoryWorkspacePanels,
  type RunHistoryWorkspaceSectionProps,
} from "../routes/runHistoryWorkspacePanels";

export function buildControlRoomRunHistoryWorkspacePanels(model: any) {
  const {
    backtestRunFilter,
    backtests,
    cancelLiveOrder,
    getLiveOrderReplacementDraft,
    liveRunFilter,
    liveRuns,
    paperRunFilter,
    paperRuns,
    presets,
    replaceLiveOrder,
    rerunBacktest,
    rerunPaper,
    rerunSandbox,
    runSurfaceCapabilities,
    sandboxRunFilter,
    sandboxRuns,
    setBacktestRunFilter,
    setLiveOrderReplacementDraft,
    setLiveRunFilter,
    setPaperRunFilter,
    setSandboxRunFilter,
    stopLiveRun,
    stopPaperRun,
    stopSandboxRun,
    strategies,
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
