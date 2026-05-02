from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationGuardedLiveWorkerMixin:
  def _build_guarded_live_internal_snapshot(
    self,
    *,
    state: GuardedLiveState | None = None,
  ) -> GuardedLiveInternalStateSnapshot:
    captured_at = self._clock()
    exposures: list[GuardedLiveInternalExposure] = []
    open_order_count = 0
    running_run_ids: list[str] = []
    running_live_count = 0

    for mode in (RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE):
      for run in self._runs.list_runs(mode=mode.value):
        if run.status == RunStatus.RUNNING:
          running_run_ids.append(run.config.run_id)
          if mode == RunMode.LIVE:
            running_live_count += 1
        open_order_count += sum(
          1
          for order in run.orders
          if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}
        )
        for position in run.positions.values():
          if not position.is_open:
            continue
          exposures.append(
            GuardedLiveInternalExposure(
              run_id=run.config.run_id,
              mode=run.config.mode.value,
              instrument_id=position.instrument_id,
              quantity=position.quantity,
            )
          )

    if (
      running_live_count == 0
      and state is not None
      and state.recovery.state in {"recovered", "recovered_with_warnings"}
    ):
      for exposure in state.recovery.exposures:
        exposures.append(
          GuardedLiveInternalExposure(
            run_id="guarded_live_recovery_projection",
            mode=RunMode.LIVE.value,
            instrument_id=exposure.instrument_id,
            quantity=exposure.quantity,
          )
        )
      open_order_count += sum(
        1
        for order in state.recovery.open_orders
        if order.status.lower() not in {"closed", "filled", "canceled", "cancelled", "rejected"}
      )

    return GuardedLiveInternalStateSnapshot(
      captured_at=captured_at,
      running_run_ids=tuple(sorted(running_run_ids)),
      exposures=tuple(sorted(exposures, key=lambda exposure: (exposure.instrument_id, exposure.run_id))),
      open_order_count=open_order_count,
    )
  def _build_guarded_live_venue_mismatch_findings(
    self,
    *,
    internal_snapshot: GuardedLiveInternalStateSnapshot,
    venue_snapshot: GuardedLiveVenueStateSnapshot,
  ) -> list[GuardedLiveReconciliationFinding]:
    findings: list[GuardedLiveReconciliationFinding] = []
    if venue_snapshot.verification_state == "unavailable":
      return findings
    tolerance = self._guarded_live_balance_tolerance

    internal_exposure_by_asset = self._aggregate_internal_exposure_by_asset(internal_snapshot.exposures)
    quote_assets = self._collect_internal_quote_assets(internal_snapshot.exposures)
    venue_balance_by_asset = {
      balance.asset: balance.total
      for balance in venue_snapshot.balances
      if abs(balance.total) > tolerance
    }

    for asset, expected_quantity in sorted(internal_exposure_by_asset.items()):
      actual_quantity = venue_balance_by_asset.get(asset, 0.0)
      if abs(actual_quantity - expected_quantity) <= tolerance:
        continue
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_balance_mismatch",
          severity="critical",
          summary=f"Venue balance for {asset} does not match local open exposure.",
          detail=(
            f"Internal runtime exposure expects {expected_quantity:.8f} {asset}, "
            f"but venue snapshot reported {actual_quantity:.8f}."
          ),
        )
      )

    ignored_quote_assets = {"USD", "USDT", "USDC", "BUSD", *quote_assets}
    for asset, venue_quantity in sorted(venue_balance_by_asset.items()):
      if asset in internal_exposure_by_asset or asset in ignored_quote_assets:
        continue
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="unexpected_venue_balance_exposure",
          severity="critical",
          summary=f"Venue snapshot contains unexpected {asset} exposure.",
          detail=(
            f"Venue snapshot reported {venue_quantity:.8f} {asset} with no matching local runtime exposure."
          ),
        )
      )

    venue_open_order_count = len(venue_snapshot.open_orders)
    if internal_snapshot.open_order_count != venue_open_order_count:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_open_order_mismatch",
          severity="critical",
          summary="Venue open-order count does not match local runtime expectations.",
          detail=(
            f"Local runtime expects {internal_snapshot.open_order_count} open orders, "
            f"but venue snapshot reported {venue_open_order_count}."
          ),
        )
      )

    return findings
  def _aggregate_internal_exposure_by_asset(
    self,
    exposures: tuple[GuardedLiveInternalExposure, ...],
  ) -> dict[str, float]:
    aggregated: dict[str, float] = {}
    for exposure in exposures:
      asset = self._base_asset_from_instrument_id(exposure.instrument_id)
      aggregated[asset] = aggregated.get(asset, 0.0) + exposure.quantity
    return aggregated
  def _collect_internal_quote_assets(
    self,
    exposures: tuple[GuardedLiveInternalExposure, ...],
  ) -> set[str]:
    quote_assets: set[str] = set()
    for exposure in exposures:
      quote_assets.add(self._quote_asset_from_instrument_id(exposure.instrument_id))
    return quote_assets
  @staticmethod
  def _base_asset_from_instrument_id(instrument_id: str) -> str:
    symbol = instrument_id.split(":", 1)[1] if ":" in instrument_id else instrument_id
    return symbol.split("/", 1)[0]
  @staticmethod
  def _quote_asset_from_instrument_id(instrument_id: str) -> str:
    symbol = instrument_id.split(":", 1)[1] if ":" in instrument_id else instrument_id
    parts = symbol.split("/", 1)
    return parts[1] if len(parts) == 2 else "unknown"
  def maintain_sandbox_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]:
    maintained = 0
    recovered = 0
    ticks_processed = 0
    current_time = self._clock()
    for run in self._runs.list_runs(mode=RunMode.SANDBOX.value):
      if run.status != RunStatus.RUNNING:
        continue
      try:
        if force_recovery or self._run_supervisor.needs_worker_recovery(run=run, now=current_time):
          self._run_supervisor.recover_worker_session(
            run=run,
            worker_kind=self._sandbox_worker_kind,
            heartbeat_interval_seconds=self._sandbox_worker_heartbeat_interval_seconds,
            heartbeat_timeout_seconds=self._sandbox_worker_heartbeat_timeout_seconds,
            reason=recovery_reason,
            now=current_time,
            started_at=run.started_at,
            primed_candle_count=self._infer_sandbox_primed_candle_count(run),
            processed_tick_count=len(run.equity_curve),
            last_processed_candle_at=self._infer_last_processed_candle_at(run),
            last_seen_candle_at=self._infer_last_processed_candle_at(run),
          )
          run.notes.append(
            f"{current_time.isoformat()} | sandbox_worker_recovered | {recovery_reason}"
          )
          recovered += 1

        ticks_processed += self._advance_sandbox_worker_run(run)
        self._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
      except Exception as exc:
        self._run_supervisor.fail(
          run,
          reason=f"{current_time.isoformat()} | sandbox_worker_failed | {exc}",
          now=current_time,
        )
      self._runs.save_run(run)
      maintained += 1
    return {
      "maintained": maintained,
      "recovered": recovered,
      "ticks_processed": ticks_processed,
    }
  def _advance_sandbox_worker_run(self, run: RunRecord) -> int:
    session = run.provenance.runtime_session
    if session is None:
      return 0

    strategy = self._strategies.load(run.config.strategy_id)
    parameters = self._resolve_execution_parameters(run)
    candles = self._load_sandbox_worker_candles(run=run)
    if not candles:
      return 0

    latest_seen_candle_at = candles[-1].timestamp
    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=latest_seen_candle_at,
    )
    if (
      session.last_processed_candle_at is not None
      and latest_seen_candle_at <= session.last_processed_candle_at
    ):
      return 0

    enriched = strategy.build_feature_frame(candles_to_frame(candles), parameters)
    warmup = strategy.warmup_spec().required_bars
    if len(enriched) < max(warmup, 2):
      return 0

    cache = self._restore_state_cache(run)
    latest_processed_candle_at = session.last_processed_candle_at
    processed_ticks = 0
    for index in range(max(warmup, 2), len(enriched)):
      history = enriched.iloc[: index + 1]
      latest_row = history.iloc[-1]
      latest_timestamp = latest_row["timestamp"].to_pydatetime()
      if latest_processed_candle_at is not None and latest_timestamp <= latest_processed_candle_at:
        continue
      state = cache.snapshot(
        timestamp=latest_timestamp,
        parameters=parameters,
      )
      decision = strategy.evaluate(history, parameters, state)
      self._execution_engine.apply_decision(
        run=run,
        config=run.config,
        decision=decision,
        cache=cache,
        market_price=float(latest_row["close"]),
      )
      processed_ticks += 1
      latest_processed_candle_at = latest_timestamp

    if processed_ticks == 0:
      return 0

    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=latest_seen_candle_at,
      last_processed_candle_at=latest_processed_candle_at,
      processed_tick_count_increment=processed_ticks,
    )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    return processed_ticks
  def _load_sandbox_worker_candles(self, *, run: RunRecord) -> list:
    symbol = run.config.symbols[0]
    history_start_at = self._resolve_sandbox_worker_history_start_at(run)
    return self._market_data.get_candles(
      symbol=symbol,
      timeframe=run.config.timeframe,
      start_at=history_start_at,
      end_at=run.config.end_at,
      limit=None,
    )
  def _resolve_sandbox_worker_history_start_at(self, run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    return (
      run.config.start_at
      or (market_data.effective_start_at if market_data is not None else None)
      or (market_data.requested_start_at if market_data is not None else None)
    )
  def _resolve_execution_parameters(self, run: RunRecord) -> dict:
    strategy_snapshot = run.provenance.strategy
    if strategy_snapshot is None:
      return deepcopy(run.config.parameters)
    return deepcopy(strategy_snapshot.parameter_snapshot.resolved or run.config.parameters)
  def _restore_state_cache(self, run: RunRecord) -> StateCache:
    instrument_id = f"{run.config.venue}:{run.config.symbols[0]}"
    cash = run.equity_curve[-1].cash if run.equity_curve else run.config.initial_cash
    cache = StateCache(instrument_id=instrument_id, cash=cash)
    position = run.positions.get(instrument_id)
    cache.apply(
      cash=cash,
      position=position if position is not None and position.is_open else None,
    )
    return cache
  def _infer_last_processed_candle_at(self, run: RunRecord) -> datetime | None:
    return infer_last_processed_candle_at_support(run)
  def _infer_sandbox_primed_candle_count(self, run: RunRecord) -> int:
    return infer_sandbox_primed_candle_count_support(run)
  def maintain_guarded_live_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]:
    return maintain_guarded_live_worker_sessions_support(
      self,
      force_recovery=force_recovery,
      recovery_reason=recovery_reason,
    )
  def _sync_guarded_live_orders(self, run: RunRecord) -> int:
    return sync_guarded_live_orders_support(self, run)
  def _sync_guarded_live_session(
    self,
    *,
    run: RunRecord,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> dict[str, object]:
    return sync_guarded_live_session_support(
      self,
      run=run,
      handoff=handoff,
    )
  def _apply_guarded_live_synced_order_state(
    self,
    *,
    run: RunRecord,
    order: Order,
    synced_state: GuardedLiveVenueOrderResult,
  ) -> int:
    return apply_guarded_live_synced_order_state_support(
      self,
      run=run,
      order=order,
      synced_state=synced_state,
    )
  def _materialize_guarded_live_fill_delta(
    self,
    *,
    run: RunRecord,
    order: Order,
    fill_quantity: float,
    fee_paid: float,
    fill_price: float,
    fill_timestamp: datetime,
  ) -> None:
    materialize_guarded_live_fill_delta_support(
      self,
      run=run,
      order=order,
      fill_quantity=fill_quantity,
      fee_paid=fee_paid,
      fill_price=fill_price,
      fill_timestamp=fill_timestamp,
    )
  @staticmethod
  def _map_guarded_live_order_status(
    status: str,
    *,
    filled_quantity: float,
    remaining_quantity: float,
  ) -> OrderStatus:
    return map_guarded_live_order_status_support(
      status,
      filled_quantity=filled_quantity,
      remaining_quantity=remaining_quantity,
    )
  def _advance_guarded_live_worker_run(self, run: RunRecord) -> dict[str, int]:
    return advance_guarded_live_worker_run_support(self, run)
  def _apply_guarded_live_decision(
    self,
    *,
    run: RunRecord,
    decision,
    cache: StateCache,
    market_price: float,
  ) -> int:
    return apply_guarded_live_decision_support(
      self,
      run=run,
      decision=decision,
      cache=cache,
      market_price=market_price,
    )
  def _submit_guarded_live_market_order(
    self,
    *,
    run: RunRecord,
    order: Order,
    market_price: float,
  ) -> GuardedLiveVenueOrderResult:
    return submit_guarded_live_market_order_support(
      self,
      run=run,
      order=order,
      market_price=market_price,
    )
  def _submit_guarded_live_limit_order(
    self,
    *,
    run: RunRecord,
    order: Order,
    limit_price: float,
  ) -> GuardedLiveVenueOrderResult:
    return submit_guarded_live_limit_order_support(
      self,
      run=run,
      order=order,
      limit_price=limit_price,
    )
  def _guarded_live_delivery_targets(self) -> tuple[str, ...]:
    return (
      "operator_visibility",
      "guarded_live_status",
      "control_room",
      *self._operator_alert_delivery.list_targets(),
    )
  def _resolve_guarded_live_market_data_timeframes(
    self,
    *,
    live_runs: list[RunRecord],
  ) -> tuple[str, ...]:
    timeframes = list(self._guarded_live_market_data_timeframes)
    for run in live_runs:
      if run.config.timeframe not in timeframes:
        timeframes.append(run.config.timeframe)
    return tuple(timeframes or ("5m",))
  def _collect_guarded_live_channel_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    threshold_seconds = max(self._guarded_live_worker_heartbeat_timeout_seconds, 1)
    threshold = timedelta(seconds=threshold_seconds)
    handoff_anchor = handoff.last_sync_at or handoff.handed_off_at or current_time
    has_critical = False

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_state == "unavailable":
      add_finding(
        "depth/order-book supervision is unavailable.",
        detected_at=handoff.last_sync_at or handoff.handed_off_at or current_time,
        critical=True,
      )
    elif handoff.order_book_state == "resync_required":
      add_finding(
        "depth/order-book continuity requires a resync before the local book is trustworthy.",
        detected_at=handoff.last_sync_at or handoff.handed_off_at or current_time,
        critical=True,
      )

    for channel_name, event_at, critical_channel in self._resolve_guarded_live_market_channel_activity(
      handoff=handoff
    ):
      if event_at is None:
        if current_time - handoff_anchor >= threshold:
          add_finding(
            f"{channel_name} has not produced any events within {threshold_seconds}s of the active venue handoff.",
            detected_at=handoff_anchor,
            critical=critical_channel,
          )
        continue
      if current_time - event_at > threshold:
        add_finding(
          f"{channel_name} is stale; last event at {event_at.isoformat()}.",
          detected_at=event_at,
          critical=critical_channel,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical
