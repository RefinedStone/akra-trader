from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.config import Settings
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import GuardedLiveBookTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveKlineChannelSnapshot
from akra_trader.domain.models import GuardedLiveOrderBookLevel
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import Position
from akra_trader.domain.models import SyncFailure
from akra_trader.main import create_app
from akra_trader.adapters.venue_execution import SeededVenueExecutionAdapter


def build_client(
  database_path: Path,
  *,
  guarded_live_execution_enabled: bool = False,
  guarded_live_venue: str | None = None,
  operator_alert_external_sync_token: str | None = None,
) -> TestClient:
  settings = Settings(
    runs_database_url=f"sqlite:///{database_path}",
    market_data_provider="seeded",
    guarded_live_execution_enabled=guarded_live_execution_enabled,
    guarded_live_venue=guarded_live_venue,
    operator_alert_external_sync_token=operator_alert_external_sync_token,
  )
  return TestClient(create_app(settings))


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


def test_list_strategies_returns_builtin_strategy(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.get("/api/strategies")
  assert response.status_code == 200
  payload = response.json()
  assert payload[0]["strategy_id"] == "ma_cross_v1"
  assert payload[0]["lifecycle"]["stage"] == "active"
  assert payload[0]["version_lineage"] == ["1.0.0"]
  assert payload[0]["supported_timeframes"] == ["5m", "1h"]


def test_list_strategies_can_filter_by_lane_and_lifecycle_stage(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/strategies?lane=freqtrade_reference&lifecycle_stage=imported")

  assert response.status_code == 200
  payload = response.json()
  assert payload
  assert all(item["runtime"] == "freqtrade_reference" for item in payload)
  assert all(item["lifecycle"]["stage"] == "imported" for item in payload)


def test_list_references_returns_catalog_entries(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.get("/api/references")
  assert response.status_code == 200
  payload = response.json()
  assert any(item["reference_id"] == "nautilus-trader" for item in payload)
  assert any(item["reference_id"] == "nostalgia-for-infinity" for item in payload)


def test_backtest_endpoint_returns_run_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["status"] == "completed"
  assert payload["config"]["strategy_id"] == "ma_cross_v1"
  assert payload["provenance"]["strategy"]["strategy_id"] == "ma_cross_v1"
  assert payload["provenance"]["strategy"]["lifecycle"]["stage"] == "active"
  assert payload["provenance"]["strategy"]["parameter_snapshot"]["requested"] == {}
  assert payload["provenance"]["strategy"]["parameter_snapshot"]["resolved"] == {
    "short_window": 8,
    "long_window": 21,
  }
  assert payload["provenance"]["strategy"]["warmup"]["required_bars"] == 21
  assert payload["provenance"]["strategy"]["warmup"]["timeframes"] == ["5m"]
  assert payload["provenance"]["market_data"]["provider"] == "seeded"
  assert payload["provenance"]["market_data"]["dataset_identity"].startswith("dataset-v1:")
  assert payload["provenance"]["market_data"]["sync_checkpoint_id"] is None
  assert payload["provenance"]["market_data"]["reproducibility_state"] == "pinned"
  assert payload["provenance"]["market_data"]["sync_status"] == "fixture"
  assert payload["provenance"]["rerun_boundary_id"].startswith("rerun-v1:")
  assert payload["provenance"]["rerun_boundary_state"] == "pinned"
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["provider"] == "seeded"
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["dataset_identity"].startswith(
    "candles-v1:"
  )


def test_backtest_run_survives_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"
  client = build_client(database_path)
  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert response.status_code == 200
  run_id = response.json()["config"]["run_id"]

  restarted_client = build_client(database_path)
  restarted_response = restarted_client.get(f"/api/runs/backtests/{run_id}")

  assert restarted_response.status_code == 200
  assert restarted_response.json()["config"]["run_id"] == run_id


def test_sandbox_endpoint_returns_run_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 48,
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["status"] == "running"
  assert payload["config"]["mode"] == "sandbox"
  assert payload["notes"][0].startswith("Sandbox worker session primed from the latest market snapshot using ")
  assert payload["provenance"]["runtime_session"]["worker_kind"] == "sandbox_native_worker"
  assert payload["provenance"]["runtime_session"]["lifecycle_state"] == "active"
  assert payload["provenance"]["runtime_session"]["primed_candle_count"] == 48
  assert payload["provenance"]["runtime_session"]["processed_tick_count"] == 1
  assert payload["provenance"]["runtime_session"]["recovery_count"] == 0
  assert (
    payload["provenance"]["runtime_session"]["last_processed_candle_at"]
    == payload["provenance"]["market_data"]["effective_end_at"]
  )
  assert (
    payload["provenance"]["runtime_session"]["last_seen_candle_at"]
    == payload["provenance"]["market_data"]["effective_end_at"]
  )


def test_paper_alias_still_works(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/paper",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["config"]["mode"] == "paper"
  assert payload["notes"][0].startswith("Paper session primed from the latest market snapshot using ")
  assert all("Sandbox preview replayed" not in note for note in payload["notes"])
  assert payload["provenance"]["runtime_session"] is None


def test_sandbox_worker_recovers_running_session_after_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path) as first_client:
    response = first_client.post(
      "/api/runs/sandbox",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
      },
    )
    assert response.status_code == 200
    run_id = response.json()["config"]["run_id"]

  with build_client(database_path) as restarted_client:
    restarted_response = restarted_client.get(f"/api/runs/backtests/{run_id}")

  assert restarted_response.status_code == 200
  payload = restarted_response.json()
  assert payload["config"]["mode"] == "sandbox"
  assert payload["provenance"]["runtime_session"]["recovery_count"] >= 1
  assert payload["provenance"]["runtime_session"]["last_recovery_reason"] == "process_restart"
  assert payload["provenance"]["runtime_session"]["processed_tick_count"] == 1
  assert any("sandbox_worker_recovered | process_restart" in note for note in payload["notes"])


def test_market_data_status_endpoint_returns_status_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/market-data/status")

  assert response.status_code == 200
  payload = response.json()
  assert payload["provider"] == "seeded"
  assert payload["instruments"]
  assert "sync_status" in payload["instruments"][0]
  assert payload["instruments"][0]["sync_checkpoint"] is None
  assert payload["instruments"][0]["recent_failures"] == []
  assert payload["instruments"][0]["failure_count_24h"] == 0
  assert payload["instruments"][0]["backfill_target_candles"] is None
  assert payload["instruments"][0]["backfill_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_contiguous_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_missing_candles"] is None
  assert payload["instruments"][0]["backfill_gap_windows"] == []


def test_operator_visibility_endpoint_reports_stale_runtime_alerts(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    clock = lambda: datetime(2025, 1, 3, 13, 0, tzinfo=UTC)
    app._clock = clock
    app._sandbox_worker_heartbeat_timeout_seconds = 15
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
    app._clock = lambda: datetime(2025, 1, 3, 13, 0, 20, tzinfo=UTC)

    response = client.get("/api/operator/visibility")

  assert response.status_code == 200
  payload = response.json()
  assert payload["alerts"][0]["category"] == "stale_runtime"
  assert payload["alerts"][0]["severity"] == "warning"
  assert payload["audit_events"][0]["kind"] == "sandbox_worker_stale"


def test_operator_visibility_endpoint_reports_worker_failures(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
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

    def fail_worker(*, run):
      raise RuntimeError("worker crash")

    app._load_sandbox_worker_candles = fail_worker
    app.maintain_sandbox_worker_sessions()

    response = client.get("/api/operator/visibility")

  assert response.status_code == 200
  payload = response.json()
  assert payload["alerts"][0]["category"] == "worker_failure"
  assert payload["alerts"][0]["severity"] == "critical"
  assert any(event["kind"] == "sandbox_worker_failed" for event in payload["audit_events"])


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

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    assert any(event["alert_id"] == "guarded-live:market-data:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-quality:binance:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-continuity:binance:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-venue:binance:5m" for event in incident_events)
    assert any(event["alert_id"].startswith("guarded-live:risk-breach:") for event in incident_events)


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
          "verification": {"state": "passed"},
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


def test_live_endpoints_use_configured_supported_guarded_live_venue(tmp_path: Path) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    guarded_live_venue="coinbase",
  ) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="coinbase",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),
        ),
      )
    )
    app._venue_execution = SeededVenueExecutionAdapter(venue="coinbase")

    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "coinbase_pre_live_check"},
    )
    assert reconcile_response.status_code == 200
    assert reconcile_response.json()["reconciliation"]["venue_snapshot"]["venue"] == "coinbase"

    recovery_response = client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "coinbase_pre_live_recovery"},
    )
    assert recovery_response.status_code == 200
    recovery_payload = recovery_response.json()
    assert recovery_payload["recovery"]["exposures"][0]["instrument_id"] == "coinbase:ETH/USDT"

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
        "operator_reason": "coinbase_guarded_live_launch",
      },
    )

  assert live_response.status_code == 200
  payload = live_response.json()
  assert payload["config"]["mode"] == "live"
  assert payload["config"]["venue"] == "coinbase"


def test_live_run_payload_exposes_synced_order_lifecycle(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    venue_execution = app._venue_execution
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 0, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

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
        "operator_reason": "sync_payload_test",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    venue_execution.set_order_state(
      "venue-open-order-1",
      symbol="ETH/USDT",
      side="buy",
      amount=0.5,
      status="partially_filled",
      average_fill_price=2_010.0,
      fee_paid=0.2,
      filled_amount=0.2,
      remaining_amount=0.3,
    )
    app.maintain_guarded_live_worker_sessions()

    runs_response = client.get("/api/runs?mode=live")

  assert runs_response.status_code == 200
  payload = runs_response.json()
  assert len(payload) == 1
  live_run = payload[0]
  assert live_run["config"]["run_id"] == run_id
  assert live_run["orders"][0]["status"] == "partially_filled"
  assert live_run["orders"][0]["filled_quantity"] == 0.2
  assert live_run["orders"][0]["remaining_quantity"] == 0.3
  assert live_run["orders"][0]["last_synced_at"] is not None


def test_live_order_cancel_endpoint_marks_active_order_canceled(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 30, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
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
        "operator_reason": "cancel_payload_test",
      },
    )
    run_id = live_response.json()["config"]["run_id"]

    cancel_response = client.post(
      f"/api/runs/live/{run_id}/orders/venue-open-order-1/cancel",
      json={"actor": "operator", "reason": "reduce_venue_risk"},
    )

  assert cancel_response.status_code == 200
  payload = cancel_response.json()
  assert payload["orders"][0]["order_id"] == "venue-open-order-1"
  assert payload["orders"][0]["status"] == "canceled"


def test_live_order_replace_endpoint_appends_repriced_limit_order(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 45, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
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
        "operator_reason": "replace_payload_test",
      },
    )
    run_id = live_response.json()["config"]["run_id"]

    replace_response = client.post(
      f"/api/runs/live/{run_id}/orders/venue-open-order-1/replace",
      json={
        "actor": "operator",
        "reason": "reprice_remaining_order",
        "price": 1985.0,
        "quantity": 0.3,
      },
    )

  assert replace_response.status_code == 200
  payload = replace_response.json()
  assert len(payload["orders"]) == 2
  assert payload["orders"][0]["status"] == "canceled"
  assert payload["orders"][1]["order_type"] == "limit"
  assert payload["orders"][1]["status"] == "open"
  assert payload["orders"][1]["requested_price"] == 1985.0
  assert payload["orders"][1]["quantity"] == 0.3


def test_guarded_live_status_and_resume_expose_ownership_and_order_book(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path, guarded_live_execution_enabled=True) as first_client:
    app = first_client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 21, 0, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )
    first_client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    first_client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
    live_response = first_client.post(
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
        "operator_reason": "owned_session_start",
      },
    )
    run_id = live_response.json()["config"]["run_id"]

    status_response = first_client.get("/api/guarded-live")

  assert status_response.status_code == 200
  status_payload = status_response.json()
  assert status_payload["ownership"]["state"] == "owned"
  assert status_payload["ownership"]["owner_run_id"] == run_id
  assert status_payload["order_book"]["open_orders"][0]["order_id"] == "venue-open-order-1"
  assert status_payload["session_handoff"]["state"] == "active"
  assert status_payload["session_handoff"]["transport"] == "seeded_stream"

  with build_client(database_path, guarded_live_execution_enabled=True) as restarted_client:
    restarted_client.app.state.container.app._venue_execution = SeededVenueExecutionAdapter(
      restored_orders=(
        GuardedLiveVenueOrderResult(
          order_id="venue-open-order-1",
          venue="binance",
          symbol="ETH/USDT",
          side="buy",
          amount=0.5,
          status="partially_filled",
          submitted_at=datetime(2025, 1, 3, 21, 0, tzinfo=UTC),
          updated_at=datetime(2025, 1, 3, 21, 5, tzinfo=UTC),
          requested_price=2_000.0,
          average_fill_price=1_998.0,
          fee_paid=0.2,
          requested_amount=0.5,
          filled_amount=0.2,
          remaining_amount=0.3,
        ),
      )
    )
    resume_response = restarted_client.post(
      "/api/guarded-live/resume",
      json={"actor": "operator", "reason": "process_restart_resume"},
    )
    resumed_status_response = restarted_client.get("/api/guarded-live")

  assert resume_response.status_code == 200
  resume_payload = resume_response.json()
  assert resume_payload["config"]["run_id"] == run_id
  assert resume_payload["status"] == "running"
  assert resume_payload["provenance"]["runtime_session"]["recovery_count"] >= 1
  assert resume_payload["orders"][0]["status"] == "partially_filled"
  assert resume_payload["orders"][0]["filled_quantity"] == 0.2
  assert resume_payload["orders"][0]["remaining_quantity"] == 0.3
  assert resumed_status_response.status_code == 200
  resumed_status_payload = resumed_status_response.json()
  assert resumed_status_payload["session_restore"]["state"] == "restored"
  assert resumed_status_payload["session_restore"]["source"] == "seeded_venue_execution"
  assert resumed_status_payload["session_restore"]["owner_run_id"] == run_id
  assert resumed_status_payload["session_handoff"]["state"] == "active"
  assert resumed_status_payload["session_handoff"]["transport"] == "seeded_stream"
  assert resumed_status_payload["session_handoff"]["owner_run_id"] == run_id
  assert resumed_status_payload["order_book"]["open_orders"][0]["amount"] == 0.3


def test_runs_endpoint_can_filter_by_strategy_version(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  native_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert native_response.status_code == 200

  reference_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "nfi_x7_reference",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert reference_response.status_code == 200

  filtered = client.get("/api/runs?mode=backtest&strategy_id=ma_cross_v1&strategy_version=1.0.0")

  assert filtered.status_code == 200
  payload = filtered.json()
  assert len(payload) == 1
  assert payload[0]["config"]["strategy_id"] == "ma_cross_v1"
  assert payload[0]["config"]["strategy_version"] == "1.0.0"


def test_runs_endpoint_can_filter_by_rerun_boundary_id(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  first_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert first_response.status_code == 200
  rerun_boundary_id = first_response.json()["provenance"]["rerun_boundary_id"]

  second_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert second_response.status_code == 200

  other_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 12000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert other_response.status_code == 200

  filtered = client.get(f"/api/runs?rerun_boundary_id={rerun_boundary_id}")

  assert filtered.status_code == 200
  payload = filtered.json()
  assert len(payload) == 2
  assert all(item["provenance"]["rerun_boundary_id"] == rerun_boundary_id for item in payload)


def test_runs_endpoint_filters_paper_history_separately_from_sandbox(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  sandbox_response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert sandbox_response.status_code == 200

  paper_response = client.post(
    "/api/runs/paper",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert paper_response.status_code == 200

  sandbox_filtered = client.get("/api/runs?mode=sandbox")
  paper_filtered = client.get("/api/runs?mode=paper")

  assert sandbox_filtered.status_code == 200
  assert paper_filtered.status_code == 200
  assert [item["config"]["mode"] for item in sandbox_filtered.json()] == ["sandbox"]
  assert [item["config"]["mode"] for item in paper_filtered.json()] == ["paper"]


def test_rerun_boundary_endpoint_creates_backtest_from_stored_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
      "start_at": "2025-01-01T04:00:00Z",
      "end_at": "2025-01-01T12:00:00Z",
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/backtests")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["run_id"] != source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "matched"
  assert rerun_payload["provenance"]["rerun_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]
  assert rerun_payload["provenance"]["strategy"]["parameter_snapshot"]["resolved"] == {
    "short_window": 13,
    "long_window": 21,
  }


def test_rerun_boundary_endpoint_creates_sandbox_run_from_stored_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/sandbox")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["run_id"] != source_payload["config"]["run_id"]
  assert rerun_payload["config"]["mode"] == "sandbox"
  assert rerun_payload["status"] == "running"
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "matched"
  assert rerun_payload["provenance"]["rerun_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]


def test_rerun_boundary_paper_endpoint_replays_boundary_with_expected_mode_drift(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
      "start_at": "2025-01-01T04:00:00Z",
      "end_at": "2025-01-01T12:00:00Z",
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/paper")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["mode"] == "paper"
  assert rerun_payload["status"] == "running"
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "drifted"
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]


def test_rerun_boundary_endpoint_returns_not_found_for_unknown_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.post("/api/runs/rerun-boundaries/rerun-v1:missing/backtests")

  assert response.status_code == 404

  sandbox_response = client.post("/api/runs/rerun-boundaries/rerun-v1:missing/sandbox")

  assert sandbox_response.status_code == 404


def test_compare_runs_endpoint_returns_native_and_reference_benchmark_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  native_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert native_response.status_code == 200
  native_run_id = native_response.json()["config"]["run_id"]

  reference_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "nfi_x7_reference",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert reference_response.status_code == 200
  reference_run_id = reference_response.json()["config"]["run_id"]

  comparison_response = client.get(
    f"/api/runs/compare?run_id={native_run_id}&run_id={reference_run_id}&intent=strategy_tuning"
  )

  assert comparison_response.status_code == 200
  payload = comparison_response.json()
  assert payload["intent"] == "strategy_tuning"
  assert payload["baseline_run_id"] == native_run_id
  assert [run["lane"] for run in payload["runs"]] == ["native", "reference"]
  assert payload["runs"][1]["reference_id"] == "nostalgia-for-infinity"
  assert payload["runs"][1]["integration_mode"] == "external_runtime"
  assert payload["runs"][1]["reference"]["title"] == "NostalgiaForInfinity"
  assert payload["runs"][1]["artifact_paths"]
  assert len(payload["narratives"]) == 1
  assert payload["narratives"][0]["comparison_type"] == "native_vs_reference"
  assert payload["narratives"][0]["run_id"] == reference_run_id
  assert payload["narratives"][0]["rank"] == 1
  assert payload["narratives"][0]["is_primary"] is True
  assert payload["narratives"][0]["insight_score"] > 0
  assert payload["narratives"][0]["title"].startswith("Strategy tuning")
  artifact_kinds = {artifact["kind"] for artifact in payload["runs"][1]["benchmark_artifacts"]}
  assert "result_snapshot_root" in artifact_kinds
  assert "runtime_log_root" in artifact_kinds
  assert all("summary" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("sections" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("summary_source_path" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  metric_rows = {row["key"]: row for row in payload["metric_rows"]}
  assert metric_rows["total_return_pct"]["annotation"] == (
    "Tuning read: return deltas show optimization edge versus the baseline."
  )
  assert metric_rows["total_return_pct"]["delta_annotations"][native_run_id] == "tuning baseline"
  assert metric_rows["total_return_pct"]["values"][native_run_id] is not None
  assert reference_run_id in metric_rows["trade_count"]["values"]
  assert payload["runs"][1]["notes"]
