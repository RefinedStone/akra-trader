from __future__ import annotations

from collections import OrderedDict
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from importlib import import_module
from typing import Iterable

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import Candle
from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
from akra_trader.domain.models import ReplayIntentAliasAuditRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportArtifactRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportJobAuditRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportJobRecord
from akra_trader.domain.models import ReplayIntentAliasRecord
from akra_trader.domain.models import ProviderProvenanceAnalyticsPresetRecord
from akra_trader.domain.models import ProviderProvenanceDashboardViewRecord
from akra_trader.domain.models import ProviderProvenanceExportArtifactRecord
from akra_trader.domain.models import ProviderProvenanceExportJobAuditRecord
from akra_trader.domain.models import ProviderProvenanceExportJobRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerHealthRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportViewAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportViewRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportViewRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeRegistryRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeTemplateRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord
from akra_trader.domain.models import ProviderProvenanceScheduledReportAuditRecord
from akra_trader.domain.models import ProviderProvenanceScheduledReportRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyCatalogSemantics
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.ports import MarketDataPort
from akra_trader.ports import ExperimentPresetCatalogPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.lineage import build_candle_dataset_identity
from akra_trader.lineage import build_dataset_boundary_contract
from akra_trader.strategies.base import Strategy
from akra_trader.strategies.examples import MovingAverageCrossStrategy




class InMemoryProviderProvenanceRepositoryMixin:
  def save_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    self._provider_provenance_scheduler_narrative_governance_policy_templates[record.policy_template_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_policy_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_policy_templates.values(),
        key=lambda record: (record.updated_at, record.policy_template_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None:
    return self._provider_provenance_scheduler_narrative_governance_policy_templates.get(policy_template_id)

  def save_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
    self._provider_provenance_scheduler_narrative_governance_policy_template_revisions[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_policy_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_policy_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    return self._provider_provenance_scheduler_narrative_governance_policy_template_revisions.get(revision_id)

  def save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord:
    self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records[record.audit_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_stitched_report_governance_policy_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    self._provider_provenance_scheduler_stitched_report_governance_policy_templates[
      record.policy_template_id
    ] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_policy_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_policy_templates.values(),
        key=lambda record: (record.updated_at, record.policy_template_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_governance_policy_template(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None:
    return self._provider_provenance_scheduler_stitched_report_governance_policy_templates.get(
      policy_template_id
    )

  def save_provider_provenance_scheduler_stitched_report_governance_policy_template_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
    self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions[
      record.revision_id
    ] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_policy_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_governance_policy_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    return self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.get(
      revision_id
    )

  def save_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord:
    self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records[
      record.audit_id
    ] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    self._provider_provenance_scheduler_narrative_governance_policy_catalogs[record.catalog_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_policy_catalogs(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_policy_catalogs.values(),
        key=lambda record: (record.updated_at, record.catalog_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None:
    return self._provider_provenance_scheduler_narrative_governance_policy_catalogs.get(catalog_id)

  def save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    return self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.get(revision_id)

  def save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records[record.audit_id] = (
      record
    )
    return record

  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_stitched_report_governance_policy_catalog(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs[record.catalog_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_policy_catalogs(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs.values(),
        key=lambda record: (record.updated_at, record.catalog_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_governance_policy_catalog(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None:
    return self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs.get(catalog_id)

  def save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions[
      record.revision_id
    ] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    return self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.get(
      revision_id
    )

  def save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records[
      record.audit_id
    ] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates[
      record.hierarchy_step_template_id
    ] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.values(),
        key=lambda record: (record.updated_at, record.hierarchy_step_template_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord | None:
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.get(
      hierarchy_step_template_id
    )

  def save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord:
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions[
      record.revision_id
    ] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord | None:
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.get(
      revision_id
    )

  def save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord:
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records[
      record.audit_id
    ] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_narrative_governance_plan(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    self._provider_provenance_scheduler_narrative_governance_plans[record.plan_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_governance_plans(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_plans.values(),
        key=lambda record: (record.updated_at, record.plan_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord | None:
    return self._provider_provenance_scheduler_narrative_governance_plans.get(plan_id)

  def save_provider_provenance_scheduler_stitched_report_governance_plan(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    self._provider_provenance_scheduler_stitched_report_governance_plans[record.plan_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_plans(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_plans.values(),
        key=lambda record: (record.updated_at, record.plan_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_governance_plan(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord | None:
    return self._provider_provenance_scheduler_stitched_report_governance_plans.get(plan_id)

  def save_provider_provenance_scheduled_report_audit_record(
    self,
    record: ProviderProvenanceScheduledReportAuditRecord,
  ) -> ProviderProvenanceScheduledReportAuditRecord:
    self._provider_provenance_scheduled_report_audit_records[record.audit_id] = record
    return record

  def list_provider_provenance_scheduled_report_audit_records(
    self,
    report_id: str | None = None,
  ) -> tuple[ProviderProvenanceScheduledReportAuditRecord, ...]:
    records = [
      record
      for record in self._provider_provenance_scheduled_report_audit_records.values()
      if report_id is None or record.report_id == report_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def prune_provider_provenance_scheduled_report_audit_records(self, current_time: datetime) -> int:
    original_count = len(self._provider_provenance_scheduled_report_audit_records)
    self._provider_provenance_scheduled_report_audit_records = OrderedDict(
      (
        audit_id,
        record,
      )
      for audit_id, record in self._provider_provenance_scheduled_report_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._provider_provenance_scheduled_report_audit_records)

  def save_provider_provenance_scheduler_health_record(
    self,
    record: ProviderProvenanceSchedulerHealthRecord,
  ) -> ProviderProvenanceSchedulerHealthRecord:
    self._provider_provenance_scheduler_health_records[record.record_id] = record
    return record

  def list_provider_provenance_scheduler_health_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerHealthRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_health_records.values(),
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )

  def prune_provider_provenance_scheduler_health_records(self, current_time: datetime) -> int:
    original_count = len(self._provider_provenance_scheduler_health_records)
    self._provider_provenance_scheduler_health_records = OrderedDict(
      (
        record_id,
        record,
      )
      for record_id, record in self._provider_provenance_scheduler_health_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._provider_provenance_scheduler_health_records)

  def save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    self._provider_provenance_scheduler_search_document_records[record.record_id] = record
    return record

  def list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_search_document_records.values(),
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )

  def prune_provider_provenance_scheduler_search_document_records(self, current_time: datetime) -> int:
    original_count = len(self._provider_provenance_scheduler_search_document_records)
    self._provider_provenance_scheduler_search_document_records = OrderedDict(
      (
        record_id,
        record,
      )
      for record_id, record in self._provider_provenance_scheduler_search_document_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._provider_provenance_scheduler_search_document_records)

  def load_replay_intent_alias_signing_secret(self) -> str | None:
    return self._replay_intent_alias_signing_secret

  def save_replay_intent_alias_signing_secret(self, secret: str) -> str:
    self._replay_intent_alias_signing_secret = secret
    return secret
