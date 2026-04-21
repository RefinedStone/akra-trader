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


def build_seeded_market_data() -> dict[str, list[Candle]]:
  instruments = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
  start = datetime(2025, 1, 1, tzinfo=UTC)
  series: dict[str, list[Candle]] = {}
  for offset, symbol in enumerate(instruments):
    candles: list[Candle] = []
    price = 40_000.0 / (offset + 1)
    for index in range(240):
      timestamp = start + timedelta(minutes=5 * index)
      drift = 1 + (0.0008 * (index / 8))
      cycle = ((index % 24) - 12) / 280
      open_price = price
      close_price = price * drift + price * cycle
      high_price = max(open_price, close_price) * 1.004
      low_price = min(open_price, close_price) * 0.996
      volume = 500 + (index * 3) + (offset * 15)
      candles.append(
        Candle(
          timestamp=timestamp,
          open=round(open_price, 2),
          high=round(high_price, 2),
          low=round(low_price, 2),
          close=round(close_price, 2),
          volume=round(volume, 2),
        )
      )
      price = close_price
    series[symbol] = candles
  return series


class SeededMarketDataAdapter(MarketDataPort):
  def __init__(self, venue: str = "binance") -> None:
    self._venue = venue
    self._candles = build_seeded_market_data()
    self._instruments = [
      Instrument(
        symbol=symbol,
        venue=venue,
        base_currency=symbol.split("/")[0],
        quote_currency=symbol.split("/")[1],
        asset_type=AssetType.CRYPTO,
        market_type=MarketType.SPOT,
      )
      for symbol in self._candles
    ]

  def list_instruments(self) -> list[Instrument]:
    return list(self._instruments)

  def get_candles(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> list[Candle]:
    candles = list(self._candles.get(symbol, ()))
    if start_at is not None:
      candles = [candle for candle in candles if candle.timestamp >= start_at]
    if end_at is not None:
      candles = [candle for candle in candles if candle.timestamp <= end_at]
    if limit is not None:
      candles = candles[-limit:]
    return candles

  def get_status(self, timeframe: str) -> MarketDataStatus:
    instruments = []
    for symbol, candles in self._candles.items():
      first = candles[0].timestamp if candles else None
      last = candles[-1].timestamp if candles else None
      instruments.append(
        InstrumentStatus(
          instrument_id=f"{self._venue}:{symbol}",
          timeframe=timeframe,
          candle_count=len(candles),
          first_timestamp=first,
          last_timestamp=last,
        )
      )
    return MarketDataStatus(provider="seeded", venue=self._venue, instruments=instruments)

  def list_lineage_history(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataLineageHistoryRecord, ...]:
    resolved_timeframe = timeframe or "5m"
    records: list[MarketDataLineageHistoryRecord] = []
    status = self.get_status(resolved_timeframe)
    for instrument in status.instruments:
      resolved_symbol = instrument.instrument_id.split(":", 1)[-1]
      if symbol is not None and resolved_symbol != symbol:
        continue
      candles = self.get_candles(symbol=resolved_symbol, timeframe=resolved_timeframe)
      lineage = self.describe_lineage(
        symbol=resolved_symbol,
        timeframe=resolved_timeframe,
        candles=candles,
      )
      dataset_boundary = build_dataset_boundary_contract(lineage=lineage)
      claim = dataset_boundary.validation_claim if dataset_boundary is not None else "window_only"
      if sync_status is not None and lineage.sync_status != sync_status:
        continue
      if validation_claim is not None and claim != validation_claim:
        continue
      recorded_at = candles[-1].timestamp if candles else datetime.now(UTC)
      records.append(
        MarketDataLineageHistoryRecord(
          history_id=f"seeded-lineage:{self._venue}:{resolved_symbol}:{resolved_timeframe}",
          source_job_id=None,
          provider="seeded",
          venue=self._venue,
          symbol=resolved_symbol,
          timeframe=resolved_timeframe,
          recorded_at=recorded_at,
          sync_status=lineage.sync_status,
          validation_claim=claim,
          reproducibility_state=lineage.reproducibility_state,
          boundary_id=dataset_boundary.boundary_id if dataset_boundary is not None else None,
          checkpoint_id=lineage.sync_checkpoint_id,
          dataset_boundary=dataset_boundary,
          first_timestamp=lineage.effective_start_at,
          last_timestamp=lineage.effective_end_at,
          candle_count=lineage.candle_count,
          lag_seconds=0 if candles else None,
          last_sync_at=recorded_at if candles else None,
          failure_count_24h=0,
          contiguous_missing_candles=0 if candles else None,
          gap_window_count=0,
          last_error=None,
          issues=lineage.issues,
        )
      )
    records.sort(key=lambda record: (record.recorded_at, record.history_id), reverse=True)
    if limit is not None:
      records = records[:limit]
    return tuple(records)

  def list_ingestion_jobs(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataIngestionJobRecord, ...]:
    del timeframe, symbol, operation, status, limit
    return ()

  def describe_lineage(
    self,
    *,
    symbol: str,
    timeframe: str,
    candles: list[Candle],
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> MarketDataLineage:
    issues: list[str] = []
    if limit is not None and len(candles) < limit:
      issues.append("insufficient_fixture_coverage")
    dataset_identity = None
    reproducibility_state = "range_only"
    if candles:
      dataset_identity = build_candle_dataset_identity(
        provider="seeded",
        venue=self._venue,
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
      )
      reproducibility_state = "pinned"
    return MarketDataLineage(
      provider="seeded",
      venue=self._venue,
      symbols=(symbol,),
      timeframe=timeframe,
      dataset_identity=dataset_identity,
      sync_checkpoint_id=None,
      reproducibility_state=reproducibility_state,
      requested_start_at=start_at,
      requested_end_at=end_at,
      effective_start_at=candles[0].timestamp if candles else None,
      effective_end_at=candles[-1].timestamp if candles else None,
      candle_count=len(candles),
      sync_status="fixture",
      issues=tuple(issues),
    )

  def remediate(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
  ) -> MarketDataRemediationResult:
    current_time = datetime.now(UTC)
    return MarketDataRemediationResult(
      kind=kind,
      symbol=symbol,
      timeframe=timeframe,
      status="skipped",
      started_at=current_time,
      finished_at=current_time,
      detail="seeded_market_data_provider_has_no_live_remediation_jobs",
    )


class InMemoryRunRepository(RunRepositoryPort):
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
    self._provider_provenance_scheduler_narrative_governance_policy_template_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_catalogs: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduler_narrative_governance_plans: OrderedDict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
    ] = OrderedDict()
    self._provider_provenance_scheduled_report_audit_records: OrderedDict[str, ProviderProvenanceScheduledReportAuditRecord] = OrderedDict()
    self._provider_provenance_scheduler_health_records: OrderedDict[str, ProviderProvenanceSchedulerHealthRecord] = OrderedDict()
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

  def load_replay_intent_alias_signing_secret(self) -> str | None:
    return self._replay_intent_alias_signing_secret

  def save_replay_intent_alias_signing_secret(self, secret: str) -> str:
    self._replay_intent_alias_signing_secret = secret
    return secret


class InMemoryExperimentPresetCatalog(ExperimentPresetCatalogPort):
  def __init__(self) -> None:
    self._presets: OrderedDict[str, ExperimentPreset] = OrderedDict()

  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    presets = list(reversed(self._presets.values()))
    if strategy_id is not None:
      presets = [
        preset
        for preset in presets
        if preset.strategy_id is None or preset.strategy_id == strategy_id
      ]
    if timeframe is not None:
      presets = [
        preset
        for preset in presets
        if preset.timeframe is None or preset.timeframe == timeframe
      ]
    if lifecycle_stage is not None:
      presets = [
        preset
        for preset in presets
        if preset.lifecycle.stage == lifecycle_stage
      ]
    return presets

  def get_preset(self, preset_id: str) -> ExperimentPreset | None:
    return self._presets.get(preset_id)

  def save_preset(self, preset: ExperimentPreset) -> ExperimentPreset:
    self._presets[preset.preset_id] = preset
    return preset


class LocalStrategyCatalog(StrategyCatalogPort):
  def __init__(self, builtins: Iterable[type[Strategy]] | None = None) -> None:
    builtin_factories: dict[str, callable] = {}
    for strategy in (builtins or (MovingAverageCrossStrategy,)):
      metadata = strategy().describe()
      builtin_factories[metadata.strategy_id] = strategy
    for strategy in build_reference_strategies():
      builtin_factories[strategy.describe().strategy_id] = strategy.__class__
    self._builtins = builtin_factories
    self._references = {strategy.describe().strategy_id: strategy for strategy in build_reference_strategies()}
    self._registrations: dict[str, StrategyRegistration] = {}

  def list_strategies(
    self,
    *,
    runtime: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    metadata_by_strategy_id = {
      strategy_id: self._describe_strategy(strategy_id)
      for strategy_id in self._builtins
    }
    for strategy_id in self._registrations:
      metadata_by_strategy_id[strategy_id] = self._describe_strategy(strategy_id)

    metadata = list(metadata_by_strategy_id.values())
    if runtime is not None:
      metadata = [item for item in metadata if item.runtime == runtime]
    if lifecycle_stage is not None:
      metadata = [item for item in metadata if item.lifecycle.stage == lifecycle_stage]
    if version is not None:
      metadata = [
        item
        for item in metadata
        if item.version == version or version in (item.version_lineage or (item.version,))
      ]
    return sorted(metadata, key=lambda item: item.strategy_id)

  def load(self, strategy_id: str) -> Strategy:
    if strategy_id in self._references:
      return self._references[strategy_id]
    if strategy_id in self._builtins:
      return self._builtins[strategy_id]()
    registration = self._registrations[strategy_id]
    module = import_module(registration.module_path)
    strategy_cls = getattr(module, registration.class_name)
    return strategy_cls()

  def register(self, registration: StrategyRegistration) -> StrategyMetadata:
    module = import_module(registration.module_path)
    strategy_cls = getattr(module, registration.class_name)
    strategy = strategy_cls()
    self._registrations[registration.strategy_id] = registration
    return self._apply_registration_metadata(strategy.describe())

  def get_registration(self, strategy_id: str) -> StrategyRegistration | None:
    return self._registrations.get(strategy_id)

  def _describe_strategy(self, strategy_id: str) -> StrategyMetadata:
    if strategy_id in self._references:
      metadata = self._references[strategy_id].describe()
    elif strategy_id in self._builtins:
      metadata = self._builtins[strategy_id]().describe()
    else:
      metadata = self.load(strategy_id).describe()
    return self._apply_registration_metadata(metadata)

  def _apply_registration_metadata(self, metadata: StrategyMetadata) -> StrategyMetadata:
    registration = self._registrations.get(metadata.strategy_id)
    if registration is None or metadata.lifecycle.registered_at is not None:
      return metadata
    base_semantics = metadata.catalog_semantics
    parameter_contract = (
      base_semantics.parameter_contract
      or (
        "Publishes a typed parameter schema for presets and semantic diffs."
        if metadata.parameter_schema
        else "Does not advertise a typed parameter schema; presets can only store freeform parameters."
      )
    )
    operator_notes = tuple(dict.fromkeys((*base_semantics.operator_notes, "Imported from a locally registered module path.")))
    return replace(
      metadata,
      lifecycle=replace(metadata.lifecycle, registered_at=registration.registered_at),
      catalog_semantics=StrategyCatalogSemantics(
        strategy_kind="imported_module",
        execution_model=(
          base_semantics.execution_model
          or "Loaded from a locally registered module and executed through the declared runtime."
        ),
        parameter_contract=parameter_contract,
        source_descriptor=f"{registration.module_path}:{registration.class_name}",
        operator_notes=operator_notes,
      ),
    )


def candles_to_frame(candles: list[Candle]) -> pd.DataFrame:
  return pd.DataFrame(
    [
      {
        "timestamp": candle.timestamp,
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
      }
      for candle in candles
    ]
  )
