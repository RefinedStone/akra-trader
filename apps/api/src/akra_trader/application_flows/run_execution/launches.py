from __future__ import annotations

from datetime import datetime
from typing import Iterable
from uuid import uuid4

from akra_trader.application_flows.strategy_catalog import _build_run_experiment_metadata
from akra_trader.application_flows.strategy_catalog import _merge_preset_parameters
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.services import summarize_performance
from akra_trader.runtime import StateCache


def _prepare_run_inputs(
  flow,
  *,
  strategy_id: str,
  timeframe: str,
  parameters: dict,
  tags: Iterable[str],
  preset_id: str | None,
  benchmark_family: str | None,
):
  app = flow.app
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
  return resolved_parameters, strategy, metadata, strategy_snapshot, experiment_metadata


def run_backtest(
  flow,
  *,
  strategy_id: str,
  symbol: str,
  timeframe: str,
  initial_cash: float,
  fee_rate: float,
  slippage_bps: float,
  parameters: dict,
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  app = flow.app
  resolved_parameters, strategy, metadata, strategy_snapshot, experiment_metadata = _prepare_run_inputs(
    flow,
    strategy_id=strategy_id,
    timeframe=timeframe,
    parameters=parameters,
    tags=tags,
    preset_id=preset_id,
    benchmark_family=benchmark_family,
  )
  config = RunConfig(
    run_id=str(uuid4()),
    mode=RunMode.BACKTEST,
    strategy_id=metadata.strategy_id,
    strategy_version=metadata.version,
    venue="binance",
    symbols=(symbol,),
    timeframe=timeframe,
    parameters=resolved_parameters,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    start_at=start_at,
    end_at=end_at,
  )
  if metadata.runtime == "freqtrade_reference":
    run = RunRecord(
      config=config,
      status=RunStatus.PENDING,
      provenance=RunProvenance(
        lane="reference",
        strategy=strategy_snapshot,
        experiment=experiment_metadata,
      ),
    )
    if app._freqtrade_reference is None:
      run.status = RunStatus.FAILED
      run.notes.append("Freqtrade reference adapter is not configured.")
    else:
      run = app._freqtrade_reference.execute_backtest(run, metadata)
    app._attach_rerun_boundary(run)
    return app._runs.save_run(run)
  run = app._simulate_run(
    config=config,
    strategy=strategy,
    strategy_snapshot=strategy_snapshot,
    active_bars=None,
  )
  run.provenance.experiment = experiment_metadata
  if run.status != RunStatus.FAILED:
    app._run_supervisor.complete(run)
  return app._runs.save_run(run)


def start_sandbox_run(
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
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  return flow.start_sandbox_session(
    strategy_id=strategy_id,
    symbol=symbol,
    timeframe=timeframe,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    parameters=parameters,
    replay_bars=replay_bars,
    start_at=start_at,
    end_at=end_at,
    tags=tags,
    preset_id=preset_id,
    benchmark_family=benchmark_family,
  )


def start_paper_run(
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
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  return flow.start_paper_session(
    strategy_id=strategy_id,
    symbol=symbol,
    timeframe=timeframe,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    parameters=parameters,
    replay_bars=replay_bars,
    start_at=start_at,
    end_at=end_at,
    tags=tags,
    preset_id=preset_id,
    benchmark_family=benchmark_family,
  )


def start_sandbox_session(
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
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  return flow.start_native_session(
    target_mode=RunMode.SANDBOX,
    reference_failure_copy="Sandbox worker sessions remain on the native engine for now.",
    primed_note_prefix="Sandbox worker session primed from the latest market snapshot",
    insufficient_candles_copy="Sandbox worker session requires at least",
    attach_runtime_session=True,
    strategy_id=strategy_id,
    symbol=symbol,
    timeframe=timeframe,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    parameters=parameters,
    replay_bars=replay_bars,
    start_at=start_at,
    end_at=end_at,
    tags=tags,
    preset_id=preset_id,
    benchmark_family=benchmark_family,
  )


def start_paper_session(
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
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  return flow.start_native_session(
    target_mode=RunMode.PAPER,
    reference_failure_copy="Paper trading remains on the native engine for now.",
    primed_note_prefix="Paper session primed from the latest market snapshot",
    insufficient_candles_copy="Paper session requires at least",
    attach_runtime_session=False,
    strategy_id=strategy_id,
    symbol=symbol,
    timeframe=timeframe,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    parameters=parameters,
    replay_bars=replay_bars,
    start_at=start_at,
    end_at=end_at,
    tags=tags,
    preset_id=preset_id,
    benchmark_family=benchmark_family,
  )


def start_native_session(
  flow,
  *,
  target_mode: RunMode,
  reference_failure_copy: str,
  primed_note_prefix: str,
  insufficient_candles_copy: str,
  attach_runtime_session: bool,
  strategy_id: str,
  symbol: str,
  timeframe: str,
  initial_cash: float,
  fee_rate: float,
  slippage_bps: float,
  parameters: dict,
  replay_bars: int | None = 96,
  start_at: datetime | None = None,
  end_at: datetime | None = None,
  tags: Iterable[str] = (),
  preset_id: str | None = None,
  benchmark_family: str | None = None,
) -> RunRecord:
  app = flow.app
  resolved_parameters, strategy, metadata, strategy_snapshot, experiment_metadata = _prepare_run_inputs(
    flow,
    strategy_id=strategy_id,
    timeframe=timeframe,
    parameters=parameters,
    tags=tags,
    preset_id=preset_id,
    benchmark_family=benchmark_family,
  )
  config = RunConfig(
    run_id=str(uuid4()),
    mode=target_mode,
    strategy_id=metadata.strategy_id,
    strategy_version=metadata.version,
    venue="binance",
    symbols=(symbol,),
    timeframe=timeframe,
    parameters=resolved_parameters,
    initial_cash=initial_cash,
    fee_rate=fee_rate,
    slippage_bps=slippage_bps,
    start_at=start_at,
    end_at=end_at,
  )
  app._ensure_operator_control_runtime_allowed(target_mode)
  if metadata.runtime == "freqtrade_reference":
    run = RunRecord(
      config=config,
      status=RunStatus.FAILED,
      provenance=RunProvenance(
        lane="reference",
        strategy=strategy_snapshot,
        experiment=experiment_metadata,
      ),
    )
    run.notes.append(
      "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
      + reference_failure_copy
    )
    return app._runs.save_run(run)

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
      f"{insufficient_candles_copy} {required_bars} candles to prime the current strategy state."
    )
    return app._runs.save_run(run)

  cache = StateCache(
    instrument_id=f"{config.venue}:{config.symbols[0]}",
    cash=config.initial_cash,
  )
  history = enriched.iloc[:]
  latest_row = history.iloc[-1]
  state = cache.snapshot(
    timestamp=latest_row["timestamp"].to_pydatetime(),
    parameters=config.parameters,
  )
  decision = strategy.evaluate(history, config.parameters, state)
  app._execution_engine.apply_decision(
    run=run,
    config=config,
    decision=decision,
    cache=cache,
    market_price=float(latest_row["close"]),
  )
  run.metrics = summarize_performance(
    initial_cash=config.initial_cash,
    equity_curve=run.equity_curve,
    closed_trades=run.closed_trades,
  )
  app._run_supervisor.start_mode(
    run=run,
    mode=target_mode,
    mode_service=app._mode_service,
    replay_bars=replay_bars if target_mode == RunMode.SANDBOX else None,
  )
  if attach_runtime_session:
    primed_timestamp = latest_row["timestamp"].to_pydatetime()
    primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
    app._run_supervisor.start_worker_session(
      run=run,
      worker_kind=app._sandbox_worker_kind,
      heartbeat_interval_seconds=app._sandbox_worker_heartbeat_interval_seconds,
      heartbeat_timeout_seconds=app._sandbox_worker_heartbeat_timeout_seconds,
      now=app._clock(),
      primed_candle_count=primed_candle_count,
      processed_tick_count=1,
      last_processed_candle_at=primed_timestamp,
      last_seen_candle_at=primed_timestamp,
    )
  primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
  run.notes.insert(
    0,
    f"{primed_note_prefix} using {primed_candle_count} candles.",
  )
  return app._runs.save_run(run)
