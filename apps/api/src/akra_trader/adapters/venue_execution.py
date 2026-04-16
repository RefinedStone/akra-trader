from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Protocol

import ccxt

from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
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
  ) -> None:
    self._venue = venue
    self._clock = clock or (lambda: datetime.now(UTC))
    self.submitted_orders: list[GuardedLiveVenueOrderResult] = []

  def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
    return True, ()

  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    submitted_at = self._clock()
    result = GuardedLiveVenueOrderResult(
      order_id=f"seeded-live-order-{len(self.submitted_orders) + 1}",
      venue=self._venue,
      symbol=request.symbol,
      side=request.side,
      amount=request.amount,
      status="filled",
      submitted_at=submitted_at,
      average_fill_price=request.reference_price,
      fee_paid=0.0,
    )
    self.submitted_orders.append(result)
    return result


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

  def submit_market_order(
    self,
    request: GuardedLiveVenueOrderRequest,
  ) -> GuardedLiveVenueOrderResult:
    exchange = self._exchange
    if exchange is None:
      ready, issues = self.describe_capability()
      if not ready:
        raise RuntimeError(", ".join(issues))
      exchange = build_binance_trade_exchange(
        api_key=self._api_key,
        api_secret=self._api_secret,
      )

    row = exchange.create_order(
      request.symbol,
      "market",
      request.side,
      request.amount,
      None,
      {},
    )
    submitted_at = self._clock()
    order_id = str(row.get("id") or row.get("clientOrderId") or f"live-order:{submitted_at.isoformat()}")
    amount = _coerce_float(row.get("filled"))
    if amount is None or amount <= 0:
      amount = _coerce_float(row.get("amount")) or request.amount
    average_fill_price = (
      _coerce_float(row.get("average"))
      or _coerce_float(row.get("price"))
      or request.reference_price
    )
    fee_paid = _extract_fee(row)
    status = _normalize_order_status(row, requested_amount=request.amount, filled_amount=amount)
    return GuardedLiveVenueOrderResult(
      order_id=order_id,
      venue=self._venue,
      symbol=str(row.get("symbol") or request.symbol),
      side=str(row.get("side") or request.side),
      amount=amount,
      status=status,
      submitted_at=submitted_at,
      average_fill_price=average_fill_price,
      fee_paid=fee_paid,
    )


def _normalize_order_status(
  row: dict[str, Any],
  *,
  requested_amount: float,
  filled_amount: float,
) -> str:
  raw_status = str(row.get("status") or "").lower()
  if raw_status in {"closed", "filled"}:
    return "filled"
  if raw_status in {"canceled", "cancelled", "rejected", "expired"}:
    return raw_status
  if filled_amount >= requested_amount and requested_amount > 0:
    return "filled"
  return raw_status or "unknown"


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


def _coerce_float(value: Any) -> float | None:
  if isinstance(value, (int, float)):
    return float(value)
  try:
    return float(value)
  except (TypeError, ValueError):
    return None
