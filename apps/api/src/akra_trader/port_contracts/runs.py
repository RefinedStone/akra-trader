from __future__ import annotations

from typing import Protocol

from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus


class RunRepositoryPort(Protocol):
  def save_run(self, run: RunRecord) -> RunRecord: ...

  def get_run(self, run_id: str) -> RunRecord | None: ...

  def compare_runs(self, run_ids: list[str]) -> list[RunRecord]: ...

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
    preset_id: str | None = None,
    benchmark_family: str | None = None,
    dataset_identity: str | None = None,
    tags: tuple[str, ...] = (),
  ) -> list[RunRecord]: ...

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None: ...
