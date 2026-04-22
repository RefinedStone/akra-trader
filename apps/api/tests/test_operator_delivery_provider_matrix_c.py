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


def test_operator_alert_delivery_adapter_supports_squzy_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("squzy",),
    squzy_api_token="squzy-token",
    squzy_api_url="https://api.squzy.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-squzy-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-squzy-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 40, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("squzy_incidents",)
  assert opened_records[0].target == "squzy_incidents"
  assert opened_records[0].external_provider == "squzy"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.squzy.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer squzy-token"
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


def test_operator_alert_delivery_adapter_syncs_squzy_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("squzy",),
    squzy_api_token="squzy-token",
    squzy_api_url="https://api.squzy.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-squzy-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="squzy",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="SQ-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="squzy",
        job_id="squzy-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="squzy",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="squzy",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="squzy",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "squzy-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="squzy",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "squzy-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("squzy",)
  assert acknowledge[0].target == "squzy_workflow"
  assert acknowledge[0].external_reference == "SQ-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/SQ-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/SQ-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/SQ-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/SQ-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer squzy-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "squzy-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "squzy-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_squzy_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.squzy.example/alerts/SQ-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "SQ-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://squzy.example/alerts/SQ-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "squzy-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "squzy-job-9",
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
                  "progress_percent": 67,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "squzy-body-9",
                },
                "remediation_provider_telemetry_url": "https://squzy-engine.example/recovery/squzy-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://squzy-engine.example/recovery/squzy-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Squzy engine is verifying restored channels",
              "external_run_id": "squzy-engine-9",
              "updated_at": "2025-01-03T16:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("squzy",),
    squzy_api_token="squzy-token",
    squzy_api_url="https://api.squzy.example",
    squzy_recovery_engine_url_template=(
      "https://squzy-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    squzy_recovery_engine_token="squzy-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-squzy-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="squzy",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SQ-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="squzy",
  )

  assert snapshot is not None
  assert snapshot.provider == "squzy"
  assert snapshot.workflow_reference == "SQ-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "squzy-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "squzy"
  assert snapshot.payload["provider_schema"]["squzy"]["alert_id"] == "SQ-123"
  assert snapshot.payload["provider_schema"]["squzy"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["squzy"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["squzy"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["squzy"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["squzy"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Squzy engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "squzy-engine-9"
  assert requests[0][0].endswith("/alerts/SQ-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer squzy-token"
  assert requests[1][0] == "https://squzy-engine.example/recovery/squzy-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer squzy-recovery-token"


def test_operator_alert_delivery_adapter_supports_crisescontrol_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("crisescontrol",),
    crisescontrol_api_token="crisescontrol-token",
    crisescontrol_api_url="https://api.crisescontrol.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-crisescontrol-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-crisescontrol-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 40, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("crisescontrol_incidents",)
  assert opened_records[0].target == "crisescontrol_incidents"
  assert opened_records[0].external_provider == "crisescontrol"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.crisescontrol.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer crisescontrol-token"
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


def test_operator_alert_delivery_adapter_syncs_crisescontrol_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("crisescontrol",),
    crisescontrol_api_token="crisescontrol-token",
    crisescontrol_api_url="https://api.crisescontrol.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-crisescontrol-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="crisescontrol",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="CC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="crisescontrol",
        job_id="crisescontrol-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="crisescontrol",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="crisescontrol",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="crisescontrol",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "crisescontrol-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="crisescontrol",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "crisescontrol-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("crisescontrol",)
  assert acknowledge[0].target == "crisescontrol_workflow"
  assert acknowledge[0].external_reference == "CC-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/CC-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/CC-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/CC-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/CC-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer crisescontrol-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "crisescontrol-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "crisescontrol-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_crisescontrol_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.crisescontrol.example/alerts/CC-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "CC-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://crisescontrol.example/alerts/CC-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "crisescontrol-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "crisescontrol-job-9",
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
                  "progress_percent": 67,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "crisescontrol-body-9",
                },
                "remediation_provider_telemetry_url": "https://crisescontrol-engine.example/recovery/crisescontrol-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://crisescontrol-engine.example/recovery/crisescontrol-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Crises Control engine is verifying restored channels",
              "external_run_id": "crisescontrol-engine-9",
              "updated_at": "2025-01-03T16:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("crisescontrol",),
    crisescontrol_api_token="crisescontrol-token",
    crisescontrol_api_url="https://api.crisescontrol.example",
    crisescontrol_recovery_engine_url_template=(
      "https://crisescontrol-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    crisescontrol_recovery_engine_token="crisescontrol-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-crisescontrol-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="crisescontrol",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="CC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="crisescontrol",
  )

  assert snapshot is not None
  assert snapshot.provider == "crisescontrol"
  assert snapshot.workflow_reference == "CC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "crisescontrol-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "crisescontrol"
  assert snapshot.payload["provider_schema"]["crisescontrol"]["alert_id"] == "CC-123"
  assert snapshot.payload["provider_schema"]["crisescontrol"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["crisescontrol"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["crisescontrol"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["crisescontrol"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["crisescontrol"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Crises Control engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "crisescontrol-engine-9"
  assert requests[0][0].endswith("/alerts/CC-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer crisescontrol-token"
  assert requests[1][0] == "https://crisescontrol-engine.example/recovery/crisescontrol-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer crisescontrol-recovery-token"


def test_operator_alert_delivery_adapter_supports_freshservice_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("freshservice",),
    freshservice_api_token="freshservice-token",
    freshservice_api_url="https://api.freshservice.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-freshservice-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-freshservice-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 40, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("freshservice_incidents",)
  assert opened_records[0].target == "freshservice_incidents"
  assert opened_records[0].external_provider == "freshservice"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.freshservice.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer freshservice-token"
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


def test_operator_alert_delivery_adapter_syncs_freshservice_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("freshservice",),
    freshservice_api_token="freshservice-token",
    freshservice_api_url="https://api.freshservice.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-freshservice-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="freshservice",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="FS-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="freshservice",
        job_id="freshservice-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshservice",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshservice",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshservice",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "freshservice-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshservice",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "freshservice-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("freshservice",)
  assert acknowledge[0].target == "freshservice_workflow"
  assert acknowledge[0].external_reference == "FS-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/FS-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/FS-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/FS-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/FS-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer freshservice-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "freshservice-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "freshservice-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_freshservice_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.freshservice.example/alerts/FS-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "FS-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://freshservice.example/alerts/FS-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "freshservice-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "freshservice-job-9",
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
                  "progress_percent": 67,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "freshservice-body-9",
                },
                "remediation_provider_telemetry_url": "https://freshservice-engine.example/recovery/freshservice-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://freshservice-engine.example/recovery/freshservice-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Freshservice engine is verifying restored channels",
              "external_run_id": "freshservice-engine-9",
              "updated_at": "2025-01-03T16:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("freshservice",),
    freshservice_api_token="freshservice-token",
    freshservice_api_url="https://api.freshservice.example",
    freshservice_recovery_engine_url_template=(
      "https://freshservice-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    freshservice_recovery_engine_token="freshservice-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-freshservice-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="freshservice",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="FS-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="freshservice",
  )

  assert snapshot is not None
  assert snapshot.provider == "freshservice"
  assert snapshot.workflow_reference == "FS-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "freshservice-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "freshservice"
  assert snapshot.payload["provider_schema"]["freshservice"]["alert_id"] == "FS-123"
  assert snapshot.payload["provider_schema"]["freshservice"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["freshservice"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["freshservice"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["freshservice"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["freshservice"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Freshservice engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "freshservice-engine-9"
  assert requests[0][0].endswith("/alerts/FS-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer freshservice-token"
  assert requests[1][0] == "https://freshservice-engine.example/recovery/freshservice-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer freshservice-recovery-token"


def test_operator_alert_delivery_adapter_supports_freshdesk_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("freshdesk",),
    freshdesk_api_token="freshdesk-token",
    freshdesk_api_url="https://api.freshdesk.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-freshdesk-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 44, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-freshdesk-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 45, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("freshdesk_incidents",)
  assert opened_records[0].target == "freshdesk_incidents"
  assert opened_records[0].external_provider == "freshdesk"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.freshdesk.example/tickets"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer freshdesk-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["ticket"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["ticket"]["priority"] == "high"
  assert create_payload["ticket"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/tickets/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_freshdesk_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("freshdesk",),
    freshdesk_api_token="freshdesk-token",
    freshdesk_api_url="https://api.freshdesk.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-freshdesk-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="freshdesk",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="FD-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="freshdesk",
        job_id="freshdesk-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshdesk",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshdesk",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshdesk",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "freshdesk-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="freshdesk",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "freshdesk-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("freshdesk",)
  assert acknowledge[0].target == "freshdesk_workflow"
  assert acknowledge[0].external_reference == "FD-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/tickets/FD-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/tickets/FD-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/tickets/FD-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/tickets/FD-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer freshdesk-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "freshdesk-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "freshdesk-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_freshdesk_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.freshdesk.example/tickets/FD-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "ticket": {
              "alert_id": "FD-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:47:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://freshdesk.example/tickets/FD-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "freshdesk-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "freshdesk-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "ticket_body",
                  "last_message": "ticket body telemetry is lagging",
                  "external_run_id": "freshdesk-body-9",
                },
                "remediation_provider_telemetry_url": "https://freshdesk-engine.example/recovery/freshdesk-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://freshdesk-engine.example/recovery/freshdesk-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 96,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Freshdesk engine is verifying restored channels",
              "external_run_id": "freshdesk-engine-9",
              "updated_at": "2025-01-03T16:48:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("freshdesk",),
    freshdesk_api_token="freshdesk-token",
    freshdesk_api_url="https://api.freshdesk.example",
    freshdesk_recovery_engine_url_template=(
      "https://freshdesk-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    freshdesk_recovery_engine_token="freshdesk-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-freshdesk-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="freshdesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="FD-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="freshdesk",
  )

  assert snapshot is not None
  assert snapshot.provider == "freshdesk"
  assert snapshot.workflow_reference == "FD-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "freshdesk-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "freshdesk"
  assert snapshot.payload["provider_schema"]["freshdesk"]["alert_id"] == "FD-123"
  assert snapshot.payload["provider_schema"]["freshdesk"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["freshdesk"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["freshdesk"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["freshdesk"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["freshdesk"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 96
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Freshdesk engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "freshdesk-engine-9"
  assert requests[0][0].endswith("/tickets/FD-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer freshdesk-token"
  assert requests[1][0] == "https://freshdesk-engine.example/recovery/freshdesk-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer freshdesk-recovery-token"


def test_operator_alert_delivery_adapter_supports_happyfox_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("happyfox",),
    happyfox_api_token="happyfox-token",
    happyfox_api_url="https://api.happyfox.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-happyfox-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 44, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-happyfox-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 45, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("happyfox_incidents",)
  assert opened_records[0].target == "happyfox_incidents"
  assert opened_records[0].external_provider == "happyfox"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.happyfox.example/tickets"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer happyfox-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["ticket"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["ticket"]["priority"] == "high"
  assert create_payload["ticket"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/tickets/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_happyfox_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("happyfox",),
    happyfox_api_token="happyfox-token",
    happyfox_api_url="https://api.happyfox.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-happyfox-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="happyfox",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="HF-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="happyfox",
        job_id="happyfox-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="happyfox",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="happyfox",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="happyfox",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "happyfox-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="happyfox",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "happyfox-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("happyfox",)
  assert acknowledge[0].target == "happyfox_workflow"
  assert acknowledge[0].external_reference == "HF-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/tickets/HF-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/tickets/HF-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/tickets/HF-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/tickets/HF-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer happyfox-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "happyfox-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "happyfox-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_happyfox_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.happyfox.example/tickets/HF-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "ticket": {
              "alert_id": "HF-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:47:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://happyfox.example/tickets/HF-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "happyfox-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "happyfox-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "ticket_body",
                  "last_message": "ticket body telemetry is lagging",
                  "external_run_id": "happyfox-body-9",
                },
                "remediation_provider_telemetry_url": "https://happyfox-engine.example/recovery/happyfox-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://happyfox-engine.example/recovery/happyfox-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 96,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "HappyFox engine is verifying restored channels",
              "external_run_id": "happyfox-engine-9",
              "updated_at": "2025-01-03T16:48:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("happyfox",),
    happyfox_api_token="happyfox-token",
    happyfox_api_url="https://api.happyfox.example",
    happyfox_recovery_engine_url_template=(
      "https://happyfox-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    happyfox_recovery_engine_token="happyfox-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-happyfox-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="happyfox",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="HF-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="happyfox",
  )

  assert snapshot is not None
  assert snapshot.provider == "happyfox"
  assert snapshot.workflow_reference == "HF-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "happyfox-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "happyfox"
  assert snapshot.payload["provider_schema"]["happyfox"]["alert_id"] == "HF-123"
  assert snapshot.payload["provider_schema"]["happyfox"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["happyfox"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["happyfox"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["happyfox"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["happyfox"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 96
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "HappyFox engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "happyfox-engine-9"
  assert requests[0][0].endswith("/tickets/HF-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer happyfox-token"
  assert requests[1][0] == "https://happyfox-engine.example/recovery/happyfox-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer happyfox-recovery-token"


def test_operator_alert_delivery_adapter_supports_zendesk_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zendesk",),
    zendesk_api_token="zendesk-token",
    zendesk_api_url="https://api.zendesk.example/api/v2",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-zendesk-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 44, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-zendesk-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 45, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("zendesk_incidents",)
  assert opened_records[0].target == "zendesk_incidents"
  assert opened_records[0].external_provider == "zendesk"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.zendesk.example/api/v2/tickets"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer zendesk-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["ticket"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["ticket"]["priority"] == "high"
  assert create_payload["ticket"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/tickets/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_zendesk_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zendesk",),
    zendesk_api_token="zendesk-token",
    zendesk_api_url="https://api.zendesk.example/api/v2",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-zendesk-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="zendesk",
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
        provider="zendesk",
        job_id="zendesk-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="zendesk",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="zendesk",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="zendesk",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "zendesk-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="zendesk",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "zendesk-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("zendesk",)
  assert acknowledge[0].target == "zendesk_workflow"
  assert acknowledge[0].external_reference == "ZD-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/tickets/ZD-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/tickets/ZD-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/tickets/ZD-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/tickets/ZD-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer zendesk-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "zendesk-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "zendesk-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_zendesk_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.zendesk.example/api/v2/tickets/ZD-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "ticket": {
              "alert_id": "ZD-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:47:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://zendesk.example/tickets/ZD-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "zendesk-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "zendesk-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "ticket_body",
                  "last_message": "ticket body telemetry is lagging",
                  "external_run_id": "zendesk-body-9",
                },
                "remediation_provider_telemetry_url": "https://zendesk-engine.example/recovery/zendesk-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://zendesk-engine.example/recovery/zendesk-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 96,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Zendesk engine is verifying restored channels",
              "external_run_id": "zendesk-engine-9",
              "updated_at": "2025-01-03T16:48:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zendesk",),
    zendesk_api_token="zendesk-token",
    zendesk_api_url="https://api.zendesk.example/api/v2",
    zendesk_recovery_engine_url_template=(
      "https://zendesk-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    zendesk_recovery_engine_token="zendesk-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-zendesk-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="zendesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="ZD-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="zendesk",
  )

  assert snapshot is not None
  assert snapshot.provider == "zendesk"
  assert snapshot.workflow_reference == "ZD-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "zendesk-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "zendesk"
  assert snapshot.payload["provider_schema"]["zendesk"]["alert_id"] == "ZD-123"
  assert snapshot.payload["provider_schema"]["zendesk"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["zendesk"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["zendesk"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["zendesk"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["zendesk"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 96
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Zendesk engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "zendesk-engine-9"
  assert requests[0][0].endswith("/tickets/ZD-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer zendesk-token"
  assert requests[1][0] == "https://zendesk-engine.example/recovery/zendesk-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer zendesk-recovery-token"


def test_operator_alert_delivery_adapter_supports_zohodesk_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zohodesk",),
    zohodesk_api_token="zohodesk-token",
    zohodesk_api_url="https://desk.zoho.example/api/v1",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-zohodesk-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 45, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed.",
    detail="worker heartbeat timed out",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-zohodesk-1",
    alert_id=opened.alert_id,
    timestamp=opened.timestamp,
    kind="incident_resolved",
    severity=opened.severity,
    summary=opened.summary,
    detail="live worker recovered",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("zohodesk_incidents",)
  assert opened_records[0].target == "zohodesk_incidents"
  assert opened_records[0].external_provider == "zohodesk"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://desk.zoho.example/api/v1/tickets"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer zohodesk-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["ticket"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["ticket"]["priority"] == "high"
  assert create_payload["ticket"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/tickets/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_zohodesk_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zohodesk",),
    zohodesk_api_token="zohodesk-token",
    zohodesk_api_url="https://desk.zoho.example/api/v1",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-zohodesk-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="zohodesk",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="ZHD-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="zohodesk",
        job_id="zohodesk-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="zohodesk",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="zohodesk",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="zohodesk",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "zohodesk-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="zohodesk",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "zohodesk-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("zohodesk",)
  assert acknowledge[0].target == "zohodesk_workflow"
  assert acknowledge[0].external_reference == "ZHD-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/tickets/ZHD-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/tickets/ZHD-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/tickets/ZHD-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/tickets/ZHD-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer zohodesk-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "zohodesk-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "zohodesk-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_zohodesk_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://desk.zoho.example/api/v1/tickets/ZHD-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "ticket": {
              "alert_id": "ZHD-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:47:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://desk.zoho.example/tickets/ZHD-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "zohodesk-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "zohodesk-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "ticket_body",
                  "last_message": "ticket body telemetry is lagging",
                  "external_run_id": "zohodesk-body-9",
                },
                "remediation_provider_telemetry_url": "https://zohodesk-engine.example/recovery/zohodesk-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://zohodesk-engine.example/recovery/zohodesk-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 96,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Zoho Desk engine is verifying restored channels",
              "external_run_id": "zohodesk-engine-9",
              "updated_at": "2025-01-03T16:48:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("zohodesk",),
    zohodesk_api_token="zohodesk-token",
    zohodesk_api_url="https://desk.zoho.example/api/v1",
    zohodesk_recovery_engine_url_template=(
      "https://zohodesk-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    zohodesk_recovery_engine_token="zohodesk-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-zohodesk-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 46, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="zohodesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="ZHD-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="zohodesk",
  )

  assert snapshot is not None
  assert snapshot.provider == "zohodesk"
  assert snapshot.workflow_reference == "ZHD-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "zohodesk-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "zohodesk"
  assert snapshot.payload["provider_schema"]["zohodesk"]["alert_id"] == "ZHD-123"
  assert snapshot.payload["provider_schema"]["zohodesk"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["zohodesk"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["zohodesk"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["zohodesk"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["zohodesk"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 96
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Zoho Desk engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "zohodesk-engine-9"
  assert requests[0][0].endswith("/tickets/ZHD-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer zohodesk-token"
  assert requests[1][0] == "https://zohodesk-engine.example/recovery/zohodesk-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer zohodesk-recovery-token"


def test_operator_alert_delivery_adapter_supports_helpscout_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("helpscout",),
    helpscout_api_token="helpscout-token",
    helpscout_api_url="https://api.helpscout.example/v2",
    webhook_timeout_seconds=9,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-helpscout-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data freshness degraded.",
    detail="market-data freshness degraded",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-helpscout-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 33, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live market-data freshness degraded.",
    detail="market-data freshness recovered",
    external_reference="guarded-live:market-data:5m",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("helpscout_incidents",)
  assert opened_records[0].target == "helpscout_incidents"
  assert opened_records[0].external_provider == "helpscout"
  assert resolved_records[0].external_reference == "guarded-live:market-data:5m"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.helpscout.example/v2/conversations"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer helpscout-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["conversation"]["external_reference"] == "guarded-live:market-data:5m"
  assert create_payload["conversation"]["priority"] == "high"
  assert create_payload["conversation"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/conversations/guarded-live%3Amarket-data%3A5m/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "market-data freshness recovered"


def test_operator_alert_delivery_adapter_syncs_helpscout_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("helpscout",),
    helpscout_api_token="helpscout-token",
    helpscout_api_url="https://api.helpscout.example/v2",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-helpscout-2",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data freshness degraded.",
    detail="market-data freshness degraded",
    external_provider="helpscout",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="HS-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="suggested",
      kind="recent_sync",
      runbook="market_data.sync_recent",
      summary="Refresh the live timeframe sync window.",
      provider="helpscout",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        provider="helpscout",
        job_id="helpscout-job-existing",
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="helpscout",
    action="acknowledge",
    actor="operator",
    detail="operator acknowledged",
    payload=None,
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="helpscout",
    action="escalate",
    actor="operator",
    detail="operator escalated",
    payload=None,
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="helpscout",
    action="resolve",
    actor="operator",
    detail="recovered",
    payload={"job_id": "helpscout-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="helpscout",
    action="remediate",
    actor="operator",
    detail="requested remediation",
    payload={"job_id": "helpscout-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("helpscout",)
  assert acknowledge[0].target == "helpscout_workflow"
  assert escalate[0].target == "helpscout_workflow"
  assert resolve[0].target == "helpscout_workflow"
  assert remediate[0].target == "helpscout_workflow"

  assert requests[0][0] == "https://api.helpscout.example/v2/conversations/HS-123/acknowledge?identifier_type=id"
  assert requests[1][0] == "https://api.helpscout.example/v2/conversations/HS-123/escalate?identifier_type=id"
  assert requests[2][0] == "https://api.helpscout.example/v2/conversations/HS-123/resolve?identifier_type=id"
  assert requests[3][0] == "https://api.helpscout.example/v2/conversations/HS-123/remediate?identifier_type=id"
  assert requests[0][3]["Authorization"] == "Bearer helpscout-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "helpscout-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "helpscout-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_helpscout_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.helpscout.example/v2/conversations/HS-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "HS-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T18:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://api.helpscout.example/conversations/HS-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "helpscout-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "helpscout-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "conversation_body",
                  "last_message": "conversation telemetry is lagging",
                  "external_run_id": "helpscout-body-9",
                },
                "remediation_provider_telemetry_url": "https://helpscout-engine.example/recovery/helpscout-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://helpscout-engine.example/recovery/helpscout-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Help Scout engine is verifying restored channels",
              "external_run_id": "helpscout-engine-9",
              "updated_at": "2025-01-03T18:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("helpscout",),
    helpscout_api_token="helpscout-token",
    helpscout_api_url="https://api.helpscout.example/v2",
    helpscout_recovery_engine_url_template=(
      "https://helpscout-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    helpscout_recovery_engine_token="helpscout-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-helpscout-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="helpscout",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="HS-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="helpscout",
  )

  assert snapshot is not None
  assert snapshot.provider == "helpscout"
  assert snapshot.workflow_reference == "HS-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "helpscout-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "helpscout"
  assert snapshot.payload["provider_schema"]["helpscout"]["alert_id"] == "HS-123"
  assert snapshot.payload["provider_schema"]["helpscout"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["helpscout"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["helpscout"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["helpscout"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["helpscout"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 95
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Help Scout engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "helpscout-engine-9"
  assert requests[0][0] == "https://api.helpscout.example/v2/conversations/HS-123?identifier_type=id"
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer helpscout-token"
  assert requests[1][0] == "https://helpscout-engine.example/recovery/helpscout-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer helpscout-recovery-token"


def test_operator_alert_delivery_adapter_supports_kayako_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("kayako",),
    kayako_api_token="kayako-token",
    kayako_api_url="https://api.kayako.example/v1",
    webhook_timeout_seconds=9,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-kayako-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data freshness degraded.",
    detail="market-data freshness degraded",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-kayako-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 33, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live market-data freshness degraded.",
    detail="market-data freshness recovered",
    external_reference="guarded-live:market-data:5m",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("kayako_incidents",)
  assert opened_records[0].target == "kayako_incidents"
  assert opened_records[0].external_provider == "kayako"
  assert resolved_records[0].external_reference == "guarded-live:market-data:5m"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.kayako.example/v1/cases"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer kayako-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["case"]["external_reference"] == "guarded-live:market-data:5m"
  assert create_payload["case"]["priority"] == "high"
  assert create_payload["case"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/cases/guarded-live%3Amarket-data%3A5m/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "market-data freshness recovered"


def test_operator_alert_delivery_adapter_syncs_kayako_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("kayako",),
    kayako_api_token="kayako-token",
    kayako_api_url="https://api.kayako.example/v1",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-kayako-2",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data freshness degraded.",
    detail="market-data freshness degraded",
    external_provider="kayako",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="KY-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="suggested",
      kind="recent_sync",
      runbook="market_data.sync_recent",
      summary="Refresh the live timeframe sync window.",
      provider="kayako",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        provider="kayako",
        job_id="kayako-job-existing",
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="kayako",
    action="acknowledge",
    actor="operator",
    detail="operator acknowledged",
    payload=None,
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="kayako",
    action="escalate",
    actor="operator",
    detail="operator escalated",
    payload=None,
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="kayako",
    action="resolve",
    actor="operator",
    detail="recovered",
    payload={"job_id": "kayako-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="kayako",
    action="remediate",
    actor="operator",
    detail="requested remediation",
    payload={"job_id": "kayako-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("kayako",)
  assert acknowledge[0].target == "kayako_workflow"
  assert escalate[0].target == "kayako_workflow"
  assert resolve[0].target == "kayako_workflow"
  assert remediate[0].target == "kayako_workflow"

  assert requests[0][0] == "https://api.kayako.example/v1/cases/KY-123/acknowledge?identifier_type=id"
  assert requests[1][0] == "https://api.kayako.example/v1/cases/KY-123/escalate?identifier_type=id"
  assert requests[2][0] == "https://api.kayako.example/v1/cases/KY-123/resolve?identifier_type=id"
  assert requests[3][0] == "https://api.kayako.example/v1/cases/KY-123/remediate?identifier_type=id"
  assert requests[0][3]["Authorization"] == "Bearer kayako-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "kayako-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "kayako-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_kayako_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.kayako.example/v1/cases/KY-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "KY-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T18:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://api.kayako.example/cases/KY-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "kayako-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "kayako-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "case_body",
                  "last_message": "case telemetry is lagging",
                  "external_run_id": "kayako-body-9",
                },
                "remediation_provider_telemetry_url": "https://kayako-engine.example/recovery/kayako-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://kayako-engine.example/recovery/kayako-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Kayako engine is verifying restored channels",
              "external_run_id": "kayako-engine-9",
              "updated_at": "2025-01-03T18:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("kayako",),
    kayako_api_token="kayako-token",
    kayako_api_url="https://api.kayako.example/v1",
    kayako_recovery_engine_url_template=(
      "https://kayako-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    kayako_recovery_engine_token="kayako-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-kayako-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="kayako",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="KY-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="kayako",
  )

  assert snapshot is not None
  assert snapshot.provider == "kayako"
  assert snapshot.workflow_reference == "KY-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "kayako-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "kayako"
  assert snapshot.payload["provider_schema"]["kayako"]["alert_id"] == "KY-123"
  assert snapshot.payload["provider_schema"]["kayako"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["kayako"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["kayako"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["kayako"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["kayako"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 95
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Kayako engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "kayako-engine-9"
  assert requests[0][0] == "https://api.kayako.example/v1/cases/KY-123?identifier_type=id"
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer kayako-token"
  assert requests[1][0] == "https://kayako-engine.example/recovery/kayako-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer kayako-recovery-token"


def test_operator_alert_delivery_adapter_supports_intercom_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("intercom",),
    intercom_api_token="intercom-token",
    intercom_api_url="https://api.intercom.example",
    webhook_timeout_seconds=9,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-intercom-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data freshness degraded.",
    detail="market-data freshness degraded",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-intercom-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 33, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live market-data freshness degraded.",
    detail="market-data freshness recovered",
    external_reference="guarded-live:market-data:5m",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("intercom_incidents",)
  assert opened_records[0].target == "intercom_incidents"
  assert opened_records[0].external_provider == "intercom"
  assert resolved_records[0].external_reference == "guarded-live:market-data:5m"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.intercom.example/conversations"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer intercom-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["conversation"]["external_reference"] == "guarded-live:market-data:5m"
  assert create_payload["conversation"]["priority"] == "high"
  assert create_payload["conversation"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/conversations/guarded-live%3Amarket-data%3A5m/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "market-data freshness recovered"


def test_operator_alert_delivery_adapter_syncs_intercom_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("intercom",),
    intercom_api_token="intercom-token",
    intercom_api_url="https://api.intercom.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-intercom-2",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data freshness degraded.",
    detail="market-data freshness degraded",
    external_provider="intercom",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="IC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="suggested",
      kind="recent_sync",
      runbook="market_data.sync_recent",
      summary="Refresh the live timeframe sync window.",
      provider="intercom",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        provider="intercom",
        job_id="intercom-job-existing",
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="intercom",
    action="acknowledge",
    actor="operator",
    detail="operator acknowledged",
    payload=None,
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="intercom",
    action="escalate",
    actor="operator",
    detail="operator escalated",
    payload=None,
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="intercom",
    action="resolve",
    actor="operator",
    detail="recovered",
    payload={"job_id": "intercom-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="intercom",
    action="remediate",
    actor="operator",
    detail="requested remediation",
    payload={"job_id": "intercom-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("intercom",)
  assert acknowledge[0].target == "intercom_workflow"
  assert escalate[0].target == "intercom_workflow"
  assert resolve[0].target == "intercom_workflow"
  assert remediate[0].target == "intercom_workflow"

  assert requests[0][0] == "https://api.intercom.example/conversations/IC-123/acknowledge?identifier_type=id"
  assert requests[1][0] == "https://api.intercom.example/conversations/IC-123/escalate?identifier_type=id"
  assert requests[2][0] == "https://api.intercom.example/conversations/IC-123/resolve?identifier_type=id"
  assert requests[3][0] == "https://api.intercom.example/conversations/IC-123/remediate?identifier_type=id"
  assert requests[0][3]["Authorization"] == "Bearer intercom-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "intercom-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "intercom-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_intercom_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.intercom.example/conversations/IC-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "IC-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T18:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://api.intercom.example/conversations/IC-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "intercom-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "intercom-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "conversation_body",
                  "last_message": "conversation telemetry is lagging",
                  "external_run_id": "intercom-body-9",
                },
                "remediation_provider_telemetry_url": "https://intercom-engine.example/recovery/intercom-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://intercom-engine.example/recovery/intercom-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Intercom engine is verifying restored channels",
              "external_run_id": "intercom-engine-9",
              "updated_at": "2025-01-03T18:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("intercom",),
    intercom_api_token="intercom-token",
    intercom_api_url="https://api.intercom.example",
    intercom_recovery_engine_url_template=(
      "https://intercom-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    intercom_recovery_engine_token="intercom-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-intercom-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="intercom",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="IC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="intercom",
  )

  assert snapshot is not None
  assert snapshot.provider == "intercom"
  assert snapshot.workflow_reference == "IC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "intercom-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "intercom"
  assert snapshot.payload["provider_schema"]["intercom"]["alert_id"] == "IC-123"
  assert snapshot.payload["provider_schema"]["intercom"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["intercom"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["intercom"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["intercom"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["intercom"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 95
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Intercom engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "intercom-engine-9"
  assert requests[0][0] == "https://api.intercom.example/conversations/IC-123?identifier_type=id"
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer intercom-token"
  assert requests[1][0] == "https://intercom-engine.example/recovery/intercom-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer intercom-recovery-token"


def test_operator_alert_delivery_adapter_supports_front_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("front",),
    front_api_token="front-token",
    front_api_url="https://api.front.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-front-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 18, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-front-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 18, 40, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("front_incidents",)
  assert opened_records[0].target == "front_incidents"
  assert opened_records[0].external_provider == "front"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.front.example/conversations"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer front-token"
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["conversation"]["external_reference"] == "guarded-live:worker-failed:run-1"
  assert create_payload["conversation"]["priority"] == "high"
  assert create_payload["conversation"]["status"] == "pending"

  assert resolve_request[0].endswith(
    "/conversations/guarded-live%3Aworker-failed%3Arun-1/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "live worker recovered"


def test_operator_alert_delivery_adapter_syncs_front_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("front",),
    front_api_token="front-token",
    front_api_url="https://api.front.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-front-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 18, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="front",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="FR-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        provider="front",
        job_id="front-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="front",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="front",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="front",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "front-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="front",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "front-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("front",)
  assert acknowledge[0].target == "front_workflow"
  assert escalate[0].target == "front_workflow"
  assert resolve[0].target == "front_workflow"
  assert remediate[0].target == "front_workflow"

  assert requests[0][0] == "https://api.front.example/conversations/FR-123/acknowledge?identifier_type=id"
  assert requests[1][0] == "https://api.front.example/conversations/FR-123/escalate?identifier_type=id"
  assert requests[2][0] == "https://api.front.example/conversations/FR-123/resolve?identifier_type=id"
  assert requests[3][0] == "https://api.front.example/conversations/FR-123/remediate?identifier_type=id"
  assert requests[0][3]["Authorization"] == "Bearer front-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "front-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "front-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_front_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.front.example/conversations/FR-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "FR-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T18:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://api.front.example/conversations/FR-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "front-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "front-job-9",
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
                  "progress_percent": 68,
                  "attempt_count": 1,
                  "current_step": "conversation_body",
                  "last_message": "conversation telemetry is lagging",
                  "external_run_id": "front-body-9",
                },
                "remediation_provider_telemetry_url": "https://front-engine.example/recovery/front-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://front-engine.example/recovery/front-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Front engine is verifying restored channels",
              "external_run_id": "front-engine-9",
              "updated_at": "2025-01-03T18:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("front",),
    front_api_token="front-token",
    front_api_url="https://api.front.example",
    front_recovery_engine_url_template=(
      "https://front-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    front_recovery_engine_token="front-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-front-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 18, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="front",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="FR-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="front",
  )

  assert snapshot is not None
  assert snapshot.provider == "front"
  assert snapshot.workflow_reference == "FR-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "front-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "front"
  assert snapshot.payload["provider_schema"]["front"]["alert_id"] == "FR-123"
  assert snapshot.payload["provider_schema"]["front"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["front"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["front"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["front"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["front"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 95
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Front engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "front-engine-9"
  assert requests[0][0] == "https://api.front.example/conversations/FR-123?identifier_type=id"
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer front-token"
  assert requests[1][0] == "https://front-engine.example/recovery/front-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer front-recovery-token"


def test_operator_alert_delivery_adapter_supports_servicedeskplus_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("servicedeskplus",),
    servicedeskplus_api_token="servicedeskplus-token",
    servicedeskplus_api_url="https://api.servicedeskplus.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-servicedeskplus-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-servicedeskplus-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 40, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("servicedeskplus_incidents",)
  assert opened_records[0].target == "servicedeskplus_incidents"
  assert opened_records[0].external_provider == "servicedeskplus"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.servicedeskplus.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer servicedeskplus-token"
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


def test_operator_alert_delivery_adapter_syncs_servicedeskplus_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("servicedeskplus",),
    servicedeskplus_api_token="servicedeskplus-token",
    servicedeskplus_api_url="https://api.servicedeskplus.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-servicedeskplus-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="servicedeskplus",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="SDP-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="servicedeskplus",
        job_id="servicedeskplus-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicedeskplus",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicedeskplus",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicedeskplus",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "servicedeskplus-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="servicedeskplus",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "servicedeskplus-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("servicedeskplus",)
  assert acknowledge[0].target == "servicedeskplus_workflow"
  assert acknowledge[0].external_reference == "SDP-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/SDP-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/SDP-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/SDP-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/SDP-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer servicedeskplus-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "servicedeskplus-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "servicedeskplus-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_servicedeskplus_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.servicedeskplus.example/alerts/SDP-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "SDP-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://servicedeskplus.example/alerts/SDP-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "servicedeskplus-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "servicedeskplus-job-9",
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
                  "progress_percent": 67,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "servicedeskplus-body-9",
                },
                "remediation_provider_telemetry_url": "https://servicedeskplus-engine.example/recovery/servicedeskplus-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://servicedeskplus-engine.example/recovery/servicedeskplus-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "ServiceDesk Plus engine is verifying restored channels",
              "external_run_id": "servicedeskplus-engine-9",
              "updated_at": "2025-01-03T16:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("servicedeskplus",),
    servicedeskplus_api_token="servicedeskplus-token",
    servicedeskplus_api_url="https://api.servicedeskplus.example",
    servicedeskplus_recovery_engine_url_template=(
      "https://servicedeskplus-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    servicedeskplus_recovery_engine_token="servicedeskplus-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-servicedeskplus-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="servicedeskplus",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SDP-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="servicedeskplus",
  )

  assert snapshot is not None
  assert snapshot.provider == "servicedeskplus"
  assert snapshot.workflow_reference == "SDP-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "servicedeskplus-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "servicedeskplus"
  assert snapshot.payload["provider_schema"]["servicedeskplus"]["alert_id"] == "SDP-123"
  assert snapshot.payload["provider_schema"]["servicedeskplus"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["servicedeskplus"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["servicedeskplus"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["servicedeskplus"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["servicedeskplus"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "ServiceDesk Plus engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "servicedeskplus-engine-9"
  assert requests[0][0].endswith("/alerts/SDP-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer servicedeskplus-token"
  assert requests[1][0] == "https://servicedeskplus-engine.example/recovery/servicedeskplus-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer servicedeskplus-recovery-token"


def test_operator_alert_delivery_adapter_supports_sysaid_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("sysaid",),
    sysaid_api_token="sysaid-token",
    sysaid_api_url="https://api.sysaid.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-sysaid-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 49, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-sysaid-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 50, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("sysaid_incidents",)
  assert opened_records[0].target == "sysaid_incidents"
  assert opened_records[0].external_provider == "sysaid"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.sysaid.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer sysaid-token"
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


def test_operator_alert_delivery_adapter_syncs_sysaid_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("sysaid",),
    sysaid_api_token="sysaid-token",
    sysaid_api_url="https://api.sysaid.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-sysaid-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 51, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="sysaid",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="SYSAID-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="sysaid",
        job_id="sysaid-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="sysaid",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="sysaid",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="sysaid",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "sysaid-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="sysaid",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "sysaid-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("sysaid",)
  assert acknowledge[0].target == "sysaid_workflow"
  assert acknowledge[0].external_reference == "SYSAID-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/SYSAID-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/SYSAID-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/SYSAID-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/SYSAID-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer sysaid-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "sysaid-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "sysaid-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_sysaid_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.sysaid.example/alerts/SYSAID-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "SYSAID-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:52:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://sysaid.example/alerts/SYSAID-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "sysaid-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "sysaid-job-9",
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
                  "progress_percent": 67,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "sysaid-body-9",
                },
                "remediation_provider_telemetry_url": "https://sysaid-engine.example/recovery/sysaid-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://sysaid-engine.example/recovery/sysaid-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 93,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "SysAid engine is verifying restored channels",
              "external_run_id": "sysaid-engine-9",
              "updated_at": "2025-01-03T16:53:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("sysaid",),
    sysaid_api_token="sysaid-token",
    sysaid_api_url="https://api.sysaid.example",
    sysaid_recovery_engine_url_template=(
      "https://sysaid-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    sysaid_recovery_engine_token="sysaid-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-sysaid-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 51, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="sysaid",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SYSAID-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="sysaid",
  )

  assert snapshot is not None
  assert snapshot.provider == "sysaid"
  assert snapshot.workflow_reference == "SYSAID-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "sysaid-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "sysaid"
  assert snapshot.payload["provider_schema"]["sysaid"]["alert_id"] == "SYSAID-123"
  assert snapshot.payload["provider_schema"]["sysaid"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["sysaid"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["sysaid"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["sysaid"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["sysaid"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 93
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "SysAid engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "sysaid-engine-9"
  assert requests[0][0].endswith("/alerts/SYSAID-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer sysaid-token"
  assert requests[1][0] == "https://sysaid-engine.example/recovery/sysaid-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer sysaid-recovery-token"


def test_operator_alert_delivery_adapter_supports_bmchelix_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("bmchelix",),
    bmchelix_api_token="bmchelix-token",
    bmchelix_api_url="https://api.bmchelix.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-bmchelix-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 17, 1, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-bmchelix-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 17, 2, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("bmchelix_incidents",)
  assert opened_records[0].target == "bmchelix_incidents"
  assert opened_records[0].external_provider == "bmchelix"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.bmchelix.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer bmchelix-token"
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


def test_operator_alert_delivery_adapter_syncs_bmchelix_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("bmchelix",),
    bmchelix_api_token="bmchelix-token",
    bmchelix_api_url="https://api.bmchelix.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-bmchelix-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 17, 3, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="bmchelix",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="BMC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="bmchelix",
        job_id="bmchelix-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="bmchelix",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="bmchelix",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="bmchelix",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "bmchelix-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="bmchelix",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "bmchelix-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("bmchelix",)
  assert acknowledge[0].target == "bmchelix_workflow"
  assert acknowledge[0].external_reference == "BMC-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/BMC-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/BMC-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/BMC-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/BMC-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer bmchelix-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "bmchelix-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "bmchelix-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_bmchelix_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.bmchelix.example/alerts/BMC-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "BMC-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T17:04:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://bmchelix.example/alerts/BMC-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "bmchelix-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "bmchelix-job-9",
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
                  "progress_percent": 67,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "bmchelix-body-9",
                },
                "remediation_provider_telemetry_url": "https://bmchelix-engine.example/recovery/bmchelix-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://bmchelix-engine.example/recovery/bmchelix-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "BMC Helix engine is verifying restored channels",
              "external_run_id": "bmchelix-engine-9",
              "updated_at": "2025-01-03T17:05:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("bmchelix",),
    bmchelix_api_token="bmchelix-token",
    bmchelix_api_url="https://api.bmchelix.example",
    bmchelix_recovery_engine_url_template=(
      "https://bmchelix-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    bmchelix_recovery_engine_token="bmchelix-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-bmchelix-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 17, 3, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="bmchelix",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="BMC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="bmchelix",
  )

  assert snapshot is not None
  assert snapshot.provider == "bmchelix"
  assert snapshot.workflow_reference == "BMC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "bmchelix-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "bmchelix"
  assert snapshot.payload["provider_schema"]["bmchelix"]["alert_id"] == "BMC-123"
  assert snapshot.payload["provider_schema"]["bmchelix"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["bmchelix"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["bmchelix"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["bmchelix"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["bmchelix"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 95
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "BMC Helix engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "bmchelix-engine-9"
  assert requests[0][0].endswith("/alerts/BMC-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer bmchelix-token"
  assert requests[1][0] == "https://bmchelix-engine.example/recovery/bmchelix-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer bmchelix-recovery-token"


def test_operator_alert_delivery_adapter_supports_solarwindsservicedesk_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def handler(request, timeout: float):
    body = request.data or b""
    requests.append((request.full_url, request.method, body, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("solarwindsservicedesk",),
    solarwindsservicedesk_api_token="solarwindsservicedesk-token",
    solarwindsservicedesk_api_url="https://api.solarwindsservicedesk.example",
    webhook_timeout_seconds=17,
    urlopen=handler,
  )
  opened_records = adapter.deliver(
    incident=OperatorIncidentEvent(
      event_id="incident-opened-solarwindsservicedesk-1",
      alert_id="guarded-live:market-data:5m",
      timestamp=datetime(2025, 1, 3, 17, 0, tzinfo=UTC),
      kind="incident_opened",
      severity="warning",
      summary="Guarded-live market-data incident",
      detail="market-data freshness degraded",
    ),
  )
  resolved_records = adapter.deliver(
    incident=OperatorIncidentEvent(
      event_id="incident-resolved-solarwindsservicedesk-1",
      alert_id="guarded-live:market-data:5m",
      timestamp=datetime(2025, 1, 3, 17, 2, tzinfo=UTC),
      kind="incident_resolved",
      severity="warning",
      summary="Guarded-live market-data incident resolved",
      detail="market-data freshness recovered",
      external_reference="guarded-live:market-data:5m",
    ),
  )

  assert adapter.list_targets() == ("solarwindsservicedesk_incidents",)
  assert opened_records[0].target == "solarwindsservicedesk_incidents"
  assert opened_records[0].external_provider == "solarwindsservicedesk"
  assert opened_records[0].status == "delivered"
  assert resolved_records[0].status == "delivered"
  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.solarwindsservicedesk.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer solarwindsservicedesk-token"
  assert create_request[4] == 17
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["summary"] == "Guarded-live market-data incident"
  assert create_payload["alert"]["priority"] == "medium"
  assert create_payload["alert"]["external_reference"] == "guarded-live:market-data:5m"
  assert (
    resolve_request[0]
    == "https://api.solarwindsservicedesk.example/alerts/guarded-live%3Amarket-data%3A5m/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "market-data freshness recovered"


def test_operator_alert_delivery_adapter_syncs_solarwindsservicedesk_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def handler(request, timeout: float):
    body = request.data or b""
    requests.append((request.full_url, request.method, body, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("solarwindsservicedesk",),
    solarwindsservicedesk_api_token="solarwindsservicedesk-token",
    solarwindsservicedesk_api_url="https://api.solarwindsservicedesk.example",
    webhook_timeout_seconds=11,
    urlopen=handler,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-solarwindsservicedesk-2",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 17, 5, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="solarwindsservicedesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SWSD-123",
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="historical_backfill",
      owner="provider",
      provider="solarwindsservicedesk",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        provider="solarwindsservicedesk",
        job_id="solarwindsservicedesk-job-existing",
      ),
      summary="Backfill the degraded historical window.",
      runbook="market_data.backfill_history",
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="solarwindsservicedesk",
    action="acknowledge",
    actor="operator",
    detail="operator_ack",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="solarwindsservicedesk",
    action="escalate",
    actor="operator",
    detail="operator_escalate",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="solarwindsservicedesk",
    action="resolve",
    actor="operator",
    detail="operator_resolve",
    payload={"job_id": "solarwindsservicedesk-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="solarwindsservicedesk",
    action="remediate",
    actor="operator",
    detail="operator_remediate",
    payload={"job_id": "solarwindsservicedesk-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("solarwindsservicedesk",)
  assert acknowledge[0].target == "solarwindsservicedesk_workflow"
  assert acknowledge[0].status == "delivered"
  assert escalate[0].status == "delivered"
  assert resolve[0].status == "delivered"
  assert remediate[0].status == "delivered"
  assert requests[0][0].endswith("/alerts/SWSD-123/acknowledge?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer solarwindsservicedesk-token"
  assert requests[1][0].endswith("/alerts/SWSD-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/SWSD-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/SWSD-123/remediate?identifier_type=id")
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert '"job_id": "solarwindsservicedesk-job-1"' in resolve_payload["note"]
  assert '"job_id": "solarwindsservicedesk-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_solarwindsservicedesk_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str]]] = []

  def handler(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers)))
    if request.full_url == "https://api.solarwindsservicedesk.example/alerts/SWSD-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "alert": {
              "id": "SWSD-123",
              "alert_status": "acknowledged",
              "priority": "high",
              "source": "market-data-primary",
              "owner": {"display_name": "market-data-oncall"},
              "url": "https://solarwindsservicedesk.example/alerts/SWSD-123",
              "updated_at": "2025-01-03T17:08:00+00:00",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "solarwindsservicedesk-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "solarwindsservicedesk-job-9",
                  "channels": ["kline", "depth"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 70,
                  "attempt_count": 1,
                  "current_step": "restore_market_channels",
                  "last_message": "provider body placeholder",
                  "external_run_id": "solarwindsservicedesk-body-9",
                },
                "remediation_provider_telemetry_url": "https://solarwindsservicedesk-engine.example/recovery/solarwindsservicedesk-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://solarwindsservicedesk-engine.example/recovery/solarwindsservicedesk-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "SolarWinds Service Desk engine is verifying restored channels",
              "external_run_id": "solarwindsservicedesk-engine-9",
            }
          }
        ).encode("utf-8"),
      )
    raise AssertionError(f"unexpected request: {request.full_url}")

  adapter = OperatorAlertDeliveryAdapter(
    targets=("solarwindsservicedesk",),
    solarwindsservicedesk_api_token="solarwindsservicedesk-token",
    solarwindsservicedesk_api_url="https://api.solarwindsservicedesk.example",
    solarwindsservicedesk_recovery_engine_url_template=(
      "https://solarwindsservicedesk-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    solarwindsservicedesk_recovery_engine_token="solarwindsservicedesk-recovery-token",
    urlopen=handler,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-solarwindsservicedesk-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 17, 3, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="solarwindsservicedesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SWSD-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="solarwindsservicedesk",
  )

  assert snapshot is not None
  assert snapshot.provider == "solarwindsservicedesk"
  assert snapshot.workflow_reference == "SWSD-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "solarwindsservicedesk-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "solarwindsservicedesk"
  assert snapshot.payload["provider_schema"]["solarwindsservicedesk"]["alert_id"] == "SWSD-123"
  assert snapshot.payload["provider_schema"]["solarwindsservicedesk"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["solarwindsservicedesk"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["solarwindsservicedesk"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["solarwindsservicedesk"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["solarwindsservicedesk"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["external_run_id"] == "solarwindsservicedesk-engine-9"
  assert snapshot.payload["telemetry"]["last_message"] == (
    "SolarWinds Service Desk engine is verifying restored channels"
  )
  assert requests[0][2]["Authorization"] == "Bearer solarwindsservicedesk-token"
  assert requests[1][0] == (
    "https://solarwindsservicedesk-engine.example/recovery/solarwindsservicedesk-job-9"
  )
  assert requests[1][2]["Authorization"] == "Bearer solarwindsservicedesk-recovery-token"


def test_operator_alert_delivery_adapter_supports_topdesk_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def handler(request, timeout: float):
    body = request.data or b""
    requests.append((request.full_url, request.method, body, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("topdesk",),
    topdesk_api_token="topdesk-token",
    topdesk_api_url="https://api.topdesk.example",
    webhook_timeout_seconds=17,
    urlopen=handler,
  )
  opened_records = adapter.deliver(
    incident=OperatorIncidentEvent(
      event_id="incident-opened-topdesk-1",
      alert_id="guarded-live:market-data:5m",
      timestamp=datetime(2025, 1, 3, 17, 0, tzinfo=UTC),
      kind="incident_opened",
      severity="warning",
      summary="Guarded-live market-data incident",
      detail="market-data freshness degraded",
    ),
  )
  resolved_records = adapter.deliver(
    incident=OperatorIncidentEvent(
      event_id="incident-resolved-topdesk-1",
      alert_id="guarded-live:market-data:5m",
      timestamp=datetime(2025, 1, 3, 17, 2, tzinfo=UTC),
      kind="incident_resolved",
      severity="warning",
      summary="Guarded-live market-data incident resolved",
      detail="market-data freshness recovered",
      external_reference="guarded-live:market-data:5m",
    ),
  )

  assert adapter.list_targets() == ("topdesk_incidents",)
  assert opened_records[0].target == "topdesk_incidents"
  assert opened_records[0].external_provider == "topdesk"
  assert opened_records[0].status == "delivered"
  assert resolved_records[0].status == "delivered"
  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.topdesk.example/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer topdesk-token"
  assert create_request[4] == 17
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["summary"] == "Guarded-live market-data incident"
  assert create_payload["alert"]["priority"] == "medium"
  assert create_payload["alert"]["external_reference"] == "guarded-live:market-data:5m"
  assert (
    resolve_request[0]
    == "https://api.topdesk.example/incidents/guarded-live%3Amarket-data%3A5m/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "market-data freshness recovered"


def test_operator_alert_delivery_adapter_syncs_topdesk_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def handler(request, timeout: float):
    body = request.data or b""
    requests.append((request.full_url, request.method, body, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("topdesk",),
    topdesk_api_token="topdesk-token",
    topdesk_api_url="https://api.topdesk.example",
    webhook_timeout_seconds=11,
    urlopen=handler,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-topdesk-2",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 17, 5, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="topdesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="TOP-123",
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="historical_backfill",
      owner="provider",
      provider="topdesk",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        provider="topdesk",
        job_id="topdesk-job-existing",
      ),
      summary="Backfill the degraded historical window.",
      runbook="market_data.backfill_history",
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="topdesk",
    action="acknowledge",
    actor="operator",
    detail="operator_ack",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="topdesk",
    action="escalate",
    actor="operator",
    detail="operator_escalate",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="topdesk",
    action="resolve",
    actor="operator",
    detail="operator_resolve",
    payload={"job_id": "topdesk-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="topdesk",
    action="remediate",
    actor="operator",
    detail="operator_remediate",
    payload={"job_id": "topdesk-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("topdesk",)
  assert acknowledge[0].target == "topdesk_workflow"
  assert acknowledge[0].status == "delivered"
  assert escalate[0].status == "delivered"
  assert resolve[0].status == "delivered"
  assert remediate[0].status == "delivered"
  assert requests[0][0].endswith("/incidents/TOP-123/acknowledge?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer topdesk-token"
  assert requests[1][0].endswith("/incidents/TOP-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/incidents/TOP-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/incidents/TOP-123/remediate?identifier_type=id")
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert '"job_id": "topdesk-job-1"' in resolve_payload["note"]
  assert '"job_id": "topdesk-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_topdesk_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str]]] = []

  def handler(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers)))
    if request.full_url == "https://api.topdesk.example/incidents/TOP-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "incident": {
              "id": "TOP-123",
              "alert_status": "acknowledged",
              "priority": "high",
              "source": "market-data-primary",
              "owner": {"display_name": "market-data-oncall"},
              "url": "https://topdesk.example/incidents/TOP-123",
              "updated_at": "2025-01-03T17:08:00+00:00",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "topdesk-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "topdesk-job-9",
                  "channels": ["kline", "depth"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 70,
                  "attempt_count": 1,
                  "current_step": "restore_market_channels",
                  "last_message": "provider body placeholder",
                  "external_run_id": "topdesk-body-9",
                },
                "remediation_provider_telemetry_url": "https://topdesk-engine.example/recovery/topdesk-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://topdesk-engine.example/recovery/topdesk-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "TOPdesk engine is verifying restored channels",
              "external_run_id": "topdesk-engine-9",
            }
          }
        ).encode("utf-8"),
      )
    raise AssertionError(f"unexpected request: {request.full_url}")

  adapter = OperatorAlertDeliveryAdapter(
    targets=("topdesk",),
    topdesk_api_token="topdesk-token",
    topdesk_api_url="https://api.topdesk.example",
    topdesk_recovery_engine_url_template=(
      "https://topdesk-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    topdesk_recovery_engine_token="topdesk-recovery-token",
    urlopen=handler,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-topdesk-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 17, 3, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="topdesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="TOP-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="topdesk",
  )

  assert snapshot is not None
  assert snapshot.provider == "topdesk"
  assert snapshot.workflow_reference == "TOP-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "topdesk-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "topdesk"
  assert snapshot.payload["provider_schema"]["topdesk"]["alert_id"] == "TOP-123"
  assert snapshot.payload["provider_schema"]["topdesk"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["topdesk"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["topdesk"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["topdesk"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["topdesk"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["external_run_id"] == "topdesk-engine-9"
  assert snapshot.payload["telemetry"]["last_message"] == "TOPdesk engine is verifying restored channels"
  assert requests[0][2]["Authorization"] == "Bearer topdesk-token"
  assert requests[1][0] == "https://topdesk-engine.example/recovery/topdesk-job-9"
  assert requests[1][2]["Authorization"] == "Bearer topdesk-recovery-token"


def test_operator_alert_delivery_adapter_supports_invgateservicedesk_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def handler(request, timeout: float):
    body = request.data or b""
    requests.append((request.full_url, request.method, body, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("invgateservicedesk",),
    invgateservicedesk_api_token="invgateservicedesk-token",
    invgateservicedesk_api_url="https://api.invgateservicedesk.example",
    webhook_timeout_seconds=17,
    urlopen=handler,
  )
  opened_records = adapter.deliver(
    incident=OperatorIncidentEvent(
      event_id="incident-opened-invgateservicedesk-1",
      alert_id="guarded-live:market-data:5m",
      timestamp=datetime(2025, 1, 3, 17, 0, tzinfo=UTC),
      kind="incident_opened",
      severity="warning",
      summary="Guarded-live market-data incident",
      detail="market-data freshness degraded",
    ),
  )
  resolved_records = adapter.deliver(
    incident=OperatorIncidentEvent(
      event_id="incident-resolved-invgateservicedesk-1",
      alert_id="guarded-live:market-data:5m",
      timestamp=datetime(2025, 1, 3, 17, 2, tzinfo=UTC),
      kind="incident_resolved",
      severity="warning",
      summary="Guarded-live market-data incident resolved",
      detail="market-data freshness recovered",
      external_reference="guarded-live:market-data:5m",
    ),
  )

  assert adapter.list_targets() == ("invgateservicedesk_incidents",)
  assert opened_records[0].target == "invgateservicedesk_incidents"
  assert opened_records[0].external_provider == "invgateservicedesk"
  assert opened_records[0].status == "delivered"
  assert resolved_records[0].status == "delivered"
  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.invgateservicedesk.example/incidents"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer invgateservicedesk-token"
  assert create_request[4] == 17
  create_payload = json.loads(create_request[2].decode("utf-8"))
  assert create_payload["alert"]["summary"] == "Guarded-live market-data incident"
  assert create_payload["alert"]["priority"] == "medium"
  assert create_payload["alert"]["external_reference"] == "guarded-live:market-data:5m"
  assert (
    resolve_request[0]
    == "https://api.invgateservicedesk.example/incidents/guarded-live%3Amarket-data%3A5m/resolve?identifier_type=external_reference"
  )
  assert resolve_request[1] == "PUT"
  resolve_payload = json.loads(resolve_request[2].decode("utf-8"))
  assert resolve_payload["note"] == "market-data freshness recovered"


def test_operator_alert_delivery_adapter_syncs_invgateservicedesk_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def handler(request, timeout: float):
    body = request.data or b""
    requests.append((request.full_url, request.method, body, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("invgateservicedesk",),
    invgateservicedesk_api_token="invgateservicedesk-token",
    invgateservicedesk_api_url="https://api.invgateservicedesk.example",
    webhook_timeout_seconds=11,
    urlopen=handler,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-invgateservicedesk-2",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 17, 5, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="invgateservicedesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="IGSD-123",
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="historical_backfill",
      owner="provider",
      provider="invgateservicedesk",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        provider="invgateservicedesk",
        job_id="invgateservicedesk-job-existing",
      ),
      summary="Backfill the degraded historical window.",
      runbook="market_data.backfill_history",
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="invgateservicedesk",
    action="acknowledge",
    actor="operator",
    detail="operator_ack",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="invgateservicedesk",
    action="escalate",
    actor="operator",
    detail="operator_escalate",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="invgateservicedesk",
    action="resolve",
    actor="operator",
    detail="operator_resolve",
    payload={"job_id": "invgateservicedesk-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="invgateservicedesk",
    action="remediate",
    actor="operator",
    detail="operator_remediate",
    payload={"job_id": "invgateservicedesk-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("invgateservicedesk",)
  assert acknowledge[0].target == "invgateservicedesk_workflow"
  assert acknowledge[0].status == "delivered"
  assert escalate[0].status == "delivered"
  assert resolve[0].status == "delivered"
  assert remediate[0].status == "delivered"
  assert requests[0][0].endswith("/incidents/IGSD-123/acknowledge?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer invgateservicedesk-token"
  assert requests[1][0].endswith("/incidents/IGSD-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/incidents/IGSD-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/incidents/IGSD-123/remediate?identifier_type=id")
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert '"job_id": "invgateservicedesk-job-1"' in resolve_payload["note"]
  assert '"job_id": "invgateservicedesk-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_invgateservicedesk_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str]]] = []

  def handler(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers)))
    if request.full_url == "https://api.invgateservicedesk.example/incidents/IGSD-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "incident": {
              "id": "IGSD-123",
              "alert_status": "acknowledged",
              "priority": "high",
              "source": "market-data-primary",
              "owner": {"display_name": "market-data-oncall"},
              "url": "https://invgateservicedesk.example/incidents/IGSD-123",
              "updated_at": "2025-01-03T17:08:00+00:00",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "invgateservicedesk-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "invgateservicedesk-job-9",
                  "channels": ["kline", "depth"],
                  "symbols": ["ETH/USDT"],
                  "timeframe": "5m",
                  "status_machine_state": "provider_running",
                  "status_machine_workflow_state": "acknowledged",
                  "status_machine_job_state": "running",
                },
                "remediation_provider_telemetry": {
                  "source": "provider_payload",
                  "state": "running",
                  "progress_percent": 70,
                  "attempt_count": 1,
                  "current_step": "restore_market_channels",
                  "last_message": "provider body placeholder",
                  "external_run_id": "invgateservicedesk-body-9",
                },
                "remediation_provider_telemetry_url": "https://invgateservicedesk-engine.example/recovery/invgateservicedesk-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://invgateservicedesk-engine.example/recovery/invgateservicedesk-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 95,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "InvGate Service Desk engine is verifying restored channels",
              "external_run_id": "invgateservicedesk-engine-9",
            }
          }
        ).encode("utf-8"),
      )
    raise AssertionError(f"unexpected request: {request.full_url}")

  adapter = OperatorAlertDeliveryAdapter(
    targets=("invgateservicedesk",),
    invgateservicedesk_api_token="invgateservicedesk-token",
    invgateservicedesk_api_url="https://api.invgateservicedesk.example",
    invgateservicedesk_recovery_engine_url_template=(
      "https://invgateservicedesk-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    invgateservicedesk_recovery_engine_token="invgateservicedesk-recovery-token",
    urlopen=handler,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-invgateservicedesk-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 17, 3, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="invgateservicedesk",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="IGSD-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="invgateservicedesk",
  )

  assert snapshot is not None
  assert snapshot.provider == "invgateservicedesk"
  assert snapshot.workflow_reference == "IGSD-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "invgateservicedesk-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "invgateservicedesk"
  assert snapshot.payload["provider_schema"]["invgateservicedesk"]["alert_id"] == "IGSD-123"
  assert snapshot.payload["provider_schema"]["invgateservicedesk"]["alert_status"] == "acknowledged"
  assert (
    snapshot.payload["provider_schema"]["invgateservicedesk"]["phase_graph"]["alert_phase"]
    == "acknowledged"
  )
  assert (
    snapshot.payload["provider_schema"]["invgateservicedesk"]["phase_graph"]["workflow_phase"]
    == "provider_recovering"
  )
  assert (
    snapshot.payload["provider_schema"]["invgateservicedesk"]["phase_graph"]["ownership_phase"]
    == "assigned"
  )
  assert (
    snapshot.payload["provider_schema"]["invgateservicedesk"]["phase_graph"]["escalation_phase"]
    == "configured"
  )
  assert snapshot.payload["telemetry"]["external_run_id"] == "invgateservicedesk-engine-9"
  assert (
    snapshot.payload["telemetry"]["last_message"]
    == "InvGate Service Desk engine is verifying restored channels"
  )
  assert requests[0][2]["Authorization"] == "Bearer invgateservicedesk-token"
  assert (
    requests[1][0]
    == "https://invgateservicedesk-engine.example/recovery/invgateservicedesk-job-9"
  )
  assert requests[1][2]["Authorization"] == "Bearer invgateservicedesk-recovery-token"


def test_operator_alert_delivery_adapter_supports_opsramp_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("opsramp",),
    opsramp_api_token="opsramp-token",
    opsramp_api_url="https://api.opsramp.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-opsramp-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 9, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-opsramp-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 10, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("opsramp_incidents",)
  assert opened_records[0].target == "opsramp_incidents"
  assert opened_records[0].external_provider == "opsramp"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.opsramp.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer opsramp-token"
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


def test_operator_alert_delivery_adapter_syncs_opsramp_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("opsramp",),
    opsramp_api_token="opsramp-token",
    opsramp_api_url="https://api.opsramp.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-opsramp-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 11, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="opsramp",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="OR-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="opsramp",
        job_id="opsramp-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsramp",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsramp",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsramp",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "opsramp-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="opsramp",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "opsramp-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("opsramp",)
  assert acknowledge[0].target == "opsramp_workflow"
  assert acknowledge[0].external_reference == "OR-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/OR-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/OR-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/OR-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/OR-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer opsramp-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "opsramp-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "opsramp-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_opsramp_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.opsramp.example/alerts/OR-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "OR-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:12:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://opsramp.example/alerts/OR-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "opsramp-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "opsramp-job-9",
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
                  "progress_percent": 64,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "opsramp-body-9",
                },
                "remediation_provider_telemetry_url": "https://opsramp-engine.example/recovery/opsramp-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://opsramp-engine.example/recovery/opsramp-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 92,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "OpsRamp engine is verifying restored channels",
              "external_run_id": "opsramp-engine-9",
              "updated_at": "2025-01-03T16:13:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("opsramp",),
    opsramp_api_token="opsramp-token",
    opsramp_api_url="https://api.opsramp.example",
    opsramp_recovery_engine_url_template=(
      "https://opsramp-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    opsramp_recovery_engine_token="opsramp-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-opsramp-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 11, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="opsramp",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="OR-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="opsramp",
  )

  assert snapshot is not None
  assert snapshot.provider == "opsramp"
  assert snapshot.workflow_reference == "OR-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "opsramp-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "opsramp"
  assert snapshot.payload["provider_schema"]["opsramp"]["alert_id"] == "OR-123"
  assert snapshot.payload["provider_schema"]["opsramp"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["opsramp"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["opsramp"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["opsramp"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["opsramp"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 92
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "OpsRamp engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "opsramp-engine-9"
  assert requests[0][0].endswith("/alerts/OR-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer opsramp-token"
  assert requests[1][0] == "https://opsramp-engine.example/recovery/opsramp-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer opsramp-recovery-token"


