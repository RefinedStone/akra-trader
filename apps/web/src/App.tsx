import { FormEvent, useEffect, useMemo, useState } from "react";

type ParameterSchema = Record<
  string,
  {
    default?: unknown;
    minimum?: number;
    type?: string;
  }
>;

type Strategy = {
  strategy_id: string;
  name: string;
  version: string;
  version_lineage: string[];
  runtime: string;
  asset_types: string[];
  supported_timeframes: string[];
  parameter_schema: ParameterSchema;
  description: string;
  lifecycle: {
    stage: string;
    registered_at?: string | null;
  };
  reference_id?: string | null;
  reference_path?: string | null;
  entrypoint?: string | null;
};

type ReferenceSource = {
  reference_id: string;
  title: string;
  kind?: string;
  homepage?: string;
  license: string;
  integration_mode: string;
  local_path?: string | null;
  runtime?: string | null;
  summary: string;
};

type BenchmarkArtifact = {
  kind: string;
  label: string;
  path: string;
  format?: string | null;
  exists: boolean;
  is_directory: boolean;
  summary: Record<string, unknown>;
  sections?: Record<string, Record<string, unknown>>;
  summary_source_path?: string | null;
};

type Run = {
  config: {
    run_id: string;
    mode: string;
    strategy_id: string;
    strategy_version: string;
    symbols: string[];
    timeframe: string;
    initial_cash: number;
  };
  status: string;
  started_at: string;
  ended_at?: string | null;
  provenance: {
    lane: string;
    reference_id?: string | null;
    reference_version?: string | null;
    integration_mode?: string | null;
    reference?: ReferenceSource | null;
    working_directory?: string | null;
    external_command: string[];
    artifact_paths: string[];
    benchmark_artifacts: BenchmarkArtifact[];
    strategy?: {
      strategy_id: string;
      name: string;
      version: string;
      version_lineage: string[];
      runtime: string;
      lifecycle: {
        stage: string;
        registered_at?: string | null;
      };
      parameter_snapshot: {
        requested: Record<string, unknown>;
        resolved: Record<string, unknown>;
        schema: ParameterSchema;
      };
      supported_timeframes: string[];
      warmup: {
        required_bars: number;
        timeframes: string[];
      };
      reference_id?: string | null;
      reference_path?: string | null;
      entrypoint?: string | null;
    } | null;
    market_data?: {
      provider: string;
      venue: string;
      symbols: string[];
      timeframe: string;
      requested_start_at?: string | null;
      requested_end_at?: string | null;
      effective_start_at?: string | null;
      effective_end_at?: string | null;
      candle_count: number;
      sync_status: string;
      last_sync_at?: string | null;
      issues: string[];
    } | null;
    market_data_by_symbol?: Record<
      string,
      {
        provider: string;
        venue: string;
        symbols: string[];
        timeframe: string;
        requested_start_at?: string | null;
        requested_end_at?: string | null;
        effective_start_at?: string | null;
        effective_end_at?: string | null;
        candle_count: number;
        sync_status: string;
        last_sync_at?: string | null;
        issues: string[];
      }
    >;
  };
  metrics: Record<string, number>;
  notes: string[];
};

type RunComparison = {
  requested_run_ids: string[];
  baseline_run_id: string;
  intent: ComparisonIntent;
  runs: {
    run_id: string;
    mode: string;
    status: string;
    lane: string;
    strategy_id: string;
    strategy_name?: string | null;
    strategy_version: string;
    symbols: string[];
    timeframe: string;
    started_at: string;
    ended_at?: string | null;
    reference_id?: string | null;
    reference_version?: string | null;
    integration_mode?: string | null;
    reference?: ReferenceSource | null;
    working_directory?: string | null;
    external_command: string[];
    artifact_paths: string[];
    benchmark_artifacts: BenchmarkArtifact[];
    metrics: Record<string, number>;
    notes: string[];
  }[];
  metric_rows: {
    key: string;
    label: string;
    unit: string;
    higher_is_better?: boolean | null;
    values: Record<string, number | null>;
    deltas_vs_baseline: Record<string, number | null>;
    best_run_id?: string | null;
  }[];
  narratives: {
    run_id: string;
    baseline_run_id: string;
    comparison_type: string;
    title: string;
    summary: string;
    bullets: string[];
    rank: number;
    insight_score: number;
    is_primary: boolean;
  }[];
};

type MarketDataStatus = {
  provider: string;
  venue: string;
  instruments: {
    instrument_id: string;
    timeframe: string;
    candle_count: number;
    first_timestamp: string | null;
    last_timestamp: string | null;
    sync_status: string;
    lag_seconds: number | null;
    last_sync_at: string | null;
    backfill_target_candles: number | null;
    backfill_completion_ratio: number | null;
    backfill_complete: boolean | null;
    backfill_contiguous_completion_ratio: number | null;
    backfill_contiguous_complete: boolean | null;
    backfill_contiguous_missing_candles: number | null;
    backfill_gap_windows: {
      start_at: string;
      end_at: string;
      missing_candles: number;
    }[];
    issues: string[];
  }[];
};

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";
const MAX_VISIBLE_GAP_WINDOWS = 3;
const CONTROL_ROOM_UI_STATE_STORAGE_KEY = "akra-trader-control-room-ui-state";
const CONTROL_ROOM_UI_STATE_VERSION = 1;
const LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY = "akra-trader-gap-window-expansion";
const ALL_FILTER_VALUE = "__all__";
const MAX_COMPARISON_RUNS = 4;

type ControlRoomUiStateV1 = {
  version: typeof CONTROL_ROOM_UI_STATE_VERSION;
  expandedGapRows: Record<string, boolean>;
};

type RunHistoryFilter = {
  strategy_id: string;
  strategy_version: string;
};

type ComparisonIntent = "benchmark_validation" | "execution_regression" | "strategy_tuning";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

const defaultRunForm = {
  strategy_id: "ma_cross_v1",
  symbol: "BTC/USDT",
  timeframe: "5m",
  initial_cash: 10000,
  fee_rate: 0.001,
  slippage_bps: 3,
};

const defaultRunHistoryFilter: RunHistoryFilter = {
  strategy_id: ALL_FILTER_VALUE,
  strategy_version: ALL_FILTER_VALUE,
};

const DEFAULT_COMPARISON_INTENT: ComparisonIntent = "benchmark_validation";
const comparisonIntentOptions: ComparisonIntent[] = [
  "benchmark_validation",
  "execution_regression",
  "strategy_tuning",
];

export default function App() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [references, setReferences] = useState<ReferenceSource[]>([]);
  const [backtests, setBacktests] = useState<Run[]>([]);
  const [sandboxRuns, setSandboxRuns] = useState<Run[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketDataStatus | null>(null);
  const [statusText, setStatusText] = useState("Loading control room...");
  const [backtestForm, setBacktestForm] = useState(defaultRunForm);
  const [sandboxForm, setSandboxForm] = useState(defaultRunForm);
  const [backtestRunFilter, setBacktestRunFilter] = useState<RunHistoryFilter>(defaultRunHistoryFilter);
  const [sandboxRunFilter, setSandboxRunFilter] = useState<RunHistoryFilter>(defaultRunHistoryFilter);
  const [selectedComparisonRunIds, setSelectedComparisonRunIds] = useState<string[]>([]);
  const [comparisonIntent, setComparisonIntent] = useState<ComparisonIntent>(DEFAULT_COMPARISON_INTENT);
  const [runComparison, setRunComparison] = useState<RunComparison | null>(null);
  const [runComparisonLoading, setRunComparisonLoading] = useState(false);
  const [runComparisonError, setRunComparisonError] = useState<string | null>(null);
  const [expandedGapRows, setExpandedGapRows] = useState<Record<string, boolean>>(
    loadExpandedGapRows,
  );

  async function loadAll() {
    setStatusText("Refreshing data plane...");
    try {
      const [strategiesResponse, referencesResponse, backtestsResponse, sandboxResponse, marketResponse] = await Promise.all([
        fetchJson<Strategy[]>("/strategies"),
        fetchJson<ReferenceSource[]>("/references"),
        fetchJson<Run[]>(buildRunsPath("backtest", backtestRunFilter)),
        fetchJson<Run[]>(buildRunsPath("sandbox", sandboxRunFilter)),
        fetchJson<MarketDataStatus>("/market-data/status"),
      ]);
      setStrategies(strategiesResponse);
      setReferences(referencesResponse);
      setBacktests(backtestsResponse);
      setSandboxRuns(sandboxResponse);
      setMarketStatus(marketResponse);
      setStatusText("Control room synchronized.");
    } catch (error) {
      setStatusText(`Load failed: ${(error as Error).message}`);
    }
  }

  useEffect(() => {
    void loadAll();
  }, [backtestRunFilter, sandboxRunFilter]);

  useEffect(() => {
    if (!strategies.length) {
      return;
    }
    const preferredNative = strategies.find((strategy) => strategy.runtime === "native") ?? strategies[0];
    setBacktestForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
    setSandboxForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
  }, [strategies]);

  useEffect(() => {
    if (!strategies.length) {
      return;
    }
    setBacktestRunFilter((current) => normalizeRunHistoryFilter(current, strategies));
    setSandboxRunFilter((current) => normalizeRunHistoryFilter(current, strategies));
  }, [strategies]);

  useEffect(() => {
    const availableRunIds = new Set(backtests.map((run) => run.config.run_id));
    setSelectedComparisonRunIds((current) => {
      const next = current.filter((runId) => availableRunIds.has(runId));
      return next.length === current.length ? current : next;
    });
  }, [backtests]);

  useEffect(() => {
    if (selectedComparisonRunIds.length < 2) {
      setRunComparison(null);
      setRunComparisonError(null);
      setRunComparisonLoading(false);
      return;
    }

    let cancelled = false;
    setRunComparisonLoading(true);
    setRunComparisonError(null);

    void fetchJson<RunComparison>(buildRunComparisonPath(selectedComparisonRunIds, comparisonIntent))
      .then((payload) => {
        if (cancelled) {
          return;
        }
        setRunComparison(payload);
      })
      .catch((error) => {
        if (cancelled) {
          return;
        }
        setRunComparison(null);
        setRunComparisonError((error as Error).message);
      })
      .finally(() => {
        if (!cancelled) {
          setRunComparisonLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedComparisonRunIds, comparisonIntent]);

  useEffect(() => {
    persistExpandedGapRows(expandedGapRows);
  }, [expandedGapRows]);

  useEffect(() => {
    if (!marketStatus) {
      return;
    }
    setExpandedGapRows((current) => pruneExpandedGapRows(current, marketStatus));
  }, [marketStatus]);

  const strategyGroups = useMemo(() => {
    return {
      native: strategies.filter((strategy) => strategy.runtime === "native"),
      reference: strategies.filter((strategy) => strategy.runtime === "freqtrade_reference"),
      future: strategies.filter((strategy) => strategy.runtime === "decision_engine"),
    };
  }, [strategies]);

  const backfillSummary = useMemo(() => {
    if (!marketStatus) {
      return null;
    }
    const tracked = marketStatus.instruments.filter(
      (instrument) => instrument.backfill_target_candles !== null,
    );
    if (!tracked.length) {
      return null;
    }
    const contiguousTracked = tracked.filter(
      (instrument) => instrument.backfill_contiguous_completion_ratio !== null,
    );
    const targetCandles = tracked.reduce(
      (total, instrument) => total + (instrument.backfill_target_candles ?? 0),
      0,
    );
    const coveredCandles = tracked.reduce(
      (total, instrument) =>
        total +
        Math.min(
          instrument.candle_count,
          instrument.backfill_target_candles ?? instrument.candle_count,
        ),
      0,
    );
    const completeCount = tracked.filter((instrument) => instrument.backfill_complete).length;
    return {
      targetCandles,
      coveredCandles,
      completeCount,
      instrumentCount: tracked.length,
      completionRatio: targetCandles > 0 ? coveredCandles / targetCandles : null,
      contiguousQualityRatio:
        contiguousTracked.length > 0
          ? contiguousTracked.reduce(
              (total, instrument) =>
                total + (instrument.backfill_contiguous_completion_ratio ?? 0),
              0,
            ) / contiguousTracked.length
          : null,
      contiguousCompleteCount: contiguousTracked.filter(
        (instrument) => instrument.backfill_contiguous_complete,
      ).length,
      contiguousInstrumentCount: contiguousTracked.length,
    };
  }, [marketStatus]);

  async function handleBacktestSubmit(event: FormEvent) {
    event.preventDefault();
    setStatusText("Running backtest...");
    try {
      await fetchJson<Run>("/runs/backtests", {
        method: "POST",
        body: JSON.stringify({ ...backtestForm, parameters: {} }),
      });
      await loadAll();
    } catch (error) {
      setStatusText(`Backtest failed: ${(error as Error).message}`);
    }
  }

  async function handleSandboxSubmit(event: FormEvent) {
    event.preventDefault();
    setStatusText("Starting sandbox run...");
    try {
      await fetchJson<Run>("/runs/sandbox", {
        method: "POST",
        body: JSON.stringify({ ...sandboxForm, parameters: {}, replay_bars: 96 }),
      });
      await loadAll();
    } catch (error) {
      setStatusText(`Sandbox run failed: ${(error as Error).message}`);
    }
  }

  async function stopSandboxRun(runId: string) {
    setStatusText(`Stopping run ${runId}...`);
    try {
      await fetchJson<Run>(`/runs/sandbox/${runId}/stop`, { method: "POST" });
      await loadAll();
    } catch (error) {
      setStatusText(`Stop failed: ${(error as Error).message}`);
    }
  }

  function toggleComparisonRun(runId: string) {
    setSelectedComparisonRunIds((current) => {
      if (current.includes(runId)) {
        return current.filter((value) => value !== runId);
      }
      if (current.length >= MAX_COMPARISON_RUNS) {
        setStatusText(`Comparison supports up to ${MAX_COMPARISON_RUNS} backtests at once.`);
        return current;
      }
      return [...current, runId];
    });
  }

  function clearComparisonRuns() {
    setSelectedComparisonRunIds([]);
  }

  function selectBenchmarkPair() {
    const nativeRun = pickLatestBenchmarkRun(backtests, "native");
    const referenceRun = pickLatestBenchmarkRun(backtests, "reference");

    if (!nativeRun || !referenceRun) {
      setStatusText("Benchmark comparison needs one native and one reference backtest.");
      return;
    }

    setComparisonIntent(DEFAULT_COMPARISON_INTENT);
    setSelectedComparisonRunIds([nativeRun.config.run_id, referenceRun.config.run_id]);
  }

  return (
    <div className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Akra Trader / Hexagonal Control Room</p>
          <h1>Strategy operations with native engines and NFI reference delegates.</h1>
          <p className="hero-copy">
            The backend separates feature building, decision context creation, and execution so
            rule-based strategies, Freqtrade references, and future LLM policies can share the
            same orchestration layer.
          </p>
        </div>
        <aside className="hero-panel">
          <span className="status-indicator" />
          <strong>{statusText}</strong>
          <p>API base: {apiBase}</p>
        </aside>
      </header>

      <main className="grid">
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

          <div className="strategy-columns">
            <StrategyColumn title="Native" strategies={strategyGroups.native} accent="amber" />
            <StrategyColumn title="NFI References" strategies={strategyGroups.reference} accent="cyan" />
            <StrategyColumn title="Future LLM" strategies={strategyGroups.future} accent="ember" />
          </div>
        </section>

        <section className="panel">
          <p className="kicker">Backtest</p>
          <h2>Launch a run</h2>
          <RunForm form={backtestForm} setForm={setBacktestForm} strategies={strategies} onSubmit={handleBacktestSubmit} />
        </section>

        <section className="panel">
          <p className="kicker">Sandbox</p>
          <h2>Start native replay</h2>
          <RunForm form={sandboxForm} setForm={setSandboxForm} strategies={strategies.filter((strategy) => strategy.runtime === "native")} onSubmit={handleSandboxSubmit} />
        </section>

        <section className="panel panel-wide">
          <p className="kicker">Reference lane</p>
          <h2>Third-party references</h2>
          <ReferenceCatalog references={references} />
        </section>

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
                    <th>Issues</th>
                  </tr>
                </thead>
                <tbody>
                  {marketStatus.instruments.map((instrument) => (
                    <tr key={instrument.instrument_id}>
                      <td>{instrument.instrument_id}</td>
                      <td>{instrument.timeframe}</td>
                      <td>{instrument.sync_status}</td>
                      <td>{instrument.candle_count}</td>
                      <td>{instrument.backfill_target_candles ?? "n/a"}</td>
                      <td>
                        <BackfillCountStatus instrument={instrument} />
                      </td>
                      <td>
                        <BackfillQualityStatus
                          expanded={Boolean(expandedGapRows[instrumentGapRowKey(instrument)])}
                          instrument={instrument}
                          onToggle={() => {
                            const key = instrumentGapRowKey(instrument);
                            setExpandedGapRows((current) => toggleExpandedGapRow(current, key));
                          }}
                        />
                      </td>
                      <td>{instrument.lag_seconds ?? "n/a"}</td>
                      <td>{instrument.last_timestamp ?? "n/a"}</td>
                      <td>{instrument.issues.length ? instrument.issues.join(", ") : "ok"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No data status loaded.</p>
          )}
        </section>

        <RunSection
          title="Recent backtests"
          runs={backtests}
          strategies={strategies}
          filter={backtestRunFilter}
          setFilter={setBacktestRunFilter}
          comparison={{
            selectedRunIds: selectedComparisonRunIds,
            comparisonIntent,
            payload: runComparison,
            loading: runComparisonLoading,
            error: runComparisonError,
            onChangeComparisonIntent: setComparisonIntent,
            onToggleRunSelection: toggleComparisonRun,
            onClearSelection: clearComparisonRuns,
            onSelectBenchmarkPair: selectBenchmarkPair,
          }}
        />
        <RunSection
          title="Sandbox runs"
          runs={sandboxRuns}
          strategies={strategies}
          filter={sandboxRunFilter}
          setFilter={setSandboxRunFilter}
          onStop={stopSandboxRun}
        />
      </main>
    </div>
  );
}

function BackfillCountStatus({
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  if (instrument.backfill_target_candles === null) {
    return <span>n/a</span>;
  }
  return (
    <div className="progress-stack">
      <strong>{formatCompletion(instrument.backfill_completion_ratio)}</strong>
      <span>
        {Math.min(instrument.candle_count, instrument.backfill_target_candles)} /{" "}
        {instrument.backfill_target_candles}
        {instrument.backfill_complete ? " ready" : ""}
      </span>
      <div className="progress-track" aria-hidden="true">
        <span
          style={{
            width: `${Math.round((instrument.backfill_completion_ratio ?? 0) * 100)}%`,
          }}
        />
      </div>
    </div>
  );
}

function BackfillQualityStatus({
  expanded,
  instrument,
  onToggle,
}: {
  expanded: boolean;
  instrument: MarketDataStatus["instruments"][number];
  onToggle: () => void;
}) {
  if (instrument.backfill_contiguous_completion_ratio === null) {
    return <span>n/a</span>;
  }
  const canToggleGapWindows = instrument.backfill_gap_windows.length > MAX_VISIBLE_GAP_WINDOWS;
  const gapLines = expanded
    ? formatGapWindows(instrument.backfill_gap_windows)
    : summarizeGapWindows(instrument.backfill_gap_windows);
  return (
    <div className="progress-stack">
      <strong>{formatCompletion(instrument.backfill_contiguous_completion_ratio)}</strong>
      <span>
        {instrument.backfill_contiguous_complete
          ? "gap-free"
          : `gaps: ${instrument.backfill_contiguous_missing_candles ?? 0}`}
      </span>
      {gapLines.length ? (
        <div className="progress-detail-list">
          {gapLines.map((line) => (
            <span
              className={line.kind === "summary" ? "progress-detail-summary" : undefined}
              key={line.key}
            >
              {line.label}
            </span>
          ))}
        </div>
      ) : null}
      {canToggleGapWindows ? (
        <button
          className="progress-toggle"
          onClick={onToggle}
          type="button"
        >
          {expanded
            ? "Collapse gaps"
            : `Show all ${instrument.backfill_gap_windows.length} gaps`}
        </button>
      ) : null}
      <div className="progress-track" aria-hidden="true">
        <span
          style={{
            width: `${Math.round((instrument.backfill_contiguous_completion_ratio ?? 0) * 100)}%`,
          }}
        />
      </div>
    </div>
  );
}

function formatCompletion(value: number | null) {
  if (value === null) {
    return "n/a";
  }
  return `${Math.round(value * 100)}%`;
}

function summarizeGapWindows(
  gapWindows: MarketDataStatus["instruments"][number]["backfill_gap_windows"],
) {
  if (gapWindows.length <= MAX_VISIBLE_GAP_WINDOWS) {
    return formatGapWindows(gapWindows);
  }

  const recentWindows = gapWindows.slice(-(MAX_VISIBLE_GAP_WINDOWS - 1));
  const collapsedWindows = gapWindows.slice(0, -(MAX_VISIBLE_GAP_WINDOWS - 1));
  const collapsedMissing = collapsedWindows.reduce(
    (total, gap) => total + gap.missing_candles,
    0,
  );
  const lastCollapsedWindow = collapsedWindows[collapsedWindows.length - 1];

  return [
    {
      key: `summary-${collapsedWindows[0].start_at}-${lastCollapsedWindow.end_at}`,
      kind: "summary" as const,
      label:
        `${collapsedWindows.length} older windows | ` +
        `${formatRange(collapsedWindows[0].start_at, lastCollapsedWindow.end_at)} | ` +
        `${collapsedMissing} missing`,
    },
    ...formatGapWindows(recentWindows),
  ];
}

function formatGapWindows(
  gapWindows: MarketDataStatus["instruments"][number]["backfill_gap_windows"],
) {
  return gapWindows.map((gap, index) => ({
    key: `${gap.start_at}-${gap.end_at}-${index}`,
    kind: "exact" as const,
    label: `${formatRange(gap.start_at, gap.end_at)} (${gap.missing_candles})`,
  }));
}

function instrumentGapRowKey(instrument: MarketDataStatus["instruments"][number]) {
  return `${instrument.instrument_id}:${instrument.timeframe}`;
}

function toggleExpandedGapRow(current: Record<string, boolean>, key: string) {
  if (current[key]) {
    const next = { ...current };
    delete next[key];
    return next;
  }
  return { ...current, [key]: true };
}

function pruneExpandedGapRows(
  current: Record<string, boolean>,
  marketStatus: MarketDataStatus,
) {
  const activeKeys = new Set(
    marketStatus.instruments
      .filter((instrument) => instrument.backfill_gap_windows.length > MAX_VISIBLE_GAP_WINDOWS)
      .map((instrument) => instrumentGapRowKey(instrument)),
  );
  const next = Object.fromEntries(
    Object.entries(current).filter(([key, expanded]) => expanded && activeKeys.has(key)),
  );
  const currentKeys = Object.keys(current);
  const nextKeys = Object.keys(next);
  if (
    currentKeys.length === nextKeys.length &&
    currentKeys.every((key) => next[key] === current[key])
  ) {
    return current;
  }
  return next;
}

function loadExpandedGapRows() {
  const persistedState = loadControlRoomUiState();
  if (persistedState) {
    return persistedState.expandedGapRows;
  }
  return loadLegacyExpandedGapRows();
}

function loadControlRoomUiState() {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(CONTROL_ROOM_UI_STATE_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (!isControlRoomUiStateV1(parsed)) {
      return null;
    }
    return {
      version: parsed.version,
      expandedGapRows: filterExpandedGapRows(parsed.expandedGapRows),
    };
  } catch {
    return null;
  }
}

function persistExpandedGapRows(value: Record<string, boolean>) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: ControlRoomUiStateV1 = {
      version: CONTROL_ROOM_UI_STATE_VERSION,
      expandedGapRows: filterExpandedGapRows(value),
    };
    window.localStorage.setItem(
      CONTROL_ROOM_UI_STATE_STORAGE_KEY,
      JSON.stringify(nextState),
    );
    window.localStorage.removeItem(LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY);
  } catch {
    return;
  }
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

function isControlRoomUiStateV1(value: unknown): value is ControlRoomUiStateV1 {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ControlRoomUiStateV1>;
  return (
    candidate.version === CONTROL_ROOM_UI_STATE_VERSION &&
    candidate.expandedGapRows !== undefined
  );
}

function buildRunsPath(mode: string, filter: RunHistoryFilter) {
  const params = new URLSearchParams({ mode });
  if (filter.strategy_id !== ALL_FILTER_VALUE) {
    params.set("strategy_id", filter.strategy_id);
  }
  if (filter.strategy_version !== ALL_FILTER_VALUE) {
    params.set("strategy_version", filter.strategy_version);
  }
  return `/runs?${params.toString()}`;
}

function buildRunComparisonPath(runIds: string[], intent: ComparisonIntent) {
  const params = new URLSearchParams();
  runIds.forEach((runId) => params.append("run_id", runId));
  params.set("intent", intent);
  return `/runs/compare?${params.toString()}`;
}

function normalizeRunHistoryFilter(current: RunHistoryFilter, strategies: Strategy[]) {
  const availableStrategyIds = new Set(strategies.map((strategy) => strategy.strategy_id));
  if (
    current.strategy_id !== ALL_FILTER_VALUE &&
    !availableStrategyIds.has(current.strategy_id)
  ) {
    return defaultRunHistoryFilter;
  }
  const availableVersions = getStrategyVersionOptions(strategies, current.strategy_id);
  if (
    current.strategy_version !== ALL_FILTER_VALUE &&
    !availableVersions.includes(current.strategy_version)
  ) {
    return { ...current, strategy_version: ALL_FILTER_VALUE };
  }
  return current;
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

function pickLatestBenchmarkRun(runs: Run[], lane: string) {
  return (
    runs.find((run) => run.provenance.lane === lane && run.status === "completed") ??
    runs.find((run) => run.provenance.lane === lane) ??
    null
  );
}

function StrategyColumn({
  title,
  strategies,
  accent,
}: {
  title: string;
  strategies: Strategy[];
  accent: string;
}) {
  return (
    <div className={`strategy-column ${accent}`}>
      <h3>{title}</h3>
      {strategies.length ? (
        strategies.map((strategy) => (
          <article className="strategy-card" key={strategy.strategy_id}>
            <div className="strategy-head">
              <div>
                <strong>{strategy.name}</strong>
                <div className="strategy-badges">
                  <span className="meta-pill">{formatLaneLabel(strategy.runtime)}</span>
                  <span className="meta-pill subtle">{strategy.lifecycle.stage}</span>
                  <span className="meta-pill subtle">{strategy.version}</span>
                </div>
              </div>
              <span>{formatVersionLineage(strategy.version_lineage, strategy.version)}</span>
            </div>
            <p>{strategy.description}</p>
            <dl>
              <div>
                <dt>ID</dt>
                <dd>{strategy.strategy_id}</dd>
              </div>
              <div>
                <dt>Timeframes</dt>
                <dd>{strategy.supported_timeframes.join(", ")}</dd>
              </div>
              <div>
                <dt>Assets</dt>
                <dd>{strategy.asset_types.join(", ")}</dd>
              </div>
              <div>
                <dt>Defaults</dt>
                <dd>{formatParameterMap(extractDefaultParameters(strategy.parameter_schema))}</dd>
              </div>
              {strategy.reference_path ? (
                <div>
                  <dt>Reference</dt>
                  <dd>{strategy.reference_path}</dd>
                </div>
              ) : null}
              {strategy.reference_id ? (
                <div>
                  <dt>Reference ID</dt>
                  <dd>{strategy.reference_id}</dd>
                </div>
              ) : null}
              {strategy.lifecycle.registered_at ? (
                <div>
                  <dt>Registered</dt>
                  <dd>{formatTimestamp(strategy.lifecycle.registered_at)}</dd>
                </div>
              ) : null}
            </dl>
          </article>
        ))
      ) : (
        <p className="empty-state">No strategies registered.</p>
      )}
    </div>
  );
}

function ReferenceCatalog({ references }: { references: ReferenceSource[] }) {
  return references.length ? (
    <div className="run-list">
      {references.map((reference) => (
        <article className="run-card" key={reference.reference_id}>
          <div className="run-card-head">
            <div>
              <strong>{reference.title}</strong>
              <span>{reference.reference_id}</span>
            </div>
            <div className="run-status completed">{reference.integration_mode}</div>
          </div>
          <div className="run-metrics">
            <Metric label="License" value={reference.license} />
            <Metric label="Runtime" value={reference.runtime ?? "n/a"} />
          </div>
          <p className="run-note">{reference.summary}</p>
        </article>
      ))}
    </div>
  ) : (
    <p className="empty-state">No references registered.</p>
  );
}

function RunForm({
  form,
  setForm,
  strategies,
  onSubmit,
}: {
  form: typeof defaultRunForm;
  setForm: (updater: (value: typeof defaultRunForm) => typeof defaultRunForm) => void;
  strategies: Strategy[];
  onSubmit: (event: FormEvent) => Promise<void> | void;
}) {
  return (
    <form className="run-form" onSubmit={onSubmit}>
      <label>
        Strategy
        <select
          value={form.strategy_id}
          onChange={(event) => setForm((current) => ({ ...current, strategy_id: event.target.value }))}
        >
          {strategies.map((strategy) => (
            <option key={strategy.strategy_id} value={strategy.strategy_id}>
              {strategy.name} / {strategy.runtime}
            </option>
          ))}
        </select>
      </label>
      <label>
        Symbol
        <input
          value={form.symbol}
          onChange={(event) => setForm((current) => ({ ...current, symbol: event.target.value }))}
        />
      </label>
      <label>
        Timeframe
        <input
          value={form.timeframe}
          onChange={(event) => setForm((current) => ({ ...current, timeframe: event.target.value }))}
        />
      </label>
      <label>
        Initial cash
        <input
          type="number"
          value={form.initial_cash}
          onChange={(event) => setForm((current) => ({ ...current, initial_cash: Number(event.target.value) }))}
        />
      </label>
      <label>
        Fee rate
        <input
          type="number"
          step="0.0001"
          value={form.fee_rate}
          onChange={(event) => setForm((current) => ({ ...current, fee_rate: Number(event.target.value) }))}
        />
      </label>
      <label>
        Slippage (bps)
        <input
          type="number"
          value={form.slippage_bps}
          onChange={(event) => setForm((current) => ({ ...current, slippage_bps: Number(event.target.value) }))}
        />
      </label>
      <button type="submit">Submit</button>
    </form>
  );
}

type RunSectionComparisonControls = {
  selectedRunIds: string[];
  comparisonIntent: ComparisonIntent;
  payload: RunComparison | null;
  loading: boolean;
  error: string | null;
  onChangeComparisonIntent: (intent: ComparisonIntent) => void;
  onToggleRunSelection: (runId: string) => void;
  onClearSelection: () => void;
  onSelectBenchmarkPair: () => void;
};

function RunSection({
  title,
  runs,
  strategies,
  filter,
  setFilter,
  comparison,
  onStop,
}: {
  title: string;
  runs: Run[];
  strategies: Strategy[];
  filter: RunHistoryFilter;
  setFilter: (updater: (value: RunHistoryFilter) => RunHistoryFilter) => void;
  comparison?: RunSectionComparisonControls;
  onStop?: (runId: string) => Promise<void>;
}) {
  const versionOptions = getStrategyVersionOptions(strategies, filter.strategy_id);

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
          </div>
          {comparison ? (
            <div className="comparison-toolbar">
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
            </div>
          ) : null}
        </div>
      </div>
      {runs.length ? (
        <div className="run-list">
          {runs.map((run) => (
            <article className="run-card" key={run.config.run_id}>
              <div className="run-card-head">
                <div>
                  <strong>{run.config.strategy_id}</strong>
                  <span>
                    {run.config.symbols.join(", ")} / {run.config.strategy_version}
                  </span>
                </div>
                <div className={`run-status ${run.status}`}>{run.status}</div>
              </div>
              <div className="run-metrics">
                <Metric label="Mode" value={run.config.mode} />
                <Metric label="Lane" value={run.provenance.lane} />
                <Metric
                  label="Lifecycle"
                  value={run.provenance.strategy?.lifecycle.stage ?? "n/a"}
                />
                <Metric label="Version" value={run.config.strategy_version} />
                <Metric label="Return" value={formatMetric(run.metrics.total_return_pct, "%")} />
                <Metric label="Drawdown" value={formatMetric(run.metrics.max_drawdown_pct, "%")} />
                <Metric label="Win rate" value={formatMetric(run.metrics.win_rate_pct, "%")} />
                <Metric label="Trades" value={formatMetric(run.metrics.trade_count)} />
              </div>
              {run.provenance.strategy ? (
                <RunStrategySnapshot strategy={run.provenance.strategy} />
              ) : null}
              <p className="run-note">
                {run.provenance.reference_id
                  ? `Reference ${run.provenance.reference_id} (${run.provenance.reference_version ?? "unknown"})`
                  : run.notes[0] ?? "No notes recorded."}
              </p>
              {run.provenance.reference ? (
                <ReferenceRunProvenanceSummary
                  artifactPaths={run.provenance.artifact_paths}
                  benchmarkArtifacts={run.provenance.benchmark_artifacts}
                  externalCommand={run.provenance.external_command}
                  reference={run.provenance.reference}
                  referenceVersion={run.provenance.reference_version}
                  workingDirectory={run.provenance.working_directory}
                />
              ) : null}
              {run.provenance.market_data ? (
                <RunMarketDataLineage
                  lineage={run.provenance.market_data}
                  lineageBySymbol={run.provenance.market_data_by_symbol}
                />
              ) : null}
              <div className="run-card-actions">
                {comparison ? (
                  <button
                    className="ghost-button"
                    onClick={() => comparison.onToggleRunSelection(run.config.run_id)}
                    type="button"
                  >
                    {comparison.selectedRunIds.includes(run.config.run_id)
                      ? "Remove from compare"
                      : "Add to compare"}
                  </button>
                ) : null}
                {onStop && run.status === "running" ? (
                  <button className="ghost-button" onClick={() => void onStop(run.config.run_id)} type="button">
                    Stop
                  </button>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="empty-state">No runs yet.</p>
      )}
      {comparison ? (
        <RunComparisonPanel
          comparison={comparison.payload}
          error={comparison.error}
          loading={comparison.loading}
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
  selectedRunIds,
}: {
  comparison: RunComparison | null;
  error: string | null;
  loading: boolean;
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

  return (
    <section className="comparison-panel">
      <div className="comparison-head">
        <div>
          <p className="kicker">Comparison deck</p>
          <h3>Native and reference backtests, side by side</h3>
        </div>
        <p className="comparison-baseline">
          Baseline: {comparison.baseline_run_id} / Intent: {formatComparisonIntentLabel(comparison.intent)}
        </p>
      </div>
      <div className="comparison-run-grid">
        {comparison.runs.map((run) => (
          <article
            className={`comparison-run-card ${
              run.run_id === comparison.baseline_run_id ? "baseline" : ""
            }`}
            key={run.run_id}
          >
            <div className="comparison-run-head">
              <strong>{run.strategy_name ?? run.strategy_id}</strong>
              <div className={`run-status ${run.status}`}>{run.status}</div>
            </div>
            <div className="strategy-badges">
              <span className="meta-pill">{run.lane}</span>
              <span className="meta-pill subtle">{run.strategy_version}</span>
              {run.reference_id ? (
                <span className="meta-pill subtle">{run.reference_id}</span>
              ) : null}
            </div>
            <p className="run-note">
              {run.strategy_id} / {run.symbols.join(", ")} / {run.timeframe}
            </p>
            <p className="run-note">
              Started {formatTimestamp(run.started_at)}
              {run.ended_at ? ` / Ended ${formatTimestamp(run.ended_at)}` : ""}
            </p>
            {run.reference ? (
              <ReferenceRunProvenanceSummary
                artifactPaths={run.artifact_paths}
                benchmarkArtifacts={run.benchmark_artifacts}
                externalCommand={run.external_command}
                reference={run.reference}
                referenceVersion={run.reference_version}
                workingDirectory={run.working_directory}
              />
            ) : null}
          </article>
        ))}
      </div>
      {primaryNarrative ? (
        <div className="comparison-top-story">
          <p className="kicker">Top insight / {formatComparisonIntentLabel(comparison.intent)}</p>
          <ComparisonNarrativeCard comparison={comparison} featured narrative={primaryNarrative} />
        </div>
      ) : null}
      {secondaryNarratives.length ? (
        <div className="comparison-story-grid">
          {secondaryNarratives.map((narrative) => (
            <ComparisonNarrativeCard comparison={comparison} key={`${narrative.baseline_run_id}-${narrative.run_id}`} narrative={narrative} />
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
            {comparison.metric_rows.map((metricRow) => (
              <tr key={metricRow.key}>
                <th>{metricRow.label}</th>
                {comparison.runs.map((run) => (
                  <td
                    className={metricRow.best_run_id === run.run_id ? "comparison-best" : undefined}
                    key={`${metricRow.key}-${run.run_id}`}
                  >
                    <strong>
                      {formatComparisonMetric(metricRow.values[run.run_id], metricRow.unit)}
                    </strong>
                    <span className="comparison-delta">
                      {run.run_id === comparison.baseline_run_id
                        ? "baseline"
                        : formatComparisonDelta(
                            metricRow.deltas_vs_baseline[run.run_id],
                            metricRow.unit,
                          )}
                    </span>
                  </td>
                ))}
              </tr>
            ))}
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
  comparison,
  narrative,
  featured = false,
}: {
  comparison: RunComparison;
  narrative: RunComparison["narratives"][number];
  featured?: boolean;
}) {
  const run = comparison.runs.find((candidate) => candidate.run_id === narrative.run_id);
  const runLabel = run?.reference?.title ?? run?.strategy_name ?? run?.strategy_id ?? narrative.run_id;

  return (
    <article className={`comparison-story-card ${featured ? "featured" : ""}`}>
      <div className="comparison-story-head">
        <span>{formatComparisonNarrativeLabel(narrative.comparison_type)}</span>
        <strong>{runLabel}</strong>
      </div>
      <div className="comparison-story-meta">
        <span>#{narrative.rank}</span>
        <span>Score {narrative.insight_score}</span>
      </div>
      <p className="comparison-story-title">{narrative.title}</p>
      <p className="comparison-story-summary">{narrative.summary}</p>
      {narrative.bullets.length ? (
        <ul className="comparison-story-list">
          {narrative.bullets.map((bullet) => (
            <li key={`${narrative.run_id}-${bullet}`}>{bullet}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

function ReferenceRunProvenanceSummary({
  artifactPaths,
  benchmarkArtifacts,
  externalCommand,
  reference,
  referenceVersion,
  workingDirectory,
}: {
  artifactPaths: string[];
  benchmarkArtifacts: BenchmarkArtifact[];
  externalCommand: string[];
  reference: ReferenceSource;
  referenceVersion?: string | null;
  workingDirectory?: string | null;
}) {
  return (
    <section className="reference-provenance">
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
        <p>ID: {reference.reference_id}</p>
        {reference.homepage ? <p>Homepage: {reference.homepage}</p> : null}
        {workingDirectory ? <p>Working dir: {workingDirectory}</p> : null}
        {externalCommand.length ? <p>Command: {externalCommand.join(" ")}</p> : null}
        {benchmarkArtifacts.length ? (
          <div className="reference-artifact-list">
            {benchmarkArtifacts.map((artifact) => {
              const summaryEntries = formatBenchmarkArtifactSummaryEntries(artifact.summary);
              const sectionEntries = formatBenchmarkArtifactSectionEntries(artifact.sections ?? {});
              return (
                <article className="reference-artifact-card" key={`${artifact.kind}-${artifact.path}`}>
                  <div className="reference-artifact-head">
                    <strong>{artifact.label}</strong>
                    <span>{artifact.kind}</span>
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
                  {summaryEntries.length ? (
                    <dl className="reference-artifact-summary">
                      {summaryEntries.map(([key, value]) => (
                        <div className="reference-artifact-summary-row" key={`${artifact.path}-${key}`}>
                          <dt>{formatBenchmarkArtifactSummaryLabel(key)}</dt>
                          <dd>{value}</dd>
                        </div>
                      ))}
                    </dl>
                  ) : null}
                  {sectionEntries.length ? (
                    <div className="reference-artifact-sections">
                      {sectionEntries.map(([key, lines]) => (
                        <article className="reference-artifact-section-card" key={`${artifact.path}-${key}`}>
                          <div className="reference-artifact-section-head">
                            <strong>{formatBenchmarkArtifactSectionLabel(key)}</strong>
                          </div>
                          <div className="reference-artifact-section-body">
                            {lines.map((line) => (
                              <p key={`${artifact.path}-${key}-${line}`}>{line}</p>
                            ))}
                          </div>
                        </article>
                      ))}
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        ) : (
          <p>Artifacts: {artifactPaths.length ? artifactPaths.join(" | ") : "none recorded"}</p>
        )}
      </div>
    </section>
  );
}

function RunStrategySnapshot({
  strategy,
}: {
  strategy: NonNullable<Run["provenance"]["strategy"]>;
}) {
  return (
    <section className="run-strategy">
      <div className="run-strategy-head">
        <span>Strategy snapshot</span>
        <strong>{formatLaneLabel(strategy.runtime)}</strong>
      </div>
      <div className="run-strategy-grid">
        <Metric label="Version" value={strategy.version} />
        <Metric label="Lifecycle" value={strategy.lifecycle.stage} />
        <Metric label="Warmup" value={`${strategy.warmup.required_bars} bars`} />
        <Metric label="TFs" value={strategy.warmup.timeframes.join(", ")} />
      </div>
      <div className="run-strategy-copy">
        <p>Supported timeframes: {strategy.supported_timeframes.join(", ") || "n/a"}</p>
        <p>Version lineage: {formatVersionLineage(strategy.version_lineage, strategy.version)}</p>
        <p>Resolved params: {formatParameterMap(strategy.parameter_snapshot.resolved)}</p>
        <p>Requested params: {formatParameterMap(strategy.parameter_snapshot.requested)}</p>
        {strategy.entrypoint ? <p>Entrypoint: {strategy.entrypoint}</p> : null}
        {strategy.lifecycle.registered_at ? (
          <p>Registered: {formatTimestamp(strategy.lifecycle.registered_at)}</p>
        ) : null}
      </div>
    </section>
  );
}

function RunMarketDataLineage({
  lineage,
  lineageBySymbol,
}: {
  lineage: NonNullable<Run["provenance"]["market_data"]>;
  lineageBySymbol?: NonNullable<Run["provenance"]["market_data_by_symbol"]>;
}) {
  const symbolEntries = Object.entries(lineageBySymbol ?? {});

  return (
    <section className="run-lineage">
      <div className="run-lineage-head">
        <span>Data lineage</span>
        <strong>{lineage.provider}</strong>
      </div>
      <div className="run-lineage-grid">
        <Metric label="Provider" value={lineage.provider} />
        <Metric label="Sync" value={lineage.sync_status} />
        <Metric label="Candles" value={String(lineage.candle_count)} />
        <Metric label="Timeframe" value={lineage.timeframe} />
      </div>
      <div className="run-lineage-copy">
        <p>
          {lineage.venue}:{lineage.symbols.join(", ")}
        </p>
        <p>Requested window: {formatRange(lineage.requested_start_at, lineage.requested_end_at)}</p>
        <p>Effective window: {formatRange(lineage.effective_start_at, lineage.effective_end_at)}</p>
        <p>Last sync: {formatTimestamp(lineage.last_sync_at)}</p>
        <p>Issues: {lineage.issues.length ? lineage.issues.join(", ") : "none"}</p>
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
                <Metric label="Candles" value={String(symbolLineage.candle_count)} />
                <Metric label="Provider" value={symbolLineage.provider} />
                <Metric label="Window" value={formatRange(symbolLineage.effective_start_at, symbolLineage.effective_end_at)} />
              </div>
              <p className="run-lineage-symbol-copy">Last sync: {formatTimestamp(symbolLineage.last_sync_at)}</p>
              <p className="run-lineage-symbol-copy">
                Issues: {symbolLineage.issues.length ? symbolLineage.issues.join(", ") : "none"}
              </p>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-tile">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatMetric(value?: number, suffix = "") {
  if (value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
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
