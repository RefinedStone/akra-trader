import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { UTCTimestamp } from "lightweight-charts";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App, { buildOrderMarkers, buildSeriesOrderMarkers } from "./ControlRoomApp";

const strategyResponse = {
  strategies: [
    {
      strategy_id: "ma_cross_v1",
      name: "Moving Average Cross",
      runtime: "native",
      lifecycle: { stage: "active" },
      supported_timeframes: ["5m"],
      parameter_schema: {},
    },
    {
      strategy_id: "external_decision_template",
      name: "Future LLM Research Lane",
      runtime: "decision_engine",
      lifecycle: { stage: "experimental" },
      supported_timeframes: ["5m"],
      parameter_schema: {},
    },
  ],
  llm_strategy: {
    runtime: "decision_engine",
    decision_port: "DecisionEnginePort",
    isolation_state: "interface_only",
    trace_envelope: { signal: "SignalDecision", trace: "provider-neutral dict" },
  },
};

const marketStatus = {
  provider: "seeded",
  venue: "binance",
  instruments: [
    {
      instrument_id: "binance:BTC/USDT",
      timeframe: "5m",
      candle_count: 240,
      sync_status: "fixture",
      last_timestamp: "2025-01-01T00:00:00Z",
    },
  ],
};

const healthResponse = {
  status: "ok",
  market_data_provider: "seeded",
  guarded_live: {
    venue: "binance",
    enabled: true,
  },
};

const sandboxRun = {
  run_id: "run-1",
  mode: "sandbox",
  status: "running",
  started_at: "2026-05-11T00:00:00Z",
  ended_at: null,
  config: {
    symbols: ["BTC/USDT"],
    timeframe: "5m",
    initial_cash: 10000,
    start_at: null,
    end_at: null,
  },
  strategy: { name: "Moving Average Cross", strategy_id: "ma_cross_v1" },
  market_data: {
    provider: "seeded",
    venue: "binance",
    timeframe: "5m",
    effective_start_at: "2025-01-01T00:00:00Z",
    effective_end_at: "2025-01-01T02:00:00Z",
    candle_count: 30,
    sync_status: "fixture",
    issues: [],
  },
  metrics: { ending_equity: 10025, total_return_pct: 0.25, trade_count: 1 },
  orders_count: 1,
  positions_count: 1,
  notes: [],
};

const backtestRun = {
  ...sandboxRun,
  run_id: "run-backtest",
  mode: "backtest",
  status: "completed",
  config: {
    symbols: ["BTC/USDT"],
    timeframe: "5m",
    initial_cash: 10000,
    start_at: "2025-01-01T00:00:00Z",
    end_at: "2025-01-02T00:00:00Z",
  },
  market_data: {
    provider: "seeded",
    venue: "binance",
    timeframe: "5m",
    requested_start_at: "2025-01-01T00:00:00Z",
    requested_end_at: "2025-01-02T00:00:00Z",
    effective_start_at: "2025-01-01T00:00:00Z",
    effective_end_at: "2025-01-02T00:00:00Z",
    candle_count: 289,
    sync_status: "fixture",
    issues: [],
  },
  metrics: {
    ending_equity: 10250,
    total_return_pct: 2.5,
    max_drawdown_pct: 1.1,
    trade_count: 3,
  },
};

const syncResult = {
  provider: "seeded",
  venue: "binance",
  symbol: "BTC/USDT",
  timeframe: "5m",
  status: "fixture",
  requested_start_at: "2025-01-01T00:00:00Z",
  requested_end_at: "2025-01-01T00:20:00Z",
  requested_limit: 2000,
  effective_start_at: "2025-01-01T00:00:00Z",
  effective_end_at: "2025-01-01T00:20:00Z",
  candle_count: 5,
  issues: [],
};

const orderFixture = {
  order_id: "order-1",
  instrument_id: "binance:BTC/USDT",
  side: "buy",
  quantity: 0.25,
  filled_quantity: 0.25,
  requested_price: 81200,
  average_fill_price: 81210,
  order_type: "market",
  status: "filled",
  created_at: "2026-05-11T00:10:00Z",
  filled_at: "2026-05-11T00:10:01Z",
};

const positionFixture = {
  instrument_id: "binance:BTC/USDT",
  quantity: 0.25,
  average_price: 81210,
  realized_pnl: 126.5,
  opened_at: "2026-05-11T00:10:01Z",
  updated_at: "2026-05-11T00:15:00Z",
};

const logFixture = {
  log_id: "log-1",
  recorded_at: "2026-05-11T00:16:00Z",
  layer: "engine",
  event_type: "worker_candles_processed",
  message: "Processed closed candle for BTC/USDT.",
  severity: "info",
  run_id: "run-1",
  mode: "sandbox",
};

function jsonResponse(body: unknown, ok = true, status = 200) {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(body),
  } as Response);
}

describe("ControlRoomApp", () => {
  let runs: Array<typeof sandboxRun | typeof backtestRun> = [];

  beforeEach(() => {
    runs = [];
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        if (url.includes("/api/health")) {
          return jsonResponse(healthResponse);
        }
        if (url.includes("/api/strategies")) {
          return jsonResponse(strategyResponse);
        }
        if (url.includes("/api/market-data/status")) {
          return jsonResponse(marketStatus);
        }
        if (url.includes("/api/market-data/candles")) {
          const params = new URLSearchParams(url.split("?")[1] ?? "");
          const endAt = params.get("end_at");
          if (endAt && new Date(endAt).getTime() < new Date("2025-01-01T00:00:00Z").getTime()) {
            return jsonResponse({
              candles: [
                { timestamp: "2024-12-31T23:55:00Z", open: 1, high: 2, low: 1, close: 1.5, volume: 10 },
              ],
            });
          }
          return jsonResponse({
            candles: [{ timestamp: "2025-01-01T00:00:00Z", open: 1, high: 2, low: 1, close: 2, volume: 10 }],
          });
        }
        if (url.endsWith("/api/logs?limit=100") || url.includes("/api/logs?")) {
          return jsonResponse({ logs: [logFixture] });
        }
        if (url.endsWith("/api/runs/sandbox") && init?.method === "POST") {
          runs = [sandboxRun];
          return jsonResponse(sandboxRun);
        }
        if (url.endsWith("/api/runs/backtests") && init?.method === "POST") {
          runs = [backtestRun];
          return jsonResponse(backtestRun);
        }
        if (url.endsWith("/api/market-data/sync") && init?.method === "POST") {
          return jsonResponse(syncResult);
        }
        if (url.endsWith("/api/runs/run-1/orders")) {
          return jsonResponse({ orders: [orderFixture] });
        }
        if (url.endsWith("/api/runs/run-1/positions")) {
          return jsonResponse({ positions: [positionFixture] });
        }
        if (url.endsWith("/api/runs/run-1")) {
          return jsonResponse(sandboxRun);
        }
        if (url.endsWith("/api/runs/run-backtest/orders")) {
          return jsonResponse({ orders: [] });
        }
        if (url.endsWith("/api/runs/run-backtest/positions")) {
          return jsonResponse({ positions: [] });
        }
        if (url.endsWith("/api/runs/run-backtest")) {
          return jsonResponse(backtestRun);
        }
        const dynamicRun = runs.find((run) => url.endsWith(`/api/runs/${run.run_id}`));
        if (dynamicRun) {
          return jsonResponse(dynamicRun);
        }
        if (runs.some((run) => url.endsWith(`/api/runs/${run.run_id}/orders`))) {
          return jsonResponse({ orders: [] });
        }
        if (runs.some((run) => url.endsWith(`/api/runs/${run.run_id}/positions`))) {
          return jsonResponse({ positions: [] });
        }
        if (url.endsWith("/api/runs")) {
          return jsonResponse({ runs });
        }
        return jsonResponse({}, false, 404);
      }),
    );
    window.history.pushState(null, "", "/data");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the core sections and submits a sandbox payload", async () => {
    render(<App />);

    expect(await screen.findByRole("button", { name: /데이터/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /백테스트/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /샌드박스/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /실전 매매/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /성과/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /로그/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /LLM 전략/ })).toBeInTheDocument();
    for (const timeframe of ["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"]) {
      expect(screen.getByRole("option", { name: timeframe })).toBeInTheDocument();
    }
    expect(screen.getByText("MA5")).toBeInTheDocument();
    expect(screen.getByText("MA20 황금선")).toBeInTheDocument();
    expect(screen.getByText("MA60")).toBeInTheDocument();
    expect(screen.getByText("RSI14")).toBeInTheDocument();
    expect(screen.getByText("Bull OB")).toBeInTheDocument();
    expect(screen.getByText("Bear OB")).toBeInTheDocument();
    expect(screen.getByText("BUY")).toBeInTheDocument();
    expect(screen.getByText("SELL")).toBeInTheDocument();
    expect(screen.getByText("2025-01-01 09:00:00")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /샌드박스/ }));
    expect(screen.getByRole("combobox", { name: "심볼" })).toHaveValue("BTC/USDT");
    fireEvent.click(screen.getByRole("button", { name: "샌드박스 실행" }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/runs/sandbox",
        expect.objectContaining({ method: "POST" }),
      );
    });
    await waitFor(() => {
      expect(screen.getAllByText("Moving Average Cross").length).toBeGreaterThan(1);
    });
  });

  it("shows the LLM strategy as an isolated interface", async () => {
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: /LLM 전략/ }));

    expect(screen.getByText("DecisionEnginePort")).toBeInTheDocument();
    expect(screen.getByText("인터페이스만 유지")).toBeInTheDocument();
  });

  it("renders the performance dashboard from run metrics", async () => {
    runs = [backtestRun, sandboxRun];
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: /성과/ }));

    expect(screen.getByText("성과 대시보드")).toBeInTheDocument();
    expect(screen.getByText("수익률 추이 비교")).toBeInTheDocument();
    expect(screen.getByText("전략 성과 비교")).toBeInTheDocument();
    expect(screen.getByText("심볼별 수익 기여도")).toBeInTheDocument();
    expect(screen.getByText("성과 인사이트")).toBeInTheDocument();
    expect(screen.queryByText("실행 상세")).not.toBeInTheDocument();
  });

  it("aggregates independent run returns without compounding them", async () => {
    runs = [0, 1, 2].map((index) => ({
      ...backtestRun,
      run_id: `high-return-${index}`,
      started_at: `2026-05-1${index}T00:00:00Z`,
      metrics: {
        ...backtestRun.metrics,
        ending_equity: 20000,
        initial_cash: 10000,
        total_return_pct: 100,
      },
    }));
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: /성과/ }));

    expect(screen.getByText("가중 수익률")).toBeInTheDocument();
    expect(screen.getAllByText("+100%").length).toBeGreaterThan(0);
    expect(screen.queryByText("+700%")).not.toBeInTheDocument();
  });

  it("loads market data through one sync-backed query flow", async () => {
    render(<App />);

    expect(await screen.findByText("캔들 조회")).toBeInTheDocument();
    await screen.findByRole("button", { name: "조회" });
    vi.mocked(globalThis.fetch).mockClear();

    fireEvent.change(screen.getByLabelText("시작일"), { target: { value: "2025-01-01T00:00" } });
    fireEvent.change(screen.getByLabelText("종료일"), { target: { value: "2025-01-01T00:20" } });
    fireEvent.change(screen.getByLabelText("조회 개수"), { target: { value: "2000" } });
    fireEvent.click(screen.getByRole("button", { name: "조회" }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/market-data/sync",
        expect.objectContaining({ method: "POST" }),
      );
    });
    const syncCall = vi.mocked(globalThis.fetch).mock.calls.find(([url]) =>
      String(url).endsWith("/api/market-data/sync"),
    );
    expect(JSON.parse(String(syncCall?.[1]?.body))).toMatchObject({
      symbol: "BTC/USDT",
      timeframe: "5m",
      start_at: new Date("2025-01-01T00:00").toISOString(),
      end_at: new Date("2025-01-01T00:20").toISOString(),
      limit: 2000,
    });
    const candleCall = vi.mocked(globalThis.fetch).mock.calls.find(([url]) =>
      String(url).includes("/api/market-data/candles"),
    );
    const candleParams = new URLSearchParams(String(candleCall?.[0]).split("?")[1] ?? "");
    expect(candleParams.get("symbol")).toBe("BTC/USDT");
    expect(candleParams.get("timeframe")).toBe("5m");
    expect(candleParams.get("start_at")).toBe(new Date("2025-01-01T00:00").toISOString());
    expect(candleParams.get("end_at")).toBe(new Date("2025-01-01T00:20").toISOString());
    expect(candleParams.get("limit")).toBe("2000");
    await waitFor(() => {
      expect(screen.getByText("5개")).toBeInTheDocument();
    });
  });

  it("pages older market data before the current earliest candle", async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "이전 구간 더 보기" })).not.toBeDisabled();
    });
    vi.mocked(globalThis.fetch).mockClear();
    fireEvent.click(screen.getByRole("button", { name: "이전 구간 더 보기" }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/market-data/sync",
        expect.objectContaining({ method: "POST" }),
      );
    });
    const syncCall = vi.mocked(globalThis.fetch).mock.calls.find(([url]) =>
      String(url).endsWith("/api/market-data/sync"),
    );
    expect(JSON.parse(String(syncCall?.[1]?.body))).toMatchObject({
      start_at: null,
      end_at: "2024-12-31T23:55:00.000Z",
      limit: 500,
    });
    await waitFor(() => {
      expect(screen.getByText("2025-01-01 08:55:00 - 2025-01-01 09:00:00")).toBeInTheDocument();
    });
  });

  it("includes backtest start and end datetimes in the run payload", async () => {
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: /백테스트/ }));
    fireEvent.change(screen.getByLabelText("시작일"), { target: { value: "2025-01-01T00:00" } });
    fireEvent.change(screen.getByLabelText("종료일"), { target: { value: "2025-01-02T00:00" } });
    fireEvent.click(screen.getByRole("button", { name: "백테스트 실행" }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/runs/backtests",
        expect.objectContaining({ method: "POST" }),
      );
    });
    const runCall = vi.mocked(globalThis.fetch).mock.calls.find(([url]) =>
      String(url).endsWith("/api/runs/backtests"),
    );
    expect(JSON.parse(String(runCall?.[1]?.body))).toMatchObject({
      start_at: new Date("2025-01-01T00:00").toISOString(),
      end_at: new Date("2025-01-02T00:00").toISOString(),
    });
  });

  it("aligns backtest datetimes to the selected timeframe before submit", async () => {
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: /백테스트/ }));
    fireEvent.change(screen.getByLabelText("시작일"), { target: { value: "2025-01-01T01:19" } });
    fireEvent.change(screen.getByLabelText("종료일"), { target: { value: "2025-01-01T02:19" } });
    fireEvent.click(screen.getByRole("button", { name: "백테스트 실행" }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/runs/backtests",
        expect.objectContaining({ method: "POST" }),
      );
    });
    const runCall = vi.mocked(globalThis.fetch).mock.calls.find(([url]) =>
      String(url).endsWith("/api/runs/backtests"),
    );
    expect(JSON.parse(String(runCall?.[1]?.body))).toMatchObject({
      start_at: new Date("2025-01-01T01:20").toISOString(),
      end_at: new Date("2025-01-01T02:15").toISOString(),
    });
  });

  it("maps backtest orders onto wider chart timeframe candles", () => {
    const order = {
      ...orderFixture,
      filled_at: "2026-05-11T00:10:01Z",
    };
    const selectedRun = backtestRun as Parameters<typeof buildOrderMarkers>[1]["selectedRun"];

    expect(
      buildOrderMarkers([order], {
        candles: [
          { timestamp: "2026-05-11T00:00:00Z", open: 81000, high: 81300, low: 80900, close: 81250, volume: 10 },
          { timestamp: "2026-05-11T00:15:00Z", open: 81250, high: 81400, low: 81100, close: 81320, volume: 12 },
        ],
        selectedRun,
        symbol: "BTC/USDT",
        timeframe: "15m",
      }),
    ).toMatchObject([{ id: "order-1", side: "buy", time: 1778457600 }]);

    expect(
      buildOrderMarkers([order], {
        candles: [
          { timestamp: "2026-05-11T00:00:00Z", open: 81000, high: 81400, low: 80900, close: 81320, volume: 22 },
          { timestamp: "2026-05-11T01:00:00Z", open: 81320, high: 81600, low: 81200, close: 81550, volume: 18 },
        ],
        selectedRun,
        symbol: "BTC/USDT",
        timeframe: "1h",
      }),
    ).toMatchObject([{ id: "order-1", side: "buy", time: 1778457600 }]);
  });

  it("anchors order markers to chart bars instead of absolute overlay coordinates", () => {
    const markers = [
      { id: "buy-1", price: 81210, side: "buy" as const, time: 1778457600 as UTCTimestamp },
      { id: "sell-1", price: 81310, side: "sell" as const, time: 1778458500 as UTCTimestamp },
    ];

    expect(buildSeriesOrderMarkers(markers, "buy-1")).toMatchObject([
      { id: "buy-1", position: "belowBar", shape: "arrowUp", size: 1.85, text: "BUY" },
      { id: "sell-1", position: "aboveBar", shape: "arrowDown", size: 1.15, text: "SELL" },
    ]);
  });

  it("renders operational detail tabs with summarized orders, positions, and logs", async () => {
    runs = [sandboxRun];
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: /샌드박스/ }));
    await waitFor(() => {
      expect(screen.getAllByText("Moving Average Cross").length).toBeGreaterThan(0);
    });

    fireEvent.click(screen.getByRole("button", { name: "주문" }));
    expect(screen.getByText("총 주문")).toBeInTheDocument();
    expect(screen.getByText("주문 활동 타임라인")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "order-1" }));
    expect(screen.getByRole("button", { name: "order-1" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getAllByText("BUY").length).toBeGreaterThan(0);
    expect(screen.getAllByText("체결").length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole("button", { name: "포지션" }));
    expect(screen.getByText("선택 포지션 상세")).toBeInTheDocument();
    expect(screen.getByText("노출 분포")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "로그" }));
    expect(screen.getByText("선택 로그 상세")).toBeInTheDocument();
    expect(screen.getAllByText("Processed closed candle for BTC/USDT.").length).toBeGreaterThan(0);
  });

  it("shows clickable run detail tabs and backtest results", async () => {
    runs = [backtestRun];
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: /백테스트/ }));
    await waitFor(() => {
      expect(screen.getByText("10,250")).toBeInTheDocument();
      expect(screen.getByText("2.5%")).toBeInTheDocument();
      expect(screen.getByText("289")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "지표" }));
    expect(screen.getByText("총수익률")).toBeInTheDocument();
    expect(screen.getByText("최대 낙폭")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "주문" }));
    expect(screen.getByText("주문이 없습니다.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "결과" }));
    expect(screen.getByText("데이터 상태")).toBeInTheDocument();
  });
});
