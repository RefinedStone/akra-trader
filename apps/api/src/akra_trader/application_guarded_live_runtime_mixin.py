from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationGuardedLiveRuntimeMixin:
  def _ensure_guarded_live_live_order_replace_allowed(self) -> None:
    self._run_execution_flow.ensure_guarded_live_live_order_replace_allowed()
  def _ensure_guarded_live_resume_allowed(self) -> None:
    self._run_execution_flow.ensure_guarded_live_resume_allowed()
  def _persist_guarded_live_state(self, state: GuardedLiveState) -> GuardedLiveState:
    return self._guarded_live_state.save_state(state)
  def _claim_guarded_live_session_ownership(
    self,
    *,
    run: RunRecord,
    actor: str,
    reason: str,
    resumed: bool = False,
    session_restore: GuardedLiveVenueSessionRestore | None = None,
    session_handoff: GuardedLiveVenueSessionHandoff | None = None,
  ) -> None:
    session = run.provenance.runtime_session
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    existing = state.ownership
    self._persist_guarded_live_state(
      replace(
        state,
        ownership=GuardedLiveSessionOwnership(
          state="owned",
          owner_run_id=run.config.run_id,
          owner_session_id=session.session_id if session is not None else None,
          symbol=run.config.symbols[0] if run.config.symbols else None,
          claimed_at=existing.claimed_at if existing.owner_run_id == run.config.run_id else current_time,
          claimed_by=existing.claimed_by if existing.owner_run_id == run.config.run_id else actor,
          last_heartbeat_at=session.last_heartbeat_at if session is not None else current_time,
          last_order_sync_at=current_time,
          last_resumed_at=current_time if resumed else existing.last_resumed_at,
          last_reason=reason,
          last_released_at=None,
        ),
        order_book=self._build_guarded_live_order_book_sync(run=run),
        session_restore=self._resolve_guarded_live_session_restore_state(
          run=run,
          existing=state.session_restore,
          session_restore=session_restore,
        ),
        session_handoff=self._resolve_guarded_live_session_handoff_state(
          run=run,
          existing=state.session_handoff,
          session_handoff=session_handoff,
        ),
      )
    )
  def _release_guarded_live_session_ownership(
    self,
    *,
    run: RunRecord,
    actor: str,
    reason: str,
    ownership_state: str,
    session_handoff: GuardedLiveVenueSessionHandoff | None = None,
  ) -> None:
    session = run.provenance.runtime_session
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    existing = state.ownership
    self._persist_guarded_live_state(
      replace(
        state,
        ownership=GuardedLiveSessionOwnership(
          state=ownership_state,
          owner_run_id=run.config.run_id,
          owner_session_id=session.session_id if session is not None else existing.owner_session_id,
          symbol=run.config.symbols[0] if run.config.symbols else existing.symbol,
          claimed_at=existing.claimed_at or run.started_at,
          claimed_by=existing.claimed_by or actor,
          last_heartbeat_at=session.last_heartbeat_at if session is not None else existing.last_heartbeat_at,
          last_order_sync_at=current_time,
          last_resumed_at=existing.last_resumed_at,
          last_reason=reason,
          last_released_at=current_time if ownership_state == "released" else existing.last_released_at,
        ),
        order_book=self._build_guarded_live_order_book_sync(run=run),
        session_restore=self._resolve_guarded_live_session_restore_state(
          run=run,
          existing=state.session_restore,
        ),
        session_handoff=self._resolve_guarded_live_session_handoff_state(
          run=run,
          existing=state.session_handoff,
          session_handoff=session_handoff,
        ),
      )
    )
  def _resolve_guarded_live_session_restore_state(
    self,
    *,
    run: RunRecord,
    existing: GuardedLiveVenueSessionRestore,
    session_restore: GuardedLiveVenueSessionRestore | None = None,
  ) -> GuardedLiveVenueSessionRestore:
    session = run.provenance.runtime_session
    session_id = session.session_id if session is not None else existing.owner_session_id
    symbol = run.config.symbols[0] if run.config.symbols else existing.symbol
    if session_restore is not None:
      return replace(
        session_restore,
        venue=session_restore.venue or run.config.venue,
        symbol=session_restore.symbol or symbol,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    if existing.owner_run_id == run.config.run_id:
      return replace(
        existing,
        venue=existing.venue or run.config.venue,
        symbol=existing.symbol or symbol,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    return GuardedLiveVenueSessionRestore(
      state="not_restored",
      source="live_start",
      venue=run.config.venue,
      symbol=symbol,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
    )
  def _resolve_guarded_live_session_handoff_state(
    self,
    *,
    run: RunRecord,
    existing: GuardedLiveVenueSessionHandoff,
    session_handoff: GuardedLiveVenueSessionHandoff | None = None,
  ) -> GuardedLiveVenueSessionHandoff:
    session = run.provenance.runtime_session
    session_id = session.session_id if session is not None else existing.owner_session_id
    symbol = run.config.symbols[0] if run.config.symbols else existing.symbol
    if session_handoff is not None:
      return replace(
        session_handoff,
        venue=session_handoff.venue or run.config.venue,
        symbol=session_handoff.symbol or symbol,
        timeframe=session_handoff.timeframe or run.config.timeframe,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    if existing.owner_run_id == run.config.run_id:
      return replace(
        existing,
        venue=existing.venue or run.config.venue,
        symbol=existing.symbol or symbol,
        timeframe=existing.timeframe or run.config.timeframe,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    return GuardedLiveVenueSessionHandoff(
      state="inactive",
      source="live_start",
      venue=run.config.venue,
      symbol=symbol,
      timeframe=run.config.timeframe,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
    )
  def _activate_guarded_live_venue_session(
    self,
    *,
    run: RunRecord,
    reason: str,
  ) -> GuardedLiveVenueSessionHandoff:
    session = run.provenance.runtime_session
    handoff = self._venue_execution.handoff_session(
      symbol=run.config.symbols[0],
      timeframe=run.config.timeframe,
      owner_run_id=run.config.run_id,
      owner_session_id=session.session_id if session is not None else None,
      owned_order_ids=tuple(order.order_id for order in run.orders),
    )
    current_time = self._clock()
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_venue_session_handed_off | "
      f"source={handoff.source}; transport={handoff.transport}; state={handoff.state}; "
      f"supervision={handoff.supervision_state}; order_book={handoff.order_book_state}; "
      f"continuation={handoff.channel_continuation_state}; "
      f"failovers={handoff.failover_count}; reason={reason}"
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_venue_session_handed_off",
      actor="system",
      summary=f"Guarded-live venue session handed off for {run.config.symbols[0]}.",
      detail=(
        f"Reason: {reason}. Source {handoff.source} activated transport {handoff.transport} "
        f"with session {handoff.venue_session_id or 'n/a'}. Supervision "
        f"{handoff.supervision_state} with coverage {', '.join(handoff.coverage) or 'none'} "
        f"and order-book state {handoff.order_book_state}."
      ),
      run_id=run.config.run_id,
      session_id=session.session_id if session is not None else None,
    )
    return handoff
  def _release_guarded_live_venue_session(
    self,
    *,
    run: RunRecord,
  ) -> GuardedLiveVenueSessionHandoff:
    state = self._guarded_live_state.load_state()
    current_handoff = state.session_handoff
    if current_handoff.owner_run_id != run.config.run_id:
      return current_handoff
    released = self._venue_execution.release_session(handoff=current_handoff)
    current_time = self._clock()
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_venue_session_released | "
      f"source={released.source}; transport={released.transport}; state={released.state}; "
      f"supervision={released.supervision_state}; failovers={released.failover_count}"
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_venue_session_released",
      actor="system",
      summary=f"Guarded-live venue session released for {run.config.symbols[0]}.",
      detail=(
        f"Source {released.source} released transport {released.transport} "
        f"for session {released.venue_session_id or 'n/a'} after "
        f"{released.failover_count} failover(s)."
      ),
      run_id=run.config.run_id,
      session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
    )
    return released
  def _restore_guarded_live_venue_session(
    self,
    *,
    run: RunRecord,
    state: GuardedLiveState,
    reason: str,
  ) -> GuardedLiveVenueSessionRestore:
    current_time = self._clock()
    symbol = run.config.symbols[0]
    session = run.provenance.runtime_session
    session_id = session.session_id if session is not None else None
    owned_order_ids = tuple(order.order_id for order in run.orders)
    try:
      venue_restore = self._venue_execution.restore_session(
        symbol=symbol,
        owned_order_ids=owned_order_ids,
      )
    except Exception as exc:
      venue_restore = GuardedLiveVenueSessionRestore(
        state="unavailable",
        restored_at=current_time,
        source="venue_execution",
        venue=run.config.venue,
        symbol=symbol,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
        issues=(f"venue_session_restore_failed:{exc}",),
      )
    venue_restore = replace(
      venue_restore,
      restored_at=venue_restore.restored_at or current_time,
      venue=venue_restore.venue or run.config.venue,
      symbol=venue_restore.symbol or symbol,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
    )
    if self._guarded_live_venue_restore_has_state(venue_restore):
      self._apply_guarded_live_restored_session(
        run=run,
        session_restore=venue_restore,
      )
      run.notes.append(
        f"{current_time.isoformat()} | guarded_live_venue_session_restored | "
        f"source={venue_restore.source}; open_orders={len(venue_restore.open_orders)}; "
        f"tracked_orders={len(venue_restore.synced_orders)}; reason={reason}"
      )
      self._append_guarded_live_audit_event(
        kind="guarded_live_venue_session_restored",
        actor="system",
        summary=f"Guarded-live venue session restored for {symbol}.",
        detail=(
          f"Resume reason: {reason}. Source {venue_restore.source} restored "
          f"{len(venue_restore.synced_orders)} tracked order state(s) and "
          f"{len(venue_restore.open_orders)} open venue order(s)."
        ),
        run_id=run.config.run_id,
        session_id=session_id,
      )
      return venue_restore

    self._seed_guarded_live_execution_order_book(state.order_book)
    fallback_issues = tuple(dict.fromkeys((*venue_restore.issues, "venue_session_restore_unavailable")))
    fallback_restore = GuardedLiveVenueSessionRestore(
      state="fallback_snapshot",
      restored_at=current_time,
      source="durable_order_book_snapshot",
      venue=run.config.venue,
      symbol=symbol,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
      open_orders=state.order_book.open_orders,
      synced_orders=(),
      issues=fallback_issues,
    )
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_venue_session_restore_fallback | "
      f"source={fallback_restore.source}; issues={', '.join(fallback_issues) if fallback_issues else 'none'}; "
      f"reason={reason}"
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_venue_session_restore_fallback",
      actor="system",
      summary=f"Guarded-live session restore fell back to persisted order book for {symbol}.",
      detail=(
        f"Resume reason: {reason}. Venue-native restore was unavailable, so the persisted "
        f"order-book snapshot was reseeded instead. Issues: "
        f"{', '.join(fallback_issues) if fallback_issues else 'none'}."
      ),
      run_id=run.config.run_id,
      session_id=session_id,
    )
    return fallback_restore
  @staticmethod
  def _guarded_live_venue_restore_has_state(
    session_restore: GuardedLiveVenueSessionRestore,
  ) -> bool:
    return guarded_live_venue_restore_has_state_support(session_restore)
  def _apply_guarded_live_restored_session(
    self,
    *,
    run: RunRecord,
    session_restore: GuardedLiveVenueSessionRestore,
  ) -> int:
    return apply_guarded_live_restored_session_support(
      self,
      run=run,
      session_restore=session_restore,
    )
  def _materialize_guarded_live_restored_order(
    self,
    *,
    run: RunRecord,
    synced_state: GuardedLiveVenueOrderResult | None,
    open_order: GuardedLiveVenueOpenOrder | None,
  ) -> Order:
    return materialize_guarded_live_restored_order_support(
      self,
      run=run,
      synced_state=synced_state,
      open_order=open_order,
    )
  def _build_guarded_live_order_book_sync(self, *, run: RunRecord) -> GuardedLiveOrderBookSync:
    session = run.provenance.runtime_session
    open_orders = self._build_guarded_live_open_orders_from_run(run)
    current_time = self._clock()
    return GuardedLiveOrderBookSync(
      state="synced" if open_orders else "empty",
      synced_at=current_time,
      owner_run_id=run.config.run_id,
      owner_session_id=session.session_id if session is not None else None,
      symbol=run.config.symbols[0] if run.config.symbols else None,
      open_orders=open_orders,
      issues=(),
    )
  def _build_guarded_live_open_orders_from_run(
    self,
    run: RunRecord,
  ) -> tuple[GuardedLiveVenueOpenOrder, ...]:
    symbol = run.config.symbols[0] if run.config.symbols else None
    open_orders: list[GuardedLiveVenueOpenOrder] = []
    for order in run.orders:
      if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
        continue
      open_orders.append(
        GuardedLiveVenueOpenOrder(
          order_id=order.order_id,
          symbol=symbol or order.instrument_id.split(":", 1)[-1],
          side=order.side.value,
          amount=self._resolve_guarded_live_order_remaining_quantity(order),
          status=order.status.value,
          price=order.requested_price,
        )
      )
    open_orders.sort(key=lambda item: (item.symbol, item.order_id))
    return tuple(open_orders)
  def _seed_guarded_live_execution_order_book(
    self,
    order_book: GuardedLiveOrderBookSync,
  ) -> None:
    if not order_book.open_orders:
      return
    setter = getattr(self._venue_execution, "set_order_state", None)
    if not callable(setter):
      return
    for order in order_book.open_orders:
      setter(
        order.order_id,
        symbol=order.symbol,
        side=order.side,
        amount=order.amount,
        requested_price=order.price,
        status=order.status,
        updated_at=order_book.synced_at or self._clock(),
        filled_amount=0.0,
        remaining_amount=order.amount,
      )
  def _prepare_guarded_live_order_action(
    self,
    *,
    run_id: str,
    order_id: str,
    require_active: bool,
  ) -> tuple[RunRecord, Order]:
    run = self._runs.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    if run.config.mode != RunMode.LIVE:
      raise ValueError("Guarded-live order controls are available only for live runs.")
    if self._sync_guarded_live_orders(run) > 0:
      run = self._runs.save_run(run)
    order = self._get_guarded_live_order(run=run, order_id=order_id)
    if require_active and order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
      raise ValueError("Only active guarded-live venue orders can be controlled.")
    return run, order
  @staticmethod
  def _get_guarded_live_order(
    *,
    run: RunRecord,
    order_id: str,
  ) -> Order:
    for order in run.orders:
      if order.order_id == order_id:
        return order
    raise LookupError("Order not found")
  @staticmethod
  def _resolve_guarded_live_order_remaining_quantity(order: Order) -> float:
    if order.remaining_quantity is not None:
      return max(order.remaining_quantity, 0.0)
    return max(order.quantity - order.filled_quantity, 0.0)
  def _select_guarded_live_recovery_snapshot(
    self,
    state: GuardedLiveState,
  ) -> GuardedLiveVenueStateSnapshot:
    snapshot = state.reconciliation.venue_snapshot
    if (
      snapshot is not None
      and snapshot.verification_state != "unavailable"
      and snapshot.venue == self._guarded_live_venue
    ):
      return snapshot
    return self._venue_state.capture_snapshot()
  def _recover_exposures_from_venue_snapshot(
    self,
    snapshot: GuardedLiveVenueStateSnapshot,
  ) -> tuple[tuple[GuardedLiveRecoveredExposure, ...], tuple[str, ...]]:
    tolerance = self._guarded_live_balance_tolerance
    instruments = self._market_data.list_instruments()
    quote_assets = {instrument.quote_currency for instrument in instruments}
    recovered: list[GuardedLiveRecoveredExposure] = []
    issues: list[str] = []

    for balance in snapshot.balances:
      if abs(balance.total) <= tolerance:
        continue
      if balance.asset in quote_assets:
        continue
      instrument = self._resolve_recovery_instrument(balance.asset, snapshot.open_orders, instruments)
      if instrument is None:
        issues.append(f"unmapped_recovery_asset:{balance.asset}")
        recovered.append(
          GuardedLiveRecoveredExposure(
            instrument_id=f"{self._guarded_live_venue}:{balance.asset}",
            symbol=balance.asset,
            asset=balance.asset,
            quantity=balance.total,
          )
        )
        continue
      recovered.append(
        GuardedLiveRecoveredExposure(
          instrument_id=f"{self._guarded_live_venue}:{instrument.symbol}",
          symbol=instrument.symbol,
          asset=balance.asset,
          quantity=balance.total,
        )
      )
    recovered.sort(key=lambda exposure: (exposure.symbol, exposure.asset))
    return tuple(recovered), tuple(issues)
  def _resolve_recovery_instrument(
    self,
    asset: str,
    open_orders: tuple[GuardedLiveVenueOpenOrder, ...],
    instruments: list[Instrument],
  ) -> Instrument | None:
    for order in open_orders:
      if order.symbol.split("/", 1)[0] != asset:
        continue
      for instrument in instruments:
        if instrument.symbol == order.symbol:
          return instrument

    candidates = [instrument for instrument in instruments if instrument.base_currency == asset]
    if not candidates:
      return None
    if len(candidates) == 1:
      return candidates[0]
    candidates.sort(key=lambda instrument: (instrument.quote_currency != "USDT", instrument.symbol))
    return candidates[0]
  def _append_guarded_live_audit_event(
    self,
    *,
    kind: str,
    actor: str,
    summary: str,
    detail: str,
    run_id: str | None = None,
    session_id: str | None = None,
  ) -> None:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    event = OperatorAuditEvent(
      event_id=f"{kind}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind=kind,
      summary=summary,
      detail=detail,
      run_id=run_id,
      session_id=session_id,
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        audit_events=(event, *state.audit_events),
      )
    )
  def _build_guarded_live_cache(
    self,
    *,
    config: RunConfig,
    state: GuardedLiveState,
    fallback_cash: float,
    latest_market_price: float,
  ) -> StateCache:
    instrument_id = f"{config.venue}:{config.symbols[0]}"
    quote_asset = config.symbols[0].split("/", 1)[1] if "/" in config.symbols[0] else "USDT"
    cash = self._resolve_guarded_live_cash_balance(
      state=state,
      quote_asset=quote_asset,
      fallback_cash=fallback_cash,
    )
    cache = StateCache(instrument_id=instrument_id, cash=cash)
    recovered_exposure = next(
      (exposure for exposure in state.recovery.exposures if exposure.instrument_id == instrument_id),
      None,
    )
    if recovered_exposure is not None and recovered_exposure.quantity > self._guarded_live_balance_tolerance:
      recovered_at = state.recovery.recovered_at or self._clock()
      cache.apply(
        cash=cash,
        position=Position(
          instrument_id=instrument_id,
          quantity=recovered_exposure.quantity,
          average_price=latest_market_price,
          opened_at=recovered_at,
          updated_at=recovered_at,
        ),
      )
    return cache
  def _resolve_guarded_live_cash_balance(
    self,
    *,
    state: GuardedLiveState,
    quote_asset: str,
    fallback_cash: float,
  ) -> float:
    snapshot = state.reconciliation.venue_snapshot
    if snapshot is None:
      return fallback_cash
    for balance in snapshot.balances:
      if balance.asset == quote_asset:
        return balance.free if balance.free is not None else balance.total
    return fallback_cash
  def _seed_guarded_live_runtime_state(
    self,
    *,
    run: RunRecord,
    state: GuardedLiveState,
    cache: StateCache,
    timestamp: datetime,
    market_price: float,
  ) -> None:
    if cache.position is not None and cache.position.is_open:
      run.positions[cache.position.instrument_id] = cache.position

    symbol = run.config.symbols[0]
    recovered_order_count = 0
    for recovered_order in state.recovery.open_orders:
      if recovered_order.symbol != symbol:
        continue
      if recovered_order.status.lower() in {"closed", "filled", "canceled", "cancelled", "rejected"}:
        continue
      recovered_order_count += 1
      run.orders.append(
        Order(
          run_id=run.config.run_id,
          instrument_id=f"{run.config.venue}:{symbol}",
          side=self._resolve_order_side(recovered_order.side),
          quantity=recovered_order.amount,
          requested_price=recovered_order.price or market_price,
          order_type=OrderType.LIMIT if recovered_order.price is not None else OrderType.MARKET,
          status=OrderStatus.OPEN,
          order_id=recovered_order.order_id,
          created_at=state.recovery.recovered_at or self._clock(),
          updated_at=state.recovery.recovered_at or self._clock(),
          filled_quantity=0.0,
          remaining_quantity=recovered_order.amount,
          last_synced_at=state.recovery.recovered_at or self._clock(),
        )
      )
      self._seed_guarded_live_execution_order_state(
        order=run.orders[-1],
        symbol=symbol,
      )

    run.equity_curve.append(
      build_equity_point(
        timestamp=timestamp,
        cash=cache.cash,
        position=cache.position if cache.position and cache.position.is_open else None,
        market_price=market_price,
      )
    )
    run.notes.append(
      "Recovered guarded-live runtime state with "
      f"{1 if cache.position is not None and cache.position.is_open else 0} exposure(s) "
      f"and {recovered_order_count} open venue order(s)."
    )
  def _seed_guarded_live_execution_order_state(
    self,
    *,
    order: Order,
    symbol: str,
  ) -> None:
    setter = getattr(self._venue_execution, "set_order_state", None)
    if not callable(setter):
      return
    setter(
      order.order_id,
      symbol=symbol,
      side=order.side.value,
      amount=order.quantity,
      requested_price=order.requested_price,
      status=order.status.value,
      updated_at=order.updated_at or order.created_at,
      average_fill_price=order.average_fill_price,
      fee_paid=order.fee_paid,
      filled_amount=order.filled_quantity,
      remaining_amount=self._resolve_guarded_live_order_remaining_quantity(order),
    )
  @staticmethod
  def _resolve_order_side(side: str) -> OrderSide:
    return OrderSide.SELL if side.lower() == OrderSide.SELL.value else OrderSide.BUY
  def _count_running_runs(self, mode: RunMode) -> int:
    return sum(
      1
      for run in self._runs.list_runs(mode=mode.value)
      if run.status == RunStatus.RUNNING
    )
  def _stop_runs_for_kill_switch(self, *, actor: str, reason: str) -> list[str]:
    stopped_runs: list[str] = []
    for mode, label in (
      (RunMode.SANDBOX, "Sandbox worker"),
      (RunMode.PAPER, "Paper session"),
      (RunMode.LIVE, "Guarded-live worker"),
    ):
      for run in self._runs.list_runs(mode=mode.value):
        if run.status != RunStatus.RUNNING:
          continue
        self._run_supervisor.stop(
          run,
          reason=f"{label} stopped by guarded-live kill switch ({actor}: {reason}).",
        )
        self._runs.save_run(run)
        stopped_runs.append(run.config.run_id)
    return stopped_runs
  def _build_guarded_live_reconciliation_findings(self) -> list[GuardedLiveReconciliationFinding]:
    _, _, findings = self._build_guarded_live_reconciliation_result()
    return findings
  def _build_guarded_live_reconciliation(
    self,
    *,
    state: GuardedLiveState,
    checked_at: datetime,
    checked_by: str,
  ) -> GuardedLiveReconciliation:
    internal_snapshot, venue_snapshot, findings = self._build_guarded_live_reconciliation_result(state=state)
    return GuardedLiveReconciliation(
      state="clear" if not findings else "issues_detected",
      checked_at=checked_at,
      checked_by=checked_by,
      scope="venue_state",
      summary=(
        "Guarded-live reconciliation verified venue state against local runtime state."
        if not findings
        else f"Guarded-live reconciliation found {len(findings)} venue-state issue(s)."
      ),
      findings=tuple(findings),
      internal_snapshot=internal_snapshot,
      venue_snapshot=venue_snapshot,
    )
