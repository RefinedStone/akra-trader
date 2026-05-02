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

from akra_trader.adapters.provider_provenance_search_service import ProviderProvenanceSchedulerSearchService

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

  @app.post("/provider-provenance-scheduler-search/moderation-catalog-governance-meta-policies")
  def save_moderation_catalog_governance_meta_policy(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-catalog-governance-meta-policies")
  def list_moderation_catalog_governance_meta_policies(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationCatalogGovernanceMetaPolicyListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationCatalogGovernanceMetaPolicyListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records()
      )
    )

  @app.post("/provider-provenance-scheduler-search/moderation-catalog-governance-meta-plans")
  def save_moderation_catalog_governance_meta_plan(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
    authorization: str | None = Header(default=None),
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    _require_authorization(authorization)
    return service.save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
      record
    )

  @app.get("/provider-provenance-scheduler-search/moderation-catalog-governance-meta-plans")
  def list_moderation_catalog_governance_meta_plans(
    authorization: str | None = Header(default=None),
  ) -> _SchedulerSearchModerationCatalogGovernanceMetaPlanListResponse:
    _require_authorization(authorization)
    return _SchedulerSearchModerationCatalogGovernanceMetaPlanListResponse(
      items=list(
        service.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records()
      )
    )

  return app
