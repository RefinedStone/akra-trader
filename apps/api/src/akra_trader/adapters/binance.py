from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Callable
from typing import Protocol

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
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
from akra_trader.domain.models import SyncCheckpoint
from akra_trader.domain.models import SyncFailure
from akra_trader.lineage import build_candle_dataset_identity
from akra_trader.lineage import build_sync_checkpoint_identity
from akra_trader.ports import MarketDataPort


metadata = MetaData()
market_candles = Table(
  "market_candles",
  metadata,
  Column("venue", String, primary_key=True),
  Column("symbol", String, primary_key=True),
  Column("timeframe", String, primary_key=True),
  Column("timestamp", DateTime(timezone=True), primary_key=True),
  Column("open", Float, nullable=False),
  Column("high", Float, nullable=False),
  Column("low", Float, nullable=False),
  Column("close", Float, nullable=False),
  Column("volume", Float, nullable=False),
  Column("ingested_at", DateTime(timezone=True), nullable=False),
)
market_sync_state = Table(
  "market_sync_state",
  metadata,
  Column("venue", String, primary_key=True),
  Column("symbol", String, primary_key=True),
  Column("timeframe", String, primary_key=True),
  Column("sync_status", String, nullable=False),
  Column("last_sync_at", DateTime(timezone=True), nullable=True),
  Column("last_error", Text, nullable=True),
  Column("checkpoint_id", String, nullable=True),
  Column("checkpoint_recorded_at", DateTime(timezone=True), nullable=True),
  Column("checkpoint_first_timestamp", DateTime(timezone=True), nullable=True),
  Column("checkpoint_last_timestamp", DateTime(timezone=True), nullable=True),
  Column("checkpoint_candle_count", Integer, nullable=True),
  Column("checkpoint_contiguous_missing_candles", Integer, nullable=True),
)
market_sync_failures = Table(
  "market_sync_failures",
  metadata,
  Column("failure_id", Integer, primary_key=True, autoincrement=True),
  Column("venue", String, nullable=False),
  Column("symbol", String, nullable=False),
  Column("timeframe", String, nullable=False),
  Column("operation", String, nullable=False),
  Column("failed_at", DateTime(timezone=True), nullable=False),
  Column("error", Text, nullable=False),
)

_TIMEFRAME_SECONDS = {
  "1m": 60,
  "3m": 3 * 60,
  "5m": 5 * 60,
  "15m": 15 * 60,
  "30m": 30 * 60,
  "1h": 60 * 60,
  "2h": 2 * 60 * 60,
  "4h": 4 * 60 * 60,
  "1d": 24 * 60 * 60,
}


class OhlcvExchange(Protocol):
  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "5m",
    since: int | None = None,
    limit: int | None = None,
  ) -> list[list[float]]: ...


@dataclass(frozen=True)
class CandleCoverage:
  candle_count: int
  first_timestamp: datetime | None
  last_timestamp: datetime | None
  latest_ingested_at: datetime | None


@dataclass(frozen=True)
class SyncState:
  sync_status: str
  last_sync_at: datetime | None
  last_error: str | None
  checkpoint: SyncCheckpoint | None = None


@dataclass(frozen=True)
class QualitySnapshot:
  coverage: CandleCoverage
  sync_state: SyncState | None
  lag_seconds: int | None
  sync_status: str
  issues: tuple[str, ...]


@dataclass(frozen=True)
class BackfillSnapshot:
  target_candles: int
  completion_ratio: float
  complete: bool
  contiguous_completion_ratio: float | None
  contiguous_complete: bool | None
  contiguous_missing_candles: int | None
  gap_windows: tuple[GapWindow, ...]


SUPPORTED_CCXT_MARKET_DATA_VENUES = ("binance", "coinbase", "kraken")


def build_ccxt_exchange(*, venue: str = "binance") -> OhlcvExchange:
  exchange_factory = getattr(ccxt, venue, None)
  if not callable(exchange_factory):
    raise ValueError(f"Unsupported market data provider: {venue}")
  return exchange_factory({"enableRateLimit": True})


def build_binance_exchange() -> OhlcvExchange:
  return build_ccxt_exchange(venue="binance")


class CcxtMarketDataAdapter(MarketDataPort):
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

  def sync_tracked(self, timeframe: str) -> None:
    for symbol in self._tracked_symbols:
      if not self._sync_recent(symbol=symbol, timeframe=timeframe):
        continue
      self._backfill_history(
        symbol=symbol,
        timeframe=timeframe,
        target_candle_count=self._historical_candle_limit,
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
    try:
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

  def _read_coverage(self, *, symbol: str, timeframe: str) -> CandleCoverage:
    statement = select(
      func.count().label("candle_count"),
      func.min(market_candles.c.timestamp).label("first_timestamp"),
      func.max(market_candles.c.timestamp).label("last_timestamp"),
      func.max(market_candles.c.ingested_at).label("latest_ingested_at"),
    ).where(
      and_(
        market_candles.c.venue == self._venue,
        market_candles.c.symbol == symbol,
        market_candles.c.timeframe == timeframe,
      )
    )
    with self._engine.connect() as connection:
      row = connection.execute(statement).mappings().one()
    return CandleCoverage(
      candle_count=int(row["candle_count"] or 0),
      first_timestamp=self._ensure_utc(row["first_timestamp"]),
      last_timestamp=self._ensure_utc(row["last_timestamp"]),
      latest_ingested_at=self._ensure_utc(row["latest_ingested_at"]),
    )

  def _read_sync_state(self, *, symbol: str, timeframe: str) -> SyncState | None:
    statement = select(market_sync_state).where(
      and_(
        market_sync_state.c.venue == self._venue,
        market_sync_state.c.symbol == symbol,
        market_sync_state.c.timeframe == timeframe,
      )
    )
    with self._engine.connect() as connection:
      row = connection.execute(statement).mappings().first()
    if row is None:
      return None
    checkpoint = None
    if row["checkpoint_id"] is not None and row["checkpoint_recorded_at"] is not None:
      checkpoint = SyncCheckpoint(
        checkpoint_id=row["checkpoint_id"],
        recorded_at=self._ensure_utc(row["checkpoint_recorded_at"]),
        candle_count=int(row["checkpoint_candle_count"] or 0),
        first_timestamp=self._ensure_utc(row["checkpoint_first_timestamp"]),
        last_timestamp=self._ensure_utc(row["checkpoint_last_timestamp"]),
        contiguous_missing_candles=int(row["checkpoint_contiguous_missing_candles"] or 0),
      )
    return SyncState(
      sync_status=row["sync_status"],
      last_sync_at=self._ensure_utc(row["last_sync_at"]),
      last_error=row["last_error"],
      checkpoint=checkpoint,
    )

  def _record_sync_state(
    self,
    *,
    symbol: str,
    timeframe: str,
    sync_status: str,
    last_error: str | None,
  ) -> None:
    row = {
      "venue": self._venue,
      "symbol": symbol,
      "timeframe": timeframe,
      "sync_status": sync_status,
      "last_sync_at": self._clock(),
      "last_error": last_error,
    }
    if sync_status == "synced":
      checkpoint = self._build_sync_checkpoint(
        symbol=symbol,
        timeframe=timeframe,
        coverage=self._read_coverage(symbol=symbol, timeframe=timeframe),
      )
      if checkpoint is not None:
        row.update(
          {
            "checkpoint_id": checkpoint.checkpoint_id,
            "checkpoint_recorded_at": checkpoint.recorded_at,
            "checkpoint_first_timestamp": checkpoint.first_timestamp,
            "checkpoint_last_timestamp": checkpoint.last_timestamp,
            "checkpoint_candle_count": checkpoint.candle_count,
            "checkpoint_contiguous_missing_candles": checkpoint.contiguous_missing_candles,
          }
        )
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(market_sync_state.c.symbol).where(
          and_(
            market_sync_state.c.venue == self._venue,
            market_sync_state.c.symbol == symbol,
            market_sync_state.c.timeframe == timeframe,
          )
        )
      ).first()
      if existing is None:
        connection.execute(insert(market_sync_state).values(**row))
      else:
        connection.execute(
          update(market_sync_state)
          .where(
            and_(
              market_sync_state.c.venue == self._venue,
              market_sync_state.c.symbol == symbol,
              market_sync_state.c.timeframe == timeframe,
            )
          )
          .values(**row)
        )

  def _record_failure_event(
    self,
    *,
    symbol: str,
    timeframe: str,
    operation: str,
    error: str,
  ) -> None:
    with self._engine.begin() as connection:
      connection.execute(
        insert(market_sync_failures).values(
          venue=self._venue,
          symbol=symbol,
          timeframe=timeframe,
          operation=operation,
          failed_at=self._clock(),
          error=error,
        )
      )

  def _read_recent_failures(
    self,
    *,
    symbol: str,
    timeframe: str,
    limit: int = 3,
  ) -> tuple[SyncFailure, ...]:
    statement = (
      select(market_sync_failures)
      .where(
        and_(
          market_sync_failures.c.venue == self._venue,
          market_sync_failures.c.symbol == symbol,
          market_sync_failures.c.timeframe == timeframe,
        )
      )
      .order_by(market_sync_failures.c.failed_at.desc(), market_sync_failures.c.failure_id.desc())
      .limit(limit)
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      SyncFailure(
        failed_at=self._ensure_utc(row["failed_at"]),
        operation=row["operation"],
        error=row["error"],
      )
      for row in rows
    )

  def _count_failures_since(
    self,
    *,
    symbol: str,
    timeframe: str,
    since: datetime,
  ) -> int:
    statement = select(func.count()).where(
      and_(
        market_sync_failures.c.venue == self._venue,
        market_sync_failures.c.symbol == symbol,
        market_sync_failures.c.timeframe == timeframe,
        market_sync_failures.c.failed_at >= since,
      )
    )
    with self._engine.connect() as connection:
      return int(connection.execute(statement).scalar_one())

  def _build_sync_checkpoint(
    self,
    *,
    symbol: str,
    timeframe: str,
    coverage: CandleCoverage,
    contiguous_missing_candles: int | None = None,
    recorded_at: datetime | None = None,
  ) -> SyncCheckpoint | None:
    if coverage.candle_count == 0 or coverage.latest_ingested_at is None:
      return None
    missing_candles = (
      contiguous_missing_candles
      if contiguous_missing_candles is not None
      else self._count_missing_candles(symbol=symbol, timeframe=timeframe)
    )
    return SyncCheckpoint(
      checkpoint_id=build_sync_checkpoint_identity(
        provider=self._provider,
        venue=self._venue,
        symbol=symbol,
        timeframe=timeframe,
        candle_count=coverage.candle_count,
        first_timestamp=coverage.first_timestamp,
        last_timestamp=coverage.last_timestamp,
        latest_ingested_at=coverage.latest_ingested_at,
        contiguous_missing_candles=missing_candles,
      ),
      recorded_at=recorded_at or self._clock(),
      candle_count=coverage.candle_count,
      first_timestamp=coverage.first_timestamp,
      last_timestamp=coverage.last_timestamp,
      contiguous_missing_candles=missing_candles,
    )

  def _build_quality_snapshot(self, *, symbol: str, timeframe: str) -> QualitySnapshot:
    coverage = self._read_coverage(symbol=symbol, timeframe=timeframe)
    sync_state = self._read_sync_state(symbol=symbol, timeframe=timeframe)
    lag_seconds = self._calculate_lag_seconds(coverage.last_timestamp)
    missing_candles = self._count_missing_candles(symbol=symbol, timeframe=timeframe)
    issues: list[str] = []
    sync_status = "empty"
    if coverage.candle_count > 0:
      sync_status = "synced"
    if sync_state is not None and sync_state.sync_status == "error":
      sync_status = "error"
      issues.append("last_sync_failed")
    elif lag_seconds is not None and lag_seconds > self._freshness_threshold_seconds(timeframe):
      sync_status = "stale"
      issues.append("lagging")
      issues.append(
        f"freshness_threshold_exceeded:{lag_seconds}:{self._freshness_threshold_seconds(timeframe)}"
      )
    if missing_candles > 0:
      issues.append(f"missing_candles:{missing_candles}")
    return QualitySnapshot(
      coverage=coverage,
      sync_state=sync_state,
      lag_seconds=lag_seconds,
      sync_status=sync_status,
      issues=tuple(issues),
    )

  def _build_backfill_snapshot(
    self,
    *,
    symbol: str,
    timeframe: str,
    coverage: CandleCoverage,
  ) -> BackfillSnapshot:
    target_candles = self._historical_candle_limit
    completion_ratio = min(coverage.candle_count / target_candles, 1.0) if target_candles > 0 else 0.0
    complete = coverage.candle_count >= target_candles

    if (
      target_candles <= 0
      or coverage.first_timestamp is None
      or coverage.last_timestamp is None
      or coverage.candle_count == 0
    ):
      return BackfillSnapshot(
        target_candles=target_candles,
        completion_ratio=completion_ratio,
        complete=complete,
        contiguous_completion_ratio=None,
        contiguous_complete=None,
        contiguous_missing_candles=None,
        gap_windows=(),
      )

    timeframe_delta = self._timeframe_delta(timeframe)
    window_start = coverage.first_timestamp
    expected_candle_count = self._estimate_bar_count(
      start_at=coverage.first_timestamp,
      end_at=coverage.last_timestamp,
      timeframe=timeframe,
    )
    if complete:
      window_start = coverage.last_timestamp - (timeframe_delta * max(target_candles - 1, 0))
      expected_candle_count = target_candles

    timestamps = self._read_timestamps(
      symbol=symbol,
      timeframe=timeframe,
      start_at=window_start,
      end_at=coverage.last_timestamp,
    )
    gap_windows = self._build_gap_windows_from_timestamps(
      timestamps=timestamps,
      timeframe=timeframe,
    )
    missing_candles = sum(window.missing_candles for window in gap_windows)
    contiguous_completion_ratio = (
      min(len(timestamps) / expected_candle_count, 1.0)
      if expected_candle_count > 0
      else None
    )
    return BackfillSnapshot(
      target_candles=target_candles,
      completion_ratio=completion_ratio,
      complete=complete,
      contiguous_completion_ratio=contiguous_completion_ratio,
      contiguous_complete=missing_candles == 0,
      contiguous_missing_candles=missing_candles,
      gap_windows=gap_windows,
    )

  def _build_status_issues(
    self,
    *,
    timeframe: str,
    quality: QualitySnapshot,
    backfill: BackfillSnapshot,
    recent_failures: tuple[SyncFailure, ...],
    failure_count_24h: int,
  ) -> tuple[str, ...]:
    issues = list(quality.issues)
    if (
      backfill.target_candles is not None
      and backfill.target_candles > 0
      and quality.coverage.candle_count > 0
      and backfill.complete is False
    ):
      issues.append(
        f"backfill_target_incomplete:{quality.coverage.candle_count}:{backfill.target_candles}"
      )
    if backfill.contiguous_missing_candles is not None and backfill.contiguous_missing_candles > 0:
      issues.append(f"contiguous_backfill_incomplete:{backfill.contiguous_missing_candles}")
      issues.append(f"gap_windows:{len(backfill.gap_windows)}")
    if failure_count_24h > 0:
      issues.append(
        f"{'repeated_sync_failures' if failure_count_24h > 1 else 'recent_sync_failure'}:{failure_count_24h}"
      )
    for failure in recent_failures:
      issues.extend(self._classify_failure_semantics(failure.error))
    return tuple(dict.fromkeys(issues))

  def _classify_failure_semantics(self, error: str) -> tuple[str, ...]:
    normalized = error.lower()
    semantics: list[str] = []
    if "timeout" in normalized or "timed out" in normalized:
      semantics.append(f"{self._venue}_timeout")
    if (
      "rate limit" in normalized
      or "too many requests" in normalized
      or "429" in normalized
      or "throttle" in normalized
    ):
      semantics.append(f"{self._venue}_rate_limited")
    if (
      "network" in normalized
      or "connection" in normalized
      or "socket" in normalized
      or "dns" in normalized
    ):
      semantics.append(f"{self._venue}_network_fault")
    if (
      "auth" in normalized
      or "api key" in normalized
      or "api-key" in normalized
      or "signature" in normalized
      or "forbidden" in normalized
      or "unauthorized" in normalized
      or "permission denied" in normalized
    ):
      semantics.append(f"{self._venue}_auth_fault")
    if (
      "invalid symbol" in normalized
      or "unknown symbol" in normalized
      or "symbol not found" in normalized
      or "market not found" in normalized
      or "unknown market" in normalized
    ):
      semantics.append(f"{self._venue}_symbol_unavailable")
    if (
      "maintenance" in normalized
      or "service unavailable" in normalized
      or "system upgrade" in normalized
    ):
      semantics.append(f"{self._venue}_maintenance")
    if not semantics:
      semantics.append(f"{self._venue}_upstream_fault")
    return tuple(dict.fromkeys(semantics))

  def _count_missing_candles(self, *, symbol: str, timeframe: str) -> int:
    timestamps = self._read_timestamps(symbol=symbol, timeframe=timeframe)
    return sum(
      window.missing_candles
      for window in self._build_gap_windows_from_timestamps(
        timestamps=timestamps,
        timeframe=timeframe,
      )
    )

  def _build_gap_windows_from_timestamps(
    self,
    *,
    timestamps: list[datetime],
    timeframe: str,
  ) -> tuple[GapWindow, ...]:
    if len(timestamps) < 2:
      return ()

    timeframe_delta = self._timeframe_delta(timeframe)
    windows: list[GapWindow] = []
    for previous, current in zip(timestamps, timestamps[1:]):
      gap_size = int((current - previous).total_seconds() // timeframe_delta.total_seconds()) - 1
      if gap_size > 0:
        windows.append(
          GapWindow(
            start_at=previous + timeframe_delta,
            end_at=current - timeframe_delta,
            missing_candles=gap_size,
          )
        )
    return tuple(windows)

  def _read_timestamps(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> list[datetime]:
    statement = select(market_candles.c.timestamp).where(
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
    statement = statement.order_by(market_candles.c.timestamp.asc())
    with self._engine.connect() as connection:
      return [self._ensure_utc(row[0]) for row in connection.execute(statement).all()]

  def _calculate_lag_seconds(self, last_timestamp: datetime | None) -> int | None:
    if last_timestamp is None:
      return None
    return max(int((self._clock() - last_timestamp).total_seconds()), 0)

  def _estimate_bar_count(self, *, start_at: datetime, end_at: datetime, timeframe: str) -> int:
    if end_at <= start_at:
      return 1
    timeframe_seconds = self._timeframe_seconds(timeframe)
    return max(int(((end_at - start_at).total_seconds() // timeframe_seconds) + 1), 1)

  def _freshness_threshold_seconds(self, timeframe: str) -> int:
    return self._timeframe_seconds(timeframe) * 2

  def _timeframe_delta(self, timeframe: str) -> timedelta:
    return timedelta(seconds=self._timeframe_seconds(timeframe))

  def _timeframe_seconds(self, timeframe: str) -> int:
    if timeframe not in _TIMEFRAME_SECONDS:
      raise ValueError(f"Unsupported timeframe: {timeframe}")
    return _TIMEFRAME_SECONDS[timeframe]

  def _normalize_ohlcv(self, raw_candles: list[list[float]]) -> list[Candle]:
    candles: list[Candle] = []
    for row in raw_candles:
      if len(row) < 6:
        continue
      candles.append(
        Candle(
          timestamp=datetime.fromtimestamp(row[0] / 1000, tz=UTC),
          open=float(row[1]),
          high=float(row[2]),
          low=float(row[3]),
          close=float(row[4]),
          volume=float(row[5]),
        )
      )
    return candles

  def _row_to_candle(self, row: dict) -> Candle:
    return Candle(
      timestamp=self._ensure_utc(row["timestamp"]),
      open=row["open"],
      high=row["high"],
      low=row["low"],
      close=row["close"],
      volume=row["volume"],
    )

  def _to_exchange_milliseconds(self, value: datetime) -> int:
    return int(value.timestamp() * 1000)

  def _ensure_utc(self, value: datetime | None) -> datetime | None:
    if value is None:
      return None
    if value.tzinfo is None:
      return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)

  def _ensure_schema(self) -> None:
    inspector = inspect(self._engine)
    existing_columns = {
      column["name"]
      for column in inspector.get_columns("market_sync_state")
    }
    missing_columns = {
      "checkpoint_id": "TEXT",
      "checkpoint_recorded_at": "TIMESTAMP",
      "checkpoint_first_timestamp": "TIMESTAMP",
      "checkpoint_last_timestamp": "TIMESTAMP",
      "checkpoint_candle_count": "INTEGER",
      "checkpoint_contiguous_missing_candles": "INTEGER",
    }
    with self._engine.begin() as connection:
      for column_name, column_type in missing_columns.items():
        if column_name in existing_columns:
          continue
        connection.exec_driver_sql(
          f"ALTER TABLE market_sync_state ADD COLUMN {column_name} {column_type}"
        )

  def _build_engine(self, database_url: str) -> Engine:
    url = make_url(database_url)
    engine_kwargs = {"pool_pre_ping": True}
    if url.get_backend_name() == "sqlite" and url.database not in {None, "", ":memory:"}:
      Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
      return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        **engine_kwargs,
      )
    return create_engine(database_url, **engine_kwargs)


BinanceMarketDataAdapter = CcxtMarketDataAdapter
