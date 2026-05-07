// @ts-nocheck
import { RunSection } from "../features/run-history/RunSection";
import {
  buildRunHistoryWorkspacePanels,
  type RunHistoryWorkspaceSectionProps,
} from "../routes/runHistoryWorkspacePanels";

const legacyReferenceRunMarkers = [
  "nostalgiaforinfinity",
  "nostalgia-for-infinity",
  "nfi_",
  "nfi-",
  "freqtrade_reference",
  "v17.3.",
];

export function isLegacyReferenceRun(run: any) {
  const provenance = run?.provenance ?? {};
  const strategy = provenance.strategy ?? {};
  if (provenance.lane === "reference") {
    return true;
  }
  if ("reference_id" in provenance || "reference" in provenance) {
    return true;
  }
  if ("reference_path" in strategy || "reference_id" in strategy) {
    return true;
  }
  if (strategy.runtime === "freqtrade_reference") {
    return true;
  }
  const legacyText = JSON.stringify({
    runId: run?.config?.run_id,
    strategyId: run?.config?.strategy_id,
    strategyVersion: run?.config?.strategy_version,
    strategyRuntime: strategy.runtime,
    strategyEntrypoint: strategy.entrypoint,
    strategyName: strategy.name,
  }).toLowerCase();
  return legacyReferenceRunMarkers.some((marker) => legacyText.includes(marker));
}

function visibleRuns(runs: any[]) {
  return Array.isArray(runs) ? runs.filter((run) => !isLegacyReferenceRun(run)) : [];
}

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
      runs: visibleRuns(backtests),
      presets,
      runSurfaceCapabilities: null,
      strategies,
      filter: backtestRunFilter,
      setFilter: setBacktestRunFilter,
      rerunActions: [
        {
          availabilityKey: "rerun_backtest",
          label: "백테스트 다시 실행",
          onRerun: rerunBacktest,
        },
        {
          availabilityKey: "rerun_sandbox",
          label: "샌드박스로 확인",
          onRerun: rerunSandbox,
        },
        {
          availabilityKey: "rerun_paper",
          label: "페이퍼로 확인",
          onRerun: rerunPaper,
        },
      ],
    },
    runtime: {
      sandbox: {
        runs: visibleRuns(sandboxRuns),
        presets,
        runSurfaceCapabilities: null,
        strategies,
        filter: sandboxRunFilter,
        setFilter: setSandboxRunFilter,
        rerunActions: [
          {
            availabilityKey: "rerun_sandbox",
            label: "샌드박스 다시 시작",
            onRerun: rerunSandbox,
          },
          {
            availabilityKey: "rerun_paper",
            label: "페이퍼로 확인",
            onRerun: rerunPaper,
          },
        ],
        onStop: stopSandboxRun,
      },
      paper: {
        runs: visibleRuns(paperRuns),
        presets,
        runSurfaceCapabilities: null,
        strategies,
        filter: paperRunFilter,
        setFilter: setPaperRunFilter,
        rerunActions: [
          {
            availabilityKey: "rerun_sandbox",
            label: "샌드박스로 확인",
            onRerun: rerunSandbox,
          },
          {
            availabilityKey: "rerun_paper",
            label: "페이퍼 다시 시작",
            onRerun: rerunPaper,
          },
        ],
        onStop: stopPaperRun,
      },
    },
    live: {
      runs: visibleRuns(liveRuns),
      presets,
      runSurfaceCapabilities: null,
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
