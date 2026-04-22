from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
import json
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from pydantic import BaseModel
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

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchFeedbackRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchQueryAnalyticsRecord
from akra_trader.port_contracts.search import ProviderProvenanceSchedulerSearchBackendPort


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


metadata = MetaData()
provider_provenance_scheduler_search_documents = Table(
  "provider_provenance_scheduler_search_documents",
  metadata,
  Column("record_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_query_analytics = Table(
  "provider_provenance_scheduler_search_query_analytics",
  metadata,
  Column("query_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("query", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_feedback = Table(
  "provider_provenance_scheduler_search_feedback",
  metadata,
  Column("feedback_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("query_id", String, nullable=False, index=True),
  Column("query", String, nullable=False, index=True),
  Column("occurrence_id", String, nullable=False, index=True),
  Column("signal", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_policy_catalogs = Table(
  "provider_provenance_scheduler_search_moderation_policy_catalogs",
  metadata,
  Column("catalog_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_policy_catalog_revisions = Table(
  "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_policy_catalog_audits = Table(
  "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_plans = Table(
  "provider_provenance_scheduler_search_moderation_plans",
  metadata,
  Column("plan_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("queue_state", String, nullable=False, index=True),
  Column("policy_catalog_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_policies = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
  metadata,
  Column("governance_policy_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("action_scope", String, nullable=False, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("governance_policy_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("governance_policy_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_plans = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
  metadata,
  Column("plan_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("queue_state", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("governance_policy_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)


class _SchedulerSearchDocumentPruneRequest(BaseModel):
  current_time: datetime


class _SchedulerSearchDocumentPruneResponse(BaseModel):
  deleted_count: int


class _SchedulerSearchDocumentListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchDocumentRecord]


class _SchedulerSearchAnalyticsPruneRequest(BaseModel):
  current_time: datetime


class _SchedulerSearchAnalyticsPruneResponse(BaseModel):
  deleted_count: int


class _SchedulerSearchAnalyticsListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord]


class _SchedulerSearchFeedbackPruneRequest(BaseModel):
  current_time: datetime


class _SchedulerSearchFeedbackPruneResponse(BaseModel):
  deleted_count: int


class _SchedulerSearchFeedbackListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchFeedbackRecord]


class _SchedulerSearchModerationPolicyCatalogListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord]


class _SchedulerSearchModerationPolicyCatalogRevisionListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord]


class _SchedulerSearchModerationPolicyCatalogAuditListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord]


class _SchedulerSearchModerationPlanListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPlanRecord]


class _SchedulerSearchModerationCatalogGovernancePolicyListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord]


class _SchedulerSearchModerationCatalogGovernancePolicyRevisionListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord]


class _SchedulerSearchModerationCatalogGovernancePolicyAuditListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord]


class _SchedulerSearchModerationCatalogGovernancePlanListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord]


def _normalize_service_auth_token(value: str | None) -> str | None:
  if not isinstance(value, str):
    return None
  normalized = value.strip()
  return normalized or None


class InMemoryProviderProvenanceSchedulerSearchStore:
  def __init__(self) -> None:
    self._records: OrderedDict[str, ProviderProvenanceSchedulerSearchDocumentRecord] = (
      OrderedDict()
    )
    self._analytics_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
    ] = OrderedDict()
    self._feedback_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchFeedbackRecord,
    ] = OrderedDict()
    self._moderation_policy_catalog_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    ] = OrderedDict()
    self._moderation_policy_catalog_revision_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
    ] = OrderedDict()
    self._moderation_policy_catalog_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
    ] = OrderedDict()
    self._moderation_plan_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationPlanRecord,
    ] = OrderedDict()
    self._moderation_catalog_governance_policy_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    ] = OrderedDict()
    self._moderation_catalog_governance_policy_revision_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
    ] = OrderedDict()
    self._moderation_catalog_governance_policy_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
    ] = OrderedDict()
    self._moderation_catalog_governance_plan_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
    ] = OrderedDict()

  def save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    self._records[record.record_id] = record
    return record

  def list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    return tuple(
      sorted(
        self._records.values(),
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )

  def prune_provider_provenance_scheduler_search_document_records(
    self,
    current_time: datetime,
  ) -> int:
    original_count = len(self._records)
    self._records = OrderedDict(
      (
        record_id,
        record,
      )
      for record_id, record in self._records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._records)

  def save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    self._analytics_records[record.query_id] = record
    return record

  def list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]:
    return tuple(
      sorted(
        self._analytics_records.values(),
        key=lambda record: (record.recorded_at, record.query_id),
        reverse=True,
      )
    )

  def prune_provider_provenance_scheduler_search_query_analytics_records(
    self,
    current_time: datetime,
  ) -> int:
    original_count = len(self._analytics_records)
    self._analytics_records = OrderedDict(
      (
        query_id,
        record,
      )
      for query_id, record in self._analytics_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._analytics_records)

  def save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    self._feedback_records[record.feedback_id] = record
    return record

  def list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]:
    return tuple(
      sorted(
        self._feedback_records.values(),
        key=lambda record: (record.recorded_at, record.feedback_id),
        reverse=True,
      )
    )

  def prune_provider_provenance_scheduler_search_feedback_records(
    self,
    current_time: datetime,
  ) -> int:
    original_count = len(self._feedback_records)
    self._feedback_records = OrderedDict(
      (
        feedback_id,
        record,
      )
      for feedback_id, record in self._feedback_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._feedback_records)

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    self._moderation_policy_catalog_records[record.catalog_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord, ...]:
    return tuple(
      sorted(
        self._moderation_policy_catalog_records.values(),
        key=lambda record: (record.updated_at, record.catalog_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    self._moderation_policy_catalog_revision_records[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord, ...]:
    return tuple(
      sorted(
        self._moderation_policy_catalog_revision_records.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    self._moderation_policy_catalog_audit_records[record.audit_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ...]:
    return tuple(
      sorted(
        self._moderation_policy_catalog_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    self._moderation_plan_records[record.plan_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    return tuple(
      sorted(
        self._moderation_plan_records.values(),
        key=lambda record: (record.updated_at, record.plan_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    self._moderation_catalog_governance_policy_records[record.governance_policy_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
    return tuple(
      sorted(
        self._moderation_catalog_governance_policy_records.values(),
        key=lambda record: (record.updated_at, record.governance_policy_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    self._moderation_catalog_governance_policy_revision_records[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
    return tuple(
      sorted(
        self._moderation_catalog_governance_policy_revision_records.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    self._moderation_catalog_governance_policy_audit_records[record.audit_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
    return tuple(
      sorted(
        self._moderation_catalog_governance_policy_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    self._moderation_catalog_governance_plan_records[record.plan_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
    return tuple(
      sorted(
        self._moderation_catalog_governance_plan_records.values(),
        key=lambda record: (record.updated_at, record.plan_id),
        reverse=True,
      )
    )


class SqlAlchemyProviderProvenanceSchedulerSearchStore:
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

  def _ensure_schema(self) -> None:
    inspector = inspect(self._engine)
    existing_indexes_by_table = {
      table_name: {
        index["name"]
        for index in inspector.get_indexes(table_name)
      }
      for table_name in (
        "provider_provenance_scheduler_search_documents",
        "provider_provenance_scheduler_search_query_analytics",
        "provider_provenance_scheduler_search_feedback",
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "provider_provenance_scheduler_search_moderation_plans",
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
      )
    }
    index_specs = (
      (
        "provider_provenance_scheduler_search_documents",
        "ix_provider_provenance_scheduler_search_documents_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_documents",
        "ix_provider_provenance_scheduler_search_documents_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_documents",
        "ix_provider_provenance_scheduler_search_documents_expires_at",
        "expires_at",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_expires_at",
        "expires_at",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_query",
        "query",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_expires_at",
        "expires_at",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_query_id",
        "query_id",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_query",
        "query",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_occurrence_id",
        "occurrence_id",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_signal",
        "signal",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_catalog_id",
        "catalog_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_catalog_id",
        "catalog_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_actor_tab_id",
        "actor_tab_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_queue_state",
        "queue_state",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_policy_catalog_id",
        "policy_catalog_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_action_scope",
        "action_scope",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_governance_policy_id",
        "governance_policy_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_governance_policy_id",
        "governance_policy_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_actor_tab_id",
        "actor_tab_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_queue_state",
        "queue_state",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_governance_policy_id",
        "governance_policy_id",
      ),
    )
    with self._engine.begin() as connection:
      for table_name, index_name, column_name in index_specs:
        if index_name in existing_indexes_by_table.get(table_name, set()):
          continue
        connection.exec_driver_sql(
          "CREATE INDEX IF NOT EXISTS "
          f"{index_name} ON {table_name} ({column_name})"
        )


class ProviderProvenanceSchedulerSearchService:
  service_mode = "provider_provenance_scheduler_search_service.v1"

  def __init__(
    self,
    *,
    store: InMemoryProviderProvenanceSchedulerSearchStore | SqlAlchemyProviderProvenanceSchedulerSearchStore,
  ) -> None:
    self._store = store

  def save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    return self._store.save_provider_provenance_scheduler_search_document_record(record)

  def list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_document_records()

  def prune_provider_provenance_scheduler_search_document_records(
    self,
    current_time: datetime,
  ) -> int:
    return self._store.prune_provider_provenance_scheduler_search_document_records(current_time)

  def save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    return self._store.save_provider_provenance_scheduler_search_query_analytics_record(record)

  def list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_query_analytics_records()

  def prune_provider_provenance_scheduler_search_query_analytics_records(
    self,
    current_time: datetime,
  ) -> int:
    return self._store.prune_provider_provenance_scheduler_search_query_analytics_records(
      current_time
    )

  def save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    return self._store.save_provider_provenance_scheduler_search_feedback_record(record)

  def list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_feedback_records()

  def prune_provider_provenance_scheduler_search_feedback_records(
    self,
    current_time: datetime,
  ) -> int:
    return self._store.prune_provider_provenance_scheduler_search_feedback_records(current_time)

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_policy_catalog_records()

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records()

  def save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_plan_record(record)

  def list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_plan_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records()


def create_provider_provenance_scheduler_search_service_app(
  *,
  service: ProviderProvenanceSchedulerSearchService,
  auth_token: str | None = None,
) -> FastAPI:
  app = FastAPI(title="Akra Provider Provenance Scheduler Search Service")
  normalized_auth_token = _normalize_service_auth_token(auth_token)

  def _require_authorization(authorization: str | None) -> None:
    if normalized_auth_token is None:
      return
    expected = f"Bearer {normalized_auth_token}"
    if authorization != expected:
      raise HTTPException(status_code=401, detail="Unauthorized search service request.")

  @app.post("/provider-provenance-scheduler-search/documents")
  def save_document(
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_document_record(record)

  @app.get("/provider-provenance-scheduler-search/documents")
  def list_documents(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchDocumentListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchDocumentListResponse(
      items=list(service.list_provider_provenance_scheduler_search_document_records())
    )

  @app.post("/provider-provenance-scheduler-search/documents/prune")
  def prune_documents(
    request: _SchedulerSearchDocumentPruneRequest,
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchDocumentPruneResponse:
    _require_authorization(authorization)
    return _SchedulerSearchDocumentPruneResponse(
      deleted_count=service.prune_provider_provenance_scheduler_search_document_records(
        request.current_time
      )
    )

  @app.post("/provider-provenance-scheduler-search/analytics")
  def save_query_analytics(
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_query_analytics_record(record)

  @app.get("/provider-provenance-scheduler-search/analytics")
  def list_query_analytics(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchAnalyticsListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchAnalyticsListResponse(
      items=list(service.list_provider_provenance_scheduler_search_query_analytics_records())
    )

  @app.post("/provider-provenance-scheduler-search/analytics/prune")
  def prune_query_analytics(
    request: _SchedulerSearchAnalyticsPruneRequest,
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchAnalyticsPruneResponse:
    _require_authorization(authorization)
    return _SchedulerSearchAnalyticsPruneResponse(
      deleted_count=service.prune_provider_provenance_scheduler_search_query_analytics_records(
        request.current_time
      )
    )

  @app.post("/provider-provenance-scheduler-search/feedback")
  def save_feedback(
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_feedback_record(record)

  @app.get("/provider-provenance-scheduler-search/feedback")
  def list_feedback(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchFeedbackListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchFeedbackListResponse(
      items=list(service.list_provider_provenance_scheduler_search_feedback_records())
    )

  @app.post("/provider-provenance-scheduler-search/feedback/prune")
  def prune_feedback(
    request: _SchedulerSearchFeedbackPruneRequest,
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchFeedbackPruneResponse:
    _require_authorization(authorization)
    return _SchedulerSearchFeedbackPruneResponse(
      deleted_count=service.prune_provider_provenance_scheduler_search_feedback_records(
        request.current_time
      )
    )

  @app.post("/provider-provenance-scheduler-search/moderation-policy-catalogs")
  def save_moderation_policy_catalog(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-policy-catalogs")
  def list_moderation_policy_catalogs(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationPolicyCatalogListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationPolicyCatalogListResponse(
      items=list(service.list_provider_provenance_scheduler_search_moderation_policy_catalog_records())
    )

  @app.post("/provider-provenance-scheduler-search/moderation-policy-catalog-revisions")
  def save_moderation_policy_catalog_revision(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-policy-catalog-revisions")
  def list_moderation_policy_catalog_revisions(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationPolicyCatalogRevisionListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationPolicyCatalogRevisionListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()
      )
    )

  @app.post("/provider-provenance-scheduler-search/moderation-policy-catalog-audits")
  def save_moderation_policy_catalog_audit(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-policy-catalog-audits")
  def list_moderation_policy_catalog_audits(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationPolicyCatalogAuditListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationPolicyCatalogAuditListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records()
      )
    )

  @app.post("/provider-provenance-scheduler-search/moderation-plans")
  def save_moderation_plan(
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_plan_record(record)

  @app.get("/provider-provenance-scheduler-search/moderation-plans")
  def list_moderation_plans(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationPlanListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationPlanListResponse(
      items=list(service.list_provider_provenance_scheduler_search_moderation_plan_records())
    )

  @app.post("/provider-provenance-scheduler-search/moderation-catalog-governance-policies")
  def save_moderation_catalog_governance_policy(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-catalog-governance-policies")
  def list_moderation_catalog_governance_policies(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationCatalogGovernancePolicyListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationCatalogGovernancePolicyListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records()
      )
    )

  @app.post("/provider-provenance-scheduler-search/moderation-catalog-governance-policy-revisions")
  def save_moderation_catalog_governance_policy_revision(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-catalog-governance-policy-revisions")
  def list_moderation_catalog_governance_policy_revisions(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationCatalogGovernancePolicyRevisionListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationCatalogGovernancePolicyRevisionListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records()
      )
    )

  @app.post("/provider-provenance-scheduler-search/moderation-catalog-governance-policy-audits")
  def save_moderation_catalog_governance_policy_audit(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-catalog-governance-policy-audits")
  def list_moderation_catalog_governance_policy_audits(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationCatalogGovernancePolicyAuditListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationCatalogGovernancePolicyAuditListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records()
      )
    )

  @app.post("/provider-provenance-scheduler-search/moderation-catalog-governance-plans")
  def save_moderation_catalog_governance_plan(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-catalog-governance-plans")
  def list_moderation_catalog_governance_plans(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationCatalogGovernancePlanListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationCatalogGovernancePlanListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records()
      )
    )

  return app


class EmbeddedProviderProvenanceSchedulerSearchServiceClient(
  ProviderProvenanceSchedulerSearchBackendPort
):
  persistence_mode = "embedded_scheduler_search_service"

  def __init__(self, service: ProviderProvenanceSchedulerSearchService) -> None:
    self._service = service

  def save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    return self._service.save_provider_provenance_scheduler_search_document_record(record)

  def list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_document_records()

  def prune_provider_provenance_scheduler_search_document_records(
    self,
    current_time: datetime,
  ) -> int:
    return self._service.prune_provider_provenance_scheduler_search_document_records(current_time)

  def save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    return self._service.save_provider_provenance_scheduler_search_query_analytics_record(record)

  def list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_query_analytics_records()

  def prune_provider_provenance_scheduler_search_query_analytics_records(
    self,
    current_time: datetime,
  ) -> int:
    return self._service.prune_provider_provenance_scheduler_search_query_analytics_records(
      current_time
    )

  def save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    return self._service.save_provider_provenance_scheduler_search_feedback_record(record)

  def list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_feedback_records()

  def prune_provider_provenance_scheduler_search_feedback_records(
    self,
    current_time: datetime,
  ) -> int:
    return self._service.prune_provider_provenance_scheduler_search_feedback_records(
      current_time
    )

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_policy_catalog_records()

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records()

  def save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_plan_record(record)

  def list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_plan_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records()


class HttpProviderProvenanceSchedulerSearchServiceClient(
  ProviderProvenanceSchedulerSearchBackendPort
):
  persistence_mode = "external_scheduler_search_service"
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
  _list_response_adapter = TypeAdapter(_SchedulerSearchDocumentListResponse)
  _prune_response_adapter = TypeAdapter(_SchedulerSearchDocumentPruneResponse)
  _analytics_list_response_adapter = TypeAdapter(_SchedulerSearchAnalyticsListResponse)
  _analytics_prune_response_adapter = TypeAdapter(_SchedulerSearchAnalyticsPruneResponse)
  _feedback_list_response_adapter = TypeAdapter(_SchedulerSearchFeedbackListResponse)
  _feedback_prune_response_adapter = TypeAdapter(_SchedulerSearchFeedbackPruneResponse)
  _moderation_policy_catalog_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationPolicyCatalogListResponse
  )
  _moderation_policy_catalog_revision_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationPolicyCatalogRevisionListResponse
  )
  _moderation_policy_catalog_audit_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationPolicyCatalogAuditListResponse
  )
  _moderation_plan_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationPlanListResponse
  )
  _moderation_catalog_governance_policy_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationCatalogGovernancePolicyListResponse
  )
  _moderation_catalog_governance_policy_revision_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationCatalogGovernancePolicyRevisionListResponse
  )
  _moderation_catalog_governance_policy_audit_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationCatalogGovernancePolicyAuditListResponse
  )
  _moderation_catalog_governance_plan_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationCatalogGovernancePlanListResponse
  )

  def __init__(
    self,
    *,
    service_url: str,
    auth_token: str | None = None,
    timeout_seconds: float = 5.0,
    urlopen=urllib_request.urlopen,
  ) -> None:
    normalized_service_url = service_url.rstrip("/")
    if not normalized_service_url:
      raise ValueError("Search service URL is required.")
    self._service_url = normalized_service_url
    self._auth_token = _normalize_service_auth_token(auth_token)
    self._timeout_seconds = max(float(timeout_seconds), 0.1)
    self._urlopen = urlopen

  def save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    payload = self._record_adapter.dump_python(record, mode="json")
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/documents",
      payload=payload,
    )
    return self._record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/documents",
    )
    parsed = self._list_response_adapter.validate_python(response)
    return tuple(parsed.items)

  def prune_provider_provenance_scheduler_search_document_records(
    self,
    current_time: datetime,
  ) -> int:
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/documents/prune",
      payload={"current_time": current_time.isoformat()},
    )
    parsed = self._prune_response_adapter.validate_python(response)
    return parsed.deleted_count

  def save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    payload = self._analytics_record_adapter.dump_python(record, mode="json")
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/analytics",
      payload=payload,
    )
    return self._analytics_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/analytics",
    )
    parsed = self._analytics_list_response_adapter.validate_python(response)
    return tuple(parsed.items)

  def prune_provider_provenance_scheduler_search_query_analytics_records(
    self,
    current_time: datetime,
  ) -> int:
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/analytics/prune",
      payload={"current_time": current_time.isoformat()},
    )
    parsed = self._analytics_prune_response_adapter.validate_python(response)
    return parsed.deleted_count

  def save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    payload = self._feedback_record_adapter.dump_python(record, mode="json")
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/feedback",
      payload=payload,
    )
    return self._feedback_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/feedback",
    )
    parsed = self._feedback_list_response_adapter.validate_python(response)
    return tuple(parsed.items)

  def prune_provider_provenance_scheduler_search_feedback_records(
    self,
    current_time: datetime,
  ) -> int:
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/feedback/prune",
      payload={"current_time": current_time.isoformat()},
    )
    parsed = self._feedback_prune_response_adapter.validate_python(response)
    return parsed.deleted_count

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    payload = self._moderation_policy_catalog_record_adapter.dump_python(record, mode="json")
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-policy-catalogs",
      payload=payload,
    )
    return self._moderation_policy_catalog_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-policy-catalogs",
    )
    parsed = self._moderation_policy_catalog_list_response_adapter.validate_python(response)
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    payload = self._moderation_policy_catalog_revision_record_adapter.dump_python(record, mode="json")
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-policy-catalog-revisions",
      payload=payload,
    )
    return self._moderation_policy_catalog_revision_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-policy-catalog-revisions",
    )
    parsed = self._moderation_policy_catalog_revision_list_response_adapter.validate_python(response)
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    payload = self._moderation_policy_catalog_audit_record_adapter.dump_python(record, mode="json")
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-policy-catalog-audits",
      payload=payload,
    )
    return self._moderation_policy_catalog_audit_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-policy-catalog-audits",
    )
    parsed = self._moderation_policy_catalog_audit_list_response_adapter.validate_python(response)
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    payload = self._moderation_plan_record_adapter.dump_python(record, mode="json")
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-plans",
      payload=payload,
    )
    return self._moderation_plan_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-plans",
    )
    parsed = self._moderation_plan_list_response_adapter.validate_python(response)
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    payload = self._moderation_catalog_governance_policy_record_adapter.dump_python(
      record,
      mode="json",
    )
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-policies",
      payload=payload,
    )
    return self._moderation_catalog_governance_policy_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-policies",
    )
    parsed = self._moderation_catalog_governance_policy_list_response_adapter.validate_python(
      response
    )
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    payload = self._moderation_catalog_governance_policy_revision_record_adapter.dump_python(
      record,
      mode="json",
    )
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-policy-revisions",
      payload=payload,
    )
    return self._moderation_catalog_governance_policy_revision_record_adapter.validate_python(
      response
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-policy-revisions",
    )
    parsed = self._moderation_catalog_governance_policy_revision_list_response_adapter.validate_python(
      response
    )
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    payload = self._moderation_catalog_governance_policy_audit_record_adapter.dump_python(
      record,
      mode="json",
    )
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-policy-audits",
      payload=payload,
    )
    return self._moderation_catalog_governance_policy_audit_record_adapter.validate_python(
      response
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-policy-audits",
    )
    parsed = self._moderation_catalog_governance_policy_audit_list_response_adapter.validate_python(
      response
    )
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    payload = self._moderation_catalog_governance_plan_record_adapter.dump_python(
      record,
      mode="json",
    )
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-plans",
      payload=payload,
    )
    return self._moderation_catalog_governance_plan_record_adapter.validate_python(response)

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-plans",
    )
    parsed = self._moderation_catalog_governance_plan_list_response_adapter.validate_python(
      response
    )
    return tuple(parsed.items)

  def _request(
    self,
    *,
    method: str,
    path: str,
    payload: dict[str, object] | None = None,
  ) -> object:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
      data = json.dumps(payload).encode("utf-8")
      headers["Content-Type"] = "application/json"
    if self._auth_token is not None:
      headers["Authorization"] = f"Bearer {self._auth_token}"
    request = urllib_request.Request(
      f"{self._service_url}{path}",
      data=data,
      headers=headers,
      method=method,
    )
    try:
      with self._urlopen(request, timeout=self._timeout_seconds) as response:
        body = response.read().decode("utf-8")
    except urllib_error.HTTPError as exc:  # pragma: no cover - thin wrapper
      detail = exc.read().decode("utf-8", errors="replace")
      raise RuntimeError(
        f"Search service request failed with status {exc.code}: {detail}"
      ) from exc
    except urllib_error.URLError as exc:  # pragma: no cover - thin wrapper
      raise RuntimeError(f"Search service request failed: {exc.reason}") from exc
    return json.loads(body) if body else {}
