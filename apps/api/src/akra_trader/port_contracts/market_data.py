from __future__ import annotations

from datetime import datetime
from typing import Protocol

from akra_trader.domain.models import Candle
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataStatus


class MarketDataPort(Protocol):
  def list_instruments(self) -> list[Instrument]: ...

  def get_candles(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> list[Candle]: ...

  def describe_lineage(
    self,
    *,
    symbol: str,
    timeframe: str,
    candles: list[Candle],
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> MarketDataLineage: ...

  def get_status(self, timeframe: str) -> MarketDataStatus: ...

  def list_lineage_history(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataLineageHistoryRecord, ...]: ...

  def list_ingestion_jobs(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataIngestionJobRecord, ...]: ...

  def remediate(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
  ) -> MarketDataRemediationResult: ...
