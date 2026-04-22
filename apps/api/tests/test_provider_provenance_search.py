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
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchFeedbackRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPlanPreviewItem
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchQueryAnalyticsRecord


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


def test_http_scheduler_search_service_client_round_trips_analytics_and_feedback() -> None:
  service = ProviderProvenanceSchedulerSearchService(
    store=InMemoryProviderProvenanceSchedulerSearchStore()
  )
  service_app = create_provider_provenance_scheduler_search_service_app(
    service=service,
    auth_token="search-token",
  )
  analytics_record = ProviderProvenanceSchedulerSearchQueryAnalyticsRecord(
    query_id="query-1",
    recorded_at=datetime(2026, 4, 22, 12, 5, tzinfo=UTC),
    expires_at=datetime(2026, 4, 29, 12, 5, tzinfo=UTC),
    query="status:resolved AND recovered",
    token_count=2,
    matched_occurrences=2,
    top_score=440,
    query_terms=("recovered",),
    parsed_operators=("status:resolved",),
  )
  feedback_record = ProviderProvenanceSchedulerSearchFeedbackRecord(
    feedback_id="feedback-1",
    recorded_at=datetime(2026, 4, 22, 12, 6, tzinfo=UTC),
    expires_at=datetime(2026, 4, 29, 12, 6, tzinfo=UTC),
    query_id="query-1",
    query="status:resolved AND recovered",
    occurrence_id="occ-1",
    signal="relevant",
    matched_fields=("summary", "status_sequence"),
    semantic_concepts=("recovery",),
    operator_hits=("status:resolved",),
    lexical_score=220,
    semantic_score=110,
    operator_score=160,
    score=530,
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

    saved_analytics = backend.save_provider_provenance_scheduler_search_query_analytics_record(
      analytics_record
    )
    saved_feedback = backend.save_provider_provenance_scheduler_search_feedback_record(
      feedback_record
    )
    listed_analytics = backend.list_provider_provenance_scheduler_search_query_analytics_records()
    listed_feedback = backend.list_provider_provenance_scheduler_search_feedback_records()
    deleted_analytics = backend.prune_provider_provenance_scheduler_search_query_analytics_records(
      analytics_record.expires_at + timedelta(seconds=1)  # type: ignore[operator]
    )
    deleted_feedback = backend.prune_provider_provenance_scheduler_search_feedback_records(
      feedback_record.expires_at + timedelta(seconds=1)  # type: ignore[operator]
    )

  assert saved_analytics.query_id == "query-1"
  assert saved_feedback.feedback_id == "feedback-1"
  assert len(listed_analytics) == 1
  assert listed_analytics[0].parsed_operators == ("status:resolved",)
  assert len(listed_feedback) == 1
  assert listed_feedback[0].signal == "relevant"
  assert deleted_analytics == 1
  assert deleted_feedback == 1


def test_http_scheduler_search_service_client_round_trips_moderation_catalogs_and_plans() -> None:
  service = ProviderProvenanceSchedulerSearchService(
    store=InMemoryProviderProvenanceSchedulerSearchStore()
  )
  service_app = create_provider_provenance_scheduler_search_service_app(
    service=service,
    auth_token="search-token",
  )
  catalog_record = ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord(
    catalog_id="catalog-1",
    created_at=datetime(2026, 4, 22, 13, 0, tzinfo=UTC),
    updated_at=datetime(2026, 4, 22, 13, 0, tzinfo=UTC),
    name="Pending scheduler approvals",
    description="Moderate high-signal scheduler feedback before ranking learns from it.",
    default_moderation_status="approved",
    governance_view="high_score_pending",
    window_days=30,
    stale_pending_hours=24,
    minimum_score=150,
    require_note=True,
  )
  plan_record = ProviderProvenanceSchedulerSearchModerationPlanRecord(
    plan_id="plan-1",
    created_at=datetime(2026, 4, 22, 13, 5, tzinfo=UTC),
    updated_at=datetime(2026, 4, 22, 13, 5, tzinfo=UTC),
    policy_catalog_id="catalog-1",
    policy_catalog_name="Pending scheduler approvals",
    proposed_moderation_status="approved",
    governance_view="high_score_pending",
    window_days=30,
    stale_pending_hours=24,
    minimum_score=150,
    require_note=True,
    requested_feedback_ids=("feedback-1",),
    feedback_ids=("feedback-1",),
    preview_items=(
      ProviderProvenanceSchedulerSearchModerationPlanPreviewItem(
        feedback_id="feedback-1",
        occurrence_id="occ-1",
        query="status:resolved AND recovered",
        signal="relevant",
        current_moderation_status="pending",
        proposed_moderation_status="approved",
        score=530,
        age_hours=2,
        stale_pending=False,
        high_score_pending=True,
        query_run_count=3,
      ),
    ),
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

    saved_catalog = backend.save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
      catalog_record
    )
    saved_plan = backend.save_provider_provenance_scheduler_search_moderation_plan_record(
      plan_record
    )
    listed_catalogs = backend.list_provider_provenance_scheduler_search_moderation_policy_catalog_records()
    listed_plans = backend.list_provider_provenance_scheduler_search_moderation_plan_records()

  assert saved_catalog.catalog_id == "catalog-1"
  assert saved_plan.plan_id == "plan-1"
  assert len(listed_catalogs) == 1
  assert listed_catalogs[0].require_note is True
  assert len(listed_plans) == 1
  assert listed_plans[0].preview_items[0].feedback_id == "feedback-1"
