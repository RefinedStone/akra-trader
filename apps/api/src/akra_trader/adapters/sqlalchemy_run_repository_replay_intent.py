from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403

class SqlAlchemyRunRepositoryReplayIntentMixin:
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
