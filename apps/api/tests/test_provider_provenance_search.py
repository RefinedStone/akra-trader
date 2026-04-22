from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from io import BytesIO
from urllib import error as urllib_error

from fastapi.testclient import TestClient

from akra_trader.adapters.provider_provenance_search import (
  HttpProviderProvenanceSchedulerSearchServiceClient,
)
from akra_trader.adapters.provider_provenance_search import (
  InMemoryProviderProvenanceSchedulerSearchStore,
)
from akra_trader.adapters.provider_provenance_search import (
  ProviderProvenanceSchedulerSearchService,
)
from akra_trader.adapters.provider_provenance_search import (
  create_provider_provenance_scheduler_search_service_app,
)
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord


class FakeResponse:
  def __init__(self, status: int, body: bytes) -> None:
    self.status = status
    self._body = body

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc, tb) -> None:
    return None

  def read(self) -> bytes:
    return self._body


def test_http_scheduler_search_service_client_round_trips_documents() -> None:
  service = ProviderProvenanceSchedulerSearchService(
    store=InMemoryProviderProvenanceSchedulerSearchStore()
  )
  service_app = create_provider_provenance_scheduler_search_service_app(
    service=service,
    auth_token="search-token",
  )
  record = ProviderProvenanceSchedulerSearchDocumentRecord(
    record_id="sched-1",
    recorded_at=datetime(2026, 4, 22, 12, 0, tzinfo=UTC),
    expires_at=datetime(2026, 4, 29, 12, 0, tzinfo=UTC),
    lexical_terms=("scheduler", "lag", "recovered"),
    semantic_concepts=("recovery", "lag"),
    fields={"status": ("resolved",), "summary": ("lag resolved after recovery",)},
  )

  with TestClient(service_app) as service_client:
    def fake_urlopen(request, timeout: float):
      response = service_client.request(
        request.get_method(),
        request.full_url,
        content=request.data,
        headers=dict(request.headers),
      )
      body = response.content
      if response.status_code >= 400:
        raise urllib_error.HTTPError(
          request.full_url,
          response.status_code,
          getattr(response, "reason_phrase", "search service error"),
          hdrs=response.headers,
          fp=BytesIO(body),
        )
      return FakeResponse(response.status_code, body)

    backend = HttpProviderProvenanceSchedulerSearchServiceClient(
      service_url="https://search-service.example",
      auth_token="search-token",
      urlopen=fake_urlopen,
    )

    saved = backend.save_provider_provenance_scheduler_search_document_record(record)
    listed = backend.list_provider_provenance_scheduler_search_document_records()
    deleted = backend.prune_provider_provenance_scheduler_search_document_records(
      record.expires_at + timedelta(seconds=1)  # type: ignore[operator]
    )

  assert backend.persistence_mode == "external_scheduler_search_service"
  assert saved.record_id == "sched-1"
  assert len(listed) == 1
  assert listed[0].semantic_concepts == ("recovery", "lag")
  assert deleted == 1
