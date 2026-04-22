from __future__ import annotations

from dataclasses import asdict
from typing import Any

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import StrategyMetadata

from .support import _serialize_preset_lifecycle_event


def serialize_preset_revision(revision: ExperimentPreset.Revision) -> dict[str, Any]:
  payload = asdict(revision)
  payload["tags"] = list(revision.tags)
  payload["created_at"] = revision.created_at.isoformat()
  return payload


def serialize_preset(preset: ExperimentPreset) -> dict[str, Any]:
  payload = asdict(preset)
  payload["tags"] = list(preset.tags)
  payload["lifecycle"]["history"] = [
    _serialize_preset_lifecycle_event(event)
    for event in preset.lifecycle.history
  ]
  payload["revisions"] = [
    serialize_preset_revision(revision)
    for revision in preset.revisions
  ]
  payload["created_at"] = preset.created_at.isoformat()
  payload["updated_at"] = preset.updated_at.isoformat()
  return payload


def serialize_strategy(strategy: StrategyMetadata) -> dict[str, Any]:
  payload = asdict(strategy)
  payload["asset_types"] = [asset_type.value for asset_type in strategy.asset_types]
  payload["supported_timeframes"] = list(strategy.supported_timeframes)
  payload["version_lineage"] = list(strategy.version_lineage or (strategy.version,))
  payload["catalog_semantics"]["operator_notes"] = list(strategy.catalog_semantics.operator_notes)
  return payload
