from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.config import Settings
from akra_trader.domain.models import DatasetBoundaryContract
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import GuardedLiveBookTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveKlineChannelSnapshot
from akra_trader.domain.models import GuardedLiveOrderBookLevel
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonNarrative
from akra_trader.domain.models import RunComparisonRun
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import ProviderProvenanceSchedulerHealth
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import SyncFailure
from akra_trader.main import create_app
from akra_trader.adapters.venue_execution import SeededVenueExecutionAdapter
from akra_trader.strategies.llm import ExternalDecisionStrategy


def build_client(
  database_path: Path,
  *,
  guarded_live_execution_enabled: bool = False,
  guarded_live_venue: str | None = None,
  provider_provenance_report_scheduler_enabled: bool = True,
  operator_alert_external_sync_token: str | None = None,
  replay_alias_audit_admin_read_token: str | None = None,
  replay_alias_audit_admin_write_token: str | None = None,
) -> TestClient:
  settings = Settings(
    runs_database_url=f"sqlite:///{database_path}",
    provider_provenance_scheduler_search_database_url=(
      f"sqlite:///{database_path.with_name(f'{database_path.stem}-scheduler-search.sqlite3')}"
    ),
    provider_provenance_scheduler_search_service_url="embedded://provider-provenance-scheduler-search",
    market_data_provider="seeded",
    guarded_live_execution_enabled=guarded_live_execution_enabled,
    guarded_live_venue=guarded_live_venue,
    provider_provenance_report_scheduler_enabled=provider_provenance_report_scheduler_enabled,
    operator_alert_external_sync_token=operator_alert_external_sync_token,
    replay_alias_audit_admin_read_token=replay_alias_audit_admin_read_token,
    replay_alias_audit_admin_write_token=replay_alias_audit_admin_write_token,
  )
  return TestClient(create_app(settings))


def _first_non_null_schema_branch(schema: dict) -> dict:
  if "anyOf" not in schema:
    return schema
  return next(branch for branch in schema["anyOf"] if branch.get("type") != "null")


def create_preset(
  client: TestClient,
  *,
  name: str,
  preset_id: str,
  strategy_id: str | None = None,
  timeframe: str | None = None,
  benchmark_family: str | None = None,
  tags: list[str] | None = None,
  parameters: dict[str, object] | None = None,
) -> dict:
  response = client.post(
    "/api/presets",
    json={
      "name": name,
      "preset_id": preset_id,
      "strategy_id": strategy_id,
      "timeframe": timeframe,
      "benchmark_family": benchmark_family,
      "tags": tags or [],
      "parameters": parameters or {},
    },
  )
  assert response.status_code == 200
  return response.json()


def without_surface_rule(
  capabilities: RunSurfaceCapabilities,
  *,
  family_key: str,
  surface_key: str,
) -> RunSurfaceCapabilities:
  return replace(
    capabilities,
    shared_contracts=tuple(
      replace(
        contract,
        surface_rules=tuple(
          rule
          for rule in contract.surface_rules
          if rule.surface_key != surface_key
        ),
      )
      if contract.contract_key == f"family:{family_key}" and contract.contract_kind == "capability_family"
      else contract
      for contract in capabilities.shared_contracts
    ),
  )


class StaticVenueStateAdapter:
  def __init__(self, snapshot: GuardedLiveVenueStateSnapshot) -> None:
    self._snapshot = snapshot

  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
    return self._snapshot


class StatusOverrideSeededMarketDataAdapter(SeededMarketDataAdapter):
  def __init__(self) -> None:
    super().__init__()
    self._status_by_timeframe: dict[str, MarketDataStatus] = {}
    self._remediation_status_by_key: dict[tuple[str, str], MarketDataStatus] = {}
    self._lineage_history: tuple[MarketDataLineageHistoryRecord, ...] = ()
    self._ingestion_jobs: tuple[MarketDataIngestionJobRecord, ...] = ()

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

  def set_lineage_history(
    self,
    records: tuple[MarketDataLineageHistoryRecord, ...],
  ) -> None:
    self._lineage_history = records

  def set_ingestion_jobs(
    self,
    records: tuple[MarketDataIngestionJobRecord, ...],
  ) -> None:
    self._ingestion_jobs = records

  def get_status(self, timeframe: str) -> MarketDataStatus:
    status = self._status_by_timeframe.get(timeframe)
    if status is not None:
      return status
    return super().get_status(timeframe)

  def list_lineage_history(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataLineageHistoryRecord, ...]:
    records = self._lineage_history or super().list_lineage_history(
      timeframe=timeframe,
      symbol=symbol,
      sync_status=sync_status,
      validation_claim=validation_claim,
      limit=limit,
    )
    filtered = [
      record
      for record in records
      if (timeframe is None or record.timeframe == timeframe)
      and (symbol is None or record.symbol == symbol)
      and (sync_status is None or record.sync_status == sync_status)
      and (validation_claim is None or record.validation_claim == validation_claim)
    ]
    if limit is not None:
      filtered = filtered[:limit]
    return tuple(filtered)

  def list_ingestion_jobs(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataIngestionJobRecord, ...]:
    records = self._ingestion_jobs or super().list_ingestion_jobs(
      timeframe=timeframe,
      symbol=symbol,
      operation=operation,
      status=status,
      limit=limit,
    )
    filtered = [
      record
      for record in records
      if (timeframe is None or record.timeframe == timeframe)
      and (symbol is None or record.symbol == symbol)
      and (operation is None or record.operation == operation)
      and (status is None or record.status == status)
    ]
    if limit is not None:
      filtered = filtered[:limit]
    return tuple(filtered)

  def remediate(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
  ) -> MarketDataRemediationResult:
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


class StubDecisionEngine:
  def decide(self, context) -> StrategyDecisionEnvelope:
    return StrategyDecisionEnvelope(
      signal=SignalDecision(timestamp=context.timestamp, action=SignalAction.HOLD),
      rationale="stub",
      context=context,
    )


def test_operator_visibility_endpoint_persists_guarded_live_alert_history(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 15, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),
        ),
      )
    )

    first_reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_balance_check"},
    )
    assert first_reconcile.status_code == 200

    active_visibility = client.get("/api/operator/visibility")
    assert active_visibility.status_code == 200
    active_payload = active_visibility.json()
    active_alert = next(
      alert for alert in active_payload["alerts"]
      if alert["alert_id"] == "guarded-live:reconciliation"
    )
    assert active_alert["source"] == "guarded_live"
    assert "guarded_live_status" in active_alert["delivery_targets"]
    active_history = next(
      alert for alert in active_payload["alert_history"]
      if alert["alert_id"] == "guarded-live:reconciliation"
    )
    assert active_history["status"] == "active"
    assert active_payload["incident_events"][0]["kind"] == "incident_opened"
    assert active_payload["incident_events"][0]["alert_id"] == "guarded-live:reconciliation"
    assert active_payload["delivery_history"][0]["target"] == "operator_console"
    assert active_payload["delivery_history"][0]["status"] == "delivered"
    assert active_payload["delivery_history"][0]["attempt_number"] == 1
    assert active_payload["delivery_history"][0]["next_retry_at"] is None
    assert any(event["kind"] == "guarded_live_reconciliation_ran" for event in active_payload["audit_events"])

    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 20, tzinfo=UTC),
      )
    )
    second_reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "post_fix_balance_check"},
    )
    assert second_reconcile.status_code == 200

    resolved_visibility = client.get("/api/operator/visibility")

  assert resolved_visibility.status_code == 200
  resolved_payload = resolved_visibility.json()
  assert all(
    alert["alert_id"] != "guarded-live:reconciliation"
    for alert in resolved_payload["alerts"]
  )
  resolved_history = next(
    alert for alert in resolved_payload["alert_history"]
    if alert["alert_id"] == "guarded-live:reconciliation"
  )
  assert resolved_history["status"] == "resolved"
  assert resolved_history["resolved_at"] is not None
  assert resolved_payload["incident_events"][0]["kind"] == "incident_resolved"


def test_guarded_live_endpoints_manage_kill_switch_and_block_runtime_starts(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    initial = client.get("/api/guarded-live")
    assert initial.status_code == 200
    assert initial.json()["kill_switch"]["state"] == "released"

    engage_response = client.post(
      "/api/guarded-live/kill-switch/engage",
      json={"actor": "operator", "reason": "manual_safety_drill"},
    )

    assert engage_response.status_code == 200
    payload = engage_response.json()
    assert payload["kill_switch"]["state"] == "engaged"
    assert payload["kill_switch"]["updated_by"] == "operator"
    assert payload["audit_events"][0]["kind"] == "guarded_live_kill_switch_engaged"

    blocked_start = client.post(
      "/api/runs/sandbox",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
      },
    )

    assert blocked_start.status_code == 400
    assert "kill switch" in blocked_start.json()["detail"]

    release_response = client.post(
      "/api/guarded-live/kill-switch/release",
      json={"actor": "operator", "reason": "drill_complete"},
    )

    assert release_response.status_code == 200
    released_payload = release_response.json()
    assert released_payload["kill_switch"]["state"] == "released"
    assert any(
      event["kind"] == "guarded_live_kill_switch_released"
      for event in released_payload["audit_events"]
    )


def test_guarded_live_incident_endpoints_acknowledge_and_escalate(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._operator_alert_escalation_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 15, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),),
      )
    )
    reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "incident_actions"},
    )
    assert reconcile.status_code == 200
    incident = next(
      event
      for event in reconcile.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:reconciliation"
    )

    acknowledged = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/acknowledge",
      json={"actor": "operator", "reason": "on_call_ack"},
    )
    assert acknowledged.status_code == 200
    acknowledged_incident = next(
      event
      for event in acknowledged.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert acknowledged_incident["acknowledgment_state"] == "acknowledged"
    assert acknowledged_incident["acknowledged_by"] == "operator"
    assert acknowledged_incident["acknowledgment_reason"] == "on_call_ack"

    escalated = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/escalate",
      json={"actor": "operator", "reason": "manager_page"},
    )
    assert escalated.status_code == 200
    escalated_incident = next(
      event
      for event in escalated.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert escalated_incident["escalation_level"] == 1
    assert escalated_incident["last_escalated_by"] == "operator"
    assert escalated_incident["escalation_reason"] == "manager_page"
    escalation_delivery = next(
      record
      for record in escalated.json()["delivery_history"]
      if record["incident_event_id"] == incident["event_id"] and record["phase"] == "escalation"
    )
    assert escalation_delivery["target"] == "pagerduty_events"


def test_external_incident_sync_endpoint_updates_paging_state_and_requires_token(tmp_path: Path) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    operator_alert_external_sync_token="shared-token",
  ) as client:
    app = client.app.state.container.app
    app._operator_alert_escalation_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 15, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),),
      )
    )
    reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "external_incident_sync"},
    )
    assert reconcile.status_code == 200

    forbidden = client.post(
      "/api/operator/incidents/external-sync",
      json={
        "provider": "pagerduty",
        "event_kind": "acknowledged",
        "actor": "responder-1",
        "detail": "pd_ack",
        "alert_id": "guarded-live:reconciliation",
      },
    )
    assert forbidden.status_code == 403

    synced = client.post(
      "/api/operator/incidents/external-sync",
      headers={"X-Akra-Incident-Sync-Token": "shared-token"},
      json={
        "provider": "pagerduty",
        "event_kind": "acknowledged",
        "actor": "responder-1",
        "detail": "pd_ack",
        "alert_id": "guarded-live:reconciliation",
        "external_reference": "guarded-live:reconciliation",
        "occurred_at": "2025-01-03T13:16:00Z",
      },
    )
    assert synced.status_code == 200
    incident = next(
      event
      for event in synced.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:reconciliation"
    )
    assert incident["acknowledgment_state"] == "acknowledged"
    assert incident["acknowledged_by"] == "pagerduty:responder-1"
    assert incident["external_provider"] == "pagerduty"
    assert incident["external_status"] == "acknowledged"
    assert incident["paging_status"] == "acknowledged"


def test_incident_endpoints_surface_provider_workflow_and_paging_policy(tmp_path: Path) -> None:
  class FakeProviderWorkflowDeliveryAdapter:
    def list_targets(self) -> tuple[str, ...]:
      return ("operator_console",)

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
      resolved_targets = targets or self.list_targets()
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_delivery:{target}",
          attempt_number=attempt_number,
          phase=phase,
          external_provider="pagerduty" if target == "pagerduty_events" else None,
          external_reference=incident.external_reference or incident.alert_id,
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
      payload=None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return (
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{provider}_workflow:{action}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=f"{provider}_workflow",
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_provider_workflow:{action}:{detail}",
          attempt_number=attempt_number,
          phase=f"provider_{action}",
          provider_action=action,
          external_provider=provider,
          external_reference=incident.provider_workflow_reference,
          source=incident.source,
        ),
      )

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ):
      return None

  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    operator_alert_external_sync_token="shared-token",
  ) as client:
    app = client.app.state.container.app
    app._operator_alert_delivery = FakeProviderWorkflowDeliveryAdapter()
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("slack_webhook", "pagerduty_events")
    app._operator_alert_paging_policy_critical_targets = ("slack_webhook", "pagerduty_events")
    app._operator_alert_paging_policy_warning_escalation_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_escalation_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 14, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),),
      )
    )

    reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "provider_workflow_surface"},
    )
    assert reconcile.status_code == 200
    incident = next(
      event
      for event in reconcile.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:reconciliation"
    )
    assert incident["paging_provider"] == "pagerduty"
    assert incident["paging_policy_id"] in {"severity:warning", "severity:critical"}

    synced = client.post(
      "/api/operator/incidents/external-sync",
      headers={"X-Akra-Incident-Sync-Token": "shared-token"},
      json={
        "provider": "pagerduty",
        "event_kind": "triggered",
        "actor": "responder-1",
        "detail": "provider_triggered",
        "alert_id": "guarded-live:reconciliation",
        "external_reference": "guarded-live:reconciliation",
        "workflow_reference": "PDINC-901",
        "occurred_at": "2025-01-03T14:01:00Z",
      },
    )
    assert synced.status_code == 200

    acknowledged = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/acknowledge",
      json={"actor": "operator", "reason": "provider_ack"},
    )
    assert acknowledged.status_code == 200
    acknowledged_incident = next(
      event
      for event in acknowledged.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert acknowledged_incident["provider_workflow_reference"] == "PDINC-901"
    assert acknowledged_incident["provider_workflow_state"] == "delivered"
    assert acknowledged_incident["provider_workflow_action"] == "acknowledge"
    provider_delivery = next(
      record
      for record in acknowledged.json()["delivery_history"]
      if record["incident_event_id"] == incident["event_id"] and record["phase"] == "provider_acknowledge"
    )
    assert provider_delivery["target"] == "pagerduty_workflow"


def test_guarded_live_status_survives_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path) as client:
    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "startup_drill"},
    )
    assert reconcile_response.status_code == 200

    engage_response = client.post(
      "/api/guarded-live/kill-switch/engage",
      json={"actor": "operator", "reason": "startup_safety_latch"},
    )
    assert engage_response.status_code == 200

  with build_client(database_path) as restarted_client:
    response = restarted_client.get("/api/guarded-live")

  assert response.status_code == 200
  payload = response.json()
  assert payload["kill_switch"]["state"] == "engaged"
  assert payload["reconciliation"]["checked_by"] == "operator"
  assert payload["reconciliation"]["scope"] == "venue_state"
  assert payload["reconciliation"]["venue_snapshot"]["provider"] == "seeded"
  assert payload["reconciliation"]["venue_snapshot"]["verification_state"] == "verified"
  assert any(event["kind"] == "guarded_live_reconciliation_ran" for event in payload["audit_events"])
  assert any(event["kind"] == "guarded_live_kill_switch_engaged" for event in payload["audit_events"])


def test_guarded_live_reconciliation_endpoint_surfaces_venue_balance_mismatch(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
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
        quantity=1.25,
        average_price=2_000.0,
        opened_at=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
        updated_at=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
      )
    }
    app._runs.save_run(run)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 16, 5, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.5, free=0.5, used=0.0),
          GuardedLiveVenueBalance(asset="USDT", total=9_000.0, free=9_000.0, used=0.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_100.0,
          ),
        ),
      )
    )

    response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "venue_state_drill"},
    )

  assert response.status_code == 200
  payload = response.json()
  assert payload["reconciliation"]["venue_snapshot"]["verification_state"] == "verified"
  assert any(
    finding["kind"] == "venue_balance_mismatch"
    for finding in payload["reconciliation"]["findings"]
  )
  assert any(
    finding["kind"] == "venue_open_order_mismatch"
    for finding in payload["reconciliation"]["findings"]
  )


def test_guarded_live_recovery_endpoint_recovers_from_stored_verified_snapshot_after_restart(
  tmp_path: Path,
) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 17, 0, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.6, free=0.4, used=0.2),
          GuardedLiveVenueBalance(asset="USDT", total=9_400.0, free=9_400.0, used=0.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-order-2",
            symbol="ETH/USDT",
            side="sell",
            amount=0.2,
            status="open",
            price=2_250.0,
          ),
        ),
      )
    )

    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_restart_snapshot"},
    )
    assert reconcile_response.status_code == 200

    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="binance",
        venue="binance",
        verification_state="unavailable",
        captured_at=datetime(2025, 1, 3, 17, 5, tzinfo=UTC),
        issues=("temporary_venue_fault",),
      )
    )
    recovery_response = client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "post_restart_recovery"},
    )

    assert recovery_response.status_code == 200
    recovery_payload = recovery_response.json()
    assert recovery_payload["recovery"]["state"] == "recovered"
    assert recovery_payload["recovery"]["source_verification_state"] == "verified"
    assert recovery_payload["recovery"]["exposures"][0]["instrument_id"] == "binance:ETH/USDT"
    assert recovery_payload["recovery"]["open_orders"][0]["order_id"] == "venue-order-2"
    assert any(event["kind"] == "guarded_live_runtime_recovered" for event in recovery_payload["audit_events"])

  with build_client(database_path) as restarted_client:
    status_response = restarted_client.get("/api/guarded-live")

  assert status_response.status_code == 200
  payload = status_response.json()
  assert payload["recovery"]["state"] == "recovered"
  assert payload["recovery"]["source_verification_state"] == "verified"
  assert payload["recovery"]["exposures"][0]["symbol"] == "ETH/USDT"


def test_live_endpoints_launch_and_stop_guarded_live_worker_after_gates_clear(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
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

    blocked_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "pre_gate_attempt",
      },
    )
    assert blocked_response.status_code == 400
    assert "blocked" in blocked_response.json()["detail"]

    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    assert reconcile_response.status_code == 200

    recovery_response = client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    assert recovery_response.status_code == 200

    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "guarded_live_launch",
      },
    )

    assert live_response.status_code == 200
    payload = live_response.json()
    assert payload["config"]["mode"] == "live"
    assert payload["status"] == "running"
    assert payload["provenance"]["runtime_session"]["worker_kind"] == "guarded_live_native_worker"
    assert payload["notes"][0].startswith("Guarded live worker primed from recovered venue state")

    run_id = payload["config"]["run_id"]
    stop_response = client.post(f"/api/runs/live/{run_id}/stop")

  assert stop_response.status_code == 200
  stopped_payload = stop_response.json()
  assert stopped_payload["status"] == "stopped"
  assert stopped_payload["provenance"]["runtime_session"]["lifecycle_state"] == "stopped"


def test_stop_sandbox_endpoint_rejects_when_control_surface_rule_is_disabled(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    run_response = client.post(
      "/api/runs/sandbox",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
      },
    )
    run_id = run_response.json()["config"]["run_id"]
    base_capabilities = app.get_run_surface_capabilities()
    app.get_run_surface_capabilities = lambda: without_surface_rule(
      base_capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
    )

    stop_response = client.post(f"/api/runs/sandbox/{run_id}/stop")

  assert stop_response.status_code == 400
  assert stop_response.json()["detail"] == (
    "Surface rule rerun_and_stop_controls is disabled by the run-surface capability contract."
  )


def test_operator_visibility_endpoint_surfaces_risk_breach_and_live_fault_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "risk_fault_visibility",
      },
    )
    assert live_response.status_code == 200
    payload = live_response.json()
    run = app.get_run(payload["config"]["run_id"])
    assert run is not None
    assert run.provenance.runtime_session is not None
    run.provenance.runtime_session.recovery_count = 2
    run.provenance.runtime_session.last_recovered_at = datetime(2025, 1, 3, 18, 1, tzinfo=UTC)
    run.provenance.runtime_session.last_recovery_reason = "heartbeat_timeout"
    run.metrics["max_drawdown_pct"] = 41.0
    run.orders.append(
      Order(
        run_id=run.config.run_id,
        instrument_id="binance:ETH/USDT",
        side=OrderSide.BUY,
        quantity=0.2,
        requested_price=3_150.0,
        order_type=OrderType.LIMIT,
        status=OrderStatus.OPEN,
        order_id="stale-api-live-order-1",
        created_at=datetime(2025, 1, 3, 17, 50, tzinfo=UTC),
        updated_at=datetime(2025, 1, 3, 17, 51, tzinfo=UTC),
        last_synced_at=datetime(2025, 1, 3, 17, 52, tzinfo=UTC),
        remaining_quantity=0.2,
      )
    )
    app._runs.save_run(run)

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run.config.run_id and alert.get("source") == "guarded_live"
    }
    assert {"risk_breach", "runtime_recovery", "order_sync"} <= categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    assert any(event["alert_id"].startswith("guarded-live:risk-breach:") for event in incident_events)
    assert any(event["alert_id"].startswith("guarded-live:order-sync:") for event in incident_events)


def test_operator_visibility_endpoint_surfaces_market_data_freshness_and_wider_risk_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    market_data = StatusOverrideSeededMarketDataAdapter()
    app._market_data = market_data
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "market_data_risk_visibility",
      },
    )
    assert live_response.status_code == 200
    run = app.get_run(live_response.json()["config"]["run_id"])
    assert run is not None
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
            first_timestamp=datetime(2025, 1, 2, 18, 0, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 17, 40, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 17, 45, tzinfo=UTC),
            recent_failures=(
              SyncFailure(
                failed_at=datetime(2025, 1, 3, 17, 51, tzinfo=UTC),
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
                start_at=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
                end_at=datetime(2025, 1, 3, 16, 10, tzinfo=UTC),
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
        order_id="api-pending-risk-order-1",
        created_at=datetime(2025, 1, 3, 17, 54, tzinfo=UTC),
        updated_at=datetime(2025, 1, 3, 17, 54, tzinfo=UTC),
        last_synced_at=datetime(2025, 1, 3, 17, 59, 30, tzinfo=UTC),
        remaining_quantity=4.0,
      )
    )
    app._runs.save_run(run)

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {alert["category"] for alert in alerts if alert.get("source") == "guarded_live"}
    assert {
      "market_data_freshness",
      "market_data_quality",
      "market_data_candle_continuity",
      "market_data_venue",
      "risk_breach",
    } <= categories
    market_data_alert = next(alert for alert in alerts if alert["category"] == "market_data_freshness")
    assert "ETH/USDT lagged 1200s." in market_data_alert["detail"]
    assert market_data_alert["symbol"] == "ETH/USDT"
    assert market_data_alert["symbols"] == ["ETH/USDT"]
    assert market_data_alert["timeframe"] == "5m"
    market_data_quality_alert = next(alert for alert in alerts if alert["category"] == "market_data_quality")
    assert "backfill target covers 72.00%" in market_data_quality_alert["detail"]
    market_data_continuity_alert = next(alert for alert in alerts if alert["category"] == "market_data_candle_continuity")
    assert "has 3 missing candle(s) across 1 gap window(s)." in market_data_continuity_alert["detail"]
    assert "contiguous backfill quality is 91.00%" in market_data_continuity_alert["detail"]
    market_data_venue_alert = next(alert for alert in alerts if alert["category"] == "market_data_venue")
    assert "recorded 2 sync failure(s)" in market_data_venue_alert["detail"]
    assert "venue semantics: timeout" in market_data_venue_alert["detail"]
    risk_alert = next(
      alert for alert in alerts
      if alert.get("run_id") == run.config.run_id and alert["category"] == "risk_breach"
    )
    assert "total return -24.00%" in risk_alert["detail"]
    assert "gross open risk reached" in risk_alert["detail"]
    assert risk_alert["symbol"] == "ETH/USDT"
    assert risk_alert["symbols"] == ["ETH/USDT"]
    assert risk_alert["timeframe"] == "5m"

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    market_data_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert market_data_incident["symbol"] == "ETH/USDT"
    assert market_data_incident["symbols"] == ["ETH/USDT"]
    assert market_data_incident["timeframe"] == "5m"
    assert any(event["alert_id"] == "guarded-live:market-data:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-quality:binance:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-continuity:binance:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-venue:binance:5m" for event in incident_events)
    assert any(event["alert_id"].startswith("guarded-live:risk-breach:") for event in incident_events)


def test_operator_visibility_endpoint_embeds_multi_symbol_primary_focus_metadata(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    market_data = StatusOverrideSeededMarketDataAdapter()
    app._market_data = market_data
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "api_multi_symbol_primary_focus",
      },
    )
    assert live_response.status_code == 200
    run = app.get_run(live_response.json()["config"]["run_id"])
    assert run is not None
    secondary_run = replace(
      run,
      config=replace(
        run.config,
        run_id="api-live-run-btc-primary-focus",
        symbols=("BTC/USDT",),
      ),
      provenance=replace(
        run.provenance,
        runtime_session=replace(
          run.provenance.runtime_session,
          session_id="worker-live-btc-primary-focus-api",
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
    app._runs.save_run(secondary_run)
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
            first_timestamp=datetime(2025, 1, 2, 18, 0, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 17, 42, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_080,
            last_sync_at=datetime(2025, 1, 3, 17, 48, tzinfo=UTC),
            failure_count_24h=2,
            backfill_gap_windows=(
              GapWindow(
                start_at=datetime(2025, 1, 3, 17, 0, tzinfo=UTC),
                end_at=datetime(2025, 1, 3, 17, 10, tzinfo=UTC),
                missing_candles=2,
              ),
            ),
            issues=("freshness_threshold_exceeded:1080:600", "repeated_sync_failures:2"),
          ),
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 0, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 17, 59, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 17, 59, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    market_data_alert = next(
      alert
      for alert in visibility_response.json()["alerts"]
      if alert["category"] == "market_data_freshness"
    )
    assert market_data_alert["symbol"] is None
    assert market_data_alert["symbols"] == ["BTC/USDT", "ETH/USDT"]
    assert market_data_alert["primary_focus"] == {
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "candidate_symbols": ["BTC/USDT", "ETH/USDT"],
      "candidate_count": 2,
      "policy": "market_data_risk_order",
      "reason": "Selected BTC/USDT as the highest-risk market-data candidate from 2 symbols.",
    }

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    market_data_incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert market_data_incident["symbol"] is None
    assert market_data_incident["symbols"] == ["BTC/USDT", "ETH/USDT"]
    assert market_data_incident["primary_focus"] == market_data_alert["primary_focus"]


def test_market_data_incident_endpoint_surfaces_remediation_and_provider_workflow(
  tmp_path: Path,
) -> None:
  class FakeProviderWorkflowDeliveryAdapter:
    def list_targets(self) -> tuple[str, ...]:
      return ("pagerduty_events",)

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
      resolved_targets = targets or self.list_targets()
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_delivery:{target}",
          attempt_number=attempt_number,
          phase=phase,
          external_provider="pagerduty",
          external_reference=incident.external_reference or incident.alert_id,
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
      payload=None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return (
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{provider}_workflow:{action}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=f"{provider}_workflow",
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_provider_workflow:{action}:{detail}",
          attempt_number=attempt_number,
          phase=f"provider_{action}",
          provider_action=action,
          external_provider=provider,
          external_reference=incident.provider_workflow_reference or incident.external_reference or incident.alert_id,
          source=incident.source,
        ),
      )

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ):
      return None

  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._operator_alert_delivery = FakeProviderWorkflowDeliveryAdapter()
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "market_data_remediation_surface"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "market_data_remediation_surface"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "market_data_remediation_surface",
      },
    )
    assert live_response.status_code == 200
    market_data = StatusOverrideSeededMarketDataAdapter()
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
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 10, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
            issues=("freshness_threshold_exceeded:1200:600",),
          ),
        ],
      ),
    )
    app._market_data = market_data

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert incident["remediation"]["kind"] == "recent_sync"
    assert incident["remediation"]["state"] == "skipped"
    assert incident["remediation"]["runbook"] == "market_data.sync_recent"
    assert incident["remediation"]["provider"] == "pagerduty"
    assert incident["remediation"]["provider_recovery"]["lifecycle_state"] == "requested"
    assert incident["remediation"]["provider_recovery"]["status_machine"]["state"] == "provider_requested"
    assert incident["remediation"]["provider_recovery"]["status_machine"]["workflow_action"] == "remediate"
    assert "seeded_market_data_provider_has_no_live_remediation_jobs" in incident["remediation"]["detail"]
    assert any(
      record["incident_event_id"] == incident["event_id"] and record["phase"] == "provider_remediate"
      for record in guarded_live_response.json()["delivery_history"]
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
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )

    remediated = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/remediate",
      json={"actor": "operator", "reason": "manual_market_data_resync"},
    )
    assert remediated.status_code == 200
    refreshed = next(
      event
      for event in remediated.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert refreshed["remediation"]["state"] == "executed"
    assert refreshed["remediation"]["requested_by"] == "operator"
    assert "recent_sync:ETH/USDT:5m:status_repaired" in refreshed["remediation"]["detail"]
    assert any(
      event["kind"] == "incident_resolved" and event["alert_id"] == "guarded-live:market-data:5m"
      for event in remediated.json()["incident_events"]
    )
  assert all(
      alert["alert_id"] != "guarded-live:market-data:5m"
      for alert in remediated.json()["active_alerts"]
    )


def test_guarded_live_channel_restore_incidents_auto_run_local_session_job(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "channel_restore_local_remediation"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "channel_restore_local_remediation"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "channel_restore_local_remediation",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("trade_ticks", "depth_updates", "kline_candles"),
          handed_off_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_trade_event_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_kline_event_at=None,
          channel_restore_state="unavailable",
          channel_restore_count=2,
          channel_last_restored_at=datetime(2025, 1, 3, 18, 29, tzinfo=UTC),
          channel_continuation_state="unavailable",
          channel_continuation_count=2,
          channel_last_continued_at=datetime(2025, 1, 3, 18, 29, tzinfo=UTC),
          issues=("binance_market_channel_restore_failed:ticker:timeout:exchange timeout",),
        ),
      )
    )

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-channel-restore:{run_id}"
    )
    assert incident["remediation"]["kind"] == "channel_restore"
    assert guarded_live_response.json()["session_handoff"]["channel_restore_state"] == "synthetic"
    assert guarded_live_response.json()["session_handoff"]["channel_continuation_state"] == "synthetic"
    assert any(
      event["kind"] == "incident_resolved"
      and event["alert_id"] == f"guarded-live:market-data-channel-restore:{run_id}"
      for event in guarded_live_response.json()["incident_events"]
    )
    assert all(
      alert["alert_id"] != f"guarded-live:market-data-channel-restore:{run_id}"
      for alert in guarded_live_response.json()["active_alerts"]
    )
    assert any(
      event["kind"] == "guarded_live_incident_local_remediation_executed"
      and "channel_restore:ETH/USDT:5m:channel_restore=synthetic" in event["detail"]
      for event in guarded_live_response.json()["audit_events"]
    )


def test_external_market_data_recovery_sync_endpoint_resolves_incident(
  tmp_path: Path,
) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    operator_alert_external_sync_token="shared-token",
  ) as client:
    app = client.app.state.container.app
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "provider_market_data_recovery_surface"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "provider_market_data_recovery_surface"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "provider_market_data_recovery_surface",
      },
    )
    assert live_response.status_code == 200
    market_data = StatusOverrideSeededMarketDataAdapter()
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
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 10, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
            issues=("freshness_threshold_exceeded:1200:600",),
          ),
        ],
      ),
    )
    app._market_data = market_data

    guarded_live_response = client.get("/api/guarded-live")
    incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert incident["remediation"]["state"] == "not_supported"

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
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )

    synced = client.post(
      "/api/operator/incidents/external-sync",
      headers={"X-Akra-Incident-Sync-Token": "shared-token"},
      json={
        "provider": "pagerduty",
        "event_kind": "remediation_completed",
        "actor": "responder-1",
        "detail": "provider_market_data_recovered",
        "alert_id": "guarded-live:market-data:5m",
        "external_reference": "guarded-live:market-data:5m",
        "workflow_reference": "PDINC-REC-901",
        "occurred_at": "2025-01-03T18:31:00Z",
          "payload": {
            "job_id": "provider-job-901",
            "summary": "provider completed recovery verification",
            "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
            "verification": {"state": "passed"},
            "telemetry": {
              "state": "completed",
              "progress_percent": 100,
              "attempt_count": 2,
              "current_step": "verification",
              "external_run_id": "pd-api-telemetry-901",
            },
          },
        },
      )
    assert synced.status_code == 200
    updated_incident = next(
      event
      for event in synced.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert updated_incident["remediation"]["state"] == "executed"
    assert updated_incident["remediation"]["requested_by"] == "pagerduty:responder-1"
    assert updated_incident["remediation"]["provider_payload"]["job_id"] == "provider-job-901"
    assert updated_incident["remediation"]["provider_recovery"]["job_id"] == "provider-job-901"
    assert updated_incident["remediation"]["provider_recovery"]["provider_schema_kind"] == "pagerduty"
    assert updated_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_id"] == "PDINC-REC-901"
    assert updated_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_status"] == "delivered"
    assert updated_incident["remediation"]["provider_recovery"]["pagerduty"]["phase_graph"]["workflow_phase"] == "verified_pending_resolve"
    assert updated_incident["remediation"]["provider_recovery"]["telemetry"]["state"] == "completed"
    assert updated_incident["remediation"]["provider_recovery"]["telemetry"]["progress_percent"] == 100
    assert updated_incident["remediation"]["provider_recovery"]["telemetry"]["current_step"] == "verification"
    assert updated_incident["remediation"]["provider_recovery"]["symbols"] == ["ETH/USDT"]
    assert updated_incident["remediation"]["provider_recovery"]["timeframe"] == "5m"
    assert updated_incident["remediation"]["provider_recovery"]["verification"]["state"] == "passed"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["state"] == "verified"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_state"] == "delivered"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_action"] == "remediate"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["job_state"] == "verified"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["sync_state"] == "bidirectional_synced"
    assert updated_incident["provider_workflow_action"] == "remediate"
    assert updated_incident["provider_workflow_state"] == "delivered"
    assert updated_incident["provider_workflow_reference"] == "PDINC-REC-901"
    resolved_incident = next(
      event
      for event in synced.json()["incident_events"]
      if event["kind"] == "incident_resolved" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert resolved_incident["provider_workflow_action"] == "resolve"
    assert resolved_incident["provider_workflow_state"] in {"delivered", "not_supported"}
    assert resolved_incident["remediation"]["provider_payload"]["job_id"] == "provider-job-901"
    assert resolved_incident["remediation"]["provider_recovery"]["job_id"] == "provider-job-901"
    assert resolved_incident["remediation"]["provider_recovery"]["status_machine"]["state"] == "resolved"
    assert resolved_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_action"] == "resolve"
    assert resolved_incident["remediation"]["provider_recovery"]["status_machine"]["job_state"] == "resolved"


def test_guarded_live_endpoint_pull_syncs_provider_authoritative_recovery_state(
  tmp_path: Path,
) -> None:
  class FakeProviderPullSyncAdapter:
    def __init__(self) -> None:
      self.pull_attempts: list[tuple[str, str, str | None]] = []

    def list_targets(self) -> tuple[str, ...]:
      return ("pagerduty_events",)

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
      resolved_targets = targets or self.list_targets()
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_delivery:{target}",
          attempt_number=attempt_number,
          phase=phase,
          external_provider="pagerduty",
          external_reference=incident.external_reference or incident.alert_id,
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
      payload=None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return (
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{provider}_workflow:{action}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=f"{provider}_workflow",
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_provider_workflow:{action}:{detail}",
          attempt_number=attempt_number,
          phase=f"provider_{action}",
          provider_action=action,
          external_provider=provider,
          external_reference=incident.provider_workflow_reference or incident.external_reference or incident.alert_id,
          source=incident.source,
        ),
      )

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ):
      reference = incident.provider_workflow_reference or incident.external_reference
      self.pull_attempts.append((incident.event_id, provider, reference))
      if incident.alert_id != "guarded-live:market-data:5m":
        return None
      return OperatorIncidentProviderPullSync(
        provider="pagerduty",
        workflow_reference="PDINC-PULL-API-1",
        external_reference="guarded-live:market-data:5m",
        workflow_state="acknowledged",
        remediation_state="provider_recovered",
        detail="provider authoritatively completed recovery job",
        payload={
          "job_id": "pd-job-api-1",
          "channels": ["kline", "depth"],
          "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
          "market_context_provenance": {
            "provider": "pagerduty",
            "vendor_field": "custom_details",
            "symbols": {
              "scope": "provider_payload",
              "path": "custom_details.market_context.symbols",
            },
            "timeframe": {
              "scope": "provider_payload",
              "path": "custom_details.market_context.timeframe",
            },
          },
          "verification": {"state": "passed"},
          "status_machine": {
            "state": "provider_running",
            "workflow_state": "acknowledged",
            "workflow_action": "remediate",
            "job_state": "completed",
            "sync_state": "provider_authoritative",
          },
        },
        synced_at=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
      )

  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    pull_adapter = FakeProviderPullSyncAdapter()
    app._operator_alert_delivery = pull_adapter
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "provider_pull_sync_surface"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "provider_pull_sync_surface"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "provider_pull_sync_surface",
      },
    )
    assert live_response.status_code == 200
    market_data = StatusOverrideSeededMarketDataAdapter()
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
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 10, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
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
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )
    app._market_data = market_data

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    opened_incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert opened_incident["remediation"]["state"] == "executed"
    assert opened_incident["remediation"]["provider_recovery"]["job_id"] == "pd-job-api-1"
    assert opened_incident["remediation"]["provider_recovery"]["provider_schema_kind"] == "pagerduty"
    assert opened_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_id"] == "PDINC-PULL-API-1"
    assert opened_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_status"] == "acknowledged"
    assert opened_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_state"] == "acknowledged"
    assert opened_incident["remediation"]["provider_recovery"]["status_machine"]["sync_state"] == "bidirectional_synced"
    assert opened_incident["remediation"]["provider_recovery"]["market_context_provenance"]["provider"] == "pagerduty"
    assert (
      opened_incident["remediation"]["provider_recovery"]["market_context_provenance"]["symbols"]["path"]
      == "custom_details.market_context.symbols"
    )
    assert any(
      event["kind"] == "incident_resolved" and event["alert_id"] == "guarded-live:market-data:5m"
      for event in guarded_live_response.json()["incident_events"]
    )
    assert all(
      alert["alert_id"] != "guarded-live:market-data:5m"
      for alert in guarded_live_response.json()["active_alerts"]
    )
    assert any(
      event["kind"] == "guarded_live_incident_provider_pull_synced"
      for event in guarded_live_response.json()["audit_events"]
    )
    assert any(
      attempt[0] == opened_incident["event_id"] and attempt[1] == "pagerduty"
      for attempt in pull_adapter.pull_attempts
    )


def test_operator_visibility_endpoint_surfaces_channel_level_market_data_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "channel_level_incident_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("trade_ticks", "depth_updates", "kline_candles"),
          handed_off_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_trade_event_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_kline_event_at=None,
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=1,
          order_book_rebuild_count=2,
          order_book_last_update_id=34,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          channel_restore_state="unavailable",
          channel_restore_count=2,
          channel_last_restored_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          channel_continuation_state="unavailable",
          channel_continuation_count=2,
          channel_last_continued_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          issues=(
            "binance_order_book_gap_detected:25:29",
            "binance_market_channel_restore_failed:ticker:timeout:exchange timeout",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    consistency_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-channel-consistency:{run_id}"
    )
    assert "trade ticks is stale" in consistency_incident["detail"]
    assert "depth/order-book updates is stale" in consistency_incident["detail"]
    assert "kline candles has not produced any events within 45s" in consistency_incident["detail"]
    restore_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-channel-restore:{run_id}"
    )
    assert "market-channel restore is unavailable." in restore_incident["detail"]
    assert "market-channel continuation is unavailable." in restore_incident["detail"]
    assert "binance ticker restore failed: timeout:exchange timeout." in restore_incident["detail"]
    ladder_integrity_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-integrity:{run_id}"
    )
    assert "binance ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident["detail"]
    assert "binance ladder integrity required 2 snapshot rebuild(s)." in ladder_integrity_incident["detail"]
    assert "binance depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident["detail"]


def test_operator_visibility_endpoint_separates_venue_native_ladder_integrity_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USD",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "venue_native_ladder_integrity_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    owner_session_id = (
      state.ownership.owner_session_id
      or state.session_handoff.owner_session_id
      or "worker-live-coinbase-market"
    )
    app._guarded_live_state.save_state(
      replace(
        state,
        ownership=replace(
          state.ownership,
          state="owned",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
        ),
        session_handoff=replace(
          state.session_handoff,
          state="active",
          venue="coinbase",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
          coverage=("depth_updates",),
          handed_off_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 18, 59, 40, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 18, 59, 50, tzinfo=UTC),
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=1,
          order_book_rebuild_count=1,
          order_book_last_update_id=34,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 18, 59, 45, tzinfo=UTC),
          issues=(
            "coinbase_order_book_gap_detected:25:29",
            "coinbase_order_book_snapshot_failed:session_missing:stream timeout",
            "coinbase_order_book_snapshot_crossed:2501.5:2501.2",
            "coinbase_order_book_snapshot_non_monotonic:bids:2:2501.3:2501.0",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    ladder_integrity_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-integrity:{run_id}"
    )
    assert "coinbase ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident["detail"]
    assert "coinbase ladder integrity required 1 snapshot rebuild(s)." in ladder_integrity_incident["detail"]
    assert "coinbase depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident["detail"]
    assert "snapshot rebuild failed" not in ladder_integrity_incident["detail"]
    venue_ladder_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-venue-ladder-integrity:{run_id}"
    )
    assert "coinbase ladder snapshot rebuild failed during session missing: stream timeout." in venue_ladder_incident["detail"]
    assert "coinbase ladder snapshot is crossed: best bid 2501.50000000 is above best ask 2501.20000000." in venue_ladder_incident["detail"]
    assert "coinbase bid ladder snapshot is not strictly descending at level 2 (2501.30000000 after 2501.00000000)." in venue_ladder_incident["detail"]


def test_operator_visibility_endpoint_separates_ladder_bridge_integrity_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 5, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "exchange_specific_ladder_integrity_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    owner_session_id = (
      state.ownership.owner_session_id
      or state.session_handoff.owner_session_id
      or "worker-live-binance-market"
    )
    app._guarded_live_state.save_state(
      replace(
        state,
        ownership=replace(
          state.ownership,
          state="owned",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
        ),
        session_handoff=replace(
          state.session_handoff,
          state="active",
          venue="binance",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
          coverage=("depth_updates",),
          handed_off_at=datetime(2025, 1, 3, 19, 4, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 19, 4, 40, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 4, 50, tzinfo=UTC),
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=1,
          order_book_rebuild_count=1,
          order_book_last_update_id=34,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 19, 4, 45, tzinfo=UTC),
          issues=(
            "binance_order_book_gap_detected:25:29",
            "binance_order_book_bridge_previous_mismatch:25:29",
            "binance_order_book_bridge_range_mismatch:26:31:34",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    ladder_integrity_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-integrity:{run_id}"
    )
    assert "binance ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident["detail"]
    assert "binance ladder integrity required 1 snapshot rebuild(s)." in ladder_integrity_incident["detail"]
    assert "binance depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident["detail"]
    assert "bridge expected previous update id" not in ladder_integrity_incident["detail"]
    bridge_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-bridge:{run_id}"
    )
    assert "binance depth bridge expected previous update id 25 but received 29." in bridge_incident["detail"]
    assert "binance depth bridge range 31-34 does not cover expected next update id 26." in bridge_incident["detail"]


def test_operator_visibility_endpoint_separates_ladder_sequence_and_snapshot_refresh_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 6, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USD",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "ladder_sequence_snapshot_refresh_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    owner_session_id = (
      state.ownership.owner_session_id
      or state.session_handoff.owner_session_id
      or "worker-live-coinbase-sequence"
    )
    app._guarded_live_state.save_state(
      replace(
        state,
        ownership=replace(
          state.ownership,
          state="owned",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
        ),
        session_handoff=replace(
          state.session_handoff,
          state="active",
          venue="coinbase",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
          coverage=("depth_updates",),
          handed_off_at=datetime(2025, 1, 3, 19, 5, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 19, 5, 40, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 5, 50, tzinfo=UTC),
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=0,
          order_book_rebuild_count=1,
          order_book_last_update_id=704,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 19, 5, 45, tzinfo=UTC),
          issues=(
            "coinbase_order_book_sequence_mismatch:701:703:704",
            "coinbase_order_book_snapshot_refresh:700:701",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    sequence_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-sequence:{run_id}"
    )
    assert "coinbase ladder sequence expected previous update id 701 but received 703 before update 704." in sequence_incident["detail"]
    snapshot_refresh_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-snapshot-refresh:{run_id}"
    )
    assert "coinbase ladder snapshot refresh replaced update id 700 with 701." in snapshot_refresh_incident["detail"]


def test_operator_visibility_endpoint_surfaces_book_and_kline_consistency_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "book_kline_consistency_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("book_ticker", "depth_updates", "kline_candles"),
          last_sync_at=datetime(2025, 1, 3, 19, 30, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          last_book_ticker_event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          last_kline_event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
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
            event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          ),
          kline_snapshot=GuardedLiveKlineChannelSnapshot(
            timeframe="1m",
            open_at=datetime(2025, 1, 3, 19, 25, tzinfo=UTC),
            close_at=datetime(2025, 1, 3, 19, 24, tzinfo=UTC),
            open_price=2499.5,
            high_price=2500.0,
            low_price=2499.0,
            close_price=2501.0,
            volume=4.2,
            closed=True,
            event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    book_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-book-consistency:{run_id}"
    )
    assert "binance local order book is crossed: best bid 2501.20000000 is above best ask 2500.80000000." in book_incident["detail"]
    assert "binance book-ticker quote is crossed: bid 2501.10000000 is above ask 2500.90000000." in book_incident["detail"]
    assert "binance local best bid 2501.20000000 is above book-ticker ask 2500.90000000." in book_incident["detail"]
    kline_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-kline-consistency:{run_id}"
    )
    assert "binance kline timeframe 1m does not match the guarded-live timeframe 5m." in kline_incident["detail"]
    assert "binance kline closes at" in kline_incident["detail"]
    assert "binance kline close 2501.00000000 falls outside the high/low range 2499.00000000-2500.00000000." in kline_incident["detail"]


def test_operator_visibility_endpoint_splits_depth_ladder_and_candle_sequence_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "depth_ladder_candle_sequence_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("depth_updates", "kline_candles"),
          last_sync_at=datetime(2025, 1, 3, 20, 0, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 59, 55, tzinfo=UTC),
          last_kline_event_at=datetime(2025, 1, 3, 19, 59, 55, tzinfo=UTC),
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
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    depth_ladder_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-depth-ladder:{run_id}"
    )
    assert "binance bid ladder count 2 does not match stored bid level count 3." in depth_ladder_incident["detail"]
    assert "binance best bid ladder head 2501.00000000/0.50000000 does not match stored best bid 2501.20000000/1.00000000." in depth_ladder_incident["detail"]
    assert "binance bid ladder is not strictly descending at level 2 (2501.30000000 after 2501.00000000)." in depth_ladder_incident["detail"]
    candle_sequence_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-candle-sequence:{run_id}"
    )
    assert "binance kline open 2025-01-03T19:26:00+00:00 is not aligned to the 5m timeframe boundary." in candle_sequence_incident["detail"]
    assert "binance kline close 2025-01-03T19:29:00+00:00 does not match the expected 5m boundary close 2025-01-03T19:31:00+00:00." in candle_sequence_incident["detail"]
    assert "binance closed kline event arrived at 2025-01-03T19:28:00+00:00 before the candle close 2025-01-03T19:29:00+00:00." in candle_sequence_incident["detail"]


