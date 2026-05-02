from __future__ import annotations

from akra_trader.adapters.venue_execution_common import *

class BinanceVenueExecutionOrderMixin:
  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    exchange = self._resolve_exchange()
    row = exchange.create_order(request.symbol, "market", request.side, request.amount, None, {})
    result = _build_order_result_from_exchange_row(
      row,
      venue=self._venue,
      fallback_symbol=request.symbol,
      fallback_side=request.side,
      fallback_amount=request.amount,
      fallback_reference_price=request.reference_price,
      fallback_time=self._clock(),
    )
    self._order_states[result.order_id] = result
    return result

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
    result = _build_order_result_from_exchange_row(
      row,
      venue=self._venue,
      fallback_symbol=request.symbol,
      fallback_side=request.side,
      fallback_amount=request.amount,
      fallback_reference_price=request.reference_price,
      fallback_time=self._clock(),
    )
    self._order_states[result.order_id] = result
    return result

  def cancel_order(
    self,
    *,
    symbol: str,
    order_id: str,
  ) -> GuardedLiveVenueOrderResult:
    exchange = self._resolve_exchange()
    row = exchange.cancel_order(order_id, symbol, {})
    result = _build_order_result_from_exchange_row(
      row,
      venue=self._venue,
      fallback_symbol=symbol,
      fallback_time=self._clock(),
    )
    self._order_states[result.order_id] = result
    return result

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
      exchange = build_trade_exchange(
        venue=self._venue,
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
        if cached := self._order_states.get(order_id):
          results.append(cached)
          continue
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
    for result in results:
      if result.status != "unknown":
        self._order_states[result.order_id] = result
    return tuple(results)
