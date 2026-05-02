from __future__ import annotations

from akra_trader.adapters.venue_execution_common import *

class KrakenWebSocketMarketStreamSession:
  transport = "kraken_spot_market_websocket"

  def __init__(
    self,
    *,
    session_id: str,
    websocket_url: str,
    symbol: str,
    timeframe: str,
    interval_minutes: int,
    clock: Callable[[], datetime],
  ) -> None:
    self.session_id = session_id
    self._websocket_url = websocket_url
    self._symbol = symbol
    self._timeframe = timeframe
    self._interval_minutes = interval_minutes
    self._clock = clock
    self._events: Queue[dict[str, Any]] = Queue()
    self._closed = False
    self._reader_stop = threading.Event()
    self._book_sequence_num = 0
    self._connect = self._resolve_connect()
    self._connection = self._connect(self._websocket_url)
    self._subscribe()
    self._reader = threading.Thread(
      target=self._reader_loop,
      name=f"kraken-market-stream-{session_id}",
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
      {
        "method": "subscribe",
        "params": {
          "channel": "ticker",
          "symbol": [self._symbol],
          "event_trigger": "trades",
          "snapshot": True,
        },
      },
      {
        "method": "subscribe",
        "params": {
          "channel": "trade",
          "symbol": [self._symbol],
          "snapshot": True,
        },
      },
      {
        "method": "subscribe",
        "params": {
          "channel": "book",
          "symbol": [self._symbol],
          "depth": 10,
          "snapshot": True,
        },
      },
      {
        "method": "subscribe",
        "params": {
          "channel": "ohlc",
          "symbol": [self._symbol],
          "interval": self._interval_minutes,
          "snapshot": True,
        },
      },
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
    channel = str(payload.get("channel") or "")
    if channel == "heartbeat":
      received_at = self._clock()
      return (
        {
          "e": "streamHeartbeat",
          "stream_scope": "market_data",
          "stream": "kraken@heartbeat",
          "E": int(received_at.timestamp() * 1000),
          "_received_at_ms": int(received_at.timestamp() * 1000),
        },
      )
    if payload.get("success") is False:
      warning = _coerce_string(payload.get("error")) or _coerce_string(payload.get("message")) or "kraken_stream_error"
      return (
        {
          "e": "streamWarning",
          "stream_scope": "market_data",
          "message": warning,
          "E": int(self._clock().timestamp() * 1000),
        },
      )
    if channel in {"", "status"} or str(payload.get("method") or "").lower() in {"subscribe", "unsubscribe"}:
      return ()
    data = payload.get("data")
    if not isinstance(data, list):
      return ()
    normalized: list[dict[str, Any]] = []
    if channel == "ticker":
      normalized.extend(self._normalize_ticker_rows(rows=data))
    elif channel == "trade":
      normalized.extend(self._normalize_trade_rows(rows=data))
    elif channel == "book":
      normalized.extend(self._normalize_book_rows(rows=data, payload_type=str(payload.get("type") or "")))
    elif channel == "ohlc":
      normalized.extend(self._normalize_ohlc_rows(rows=data))
    return tuple(normalized)

  def _normalize_ticker_rows(self, *, rows: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
      if not isinstance(row, dict):
        continue
      event_at = _coerce_datetime(row.get("timestamp"), None) or self._clock()
      best_bid = _coerce_float(row.get("bid"))
      best_bid_quantity = _coerce_float(row.get("bid_qty"))
      best_ask = _coerce_float(row.get("ask"))
      best_ask_quantity = _coerce_float(row.get("ask_qty"))
      last_price = _coerce_float(row.get("last"))
      change = _coerce_float(row.get("change"))
      open_price = (last_price - change) if last_price is not None and change is not None else None
      base_volume = _coerce_float(row.get("volume"))
      vwap = _coerce_float(row.get("vwap"))
      quote_volume = (base_volume * vwap) if base_volume is not None and vwap is not None else None
      if best_bid is not None or best_ask is not None:
        normalized.append(
          {
            "e": "bookTicker",
            "E": int(event_at.timestamp() * 1000),
            "b": str(row.get("bid") or ""),
            "B": str(row.get("bid_qty") or ""),
            "a": str(row.get("ask") or ""),
            "A": str(row.get("ask_qty") or ""),
            "stream_scope": "market_data",
            "stream": "kraken@ticker",
            "_received_at_ms": int(event_at.timestamp() * 1000),
          }
        )
      normalized.append(
        {
          "e": "24hrMiniTicker",
          "E": int(event_at.timestamp() * 1000),
          "o": "" if open_price is None else str(open_price),
          "c": str(row.get("last") or ""),
          "h": str(row.get("high") or ""),
          "l": str(row.get("low") or ""),
          "v": str(row.get("volume") or ""),
          "q": "" if quote_volume is None else str(quote_volume),
          "stream_scope": "market_data",
          "stream": "kraken@ticker",
          "_received_at_ms": int(event_at.timestamp() * 1000),
        }
      )
    return tuple(normalized)

  def _normalize_trade_rows(self, *, rows: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
      if not isinstance(row, dict):
        continue
      event_at = _coerce_datetime(row.get("timestamp"), None) or self._clock()
      event_id = _coerce_string(row.get("trade_id")) or str(int(event_at.timestamp() * 1000))
      normalized.extend(
        (
          {
            "e": "trade",
            "E": int(event_at.timestamp() * 1000),
            "T": int(event_at.timestamp() * 1000),
            "t": event_id,
            "p": str(row.get("price") or ""),
            "q": str(row.get("qty") or ""),
            "stream_scope": "market_data",
            "stream": "kraken@trade",
            "_received_at_ms": int(event_at.timestamp() * 1000),
          },
          {
            "e": "aggTrade",
            "E": int(event_at.timestamp() * 1000),
            "T": int(event_at.timestamp() * 1000),
            "a": event_id,
            "p": str(row.get("price") or ""),
            "q": str(row.get("qty") or ""),
            "stream_scope": "market_data",
            "stream": "kraken@trade",
            "_received_at_ms": int(event_at.timestamp() * 1000),
          },
        )
      )
    return tuple(normalized)

  def _normalize_book_rows(
    self,
    *,
    rows: list[dict[str, Any]],
    payload_type: str,
  ) -> tuple[dict[str, Any], ...]:
    normalized: list[dict[str, Any]] = []
    previous_sequence = self._book_sequence_num or None
    self._book_sequence_num += 1
    current_sequence = self._book_sequence_num
    for row in rows:
      if not isinstance(row, dict):
        continue
      event_at = _coerce_datetime(row.get("timestamp"), None) or self._clock()
      bids = _coerce_named_depth_levels(row.get("bids"))
      asks = _coerce_named_depth_levels(row.get("asks"))
      if not bids and not asks:
        continue
      normalized.append(
        {
          "e": "depthUpdate",
          "E": int(event_at.timestamp() * 1000),
          "U": current_sequence,
          "u": current_sequence,
          "pu": previous_sequence,
          "b": [[price, quantity] for price, quantity in bids],
          "a": [[price, quantity] for price, quantity in asks],
          "_snapshot_depth": payload_type.lower() == "snapshot",
          "stream_scope": "market_data",
          "stream": "kraken@book",
          "_received_at_ms": int(event_at.timestamp() * 1000),
        }
      )
    return tuple(normalized)

  def _normalize_ohlc_rows(self, *, rows: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
      if not isinstance(row, dict):
        continue
      interval_minutes = _coerce_int(row.get("interval")) or self._interval_minutes
      row_timeframe = _minutes_to_timeframe(interval_minutes) or self._timeframe
      open_at = _coerce_datetime(row.get("interval_begin"), None) or self._clock()
      close_at = open_at + timedelta(minutes=interval_minutes)
      event_at = _coerce_datetime(row.get("timestamp"), None) or close_at
      normalized.append(
        {
          "e": "kline",
          "E": int(event_at.timestamp() * 1000),
          "stream_scope": "market_data",
          "stream": f"kraken@ohlc_{row_timeframe}",
          "_received_at_ms": int(event_at.timestamp() * 1000),
          "k": {
            "i": row_timeframe,
            "t": int(open_at.timestamp() * 1000),
            "T": int(close_at.timestamp() * 1000),
            "o": str(row.get("open") or ""),
            "h": str(row.get("high") or ""),
            "l": str(row.get("low") or ""),
            "c": str(row.get("close") or ""),
            "v": str(row.get("volume") or ""),
            "x": close_at <= event_at,
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


class KrakenWebSocketMarketStreamClient:
  transport = "kraken_spot_market_websocket"

  def __init__(
    self,
    *,
    symbol: str,
    timeframe: str,
    websocket_url: str = "wss://ws.kraken.com/v2",
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    interval_minutes = _timeframe_to_minutes(timeframe)
    if interval_minutes is None:
      raise ValueError(f"Kraken websocket transport does not support timeframe {timeframe}.")
    self._symbol = symbol
    self._timeframe = timeframe
    self._interval_minutes = interval_minutes
    self._websocket_url = websocket_url
    self._clock = clock or (lambda: datetime.now(UTC))

  def open_session(self) -> BinanceVenueStreamSession:
    return KrakenWebSocketMarketStreamSession(
      session_id=f"kraken-market:{self._symbol}:ticker+trade+book+ohlc_{self._timeframe}",
      websocket_url=self._websocket_url,
      symbol=self._symbol,
      timeframe=self._timeframe,
      interval_minutes=self._interval_minutes,
      clock=self._clock,
    )
