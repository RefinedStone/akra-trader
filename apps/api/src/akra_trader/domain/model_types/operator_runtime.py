from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class OperatorAlertPrimaryFocus:
  kind: str = "runtime"
  run_id: str | None = None
  symbol: str | None = None
  timeframe: str | None = None


@dataclass(frozen=True)
class OperatorAlert:
  alert_id: str
  timestamp: datetime
  severity: str
  kind: str
  summary: str
  detail: str = ""
  run_id: str | None = None
  symbol: str | None = None
  source: str = "runtime"
  primary_focus: OperatorAlertPrimaryFocus | None = None
  payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OperatorAuditEvent:
  event_id: str
  recorded_at: datetime
  kind: str
  summary: str
  actor: str = "system"
  run_id: str | None = None
  source: str = "runtime"
  payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OperatorIncidentEvent:
  event_id: str
  alert_id: str
  timestamp: datetime
  kind: str
  severity: str
  summary: str
  detail: str = ""
  run_id: str | None = None
  session_id: str | None = None
  symbol: str | None = None
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  primary_focus: OperatorAlertPrimaryFocus | None = None
  source: str = "runtime"
  delivery_state: str = "internal_only"
  acknowledgment_state: str = "not_applicable"
  acknowledged_at: datetime | None = None
  acknowledged_by: str | None = None
  payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OperatorIncidentDelivery:
  delivery_id: str
  incident_event_id: str
  alert_id: str
  incident_kind: str
  target: str
  status: str
  attempted_at: datetime
  detail: str = ""
  attempt_number: int = 1
  next_retry_at: datetime | None = None
  phase: str = "internal"
  source: str = "runtime"


@dataclass(frozen=True)
class OperatorVisibility:
  generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  alerts: tuple[OperatorAlert, ...] = ()
  alert_history: tuple[OperatorAlert, ...] = ()
  incident_events: tuple[OperatorIncidentEvent, ...] = ()
  delivery_history: tuple[OperatorIncidentDelivery, ...] = ()
  audit_events: tuple[OperatorAuditEvent, ...] = ()
  issues: tuple[str, ...] = ()
