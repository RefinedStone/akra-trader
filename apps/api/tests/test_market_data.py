from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest

from akra_trader.adapters.binance import BinanceMarketDataAdapter
from akra_trader.adapters.binance import CcxtMarketDataAdapter


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


class BrokenExchange:
  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "5m",
    since: int | None = None,
    limit: int | None = None,
  ) -> list[list[float]]:
    raise RuntimeError(f"upstream fetch failed for {symbol} {timeframe}")


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
  assert status.instruments[0].sync_checkpoint is not None
  assert status.instruments[0].sync_checkpoint.checkpoint_id.startswith("checkpoint-v1:")
  assert status.instruments[0].sync_checkpoint.candle_count == 6
  assert status.instruments[0].sync_checkpoint.last_timestamp == now
  assert status.instruments[0].recent_failures == ()
  assert status.instruments[0].failure_count_24h == 0
  assert status.instruments[0].backfill_target_candles == 6
  assert status.instruments[0].backfill_completion_ratio == 1.0
  assert status.instruments[0].backfill_complete is True
  assert status.instruments[0].backfill_contiguous_completion_ratio == 1.0
  assert status.instruments[0].backfill_contiguous_complete is True
  assert status.instruments[0].backfill_contiguous_missing_candles == 0
  assert status.instruments[0].backfill_gap_windows == ()
  assert not status.instruments[0].issues
  assert len(candles) == 4
  assert candles[-1].close == 105.5
  assert lineage.provider == "binance"
  assert lineage.dataset_identity is not None
  assert lineage.dataset_identity.startswith("candles-v1:")
  assert lineage.reproducibility_state == "pinned"
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
  assert status.instruments[0].backfill_gap_windows == ()
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
  assert len(status.instruments[0].backfill_gap_windows) == 1
  assert status.instruments[0].backfill_gap_windows[0].start_at == now - timedelta(minutes=15)
  assert status.instruments[0].backfill_gap_windows[0].end_at == now - timedelta(minutes=15)
  assert status.instruments[0].backfill_gap_windows[0].missing_candles == 1
  assert "missing_candles:1" in status.instruments[0].issues
  assert "contiguous_backfill_incomplete:1" in status.instruments[0].issues
  assert "gap_windows:1" in status.instruments[0].issues


def test_binance_adapter_recent_sync_remediation_executes_and_refreshes_status(tmp_path: Path) -> None:
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
    historical_candle_limit=6,
    clock=lambda: now,
  )

  result = adapter.remediate(
    kind="recent_sync",
    symbol="BTC/USDT",
    timeframe="5m",
  )
  status = adapter.get_status("5m")

  assert result.status == "executed"
  assert "sync_status=synced" in result.detail
  assert status.instruments[0].sync_status == "synced"
  assert status.instruments[0].candle_count == 6


def test_binance_adapter_candle_repair_remediation_closes_gap_windows(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  gap_rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=30),
    count=6,
    gap_after_index=2,
  )
  full_rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=30),
    count=7,
  )
  adapter = BinanceMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market-data.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange=FakeExchange({("BTC/USDT", "5m"): gap_rows}),
    default_candle_limit=6,
    historical_candle_limit=6,
    exchange_batch_limit=6,
    clock=lambda: now,
  )

  adapter.sync_tracked("5m")
  adapter._exchange = FakeExchange({("BTC/USDT", "5m"): full_rows})

  result = adapter.remediate(
    kind="candle_repair",
    symbol="BTC/USDT",
    timeframe="5m",
  )
  status = adapter.get_status("5m")

  assert result.status == "executed"
  assert "repaired_gap_windows=1" in result.detail
  assert status.instruments[0].backfill_contiguous_missing_candles == 0
  assert status.instruments[0].backfill_gap_windows == ()


def test_binance_adapter_status_exposes_checkpoint_and_recent_failure_history(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=25),
    count=6,
  )
  database_url = f"sqlite:///{tmp_path / 'market-data.sqlite3'}"
  healthy_adapter = BinanceMarketDataAdapter(
    database_url=database_url,
    tracked_symbols=("BTC/USDT",),
    exchange=FakeExchange({("BTC/USDT", "5m"): rows}),
    default_candle_limit=6,
    historical_candle_limit=6,
    clock=lambda: now,
  )
  healthy_adapter.sync_tracked("5m")
  initial_status = healthy_adapter.get_status("5m")

  degraded_adapter = BinanceMarketDataAdapter(
    database_url=database_url,
    tracked_symbols=("BTC/USDT",),
    exchange=BrokenExchange(),
    default_candle_limit=6,
    historical_candle_limit=6,
    clock=lambda: now + timedelta(minutes=5),
  )
  degraded_adapter.sync_tracked("5m")
  degraded_status = degraded_adapter.get_status("5m")

  initial_checkpoint = initial_status.instruments[0].sync_checkpoint
  degraded_instrument = degraded_status.instruments[0]

  assert initial_checkpoint is not None
  assert degraded_instrument.sync_status == "error"
  assert degraded_instrument.sync_checkpoint == initial_checkpoint
  assert degraded_instrument.failure_count_24h == 1
  assert len(degraded_instrument.recent_failures) == 1
  assert degraded_instrument.recent_failures[0].operation == "sync_recent"
  assert "upstream fetch failed" in degraded_instrument.recent_failures[0].error
  assert "last_sync_failed" in degraded_instrument.issues
  assert "recent_sync_failure:1" in degraded_instrument.issues
  assert "binance_upstream_fault" in degraded_instrument.issues


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
  assert status.instruments[0].sync_checkpoint is None
  assert status.instruments[0].recent_failures == ()
  assert status.instruments[0].failure_count_24h == 0
  assert status.instruments[0].backfill_target_candles == 6
  assert status.instruments[0].backfill_completion_ratio == 0.0
  assert status.instruments[0].backfill_complete is False
  assert status.instruments[0].backfill_contiguous_completion_ratio is None
  assert status.instruments[0].backfill_contiguous_complete is None
  assert status.instruments[0].backfill_contiguous_missing_candles is None
  assert status.instruments[0].backfill_gap_windows == ()
  assert candles == []
  assert lineage.dataset_identity is None
  assert lineage.reproducibility_state == "range_only"
  assert lineage.sync_status == "empty"
  assert "insufficient_candle_coverage" in lineage.issues


def test_ccxt_adapter_supports_supported_non_binance_provider(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = build_ohlcv_rows(
    start_at=now - timedelta(minutes=25),
    count=6,
  )
  exchange = FakeExchange({("BTC/USDT", "5m"): rows})
  adapter = CcxtMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market-data.sqlite3'}",
    venue="coinbase",
    tracked_symbols=("BTC/USDT",),
    exchange=exchange,
    default_candle_limit=6,
    historical_candle_limit=6,
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

  assert status.provider == "coinbase"
  assert status.venue == "coinbase"
  assert status.instruments[0].instrument_id == "coinbase:BTC/USDT"
  assert status.instruments[0].sync_checkpoint is not None
  assert status.instruments[0].sync_checkpoint.checkpoint_id.startswith("checkpoint-v1:")
  assert lineage.provider == "coinbase"
  assert lineage.venue == "coinbase"
  assert lineage.dataset_identity is not None
  assert lineage.sync_checkpoint_id == status.instruments[0].sync_checkpoint.checkpoint_id
