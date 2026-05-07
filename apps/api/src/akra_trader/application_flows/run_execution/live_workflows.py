from __future__ import annotations

from datetime import datetime
from typing import Iterable
from uuid import uuid4

from akra_trader.application_flows.strategy_catalog import _build_run_experiment_metadata
from akra_trader.application_flows.strategy_catalog import _merge_preset_parameters
from akra_trader.application_support.run_surfaces import _ensure_order_action_allowed
from akra_trader.application_support.run_surfaces import _ensure_run_action_allowed
from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.services import summarize_performance


def start_live_run(
  flow,
  *,
  strategy_id: str,
  symbol: str,
  timeframe: str,
  initial_cash: float,
  fee_rate: float,
  slippage_bps: float,
  parameters: dict,
  replay_bars: int | None = 96,
  operator_reason: str = "guarded_live_launch",
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  return start_live_session(
    flow,
    strategy_id=strategy_id,
    symbol=symbol,
    timeframe=timeframe,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    parameters=parameters,
    replay_bars=replay_bars,
    operator_reason=operator_reason,
    start_at=start_at,
    end_at=end_at,
    tags=tags,
    preset_id=preset_id,
    benchmark_family=benchmark_family,
  )


def start_live_session(
  flow,
  *,
  strategy_id: str,
  symbol: str,
  timeframe: str,
  initial_cash: float,
  fee_rate: float,
  slippage_bps: float,
  parameters: dict,
  replay_bars: int | None = 96,
  operator_reason: str,
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  app = flow.app
  ensure_guarded_live_worker_start_allowed(flow)
  state = app._guarded_live_state.load_state()
  preset = app._resolve_experiment_preset(
    preset_id=preset_id,
    strategy_id=strategy_id,
    timeframe=timeframe,
  )
  resolved_parameters = _merge_preset_parameters(preset=preset, requested_parameters=parameters)
  strategy, metadata, strategy_snapshot = app._prepare_strategy(
    strategy_id=strategy_id,
    parameters=resolved_parameters,
  )
  experiment_metadata = _build_run_experiment_metadata(
    tags=tags,
    preset=preset,
    benchmark_family=benchmark_family,
    strategy_metadata=metadata,
  )
  config = RunConfig(
    run_id=str(uuid4()),
    mode=RunMode.LIVE,
    strategy_id=metadata.strategy_id,
    strategy_version=metadata.version,
    venue=app._guarded_live_venue,
    symbols=(symbol,),
    timeframe=timeframe,
    parameters=resolved_parameters,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    start_at=start_at,
    end_at=end_at,
  )
  loaded = app._data_engine.load_frame(config=config, active_bars=replay_bars)
  run = app._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
  run.provenance.experiment = experiment_metadata
  run.provenance.market_data = loaded.lineage
  run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
  app._attach_rerun_boundary(run)
  data = loaded.frame
  if data.empty:
    run.notes.append("No candles available for the requested range.")
    run.status = RunStatus.FAILED
    return app._runs.save_run(run)

  enriched = strategy.build_feature_frame(data, config.parameters)
  required_bars = max(strategy.warmup_spec().required_bars, 2)
  if len(enriched) < required_bars:
    run.status = RunStatus.FAILED
    run.notes.append(
      f"Guarded live worker requires at least {required_bars} candles to prime the current strategy state."
    )
    return app._runs.save_run(run)

  latest_row = enriched.iloc[-1]
  latest_timestamp = latest_row["timestamp"].to_pydatetime()
  latest_market_price = float(latest_row["close"])
  cache = app._build_guarded_live_cache(
    config=config,
    state=state,
    fallback_cash=initial_cash,
    latest_market_price=latest_market_price,
  )
  app._seed_guarded_live_runtime_state(
    run=run,
    state=state,
    cache=cache,
    timestamp=latest_timestamp,
    market_price=latest_market_price,
  )
  run.metrics = summarize_performance(
    initial_cash=run.config.initial_cash,
    equity_curve=run.equity_curve,
    closed_trades=run.closed_trades,
  )
  app._run_supervisor.start_mode(
    run=run,
    mode=RunMode.LIVE,
    mode_service=app._mode_service,
    replay_bars=None,
  )
  primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
  app._run_supervisor.start_worker_session(
    run=run,
    worker_kind=app._guarded_live_worker_kind,
    heartbeat_interval_seconds=app._guarded_live_worker_heartbeat_interval_seconds,
    heartbeat_timeout_seconds=app._guarded_live_worker_heartbeat_timeout_seconds,
    now=app._clock(),
    primed_candle_count=primed_candle_count,
    processed_tick_count=0,
    last_processed_candle_at=latest_timestamp,
    last_seen_candle_at=latest_timestamp,
  )
  run.notes.insert(
    0,
    (
      "Guarded live worker primed from recovered venue state and the latest market snapshot "
      f"using {primed_candle_count} candles."
    ),
  )
  saved_run = app._runs.save_run(run)
  session_handoff = app._activate_guarded_live_venue_session(
    run=saved_run,
    reason=operator_reason,
  )
  saved_run = app._runs.save_run(saved_run)
  app._claim_guarded_live_session_ownership(
    run=saved_run,
    actor="operator",
    reason=operator_reason,
    session_handoff=session_handoff,
  )
  app._append_guarded_live_audit_event(
    kind="guarded_live_worker_started",
    actor="operator",
    summary=f"Guarded-live worker started for {symbol}.",
    detail=(
      f"Reason: {operator_reason}. Strategy {strategy_id} launched with "
      f"{len(saved_run.orders)} recovered/open order(s)."
    ),
    run_id=saved_run.config.run_id,
    session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
  )
  return saved_run


def stop_live_run(flow, run_id: str) -> RunRecord | None:
  app = flow.app
  run = app._runs.get_run(run_id)
  if run is None:
    return None
  _ensure_run_action_allowed(
    run=run,
    capabilities=app.get_run_surface_capabilities(),
    action_key="stop_run",
  )
  app._run_supervisor.stop(
    run,
    reason="Guarded-live worker stopped by operator. Venue open orders remain operator-managed.",
  )
  saved_run = app._runs.save_run(run)
  session_handoff = app._release_guarded_live_venue_session(run=saved_run)
  saved_run = app._runs.save_run(saved_run)
  app._release_guarded_live_session_ownership(
    run=saved_run,
    actor="operator",
    reason="operator_stop",
    ownership_state="released",
    session_handoff=session_handoff,
  )
  app._append_guarded_live_audit_event(
    kind="guarded_live_worker_stopped",
    actor="operator",
    summary=f"Guarded-live worker stopped for {run.config.symbols[0]}.",
    detail="Operator stop requested for the guarded-live worker session.",
    run_id=saved_run.config.run_id,
    session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
  )
  return saved_run


def resume_guarded_live_run(
  flow,
  *,
  actor: str,
  reason: str,
) -> RunRecord:
  app = flow.app
  ensure_guarded_live_resume_allowed(flow)
  state = app._guarded_live_state.load_state()
  if state.ownership.owner_run_id is None:
    raise ValueError("No guarded-live session ownership is available to resume.")
  run = app._runs.get_run(state.ownership.owner_run_id)
  if run is None:
    raise LookupError("Owned guarded-live run not found")
  if run.config.mode != RunMode.LIVE:
    raise ValueError("Guarded-live ownership does not point to a live run.")
  if run.status in {RunStatus.STOPPED, RunStatus.COMPLETED}:
    raise ValueError("Terminal guarded-live runs cannot be resumed.")

  current_time = app._clock()
  if run.status == RunStatus.FAILED:
    run.status = RunStatus.RUNNING
    run.ended_at = None
  last_processed_candle_at = app._infer_last_processed_candle_at(run)
  app._run_supervisor.recover_worker_session(
    run=run,
    worker_kind=app._guarded_live_worker_kind,
    heartbeat_interval_seconds=app._guarded_live_worker_heartbeat_interval_seconds,
    heartbeat_timeout_seconds=app._guarded_live_worker_heartbeat_timeout_seconds,
    reason="operator_resume",
    now=current_time,
    started_at=run.started_at,
    primed_candle_count=app._infer_sandbox_primed_candle_count(run),
    processed_tick_count=run.provenance.runtime_session.processed_tick_count if run.provenance.runtime_session else 0,
    last_processed_candle_at=last_processed_candle_at,
    last_seen_candle_at=last_processed_candle_at,
  )
  session_restore = app._restore_guarded_live_venue_session(
    run=run,
    state=state,
    reason=reason,
  )
  if session_restore.state == "fallback_snapshot":
    try:
      app._sync_guarded_live_orders(run)
    except Exception as exc:
      run.notes.append(
        f"{current_time.isoformat()} | guarded_live_order_book_resume_warning | {exc}"
      )
  session_handoff = app._activate_guarded_live_venue_session(
    run=run,
    reason=reason,
  )
  app._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
  run.notes.append(
    f"{current_time.isoformat()} | guarded_live_worker_resumed | {reason}"
  )
  run.metrics = summarize_performance(
    initial_cash=run.config.initial_cash,
    equity_curve=run.equity_curve,
    closed_trades=run.closed_trades,
  )
  saved_run = app._runs.save_run(run)
  app._claim_guarded_live_session_ownership(
    run=saved_run,
    actor=actor,
    reason=reason,
    resumed=True,
    session_restore=session_restore,
    session_handoff=session_handoff,
  )
  app._append_guarded_live_audit_event(
    kind="guarded_live_worker_resumed",
    actor=actor,
    summary=f"Guarded-live worker resumed for {saved_run.config.symbols[0]}.",
    detail=f"Reason: {reason}.",
    run_id=saved_run.config.run_id,
    session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
  )
  return saved_run


def cancel_live_order(
  flow,
  *,
  run_id: str,
  order_id: str,
  actor: str,
  reason: str,
) -> RunRecord:
  app = flow.app
  run, order = app._prepare_guarded_live_order_action(
    run_id=run_id,
    order_id=order_id,
    require_active=True,
  )
  _ensure_order_action_allowed(
    run=run,
    order=order,
    capabilities=app.get_run_surface_capabilities(),
    action_key="cancel",
  )
  venue_result = app._venue_execution.cancel_order(
    symbol=run.config.symbols[0],
    order_id=order.order_id,
  )
  app._apply_guarded_live_synced_order_state(run=run, order=order, synced_state=venue_result)
  run.metrics = summarize_performance(
    initial_cash=run.config.initial_cash,
    equity_curve=run.equity_curve,
    closed_trades=run.closed_trades,
  )
  run.notes.append(
    f"{app._clock().isoformat()} | guarded_live_order_canceled | "
    f"Reason: {reason}. Operator requested cancel for {order.order_id} and venue returned {order.status.value}."
  )
  saved_run = app._runs.save_run(run)
  app._claim_guarded_live_session_ownership(
    run=saved_run,
    actor=actor,
    reason=reason,
  )
  app._append_guarded_live_audit_event(
    kind="guarded_live_order_canceled",
    actor=actor,
    summary=f"Guarded-live order canceled for {run.config.symbols[0]}.",
    detail=(
      f"Reason: {reason}. Operator canceled {order.order_id}; "
      f"remaining quantity is {app._resolve_guarded_live_order_remaining_quantity(order):.8f} "
      f"and venue state is {order.status.value}."
    ),
    run_id=saved_run.config.run_id,
    session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
  )
  return saved_run


def replace_live_order(
  flow,
  *,
  run_id: str,
  order_id: str,
  price: float,
  quantity: float | None,
  actor: str,
  reason: str,
) -> RunRecord:
  app = flow.app
  if price <= 0:
    raise ValueError("Replacement price must be positive.")
  ensure_guarded_live_live_order_replace_allowed(flow)
  run, order = app._prepare_guarded_live_order_action(
    run_id=run_id,
    order_id=order_id,
    require_active=True,
  )
  _ensure_order_action_allowed(
    run=run,
    order=order,
    capabilities=app.get_run_surface_capabilities(),
    action_key="replace",
  )
  remaining_quantity = app._resolve_guarded_live_order_remaining_quantity(order)
  replacement_quantity = quantity if quantity is not None else remaining_quantity
  if replacement_quantity <= app._guarded_live_balance_tolerance:
    raise ValueError("Replacement quantity resolved to zero.")
  if replacement_quantity - remaining_quantity > app._guarded_live_balance_tolerance:
    raise ValueError("Replacement quantity cannot exceed the current remaining order quantity.")

  cancel_result = app._venue_execution.cancel_order(
    symbol=run.config.symbols[0],
    order_id=order.order_id,
  )
  app._apply_guarded_live_synced_order_state(run=run, order=order, synced_state=cancel_result)
  if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
    raise RuntimeError(
      f"Guarded-live order replacement requires the current order to be canceled first: {order.order_id}"
    )
  run.metrics = summarize_performance(
    initial_cash=run.config.initial_cash,
    equity_curve=run.equity_curve,
    closed_trades=run.closed_trades,
  )
  run = app._runs.save_run(run)
  order = app._get_guarded_live_order(run=run, order_id=order_id)

  replacement_order = Order(
    run_id=run.config.run_id,
    instrument_id=order.instrument_id,
    side=order.side,
    quantity=replacement_quantity,
    requested_price=price,
    order_type=OrderType.LIMIT,
  )
  venue_result = app._submit_guarded_live_limit_order(
    run=run,
    order=replacement_order,
    limit_price=price,
  )
  replacement_order.order_id = venue_result.order_id
  replacement_order.created_at = venue_result.submitted_at
  replacement_order.updated_at = venue_result.updated_at or venue_result.submitted_at
  replacement_order.last_synced_at = venue_result.updated_at or venue_result.submitted_at
  replacement_order.status = app._map_guarded_live_order_status(
    venue_result.status,
    filled_quantity=venue_result.filled_amount or 0.0,
    remaining_quantity=venue_result.remaining_amount or 0.0,
  )
  if venue_result.average_fill_price is not None:
    replacement_order.average_fill_price = venue_result.average_fill_price
  replacement_order.fee_paid = venue_result.fee_paid or 0.0
  replacement_order.filled_quantity = venue_result.filled_amount or 0.0
  replacement_order.remaining_quantity = (
    venue_result.remaining_amount
    if venue_result.remaining_amount is not None
    else max(replacement_order.quantity - replacement_order.filled_quantity, 0.0)
  )
  if replacement_order.status == OrderStatus.FILLED:
    replacement_order.filled_at = venue_result.updated_at or venue_result.submitted_at
  run.orders.append(replacement_order)
  if replacement_order.filled_quantity > app._guarded_live_balance_tolerance:
    app._materialize_guarded_live_fill_delta(
      run=run,
      order=replacement_order,
      fill_quantity=replacement_order.filled_quantity,
      fee_paid=replacement_order.fee_paid,
      fill_price=venue_result.average_fill_price or replacement_order.requested_price,
      fill_timestamp=replacement_order.filled_at or venue_result.submitted_at,
    )
  run.metrics = summarize_performance(
    initial_cash=run.config.initial_cash,
    equity_curve=run.equity_curve,
    closed_trades=run.closed_trades,
  )
  run.notes.append(
    f"{app._clock().isoformat()} | guarded_live_order_replaced | "
    f"Reason: {reason}. Replaced {order.order_id} with {replacement_order.order_id} "
    f"for {replacement_quantity:.8f} at {price:.8f}."
  )
  saved_run = app._runs.save_run(run)
  app._claim_guarded_live_session_ownership(
    run=saved_run,
    actor=actor,
    reason=reason,
  )
  app._append_guarded_live_audit_event(
    kind="guarded_live_order_replaced",
    actor=actor,
    summary=f"Guarded-live order replaced for {run.config.symbols[0]}.",
    detail=(
      f"Reason: {reason}. Operator replaced {order.order_id} with {replacement_order.order_id} "
      f"for {replacement_quantity:.8f} at {price:.8f}; new venue state is {replacement_order.status.value}."
    ),
    run_id=saved_run.config.run_id,
    session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
  )
  return saved_run


def ensure_operator_control_runtime_allowed(flow, mode: RunMode) -> None:
  app = flow.app
  if mode not in {RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE}:
    return
  state = app._guarded_live_state.load_state()
  if state.kill_switch.state == "engaged":
    raise ValueError(
      "Guarded-live kill switch is engaged. Release it before starting operator-controlled runtime sessions."
    )


def ensure_guarded_live_worker_start_allowed(flow) -> None:
  app = flow.app
  ensure_operator_control_runtime_allowed(flow, RunMode.LIVE)
  status: GuardedLiveStatus = app.get_guarded_live_status()
  if status.running_live_count > 0:
    raise ValueError("A guarded-live worker is already running. Stop it before launching another.")
  if status.blockers:
    raise ValueError("Guarded-live launch is blocked: " + " ".join(status.blockers))


def ensure_guarded_live_live_order_replace_allowed(flow) -> None:
  app = flow.app
  state = app._guarded_live_state.load_state()
  if state.kill_switch.state == "engaged":
    raise ValueError("Guarded-live kill switch is engaged. Cancel venue orders instead of replacing them.")
  ready, issues = app._venue_execution.describe_capability()
  if not ready:
    raise RuntimeError(
      "Venue order execution is unavailable: "
      + (", ".join(issues) if issues else "adapter not ready")
      + "."
    )


def ensure_guarded_live_resume_allowed(flow) -> None:
  app = flow.app
  state = app._guarded_live_state.load_state()
  if state.kill_switch.state == "engaged":
    raise ValueError("Guarded-live kill switch is engaged. Release it before resuming live execution.")
  if state.recovery.state not in {"recovered", "recovered_with_warnings"}:
    raise ValueError("Guarded-live runtime recovery must be recorded before resume.")
  ready, issues = app._venue_execution.describe_capability()
  if not ready:
    raise RuntimeError(
      "Venue order execution is unavailable: "
      + (", ".join(issues) if issues else "adapter not ready")
      + "."
    )
  if state.ownership.state not in {"owned", "orphaned"}:
    raise ValueError("No guarded-live session ownership is available to resume.")
