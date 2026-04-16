from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from typing import NamedTuple

import pandas as pd

from akra_trader.domain.models import Candle
from akra_trader.domain.models import ExecutionPlan
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import RuntimeSessionState
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import StrategySnapshot
from akra_trader.domain.services import apply_signal
from akra_trader.domain.services import build_equity_point
from akra_trader.lineage import build_aggregate_dataset_identity
from akra_trader.lineage import build_aggregate_sync_checkpoint_identity
from akra_trader.lineage import combine_reproducibility_states
from akra_trader.ports import MarketDataPort


class LoadedFrame(NamedTuple):
  frame: pd.DataFrame
  lineage: MarketDataLineage
  lineage_by_symbol: dict[str, MarketDataLineage]


def candles_to_frame(candles: list[Candle]) -> pd.DataFrame:
  return pd.DataFrame(
    [
      {
        "timestamp": candle.timestamp,
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
      }
      for candle in candles
    ]
  )


class ExecutionModeService:
  _legacy_aliases = {"paper": RunMode.PAPER.value}

  def normalize(self, mode: str | None) -> str | None:
    if mode is None:
      return None
    return self._legacy_aliases.get(mode, mode)

  def launch_note(self, mode: RunMode, replay_bars: int | None = None) -> str | None:
    suffix = self._build_replay_suffix(replay_bars)
    if mode == RunMode.SANDBOX:
      return (
        "Sandbox worker session is active on the native engine with heartbeat and recovery supervision."
        f"{suffix}"
      )
    if mode == RunMode.PAPER:
      return "Paper run starts from the latest simulated market snapshot and remains isolated from venue-backed live execution."
    if mode == RunMode.LIVE:
      return "Live mode is reserved for guarded venue-backed execution."
    return None

  @staticmethod
  def _build_replay_suffix(replay_bars: int | None) -> str:
    if replay_bars is None:
      return ""
    return f" Initial priming window: {replay_bars} bars."


class DataEngine:
  def __init__(self, market_data: MarketDataPort) -> None:
    self._market_data = market_data

  def load_frame(self, *, config: RunConfig, active_bars: int | None) -> LoadedFrame:
    candles_by_symbol: dict[str, list[Candle]] = {}
    lineage_by_symbol: dict[str, MarketDataLineage] = {}
    for symbol in config.symbols:
      candles = self._market_data.get_candles(
        symbol=symbol,
        timeframe=config.timeframe,
        start_at=config.start_at,
        end_at=config.end_at,
        limit=active_bars,
      )
      candles_by_symbol[symbol] = candles
      lineage_by_symbol[symbol] = self._market_data.describe_lineage(
        symbol=symbol,
        timeframe=config.timeframe,
        candles=candles,
        start_at=config.start_at,
        end_at=config.end_at,
        limit=active_bars,
      )

    primary_symbol = config.symbols[0]
    return LoadedFrame(
      frame=candles_to_frame(candles_by_symbol[primary_symbol]),
      lineage=self._aggregate_lineage(config=config, lineage_by_symbol=lineage_by_symbol),
      lineage_by_symbol=lineage_by_symbol,
    )

  def _aggregate_lineage(
    self,
    *,
    config: RunConfig,
    lineage_by_symbol: dict[str, MarketDataLineage],
  ) -> MarketDataLineage:
    lineages = list(lineage_by_symbol.values())
    if not lineages:
      return MarketDataLineage(
        provider="unknown",
        venue=config.venue,
        symbols=config.symbols,
        timeframe=config.timeframe,
        reproducibility_state="range_only",
        requested_start_at=config.start_at,
        requested_end_at=config.end_at,
        sync_status="unknown",
      )

    effective_starts = [lineage.effective_start_at for lineage in lineages if lineage.effective_start_at is not None]
    effective_ends = [lineage.effective_end_at for lineage in lineages if lineage.effective_end_at is not None]
    last_sync_times = [lineage.last_sync_at for lineage in lineages if lineage.last_sync_at is not None]
    prefixed_issues = tuple(
      dict.fromkeys(
        f"{symbol}:{issue}"
        for symbol, lineage in lineage_by_symbol.items()
        for issue in lineage.issues
      )
    )
    reproducibility_state = combine_reproducibility_states(
      [lineage.reproducibility_state for lineage in lineages]
    )
    symbol_identities = {
      symbol: lineage.dataset_identity
      for symbol, lineage in lineage_by_symbol.items()
      if lineage.dataset_identity is not None
    }
    symbol_checkpoint_ids = {
      symbol: lineage.sync_checkpoint_id
      for symbol, lineage in lineage_by_symbol.items()
      if lineage.sync_checkpoint_id is not None
    }
    dataset_identity = None
    if reproducibility_state == "pinned" and len(symbol_identities) == len(lineage_by_symbol):
      dataset_identity = build_aggregate_dataset_identity(
        provider=lineages[0].provider,
        venue=lineages[0].venue,
        timeframe=config.timeframe,
        symbol_identities=symbol_identities,
      )
    sync_checkpoint_id = None
    if len(symbol_checkpoint_ids) == len(lineage_by_symbol):
      sync_checkpoint_id = build_aggregate_sync_checkpoint_identity(
        provider=lineages[0].provider,
        venue=lineages[0].venue,
        timeframe=config.timeframe,
        symbol_checkpoint_ids=symbol_checkpoint_ids,
      )

    return MarketDataLineage(
      provider=lineages[0].provider,
      venue=lineages[0].venue,
      symbols=config.symbols,
      timeframe=config.timeframe,
      dataset_identity=dataset_identity,
      sync_checkpoint_id=sync_checkpoint_id,
      reproducibility_state=reproducibility_state,
      requested_start_at=config.start_at,
      requested_end_at=config.end_at,
      effective_start_at=min(effective_starts) if effective_starts else None,
      effective_end_at=max(effective_ends) if effective_ends else None,
      candle_count=sum(lineage.candle_count for lineage in lineages),
      sync_status=self._aggregate_sync_status(lineages),
      last_sync_at=max(last_sync_times) if last_sync_times else None,
      issues=prefixed_issues,
    )

  def _aggregate_sync_status(self, lineages: list[MarketDataLineage]) -> str:
    status_priority = {
      "error": 5,
      "stale": 4,
      "empty": 3,
      "delegated": 2,
      "fixture": 1,
      "synced": 0,
      "unknown": -1,
    }
    return max(lineages, key=lambda lineage: status_priority.get(lineage.sync_status, -1)).sync_status


class StateCache:
  def __init__(self, *, instrument_id: str, cash: float) -> None:
    self.instrument_id = instrument_id
    self.cash = cash
    self.position: Position | None = None
    self.last_price: float | None = None

  def mark_price(self, market_price: float) -> None:
    self.last_price = market_price

  def snapshot(self, *, timestamp: datetime, parameters: dict) -> StrategyExecutionState:
    return StrategyExecutionState(
      timestamp=timestamp,
      instrument_id=self.instrument_id,
      has_position=self.position is not None and self.position.is_open,
      cash=self.cash,
      position_size=self.position.quantity if self.position else 0.0,
      parameters=parameters,
    )

  def apply(self, *, cash: float, position: Position | None) -> None:
    self.cash = cash
    self.position = position


class RiskEngine:
  def review(self, decision: StrategyDecisionEnvelope) -> StrategyDecisionEnvelope:
    state = decision.context.state
    plan = decision.execution
    normalized_fraction = min(max(plan.size_fraction, 0.0), min(max(plan.max_position_fraction, 0.0), 1.0))
    normalized_plan = replace(plan, size_fraction=normalized_fraction)

    if plan.reduce_only and decision.signal.action == SignalAction.BUY:
      return self._block(decision, normalized_plan, "reduce_only_prevents_buy")
    if decision.signal.action == SignalAction.BUY and state.has_position and not normalized_plan.allow_scale_in:
      return self._block(decision, normalized_plan, "scale_in_disabled")
    if decision.signal.action == SignalAction.SELL and not state.has_position:
      return self._block(decision, normalized_plan, "no_position_to_reduce")
    if decision.signal.action == SignalAction.BUY and state.cash <= 0:
      return self._block(decision, normalized_plan, "insufficient_cash")
    if normalized_fraction == 0 and decision.signal.action != SignalAction.HOLD:
      return self._block(decision, normalized_plan, "size_fraction_zero")

    if normalized_plan != plan:
      trace = {**decision.trace, "risk_adjustments": ("normalized_size_fraction",)}
      return replace(decision, execution=normalized_plan, trace=trace)
    return decision

  def _block(
    self,
    decision: StrategyDecisionEnvelope,
    execution: ExecutionPlan,
    reason: str,
  ) -> StrategyDecisionEnvelope:
    blocked_signal = SignalDecision(
      timestamp=decision.signal.timestamp,
      action=SignalAction.HOLD,
      size_fraction=0.0,
      confidence=decision.signal.confidence,
      tags=(*decision.signal.tags, "risk_blocked"),
      reason=reason,
    )
    trace = {**decision.trace, "risk_block": reason}
    return StrategyDecisionEnvelope(
      signal=blocked_signal,
      rationale=f"{decision.rationale} RiskEngine blocked execution: {reason}.",
      context=decision.context,
      execution=replace(execution, size_fraction=0.0),
      trace=trace,
    )


class ExecutionEngine:
  def __init__(self, risk_engine: RiskEngine | None = None) -> None:
    self._risk_engine = risk_engine or RiskEngine()

  def apply_decision(
    self,
    *,
    run: RunRecord,
    config: RunConfig,
    decision: StrategyDecisionEnvelope,
    cache: StateCache,
    market_price: float,
  ) -> None:
    reviewed = self._risk_engine.review(decision)
    cash, position, order, fill, closed_trade = apply_signal(
      run_id=config.run_id,
      instrument_id=cache.instrument_id,
      signal=reviewed.signal,
      execution=reviewed.execution,
      market_price=market_price,
      position=cache.position,
      cash=cache.cash,
      fee_rate=config.fee_rate,
      slippage_bps=config.slippage_bps,
    )
    cache.mark_price(market_price)
    cache.apply(cash=cash, position=position)

    if order is not None:
      run.orders.append(order)
    if fill is not None:
      run.fills.append(fill)
    if position is not None:
      run.positions[position.instrument_id] = position
    if closed_trade is not None:
      run.closed_trades.append(closed_trade)

    run.equity_curve.append(
      build_equity_point(
        timestamp=reviewed.signal.timestamp,
        cash=cache.cash,
        position=cache.position if cache.position and cache.position.is_open else None,
        market_price=market_price,
      )
    )
    run.notes.append(
      f"{reviewed.context.timestamp.isoformat()} | "
      f"{reviewed.signal.action.value} | {reviewed.rationale}"
    )


class RunSupervisor:
  def create_native_run(
    self,
    *,
    config: RunConfig,
    strategy: StrategySnapshot | None = None,
  ) -> RunRecord:
    return RunRecord(
      config=config,
      status=RunStatus.RUNNING,
      provenance=RunProvenance(lane="native", strategy=strategy),
    )

  def complete(self, run: RunRecord) -> RunRecord:
    run.status = RunStatus.COMPLETED
    run.ended_at = datetime.now(UTC)
    return run

  def start_mode(
    self,
    *,
    run: RunRecord,
    mode: RunMode,
    mode_service: ExecutionModeService,
    replay_bars: int | None = None,
  ) -> RunRecord:
    if run.status == RunStatus.FAILED:
      return run
    run.status = RunStatus.RUNNING
    note = mode_service.launch_note(mode, replay_bars=replay_bars)
    if note:
      run.notes.append(note)
    return run

  def stop(self, run: RunRecord, *, reason: str) -> RunRecord:
    run.status = RunStatus.STOPPED
    run.ended_at = datetime.now(UTC)
    if run.provenance.runtime_session is not None:
      run.provenance.runtime_session.lifecycle_state = "stopped"
      run.provenance.runtime_session.last_heartbeat_at = run.ended_at
    run.notes.append(reason)
    return run

  def fail(
    self,
    run: RunRecord,
    *,
    reason: str,
    now: datetime | None = None,
  ) -> RunRecord:
    failed_at = now or datetime.now(UTC)
    run.status = RunStatus.FAILED
    run.ended_at = failed_at
    if run.provenance.runtime_session is not None:
      run.provenance.runtime_session.lifecycle_state = "failed"
      run.provenance.runtime_session.last_heartbeat_at = failed_at
    run.notes.append(reason)
    return run

  def start_worker_session(
    self,
    *,
    run: RunRecord,
    worker_kind: str,
    heartbeat_interval_seconds: int,
    heartbeat_timeout_seconds: int,
    now: datetime | None = None,
    primed_candle_count: int = 0,
    processed_tick_count: int = 0,
    last_processed_candle_at: datetime | None = None,
    last_seen_candle_at: datetime | None = None,
  ) -> RunRecord:
    started_at = now or datetime.now(UTC)
    run.provenance.runtime_session = RuntimeSessionState(
      worker_kind=worker_kind,
      lifecycle_state="active",
      started_at=started_at,
      primed_candle_count=primed_candle_count,
      processed_tick_count=processed_tick_count,
      last_heartbeat_at=started_at,
      last_processed_candle_at=last_processed_candle_at,
      last_seen_candle_at=last_seen_candle_at,
      heartbeat_interval_seconds=heartbeat_interval_seconds,
      heartbeat_timeout_seconds=heartbeat_timeout_seconds,
    )
    return run

  def needs_worker_recovery(
    self,
    *,
    run: RunRecord,
    now: datetime | None = None,
  ) -> bool:
    if run.status != RunStatus.RUNNING:
      return False
    session = run.provenance.runtime_session
    if session is None:
      return True
    if session.lifecycle_state == "stopped":
      return False
    heartbeat_at = session.last_heartbeat_at or session.started_at
    current = now or datetime.now(UTC)
    elapsed_seconds = (current - heartbeat_at).total_seconds()
    return elapsed_seconds >= session.heartbeat_timeout_seconds

  def heartbeat_worker_session(
    self,
    *,
    run: RunRecord,
    now: datetime | None = None,
  ) -> RunRecord:
    session = run.provenance.runtime_session
    if session is None:
      return run
    session.lifecycle_state = "active"
    session.last_heartbeat_at = now or datetime.now(UTC)
    return run

  def recover_worker_session(
    self,
    *,
    run: RunRecord,
    worker_kind: str,
    heartbeat_interval_seconds: int,
    heartbeat_timeout_seconds: int,
    reason: str,
    now: datetime | None = None,
    started_at: datetime | None = None,
    primed_candle_count: int = 0,
    processed_tick_count: int = 0,
    last_processed_candle_at: datetime | None = None,
    last_seen_candle_at: datetime | None = None,
  ) -> RunRecord:
    recovered_at = now or datetime.now(UTC)
    session = run.provenance.runtime_session
    if session is None:
      session = RuntimeSessionState(
        worker_kind=worker_kind,
        lifecycle_state="active",
        started_at=started_at or recovered_at,
        primed_candle_count=primed_candle_count,
        processed_tick_count=processed_tick_count,
        last_heartbeat_at=recovered_at,
        last_processed_candle_at=last_processed_candle_at,
        last_seen_candle_at=last_seen_candle_at,
        heartbeat_interval_seconds=heartbeat_interval_seconds,
        heartbeat_timeout_seconds=heartbeat_timeout_seconds,
        recovery_count=1,
        last_recovered_at=recovered_at,
        last_recovery_reason=reason,
      )
      run.provenance.runtime_session = session
      return run

    session.worker_kind = worker_kind
    session.lifecycle_state = "active"
    session.last_heartbeat_at = recovered_at
    session.last_processed_candle_at = last_processed_candle_at or session.last_processed_candle_at
    session.last_seen_candle_at = last_seen_candle_at or session.last_seen_candle_at
    session.primed_candle_count = max(session.primed_candle_count, primed_candle_count)
    session.processed_tick_count = max(session.processed_tick_count, processed_tick_count)
    session.heartbeat_interval_seconds = heartbeat_interval_seconds
    session.heartbeat_timeout_seconds = heartbeat_timeout_seconds
    session.recovery_count += 1
    session.last_recovered_at = recovered_at
    session.last_recovery_reason = reason
    return run

  def record_worker_market_progress(
    self,
    *,
    run: RunRecord,
    last_seen_candle_at: datetime | None = None,
    last_processed_candle_at: datetime | None = None,
    processed_tick_count_increment: int = 0,
  ) -> RunRecord:
    session = run.provenance.runtime_session
    if session is None:
      return run
    if last_seen_candle_at is not None:
      session.last_seen_candle_at = last_seen_candle_at
    if last_processed_candle_at is not None:
      session.last_processed_candle_at = last_processed_candle_at
    if processed_tick_count_increment > 0:
      session.processed_tick_count += processed_tick_count_increment
    return run
