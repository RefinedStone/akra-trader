from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Protocol

import ccxt

from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.ports import VenueStatePort


class VenueStateExchange(Protocol):
  def fetch_balance(self) -> dict[str, Any]: ...

  def fetch_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]: ...


def build_binance_account_exchange(
  *,
  api_key: str | None = None,
  api_secret: str | None = None,
) -> VenueStateExchange:
  options: dict[str, Any] = {"enableRateLimit": True}
  if api_key:
    options["apiKey"] = api_key
  if api_secret:
    options["secret"] = api_secret
  return ccxt.binance(options)


class SeededVenueStateAdapter(VenueStatePort):
  def __init__(
    self,
    *,
    venue: str = "binance",
    clock: Callable[[], datetime] | None = None,
    balances: tuple[GuardedLiveVenueBalance, ...] | None = None,
    open_orders: tuple[GuardedLiveVenueOpenOrder, ...] = (),
  ) -> None:
    self._venue = venue
    self._clock = clock or (lambda: datetime.now(UTC))
    self._balances = balances or (
      GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),
    )
    self._open_orders = open_orders

  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
    return GuardedLiveVenueStateSnapshot(
      provider="seeded",
      venue=self._venue,
      verification_state="verified",
      captured_at=self._clock(),
      balances=self._balances,
      open_orders=self._open_orders,
    )


class BinanceVenueStateAdapter(VenueStatePort):
  def __init__(
    self,
    *,
    tracked_symbols: tuple[str, ...],
    venue: str = "binance",
    api_key: str | None = None,
    api_secret: str | None = None,
    exchange: VenueStateExchange | None = None,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._tracked_symbols = tracked_symbols
    self._venue = venue
    self._api_key = api_key
    self._api_secret = api_secret
    self._exchange = exchange
    self._clock = clock or (lambda: datetime.now(UTC))

  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
    current_time = self._clock()
    exchange = self._exchange
    if exchange is None and not (self._api_key and self._api_secret):
      return GuardedLiveVenueStateSnapshot(
        provider="binance",
        venue=self._venue,
        verification_state="unavailable",
        captured_at=current_time,
        issues=("binance_api_credentials_missing",),
      )
    if exchange is None:
      exchange = build_binance_account_exchange(
        api_key=self._api_key,
        api_secret=self._api_secret,
      )

    balances: tuple[GuardedLiveVenueBalance, ...] = ()
    open_orders: tuple[GuardedLiveVenueOpenOrder, ...] = ()
    issues: list[str] = []

    try:
      balances = self._extract_balances(exchange.fetch_balance())
    except Exception as exc:
      issues.append(f"balance_fetch_failed:{exc}")

    try:
      open_orders = self._extract_open_orders(exchange=exchange)
    except Exception as exc:
      issues.append(f"open_orders_fetch_failed:{exc}")

    verification_state = "verified"
    if issues:
      verification_state = "partial" if balances or open_orders else "unavailable"

    return GuardedLiveVenueStateSnapshot(
      provider="binance",
      venue=self._venue,
      verification_state=verification_state,
      captured_at=current_time,
      balances=balances,
      open_orders=open_orders,
      issues=tuple(issues),
    )

  def _extract_balances(self, payload: dict[str, Any]) -> tuple[GuardedLiveVenueBalance, ...]:
    total_map = payload.get("total")
    free_map = payload.get("free")
    used_map = payload.get("used")
    if not isinstance(total_map, dict):
      return ()

    balances: list[GuardedLiveVenueBalance] = []
    for asset, total in sorted(total_map.items()):
      total_value = _coerce_float(total)
      free_value = _coerce_float(free_map.get(asset)) if isinstance(free_map, dict) else None
      used_value = _coerce_float(used_map.get(asset)) if isinstance(used_map, dict) else None
      if total_value is None:
        continue
      if abs(total_value) <= 1e-12 and abs(free_value or 0.0) <= 1e-12 and abs(used_value or 0.0) <= 1e-12:
        continue
      balances.append(
        GuardedLiveVenueBalance(
          asset=asset,
          total=total_value,
          free=free_value,
          used=used_value,
        )
      )
    return tuple(balances)

  def _extract_open_orders(
    self,
    *,
    exchange: VenueStateExchange,
  ) -> tuple[GuardedLiveVenueOpenOrder, ...]:
    try:
      rows = exchange.fetch_open_orders()
    except TypeError:
      rows = []
      for symbol in self._tracked_symbols:
        rows.extend(exchange.fetch_open_orders(symbol))
    except ccxt.NotSupported:
      rows = []
      for symbol in self._tracked_symbols:
        rows.extend(exchange.fetch_open_orders(symbol))

    open_orders: dict[str, GuardedLiveVenueOpenOrder] = {}
    for row in rows:
      order_id = str(row.get("id") or row.get("clientOrderId") or f"unknown:{len(open_orders)}")
      symbol = str(row.get("symbol") or "unknown")
      side = str(row.get("side") or "unknown")
      status = str(row.get("status") or "open")
      amount = _coerce_float(row.get("amount")) or 0.0
      price = _coerce_float(row.get("price"))
      open_orders[order_id] = GuardedLiveVenueOpenOrder(
        order_id=order_id,
        symbol=symbol,
        side=side,
        amount=amount,
        status=status,
        price=price,
      )
    return tuple(sorted(open_orders.values(), key=lambda order: (order.symbol, order.order_id)))


def _coerce_float(value: Any) -> float | None:
  if isinstance(value, (int, float)):
    return float(value)
  try:
    return float(value)
  except (TypeError, ValueError):
    return None
