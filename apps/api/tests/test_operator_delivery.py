from __future__ import annotations

import json
from datetime import UTC
from datetime import datetime

from akra_trader.adapters.operator_delivery import OperatorAlertDeliveryAdapter
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
  assert '"job_id": "pd-job-1"' in remediate_payload["note"]["content"]
  assert '"channels": ["kline", "depth"]' in remediate_payload["note"]["content"]
  assert incident.remediation.provider_recovery.status_machine.state == "not_requested"


def test_operator_alert_delivery_adapter_pulls_pagerduty_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
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
              "remediation_state": "provider_recovered",
              "remediation_provider_payload": {
                "job_id": "pd-job-9",
                "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                "verification": {"state": "passed"},
              },
              "remediation_provider_recovery": {
                "lifecycle_state": "recovered",
                "job_id": "pd-job-9",
                "channels": ["depth", "kline"],
                "symbols": ["ETH/USDT"],
                "timeframe": "5m",
                "verification_state": "passed",
                "status_machine_state": "provider_running",
                "status_machine_workflow_state": "acknowledged",
                "status_machine_job_state": "completed",
              },
            },
          }
        }
      ).encode("utf-8"),
    )

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagerduty",),
    pagerduty_api_token="pagerduty-api-token",
    pagerduty_from_email="akra-ops@example.com",
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
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert requests[0][0].endswith("/incidents/PDINC-123")
  assert requests[0][1] == "GET"
  assert requests[0][2]["From"] == "akra-ops@example.com"


def test_operator_alert_delivery_adapter_supports_opsgenie_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("opsgenie",),
    opsgenie_api_key="opsgenie-key",
    opsgenie_api_url="https://api.opsgenie.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-opsgenie-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 5, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-opsgenie-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 6, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("opsgenie_alerts",)
  assert opened_records[0].target == "opsgenie_alerts"
  assert opened_records[0].external_provider == "opsgenie"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.opsgenie.example/v2/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "GenieKey opsgenie-key"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alias"] == "guarded-live:worker-failed:run-1"
  assert create_payload["priority"] == "P1"

  assert resolve_request[0].endswith(
    "/v2/alerts/guarded-live%3Aworker-failed%3Arun-1/close?identifierType=alias"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_opsgenie_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("opsgenie",),
    opsgenie_api_key="opsgenie-key",
    opsgenie_api_url="https://api.opsgenie.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-opsgenie-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 10, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="opsgenie",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="OG-123",
    escalation_level=3,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="opsgenie",
        job_id="og-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsgenie",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsgenie",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsgenie",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "og-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsgenie",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "og-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("opsgenie",)
  assert acknowledge[0].target == "opsgenie_workflow"
  assert acknowledge[0].external_reference == "OG-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v2/alerts/OG-123/acknowledge?identifierType=id")
  assert requests[0][1] == "POST"
  assert requests[1][0].endswith("/v2/alerts/OG-123/notes?identifierType=id")
  assert requests[2][0].endswith("/v2/alerts/OG-123/close?identifierType=id")
  assert requests[3][0].endswith("/v2/alerts/OG-123/notes?identifierType=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  assert "level 3" in escalate_payload["note"]
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "og-job-2"' in remediate_payload["note"]
  assert '"job_id": "og-job-1"' in resolve_payload["note"]
  assert incident.remediation.provider_recovery.status_machine.state == "not_requested"


def test_operator_alert_delivery_adapter_pulls_opsgenie_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    return FakeResponse(
      200,
      json.dumps(
        {
          "data": {
            "id": "OG-123",
            "alias": "guarded-live:market-data:5m",
            "status": "acknowledged",
            "message": "Guarded-live market-data incident",
            "updatedAt": "2025-01-03T14:12:00Z",
            "details": {
              "remediation_state": "requested",
              "remediation_provider_payload": {
                "job_id": "og-job-7",
                "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
              },
              "remediation_provider_recovery": {
                "lifecycle_state": "recovering",
                "job_id": "og-job-7",
                "channels": ["kline"],
                "symbols": ["ETH/USDT"],
                "timeframe": "5m",
                "status_machine_state": "provider_requested",
                "status_machine_workflow_state": "acknowledged",
                "status_machine_job_state": "requested",
              },
            },
          }
        }
      ).encode("utf-8"),
    )

  adapter = OperatorAlertDeliveryAdapter(
    targets=("opsgenie",),
    opsgenie_api_key="opsgenie-key",
    opsgenie_api_url="https://api.opsgenie.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-opsgenie-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 10, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="opsgenie",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="OG-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="opsgenie",
  )

  assert snapshot is not None
  assert snapshot.provider == "opsgenie"
  assert snapshot.workflow_reference == "OG-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "requested"
  assert snapshot.payload["job_id"] == "og-job-7"
  assert snapshot.payload["channels"] == ["kline"]
  assert snapshot.payload["status_machine"]["job_state"] == "requested"
  assert requests[0][0].endswith("/v2/alerts/OG-123?identifierType=id")
  assert requests[0][1] == "GET"
