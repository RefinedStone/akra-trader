from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403

class SqlAlchemyRunRepositoryNarrativeTemplatesMixin:
  def save_provider_provenance_scheduler_narrative_template_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord:
    payload = self._provider_provenance_scheduler_narrative_template_revision_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "template_id": record.template_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_narrative_template_revisions.c.revision_id).where(
          provider_provenance_scheduler_narrative_template_revisions.c.revision_id == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_narrative_template_revisions).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_template_revisions)
          .where(provider_provenance_scheduler_narrative_template_revisions.c.revision_id == record.revision_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord, ...]:
    statement = select(provider_provenance_scheduler_narrative_template_revisions.c.payload).order_by(
      provider_provenance_scheduler_narrative_template_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_template_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_template_revision_adapter.validate_python(row["payload"])
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_template_revisions.c.payload).where(
          provider_provenance_scheduler_narrative_template_revisions.c.revision_id == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_template_revision_adapter.validate_python(
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
  def save_provider_provenance_scheduler_narrative_registry_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord:
    payload = self._provider_provenance_scheduler_narrative_registry_revision_adapter.dump_python(
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
        select(provider_provenance_scheduler_narrative_registry_revisions.c.revision_id).where(
          provider_provenance_scheduler_narrative_registry_revisions.c.revision_id == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_narrative_registry_revisions).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_registry_revisions)
          .where(provider_provenance_scheduler_narrative_registry_revisions.c.revision_id == record.revision_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_registry_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord, ...]:
    statement = select(provider_provenance_scheduler_narrative_registry_revisions.c.payload).order_by(
      provider_provenance_scheduler_narrative_registry_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_registry_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_registry_revision_adapter.validate_python(row["payload"])
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_registry_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_registry_revisions.c.payload).where(
          provider_provenance_scheduler_narrative_registry_revisions.c.revision_id == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_registry_revision_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_template_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "policy_template_id": record.policy_template_id,
      "name": record.name,
      "item_type_scope": record.item_type_scope,
      "action_scope": record.action_scope,
      "approval_lane": record.approval_lane,
      "approval_priority": record.approval_priority,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_policy_templates.c.policy_template_id).where(
          provider_provenance_scheduler_narrative_governance_policy_templates.c.policy_template_id
          == record.policy_template_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_policy_templates).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_policy_templates)
          .where(
            provider_provenance_scheduler_narrative_governance_policy_templates.c.policy_template_id
            == record.policy_template_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_policy_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_policy_templates.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_policy_templates.c.updated_at.desc(),
      provider_provenance_scheduler_narrative_governance_policy_templates.c.policy_template_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_template_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_policy_templates.c.payload).where(
          provider_provenance_scheduler_narrative_governance_policy_templates.c.policy_template_id
          == policy_template_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_template_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_template_revision_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "policy_template_id": record.policy_template_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(
          provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.revision_id
        ).where(
          provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.revision_id
          == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_policy_template_revisions).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_policy_template_revisions)
          .where(
            provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.revision_id
            == record.revision_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_policy_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_template_revision_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(
          provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.payload
        ).where(
          provider_provenance_scheduler_narrative_governance_policy_template_revisions.c.revision_id
          == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_template_revision_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_template_audit_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "audit_id": record.audit_id,
      "policy_template_id": record.policy_template_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "actor_tab_id": record.actor_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(
          provider_provenance_scheduler_narrative_governance_policy_template_audit_records.c.audit_id
        ).where(
          provider_provenance_scheduler_narrative_governance_policy_template_audit_records.c.audit_id
          == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_policy_template_audit_records).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_policy_template_audit_records)
          .where(
            provider_provenance_scheduler_narrative_governance_policy_template_audit_records.c.audit_id
            == record.audit_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_policy_template_audit_records.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_policy_template_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_governance_policy_template_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_template_audit_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def save_provider_provenance_scheduler_stitched_report_governance_policy_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_template_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "policy_template_id": record.policy_template_id,
      "name": record.name,
      "item_type_scope": record.item_type_scope,
      "action_scope": record.action_scope,
      "approval_lane": record.approval_lane,
      "approval_priority": record.approval_priority,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_policy_templates.c.policy_template_id).where(
          provider_provenance_scheduler_stitched_report_governance_policy_templates.c.policy_template_id
          == record.policy_template_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_stitched_report_governance_policy_templates).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_policy_templates)
          .where(
            provider_provenance_scheduler_stitched_report_governance_policy_templates.c.policy_template_id
            == record.policy_template_id
          )
          .values(**row)
        )
    return record
