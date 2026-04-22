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

