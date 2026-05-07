from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from akra_trader.domain.model_types.strategy_catalog import RunExperimentMetadata
from akra_trader.domain.model_types.strategy_catalog import StrategyCatalogSemantics

if TYPE_CHECKING:
  from akra_trader.domain.model_types.run_execution import BenchmarkArtifact


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
  catalog_semantics: StrategyCatalogSemantics = field(default_factory=StrategyCatalogSemantics)
  ended_at: datetime | None = None
  rerun_boundary_id: str | None = None
  rerun_boundary_state: str = "range_only"
  dataset_identity: str | None = None
  experiment: RunExperimentMetadata = field(default_factory=RunExperimentMetadata)
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
