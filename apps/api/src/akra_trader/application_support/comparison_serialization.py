from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, replace
from numbers import Number
from typing import Any

from akra_trader.application_support.comparison import COMPARISON_INTENT_COPY
from akra_trader.application_support.comparison import COMPARISON_INTENT_DEFAULT
from akra_trader.application_support.comparison import COMPARISON_INTENT_WEIGHTS
from akra_trader.application_support.comparison import COMPARISON_METRIC_COPY
from akra_trader.application_support.run_surfaces import _build_run_surface_enforcement
from akra_trader.application_support.standalone_surfaces import serialize_run_surface_shared_contracts
from akra_trader.domain.models import ComparisonEligibilityContract
from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonMetricRow
from akra_trader.domain.models import RunComparisonNarrative
from akra_trader.domain.models import RunComparisonRun
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import StrategyCatalogSemantics
from akra_trader.domain.models import default_comparison_eligibility_contract

def serialize_run_comparison(
  comparison: RunComparison,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  payload = asdict(comparison)
  payload["requested_run_ids"] = list(comparison.requested_run_ids)
  payload["runs"] = [
    {
      **run_payload,
      "experiment": {
        **run_payload["experiment"],
        "tags": list(run.experiment.tags),
      },
      "symbols": list(run.symbols),
      "external_command": list(run.external_command),
      "artifact_paths": list(run.artifact_paths),
      "benchmark_artifacts": [asdict(artifact) for artifact in run.benchmark_artifacts],
      "catalog_semantics": {
        **run_payload["catalog_semantics"],
        "operator_notes": list(run.catalog_semantics.operator_notes),
      },
      "notes": list(run.notes),
    }
    for run_payload, run in zip(payload["runs"], comparison.runs, strict=True)
  ]
  payload["surface_enforcement"] = _build_run_surface_enforcement(resolved_capabilities)
  return payload


def serialize_run_surface_capabilities(capabilities: RunSurfaceCapabilities) -> dict[str, Any]:
  return {
    "discovery": {
      "shared_contracts": serialize_run_surface_shared_contracts(capabilities),
    },
    "comparison_eligibility_contract": serialize_comparison_eligibility_contract(
      capabilities.comparison_eligibility_contract
    )
  }


def serialize_comparison_eligibility_contract(
  contract: ComparisonEligibilityContract | None = None,
) -> dict[str, Any]:
  resolved_contract = contract or default_comparison_eligibility_contract()
  payload = asdict(resolved_contract)
  payload["groups"] = {
    key: {
      **group_payload,
      "surface_ids": list(resolved_contract.groups[key].surface_ids),
    }
    for key, group_payload in payload["groups"].items()
  }
  return payload


def _normalize_run_ids(run_ids: list[str]) -> list[str]:
  normalized_run_ids: list[str] = []
  seen_run_ids: set[str] = set()
  for run_id in run_ids:
    if run_id in seen_run_ids:
      continue
    seen_run_ids.add(run_id)
    normalized_run_ids.append(run_id)
  return normalized_run_ids


def _serialize_comparison_run(run: RunRecord) -> RunComparisonRun:
  return RunComparisonRun(
    run_id=run.config.run_id,
    mode=run.config.mode.value,
    status=run.status.value,
    lane=run.provenance.lane,
    strategy_id=run.config.strategy_id,
    strategy_name=run.provenance.strategy.name if run.provenance.strategy is not None else None,
    strategy_version=run.config.strategy_version,
    catalog_semantics=deepcopy(
      run.provenance.strategy.catalog_semantics
      if run.provenance.strategy is not None
      else StrategyCatalogSemantics()
    ),
    symbols=run.config.symbols,
    timeframe=run.config.timeframe,
    started_at=run.started_at,
    ended_at=run.ended_at,
    reference_id=run.provenance.reference_id,
    reference_version=run.provenance.reference_version,
    integration_mode=run.provenance.integration_mode,
    reference=deepcopy(run.provenance.reference),
    working_directory=run.provenance.working_directory,
    rerun_boundary_id=run.provenance.rerun_boundary_id,
    rerun_boundary_state=run.provenance.rerun_boundary_state,
    dataset_identity=(
      run.provenance.market_data.dataset_identity
      if run.provenance.market_data is not None
      else None
    ),
    experiment=deepcopy(run.provenance.experiment),
    external_command=tuple(run.provenance.external_command),
    artifact_paths=tuple(run.provenance.artifact_paths),
    benchmark_artifacts=tuple(run.provenance.benchmark_artifacts),
    metrics=deepcopy(run.metrics),
    notes=tuple(run.notes),
  )


def _build_comparison_metric_row(
  *,
  runs: list[RunRecord],
  baseline_run: RunRecord,
  intent: str,
  key: str,
  label: str,
  unit: str,
  higher_is_better: bool,
) -> RunComparisonMetricRow:
  baseline_value = _resolve_run_metric_value(baseline_run, key)
  values = {
    run.config.run_id: _resolve_run_metric_value(run, key)
    for run in runs
  }
  deltas_vs_baseline = {
    run_id: _calculate_metric_delta(value, baseline_value)
    for run_id, value in values.items()
  }
  delta_annotations = {
    run_id: _build_metric_delta_annotation(
      intent=intent,
      key=key,
      unit=unit,
      is_baseline=run_id == baseline_run.config.run_id,
      baseline_run=baseline_run,
      run=run,
      higher_is_better=higher_is_better,
      delta=deltas_vs_baseline[run_id],
      value=values[run_id],
    )
    for run_id, run in ((candidate.config.run_id, candidate) for candidate in runs)
  }
  comparable_values = {
    run_id: value
    for run_id, value in values.items()
    if value is not None
  }
  best_run_id: str | None = None
  if comparable_values:
    best_run_id = (
      max(comparable_values, key=comparable_values.get)
      if higher_is_better
      else min(comparable_values, key=comparable_values.get)
    )
  return RunComparisonMetricRow(
    key=key,
    label=label,
    unit=unit,
    higher_is_better=higher_is_better,
    values=values,
    deltas_vs_baseline=deltas_vs_baseline,
    delta_annotations=delta_annotations,
    annotation=_build_metric_annotation(
      intent=intent,
      key=key,
      baseline_run=baseline_run,
      runs=runs,
    ),
    best_run_id=best_run_id,
  )


def _build_metric_annotation(
  *,
  intent: str,
  key: str,
  baseline_run: RunRecord,
  runs: list[RunRecord],
) -> str | None:
  annotation = COMPARISON_METRIC_COPY.get(intent, {}).get(key, {}).get("annotation")
  semantic_suffix = _build_metric_semantic_annotation_suffix(
    baseline_run=baseline_run,
    runs=runs,
  )
  if annotation is None:
    return f"Semantic context: {semantic_suffix}." if semantic_suffix else None
  if semantic_suffix is None:
    return annotation
  return f"{annotation} Semantic context: {semantic_suffix}."


def _build_metric_delta_annotation(
  *,
  intent: str,
  key: str,
  unit: str,
  is_baseline: bool,
  baseline_run: RunRecord,
  run: RunRecord,
  higher_is_better: bool,
  delta: float | int | None,
  value: float | int | None,
) -> str:
  copy = COMPARISON_METRIC_COPY.get(intent, {}).get(key, {})
  semantic_suffix = _build_metric_delta_semantic_suffix(
    baseline_run=baseline_run,
    run=run,
  )
  if is_baseline:
    return copy.get("baseline", "baseline")
  if value is None or delta is None:
    missing = copy.get("missing", "delta unavailable")
    return f"{missing} for {semantic_suffix}" if semantic_suffix else missing
  if delta == 0:
    return f"aligned with baseline for {semantic_suffix}" if semantic_suffix else "aligned with baseline"

  magnitude = _format_metric_delta_magnitude(delta=delta, unit=unit)
  positive_phrase = copy.get("positive_delta", "above baseline")
  negative_phrase = copy.get("negative_delta", "below baseline")

  if higher_is_better:
    phrase = positive_phrase if delta > 0 else negative_phrase
  else:
    phrase = positive_phrase if delta > 0 else negative_phrase
  annotation = f"{magnitude} {phrase}"
  return f"{annotation} for {semantic_suffix}" if semantic_suffix else annotation


def _format_metric_delta_magnitude(
  *,
  delta: float | int,
  unit: str,
) -> str:
  magnitude = abs(float(delta))
  if unit == "pct":
    rounded = round(magnitude, 2)
    return f"{rounded:g} pts"
  rounded = round(magnitude, 2)
  if rounded.is_integer():
    return str(int(rounded))
  return f"{rounded:g}"


def _build_comparison_narrative(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  intent: str,
  metric_row_by_key: dict[str, RunComparisonMetricRow],
) -> RunComparisonNarrative | None:
  comparison_type = _classify_comparison_type(baseline_run, run)
  target_label = _comparison_run_label(run)
  baseline_label = _comparison_run_label(baseline_run)
  target_subject = _comparison_subject_label(run)

  total_return_delta = _metric_row_delta(metric_row_by_key, "total_return_pct", run.config.run_id)
  max_drawdown_delta = _metric_row_delta(metric_row_by_key, "max_drawdown_pct", run.config.run_id)
  win_rate_delta = _metric_row_delta(metric_row_by_key, "win_rate_pct", run.config.run_id)
  trade_count_delta = _metric_row_delta(metric_row_by_key, "trade_count", run.config.run_id)

  title = _build_comparison_narrative_title(
    intent=intent,
    comparison_type=comparison_type,
    target_subject=target_subject,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
  )
  summary = _build_comparison_narrative_summary(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )
  bullets = _build_comparison_narrative_bullets(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    target_label=target_label,
    baseline_label=baseline_label,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  if not title and not summary and not bullets:
    return None

  insight_score, score_breakdown = _score_comparison_narrative(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  return RunComparisonNarrative(
    run_id=run.config.run_id,
    baseline_run_id=baseline_run.config.run_id,
    comparison_type=comparison_type,
    title=title or f"{target_subject} diverged from {baseline_label}.",
    summary=summary or f"{target_label} is being compared against {baseline_label}.",
    bullets=tuple(bullets),
    score_breakdown=score_breakdown,
    insight_score=insight_score,
  )


def _rank_comparison_narratives(
  narratives: list[RunComparisonNarrative],
) -> list[RunComparisonNarrative]:
  ordered = sorted(
    narratives,
    key=lambda narrative: (-narrative.insight_score, narrative.run_id),
  )
  return [
    replace(
      narrative,
      rank=index + 1,
      is_primary=index == 0,
    )
    for index, narrative in enumerate(ordered)
  ]


def _score_comparison_narrative(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> tuple[float, dict[str, Any]]:
  weights = COMPARISON_INTENT_WEIGHTS[intent]
  metric_components = {
    "total_return_pct": _build_metric_score_component(
      delta=total_return_delta,
      weight=weights["return"],
    ),
    "max_drawdown_pct": _build_metric_score_component(
      delta=max_drawdown_delta,
      weight=weights["drawdown"],
    ),
    "win_rate_pct": _build_metric_score_component(
      delta=win_rate_delta,
      weight=weights["win_rate"],
    ),
    "trade_count": _build_metric_score_component(
      delta=trade_count_delta,
      weight=weights["trade_count"],
      cap=50.0,
    ),
  }
  semantic_components = _build_comparison_semantic_delta_breakdown(
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )
  semantic_components["vocabulary"] = _build_comparison_semantic_vocabulary_breakdown(
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )
  semantic_components["provenance_richness"] = _build_comparison_provenance_richness_breakdown(
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )
  context_components = _build_comparison_context_score_breakdown(
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )

  metric_total = round(
    sum(component["score"] for component in metric_components.values()),
    2,
  )
  semantic_total = round(
    sum(component["score"] for component in semantic_components.values()),
    2,
  )
  context_total = _context_subtotal(context_components)
  if metric_total + semantic_total + context_total == 0.0 and _has_reference_context(run, baseline_run):
    context_components["reference_floor"] = {
      "applied": True,
      "score": weights["reference_floor"],
    }
    context_total = _context_subtotal(context_components)
  score = round(metric_total + semantic_total + context_total, 2)

  breakdown = {
    "metrics": {
      "total": metric_total,
      "components": metric_components,
    },
    "semantics": {
      "total": semantic_total,
      "components": semantic_components,
    },
    "context": {
      "total": context_total,
      "components": context_components,
    },
    "total": score,
  }
  return score, breakdown


def _build_metric_score_component(
  *,
  delta: float | int | None,
  weight: float,
  cap: float | None = None,
) -> dict[str, Any]:
  raw_delta = abs(float(delta or 0.0))
  effective_delta = min(raw_delta, cap) if cap is not None else raw_delta
  score = round(effective_delta * weight, 2)
  return {
    "delta": 0.0 if delta is None else float(delta),
    "effective_delta": effective_delta,
    "weight": weight,
    "score": score,
  }


def _build_comparison_semantic_delta_breakdown(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, dict[str, Any]]:
  baseline_semantics = _strategy_semantics(baseline_run)
  run_semantics = _strategy_semantics(run)
  strategy_kind_applied = baseline_semantics.strategy_kind != run_semantics.strategy_kind
  execution_applied = _normalized_semantic_text(
    baseline_semantics.execution_model
  ) != _normalized_semantic_text(run_semantics.execution_model) and _normalized_semantic_text(
    run_semantics.execution_model
  ) is not None
  source_applied = _normalized_semantic_text(
    baseline_semantics.source_descriptor
  ) != _normalized_semantic_text(run_semantics.source_descriptor) and _normalized_semantic_text(
    run_semantics.source_descriptor
  ) is not None
  parameter_contract_applied = _normalized_semantic_text(
    baseline_semantics.parameter_contract
  ) != _normalized_semantic_text(run_semantics.parameter_contract) and _normalized_semantic_text(
    run_semantics.parameter_contract
  ) is not None
  return {
    "strategy_kind": {
      "applied": strategy_kind_applied,
      "baseline": baseline_semantics.strategy_kind,
      "target": run_semantics.strategy_kind,
      "weight": weights["semantic_kind_bonus"],
      "score": weights["semantic_kind_bonus"] if strategy_kind_applied else 0.0,
    },
    "execution_model": {
      "applied": execution_applied,
      "baseline": _normalized_semantic_text(baseline_semantics.execution_model),
      "target": _normalized_semantic_text(run_semantics.execution_model),
      "weight": weights["semantic_execution_bonus"],
      "score": weights["semantic_execution_bonus"] if execution_applied else 0.0,
    },
    "source_descriptor": {
      "applied": source_applied,
      "baseline": _normalized_semantic_text(baseline_semantics.source_descriptor),
      "target": _normalized_semantic_text(run_semantics.source_descriptor),
      "weight": weights["semantic_source_bonus"],
      "score": weights["semantic_source_bonus"] if source_applied else 0.0,
    },
    "parameter_contract": {
      "applied": parameter_contract_applied,
      "baseline": _normalized_semantic_text(baseline_semantics.parameter_contract),
      "target": _normalized_semantic_text(run_semantics.parameter_contract),
      "weight": weights["semantic_parameter_contract_bonus"],
      "score": (
        weights["semantic_parameter_contract_bonus"]
        if parameter_contract_applied
        else 0.0
      ),
    },
  }


def _normalized_semantic_text(value: str | None) -> str | None:
  if value is None:
    return None
  normalized = value.strip()
  return normalized or None


def _build_comparison_semantic_vocabulary_breakdown(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, Any]:
  baseline_schema = _strategy_parameter_schema(baseline_run)
  run_schema = _strategy_parameter_schema(run)
  baseline_parameters = _strategy_parameter_values(baseline_run)
  run_parameters = _strategy_parameter_values(run)

  changed_keys = sorted(
    key
    for key in set(baseline_parameters) | set(run_parameters)
    if baseline_parameters.get(key) != run_parameters.get(key)
  )

  richness_units = 0.0
  for key in changed_keys:
    schema_entry = run_schema.get(key)
    if not isinstance(schema_entry, dict):
      schema_entry = baseline_schema.get(key)
    richness_units += _parameter_semantic_descriptor_score(schema_entry)

  schema_richness_delta = max(
    _semantic_schema_richness(run_schema) - _semantic_schema_richness(baseline_schema),
    0.0,
  )
  richness_units += min(schema_richness_delta, 4.0) * 0.35
  capped_units = min(richness_units, 8.0)
  score = round(capped_units * weights["semantic_vocabulary_unit_bonus"], 2)
  return {
    "changed_keys": changed_keys,
    "schema_richness_delta": round(schema_richness_delta, 2),
    "units": round(richness_units, 2),
    "capped_units": round(capped_units, 2),
    "weight": weights["semantic_vocabulary_unit_bonus"],
    "score": score,
  }


def _build_comparison_provenance_richness_breakdown(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, Any]:
  baseline_richness = _benchmark_provenance_richness(baseline_run)
  target_richness = _benchmark_provenance_richness(run)
  richness_delta = max(target_richness - baseline_richness, 0.0)
  capped_units = min(richness_delta, 10.0)
  score = round(capped_units * weights["provenance_richness_unit_bonus"], 2)
  return {
    "baseline_units": round(baseline_richness, 2),
    "target_units": round(target_richness, 2),
    "units": round(richness_delta, 2),
    "capped_units": round(capped_units, 2),
    "weight": weights["provenance_richness_unit_bonus"],
    "score": score,
  }


def _build_comparison_context_score_breakdown(
  *,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, dict[str, Any]]:
  native_reference_applied = comparison_type == "native_vs_reference"
  reference_applied = comparison_type == "reference_vs_reference"
  status_applied = run.status != baseline_run.status
  benchmark_story_applied = bool(_extract_benchmark_story(run) or _extract_benchmark_story(baseline_run))
  context_components = {
    "native_reference_bonus": {
      "applied": native_reference_applied,
      "score": weights["native_reference_bonus"] if native_reference_applied else 0.0,
    },
    "reference_bonus": {
      "applied": reference_applied,
      "score": weights["reference_bonus"] if reference_applied else 0.0,
    },
    "status_bonus": {
      "applied": status_applied,
      "score": weights["status_bonus"] if status_applied else 0.0,
    },
    "benchmark_story_bonus": {
      "applied": benchmark_story_applied,
      "score": weights["benchmark_story_bonus"] if benchmark_story_applied else 0.0,
    },
    "reference_floor": {
      "applied": False,
      "score": 0.0,
    },
  }
  return context_components


def _context_subtotal(components: dict[str, dict[str, Any]]) -> float:
  return round(sum(float(component["score"]) for component in components.values()), 2)


def _strategy_parameter_schema(run: RunRecord) -> dict[str, Any]:
  strategy_snapshot = run.provenance.strategy
  if strategy_snapshot is None:
    return {}
  return strategy_snapshot.parameter_snapshot.schema


def _strategy_parameter_values(run: RunRecord) -> dict[str, Any]:
  strategy_snapshot = run.provenance.strategy
  if strategy_snapshot is None:
    return run.config.parameters
  return strategy_snapshot.parameter_snapshot.resolved or run.config.parameters


def _parameter_semantic_descriptor_score(schema_entry: object) -> float:
  if not isinstance(schema_entry, dict):
    return 0.0
  score = 0.0
  if _normalized_semantic_text(schema_entry.get("semantic_hint")) is not None:
    score += 1.0
  if (
    _normalized_semantic_text(schema_entry.get("delta_higher_label")) is not None
    or _normalized_semantic_text(schema_entry.get("delta_lower_label")) is not None
  ):
    score += 0.75
  semantic_ranks = schema_entry.get("semantic_ranks")
  if isinstance(semantic_ranks, dict) and semantic_ranks:
    score += 0.5
  if _normalized_semantic_text(schema_entry.get("unit")) is not None:
    score += 0.25
  return score


def _semantic_schema_richness(schema: dict[str, Any]) -> float:
  return sum(
    _parameter_semantic_descriptor_score(schema_entry)
    for schema_entry in schema.values()
  )


def _benchmark_provenance_richness(run: RunRecord) -> float:
  score = 0.0
  for artifact in run.provenance.benchmark_artifacts:
    if artifact.exists:
      score += 0.2
    score += 0.8
    score += min(len(artifact.summary), 6) * 0.2
    score += min(len(artifact.sections), 8) * 0.3
    if artifact.summary_source_path:
      score += 0.5
    benchmark_story = artifact.sections.get("benchmark_story")
    if isinstance(benchmark_story, dict):
      score += min(len(benchmark_story), 6) * 0.25
  return score


def _normalize_comparison_intent(intent: str | None) -> str:
  if intent in (None, ""):
    return COMPARISON_INTENT_DEFAULT
  if intent not in COMPARISON_INTENT_WEIGHTS:
    supported = ", ".join(sorted(COMPARISON_INTENT_WEIGHTS))
    raise ValueError(f"Unsupported comparison intent: {intent}. Expected one of: {supported}.")
  return intent


def _build_comparison_narrative_title(
  *,
  intent: str,
  comparison_type: str,
  target_subject: str,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  versus_baseline = "the baseline" if comparison_type != "native_vs_reference" else f"the native/reference baseline {baseline_label}"
  if total_return_delta is not None and max_drawdown_delta is not None:
    if intent == "benchmark_validation":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} favors {target_subject}: higher return without extra drawdown versus {versus_baseline}."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} running hotter than {versus_baseline}: more return, but deeper drawdown."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} staying safer than {versus_baseline}, but giving up return."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as off-benchmark versus {versus_baseline}."
      return f"{copy['title_prefix']} shows {target_subject} holding close to {versus_baseline}."
    if intent == "execution_regression":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} sees {target_subject} diverging from {versus_baseline}, but not as a degradation."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} changing risk behavior versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} throttling risk versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as a clear degradation versus {versus_baseline}."
      return f"{copy['title_prefix']} sees only limited drift in {target_subject} versus {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} clearly prefers {target_subject} over {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} treats {target_subject} as the higher-upside variant versus {versus_baseline}, with a drawdown tradeoff."
    if total_return_delta < 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} treats {target_subject} as the more defensive variant versus {versus_baseline}."
    if total_return_delta < 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} finds little upside in {target_subject} versus {versus_baseline}."
    return f"{copy['title_prefix']} keeps {target_subject} near-neutral against {versus_baseline}."
  if total_return_delta is not None:
    if intent == "strategy_tuning":
      if total_return_delta > 0:
        return f"{copy['title_prefix']} prefers {target_subject} for return potential versus {versus_baseline}."
      if total_return_delta < 0:
        return f"{copy['title_prefix']} sees {target_subject} as lower-upside than {versus_baseline}."
      return f"{copy['title_prefix']} sees no return edge between {target_subject} and {versus_baseline}."
    if total_return_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} ahead of {versus_baseline} on total return."
    if total_return_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} trailing {versus_baseline} on total return."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on total return."
  if max_drawdown_delta is not None:
    if max_drawdown_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} containing drawdown better than {versus_baseline}."
    if max_drawdown_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} running with deeper drawdown than {versus_baseline}."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on drawdown."
  if comparison_type == "native_vs_reference":
    return f"{copy['title_prefix']} frames {target_subject} as the comparison counterpart to {baseline_label}."
  return f"{copy['title_prefix']} reads {target_subject} against {baseline_label}."


def _build_comparison_narrative_summary(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  semantic_context = _build_comparison_semantic_context_sentence(
    baseline_run=baseline_run,
    run=run,
    comparison_type=comparison_type,
  )
  metric_shifts: list[str] = []
  if total_return_delta is not None:
    metric_shifts.append(f"return {_format_metric_delta(total_return_delta, 'pct_points')}")
  if max_drawdown_delta is not None:
    metric_shifts.append(f"drawdown {_format_metric_delta(max_drawdown_delta, 'pct_points')}")
  if win_rate_delta is not None:
    metric_shifts.append(f"win rate {_format_metric_delta(win_rate_delta, 'pct_points')}")
  if trade_count_delta is not None:
    metric_shifts.append(f"trades {_format_metric_delta(trade_count_delta, 'count')}")
  if metric_shifts:
    if intent == "benchmark_validation":
      summary = (
        f"{copy['summary_prefix']} treats these shifts as benchmark drift against "
        f"{baseline_label}: {', '.join(metric_shifts)}."
      )
      return f"{summary} {semantic_context}" if semantic_context else summary
    if intent == "execution_regression":
      summary = (
        f"{copy['summary_prefix']} interprets these changes as execution drift against "
        f"{baseline_label}: {', '.join(metric_shifts)}."
      )
      return f"{summary} {semantic_context}" if semantic_context else summary
    summary = (
      f"{copy['summary_prefix']} reads these changes as optimization tradeoffs against "
      f"{baseline_label}: {', '.join(metric_shifts)}."
    )
    return f"{summary} {semantic_context}" if semantic_context else summary

  if comparison_type == "native_vs_reference" and _has_reference_context(run, baseline_run):
    summary = copy["partial_summary"]
    return f"{summary} {semantic_context}" if semantic_context else summary
  if run.status != baseline_run.status:
    summary = (
      f"{copy['summary_prefix']} also notes a status split: {run.status} versus "
      f"{baseline_run.status}."
    )
    return f"{summary} {semantic_context}" if semantic_context else summary
  return semantic_context


def _build_comparison_narrative_bullets(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  target_label: str,
  baseline_label: str,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> list[str]:
  bullets: list[str] = []

  lane_context = _build_lane_context_bullet(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
  )
  if lane_context is not None:
    bullets.append(lane_context)

  activity_context = _build_activity_context_bullet(
    intent=intent,
    run=run,
    trade_count_delta=trade_count_delta,
    win_rate_delta=win_rate_delta,
  )
  if activity_context is not None:
    bullets.append(activity_context)

  reference_story = _build_reference_story_bullet(intent=intent, baseline_run=baseline_run, run=run)
  if reference_story is not None:
    bullets.append(reference_story)

  if not bullets and comparison_type == "native_vs_reference":
    bullets.append(f"{COMPARISON_INTENT_COPY[intent]['lane_prefix']}: {target_label} is the reference/native counterpart to {baseline_label}.")
  return bullets[:3]


def _build_lane_context_bullet(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  if comparison_type != "native_vs_reference":
    return None
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = run if run.provenance.lane == "reference" else baseline_run
  native_run = baseline_run if reference_run is run else run
  reference_label = _comparison_run_label(reference_run)
  native_role = _format_comparison_semantic_role(native_run)
  reference_role = _format_comparison_semantic_role(reference_run, include_execution=True)
  reference_source = _strategy_semantics(reference_run).source_descriptor
  source_suffix = f" / source {reference_source}" if reference_source else ""
  return (
    f"{copy['lane_prefix']}: {native_role} engine {_comparison_run_label(native_run)} is being "
    f"read against {reference_role} benchmark {reference_label}{source_suffix}."
  )


def _build_activity_context_bullet(
  *,
  intent: str,
  run: RunRecord,
  trade_count_delta: float | int | None,
  win_rate_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  trade_count = _resolve_run_metric_value(run, "trade_count")
  win_rate = _resolve_run_metric_value(run, "win_rate_pct")
  segments: list[str] = []
  if trade_count is not None:
    segment = f"trade flow landed at {trade_count}"
    if trade_count_delta is not None:
      segment += f" ({_format_metric_delta(trade_count_delta, 'count')} vs baseline)"
    segments.append(segment)
  if win_rate is not None:
    segment = f"win rate closed at {win_rate}%"
    if win_rate_delta is not None:
      segment += f" ({_format_metric_delta(win_rate_delta, 'pct_points')} vs baseline)"
    segments.append(segment)
  if not segments:
    return None
  return f"{copy['activity_prefix']}: " + "; ".join(segments) + "."


def _build_reference_story_bullet(
  *,
  intent: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = None
  if run.provenance.lane == "reference":
    reference_run = run
  elif baseline_run.provenance.lane == "reference":
    reference_run = baseline_run
  if reference_run is None:
    return None
  benchmark_story = _extract_benchmark_story(reference_run)
  if not benchmark_story:
    return None
  for key in ("headline", "signal_context", "exit_context", "market_context", "pair_context", "portfolio_context"):
    value = benchmark_story.get(key)
    if isinstance(value, str) and value:
      return f"{copy['reference_prefix']}: {value}"
  return None


def _classify_comparison_type(baseline_run: RunRecord, run: RunRecord) -> str:
  lanes = {baseline_run.provenance.lane, run.provenance.lane}
  if lanes == {"native", "reference"}:
    return "native_vs_reference"
  if lanes == {"reference"}:
    return "reference_vs_reference"
  if lanes == {"native"}:
    return "native_vs_native"
  return "run_vs_baseline"


def _comparison_run_label(run: RunRecord) -> str:
  if run.provenance.reference is not None and run.provenance.reference.title:
    return run.provenance.reference.title
  if run.provenance.strategy is not None and run.provenance.strategy.name:
    return run.provenance.strategy.name
  return run.config.strategy_id


def _comparison_subject_label(run: RunRecord) -> str:
  label = _comparison_run_label(run)
  semantics = _strategy_semantics(run)
  role = _format_comparison_semantic_role(run)
  if run.provenance.lane == "reference":
    return f"{role} benchmark {label}"
  if semantics.strategy_kind == "imported_module":
    return f"{role} strategy {label}"
  if run.provenance.lane == "native":
    return f"{role} run {label}"
  return label


def _has_reference_context(run: RunRecord, baseline_run: RunRecord) -> bool:
  return any(candidate.provenance.lane == "reference" for candidate in (run, baseline_run))


def _build_metric_semantic_annotation_suffix(
  *,
  baseline_run: RunRecord,
  runs: list[RunRecord],
) -> str | None:
  baseline_role = _format_comparison_semantic_role(baseline_run, include_execution=True)
  comparison_roles = [
    role
    for role in dict.fromkeys(
      _build_metric_annotation_role_label(baseline_run=baseline_run, run=run)
      for run in runs
      if run.config.run_id != baseline_run.config.run_id
    )
    if role is not None
  ]
  if not comparison_roles:
    return None
  if len(comparison_roles) == 1:
    return f"baseline {baseline_role}; compared against {comparison_roles[0]}"
  listed_roles = ", ".join(comparison_roles[:2])
  if len(comparison_roles) > 2:
    listed_roles = f"{listed_roles}, +{len(comparison_roles) - 2} more"
  return f"baseline {baseline_role}; compared against {listed_roles}"


def _build_metric_annotation_role_label(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  baseline_role = _format_comparison_semantic_role(baseline_run, include_execution=True)
  run_role = _format_comparison_semantic_role(run, include_execution=True)
  if run_role == baseline_role:
    return None
  return run_role


def _build_metric_delta_semantic_suffix(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  role = _build_metric_annotation_role_label(baseline_run=baseline_run, run=run)
  if role is None:
    return None
  source_descriptor = _strategy_semantics(run).source_descriptor
  if source_descriptor is None:
    return role
  return f"{role} ({source_descriptor})"


def _build_comparison_semantic_context_sentence(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  comparison_type: str,
) -> str | None:
  if not _comparison_has_semantic_signal(baseline_run=baseline_run, run=run):
    return None
  baseline_role = _format_comparison_semantic_role(baseline_run, include_execution=True)
  run_role = _format_comparison_semantic_role(run, include_execution=True)
  run_source = _strategy_semantics(run).source_descriptor
  if comparison_type == "native_vs_reference":
    summary = f"Semantic context compares {baseline_role} execution to {run_role}"
  else:
    summary = f"Semantic context compares {run_role} against {baseline_role}"
  if run_source:
    summary = f"{summary} (source {run_source})"
  return f"{summary}."


def _comparison_has_semantic_signal(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
) -> bool:
  baseline_semantics = _strategy_semantics(baseline_run)
  run_semantics = _strategy_semantics(run)
  return (
    baseline_run.provenance.lane != run.provenance.lane
    or baseline_semantics.strategy_kind != run_semantics.strategy_kind
    or baseline_semantics.execution_model != run_semantics.execution_model
    or baseline_semantics.source_descriptor != run_semantics.source_descriptor
    or baseline_semantics.parameter_contract != run_semantics.parameter_contract
  )


def _strategy_semantics(run: RunRecord) -> StrategyCatalogSemantics:
  if run.provenance.strategy is not None:
    return run.provenance.strategy.catalog_semantics
  return StrategyCatalogSemantics()


def _format_comparison_semantic_role(
  run: RunRecord,
  *,
  include_execution: bool = False,
) -> str:
  semantics = _strategy_semantics(run)
  lane = run.provenance.lane or "run"
  if semantics.strategy_kind == "reference_delegate":
    role = "reference delegate"
  elif semantics.strategy_kind == "imported_module":
    role = "imported module"
  elif semantics.strategy_kind in ("", "standard"):
    role = f"{lane} standard"
  else:
    normalized_kind = semantics.strategy_kind.replace("_", " ")
    role = normalized_kind if lane in normalized_kind else f"{lane} {normalized_kind}"
  execution_label = _format_comparison_execution_label(run)
  if include_execution and execution_label:
    return f"{role} via {execution_label}"
  return role


def _format_comparison_execution_label(run: RunRecord) -> str | None:
  if run.provenance.integration_mode:
    return run.provenance.integration_mode
  execution_model = _strategy_semantics(run).execution_model.strip()
  if execution_model and len(execution_model) <= 40:
    return execution_model
  return None


def _metric_row_delta(
  metric_row_by_key: dict[str, RunComparisonMetricRow],
  key: str,
  run_id: str,
) -> float | int | None:
  metric_row = metric_row_by_key.get(key)
  if metric_row is None:
    return None
  return metric_row.deltas_vs_baseline.get(run_id)


def _resolve_run_metric_value(run: RunRecord, key: str) -> float | int | None:
  direct_value = _coerce_metric_value(run.metrics.get(key))
  if direct_value is not None:
    return direct_value
  return _extract_benchmark_metric_value(run, key)


def _extract_benchmark_metric_value(run: RunRecord, key: str) -> float | int | None:
  summary_key_map = {
    "total_return_pct": "profit_total_pct",
    "max_drawdown_pct": "max_drawdown_pct",
    "trade_count": "trade_count",
    "win_rate_pct": "win_rate_pct",
  }
  summary_key = summary_key_map.get(key)
  if summary_key is None:
    return None

  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    value = _coerce_metric_value(artifact.summary.get(summary_key))
    if value is not None:
      return value
    if key == "win_rate_pct":
      for section_name, row_key in (
        ("strategy_comparison", "best"),
        ("pair_metrics", "total"),
      ):
        section = artifact.sections.get(section_name)
        if not isinstance(section, dict):
          continue
        candidate_row = section.get(row_key)
        if isinstance(candidate_row, dict):
          value = _coerce_metric_value(candidate_row.get(summary_key))
          if value is not None:
            return value
        preview = section.get("preview")
        if isinstance(preview, list) and preview:
          first_row = preview[0]
          if isinstance(first_row, dict):
            value = _coerce_metric_value(first_row.get(summary_key))
            if value is not None:
              return value
  return None


def _extract_benchmark_story(run: RunRecord) -> dict[str, str]:
  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    story = artifact.sections.get("benchmark_story")
    if not isinstance(story, dict):
      continue
    normalized_story = {
      key: value
      for key, value in story.items()
      if isinstance(value, str) and value
    }
    if normalized_story:
      return normalized_story
  return {}


def _benchmark_artifact_priority(kind: str) -> int:
  priorities = {
    "result_snapshot": 0,
    "result_snapshot_root": 1,
    "result_manifest": 2,
  }
  return priorities.get(kind, 100)


def _format_metric_delta(value: float | int | None, unit: str) -> str:
  if value is None:
    return "n/a"
  prefix = "+" if value > 0 else ""
  if unit == "pct_points":
    return f"{prefix}{value} pts"
  if unit == "count":
    suffix = "trade" if value in {-1, 1} else "trades"
    return f"{prefix}{value} {suffix}"
  return f"{prefix}{value}"


def _coerce_metric_value(value: object) -> float | int | None:
  if isinstance(value, bool) or not isinstance(value, Number):
    return None
  if isinstance(value, int):
    return value
  return round(float(value), 2)


def _calculate_metric_delta(
  value: float | int | None,
  baseline_value: float | int | None,
) -> float | int | None:
  if value is None or baseline_value is None:
    return None
  delta = value - baseline_value
  if isinstance(value, int) and isinstance(baseline_value, int):
    return int(delta)
  return round(float(delta), 2)
