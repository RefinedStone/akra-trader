from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import json
from pathlib import Path
from typing import Any

import pytest

from akra_trader.adapters.binance import BinanceMarketDataAdapter
from akra_trader.adapters.guarded_live import SqlAlchemyGuardedLiveStateRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.sqlalchemy import SqlAlchemyExperimentPresetCatalog
from akra_trader.adapters.sqlalchemy import SqlAlchemyRunRepository
from akra_trader.adapters.venue_execution import SeededVenueExecutionAdapter
from akra_trader.application import get_run_subresource_contract
from akra_trader.application import get_run_subresource_runtime_binding
from akra_trader.application import list_run_subresource_contracts
from akra_trader.application import list_run_subresource_runtime_bindings
from akra_trader.application import list_standalone_surface_runtime_bindings
from akra_trader.application import execute_standalone_surface_binding
from akra_trader.application import serialize_standalone_surface_response
from akra_trader.application import TradingApplication
from akra_trader.application import serialize_run_surface_capabilities
from akra_trader.application import serialize_run_subresource_response
from akra_trader.domain.models import AssetType
from akra_trader.domain.models import BenchmarkArtifact
from akra_trader.domain.models import Candle
from akra_trader.domain.models import DatasetBoundaryContract
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import GuardedLiveBookTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveKlineChannelSnapshot
from akra_trader.domain.models import GuardedLiveOrderBookLevel
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import SyncFailure
from akra_trader.domain.models import WarmupSpec
from akra_trader.lineage import build_dataset_boundary_contract
from akra_trader.strategies.base import Strategy

from .application_test_support import AlwaysBuyStrategy
from .application_test_support import FakeExchange
from .application_test_support import FakeOperatorAlertDeliveryAdapter
from .application_test_support import MutableClock
from .application_test_support import MutableSeededMarketDataAdapter
from .application_test_support import StaticVenueStateAdapter
from .application_test_support import StatusOverrideSeededMarketDataAdapter
from .application_test_support import build_preset_catalog
from .application_test_support import build_runs_repository
from .application_test_support import without_surface_rule


def test_registered_strategy_run_records_lifecycle_timestamp(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  strategies = LocalStrategyCatalog()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=strategies,
    runs=runs,
  )

  app.register_strategy(
    strategy_id="ma_cross_v1",
    module_path="akra_trader.strategies.examples",
    class_name="MovingAverageCrossStrategy",
  )
  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
  )

  assert run.provenance.strategy is not None
  assert run.provenance.strategy.lifecycle.registered_at is not None
  assert run.provenance.strategy.catalog_semantics.strategy_kind == "imported_module"
  assert run.provenance.strategy.catalog_semantics.source_descriptor == (
    "akra_trader.strategies.examples:MovingAverageCrossStrategy"
  )
  assert run.provenance.strategy.parameter_snapshot.requested == {"short_window": 13}
  assert run.provenance.strategy.parameter_snapshot.resolved == {
    "short_window": 13,
    "long_window": 21,
  }

def test_list_runs_can_filter_by_strategy_metadata(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  filtered = app.list_runs(
    mode="backtest",
    strategy_id="ma_cross_v1",
    strategy_version="1.0.0",
  )

  assert len(filtered) == 1
  assert filtered[0].config.strategy_id == "ma_cross_v1"
  assert filtered[0].config.strategy_version == "1.0.0"

def test_run_experiment_metadata_is_durable_queryable_and_preserved_for_reruns(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=presets,
    runs=runs,
  )
  app.create_preset(
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    benchmark_family="native_validation",
    parameters={"short_window": 5, "long_window": 13},
  )
  app.create_preset(
    name="Tuned 5m",
    preset_id="tuned_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    benchmark_family="native_tuning",
  )

  baseline = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    tags=("baseline", "momentum"),
    preset_id="core_5m",
    benchmark_family="native_validation",
  )
  app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
    tags=("alternate",),
    preset_id="tuned_5m",
    benchmark_family="native_tuning",
  )

  assert baseline.provenance.market_data is not None

  filtered = app.list_runs(
    mode="backtest",
    preset_id="core_5m",
    benchmark_family="native_validation",
    dataset_identity=baseline.provenance.market_data.dataset_identity,
    tags=("baseline", "momentum"),
  )

  assert [run.config.run_id for run in filtered] == [baseline.config.run_id]

  reloaded = build_runs_repository(tmp_path).get_run(baseline.config.run_id)

  assert reloaded is not None
  assert reloaded.provenance.experiment.preset_id == "core_5m"
  assert reloaded.provenance.experiment.benchmark_family == "native_validation"
  assert reloaded.provenance.experiment.tags == ("baseline", "momentum")

  rerun = app.rerun_backtest_from_boundary(rerun_boundary_id=baseline.provenance.rerun_boundary_id)

  assert rerun.provenance.experiment == baseline.provenance.experiment

def test_preset_parameter_bundle_applies_and_request_parameters_override(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=presets,
    runs=runs,
  )
  app.create_preset(
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    parameters={"short_window": 5, "long_window": 13},
  )

  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"long_window": 21},
    preset_id="core_5m",
  )

  assert run.config.parameters == {"short_window": 5, "long_window": 21}
  assert run.provenance.strategy is not None
  assert run.provenance.strategy.parameter_snapshot.requested == {"short_window": 5, "long_window": 21}
  assert run.provenance.strategy.parameter_snapshot.resolved == {"short_window": 5, "long_window": 21}

def test_preset_lifecycle_actions_are_durable(tmp_path: Path) -> None:
  presets = build_preset_catalog(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=presets,
    runs=build_runs_repository(tmp_path),
  )
  created = app.create_preset(
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    parameters={"short_window": 5, "long_window": 13},
  )

  assert created.lifecycle.stage == "draft"

  promoted = app.apply_preset_lifecycle_action(
    preset_id="core_5m",
    action="promote",
    actor="operator",
    reason="benchmark_candidate_ready",
    lineage_evidence_pack_id="operator-lineage-drill-pack:promotion",
    lineage_evidence_retention_expires_at=datetime(2025, 12, 28, tzinfo=UTC),
    lineage_evidence_summary="exact-match / accepted; 1 lineage snapshot(s); 1 ingestion job(s)",
  )
  archived = app.apply_preset_lifecycle_action(
    preset_id="core_5m",
    action="archive",
    actor="operator",
    reason="superseded_by_v2",
  )
  restored = app.apply_preset_lifecycle_action(
    preset_id="core_5m",
    action="restore",
    actor="operator",
    reason="reopening_research_path",
  )
  reloaded = build_preset_catalog(tmp_path).get_preset("core_5m")

  assert promoted.lifecycle.stage == "benchmark_candidate"
  assert promoted.lifecycle.history[-1].lineage_evidence_pack_id == "operator-lineage-drill-pack:promotion"
  assert promoted.lifecycle.history[-1].lineage_evidence_retention_expires_at == datetime(2025, 12, 28, tzinfo=UTC)
  assert (
    promoted.lifecycle.history[-1].lineage_evidence_summary
    == "exact-match / accepted; 1 lineage snapshot(s); 1 ingestion job(s)"
  )
  assert archived.lifecycle.stage == "archived"
  assert restored.lifecycle.stage == "draft"
  assert reloaded is not None
  assert reloaded.parameters == {"short_window": 5, "long_window": 13}
  assert reloaded.lifecycle.stage == "draft"
  assert [event.action for event in reloaded.lifecycle.history] == [
    "created",
    "promote",
    "archive",
    "restore",
  ]
  assert reloaded.lifecycle.history[1].lineage_evidence_pack_id == "operator-lineage-drill-pack:promotion"
  assert reloaded.lifecycle.history[1].lineage_evidence_retention_expires_at == datetime(
    2025,
    12,
    28,
    tzinfo=UTC,
  )
  assert (
    reloaded.lifecycle.history[1].lineage_evidence_summary
    == "exact-match / accepted; 1 lineage snapshot(s); 1 ingestion job(s)"
  )

def test_preset_update_creates_durable_revision_entries(tmp_path: Path) -> None:
  presets = build_preset_catalog(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=presets,
    runs=build_runs_repository(tmp_path),
  )
  created = app.create_preset(
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    parameters={"short_window": 5, "long_window": 13},
    tags=("baseline",),
  )

  updated = app.update_preset(
    preset_id="core_5m",
    changes={
      "description": "Expanded validation bundle",
      "benchmark_family": "native_validation",
      "tags": ["baseline", "momentum"],
      "parameters": {"short_window": 7, "long_window": 21},
    },
    actor="operator",
    reason="tighten_signal_bundle",
  )
  revisions = app.list_preset_revisions(preset_id="core_5m")
  reloaded = build_preset_catalog(tmp_path).get_preset("core_5m")

  assert created.revisions[0].revision_id == "core_5m:r0001"
  assert updated.revisions[-1].revision_id == "core_5m:r0002"
  assert updated.description == "Expanded validation bundle"
  assert updated.benchmark_family == "native_validation"
  assert updated.tags == ("baseline", "momentum")
  assert updated.parameters == {"short_window": 7, "long_window": 21}
  assert revisions[0].revision_id == "core_5m:r0002"
  assert revisions[0].action == "updated"
  assert revisions[0].reason == "tighten_signal_bundle"
  assert reloaded is not None
  assert [revision.revision_id for revision in reloaded.revisions] == [
    "core_5m:r0001",
    "core_5m:r0002",
  ]

def test_preset_revision_restore_reinstates_prior_bundle(tmp_path: Path) -> None:
  presets = build_preset_catalog(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=presets,
    runs=build_runs_repository(tmp_path),
  )
  app.create_preset(
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    parameters={"short_window": 5, "long_window": 13},
    tags=("baseline",),
  )
  app.update_preset(
    preset_id="core_5m",
    changes={
      "benchmark_family": "native_validation",
      "tags": ["baseline", "momentum"],
      "parameters": {"short_window": 7, "long_window": 21},
    },
    actor="operator",
    reason="tighten_signal_bundle",
  )

  restored = app.restore_preset_revision(
    preset_id="core_5m",
    revision_id="core_5m:r0001",
    actor="operator",
    reason="revert_to_baseline",
  )
  reloaded = build_preset_catalog(tmp_path).get_preset("core_5m")

  assert restored.parameters == {"short_window": 5, "long_window": 13}
  assert restored.tags == ("baseline",)
  assert restored.benchmark_family is None
  assert restored.revisions[-1].revision_id == "core_5m:r0003"
  assert restored.revisions[-1].action == "restored"
  assert restored.revisions[-1].source_revision_id == "core_5m:r0001"
  assert reloaded is not None
  assert reloaded.parameters == {"short_window": 5, "long_window": 13}
  assert [revision.action for revision in reloaded.revisions] == [
    "created",
    "updated",
    "restored",
  ]

def test_archived_preset_cannot_launch_run(tmp_path: Path) -> None:
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=build_preset_catalog(tmp_path),
    runs=build_runs_repository(tmp_path),
  )
  app.create_preset(
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
  )
  app.apply_preset_lifecycle_action(
    preset_id="core_5m",
    action="archive",
    actor="operator",
    reason="superseded",
  )

  with pytest.raises(ValueError, match="archived and cannot be launched"):
    app.run_backtest(
      strategy_id="ma_cross_v1",
      symbol="BTC/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      preset_id="core_5m",
    )

def test_run_backtest_requires_cataloged_preset(tmp_path: Path) -> None:
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=build_runs_repository(tmp_path),
  )

  with pytest.raises(ValueError, match="Preset not found: missing_preset"):
    app.run_backtest(
      strategy_id="ma_cross_v1",
      symbol="BTC/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      preset_id="missing preset",
    )

def test_list_runs_can_filter_paper_history_separately_from_sandbox(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  sandbox_run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )
  paper_run = app.start_paper_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  sandbox_filtered = app.list_runs(mode="sandbox")
  paper_filtered = app.list_runs(mode="paper")

  assert [run.config.run_id for run in sandbox_filtered] == [sandbox_run.config.run_id]
  assert [run.config.run_id for run in paper_filtered] == [paper_run.config.run_id]

def test_list_runs_can_filter_by_rerun_boundary_id(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  first = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  second = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  other = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=5,
    parameters={},
  )

  filtered = app.list_runs(rerun_boundary_id=first.provenance.rerun_boundary_id)

  assert [run.config.run_id for run in filtered] == [second.config.run_id, first.config.run_id]
  assert other.config.run_id not in [run.config.run_id for run in filtered]

def test_rerun_backtest_from_boundary_uses_stored_effective_window_and_records_match(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  source = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    start_at=datetime(2025, 1, 1, 4, 0, tzinfo=UTC),
    end_at=datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
  )

  rerun = app.rerun_backtest_from_boundary(rerun_boundary_id=source.provenance.rerun_boundary_id)

  assert rerun.config.run_id != source.config.run_id
  assert rerun.provenance.rerun_source_run_id == source.config.run_id
  assert rerun.provenance.rerun_target_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.rerun_match_status == "matched"
  assert rerun.provenance.rerun_validation_category == "exact_match"
  assert rerun.provenance.rerun_validation_summary == (
    "Exact dataset boundary matched the stored rerun boundary."
  )
  assert rerun.provenance.rerun_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.market_data is not None
  assert rerun.provenance.market_data.effective_start_at == source.provenance.market_data.effective_start_at
  assert rerun.provenance.market_data.effective_end_at == source.provenance.market_data.effective_end_at
  assert rerun.notes[0].startswith("Explicit backtest rerun from boundary ")
  assert rerun.notes[-1] == "Exact dataset boundary matched the stored rerun boundary."

def test_rerun_backtest_from_boundary_rejects_when_control_surface_rule_is_disabled(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  source = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  base_capabilities = app.get_run_surface_capabilities()
  app.get_run_surface_capabilities = lambda: without_surface_rule(
    base_capabilities,
    family_key="execution_controls",
    surface_key="rerun_and_stop_controls",
  )

  with pytest.raises(ValueError, match="Surface rule rerun_and_stop_controls is disabled"):
    app.rerun_backtest_from_boundary(rerun_boundary_id=source.provenance.rerun_boundary_id)

def test_rerun_backtest_from_boundary_uses_resolved_strategy_parameters(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  source = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
  )

  rerun = app.rerun_backtest_from_boundary(rerun_boundary_id=source.provenance.rerun_boundary_id)

  assert rerun.config.parameters == {"short_window": 13, "long_window": 21}
  assert rerun.provenance.strategy is not None
  assert rerun.provenance.strategy.parameter_snapshot.requested == {"short_window": 13, "long_window": 21}
  assert rerun.provenance.strategy.parameter_snapshot.resolved == {"short_window": 13, "long_window": 21}

def test_rerun_sandbox_from_boundary_uses_stored_effective_window_and_replays_same_mode_boundary(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  source = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  rerun = app.rerun_sandbox_from_boundary(rerun_boundary_id=source.provenance.rerun_boundary_id)

  assert rerun.config.run_id != source.config.run_id
  assert rerun.config.mode == RunMode.SANDBOX
  assert rerun.status == RunStatus.RUNNING
  assert rerun.provenance.rerun_source_run_id == source.config.run_id
  assert rerun.provenance.rerun_target_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.rerun_match_status == "matched"
  assert rerun.provenance.rerun_validation_category == "exact_match"
  assert rerun.provenance.rerun_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.market_data is not None
  assert rerun.provenance.market_data.effective_start_at == source.provenance.market_data.effective_start_at
  assert rerun.provenance.market_data.effective_end_at == source.provenance.market_data.effective_end_at
  assert rerun.provenance.runtime_session is not None
  assert rerun.notes[0].startswith("Explicit sandbox rerun from boundary ")
  assert rerun.notes[1] == "Sandbox rerun restored the stored worker-session priming window."
  assert rerun.notes[-1] == "Exact dataset boundary matched the stored rerun boundary."

def test_rerun_paper_from_boundary_uses_stored_effective_window_and_replays_same_mode_boundary(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  source = app.start_paper_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  rerun = app.rerun_paper_from_boundary(rerun_boundary_id=source.provenance.rerun_boundary_id)

  assert rerun.config.run_id != source.config.run_id
  assert rerun.config.mode == RunMode.PAPER
  assert rerun.status == RunStatus.RUNNING
  assert rerun.provenance.rerun_source_run_id == source.config.run_id
  assert rerun.provenance.rerun_target_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.rerun_match_status == "matched"
  assert rerun.provenance.rerun_validation_category == "exact_match"
  assert rerun.provenance.rerun_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.notes[0].startswith("Explicit paper rerun from boundary ")
  assert rerun.notes[1] == "Paper rerun seeded the current paper session from the stored priming window."
  assert rerun.notes[-1] == "Exact dataset boundary matched the stored rerun boundary."

def test_rerun_paper_from_backtest_boundary_records_expected_mode_drift(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  source = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
    start_at=datetime(2025, 1, 1, 4, 0, tzinfo=UTC),
    end_at=datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
  )

  rerun = app.rerun_paper_from_boundary(rerun_boundary_id=source.provenance.rerun_boundary_id)

  assert rerun.config.mode == RunMode.PAPER
  assert rerun.status == RunStatus.RUNNING
  assert rerun.provenance.rerun_source_run_id == source.config.run_id
  assert rerun.provenance.rerun_target_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.rerun_match_status == "drifted"
  assert rerun.provenance.rerun_validation_category == "mode_translation"
  assert rerun.provenance.rerun_validation_summary == (
    "Dataset boundary matched, but the rerun translated it into a different execution mode."
  )
  assert rerun.provenance.market_data is not None
  assert rerun.provenance.market_data.effective_start_at == source.provenance.market_data.effective_start_at
  assert rerun.provenance.market_data.effective_end_at == source.provenance.market_data.effective_end_at
  assert rerun.provenance.strategy is not None
  assert rerun.provenance.strategy.parameter_snapshot.resolved == {"short_window": 13, "long_window": 21}
  assert rerun.notes[0].startswith("Explicit paper rerun from boundary ")
  assert rerun.notes[1] == "Paper rerun seeded the current paper session from the stored effective market-data window."
  assert rerun.notes[-1] == (
    "Dataset boundary matched, but the rerun translated it into a different execution mode."
  )

def test_compare_runs_uses_strategy_semantics_to_break_close_ranking_ties(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  strategies = LocalStrategyCatalog()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=strategies,
    runs=runs,
  )

  baseline_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  alternate_native_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
  )
  app.register_strategy(
    strategy_id="ma_cross_v1",
    module_path="akra_trader.strategies.examples",
    class_name="MovingAverageCrossStrategy",
  )
  imported_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="SOL/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
  )

  for run in (baseline_run, alternate_native_run, imported_run):
    run.metrics.update({
      "total_return_pct": 10.0,
      "max_drawdown_pct": 5.0,
      "win_rate_pct": 60.0,
      "trade_count": 20,
    })
    runs.save_run(run)

  comparison = app.compare_runs(
    run_ids=[
      baseline_run.config.run_id,
      alternate_native_run.config.run_id,
      imported_run.config.run_id,
    ],
    intent="strategy_tuning",
  )

  assert [narrative.run_id for narrative in comparison.narratives] == [
    imported_run.config.run_id,
    alternate_native_run.config.run_id,
  ]
  narrative_by_run = {
    narrative.run_id: narrative
    for narrative in comparison.narratives
  }
  assert imported_run.provenance.strategy is not None
  assert imported_run.provenance.strategy.catalog_semantics.strategy_kind == "imported_module"
  assert narrative_by_run[imported_run.config.run_id].comparison_type == "native_vs_native"
  assert narrative_by_run[imported_run.config.run_id].insight_score > 0
  assert narrative_by_run[alternate_native_run.config.run_id].insight_score > 0
  assert (
    narrative_by_run[imported_run.config.run_id].insight_score
    > narrative_by_run[alternate_native_run.config.run_id].insight_score
  )

def test_backtest_failure_still_records_requested_market_lineage(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    start_at=datetime(2030, 1, 1, tzinfo=UTC),
  )

  assert run.status == RunStatus.FAILED
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.dataset_identity is None
  assert run.provenance.market_data.sync_checkpoint_id is None
  assert run.provenance.market_data.reproducibility_state == "range_only"
  window_boundary = build_dataset_boundary_contract(lineage=run.provenance.market_data)
  assert window_boundary is not None
  assert window_boundary.validation_claim == "window_only"
  assert window_boundary.boundary_id is None
  assert run.provenance.market_data.requested_start_at == datetime(2030, 1, 1, tzinfo=UTC)
  assert run.provenance.market_data.candle_count == 0
  assert run.provenance.rerun_boundary_id is not None
  assert run.provenance.rerun_boundary_state == "range_only"

def test_multi_symbol_run_records_market_lineage_per_symbol(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )
  config = RunConfig(
    run_id="multi-symbol-lineage",
    mode=RunMode.BACKTEST,
    strategy_id="ma_cross_v1",
    strategy_version="1.0.0",
    venue="binance",
    symbols=("BTC/USDT", "ETH/USDT"),
    timeframe="5m",
    parameters={},
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
  )

  run = app._simulate_run(config=config, active_bars=24)
  runs.save_run(run)
  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)

  assert run.provenance.market_data is not None
  assert run.provenance.market_data.symbols == ("BTC/USDT", "ETH/USDT")
  assert run.provenance.market_data.candle_count == 48
  assert run.provenance.market_data.dataset_identity is not None
  assert run.provenance.market_data.sync_checkpoint_id is None
  assert run.provenance.market_data.reproducibility_state == "pinned"
  assert run.provenance.market_data.sync_status == "fixture"
  assert run.provenance.rerun_boundary_id is not None
  assert run.provenance.rerun_boundary_state == "pinned"
  assert run.provenance.market_data_by_symbol["BTC/USDT"].symbols == ("BTC/USDT",)
  assert run.provenance.market_data_by_symbol["BTC/USDT"].candle_count == 24
  assert run.provenance.market_data_by_symbol["BTC/USDT"].dataset_identity is not None
  assert run.provenance.market_data_by_symbol["BTC/USDT"].sync_checkpoint_id is None
  assert run.provenance.market_data_by_symbol["BTC/USDT"].reproducibility_state == "pinned"
  assert run.provenance.market_data_by_symbol["ETH/USDT"].symbols == ("ETH/USDT",)
  assert run.provenance.market_data_by_symbol["ETH/USDT"].candle_count == 24
  assert run.provenance.market_data_by_symbol["ETH/USDT"].dataset_identity is not None
  assert run.provenance.market_data_by_symbol["ETH/USDT"].sync_checkpoint_id is None
  assert run.provenance.market_data_by_symbol["ETH/USDT"].reproducibility_state == "pinned"
  assert reloaded is not None
  assert reloaded.provenance.market_data_by_symbol == run.provenance.market_data_by_symbol
