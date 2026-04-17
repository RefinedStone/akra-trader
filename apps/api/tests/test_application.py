from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from akra_trader.adapters.binance import BinanceMarketDataAdapter
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.guarded_live import SqlAlchemyGuardedLiveStateRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.references import load_reference_catalog
from akra_trader.adapters.sqlalchemy import SqlAlchemyRunRepository
from akra_trader.adapters.venue_execution import SeededVenueExecutionAdapter
from akra_trader.application import TradingApplication
from akra_trader.domain.models import AssetType
from akra_trader.domain.models import BenchmarkArtifact
from akra_trader.domain.models import Candle
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import GuardedLiveBookTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveKlineChannelSnapshot
from akra_trader.domain.models import GuardedLiveOrderBookLevel
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import SyncFailure
from akra_trader.domain.models import WarmupSpec
from akra_trader.strategies.base import Strategy


class FakeExchange:
  def __init__(self, series: dict[tuple[str, str], list[list[float]]]) -> None:
    self._series = series

  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "5m",
    since: int | None = None,
    limit: int | None = None,
  ) -> list[list[float]]:
    values = list(self._series[(symbol, timeframe)])
    if since is not None:
      values = [row for row in values if row[0] >= since]
    if limit is not None:
      values = values[:limit]
    return values


def build_references():
  repo_root = Path(__file__).resolve().parents[3]
  return load_reference_catalog(repo_root / "reference" / "catalog.toml")


def build_runs_repository(tmp_path: Path) -> SqlAlchemyRunRepository:
  return SqlAlchemyRunRepository(f"sqlite:///{tmp_path / 'runs.sqlite3'}")


class MutableClock:
  def __init__(self, current: datetime) -> None:
    self.current = current

  def __call__(self) -> datetime:
    return self.current

  def advance(self, delta: timedelta) -> None:
    self.current += delta


class MutableSeededMarketDataAdapter(SeededMarketDataAdapter):
  def append_candle(self, *, symbol: str, candle: Candle) -> None:
    self._candles[symbol].append(candle)


class StatusOverrideSeededMarketDataAdapter(MutableSeededMarketDataAdapter):
  def __init__(self) -> None:
    super().__init__()
    self._status_by_timeframe: dict[str, MarketDataStatus] = {}
    self._remediation_status_by_key: dict[tuple[str, str], MarketDataStatus] = {}
    self.remediation_calls: list[tuple[str, str, str]] = []

  def set_status(self, *, timeframe: str, status: MarketDataStatus) -> None:
    self._status_by_timeframe[timeframe] = status

  def set_remediation_status(
    self,
    *,
    kind: str,
    timeframe: str,
    status: MarketDataStatus,
  ) -> None:
    self._remediation_status_by_key[(kind, timeframe)] = status

  def get_status(self, timeframe: str) -> MarketDataStatus:
    status = self._status_by_timeframe.get(timeframe)
    if status is not None:
      return status
    return super().get_status(timeframe)

  def remediate(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
  ) -> MarketDataRemediationResult:
    self.remediation_calls.append((kind, symbol, timeframe))
    current_time = datetime.now(UTC)
    remediated_status = self._remediation_status_by_key.get((kind, timeframe))
    if remediated_status is not None:
      self._status_by_timeframe[timeframe] = remediated_status
      return MarketDataRemediationResult(
        kind=kind,
        symbol=symbol,
        timeframe=timeframe,
        status="executed",
        started_at=current_time,
        finished_at=current_time,
        detail=f"{kind}:{symbol}:{timeframe}:status_repaired",
      )
    return super().remediate(kind=kind, symbol=symbol, timeframe=timeframe)


class StaticVenueStateAdapter:
  def __init__(self, snapshot: GuardedLiveVenueStateSnapshot) -> None:
    self._snapshot = snapshot

  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
    return self._snapshot


class FakeOperatorAlertDeliveryAdapter:
  def __init__(
    self,
    *,
    targets: tuple[str, ...] = ("operator_console",),
    failures_before_success: dict[str, int] | None = None,
    workflow_failures_before_success: dict[str, int] | None = None,
    supported_workflow_providers: tuple[str, ...] = ("pagerduty",),
    clock=None,
  ) -> None:
    self._targets = targets
    self._supported_workflow_providers = supported_workflow_providers
    self.delivered_incidents: list[OperatorIncidentEvent] = []
    self.delivery_attempts: list[tuple[str, str, int]] = []
    self.workflow_attempts: list[tuple[str, str, str, int]] = []
    self.workflow_payloads: list[tuple[str, str, str, dict[str, Any] | None]] = []
    self._failures_before_success = dict(failures_before_success or {})
    self._workflow_failures_before_success = dict(workflow_failures_before_success or {})
    self._attempts_by_target: dict[str, int] = {}
    self._workflow_attempts_by_key: dict[tuple[str, str], int] = {}
    self._clock = clock

  def list_targets(self) -> tuple[str, ...]:
    return self._targets

  def list_supported_workflow_providers(self) -> tuple[str, ...]:
    return self._supported_workflow_providers

  def deliver(
    self,
    *,
    incident: OperatorIncidentEvent,
    targets: tuple[str, ...] | None = None,
    attempt_number: int = 1,
    phase: str = "initial",
  ) -> tuple[OperatorIncidentDelivery, ...]:
    self.delivered_incidents.append(incident)
    resolved_targets = targets or self._targets
    records: list[OperatorIncidentDelivery] = []
    for target in resolved_targets:
      self.delivery_attempts.append((incident.event_id, target, attempt_number))
      delivered_attempts = self._attempts_by_target.get(target, 0) + 1
      self._attempts_by_target[target] = delivered_attempts
      should_fail = delivered_attempts <= self._failures_before_success.get(target, 0)
      external_provider = None
      if target == "pagerduty_events":
        external_provider = "pagerduty"
      elif target == "opsgenie_alerts":
        external_provider = "opsgenie"
      records.append(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="failed" if should_fail else "delivered",
          attempted_at=self._clock() if callable(self._clock) else incident.timestamp,
          detail=(
            f"fake_failure:{target}:attempt-{attempt_number}"
            if should_fail
            else f"fake_delivery:{target}:attempt-{attempt_number}"
          ),
          attempt_number=attempt_number,
          phase=phase,
          external_provider=external_provider,
          external_reference=incident.external_reference or incident.alert_id if external_provider else None,
          source=incident.source,
        )
      )
    return tuple(records)

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
    self.workflow_attempts.append((incident.event_id, provider, action, attempt_number))
    self.workflow_payloads.append((incident.event_id, provider, action, payload))
    target = f"{provider}_workflow"
    key = (provider, action)
    delivered_attempts = self._workflow_attempts_by_key.get(key, 0) + 1
    self._workflow_attempts_by_key[key] = delivered_attempts
    should_fail = delivered_attempts <= self._workflow_failures_before_success.get(action, 0)
    workflow_reference = incident.provider_workflow_reference
    if workflow_reference is None and provider != "pagerduty":
      workflow_reference = incident.external_reference
    if workflow_reference is None and action == "remediate":
      workflow_reference = incident.external_reference or incident.alert_id
    if workflow_reference is None:
      should_fail = True
    return (
      OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed" if should_fail else "delivered",
        attempted_at=self._clock() if callable(self._clock) else incident.timestamp,
        detail=(
          f"fake_provider_workflow_reference_unavailable:{action}"
          if workflow_reference is None
          else (
            f"fake_provider_workflow_failed:{action}:attempt-{attempt_number}"
            if should_fail
            else f"fake_provider_workflow_delivered:{action}:attempt-{attempt_number}"
          )
        ),
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider=provider,
        external_reference=workflow_reference,
        source=incident.source,
      ),
    )


def build_guarded_live_repository(tmp_path: Path):
  return SqlAlchemyGuardedLiveStateRepository(f"sqlite:///{tmp_path / 'guarded-live.sqlite3'}")


class AlwaysBuyStrategy(Strategy):
  def describe(self) -> StrategyMetadata:
    return StrategyMetadata(
      strategy_id="always_buy_v1",
      name="Always Buy",
      version="1.0.0",
      runtime="native",
      asset_types=(AssetType.CRYPTO,),
      supported_timeframes=("5m",),
      parameter_schema={},
      description="Test helper strategy that always emits a buy signal.",
    )

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(required_bars=2)

  def decide(self, context) -> StrategyDecisionEnvelope:
    return StrategyDecisionEnvelope(
      signal=SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.BUY,
        size_fraction=0.25,
        reason="always_buy",
      ),
      rationale="always_buy",
      context=context,
    )


def test_backtest_creates_completed_run_with_metrics(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
  assert len(visibility.audit_events) >= 2
  assert visibility.audit_events[0].kind == "sandbox_worker_stale"
  assert visibility.audit_events[0].run_id == run.config.run_id


def test_operator_visibility_surfaces_worker_failure_and_operator_stop_audit(
  monkeypatch,
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 12, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
  assert any(event.kind == "sandbox_worker_failed" for event in failed_visibility.audit_events)

  stopped = app.stop_sandbox_run(run.config.run_id)
  stopped_visibility = app.get_operator_visibility()

  assert stopped is not None
  assert any(event.kind == "sandbox_worker_stopped" for event in stopped_visibility.audit_events)


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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
  }
  assert updated_incident.remediation.provider_recovery.lifecycle_state == "verified"
  assert updated_incident.remediation.provider_recovery.provider == "pagerduty"
  assert updated_incident.remediation.provider_recovery.job_id == "recovery-job-1"
  assert updated_incident.remediation.provider_recovery.channels == ("kline", "depth")
  assert updated_incident.remediation.provider_recovery.symbols == ("ETH/USDT",)
  assert updated_incident.remediation.provider_recovery.timeframe == "5m"
  assert updated_incident.remediation.provider_recovery.verification.state == "passed"
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


def test_guarded_live_channel_restore_incidents_auto_run_local_session_remediation(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 0, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    supported_workflow_providers=("pagerduty",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=StatusOverrideSeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    operator_reason="channel_restore_local_remediation",
  )

  state = guarded_live_state.load_state()
  guarded_live_state.save_state(
    replace(
      state,
      session_handoff=replace(
        state.session_handoff,
        coverage=("trade_ticks", "depth_updates", "kline_candles"),
        handed_off_at=clock.current - timedelta(minutes=2),
        last_sync_at=clock.current - timedelta(minutes=2),
        last_trade_event_at=clock.current - timedelta(minutes=2),
        last_depth_event_at=clock.current - timedelta(minutes=2),
        last_kline_event_at=None,
        channel_restore_state="unavailable",
        channel_restore_count=2,
        channel_last_restored_at=clock.current - timedelta(minutes=1),
        channel_continuation_state="unavailable",
        channel_continuation_count=2,
        channel_last_continued_at=clock.current - timedelta(minutes=1),
        issues=("binance_market_channel_restore_failed:ticker:timeout:exchange timeout",),
      ),
    )
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-channel-restore:{run.config.run_id}"
  )
  assert incident.remediation.kind == "channel_restore"
  assert incident.remediation.state == "executed"
  assert incident.remediation.requested_by == "system"
  assert "channel_restore:ETH/USDT:5m:channel_restore=synthetic" in incident.remediation.detail
  assert opened.session_handoff.channel_restore_state == "synthetic"
  assert opened.session_handoff.channel_continuation_state == "synthetic"
  assert opened.session_handoff.state == "active"
  assert any(
    event.kind == "incident_resolved"
    and event.alert_id == f"guarded-live:market-data-channel-restore:{run.config.run_id}"
    for event in opened.incident_events
  )
  assert all(
    alert.alert_id != f"guarded-live:market-data-channel-restore:{run.config.run_id}"
    for alert in opened.active_alerts
  )


def test_guarded_live_ladder_incidents_auto_run_local_order_book_rebuild(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 30, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    supported_workflow_providers=("pagerduty",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=StatusOverrideSeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    operator_reason="order_book_rebuild_auto_remediation",
  )

  state = guarded_live_state.load_state()
  guarded_live_state.save_state(
    replace(
      state,
      session_handoff=replace(
        state.session_handoff,
        last_sync_at=clock.current - timedelta(minutes=1),
        last_depth_event_at=clock.current - timedelta(minutes=1),
        order_book_state="resync_required",
        order_book_gap_count=2,
        order_book_rebuild_count=1,
        order_book_last_update_id=34,
        order_book_last_rebuilt_at=clock.current - timedelta(minutes=1),
        issues=("binance_order_book_gap_detected:25:29",),
      ),
    )
  )

  guarded_live_status = app.get_guarded_live_status()

  incident = next(
    event
    for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
  )
  assert incident.remediation.kind == "order_book_rebuild"
  assert incident.remediation.state == "executed"
  assert incident.remediation.requested_by == "system"
  assert "order_book_rebuild:ETH/USDT:5m:order_book=synthetic" in incident.remediation.detail
  assert guarded_live_status.session_handoff.order_book_state == "synthetic"
  assert guarded_live_status.session_handoff.order_book_gap_count == 0
  assert any(
    event.kind == "incident_resolved"
    and event.alert_id == f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert all(
    alert.alert_id != f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
    for alert in guarded_live_status.active_alerts
  )


def test_operator_visibility_promotes_channel_level_market_data_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 0, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    operator_reason="channel_level_incident_visibility",
  )

  state = guarded_live_state.load_state()
  degraded_handoff = replace(
    state.session_handoff,
    coverage=("trade_ticks", "depth_updates", "kline_candles"),
    handed_off_at=clock.current - timedelta(minutes=2),
    last_sync_at=clock.current - timedelta(minutes=2),
    last_trade_event_at=clock.current - timedelta(minutes=2),
    last_depth_event_at=clock.current - timedelta(minutes=2),
    last_kline_event_at=None,
    order_book_state="snapshot_rebuilt",
    order_book_gap_count=1,
    order_book_rebuild_count=2,
    order_book_last_update_id=34,
    order_book_last_rebuilt_at=clock.current - timedelta(minutes=1),
    channel_restore_state="unavailable",
    channel_restore_count=2,
    channel_last_restored_at=clock.current - timedelta(minutes=1),
    channel_continuation_state="unavailable",
    channel_continuation_count=2,
    channel_last_continued_at=clock.current - timedelta(minutes=1),
    issues=(
      "binance_order_book_gap_detected:25:29",
      "binance_market_channel_restore_failed:ticker:timeout:exchange timeout",
    ),
  )
  guarded_live_state.save_state(replace(state, session_handoff=degraded_handoff))

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  categories = {
    alert.category
    for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.source == "guarded_live"
  }
  assert not categories

  consistency_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-channel-consistency:{run.config.run_id}"
  )
  assert "trade ticks is stale" in consistency_incident.detail
  assert "depth/order-book updates is stale" in consistency_incident.detail
  assert "kline candles has not produced any events within 45s" in consistency_incident.detail

  ladder_integrity_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
  )
  assert "binance ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident.detail
  assert "binance ladder integrity required 2 snapshot rebuild(s)." in ladder_integrity_incident.detail
  assert "binance depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident.detail

  restore_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-channel-restore:{run.config.run_id}"
  )
  assert "market-channel restore is unavailable." in restore_incident.detail
  assert "market-channel continuation is unavailable." in restore_incident.detail
  assert "binance ticker restore failed: timeout:exchange timeout." in restore_incident.detail

  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-channel-consistency:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-channel-restore:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-channel-consistency:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-channel-restore:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )


def test_operator_visibility_separates_venue_native_ladder_integrity_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 0, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="BTC/USD",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="venue_native_ladder_integrity_visibility",
  )

  state = guarded_live_state.load_state()
  owner_session_id = (
    state.ownership.owner_session_id
    or state.session_handoff.owner_session_id
    or "worker-live-coinbase-market"
  )
  degraded_handoff = replace(
    state.session_handoff,
    state="active",
    venue="coinbase",
    owner_run_id=run.config.run_id,
    owner_session_id=owner_session_id,
    coverage=("depth_updates",),
    handed_off_at=clock.current - timedelta(minutes=1),
    last_sync_at=clock.current - timedelta(seconds=20),
    last_depth_event_at=clock.current - timedelta(seconds=10),
    order_book_state="snapshot_rebuilt",
    order_book_gap_count=1,
    order_book_rebuild_count=1,
    order_book_last_update_id=34,
    order_book_last_rebuilt_at=clock.current - timedelta(seconds=15),
    issues=(
      "coinbase_order_book_gap_detected:25:29",
      "coinbase_order_book_snapshot_failed:session_missing:stream timeout",
      "coinbase_order_book_snapshot_crossed:2501.5:2501.2",
      "coinbase_order_book_snapshot_non_monotonic:bids:2:2501.3:2501.0",
    ),
  )
  guarded_live_state.save_state(
    replace(
      state,
      ownership=replace(
        state.ownership,
        state="owned",
        owner_run_id=run.config.run_id,
        owner_session_id=owner_session_id,
      ),
      session_handoff=degraded_handoff,
    )
  )

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  categories = {
    alert.category
    for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.source == "guarded_live"
  }
  assert not categories

  ladder_integrity_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
  )
  assert "coinbase ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident.detail
  assert "coinbase ladder integrity required 1 snapshot rebuild(s)." in ladder_integrity_incident.detail
  assert "coinbase depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident.detail
  assert "snapshot rebuild failed" not in ladder_integrity_incident.detail

  venue_ladder_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-venue-ladder-integrity:{run.config.run_id}"
  )
  assert "coinbase ladder snapshot rebuild failed during session missing: stream timeout." in venue_ladder_incident.detail
  assert "coinbase ladder snapshot is crossed: best bid 2501.50000000 is above best ask 2501.20000000." in venue_ladder_incident.detail
  assert "coinbase bid ladder snapshot is not strictly descending at level 2 (2501.30000000 after 2501.00000000)." in venue_ladder_incident.detail

  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-venue-ladder-integrity:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-venue-ladder-integrity:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )


def test_operator_visibility_separates_ladder_bridge_integrity_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 5, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    operator_reason="exchange_specific_ladder_integrity_visibility",
  )

  state = guarded_live_state.load_state()
  owner_session_id = (
    state.ownership.owner_session_id
    or state.session_handoff.owner_session_id
    or "worker-live-binance-market"
  )
  guarded_live_state.save_state(
    replace(
      state,
      ownership=replace(
        state.ownership,
        state="owned",
        owner_run_id=run.config.run_id,
        owner_session_id=owner_session_id,
      ),
      session_handoff=replace(
        state.session_handoff,
        state="active",
        venue="binance",
        owner_run_id=run.config.run_id,
        owner_session_id=owner_session_id,
        coverage=("depth_updates",),
        handed_off_at=clock.current - timedelta(minutes=1),
        last_sync_at=clock.current - timedelta(seconds=20),
        last_depth_event_at=clock.current - timedelta(seconds=10),
        order_book_state="snapshot_rebuilt",
        order_book_gap_count=1,
        order_book_rebuild_count=1,
        order_book_last_update_id=34,
        order_book_last_rebuilt_at=clock.current - timedelta(seconds=15),
        issues=(
          "binance_order_book_gap_detected:25:29",
          "binance_order_book_bridge_previous_mismatch:25:29",
          "binance_order_book_bridge_range_mismatch:26:31:34",
        ),
      ),
    )
  )

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  categories = {
    alert.category
    for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.source == "guarded_live"
  }
  assert not categories

  ladder_integrity_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-integrity:{run.config.run_id}"
  )
  assert "binance ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident.detail
  assert "binance ladder integrity required 1 snapshot rebuild(s)." in ladder_integrity_incident.detail
  assert "binance depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident.detail
  assert "bridge expected previous update id" not in ladder_integrity_incident.detail

  bridge_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-bridge:{run.config.run_id}"
  )
  assert "binance depth bridge expected previous update id 25 but received 29." in bridge_incident.detail
  assert "binance depth bridge range 31-34 does not cover expected next update id 26." in bridge_incident.detail

  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-bridge:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-ladder-bridge:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )


def test_operator_visibility_separates_ladder_sequence_and_snapshot_refresh_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 6, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="pre_live_check")
  app.recover_guarded_live_runtime_state(actor="operator", reason="pre_live_recovery")
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="BTC/USD",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    operator_reason="ladder_sequence_snapshot_refresh_visibility",
  )

  state = guarded_live_state.load_state()
  owner_session_id = (
    state.ownership.owner_session_id
    or state.session_handoff.owner_session_id
    or "worker-live-coinbase-sequence"
  )
  guarded_live_state.save_state(
    replace(
      state,
      ownership=replace(
        state.ownership,
        state="owned",
        owner_run_id=run.config.run_id,
        owner_session_id=owner_session_id,
      ),
      session_handoff=replace(
        state.session_handoff,
        state="active",
        venue="coinbase",
        owner_run_id=run.config.run_id,
        owner_session_id=owner_session_id,
        coverage=("depth_updates",),
        handed_off_at=clock.current - timedelta(minutes=1),
        last_sync_at=clock.current - timedelta(seconds=20),
        last_depth_event_at=clock.current - timedelta(seconds=10),
        order_book_state="snapshot_rebuilt",
        order_book_gap_count=0,
        order_book_rebuild_count=1,
        order_book_last_update_id=704,
        order_book_last_rebuilt_at=clock.current - timedelta(seconds=15),
        issues=(
          "coinbase_order_book_sequence_mismatch:701:703:704",
          "coinbase_order_book_snapshot_refresh:700:701",
        ),
      ),
    )
  )

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  categories = {
    alert.category
    for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.source == "guarded_live"
  }
  assert not categories

  sequence_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-sequence:{run.config.run_id}"
  )
  assert "coinbase ladder sequence expected previous update id 701 but received 703 before update 704." in sequence_incident.detail

  snapshot_refresh_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-snapshot-refresh:{run.config.run_id}"
  )
  assert "coinbase ladder snapshot refresh replaced update id 700 with 701." in snapshot_refresh_incident.detail

  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-sequence:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-ladder-snapshot-refresh:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )


def test_operator_visibility_promotes_book_and_kline_consistency_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 30, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    operator_reason="book_kline_consistency_visibility",
  )

  state = guarded_live_state.load_state()
  degraded_handoff = replace(
    state.session_handoff,
    coverage=("book_ticker", "depth_updates", "kline_candles"),
    last_sync_at=clock.current,
    last_depth_event_at=clock.current - timedelta(seconds=5),
    last_book_ticker_event_at=clock.current - timedelta(seconds=5),
    last_kline_event_at=clock.current - timedelta(seconds=5),
    order_book_state="streaming",
    order_book_best_bid_price=2501.2,
    order_book_best_ask_price=2500.8,
    order_book_bid_level_count=2,
    order_book_ask_level_count=2,
    book_ticker_snapshot=GuardedLiveBookTickerChannelSnapshot(
      bid_price=2501.1,
      bid_quantity=1.0,
      ask_price=2500.9,
      ask_quantity=0.9,
      event_at=clock.current - timedelta(seconds=5),
    ),
    kline_snapshot=GuardedLiveKlineChannelSnapshot(
      timeframe="1m",
      open_at=clock.current - timedelta(minutes=5),
      close_at=clock.current - timedelta(minutes=6),
      open_price=2499.5,
      high_price=2500.0,
      low_price=2499.0,
      close_price=2501.0,
      volume=4.2,
      closed=True,
      event_at=clock.current - timedelta(seconds=5),
    ),
  )
  guarded_live_state.save_state(replace(state, session_handoff=degraded_handoff))

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  categories = {
    alert.category
    for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.source == "guarded_live"
  }
  assert not categories

  book_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-book-consistency:{run.config.run_id}"
  )
  assert "binance local order book is crossed: best bid 2501.20000000 is above best ask 2500.80000000." in book_incident.detail
  assert "binance book-ticker quote is crossed: bid 2501.10000000 is above ask 2500.90000000." in book_incident.detail
  assert "binance local best bid 2501.20000000 is above book-ticker ask 2500.90000000." in book_incident.detail

  kline_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-kline-consistency:{run.config.run_id}"
  )
  assert "binance kline timeframe 1m does not match the guarded-live timeframe 5m." in kline_incident.detail
  assert "binance kline closes at" in kline_incident.detail
  assert "binance kline close 2501.00000000 falls outside the high/low range 2499.00000000-2500.00000000." in kline_incident.detail

  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-book-consistency:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-kline-consistency:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-book-consistency:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-kline-consistency:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )


def test_operator_visibility_splits_depth_ladder_and_candle_sequence_incidents(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 20, 0, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    operator_reason="depth_ladder_candle_sequence_visibility",
  )

  state = guarded_live_state.load_state()
  degraded_handoff = replace(
    state.session_handoff,
    coverage=("depth_updates", "kline_candles"),
    last_sync_at=clock.current,
    last_depth_event_at=clock.current - timedelta(seconds=5),
    last_kline_event_at=clock.current - timedelta(seconds=5),
    order_book_state="streaming",
    order_book_bid_level_count=3,
    order_book_ask_level_count=2,
    order_book_best_bid_price=2501.2,
    order_book_best_bid_quantity=1.0,
    order_book_best_ask_price=2501.5,
    order_book_best_ask_quantity=0.6,
    order_book_bids=(
      GuardedLiveOrderBookLevel(price=2501.0, quantity=0.5),
      GuardedLiveOrderBookLevel(price=2501.3, quantity=0.4),
    ),
    order_book_asks=(
      GuardedLiveOrderBookLevel(price=2501.5, quantity=0.6),
      GuardedLiveOrderBookLevel(price=2501.7, quantity=0.8),
    ),
    kline_snapshot=GuardedLiveKlineChannelSnapshot(
      timeframe="5m",
      open_at=datetime(2025, 1, 3, 19, 26, tzinfo=UTC),
      close_at=datetime(2025, 1, 3, 19, 29, tzinfo=UTC),
      open_price=2499.2,
      high_price=2500.0,
      low_price=2499.0,
      close_price=2499.6,
      volume=3.2,
      closed=True,
      event_at=datetime(2025, 1, 3, 19, 28, tzinfo=UTC),
    ),
  )
  guarded_live_state.save_state(replace(state, session_handoff=degraded_handoff))

  visibility = app.get_operator_visibility()
  guarded_live_status = app.get_guarded_live_status()

  categories = {
    alert.category
    for alert in visibility.alerts
    if alert.run_id == run.config.run_id and alert.source == "guarded_live"
  }
  assert not categories

  depth_ladder_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-depth-ladder:{run.config.run_id}"
  )
  assert "binance bid ladder count 2 does not match stored bid level count 3." in depth_ladder_incident.detail
  assert "binance best bid ladder head 2501.00000000/0.50000000 does not match stored best bid 2501.20000000/1.00000000." in depth_ladder_incident.detail
  assert "binance bid ladder is not strictly descending at level 2 (2501.30000000 after 2501.00000000)." in depth_ladder_incident.detail

  candle_sequence_incident = next(
    event for event in guarded_live_status.incident_events
    if event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-candle-sequence:{run.config.run_id}"
  )
  assert "binance kline open 2025-01-03T19:26:00+00:00 is not aligned to the 5m timeframe boundary." in candle_sequence_incident.detail
  assert "binance kline close 2025-01-03T19:29:00+00:00 does not match the expected 5m boundary close 2025-01-03T19:31:00+00:00." in candle_sequence_incident.detail
  assert "binance closed kline event arrived at 2025-01-03T19:28:00+00:00 before the candle close 2025-01-03T19:29:00+00:00." in candle_sequence_incident.detail

  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-depth-ladder:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    event.kind == "incident_opened"
    and event.alert_id == f"guarded-live:market-data-candle-sequence:{run.config.run_id}"
    for event in guarded_live_status.incident_events
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-depth-ladder:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )
  assert any(
    record.alert_id == f"guarded-live:market-data-candle-sequence:{run.config.run_id}"
    for record in guarded_live_status.delivery_history
  )


def test_guarded_live_delivery_retries_failed_outbound_target_with_backoff(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 13, 0, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("operator_webhook", "slack_webhook"),
    failures_before_success={"slack_webhook": 1},
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    operator_alert_delivery_initial_backoff_seconds=30,
    operator_alert_delivery_max_backoff_seconds=300,
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

  first_visibility = app.get_operator_visibility()
  assert not first_visibility.delivery_history

  app.run_guarded_live_reconciliation(
    actor="operator",
    reason="retryable_delivery_open",
  )
  visibility = app.get_operator_visibility()
  incident = next(
    event for event in visibility.incident_events
    if event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.delivery_state == "retrying"
  first_slack_attempt = next(
    record for record in visibility.delivery_history
    if record.target == "slack_webhook" and record.incident_event_id == incident.event_id
  )
  assert first_slack_attempt.status == "retry_scheduled"
  assert first_slack_attempt.attempt_number == 1
  assert first_slack_attempt.next_retry_at == clock.current + timedelta(seconds=30)

  clock.advance(timedelta(seconds=29))
  not_yet_retried = app.get_operator_visibility()
  slack_attempts = [
    record
    for record in not_yet_retried.delivery_history
    if record.target == "slack_webhook" and record.incident_event_id == incident.event_id
  ]
  assert len(slack_attempts) == 1

  clock.advance(timedelta(seconds=1))
  retried = app.get_operator_visibility()
  slack_attempts = [
    record
    for record in retried.delivery_history
    if record.target == "slack_webhook" and record.incident_event_id == incident.event_id
  ]
  assert len(slack_attempts) == 2
  assert slack_attempts[0].attempt_number == 2
  assert slack_attempts[0].status == "delivered"
  retried_incident = next(
    event for event in retried.incident_events
    if event.event_id == incident.event_id
  )
  assert retried_incident.delivery_state == "delivered"


def test_acknowledge_guarded_live_incident_suppresses_pending_retries(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 13, 15, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("slack_webhook",),
    failures_before_success={"slack_webhook": 4},
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    operator_alert_delivery_initial_backoff_seconds=30,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.3, free=0.3, used=0.0),),
      )
    ),
    guarded_live_execution_enabled=True,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="ack_flow")
  visibility = app.get_guarded_live_status()
  incident = next(
    event for event in visibility.incident_events
    if event.alert_id == "guarded-live:reconciliation" and event.kind == "incident_opened"
  )
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="on_call_ack",
  )
  updated = next(
    event for event in acknowledged.incident_events
    if event.event_id == incident.event_id
  )
  assert updated.acknowledgment_state == "acknowledged"
  assert updated.acknowledged_by == "operator"
  assert updated.acknowledgment_reason == "on_call_ack"
  assert updated.next_escalation_at is None
  suppressed = next(
    record for record in acknowledged.delivery_history
    if record.incident_event_id == incident.event_id and record.status == "retry_suppressed"
  )
  assert suppressed.target == "slack_webhook"
  assert any(event.kind == "guarded_live_incident_acknowledged" for event in acknowledged.audit_events)

  attempts_before = len(delivery.delivery_attempts)
  clock.advance(timedelta(minutes=10))
  after_wait = app.get_guarded_live_status()
  assert len(delivery.delivery_attempts) == attempts_before
  after_wait_incident = next(
    event for event in after_wait.incident_events
    if event.event_id == incident.event_id
  )
  assert after_wait_incident.acknowledgment_state == "acknowledged"


def test_guarded_live_incident_auto_escalates_after_retry_exhaustion(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 13, 30, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("operator_webhook",),
    failures_before_success={"operator_webhook": 3, "pagerduty_events": 0},
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    operator_alert_delivery_max_attempts=2,
    operator_alert_delivery_initial_backoff_seconds=15,
    operator_alert_escalation_targets=("pagerduty_events",),
    operator_alert_incident_ack_timeout_seconds=300,
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.3, free=0.3, used=0.0),),
      )
    ),
    guarded_live_execution_enabled=True,
  )

  app.run_guarded_live_reconciliation(actor="operator", reason="auto_escalation")
  first = app.get_guarded_live_status()
  incident = next(
    event for event in first.incident_events
    if event.alert_id == "guarded-live:reconciliation" and event.kind == "incident_opened"
  )
  assert incident.delivery_state == "retrying"

  clock.advance(timedelta(seconds=15))
  exhausted = app.get_guarded_live_status()
  exhausted_attempts = [
    record
    for record in exhausted.delivery_history
    if record.incident_event_id == incident.event_id and record.phase == "initial"
  ]
  assert exhausted_attempts[0].attempt_number == 2
  assert exhausted_attempts[0].status == "failed"

  escalated = app.get_guarded_live_status()
  updated = next(
    event for event in escalated.incident_events
    if event.event_id == incident.event_id
  )
  assert updated.escalation_level == 1
  assert updated.escalation_state == "escalated"
  assert updated.last_escalated_by == "system"
  assert updated.escalation_reason == "retry_budget_exhausted"
  escalation_delivery = next(
    record
    for record in escalated.delivery_history
    if record.incident_event_id == incident.event_id and record.phase == "escalation"
  )
  assert escalation_delivery.target == "pagerduty_events"
  assert escalation_delivery.status == "delivered"
  assert any(event.kind == "guarded_live_incident_escalated" for event in escalated.audit_events)


def test_external_incident_sync_acknowledges_and_preserves_local_alert_truth(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 13, 45, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    failures_before_success={"pagerduty_events": 3},
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    operator_alert_delivery_initial_backoff_seconds=30,
    operator_alert_external_sync_token="shared-token",
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.3, free=0.3, used=0.0),),
      )
    ),
    guarded_live_execution_enabled=True,
  )

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="external_pd_sync")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.delivery_state == "retrying"

  acked = app.sync_guarded_live_incident_from_external(
    provider="pagerduty",
    event_kind="acknowledged",
    actor="responder-1",
    detail="acknowledged_in_pagerduty",
    alert_id="guarded-live:reconciliation",
    external_reference=incident.alert_id,
    occurred_at=clock.current + timedelta(minutes=1),
  )
  synced = next(event for event in acked.incident_events if event.event_id == incident.event_id)
  assert synced.acknowledgment_state == "acknowledged"
  assert synced.acknowledged_by == "pagerduty:responder-1"
  assert synced.external_provider == "pagerduty"
  assert synced.external_reference == "guarded-live:reconciliation"
  assert synced.external_status == "acknowledged"
  assert synced.paging_status == "acknowledged"
  suppressed = next(
    record
    for record in acked.delivery_history
    if record.incident_event_id == incident.event_id and record.status == "retry_suppressed"
  )
  assert suppressed.target == "pagerduty_events"
  assert any(event.kind == "guarded_live_incident_external_synced" for event in acked.audit_events)
  assert any(alert.alert_id == "guarded-live:reconciliation" for alert in acked.active_alerts)

  resolved = app.sync_guarded_live_incident_from_external(
    provider="pagerduty",
    event_kind="resolved",
    actor="responder-1",
    detail="resolved_in_pagerduty",
    alert_id="guarded-live:reconciliation",
    external_reference=incident.alert_id,
    occurred_at=clock.current + timedelta(minutes=2),
  )
  resolved_incident = next(event for event in resolved.incident_events if event.event_id == incident.event_id)
  assert resolved_incident.external_status == "resolved"
  assert resolved_incident.paging_status == "resolved"
  assert any(alert.alert_id == "guarded-live:reconciliation" for alert in resolved.active_alerts)


def test_guarded_live_incident_uses_paging_policy_and_syncs_provider_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 0, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("operator_console",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    operator_alert_paging_policy_default_provider="pagerduty",
    operator_alert_paging_policy_warning_targets=("slack_webhook", "pagerduty_events"),
    operator_alert_paging_policy_critical_targets=("slack_webhook", "pagerduty_events"),
    operator_alert_paging_policy_warning_escalation_targets=("pagerduty_events",),
    operator_alert_paging_policy_critical_escalation_targets=("pagerduty_events",),
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.3, free=0.3, used=0.0),),
      )
    ),
    guarded_live_execution_enabled=True,
  )

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="policy_sync")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_policy_id in {"severity:warning", "severity:critical"}
  assert incident.paging_provider == "pagerduty"
  assert incident.delivery_targets == ("slack_webhook", "pagerduty_events")
  assert incident.escalation_targets == ("pagerduty_events",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="pagerduty",
    event_kind="triggered",
    actor="pagerduty",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="PDINC-123",
    occurred_at=clock.current + timedelta(seconds=30),
  )
  triggered_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered_incident.provider_workflow_reference == "PDINC-123"
  assert triggered_incident.external_status == "triggered"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="provider_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert updated.provider_workflow_reference == "PDINC-123"
  assert any(
    attempt[1:] == ("pagerduty", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_provider_workflow_retry_recovers_after_external_reference_sync(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 30, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagerduty_events",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    operator_alert_delivery_initial_backoff_seconds=30,
    operator_alert_paging_policy_default_provider="pagerduty",
    operator_alert_paging_policy_warning_targets=("pagerduty_events",),
    operator_alert_paging_policy_critical_targets=("pagerduty_events",),
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.3, free=0.3, used=0.0),),
      )
    ),
    guarded_live_execution_enabled=True,
  )

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="workflow_retry")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )

  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="missing_reference",
  )
  first_pass = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert first_pass.provider_workflow_state == "retrying"
  failed_record = next(
    record
    for record in acknowledged.delivery_history
    if record.incident_event_id == incident.event_id and record.phase == "provider_acknowledge"
  )
  assert failed_record.status == "retry_scheduled"

  synced = app.sync_guarded_live_incident_from_external(
    provider="pagerduty",
    event_kind="triggered",
    actor="pagerduty",
    detail="provider_incident_reference",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="PDINC-456",
    occurred_at=clock.current + timedelta(seconds=5),
  )
  synced_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert synced_incident.provider_workflow_reference == "PDINC-456"

  clock.advance(timedelta(seconds=30))
  retried = app.get_guarded_live_status()
  retried_incident = next(event for event in retried.incident_events if event.event_id == incident.event_id)
  assert retried_incident.provider_workflow_state == "delivered"
  assert any(
    attempt[1:] == ("pagerduty", "acknowledge", 2)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_opsgenie_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 45, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("opsgenie_alerts",),
    supported_workflow_providers=("opsgenie",),
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
    clock=clock,
    guarded_live_state=guarded_live_state,
    operator_alert_delivery=delivery,
    operator_alert_paging_policy_warning_targets=("opsgenie_alerts",),
    operator_alert_paging_policy_critical_targets=("opsgenie_alerts",),
    operator_alert_paging_policy_warning_escalation_targets=("opsgenie_alerts",),
    operator_alert_paging_policy_critical_escalation_targets=("opsgenie_alerts",),
    venue_state=StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=clock(),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.3, free=0.3, used=0.0),),
      )
    ),
    guarded_live_execution_enabled=True,
  )

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="opsgenie_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "opsgenie"
  assert incident.delivery_targets == ("opsgenie_alerts",)
  assert incident.escalation_targets == ("opsgenie_alerts",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="opsgenie",
    event_kind="triggered",
    actor="opsgenie",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OG-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "OG-123"
  assert triggered.external_provider == "opsgenie"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="opsgenie_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("opsgenie", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_guarded_live_kill_switch_stops_operator_control_sessions_and_blocks_restarts(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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


def test_reference_backtest_records_external_provenance(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )

  run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  assert run.provenance.strategy is not None
  assert run.provenance.strategy.runtime == "freqtrade_reference"
  assert run.provenance.strategy.entrypoint == "NostalgiaForInfinityX7"
  assert run.provenance.strategy.parameter_snapshot.requested == {}
  assert run.provenance.strategy.parameter_snapshot.resolved == {}
  assert run.provenance.reference_id == "nostalgia-for-infinity"
  assert run.provenance.reference is not None
  assert run.provenance.reference.title == "NostalgiaForInfinity"
  assert run.provenance.reference.integration_mode == "external_runtime"
  assert run.provenance.integration_mode == "external_runtime"
  assert run.provenance.working_directory.endswith("reference/NostalgiaForInfinity")
  assert run.provenance.external_command
  assert any(path.endswith("user_data/backtest_results") for path in run.provenance.artifact_paths)
  artifact_kinds = {artifact.kind for artifact in run.provenance.benchmark_artifacts}
  assert "result_snapshot_root" in artifact_kinds
  assert "runtime_log_root" in artifact_kinds
  assert all(isinstance(artifact.summary, dict) for artifact in run.provenance.benchmark_artifacts)
  assert all(isinstance(artifact.sections, dict) for artifact in run.provenance.benchmark_artifacts)
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.provider == "freqtrade_reference"
  assert run.provenance.market_data.dataset_identity is None
  assert run.provenance.market_data.reproducibility_state == "delegated"
  assert run.provenance.market_data.sync_status == "delegated"
  assert run.provenance.market_data_by_symbol["BTC/USDT"].dataset_identity is None
  assert run.provenance.market_data_by_symbol["BTC/USDT"].reproducibility_state == "delegated"
  assert run.provenance.market_data_by_symbol["BTC/USDT"].sync_status == "delegated"


def test_registered_strategy_run_records_lifecycle_timestamp(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  strategies = LocalStrategyCatalog()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=strategies,
    references=build_references(),
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
    references=build_references(),
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
  app.run_backtest(
    strategy_id="nfi_x7_reference",
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


def test_list_runs_can_filter_paper_history_separately_from_sandbox(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    references=build_references(),
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
    references=build_references(),
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
  assert rerun.provenance.rerun_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.market_data is not None
  assert rerun.provenance.market_data.effective_start_at == source.provenance.market_data.effective_start_at
  assert rerun.provenance.market_data.effective_end_at == source.provenance.market_data.effective_end_at
  assert rerun.notes[0].startswith("Explicit backtest rerun from boundary ")
  assert rerun.notes[-1] == "Explicit rerun matched the stored rerun boundary."


def test_rerun_backtest_from_boundary_uses_resolved_strategy_parameters(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
    references=build_references(),
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
  assert rerun.provenance.rerun_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.provenance.market_data is not None
  assert rerun.provenance.market_data.effective_start_at == source.provenance.market_data.effective_start_at
  assert rerun.provenance.market_data.effective_end_at == source.provenance.market_data.effective_end_at
  assert rerun.provenance.runtime_session is not None
  assert rerun.notes[0].startswith("Explicit sandbox rerun from boundary ")
  assert rerun.notes[1] == "Sandbox rerun restored the stored worker-session priming window."
  assert rerun.notes[-1] == "Explicit rerun matched the stored rerun boundary."


def test_rerun_paper_from_boundary_uses_stored_effective_window_and_replays_same_mode_boundary(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
  assert rerun.provenance.rerun_boundary_id == source.provenance.rerun_boundary_id
  assert rerun.notes[0].startswith("Explicit paper rerun from boundary ")
  assert rerun.notes[1] == "Paper rerun seeded the current paper session from the stored priming window."
  assert rerun.notes[-1] == "Explicit rerun matched the stored rerun boundary."


def test_rerun_paper_from_backtest_boundary_records_expected_mode_drift(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
  assert rerun.provenance.market_data is not None
  assert rerun.provenance.market_data.effective_start_at == source.provenance.market_data.effective_start_at
  assert rerun.provenance.market_data.effective_end_at == source.provenance.market_data.effective_end_at
  assert rerun.provenance.strategy is not None
  assert rerun.provenance.strategy.parameter_snapshot.resolved == {"short_window": 13, "long_window": 21}
  assert rerun.notes[0].startswith("Explicit paper rerun from boundary ")
  assert rerun.notes[1] == "Paper rerun seeded the current paper session from the stored effective market-data window."
  assert rerun.notes[-1] == (
    "Mode-specific rerun boundary drift is expected when replaying a stored boundary into a different execution mode."
  )


def test_compare_runs_returns_side_by_side_native_and_reference_summary(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )

  native_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  reference_run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  comparison = app.compare_runs(run_ids=[native_run.config.run_id, reference_run.config.run_id])

  assert comparison.intent == "benchmark_validation"
  assert comparison.baseline_run_id == native_run.config.run_id
  assert [run.lane for run in comparison.runs] == ["native", "reference"]
  assert comparison.runs[1].reference_id == "nostalgia-for-infinity"
  assert comparison.runs[1].reference is not None
  assert comparison.runs[1].reference.integration_mode == "external_runtime"
  assert comparison.runs[1].artifact_paths
  assert comparison.runs[1].benchmark_artifacts
  assert all(isinstance(artifact.summary, dict) for artifact in comparison.runs[1].benchmark_artifacts)
  assert all(isinstance(artifact.sections, dict) for artifact in comparison.runs[1].benchmark_artifacts)
  assert len(comparison.narratives) == 1
  assert comparison.narratives[0].comparison_type == "native_vs_reference"
  assert comparison.narratives[0].run_id == reference_run.config.run_id
  assert comparison.narratives[0].rank == 1
  assert comparison.narratives[0].is_primary is True
  assert comparison.narratives[0].insight_score > 0
  assert comparison.narratives[0].title.startswith("Benchmark validation")
  assert comparison.narratives[0].summary == (
    "Benchmark validation falls back to persisted reference provenance because direct metric "
    "deltas are partial."
  )
  metric_rows = {row.key: row for row in comparison.metric_rows}
  assert set(metric_rows) == {
    "total_return_pct",
    "max_drawdown_pct",
    "win_rate_pct",
    "trade_count",
  }
  assert metric_rows["total_return_pct"].annotation == (
    "Validation read: return drift versus the selected benchmark baseline."
  )
  assert metric_rows["total_return_pct"].delta_annotations[native_run.config.run_id] == "benchmark baseline"
  assert metric_rows["total_return_pct"].values[native_run.config.run_id] == native_run.metrics["total_return_pct"]
  assert reference_run.config.run_id in metric_rows["trade_count"].values
  assert comparison.runs[1].notes


def test_compare_runs_uses_reference_artifact_summary_for_divergence_narratives(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )

  native_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  reference_run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  reference_run.provenance.benchmark_artifacts = (
    BenchmarkArtifact(
      kind="result_snapshot_root",
      label="Backtest results root",
      path="/tmp/reference/backtest_results",
      summary={
        "strategy_name": "NostalgiaForInfinityX7",
        "profit_total_pct": 12.4,
        "max_drawdown_pct": 7.2,
        "trade_count": 36,
      },
      sections={
        "benchmark_story": {
          "headline": "NostalgiaForInfinityX7 returned 12.4% across 36 trades with 7.2% max drawdown.",
          "signal_context": "Signal exports captured 36 rows across 10 pairs.",
        },
      },
    ),
  )
  runs.save_run(reference_run)

  comparison = app.compare_runs(run_ids=[native_run.config.run_id, reference_run.config.run_id])

  assert comparison.intent == "benchmark_validation"
  metric_rows = {row.key: row for row in comparison.metric_rows}
  assert metric_rows["total_return_pct"].values[reference_run.config.run_id] == 12.4
  assert metric_rows["max_drawdown_pct"].values[reference_run.config.run_id] == 7.2
  assert metric_rows["trade_count"].values[reference_run.config.run_id] == 36
  assert "benchmark" in metric_rows["total_return_pct"].delta_annotations[reference_run.config.run_id]
  assert "benchmark" in metric_rows["max_drawdown_pct"].delta_annotations[reference_run.config.run_id]
  assert len(comparison.narratives) == 1
  assert comparison.narratives[0].comparison_type == "native_vs_reference"
  assert comparison.narratives[0].rank == 1
  assert comparison.narratives[0].is_primary is True
  assert comparison.narratives[0].title.startswith("Benchmark validation")
  assert "benchmark drift" in comparison.narratives[0].summary
  assert any(
    bullet.startswith("Benchmark evidence: NostalgiaForInfinityX7 returned 12.4%")
    for bullet in comparison.narratives[0].bullets
  )


def test_compare_runs_reweights_multi_run_narratives_by_intent(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
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
  reference_run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  baseline_run.metrics.update({
    "total_return_pct": 10.0,
    "max_drawdown_pct": 5.0,
    "win_rate_pct": 60.0,
    "trade_count": 20,
  })
  alternate_native_run.metrics.update({
    "total_return_pct": 15.0,
    "max_drawdown_pct": 7.0,
    "win_rate_pct": 64.0,
    "trade_count": 30,
  })
  reference_run.provenance.benchmark_artifacts = (
    BenchmarkArtifact(
      kind="result_snapshot_root",
      label="Backtest results root",
      path="/tmp/reference/backtest_results",
      summary={
        "strategy_name": "NostalgiaForInfinityX7",
        "profit_total_pct": 12.0,
        "max_drawdown_pct": 6.0,
        "trade_count": 22,
        "win_rate_pct": 61.0,
      },
      sections={
        "benchmark_story": {
          "headline": "NostalgiaForInfinityX7 returned 12% across 22 trades with 6% max drawdown.",
        },
      },
    ),
  )

  runs.save_run(baseline_run)
  runs.save_run(alternate_native_run)
  runs.save_run(reference_run)

  benchmark_validation = app.compare_runs(
    run_ids=[
      baseline_run.config.run_id,
      alternate_native_run.config.run_id,
      reference_run.config.run_id,
    ],
    intent="benchmark_validation",
  )
  strategy_tuning = app.compare_runs(
    run_ids=[
      baseline_run.config.run_id,
      alternate_native_run.config.run_id,
      reference_run.config.run_id,
    ],
    intent="strategy_tuning",
  )
  execution_regression = app.compare_runs(
    run_ids=[
      baseline_run.config.run_id,
      alternate_native_run.config.run_id,
      reference_run.config.run_id,
    ],
    intent="execution_regression",
  )

  assert benchmark_validation.intent == "benchmark_validation"
  assert [narrative.run_id for narrative in benchmark_validation.narratives] == [
    reference_run.config.run_id,
    alternate_native_run.config.run_id,
  ]
  benchmark_metric_rows = {row.key: row for row in benchmark_validation.metric_rows}
  assert [narrative.rank for narrative in benchmark_validation.narratives] == [1, 2]
  assert benchmark_validation.narratives[0].is_primary is True
  assert benchmark_validation.narratives[0].comparison_type == "native_vs_reference"
  assert benchmark_validation.narratives[0].title.startswith("Benchmark validation")
  assert "benchmark drift" in benchmark_validation.narratives[0].summary
  assert any(
    bullet.startswith("Benchmark evidence:")
    for bullet in benchmark_validation.narratives[0].bullets
  )

  assert strategy_tuning.intent == "strategy_tuning"
  assert [narrative.run_id for narrative in strategy_tuning.narratives] == [
    alternate_native_run.config.run_id,
    reference_run.config.run_id,
  ]
  strategy_metric_rows = {row.key: row for row in strategy_tuning.metric_rows}
  assert [narrative.rank for narrative in strategy_tuning.narratives] == [1, 2]
  assert strategy_tuning.narratives[0].is_primary is True
  assert strategy_tuning.narratives[0].comparison_type == "native_vs_native"
  assert strategy_tuning.narratives[0].title.startswith("Strategy tuning")
  assert "optimization tradeoffs" in strategy_tuning.narratives[0].summary
  assert any(
    bullet.startswith("Tuning signal:")
    for bullet in strategy_tuning.narratives[0].bullets
  )

  assert execution_regression.intent == "execution_regression"
  execution_metric_rows = {row.key: row for row in execution_regression.metric_rows}
  assert execution_regression.narratives[0].run_id == alternate_native_run.config.run_id
  assert execution_regression.narratives[0].title.startswith("Execution regression")
  assert "execution drift" in execution_regression.narratives[0].summary
  assert any(
    bullet.startswith("Execution signal:")
    for bullet in execution_regression.narratives[0].bullets
  )
  assert benchmark_metric_rows["total_return_pct"].annotation == (
    "Validation read: return drift versus the selected benchmark baseline."
  )
  assert strategy_metric_rows["total_return_pct"].annotation == (
    "Tuning read: return deltas show optimization edge versus the baseline."
  )
  assert execution_metric_rows["total_return_pct"].annotation == (
    "Regression read: return movement is treated as execution drift."
  )
  assert benchmark_metric_rows["total_return_pct"].delta_annotations[reference_run.config.run_id] == "2 pts above benchmark"
  assert strategy_metric_rows["total_return_pct"].delta_annotations[alternate_native_run.config.run_id] == "5 pts tuning edge"
  assert execution_metric_rows["trade_count"].delta_annotations[alternate_native_run.config.run_id] == "10 extra activity"
  assert benchmark_validation.narratives[0].insight_score > benchmark_validation.narratives[1].insight_score
  assert strategy_tuning.narratives[0].insight_score > strategy_tuning.narratives[1].insight_score


def test_backtest_failure_still_records_requested_market_lineage(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
  assert run.provenance.market_data.requested_start_at == datetime(2030, 1, 1, tzinfo=UTC)
  assert run.provenance.market_data.candle_count == 0
  assert run.provenance.rerun_boundary_id is not None
  assert run.provenance.rerun_boundary_state == "range_only"


def test_multi_symbol_run_records_market_lineage_per_symbol(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
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
