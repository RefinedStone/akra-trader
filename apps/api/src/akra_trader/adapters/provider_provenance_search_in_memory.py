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
    self._moderation_catalog_governance_meta_policy_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
    ] = OrderedDict()
    self._moderation_catalog_governance_meta_plan_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
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

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    self._moderation_catalog_governance_meta_policy_records[record.meta_policy_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord, ...]:
    return tuple(
      sorted(
        self._moderation_catalog_governance_meta_policy_records.values(),
        key=lambda record: (record.updated_at, record.meta_policy_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    self._moderation_catalog_governance_meta_plan_records[record.plan_id] = record
    return record

  def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord, ...]:
    return tuple(
      sorted(
        self._moderation_catalog_governance_meta_plan_records.values(),
        key=lambda record: (record.updated_at, record.plan_id),
        reverse=True,
      )
    )
