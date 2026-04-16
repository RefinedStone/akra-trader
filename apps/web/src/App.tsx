import { FormEvent, useEffect, useMemo, useState } from "react";

type Strategy = {
  strategy_id: string;
  name: string;
  version: string;
  runtime: string;
  description: string;
  reference_path?: string | null;
  entrypoint?: string | null;
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
  const [backtests, setBacktests] = useState<Run[]>([]);
  const [paperRuns, setPaperRuns] = useState<Run[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketDataStatus | null>(null);
  const [statusText, setStatusText] = useState("Loading control room...");
  const [backtestForm, setBacktestForm] = useState(defaultRunForm);
  const [paperForm, setPaperForm] = useState(defaultRunForm);

  async function loadAll() {
    setStatusText("Refreshing data plane...");
    try {
      const [strategiesResponse, backtestsResponse, paperResponse, marketResponse] = await Promise.all([
        fetchJson<Strategy[]>("/strategies"),
        fetchJson<Run[]>("/runs?mode=backtest"),
        fetchJson<Run[]>("/runs?mode=paper"),
        fetchJson<MarketDataStatus>("/market-data/status"),
      ]);
      setStrategies(strategiesResponse);
      setBacktests(backtestsResponse);
      setPaperRuns(paperResponse);
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
    setPaperForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
  }, [strategies]);

  const strategyGroups = useMemo(() => {
    return {
      native: strategies.filter((strategy) => strategy.runtime === "native"),
      reference: strategies.filter((strategy) => strategy.runtime === "freqtrade_reference"),
      future: strategies.filter((strategy) => strategy.runtime === "decision_engine"),
    };
  }, [strategies]);

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

  async function handlePaperSubmit(event: FormEvent) {
    event.preventDefault();
    setStatusText("Starting paper run...");
    try {
      await fetchJson<Run>("/runs/paper", {
        method: "POST",
        body: JSON.stringify({ ...paperForm, parameters: {}, replay_bars: 96 }),
      });
      await loadAll();
    } catch (error) {
      setStatusText(`Paper run failed: ${(error as Error).message}`);
    }
  }

  async function stopPaperRun(runId: string) {
    setStatusText(`Stopping run ${runId}...`);
    try {
      await fetchJson<Run>(`/runs/paper/${runId}/stop`, { method: "POST" });
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
          <p className="kicker">Paper</p>
          <h2>Start native replay</h2>
          <RunForm form={paperForm} setForm={setPaperForm} strategies={strategies.filter((strategy) => strategy.runtime === "native")} onSubmit={handlePaperSubmit} />
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
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Instrument</th>
                    <th>Timeframe</th>
                    <th>Candles</th>
                    <th>Latest</th>
                  </tr>
                </thead>
                <tbody>
                  {marketStatus.instruments.map((instrument) => (
                    <tr key={instrument.instrument_id}>
                      <td>{instrument.instrument_id}</td>
                      <td>{instrument.timeframe}</td>
                      <td>{instrument.candle_count}</td>
                      <td>{instrument.last_timestamp ?? "n/a"}</td>
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
        <RunSection title="Paper runs" runs={paperRuns} onStop={stopPaperRun} />
      </main>
    </div>
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
            </dl>
          </article>
        ))
      ) : (
        <p className="empty-state">No strategies registered.</p>
      )}
    </div>
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
                <Metric label="Return" value={formatMetric(run.metrics.total_return_pct, "%")} />
                <Metric label="Drawdown" value={formatMetric(run.metrics.max_drawdown_pct, "%")} />
                <Metric label="Win rate" value={formatMetric(run.metrics.win_rate_pct, "%")} />
                <Metric label="Trades" value={formatMetric(run.metrics.trade_count)} />
              </div>
              <p className="run-note">{run.notes[0] ?? "No notes recorded."}</p>
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
