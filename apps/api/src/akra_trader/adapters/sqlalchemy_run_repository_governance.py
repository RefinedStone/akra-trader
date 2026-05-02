from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403

class SqlAlchemyRunRepositoryGovernanceMixin:
  def list_provider_provenance_scheduler_stitched_report_governance_policy_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    statement = select(
      provider_provenance_scheduler_stitched_report_governance_policy_templates.c.payload
    ).order_by(
      provider_provenance_scheduler_stitched_report_governance_policy_templates.c.updated_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_policy_templates.c.policy_template_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_template_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_governance_policy_template(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_policy_templates.c.payload).where(
          provider_provenance_scheduler_stitched_report_governance_policy_templates.c.policy_template_id
          == policy_template_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_template_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_governance_policy_template_revision(
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
          provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.revision_id
        ).where(
          provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.revision_id
          == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_stitched_report_governance_policy_template_revisions).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_policy_template_revisions)
          .where(
            provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.revision_id
            == record.revision_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_policy_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    statement = select(
      provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.payload
    ).order_by(
      provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_template_revision_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_governance_policy_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(
          provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.payload
        ).where(
          provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.c.revision_id
          == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_template_revision_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_record(
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
          provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.c.audit_id
        ).where(
          provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.c.audit_id
          == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records).values(
            **row
          )
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records)
          .where(
            provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.c.audit_id
            == record.audit_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    statement = select(
      provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.c.payload
    ).order_by(
      provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_template_audit_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def save_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_catalog_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "catalog_id": record.catalog_id,
      "name": record.name,
      "default_policy_template_id": record.default_policy_template_id,
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
        select(provider_provenance_scheduler_narrative_governance_policy_catalogs.c.catalog_id).where(
          provider_provenance_scheduler_narrative_governance_policy_catalogs.c.catalog_id == record.catalog_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_narrative_governance_policy_catalogs).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_policy_catalogs)
          .where(provider_provenance_scheduler_narrative_governance_policy_catalogs.c.catalog_id == record.catalog_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_policy_catalogs(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    statement = select(provider_provenance_scheduler_narrative_governance_policy_catalogs.c.payload).order_by(
      provider_provenance_scheduler_narrative_governance_policy_catalogs.c.updated_at.desc(),
      provider_provenance_scheduler_narrative_governance_policy_catalogs.c.catalog_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_catalog_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_policy_catalogs.c.payload).where(
          provider_provenance_scheduler_narrative_governance_policy_catalogs.c.catalog_id == catalog_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_catalog_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_catalog_revision_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.revision_id).where(
          provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.revision_id
          == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_policy_catalog_revisions).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_policy_catalog_revisions)
          .where(
            provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.revision_id
            == record.revision_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_catalog_revision_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.payload).where(
          provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.c.revision_id
          == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_catalog_revision_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "audit_id": record.audit_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "actor_tab_id": record.actor_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.c.audit_id).where(
          provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.c.audit_id
          == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records).values(
            **row
          )
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records)
          .where(
            provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.c.audit_id
            == record.audit_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def save_provider_provenance_scheduler_stitched_report_governance_policy_catalog(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_catalog_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "catalog_id": record.catalog_id,
      "name": record.name,
      "default_policy_template_id": record.default_policy_template_id,
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
        select(provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.catalog_id).where(
          provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.catalog_id
          == record.catalog_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_stitched_report_governance_policy_catalogs).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_policy_catalogs)
          .where(
            provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.catalog_id
            == record.catalog_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_policy_catalogs(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.updated_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.catalog_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_catalog_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_governance_policy_catalog(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.payload).where(
          provider_provenance_scheduler_stitched_report_governance_policy_catalogs.c.catalog_id
          == catalog_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_catalog_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_catalog_revision_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.revision_id).where(
          provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.revision_id
          == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions)
          .where(
            provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.revision_id
            == record.revision_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    statement = select(
      provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.payload
    ).order_by(
      provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_catalog_revision_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.payload).where(
          provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.c.revision_id
          == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_policy_catalog_revision_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "audit_id": record.audit_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "actor_tab_id": record.actor_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.c.audit_id).where(
          provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.c.audit_id
          == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records).values(
            **row
          )
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records)
          .where(
            provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.c.audit_id
            == record.audit_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    statement = select(
      provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.c.payload
    ).order_by(
      provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "hierarchy_step_template_id": record.hierarchy_step_template_id,
      "name": record.name,
      "item_type": record.item_type,
      "origin_catalog_id": record.origin_catalog_id,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.hierarchy_step_template_id
        ).where(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.hierarchy_step_template_id
          == record.hierarchy_step_template_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_hierarchy_step_templates).values(
            **row
          )
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_hierarchy_step_templates)
          .where(
            provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.hierarchy_step_template_id
            == record.hierarchy_step_template_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.updated_at.desc(),
      provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.hierarchy_step_template_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.payload).where(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.c.hierarchy_step_template_id
          == hierarchy_step_template_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "hierarchy_step_template_id": record.hierarchy_step_template_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.revision_id
        ).where(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.revision_id
          == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions).values(
            **row
          )
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions)
          .where(
            provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.revision_id
            == record.revision_id
          )
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.payload
        ).where(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.c.revision_id
          == revision_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "audit_id": record.audit_id,
      "hierarchy_step_template_id": record.hierarchy_step_template_id,
      "action": record.action,
      "recorded_at": record.recorded_at.isoformat(),
      "actor_tab_id": record.actor_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.c.audit_id
        ).where(
          provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.c.audit_id
          == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records).values(
            **row
          )
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records)
          .where(
            provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.c.audit_id
            == record.audit_id
          )
          .values(**row)
        )
    return record
