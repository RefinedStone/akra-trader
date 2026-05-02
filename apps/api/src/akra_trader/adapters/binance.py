from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import json
from pathlib import Path
from typing import Callable
from typing import Protocol
from uuid import uuid4

import ccxt
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import Candle
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
from akra_trader.domain.models import SyncCheckpoint
from akra_trader.domain.models import SyncFailure
from akra_trader.lineage import build_candle_dataset_identity
from akra_trader.lineage import build_dataset_boundary_contract
from akra_trader.lineage import build_sync_checkpoint_identity
from akra_trader.ports import MarketDataPort


from akra_trader.adapters.binance_schema import SUPPORTED_CCXT_MARKET_DATA_VENUES
from akra_trader.adapters.binance_schema import metadata
from akra_trader.adapters.binance_schema import market_candles
from akra_trader.adapters.binance_schema import market_ingestion_jobs
from akra_trader.adapters.binance_schema import market_lineage_history
from akra_trader.adapters.binance_schema import market_sync_failures
from akra_trader.adapters.binance_schema import market_sync_state
from akra_trader.adapters.binance_schema import OhlcvExchange
from akra_trader.adapters.binance_schema import BackfillSnapshot
from akra_trader.adapters.binance_schema import CandleCoverage
from akra_trader.adapters.binance_schema import QualitySnapshot
from akra_trader.adapters.binance_schema import SyncState
from akra_trader.adapters.binance_storage import CcxtMarketDataStorageMixin


def build_ccxt_exchange(*, venue: str = "binance") -> OhlcvExchange:
  exchange_factory = getattr(ccxt, venue, None)
  if not callable(exchange_factory):
    raise ValueError(f"Unsupported market data provider: {venue}")
  return exchange_factory({"enableRateLimit": True})


def build_binance_exchange() -> OhlcvExchange:
  return build_ccxt_exchange(venue="binance")


class CcxtMarketDataAdapter(CcxtMarketDataStorageMixin, MarketDataPort):
  def __init__(
    self,
    *,
    database_url: str,
    tracked_symbols: tuple[str, ...] = ("BTC/USDT", "ETH/USDT", "SOL/USDT"),
    venue: str = "binance",
    provider: str | None = None,
    default_candle_limit: int = 500,
    historical_candle_limit: int | None = None,
    exchange_batch_limit: int = 500,
    exchange: OhlcvExchange | None = None,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._database_url = database_url
    self._tracked_symbols = tracked_symbols
    self._venue = venue
    self._provider = provider or venue
    self._default_candle_limit = default_candle_limit
    self._historical_candle_limit = max(
      historical_candle_limit or default_candle_limit,
      default_candle_limit,
    )
    self._exchange_batch_limit = exchange_batch_limit
    self._exchange = exchange or build_ccxt_exchange(venue=venue)
    self._clock = clock or (lambda: datetime.now(UTC))
    self._engine = self._build_engine(database_url)
    metadata.create_all(self._engine)
    self._ensure_schema()

  def list_instruments(self) -> list[Instrument]:
    return [self._build_instrument(symbol) for symbol in self._tracked_symbols]

  def get_candles(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> list[Candle]:
    statement = select(market_candles).where(
      and_(
        market_candles.c.venue == self._venue,
        market_candles.c.symbol == symbol,
        market_candles.c.timeframe == timeframe,
      )
    )
    if start_at is not None:
      statement = statement.where(market_candles.c.timestamp >= start_at)
    if end_at is not None:
      statement = statement.where(market_candles.c.timestamp <= end_at)

    with self._engine.connect() as connection:
      if limit is None:
        rows = connection.execute(
          statement.order_by(market_candles.c.timestamp.asc())
        ).mappings().all()
      else:
        rows = connection.execute(
          statement.order_by(market_candles.c.timestamp.desc()).limit(limit)
        ).mappings().all()
        rows = list(reversed(rows))
    return [self._row_to_candle(row) for row in rows]

  def get_status(self, timeframe: str) -> MarketDataStatus:
    instruments: list[InstrumentStatus] = []
    for symbol in self._tracked_symbols:
      quality = self._build_quality_snapshot(symbol=symbol, timeframe=timeframe)
      backfill = self._build_backfill_snapshot(
        symbol=symbol,
        timeframe=timeframe,
        coverage=quality.coverage,
      )
      recent_failures = self._read_recent_failures(symbol=symbol, timeframe=timeframe)
      failure_count_24h = self._count_failures_since(
        symbol=symbol,
        timeframe=timeframe,
        since=self._clock() - timedelta(hours=24),
      )
      sync_checkpoint = quality.sync_state.checkpoint if quality.sync_state is not None else None
      if sync_checkpoint is None and quality.coverage.candle_count > 0:
        sync_checkpoint = self._build_sync_checkpoint(
          symbol=symbol,
          timeframe=timeframe,
          coverage=quality.coverage,
          contiguous_missing_candles=backfill.contiguous_missing_candles,
          recorded_at=quality.coverage.latest_ingested_at,
        )

      instruments.append(
        InstrumentStatus(
          instrument_id=f"{self._venue}:{symbol}",
          timeframe=timeframe,
          candle_count=quality.coverage.candle_count,
          first_timestamp=quality.coverage.first_timestamp,
          last_timestamp=quality.coverage.last_timestamp,
          sync_status=quality.sync_status,
          lag_seconds=quality.lag_seconds,
          last_sync_at=quality.sync_state.last_sync_at if quality.sync_state is not None else None,
          sync_checkpoint=sync_checkpoint,
          recent_failures=recent_failures,
          failure_count_24h=failure_count_24h,
          backfill_target_candles=backfill.target_candles,
          backfill_completion_ratio=backfill.completion_ratio,
          backfill_complete=backfill.complete,
          backfill_contiguous_completion_ratio=backfill.contiguous_completion_ratio,
          backfill_contiguous_complete=backfill.contiguous_complete,
          backfill_contiguous_missing_candles=backfill.contiguous_missing_candles,
          backfill_gap_windows=backfill.gap_windows,
          issues=self._build_status_issues(
            timeframe=timeframe,
            quality=quality,
            backfill=backfill,
            recent_failures=recent_failures,
            failure_count_24h=failure_count_24h,
          ),
        )
      )
    return MarketDataStatus(provider=self._provider, venue=self._venue, instruments=instruments)

  def list_lineage_history(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataLineageHistoryRecord, ...]:
    statement = select(market_lineage_history).where(market_lineage_history.c.venue == self._venue)
    if timeframe is not None:
      statement = statement.where(market_lineage_history.c.timeframe == timeframe)
    if symbol is not None:
      statement = statement.where(market_lineage_history.c.symbol == symbol)
    if sync_status is not None:
      statement = statement.where(market_lineage_history.c.sync_status == sync_status)
    if validation_claim is not None:
      statement = statement.where(market_lineage_history.c.validation_claim == validation_claim)
    statement = statement.order_by(
      market_lineage_history.c.recorded_at.desc(),
      market_lineage_history.c.history_id.desc(),
    )
    if limit is not None:
      statement = statement.limit(limit)
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(self._row_to_lineage_history_record(row) for row in rows)

  def list_ingestion_jobs(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataIngestionJobRecord, ...]:
    statement = select(market_ingestion_jobs).where(market_ingestion_jobs.c.venue == self._venue)
    if timeframe is not None:
      statement = statement.where(market_ingestion_jobs.c.timeframe == timeframe)
    if symbol is not None:
      statement = statement.where(market_ingestion_jobs.c.symbol == symbol)
    if operation is not None:
      statement = statement.where(market_ingestion_jobs.c.operation == operation)
    if status is not None:
      statement = statement.where(market_ingestion_jobs.c.status == status)
    statement = statement.order_by(
      market_ingestion_jobs.c.started_at.desc(),
      market_ingestion_jobs.c.job_id.desc(),
    )
    if limit is not None:
      statement = statement.limit(limit)
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(self._row_to_ingestion_job_record(row) for row in rows)

  def delete_market_data_lineage_history_records(
    self,
    history_ids: tuple[str, ...],
  ) -> int:
    if not history_ids:
      return 0
    statement = delete(market_lineage_history).where(
      and_(
        market_lineage_history.c.venue == self._venue,
        market_lineage_history.c.history_id.in_(history_ids),
      )
    )
    with self._engine.begin() as connection:
      result = connection.execute(statement)
    return int(result.rowcount or 0)

  def delete_market_data_ingestion_jobs(
    self,
    job_ids: tuple[str, ...],
  ) -> int:
    if not job_ids:
      return 0
    statement = delete(market_ingestion_jobs).where(
      and_(
        market_ingestion_jobs.c.venue == self._venue,
        market_ingestion_jobs.c.job_id.in_(job_ids),
      )
    )
    with self._engine.begin() as connection:
      result = connection.execute(statement)
    return int(result.rowcount or 0)

  def sync_tracked(self, timeframe: str) -> None:
    for symbol in self._tracked_symbols:
      if not self._sync_recent(symbol=symbol, timeframe=timeframe):
        continue
      self._backfill_history(
        symbol=symbol,
        timeframe=timeframe,
        target_candle_count=self._historical_candle_limit,
      )

  def remediate(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
  ) -> MarketDataRemediationResult:
    started_at = self._clock()
    detail = "market_data_remediation_not_supported"
    status = "not_supported"
    try:
      if kind == "recent_sync":
        successful = self._sync_recent(symbol=symbol, timeframe=timeframe)
      elif kind == "historical_backfill":
        recent_successful = self._sync_recent(symbol=symbol, timeframe=timeframe)
        backfill_successful = self._backfill_history(
          symbol=symbol,
          timeframe=timeframe,
          target_candle_count=self._historical_candle_limit,
        )
        successful = recent_successful and backfill_successful
      elif kind == "candle_repair":
        recent_successful = self._sync_recent(symbol=symbol, timeframe=timeframe)
        repaired_windows = self._repair_gap_windows(symbol=symbol, timeframe=timeframe)
        backfill_successful = self._backfill_history(
          symbol=symbol,
          timeframe=timeframe,
          target_candle_count=self._historical_candle_limit,
        )
        successful = recent_successful and backfill_successful
        status = "executed" if successful else "failed"
        detail = self._build_remediation_detail(
          kind=kind,
          symbol=symbol,
          timeframe=timeframe,
          repaired_windows=repaired_windows,
        )
        return MarketDataRemediationResult(
          kind=kind,
          symbol=symbol,
          timeframe=timeframe,
          status=status,
          started_at=started_at,
          finished_at=self._clock(),
          detail=detail,
        )
      elif kind in {"venue_fault_review", "market_data_review"}:
        recent_successful = self._sync_recent(symbol=symbol, timeframe=timeframe)
        backfill_successful = self._backfill_history(
          symbol=symbol,
          timeframe=timeframe,
          target_candle_count=self._historical_candle_limit,
        )
        successful = recent_successful and backfill_successful
      else:
        return MarketDataRemediationResult(
          kind=kind,
          symbol=symbol,
          timeframe=timeframe,
          status=status,
          started_at=started_at,
          finished_at=self._clock(),
          detail=detail,
        )
      status = "executed" if successful else "failed"
      detail = self._build_remediation_detail(
        kind=kind,
        symbol=symbol,
        timeframe=timeframe,
      )
    except Exception as exc:
      status = "failed"
      detail = f"market_data_remediation_failed:{exc}"
    return MarketDataRemediationResult(
      kind=kind,
      symbol=symbol,
      timeframe=timeframe,
      status=status,
      started_at=started_at,
      finished_at=self._clock(),
      detail=detail,
    )

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
    quality = self._build_quality_snapshot(symbol=symbol, timeframe=timeframe)
    sync_checkpoint = quality.sync_state.checkpoint if quality.sync_state is not None else None
    if sync_checkpoint is None and quality.coverage.candle_count > 0:
      sync_checkpoint = self._build_sync_checkpoint(
        symbol=symbol,
        timeframe=timeframe,
        coverage=quality.coverage,
      )
    issues = list(quality.issues)
    if limit is not None and len(candles) < limit:
      issues.append("insufficient_candle_coverage")
    dataset_identity = None
    reproducibility_state = "range_only"
    if candles:
      dataset_identity = build_candle_dataset_identity(
        provider=self._provider,
        venue=self._venue,
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
      )
      reproducibility_state = "pinned"
    return MarketDataLineage(
      provider=self._provider,
      venue=self._venue,
      symbols=(symbol,),
      timeframe=timeframe,
      dataset_identity=dataset_identity,
      sync_checkpoint_id=sync_checkpoint.checkpoint_id if sync_checkpoint is not None else None,
      reproducibility_state=reproducibility_state,
      requested_start_at=start_at,
      requested_end_at=end_at,
      effective_start_at=candles[0].timestamp if candles else None,
      effective_end_at=candles[-1].timestamp if candles else None,
      candle_count=len(candles),
      sync_status=quality.sync_status,
      last_sync_at=quality.sync_state.last_sync_at if quality.sync_state is not None else None,
      issues=tuple(issues),
    )

  def _build_instrument(self, symbol: str) -> Instrument:
    base_currency, quote_currency = symbol.split("/")
    return Instrument(
      symbol=symbol,
      venue=self._venue,
      base_currency=base_currency,
      quote_currency=quote_currency,
      asset_type=AssetType.CRYPTO,
      market_type=MarketType.SPOT,
    )

  @staticmethod
  def _symbol_from_instrument_id(instrument_id: str) -> str:
    _, _, symbol = instrument_id.partition(":")
    return symbol or instrument_id

  def _sync_recent(
    self,
    *,
    symbol: str,
    timeframe: str,
    required_count: int | None = None,
  ) -> bool:
    coverage = self._read_coverage(symbol=symbol, timeframe=timeframe)
    timeframe_delta = self._timeframe_delta(timeframe)
    requested_count = required_count or self._default_candle_limit
    if coverage.last_timestamp is None or coverage.candle_count < requested_count:
      lookback_count = max(requested_count, self._default_candle_limit)
      start_at = self._clock() - (timeframe_delta * max(lookback_count - 1, 1))
      return self._sync_range(
        symbol=symbol,
        timeframe=timeframe,
        start_at=start_at,
        end_at=None,
        limit=lookback_count,
      )
    started_at = self._clock()
    job_id = self._new_ingestion_job_id()
    try:
      raw = self._exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        since=self._to_exchange_milliseconds(coverage.last_timestamp + timeframe_delta),
        limit=self._exchange_batch_limit,
      )
      candles = self._normalize_ohlcv(raw)
      if candles:
        self._upsert_candles(symbol=symbol, timeframe=timeframe, candles=candles)
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="synced",
        last_error=None,
      )
      self._finalize_ingestion_job(
        job_id=job_id,
        symbol=symbol,
        timeframe=timeframe,
        operation="sync_recent",
        status="succeeded",
        started_at=started_at,
        finished_at=self._clock(),
        requested_start_at=coverage.last_timestamp + timeframe_delta,
        requested_end_at=None,
        requested_limit=self._exchange_batch_limit,
        fetched_candle_count=len(candles),
        last_error=None,
      )
      return True
    except Exception as exc:
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="error",
        last_error=str(exc),
      )
      self._record_failure_event(
        symbol=symbol,
        timeframe=timeframe,
        operation="sync_recent",
        error=str(exc),
      )
      self._finalize_ingestion_job(
        job_id=job_id,
        symbol=symbol,
        timeframe=timeframe,
        operation="sync_recent",
        status="failed",
        started_at=started_at,
        finished_at=self._clock(),
        requested_start_at=coverage.last_timestamp + timeframe_delta,
        requested_end_at=None,
        requested_limit=self._exchange_batch_limit,
        fetched_candle_count=0,
        last_error=str(exc),
      )
      return False

  def _sync_range(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None,
    end_at: datetime | None,
    limit: int | None,
  ) -> bool:
    timeframe_delta = self._timeframe_delta(timeframe)
    if start_at is None:
      start_at = self._clock() - (timeframe_delta * max((limit or self._default_candle_limit) - 1, 1))
    end_boundary = end_at or self._clock()
    remaining = limit or self._estimate_bar_count(
      start_at=start_at,
      end_at=end_boundary,
      timeframe=timeframe,
    )
    cursor = start_at
    started_at = self._clock()
    job_id = self._new_ingestion_job_id()
    fetched_candle_count = 0
    try:
      while cursor <= end_boundary and remaining > 0:
        batch_limit = min(max(remaining, 1), self._exchange_batch_limit)
        raw = self._exchange.fetch_ohlcv(
          symbol=symbol,
          timeframe=timeframe,
          since=self._to_exchange_milliseconds(cursor),
          limit=batch_limit,
        )
        candles = [
          candle
          for candle in self._normalize_ohlcv(raw)
          if candle.timestamp >= cursor and candle.timestamp <= end_boundary
        ]
        if not candles:
          break
        fetched_candle_count += len(candles)
        self._upsert_candles(symbol=symbol, timeframe=timeframe, candles=candles)
        next_cursor = candles[-1].timestamp + timeframe_delta
        remaining -= len(candles)
        if next_cursor <= cursor:
          break
        cursor = next_cursor
        if len(candles) < batch_limit:
          break
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="synced",
        last_error=None,
      )
      self._finalize_ingestion_job(
        job_id=job_id,
        symbol=symbol,
        timeframe=timeframe,
        operation="sync_range",
        status="succeeded",
        started_at=started_at,
        finished_at=self._clock(),
        requested_start_at=start_at,
        requested_end_at=end_boundary,
        requested_limit=limit,
        fetched_candle_count=fetched_candle_count,
        last_error=None,
      )
      return True
    except Exception as exc:
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="error",
        last_error=str(exc),
      )
      self._record_failure_event(
        symbol=symbol,
        timeframe=timeframe,
        operation="sync_range",
        error=str(exc),
      )
      self._finalize_ingestion_job(
        job_id=job_id,
        symbol=symbol,
        timeframe=timeframe,
        operation="sync_range",
        status="failed",
        started_at=started_at,
        finished_at=self._clock(),
        requested_start_at=start_at,
        requested_end_at=end_boundary,
        requested_limit=limit,
        fetched_candle_count=fetched_candle_count,
        last_error=str(exc),
      )
      return False

  def _backfill_history(
    self,
    *,
    symbol: str,
    timeframe: str,
    target_candle_count: int,
  ) -> bool:
    coverage = self._read_coverage(symbol=symbol, timeframe=timeframe)
    if coverage.first_timestamp is None or coverage.candle_count >= target_candle_count:
      return True

    timeframe_delta = self._timeframe_delta(timeframe)
    started_at = self._clock()
    job_id = self._new_ingestion_job_id()
    fetched_candle_count = 0
    requested_end_at = coverage.first_timestamp - timeframe_delta if coverage.first_timestamp is not None else None
    try:
      while coverage.first_timestamp is not None and coverage.candle_count < target_candle_count:
        remaining = target_candle_count - coverage.candle_count
        batch_limit = min(max(remaining, 1), self._exchange_batch_limit)
        start_at = coverage.first_timestamp - (timeframe_delta * batch_limit)
        raw = self._exchange.fetch_ohlcv(
          symbol=symbol,
          timeframe=timeframe,
          since=self._to_exchange_milliseconds(start_at),
          limit=batch_limit,
        )
        candles = [
          candle
          for candle in self._normalize_ohlcv(raw)
          if candle.timestamp < coverage.first_timestamp
        ]
        if not candles:
          break
        fetched_candle_count += len(candles)
        previous_coverage = coverage
        self._upsert_candles(symbol=symbol, timeframe=timeframe, candles=candles)
        coverage = self._read_coverage(symbol=symbol, timeframe=timeframe)
        if coverage.candle_count <= previous_coverage.candle_count:
          break
        if coverage.first_timestamp is None or coverage.first_timestamp >= previous_coverage.first_timestamp:
          break
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="synced",
        last_error=None,
      )
      self._finalize_ingestion_job(
        job_id=job_id,
        symbol=symbol,
        timeframe=timeframe,
        operation="backfill_history",
        status="succeeded",
        started_at=started_at,
        finished_at=self._clock(),
        requested_start_at=coverage.first_timestamp,
        requested_end_at=requested_end_at,
        requested_limit=target_candle_count,
        fetched_candle_count=fetched_candle_count,
        last_error=None,
      )
      return True
    except Exception as exc:
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="error",
        last_error=str(exc),
      )
      self._record_failure_event(
        symbol=symbol,
        timeframe=timeframe,
        operation="backfill_history",
        error=str(exc),
      )
      self._finalize_ingestion_job(
        job_id=job_id,
        symbol=symbol,
        timeframe=timeframe,
        operation="backfill_history",
        status="failed",
        started_at=started_at,
        finished_at=self._clock(),
        requested_start_at=coverage.first_timestamp,
        requested_end_at=requested_end_at,
        requested_limit=target_candle_count,
        fetched_candle_count=fetched_candle_count,
        last_error=str(exc),
      )
      return False

  def _upsert_candles(self, *, symbol: str, timeframe: str, candles: list[Candle]) -> None:
    ingested_at = self._clock()
    with self._engine.begin() as connection:
      for candle in candles:
        key_filter = and_(
          market_candles.c.venue == self._venue,
          market_candles.c.symbol == symbol,
          market_candles.c.timeframe == timeframe,
          market_candles.c.timestamp == candle.timestamp,
        )
        row = {
          "venue": self._venue,
          "symbol": symbol,
          "timeframe": timeframe,
          "timestamp": candle.timestamp,
          "open": candle.open,
          "high": candle.high,
          "low": candle.low,
          "close": candle.close,
          "volume": candle.volume,
          "ingested_at": ingested_at,
        }
        updated = connection.execute(update(market_candles).where(key_filter).values(**row))
        if updated.rowcount == 0:
          connection.execute(insert(market_candles).values(**row))

BinanceMarketDataAdapter = CcxtMarketDataAdapter
