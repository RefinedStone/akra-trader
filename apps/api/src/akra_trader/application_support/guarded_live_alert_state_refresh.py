from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any

from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import RunMode

def get_guarded_live_status(app: Any) -> GuardedLiveStatus:
  current_time = app._clock()
  sandbox_alerts, _ = app._collect_sandbox_operator_visibility(current_time=current_time)
  state, live_alerts = app._refresh_guarded_live_alert_state(current_time=current_time)
  runtime_alerts = [*sandbox_alerts, *live_alerts]
  running_sandbox_count = app._count_running_runs(RunMode.SANDBOX)
  running_paper_count = app._count_running_runs(RunMode.PAPER)
  running_live_count = app._count_running_runs(RunMode.LIVE)
  venue_execution_ready, venue_execution_issues = app._venue_execution.describe_capability()

  blockers: list[str] = []
  if not app._guarded_live_execution_enabled:
    blockers.append("Guarded-live venue execution is disabled in configuration.")
  if state.kill_switch.state == "engaged":
    blockers.append("Kill switch is engaged for operator-controlled runtime sessions.")
  if state.reconciliation.state != "clear":
    blockers.append("Guarded-live reconciliation has not been cleared.")
  if state.recovery.state not in {"recovered", "recovered_with_warnings"}:
    blockers.append("Guarded-live runtime recovery has not been recorded from venue snapshots.")
  if state.recovery.state == "failed":
    blockers.append("Guarded-live runtime recovery failed after the latest restart or fault drill.")
  if not venue_execution_ready:
    blockers.append(
      "Venue order execution is unavailable: "
      + (", ".join(venue_execution_issues) if venue_execution_issues else "adapter not ready")
      + "."
    )
  if state.ownership.state in {"owned", "orphaned"} and state.ownership.owner_run_id is not None:
    blockers.append(
      "Guarded-live session ownership is still held by "
      f"{state.ownership.owner_run_id}. Resume or release it before launching a new live worker."
    )
  if runtime_alerts:
    blockers.append("Unresolved operator alerts remain in runtime operations.")

  audit_events = tuple(
    sorted(state.audit_events, key=lambda event: event.timestamp, reverse=True)
  )
  incident_events = tuple(
    sorted(state.incident_events, key=lambda event: event.timestamp, reverse=True)
  )
  delivery_history = tuple(
    sorted(state.delivery_history, key=lambda record: record.attempted_at, reverse=True)
  )
  return GuardedLiveStatus(
    generated_at=current_time,
    candidacy_status="blocked" if blockers else "candidate",
    blockers=tuple(dict.fromkeys(blockers)),
    active_alerts=tuple(live_alerts),
    alert_history=state.alert_history,
    incident_events=incident_events,
    delivery_history=delivery_history,
    kill_switch=state.kill_switch,
    reconciliation=state.reconciliation,
    recovery=state.recovery,
    ownership=state.ownership,
    order_book=state.order_book,
    session_restore=state.session_restore,
    session_handoff=state.session_handoff,
    audit_events=audit_events,
    active_runtime_alert_count=len(runtime_alerts),
    running_sandbox_count=running_sandbox_count,
    running_paper_count=running_paper_count,
    running_live_count=running_live_count,
  )


def _refresh_guarded_live_alert_state(
  app,
  *,
  current_time: datetime,
  allow_post_remediation_recompute: bool = True,
) -> tuple[GuardedLiveState, list[OperatorAlert]]:
  state = app._guarded_live_state.load_state()
  active_alerts = app._build_guarded_live_operator_alerts(
    state=state,
    current_time=current_time,
  )
  merged_history = app._merge_operator_alert_history(
    existing=state.alert_history,
    active_alerts=active_alerts,
    current_time=current_time,
  )
  incident_events = app._build_guarded_live_incident_events(
    previous_history=state.alert_history,
    merged_history=merged_history,
    current_time=current_time,
  )
  delivery_records = state.delivery_history
  new_incident_events, new_delivery_records, auto_remediation_executed = app._deliver_guarded_live_incident_events(
    incident_events=incident_events,
    current_time=current_time,
  )
  delivery_records = tuple((*new_delivery_records, *delivery_records))
  provider_synced_incident_events, provider_synced_delivery_history, provider_pull_audit_events, provider_pull_executed = (
    app._pull_sync_guarded_live_provider_recovery(
      incident_events=tuple((*new_incident_events, *state.incident_events)),
      delivery_history=delivery_records,
      current_time=current_time,
    )
  )
  delivery_records = provider_synced_delivery_history
  workflow_incident_events, workflow_delivery_history, workflow_audit_events = (
    app._refresh_guarded_live_incident_workflow(
      incident_events=provider_synced_incident_events,
      delivery_history=delivery_records,
      current_time=current_time,
    )
  )
  delivery_records = workflow_delivery_history
  refreshed_incident_events = app._apply_incident_delivery_state(
    incident_events=workflow_incident_events,
    delivery_history=delivery_records,
  )
  retry_delivery_records = app._retry_guarded_live_incident_deliveries(
    incident_events=refreshed_incident_events,
    delivery_history=delivery_records,
    current_time=current_time,
  )
  if retry_delivery_records:
    delivery_records = tuple((*retry_delivery_records, *delivery_records))
    refreshed_incident_events = app._apply_incident_delivery_state(
      incident_events=refreshed_incident_events,
      delivery_history=delivery_records,
    )
  if (
    merged_history != state.alert_history
    or refreshed_incident_events != state.incident_events
    or delivery_records != state.delivery_history
    or bool(provider_pull_audit_events)
    or bool(workflow_audit_events)
  ):
    latest_state = app._guarded_live_state.load_state()
    state = app._persist_guarded_live_state(
      replace(
        latest_state,
        alert_history=merged_history,
        incident_events=refreshed_incident_events,
        delivery_history=delivery_records,
        audit_events=tuple((*provider_pull_audit_events, *workflow_audit_events, *latest_state.audit_events)),
      )
    )
  if (auto_remediation_executed or provider_pull_executed) and allow_post_remediation_recompute:
    return app._refresh_guarded_live_alert_state(
      current_time=current_time,
      allow_post_remediation_recompute=False,
    )
  return state, active_alerts
