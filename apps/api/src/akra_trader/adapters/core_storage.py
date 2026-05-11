from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
import json
from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine

from akra_trader.domain.models import OperationLog
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus


class InMemoryCoreRepository:
  def __init__(self) -> None:
    self._runs: OrderedDict[str, RunRecord] = OrderedDict()
    self._logs: OrderedDict[str, OperationLog] = OrderedDict()

  def save_run(self, run: RunRecord) -> RunRecord:
    self._runs[run.config.run_id] = run
    return run

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get(run_id)

  def list_runs(self, mode: str | None = None) -> list[RunRecord]:
    runs = list(reversed(self._runs.values()))
    if mode is not None:
      runs = [run for run in runs if run.config.mode.value == mode]
    return runs

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None:
    run = self.get_run(run_id)
    if run is None:
      return None
    run.status = status
    self.save_run(run)
    return run

  def save_log(self, log: OperationLog) -> OperationLog:
    self._logs[log.log_id] = log
    return log

  def list_logs(
    self,
    *,
    run_id: str | None = None,
    mode: str | None = None,
    severity: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 200,
  ) -> list[OperationLog]:
    logs = list(reversed(self._logs.values()))
    if run_id is not None:
      logs = [log for log in logs if log.run_id == run_id]
    if mode is not None:
      logs = [log for log in logs if log.mode is not None and log.mode.value == mode]
    if severity is not None:
      logs = [log for log in logs if log.severity == severity]
    if since is not None:
      logs = [log for log in logs if log.recorded_at >= since]
    if until is not None:
      logs = [log for log in logs if log.recorded_at <= until]
    return logs[:limit]


metadata = MetaData()

core_runs = Table(
  "core_runs",
  metadata,
  Column("id", Integer, primary_key=True),
  Column("run_id", String(80), nullable=False, unique=True, index=True),
  Column("mode", String(20), nullable=False, index=True),
  Column("status", String(20), nullable=False, index=True),
  Column("started_at", DateTime(timezone=True), nullable=False, index=True),
  Column("ended_at", DateTime(timezone=True), nullable=True),
  Column("payload", Text, nullable=False),
)

operation_logs = Table(
  "operation_logs",
  metadata,
  Column("id", Integer, primary_key=True),
  Column("log_id", String(100), nullable=False, unique=True, index=True),
  Column("recorded_at", DateTime(timezone=True), nullable=False, index=True),
  Column("layer", String(40), nullable=False, index=True),
  Column("event_type", String(80), nullable=False, index=True),
  Column("severity", String(20), nullable=False, index=True),
  Column("run_id", String(80), nullable=True, index=True),
  Column("mode", String(20), nullable=True, index=True),
  Column("payload", Text, nullable=False),
)


class SqlAlchemyCoreRepository(InMemoryCoreRepository):
  _run_adapter = TypeAdapter(RunRecord)
  _log_adapter = TypeAdapter(OperationLog)

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = _build_engine(database_url)
    metadata.create_all(self._engine)

  def save_run(self, run: RunRecord) -> RunRecord:
    payload = self._run_adapter.dump_python(run, mode="json")
    row = {
      "run_id": run.config.run_id,
      "mode": run.config.mode.value,
      "status": run.status.value,
      "started_at": run.started_at,
      "ended_at": run.ended_at,
      "payload": json.dumps(payload, separators=(",", ":"), sort_keys=True),
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(core_runs.c.run_id).where(core_runs.c.run_id == run.config.run_id)
      ).first()
      if existing is None:
        connection.execute(insert(core_runs).values(**row))
      else:
        connection.execute(
          update(core_runs).where(core_runs.c.run_id == run.config.run_id).values(**row)
        )
    return run

  def get_run(self, run_id: str) -> RunRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(core_runs.c.payload).where(core_runs.c.run_id == run_id)
      ).mappings().first()
    if row is None:
      return None
    return self._run_adapter.validate_python(json.loads(row["payload"]))

  def list_runs(self, mode: str | None = None) -> list[RunRecord]:
    statement = select(core_runs.c.payload).order_by(
      core_runs.c.started_at.desc(),
      core_runs.c.run_id.desc(),
    )
    if mode is not None:
      statement = statement.where(core_runs.c.mode == mode)
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return [self._run_adapter.validate_python(json.loads(row["payload"])) for row in rows]

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None:
    run = self.get_run(run_id)
    if run is None:
      return None
    run.status = status
    self.save_run(run)
    return run

  def save_log(self, log: OperationLog) -> OperationLog:
    payload = self._log_adapter.dump_python(log, mode="json")
    row = {
      "log_id": log.log_id,
      "recorded_at": log.recorded_at,
      "layer": log.layer,
      "event_type": log.event_type,
      "severity": log.severity,
      "run_id": log.run_id,
      "mode": log.mode.value if log.mode is not None else None,
      "payload": json.dumps(payload, separators=(",", ":"), sort_keys=True),
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(operation_logs.c.log_id).where(operation_logs.c.log_id == log.log_id)
      ).first()
      if existing is None:
        connection.execute(insert(operation_logs).values(**row))
      else:
        connection.execute(
          update(operation_logs)
          .where(operation_logs.c.log_id == log.log_id)
          .values(**row)
        )
    return log

  def list_logs(
    self,
    *,
    run_id: str | None = None,
    mode: str | None = None,
    severity: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 200,
  ) -> list[OperationLog]:
    statement = select(operation_logs.c.payload)
    if run_id is not None:
      statement = statement.where(operation_logs.c.run_id == run_id)
    if mode is not None:
      statement = statement.where(operation_logs.c.mode == mode)
    if severity is not None:
      statement = statement.where(operation_logs.c.severity == severity)
    if since is not None:
      statement = statement.where(operation_logs.c.recorded_at >= since)
    if until is not None:
      statement = statement.where(operation_logs.c.recorded_at <= until)
    statement = statement.order_by(
      operation_logs.c.recorded_at.desc(),
      operation_logs.c.log_id.desc(),
    ).limit(limit)
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return [self._log_adapter.validate_python(json.loads(row["payload"])) for row in rows]


def _build_engine(database_url: str) -> Engine:
  if database_url.startswith("sqlite:///"):
    database_path = Path(database_url.removeprefix("sqlite:///"))
    if str(database_path) not in {":memory:", ""}:
      database_path.parent.mkdir(parents=True, exist_ok=True)
  return create_engine(database_url, future=True)
