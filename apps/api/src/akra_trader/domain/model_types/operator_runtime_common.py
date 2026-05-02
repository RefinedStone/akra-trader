from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from akra_trader.domain.model_types.provider_provenance import ProviderProvenanceSchedulerHealth

@dataclass(frozen=True)
class OperatorAlertPrimaryFocus:
  symbol: str | None = None
  timeframe: str | None = None
  candidate_symbols: tuple[str, ...] = ()
  candidate_count: int = 0
  policy: str = "none"
  reason: str | None = None


@dataclass(frozen=True)
class OperatorAlertMarketContextFieldProvenance:
  scope: str | None = None
  path: str | None = None


@dataclass(frozen=True)
class OperatorAlertMarketContextProvenance:
  provider: str | None = None
  vendor_field: str | None = None
  symbol: OperatorAlertMarketContextFieldProvenance | None = None
  symbols: OperatorAlertMarketContextFieldProvenance | None = None
  timeframe: OperatorAlertMarketContextFieldProvenance | None = None
  primary_focus: OperatorAlertMarketContextFieldProvenance | None = None


@dataclass(frozen=True)
class OperatorAlert:
  alert_id: str
  severity: str
  category: str
  summary: str
  detail: str
  detected_at: datetime
  run_id: str | None = None
  session_id: str | None = None
  symbol: str | None = None
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  primary_focus: OperatorAlertPrimaryFocus | None = None
  occurrence_id: str | None = None
  timeline_key: str | None = None
  timeline_position: int | None = None
  timeline_total: int | None = None
  status: str = "active"
  resolved_at: datetime | None = None
  source: str = "runtime"
  delivery_targets: tuple[str, ...] = ()


@dataclass(frozen=True)
class OperatorAuditEvent:
  event_id: str
  timestamp: datetime
  actor: str
  kind: str
  summary: str
  detail: str
  run_id: str | None = None
  session_id: str | None = None
  source: str = "runtime"
