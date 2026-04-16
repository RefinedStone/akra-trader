from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Protocol

import ccxt

from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueSessionHandoff
from akra_trader.domain.models import GuardedLiveVenueSessionRestore
from akra_trader.domain.models import GuardedLiveVenueSessionSync
from akra_trader.ports import VenueExecutionPort


class VenueExecutionExchange(Protocol):
  def create_order(
    self,
    symbol: str,
    type: str,
    side: str,
    amount: float,
    price: float | None = None,
    params: dict[str, Any] | None = None,
  ) -> dict[str, Any]: ...

  def fetch_orders(
    self,
    symbol: str | None = None,
    since: int | None = None,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
  ) -> list[dict[str, Any]]: ...

  def cancel_order(
    self,
    id: str,
    symbol: str | None = None,
    params: dict[str, Any] | None = None,
  ) -> dict[str, Any]: ...

  def fetch_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]: ...

  def fetch_closed_orders(
    self,
    symbol: str | None = None,
    since: int | None = None,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
  ) -> list[dict[str, Any]]: ...


def build_binance_trade_exchange(
  *,
  api_key: str | None = None,
  api_secret: str | None = None,
) -> VenueExecutionExchange:
  options: dict[str, Any] = {"enableRateLimit": True}
  if api_key:
    options["apiKey"] = api_key
  if api_secret:
    options["secret"] = api_secret
  return ccxt.binance(options)


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
      owner_run_id=owner_run_id,
      owner_session_id=owner_session_id,
      venue_session_id=session_key,
      transport="seeded_stream",
      cursor="event-0",
      last_event_at=self._resolve_last_event_at(symbol=symbol),
      last_sync_at=current_time,
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
      owner_run_id=existing.owner_run_id or handoff.owner_run_id,
      owner_session_id=existing.owner_session_id or handoff.owner_session_id,
      venue_session_id=session_key or None,
      transport=existing.transport or handoff.transport or "seeded_stream",
      cursor=next_cursor,
      last_event_at=self._resolve_last_event_at(symbol=existing.symbol or handoff.symbol or ""),
      last_sync_at=current_time,
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
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      venue_session_id=handoff.venue_session_id,
      transport=handoff.transport or "seeded_stream",
      cursor=handoff.cursor,
      last_event_at=handoff.last_event_at,
      last_sync_at=current_time,
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


class BinanceVenueExecutionAdapter(VenueExecutionPort):
  def __init__(
    self,
    *,
    venue: str = "binance",
    api_key: str | None = None,
    api_secret: str | None = None,
    exchange: VenueExecutionExchange | None = None,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._venue = venue
    self._api_key = api_key
    self._api_secret = api_secret
    self._exchange = exchange
    self._clock = clock or (lambda: datetime.now(UTC))

  def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
    if self._exchange is not None:
      return True, ()
    if self._api_key and self._api_secret:
      return True, ()
    return False, ("binance_trade_credentials_missing",)

  def restore_session(
    self,
    *,
    symbol: str,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionRestore:
    current_time = self._clock()
    try:
      exchange = self._resolve_exchange()
      rows = self._fetch_order_rows(exchange=exchange, symbol=symbol)
    except Exception as exc:
      return GuardedLiveVenueSessionRestore(
        state="unavailable",
        restored_at=current_time,
        source="binance_exchange",
        venue=self._venue,
        symbol=symbol,
        issues=(f"venue_session_restore_failed:{exc}",),
      )

    rows_by_id: dict[str, GuardedLiveVenueOrderResult] = {}
    for row in rows:
      result = _build_order_result_from_exchange_row(
        row,
        venue=self._venue,
        fallback_symbol=symbol,
        fallback_time=current_time,
      )
      rows_by_id[result.order_id] = result

    synced_orders: list[GuardedLiveVenueOrderResult] = []
    issues: list[str] = []
    found_owned_state = False
    for order_id in owned_order_ids:
      result = rows_by_id.get(order_id)
      if result is None:
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
      synced_orders.append(result)
      found_owned_state = True

    open_orders = tuple(
      sorted(
        (
          GuardedLiveVenueOpenOrder(
            order_id=result.order_id,
            symbol=result.symbol,
            side=result.side,
            amount=result.remaining_amount if result.remaining_amount is not None else result.amount,
            status=result.status,
            price=result.requested_price or result.average_fill_price,
          )
          for result in rows_by_id.values()
          if result.status in {"open", "partially_filled"}
          and (result.remaining_amount is None or result.remaining_amount > 0)
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
      source="binance_exchange",
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
    owner_run_id: str,
    owner_session_id: str | None,
    owned_order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionHandoff:
    current_time = self._clock()
    restore = self.restore_session(symbol=symbol, owned_order_ids=owned_order_ids)
    handoff_state = "active" if restore.state in {"restored", "partial", "not_found"} else "unavailable"
    return GuardedLiveVenueSessionHandoff(
      state=handoff_state,
      handed_off_at=current_time,
      source="binance_exchange",
      venue=self._venue,
      symbol=symbol,
      owner_run_id=owner_run_id,
      owner_session_id=owner_session_id,
      venue_session_id=f"binance-session:{symbol}:{int(current_time.timestamp())}",
      transport="binance_rest_session",
      cursor=current_time.isoformat(),
      last_event_at=restore.restored_at,
      last_sync_at=current_time,
      active_order_count=len(restore.open_orders),
      issues=restore.issues,
    )

  def sync_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionSync:
    current_time = self._clock()
    symbol = handoff.symbol or ""
    restore = self.restore_session(symbol=symbol, owned_order_ids=order_ids)
    synced_orders = restore.synced_orders
    open_orders = restore.open_orders
    active_order_count = len(open_orders)
    handoff_state = "active" if handoff.state != "released" else "released"
    last_event_at = restore.restored_at or handoff.last_event_at
    next_handoff = GuardedLiveVenueSessionHandoff(
      state=handoff_state,
      handed_off_at=handoff.handed_off_at,
      released_at=handoff.released_at,
      source=handoff.source or "binance_exchange",
      venue=handoff.venue or self._venue,
      symbol=symbol or handoff.symbol,
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      venue_session_id=handoff.venue_session_id,
      transport=handoff.transport or "binance_rest_session",
      cursor=current_time.isoformat(),
      last_event_at=last_event_at,
      last_sync_at=current_time,
      active_order_count=active_order_count,
      issues=restore.issues,
    )
    return GuardedLiveVenueSessionSync(
      state=handoff_state,
      synced_at=current_time,
      handoff=next_handoff,
      synced_orders=synced_orders,
      open_orders=open_orders,
      issues=restore.issues,
    )

  def release_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveVenueSessionHandoff:
    current_time = self._clock()
    return GuardedLiveVenueSessionHandoff(
      state="released",
      handed_off_at=handoff.handed_off_at,
      released_at=current_time,
      source=handoff.source or "binance_exchange",
      venue=handoff.venue or self._venue,
      symbol=handoff.symbol,
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      venue_session_id=handoff.venue_session_id,
      transport=handoff.transport or "binance_rest_session",
      cursor=current_time.isoformat(),
      last_event_at=handoff.last_event_at,
      last_sync_at=current_time,
      active_order_count=0,
      issues=handoff.issues,
    )

  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    exchange = self._resolve_exchange()
    row = exchange.create_order(request.symbol, "market", request.side, request.amount, None, {})
    return _build_order_result_from_exchange_row(
      row,
      venue=self._venue,
      fallback_symbol=request.symbol,
      fallback_side=request.side,
      fallback_amount=request.amount,
      fallback_reference_price=request.reference_price,
      fallback_time=self._clock(),
    )

  def submit_limit_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    if request.reference_price is None or request.reference_price <= 0:
      raise ValueError("Guarded-live limit replacement requires a positive reference price.")
    exchange = self._resolve_exchange()
    row = exchange.create_order(
      request.symbol,
      "limit",
      request.side,
      request.amount,
      request.reference_price,
      {},
    )
    return _build_order_result_from_exchange_row(
      row,
      venue=self._venue,
      fallback_symbol=request.symbol,
      fallback_side=request.side,
      fallback_amount=request.amount,
      fallback_reference_price=request.reference_price,
      fallback_time=self._clock(),
    )

  def cancel_order(
    self,
    *,
    symbol: str,
    order_id: str,
  ) -> GuardedLiveVenueOrderResult:
    exchange = self._resolve_exchange()
    row = exchange.cancel_order(order_id, symbol, {})
    return _build_order_result_from_exchange_row(
      row,
      venue=self._venue,
      fallback_symbol=symbol,
      fallback_time=self._clock(),
    )

  def sync_order_states(
    self,
    *,
    symbol: str,
    order_ids: tuple[str, ...],
  ) -> tuple[GuardedLiveVenueOrderResult, ...]:
    if not order_ids:
      return ()

    exchange = self._exchange
    if exchange is None:
      ready, issues = self.describe_capability()
      if not ready:
        raise RuntimeError(", ".join(issues))
      exchange = build_binance_trade_exchange(
        api_key=self._api_key,
        api_secret=self._api_secret,
      )

    rows_by_id: dict[str, dict[str, Any]] = {}
    current_time = self._clock()
    for row in self._fetch_order_rows(exchange=exchange, symbol=symbol):
      order_id = str(row.get("id") or row.get("clientOrderId") or "")
      if not order_id or order_id not in order_ids:
        continue
      rows_by_id[order_id] = row

    results: list[GuardedLiveVenueOrderResult] = []
    for order_id in order_ids:
      row = rows_by_id.get(order_id)
      if row is None:
        results.append(
          GuardedLiveVenueOrderResult(
            order_id=order_id,
            venue=self._venue,
            symbol=symbol,
            side="unknown",
            amount=0.0,
            status="unknown",
            submitted_at=current_time,
            updated_at=current_time,
            issues=("order_state_unavailable",),
          )
        )
        continue
      results.append(
        _build_order_result_from_exchange_row(
          row,
          venue=self._venue,
          fallback_symbol=symbol,
          fallback_time=current_time,
        )
      )
    return tuple(results)

  def _resolve_exchange(self) -> VenueExecutionExchange:
    exchange = self._exchange
    if exchange is not None:
      return exchange
    ready, issues = self.describe_capability()
    if not ready:
      raise RuntimeError(", ".join(issues))
    return build_binance_trade_exchange(
      api_key=self._api_key,
      api_secret=self._api_secret,
    )

  def _fetch_order_rows(
    self,
    *,
    exchange: VenueExecutionExchange,
    symbol: str,
  ) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
      rows.extend(exchange.fetch_orders(symbol, None, None, {}))
      return rows
    except (AttributeError, TypeError, ccxt.NotSupported):
      pass

    for fetcher_name in ("fetch_open_orders", "fetch_closed_orders"):
      fetcher = getattr(exchange, fetcher_name, None)
      if fetcher is None:
        continue
      try:
        if fetcher_name == "fetch_open_orders":
          rows.extend(fetcher(symbol))
        else:
          rows.extend(fetcher(symbol, None, None, {}))
      except (AttributeError, TypeError, ccxt.NotSupported):
        continue
    return rows


def _normalize_order_status(
  *,
  raw_status: str,
  requested_amount: float,
  filled_amount: float,
  remaining_amount: float | None,
) -> str:
  if raw_status in {"closed", "filled"}:
    return "filled"
  if raw_status in {"canceled", "cancelled", "rejected", "expired"}:
    return raw_status
  if remaining_amount is not None and remaining_amount > 0 and filled_amount > 0:
    return "partially_filled"
  if filled_amount >= requested_amount and requested_amount > 0:
    return "filled"
  if filled_amount > 0:
    return "partially_filled"
  if raw_status in {"open", "new"}:
    return "open"
  return raw_status or "unknown"


def _build_order_result_from_exchange_row(
  row: dict[str, Any],
  *,
  venue: str,
  fallback_symbol: str,
  fallback_side: str | None = None,
  fallback_amount: float | None = None,
  fallback_reference_price: float | None = None,
  fallback_time: datetime,
) -> GuardedLiveVenueOrderResult:
  submitted_at = _coerce_datetime(row.get("datetime"), row.get("timestamp")) or fallback_time
  updated_at = (
    _coerce_datetime(None, row.get("lastTradeTimestamp"))
    or _coerce_datetime(None, _extract_nested_value(row, ("info", "updateTime")))
    or submitted_at
  )
  requested_amount = _coerce_float(row.get("amount")) or fallback_amount or 0.0
  filled_amount = _coerce_float(row.get("filled"))
  if filled_amount is None:
    filled_amount = requested_amount if str(row.get("status") or "").lower() in {"filled", "closed"} else 0.0
  remaining_amount = _coerce_float(row.get("remaining"))
  if remaining_amount is None:
    remaining_amount = max(requested_amount - filled_amount, 0.0)
  status = _normalize_order_status(
    raw_status=str(row.get("status") or "").lower(),
    requested_amount=requested_amount,
    filled_amount=filled_amount,
    remaining_amount=remaining_amount,
  )
  average_fill_price = _coerce_float(row.get("average"))
  if average_fill_price is None and status in {"filled", "partially_filled"}:
    average_fill_price = _coerce_float(row.get("price")) or fallback_reference_price
  fee_paid = _extract_fee(row)
  return GuardedLiveVenueOrderResult(
    order_id=str(row.get("id") or row.get("clientOrderId") or f"live-order:{submitted_at.isoformat()}"),
    venue=venue,
    symbol=str(row.get("symbol") or fallback_symbol),
    side=str(row.get("side") or fallback_side or "unknown"),
    amount=filled_amount if status == "filled" else requested_amount,
    status=status,
    submitted_at=submitted_at,
    updated_at=updated_at,
    requested_price=_coerce_float(row.get("price")) or fallback_reference_price,
    average_fill_price=average_fill_price,
    fee_paid=fee_paid,
    requested_amount=requested_amount,
    filled_amount=filled_amount,
    remaining_amount=remaining_amount,
  )


def _extract_fee(row: dict[str, Any]) -> float | None:
  fee = row.get("fee")
  if isinstance(fee, dict):
    fee_cost = _coerce_float(fee.get("cost"))
    if fee_cost is not None:
      return fee_cost
  fees = row.get("fees")
  if isinstance(fees, list):
    total_fee = 0.0
    found_fee = False
    for item in fees:
      if not isinstance(item, dict):
        continue
      fee_cost = _coerce_float(item.get("cost"))
      if fee_cost is None:
        continue
      total_fee += fee_cost
      found_fee = True
    if found_fee:
      return total_fee
  return None


def _extract_nested_value(row: dict[str, Any], path: tuple[str, ...]) -> Any:
  current: Any = row
  for key in path:
    if not isinstance(current, dict):
      return None
    current = current.get(key)
  return current


def _coerce_datetime(
  iso_value: Any,
  timestamp_value: Any,
) -> datetime | None:
  if isinstance(iso_value, str):
    try:
      return datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
    except ValueError:
      pass
  timestamp = _coerce_float(timestamp_value)
  if timestamp is None:
    return None
  if timestamp > 1_000_000_000_000:
    timestamp /= 1000
  return datetime.fromtimestamp(timestamp, UTC)


def _coerce_float(value: Any) -> float | None:
  if isinstance(value, (int, float)):
    return float(value)
  try:
    return float(value)
  except (TypeError, ValueError):
    return None
