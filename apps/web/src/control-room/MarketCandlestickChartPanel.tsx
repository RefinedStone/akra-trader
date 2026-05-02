import { useEffect, useMemo, useRef, useState } from "react";
import {
  CandlestickSeries,
  ColorType,
  HistogramSeries,
  LineSeries,
  LineStyle,
  createChart,
  type IChartApi,
  type IPriceLine,
  type ISeriesApi,
  type UTCTimestamp,
} from "lightweight-charts";

import { getMarketDataStatus, listMarketDataCandles } from "../controlRoomApi";
import type { MarketDataCandle, MarketDataStatus } from "../controlRoomDefinitions";

const DEFAULT_SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"];
const TIMEFRAMES = ["1m", "5m", "15m", "1h", "1d"];
const CANDLE_LIMIT = 800;

type OrderBlockZone = {
  direction: "bullish" | "bearish";
  high: number;
  low: number;
  midpoint: number;
  timestamp: string;
};

function toUnixSeconds(timestamp: string): UTCTimestamp {
  return Math.floor(new Date(timestamp).getTime() / 1000) as UTCTimestamp;
}

function formatPrice(value: number | null) {
  if (value === null || !Number.isFinite(value)) {
    return "n/a";
  }
  return value.toLocaleString(undefined, {
    maximumFractionDigits: Math.abs(value) >= 100 ? 2 : 4,
    minimumFractionDigits: Math.abs(value) >= 100 ? 2 : 4,
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

function buildMovingAverage(candles: MarketDataCandle[], period: number) {
  const rows: { time: UTCTimestamp; value: number }[] = [];
  let sum = 0;
  candles.forEach((candle, index) => {
    sum += candle.close;
    if (index >= period) {
      sum -= candles[index - period].close;
    }
    if (index >= period - 1) {
      rows.push({
        time: toUnixSeconds(candle.timestamp),
        value: sum / period,
      });
    }
  });
  return rows;
}

function buildRsi(candles: MarketDataCandle[], period: number) {
  const rows: { time: UTCTimestamp; value: number }[] = [];
  if (candles.length <= period) {
    return rows;
  }
  let gainSum = 0;
  let lossSum = 0;
  for (let index = 1; index <= period; index += 1) {
    const change = candles[index].close - candles[index - 1].close;
    gainSum += Math.max(change, 0);
    lossSum += Math.max(-change, 0);
  }
  let averageGain = gainSum / period;
  let averageLoss = lossSum / period;
  for (let index = period; index < candles.length; index += 1) {
    if (index > period) {
      const change = candles[index].close - candles[index - 1].close;
      averageGain = (averageGain * (period - 1) + Math.max(change, 0)) / period;
      averageLoss = (averageLoss * (period - 1) + Math.max(-change, 0)) / period;
    }
    const value = averageLoss === 0 ? 100 : 100 - 100 / (1 + averageGain / averageLoss);
    rows.push({
      time: toUnixSeconds(candles[index].timestamp),
      value,
    });
  }
  return rows;
}

function detectOrderBlocks(candles: MarketDataCandle[]) {
  const recent = candles.slice(-160);
  if (recent.length < 24) {
    return [] as OrderBlockZone[];
  }
  const averageRange =
    recent.reduce((sum, candle) => sum + Math.max(candle.high - candle.low, 0), 0) /
    recent.length;
  const zones: OrderBlockZone[] = [];
  for (let index = 1; index < recent.length - 2; index += 1) {
    const current = recent[index];
    const next = recent[index + 1];
    const nextBody = Math.abs(next.close - next.open);
    const bullishDisplacement =
      current.close < current.open &&
      next.close > next.open &&
      next.close > current.high &&
      nextBody >= averageRange * 0.55;
    const bearishDisplacement =
      current.close > current.open &&
      next.close < next.open &&
      next.close < current.low &&
      nextBody >= averageRange * 0.55;
    if (bullishDisplacement || bearishDisplacement) {
      zones.push({
        direction: bullishDisplacement ? "bullish" : "bearish",
        high: Math.max(current.open, current.high),
        low: Math.min(current.open, current.low),
        midpoint: (Math.max(current.open, current.high) + Math.min(current.open, current.low)) / 2,
        timestamp: current.timestamp,
      });
    }
  }
  return zones.slice(-6).reverse();
}

export function MarketCandlestickChartPanel() {
  const chartElementRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const ma5SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const ma20SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const ma60SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const rsiSeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const rsiGuideLinesRef = useRef<IPriceLine[]>([]);
  const orderBlockLinesRef = useRef<IPriceLine[]>([]);
  const [status, setStatus] = useState<MarketDataStatus | null>(null);
  const [candles, setCandles] = useState<MarketDataCandle[]>([]);
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("5m");
  const [showMa5, setShowMa5] = useState(true);
  const [showMa20, setShowMa20] = useState(true);
  const [showMa60, setShowMa60] = useState(true);
  const [showRsi, setShowRsi] = useState(true);
  const [showOrderBlocks, setShowOrderBlocks] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const symbols = useMemo(() => resolveSymbols(status), [status]);
  const latestCandle = candles.at(-1) ?? null;
  const previousCandle = candles.at(-2) ?? null;
  const latestInstrument = status?.instruments.find(
    (instrument) => instrument.instrument_id.endsWith(symbol) && instrument.timeframe === timeframe,
  );
  const ma5 = useMemo(() => buildMovingAverage(candles, 5), [candles]);
  const ma20 = useMemo(() => buildMovingAverage(candles, 20), [candles]);
  const ma60 = useMemo(() => buildMovingAverage(candles, 60), [candles]);
  const rsi14 = useMemo(() => buildRsi(candles, 14), [candles]);
  const orderBlocks = useMemo(() => detectOrderBlocks(candles), [candles]);
  const activeOrderBlocks = orderBlocks.slice(0, 2);
  const latestRsi = rsi14.at(-1)?.value ?? null;
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
    const ma5Series = chart.addSeries(LineSeries, {
      color: "#fbbf24",
      lineWidth: 2,
      priceLineVisible: false,
      title: "MA 5",
    });
    const ma20Series = chart.addSeries(LineSeries, {
      color: "#38bdf8",
      lineWidth: 2,
      priceLineVisible: false,
      title: "MA 20",
    });
    const ma60Series = chart.addSeries(LineSeries, {
      color: "#f472b6",
      lineWidth: 2,
      priceLineVisible: false,
      title: "MA 60",
    });
    const rsiSeries = chart.addSeries(
      LineSeries,
      {
        color: "#c084fc",
        lineWidth: 2,
        priceLineVisible: false,
        title: "RSI 14",
      },
      1,
    );
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        bottom: 0,
        top: 0.82,
      },
    });
    rsiSeries.priceScale().applyOptions({
      scaleMargins: {
        bottom: 0.08,
        top: 0.08,
      },
    });
    rsiGuideLinesRef.current = [
      rsiSeries.createPriceLine({
        axisLabelVisible: true,
        color: "rgba(248, 113, 113, 0.85)",
        lineStyle: LineStyle.Dashed,
        lineWidth: 1,
        price: 70,
        title: "RSI 70",
      }),
      rsiSeries.createPriceLine({
        axisLabelVisible: true,
        color: "rgba(74, 222, 128, 0.85)",
        lineStyle: LineStyle.Dashed,
        lineWidth: 1,
        price: 30,
        title: "RSI 30",
      }),
    ];
    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;
    ma5SeriesRef.current = ma5Series;
    ma20SeriesRef.current = ma20Series;
    ma60SeriesRef.current = ma60Series;
    rsiSeriesRef.current = rsiSeries;
    return () => {
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
      ma5SeriesRef.current = null;
      ma20SeriesRef.current = null;
      ma60SeriesRef.current = null;
      rsiSeriesRef.current = null;
      rsiGuideLinesRef.current = [];
      orderBlockLinesRef.current = [];
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
    ma5SeriesRef.current?.setData(showMa5 ? ma5 : []);
    ma20SeriesRef.current?.setData(showMa20 ? ma20 : []);
    ma60SeriesRef.current?.setData(showMa60 ? ma60 : []);
    rsiSeriesRef.current?.setData(showRsi ? rsi14 : []);
    if (candleSeriesRef.current) {
      for (const line of orderBlockLinesRef.current) {
        candleSeriesRef.current.removePriceLine(line);
      }
      orderBlockLinesRef.current = [];
      if (showOrderBlocks) {
        for (const zone of activeOrderBlocks) {
          const color =
            zone.direction === "bullish"
              ? "rgba(34, 197, 94, 0.85)"
              : "rgba(239, 68, 68, 0.85)";
          orderBlockLinesRef.current.push(
            candleSeriesRef.current.createPriceLine({
              axisLabelVisible: true,
              color,
              lineStyle: LineStyle.LargeDashed,
              lineWidth: 2,
              price: zone.midpoint,
              title: zone.direction === "bullish" ? "Bull OB" : "Bear OB",
            }),
          );
        }
      }
    }
    chartRef.current?.timeScale().fitContent();
  }, [activeOrderBlocks, candles, ma5, ma20, ma60, rsi14, showMa5, showMa20, showMa60, showOrderBlocks, showRsi]);

  useEffect(() => {
    for (const line of rsiGuideLinesRef.current) {
      line.applyOptions({ lineVisible: showRsi, axisLabelVisible: showRsi });
    }
  }, [showRsi]);

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

      <div className="market-chart-indicator-bar" aria-label="Indicator controls">
        <label>
          <input checked={showMa5} onChange={(event) => setShowMa5(event.target.checked)} type="checkbox" />
          MA 5
        </label>
        <label>
          <input checked={showMa20} onChange={(event) => setShowMa20(event.target.checked)} type="checkbox" />
          MA 20
        </label>
        <label>
          <input checked={showMa60} onChange={(event) => setShowMa60(event.target.checked)} type="checkbox" />
          MA 60
        </label>
        <label>
          <input checked={showRsi} onChange={(event) => setShowRsi(event.target.checked)} type="checkbox" />
          RSI 14
        </label>
        <label>
          <input
            checked={showOrderBlocks}
            onChange={(event) => setShowOrderBlocks(event.target.checked)}
            type="checkbox"
          />
          Order Block
        </label>
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
          <span>RSI 14</span>
          <strong>{latestRsi === null ? "n/a" : latestRsi.toFixed(1)}</strong>
        </div>
        <div className="metric-tile">
          <span>Order blocks</span>
          <strong>{orderBlocks.length}</strong>
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
        {!loading && !error && candles.length === 0 ? (
          <div className="market-chart-overlay">No candles synced for {timeframe}</div>
        ) : null}
      </div>

      {activeOrderBlocks.length ? (
        <div className="market-chart-order-blocks">
          {activeOrderBlocks.map((zone) => (
            <div className={`market-chart-order-block is-${zone.direction}`} key={`${zone.direction}-${zone.timestamp}`}>
              <span>{zone.direction === "bullish" ? "Bull OB" : "Bear OB"}</span>
              <strong>
                {formatPrice(zone.low)} - {formatPrice(zone.high)}
              </strong>
              <small>{formatTimestamp(zone.timestamp)}</small>
            </div>
          ))}
        </div>
      ) : null}

      <div className="market-chart-footer">
        <span>{status ? `${status.provider} / ${status.venue}` : "market data provider"}</span>
        <span>{latestInstrument?.sync_status ?? "sync unknown"}</span>
        <span>Latest candle {formatTimestamp(latestCandle?.timestamp ?? null)}</span>
      </div>
    </section>
  );
}
