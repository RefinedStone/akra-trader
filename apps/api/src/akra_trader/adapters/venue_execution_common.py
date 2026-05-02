from __future__ import annotations

import base64
from dataclasses import dataclass
import json
from queue import Empty
from queue import Queue
import threading
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import Protocol
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from uuid import uuid4

import ccxt

from akra_trader.domain.models import GuardedLiveBookTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveKlineChannelSnapshot
from akra_trader.domain.models import GuardedLiveMiniTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveOrderBookLevel
from akra_trader.domain.models import GuardedLiveTradeChannelSnapshot
from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueSessionHandoff
from akra_trader.domain.models import GuardedLiveVenueSessionRestore
from akra_trader.domain.models import GuardedLiveVenueSessionSync
from akra_trader.ports import VenueExecutionPort


class BinanceVenueStreamSession(Protocol):
  session_id: str
  transport: str

  def drain_events(self) -> tuple[dict[str, Any], ...]: ...

  def close(self) -> None: ...


class BinanceVenueStreamClient(Protocol):
  def open_session(self) -> BinanceVenueStreamSession: ...


@dataclass
class LocalOrderBookState:
  symbol: str
  last_update_id: int | None
  rebuilt_at: datetime
  rebuild_count: int
  bids: dict[float, float]
  asks: dict[float, float]

  @property
  def bid_level_count(self) -> int:
    return len(self.bids)

  @property
  def ask_level_count(self) -> int:
    return len(self.asks)

  @property
  def best_bid(self) -> tuple[float | None, float | None]:
    if not self.bids:
      return None, None
    price = max(self.bids)
    return price, self.bids[price]

  @property
  def best_ask(self) -> tuple[float | None, float | None]:
    if not self.asks:
      return None, None
    price = min(self.asks)
    return price, self.asks[price]


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

  def fetch_order_book(
    self,
    symbol: str,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
  ) -> dict[str, Any]: ...

  def fetch_ticker(self, symbol: str, params: dict[str, Any] | None = None) -> dict[str, Any]: ...

  def fetch_trades(
    self,
    symbol: str,
    since: int | None = None,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
  ) -> list[dict[str, Any]]: ...

  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "1m",
    since: int | None = None,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
  ) -> list[list[Any]]: ...

  def fetch_closed_orders(
    self,
    symbol: str | None = None,
    since: int | None = None,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
  ) -> list[dict[str, Any]]: ...


def build_trade_exchange(
  *,
  venue: str = "binance",
  api_key: str | None = None,
  api_secret: str | None = None,
) -> VenueExecutionExchange:
  options: dict[str, Any] = {"enableRateLimit": True}
  if api_key:
    options["apiKey"] = api_key
  if api_secret:
    options["secret"] = api_secret
  exchange_factory = getattr(ccxt, venue, None)
  if not callable(exchange_factory):
    raise ValueError(f"Unsupported trade venue: {venue}")
  return exchange_factory(options)


def build_binance_trade_exchange(
  *,
  api_key: str | None = None,
  api_secret: str | None = None,
) -> VenueExecutionExchange:
  return build_trade_exchange(
    venue="binance",
    api_key=api_key,
    api_secret=api_secret,
  )


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


def _normalize_binance_stream_symbol(symbol: str) -> str:
  return symbol.replace("/", "").replace("-", "").lower()


def _normalize_coinbase_product_id(symbol: str) -> str:
  return symbol.replace("/", "-").upper()


def _sanitize_coinbase_zero_time(value: Any) -> Any:
  if isinstance(value, str) and value.startswith("0001-01-01T00:00:00"):
    return None
  return value


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


def _coerce_int(value: Any) -> int | None:
  if isinstance(value, bool):
    return None
  if isinstance(value, int):
    return value
  try:
    return int(str(value))
  except (TypeError, ValueError):
    return None


def _coerce_string(value: Any) -> str | None:
  if value is None:
    return None
  text = str(value)
  return text if text else None


def _base64url_encode_json(value: dict[str, Any]) -> bytes:
  payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
  return base64.urlsafe_b64encode(payload).rstrip(b"=")


def _base64url_encode_bytes(value: bytes) -> str:
  return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _build_coinbase_websocket_jwt(
  *,
  api_key: str,
  signing_key: str,
  current_time: datetime,
) -> str:
  from cryptography.hazmat.primitives import hashes
  from cryptography.hazmat.primitives import serialization
  from cryptography.hazmat.primitives.asymmetric import ec
  from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

  issued_at = int(current_time.timestamp())
  header = {
    "alg": "ES256",
    "kid": api_key,
    "nonce": uuid4().hex,
    "typ": "JWT",
  }
  payload = {
    "iss": "cdp",
    "nbf": issued_at,
    "exp": issued_at + 120,
    "sub": api_key,
  }
  signing_input = b".".join((_base64url_encode_json(header), _base64url_encode_json(payload)))
  private_key = serialization.load_pem_private_key(signing_key.encode(), password=None)
  if not isinstance(private_key, ec.EllipticCurvePrivateKey):
    raise RuntimeError("coinbase_websocket_signing_key_invalid")
  der_signature = private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
  r, s = decode_dss_signature(der_signature)
  raw_signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
  return f"{signing_input.decode()}.{_base64url_encode_bytes(raw_signature)}"


def _coerce_first_depth_level(value: Any) -> tuple[float | None, float | None]:
  if not isinstance(value, list) or not value:
    return None, None
  first_level = value[0]
  if not isinstance(first_level, (list, tuple)) or len(first_level) < 2:
    return None, None
  return _coerce_float(first_level[0]), _coerce_float(first_level[1])


def _coerce_depth_levels(value: Any) -> tuple[tuple[float, float], ...]:
  if not isinstance(value, list):
    return ()
  levels: list[tuple[float, float]] = []
  for item in value:
    if not isinstance(item, (list, tuple)) or len(item) < 2:
      continue
    price = _coerce_float(item[0])
    quantity = _coerce_float(item[1])
    if price is None or quantity is None:
      continue
    levels.append((price, quantity))
  return tuple(levels)


def _coerce_named_depth_levels(value: Any) -> tuple[tuple[float, float], ...]:
  if not isinstance(value, list):
    return ()
  levels: list[tuple[float, float]] = []
  for item in value:
    if not isinstance(item, dict):
      continue
    price = _coerce_float(item.get("price"))
    quantity = _coerce_float(item.get("qty"))
    if price is None or quantity is None:
      continue
    levels.append((price, quantity))
  return tuple(levels)


def _drain_stream_event_queue(
  queue: Queue[dict[str, Any]],
  *,
  first_event_timeout_seconds: float = 0.01,
) -> tuple[dict[str, Any], ...]:
  events: list[dict[str, Any]] = []
  try:
    events.append(queue.get(timeout=first_event_timeout_seconds))
  except Empty:
    return ()
  while True:
    try:
      events.append(queue.get_nowait())
    except Empty:
      break
  return tuple(events)


def _depth_event_matches_local_book(
  *,
  book: LocalOrderBookState | None,
  first_update_id: int | None,
  last_update_id: int | None,
  previous_update_id: int | None,
) -> bool:
  if book is None or book.last_update_id is None:
    return False
  if last_update_id is not None and last_update_id <= book.last_update_id:
    return True
  if previous_update_id is not None:
    return previous_update_id == book.last_update_id
  if first_update_id is None or last_update_id is None:
    return False
  return first_update_id <= (book.last_update_id + 1) <= last_update_id


def _build_local_order_book_from_snapshot_row(
  *,
  symbol: str,
  row: dict[str, Any],
  rebuilt_at: datetime,
  rebuild_count: int,
) -> LocalOrderBookState:
  bids = {price: quantity for price, quantity in _coerce_depth_levels(row.get("bids")) if quantity > 0}
  asks = {price: quantity for price, quantity in _coerce_depth_levels(row.get("asks")) if quantity > 0}
  last_update_id = (
    _coerce_int(_extract_nested_value(row, ("info", "lastUpdateId")))
    or _coerce_int(row.get("nonce"))
    or _coerce_int(row.get("lastUpdateId"))
  )
  return LocalOrderBookState(
    symbol=symbol,
    last_update_id=last_update_id,
    rebuilt_at=rebuilt_at,
    rebuild_count=rebuild_count,
    bids=bids,
    asks=asks,
  )


def _build_trade_snapshot_from_exchange_trade_row(
  row: dict[str, Any],
  *,
  fallback_event_at: datetime,
) -> GuardedLiveTradeChannelSnapshot:
  return GuardedLiveTradeChannelSnapshot(
    event_id=_coerce_string(row.get("id")),
    price=_coerce_float(row.get("price")),
    quantity=_coerce_float(row.get("amount")),
    event_at=_coerce_datetime(row.get("datetime"), row.get("timestamp")) or fallback_event_at,
  )


def _build_book_ticker_snapshot_from_ticker_row(
  row: dict[str, Any],
  *,
  fallback_event_at: datetime,
) -> GuardedLiveBookTickerChannelSnapshot:
  return GuardedLiveBookTickerChannelSnapshot(
    bid_price=_coerce_float(row.get("bid")),
    bid_quantity=_coerce_float(row.get("bidVolume")),
    ask_price=_coerce_float(row.get("ask")),
    ask_quantity=_coerce_float(row.get("askVolume")),
    event_at=_coerce_datetime(row.get("datetime"), row.get("timestamp")) or fallback_event_at,
  )


def _build_mini_ticker_snapshot_from_ticker_row(
  row: dict[str, Any],
  *,
  fallback_event_at: datetime,
) -> GuardedLiveMiniTickerChannelSnapshot:
  return GuardedLiveMiniTickerChannelSnapshot(
    open_price=_coerce_float(row.get("open")),
    close_price=_coerce_float(row.get("last")) or _coerce_float(row.get("close")),
    high_price=_coerce_float(row.get("high")),
    low_price=_coerce_float(row.get("low")),
    base_volume=_coerce_float(row.get("baseVolume")),
    quote_volume=_coerce_float(row.get("quoteVolume")),
    event_at=_coerce_datetime(row.get("datetime"), row.get("timestamp")) or fallback_event_at,
  )


def _build_kline_snapshot_from_stream_event(
  *,
  event: dict[str, Any],
  timeframe: str,
  fallback_event_at: datetime,
) -> GuardedLiveKlineChannelSnapshot:
  kline_row = _extract_nested_value(event, ("k",))
  if not isinstance(kline_row, dict):
    return GuardedLiveKlineChannelSnapshot(timeframe=timeframe, event_at=fallback_event_at)
  return GuardedLiveKlineChannelSnapshot(
    timeframe=_coerce_string(kline_row.get("i")) or timeframe,
    open_at=_coerce_datetime(None, kline_row.get("t")),
    close_at=_coerce_datetime(None, kline_row.get("T")),
    open_price=_coerce_float(kline_row.get("o")),
    high_price=_coerce_float(kline_row.get("h")),
    low_price=_coerce_float(kline_row.get("l")),
    close_price=_coerce_float(kline_row.get("c")),
    volume=_coerce_float(kline_row.get("v")),
    closed=bool(kline_row.get("x")),
    event_at=_coerce_datetime(None, event.get("E")) or fallback_event_at,
  )


def _build_kline_snapshot_from_ohlcv_row(
  row: list[Any],
  *,
  timeframe: str,
  fallback_event_at: datetime,
) -> GuardedLiveKlineChannelSnapshot:
  open_at = _coerce_ohlcv_timestamp(row[0] if row else None, timeframe=timeframe)
  close_at = _coerce_ohlcv_close_timestamp(row[0] if row else None, timeframe=timeframe)
  return GuardedLiveKlineChannelSnapshot(
    timeframe=timeframe,
    open_at=open_at,
    close_at=close_at,
    open_price=_coerce_float(row[1] if len(row) > 1 else None),
    high_price=_coerce_float(row[2] if len(row) > 2 else None),
    low_price=_coerce_float(row[3] if len(row) > 3 else None),
    close_price=_coerce_float(row[4] if len(row) > 4 else None),
    volume=_coerce_float(row[5] if len(row) > 5 else None),
    closed=True,
    event_at=close_at or open_at or fallback_event_at,
  )


def _serialize_order_book_side(
  levels: dict[float, float],
  *,
  reverse: bool,
) -> tuple[GuardedLiveOrderBookLevel, ...]:
  return tuple(
    GuardedLiveOrderBookLevel(price=price, quantity=levels[price])
    for price in sorted(levels, reverse=reverse)
  )


def _max_datetime(first: datetime | None, second: datetime | None) -> datetime | None:
  if first is None:
    return second
  if second is None:
    return first
  return max(first, second)


def _coerce_ohlcv_timestamp(value: Any, *, timeframe: str) -> datetime | None:
  timestamp = _coerce_datetime(None, value)
  if timestamp is not None:
    return timestamp
  if not isinstance(value, str):
    return None
  try:
    if len(value) == 10:
      return datetime.fromisoformat(f"{value}T00:00:00+00:00")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
  except ValueError:
    return None


def _coerce_ohlcv_close_timestamp(value: Any, *, timeframe: str) -> datetime | None:
  opened_at = _coerce_ohlcv_timestamp(value, timeframe=timeframe)
  if opened_at is None:
    return None
  delta = _timeframe_to_timedelta(timeframe)
  if delta is None:
    return opened_at
  return opened_at + delta


def _timeframe_to_timedelta(timeframe: str) -> timedelta | None:
  if not timeframe:
    return None
  unit = timeframe[-1]
  amount = _coerce_int(timeframe[:-1])
  if amount is None or amount <= 0:
    return None
  if unit == "m":
    return timedelta(minutes=amount)
  if unit == "h":
    return timedelta(hours=amount)
  if unit == "d":
    return timedelta(days=amount)
  if unit == "w":
    return timedelta(weeks=amount)
  return None


def _timeframe_to_minutes(timeframe: str) -> int | None:
  delta = _timeframe_to_timedelta(timeframe)
  if delta is None:
    return None
  total_minutes = int(delta.total_seconds() // 60)
  supported_minutes = {1, 5, 15, 30, 60, 240, 1440, 10080, 21600}
  if total_minutes not in supported_minutes:
    return None
  return total_minutes


def _minutes_to_timeframe(minutes: int | None) -> str | None:
  if minutes is None or minutes <= 0:
    return None
  if minutes % 10080 == 0:
    weeks = minutes // 10080
    return f"{weeks}w"
  if minutes % 1440 == 0:
    days = minutes // 1440
    return f"{days}d"
  if minutes % 60 == 0:
    hours = minutes // 60
    return f"{hours}h"
  return f"{minutes}m"
