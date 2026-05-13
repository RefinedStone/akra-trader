from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from importlib import import_module

from akra_trader.domain.models import StrategyCatalogSemantics
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.ports import StrategyCatalogPort
from akra_trader.strategies.base import Strategy
from akra_trader.strategies.examples import MovingAverageCrossStrategy
from akra_trader.strategies.quant_examples import RsiAtrOversoldPeakTurnStrategy


class LocalStrategyCatalog(StrategyCatalogPort):
  def __init__(self, builtins: Iterable[type[Strategy]] | None = None) -> None:
    self._builtins: dict[str, type[Strategy]] = {}
    for strategy_type in builtins or (MovingAverageCrossStrategy, RsiAtrOversoldPeakTurnStrategy):
      metadata = strategy_type().describe()
      self._builtins[metadata.strategy_id] = strategy_type
    self._registrations: dict[str, StrategyRegistration] = {}

  def list_strategies(
    self,
    *,
    runtime: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    metadata = [self._describe_strategy(strategy_id) for strategy_id in self._builtins]
    metadata.extend(self._describe_strategy(strategy_id) for strategy_id in self._registrations)
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
    if strategy_id in self._builtins:
      return self._builtins[strategy_id]()
    registration = self._registrations.get(strategy_id)
    if registration is None:
      raise KeyError(f"Unknown strategy: {strategy_id}")
    module = import_module(registration.module_path)
    strategy_type = getattr(module, registration.class_name)
    return strategy_type()

  def register(self, registration: StrategyRegistration) -> StrategyMetadata:
    if registration.registered_at is None:
      registration = replace(registration, registered_at=datetime.now(UTC))
    module = import_module(registration.module_path)
    strategy_type = getattr(module, registration.class_name)
    strategy = strategy_type()
    metadata = strategy.describe()
    self._registrations[registration.strategy_id] = registration
    return self._apply_registration_metadata(metadata)

  def get_registration(self, strategy_id: str) -> StrategyRegistration | None:
    return self._registrations.get(strategy_id)

  def _describe_strategy(self, strategy_id: str) -> StrategyMetadata:
    metadata = self.load(strategy_id).describe()
    return self._apply_registration_metadata(metadata)

  def _apply_registration_metadata(self, metadata: StrategyMetadata) -> StrategyMetadata:
    registration = self._registrations.get(metadata.strategy_id)
    if registration is None or metadata.lifecycle.registered_at is not None:
      return metadata
    semantics = metadata.catalog_semantics
    return replace(
      metadata,
      lifecycle=replace(metadata.lifecycle, registered_at=registration.registered_at),
      catalog_semantics=StrategyCatalogSemantics(
        strategy_kind="imported_module",
        execution_model=(
          semantics.execution_model
          or "Loaded from a locally registered module and executed through the declared runtime."
        ),
        parameter_contract=(
          semantics.parameter_contract
          or "Publishes a typed parameter schema for runtime launch forms."
        ),
        source_descriptor=f"{registration.module_path}:{registration.class_name}",
        operator_notes=tuple(
          dict.fromkeys((*semantics.operator_notes, "Imported from a local module path."))
        ),
      ),
    )
