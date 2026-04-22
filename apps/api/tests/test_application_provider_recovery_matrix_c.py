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

