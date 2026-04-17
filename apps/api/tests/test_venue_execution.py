from __future__ import annotations

import io
import json
from queue import Empty
from queue import Queue
import time
from datetime import UTC
from datetime import datetime
from datetime import timedelta

from akra_trader.adapters.venue_execution import BinanceVenueExecutionAdapter
from akra_trader.adapters.venue_execution import COINBASE_ADVANCED_TRADE_MARKET_STREAM_COVERAGE
from akra_trader.adapters.venue_execution import BinanceWebSocketMarketStreamClient
from akra_trader.adapters.venue_execution import BinanceWebSocketUserDataStreamClient
from akra_trader.adapters.venue_execution import KRAKEN_SPOT_MARKET_STREAM_COVERAGE


class MutableClock:
  def __init__(self, current: datetime) -> None:
    self.current = current

  def __call__(self) -> datetime:
    return self.current

  def advance(self, delta: timedelta) -> None:
    self.current += delta


class FakeUrlOpenResponse(io.BytesIO):
  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc, tb) -> None:
    self.close()


class FakeWebSocketConnection:
  def __init__(self) -> None:
    self.messages: Queue[str] = Queue()
    self.sent_messages: list[str] = []
    self.closed = False

  def recv(self) -> str:
    while not self.closed:
      try:
        return self.messages.get(timeout=0.01)
      except Empty:
        continue
    raise RuntimeError("closed")

  def send(self, payload: str) -> None:
    self.sent_messages.append(payload)

  def close(self) -> None:
    self.closed = True


class FakeExecutionExchange:
  def __init__(
    self,
    *,
    fetch_rows: list[dict[str, object]],
    order_books: list[dict[str, object]] | None = None,
    ticker: dict[str, object] | None = None,
    ticker_sequence: list[dict[str, object]] | None = None,
    trades: list[dict[str, object]] | None = None,
    trades_sequence: list[list[dict[str, object]]] | None = None,
    ohlcv: list[list[object]] | None = None,
    ohlcv_sequence: list[list[list[object]]] | None = None,
  ) -> None:
    self._fetch_rows = fetch_rows
    self._order_books = list(order_books or [])
    self._ticker = dict(ticker or {})
    self._ticker_sequence = [dict(entry) for entry in (ticker_sequence or [])]
    self._trades = list(trades or [])
    self._trades_sequence = [
      [dict(trade) for trade in snapshot]
      for snapshot in (trades_sequence or [])
    ]
    self._ohlcv = [list(candle) for candle in (ohlcv or [])]
    self._ohlcv_sequence = [
      [list(candle) for candle in snapshot]
      for snapshot in (ohlcv_sequence or [])
    ]
    self.fetch_order_book_calls = 0
    self.fetch_ticker_calls = 0
    self.fetch_trades_calls = 0
    self.fetch_ohlcv_calls = 0

  def create_order(self, symbol, type, side, amount, price=None, params=None) -> dict[str, object]:
    raise AssertionError("create_order should not be called in this test")

  def fetch_orders(self, symbol=None, since=None, limit=None, params=None) -> list[dict[str, object]]:
    return list(self._fetch_rows)

  def cancel_order(self, id, symbol=None, params=None) -> dict[str, object]:
    raise AssertionError("cancel_order should not be called in this test")

  def fetch_open_orders(self, symbol=None) -> list[dict[str, object]]:
    return []

  def fetch_order_book(self, symbol, limit=None, params=None) -> dict[str, object]:
    self.fetch_order_book_calls += 1
    if not self._order_books:
      raise AssertionError("fetch_order_book called without a prepared snapshot")
    if len(self._order_books) == 1:
      return dict(self._order_books[0])
    return dict(self._order_books.pop(0))

  def fetch_ticker(self, symbol, params=None) -> dict[str, object]:
    self.fetch_ticker_calls += 1
    if self._ticker_sequence:
      if len(self._ticker_sequence) == 1:
        return dict(self._ticker_sequence[0])
      return dict(self._ticker_sequence.pop(0))
    if not self._ticker:
      raise AssertionError("fetch_ticker called without a prepared ticker")
    return dict(self._ticker)

  def fetch_trades(self, symbol, since=None, limit=None, params=None) -> list[dict[str, object]]:
    self.fetch_trades_calls += 1
    if self._trades_sequence:
      if len(self._trades_sequence) == 1:
        return [dict(trade) for trade in self._trades_sequence[0]]
      return [dict(trade) for trade in self._trades_sequence.pop(0)]
    return [dict(trade) for trade in self._trades]

  def fetch_ohlcv(self, symbol, timeframe="1m", since=None, limit=None, params=None) -> list[list[object]]:
    self.fetch_ohlcv_calls += 1
    if self._ohlcv_sequence:
      if len(self._ohlcv_sequence) == 1:
        return [list(candle) for candle in self._ohlcv_sequence[0]]
      return [list(candle) for candle in self._ohlcv_sequence.pop(0)]
    return [list(candle) for candle in self._ohlcv]

  def fetch_closed_orders(self, symbol=None, since=None, limit=None, params=None) -> list[dict[str, object]]:
    return []


class FakeStreamSession:
  def __init__(self, session_id: str, *, transport: str = "binance_multi_stream_websocket") -> None:
    self.session_id = session_id
    self.transport = transport
    self.closed = False
    self._events: list[dict[str, object]] = []

  def push(self, event: dict[str, object]) -> None:
    self._events.append(event)

  def drain_events(self) -> tuple[dict[str, object], ...]:
    events = tuple(self._events)
    self._events.clear()
    return events

  def close(self) -> None:
    self.closed = True


class FakeStreamClient:
  def __init__(self, *sessions: FakeStreamSession) -> None:
    self._sessions = list(sessions)
    self.open_count = 0

  def open_session(self) -> FakeStreamSession:
    if not self._sessions:
      raise RuntimeError("no_fake_stream_session_available")
    self.open_count += 1
    if len(self._sessions) == 1:
      return self._sessions[0]
    return self._sessions.pop(0)


def _wait_for_events(
  session,
  *,
  expected_count: int = 1,
  timeout_seconds: float = 0.5,
) -> tuple[dict[str, object], ...]:
  deadline = time.monotonic() + timeout_seconds
  while time.monotonic() < deadline:
    events = session.drain_events()
    if len(events) >= expected_count:
      return events
    time.sleep(0.01)
  return ()


def test_binance_websocket_user_data_stream_client_opens_stream_and_refreshes_listen_key(
  monkeypatch,
) -> None:
  clock = MutableClock(datetime(2026, 4, 17, 12, 0, tzinfo=UTC))
  request_methods: list[str] = []
  request_urls: list[str] = []
  connection = FakeWebSocketConnection()

  def fake_urlopen(request, timeout=10):
    request_methods.append(request.get_method())
    request_urls.append(request.full_url)
    if request.get_method() == "POST":
      return FakeUrlOpenResponse(b'{"listenKey":"listen-key-1"}')
    return FakeUrlOpenResponse(b"{}")

  def fake_connect(url: str):
    request_urls.append(url)
    return connection

  monkeypatch.setattr("akra_trader.adapters.venue_execution.urllib_request.urlopen", fake_urlopen)
  monkeypatch.setattr(
    "akra_trader.adapters.venue_execution.BinanceWebSocketUserDataStreamSession._resolve_connect",
    staticmethod(lambda: fake_connect),
  )

  client = BinanceWebSocketUserDataStreamClient(
    api_key="test-key",
    rest_base_url="https://api.binance.test",
    websocket_url="wss://stream.binance.test/ws",
    clock=clock,
  )

  session = client.open_session()
  connection.messages.put(
    json.dumps(
      {
        "e": "executionReport",
        "E": int(clock().timestamp() * 1000),
        "O": int(clock().timestamp() * 1000),
        "T": int(clock().timestamp() * 1000),
        "i": "order-1",
        "S": "BUY",
        "q": "1.0",
        "z": "0.25",
        "p": "2500.0",
        "X": "PARTIALLY_FILLED",
        "Z": "625.0",
      }
    )
  )

  events = _wait_for_events(session)

  assert session.transport == "binance_user_data_websocket"
  assert request_methods[0] == "POST"
  assert request_urls[0] == "https://api.binance.test/api/v3/userDataStream"
  assert "wss://stream.binance.test/ws/listen-key-1" in request_urls
  assert events and events[0]["e"] == "executionReport"

  clock.advance(timedelta(minutes=31))
  session.drain_events()
  session.close()

  assert "PUT" in request_methods
  assert "DELETE" in request_methods
  assert connection.closed is True


def test_binance_websocket_market_stream_client_opens_wider_market_channels(
  monkeypatch,
) -> None:
  clock = MutableClock(datetime(2026, 4, 17, 12, 0, tzinfo=UTC))
  request_urls: list[str] = []
  connection = FakeWebSocketConnection()

  def fake_connect(url: str):
    request_urls.append(url)
    return connection

  monkeypatch.setattr(
    "akra_trader.adapters.venue_execution.BinanceWebSocketMarketStreamSession._resolve_connect",
    staticmethod(lambda: fake_connect),
  )

  client = BinanceWebSocketMarketStreamClient(
    symbol="ETH/USDT",
    timeframe="5m",
    websocket_url="wss://stream.binance.test/stream",
    clock=clock,
  )
  session = client.open_session()
  connection.messages.put(
    json.dumps(
      {
        "stream": "ethusdt@trade",
        "data": {
          "e": "trade",
          "E": int(clock().timestamp() * 1000),
          "T": int(clock().timestamp() * 1000),
        },
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "stream": "ethusdt@aggTrade",
        "data": {
          "a": 17,
          "T": int(clock().timestamp() * 1000),
        },
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "stream": "ethusdt@bookTicker",
        "data": {
          "u": 123,
        },
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "stream": "ethusdt@miniTicker",
        "data": {
          "E": int(clock().timestamp() * 1000),
        },
      }
    )
  )

  events = _wait_for_events(session, expected_count=4)

  assert session.transport == "binance_market_data_websocket"
  assert request_urls == [
    "wss://stream.binance.test/stream?streams=ethusdt@trade/ethusdt@aggTrade/ethusdt@bookTicker/ethusdt@miniTicker/ethusdt@depth20@100ms/ethusdt@kline_5m"
  ]
  assert events[0]["e"] == "trade"
  assert events[0]["stream_scope"] == "market_data"
  assert events[1]["e"] == "aggTrade"
  assert events[1]["stream"] == "ethusdt@aggTrade"
  assert events[2]["e"] == "bookTicker"
  assert events[2]["stream"] == "ethusdt@bookTicker"
  assert events[3]["e"] == "24hrMiniTicker"
  assert events[3]["stream"] == "ethusdt@miniTicker"

  session.close()
  assert connection.closed is True


def test_binance_adapter_handoff_failsover_and_tracks_broader_stream_coverage() -> None:
  current_time = datetime(2026, 4, 17, 12, 0, tzinfo=UTC)
  clock = MutableClock(current_time)
  exchange = FakeExecutionExchange(
    fetch_rows=[
      {
        "id": "order-1",
        "symbol": "ETH/USDT",
        "side": "buy",
        "amount": 1.0,
        "filled": 0.0,
        "remaining": 1.0,
        "price": 2500.0,
        "status": "open",
        "timestamp": int(current_time.timestamp() * 1000),
        "lastTradeTimestamp": int(current_time.timestamp() * 1000),
      }
    ],
    order_books=[
      {
        "nonce": 100,
        "bids": [[2498.8, 0.75], [2498.7, 0.65]],
        "asks": [[2501.2, 0.85], [2501.3, 0.95]],
      },
      {
        "nonce": 101,
        "bids": [[2499.1, 0.90], [2499.0, 0.70]],
        "asks": [[2500.9, 0.80], [2501.0, 1.05]],
      },
    ],
    ticker={
      "timestamp": int(current_time.timestamp() * 1000),
      "bid": 2498.95,
      "bidVolume": 1.2,
      "ask": 2501.05,
      "askVolume": 0.9,
      "open": 2492.5,
      "last": 2500.2,
      "high": 2504.5,
      "low": 2489.7,
      "baseVolume": 125.0,
      "quoteVolume": 312400.0,
    },
    trades=[
      {
        "id": "trade-restore-1",
        "price": 2500.1,
        "amount": 0.42,
        "timestamp": int(current_time.timestamp() * 1000),
      }
    ],
    ohlcv=[
      [int(current_time.timestamp() * 1000), 2499.0, 2502.0, 2497.5, 2500.0, 18.0]
    ],
  )
  first_stream_session = FakeStreamSession("listen-key-1")
  second_stream_session = FakeStreamSession("listen-key-2")
  stream_client = FakeStreamClient(first_stream_session, second_stream_session)
  adapter = BinanceVenueExecutionAdapter(
    exchange=exchange,
    venue_stream_client=stream_client,
    clock=clock,
  )

  handoff = adapter.handoff_session(
    symbol="ETH/USDT",
    timeframe="5m",
    owner_run_id="run-live-1",
    owner_session_id="worker-live-1",
    owned_order_ids=("order-1",),
  )

  assert handoff.state == "active"
  assert handoff.source == "binance_venue_stream"
  assert handoff.transport == "binance_multi_stream_websocket"
  assert handoff.venue_session_id == "listen-key-1"
  assert handoff.supervision_state == "streaming"
  assert handoff.failover_count == 0
  assert handoff.coverage == (
    "execution_reports",
    "account_positions",
    "balance_updates",
    "order_list_status",
    "trade_ticks",
    "aggregate_trade_ticks",
    "book_ticker",
    "mini_ticker",
    "depth_updates",
    "kline_candles",
    "order_book_lifecycle",
  )
  assert handoff.active_order_count == 1
  assert handoff.order_book_state == "snapshot_rebuilt"
  assert handoff.order_book_last_update_id == 100
  assert handoff.order_book_rebuild_count == 1
  assert handoff.order_book_bid_level_count == 2
  assert handoff.order_book_ask_level_count == 2
  assert handoff.order_book_best_bid_price == 2498.8
  assert handoff.order_book_best_ask_price == 2501.2
  assert tuple((level.price, level.quantity) for level in handoff.order_book_bids) == (
    (2498.8, 0.75),
    (2498.7, 0.65),
  )
  assert tuple((level.price, level.quantity) for level in handoff.order_book_asks) == (
    (2501.2, 0.85),
    (2501.3, 0.95),
  )
  assert handoff.channel_restore_state == "restored_from_exchange"
  assert handoff.channel_restore_count == 1
  assert handoff.channel_last_restored_at == current_time
  assert handoff.channel_continuation_state == "restored_from_exchange"
  assert handoff.channel_continuation_count == 1
  assert handoff.channel_last_continued_at == current_time
  assert handoff.trade_snapshot is not None
  assert handoff.trade_snapshot.event_id == "trade-restore-1"
  assert handoff.trade_snapshot.price == 2500.1
  assert handoff.trade_snapshot.quantity == 0.42
  assert handoff.aggregate_trade_snapshot is not None
  assert handoff.aggregate_trade_snapshot.price == 2500.1
  assert handoff.book_ticker_snapshot is not None
  assert handoff.book_ticker_snapshot.bid_price == 2498.95
  assert handoff.book_ticker_snapshot.ask_price == 2501.05
  assert handoff.mini_ticker_snapshot is not None
  assert handoff.mini_ticker_snapshot.close_price == 2500.2
  assert handoff.mini_ticker_snapshot.base_volume == 125.0
  assert handoff.kline_snapshot is not None
  assert handoff.kline_snapshot.timeframe == "5m"
  assert handoff.kline_snapshot.close_price == 2500.0
  assert handoff.last_market_event_at == current_time
  assert handoff.last_trade_event_at == current_time
  assert handoff.last_aggregate_trade_event_at == current_time
  assert handoff.last_book_ticker_event_at == current_time
  assert handoff.last_mini_ticker_event_at == current_time
  assert handoff.last_kline_event_at == current_time
  assert stream_client.open_count == 1

  clock.advance(timedelta(minutes=1))
  first_stream_session.push(
    {
      "e": "outboundAccountPosition",
      "E": int(clock().timestamp() * 1000),
    }
  )
  first_stream_session.push(
    {
      "e": "executionReport",
      "E": int(clock().timestamp() * 1000),
      "O": int(current_time.timestamp() * 1000),
      "T": int(clock().timestamp() * 1000),
      "i": "order-1",
      "S": "BUY",
      "q": "1.0",
      "z": "0.25",
      "p": "2500.0",
      "X": "PARTIALLY_FILLED",
      "Z": "625.0",
    }
  )
  first_stream_session.push(
    {
      "e": "streamDisconnect",
      "E": int(clock().timestamp() * 1000),
      "message": "socket_reset",
    }
  )
  first_sync = adapter.sync_session(handoff=handoff, order_ids=("order-1",))

  assert first_sync.state == "active"
  assert first_sync.handoff.transport == "binance_multi_stream_websocket"
  assert first_sync.handoff.venue_session_id == "listen-key-2"
  assert first_sync.handoff.cursor == "event-4"
  assert first_sync.handoff.active_order_count == 1
  assert first_sync.handoff.supervision_state == "streaming"
  assert first_sync.handoff.failover_count == 1
  assert first_sync.handoff.order_book_state == "snapshot_rebuilt"
  assert first_sync.handoff.order_book_last_update_id == 101
  assert first_sync.handoff.order_book_rebuild_count == 2
  assert first_sync.handoff.channel_restore_state == "restored_from_exchange"
  assert first_sync.handoff.channel_restore_count == 2
  assert first_sync.handoff.channel_last_restored_at == clock()
  assert first_sync.handoff.channel_continuation_state == "restored_from_exchange"
  assert first_sync.handoff.channel_continuation_count == 2
  assert first_sync.handoff.channel_last_continued_at == clock()
  assert first_sync.handoff.last_failover_at == clock()
  assert first_sync.handoff.last_account_event_at == clock()
  assert first_sync.synced_orders[0].status == "partially_filled"
  assert first_sync.synced_orders[0].filled_amount == 0.25
  assert first_sync.open_orders[0].order_id == "order-1"
  assert first_stream_session.closed is True

  clock.advance(timedelta(minutes=1))
  second_stream_session.push(
    {
      "e": "balanceUpdate",
      "E": int(clock().timestamp() * 1000),
    }
  )
  second_stream_session.push(
    {
      "e": "trade",
      "E": int(clock().timestamp() * 1000),
      "T": int(clock().timestamp() * 1000),
      "t": 17,
      "p": "2499.70",
      "q": "0.35",
    }
  )
  second_stream_session.push(
    {
      "e": "aggTrade",
      "E": int(clock().timestamp() * 1000),
      "T": int(clock().timestamp() * 1000),
      "a": 23,
      "p": "2499.65",
      "q": "0.55",
    }
  )
  second_stream_session.push(
    {
      "e": "bookTicker",
      "_received_at_ms": int(clock().timestamp() * 1000),
      "b": "2499.5",
      "B": "0.80",
      "a": "2500.5",
      "A": "1.10",
    }
  )
  second_stream_session.push(
    {
      "e": "24hrMiniTicker",
      "E": int(clock().timestamp() * 1000),
      "o": "2494.00",
      "c": "2500.70",
      "h": "2503.00",
      "l": "2492.50",
      "v": "123.40",
      "q": "308500.00",
    }
  )
  second_stream_session.push(
    {
      "e": "depthUpdate",
      "E": int(clock().timestamp() * 1000),
      "U": 102,
      "u": 103,
      "pu": 101,
      "b": [["2499.4", "1.25"]],
      "a": [["2500.6", "0.95"]],
    }
  )
  second_stream_session.push(
    {
      "e": "kline",
      "E": int(clock().timestamp() * 1000),
      "k": {
        "i": "5m",
        "t": int(clock().timestamp() * 1000),
        "T": int(clock().timestamp() * 1000),
        "o": "2497.90",
        "h": "2501.10",
        "l": "2497.50",
        "c": "2500.40",
        "v": "18.25",
        "x": True,
      },
    }
  )
  second_stream_session.push(
    {
      "e": "listStatus",
      "E": int(clock().timestamp() * 1000),
    }
  )
  second_stream_session.push(
    {
      "e": "executionReport",
      "E": int(clock().timestamp() * 1000),
      "O": int(current_time.timestamp() * 1000),
      "T": int(clock().timestamp() * 1000),
      "i": "order-1",
      "S": "BUY",
      "q": "1.0",
      "z": "1.0",
      "p": "2500.0",
      "X": "FILLED",
      "Z": "2500.0",
    }
  )
  second_sync = adapter.sync_session(handoff=first_sync.handoff, order_ids=("order-1",))
  released = adapter.release_session(handoff=second_sync.handoff)

  assert second_sync.handoff.cursor == "event-13"
  assert second_sync.handoff.active_order_count == 0
  assert second_sync.handoff.order_book_state == "streaming"
  assert second_sync.handoff.order_book_last_update_id == 103
  assert second_sync.handoff.order_book_gap_count == 1
  assert second_sync.handoff.order_book_rebuild_count == 2
  assert second_sync.handoff.order_book_best_bid_price == 2499.4
  assert second_sync.handoff.order_book_best_bid_quantity == 1.25
  assert second_sync.handoff.order_book_best_ask_price == 2500.6
  assert second_sync.handoff.order_book_best_ask_quantity == 0.95
  assert second_sync.handoff.channel_continuation_state == "streaming"
  assert second_sync.handoff.channel_continuation_count == 2
  assert second_sync.handoff.channel_last_continued_at == clock()
  assert second_sync.handoff.trade_snapshot is not None
  assert second_sync.handoff.trade_snapshot.event_id == "17"
  assert second_sync.handoff.trade_snapshot.price == 2499.7
  assert second_sync.handoff.trade_snapshot.quantity == 0.35
  assert second_sync.handoff.aggregate_trade_snapshot is not None
  assert second_sync.handoff.aggregate_trade_snapshot.event_id == "23"
  assert second_sync.handoff.aggregate_trade_snapshot.price == 2499.65
  assert second_sync.handoff.book_ticker_snapshot is not None
  assert second_sync.handoff.book_ticker_snapshot.bid_price == 2499.5
  assert second_sync.handoff.book_ticker_snapshot.ask_price == 2500.5
  assert second_sync.handoff.mini_ticker_snapshot is not None
  assert second_sync.handoff.mini_ticker_snapshot.close_price == 2500.7
  assert second_sync.handoff.mini_ticker_snapshot.quote_volume == 308500.0
  assert second_sync.handoff.kline_snapshot is not None
  assert second_sync.handoff.kline_snapshot.close_price == 2500.4
  assert second_sync.handoff.kline_snapshot.closed is True
  assert tuple((level.price, level.quantity) for level in second_sync.handoff.order_book_bids[:2]) == (
    (2499.4, 1.25),
    (2499.1, 0.9),
  )
  assert tuple((level.price, level.quantity) for level in second_sync.handoff.order_book_asks[:2]) == (
    (2500.6, 0.95),
    (2500.9, 0.8),
  )
  assert second_sync.handoff.last_market_event_at == clock()
  assert second_sync.handoff.last_depth_event_at == clock()
  assert second_sync.handoff.last_kline_event_at == clock()
  assert second_sync.handoff.last_aggregate_trade_event_at == clock()
  assert second_sync.handoff.last_mini_ticker_event_at == clock()
  assert second_sync.handoff.last_balance_event_at == clock()
  assert second_sync.handoff.last_order_list_event_at == clock()
  assert second_sync.handoff.last_trade_event_at == clock()
  assert second_sync.handoff.last_book_ticker_event_at == clock()
  assert second_sync.synced_orders[0].status == "filled"
  assert second_sync.synced_orders[0].filled_amount == 1.0
  assert second_sync.open_orders == ()
  assert released.state == "released"
  assert released.transport == "binance_multi_stream_websocket"
  assert released.supervision_state == "released"
  assert released.order_book_state == "released"
  assert released.channel_restore_state == second_sync.handoff.channel_restore_state
  assert released.channel_restore_count == second_sync.handoff.channel_restore_count
  assert released.channel_continuation_state == "released"
  assert released.channel_continuation_count == second_sync.handoff.channel_continuation_count
  assert released.failover_count == 1
  assert second_stream_session.closed is True


def test_coinbase_adapter_uses_push_native_multi_venue_transport(monkeypatch) -> None:
  current_time = datetime(2026, 4, 17, 12, 0, tzinfo=UTC)
  clock = MutableClock(current_time)
  request_urls: list[str] = []
  connection = FakeWebSocketConnection()

  def fake_connect(url: str):
    request_urls.append(url)
    return connection

  monkeypatch.setattr(
    "akra_trader.adapters.venue_execution.CoinbaseAdvancedTradeWebSocketMarketStreamSession._resolve_connect",
    staticmethod(lambda: fake_connect),
  )

  exchange = FakeExecutionExchange(
    fetch_rows=[],
    order_books=[
      {
        "nonce": 700,
        "bids": [[21931.98, 1.10], [21931.25, 0.65]],
        "asks": [[21933.98, 1.25], [21934.50, 0.40]],
      },
    ],
    ticker={
      "timestamp": int(current_time.timestamp() * 1000),
      "bid": 21931.98,
      "bidVolume": 1.10,
      "ask": 21933.98,
      "askVolume": 1.25,
      "last": 21932.98,
      "high": 23011.18,
      "low": 21835.29,
      "baseVolume": 16038.28770938,
      "quoteVolume": 351749098.37,
    },
    trades=[
      {
        "id": "coinbase-trade-restore-1",
        "price": 21932.98,
        "amount": 0.30,
        "timestamp": int(current_time.timestamp() * 1000),
      }
    ],
    ohlcv=[
      [int((current_time - timedelta(minutes=5)).timestamp() * 1000), 21920.0, 21940.0, 21910.0, 21932.5, 12.0]
    ],
  )
  adapter = BinanceVenueExecutionAdapter(
    venue="coinbase",
    exchange=exchange,
    clock=clock,
  )

  ready, issues = adapter.describe_capability()

  assert ready is True
  assert issues == ()

  handoff = adapter.handoff_session(
    symbol="BTC/USD",
    timeframe="5m",
    owner_run_id="run-live-coinbase",
    owner_session_id="worker-live-coinbase",
    owned_order_ids=(),
  )

  sent_messages = [json.loads(payload) for payload in connection.sent_messages]

  assert request_urls == ["wss://advanced-trade-ws.coinbase.com"]
  assert sent_messages == [
    {"type": "subscribe", "channel": "heartbeats"},
    {"type": "subscribe", "channel": "ticker", "product_ids": ["BTC-USD"]},
    {"type": "subscribe", "channel": "market_trades", "product_ids": ["BTC-USD"]},
    {"type": "subscribe", "channel": "level2", "product_ids": ["BTC-USD"]},
    {"type": "subscribe", "channel": "candles", "product_ids": ["BTC-USD"]},
  ]
  assert handoff.state == "active"
  assert handoff.source == "coinbase_market_push_transport"
  assert handoff.transport == "coinbase_advanced_trade_market_websocket"
  assert handoff.supervision_state == "streaming"
  assert handoff.coverage == COINBASE_ADVANCED_TRADE_MARKET_STREAM_COVERAGE
  assert "venue_stream_transport_fallback:coinbase_advanced_trade_market_websocket" in handoff.issues
  assert handoff.order_book_state == "snapshot_rebuilt"
  assert handoff.order_book_last_update_id == 700
  assert handoff.channel_restore_state == "restored_from_exchange"
  assert handoff.channel_continuation_state == "restored_from_exchange"
  assert handoff.trade_snapshot is not None
  assert handoff.trade_snapshot.event_id == "coinbase-trade-restore-1"
  assert handoff.book_ticker_snapshot is not None
  assert handoff.book_ticker_snapshot.bid_price == 21931.98
  assert handoff.mini_ticker_snapshot is not None
  assert handoff.mini_ticker_snapshot.close_price == 21932.98
  assert handoff.kline_snapshot is not None
  assert handoff.kline_snapshot.close_price == 21932.5

  clock.advance(timedelta(minutes=5))
  connection.messages.put(
    json.dumps(
      {
        "channel": "heartbeats",
        "timestamp": clock().isoformat().replace("+00:00", "Z"),
        "events": [{"current_time": clock().isoformat().replace("+00:00", "Z"), "heartbeat_counter": "1"}],
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "channel": "ticker",
        "timestamp": clock().isoformat().replace("+00:00", "Z"),
        "sequence_num": 701,
        "events": [
          {
            "type": "snapshot",
            "tickers": [
              {
                "type": "ticker",
                "product_id": "BTC-USD",
                "price": "21934.10",
                "volume_24_h": "16040.10",
                "low_24_h": "21835.29",
                "high_24_h": "23011.18",
                "best_bid": "21934.00",
                "best_bid_quantity": "0.95",
                "best_ask": "21934.20",
                "best_ask_quantity": "1.05",
              }
            ],
          }
        ],
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "channel": "market_trades",
        "timestamp": clock().isoformat().replace("+00:00", "Z"),
        "sequence_num": 702,
        "events": [
          {
            "type": "update",
            "trades": [
              {
                "trade_id": "coinbase-trade-2",
                "product_id": "BTC-USD",
                "price": "21934.12",
                "size": "0.42",
                "side": "BUY",
                "time": clock().isoformat().replace("+00:00", "Z"),
              }
            ],
          }
        ],
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "channel": "l2_data",
        "timestamp": clock().isoformat().replace("+00:00", "Z"),
        "sequence_num": 701,
        "events": [
          {
            "type": "update",
            "product_id": "BTC-USD",
            "updates": [
              {
                "side": "bid",
                "event_time": clock().isoformat().replace("+00:00", "Z"),
                "price_level": "21934.00",
                "new_quantity": "0.95",
              },
              {
                "side": "offer",
                "event_time": clock().isoformat().replace("+00:00", "Z"),
                "price_level": "21934.20",
                "new_quantity": "1.05",
              },
            ],
          }
        ],
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "channel": "candles",
        "timestamp": clock().isoformat().replace("+00:00", "Z"),
        "sequence_num": 703,
        "events": [
          {
            "type": "snapshot",
            "candles": [
              {
                "start": str(int((clock() - timedelta(minutes=5)).timestamp())),
                "high": "21936.00",
                "low": "21920.00",
                "open": "21930.00",
                "close": "21934.50",
                "volume": "18.25",
                "product_id": "BTC-USD",
              }
            ],
          }
        ],
      }
    )
  )
  sync = adapter.sync_session(handoff=handoff, order_ids=())
  released = adapter.release_session(handoff=sync.handoff)

  assert sync.state == "active"
  assert sync.handoff.transport == "coinbase_advanced_trade_market_websocket"
  assert sync.handoff.source == "coinbase_market_push_transport"
  assert sync.handoff.supervision_state == "streaming"
  assert sync.handoff.failover_count == 0
  assert sync.handoff.coverage == COINBASE_ADVANCED_TRADE_MARKET_STREAM_COVERAGE
  assert sync.handoff.order_book_state == "streaming"
  assert sync.handoff.order_book_last_update_id == 701
  assert tuple((level.price, level.quantity) for level in sync.handoff.order_book_bids[:2]) == (
    (21934.0, 0.95),
    (21931.98, 1.1),
  )
  assert tuple((level.price, level.quantity) for level in sync.handoff.order_book_asks[:2]) == (
    (21933.98, 1.25),
    (21934.2, 1.05),
  )
  assert sync.handoff.order_book_best_bid_price == 21934.0
  assert sync.handoff.order_book_best_ask_price == 21933.98
  assert sync.handoff.channel_continuation_state == "streaming"
  assert sync.handoff.channel_continuation_count == 1
  assert sync.handoff.trade_snapshot is not None
  assert sync.handoff.trade_snapshot.event_id == "coinbase-trade-2"
  assert sync.handoff.aggregate_trade_snapshot is not None
  assert sync.handoff.aggregate_trade_snapshot.event_id == "coinbase-trade-2"
  assert sync.handoff.book_ticker_snapshot is not None
  assert sync.handoff.book_ticker_snapshot.bid_price == 21934.0
  assert sync.handoff.book_ticker_snapshot.ask_price == 21934.2
  assert sync.handoff.mini_ticker_snapshot is not None
  assert sync.handoff.mini_ticker_snapshot.close_price == 21934.1
  assert sync.handoff.kline_snapshot is not None
  assert sync.handoff.kline_snapshot.close_price == 21934.5
  assert sync.handoff.channel_last_continued_at == sync.handoff.kline_snapshot.close_at
  assert sync.handoff.last_market_event_at == sync.handoff.kline_snapshot.close_at
  assert sync.handoff.last_depth_event_at == clock()
  assert sync.handoff.last_trade_event_at == clock()
  assert sync.handoff.last_aggregate_trade_event_at == clock()
  assert sync.handoff.last_book_ticker_event_at == clock()
  assert sync.handoff.last_mini_ticker_event_at == clock()
  assert sync.handoff.last_kline_event_at == sync.handoff.kline_snapshot.close_at
  assert released.state == "released"
  assert released.transport == "coinbase_advanced_trade_market_websocket"
  assert released.source == "coinbase_market_push_transport"
  assert connection.closed is True


def test_kraken_adapter_extends_push_native_multi_venue_transport(monkeypatch) -> None:
  current_time = datetime(2026, 4, 17, 12, 0, tzinfo=UTC)
  clock = MutableClock(current_time)
  request_urls: list[str] = []
  connection = FakeWebSocketConnection()

  def fake_connect(url: str):
    request_urls.append(url)
    return connection

  monkeypatch.setattr(
    "akra_trader.adapters.venue_execution.KrakenWebSocketMarketStreamSession._resolve_connect",
    staticmethod(lambda: fake_connect),
  )

  exchange = FakeExecutionExchange(
    fetch_rows=[],
    order_books=[
      {
        "nonce": 900,
        "bids": [[21931.98, 1.10], [21931.25, 0.65]],
        "asks": [[21933.98, 1.25], [21934.50, 0.40]],
      },
    ],
    ticker={
      "timestamp": int(current_time.timestamp() * 1000),
      "bid": 21931.98,
      "bidVolume": 1.10,
      "ask": 21933.98,
      "askVolume": 1.25,
      "last": 21932.98,
      "high": 23011.18,
      "low": 21835.29,
      "baseVolume": 16038.28770938,
      "quoteVolume": 351749098.37,
    },
    trades=[
      {
        "id": "kraken-trade-restore-1",
        "price": 21932.98,
        "amount": 0.30,
        "timestamp": int(current_time.timestamp() * 1000),
      }
    ],
    ohlcv=[
      [int((current_time - timedelta(minutes=5)).timestamp() * 1000), 21920.0, 21940.0, 21910.0, 21932.5, 12.0]
    ],
  )
  adapter = BinanceVenueExecutionAdapter(
    venue="kraken",
    exchange=exchange,
    clock=clock,
  )

  ready, issues = adapter.describe_capability()

  assert ready is True
  assert issues == ()

  handoff = adapter.handoff_session(
    symbol="BTC/USD",
    timeframe="5m",
    owner_run_id="run-live-kraken",
    owner_session_id="worker-live-kraken",
    owned_order_ids=(),
  )

  sent_messages = [json.loads(payload) for payload in connection.sent_messages]

  assert request_urls == ["wss://ws.kraken.com/v2"]
  assert sent_messages == [
    {
      "method": "subscribe",
      "params": {
        "channel": "ticker",
        "symbol": ["BTC/USD"],
        "event_trigger": "trades",
        "snapshot": True,
      },
    },
    {
      "method": "subscribe",
      "params": {
        "channel": "trade",
        "symbol": ["BTC/USD"],
        "snapshot": True,
      },
    },
    {
      "method": "subscribe",
      "params": {
        "channel": "book",
        "symbol": ["BTC/USD"],
        "depth": 10,
        "snapshot": True,
      },
    },
    {
      "method": "subscribe",
      "params": {
        "channel": "ohlc",
        "symbol": ["BTC/USD"],
        "interval": 5,
        "snapshot": True,
      },
    },
  ]
  assert handoff.state == "active"
  assert handoff.source == "kraken_market_push_transport"
  assert handoff.transport == "kraken_spot_market_websocket"
  assert handoff.supervision_state == "streaming"
  assert handoff.coverage == KRAKEN_SPOT_MARKET_STREAM_COVERAGE
  assert "venue_stream_transport_fallback:kraken_spot_market_websocket" in handoff.issues
  assert handoff.order_book_state == "snapshot_rebuilt"
  assert handoff.order_book_last_update_id == 900
  assert handoff.channel_restore_state == "restored_from_exchange"
  assert handoff.channel_continuation_state == "restored_from_exchange"
  assert handoff.trade_snapshot is not None
  assert handoff.trade_snapshot.event_id == "kraken-trade-restore-1"
  assert handoff.book_ticker_snapshot is not None
  assert handoff.book_ticker_snapshot.bid_price == 21931.98
  assert handoff.mini_ticker_snapshot is not None
  assert handoff.mini_ticker_snapshot.close_price == 21932.98
  assert handoff.kline_snapshot is not None
  assert handoff.kline_snapshot.close_price == 21932.5

  clock.advance(timedelta(minutes=5))
  connection.messages.put(json.dumps({"channel": "heartbeat"}))
  connection.messages.put(
    json.dumps(
      {
        "channel": "ticker",
        "type": "update",
        "data": [
          {
            "symbol": "BTC/USD",
            "bid": 21934.00,
            "bid_qty": 0.95,
            "ask": 21934.20,
            "ask_qty": 1.05,
            "last": 21934.10,
            "volume": 16040.10,
            "vwap": 21920.50,
            "low": 21835.29,
            "high": 23011.18,
            "change": 1.12,
            "change_pct": 0.01,
            "timestamp": clock().isoformat().replace("+00:00", "Z"),
          }
        ],
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "channel": "trade",
        "type": "update",
        "data": [
          {
            "symbol": "BTC/USD",
            "side": "buy",
            "price": 21934.12,
            "qty": 0.42,
            "ord_type": "market",
            "trade_id": 701,
            "timestamp": clock().isoformat().replace("+00:00", "Z"),
          }
        ],
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "channel": "book",
        "type": "snapshot",
        "data": [
          {
            "symbol": "BTC/USD",
            "bids": [
              {"price": 21934.00, "qty": 0.95},
              {"price": 21931.98, "qty": 1.10},
            ],
            "asks": [
              {"price": 21934.20, "qty": 1.05},
              {"price": 21934.50, "qty": 0.40},
            ],
            "timestamp": clock().isoformat().replace("+00:00", "Z"),
          }
        ],
      }
    )
  )
  connection.messages.put(
    json.dumps(
      {
        "channel": "ohlc",
        "type": "update",
        "data": [
          {
            "symbol": "BTC/USD",
            "open": 21930.00,
            "high": 21936.00,
            "low": 21920.00,
            "close": 21934.50,
            "vwap": 21932.20,
            "trades": 12,
            "volume": 18.25,
            "interval_begin": (clock() - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
            "interval": 5,
            "timestamp": clock().isoformat().replace("+00:00", "Z"),
          }
        ],
      }
    )
  )

  sync = adapter.sync_session(handoff=handoff, order_ids=())
  released = adapter.release_session(handoff=sync.handoff)

  assert sync.state == "active"
  assert sync.handoff.transport == "kraken_spot_market_websocket"
  assert sync.handoff.source == "kraken_market_push_transport"
  assert sync.handoff.supervision_state == "streaming"
  assert sync.handoff.failover_count == 0
  assert sync.handoff.coverage == KRAKEN_SPOT_MARKET_STREAM_COVERAGE
  assert sync.handoff.order_book_state == "streaming"
  assert sync.handoff.order_book_last_update_id == 1
  assert tuple((level.price, level.quantity) for level in sync.handoff.order_book_bids[:2]) == (
    (21934.0, 0.95),
    (21931.98, 1.1),
  )
  assert tuple((level.price, level.quantity) for level in sync.handoff.order_book_asks[:2]) == (
    (21934.2, 1.05),
    (21934.5, 0.4),
  )
  assert sync.handoff.order_book_best_bid_price == 21934.0
  assert sync.handoff.order_book_best_ask_price == 21934.2
  assert sync.handoff.channel_continuation_state == "streaming"
  assert sync.handoff.channel_continuation_count == 1
  assert sync.handoff.trade_snapshot is not None
  assert sync.handoff.trade_snapshot.event_id == "701"
  assert sync.handoff.aggregate_trade_snapshot is not None
  assert sync.handoff.aggregate_trade_snapshot.event_id == "701"
  assert sync.handoff.book_ticker_snapshot is not None
  assert sync.handoff.book_ticker_snapshot.bid_price == 21934.0
  assert sync.handoff.book_ticker_snapshot.ask_price == 21934.2
  assert sync.handoff.mini_ticker_snapshot is not None
  assert sync.handoff.mini_ticker_snapshot.close_price == 21934.1
  assert sync.handoff.kline_snapshot is not None
  assert sync.handoff.kline_snapshot.close_price == 21934.5
  assert sync.handoff.last_market_event_at == clock()
  assert sync.handoff.last_depth_event_at == clock()
  assert sync.handoff.last_trade_event_at == clock()
  assert sync.handoff.last_aggregate_trade_event_at == clock()
  assert sync.handoff.last_book_ticker_event_at == clock()
  assert sync.handoff.last_mini_ticker_event_at == clock()
  assert sync.handoff.last_kline_event_at == clock()
  assert released.state == "released"
  assert released.transport == "kraken_spot_market_websocket"
  assert released.source == "kraken_market_push_transport"
  assert connection.closed is True


def test_binance_adapter_rebuilds_local_book_from_snapshot_on_depth_sequence_gap() -> None:
  current_time = datetime(2026, 4, 17, 12, 0, tzinfo=UTC)
  clock = MutableClock(current_time)
  exchange = FakeExecutionExchange(
    fetch_rows=[],
    order_books=[
      {
        "nonce": 20,
        "bids": [[2498.0, 0.50], [2497.9, 0.40]],
        "asks": [[2498.8, 0.45], [2498.9, 0.60]],
      },
      {
        "nonce": 34,
        "bids": [[2497.3, 0.95], [2497.1, 0.55]],
        "asks": [[2498.2, 0.72], [2498.5, 0.68]],
      },
    ],
    ticker={
      "timestamp": int(current_time.timestamp() * 1000),
      "bid": 2498.0,
      "bidVolume": 0.5,
      "ask": 2498.8,
      "askVolume": 0.45,
      "open": 2496.0,
      "last": 2498.4,
      "high": 2499.1,
      "low": 2495.8,
      "baseVolume": 22.0,
      "quoteVolume": 54963.0,
    },
    trades=[
      {
        "id": "trade-gap-1",
        "price": 2498.35,
        "amount": 0.18,
        "timestamp": int(current_time.timestamp() * 1000),
      }
    ],
    ohlcv=[
      [int(current_time.timestamp() * 1000), 2498.0, 2499.1, 2497.5, 2498.4, 11.0]
    ],
  )
  stream_session = FakeStreamSession("listen-key-gap")
  stream_client = FakeStreamClient(stream_session)
  adapter = BinanceVenueExecutionAdapter(
    exchange=exchange,
    venue_stream_client=stream_client,
    clock=clock,
  )

  handoff = adapter.handoff_session(
    symbol="ETH/USDT",
    timeframe="5m",
    owner_run_id="run-live-gap",
    owner_session_id="worker-live-gap",
    owned_order_ids=(),
  )

  clock.advance(timedelta(seconds=30))
  stream_session.push(
    {
      "e": "depthUpdate",
      "E": int(clock().timestamp() * 1000),
      "U": 21,
      "u": 25,
      "b": [["2498.0", "0.50"]],
      "a": [["2498.8", "0.45"]],
    }
  )
  first_sync = adapter.sync_session(handoff=handoff, order_ids=())

  clock.advance(timedelta(seconds=30))
  stream_session.push(
    {
      "e": "depthUpdate",
      "E": int(clock().timestamp() * 1000),
      "U": 31,
      "u": 34,
      "pu": 29,
      "b": [["2497.5", "0.80"]],
      "a": [["2498.4", "0.70"]],
    }
  )
  second_sync = adapter.sync_session(handoff=first_sync.handoff, order_ids=())

  assert handoff.order_book_state == "snapshot_rebuilt"
  assert handoff.order_book_last_update_id == 20
  assert handoff.order_book_rebuild_count == 1
  assert first_sync.handoff.order_book_state == "streaming"
  assert first_sync.handoff.order_book_last_update_id == 25
  assert second_sync.handoff.order_book_state == "snapshot_rebuilt"
  assert second_sync.handoff.order_book_gap_count == 1
  assert second_sync.handoff.order_book_last_update_id == 34
  assert second_sync.handoff.order_book_rebuild_count == 2
  assert second_sync.handoff.order_book_bid_level_count == 2
  assert second_sync.handoff.order_book_ask_level_count == 2
  assert second_sync.handoff.order_book_best_bid_price == 2497.3
  assert second_sync.handoff.order_book_best_ask_price == 2498.2
  assert tuple((level.price, level.quantity) for level in second_sync.handoff.order_book_bids) == (
    (2497.3, 0.95),
    (2497.1, 0.55),
  )
  assert tuple((level.price, level.quantity) for level in second_sync.handoff.order_book_asks) == (
    (2498.2, 0.72),
    (2498.5, 0.68),
  )
  assert second_sync.handoff.channel_restore_state == "restored_from_exchange"
  assert second_sync.handoff.channel_restore_count == 2
  assert second_sync.handoff.channel_last_restored_at == clock()
  assert second_sync.handoff.channel_continuation_state == "restored_from_exchange"
  assert second_sync.handoff.channel_continuation_count == 2
  assert second_sync.handoff.channel_last_continued_at == clock()
  assert second_sync.handoff.trade_snapshot is not None
  assert second_sync.handoff.trade_snapshot.event_id == "trade-gap-1"
  assert second_sync.handoff.book_ticker_snapshot is not None
  assert second_sync.handoff.mini_ticker_snapshot is not None
  assert second_sync.handoff.kline_snapshot is not None
  assert "binance_order_book_gap_detected:25:29" in second_sync.handoff.issues


def test_binance_adapter_restores_persisted_order_book_and_deeper_channels_after_restart() -> None:
  current_time = datetime(2026, 4, 17, 12, 0, tzinfo=UTC)
  clock = MutableClock(current_time)
  initial_exchange = FakeExecutionExchange(
    fetch_rows=[],
    order_books=[
      {
        "nonce": 40,
        "bids": [[2499.9, 0.55], [2499.7, 0.45]],
        "asks": [[2500.2, 0.60], [2500.4, 0.75]],
      }
    ],
    ticker={
      "timestamp": int(current_time.timestamp() * 1000),
      "bid": 2499.95,
      "bidVolume": 0.7,
      "ask": 2500.25,
      "askVolume": 0.8,
      "open": 2498.4,
      "last": 2500.0,
      "high": 2501.0,
      "low": 2498.0,
      "baseVolume": 12.0,
      "quoteVolume": 30005.0,
    },
    trades=[
      {
        "id": "trade-persisted-1",
        "price": 2500.05,
        "amount": 0.21,
        "timestamp": int(current_time.timestamp() * 1000),
      }
    ],
    ohlcv=[
      [int(current_time.timestamp() * 1000), 2499.5, 2500.5, 2499.1, 2500.0, 7.0]
    ],
  )
  first_stream_session = FakeStreamSession("listen-key-persisted")
  initial_adapter = BinanceVenueExecutionAdapter(
    exchange=initial_exchange,
    venue_stream_client=FakeStreamClient(first_stream_session),
    clock=clock,
  )

  handoff = initial_adapter.handoff_session(
    symbol="ETH/USDT",
    timeframe="5m",
    owner_run_id="run-live-persisted",
    owner_session_id="worker-live-persisted",
    owned_order_ids=(),
  )

  assert initial_exchange.fetch_order_book_calls == 1
  assert handoff.order_book_last_update_id == 40
  assert len(handoff.order_book_bids) == 2
  assert len(handoff.order_book_asks) == 2
  assert handoff.channel_continuation_state == "restored_from_exchange"
  assert handoff.channel_continuation_count == 1
  assert handoff.trade_snapshot is not None
  assert handoff.trade_snapshot.event_id == "trade-persisted-1"

  clock.advance(timedelta(seconds=45))
  restart_exchange = FakeExecutionExchange(
    fetch_rows=[],
    ticker={
      "timestamp": int(clock().timestamp() * 1000),
      "bid": 2500.0,
      "bidVolume": 0.9,
      "ask": 2500.3,
      "askVolume": 0.85,
      "open": 2499.0,
      "last": 2500.15,
      "high": 2500.8,
      "low": 2498.9,
      "baseVolume": 14.0,
      "quoteVolume": 35002.0,
    },
    trades=[
      {
        "id": "trade-persisted-2",
        "price": 2500.12,
        "amount": 0.33,
        "timestamp": int(clock().timestamp() * 1000),
      }
    ],
    ohlcv=[
      [int(clock().timestamp() * 1000), 2499.8, 2500.8, 2499.5, 2500.1, 9.0]
    ],
  )
  restart_stream_session = FakeStreamSession("listen-key-persisted-2")
  restart_stream_session.push(
    {
      "e": "depthUpdate",
      "E": int(clock().timestamp() * 1000),
      "U": 41,
      "u": 42,
      "pu": 40,
      "b": [["2499.95", "0.80"]],
      "a": [["2500.15", "0.65"]],
    }
  )
  restart_stream_session.push(
    {
      "e": "bookTicker",
      "E": int(clock().timestamp() * 1000),
      "b": "2499.98",
      "B": "0.72",
      "a": "2500.18",
      "A": "0.61",
    }
  )
  restart_stream_session.push(
    {
      "e": "trade",
      "E": int(clock().timestamp() * 1000),
      "T": int(clock().timestamp() * 1000),
      "t": 44,
      "p": "2500.16",
      "q": "0.27",
    }
  )
  restart_stream_session.push(
    {
      "e": "kline",
      "E": int(clock().timestamp() * 1000),
      "k": {
        "i": "5m",
        "t": int(clock().timestamp() * 1000),
        "T": int(clock().timestamp() * 1000),
        "o": "2499.80",
        "h": "2500.40",
        "l": "2499.60",
        "c": "2500.20",
        "v": "9.50",
        "x": False,
      },
    }
  )
  restarted_adapter = BinanceVenueExecutionAdapter(
    exchange=restart_exchange,
    venue_stream_client=FakeStreamClient(restart_stream_session),
    clock=clock,
  )

  sync = restarted_adapter.sync_session(handoff=handoff, order_ids=())

  assert restart_exchange.fetch_order_book_calls == 0
  assert restart_exchange.fetch_ticker_calls == 1
  assert restart_exchange.fetch_trades_calls == 1
  assert restart_exchange.fetch_ohlcv_calls == 1
  assert sync.state == "active"
  assert sync.handoff.venue_session_id == "listen-key-persisted-2"
  assert sync.handoff.failover_count == 1
  assert sync.handoff.order_book_state == "streaming"
  assert sync.handoff.order_book_last_update_id == 42
  assert sync.handoff.order_book_gap_count == 1
  assert sync.handoff.order_book_rebuild_count == 1
  assert sync.handoff.order_book_best_bid_price == 2499.98
  assert sync.handoff.order_book_best_ask_price == 2500.18
  assert sync.handoff.channel_continuation_state == "streaming"
  assert sync.handoff.channel_continuation_count == 3
  assert sync.handoff.channel_last_continued_at == clock()
  assert sync.handoff.trade_snapshot is not None
  assert sync.handoff.trade_snapshot.event_id == "44"
  assert sync.handoff.trade_snapshot.price == 2500.16
  assert sync.handoff.book_ticker_snapshot is not None
  assert sync.handoff.book_ticker_snapshot.bid_price == 2499.98
  assert sync.handoff.mini_ticker_snapshot is not None
  assert sync.handoff.mini_ticker_snapshot.close_price == 2500.15
  assert sync.handoff.kline_snapshot is not None
  assert sync.handoff.kline_snapshot.close_price == 2500.2
  assert sync.handoff.kline_snapshot.closed is False
  assert tuple((level.price, level.quantity) for level in sync.handoff.order_book_bids[:3]) == (
    (2499.95, 0.8),
    (2499.9, 0.55),
    (2499.7, 0.45),
  )
  assert tuple((level.price, level.quantity) for level in sync.handoff.order_book_asks[:3]) == (
    (2500.15, 0.65),
    (2500.2, 0.6),
    (2500.4, 0.75),
  )
  assert sync.handoff.channel_restore_state == "restored_from_exchange"
  assert sync.handoff.channel_restore_count == 2
  assert sync.handoff.channel_last_restored_at == clock()
  assert sync.handoff.last_market_event_at == clock()
  assert sync.handoff.last_trade_event_at == clock()
  assert sync.handoff.last_aggregate_trade_event_at == clock()
  assert sync.handoff.last_book_ticker_event_at == clock()
  assert sync.handoff.last_mini_ticker_event_at == clock()
  assert sync.handoff.last_kline_event_at == clock()
