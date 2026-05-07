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
    self._builtins = builtin_factories
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
    if strategy_id in self._builtins:
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
