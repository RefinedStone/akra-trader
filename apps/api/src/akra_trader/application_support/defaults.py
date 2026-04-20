from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Callable

from akra_trader.domain.models import ExperimentPreset
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
from akra_trader.port_contracts import ExperimentPresetCatalogPort
from akra_trader.port_contracts import GuardedLiveStatePort
from akra_trader.port_contracts import OperatorAlertDeliveryPort
from akra_trader.port_contracts import VenueExecutionPort
from akra_trader.port_contracts import VenueStatePort


@dataclass(frozen=True)
class _IncidentPagingPolicy:
  policy_id: str
  provider: str | None
  initial_targets: tuple[str, ...]
  escalation_targets: tuple[str, ...]
  resolution_targets: tuple[str, ...]


@dataclass(frozen=True)
class _IncidentRemediationPlan:
  kind: str
  owner: str
  summary: str
  detail: str
  runbook: str


class _EphemeralGuardedLiveStateStore(GuardedLiveStatePort):
  def __init__(self) -> None:
    self._state = GuardedLiveState()

  def load_state(self) -> GuardedLiveState:
    return self._state

  def save_state(self, state: GuardedLiveState) -> GuardedLiveState:
    self._state = state
    return state


class _EphemeralExperimentPresetCatalog(ExperimentPresetCatalogPort):
  def __init__(self) -> None:
    self._presets: dict[str, ExperimentPreset] = {}

  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    presets = list(reversed(tuple(self._presets.values())))
    if strategy_id is not None:
      presets = [
        preset
        for preset in presets
        if preset.strategy_id is None or preset.strategy_id == strategy_id
      ]
    if timeframe is not None:
      presets = [
        preset
        for preset in presets
        if preset.timeframe is None or preset.timeframe == timeframe
      ]
    if lifecycle_stage is not None:
      presets = [
        preset
        for preset in presets
        if preset.lifecycle.stage == lifecycle_stage
      ]
    return presets

  def get_preset(self, preset_id: str) -> ExperimentPreset | None:
    return self._presets.get(preset_id)

  def save_preset(self, preset: ExperimentPreset) -> ExperimentPreset:
    self._presets[preset.preset_id] = preset
    return preset


class UnavailableVenueStateAdapter(VenueStatePort):
  def __init__(self, clock: Callable[[], datetime]) -> None:
    self._clock = clock

  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
    return GuardedLiveVenueStateSnapshot(
      provider="unconfigured",
      venue="unconfigured",
      verification_state="unavailable",
      captured_at=self._clock(),
      issues=("venue_state_port_unconfigured",),
    )


class UnavailableVenueExecutionAdapter(VenueExecutionPort):
  def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
    return False, ("venue_execution_port_unconfigured",)

  def restore_session(
    self,
    *,
    symbol: str,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionRestore:
    raise RuntimeError("Venue execution port is not configured.")

  def handoff_session(
    self,
    *,
    symbol: str,
    timeframe: str,
    owner_run_id: str,
    owner_session_id: str | None,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionHandoff:
    raise RuntimeError("Venue execution port is not configured.")

  def sync_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionSync:
    raise RuntimeError("Venue execution port is not configured.")

  def release_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveVenueSessionHandoff:
    raise RuntimeError("Venue execution port is not configured.")

  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    raise RuntimeError("Venue execution port is not configured.")

  def submit_limit_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    raise RuntimeError("Venue execution port is not configured.")

  def cancel_order(
    self,
    *,
    symbol: str,
    order_id: str,
  ) -> GuardedLiveVenueOrderResult:
    raise RuntimeError("Venue execution port is not configured.")

  def sync_order_states(
    self,
    *,
    symbol: str,
    order_ids: tuple[str, ...],
  ) -> tuple[GuardedLiveVenueOrderResult, ...]:
    raise RuntimeError("Venue execution port is not configured.")


class NoopOperatorAlertDeliveryAdapter(OperatorAlertDeliveryPort):
  def list_targets(self) -> tuple[str, ...]:
    return ()

  def list_supported_workflow_providers(self) -> tuple[str, ...]:
    return ()

  def deliver(
    self,
    *,
    incident: OperatorIncidentEvent,
    targets: tuple[str, ...] | None = None,
    attempt_number: int = 1,
    phase: str = "initial",
  ) -> tuple[OperatorIncidentDelivery, ...]:
    return ()

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
  ) -> tuple[OperatorIncidentDelivery, ...]:
    return ()

  def pull_incident_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
  ) -> OperatorIncidentProviderPullSync | None:
    return None
