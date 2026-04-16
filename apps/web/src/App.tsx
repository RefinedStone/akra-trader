import {
  CSSProperties,
  FormEvent,
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
    delta_annotations: Record<string, string>;
    annotation?: string | null;
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
const COMPARISON_TOOLTIP_TUNING_STORAGE_KEY = "akra-trader-comparison-tooltip-tuning";
const COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION = 1;
const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY = "akra-trader-comparison-tooltip-conflict-ui";
const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION = 1;
const COMPARISON_TOOLTIP_TUNING_SHARE_PARAM = "comparisonTooltipTuning";
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
type ComparisonCueKind = "mode" | "baseline" | "best" | "insight";
type ComparisonTooltipTargetProps = {
  "aria-describedby"?: string;
  "data-tooltip-visible": "true" | "false";
  onBlur: () => void;
  onFocus: () => void;
  onKeyDown: (event: KeyboardEvent<HTMLElement>) => void;
  onMouseEnter: (event: MouseEvent<HTMLElement>) => void;
  onMouseLeave: (event: MouseEvent<HTMLElement>) => void;
  onMouseMove?: (event: MouseEvent<HTMLElement>) => void;
};
type ComparisonTooltipInteractionOptions = {
  hoverCloseDelayMs?: number;
  hoverOpenDelayMs?: number;
};
type ComparisonTooltipTuning = {
  column_down_sweep_close_ms: number;
  column_down_sweep_hold_ms: number;
  column_down_sweep_open_ms: number;
  column_up_sweep_close_ms: number;
  column_up_sweep_hold_ms: number;
  column_up_sweep_open_ms: number;
  horizontal_distance_ratio: number;
  horizontal_velocity_threshold: number;
  metric_hover_close_ms: number;
  metric_hover_open_ms: number;
  row_sweep_close_ms: number;
  row_sweep_hold_ms: number;
  row_sweep_open_ms: number;
  speed_adjustment_base: number;
  speed_adjustment_max: number;
  speed_adjustment_min: number;
  speed_adjustment_slope: number;
  sweep_time_max_ms: number;
  sweep_time_min_ms: number;
  sweep_time_speed_multiplier: number;
  vertical_distance_ratio: number;
  vertical_velocity_threshold: number;
};
type ComparisonTooltipTuningPresetStateV1 = {
  current_tuning: ComparisonTooltipTuning;
  presets: Record<string, ComparisonTooltipTuning>;
  selected_preset_name?: string | null;
  version: typeof COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION;
};
type ComparisonTooltipTuningSinglePresetShareV1 = {
  preset_name: string;
  tuning: ComparisonTooltipTuning;
  version: typeof COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION;
};
type ComparisonTooltipPresetImportConflictPolicy = "overwrite" | "rename";
type ComparisonTooltipPresetImportResolution = {
  conflicted: boolean;
  final_preset_name: string;
  imported_preset_name: string;
  policy: ComparisonTooltipPresetImportConflictPolicy;
  renamed: boolean;
  overwritten: boolean;
};
type ComparisonTooltipPendingPresetImportConflict = {
  imported_preset_name: string;
  proposed_preset_name: string;
  raw: string;
  tuning: ComparisonTooltipTuning;
};
type ComparisonTooltipPresetConflictPreviewRow = {
  changed: boolean;
  delta_direction: "higher" | "lower" | "same";
  delta_label: string;
  existing_value: number;
  group_key: string;
  group_label: string;
  group_order: number;
  incoming_value: number;
  key: keyof ComparisonTooltipTuning;
  label: string;
};
type ComparisonTooltipPresetConflictPreviewGroup = {
  changed_count: number;
  higher_count: number;
  key: string;
  label: string;
  lower_count: number;
  rows: ComparisonTooltipPresetConflictPreviewRow[];
  same_count: number;
  summary_label: string;
};
type ComparisonTooltipConflictSessionUiState = {
  collapsed_unchanged_groups: Record<string, boolean>;
  show_unchanged_conflict_rows: boolean;
};
type ComparisonTooltipConflictUiStateV1 = {
  sessions: Record<string, ComparisonTooltipConflictSessionUiState>;
  version: typeof COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION;
};
type ComparisonTooltipTuningShareImport =
  | {
      kind: "bundle";
      raw: string;
      state: ComparisonTooltipTuningPresetStateV1;
    }
  | {
      kind: "preset";
      preset_name: string;
      raw: string;
      tuning: ComparisonTooltipTuning;
    };
type ComparisonTooltipLayout = {
  tooltipId: string;
  left: number;
  top: number;
  maxWidth: number;
  arrowLeft: number;
  side: "top" | "bottom";
};

const DEFAULT_COMPARISON_TOOLTIP_TUNING: ComparisonTooltipTuning = {
  column_down_sweep_close_ms: 80,
  column_down_sweep_hold_ms: 140,
  column_down_sweep_open_ms: 170,
  column_up_sweep_close_ms: 95,
  column_up_sweep_hold_ms: 180,
  column_up_sweep_open_ms: 260,
  horizontal_distance_ratio: 0.32,
  horizontal_velocity_threshold: 0.42,
  metric_hover_close_ms: 70,
  metric_hover_open_ms: 110,
  row_sweep_close_ms: 90,
  row_sweep_hold_ms: 180,
  row_sweep_open_ms: 250,
  speed_adjustment_base: 1.18,
  speed_adjustment_max: 1.12,
  speed_adjustment_min: 0.72,
  speed_adjustment_slope: 0.28,
  sweep_time_max_ms: 126,
  sweep_time_min_ms: 72,
  sweep_time_speed_multiplier: 42,
  vertical_distance_ratio: 0.42,
  vertical_velocity_threshold: 0.34,
};
const SHOW_COMPARISON_TOOLTIP_TUNING_PANEL = import.meta.env.DEV;
const DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY: ComparisonTooltipPresetImportConflictPolicy =
  "rename";
const COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD = 3;
const COMPARISON_TOOLTIP_TUNING_LABELS: Record<keyof ComparisonTooltipTuning, string> = {
  column_down_sweep_close_ms: "Col down close",
  column_down_sweep_hold_ms: "Col down hold",
  column_down_sweep_open_ms: "Col down open",
  column_up_sweep_close_ms: "Col up close",
  column_up_sweep_hold_ms: "Col up hold",
  column_up_sweep_open_ms: "Col up open",
  horizontal_distance_ratio: "Horiz ratio",
  horizontal_velocity_threshold: "Horiz velocity",
  metric_hover_close_ms: "Metric close",
  metric_hover_open_ms: "Metric open",
  row_sweep_close_ms: "Row close",
  row_sweep_hold_ms: "Row hold",
  row_sweep_open_ms: "Row open",
  speed_adjustment_base: "Speed base",
  speed_adjustment_max: "Speed max",
  speed_adjustment_min: "Speed min",
  speed_adjustment_slope: "Speed slope",
  sweep_time_max_ms: "Time max",
  sweep_time_min_ms: "Time min",
  sweep_time_speed_multiplier: "Time speed",
  vertical_distance_ratio: "Vert ratio",
  vertical_velocity_threshold: "Vert velocity",
};
const COMPARISON_TOOLTIP_TUNING_GROUPS: Record<
  keyof ComparisonTooltipTuning,
  { key: string; label: string; order: number }
> = {
  column_down_sweep_close_ms: {
    key: "column-down-sweep",
    label: "Column Down Sweep",
    order: 4,
  },
  column_down_sweep_hold_ms: {
    key: "column-down-sweep",
    label: "Column Down Sweep",
    order: 4,
  },
  column_down_sweep_open_ms: {
    key: "column-down-sweep",
    label: "Column Down Sweep",
    order: 4,
  },
  column_up_sweep_close_ms: {
    key: "column-up-sweep",
    label: "Column Up Sweep",
    order: 5,
  },
  column_up_sweep_hold_ms: {
    key: "column-up-sweep",
    label: "Column Up Sweep",
    order: 5,
  },
  column_up_sweep_open_ms: {
    key: "column-up-sweep",
    label: "Column Up Sweep",
    order: 5,
  },
  horizontal_distance_ratio: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  horizontal_velocity_threshold: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  metric_hover_close_ms: {
    key: "hover-timing",
    label: "Hover Timing",
    order: 0,
  },
  metric_hover_open_ms: {
    key: "hover-timing",
    label: "Hover Timing",
    order: 0,
  },
  row_sweep_close_ms: {
    key: "row-sweep",
    label: "Row Sweep",
    order: 3,
  },
  row_sweep_hold_ms: {
    key: "row-sweep",
    label: "Row Sweep",
    order: 3,
  },
  row_sweep_open_ms: {
    key: "row-sweep",
    label: "Row Sweep",
    order: 3,
  },
  speed_adjustment_base: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  speed_adjustment_max: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  speed_adjustment_min: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  speed_adjustment_slope: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  sweep_time_max_ms: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  sweep_time_min_ms: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  sweep_time_speed_multiplier: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  vertical_distance_ratio: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  vertical_velocity_threshold: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
};

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
  const tooltipScopeId = sanitizeComparisonTooltipId(useId());
  const tooltipTargetRefs = useRef(new Map<string, HTMLElement>());
  const tooltipBubbleRefs = useRef(new Map<string, HTMLSpanElement>());
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

  const showComparisonTooltip = (tooltipId: string) => {
    setDismissedTooltipId((current) => (current === tooltipId ? null : current));
    setActiveTooltipId(tooltipId);
  };

  const hideComparisonTooltip = (tooltipId: string) => {
    setActiveTooltipId((current) => (current === tooltipId ? null : current));
    setDismissedTooltipId((current) => (current === tooltipId ? null : current));
  };

  const dismissComparisonTooltip = (tooltipId: string) => {
    setActiveTooltipId((current) => (current === tooltipId ? null : current));
    setActiveTooltipLayout((current) => (current?.tooltipId === tooltipId ? null : current));
    setDismissedTooltipId(tooltipId);
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

  const registerComparisonTooltipTargetRef = (tooltipId?: string) => (node: HTMLElement | null) => {
    if (!tooltipId) {
      return;
    }
    if (node) {
      tooltipTargetRefs.current.set(tooltipId, node);
      return;
    }
    tooltipTargetRefs.current.delete(tooltipId);
  };

  const registerComparisonTooltipBubbleRef =
    (tooltipId: string) => (node: HTMLSpanElement | null) => {
      if (node) {
        tooltipBubbleRefs.current.set(tooltipId, node);
        return;
      }
      tooltipBubbleRefs.current.delete(tooltipId);
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
        {comparison.runs.map((run) => (
          <article
            className={`comparison-run-card ${
              run.run_id === comparison.baseline_run_id
                ? "baseline comparison-cue-card comparison-tooltip"
                : ""
            }`}
            key={run.run_id}
            ref={
              run.run_id === comparison.baseline_run_id
                ? registerComparisonTooltipTargetRef(baselineRunTooltipId)
                : undefined
            }
            tabIndex={run.run_id === comparison.baseline_run_id ? 0 : undefined}
            {...(run.run_id === comparison.baseline_run_id
              ? getComparisonTooltipTargetProps(baselineRunTooltipId)
              : {})}
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
        ))}
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
            featured
            narrative={primaryNarrative}
            registerTooltipBubbleRef={registerComparisonTooltipBubbleRef}
            registerTooltipTargetRef={registerComparisonTooltipTargetRef}
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
              key={`${narrative.baseline_run_id}-${narrative.run_id}`}
              narrative={narrative}
              registerTooltipBubbleRef={registerComparisonTooltipBubbleRef}
              registerTooltipTargetRef={registerComparisonTooltipTargetRef}
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
            {comparison.metric_rows.map((metricRow) => (
              <tr key={metricRow.key}>
                <th>
                  <span>{metricRow.label}</span>
                  {metricRow.annotation ? (
                    <small className="comparison-metric-annotation">{metricRow.annotation}</small>
                  ) : null}
                </th>
                {comparison.runs.map((run) => {
                  const cellTooltip =
                    buildComparisonCellTooltip(
                      comparison.intent,
                      metricRow.label,
                      run.run_id === comparison.baseline_run_id,
                      metricRow.best_run_id === run.run_id,
                    ) || undefined;
                  const cellTooltipId = cellTooltip
                    ? buildComparisonTooltipId(tooltipScopeId, "metric", metricRow.key, run.run_id)
                    : undefined;
                  const cellClassName =
                    [
                      metricRow.best_run_id === run.run_id ? "comparison-best" : "",
                      run.run_id === comparison.baseline_run_id ? "comparison-baseline-cell" : "",
                      cellTooltip ? "comparison-cue comparison-tooltip comparison-cell-cue" : "",
                    ]
                      .filter(Boolean)
                      .join(" ") || undefined;

                  return (
                    <td
                      className={cellClassName}
                      key={`${metricRow.key}-${run.run_id}`}
                      ref={
                        cellTooltipId
                          ? registerComparisonTooltipTargetRef(cellTooltipId)
                          : undefined
                      }
                      tabIndex={cellTooltip ? 0 : undefined}
                      {...(cellTooltipId
                        ? getMetricComparisonTooltipTargetProps(
                            cellTooltipId,
                            metricRow.key,
                            run.run_id,
                          )
                        : {})}
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
  activeTooltipLayout,
  comparison,
  narrative,
  featured = false,
  registerTooltipBubbleRef,
  registerTooltipTargetRef,
  tooltipId,
  tooltipTargetProps,
  tooltip,
}: {
  activeTooltipLayout: ComparisonTooltipLayout | null;
  comparison: RunComparison;
  narrative: RunComparison["narratives"][number];
  featured?: boolean;
  registerTooltipBubbleRef: (tooltipId: string) => (node: HTMLSpanElement | null) => void;
  registerTooltipTargetRef: (tooltipId?: string) => (node: HTMLElement | null) => void;
  tooltipId?: string;
  tooltipTargetProps?: ComparisonTooltipTargetProps;
  tooltip?: string;
}) {
  const run = comparison.runs.find((candidate) => candidate.run_id === narrative.run_id);
  const runLabel = run?.reference?.title ?? run?.strategy_name ?? run?.strategy_id ?? narrative.run_id;

  return (
    <article
      className={`comparison-story-card ${
        featured ? "featured comparison-cue-card comparison-tooltip" : ""
      }`}
      ref={tooltipId ? registerTooltipTargetRef(tooltipId) : undefined}
      tabIndex={tooltip ? 0 : undefined}
      {...tooltipTargetProps}
    >
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
      };
      return {
        ...current,
        [conflictSessionKey]: updater(nextCurrent),
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

function hashComparisonTooltipConflictSessionRaw(value: string) {
  let hash = 5381;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 33) ^ value.charCodeAt(index);
  }
  return (hash >>> 0).toString(36);
}

function formatComparisonTooltipTuningValue(value: number) {
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
