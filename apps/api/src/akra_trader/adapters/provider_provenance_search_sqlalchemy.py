from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
import json
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from pydantic import TypeAdapter
from sqlalchemy import delete
from sqlalchemy import inspect
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchFeedbackRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchQueryAnalyticsRecord
from akra_trader.port_contracts.search import ProviderProvenanceSchedulerSearchBackendPort
from akra_trader.adapters.provider_provenance_search_schema import *

from akra_trader.adapters.provider_provenance_search_sqlalchemy_schema import SqlAlchemyProviderProvenanceSchedulerSearchSchemaMixin

class SqlAlchemyProviderProvenanceSchedulerSearchStore(SqlAlchemyProviderProvenanceSchedulerSearchSchemaMixin):
  _record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchDocumentRecord)
  _analytics_record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchQueryAnalyticsRecord)
  _feedback_record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchFeedbackRecord)
  _moderation_policy_catalog_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord
  )
  _moderation_policy_catalog_revision_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord
  )
  _moderation_policy_catalog_audit_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord
  )
  _moderation_plan_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationPlanRecord
  )
  _moderation_catalog_governance_policy_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord
  )
  _moderation_catalog_governance_policy_revision_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord
  )
  _moderation_catalog_governance_policy_audit_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord
  )
  _moderation_catalog_governance_plan_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord
  )
  _moderation_catalog_governance_meta_policy_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord
  )
  _moderation_catalog_governance_meta_plan_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord
  )

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = _build_engine(database_url)
    metadata.create_all(self._engine)
    self._ensure_schema()

  def save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    payload = self._record_adapter.dump_python(record, mode="json")
    row = {
      "record_id": record.record_id,
      "scheduler_key": record.scheduler_key,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_search_documents.c.record_id).where(
          provider_provenance_scheduler_search_documents.c.record_id == record.record_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_search_documents).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_documents)
          .where(provider_provenance_scheduler_search_documents.c.record_id == record.record_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    statement = select(provider_provenance_scheduler_search_documents.c.payload).order_by(
      provider_provenance_scheduler_search_documents.c.recorded_at.desc(),
      provider_provenance_scheduler_search_documents.c.record_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def prune_provider_provenance_scheduler_search_document_records(
    self,
    current_time: datetime,
  ) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_scheduler_search_documents).where(
          provider_provenance_scheduler_search_documents.c.expires_at.is_not(None),
          provider_provenance_scheduler_search_documents.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    payload = self._analytics_record_adapter.dump_python(record, mode="json")
    row = {
      "query_id": record.query_id,
      "scheduler_key": record.scheduler_key,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "query": record.query,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_search_query_analytics.c.query_id).where(
          provider_provenance_scheduler_search_query_analytics.c.query_id == record.query_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_search_query_analytics).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_query_analytics)
          .where(provider_provenance_scheduler_search_query_analytics.c.query_id == record.query_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]:
    statement = select(provider_provenance_scheduler_search_query_analytics.c.payload).order_by(
      provider_provenance_scheduler_search_query_analytics.c.recorded_at.desc(),
      provider_provenance_scheduler_search_query_analytics.c.query_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._analytics_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def prune_provider_provenance_scheduler_search_query_analytics_records(
    self,
    current_time: datetime,
  ) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_scheduler_search_query_analytics).where(
          provider_provenance_scheduler_search_query_analytics.c.expires_at.is_not(None),
          provider_provenance_scheduler_search_query_analytics.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    payload = self._feedback_record_adapter.dump_python(record, mode="json")
    row = {
      "feedback_id": record.feedback_id,
      "scheduler_key": record.scheduler_key,
      "recorded_at": record.recorded_at.isoformat(),
      "expires_at": record.expires_at.isoformat() if record.expires_at is not None else None,
      "query_id": record.query_id,
      "query": record.query,
      "occurrence_id": record.occurrence_id,
      "signal": record.signal,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_search_feedback.c.feedback_id).where(
          provider_provenance_scheduler_search_feedback.c.feedback_id == record.feedback_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_search_feedback).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_feedback)
          .where(provider_provenance_scheduler_search_feedback.c.feedback_id == record.feedback_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]:
    statement = select(provider_provenance_scheduler_search_feedback.c.payload).order_by(
      provider_provenance_scheduler_search_feedback.c.recorded_at.desc(),
      provider_provenance_scheduler_search_feedback.c.feedback_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._feedback_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def prune_provider_provenance_scheduler_search_feedback_records(
    self,
    current_time: datetime,
  ) -> int:
    with self._engine.begin() as connection:
      result = connection.execute(
        delete(provider_provenance_scheduler_search_feedback).where(
          provider_provenance_scheduler_search_feedback.c.expires_at.is_not(None),
          provider_provenance_scheduler_search_feedback.c.expires_at <= current_time.isoformat(),
        )
      )
    return result.rowcount or 0

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    payload = self._moderation_policy_catalog_record_adapter.dump_python(record, mode="json")
    row = {
      "catalog_id": record.catalog_id,
      "scheduler_key": record.scheduler_key,
      "created_at": record.created_at.isoformat(),
      "updated_at": record.updated_at.isoformat(),
      "status": record.status,
      "name": record.name,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_search_moderation_policy_catalogs.c.catalog_id).where(
          provider_provenance_scheduler_search_moderation_policy_catalogs.c.catalog_id == record.catalog_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_search_moderation_policy_catalogs).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_policy_catalogs)
          .where(
            provider_provenance_scheduler_search_moderation_policy_catalogs.c.catalog_id
            == record.catalog_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_policy_catalogs.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_policy_catalogs.c.updated_at.desc(),
      provider_provenance_scheduler_search_moderation_policy_catalogs.c.catalog_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_policy_catalog_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    payload = self._moderation_policy_catalog_revision_record_adapter.dump_python(record, mode="json")
    row = {
      "revision_id": record.revision_id,
      "catalog_id": record.catalog_id,
      "scheduler_key": record.scheduler_key,
      "recorded_at": record.recorded_at.isoformat(),
      "action": record.action,
      "status": record.status,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_search_moderation_policy_catalog_revisions.c.revision_id).where(
          provider_provenance_scheduler_search_moderation_policy_catalog_revisions.c.revision_id == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_search_moderation_policy_catalog_revisions).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_policy_catalog_revisions)
          .where(
            provider_provenance_scheduler_search_moderation_policy_catalog_revisions.c.revision_id
            == record.revision_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_policy_catalog_revisions.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_policy_catalog_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_search_moderation_policy_catalog_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_policy_catalog_revision_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    payload = self._moderation_policy_catalog_audit_record_adapter.dump_python(record, mode="json")
    row = {
      "audit_id": record.audit_id,
      "catalog_id": record.catalog_id,
      "scheduler_key": record.scheduler_key,
      "recorded_at": record.recorded_at.isoformat(),
      "action": record.action,
      "status": record.status,
      "actor_tab_id": record.actor_tab_id,
      "name": record.name,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_search_moderation_policy_catalog_audits.c.audit_id).where(
          provider_provenance_scheduler_search_moderation_policy_catalog_audits.c.audit_id == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(provider_provenance_scheduler_search_moderation_policy_catalog_audits).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_policy_catalog_audits)
          .where(
            provider_provenance_scheduler_search_moderation_policy_catalog_audits.c.audit_id
            == record.audit_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_policy_catalog_audits.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_policy_catalog_audits.c.recorded_at.desc(),
      provider_provenance_scheduler_search_moderation_policy_catalog_audits.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_policy_catalog_audit_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    payload = self._moderation_plan_record_adapter.dump_python(record, mode="json")
    row = {
      "plan_id": record.plan_id,
      "scheduler_key": record.scheduler_key,
      "created_at": record.created_at.isoformat(),
      "updated_at": record.updated_at.isoformat(),
      "status": record.status,
      "queue_state": record.queue_state,
      "policy_catalog_id": record.policy_catalog_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(provider_provenance_scheduler_search_moderation_plans.c.plan_id).where(
          provider_provenance_scheduler_search_moderation_plans.c.plan_id == record.plan_id
        )
      ).first()
      if existing is None:
        connection.execute(insert(provider_provenance_scheduler_search_moderation_plans).values(**row))
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_plans)
          .where(provider_provenance_scheduler_search_moderation_plans.c.plan_id == record.plan_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    statement = select(provider_provenance_scheduler_search_moderation_plans.c.payload).order_by(
      provider_provenance_scheduler_search_moderation_plans.c.updated_at.desc(),
      provider_provenance_scheduler_search_moderation_plans.c.plan_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_plan_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    payload = self._moderation_catalog_governance_policy_record_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "governance_policy_id": record.governance_policy_id,
      "scheduler_key": record.scheduler_key,
      "created_at": record.created_at.isoformat(),
      "updated_at": record.updated_at.isoformat(),
      "status": record.status,
      "action_scope": record.action_scope,
      "name": record.name,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      exists = connection.execute(
        select(
          provider_provenance_scheduler_search_moderation_catalog_governance_policies.c.governance_policy_id
        ).where(
          provider_provenance_scheduler_search_moderation_catalog_governance_policies.c.governance_policy_id
          == record.governance_policy_id
        )
      ).first()
      if exists is None:
        connection.execute(
          insert(provider_provenance_scheduler_search_moderation_catalog_governance_policies).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_catalog_governance_policies)
          .where(
            provider_provenance_scheduler_search_moderation_catalog_governance_policies.c.governance_policy_id
            == record.governance_policy_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_catalog_governance_policies.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_catalog_governance_policies.c.updated_at.desc(),
      provider_provenance_scheduler_search_moderation_catalog_governance_policies.c.governance_policy_id.desc(),
    )
    with self._engine.begin() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_catalog_governance_policy_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    payload = self._moderation_catalog_governance_policy_revision_record_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "revision_id": record.revision_id,
      "governance_policy_id": record.governance_policy_id,
      "scheduler_key": record.scheduler_key,
      "recorded_at": record.recorded_at.isoformat(),
      "action": record.action,
      "status": record.status,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(
          provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions.c.revision_id
        ).where(
          provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions.c.revision_id
          == record.revision_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(
            provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions
          ).values(**row)
        )
      else:
        connection.execute(
          update(
            provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions
          )
          .where(
            provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions.c.revision_id
            == record.revision_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions.c.recorded_at.desc(),
      provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions.c.revision_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_catalog_governance_policy_revision_record_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    payload = self._moderation_catalog_governance_policy_audit_record_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "audit_id": record.audit_id,
      "governance_policy_id": record.governance_policy_id,
      "scheduler_key": record.scheduler_key,
      "recorded_at": record.recorded_at.isoformat(),
      "action": record.action,
      "status": record.status,
      "actor_tab_id": record.actor_tab_id,
      "name": record.name,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(
          provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits.c.audit_id
        ).where(
          provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits.c.audit_id
          == record.audit_id
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(
            provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits
          ).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits)
          .where(
            provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits.c.audit_id
            == record.audit_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits.c.recorded_at.desc(),
      provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits.c.audit_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_catalog_governance_policy_audit_record_adapter.validate_python(
        row["payload"]
      )
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    payload = self._moderation_catalog_governance_plan_record_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "plan_id": record.plan_id,
      "scheduler_key": record.scheduler_key,
      "created_at": record.created_at.isoformat(),
      "updated_at": record.updated_at.isoformat(),
      "status": record.status,
      "queue_state": record.queue_state,
      "action": record.action,
      "governance_policy_id": record.governance_policy_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      exists = connection.execute(
        select(provider_provenance_scheduler_search_moderation_catalog_governance_plans.c.plan_id).where(
          provider_provenance_scheduler_search_moderation_catalog_governance_plans.c.plan_id == record.plan_id
        )
      ).first()
      if exists is None:
        connection.execute(
          insert(provider_provenance_scheduler_search_moderation_catalog_governance_plans).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_catalog_governance_plans)
          .where(provider_provenance_scheduler_search_moderation_catalog_governance_plans.c.plan_id == record.plan_id)
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_catalog_governance_plans.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_catalog_governance_plans.c.updated_at.desc(),
      provider_provenance_scheduler_search_moderation_catalog_governance_plans.c.plan_id.desc(),
    )
    with self._engine.begin() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_catalog_governance_plan_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    payload = self._moderation_catalog_governance_meta_policy_record_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "meta_policy_id": record.meta_policy_id,
      "scheduler_key": record.scheduler_key,
      "created_at": record.created_at.isoformat(),
      "updated_at": record.updated_at.isoformat(),
      "status": record.status,
      "action_scope": record.action_scope,
      "name": record.name,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      exists = connection.execute(
        select(provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies.c.meta_policy_id).where(
          provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies.c.meta_policy_id
          == record.meta_policy_id
        )
      ).first()
      if exists is None:
        connection.execute(
          insert(provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies)
          .where(
            provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies.c.meta_policy_id
            == record.meta_policy_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies.c.updated_at.desc(),
      provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies.c.meta_policy_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_catalog_governance_meta_policy_record_adapter.validate_python(row["payload"])
      for row in rows
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    payload = self._moderation_catalog_governance_meta_plan_record_adapter.dump_python(
      record,
      mode="json",
    )
    row = {
      "plan_id": record.plan_id,
      "scheduler_key": record.scheduler_key,
      "created_at": record.created_at.isoformat(),
      "updated_at": record.updated_at.isoformat(),
      "status": record.status,
      "queue_state": record.queue_state,
      "action": record.action,
      "meta_policy_id": record.meta_policy_id,
      "payload": payload,
    }
    with self._engine.begin() as connection:
      exists = connection.execute(
        select(provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans.c.plan_id).where(
          provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans.c.plan_id
          == record.plan_id
        )
      ).first()
      if exists is None:
        connection.execute(
          insert(provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans).values(**row)
        )
      else:
        connection.execute(
          update(provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans)
          .where(
            provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans.c.plan_id
            == record.plan_id
          )
          .values(**row)
        )
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord, ...]:
    statement = select(
      provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans.c.payload
    ).order_by(
      provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans.c.updated_at.desc(),
      provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans.c.plan_id.desc(),
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      self._moderation_catalog_governance_meta_plan_record_adapter.validate_python(row["payload"])
      for row in rows
    )
