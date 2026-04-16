from __future__ import annotations

from datetime import datetime
from typing import Protocol

import pandas as pd

from akra_trader.domain.models import Candle
from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueSessionRestore
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.domain.models import WarmupSpec


class StrategyRuntime(Protocol):
  def describe(self) -> StrategyMetadata: ...

  def warmup_spec(self) -> WarmupSpec: ...

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame: ...

  def build_decision_context(
    self,
    candles: pd.DataFrame,
    parameters: dict,
    state: StrategyExecutionState,
  ) -> StrategyDecisionContext: ...

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope: ...


class DecisionEnginePort(Protocol):
  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope: ...


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


class StrategyCatalogPort(Protocol):
  def list_strategies(
    self,
    *,
    runtime: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]: ...

  def load(self, strategy_id: str) -> StrategyRuntime: ...

  def register(self, registration: StrategyRegistration) -> StrategyMetadata: ...

  def get_registration(self, strategy_id: str) -> StrategyRegistration | None: ...


class ReferenceCatalogPort(Protocol):
  def list_entries(self) -> list[ReferenceSource]: ...

  def get(self, reference_id: str) -> ReferenceSource: ...


class RunRepositoryPort(Protocol):
  def save_run(self, run: RunRecord) -> RunRecord: ...

  def get_run(self, run_id: str) -> RunRecord | None: ...

  def compare_runs(self, run_ids: list[str]) -> list[RunRecord]: ...

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
  ) -> list[RunRecord]: ...

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None: ...


class GuardedLiveStatePort(Protocol):
  def load_state(self) -> GuardedLiveState: ...

  def save_state(self, state: GuardedLiveState) -> GuardedLiveState: ...


class VenueStatePort(Protocol):
  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot: ...


class VenueExecutionPort(Protocol):
  def describe_capability(self) -> tuple[bool, tuple[str, ...]]: ...

  def restore_session(
    self,
    *,
    symbol: str,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionRestore: ...

  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult: ...

  def submit_limit_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult: ...

  def cancel_order(
    self,
    *,
    symbol: str,
    order_id: str,
  ) -> GuardedLiveVenueOrderResult: ...

  def sync_order_states(
    self,
    *,
    symbol: str,
    order_ids: tuple[str, ...],
  ) -> tuple[GuardedLiveVenueOrderResult, ...]: ...
