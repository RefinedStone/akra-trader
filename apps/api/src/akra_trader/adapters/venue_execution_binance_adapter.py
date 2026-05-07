from __future__ import annotations

from akra_trader.adapters.venue_execution_common import *
from akra_trader.adapters.venue_execution_common import _build_kline_snapshot_from_stream_event
from akra_trader.adapters.venue_execution_common import _build_local_order_book_from_snapshot_row
from akra_trader.adapters.venue_execution_common import _build_order_result_from_exchange_row
from akra_trader.adapters.venue_execution_common import _coerce_depth_levels
from akra_trader.adapters.venue_execution_common import _coerce_float
from akra_trader.adapters.venue_execution_common import _coerce_int
from akra_trader.adapters.venue_execution_common import _coerce_string
from akra_trader.adapters.venue_execution_common import _depth_event_matches_local_book
from akra_trader.adapters.venue_execution_common import _max_datetime
from akra_trader.adapters.venue_execution_common import _serialize_order_book_side

from akra_trader.adapters.venue_execution_binance_orders_mixin import BinanceVenueExecutionOrderMixin
from akra_trader.adapters.venue_execution_binance_stream_helpers_mixin import BinanceVenueExecutionStreamHelperMixin
from akra_trader.adapters.venue_execution_binance_streams import BinanceCombinedWebSocketVenueStreamClient
from akra_trader.adapters.venue_execution_coinbase_streams import CoinbaseCombinedWebSocketVenueStreamClient
from akra_trader.adapters.venue_execution_kraken_streams import KrakenWebSocketMarketStreamClient

class BinanceVenueExecutionAdapter(
  BinanceVenueExecutionOrderMixin,
  BinanceVenueExecutionStreamHelperMixin,
  VenueExecutionPort,
):
  def __init__(
    self,
    *,
    venue: str = "binance",
    api_key: str | None = None,
    api_secret: str | None = None,
    exchange: VenueExecutionExchange | None = None,
    venue_stream_client: BinanceVenueStreamClient | None = None,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._venue = venue
    self._api_key = api_key
    self._api_secret = api_secret
    self._exchange = exchange
    self._clock = clock or (lambda: datetime.now(UTC))
    self._venue_stream_client = venue_stream_client
    self._active_stream_sessions: dict[str, BinanceVenueStreamSession] = {}
    self._order_states: dict[str, GuardedLiveVenueOrderResult] = {}
    self._local_order_books: dict[str, LocalOrderBookState] = {}

  def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []
    if self._exchange is None and not (self._api_key and self._api_secret):
      issues.append("venue_trade_credentials_missing")
    if self._venue_stream_client is None and not self._has_builtin_stream_transport():
      issues.append("venue_stream_transport_unavailable")
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
      if event_type == "streamHeartbeat":
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
        if bool(event.get("_snapshot_depth")):
          issues.extend(
            self._exchange_specific_snapshot_refresh_issues(
              previous_update_id=local_book.last_update_id if local_book is not None else order_book_last_update_id,
              next_update_id=depth_last_update_id or depth_first_update_id,
            )
          )
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
            f"{self._order_book_issue_prefix()}_gap_detected:"
            f"{order_book_last_update_id or 'none'}:"
            f"{depth_previous_update_id or depth_first_update_id or 'none'}"
          )
          issues.extend(
            self._exchange_specific_continuity_issues(
              local_book=local_book,
              first_update_id=depth_first_update_id,
              last_update_id=depth_last_update_id,
              previous_update_id=depth_previous_update_id,
            )
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
    if self._requires_order_state_sync(resolved_transport):
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
