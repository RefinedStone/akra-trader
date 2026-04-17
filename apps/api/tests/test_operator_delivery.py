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
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
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


def test_operator_alert_delivery_adapter_supports_rootly_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("rootly",),
    rootly_api_token="rootly-token",
    rootly_api_url="https://api.rootly.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-rootly-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 2, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-rootly-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 3, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("rootly_incidents",)
  assert opened_records[0].target == "rootly_incidents"
  assert opened_records[0].external_provider == "rootly"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.rootly.example/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer rootly-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity_id"] == "sev_critical"
  assert create_payload["incident"]["slug"] == "guarded-live:worker-failed:run-1"

  assert resolve_request[0].endswith(
    "/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_rootly_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("rootly",),
    rootly_api_token="rootly-token",
    rootly_api_url="https://api.rootly.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-rootly-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 4, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="rootly",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="RT-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="rootly",
        job_id="rt-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="rootly",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="rootly",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="rootly",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "rt-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="rootly",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "rt-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("rootly",)
  assert acknowledge[0].target == "rootly_workflow"
  assert acknowledge[0].external_reference == "RT-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v1/incidents/RT-123/acknowledge?identifier_type=id")
  assert requests[0][1] == "POST"
  assert requests[1][0].endswith("/v1/incidents/RT-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v1/incidents/RT-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v1/incidents/RT-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "rt-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "rt-job-2"' in remediate_payload["note"]
  assert incident.remediation.provider_recovery.status_machine.state == "not_requested"


def test_operator_alert_delivery_adapter_pulls_rootly_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.rootly.example/v1/incidents/RT-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "data": {
              "id": "RT-123",
              "attributes": {
                "external_reference": "guarded-live:market-data:5m",
                "status": "acknowledged",
                "title": "Guarded-live market-data incident",
                "updated_at": "2025-01-03T14:14:00Z",
                "severity_id": "sev_critical",
                "private": True,
                "slug": "rt-123",
                "url": "https://rootly.example/incidents/RT-123",
                "acknowledged_at": "2025-01-03T14:13:00Z",
                "metadata": {
                  "remediation_state": "recovering",
                  "remediation_provider_payload": {
                    "job_id": "rt-job-9",
                    "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                    "verification": {"state": "pending"},
                  },
                  "remediation_provider_recovery": {
                    "lifecycle_state": "recovering",
                    "job_id": "rt-job-9",
                    "channels": ["depth", "kline"],
                    "symbols": ["ETH/USDT"],
                    "timeframe": "5m",
                    "status_machine_state": "provider_running",
                    "status_machine_workflow_state": "acknowledged",
                    "status_machine_job_state": "running",
                  },
                  "remediation_provider_telemetry": {
                    "source": "provider_payload",
                    "state": "running",
                    "progress_percent": 40,
                    "attempt_count": 1,
                    "current_step": "incident_body",
                    "last_message": "incident body telemetry is lagging",
                    "external_run_id": "rt-body-9",
                  },
                  "remediation_provider_telemetry_url": "https://rootly-engine.example/recovery/rt-job-9",
                },
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://rootly-engine.example/recovery/rt-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 92,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Rootly engine is verifying restored channels",
              "external_run_id": "rt-engine-9",
              "updated_at": "2025-01-03T14:15:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("rootly",),
    rootly_api_token="rootly-token",
    rootly_api_url="https://api.rootly.example",
    rootly_recovery_engine_url_template="https://rootly-engine.example/recovery/{job_id_urlencoded}",
    rootly_recovery_engine_token="rootly-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-rootly-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 12, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="rootly",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="RT-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="rootly",
  )

  assert snapshot is not None
  assert snapshot.provider == "rootly"
  assert snapshot.workflow_reference == "RT-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "rt-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "rootly"
  assert snapshot.payload["provider_schema"]["rootly"]["incident_id"] == "RT-123"
  assert snapshot.payload["provider_schema"]["rootly"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["rootly"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["rootly"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["rootly"]["phase_graph"]["acknowledgment_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["rootly"]["phase_graph"]["visibility_phase"] == "private"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 92
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Rootly engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "rt-engine-9"
  assert requests[0][0].endswith("/v1/incidents/RT-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer rootly-token"
  assert requests[1][0] == "https://rootly-engine.example/recovery/rt-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer rootly-recovery-token"


def test_operator_alert_delivery_adapter_supports_blameless_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("blameless",),
    blameless_api_token="blameless-token",
    blameless_api_url="https://api.blameless.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-blameless-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 16, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-blameless-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 17, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("blameless_incidents",)
  assert opened_records[0].target == "blameless_incidents"
  assert opened_records[0].external_provider == "blameless"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.blameless.example/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer blameless-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "sev1"
  assert create_payload["incident"]["visibility"] == "private"

  assert resolve_request[0].endswith(
    "/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_blameless_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("blameless",),
    blameless_api_token="blameless-token",
    blameless_api_url="https://api.blameless.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-blameless-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 18, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="blameless",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="BL-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="blameless",
        job_id="bl-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="blameless",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="blameless",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="blameless",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "bl-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="blameless",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "bl-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("blameless",)
  assert acknowledge[0].target == "blameless_workflow"
  assert acknowledge[0].external_reference == "BL-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v1/incidents/BL-123/acknowledge?identifier_type=id")
  assert requests[0][1] == "POST"
  assert requests[1][0].endswith("/v1/incidents/BL-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v1/incidents/BL-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v1/incidents/BL-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "bl-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "bl-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_blameless_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.blameless.example/v1/incidents/BL-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "data": {
              "id": "BL-123",
              "attributes": {
                "external_reference": "guarded-live:market-data:5m",
                "status": "acknowledged",
                "title": "Guarded-live market-data incident",
                "updated_at": "2025-01-03T14:24:00Z",
                "severity": "sev2",
                "commander": "market-data-oncall",
                "visibility": "private",
                "url": "https://blameless.example/incidents/BL-123",
                "metadata": {
                  "remediation_state": "recovering",
                  "remediation_provider_payload": {
                    "job_id": "bl-job-9",
                    "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                    "verification": {"state": "pending"},
                  },
                  "remediation_provider_recovery": {
                    "lifecycle_state": "recovering",
                    "job_id": "bl-job-9",
                    "channels": ["depth", "kline"],
                    "symbols": ["ETH/USDT"],
                    "timeframe": "5m",
                    "status_machine_state": "provider_running",
                    "status_machine_workflow_state": "acknowledged",
                    "status_machine_job_state": "running",
                  },
                  "remediation_provider_telemetry": {
                    "source": "provider_payload",
                    "state": "running",
                    "progress_percent": 35,
                    "attempt_count": 1,
                    "current_step": "incident_body",
                    "last_message": "incident body telemetry is lagging",
                    "external_run_id": "bl-body-9",
                  },
                  "remediation_provider_telemetry_url": "https://blameless-engine.example/recovery/bl-job-9",
                },
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://blameless-engine.example/recovery/bl-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 88,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Blameless engine is verifying restored channels",
              "external_run_id": "bl-engine-9",
              "updated_at": "2025-01-03T14:25:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("blameless",),
    blameless_api_token="blameless-token",
    blameless_api_url="https://api.blameless.example",
    blameless_recovery_engine_url_template="https://blameless-engine.example/recovery/{job_id_urlencoded}",
    blameless_recovery_engine_token="blameless-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-blameless-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 22, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="blameless",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="BL-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="blameless",
  )

  assert snapshot is not None
  assert snapshot.provider == "blameless"
  assert snapshot.workflow_reference == "BL-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "bl-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "blameless"
  assert snapshot.payload["provider_schema"]["blameless"]["incident_id"] == "BL-123"
  assert snapshot.payload["provider_schema"]["blameless"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["blameless"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["blameless"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["blameless"]["phase_graph"]["command_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["blameless"]["phase_graph"]["visibility_phase"] == "private"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 88
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Blameless engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "bl-engine-9"
  assert requests[0][0].endswith("/v1/incidents/BL-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer blameless-token"
  assert requests[1][0] == "https://blameless-engine.example/recovery/bl-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer blameless-recovery-token"


def test_operator_alert_delivery_adapter_supports_xmatters_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("xmatters",),
    xmatters_api_token="xmatters-token",
    xmatters_api_url="https://api.xmatters.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-xmatters-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 30, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-xmatters-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 31, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("xmatters_incidents",)
  assert opened_records[0].target == "xmatters_incidents"
  assert opened_records[0].external_provider == "xmatters"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.xmatters.example/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer xmatters-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["priority"] == "P1"

  assert resolve_request[0].endswith(
    "/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_xmatters_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("xmatters",),
    xmatters_api_token="xmatters-token",
    xmatters_api_url="https://api.xmatters.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-xmatters-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 32, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="xmatters",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="XM-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="xmatters",
        job_id="xm-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="xmatters",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="xmatters",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="xmatters",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "xm-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="xmatters",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "xm-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("xmatters",)
  assert acknowledge[0].target == "xmatters_workflow"
  assert acknowledge[0].external_reference == "XM-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v1/incidents/XM-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/v1/incidents/XM-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v1/incidents/XM-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v1/incidents/XM-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "xm-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "xm-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_xmatters_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.xmatters.example/v1/incidents/XM-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "data": {
              "id": "XM-123",
              "attributes": {
                "external_reference": "guarded-live:market-data:5m",
                "status": "acknowledged",
                "title": "Guarded-live market-data incident",
                "updated_at": "2025-01-03T14:38:00Z",
                "priority": "P2",
                "assignee": "market-data-oncall",
                "response_plan": "market-data-repair",
                "url": "https://xmatters.example/incidents/XM-123",
                "metadata": {
                  "remediation_state": "recovering",
                  "remediation_provider_payload": {
                    "job_id": "xm-job-9",
                    "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                    "verification": {"state": "pending"},
                  },
                  "remediation_provider_recovery": {
                    "lifecycle_state": "recovering",
                    "job_id": "xm-job-9",
                    "channels": ["depth", "kline"],
                    "symbols": ["ETH/USDT"],
                    "timeframe": "5m",
                    "status_machine_state": "provider_running",
                    "status_machine_workflow_state": "acknowledged",
                    "status_machine_job_state": "running",
                  },
                  "remediation_provider_telemetry": {
                    "source": "provider_payload",
                    "state": "running",
                    "progress_percent": 42,
                    "attempt_count": 1,
                    "current_step": "incident_body",
                    "last_message": "incident body telemetry is lagging",
                    "external_run_id": "xm-body-9",
                  },
                  "remediation_provider_telemetry_url": "https://xmatters-engine.example/recovery/xm-job-9",
                },
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://xmatters-engine.example/recovery/xm-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 91,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "xMatters engine is verifying restored channels",
              "external_run_id": "xm-engine-9",
              "updated_at": "2025-01-03T14:39:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("xmatters",),
    xmatters_api_token="xmatters-token",
    xmatters_api_url="https://api.xmatters.example",
    xmatters_recovery_engine_url_template="https://xmatters-engine.example/recovery/{job_id_urlencoded}",
    xmatters_recovery_engine_token="xmatters-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-xmatters-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 36, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="xmatters",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="XM-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="xmatters",
  )

  assert snapshot is not None
  assert snapshot.provider == "xmatters"
  assert snapshot.workflow_reference == "XM-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "xm-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "xmatters"
  assert snapshot.payload["provider_schema"]["xmatters"]["incident_id"] == "XM-123"
  assert snapshot.payload["provider_schema"]["xmatters"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["xmatters"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["xmatters"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["xmatters"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["xmatters"]["phase_graph"]["response_plan_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 91
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "xMatters engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "xm-engine-9"
  assert requests[0][0].endswith("/v1/incidents/XM-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer xmatters-token"
  assert requests[1][0] == "https://xmatters-engine.example/recovery/xm-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer xmatters-recovery-token"


def test_operator_alert_delivery_adapter_supports_servicenow_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("servicenow",),
    servicenow_api_token="servicenow-token",
    servicenow_api_url="https://api.servicenow.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-servicenow-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 40, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-servicenow-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 41, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("servicenow_incidents",)
  assert opened_records[0].target == "servicenow_incidents"
  assert opened_records[0].external_provider == "servicenow"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.servicenow.example/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer servicenow-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["priority"] == "1"
  assert create_payload["incident"]["state"] == "new"

  assert resolve_request[0].endswith(
    "/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_servicenow_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("servicenow",),
    servicenow_api_token="servicenow-token",
    servicenow_api_url="https://api.servicenow.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-servicenow-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 42, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="servicenow",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="INC00123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="servicenow",
        job_id="sn-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicenow",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicenow",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicenow",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "sn-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicenow",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "sn-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("servicenow",)
  assert acknowledge[0].target == "servicenow_workflow"
  assert acknowledge[0].external_reference == "INC00123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v1/incidents/INC00123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/v1/incidents/INC00123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v1/incidents/INC00123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v1/incidents/INC00123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "sn-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "sn-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_servicenow_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.servicenow.example/v1/incidents/INC00123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_number": "INC00123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "in_progress",
              "short_description": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T14:48:00Z",
              "priority": "2",
              "assigned_to": "market-data-oncall",
              "assignment_group": "market-data-ops",
              "url": "https://servicenow.example/incidents/INC00123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "sn-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "sn-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "in_progress",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 44,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "sn-body-9",
                },
                "remediation_provider_telemetry_url": "https://servicenow-engine.example/recovery/sn-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://servicenow-engine.example/recovery/sn-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 92,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "ServiceNow engine is verifying restored channels",
              "external_run_id": "sn-engine-9",
              "updated_at": "2025-01-03T14:49:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("servicenow",),
    servicenow_api_token="servicenow-token",
    servicenow_api_url="https://api.servicenow.example",
    servicenow_recovery_engine_url_template="https://servicenow-engine.example/recovery/{job_id_urlencoded}",
    servicenow_recovery_engine_token="servicenow-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-servicenow-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="servicenow",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="INC00123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="servicenow",
  )

  assert snapshot is not None
  assert snapshot.provider == "servicenow"
  assert snapshot.workflow_reference == "INC00123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "in_progress"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "sn-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "servicenow"
  assert snapshot.payload["provider_schema"]["servicenow"]["incident_number"] == "INC00123"
  assert snapshot.payload["provider_schema"]["servicenow"]["incident_status"] == "in_progress"
  assert snapshot.payload["provider_schema"]["servicenow"]["phase_graph"]["incident_phase"] == "in_progress"
  assert snapshot.payload["provider_schema"]["servicenow"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["servicenow"]["phase_graph"]["assignment_phase"] == "assigned_to_user"
  assert snapshot.payload["provider_schema"]["servicenow"]["phase_graph"]["group_phase"] == "group_configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 92
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "ServiceNow engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "sn-engine-9"
  assert requests[0][0].endswith("/v1/incidents/INC00123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer servicenow-token"
  assert requests[1][0] == "https://servicenow-engine.example/recovery/sn-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer servicenow-recovery-token"


def test_operator_alert_delivery_adapter_supports_squadcast_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("squadcast",),
    squadcast_api_token="squadcast-token",
    squadcast_api_url="https://api.squadcast.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-squadcast-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 50, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-squadcast-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 51, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("squadcast_incidents",)
  assert opened_records[0].target == "squadcast_incidents"
  assert opened_records[0].external_provider == "squadcast"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.squadcast.example/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer squadcast-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "critical"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_squadcast_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("squadcast",),
    squadcast_api_token="squadcast-token",
    squadcast_api_url="https://api.squadcast.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-squadcast-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 52, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="squadcast",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="SC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="squadcast",
        job_id="sc-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="squadcast",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="squadcast",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="squadcast",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "sc-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="squadcast",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "sc-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("squadcast",)
  assert acknowledge[0].target == "squadcast_workflow"
  assert acknowledge[0].external_reference == "SC-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v1/incidents/SC-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/v1/incidents/SC-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v1/incidents/SC-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v1/incidents/SC-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "sc-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "sc-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_squadcast_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.squadcast.example/v1/incidents/SC-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "SC-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T14:58:00Z",
              "severity": "high",
              "assignee": "market-data-oncall",
              "escalation_policy": "market-data-primary",
              "url": "https://squadcast.example/incidents/SC-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "sc-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "sc-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 49,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "sc-body-9",
                },
                "remediation_provider_telemetry_url": "https://squadcast-engine.example/recovery/sc-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://squadcast-engine.example/recovery/sc-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 93,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Squadcast engine is verifying restored channels",
              "external_run_id": "sc-engine-9",
              "updated_at": "2025-01-03T14:59:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("squadcast",),
    squadcast_api_token="squadcast-token",
    squadcast_api_url="https://api.squadcast.example",
    squadcast_recovery_engine_url_template="https://squadcast-engine.example/recovery/{job_id_urlencoded}",
    squadcast_recovery_engine_token="squadcast-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-squadcast-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 56, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="squadcast",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="squadcast",
  )

  assert snapshot is not None
  assert snapshot.provider == "squadcast"
  assert snapshot.workflow_reference == "SC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "sc-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "squadcast"
  assert snapshot.payload["provider_schema"]["squadcast"]["incident_id"] == "SC-123"
  assert snapshot.payload["provider_schema"]["squadcast"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["squadcast"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["squadcast"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["squadcast"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["squadcast"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 93
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Squadcast engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "sc-engine-9"
  assert requests[0][0].endswith("/v1/incidents/SC-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer squadcast-token"
  assert requests[1][0] == "https://squadcast-engine.example/recovery/sc-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer squadcast-recovery-token"


def test_operator_alert_delivery_adapter_supports_bigpanda_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("bigpanda",),
    bigpanda_api_token="bigpanda-token",
    bigpanda_api_url="https://api.bigpanda.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-bigpanda-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 0, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-bigpanda-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 1, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("bigpanda_incidents",)
  assert opened_records[0].target == "bigpanda_incidents"
  assert opened_records[0].external_provider == "bigpanda"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.bigpanda.example/v2/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer bigpanda-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "critical"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/v2/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_bigpanda_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("bigpanda",),
    bigpanda_api_token="bigpanda-token",
    bigpanda_api_url="https://api.bigpanda.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-bigpanda-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 2, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="bigpanda",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="BP-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="bigpanda",
        job_id="bp-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="bigpanda",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="bigpanda",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="bigpanda",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "bp-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="bigpanda",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "bp-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("bigpanda",)
  assert acknowledge[0].target == "bigpanda_workflow"
  assert acknowledge[0].external_reference == "BP-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v2/incidents/BP-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/v2/incidents/BP-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v2/incidents/BP-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v2/incidents/BP-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "bp-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "bp-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_bigpanda_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.bigpanda.example/v2/incidents/BP-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "BP-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:08:00Z",
              "severity": "high",
              "assignee": "market-data-oncall",
              "team": "market-data-team",
              "url": "https://bigpanda.example/incidents/BP-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "bp-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "bp-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 51,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "bp-body-9",
                },
                "remediation_provider_telemetry_url": "https://bigpanda-engine.example/recovery/bp-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://bigpanda-engine.example/recovery/bp-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 91,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "BigPanda engine is verifying restored channels",
              "external_run_id": "bp-engine-9",
              "updated_at": "2025-01-03T15:09:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("bigpanda",),
    bigpanda_api_token="bigpanda-token",
    bigpanda_api_url="https://api.bigpanda.example",
    bigpanda_recovery_engine_url_template="https://bigpanda-engine.example/recovery/{job_id_urlencoded}",
    bigpanda_recovery_engine_token="bigpanda-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-bigpanda-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 6, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="bigpanda",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="BP-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="bigpanda",
  )

  assert snapshot is not None
  assert snapshot.provider == "bigpanda"
  assert snapshot.workflow_reference == "BP-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "bp-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "bigpanda"
  assert snapshot.payload["provider_schema"]["bigpanda"]["incident_id"] == "BP-123"
  assert snapshot.payload["provider_schema"]["bigpanda"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["bigpanda"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["bigpanda"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["bigpanda"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["bigpanda"]["phase_graph"]["team_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 91
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "BigPanda engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "bp-engine-9"
  assert requests[0][0].endswith("/v2/incidents/BP-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer bigpanda-token"
  assert requests[1][0] == "https://bigpanda-engine.example/recovery/bp-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer bigpanda-recovery-token"


def test_operator_alert_delivery_adapter_supports_grafana_oncall_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("grafana_oncall",),
    grafana_oncall_api_token="grafana-oncall-token",
    grafana_oncall_api_url="https://oncall-api.grafana.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-grafana-oncall-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 10, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-grafana-oncall-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 11, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("grafana_oncall_incidents",)
  assert opened_records[0].target == "grafana_oncall_incidents"
  assert opened_records[0].external_provider == "grafana_oncall"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://oncall-api.grafana.example/api/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer grafana-oncall-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "critical"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/api/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_grafana_oncall_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("grafana_oncall",),
    grafana_oncall_api_token="grafana-oncall-token",
    grafana_oncall_api_url="https://oncall-api.grafana.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-grafana-oncall-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 12, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="grafana_oncall",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="GO-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="grafana_oncall",
        job_id="go-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="grafana_oncall",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="grafana_oncall",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="grafana_oncall",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "go-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="grafana_oncall",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "go-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("grafana_oncall",)
  assert acknowledge[0].target == "grafana_oncall_workflow"
  assert acknowledge[0].external_reference == "GO-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/api/v1/incidents/GO-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/api/v1/incidents/GO-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/api/v1/incidents/GO-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/api/v1/incidents/GO-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "go-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "go-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_grafana_oncall_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://oncall-api.grafana.example/api/v1/incidents/GO-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "GO-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:13:00Z",
              "severity": "high",
              "assignee": "market-data-oncall",
              "escalation_chain": "market-data-primary",
              "url": "https://grafana-oncall.example/incidents/GO-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "go-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "go-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 52,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "go-body-9",
                },
                "remediation_provider_telemetry_url": "https://grafana-oncall-engine.example/recovery/go-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://grafana-oncall-engine.example/recovery/go-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 92,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Grafana OnCall engine is verifying restored channels",
              "external_run_id": "go-engine-9",
              "updated_at": "2025-01-03T15:14:00Z",
              "url": "https://grafana-oncall-engine.example/jobs/go-job-9",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("grafana_oncall",),
    grafana_oncall_api_token="grafana-oncall-token",
    grafana_oncall_api_url="https://oncall-api.grafana.example",
    grafana_oncall_recovery_engine_url_template="https://grafana-oncall-engine.example/recovery/{job_id_urlencoded}",
    grafana_oncall_recovery_engine_token="grafana-oncall-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-grafana-oncall-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 12, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="grafana_oncall",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="GO-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="grafana_oncall",
  )

  assert snapshot is not None
  assert snapshot.provider == "grafana_oncall"
  assert snapshot.workflow_reference == "GO-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "go-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "grafana_oncall"
  assert snapshot.payload["provider_schema"]["grafana_oncall"]["incident_id"] == "GO-123"
  assert snapshot.payload["provider_schema"]["grafana_oncall"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["grafana_oncall"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["grafana_oncall"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["grafana_oncall"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["grafana_oncall"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 92
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Grafana OnCall engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "go-engine-9"
  assert requests[0][0].endswith("/api/v1/incidents/GO-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer grafana-oncall-token"
  assert requests[1][0] == "https://grafana-oncall-engine.example/recovery/go-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer grafana-oncall-recovery-token"


def test_operator_alert_delivery_adapter_supports_zenduty_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zenduty",),
    zenduty_api_token="zenduty-token",
    zenduty_api_url="https://api.zenduty.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-zenduty-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 15, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-zenduty-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 16, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("zenduty_incidents",)
  assert opened_records[0].target == "zenduty_incidents"
  assert opened_records[0].external_provider == "zenduty"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.zenduty.example/api/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer zenduty-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "critical"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/api/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_zenduty_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zenduty",),
    zenduty_api_token="zenduty-token",
    zenduty_api_url="https://api.zenduty.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-zenduty-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 17, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="zenduty",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="ZD-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="zenduty",
        job_id="zd-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="zenduty",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="zenduty",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="zenduty",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "zd-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="zenduty",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "zd-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("zenduty",)
  assert acknowledge[0].target == "zenduty_workflow"
  assert acknowledge[0].external_reference == "ZD-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/api/v1/incidents/ZD-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/api/v1/incidents/ZD-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/api/v1/incidents/ZD-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/api/v1/incidents/ZD-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "zd-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "zd-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_zenduty_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.zenduty.example/api/v1/incidents/ZD-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "ZD-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:18:00Z",
              "severity": "high",
              "assignee": "market-data-oncall",
              "service": "market-data-sync",
              "url": "https://zenduty.example/incidents/ZD-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "zd-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "zd-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 53,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "zd-body-9",
                },
                "remediation_provider_telemetry_url": "https://zenduty-engine.example/recovery/zd-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://zenduty-engine.example/recovery/zd-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 93,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Zenduty engine is verifying restored channels",
              "external_run_id": "zd-engine-9",
              "updated_at": "2025-01-03T15:19:00Z",
              "url": "https://zenduty-engine.example/jobs/zd-job-9",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zenduty",),
    zenduty_api_token="zenduty-token",
    zenduty_api_url="https://api.zenduty.example",
    zenduty_recovery_engine_url_template="https://zenduty-engine.example/recovery/{job_id_urlencoded}",
    zenduty_recovery_engine_token="zenduty-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-zenduty-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 17, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="zenduty",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="ZD-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="zenduty",
  )

  assert snapshot is not None
  assert snapshot.provider == "zenduty"
  assert snapshot.workflow_reference == "ZD-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "zd-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "zenduty"
  assert snapshot.payload["provider_schema"]["zenduty"]["incident_id"] == "ZD-123"
  assert snapshot.payload["provider_schema"]["zenduty"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["zenduty"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["zenduty"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["zenduty"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["zenduty"]["phase_graph"]["service_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 93
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Zenduty engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "zd-engine-9"
  assert requests[0][0].endswith("/api/v1/incidents/ZD-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer zenduty-token"
  assert requests[1][0] == "https://zenduty-engine.example/recovery/zd-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer zenduty-recovery-token"


def test_operator_alert_delivery_adapter_supports_splunk_oncall_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("splunk_oncall",),
    splunk_oncall_api_token="splunk-oncall-token",
    splunk_oncall_api_url="https://api.splunkoncall.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-splunk-oncall-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 19, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-splunk-oncall-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 20, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("splunk_oncall_incidents",)
  assert opened_records[0].target == "splunk_oncall_incidents"
  assert opened_records[0].external_provider == "splunk_oncall"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.splunkoncall.example/api/v3/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer splunk-oncall-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "critical"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/api/v3/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_splunk_oncall_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("splunk_oncall",),
    splunk_oncall_api_token="splunk-oncall-token",
    splunk_oncall_api_url="https://api.splunkoncall.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-splunk-oncall-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 21, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="splunk_oncall",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="SOC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="splunk_oncall",
        job_id="soc-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="splunk_oncall",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="splunk_oncall",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="splunk_oncall",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "soc-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="splunk_oncall",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "soc-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("splunk_oncall",)
  assert acknowledge[0].target == "splunk_oncall_workflow"
  assert acknowledge[0].external_reference == "SOC-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/api/v3/incidents/SOC-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/api/v3/incidents/SOC-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/api/v3/incidents/SOC-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/api/v3/incidents/SOC-123/remediate?identifier_type=id")
  assert requests[0][3]["Authorization"] == "Bearer splunk-oncall-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "soc-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "soc-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_splunk_oncall_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.splunkoncall.example/api/v3/incidents/SOC-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "SOC-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:22:00Z",
              "severity": "high",
              "assignee": "market-data-oncall",
              "routing_key": "market-data-primary",
              "url": "https://splunk-oncall.example/incidents/SOC-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "soc-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "soc-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 45,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "soc-body-9",
                },
                "remediation_provider_telemetry_url": "https://splunk-oncall-engine.example/recovery/soc-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://splunk-oncall-engine.example/recovery/soc-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 93,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Splunk On-Call engine is verifying restored channels",
              "external_run_id": "soc-engine-9",
              "updated_at": "2025-01-03T15:23:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("splunk_oncall",),
    splunk_oncall_api_token="splunk-oncall-token",
    splunk_oncall_api_url="https://api.splunkoncall.example",
    splunk_oncall_recovery_engine_url_template=(
      "https://splunk-oncall-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    splunk_oncall_recovery_engine_token="splunk-oncall-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-splunk-oncall-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 21, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="splunk_oncall",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SOC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="splunk_oncall",
  )

  assert snapshot is not None
  assert snapshot.provider == "splunk_oncall"
  assert snapshot.workflow_reference == "SOC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "soc-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "splunk_oncall"
  assert snapshot.payload["provider_schema"]["splunk_oncall"]["incident_id"] == "SOC-123"
  assert snapshot.payload["provider_schema"]["splunk_oncall"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["splunk_oncall"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["splunk_oncall"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["splunk_oncall"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["splunk_oncall"]["phase_graph"]["routing_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 93
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Splunk On-Call engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "soc-engine-9"
  assert requests[0][0].endswith("/api/v3/incidents/SOC-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer splunk-oncall-token"
  assert requests[1][0] == "https://splunk-oncall-engine.example/recovery/soc-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer splunk-oncall-recovery-token"


def test_operator_alert_delivery_adapter_supports_jira_service_management_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("jira_service_management",),
    jira_service_management_api_token="jsm-token",
    jira_service_management_api_url="https://api.jsm.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-jsm-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 24, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-jsm-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 25, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("jira_service_management_incidents",)
  assert opened_records[0].target == "jira_service_management_incidents"
  assert opened_records[0].external_provider == "jira_service_management"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.jsm.example/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer jsm-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["priority"] == "highest"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_jira_service_management_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("jira_service_management",),
    jira_service_management_api_token="jsm-token",
    jira_service_management_api_url="https://api.jsm.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-jsm-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 26, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="jira_service_management",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="JSM-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="jira_service_management",
        job_id="jsm-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="jira_service_management",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="jira_service_management",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="jira_service_management",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "jsm-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="jira_service_management",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "jsm-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("jira_service_management",)
  assert acknowledge[0].target == "jira_service_management_workflow"
  assert acknowledge[0].external_reference == "JSM-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v1/incidents/JSM-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/v1/incidents/JSM-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v1/incidents/JSM-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v1/incidents/JSM-123/remediate?identifier_type=id")
  assert requests[0][3]["Authorization"] == "Bearer jsm-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "jsm-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "jsm-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_jira_service_management_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.jsm.example/v1/incidents/JSM-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "JSM-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:27:00Z",
              "priority": "high",
              "assignee": "market-data-oncall",
              "service_project": "market-data-platform",
              "url": "https://jsm.example/incidents/JSM-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "jsm-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "jsm-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 47,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "jsm-body-9",
                },
                "remediation_provider_telemetry_url": "https://jsm-engine.example/recovery/jsm-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://jsm-engine.example/recovery/jsm-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "JSM engine is verifying restored channels",
              "external_run_id": "jsm-engine-9",
              "updated_at": "2025-01-03T15:28:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("jira_service_management",),
    jira_service_management_api_token="jsm-token",
    jira_service_management_api_url="https://api.jsm.example",
    jira_service_management_recovery_engine_url_template=(
      "https://jsm-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    jira_service_management_recovery_engine_token="jsm-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-jsm-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 26, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="jira_service_management",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="JSM-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="jira_service_management",
  )

  assert snapshot is not None
  assert snapshot.provider == "jira_service_management"
  assert snapshot.workflow_reference == "JSM-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "jsm-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "jira_service_management"
  assert snapshot.payload["provider_schema"]["jira_service_management"]["incident_id"] == "JSM-123"
  assert snapshot.payload["provider_schema"]["jira_service_management"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["jira_service_management"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["jira_service_management"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["jira_service_management"]["phase_graph"]["assignment_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["jira_service_management"]["phase_graph"]["project_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "JSM engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "jsm-engine-9"
  assert requests[0][0].endswith("/v1/incidents/JSM-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer jsm-token"
  assert requests[1][0] == "https://jsm-engine.example/recovery/jsm-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer jsm-recovery-token"


def test_operator_alert_delivery_adapter_supports_pagertree_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagertree",),
    pagertree_api_token="pagertree-token",
    pagertree_api_url="https://api.pagertree.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-pagertree-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 24, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-pagertree-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 25, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("pagertree_incidents",)
  assert opened_records[0].target == "pagertree_incidents"
  assert opened_records[0].external_provider == "pagertree"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.pagertree.example/api/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer pagertree-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["urgency"] == "critical"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/api/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_pagertree_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagertree",),
    pagertree_api_token="pagertree-token",
    pagertree_api_url="https://api.pagertree.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-pagertree-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 26, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="pagertree",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="PT-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="pagertree",
        job_id="pt-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="pagertree",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="pagertree",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="pagertree",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "pt-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="pagertree",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "pt-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("pagertree",)
  assert acknowledge[0].target == "pagertree_workflow"
  assert acknowledge[0].external_reference == "PT-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/api/v1/incidents/PT-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/api/v1/incidents/PT-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/api/v1/incidents/PT-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/api/v1/incidents/PT-123/remediate?identifier_type=id")
  assert requests[0][3]["Authorization"] == "Bearer pagertree-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "pt-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "pt-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_pagertree_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.pagertree.example/api/v1/incidents/PT-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "PT-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:27:00Z",
              "urgency": "high",
              "assignee": "market-data-oncall",
              "team": "market-data-platform",
              "url": "https://pagertree.example/incidents/PT-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "pt-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "pt-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 48,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "pt-body-9",
                },
                "remediation_provider_telemetry_url": "https://pagertree-engine.example/recovery/pt-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://pagertree-engine.example/recovery/pt-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "PagerTree engine is verifying restored channels",
              "external_run_id": "pt-engine-9",
              "updated_at": "2025-01-03T15:28:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("pagertree",),
    pagertree_api_token="pagertree-token",
    pagertree_api_url="https://api.pagertree.example",
    pagertree_recovery_engine_url_template=(
      "https://pagertree-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    pagertree_recovery_engine_token="pagertree-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-pagertree-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 26, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="pagertree",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="PT-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="pagertree",
  )

  assert snapshot is not None
  assert snapshot.provider == "pagertree"
  assert snapshot.workflow_reference == "PT-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "pt-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "pagertree"
  assert snapshot.payload["provider_schema"]["pagertree"]["incident_id"] == "PT-123"
  assert snapshot.payload["provider_schema"]["pagertree"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["pagertree"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["pagertree"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["pagertree"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["pagertree"]["phase_graph"]["team_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 95
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "PagerTree engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "pt-engine-9"
  assert requests[0][0].endswith("/api/v1/incidents/PT-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer pagertree-token"
  assert requests[1][0] == "https://pagertree-engine.example/recovery/pt-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer pagertree-recovery-token"


def test_operator_alert_delivery_adapter_supports_alertops_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("alertops",),
    alertops_api_token="alertops-token",
    alertops_api_url="https://api.alertops.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-alertops-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 29, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-alertops-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 30, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("alertops_incidents",)
  assert opened_records[0].target == "alertops_incidents"
  assert opened_records[0].external_provider == "alertops"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.alertops.example/api/v2/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer alertops-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["priority"] == "p1"
  assert create_payload["incident"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/api/v2/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_alertops_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("alertops",),
    alertops_api_token="alertops-token",
    alertops_api_url="https://api.alertops.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-alertops-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 31, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="alertops",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="AO-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="alertops",
        job_id="ao-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="alertops",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="alertops",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="alertops",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "ao-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="alertops",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "ao-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("alertops",)
  assert acknowledge[0].target == "alertops_workflow"
  assert acknowledge[0].external_reference == "AO-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/api/v2/incidents/AO-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/api/v2/incidents/AO-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/api/v2/incidents/AO-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/api/v2/incidents/AO-123/remediate?identifier_type=id")
  assert requests[0][3]["Authorization"] == "Bearer alertops-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "ao-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "ao-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_alertops_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.alertops.example/api/v2/incidents/AO-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "incident_id": "AO-123",
              "external_reference": "guarded-live:market-data:5m",
              "incident_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:32:00Z",
              "priority": "p2",
              "owner": "market-data-oncall",
              "service": "market-data-platform",
              "url": "https://alertops.example/incidents/AO-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "ao-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "ao-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 49,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "ao-body-9",
                },
                "remediation_provider_telemetry_url": "https://alertops-engine.example/recovery/ao-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://alertops-engine.example/recovery/ao-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 96,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "AlertOps engine is verifying restored channels",
              "external_run_id": "ao-engine-9",
              "updated_at": "2025-01-03T15:33:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("alertops",),
    alertops_api_token="alertops-token",
    alertops_api_url="https://api.alertops.example",
    alertops_recovery_engine_url_template=(
      "https://alertops-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    alertops_recovery_engine_token="alertops-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-alertops-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 31, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="alertops",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="AO-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="alertops",
  )

  assert snapshot is not None
  assert snapshot.provider == "alertops"
  assert snapshot.workflow_reference == "AO-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "ao-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "alertops"
  assert snapshot.payload["provider_schema"]["alertops"]["incident_id"] == "AO-123"
  assert snapshot.payload["provider_schema"]["alertops"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["alertops"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["alertops"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["alertops"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["alertops"]["phase_graph"]["service_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 96
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "AlertOps engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "ao-engine-9"
  assert requests[0][0].endswith("/api/v2/incidents/AO-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer alertops-token"
  assert requests[1][0] == "https://alertops-engine.example/recovery/ao-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer alertops-recovery-token"


def test_operator_alert_delivery_adapter_supports_signl4_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("signl4",),
    signl4_api_token="signl4-token",
    signl4_api_url="https://api.signl4.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-signl4-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 34, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-signl4-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 35, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("signl4_incidents",)
  assert opened_records[0].target == "signl4_incidents"
  assert opened_records[0].external_provider == "signl4"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.signl4.example/api/v1/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer signl4-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["alert"]["priority"] == "critical"
  assert create_payload["alert"]["status"] == "triggered"

  assert resolve_request[0].endswith(
    "/api/v1/alerts/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_signl4_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("signl4",),
    signl4_api_token="signl4-token",
    signl4_api_url="https://api.signl4.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-signl4-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 36, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="signl4",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="S4-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="signl4",
        job_id="s4-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="signl4",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="signl4",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="signl4",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "s4-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="signl4",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "s4-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("signl4",)
  assert acknowledge[0].target == "signl4_workflow"
  assert acknowledge[0].external_reference == "S4-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/api/v1/alerts/S4-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/api/v1/alerts/S4-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/api/v1/alerts/S4-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/api/v1/alerts/S4-123/remediate?identifier_type=id")
  assert requests[0][3]["Authorization"] == "Bearer signl4-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "s4-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "s4-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_signl4_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.signl4.example/api/v1/alerts/S4-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "S4-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:37:00Z",
              "priority": "high",
              "team": "market-data-platform",
              "assignee": "market-data-oncall",
              "url": "https://signl4.example/alerts/S4-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "s4-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "s4-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 52,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "s4-body-9",
                },
                "remediation_provider_telemetry_url": "https://signl4-engine.example/recovery/s4-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://signl4-engine.example/recovery/s4-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 91,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "SIGNL4 engine is verifying restored channels",
              "external_run_id": "s4-engine-9",
              "updated_at": "2025-01-03T15:38:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("signl4",),
    signl4_api_token="signl4-token",
    signl4_api_url="https://api.signl4.example",
    signl4_recovery_engine_url_template=(
      "https://signl4-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    signl4_recovery_engine_token="signl4-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-signl4-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 36, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="signl4",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="S4-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="signl4",
  )

  assert snapshot is not None
  assert snapshot.provider == "signl4"
  assert snapshot.workflow_reference == "S4-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "s4-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "signl4"
  assert snapshot.payload["provider_schema"]["signl4"]["alert_id"] == "S4-123"
  assert snapshot.payload["provider_schema"]["signl4"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["signl4"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["signl4"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["signl4"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["signl4"]["phase_graph"]["team_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 91
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "SIGNL4 engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "s4-engine-9"
  assert requests[0][0].endswith("/api/v1/alerts/S4-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer signl4-token"
  assert requests[1][0] == "https://signl4-engine.example/recovery/s4-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer signl4-recovery-token"


def test_operator_alert_delivery_adapter_supports_ilert_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("ilert",),
    ilert_api_token="ilert-token",
    ilert_api_url="https://api.ilert.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-ilert-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-ilert-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 40, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("ilert_incidents",)
  assert opened_records[0].target == "ilert_incidents"
  assert opened_records[0].external_provider == "ilert"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.ilert.example/api/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer ilert-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["alert"]["priority"] == "HIGH"
  assert create_payload["alert"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/api/alerts/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_ilert_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("ilert",),
    ilert_api_token="ilert-token",
    ilert_api_url="https://api.ilert.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-ilert-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="ilert",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="IL-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="ilert",
        job_id="ilert-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="ilert",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="ilert",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="ilert",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "ilert-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="ilert",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "ilert-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("ilert",)
  assert acknowledge[0].target == "ilert_workflow"
  assert acknowledge[0].external_reference == "IL-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/api/alerts/IL-123/accept?identifier_type=id")
  assert requests[1][0].endswith("/api/alerts/IL-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/api/alerts/IL-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/api/alerts/IL-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer ilert-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "ilert-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "ilert-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_ilert_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.ilert.example/api/alerts/IL-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "IL-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "accepted",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:42:00Z",
              "priority": "HIGH",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://ilert.example/alerts/IL-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "ilert-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "ilert-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "accepted",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 58,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "ilert-body-9",
                },
                "remediation_provider_telemetry_url": "https://ilert-engine.example/recovery/ilert-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://ilert-engine.example/recovery/ilert-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 88,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "iLert engine is verifying restored channels",
              "external_run_id": "ilert-engine-9",
              "updated_at": "2025-01-03T15:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("ilert",),
    ilert_api_token="ilert-token",
    ilert_api_url="https://api.ilert.example",
    ilert_recovery_engine_url_template=(
      "https://ilert-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    ilert_recovery_engine_token="ilert-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-ilert-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="ilert",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="IL-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="ilert",
  )

  assert snapshot is not None
  assert snapshot.provider == "ilert"
  assert snapshot.workflow_reference == "IL-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "accepted"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "ilert-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "ilert"
  assert snapshot.payload["provider_schema"]["ilert"]["alert_id"] == "IL-123"
  assert snapshot.payload["provider_schema"]["ilert"]["alert_status"] == "accepted"
  assert snapshot.payload["provider_schema"]["ilert"]["phase_graph"]["alert_phase"] == "accepted"
  assert snapshot.payload["provider_schema"]["ilert"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["ilert"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["ilert"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 88
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "iLert engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "ilert-engine-9"
  assert requests[0][0].endswith("/api/alerts/IL-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer ilert-token"
  assert requests[1][0] == "https://ilert-engine.example/recovery/ilert-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer ilert-recovery-token"


def test_operator_alert_delivery_adapter_supports_betterstack_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("betterstack",),
    betterstack_api_token="betterstack-token",
    betterstack_api_url="https://api.betterstack.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-betterstack-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 49, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-betterstack-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 50, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("betterstack_incidents",)
  assert opened_records[0].target == "betterstack_incidents"
  assert opened_records[0].external_provider == "betterstack"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.betterstack.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer betterstack-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["alert"]["priority"] == "high"
  assert create_payload["alert"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/alerts/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_betterstack_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("betterstack",),
    betterstack_api_token="betterstack-token",
    betterstack_api_url="https://api.betterstack.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-betterstack-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 51, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="betterstack",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="BS-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="betterstack",
        job_id="betterstack-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="betterstack",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="betterstack",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="betterstack",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "betterstack-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="betterstack",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "betterstack-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("betterstack",)
  assert acknowledge[0].target == "betterstack_workflow"
  assert acknowledge[0].external_reference == "BS-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/BS-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/BS-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/BS-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/BS-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer betterstack-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "betterstack-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "betterstack-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_betterstack_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.betterstack.example/alerts/BS-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "BS-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:52:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://betterstack.example/alerts/BS-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "betterstack-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "betterstack-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 58,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "betterstack-body-9",
                },
                "remediation_provider_telemetry_url": "https://betterstack-engine.example/recovery/betterstack-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://betterstack-engine.example/recovery/betterstack-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 88,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Better Stack engine is verifying restored channels",
              "external_run_id": "betterstack-engine-9",
              "updated_at": "2025-01-03T15:53:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("betterstack",),
    betterstack_api_token="betterstack-token",
    betterstack_api_url="https://api.betterstack.example",
    betterstack_recovery_engine_url_template=(
      "https://betterstack-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    betterstack_recovery_engine_token="betterstack-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-betterstack-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 51, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="betterstack",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="BS-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="betterstack",
  )

  assert snapshot is not None
  assert snapshot.provider == "betterstack"
  assert snapshot.workflow_reference == "BS-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "betterstack-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "betterstack"
  assert snapshot.payload["provider_schema"]["betterstack"]["alert_id"] == "BS-123"
  assert snapshot.payload["provider_schema"]["betterstack"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["betterstack"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["betterstack"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["betterstack"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["betterstack"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 88
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Better Stack engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "betterstack-engine-9"
  assert requests[0][0].endswith("/alerts/BS-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer betterstack-token"
  assert requests[1][0] == "https://betterstack-engine.example/recovery/betterstack-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer betterstack-recovery-token"


def test_operator_alert_delivery_adapter_supports_onpage_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("onpage",),
    onpage_api_token="onpage-token",
    onpage_api_url="https://api.onpage.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-onpage-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 54, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-onpage-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 55, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("onpage_incidents",)
  assert opened_records[0].target == "onpage_incidents"
  assert opened_records[0].external_provider == "onpage"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.onpage.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer onpage-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["alert"]["priority"] == "high"
  assert create_payload["alert"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/alerts/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_onpage_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("onpage",),
    onpage_api_token="onpage-token",
    onpage_api_url="https://api.onpage.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-onpage-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 56, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="onpage",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="OP-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="onpage",
        job_id="onpage-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="onpage",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="onpage",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="onpage",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "onpage-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="onpage",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "onpage-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("onpage",)
  assert acknowledge[0].target == "onpage_workflow"
  assert acknowledge[0].external_reference == "OP-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/OP-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/OP-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/OP-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/OP-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer onpage-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "onpage-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "onpage-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_onpage_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.onpage.example/alerts/OP-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "OP-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:57:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://onpage.example/alerts/OP-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "onpage-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "onpage-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 61,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "onpage-body-9",
                },
                "remediation_provider_telemetry_url": "https://onpage-engine.example/recovery/onpage-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://onpage-engine.example/recovery/onpage-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 91,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "OnPage engine is verifying restored channels",
              "external_run_id": "onpage-engine-9",
              "updated_at": "2025-01-03T15:58:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("onpage",),
    onpage_api_token="onpage-token",
    onpage_api_url="https://api.onpage.example",
    onpage_recovery_engine_url_template=(
      "https://onpage-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    onpage_recovery_engine_token="onpage-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-onpage-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 56, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="onpage",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="OP-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="onpage",
  )

  assert snapshot is not None
  assert snapshot.provider == "onpage"
  assert snapshot.workflow_reference == "OP-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "onpage-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "onpage"
  assert snapshot.payload["provider_schema"]["onpage"]["alert_id"] == "OP-123"
  assert snapshot.payload["provider_schema"]["onpage"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["onpage"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["onpage"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["onpage"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["onpage"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 91
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "OnPage engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "onpage-engine-9"
  assert requests[0][0].endswith("/alerts/OP-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer onpage-token"
  assert requests[1][0] == "https://onpage-engine.example/recovery/onpage-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer onpage-recovery-token"


def test_operator_alert_delivery_adapter_supports_allquiet_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("allquiet",),
    allquiet_api_token="allquiet-token",
    allquiet_api_url="https://api.allquiet.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-allquiet-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 54, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-allquiet-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 55, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("allquiet_incidents",)
  assert opened_records[0].target == "allquiet_incidents"
  assert opened_records[0].external_provider == "allquiet"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.allquiet.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer allquiet-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["alert"]["priority"] == "high"
  assert create_payload["alert"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/alerts/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_allquiet_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("allquiet",),
    allquiet_api_token="allquiet-token",
    allquiet_api_url="https://api.allquiet.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-allquiet-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 56, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="allquiet",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="AQ-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="allquiet",
        job_id="allquiet-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="allquiet",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="allquiet",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="allquiet",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "allquiet-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="allquiet",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "allquiet-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("allquiet",)
  assert acknowledge[0].target == "allquiet_workflow"
  assert acknowledge[0].external_reference == "AQ-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/AQ-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/AQ-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/AQ-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/AQ-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer allquiet-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "allquiet-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "allquiet-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_allquiet_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.allquiet.example/alerts/AQ-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "AQ-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:57:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://allquiet.example/alerts/AQ-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "allquiet-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "allquiet-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 61,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "allquiet-body-9",
                },
                "remediation_provider_telemetry_url": "https://allquiet-engine.example/recovery/allquiet-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://allquiet-engine.example/recovery/allquiet-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 91,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "All Quiet engine is verifying restored channels",
              "external_run_id": "allquiet-engine-9",
              "updated_at": "2025-01-03T15:58:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("allquiet",),
    allquiet_api_token="allquiet-token",
    allquiet_api_url="https://api.allquiet.example",
    allquiet_recovery_engine_url_template=(
      "https://allquiet-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    allquiet_recovery_engine_token="allquiet-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-allquiet-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 56, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="allquiet",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="AQ-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="allquiet",
  )

  assert snapshot is not None
  assert snapshot.provider == "allquiet"
  assert snapshot.workflow_reference == "AQ-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "allquiet-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "allquiet"
  assert snapshot.payload["provider_schema"]["allquiet"]["alert_id"] == "AQ-123"
  assert snapshot.payload["provider_schema"]["allquiet"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["allquiet"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["allquiet"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["allquiet"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["allquiet"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 91
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "All Quiet engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "allquiet-engine-9"
  assert requests[0][0].endswith("/alerts/AQ-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer allquiet-token"
  assert requests[1][0] == "https://allquiet-engine.example/recovery/allquiet-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer allquiet-recovery-token"


def test_operator_alert_delivery_adapter_supports_moogsoft_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("moogsoft",),
    moogsoft_api_token="moogsoft-token",
    moogsoft_api_url="https://api.moogsoft.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-moogsoft-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 54, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-moogsoft-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 55, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("moogsoft_incidents",)
  assert opened_records[0].target == "moogsoft_incidents"
  assert opened_records[0].external_provider == "moogsoft"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.moogsoft.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer moogsoft-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["alert"]["priority"] == "high"
  assert create_payload["alert"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/alerts/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_moogsoft_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("moogsoft",),
    moogsoft_api_token="moogsoft-token",
    moogsoft_api_url="https://api.moogsoft.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-moogsoft-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 15, 56, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="moogsoft",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="MG-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="moogsoft",
        job_id="moogsoft-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="moogsoft",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="moogsoft",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="moogsoft",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "moogsoft-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="moogsoft",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "moogsoft-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("moogsoft",)
  assert acknowledge[0].target == "moogsoft_workflow"
  assert acknowledge[0].external_reference == "MG-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/MG-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/MG-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/MG-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/MG-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer moogsoft-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "moogsoft-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "moogsoft-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_moogsoft_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.moogsoft.example/alerts/MG-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "MG-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T15:57:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://moogsoft.example/alerts/MG-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "moogsoft-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "moogsoft-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 61,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "moogsoft-body-9",
                },
                "remediation_provider_telemetry_url": "https://moogsoft-engine.example/recovery/moogsoft-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://moogsoft-engine.example/recovery/moogsoft-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 91,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Moogsoft engine is verifying restored channels",
              "external_run_id": "moogsoft-engine-9",
              "updated_at": "2025-01-03T15:58:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("moogsoft",),
    moogsoft_api_token="moogsoft-token",
    moogsoft_api_url="https://api.moogsoft.example",
    moogsoft_recovery_engine_url_template=(
      "https://moogsoft-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    moogsoft_recovery_engine_token="moogsoft-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-moogsoft-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 15, 56, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="moogsoft",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="MG-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="moogsoft",
  )

  assert snapshot is not None
  assert snapshot.provider == "moogsoft"
  assert snapshot.workflow_reference == "MG-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "moogsoft-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "moogsoft"
  assert snapshot.payload["provider_schema"]["moogsoft"]["alert_id"] == "MG-123"
  assert snapshot.payload["provider_schema"]["moogsoft"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["moogsoft"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["moogsoft"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["moogsoft"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["moogsoft"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 91
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Moogsoft engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "moogsoft-engine-9"
  assert requests[0][0].endswith("/alerts/MG-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer moogsoft-token"
  assert requests[1][0] == "https://moogsoft-engine.example/recovery/moogsoft-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer moogsoft-recovery-token"


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
    if request.full_url == "https://api.opsgenie.example/v2/alerts/OG-123?identifierType=id":
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
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 45,
                  "attempt_count": 1,
                  "current_step": "backfill",
                  "last_message": "repair job started",
                  "external_run_id": "og-rem-7",
                },
                "remediation_provider_telemetry_url": "https://opsgenie-engine.example/recovery/og-job-7",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://opsgenie-engine.example/recovery/og-job-7":
      return FakeResponse(
        200,
        json.dumps(
          {
            "data": {
              "state": "running",
              "progress_percent": 80,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "provider engine is verifying restored channels",
              "external_run_id": "og-engine-7",
              "updatedAt": "2025-01-03T14:13:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("opsgenie",),
    opsgenie_api_key="opsgenie-key",
    opsgenie_api_url="https://api.opsgenie.example",
    opsgenie_recovery_engine_api_key="opsgenie-recovery-key",
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
  assert snapshot.payload["provider_schema"]["kind"] == "opsgenie"
  assert snapshot.payload["provider_schema"]["opsgenie"]["alert_id"] == "OG-123"
  assert snapshot.payload["provider_schema"]["opsgenie"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["opsgenie"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["opsgenie"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["opsgenie"]["phase_graph"]["acknowledgment_phase"] == "acknowledged"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 80
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "provider engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "og-engine-7"
  assert requests[0][0].endswith("/v2/alerts/OG-123?identifierType=id")
  assert requests[0][1] == "GET"
  assert requests[1][0] == "https://opsgenie-engine.example/recovery/og-job-7"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "GenieKey opsgenie-recovery-key"


def test_operator_alert_delivery_adapter_supports_incidentio_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidentio",),
    incidentio_api_token="incidentio-token",
    incidentio_api_url="https://api.incidentio.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-incidentio-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 15, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-incidentio-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 16, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("incidentio_incidents",)
  assert opened_records[0].target == "incidentio_incidents"
  assert opened_records[0].external_provider == "incidentio"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.incidentio.example/v2/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer incidentio-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "critical"

  assert resolve_request[0].endswith(
    "/v2/incidents/guarded-live%3Aworker-failed%3Arun-1/actions/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["message"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_incidentio_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidentio",),
    incidentio_api_token="incidentio-token",
    incidentio_api_url="https://api.incidentio.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-incidentio-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 20, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="incidentio",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="INC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="incidentio",
        job_id="io-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentio",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentio",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentio",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "io-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentio",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "io-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("incidentio",)
  assert acknowledge[0].target == "incidentio_workflow"
  assert acknowledge[0].external_reference == "INC-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v2/incidents/INC-123/actions/acknowledge?identifier_type=id")
  assert requests[0][1] == "POST"
  assert requests[1][0].endswith("/v2/incidents/INC-123/actions/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v2/incidents/INC-123/actions/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v2/incidents/INC-123/actions/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  assert "level 2" in escalate_payload["message"]
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  assert "requested remediation" in remediate_payload["message"]
  assert "market_data.sync_recent" in remediate_payload["message"]
  assert '"job_id": "io-job-2"' in remediate_payload["message"]
  assert '"job_id": "io-job-1"' in resolve_payload["message"]
  assert incident.remediation.provider_recovery.status_machine.state == "not_requested"


def test_operator_alert_delivery_adapter_pulls_incidentio_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.incidentio.example/v2/incidents/INC-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "incident": {
              "id": "INC-123",
              "external_reference": "guarded-live:market-data:5m",
              "status": "acknowledged",
              "name": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T14:20:00Z",
              "severity": "critical",
              "mode": "standard",
              "visibility": "public",
              "url": "https://incident.io/incidents/INC-123",
              "assignee": {"name": "On-call engineer"},
              "metadata": {
                "remediation_state": "provider_recovered",
                "remediation_provider_payload": {
                  "job_id": "io-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "passed"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovered",
                  "job_id": "io-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "verification_state": "passed",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "completed",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "completed",
                  "progress_percent": 70,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body copy still stale",
                  "external_run_id": "io-body-9",
                },
                "remediation_provider_telemetry_url": "https://incidentio-engine.example/recovery/io-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://incidentio-engine.example/recovery/io-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "data": {
              "state": "completed",
              "progress_percent": 100,
              "attempt_count": 2,
              "current_step": "verification",
              "last_message": "incident.io engine completed verification",
              "external_run_id": "io-engine-9",
              "updated_at": "2025-01-03T14:21:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidentio",),
    incidentio_api_token="incidentio-token",
    incidentio_api_url="https://api.incidentio.example",
    incidentio_recovery_engine_url_template="https://incidentio-engine.example/recovery/{job_id_urlencoded}",
    incidentio_recovery_engine_token="incidentio-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-incidentio-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 20, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="incidentio",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="INC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="incidentio",
  )

  assert snapshot is not None
  assert snapshot.provider == "incidentio"
  assert snapshot.workflow_reference == "INC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "provider_recovered"
  assert snapshot.payload["job_id"] == "io-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "incidentio"
  assert snapshot.payload["provider_schema"]["incidentio"]["incident_id"] == "INC-123"
  assert snapshot.payload["provider_schema"]["incidentio"]["incident_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["incidentio"]["phase_graph"]["incident_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["incidentio"]["phase_graph"]["workflow_phase"] == "awaiting_local_verification"
  assert snapshot.payload["provider_schema"]["incidentio"]["phase_graph"]["assignment_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["incidentio"]["phase_graph"]["visibility_phase"] == "public"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "completed"
  assert snapshot.payload["telemetry"]["progress_percent"] == 100
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verification"
  assert snapshot.payload["telemetry"]["last_message"] == "incident.io engine completed verification"
  assert snapshot.payload["telemetry"]["external_run_id"] == "io-engine-9"
  assert requests[0][0].endswith("/v2/incidents/INC-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer incidentio-token"
  assert requests[1][0] == "https://incidentio-engine.example/recovery/io-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer incidentio-recovery-token"


def test_operator_alert_delivery_adapter_supports_firehydrant_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("firehydrant",),
    firehydrant_api_token="firehydrant-token",
    firehydrant_api_url="https://api.firehydrant.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-firehydrant-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 25, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-firehydrant-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 14, 26, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("firehydrant_incidents",)
  assert opened_records[0].target == "firehydrant_incidents"
  assert opened_records[0].external_provider == "firehydrant"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.firehydrant.example/v1/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer firehydrant-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["incident"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["incident"]["severity"] == "SEV1"
  assert create_payload["incident"]["priority"] == "P1"

  assert resolve_request[0].endswith(
    "/v1/incidents/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "POST"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_firehydrant_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("firehydrant",),
    firehydrant_api_token="firehydrant-token",
    firehydrant_api_url="https://api.firehydrant.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-firehydrant-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 14, 30, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="firehydrant",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="FH-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="firehydrant",
        job_id="fh-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="firehydrant",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="firehydrant",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="firehydrant",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "fh-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="firehydrant",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "fh-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("firehydrant",)
  assert acknowledge[0].target == "firehydrant_workflow"
  assert acknowledge[0].external_reference == "FH-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/v1/incidents/FH-123/acknowledge?identifier_type=id")
  assert requests[0][1] == "POST"
  assert requests[1][0].endswith("/v1/incidents/FH-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/v1/incidents/FH-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/v1/incidents/FH-123/remediate?identifier_type=id")
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "fh-job-2"' in remediate_payload["note"]
  assert '"job_id": "fh-job-1"' in resolve_payload["note"]
  assert incident.remediation.provider_recovery.status_machine.state == "not_requested"


def test_operator_alert_delivery_adapter_pulls_firehydrant_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.firehydrant.example/v1/incidents/FH-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "incident": {
              "id": "FH-123",
              "external_reference": "guarded-live:market-data:5m",
              "status": "investigating",
              "name": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T14:30:00Z",
              "severity": "SEV1",
              "priority": "P1",
              "url": "https://firehydrant.example/incidents/FH-123",
              "team": {"name": "Core Ops"},
              "runbook": {"name": "Repair candles"},
              "details": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "fh-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "fh-job-9",
                  "channels": ["depth", "kline"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "verification_state": "pending",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "investigating",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 55,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "incident body telemetry is lagging",
                  "external_run_id": "fh-body-9",
                },
                "remediation_provider_telemetry_url": "https://firehydrant-engine.example/recovery/fh-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://firehydrant-engine.example/recovery/fh-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 90,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "FireHydrant engine is verifying restored channels",
              "external_run_id": "fh-engine-9",
              "updated_at": "2025-01-03T14:31:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("firehydrant",),
    firehydrant_api_token="firehydrant-token",
    firehydrant_api_url="https://api.firehydrant.example",
    firehydrant_recovery_engine_url_template="https://firehydrant-engine.example/recovery/{job_id_urlencoded}",
    firehydrant_recovery_engine_token="firehydrant-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-firehydrant-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 14, 30, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="firehydrant",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="FH-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="firehydrant",
  )

  assert snapshot is not None
  assert snapshot.provider == "firehydrant"
  assert snapshot.workflow_reference == "FH-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "investigating"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "fh-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "firehydrant"
  assert snapshot.payload["provider_schema"]["firehydrant"]["incident_id"] == "FH-123"
  assert snapshot.payload["provider_schema"]["firehydrant"]["incident_status"] == "investigating"
  assert snapshot.payload["provider_schema"]["firehydrant"]["phase_graph"]["incident_phase"] == "investigating"
  assert snapshot.payload["provider_schema"]["firehydrant"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["firehydrant"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 90
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "FireHydrant engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "fh-engine-9"
  assert requests[0][0].endswith("/v1/incidents/FH-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer firehydrant-token"
  assert requests[1][0] == "https://firehydrant-engine.example/recovery/fh-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer firehydrant-recovery-token"
