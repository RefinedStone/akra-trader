from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import Candle
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataSyncResult
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
from akra_trader.ports import MarketDataPort
from akra_trader.lineage import build_candle_dataset_identity
from akra_trader.lineage import build_dataset_boundary_contract


def build_seeded_market_data() -> dict[str, list[Candle]]:
  instruments = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
  start = datetime(2025, 1, 1, tzinfo=UTC)
  series: dict[str, list[Candle]] = {}
  for offset, symbol in enumerate(instruments):
    candles: list[Candle] = []
    price = 40_000.0 / (offset + 1)
    for index in range(240):
      timestamp = start + timedelta(minutes=5 * index)
      drift = 1 + (0.0008 * (index / 8))
      cycle = ((index % 24) - 12) / 280
      open_price = price
      close_price = price * drift + price * cycle
      high_price = max(open_price, close_price) * 1.004
      low_price = min(open_price, close_price) * 0.996
      volume = 500 + (index * 3) + (offset * 15)
      candles.append(
        Candle(
          timestamp=timestamp,
          open=round(open_price, 2),
          high=round(high_price, 2),
          low=round(low_price, 2),
          close=round(close_price, 2),
          volume=round(volume, 2),
        )
      )
      price = close_price
    series[symbol] = candles
  return series


class SeededMarketDataAdapter(MarketDataPort):
  def __init__(self, venue: str = "binance") -> None:
    self._venue = venue
    self._candles = build_seeded_market_data()
    self._instruments = [
      Instrument(
        symbol=symbol,
        venue=venue,
        base_currency=symbol.split("/")[0],
        quote_currency=symbol.split("/")[1],
        asset_type=AssetType.CRYPTO,
        market_type=MarketType.SPOT,
      )
      for symbol in self._candles
    ]

  def list_instruments(self) -> list[Instrument]:
    return list(self._instruments)

  def get_candles(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> list[Candle]:
    candles = list(self._candles.get(symbol, ()))
    if start_at is not None:
      candles = [candle for candle in candles if candle.timestamp >= start_at]
    if end_at is not None:
      candles = [candle for candle in candles if candle.timestamp <= end_at]
    if limit is not None:
      candles = candles[-limit:]
    return candles

  def ensure_candles(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> MarketDataSyncResult:
    candles = self.get_candles(
      symbol=symbol,
      timeframe=timeframe,
      start_at=start_at,
      end_at=end_at,
      limit=limit if start_at is None and end_at is None else None,
    )
    issues: list[str] = []
    if limit is not None and len(candles) < limit:
      issues.append("insufficient_fixture_coverage")
    if symbol not in self._candles:
      issues.append("fixture_symbol_unavailable")
    issues.extend(
      _build_requested_range_issues(
        candles=candles,
        timeframe=timeframe,
        start_at=start_at,
        end_at=end_at,
      )
    )
    return MarketDataSyncResult(
      provider="seeded",
      venue=self._venue,
      symbol=symbol,
      timeframe=timeframe,
      status="fixture",
      requested_start_at=start_at,
      requested_end_at=end_at,
      requested_limit=limit,
      effective_start_at=candles[0].timestamp if candles else None,
      effective_end_at=candles[-1].timestamp if candles else None,
      candle_count=len(candles),
      issues=tuple(issues),
    )

  def get_status(self, timeframe: str) -> MarketDataStatus:
    instruments = []
    for symbol, candles in self._candles.items():
      first = candles[0].timestamp if candles else None
      last = candles[-1].timestamp if candles else None
      instruments.append(
        InstrumentStatus(
          instrument_id=f"{self._venue}:{symbol}",
          timeframe=timeframe,
          candle_count=len(candles),
          first_timestamp=first,
          last_timestamp=last,
        )
      )
    return MarketDataStatus(provider="seeded", venue=self._venue, instruments=instruments)

  def list_lineage_history(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataLineageHistoryRecord, ...]:
    resolved_timeframe = timeframe or "5m"
    records: list[MarketDataLineageHistoryRecord] = []
    status = self.get_status(resolved_timeframe)
    for instrument in status.instruments:
      resolved_symbol = instrument.instrument_id.split(":", 1)[-1]
      if symbol is not None and resolved_symbol != symbol:
        continue
      candles = self.get_candles(symbol=resolved_symbol, timeframe=resolved_timeframe)
      lineage = self.describe_lineage(
        symbol=resolved_symbol,
        timeframe=resolved_timeframe,
        candles=candles,
      )
      dataset_boundary = build_dataset_boundary_contract(lineage=lineage)
      claim = dataset_boundary.validation_claim if dataset_boundary is not None else "window_only"
      if sync_status is not None and lineage.sync_status != sync_status:
        continue
      if validation_claim is not None and claim != validation_claim:
        continue
      recorded_at = candles[-1].timestamp if candles else datetime.now(UTC)
      records.append(
        MarketDataLineageHistoryRecord(
          history_id=f"seeded-lineage:{self._venue}:{resolved_symbol}:{resolved_timeframe}",
          source_job_id=None,
          provider="seeded",
          venue=self._venue,
          symbol=resolved_symbol,
          timeframe=resolved_timeframe,
          recorded_at=recorded_at,
          sync_status=lineage.sync_status,
          validation_claim=claim,
          reproducibility_state=lineage.reproducibility_state,
          boundary_id=dataset_boundary.boundary_id if dataset_boundary is not None else None,
          checkpoint_id=lineage.sync_checkpoint_id,
          dataset_boundary=dataset_boundary,
          first_timestamp=lineage.effective_start_at,
          last_timestamp=lineage.effective_end_at,
          candle_count=lineage.candle_count,
          lag_seconds=0 if candles else None,
          last_sync_at=recorded_at if candles else None,
          failure_count_24h=0,
          contiguous_missing_candles=0 if candles else None,
          gap_window_count=0,
          last_error=None,
          issues=lineage.issues,
        )
      )
    records.sort(key=lambda record: (record.recorded_at, record.history_id), reverse=True)
    if limit is not None:
      records = records[:limit]
    return tuple(records)

  def list_ingestion_jobs(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataIngestionJobRecord, ...]:
    del timeframe, symbol, operation, status, limit
    return ()

  def delete_market_data_lineage_history_records(
    self,
    history_ids: tuple[str, ...],
  ) -> int:
    del history_ids
    return 0

  def delete_market_data_ingestion_jobs(
    self,
    job_ids: tuple[str, ...],
  ) -> int:
    del job_ids
    return 0

  def describe_lineage(
    self,
    *,
    symbol: str,
    timeframe: str,
    candles: list[Candle],
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> MarketDataLineage:
    issues: list[str] = []
    if limit is not None and len(candles) < limit:
      issues.append("insufficient_fixture_coverage")
    issues.extend(
      _build_requested_range_issues(
        candles=candles,
        timeframe=timeframe,
        start_at=start_at,
        end_at=end_at,
      )
    )
    dataset_identity = None
    reproducibility_state = "range_only"
    if candles:
      dataset_identity = build_candle_dataset_identity(
        provider="seeded",
        venue=self._venue,
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
      )
      reproducibility_state = "pinned"
    return MarketDataLineage(
      provider="seeded",
      venue=self._venue,
      symbols=(symbol,),
      timeframe=timeframe,
      dataset_identity=dataset_identity,
      sync_checkpoint_id=None,
      reproducibility_state=reproducibility_state,
      requested_start_at=start_at,
      requested_end_at=end_at,
      effective_start_at=candles[0].timestamp if candles else None,
      effective_end_at=candles[-1].timestamp if candles else None,
      candle_count=len(candles),
      sync_status="fixture",
      issues=tuple(issues),
    )

  def remediate(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
  ) -> MarketDataRemediationResult:
    current_time = datetime.now(UTC)
    return MarketDataRemediationResult(
      kind=kind,
      symbol=symbol,
      timeframe=timeframe,
      status="skipped",
      started_at=current_time,
      finished_at=current_time,
      detail="seeded_market_data_provider_has_no_live_remediation_jobs",
    )



def candles_to_frame(candles: list[Candle]) -> pd.DataFrame:
  return pd.DataFrame(
    [
      {
        "timestamp": candle.timestamp,
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
      }
      for candle in candles
    ]
  )


def _build_requested_range_issues(
  *,
  candles: list[Candle],
  timeframe: str,
  start_at: datetime | None,
  end_at: datetime | None,
) -> tuple[str, ...]:
  if not candles:
    if start_at is not None or end_at is not None:
      return ("requested_range_empty",)
    return ()
  timeframe_delta = _timeframe_delta(timeframe)
  issues: list[str] = []
  if start_at is not None and candles[0].timestamp > start_at:
    issues.append("requested_start_missing")
  if end_at is not None and candles[-1].timestamp + timeframe_delta <= end_at:
    issues.append("requested_end_missing")
  for previous, current in zip(candles, candles[1:]):
    if current.timestamp - previous.timestamp > timeframe_delta:
      issues.append("requested_range_gap")
      break
  return tuple(issues)


def _timeframe_delta(timeframe: str) -> timedelta:
  unit = timeframe[-1:]
  amount = int(timeframe[:-1])
  if unit == "m":
    return timedelta(minutes=amount)
  if unit == "h":
    return timedelta(hours=amount)
  if unit == "d":
    return timedelta(days=amount)
  if unit == "w":
    return timedelta(weeks=amount)
  if unit == "M":
    return timedelta(days=30 * amount)
  return timedelta(minutes=5)
