from __future__ import annotations

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


class BinanceWebSocketUserDataStreamSession:
  transport = "binance_user_data_websocket"

  def __init__(
    self,
    *,
    session_id: str,
    websocket_url: str,
    rest_base_url: str,
    api_key: str,
    clock: Callable[[], datetime],
  ) -> None:
    self.session_id = session_id
    self._websocket_url = websocket_url.rstrip("/")
    self._rest_base_url = rest_base_url.rstrip("/")
    self._api_key = api_key
    self._clock = clock
    self._events: Queue[dict[str, Any]] = Queue()
    self._closed = False
    self._reader_stop = threading.Event()
    self._last_keepalive_at = clock()
    self._connect = self._resolve_connect()
    self._connection = self._connect(f"{self._websocket_url}/{self.session_id}")
    self._reader = threading.Thread(target=self._reader_loop, name=f"binance-user-stream-{session_id}", daemon=True)
    self._reader.start()

  def drain_events(self) -> tuple[dict[str, Any], ...]:
    if self._closed:
      return ()
    self._maybe_keepalive()
    events: list[dict[str, Any]] = []
    while True:
      try:
        events.append(self._events.get_nowait())
      except Empty:
        break
    return tuple(events)

  def close(self) -> None:
    if self._closed:
      return
    self._closed = True
    self._reader_stop.set()
    try:
      self._connection.close()
    except Exception:
      pass
    if self._reader.is_alive():
      self._reader.join(timeout=1.0)
    try:
      self._request_listen_key("DELETE")
    except Exception:
      pass

  def _reader_loop(self) -> None:
    while not self._reader_stop.is_set():
      try:
        message = self._connection.recv()
      except Exception as exc:
        if self._reader_stop.is_set():
          return
        self._events.put(
          {
            "e": "streamDisconnect",
            "message": str(exc),
            "E": int(self._clock().timestamp() * 1000),
          }
        )
        return
      if message is None:
        if self._reader_stop.is_set():
          return
        self._events.put(
          {
            "e": "streamDisconnect",
            "message": "connection_closed",
            "E": int(self._clock().timestamp() * 1000),
          }
        )
        return
      try:
        payload = json.loads(message)
      except json.JSONDecodeError as exc:
        self._events.put(
          {
            "e": "streamWarning",
            "message": f"invalid_json:{exc}",
            "E": int(self._clock().timestamp() * 1000),
          }
        )
        continue
      payload.setdefault("_received_at_ms", int(self._clock().timestamp() * 1000))
      self._events.put(payload)

  def _maybe_keepalive(self) -> None:
    now = self._clock()
    if (now - self._last_keepalive_at).total_seconds() < 30 * 60:
      return
    self._request_listen_key("PUT")
    self._last_keepalive_at = now

  def _request_listen_key(self, method: str) -> None:
    body = urllib_parse.urlencode({"listenKey": self.session_id}).encode()
    request = urllib_request.Request(
      f"{self._rest_base_url}/api/v3/userDataStream",
      data=body,
      method=method,
      headers={
        "X-MBX-APIKEY": self._api_key,
        "Content-Type": "application/x-www-form-urlencoded",
      },
    )
    with urllib_request.urlopen(request, timeout=10):
      return None

  @staticmethod
  def _resolve_connect():
    try:
      from websockets.sync.client import connect
    except ImportError as exc:
      raise RuntimeError("websockets_dependency_missing") from exc
    return connect


class BinanceWebSocketUserDataStreamClient:
  def __init__(
    self,
    *,
    api_key: str,
    rest_base_url: str = "https://api.binance.com",
    websocket_url: str = "wss://stream.binance.com:9443/ws",
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._api_key = api_key
    self._rest_base_url = rest_base_url
    self._websocket_url = websocket_url
    self._clock = clock or (lambda: datetime.now(UTC))

  def open_session(self) -> BinanceVenueStreamSession:
    listen_key = self._create_listen_key()
    return BinanceWebSocketUserDataStreamSession(
      session_id=listen_key,
      websocket_url=self._websocket_url,
      rest_base_url=self._rest_base_url,
      api_key=self._api_key,
      clock=self._clock,
    )

  def _create_listen_key(self) -> str:
    request = urllib_request.Request(
      f"{self._rest_base_url.rstrip('/')}/api/v3/userDataStream",
      data=b"",
      method="POST",
      headers={"X-MBX-APIKEY": self._api_key},
    )
    try:
      with urllib_request.urlopen(request, timeout=10) as response:
        payload = json.load(response)
    except urllib_error.URLError as exc:
      raise RuntimeError(f"binance_user_data_stream_unavailable:{exc}") from exc
    listen_key = payload.get("listenKey")
    if not isinstance(listen_key, str) or not listen_key:
      raise RuntimeError("binance_user_data_stream_missing_listen_key")
    return listen_key


class BinanceWebSocketMarketStreamSession:
  transport = "binance_market_data_websocket"

  def __init__(
    self,
    *,
    session_id: str,
    websocket_url: str,
    clock: Callable[[], datetime],
  ) -> None:
    self.session_id = session_id
    self._websocket_url = websocket_url
    self._clock = clock
    self._events: Queue[dict[str, Any]] = Queue()
    self._closed = False
    self._reader_stop = threading.Event()
    self._connect = self._resolve_connect()
    self._connection = self._connect(self._websocket_url)
    self._reader = threading.Thread(target=self._reader_loop, name=f"binance-market-stream-{session_id}", daemon=True)
    self._reader.start()

  def drain_events(self) -> tuple[dict[str, Any], ...]:
    if self._closed:
      return ()
    events: list[dict[str, Any]] = []
    while True:
      try:
        events.append(self._events.get_nowait())
      except Empty:
        break
    return tuple(events)

  def close(self) -> None:
    if self._closed:
      return
    self._closed = True
    self._reader_stop.set()
    try:
      self._connection.close()
    except Exception:
      pass
    if self._reader.is_alive():
      self._reader.join(timeout=1.0)

  def _reader_loop(self) -> None:
    while not self._reader_stop.is_set():
      try:
        message = self._connection.recv()
      except Exception as exc:
        if self._reader_stop.is_set():
          return
        self._events.put(
          {
            "e": "streamDisconnect",
            "stream_scope": "market_data",
            "message": str(exc),
            "E": int(self._clock().timestamp() * 1000),
          }
        )
        return
      if message is None:
        if self._reader_stop.is_set():
          return
        self._events.put(
          {
            "e": "streamDisconnect",
            "stream_scope": "market_data",
            "message": "connection_closed",
            "E": int(self._clock().timestamp() * 1000),
          }
        )
        return
      try:
        payload = json.loads(message)
      except json.JSONDecodeError as exc:
        self._events.put(
          {
            "e": "streamWarning",
            "stream_scope": "market_data",
            "message": f"invalid_json:{exc}",
            "E": int(self._clock().timestamp() * 1000),
          }
        )
        continue
      stream_name = str(payload.get("stream") or "")
      data = payload.get("data")
      if isinstance(data, dict):
        event = dict(data)
      elif isinstance(payload, dict):
        event = dict(payload)
      else:
        event = {}
      if "e" not in event:
        if stream_name.endswith("@bookTicker"):
          event["e"] = "bookTicker"
        elif stream_name.endswith("@trade"):
          event["e"] = "trade"
        elif stream_name.endswith("@aggTrade"):
          event["e"] = "aggTrade"
        elif stream_name.endswith("@miniTicker"):
          event["e"] = "24hrMiniTicker"
        elif "@depth" in stream_name:
          event["e"] = "depthUpdate"
        elif "@kline_" in stream_name:
          event["e"] = "kline"
      event["stream_scope"] = "market_data"
      event["stream"] = stream_name
      event.setdefault("_received_at_ms", int(self._clock().timestamp() * 1000))
      self._events.put(event)

  @staticmethod
  def _resolve_connect():
    try:
      from websockets.sync.client import connect
    except ImportError as exc:
      raise RuntimeError("websockets_dependency_missing") from exc
    return connect


class BinanceWebSocketMarketStreamClient:
  def __init__(
    self,
    *,
    symbol: str,
    timeframe: str,
    websocket_url: str = "wss://stream.binance.com:9443/stream",
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._symbol = symbol
    self._timeframe = timeframe
    self._websocket_url = websocket_url.rstrip("/")
    self._clock = clock or (lambda: datetime.now(UTC))

  def open_session(self) -> BinanceVenueStreamSession:
    market_symbol = _normalize_binance_stream_symbol(self._symbol)
    streams = (
      f"{market_symbol}@trade/"
      f"{market_symbol}@aggTrade/"
      f"{market_symbol}@bookTicker/"
      f"{market_symbol}@miniTicker/"
      f"{market_symbol}@depth20@100ms/"
      f"{market_symbol}@kline_{self._timeframe}"
    )
    return BinanceWebSocketMarketStreamSession(
      session_id=f"market:{market_symbol}:trade+aggTrade+bookTicker+miniTicker+depth+kline_{self._timeframe}",
      websocket_url=f"{self._websocket_url}?streams={streams}",
      clock=self._clock,
    )


class BinanceCombinedWebSocketVenueSession:
  transport = "binance_multi_stream_websocket"

  def __init__(
    self,
    *,
    user_data_session: BinanceVenueStreamSession,
    market_stream_session: BinanceVenueStreamSession,
  ) -> None:
    self.session_id = f"{user_data_session.session_id}|{market_stream_session.session_id}"
    self._user_data_session = user_data_session
    self._market_stream_session = market_stream_session

  def drain_events(self) -> tuple[dict[str, Any], ...]:
    events: list[dict[str, Any]] = []
    for event in self._user_data_session.drain_events():
      next_event = dict(event)
      next_event.setdefault("stream_scope", "user_data")
      events.append(next_event)
    for event in self._market_stream_session.drain_events():
      next_event = dict(event)
      next_event.setdefault("stream_scope", "market_data")
      events.append(next_event)
    return tuple(events)

  def close(self) -> None:
    user_error: Exception | None = None
    try:
      self._user_data_session.close()
    except Exception as exc:  # pragma: no cover - defensive aggregation
      user_error = exc
    try:
      self._market_stream_session.close()
    except Exception as exc:  # pragma: no cover - defensive aggregation
      if user_error is not None:
        raise RuntimeError(f"{user_error}; {exc}") from exc
      raise
    if user_error is not None:
      raise user_error


class BinanceCombinedWebSocketVenueStreamClient:
  transport = "binance_multi_stream_websocket"

  def __init__(
    self,
    *,
    api_key: str,
    symbol: str,
    timeframe: str,
    rest_base_url: str = "https://api.binance.com",
    user_data_websocket_url: str = "wss://stream.binance.com:9443/ws",
    market_websocket_url: str = "wss://stream.binance.com:9443/stream",
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._user_data_client = BinanceWebSocketUserDataStreamClient(
      api_key=api_key,
      rest_base_url=rest_base_url,
      websocket_url=user_data_websocket_url,
      clock=clock,
    )
    self._market_stream_client = BinanceWebSocketMarketStreamClient(
      symbol=symbol,
      timeframe=timeframe,
      websocket_url=market_websocket_url,
      clock=clock,
    )

  def open_session(self) -> BinanceVenueStreamSession:
    user_data_session = self._user_data_client.open_session()
    try:
      market_stream_session = self._market_stream_client.open_session()
    except Exception:
      user_data_session.close()
      raise
    return BinanceCombinedWebSocketVenueSession(
      user_data_session=user_data_session,
      market_stream_session=market_stream_session,
    )


GENERIC_POLLING_VENUE_STREAM_COVERAGE = (
  "order_state_snapshots",
  "trade_ticks",
  "aggregate_trade_ticks",
  "book_ticker",
  "mini_ticker",
  "depth_updates",
  "kline_candles",
  "order_book_lifecycle",
)
BINANCE_USER_DATA_STREAM_COVERAGE = (
  "execution_reports",
  "account_positions",
  "balance_updates",
  "order_list_status",
)
BINANCE_MARKET_STREAM_COVERAGE = (
  "trade_ticks",
  "aggregate_trade_ticks",
  "book_ticker",
  "mini_ticker",
  "depth_updates",
  "kline_candles",
  "order_book_lifecycle",
)
BINANCE_VENUE_STREAM_COVERAGE = (
  *BINANCE_USER_DATA_STREAM_COVERAGE,
  *BINANCE_MARKET_STREAM_COVERAGE,
)


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


class GenericPollingVenueStreamSession:
  transport = "generic_ccxt_polling_transport"

  def __init__(
    self,
    *,
    session_id: str,
    exchange: VenueExecutionExchange,
    symbol: str,
    timeframe: str,
    clock: Callable[[], datetime],
    poll_interval_seconds: int,
  ) -> None:
    self.session_id = session_id
    self._exchange = exchange
    self._symbol = symbol
    self._timeframe = timeframe
    self._clock = clock
    self._poll_interval_seconds = max(poll_interval_seconds, 0)
    self._closed = False
    self._last_polled_at: datetime | None = None
    self._last_depth_key: tuple[object, ...] | None = None
    self._last_ticker_key: tuple[object, ...] | None = None
    self._last_trade_key: tuple[object, ...] | None = None
    self._last_kline_key: tuple[object, ...] | None = None
    self._last_depth_update_id: int | None = None

  def drain_events(self) -> tuple[dict[str, Any], ...]:
    if self._closed:
      return ()
    now = self._clock()
    if (
      self._last_polled_at is not None
      and self._poll_interval_seconds > 0
      and (now - self._last_polled_at).total_seconds() < self._poll_interval_seconds
    ):
      return ()
    self._last_polled_at = now
    events: list[dict[str, Any]] = []

    try:
      snapshot = self._exchange.fetch_order_book(self._symbol, 20, {})
      if event := self._build_depth_event(snapshot=snapshot, polled_at=now):
        events.append(event)
    except Exception as exc:
      events.append(self._build_warning_event(kind="order_book", message=str(exc), event_at=now))

    try:
      ticker = self._exchange.fetch_ticker(self._symbol, {})
      next_events = self._build_ticker_events(ticker=ticker, polled_at=now)
      events.extend(next_events)
    except Exception as exc:
      events.append(self._build_warning_event(kind="ticker", message=str(exc), event_at=now))

    try:
      trades = self._exchange.fetch_trades(self._symbol, None, 1, {})
      if trades:
        next_events = self._build_trade_events(trade=trades[-1], polled_at=now)
        events.extend(next_events)
    except Exception as exc:
      events.append(self._build_warning_event(kind="trades", message=str(exc), event_at=now))

    try:
      candles = self._exchange.fetch_ohlcv(self._symbol, self._timeframe, None, 1, {})
      if candles:
        if event := self._build_kline_event(row=candles[-1], polled_at=now):
          events.append(event)
    except Exception as exc:
      events.append(self._build_warning_event(kind="ohlcv", message=str(exc), event_at=now))

    return tuple(events)

  def close(self) -> None:
    self._closed = True

  def _build_depth_event(self, *, snapshot: dict[str, Any], polled_at: datetime) -> dict[str, Any] | None:
    update_id = (
      _coerce_int(_extract_nested_value(snapshot, ("info", "lastUpdateId")))
      or _coerce_int(snapshot.get("nonce"))
      or _coerce_int(snapshot.get("lastUpdateId"))
    )
    bids = _coerce_depth_levels(snapshot.get("bids"))
    asks = _coerce_depth_levels(snapshot.get("asks"))
    key = (
      update_id,
      tuple(bids),
      tuple(asks),
    )
    if key == self._last_depth_key:
      return None
    previous_update_id = self._last_depth_update_id
    self._last_depth_key = key
    self._last_depth_update_id = update_id
    event_at = _coerce_datetime(snapshot.get("datetime"), snapshot.get("timestamp")) or polled_at
    return {
      "e": "depthUpdate",
      "E": int(event_at.timestamp() * 1000),
      "U": update_id,
      "u": update_id,
      "pu": previous_update_id,
      "b": [[str(price), str(quantity)] for price, quantity in bids],
      "a": [[str(price), str(quantity)] for price, quantity in asks],
      "stream_scope": "market_data",
      "stream": "polling@depth",
      "_received_at_ms": int(polled_at.timestamp() * 1000),
    }

  def _build_ticker_events(self, *, ticker: dict[str, Any], polled_at: datetime) -> tuple[dict[str, Any], ...]:
    event_at = _coerce_datetime(ticker.get("datetime"), ticker.get("timestamp")) or polled_at
    key = (
      _coerce_float(ticker.get("bid")),
      _coerce_float(ticker.get("bidVolume")),
      _coerce_float(ticker.get("ask")),
      _coerce_float(ticker.get("askVolume")),
      _coerce_float(ticker.get("open")),
      _coerce_float(ticker.get("last")) or _coerce_float(ticker.get("close")),
      _coerce_float(ticker.get("high")),
      _coerce_float(ticker.get("low")),
      _coerce_float(ticker.get("baseVolume")),
      _coerce_float(ticker.get("quoteVolume")),
      event_at,
    )
    if key == self._last_ticker_key:
      return ()
    self._last_ticker_key = key
    event_ms = int(event_at.timestamp() * 1000)
    return (
      {
        "e": "bookTicker",
        "E": event_ms,
        "b": str(ticker.get("bid") or ""),
        "B": str(ticker.get("bidVolume") or ""),
        "a": str(ticker.get("ask") or ""),
        "A": str(ticker.get("askVolume") or ""),
        "stream_scope": "market_data",
        "stream": "polling@bookTicker",
        "_received_at_ms": int(polled_at.timestamp() * 1000),
      },
      {
        "e": "24hrMiniTicker",
        "E": event_ms,
        "o": str(ticker.get("open") or ""),
        "c": str(ticker.get("last") or ticker.get("close") or ""),
        "h": str(ticker.get("high") or ""),
        "l": str(ticker.get("low") or ""),
        "v": str(ticker.get("baseVolume") or ""),
        "q": str(ticker.get("quoteVolume") or ""),
        "stream_scope": "market_data",
        "stream": "polling@miniTicker",
        "_received_at_ms": int(polled_at.timestamp() * 1000),
      },
    )

  def _build_trade_events(self, *, trade: dict[str, Any], polled_at: datetime) -> tuple[dict[str, Any], ...]:
    event_at = _coerce_datetime(trade.get("datetime"), trade.get("timestamp")) or polled_at
    event_id = _coerce_string(trade.get("id")) or str(int(event_at.timestamp() * 1000))
    key = (
      event_id,
      _coerce_float(trade.get("price")),
      _coerce_float(trade.get("amount")),
      event_at,
    )
    if key == self._last_trade_key:
      return ()
    self._last_trade_key = key
    event_ms = int(event_at.timestamp() * 1000)
    return (
      {
        "e": "trade",
        "E": event_ms,
        "T": event_ms,
        "t": event_id,
        "p": str(trade.get("price") or ""),
        "q": str(trade.get("amount") or ""),
        "stream_scope": "market_data",
        "stream": "polling@trade",
        "_received_at_ms": int(polled_at.timestamp() * 1000),
      },
      {
        "e": "aggTrade",
        "E": event_ms,
        "T": event_ms,
        "a": event_id,
        "p": str(trade.get("price") or ""),
        "q": str(trade.get("amount") or ""),
        "stream_scope": "market_data",
        "stream": "polling@aggTrade",
        "_received_at_ms": int(polled_at.timestamp() * 1000),
      },
    )

  def _build_kline_event(self, *, row: list[Any], polled_at: datetime) -> dict[str, Any] | None:
    key = tuple(row)
    if key == self._last_kline_key:
      return None
    self._last_kline_key = key
    open_at = _coerce_ohlcv_timestamp(row[0] if row else None, timeframe=self._timeframe) or polled_at
    close_at = _coerce_ohlcv_close_timestamp(row[0] if row else None, timeframe=self._timeframe) or open_at
    return {
      "e": "kline",
      "E": int(close_at.timestamp() * 1000),
      "stream_scope": "market_data",
      "stream": f"polling@kline_{self._timeframe}",
      "_received_at_ms": int(polled_at.timestamp() * 1000),
      "k": {
        "i": self._timeframe,
        "t": int(open_at.timestamp() * 1000),
        "T": int(close_at.timestamp() * 1000),
        "o": str(row[1] if len(row) > 1 else ""),
        "h": str(row[2] if len(row) > 2 else ""),
        "l": str(row[3] if len(row) > 3 else ""),
        "c": str(row[4] if len(row) > 4 else ""),
        "v": str(row[5] if len(row) > 5 else ""),
        "x": True,
      },
    }

  @staticmethod
  def _build_warning_event(*, kind: str, message: str, event_at: datetime) -> dict[str, Any]:
    return {
      "e": "streamWarning",
      "stream_scope": "market_data",
      "message": f"polling_{kind}_failed:{message}",
      "E": int(event_at.timestamp() * 1000),
      "_received_at_ms": int(event_at.timestamp() * 1000),
    }


class GenericPollingVenueStreamClient:
  transport = "generic_ccxt_polling_transport"

  def __init__(
    self,
    *,
    venue: str,
    exchange: VenueExecutionExchange,
    symbol: str,
    timeframe: str,
    clock: Callable[[], datetime],
    poll_interval_seconds: int,
  ) -> None:
    self._venue = venue
    self._exchange = exchange
    self._symbol = symbol
    self._timeframe = timeframe
    self._clock = clock
    self._poll_interval_seconds = poll_interval_seconds
    self._session_count = 0

  def open_session(self) -> BinanceVenueStreamSession:
    self._session_count += 1
    return GenericPollingVenueStreamSession(
      session_id=f"{self._venue}:poll:{_normalize_binance_stream_symbol(self._symbol)}:{self._timeframe}:{self._session_count}",
      exchange=self._exchange,
      symbol=self._symbol,
      timeframe=self._timeframe,
      clock=self._clock,
      poll_interval_seconds=self._poll_interval_seconds,
    )


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


class BinanceVenueExecutionAdapter(VenueExecutionPort):
  def __init__(
    self,
    *,
    venue: str = "binance",
    api_key: str | None = None,
    api_secret: str | None = None,
    exchange: VenueExecutionExchange | None = None,
    venue_stream_client: BinanceVenueStreamClient | None = None,
    poll_interval_seconds: int = 15,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._venue = venue
    self._api_key = api_key
    self._api_secret = api_secret
    self._exchange = exchange
    self._clock = clock or (lambda: datetime.now(UTC))
    self._venue_stream_client = venue_stream_client
    self._poll_interval_seconds = poll_interval_seconds
    self._active_stream_sessions: dict[str, BinanceVenueStreamSession] = {}
    self._order_states: dict[str, GuardedLiveVenueOrderResult] = {}
    self._local_order_books: dict[str, LocalOrderBookState] = {}

  def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []
    if self._exchange is None and not (self._api_key and self._api_secret):
      issues.append("binance_trade_credentials_missing")
    if self._venue_stream_client is None and self._exchange is None and not self._api_key:
      issues.append("binance_venue_stream_unavailable")
    return (len(issues) == 0), tuple(issues)

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
    restore = GuardedLiveVenueSessionRestore(
      state=state,
      restored_at=current_time,
      source="binance_exchange",
      venue=self._venue,
      symbol=symbol,
      open_orders=open_orders,
      synced_orders=tuple(synced_orders),
      issues=tuple(issues),
    )
    self._record_restore_state(restore)
    return restore

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
    restore = self.restore_session(symbol=symbol, owned_order_ids=owned_order_ids)
    opened_stream = self._open_stream_session(
      symbol=symbol,
      timeframe=timeframe,
      current_issues=restore.issues,
    )
    stream_session = opened_stream["session"]
    stream_issues = tuple(opened_stream["issues"])
    if stream_session is None:
      return GuardedLiveVenueSessionHandoff(
        state="unavailable",
        handed_off_at=current_time,
        source="venue_stream_transport",
        venue=self._venue,
        symbol=symbol,
        timeframe=timeframe,
        owner_run_id=owner_run_id,
        owner_session_id=owner_session_id,
        transport="venue_stream_unavailable",
        supervision_state="unavailable",
        order_book_state="unavailable",
        coverage=self._coverage_for_transport(None),
        active_order_count=len(restore.open_orders),
        issues=stream_issues,
      )
    session_id = stream_session.session_id
    order_book_key = self._resolve_order_book_key(
      owner_run_id=owner_run_id,
      owner_session_id=owner_session_id,
      session_id=session_id,
      symbol=symbol,
    )
    rebuild = self._rebuild_local_order_book_from_snapshot(
      symbol=symbol,
      order_book_key=order_book_key,
      rebuild_count=0,
      reason="handoff",
    )
    channel_restore = self._restore_market_channels_from_exchange(
      symbol=symbol,
      timeframe=timeframe,
      reason="handoff",
    )
    return GuardedLiveVenueSessionHandoff(
      state="active",
      handed_off_at=current_time,
      source=self._source_for_transport(stream_session.transport),
      venue=self._venue,
      symbol=symbol,
      timeframe=timeframe,
      owner_run_id=owner_run_id,
      owner_session_id=owner_session_id,
      venue_session_id=session_id,
      transport=stream_session.transport,
      cursor="event-0",
      last_event_at=restore.restored_at,
      last_sync_at=current_time,
      supervision_state=self._supervision_state_for_transport(stream_session.transport),
      order_book_state=str(rebuild["state"]),
      order_book_last_update_id=rebuild["last_update_id"],
      order_book_gap_count=0,
      order_book_rebuild_count=rebuild["rebuild_count"],
      order_book_last_rebuilt_at=rebuild["rebuilt_at"],
      order_book_bid_level_count=rebuild["bid_level_count"],
      order_book_ask_level_count=rebuild["ask_level_count"],
      order_book_best_bid_price=rebuild["best_bid_price"],
      order_book_best_bid_quantity=rebuild["best_bid_quantity"],
      order_book_best_ask_price=rebuild["best_ask_price"],
      order_book_best_ask_quantity=rebuild["best_ask_quantity"],
      order_book_bids=rebuild["bids"],
      order_book_asks=rebuild["asks"],
      channel_restore_state=str(channel_restore["state"]),
      channel_restore_count=1 if channel_restore["restored_at"] is not None else 0,
      channel_last_restored_at=channel_restore["restored_at"],
      channel_continuation_state=(
        "restored_from_exchange"
        if channel_restore["restored_at"] is not None
        else "inactive"
      ),
      channel_continuation_count=1 if channel_restore["restored_at"] is not None else 0,
      channel_last_continued_at=channel_restore["restored_at"],
      trade_snapshot=channel_restore["trade_snapshot"],
      aggregate_trade_snapshot=channel_restore["aggregate_trade_snapshot"],
      book_ticker_snapshot=channel_restore["book_ticker_snapshot"],
      mini_ticker_snapshot=channel_restore["mini_ticker_snapshot"],
      kline_snapshot=channel_restore["kline_snapshot"],
      coverage=self._coverage_for_transport(stream_session.transport),
      last_market_event_at=channel_restore["last_market_event_at"],
      last_kline_event_at=channel_restore["last_kline_event_at"],
      last_aggregate_trade_event_at=channel_restore["last_aggregate_trade_event_at"],
      last_mini_ticker_event_at=channel_restore["last_mini_ticker_event_at"],
      last_trade_event_at=channel_restore["last_trade_event_at"],
      last_book_ticker_event_at=channel_restore["last_book_ticker_event_at"],
      active_order_count=len(restore.open_orders),
      issues=tuple(dict.fromkeys((*stream_issues, *tuple(rebuild["issues"]), *tuple(channel_restore["issues"])))),
    )

  def sync_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    order_ids: tuple[str, ...],
  ) -> GuardedLiveVenueSessionSync:
    current_time = self._clock()
    session_id = handoff.venue_session_id or ""
    order_book_key = self._resolve_order_book_key(
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      session_id=session_id,
      symbol=handoff.symbol,
    )
    stream_session = self._active_stream_sessions.get(session_id)
    local_book = self._local_order_books.get(order_book_key)
    issues: list[str] = self._filter_venue_stream_issues(handoff.issues)
    supervision_state = (
      handoff.supervision_state
      if handoff.state != "released" and handoff.supervision_state
      else ("streaming" if handoff.state != "released" else "released")
    )
    failover_count = handoff.failover_count
    last_failover_at = handoff.last_failover_at
    coverage = handoff.coverage or self._coverage_for_transport(handoff.transport)
    order_book_state = handoff.order_book_state or "awaiting_depth"
    order_book_last_update_id = handoff.order_book_last_update_id
    order_book_gap_count = handoff.order_book_gap_count
    order_book_rebuild_count = handoff.order_book_rebuild_count
    order_book_last_rebuilt_at = handoff.order_book_last_rebuilt_at
    order_book_bid_level_count = handoff.order_book_bid_level_count
    order_book_ask_level_count = handoff.order_book_ask_level_count
    order_book_best_bid_price = handoff.order_book_best_bid_price
    order_book_best_bid_quantity = handoff.order_book_best_bid_quantity
    order_book_best_ask_price = handoff.order_book_best_ask_price
    order_book_best_ask_quantity = handoff.order_book_best_ask_quantity
    order_book_bids = handoff.order_book_bids
    order_book_asks = handoff.order_book_asks
    channel_restore_state = handoff.channel_restore_state or "inactive"
    channel_restore_count = handoff.channel_restore_count
    channel_last_restored_at = handoff.channel_last_restored_at
    channel_continuation_state = handoff.channel_continuation_state or "inactive"
    channel_continuation_count = handoff.channel_continuation_count
    channel_last_continued_at = handoff.channel_last_continued_at
    trade_snapshot = handoff.trade_snapshot
    aggregate_trade_snapshot = handoff.aggregate_trade_snapshot
    book_ticker_snapshot = handoff.book_ticker_snapshot
    mini_ticker_snapshot = handoff.mini_ticker_snapshot
    kline_snapshot = handoff.kline_snapshot
    last_event_at = handoff.last_event_at
    last_market_event_at = handoff.last_market_event_at
    last_depth_event_at = handoff.last_depth_event_at
    last_kline_event_at = handoff.last_kline_event_at
    last_aggregate_trade_event_at = handoff.last_aggregate_trade_event_at
    last_mini_ticker_event_at = handoff.last_mini_ticker_event_at
    last_account_event_at = handoff.last_account_event_at
    last_balance_event_at = handoff.last_balance_event_at
    last_order_list_event_at = handoff.last_order_list_event_at
    last_trade_event_at = handoff.last_trade_event_at
    last_book_ticker_event_at = handoff.last_book_ticker_event_at
    event_count = 0
    if local_book is None and handoff.state != "released":
      local_book = self._restore_local_order_book_from_handoff(
        handoff=handoff,
        order_book_key=order_book_key,
      )
      if local_book is not None:
        order_book_state = "persisted_recovered"
        order_book_last_update_id = local_book.last_update_id
        order_book_rebuild_count = local_book.rebuild_count
        order_book_last_rebuilt_at = local_book.rebuilt_at
        order_book_bid_level_count = local_book.bid_level_count
        order_book_ask_level_count = local_book.ask_level_count
        order_book_best_bid_price, order_book_best_bid_quantity = local_book.best_bid
        order_book_best_ask_price, order_book_best_ask_quantity = local_book.best_ask
        order_book_bids = handoff.order_book_bids
        order_book_asks = handoff.order_book_asks
        if self._handoff_has_channel_snapshots(handoff):
          channel_continuation_state = "persisted_recovered"
          channel_continuation_count += 1
          channel_last_continued_at = current_time
      else:
        rebuild = self._rebuild_local_order_book_from_snapshot(
          symbol=handoff.symbol or "",
          order_book_key=order_book_key,
          rebuild_count=order_book_rebuild_count,
          reason="local_book_missing",
        )
        local_book = rebuild["book"]
        order_book_state = str(rebuild["state"])
        order_book_last_update_id = rebuild["last_update_id"]
        order_book_rebuild_count = rebuild["rebuild_count"]
        order_book_last_rebuilt_at = rebuild["rebuilt_at"]
        order_book_bid_level_count = rebuild["bid_level_count"]
        order_book_ask_level_count = rebuild["ask_level_count"]
        order_book_best_bid_price = rebuild["best_bid_price"]
        order_book_best_bid_quantity = rebuild["best_bid_quantity"]
        order_book_best_ask_price = rebuild["best_ask_price"]
        order_book_best_ask_quantity = rebuild["best_ask_quantity"]
        order_book_bids = rebuild["bids"]
        order_book_asks = rebuild["asks"]
        issues.extend(tuple(rebuild["issues"]))
    if stream_session is None and handoff.state != "released":
      failover = self._failover_stream_session(
        session_id=session_id,
        symbol=handoff.symbol or "",
        timeframe=handoff.timeframe or "5m",
        current_issues=tuple(issues),
        reason="session_missing",
      )
      stream_session = failover["session"]
      issues = list(failover["issues"])
      if stream_session is None:
        supervision_state = "reconnect_failed"
        order_book_state = "unavailable"
      else:
        session_id = stream_session.session_id
        supervision_state = self._supervision_state_for_transport(stream_session.transport)
        coverage = self._coverage_for_transport(stream_session.transport)
        failover_count += 1
        last_failover_at = current_time
        order_book_gap_count += 1
        if local_book is None:
          rebuild = self._rebuild_local_order_book_from_snapshot(
            symbol=handoff.symbol or "",
            order_book_key=order_book_key,
            rebuild_count=order_book_rebuild_count,
            reason="session_missing",
          )
          local_book = rebuild["book"]
          order_book_state = str(rebuild["state"])
          order_book_last_update_id = rebuild["last_update_id"]
          order_book_rebuild_count = rebuild["rebuild_count"]
          order_book_last_rebuilt_at = rebuild["rebuilt_at"]
          order_book_bid_level_count = rebuild["bid_level_count"]
          order_book_ask_level_count = rebuild["ask_level_count"]
          order_book_best_bid_price = rebuild["best_bid_price"]
          order_book_best_bid_quantity = rebuild["best_bid_quantity"]
          order_book_best_ask_price = rebuild["best_ask_price"]
          order_book_best_ask_quantity = rebuild["best_ask_quantity"]
          order_book_bids = rebuild["bids"]
          order_book_asks = rebuild["asks"]
          issues.extend(tuple(rebuild["issues"]))
        channel_restore = self._restore_market_channels_from_exchange(
          symbol=handoff.symbol or "",
          timeframe=handoff.timeframe or "5m",
          reason="session_missing",
        )
        channel_restore_state = str(channel_restore["state"])
        if channel_restore["restored_at"] is not None:
          channel_restore_count += 1
          channel_last_restored_at = channel_restore["restored_at"]
          channel_continuation_state = "restored_from_exchange"
          channel_continuation_count += 1
          channel_last_continued_at = channel_restore["restored_at"]
          trade_snapshot = channel_restore["trade_snapshot"] or trade_snapshot
          aggregate_trade_snapshot = channel_restore["aggregate_trade_snapshot"] or aggregate_trade_snapshot
          book_ticker_snapshot = channel_restore["book_ticker_snapshot"] or book_ticker_snapshot
          mini_ticker_snapshot = channel_restore["mini_ticker_snapshot"] or mini_ticker_snapshot
          kline_snapshot = channel_restore["kline_snapshot"] or kline_snapshot
        last_market_event_at = _max_datetime(last_market_event_at, channel_restore["last_market_event_at"])
        last_trade_event_at = _max_datetime(last_trade_event_at, channel_restore["last_trade_event_at"])
        last_aggregate_trade_event_at = _max_datetime(
          last_aggregate_trade_event_at,
          channel_restore["last_aggregate_trade_event_at"],
        )
        last_book_ticker_event_at = _max_datetime(
          last_book_ticker_event_at,
          channel_restore["last_book_ticker_event_at"],
        )
        last_mini_ticker_event_at = _max_datetime(
          last_mini_ticker_event_at,
          channel_restore["last_mini_ticker_event_at"],
        )
        last_kline_event_at = _max_datetime(last_kline_event_at, channel_restore["last_kline_event_at"])
        if order_book_best_bid_price is None and channel_restore["best_bid_price"] is not None:
          order_book_best_bid_price = channel_restore["best_bid_price"]
        if order_book_best_bid_quantity is None and channel_restore["best_bid_quantity"] is not None:
          order_book_best_bid_quantity = channel_restore["best_bid_quantity"]
        if order_book_best_ask_price is None and channel_restore["best_ask_price"] is not None:
          order_book_best_ask_price = channel_restore["best_ask_price"]
        if order_book_best_ask_quantity is None and channel_restore["best_ask_quantity"] is not None:
          order_book_best_ask_quantity = channel_restore["best_ask_quantity"]
        issues.extend(tuple(channel_restore["issues"]))
        event_count += 1

    events = stream_session.drain_events() if stream_session is not None else ()
    active_transport = stream_session.transport if stream_session is not None else handoff.transport
    failover_reason: str | None = None
    for event in events:
      event_type = str(event.get("e") or "")
      event_at = self._coerce_stream_event_at(event) or current_time
      if event_type == "streamDisconnect":
        failover_reason = str(event.get("message") or "stream_disconnect")
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "streamWarning":
        issues.append(
          f"{self._stream_issue_prefix_for_transport(active_transport)}_warning:"
          f"{event.get('message', 'unknown')}"
        )
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "outboundAccountPosition":
        last_account_event_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "balanceUpdate":
        last_balance_event_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "listStatus":
        last_order_list_event_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "trade":
        last_market_event_at = event_at
        last_trade_event_at = event_at
        trade_snapshot = GuardedLiveTradeChannelSnapshot(
          event_id=_coerce_string(event.get("t")),
          price=_coerce_float(event.get("p")),
          quantity=_coerce_float(event.get("q")),
          event_at=event_at,
        )
        channel_continuation_state = "streaming"
        channel_last_continued_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "aggTrade":
        last_market_event_at = event_at
        last_aggregate_trade_event_at = event_at
        aggregate_trade_snapshot = GuardedLiveTradeChannelSnapshot(
          event_id=_coerce_string(event.get("a")),
          price=_coerce_float(event.get("p")),
          quantity=_coerce_float(event.get("q")),
          event_at=event_at,
        )
        channel_continuation_state = "streaming"
        channel_last_continued_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "24hrMiniTicker":
        last_market_event_at = event_at
        last_mini_ticker_event_at = event_at
        mini_ticker_snapshot = GuardedLiveMiniTickerChannelSnapshot(
          open_price=_coerce_float(event.get("o")),
          close_price=_coerce_float(event.get("c")),
          high_price=_coerce_float(event.get("h")),
          low_price=_coerce_float(event.get("l")),
          base_volume=_coerce_float(event.get("v")),
          quote_volume=_coerce_float(event.get("q")),
          event_at=event_at,
        )
        channel_continuation_state = "streaming"
        channel_last_continued_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "bookTicker":
        last_market_event_at = event_at
        last_book_ticker_event_at = event_at
        book_bid_price = _coerce_float(event.get("b"))
        book_bid_quantity = _coerce_float(event.get("B"))
        book_ask_price = _coerce_float(event.get("a"))
        book_ask_quantity = _coerce_float(event.get("A"))
        if book_bid_price is not None:
          order_book_best_bid_price = book_bid_price
        if book_bid_quantity is not None:
          order_book_best_bid_quantity = book_bid_quantity
        if book_ask_price is not None:
          order_book_best_ask_price = book_ask_price
        if book_ask_quantity is not None:
          order_book_best_ask_quantity = book_ask_quantity
        book_ticker_snapshot = GuardedLiveBookTickerChannelSnapshot(
          bid_price=book_bid_price,
          bid_quantity=book_bid_quantity,
          ask_price=book_ask_price,
          ask_quantity=book_ask_quantity,
          event_at=event_at,
        )
        channel_continuation_state = "streaming"
        channel_last_continued_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "depthUpdate":
        last_market_event_at = event_at
        last_depth_event_at = event_at
        depth_first_update_id = _coerce_int(event.get("U"))
        depth_last_update_id = _coerce_int(event.get("u"))
        depth_previous_update_id = _coerce_int(event.get("pu"))
        depth_bids = _coerce_depth_levels(event.get("b"))
        depth_asks = _coerce_depth_levels(event.get("a"))
        if self._is_polling_transport(active_transport):
          local_book = _build_local_order_book_from_snapshot_row(
            symbol=handoff.symbol or "",
            row={
              "lastUpdateId": depth_last_update_id or depth_first_update_id,
              "bids": [[price, quantity] for price, quantity in depth_bids],
              "asks": [[price, quantity] for price, quantity in depth_asks],
            },
            rebuilt_at=order_book_last_rebuilt_at or handoff.handed_off_at or current_time,
            rebuild_count=order_book_rebuild_count,
          )
          self._local_order_books[order_book_key] = local_book
          order_book_state = "streaming"
          order_book_last_update_id = local_book.last_update_id
          order_book_bid_level_count = local_book.bid_level_count
          order_book_ask_level_count = local_book.ask_level_count
          order_book_best_bid_price, order_book_best_bid_quantity = local_book.best_bid
          order_book_best_ask_price, order_book_best_ask_quantity = local_book.best_ask
          order_book_bids = _serialize_order_book_side(local_book.bids, reverse=True)
          order_book_asks = _serialize_order_book_side(local_book.asks, reverse=False)
          event_count += 1
          last_event_at = event_at
          continue
        if local_book is None:
          rebuild = self._rebuild_local_order_book_from_snapshot(
            symbol=handoff.symbol or "",
            order_book_key=order_book_key,
            rebuild_count=order_book_rebuild_count,
            reason="depth_without_local_book",
          )
          local_book = rebuild["book"]
          order_book_state = str(rebuild["state"])
          order_book_last_update_id = rebuild["last_update_id"]
          order_book_rebuild_count = rebuild["rebuild_count"]
          order_book_last_rebuilt_at = rebuild["rebuilt_at"]
          order_book_bid_level_count = rebuild["bid_level_count"]
          order_book_ask_level_count = rebuild["ask_level_count"]
          order_book_best_bid_price = rebuild["best_bid_price"]
          order_book_best_bid_quantity = rebuild["best_bid_quantity"]
          order_book_best_ask_price = rebuild["best_ask_price"]
          order_book_best_ask_quantity = rebuild["best_ask_quantity"]
          order_book_bids = rebuild["bids"]
          order_book_asks = rebuild["asks"]
          issues.extend(tuple(rebuild["issues"]))
        if local_book is not None and depth_last_update_id is not None and local_book.last_update_id is not None:
          if depth_last_update_id <= local_book.last_update_id:
            event_count += 1
            last_event_at = event_at
            continue
        continuity_ok = _depth_event_matches_local_book(
          book=local_book,
          first_update_id=depth_first_update_id,
          last_update_id=depth_last_update_id,
          previous_update_id=depth_previous_update_id,
        )
        if local_book is None or not continuity_ok:
          order_book_gap_count += 1
          issues.append(
            "binance_order_book_gap_detected:"
            f"{order_book_last_update_id or 'none'}:"
            f"{depth_previous_update_id or depth_first_update_id or 'none'}"
          )
          rebuild = self._rebuild_local_order_book_from_snapshot(
            symbol=handoff.symbol or "",
            order_book_key=order_book_key,
            rebuild_count=order_book_rebuild_count,
            reason="depth_gap",
          )
          local_book = rebuild["book"]
          order_book_state = str(rebuild["state"])
          order_book_last_update_id = rebuild["last_update_id"]
          order_book_rebuild_count = rebuild["rebuild_count"]
          order_book_last_rebuilt_at = rebuild["rebuilt_at"]
          order_book_bid_level_count = rebuild["bid_level_count"]
          order_book_ask_level_count = rebuild["ask_level_count"]
          order_book_best_bid_price = rebuild["best_bid_price"]
          order_book_best_bid_quantity = rebuild["best_bid_quantity"]
          order_book_best_ask_price = rebuild["best_ask_price"]
          order_book_best_ask_quantity = rebuild["best_ask_quantity"]
          order_book_bids = rebuild["bids"]
          order_book_asks = rebuild["asks"]
          channel_restore = self._restore_market_channels_from_exchange(
            symbol=handoff.symbol or "",
            timeframe=handoff.timeframe or "5m",
            reason="depth_gap",
          )
          channel_restore_state = str(channel_restore["state"])
          if channel_restore["restored_at"] is not None:
            channel_restore_count += 1
            channel_last_restored_at = channel_restore["restored_at"]
            channel_continuation_state = "restored_from_exchange"
            channel_continuation_count += 1
            channel_last_continued_at = channel_restore["restored_at"]
            trade_snapshot = channel_restore["trade_snapshot"] or trade_snapshot
            aggregate_trade_snapshot = channel_restore["aggregate_trade_snapshot"] or aggregate_trade_snapshot
            book_ticker_snapshot = channel_restore["book_ticker_snapshot"] or book_ticker_snapshot
            mini_ticker_snapshot = channel_restore["mini_ticker_snapshot"] or mini_ticker_snapshot
            kline_snapshot = channel_restore["kline_snapshot"] or kline_snapshot
          last_market_event_at = _max_datetime(last_market_event_at, channel_restore["last_market_event_at"])
          last_trade_event_at = _max_datetime(last_trade_event_at, channel_restore["last_trade_event_at"])
          last_aggregate_trade_event_at = _max_datetime(
            last_aggregate_trade_event_at,
            channel_restore["last_aggregate_trade_event_at"],
          )
          last_book_ticker_event_at = _max_datetime(
            last_book_ticker_event_at,
            channel_restore["last_book_ticker_event_at"],
          )
          last_mini_ticker_event_at = _max_datetime(
            last_mini_ticker_event_at,
            channel_restore["last_mini_ticker_event_at"],
          )
          last_kline_event_at = _max_datetime(last_kline_event_at, channel_restore["last_kline_event_at"])
          if order_book_best_bid_price is None and channel_restore["best_bid_price"] is not None:
            order_book_best_bid_price = channel_restore["best_bid_price"]
          if order_book_best_bid_quantity is None and channel_restore["best_bid_quantity"] is not None:
            order_book_best_bid_quantity = channel_restore["best_bid_quantity"]
          if order_book_best_ask_price is None and channel_restore["best_ask_price"] is not None:
            order_book_best_ask_price = channel_restore["best_ask_price"]
          if order_book_best_ask_quantity is None and channel_restore["best_ask_quantity"] is not None:
            order_book_best_ask_quantity = channel_restore["best_ask_quantity"]
          issues.extend(tuple(channel_restore["issues"]))
          issues.extend(tuple(rebuild["issues"]))
          event_count += 1
          last_event_at = event_at
          continue
        local_book = self._apply_depth_update_to_local_book(
          book=local_book,
          last_update_id=depth_last_update_id,
          bids=depth_bids,
          asks=depth_asks,
        )
        self._local_order_books[order_book_key] = local_book
        order_book_state = "streaming"
        order_book_last_update_id = local_book.last_update_id
        order_book_rebuild_count = local_book.rebuild_count
        order_book_last_rebuilt_at = local_book.rebuilt_at
        order_book_bid_level_count = local_book.bid_level_count
        order_book_ask_level_count = local_book.ask_level_count
        order_book_best_bid_price, order_book_best_bid_quantity = local_book.best_bid
        order_book_best_ask_price, order_book_best_ask_quantity = local_book.best_ask
        order_book_bids = _serialize_order_book_side(local_book.bids, reverse=True)
        order_book_asks = _serialize_order_book_side(local_book.asks, reverse=False)
        event_count += 1
        last_event_at = event_at
        continue
      if event_type == "kline":
        last_market_event_at = event_at
        last_kline_event_at = event_at
        kline_snapshot = _build_kline_snapshot_from_stream_event(
          event=event,
          timeframe=handoff.timeframe or "5m",
          fallback_event_at=event_at,
        )
        channel_continuation_state = "streaming"
        channel_last_continued_at = event_at
        event_count += 1
        last_event_at = event_at
        continue
      result, event_issues = self._build_order_result_from_stream_event(
        event=event,
        fallback_symbol=handoff.symbol or "",
      )
      if result is not None:
        self._order_states[result.order_id] = result
        event_count += 1
        last_event_at = result.updated_at or result.submitted_at or last_event_at
      issues.extend(event_issues)

    if failover_reason is not None and handoff.state != "released":
      failover = self._failover_stream_session(
        session_id=session_id,
        symbol=handoff.symbol or "",
        timeframe=handoff.timeframe or "5m",
        current_issues=tuple(issues),
        reason=failover_reason,
      )
      stream_session = failover["session"]
      issues = list(failover["issues"])
      if stream_session is None:
        supervision_state = "reconnect_failed"
        order_book_state = "unavailable"
      else:
        session_id = stream_session.session_id
        supervision_state = self._supervision_state_for_transport(stream_session.transport)
        coverage = self._coverage_for_transport(stream_session.transport)
        failover_count += 1
        last_failover_at = current_time
        order_book_gap_count += 1
        rebuild = self._rebuild_local_order_book_from_snapshot(
          symbol=handoff.symbol or "",
          order_book_key=order_book_key,
          rebuild_count=order_book_rebuild_count,
          reason=failover_reason,
        )
        local_book = rebuild["book"]
        order_book_state = str(rebuild["state"])
        order_book_last_update_id = rebuild["last_update_id"]
        order_book_rebuild_count = rebuild["rebuild_count"]
        order_book_last_rebuilt_at = rebuild["rebuilt_at"]
        order_book_bid_level_count = rebuild["bid_level_count"]
        order_book_ask_level_count = rebuild["ask_level_count"]
        order_book_best_bid_price = rebuild["best_bid_price"]
        order_book_best_bid_quantity = rebuild["best_bid_quantity"]
        order_book_best_ask_price = rebuild["best_ask_price"]
        order_book_best_ask_quantity = rebuild["best_ask_quantity"]
        order_book_bids = rebuild["bids"]
        order_book_asks = rebuild["asks"]
        channel_restore = self._restore_market_channels_from_exchange(
          symbol=handoff.symbol or "",
          timeframe=handoff.timeframe or "5m",
          reason=failover_reason,
        )
        channel_restore_state = str(channel_restore["state"])
        if channel_restore["restored_at"] is not None:
          channel_restore_count += 1
          channel_last_restored_at = channel_restore["restored_at"]
          channel_continuation_state = "restored_from_exchange"
          channel_continuation_count += 1
          channel_last_continued_at = channel_restore["restored_at"]
          trade_snapshot = channel_restore["trade_snapshot"] or trade_snapshot
          aggregate_trade_snapshot = channel_restore["aggregate_trade_snapshot"] or aggregate_trade_snapshot
          book_ticker_snapshot = channel_restore["book_ticker_snapshot"] or book_ticker_snapshot
          mini_ticker_snapshot = channel_restore["mini_ticker_snapshot"] or mini_ticker_snapshot
          kline_snapshot = channel_restore["kline_snapshot"] or kline_snapshot
        last_market_event_at = _max_datetime(last_market_event_at, channel_restore["last_market_event_at"])
        last_trade_event_at = _max_datetime(last_trade_event_at, channel_restore["last_trade_event_at"])
        last_aggregate_trade_event_at = _max_datetime(
          last_aggregate_trade_event_at,
          channel_restore["last_aggregate_trade_event_at"],
        )
        last_book_ticker_event_at = _max_datetime(
          last_book_ticker_event_at,
          channel_restore["last_book_ticker_event_at"],
        )
        last_mini_ticker_event_at = _max_datetime(
          last_mini_ticker_event_at,
          channel_restore["last_mini_ticker_event_at"],
        )
        last_kline_event_at = _max_datetime(last_kline_event_at, channel_restore["last_kline_event_at"])
        if order_book_best_bid_price is None and channel_restore["best_bid_price"] is not None:
          order_book_best_bid_price = channel_restore["best_bid_price"]
        if order_book_best_bid_quantity is None and channel_restore["best_bid_quantity"] is not None:
          order_book_best_bid_quantity = channel_restore["best_bid_quantity"]
        if order_book_best_ask_price is None and channel_restore["best_ask_price"] is not None:
          order_book_best_ask_price = channel_restore["best_ask_price"]
        if order_book_best_ask_quantity is None and channel_restore["best_ask_quantity"] is not None:
          order_book_best_ask_quantity = channel_restore["best_ask_quantity"]
        issues.extend(tuple(rebuild["issues"]))
        issues.extend(tuple(channel_restore["issues"]))
        event_count += 1

    resolved_transport = stream_session.transport if stream_session is not None else handoff.transport
    if self._is_polling_transport(resolved_transport):
      synced_orders = self.sync_order_states(
        symbol=handoff.symbol or "",
        order_ids=order_ids,
      )
    else:
      synced_orders = tuple(self._build_synced_orders_from_state(symbol=handoff.symbol or "", order_ids=order_ids))
    open_orders = self._build_open_orders_from_state(symbol=handoff.symbol or "")
    active_order_count = len(open_orders)
    next_state = "active" if handoff.state != "released" else "released"
    if stream_session is None and next_state != "released":
      next_state = "unavailable"
    next_handoff = GuardedLiveVenueSessionHandoff(
      state=next_state,
      handed_off_at=handoff.handed_off_at,
      released_at=handoff.released_at,
      source=self._source_for_transport(resolved_transport) or handoff.source or "venue_stream_transport",
      venue=handoff.venue or self._venue,
      symbol=handoff.symbol,
      timeframe=handoff.timeframe,
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      venue_session_id=session_id or handoff.venue_session_id,
      transport=resolved_transport or handoff.transport or "binance_multi_stream_websocket",
      cursor=self._advance_event_cursor(handoff.cursor, increment=event_count),
      last_event_at=last_event_at,
      last_sync_at=current_time,
      supervision_state=(
        "released"
        if next_state == "released"
        else supervision_state
      ),
      order_book_state=(
        "released"
        if next_state == "released"
        else "unavailable" if next_state == "unavailable" else order_book_state
      ),
      order_book_last_update_id=order_book_last_update_id,
      order_book_gap_count=order_book_gap_count,
      order_book_rebuild_count=order_book_rebuild_count,
      order_book_last_rebuilt_at=order_book_last_rebuilt_at,
      order_book_bid_level_count=order_book_bid_level_count,
      order_book_ask_level_count=order_book_ask_level_count,
      order_book_best_bid_price=order_book_best_bid_price,
      order_book_best_bid_quantity=order_book_best_bid_quantity,
      order_book_best_ask_price=order_book_best_ask_price,
      order_book_best_ask_quantity=order_book_best_ask_quantity,
      order_book_bids=order_book_bids,
      order_book_asks=order_book_asks,
      channel_restore_state=channel_restore_state,
      channel_restore_count=channel_restore_count,
      channel_last_restored_at=channel_last_restored_at,
      channel_continuation_state=(
        "released"
        if next_state == "released"
        else "unavailable" if next_state == "unavailable" else channel_continuation_state
      ),
      channel_continuation_count=channel_continuation_count,
      channel_last_continued_at=channel_last_continued_at,
      trade_snapshot=trade_snapshot,
      aggregate_trade_snapshot=aggregate_trade_snapshot,
      book_ticker_snapshot=book_ticker_snapshot,
      mini_ticker_snapshot=mini_ticker_snapshot,
      kline_snapshot=kline_snapshot,
      failover_count=failover_count,
      last_failover_at=last_failover_at,
      coverage=coverage,
      last_market_event_at=last_market_event_at,
      last_depth_event_at=last_depth_event_at,
      last_kline_event_at=last_kline_event_at,
      last_aggregate_trade_event_at=last_aggregate_trade_event_at,
      last_mini_ticker_event_at=last_mini_ticker_event_at,
      last_account_event_at=last_account_event_at,
      last_balance_event_at=last_balance_event_at,
      last_order_list_event_at=last_order_list_event_at,
      last_trade_event_at=last_trade_event_at,
      last_book_ticker_event_at=last_book_ticker_event_at,
      active_order_count=active_order_count,
      issues=tuple(dict.fromkeys(issues)),
    )
    return GuardedLiveVenueSessionSync(
      state=next_handoff.state,
      synced_at=current_time,
      handoff=next_handoff,
      synced_orders=synced_orders,
      open_orders=open_orders,
      issues=next_handoff.issues,
    )

  def release_session(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveVenueSessionHandoff:
    current_time = self._clock()
    session_id = handoff.venue_session_id or ""
    order_book_key = self._resolve_order_book_key(
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      session_id=session_id,
      symbol=handoff.symbol,
    )
    stream_session = self._active_stream_sessions.pop(session_id, None)
    self._local_order_books.pop(order_book_key, None)
    issues: tuple[str, ...] = handoff.issues
    if stream_session is not None:
      try:
        stream_session.close()
      except Exception as exc:
        issues = tuple(
          dict.fromkeys(
            (
              *issues,
              f"{self._stream_issue_prefix_for_transport(stream_session.transport)}_close_failed:{exc}",
            )
          )
        )
    return GuardedLiveVenueSessionHandoff(
      state="released",
      handed_off_at=handoff.handed_off_at,
      released_at=current_time,
      source=handoff.source or self._source_for_transport(handoff.transport) or "venue_stream_transport",
      venue=handoff.venue or self._venue,
      symbol=handoff.symbol,
      timeframe=handoff.timeframe,
      owner_run_id=handoff.owner_run_id,
      owner_session_id=handoff.owner_session_id,
      venue_session_id=handoff.venue_session_id,
      transport=handoff.transport or "binance_multi_stream_websocket",
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
      issues=issues,
    )

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

  def _resolve_stream_clients(self, *, symbol: str, timeframe: str) -> tuple[BinanceVenueStreamClient, ...]:
    clients: list[BinanceVenueStreamClient] = []
    if self._venue_stream_client is not None:
      clients.append(self._venue_stream_client)
    elif self._api_key and symbol and timeframe:
      try:
        clients.append(
          BinanceCombinedWebSocketVenueStreamClient(
            api_key=self._api_key,
            symbol=symbol,
            timeframe=timeframe,
            clock=self._clock,
          )
        )
      except Exception:
        pass
    if symbol and timeframe:
      polling_client = self._resolve_polling_stream_client(symbol=symbol, timeframe=timeframe)
      if polling_client is not None:
        clients.append(polling_client)
    return tuple(clients)

  def _resolve_polling_stream_client(self, *, symbol: str, timeframe: str) -> BinanceVenueStreamClient | None:
    if not symbol or not timeframe:
      return None
    try:
      exchange = self._resolve_exchange()
    except Exception:
      return None
    return GenericPollingVenueStreamClient(
      venue=self._venue,
      exchange=exchange,
      symbol=symbol,
      timeframe=timeframe,
      clock=self._clock,
      poll_interval_seconds=self._poll_interval_seconds,
    )

  def _open_stream_session(
    self,
    *,
    symbol: str,
    timeframe: str,
    current_issues: tuple[str, ...],
  ) -> dict[str, object]:
    issues = list(current_issues)
    for client in self._resolve_stream_clients(symbol=symbol, timeframe=timeframe):
      try:
        session = client.open_session()
      except Exception as exc:
        issues.append(
          f"{self._stream_issue_prefix_for_transport(getattr(client, 'transport', None))}_open_failed:{exc}"
        )
        continue
      self._active_stream_sessions[session.session_id] = session
      if self._is_polling_transport(session.transport):
        issues.append(f"venue_stream_transport_fallback:{session.transport}")
      return {
        "session": session,
        "issues": tuple(dict.fromkeys(issues)),
      }
    if not issues:
      issues.append("venue_stream_unavailable")
    return {
      "session": None,
      "issues": tuple(dict.fromkeys(issues)),
    }

  def _record_restore_state(self, restore: GuardedLiveVenueSessionRestore) -> None:
    for result in restore.synced_orders:
      if result.status == "unknown":
        continue
      self._order_states[result.order_id] = result

  def _failover_stream_session(
    self,
    *,
    session_id: str,
    symbol: str,
    timeframe: str,
    current_issues: tuple[str, ...],
    reason: str,
  ) -> dict[str, object]:
    issues = list(current_issues)
    previous_session = self._active_stream_sessions.pop(session_id, None)
    if previous_session is not None:
      try:
        previous_session.close()
      except Exception as exc:
        issues.append(f"{self._stream_issue_prefix_for_transport(previous_session.transport)}_close_failed:{exc}")
    opened = self._open_stream_session(
      symbol=symbol,
      timeframe=timeframe,
      current_issues=tuple(issues),
    )
    replacement = opened["session"]
    next_issues = list(opened["issues"])
    if replacement is None:
      next_issues.append(f"venue_stream_failover_failed:{reason}:stream_unavailable")
      return {
        "session": None,
        "issues": tuple(dict.fromkeys(next_issues)),
      }
    return {
      "session": replacement,
      "issues": tuple(dict.fromkeys(next_issues)),
    }

  @staticmethod
  def _coverage_for_transport(transport: str | None) -> tuple[str, ...]:
    if transport == "generic_ccxt_polling_transport":
      return GENERIC_POLLING_VENUE_STREAM_COVERAGE
    if transport in {
      "binance_multi_stream_websocket",
      "binance_user_data_websocket",
      "binance_market_data_websocket",
    }:
      return BINANCE_VENUE_STREAM_COVERAGE
    if transport in {None, "venue_stream_unavailable"}:
      return ()
    return BINANCE_VENUE_STREAM_COVERAGE

  @staticmethod
  def _supervision_state_for_transport(transport: str | None) -> str:
    if transport == "generic_ccxt_polling_transport":
      return "polling"
    if transport in {"binance_multi_stream_websocket", "binance_user_data_websocket", "binance_market_data_websocket"}:
      return "streaming"
    return "inactive"

  @staticmethod
  def _is_polling_transport(transport: str | None) -> bool:
    return transport == "generic_ccxt_polling_transport"

  @staticmethod
  def _source_for_transport(transport: str | None) -> str:
    if transport == "generic_ccxt_polling_transport":
      return "venue_polling_transport"
    if transport in {"binance_multi_stream_websocket", "binance_user_data_websocket", "binance_market_data_websocket"}:
      return "binance_venue_stream"
    return "venue_stream_transport"

  @staticmethod
  def _stream_issue_prefix_for_transport(transport: str | None) -> str:
    if transport == "generic_ccxt_polling_transport":
      return "generic_venue_stream"
    if transport in {"binance_multi_stream_websocket", "binance_user_data_websocket", "binance_market_data_websocket"}:
      return "binance_venue_stream"
    return "venue_stream"

  @staticmethod
  def _resolve_order_book_key(
    *,
    owner_run_id: str | None,
    owner_session_id: str | None,
    session_id: str | None,
    symbol: str | None,
  ) -> str:
    return owner_run_id or owner_session_id or session_id or symbol or "guarded-live-order-book"

  def _rebuild_local_order_book_from_snapshot(
    self,
    *,
    symbol: str,
    order_book_key: str,
    rebuild_count: int,
    reason: str,
  ) -> dict[str, object]:
    current_time = self._clock()
    if not symbol:
      return {
        "book": None,
        "state": "rebuild_failed",
        "issues": ("binance_order_book_snapshot_failed:missing_symbol",),
        "last_update_id": None,
        "rebuild_count": rebuild_count,
        "rebuilt_at": None,
        "bid_level_count": 0,
        "ask_level_count": 0,
        "best_bid_price": None,
        "best_bid_quantity": None,
        "best_ask_price": None,
        "best_ask_quantity": None,
        "bids": (),
        "asks": (),
      }
    try:
      exchange = self._resolve_exchange()
      snapshot = exchange.fetch_order_book(symbol, 20, {})
      book = _build_local_order_book_from_snapshot_row(
        symbol=symbol,
        row=snapshot,
        rebuilt_at=current_time,
        rebuild_count=rebuild_count + 1,
      )
    except Exception as exc:
      return {
        "book": None,
        "state": "rebuild_failed",
        "issues": (f"binance_order_book_snapshot_failed:{reason}:{exc}",),
        "last_update_id": None,
        "rebuild_count": rebuild_count,
        "rebuilt_at": None,
        "bid_level_count": 0,
        "ask_level_count": 0,
        "best_bid_price": None,
        "best_bid_quantity": None,
        "best_ask_price": None,
        "best_ask_quantity": None,
        "bids": (),
        "asks": (),
      }
    self._local_order_books[order_book_key] = book
    best_bid_price, best_bid_quantity = book.best_bid
    best_ask_price, best_ask_quantity = book.best_ask
    return {
      "book": book,
      "state": "snapshot_rebuilt",
      "issues": (),
      "last_update_id": book.last_update_id,
      "rebuild_count": book.rebuild_count,
      "rebuilt_at": book.rebuilt_at,
      "bid_level_count": book.bid_level_count,
      "ask_level_count": book.ask_level_count,
      "best_bid_price": best_bid_price,
      "best_bid_quantity": best_bid_quantity,
      "best_ask_price": best_ask_price,
      "best_ask_quantity": best_ask_quantity,
      "bids": _serialize_order_book_side(book.bids, reverse=True),
      "asks": _serialize_order_book_side(book.asks, reverse=False),
    }

  def _restore_local_order_book_from_handoff(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    order_book_key: str,
  ) -> LocalOrderBookState | None:
    if not handoff.symbol:
      return None
    if not handoff.order_book_bids and not handoff.order_book_asks:
      return None
    bids = {level.price: level.quantity for level in handoff.order_book_bids}
    asks = {level.price: level.quantity for level in handoff.order_book_asks}
    book = LocalOrderBookState(
      symbol=handoff.symbol,
      last_update_id=handoff.order_book_last_update_id,
      rebuilt_at=handoff.order_book_last_rebuilt_at or self._clock(),
      rebuild_count=handoff.order_book_rebuild_count,
      bids=bids,
      asks=asks,
    )
    self._local_order_books[order_book_key] = book
    return book

  @staticmethod
  def _handoff_has_channel_snapshots(handoff: GuardedLiveVenueSessionHandoff) -> bool:
    return any(
      snapshot is not None
      for snapshot in (
        handoff.trade_snapshot,
        handoff.aggregate_trade_snapshot,
        handoff.book_ticker_snapshot,
        handoff.mini_ticker_snapshot,
        handoff.kline_snapshot,
      )
    )

  def _restore_market_channels_from_exchange(
    self,
    *,
    symbol: str,
    timeframe: str,
    reason: str,
  ) -> dict[str, object]:
    current_time = self._clock()
    if not symbol:
      return {
        "state": "unavailable",
        "issues": ("binance_market_channel_restore_failed:missing_symbol",),
        "restored_at": None,
        "last_market_event_at": None,
        "last_trade_event_at": None,
        "last_aggregate_trade_event_at": None,
        "last_book_ticker_event_at": None,
        "last_mini_ticker_event_at": None,
        "last_kline_event_at": None,
        "best_bid_price": None,
        "best_bid_quantity": None,
        "best_ask_price": None,
        "best_ask_quantity": None,
        "trade_snapshot": None,
        "aggregate_trade_snapshot": None,
        "book_ticker_snapshot": None,
        "mini_ticker_snapshot": None,
        "kline_snapshot": None,
      }
    issues: list[str] = []
    restored_any = False
    last_market_event_at: datetime | None = None
    last_trade_event_at: datetime | None = None
    last_aggregate_trade_event_at: datetime | None = None
    last_book_ticker_event_at: datetime | None = None
    last_mini_ticker_event_at: datetime | None = None
    last_kline_event_at: datetime | None = None
    best_bid_price: float | None = None
    best_bid_quantity: float | None = None
    best_ask_price: float | None = None
    best_ask_quantity: float | None = None
    trade_snapshot: GuardedLiveTradeChannelSnapshot | None = None
    aggregate_trade_snapshot: GuardedLiveTradeChannelSnapshot | None = None
    book_ticker_snapshot: GuardedLiveBookTickerChannelSnapshot | None = None
    mini_ticker_snapshot: GuardedLiveMiniTickerChannelSnapshot | None = None
    kline_snapshot: GuardedLiveKlineChannelSnapshot | None = None
    try:
      exchange = self._resolve_exchange()
    except Exception as exc:
      return {
        "state": "unavailable",
        "issues": (f"binance_market_channel_restore_failed:{reason}:{exc}",),
        "restored_at": None,
        "last_market_event_at": None,
        "last_trade_event_at": None,
        "last_aggregate_trade_event_at": None,
        "last_book_ticker_event_at": None,
        "last_mini_ticker_event_at": None,
        "last_kline_event_at": None,
        "best_bid_price": None,
        "best_bid_quantity": None,
        "best_ask_price": None,
        "best_ask_quantity": None,
        "trade_snapshot": None,
        "aggregate_trade_snapshot": None,
        "book_ticker_snapshot": None,
        "mini_ticker_snapshot": None,
        "kline_snapshot": None,
      }
    try:
      ticker = exchange.fetch_ticker(symbol, {})
      ticker_at = _coerce_datetime(ticker.get("datetime"), ticker.get("timestamp")) or current_time
      last_market_event_at = ticker_at
      last_book_ticker_event_at = ticker_at
      last_mini_ticker_event_at = ticker_at
      best_bid_price = _coerce_float(ticker.get("bid"))
      best_bid_quantity = _coerce_float(ticker.get("bidVolume"))
      best_ask_price = _coerce_float(ticker.get("ask"))
      best_ask_quantity = _coerce_float(ticker.get("askVolume"))
      book_ticker_snapshot = _build_book_ticker_snapshot_from_ticker_row(
        ticker,
        fallback_event_at=ticker_at,
      )
      mini_ticker_snapshot = _build_mini_ticker_snapshot_from_ticker_row(
        ticker,
        fallback_event_at=ticker_at,
      )
      restored_any = True
    except Exception as exc:
      issues.append(f"binance_market_channel_restore_failed:ticker:{reason}:{exc}")
    try:
      trades = exchange.fetch_trades(symbol, None, 1, {})
      if trades:
        trade = trades[-1]
        trade_at = _coerce_datetime(trade.get("datetime"), trade.get("timestamp")) or current_time
        last_trade_event_at = trade_at
        last_aggregate_trade_event_at = trade_at
        last_market_event_at = _max_datetime(last_market_event_at, trade_at)
        trade_snapshot = _build_trade_snapshot_from_exchange_trade_row(
          trade,
          fallback_event_at=trade_at,
        )
        aggregate_trade_snapshot = trade_snapshot
        restored_any = True
    except Exception as exc:
      issues.append(f"binance_market_channel_restore_failed:trades:{reason}:{exc}")
    try:
      candles = exchange.fetch_ohlcv(symbol, timeframe, None, 1, {})
      if candles:
        candle_at = _coerce_ohlcv_timestamp(candles[-1][0], timeframe=timeframe) or current_time
        last_kline_event_at = candle_at
        last_market_event_at = _max_datetime(last_market_event_at, candle_at)
        kline_snapshot = _build_kline_snapshot_from_ohlcv_row(
          candles[-1],
          timeframe=timeframe,
          fallback_event_at=current_time,
        )
        restored_any = True
    except Exception as exc:
      issues.append(f"binance_market_channel_restore_failed:ohlcv:{reason}:{exc}")
    return {
      "state": "restored_from_exchange" if restored_any and not issues else ("partial" if restored_any else "unavailable"),
      "issues": tuple(issues),
      "restored_at": current_time if restored_any else None,
      "last_market_event_at": last_market_event_at,
      "last_trade_event_at": last_trade_event_at,
      "last_aggregate_trade_event_at": last_aggregate_trade_event_at,
      "last_book_ticker_event_at": last_book_ticker_event_at,
      "last_mini_ticker_event_at": last_mini_ticker_event_at,
      "last_kline_event_at": last_kline_event_at,
      "best_bid_price": best_bid_price,
      "best_bid_quantity": best_bid_quantity,
      "best_ask_price": best_ask_price,
      "best_ask_quantity": best_ask_quantity,
      "trade_snapshot": trade_snapshot,
      "aggregate_trade_snapshot": aggregate_trade_snapshot,
      "book_ticker_snapshot": book_ticker_snapshot,
      "mini_ticker_snapshot": mini_ticker_snapshot,
      "kline_snapshot": kline_snapshot,
    }

  @staticmethod
  def _apply_depth_update_to_local_book(
    *,
    book: LocalOrderBookState,
    last_update_id: int | None,
    bids: tuple[tuple[float, float], ...],
    asks: tuple[tuple[float, float], ...],
  ) -> LocalOrderBookState:
    for price, quantity in bids:
      if quantity <= 0:
        book.bids.pop(price, None)
      else:
        book.bids[price] = quantity
    for price, quantity in asks:
      if quantity <= 0:
        book.asks.pop(price, None)
      else:
        book.asks[price] = quantity
    if last_update_id is not None:
      book.last_update_id = last_update_id
    return book

  @staticmethod
  def _filter_venue_stream_issues(issues: tuple[str, ...]) -> list[str]:
    return [
      issue
      for issue in issues
      if not issue.startswith("binance_venue_stream")
      and not issue.startswith("binance_user_data_stream")
      and not issue.startswith("generic_venue_stream")
      and not issue.startswith("venue_stream_failover_failed")
    ]

  @staticmethod
  def _coerce_stream_event_at(event: dict[str, Any]) -> datetime | None:
    return (
      _coerce_datetime(None, event.get("E"))
      or _coerce_datetime(None, event.get("_received_at_ms"))
      or _coerce_datetime(None, event.get("T"))
      or _coerce_datetime(None, event.get("u"))
      or _coerce_datetime(None, _extract_nested_value(event, ("k", "T")))
      or _coerce_datetime(None, _extract_nested_value(event, ("k", "t")))
    )

  def _build_synced_orders_from_state(
    self,
    *,
    symbol: str,
    order_ids: tuple[str, ...],
  ) -> list[GuardedLiveVenueOrderResult]:
    current_time = self._clock()
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
            submitted_at=current_time,
            updated_at=current_time,
            issues=("order_state_unavailable",),
          )
        )
        continue
      results.append(state)
    return results

  def _build_open_orders_from_state(
    self,
    *,
    symbol: str,
  ) -> tuple[GuardedLiveVenueOpenOrder, ...]:
    return tuple(
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
          for result in self._order_states.values()
          if result.symbol == symbol
          and result.status in {"open", "partially_filled"}
          and (result.remaining_amount is None or result.remaining_amount > 0)
        ),
        key=lambda order: (order.symbol, order.order_id),
      )
    )

  def _build_order_result_from_stream_event(
    self,
    *,
    event: dict[str, Any],
    fallback_symbol: str,
  ) -> tuple[GuardedLiveVenueOrderResult | None, tuple[str, ...]]:
    event_type = str(event.get("e") or "")
    if event_type != "executionReport":
      return None, ()
    submitted_at = _coerce_datetime(None, event.get("O") or event.get("E")) or self._clock()
    updated_at = _coerce_datetime(None, event.get("T") or event.get("E")) or submitted_at
    requested_amount = _coerce_float(event.get("q")) or 0.0
    filled_amount = _coerce_float(event.get("z")) or 0.0
    remaining_amount = max(requested_amount - filled_amount, 0.0)
    raw_status = str(event.get("X") or event.get("x") or "").lower()
    price = _coerce_float(event.get("p"))
    cumulative_quote = _coerce_float(event.get("Z"))
    average_fill_price = None
    if cumulative_quote is not None and filled_amount > 0:
      average_fill_price = cumulative_quote / filled_amount
    elif _coerce_float(event.get("L")) is not None and filled_amount > 0:
      average_fill_price = _coerce_float(event.get("L"))
    status = _normalize_order_status(
      raw_status=raw_status,
      requested_amount=requested_amount,
      filled_amount=filled_amount,
      remaining_amount=remaining_amount,
    )
    result = GuardedLiveVenueOrderResult(
      order_id=str(event.get("i") or event.get("c") or f"binance-stream-order:{submitted_at.isoformat()}"),
      venue=self._venue,
      symbol=fallback_symbol,
      side=str(event.get("S") or "unknown").lower(),
      amount=filled_amount if status == "filled" else requested_amount,
      status=status,
      submitted_at=submitted_at,
      updated_at=updated_at,
      requested_price=price,
      average_fill_price=average_fill_price,
      fee_paid=_coerce_float(event.get("n")),
      requested_amount=requested_amount,
      filled_amount=filled_amount,
      remaining_amount=remaining_amount,
    )
    return result, ()

  @staticmethod
  def _advance_event_cursor(cursor: str | None, *, increment: int) -> str:
    if cursor is None or not cursor.startswith("event-"):
      current = 0
    else:
      try:
        current = int(cursor.split("-", 1)[1])
      except (IndexError, ValueError):
        current = 0
    return f"event-{current + increment}"

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


def _normalize_binance_stream_symbol(symbol: str) -> str:
  return symbol.replace("/", "").replace("-", "").lower()


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
