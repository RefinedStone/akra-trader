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


def test_operator_alert_delivery_adapter_supports_spikesh_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("spikesh",),
    spikesh_api_token="spikesh-token",
    spikesh_api_url="https://api.spikesh.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-spikesh-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 59, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-spikesh-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("spikesh_incidents",)
  assert opened_records[0].target == "spikesh_incidents"
  assert opened_records[0].external_provider == "spikesh"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.spikesh.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer spikesh-token"
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


def test_operator_alert_delivery_adapter_syncs_spikesh_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("spikesh",),
    spikesh_api_token="spikesh-token",
    spikesh_api_url="https://api.spikesh.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-spikesh-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 1, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="spikesh",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="SPK-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="spikesh",
        job_id="spikesh-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="spikesh",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="spikesh",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="spikesh",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "spikesh-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="spikesh",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "spikesh-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("spikesh",)
  assert acknowledge[0].target == "spikesh_workflow"
  assert acknowledge[0].external_reference == "SPK-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/SPK-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/SPK-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/SPK-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/SPK-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer spikesh-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "spikesh-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "spikesh-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_spikesh_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.spikesh.example/alerts/SPK-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "SPK-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:02:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://spike.example/alerts/SPK-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "spikesh-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "spikesh-job-9",
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
                  "external_run_id": "spikesh-body-9",
                },
                "remediation_provider_telemetry_url": "https://spikesh-engine.example/recovery/spikesh-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://spikesh-engine.example/recovery/spikesh-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 93,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Spike.sh engine is verifying restored channels",
              "external_run_id": "spikesh-engine-9",
              "updated_at": "2025-01-03T16:03:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("spikesh",),
    spikesh_api_token="spikesh-token",
    spikesh_api_url="https://api.spikesh.example",
    spikesh_recovery_engine_url_template=(
      "https://spikesh-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    spikesh_recovery_engine_token="spikesh-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-spikesh-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 1, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="spikesh",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="SPK-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="spikesh",
  )

  assert snapshot is not None
  assert snapshot.provider == "spikesh"
  assert snapshot.workflow_reference == "SPK-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "spikesh-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "spikesh"
  assert snapshot.payload["provider_schema"]["spikesh"]["alert_id"] == "SPK-123"
  assert snapshot.payload["provider_schema"]["spikesh"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["spikesh"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["spikesh"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["spikesh"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["spikesh"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 93
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Spike.sh engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "spikesh-engine-9"
  assert requests[0][0].endswith("/alerts/SPK-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer spikesh-token"
  assert requests[1][0] == "https://spikesh-engine.example/recovery/spikesh-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer spikesh-recovery-token"


def test_operator_alert_delivery_adapter_supports_dutycalls_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("dutycalls",),
    dutycalls_api_token="dutycalls-token",
    dutycalls_api_url="https://api.dutycalls.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-dutycalls-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 59, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-dutycalls-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("dutycalls_incidents",)
  assert opened_records[0].target == "dutycalls_incidents"
  assert opened_records[0].external_provider == "dutycalls"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.dutycalls.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer dutycalls-token"
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


def test_operator_alert_delivery_adapter_syncs_dutycalls_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("dutycalls",),
    dutycalls_api_token="dutycalls-token",
    dutycalls_api_url="https://api.dutycalls.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-dutycalls-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 1, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="dutycalls",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="DC-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="dutycalls",
        job_id="dutycalls-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="dutycalls",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="dutycalls",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="dutycalls",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "dutycalls-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="dutycalls",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "dutycalls-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("dutycalls",)
  assert acknowledge[0].target == "dutycalls_workflow"
  assert acknowledge[0].external_reference == "DC-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/DC-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/DC-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/DC-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/DC-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer dutycalls-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "dutycalls-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "dutycalls-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_dutycalls_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.dutycalls.example/alerts/DC-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "DC-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:02:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://dutycalls.example/alerts/DC-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "dutycalls-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "dutycalls-job-9",
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
                  "external_run_id": "dutycalls-body-9",
                },
                "remediation_provider_telemetry_url": "https://dutycalls-engine.example/recovery/dutycalls-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://dutycalls-engine.example/recovery/dutycalls-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 91,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "DutyCalls engine is verifying restored channels",
              "external_run_id": "dutycalls-engine-9",
              "updated_at": "2025-01-03T16:03:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("dutycalls",),
    dutycalls_api_token="dutycalls-token",
    dutycalls_api_url="https://api.dutycalls.example",
    dutycalls_recovery_engine_url_template=(
      "https://dutycalls-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    dutycalls_recovery_engine_token="dutycalls-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-dutycalls-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 1, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="dutycalls",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="DC-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="dutycalls",
  )

  assert snapshot is not None
  assert snapshot.provider == "dutycalls"
  assert snapshot.workflow_reference == "DC-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "dutycalls-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "dutycalls"
  assert snapshot.payload["provider_schema"]["dutycalls"]["alert_id"] == "DC-123"
  assert snapshot.payload["provider_schema"]["dutycalls"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["dutycalls"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["dutycalls"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["dutycalls"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["dutycalls"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 91
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "DutyCalls engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "dutycalls-engine-9"
  assert requests[0][0].endswith("/alerts/DC-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer dutycalls-token"
  assert requests[1][0] == "https://dutycalls-engine.example/recovery/dutycalls-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer dutycalls-recovery-token"


def test_operator_alert_delivery_adapter_supports_incidenthub_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidenthub",),
    incidenthub_api_token="incidenthub-token",
    incidenthub_api_url="https://api.incidenthub.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-incidenthub-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 15, 59, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-incidenthub-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("incidenthub_incidents",)
  assert opened_records[0].target == "incidenthub_incidents"
  assert opened_records[0].external_provider == "incidenthub"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.incidenthub.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer incidenthub-token"
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


def test_operator_alert_delivery_adapter_syncs_incidenthub_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidenthub",),
    incidenthub_api_token="incidenthub-token",
    incidenthub_api_url="https://api.incidenthub.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-incidenthub-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 1, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="incidenthub",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="IH-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="incidenthub",
        job_id="incidenthub-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidenthub",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidenthub",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidenthub",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "incidenthub-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidenthub",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "incidenthub-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("incidenthub",)
  assert acknowledge[0].target == "incidenthub_workflow"
  assert acknowledge[0].external_reference == "IH-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/IH-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/IH-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/IH-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/IH-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer incidenthub-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "incidenthub-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "incidenthub-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_incidenthub_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.incidenthub.example/alerts/IH-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "IH-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:02:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://incidenthub.example/alerts/IH-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "incidenthub-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "incidenthub-job-9",
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
                  "external_run_id": "incidenthub-body-9",
                },
                "remediation_provider_telemetry_url": "https://incidenthub-engine.example/recovery/incidenthub-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://incidenthub-engine.example/recovery/incidenthub-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 92,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "IncidentHub engine is verifying restored channels",
              "external_run_id": "incidenthub-engine-9",
              "updated_at": "2025-01-03T16:03:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidenthub",),
    incidenthub_api_token="incidenthub-token",
    incidenthub_api_url="https://api.incidenthub.example",
    incidenthub_recovery_engine_url_template=(
      "https://incidenthub-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    incidenthub_recovery_engine_token="incidenthub-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-incidenthub-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 1, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="incidenthub",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="IH-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="incidenthub",
  )

  assert snapshot is not None
  assert snapshot.provider == "incidenthub"
  assert snapshot.workflow_reference == "IH-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "incidenthub-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "incidenthub"
  assert snapshot.payload["provider_schema"]["incidenthub"]["alert_id"] == "IH-123"
  assert snapshot.payload["provider_schema"]["incidenthub"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["incidenthub"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["incidenthub"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["incidenthub"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["incidenthub"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 92
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "IncidentHub engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "incidenthub-engine-9"
  assert requests[0][0].endswith("/alerts/IH-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer incidenthub-token"
  assert requests[1][0] == "https://incidenthub-engine.example/recovery/incidenthub-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer incidenthub-recovery-token"


def test_operator_alert_delivery_adapter_supports_resolver_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("resolver",),
    resolver_api_token="resolver-token",
    resolver_api_url="https://api.resolver.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-resolver-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 5, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-resolver-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 6, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("resolver_incidents",)
  assert opened_records[0].target == "resolver_incidents"
  assert opened_records[0].external_provider == "resolver"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.resolver.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer resolver-token"
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


def test_operator_alert_delivery_adapter_syncs_resolver_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("resolver",),
    resolver_api_token="resolver-token",
    resolver_api_url="https://api.resolver.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-resolver-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 7, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="resolver",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="RV-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="resolver",
        job_id="resolver-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="resolver",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="resolver",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="resolver",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "resolver-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="resolver",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "resolver-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("resolver",)
  assert acknowledge[0].target == "resolver_workflow"
  assert acknowledge[0].external_reference == "RV-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/RV-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/RV-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/RV-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/RV-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer resolver-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "resolver-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "resolver-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_resolver_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.resolver.example/alerts/RV-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "RV-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:08:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://resolver.example/alerts/RV-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "resolver-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "resolver-job-9",
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
                  "external_run_id": "resolver-body-9",
                },
                "remediation_provider_telemetry_url": "https://resolver-engine.example/recovery/resolver-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://resolver-engine.example/recovery/resolver-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 92,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Resolver engine is verifying restored channels",
              "external_run_id": "resolver-engine-9",
              "updated_at": "2025-01-03T16:09:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("resolver",),
    resolver_api_token="resolver-token",
    resolver_api_url="https://api.resolver.example",
    resolver_recovery_engine_url_template=(
      "https://resolver-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    resolver_recovery_engine_token="resolver-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-resolver-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 7, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="resolver",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="RV-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="resolver",
  )

  assert snapshot is not None
  assert snapshot.provider == "resolver"
  assert snapshot.workflow_reference == "RV-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "resolver-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "resolver"
  assert snapshot.payload["provider_schema"]["resolver"]["alert_id"] == "RV-123"
  assert snapshot.payload["provider_schema"]["resolver"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["resolver"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["resolver"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["resolver"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["resolver"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 92
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Resolver engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "resolver-engine-9"
  assert requests[0][0].endswith("/alerts/RV-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer resolver-token"
  assert requests[1][0] == "https://resolver-engine.example/recovery/resolver-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer resolver-recovery-token"


def test_operator_alert_delivery_adapter_supports_openduty_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("openduty",),
    openduty_api_token="openduty-token",
    openduty_api_url="https://api.openduty.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-openduty-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 7, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-openduty-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 8, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("openduty_incidents",)
  assert opened_records[0].target == "openduty_incidents"
  assert opened_records[0].external_provider == "openduty"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.openduty.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer openduty-token"
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


def test_operator_alert_delivery_adapter_syncs_openduty_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("openduty",),
    openduty_api_token="openduty-token",
    openduty_api_url="https://api.openduty.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-openduty-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 9, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="openduty",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="OD-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="openduty",
        job_id="openduty-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="openduty",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="openduty",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="openduty",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "openduty-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="openduty",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "openduty-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("openduty",)
  assert acknowledge[0].target == "openduty_workflow"
  assert acknowledge[0].external_reference == "OD-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/OD-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/OD-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/OD-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/OD-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer openduty-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "openduty-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "openduty-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_openduty_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.openduty.example/alerts/OD-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "OD-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:10:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://openduty.example/alerts/OD-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "openduty-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "openduty-job-9",
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
                  "external_run_id": "openduty-body-9",
                },
                "remediation_provider_telemetry_url": "https://openduty-engine.example/recovery/openduty-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://openduty-engine.example/recovery/openduty-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 92,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "OpenDuty engine is verifying restored channels",
              "external_run_id": "openduty-engine-9",
              "updated_at": "2025-01-03T16:11:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("openduty",),
    openduty_api_token="openduty-token",
    openduty_api_url="https://api.openduty.example",
    openduty_recovery_engine_url_template=(
      "https://openduty-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    openduty_recovery_engine_token="openduty-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-openduty-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 9, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="openduty",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="OD-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="openduty",
  )

  assert snapshot is not None
  assert snapshot.provider == "openduty"
  assert snapshot.workflow_reference == "OD-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "openduty-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "openduty"
  assert snapshot.payload["provider_schema"]["openduty"]["alert_id"] == "OD-123"
  assert snapshot.payload["provider_schema"]["openduty"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["openduty"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["openduty"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["openduty"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["openduty"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 92
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "OpenDuty engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "openduty-engine-9"
  assert requests[0][0].endswith("/alerts/OD-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer openduty-token"
  assert requests[1][0] == "https://openduty-engine.example/recovery/openduty-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer openduty-recovery-token"


def test_operator_alert_delivery_adapter_supports_cabot_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("cabot",),
    cabot_api_token="cabot-token",
    cabot_api_url="https://api.cabot.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-cabot-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 17, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-cabot-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 18, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("cabot_incidents",)
  assert opened_records[0].target == "cabot_incidents"
  assert opened_records[0].external_provider == "cabot"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.cabot.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer cabot-token"
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


def test_operator_alert_delivery_adapter_syncs_cabot_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("cabot",),
    cabot_api_token="cabot-token",
    cabot_api_url="https://api.cabot.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-cabot-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 19, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="cabot",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="CB-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="cabot",
        job_id="cabot-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="cabot",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="cabot",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="cabot",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "cabot-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="cabot",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "cabot-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("cabot",)
  assert acknowledge[0].target == "cabot_workflow"
  assert acknowledge[0].external_reference == "CB-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/CB-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/CB-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/CB-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/CB-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer cabot-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "cabot-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "cabot-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_cabot_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.cabot.example/alerts/CB-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "CB-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:20:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://cabot.example/alerts/CB-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "cabot-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "cabot-job-9",
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
                  "progress_percent": 65,
                  "attempt_count": 1,
                  "current_step": "incident_body",
                  "last_message": "alert body telemetry is lagging",
                  "external_run_id": "cabot-body-9",
                },
                "remediation_provider_telemetry_url": "https://cabot-engine.example/recovery/cabot-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://cabot-engine.example/recovery/cabot-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 93,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "Cabot engine is verifying restored channels",
              "external_run_id": "cabot-engine-9",
              "updated_at": "2025-01-03T16:21:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("cabot",),
    cabot_api_token="cabot-token",
    cabot_api_url="https://api.cabot.example",
    cabot_recovery_engine_url_template=(
      "https://cabot-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    cabot_recovery_engine_token="cabot-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-cabot-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 19, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="cabot",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="CB-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="cabot",
  )

  assert snapshot is not None
  assert snapshot.provider == "cabot"
  assert snapshot.workflow_reference == "CB-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "cabot-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "cabot"
  assert snapshot.payload["provider_schema"]["cabot"]["alert_id"] == "CB-123"
  assert snapshot.payload["provider_schema"]["cabot"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["cabot"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["cabot"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["cabot"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["cabot"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 93
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "Cabot engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "cabot-engine-9"
  assert requests[0][0].endswith("/alerts/CB-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer cabot-token"
  assert requests[1][0] == "https://cabot-engine.example/recovery/cabot-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer cabot-recovery-token"


def test_operator_alert_delivery_adapter_supports_haloitsm_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("haloitsm",),
    haloitsm_api_token="haloitsm-token",
    haloitsm_api_url="https://api.haloitsm.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-haloitsm-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 27, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-haloitsm-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 28, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("haloitsm_incidents",)
  assert opened_records[0].target == "haloitsm_incidents"
  assert opened_records[0].external_provider == "haloitsm"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.haloitsm.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer haloitsm-token"
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


def test_operator_alert_delivery_adapter_syncs_haloitsm_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("haloitsm",),
    haloitsm_api_token="haloitsm-token",
    haloitsm_api_url="https://api.haloitsm.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-haloitsm-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 29, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="haloitsm",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="HI-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="haloitsm",
        job_id="haloitsm-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="haloitsm",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="haloitsm",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="haloitsm",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "haloitsm-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="haloitsm",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "haloitsm-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("haloitsm",)
  assert acknowledge[0].target == "haloitsm_workflow"
  assert acknowledge[0].external_reference == "HI-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/HI-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/HI-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/HI-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/HI-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer haloitsm-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "haloitsm-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "haloitsm-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_haloitsm_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.haloitsm.example/alerts/HI-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "HI-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:30:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://haloitsm.example/alerts/HI-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "haloitsm-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "haloitsm-job-9",
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
                  "external_run_id": "haloitsm-body-9",
                },
                "remediation_provider_telemetry_url": "https://haloitsm-engine.example/recovery/haloitsm-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://haloitsm-engine.example/recovery/haloitsm-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "HaloITSM engine is verifying restored channels",
              "external_run_id": "haloitsm-engine-9",
              "updated_at": "2025-01-03T16:31:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("haloitsm",),
    haloitsm_api_token="haloitsm-token",
    haloitsm_api_url="https://api.haloitsm.example",
    haloitsm_recovery_engine_url_template=(
      "https://haloitsm-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    haloitsm_recovery_engine_token="haloitsm-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-haloitsm-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 29, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="haloitsm",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="HI-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="haloitsm",
  )

  assert snapshot is not None
  assert snapshot.provider == "haloitsm"
  assert snapshot.workflow_reference == "HI-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "haloitsm-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "haloitsm"
  assert snapshot.payload["provider_schema"]["haloitsm"]["alert_id"] == "HI-123"
  assert snapshot.payload["provider_schema"]["haloitsm"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["haloitsm"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["haloitsm"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["haloitsm"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["haloitsm"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "HaloITSM engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "haloitsm-engine-9"
  assert requests[0][0].endswith("/alerts/HI-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer haloitsm-token"
  assert requests[1][0] == "https://haloitsm-engine.example/recovery/haloitsm-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer haloitsm-recovery-token"


def test_operator_alert_delivery_adapter_supports_incidentmanagerio_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidentmanagerio",),
    incidentmanagerio_api_token="incidentmanagerio-token",
    incidentmanagerio_api_url="https://api.incidentmanagerio.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-incidentmanagerio-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 33, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-incidentmanagerio-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 34, tzinfo=UTC),
    kind="incident_resolved",
    severity="warning",
    summary="Resolved: Guarded-live worker failed for ETH/USDT.",
    detail="live worker recovered",
    external_reference="guarded-live:worker-failed:run-1",
  )

  opened_records = adapter.deliver(incident=opened)
  resolved_records = adapter.deliver(incident=resolved)

  assert adapter.list_targets() == ("incidentmanagerio_incidents",)
  assert opened_records[0].target == "incidentmanagerio_incidents"
  assert opened_records[0].external_provider == "incidentmanagerio"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.incidentmanagerio.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer incidentmanagerio-token"
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


def test_operator_alert_delivery_adapter_syncs_incidentmanagerio_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidentmanagerio",),
    incidentmanagerio_api_token="incidentmanagerio-token",
    incidentmanagerio_api_url="https://api.incidentmanagerio.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-incidentmanagerio-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 35, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="incidentmanagerio",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="IM-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="incidentmanagerio",
        job_id="incidentmanagerio-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentmanagerio",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentmanagerio",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentmanagerio",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "incidentmanagerio-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="incidentmanagerio",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "incidentmanagerio-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("incidentmanagerio",)
  assert acknowledge[0].target == "incidentmanagerio_workflow"
  assert acknowledge[0].external_reference == "IM-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/IM-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/IM-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/IM-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/IM-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer incidentmanagerio-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "incidentmanagerio-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "incidentmanagerio-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_incidentmanagerio_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.incidentmanagerio.example/alerts/IM-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "IM-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:36:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://incidentmanagerio.example/alerts/IM-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "incidentmanagerio-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "incidentmanagerio-job-9",
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
                  "external_run_id": "incidentmanagerio-body-9",
                },
                "remediation_provider_telemetry_url": "https://incidentmanagerio-engine.example/recovery/incidentmanagerio-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://incidentmanagerio-engine.example/recovery/incidentmanagerio-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "incidentmanager.io engine is verifying restored channels",
              "external_run_id": "incidentmanagerio-engine-9",
              "updated_at": "2025-01-03T16:37:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("incidentmanagerio",),
    incidentmanagerio_api_token="incidentmanagerio-token",
    incidentmanagerio_api_url="https://api.incidentmanagerio.example",
    incidentmanagerio_recovery_engine_url_template=(
      "https://incidentmanagerio-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    incidentmanagerio_recovery_engine_token="incidentmanagerio-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-incidentmanagerio-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 35, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="incidentmanagerio",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="IM-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="incidentmanagerio",
  )

  assert snapshot is not None
  assert snapshot.provider == "incidentmanagerio"
  assert snapshot.workflow_reference == "IM-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "incidentmanagerio-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "incidentmanagerio"
  assert snapshot.payload["provider_schema"]["incidentmanagerio"]["alert_id"] == "IM-123"
  assert snapshot.payload["provider_schema"]["incidentmanagerio"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["incidentmanagerio"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["incidentmanagerio"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["incidentmanagerio"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["incidentmanagerio"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "incidentmanager.io engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "incidentmanagerio-engine-9"
  assert requests[0][0].endswith("/alerts/IM-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer incidentmanagerio-token"
  assert requests[1][0] == "https://incidentmanagerio-engine.example/recovery/incidentmanagerio-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer incidentmanagerio-recovery-token"


def test_operator_alert_delivery_adapter_supports_oneuptime_target_and_resolution() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("oneuptime",),
    oneuptime_api_token="oneuptime-token",
    oneuptime_api_url="https://api.oneuptime.example",
    webhook_timeout_seconds=6,
    urlopen=fake_urlopen,
  )
  opened = OperatorIncidentEvent(
    event_id="incident-opened-oneuptime-1",
    alert_id="guarded-live:worker-failed:run-1",
    timestamp=datetime(2025, 1, 3, 16, 39, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live worker failed for ETH/USDT.",
    detail="live worker crash",
  )
  resolved = OperatorIncidentEvent(
    event_id="incident-resolved-oneuptime-1",
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

  assert adapter.list_targets() == ("oneuptime_incidents",)
  assert opened_records[0].target == "oneuptime_incidents"
  assert opened_records[0].external_provider == "oneuptime"
  assert resolved_records[0].external_reference == "guarded-live:worker-failed:run-1"

  create_request = requests[0]
  resolve_request = requests[1]
  assert create_request[0] == "https://api.oneuptime.example/alerts"
  assert create_request[1] == "POST"
  assert create_request[3]["Authorization"] == "Bearer oneuptime-token"
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


def test_operator_alert_delivery_adapter_syncs_oneuptime_workflow_actions() -> None:
  requests: list[tuple[str, str, bytes, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, request.data, dict(request.headers), timeout))
    return FakeResponse(202)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("oneuptime",),
    oneuptime_api_token="oneuptime-token",
    oneuptime_api_url="https://api.oneuptime.example",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-oneuptime-2",
    alert_id="guarded-live:reconciliation",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="critical",
    summary="Guarded-live reconciliation has unresolved findings.",
    detail="reconciliation drift",
    external_provider="oneuptime",
    external_reference="guarded-live:reconciliation",
    provider_workflow_reference="OU-123",
    escalation_level=2,
    remediation=OperatorIncidentRemediation(
      state="requested",
      kind="recent_sync",
      summary="Refresh the live timeframe sync window and verify freshness thresholds.",
      runbook="market_data.sync_recent",
      provider_recovery=OperatorIncidentProviderRecoveryState(
        lifecycle_state="recovering",
        provider="oneuptime",
        job_id="oneuptime-job-existing",
        channels=("kline",),
        symbols=("ETH/USDT",),
        timeframe="5m",
        verification=OperatorIncidentProviderRecoveryVerification(state="pending"),
      ),
    ),
  )

  acknowledge = adapter.sync_incident_workflow(
    incident=incident,
    provider="oneuptime",
    action="acknowledge",
    actor="operator",
    detail="triaged",
  )
  escalate = adapter.sync_incident_workflow(
    incident=incident,
    provider="oneuptime",
    action="escalate",
    actor="operator",
    detail="handoff",
  )
  resolve = adapter.sync_incident_workflow(
    incident=incident,
    provider="oneuptime",
    action="resolve",
    actor="operator",
    detail="fixed",
    payload={"job_id": "oneuptime-job-1", "verification": {"state": "passed"}},
  )
  remediate = adapter.sync_incident_workflow(
    incident=incident,
    provider="oneuptime",
    action="remediate",
    actor="operator",
    detail="restart_sync_and_verify_checkpoint",
    payload={"job_id": "oneuptime-job-2", "channels": ["kline", "depth"]},
  )

  assert adapter.list_supported_workflow_providers() == ("oneuptime",)
  assert acknowledge[0].target == "oneuptime_workflow"
  assert acknowledge[0].external_reference == "OU-123"
  assert escalate[0].provider_action == "escalate"
  assert resolve[0].provider_action == "resolve"
  assert remediate[0].provider_action == "remediate"

  assert requests[0][0].endswith("/alerts/OU-123/acknowledge?identifier_type=id")
  assert requests[1][0].endswith("/alerts/OU-123/escalate?identifier_type=id")
  assert requests[2][0].endswith("/alerts/OU-123/resolve?identifier_type=id")
  assert requests[3][0].endswith("/alerts/OU-123/remediate?identifier_type=id")
  assert requests[0][1] == "PUT"
  assert requests[0][3]["Authorization"] == "Bearer oneuptime-token"
  escalate_payload = json.loads(requests[1][2].decode("utf-8"))
  resolve_payload = json.loads(requests[2][2].decode("utf-8"))
  remediate_payload = json.loads(requests[3][2].decode("utf-8"))
  assert "level 2" in escalate_payload["note"]
  assert '"job_id": "oneuptime-job-1"' in resolve_payload["note"]
  assert "requested remediation" in remediate_payload["note"]
  assert "market_data.sync_recent" in remediate_payload["note"]
  assert '"job_id": "oneuptime-job-2"' in remediate_payload["note"]


def test_operator_alert_delivery_adapter_pulls_oneuptime_provider_state() -> None:
  requests: list[tuple[str, str, dict[str, str], float]] = []

  def fake_urlopen(request, timeout: float):
    requests.append((request.full_url, request.method, dict(request.headers), timeout))
    if request.full_url == "https://api.oneuptime.example/alerts/OU-123?identifier_type=id":
      return FakeResponse(
        200,
        json.dumps(
          {
            "result": {
              "alert_id": "OU-123",
              "external_reference": "guarded-live:market-data:5m",
              "alert_status": "acknowledged",
              "summary": "Guarded-live market-data incident",
              "updated_at": "2025-01-03T16:42:00Z",
              "priority": "high",
              "escalation_policy": "market-data-primary",
              "assignee": "market-data-oncall",
              "url": "https://oneuptime.example/alerts/OU-123",
              "metadata": {
                "remediation_state": "recovering",
                "remediation_provider_payload": {
                  "job_id": "oneuptime-job-9",
                  "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
                  "verification": {"state": "pending"},
                },
                "remediation_provider_recovery": {
                  "lifecycle_state": "recovering",
                  "job_id": "oneuptime-job-9",
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
                  "external_run_id": "oneuptime-body-9",
                },
                "remediation_provider_telemetry_url": "https://oneuptime-engine.example/recovery/oneuptime-job-9",
              },
            }
          }
        ).encode("utf-8"),
      )
    if request.full_url == "https://oneuptime-engine.example/recovery/oneuptime-job-9":
      return FakeResponse(
        200,
        json.dumps(
          {
            "job": {
              "state": "running",
              "progress_percent": 94,
              "attempt_count": 2,
              "current_step": "verify_restored_channels",
              "last_message": "OneUptime engine is verifying restored channels",
              "external_run_id": "oneuptime-engine-9",
              "updated_at": "2025-01-03T16:43:00Z",
            }
          }
        ).encode("utf-8"),
      )
    return FakeResponse(404)

  adapter = OperatorAlertDeliveryAdapter(
    targets=("oneuptime",),
    oneuptime_api_token="oneuptime-token",
    oneuptime_api_url="https://api.oneuptime.example",
    oneuptime_recovery_engine_url_template=(
      "https://oneuptime-engine.example/recovery/{workflow_reference_urlencoded}"
    ),
    oneuptime_recovery_engine_token="oneuptime-recovery-token",
    urlopen=fake_urlopen,
  )
  incident = OperatorIncidentEvent(
    event_id="incident-opened-oneuptime-pull-1",
    alert_id="guarded-live:market-data:5m",
    timestamp=datetime(2025, 1, 3, 16, 41, tzinfo=UTC),
    kind="incident_opened",
    severity="warning",
    summary="Guarded-live market-data incident",
    detail="market-data freshness degraded",
    external_provider="oneuptime",
    external_reference="guarded-live:market-data:5m",
    provider_workflow_reference="OU-123",
  )

  snapshot = adapter.pull_incident_workflow_state(
    incident=incident,
    provider="oneuptime",
  )

  assert snapshot is not None
  assert snapshot.provider == "oneuptime"
  assert snapshot.workflow_reference == "OU-123"
  assert snapshot.external_reference == "guarded-live:market-data:5m"
  assert snapshot.workflow_state == "acknowledged"
  assert snapshot.remediation_state == "recovering"
  assert snapshot.payload["job_id"] == "oneuptime-job-9"
  assert snapshot.payload["targets"]["symbols"] == ["ETH/USDT"]
  assert snapshot.payload["status_machine"]["sync_state"] == "provider_authoritative"
  assert snapshot.payload["provider_schema"]["kind"] == "oneuptime"
  assert snapshot.payload["provider_schema"]["oneuptime"]["alert_id"] == "OU-123"
  assert snapshot.payload["provider_schema"]["oneuptime"]["alert_status"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["oneuptime"]["phase_graph"]["alert_phase"] == "acknowledged"
  assert snapshot.payload["provider_schema"]["oneuptime"]["phase_graph"]["workflow_phase"] == "provider_recovering"
  assert snapshot.payload["provider_schema"]["oneuptime"]["phase_graph"]["ownership_phase"] == "assigned"
  assert snapshot.payload["provider_schema"]["oneuptime"]["phase_graph"]["escalation_phase"] == "configured"
  assert snapshot.payload["telemetry"]["source"] == "provider_engine"
  assert snapshot.payload["telemetry"]["state"] == "running"
  assert snapshot.payload["telemetry"]["progress_percent"] == 94
  assert snapshot.payload["telemetry"]["attempt_count"] == 2
  assert snapshot.payload["telemetry"]["current_step"] == "verify_restored_channels"
  assert snapshot.payload["telemetry"]["last_message"] == "OneUptime engine is verifying restored channels"
  assert snapshot.payload["telemetry"]["external_run_id"] == "oneuptime-engine-9"
  assert requests[0][0].endswith("/alerts/OU-123?identifier_type=id")
  assert requests[0][1] == "GET"
  assert requests[0][2]["Authorization"] == "Bearer oneuptime-token"
  assert requests[1][0] == "https://oneuptime-engine.example/recovery/oneuptime-job-9"
  assert requests[1][1] == "GET"
  assert requests[1][2]["Authorization"] == "Bearer oneuptime-recovery-token"


