from __future__ import annotations

from akra_trader.adapters.venue_execution_common import *

class BinanceVenueExecutionStreamHelperMixin:
  def _resolve_stream_clients(self, *, symbol: str, timeframe: str) -> tuple[BinanceVenueStreamClient, ...]:
    clients: list[BinanceVenueStreamClient] = []
    if self._venue_stream_client is not None:
      clients.append(self._venue_stream_client)
    elif self._venue == "binance" and self._api_key and symbol and timeframe:
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
    elif self._venue == "coinbase" and self._api_key and self._api_secret and symbol and timeframe:
      try:
        clients.append(
          CoinbaseCombinedWebSocketVenueStreamClient(
            api_key=self._api_key,
            signing_key=self._api_secret,
            symbol=symbol,
            timeframe=timeframe,
            clock=self._clock,
          )
        )
      except Exception:
        pass
    if symbol and timeframe:
      push_client = self._resolve_push_stream_client(symbol=symbol, timeframe=timeframe)
      if push_client is not None:
        clients.append(push_client)
    return tuple(clients)

  def _resolve_push_stream_client(self, *, symbol: str, timeframe: str) -> BinanceVenueStreamClient | None:
    if not symbol or not timeframe:
      return None
    if self._venue == "binance":
      return BinanceWebSocketMarketStreamClient(
        symbol=symbol,
        timeframe=timeframe,
        clock=self._clock,
      )
    if self._venue == "coinbase" and timeframe == "5m":
      return CoinbaseAdvancedTradeWebSocketMarketStreamClient(
        symbol=symbol,
        timeframe=timeframe,
        clock=self._clock,
      )
    if self._venue == "kraken" and _timeframe_to_minutes(timeframe) is not None:
      return KrakenWebSocketMarketStreamClient(
        symbol=symbol,
        timeframe=timeframe,
        clock=self._clock,
      )
    return None

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
      if self._is_fallback_transport(session.transport):
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
    if transport in {"binance_multi_stream_websocket", "binance_user_data_websocket"}:
      return BINANCE_VENUE_STREAM_COVERAGE
    if transport == "binance_market_data_websocket":
      return BINANCE_MARKET_PUSH_VENUE_STREAM_COVERAGE
    if transport in {"coinbase_advanced_trade_combined_websocket", "coinbase_advanced_trade_user_websocket"}:
      return COINBASE_ADVANCED_TRADE_VENUE_STREAM_COVERAGE
    if transport == "coinbase_advanced_trade_market_websocket":
      return COINBASE_ADVANCED_TRADE_MARKET_STREAM_COVERAGE
    if transport == "kraken_spot_market_websocket":
      return KRAKEN_SPOT_MARKET_STREAM_COVERAGE
    if transport in {None, "venue_stream_unavailable"}:
      return ()
    return ()

  @staticmethod
  def _supervision_state_for_transport(transport: str | None) -> str:
    if transport in {
      "binance_multi_stream_websocket",
      "binance_user_data_websocket",
      "binance_market_data_websocket",
      "coinbase_advanced_trade_combined_websocket",
      "coinbase_advanced_trade_user_websocket",
      "coinbase_advanced_trade_market_websocket",
      "kraken_spot_market_websocket",
    }:
      return "streaming"
    return "inactive"

  @staticmethod
  def _requires_order_state_sync(transport: str | None) -> bool:
    return transport in {
      "binance_market_data_websocket",
      "coinbase_advanced_trade_market_websocket",
      "kraken_spot_market_websocket",
    }

  @staticmethod
  def _is_fallback_transport(transport: str | None) -> bool:
    return transport in {
      "binance_market_data_websocket",
      "coinbase_advanced_trade_market_websocket",
      "kraken_spot_market_websocket",
    }

  def _has_builtin_stream_transport(self) -> bool:
    return self._venue in {"binance", "coinbase", "kraken"}

  @staticmethod
  def _source_for_transport(transport: str | None) -> str:
    if transport in {"binance_multi_stream_websocket", "binance_user_data_websocket"}:
      return "binance_venue_stream"
    if transport == "binance_market_data_websocket":
      return "binance_market_push_transport"
    if transport in {"coinbase_advanced_trade_combined_websocket", "coinbase_advanced_trade_user_websocket"}:
      return "coinbase_venue_stream"
    if transport == "coinbase_advanced_trade_market_websocket":
      return "coinbase_market_push_transport"
    if transport == "kraken_spot_market_websocket":
      return "kraken_market_push_transport"
    return "venue_stream_transport"

  @staticmethod
  def _stream_issue_prefix_for_transport(transport: str | None) -> str:
    if transport in {"binance_multi_stream_websocket", "binance_user_data_websocket", "binance_market_data_websocket"}:
      return "binance_venue_stream"
    if transport in {"coinbase_advanced_trade_combined_websocket", "coinbase_advanced_trade_user_websocket"}:
      return "coinbase_venue_stream"
    if transport == "coinbase_advanced_trade_market_websocket":
      return "coinbase_venue_stream"
    if transport == "kraken_spot_market_websocket":
      return "kraken_venue_stream"
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

  def _order_book_issue_prefix(self) -> str:
    return f"{self._venue or 'venue'}_order_book"

  def _exchange_specific_snapshot_refresh_issues(
    self,
    *,
    previous_update_id: int | None,
    next_update_id: int | None,
  ) -> tuple[str, ...]:
    if self._venue not in {"coinbase", "kraken"}:
      return ()
    if previous_update_id is None:
      return ()
    return (
      f"{self._order_book_issue_prefix()}_snapshot_refresh:"
      f"{previous_update_id}:{next_update_id or 'none'}",
    )

  def _exchange_specific_continuity_issues(
    self,
    *,
    local_book: LocalOrderBookState | None,
    first_update_id: int | None,
    last_update_id: int | None,
    previous_update_id: int | None,
  ) -> tuple[str, ...]:
    if local_book is None or local_book.last_update_id is None:
      return ()

    prefix = self._order_book_issue_prefix()
    if self._venue == "binance":
      if previous_update_id is not None and previous_update_id != local_book.last_update_id:
        return (
          f"{prefix}_bridge_previous_mismatch:{local_book.last_update_id}:{previous_update_id}",
        )
      expected_next = local_book.last_update_id + 1
      return (
        f"{prefix}_bridge_range_mismatch:{expected_next}:{first_update_id or 'none'}:{last_update_id or 'none'}",
      )

    if self._venue == "coinbase":
      return (
        f"{prefix}_sequence_mismatch:"
        f"{local_book.last_update_id}:{previous_update_id or 'none'}:{last_update_id or first_update_id or 'none'}",
      )

    return ()

  def _inspect_order_book_snapshot(
    self,
    *,
    snapshot: dict[str, Any],
  ) -> tuple[str, ...]:
    prefix = self._order_book_issue_prefix()
    bids = _coerce_depth_levels(snapshot.get("bids"))
    asks = _coerce_depth_levels(snapshot.get("asks"))
    issues: list[str] = []

    if not bids:
      issues.append(f"{prefix}_snapshot_missing_side:bids")
    if not asks:
      issues.append(f"{prefix}_snapshot_missing_side:asks")

    if bids and asks and bids[0][0] >= asks[0][0]:
      issues.append(f"{prefix}_snapshot_crossed:{bids[0][0]}:{asks[0][0]}")

    previous_price: float | None = None
    for index, (price, _quantity) in enumerate(bids, start=1):
      if previous_price is not None and price >= previous_price:
        issues.append(f"{prefix}_snapshot_non_monotonic:bids:{index}:{price}:{previous_price}")
      previous_price = price

    previous_price = None
    for index, (price, _quantity) in enumerate(asks, start=1):
      if previous_price is not None and price <= previous_price:
        issues.append(f"{prefix}_snapshot_non_monotonic:asks:{index}:{price}:{previous_price}")
      previous_price = price

    return tuple(dict.fromkeys(issues))

  def _rebuild_local_order_book_from_snapshot(
    self,
    *,
    symbol: str,
    order_book_key: str,
    rebuild_count: int,
    reason: str,
  ) -> dict[str, object]:
    current_time = self._clock()
    issue_prefix = self._order_book_issue_prefix()
    if not symbol:
      return {
        "book": None,
        "state": "rebuild_failed",
        "issues": (f"{issue_prefix}_snapshot_failed:missing_symbol",),
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
      snapshot_issues = self._inspect_order_book_snapshot(snapshot=snapshot)
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
        "issues": (f"{issue_prefix}_snapshot_failed:{reason}:{exc}",),
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
      "issues": snapshot_issues,
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
      and not issue.startswith("coinbase_venue_stream")
      and not issue.startswith("kraken_venue_stream")
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
    return build_trade_exchange(
      venue=self._venue,
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
