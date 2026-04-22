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
    payload={
      "job_id": "bl-job-1",
      "verification": {"state": "passed"},
      "market_context": {
        "symbol": "ETH/USDT",
        "symbols": ["ETH/USDT"],
        "timeframe": "5m",
      },
    },
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="blameless",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={
      "job_id": "bl-job-2",
      "channels": ["kline", "depth"],
      "market_context": {
        "symbol": "ETH/USDT",
        "symbols": ["ETH/USDT"],
        "timeframe": "5m",
      },
    },
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
  assert resolve_payload["metadata"]["market_context"]["symbol"] == "ETH/USDT"
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert remediate_payload["metadata"]["market_context"]["timeframe"] == "5m"
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


