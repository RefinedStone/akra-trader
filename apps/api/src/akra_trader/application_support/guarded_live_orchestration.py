from __future__ import annotations

from typing import Any

from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunStatus


def maintain_guarded_live_worker_sessions(
  app: Any,
  *,
  force_recovery: bool = False,
  recovery_reason: str = "heartbeat_timeout",
) -> dict[str, int]:
  if not app._guarded_live_execution_enabled:
    return {
      "maintained": 0,
      "recovered": 0,
      "ticks_processed": 0,
      "orders_submitted": 0,
      "orders_synced": 0,
    }

  maintained = 0
  recovered = 0
  ticks_processed = 0
  orders_submitted = 0
  orders_synced = 0
  current_time = app._clock()
  for run in app._runs.list_runs(mode=RunMode.LIVE.value):
    if run.status != RunStatus.RUNNING:
      continue
    try:
      state = app._guarded_live_state.load_state()
      if force_recovery or app._run_supervisor.needs_worker_recovery(run=run, now=current_time):
        app._run_supervisor.recover_worker_session(
          run=run,
          worker_kind=app._guarded_live_worker_kind,
          heartbeat_interval_seconds=app._guarded_live_worker_heartbeat_interval_seconds,
          heartbeat_timeout_seconds=app._guarded_live_worker_heartbeat_timeout_seconds,
          reason=recovery_reason,
          now=current_time,
          started_at=run.started_at,
          primed_candle_count=app._infer_sandbox_primed_candle_count(run),
          processed_tick_count=run.provenance.runtime_session.processed_tick_count if run.provenance.runtime_session else 0,
          last_processed_candle_at=app._infer_last_processed_candle_at(run),
          last_seen_candle_at=app._infer_last_processed_candle_at(run),
        )
        run.notes.append(
          f"{current_time.isoformat()} | guarded_live_worker_recovered | {recovery_reason}"
        )
        app._append_guarded_live_audit_event(
          kind="guarded_live_worker_recovered",
          actor="system",
          summary=f"Guarded-live worker recovered for {run.config.symbols[0]}.",
          detail=f"Recovery reason: {recovery_reason}.",
          run_id=run.config.run_id,
          session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
        )
        recovered += 1

      session_handoff = state.session_handoff
      if session_handoff.owner_run_id == run.config.run_id and session_handoff.state == "active":
        session_sync = app._sync_guarded_live_session(run=run, handoff=session_handoff)
        orders_synced += session_sync["synced"]
        session_handoff = session_sync["handoff"]
      else:
        orders_synced += app._sync_guarded_live_orders(run)
        session_handoff = app._activate_guarded_live_venue_session(
          run=run,
          reason=recovery_reason if force_recovery else "worker_heartbeat",
        )
      advance = app._advance_guarded_live_worker_run(run)
      ticks_processed += advance["ticks_processed"]
      orders_submitted += advance["orders_submitted"]
      app._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
      app._claim_guarded_live_session_ownership(
        run=run,
        actor="system",
        reason=recovery_reason if force_recovery else "worker_heartbeat",
        resumed=force_recovery,
        session_handoff=session_handoff,
      )
    except Exception as exc:
      app._run_supervisor.fail(
        run,
        reason=f"{current_time.isoformat()} | guarded_live_worker_failed | {exc}",
        now=current_time,
      )
      session_handoff = app._release_guarded_live_venue_session(run=run)
      app._release_guarded_live_session_ownership(
        run=run,
        actor="system",
        reason=str(exc),
        ownership_state="orphaned",
        session_handoff=session_handoff,
      )
      app._append_guarded_live_audit_event(
        kind="guarded_live_worker_failed",
        actor="system",
        summary=f"Guarded-live worker failed for {run.config.symbols[0]}.",
        detail=str(exc),
        run_id=run.config.run_id,
        session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
      )
    app._runs.save_run(run)
    maintained += 1

  return {
    "maintained": maintained,
    "recovered": recovered,
    "ticks_processed": ticks_processed,
    "orders_submitted": orders_submitted,
    "orders_synced": orders_synced,
  }
