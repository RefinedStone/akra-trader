from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403

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
