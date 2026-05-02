import { useEffect, useMemo, useRef, useState } from "react";
import {
  CandlestickSeries,
  ColorType,
  HistogramSeries,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
} from "lightweight-charts";

import { getMarketDataStatus, listMarketDataCandles } from "../controlRoomApi";
import type { MarketDataCandle, MarketDataStatus } from "../controlRoomDefinitions";

const DEFAULT_SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"];
const TIMEFRAMES = ["5m"];
const CANDLE_LIMIT = 500;

function toUnixSeconds(timestamp: string): UTCTimestamp {
  return Math.floor(new Date(timestamp).getTime() / 1000) as UTCTimestamp;
}

function formatPrice(value: number | null) {
  if (value === null || !Number.isFinite(value)) {
    return "n/a";
  }
  return value.toLocaleString(undefined, {
    maximumFractionDigits: value >= 100 ? 2 : 4,
    minimumFractionDigits: value >= 100 ? 2 : 4,
  });
}

function formatTimestamp(timestamp: string | null) {
  if (!timestamp) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(timestamp));
}

function resolveSymbols(status: MarketDataStatus | null) {
  const symbols =
    status?.instruments
      .map((instrument) => instrument.instrument_id.split(":").at(-1))
      .filter((symbol): symbol is string => Boolean(symbol)) ?? [];
  return Array.from(new Set(symbols.length ? symbols : DEFAULT_SYMBOLS));
}

export function MarketCandlestickChartPanel() {
  const chartElementRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const [status, setStatus] = useState<MarketDataStatus | null>(null);
  const [candles, setCandles] = useState<MarketDataCandle[]>([]);
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("5m");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const symbols = useMemo(() => resolveSymbols(status), [status]);
  const latestCandle = candles.at(-1) ?? null;
  const previousCandle = candles.at(-2) ?? null;
  const latestInstrument = status?.instruments.find(
    (instrument) => instrument.instrument_id.endsWith(symbol) && instrument.timeframe === timeframe,
  );
  const priceDelta =
    latestCandle && previousCandle ? latestCandle.close - previousCandle.close : null;
  const priceDeltaRatio =
    latestCandle && previousCandle && previousCandle.close !== 0
      ? (latestCandle.close - previousCandle.close) / previousCandle.close
      : null;

  useEffect(() => {
    if (!symbols.includes(symbol)) {
      setSymbol(symbols[0] ?? "BTC/USDT");
    }
  }, [symbol, symbols]);

  useEffect(() => {
    let cancelled = false;
    async function loadMarketData() {
      setLoading(true);
      setError(null);
      try {
        const [nextStatus, candleResponse] = await Promise.all([
          getMarketDataStatus({ timeframe }),
          listMarketDataCandles({ symbol, timeframe, limit: CANDLE_LIMIT }),
        ]);
        if (cancelled) {
          return;
        }
        setStatus(nextStatus);
        setCandles(candleResponse.candles);
      } catch (caught) {
        if (!cancelled) {
          setError(caught instanceof Error ? caught.message : "market data request failed");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    void loadMarketData();
    const refresh = window.setInterval(() => void loadMarketData(), 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(refresh);
    };
  }, [symbol, timeframe]);

  useEffect(() => {
    if (!chartElementRef.current) {
      return;
    }
    const chart = createChart(chartElementRef.current, {
      autoSize: true,
      layout: {
        background: { color: "#111827", type: ColorType.Solid },
        textColor: "#d1d5db",
      },
      grid: {
        horzLines: { color: "rgba(148, 163, 184, 0.12)" },
        vertLines: { color: "rgba(148, 163, 184, 0.08)" },
      },
      rightPriceScale: {
        borderColor: "rgba(148, 163, 184, 0.22)",
      },
      timeScale: {
        borderColor: "rgba(148, 163, 184, 0.22)",
        secondsVisible: false,
        timeVisible: true,
      },
    });
    const candleSeries = chart.addSeries(CandlestickSeries, {
      borderDownColor: "#ef4444",
      borderUpColor: "#22c55e",
      downColor: "#ef4444",
      upColor: "#22c55e",
      wickDownColor: "#ef4444",
      wickUpColor: "#22c55e",
    });
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: "rgba(59, 130, 246, 0.35)",
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        bottom: 0,
        top: 0.82,
      },
    });
    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;
    return () => {
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    candleSeriesRef.current?.setData(
      candles.map((candle) => ({
        close: candle.close,
        high: candle.high,
        low: candle.low,
        open: candle.open,
        time: toUnixSeconds(candle.timestamp),
      })),
    );
    volumeSeriesRef.current?.setData(
      candles.map((candle) => ({
        color:
          candle.close >= candle.open
            ? "rgba(34, 197, 94, 0.28)"
            : "rgba(239, 68, 68, 0.28)",
        time: toUnixSeconds(candle.timestamp),
        value: candle.volume,
      })),
    );
    chartRef.current?.timeScale().fitContent();
  }, [candles]);

  return (
    <section className="panel panel-wide market-chart-panel">
      <div className="section-heading">
        <div>
          <p className="kicker">Binance market data</p>
          <h2>Live candlestick chart</h2>
        </div>
        <div className="market-chart-controls">
          <select value={symbol} onChange={(event) => setSymbol(event.target.value)}>
            {symbols.map((candidate) => (
              <option key={candidate} value={candidate}>
                {candidate}
              </option>
            ))}
          </select>
          <select value={timeframe} onChange={(event) => setTimeframe(event.target.value)}>
            {TIMEFRAMES.map((candidate) => (
              <option key={candidate} value={candidate}>
                {candidate}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="market-chart-metrics">
        <div className="metric-tile">
          <span>Last close</span>
          <strong>{formatPrice(latestCandle?.close ?? null)}</strong>
        </div>
        <div className="metric-tile">
          <span>Change</span>
          <strong className={priceDelta !== null && priceDelta < 0 ? "is-negative" : "is-positive"}>
            {priceDelta === null ? "n/a" : `${formatPrice(priceDelta)} (${((priceDeltaRatio ?? 0) * 100).toFixed(2)}%)`}
          </strong>
        </div>
        <div className="metric-tile">
          <span>Candles</span>
          <strong>{candles.length}</strong>
        </div>
        <div className="metric-tile">
          <span>Last sync</span>
          <strong>{formatTimestamp(latestInstrument?.last_sync_at ?? null)}</strong>
        </div>
      </div>

      <div className="market-chart-frame">
        <div ref={chartElementRef} className="market-chart-canvas" />
        {loading ? <div className="market-chart-overlay">Loading market data</div> : null}
        {error ? <div className="market-chart-overlay is-error">{error}</div> : null}
      </div>

      <div className="market-chart-footer">
        <span>{status ? `${status.provider} / ${status.venue}` : "market data provider"}</span>
        <span>{latestInstrument?.sync_status ?? "sync unknown"}</span>
        <span>Latest candle {formatTimestamp(latestCandle?.timestamp ?? null)}</span>
      </div>
    </section>
  );
}
