from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any

from akra_trader.domain.models import ClosedTrade
from akra_trader.domain.models import Fill
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueSessionHandoff
from akra_trader.domain.models import GuardedLiveVenueSessionRestore
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunRecord
from akra_trader.domain.services import apply_signal
from akra_trader.domain.services import build_equity_point
from akra_trader.domain.services import summarize_performance
from akra_trader.runtime import candles_to_frame


def infer_last_processed_candle_at(run: RunRecord) -> datetime | None:
  if run.equity_curve:
    return run.equity_curve[-1].timestamp
  market_data = run.provenance.market_data
  return market_data.effective_end_at if market_data is not None else None


def infer_sandbox_primed_candle_count(run: RunRecord) -> int:
  session = run.provenance.runtime_session
  if session is not None and session.primed_candle_count > 0:
    return session.primed_candle_count
  market_data = run.provenance.market_data
  if market_data is None:
    return 0
  return market_data.candle_count


def guarded_live_venue_restore_has_state(
  session_restore: GuardedLiveVenueSessionRestore,
) -> bool:
  if session_restore.open_orders:
    return True
  return any(result.status != "unknown" for result in session_restore.synced_orders)


def map_guarded_live_order_status(
  status: str,
  *,
  filled_quantity: float,
  remaining_quantity: float,
) -> OrderStatus:
  normalized = status.lower()
  if normalized in {"canceled", "cancelled", "expired"}:
    return OrderStatus.CANCELED
  if normalized == "rejected":
    return OrderStatus.REJECTED
  if normalized in {"filled", "closed"} or (filled_quantity > 0 and remaining_quantity <= 0):
    return OrderStatus.FILLED
  if normalized in {"partially_filled", "partial"} or (filled_quantity > 0 and remaining_quantity > 0):
    return OrderStatus.PARTIALLY_FILLED
  return OrderStatus.OPEN


def materialize_guarded_live_restored_order(
  app: Any,
  *,
  run: RunRecord,
  synced_state: GuardedLiveVenueOrderResult | None,
  open_order: GuardedLiveVenueOpenOrder | None,
) -> Order:
  symbol = run.config.symbols[0]
  restored_at = synced_state.submitted_at if synced_state is not None else app._clock()
  explicit_price = None
  if synced_state is not None:
    explicit_price = synced_state.requested_price
  if explicit_price is None and open_order is not None:
    explicit_price = open_order.price
  quantity = (
    (synced_state.requested_amount if synced_state is not None else None)
    or (synced_state.amount if synced_state is not None and synced_state.amount > 0 else None)
    or (open_order.amount if open_order is not None else None)
    or 0.0
  )
  restored_order = Order(
    run_id=run.config.run_id,
    instrument_id=f"{run.config.venue}:{symbol}",
    side=app._resolve_order_side(
      synced_state.side if synced_state is not None else open_order.side if open_order is not None else "buy"
    ),
    quantity=quantity,
    requested_price=(
      explicit_price
      if explicit_price is not None
      else (
        synced_state.average_fill_price
        if synced_state is not None and synced_state.average_fill_price is not None
        else 0.0
      )
    ),
    order_type=OrderType.LIMIT if explicit_price is not None else OrderType.MARKET,
    status=(
      map_guarded_live_order_status(
        open_order.status,
        filled_quantity=0.0,
        remaining_quantity=quantity,
      )
      if open_order is not None
      else OrderStatus.OPEN
    ),
    order_id=synced_state.order_id if synced_state is not None else open_order.order_id,
    created_at=restored_at,
    updated_at=synced_state.updated_at if synced_state is not None else restored_at,
    last_synced_at=synced_state.updated_at if synced_state is not None else restored_at,
    remaining_quantity=quantity,
  )
  run.orders.append(restored_order)
  return restored_order


def materialize_guarded_live_fill_delta(
  app: Any,
  *,
  run: RunRecord,
  order: Order,
  fill_quantity: float,
  fee_paid: float,
  fill_price: float,
  fill_timestamp: datetime,
) -> None:
  cache = app._restore_state_cache(run)
  active_position = cache.position if cache.position is not None and cache.position.is_open else None
  if order.side == OrderSide.BUY:
    gross_cost = fill_quantity * fill_price
    next_cash = cache.cash - gross_cost - fee_paid
    if active_position is None:
      next_position = Position(
        instrument_id=order.instrument_id,
        quantity=fill_quantity,
        average_price=fill_price,
        opened_at=fill_timestamp,
        updated_at=fill_timestamp,
      )
    else:
      total_quantity = active_position.quantity + fill_quantity
      average_price = (
        (active_position.quantity * active_position.average_price) + (fill_quantity * fill_price)
      ) / total_quantity
      next_position = replace(
        active_position,
        quantity=total_quantity,
        average_price=average_price,
        updated_at=fill_timestamp,
      )
    cache.apply(cash=next_cash, position=next_position)
    run.positions[order.instrument_id] = next_position
  else:
    if active_position is None or not active_position.is_open:
      raise RuntimeError(f"guarded_live_sell_sync_without_position:{order.order_id}")
    sell_quantity = min(fill_quantity, active_position.quantity)
    gross_value = sell_quantity * fill_price
    proceeds = gross_value - fee_paid
    pnl = proceeds - (sell_quantity * active_position.average_price)
    remaining_quantity = max(active_position.quantity - sell_quantity, 0.0)
    next_position = replace(
      active_position,
      quantity=remaining_quantity,
      updated_at=fill_timestamp,
      realized_pnl=active_position.realized_pnl + pnl,
    )
    cache.apply(
      cash=cache.cash + proceeds,
      position=next_position if next_position.is_open else None,
    )
    run.positions[order.instrument_id] = next_position
    run.closed_trades.append(
      ClosedTrade(
        instrument_id=order.instrument_id,
        entry_price=active_position.average_price,
        exit_price=fill_price,
        quantity=sell_quantity,
        fee_paid=fee_paid,
        pnl=pnl,
        opened_at=active_position.opened_at or fill_timestamp,
        closed_at=fill_timestamp,
      )
    )

  run.fills.append(
    Fill(
      order_id=order.order_id,
      quantity=fill_quantity,
      price=fill_price,
      fee_paid=fee_paid,
      timestamp=fill_timestamp,
    )
  )
  run.equity_curve.append(
    build_equity_point(
      timestamp=fill_timestamp,
      cash=cache.cash,
      position=cache.position if cache.position and cache.position.is_open else None,
      market_price=fill_price,
    )
  )


def apply_guarded_live_synced_order_state(
  app: Any,
  *,
  run: RunRecord,
  order: Order,
  synced_state: GuardedLiveVenueOrderResult,
) -> int:
  status_changed = False
  fill_recorded = False
  previous_status = order.status
  previous_filled_quantity = order.filled_quantity
  sync_time = synced_state.updated_at or synced_state.submitted_at or app._clock()
  order.last_synced_at = sync_time
  order.updated_at = sync_time
  if synced_state.average_fill_price is not None:
    order.average_fill_price = synced_state.average_fill_price

  total_fee = synced_state.fee_paid if synced_state.fee_paid is not None else order.fee_paid
  total_filled = synced_state.filled_amount
  if total_filled is None:
    if synced_state.status == OrderStatus.FILLED.value:
      total_filled = order.quantity
    elif synced_state.status == OrderStatus.PARTIALLY_FILLED.value:
      total_filled = order.filled_quantity
    else:
      total_filled = order.filled_quantity
  remaining_quantity = synced_state.remaining_amount
  if remaining_quantity is None:
    remaining_quantity = max(order.quantity - total_filled, 0.0)

  incremental_fill = max(total_filled - order.filled_quantity, 0.0)
  if incremental_fill > app._guarded_live_balance_tolerance:
    incremental_fee = max(total_fee - order.fee_paid, 0.0)
    materialize_guarded_live_fill_delta(
      app,
      run=run,
      order=order,
      fill_quantity=incremental_fill,
      fee_paid=incremental_fee,
      fill_price=synced_state.average_fill_price or order.average_fill_price or order.requested_price,
      fill_timestamp=sync_time,
    )
    fill_recorded = True

  order.fee_paid = total_fee
  order.filled_quantity = total_filled
  order.remaining_quantity = remaining_quantity
  mapped_status = map_guarded_live_order_status(
    synced_state.status,
    filled_quantity=total_filled,
    remaining_quantity=remaining_quantity,
  )
  if mapped_status != order.status:
    order.status = mapped_status
    status_changed = True
  if order.status == OrderStatus.FILLED and order.filled_at is None:
    order.filled_at = sync_time

  if status_changed or fill_recorded or synced_state.issues:
    transition_copy = (
      f"{previous_status.value}->{order.status.value}"
      if status_changed
      else f"{order.status.value}"
    )
    detail = (
      f"Order {order.order_id} synced as {transition_copy}. "
      f"filled {previous_filled_quantity:.8f}->{order.filled_quantity:.8f}, "
      f"remaining {order.remaining_quantity or 0.0:.8f}."
    )
    if synced_state.issues:
      detail += " Issues: " + ", ".join(synced_state.issues) + "."
    run.notes.append(f"{sync_time.isoformat()} | guarded_live_order_synced | {detail}")
    app._append_guarded_live_audit_event(
      kind="guarded_live_order_synced",
      actor="system",
      summary=f"Guarded-live order synced for {run.config.symbols[0]}.",
      detail=detail,
      run_id=run.config.run_id,
      session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
    )
    return 1
  return 0


def apply_guarded_live_restored_session(
  app: Any,
  *,
  run: RunRecord,
  session_restore: GuardedLiveVenueSessionRestore,
) -> int:
  existing_orders = {order.order_id: order for order in run.orders}
  open_orders_by_id = {
    order.order_id: order
    for order in session_restore.open_orders
  }
  state_changes = 0
  for synced_state in session_restore.synced_orders:
    if synced_state.status == "unknown":
      continue
    order = existing_orders.get(synced_state.order_id)
    if order is None:
      order = materialize_guarded_live_restored_order(
        app,
        run=run,
        synced_state=synced_state,
        open_order=open_orders_by_id.get(synced_state.order_id),
      )
      existing_orders[order.order_id] = order
      state_changes += 1
    state_changes += apply_guarded_live_synced_order_state(
      app,
      run=run,
      order=order,
      synced_state=synced_state,
    )

  for open_order in session_restore.open_orders:
    if open_order.order_id in existing_orders:
      continue
    order = materialize_guarded_live_restored_order(
      app,
      run=run,
      synced_state=None,
      open_order=open_order,
    )
    existing_orders[order.order_id] = order
    state_changes += 1

  if state_changes > 0:
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
  return state_changes


def sync_guarded_live_orders(
  app: Any,
  run: RunRecord,
) -> int:
  tracked_orders = [
    order
    for order in run.orders
    if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}
  ]
  if not tracked_orders:
    return 0

  synced_states = {
    state.order_id: state
    for state in app._venue_execution.sync_order_states(
      symbol=run.config.symbols[0],
      order_ids=tuple(order.order_id for order in tracked_orders),
    )
  }
  synced_count = 0
  for order in tracked_orders:
    synced_state = synced_states.get(order.order_id)
    if synced_state is None:
      continue
    synced_count += apply_guarded_live_synced_order_state(
      app,
      run=run,
      order=order,
      synced_state=synced_state,
    )
  if synced_count > 0:
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
  return synced_count


def sync_guarded_live_session(
  app: Any,
  *,
  run: RunRecord,
  handoff: GuardedLiveVenueSessionHandoff,
) -> dict[str, object]:
  session_sync = app._venue_execution.sync_session(
    handoff=handoff,
    order_ids=tuple(order.order_id for order in run.orders),
  )
  restore_view = GuardedLiveVenueSessionRestore(
    state="restored" if session_sync.state == "active" else session_sync.state,
    restored_at=session_sync.synced_at,
    source=session_sync.handoff.source,
    venue=session_sync.handoff.venue,
    symbol=session_sync.handoff.symbol,
    owner_run_id=session_sync.handoff.owner_run_id,
    owner_session_id=session_sync.handoff.owner_session_id,
    open_orders=session_sync.open_orders,
    synced_orders=session_sync.synced_orders,
    issues=session_sync.issues,
  )
  synced_count = apply_guarded_live_restored_session(
    app,
    run=run,
    session_restore=restore_view,
  )
  next_handoff = session_sync.handoff
  if synced_count > 0 or session_sync.issues or next_handoff.last_event_at != handoff.last_event_at:
    sync_time = session_sync.synced_at or app._clock()
    detail = (
      f"source={next_handoff.source}; transport={next_handoff.transport}; "
      f"state={next_handoff.state}; active_orders={next_handoff.active_order_count}; "
      f"cursor={next_handoff.cursor or 'n/a'}; supervision={next_handoff.supervision_state}; "
      f"order_book={next_handoff.order_book_state}; failovers={next_handoff.failover_count}; "
      f"coverage={','.join(next_handoff.coverage) or 'none'}; "
      f"continuation={next_handoff.channel_continuation_state}"
    )
    if (
      next_handoff.order_book_best_bid_price is not None
      or next_handoff.order_book_best_ask_price is not None
    ):
      detail += (
        f"; top_of_book={next_handoff.order_book_best_bid_price or 0.0:.8f}/"
        f"{next_handoff.order_book_best_ask_price or 0.0:.8f}"
      )
    if next_handoff.order_book_last_update_id is not None:
      detail += f"; depth_update_id={next_handoff.order_book_last_update_id}"
    if next_handoff.order_book_gap_count > 0:
      detail += f"; depth_gaps={next_handoff.order_book_gap_count}"
    if next_handoff.order_book_rebuild_count > 0:
      detail += f"; depth_rebuilds={next_handoff.order_book_rebuild_count}"
    if next_handoff.order_book_last_rebuilt_at is not None:
      detail += f"; last_depth_rebuild={next_handoff.order_book_last_rebuilt_at.isoformat()}"
    if session_sync.issues:
      detail += f"; issues={', '.join(session_sync.issues)}"
    run.notes.append(
      f"{sync_time.isoformat()} | guarded_live_venue_session_synced | {detail}"
    )
    app._append_guarded_live_audit_event(
      kind="guarded_live_venue_session_synced",
      actor="system",
      summary=f"Guarded-live venue session synced for {run.config.symbols[0]}.",
      detail=detail,
      run_id=run.config.run_id,
      session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
    )
  return {
    "synced": synced_count,
    "handoff": next_handoff,
  }


def submit_guarded_live_market_order(
  app: Any,
  *,
  run: RunRecord,
  order: Order,
  market_price: float,
) -> GuardedLiveVenueOrderResult:
  session = run.provenance.runtime_session
  if session is None:
    raise RuntimeError("guarded_live_runtime_session_missing")
  request = GuardedLiveVenueOrderRequest(
    run_id=run.config.run_id,
    session_id=session.session_id,
    venue=run.config.venue,
    symbol=run.config.symbols[0],
    side=order.side.value,
    amount=order.quantity,
    order_type=OrderType.MARKET.value,
    reference_price=market_price,
  )
  return app._venue_execution.submit_market_order(request)


def submit_guarded_live_limit_order(
  app: Any,
  *,
  run: RunRecord,
  order: Order,
  limit_price: float,
) -> GuardedLiveVenueOrderResult:
  session = run.provenance.runtime_session
  if session is None:
    raise RuntimeError("guarded_live_runtime_session_missing")
  request = GuardedLiveVenueOrderRequest(
    run_id=run.config.run_id,
    session_id=session.session_id,
    venue=run.config.venue,
    symbol=run.config.symbols[0],
    side=order.side.value,
    amount=order.quantity,
    order_type=OrderType.LIMIT.value,
    reference_price=limit_price,
  )
  return app._venue_execution.submit_limit_order(request)


def apply_guarded_live_decision(
  app: Any,
  *,
  run: RunRecord,
  decision: Any,
  cache: Any,
  market_price: float,
) -> int:
  reviewed = app._execution_engine.review_decision(decision)
  _, _, order, _, _ = apply_signal(
    run_id=run.config.run_id,
    instrument_id=cache.instrument_id,
    signal=reviewed.signal,
    execution=reviewed.execution,
    market_price=market_price,
    position=cache.position,
    cash=cache.cash,
    fee_rate=run.config.fee_rate,
    slippage_bps=run.config.slippage_bps,
  )

  submitted_orders = 0
  effective_price = market_price
  fill_materialized = False
  if order is not None:
    venue_result = submit_guarded_live_market_order(
      app,
      run=run,
      order=order,
      market_price=market_price,
    )
    order.order_id = venue_result.order_id
    order.created_at = venue_result.submitted_at
    order.updated_at = venue_result.updated_at or venue_result.submitted_at
    order.last_synced_at = venue_result.updated_at or venue_result.submitted_at
    order.status = map_guarded_live_order_status(
      venue_result.status,
      filled_quantity=venue_result.filled_amount or 0.0,
      remaining_quantity=venue_result.remaining_amount or 0.0,
    )
    if venue_result.average_fill_price is not None:
      order.average_fill_price = venue_result.average_fill_price
      effective_price = venue_result.average_fill_price
    order.fee_paid = venue_result.fee_paid or 0.0
    order.filled_quantity = venue_result.filled_amount or 0.0
    order.remaining_quantity = (
      venue_result.remaining_amount
      if venue_result.remaining_amount is not None
      else max(order.quantity - order.filled_quantity, 0.0)
    )
    if order.status == OrderStatus.FILLED:
      order.filled_at = venue_result.updated_at or venue_result.submitted_at
    run.orders.append(order)
    submitted_orders = 1
    if order.filled_quantity > app._guarded_live_balance_tolerance:
      materialize_guarded_live_fill_delta(
        app,
        run=run,
        order=order,
        fill_quantity=order.filled_quantity,
        fee_paid=order.fee_paid,
        fill_price=effective_price,
        fill_timestamp=order.filled_at or venue_result.submitted_at,
      )
      fill_materialized = True
    app._append_guarded_live_audit_event(
      kind="guarded_live_order_submitted",
      actor="system",
      summary=f"Guarded-live venue order submitted for {run.config.symbols[0]}.",
      detail=(
        f"{reviewed.signal.action.value} {order.quantity:.8f} {run.config.symbols[0]} "
        f"via {venue_result.order_id} ({order.status.value})."
      ),
      run_id=run.config.run_id,
      session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
    )

  cache = app._restore_state_cache(run)
  cache.mark_price(effective_price)
  if not fill_materialized:
    run.equity_curve.append(
      build_equity_point(
        timestamp=reviewed.signal.timestamp,
        cash=cache.cash,
        position=cache.position if cache.position and cache.position.is_open else None,
        market_price=effective_price,
      )
    )
  run.notes.append(
    f"{reviewed.context.timestamp.isoformat()} | {reviewed.signal.action.value} | {reviewed.rationale}"
  )
  return submitted_orders


def advance_guarded_live_worker_run(
  app: Any,
  run: RunRecord,
) -> dict[str, int]:
  session = run.provenance.runtime_session
  if session is None:
    return {"ticks_processed": 0, "orders_submitted": 0}

  strategy = app._strategies.load(run.config.strategy_id)
  parameters = app._resolve_execution_parameters(run)
  candles = app._load_sandbox_worker_candles(run=run)
  if not candles:
    return {"ticks_processed": 0, "orders_submitted": 0}

  latest_seen_candle_at = candles[-1].timestamp
  app._run_supervisor.record_worker_market_progress(
    run=run,
    last_seen_candle_at=latest_seen_candle_at,
  )
  if (
    session.last_processed_candle_at is not None
    and latest_seen_candle_at <= session.last_processed_candle_at
  ):
    return {"ticks_processed": 0, "orders_submitted": 0}

  enriched = strategy.build_feature_frame(candles_to_frame(candles), parameters)
  warmup = strategy.warmup_spec().required_bars
  if len(enriched) < max(warmup, 2):
    return {"ticks_processed": 0, "orders_submitted": 0}

  cache = app._restore_state_cache(run)
  latest_processed_candle_at = session.last_processed_candle_at
  processed_ticks = 0
  orders_submitted = 0
  for index in range(max(warmup, 2), len(enriched)):
    history = enriched.iloc[: index + 1]
    latest_row = history.iloc[-1]
    latest_timestamp = latest_row["timestamp"].to_pydatetime()
    if latest_processed_candle_at is not None and latest_timestamp <= latest_processed_candle_at:
      continue
    state = cache.snapshot(
      timestamp=latest_timestamp,
      parameters=parameters,
    )
    decision = strategy.evaluate(history, parameters, state)
    orders_submitted += apply_guarded_live_decision(
      app,
      run=run,
      decision=decision,
      cache=cache,
      market_price=float(latest_row["close"]),
    )
    processed_ticks += 1
    latest_processed_candle_at = latest_timestamp

  if processed_ticks == 0:
    return {"ticks_processed": 0, "orders_submitted": 0}

  app._run_supervisor.record_worker_market_progress(
    run=run,
    last_seen_candle_at=latest_seen_candle_at,
    last_processed_candle_at=latest_processed_candle_at,
    processed_tick_count_increment=processed_ticks,
  )
  run.metrics = summarize_performance(
    initial_cash=run.config.initial_cash,
    equity_curve=run.equity_curve,
    closed_trades=run.closed_trades,
  )
  return {"ticks_processed": processed_ticks, "orders_submitted": orders_submitted}
