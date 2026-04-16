import { FormEvent, useEffect, useMemo, useState } from "react";

type Strategy = {
  strategy_id: string;
  name: string;
  version: string;
  runtime: string;
  description: string;
  reference_id?: string | null;
  reference_path?: string | null;
  entrypoint?: string | null;
};

type ReferenceSource = {
  reference_id: string;
  title: string;
  license: string;
  integration_mode: string;
  runtime?: string | null;
  summary: string;
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
    external_command: string[];
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
    issues: string[];
  }[];
};

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

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

export default function App() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [references, setReferences] = useState<ReferenceSource[]>([]);
  const [backtests, setBacktests] = useState<Run[]>([]);
  const [sandboxRuns, setSandboxRuns] = useState<Run[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketDataStatus | null>(null);
  const [statusText, setStatusText] = useState("Loading control room...");
  const [backtestForm, setBacktestForm] = useState(defaultRunForm);
  const [sandboxForm, setSandboxForm] = useState(defaultRunForm);

  async function loadAll() {
    setStatusText("Refreshing data plane...");
    try {
      const [strategiesResponse, referencesResponse, backtestsResponse, sandboxResponse, marketResponse] = await Promise.all([
        fetchJson<Strategy[]>("/strategies"),
        fetchJson<ReferenceSource[]>("/references"),
        fetchJson<Run[]>("/runs?mode=backtest"),
        fetchJson<Run[]>("/runs?mode=sandbox"),
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
  }, []);

  useEffect(() => {
    if (!strategies.length) {
      return;
    }
    const preferredNative = strategies.find((strategy) => strategy.runtime === "native") ?? strategies[0];
    setBacktestForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
    setSandboxForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
  }, [strategies]);

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
                        <BackfillQualityStatus instrument={instrument} />
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

        <RunSection title="Recent backtests" runs={backtests} />
        <RunSection title="Sandbox runs" runs={sandboxRuns} onStop={stopSandboxRun} />
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
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  if (instrument.backfill_contiguous_completion_ratio === null) {
    return <span>n/a</span>;
  }
  return (
    <div className="progress-stack">
      <strong>{formatCompletion(instrument.backfill_contiguous_completion_ratio)}</strong>
      <span>
        {instrument.backfill_contiguous_complete
          ? "gap-free"
          : `gaps: ${instrument.backfill_contiguous_missing_candles ?? 0}`}
      </span>
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
              <strong>{strategy.name}</strong>
              <span>{strategy.version}</span>
            </div>
            <p>{strategy.description}</p>
            <dl>
              <div>
                <dt>ID</dt>
                <dd>{strategy.strategy_id}</dd>
              </div>
              <div>
                <dt>Runtime</dt>
                <dd>{strategy.runtime}</dd>
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

function RunSection({
  title,
  runs,
  onStop,
}: {
  title: string;
  runs: Run[];
  onStop?: (runId: string) => Promise<void>;
}) {
  return (
    <section className="panel panel-wide">
      <p className="kicker">Execution plane</p>
      <h2>{title}</h2>
      {runs.length ? (
        <div className="run-list">
          {runs.map((run) => (
            <article className="run-card" key={run.config.run_id}>
              <div className="run-card-head">
                <div>
                  <strong>{run.config.strategy_id}</strong>
                  <span>{run.config.symbols.join(", ")}</span>
                </div>
                <div className={`run-status ${run.status}`}>{run.status}</div>
              </div>
              <div className="run-metrics">
                <Metric label="Mode" value={run.config.mode} />
                <Metric label="Lane" value={run.provenance.lane} />
                <Metric label="Return" value={formatMetric(run.metrics.total_return_pct, "%")} />
                <Metric label="Drawdown" value={formatMetric(run.metrics.max_drawdown_pct, "%")} />
                <Metric label="Win rate" value={formatMetric(run.metrics.win_rate_pct, "%")} />
                <Metric label="Trades" value={formatMetric(run.metrics.trade_count)} />
              </div>
              <p className="run-note">
                {run.provenance.reference_id
                  ? `Reference ${run.provenance.reference_id} (${run.provenance.reference_version ?? "unknown"})`
                  : run.notes[0] ?? "No notes recorded."}
              </p>
              {run.provenance.external_command.length ? (
                <p className="run-note">{run.provenance.external_command.join(" ")}</p>
              ) : null}
              {run.provenance.market_data ? (
                <RunMarketDataLineage
                  lineage={run.provenance.market_data}
                  lineageBySymbol={run.provenance.market_data_by_symbol}
                />
              ) : null}
              {onStop && run.status === "running" ? (
                <button className="ghost-button" onClick={() => void onStop(run.config.run_id)}>
                  Stop
                </button>
              ) : null}
            </article>
          ))}
        </div>
      ) : (
        <p className="empty-state">No runs yet.</p>
      )}
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
