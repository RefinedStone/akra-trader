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
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.guarded_live import SqlAlchemyGuardedLiveStateRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.references import load_reference_catalog
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
from .application_test_support import build_references
from .application_test_support import build_runs_repository
from .application_test_support import without_surface_rule


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

