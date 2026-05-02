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
from akra_trader.strategies.reference import build_reference_strategies


from akra_trader.adapters.in_memory_catalogs import InMemoryExperimentPresetCatalog
from akra_trader.adapters.in_memory_catalogs import LocalStrategyCatalog
from akra_trader.adapters.in_memory_market_data import SeededMarketDataAdapter
from akra_trader.adapters.in_memory_market_data import build_seeded_market_data
from akra_trader.adapters.in_memory_market_data import candles_to_frame
from akra_trader.adapters.in_memory_provider_provenance import InMemoryProviderProvenanceRepositoryMixin


class InMemoryRunRepository(InMemoryProviderProvenanceRepositoryMixin, RunRepositoryPort):
  def __init__(self) -> None:
    self._runs: OrderedDict[str, RunRecord] = OrderedDict()
    self._replay_intent_alias_records: OrderedDict[str, ReplayIntentAliasRecord] = OrderedDict()
    self._replay_intent_alias_audit_records: OrderedDict[str, ReplayIntentAliasAuditRecord] = OrderedDict()
    self._replay_intent_alias_audit_export_artifacts: OrderedDict[str, ReplayIntentAliasAuditExportArtifactRecord] = OrderedDict()
    self._replay_intent_alias_audit_export_jobs: OrderedDict[str, ReplayIntentAliasAuditExportJobRecord] = OrderedDict()
    self._replay_intent_alias_audit_export_job_audit_records: OrderedDict[str, ReplayIntentAliasAuditExportJobAuditRecord] = OrderedDict()
    self._provider_provenance_export_artifacts: OrderedDict[str, ProviderProvenanceExportArtifactRecord] = OrderedDict()
    self._provider_provenance_export_jobs: OrderedDict[str, ProviderProvenanceExportJobRecord] = OrderedDict()
    self._provider_provenance_export_job_audit_records: OrderedDict[str, ProviderProvenanceExportJobAuditRecord] = OrderedDict()
    self._provider_provenance_analytics_presets: OrderedDict[str, ProviderProvenanceAnalyticsPresetRecord] = OrderedDict()
    self._provider_provenance_dashboard_views: OrderedDict[str, ProviderProvenanceDashboardViewRecord] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_views: OrderedDict[
      str,
      ProviderProvenanceSchedulerStitchedReportViewRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_view_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerStitchedReportViewRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_view_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_registries: OrderedDict[
      str,
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_registry_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduled_reports: OrderedDict[str, ProviderProvenanceScheduledReportRecord] = OrderedDict()
    self._provider_provenance_scheduler_narrative_templates: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeTemplateRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_template_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_registry: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeRegistryRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_registry_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_templates: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_policy_templates: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_template_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_catalogs: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_plans: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_stitched_report_governance_plans: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduled_report_audit_records: OrderedDict[str, ProviderProvenanceScheduledReportAuditRecord] = OrderedDict()
    self._provider_provenance_scheduler_health_records: OrderedDict[str, ProviderProvenanceSchedulerHealthRecord] = OrderedDict()
    self._provider_provenance_scheduler_search_document_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerSearchDocumentRecord,
    ] = OrderedDict()
    self._replay_intent_alias_signing_secret: str | None = None

  def save_run(self, run: RunRecord) -> RunRecord:
    self._runs[run.config.run_id] = run
    return run

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get(run_id)

  def compare_runs(self, run_ids: list[str]) -> list[RunRecord]:
    return [run for run_id in run_ids if (run := self._runs.get(run_id)) is not None]

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
    preset_id: str | None = None,
    benchmark_family: str | None = None,
    dataset_identity: str | None = None,
    tags: tuple[str, ...] = (),
  ) -> list[RunRecord]:
    values = list(self._runs.values())
    runs = list(reversed(values))
    if mode is not None:
      runs = [run for run in runs if run.config.mode.value == mode]
    if strategy_id is not None:
      runs = [run for run in runs if run.config.strategy_id == strategy_id]
    if strategy_version is not None:
      runs = [run for run in runs if run.config.strategy_version == strategy_version]
    if rerun_boundary_id is not None:
      runs = [run for run in runs if run.provenance.rerun_boundary_id == rerun_boundary_id]
    if preset_id is not None:
      runs = [run for run in runs if run.provenance.experiment.preset_id == preset_id]
    if benchmark_family is not None:
      runs = [run for run in runs if run.provenance.experiment.benchmark_family == benchmark_family]
    if dataset_identity is not None:
      runs = [
        run
        for run in runs
        if run.provenance.market_data is not None
        and run.provenance.market_data.dataset_identity == dataset_identity
      ]
    if tags:
      required_tags = set(tags)
      runs = [
        run
        for run in runs
        if required_tags.issubset(set(run.provenance.experiment.tags))
      ]
    return runs

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None:
    run = self._runs.get(run_id)
    if run is None:
      return None
    run.status = status
    if status in {RunStatus.COMPLETED, RunStatus.STOPPED, RunStatus.FAILED}:
      run.ended_at = datetime.now(UTC)
    return run

  def save_replay_intent_alias(self, record: ReplayIntentAliasRecord) -> ReplayIntentAliasRecord:
    self._replay_intent_alias_records[record.alias_id] = record
    return record

  def get_replay_intent_alias(self, alias_id: str) -> ReplayIntentAliasRecord | None:
    return self._replay_intent_alias_records.get(alias_id)

  def save_replay_intent_alias_audit_record(
    self,
    record: ReplayIntentAliasAuditRecord,
  ) -> ReplayIntentAliasAuditRecord:
    self._replay_intent_alias_audit_records[record.audit_id] = record
    return record

  def list_replay_intent_alias_audit_records(
    self,
    alias_id: str | None = None,
  ) -> tuple[ReplayIntentAliasAuditRecord, ...]:
    records = [
      record
      for record in self._replay_intent_alias_audit_records.values()
      if alias_id is None or record.alias_id == alias_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def delete_replay_intent_alias_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    deleted_count = 0
    for audit_id in audit_ids:
      if audit_id in self._replay_intent_alias_audit_records:
        deleted_count += 1
        del self._replay_intent_alias_audit_records[audit_id]
    return deleted_count

  def prune_replay_intent_alias_audit_records(self, current_time: datetime) -> int:
    original_count = len(self._replay_intent_alias_audit_records)
    self._replay_intent_alias_audit_records = OrderedDict(
      (
        audit_id,
        record,
      )
      for audit_id, record in self._replay_intent_alias_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._replay_intent_alias_audit_records)

  def save_replay_intent_alias_audit_export_artifact(
    self,
    record: ReplayIntentAliasAuditExportArtifactRecord,
  ) -> ReplayIntentAliasAuditExportArtifactRecord:
    self._replay_intent_alias_audit_export_artifacts[record.artifact_id] = record
    return record

  def get_replay_intent_alias_audit_export_artifact(
    self,
    artifact_id: str,
  ) -> ReplayIntentAliasAuditExportArtifactRecord | None:
    return self._replay_intent_alias_audit_export_artifacts.get(artifact_id)

  def delete_replay_intent_alias_audit_export_artifacts(self, artifact_ids: tuple[str, ...]) -> int:
    deleted_count = 0
    for artifact_id in artifact_ids:
      if artifact_id in self._replay_intent_alias_audit_export_artifacts:
        deleted_count += 1
        del self._replay_intent_alias_audit_export_artifacts[artifact_id]
    return deleted_count

  def prune_replay_intent_alias_audit_export_artifacts(self, current_time: datetime) -> int:
    original_count = len(self._replay_intent_alias_audit_export_artifacts)
    self._replay_intent_alias_audit_export_artifacts = OrderedDict(
      (
        artifact_id,
        record,
      )
      for artifact_id, record in self._replay_intent_alias_audit_export_artifacts.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._replay_intent_alias_audit_export_artifacts)

  def save_replay_intent_alias_audit_export_job(
    self,
    record: ReplayIntentAliasAuditExportJobRecord,
  ) -> ReplayIntentAliasAuditExportJobRecord:
    self._replay_intent_alias_audit_export_jobs[record.job_id] = record
    return record

  def get_replay_intent_alias_audit_export_job(
    self,
    job_id: str,
  ) -> ReplayIntentAliasAuditExportJobRecord | None:
    return self._replay_intent_alias_audit_export_jobs.get(job_id)

  def list_replay_intent_alias_audit_export_jobs(
    self,
  ) -> tuple[ReplayIntentAliasAuditExportJobRecord, ...]:
    return tuple(
      sorted(
        self._replay_intent_alias_audit_export_jobs.values(),
        key=lambda record: (record.created_at, record.job_id),
        reverse=True,
      )
    )

  def prune_replay_intent_alias_audit_export_jobs(self, current_time: datetime) -> int:
    original_count = len(self._replay_intent_alias_audit_export_jobs)
    self._replay_intent_alias_audit_export_jobs = OrderedDict(
      (
        job_id,
        record,
      )
      for job_id, record in self._replay_intent_alias_audit_export_jobs.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._replay_intent_alias_audit_export_jobs)

  def delete_replay_intent_alias_audit_export_jobs(self, job_ids: tuple[str, ...]) -> int:
    deleted_count = 0
    for job_id in job_ids:
      if job_id in self._replay_intent_alias_audit_export_jobs:
        deleted_count += 1
        del self._replay_intent_alias_audit_export_jobs[job_id]
    return deleted_count

  def save_replay_intent_alias_audit_export_job_audit_record(
    self,
    record: ReplayIntentAliasAuditExportJobAuditRecord,
  ) -> ReplayIntentAliasAuditExportJobAuditRecord:
    self._replay_intent_alias_audit_export_job_audit_records[record.audit_id] = record
    return record

  def list_replay_intent_alias_audit_export_job_audit_records(
    self,
    job_id: str | None = None,
  ) -> tuple[ReplayIntentAliasAuditExportJobAuditRecord, ...]:
    records = [
      record
      for record in self._replay_intent_alias_audit_export_job_audit_records.values()
      if job_id is None or record.job_id == job_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def delete_replay_intent_alias_audit_export_job_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    deleted_count = 0
    for audit_id in audit_ids:
      if audit_id in self._replay_intent_alias_audit_export_job_audit_records:
        deleted_count += 1
        del self._replay_intent_alias_audit_export_job_audit_records[audit_id]
    return deleted_count

  def prune_replay_intent_alias_audit_export_job_audit_records(self, current_time: datetime) -> int:
    original_count = len(self._replay_intent_alias_audit_export_job_audit_records)
    self._replay_intent_alias_audit_export_job_audit_records = OrderedDict(
      (
        audit_id,
        record,
      )
      for audit_id, record in self._replay_intent_alias_audit_export_job_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._replay_intent_alias_audit_export_job_audit_records)

  def save_provider_provenance_export_artifact(
    self,
    record: ProviderProvenanceExportArtifactRecord,
  ) -> ProviderProvenanceExportArtifactRecord:
    self._provider_provenance_export_artifacts[record.artifact_id] = record
    return record

  def get_provider_provenance_export_artifact(
    self,
    artifact_id: str,
  ) -> ProviderProvenanceExportArtifactRecord | None:
    return self._provider_provenance_export_artifacts.get(artifact_id)

  def delete_provider_provenance_export_artifacts(self, artifact_ids: tuple[str, ...]) -> int:
    deleted_count = 0
    for artifact_id in artifact_ids:
      if artifact_id in self._provider_provenance_export_artifacts:
        deleted_count += 1
        del self._provider_provenance_export_artifacts[artifact_id]
    return deleted_count

  def prune_provider_provenance_export_artifacts(self, current_time: datetime) -> int:
    original_count = len(self._provider_provenance_export_artifacts)
    self._provider_provenance_export_artifacts = OrderedDict(
      (
        artifact_id,
        record,
      )
      for artifact_id, record in self._provider_provenance_export_artifacts.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._provider_provenance_export_artifacts)

  def save_provider_provenance_export_job(
    self,
    record: ProviderProvenanceExportJobRecord,
  ) -> ProviderProvenanceExportJobRecord:
    self._provider_provenance_export_jobs[record.job_id] = record
    return record

  def get_provider_provenance_export_job(
    self,
    job_id: str,
  ) -> ProviderProvenanceExportJobRecord | None:
    return self._provider_provenance_export_jobs.get(job_id)

  def list_provider_provenance_export_jobs(
    self,
  ) -> tuple[ProviderProvenanceExportJobRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_export_jobs.values(),
        key=lambda record: (record.exported_at or record.created_at, record.job_id),
        reverse=True,
      )
    )

  def prune_provider_provenance_export_jobs(self, current_time: datetime) -> int:
    original_count = len(self._provider_provenance_export_jobs)
    self._provider_provenance_export_jobs = OrderedDict(
      (
        job_id,
        record,
      )
      for job_id, record in self._provider_provenance_export_jobs.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._provider_provenance_export_jobs)

  def delete_provider_provenance_export_jobs(self, job_ids: tuple[str, ...]) -> int:
    deleted_count = 0
    for job_id in job_ids:
      if job_id in self._provider_provenance_export_jobs:
        deleted_count += 1
        del self._provider_provenance_export_jobs[job_id]
    return deleted_count

  def save_provider_provenance_export_job_audit_record(
    self,
    record: ProviderProvenanceExportJobAuditRecord,
  ) -> ProviderProvenanceExportJobAuditRecord:
    self._provider_provenance_export_job_audit_records[record.audit_id] = record
    return record

  def list_provider_provenance_export_job_audit_records(
    self,
    job_id: str | None = None,
  ) -> tuple[ProviderProvenanceExportJobAuditRecord, ...]:
    records = [
      record
      for record in self._provider_provenance_export_job_audit_records.values()
      if job_id is None or record.job_id == job_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def delete_provider_provenance_export_job_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    deleted_count = 0
    for audit_id in audit_ids:
      if audit_id in self._provider_provenance_export_job_audit_records:
        deleted_count += 1
        del self._provider_provenance_export_job_audit_records[audit_id]
    return deleted_count

  def prune_provider_provenance_export_job_audit_records(self, current_time: datetime) -> int:
    original_count = len(self._provider_provenance_export_job_audit_records)
    self._provider_provenance_export_job_audit_records = OrderedDict(
      (
        audit_id,
        record,
      )
      for audit_id, record in self._provider_provenance_export_job_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    )
    return original_count - len(self._provider_provenance_export_job_audit_records)

  def save_provider_provenance_analytics_preset(
    self,
    record: ProviderProvenanceAnalyticsPresetRecord,
  ) -> ProviderProvenanceAnalyticsPresetRecord:
    self._provider_provenance_analytics_presets[record.preset_id] = record
    return record

  def list_provider_provenance_analytics_presets(
    self,
  ) -> tuple[ProviderProvenanceAnalyticsPresetRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_analytics_presets.values(),
        key=lambda record: (record.updated_at, record.preset_id),
        reverse=True,
      )
    )

  def get_provider_provenance_analytics_preset(
    self,
    preset_id: str,
  ) -> ProviderProvenanceAnalyticsPresetRecord | None:
    return self._provider_provenance_analytics_presets.get(preset_id)

  def save_provider_provenance_dashboard_view(
    self,
    record: ProviderProvenanceDashboardViewRecord,
  ) -> ProviderProvenanceDashboardViewRecord:
    self._provider_provenance_dashboard_views[record.view_id] = record
    return record

  def list_provider_provenance_dashboard_views(
    self,
  ) -> tuple[ProviderProvenanceDashboardViewRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_dashboard_views.values(),
        key=lambda record: (record.updated_at, record.view_id),
        reverse=True,
      )
    )

  def get_provider_provenance_dashboard_view(
    self,
    view_id: str,
  ) -> ProviderProvenanceDashboardViewRecord | None:
    return self._provider_provenance_dashboard_views.get(view_id)

  def save_provider_provenance_scheduler_stitched_report_view(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    self._provider_provenance_scheduler_stitched_report_views[record.view_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_views(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_views.values(),
        key=lambda record: (record.updated_at, record.view_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_view(
    self,
    view_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord | None:
    return self._provider_provenance_scheduler_stitched_report_views.get(view_id)

  def save_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord:
    self._provider_provenance_scheduler_stitched_report_view_revisions[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_view_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_view_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord | None:
    return self._provider_provenance_scheduler_stitched_report_view_revisions.get(revision_id)

  def save_provider_provenance_scheduler_stitched_report_view_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewAuditRecord:
    self._provider_provenance_scheduler_stitched_report_view_audit_records[record.audit_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_view_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_view_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    self._provider_provenance_scheduler_stitched_report_governance_registries[record.registry_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_registries(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registries.values(),
        key=lambda record: (record.updated_at, record.registry_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord | None:
    return self._provider_provenance_scheduler_stitched_report_governance_registries.get(
      registry_id
    )

  def save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord:
    self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records[record.audit_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_registry_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def save_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord:
    self._provider_provenance_scheduler_stitched_report_governance_registry_revisions[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_stitched_report_governance_registry_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registry_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord | None:
    return self._provider_provenance_scheduler_stitched_report_governance_registry_revisions.get(
      revision_id
    )

  def save_provider_provenance_scheduled_report(
    self,
    record: ProviderProvenanceScheduledReportRecord,
  ) -> ProviderProvenanceScheduledReportRecord:
    self._provider_provenance_scheduled_reports[record.report_id] = record
    return record

  def list_provider_provenance_scheduled_reports(
    self,
  ) -> tuple[ProviderProvenanceScheduledReportRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduled_reports.values(),
        key=lambda record: (record.updated_at, record.report_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduled_report(
    self,
    report_id: str,
  ) -> ProviderProvenanceScheduledReportRecord | None:
    return self._provider_provenance_scheduled_reports.get(report_id)

  def save_provider_provenance_scheduler_narrative_template(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    self._provider_provenance_scheduler_narrative_templates[record.template_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_templates(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_templates.values(),
        key=lambda record: (record.updated_at, record.template_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_template(
    self,
    template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord | None:
    return self._provider_provenance_scheduler_narrative_templates.get(template_id)

  def save_provider_provenance_scheduler_narrative_template_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord:
    self._provider_provenance_scheduler_narrative_template_revisions[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_template_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_template_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord | None:
    return self._provider_provenance_scheduler_narrative_template_revisions.get(revision_id)

  def save_provider_provenance_scheduler_narrative_registry_entry(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    self._provider_provenance_scheduler_narrative_registry[record.registry_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_registry_entries(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_registry.values(),
        key=lambda record: (record.updated_at, record.registry_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_registry_entry(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord | None:
    return self._provider_provenance_scheduler_narrative_registry.get(registry_id)

  def save_provider_provenance_scheduler_narrative_registry_revision(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord:
    self._provider_provenance_scheduler_narrative_registry_revisions[record.revision_id] = record
    return record

  def list_provider_provenance_scheduler_narrative_registry_revisions(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord, ...]:
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_registry_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def get_provider_provenance_scheduler_narrative_registry_revision(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord | None:
    return self._provider_provenance_scheduler_narrative_registry_revisions.get(revision_id)
