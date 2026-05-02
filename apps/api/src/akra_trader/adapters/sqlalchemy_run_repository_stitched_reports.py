from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403

class SqlAlchemyRunRepositoryStitchedReportsMixin:
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
  def save_provider_provenance_scheduler_stitched_report_view(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    payload = self._provider_provenance_scheduler_stitched_report_view_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "view_id": record.view_id,
      "name": record.name,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_views.c.view_id).where(
          provider_provenance_scheduler_stitched_report_views.c.view_id == record.view_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_stitched_report_views).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_views)
          .where(provider_provenance_scheduler_stitched_report_views.c.view_id == record.view_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_views(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_views.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_views.c.updated_at.desc(),
      provider_provenance_scheduler_stitched_report_views.c.view_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_stitched_report_view_adapter.validate_python(row["payload"])
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_view(
    self,
    view_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_stitched_report_views.c.payload).where(
          provider_provenance_scheduler_stitched_report_views.c.view_id == view_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_stitched_report_view_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord:
    payload = self._provider_provenance_scheduler_stitched_report_view_revision_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "view_id": record.view_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_view_revisions.c.revision_id).where(
          provider_provenance_scheduler_stitched_report_view_revisions.c.revision_id == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_stitched_report_view_revisions).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_view_revisions)
          .where(provider_provenance_scheduler_stitched_report_view_revisions.c.revision_id == record.revision_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_view_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRevisionRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_view_revisions.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_view_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_view_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_stitched_report_view_revision_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_stitched_report_view_revisions.c.payload).where(
          provider_provenance_scheduler_stitched_report_view_revisions.c.revision_id == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_stitched_report_view_revision_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_view_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewAuditRecord:
    payload = self._provider_provenance_scheduler_stitched_report_view_audit_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "audit_id": record.audit_id,
      "view_id": record.view_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_view_audit_records.c.audit_id).where(
          provider_provenance_scheduler_stitched_report_view_audit_records.c.audit_id == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_stitched_report_view_audit_records).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_view_audit_records)
          .where(provider_provenance_scheduler_stitched_report_view_audit_records.c.audit_id == record.audit_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_view_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_view_audit_records.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_view_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_view_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_stitched_report_view_audit_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def save_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    payload = self._provider_provenance_scheduler_stitched_report_governance_registry_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "registry_id": record.registry_id,
      "name": record.name,
      "status": record.status,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_registries.c.registry_id).where(
          provider_provenance_scheduler_stitched_report_governance_registries.c.registry_id == record.registry_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_stitched_report_governance_registries).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_registries)
          .where(provider_provenance_scheduler_stitched_report_governance_registries.c.registry_id == record.registry_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_registries(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_governance_registries.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_governance_registries.c.updated_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_registries.c.registry_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_stitched_report_governance_registry_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_registries.c.payload).where(
          provider_provenance_scheduler_stitched_report_governance_registries.c.registry_id == registry_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_stitched_report_governance_registry_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord:
    payload = self._provider_provenance_scheduler_stitched_report_governance_registry_audit_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "audit_id": record.audit_id,
      "registry_id": record.registry_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_registry_audit_records.c.audit_id).where(
          provider_provenance_scheduler_stitched_report_governance_registry_audit_records.c.audit_id == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_stitched_report_governance_registry_audit_records).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_registry_audit_records)
          .where(
            provider_provenance_scheduler_stitched_report_governance_registry_audit_records.c.audit_id == record.audit_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_registry_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_governance_registry_audit_records.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_governance_registry_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_registry_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_stitched_report_governance_registry_audit_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def save_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord:
    payload = self._provider_provenance_scheduler_stitched_report_governance_registry_revision_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "registry_id": record.registry_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.revision_id).where(
          provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.revision_id == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_stitched_report_governance_registry_revisions).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_registry_revisions)
          .where(provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.revision_id == record.revision_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_registry_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_stitched_report_governance_registry_revision_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.payload).where(
          provider_provenance_scheduler_stitched_report_governance_registry_revisions.c.revision_id == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_stitched_report_governance_registry_revision_adapter.validate_python(
      row["payload"]
    )
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
