from __future__ import annotations

from typing import Any
from typing import Protocol

from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueSessionHandoff
from akra_trader.domain.models import GuardedLiveVenueSessionRestore
from akra_trader.domain.models import GuardedLiveVenueSessionSync
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


class GuardedLiveStatePort(Protocol):
  def load_state(self) -> GuardedLiveState: ...

  def save_state(self, state: GuardedLiveState) -> GuardedLiveState: ...


class OperatorAlertDeliveryPort(Protocol):
  def list_targets(self) -> tuple[str, ...]: ...

  def list_supported_workflow_providers(self) -> tuple[str, ...]: ...

  def deliver(
    self,
    *,
    incident: OperatorIncidentEvent,
    targets: tuple[str, ...] | None = None,
    attempt_number: int = 1,
    phase: str = "initial",
  ) -> tuple[OperatorIncidentDelivery, ...]: ...

  def sync_incident_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None = None,
    attempt_number: int = 1,
  ) -> tuple[OperatorIncidentDelivery, ...]: ...

  def pull_incident_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
  ) -> OperatorIncidentProviderPullSync | None: ...


class VenueStatePort(Protocol):
  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot: ...


class VenueExecutionPort(Protocol):
  def describe_capability(self) -> tuple[bool, tuple[str, ...]]: ...

  def restore_session(
    self,
    *,
    symbol: str,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionRestore: ...

  def handoff_session(
    self,
    *,
    symbol: str,
    timeframe: str,
    owner_run_id: str,
    owner_session_id: str | None,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionHandoff: ...

  def sync_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionSync: ...

  def release_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveVenueSessionHandoff: ...

  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult: ...

  def submit_limit_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult: ...

  def cancel_order(
    self,
    *,
    symbol: str,
    order_id: str,
  ) -> GuardedLiveVenueOrderResult: ...

  def sync_order_states(
    self,
    *,
    symbol: str,
    order_ids: tuple[str, ...],
  ) -> tuple[GuardedLiveVenueOrderResult, ...]: ...
