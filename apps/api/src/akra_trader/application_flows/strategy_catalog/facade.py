from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Iterable

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import StrategyMetadata
from akra_trader.ports import ExperimentPresetCatalogPort
from akra_trader.ports import ReferenceCatalogPort
from akra_trader.ports import StrategyCatalogPort

from . import commands
from . import queries


@dataclass(slots=True)
class StrategyCatalogFlow:
  strategies: StrategyCatalogPort
  references: ReferenceCatalogPort
  presets: ExperimentPresetCatalogPort
  clock: Callable[[], datetime]

  def list_strategies(
    self,
    *,
    lane: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    return queries.list_strategies(
      self,
      lane=lane,
      lifecycle_stage=lifecycle_stage,
      version=version,
    )

  def list_references(self):
    return queries.list_references(self)

  def register_strategy(self, *, strategy_id: str, module_path: str, class_name: str) -> StrategyMetadata:
    return commands.register_strategy(
      self,
      strategy_id=strategy_id,
      module_path=module_path,
      class_name=class_name,
    )

  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    return queries.list_presets(
      self,
      strategy_id=strategy_id,
      timeframe=timeframe,
      lifecycle_stage=lifecycle_stage,
    )

  def get_preset(self, *, preset_id: str) -> ExperimentPreset:
    return queries.get_preset(self, preset_id=preset_id)

  def get_preset_or_raise(self, preset_id: str) -> ExperimentPreset:
    return queries.get_preset_or_raise(self, preset_id)

  def create_preset(
    self,
    *,
    name: str,
    preset_id: str | None = None,
    description: str = "",
    strategy_id: str | None = None,
    timeframe: str | None = None,
    tags: Iterable[str] = (),
    parameters: dict[str, Any] | None = None,
    benchmark_family: str | None = None,
  ) -> ExperimentPreset:
    return commands.create_preset(
      self,
      name=name,
      preset_id=preset_id,
      description=description,
      strategy_id=strategy_id,
      timeframe=timeframe,
      tags=tags,
      parameters=parameters,
      benchmark_family=benchmark_family,
    )

  def update_preset(
    self,
    *,
    preset_id: str,
    changes: dict[str, Any],
    actor: str = "operator",
    reason: str = "manual_preset_edit",
  ) -> ExperimentPreset:
    return commands.update_preset(
      self,
      preset_id=preset_id,
      changes=changes,
      actor=actor,
      reason=reason,
    )

  def list_preset_revisions(
    self,
    *,
    preset_id: str,
  ) -> tuple[ExperimentPreset.Revision, ...]:
    return queries.list_preset_revisions(
      self,
      preset_id=preset_id,
    )

  def restore_preset_revision(
    self,
    *,
    preset_id: str,
    revision_id: str,
    actor: str = "operator",
    reason: str = "manual_preset_revision_restore",
  ) -> ExperimentPreset:
    return commands.restore_preset_revision(
      self,
      preset_id=preset_id,
      revision_id=revision_id,
      actor=actor,
      reason=reason,
    )

  def apply_preset_lifecycle_action(
    self,
    *,
    preset_id: str,
    action: str,
    actor: str = "operator",
    reason: str = "manual_preset_lifecycle_action",
  ) -> ExperimentPreset:
    return commands.apply_preset_lifecycle_action(
      self,
      preset_id=preset_id,
      action=action,
      actor=actor,
      reason=reason,
    )

  def validate_preset_strategy(self, *, strategy_id: str | None) -> None:
    commands.validate_preset_strategy(self, strategy_id=strategy_id)

  def resolve_experiment_preset(
    self,
    *,
    preset_id: str | None,
    strategy_id: str,
    timeframe: str,
  ) -> ExperimentPreset | None:
    return commands.resolve_experiment_preset(
      self,
      preset_id=preset_id,
      strategy_id=strategy_id,
      timeframe=timeframe,
    )

  def migrate_legacy_preset_from_run(self, run: RunRecord) -> ExperimentPreset | None:
    return commands.migrate_legacy_preset_from_run(self, run)
