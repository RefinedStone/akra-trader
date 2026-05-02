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
