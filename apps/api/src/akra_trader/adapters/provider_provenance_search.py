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


class _SchedulerSearchDocumentPruneRequest(BaseModel):
  current_time: datetime


class _SchedulerSearchDocumentPruneResponse(BaseModel):
  deleted_count: int


class _SchedulerSearchDocumentListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchDocumentRecord]


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


class SqlAlchemyProviderProvenanceSchedulerSearchStore:
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


class HttpProviderProvenanceSchedulerSearchServiceClient(
  ProviderProvenanceSchedulerSearchBackendPort
):
  persistence_mode = "external_scheduler_search_service"
  _record_adapter = TypeAdapter(ProviderProvenanceSchedulerSearchDocumentRecord)
  _list_response_adapter = TypeAdapter(_SchedulerSearchDocumentListResponse)
  _prune_response_adapter = TypeAdapter(_SchedulerSearchDocumentPruneResponse)

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
