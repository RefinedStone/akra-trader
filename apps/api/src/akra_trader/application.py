from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from numbers import Number
from typing import Callable
from uuid import uuid4

from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonNarrative
from akra_trader.domain.models import RunComparisonMetricRow
from akra_trader.domain.models import RunComparisonRun
from akra_trader.domain.models import GuardedLiveKillSwitch
from akra_trader.domain.models import GuardedLiveInternalExposure
from akra_trader.domain.models import GuardedLiveInternalStateSnapshot
from akra_trader.domain.models import GuardedLiveReconciliation
from akra_trader.domain.models import GuardedLiveReconciliationFinding
from akra_trader.domain.models import GuardedLiveRecoveredExposure
from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import GuardedLiveRuntimeRecovery
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import OperatorAuditEvent
from akra_trader.domain.models import OperatorVisibility
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyParameterSnapshot
from akra_trader.domain.models import StrategyRegistration
from akra_trader.domain.models import StrategySnapshot
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.domain.services import summarize_performance
from akra_trader.lineage import build_rerun_boundary_identity
from akra_trader.ports import GuardedLiveStatePort
from akra_trader.ports import MarketDataPort
from akra_trader.ports import ReferenceCatalogPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.ports import StrategyRuntime
from akra_trader.ports import VenueStatePort
from akra_trader.runtime import DataEngine
from akra_trader.runtime import ExecutionEngine
from akra_trader.runtime import ExecutionModeService
from akra_trader.runtime import RunSupervisor
from akra_trader.runtime import StateCache
from akra_trader.runtime import candles_to_frame


COMPARISON_METRICS: tuple[tuple[str, str, str, bool], ...] = (
  ("total_return_pct", "Total return", "pct", True),
  ("max_drawdown_pct", "Max drawdown", "pct", False),
  ("win_rate_pct", "Win rate", "pct", True),
  ("trade_count", "Trades", "count", True),
)

COMPARISON_INTENT_DEFAULT = "benchmark_validation"
COMPARISON_INTENT_WEIGHTS: dict[str, dict[str, float]] = {
  "benchmark_validation": {
    "return": 0.8,
    "drawdown": 1.5,
    "win_rate": 0.7,
    "trade_count": 0.12,
    "native_reference_bonus": 8.0,
    "reference_bonus": 3.0,
    "status_bonus": 1.5,
    "benchmark_story_bonus": 1.5,
    "reference_floor": 1.0,
  },
  "execution_regression": {
    "return": 0.9,
    "drawdown": 1.9,
    "win_rate": 1.0,
    "trade_count": 0.4,
    "native_reference_bonus": 3.0,
    "reference_bonus": 1.0,
    "status_bonus": 3.0,
    "benchmark_story_bonus": 0.8,
    "reference_floor": 1.0,
  },
  "strategy_tuning": {
    "return": 2.0,
    "drawdown": 0.7,
    "win_rate": 1.3,
    "trade_count": 0.35,
    "native_reference_bonus": 1.5,
    "reference_bonus": 0.5,
    "status_bonus": 0.8,
    "benchmark_story_bonus": 0.4,
    "reference_floor": 0.5,
  },
}

COMPARISON_INTENT_COPY: dict[str, dict[str, str]] = {
  "benchmark_validation": {
    "title_prefix": "Benchmark validation",
    "summary_prefix": "Validation view",
    "partial_summary": (
      "Benchmark validation falls back to persisted reference provenance because direct metric "
      "deltas are partial."
    ),
    "lane_prefix": "Validation context",
    "activity_prefix": "Validation signal",
    "reference_prefix": "Benchmark evidence",
  },
  "execution_regression": {
    "title_prefix": "Execution regression",
    "summary_prefix": "Regression view",
    "partial_summary": (
      "Execution regression falls back to persisted reference provenance because direct execution "
      "deltas are partial."
    ),
    "lane_prefix": "Regression context",
    "activity_prefix": "Execution signal",
    "reference_prefix": "Reference baseline",
  },
  "strategy_tuning": {
    "title_prefix": "Strategy tuning",
    "summary_prefix": "Tuning view",
    "partial_summary": (
      "Strategy tuning falls back to benchmark provenance because direct optimization deltas are partial."
    ),
    "lane_prefix": "Tuning context",
    "activity_prefix": "Tuning signal",
    "reference_prefix": "Benchmark backdrop",
  },
}

COMPARISON_METRIC_COPY: dict[str, dict[str, dict[str, str]]] = {
  "benchmark_validation": {
    "total_return_pct": {
      "annotation": "Validation read: return drift versus the selected benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Validation read: downside drift versus the benchmark risk envelope.",
      "positive_delta": "deeper than benchmark",
      "negative_delta": "tighter than benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark drawdown delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Validation read: hit-rate drift versus the benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark hit-rate delta unavailable",
    },
    "trade_count": {
      "annotation": "Validation read: participation and pacing drift versus the benchmark.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark activity delta unavailable",
    },
  },
  "execution_regression": {
    "total_return_pct": {
      "annotation": "Regression read: return movement is treated as execution drift.",
      "positive_delta": "return lift",
      "negative_delta": "return regression",
      "baseline": "regression baseline",
      "missing": "return regression unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Regression read: higher drawdown is treated as risk regression.",
      "positive_delta": "extra drawdown",
      "negative_delta": "risk improvement",
      "baseline": "regression baseline",
      "missing": "drawdown regression unavailable",
    },
    "win_rate_pct": {
      "annotation": "Regression read: hit-rate movement is treated as execution drift.",
      "positive_delta": "hit-rate lift",
      "negative_delta": "hit-rate regression",
      "baseline": "regression baseline",
      "missing": "hit-rate regression unavailable",
    },
    "trade_count": {
      "annotation": "Regression read: trade-flow changes point to execution behavior drift.",
      "positive_delta": "extra activity",
      "negative_delta": "reduced activity",
      "baseline": "regression baseline",
      "missing": "activity regression unavailable",
    },
  },
  "strategy_tuning": {
    "total_return_pct": {
      "annotation": "Tuning read: return deltas show optimization edge versus the baseline.",
      "positive_delta": "tuning edge",
      "negative_delta": "tuning gap",
      "baseline": "tuning baseline",
      "missing": "tuning delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Tuning read: lower drawdown marks a cleaner optimization tradeoff.",
      "positive_delta": "drawdown penalty",
      "negative_delta": "drawdown improvement",
      "baseline": "tuning baseline",
      "missing": "drawdown tuning delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Tuning read: hit-rate deltas show signal-quality tradeoffs.",
      "positive_delta": "hit-rate edge",
      "negative_delta": "hit-rate gap",
      "baseline": "tuning baseline",
      "missing": "hit-rate tuning delta unavailable",
    },
    "trade_count": {
      "annotation": "Tuning read: trade-count changes expose activity tradeoffs in the variant.",
      "positive_delta": "activity expansion",
      "negative_delta": "activity reduction",
      "baseline": "tuning baseline",
      "missing": "activity tuning delta unavailable",
    },
  },
}


class TradingApplication:
  _sandbox_worker_kind = "sandbox_native_worker"
  _guarded_live_balance_tolerance = 1e-9

  class _EphemeralGuardedLiveStateStore(GuardedLiveStatePort):
    def __init__(self) -> None:
      self._state = GuardedLiveState()

    def load_state(self) -> GuardedLiveState:
      return self._state

    def save_state(self, state: GuardedLiveState) -> GuardedLiveState:
      self._state = state
      return state

  class _UnavailableVenueStateAdapter(VenueStatePort):
    def __init__(self, clock: Callable[[], datetime]) -> None:
      self._clock = clock

    def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
      return GuardedLiveVenueStateSnapshot(
        provider="unconfigured",
        venue="unconfigured",
        verification_state="unavailable",
        captured_at=self._clock(),
        issues=("venue_state_port_unconfigured",),
      )

  def __init__(
    self,
    *,
    market_data: MarketDataPort,
    strategies: StrategyCatalogPort,
    references: ReferenceCatalogPort,
    runs: RunRepositoryPort,
    guarded_live_state: GuardedLiveStatePort | None = None,
    venue_state: VenueStatePort | None = None,
    freqtrade_reference: FreqtradeReferenceAdapter | None = None,
    mode_service: ExecutionModeService | None = None,
    data_engine: DataEngine | None = None,
    execution_engine: ExecutionEngine | None = None,
    run_supervisor: RunSupervisor | None = None,
    sandbox_worker_heartbeat_interval_seconds: int = 15,
    sandbox_worker_heartbeat_timeout_seconds: int = 45,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._clock = clock or (lambda: datetime.now(UTC))
    self._market_data = market_data
    self._strategies = strategies
    self._references = references
    self._runs = runs
    self._guarded_live_state = guarded_live_state or self._EphemeralGuardedLiveStateStore()
    self._venue_state = venue_state or self._UnavailableVenueStateAdapter(self._clock)
    self._freqtrade_reference = freqtrade_reference
    self._mode_service = mode_service or ExecutionModeService()
    self._data_engine = data_engine or DataEngine(market_data)
    self._execution_engine = execution_engine or ExecutionEngine()
    self._run_supervisor = run_supervisor or RunSupervisor()
    self._sandbox_worker_heartbeat_interval_seconds = sandbox_worker_heartbeat_interval_seconds
    self._sandbox_worker_heartbeat_timeout_seconds = sandbox_worker_heartbeat_timeout_seconds

  def list_strategies(
    self,
    *,
    lane: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    return self._strategies.list_strategies(
      runtime=lane,
      lifecycle_stage=lifecycle_stage,
      version=version,
    )

  def list_references(self) -> list[ReferenceSource]:
    return self._references.list_entries()

  def register_strategy(self, *, strategy_id: str, module_path: str, class_name: str) -> StrategyMetadata:
    registration = StrategyRegistration(
      strategy_id=strategy_id,
      module_path=module_path,
      class_name=class_name,
      registered_at=datetime.now(UTC),
    )
    return self._strategies.register(registration)

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
  ) -> list[RunRecord]:
    return self._runs.list_runs(
      mode=self._mode_service.normalize(mode),
      strategy_id=strategy_id,
      strategy_version=strategy_version,
      rerun_boundary_id=rerun_boundary_id,
    )

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get_run(run_id)

  def rerun_backtest_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.BACKTEST,
      requested_mode_label=RunMode.BACKTEST.value,
    )

  def rerun_sandbox_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.SANDBOX,
      requested_mode_label=RunMode.SANDBOX.value,
    )

  def rerun_paper_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.PAPER,
      requested_mode_label=RunMode.PAPER.value,
    )

  def compare_runs(self, *, run_ids: list[str], intent: str | None = None) -> RunComparison:
    normalized_run_ids = _normalize_run_ids(run_ids)
    if len(normalized_run_ids) < 2:
      raise ValueError("Run comparison requires at least two unique run IDs.")
    resolved_intent = _normalize_comparison_intent(intent)

    runs = self._runs.compare_runs(normalized_run_ids)
    run_by_id = {run.config.run_id: run for run in runs}
    missing_run_ids = [run_id for run_id in normalized_run_ids if run_id not in run_by_id]
    if missing_run_ids:
      raise LookupError(f"Run not found: {', '.join(missing_run_ids)}")

    ordered_runs = [run_by_id[run_id] for run_id in normalized_run_ids]
    baseline_run = ordered_runs[0]
    metric_rows = tuple(
      _build_comparison_metric_row(
        runs=ordered_runs,
        baseline_run=baseline_run,
        intent=resolved_intent,
        key=key,
        label=label,
        unit=unit,
        higher_is_better=higher_is_better,
      )
      for key, label, unit, higher_is_better in COMPARISON_METRICS
    )
    metric_row_by_key = {row.key: row for row in metric_rows}
    ranked_narratives = _rank_comparison_narratives([
      narrative
      for run in ordered_runs[1:]
      if (
        narrative := _build_comparison_narrative(
          baseline_run=baseline_run,
          run=run,
          intent=resolved_intent,
          metric_row_by_key=metric_row_by_key,
        )
      ) is not None
    ])
    return RunComparison(
      requested_run_ids=tuple(normalized_run_ids),
      intent=resolved_intent,
      baseline_run_id=baseline_run.config.run_id,
      runs=tuple(_serialize_comparison_run(run) for run in ordered_runs),
      metric_rows=metric_rows,
      narratives=tuple(ranked_narratives),
    )

  def get_market_data_status(self, timeframe: str) -> MarketDataStatus:
    return self._market_data.get_status(timeframe)

  def get_operator_visibility(self) -> OperatorVisibility:
    current_time = self._clock()
    alerts: list[OperatorAlert] = []
    audit_events: list[OperatorAuditEvent] = []
    for run in self._runs.list_runs(mode=RunMode.SANDBOX.value):
      alerts.extend(self._build_operator_alerts_for_run(run=run, current_time=current_time))
      audit_events.extend(self._build_operator_audit_events_for_run(run=run, current_time=current_time))
    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    audit_events.sort(key=lambda event: event.timestamp, reverse=True)
    return OperatorVisibility(
      generated_at=current_time,
      alerts=tuple(alerts),
      audit_events=tuple(audit_events),
    )

  def get_guarded_live_status(self) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    runtime_visibility = self.get_operator_visibility()
    running_sandbox_count = self._count_running_runs(RunMode.SANDBOX)
    running_paper_count = self._count_running_runs(RunMode.PAPER)
    running_live_count = self._count_running_runs(RunMode.LIVE)

    blockers: list[str] = []
    if state.kill_switch.state == "engaged":
      blockers.append("Kill switch is engaged for operator-controlled runtime sessions.")
    if state.reconciliation.state != "clear":
      blockers.append("Guarded-live reconciliation has not been cleared.")
    if state.recovery.state == "failed":
      blockers.append("Guarded-live runtime recovery failed after the latest restart or fault drill.")
    if runtime_visibility.alerts:
      blockers.append("Unresolved runtime alerts remain in sandbox operations.")
    blockers.append("Venue-backed live execution is not implemented.")

    audit_events = tuple(
      sorted(state.audit_events, key=lambda event: event.timestamp, reverse=True)
    )
    return GuardedLiveStatus(
      generated_at=current_time,
      candidacy_status="blocked" if blockers else "candidate",
      blockers=tuple(dict.fromkeys(blockers)),
      kill_switch=state.kill_switch,
      reconciliation=state.reconciliation,
      recovery=state.recovery,
      audit_events=audit_events,
      active_runtime_alert_count=len(runtime_visibility.alerts),
      running_sandbox_count=running_sandbox_count,
      running_paper_count=running_paper_count,
      running_live_count=running_live_count,
    )

  def engage_guarded_live_kill_switch(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    stopped_runs = self._stop_runs_for_kill_switch(actor=actor, reason=reason)
    activation_count = state.kill_switch.activation_count
    if state.kill_switch.state != "engaged":
      activation_count += 1
    kill_switch = GuardedLiveKillSwitch(
      state="engaged",
      reason=reason,
      updated_at=current_time,
      updated_by=actor,
      activation_count=activation_count,
      last_engaged_at=current_time,
      last_released_at=state.kill_switch.last_released_at,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-kill-switch-engaged:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_kill_switch_engaged",
      summary="Guarded-live kill switch engaged.",
      detail=(
        f"Reason: {reason}. Stopped {len(stopped_runs)} operator-controlled runtime "
        f"session(s): {', '.join(stopped_runs) if stopped_runs else 'none'}."
      ),
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        kill_switch=kill_switch,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def release_guarded_live_kill_switch(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    kill_switch = GuardedLiveKillSwitch(
      state="released",
      reason=reason,
      updated_at=current_time,
      updated_by=actor,
      activation_count=state.kill_switch.activation_count,
      last_engaged_at=state.kill_switch.last_engaged_at,
      last_released_at=current_time,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-kill-switch-released:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_kill_switch_released",
      summary="Guarded-live kill switch released.",
      detail=f"Reason: {reason}. Operator-controlled runtime sessions may start again.",
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        kill_switch=kill_switch,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def run_guarded_live_reconciliation(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    internal_snapshot, venue_snapshot, findings = self._build_guarded_live_reconciliation_result()
    reconciliation = GuardedLiveReconciliation(
      state="clear" if not findings else "issues_detected",
      checked_at=current_time,
      checked_by=actor,
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
    event = OperatorAuditEvent(
      event_id=f"guarded-live-reconciliation-ran:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_reconciliation_ran",
      summary="Guarded-live reconciliation recorded.",
      detail=f"Reason: {reason}. {reconciliation.summary}",
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        reconciliation=reconciliation,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def recover_guarded_live_runtime_state(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    snapshot = self._select_guarded_live_recovery_snapshot(state)
    recovered_exposures, recovery_issues = self._recover_exposures_from_venue_snapshot(snapshot)
    recovered_open_orders = snapshot.open_orders

    if snapshot.verification_state == "unavailable":
      recovery_state = GuardedLiveRuntimeRecovery(
        state="failed",
        recovered_at=current_time,
        recovered_by=actor,
        reason=reason,
        source_snapshot_at=snapshot.captured_at,
        source_verification_state=snapshot.verification_state,
        summary="Guarded-live runtime recovery failed because no usable venue snapshot was available.",
        exposures=(),
        open_orders=(),
        issues=tuple(snapshot.issues),
      )
    else:
      recovered_with_warnings = bool(recovery_issues) or snapshot.verification_state != "verified"
      recovery_state = GuardedLiveRuntimeRecovery(
        state="recovered_with_warnings" if recovered_with_warnings else "recovered",
        recovered_at=current_time,
        recovered_by=actor,
        reason=reason,
        source_snapshot_at=snapshot.captured_at,
        source_verification_state=snapshot.verification_state,
        summary=(
          "Guarded-live runtime state recovered from the latest verified venue snapshot."
          if not recovered_with_warnings
          else "Guarded-live runtime state recovered from venue data with follow-up issues to review."
        ),
        exposures=recovered_exposures,
        open_orders=recovered_open_orders,
        issues=tuple(dict.fromkeys((*snapshot.issues, *recovery_issues))),
      )

    event = OperatorAuditEvent(
      event_id=f"guarded-live-runtime-recovered:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_runtime_recovered",
      summary="Guarded-live runtime recovery recorded.",
      detail=(
        f"Reason: {reason}. {recovery_state.summary} "
        f"Recovered {len(recovery_state.exposures)} exposure(s) and {len(recovery_state.open_orders)} open order(s)."
      ),
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        recovery=recovery_state,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def run_backtest(
    self,
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
  ) -> RunRecord:
    strategy, metadata, strategy_snapshot = self._prepare_strategy(strategy_id=strategy_id, parameters=parameters)
    config = RunConfig(
      run_id=str(uuid4()),
      mode=RunMode.BACKTEST,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue="binance",
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=parameters,
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
        provenance=RunProvenance(lane="reference", strategy=strategy_snapshot),
      )
      if self._freqtrade_reference is None:
        run.status = RunStatus.FAILED
        run.notes.append("Freqtrade reference adapter is not configured.")
      else:
        run = self._freqtrade_reference.execute_backtest(run, metadata)
      self._attach_rerun_boundary(run)
      return self._runs.save_run(run)
    run = self._simulate_run(
      config=config,
      strategy=strategy,
      strategy_snapshot=strategy_snapshot,
      active_bars=None,
    )
    if run.status != RunStatus.FAILED:
      self._run_supervisor.complete(run)
    return self._runs.save_run(run)

  def start_sandbox_run(
    self,
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
  ) -> RunRecord:
    return self._start_sandbox_session(
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
    )

  def start_paper_run(
    self,
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
  ) -> RunRecord:
    return self._start_paper_session(
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
    )

  def _start_sandbox_session(
    self,
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
  ) -> RunRecord:
    return self._start_native_session(
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
    )

  def _start_paper_session(
    self,
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
  ) -> RunRecord:
    return self._start_native_session(
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
    )

  def _start_native_session(
    self,
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
  ) -> RunRecord:
    strategy, metadata, strategy_snapshot = self._prepare_strategy(strategy_id=strategy_id, parameters=parameters)
    config = RunConfig(
      run_id=str(uuid4()),
      mode=target_mode,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue="binance",
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=parameters,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      start_at=start_at,
      end_at=end_at,
    )
    self._ensure_operator_control_runtime_allowed(target_mode)
    if metadata.runtime == "freqtrade_reference":
      run = RunRecord(
        config=config,
        status=RunStatus.FAILED,
        provenance=RunProvenance(lane="reference", strategy=strategy_snapshot),
      )
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        + reference_failure_copy
      )
      return self._runs.save_run(run)

    loaded = self._data_engine.load_frame(config=config, active_bars=replay_bars)
    run = self._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
    run.provenance.market_data = loaded.lineage
    run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
    self._attach_rerun_boundary(run)
    data = loaded.frame
    if data.empty:
      run.notes.append("No candles available for the requested range.")
      run.status = RunStatus.FAILED
      return self._runs.save_run(run)

    enriched = strategy.build_feature_frame(data, config.parameters)
    required_bars = max(strategy.warmup_spec().required_bars, 2)
    if len(enriched) < required_bars:
      run.status = RunStatus.FAILED
      run.notes.append(
        f"{insufficient_candles_copy} {required_bars} candles to prime the current strategy state."
      )
      return self._runs.save_run(run)

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
    self._execution_engine.apply_decision(
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
    self._run_supervisor.start_mode(
      run=run,
      mode=target_mode,
      mode_service=self._mode_service,
      replay_bars=replay_bars if target_mode == RunMode.SANDBOX else None,
    )
    if attach_runtime_session:
      primed_timestamp = latest_row["timestamp"].to_pydatetime()
      primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
      self._run_supervisor.start_worker_session(
        run=run,
        worker_kind=self._sandbox_worker_kind,
        heartbeat_interval_seconds=self._sandbox_worker_heartbeat_interval_seconds,
        heartbeat_timeout_seconds=self._sandbox_worker_heartbeat_timeout_seconds,
        now=self._clock(),
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
    return self._runs.save_run(run)

  def stop_sandbox_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    self._run_supervisor.stop(run, reason="Sandbox run stopped by operator.")
    return self._runs.save_run(run)

  def stop_paper_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    self._run_supervisor.stop(run, reason="Paper run stopped by operator.")
    return self._runs.save_run(run)

  def _ensure_operator_control_runtime_allowed(self, mode: RunMode) -> None:
    if mode not in {RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE}:
      return
    state = self._guarded_live_state.load_state()
    if state.kill_switch.state == "engaged":
      raise ValueError(
        "Guarded-live kill switch is engaged. Release it before starting operator-controlled runtime sessions."
      )

  def _persist_guarded_live_state(self, state: GuardedLiveState) -> GuardedLiveState:
    return self._guarded_live_state.save_state(state)

  def _select_guarded_live_recovery_snapshot(
    self,
    state: GuardedLiveState,
  ) -> GuardedLiveVenueStateSnapshot:
    snapshot = state.reconciliation.venue_snapshot
    if snapshot is not None and snapshot.verification_state != "unavailable":
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
            instrument_id=f"{snapshot.venue}:{balance.asset}",
            symbol=balance.asset,
            asset=balance.asset,
            quantity=balance.total,
          )
        )
        continue
      recovered.append(
        GuardedLiveRecoveredExposure(
          instrument_id=instrument.instrument_id,
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

  def _build_guarded_live_reconciliation_result(
    self,
  ) -> tuple[
    GuardedLiveInternalStateSnapshot,
    GuardedLiveVenueStateSnapshot,
    list[GuardedLiveReconciliationFinding],
  ]:
    findings: list[GuardedLiveReconciliationFinding] = []
    internal_snapshot = self._build_guarded_live_internal_snapshot()
    venue_snapshot = self._venue_state.capture_snapshot()

    runtime_visibility = self.get_operator_visibility()
    if runtime_visibility.alerts:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="runtime_alerts_present",
          severity="warning",
          summary=f"{len(runtime_visibility.alerts)} unresolved runtime alert(s) remain active.",
          detail="Guarded-live candidacy stays blocked while sandbox runtime alerts remain unresolved.",
        )
      )

    running_live_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if run.status == RunStatus.RUNNING
    ]
    if running_live_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="unexpected_live_runs",
          severity="critical",
          summary=f"{len(running_live_runs)} live run(s) are active before guarded-live support exists.",
          detail="Live execution is not implemented, so any active live run indicates a control-plane mismatch.",
        )
      )

    inconsistent_sandbox_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_sandbox_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="sandbox_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_sandbox_runs)} sandbox run(s) are missing persisted runtime session state."
          ),
          detail="Continuous sandbox workers must keep runtime-session state for restart safety and auditability.",
        )
      )

    stale_terminal_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_sessions)} terminal sandbox run(s) still report an active runtime session."
          ),
          detail="Terminal runs should not keep active worker-session state after stop, failure, or completion.",
        )
      )

    if venue_snapshot.verification_state != "verified":
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_snapshot_unavailable",
          severity="critical" if venue_snapshot.verification_state == "unavailable" else "warning",
          summary=(
            "Venue-state verification is unavailable."
            if venue_snapshot.verification_state == "unavailable"
            else "Venue-state verification completed with partial data."
          ),
          detail=(
            ", ".join(venue_snapshot.issues)
            if venue_snapshot.issues
            else "The venue adapter did not return a fully verified account snapshot."
          ),
        )
      )

    findings.extend(
      self._build_guarded_live_venue_mismatch_findings(
        internal_snapshot=internal_snapshot,
        venue_snapshot=venue_snapshot,
      )
    )
    return internal_snapshot, venue_snapshot, findings

  def _build_guarded_live_internal_snapshot(self) -> GuardedLiveInternalStateSnapshot:
    captured_at = self._clock()
    exposures: list[GuardedLiveInternalExposure] = []
    open_order_count = 0
    running_run_ids: list[str] = []

    for mode in (RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE):
      for run in self._runs.list_runs(mode=mode.value):
        if run.status == RunStatus.RUNNING:
          running_run_ids.append(run.config.run_id)
        open_order_count += sum(1 for order in run.orders if order.status.value == "open")
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
    if run.equity_curve:
      return run.equity_curve[-1].timestamp
    market_data = run.provenance.market_data
    return market_data.effective_end_at if market_data is not None else None

  def _infer_sandbox_primed_candle_count(self, run: RunRecord) -> int:
    session = run.provenance.runtime_session
    if session is not None and session.primed_candle_count > 0:
      return session.primed_candle_count
    market_data = run.provenance.market_data
    if market_data is None:
      return 0
    return market_data.candle_count

  def _build_operator_alerts_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    session = run.provenance.runtime_session
    if session is None:
      return []

    alerts: list[OperatorAlert] = []
    symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
    failed_event = self._latest_runtime_note_event(run=run, kind="sandbox_worker_failed")
    if failed_event is not None or session.lifecycle_state == "failed" or run.status == RunStatus.FAILED:
      detected_at = (
        failed_event["timestamp"]
        or run.ended_at
        or session.last_heartbeat_at
        or run.started_at
      )
      detail = failed_event["detail"] if failed_event is not None else (
        run.notes[-1] if run.notes else "Sandbox worker entered a failed runtime state."
      )
      alerts.append(
        OperatorAlert(
          alert_id=f"runtime-failed:{run.config.run_id}:{detected_at.isoformat()}",
          severity="critical",
          category="worker_failure",
          summary=f"Sandbox worker failed for {symbol}.",
          detail=detail,
          detected_at=detected_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
        )
      )

    heartbeat_at = session.last_heartbeat_at or session.started_at
    heartbeat_age_seconds = (current_time - heartbeat_at).total_seconds()
    if (
      run.status == RunStatus.RUNNING
      and session.lifecycle_state == "active"
      and heartbeat_age_seconds > session.heartbeat_timeout_seconds
    ):
      alerts.append(
        OperatorAlert(
          alert_id=f"runtime-stale:{run.config.run_id}:{current_time.isoformat()}",
          severity="warning",
          category="stale_runtime",
          summary=f"Sandbox worker heartbeat is stale for {symbol}.",
          detail=(
            f"Last heartbeat at {heartbeat_at.isoformat()} exceeded the "
            f"{session.heartbeat_timeout_seconds}s timeout while the run remains active."
          ),
          detected_at=current_time,
          run_id=run.config.run_id,
          session_id=session.session_id,
        )
      )
    return alerts

  def _build_operator_audit_events_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAuditEvent]:
    session = run.provenance.runtime_session
    if session is None:
      return []

    events: list[OperatorAuditEvent] = [
      OperatorAuditEvent(
        event_id=f"runtime-started:{run.config.run_id}:{session.started_at.isoformat()}",
        timestamp=session.started_at,
        actor="system",
        kind="sandbox_worker_started",
        summary=f"Sandbox worker started for {run.config.symbols[0]}.",
        detail=(
          f"Session {session.session_id} started with {session.primed_candle_count} primed candles "
          f"and {session.processed_tick_count} processed ticks."
        ),
        run_id=run.config.run_id,
        session_id=session.session_id,
      )
    ]

    for note in run.notes:
      if note == "Sandbox run stopped by operator.":
        timestamp = run.ended_at or current_time
        events.append(
          OperatorAuditEvent(
            event_id=f"audit:sandbox_worker_stopped:{run.config.run_id}:{timestamp.isoformat()}",
            timestamp=timestamp,
            actor="operator",
            kind="sandbox_worker_stopped",
            summary=self._build_runtime_audit_summary(run=run, kind="sandbox_worker_stopped"),
            detail=note,
            run_id=run.config.run_id,
            session_id=session.session_id,
          )
        )
        continue
      if parsed := self._parse_runtime_note_event(note):
        events.append(
          OperatorAuditEvent(
            event_id=f"audit:{parsed['kind']}:{run.config.run_id}:{parsed['timestamp'].isoformat()}",
            timestamp=parsed["timestamp"],
            actor="system",
            kind=parsed["kind"],
            summary=self._build_runtime_audit_summary(run=run, kind=parsed["kind"]),
            detail=parsed["detail"],
            run_id=run.config.run_id,
            session_id=session.session_id,
          )
        )

    heartbeat_at = session.last_heartbeat_at or session.started_at
    if (
      run.status == RunStatus.RUNNING
      and session.lifecycle_state == "active"
      and (current_time - heartbeat_at).total_seconds() > session.heartbeat_timeout_seconds
    ):
      events.append(
        OperatorAuditEvent(
          event_id=f"audit:sandbox_worker_stale:{run.config.run_id}:{current_time.isoformat()}",
          timestamp=current_time,
          actor="system",
          kind="sandbox_worker_stale",
          summary=f"Sandbox worker stale state detected for {run.config.symbols[0]}.",
          detail=(
            f"Heartbeat timeout exceeded after {session.heartbeat_timeout_seconds}s without an update."
          ),
          run_id=run.config.run_id,
          session_id=session.session_id,
        )
      )
    return events

  def _latest_runtime_note_event(
    self,
    *,
    run: RunRecord,
    kind: str,
  ) -> dict[str, datetime | str] | None:
    for note in reversed(run.notes):
      parsed = self._parse_runtime_note_event(note)
      if parsed is not None and parsed["kind"] == kind:
        return parsed
    return None

  def _parse_runtime_note_event(self, note: str) -> dict[str, datetime | str] | None:
    parts = note.split(" | ", 2)
    if len(parts) == 3:
      timestamp_raw, kind, detail = parts
      if kind.startswith("sandbox_worker_"):
        return {
          "timestamp": datetime.fromisoformat(timestamp_raw),
          "kind": kind,
          "detail": detail,
        }
    return None

  @staticmethod
  def _build_runtime_audit_summary(*, run: RunRecord, kind: str) -> str:
    symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
    summary_by_kind = {
      "sandbox_worker_recovered": f"Sandbox worker recovered for {symbol}.",
      "sandbox_worker_failed": f"Sandbox worker failed for {symbol}.",
      "sandbox_worker_stopped": f"Sandbox worker stopped by operator for {symbol}.",
    }
    return summary_by_kind.get(kind, f"Sandbox worker runtime event for {symbol}.")

  def _simulate_run(
    self,
    *,
    config: RunConfig,
    active_bars: int | None,
    strategy: StrategyRuntime | None = None,
    strategy_snapshot: StrategySnapshot | None = None,
  ) -> RunRecord:
    if strategy is None:
      strategy, _, strategy_snapshot = self._prepare_strategy(
        strategy_id=config.strategy_id,
        parameters=config.parameters,
      )
    loaded = self._data_engine.load_frame(config=config, active_bars=active_bars)
    run = self._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
    run.provenance.market_data = loaded.lineage
    run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
    self._attach_rerun_boundary(run)
    data = loaded.frame
    if data.empty:
      run.notes.append("No candles available for the requested range.")
      run.status = RunStatus.FAILED
      return run

    enriched = strategy.build_feature_frame(data, config.parameters)
    warmup = strategy.warmup_spec().required_bars
    cache = StateCache(
      instrument_id=f"{config.venue}:{config.symbols[0]}",
      cash=config.initial_cash,
    )

    for index in range(max(warmup, 2), len(enriched)):
      history = enriched.iloc[: index + 1]
      latest_row = history.iloc[-1]
      state = cache.snapshot(
        timestamp=latest_row["timestamp"].to_pydatetime(),
        parameters=config.parameters,
      )
      decision = strategy.evaluate(history, config.parameters, state)
      latest_row = history.iloc[-1]
      self._execution_engine.apply_decision(
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
    return run

  def _prepare_strategy(
    self,
    *,
    strategy_id: str,
    parameters: dict,
  ) -> tuple[StrategyRuntime, StrategyMetadata, StrategySnapshot]:
    strategy = self._strategies.load(strategy_id)
    metadata = strategy.describe()
    registration = self._strategies.get_registration(metadata.strategy_id)
    return strategy, metadata, self._build_strategy_snapshot(
      strategy=strategy,
      metadata=metadata,
      parameters=parameters,
      registration=registration,
    )

  def _build_strategy_snapshot(
    self,
    *,
    strategy: StrategyRuntime,
    metadata: StrategyMetadata,
    parameters: dict,
    registration: StrategyRegistration | None,
  ) -> StrategySnapshot:
    schema = deepcopy(metadata.parameter_schema)
    requested = deepcopy(parameters)
    resolved = self._resolve_parameters(schema=schema, requested=requested)
    lifecycle = metadata.lifecycle
    if registration is not None and lifecycle.registered_at is None:
      lifecycle = StrategyLifecycle(
        stage=lifecycle.stage,
        registered_at=registration.registered_at,
      )
    return StrategySnapshot(
      strategy_id=metadata.strategy_id,
      name=metadata.name,
      version=metadata.version,
      runtime=metadata.runtime,
      lifecycle=lifecycle,
      version_lineage=metadata.version_lineage or (metadata.version,),
      parameter_snapshot=StrategyParameterSnapshot(
        requested=requested,
        resolved=resolved,
        schema=schema,
      ),
      supported_timeframes=metadata.supported_timeframes,
      warmup=strategy.warmup_spec(),
      reference_id=metadata.reference_id,
      reference_path=metadata.reference_path,
      entrypoint=metadata.entrypoint,
    )

  @staticmethod
  def _resolve_parameters(*, schema: dict, requested: dict) -> dict:
    resolved: dict = {}
    for name, definition in schema.items():
      if isinstance(definition, dict) and "default" in definition:
        resolved[name] = deepcopy(definition["default"])
    for name, value in requested.items():
      resolved[name] = deepcopy(value)
    return resolved

  def _attach_rerun_boundary(self, run: RunRecord) -> None:
    market_data = run.provenance.market_data
    if market_data is None:
      run.provenance.rerun_boundary_id = None
      run.provenance.rerun_boundary_state = "range_only"
      return

    strategy = run.provenance.strategy
    symbol_checkpoint_ids = {
      symbol: lineage.sync_checkpoint_id
      for symbol, lineage in sorted(run.provenance.market_data_by_symbol.items())
      if lineage.sync_checkpoint_id is not None
    }
    resolved_parameters = (
      deepcopy(strategy.parameter_snapshot.resolved)
      if strategy is not None
      else deepcopy(run.config.parameters)
    )
    run.provenance.rerun_boundary_id = build_rerun_boundary_identity(
      lane=run.provenance.lane,
      mode=run.config.mode.value,
      strategy_id=run.config.strategy_id,
      strategy_version=run.config.strategy_version,
      resolved_parameters=resolved_parameters,
      venue=run.config.venue,
      symbols=run.config.symbols,
      timeframe=run.config.timeframe,
      initial_cash=run.config.initial_cash,
      fee_rate=run.config.fee_rate,
      slippage_bps=run.config.slippage_bps,
      market_data_reproducibility_state=market_data.reproducibility_state,
      market_data_dataset_identity=market_data.dataset_identity,
      market_data_sync_checkpoint_id=market_data.sync_checkpoint_id,
      market_data_symbol_checkpoint_ids=symbol_checkpoint_ids,
      requested_start_at=market_data.requested_start_at,
      requested_end_at=market_data.requested_end_at,
      effective_start_at=market_data.effective_start_at,
      effective_end_at=market_data.effective_end_at,
      candle_count=market_data.candle_count,
      reference_id=run.provenance.reference_id,
      reference_version=run.provenance.reference_version,
      integration_mode=run.provenance.integration_mode,
      external_command=run.provenance.external_command,
    )
    run.provenance.rerun_boundary_state = market_data.reproducibility_state

  def _resolve_rerun_source(self, *, rerun_boundary_id: str) -> RunRecord:
    candidates = self._runs.list_runs(rerun_boundary_id=rerun_boundary_id)
    if not candidates:
      raise LookupError(f"Rerun boundary not found: {rerun_boundary_id}")
    completed = [run for run in candidates if run.status == RunStatus.COMPLETED]
    return completed[0] if completed else candidates[0]

  def _rerun_from_boundary(
    self,
    *,
    rerun_boundary_id: str,
    target_mode: RunMode,
    requested_mode_label: str,
  ) -> RunRecord:
    source_run = self._resolve_rerun_source(rerun_boundary_id=rerun_boundary_id)
    if len(source_run.config.symbols) != 1:
      raise ValueError(f"Explicit rerun currently supports only single-symbol {requested_mode_label} runs.")

    rerun_start_at = self._resolve_rerun_start_at(source_run)
    rerun_end_at = self._resolve_rerun_end_at(source_run)
    rerun_parameters = self._resolve_rerun_parameters(source_run)
    symbol = source_run.config.symbols[0]
    session_window_note: str | None = None

    if target_mode == RunMode.BACKTEST:
      rerun = self.run_backtest(
        strategy_id=source_run.config.strategy_id,
        symbol=symbol,
        timeframe=source_run.config.timeframe,
        initial_cash=source_run.config.initial_cash,
        fee_rate=source_run.config.fee_rate,
        slippage_bps=source_run.config.slippage_bps,
        parameters=rerun_parameters,
        start_at=rerun_start_at,
        end_at=rerun_end_at,
      )
    elif target_mode in {RunMode.SANDBOX, RunMode.PAPER}:
      preview_start_at, preview_end_at, preview_replay_bars = self._resolve_preview_rerun_window(source_run)
      if target_mode == RunMode.SANDBOX:
        if preview_replay_bars is None:
          session_window_note = (
            "Sandbox rerun restored the worker session from the stored effective market-data window."
          )
        else:
          session_window_note = (
            "Sandbox rerun restored the stored worker-session priming window."
          )
        rerun = self._start_sandbox_session(
          strategy_id=source_run.config.strategy_id,
          symbol=symbol,
          timeframe=source_run.config.timeframe,
          initial_cash=source_run.config.initial_cash,
          fee_rate=source_run.config.fee_rate,
          slippage_bps=source_run.config.slippage_bps,
          parameters=rerun_parameters,
          replay_bars=preview_replay_bars,
          start_at=preview_start_at,
          end_at=preview_end_at,
        )
      else:
        if preview_replay_bars is None:
          session_window_note = "Paper rerun seeded the current paper session from the stored effective market-data window."
        else:
          session_window_note = "Paper rerun seeded the current paper session from the stored priming window."
        rerun = self._start_paper_session(
          strategy_id=source_run.config.strategy_id,
          symbol=symbol,
          timeframe=source_run.config.timeframe,
          initial_cash=source_run.config.initial_cash,
          fee_rate=source_run.config.fee_rate,
          slippage_bps=source_run.config.slippage_bps,
          parameters=rerun_parameters,
          replay_bars=preview_replay_bars,
          start_at=preview_start_at,
          end_at=preview_end_at,
        )
    else:
      raise ValueError(f"Unsupported rerun target mode: {target_mode.value}")

    return self._persist_explicit_rerun(
      rerun=rerun,
      source_run=source_run,
      rerun_boundary_id=rerun_boundary_id,
      requested_mode_label=requested_mode_label,
      preview_window_note=session_window_note,
    )

  def _persist_explicit_rerun(
    self,
    *,
    rerun: RunRecord,
    source_run: RunRecord,
    rerun_boundary_id: str,
    requested_mode_label: str,
    preview_window_note: str | None = None,
  ) -> RunRecord:
    rerun.provenance.rerun_source_run_id = source_run.config.run_id
    rerun.provenance.rerun_target_boundary_id = rerun_boundary_id
    rerun.provenance.rerun_match_status = (
      "matched"
      if rerun.provenance.rerun_boundary_id == rerun_boundary_id
      else "drifted"
    )
    rerun.notes.insert(
      0,
      f"Explicit {requested_mode_label} rerun from boundary {rerun_boundary_id} using source run {source_run.config.run_id}.",
    )
    if rerun.config.mode in {RunMode.SANDBOX, RunMode.PAPER} and preview_window_note is not None:
      rerun.notes.insert(
        1,
        preview_window_note,
      )
    if rerun.provenance.rerun_match_status == "matched":
      rerun.notes.append("Explicit rerun matched the stored rerun boundary.")
    else:
      rerun.notes.append(
        "Explicit rerun drifted from the stored rerun boundary. "
        f"Expected {rerun_boundary_id}, got {rerun.provenance.rerun_boundary_id or 'unavailable'}."
      )
      if source_run.config.mode != rerun.config.mode:
        rerun.notes.append(
          "Mode-specific rerun boundary drift is expected when replaying a stored boundary into a different execution mode."
        )
    return self._runs.save_run(rerun)

  def _resolve_rerun_parameters(self, run: RunRecord) -> dict:
    strategy = run.provenance.strategy
    if strategy is not None:
      return deepcopy(strategy.parameter_snapshot.resolved)
    return deepcopy(run.config.parameters)

  @staticmethod
  def _resolve_rerun_start_at(run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    if market_data is None:
      return run.config.start_at
    return (
      market_data.effective_start_at
      or market_data.requested_start_at
      or run.config.start_at
    )

  @staticmethod
  def _resolve_rerun_end_at(run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    if market_data is None:
      return run.config.end_at
    return (
      market_data.effective_end_at
      or market_data.requested_end_at
      or run.config.end_at
    )

  @staticmethod
  def _resolve_preview_rerun_window(run: RunRecord) -> tuple[datetime | None, datetime | None, int | None]:
    market_data = run.provenance.market_data
    if (
      run.config.mode in {RunMode.SANDBOX, RunMode.PAPER}
      and run.config.start_at is None
      and run.config.end_at is None
      and market_data is not None
      and market_data.candle_count > 0
    ):
      return None, None, market_data.candle_count
    return (
      TradingApplication._resolve_rerun_start_at(run),
      TradingApplication._resolve_rerun_end_at(run),
      None,
    )


def serialize_run(run: RunRecord) -> dict:
  payload = asdict(run)
  payload["config"]["mode"] = run.config.mode.value
  payload["status"] = run.status.value
  payload["provenance"]["external_command"] = list(run.provenance.external_command)
  payload["provenance"]["artifact_paths"] = list(run.provenance.artifact_paths)
  payload["provenance"]["benchmark_artifacts"] = [
    asdict(artifact)
    for artifact in run.provenance.benchmark_artifacts
  ]
  strategy_snapshot = payload["provenance"].get("strategy")
  if strategy_snapshot is not None:
    strategy_snapshot["version_lineage"] = list(
      run.provenance.strategy.version_lineage or (run.provenance.strategy.version,)
    )
    strategy_snapshot["supported_timeframes"] = list(run.provenance.strategy.supported_timeframes)
    strategy_snapshot["warmup"]["timeframes"] = list(run.provenance.strategy.warmup.timeframes)
  return payload


def serialize_strategy(strategy: StrategyMetadata) -> dict:
  payload = asdict(strategy)
  payload["asset_types"] = [asset_type.value for asset_type in strategy.asset_types]
  payload["supported_timeframes"] = list(strategy.supported_timeframes)
  payload["version_lineage"] = list(strategy.version_lineage or (strategy.version,))
  return payload


def serialize_run_comparison(comparison: RunComparison) -> dict:
  payload = asdict(comparison)
  payload["requested_run_ids"] = list(comparison.requested_run_ids)
  payload["runs"] = [
    {
      **run_payload,
      "symbols": list(run.symbols),
      "external_command": list(run.external_command),
      "artifact_paths": list(run.artifact_paths),
      "benchmark_artifacts": [asdict(artifact) for artifact in run.benchmark_artifacts],
      "notes": list(run.notes),
    }
    for run_payload, run in zip(payload["runs"], comparison.runs, strict=True)
  ]
  return payload


def _normalize_run_ids(run_ids: list[str]) -> list[str]:
  normalized_run_ids: list[str] = []
  seen_run_ids: set[str] = set()
  for run_id in run_ids:
    if run_id in seen_run_ids:
      continue
    seen_run_ids.add(run_id)
    normalized_run_ids.append(run_id)
  return normalized_run_ids


def _serialize_comparison_run(run: RunRecord) -> RunComparisonRun:
  return RunComparisonRun(
    run_id=run.config.run_id,
    mode=run.config.mode.value,
    status=run.status.value,
    lane=run.provenance.lane,
    strategy_id=run.config.strategy_id,
    strategy_name=run.provenance.strategy.name if run.provenance.strategy is not None else None,
    strategy_version=run.config.strategy_version,
    symbols=run.config.symbols,
    timeframe=run.config.timeframe,
    started_at=run.started_at,
    ended_at=run.ended_at,
    reference_id=run.provenance.reference_id,
    reference_version=run.provenance.reference_version,
    integration_mode=run.provenance.integration_mode,
    reference=deepcopy(run.provenance.reference),
    working_directory=run.provenance.working_directory,
    rerun_boundary_id=run.provenance.rerun_boundary_id,
    rerun_boundary_state=run.provenance.rerun_boundary_state,
    external_command=tuple(run.provenance.external_command),
    artifact_paths=tuple(run.provenance.artifact_paths),
    benchmark_artifacts=tuple(run.provenance.benchmark_artifacts),
    metrics=deepcopy(run.metrics),
    notes=tuple(run.notes),
  )


def _build_comparison_metric_row(
  *,
  runs: list[RunRecord],
  baseline_run: RunRecord,
  intent: str,
  key: str,
  label: str,
  unit: str,
  higher_is_better: bool,
) -> RunComparisonMetricRow:
  baseline_value = _resolve_run_metric_value(baseline_run, key)
  values = {
    run.config.run_id: _resolve_run_metric_value(run, key)
    for run in runs
  }
  deltas_vs_baseline = {
    run_id: _calculate_metric_delta(value, baseline_value)
    for run_id, value in values.items()
  }
  delta_annotations = {
    run_id: _build_metric_delta_annotation(
      intent=intent,
      key=key,
      unit=unit,
      is_baseline=run_id == baseline_run.config.run_id,
      higher_is_better=higher_is_better,
      delta=deltas_vs_baseline[run_id],
      value=values[run_id],
    )
    for run_id in values
  }
  comparable_values = {
    run_id: value
    for run_id, value in values.items()
    if value is not None
  }
  best_run_id: str | None = None
  if comparable_values:
    best_run_id = (
      max(comparable_values, key=comparable_values.get)
      if higher_is_better
      else min(comparable_values, key=comparable_values.get)
    )
  return RunComparisonMetricRow(
    key=key,
    label=label,
    unit=unit,
    higher_is_better=higher_is_better,
    values=values,
    deltas_vs_baseline=deltas_vs_baseline,
    delta_annotations=delta_annotations,
    annotation=_build_metric_annotation(intent=intent, key=key),
    best_run_id=best_run_id,
  )


def _build_metric_annotation(*, intent: str, key: str) -> str | None:
  return COMPARISON_METRIC_COPY.get(intent, {}).get(key, {}).get("annotation")


def _build_metric_delta_annotation(
  *,
  intent: str,
  key: str,
  unit: str,
  is_baseline: bool,
  higher_is_better: bool,
  delta: float | int | None,
  value: float | int | None,
) -> str:
  copy = COMPARISON_METRIC_COPY.get(intent, {}).get(key, {})
  if is_baseline:
    return copy.get("baseline", "baseline")
  if value is None or delta is None:
    return copy.get("missing", "delta unavailable")
  if delta == 0:
    return "aligned with baseline"

  magnitude = _format_metric_delta_magnitude(delta=delta, unit=unit)
  positive_phrase = copy.get("positive_delta", "above baseline")
  negative_phrase = copy.get("negative_delta", "below baseline")

  if higher_is_better:
    phrase = positive_phrase if delta > 0 else negative_phrase
  else:
    phrase = positive_phrase if delta > 0 else negative_phrase
  return f"{magnitude} {phrase}"


def _format_metric_delta_magnitude(
  *,
  delta: float | int,
  unit: str,
) -> str:
  magnitude = abs(float(delta))
  if unit == "pct":
    rounded = round(magnitude, 2)
    return f"{rounded:g} pts"
  rounded = round(magnitude, 2)
  if rounded.is_integer():
    return str(int(rounded))
  return f"{rounded:g}"


def _build_comparison_narrative(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  intent: str,
  metric_row_by_key: dict[str, RunComparisonMetricRow],
) -> RunComparisonNarrative | None:
  comparison_type = _classify_comparison_type(baseline_run, run)
  target_label = _comparison_run_label(run)
  baseline_label = _comparison_run_label(baseline_run)
  target_subject = _comparison_subject_label(run)

  total_return_delta = _metric_row_delta(metric_row_by_key, "total_return_pct", run.config.run_id)
  max_drawdown_delta = _metric_row_delta(metric_row_by_key, "max_drawdown_pct", run.config.run_id)
  win_rate_delta = _metric_row_delta(metric_row_by_key, "win_rate_pct", run.config.run_id)
  trade_count_delta = _metric_row_delta(metric_row_by_key, "trade_count", run.config.run_id)

  title = _build_comparison_narrative_title(
    intent=intent,
    comparison_type=comparison_type,
    target_subject=target_subject,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
  )
  summary = _build_comparison_narrative_summary(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )
  bullets = _build_comparison_narrative_bullets(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    target_label=target_label,
    baseline_label=baseline_label,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  if not title and not summary and not bullets:
    return None

  insight_score = _score_comparison_narrative(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  return RunComparisonNarrative(
    run_id=run.config.run_id,
    baseline_run_id=baseline_run.config.run_id,
    comparison_type=comparison_type,
    title=title or f"{target_subject} diverged from {baseline_label}.",
    summary=summary or f"{target_label} is being compared against {baseline_label}.",
    bullets=tuple(bullets),
    insight_score=insight_score,
  )


def _rank_comparison_narratives(
  narratives: list[RunComparisonNarrative],
) -> list[RunComparisonNarrative]:
  ordered = sorted(
    narratives,
    key=lambda narrative: (-narrative.insight_score, narrative.run_id),
  )
  return [
    replace(
      narrative,
      rank=index + 1,
      is_primary=index == 0,
    )
    for index, narrative in enumerate(ordered)
  ]


def _score_comparison_narrative(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> float:
  weights = COMPARISON_INTENT_WEIGHTS[intent]
  score = 0.0
  score += abs(float(total_return_delta or 0.0)) * weights["return"]
  score += abs(float(max_drawdown_delta or 0.0)) * weights["drawdown"]
  score += abs(float(win_rate_delta or 0.0)) * weights["win_rate"]
  score += min(abs(float(trade_count_delta or 0.0)), 50.0) * weights["trade_count"]

  if comparison_type == "native_vs_reference":
    score += weights["native_reference_bonus"]
  elif comparison_type == "reference_vs_reference":
    score += weights["reference_bonus"]

  if run.status != baseline_run.status:
    score += weights["status_bonus"]
  if _extract_benchmark_story(run) or _extract_benchmark_story(baseline_run):
    score += weights["benchmark_story_bonus"]
  if score == 0.0 and _has_reference_context(run, baseline_run):
    score = weights["reference_floor"]
  return round(score, 2)


def _normalize_comparison_intent(intent: str | None) -> str:
  if intent in (None, ""):
    return COMPARISON_INTENT_DEFAULT
  if intent not in COMPARISON_INTENT_WEIGHTS:
    supported = ", ".join(sorted(COMPARISON_INTENT_WEIGHTS))
    raise ValueError(f"Unsupported comparison intent: {intent}. Expected one of: {supported}.")
  return intent


def _build_comparison_narrative_title(
  *,
  intent: str,
  comparison_type: str,
  target_subject: str,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  versus_baseline = "the baseline" if comparison_type != "native_vs_reference" else f"the native/reference baseline {baseline_label}"
  if total_return_delta is not None and max_drawdown_delta is not None:
    if intent == "benchmark_validation":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} favors {target_subject}: higher return without extra drawdown versus {versus_baseline}."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} running hotter than {versus_baseline}: more return, but deeper drawdown."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} staying safer than {versus_baseline}, but giving up return."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as off-benchmark versus {versus_baseline}."
      return f"{copy['title_prefix']} shows {target_subject} holding close to {versus_baseline}."
    if intent == "execution_regression":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} sees {target_subject} diverging from {versus_baseline}, but not as a degradation."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} changing risk behavior versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} throttling risk versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as a clear degradation versus {versus_baseline}."
      return f"{copy['title_prefix']} sees only limited drift in {target_subject} versus {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} clearly prefers {target_subject} over {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} treats {target_subject} as the higher-upside variant versus {versus_baseline}, with a drawdown tradeoff."
    if total_return_delta < 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} treats {target_subject} as the more defensive variant versus {versus_baseline}."
    if total_return_delta < 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} finds little upside in {target_subject} versus {versus_baseline}."
    return f"{copy['title_prefix']} keeps {target_subject} near-neutral against {versus_baseline}."
  if total_return_delta is not None:
    if intent == "strategy_tuning":
      if total_return_delta > 0:
        return f"{copy['title_prefix']} prefers {target_subject} for return potential versus {versus_baseline}."
      if total_return_delta < 0:
        return f"{copy['title_prefix']} sees {target_subject} as lower-upside than {versus_baseline}."
      return f"{copy['title_prefix']} sees no return edge between {target_subject} and {versus_baseline}."
    if total_return_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} ahead of {versus_baseline} on total return."
    if total_return_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} trailing {versus_baseline} on total return."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on total return."
  if max_drawdown_delta is not None:
    if max_drawdown_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} containing drawdown better than {versus_baseline}."
    if max_drawdown_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} running with deeper drawdown than {versus_baseline}."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on drawdown."
  if comparison_type == "native_vs_reference":
    return f"{copy['title_prefix']} frames {target_subject} as the comparison counterpart to {baseline_label}."
  return f"{copy['title_prefix']} reads {target_subject} against {baseline_label}."


def _build_comparison_narrative_summary(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  metric_shifts: list[str] = []
  if total_return_delta is not None:
    metric_shifts.append(f"return {_format_metric_delta(total_return_delta, 'pct_points')}")
  if max_drawdown_delta is not None:
    metric_shifts.append(f"drawdown {_format_metric_delta(max_drawdown_delta, 'pct_points')}")
  if win_rate_delta is not None:
    metric_shifts.append(f"win rate {_format_metric_delta(win_rate_delta, 'pct_points')}")
  if trade_count_delta is not None:
    metric_shifts.append(f"trades {_format_metric_delta(trade_count_delta, 'count')}")
  if metric_shifts:
    if intent == "benchmark_validation":
      return f"{copy['summary_prefix']} treats these shifts as benchmark drift against {baseline_label}: {', '.join(metric_shifts)}."
    if intent == "execution_regression":
      return f"{copy['summary_prefix']} interprets these changes as execution drift against {baseline_label}: {', '.join(metric_shifts)}."
    return f"{copy['summary_prefix']} reads these changes as optimization tradeoffs against {baseline_label}: {', '.join(metric_shifts)}."

  if comparison_type == "native_vs_reference" and _has_reference_context(run, baseline_run):
    return copy["partial_summary"]
  if run.status != baseline_run.status:
    return f"{copy['summary_prefix']} also notes a status split: {run.status} versus {baseline_run.status}."
  return None


def _build_comparison_narrative_bullets(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  target_label: str,
  baseline_label: str,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> list[str]:
  bullets: list[str] = []

  lane_context = _build_lane_context_bullet(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
  )
  if lane_context is not None:
    bullets.append(lane_context)

  activity_context = _build_activity_context_bullet(
    intent=intent,
    run=run,
    trade_count_delta=trade_count_delta,
    win_rate_delta=win_rate_delta,
  )
  if activity_context is not None:
    bullets.append(activity_context)

  reference_story = _build_reference_story_bullet(intent=intent, baseline_run=baseline_run, run=run)
  if reference_story is not None:
    bullets.append(reference_story)

  if not bullets and comparison_type == "native_vs_reference":
    bullets.append(f"{COMPARISON_INTENT_COPY[intent]['lane_prefix']}: {target_label} is the reference/native counterpart to {baseline_label}.")
  return bullets[:3]


def _build_lane_context_bullet(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  if comparison_type != "native_vs_reference":
    return None
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = run if run.provenance.lane == "reference" else baseline_run
  native_run = baseline_run if reference_run is run else run
  reference_label = _comparison_run_label(reference_run)
  integration_mode = reference_run.provenance.integration_mode or "external_runtime"
  return (
    f"{copy['lane_prefix']}: native engine {_comparison_run_label(native_run)} is being read against "
    f"reference benchmark {reference_label} via {integration_mode}."
  )


def _build_activity_context_bullet(
  *,
  intent: str,
  run: RunRecord,
  trade_count_delta: float | int | None,
  win_rate_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  trade_count = _resolve_run_metric_value(run, "trade_count")
  win_rate = _resolve_run_metric_value(run, "win_rate_pct")
  segments: list[str] = []
  if trade_count is not None:
    segment = f"trade flow landed at {trade_count}"
    if trade_count_delta is not None:
      segment += f" ({_format_metric_delta(trade_count_delta, 'count')} vs baseline)"
    segments.append(segment)
  if win_rate is not None:
    segment = f"win rate closed at {win_rate}%"
    if win_rate_delta is not None:
      segment += f" ({_format_metric_delta(win_rate_delta, 'pct_points')} vs baseline)"
    segments.append(segment)
  if not segments:
    return None
  return f"{copy['activity_prefix']}: " + "; ".join(segments) + "."


def _build_reference_story_bullet(
  *,
  intent: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = None
  if run.provenance.lane == "reference":
    reference_run = run
  elif baseline_run.provenance.lane == "reference":
    reference_run = baseline_run
  if reference_run is None:
    return None
  benchmark_story = _extract_benchmark_story(reference_run)
  if not benchmark_story:
    return None
  for key in ("headline", "signal_context", "exit_context", "market_context", "pair_context", "portfolio_context"):
    value = benchmark_story.get(key)
    if isinstance(value, str) and value:
      return f"{copy['reference_prefix']}: {value}"
  return None


def _classify_comparison_type(baseline_run: RunRecord, run: RunRecord) -> str:
  lanes = {baseline_run.provenance.lane, run.provenance.lane}
  if lanes == {"native", "reference"}:
    return "native_vs_reference"
  if lanes == {"reference"}:
    return "reference_vs_reference"
  if lanes == {"native"}:
    return "native_vs_native"
  return "run_vs_baseline"


def _comparison_run_label(run: RunRecord) -> str:
  if run.provenance.reference is not None and run.provenance.reference.title:
    return run.provenance.reference.title
  if run.provenance.strategy is not None and run.provenance.strategy.name:
    return run.provenance.strategy.name
  return run.config.strategy_id


def _comparison_subject_label(run: RunRecord) -> str:
  label = _comparison_run_label(run)
  if run.provenance.lane == "reference":
    return f"Reference benchmark {label}"
  if run.provenance.lane == "native":
    return f"Native run {label}"
  return label


def _has_reference_context(run: RunRecord, baseline_run: RunRecord) -> bool:
  return any(candidate.provenance.lane == "reference" for candidate in (run, baseline_run))


def _metric_row_delta(
  metric_row_by_key: dict[str, RunComparisonMetricRow],
  key: str,
  run_id: str,
) -> float | int | None:
  metric_row = metric_row_by_key.get(key)
  if metric_row is None:
    return None
  return metric_row.deltas_vs_baseline.get(run_id)


def _resolve_run_metric_value(run: RunRecord, key: str) -> float | int | None:
  direct_value = _coerce_metric_value(run.metrics.get(key))
  if direct_value is not None:
    return direct_value
  return _extract_benchmark_metric_value(run, key)


def _extract_benchmark_metric_value(run: RunRecord, key: str) -> float | int | None:
  summary_key_map = {
    "total_return_pct": "profit_total_pct",
    "max_drawdown_pct": "max_drawdown_pct",
    "trade_count": "trade_count",
    "win_rate_pct": "win_rate_pct",
  }
  summary_key = summary_key_map.get(key)
  if summary_key is None:
    return None

  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    value = _coerce_metric_value(artifact.summary.get(summary_key))
    if value is not None:
      return value
    if key == "win_rate_pct":
      for section_name, row_key in (
        ("strategy_comparison", "best"),
        ("pair_metrics", "total"),
      ):
        section = artifact.sections.get(section_name)
        if not isinstance(section, dict):
          continue
        candidate_row = section.get(row_key)
        if isinstance(candidate_row, dict):
          value = _coerce_metric_value(candidate_row.get(summary_key))
          if value is not None:
            return value
        preview = section.get("preview")
        if isinstance(preview, list) and preview:
          first_row = preview[0]
          if isinstance(first_row, dict):
            value = _coerce_metric_value(first_row.get(summary_key))
            if value is not None:
              return value
  return None


def _extract_benchmark_story(run: RunRecord) -> dict[str, str]:
  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    story = artifact.sections.get("benchmark_story")
    if not isinstance(story, dict):
      continue
    normalized_story = {
      key: value
      for key, value in story.items()
      if isinstance(value, str) and value
    }
    if normalized_story:
      return normalized_story
  return {}


def _benchmark_artifact_priority(kind: str) -> int:
  priorities = {
    "result_snapshot": 0,
    "result_snapshot_root": 1,
    "result_manifest": 2,
  }
  return priorities.get(kind, 100)


def _format_metric_delta(value: float | int | None, unit: str) -> str:
  if value is None:
    return "n/a"
  prefix = "+" if value > 0 else ""
  if unit == "pct_points":
    return f"{prefix}{value} pts"
  if unit == "count":
    suffix = "trade" if value in {-1, 1} else "trades"
    return f"{prefix}{value} {suffix}"
  return f"{prefix}{value}"


def _coerce_metric_value(value: object) -> float | int | None:
  if isinstance(value, bool) or not isinstance(value, Number):
    return None
  if isinstance(value, int):
    return value
  return round(float(value), 2)


def _calculate_metric_delta(
  value: float | int | None,
  baseline_value: float | int | None,
) -> float | int | None:
  if value is None or baseline_value is None:
    return None
  delta = value - baseline_value
  if isinstance(value, int) and isinstance(baseline_value, int):
    return int(delta)
  return round(float(delta), 2)
