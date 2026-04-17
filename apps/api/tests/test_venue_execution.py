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
from akra_trader.adapters.venue_execution import BinanceWebSocketMarketStreamClient
from akra_trader.adapters.venue_execution import BinanceWebSocketUserDataStreamClient


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
    self.closed = False

  def recv(self) -> str:
    while not self.closed:
      try:
        return self.messages.get(timeout=0.01)
      except Empty:
        continue
    raise RuntimeError("closed")

  def close(self) -> None:
    self.closed = True


class FakeExecutionExchange:
  def __init__(self, *, fetch_rows: list[dict[str, object]]) -> None:
    self._fetch_rows = fetch_rows

  def create_order(self, symbol, type, side, amount, price=None, params=None) -> dict[str, object]:
    raise AssertionError("create_order should not be called in this test")

  def fetch_orders(self, symbol=None, since=None, limit=None, params=None) -> list[dict[str, object]]:
    return list(self._fetch_rows)

  def cancel_order(self, id, symbol=None, params=None) -> dict[str, object]:
    raise AssertionError("cancel_order should not be called in this test")

  def fetch_open_orders(self, symbol=None) -> list[dict[str, object]]:
    return []

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
    ]
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
  assert handoff.order_book_state == "awaiting_depth"
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
    }
  )
  second_stream_session.push(
    {
      "e": "aggTrade",
      "E": int(clock().timestamp() * 1000),
      "T": int(clock().timestamp() * 1000),
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
    }
  )
  second_stream_session.push(
    {
      "e": "depthUpdate",
      "E": int(clock().timestamp() * 1000),
      "U": 101,
      "u": 102,
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
  assert second_sync.handoff.order_book_state == "resync_required"
  assert second_sync.handoff.order_book_last_update_id == 102
  assert second_sync.handoff.order_book_gap_count == 1
  assert second_sync.handoff.order_book_best_bid_price == 2499.4
  assert second_sync.handoff.order_book_best_bid_quantity == 1.25
  assert second_sync.handoff.order_book_best_ask_price == 2500.6
  assert second_sync.handoff.order_book_best_ask_quantity == 0.95
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
  assert released.failover_count == 1
  assert second_stream_session.closed is True


def test_binance_adapter_marks_order_book_resync_required_on_depth_sequence_gap() -> None:
  current_time = datetime(2026, 4, 17, 12, 0, tzinfo=UTC)
  clock = MutableClock(current_time)
  exchange = FakeExecutionExchange(fetch_rows=[])
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

  assert first_sync.handoff.order_book_state == "streaming"
  assert first_sync.handoff.order_book_last_update_id == 25
  assert second_sync.handoff.order_book_state == "resync_required"
  assert second_sync.handoff.order_book_gap_count == 1
  assert second_sync.handoff.order_book_last_update_id == 34
  assert second_sync.handoff.order_book_best_bid_price == 2497.5
  assert second_sync.handoff.order_book_best_ask_price == 2498.4
  assert "binance_order_book_gap_detected:25:29" in second_sync.handoff.issues
