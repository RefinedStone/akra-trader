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
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import Candle
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
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


@dataclass(frozen=True)
class SyncState:
  sync_status: str
  last_sync_at: datetime | None
  last_error: str | None


@dataclass(frozen=True)
class QualitySnapshot:
  coverage: CandleCoverage
  sync_state: SyncState | None
  lag_seconds: int | None
  sync_status: str
  issues: tuple[str, ...]


def build_binance_exchange() -> OhlcvExchange:
  return ccxt.binance({"enableRateLimit": True})


class BinanceMarketDataAdapter(MarketDataPort):
  def __init__(
    self,
    *,
    database_url: str,
    tracked_symbols: tuple[str, ...] = ("BTC/USDT", "ETH/USDT", "SOL/USDT"),
    venue: str = "binance",
    default_candle_limit: int = 500,
    exchange_batch_limit: int = 500,
    exchange: OhlcvExchange | None = None,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._database_url = database_url
    self._tracked_symbols = tracked_symbols
    self._venue = venue
    self._default_candle_limit = default_candle_limit
    self._exchange_batch_limit = exchange_batch_limit
    self._exchange = exchange or build_binance_exchange()
    self._clock = clock or (lambda: datetime.now(UTC))
    self._engine = self._build_engine(database_url)
    metadata.create_all(self._engine)

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
          issues=quality.issues,
        )
      )
    return MarketDataStatus(provider="binance", venue=self._venue, instruments=instruments)

  def sync_tracked(self, timeframe: str) -> None:
    for symbol in self._tracked_symbols:
      self._sync_recent(symbol=symbol, timeframe=timeframe)

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
    issues = list(quality.issues)
    if limit is not None and len(candles) < limit:
      issues.append("insufficient_candle_coverage")
    return MarketDataLineage(
      provider="binance",
      venue=self._venue,
      symbols=(symbol,),
      timeframe=timeframe,
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
  ) -> None:
    coverage = self._read_coverage(symbol=symbol, timeframe=timeframe)
    timeframe_delta = self._timeframe_delta(timeframe)
    requested_count = required_count or self._default_candle_limit
    try:
      if coverage.last_timestamp is None or coverage.candle_count < requested_count:
        lookback_count = max(requested_count, self._default_candle_limit)
        start_at = self._clock() - (timeframe_delta * max(lookback_count - 1, 1))
        self._sync_range(
          symbol=symbol,
          timeframe=timeframe,
          start_at=start_at,
          end_at=None,
          limit=lookback_count,
        )
      else:
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
    except Exception as exc:
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="error",
        last_error=str(exc),
      )

  def _sync_range(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None,
    end_at: datetime | None,
    limit: int | None,
  ) -> None:
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
    except Exception as exc:
      self._record_sync_state(
        symbol=symbol,
        timeframe=timeframe,
        sync_status="error",
        last_error=str(exc),
      )

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
    return SyncState(
      sync_status=row["sync_status"],
      last_sync_at=self._ensure_utc(row["last_sync_at"]),
      last_error=row["last_error"],
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
    if missing_candles > 0:
      issues.append(f"missing_candles:{missing_candles}")
    return QualitySnapshot(
      coverage=coverage,
      sync_state=sync_state,
      lag_seconds=lag_seconds,
      sync_status=sync_status,
      issues=tuple(issues),
    )

  def _count_missing_candles(self, *, symbol: str, timeframe: str) -> int:
    statement = select(market_candles.c.timestamp).where(
      and_(
        market_candles.c.venue == self._venue,
        market_candles.c.symbol == symbol,
        market_candles.c.timeframe == timeframe,
      )
    ).order_by(market_candles.c.timestamp.asc())
    with self._engine.connect() as connection:
      timestamps = [row[0] for row in connection.execute(statement).all()]
    if len(timestamps) < 2:
      return 0

    timeframe_seconds = self._timeframe_seconds(timeframe)
    missing_candles = 0
    for previous, current in zip(timestamps, timestamps[1:]):
      gap_size = int((current - previous).total_seconds() // timeframe_seconds) - 1
      if gap_size > 0:
        missing_candles += gap_size
    return missing_candles

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
