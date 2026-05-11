import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import type { CandlestickData, IChartApi, ISeriesApi, LineData, Time, UTCTimestamp } from "lightweight-charts";

type SectionId = "data" | "backtest" | "sandbox" | "live" | "logs" | "llm";
type DetailTabId = "overview" | "orders" | "positions" | "metrics" | "logs";

type RunConfigSummary = {
  symbols?: string[];
  timeframe?: string;
  initial_cash?: number;
  start_at?: string | null;
  end_at?: string | null;
  parameters?: Record<string, unknown>;
};

type RunMarketDataSummary = {
  provider?: string;
  venue?: string;
  timeframe?: string;
  requested_start_at?: string | null;
  requested_end_at?: string | null;
  effective_start_at?: string | null;
  effective_end_at?: string | null;
  candle_count?: number;
  sync_status?: string;
  issues?: string[];
};

type RunSummary = {
  run_id: string;
  mode: "backtest" | "sandbox" | "live";
  status: string;
  started_at: string;
  ended_at: string | null;
  config?: RunConfigSummary;
  strategy: { name?: string; strategy_id?: string } | null;
  market_data?: RunMarketDataSummary | null;
  metrics: Record<string, number | string>;
  orders_count: number;
  positions_count: number;
  notes: string[];
};

type OperationLog = {
  log_id: string;
  recorded_at: string;
  layer: string;
  event_type: string;
  message: string;
  severity: string;
  run_id?: string | null;
  mode?: string | null;
};

type Strategy = {
  strategy_id: string;
  name: string;
  runtime: string;
  lifecycle: { stage: string };
  supported_timeframes: string[];
  parameter_schema: Record<string, unknown>;
};

type MarketStatus = {
  provider: string;
  venue: string;
  instruments: Array<{
    instrument_id: string;
    timeframe: string;
    candle_count: number;
    sync_status?: string;
    first_timestamp?: string | null;
    last_timestamp?: string | null;
  }>;
};

type MarketDataSyncResult = {
  provider: string;
  venue: string;
  symbol: string;
  timeframe: string;
  status: string;
  requested_start_at?: string | null;
  requested_end_at?: string | null;
  requested_limit?: number | null;
  effective_start_at?: string | null;
  effective_end_at?: string | null;
  candle_count: number;
  issues: string[];
};

type HealthStatus = {
  status: string;
  market_data_provider: string;
  guarded_live: {
    venue: string;
    enabled: boolean;
  };
};

type Candle = {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

type RunFormState = {
  strategy_id: string;
  symbol: string;
  timeframe: string;
  initial_cash: string;
  fee_rate: string;
  slippage_bps: string;
  replay_bars: string;
  start_at: string;
  end_at: string;
  parameters: string;
};

type DataSyncFormState = {
  symbol: string;
  timeframe: string;
  start_at: string;
  end_at: string;
  limit: string;
};

const apiBase = "/api";

const sections: Array<{ id: SectionId; label: string; eyebrow: string; mark: string; path: string }> = [
  { id: "data", label: "데이터", eyebrow: "수집 현황", mark: "D", path: "/data" },
  { id: "backtest", label: "백테스트", eyebrow: "과거 검증", mark: "B", path: "/backtest" },
  { id: "sandbox", label: "샌드박스", eyebrow: "모의 테스트", mark: "S", path: "/sandbox" },
  { id: "live", label: "실전 매매", eyebrow: "가드드 라이브", mark: "L", path: "/live" },
  { id: "logs", label: "로그", eyebrow: "운영 기록", mark: "O", path: "/logs" },
  { id: "llm", label: "LLM 전략", eyebrow: "격리 계층", mark: "A", path: "/llm-strategy" },
];

const detailTabs: Array<{ id: DetailTabId; label: string }> = [
  { id: "overview", label: "결과" },
  { id: "orders", label: "주문" },
  { id: "positions", label: "포지션" },
  { id: "metrics", label: "지표" },
  { id: "logs", label: "로그" },
];

const movingAverageLines = [
  { period: 5, label: "MA5", color: "#4d8dff", width: 1 },
  { period: 20, label: "MA20 황금선", color: "#f0c43c", width: 2 },
  { period: 60, label: "MA60", color: "#31d17d", width: 1 },
] as const;

const defaultRunForm: RunFormState = {
  strategy_id: "ma_cross_v1",
  symbol: "BTC/USDT",
  timeframe: "5m",
  initial_cash: "10000",
  fee_rate: "0.001",
  slippage_bps: "5",
  replay_bars: "96",
  start_at: "",
  end_at: "",
  parameters: '{\n  "short_window": 8,\n  "long_window": 21\n}',
};

const defaultDataSyncForm: DataSyncFormState = {
  symbol: "BTC/USDT",
  timeframe: "5m",
  start_at: "",
  end_at: "",
  limit: "2000",
};

function sectionFromPath(pathname: string): SectionId {
  const match = sections.find((section) => section.path === pathname);
  return match?.id ?? "data";
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `요청 실패: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export default function App() {
  const [activeSection, setActiveSection] = useState<SectionId>(() =>
    typeof window === "undefined" ? "data" : sectionFromPath(window.location.pathname),
  );
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [llmStrategy, setLlmStrategy] = useState<Record<string, unknown> | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [selectedRun, setSelectedRun] = useState<RunSummary | null>(null);
  const [orders, setOrders] = useState<unknown[]>([]);
  const [positions, setPositions] = useState<unknown[]>([]);
  const [logs, setLogs] = useState<OperationLog[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [form, setForm] = useState<RunFormState>(defaultRunForm);
  const [dataQuery, setDataQuery] = useState({ symbol: "BTC/USDT", timeframe: "5m", limit: "80" });
  const [dataSyncForm, setDataSyncForm] = useState<DataSyncFormState>(defaultDataSyncForm);
  const [dataSyncResult, setDataSyncResult] = useState<MarketDataSyncResult | null>(null);
  const [logFilter, setLogFilter] = useState({ mode: "", severity: "" });
  const [statusText, setStatusText] = useState("불러오는 중");
  const [error, setError] = useState<string | null>(null);

  const runCounts = useMemo(
    () => ({
      backtest: runs.filter((run) => run.mode === "backtest").length,
      sandbox: runs.filter((run) => run.mode === "sandbox").length,
      live: runs.filter((run) => run.mode === "live").length,
      running: runs.filter((run) => run.status === "running").length,
    }),
    [runs],
  );

  const activeRuns = useMemo(() => {
    if (activeSection === "backtest") {
      return runs.filter((run) => run.mode === "backtest");
    }
    if (activeSection === "sandbox") {
      return runs.filter((run) => run.mode === "sandbox");
    }
    if (activeSection === "live") {
      return runs.filter((run) => run.mode === "live");
    }
    return runs;
  }, [activeSection, runs]);

  const logSummary = useMemo(
    () => ({
      error: logs.filter((log) => log.severity === "error").length,
      warning: logs.filter((log) => log.severity === "warning").length,
      info: logs.filter((log) => log.severity === "info").length,
    }),
    [logs],
  );

  const symbolOptions = useMemo(
    () =>
      uniqueOptions([
        ...(marketStatus?.instruments.map((instrument) => toSymbol(instrument.instrument_id)) ?? []),
        dataQuery.symbol,
        dataSyncForm.symbol,
        form.symbol,
      ]),
    [dataQuery.symbol, dataSyncForm.symbol, form.symbol, marketStatus],
  );

  const timeframeOptions = useMemo(
    () =>
      uniqueOptions([
        ...(marketStatus?.instruments.map((instrument) => instrument.timeframe) ?? []),
        dataQuery.timeframe,
        dataSyncForm.timeframe,
        form.timeframe,
      ]),
    [dataQuery.timeframe, dataSyncForm.timeframe, form.timeframe, marketStatus],
  );

  const refresh = async () => {
    setError(null);
    try {
      const [healthResponse, strategyResponse, runResponse, statusResponse, logResponse] = await Promise.all([
        fetchJson<HealthStatus>("/health"),
        fetchJson<{ strategies: Strategy[]; llm_strategy: Record<string, unknown> }>("/strategies"),
        fetchJson<{ runs: RunSummary[] }>("/runs"),
        fetchJson<MarketStatus>("/market-data/status?timeframe=5m"),
        fetchJson<{ logs: OperationLog[] }>("/logs?limit=100"),
      ]);
      setHealth(healthResponse);
      setStrategies(strategyResponse.strategies);
      setLlmStrategy(strategyResponse.llm_strategy);
      setRuns(runResponse.runs);
      setMarketStatus(statusResponse);
      setLogs(logResponse.logs);
      setStatusText("준비됨");
      if (!selectedRunId && runResponse.runs.length > 0) {
        setSelectedRunId(runResponse.runs[0].run_id);
      }
    } catch (caught) {
      setStatusText("오류");
      setError(caught instanceof Error ? caught.message : "요청에 실패했습니다.");
    }
  };

  useEffect(() => {
    void refresh();
    void loadCandles();
    const onPopState = () => setActiveSection(sectionFromPath(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    if (!selectedRunId) {
      setSelectedRun(null);
      setOrders([]);
      setPositions([]);
      return;
    }
    void loadRunDetail(selectedRunId);
  }, [selectedRunId]);

  const navigate = (section: SectionId) => {
    setActiveSection(section);
    const next = sections.find((item) => item.id === section);
    if (next && typeof window !== "undefined" && window.location.pathname !== next.path) {
      window.history.pushState(window.history.state, "", next.path);
    }
  };

  const submitRun = async (mode: "backtests" | "sandbox" | "live") => {
    setError(null);
    let parameters: Record<string, unknown>;
    try {
      parameters = JSON.parse(form.parameters);
    } catch {
      setError("전략 파라미터는 올바른 JSON이어야 합니다.");
      return;
    }
    const payload = {
      strategy_id: form.strategy_id,
      symbol: form.symbol,
      timeframe: form.timeframe,
      initial_cash: Number(form.initial_cash),
      fee_rate: Number(form.fee_rate),
      slippage_bps: Number(form.slippage_bps),
      replay_bars: Number(form.replay_bars),
      start_at: toApiDateTime(form.start_at),
      end_at: toApiDateTime(form.end_at),
      parameters,
    };
    try {
      const run = await fetchJson<RunSummary>(`/runs/${mode}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setSelectedRunId(run.run_id);
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "실행 요청에 실패했습니다.");
    }
  };

  const stopSelectedRun = async () => {
    if (!selectedRunId) {
      return;
    }
    try {
      await fetchJson<RunSummary>(`/runs/${selectedRunId}/stop`, { method: "POST" });
      await refresh();
      await loadRunDetail(selectedRunId);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "중지 요청에 실패했습니다.");
    }
  };

  const loadRunDetail = async (runId: string) => {
    const [run, orderResponse, positionResponse] = await Promise.all([
      fetchJson<RunSummary>(`/runs/${runId}`),
      fetchJson<{ orders: unknown[] }>(`/runs/${runId}/orders`),
      fetchJson<{ positions: unknown[] }>(`/runs/${runId}/positions`),
    ]);
    setSelectedRun(run);
    setOrders(orderResponse.orders);
    setPositions(positionResponse.positions);
  };

  const loadCandles = async (queryState = dataQuery) => {
    const query = new URLSearchParams({
      symbol: queryState.symbol,
      timeframe: queryState.timeframe,
      limit: queryState.limit,
    });
    const response = await fetchJson<{ candles: Candle[] }>(`/market-data/candles?${query}`);
    setCandles(response.candles);
  };

  const syncMarketData = async () => {
    setError(null);
    const payload = {
      symbol: dataSyncForm.symbol,
      timeframe: dataSyncForm.timeframe,
      start_at: toApiDateTime(dataSyncForm.start_at),
      end_at: toApiDateTime(dataSyncForm.end_at),
      limit: dataSyncForm.limit ? Number(dataSyncForm.limit) : null,
    };
    try {
      const result = await fetchJson<MarketDataSyncResult>("/market-data/sync", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setDataSyncResult(result);
      setDataQuery({
        symbol: result.symbol,
        timeframe: result.timeframe,
        limit: dataQuery.limit,
      });
      await refresh();
      await loadCandles({ symbol: result.symbol, timeframe: result.timeframe, limit: dataQuery.limit });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "데이터 적재 요청에 실패했습니다.");
    }
  };

  const loadLogs = async () => {
    const query = new URLSearchParams({ limit: "200" });
    if (logFilter.mode) {
      query.set("mode", logFilter.mode);
    }
    if (logFilter.severity) {
      query.set("severity", logFilter.severity);
    }
    const response = await fetchJson<{ logs: OperationLog[] }>(`/logs?${query}`);
    setLogs(response.logs);
  };

  return (
    <div className="core-shell">
      <aside className="core-sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">A</div>
          <div>
            <strong>Akra Trader</strong>
            <span>운영 콘솔</span>
          </div>
        </div>
        <nav className="core-nav" aria-label="core runtime sections">
          {sections.map((section) => (
            <button
              aria-pressed={activeSection === section.id}
              className={activeSection === section.id ? "is-active" : ""}
              key={section.id}
              onClick={() => navigate(section.id)}
              type="button"
            >
              <span className="nav-mark" aria-hidden="true">{section.mark}</span>
              <span className="nav-copy">
                <small>{section.eyebrow}</small>
                <strong>{section.label}</strong>
              </span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span>환경</span>
          <strong>프로덕션</strong>
        </div>
        <div className="operator-card">
          <div className="operator-avatar">A</div>
          <div>
            <strong>akra-admin</strong>
            <span>관리자</span>
          </div>
        </div>
      </aside>

      <div className="core-workspace">
        <header className="core-header">
          <StatusTile label="서비스 상태" value={formatHealthStatus(health?.status ?? statusText)} tone="success" detail="/api/health" />
          <StatusTile label="데이터 제공자" value={marketStatus?.provider ?? health?.market_data_provider ?? "-"} detail={marketStatus?.venue ?? "binance"} />
          <StatusTile
            label="가드드 라이브"
            value={health?.guarded_live.enabled ? "사용 중" : "비활성"}
            tone={health?.guarded_live.enabled ? "success" : "warning"}
            detail={health?.guarded_live.venue ?? "binance"}
          />
          <StatusTile
            label="최근 실행"
            value={runs[0] ? `${formatMode(runs[0].mode)} · ${shortId(runs[0].run_id)}` : "없음"}
            detail={runs[0] ? formatTimestamp(runs[0].started_at) : "새 실행을 시작하세요"}
          />
          <div className="status-tile wide">
            <span>최근 로그 요약</span>
            <strong>
              <b className="dot error" /> 오류 {logSummary.error}
              <b className="dot warning" /> 경고 {logSummary.warning}
              <b className="dot info" /> 정보 {logSummary.info}
            </strong>
          </div>
          <button className="refresh-button" type="button" onClick={refresh}>
            새로고침
          </button>
        </header>

        {error ? <div className="core-alert">{error}</div> : null}

        <main className="core-layout">
          {activeSection === "data" ? (
            <DataSection
              candles={candles}
              dataQuery={dataQuery}
              dataSyncForm={dataSyncForm}
              dataSyncResult={dataSyncResult}
              marketStatus={marketStatus}
              onLoadCandles={() => void loadCandles()}
              onSyncData={() => void syncMarketData()}
              setDataQuery={setDataQuery}
              setDataSyncForm={setDataSyncForm}
              symbolOptions={symbolOptions}
              timeframeOptions={timeframeOptions}
            />
          ) : null}

          {activeSection === "backtest" ? (
            <RunLaunchSection
              activeRuns={activeRuns}
              form={form}
              mode="backtests"
              onSelectRun={setSelectedRunId}
              onSubmit={submitRun}
              selectedRunId={selectedRunId}
              setForm={setForm}
              strategies={strategies}
              symbolOptions={symbolOptions}
              timeframeOptions={timeframeOptions}
              title="백테스트"
            />
          ) : null}

          {activeSection === "sandbox" ? (
            <RunLaunchSection
              activeRuns={activeRuns}
              form={form}
              mode="sandbox"
              onSelectRun={setSelectedRunId}
              onSubmit={submitRun}
              selectedRunId={selectedRunId}
              setForm={setForm}
              strategies={strategies}
              symbolOptions={symbolOptions}
              timeframeOptions={timeframeOptions}
              title="샌드박스"
            />
          ) : null}

          {activeSection === "live" ? (
            <RunLaunchSection
              activeRuns={activeRuns}
              form={form}
              mode="live"
              onSelectRun={setSelectedRunId}
              onSubmit={submitRun}
              selectedRunId={selectedRunId}
              setForm={setForm}
              strategies={strategies}
              symbolOptions={symbolOptions}
              timeframeOptions={timeframeOptions}
              title="실전 매매"
            />
          ) : null}

          {activeSection === "logs" ? (
            <LogsSection
              logFilter={logFilter}
              logs={logs}
              onLoadLogs={() => void loadLogs()}
              setLogFilter={setLogFilter}
            />
          ) : null}

          {activeSection === "llm" ? (
            <LlmSection llmStrategy={llmStrategy} strategies={strategies} />
          ) : null}

          <RunDetailPanel
            logs={logs.filter((log) => log.run_id === selectedRunId)}
            orders={orders}
            positions={positions}
            run={selectedRun}
            onStop={stopSelectedRun}
          />
        </main>
      </div>
    </div>
  );
}

function DataSection({
  candles,
  dataQuery,
  dataSyncForm,
  dataSyncResult,
  marketStatus,
  onLoadCandles,
  onSyncData,
  setDataQuery,
  setDataSyncForm,
  symbolOptions,
  timeframeOptions,
}: {
  candles: Candle[];
  dataQuery: { symbol: string; timeframe: string; limit: string };
  dataSyncForm: DataSyncFormState;
  dataSyncResult: MarketDataSyncResult | null;
  marketStatus: MarketStatus | null;
  onLoadCandles: () => void;
  onSyncData: () => void;
  setDataQuery: (value: { symbol: string; timeframe: string; limit: string }) => void;
  setDataSyncForm: (value: DataSyncFormState) => void;
  symbolOptions: string[];
  timeframeOptions: string[];
}) {
  const latest = candles[candles.length - 1];
  const submitSync = (event: FormEvent) => {
    event.preventDefault();
    onSyncData();
  };
  return (
    <section className="core-panel core-panel-main">
      <div className="panel-heading">
        <div>
          <p className="core-eyebrow">데이터</p>
          <h2>시장 데이터</h2>
        </div>
        <button type="button" onClick={onLoadCandles}>
          캔들 불러오기
        </button>
      </div>
      <div className="form-grid compact">
        <label>
          심볼
          <select
            value={dataQuery.symbol}
            onChange={(event) => setDataQuery({ ...dataQuery, symbol: event.target.value })}
          >
            {symbolOptions.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>
        </label>
        <label>
          타임프레임
          <select
            value={dataQuery.timeframe}
            onChange={(event) => setDataQuery({ ...dataQuery, timeframe: event.target.value })}
          >
            {timeframeOptions.map((timeframe) => (
              <option key={timeframe} value={timeframe}>
                {timeframe}
              </option>
            ))}
          </select>
        </label>
        <label>
          조회 개수
          <input
            type="number"
            value={dataQuery.limit}
            onChange={(event) => setDataQuery({ ...dataQuery, limit: event.target.value })}
          />
        </label>
      </div>
      <form className="sync-panel" onSubmit={submitSync}>
        <div className="sync-panel-heading">
          <div>
            <p className="core-eyebrow">데이터 적재</p>
            <h3>REST 백필</h3>
          </div>
          <button type="submit">동기화</button>
        </div>
        <div className="form-grid sync-grid">
          <label>
            심볼
            <select
              value={dataSyncForm.symbol}
              onChange={(event) => setDataSyncForm({ ...dataSyncForm, symbol: event.target.value })}
            >
              {symbolOptions.map((symbol) => (
                <option key={symbol} value={symbol}>
                  {symbol}
                </option>
              ))}
            </select>
          </label>
          <label>
            타임프레임
            <select
              value={dataSyncForm.timeframe}
              onChange={(event) => setDataSyncForm({ ...dataSyncForm, timeframe: event.target.value })}
            >
              {timeframeOptions.map((timeframe) => (
                <option key={timeframe} value={timeframe}>
                  {timeframe}
                </option>
              ))}
            </select>
          </label>
          <label>
            시작일
            <input
              type="datetime-local"
              value={dataSyncForm.start_at}
              onChange={(event) => setDataSyncForm({ ...dataSyncForm, start_at: event.target.value })}
            />
          </label>
          <label>
            종료일
            <input
              type="datetime-local"
              value={dataSyncForm.end_at}
              onChange={(event) => setDataSyncForm({ ...dataSyncForm, end_at: event.target.value })}
            />
          </label>
          <label>
            적재 개수
            <input
              min="1"
              type="number"
              value={dataSyncForm.limit}
              onChange={(event) => setDataSyncForm({ ...dataSyncForm, limit: event.target.value })}
            />
          </label>
        </div>
        {dataSyncResult ? (
          <div className="sync-result" role="status">
            <span>{formatDataStatus(dataSyncResult.status)}</span>
            <strong>{dataSyncResult.candle_count}개</strong>
            <small>
              {formatTimestamp(dataSyncResult.effective_start_at)} - {formatTimestamp(dataSyncResult.effective_end_at)}
            </small>
          </div>
        ) : null}
      </form>
      <div className="metric-grid">
        <Metric label="제공자" value={marketStatus?.provider ?? "-"} />
        <Metric label="거래소" value={marketStatus?.venue ?? "-"} />
        <Metric label="인스트루먼트" value={String(marketStatus?.instruments.length ?? 0)} />
        <Metric label="최근 종가" value={latest ? formatNumber(latest.close) : "-"} />
      </div>
      <MarketChart candles={candles} symbol={dataQuery.symbol} timeframe={dataQuery.timeframe} />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>인스트루먼트</th>
              <th>타임프레임</th>
              <th>캔들 수</th>
              <th>상태</th>
              <th>마지막 캔들</th>
            </tr>
          </thead>
          <tbody>
            {(marketStatus?.instruments ?? []).map((instrument) => (
              <tr key={instrument.instrument_id}>
                <td>{instrument.instrument_id}</td>
                <td>{instrument.timeframe}</td>
                <td>{instrument.candle_count}</td>
                <td>{formatDataStatus(instrument.sync_status ?? "fixture")}</td>
                <td>{formatTimestamp(instrument.last_timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function MarketChart({
  candles,
  symbol,
  timeframe,
}: {
  candles: Candle[];
  symbol: string;
  timeframe: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || candles.length === 0 || import.meta.env.MODE === "test") {
      return;
    }

    let chart: IChartApi | null = null;
    let series: ISeriesApi<"Candlestick"> | null = null;
    let averageSeries: Array<ISeriesApi<"Line">> = [];
    let resizeObserver: ResizeObserver | null = null;
    let disposed = false;

    const renderChart = async () => {
      const { CandlestickSeries, ColorType, LineSeries, createChart } = await import("lightweight-charts");
      if (disposed || !containerRef.current) {
        return;
      }

      chart = createChart(containerRef.current, {
        autoSize: false,
        height: 280,
        layout: {
          background: { type: ColorType.Solid, color: "transparent" },
          textColor: "#93a1b8",
          fontFamily: "Roboto, Noto Sans KR, sans-serif",
          fontSize: 12,
        },
        localization: {
          timeFormatter: formatChartTime,
        },
        grid: {
          vertLines: { color: "rgba(46, 62, 91, 0.28)" },
          horzLines: { color: "rgba(46, 62, 91, 0.45)" },
        },
        rightPriceScale: {
          borderColor: "rgba(46, 62, 91, 0.8)",
        },
        timeScale: {
          borderColor: "rgba(46, 62, 91, 0.8)",
          timeVisible: true,
          secondsVisible: false,
          tickMarkFormatter: (time: Time) => formatChartTime(time),
        },
        crosshair: {
          vertLine: { color: "rgba(159, 122, 255, 0.48)" },
          horzLine: { color: "rgba(159, 122, 255, 0.48)" },
        },
      });

      series = chart.addSeries(CandlestickSeries, {
        upColor: "#31d17d",
        downColor: "#ff514f",
        borderUpColor: "#31d17d",
        borderDownColor: "#ff514f",
        wickUpColor: "#31d17d",
        wickDownColor: "#ff514f",
        priceLineVisible: false,
        lastValueVisible: true,
      });
      series.setData(toCandlestickSeriesData(candles));
      averageSeries = movingAverageLines.map((average) => {
        const line = chart!.addSeries(LineSeries, {
          color: average.color,
          lineWidth: average.width,
          priceLineVisible: false,
          lastValueVisible: true,
          crosshairMarkerVisible: true,
        });
        line.setData(toMovingAverageSeriesData(candles, average.period));
        return line;
      });
      chart.timeScale().fitContent();

      const resize = () => {
        const width = containerRef.current?.clientWidth ?? 0;
        if (chart && width > 0) {
          chart.resize(width, 280);
        }
      };
      resize();

      resizeObserver = new ResizeObserver(resize);
      resizeObserver.observe(containerRef.current);
    };

    void renderChart();

    return () => {
      disposed = true;
      resizeObserver?.disconnect();
      chart?.remove();
      averageSeries = [];
      series = null;
      chart = null;
    };
  }, [candles]);

  return (
    <section className="chart-panel" aria-label={`${symbol} ${timeframe} 가격 차트`}>
      <div className="chart-heading">
        <div>
          <strong>{symbol}</strong>
          <span>{timeframe} 가격 추이</span>
        </div>
        <div className="chart-heading-meta">
          <small>캔들 {candles.length}개</small>
          <div className="ma-legend" aria-label="moving average legend">
            {movingAverageLines.map((average) => (
              <span key={average.period}>
                <b style={{ backgroundColor: average.color }} />
                {average.label}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div className="market-chart" ref={containerRef}>
        {candles.length === 0 ? <span className="chart-empty">불러온 캔들 데이터가 없습니다</span> : null}
      </div>
    </section>
  );
}

function RunLaunchSection({
  activeRuns,
  form,
  mode,
  onSelectRun,
  onSubmit,
  selectedRunId,
  setForm,
  strategies,
  symbolOptions,
  timeframeOptions,
  title,
}: {
  activeRuns: RunSummary[];
  form: RunFormState;
  mode: "backtests" | "sandbox" | "live";
  onSelectRun: (runId: string) => void;
  onSubmit: (mode: "backtests" | "sandbox" | "live") => Promise<void>;
  selectedRunId: string | null;
  setForm: (value: RunFormState) => void;
  strategies: Strategy[];
  symbolOptions: string[];
  timeframeOptions: string[];
  title: string;
}) {
  const submit = (event: FormEvent) => {
    event.preventDefault();
    void onSubmit(mode);
  };
  const runnableStrategies = strategies.filter((strategy) => strategy.runtime !== "decision_engine");
  const latestRun = activeRuns[0];
  return (
    <section className="core-panel core-panel-main">
      <div className="panel-heading">
        <div>
          <p className="core-eyebrow">{title}</p>
          <h2>{title} 실행</h2>
        </div>
      </div>
      <div className="metric-grid summary-grid">
        <Metric label="종료 자산" value={String(latestRun?.metrics.ending_equity ?? "-")} tone="neutral" />
        <Metric label="수익률" value={String(latestRun?.metrics.total_return_pct ?? "-")} tone="positive" />
        <Metric label="거래 수" value={String(latestRun?.orders_count ?? 0)} />
        <Metric label="상태" value={formatRunStatus(latestRun?.status)} tone={latestRun?.status === "running" ? "positive" : "neutral"} />
      </div>
      <form className="run-form" onSubmit={submit}>
        <div className="form-grid">
          <label>
            전략
            <select
              value={form.strategy_id}
              onChange={(event) => setForm({ ...form, strategy_id: event.target.value })}
            >
              {runnableStrategies.map((strategy) => (
                <option key={strategy.strategy_id} value={strategy.strategy_id}>
                  {strategy.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            심볼
            <select
              value={form.symbol}
              onChange={(event) => setForm({ ...form, symbol: event.target.value })}
            >
              {symbolOptions.map((symbol) => (
                <option key={symbol} value={symbol}>
                  {symbol}
                </option>
              ))}
            </select>
          </label>
          <label>
            타임프레임
            <select
              value={form.timeframe}
              onChange={(event) => setForm({ ...form, timeframe: event.target.value })}
            >
              {timeframeOptions.map((timeframe) => (
                <option key={timeframe} value={timeframe}>
                  {timeframe}
                </option>
              ))}
            </select>
          </label>
          <label>
            초기 자본
            <input
              type="number"
              value={form.initial_cash}
              onChange={(event) => setForm({ ...form, initial_cash: event.target.value })}
            />
          </label>
          <label>
            수수료율
            <input
              type="number"
              step="0.0001"
              value={form.fee_rate}
              onChange={(event) => setForm({ ...form, fee_rate: event.target.value })}
            />
          </label>
          <label>
            슬리피지
            <input
              type="number"
              value={form.slippage_bps}
              onChange={(event) => setForm({ ...form, slippage_bps: event.target.value })}
            />
          </label>
          <label>
            프라이밍 캔들 수
            <input
              type="number"
              value={form.replay_bars}
              onChange={(event) => setForm({ ...form, replay_bars: event.target.value })}
            />
          </label>
          <label>
            시작일
            <input
              type="datetime-local"
              value={form.start_at}
              onChange={(event) => setForm({ ...form, start_at: event.target.value })}
            />
          </label>
          <label>
            종료일
            <input
              type="datetime-local"
              value={form.end_at}
              onChange={(event) => setForm({ ...form, end_at: event.target.value })}
            />
          </label>
        </div>
        <label>
          전략 파라미터
          <textarea
            value={form.parameters}
            onChange={(event) => setForm({ ...form, parameters: event.target.value })}
          />
        </label>
        <button type="submit">{title} 실행</button>
      </form>
      <RunList activeRuns={activeRuns} onSelectRun={onSelectRun} selectedRunId={selectedRunId} />
    </section>
  );
}

function RunList({
  activeRuns,
  onSelectRun,
  selectedRunId,
}: {
  activeRuns: RunSummary[];
  onSelectRun: (runId: string) => void;
  selectedRunId: string | null;
}) {
  return (
    <div className="run-list">
      <div className="run-list-header">
        <strong>최근 실행</strong>
        <span>{activeRuns.length}개</span>
      </div>
      {activeRuns.map((run) => (
        <button
          className={selectedRunId === run.run_id ? "run-row is-active" : "run-row"}
          key={run.run_id}
          onClick={() => onSelectRun(run.run_id)}
          type="button"
        >
          <span>{formatMode(run.mode)}</span>
          <strong>{run.strategy?.name ?? run.run_id}</strong>
          <span>{run.config?.symbols?.[0] ?? run.run_id}</span>
          <small>
            {formatRunStatus(run.status)} · {formatTimestamp(run.started_at)}
          </small>
        </button>
      ))}
    </div>
  );
}

function LogsSection({
  logFilter,
  logs,
  onLoadLogs,
  setLogFilter,
}: {
  logFilter: { mode: string; severity: string };
  logs: OperationLog[];
  onLoadLogs: () => void;
  setLogFilter: (value: { mode: string; severity: string }) => void;
}) {
  return (
    <section className="core-panel core-panel-main">
      <div className="panel-heading">
        <div>
          <p className="core-eyebrow">로그</p>
          <h2>운영 로그</h2>
        </div>
        <button type="button" onClick={onLoadLogs}>
          필터 적용
        </button>
      </div>
      <div className="form-grid compact">
        <label>
          실행 모드
          <select
            value={logFilter.mode}
            onChange={(event) => setLogFilter({ ...logFilter, mode: event.target.value })}
          >
            <option value="">전체</option>
            <option value="backtest">백테스트</option>
            <option value="sandbox">샌드박스</option>
            <option value="live">실전 매매</option>
          </select>
        </label>
        <label>
          심각도
          <select
            value={logFilter.severity}
            onChange={(event) => setLogFilter({ ...logFilter, severity: event.target.value })}
          >
            <option value="">전체</option>
            <option value="info">정보</option>
            <option value="warning">경고</option>
            <option value="error">오류</option>
          </select>
        </label>
      </div>
      <LogList logs={logs} />
    </section>
  );
}

function LlmSection({
  llmStrategy,
  strategies,
}: {
  llmStrategy: Record<string, unknown> | null;
  strategies: Strategy[];
}) {
  const metadata = strategies.find((strategy) => strategy.strategy_id === "external_decision_template");
  return (
    <section className="core-panel core-panel-main">
      <div className="panel-heading">
        <div>
          <p className="core-eyebrow">LLM 전략</p>
          <h2>격리된 의사결정 인터페이스</h2>
        </div>
      </div>
      <div className="metric-grid">
        <Metric label="전략" value={metadata?.name ?? "Future LLM Research Lane"} />
        <Metric label="런타임" value={formatRuntime(String(llmStrategy?.runtime ?? "decision_engine"))} />
        <Metric label="포트" value={String(llmStrategy?.decision_port ?? "DecisionEnginePort")} />
        <Metric label="격리 상태" value={formatIsolationState(String(llmStrategy?.isolation_state ?? "interface_only"))} />
      </div>
      <pre className="json-panel">{JSON.stringify(llmStrategy?.trace_envelope ?? {}, null, 2)}</pre>
    </section>
  );
}

function RunDetailPanel({
  logs,
  onStop,
  orders,
  positions,
  run,
}: {
  logs: OperationLog[];
  onStop: () => void;
  orders: unknown[];
  positions: unknown[];
  run: RunSummary | null;
}) {
  const [activeTab, setActiveTab] = useState<DetailTabId>("overview");

  useEffect(() => {
    setActiveTab("overview");
  }, [run?.run_id]);

  return (
    <aside className="core-panel detail-panel">
      <div className="panel-heading">
        <div>
          <p className="core-eyebrow">실행 상세</p>
          <h2>{run ? formatMode(run.mode) : "선택된 실행 없음"}</h2>
        </div>
        <button disabled={!run || run.status !== "running"} onClick={onStop} type="button">
          중지
        </button>
      </div>
      {run ? (
        <>
          <div className="detail-tabs" aria-label="run detail tabs">
            {detailTabs.map((tab) => (
              <button
                aria-pressed={activeTab === tab.id}
                className={activeTab === tab.id ? "is-active" : ""}
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                type="button"
              >
                {tab.label}
              </button>
            ))}
          </div>
          {activeTab === "overview" ? <RunOverview run={run} /> : null}
          {activeTab === "orders" ? <JsonDetail title="주문" value={orders} emptyText="주문이 없습니다." /> : null}
          {activeTab === "positions" ? (
            <JsonDetail title="포지션" value={positions} emptyText="포지션이 없습니다." />
          ) : null}
          {activeTab === "metrics" ? <RunMetricsDetail metrics={run.metrics} /> : null}
          {activeTab === "logs" ? <RunLogsDetail logs={logs} /> : null}
        </>
      ) : (
        <p className="muted">백테스트, 샌드박스, 실전 매매에서 실행을 선택하세요.</p>
      )}
    </aside>
  );
}

function RunOverview({ run }: { run: RunSummary }) {
  const marketData = run.market_data;
  const symbol = run.config?.symbols?.[0] ?? "-";
  return (
    <div className="detail-section">
      <div className="metric-grid two">
        <Metric label="상태" value={formatRunStatus(run.status)} />
        <Metric label="종료 자산" value={formatMetricValue(run.metrics.ending_equity)} />
        <Metric
          label="수익률"
          value={formatMetricValue(run.metrics.total_return_pct, "%")}
          tone={Number(run.metrics.total_return_pct ?? 0) >= 0 ? "positive" : "negative"}
        />
        <Metric label="거래 수" value={formatMetricValue(run.metrics.trade_count ?? run.orders_count)} />
      </div>
      <div className="detail-list">
        <DetailLine label="전략" value={run.strategy?.name ?? "-"} />
        <DetailLine label="심볼" value={symbol} />
        <DetailLine label="타임프레임" value={run.config?.timeframe ?? marketData?.timeframe ?? "-"} />
        <DetailLine label="요청 기간" value={formatRange(run.config?.start_at, run.config?.end_at)} />
        <DetailLine
          label="데이터 범위"
          value={formatRange(marketData?.effective_start_at, marketData?.effective_end_at)}
        />
        <DetailLine label="캔들 수" value={formatMetricValue(marketData?.candle_count)} />
        <DetailLine label="데이터 상태" value={formatDataStatus(marketData?.sync_status ?? "-")} />
      </div>
      {marketData?.issues?.length ? (
        <div className="detail-issues">
          {marketData.issues.map((issue) => (
            <span key={issue}>{issue}</span>
          ))}
        </div>
      ) : null}
      <RecentNotes notes={run.notes} />
    </div>
  );
}

function RunMetricsDetail({ metrics }: { metrics: Record<string, number | string> }) {
  const entries = Object.entries(metrics);
  return (
    <div className="detail-section">
      {entries.length > 0 ? (
        <div className="detail-list">
          {entries.map(([key, value]) => (
            <DetailLine key={key} label={formatMetricLabel(key)} value={formatMetricValue(value)} />
          ))}
        </div>
      ) : (
        <p className="muted">지표가 없습니다.</p>
      )}
      <pre className="json-panel">{JSON.stringify(metrics, null, 2)}</pre>
    </div>
  );
}

function JsonDetail({
  emptyText,
  title,
  value,
}: {
  emptyText: string;
  title: string;
  value: unknown[];
}) {
  return (
    <div className="detail-section">
      <div className="run-list-header inline">
        <strong>{title}</strong>
        <span>{value.length}개</span>
      </div>
      {value.length === 0 ? <p className="muted">{emptyText}</p> : null}
      <pre className="json-panel">{JSON.stringify(value, null, 2)}</pre>
    </div>
  );
}

function RunLogsDetail({ logs }: { logs: OperationLog[] }) {
  return (
    <div className="detail-section">
      {logs.length === 0 ? <p className="muted">이 실행에 연결된 로그가 없습니다.</p> : null}
      <LogList logs={logs} compact />
    </div>
  );
}

function DetailLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail-line">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function RecentNotes({ notes }: { notes: string[] }) {
  if (notes.length === 0) {
    return null;
  }
  return (
    <div className="notes-list">
      {notes.slice(-4).map((note) => (
        <p key={note}>{note}</p>
      ))}
    </div>
  );
}

function LogList({ compact = false, logs }: { compact?: boolean; logs: OperationLog[] }) {
  return (
    <div className={compact ? "log-list compact" : "log-list"}>
      {logs.map((log) => (
        <article key={log.log_id}>
          <span className={`severity ${log.severity}`}>{formatSeverity(log.severity)}</span>
          <strong>{formatEventType(log.event_type)}</strong>
          <p>{log.message}</p>
          <small>{formatTimestamp(log.recorded_at)}</small>
        </article>
      ))}
    </div>
  );
}

function StatusTile({
  detail,
  label,
  tone = "neutral",
  value,
}: {
  detail?: string;
  label: string;
  tone?: "neutral" | "success" | "warning";
  value: string;
}) {
  return (
    <article className={`status-tile ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </article>
  );
}

function Metric({
  label,
  tone = "neutral",
  value,
}: {
  label: string;
  tone?: "neutral" | "positive" | "negative";
  value: string;
}) {
  return (
    <article className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function shortId(value: string) {
  return value.length > 8 ? value.slice(0, 8) : value;
}

function formatTimestamp(value?: string | null) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return formatKstDate(date);
}

function formatChartTime(time: Time) {
  if (typeof time === "number") {
    return formatKstDate(new Date(time * 1000));
  }
  if (typeof time === "string") {
    const date = new Date(time);
    return Number.isNaN(date.getTime()) ? time : formatKstDate(date);
  }
  return formatKstDate(new Date(Date.UTC(time.year, time.month - 1, time.day)));
}

function formatKstDate(date: Date) {
  const parts = new Intl.DateTimeFormat("en", {
    day: "2-digit",
    hour: "2-digit",
    hour12: false,
    hourCycle: "h23",
    minute: "2-digit",
    month: "2-digit",
    timeZone: "Asia/Seoul",
    year: "2-digit",
  }).formatToParts(date);
  const part = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((item) => item.type === type)?.value ?? "00";
  return `${part("hour")}:${part("minute")} ${part("year")}-${part("month")}-${part("day")}`;
}

function toApiDateTime(value: string) {
  if (!value) {
    return null;
  }
  return new Date(value).toISOString();
}

function formatNumber(value: number) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);
}

function formatMetricValue(value: unknown, suffix = "") {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "number") {
    return `${formatNumber(value)}${suffix}`;
  }
  return `${value}${suffix}`;
}

function formatMetricLabel(value: string) {
  switch (value) {
    case "initial_cash":
      return "초기 자본";
    case "ending_equity":
      return "종료 자산";
    case "total_return_pct":
      return "총수익률";
    case "max_drawdown_pct":
      return "최대 낙폭";
    case "trade_count":
      return "거래 수";
    case "win_rate_pct":
      return "승률";
    case "exposure_pct":
      return "노출";
    default:
      return value.replaceAll("_", " ");
  }
}

function formatRange(start?: string | null, end?: string | null) {
  if (!start && !end) {
    return "-";
  }
  return `${formatTimestamp(start)} - ${formatTimestamp(end)}`;
}

function formatHealthStatus(value?: string | null) {
  switch (value) {
    case "ok":
      return "정상";
    case "error":
    case "오류":
      return "오류";
    default:
      return value ?? "-";
  }
}

function formatDataStatus(value?: string | null) {
  switch (value) {
    case "fixture":
      return "시드 데이터";
    case "synced":
      return "동기화됨";
    case "stale":
      return "지연";
    case "failed":
      return "실패";
    default:
      return value ?? "-";
  }
}

function formatMode(value?: string | null) {
  switch (value) {
    case "backtest":
      return "백테스트";
    case "sandbox":
      return "샌드박스";
    case "live":
      return "실전 매매";
    default:
      return "대기";
  }
}

function formatRunStatus(value?: string | null) {
  switch (value) {
    case "pending":
      return "대기";
    case "running":
      return "실행 중";
    case "completed":
      return "완료";
    case "failed":
      return "실패";
    case "stopped":
      return "중지됨";
    default:
      return "대기";
  }
}

function formatSeverity(value?: string | null) {
  switch (value) {
    case "error":
      return "오류";
    case "warning":
      return "경고";
    case "info":
      return "정보";
    default:
      return value ?? "-";
  }
}

function formatRuntime(value?: string | null) {
  switch (value) {
    case "decision_engine":
      return "의사결정 엔진";
    case "native":
      return "네이티브";
    default:
      return value ?? "-";
  }
}

function formatIsolationState(value?: string | null) {
  switch (value) {
    case "interface_only":
      return "인터페이스만 유지";
    default:
      return value ?? "-";
  }
}

function formatEventType(value: string) {
  switch (value) {
    case "runtime_initialized":
      return "런타임 초기화";
    case "backtest_completed":
      return "백테스트 완료";
    case "backtest_failed":
      return "백테스트 실패";
    case "sandbox_started":
      return "샌드박스 시작";
    case "sandbox_failed":
      return "샌드박스 실패";
    case "live_started":
      return "실전 매매 시작";
    case "live_failed":
      return "실전 매매 실패";
    case "run_stopped":
      return "실행 중지";
    default:
      return value.replaceAll("_", " ");
  }
}

function toSymbol(instrumentId: string) {
  return instrumentId.includes(":") ? instrumentId.split(":").at(-1) ?? instrumentId : instrumentId;
}

function uniqueOptions(values: string[]) {
  return [...new Set(values.map((value) => value.trim()).filter(Boolean))];
}

function toCandlestickSeriesData(candles: Candle[]): CandlestickData[] {
  const byTime = new Map<number, CandlestickData>();
  for (const candle of candles) {
    const timestamp = Math.floor(new Date(candle.timestamp).getTime() / 1000);
    if (Number.isFinite(timestamp)) {
      byTime.set(timestamp, {
        time: timestamp as UTCTimestamp,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      });
    }
  }
  return [...byTime.entries()]
    .sort(([left], [right]) => left - right)
    .map(([, value]) => value);
}

function toMovingAverageSeriesData(candles: Candle[], period: number): LineData[] {
  const sortedCandles = [...candles].sort(
    (left, right) => new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime(),
  );
  const values: LineData[] = [];
  let rollingSum = 0;
  for (let index = 0; index < sortedCandles.length; index += 1) {
    rollingSum += sortedCandles[index].close;
    if (index >= period) {
      rollingSum -= sortedCandles[index - period].close;
    }
    if (index < period - 1) {
      continue;
    }
    const timestamp = Math.floor(new Date(sortedCandles[index].timestamp).getTime() / 1000);
    if (Number.isFinite(timestamp)) {
      values.push({
        time: timestamp as UTCTimestamp,
        value: Number((rollingSum / period).toFixed(8)),
      });
    }
  }
  return values;
}
