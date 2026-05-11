import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import type { CandlestickData, IChartApi, IRange, ISeriesApi, LineData, Time, UTCTimestamp } from "lightweight-charts";

type SectionId = "data" | "backtest" | "sandbox" | "live" | "performance" | "logs" | "llm";
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

type UnknownRecord = Record<string, unknown>;

type PerformanceModeRow = {
  color: string;
  label: string;
  maxDrawdownPct: number;
  mode: RunSummary["mode"];
  runCount: number;
  totalReturnPct: number;
  tradeCount: number;
  winRatePct: number;
};

type PerformanceStrategyRow = {
  lastRunAt: string | null;
  maxDrawdownPct: number;
  mode: RunSummary["mode"];
  modeLabel: string;
  runCount: number;
  sharpeRatio: number;
  strategy: string;
  totalReturnPct: number;
  tradeCount: number;
  winRatePct: number;
};

type PerformanceSymbolRow = {
  runCount: number;
  symbol: string;
  totalReturnPct: number;
  weightPct: number;
};

type PerformanceMonthRow = {
  label: string;
  mode: RunSummary["mode"];
  months: string[];
  values: number[];
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

type DataQueryState = {
  symbol: string;
  timeframe: string;
  start_at: string;
  end_at: string;
  limit: string;
};

type DataLoadingMode = "idle" | "loading" | "appending";

const apiBase = "/api";
const defaultCandleQueryLimit = 500;
const maxCandleQueryLimit = 5000;
const baseTimeframeOptions = ["1m", "5m"] as const;

const sections: Array<{ id: SectionId; label: string; eyebrow: string; mark: string; path: string }> = [
  { id: "data", label: "데이터", eyebrow: "수집 현황", mark: "D", path: "/data" },
  { id: "backtest", label: "백테스트", eyebrow: "과거 검증", mark: "B", path: "/backtest" },
  { id: "sandbox", label: "샌드박스", eyebrow: "모의 테스트", mark: "S", path: "/sandbox" },
  { id: "live", label: "실전 매매", eyebrow: "가드드 라이브", mark: "L", path: "/live" },
  { id: "performance", label: "성과", eyebrow: "성과 분석", mark: "P", path: "/performance" },
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

const rsiIndicator = { period: 14, label: "RSI14", color: "#ff8f3d", width: 1 } as const;
const marketChartHeight = 340;

const performanceModeMeta: Record<RunSummary["mode"], { color: string; label: string }> = {
  backtest: { color: "#9f7aff", label: "백테스트" },
  sandbox: { color: "#4d8dff", label: "샌드박스" },
  live: { color: "#31d17d", label: "실전 매매" },
};

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

const defaultDataQuery: DataQueryState = {
  symbol: "BTC/USDT",
  timeframe: "5m",
  start_at: "",
  end_at: "",
  limit: String(defaultCandleQueryLimit),
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
  const [dataQuery, setDataQuery] = useState<DataQueryState>(defaultDataQuery);
  const [dataLoadingMode, setDataLoadingMode] = useState<DataLoadingMode>("idle");
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
        form.symbol,
      ]),
    [dataQuery.symbol, form.symbol, marketStatus],
  );

  const timeframeOptions = useMemo(
    () =>
      uniqueOptions([
        ...baseTimeframeOptions,
        ...(marketStatus?.instruments.map((instrument) => instrument.timeframe) ?? []),
        dataQuery.timeframe,
        form.timeframe,
      ]),
    [dataQuery.timeframe, form.timeframe, marketStatus],
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
      ...buildAlignedDateRange(form.start_at, form.end_at, form.timeframe),
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

  const loadCandles = async (
    queryState = dataQuery,
    options: { appendOlder?: boolean; endAtOverride?: string | null; startAtOverride?: string | null } = {},
  ) => {
    setError(null);
    setDataLoadingMode(options.appendOlder ? "appending" : "loading");
    try {
      const payload = buildMarketDataPayload(queryState, options);
      const result = await fetchJson<MarketDataSyncResult>("/market-data/sync", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const response = await fetchJson<{ candles: Candle[] }>(
        `/market-data/candles?${buildMarketDataQuery(queryState, options)}`,
      );
      setDataSyncResult(result);
      setDataQuery({
        symbol: result.symbol,
        timeframe: result.timeframe,
        start_at: queryState.start_at,
        end_at: queryState.end_at,
        limit: String(payload.limit),
      });
      setCandles((current) =>
        options.appendOlder ? mergeCandles(response.candles, current) : mergeCandles(response.candles),
      );
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "시장 데이터 요청에 실패했습니다.");
    } finally {
      setDataLoadingMode("idle");
    }
  };

  const loadOlderCandles = async () => {
    const earliestCandleAt = getEarliestCandleTimestamp(candles);
    if (!earliestCandleAt || dataLoadingMode !== "idle") {
      return;
    }
    await loadCandles(dataQuery, {
      appendOlder: true,
      endAtOverride: getPreviousPageEndAt(earliestCandleAt, dataQuery.timeframe)?.toISOString() ?? null,
      startAtOverride: null,
    });
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

        <main className={activeSection === "performance" ? "core-layout performance-layout" : "core-layout"}>
          {activeSection === "data" ? (
            <DataSection
              candles={candles}
              dataQuery={dataQuery}
              dataLoadingMode={dataLoadingMode}
              dataSyncResult={dataSyncResult}
              marketStatus={marketStatus}
              onLoadCandles={() => void loadCandles()}
              onLoadOlderCandles={() => void loadOlderCandles()}
              setDataQuery={setDataQuery}
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

          {activeSection === "performance" ? (
            <PerformanceSection logs={logs} onRefresh={() => void refresh()} runs={runs} />
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

          {activeSection !== "performance" ? (
            <RunDetailPanel
              logs={logs.filter((log) => log.run_id === selectedRunId)}
              orders={orders}
              positions={positions}
              run={selectedRun}
              onStop={stopSelectedRun}
            />
          ) : null}
        </main>
      </div>
    </div>
  );
}

function PerformanceSection({
  logs,
  onRefresh,
  runs,
}: {
  logs: OperationLog[];
  onRefresh: () => void;
  runs: RunSummary[];
}) {
  const [filters, setFilters] = useState({ mode: "all", symbol: "all", timeframe: "all" });
  const symbolOptions = useMemo(
    () => uniqueOptions(runs.map((run) => run.config?.symbols?.[0] ?? "").filter(Boolean)),
    [runs],
  );
  const timeframeOptions = useMemo(
    () => uniqueOptions(runs.map((run) => run.config?.timeframe ?? "").filter(Boolean)),
    [runs],
  );
  const filteredRuns = useMemo(
    () =>
      runs.filter((run) => {
        const symbol = run.config?.symbols?.[0] ?? "";
        const timeframe = run.config?.timeframe ?? "";
        return (
          (filters.mode === "all" || run.mode === filters.mode) &&
          (filters.symbol === "all" || symbol === filters.symbol) &&
          (filters.timeframe === "all" || timeframe === filters.timeframe)
        );
      }),
    [filters, runs],
  );
  const summary = useMemo(() => buildPerformanceSummary(filteredRuns), [filteredRuns]);
  const modeRows = useMemo(() => buildModePerformanceRows(filteredRuns), [filteredRuns]);
  const strategyRows = useMemo(() => buildStrategyPerformanceRows(filteredRuns), [filteredRuns]);
  const symbolRows = useMemo(() => buildSymbolPerformanceRows(filteredRuns), [filteredRuns]);
  const monthlyRows = useMemo(() => buildMonthlyPerformanceRows(filteredRuns), [filteredRuns]);
  const cumulativeSeries = useMemo(() => buildCumulativePerformanceSeries(filteredRuns), [filteredRuns]);
  const insightCards = useMemo(
    () => buildPerformanceInsights({ logs, modeRows, runs: filteredRuns, strategyRows }),
    [filteredRuns, logs, modeRows, strategyRows],
  );

  return (
    <section className="core-panel core-panel-main performance-panel">
      <div className="performance-heading">
        <div>
          <p className="core-eyebrow">성과</p>
          <h2>성과 대시보드</h2>
          <span>백테스트, 샌드박스, 실전 매매의 전략 성과를 같은 기준으로 비교합니다.</span>
        </div>
        <button type="button" onClick={onRefresh}>
          새로고침
        </button>
      </div>

      <div className="performance-toolbar">
        <div className="segmented-control" aria-label="performance mode filter">
          {[
            ["all", "전체"],
            ["backtest", "백테스트"],
            ["sandbox", "샌드박스"],
            ["live", "실전 매매"],
          ].map(([value, label]) => (
            <button
              aria-pressed={filters.mode === value}
              className={filters.mode === value ? "is-active" : ""}
              key={value}
              onClick={() => setFilters({ ...filters, mode: value })}
              type="button"
            >
              {label}
            </button>
          ))}
        </div>
        <label>
          심볼
          <select value={filters.symbol} onChange={(event) => setFilters({ ...filters, symbol: event.target.value })}>
            <option value="all">전체</option>
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
            value={filters.timeframe}
            onChange={(event) => setFilters({ ...filters, timeframe: event.target.value })}
          >
            <option value="all">전체</option>
            {timeframeOptions.map((timeframe) => (
              <option key={timeframe} value={timeframe}>
                {timeframe}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="performance-stat-grid">
        <PerformanceStatCard label="가중 수익률" tone={summary.totalReturnPct >= 0 ? "positive" : "negative"} value={formatPercent(summary.totalReturnPct)} />
        <PerformanceStatCard label="최대 낙폭" tone={summary.maxDrawdownPct < 0 ? "negative" : "neutral"} value={formatPercent(summary.maxDrawdownPct)} />
        <PerformanceStatCard label="승률" tone={summary.winRatePct >= 50 ? "positive" : "neutral"} value={formatPercent(summary.winRatePct)} />
        <PerformanceStatCard label="샤프 비율" tone={summary.sharpeRatio >= 1 ? "positive" : "neutral"} value={formatMetricValue(summary.sharpeRatio)} />
        <PerformanceStatCard label="총 거래 수" value={formatNumber(summary.tradeCount)} />
        <PerformanceStatCard label="활성 실행 수" value={formatNumber(summary.activeRunCount)} />
      </div>

      <div className="performance-grid">
        <article className="performance-card performance-chart-card wide">
          <div className="performance-card-heading">
            <strong>수익률 추이 비교</strong>
            <span>{filteredRuns.length}개 실행</span>
          </div>
          <PerformanceLineChart series={cumulativeSeries} />
        </article>

        <article className="performance-card">
          <div className="performance-card-heading">
            <strong>최대 낙폭</strong>
            <span>MDD</span>
          </div>
          <div className="drawdown-list">
            {modeRows.map((row) => (
              <div key={row.mode}>
                <span>{row.label}</span>
                <b>
                  <i style={{ width: `${Math.min(Math.abs(row.maxDrawdownPct), 100)}%` }} />
                </b>
                <strong>{formatPercent(row.maxDrawdownPct)}</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="performance-card">
          <div className="performance-card-heading">
            <strong>모드별 수익 기여도</strong>
            <span>{formatPercent(summary.totalReturnPct)}</span>
          </div>
          <ContributionRing rows={modeRows} />
        </article>

        <article className="performance-card">
          <div className="performance-card-heading">
            <strong>성과 인사이트</strong>
            <span>최근 {logs.length} 로그</span>
          </div>
          <div className="insight-list">
            {insightCards.map((insight) => (
              <article key={insight.title}>
                <span className={`insight-icon ${insight.tone}`}>{insight.mark}</span>
                <div>
                  <strong>{insight.title}</strong>
                  <p>{insight.body}</p>
                  <small>{insight.value}</small>
                </div>
              </article>
            ))}
          </div>
        </article>

        <article className="performance-card heatmap-card">
          <div className="performance-card-heading">
            <strong>월별 수익률 히트맵</strong>
            <span>최근 실행 기준</span>
          </div>
          <PerformanceHeatmap rows={monthlyRows} />
        </article>

        <article className="performance-card table-card">
          <div className="performance-card-heading">
            <strong>전략 성과 비교</strong>
            <span>Top 8</span>
          </div>
          <PerformanceTable rows={strategyRows} />
        </article>

        <article className="performance-card">
          <div className="performance-card-heading">
            <strong>심볼별 수익 기여도</strong>
            <span>{symbolRows.length}개 심볼</span>
          </div>
          <SymbolContributionList rows={symbolRows} />
        </article>
      </div>
    </section>
  );
}

function PerformanceStatCard({
  label,
  tone = "neutral",
  value,
}: {
  label: string;
  tone?: "neutral" | "positive" | "negative";
  value: string;
}) {
  return (
    <article className={`performance-stat ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function PerformanceLineChart({
  series,
}: {
  series: Array<{ color: string; label: string; points: number[] }>;
}) {
  const width = 720;
  const height = 260;
  const values = series.flatMap((item) => item.points);
  const minValue = Math.min(0, ...values);
  const maxValue = Math.max(1, ...values);
  const range = Math.max(maxValue - minValue, 1);
  const maxLength = Math.max(2, ...series.map((item) => item.points.length));
  const yFor = (value: number) => height - 28 - ((value - minValue) / range) * (height - 56);
  const xFor = (index: number) => 38 + (index / Math.max(maxLength - 1, 1)) * (width - 70);
  return (
    <div className="performance-chart">
      <svg aria-hidden="true" viewBox={`0 0 ${width} ${height}`}>
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const y = 18 + ratio * (height - 48);
          return <line key={ratio} x1="36" x2={width - 24} y1={y} y2={y} />;
        })}
        {series.map((item) => {
          const points = item.points.length ? item.points : [0];
          const line = points.map((value, index) => `${xFor(index)},${yFor(value)}`).join(" ");
          const area = `${xFor(0)},${yFor(0)} ${line} ${xFor(points.length - 1)},${yFor(0)}`;
          return (
            <g key={item.label}>
              <polygon fill={item.color} points={area} />
              <polyline points={line} stroke={item.color} />
            </g>
          );
        })}
      </svg>
      <div className="chart-legend">
        {series.map((item) => (
          <span key={item.label}>
            <b style={{ backgroundColor: item.color }} />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function ContributionRing({ rows }: { rows: PerformanceModeRow[] }) {
  const positiveRows = rows.filter((row) => row.totalReturnPct > 0);
  const total = positiveRows.reduce((sum, row) => sum + row.totalReturnPct, 0);
  const activeRows = rows.filter((row) => row.runCount > 0);
  const averageReturnPct = average(activeRows.map((row) => row.totalReturnPct));
  return (
    <div className="contribution-ring">
      <div className="ring-visual">
        <span>평균 수익</span>
        <strong>{formatPercent(averageReturnPct)}</strong>
      </div>
      <div className="ring-list">
        {rows.map((row) => (
          <div key={row.mode}>
            <span><b style={{ backgroundColor: row.color }} />{row.label}</span>
            <strong>{formatPercent(row.totalReturnPct)}</strong>
            <small>{total > 0 ? `${formatNumber((Math.max(row.totalReturnPct, 0) / total) * 100)}%` : "0%"}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

function PerformanceHeatmap({ rows }: { rows: PerformanceMonthRow[] }) {
  if (rows.length === 0) {
    return <p className="muted">성과 데이터가 없습니다.</p>;
  }
  return (
    <div className="performance-heatmap">
      <div />
      {rows[0].months.map((month) => (
        <strong key={month}>{month}</strong>
      ))}
      {rows.map((row) => (
        <div className="heatmap-row" key={row.mode}>
          <span>{row.label}</span>
          {row.values.map((value, index) => (
            <b className={value >= 0 ? "positive" : "negative"} key={`${row.mode}-${row.months[index]}`}>
              {formatPercent(value)}
            </b>
          ))}
        </div>
      ))}
    </div>
  );
}

function PerformanceTable({ rows }: { rows: PerformanceStrategyRow[] }) {
  if (rows.length === 0) {
    return <p className="muted">전략 성과 데이터가 없습니다.</p>;
  }
  return (
    <div className="performance-table-wrap">
      <table className="performance-table">
        <thead>
          <tr>
            <th>전략명</th>
            <th>모드</th>
            <th>수익률</th>
            <th>MDD</th>
            <th>샤프</th>
            <th>승률</th>
            <th>거래 수</th>
            <th>최근 실행</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.strategy}-${row.mode}`}>
              <td>{row.strategy}</td>
              <td>{row.modeLabel}</td>
              <td className={row.totalReturnPct >= 0 ? "positive" : "negative"}>{formatPercent(row.totalReturnPct)}</td>
              <td className={row.maxDrawdownPct < 0 ? "negative" : ""}>{formatPercent(row.maxDrawdownPct)}</td>
              <td>{formatMetricValue(row.sharpeRatio)}</td>
              <td>{formatPercent(row.winRatePct)}</td>
              <td>{formatNumber(row.tradeCount)}</td>
              <td>{formatTimestamp(row.lastRunAt)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SymbolContributionList({ rows }: { rows: PerformanceSymbolRow[] }) {
  if (rows.length === 0) {
    return <p className="muted">심볼별 성과 데이터가 없습니다.</p>;
  }
  return (
    <div className="symbol-contribution-list">
      {rows.map((row) => (
        <div key={row.symbol}>
          <span>{row.symbol}</span>
          <strong className={row.totalReturnPct >= 0 ? "positive" : "negative"}>{formatPercent(row.totalReturnPct)}</strong>
          <b>
            <i style={{ width: `${Math.max(row.weightPct, 3)}%` }} />
          </b>
          <small>{formatNumber(row.runCount)}회</small>
        </div>
      ))}
    </div>
  );
}

function DataSection({
  candles,
  dataQuery,
  dataLoadingMode,
  dataSyncResult,
  marketStatus,
  onLoadCandles,
  onLoadOlderCandles,
  setDataQuery,
  symbolOptions,
  timeframeOptions,
}: {
  candles: Candle[];
  dataQuery: DataQueryState;
  dataLoadingMode: DataLoadingMode;
  dataSyncResult: MarketDataSyncResult | null;
  marketStatus: MarketStatus | null;
  onLoadCandles: () => void;
  onLoadOlderCandles: () => void;
  setDataQuery: (value: DataQueryState) => void;
  symbolOptions: string[];
  timeframeOptions: string[];
}) {
  const isLoading = dataLoadingMode !== "idle";
  const earliest = candles[0];
  const latest = candles[candles.length - 1];
  const submitLoad = (event: FormEvent) => {
    event.preventDefault();
    onLoadCandles();
  };
  return (
    <section className="core-panel core-panel-main">
      <div className="panel-heading">
        <div>
          <p className="core-eyebrow">데이터</p>
          <h2>시장 데이터</h2>
        </div>
      </div>
      <form className="sync-panel data-load-panel" onSubmit={submitLoad}>
        <div className="sync-panel-heading">
          <div>
            <p className="core-eyebrow">데이터 로드</p>
            <h3>캔들 조회</h3>
          </div>
          <button disabled={isLoading} type="submit">
            {isLoading ? "불러오는 중" : "조회"}
          </button>
        </div>
        <div className="form-grid sync-grid">
          <label>
            심볼
            <select
              disabled={isLoading}
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
              disabled={isLoading}
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
            시작일
            <input
              disabled={isLoading}
              step={timeframeStepSeconds(dataQuery.timeframe)}
              type="datetime-local"
              value={dataQuery.start_at}
              onChange={(event) => setDataQuery({ ...dataQuery, start_at: event.target.value })}
              onBlur={() =>
                setDataQuery({
                  ...dataQuery,
                  start_at: snapDateTimeInput(dataQuery.start_at, dataQuery.timeframe, "start"),
                })
              }
            />
          </label>
          <label>
            종료일
            <input
              disabled={isLoading}
              step={timeframeStepSeconds(dataQuery.timeframe)}
              type="datetime-local"
              value={dataQuery.end_at}
              onChange={(event) => setDataQuery({ ...dataQuery, end_at: event.target.value })}
              onBlur={() =>
                setDataQuery({
                  ...dataQuery,
                  end_at: snapDateTimeInput(dataQuery.end_at, dataQuery.timeframe, "end"),
                })
              }
            />
          </label>
          <label>
            조회 개수
            <input
              disabled={isLoading}
              max="5000"
              min="1"
              type="number"
              value={dataQuery.limit}
              onChange={(event) => setDataQuery({ ...dataQuery, limit: event.target.value })}
            />
          </label>
        </div>
        {isLoading ? (
          <div className="loading-strip" role="status">
            <span className="loading-spinner" aria-hidden="true" />
            <strong>{dataLoadingMessage(dataLoadingMode)}</strong>
          </div>
        ) : null}
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
      <MarketChart
        candles={candles}
        loading={isLoading}
        loadingText={dataLoadingMessage(dataLoadingMode)}
        symbol={dataQuery.symbol}
        timeframe={dataQuery.timeframe}
      />
      <div className="chart-actions">
        <button disabled={!candles.length || isLoading} onClick={onLoadOlderCandles} type="button">
          {dataLoadingMode === "appending" ? "이어 붙이는 중" : "이전 구간 더 보기"}
        </button>
        <small>
          {candles.length > 0
            ? `${formatTimestamp(earliest?.timestamp)} - ${formatTimestamp(latest?.timestamp)}`
            : "조회된 캔들이 없습니다"}
        </small>
      </div>
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
  loading = false,
  loadingText = "불러오는 중",
  symbol,
  timeframe,
}: {
  candles: Candle[];
  loading?: boolean;
  loadingText?: string;
  symbol: string;
  timeframe: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const visibleRangeRef = useRef<IRange<Time> | null>(null);

  useEffect(() => {
    visibleRangeRef.current = null;
  }, [symbol, timeframe]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || candles.length === 0 || import.meta.env.MODE === "test") {
      return;
    }

    let chart: IChartApi | null = null;
    let series: ISeriesApi<"Candlestick"> | null = null;
    let averageSeries: Array<ISeriesApi<"Line">> = [];
    let resizeObserver: ResizeObserver | null = null;
    let visibleRangeAnimationFrame = 0;
    let acceptsVisibleRangeChanges = false;
    let disposed = false;
    const handleVisibleRangeChange = (range: IRange<Time> | null) => {
      if (acceptsVisibleRangeChanges && range) {
        visibleRangeRef.current = range;
      }
    };

    const renderChart = async () => {
      const { CandlestickSeries, ColorType, LineSeries, LineStyle, createChart } = await import("lightweight-charts");
      if (disposed || !containerRef.current) {
        return;
      }

      chart = createChart(containerRef.current, {
        autoSize: false,
        height: marketChartHeight,
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
          scaleMargins: {
            top: 0.05,
            bottom: 0.08,
          },
        },
        leftPriceScale: {
          visible: true,
          borderColor: "rgba(46, 62, 91, 0.8)",
          scaleMargins: {
            top: 0.05,
            bottom: 0.08,
          },
        },
        timeScale: {
          borderColor: "rgba(46, 62, 91, 0.8)",
          timeVisible: true,
          secondsVisible: false,
          tickMarkFormatter: (time: Time) => formatChartAxisTick(time),
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
      const rsiSeries = chart.addSeries(LineSeries, {
        color: rsiIndicator.color,
        lineWidth: rsiIndicator.width,
        priceLineVisible: false,
        lastValueVisible: true,
        crosshairMarkerVisible: true,
        priceScaleId: "left",
        autoscaleInfoProvider: () => ({
          priceRange: {
            minValue: 0,
            maxValue: 100,
          },
        }),
      });
      rsiSeries.setData(toRsiSeriesData(candles, rsiIndicator.period));
      rsiSeries.createPriceLine({
        price: 70,
        color: "rgba(255, 81, 79, 0.62)",
        lineStyle: LineStyle.Dashed,
        lineWidth: 1,
        axisLabelVisible: false,
      });
      rsiSeries.createPriceLine({
        price: 50,
        color: "rgba(147, 161, 184, 0.32)",
        lineStyle: LineStyle.Dotted,
        lineWidth: 1,
        axisLabelVisible: false,
      });
      rsiSeries.createPriceLine({
        price: 30,
        color: "rgba(49, 209, 125, 0.62)",
        lineStyle: LineStyle.Dashed,
        lineWidth: 1,
        axisLabelVisible: false,
      });
      const savedRange = visibleRangeRef.current;
      if (savedRange && timeRangeOverlapsCandles(savedRange, candles)) {
        chart.timeScale().setVisibleRange(savedRange);
      } else {
        chart.timeScale().fitContent();
      }
      chart.timeScale().subscribeVisibleTimeRangeChange(handleVisibleRangeChange);
      visibleRangeAnimationFrame = window.requestAnimationFrame(() => {
        acceptsVisibleRangeChanges = true;
      });

      const resize = () => {
        const width = containerRef.current?.clientWidth ?? 0;
        if (chart && width > 0) {
          chart.resize(width, marketChartHeight);
        }
      };
      resize();

      resizeObserver = new ResizeObserver(resize);
      resizeObserver.observe(containerRef.current);
    };

    void renderChart();

    return () => {
      disposed = true;
      if (chart && acceptsVisibleRangeChanges) {
        visibleRangeRef.current = chart.timeScale().getVisibleRange() ?? visibleRangeRef.current;
      }
      if (visibleRangeAnimationFrame) {
        window.cancelAnimationFrame(visibleRangeAnimationFrame);
      }
      chart?.timeScale().unsubscribeVisibleTimeRangeChange(handleVisibleRangeChange);
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
            <span>
              <b style={{ backgroundColor: rsiIndicator.color }} />
              {rsiIndicator.label}
            </span>
          </div>
        </div>
      </div>
      <div className="market-chart" ref={containerRef}>
        {loading ? (
          <div className="chart-loading" role="status">
            <span className="loading-spinner" aria-hidden="true" />
            <strong>{loadingText}</strong>
          </div>
        ) : null}
        {candles.length === 0 && !loading ? <span className="chart-empty">불러온 캔들 데이터가 없습니다</span> : null}
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
              step={timeframeStepSeconds(form.timeframe)}
              type="datetime-local"
              value={form.start_at}
              onChange={(event) => setForm({ ...form, start_at: event.target.value })}
              onBlur={() =>
                setForm({
                  ...form,
                  start_at: snapDateTimeInput(form.start_at, form.timeframe, "start"),
                })
              }
            />
          </label>
          <label>
            종료일
            <input
              step={timeframeStepSeconds(form.timeframe)}
              type="datetime-local"
              value={form.end_at}
              onChange={(event) => setForm({ ...form, end_at: event.target.value })}
              onBlur={() =>
                setForm({
                  ...form,
                  end_at: snapDateTimeInput(form.end_at, form.timeframe, "end"),
                })
              }
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
          <h2>{run ? `${formatMode(run.mode)} · ${shortId(run.run_id)}` : "선택된 실행 없음"}</h2>
          {run ? (
            <div className="detail-heading-meta">
              <StatusPill value={run.status} />
              <span>{run.strategy?.name ?? "전략 미지정"}</span>
            </div>
          ) : null}
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
          {activeTab === "orders" ? <OrdersDetail orders={orders} /> : null}
          {activeTab === "positions" ? <PositionsDetail positions={positions} /> : null}
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
  const returnValue = Number(run.metrics.total_return_pct ?? 0);
  const dataIssues = marketData?.issues ?? [];
  return (
    <div className="detail-section">
      <div className="detail-stat-grid">
        <DetailStat label="상태" value={formatRunStatus(run.status)} />
        <DetailStat label="종료 자산" value={formatMetricValue(run.metrics.ending_equity)} />
        <DetailStat
          label="수익률"
          tone={returnValue >= 0 ? "positive" : "negative"}
          value={formatMetricValue(run.metrics.total_return_pct, "%")}
        />
        <DetailStat label="거래 수" value={formatMetricValue(run.metrics.trade_count ?? run.orders_count)} />
        <DetailStat label="캔들 수" value={formatMetricValue(marketData?.candle_count)} />
        <DetailStat label="데이터" value={formatDataStatus(marketData?.sync_status ?? "-")} />
      </div>
      <div className="detail-card">
        <div className="detail-card-heading">
          <strong>실행 컨텍스트</strong>
          <small>{formatRange(run.started_at, run.ended_at)}</small>
        </div>
        <div className="detail-list flush">
          <DetailLine label="전략" value={run.strategy?.name ?? "-"} />
          <DetailLine label="심볼" value={symbol} />
          <DetailLine label="타임프레임" value={run.config?.timeframe ?? marketData?.timeframe ?? "-"} />
          <DetailLine label="요청 기간" value={formatRange(run.config?.start_at, run.config?.end_at)} />
          <DetailLine
            label="데이터 범위"
            value={formatRange(marketData?.effective_start_at, marketData?.effective_end_at)}
          />
          <DetailLine label="데이터 상태" value={formatDataStatus(marketData?.sync_status ?? "-")} />
        </div>
      </div>
      {dataIssues.length ? (
        <div className="detail-issues">
          {dataIssues.map((issue) => (
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
  const headlineKeys = ["ending_equity", "total_return_pct", "max_drawdown_pct", "trade_count", "win_rate_pct", "exposure_pct"];
  const headlineEntries = headlineKeys
    .filter((key) => metrics[key] !== undefined)
    .map((key) => [key, metrics[key]] as const);
  const tableEntries = entries.filter(([key]) => !headlineKeys.includes(key));
  return (
    <div className="detail-section">
      {headlineEntries.length > 0 ? (
        <div className="detail-stat-grid">
          {headlineEntries.map(([key, value]) => (
            <DetailStat
              key={key}
              label={formatMetricLabel(key)}
              tone={metricTone(key, value)}
              value={formatMetricDisplay(key, value)}
            />
          ))}
        </div>
      ) : (
        <p className="muted">지표가 없습니다.</p>
      )}
      {tableEntries.length > 0 ? (
        <div className="detail-table-wrap">
          <table className="detail-table">
            <thead>
              <tr>
                <th>지표</th>
                <th>값</th>
              </tr>
            </thead>
            <tbody>
              {tableEntries.map(([key, value]) => (
                <tr key={key}>
                  <td>{formatMetricLabel(key)}</td>
                  <td>{formatMetricDisplay(key, value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}

function OrdersDetail({ orders }: { orders: unknown[] }) {
  const records = orders.map(asRecord);
  const filled = records.filter((order) => isOrderStatus(order, ["filled", "closed", "complete", "completed"])).length;
  const open = records.filter((order) => isOrderStatus(order, ["open", "pending", "submitted", "partially_filled"])).length;
  const canceled = records.filter((order) => isOrderStatus(order, ["canceled", "cancelled", "rejected", "failed"])).length;
  const latestOrders = [...records].sort(compareRecordTimestamp("created_at")).slice(0, 6);
  return (
    <div className="detail-section">
      <div className="detail-stat-grid">
        <DetailStat label="총 주문" value={formatNumber(records.length)} />
        <DetailStat label="체결" tone="positive" value={formatNumber(filled)} />
        <DetailStat label="대기" value={formatNumber(open)} />
        <DetailStat label="취소/실패" tone={canceled > 0 ? "negative" : "neutral"} value={formatNumber(canceled)} />
      </div>
      {records.length === 0 ? (
        <EmptyDetailState message="주문이 없습니다." />
      ) : (
        <>
          <div className="detail-table-wrap">
            <table className="detail-table">
              <thead>
                <tr>
                  <th>주문 ID</th>
                  <th>심볼</th>
                  <th>유형</th>
                  <th>방향</th>
                  <th>수량</th>
                  <th>주문가</th>
                  <th>체결가</th>
                  <th>상태</th>
                  <th>시간</th>
                </tr>
              </thead>
              <tbody>
                {records.map((order, index) => (
                  <tr key={recordText(order, ["order_id"], `order-${index}`)}>
                    <td>{shortId(recordText(order, ["order_id"], "-"))}</td>
                    <td>{formatInstrument(recordText(order, ["instrument_id", "symbol"], "-"))}</td>
                    <td>{formatOrderType(recordText(order, ["order_type", "type"], "-"))}</td>
                    <td>
                      <span className={`side-pill ${sideClass(recordText(order, ["side"], ""))}`}>
                        {formatOrderSide(recordText(order, ["side"], "-"))}
                      </span>
                    </td>
                    <td>{formatMetricValue(recordNumber(order, ["filled_quantity", "quantity"]))}</td>
                    <td>{formatMetricValue(recordNumber(order, ["requested_price", "price"]))}</td>
                    <td>{formatMetricValue(recordNumber(order, ["average_fill_price", "avg_price"]))}</td>
                    <td>
                      <StatusPill value={recordText(order, ["status"], "-")} />
                    </td>
                    <td>{formatTimestamp(recordText(order, ["filled_at", "updated_at", "created_at"], null))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="detail-card">
            <div className="detail-card-heading">
              <strong>주문 활동 타임라인</strong>
              <small>최근 {latestOrders.length}건</small>
            </div>
            <div className="detail-timeline">
              {latestOrders.map((order, index) => (
                <article key={`${recordText(order, ["order_id"], "order")}-${index}`}>
                  <span>{formatTimestamp(recordText(order, ["created_at", "updated_at", "filled_at"], null))}</span>
                  <strong>
                    {formatInstrument(recordText(order, ["instrument_id", "symbol"], "-"))} ·{" "}
                    {formatOrderSide(recordText(order, ["side"], "-"))}
                  </strong>
                  <small>
                    {formatOrderStatus(recordText(order, ["status"], "-"))} · 수량{" "}
                    {formatMetricValue(recordNumber(order, ["filled_quantity", "quantity"]))}
                  </small>
                </article>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function PositionsDetail({ positions }: { positions: unknown[] }) {
  const records = positions.map(asRecord);
  const openPositions = records.filter((position) => Math.abs(recordNumber(position, ["quantity"]) ?? 0) > 0);
  const realizedPnl = records.reduce((sum, position) => sum + (recordNumber(position, ["realized_pnl", "pnl"]) ?? 0), 0);
  const notionals = records.map((position) => ({
    instrument: formatInstrument(recordText(position, ["instrument_id", "symbol"], "-")),
    notional: Math.abs((recordNumber(position, ["quantity"]) ?? 0) * (recordNumber(position, ["average_price", "entry_price"]) ?? 0)),
  }));
  const totalNotional = notionals.reduce((sum, item) => sum + item.notional, 0);
  const selectedPosition = openPositions[0] ?? records[0];
  return (
    <div className="detail-section">
      <div className="detail-stat-grid">
        <DetailStat label="총 포지션" value={formatNumber(records.length)} />
        <DetailStat label="오픈" tone={openPositions.length > 0 ? "positive" : "neutral"} value={formatNumber(openPositions.length)} />
        <DetailStat label="실현 손익" tone={realizedPnl >= 0 ? "positive" : "negative"} value={formatMetricValue(realizedPnl)} />
        <DetailStat label="노출 금액" value={formatMetricValue(totalNotional)} />
      </div>
      {records.length === 0 ? (
        <EmptyDetailState message="포지션이 없습니다." />
      ) : (
        <>
          <div className="detail-table-wrap">
            <table className="detail-table">
              <thead>
                <tr>
                  <th>심볼</th>
                  <th>수량</th>
                  <th>평균가</th>
                  <th>노출</th>
                  <th>실현 손익</th>
                  <th>업데이트</th>
                </tr>
              </thead>
              <tbody>
                {records.map((position, index) => {
                  const quantity = recordNumber(position, ["quantity"]) ?? 0;
                  const averagePrice = recordNumber(position, ["average_price", "entry_price"]) ?? 0;
                  return (
                    <tr key={`${recordText(position, ["instrument_id", "symbol"], "position")}-${index}`}>
                      <td>{formatInstrument(recordText(position, ["instrument_id", "symbol"], "-"))}</td>
                      <td>{formatMetricValue(quantity)}</td>
                      <td>{formatMetricValue(averagePrice)}</td>
                      <td>{formatMetricValue(Math.abs(quantity * averagePrice))}</td>
                      <td>{formatMetricValue(recordNumber(position, ["realized_pnl", "pnl"]))}</td>
                      <td>{formatTimestamp(recordText(position, ["updated_at", "opened_at"], null))}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="detail-split">
            <div className="detail-card">
              <div className="detail-card-heading">
                <strong>선택 포지션 상세</strong>
                <small>{selectedPosition ? formatInstrument(recordText(selectedPosition, ["instrument_id", "symbol"], "-")) : "-"}</small>
              </div>
              {selectedPosition ? (
                <div className="detail-list flush">
                  <DetailLine label="수량" value={formatMetricValue(recordNumber(selectedPosition, ["quantity"]))} />
                  <DetailLine label="평균가" value={formatMetricValue(recordNumber(selectedPosition, ["average_price", "entry_price"]))} />
                  <DetailLine label="실현 손익" value={formatMetricValue(recordNumber(selectedPosition, ["realized_pnl", "pnl"]))} />
                  <DetailLine label="오픈 시각" value={formatTimestamp(recordText(selectedPosition, ["opened_at"], null))} />
                </div>
              ) : null}
            </div>
            <div className="detail-card">
              <div className="detail-card-heading">
                <strong>노출 분포</strong>
                <small>{formatMetricValue(totalNotional)}</small>
              </div>
              <div className="exposure-list">
                {notionals.map((item) => (
                  <div key={item.instrument}>
                    <span>{item.instrument}</span>
                    <b>
                      <i style={{ width: `${totalNotional > 0 ? Math.max((item.notional / totalNotional) * 100, 3) : 0}%` }} />
                    </b>
                    <em>{formatMetricValue(item.notional)}</em>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function RunLogsDetail({ logs }: { logs: OperationLog[] }) {
  const selectedLog = logs.find((log) => log.severity === "error") ?? logs[0];
  return (
    <div className="detail-section">
      <div className="detail-stat-grid">
        <DetailStat label="전체" value={formatNumber(logs.length)} />
        <DetailStat label="오류" tone={logs.some((log) => log.severity === "error") ? "negative" : "neutral"} value={formatNumber(logs.filter((log) => log.severity === "error").length)} />
        <DetailStat label="경고" value={formatNumber(logs.filter((log) => log.severity === "warning").length)} />
        <DetailStat label="정보" value={formatNumber(logs.filter((log) => log.severity === "info").length)} />
      </div>
      {logs.length === 0 ? (
        <EmptyDetailState message="이 실행에 연결된 로그가 없습니다." />
      ) : (
        <div className="detail-split logs-split">
          <div className="detail-table-wrap">
            <table className="detail-table">
              <thead>
                <tr>
                  <th>시간</th>
                  <th>심각도</th>
                  <th>소스</th>
                  <th>메시지</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr className={selectedLog?.log_id === log.log_id ? "is-selected" : ""} key={log.log_id}>
                    <td>{formatTimestamp(log.recorded_at)}</td>
                    <td><span className={`severity ${log.severity}`}>{formatSeverity(log.severity)}</span></td>
                    <td>{log.layer}</td>
                    <td>{log.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {selectedLog ? (
            <div className="detail-card">
              <div className="detail-card-heading">
                <strong>선택 로그 상세</strong>
                <span className={`severity ${selectedLog.severity}`}>{formatSeverity(selectedLog.severity)}</span>
              </div>
              <div className="detail-list flush">
                <DetailLine label="시간" value={formatTimestamp(selectedLog.recorded_at)} />
                <DetailLine label="소스" value={selectedLog.layer} />
                <DetailLine label="이벤트" value={formatEventType(selectedLog.event_type)} />
                <DetailLine label="메시지" value={selectedLog.message} />
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}

function DetailStat({
  label,
  tone = "neutral",
  value,
}: {
  label: string;
  tone?: "neutral" | "positive" | "negative";
  value: string;
}) {
  return (
    <article className={`detail-stat ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function StatusPill({ value }: { value?: string | null }) {
  const status = String(value ?? "-");
  return <span className={`status-pill ${status.toLowerCase()}`}>{formatStatusLabel(status)}</span>;
}

function EmptyDetailState({ message }: { message: string }) {
  return (
    <div className="empty-detail">
      <strong>{message}</strong>
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

function buildPerformanceSummary(runs: RunSummary[]) {
  const drawdowns = runs.map(runDrawdownPct).filter(Number.isFinite);
  const winRates = runs.map(runWinRatePct).filter(Number.isFinite);
  const sharpeValues = runs.map((run) => metricNumber(run.metrics.sharpe_ratio ?? run.metrics.sharpe)).filter(Number.isFinite);
  return {
    activeRunCount: runs.filter((run) => run.status === "running").length,
    maxDrawdownPct: drawdowns.length ? Math.min(...drawdowns) : 0,
    sharpeRatio: average(sharpeValues),
    totalReturnPct: aggregateRunReturnPct(runs),
    tradeCount: runs.reduce((sum, run) => sum + runTradeCount(run), 0),
    winRatePct: winRates.length ? average(winRates) : inferWinRatePct(runs),
  };
}

function buildModePerformanceRows(runs: RunSummary[]): PerformanceModeRow[] {
  return (["backtest", "sandbox", "live"] as const).map((mode) => {
    const modeRuns = runs.filter((run) => run.mode === mode);
    const drawdowns = modeRuns.map(runDrawdownPct).filter(Number.isFinite);
    const meta = performanceModeMeta[mode];
    return {
      color: meta.color,
      label: meta.label,
      maxDrawdownPct: drawdowns.length ? Math.min(...drawdowns) : 0,
      mode,
      runCount: modeRuns.length,
      totalReturnPct: aggregateRunReturnPct(modeRuns),
      tradeCount: modeRuns.reduce((sum, run) => sum + runTradeCount(run), 0),
      winRatePct: inferWinRatePct(modeRuns),
    };
  });
}

function buildStrategyPerformanceRows(runs: RunSummary[]): PerformanceStrategyRow[] {
  const groups = new Map<string, RunSummary[]>();
  for (const run of runs) {
    const strategy = run.strategy?.name ?? run.strategy?.strategy_id ?? "전략 미지정";
    const key = `${strategy}|${run.mode}`;
    groups.set(key, [...(groups.get(key) ?? []), run]);
  }
  return [...groups.entries()]
    .map(([key, groupRuns]) => {
      const [strategy, mode] = key.split("|") as [string, RunSummary["mode"]];
      const drawdowns = groupRuns.map(runDrawdownPct).filter(Number.isFinite);
      const sharpeValues = groupRuns
        .map((run) => metricNumber(run.metrics.sharpe_ratio ?? run.metrics.sharpe))
        .filter(Number.isFinite);
      const latest = [...groupRuns].sort((left, right) => Date.parse(right.started_at) - Date.parse(left.started_at))[0];
      return {
        lastRunAt: latest?.started_at ?? null,
        maxDrawdownPct: drawdowns.length ? Math.min(...drawdowns) : 0,
        mode,
        modeLabel: performanceModeMeta[mode]?.label ?? mode,
        runCount: groupRuns.length,
        sharpeRatio: average(sharpeValues),
        strategy,
        totalReturnPct: aggregateRunReturnPct(groupRuns),
        tradeCount: groupRuns.reduce((sum, run) => sum + runTradeCount(run), 0),
        winRatePct: inferWinRatePct(groupRuns),
      };
    })
    .sort((left, right) => right.totalReturnPct - left.totalReturnPct)
    .slice(0, 8);
}

function buildSymbolPerformanceRows(runs: RunSummary[]): PerformanceSymbolRow[] {
  const groups = new Map<string, RunSummary[]>();
  for (const run of runs) {
    const symbol = run.config?.symbols?.[0] ?? "심볼 없음";
    groups.set(symbol, [...(groups.get(symbol) ?? []), run]);
  }
  const rows = [...groups.entries()].map(([symbol, groupRuns]) => ({
    runCount: groupRuns.length,
    symbol,
    totalReturnPct: aggregateRunReturnPct(groupRuns),
    weightPct: 0,
  }));
  const totalWeight = rows.reduce((sum, row) => sum + Math.abs(row.totalReturnPct), 0);
  return rows
    .map((row) => ({
      ...row,
      weightPct: totalWeight > 0 ? (Math.abs(row.totalReturnPct) / totalWeight) * 100 : 0,
    }))
    .sort((left, right) => Math.abs(right.totalReturnPct) - Math.abs(left.totalReturnPct));
}

function buildMonthlyPerformanceRows(runs: RunSummary[]): PerformanceMonthRow[] {
  const monthKeys = [...new Set(runs.map((run) => monthKey(run.started_at)).filter(Boolean))].sort().slice(-6);
  if (monthKeys.length === 0) {
    return [];
  }
  return (["backtest", "sandbox", "live"] as const).map((mode) => {
    const modeRuns = runs.filter((run) => run.mode === mode);
    return {
      label: performanceModeMeta[mode].label,
      mode,
      months: monthKeys.map(formatMonthKey),
      values: monthKeys.map((key) => aggregateRunReturnPct(modeRuns.filter((run) => monthKey(run.started_at) === key))),
    };
  });
}

function buildCumulativePerformanceSeries(runs: RunSummary[]) {
  return (["backtest", "sandbox", "live"] as const).map((mode) => {
    const modeRuns = runs
      .filter((run) => run.mode === mode)
      .sort((left, right) => Date.parse(left.started_at) - Date.parse(right.started_at));
    const points = modeRuns.map((_, index) => aggregateRunReturnPct(modeRuns.slice(0, index + 1)));
    return {
      color: performanceModeMeta[mode].color,
      label: performanceModeMeta[mode].label,
      points: points.length ? points : [0],
    };
  });
}

function buildPerformanceInsights({
  logs,
  modeRows,
  runs,
  strategyRows,
}: {
  logs: OperationLog[];
  modeRows: PerformanceModeRow[];
  runs: RunSummary[];
  strategyRows: PerformanceStrategyRow[];
}) {
  const bestMode = [...modeRows].sort((left, right) => right.totalReturnPct - left.totalReturnPct)[0];
  const worstMode = [...modeRows].sort((left, right) => left.maxDrawdownPct - right.maxDrawdownPct)[0];
  const bestStrategy = strategyRows[0];
  const recentErrors = logs.filter((log) => log.severity === "error").length;
  return [
    {
      body: `${bestMode?.label ?? "전체"} 모드가 가장 높은 가중 수익률을 기록했습니다.`,
      mark: "T",
      title: "최고 성과 모드",
      tone: "positive",
      value: formatPercent(bestMode?.totalReturnPct ?? 0),
    },
    {
      body: `${worstMode?.label ?? "전체"} 구간에서 가장 큰 낙폭이 발생했습니다.`,
      mark: "D",
      title: "가장 큰 낙폭",
      tone: "negative",
      value: formatPercent(worstMode?.maxDrawdownPct ?? 0),
    },
    {
      body: bestStrategy ? `${bestStrategy.strategy} 전략이 현재 필터에서 가장 앞섭니다.` : "전략 성과 데이터가 아직 부족합니다.",
      mark: "S",
      title: "최고 전략",
      tone: "positive",
      value: bestStrategy ? formatPercent(bestStrategy.totalReturnPct) : "-",
    },
    {
      body: recentErrors > 0 ? "최근 로그에 오류가 있어 성과 해석 전 운영 상태 확인이 필요합니다." : "최근 오류 없이 성과 집계가 유지되고 있습니다.",
      mark: "L",
      title: "운영 상태",
      tone: recentErrors > 0 ? "negative" : "neutral",
      value: `${formatNumber(recentErrors)}개 오류`,
    },
    {
      body: `${runs.length}개 실행 기준으로 수익, 낙폭, 거래 수를 집계했습니다.`,
      mark: "R",
      title: "성과 요약",
      tone: "neutral",
      value: `${formatNumber(runs.length)}개 실행`,
    },
  ];
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
  return formatKstDateTime(date);
}

function formatChartTime(time: Time) {
  const date = timeToDate(time);
  return date === null ? String(time) : formatKstChartDate(date);
}

function formatChartAxisTick(time: Time) {
  const date = timeToDate(time);
  if (date === null) {
    return String(time);
  }
  const parts = getKstDateParts(date);
  if (parts.hour === "00" && parts.minute === "00") {
    return `${parts.month}-${parts.day}`;
  }
  return `${parts.hour}:${parts.minute}`;
}

function formatKstChartDate(date: Date) {
  const parts = getKstDateParts(date);
  return `${parts.hour}:${parts.minute} ${parts.shortYear}-${parts.month}-${parts.day}`;
}

function formatKstDateTime(date: Date) {
  const parts = getKstDateParts(date);
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}

function getKstDateParts(date: Date) {
  const parts = new Intl.DateTimeFormat("en", {
    day: "2-digit",
    hour: "2-digit",
    hour12: false,
    hourCycle: "h23",
    minute: "2-digit",
    month: "2-digit",
    second: "2-digit",
    timeZone: "Asia/Seoul",
    year: "numeric",
  }).formatToParts(date);
  const part = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((item) => item.type === type)?.value ?? "00";
  const year = part("year");
  return {
    day: part("day"),
    hour: part("hour"),
    minute: part("minute"),
    month: part("month"),
    second: part("second"),
    shortYear: year.slice(-2),
    year,
  };
}

function timeToDate(time: Time) {
  if (typeof time === "number") {
    return new Date(time * 1000);
  }
  if (typeof time === "string") {
    const date = new Date(time);
    return Number.isNaN(date.getTime()) ? null : date;
  }
  return new Date(Date.UTC(time.year, time.month - 1, time.day));
}

function timeRangeOverlapsCandles(range: IRange<Time>, candles: Candle[]) {
  const from = timeToDate(range.from);
  const to = timeToDate(range.to);
  if (from === null || to === null || candles.length === 0) {
    return false;
  }
  const timestamps = candles
    .map((candle) => new Date(candle.timestamp).getTime())
    .filter((timestamp) => Number.isFinite(timestamp));
  if (timestamps.length === 0) {
    return false;
  }
  const first = Math.min(...timestamps);
  const last = Math.max(...timestamps);
  return from.getTime() <= last && to.getTime() >= first;
}

type TimeBoundary = "start" | "end";

function toApiDateTime(value: string, timeframe?: string, boundary: TimeBoundary = "start") {
  if (!value) {
    return null;
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return alignDateToTimeframe(date, timeframe, boundary).toISOString();
}

function buildAlignedDateRange(startValue: string, endValue: string, timeframe: string) {
  const startAt = toApiDateTime(startValue, timeframe, "start");
  let endAt = toApiDateTime(endValue, timeframe, "end");
  if (startAt && endAt && new Date(endAt).getTime() < new Date(startAt).getTime()) {
    endAt = startAt;
  }
  return { start_at: startAt, end_at: endAt };
}

function snapDateTimeInput(value: string, timeframe: string, boundary: TimeBoundary) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return formatDateTimeInput(alignDateToTimeframe(date, timeframe, boundary));
}

function alignDateToTimeframe(date: Date, timeframe?: string, boundary: TimeBoundary = "start") {
  const seconds = timeframeToSeconds(timeframe);
  if (!seconds) {
    return date;
  }
  const interval = seconds * 1000;
  const timestamp = date.getTime();
  const remainder = ((timestamp % interval) + interval) % interval;
  if (remainder === 0) {
    return date;
  }
  return new Date(boundary === "start" ? timestamp + interval - remainder : timestamp - remainder);
}

function timeframeStepSeconds(timeframe: string) {
  return timeframeToSeconds(timeframe) ?? 60;
}

function timeframeToSeconds(timeframe?: string) {
  const match = /^(\d+)([mhd])$/.exec(timeframe?.trim() ?? "");
  if (!match) {
    return null;
  }
  const amount = Number(match[1]);
  if (!Number.isFinite(amount) || amount <= 0) {
    return null;
  }
  switch (match[2]) {
    case "m":
      return amount * 60;
    case "h":
      return amount * 60 * 60;
    case "d":
      return amount * 24 * 60 * 60;
    default:
      return null;
  }
}

function formatDateTimeInput(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function buildMarketDataPayload(
  queryState: DataQueryState,
  options: { endAtOverride?: string | null; startAtOverride?: string | null } = {},
) {
  const startAt =
    "startAtOverride" in options ? options.startAtOverride : toApiDateTime(queryState.start_at, queryState.timeframe, "start");
  let endAt =
    "endAtOverride" in options ? options.endAtOverride : toApiDateTime(queryState.end_at, queryState.timeframe, "end");
  if (startAt && endAt && new Date(endAt).getTime() < new Date(startAt).getTime()) {
    endAt = startAt;
  }
  return {
    symbol: queryState.symbol,
    timeframe: queryState.timeframe,
    start_at: startAt,
    end_at: endAt,
    limit: normalizeCandleLimit(queryState.limit),
  };
}

function buildMarketDataQuery(
  queryState: DataQueryState,
  options: { endAtOverride?: string | null; startAtOverride?: string | null } = {},
) {
  const payload = buildMarketDataPayload(queryState, options);
  const query = new URLSearchParams({
    symbol: payload.symbol,
    timeframe: payload.timeframe,
    limit: String(payload.limit),
  });
  if (payload.start_at) {
    query.set("start_at", payload.start_at);
  }
  if (payload.end_at) {
    query.set("end_at", payload.end_at);
  }
  return query;
}

function normalizeCandleLimit(value: string) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 1) {
    return defaultCandleQueryLimit;
  }
  return Math.min(Math.trunc(parsed), maxCandleQueryLimit);
}

function formatNumber(value: number) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);
}

function formatPercent(value: number) {
  return `${value >= 0 ? "+" : ""}${formatNumber(value)}%`;
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

function metricNumber(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : NaN;
  }
  return NaN;
}

function average(values: number[]) {
  return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
}

function aggregateRunReturnPct(runs: RunSummary[]) {
  const samples = runs
    .map((run) => ({
      initialCapital: runInitialCapital(run),
      returnPct: runReturnPct(run),
    }))
    .filter((sample) => Number.isFinite(sample.returnPct));
  if (samples.length === 0) {
    return 0;
  }
  const weightedSamples = samples.filter((sample) => Number.isFinite(sample.initialCapital) && sample.initialCapital > 0);
  if (weightedSamples.length === samples.length) {
    const totalCapital = weightedSamples.reduce((sum, sample) => sum + sample.initialCapital, 0);
    if (totalCapital > 0) {
      return weightedSamples.reduce((sum, sample) => sum + sample.returnPct * sample.initialCapital, 0) / totalCapital;
    }
  }
  return average(samples.map((sample) => sample.returnPct));
}

function runReturnPct(run: RunSummary) {
  return metricNumber(run.metrics.total_return_pct ?? run.metrics.return_pct ?? run.metrics.pnl_pct);
}

function runInitialCapital(run: RunSummary) {
  const configInitialCash = metricNumber(run.config?.initial_cash);
  if (Number.isFinite(configInitialCash) && configInitialCash > 0) {
    return configInitialCash;
  }
  const metricInitialCash = metricNumber(
    run.metrics.initial_cash ?? run.metrics.initial_equity ?? run.metrics.starting_equity ?? run.metrics.starting_balance,
  );
  if (Number.isFinite(metricInitialCash) && metricInitialCash > 0) {
    return metricInitialCash;
  }
  const endingEquity = metricNumber(run.metrics.ending_equity ?? run.metrics.equity);
  const returnPct = runReturnPct(run);
  if (Number.isFinite(endingEquity) && endingEquity > 0 && Number.isFinite(returnPct) && returnPct > -100) {
    return endingEquity / (1 + returnPct / 100);
  }
  return NaN;
}

function runDrawdownPct(run: RunSummary) {
  const value = metricNumber(run.metrics.max_drawdown_pct ?? run.metrics.drawdown_pct ?? run.metrics.mdd_pct);
  return Number.isFinite(value) ? -Math.abs(value) : 0;
}

function runWinRatePct(run: RunSummary) {
  return metricNumber(run.metrics.win_rate_pct ?? run.metrics.win_rate);
}

function runTradeCount(run: RunSummary) {
  const count = metricNumber(run.metrics.trade_count);
  return Number.isFinite(count) ? count : run.orders_count;
}

function inferWinRatePct(runs: RunSummary[]) {
  if (runs.length === 0) {
    return 0;
  }
  const explicitRates = runs.map(runWinRatePct).filter(Number.isFinite);
  if (explicitRates.length > 0) {
    return average(explicitRates);
  }
  return (runs.filter((run) => runReturnPct(run) > 0).length / runs.length) * 100;
}

function monthKey(value: string | null | undefined) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}`;
}

function formatMonthKey(value: string) {
  const [, month] = value.split("-");
  return `${Number(month)}월`;
}

function formatMetricDisplay(key: string, value: unknown) {
  return formatMetricValue(value, key.endsWith("_pct") ? "%" : "");
}

function metricTone(key: string, value: unknown) {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return "neutral";
  }
  if (key.includes("drawdown")) {
    return numericValue > 0 ? "negative" : "neutral";
  }
  if (key.includes("return") || key.includes("pnl") || key.includes("equity")) {
    return numericValue >= 0 ? "positive" : "negative";
  }
  return "neutral";
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

function dataLoadingMessage(mode: DataLoadingMode) {
  switch (mode) {
    case "loading":
      return "백필 확인 후 차트를 갱신하는 중";
    case "appending":
      return "이전 구간을 불러와 이어 붙이는 중";
    default:
      return "준비됨";
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

function formatStatusLabel(value?: string | null) {
  const normalized = String(value ?? "").toLowerCase();
  switch (normalized) {
    case "pending":
    case "submitted":
    case "open":
      return "대기";
    case "running":
      return "실행 중";
    case "completed":
    case "complete":
      return "완료";
    case "filled":
      return "체결";
    case "partially_filled":
    case "partial":
      return "부분 체결";
    case "failed":
    case "rejected":
      return "실패";
    case "stopped":
      return "중지됨";
    case "canceled":
    case "cancelled":
      return "취소";
    default:
      return value ?? "-";
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

function asRecord(value: unknown): UnknownRecord {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as UnknownRecord) : {};
}

function recordText(record: UnknownRecord, keys: string[], fallback: string): string;
function recordText(record: UnknownRecord, keys: string[], fallback: null): string | null;
function recordText(record: UnknownRecord, keys: string[], fallback: string | null = "-") {
  for (const key of keys) {
    const value = record[key];
    if (value !== null && value !== undefined && value !== "") {
      return String(value);
    }
  }
  return fallback;
}

function recordNumber(record: UnknownRecord, keys: string[]) {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
    if (typeof value === "string" && value.trim()) {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }
  }
  return null;
}

function compareRecordTimestamp(key: string) {
  return (left: UnknownRecord, right: UnknownRecord) => {
    const leftTime = new Date(recordText(left, [key], null) ?? "").getTime();
    const rightTime = new Date(recordText(right, [key], null) ?? "").getTime();
    return (Number.isFinite(rightTime) ? rightTime : 0) - (Number.isFinite(leftTime) ? leftTime : 0);
  };
}

function isOrderStatus(order: UnknownRecord, statuses: string[]) {
  const status = recordText(order, ["status"], "").toLowerCase();
  return statuses.includes(status);
}

function formatInstrument(value: string) {
  return toSymbol(value);
}

function formatOrderSide(value: string) {
  switch (value.toLowerCase()) {
    case "buy":
      return "BUY";
    case "sell":
      return "SELL";
    case "long":
      return "LONG";
    case "short":
      return "SHORT";
    default:
      return value.toUpperCase();
  }
}

function sideClass(value: string) {
  const normalized = value.toLowerCase();
  if (normalized === "buy" || normalized === "long") {
    return "positive";
  }
  if (normalized === "sell" || normalized === "short") {
    return "negative";
  }
  return "neutral";
}

function formatOrderType(value: string) {
  switch (value.toLowerCase()) {
    case "market":
      return "시장가";
    case "limit":
      return "지정가";
    default:
      return value === "-" ? value : value.toUpperCase();
  }
}

function formatOrderStatus(value: string) {
  return formatStatusLabel(value);
}

function toSymbol(instrumentId: string) {
  return instrumentId.includes(":") ? instrumentId.split(":").at(-1) ?? instrumentId : instrumentId;
}

function uniqueOptions(values: string[]) {
  return [...new Set(values.map((value) => value.trim()).filter(Boolean))];
}

function getEarliestCandleTimestamp(candles: Candle[]) {
  const timestamps = candles
    .map((candle) => new Date(candle.timestamp).getTime())
    .filter((timestamp) => Number.isFinite(timestamp));
  if (timestamps.length === 0) {
    return null;
  }
  return new Date(Math.min(...timestamps));
}

function getPreviousPageEndAt(earliestCandleAt: Date, timeframe: string) {
  const seconds = timeframeToSeconds(timeframe);
  if (!seconds) {
    return new Date(earliestCandleAt.getTime() - 1);
  }
  return new Date(earliestCandleAt.getTime() - seconds * 1000);
}

function mergeCandles(...groups: Candle[][]) {
  const byTimestamp = new Map<string, Candle>();
  for (const candle of groups.flat()) {
    byTimestamp.set(candle.timestamp, candle);
  }
  return [...byTimestamp.values()].sort(
    (left, right) => new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime(),
  );
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

function toRsiSeriesData(candles: Candle[], period: number): LineData[] {
  const sortedCandles = [...candles].sort(
    (left, right) => new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime(),
  );
  if (sortedCandles.length <= period) {
    return [];
  }

  const values: LineData[] = [];
  let averageGain = 0;
  let averageLoss = 0;

  for (let index = 1; index < sortedCandles.length; index += 1) {
    const change = sortedCandles[index].close - sortedCandles[index - 1].close;
    const gain = Math.max(change, 0);
    const loss = Math.max(-change, 0);

    if (index <= period) {
      averageGain += gain;
      averageLoss += loss;
      if (index < period) {
        continue;
      }
      averageGain /= period;
      averageLoss /= period;
    } else {
      averageGain = (averageGain * (period - 1) + gain) / period;
      averageLoss = (averageLoss * (period - 1) + loss) / period;
    }

    const timestamp = Math.floor(new Date(sortedCandles[index].timestamp).getTime() / 1000);
    if (!Number.isFinite(timestamp)) {
      continue;
    }
    const rsi = averageLoss === 0 ? 100 : 100 - 100 / (1 + averageGain / averageLoss);
    values.push({
      time: timestamp as UTCTimestamp,
      value: Number(rsi.toFixed(4)),
    });
  }

  return values;
}
