from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from typing import Any
from typing import Iterable

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration

from .queries import get_preset_or_raise
from .support import _build_preset_revision
from .support import _normalize_experiment_filter_value
from .support import _normalize_experiment_identifier
from .support import _normalize_experiment_tags
from .support import _normalize_preset_lifecycle_action
from .support import _normalize_preset_lifecycle_stage
from .support import _resolve_preset_lifecycle_target_stage


def register_strategy(
  flow: Any,
  *,
  strategy_id: str,
  module_path: str,
  class_name: str,
) -> StrategyMetadata:
  registration = StrategyRegistration(
    strategy_id=strategy_id,
    module_path=module_path,
    class_name=class_name,
    registered_at=flow.clock(),
  )
  return flow.strategies.register(registration)


def validate_preset_strategy(flow: Any, *, strategy_id: str | None) -> None:
  if strategy_id is None:
    return
  available_strategy_ids = {
    strategy.strategy_id
    for strategy in flow.strategies.list_strategies()
  }
  if strategy_id not in available_strategy_ids:
    raise ValueError(f"Strategy not found for preset: {strategy_id}")


def create_preset(
  flow: Any,
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
  normalized_name = name.strip()
  if not normalized_name:
    raise ValueError("Preset name is required.")
  normalized_preset_id = _normalize_experiment_identifier(preset_id or name)
  if normalized_preset_id is None:
    raise ValueError("Preset ID is required.")
  if flow.presets.get_preset(normalized_preset_id) is not None:
    raise ValueError(f"Preset already exists: {normalized_preset_id}")
  normalized_strategy_id = _normalize_experiment_filter_value(strategy_id)
  validate_preset_strategy(flow, strategy_id=normalized_strategy_id)
  normalized_timeframe = _normalize_experiment_filter_value(timeframe)
  normalized_parameters = deepcopy(parameters or {})
  if normalized_parameters and normalized_strategy_id is None:
    raise ValueError("Preset parameters require a strategy_id.")
  current_time = flow.clock()
  normalized_benchmark_family = _normalize_experiment_identifier(benchmark_family)
  normalized_tags = _normalize_experiment_tags(tags)
  normalized_description = description.strip()
  preset = ExperimentPreset(
    preset_id=normalized_preset_id,
    name=normalized_name,
    description=normalized_description,
    strategy_id=normalized_strategy_id,
    timeframe=normalized_timeframe,
    benchmark_family=normalized_benchmark_family,
    tags=normalized_tags,
    parameters=normalized_parameters,
    lifecycle=ExperimentPreset.Lifecycle(
      stage="draft",
      updated_at=current_time,
      updated_by="operator",
      last_action="created",
      history=(
        ExperimentPreset.LifecycleEvent(
          action="created",
          actor="operator",
          reason="preset_created",
          occurred_at=current_time,
          from_stage=None,
          to_stage="draft",
        ),
      ),
    ),
    revisions=(
      _build_preset_revision(
        preset_id=normalized_preset_id,
        revision_number=1,
        action="created",
        actor="operator",
        reason="preset_created",
        occurred_at=current_time,
        name=normalized_name,
        description=normalized_description,
        strategy_id=normalized_strategy_id,
        timeframe=normalized_timeframe,
        benchmark_family=normalized_benchmark_family,
        tags=normalized_tags,
        parameters=normalized_parameters,
      ),
    ),
    created_at=current_time,
    updated_at=current_time,
  )
  return flow.presets.save_preset(preset)


def update_preset(
  flow: Any,
  *,
  preset_id: str,
  changes: dict[str, Any],
  actor: str = "operator",
  reason: str = "manual_preset_edit",
) -> ExperimentPreset:
  preset = get_preset_or_raise(flow, preset_id)
  allowed_fields = {
    "name",
    "description",
    "strategy_id",
    "timeframe",
    "benchmark_family",
    "tags",
    "parameters",
  }
  unexpected_fields = sorted(set(changes) - allowed_fields)
  if unexpected_fields:
    raise ValueError(f"Unsupported preset update fields: {', '.join(unexpected_fields)}")
  if not changes:
    raise ValueError("Preset update requires at least one field.")

  next_name = preset.name
  if "name" in changes:
    candidate_name = str(changes["name"] or "").strip()
    if not candidate_name:
      raise ValueError("Preset name is required.")
    next_name = candidate_name

  next_description = preset.description
  if "description" in changes:
    next_description = str(changes["description"] or "").strip()

  next_strategy_id = preset.strategy_id
  if "strategy_id" in changes:
    next_strategy_id = _normalize_experiment_filter_value(changes["strategy_id"])

  next_timeframe = preset.timeframe
  if "timeframe" in changes:
    next_timeframe = _normalize_experiment_filter_value(changes["timeframe"])

  next_benchmark_family = preset.benchmark_family
  if "benchmark_family" in changes:
    next_benchmark_family = _normalize_experiment_identifier(changes["benchmark_family"])

  next_tags = preset.tags
  if "tags" in changes:
    next_tags = _normalize_experiment_tags(changes["tags"])

  next_parameters = deepcopy(preset.parameters)
  if "parameters" in changes:
    candidate_parameters = changes["parameters"]
    if candidate_parameters is None:
      next_parameters = {}
    elif isinstance(candidate_parameters, dict):
      next_parameters = deepcopy(candidate_parameters)
    else:
      raise ValueError("Preset parameters must be a JSON object.")

  validate_preset_strategy(flow, strategy_id=next_strategy_id)
  if next_parameters and next_strategy_id is None:
    raise ValueError("Preset parameters require a strategy_id.")

  if (
    next_name == preset.name
    and next_description == preset.description
    and next_strategy_id == preset.strategy_id
    and next_timeframe == preset.timeframe
    and next_benchmark_family == preset.benchmark_family
    and next_tags == preset.tags
    and next_parameters == preset.parameters
  ):
    return preset

  current_time = flow.clock()
  normalized_actor = (actor or "operator").strip() or "operator"
  normalized_reason = (reason or "manual_preset_edit").strip() or "manual_preset_edit"
  updated = replace(
    preset,
    name=next_name,
    description=next_description,
    strategy_id=next_strategy_id,
    timeframe=next_timeframe,
    benchmark_family=next_benchmark_family,
    tags=next_tags,
    parameters=next_parameters,
    updated_at=current_time,
    revisions=(
      *preset.revisions,
      _build_preset_revision(
        preset_id=preset.preset_id,
        revision_number=len(preset.revisions) + 1,
        action="updated",
        actor=normalized_actor,
        reason=normalized_reason,
        occurred_at=current_time,
        name=next_name,
        description=next_description,
        strategy_id=next_strategy_id,
        timeframe=next_timeframe,
        benchmark_family=next_benchmark_family,
        tags=next_tags,
        parameters=next_parameters,
      ),
    ),
  )
  return flow.presets.save_preset(updated)


def restore_preset_revision(
  flow: Any,
  *,
  preset_id: str,
  revision_id: str,
  actor: str = "operator",
  reason: str = "manual_preset_revision_restore",
) -> ExperimentPreset:
  preset = get_preset_or_raise(flow, preset_id)
  target_revision = next(
    (revision for revision in preset.revisions if revision.revision_id == revision_id),
    None,
  )
  if target_revision is None:
    raise LookupError(f"Preset revision not found: {revision_id}")

  current_time = flow.clock()
  normalized_actor = (actor or "operator").strip() or "operator"
  normalized_reason = (reason or "manual_preset_revision_restore").strip() or "manual_preset_revision_restore"
  restored = replace(
    preset,
    name=target_revision.name,
    description=target_revision.description,
    strategy_id=target_revision.strategy_id,
    timeframe=target_revision.timeframe,
    benchmark_family=target_revision.benchmark_family,
    tags=target_revision.tags,
    parameters=deepcopy(target_revision.parameters),
    updated_at=current_time,
    revisions=(
      *preset.revisions,
      _build_preset_revision(
        preset_id=preset.preset_id,
        revision_number=len(preset.revisions) + 1,
        action="restored",
        actor=normalized_actor,
        reason=normalized_reason,
        occurred_at=current_time,
        source_revision_id=target_revision.revision_id,
        name=target_revision.name,
        description=target_revision.description,
        strategy_id=target_revision.strategy_id,
        timeframe=target_revision.timeframe,
        benchmark_family=target_revision.benchmark_family,
        tags=target_revision.tags,
        parameters=target_revision.parameters,
      ),
    ),
  )
  validate_preset_strategy(flow, strategy_id=restored.strategy_id)
  if restored.parameters and restored.strategy_id is None:
    raise ValueError("Preset parameters require a strategy_id.")
  return flow.presets.save_preset(restored)


def apply_preset_lifecycle_action(
  flow: Any,
  *,
  preset_id: str,
  action: str,
  actor: str = "operator",
  reason: str = "manual_preset_lifecycle_action",
  lineage_evidence_pack_id: str | None = None,
  lineage_evidence_retention_expires_at: datetime | None = None,
  lineage_evidence_summary: str | None = None,
) -> ExperimentPreset:
  normalized_preset_id = _normalize_experiment_identifier(preset_id)
  if normalized_preset_id is None:
    raise ValueError("Preset ID is required.")
  preset = flow.presets.get_preset(normalized_preset_id)
  if preset is None:
    raise LookupError(f"Preset not found: {normalized_preset_id}")
  normalized_action = _normalize_preset_lifecycle_action(action)
  if normalized_action is None:
    raise ValueError(f"Unsupported preset lifecycle action: {action}")
  current_stage = preset.lifecycle.stage
  target_stage = _resolve_preset_lifecycle_target_stage(
    current_stage=current_stage,
    action=normalized_action,
  )
  current_time = flow.clock()
  updated = replace(
    preset,
    lifecycle=replace(
      preset.lifecycle,
      stage=target_stage,
      updated_at=current_time,
      updated_by=(actor or "operator").strip() or "operator",
      last_action=normalized_action,
      history=(
        *preset.lifecycle.history,
        ExperimentPreset.LifecycleEvent(
          action=normalized_action,
          actor=(actor or "operator").strip() or "operator",
          reason=(reason or normalized_action).strip() or normalized_action,
          occurred_at=current_time,
          from_stage=current_stage,
          to_stage=target_stage,
          lineage_evidence_pack_id=(
            lineage_evidence_pack_id.strip()
            if isinstance(lineage_evidence_pack_id, str) and lineage_evidence_pack_id.strip()
            else None
          ),
          lineage_evidence_retention_expires_at=lineage_evidence_retention_expires_at,
          lineage_evidence_summary=(
            lineage_evidence_summary.strip()
            if isinstance(lineage_evidence_summary, str) and lineage_evidence_summary.strip()
            else None
          ),
        ),
      ),
    ),
    updated_at=current_time,
  )
  return flow.presets.save_preset(updated)


def resolve_experiment_preset(
  flow: Any,
  *,
  preset_id: str | None,
  strategy_id: str,
  timeframe: str,
) -> ExperimentPreset | None:
  normalized_preset_id = _normalize_experiment_identifier(preset_id)
  if normalized_preset_id is None:
    return None
  preset = flow.presets.get_preset(normalized_preset_id)
  if preset is None:
    raise ValueError(f"Preset not found: {normalized_preset_id}")
  if preset.lifecycle.stage == "archived":
    raise ValueError(f"Preset {normalized_preset_id} is archived and cannot be launched.")
  if preset.strategy_id is not None and preset.strategy_id != strategy_id:
    raise ValueError(
      f"Preset {normalized_preset_id} is pinned to strategy {preset.strategy_id}, not {strategy_id}."
    )
  if preset.timeframe is not None and preset.timeframe != timeframe:
    raise ValueError(
      f"Preset {normalized_preset_id} is pinned to timeframe {preset.timeframe}, not {timeframe}."
    )
  return preset


def migrate_legacy_preset_from_run(flow: Any, run: RunRecord) -> ExperimentPreset | None:
  preset_id = _normalize_experiment_identifier(run.provenance.experiment.preset_id)
  if preset_id is None:
    return None
  existing = flow.presets.get_preset(preset_id)
  if existing is not None:
    return existing
  normalized_benchmark_family = _normalize_experiment_identifier(
    run.provenance.experiment.benchmark_family
  )
  normalized_tags = _normalize_experiment_tags(run.provenance.experiment.tags)
  preset = ExperimentPreset(
    preset_id=preset_id,
    name=preset_id,
    description="Migrated from legacy run metadata.",
    strategy_id=run.config.strategy_id,
    timeframe=run.config.timeframe,
    benchmark_family=normalized_benchmark_family,
    tags=normalized_tags,
    parameters=deepcopy(run.config.parameters),
    lifecycle=ExperimentPreset.Lifecycle(
      stage="draft",
      updated_at=run.started_at,
      updated_by="system",
      last_action="migrated",
      history=(
        ExperimentPreset.LifecycleEvent(
          action="migrated",
          actor="system",
          reason="legacy_run_metadata_migration",
          occurred_at=run.started_at,
          from_stage=None,
          to_stage="draft",
        ),
      ),
    ),
    revisions=(
      _build_preset_revision(
        preset_id=preset_id,
        revision_number=1,
        action="migrated",
        actor="system",
        reason="legacy_run_metadata_migration",
        occurred_at=run.started_at,
        name=preset_id,
        description="Migrated from legacy run metadata.",
        strategy_id=run.config.strategy_id,
        timeframe=run.config.timeframe,
        benchmark_family=normalized_benchmark_family,
        tags=normalized_tags,
        parameters=run.config.parameters,
      ),
    ),
    created_at=run.started_at,
    updated_at=run.started_at,
  )
  return flow.presets.save_preset(preset)
