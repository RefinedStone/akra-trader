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
  _moderation_catalog_governance_meta_policy_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord
  )
  _moderation_catalog_governance_meta_plan_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord
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
  _moderation_catalog_governance_meta_policy_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationCatalogGovernanceMetaPolicyListResponse
  )
  _moderation_catalog_governance_meta_plan_list_response_adapter = TypeAdapter(
    _SchedulerSearchModerationCatalogGovernanceMetaPlanListResponse
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

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    payload = self._moderation_catalog_governance_meta_policy_record_adapter.dump_python(
      record,
      mode="json",
    )
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-meta-policies",
      payload=payload,
    )
    return self._moderation_catalog_governance_meta_policy_record_adapter.validate_python(
      response
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-meta-policies",
    )
    parsed = self._moderation_catalog_governance_meta_policy_list_response_adapter.validate_python(
      response
    )
    return tuple(parsed.items)

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    payload = self._moderation_catalog_governance_meta_plan_record_adapter.dump_python(
      record,
      mode="json",
    )
    response = self._request(
      method="POST",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-meta-plans",
      payload=payload,
    )
    return self._moderation_catalog_governance_meta_plan_record_adapter.validate_python(
      response
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord, ...]:
    response = self._request(
      method="GET",
      path="/provider-provenance-scheduler-search/moderation-catalog-governance-meta-plans",
    )
    parsed = self._moderation_catalog_governance_meta_plan_list_response_adapter.validate_python(
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
