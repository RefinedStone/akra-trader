from __future__ import annotations

from collections import OrderedDict
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

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord
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


class InMemoryProviderProvenanceSchedulerSearchBackend(
  ProviderProvenanceSchedulerSearchBackendPort
):
  persistence_mode = "embedded_scheduler_search_backend"

  def __init__(self) -> None:
    self._records: OrderedDict[str, ProviderProvenanceSchedulerSearchDocumentRecord] = (
      OrderedDict()
    )

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


class SqlAlchemyProviderProvenanceSchedulerSearchBackend(
  ProviderProvenanceSchedulerSearchBackendPort
):
  persistence_mode = "external_scheduler_search_backend"
  _record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchDocumentRecord)

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

  def _ensure_schema(self) -> None:
    inspector = inspect(self._engine)
    existing_indexes = {
      index["name"]
      for index in inspector.get_indexes("provider_provenance_scheduler_search_documents")
    }
    index_specs = (
      ("ix_provider_provenance_scheduler_search_documents_scheduler_key", "scheduler_key"),
      ("ix_provider_provenance_scheduler_search_documents_recorded_at", "recorded_at"),
      ("ix_provider_provenance_scheduler_search_documents_expires_at", "expires_at"),
    )
    with self._engine.begin() as connection:
      for index_name, column_name in index_specs:
        if index_name in existing_indexes:
          continue
        connection.exec_driver_sql(
          "CREATE INDEX IF NOT EXISTS "
          f"{index_name} ON provider_provenance_scheduler_search_documents ({column_name})"
        )
