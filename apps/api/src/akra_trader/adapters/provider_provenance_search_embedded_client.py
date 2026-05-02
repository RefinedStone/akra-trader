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

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records()

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    return self._service.save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
      record
    )

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord, ...]:
    return self._service.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records()
