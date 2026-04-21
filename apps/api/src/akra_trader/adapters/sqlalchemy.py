from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
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

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import ReplayIntentAliasAuditRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportArtifactRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportJobAuditRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportJobRecord
from akra_trader.domain.models import ReplayIntentAliasRecord
from akra_trader.domain.models import ProviderProvenanceExportArtifactRecord
from akra_trader.domain.models import ProviderProvenanceAnalyticsPresetRecord
from akra_trader.domain.models import ProviderProvenanceDashboardViewRecord
from akra_trader.domain.models import ProviderProvenanceExportJobAuditRecord
from akra_trader.domain.models import ProviderProvenanceExportJobRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerHealthRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeRegistryRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeTemplateRecord
from akra_trader.domain.models import ProviderProvenanceScheduledReportAuditRecord
from akra_trader.domain.models import ProviderProvenanceScheduledReportRecord
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.ports import ExperimentPresetCatalogPort
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
experiment_presets = Table(
  "experiment_presets",
  metadata,
  Column("preset_id", String, primary_key=True),
  Column("strategy_id", String, nullable=True, index=True),
  Column("timeframe", String, nullable=True, index=True),
  Column("lifecycle_stage", String, nullable=False, index=True, server_default="draft"),
  Column("updated_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_records = Table(
  "replay_intent_alias_records",
  metadata,
  Column("alias_id", String, primary_key=True),
  Column("template_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("revoked_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_records = Table(
  "replay_intent_alias_audit_records",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("alias_id", String, nullable=False, index=True),
  Column("template_key", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_export_jobs = Table(
  "replay_intent_alias_audit_export_jobs",
  metadata,
  Column("job_id", String, primary_key=True),
  Column("template_key", String, nullable=True, index=True),
  Column("export_format", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("requested_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_export_artifacts = Table(
  "replay_intent_alias_audit_export_artifacts",
  metadata,
  Column("artifact_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_export_job_audit_records = Table(
  "replay_intent_alias_audit_export_job_audit_records",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_export_jobs = Table(
  "provider_provenance_export_jobs",
  metadata,
  Column("job_id", String, primary_key=True),
  Column("focus_key", String, nullable=True, index=True),
  Column("symbol", String, nullable=True, index=True),
  Column("timeframe", String, nullable=True, index=True),
  Column("market_data_provider", String, nullable=True, index=True),
  Column("export_format", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("exported_at", String, nullable=True, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("requested_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_export_artifacts = Table(
  "provider_provenance_export_artifacts",
  metadata,
  Column("artifact_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_export_job_audit_records = Table(
  "provider_provenance_export_job_audit_records",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_analytics_presets = Table(
  "provider_provenance_analytics_presets",
  metadata,
  Column("preset_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_dashboard_views = Table(
  "provider_provenance_dashboard_views",
  metadata,
  Column("view_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("preset_id", String, nullable=True, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduled_reports = Table(
  "provider_provenance_scheduled_reports",
  metadata,
  Column("report_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("cadence", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("next_run_at", String, nullable=True, index=True),
  Column("last_run_at", String, nullable=True, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_templates = Table(
  "provider_provenance_scheduler_narrative_templates",
  metadata,
  Column("template_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_registry = Table(
  "provider_provenance_scheduler_narrative_registry",
  metadata,
  Column("registry_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("template_id", String, nullable=True, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduled_report_audit_records = Table(
  "provider_provenance_scheduled_report_audit_records",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("report_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_health_records = Table(
  "provider_provenance_scheduler_health_records",
  metadata,
  Column("record_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_state = Table(
  "replay_intent_alias_state",
  metadata,
  Column("state_key", String, primary_key=True),
  Column("payload", JSON, nullable=False),
)


def _build_engine(database_url: str) -> Engine:
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


class SqlAlchemyRunRepository(RunRepositoryPort):
  _terminal_statuses = {RunStatus.COMPLETED, RunStatus.STOPPED, RunStatus.FAILED}
  _adapter = TypeAdapter(RunRecord)
  _replay_alias_adapter = TypeAdapter(ReplayIntentAliasRecord)
  _replay_alias_audit_adapter = TypeAdapter(ReplayIntentAliasAuditRecord)
  _replay_alias_audit_export_artifact_adapter = TypeAdapter(ReplayIntentAliasAuditExportArtifactRecord)
  _replay_alias_audit_export_job_adapter = TypeAdapter(ReplayIntentAliasAuditExportJobRecord)
  _replay_alias_audit_export_job_audit_adapter = TypeAdapter(ReplayIntentAliasAuditExportJobAuditRecord)
  _provider_provenance_export_artifact_adapter = TypeAdapter(ProviderProvenanceExportArtifactRecord)
  _provider_provenance_export_job_adapter = TypeAdapter(ProviderProvenanceExportJobRecord)
  _provider_provenance_export_job_audit_adapter = TypeAdapter(ProviderProvenanceExportJobAuditRecord)
  _provider_provenance_analytics_preset_adapter = TypeAdapter(ProviderProvenanceAnalyticsPresetRecord)
  _provider_provenance_dashboard_view_adapter = TypeAdapter(ProviderProvenanceDashboardViewRecord)
  _provider_provenance_scheduled_report_adapter = TypeAdapter(ProviderProvenanceScheduledReportRecord)
  _provider_provenance_scheduler_narrative_template_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeTemplateRecord
  )
  _provider_provenance_scheduler_narrative_registry_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeRegistryRecord
  )
  _provider_provenance_scheduled_report_audit_adapter = TypeAdapter(ProviderProvenanceScheduledReportAuditRecord)
  _provider_provenance_scheduler_health_record_adapter = TypeAdapter(ProviderProvenanceSchedulerHealthRecord)

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = _build_engine(database_url)
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

  def save_replay_intent_alias(self, record: ReplayIntentAliasRecord) -> ReplayIntentAliasRecord:
    payload = self._replay_alias_adapter.dump_python(record, mode="json")
    row = {
      "alias_id": record.alias_id,
      "template_key": record.template_key,
      "created_at": record.created_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "revoked_at": record.revoked_at.isoformat() if record.revoked_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(replay_intent_alias_records.c.alias_id).where(
          replay_intent_alias_records.c.alias_id == record.alias_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(replay_intent_alias_records).values(**row))
      else:
        connection.execute(
          update(replay_intent_alias_records)
          .where(replay_intent_alias_records.c.alias_id == record.alias_id)
          .values(**row)
        )
    return record

  def get_replay_intent_alias(self, alias_id: str) -> ReplayIntentAliasRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(replay_intent_alias_records.c.payload).where(
          replay_intent_alias_records.c.alias_id == alias_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._replay_alias_adapter.validate_python(row["payload"])

  def save_replay_intent_alias_audit_record(
    self,
    record: ReplayIntentAliasAuditRecord,
  ) -> ReplayIntentAliasAuditRecord:
    payload = self._replay_alias_audit_adapter.dump_python(record, mode="json")
    row = {
      "audit_id": record.audit_id,
      "alias_id": record.alias_id,
      "template_key": record.template_key,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(replay_intent_alias_audit_records.c.audit_id).where(
          replay_intent_alias_audit_records.c.audit_id == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(replay_intent_alias_audit_records).values(**row))
      else:
        connection.execute(
          update(replay_intent_alias_audit_records)
          .where(replay_intent_alias_audit_records.c.audit_id == record.audit_id)
          .values(**row)
        )
    return record

  def list_replay_intent_alias_audit_records(
    self,
    alias_id: str | None = None,
  ) -> tuple[ReplayIntentAliasAuditRecord, ...]:
    statement = select(replay_intent_alias_audit_records.c.payload)
    if alias_id is not None:
      statement = statement.where(replay_intent_alias_audit_records.c.alias_id == alias_id)
    statement = statement.order_by(
      replay_intent_alias_audit_records.c.recorded_at.desc(),
      replay_intent_alias_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._replay_alias_audit_adapter.validate_python(row["payload"])
      for row in rows
    )

  def delete_replay_intent_alias_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    if not audit_ids:
      return 0
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_records).where(
          replay_intent_alias_audit_records.c.audit_id.in_(audit_ids)
        )
      )
    return result.rowcount or 0

  def prune_replay_intent_alias_audit_records(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_records).where(
          replay_intent_alias_audit_records.c.expires_at.is_not(None),
          replay_intent_alias_audit_records.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_replay_intent_alias_audit_export_artifact(
    self,
    record: ReplayIntentAliasAuditExportArtifactRecord,
  ) -> ReplayIntentAliasAuditExportArtifactRecord:
    payload = self._replay_alias_audit_export_artifact_adapter.dump_python(record, mode="json")
    row = {
      "artifact_id": record.artifact_id,
      "job_id": record.job_id,
      "created_at": record.created_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(replay_intent_alias_audit_export_artifacts.c.artifact_id).where(
          replay_intent_alias_audit_export_artifacts.c.artifact_id == record.artifact_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(replay_intent_alias_audit_export_artifacts).values(**row))
      else:
        connection.execute(
          update(replay_intent_alias_audit_export_artifacts)
          .where(replay_intent_alias_audit_export_artifacts.c.artifact_id == record.artifact_id)
          .values(**row)
        )
    return record

  def get_replay_intent_alias_audit_export_artifact(
    self,
    artifact_id: str,
  ) -> ReplayIntentAliasAuditExportArtifactRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(replay_intent_alias_audit_export_artifacts.c.payload).where(
          replay_intent_alias_audit_export_artifacts.c.artifact_id == artifact_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._replay_alias_audit_export_artifact_adapter.validate_python(row["payload"])

  def delete_replay_intent_alias_audit_export_artifacts(self, artifact_ids: tuple[str, ...]) -> int:
    if not artifact_ids:
      return 0
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_export_artifacts).where(
          replay_intent_alias_audit_export_artifacts.c.artifact_id.in_(artifact_ids)
        )
      )
    return result.rowcount or 0

  def prune_replay_intent_alias_audit_export_artifacts(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_export_artifacts).where(
          replay_intent_alias_audit_export_artifacts.c.expires_at.is_not(None),
          replay_intent_alias_audit_export_artifacts.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_replay_intent_alias_audit_export_job(
    self,
    record: ReplayIntentAliasAuditExportJobRecord,
  ) -> ReplayIntentAliasAuditExportJobRecord:
    payload = self._replay_alias_audit_export_job_adapter.dump_python(record, mode="json")
    row = {
      "job_id": record.job_id,
      "template_key": record.template_key,
      "export_format": record.export_format,
      "status": record.status,
      "created_at": record.created_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "requested_by_tab_id": record.requested_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(replay_intent_alias_audit_export_jobs.c.job_id).where(
          replay_intent_alias_audit_export_jobs.c.job_id == record.job_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(replay_intent_alias_audit_export_jobs).values(**row))
      else:
        connection.execute(
          update(replay_intent_alias_audit_export_jobs)
          .where(replay_intent_alias_audit_export_jobs.c.job_id == record.job_id)
          .values(**row)
        )
    return record

  def get_replay_intent_alias_audit_export_job(
    self,
    job_id: str,
  ) -> ReplayIntentAliasAuditExportJobRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(replay_intent_alias_audit_export_jobs.c.payload).where(
          replay_intent_alias_audit_export_jobs.c.job_id == job_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._replay_alias_audit_export_job_adapter.validate_python(row["payload"])

  def list_replay_intent_alias_audit_export_jobs(
    self,
  ) -> tuple[ReplayIntentAliasAuditExportJobRecord, ...]:
    statement = select(replay_intent_alias_audit_export_jobs.c.payload).order_by(
      replay_intent_alias_audit_export_jobs.c.created_at.desc(),
      replay_intent_alias_audit_export_jobs.c.job_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._replay_alias_audit_export_job_adapter.validate_python(row["payload"])
      for row in rows
    )

  def prune_replay_intent_alias_audit_export_jobs(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_export_jobs).where(
          replay_intent_alias_audit_export_jobs.c.expires_at.is_not(None),
          replay_intent_alias_audit_export_jobs.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def delete_replay_intent_alias_audit_export_jobs(self, job_ids: tuple[str, ...]) -> int:
    if not job_ids:
      return 0
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_export_jobs).where(
          replay_intent_alias_audit_export_jobs.c.job_id.in_(job_ids)
        )
      )
    return result.rowcount or 0

  def save_replay_intent_alias_audit_export_job_audit_record(
    self,
    record: ReplayIntentAliasAuditExportJobAuditRecord,
  ) -> ReplayIntentAliasAuditExportJobAuditRecord:
    payload = self._replay_alias_audit_export_job_audit_adapter.dump_python(record, mode="json")
    row = {
      "audit_id": record.audit_id,
      "job_id": record.job_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(replay_intent_alias_audit_export_job_audit_records.c.audit_id).where(
          replay_intent_alias_audit_export_job_audit_records.c.audit_id == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(replay_intent_alias_audit_export_job_audit_records).values(**row))
      else:
        connection.execute(
          update(replay_intent_alias_audit_export_job_audit_records)
          .where(replay_intent_alias_audit_export_job_audit_records.c.audit_id == record.audit_id)
          .values(**row)
        )
    return record

  def list_replay_intent_alias_audit_export_job_audit_records(
    self,
    job_id: str | None = None,
  ) -> tuple[ReplayIntentAliasAuditExportJobAuditRecord, ...]:
    statement = select(replay_intent_alias_audit_export_job_audit_records.c.payload)
    if job_id is not None:
      statement = statement.where(replay_intent_alias_audit_export_job_audit_records.c.job_id == job_id)
    statement = statement.order_by(
      replay_intent_alias_audit_export_job_audit_records.c.recorded_at.desc(),
      replay_intent_alias_audit_export_job_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._replay_alias_audit_export_job_audit_adapter.validate_python(row["payload"])
      for row in rows
    )

  def delete_replay_intent_alias_audit_export_job_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    if not audit_ids:
      return 0
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_export_job_audit_records).where(
          replay_intent_alias_audit_export_job_audit_records.c.audit_id.in_(audit_ids)
        )
      )
    return result.rowcount or 0

  def prune_replay_intent_alias_audit_export_job_audit_records(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(replay_intent_alias_audit_export_job_audit_records).where(
          replay_intent_alias_audit_export_job_audit_records.c.expires_at.is_not(None),
          replay_intent_alias_audit_export_job_audit_records.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_export_artifact(
    self,
    record: ProviderProvenanceExportArtifactRecord,
  ) -> ProviderProvenanceExportArtifactRecord:
    payload = self._provider_provenance_export_artifact_adapter.dump_python(record, mode="json")
    row = {
      "artifact_id": record.artifact_id,
      "job_id": record.job_id,
      "created_at": record.created_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_export_artifacts.c.artifact_id).where(
          provider_provenance_export_artifacts.c.artifact_id == record.artifact_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_export_artifacts).values(**row))
      else:
        connection.execute(
          update(provider_provenance_export_artifacts)
          .where(provider_provenance_export_artifacts.c.artifact_id == record.artifact_id)
          .values(**row)
        )
    return record

  def get_provider_provenance_export_artifact(
    self,
    artifact_id: str,
  ) -> ProviderProvenanceExportArtifactRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_export_artifacts.c.payload).where(
          provider_provenance_export_artifacts.c.artifact_id == artifact_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_export_artifact_adapter.validate_python(row["payload"])

  def delete_provider_provenance_export_artifacts(self, artifact_ids: tuple[str, ...]) -> int:
    if not artifact_ids:
      return 0
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_export_artifacts).where(
          provider_provenance_export_artifacts.c.artifact_id.in_(artifact_ids)
        )
      )
    return result.rowcount or 0

  def prune_provider_provenance_export_artifacts(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_export_artifacts).where(
          provider_provenance_export_artifacts.c.expires_at.is_not(None),
          provider_provenance_export_artifacts.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_export_job(
    self,
    record: ProviderProvenanceExportJobRecord,
  ) -> ProviderProvenanceExportJobRecord:
    payload = self._provider_provenance_export_job_adapter.dump_python(record, mode="json")
    row = {
      "job_id": record.job_id,
      "focus_key": record.focus_key,
      "symbol": record.symbol,
      "timeframe": record.timeframe,
      "market_data_provider": record.market_data_provider,
      "export_format": record.export_format,
      "status": record.status,
      "created_at": record.created_at.isoformat(),
      "exported_at": record.exported_at.isoformat() if record.exported_at is not None else None,
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "requested_by_tab_id": record.requested_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_export_jobs.c.job_id).where(
          provider_provenance_export_jobs.c.job_id == record.job_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_export_jobs).values(**row))
      else:
        connection.execute(
          update(provider_provenance_export_jobs)
          .where(provider_provenance_export_jobs.c.job_id == record.job_id)
          .values(**row)
        )
    return record

  def get_provider_provenance_export_job(
    self,
    job_id: str,
  ) -> ProviderProvenanceExportJobRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_export_jobs.c.payload).where(
          provider_provenance_export_jobs.c.job_id == job_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_export_job_adapter.validate_python(row["payload"])

  def list_provider_provenance_export_jobs(
    self,
  ) -> tuple[ProviderProvenanceExportJobRecord, ...]:
    statement = select(provider_provenance_export_jobs.c.payload).order_by(
      provider_provenance_export_jobs.c.exported_at.desc(),
      provider_provenance_export_jobs.c.created_at.desc(),
      provider_provenance_export_jobs.c.job_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_export_job_adapter.validate_python(row["payload"])
      for row in rows
    )

  def prune_provider_provenance_export_jobs(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_export_jobs).where(
          provider_provenance_export_jobs.c.expires_at.is_not(None),
          provider_provenance_export_jobs.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def delete_provider_provenance_export_jobs(self, job_ids: tuple[str, ...]) -> int:
    if not job_ids:
      return 0
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_export_jobs).where(
          provider_provenance_export_jobs.c.job_id.in_(job_ids)
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_export_job_audit_record(
    self,
    record: ProviderProvenanceExportJobAuditRecord,
  ) -> ProviderProvenanceExportJobAuditRecord:
    payload = self._provider_provenance_export_job_audit_adapter.dump_python(record, mode="json")
    row = {
      "audit_id": record.audit_id,
      "job_id": record.job_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_export_job_audit_records.c.audit_id).where(
          provider_provenance_export_job_audit_records.c.audit_id == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_export_job_audit_records).values(**row))
      else:
        connection.execute(
          update(provider_provenance_export_job_audit_records)
          .where(provider_provenance_export_job_audit_records.c.audit_id == record.audit_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_export_job_audit_records(
    self,
    job_id: str | None = None,
  ) -> tuple[ProviderProvenanceExportJobAuditRecord, ...]:
    statement = select(provider_provenance_export_job_audit_records.c.payload)
    if job_id is not None:
      statement = statement.where(provider_provenance_export_job_audit_records.c.job_id == job_id)
    statement = statement.order_by(
      provider_provenance_export_job_audit_records.c.recorded_at.desc(),
      provider_provenance_export_job_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_export_job_audit_adapter.validate_python(row["payload"])
      for row in rows
    )

  def delete_provider_provenance_export_job_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    if not audit_ids:
      return 0
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_export_job_audit_records).where(
          provider_provenance_export_job_audit_records.c.audit_id.in_(audit_ids)
        )
      )
    return result.rowcount or 0

  def prune_provider_provenance_export_job_audit_records(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_export_job_audit_records).where(
          provider_provenance_export_job_audit_records.c.expires_at.is_not(None),
          provider_provenance_export_job_audit_records.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_analytics_preset(
    self,
    record: ProviderProvenanceAnalyticsPresetRecord,
  ) -> ProviderProvenanceAnalyticsPresetRecord:
    payload = self._provider_provenance_analytics_preset_adapter.dump_python(record, mode="json")
    row = {
      "preset_id": record.preset_id,
      "name": record.name,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_analytics_presets.c.preset_id).where(
          provider_provenance_analytics_presets.c.preset_id == record.preset_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_analytics_presets).values(**row))
      else:
        connection.execute(
          update(provider_provenance_analytics_presets)
          .where(provider_provenance_analytics_presets.c.preset_id == record.preset_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_analytics_presets(
    self,
  ) -> tuple[ProviderProvenanceAnalyticsPresetRecord, ...]:
    statement = select(provider_provenance_analytics_presets.c.payload).order_by(
      provider_provenance_analytics_presets.c.updated_at.desc(),
      provider_provenance_analytics_presets.c.preset_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_analytics_preset_adapter.validate_python(row["payload"])
      for row in rows
    )

  def get_provider_provenance_analytics_preset(
    self,
    preset_id: str,
  ) -> ProviderProvenanceAnalyticsPresetRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_analytics_presets.c.payload).where(
          provider_provenance_analytics_presets.c.preset_id == preset_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_analytics_preset_adapter.validate_python(row["payload"])

  def save_provider_provenance_dashboard_view(
    self,
    record: ProviderProvenanceDashboardViewRecord,
  ) -> ProviderProvenanceDashboardViewRecord:
    payload = self._provider_provenance_dashboard_view_adapter.dump_python(record, mode="json")
    row = {
      "view_id": record.view_id,
      "name": record.name,
      "preset_id": record.preset_id,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_dashboard_views.c.view_id).where(
          provider_provenance_dashboard_views.c.view_id == record.view_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_dashboard_views).values(**row))
      else:
        connection.execute(
          update(provider_provenance_dashboard_views)
          .where(provider_provenance_dashboard_views.c.view_id == record.view_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_dashboard_views(
    self,
  ) -> tuple[ProviderProvenanceDashboardViewRecord, ...]:
    statement = select(provider_provenance_dashboard_views.c.payload).order_by(
      provider_provenance_dashboard_views.c.updated_at.desc(),
      provider_provenance_dashboard_views.c.view_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_dashboard_view_adapter.validate_python(row["payload"])
      for row in rows
    )

  def get_provider_provenance_dashboard_view(
    self,
    view_id: str,
  ) -> ProviderProvenanceDashboardViewRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_dashboard_views.c.payload).where(
          provider_provenance_dashboard_views.c.view_id == view_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_dashboard_view_adapter.validate_python(row["payload"])

  def save_provider_provenance_scheduled_report(
    self,
    record: ProviderProvenanceScheduledReportRecord,
  ) -> ProviderProvenanceScheduledReportRecord:
    payload = self._provider_provenance_scheduled_report_adapter.dump_python(record, mode="json")
    row = {
      "report_id": record.report_id,
      "name": record.name,
      "status": record.status,
      "cadence": record.cadence,
      "updated_at": record.updated_at.isoformat(),
      "next_run_at": record.next_run_at.isoformat() if record.next_run_at is not None else None,
      "last_run_at": record.last_run_at.isoformat() if record.last_run_at is not None else None,
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduled_reports.c.report_id).where(
          provider_provenance_scheduled_reports.c.report_id == record.report_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduled_reports).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduled_reports)
          .where(provider_provenance_scheduled_reports.c.report_id == record.report_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduled_reports(
    self,
  ) -> tuple[ProviderProvenanceScheduledReportRecord, ...]:
    statement = select(provider_provenance_scheduled_reports.c.payload).order_by(
      provider_provenance_scheduled_reports.c.updated_at.desc(),
      provider_provenance_scheduled_reports.c.report_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduled_report_adapter.validate_python(row["payload"])
      for row in rows
    )

  def get_provider_provenance_scheduled_report(
    self,
    report_id: str,
  ) -> ProviderProvenanceScheduledReportRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduled_reports.c.payload).where(
          provider_provenance_scheduled_reports.c.report_id == report_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduled_report_adapter.validate_python(row["payload"])

  def save_provider_provenance_scheduler_narrative_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    payload = self._provider_provenance_scheduler_narrative_template_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "template_id": record.template_id,
      "name": record.name,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_narrative_templates.c.template_id).where(
          provider_provenance_scheduler_narrative_templates.c.template_id == record.template_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_narrative_templates).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_templates)
          .where(provider_provenance_scheduler_narrative_templates.c.template_id == record.template_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_narrative_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRecord, ...]:
    statement = select(provider_provenance_scheduler_narrative_templates.c.payload).order_by(
      provider_provenance_scheduler_narrative_templates.c.updated_at.desc(),
      provider_provenance_scheduler_narrative_templates.c.template_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_template_adapter.validate_python(row["payload"])
      for row in rows
    )

  def get_provider_provenance_scheduler_narrative_template(
    self,
    template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_templates.c.payload).where(
          provider_provenance_scheduler_narrative_templates.c.template_id == template_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_template_adapter.validate_python(
      row["payload"]
    )

  def save_provider_provenance_scheduler_narrative_registry_entry(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    payload = self._provider_provenance_scheduler_narrative_registry_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "registry_id": record.registry_id,
      "name": record.name,
      "template_id": record.template_id,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_narrative_registry.c.registry_id).where(
          provider_provenance_scheduler_narrative_registry.c.registry_id == record.registry_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_narrative_registry).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_registry)
          .where(provider_provenance_scheduler_narrative_registry.c.registry_id == record.registry_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_narrative_registry_entries(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRecord, ...]:
    statement = select(provider_provenance_scheduler_narrative_registry.c.payload).order_by(
      provider_provenance_scheduler_narrative_registry.c.updated_at.desc(),
      provider_provenance_scheduler_narrative_registry.c.registry_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_registry_adapter.validate_python(row["payload"])
      for row in rows
    )

  def get_provider_provenance_scheduler_narrative_registry_entry(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_registry.c.payload).where(
          provider_provenance_scheduler_narrative_registry.c.registry_id == registry_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_registry_adapter.validate_python(
      row["payload"]
    )

  def save_provider_provenance_scheduled_report_audit_record(
    self,
    record: ProviderProvenanceScheduledReportAuditRecord,
  ) -> ProviderProvenanceScheduledReportAuditRecord:
    payload = self._provider_provenance_scheduled_report_audit_adapter.dump_python(record, mode="json")
    row = {
      "audit_id": record.audit_id,
      "report_id": record.report_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduled_report_audit_records.c.audit_id).where(
          provider_provenance_scheduled_report_audit_records.c.audit_id == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduled_report_audit_records).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduled_report_audit_records)
          .where(provider_provenance_scheduled_report_audit_records.c.audit_id == record.audit_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduled_report_audit_records(
    self,
    report_id: str | None = None,
  ) -> tuple[ProviderProvenanceScheduledReportAuditRecord, ...]:
    statement = select(provider_provenance_scheduled_report_audit_records.c.payload)
    if report_id is not None:
      statement = statement.where(
        provider_provenance_scheduled_report_audit_records.c.report_id == report_id
      )
    statement = statement.order_by(
      provider_provenance_scheduled_report_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduled_report_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduled_report_audit_adapter.validate_python(row["payload"])
      for row in rows
    )

  def prune_provider_provenance_scheduled_report_audit_records(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_scheduled_report_audit_records).where(
          provider_provenance_scheduled_report_audit_records.c.expires_at.is_not(None),
          provider_provenance_scheduled_report_audit_records.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_scheduler_health_record(
    self,
    record: ProviderProvenanceSchedulerHealthRecord,
  ) -> ProviderProvenanceSchedulerHealthRecord:
    payload = self._provider_provenance_scheduler_health_record_adapter.dump_python(record, mode="json")
    row = {
      "record_id": record.record_id,
      "scheduler_key": record.scheduler_key,
      "status": record.status,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_health_records.c.record_id).where(
          provider_provenance_scheduler_health_records.c.record_id == record.record_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_health_records).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_health_records)
          .where(provider_provenance_scheduler_health_records.c.record_id == record.record_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_health_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerHealthRecord, ...]:
    statement = select(provider_provenance_scheduler_health_records.c.payload).order_by(
      provider_provenance_scheduler_health_records.c.recorded_at.desc(),
      provider_provenance_scheduler_health_records.c.record_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_health_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def prune_provider_provenance_scheduler_health_records(self, current_time: datetime) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_scheduler_health_records).where(
          provider_provenance_scheduler_health_records.c.expires_at.is_not(None),
          provider_provenance_scheduler_health_records.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def load_replay_intent_alias_signing_secret(self) -> str | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(replay_intent_alias_state.c.payload).where(
          replay_intent_alias_state.c.state_key == "signing_secret"
        )
      ).mappings().first()
    if row is None or not isinstance(row["payload"], dict):
      return None
    secret = row["payload"].get("secret")
    return secret if isinstance(secret, str) and secret else None

  def save_replay_intent_alias_signing_secret(self, secret: str) -> str:
    row = {
      "state_key": "signing_secret",
      "payload": {"secret": secret},
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(replay_intent_alias_state.c.state_key).where(
          replay_intent_alias_state.c.state_key == "signing_secret"
        )
      ).first()
      if existing is None:
        connection.execute(insert(replay_intent_alias_state).values(**row))
      else:
        connection.execute(
          update(replay_intent_alias_state)
          .where(replay_intent_alias_state.c.state_key == "signing_secret")
          .values(**row)
        )
    return secret

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
        ("ix_replay_intent_alias_records_template_key", "template_key"),
        ("ix_replay_intent_alias_records_created_at", "created_at"),
        ("ix_replay_intent_alias_records_expires_at", "expires_at"),
        ("ix_replay_intent_alias_records_revoked_at", "revoked_at"),
        ("ix_replay_intent_alias_audit_records_alias_id", "alias_id"),
        ("ix_replay_intent_alias_audit_records_template_key", "template_key"),
        ("ix_replay_intent_alias_audit_records_action", "action"),
        ("ix_replay_intent_alias_audit_records_recorded_at", "recorded_at"),
        ("ix_replay_intent_alias_audit_records_expires_at", "expires_at"),
        ("ix_replay_intent_alias_audit_export_artifacts_job_id", "job_id"),
        ("ix_replay_intent_alias_audit_export_artifacts_created_at", "created_at"),
        ("ix_replay_intent_alias_audit_export_artifacts_expires_at", "expires_at"),
        ("ix_replay_intent_alias_audit_export_jobs_template_key", "template_key"),
        ("ix_replay_intent_alias_audit_export_jobs_export_format", "export_format"),
        ("ix_replay_intent_alias_audit_export_jobs_status", "status"),
        ("ix_replay_intent_alias_audit_export_jobs_created_at", "created_at"),
        ("ix_replay_intent_alias_audit_export_jobs_expires_at", "expires_at"),
        ("ix_replay_intent_alias_audit_export_jobs_requested_by_tab_id", "requested_by_tab_id"),
        ("ix_replay_intent_alias_audit_export_job_audit_records_job_id", "job_id"),
        ("ix_replay_intent_alias_audit_export_job_audit_records_action", "action"),
        ("ix_replay_intent_alias_audit_export_job_audit_records_recorded_at", "recorded_at"),
        ("ix_replay_intent_alias_audit_export_job_audit_records_expires_at", "expires_at"),
        ("ix_provider_provenance_analytics_presets_name", "name"),
        ("ix_provider_provenance_analytics_presets_updated_at", "updated_at"),
        ("ix_provider_provenance_analytics_presets_created_by_tab_id", "created_by_tab_id"),
        ("ix_provider_provenance_dashboard_views_name", "name"),
        ("ix_provider_provenance_dashboard_views_preset_id", "preset_id"),
        ("ix_provider_provenance_dashboard_views_updated_at", "updated_at"),
        ("ix_provider_provenance_dashboard_views_created_by_tab_id", "created_by_tab_id"),
        ("ix_provider_provenance_scheduled_reports_name", "name"),
        ("ix_provider_provenance_scheduled_reports_status", "status"),
        ("ix_provider_provenance_scheduled_reports_cadence", "cadence"),
        ("ix_provider_provenance_scheduled_reports_updated_at", "updated_at"),
        ("ix_provider_provenance_scheduled_reports_next_run_at", "next_run_at"),
        ("ix_provider_provenance_scheduled_reports_last_run_at", "last_run_at"),
        ("ix_provider_provenance_scheduled_reports_created_by_tab_id", "created_by_tab_id"),
        ("ix_provider_provenance_scheduler_narrative_templates_name", "name"),
        ("ix_provider_provenance_scheduler_narrative_templates_updated_at", "updated_at"),
        ("ix_provider_provenance_scheduler_narrative_templates_created_by_tab_id", "created_by_tab_id"),
        ("ix_provider_provenance_scheduler_narrative_registry_name", "name"),
        ("ix_provider_provenance_scheduler_narrative_registry_template_id", "template_id"),
        ("ix_provider_provenance_scheduler_narrative_registry_updated_at", "updated_at"),
        ("ix_provider_provenance_scheduler_narrative_registry_created_by_tab_id", "created_by_tab_id"),
        ("ix_provider_provenance_scheduled_report_audit_records_report_id", "report_id"),
        ("ix_provider_provenance_scheduled_report_audit_records_action", "action"),
        ("ix_provider_provenance_scheduled_report_audit_records_recorded_at", "recorded_at"),
        ("ix_provider_provenance_scheduled_report_audit_records_expires_at", "expires_at"),
        ("ix_provider_provenance_scheduler_health_records_scheduler_key", "scheduler_key"),
        ("ix_provider_provenance_scheduler_health_records_status", "status"),
        ("ix_provider_provenance_scheduler_health_records_recorded_at", "recorded_at"),
        ("ix_provider_provenance_scheduler_health_records_expires_at", "expires_at"),
      ):
        table_name = (
          "provider_provenance_scheduler_health_records"
          if index_name.startswith("ix_provider_provenance_scheduler_health_records_")
          else
          "provider_provenance_scheduled_report_audit_records"
          if index_name.startswith("ix_provider_provenance_scheduled_report_audit_records_")
          else "provider_provenance_scheduled_reports"
          if index_name.startswith("ix_provider_provenance_scheduled_reports_")
          else "provider_provenance_dashboard_views"
          if index_name.startswith("ix_provider_provenance_dashboard_views_")
          else "provider_provenance_analytics_presets"
          if index_name.startswith("ix_provider_provenance_analytics_presets_")
          else
          "run_record_tags"
          if index_name == "ix_run_record_tags_tag"
          else "replay_intent_alias_audit_export_artifacts"
            if index_name.startswith("ix_replay_intent_alias_audit_export_artifacts_")
          else "replay_intent_alias_audit_export_job_audit_records"
            if index_name.startswith("ix_replay_intent_alias_audit_export_job_audit_records_")
            else "replay_intent_alias_audit_export_jobs"
            if index_name.startswith("ix_replay_intent_alias_audit_export_jobs_")
          else "replay_intent_alias_audit_records"
            if index_name.startswith("ix_replay_intent_alias_audit_records_")
            else "replay_intent_alias_records"
            if index_name.startswith("ix_replay_intent_alias_records_")
            else "run_records"
        )
        connection.exec_driver_sql(
          f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})"
        )


class SqlAlchemyExperimentPresetCatalog(ExperimentPresetCatalogPort):
  _adapter = TypeAdapter(ExperimentPreset)

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = _build_engine(database_url)
    metadata.create_all(self._engine)
    self._ensure_schema()
    self._backfill_legacy_presets()
    self._upgrade_existing_presets()

  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    statement = select(experiment_presets.c.payload).order_by(
      experiment_presets.c.updated_at.desc(),
      experiment_presets.c.preset_id.asc(),
    )
    if strategy_id is not None:
      statement = statement.where(experiment_presets.c.strategy_id == strategy_id)
    if timeframe is not None:
      statement = statement.where(experiment_presets.c.timeframe == timeframe)
    if lifecycle_stage is not None:
      statement = statement.where(experiment_presets.c.lifecycle_stage == lifecycle_stage)
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return [self._adapter.validate_python(row["payload"]) for row in rows]

  def get_preset(self, preset_id: str) -> ExperimentPreset | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(experiment_presets.c.payload).where(experiment_presets.c.preset_id == preset_id)
      ).mappings().first()
    if row is None:
      return None
    return self._adapter.validate_python(row["payload"])

  def save_preset(self, preset: ExperimentPreset) -> ExperimentPreset:
    payload = self._adapter.dump_python(preset, mode="json")
    row = {
      "preset_id": preset.preset_id,
      "strategy_id": preset.strategy_id,
      "timeframe": preset.timeframe,
      "lifecycle_stage": preset.lifecycle.stage,
      "updated_at": preset.updated_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(experiment_presets.c.preset_id).where(experiment_presets.c.preset_id == preset.preset_id)
      ).first()
      if existing is None:
        connection.execute(insert(experiment_presets).values(**row))
      else:
        connection.execute(
          update(experiment_presets)
          .where(experiment_presets.c.preset_id == preset.preset_id)
          .values(**row)
        )
    return preset

  def _ensure_schema(self) -> None:
    with self._engine.begin() as connection:
      existing_columns = {
        column["name"]
        for column in inspect(self._engine).get_columns("experiment_presets")
      }
      if "lifecycle_stage" not in existing_columns:
        connection.exec_driver_sql(
          "ALTER TABLE experiment_presets ADD COLUMN lifecycle_stage TEXT NOT NULL DEFAULT 'draft'"
        )
      for index_name, column_name in (
        ("ix_experiment_presets_strategy_id", "strategy_id"),
        ("ix_experiment_presets_timeframe", "timeframe"),
        ("ix_experiment_presets_lifecycle_stage", "lifecycle_stage"),
        ("ix_experiment_presets_updated_at", "updated_at"),
      ):
        connection.exec_driver_sql(
          f"CREATE INDEX IF NOT EXISTS {index_name} ON experiment_presets ({column_name})"
        )

  def _backfill_legacy_presets(self) -> None:
    with self._engine.begin() as connection:
      existing_ids = {
        row["preset_id"]
        for row in connection.execute(select(experiment_presets.c.preset_id)).mappings().all()
      }
      rows = connection.execute(
        select(
          run_records.c.preset_id,
          run_records.c.strategy_id,
          run_records.c.benchmark_family,
          run_records.c.payload,
        )
        .where(run_records.c.preset_id.is_not(None))
        .order_by(run_records.c.started_at.desc(), run_records.c.run_id.desc())
      ).mappings().all()
      for row in rows:
        preset_id = row["preset_id"]
        if preset_id in existing_ids:
          continue
        payload = row["payload"] or {}
        config_payload = payload.get("config") or {}
        provenance_payload = payload.get("provenance") or {}
        experiment_payload = provenance_payload.get("experiment") or {}
        preset = ExperimentPreset(
          preset_id=preset_id,
          name=preset_id,
          description="Migrated from legacy run metadata.",
          strategy_id=row["strategy_id"] or config_payload.get("strategy_id"),
          timeframe=config_payload.get("timeframe"),
          benchmark_family=row["benchmark_family"] or experiment_payload.get("benchmark_family"),
          tags=tuple(
            tag
            for tag in experiment_payload.get("tags", ())
            if isinstance(tag, str) and tag
          ),
          parameters={},
          lifecycle=ExperimentPreset.Lifecycle(
            stage="draft",
            updated_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
            updated_by="system",
            last_action="migrated",
            history=(
              ExperimentPreset.LifecycleEvent(
                action="migrated",
                actor="system",
                reason="legacy_run_metadata_migration",
                occurred_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
                from_stage=None,
                to_stage="draft",
              ),
            ),
          ),
          revisions=(
            _build_preset_revision(
              preset_id=preset_id,
              revision_number=1,
              action="migrated",
              actor="system",
              reason="legacy_run_metadata_migration",
              occurred_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
              name=preset_id,
              description="Migrated from legacy run metadata.",
              strategy_id=row["strategy_id"] or config_payload.get("strategy_id"),
              timeframe=config_payload.get("timeframe"),
              benchmark_family=row["benchmark_family"] or experiment_payload.get("benchmark_family"),
              tags=tuple(
                tag
                for tag in experiment_payload.get("tags", ())
                if isinstance(tag, str) and tag
              ),
              parameters=(
                deepcopy(config_payload.get("parameters"))
                if isinstance(config_payload.get("parameters"), dict)
                else {}
              ),
            ),
          ),
          created_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
          updated_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
        )
        connection.execute(
          insert(experiment_presets).values(
            preset_id=preset.preset_id,
            strategy_id=preset.strategy_id,
            timeframe=preset.timeframe,
            lifecycle_stage=preset.lifecycle.stage,
            updated_at=preset.updated_at.isoformat(),
            payload=self._adapter.dump_python(preset, mode="json"),
          )
        )
        existing_ids.add(preset_id)

  def _upgrade_existing_presets(self) -> None:
    with self._engine.begin() as connection:
      rows = connection.execute(
        select(
          experiment_presets.c.preset_id,
          experiment_presets.c.payload,
          experiment_presets.c.updated_at,
        )
      ).mappings().all()
      for row in rows:
        payload = row["payload"] or {}
        if "parameters" in payload and "lifecycle" in payload and "revisions" in payload:
          continue
        preset = self._adapter.validate_python(payload)
        updated_at = _coerce_datetime(payload.get("updated_at")) or _coerce_datetime(row["updated_at"]) or datetime.now(UTC)
        created_at = _coerce_datetime(payload.get("created_at")) or updated_at
        parameters = deepcopy(payload.get("parameters", preset.parameters))
        if "lifecycle" in payload:
          lifecycle = preset.lifecycle
        else:
          lifecycle = ExperimentPreset.Lifecycle(
            stage="draft",
            updated_at=updated_at,
            updated_by="system",
            last_action="migrated",
            history=(
              ExperimentPreset.LifecycleEvent(
                action="migrated",
                actor="system",
                reason="preset_catalog_schema_upgrade",
                occurred_at=updated_at,
                from_stage=None,
                to_stage="draft",
              ),
            ),
          )
        revisions = preset.revisions
        if not revisions:
          lifecycle_event = lifecycle.history[0] if lifecycle.history else None
          revisions = (
            _build_preset_revision(
              preset_id=preset.preset_id,
              revision_number=1,
              action=(lifecycle_event.action if lifecycle_event is not None else "migrated"),
              actor=(lifecycle_event.actor if lifecycle_event is not None else "system"),
              reason=(
                lifecycle_event.reason
                if lifecycle_event is not None
                else "preset_catalog_schema_upgrade"
              ),
              occurred_at=(
                lifecycle_event.occurred_at
                if lifecycle_event is not None
                else created_at
              ),
              name=preset.name,
              description=preset.description,
              strategy_id=preset.strategy_id,
              timeframe=preset.timeframe,
              benchmark_family=preset.benchmark_family,
              tags=preset.tags,
              parameters=parameters,
            ),
          )
        upgraded = replace(
          preset,
          parameters=parameters,
          lifecycle=lifecycle,
          revisions=revisions,
          created_at=created_at,
          updated_at=updated_at,
        )
        connection.execute(
          update(experiment_presets)
          .where(experiment_presets.c.preset_id == row["preset_id"])
          .values(
            strategy_id=upgraded.strategy_id,
            timeframe=upgraded.timeframe,
            lifecycle_stage=upgraded.lifecycle.stage,
            updated_at=upgraded.updated_at.isoformat(),
            payload=self._adapter.dump_python(upgraded, mode="json"),
          )
        )


def _coerce_datetime(value: str | None) -> datetime | None:
  if not value:
    return None
  try:
    return datetime.fromisoformat(value)
  except ValueError:
    return None


def _build_preset_revision(
  *,
  preset_id: str,
  revision_number: int,
  action: str,
  actor: str,
  reason: str,
  occurred_at: datetime,
  name: str,
  description: str,
  strategy_id: str | None,
  timeframe: str | None,
  benchmark_family: str | None,
  tags: tuple[str, ...],
  parameters: dict,
) -> ExperimentPreset.Revision:
  return ExperimentPreset.Revision(
    revision_id=f"{preset_id}:r{revision_number:04d}",
    actor=(actor or "system").strip() or "system",
    reason=(reason or action).strip() or action,
    created_at=occurred_at,
    action=action,
    name=name,
    description=description,
    strategy_id=strategy_id,
    timeframe=timeframe,
    benchmark_family=benchmark_family,
    tags=tuple(tags),
    parameters=deepcopy(parameters),
  )
