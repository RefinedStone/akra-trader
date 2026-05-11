from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from akra_trader.domain.model_types.run_execution import AssetType
  from akra_trader.domain.model_types.run_execution import WarmupSpec
else:
  AssetType = Any
  WarmupSpec = Any


__all__ = [
  "StrategyLifecycle",
  "StrategyCatalogSemantics",
  "StrategyMetadata",
  "StrategyParameterSnapshot",
  "StrategySnapshot",
  "RunExperimentMetadata",
  "StrategyRegistration",
]


def _default_warmup_spec() -> WarmupSpec:
  from akra_trader.domain.model_types.run_execution import WarmupSpec

  return WarmupSpec(required_bars=0)


@dataclass(frozen=True)
class StrategyLifecycle:
  stage: str = "active"
  registered_at: datetime | None = None


@dataclass(frozen=True)
class StrategyCatalogSemantics:
  strategy_kind: str = "standard"
  execution_model: str = ""
  parameter_contract: str = ""
  source_descriptor: str | None = None
  operator_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategyMetadata:
  strategy_id: str
  name: str
  version: str
  runtime: str
  asset_types: tuple[AssetType, ...]
  supported_timeframes: tuple[str, ...]
  parameter_schema: dict[str, Any]
  description: str
  lifecycle: StrategyLifecycle = field(default_factory=StrategyLifecycle)
  catalog_semantics: StrategyCatalogSemantics = field(default_factory=StrategyCatalogSemantics)
  version_lineage: tuple[str, ...] = ()
  entrypoint: str | None = None


@dataclass(frozen=True)
class StrategyParameterSnapshot:
  requested: dict[str, Any] = field(default_factory=dict)
  resolved: dict[str, Any] = field(default_factory=dict)
  schema: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategySnapshot:
  strategy_id: str
  name: str
  version: str
  runtime: str
  lifecycle: StrategyLifecycle = field(default_factory=StrategyLifecycle)
  catalog_semantics: StrategyCatalogSemantics = field(default_factory=StrategyCatalogSemantics)
  version_lineage: tuple[str, ...] = ()
  parameter_snapshot: StrategyParameterSnapshot = field(default_factory=StrategyParameterSnapshot)
  supported_timeframes: tuple[str, ...] = ()
  warmup: WarmupSpec = field(default_factory=_default_warmup_spec)
  entrypoint: str | None = None


@dataclass(frozen=True)
class RunExperimentMetadata:
  tags: tuple[str, ...] = ()
  benchmark_family: str | None = None


@dataclass(frozen=True)
class StrategyRegistration:
  strategy_id: str
  module_path: str
  class_name: str
  registered_at: datetime


from akra_trader.domain.model_types.run_execution import AssetType as AssetType
from akra_trader.domain.model_types.run_execution import WarmupSpec as WarmupSpec
