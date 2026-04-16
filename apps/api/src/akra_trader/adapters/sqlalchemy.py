from __future__ import annotations

from datetime import UTC
from datetime import datetime
from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.ports import RunRepositoryPort


metadata = MetaData()
run_records = Table(
  "run_records",
  metadata,
  Column("run_id", String, primary_key=True),
  Column("mode", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("started_at", String, nullable=False),
  Column("ended_at", String, nullable=True),
  Column("payload", JSON, nullable=False),
)


class SqlAlchemyRunRepository(RunRepositoryPort):
  _terminal_statuses = {RunStatus.COMPLETED, RunStatus.STOPPED, RunStatus.FAILED}
  _adapter = TypeAdapter(RunRecord)

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = self._build_engine(database_url)
    metadata.create_all(self._engine)

  def save_run(self, run: RunRecord) -> RunRecord:
    row = self._build_row(run)
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(run_records.c.run_id).where(run_records.c.run_id == run.config.run_id)
      ).first()
      if existing is None:
        connection.execute(insert(run_records).values(**row))
      else:
        connection.execute(
          update(run_records)
          .where(run_records.c.run_id == run.config.run_id)
          .values(**row)
        )
    return run

  def get_run(self, run_id: str) -> RunRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(run_records.c.payload).where(run_records.c.run_id == run_id)
      ).mappings().first()
    if row is None:
      return None
    return self._adapter.validate_python(row["payload"])

  def compare_runs(self, run_ids: list[str]) -> list[RunRecord]:
    if not run_ids:
      return []
    statement = select(run_records.c.run_id, run_records.c.payload).where(
      run_records.c.run_id.in_(run_ids)
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    run_map = {
      row["run_id"]: self._adapter.validate_python(row["payload"])
      for row in rows
    }
    return [run_map[run_id] for run_id in run_ids if run_id in run_map]

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
  ) -> list[RunRecord]:
    statement = select(run_records.c.payload).order_by(
      run_records.c.started_at.desc(),
      run_records.c.run_id.desc(),
    )
    if mode is not None:
      statement = statement.where(run_records.c.mode == mode)

    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    runs = [self._adapter.validate_python(row["payload"]) for row in rows]
    if strategy_id is not None:
      runs = [run for run in runs if run.config.strategy_id == strategy_id]
    if strategy_version is not None:
      runs = [run for run in runs if run.config.strategy_version == strategy_version]
    if rerun_boundary_id is not None:
      runs = [run for run in runs if run.provenance.rerun_boundary_id == rerun_boundary_id]
    return runs

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None:
    run = self.get_run(run_id)
    if run is None:
      return None

    run.status = status
    if status in self._terminal_statuses:
      run.ended_at = datetime.now(UTC)
    return self.save_run(run)

  def _build_row(self, run: RunRecord) -> dict:
    payload = self._adapter.dump_python(run, mode="json")
    return {
      "run_id": run.config.run_id,
      "mode": run.config.mode.value,
      "status": run.status.value,
      "started_at": run.started_at.isoformat(),
      "ended_at": run.ended_at.isoformat() if run.ended_at is not None else None,
      "payload": payload,
    }

  def _build_engine(self, database_url: str) -> Engine:
    url = make_url(database_url)
    engine_kwargs = {"pool_pre_ping": True}
    if url.get_backend_name() == "sqlite" and url.database not in {None, "", ":memory:"}:
      Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
      return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        **engine_kwargs,
      )
    return create_engine(database_url, **engine_kwargs)
