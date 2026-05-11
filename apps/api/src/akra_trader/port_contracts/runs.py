from __future__ import annotations

from datetime import datetime
from typing import Protocol

from akra_trader.domain.models import OperationLog
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus


class RunRepositoryPort(Protocol):
  def save_run(self, run: RunRecord) -> RunRecord: ...

  def get_run(self, run_id: str) -> RunRecord | None: ...

  def list_runs(self, mode: str | None = None) -> list[RunRecord]: ...

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None: ...

  def save_log(self, log: OperationLog) -> OperationLog: ...

  def list_logs(
    self,
    *,
    run_id: str | None = None,
    mode: str | None = None,
    severity: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 200,
  ) -> list[OperationLog]: ...
