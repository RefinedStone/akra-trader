from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from akra_trader.domain.models import BenchmarkArtifact
  from akra_trader.domain.models import ReferenceSource
  from akra_trader.domain.models import RunExperimentMetadata
  from akra_trader.domain.models import StrategyCatalogSemantics


def _default_strategy_catalog_semantics() -> StrategyCatalogSemantics:
  from akra_trader.domain.models import StrategyCatalogSemantics

  return StrategyCatalogSemantics()


def _default_run_experiment_metadata() -> RunExperimentMetadata:
  from akra_trader.domain.models import RunExperimentMetadata

  return RunExperimentMetadata()


@dataclass(frozen=True)
class RunComparisonRun:
  run_id: str
  mode: str
  status: str
  lane: str
  strategy_id: str
  strategy_name: str | None
  strategy_version: str
  symbols: tuple[str, ...]
  timeframe: str
  started_at: datetime
  catalog_semantics: StrategyCatalogSemantics = field(
    default_factory=_default_strategy_catalog_semantics
  )
  ended_at: datetime | None = None
  reference_id: str | None = None
  reference_version: str | None = None
  integration_mode: str | None = None
  reference: ReferenceSource | None = None
  working_directory: str | None = None
  rerun_boundary_id: str | None = None
  rerun_boundary_state: str = "range_only"
  dataset_identity: str | None = None
  experiment: RunExperimentMetadata = field(default_factory=_default_run_experiment_metadata)
  external_command: tuple[str, ...] = ()
  artifact_paths: tuple[str, ...] = ()
  benchmark_artifacts: tuple[BenchmarkArtifact, ...] = ()
  metrics: dict[str, Any] = field(default_factory=dict)
  notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunComparisonMetricRow:
  key: str
  label: str
  unit: str
  higher_is_better: bool | None = None
  values: dict[str, float | int | None] = field(default_factory=dict)
  deltas_vs_baseline: dict[str, float | int | None] = field(default_factory=dict)
  delta_annotations: dict[str, str] = field(default_factory=dict)
  annotation: str | None = None
  best_run_id: str | None = None


@dataclass(frozen=True)
class RunComparisonNarrative:
  run_id: str
  baseline_run_id: str
  comparison_type: str
  title: str
  summary: str
  bullets: tuple[str, ...] = ()
  score_breakdown: dict[str, Any] = field(default_factory=dict)
  rank: int = 0
  insight_score: float = 0.0
  is_primary: bool = False


@dataclass(frozen=True)
class RunComparison:
  requested_run_ids: tuple[str, ...]
  baseline_run_id: str
  runs: tuple[RunComparisonRun, ...]
  metric_rows: tuple[RunComparisonMetricRow, ...]
  intent: str = "benchmark_validation"
  narratives: tuple[RunComparisonNarrative, ...] = ()
