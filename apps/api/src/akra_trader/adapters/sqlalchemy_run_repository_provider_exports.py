from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403

class SqlAlchemyRunRepositoryProviderExportsMixin:
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
