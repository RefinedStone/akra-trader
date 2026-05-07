from __future__ import annotations

from akra_trader.adapters.venue_execution_common import *
from akra_trader.adapters.venue_execution_common import _drain_stream_event_queue
from akra_trader.adapters.venue_execution_common import _normalize_binance_stream_symbol

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
    return _drain_stream_event_queue(self._events)

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
    return _drain_stream_event_queue(self._events)

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
BINANCE_MARKET_PUSH_VENUE_STREAM_COVERAGE = (
  "order_state_snapshots",
  *BINANCE_MARKET_STREAM_COVERAGE,
)
BINANCE_VENUE_STREAM_COVERAGE = (
  *BINANCE_USER_DATA_STREAM_COVERAGE,
  *BINANCE_MARKET_STREAM_COVERAGE,
)
COINBASE_ADVANCED_TRADE_MARKET_STREAM_COVERAGE = (
  "order_state_snapshots",
  "heartbeat_events",
  "trade_ticks",
  "aggregate_trade_ticks",
  "book_ticker",
  "mini_ticker",
  "depth_updates",
  "kline_candles",
  "order_book_lifecycle",
)
COINBASE_ADVANCED_TRADE_USER_STREAM_COVERAGE = (
  "execution_reports",
  "account_positions",
  "heartbeat_events",
)
COINBASE_ADVANCED_TRADE_VENUE_STREAM_COVERAGE = tuple(
  dict.fromkeys(
    (
      *COINBASE_ADVANCED_TRADE_USER_STREAM_COVERAGE,
      *COINBASE_ADVANCED_TRADE_MARKET_STREAM_COVERAGE,
    )
  )
)
