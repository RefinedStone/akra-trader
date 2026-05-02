from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403

class SqlAlchemyRunRepositoryMaintenanceMixin:
  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ...]:
    statement = select(
      provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.c.payload
    ).order_by(
      provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.c.recorded_at.desc(),
      provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )
  def save_provider_provenance_scheduler_narrative_governance_plan(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_plan_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "plan_id": record.plan_id,
      "item_type": record.item_type,
      "action": record.action,
      "status": record.status,
      "policy_template_id": record.policy_template_id,
      "approval_lane": record.approval_lane,
      "approval_priority": record.approval_priority,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_plans.c.plan_id).where(
          provider_provenance_scheduler_narrative_governance_plans.c.plan_id == record.plan_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_narrative_governance_plans).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_narrative_governance_plans)
          .where(provider_provenance_scheduler_narrative_governance_plans.c.plan_id == record.plan_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_narrative_governance_plans(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...]:
    statement = select(provider_provenance_scheduler_narrative_governance_plans.c.payload).order_by(
      provider_provenance_scheduler_narrative_governance_plans.c.updated_at.desc(),
      provider_provenance_scheduler_narrative_governance_plans.c.plan_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_plan_adapter.validate_python(row["payload"])
      for row in rows
    )
  def get_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(provider_provenance_scheduler_narrative_governance_plans.c.payload).where(
          provider_provenance_scheduler_narrative_governance_plans.c.plan_id == plan_id
        )
      ).mappings().first()
    if row is None:
      return None
    return self._provider_provenance_scheduler_narrative_governance_plan_adapter.validate_python(
      row["payload"]
    )
  def save_provider_provenance_scheduler_stitched_report_governance_plan(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    payload = self._provider_provenance_scheduler_narrative_governance_plan_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "plan_id": record.plan_id,
      "item_type": record.item_type,
      "action": record.action,
      "status": record.status,
      "policy_template_id": record.policy_template_id,
      "approval_lane": record.approval_lane,
      "approval_priority": record.approval_priority,
      "updated_at": record.updated_at.isoformat(),
      "created_by_tab_id": record.created_by_tab_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_stitched_report_governance_plans.c.plan_id).where(
          provider_provenance_scheduler_stitched_report_governance_plans.c.plan_id == record.plan_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_stitched_report_governance_plans).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_stitched_report_governance_plans)
          .where(provider_provenance_scheduler_stitched_report_governance_plans.c.plan_id == record.plan_id)
          .values(**row)
        )
    return record
  def list_provider_provenance_scheduler_stitched_report_governance_plans(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...]:
    statement = select(provider_provenance_scheduler_stitched_report_governance_plans.c.payload).order_by(
      provider_provenance_scheduler_stitched_report_governance_plans.c.updated_at.desc(),
      provider_provenance_scheduler_stitched_report_governance_plans.c.plan_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._provider_provenance_scheduler_narrative_governance_plan_adapter.validate_python(row["payload"])
      for row in rows
    )
