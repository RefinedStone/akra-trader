from __future__ import annotations

import json
from datetime import UTC
from datetime import datetime

from akra_trader.adapters.operator_delivery import OperatorAlertDeliveryAdapter
from akra_trader.domain.models import OperatorAlertPrimaryFocus
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderRecoveryState
from akra_trader.domain.models import OperatorIncidentProviderRecoveryVerification
from akra_trader.domain.models import OperatorIncidentRemediation


class FakeResponse:
  def __init__(self, status: int, body: bytes | None = None) -> None:
    self.status = status
    self._body = body or b""

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc, tb) -> None:
    return None

  def read(self) -> bytes:
    return self._body


def test_operator_alert_delivery_adapter_supports_slack_and_pagerduty_targets() -> None:
  requests: list[tuple[str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("slack", "pagerduty"),
    slack_webhook_url="https://hooks.slack.example/services/ops",
    pagerduty_integration_key="pagerduty-key",
    webhook_timeout_seconds=9,
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-1",
    alert_id="guarded-live:worker-failed:run-1:session-1",
    timestamp=datetime(2025, 1, 3, 13, 30, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
    run_id="run-1",
    session_id="session-1",
  )

  records = adapter.deliver(incident=incident, attempt_number=2)

  assert adapter.list_targets() == ("slack_webhook", "pagerduty_events")
  assert [record.target for record in records] == ["slack_webhook", "pagerduty_events"]
  assert all(record.status == "delivered" for record in records)
  assert all(record.attempt_number == 2 for record in records)
  assert all(record.phase == "initial" for record in records)
  pagerduty_record = next(record for record in records if record.target == "pagerduty_events")
  assert pagerduty_record.external_provider == "pagerduty"
  assert pagerduty_record.external_reference == incident.alert_id

  slack_request = next(item for item in requests if "slack.example" in item[0])
  pagerduty_request = next(item for item in requests if "pagerduty.com" in item[0])

  slack_payload = json.loads(slack_request[1].decode("utf-8"))
  pagerduty_payload = json.loads(pagerduty_request[1].decode("utf-8"))

  assert slack_payload["text"] == "[CRITICAL] Guarded-live worker failed for ETH/USDT."
  assert "live worker crash" in slack_payload["blocks"][0]["text"]["text"]
  assert pagerduty_payload["routing_key"] == "pagerduty-key"
  assert pagerduty_payload["event_action"] == "trigger"
  assert pagerduty_payload["dedup_key"] == incident.alert_id
  assert pagerduty_payload["payload"]["severity"] == "critical"


def test_operator_alert_delivery_adapter_resolves_pagerduty_incident_resolution() -> None:
  requests: list[bytes] = []

  def fake_urlopen(request, timeout: float):
    requests.append(request.data)
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagerduty",),
    pagerduty_integration_key="pagerduty-key",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-resolved-1",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 13, 35, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation cleared",
  )

  records = adapter.deliver(incident=incident)

  assert records[0].target == "pagerduty_events"
  assert records[0].status == "delivered"
  payload = json.loads(requests[0].decode("utf-8"))
  assert payload["event_action"] == "resolve"
  assert payload["payload"]["severity"] == "warning"


def test_operator_alert_delivery_adapter_carries_primary_focus_market_context_to_webhook_and_provider_payloads() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data or b"", dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("webhook", "rootly"),
    webhook_url="https://ops.example.com/alert",
    rootly_api_token="rootly-token",
    rootly_api_url="https://api.rootly.example",
    webhook_timeout_seconds=9,
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-market-context-1",
    alert_id="guarded-live:market-data:multi-symbol",
    timestamp=datetime(2025, 1, 3, 13, 45, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data freshness degraded across focused symbols.",
    detail="market-data freshness degraded",
    run_id="run-ops-1",
    session_id="session-ops-1",
    symbols=("BTC/USDT", "ETH/USDT"),
    timeframe="5m",
    primary_focus=OperatorAlertPrimaryFocus(
      symbol="BTC/USDT",
      timeframe="5m",
      candidate_symbols=("BTC/USDT", "ETH/USDT"),
      candidate_count=2,
      policy="market_data_risk_order",
      reason="Selected BTC/USDT as the highest-risk market-data candidate from 2 symbols.",
    ),
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      owner="provider",
      provider="rootly",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="rootly",
        job_id="rt-job-market-context-1",
        channels=("depth", "kline"),
        symbols=("BTC/USDT", "ETH/USDT"),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  records = adapter.deliver(incident=incident)

  assert [record.target for record in records] == ["operator_webhook", "rootly_incidents"]

  webhook_request = next(item for item in requests if item[0] == "https://ops.example.com/alert")
  rootly_request = next(
    item for item in requests if item[0] == "https://api.rootly.example/v1/incidents"
  )

  webhook_payload = json.loads(webhook_request[2].decode("utf-8"))
  assert webhook_payload["symbol"] == "BTC/USDT"
  assert webhook_payload["symbols"] == ["BTC/USDT", "ETH/USDT"]
  assert webhook_payload["timeframe"] == "5m"
  assert webhook_payload["primary_focus"] == {
    "symbol": "BTC/USDT",
    "timeframe": "5m",
    "candidate_symbols": ["BTC/USDT", "ETH/USDT"],
    "candidate_count": 2,
    "policy": "market_data_risk_order",
    "reason": "Selected BTC/USDT as the highest-risk market-data candidate from 2 symbols.",
  }
  assert webhook_payload["remediation"]["provider_recovery"]["symbol"] == "BTC/USDT"
  assert (
    webhook_payload["remediation"]["provider_recovery"]["primary_focus"]
    == webhook_payload["primary_focus"]
  )

  rootly_payload = json.loads(rootly_request[2].decode("utf-8"))
  provider_recovery = rootly_payload["incident"]["metadata"]["remediation_provider_recovery"]
  assert provider_recovery["symbol"] == "BTC/USDT"
  assert provider_recovery["symbols"] == ["BTC/USDT", "ETH/USDT"]
  assert provider_recovery["timeframe"] == "5m"
  assert provider_recovery["primary_focus"] == webhook_payload["primary_focus"]


def test_operator_alert_delivery_adapter_restores_primary_focus_market_context_from_provider_pull_payload() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.pagerduty.com/incidents/PDINC-PRIMARY-1":
      return FakeResponse(
        200,
        json.dumps(
          {
            "incident": {
              "id": "PDINC-PRIMARY-1",
              "incident_key": "guarded-live:market-data:5m",
              "status": "acknowledged",
              "title": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T14:05:00Z",
              "custom_details": {
                "remediation_state": "provider_recovered",
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovered",
                  "job_id": "pd-job-primary-1",
                  "channels": ["depth", "kline"],
                  "symbol": "btc/usdt",
                  "symbols": ["btc/usdt", "eth/usdt"],
                  "timeframe": "5M",
                  "primary_focus": {
                    "symbol": "btc/usdt",
                    "timeframe": "5M",
                    "candidate_symbols": ["btc/usdt", "eth/usdt"],
                    "candidate_count": 2,
                    "policy": "market_data_risk_order",
                    "reason": "Selected BTC/USDT as the highest-risk market-data candidate from 2 symbols.",
                  },
                  "verification_state": "passed",
                },
              },
            }
          }
        ).encode("utf-8"),
      )
    raise AssertionError(f"unexpected request: {request.full_url}")

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagerduty",),
    pagerduty_api_token="pagerduty-api-token",
    pagerduty_from_email="akra-ops@example.com",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-primary-focus-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 6, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="pagerduty",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="PDINC-PRIMARY-1",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="pagerduty",
  )

  assert snapshot is not None
  assert snapshot.payload["symbol"] == "BTC/USDT"
  assert snapshot.payload["symbols"] == ["BTC/USDT", "ETH/USDT"]
  assert snapshot.payload["timeframe"] == "5m"
  assert snapshot.payload["primary_focus"] == {
    "symbol": "BTC/USDT",
    "timeframe": "5m",
    "candidate_symbols": ["BTC/USDT", "ETH/USDT"],
    "candidate_count": 2,
    "policy": "market_data_risk_order",
    "reason": "Selected BTC/USDT as the highest-risk market-data candidate from 2 symbols.",
  }
  assert snapshot.payload["targets"]["symbol"] == "BTC/USDT"
  assert snapshot.payload["targets"]["symbols"] == ["BTC/USDT", "ETH/USDT"]
  assert snapshot.payload["targets"]["timeframe"] == "5m"
  assert snapshot.payload["targets"]["primary_focus"] == snapshot.payload["primary_focus"]
  assert snapshot.payload["market_context_provenance"] == {
    "provider": "pagerduty",
    "vendor_field": "custom_details",
    "symbol": {
      "scope": "provider_recovery",
      "path": "custom_details.remediation_provider_recovery.symbol",
    },
    "symbols": {
      "scope": "provider_recovery",
      "path": "custom_details.remediation_provider_recovery.symbols",
    },
    "timeframe": {
      "scope": "provider_recovery",
      "path": "custom_details.remediation_provider_recovery.timeframe",
    },
    "primary_focus": {
      "scope": "provider_recovery",
      "path": "custom_details.remediation_provider_recovery.primary_focus",
    },
  }
  assert requests[0][2]["From"] == "akra-ops@example.com"


def test_operator_alert_delivery_adapter_syncs_pagerduty_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagerduty",),
    pagerduty_integration_key="pagerduty-key",
    pagerduty_api_token="pagerduty-api-token",
    pagerduty_from_email="akra-ops@example.com",
    webhook_timeout_seconds=9,
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 0, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="pagerduty",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="PDINC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="pagerduty",
        job_id="pd-job-1",
        channels=("kline", "depth"),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="pagerduty",
    action="acknowledge",
    actor="operator",
    detail="triaged_by_on_call",
    attempt_number=2,
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="pagerduty",
    action="escalate",
    actor="operator",
    detail="handoff_to_manager",
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="pagerduty",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={
      "job_id": "pd-job-1",
      "channels": ["kline", "depth"],
      "verification": {"state": "passed"},
      "market_context": {
        "symbol": "ETH/USDT",
        "symbols": ["ETH/USDT"],
        "timeframe": "5m",
        "primary_focus": {
          "symbol": "ETH/USDT",
          "timeframe": "5m",
          "candidate_symbols": ["ETH/USDT"],
          "candidate_count": 1,
          "policy": "single_symbol_context",
          "reason": "Single-symbol remediation for ETH/USDT.",
        },
      },
    },
  )

  assert adapter.list_supported_workflow_providers() == ("pagerduty",)
  assert acknowledge[0].target == "pagerduty_workflow"
  assert acknowledge[0].provider_action == "acknowledge"
  assert acknowledge[0].external_reference == "PDINC-123"
  assert acknowledge[0].attempt_number == 2
  assert escalate[0].provider_action == "escalate"
  assert remediate[0].provider_action == "remediate"

  acknowledge_request = requests[0]
  escalate_request = requests[1]
  remediate_request = requests[2]
  assert acknowledge_request[0].endswith("/incidents/PDINC-123")
  assert acknowledge_request[1] == "PUT"
  assert acknowledge_request[3]["From"] == "akra-ops@example.com"
  acknowledge_payload = json.loads(acknowledge_request[2].decode("utf-8"))
  assert acknowledge_payload["incident"]["status"] == "acknowledged"

  assert escalate_request[0].endswith("/incidents/PDINC-123/notes")
  assert escalate_request[1] == "POST"
  escalate_payload = json.loads(escalate_request[2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]["content"]
  assert remediate_request[0].endswith("/incidents/PDINC-123/notes")
  remediate_payload = json.loads(remediate_request[2].decode("utf-8"))
  assert "requested remediation" in remediate_payload["note"]["content"]
  assert "market_data.sync_recent" in remediate_payload["note"]["content"]
  assert remediate_payload["custom_details"]["market_context"]["symbol"] == "ETH/USDT"
  assert remediate_payload["custom_details"]["market_context"]["timeframe"] == "5m"
  assert "Market context:" in remediate_payload["note"]["content"]
  assert '"symbol": "ETH/USDT"' in remediate_payload["note"]["content"]
  assert '"timeframe": "5m"' in remediate_payload["note"]["content"]
  assert '"job_id": "pd-job-1"' in remediate_payload["note"]["content"]
  assert '"channels": ["kline", "depth"]' in remediate_payload["note"]["content"]
  assert incident.remediation.provider_recovery.status_machine.state == "not_requested"


def test_operator_alert_delivery_adapter_pulls_pagerduty_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.pagerduty.com/incidents/PDINC-123":
      return FakeResponse(
        200,
        json.dumps(
          {
            "incident": {
              "id": "PDINC-123",
              "incident_key": "guarded-live:market-data:5m",
              "status": "acknowledged",
              "title": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T14:05:00Z",
              "custom_details": {
                "market_context": {
                  "symbol": "eth/usdt",
                  "symbols": ["eth/usdt"],
                  "timeframe": "5M",
                  "primary_focus": {
                    "symbol": "eth/usdt",
                    "timeframe": "5M",
                    "candidate_symbols": ["eth/usdt"],
                    "candidate_count": 1,
                    "policy": "single_symbol_context",
                    "reason": "Alert context resolved to one market-data instrument.",
                  },
                },
                "remediation_state": "provider_recovered",
                "remediation_provider_payload": {
                  "job_id": "pd-job-9",
                  "verification": {"state": "passed"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovered",
                  "job_id": "pd-job-9",
                  "channels": ["depth", "kline"],
                  "verification_state": "passed",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "completed",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "completed",
                  "progress_percent": 60,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "provider incident body still lagging",
                  "external_run_id": "pd-body-9",
                },
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://pagerduty-engine.example/recovery/pd-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "completed",
              "progress_percent": 100,
              "attempt_count": 2,
              "current_step": "verification",
              "last_message": "provider engine completed verification",
              "external_run_id": "pd-engine-9",
              "updated_at": "2025-01-03T14:06:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(
      404,
    )

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagerduty",),
    pagerduty_api_token="pagerduty-api-token",
    pagerduty_from_email="akra-ops@example.com",
    pagerduty_recovery_engine_url_template="https://pagerduty-engine.example/recovery/{job_id_urlencoded}",
    pagerduty_recovery_engine_token="pagerduty-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-pagerduty-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 0, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="pagerduty",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="PDINC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="pagerduty",
  )

  assert snapshot is not None
  assert snapshot.provider == "pagerduty"
  assert snapshot.workflow_reference == "PDINC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "provider_recovered"
  assert snapshot.payload["job_id"] == "pd-job-9"
  assert snapshot.payload["symbol"] == "ETH/USDT"
  assert snapshot.payload["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["timeframe"] == "5m"
  assert snapshot.payload["market_context_provenance"] == {
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
  }
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["primary_focus"]["symbol"] == "ETH/USDT"
  assert snapshot.payload["primary_focus"]["policy"] == "single_symbol_context"
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "pagerduty"
  assert snapshot.payload["provider_schema"]["pagerduty"]["incident_id"] == "PDINC-123"
  assert snapshot.payload["provider_schema"]["pagerduty"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["pagerduty"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["pagerduty"]["phase_graph"]["workflow_phase"] == "awaiting_local_verification"
  assert snapshot.payload["provider_schema"]["pagerduty"]["phase_graph"]["responder_phase"] == "engaged"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "completed"
  assert snapshot.payload["telemetry"]["progress_percent"] == 100
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verification"
  assert snapshot.payload["telemetry"]["last_message"] == "provider engine completed verification"
  assert snapshot.payload["telemetry"]["external_run_id"] == "pd-engine-9"
  assert requests[0][0].endswith("/incidents/PDINC-123")
  assert requests[0][1] == "GET"
  assert requests[0][2]["From"] == "akra-ops@example.com"
  assert requests[1][0] == "https://pagerduty-engine.example/recovery/pd-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer pagerduty-recovery-token"
  assert "From" not in requests[1][2]
