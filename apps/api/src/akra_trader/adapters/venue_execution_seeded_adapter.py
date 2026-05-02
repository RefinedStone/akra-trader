from __future__ import annotations

from akra_trader.adapters.venue_execution_common import *

class SeededVenueExecutionAdapter(VenueExecutionPort):
  def __init__(
    self,
    *,
    venue: str = "binance",
    clock: Callable[[], datetime] | None = None,
    restored_orders: tuple[GuardedLiveVenueOrderResult, ...] = (),
  ) -> None:
    self._venue = venue
    self._clock = clock or (lambda: datetime.now(UTC))
    self.submitted_orders: list[GuardedLiveVenueOrderResult] = list(restored_orders)
    self._order_states: dict[str, GuardedLiveVenueOrderResult] = {
      order.order_id: order
      for order in restored_orders
    }
    self._active_handoffs: dict[str, GuardedLiveVenueSessionHandoff] = {}

  def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
    return True, ()

  def restore_session(
    self,
    *,
    symbol: str,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionRestore:
    current_time = self._clock()
    symbol_states = {
      order_id: state
      for order_id, state in self._order_states.items()
      if state.symbol == symbol
    }
    synced_orders: list[GuardedLiveVenueOrderResult] = []
    issues: list[str] = []
    found_owned_state = False
    for order_id in owned_order_ids:
      state = symbol_states.get(order_id)
      if state is None:
        synced_orders.append(
          GuardedLiveVenueOrderResult(
            order_id=order_id,
            venue=self._venue,
            symbol=symbol,
            side="unknown",
            amount=0.0,
            status="unknown",
            submitted_at=current_time,
            updated_at=current_time,
            issues=("restored_order_state_missing",),
          )
        )
        issues.append(f"restored_order_state_missing:{order_id}")
        continue
      synced_orders.append(state)
      found_owned_state = True

    open_orders = tuple(
      sorted(
        (
          GuardedLiveVenueOpenOrder(
            order_id=state.order_id,
            symbol=state.symbol,
            side=state.side,
            amount=state.remaining_amount if state.remaining_amount is not None else state.amount,
            status=state.status,
            price=state.requested_price or state.average_fill_price,
          )
          for state in symbol_states.values()
          if state.status in {"open", "partially_filled"}
          and (state.remaining_amount is None or state.remaining_amount > 0)
        ),
        key=lambda order: (order.symbol, order.order_id),
      )
    )
    state = "not_found"
    if found_owned_state or open_orders:
      state = "restored" if not issues else "partial"
    elif issues:
      state = "unavailable"
    return GuardedLiveVenueSessionRestore(
      state=state,
      restored_at=current_time,
      source="seeded_venue_execution",
      venue=self._venue,
      symbol=symbol,
      open_orders=open_orders,
      synced_orders=tuple(synced_orders),
      issues=tuple(issues),
    )

  def handoff_session(
    self,
    *,
    symbol: str,
    timeframe: str,
    owner_run_id: str,
    owner_session_id: str | None,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionHandoff:
    current_time = self._clock()
    session_key = owner_session_id or f"seeded-session-{len(self._active_handoffs) + 1}"
    handoff = GuardedLiveVenueSessionHandoff(
      state="active",
      handed_off_at=current_time,
      source="seeded_venue_execution",
      venue=self._venue,
      symbol=symbol,
      timeframe=timeframe,
      owner_run_id=owner_run_id,
      owner_session_id=owner_session_id,
      venue_session_id=session_key,
      transport="seeded_stream",
      cursor="event-0",
      last_event_at=self._resolve_last_event_at(symbol=symbol),
      last_sync_at=current_time,
      supervision_state="streaming",
      order_book_state="synthetic",
      channel_restore_state="synthetic",
      channel_continuation_state="synthetic",
      channel_continuation_count=1,
      channel_last_continued_at=current_time,
      coverage=("execution_reports",),
      active_order_count=self._count_active_orders(symbol=symbol),
      issues=(),
    )
    self._active_handoffs[session_key] = handoff
    return handoff

  def sync_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionSync:
    current_time = self._clock()
    session_key = handoff.venue_session_id or handoff.owner_session_id or ""
    existing = self._active_handoffs.get(session_key, handoff)
    synced_orders = self.sync_order_states(
      symbol=existing.symbol or handoff.symbol or "",
      order_ids=order_ids,
    )
    open_orders = self._build_open_orders(symbol=existing.symbol or handoff.symbol or "")
    next_cursor = self._increment_cursor(existing.cursor)
    next_handoff = GuardedLiveVenueSessionHandoff(
      state="active",
      handed_off_at=existing.handed_off_at or handoff.handed_off_at or current_time,
      released_at=None,
      source=existing.source or handoff.source or "seeded_venue_execution",
      venue=existing.venue or handoff.venue or self._venue,
      symbol=existing.symbol or handoff.symbol,
      timeframe=existing.timeframe or handoff.timeframe,
      owner_run_id=existing.owner_run_id or handoff.owner_run_id,
      owner_session_id=existing.owner_session_id or handoff.owner_session_id,
      venue_session_id=session_key or None,
      transport=existing.transport or handoff.transport or "seeded_stream",
      cursor=next_cursor,
      last_event_at=self._resolve_last_event_at(symbol=existing.symbol or handoff.symbol or ""),
      last_sync_at=current_time,
      supervision_state="streaming",
      order_book_state=existing.order_book_state or handoff.order_book_state or "synthetic",
      order_book_last_update_id=existing.order_book_last_update_id or handoff.order_book_last_update_id,
      order_book_gap_count=existing.order_book_gap_count or handoff.order_book_gap_count,
      order_book_rebuild_count=existing.order_book_rebuild_count or handoff.order_book_rebuild_count,
      order_book_last_rebuilt_at=existing.order_book_last_rebuilt_at or handoff.order_book_last_rebuilt_at,
      order_book_bid_level_count=existing.order_book_bid_level_count or handoff.order_book_bid_level_count,
      order_book_ask_level_count=existing.order_book_ask_level_count or handoff.order_book_ask_level_count,
      order_book_best_bid_price=existing.order_book_best_bid_price or handoff.order_book_best_bid_price,
      order_book_best_bid_quantity=existing.order_book_best_bid_quantity or handoff.order_book_best_bid_quantity,
      order_book_best_ask_price=existing.order_book_best_ask_price or handoff.order_book_best_ask_price,
      order_book_best_ask_quantity=existing.order_book_best_ask_quantity or handoff.order_book_best_ask_quantity,
      order_book_bids=existing.order_book_bids or handoff.order_book_bids,
      order_book_asks=existing.order_book_asks or handoff.order_book_asks,
      channel_restore_state=existing.channel_restore_state or handoff.channel_restore_state or "synthetic",
      channel_restore_count=existing.channel_restore_count or handoff.channel_restore_count,
      channel_last_restored_at=existing.channel_last_restored_at or handoff.channel_last_restored_at,
      channel_continuation_state=(
        existing.channel_continuation_state or handoff.channel_continuation_state or "synthetic"
      ),
      channel_continuation_count=existing.channel_continuation_count or handoff.channel_continuation_count,
      channel_last_continued_at=existing.channel_last_continued_at or handoff.channel_last_continued_at,
      trade_snapshot=existing.trade_snapshot or handoff.trade_snapshot,
      aggregate_trade_snapshot=existing.aggregate_trade_snapshot or handoff.aggregate_trade_snapshot,
      book_ticker_snapshot=existing.book_ticker_snapshot or handoff.book_ticker_snapshot,
      mini_ticker_snapshot=existing.mini_ticker_snapshot or handoff.mini_ticker_snapshot,
      kline_snapshot=existing.kline_snapshot or handoff.kline_snapshot,
      failover_count=existing.failover_count or handoff.failover_count,
      last_failover_at=existing.last_failover_at or handoff.last_failover_at,
      coverage=existing.coverage or handoff.coverage or ("execution_reports",),
      last_market_event_at=existing.last_market_event_at or handoff.last_market_event_at,
      last_depth_event_at=existing.last_depth_event_at or handoff.last_depth_event_at,
      last_kline_event_at=existing.last_kline_event_at or handoff.last_kline_event_at,
      last_aggregate_trade_event_at=(
        existing.last_aggregate_trade_event_at or handoff.last_aggregate_trade_event_at
      ),
      last_mini_ticker_event_at=existing.last_mini_ticker_event_at or handoff.last_mini_ticker_event_at,
      last_account_event_at=existing.last_account_event_at or handoff.last_account_event_at,
      last_balance_event_at=existing.last_balance_event_at or handoff.last_balance_event_at,
      last_order_list_event_at=existing.last_order_list_event_at or handoff.last_order_list_event_at,
      last_trade_event_at=existing.last_trade_event_at or handoff.last_trade_event_at,
      last_book_ticker_event_at=existing.last_book_ticker_event_at or handoff.last_book_ticker_event_at,
      active_order_count=len(open_orders),
      issues=(),
    )
    if session_key:
      self._active_handoffs[session_key] = next_handoff
    return GuardedLiveVenueSessionSync(
      state="active",
      synced_at=current_time,
      handoff=next_handoff,
      synced_orders=synced_orders,
      open_orders=open_orders,
      issues=(),
    )

  def release_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveVenueSessionHandoff:
    current_time = self._clock()
    session_key = handoff.venue_session_id or handoff.owner_session_id or ""
    released = GuardedLiveVenueSessionHandoff(
      state="released",
      handed_off_at=handoff.handed_off_at,
      released_at=current_time,
      source=handoff.source or "seeded_venue_execution",
      venue=handoff.venue or self._venue,
      symbol=handoff.symbol,
      timeframe=handoff.timeframe,
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      venue_session_id=handoff.venue_session_id,
      transport=handoff.transport or "seeded_stream",
      cursor=handoff.cursor,
      last_event_at=handoff.last_event_at,
      last_sync_at=current_time,
      supervision_state="released",
      order_book_state="released",
      order_book_last_update_id=handoff.order_book_last_update_id,
      order_book_gap_count=handoff.order_book_gap_count,
      order_book_rebuild_count=handoff.order_book_rebuild_count,
      order_book_last_rebuilt_at=handoff.order_book_last_rebuilt_at,
      order_book_bid_level_count=handoff.order_book_bid_level_count,
      order_book_ask_level_count=handoff.order_book_ask_level_count,
      order_book_best_bid_price=handoff.order_book_best_bid_price,
      order_book_best_bid_quantity=handoff.order_book_best_bid_quantity,
      order_book_best_ask_price=handoff.order_book_best_ask_price,
      order_book_best_ask_quantity=handoff.order_book_best_ask_quantity,
      order_book_bids=handoff.order_book_bids,
      order_book_asks=handoff.order_book_asks,
      channel_restore_state=handoff.channel_restore_state,
      channel_restore_count=handoff.channel_restore_count,
      channel_last_restored_at=handoff.channel_last_restored_at,
      channel_continuation_state="released",
      channel_continuation_count=handoff.channel_continuation_count,
      channel_last_continued_at=handoff.channel_last_continued_at,
      trade_snapshot=handoff.trade_snapshot,
      aggregate_trade_snapshot=handoff.aggregate_trade_snapshot,
      book_ticker_snapshot=handoff.book_ticker_snapshot,
      mini_ticker_snapshot=handoff.mini_ticker_snapshot,
      kline_snapshot=handoff.kline_snapshot,
      failover_count=handoff.failover_count,
      last_failover_at=handoff.last_failover_at,
      coverage=handoff.coverage,
      last_market_event_at=handoff.last_market_event_at,
      last_depth_event_at=handoff.last_depth_event_at,
      last_kline_event_at=handoff.last_kline_event_at,
      last_aggregate_trade_event_at=handoff.last_aggregate_trade_event_at,
      last_mini_ticker_event_at=handoff.last_mini_ticker_event_at,
      last_account_event_at=handoff.last_account_event_at,
      last_balance_event_at=handoff.last_balance_event_at,
      last_order_list_event_at=handoff.last_order_list_event_at,
      last_trade_event_at=handoff.last_trade_event_at,
      last_book_ticker_event_at=handoff.last_book_ticker_event_at,
      active_order_count=0,
      issues=handoff.issues,
    )
    if session_key:
      self._active_handoffs[session_key] = released
    return released

  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    result = self._build_submitted_order_result(
      request=request,
      status="filled",
      average_fill_price=request.reference_price,
      filled_amount=request.amount,
      remaining_amount=0.0,
    )
    self.submitted_orders.append(result)
    self._order_states[result.order_id] = result
    return result

  def submit_limit_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    result = self._build_submitted_order_result(
      request=request,
      status="open",
      average_fill_price=None,
      filled_amount=0.0,
      remaining_amount=request.amount,
    )
    self.submitted_orders.append(result)
    self._order_states[result.order_id] = result
    return result

  def cancel_order(
    self,
    *,
    symbol: str,
    order_id: str,
  ) -> GuardedLiveVenueOrderResult:
    current = self._order_states.get(order_id)
    if current is None:
      raise RuntimeError(f"seeded_order_not_found:{order_id}")
    canceled_at = self._clock()
    filled_amount = current.filled_amount or 0.0
    requested_amount = current.requested_amount or current.amount
    canceled = GuardedLiveVenueOrderResult(
      order_id=current.order_id,
      venue=current.venue,
      symbol=symbol or current.symbol,
      side=current.side,
      amount=current.amount,
      status="canceled",
      submitted_at=current.submitted_at,
      updated_at=canceled_at,
      requested_price=current.requested_price,
      average_fill_price=current.average_fill_price,
      fee_paid=current.fee_paid,
      requested_amount=requested_amount,
      filled_amount=filled_amount,
      remaining_amount=max(requested_amount - filled_amount, 0.0),
      issues=current.issues,
    )
    self._order_states[order_id] = canceled
    return canceled

  def sync_order_states(
    self,
    *,
    symbol: str,
    order_ids: tuple[str, ...],
  ) -> tuple[GuardedLiveVenueOrderResult, ...]:
    now = self._clock()
    results: list[GuardedLiveVenueOrderResult] = []
    for order_id in order_ids:
      state = self._order_states.get(order_id)
      if state is None:
        results.append(
          GuardedLiveVenueOrderResult(
            order_id=order_id,
            venue=self._venue,
            symbol=symbol,
            side="unknown",
            amount=0.0,
            status="unknown",
            submitted_at=now,
            updated_at=now,
            issues=("seeded_order_state_missing",),
          )
        )
        continue
      results.append(state)
    return tuple(results)

  def set_order_state(
    self,
    order_id: str,
    *,
    symbol: str | None = None,
    side: str | None = None,
    amount: float | None = None,
    requested_price: float | None = None,
    status: str,
    updated_at: datetime | None = None,
    average_fill_price: float | None = None,
    fee_paid: float | None = None,
    filled_amount: float | None = None,
    remaining_amount: float | None = None,
    issues: tuple[str, ...] = (),
  ) -> GuardedLiveVenueOrderResult:
    current = self._order_states.get(order_id)
    if current is None:
      now = updated_at or self._clock()
      if symbol is None or side is None or amount is None:
        raise KeyError(order_id)
      current = GuardedLiveVenueOrderResult(
        order_id=order_id,
        venue=self._venue,
        symbol=symbol,
        side=side,
        amount=amount,
        status="open",
        submitted_at=now,
        updated_at=now,
        requested_price=requested_price,
        requested_amount=amount,
        filled_amount=0.0,
        remaining_amount=amount,
      )
    next_state = GuardedLiveVenueOrderResult(
      order_id=order_id,
      venue=current.venue,
      symbol=symbol or current.symbol,
      side=side or current.side,
      amount=amount if amount is not None else current.amount,
      status=status,
      submitted_at=current.submitted_at,
      updated_at=updated_at or self._clock(),
      requested_price=requested_price if requested_price is not None else current.requested_price,
      average_fill_price=average_fill_price if average_fill_price is not None else current.average_fill_price,
      fee_paid=fee_paid if fee_paid is not None else current.fee_paid,
      requested_amount=current.requested_amount,
      filled_amount=filled_amount if filled_amount is not None else current.filled_amount,
      remaining_amount=remaining_amount if remaining_amount is not None else current.remaining_amount,
      issues=issues,
    )
    self._order_states[order_id] = next_state
    return next_state

  def _build_submitted_order_result(
    self,
    *,
    request: GuardedLiveVenueOrderRequest,
    status: str,
    average_fill_price: float | None,
    filled_amount: float,
    remaining_amount: float,
  ) -> GuardedLiveVenueOrderResult:
    submitted_at = self._clock()
    return GuardedLiveVenueOrderResult(
      order_id=f"seeded-live-order-{len(self.submitted_orders) + 1}",
      venue=self._venue,
      symbol=request.symbol,
      side=request.side,
      amount=request.amount,
      status=status,
      submitted_at=submitted_at,
      updated_at=submitted_at,
      requested_price=request.reference_price,
      average_fill_price=average_fill_price,
      fee_paid=0.0,
      requested_amount=request.amount,
      filled_amount=filled_amount,
      remaining_amount=remaining_amount,
    )

  def _build_open_orders(
    self,
    *,
    symbol: str,
  ) -> tuple[GuardedLiveVenueOpenOrder, ...]:
    return tuple(
      sorted(
        (
          GuardedLiveVenueOpenOrder(
            order_id=state.order_id,
            symbol=state.symbol,
            side=state.side,
            amount=state.remaining_amount if state.remaining_amount is not None else state.amount,
            status=state.status,
            price=state.requested_price or state.average_fill_price,
          )
          for state in self._order_states.values()
          if state.symbol == symbol
          and state.status in {"open", "partially_filled"}
          and (state.remaining_amount is None or state.remaining_amount > 0)
        ),
        key=lambda order: (order.symbol, order.order_id),
      )
    )

  def _count_active_orders(
    self,
    *,
    symbol: str,
  ) -> int:
    return len(self._build_open_orders(symbol=symbol))

  def _resolve_last_event_at(
    self,
    *,
    symbol: str,
  ) -> datetime | None:
    matching_times = [
      state.updated_at or state.submitted_at
      for state in self._order_states.values()
      if state.symbol == symbol
    ]
    if not matching_times:
      return None
    return max(matching_times)

  @staticmethod
  def _increment_cursor(cursor: str | None) -> str:
    if cursor is None or not cursor.startswith("event-"):
      return "event-1"
    try:
      value = int(cursor.split("-", 1)[1])
    except (IndexError, ValueError):
      return "event-1"
    return f"event-{value + 1}"
