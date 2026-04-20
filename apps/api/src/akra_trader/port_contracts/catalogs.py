from __future__ import annotations

from typing import Protocol

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.port_contracts.strategies import StrategyRuntime


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


class ExperimentPresetCatalogPort(Protocol):
  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]: ...

  def get_preset(self, preset_id: str) -> ExperimentPreset | None: ...

  def save_preset(self, preset: ExperimentPreset) -> ExperimentPreset: ...
