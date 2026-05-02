from __future__ import annotations

import inspect
from datetime import datetime

from akra_trader.application_support import guarded_live_alert_state_refresh as guarded_live_alert_state_refresh_support
from akra_trader.application_support import guarded_live_alert_workflows as guarded_live_alert_workflows_support
from akra_trader.application_support import guarded_live_external_sync_orchestration as guarded_live_external_sync_orchestration_support
from akra_trader.application_support import guarded_live_market_context_support as guarded_live_market_context_support
from akra_trader.application_support import guarded_live_market_context_workflows as guarded_live_market_context_workflows_support
from akra_trader.application_support import guarded_live_payload_helpers as guarded_live_payload_helpers_support
from akra_trader.application_support import guarded_live_provider_recovery as guarded_live_provider_recovery_support
from akra_trader.domain.models import GuardedLiveReconciliationFinding
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunStatus


from akra_trader.application_flows.guarded_live.market_data_alert_mixin import GuardedLiveMarketDataAlertMixin


class GuardedLiveAlertCompatibilityMixin(GuardedLiveMarketDataAlertMixin):
  def _build_guarded_live_reconciliation_result(
    self,
    *,
    state: GuardedLiveState | None = None,
  ) -> tuple[
    GuardedLiveInternalStateSnapshot,
    GuardedLiveVenueStateSnapshot,
    list[GuardedLiveReconciliationFinding],
  ]:
    findings: list[GuardedLiveReconciliationFinding] = []
    effective_state = state or self._guarded_live_state.load_state()
    internal_snapshot = self._build_guarded_live_internal_snapshot(state=effective_state)
    venue_snapshot = self._venue_state.capture_snapshot()

    if venue_snapshot.venue != self._guarded_live_venue:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="guarded_live_venue_mismatch",
          severity="critical",
          summary="Venue-state snapshot does not match the configured guarded-live venue.",
          detail=(
            f"Guarded-live is configured for {self._guarded_live_venue}, "
            f"but venue-state reconciliation captured {venue_snapshot.venue}."
          ),
        )
      )

    sandbox_alerts, _ = self._collect_sandbox_operator_visibility(current_time=self._clock())
    if sandbox_alerts:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="runtime_alerts_present",
          severity="warning",
          summary=f"{len(sandbox_alerts)} unresolved runtime alert(s) remain active.",
          detail="Guarded-live candidacy stays blocked while sandbox runtime alerts remain unresolved.",
        )
      )

    inconsistent_sandbox_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_sandbox_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="sandbox_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_sandbox_runs)} sandbox run(s) are missing persisted runtime session state."
          ),
          detail="Continuous sandbox workers must keep runtime-session state for restart safety and auditability.",
        )
      )

    inconsistent_live_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_live_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="live_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_live_runs)} live run(s) are missing persisted runtime session state."
          ),
          detail="Guarded-live workers must keep runtime-session state for restart safety and venue auditability.",
        )
      )

    stale_terminal_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_sessions)} terminal sandbox run(s) still report an active runtime session."
          ),
          detail="Terminal runs should not keep active worker-session state after stop, failure, or completion.",
        )
      )

    stale_terminal_live_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_live_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_live_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_live_sessions)} terminal live run(s) still report an active runtime session."
          ),
          detail="Terminal guarded-live runs should not keep active worker-session state after stop or failure.",
        )
      )

    if venue_snapshot.verification_state != "verified":
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_snapshot_unavailable",
          severity="critical" if venue_snapshot.verification_state == "unavailable" else "warning",
          summary=(
            "Venue-state verification is unavailable."
            if venue_snapshot.verification_state == "unavailable"
            else "Venue-state verification completed with partial data."
          ),
          detail=(
            ", ".join(venue_snapshot.issues)
            if venue_snapshot.issues
            else "The venue adapter did not return a fully verified account snapshot."
          ),
        )
      )

    findings.extend(
      self._build_guarded_live_venue_mismatch_findings(
        internal_snapshot=internal_snapshot,
        venue_snapshot=venue_snapshot,
      )
    )
    return internal_snapshot, venue_snapshot, findings

  def _build_guarded_live_operator_alerts(
    self,
    *,
    state: GuardedLiveState,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    alerts: list[OperatorAlert] = []
    delivery_targets = self._guarded_live_delivery_targets()
    live_runs = self._runs.list_runs(mode=RunMode.LIVE.value)
    live_context_active = bool(live_runs) or state.ownership.state in {"owned", "orphaned"}
    guarded_live_context_symbol = self._first_non_empty_string(
      state.ownership.symbol,
      state.session_handoff.symbol,
      state.session_restore.symbol,
      state.order_book.symbol,
    )
    guarded_live_context_timeframe = self._first_non_empty_string(
      state.session_handoff.timeframe,
      state.session_restore.timeframe,
    )

    alerts.extend(
      self._build_guarded_live_market_data_alerts(
        live_runs=live_runs,
        current_time=current_time,
      )
    )

    if state.kill_switch.state == "engaged":
      detected_at = state.kill_switch.last_engaged_at or state.kill_switch.updated_at
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:kill-switch",
          severity="warning",
          category="kill_switch",
          summary="Guarded-live kill switch is engaged.",
          detail=(
            f"{state.kill_switch.reason} Updated by {state.kill_switch.updated_by} at "
            f"{state.kill_switch.updated_at.isoformat()}."
          ),
          detected_at=detected_at,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.reconciliation.state == "issues_detected":
      finding_copy = "; ".join(finding.summary for finding in state.reconciliation.findings[:3])
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:reconciliation",
          severity=(
            "critical"
            if any(finding.severity == "critical" for finding in state.reconciliation.findings)
            else "warning"
          ),
          category="reconciliation",
          summary="Guarded-live reconciliation has unresolved findings.",
          detail=(
            f"{state.reconciliation.summary} "
            f"{finding_copy if finding_copy else 'Review the guarded-live venue snapshot and internal exposure state.'}"
          ),
          detected_at=state.reconciliation.checked_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.recovery.state == "failed":
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:recovery-failed",
          severity="critical",
          category="runtime_recovery",
          summary="Guarded-live runtime recovery failed.",
          detail=(
            f"{state.recovery.summary} Issues: "
            f"{', '.join(state.recovery.issues) if state.recovery.issues else 'none'}."
          ),
          detected_at=state.recovery.recovered_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.ownership.state == "orphaned":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:ownership:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_ownership",
          summary="Guarded-live session ownership is orphaned.",
          detail=(
            f"Run {state.ownership.owner_run_id or 'n/a'} still owns the guarded-live session, "
            f"but the live worker is not healthy. Last reason: {state.ownership.last_reason or 'n/a'}."
          ),
          detected_at=(
            state.ownership.last_heartbeat_at
            or state.ownership.last_resumed_at
            or state.ownership.claimed_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=state.ownership.symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if live_context_active and state.session_handoff.state == "unavailable":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-transport:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_transport",
          summary="Guarded-live venue session transport is unavailable.",
          detail=(
            "Venue-native session supervision could not be maintained. Issues: "
            f"{', '.join(state.session_handoff.issues) if state.session_handoff.issues else 'none'}."
          ),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=guarded_live_context_symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
    elif live_context_active and state.session_handoff.issues:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-issues:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="session_transport",
          summary="Guarded-live venue session requires operator review.",
          detail=", ".join(state.session_handoff.issues),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=guarded_live_context_symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    order_book_issue_copy: list[str] = []
    if state.session_handoff.order_book_state == "unavailable":
      order_book_issue_copy.append("venue order-book supervision is unavailable")
    if state.order_book.issues:
      order_book_issue_copy.extend(state.order_book.issues)
    if live_context_active and order_book_issue_copy:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:order-book:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="order_book",
          summary="Guarded-live order-book supervision requires review.",
          detail="; ".join(order_book_issue_copy),
          detected_at=(
            state.order_book.synced_at
            or state.session_handoff.last_sync_at
            or state.session_handoff.handed_off_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=guarded_live_context_symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    alerts.extend(
      self._build_guarded_live_channel_operator_alerts(
        state=state,
        current_time=current_time,
        live_context_active=live_context_active,
        delivery_targets=delivery_targets,
      )
    )

    for run in live_runs:
      alerts.extend(self._build_live_operator_alerts_for_run(run=run, current_time=current_time))

    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    return alerts

_GUARDED_LIVE_SUPPORT_MODULES = (
  guarded_live_alert_state_refresh_support,
  guarded_live_alert_workflows_support,
  guarded_live_external_sync_orchestration_support,
  guarded_live_payload_helpers_support,
  guarded_live_provider_recovery_support,
  guarded_live_market_context_support,
  guarded_live_market_context_workflows_support,
)

_GUARDED_LIVE_PUBLIC_DELEGATES = {
  "acknowledge_guarded_live_incident",
  "escalate_guarded_live_incident",
  "get_guarded_live_status",
  "recover_guarded_live_runtime_state",
  "remediate_guarded_live_incident",
  "sync_guarded_live_incident_from_external",
}


def _guarded_live_delegate_descriptor(value):
  params = tuple(inspect.signature(value).parameters.values())
  if params and params[0].name in {"self", "app", "application"}:
    return value
  if params and params[0].name == "cls":
    return classmethod(value)
  return staticmethod(value)


for _support_module in _GUARDED_LIVE_SUPPORT_MODULES:
  for _name in dir(_support_module):
    if _name.startswith("__"):
      continue
    if not (_name.startswith("_") or _name in _GUARDED_LIVE_PUBLIC_DELEGATES):
      continue
    if _name in GuardedLiveAlertCompatibilityMixin.__dict__:
      continue
    _value = getattr(_support_module, _name)
    if not callable(_value):
      continue
    setattr(
      GuardedLiveAlertCompatibilityMixin,
      _name,
      _guarded_live_delegate_descriptor(_value),
    )
