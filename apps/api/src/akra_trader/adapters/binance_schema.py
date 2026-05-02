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
market_lineage_history = Table(
  "market_lineage_history",
  metadata,
  Column("history_id", String, primary_key=True),
  Column("source_job_id", String, nullable=True),
  Column("provider", String, nullable=False),
  Column("venue", String, nullable=False),
  Column("symbol", String, nullable=False),
  Column("timeframe", String, nullable=False),
  Column("recorded_at", DateTime(timezone=True), nullable=False),
  Column("sync_status", String, nullable=False),
  Column("validation_claim", String, nullable=False),
  Column("reproducibility_state", String, nullable=False),
  Column("boundary_id", String, nullable=True),
  Column("checkpoint_id", String, nullable=True),
  Column("first_timestamp", DateTime(timezone=True), nullable=True),
  Column("last_timestamp", DateTime(timezone=True), nullable=True),
  Column("candle_count", Integer, nullable=False),
  Column("lag_seconds", Integer, nullable=True),
  Column("last_sync_at", DateTime(timezone=True), nullable=True),
  Column("failure_count_24h", Integer, nullable=False),
  Column("contiguous_missing_candles", Integer, nullable=True),
  Column("gap_window_count", Integer, nullable=False),
  Column("last_error", Text, nullable=True),
  Column("issues_json", Text, nullable=False),
)
market_ingestion_jobs = Table(
  "market_ingestion_jobs",
  metadata,
  Column("job_id", String, primary_key=True),
  Column("provider", String, nullable=False),
  Column("venue", String, nullable=False),
  Column("symbol", String, nullable=False),
  Column("timeframe", String, nullable=False),
  Column("operation", String, nullable=False),
  Column("status", String, nullable=False),
  Column("started_at", DateTime(timezone=True), nullable=False),
  Column("finished_at", DateTime(timezone=True), nullable=False),
  Column("duration_ms", Integer, nullable=False),
  Column("fetched_candle_count", Integer, nullable=False),
  Column("validation_claim", String, nullable=True),
  Column("boundary_id", String, nullable=True),
  Column("checkpoint_id", String, nullable=True),
  Column("lineage_history_id", String, nullable=True),
  Column("requested_start_at", DateTime(timezone=True), nullable=True),
  Column("requested_end_at", DateTime(timezone=True), nullable=True),
  Column("requested_limit", Integer, nullable=True),
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
