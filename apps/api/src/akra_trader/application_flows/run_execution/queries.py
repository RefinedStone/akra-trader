from __future__ import annotations

from typing import Iterable

from akra_trader.application_flows.strategy_catalog import _normalize_experiment_filter_value
from akra_trader.application_flows.strategy_catalog import _normalize_experiment_identifier
from akra_trader.application_flows.strategy_catalog import _normalize_experiment_tags
from akra_trader.domain.models import RunRecord


def list_runs(
  flow,
  mode: str | None = None,
  *,
  strategy_id: str | None = None,
  strategy_version: str | None = None,
  rerun_boundary_id: str | None = None,
  preset_id: str | None = None,
  benchmark_family: str | None = None,
  dataset_identity: str | None = None,
  tags: Iterable[str] = (),
) -> list[RunRecord]:
  app = flow.app
  return app._runs.list_runs(
    mode=app._mode_service.normalize(mode),
    strategy_id=strategy_id,
    strategy_version=strategy_version,
    rerun_boundary_id=rerun_boundary_id,
    preset_id=_normalize_experiment_identifier(preset_id),
    benchmark_family=_normalize_experiment_identifier(benchmark_family),
    dataset_identity=_normalize_experiment_filter_value(dataset_identity),
    tags=_normalize_experiment_tags(tags),
  )


def get_run(flow, run_id: str) -> RunRecord | None:
  return flow.app._runs.get_run(run_id)
