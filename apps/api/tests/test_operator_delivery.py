from __future__ import annotations

import json
from datetime import UTC
from datetime import datetime

from akra_trader.adapters.operator_delivery import OperatorAlertDeliveryAdapter
from akra_trader.domain.models import OperatorIncidentEvent


class FakeResponse:
  def __init__(self, status: int) -> None:
    self.status = status

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc, tb) -> None:
    return None


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
