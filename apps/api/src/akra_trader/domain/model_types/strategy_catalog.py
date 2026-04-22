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
  "ExperimentPreset",
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
  reference_id: str | None = None
  reference_path: str | None = None
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
  reference_id: str | None = None
  reference_path: str | None = None
  entrypoint: str | None = None


@dataclass(frozen=True)
class ExperimentPreset:
  @dataclass(frozen=True)
  class Revision:
    revision_id: str
    actor: str
    reason: str
    created_at: datetime
    action: str = "updated"
    source_revision_id: str | None = None
    name: str = ""
    description: str = ""
    strategy_id: str | None = None
    timeframe: str | None = None
    benchmark_family: str | None = None
    tags: tuple[str, ...] = ()
    parameters: dict[str, Any] = field(default_factory=dict)

  @dataclass(frozen=True)
  class LifecycleEvent:
    action: str
    actor: str
    reason: str
    occurred_at: datetime
    from_stage: str | None = None
    to_stage: str = "draft"

  @dataclass(frozen=True)
  class Lifecycle:
    stage: str = "draft"
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_by: str = "operator"
    last_action: str = "created"
    history: tuple["ExperimentPreset.LifecycleEvent", ...] = ()

  preset_id: str
  name: str
  description: str = ""
  strategy_id: str | None = None
  timeframe: str | None = None
  benchmark_family: str | None = None
  tags: tuple[str, ...] = ()
  parameters: dict[str, Any] = field(default_factory=dict)
  lifecycle: "ExperimentPreset.Lifecycle" = field(
    default_factory=lambda: ExperimentPreset.Lifecycle()
  )
  revisions: tuple["ExperimentPreset.Revision", ...] = ()
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class RunExperimentMetadata:
  tags: tuple[str, ...] = ()
  preset_id: str | None = None
  benchmark_family: str | None = None


@dataclass(frozen=True)
class StrategyRegistration:
  strategy_id: str
  module_path: str
  class_name: str
  registered_at: datetime


from akra_trader.domain.model_types.run_execution import AssetType as AssetType
from akra_trader.domain.model_types.run_execution import WarmupSpec as WarmupSpec
