from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any

from akra_trader.domain.models import GuardedLiveSessionOwnership
from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveVenueSessionHandoff
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord

def _resolve_guarded_live_remediation_run(
  app: Any,
  *,
  incident: OperatorIncidentEvent,
  state: GuardedLiveState,
) -> RunRecord | None:
  if incident.run_id is not None and (run := app._runs.get_run(incident.run_id)) is not None:
    return run
  owner_run_id = state.session_handoff.owner_run_id or state.ownership.owner_run_id
  if owner_run_id is None:
    return None
  return app._runs.get_run(owner_run_id)

def _resolve_guarded_live_remediation_identity(
  *,
  run: RunRecord | None,
  state: GuardedLiveState,
) -> tuple[str, str]:
  if run is not None:
    symbol = run.config.symbols[0] if run.config.symbols else "unknown"
    timeframe = run.config.timeframe or "unknown"
    return symbol, timeframe
  symbol = state.session_handoff.symbol or state.ownership.symbol or "unknown"
  timeframe = state.session_handoff.timeframe or "unknown"
  return symbol, timeframe

def _build_guarded_live_state_for_local_session_remediation(
  app: Any,
  *,
  state: GuardedLiveState,
  run: RunRecord,
  actor: str,
  reason: str,
  session_handoff: GuardedLiveVenueSessionHandoff,
) -> GuardedLiveState:
  session = run.provenance.runtime_session
  current_time = app._clock()
  existing = state.ownership
  return replace(
    state,
    ownership=GuardedLiveSessionOwnership(
      state="owned",
      owner_run_id=run.config.run_id,
      owner_session_id=session.session_id if session is not None else existing.owner_session_id,
      symbol=run.config.symbols[0] if run.config.symbols else existing.symbol,
      claimed_at=existing.claimed_at if existing.owner_run_id == run.config.run_id else current_time,
      claimed_by=existing.claimed_by if existing.owner_run_id == run.config.run_id else actor,
      last_heartbeat_at=session.last_heartbeat_at if session is not None else existing.last_heartbeat_at,
      last_order_sync_at=current_time,
      last_resumed_at=existing.last_resumed_at,
      last_reason=reason,
      last_released_at=None,
    ),
    order_book=app._build_guarded_live_order_book_sync(run=run),
    session_restore=app._resolve_guarded_live_session_restore_state(
      run=run,
      existing=state.session_restore,
    ),
    session_handoff=app._resolve_guarded_live_session_handoff_state(
      run=run,
      existing=state.session_handoff,
      session_handoff=session_handoff,
    ),
  )

def _summarize_guarded_live_session_remediation_result(
  *,
  remediation_kind: str,
  handoff: GuardedLiveVenueSessionHandoff,
) -> str:
  symbol = handoff.symbol or "unknown"
  timeframe = handoff.timeframe or "unknown"
  if remediation_kind == "channel_restore":
    detail = (
      f"{remediation_kind}:{symbol}:{timeframe}:channel_restore={handoff.channel_restore_state};"
      f"continuation={handoff.channel_continuation_state};"
      f"transport={handoff.transport};source={handoff.source};state={handoff.state}"
    )
    if handoff.channel_last_restored_at is not None:
      detail += f";restored_at={handoff.channel_last_restored_at.isoformat()}"
    if handoff.channel_last_continued_at is not None:
      detail += f";continued_at={handoff.channel_last_continued_at.isoformat()}"
    if handoff.issues:
      detail += f";issues={','.join(handoff.issues[:3])}"
    return detail
  detail = (
    f"{remediation_kind}:{symbol}:{timeframe}:order_book={handoff.order_book_state};"
    f"transport={handoff.transport};source={handoff.source};state={handoff.state};"
    f"rebuilds={handoff.order_book_rebuild_count};gaps={handoff.order_book_gap_count}"
  )
  if handoff.order_book_last_rebuilt_at is not None:
    detail += f";rebuilt_at={handoff.order_book_last_rebuilt_at.isoformat()}"
  if handoff.order_book_best_bid_price is not None or handoff.order_book_best_ask_price is not None:
    detail += (
      f";top_of_book={handoff.order_book_best_bid_price or 0.0:.8f}/"
      f"{handoff.order_book_best_ask_price or 0.0:.8f}"
    )
  if handoff.issues:
    detail += f";issues={','.join(handoff.issues[:3])}"
  return detail

def _resolve_market_data_remediation_targets(
  app: Any,
  *,
  incident: OperatorIncidentEvent,
) -> tuple[str | None, tuple[str, ...]]:
  remediation = incident.remediation
  timeframe: str | None = None
  venue: str | None = None
  alert_parts = incident.alert_id.split(":")
  if remediation.kind == "recent_sync" and len(alert_parts) == 3 and alert_parts[1] == "market-data":
    timeframe = alert_parts[2]
  elif remediation.kind in {
    "historical_backfill",
    "candle_repair",
    "venue_fault_review",
    "market_data_review",
  } and len(alert_parts) == 4 and alert_parts[1].startswith("market-data-"):
    venue = alert_parts[2]
    timeframe = alert_parts[3]

  symbols: list[str] = []
  if incident.run_id is not None and (run := app._runs.get_run(incident.run_id)) is not None:
    timeframe = timeframe or run.config.timeframe
    venue = venue or run.config.venue
    return timeframe, tuple(dict.fromkeys(run.config.symbols))

  if timeframe is None:
    return None, ()

  try:
    status = app._market_data.get_status(timeframe)
  except Exception:
    status = None
  if status is not None:
    venue = venue or status.venue
    for instrument in status.instruments:
      symbol = app._symbol_from_instrument_id(instrument.instrument_id)
      if symbol not in symbols:
        symbols.append(symbol)

  if venue is not None and incident.run_id is None:
    live_runs = [
      run
      for run in app._runs.list_runs(mode=RunMode.LIVE.value)
      if run.config.timeframe == timeframe and run.config.venue == venue
    ]
    if live_runs:
      live_symbols = [
        symbol
        for run in live_runs
        for symbol in run.config.symbols
        if symbol in symbols or not symbols
      ]
      if live_symbols:
        symbols = list(dict.fromkeys(live_symbols))

  return timeframe, tuple(dict.fromkeys(symbols))

def _resolve_local_remediation_state(
  *,
  results: tuple[MarketDataRemediationResult, ...],
) -> str:
  executed = sum(result.status in {"executed", "skipped"} for result in results)
  failed = sum(result.status == "failed" for result in results)
  if failed and executed:
    return "partial"
  if failed:
    return "failed"
  if results and all(result.status == "skipped" for result in results):
    return "skipped"
  return "executed"

def _summarize_local_remediation_results(
  results: tuple[MarketDataRemediationResult, ...],
) -> str:
  if not results:
    return "not_executed"
  detail_copy = [result.detail for result in results if result.detail]
  summary = " ".join(detail_copy[:2]) if detail_copy else "local_remediation_executed"
  if len(detail_copy) > 2:
    summary += f" Additional jobs: {len(detail_copy) - 2}."
  return summary
