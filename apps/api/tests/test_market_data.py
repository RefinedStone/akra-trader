from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest

from akra_trader.adapters.binance import BinanceMarketDataAdapter


class FakeExchange:
  def __init__(self, series: dict[tuple[str, str], list[list[float]]]) -> None:
    self._series = series
    self.calls: list[dict[str, int | str | None]] = []

  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "5m",
    since: int | None = None,
    limit: int | None = None,
  ) -> list[list[float]]:
    self.calls.append(
      {
        "symbol": symbol,
        "timeframe": timeframe,
        "since": since,
        "limit": limit,
      }
    )
    values = list(self._series[(symbol, timeframe)])
    if since is not None:
      values = [row for row in values if row[0] >= since]
    if limit is not None:
      values = values[:limit]
    return values


def build_ohlcv_rows(
  *,
  start_at: datetime,
  count: int,
  timeframe_minutes: int = 5,
  gap_after_index: int | None = None,
) -> list[list[float]]:
  rows: list[list[float]] = []
  offset = 0
  for index in range(count):
    if gap_after_index is not None and index == gap_after_index + 1:
      offset = 1
    timestamp = start_at + timedelta(minutes=timeframe_minutes * (index + offset))
    rows.append(
      [
        int(timestamp.timestamp() * 1000),
        100 + index,
        101 + index,
        99 + index,
        100.5 + index,
        10 + index,
      ]
    )
  return rows


def test_binance_adapter_persists_recent_candles_and_status(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=25),
    count=6,
  )
  exchange = FakeExchange({("BTC/USDT", "5m"): rows})
  adapter = BinanceMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market-data.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange=exchange,
    default_candle_limit=6,
    clock=lambda: now,
  )

  adapter.sync_tracked("5m")
  status = adapter.get_status("5m")
  candles = adapter.get_candles(symbol="BTC/USDT", timeframe="5m", limit=4)
  lineage = adapter.describe_lineage(
    symbol="BTC/USDT",
    timeframe="5m",
    candles=candles,
    limit=4,
  )

  assert status.provider == "binance"
  assert status.instruments[0].sync_status == "synced"
  assert status.instruments[0].candle_count == 6
  assert status.instruments[0].lag_seconds == 0
  assert status.instruments[0].backfill_target_candles == 6
  assert status.instruments[0].backfill_completion_ratio == 1.0
  assert status.instruments[0].backfill_complete is True
  assert status.instruments[0].backfill_contiguous_completion_ratio == 1.0
  assert status.instruments[0].backfill_contiguous_complete is True
  assert status.instruments[0].backfill_contiguous_missing_candles == 0
  assert not status.instruments[0].issues
  assert len(candles) == 4
  assert candles[-1].close == 105.5
  assert lineage.provider == "binance"
  assert lineage.candle_count == 4
  assert lineage.sync_status == "synced"


def test_binance_adapter_backfills_history_beyond_recent_window(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=45),
    count=10,
  )
  exchange = FakeExchange({("BTC/USDT", "5m"): rows})
  adapter = BinanceMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market-data.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange=exchange,
    default_candle_limit=4,
    historical_candle_limit=8,
    exchange_batch_limit=4,
    clock=lambda: now,
  )

  adapter.sync_tracked("5m")
  status = adapter.get_status("5m")
  candles = adapter.get_candles(symbol="BTC/USDT", timeframe="5m")

  assert status.instruments[0].candle_count == 8
  assert status.instruments[0].backfill_target_candles == 8
  assert status.instruments[0].backfill_completion_ratio == 1.0
  assert status.instruments[0].backfill_complete is True
  assert status.instruments[0].backfill_contiguous_completion_ratio == 1.0
  assert status.instruments[0].backfill_contiguous_complete is True
  assert status.instruments[0].backfill_contiguous_missing_candles == 0
  assert candles[0].timestamp == now - timedelta(minutes=35)
  assert candles[-1].timestamp == now
  assert len(exchange.calls) == 2


def test_binance_adapter_reuses_persisted_candles_when_coverage_is_fresh(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=25),
    count=6,
  )
  database_url = f"sqlite:///{tmp_path / 'market-data.sqlite3'}"
  first_exchange = FakeExchange({("BTC/USDT", "5m"): rows})
  first_adapter = BinanceMarketDataAdapter(
    database_url=database_url,
    tracked_symbols=("BTC/USDT",),
    exchange=first_exchange,
    default_candle_limit=6,
    historical_candle_limit=6,
    clock=lambda: now,
  )

  first_adapter.sync_tracked("5m")
  first_adapter.get_candles(symbol="BTC/USDT", timeframe="5m", limit=4)

  second_exchange = FakeExchange({("BTC/USDT", "5m"): []})
  second_adapter = BinanceMarketDataAdapter(
    database_url=database_url,
    tracked_symbols=("BTC/USDT",),
    exchange=second_exchange,
    default_candle_limit=6,
    historical_candle_limit=6,
    clock=lambda: now + timedelta(minutes=5),
  )

  candles = second_adapter.get_candles(symbol="BTC/USDT", timeframe="5m", limit=4)

  assert len(candles) == 4
  assert second_exchange.calls == []


def test_binance_adapter_reports_gap_issues_in_sync_status(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=30),
    count=6,
    gap_after_index=2,
  )
  exchange = FakeExchange({("BTC/USDT", "5m"): rows})
  adapter = BinanceMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market-data.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange=exchange,
    default_candle_limit=6,
    clock=lambda: now,
  )

  adapter.sync_tracked("5m")
  status = adapter.get_status("5m")

  assert status.instruments[0].backfill_completion_ratio == 1.0
  assert status.instruments[0].backfill_complete is True
  assert status.instruments[0].backfill_contiguous_completion_ratio == pytest.approx(5 / 6)
  assert status.instruments[0].backfill_contiguous_complete is False
  assert status.instruments[0].backfill_contiguous_missing_candles == 1
  assert "missing_candles:1" in status.instruments[0].issues


def test_binance_adapter_request_path_reads_persisted_state_only(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=25),
    count=6,
  )
  exchange = FakeExchange({("BTC/USDT", "5m"): rows})
  adapter = BinanceMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market-data.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange=exchange,
    default_candle_limit=6,
    clock=lambda: now,
  )

  status = adapter.get_status("5m")
  candles = adapter.get_candles(symbol="BTC/USDT", timeframe="5m", limit=4)
  lineage = adapter.describe_lineage(
    symbol="BTC/USDT",
    timeframe="5m",
    candles=candles,
    limit=4,
  )

  assert exchange.calls == []
  assert status.instruments[0].sync_status == "empty"
  assert status.instruments[0].candle_count == 0
  assert status.instruments[0].backfill_target_candles == 6
  assert status.instruments[0].backfill_completion_ratio == 0.0
  assert status.instruments[0].backfill_complete is False
  assert status.instruments[0].backfill_contiguous_completion_ratio is None
  assert status.instruments[0].backfill_contiguous_complete is None
  assert status.instruments[0].backfill_contiguous_missing_candles is None
  assert candles == []
  assert lineage.sync_status == "empty"
  assert "insufficient_candle_coverage" in lineage.issues
