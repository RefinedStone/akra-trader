from __future__ import annotations

from akra_trader.adapters.venue_execution_common import *
from akra_trader.adapters.venue_execution_common import _build_coinbase_websocket_jwt
from akra_trader.adapters.venue_execution_common import _coerce_datetime
from akra_trader.adapters.venue_execution_common import _coerce_float
from akra_trader.adapters.venue_execution_common import _coerce_int
from akra_trader.adapters.venue_execution_common import _coerce_ohlcv_close_timestamp
from akra_trader.adapters.venue_execution_common import _coerce_ohlcv_timestamp
from akra_trader.adapters.venue_execution_common import _coerce_string
from akra_trader.adapters.venue_execution_common import _drain_stream_event_queue
from akra_trader.adapters.venue_execution_common import _max_datetime
from akra_trader.adapters.venue_execution_common import _normalize_coinbase_product_id
from akra_trader.adapters.venue_execution_common import _sanitize_coinbase_zero_time


def _coinbase_websocket_jwt(
  *,
  api_key: str,
  signing_key: str,
  current_time: datetime,
) -> str:
  try:
    from akra_trader.adapters import venue_execution
  except Exception:
    return _build_coinbase_websocket_jwt(
      api_key=api_key,
      signing_key=signing_key,
      current_time=current_time,
    )
  builder = getattr(venue_execution, "_build_coinbase_websocket_jwt", _build_coinbase_websocket_jwt)
  return builder(api_key=api_key, signing_key=signing_key, current_time=current_time)

class CoinbaseAdvancedTradeWebSocketMarketStreamSession:
  transport = "coinbase_advanced_trade_market_websocket"

  def __init__(
    self,
    *,
    session_id: str,
    websocket_url: str,
    product_id: str,
    timeframe: str,
    clock: Callable[[], datetime],
  ) -> None:
    self.session_id = session_id
    self._websocket_url = websocket_url
    self._product_id = product_id
    self._timeframe = timeframe
    self._clock = clock
    self._events: Queue[dict[str, Any]] = Queue()
    self._closed = False
    self._reader_stop = threading.Event()
    self._last_level2_sequence_num: int | None = None
    self._connect = self._resolve_connect()
    self._connection = self._connect(self._websocket_url)
    self._subscribe()
    self._reader = threading.Thread(
      target=self._reader_loop,
      name=f"coinbase-market-stream-{session_id}",
      daemon=True,
    )
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

  def _subscribe(self) -> None:
    subscription_messages = (
      {"type": "subscribe", "channel": "heartbeats"},
      {"type": "subscribe", "channel": "ticker", "product_ids": [self._product_id]},
      {"type": "subscribe", "channel": "market_trades", "product_ids": [self._product_id]},
      {"type": "subscribe", "channel": "level2", "product_ids": [self._product_id]},
      {"type": "subscribe", "channel": "candles", "product_ids": [self._product_id]},
    )
    for message in subscription_messages:
      self._connection.send(json.dumps(message))

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
      for event in self._normalize_payload(payload):
        self._events.put(event)

  def _normalize_payload(self, payload: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    if str(payload.get("type") or "").lower() == "error":
      return (
        {
          "e": "streamWarning",
          "stream_scope": "market_data",
          "message": str(payload.get("message") or "coinbase_stream_error"),
          "E": int(self._clock().timestamp() * 1000),
        },
      )
    channel = str(payload.get("channel") or "")
    if channel in {"", "subscriptions"}:
      return ()
    received_at = _coerce_datetime(payload.get("timestamp"), None) or self._clock()
    events = payload.get("events")
    if not isinstance(events, list):
      return ()
    sequence_num = _coerce_int(payload.get("sequence_num"))
    normalized: list[dict[str, Any]] = []
    for entry in events:
      if not isinstance(entry, dict):
        continue
      if channel == "heartbeats":
        normalized.append(
          {
            "e": "streamHeartbeat",
            "stream_scope": "market_data",
            "stream": "coinbase@heartbeats",
            "E": int(received_at.timestamp() * 1000),
            "_received_at_ms": int(received_at.timestamp() * 1000),
          }
        )
        continue
      if channel in {"ticker", "ticker_batch"}:
        normalized.extend(
          self._normalize_ticker_entry(
            entry=entry,
            channel=channel,
            received_at=received_at,
          )
        )
        continue
      if channel == "market_trades":
        normalized.extend(self._normalize_trade_entry(entry=entry, received_at=received_at))
        continue
      if channel in {"level2", "l2_data"}:
        normalized.extend(
          self._normalize_level2_entry(
            entry=entry,
            channel=channel,
            received_at=received_at,
            sequence_num=sequence_num,
          )
        )
        continue
      if channel == "candles":
        normalized.extend(self._normalize_candle_entry(entry=entry, received_at=received_at))
    if channel in {"level2", "l2_data"} and sequence_num is not None:
      self._last_level2_sequence_num = sequence_num
    return tuple(normalized)

  def _normalize_ticker_entry(
    self,
    *,
    entry: dict[str, Any],
    channel: str,
    received_at: datetime,
  ) -> tuple[dict[str, Any], ...]:
    rows = entry.get("tickers")
    if not isinstance(rows, list):
      return ()
    normalized: list[dict[str, Any]] = []
    for row in rows:
      if not isinstance(row, dict):
        continue
      event_at = received_at
      best_bid = _coerce_float(row.get("best_bid"))
      best_bid_quantity = _coerce_float(row.get("best_bid_quantity"))
      best_ask = _coerce_float(row.get("best_ask"))
      best_ask_quantity = _coerce_float(row.get("best_ask_quantity"))
      if best_bid is not None or best_ask is not None:
        normalized.append(
          {
            "e": "bookTicker",
            "E": int(event_at.timestamp() * 1000),
            "b": str(row.get("best_bid") or ""),
            "B": str(row.get("best_bid_quantity") or ""),
            "a": str(row.get("best_ask") or ""),
            "A": str(row.get("best_ask_quantity") or ""),
            "stream_scope": "market_data",
            "stream": f"coinbase@{channel}",
            "_received_at_ms": int(received_at.timestamp() * 1000),
          }
        )
      normalized.append(
        {
          "e": "24hrMiniTicker",
          "E": int(event_at.timestamp() * 1000),
          "c": str(row.get("price") or ""),
          "h": str(row.get("high_24_h") or ""),
          "l": str(row.get("low_24_h") or ""),
          "v": str(row.get("volume_24_h") or ""),
          "stream_scope": "market_data",
          "stream": f"coinbase@{channel}",
          "_received_at_ms": int(received_at.timestamp() * 1000),
        }
      )
    return tuple(normalized)

  def _normalize_trade_entry(
    self,
    *,
    entry: dict[str, Any],
    received_at: datetime,
  ) -> tuple[dict[str, Any], ...]:
    rows = entry.get("trades")
    if not isinstance(rows, list):
      return ()
    normalized: list[dict[str, Any]] = []
    for row in rows:
      if not isinstance(row, dict):
        continue
      event_at = _coerce_datetime(row.get("time"), None) or received_at
      event_id = _coerce_string(row.get("trade_id")) or str(int(event_at.timestamp() * 1000))
      normalized.extend(
        (
          {
            "e": "trade",
            "E": int(event_at.timestamp() * 1000),
            "T": int(event_at.timestamp() * 1000),
            "t": event_id,
            "p": str(row.get("price") or ""),
            "q": str(row.get("size") or ""),
            "stream_scope": "market_data",
            "stream": "coinbase@market_trades",
            "_received_at_ms": int(received_at.timestamp() * 1000),
          },
          {
            "e": "aggTrade",
            "E": int(event_at.timestamp() * 1000),
            "T": int(event_at.timestamp() * 1000),
            "a": event_id,
            "p": str(row.get("price") or ""),
            "q": str(row.get("size") or ""),
            "stream_scope": "market_data",
            "stream": "coinbase@market_trades",
            "_received_at_ms": int(received_at.timestamp() * 1000),
          },
        )
      )
    return tuple(normalized)

  def _normalize_level2_entry(
    self,
    *,
    entry: dict[str, Any],
    channel: str,
    received_at: datetime,
    sequence_num: int | None,
  ) -> tuple[dict[str, Any], ...]:
    updates = entry.get("updates")
    if not isinstance(updates, list):
      return ()
    bids: list[list[str]] = []
    asks: list[list[str]] = []
    event_at = received_at
    for update in updates:
      if not isinstance(update, dict):
        continue
      update_at = _coerce_datetime(update.get("event_time"), None)
      event_at = _max_datetime(event_at, update_at) or event_at
      side = str(update.get("side") or "").lower()
      level = [str(update.get("price_level") or ""), str(update.get("new_quantity") or "")]
      if side in {"bid", "buy"}:
        bids.append(level)
      else:
        asks.append(level)
    if not bids and not asks:
      return ()
    return (
      {
        "e": "depthUpdate",
        "E": int(event_at.timestamp() * 1000),
        "U": sequence_num,
        "u": sequence_num,
        "pu": self._last_level2_sequence_num,
        "b": bids,
        "a": asks,
        "_snapshot_depth": str(entry.get("type") or "").lower() == "snapshot",
        "stream_scope": "market_data",
        "stream": f"coinbase@{channel}",
        "_received_at_ms": int(received_at.timestamp() * 1000),
      },
    )

  def _normalize_candle_entry(
    self,
    *,
    entry: dict[str, Any],
    received_at: datetime,
  ) -> tuple[dict[str, Any], ...]:
    candles = entry.get("candles")
    if not isinstance(candles, list):
      return ()
    normalized: list[dict[str, Any]] = []
    for row in candles:
      if not isinstance(row, dict):
        continue
      open_at = _coerce_ohlcv_timestamp(row.get("start"), timeframe=self._timeframe) or received_at
      close_at = _coerce_ohlcv_close_timestamp(row.get("start"), timeframe=self._timeframe) or open_at
      normalized.append(
        {
          "e": "kline",
          "E": int(close_at.timestamp() * 1000),
          "stream_scope": "market_data",
          "stream": f"coinbase@candles_{self._timeframe}",
          "_received_at_ms": int(received_at.timestamp() * 1000),
          "k": {
            "i": self._timeframe,
            "t": int(open_at.timestamp() * 1000),
            "T": int(close_at.timestamp() * 1000),
            "o": str(row.get("open") or ""),
            "h": str(row.get("high") or ""),
            "l": str(row.get("low") or ""),
            "c": str(row.get("close") or ""),
            "v": str(row.get("volume") or ""),
            "x": close_at <= received_at,
          },
        }
      )
    return tuple(normalized)

  @staticmethod
  def _resolve_connect():
    try:
      from websockets.sync.client import connect
    except ImportError as exc:
      raise RuntimeError("websockets_dependency_missing") from exc
    return connect


class CoinbaseAdvancedTradeWebSocketMarketStreamClient:
  transport = "coinbase_advanced_trade_market_websocket"

  def __init__(
    self,
    *,
    symbol: str,
    timeframe: str,
    websocket_url: str = "wss://advanced-trade-ws.coinbase.com",
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._symbol = symbol
    self._timeframe = timeframe
    self._websocket_url = websocket_url
    self._clock = clock or (lambda: datetime.now(UTC))

  def open_session(self) -> BinanceVenueStreamSession:
    return CoinbaseAdvancedTradeWebSocketMarketStreamSession(
      session_id=(
        f"coinbase-market:{_normalize_coinbase_product_id(self._symbol)}:"
        f"heartbeats+ticker+market_trades+level2+candles_{self._timeframe}"
      ),
      websocket_url=self._websocket_url,
      product_id=_normalize_coinbase_product_id(self._symbol),
      timeframe=self._timeframe,
      clock=self._clock,
    )


class CoinbaseAdvancedTradeUserStreamSession:
  transport = "coinbase_advanced_trade_user_websocket"

  def __init__(
    self,
    *,
    session_id: str,
    websocket_url: str,
    api_key: str,
    signing_key: str,
    product_id: str | None,
    clock: Callable[[], datetime],
  ) -> None:
    self.session_id = session_id
    self._websocket_url = websocket_url
    self._api_key = api_key
    self._signing_key = signing_key
    self._product_id = product_id
    self._clock = clock
    self._events: Queue[dict[str, Any]] = Queue()
    self._closed = False
    self._reader_stop = threading.Event()
    self._connect = self._resolve_connect()
    self._connection = self._connect(self._websocket_url)
    self._subscribe()
    self._reader = threading.Thread(
      target=self._reader_loop,
      name=f"coinbase-user-stream-{session_id}",
      daemon=True,
    )
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

  def _subscribe(self) -> None:
    heartbeat_message = {
      "type": "subscribe",
      "channel": "heartbeats",
      "jwt": _coinbase_websocket_jwt(
        api_key=self._api_key,
        signing_key=self._signing_key,
        current_time=self._clock(),
      ),
    }
    user_message: dict[str, Any] = {
      "type": "subscribe",
      "channel": "user",
      "jwt": _coinbase_websocket_jwt(
        api_key=self._api_key,
        signing_key=self._signing_key,
        current_time=self._clock(),
      ),
    }
    if self._product_id is not None:
      user_message["product_ids"] = [self._product_id]
    for message in (heartbeat_message, user_message):
      self._connection.send(json.dumps(message))

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
            "stream_scope": "user_data",
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
            "stream_scope": "user_data",
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
            "stream_scope": "user_data",
            "message": f"invalid_json:{exc}",
            "E": int(self._clock().timestamp() * 1000),
          }
        )
        continue
      for event in self._normalize_payload(payload):
        self._events.put(event)

  def _normalize_payload(self, payload: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    channel = str(payload.get("channel") or "")
    if str(payload.get("type") or "").lower() == "error":
      return (
        {
          "e": "streamWarning",
          "stream_scope": "user_data",
          "message": str(payload.get("message") or "coinbase_user_stream_error"),
          "E": int(self._clock().timestamp() * 1000),
        },
      )
    if channel in {"", "subscriptions"}:
      return ()
    if channel == "heartbeats":
      received_at = _coerce_datetime(payload.get("timestamp"), None) or self._clock()
      return (
        {
          "e": "streamHeartbeat",
          "stream_scope": "user_data",
          "stream": "coinbase@user_heartbeats",
          "E": int(received_at.timestamp() * 1000),
          "_received_at_ms": int(received_at.timestamp() * 1000),
        },
      )
    if channel != "user":
      return ()
    received_at = _coerce_datetime(payload.get("timestamp"), None) or self._clock()
    events = payload.get("events")
    if not isinstance(events, list):
      return ()
    normalized: list[dict[str, Any]] = []
    for entry in events:
      if not isinstance(entry, dict):
        continue
      normalized.extend(self._normalize_user_event(entry=entry, received_at=received_at))
    return tuple(normalized)

  def _normalize_user_event(
    self,
    *,
    entry: dict[str, Any],
    received_at: datetime,
  ) -> tuple[dict[str, Any], ...]:
    normalized: list[dict[str, Any]] = []
    orders = entry.get("orders")
    if isinstance(orders, list):
      for row in orders:
        if not isinstance(row, dict):
          continue
        created_at = (
          _coerce_datetime(_sanitize_coinbase_zero_time(row.get("creation_time")), None)
          or received_at
        )
        updated_at = (
          _coerce_datetime(_sanitize_coinbase_zero_time(row.get("end_time")), None)
          or received_at
        )
        filled_amount = _coerce_float(row.get("cumulative_quantity")) or 0.0
        remaining_amount = _coerce_float(row.get("leaves_quantity"))
        requested_amount = (
          filled_amount + remaining_amount
          if remaining_amount is not None
          else _coerce_float(row.get("base_size"))
          or filled_amount
        )
        normalized.append(
          {
            "e": "executionReport",
            "E": int(received_at.timestamp() * 1000),
            "O": int(created_at.timestamp() * 1000),
            "T": int(updated_at.timestamp() * 1000),
            "i": str(row.get("order_id") or row.get("client_order_id") or ""),
            "c": str(row.get("client_order_id") or ""),
            "S": str(row.get("order_side") or "unknown").upper(),
            "q": str(requested_amount),
            "z": str(filled_amount),
            "p": str(row.get("limit_price") or row.get("avg_price") or ""),
            "L": str(row.get("avg_price") or ""),
            "X": str(row.get("status") or ""),
            "Z": str(row.get("filled_value") or ""),
            "n": str(row.get("total_fees") or ""),
            "stream_scope": "user_data",
            "stream": "coinbase@user",
            "_received_at_ms": int(received_at.timestamp() * 1000),
          }
        )
    positions = entry.get("positions")
    if positions not in (None, {}, [], ()):
      normalized.append(
        {
          "e": "outboundAccountPosition",
          "E": int(received_at.timestamp() * 1000),
          "stream_scope": "user_data",
          "stream": "coinbase@user",
          "_received_at_ms": int(received_at.timestamp() * 1000),
        }
      )
    return tuple(normalized)

  @staticmethod
  def _resolve_connect():
    try:
      from websockets.sync.client import connect
    except ImportError as exc:
      raise RuntimeError("websockets_dependency_missing") from exc
    return connect


class CoinbaseAdvancedTradeUserStreamClient:
  transport = "coinbase_advanced_trade_user_websocket"

  def __init__(
    self,
    *,
    api_key: str,
    signing_key: str,
    symbol: str | None = None,
    websocket_url: str = "wss://advanced-trade-ws-user.coinbase.com",
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._api_key = api_key
    self._signing_key = signing_key
    self._symbol = symbol
    self._websocket_url = websocket_url
    self._clock = clock or (lambda: datetime.now(UTC))

  def open_session(self) -> BinanceVenueStreamSession:
    product_id = _normalize_coinbase_product_id(self._symbol) if self._symbol else None
    return CoinbaseAdvancedTradeUserStreamSession(
      session_id=f"coinbase-user:{product_id or 'all'}:heartbeats+user",
      websocket_url=self._websocket_url,
      api_key=self._api_key,
      signing_key=self._signing_key,
      product_id=product_id,
      clock=self._clock,
    )


class CoinbaseCombinedWebSocketVenueSession:
  transport = "coinbase_advanced_trade_combined_websocket"

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


class CoinbaseCombinedWebSocketVenueStreamClient:
  transport = "coinbase_advanced_trade_combined_websocket"

  def __init__(
    self,
    *,
    api_key: str,
    signing_key: str,
    symbol: str,
    timeframe: str,
    user_websocket_url: str = "wss://advanced-trade-ws-user.coinbase.com",
    market_websocket_url: str = "wss://advanced-trade-ws.coinbase.com",
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._user_stream_client = CoinbaseAdvancedTradeUserStreamClient(
      api_key=api_key,
      signing_key=signing_key,
      symbol=symbol,
      websocket_url=user_websocket_url,
      clock=clock,
    )
    self._market_stream_client = CoinbaseAdvancedTradeWebSocketMarketStreamClient(
      symbol=symbol,
      timeframe=timeframe,
      websocket_url=market_websocket_url,
      clock=clock,
    )

  def open_session(self) -> BinanceVenueStreamSession:
    user_data_session = self._user_stream_client.open_session()
    try:
      market_stream_session = self._market_stream_client.open_session()
    except Exception:
      user_data_session.close()
      raise
    return CoinbaseCombinedWebSocketVenueSession(
      user_data_session=user_data_session,
      market_stream_session=market_stream_session,
    )


KRAKEN_SPOT_MARKET_STREAM_COVERAGE = (
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
