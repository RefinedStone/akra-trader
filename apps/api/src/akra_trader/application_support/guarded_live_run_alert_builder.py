from __future__ import annotations

from datetime import datetime
from numbers import Number

from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus

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

