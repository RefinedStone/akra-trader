from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from numbers import Number

from akra_trader.domain.models import GuardedLiveRuntimeRecovery
from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import OperatorAuditEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.application_support.guarded_live_alert_state_refresh import (
  _refresh_guarded_live_alert_state,
)
from akra_trader.application_support.guarded_live_alert_state_refresh import (
  get_guarded_live_status,
)
from akra_trader.application_support.guarded_live_incident_event_construction import (
  _build_guarded_live_incident_events,
)
from akra_trader.application_support.guarded_live_incident_workflow_orchestration import (
  _escalate_incident_event,
)
from akra_trader.application_support.guarded_live_incident_workflow_orchestration import (
  _refresh_guarded_live_incident_workflow,
)
from akra_trader.application_support.guarded_live_incident_workflow_orchestration import (
  _sync_incident_provider_workflow,
)
from akra_trader.application_support.guarded_live_delivery_orchestration import (
  _deliver_guarded_live_incident_events,
)
from akra_trader.application_support.guarded_live_delivery_orchestration import (
  _retry_guarded_live_incident_deliveries,
)
from akra_trader.application_support.guarded_live_remediation_orchestration import (
  _execute_local_guarded_live_session_remediation,
)
from akra_trader.application_support.guarded_live_remediation_orchestration import (
  _execute_local_incident_remediation,
)
from akra_trader.application_support.guarded_live_remediation_orchestration import (
  _request_incident_remediation,
)
from akra_trader.application_support.guarded_live_external_sync_orchestration import (
  sync_guarded_live_incident_from_external,
)
from akra_trader.application_support.guarded_live_pull_sync_orchestration import (
  _apply_provider_pull_sync,
)
from akra_trader.application_support.guarded_live_pull_sync_orchestration import (
  _pull_sync_guarded_live_provider_recovery,
)

def recover_guarded_live_runtime_state(
  app,
  *,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state = app._guarded_live_state.load_state()
  snapshot = app._select_guarded_live_recovery_snapshot(state)
  recovered_exposures, recovery_issues = app._recover_exposures_from_venue_snapshot(snapshot)
  recovered_open_orders = snapshot.open_orders or state.order_book.open_orders
  if not snapshot.open_orders and state.order_book.open_orders:
    recovery_issues = (*recovery_issues, "using_durable_order_book_sync")

  if snapshot.verification_state == "unavailable":
    recovery_state = GuardedLiveRuntimeRecovery(
      state="failed",
      recovered_at=current_time,
      recovered_by=actor,
      reason=reason,
      source_snapshot_at=snapshot.captured_at,
      source_verification_state=snapshot.verification_state,
      summary="Guarded-live runtime recovery failed because no usable venue snapshot was available.",
      exposures=(),
      open_orders=(),
      issues=tuple(snapshot.issues),
    )
  else:
    recovered_with_warnings = bool(recovery_issues) or snapshot.verification_state != "verified"
    recovery_state = GuardedLiveRuntimeRecovery(
      state="recovered_with_warnings" if recovered_with_warnings else "recovered",
      recovered_at=current_time,
      recovered_by=actor,
      reason=reason,
      source_snapshot_at=snapshot.captured_at,
      source_verification_state=snapshot.verification_state,
      summary=(
        "Guarded-live runtime state recovered from the latest verified venue snapshot."
        if not recovered_with_warnings
        else "Guarded-live runtime state recovered from venue data with follow-up issues to review."
      ),
      exposures=recovered_exposures,
      open_orders=recovered_open_orders,
      issues=tuple(dict.fromkeys((*snapshot.issues, *recovery_issues))),
    )
  projected_state = replace(state, recovery=recovery_state)
  refreshed_reconciliation = app._build_guarded_live_reconciliation(
    state=projected_state,
    checked_at=current_time,
    checked_by=actor,
  )

  event = OperatorAuditEvent(
    event_id=f"guarded-live-runtime-recovered:{current_time.isoformat()}",
    timestamp=current_time,
    actor=actor,
    kind="guarded_live_runtime_recovered",
    summary="Guarded-live runtime recovery recorded.",
    detail=(
      f"Reason: {reason}. {recovery_state.summary} "
      f"Recovered {len(recovery_state.exposures)} exposure(s) and {len(recovery_state.open_orders)} open order(s)."
    ),
    source="guarded_live",
  )
  app._persist_guarded_live_state(
    replace(
      projected_state,
      reconciliation=refreshed_reconciliation,
      recovery=recovery_state,
      audit_events=(event, *state.audit_events),
    )
  )
  return app.get_guarded_live_status()

def acknowledge_guarded_live_incident(
  app,
  *,
  event_id: str,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state, _ = app._refresh_guarded_live_alert_state(current_time=current_time)
  incident = app._require_active_guarded_live_incident(state=state, event_id=event_id)
  if incident.acknowledgment_state == "acknowledged":
    return app.get_guarded_live_status()

  updated_incident = replace(
    incident,
    acknowledgment_state="acknowledged",
    acknowledged_at=current_time,
    acknowledged_by=actor,
    acknowledgment_reason=reason,
    next_escalation_at=None,
  )
  incident_events = app._replace_incident_event(
    incident_events=state.incident_events,
    updated_incident=updated_incident,
  )
  delivery_history = app._suppress_pending_incident_retries(
    delivery_history=state.delivery_history,
    incident_event_id=event_id,
    reason="acknowledged_by_operator",
  )
  updated_incident, delivery_history = app._sync_incident_provider_workflow(
    incident=updated_incident,
    delivery_history=delivery_history,
    current_time=current_time,
    action="acknowledge",
    actor=actor,
    detail=reason,
  )
  incident_events = app._replace_incident_event(
    incident_events=incident_events,
    updated_incident=updated_incident,
  )
  incident_events = app._apply_incident_delivery_state(
    incident_events=incident_events,
    delivery_history=delivery_history,
  )
  audit_event = OperatorAuditEvent(
    event_id=f"guarded-live-incident-acknowledged:{event_id}:{current_time.isoformat()}",
    timestamp=current_time,
    actor=actor,
    kind="guarded_live_incident_acknowledged",
    summary=f"Guarded-live incident acknowledged for {incident.alert_id}.",
    detail=(
      f"Reason: {reason}. Incident {event_id} acknowledged and pending retries suppressed. "
      f"Provider workflow: {updated_incident.provider_workflow_state}."
    ),
    run_id=incident.run_id,
    session_id=incident.session_id,
    source="guarded_live",
  )
  app._persist_guarded_live_state(
    replace(
      state,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=(audit_event, *state.audit_events),
    )
  )
  return app.get_guarded_live_status()

def remediate_guarded_live_incident(
  app,
  *,
  event_id: str,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state, _ = app._refresh_guarded_live_alert_state(current_time=current_time)
  incident = app._require_active_guarded_live_incident(state=state, event_id=event_id)
  if incident.remediation.state == "not_applicable":
    raise ValueError("Guarded-live incident does not expose a remediation workflow")

  incident, local_results = app._execute_local_incident_remediation(
    incident=incident,
    actor=actor,
    current_time=current_time,
  )

  delivery_history = app._suppress_pending_incident_retries(
    delivery_history=state.delivery_history,
    incident_event_id=event_id,
    reason="manual_remediation_requested",
    phase="provider_remediate",
  )
  updated_incident, remediation_records = app._request_incident_remediation(
    incident=incident,
    delivery_history=delivery_history,
    current_time=current_time,
    actor=actor,
    detail=reason,
  )
  delivery_history = tuple((*remediation_records, *delivery_history))
  incident_events = app._replace_incident_event(
    incident_events=state.incident_events,
    updated_incident=updated_incident,
  )
  incident_events = app._apply_incident_delivery_state(
    incident_events=incident_events,
    delivery_history=delivery_history,
  )
  audit_event = OperatorAuditEvent(
    event_id=f"guarded-live-incident-remediation-requested:{event_id}:{current_time.isoformat()}",
    timestamp=current_time,
    actor=actor,
    kind="guarded_live_incident_remediation_requested",
    summary=f"Guarded-live remediation requested for {incident.alert_id}.",
    detail=(
      f"Reason: {reason}. Remediation state: {updated_incident.remediation.state}. "
      f"Provider workflow: {updated_incident.provider_workflow_state}. "
      f"Local execution: {app._summarize_local_remediation_results(local_results)}."
    ),
    run_id=incident.run_id,
    session_id=incident.session_id,
    source="guarded_live",
  )
  latest_state = app._guarded_live_state.load_state()
  app._persist_guarded_live_state(
    replace(
      latest_state,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=(audit_event, *latest_state.audit_events),
    )
  )
  return app.get_guarded_live_status()

def escalate_guarded_live_incident(
  app,
  *,
  event_id: str,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state, _ = app._refresh_guarded_live_alert_state(current_time=current_time)
  incident = app._require_active_guarded_live_incident(state=state, event_id=event_id)
  if incident.escalation_level >= app._operator_alert_incident_max_escalations:
    raise ValueError("incident escalation limit reached")

  (
    updated_incident,
    delivery_history,
    escalation_audit_event,
  ) = app._escalate_incident_event(
    incident=incident,
    delivery_history=state.delivery_history,
    current_time=current_time,
    actor=actor,
    reason=reason,
    trigger="manual_operator_escalation",
  )
  incident_events = app._replace_incident_event(
    incident_events=state.incident_events,
    updated_incident=updated_incident,
  )
  incident_events = app._apply_incident_delivery_state(
    incident_events=incident_events,
    delivery_history=delivery_history,
  )
  app._persist_guarded_live_state(
    replace(
      state,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=(escalation_audit_event, *state.audit_events),
    )
  )
  return app.get_guarded_live_status()


def _build_live_operator_alerts_for_run(
  app,
  *,
  run: RunRecord,
  current_time: datetime,
) -> list[OperatorAlert]:
  session = run.provenance.runtime_session
  if session is None:
    return []

  alerts: list[OperatorAlert] = []
  symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
  delivery_targets = app._guarded_live_delivery_targets()
  market_context = app._build_operator_alert_market_context(
    symbol=symbol,
    symbols=list(run.config.symbols),
    timeframe=run.config.timeframe,
  )
  failed_event = app._latest_runtime_note_event(run=run, kind="guarded_live_worker_failed")
  if failed_event is not None or session.lifecycle_state == "failed" or run.status == RunStatus.FAILED:
    detected_at = (
      failed_event["timestamp"]
      or run.ended_at
      or session.last_heartbeat_at
      or run.started_at
    )
    detail = failed_event["detail"] if failed_event is not None else (
      run.notes[-1] if run.notes else "Guarded-live worker entered a failed runtime state."
    )
    alerts.append(
      OperatorAlert(
        alert_id=f"guarded-live:worker-failed:{run.config.run_id}:{session.session_id}",
        severity="critical",
        category="worker_failure",
        summary=f"Guarded-live worker failed for {symbol}.",
        detail=detail,
        detected_at=detected_at,
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
      )
    )

  heartbeat_at = session.last_heartbeat_at or session.started_at
  heartbeat_age_seconds = (current_time - heartbeat_at).total_seconds()
  if (
    run.status == RunStatus.RUNNING
    and session.lifecycle_state == "active"
    and heartbeat_age_seconds > session.heartbeat_timeout_seconds
  ):
    alerts.append(
      OperatorAlert(
        alert_id=f"guarded-live:worker-stale:{run.config.run_id}:{session.session_id}",
        severity="warning",
        category="stale_runtime",
        summary=f"Guarded-live worker heartbeat is stale for {symbol}.",
        detail=(
          f"Last heartbeat at {heartbeat_at.isoformat()} exceeded the "
          f"{session.heartbeat_timeout_seconds}s timeout while the live run remains active."
        ),
        detected_at=heartbeat_at,
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
      )
    )

  risk_issues: list[str] = []
  latest_equity = run.equity_curve[-1] if run.equity_curve else None
  max_drawdown_pct = run.metrics.get("max_drawdown_pct")
  if isinstance(max_drawdown_pct, Number) and float(max_drawdown_pct) >= app._guarded_live_drawdown_breach_pct:
    risk_issues.append(
      f"max drawdown {float(max_drawdown_pct):.2f}% breached the "
      f"{app._guarded_live_drawdown_breach_pct:.2f}% guardrail"
    )
  total_return_pct = run.metrics.get("total_return_pct")
  if isinstance(total_return_pct, Number) and float(total_return_pct) <= -app._guarded_live_loss_breach_pct:
    risk_issues.append(
      f"total return {float(total_return_pct):.2f}% breached the "
      f"-{app._guarded_live_loss_breach_pct:.2f}% loss guardrail"
    )
  if latest_equity is not None and latest_equity.cash < -app._guarded_live_balance_tolerance:
    risk_issues.append(
      f"cash balance fell below zero to {latest_equity.cash:.2f}"
    )
  if latest_equity is not None and latest_equity.equity > app._guarded_live_balance_tolerance:
    pending_buy_notional = app._estimate_guarded_live_open_buy_notional(run)
    gross_open_risk = max(latest_equity.exposure, 0.0) + pending_buy_notional
    gross_open_risk_ratio = gross_open_risk / latest_equity.equity
    if gross_open_risk_ratio > app._guarded_live_gross_open_risk_ratio:
      risk_issues.append(
        f"gross open risk reached {gross_open_risk_ratio:.2f}x equity "
        f"({gross_open_risk:.2f} notional including {pending_buy_notional:.2f} pending buy notional)"
      )
  if risk_issues:
    alerts.append(
      OperatorAlert(
        alert_id=f"guarded-live:risk-breach:{run.config.run_id}:{session.session_id}",
        severity="critical",
        category="risk_breach",
        summary=f"Guarded-live risk guardrail breached for {symbol}.",
        detail=(
          "; ".join(risk_issues)
          + (
            f". Latest equity {latest_equity.equity:.2f}."
            if latest_equity is not None
            else ""
          )
        ),
        detected_at=(
          latest_equity.timestamp
          if latest_equity is not None
          else heartbeat_at
        ),
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
      )
    )

  if run.status == RunStatus.RUNNING and session.recovery_count >= app._guarded_live_recovery_alert_threshold:
    alerts.append(
      OperatorAlert(
        alert_id=f"guarded-live:recovery-loop:{run.config.run_id}:{session.session_id}",
        severity="critical" if session.recovery_count >= app._guarded_live_recovery_alert_threshold + 1 else "warning",
        category="runtime_recovery",
        summary=f"Guarded-live worker recovery loop detected for {symbol}.",
        detail=(
          f"Runtime session recovered {session.recovery_count} times. "
          f"Last recovery: {session.last_recovery_reason or 'unknown'} at "
          f"{session.last_recovered_at.isoformat() if session.last_recovered_at is not None else 'n/a'}."
        ),
        detected_at=session.last_recovered_at or heartbeat_at,
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
      )
    )

  if run.status == RunStatus.RUNNING:
    stale_orders = []
    for order in run.orders:
      if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
        continue
      synced_at = order.last_synced_at or order.updated_at or order.created_at
      if (current_time - synced_at).total_seconds() <= session.heartbeat_timeout_seconds:
        continue
      stale_orders.append((order, synced_at))
    if stale_orders:
      stale_order_ids = ", ".join(order.order_id for order, _ in stale_orders[:3])
      oldest_sync_at = min(synced_at for _, synced_at in stale_orders)
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:order-sync:{run.config.run_id}:{session.session_id}",
          severity="warning",
          category="order_sync",
          summary=f"Guarded-live venue order sync is stale for {symbol}.",
          detail=(
            f"{len(stale_orders)} active order(s) have not synced within "
            f"{session.heartbeat_timeout_seconds}s. Orders: {stale_order_ids}."
          ),
          detected_at=oldest_sync_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
  return alerts
