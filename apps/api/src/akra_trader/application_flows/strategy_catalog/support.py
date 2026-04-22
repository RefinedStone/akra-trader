from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from dataclasses import replace
from datetime import datetime
import re
from typing import Any
from typing import Iterable

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import RunExperimentMetadata
from akra_trader.domain.models import StrategyCatalogSemantics
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration


def _normalize_experiment_filter_value(value: str | None) -> str | None:
  if value is None:
    return None
  candidate = value.strip()
  return candidate or None


def _apply_registration_snapshot_metadata(
  *,
  metadata: StrategyMetadata,
  registration: StrategyRegistration | None,
) -> StrategyMetadata:
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
  operator_notes = tuple(
    dict.fromkeys((*base_semantics.operator_notes, "Imported from a locally registered module path."))
  )
  return replace(
    metadata,
    lifecycle=StrategyLifecycle(
      stage=metadata.lifecycle.stage,
      registered_at=registration.registered_at,
    ),
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


def _normalize_experiment_identifier(value: str | None) -> str | None:
  candidate = _normalize_experiment_filter_value(value)
  if candidate is None:
    return None
  normalized = re.sub(r"[^a-z0-9._:-]+", "_", candidate.lower())
  normalized = re.sub(r"_+", "_", normalized).strip("_")
  return normalized or None


def _normalize_experiment_tags(tags: Iterable[str] | None) -> tuple[str, ...]:
  if tags is None:
    return ()
  normalized: list[str] = []
  seen: set[str] = set()
  for tag in tags:
    normalized_tag = _normalize_experiment_identifier(tag)
    if normalized_tag is None or normalized_tag in seen:
      continue
    seen.add(normalized_tag)
    normalized.append(normalized_tag)
  return tuple(normalized)


def _normalize_preset_lifecycle_stage(stage: str | None) -> str | None:
  candidate = _normalize_experiment_filter_value(stage)
  if candidate is None:
    return None
  normalized = candidate.lower().replace(" ", "_")
  if normalized not in {"draft", "benchmark_candidate", "sandbox_candidate", "live_candidate", "archived"}:
    return None
  return normalized


def _normalize_preset_lifecycle_action(action: str | None) -> str | None:
  candidate = _normalize_experiment_filter_value(action)
  if candidate is None:
    return None
  normalized = candidate.lower().replace(" ", "_")
  if normalized not in {"promote", "archive", "restore"}:
    return None
  return normalized


def _resolve_preset_lifecycle_target_stage(*, current_stage: str, action: str) -> str:
  normalized_stage = _normalize_preset_lifecycle_stage(current_stage)
  if normalized_stage is None:
    raise ValueError(f"Unsupported preset lifecycle stage: {current_stage}")
  if action == "archive":
    if normalized_stage == "archived":
      raise ValueError("Preset is already archived.")
    return "archived"
  if action == "restore":
    if normalized_stage != "archived":
      raise ValueError("Only archived presets can be restored.")
    return "draft"
  promotion_order = ("draft", "benchmark_candidate", "sandbox_candidate", "live_candidate")
  if normalized_stage == "archived":
    raise ValueError("Archived presets must be restored before promotion.")
  if normalized_stage == promotion_order[-1]:
    raise ValueError("Preset is already at the live_candidate stage.")
  current_index = promotion_order.index(normalized_stage)
  return promotion_order[current_index + 1]


def _merge_preset_parameters(
  *,
  preset: ExperimentPreset | None,
  requested_parameters: dict[str, Any] | None,
) -> dict[str, Any]:
  merged = deepcopy(preset.parameters) if preset is not None else {}
  for key, value in deepcopy(requested_parameters or {}).items():
    merged[key] = value
  return merged


def _build_run_experiment_metadata(
  *,
  tags: Iterable[str] = (),
  preset: ExperimentPreset | None = None,
  benchmark_family: str | None = None,
  strategy_metadata: StrategyMetadata,
) -> RunExperimentMetadata:
  normalized_benchmark_family = _normalize_experiment_identifier(
    benchmark_family or (preset.benchmark_family if preset is not None else None)
  )
  if normalized_benchmark_family is None and strategy_metadata.runtime == "freqtrade_reference":
    normalized_benchmark_family = _normalize_experiment_identifier(
      f"reference:{strategy_metadata.reference_id or strategy_metadata.strategy_id}"
    )
  merged_tags = tuple(tags)
  if preset is not None:
    merged_tags = (*preset.tags, *merged_tags)
  return RunExperimentMetadata(
    tags=_normalize_experiment_tags(merged_tags),
    preset_id=preset.preset_id if preset is not None else None,
    benchmark_family=normalized_benchmark_family,
  )


def _build_preset_revision(
  *,
  preset_id: str,
  revision_number: int,
  action: str,
  actor: str,
  reason: str,
  occurred_at: datetime,
  name: str,
  description: str,
  strategy_id: str | None,
  timeframe: str | None,
  benchmark_family: str | None,
  tags: tuple[str, ...],
  parameters: dict[str, Any],
  source_revision_id: str | None = None,
) -> ExperimentPreset.Revision:
  normalized_actor = (actor or "operator").strip() or "operator"
  normalized_reason = (reason or action).strip() or action
  return ExperimentPreset.Revision(
    revision_id=f"{preset_id}:r{revision_number:04d}",
    actor=normalized_actor,
    reason=normalized_reason,
    created_at=occurred_at,
    action=action,
    source_revision_id=source_revision_id,
    name=name,
    description=description,
    strategy_id=strategy_id,
    timeframe=timeframe,
    benchmark_family=benchmark_family,
    tags=tuple(tags),
    parameters=deepcopy(parameters),
  )


def _serialize_preset_lifecycle_event(event: ExperimentPreset.LifecycleEvent) -> dict[str, Any]:
  payload = asdict(event)
  payload["occurred_at"] = event.occurred_at.isoformat()
  return payload
