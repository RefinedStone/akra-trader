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
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord
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


class _SchedulerSearchModerationPlanListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPlanRecord]


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
    self._moderation_plan_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationPlanRecord,
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


class SqlAlchemyProviderProvenanceSchedulerSearchStore:
  _record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchDocumentRecord)
  _analytics_record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchQueryAnalyticsRecord)
  _feedback_record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchFeedbackRecord)
  _moderation_policy_catalog_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord
  )
  _moderation_plan_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationPlanRecord
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
        "provider_provenance_scheduler_search_moderation_plans",
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

  def save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    return self._store.save_provider_provenance_scheduler_search_moderation_plan_record(record)

  def list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    return self._store.list_provider_provenance_scheduler_search_moderation_plan_records()


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

  def save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_plan_record(record)

  def list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_plan_records()


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
  _moderation_plan_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationPlanRecord
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
  _moderation_plan_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationPlanListResponse
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
