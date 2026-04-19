from __future__ import annotations

from collections import OrderedDict
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from importlib import import_module
from typing import Iterable

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import Candle
from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyCatalogSemantics
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.ports import MarketDataPort
from akra_trader.ports import ExperimentPresetCatalogPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.lineage import build_candle_dataset_identity
from akra_trader.strategies.base import Strategy
from akra_trader.strategies.examples import MovingAverageCrossStrategy
from akra_trader.strategies.reference import build_reference_strategies


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


class InMemoryRunRepository(RunRepositoryPort):
  def __init__(self) -> None:
    self._runs: OrderedDict[str, RunRecord] = OrderedDict()

  def save_run(self, run: RunRecord) -> RunRecord:
    self._runs[run.config.run_id] = run
    return run

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get(run_id)

  def compare_runs(self, run_ids: list[str]) -> list[RunRecord]:
    return [run for run_id in run_ids if (run := self._runs.get(run_id)) is not None]

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
    preset_id: str | None = None,
    benchmark_family: str | None = None,
    dataset_identity: str | None = None,
    tags: tuple[str, ...] = (),
  ) -> list[RunRecord]:
    values = list(self._runs.values())
    runs = list(reversed(values))
    if mode is not None:
      runs = [run for run in runs if run.config.mode.value == mode]
    if strategy_id is not None:
      runs = [run for run in runs if run.config.strategy_id == strategy_id]
    if strategy_version is not None:
      runs = [run for run in runs if run.config.strategy_version == strategy_version]
    if rerun_boundary_id is not None:
      runs = [run for run in runs if run.provenance.rerun_boundary_id == rerun_boundary_id]
    if preset_id is not None:
      runs = [run for run in runs if run.provenance.experiment.preset_id == preset_id]
    if benchmark_family is not None:
      runs = [run for run in runs if run.provenance.experiment.benchmark_family == benchmark_family]
    if dataset_identity is not None:
      runs = [
        run
        for run in runs
        if run.provenance.market_data is not None
        and run.provenance.market_data.dataset_identity == dataset_identity
      ]
    if tags:
      required_tags = set(tags)
      runs = [
        run
        for run in runs
        if required_tags.issubset(set(run.provenance.experiment.tags))
      ]
    return runs

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None:
    run = self._runs.get(run_id)
    if run is None:
      return None
    run.status = status
    if status in {RunStatus.COMPLETED, RunStatus.STOPPED, RunStatus.FAILED}:
      run.ended_at = datetime.now(UTC)
    return run


class InMemoryExperimentPresetCatalog(ExperimentPresetCatalogPort):
  def __init__(self) -> None:
    self._presets: OrderedDict[str, ExperimentPreset] = OrderedDict()

  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    presets = list(reversed(self._presets.values()))
    if strategy_id is not None:
      presets = [
        preset
        for preset in presets
        if preset.strategy_id is None or preset.strategy_id == strategy_id
      ]
    if timeframe is not None:
      presets = [
        preset
        for preset in presets
        if preset.timeframe is None or preset.timeframe == timeframe
      ]
    if lifecycle_stage is not None:
      presets = [
        preset
        for preset in presets
        if preset.lifecycle.stage == lifecycle_stage
      ]
    return presets

  def get_preset(self, preset_id: str) -> ExperimentPreset | None:
    return self._presets.get(preset_id)

  def save_preset(self, preset: ExperimentPreset) -> ExperimentPreset:
    self._presets[preset.preset_id] = preset
    return preset


class LocalStrategyCatalog(StrategyCatalogPort):
  def __init__(self, builtins: Iterable[type[Strategy]] | None = None) -> None:
    builtin_factories: dict[str, callable] = {}
    for strategy in (builtins or (MovingAverageCrossStrategy,)):
      metadata = strategy().describe()
      builtin_factories[metadata.strategy_id] = strategy
    for strategy in build_reference_strategies():
      builtin_factories[strategy.describe().strategy_id] = strategy.__class__
    self._builtins = builtin_factories
    self._references = {strategy.describe().strategy_id: strategy for strategy in build_reference_strategies()}
    self._registrations: dict[str, StrategyRegistration] = {}

  def list_strategies(
    self,
    *,
    runtime: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    metadata_by_strategy_id = {
      strategy_id: self._describe_strategy(strategy_id)
      for strategy_id in self._builtins
    }
    for strategy_id in self._registrations:
      metadata_by_strategy_id[strategy_id] = self._describe_strategy(strategy_id)

    metadata = list(metadata_by_strategy_id.values())
    if runtime is not None:
      metadata = [item for item in metadata if item.runtime == runtime]
    if lifecycle_stage is not None:
      metadata = [item for item in metadata if item.lifecycle.stage == lifecycle_stage]
    if version is not None:
      metadata = [
        item
        for item in metadata
        if item.version == version or version in (item.version_lineage or (item.version,))
      ]
    return sorted(metadata, key=lambda item: item.strategy_id)

  def load(self, strategy_id: str) -> Strategy:
    if strategy_id in self._references:
      return self._references[strategy_id]
    if strategy_id in self._builtins:
      return self._builtins[strategy_id]()
    registration = self._registrations[strategy_id]
    module = import_module(registration.module_path)
    strategy_cls = getattr(module, registration.class_name)
    return strategy_cls()

  def register(self, registration: StrategyRegistration) -> StrategyMetadata:
    module = import_module(registration.module_path)
    strategy_cls = getattr(module, registration.class_name)
    strategy = strategy_cls()
    self._registrations[registration.strategy_id] = registration
    return self._apply_registration_metadata(strategy.describe())

  def get_registration(self, strategy_id: str) -> StrategyRegistration | None:
    return self._registrations.get(strategy_id)

  def _describe_strategy(self, strategy_id: str) -> StrategyMetadata:
    if strategy_id in self._references:
      metadata = self._references[strategy_id].describe()
    elif strategy_id in self._builtins:
      metadata = self._builtins[strategy_id]().describe()
    else:
      metadata = self.load(strategy_id).describe()
    return self._apply_registration_metadata(metadata)

  def _apply_registration_metadata(self, metadata: StrategyMetadata) -> StrategyMetadata:
    registration = self._registrations.get(metadata.strategy_id)
    if registration is None or metadata.lifecycle.registered_at is not None:
      return metadata
    base_semantics = metadata.catalog_semantics
    parameter_contract = (
      base_semantics.parameter_contract
      or (
        "Publishes a typed parameter schema for presets and semantic diffs."
        if metadata.parameter_schema
        else "Does not advertise a typed parameter schema; presets can only store freeform parameters."
      )
    )
    operator_notes = tuple(dict.fromkeys((*base_semantics.operator_notes, "Imported from a locally registered module path.")))
    return replace(
      metadata,
      lifecycle=replace(metadata.lifecycle, registered_at=registration.registered_at),
      catalog_semantics=StrategyCatalogSemantics(
        strategy_kind="imported_module",
        execution_model=(
          base_semantics.execution_model
          or "Loaded from a locally registered module and executed through the declared runtime."
        ),
        parameter_contract=parameter_contract,
        source_descriptor=f"{registration.module_path}:{registration.class_name}",
        operator_notes=operator_notes,
      ),
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
