from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403
from akra_trader.adapters.sqlalchemy_schema import _COMPACT_SQL_TABLE_NAMES
from akra_trader.adapters.sqlalchemy_schema import _build_engine
from akra_trader.adapters.sqlalchemy_schema import _quote_identifier

class SqlAlchemyRunRepositoryCoreMixin:
  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = _build_engine(database_url)
    self._ensure_schema(prepare_only=True)
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

  def _ensure_schema(self, *, prepare_only: bool = False) -> None:
    with self._engine.begin() as connection:
      self._best_effort_migrate_compact_identifiers(connection)
      inspector = inspect(connection)
      existing_tables = set(inspector.get_table_names())
      if run_records.name in existing_tables:
        existing_columns = {
          column["name"]
          for column in inspector.get_columns(run_records.name)
        }
        missing_columns = {
          "strategy_id": "TEXT",
          "strategy_version": "TEXT",
          "rerun_boundary_id": "TEXT",
          "dataset_identity": "TEXT",
          "preset_id": "TEXT",
          "benchmark_family": "TEXT",
        }
        for column_name, column_type in missing_columns.items():
          if column_name in existing_columns:
            continue
          connection.exec_driver_sql(
            f"ALTER TABLE {_quote_identifier(run_records.name)} "
            f"ADD COLUMN {_quote_identifier(column_name)} {column_type}"
          )
      if prepare_only:
        return
      inspector = inspect(connection)
      existing_tables = set(inspector.get_table_names())
      for table in metadata.sorted_tables:
        if table.name not in existing_tables:
          continue
        existing_indexes = {
          index["name"]
          for index in inspector.get_indexes(table.name)
        }
        for index in table.indexes:
          if not index.name or index.name in existing_indexes:
            continue
          column_names = [column.name for column in index.columns]
          if not column_names:
            continue
          quoted_columns = ", ".join(_quote_identifier(column_name) for column_name in column_names)
          connection.exec_driver_sql(
            f"CREATE INDEX IF NOT EXISTS {_quote_identifier(index.name)} "
            f"ON {_quote_identifier(table.name)} ({quoted_columns})"
          )

  def _best_effort_migrate_compact_identifiers(self, connection) -> None:
    if connection.dialect.name != "sqlite":
      return
    inspector = inspect(connection)
    existing_tables = set(inspector.get_table_names())
    for legacy_table_name, compact_table_name in _COMPACT_SQL_TABLE_NAMES.items():
      if legacy_table_name not in existing_tables:
        continue
      if compact_table_name in existing_tables:
        legacy_columns = [
          column["name"]
          for column in inspect(connection).get_columns(legacy_table_name)
        ]
        compact_columns = {
          column["name"]
          for column in inspect(connection).get_columns(compact_table_name)
        }
        shared_columns = [
          column_name
          for column_name in legacy_columns
          if column_name in compact_columns
        ]
        if shared_columns:
          quoted_columns = ", ".join(_quote_identifier(column_name) for column_name in shared_columns)
          connection.exec_driver_sql(
            f"INSERT OR IGNORE INTO {_quote_identifier(compact_table_name)} ({quoted_columns}) "
            f"SELECT {quoted_columns} FROM {_quote_identifier(legacy_table_name)}"
          )
        connection.exec_driver_sql(f"DROP TABLE {_quote_identifier(legacy_table_name)}")
      else:
        connection.exec_driver_sql(
          f"ALTER TABLE {_quote_identifier(legacy_table_name)} "
          f"RENAME TO {_quote_identifier(compact_table_name)}"
        )
      existing_tables.discard(legacy_table_name)
      existing_tables.add(compact_table_name)
    existing_indexes = {
      row[0]
      for row in connection.exec_driver_sql(
        "SELECT name FROM sqlite_master WHERE type = 'index' AND name IS NOT NULL"
      ).fetchall()
      if row[0]
    }
    for legacy_table_name, compact_table_name in _COMPACT_SQL_TABLE_NAMES.items():
      compact_table = metadata.tables.get(compact_table_name)
      if compact_table is None:
        continue
      for index in compact_table.indexes:
        legacy_column_names = [column.name for column in index.columns]
        if not legacy_column_names:
          continue
        legacy_index_name = f"ix_{legacy_table_name}_{'_'.join(legacy_column_names)}"
        if legacy_index_name in existing_indexes:
          connection.exec_driver_sql(
            f"DROP INDEX IF EXISTS {_quote_identifier(legacy_index_name)}"
          )
