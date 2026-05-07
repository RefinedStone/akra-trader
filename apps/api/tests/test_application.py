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
from .application_test_support import build_guarded_live_repository
from .application_test_support import build_preset_catalog
from .application_test_support import build_runs_repository
from .application_test_support import without_surface_rule


def test_backtest_creates_completed_run_with_metrics(tmp_path: Path) -> None:
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
  )

  assert run.status == RunStatus.COMPLETED
  assert run.metrics["initial_cash"] == 10_000
  assert "total_return_pct" in run.metrics
  assert run.config.strategy_id == "ma_cross_v1"
  assert run.provenance.strategy is not None
  assert run.provenance.strategy.strategy_id == "ma_cross_v1"
  assert run.provenance.strategy.lifecycle.stage == "active"
  assert run.provenance.strategy.catalog_semantics.strategy_kind == "standard"
  assert run.provenance.strategy.catalog_semantics.execution_model == ""
  assert run.provenance.strategy.parameter_snapshot.requested == {}
  assert run.provenance.strategy.parameter_snapshot.resolved == {
    "short_window": 8,
    "long_window": 21,
  }
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.provider == "seeded"
  assert run.provenance.market_data.candle_count > 0
  assert run.provenance.market_data.dataset_identity is not None
  assert run.provenance.market_data.dataset_identity.startswith("dataset-v1:")
  assert run.provenance.market_data.sync_checkpoint_id is None
  assert run.provenance.market_data.reproducibility_state == "pinned"
  assert run.provenance.market_data.sync_status == "fixture"
  assert run.provenance.rerun_boundary_id is not None
  assert run.provenance.rerun_boundary_id.startswith("rerun-v1:")
  assert run.provenance.rerun_boundary_state == "pinned"

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.COMPLETED
  assert reloaded.metrics == run.metrics
  assert reloaded.provenance.strategy == run.provenance.strategy
  assert reloaded.provenance.market_data == run.provenance.market_data


def test_backtest_dataset_identity_is_stable_for_matching_data_boundaries(tmp_path: Path) -> None:
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
    initial_cash=5_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
  )
  bounded = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    start_at=datetime(2025, 1, 1, 6, 0, tzinfo=UTC),
  )

  first_identity = first.provenance.market_data.dataset_identity
  second_identity = second.provenance.market_data.dataset_identity
  bounded_identity = bounded.provenance.market_data.dataset_identity

  assert first_identity is not None
  assert first_identity == second_identity
  assert bounded_identity is not None
  assert bounded_identity != first_identity


def test_backtest_rerun_boundary_is_stable_only_for_matching_execution_inputs(tmp_path: Path) -> None:
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
  changed_cash = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=12_500,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  assert first.provenance.rerun_boundary_id is not None
  assert first.provenance.rerun_boundary_id == second.provenance.rerun_boundary_id
  assert changed_cash.provenance.rerun_boundary_id != first.provenance.rerun_boundary_id


def test_backtest_provenance_links_directly_to_binance_sync_checkpoint(tmp_path: Path) -> None:
  now = datetime(2025, 1, 2, 0, 0, tzinfo=UTC)
  rows = [
    [
      int((now - timedelta(minutes=25 - (index * 5))).timestamp() * 1000),
      100 + index,
      101 + index,
      99 + index,
      100.5 + index,
      10 + index,
    ]
    for index in range(6)
  ]
  market_data = BinanceMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market-data.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange=FakeExchange({("BTC/USDT", "5m"): rows}),
    default_candle_limit=6,
    historical_candle_limit=6,
    clock=lambda: now,
  )
  market_data.sync_tracked("5m")
  status = market_data.get_status("5m")
  checkpoint = status.instruments[0].sync_checkpoint
  assert checkpoint is not None

  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=build_runs_repository(tmp_path),
  )

  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  assert run.provenance.market_data is not None
  assert run.provenance.market_data.sync_checkpoint_id is not None
  assert run.provenance.market_data.sync_checkpoint_id.startswith("checkpoint-group-v1:")
  assert run.provenance.market_data_by_symbol["BTC/USDT"].sync_checkpoint_id == checkpoint.checkpoint_id
  assert run.provenance.rerun_boundary_state == "pinned"
  assert run.provenance.rerun_boundary_id is not None


def test_sandbox_run_is_created_as_running(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 0, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=48,
  )

  assert run.status == RunStatus.RUNNING
  assert run.config.mode.value == "sandbox"
  assert run.notes
  assert run.notes[0] == "Sandbox worker session primed from the latest market snapshot using 48 candles."
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.candle_count == 48
  assert run.provenance.runtime_session is not None
  assert run.provenance.runtime_session.worker_kind == "sandbox_native_worker"
  assert run.provenance.runtime_session.lifecycle_state == "active"
  assert run.provenance.runtime_session.started_at == clock.current
  assert run.provenance.runtime_session.primed_candle_count == 48
  assert run.provenance.runtime_session.processed_tick_count == 1
  assert run.provenance.runtime_session.last_heartbeat_at == clock.current
  assert run.provenance.runtime_session.last_processed_candle_at == run.provenance.market_data.effective_end_at
  assert run.provenance.runtime_session.last_seen_candle_at == run.provenance.market_data.effective_end_at
  assert run.provenance.runtime_session.recovery_count == 0

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.RUNNING
  assert reloaded.notes == run.notes
  assert reloaded.provenance.runtime_session == run.provenance.runtime_session


def test_paper_run_is_created_as_running_with_separate_mode(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  run = app.start_paper_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=36,
  )

  assert run.status == RunStatus.RUNNING
  assert run.config.mode == RunMode.PAPER
  assert run.notes
  assert run.notes[0] == "Paper session primed from the latest market snapshot using 36 candles."
  assert all("Sandbox preview replayed" not in note for note in run.notes)
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.candle_count == 36
  assert run.provenance.runtime_session is None

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.RUNNING
  assert reloaded.config.mode == RunMode.PAPER
  assert reloaded.notes == run.notes


def test_stop_sandbox_run_persists_terminal_state(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  stopped = app.stop_sandbox_run(run.config.run_id)

  assert stopped is not None
  assert stopped.status == RunStatus.STOPPED
  assert stopped.ended_at is not None
  assert stopped.notes[-1] == "Sandbox run stopped by operator."
  assert stopped.provenance.runtime_session is not None
  assert stopped.provenance.runtime_session.lifecycle_state == "stopped"
  assert stopped.provenance.runtime_session.last_heartbeat_at == stopped.ended_at

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.STOPPED
  assert reloaded.ended_at is not None
  assert reloaded.notes[-1] == "Sandbox run stopped by operator."
  assert reloaded.provenance.runtime_session is not None
  assert reloaded.provenance.runtime_session.lifecycle_state == "stopped"


def test_sandbox_worker_heartbeat_updates_runtime_session_state(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 6, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )
  first_heartbeat_at = run.provenance.runtime_session.last_heartbeat_at
  clock.advance(timedelta(seconds=10))

  result = app.maintain_sandbox_worker_sessions()
  updated = app.get_run(run.config.run_id)

  assert result == {"maintained": 1, "recovered": 0, "ticks_processed": 0}
  assert updated is not None
  assert updated.provenance.runtime_session is not None
  assert updated.provenance.runtime_session.last_heartbeat_at == clock.current
  assert updated.provenance.runtime_session.last_heartbeat_at != first_heartbeat_at
  assert updated.provenance.runtime_session.recovery_count == 0
  assert updated.provenance.runtime_session.processed_tick_count == 1


def test_sandbox_worker_recovery_marks_restart_and_timeout_history(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 8, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    sandbox_worker_heartbeat_interval_seconds=5,
    sandbox_worker_heartbeat_timeout_seconds=15,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  startup_result = app.maintain_sandbox_worker_sessions(
    force_recovery=True,
    recovery_reason="process_restart",
  )
  clock.advance(timedelta(seconds=20))
  timeout_result = app.maintain_sandbox_worker_sessions()
  updated = app.get_run(run.config.run_id)

  assert startup_result == {"maintained": 1, "recovered": 1, "ticks_processed": 0}
  assert timeout_result == {"maintained": 1, "recovered": 1, "ticks_processed": 0}
  assert updated is not None
  assert updated.provenance.runtime_session is not None
  assert updated.provenance.runtime_session.recovery_count == 2
  assert updated.provenance.runtime_session.last_recovery_reason == "heartbeat_timeout"
  assert updated.provenance.runtime_session.last_recovered_at == clock.current
  assert updated.provenance.runtime_session.last_heartbeat_at == clock.current
  assert any("sandbox_worker_recovered | process_restart" in note for note in updated.notes)
  assert any("sandbox_worker_recovered | heartbeat_timeout" in note for note in updated.notes)


def test_sandbox_worker_processes_new_candles_continuously(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 9, 0, tzinfo=UTC))
  market_data = MutableSeededMarketDataAdapter()
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )
  initial_equity_points = len(run.equity_curve)
  latest_candle = market_data.get_candles(symbol="ETH/USDT", timeframe="5m")[-1]
  first_new_candle = Candle(
    timestamp=latest_candle.timestamp + timedelta(minutes=5),
    open=latest_candle.close,
    high=latest_candle.close * 1.001,
    low=latest_candle.close * 0.999,
    close=latest_candle.close * 1.0005,
    volume=latest_candle.volume + 10,
  )
  second_new_candle = Candle(
    timestamp=latest_candle.timestamp + timedelta(minutes=10),
    open=first_new_candle.close,
    high=first_new_candle.close * 1.001,
    low=first_new_candle.close * 0.999,
    close=first_new_candle.close * 1.0005,
    volume=first_new_candle.volume + 10,
  )
  market_data.append_candle(symbol="ETH/USDT", candle=first_new_candle)
  market_data.append_candle(symbol="ETH/USDT", candle=second_new_candle)
  clock.advance(timedelta(seconds=5))

  result = app.maintain_sandbox_worker_sessions()
  updated = app.get_run(run.config.run_id)

  assert result == {"maintained": 1, "recovered": 0, "ticks_processed": 2}
  assert updated is not None
  assert len(updated.equity_curve) == initial_equity_points + 2
  assert updated.provenance.runtime_session is not None
  assert updated.provenance.runtime_session.processed_tick_count == 3
  assert updated.provenance.runtime_session.last_processed_candle_at == second_new_candle.timestamp
  assert updated.provenance.runtime_session.last_seen_candle_at == second_new_candle.timestamp


def test_sandbox_worker_does_not_reprocess_same_latest_candle(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 10, 0, tzinfo=UTC))
  market_data = MutableSeededMarketDataAdapter()
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )
  latest_candle = market_data.get_candles(symbol="ETH/USDT", timeframe="5m")[-1]
  new_candle = Candle(
    timestamp=latest_candle.timestamp + timedelta(minutes=5),
    open=latest_candle.close,
    high=latest_candle.close * 1.001,
    low=latest_candle.close * 0.999,
    close=latest_candle.close * 1.0005,
    volume=latest_candle.volume + 10,
  )
  market_data.append_candle(symbol="ETH/USDT", candle=new_candle)
  first_result = app.maintain_sandbox_worker_sessions()
  first_update = app.get_run(run.config.run_id)
  first_equity_points = len(first_update.equity_curve)
  clock.advance(timedelta(seconds=5))

  second_result = app.maintain_sandbox_worker_sessions()
  second_update = app.get_run(run.config.run_id)

  assert first_result == {"maintained": 1, "recovered": 0, "ticks_processed": 1}
  assert second_result == {"maintained": 1, "recovered": 0, "ticks_processed": 0}
  assert second_update is not None
  assert len(second_update.equity_curve) == first_equity_points
  assert second_update.provenance.runtime_session is not None
  assert second_update.provenance.runtime_session.processed_tick_count == 2
  assert second_update.provenance.runtime_session.last_processed_candle_at == new_candle.timestamp


def test_operator_visibility_flags_stale_sandbox_worker_runtime(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 11, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    sandbox_worker_heartbeat_interval_seconds=5,
    sandbox_worker_heartbeat_timeout_seconds=15,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )
  clock.advance(timedelta(seconds=20))

  visibility = app.get_operator_visibility()

  assert len(visibility.alerts) == 1
  assert visibility.alerts[0].category == "stale_runtime"
  assert visibility.alerts[0].severity == "warning"
  assert visibility.alerts[0].run_id == run.config.run_id
  assert visibility.alerts[0].symbol == "ETH/USDT"
  assert visibility.alerts[0].symbols == ("ETH/USDT",)
  assert visibility.alerts[0].timeframe == "5m"
  assert len(visibility.audit_events) >= 2
  assert visibility.audit_events[0].kind == "sandbox_worker_stale"
  assert visibility.audit_events[0].run_id == run.config.run_id


def test_operator_visibility_surfaces_provider_provenance_scheduler_lag(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 11, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    operator_alert_delivery=FakeOperatorAlertDeliveryAdapter(),
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  report_a = app.create_provider_provenance_scheduled_report(name="Drift watch A")
  report_b = app.create_provider_provenance_scheduled_report(name="Drift watch B")
  overdue_at = clock.current - timedelta(minutes=10)
  app._save_provider_provenance_scheduled_report_record(
    replace(report_a, next_run_at=overdue_at)
  )
  app._save_provider_provenance_scheduled_report_record(
    replace(report_b, next_run_at=overdue_at)
  )

  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  visibility = app.get_operator_visibility()

  assert visibility.provider_provenance_scheduler is not None
  assert visibility.provider_provenance_scheduler.status == "lagging"
  assert visibility.provider_provenance_scheduler.due_report_count == 1
  assert visibility.provider_provenance_scheduler.max_due_lag_seconds == 600
  assert any(alert.category == "scheduler_lag" for alert in visibility.alerts)
  assert any(
    event.kind == "provider_provenance_scheduler_lagging"
    for event in visibility.audit_events
  )


def test_provider_provenance_scheduler_lag_auto_runs_export_workflow_once(
  tmp_path: Path,
) -> None:
  class FakeSchedulerExportDeliveryAdapter:
    def __init__(self) -> None:
      self.deliveries: list[tuple[str, tuple[str, ...], str]] = []

    def list_targets(self) -> tuple[str, ...]:
      return ("slack_webhook", "pagerduty_events")

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty",)

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      resolved_targets = tuple(targets or ())
      self.deliveries.append((incident.alert_id, resolved_targets, phase))
      attempted_at = incident.timestamp
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{target}:{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=attempted_at,
          detail=f"Delivered to {target}",
          attempt_number=attempt_number,
          phase=phase,
          source=incident.source,
        )
        for target in resolved_targets
      )

    def sync_incident_workflow(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      payload: dict[str, Any] | None = None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return ()

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ) -> OperatorIncidentProviderPullSync | None:
      return None

  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 11, 0, tzinfo=UTC))
  delivery = FakeSchedulerExportDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    operator_alert_delivery=delivery,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  overdue_at = clock.current - timedelta(minutes=10)
  for name in ("Drift watch A", "Drift watch B", "Drift watch C"):
    report = app.create_provider_provenance_scheduled_report(name=name)
    app._save_provider_provenance_scheduled_report_record(
      replace(report, next_run_at=overdue_at)
    )

  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  first_visibility = app.get_operator_visibility()
  first_exports = app.list_provider_provenance_export_jobs(
    export_scope="provider_provenance_scheduler_health",
    requested_by_tab_id="system:provider-provenance-scheduler-alerts",
    limit=10,
  )

  assert len(first_exports) == 1
  assert first_exports[0].routing_policy_id == "default_critical"
  assert first_exports[0].escalation_count == 1
  assert first_exports[0].last_escalation_reason == "scheduler_lag_auto_export"
  assert first_exports[0].last_delivery_status == "delivered"
  assert first_visibility.provider_provenance_scheduler is not None
  assert first_visibility.provider_provenance_scheduler.alert_workflow_job_id == first_exports[0].job_id
  assert first_visibility.provider_provenance_scheduler.alert_workflow_state == "escalated_delivered"

  clock.advance(timedelta(minutes=1))
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  second_exports = app.list_provider_provenance_export_jobs(
    export_scope="provider_provenance_scheduler_health",
    requested_by_tab_id="system:provider-provenance-scheduler-alerts",
    limit=10,
  )

  assert len(second_exports) == 1
  assert second_exports[0].job_id == first_exports[0].job_id
  assert len(delivery.deliveries) == 1


def test_operator_visibility_surfaces_worker_failure_and_operator_stop_audit(
  monkeypatch,
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  def fail_worker(*, run: RunRecord) -> list[Candle]:
    raise RuntimeError("worker crash")

  monkeypatch.setattr(app, "_load_sandbox_worker_candles", fail_worker)
  app.maintain_sandbox_worker_sessions()
  failed_visibility = app.get_operator_visibility()

  assert len(failed_visibility.alerts) == 1
  assert failed_visibility.alerts[0].category == "worker_failure"
  assert failed_visibility.alerts[0].severity == "critical"
  assert failed_visibility.alerts[0].run_id == run.config.run_id
  assert failed_visibility.alerts[0].symbol == "ETH/USDT"
  assert failed_visibility.alerts[0].symbols == ("ETH/USDT",)
  assert failed_visibility.alerts[0].timeframe == "5m"
  assert any(event.kind == "sandbox_worker_failed" for event in failed_visibility.audit_events)

  stopped = app.stop_sandbox_run(run.config.run_id)
  stopped_visibility = app.get_operator_visibility()

  assert stopped is not None
  assert any(event.kind == "sandbox_worker_stopped" for event in stopped_visibility.audit_events)


def test_operator_visibility_surfaces_provider_provenance_scheduler_failure(
  monkeypatch,
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
  )

  def fail_scheduler(*args, **kwargs):
    raise RuntimeError("scheduler crash")

  monkeypatch.setattr(app, "run_due_provider_provenance_scheduled_reports", fail_scheduler)
  with pytest.raises(RuntimeError, match="scheduler crash"):
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )

  visibility = app.get_operator_visibility()

  assert visibility.provider_provenance_scheduler is not None
  assert visibility.provider_provenance_scheduler.status == "failed"
  assert visibility.provider_provenance_scheduler.last_error == "scheduler crash"
  assert any(alert.category == "scheduler_failure" for alert in visibility.alerts)
  assert any(
    event.kind == "provider_provenance_scheduler_failed"
    for event in visibility.audit_events
  )


def test_provider_provenance_scheduler_failure_auto_runs_export_workflow(
  monkeypatch,
  tmp_path: Path,
) -> None:
  class FakeSchedulerExportDeliveryAdapter:
    def __init__(self) -> None:
      self.deliveries: list[tuple[str, tuple[str, ...], str]] = []

    def list_targets(self) -> tuple[str, ...]:
      return ("slack_webhook", "pagerduty_events")

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty",)

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      resolved_targets = tuple(targets or ())
      self.deliveries.append((incident.alert_id, resolved_targets, phase))
      attempted_at = incident.timestamp
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{target}:{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=attempted_at,
          detail=f"Delivered to {target}",
          attempt_number=attempt_number,
          phase=phase,
          source=incident.source,
        )
        for target in resolved_targets
      )

    def sync_incident_workflow(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      payload: dict[str, Any] | None = None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return ()

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ) -> OperatorIncidentProviderPullSync | None:
      return None

  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 0, tzinfo=UTC))
  delivery = FakeSchedulerExportDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    operator_alert_delivery=delivery,
    provider_provenance_report_scheduler_interval_seconds=60,
  )

  def fail_scheduler(*args, **kwargs):
    raise RuntimeError("scheduler crash")

  monkeypatch.setattr(app, "run_due_provider_provenance_scheduled_reports", fail_scheduler)
  with pytest.raises(RuntimeError, match="scheduler crash"):
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )

  visibility = app.get_operator_visibility()
  exports = app.list_provider_provenance_export_jobs(
    export_scope="provider_provenance_scheduler_health",
    requested_by_tab_id="system:provider-provenance-scheduler-alerts",
    limit=10,
  )

  assert len(exports) == 1
  assert exports[0].routing_policy_id == "default_critical"
  assert exports[0].escalation_count == 1
  assert exports[0].last_escalation_reason == "scheduler_failure_auto_export"
  assert exports[0].last_delivery_status == "delivered"
  assert visibility.provider_provenance_scheduler is not None
  assert visibility.provider_provenance_scheduler.alert_workflow_job_id == exports[0].job_id
  assert visibility.provider_provenance_scheduler.alert_workflow_state == "escalated_delivered"
  assert len(delivery.deliveries) == 1


def test_resolved_scheduler_alert_row_reconstructs_historical_export(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    operator_alert_delivery=FakeOperatorAlertDeliveryAdapter(),
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  overdue_at = clock.current - timedelta(minutes=10)
  for name in ("Drift watch A", "Drift watch B"):
    report = app.create_provider_provenance_scheduled_report(name=name)
    app._save_provider_provenance_scheduled_report_record(
      replace(report, next_run_at=overdue_at)
    )

  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current - timedelta(minutes=10))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  resolved_visibility = app.get_operator_visibility()
  resolved_alerts = [
    alert
    for alert in resolved_visibility.alert_history
    if alert.category == "scheduler_lag" and alert.status == "resolved"
  ]
  assert len(resolved_alerts) == 2
  assert len({alert.occurrence_id for alert in resolved_alerts}) == 2
  oldest_resolved_alert = min(
    resolved_alerts,
    key=lambda alert: alert.detected_at,
  )
  newest_resolved_alert = max(
    resolved_alerts,
    key=lambda alert: alert.detected_at,
  )
  assert oldest_resolved_alert.timeline_key == "scheduler_lag"
  assert oldest_resolved_alert.timeline_position == 1
  assert newest_resolved_alert.timeline_position == 2
  assert oldest_resolved_alert.timeline_total == 2
  assert newest_resolved_alert.timeline_total == 2

  export_payload = app.reconstruct_provider_provenance_scheduler_health_export(
    alert_category=oldest_resolved_alert.category,
    detected_at=oldest_resolved_alert.detected_at,
    resolved_at=oldest_resolved_alert.resolved_at,
    export_format="json",
    history_limit=8,
    drilldown_history_limit=12,
  )
  reconstructed = json.loads(export_payload["content"])
  shared_export = app.create_provider_provenance_export_job(
    content=export_payload["content"],
    requested_by_tab_id="tab_scheduler_history",
    requested_by_tab_label="Scheduler history row",
  )

  assert export_payload["format"] == "json"
  assert reconstructed["reconstruction"]["mode"] == "resolved_alert_row"
  assert reconstructed["reconstruction"]["alert_category"] == "scheduler_lag"
  assert reconstructed["current"]["status"] == "lagging"
  assert reconstructed["history_page"]["total"] >= 1
  assert reconstructed["analytics"]["query"]["reconstruction_mode"] == "resolved_alert_row"
  assert reconstructed["analytics"]["query"]["alert_resolved_at"] == oldest_resolved_alert.resolved_at.isoformat()
  assert reconstructed["analytics"]["query"]["alert_detected_at"] == oldest_resolved_alert.detected_at.isoformat()
  assert shared_export.export_scope == "provider_provenance_scheduler_health"
  assert "resolved alert reconstruction" in (shared_export.filter_summary or "")


def test_resolved_scheduler_alert_row_can_export_mixed_status_post_resolution_narrative(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 30, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    operator_alert_delivery=FakeOperatorAlertDeliveryAdapter(),
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  overdue_at = clock.current - timedelta(minutes=10)
  for name in ("Narrative watch A", "Narrative watch B"):
    report = app.create_provider_provenance_scheduled_report(name=name)
    app._save_provider_provenance_scheduled_report_record(
      replace(report, next_run_at=overdue_at)
    )

  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current - timedelta(minutes=10))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )

  resolved_alert = min(
    (
      alert
      for alert in app.get_operator_visibility().alert_history
      if alert.category == "scheduler_lag" and alert.status == "resolved"
    ),
    key=lambda alert: alert.detected_at,
  )

  export_payload = app.reconstruct_provider_provenance_scheduler_health_export(
    alert_category=resolved_alert.category,
    detected_at=resolved_alert.detected_at,
    resolved_at=resolved_alert.resolved_at,
    narrative_mode="mixed_status_post_resolution",
    export_format="json",
    history_limit=8,
    drilldown_history_limit=12,
  )
  reconstructed = json.loads(export_payload["content"])
  shared_export = app.create_provider_provenance_export_job(
    content=export_payload["content"],
    requested_by_tab_id="tab_scheduler_history",
    requested_by_tab_label="Scheduler narrative row",
  )

  assert reconstructed["reconstruction"]["mode"] == "resolved_alert_row"
  assert reconstructed["reconstruction"]["narrative_mode"] == "mixed_status_post_resolution"
  assert reconstructed["current"]["status"] == "healthy"
  assert reconstructed["history_page"]["total"] == 2
  assert [item["status"] for item in reconstructed["history_page"]["items"]] == ["healthy", "lagging"]
  assert reconstructed["mixed_status_narrative"]["selected_occurrence"]["current"]["status"] == "lagging"
  assert reconstructed["mixed_status_narrative"]["post_resolution_history"]["total"] == 1
  assert reconstructed["mixed_status_narrative"]["post_resolution_history"]["items"][0]["status"] == "healthy"
  assert reconstructed["analytics"]["query"]["narrative_mode"] == "mixed_status_post_resolution"
  assert "mixed-status narrative" in (shared_export.filter_summary or "")


def test_scheduler_alert_history_can_export_stitched_multi_occurrence_report(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 45, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  overdue_at = clock.current - timedelta(minutes=10)
  for name in ("Report watch A", "Report watch B"):
    report = app.create_provider_provenance_scheduled_report(name=name)
    app._save_provider_provenance_scheduled_report_record(
      replace(report, next_run_at=overdue_at)
    )

  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current - timedelta(minutes=10))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )

  export_payload = app.export_provider_provenance_scheduler_stitched_narrative_report(
    category="scheduler_lag",
    status="resolved",
    narrative_facet="resolved_narratives",
    occurrence_limit=4,
    export_format="json",
    history_limit=8,
    drilldown_history_limit=12,
  )
  stitched_report = json.loads(export_payload["content"])
  shared_export = app.create_provider_provenance_export_job(
    content=export_payload["content"],
    requested_by_tab_id="tab_scheduler_stitched",
    requested_by_tab_label="Scheduler stitched report",
  )

  assert stitched_report["query"]["reconstruction_mode"] == "stitched_occurrence_report"
  assert stitched_report["query"]["narrative_mode"] == "stitched_multi_occurrence"
  assert stitched_report["query"]["narrative_facet"] == "resolved_narratives"
  assert stitched_report["stitched_occurrence_report"]["mode"] == "stitched_multi_occurrence"
  assert stitched_report["stitched_occurrence_report"]["summary"]["occurrence_count"] == 2
  assert len(stitched_report["stitched_occurrence_report"]["occurrences"]) == 2
  assert stitched_report["stitched_occurrence_report"]["stitched_status_sequence"]
  assert all(
    segment["occurrence_id"]
    for segment in stitched_report["stitched_occurrence_report"]["stitched_status_sequence"]
  )
  assert stitched_report["history_page"]["total"] >= 2
  assert shared_export.export_scope == "provider_provenance_scheduler_health"
  assert "stitched occurrence report" in (shared_export.filter_summary or "")
  assert "stitched multi-occurrence narrative" in (shared_export.filter_summary or "")


def test_scheduler_alert_history_tracks_multiple_resolved_occurrences_per_category(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 13, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  for name in ("Timeline watch A", "Timeline watch B"):
    report = app.create_provider_provenance_scheduled_report(name=name)
    app._save_provider_provenance_scheduled_report_record(
      replace(report, next_run_at=clock.current - timedelta(minutes=10))
    )

  for should_be_overdue in (False, True, False):
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    clock.advance(timedelta(minutes=1))
    next_run_at = (
      clock.current - timedelta(minutes=10)
      if should_be_overdue
      else clock.current + timedelta(days=7)
    )
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=next_run_at)
      )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )

  visibility = app.get_operator_visibility()
  resolved_alerts = [
    alert
    for alert in visibility.alert_history
    if alert.category == "scheduler_lag" and alert.status == "resolved"
  ]

  assert len(resolved_alerts) == 2
  assert [alert.timeline_position for alert in sorted(resolved_alerts, key=lambda alert: alert.detected_at)] == [1, 2]
  assert all(alert.timeline_total == 2 for alert in resolved_alerts)
  assert len({alert.occurrence_id for alert in resolved_alerts}) == 2


def test_provider_provenance_scheduler_alert_history_page_paginates_occurrences(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 13, 30, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  for name in ("Timeline page A", "Timeline page B"):
    report = app.create_provider_provenance_scheduled_report(name=name)
    app._save_provider_provenance_scheduled_report_record(
      replace(report, next_run_at=clock.current - timedelta(minutes=10))
    )

  for should_be_overdue in (False, True, False):
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    clock.advance(timedelta(minutes=1))
    next_run_at = (
      clock.current - timedelta(minutes=10)
      if should_be_overdue
      else clock.current + timedelta(days=7)
    )
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=next_run_at)
      )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )

  first_page = app.get_provider_provenance_scheduler_alert_history_page(
    category="scheduler_lag",
    status="resolved",
    limit=1,
    offset=0,
  )
  second_page = app.get_provider_provenance_scheduler_alert_history_page(
    category="scheduler_lag",
    status="resolved",
    limit=1,
    offset=1,
  )
  narrative_page = app.get_provider_provenance_scheduler_alert_history_page(
    category="scheduler_lag",
    narrative_facet="post_resolution_recovery",
    limit=10,
    offset=0,
  )

  assert first_page["query"]["category"] == "scheduler_lag"
  assert first_page["query"]["status"] == "resolved"
  assert first_page["total"] == 2
  assert first_page["returned"] == 1
  assert first_page["next_offset"] == 1
  assert first_page["summary"]["by_category"][0]["category"] == "scheduler_lag"
  assert first_page["items"][0]["alert"].timeline_position == 2
  assert first_page["items"][0]["alert"].timeline_total == 2
  assert second_page["returned"] == 1
  assert second_page["previous_offset"] == 0
  assert second_page["items"][0]["alert"].timeline_position == 1
  assert narrative_page["query"]["narrative_facet"] == "post_resolution_recovery"
  assert narrative_page["returned"] >= 1
  assert all(
    bool(item["narrative"]["has_post_resolution_history"])
    for item in narrative_page["items"]
  )


def test_provider_provenance_scheduler_alert_history_binding_serializes_occurrences(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )
  bindings_by_key = {
    binding.surface_key: binding
    for binding in list_standalone_surface_runtime_bindings()
  }

  report_a = app.create_provider_provenance_scheduled_report(name="Binding timeline watch A")
  report_b = app.create_provider_provenance_scheduled_report(name="Binding timeline watch B")
  for report in (report_a, report_b):
    app._save_provider_provenance_scheduled_report_record(
      replace(report, next_run_at=clock.current - timedelta(minutes=10))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )

  payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_alert_history"],
    app=app,
    filters={
      "category": "scheduler_lag",
      "status": "resolved",
      "narrative_facet": "post_resolution_recovery",
      "limit": 10,
      "offset": 0,
    },
  )

  assert payload["query"]["category"] == "scheduler_lag"
  assert payload["query"]["status"] == "resolved"
  assert payload["query"]["narrative_facet"] == "post_resolution_recovery"
  assert payload["summary"]["total_occurrences"] == 1
  assert payload["summary"]["resolved_count"] == 1
  assert payload["returned"] == 1
  assert payload["items"][0]["category"] == "scheduler_lag"
  assert payload["items"][0]["status"] == "resolved"
  assert payload["available_filters"]["narrative_facets"][0] == "all_occurrences"
  assert payload["items"][0]["narrative"]["has_post_resolution_history"] is True
  assert payload["items"][0]["occurrence_id"]
  assert payload["items"][0]["timeline_total"] == 1

  search_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_alert_history"],
    app=app,
    filters={
      "search": "status:resolved AND (recovered OR healthy) AND NOT category:failure",
      "limit": 10,
      "offset": 0,
    },
  )
  assert search_payload["query"]["search"] == "status:resolved AND (recovered OR healthy) AND NOT category:failure"
  assert search_payload["search_summary"]["mode"] == "persistent_full_text_boolean_semantic_ranking"
  assert search_payload["search_summary"]["top_score"] > 0
  assert search_payload["search_summary"]["operator_count"] == 2
  assert search_payload["search_summary"]["boolean_operator_count"] >= 4
  assert search_payload["search_summary"]["indexed_occurrence_count"] >= 1
  assert search_payload["search_summary"]["indexed_term_count"] > 0
  assert search_payload["search_summary"]["persistence_mode"] == "embedded_scheduler_search_service"
  assert search_payload["search_summary"]["relevance_model"] == "tfidf_field_weight_v1"
  assert search_payload["search_summary"]["query_id"]
  assert (
    search_payload["search_summary"]["retrieval_cluster_mode"]
    == "cross_occurrence_semantic_vector_cluster_v1"
  )
  assert search_payload["search_summary"]["retrieval_cluster_count"] >= 1
  assert "recovery" in search_payload["search_summary"]["semantic_concepts"]
  assert "AND" in search_payload["search_summary"]["query_plan"]
  assert "OR" in search_payload["search_summary"]["query_plan"]
  assert "NOT" in search_payload["search_summary"]["query_plan"]
  assert search_payload["returned"] >= 1
  assert search_payload["retrieval_clusters"]
  assert any(
    item["narrative"]["has_post_resolution_history"]
    for item in search_payload["items"]
  )
  assert search_payload["items"][0]["search_match"]["score"] > 0
  assert "status:resolved" in search_payload["items"][0]["search_match"]["operator_hits"]
  assert "recovery" in search_payload["items"][0]["search_match"]["semantic_concepts"]
  assert search_payload["items"][0]["search_match"]["relevance_model"] == "tfidf_field_weight_v1"
  assert search_payload["search_analytics"]["feedback_count"] == 0
  assert search_payload["search_analytics"]["learned_relevance_active"] is False
  assert search_payload["items"][0]["retrieval_cluster"]["cluster_id"]
  assert search_payload["items"][0]["retrieval_cluster"]["label"]

  feedback_result = app.record_provider_provenance_scheduler_alert_search_feedback(
    query_id=search_payload["search_summary"]["query_id"],
    query=search_payload["query"]["search"],
    occurrence_id=search_payload["items"][0]["occurrence_id"],
    signal="relevant",
    matched_fields=tuple(search_payload["items"][0]["search_match"]["matched_fields"]),
    semantic_concepts=tuple(search_payload["items"][0]["search_match"]["semantic_concepts"]),
    operator_hits=tuple(search_payload["items"][0]["search_match"]["operator_hits"]),
    lexical_score=search_payload["items"][0]["search_match"]["lexical_score"],
    semantic_score=search_payload["items"][0]["search_match"]["semantic_score"],
    operator_score=search_payload["items"][0]["search_match"]["operator_score"],
    score=search_payload["items"][0]["search_match"]["score"],
    ranking_reason=search_payload["items"][0]["search_match"]["ranking_reason"],
  )
  assert feedback_result["feedback_count"] == 1
  assert feedback_result["moderation_status"] == "pending"
  assert feedback_result["pending_feedback_count"] == 1

  pending_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_alert_history"],
    app=app,
    filters={
      "search": "status:resolved AND (recovered OR healthy) AND NOT category:failure",
      "limit": 10,
      "offset": 0,
    },
  )
  assert pending_payload["search_summary"]["relevance_model"] == "tfidf_field_weight_v1"
  assert pending_payload["search_analytics"]["feedback_count"] == 1
  assert pending_payload["search_analytics"]["pending_feedback_count"] == 1
  assert pending_payload["search_analytics"]["approved_feedback_count"] == 0
  assert pending_payload["search_analytics"]["learned_relevance_active"] is False
  assert pending_payload["items"][0]["search_match"]["relevance_model"] == "tfidf_field_weight_v1"

  dashboard_payload = app.get_provider_provenance_scheduler_search_dashboard(
    governance_view="pending_queue",
    window_days=30,
    stale_pending_hours=1,
    moderation_status="pending",
    feedback_limit=10,
  )
  assert dashboard_payload["summary"]["feedback_count"] >= 1
  assert dashboard_payload["summary"]["pending_feedback_count"] >= 1
  assert dashboard_payload["query"]["governance_view"] == "pending_queue"
  assert dashboard_payload["quality_dashboard"]["window_days"] == 30
  assert dashboard_payload["quality_dashboard"]["time_series"]
  assert dashboard_payload["moderation_governance"]["pending_feedback_count"] >= 1
  assert dashboard_payload["feedback_items"][0]["feedback_id"] == feedback_result["feedback_id"]
  assert dashboard_payload["feedback_items"][0]["age_hours"] >= 0

  moderation_result = app.moderate_provider_provenance_scheduler_search_feedback_batch(
    feedback_ids=(feedback_result["feedback_id"],),
    moderation_status="approved",
    actor="operator",
  )
  assert moderation_result["moderation_status"] == "approved"
  assert moderation_result["updated_count"] == 1

  tuned_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_alert_history"],
    app=app,
    filters={
      "search": "status:resolved AND (recovered OR healthy) AND NOT category:failure",
      "limit": 10,
      "offset": 0,
    },
  )
  assert tuned_payload["search_summary"]["relevance_model"] == "tfidf_field_weight_feedback_v2"
  assert tuned_payload["search_analytics"]["feedback_count"] == 1
  assert tuned_payload["search_analytics"]["approved_feedback_count"] == 1
  assert tuned_payload["search_analytics"]["learned_relevance_active"] is True
  assert tuned_payload["items"][0]["search_match"]["relevance_model"] == "tfidf_field_weight_feedback_v2"
  assert tuned_payload["items"][0]["search_match"]["feedback_signal_count"] >= 1


def test_provider_provenance_scheduler_search_moderation_policy_catalog_and_plan_flow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )
  bindings_by_key = {
    binding.surface_key: binding
    for binding in list_standalone_surface_runtime_bindings()
  }

  report_a = app.create_provider_provenance_scheduled_report(name="Moderation policy watch A")
  report_b = app.create_provider_provenance_scheduled_report(name="Moderation policy watch B")
  overdue_at = clock.current - timedelta(minutes=10)
  app._save_provider_provenance_scheduled_report_record(
    replace(report_a, next_run_at=overdue_at)
  )
  app._save_provider_provenance_scheduled_report_record(
    replace(report_b, next_run_at=overdue_at)
  )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(minutes=1))
  for current_report in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(current_report, next_run_at=clock.current + timedelta(days=7))
    )
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )

  search_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_alert_history"],
    app=app,
    filters={
      "search": "status:resolved AND (recovered OR healthy) AND NOT category:failure",
      "limit": 10,
      "offset": 0,
    },
  )
  feedback_result = app.record_provider_provenance_scheduler_alert_search_feedback(
    query_id=search_payload["search_summary"]["query_id"],
    query=search_payload["query"]["search"],
    occurrence_id=search_payload["items"][0]["occurrence_id"],
    signal="relevant",
    matched_fields=tuple(search_payload["items"][0]["search_match"]["matched_fields"]),
    semantic_concepts=tuple(search_payload["items"][0]["search_match"]["semantic_concepts"]),
    operator_hits=tuple(search_payload["items"][0]["search_match"]["operator_hits"]),
    lexical_score=search_payload["items"][0]["search_match"]["lexical_score"],
    semantic_score=search_payload["items"][0]["search_match"]["semantic_score"],
    operator_score=search_payload["items"][0]["search_match"]["operator_score"],
    score=search_payload["items"][0]["search_match"]["score"],
    ranking_reason=search_payload["items"][0]["search_match"]["ranking_reason"],
  )

  catalog = app.create_provider_provenance_scheduler_search_moderation_policy_catalog(
    name="High-signal scheduler approvals",
    description="Approve only strong scheduler matches with an explicit note.",
    default_moderation_status="approved",
    governance_view="high_score_pending",
    minimum_score=150,
    require_note=True,
    created_by_tab_id="control-room",
    created_by_tab_label="Control room",
  )
  assert catalog["default_moderation_status"] == "approved"
  catalogs = app.list_provider_provenance_scheduler_search_moderation_policy_catalogs()
  assert catalogs["total"] == 1
  assert catalogs["items"][0]["revision_count"] == 1

  updated_catalog = app.update_provider_provenance_scheduler_search_moderation_policy_catalog(
    catalog["catalog_id"],
    description="Approve and review only strong scheduler matches with a note.",
    governance_view="pending_queue",
    stale_pending_hours=48,
    actor_tab_id="control-room",
    actor_tab_label="Control room",
  )
  assert updated_catalog["governance_view"] == "pending_queue"
  assert updated_catalog["revision_count"] == 2

  revision_payload = app.list_provider_provenance_scheduler_search_moderation_policy_catalog_revisions(
    catalog["catalog_id"]
  )
  assert revision_payload["catalog"]["catalog_id"] == catalog["catalog_id"]
  assert revision_payload["history"][0]["action"] == "updated"
  assert revision_payload["history"][-1]["action"] == "created"

  audit_payload = app.list_provider_provenance_scheduler_search_moderation_policy_catalog_audits(
    catalog_id=catalog["catalog_id"],
  )
  assert audit_payload["total"] >= 2
  assert audit_payload["items"][0]["catalog_id"] == catalog["catalog_id"]

  bulk_result = app.bulk_govern_provider_provenance_scheduler_search_moderation_policy_catalogs(
    catalog_ids=(catalog["catalog_id"],),
    action="update",
    name_prefix="[Ops] ",
    description_append=" Bulk reviewed.",
    minimum_score=175,
    actor_tab_id="control-room",
    actor_tab_label="Control room",
  )
  assert bulk_result.applied_count == 1
  post_bulk_catalog = app.list_provider_provenance_scheduler_search_moderation_policy_catalogs()["items"][0]
  assert post_bulk_catalog["name"].startswith("[Ops] ")
  assert post_bulk_catalog["minimum_score"] == 175

  previewed = app.stage_provider_provenance_scheduler_search_moderation_plan(
    feedback_ids=(feedback_result["feedback_id"],),
    policy_catalog_id=post_bulk_catalog["catalog_id"],
    actor="operator",
    source_tab_id="control-room",
    source_tab_label="Control room",
  )
  assert previewed["queue_state"] == "pending_approval"
  assert previewed["preview_count"] == 1
  assert previewed["preview_items"][0]["eligible"] is True

  queue_payload = app.list_provider_provenance_scheduler_search_moderation_plans(
    queue_state="pending_approval",
  )
  assert queue_payload["summary"]["pending_approval_count"] == 1
  assert queue_payload["items"][0]["plan_id"] == previewed["plan_id"]

  approved = app.approve_provider_provenance_scheduler_search_moderation_plan(
    plan_id=previewed["plan_id"],
    actor="operator",
    note="High-signal recovery query approved for tuning.",
    source_tab_id="control-room",
    source_tab_label="Control room",
  )
  assert approved["queue_state"] == "ready_to_apply"
  assert approved["approval_note"]

  applied = app.apply_provider_provenance_scheduler_search_moderation_plan(
    plan_id=previewed["plan_id"],
    actor="operator",
    note="Apply approved moderation decision to feedback.",
    source_tab_id="control-room",
    source_tab_label="Control room",
  )
  assert applied["queue_state"] == "completed"
  assert applied["applied_result"]["updated_count"] == 1

  tuned_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_alert_history"],
    app=app,
    filters={
      "search": "status:resolved AND (recovered OR healthy) AND NOT category:failure",
      "limit": 10,
      "offset": 0,
    },
  )
  assert tuned_payload["search_summary"]["relevance_model"] == "tfidf_field_weight_feedback_v2"
  assert tuned_payload["search_analytics"]["approved_feedback_count"] == 1
  assert tuned_payload["search_analytics"]["learned_relevance_active"] is True


def test_provider_provenance_scheduler_search_moderation_catalog_governance_flow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  catalog = app.create_provider_provenance_scheduler_search_moderation_policy_catalog(
    name="Scheduler governance candidate",
    description="Catalog changes should flow through governance review.",
    default_moderation_status="approved",
    governance_view="pending_queue",
    minimum_score=100,
    created_by_tab_id="control-room",
    created_by_tab_label="Control room",
  )
  governance_policy = (
    app.create_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
      name="Require reviewed catalog updates",
      description="Reusable governance defaults for moderation policy catalogs.",
      action_scope="update",
      require_approval_note=True,
      guidance="Approval note is mandatory before moderation catalog changes apply.",
      description_append=" Reviewed by governance queue.",
      default_moderation_status="approved",
      governance_view="high_score_pending",
      window_days=30,
      stale_pending_hours=24,
      minimum_score=180,
      require_note=True,
      created_by_tab_id="control-room",
      created_by_tab_label="Control room",
    )
  )
  assert governance_policy["action_scope"] == "update"
  assert governance_policy["require_approval_note"] is True

  governance_policies = (
    app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
      action_scope="update",
    )
  )
  assert governance_policies["total"] == 1
  assert (
    governance_policies["items"][0]["governance_policy_id"]
    == governance_policy["governance_policy_id"]
  )
  assert governance_policies["items"][0]["revision_count"] == 1

  updated_governance_policy = (
    app.update_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
      governance_policy["governance_policy_id"],
      guidance="Updated moderation governance note.",
      minimum_score=220,
      actor_tab_id="control-room",
      actor_tab_label="Control room",
    )
  )
  assert updated_governance_policy["minimum_score"] == 220

  governance_policy_revisions = (
    app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions(
      governance_policy["governance_policy_id"]
    )
  )
  assert len(governance_policy_revisions["history"]) == 2

  governance_policy_audits = (
    app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits(
      governance_policy_id=governance_policy["governance_policy_id"]
    )
  )
  assert governance_policy_audits["total"] >= 2

  staged_plan = app.stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    catalog_ids=(catalog["catalog_id"],),
    action="update",
    governance_policy_id=governance_policy["governance_policy_id"],
    actor="operator",
    source_tab_id="control-room",
    source_tab_label="Control room",
  )
  assert staged_plan["queue_state"] == "pending_approval"
  assert staged_plan["preview_count"] == 1
  assert staged_plan["preview_items"][0]["outcome"] == "changed"
  assert "description" in staged_plan["preview_items"][0]["changed_fields"]
  assert staged_plan["preview_items"][0]["proposed_snapshot"]["minimum_score"] == 220

  queued_plans = app.list_provider_provenance_scheduler_search_moderation_catalog_governance_plans(
    queue_state="pending_approval",
  )
  assert queued_plans["summary"]["pending_approval_count"] == 1
  assert queued_plans["items"][0]["plan_id"] == staged_plan["plan_id"]

  approved_plan = app.approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    plan_id=staged_plan["plan_id"],
    actor="operator",
    note="Catalog changes reviewed for scheduler governance.",
    source_tab_id="control-room",
    source_tab_label="Control room",
  )
  assert approved_plan["queue_state"] == "ready_to_apply"
  assert approved_plan["approval_note"] == "Catalog changes reviewed for scheduler governance."

  applied_plan = app.apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    plan_id=staged_plan["plan_id"],
    actor="operator",
    note="Apply reviewed moderation catalog changes.",
    source_tab_id="control-room",
    source_tab_label="Control room",
  )
  assert applied_plan["queue_state"] == "completed"
  assert applied_plan["applied_result"]["applied_count"] == 1

  updated_catalog = app.list_provider_provenance_scheduler_search_moderation_policy_catalogs()["items"][0]
  assert updated_catalog["minimum_score"] == 220
  assert updated_catalog["require_note"] is True
  assert updated_catalog["description"].endswith("Reviewed by governance queue.")

  bulk_deleted = (
    app.bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
      governance_policy_ids=(governance_policy["governance_policy_id"],),
      action="delete",
      actor_tab_id="control-room",
      actor_tab_label="Control room",
    )
  )
  assert bulk_deleted.applied_count == 1

  deleted_policy = app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policies()[
    "items"
  ][0]
  assert deleted_policy["status"] == "deleted"

  bulk_restored = (
    app.bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
      governance_policy_ids=(governance_policy["governance_policy_id"],),
      action="restore",
      actor_tab_id="control-room",
      actor_tab_label="Control room",
    )
  )
  assert bulk_restored.applied_count == 1

  restored_policy = app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policies()[
    "items"
  ][0]
  assert restored_policy["status"] == "active"

  meta_policy = (
    app.create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy(
      name="Escalate governance policy review",
      description="Reusable queue defaults for moderation governance policy changes.",
      action_scope="update",
      require_approval_note=True,
      guidance="Meta-policy review note is required.",
      name_prefix="[Meta] ",
      description_append=" Escalated through policy review.",
      policy_action_scope="update",
      policy_require_approval_note=True,
      policy_guidance="Require policy-level note for apply.",
      default_moderation_status="approved",
      governance_view="high_score_pending",
      window_days=45,
      stale_pending_hours=12,
      minimum_score=260,
      require_note=True,
      created_by_tab_id="control-room",
      created_by_tab_label="Control room",
    )
  )
  assert meta_policy["action_scope"] == "update"
  assert meta_policy["policy_action_scope"] == "update"

  meta_policies = (
    app.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies(
      action_scope="update",
    )
  )
  assert meta_policies["total"] == 1
  assert meta_policies["items"][0]["meta_policy_id"] == meta_policy["meta_policy_id"]

  staged_meta_plan = app.stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    governance_policy_ids=(governance_policy["governance_policy_id"],),
    action="update",
    meta_policy_id=meta_policy["meta_policy_id"],
    actor="operator",
    source_tab_id="control-room",
    source_tab_label="Control room",
  )
  assert staged_meta_plan["queue_state"] == "pending_approval"
  assert staged_meta_plan["preview_count"] == 1
  assert staged_meta_plan["preview_items"][0]["governance_policy_id"] == governance_policy["governance_policy_id"]
  assert staged_meta_plan["preview_items"][0]["proposed_snapshot"]["minimum_score"] == 260

  queued_meta_plans = (
    app.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans(
      queue_state="pending_approval",
      meta_policy_id=meta_policy["meta_policy_id"],
    )
  )
  assert queued_meta_plans["summary"]["pending_approval_count"] == 1
  assert queued_meta_plans["items"][0]["plan_id"] == staged_meta_plan["plan_id"]

  approved_meta_plan = (
    app.approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
      plan_id=staged_meta_plan["plan_id"],
      actor="operator",
      note="Reviewed moderation governance policy changes.",
      source_tab_id="control-room",
      source_tab_label="Control room",
    )
  )
  assert approved_meta_plan["queue_state"] == "ready_to_apply"
  assert approved_meta_plan["approval_note"] == "Reviewed moderation governance policy changes."

  applied_meta_plan = (
    app.apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
      plan_id=staged_meta_plan["plan_id"],
      actor="operator",
      note="Apply reviewed moderation governance policy changes.",
      source_tab_id="control-room",
      source_tab_label="Control room",
    )
  )
  assert applied_meta_plan["queue_state"] == "completed"
  assert applied_meta_plan["applied_result"]["applied_count"] == 1

  meta_updated_policy = app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policies()[
    "items"
  ][0]
  assert meta_updated_policy["minimum_score"] == 260
  assert meta_updated_policy["require_approval_note"] is True
  assert meta_updated_policy["guidance"] == "Require policy-level note for apply."
  assert meta_updated_policy["description"].endswith("Escalated through policy review.")


def test_provider_provenance_scheduler_history_and_analytics_persist(
  monkeypatch,
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  presets = build_preset_catalog(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    presets=presets,
    clock=clock,
    provider_provenance_report_scheduler_interval_seconds=60,
    provider_provenance_report_scheduler_batch_limit=1,
  )

  report_a = app.create_provider_provenance_scheduled_report(name="Drift watch A")
  report_b = app.create_provider_provenance_scheduled_report(name="Drift watch B")
  overdue_at = clock.current - timedelta(minutes=10)
  app._save_provider_provenance_scheduled_report_record(replace(report_a, next_run_at=overdue_at))
  app._save_provider_provenance_scheduled_report_record(replace(report_b, next_run_at=overdue_at))

  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  for record in app.list_provider_provenance_scheduled_reports(limit=10):
    app._save_provider_provenance_scheduled_report_record(
      replace(record, next_run_at=clock.current + timedelta(days=7))
    )
  clock.advance(timedelta(days=1))
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )
  clock.advance(timedelta(days=1))

  def fail_scheduler(*args, **kwargs):
    raise RuntimeError("scheduler crash")

  monkeypatch.setattr(app, "run_due_provider_provenance_scheduled_reports", fail_scheduler)
  with pytest.raises(RuntimeError, match="scheduler crash"):
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )

  history = app.list_provider_provenance_scheduler_health_history(limit=10)

  assert [record.status for record in history] == ["failed", "healthy", "lagging"]
  assert history[0].last_error == "scheduler crash"
  assert history[1].last_executed_count == 0
  assert history[2].due_report_count == 1

  analytics = app.get_provider_provenance_scheduler_health_analytics(window_days=3, history_limit=5)

  assert analytics["totals"] == {
    "record_count": 3,
    "healthy_count": 1,
    "lagging_count": 1,
    "failed_count": 1,
    "disabled_count": 0,
    "starting_count": 0,
    "executed_report_count": 1,
    "peak_lag_seconds": 600,
    "peak_due_report_count": 1,
  }
  assert [bucket["bucket_key"] for bucket in analytics["time_series"]["health_status"]["series"]] == [
    "2025-01-03",
    "2025-01-04",
    "2025-01-05",
  ]
  assert analytics["time_series"]["health_status"]["summary"] == {
    "peak_cycle_bucket_key": "2025-01-05",
    "peak_cycle_bucket_label": "Jan 05",
    "peak_cycle_count": 1,
    "latest_bucket_key": "2025-01-05",
    "latest_bucket_label": "Jan 05",
    "latest_status": "failed",
    "latest_cycle_count": 1,
  }
  assert analytics["time_series"]["lag_trend"]["summary"] == {
    "peak_lag_bucket_key": "2025-01-03",
    "peak_lag_bucket_label": "Jan 03",
    "peak_lag_seconds": 600,
    "latest_bucket_key": "2025-01-05",
    "latest_bucket_label": "Jan 05",
    "latest_lag_seconds": 0,
    "latest_due_report_count": 0,
    "latest_failure_count": 1,
  }
  assert analytics["recent_history"][0]["status"] == "failed"
  assert analytics["current"]["status"] == "failed"


def test_guarded_live_alert_history_persists_and_resolves_reconciliation_alerts(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 30, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(targets=("operator_console", "operator_webhook"))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.3, free=0.3, used=0.0),
        ),
      )
    ),
    guarded_live_execution_enabled=True,
  )

  status = app.run_guarded_live_reconciliation(
    actor="operator",
    reason="pre_live_balance_check",
  )
  visibility = app.get_operator_visibility()

  reconciliation_alert = next(
    alert for alert in visibility.alerts
    if alert.alert_id == "guarded-live:reconciliation"
  )

  assert status.active_alerts[0].alert_id == "guarded-live:reconciliation"
  assert reconciliation_alert.source == "guarded_live"
  assert "control_room" in reconciliation_alert.delivery_targets
  history_alert = next(
    alert for alert in visibility.alert_history
    if alert.alert_id == "guarded-live:reconciliation"
  )
  assert history_alert.status == "active"
  assert history_alert.resolved_at is None
  assert visibility.incident_events[0].kind == "incident_opened"
  assert visibility.incident_events[0].alert_id == "guarded-live:reconciliation"
  assert visibility.incident_events[0].delivery_state == "delivered"
  assert {record.target for record in visibility.delivery_history[:2]} == {
    "operator_console",
    "operator_webhook",
  }
  assert delivery.delivered_incidents[0].kind == "incident_opened"

  clock.advance(timedelta(minutes=5))
  app._venue_state = StaticVenueStateAdapter(
    GuardedLiveVenueStateSnapshot(
      provider="seeded",
      venue="binance",
      verification_state="verified",
      captured_at=clock(),
    )
  )
  app.run_guarded_live_reconciliation(
    actor="operator",
    reason="post_fix_balance_check",
  )
  resolved_visibility = app.get_operator_visibility()

  assert all(
    alert.alert_id != "guarded-live:reconciliation"
    for alert in resolved_visibility.alerts
  )
  resolved_history_alert = next(
    alert for alert in resolved_visibility.alert_history
    if alert.alert_id == "guarded-live:reconciliation"
  )
  assert resolved_history_alert.status == "resolved"
  assert resolved_history_alert.resolved_at == clock()
  assert resolved_visibility.incident_events[0].kind == "incident_resolved"
  assert resolved_visibility.incident_events[0].alert_id == "guarded-live:reconciliation"
  assert delivery.delivered_incidents[-1].kind == "incident_resolved"

  restarted = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
      )
    ),
    guarded_live_execution_enabled=True,
  )
  restarted_visibility = restarted.get_operator_visibility()
  restarted_history_alert = next(
    alert for alert in restarted_visibility.alert_history
    if alert.alert_id == "guarded-live:reconciliation"
  )
  assert restarted_history_alert.status == "resolved"
  assert restarted_history_alert.resolved_at == clock()
  assert restarted_visibility.incident_events[0].kind == "incident_resolved"


def test_operator_visibility_surfaces_guarded_live_worker_failure_and_persists_history(
  monkeypatch,
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 45, tzinfo=UTC))
  market_data = MutableSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    operator_alert_delivery=delivery,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),
        ),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="operator_visibility_live_failure",
  )

  def fail_advance(_run: RunRecord) -> dict[str, int]:
    raise RuntimeError("live worker crash")

  monkeypatch.setattr(app, "_advance_guarded_live_worker_run", fail_advance)
  app.maintain_guarded_live_worker_sessions()
  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  failure_alert = next(
    alert
    for alert in visibility.alerts
    if alert.category == "worker_failure" and alert.run_id == run.config.run_id
  )
  assert failure_alert.source == "guarded_live"
  assert failure_alert.symbol == "ETH/USDT"
  assert failure_alert.symbols == ("ETH/USDT",)
  assert failure_alert.timeframe == "5m"
  assert "operator_visibility" in failure_alert.delivery_targets
  assert any(event.kind == "guarded_live_worker_failed" for event in visibility.audit_events)
  assert any(alert.alert_id == failure_alert.alert_id for alert in guarded_live_status.active_alerts)
  history_alert = next(
    alert
    for alert in visibility.alert_history
    if alert.alert_id == failure_alert.alert_id
  )
  assert history_alert.status == "active"
  assert any(
    event.kind == "incident_opened" and event.alert_id == failure_alert.alert_id
    for event in guarded_live_status.incident_events
  )
  failure_incident = next(
    event
    for event in guarded_live_status.incident_events
    if event.kind == "incident_opened" and event.alert_id == failure_alert.alert_id
  )
  assert failure_incident.symbol == "ETH/USDT"
  assert failure_incident.symbols == ("ETH/USDT",)
  assert failure_incident.timeframe == "5m"
  assert any(
    record.target == "operator_console" and record.alert_id == failure_alert.alert_id
    for record in guarded_live_status.delivery_history
  )
  assert any(incident.alert_id == failure_alert.alert_id for incident in delivery.delivered_incidents)


def test_operator_visibility_persists_risk_breach_and_live_fault_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 13, 5, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=MutableSeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    operator_alert_delivery=delivery,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="operator_visibility_risk_faults",
  )
  assert run.provenance.runtime_session is not None
  run.provenance.runtime_session.recovery_count = 2
  run.provenance.runtime_session.last_recovered_at = clock.current - timedelta(minutes=1)
  run.provenance.runtime_session.last_recovery_reason = "heartbeat_timeout"
  run.metrics["max_drawdown_pct"] = 42.0
  run.orders.append(
    Order(
      run_id=run.config.run_id,
      instrument_id="binance:ETH/USDT",
      side=OrderSide.BUY,
      quantity=0.15,
      requested_price=3_200.0,
      order_type=OrderType.LIMIT,
      status=OrderStatus.OPEN,
      order_id="stale-live-order-1",
      created_at=clock.current - timedelta(minutes=10),
      updated_at=clock.current - timedelta(minutes=9),
      last_synced_at=clock.current - timedelta(minutes=8),
      remaining_quantity=0.15,
    )
  )
  runs.save_run(run)

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  categories = {
    alert.category
    for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.source == "guarded_live"
  }
  assert {"risk_breach", "runtime_recovery", "order_sync"} <= categories
  assert any(
    event.kind == "incident_opened" and event.alert_id.startswith("guarded-live:risk-breach:")
    for event in guarded_live_status.incident_events
  )
  assert any(
    record.alert_id.startswith("guarded-live:order-sync:")
    for record in guarded_live_status.delivery_history
  )
  assert any(
    incident.alert_id.startswith("guarded-live:recovery-loop:")
    for incident in delivery.delivered_incidents
  )


def test_operator_visibility_persists_market_data_freshness_and_wider_risk_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 0, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    operator_alert_delivery=delivery,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
    market_data_sync_timeframes=("5m",),
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="operator_visibility_market_data_risk",
  )
  market_data.set_status(
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current - timedelta(minutes=20),
          sync_status="stale",
          lag_seconds=1_200,
          last_sync_at=clock.current - timedelta(minutes=15),
          recent_failures=(
            SyncFailure(
              failed_at=clock.current - timedelta(minutes=9),
              operation="sync_recent",
              error="exchange timeout",
            ),
          ),
          failure_count_24h=2,
          backfill_target_candles=400,
          backfill_completion_ratio=0.72,
          backfill_complete=False,
          backfill_contiguous_completion_ratio=0.91,
          backfill_contiguous_complete=False,
          backfill_contiguous_missing_candles=3,
          backfill_gap_windows=(
            GapWindow(
              start_at=clock.current - timedelta(hours=2),
              end_at=clock.current - timedelta(hours=2) + timedelta(minutes=10),
              missing_candles=3,
            ),
          ),
          issues=(
            "lagging",
            "freshness_threshold_exceeded:1200:600",
            "missing_candles:3",
            "backfill_target_incomplete:288:400",
            "contiguous_backfill_incomplete:3",
            "gap_windows:1",
            "repeated_sync_failures:2",
            "binance_timeout",
          ),
        ),
      ],
    ),
  )
  run.metrics["total_return_pct"] = -24.0
  run.orders.append(
    Order(
      run_id=run.config.run_id,
      instrument_id="binance:ETH/USDT",
      side=OrderSide.BUY,
      quantity=4.0,
      requested_price=3_200.0,
      order_type=OrderType.LIMIT,
      status=OrderStatus.OPEN,
      order_id="pending-risk-order-1",
      created_at=clock.current - timedelta(minutes=6),
      updated_at=clock.current - timedelta(minutes=6),
      last_synced_at=clock.current - timedelta(seconds=30),
      remaining_quantity=4.0,
    )
  )
  runs.save_run(run)

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  active_categories = {alert.category for alert in visibility.alerts if alert.source == "guarded_live"}
  assert {
    "market_data_freshness",
    "market_data_quality",
    "market_data_candle_continuity",
    "market_data_venue",
    "risk_breach",
  } <= active_categories
  market_data_alert = next(
    alert for alert in visibility.alerts
    if alert.category == "market_data_freshness"
  )
  assert "ETH/USDT lagged 1200s." in market_data_alert.detail
  assert market_data_alert.symbol == "ETH/USDT"
  assert market_data_alert.symbols == ("ETH/USDT",)
  assert market_data_alert.timeframe == "5m"
  market_data_quality_alert = next(
    alert for alert in visibility.alerts
    if alert.category == "market_data_quality"
  )
  assert "backfill target covers 72.00%" in market_data_quality_alert.detail
  market_data_continuity_alert = next(
    alert for alert in visibility.alerts
    if alert.category == "market_data_candle_continuity"
  )
  assert "has 3 missing candle(s) across 1 gap window(s)." in market_data_continuity_alert.detail
  assert "contiguous backfill quality is 91.00%" in market_data_continuity_alert.detail
  market_data_venue_alert = next(
    alert for alert in visibility.alerts
    if alert.category == "market_data_venue"
  )
  assert "recorded 2 sync failure(s)" in market_data_venue_alert.detail
  assert "venue semantics: timeout" in market_data_venue_alert.detail
  risk_alert = next(
    alert for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.category == "risk_breach"
  )
  assert "total return -24.00%" in risk_alert.detail
  assert "gross open risk reached" in risk_alert.detail
  assert risk_alert.symbol == "ETH/USDT"
  assert risk_alert.symbols == ("ETH/USDT",)
  assert risk_alert.timeframe == "5m"
  market_data_incident = next(
    event
    for event in guarded_live_status.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )
  assert market_data_incident.symbol == "ETH/USDT"
  assert market_data_incident.symbols == ("ETH/USDT",)
  assert market_data_incident.timeframe == "5m"
  assert any(
    event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == "guarded-live:market-data-quality:binance:5m"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == "guarded-live:market-data-continuity:binance:5m"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == "guarded-live:market-data-venue:binance:5m"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened" and event.alert_id.startswith("guarded-live:risk-breach:")
    for event in guarded_live_status.incident_events
  )
  assert any(
    record.alert_id == "guarded-live:market-data:5m"
    for record in guarded_live_status.delivery_history
  )
  assert any(
    record.alert_id == "guarded-live:market-data-quality:binance:5m"
    for record in guarded_live_status.delivery_history
  )
  assert any(
    record.alert_id == "guarded-live:market-data-continuity:binance:5m"
    for record in guarded_live_status.delivery_history
  )


def test_multi_symbol_market_data_alerts_embed_primary_focus_metadata(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 0, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    operator_alert_delivery=FakeOperatorAlertDeliveryAdapter(),
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
    market_data_sync_timeframes=("5m",),
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="multi_symbol_primary_focus",
  )
  secondary_run = replace(
    run,
    config=replace(
      run.config,
      run_id="live-run-btc-primary-focus",
      symbols=("BTC/USDT",),
    ),
    provenance=replace(
      run.provenance,
      runtime_session=replace(
        run.provenance.runtime_session,
        session_id="worker-live-btc-primary-focus",
      ) if run.provenance.runtime_session is not None else None,
    ),
    orders=[],
    fills=[],
    positions={},
    equity_curve=[],
    closed_trades=[],
    metrics={},
    notes=list(run.notes),
  )
  runs.save_run(secondary_run)
  market_data.set_status(
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:BTC/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current - timedelta(minutes=18),
          sync_status="stale",
          lag_seconds=1_080,
          last_sync_at=clock.current - timedelta(minutes=12),
          failure_count_24h=2,
          backfill_gap_windows=(
            GapWindow(
              start_at=clock.current - timedelta(hours=1),
              end_at=clock.current - timedelta(hours=1) + timedelta(minutes=10),
              missing_candles=2,
            ),
          ),
          issues=("freshness_threshold_exceeded:1080:600", "repeated_sync_failures:2"),
        ),
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current - timedelta(minutes=1),
          sync_status="synced",
          lag_seconds=0,
          last_sync_at=clock.current - timedelta(minutes=1),
          issues=(),
        ),
      ],
    ),
  )

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  market_data_alert = next(
    alert for alert in visibility.alerts
    if alert.category == "market_data_freshness"
  )
  assert market_data_alert.symbol is None
  assert market_data_alert.symbols == ("BTC/USDT", "ETH/USDT")
  assert market_data_alert.primary_focus is not None
  assert market_data_alert.primary_focus.symbol == "BTC/USDT"
  assert market_data_alert.primary_focus.timeframe == "5m"
  assert market_data_alert.primary_focus.candidate_symbols == ("BTC/USDT", "ETH/USDT")
  assert market_data_alert.primary_focus.candidate_count == 2
  assert market_data_alert.primary_focus.policy == "market_data_risk_order"
  assert "highest-risk market-data candidate" in (market_data_alert.primary_focus.reason or "")

  market_data_incident = next(
    event
    for event in guarded_live_status.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )
  assert market_data_incident.symbol is None
  assert market_data_incident.symbols == ("BTC/USDT", "ETH/USDT")
  assert market_data_incident.primary_focus == market_data_alert.primary_focus


def test_market_data_incidents_request_remediation_and_provider_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 30, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    supported_workflow_providers=("pagerduty",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    operator_alert_delivery=delivery,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
    market_data_sync_timeframes=("5m",),
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="market_data_remediation_provider_workflow",
  )
  market_data.set_status(
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current - timedelta(minutes=20),
          sync_status="stale",
          lag_seconds=1_200,
          last_sync_at=clock.current - timedelta(minutes=15),
          issues=("freshness_threshold_exceeded:1200:600",),
        ),
      ],
    ),
  )

  guarded_live_status = app.get_guarded_live_status()
  incident = next(
    event
    for event in guarded_live_status.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )
  assert incident.remediation.kind == "recent_sync"
  assert incident.remediation.state == "skipped"
  assert incident.remediation.summary == "Refresh the live timeframe sync window and verify freshness thresholds."
  assert incident.remediation.runbook == "market_data.sync_recent"
  assert incident.remediation.provider == "pagerduty"
  assert incident.remediation.reference == "guarded-live:market-data:5m"
  assert incident.remediation.requested_by == "system"
  assert "seeded_market_data_provider_has_no_live_remediation_jobs" in incident.remediation.detail
  assert incident.remediation.provider_recovery.lifecycle_state == "requested"
  assert incident.remediation.provider_recovery.status_machine.state == "provider_requested"
  assert incident.remediation.provider_recovery.status_machine.workflow_state == "delivered"
  assert incident.remediation.provider_recovery.status_machine.workflow_action == "remediate"
  assert incident.remediation.provider_recovery.status_machine.job_state == "requested"
  assert incident.remediation.provider_recovery.status_machine.sync_state == "local_dispatched"
  assert market_data.remediation_calls[-1] == ("recent_sync", "ETH/USDT", "5m")
  assert any(
    workflow_event_id == incident.event_id and provider == "pagerduty" and action == "remediate"
    for workflow_event_id, provider, action, _ in delivery.workflow_attempts
  )
  workflow_payload = next(
    payload
    for workflow_event_id, provider, action, payload in delivery.workflow_payloads
    if workflow_event_id == incident.event_id and provider == "pagerduty" and action == "remediate"
  )
  assert workflow_payload["market_context"] == {
    "symbol": "ETH/USDT",
    "symbols": ["ETH/USDT"],
    "timeframe": "5m",
    "primary_focus": {
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "candidate_symbols": ["ETH/USDT"],
      "candidate_count": 1,
      "policy": "single_symbol_context",
      "reason": "Alert context resolved to one market-data instrument.",
    },
  }
  remediation_delivery = next(
    record
    for record in guarded_live_status.delivery_history
    if record.incident_event_id == incident.event_id and record.phase == "provider_remediate"
  )
  assert remediation_delivery.external_provider == "pagerduty"

  market_data.set_remediation_status(
    kind="recent_sync",
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current,
          sync_status="synced",
          lag_seconds=0,
          last_sync_at=clock.current,
          issues=(),
        ),
      ],
    ),
  )

  updated_status = app.remediate_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="manual_market_data_resync",
  )
  refreshed_incident = next(
    event
    for event in updated_status.incident_events
    if event.event_id == incident.event_id
  )
  assert refreshed_incident.remediation.state == "executed"
  assert refreshed_incident.remediation.requested_by == "operator"
  assert "recent_sync:ETH/USDT:5m:status_repaired" in refreshed_incident.remediation.detail
  assert market_data.remediation_calls[-1] == ("recent_sync", "ETH/USDT", "5m")
  assert any(
    event.kind == "incident_resolved" and event.alert_id == "guarded-live:market-data:5m"
    for event in updated_status.incident_events
  )
  assert all(
    alert.alert_id != "guarded-live:market-data:5m"
    for alert in updated_status.active_alerts
  )
  assert any(
    workflow_event_id == incident.event_id and provider == "pagerduty" and action == "remediate"
    for workflow_event_id, provider, action, _ in delivery.workflow_attempts[1:]
  )
  assert any(
    event.kind == "guarded_live_incident_remediation_requested"
    for event in updated_status.audit_events
  )


def test_market_data_incidents_auto_remediate_on_incident_open(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 0, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  guarded_live_state = build_guarded_live_repository(tmp_path)
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    supported_workflow_providers=("pagerduty",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    guarded_live_state=guarded_live_state,
    clock=clock,
    operator_alert_delivery=delivery,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
    market_data_sync_timeframes=("5m",),
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="auto_market_data_remediation",
  )
  market_data.set_status(
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current - timedelta(minutes=20),
          sync_status="stale",
          lag_seconds=1_200,
          last_sync_at=clock.current - timedelta(minutes=15),
          issues=("freshness_threshold_exceeded:1200:600",),
        ),
      ],
    ),
  )
  market_data.set_remediation_status(
    kind="recent_sync",
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current,
          sync_status="synced",
          lag_seconds=0,
          last_sync_at=clock.current,
          issues=(),
        ),
      ],
    ),
  )

  guarded_live_status = app.get_guarded_live_status()

  incident = next(
    event
    for event in guarded_live_status.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )
  assert incident.remediation.state == "executed"
  assert incident.remediation.requested_by == "system"
  assert market_data.remediation_calls[-1] == ("recent_sync", "ETH/USDT", "5m")
  assert any(
    event.kind == "incident_resolved" and event.alert_id == "guarded-live:market-data:5m"
    for event in guarded_live_status.incident_events
  )
  assert all(
    alert.alert_id != "guarded-live:market-data:5m"
    for alert in guarded_live_status.active_alerts
  )
  assert any(
    workflow_event_id == incident.event_id and provider == "pagerduty" and action == "remediate"
    for workflow_event_id, provider, action, _ in delivery.workflow_attempts
  )


def test_external_market_data_recovery_sync_executes_local_verification_and_resolves_incident(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 30, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    supported_workflow_providers=("pagerduty",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    guarded_live_state=guarded_live_state,
    clock=clock,
    operator_alert_delivery=delivery,
    operator_alert_paging_policy_default_provider="pagerduty",
    operator_alert_paging_policy_warning_targets=("pagerduty_events",),
    operator_alert_paging_policy_critical_targets=("pagerduty_events",),
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
    market_data_sync_timeframes=("5m",),
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="provider_market_data_recovery_sync",
  )
  market_data.set_status(
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current - timedelta(minutes=20),
          sync_status="stale",
          lag_seconds=1_200,
          last_sync_at=clock.current - timedelta(minutes=15),
          issues=("freshness_threshold_exceeded:1200:600",),
        ),
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )
  assert incident.remediation.state == "skipped"

  market_data.set_remediation_status(
    kind="recent_sync",
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current,
          sync_status="synced",
          lag_seconds=0,
          last_sync_at=clock.current,
          issues=(),
        ),
      ],
    ),
  )

  synced = app.sync_guarded_live_incident_from_external(
    provider="pagerduty",
    event_kind="remediation_completed",
    actor="pagerduty",
    detail="provider_market_data_recovered",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="PDINC-REC-1",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "recovery-job-1",
      "summary": "provider verified market-data recovery",
      "channels": ["kline", "depth"],
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "verification": {"state": "passed"},
      "telemetry": {
        "state": "completed",
        "progress_percent": 100,
        "attempt_count": 3,
        "current_step": "verification",
        "last_message": "provider repair verified",
        "external_run_id": "pd-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.state == "executed"
  assert updated_incident.remediation.requested_by == "pagerduty:pagerduty"
  assert updated_incident.remediation.provider_payload == {
    "job_id": "recovery-job-1",
    "summary": "provider verified market-data recovery",
    "channels": ["kline", "depth"],
    "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
    "verification": {"state": "passed"},
    "telemetry": {
      "state": "completed",
      "progress_percent": 100,
      "attempt_count": 3,
      "current_step": "verification",
      "last_message": "provider repair verified",
      "external_run_id": "pd-telemetry-1",
    },
  }
  assert updated_incident.remediation.provider_recovery.lifecycle_state == "verified"
  assert updated_incident.remediation.provider_recovery.provider == "pagerduty"
  assert updated_incident.remediation.provider_recovery.job_id == "recovery-job-1"
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "pagerduty"
  assert updated_incident.remediation.provider_recovery.pagerduty.incident_id == "PDINC-REC-1"
  assert updated_incident.remediation.provider_recovery.pagerduty.incident_status == "delivered"
  assert updated_incident.remediation.provider_recovery.pagerduty.phase_graph.workflow_phase == "verified_pending_resolve"
  assert updated_incident.remediation.provider_recovery.pagerduty.phase_graph.incident_phase == "unknown"
  assert updated_incident.remediation.provider_recovery.channels == ("kline", "depth")
  assert updated_incident.remediation.provider_recovery.symbols == ("ETH/USDT",)
  assert updated_incident.remediation.provider_recovery.timeframe == "5m"
  assert updated_incident.remediation.provider_recovery.verification.state == "passed"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "completed"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 100
  assert updated_incident.remediation.provider_recovery.telemetry.attempt_count == 3
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verification"
  assert updated_incident.remediation.provider_recovery.telemetry.external_run_id == "pd-telemetry-1"
  assert updated_incident.remediation.provider_recovery.status_machine.state == "verified"
  assert updated_incident.remediation.provider_recovery.status_machine.workflow_state == "delivered"
  assert updated_incident.remediation.provider_recovery.status_machine.workflow_action == "remediate"
  assert updated_incident.remediation.provider_recovery.status_machine.job_state == "verified"
  assert updated_incident.remediation.provider_recovery.status_machine.sync_state == "bidirectional_synced"
  assert updated_incident.remediation.provider_recovery.status_machine.last_event_kind == "local_verification_executed"
  assert updated_incident.remediation.provider_recovery.status_machine.attempt_number == 1
  assert updated_incident.provider_workflow_action == "remediate"
  assert updated_incident.provider_workflow_state == "delivered"
  assert updated_incident.provider_workflow_reference == "PDINC-REC-1"
  resolved_incident = next(
    event
    for event in synced.incident_events
    if event.kind == "incident_resolved" and event.alert_id == incident.alert_id
  )
  assert resolved_incident.provider_workflow_action == "resolve"
  assert resolved_incident.provider_workflow_state == "delivered"
  assert resolved_incident.provider_workflow_reference == "PDINC-REC-1"
  assert resolved_incident.remediation.provider_payload["job_id"] == "recovery-job-1"
  assert resolved_incident.remediation.provider_recovery.job_id == "recovery-job-1"
  assert resolved_incident.remediation.provider_recovery.verification.state == "passed"
  assert resolved_incident.remediation.provider_recovery.lifecycle_state == "resolved"
  assert resolved_incident.remediation.provider_recovery.status_machine.state == "resolved"
  assert resolved_incident.remediation.provider_recovery.status_machine.workflow_action == "resolve"
  assert resolved_incident.remediation.provider_recovery.status_machine.job_state == "resolved"
  assert resolved_incident.remediation.provider_recovery.status_machine.sync_state == "bidirectional_synced"
  assert resolved_incident.remediation.provider_recovery.status_machine.last_event_kind == "provider_resolve_requested"
  assert any(
    record.phase == "provider_remediate"
    and record.external_reference == "PDINC-REC-1"
    for record in synced.delivery_history
  )
  assert any(
    record.incident_event_id == resolved_incident.event_id
    and record.phase == "provider_resolve"
    and record.external_reference == "PDINC-REC-1"
    for record in synced.delivery_history
  )
  assert any(
    workflow_event_id == resolved_incident.event_id and provider == "pagerduty" and action == "resolve"
    for workflow_event_id, provider, action, _ in delivery.workflow_attempts
  )
  assert any(
    workflow_event_id == resolved_incident.event_id
    and provider == "pagerduty"
    and action == "resolve"
    and payload is not None
    and payload.get("remediation", {}).get("provider_payload", {}).get("job_id") == "recovery-job-1"
    and payload.get("remediation", {}).get("provider_recovery", {}).get("job_id") == "recovery-job-1"
    for workflow_event_id, provider, action, payload in delivery.workflow_payloads
  )
  assert any(
    event.kind == "guarded_live_incident_external_synced"
    and "Local remediation: recent_sync:ETH/USDT:5m:status_repaired" in event.detail
    for event in synced.audit_events
  )


def test_provider_pull_sync_reconciles_recovery_state_and_closes_market_data_incident(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 45, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    supported_workflow_providers=("pagerduty",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    guarded_live_state=guarded_live_state,
    clock=clock,
    operator_alert_delivery=delivery,
    operator_alert_paging_policy_default_provider="pagerduty",
    operator_alert_paging_policy_warning_targets=("pagerduty_events",),
    operator_alert_paging_policy_critical_targets=("pagerduty_events",),
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
    market_data_sync_timeframes=("5m",),
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="provider_pull_sync_market_data_recovery",
  )
  market_data.set_status(
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current - timedelta(minutes=20),
          sync_status="stale",
          lag_seconds=1_200,
          last_sync_at=clock.current - timedelta(minutes=15),
          issues=("freshness_threshold_exceeded:1200:600",),
        ),
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )
  assert incident.remediation.provider_recovery.status_machine.state == "provider_requested"

  market_data.set_remediation_status(
    kind="recent_sync",
    timeframe="5m",
    status=MarketDataStatus(
      provider="binance",
      venue="binance",
      instruments=[
        InstrumentStatus(
          instrument_id="binance:ETH/USDT",
          timeframe="5m",
          candle_count=288,
          first_timestamp=clock.current - timedelta(hours=24),
          last_timestamp=clock.current,
          sync_status="synced",
          lag_seconds=0,
          last_sync_at=clock.current,
          issues=(),
        ),
      ],
    ),
  )
  delivery.set_pull_sync(
    provider="pagerduty",
    reference="guarded-live:market-data:5m",
    snapshot=OperatorIncidentProviderPullSync(
      provider="pagerduty",
      workflow_reference="PDINC-PULL-1",
      external_reference="guarded-live:market-data:5m",
      workflow_state="acknowledged",
      remediation_state="provider_recovered",
      detail="provider authoritatively completed recovery job",
      payload={
        "job_id": "pd-job-77",
        "channels": ["kline", "depth"],
        "symbol": "ETH/USDT",
        "symbols": ["ETH/USDT"],
        "timeframe": "5m",
        "primary_focus": {
          "symbol": "ETH/USDT",
          "timeframe": "5m",
          "candidate_symbols": ["ETH/USDT"],
          "candidate_count": 1,
          "policy": "single_symbol_context",
          "reason": "Alert context resolved to one market-data instrument.",
        },
        "market_context_provenance": {
          "provider": "pagerduty",
          "vendor_field": "custom_details",
          "symbol": {
            "scope": "provider_payload",
            "path": "custom_details.market_context.symbol",
          },
          "symbols": {
            "scope": "provider_payload",
            "path": "custom_details.market_context.symbols",
          },
          "timeframe": {
            "scope": "provider_payload",
            "path": "custom_details.market_context.timeframe",
          },
          "primary_focus": {
            "scope": "provider_payload",
            "path": "custom_details.market_context.primary_focus",
          },
        },
        "targets": {
          "symbol": "ETH/USDT",
          "symbols": ["ETH/USDT"],
          "timeframe": "5m",
          "primary_focus": {
            "symbol": "ETH/USDT",
            "timeframe": "5m",
            "candidate_symbols": ["ETH/USDT"],
            "candidate_count": 1,
            "policy": "single_symbol_context",
            "reason": "Alert context resolved to one market-data instrument.",
          },
        },
        "verification": {"state": "passed"},
        "telemetry": {
          "state": "completed",
          "progress_percent": 100,
          "attempt_count": 2,
          "current_step": "verification",
          "last_message": "provider authoritative repair complete",
          "external_run_id": "pd-run-77",
        },
        "status_machine": {
          "state": "provider_running",
          "workflow_state": "acknowledged",
          "workflow_action": "remediate",
          "job_state": "completed",
          "sync_state": "provider_authoritative",
        },
      },
      synced_at=clock.current + timedelta(minutes=1),
    ),
  )

  reconciled = app.get_guarded_live_status()

  updated_incident = next(
    event
    for event in reconciled.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.state == "executed"
  assert updated_incident.remediation.requested_by == "pagerduty:pull_sync"
  assert updated_incident.remediation.provider_recovery.job_id == "pd-job-77"
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "pagerduty"
  assert updated_incident.remediation.provider_recovery.pagerduty.incident_id == "PDINC-PULL-1"
  assert updated_incident.remediation.provider_recovery.pagerduty.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.pagerduty.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.pagerduty.phase_graph.workflow_phase == "verified_pending_resolve"
  assert updated_incident.remediation.provider_recovery.channels == ("kline", "depth")
  assert updated_incident.symbol == "ETH/USDT"
  assert updated_incident.symbols == ("ETH/USDT",)
  assert updated_incident.timeframe == "5m"
  assert updated_incident.primary_focus is not None
  assert updated_incident.primary_focus.symbol == "ETH/USDT"
  assert updated_incident.primary_focus.timeframe == "5m"
  assert updated_incident.remediation.provider_recovery.primary_focus == updated_incident.primary_focus
  assert updated_incident.remediation.provider_recovery.market_context_provenance is not None
  assert updated_incident.remediation.provider_recovery.market_context_provenance.provider == "pagerduty"
  assert updated_incident.remediation.provider_recovery.market_context_provenance.vendor_field == "custom_details"
  assert (
    updated_incident.remediation.provider_recovery.market_context_provenance.symbol.path
    == "custom_details.market_context.symbol"
  )
  assert (
    updated_incident.remediation.provider_recovery.market_context_provenance.primary_focus.path
    == "custom_details.market_context.primary_focus"
  )
  assert updated_incident.remediation.provider_recovery.telemetry.state == "completed"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 100
  assert updated_incident.remediation.provider_recovery.telemetry.attempt_count == 2
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verification"
  assert updated_incident.remediation.provider_recovery.status_machine.workflow_state == "acknowledged"
  assert updated_incident.remediation.provider_recovery.status_machine.sync_state == "bidirectional_synced"
  assert any(
    event.kind == "incident_resolved" and event.alert_id == "guarded-live:market-data:5m"
    for event in reconciled.incident_events
  )
  assert all(
    alert.alert_id != "guarded-live:market-data:5m"
    for alert in reconciled.active_alerts
  )
  assert any(
    attempt[0] == incident.event_id and attempt[1] == "pagerduty"
    for attempt in delivery.pull_sync_attempts
  )
  assert any(
    event.kind == "guarded_live_incident_provider_pull_synced"
    and "Workflow state: acknowledged." in event.detail
    for event in reconciled.audit_events
  )


def test_guarded_live_kill_switch_stops_operator_control_sessions_and_blocks_restarts(
  tmp_path: Path,
) -> None:
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
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  status = app.engage_guarded_live_kill_switch(
    actor="operator",
    reason="manual_safety_drill",
  )

  reloaded_sandbox = app.get_run(sandbox_run.config.run_id)
  reloaded_paper = app.get_run(paper_run.config.run_id)

  assert status.kill_switch.state == "engaged"
  assert status.kill_switch.updated_by == "operator"
  assert status.running_sandbox_count == 0
  assert status.running_paper_count == 0
  assert status.audit_events[0].kind == "guarded_live_kill_switch_engaged"
  assert reloaded_sandbox is not None
  assert reloaded_sandbox.status == RunStatus.STOPPED
  assert "guarded-live kill switch" in reloaded_sandbox.notes[-1]
  assert reloaded_paper is not None
  assert reloaded_paper.status == RunStatus.STOPPED
  assert "guarded-live kill switch" in reloaded_paper.notes[-1]

  with pytest.raises(ValueError, match="kill switch"):
    app.start_sandbox_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      replay_bars=24,
    )


def test_guarded_live_reconciliation_records_runtime_findings(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    sandbox_worker_heartbeat_interval_seconds=5,
    sandbox_worker_heartbeat_timeout_seconds=15,
  )

  app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )
  clock.advance(timedelta(seconds=20))

  status = app.run_guarded_live_reconciliation(
    actor="operator",
    reason="pre_live_reconciliation_drill",
  )

  assert status.reconciliation.state == "issues_detected"
  assert status.reconciliation.checked_by == "operator"
  assert any(
    finding.kind == "runtime_alerts_present"
    for finding in status.reconciliation.findings
  )
  assert status.audit_events[0].kind == "guarded_live_reconciliation_ran"
  assert "Guarded-live reconciliation has not been cleared." in status.blockers


def test_guarded_live_reconciliation_verifies_venue_state_against_internal_exposure(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 0, tzinfo=UTC))
  venue_snapshot = GuardedLiveVenueStateSnapshot(
    provider="seeded",
    venue="binance",
    verification_state="verified",
    captured_at=clock(),
    balances=(
      GuardedLiveVenueBalance(asset="ETH", total=0.25, free=0.2, used=0.05),
      GuardedLiveVenueBalance(asset="USDT", total=9_500.0, free=9_500.0, used=0.0),
    ),
    open_orders=(
      GuardedLiveVenueOpenOrder(
        order_id="venue-order-1",
        symbol="ETH/USDT",
        side="buy",
        amount=0.25,
        status="open",
        price=2_100.0,
      ),
    ),
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    venue_state=StaticVenueStateAdapter(venue_snapshot),
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )
  run.positions = {
    "binance:ETH/USDT": Position(
      instrument_id="binance:ETH/USDT",
      quantity=1.0,
      average_price=2_000.0,
      opened_at=clock(),
      updated_at=clock(),
    )
  }
  runs.save_run(run)

  status = app.run_guarded_live_reconciliation(
    actor="operator",
    reason="venue_state_drill",
  )

  assert status.reconciliation.scope == "venue_state"
  assert status.reconciliation.venue_snapshot is not None
  assert status.reconciliation.venue_snapshot.verification_state == "verified"
  assert status.reconciliation.internal_snapshot is not None
  assert status.reconciliation.internal_snapshot.exposures[0].instrument_id == "binance:ETH/USDT"
  assert any(
    finding.kind == "venue_balance_mismatch"
    for finding in status.reconciliation.findings
  )
  assert any(
    finding.kind == "venue_open_order_mismatch"
    for finding in status.reconciliation.findings
  )


def test_guarded_live_runtime_recovery_uses_last_verified_venue_snapshot_after_fault(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 30, tzinfo=UTC))
  verified_snapshot = GuardedLiveVenueStateSnapshot(
    provider="seeded",
    venue="binance",
    verification_state="verified",
    captured_at=clock(),
    balances=(
      GuardedLiveVenueBalance(asset="ETH", total=0.75, free=0.5, used=0.25),
      GuardedLiveVenueBalance(asset="USDT", total=9_250.0, free=9_250.0, used=0.0),
    ),
    open_orders=(
      GuardedLiveVenueOpenOrder(
        order_id="venue-order-2",
        symbol="ETH/USDT",
        side="sell",
        amount=0.25,
        status="open",
        price=2_200.0,
      ),
    ),
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    venue_state=StaticVenueStateAdapter(verified_snapshot),
  )

  app.run_guarded_live_reconciliation(
    actor="operator",
    reason="pre_fault_snapshot",
  )
  app._venue_state = StaticVenueStateAdapter(
    GuardedLiveVenueStateSnapshot(
      provider="binance",
      venue="binance",
      verification_state="unavailable",
      captured_at=clock(),
      issues=("temporary_venue_fault",),
    )
  )

  status = app.recover_guarded_live_runtime_state(
    actor="operator",
    reason="post_fault_recovery",
  )

  assert status.recovery.state == "recovered"
  assert status.recovery.source_verification_state == "verified"
  assert status.recovery.source_snapshot_at == verified_snapshot.captured_at
  assert status.recovery.exposures[0].instrument_id == "binance:ETH/USDT"
  assert status.recovery.exposures[0].quantity == 0.75
  assert status.recovery.open_orders[0].order_id == "venue-order-2"
  assert status.audit_events[0].kind == "guarded_live_runtime_recovered"


def test_guarded_live_launch_requires_clear_reconciliation_and_recovery(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  venue_state = StaticVenueStateAdapter(
    GuardedLiveVenueStateSnapshot(
      provider="seeded",
      venue="binance",
      verification_state="verified",
      captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
      balances=(
        GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),
      ),
    )
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    venue_state=venue_state,
    venue_execution=SeededVenueExecutionAdapter(),
    guarded_live_execution_enabled=True,
  )

  with pytest.raises(ValueError, match="reconciliation"):
    app.start_live_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
    )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")

  with pytest.raises(ValueError, match="runtime recovery"):
    app.start_live_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
    )

  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="guarded_live_drill",
  )

  assert run.status == RunStatus.RUNNING
  assert run.config.mode == RunMode.LIVE
  assert run.provenance.runtime_session is not None
  assert run.provenance.runtime_session.worker_kind == "guarded_live_native_worker"
  assert run.notes[0].startswith("Guarded live worker primed from recovered venue state")


def test_guarded_live_reconciliation_and_launch_use_configured_supported_venue(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 30, tzinfo=UTC))
  venue_state = StaticVenueStateAdapter(
    GuardedLiveVenueStateSnapshot(
      provider="seeded",
      venue="coinbase",
      verification_state="verified",
      captured_at=clock(),
      balances=(
        GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),
        GuardedLiveVenueBalance(asset="USDT", total=9_200.0, free=9_200.0, used=0.0),
      ),
    )
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    venue_state=venue_state,
    venue_execution=SeededVenueExecutionAdapter(venue="coinbase"),
    guarded_live_venue="coinbase",
    guarded_live_execution_enabled=True,
  )

  reconciliation = app.run_guarded_live_reconciliation(
    actor="operator",
    reason="coinbase_pre_live_check",
  )
  recovery = app.recover_guarded_live_runtime_state(
    actor="operator",
    reason="coinbase_pre_live_recovery",
  )
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="coinbase_guarded_live_launch",
  )

  assert reconciliation.reconciliation.venue_snapshot is not None
  assert reconciliation.reconciliation.venue_snapshot.venue == "coinbase"
  assert recovery.reconciliation.state == "clear"
  assert recovery.recovery.exposures[0].instrument_id == "coinbase:ETH/USDT"
  assert run.config.venue == "coinbase"
  assert "coinbase:ETH/USDT" in run.positions


def test_guarded_live_worker_submits_venue_order_on_new_candle(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 0, tzinfo=UTC))
  market_data = MutableSeededMarketDataAdapter()
  venue_execution = SeededVenueExecutionAdapter(clock=clock)
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(builtins=(AlwaysBuyStrategy,)),
    runs=runs,
    clock=clock,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),
        ),
      )
    ),
    venue_execution=venue_execution,
    guarded_live_execution_enabled=True,
    guarded_live_worker_heartbeat_interval_seconds=5,
    guarded_live_worker_heartbeat_timeout_seconds=15,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="always_buy_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
    operator_reason="guarded_live_buy_test",
  )

  latest_candle = market_data.get_candles(symbol="ETH/USDT", timeframe="5m")[-1]
  new_candle = Candle(
    timestamp=latest_candle.timestamp + timedelta(minutes=5),
    open=latest_candle.close,
    high=latest_candle.close * 1.001,
    low=latest_candle.close * 0.999,
    close=latest_candle.close * 1.0005,
    volume=latest_candle.volume + 25,
  )
  market_data.append_candle(symbol="ETH/USDT", candle=new_candle)
  clock.advance(timedelta(seconds=5))

  result = app.maintain_guarded_live_worker_sessions()
  updated = app.get_run(run.config.run_id)
  guarded_live_status = app.get_guarded_live_status()

  assert result == {
    "maintained": 1,
    "recovered": 0,
    "ticks_processed": 1,
    "orders_submitted": 1,
    "orders_synced": 0,
  }
  assert len(venue_execution.submitted_orders) == 1
  assert updated is not None
  assert updated.orders[-1].order_id == "seeded-live-order-1"
  assert updated.orders[-1].status == OrderStatus.FILLED
  assert len(updated.fills) == 1
  assert updated.positions["binance:ETH/USDT"].is_open
  assert updated.provenance.runtime_session is not None
  assert updated.provenance.runtime_session.processed_tick_count == 1
  assert any(event.kind == "guarded_live_order_submitted" for event in guarded_live_status.audit_events)


def test_guarded_live_worker_syncs_recovered_order_lifecycle_into_local_state(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 20, 0, tzinfo=UTC))
  market_data = MutableSeededMarketDataAdapter()
  venue_execution = SeededVenueExecutionAdapter(clock=clock)
  recovered_order_id = "venue-open-order-1"
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id=recovered_order_id,
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    ),
    venue_execution=venue_execution,
    guarded_live_execution_enabled=True,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
    operator_reason="sync_recovered_orders",
  )

  venue_execution.set_order_state(
    recovered_order_id,
    symbol="ETH/USDT",
    side="buy",
    amount=0.5,
    status="partially_filled",
    updated_at=clock(),
    average_fill_price=2_010.0,
    fee_paid=0.2,
    filled_amount=0.2,
    remaining_amount=0.3,
  )
  first_sync = app.maintain_guarded_live_worker_sessions()
  partially_synced = app.get_run(run.config.run_id)

  assert first_sync["orders_synced"] == 1
  assert partially_synced is not None
  assert partially_synced.orders[0].status == OrderStatus.PARTIALLY_FILLED
  assert partially_synced.orders[0].filled_quantity == pytest.approx(0.2)
  assert partially_synced.orders[0].remaining_quantity == pytest.approx(0.3)
  assert partially_synced.positions["binance:ETH/USDT"].quantity == pytest.approx(0.2)
  assert len(partially_synced.fills) == 1

  clock.advance(timedelta(seconds=5))
  venue_execution.set_order_state(
    recovered_order_id,
    status="filled",
    updated_at=clock(),
    average_fill_price=2_012.0,
    fee_paid=0.5,
    filled_amount=0.5,
    remaining_amount=0.0,
  )
  second_sync = app.maintain_guarded_live_worker_sessions()
  filled_synced = app.get_run(run.config.run_id)
  guarded_live_status = app.get_guarded_live_status()

  assert second_sync["orders_synced"] == 1
  assert filled_synced is not None
  assert filled_synced.orders[0].status == OrderStatus.FILLED
  assert filled_synced.orders[0].filled_quantity == pytest.approx(0.5)
  assert filled_synced.orders[0].remaining_quantity == pytest.approx(0.0)
  assert filled_synced.orders[0].filled_at == clock.current
  assert filled_synced.positions["binance:ETH/USDT"].quantity == pytest.approx(0.5)
  assert len(filled_synced.fills) == 2
  assert any(event.kind == "guarded_live_order_synced" for event in guarded_live_status.audit_events)


def test_cancel_live_order_marks_recovered_order_canceled(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 20, 30, tzinfo=UTC))
  recovered_order_id = "venue-open-order-1"
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id=recovered_order_id,
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
    operator_reason="cancel_open_order",
  )

  canceled = app.cancel_live_order(
    run_id=run.config.run_id,
    order_id=recovered_order_id,
    actor="operator",
    reason="reduce_venue_risk",
  )
  guarded_live_status = app.get_guarded_live_status()

  assert canceled.orders[0].order_id == recovered_order_id
  assert canceled.orders[0].status == OrderStatus.CANCELED
  assert canceled.orders[0].remaining_quantity == pytest.approx(0.5)
  assert any("guarded_live_order_canceled" in note for note in canceled.notes)
  assert any(event.kind == "guarded_live_order_canceled" for event in guarded_live_status.audit_events)


def test_replace_live_order_cancels_old_order_and_appends_limit_replacement(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 20, 45, tzinfo=UTC))
  recovered_order_id = "venue-open-order-1"
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id=recovered_order_id,
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    ),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
    operator_reason="replace_open_order",
  )

  replaced = app.replace_live_order(
    run_id=run.config.run_id,
    order_id=recovered_order_id,
    price=1_985.0,
    quantity=0.3,
    actor="operator",
    reason="reprice_remaining_order",
  )
  guarded_live_status = app.get_guarded_live_status()
  original_order, replacement_order = replaced.orders

  assert original_order.order_id == recovered_order_id
  assert original_order.status == OrderStatus.CANCELED
  assert replacement_order.order_id == "seeded-live-order-1"
  assert replacement_order.order_type == OrderType.LIMIT
  assert replacement_order.status == OrderStatus.OPEN
  assert replacement_order.quantity == pytest.approx(0.3)
  assert replacement_order.requested_price == pytest.approx(1_985.0)
  assert replacement_order.remaining_quantity == pytest.approx(0.3)
  assert any("guarded_live_order_replaced" in note for note in replaced.notes)
  assert any(event.kind == "guarded_live_order_replaced" for event in guarded_live_status.audit_events)


def test_guarded_live_resume_reuses_durable_order_book_and_session_ownership(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 21, 0, tzinfo=UTC))
  recovered_order_id = "venue-open-order-1"
  venue_snapshot = GuardedLiveVenueStateSnapshot(
    provider="seeded",
    venue="binance",
    verification_state="verified",
    captured_at=clock(),
    balances=(
      GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
    ),
    open_orders=(
      GuardedLiveVenueOpenOrder(
        order_id=recovered_order_id,
        symbol="ETH/USDT",
        side="buy",
        amount=0.5,
        status="open",
        price=2_000.0,
      ),
    ),
  )
  first_app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    guarded_live_state=guarded_live_state,
    clock=clock,
    venue_state=StaticVenueStateAdapter(venue_snapshot),
    venue_execution=SeededVenueExecutionAdapter(clock=clock),
    guarded_live_execution_enabled=True,
  )

  first_app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  first_app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = first_app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
    operator_reason="start_owned_session",
  )
  first_status = first_app.get_guarded_live_status()

  assert first_status.ownership.state == "owned"
  assert first_status.ownership.owner_run_id == run.config.run_id
  assert first_status.order_book.open_orders[0].order_id == recovered_order_id
  assert first_status.session_handoff.state == "active"
  assert first_status.session_handoff.transport == "seeded_stream"

  clock.advance(timedelta(seconds=5))
  resumed_execution = SeededVenueExecutionAdapter(
    clock=clock,
    restored_orders=(
      GuardedLiveVenueOrderResult(
        order_id=recovered_order_id,
        venue="binance",
        symbol="ETH/USDT",
        side="buy",
        amount=0.5,
        status="partially_filled",
        submitted_at=run.started_at,
        updated_at=clock(),
        requested_price=2_000.0,
        average_fill_price=1_998.0,
        fee_paid=0.2,
        requested_amount=0.5,
        filled_amount=0.2,
        remaining_amount=0.3,
      ),
    ),
  )
  resumed_app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    guarded_live_state=guarded_live_state,
    clock=clock,
    venue_state=StaticVenueStateAdapter(venue_snapshot),
    venue_execution=resumed_execution,
    guarded_live_execution_enabled=True,
  )

  resumed = resumed_app.resume_guarded_live_run(
    actor="operator",
    reason="process_restart_resume",
  )
  resumed_status = resumed_app.get_guarded_live_status()

  assert resumed.status == RunStatus.RUNNING
  assert resumed.provenance.runtime_session is not None
  assert resumed.provenance.runtime_session.recovery_count >= 1
  assert resumed.orders[0].status == OrderStatus.PARTIALLY_FILLED
  assert resumed.orders[0].filled_quantity == pytest.approx(0.2)
  assert resumed.orders[0].remaining_quantity == pytest.approx(0.3)
  assert len(resumed.fills) == 1
  assert any("guarded_live_worker_resumed" in note for note in resumed.notes)
  assert any("guarded_live_venue_session_restored" in note for note in resumed.notes)
  assert resumed_status.ownership.state == "owned"
  assert resumed_status.ownership.owner_run_id == run.config.run_id
  assert resumed_status.session_restore.state == "restored"
  assert resumed_status.session_restore.source == "seeded_venue_execution"
  assert resumed_status.session_restore.owner_run_id == run.config.run_id
  assert resumed_status.session_handoff.state == "active"
  assert resumed_status.session_handoff.transport == "seeded_stream"
  assert resumed_status.session_handoff.owner_run_id == run.config.run_id
  assert resumed_status.order_book.open_orders[0].order_id == recovered_order_id
  assert resumed_status.order_book.open_orders[0].amount == pytest.approx(0.3)

  prior_cursor = resumed_status.session_handoff.cursor
  clock.advance(timedelta(seconds=5))
  resumed_execution.set_order_state(
    recovered_order_id,
    symbol="ETH/USDT",
    side="buy",
    amount=0.5,
    requested_price=2_000.0,
    status="filled",
    updated_at=clock(),
    average_fill_price=1_999.0,
    fee_paid=0.3,
    filled_amount=0.5,
    remaining_amount=0.0,
  )
  maintenance = resumed_app.maintain_guarded_live_worker_sessions()
  post_sync_status = resumed_app.get_guarded_live_status()

  assert maintenance["maintained"] == 1
  assert maintenance["orders_synced"] >= 1
  synced_run = resumed_app.get_run(run.config.run_id)
  assert synced_run is not None
  assert synced_run.orders[0].status == OrderStatus.FILLED
  assert post_sync_status.session_handoff.state == "active"
  assert post_sync_status.session_handoff.cursor != prior_cursor
  assert post_sync_status.session_handoff.last_event_at == clock()
  assert post_sync_status.order_book.state == "empty"
  assert any("guarded_live_venue_session_synced" in note for note in resumed_app.get_run(run.config.run_id).notes)


def test_stop_paper_run_persists_terminal_state(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  run = app.start_paper_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  stopped = app.stop_paper_run(run.config.run_id)

  assert stopped is not None
  assert stopped.status == RunStatus.STOPPED
  assert stopped.ended_at is not None
  assert stopped.notes[-1] == "Paper run stopped by operator."

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.STOPPED
  assert reloaded.ended_at is not None
  assert reloaded.notes[-1] == "Paper run stopped by operator."


def test_run_subresource_serializer_registry_rejects_unknown_key(tmp_path: Path) -> None:
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
  )

  with pytest.raises(ValueError, match="Unsupported run subresource serializer: unknown"):
    serialize_run_subresource_response(run, subresource_key="unknown")


def test_run_subresource_serializer_registry_exposes_typed_metadata() -> None:
  contracts = list_run_subresource_contracts()
  bindings = list_run_subresource_runtime_bindings()
  orders_contract = get_run_subresource_contract("orders")
  orders_binding = get_run_subresource_runtime_binding("orders")
  positions_contract = get_run_subresource_contract("positions")
  metrics_contract = get_run_subresource_contract("metrics")
  capabilities = RunSurfaceCapabilities()
  shared_contracts = {
    contract.contract_key: contract
    for contract in capabilities.shared_contracts
  }

  assert [contract.subresource_key for contract in contracts] == ["orders", "positions", "metrics"]
  assert [binding.contract.subresource_key for binding in bindings] == ["orders", "positions", "metrics"]
  assert orders_binding.contract == orders_contract
  assert orders_contract.body_key == "orders"
  assert orders_contract.response_title == "Run order list"
  assert orders_contract.route_path == "/runs/{run_id}/orders"
  assert orders_contract.route_name == "get_run_orders"
  assert positions_contract.body_key == "positions"
  assert positions_contract.response_title == "Run positions"
  assert positions_contract.route_path == "/runs/{run_id}/positions"
  assert positions_contract.route_name == "get_run_positions"
  assert metrics_contract.body_key == "metrics"
  assert metrics_contract.response_title == "Run metrics"
  assert metrics_contract.route_path == "/runs/{run_id}/metrics"
  assert metrics_contract.route_name == "get_run_metrics"
  assert shared_contracts["subresource:orders"].schema_detail == {
    "body_key": "orders",
    "route_path": "/runs/{run_id}/orders",
    "route_name": "get_run_orders",
  }
  assert shared_contracts["subresource:orders"].title == "Run order list"
  assert shared_contracts["subresource:metrics"].member_keys == ("body:metrics", "route:get_run_metrics")

  payload = serialize_run_surface_capabilities(capabilities)

  assert payload["discovery"].keys() == {"shared_contracts"}
  assert "families" not in payload
  shared_contracts = {
    contract["contract_key"]: contract
    for contract in payload["discovery"]["shared_contracts"]
  }
  assert shared_contracts["schema:run-surface-capabilities"]["contract_kind"] == "schema_metadata"
  assert shared_contracts["schema:run-surface-capabilities"]["version"] == "run-surface-capabilities.v14"
  assert shared_contracts["schema:run-surface-capabilities"]["related_family_keys"] == [
    "comparison_eligibility",
    "strategy_schema",
    "collection_query",
    "provenance_semantics",
    "execution_controls",
  ]
  assert shared_contracts["schema:run-surface-capabilities"]["schema_detail"] == {
    "comparison_eligibility_group_order": [
      "eligible_metrics",
      "supporting_identity",
      "operational_workflow",
      "operational_order_actions",
    ],
    "family_order": [
      "comparison_eligibility",
      "strategy_schema",
      "collection_query",
      "provenance_semantics",
      "execution_controls",
    ],
    "run_subresource_contract_keys": [
      "subresource:orders",
      "subresource:positions",
      "subresource:metrics",
    ],
    "collection_query_contract_keys": [
      "query_collection:run_list",
    ],
  }
  assert shared_contracts["family:comparison_eligibility"]["contract_kind"] == "capability_family"
  assert shared_contracts["family:comparison_eligibility"]["discovery_flow"] == (
    "Shared UI contract panel and run-list boundary notes."
  )
  assert shared_contracts["family:comparison_eligibility"]["ui_surfaces"] == [
    "Run-list metric tiles",
    "Boundary note panels",
    "Order workflow gates",
  ]
  assert shared_contracts["family:comparison_eligibility"]["schema_sources"] == [
    "Run-surface capability endpoint",
    "Comparison score drill-back wiring",
    "Run-list boundary notes",
  ]
  assert shared_contracts["family:comparison_eligibility"]["policy"]["policy_key"] == (
    "comparison_surface_allowlist"
  )
  assert shared_contracts["family:comparison_eligibility"]["enforcement"]["level"] == "hard_gate"
  assert shared_contracts["family:comparison_eligibility"]["surface_rules"][0]["surface_key"] == (
    "run_list_metric_tiles"
  )
  assert "run_list_metric_tiles" in shared_contracts["family:comparison_eligibility"]["member_keys"]
  assert shared_contracts["subresource:orders"]["contract_kind"] == "run_subresource"
  assert shared_contracts["subresource:orders"]["member_keys"] == [
    "body:orders",
    "route:get_run_orders",
  ]
  assert shared_contracts["subresource:orders"]["schema_detail"] == {
    "body_key": "orders",
    "route_path": "/runs/{run_id}/orders",
    "route_name": "get_run_orders",
  }
  assert shared_contracts["query_collection:run_list"]["contract_kind"] == "query_collection_schema"
  assert shared_contracts["query_collection:run_list"]["related_family_keys"] == ["collection_query"]
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["surface_key"] == "run_list"
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["expression_param"] == "filter_expr"
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["expression_authoring"] == {
    "predicate_refs": {
      "registry_field": "predicates",
      "reference_field": "predicate_ref",
    },
    "predicate_templates": {
      "registry_field": "predicate_templates",
      "template_field": "template",
      "parameters_field": "parameters",
      "bindings_field": "bindings",
      "binding_reference_shape": {
        "binding": "<parameter_name>",
      },
    },
    "collection_nodes": {
      "field": "collection",
      "shape": {
        "path": "<collection path>",
        "path_template": "<collection path template>",
        "bindings": {
          "<parameter_key>": "<value or binding reference>",
        },
        "quantifier": "any|all|none",
      },
    },
  }
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["collection_schemas"][1]["path_template"] == [
    "provenance",
    "market_data_by_symbol",
    "{symbol_key}",
    "issues",
  ]
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["collection_schemas"][1]["parameters"][0]["domain"] == {
    "key": "market_data_symbol_key",
    "source": "run.provenance.market_data_by_symbol",
    "values": ["binance:BTC/USDT"],
    "enum_source": {
      "kind": "dynamic_map_keys",
      "surface_key": "run_list",
      "path": ["provenance", "market_data_by_symbol"],
    },
  }
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["parameter_domains"][0]["domain"] == {
    "key": "market_data_symbol_key",
    "source": "run.provenance.market_data_by_symbol",
    "values": ["binance:BTC/USDT"],
    "enum_source": {
      "kind": "dynamic_map_keys",
      "surface_key": "run_list",
      "path": ["provenance", "market_data_by_symbol"],
    },
  }
  assert shared_contracts["family:collection_query"]["contract_kind"] == "capability_family"
  assert shared_contracts["family:collection_query"]["policy"]["policy_key"] == (
    "typed_collection_query_discovery"
  )


def test_standalone_surface_runtime_bindings_cover_capabilities_and_run_subresources(tmp_path: Path) -> None:
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
  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  bindings = list_standalone_surface_runtime_bindings(app.get_run_surface_capabilities())
  bindings_by_key = {
    binding.surface_key: binding
    for binding in bindings
  }

  assert set(bindings_by_key) == {
    "health_status",
    "run_surface_capabilities",
    "replay_link_alias_create",
    "replay_link_alias_resolve",
    "replay_link_alias_history",
    "replay_link_audit_list",
    "replay_link_audit_export",
    "replay_link_audit_export_job_create",
    "replay_link_audit_export_job_list",
    "replay_link_audit_export_job_download",
    "replay_link_audit_export_job_history",
    "replay_link_audit_export_job_prune",
    "replay_link_audit_prune",
    "replay_link_alias_revoke",
    "market_data_status",
    "market_data_lineage_history",
    "market_data_ingestion_job_history",
    "market_data_lineage_evidence_retention_prune",
    "market_data_lineage_drill_evidence_pack_export",
    "operator_visibility",
    "operator_provider_provenance_export_job_create",
    "operator_provider_provenance_export_job_list",
    "operator_provider_provenance_export_analytics",
    "operator_provider_provenance_export_job_download",
    "operator_provider_provenance_export_job_history",
    "operator_provider_provenance_export_job_policy",
    "operator_provider_provenance_export_job_approval",
    "operator_provider_provenance_export_job_escalate",
    "operator_provider_provenance_analytics_preset_create",
    "operator_provider_provenance_analytics_preset_list",
    "operator_provider_provenance_dashboard_view_create",
    "operator_provider_provenance_dashboard_view_list",
    "operator_provider_provenance_scheduler_stitched_report_view_create",
    "operator_provider_provenance_scheduler_stitched_report_view_list",
    "operator_provider_provenance_scheduler_stitched_report_view_update",
    "operator_provider_provenance_scheduler_stitched_report_view_delete",
    "operator_provider_provenance_scheduler_stitched_report_view_bulk_governance",
    "operator_provider_provenance_scheduler_stitched_report_view_revision_list",
    "operator_provider_provenance_scheduler_stitched_report_view_revision_restore",
    "operator_provider_provenance_scheduler_stitched_report_view_audit_list",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_create",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_list",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_update",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_delete",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance",
    "operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list",
    "operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list",
    "operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list",
    "operator_provider_provenance_scheduler_stitched_report_governance_plan_create",
    "operator_provider_provenance_scheduler_stitched_report_governance_plan_list",
    "operator_provider_provenance_scheduler_stitched_report_governance_plan_approve",
    "operator_provider_provenance_scheduler_stitched_report_governance_plan_apply",
    "operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback",
    "operator_provider_provenance_scheduler_narrative_template_create",
    "operator_provider_provenance_scheduler_narrative_template_list",
    "operator_provider_provenance_scheduler_narrative_template_update",
    "operator_provider_provenance_scheduler_narrative_template_delete",
    "operator_provider_provenance_scheduler_narrative_template_bulk_governance",
    "operator_provider_provenance_scheduler_narrative_template_revision_list",
    "operator_provider_provenance_scheduler_narrative_template_revision_restore",
    "operator_provider_provenance_scheduler_narrative_registry_create",
    "operator_provider_provenance_scheduler_narrative_registry_list",
    "operator_provider_provenance_scheduler_narrative_registry_update",
    "operator_provider_provenance_scheduler_narrative_registry_delete",
    "operator_provider_provenance_scheduler_narrative_registry_bulk_governance",
    "operator_provider_provenance_scheduler_narrative_registry_revision_list",
    "operator_provider_provenance_scheduler_narrative_registry_revision_restore",
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_create",
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_list",
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_update",
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_delete",
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list",
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore",
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage",
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage",
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage",
    "operator_provider_provenance_scheduler_narrative_governance_plan_create",
    "operator_provider_provenance_scheduler_narrative_governance_plan_list",
    "operator_provider_provenance_scheduler_narrative_governance_plan_approve",
    "operator_provider_provenance_scheduler_narrative_governance_plan_apply",
    "operator_provider_provenance_scheduler_narrative_governance_plan_batch_action",
    "operator_provider_provenance_scheduler_narrative_governance_plan_rollback",
    "operator_provider_provenance_scheduled_report_create",
    "operator_provider_provenance_scheduled_report_list",
    "operator_provider_provenance_scheduled_report_run",
    "operator_provider_provenance_scheduled_report_run_due",
    "operator_provider_provenance_scheduled_report_history",
    "operator_provider_provenance_scheduler_health_history",
    "operator_provider_provenance_scheduler_alert_history",
    "operator_provider_provenance_scheduler_health_analytics",
    "operator_provider_provenance_scheduler_health_export",
    "guarded_live_status",
    "strategy_catalog_discovery",
    "preset_catalog_discovery",
    "preset_catalog_create",
    "preset_catalog_item_get",
    "preset_catalog_item_update",
    "preset_catalog_revision_list",
    "preset_catalog_revision_restore",
    "preset_catalog_lifecycle_apply",
    "strategy_catalog_register",
    "run_list",
    "run_compare",
    "run_backtest_launch",
    "run_backtest_item_get",
    "run_rerun_backtest",
    "run_rerun_sandbox",
    "run_rerun_paper",
    "run_sandbox_launch",
    "run_paper_launch",
    "run_live_launch",
    "operator_incident_external_sync",
    "guarded_live_kill_switch_engage",
    "guarded_live_kill_switch_release",
    "guarded_live_reconciliation",
    "guarded_live_recovery",
    "guarded_live_incident_acknowledge",
    "guarded_live_incident_remediate",
    "guarded_live_incident_escalate",
    "guarded_live_resume",
    "run_stop_sandbox",
    "run_stop_paper",
    "run_stop_live",
    "run_live_order_cancel",
    "run_live_order_replace",
    "run_subresource:orders",
    "run_subresource:positions",
    "run_subresource:metrics",
  }
  assert bindings_by_key["health_status"].scope == "app"
  assert bindings_by_key["health_status"].route_path == "/health"
  assert bindings_by_key["run_surface_capabilities"].scope == "app"
  assert bindings_by_key["run_surface_capabilities"].route_path == "/capabilities/run-surfaces"
  assert bindings_by_key["replay_link_alias_create"].methods == ("POST",)
  assert bindings_by_key["replay_link_alias_resolve"].path_param_keys == ("alias_token",)
  assert bindings_by_key["replay_link_alias_history"].route_path == "/replay-links/aliases/{alias_token}/history"
  assert bindings_by_key["replay_link_audit_list"].route_path == "/replay-links/audits"
  assert bindings_by_key["replay_link_audit_list"].header_keys == ("x_akra_replay_audit_admin_token",)
  assert bindings_by_key["replay_link_audit_list"].filter_param_specs[0].key == "alias_id"
  assert bindings_by_key["replay_link_audit_export"].route_path == "/replay-links/audits/export"
  assert bindings_by_key["replay_link_audit_export"].header_keys == ("x_akra_replay_audit_admin_token",)
  assert bindings_by_key["replay_link_audit_export"].filter_param_specs[-1].key == "format"
  assert bindings_by_key["replay_link_audit_export_job_create"].methods == ("POST",)
  assert bindings_by_key["replay_link_audit_export_job_create"].request_payload_kind == "replay_link_audit_export_job_create"
  assert bindings_by_key["replay_link_audit_export_job_list"].route_path == "/replay-links/audits/export-jobs"
  assert bindings_by_key["replay_link_audit_export_job_list"].filter_param_specs[1].key == "format"
  assert bindings_by_key["replay_link_audit_export_job_download"].path_param_keys == ("job_id",)
  assert bindings_by_key["replay_link_audit_export_job_history"].route_path == "/replay-links/audits/export-jobs/{job_id}/history"
  assert bindings_by_key["replay_link_audit_export_job_prune"].request_payload_kind == "replay_link_audit_export_job_prune"
  assert bindings_by_key["replay_link_audit_prune"].header_keys == ("x_akra_replay_audit_admin_token",)
  assert bindings_by_key["replay_link_audit_prune"].request_payload_kind == "replay_link_audit_prune"
  assert bindings_by_key["replay_link_alias_revoke"].request_payload_kind == "replay_link_alias_revoke"
  assert bindings_by_key["market_data_status"].route_path == "/market-data/status"
  assert bindings_by_key["market_data_status"].filter_param_specs[0].key == "timeframe"
  assert bindings_by_key["market_data_status"].filter_param_specs[0].constraints.min_length == 2
  assert bindings_by_key["market_data_status"].filter_param_specs[0].openapi.title == "Timeframe"
  assert bindings_by_key["market_data_status"].filter_param_specs[0].operators[0].key == "eq"
  assert bindings_by_key["market_data_lineage_history"].route_path == "/market-data/lineage-history"
  assert bindings_by_key["market_data_lineage_history"].filter_param_specs[0].key == "symbol"
  assert bindings_by_key["market_data_lineage_history"].filter_param_specs[3].key == "validation_claim"
  assert bindings_by_key["market_data_lineage_history"].sort_field_specs[0].key == "recorded_at"
  assert bindings_by_key["market_data_lineage_history"].sort_field_specs[-1].key == "lag_seconds"
  assert bindings_by_key["market_data_ingestion_job_history"].route_path == "/market-data/ingestion-jobs"
  assert bindings_by_key["market_data_ingestion_job_history"].filter_param_specs[2].key == "operation"
  assert bindings_by_key["market_data_ingestion_job_history"].filter_param_specs[-1].key == "last_error"
  assert bindings_by_key["market_data_ingestion_job_history"].sort_field_specs[0].key == "started_at"
  assert bindings_by_key["market_data_ingestion_job_history"].sort_field_specs[-1].key == "fetched_candle_count"
  assert bindings_by_key["market_data_lineage_evidence_retention_prune"].methods == ("POST",)
  assert bindings_by_key["market_data_lineage_evidence_retention_prune"].request_payload_kind == (
    "market_data_lineage_evidence_retention_prune"
  )
  assert bindings_by_key["market_data_lineage_drill_evidence_pack_export"].route_path == (
    "/market-data/lineage-evidence/drill-packs/export"
  )
  assert bindings_by_key["market_data_lineage_drill_evidence_pack_export"].methods == ("POST",)
  assert bindings_by_key["market_data_lineage_drill_evidence_pack_export"].request_payload_kind == (
    "market_data_lineage_drill_evidence_pack_export"
  )
  assert bindings_by_key["operator_visibility"].route_path == "/operator/visibility"
  assert bindings_by_key["operator_provider_provenance_export_job_create"].methods == ("POST",)
  assert (
    bindings_by_key["operator_provider_provenance_export_job_create"].request_payload_kind
    == "operator_provider_provenance_export_job_create"
  )
  assert bindings_by_key["operator_provider_provenance_export_job_list"].route_path == (
    "/operator/provider-provenance-exports"
  )
  assert bindings_by_key["operator_provider_provenance_export_job_list"].filter_param_specs[0].key == "export_scope"
  assert bindings_by_key["operator_provider_provenance_export_job_list"].filter_param_specs[5].key == "vendor_field"
  assert bindings_by_key["operator_provider_provenance_export_analytics"].route_path == (
    "/operator/provider-provenance-exports/analytics"
  )
  assert bindings_by_key["operator_provider_provenance_export_analytics"].filter_param_specs[-2].key == "result_limit"
  assert bindings_by_key["operator_provider_provenance_export_analytics"].filter_param_specs[-1].key == "window_days"
  assert bindings_by_key["operator_provider_provenance_export_job_download"].path_param_keys == ("job_id",)
  assert bindings_by_key["operator_provider_provenance_export_job_download"].filter_param_specs[0].key == "source_tab_id"
  assert bindings_by_key["operator_provider_provenance_export_job_history"].route_path == (
    "/operator/provider-provenance-exports/{job_id}/history"
  )
  assert bindings_by_key["operator_provider_provenance_export_job_policy"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_export_job_policy"].request_payload_kind == (
    "operator_provider_provenance_export_job_policy"
  )
  assert bindings_by_key["operator_provider_provenance_export_job_approval"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_export_job_approval"].request_payload_kind == (
    "operator_provider_provenance_export_job_approval"
  )
  assert bindings_by_key["operator_provider_provenance_export_job_escalate"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_export_job_escalate"].request_payload_kind == (
    "operator_provider_provenance_export_job_escalate"
  )
  assert bindings_by_key["operator_provider_provenance_analytics_preset_create"].methods == ("POST",)
  assert (
    bindings_by_key["operator_provider_provenance_analytics_preset_create"].request_payload_kind
    == "operator_provider_provenance_analytics_preset_create"
  )
  assert bindings_by_key["operator_provider_provenance_analytics_preset_list"].filter_param_specs[1].key == (
    "focus_scope"
  )
  assert bindings_by_key["operator_provider_provenance_dashboard_view_create"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_dashboard_view_list"].filter_param_specs[3].key == (
    "highlight_panel"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_create"].methods == (
    "POST",
  )
  assert (
    bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_list"].filter_param_specs[2].key
    == "narrative_facet"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_update"].methods == (
    "PATCH",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_delete"].path_param_keys == (
    "view_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_bulk_governance"].methods == (
    "POST",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_revision_list"].route_path.endswith(
    "/scheduler-stitched-report-views/{view_id}/revisions"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_revision_restore"].path_param_keys == (
    "view_id",
    "revision_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_audit_list"].route_path.endswith(
    "/scheduler-stitched-report-views/audits"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_create"].methods == (
    "POST",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_list"].filter_param_specs[0].key == (
    "search"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_update"].methods == (
    "PATCH",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_delete"].path_param_keys == (
    "registry_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list"].route_path.endswith(
    "/scheduler-stitched-report-governance-registries/{registry_id}/revisions"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore"].path_param_keys == (
    "registry_id",
    "revision_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance"].methods == (
    "POST",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list"].route_path.endswith(
    "/scheduler-stitched-report-governance-registries/audits"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list"].filter_param_specs[0].key == (
    "action_scope"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list"].filter_param_specs[0].key == (
    "search"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_create"].methods == (
    "POST",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_list"].filter_param_specs[0].key == (
    "status"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_approve"].path_param_keys == (
    "plan_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_apply"].path_param_keys == (
    "plan_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback"].path_param_keys == (
    "plan_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_template_create"].methods == ("POST",)
  assert (
    bindings_by_key["operator_provider_provenance_scheduler_narrative_template_list"].filter_param_specs[3].key
    == "narrative_facet"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_template_update"].methods == ("PATCH",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_template_delete"].path_param_keys == (
    "template_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_template_bulk_governance"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_template_revision_list"].route_path.endswith(
    "/scheduler-narrative-templates/{template_id}/revisions"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_template_revision_restore"].path_param_keys == (
    "template_id",
    "revision_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_create"].methods == ("POST",)
  assert (
    bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_list"].filter_param_specs[0].key
    == "template_id"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_update"].methods == ("PATCH",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_delete"].path_param_keys == (
    "registry_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_bulk_governance"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_revision_list"].route_path.endswith(
    "/scheduler-narrative-registry/{registry_id}/revisions"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_revision_restore"].path_param_keys == (
    "registry_id",
    "revision_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_create"].methods == ("POST",)
  assert (
    bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_list"].filter_param_specs[0].key
    == "item_type_scope"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_update"].methods == ("PATCH",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_delete"].path_param_keys == (
    "policy_template_id",
  )
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list"
  ].route_path.endswith("/scheduler-narrative-governance/policy-templates/{policy_template_id}/revisions")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore"
  ].path_param_keys == ("policy_template_id", "revision_id")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list"
  ].filter_param_specs[0].key == "policy_template_id"
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list"].filter_param_specs[0].key == (
    "search"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update"].methods == ("PATCH",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete"].path_param_keys == (
    "catalog_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance"].methods == ("POST",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list"
  ].route_path.endswith("/scheduler-narrative-governance/policy-catalogs/{catalog_id}/revisions")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore"
  ].path_param_keys == ("catalog_id", "revision_id")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list"
  ].filter_param_specs[0].key == "catalog_id"
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture"
  ].path_param_keys == ("catalog_id",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update"
  ].path_param_keys == ("catalog_id", "step_id")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore"
  ].path_param_keys == ("catalog_id", "step_id", "revision_id")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance"
  ].methods == ("POST",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create"
  ].methods == ("POST",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list"
  ].filter_param_specs[0].key == "item_type"
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update"
  ].methods == ("PATCH",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete"
  ].path_param_keys == ("hierarchy_step_template_id",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance"
  ].methods == ("POST",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list"
  ].route_path.endswith("/scheduler-narrative-governance/hierarchy-step-templates/{hierarchy_step_template_id}/revisions")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore"
  ].path_param_keys == ("hierarchy_step_template_id", "revision_id")
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list"
  ].filter_param_specs[0].key == "hierarchy_step_template_id"
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply"
  ].path_param_keys == ("hierarchy_step_template_id",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage"
  ].path_param_keys == ("hierarchy_step_template_id",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage"
  ].methods == ("POST",)
  assert bindings_by_key[
    "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage"
  ].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_create"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_list"].filter_param_specs[0].key == (
    "item_type"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_list"].filter_param_specs[7].key == (
    "source_hierarchy_step_template_id"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_list"].filter_param_specs[9].key == (
    "sort"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_approve"].path_param_keys == (
    "plan_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_apply"].path_param_keys == (
    "plan_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_batch_action"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_rollback"].path_param_keys == (
    "plan_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduled_report_create"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduled_report_list"].filter_param_specs[1].key == (
    "cadence"
  )
  assert bindings_by_key["operator_provider_provenance_scheduled_report_run"].path_param_keys == (
    "report_id",
  )
  assert bindings_by_key["operator_provider_provenance_scheduled_report_run_due"].methods == ("POST",)
  assert bindings_by_key["operator_provider_provenance_scheduled_report_history"].route_path == (
    "/operator/provider-provenance-analytics/reports/{report_id}/history"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_health_history"].route_path == (
    "/operator/provider-provenance-analytics/scheduler-health"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_health_history"].filter_param_specs[-1].key == (
    "offset"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_alert_history"].route_path == (
    "/operator/provider-provenance-analytics/scheduler-alerts"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_alert_history"].filter_param_specs[0].key == (
    "category"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_alert_history"].filter_param_specs[2].key == (
    "narrative_facet"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_alert_history"].filter_param_specs[3].key == (
    "search"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_alert_history"].filter_param_specs[-1].key == (
    "offset"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_health_analytics"].route_path == (
    "/operator/provider-provenance-analytics/scheduler-health/analytics"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_health_analytics"].filter_param_specs[-1].key == (
    "drilldown_history_limit"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_health_export"].route_path == (
    "/operator/provider-provenance-analytics/scheduler-health/export"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_health_export"].filter_param_specs[-1].key == (
    "format"
  )
  assert bindings_by_key["operator_provider_provenance_scheduler_health_export"].filter_param_specs[-2].key == (
    "limit"
  )
  assert bindings_by_key["guarded_live_status"].route_path == "/guarded-live"
  assert bindings_by_key["strategy_catalog_discovery"].route_path == "/strategies"
  assert bindings_by_key["strategy_catalog_discovery"].filter_param_specs[0].key == "lane"
  assert bindings_by_key["strategy_catalog_discovery"].filter_param_specs[0].value_path == ("runtime",)
  assert bindings_by_key["strategy_catalog_discovery"].filter_param_specs[0].openapi.description == (
    "Filter strategies by runtime lane."
  )
  assert bindings_by_key["strategy_catalog_discovery"].filter_param_specs[-1].key == "registered_at"
  assert bindings_by_key["strategy_catalog_discovery"].filter_param_specs[-1].value_path == (
    "lifecycle",
    "registered_at",
  )
  assert bindings_by_key["strategy_catalog_discovery"].sort_field_specs[0].key == "strategy_id"
  assert bindings_by_key["strategy_catalog_discovery"].sort_field_specs[-1].key == "lifecycle.registered_at"
  assert bindings_by_key["preset_catalog_discovery"].route_path == "/presets"
  assert bindings_by_key["preset_catalog_discovery"].filter_param_specs[1].key == "timeframe"
  assert bindings_by_key["preset_catalog_discovery"].filter_param_specs[-1].key == "updated_at"
  assert bindings_by_key["preset_catalog_discovery"].sort_field_specs[-1].key == "timestamps.created_at"
  assert bindings_by_key["preset_catalog_create"].methods == ("POST",)
  assert bindings_by_key["preset_catalog_item_get"].path_param_keys == ("preset_id",)
  assert bindings_by_key["preset_catalog_item_update"].methods == ("PATCH",)
  assert bindings_by_key["preset_catalog_revision_restore"].path_param_keys == ("preset_id", "revision_id")
  assert bindings_by_key["strategy_catalog_register"].methods == ("POST",)
  assert bindings_by_key["run_list"].filter_keys[-1] == "tag"
  assert bindings_by_key["run_list"].filter_param_specs[-1].key == "tag"
  assert bindings_by_key["run_list"].filter_param_specs[0].openapi.title == "Run mode"
  assert bindings_by_key["run_list"].filter_param_specs[0].value_path == ("config", "mode", "value")
  assert any(spec.key == "started_at" for spec in bindings_by_key["run_list"].filter_param_specs)
  assert any(spec.key == "initial_cash" for spec in bindings_by_key["run_list"].filter_param_specs)
  run_total_return_spec = next(
    spec
    for spec in bindings_by_key["run_list"].filter_param_specs
    if spec.key == "total_return_pct"
  )
  assert run_total_return_spec.value_path == ("metrics", "total_return_pct")
  assert [operator.key for operator in run_total_return_spec.operators] == ["eq", "gt", "ge", "lt", "le"]
  run_trade_count_spec = next(
    spec
    for spec in bindings_by_key["run_list"].filter_param_specs
    if spec.key == "trade_count"
  )
  assert run_trade_count_spec.constraints.ge == 0
  run_order_status_spec = next(
    spec
    for spec in bindings_by_key["run_list"].filter_param_specs
    if spec.key == "order_status"
  )
  assert run_order_status_spec.value_path == ("status", "value")
  assert run_order_status_spec.query_exposed is False
  run_issue_text_spec = next(
    spec
    for spec in bindings_by_key["run_list"].filter_param_specs
    if spec.key == "issue_text"
  )
  assert run_issue_text_spec.value_root is True
  assert run_issue_text_spec.query_exposed is False
  assert bindings_by_key["run_list"].filter_param_specs[-1].operators[0].key == "contains_all"
  assert bindings_by_key["run_list"].collection_path_specs[0].path == ("orders",)
  assert bindings_by_key["run_list"].collection_path_specs[0].path_template == ("orders",)
  assert bindings_by_key["run_list"].collection_path_specs[0].filter_keys == ("order_status", "order_type")
  assert bindings_by_key["run_list"].collection_path_specs[1].path == (
    "provenance",
    "market_data_by_symbol",
    "issues",
  )
  assert bindings_by_key["run_list"].collection_path_specs[1].path_template == (
    "provenance",
    "market_data_by_symbol",
    "{symbol_key}",
    "issues",
  )
  assert bindings_by_key["run_list"].collection_path_specs[1].item_kind == "issue_text"
  assert bindings_by_key["run_list"].collection_path_specs[1].parameters[0].key == "symbol_key"
  assert bindings_by_key["run_list"].collection_path_specs[1].parameters[0].kind == "dynamic_map_key"
  assert bindings_by_key["run_list"].collection_path_specs[1].parameters[0].domain_key == "market_data_symbol_key"
  assert bindings_by_key["run_list"].collection_path_specs[1].parameters[0].domain_source == (
    "run.provenance.market_data_by_symbol"
  )
  assert bindings_by_key["run_list"].collection_path_specs[1].parameters[0].enum_source_kind == (
    "dynamic_map_keys"
  )
  assert bindings_by_key["run_list"].collection_path_specs[1].parameters[0].enum_source_path == (
    "provenance",
    "market_data_by_symbol",
  )
  assert bindings_by_key["run_list"].sort_field_specs[0].default_direction == "desc"
  assert bindings_by_key["run_list"].sort_field_specs[-1].key == "metrics.trade_count"
  nested_run_metric_sort = next(
    field
    for field in bindings_by_key["run_list"].sort_field_specs
    if field.key == "metrics.total_return_pct"
  )
  assert nested_run_metric_sort.value_path == ("metrics", "total_return_pct")
  assert bindings_by_key["run_compare"].filter_keys == ("run_id", "intent", "narrative_score")
  assert bindings_by_key["run_compare"].filter_param_specs[0].key == "run_id"
  assert bindings_by_key["run_compare"].filter_param_specs[1].constraints.min_length == 1
  compare_score_spec = next(
    spec
    for spec in bindings_by_key["run_compare"].filter_param_specs
    if spec.key == "narrative_score"
  )
  assert compare_score_spec.value_path == ("insight_score",)
  assert [operator.key for operator in compare_score_spec.operators] == ["eq", "gt", "ge", "lt", "le"]
  assert bindings_by_key["run_compare"].sort_field_specs[1].key == "narrative_score"
  assert bindings_by_key["run_compare"].sort_field_specs[-1].key == "narratives.insight_score"
  assert bindings_by_key["run_backtest_launch"].methods == ("POST",)
  assert bindings_by_key["run_backtest_item_get"].route_path == "/runs/backtests/{run_id}"
  assert bindings_by_key["run_rerun_backtest"].path_param_keys == ("rerun_boundary_id",)
  assert bindings_by_key["run_live_launch"].request_payload_kind == "live_launch"
  assert bindings_by_key["operator_incident_external_sync"].header_keys == ("x_akra_incident_sync_token",)
  assert bindings_by_key["guarded_live_incident_acknowledge"].path_param_keys == ("event_id",)
  assert bindings_by_key["run_stop_sandbox"].methods == ("POST",)
  assert bindings_by_key["run_live_order_cancel"].path_param_keys == ("order_id",)
  assert bindings_by_key["run_subresource:orders"].scope == "run"
  assert bindings_by_key["run_subresource:orders"].route_path == "/runs/{run_id}/orders"

  launched_backtest_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["run_backtest_launch"],
    app=app,
    request_payload={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 12_000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
    },
  )
  fetched_backtest_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["run_backtest_item_get"],
    app=app,
    run_id=launched_backtest_payload["config"]["run_id"],
  )
  run_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["run_list"],
    app=app,
    filters={"mode": "backtest", "strategy_id": "ma_cross_v1", "tag": []},
  )
  compare_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["run_compare"],
    app=app,
    filters={
      "run_id": [run.config.run_id, launched_backtest_payload["config"]["run_id"]],
      "intent": "strategy_tuning",
    },
  )
  rerun_backtest_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["run_rerun_backtest"],
    app=app,
    path_params={"rerun_boundary_id": launched_backtest_payload["provenance"]["rerun_boundary_id"]},
  )
  created_preset_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["preset_catalog_create"],
    app=app,
    request_payload={
      "name": "Swing 1h",
      "preset_id": "swing_1h",
      "description": "runtime-created preset",
      "strategy_id": "ma_cross_v1",
      "timeframe": "1h",
      "tags": ["swing"],
      "parameters": {"short_window": 8, "long_window": 21},
      "benchmark_family": "trend",
    },
  )
  fetched_preset_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["preset_catalog_item_get"],
    app=app,
    path_params={"preset_id": "swing_1h"},
  )
  updated_preset_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["preset_catalog_item_update"],
    app=app,
    path_params={"preset_id": "swing_1h"},
    request_payload={
      "description": "updated bundle",
      "parameters": {"short_window": 9, "long_window": 34},
      "actor": "operator",
      "reason": "refresh_bundle",
    },
  )
  lifecycle_preset_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["preset_catalog_lifecycle_apply"],
    app=app,
    path_params={"preset_id": "swing_1h"},
    request_payload={
      "action": "promote",
      "actor": "operator",
      "reason": "ready_for_review",
    },
  )
  preset_revisions_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["preset_catalog_revision_list"],
    app=app,
    path_params={"preset_id": "swing_1h"},
  )
  restored_preset_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["preset_catalog_revision_restore"],
    app=app,
    path_params={"preset_id": "swing_1h", "revision_id": "swing_1h:r0001"},
    request_payload={
      "actor": "operator",
      "reason": "revert_bundle",
    },
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
  stopped_sandbox_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["run_stop_sandbox"],
    app=app,
    run_id=sandbox_run.config.run_id,
  )
  health_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["health_status"],
    app=app,
  )
  capabilities_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["run_surface_capabilities"],
    app=app,
  )
  market_data_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["market_data_status"],
    app=app,
    filters={"timeframe": "5m"},
  )
  lineage_history_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["market_data_lineage_history"],
    app=app,
    filters={"timeframe": "5m"},
  )
  ingestion_job_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["market_data_ingestion_job_history"],
    app=app,
    filters={"timeframe": "5m"},
  )
  operator_visibility_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["operator_visibility"],
    app=app,
  )
  guarded_live_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["guarded_live_status"],
    app=app,
  )
  orders_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["run_subresource:orders"],
      app=app,
      run_id=run.config.run_id,
  )
  strategy_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["strategy_catalog_discovery"],
    app=app,
    filters={"lane": "native"},
  )
  preset_payload = serialize_standalone_surface_response(
    binding=bindings_by_key["preset_catalog_discovery"],
    app=app,
    filters={"strategy_id": "ma_cross_v1"},
  )
  kill_switch_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["guarded_live_kill_switch_engage"],
    app=app,
    request_payload={"actor": "operator", "reason": "manual_safety_drill"},
  )
  released_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["guarded_live_kill_switch_release"],
    app=app,
    request_payload={"actor": "operator", "reason": "drill_complete"},
  )

  assert launched_backtest_payload["config"]["strategy_id"] == "ma_cross_v1"
  assert fetched_backtest_payload["config"]["run_id"] == launched_backtest_payload["config"]["run_id"]
  assert len(run_list_payload) >= 2
  assert compare_payload["intent"] == "strategy_tuning"
  assert compare_payload["baseline_run_id"] == run.config.run_id
  assert rerun_backtest_payload["provenance"]["rerun_target_boundary_id"] == (
    launched_backtest_payload["provenance"]["rerun_boundary_id"]
  )
  assert created_preset_payload["preset_id"] == "swing_1h"
  assert fetched_preset_payload["preset_id"] == "swing_1h"
  assert updated_preset_payload["parameters"] == {"short_window": 9, "long_window": 34}
  assert lifecycle_preset_payload["lifecycle"]["stage"] == "benchmark_candidate"
  assert [item["revision_id"] for item in preset_revisions_payload[:2]] == ["swing_1h:r0002", "swing_1h:r0001"]
  assert restored_preset_payload["parameters"] == {"short_window": 8, "long_window": 21}
  assert stopped_sandbox_payload["status"] == "stopped"
  assert health_payload == {"status": "ok"}
  assert capabilities_payload["discovery"]["shared_contracts"]
  assert market_data_payload["provider"] == "seeded"
  assert market_data_payload["venue"] == "binance"
  assert market_data_payload["instruments"]
  assert lineage_history_payload
  assert all(item["dataset_boundary"]["validation_claim"] == "exact_dataset" for item in lineage_history_payload)
  assert {item["symbol"] for item in lineage_history_payload} >= {"BTC/USDT", "ETH/USDT", "SOL/USDT"}
  assert ingestion_job_payload == []
  assert operator_visibility_payload["generated_at"]
  assert "alerts" in operator_visibility_payload
  assert guarded_live_payload["generated_at"]
  assert "candidacy_status" in guarded_live_payload
  assert orders_payload["run_id"] == run.config.run_id
  assert "orders" in orders_payload
  assert strategy_payload
  assert all(item["runtime"] == "native" for item in strategy_payload)
  assert sorted(item["preset_id"] for item in preset_payload) == ["core_5m", "swing_1h"]
  assert kill_switch_payload["kill_switch"]["state"] == "engaged"
  assert released_payload["kill_switch"]["state"] == "released"
