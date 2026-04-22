from __future__ import annotations

from typing import Any

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import StrategyMetadata

from .support import _normalize_experiment_filter_value
from .support import _normalize_experiment_identifier
from .support import _normalize_preset_lifecycle_stage


def list_strategies(
  flow: Any,
  *,
  lane: str | None = None,
  lifecycle_stage: str | None = None,
  version: str | None = None,
) -> list[StrategyMetadata]:
  return flow.strategies.list_strategies(
    runtime=lane,
    lifecycle_stage=lifecycle_stage,
    version=version,
  )


def list_references(flow: Any) -> list[ReferenceSource]:
  return flow.references.list_entries()


def list_presets(
  flow: Any,
  *,
  strategy_id: str | None = None,
  timeframe: str | None = None,
  lifecycle_stage: str | None = None,
) -> list[ExperimentPreset]:
  return flow.presets.list_presets(
    strategy_id=_normalize_experiment_filter_value(strategy_id),
    timeframe=_normalize_experiment_filter_value(timeframe),
    lifecycle_stage=_normalize_preset_lifecycle_stage(lifecycle_stage),
  )


def get_preset_or_raise(flow: Any, preset_id: str) -> ExperimentPreset:
  normalized_preset_id = _normalize_experiment_identifier(preset_id)
  if normalized_preset_id is None:
    raise ValueError("Preset ID is required.")
  preset = flow.presets.get_preset(normalized_preset_id)
  if preset is None:
    raise LookupError(f"Preset not found: {normalized_preset_id}")
  return preset


def get_preset(flow: Any, *, preset_id: str) -> ExperimentPreset:
  return get_preset_or_raise(flow, preset_id)


def list_preset_revisions(
  flow: Any,
  *,
  preset_id: str,
) -> tuple[ExperimentPreset.Revision, ...]:
  preset = get_preset_or_raise(flow, preset_id)
  return tuple(reversed(preset.revisions))
