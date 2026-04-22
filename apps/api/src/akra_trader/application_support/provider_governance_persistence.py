from __future__ import annotations

from typing import Any

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord


def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
  app: Any,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
  return (
    app._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      record
    )
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
  app: Any,
) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
  return tuple(
    app._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records()
  )


def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
  app: Any,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
  return (
    app._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
      record
    )
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
  app: Any,
) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
  return tuple(
    app._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records()
  )


def save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
  app: Any,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
  return (
    app._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
      record
    )
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
  app: Any,
) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
  return tuple(
    app._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records()
  )


def save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
  app: Any,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
  return (
    app._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
      record
    )
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
  app: Any,
) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
  return tuple(
    app._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records()
  )


def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
  app: Any,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
  return (
    app._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
      record
    )
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records(
  app: Any,
) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord, ...]:
  return tuple(
    app._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records()
  )


def save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
  app: Any,
  record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
  return (
    app._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
      record
    )
  )


def list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records(
  app: Any,
) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord, ...]:
  return tuple(
    app._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records()
  )
