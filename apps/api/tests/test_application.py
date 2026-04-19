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
    self.pull_sync_attempts: list[tuple[str, str, str | None]] = []
    self._failures_before_success = dict(failures_before_success or {})
    self._workflow_failures_before_success = dict(workflow_failures_before_success or {})
    self._attempts_by_target: dict[str, int] = {}
    self._workflow_attempts_by_key: dict[tuple[str, str], int] = {}
    self._pull_sync_by_key: dict[tuple[str, str], OperatorIncidentProviderPullSync] = {}
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
      elif target == "incidentio_incidents":
        external_provider = "incidentio"
      elif target == "firehydrant_incidents":
        external_provider = "firehydrant"
      elif target == "rootly_incidents":
        external_provider = "rootly"
      elif target == "blameless_incidents":
        external_provider = "blameless"
      elif target == "xmatters_incidents":
        external_provider = "xmatters"
      elif target == "servicenow_incidents":
        external_provider = "servicenow"
      elif target == "squadcast_incidents":
        external_provider = "squadcast"
      elif target == "bigpanda_incidents":
        external_provider = "bigpanda"
      elif target == "grafana_oncall_incidents":
        external_provider = "grafana_oncall"
      elif target == "splunk_oncall_incidents":
        external_provider = "splunk_oncall"
      elif target == "jira_service_management_incidents":
        external_provider = "jira_service_management"
      elif target == "pagertree_incidents":
        external_provider = "pagertree"
      elif target == "alertops_incidents":
        external_provider = "alertops"
      elif target == "signl4_incidents":
        external_provider = "signl4"
      elif target == "ilert_incidents":
        external_provider = "ilert"
      elif target == "betterstack_incidents":
        external_provider = "betterstack"
      elif target == "onpage_incidents":
        external_provider = "onpage"
      elif target == "allquiet_incidents":
        external_provider = "allquiet"
      elif target == "moogsoft_incidents":
        external_provider = "moogsoft"
      elif target == "spikesh_incidents":
        external_provider = "spikesh"
      elif target == "dutycalls_incidents":
        external_provider = "dutycalls"
      elif target == "incidenthub_incidents":
        external_provider = "incidenthub"
      elif target == "resolver_incidents":
        external_provider = "resolver"
      elif target == "openduty_incidents":
        external_provider = "openduty"
      elif target == "cabot_incidents":
        external_provider = "cabot"
      elif target == "haloitsm_incidents":
        external_provider = "haloitsm"
      elif target == "incidentmanagerio_incidents":
        external_provider = "incidentmanagerio"
      elif target == "oneuptime_incidents":
        external_provider = "oneuptime"
      elif target == "squzy_incidents":
        external_provider = "squzy"
      elif target == "crisescontrol_incidents":
        external_provider = "crisescontrol"
      elif target == "freshservice_incidents":
        external_provider = "freshservice"
      elif target == "freshdesk_incidents":
        external_provider = "freshdesk"
      elif target == "happyfox_incidents":
        external_provider = "happyfox"
      elif target == "zendesk_incidents":
        external_provider = "zendesk"
      elif target == "zohodesk_incidents":
        external_provider = "zohodesk"
      elif target == "helpscout_incidents":
        external_provider = "helpscout"
      elif target == "kayako_incidents":
        external_provider = "kayako"
      elif target == "intercom_incidents":
        external_provider = "intercom"
      elif target == "front_incidents":
        external_provider = "front"
      elif target == "servicedeskplus_incidents":
        external_provider = "servicedeskplus"
      elif target == "sysaid_incidents":
        external_provider = "sysaid"
      elif target == "bmchelix_incidents":
        external_provider = "bmchelix"
      elif target == "solarwindsservicedesk_incidents":
        external_provider = "solarwindsservicedesk"
      elif target == "topdesk_incidents":
        external_provider = "topdesk"
      elif target == "invgateservicedesk_incidents":
        external_provider = "invgateservicedesk"
      elif target == "opsramp_incidents":
        external_provider = "opsramp"
      elif target == "zenduty_incidents":
        external_provider = "zenduty"
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

  def set_pull_sync(
    self,
    *,
    provider: str,
    reference: str,
    snapshot: OperatorIncidentProviderPullSync,
  ) -> None:
    self._pull_sync_by_key[(provider, reference)] = snapshot

  def pull_incident_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference
    self.pull_sync_attempts.append((incident.event_id, provider, reference))
    if reference is None:
      return None
    return self._pull_sync_by_key.get((provider, reference))


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
        "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
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


def test_external_opsgenie_recovery_sync_populates_opsgenie_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 50, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("opsgenie_alerts",),
    supported_workflow_providers=("opsgenie",),
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
    operator_alert_paging_policy_default_provider="opsgenie",
    operator_alert_paging_policy_warning_targets=("opsgenie_alerts",),
    operator_alert_paging_policy_critical_targets=("opsgenie_alerts",),
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
    operator_reason="opsgenie_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="opsgenie",
    event_kind="remediation_started",
    actor="opsgenie",
    detail="opsgenie_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OG-REC-1",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "og-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "opsgenie": {
        "alert_id": "OG-REC-1",
        "alias": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "P3",
        "owner": "oncall-primary",
        "teams": ["market-data"],
        "tiny_id": "42",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 45,
        "attempt_count": 1,
        "current_step": "backfill",
        "last_message": "opsgenie recovery started",
        "external_run_id": "og-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "opsgenie"
  assert updated_incident.remediation.provider_recovery.opsgenie.alert_id == "OG-REC-1"
  assert updated_incident.remediation.provider_recovery.opsgenie.alias == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.opsgenie.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.opsgenie.priority == "P3"
  assert updated_incident.remediation.provider_recovery.opsgenie.owner == "oncall-primary"
  assert updated_incident.remediation.provider_recovery.opsgenie.teams == ("market-data",)
  assert updated_incident.remediation.provider_recovery.opsgenie.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.opsgenie.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.opsgenie.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 45
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "backfill"


def test_external_blameless_recovery_sync_populates_blameless_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 5, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("blameless_incidents",),
    supported_workflow_providers=("blameless",),
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
    operator_alert_paging_policy_default_provider="blameless",
    operator_alert_paging_policy_warning_targets=("blameless_incidents",),
    operator_alert_paging_policy_critical_targets=("blameless_incidents",),
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
    operator_reason="blameless_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="blameless",
    event_kind="remediation_started",
    actor="blameless",
    detail="blameless_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BL-REC-1",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "bl-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "blameless": {
        "incident_id": "BL-REC-1",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "severity": "sev2",
        "commander": "market-data-oncall",
        "visibility": "private",
        "url": "https://blameless.example/incidents/BL-REC-1",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 55,
        "attempt_count": 1,
        "current_step": "repair_candles",
        "last_message": "blameless recovery started",
        "external_run_id": "bl-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "blameless"
  assert updated_incident.remediation.provider_recovery.blameless.incident_id == "BL-REC-1"
  assert updated_incident.remediation.provider_recovery.blameless.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.blameless.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.blameless.severity == "sev2"
  assert updated_incident.remediation.provider_recovery.blameless.commander == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.blameless.visibility == "private"
  assert updated_incident.remediation.provider_recovery.blameless.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.blameless.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.blameless.phase_graph.command_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 55
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_candles"


def test_external_xmatters_recovery_sync_populates_xmatters_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 20, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("xmatters_incidents",),
    supported_workflow_providers=("xmatters",),
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
    operator_alert_paging_policy_default_provider="xmatters",
    operator_alert_paging_policy_warning_targets=("xmatters_incidents",),
    operator_alert_paging_policy_critical_targets=("xmatters_incidents",),
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
    operator_reason="xmatters_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="xmatters",
    event_kind="remediation_started",
    actor="xmatters",
    detail="xmatters_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="XM-REC-1",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "xm-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "xmatters": {
        "incident_id": "XM-REC-1",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "priority": "P2",
        "assignee": "market-data-oncall",
        "response_plan": "market-data-repair",
        "url": "https://xmatters.example/incidents/XM-REC-1",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 60,
        "attempt_count": 1,
        "current_step": "backfill_window",
        "last_message": "xmatters recovery started",
        "external_run_id": "xm-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "xmatters"
  assert updated_incident.remediation.provider_recovery.xmatters.incident_id == "XM-REC-1"
  assert updated_incident.remediation.provider_recovery.xmatters.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.xmatters.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.xmatters.priority == "P2"
  assert updated_incident.remediation.provider_recovery.xmatters.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.xmatters.response_plan == "market-data-repair"
  assert updated_incident.remediation.provider_recovery.xmatters.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.xmatters.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.xmatters.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 60
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "backfill_window"


def test_external_servicenow_recovery_sync_populates_servicenow_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 25, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("servicenow_incidents",),
    supported_workflow_providers=("servicenow",),
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
    operator_alert_paging_policy_default_provider="servicenow",
    operator_alert_paging_policy_warning_targets=("servicenow_incidents",),
    operator_alert_paging_policy_critical_targets=("servicenow_incidents",),
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
    operator_reason="servicenow_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="servicenow",
    event_kind="remediation_started",
    actor="servicenow",
    detail="servicenow_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="INC00123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "sn-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "servicenow": {
        "incident_number": "INC00123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "in_progress",
        "priority": "2",
        "assigned_to": "market-data-oncall",
        "assignment_group": "market-data-ops",
        "url": "https://servicenow.example/incidents/INC00123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 65,
        "attempt_count": 1,
        "current_step": "verify_freshness_window",
        "last_message": "servicenow recovery started",
        "external_run_id": "sn-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "servicenow"
  assert updated_incident.remediation.provider_recovery.servicenow.incident_number == "INC00123"
  assert updated_incident.remediation.provider_recovery.servicenow.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.servicenow.incident_status == "in_progress"
  assert updated_incident.remediation.provider_recovery.servicenow.priority == "2"
  assert updated_incident.remediation.provider_recovery.servicenow.assigned_to == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.servicenow.assignment_group == "market-data-ops"
  assert updated_incident.remediation.provider_recovery.servicenow.phase_graph.incident_phase == "in_progress"
  assert updated_incident.remediation.provider_recovery.servicenow.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.servicenow.phase_graph.assignment_phase == "assigned_to_user"
  assert updated_incident.remediation.provider_recovery.servicenow.phase_graph.group_phase == "group_configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 65
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_freshness_window"


def test_external_squadcast_recovery_sync_populates_squadcast_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 28, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("squadcast_incidents",),
    supported_workflow_providers=("squadcast",),
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
    operator_alert_paging_policy_default_provider="squadcast",
    operator_alert_paging_policy_warning_targets=("squadcast_incidents",),
    operator_alert_paging_policy_critical_targets=("squadcast_incidents",),
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
    operator_reason="squadcast_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="squadcast",
    event_kind="remediation_started",
    actor="squadcast",
    detail="squadcast_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SC-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "sc-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "squadcast": {
        "incident_id": "SC-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "severity": "high",
        "assignee": "market-data-oncall",
        "escalation_policy": "market-data-primary",
        "url": "https://squadcast.example/incidents/SC-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 58,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "squadcast recovery started",
        "external_run_id": "sc-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "squadcast"
  assert updated_incident.remediation.provider_recovery.squadcast.incident_id == "SC-123"
  assert updated_incident.remediation.provider_recovery.squadcast.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.squadcast.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.squadcast.severity == "high"
  assert updated_incident.remediation.provider_recovery.squadcast.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.squadcast.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.squadcast.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.squadcast.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.squadcast.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.squadcast.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 58
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_external_bigpanda_recovery_sync_populates_bigpanda_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 31, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("bigpanda_incidents",),
    supported_workflow_providers=("bigpanda",),
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
    operator_alert_paging_policy_default_provider="bigpanda",
    operator_alert_paging_policy_warning_targets=("bigpanda_incidents",),
    operator_alert_paging_policy_critical_targets=("bigpanda_incidents",),
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
    operator_reason="bigpanda_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="bigpanda",
    event_kind="remediation_started",
    actor="bigpanda",
    detail="bigpanda_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BP-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "bp-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "bigpanda": {
        "incident_id": "BP-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "severity": "high",
        "assignee": "market-data-oncall",
        "team": "market-data-team",
        "url": "https://bigpanda.example/incidents/BP-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 61,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "bigpanda recovery started",
        "external_run_id": "bp-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "bigpanda"
  assert updated_incident.remediation.provider_recovery.bigpanda.incident_id == "BP-123"
  assert updated_incident.remediation.provider_recovery.bigpanda.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.bigpanda.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.bigpanda.severity == "high"
  assert updated_incident.remediation.provider_recovery.bigpanda.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.bigpanda.team == "market-data-team"
  assert updated_incident.remediation.provider_recovery.bigpanda.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.bigpanda.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.bigpanda.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.bigpanda.phase_graph.team_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 61
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_external_grafana_oncall_recovery_sync_populates_grafana_oncall_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 34, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("grafana_oncall_incidents",),
    supported_workflow_providers=("grafana_oncall",),
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
    operator_alert_paging_policy_default_provider="grafana_oncall",
    operator_alert_paging_policy_warning_targets=("grafana_oncall_incidents",),
    operator_alert_paging_policy_critical_targets=("grafana_oncall_incidents",),
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
    operator_reason="grafana_oncall_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="grafana_oncall",
    event_kind="remediation_started",
    actor="grafana_oncall",
    detail="grafana_oncall_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="GO-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "go-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "grafana_oncall": {
        "incident_id": "GO-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "severity": "high",
        "assignee": "market-data-oncall",
        "escalation_chain": "market-data-primary",
        "url": "https://grafana-oncall.example/incidents/GO-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 63,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "grafana oncall recovery started",
        "external_run_id": "go-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "grafana_oncall"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.incident_id == "GO-123"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.severity == "high"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.escalation_chain == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.grafana_oncall.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 63
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_external_zenduty_recovery_sync_populates_zenduty_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 36, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("zenduty_incidents",),
    supported_workflow_providers=("zenduty",),
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
    operator_alert_paging_policy_default_provider="zenduty",
    operator_alert_paging_policy_warning_targets=("zenduty_incidents",),
    operator_alert_paging_policy_critical_targets=("zenduty_incidents",),
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
    operator_reason="zenduty_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="zenduty",
    event_kind="remediation_started",
    actor="zenduty",
    detail="zenduty_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="ZD-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "zd-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "zenduty": {
        "incident_id": "ZD-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "severity": "high",
        "assignee": "market-data-oncall",
        "service": "market-data-sync",
        "url": "https://zenduty.example/incidents/ZD-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 64,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "zenduty recovery started",
        "external_run_id": "zd-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "zenduty"
  assert updated_incident.remediation.provider_recovery.zenduty.incident_id == "ZD-123"
  assert updated_incident.remediation.provider_recovery.zenduty.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.zenduty.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.zenduty.severity == "high"
  assert updated_incident.remediation.provider_recovery.zenduty.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.zenduty.service == "market-data-sync"
  assert updated_incident.remediation.provider_recovery.zenduty.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.zenduty.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.zenduty.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.zenduty.phase_graph.service_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 64
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_external_splunk_oncall_recovery_sync_populates_splunk_oncall_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 40, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("splunk_oncall_incidents",),
    supported_workflow_providers=("splunk_oncall",),
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
    operator_alert_paging_policy_default_provider="splunk_oncall",
    operator_alert_paging_policy_warning_targets=("splunk_oncall_incidents",),
    operator_alert_paging_policy_critical_targets=("splunk_oncall_incidents",),
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
    operator_reason="splunk_oncall_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="splunk_oncall",
    event_kind="remediation_started",
    actor="splunk_oncall",
    detail="splunk_oncall_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SOC-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "soc-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "splunk_oncall": {
        "incident_id": "SOC-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "severity": "high",
        "assignee": "market-data-oncall",
        "routing_key": "market-data-primary",
        "url": "https://splunk-oncall.example/incidents/SOC-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 65,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "splunk on-call recovery started",
        "external_run_id": "soc-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "splunk_oncall"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.incident_id == "SOC-123"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.severity == "high"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.routing_key == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.splunk_oncall.phase_graph.routing_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 65
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_external_jira_service_management_recovery_sync_populates_jira_service_management_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 42, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("jira_service_management_incidents",),
    supported_workflow_providers=("jira_service_management",),
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
    operator_alert_paging_policy_default_provider="jira_service_management",
    operator_alert_paging_policy_warning_targets=("jira_service_management_incidents",),
    operator_alert_paging_policy_critical_targets=("jira_service_management_incidents",),
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
    operator_reason="jsm_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="jira_service_management",
    event_kind="remediation_started",
    actor="jira_service_management",
    detail="jsm_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="JSM-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "jsm-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "jira_service_management": {
        "incident_id": "JSM-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "priority": "high",
        "assignee": "market-data-oncall",
        "service_project": "market-data-platform",
        "url": "https://jsm.example/incidents/JSM-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 66,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "jsm recovery started",
        "external_run_id": "jsm-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "jira_service_management"
  assert updated_incident.remediation.provider_recovery.jira_service_management.incident_id == "JSM-123"
  assert updated_incident.remediation.provider_recovery.jira_service_management.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.jira_service_management.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.jira_service_management.priority == "high"
  assert updated_incident.remediation.provider_recovery.jira_service_management.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.jira_service_management.service_project == "market-data-platform"
  assert updated_incident.remediation.provider_recovery.jira_service_management.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.jira_service_management.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.jira_service_management.phase_graph.assignment_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.jira_service_management.phase_graph.project_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 66
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_external_pagertree_recovery_sync_populates_pagertree_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 43, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagertree_incidents",),
    supported_workflow_providers=("pagertree",),
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
    operator_alert_paging_policy_default_provider="pagertree",
    operator_alert_paging_policy_warning_targets=("pagertree_incidents",),
    operator_alert_paging_policy_critical_targets=("pagertree_incidents",),
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
    operator_reason="pagertree_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="pagertree",
    event_kind="remediation_started",
    actor="pagertree",
    detail="pagertree_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="PT-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "pt-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "pagertree": {
        "incident_id": "PT-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "urgency": "high",
        "assignee": "market-data-oncall",
        "team": "market-data-platform",
        "url": "https://pagertree.example/incidents/PT-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 67,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "pagertree recovery started",
        "external_run_id": "pagertree-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "pagertree"
  assert updated_incident.remediation.provider_recovery.pagertree.incident_id == "PT-123"
  assert updated_incident.remediation.provider_recovery.pagertree.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.pagertree.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.pagertree.urgency == "high"
  assert updated_incident.remediation.provider_recovery.pagertree.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.pagertree.team == "market-data-platform"
  assert updated_incident.remediation.provider_recovery.pagertree.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.pagertree.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.pagertree.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.pagertree.phase_graph.team_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 67
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


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


def test_incident_paging_provider_can_be_inferred_for_incidentio_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 14, 50, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("incidentio_incidents",),
    supported_workflow_providers=("incidentio",),
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
    operator_alert_paging_policy_warning_targets=("incidentio_incidents",),
    operator_alert_paging_policy_critical_targets=("incidentio_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("incidentio_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("incidentio_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="incidentio_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "incidentio"
  assert incident.delivery_targets == ("incidentio_incidents",)
  assert incident.escalation_targets == ("incidentio_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="incidentio",
    event_kind="triggered",
    actor="incidentio",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="INC-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "INC-123"
  assert triggered.external_provider == "incidentio"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="incidentio_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("incidentio", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_firehydrant_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 10, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("firehydrant_incidents",),
    supported_workflow_providers=("firehydrant",),
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
    operator_alert_paging_policy_warning_targets=("firehydrant_incidents",),
    operator_alert_paging_policy_critical_targets=("firehydrant_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("firehydrant_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("firehydrant_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="firehydrant_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "firehydrant"
  assert incident.delivery_targets == ("firehydrant_incidents",)
  assert incident.escalation_targets == ("firehydrant_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="firehydrant",
    event_kind="triggered",
    actor="firehydrant",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="FH-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "FH-123"
  assert triggered.external_provider == "firehydrant"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="firehydrant_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("firehydrant", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_rootly_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 30, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("rootly_incidents",),
    supported_workflow_providers=("rootly",),
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
    operator_alert_paging_policy_warning_targets=("rootly_incidents",),
    operator_alert_paging_policy_critical_targets=("rootly_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("rootly_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("rootly_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="rootly_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "rootly"
  assert incident.delivery_targets == ("rootly_incidents",)
  assert incident.escalation_targets == ("rootly_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="rootly",
    event_kind="triggered",
    actor="rootly",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="RT-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "RT-123"
  assert triggered.external_provider == "rootly"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="rootly_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("rootly", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_blameless_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 45, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("blameless_incidents",),
    supported_workflow_providers=("blameless",),
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
    operator_alert_paging_policy_warning_targets=("blameless_incidents",),
    operator_alert_paging_policy_critical_targets=("blameless_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("blameless_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("blameless_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="blameless_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "blameless"
  assert incident.delivery_targets == ("blameless_incidents",)
  assert incident.escalation_targets == ("blameless_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="blameless",
    event_kind="triggered",
    actor="blameless",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BL-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "BL-123"
  assert triggered.external_provider == "blameless"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="blameless_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("blameless", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_xmatters_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 55, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("xmatters_incidents",),
    supported_workflow_providers=("xmatters",),
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
    operator_alert_paging_policy_warning_targets=("xmatters_incidents",),
    operator_alert_paging_policy_critical_targets=("xmatters_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("xmatters_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("xmatters_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="xmatters_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "xmatters"
  assert incident.delivery_targets == ("xmatters_incidents",)
  assert incident.escalation_targets == ("xmatters_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="xmatters",
    event_kind="triggered",
    actor="xmatters",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="XM-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "XM-123"
  assert triggered.external_provider == "xmatters"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="xmatters_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("xmatters", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_servicenow_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 57, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("servicenow_incidents",),
    supported_workflow_providers=("servicenow",),
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
    operator_alert_paging_policy_warning_targets=("servicenow_incidents",),
    operator_alert_paging_policy_critical_targets=("servicenow_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("servicenow_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("servicenow_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="servicenow_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "servicenow"
  assert incident.delivery_targets == ("servicenow_incidents",)
  assert incident.escalation_targets == ("servicenow_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="servicenow",
    event_kind="triggered",
    actor="servicenow",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="INC00123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "INC00123"
  assert triggered.external_provider == "servicenow"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="servicenow_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("servicenow", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_squadcast_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 58, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("squadcast_incidents",),
    supported_workflow_providers=("squadcast",),
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
    operator_alert_paging_policy_warning_targets=("squadcast_incidents",),
    operator_alert_paging_policy_critical_targets=("squadcast_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("squadcast_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("squadcast_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="squadcast_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "squadcast"
  assert incident.delivery_targets == ("squadcast_incidents",)
  assert incident.escalation_targets == ("squadcast_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="squadcast",
    event_kind="triggered",
    actor="squadcast",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SC-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "SC-123"
  assert triggered.external_provider == "squadcast"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="squadcast_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("squadcast", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_bigpanda_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 15, 59, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("bigpanda_incidents",),
    supported_workflow_providers=("bigpanda",),
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
    operator_alert_paging_policy_warning_targets=("bigpanda_incidents",),
    operator_alert_paging_policy_critical_targets=("bigpanda_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("bigpanda_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("bigpanda_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="bigpanda_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "bigpanda"
  assert incident.delivery_targets == ("bigpanda_incidents",)
  assert incident.escalation_targets == ("bigpanda_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="bigpanda",
    event_kind="triggered",
    actor="bigpanda",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BP-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "BP-123"
  assert triggered.external_provider == "bigpanda"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="bigpanda_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("bigpanda", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_grafana_oncall_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 1, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("grafana_oncall_incidents",),
    supported_workflow_providers=("grafana_oncall",),
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
    operator_alert_paging_policy_warning_targets=("grafana_oncall_incidents",),
    operator_alert_paging_policy_critical_targets=("grafana_oncall_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("grafana_oncall_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("grafana_oncall_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="grafana_oncall_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "grafana_oncall"
  assert incident.delivery_targets == ("grafana_oncall_incidents",)
  assert incident.escalation_targets == ("grafana_oncall_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="grafana_oncall",
    event_kind="triggered",
    actor="grafana_oncall",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="GO-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "GO-123"
  assert triggered.external_provider == "grafana_oncall"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="grafana_oncall_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("grafana_oncall", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_zenduty_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 2, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("zenduty_incidents",),
    supported_workflow_providers=("zenduty",),
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
    operator_alert_paging_policy_warning_targets=("zenduty_incidents",),
    operator_alert_paging_policy_critical_targets=("zenduty_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("zenduty_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("zenduty_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="zenduty_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "zenduty"
  assert incident.delivery_targets == ("zenduty_incidents",)
  assert incident.escalation_targets == ("zenduty_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="zenduty",
    event_kind="triggered",
    actor="zenduty",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="ZD-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "ZD-123"
  assert triggered.external_provider == "zenduty"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="zenduty_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("zenduty", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_splunk_oncall_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 4, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("splunk_oncall_incidents",),
    supported_workflow_providers=("splunk_oncall",),
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
    operator_alert_paging_policy_warning_targets=("splunk_oncall_incidents",),
    operator_alert_paging_policy_critical_targets=("splunk_oncall_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("splunk_oncall_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("splunk_oncall_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="splunk_oncall_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "splunk_oncall"
  assert incident.delivery_targets == ("splunk_oncall_incidents",)
  assert incident.escalation_targets == ("splunk_oncall_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="splunk_oncall",
    event_kind="triggered",
    actor="splunk_oncall",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SOC-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "SOC-123"
  assert triggered.external_provider == "splunk_oncall"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="splunk_oncall_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("splunk_oncall", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_jira_service_management_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 6, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("jira_service_management_incidents",),
    supported_workflow_providers=("jira_service_management",),
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
    operator_alert_paging_policy_warning_targets=("jira_service_management_incidents",),
    operator_alert_paging_policy_critical_targets=("jira_service_management_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("jira_service_management_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("jira_service_management_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="jsm_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "jira_service_management"
  assert incident.delivery_targets == ("jira_service_management_incidents",)
  assert incident.escalation_targets == ("jira_service_management_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="jira_service_management",
    event_kind="triggered",
    actor="jira_service_management",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="JSM-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "JSM-123"
  assert triggered.external_provider == "jira_service_management"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="jsm_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("jira_service_management", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_pagertree_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 7, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("pagertree_incidents",),
    supported_workflow_providers=("pagertree",),
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
    operator_alert_paging_policy_warning_targets=("pagertree_incidents",),
    operator_alert_paging_policy_critical_targets=("pagertree_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("pagertree_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("pagertree_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="pagertree_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "pagertree"
  assert incident.delivery_targets == ("pagertree_incidents",)
  assert incident.escalation_targets == ("pagertree_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="pagertree",
    event_kind="triggered",
    actor="pagertree",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="PT-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "PT-123"
  assert triggered.external_provider == "pagertree"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="pagertree_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("pagertree", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_alertops_recovery_sync_populates_alertops_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 44, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("alertops_incidents",),
    supported_workflow_providers=("alertops",),
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
    operator_alert_paging_policy_default_provider="alertops",
    operator_alert_paging_policy_warning_targets=("alertops_incidents",),
    operator_alert_paging_policy_critical_targets=("alertops_incidents",),
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
    operator_reason="alertops_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="alertops",
    event_kind="remediation_started",
    actor="alertops",
    detail="alertops_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="AO-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "ao-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "alertops": {
        "incident_id": "AO-123",
        "external_reference": "guarded-live:market-data:5m",
        "incident_status": "acknowledged",
        "priority": "p2",
        "owner": "market-data-oncall",
        "service": "market-data-platform",
        "url": "https://alertops.example/incidents/AO-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 68,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "alertops recovery started",
        "external_run_id": "alertops-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "alertops"
  assert updated_incident.remediation.provider_recovery.alertops.incident_id == "AO-123"
  assert updated_incident.remediation.provider_recovery.alertops.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.alertops.incident_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.alertops.priority == "p2"
  assert updated_incident.remediation.provider_recovery.alertops.owner == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.alertops.service == "market-data-platform"
  assert updated_incident.remediation.provider_recovery.alertops.phase_graph.incident_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.alertops.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.alertops.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.alertops.phase_graph.service_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 68
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_incident_paging_provider_can_be_inferred_for_alertops_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 8, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("alertops_incidents",),
    supported_workflow_providers=("alertops",),
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
    operator_alert_paging_policy_warning_targets=("alertops_incidents",),
    operator_alert_paging_policy_critical_targets=("alertops_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("alertops_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("alertops_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="alertops_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "alertops"
  assert incident.delivery_targets == ("alertops_incidents",)
  assert incident.escalation_targets == ("alertops_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="alertops",
    event_kind="triggered",
    actor="alertops",
    detail="provider_incident_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="AO-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "AO-123"
  assert triggered.external_provider == "alertops"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="alertops_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("alertops", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_signl4_recovery_sync_populates_signl4_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 45, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("signl4_incidents",),
    supported_workflow_providers=("signl4",),
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
    operator_alert_paging_policy_default_provider="signl4",
    operator_alert_paging_policy_warning_targets=("signl4_incidents",),
    operator_alert_paging_policy_critical_targets=("signl4_incidents",),
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
    operator_reason="signl4_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="signl4",
    event_kind="remediation_started",
    actor="signl4",
    detail="signl4_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="S4-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "s4-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "signl4": {
        "alert_id": "S4-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "team": "market-data-platform",
        "assignee": "market-data-oncall",
        "url": "https://signl4.example/alerts/S4-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 73,
        "attempt_count": 1,
        "current_step": "repair_channel_window",
        "last_message": "signl4 recovery started",
        "external_run_id": "signl4-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "signl4"
  assert updated_incident.remediation.provider_recovery.signl4.alert_id == "S4-123"
  assert updated_incident.remediation.provider_recovery.signl4.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.signl4.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.signl4.priority == "high"
  assert updated_incident.remediation.provider_recovery.signl4.team == "market-data-platform"
  assert updated_incident.remediation.provider_recovery.signl4.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.signl4.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.signl4.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.signl4.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.signl4.phase_graph.team_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 73
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "repair_channel_window"


def test_incident_paging_provider_can_be_inferred_for_signl4_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 9, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("signl4_incidents",),
    supported_workflow_providers=("signl4",),
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
    operator_alert_paging_policy_warning_targets=("signl4_incidents",),
    operator_alert_paging_policy_critical_targets=("signl4_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("signl4_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("signl4_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="signl4_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "signl4"
  assert incident.delivery_targets == ("signl4_incidents",)
  assert incident.escalation_targets == ("signl4_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="signl4",
    event_kind="triggered",
    actor="signl4",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="S4-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "S4-123"
  assert triggered.external_provider == "signl4"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="signl4_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("signl4", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_ilert_recovery_sync_populates_ilert_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 52, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("ilert_incidents",),
    supported_workflow_providers=("ilert",),
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
    operator_alert_paging_policy_default_provider="ilert",
    operator_alert_paging_policy_warning_targets=("ilert_incidents",),
    operator_alert_paging_policy_critical_targets=("ilert_incidents",),
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
    operator_reason="ilert_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="ilert",
    event_kind="remediation_started",
    actor="ilert",
    detail="ilert_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IL-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "ilert-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "ilert": {
        "alert_id": "IL-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "accepted",
        "priority": "HIGH",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://ilert.example/alerts/IL-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 67,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "ilert recovery started",
        "external_run_id": "ilert-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "ilert"
  assert updated_incident.remediation.provider_recovery.ilert.alert_id == "IL-123"
  assert updated_incident.remediation.provider_recovery.ilert.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.ilert.alert_status == "accepted"
  assert updated_incident.remediation.provider_recovery.ilert.priority == "HIGH"
  assert updated_incident.remediation.provider_recovery.ilert.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.ilert.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.ilert.phase_graph.alert_phase == "accepted"
  assert updated_incident.remediation.provider_recovery.ilert.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.ilert.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.ilert.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 67
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_ilert_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 12, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("ilert_incidents",),
    supported_workflow_providers=("ilert",),
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
    operator_alert_paging_policy_warning_targets=("ilert_incidents",),
    operator_alert_paging_policy_critical_targets=("ilert_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("ilert_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("ilert_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="ilert_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "ilert"
  assert incident.delivery_targets == ("ilert_incidents",)
  assert incident.escalation_targets == ("ilert_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="ilert",
    event_kind="triggered",
    actor="ilert",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IL-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "IL-123"
  assert triggered.external_provider == "ilert"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="ilert_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("ilert", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_betterstack_recovery_sync_populates_betterstack_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 2, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("betterstack_incidents",),
    supported_workflow_providers=("betterstack",),
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
    operator_alert_paging_policy_default_provider="betterstack",
    operator_alert_paging_policy_warning_targets=("betterstack_incidents",),
    operator_alert_paging_policy_critical_targets=("betterstack_incidents",),
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
    operator_reason="betterstack_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="betterstack",
    event_kind="remediation_started",
    actor="betterstack",
    detail="betterstack_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BS-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "betterstack-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "betterstack": {
        "alert_id": "BS-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://betterstack.example/alerts/BS-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 72,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "betterstack recovery started",
        "external_run_id": "betterstack-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "betterstack"
  assert updated_incident.remediation.provider_recovery.betterstack.alert_id == "BS-123"
  assert updated_incident.remediation.provider_recovery.betterstack.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.betterstack.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.betterstack.priority == "high"
  assert updated_incident.remediation.provider_recovery.betterstack.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.betterstack.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.betterstack.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.betterstack.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.betterstack.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.betterstack.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 72
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_betterstack_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 22, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("betterstack_incidents",),
    supported_workflow_providers=("betterstack",),
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
    operator_alert_paging_policy_warning_targets=("betterstack_incidents",),
    operator_alert_paging_policy_critical_targets=("betterstack_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("betterstack_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("betterstack_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="betterstack_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "betterstack"
  assert incident.delivery_targets == ("betterstack_incidents",)
  assert incident.escalation_targets == ("betterstack_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="betterstack",
    event_kind="triggered",
    actor="betterstack",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BS-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "BS-123"
  assert triggered.external_provider == "betterstack"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="betterstack_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("betterstack", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_onpage_recovery_sync_populates_onpage_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 12, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("onpage_incidents",),
    supported_workflow_providers=("onpage",),
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
    operator_alert_paging_policy_default_provider="onpage",
    operator_alert_paging_policy_warning_targets=("onpage_incidents",),
    operator_alert_paging_policy_critical_targets=("onpage_incidents",),
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
    operator_reason="onpage_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="onpage",
    event_kind="remediation_started",
    actor="onpage",
    detail="onpage_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OP-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "onpage-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "onpage": {
        "alert_id": "OP-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://onpage.example/alerts/OP-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 74,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "onpage recovery started",
        "external_run_id": "onpage-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "onpage"
  assert updated_incident.remediation.provider_recovery.onpage.alert_id == "OP-123"
  assert updated_incident.remediation.provider_recovery.onpage.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.onpage.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.onpage.priority == "high"
  assert updated_incident.remediation.provider_recovery.onpage.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.onpage.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.onpage.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.onpage.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.onpage.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.onpage.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 74
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_onpage_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 32, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("onpage_incidents",),
    supported_workflow_providers=("onpage",),
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
    operator_alert_paging_policy_warning_targets=("onpage_incidents",),
    operator_alert_paging_policy_critical_targets=("onpage_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("onpage_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("onpage_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="onpage_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "onpage"
  assert incident.delivery_targets == ("onpage_incidents",)
  assert incident.escalation_targets == ("onpage_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="onpage",
    event_kind="triggered",
    actor="onpage",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OP-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "OP-123"
  assert triggered.external_provider == "onpage"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="onpage_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("onpage", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_allquiet_recovery_sync_populates_allquiet_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 18, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("allquiet_incidents",),
    supported_workflow_providers=("allquiet",),
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
    operator_alert_paging_policy_default_provider="allquiet",
    operator_alert_paging_policy_warning_targets=("allquiet_incidents",),
    operator_alert_paging_policy_critical_targets=("allquiet_incidents",),
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
    operator_reason="allquiet_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="allquiet",
    event_kind="remediation_started",
    actor="allquiet",
    detail="allquiet_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="AQ-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "allquiet-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "allquiet": {
        "alert_id": "AQ-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://allquiet.example/alerts/AQ-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 74,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "allquiet recovery started",
        "external_run_id": "allquiet-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "allquiet"
  assert updated_incident.remediation.provider_recovery.allquiet.alert_id == "AQ-123"
  assert updated_incident.remediation.provider_recovery.allquiet.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.allquiet.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.allquiet.priority == "high"
  assert updated_incident.remediation.provider_recovery.allquiet.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.allquiet.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.allquiet.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.allquiet.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.allquiet.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.allquiet.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 74
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_allquiet_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 36, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("allquiet_incidents",),
    supported_workflow_providers=("allquiet",),
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
    operator_alert_paging_policy_warning_targets=("allquiet_incidents",),
    operator_alert_paging_policy_critical_targets=("allquiet_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("allquiet_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("allquiet_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="allquiet_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "allquiet"
  assert incident.delivery_targets == ("allquiet_incidents",)
  assert incident.escalation_targets == ("allquiet_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="allquiet",
    event_kind="triggered",
    actor="allquiet",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="AQ-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "AQ-123"
  assert triggered.external_provider == "allquiet"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="allquiet_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("allquiet", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_moogsoft_recovery_sync_populates_moogsoft_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 24, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("moogsoft_incidents",),
    supported_workflow_providers=("moogsoft",),
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
    operator_alert_paging_policy_default_provider="moogsoft",
    operator_alert_paging_policy_warning_targets=("moogsoft_incidents",),
    operator_alert_paging_policy_critical_targets=("moogsoft_incidents",),
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
    operator_reason="moogsoft_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="moogsoft",
    event_kind="remediation_started",
    actor="moogsoft",
    detail="moogsoft_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="MG-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "moogsoft-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "moogsoft": {
        "alert_id": "MG-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://moogsoft.example/alerts/MG-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 74,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "moogsoft recovery started",
        "external_run_id": "moogsoft-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "moogsoft"
  assert updated_incident.remediation.provider_recovery.moogsoft.alert_id == "MG-123"
  assert updated_incident.remediation.provider_recovery.moogsoft.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.moogsoft.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.moogsoft.priority == "high"
  assert updated_incident.remediation.provider_recovery.moogsoft.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.moogsoft.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.moogsoft.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.moogsoft.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.moogsoft.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.moogsoft.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 74
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_moogsoft_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 40, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("moogsoft_incidents",),
    supported_workflow_providers=("moogsoft",),
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
    operator_alert_paging_policy_warning_targets=("moogsoft_incidents",),
    operator_alert_paging_policy_critical_targets=("moogsoft_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("moogsoft_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("moogsoft_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="moogsoft_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "moogsoft"
  assert incident.delivery_targets == ("moogsoft_incidents",)
  assert incident.escalation_targets == ("moogsoft_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="moogsoft",
    event_kind="triggered",
    actor="moogsoft",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="MG-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "MG-123"
  assert triggered.external_provider == "moogsoft"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="moogsoft_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("moogsoft", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_spikesh_recovery_sync_populates_spikesh_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 29, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("spikesh_incidents",),
    supported_workflow_providers=("spikesh",),
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
    operator_alert_paging_policy_default_provider="spikesh",
    operator_alert_paging_policy_warning_targets=("spikesh_incidents",),
    operator_alert_paging_policy_critical_targets=("spikesh_incidents",),
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
    operator_reason="spikesh_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="spikesh",
    event_kind="remediation_started",
    actor="spikesh",
    detail="spikesh_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SPK-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "spikesh-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "spikesh": {
        "alert_id": "SPK-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://spike.example/alerts/SPK-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 76,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "spikesh recovery started",
        "external_run_id": "spikesh-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "spikesh"
  assert updated_incident.remediation.provider_recovery.spikesh.alert_id == "SPK-123"
  assert updated_incident.remediation.provider_recovery.spikesh.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.spikesh.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.spikesh.priority == "high"
  assert updated_incident.remediation.provider_recovery.spikesh.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.spikesh.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.spikesh.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.spikesh.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.spikesh.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.spikesh.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 76
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_spikesh_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 45, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("spikesh_incidents",),
    supported_workflow_providers=("spikesh",),
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
    operator_alert_paging_policy_warning_targets=("spikesh_incidents",),
    operator_alert_paging_policy_critical_targets=("spikesh_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("spikesh_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("spikesh_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="spikesh_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "spikesh"
  assert incident.delivery_targets == ("spikesh_incidents",)
  assert incident.escalation_targets == ("spikesh_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="spikesh",
    event_kind="triggered",
    actor="spikesh",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SPK-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "SPK-123"
  assert triggered.external_provider == "spikesh"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="spikesh_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("spikesh", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_dutycalls_recovery_sync_populates_dutycalls_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 34, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("dutycalls_incidents",),
    supported_workflow_providers=("dutycalls",),
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
    operator_alert_paging_policy_default_provider="dutycalls",
    operator_alert_paging_policy_warning_targets=("dutycalls_incidents",),
    operator_alert_paging_policy_critical_targets=("dutycalls_incidents",),
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
    operator_reason="dutycalls_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="dutycalls",
    event_kind="remediation_started",
    actor="dutycalls",
    detail="dutycalls_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="DC-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "dutycalls-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "dutycalls": {
        "alert_id": "DC-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://dutycalls.example/alerts/DC-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 74,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "dutycalls recovery started",
        "external_run_id": "dutycalls-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "dutycalls"
  assert updated_incident.remediation.provider_recovery.dutycalls.alert_id == "DC-123"
  assert updated_incident.remediation.provider_recovery.dutycalls.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.dutycalls.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.dutycalls.priority == "high"
  assert updated_incident.remediation.provider_recovery.dutycalls.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.dutycalls.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.dutycalls.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.dutycalls.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.dutycalls.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.dutycalls.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 74
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_dutycalls_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 47, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("dutycalls_incidents",),
    supported_workflow_providers=("dutycalls",),
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
    operator_alert_paging_policy_warning_targets=("dutycalls_incidents",),
    operator_alert_paging_policy_critical_targets=("dutycalls_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("dutycalls_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("dutycalls_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="dutycalls_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "dutycalls"
  assert incident.delivery_targets == ("dutycalls_incidents",)
  assert incident.escalation_targets == ("dutycalls_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="dutycalls",
    event_kind="triggered",
    actor="dutycalls",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="DC-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "DC-123"
  assert triggered.external_provider == "dutycalls"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="dutycalls_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("dutycalls", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_incidenthub_recovery_sync_populates_incidenthub_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 36, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("incidenthub_incidents",),
    supported_workflow_providers=("incidenthub",),
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
    operator_alert_paging_policy_default_provider="incidenthub",
    operator_alert_paging_policy_warning_targets=("incidenthub_incidents",),
    operator_alert_paging_policy_critical_targets=("incidenthub_incidents",),
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
    operator_reason="incidenthub_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="incidenthub",
    event_kind="remediation_started",
    actor="incidenthub",
    detail="incidenthub_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IH-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "incidenthub-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "incidenthub": {
        "alert_id": "IH-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://incidenthub.example/alerts/IH-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "incidenthub recovery started",
        "external_run_id": "incidenthub-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "incidenthub"
  assert updated_incident.remediation.provider_recovery.incidenthub.alert_id == "IH-123"
  assert updated_incident.remediation.provider_recovery.incidenthub.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.incidenthub.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.incidenthub.priority == "high"
  assert updated_incident.remediation.provider_recovery.incidenthub.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.incidenthub.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.incidenthub.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.incidenthub.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.incidenthub.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.incidenthub.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_incidenthub_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 49, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("incidenthub_incidents",),
    supported_workflow_providers=("incidenthub",),
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
    operator_alert_paging_policy_warning_targets=("incidenthub_incidents",),
    operator_alert_paging_policy_critical_targets=("incidenthub_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("incidenthub_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("incidenthub_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="incidenthub_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "incidenthub"
  assert incident.delivery_targets == ("incidenthub_incidents",)
  assert incident.escalation_targets == ("incidenthub_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="incidenthub",
    event_kind="triggered",
    actor="incidenthub",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IH-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "IH-123"
  assert triggered.external_provider == "incidenthub"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="incidenthub_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("incidenthub", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_opsramp_recovery_sync_populates_opsramp_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 46, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("opsramp_incidents",),
    supported_workflow_providers=("opsramp",),
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
    operator_alert_paging_policy_default_provider="opsramp",
    operator_alert_paging_policy_warning_targets=("opsramp_incidents",),
    operator_alert_paging_policy_critical_targets=("opsramp_incidents",),
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
    operator_reason="opsramp_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="opsramp",
    event_kind="remediation_started",
    actor="opsramp",
    detail="opsramp_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OR-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "opsramp-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "opsramp": {
        "alert_id": "OR-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://opsramp.example/alerts/OR-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "opsramp recovery started",
        "external_run_id": "opsramp-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "opsramp"
  assert updated_incident.remediation.provider_recovery.opsramp.alert_id == "OR-123"
  assert updated_incident.remediation.provider_recovery.opsramp.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.opsramp.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.opsramp.priority == "high"
  assert updated_incident.remediation.provider_recovery.opsramp.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.opsramp.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.opsramp.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.opsramp.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.opsramp.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.opsramp.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_external_resolver_recovery_sync_populates_resolver_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 41, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("resolver_incidents",),
    supported_workflow_providers=("resolver",),
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
    operator_alert_paging_policy_default_provider="resolver",
    operator_alert_paging_policy_warning_targets=("resolver_incidents",),
    operator_alert_paging_policy_critical_targets=("resolver_incidents",),
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
    operator_reason="resolver_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="resolver",
    event_kind="remediation_started",
    actor="resolver",
    detail="resolver_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="RV-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "resolver-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "resolver": {
        "alert_id": "RV-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://resolver.example/alerts/RV-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "resolver recovery started",
        "external_run_id": "resolver-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "resolver"
  assert updated_incident.remediation.provider_recovery.resolver.alert_id == "RV-123"
  assert updated_incident.remediation.provider_recovery.resolver.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.resolver.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.resolver.priority == "high"
  assert updated_incident.remediation.provider_recovery.resolver.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.resolver.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.resolver.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.resolver.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.resolver.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.resolver.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_resolver_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 54, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("resolver_incidents",),
    supported_workflow_providers=("resolver",),
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
    operator_alert_paging_policy_warning_targets=("resolver_incidents",),
    operator_alert_paging_policy_critical_targets=("resolver_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("resolver_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("resolver_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="resolver_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "resolver"
  assert incident.delivery_targets == ("resolver_incidents",)
  assert incident.escalation_targets == ("resolver_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="resolver",
    event_kind="triggered",
    actor="resolver",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="RV-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "RV-123"
  assert triggered.external_provider == "resolver"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="resolver_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("resolver", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_openduty_recovery_sync_populates_openduty_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 43, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("openduty_incidents",),
    supported_workflow_providers=("openduty",),
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
    operator_alert_paging_policy_default_provider="openduty",
    operator_alert_paging_policy_warning_targets=("openduty_incidents",),
    operator_alert_paging_policy_critical_targets=("openduty_incidents",),
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
    operator_reason="openduty_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="openduty",
    event_kind="remediation_started",
    actor="openduty",
    detail="openduty_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OD-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "openduty-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "openduty": {
        "alert_id": "OD-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://openduty.example/alerts/OD-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "openduty recovery started",
        "external_run_id": "openduty-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "openduty"
  assert updated_incident.remediation.provider_recovery.openduty.alert_id == "OD-123"
  assert updated_incident.remediation.provider_recovery.openduty.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.openduty.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.openduty.priority == "high"
  assert updated_incident.remediation.provider_recovery.openduty.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.openduty.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.openduty.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.openduty.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.openduty.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.openduty.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_openduty_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 56, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("openduty_incidents",),
    supported_workflow_providers=("openduty",),
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
    operator_alert_paging_policy_warning_targets=("openduty_incidents",),
    operator_alert_paging_policy_critical_targets=("openduty_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("openduty_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("openduty_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="openduty_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "openduty"
  assert incident.delivery_targets == ("openduty_incidents",)
  assert incident.escalation_targets == ("openduty_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="openduty",
    event_kind="triggered",
    actor="openduty",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OD-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "OD-123"
  assert triggered.external_provider == "openduty"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="openduty_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("openduty", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_cabot_recovery_sync_populates_cabot_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 12, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("cabot_incidents",),
    supported_workflow_providers=("cabot",),
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
    operator_alert_paging_policy_default_provider="cabot",
    operator_alert_paging_policy_warning_targets=("cabot_incidents",),
    operator_alert_paging_policy_critical_targets=("cabot_incidents",),
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
    operator_reason="cabot_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="cabot",
    event_kind="remediation_started",
    actor="cabot",
    detail="cabot_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="CB-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "cabot-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "cabot": {
        "alert_id": "CB-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://cabot.example/alerts/CB-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 81,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "cabot recovery started",
        "external_run_id": "cabot-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "cabot"
  assert updated_incident.remediation.provider_recovery.cabot.alert_id == "CB-123"
  assert updated_incident.remediation.provider_recovery.cabot.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.cabot.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.cabot.priority == "high"
  assert updated_incident.remediation.provider_recovery.cabot.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.cabot.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.cabot.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.cabot.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.cabot.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.cabot.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 81
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_cabot_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 8, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("cabot_incidents",),
    supported_workflow_providers=("cabot",),
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
    operator_alert_paging_policy_warning_targets=("cabot_incidents",),
    operator_alert_paging_policy_critical_targets=("cabot_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("cabot_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("cabot_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="cabot_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "cabot"
  assert incident.delivery_targets == ("cabot_incidents",)
  assert incident.escalation_targets == ("cabot_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="cabot",
    event_kind="triggered",
    actor="cabot",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="CB-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "CB-123"
  assert triggered.external_provider == "cabot"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="cabot_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("cabot", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_haloitsm_recovery_sync_populates_haloitsm_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 31, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("haloitsm_incidents",),
    supported_workflow_providers=("haloitsm",),
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
    operator_alert_paging_policy_default_provider="haloitsm",
    operator_alert_paging_policy_warning_targets=("haloitsm_incidents",),
    operator_alert_paging_policy_critical_targets=("haloitsm_incidents",),
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
    operator_reason="haloitsm_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="haloitsm",
    event_kind="remediation_started",
    actor="haloitsm",
    detail="haloitsm_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="HI-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "haloitsm-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "haloitsm": {
        "alert_id": "HI-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://haloitsm.example/alerts/HI-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 83,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "haloitsm recovery started",
        "external_run_id": "haloitsm-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "haloitsm"
  assert updated_incident.remediation.provider_recovery.haloitsm.alert_id == "HI-123"
  assert updated_incident.remediation.provider_recovery.haloitsm.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.haloitsm.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.haloitsm.priority == "high"
  assert updated_incident.remediation.provider_recovery.haloitsm.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.haloitsm.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.haloitsm.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.haloitsm.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.haloitsm.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.haloitsm.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 83
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_haloitsm_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 24, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("haloitsm_incidents",),
    supported_workflow_providers=("haloitsm",),
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
    operator_alert_paging_policy_warning_targets=("haloitsm_incidents",),
    operator_alert_paging_policy_critical_targets=("haloitsm_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("haloitsm_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("haloitsm_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="haloitsm_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "haloitsm"
  assert incident.delivery_targets == ("haloitsm_incidents",)
  assert incident.escalation_targets == ("haloitsm_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="haloitsm",
    event_kind="triggered",
    actor="haloitsm",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="HI-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "HI-123"
  assert triggered.external_provider == "haloitsm"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="haloitsm_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("haloitsm", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_incidentmanagerio_recovery_sync_populates_incidentmanagerio_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 49, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("incidentmanagerio_incidents",),
    supported_workflow_providers=("incidentmanagerio",),
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
    operator_alert_paging_policy_default_provider="incidentmanagerio",
    operator_alert_paging_policy_warning_targets=("incidentmanagerio_incidents",),
    operator_alert_paging_policy_critical_targets=("incidentmanagerio_incidents",),
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
    operator_reason="incidentmanagerio_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="incidentmanagerio",
    event_kind="remediation_started",
    actor="incidentmanagerio",
    detail="incidentmanagerio_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IM-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "incidentmanagerio-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "incidentmanagerio": {
        "alert_id": "IM-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://incidentmanagerio.example/alerts/IM-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 81,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "incidentmanagerio recovery started",
        "external_run_id": "incidentmanagerio-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "incidentmanagerio"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.alert_id == "IM-123"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.priority == "high"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.incidentmanagerio.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 81
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_incidentmanagerio_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 41, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("incidentmanagerio_incidents",),
    supported_workflow_providers=("incidentmanagerio",),
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
    operator_alert_paging_policy_warning_targets=("incidentmanagerio_incidents",),
    operator_alert_paging_policy_critical_targets=("incidentmanagerio_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("incidentmanagerio_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("incidentmanagerio_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="incidentmanagerio_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "incidentmanagerio"
  assert incident.delivery_targets == ("incidentmanagerio_incidents",)
  assert incident.escalation_targets == ("incidentmanagerio_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="incidentmanagerio",
    event_kind="triggered",
    actor="incidentmanagerio",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IM-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "IM-123"
  assert triggered.external_provider == "incidentmanagerio"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="incidentmanagerio_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("incidentmanagerio", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_oneuptime_recovery_sync_populates_oneuptime_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 57, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("oneuptime_incidents",),
    supported_workflow_providers=("oneuptime",),
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
    operator_alert_paging_policy_default_provider="oneuptime",
    operator_alert_paging_policy_warning_targets=("oneuptime_incidents",),
    operator_alert_paging_policy_critical_targets=("oneuptime_incidents",),
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
    operator_reason="oneuptime_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="oneuptime",
    event_kind="remediation_started",
    actor="oneuptime",
    detail="oneuptime_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OU-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "oneuptime-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "oneuptime": {
        "alert_id": "OU-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://oneuptime.example/alerts/OU-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "oneuptime recovery started",
        "external_run_id": "oneuptime-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "oneuptime"
  assert updated_incident.remediation.provider_recovery.oneuptime.alert_id == "OU-123"
  assert updated_incident.remediation.provider_recovery.oneuptime.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.oneuptime.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.oneuptime.priority == "high"
  assert updated_incident.remediation.provider_recovery.oneuptime.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.oneuptime.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.oneuptime.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.oneuptime.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.oneuptime.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.oneuptime.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_oneuptime_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 52, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("oneuptime_incidents",),
    supported_workflow_providers=("oneuptime",),
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
    operator_alert_paging_policy_warning_targets=("oneuptime_incidents",),
    operator_alert_paging_policy_critical_targets=("oneuptime_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("oneuptime_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("oneuptime_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="oneuptime_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "oneuptime"
  assert incident.delivery_targets == ("oneuptime_incidents",)
  assert incident.escalation_targets == ("oneuptime_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="oneuptime",
    event_kind="triggered",
    actor="oneuptime",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OU-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "OU-123"
  assert triggered.external_provider == "oneuptime"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="oneuptime_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("oneuptime", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_squzy_recovery_sync_populates_squzy_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 57, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("squzy_incidents",),
    supported_workflow_providers=("squzy",),
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
    operator_alert_paging_policy_default_provider="squzy",
    operator_alert_paging_policy_warning_targets=("squzy_incidents",),
    operator_alert_paging_policy_critical_targets=("squzy_incidents",),
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
    operator_reason="squzy_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="squzy",
    event_kind="remediation_started",
    actor="squzy",
    detail="squzy_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SQ-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "squzy-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "squzy": {
        "alert_id": "SQ-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://squzy.example/alerts/SQ-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "squzy recovery started",
        "external_run_id": "squzy-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "squzy"
  assert updated_incident.remediation.provider_recovery.squzy.alert_id == "SQ-123"
  assert updated_incident.remediation.provider_recovery.squzy.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.squzy.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.squzy.priority == "high"
  assert updated_incident.remediation.provider_recovery.squzy.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.squzy.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.squzy.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.squzy.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.squzy.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.squzy.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_squzy_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 52, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("squzy_incidents",),
    supported_workflow_providers=("squzy",),
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
    operator_alert_paging_policy_warning_targets=("squzy_incidents",),
    operator_alert_paging_policy_critical_targets=("squzy_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("squzy_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("squzy_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="squzy_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "squzy"
  assert incident.delivery_targets == ("squzy_incidents",)
  assert incident.escalation_targets == ("squzy_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="squzy",
    event_kind="triggered",
    actor="squzy",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SQ-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "SQ-123"
  assert triggered.external_provider == "squzy"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="squzy_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("squzy", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_crisescontrol_recovery_sync_populates_crisescontrol_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 57, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("crisescontrol_incidents",),
    supported_workflow_providers=("crisescontrol",),
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
    operator_alert_paging_policy_default_provider="crisescontrol",
    operator_alert_paging_policy_warning_targets=("crisescontrol_incidents",),
    operator_alert_paging_policy_critical_targets=("crisescontrol_incidents",),
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
    operator_reason="crisescontrol_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="crisescontrol",
    event_kind="remediation_started",
    actor="crisescontrol",
    detail="crisescontrol_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="CC-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "crisescontrol-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "crisescontrol": {
        "alert_id": "CC-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://crisescontrol.example/alerts/CC-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "crisescontrol recovery started",
        "external_run_id": "crisescontrol-telemetry-1",
      },
    },
  )

  updated_incident = next(
    event
    for event in synced.incident_events
    if event.event_id == incident.event_id
  )
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "crisescontrol"
  assert updated_incident.remediation.provider_recovery.crisescontrol.alert_id == "CC-123"
  assert updated_incident.remediation.provider_recovery.crisescontrol.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.crisescontrol.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.crisescontrol.priority == "high"
  assert updated_incident.remediation.provider_recovery.crisescontrol.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.crisescontrol.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.crisescontrol.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.crisescontrol.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.crisescontrol.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.crisescontrol.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_crisescontrol_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 52, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("crisescontrol_incidents",),
    supported_workflow_providers=("crisescontrol",),
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
    operator_alert_paging_policy_warning_targets=("crisescontrol_incidents",),
    operator_alert_paging_policy_critical_targets=("crisescontrol_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("crisescontrol_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("crisescontrol_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="crisescontrol_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "crisescontrol"
  assert incident.delivery_targets == ("crisescontrol_incidents",)
  assert incident.escalation_targets == ("crisescontrol_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="crisescontrol",
    event_kind="triggered",
    actor="crisescontrol",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="CC-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "CC-123"
  assert triggered.external_provider == "crisescontrol"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="crisescontrol_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("crisescontrol", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_freshservice_recovery_sync_populates_freshservice_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 57, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("freshservice_incidents",),
    supported_workflow_providers=("freshservice",),
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
    operator_alert_paging_policy_default_provider="freshservice",
    operator_alert_paging_policy_warning_targets=("freshservice_incidents",),
    operator_alert_paging_policy_critical_targets=("freshservice_incidents",),
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
    operator_reason="freshservice_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="freshservice",
    event_kind="remediation_started",
    actor="freshservice",
    detail="freshservice_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="FS-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "freshservice-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "freshservice": {
        "alert_id": "FS-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://freshservice.example/alerts/FS-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "freshservice recovery started",
        "external_run_id": "freshservice-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "freshservice"
  assert updated_incident.remediation.provider_recovery.freshservice.alert_id == "FS-123"
  assert updated_incident.remediation.provider_recovery.freshservice.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.freshservice.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.freshservice.priority == "high"
  assert updated_incident.remediation.provider_recovery.freshservice.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.freshservice.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.freshservice.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.freshservice.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.freshservice.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.freshservice.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_freshservice_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 52, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("freshservice_incidents",),
    supported_workflow_providers=("freshservice",),
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
    operator_alert_paging_policy_warning_targets=("freshservice_incidents",),
    operator_alert_paging_policy_critical_targets=("freshservice_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("freshservice_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("freshservice_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="freshservice_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "freshservice"
  assert incident.delivery_targets == ("freshservice_incidents",)
  assert incident.escalation_targets == ("freshservice_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="freshservice",
    event_kind="triggered",
    actor="freshservice",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="FS-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "FS-123"
  assert triggered.external_provider == "freshservice"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="freshservice_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("freshservice", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_freshdesk_recovery_sync_populates_freshdesk_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 59, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("freshdesk_incidents",),
    supported_workflow_providers=("freshdesk",),
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
    operator_alert_paging_policy_default_provider="freshdesk",
    operator_alert_paging_policy_warning_targets=("freshdesk_incidents",),
    operator_alert_paging_policy_critical_targets=("freshdesk_incidents",),
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
    operator_reason="freshdesk_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="freshdesk",
    event_kind="remediation_started",
    actor="freshdesk",
    detail="freshdesk_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="FD-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "freshdesk-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "freshdesk": {
        "alert_id": "FD-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://freshdesk.example/tickets/FD-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 81,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "freshdesk recovery started",
        "external_run_id": "freshdesk-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "freshdesk"
  assert updated_incident.remediation.provider_recovery.freshdesk.alert_id == "FD-123"
  assert updated_incident.remediation.provider_recovery.freshdesk.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.freshdesk.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.freshdesk.priority == "high"
  assert updated_incident.remediation.provider_recovery.freshdesk.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.freshdesk.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.freshdesk.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.freshdesk.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.freshdesk.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.freshdesk.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 81
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_freshdesk_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 54, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("freshdesk_incidents",),
    supported_workflow_providers=("freshdesk",),
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
    operator_alert_paging_policy_warning_targets=("freshdesk_incidents",),
    operator_alert_paging_policy_critical_targets=("freshdesk_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("freshdesk_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("freshdesk_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="freshdesk_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "freshdesk"
  assert incident.delivery_targets == ("freshdesk_incidents",)
  assert incident.escalation_targets == ("freshdesk_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="freshdesk",
    event_kind="triggered",
    actor="freshdesk",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="FD-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "FD-456"
  assert triggered.external_provider == "freshdesk"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="freshdesk_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("freshdesk", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_happyfox_recovery_sync_populates_happyfox_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 12, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("happyfox_incidents",),
    supported_workflow_providers=("happyfox",),
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
    operator_alert_paging_policy_default_provider="happyfox",
    operator_alert_paging_policy_warning_targets=("happyfox_incidents",),
    operator_alert_paging_policy_critical_targets=("happyfox_incidents",),
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
    operator_reason="happyfox_market_data_recovery_sync",
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
        )
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )

  updated = app.sync_guarded_live_incident_from_external(
    provider="happyfox",
    event_kind="remediation_started",
    actor="happyfox",
    detail="happyfox_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference="guarded-live:market-data:5m",
    workflow_reference="HF-123",
    occurred_at=clock.current + timedelta(seconds=30),
    payload={
      "job_id": "happyfox-job-11",
      "channels": ["kline", "depth"],
      "symbols": ["ETH/USDT"],
      "timeframe": "5m",
      "happyfox": {
        "alert_id": "HF-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://happyfox.example/tickets/HF-123",
      },
      "telemetry": {
        "source": "provider_payload",
        "state": "running",
        "progress_percent": 81,
        "attempt_count": 2,
        "current_step": "verify_repaired_window",
      },
    },
  )
  updated_incident = next(event for event in updated.incident_events if event.event_id == incident.event_id)

  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "happyfox"
  assert updated_incident.remediation.provider_recovery.happyfox.alert_id == "HF-123"
  assert updated_incident.remediation.provider_recovery.happyfox.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.happyfox.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.happyfox.priority == "high"
  assert updated_incident.remediation.provider_recovery.happyfox.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.happyfox.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.happyfox.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.happyfox.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.happyfox.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.happyfox.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 81
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_happyfox_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 58, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("happyfox_incidents",),
    supported_workflow_providers=("happyfox",),
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
    operator_alert_paging_policy_warning_targets=("happyfox_incidents",),
    operator_alert_paging_policy_critical_targets=("happyfox_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("happyfox_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("happyfox_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="happyfox_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "happyfox"
  assert incident.delivery_targets == ("happyfox_incidents",)
  assert incident.escalation_targets == ("happyfox_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="happyfox",
    event_kind="triggered",
    actor="happyfox",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="HF-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "HF-456"
  assert triggered.external_provider == "happyfox"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="happyfox_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("happyfox", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_zendesk_recovery_sync_populates_zendesk_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 22, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("zendesk_incidents",),
    supported_workflow_providers=("zendesk",),
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
    operator_alert_paging_policy_default_provider="zendesk",
    operator_alert_paging_policy_warning_targets=("zendesk_incidents",),
    operator_alert_paging_policy_critical_targets=("zendesk_incidents",),
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
    operator_reason="zendesk_market_data_recovery_sync",
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
        )
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )

  updated = app.sync_guarded_live_incident_from_external(
    provider="zendesk",
    event_kind="remediation_started",
    actor="zendesk",
    detail="zendesk_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference="guarded-live:market-data:5m",
    workflow_reference="ZD-123",
    occurred_at=clock.current + timedelta(seconds=30),
    payload={
      "job_id": "zendesk-job-11",
      "channels": ["kline", "depth"],
      "symbols": ["ETH/USDT"],
      "timeframe": "5m",
      "zendesk": {
        "alert_id": "ZD-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://zendesk.example/tickets/ZD-123",
      },
      "telemetry": {
        "source": "provider_payload",
        "state": "running",
        "progress_percent": 81,
        "attempt_count": 2,
        "current_step": "verify_repaired_window",
      },
    },
  )
  updated_incident = next(event for event in updated.incident_events if event.event_id == incident.event_id)

  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "zendesk"
  assert updated_incident.remediation.provider_recovery.zendesk.alert_id == "ZD-123"
  assert updated_incident.remediation.provider_recovery.zendesk.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.zendesk.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.zendesk.priority == "high"
  assert updated_incident.remediation.provider_recovery.zendesk.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.zendesk.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.zendesk.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.zendesk.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.zendesk.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.zendesk.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 81
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_zendesk_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 8, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("zendesk_incidents",),
    supported_workflow_providers=("zendesk",),
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
    operator_alert_paging_policy_warning_targets=("zendesk_incidents",),
    operator_alert_paging_policy_critical_targets=("zendesk_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("zendesk_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("zendesk_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="zendesk_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "zendesk"
  assert incident.delivery_targets == ("zendesk_incidents",)
  assert incident.escalation_targets == ("zendesk_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="zendesk",
    event_kind="triggered",
    actor="zendesk",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="ZD-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "ZD-456"
  assert triggered.external_provider == "zendesk"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="zendesk_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("zendesk", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_zohodesk_recovery_sync_populates_zohodesk_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 23, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("zohodesk_incidents",),
    supported_workflow_providers=("zohodesk",),
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
    operator_alert_paging_policy_default_provider="zohodesk",
    operator_alert_paging_policy_warning_targets=("zohodesk_incidents",),
    operator_alert_paging_policy_critical_targets=("zohodesk_incidents",),
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
    operator_reason="zohodesk_market_data_recovery_sync",
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
        )
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )

  updated = app.sync_guarded_live_incident_from_external(
    provider="zohodesk",
    event_kind="remediation_started",
    actor="zohodesk",
    detail="zohodesk_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference="guarded-live:market-data:5m",
    workflow_reference="ZD-223",
    occurred_at=clock.current + timedelta(seconds=30),
    payload={
      "job_id": "zohodesk-job-11",
      "channels": ["kline", "depth"],
      "symbols": ["ETH/USDT"],
      "timeframe": "5m",
      "zohodesk": {
        "alert_id": "ZHD-223",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://desk.zoho.example/tickets/ZHD-223",
      },
      "telemetry": {
        "source": "provider_payload",
        "state": "running",
        "progress_percent": 82,
        "attempt_count": 2,
        "current_step": "verify_repaired_window",
      },
    },
  )
  updated_incident = next(event for event in updated.incident_events if event.event_id == incident.event_id)

  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "zohodesk"
  assert updated_incident.remediation.provider_recovery.zohodesk.alert_id == "ZHD-223"
  assert updated_incident.remediation.provider_recovery.zohodesk.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.zohodesk.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.zohodesk.priority == "high"
  assert updated_incident.remediation.provider_recovery.zohodesk.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.zohodesk.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.zohodesk.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.zohodesk.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.zohodesk.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.zohodesk.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 82
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_zohodesk_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 9, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("zohodesk_incidents",),
    supported_workflow_providers=("zohodesk",),
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
    operator_alert_paging_policy_warning_targets=("zohodesk_incidents",),
    operator_alert_paging_policy_critical_targets=("zohodesk_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("zohodesk_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("zohodesk_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="zohodesk_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "zohodesk"
  assert incident.delivery_targets == ("zohodesk_incidents",)
  assert incident.escalation_targets == ("zohodesk_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="zohodesk",
    event_kind="triggered",
    actor="zohodesk",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="ZHD-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "ZHD-456"
  assert triggered.external_provider == "zohodesk"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="zohodesk_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("zohodesk", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_helpscout_recovery_sync_populates_helpscout_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 31, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("helpscout_incidents",),
    supported_workflow_providers=("helpscout",),
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
    operator_alert_paging_policy_default_provider="helpscout",
    operator_alert_paging_policy_warning_targets=("helpscout_incidents",),
    operator_alert_paging_policy_critical_targets=("helpscout_incidents",),
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
    operator_reason="helpscout_market_data_recovery_sync",
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
        )
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )

  updated = app.sync_guarded_live_incident_from_external(
    provider="helpscout",
    event_kind="remediation_started",
    actor="helpscout",
    detail="helpscout_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference="guarded-live:market-data:5m",
    workflow_reference="HS-223",
    occurred_at=clock.current + timedelta(seconds=30),
    payload={
      "job_id": "helpscout-job-11",
      "channels": ["kline", "depth"],
      "symbols": ["ETH/USDT"],
      "timeframe": "5m",
      "helpscout": {
        "alert_id": "HS-223",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://api.helpscout.example/conversations/HS-223",
      },
      "telemetry": {
        "source": "provider_payload",
        "state": "running",
        "progress_percent": 83,
        "attempt_count": 2,
        "current_step": "verify_repaired_window",
      },
    },
  )
  updated_incident = next(event for event in updated.incident_events if event.event_id == incident.event_id)

  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "helpscout"
  assert updated_incident.remediation.provider_recovery.helpscout.alert_id == "HS-223"
  assert updated_incident.remediation.provider_recovery.helpscout.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.helpscout.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.helpscout.priority == "high"
  assert updated_incident.remediation.provider_recovery.helpscout.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.helpscout.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.helpscout.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.helpscout.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.helpscout.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.helpscout.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 83
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_helpscout_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 17, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("helpscout_incidents",),
    supported_workflow_providers=("helpscout",),
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
    operator_alert_paging_policy_warning_targets=("helpscout_incidents",),
    operator_alert_paging_policy_critical_targets=("helpscout_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("helpscout_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("helpscout_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="helpscout_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "helpscout"
  assert incident.delivery_targets == ("helpscout_incidents",)
  assert incident.escalation_targets == ("helpscout_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="helpscout",
    event_kind="triggered",
    actor="helpscout",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="HS-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "HS-456"
  assert triggered.external_provider == "helpscout"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="helpscout_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("helpscout", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_kayako_recovery_sync_populates_kayako_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 31, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("kayako_incidents",),
    supported_workflow_providers=("kayako",),
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
    operator_alert_paging_policy_default_provider="kayako",
    operator_alert_paging_policy_warning_targets=("kayako_incidents",),
    operator_alert_paging_policy_critical_targets=("kayako_incidents",),
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
    operator_reason="kayako_market_data_recovery_sync",
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
        )
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )

  updated = app.sync_guarded_live_incident_from_external(
    provider="kayako",
    event_kind="remediation_started",
    actor="kayako",
    detail="kayako_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference="guarded-live:market-data:5m",
    workflow_reference="KY-223",
    occurred_at=clock.current + timedelta(seconds=30),
    payload={
      "job_id": "kayako-job-11",
      "channels": ["kline", "depth"],
      "symbols": ["ETH/USDT"],
      "timeframe": "5m",
      "kayako": {
        "alert_id": "KY-223",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://api.kayako.example/cases/KY-223",
      },
      "telemetry": {
        "source": "provider_payload",
        "state": "running",
        "progress_percent": 83,
        "attempt_count": 2,
        "current_step": "verify_repaired_window",
      },
    },
  )
  updated_incident = next(event for event in updated.incident_events if event.event_id == incident.event_id)

  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "kayako"
  assert updated_incident.remediation.provider_recovery.kayako.alert_id == "KY-223"
  assert updated_incident.remediation.provider_recovery.kayako.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.kayako.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.kayako.priority == "high"
  assert updated_incident.remediation.provider_recovery.kayako.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.kayako.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.kayako.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.kayako.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.kayako.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.kayako.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 83
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_kayako_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 17, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("kayako_incidents",),
    supported_workflow_providers=("kayako",),
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
    operator_alert_paging_policy_warning_targets=("kayako_incidents",),
    operator_alert_paging_policy_critical_targets=("kayako_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("kayako_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("kayako_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="kayako_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "kayako"
  assert incident.delivery_targets == ("kayako_incidents",)
  assert incident.escalation_targets == ("kayako_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="kayako",
    event_kind="triggered",
    actor="kayako",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="KY-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "KY-456"
  assert triggered.external_provider == "kayako"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="kayako_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("kayako", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_intercom_recovery_sync_populates_intercom_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 31, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("intercom_incidents",),
    supported_workflow_providers=("intercom",),
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
    operator_alert_paging_policy_default_provider="intercom",
    operator_alert_paging_policy_warning_targets=("intercom_incidents",),
    operator_alert_paging_policy_critical_targets=("intercom_incidents",),
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
    operator_reason="intercom_market_data_recovery_sync",
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
        )
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )

  updated = app.sync_guarded_live_incident_from_external(
    provider="intercom",
    event_kind="remediation_started",
    actor="intercom",
    detail="intercom_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference="guarded-live:market-data:5m",
    workflow_reference="IC-223",
    occurred_at=clock.current + timedelta(seconds=30),
    payload={
      "job_id": "intercom-job-11",
      "channels": ["kline", "depth"],
      "symbols": ["ETH/USDT"],
      "timeframe": "5m",
      "intercom": {
        "alert_id": "IC-223",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://api.intercom.example/conversations/IC-223",
      },
      "telemetry": {
        "source": "provider_payload",
        "state": "running",
        "progress_percent": 83,
        "attempt_count": 2,
        "current_step": "verify_repaired_window",
      },
    },
  )
  updated_incident = next(event for event in updated.incident_events if event.event_id == incident.event_id)

  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "intercom"
  assert updated_incident.remediation.provider_recovery.intercom.alert_id == "IC-223"
  assert updated_incident.remediation.provider_recovery.intercom.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.intercom.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.intercom.priority == "high"
  assert updated_incident.remediation.provider_recovery.intercom.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.intercom.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.intercom.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.intercom.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.intercom.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.intercom.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 83
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_intercom_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 17, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("intercom_incidents",),
    supported_workflow_providers=("intercom",),
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
    operator_alert_paging_policy_warning_targets=("intercom_incidents",),
    operator_alert_paging_policy_critical_targets=("intercom_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("intercom_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("intercom_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="intercom_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "intercom"
  assert incident.delivery_targets == ("intercom_incidents",)
  assert incident.escalation_targets == ("intercom_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="intercom",
    event_kind="triggered",
    actor="intercom",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IC-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "IC-456"
  assert triggered.external_provider == "intercom"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="intercom_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("intercom", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_front_recovery_sync_populates_front_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 31, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("front_incidents",),
    supported_workflow_providers=("front",),
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
    operator_alert_paging_policy_default_provider="front",
    operator_alert_paging_policy_warning_targets=("front_incidents",),
    operator_alert_paging_policy_critical_targets=("front_incidents",),
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
    operator_reason="front_market_data_recovery_sync",
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
        )
      ],
    ),
  )

  opened = app.get_guarded_live_status()
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:market-data:5m"
  )

  updated = app.sync_guarded_live_incident_from_external(
    provider="front",
    event_kind="remediation_started",
    actor="front",
    detail="front_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference="guarded-live:market-data:5m",
    workflow_reference="FR-223",
    occurred_at=clock.current + timedelta(seconds=30),
    payload={
      "job_id": "front-job-11",
      "channels": ["kline", "depth"],
      "symbols": ["ETH/USDT"],
      "timeframe": "5m",
      "front": {
        "alert_id": "FR-223",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://api.front.example/conversations/FR-223",
      },
      "telemetry": {
        "source": "provider_payload",
        "state": "running",
        "progress_percent": 83,
        "attempt_count": 2,
        "current_step": "verify_repaired_window",
      },
    },
  )
  updated_incident = next(event for event in updated.incident_events if event.event_id == incident.event_id)

  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "front"
  assert updated_incident.remediation.provider_recovery.front.alert_id == "FR-223"
  assert updated_incident.remediation.provider_recovery.front.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.front.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.front.priority == "high"
  assert updated_incident.remediation.provider_recovery.front.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.front.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.front.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.front.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.front.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.front.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 83
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_front_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 17, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("front_incidents",),
    supported_workflow_providers=("front",),
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
    operator_alert_paging_policy_warning_targets=("front_incidents",),
    operator_alert_paging_policy_critical_targets=("front_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("front_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("front_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="front_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "front"
  assert incident.delivery_targets == ("front_incidents",)
  assert incident.escalation_targets == ("front_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="front",
    event_kind="triggered",
    actor="front",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="FR-456",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "FR-456"
  assert triggered.external_provider == "front"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="front_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("front", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_servicedeskplus_recovery_sync_populates_servicedeskplus_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 58, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("servicedeskplus_incidents",),
    supported_workflow_providers=("servicedeskplus",),
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
    operator_alert_paging_policy_default_provider="servicedeskplus",
    operator_alert_paging_policy_warning_targets=("servicedeskplus_incidents",),
    operator_alert_paging_policy_critical_targets=("servicedeskplus_incidents",),
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
    operator_reason="servicedeskplus_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="servicedeskplus",
    event_kind="remediation_started",
    actor="servicedeskplus",
    detail="servicedeskplus_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SDP-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "servicedeskplus-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "servicedeskplus": {
        "alert_id": "SDP-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://servicedeskplus.example/alerts/SDP-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 79,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "servicedeskplus recovery started",
        "external_run_id": "servicedeskplus-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "servicedeskplus"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.alert_id == "SDP-123"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.priority == "high"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.servicedeskplus.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 79
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_servicedeskplus_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 17, 53, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("servicedeskplus_incidents",),
    supported_workflow_providers=("servicedeskplus",),
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
    operator_alert_paging_policy_warning_targets=("servicedeskplus_incidents",),
    operator_alert_paging_policy_critical_targets=("servicedeskplus_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("servicedeskplus_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("servicedeskplus_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="servicedeskplus_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "servicedeskplus"
  assert incident.delivery_targets == ("servicedeskplus_incidents",)
  assert incident.escalation_targets == ("servicedeskplus_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="servicedeskplus",
    event_kind="triggered",
    actor="servicedeskplus",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SDP-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "SDP-123"
  assert triggered.external_provider == "servicedeskplus"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="servicedeskplus_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("servicedeskplus", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_sysaid_recovery_sync_populates_sysaid_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 8, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("sysaid_incidents",),
    supported_workflow_providers=("sysaid",),
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
    operator_alert_paging_policy_default_provider="sysaid",
    operator_alert_paging_policy_warning_targets=("sysaid_incidents",),
    operator_alert_paging_policy_critical_targets=("sysaid_incidents",),
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
    operator_reason="sysaid_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="sysaid",
    event_kind="remediation_started",
    actor="sysaid",
    detail="sysaid_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SYSAID-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "sysaid-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "sysaid": {
        "alert_id": "SYSAID-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://sysaid.example/alerts/SYSAID-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 81,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "sysaid recovery started",
        "external_run_id": "sysaid-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "sysaid"
  assert updated_incident.remediation.provider_recovery.sysaid.alert_id == "SYSAID-123"
  assert updated_incident.remediation.provider_recovery.sysaid.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.sysaid.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.sysaid.priority == "high"
  assert updated_incident.remediation.provider_recovery.sysaid.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.sysaid.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.sysaid.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.sysaid.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.sysaid.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.sysaid.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 81
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_sysaid_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 3, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("sysaid_incidents",),
    supported_workflow_providers=("sysaid",),
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
    operator_alert_paging_policy_warning_targets=("sysaid_incidents",),
    operator_alert_paging_policy_critical_targets=("sysaid_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("sysaid_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("sysaid_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="sysaid_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "sysaid"
  assert incident.delivery_targets == ("sysaid_incidents",)
  assert incident.escalation_targets == ("sysaid_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="sysaid",
    event_kind="triggered",
    actor="sysaid",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SYSAID-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "SYSAID-123"
  assert triggered.external_provider == "sysaid"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="sysaid_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("sysaid", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_bmchelix_recovery_sync_populates_bmchelix_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 18, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("bmchelix_incidents",),
    supported_workflow_providers=("bmchelix",),
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
    operator_alert_paging_policy_default_provider="bmchelix",
    operator_alert_paging_policy_warning_targets=("bmchelix_incidents",),
    operator_alert_paging_policy_critical_targets=("bmchelix_incidents",),
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
    operator_reason="bmchelix_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="bmchelix",
    event_kind="remediation_started",
    actor="bmchelix",
    detail="bmchelix_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BMC-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "bmchelix-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "bmchelix": {
        "alert_id": "BMC-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://bmchelix.example/alerts/BMC-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 82,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "bmchelix recovery started",
        "external_run_id": "bmchelix-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "bmchelix"
  assert updated_incident.remediation.provider_recovery.bmchelix.alert_id == "BMC-123"
  assert updated_incident.remediation.provider_recovery.bmchelix.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.bmchelix.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.bmchelix.priority == "high"
  assert updated_incident.remediation.provider_recovery.bmchelix.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.bmchelix.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.bmchelix.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.bmchelix.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.bmchelix.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.bmchelix.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 82
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_bmchelix_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 13, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("bmchelix_incidents",),
    supported_workflow_providers=("bmchelix",),
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
    operator_alert_paging_policy_warning_targets=("bmchelix_incidents",),
    operator_alert_paging_policy_critical_targets=("bmchelix_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("bmchelix_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("bmchelix_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="bmchelix_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "bmchelix"
  assert incident.delivery_targets == ("bmchelix_incidents",)
  assert incident.escalation_targets == ("bmchelix_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="bmchelix",
    event_kind="triggered",
    actor="bmchelix",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="BMC-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "BMC-123"
  assert triggered.external_provider == "bmchelix"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="bmchelix_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("bmchelix", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_solarwindsservicedesk_recovery_sync_populates_solarwindsservicedesk_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 24, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("solarwindsservicedesk_incidents",),
    supported_workflow_providers=("solarwindsservicedesk",),
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
    operator_alert_paging_policy_default_provider="solarwindsservicedesk",
    operator_alert_paging_policy_warning_targets=("solarwindsservicedesk_incidents",),
    operator_alert_paging_policy_critical_targets=("solarwindsservicedesk_incidents",),
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
    operator_reason="solarwindsservicedesk_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="solarwindsservicedesk",
    event_kind="remediation_started",
    actor="solarwindsservicedesk",
    detail="solarwindsservicedesk_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SWSD-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "solarwindsservicedesk-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "solarwindsservicedesk": {
        "alert_id": "SWSD-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://solarwindsservicedesk.example/alerts/SWSD-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 82,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "solarwindsservicedesk recovery started",
        "external_run_id": "solarwindsservicedesk-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "solarwindsservicedesk"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.alert_id == "SWSD-123"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.priority == "high"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.solarwindsservicedesk.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 82
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_solarwindsservicedesk_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 19, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("solarwindsservicedesk_incidents",),
    supported_workflow_providers=("solarwindsservicedesk",),
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
    operator_alert_paging_policy_warning_targets=("solarwindsservicedesk_incidents",),
    operator_alert_paging_policy_critical_targets=("solarwindsservicedesk_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("solarwindsservicedesk_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("solarwindsservicedesk_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="solarwindsservicedesk_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "solarwindsservicedesk"
  assert incident.delivery_targets == ("solarwindsservicedesk_incidents",)
  assert incident.escalation_targets == ("solarwindsservicedesk_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="solarwindsservicedesk",
    event_kind="triggered",
    actor="solarwindsservicedesk",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="SWSD-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "SWSD-123"
  assert triggered.external_provider == "solarwindsservicedesk"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="solarwindsservicedesk_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("solarwindsservicedesk", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_topdesk_recovery_sync_populates_topdesk_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 29, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("topdesk_incidents",),
    supported_workflow_providers=("topdesk",),
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
    operator_alert_paging_policy_default_provider="topdesk",
    operator_alert_paging_policy_warning_targets=("topdesk_incidents",),
    operator_alert_paging_policy_critical_targets=("topdesk_incidents",),
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
    operator_reason="topdesk_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="topdesk",
    event_kind="remediation_started",
    actor="topdesk",
    detail="topdesk_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="TOP-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "topdesk-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "topdesk": {
        "alert_id": "TOP-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://topdesk.example/incidents/TOP-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 82,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "topdesk recovery started",
        "external_run_id": "topdesk-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "topdesk"
  assert updated_incident.remediation.provider_recovery.topdesk.alert_id == "TOP-123"
  assert updated_incident.remediation.provider_recovery.topdesk.external_reference == "guarded-live:market-data:5m"
  assert updated_incident.remediation.provider_recovery.topdesk.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.topdesk.priority == "high"
  assert updated_incident.remediation.provider_recovery.topdesk.escalation_policy == "market-data-primary"
  assert updated_incident.remediation.provider_recovery.topdesk.assignee == "market-data-oncall"
  assert updated_incident.remediation.provider_recovery.topdesk.phase_graph.alert_phase == "acknowledged"
  assert updated_incident.remediation.provider_recovery.topdesk.phase_graph.workflow_phase == "provider_recovering"
  assert updated_incident.remediation.provider_recovery.topdesk.phase_graph.ownership_phase == "assigned"
  assert updated_incident.remediation.provider_recovery.topdesk.phase_graph.escalation_phase == "configured"
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 82
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_topdesk_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 24, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("topdesk_incidents",),
    supported_workflow_providers=("topdesk",),
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
    operator_alert_paging_policy_warning_targets=("topdesk_incidents",),
    operator_alert_paging_policy_critical_targets=("topdesk_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("topdesk_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("topdesk_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="topdesk_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "topdesk"
  assert incident.delivery_targets == ("topdesk_incidents",)
  assert incident.escalation_targets == ("topdesk_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="topdesk",
    event_kind="triggered",
    actor="topdesk",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="TOP-123",
    occurred_at=clock.current + timedelta(minutes=1),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.external_provider == "topdesk"
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="topdesk_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("topdesk", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_external_invgateservicedesk_recovery_sync_populates_invgateservicedesk_typed_schema(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 19, 29, tzinfo=UTC))
  market_data = StatusOverrideSeededMarketDataAdapter()
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("invgateservicedesk_incidents",),
    supported_workflow_providers=("invgateservicedesk",),
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
    operator_alert_paging_policy_default_provider="invgateservicedesk",
    operator_alert_paging_policy_warning_targets=("invgateservicedesk_incidents",),
    operator_alert_paging_policy_critical_targets=("invgateservicedesk_incidents",),
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
    operator_reason="invgateservicedesk_market_data_recovery_sync",
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

  synced = app.sync_guarded_live_incident_from_external(
    provider="invgateservicedesk",
    event_kind="remediation_started",
    actor="invgateservicedesk",
    detail="invgateservicedesk_market_data_recovery_started",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IGSD-123",
    occurred_at=clock.current + timedelta(minutes=1),
    payload={
      "job_id": "invgateservicedesk-job-11",
      "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
      "invgateservicedesk": {
        "alert_id": "IGSD-123",
        "external_reference": "guarded-live:market-data:5m",
        "alert_status": "acknowledged",
        "priority": "high",
        "escalation_policy": "market-data-primary",
        "assignee": "market-data-oncall",
        "url": "https://invgateservicedesk.example/incidents/IGSD-123",
      },
      "telemetry": {
        "state": "running",
        "progress_percent": 82,
        "attempt_count": 1,
        "current_step": "verify_repaired_window",
        "last_message": "invgateservicedesk recovery started",
        "external_run_id": "invgateservicedesk-telemetry-1",
      },
    },
  )

  updated_incident = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert updated_incident.remediation.provider_recovery.provider_schema_kind == "invgateservicedesk"
  assert updated_incident.remediation.provider_recovery.invgateservicedesk.alert_id == "IGSD-123"
  assert (
    updated_incident.remediation.provider_recovery.invgateservicedesk.external_reference
    == "guarded-live:market-data:5m"
  )
  assert updated_incident.remediation.provider_recovery.invgateservicedesk.alert_status == "acknowledged"
  assert updated_incident.remediation.provider_recovery.invgateservicedesk.priority == "high"
  assert (
    updated_incident.remediation.provider_recovery.invgateservicedesk.escalation_policy
    == "market-data-primary"
  )
  assert updated_incident.remediation.provider_recovery.invgateservicedesk.assignee == "market-data-oncall"
  assert (
    updated_incident.remediation.provider_recovery.invgateservicedesk.phase_graph.alert_phase
    == "acknowledged"
  )
  assert (
    updated_incident.remediation.provider_recovery.invgateservicedesk.phase_graph.workflow_phase
    == "provider_recovering"
  )
  assert (
    updated_incident.remediation.provider_recovery.invgateservicedesk.phase_graph.ownership_phase
    == "assigned"
  )
  assert (
    updated_incident.remediation.provider_recovery.invgateservicedesk.phase_graph.escalation_phase
    == "configured"
  )
  assert updated_incident.remediation.provider_recovery.telemetry.state == "running"
  assert updated_incident.remediation.provider_recovery.telemetry.progress_percent == 82
  assert updated_incident.remediation.provider_recovery.telemetry.current_step == "verify_repaired_window"


def test_incident_paging_provider_can_be_inferred_for_invgateservicedesk_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 18, 24, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("invgateservicedesk_incidents",),
    supported_workflow_providers=("invgateservicedesk",),
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
    operator_alert_paging_policy_warning_targets=("invgateservicedesk_incidents",),
    operator_alert_paging_policy_critical_targets=("invgateservicedesk_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("invgateservicedesk_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("invgateservicedesk_incidents",),
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

  opened = app.run_guarded_live_reconciliation(
    actor="operator",
    reason="invgateservicedesk_policy",
  )
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "invgateservicedesk"
  assert incident.delivery_targets == ("invgateservicedesk_incidents",)
  assert incident.escalation_targets == ("invgateservicedesk_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="invgateservicedesk",
    event_kind="triggered",
    actor="invgateservicedesk",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="IGSD-456",
    occurred_at=clock.current + timedelta(minutes=1),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.external_provider == "invgateservicedesk"
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="invgateservicedesk_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("invgateservicedesk", "acknowledge", 1)
    for attempt in delivery.workflow_attempts
  )


def test_incident_paging_provider_can_be_inferred_for_opsramp_workflow(
  tmp_path: Path,
) -> None:
  runs = build_runs_repository(tmp_path)
  guarded_live_state = build_guarded_live_repository(tmp_path)
  clock = MutableClock(datetime(2025, 1, 3, 16, 59, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("opsramp_incidents",),
    supported_workflow_providers=("opsramp",),
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
    operator_alert_paging_policy_warning_targets=("opsramp_incidents",),
    operator_alert_paging_policy_critical_targets=("opsramp_incidents",),
    operator_alert_paging_policy_warning_escalation_targets=("opsramp_incidents",),
    operator_alert_paging_policy_critical_escalation_targets=("opsramp_incidents",),
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

  opened = app.run_guarded_live_reconciliation(actor="operator", reason="opsramp_policy")
  incident = next(
    event
    for event in opened.incident_events
    if event.kind == "incident_opened" and event.alert_id == "guarded-live:reconciliation"
  )
  assert incident.paging_provider == "opsramp"
  assert incident.delivery_targets == ("opsramp_incidents",)
  assert incident.escalation_targets == ("opsramp_incidents",)

  synced = app.sync_guarded_live_incident_from_external(
    provider="opsramp",
    event_kind="triggered",
    actor="opsramp",
    detail="provider_alert_opened",
    alert_id=incident.alert_id,
    external_reference=incident.alert_id,
    workflow_reference="OR-123",
    occurred_at=clock.current + timedelta(seconds=15),
  )
  triggered = next(event for event in synced.incident_events if event.event_id == incident.event_id)
  assert triggered.provider_workflow_reference == "OR-123"
  assert triggered.external_provider == "opsramp"

  clock.advance(timedelta(minutes=1))
  acknowledged = app.acknowledge_guarded_live_incident(
    event_id=incident.event_id,
    actor="operator",
    reason="opsramp_ack",
  )
  updated = next(event for event in acknowledged.incident_events if event.event_id == incident.event_id)
  assert updated.provider_workflow_state == "delivered"
  assert updated.provider_workflow_action == "acknowledge"
  assert any(
    attempt[1:] == ("opsramp", "acknowledge", 1)
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


def test_run_experiment_metadata_is_durable_queryable_and_preserved_for_reruns(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
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
