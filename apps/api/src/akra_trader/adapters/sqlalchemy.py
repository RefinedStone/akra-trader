from __future__ import annotations

from datetime import UTC
from datetime import datetime
from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import delete
from sqlalchemy import inspect
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
  Column("strategy_id", String, nullable=True, index=True),
  Column("strategy_version", String, nullable=True, index=True),
  Column("rerun_boundary_id", String, nullable=True, index=True),
  Column("dataset_identity", String, nullable=True, index=True),
  Column("preset_id", String, nullable=True, index=True),
  Column("benchmark_family", String, nullable=True, index=True),
  Column("started_at", String, nullable=False),
  Column("ended_at", String, nullable=True),
  Column("payload", JSON, nullable=False),
)
run_record_tags = Table(
  "run_record_tags",
  metadata,
  Column("run_id", String, primary_key=True),
  Column("tag", String, primary_key=True, index=True),
)


class SqlAlchemyRunRepository(RunRepositoryPort):
  _terminal_statuses = {RunStatus.COMPLETED, RunStatus.STOPPED, RunStatus.FAILED}
  _adapter = TypeAdapter(RunRecord)

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = self._build_engine(database_url)
    metadata.create_all(self._engine)
    self._ensure_schema()

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
      connection.execute(delete(run_record_tags).where(run_record_tags.c.run_id == run.config.run_id))
      experiment_tags = tuple(dict.fromkeys(run.provenance.experiment.tags))
      if experiment_tags:
        connection.execute(
          insert(run_record_tags),
          [{"run_id": run.config.run_id, "tag": tag} for tag in experiment_tags],
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
    preset_id: str | None = None,
    benchmark_family: str | None = None,
    dataset_identity: str | None = None,
    tags: tuple[str, ...] = (),
  ) -> list[RunRecord]:
    statement = select(run_records.c.payload).order_by(
      run_records.c.started_at.desc(),
      run_records.c.run_id.desc(),
    )
    if mode is not None:
      statement = statement.where(run_records.c.mode == mode)
    if strategy_id is not None:
      statement = statement.where(run_records.c.strategy_id == strategy_id)
    if strategy_version is not None:
      statement = statement.where(run_records.c.strategy_version == strategy_version)
    if rerun_boundary_id is not None:
      statement = statement.where(run_records.c.rerun_boundary_id == rerun_boundary_id)
    if preset_id is not None:
      statement = statement.where(run_records.c.preset_id == preset_id)
    if benchmark_family is not None:
      statement = statement.where(run_records.c.benchmark_family == benchmark_family)
    if dataset_identity is not None:
      statement = statement.where(run_records.c.dataset_identity == dataset_identity)
    for index, tag in enumerate(tuple(dict.fromkeys(tags))):
      tag_alias = run_record_tags.alias(f"run_record_tags_{index}")
      statement = (
        statement
        .join(tag_alias, tag_alias.c.run_id == run_records.c.run_id)
        .where(tag_alias.c.tag == tag)
      )

    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return [self._adapter.validate_python(row["payload"]) for row in rows]

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
      "strategy_id": run.config.strategy_id,
      "strategy_version": run.config.strategy_version,
      "rerun_boundary_id": run.provenance.rerun_boundary_id,
      "dataset_identity": (
        run.provenance.market_data.dataset_identity
        if run.provenance.market_data is not None
        else None
      ),
      "preset_id": run.provenance.experiment.preset_id,
      "benchmark_family": run.provenance.experiment.benchmark_family,
      "started_at": run.started_at.isoformat(),
      "ended_at": run.ended_at.isoformat() if run.ended_at is not None else None,
      "payload": payload,
    }

  def _ensure_schema(self) -> None:
    inspector = inspect(self._engine)
    existing_columns = {
      column["name"]
      for column in inspector.get_columns("run_records")
    }
    missing_columns = {
      "strategy_id": "TEXT",
      "strategy_version": "TEXT",
      "rerun_boundary_id": "TEXT",
      "dataset_identity": "TEXT",
      "preset_id": "TEXT",
      "benchmark_family": "TEXT",
    }
    with self._engine.begin() as connection:
      for column_name, column_type in missing_columns.items():
        if column_name in existing_columns:
          continue
        connection.exec_driver_sql(
          f"ALTER TABLE run_records ADD COLUMN {column_name} {column_type}"
        )
      for index_name, column_name in (
        ("ix_run_records_strategy_id", "strategy_id"),
        ("ix_run_records_strategy_version", "strategy_version"),
        ("ix_run_records_rerun_boundary_id", "rerun_boundary_id"),
        ("ix_run_records_dataset_identity", "dataset_identity"),
        ("ix_run_records_preset_id", "preset_id"),
        ("ix_run_records_benchmark_family", "benchmark_family"),
        ("ix_run_record_tags_tag", "tag"),
      ):
        table_name = "run_record_tags" if index_name == "ix_run_record_tags_tag" else "run_records"
        connection.exec_driver_sql(
          f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})"
        )

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
