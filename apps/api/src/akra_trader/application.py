from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from numbers import Number
from typing import Callable
from uuid import uuid4

from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonNarrative
from akra_trader.domain.models import RunComparisonMetricRow
from akra_trader.domain.models import RunComparisonRun
from akra_trader.domain.models import GuardedLiveKillSwitch
from akra_trader.domain.models import ClosedTrade
from akra_trader.domain.models import GuardedLiveInternalExposure
from akra_trader.domain.models import GuardedLiveInternalStateSnapshot
from akra_trader.domain.models import GuardedLiveReconciliation
from akra_trader.domain.models import GuardedLiveReconciliationFinding
from akra_trader.domain.models import GuardedLiveRecoveredExposure
from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueSessionHandoff
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import GuardedLiveRuntimeRecovery
from akra_trader.domain.models import GuardedLiveOrderBookSync
from akra_trader.domain.models import GuardedLiveSessionOwnership
from akra_trader.domain.models import GuardedLiveVenueSessionRestore
from akra_trader.domain.models import GuardedLiveVenueSessionSync
from akra_trader.domain.models import Fill
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import OperatorAuditEvent
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentRemediation
from akra_trader.domain.models import OperatorVisibility
from akra_trader.domain.models import Position
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
from akra_trader.domain.services import apply_signal
from akra_trader.domain.services import build_equity_point
from akra_trader.domain.services import summarize_performance
from akra_trader.lineage import build_rerun_boundary_identity
from akra_trader.ports import GuardedLiveStatePort
from akra_trader.ports import MarketDataPort
from akra_trader.ports import OperatorAlertDeliveryPort
from akra_trader.ports import ReferenceCatalogPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.ports import StrategyRuntime
from akra_trader.ports import VenueExecutionPort
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


@dataclass(frozen=True)
class _IncidentPagingPolicy:
  policy_id: str
  provider: str | None
  initial_targets: tuple[str, ...]
  escalation_targets: tuple[str, ...]
  resolution_targets: tuple[str, ...]


@dataclass(frozen=True)
class _IncidentRemediationPlan:
  kind: str
  owner: str
  summary: str
  detail: str
  runbook: str

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
  _guarded_live_worker_kind = "guarded_live_native_worker"
  _guarded_live_balance_tolerance = 1e-9
  _guarded_live_market_data_failure_burst_threshold = 2
  _guarded_live_market_data_backfill_completion_floor = 0.9
  _guarded_live_market_data_contiguous_completion_floor = 0.98
  _guarded_live_drawdown_breach_pct = 35.0
  _guarded_live_loss_breach_pct = 20.0
  _guarded_live_gross_open_risk_ratio = 1.1
  _guarded_live_recovery_alert_threshold = 2

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

  class _UnavailableVenueExecutionAdapter(VenueExecutionPort):
    def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
      return False, ("venue_execution_port_unconfigured",)

    def restore_session(
      self,
      *,
      symbol: str,
      owned_order_ids: tuple[str, ...],
    ) -> GuardedLiveVenueSessionRestore:
      raise RuntimeError("Venue execution port is not configured.")

    def handoff_session(
      self,
      *,
      symbol: str,
      timeframe: str,
      owner_run_id: str,
      owner_session_id: str | None,
      owned_order_ids: tuple[str, ...],
    ) -> GuardedLiveVenueSessionHandoff:
      raise RuntimeError("Venue execution port is not configured.")

    def sync_session(
      self,
      *,
      handoff: GuardedLiveVenueSessionHandoff,
      order_ids: tuple[str, ...],
    ) -> GuardedLiveVenueSessionSync:
      raise RuntimeError("Venue execution port is not configured.")

    def release_session(
      self,
      *,
      handoff: GuardedLiveVenueSessionHandoff,
    ) -> GuardedLiveVenueSessionHandoff:
      raise RuntimeError("Venue execution port is not configured.")

    def submit_market_order(
      self,
      request: GuardedLiveVenueOrderRequest,
    ) -> GuardedLiveVenueOrderResult:
      raise RuntimeError("Venue execution port is not configured.")

    def submit_limit_order(
      self,
      request: GuardedLiveVenueOrderRequest,
    ) -> GuardedLiveVenueOrderResult:
      raise RuntimeError("Venue execution port is not configured.")

    def cancel_order(
      self,
      *,
      symbol: str,
      order_id: str,
    ) -> GuardedLiveVenueOrderResult:
      raise RuntimeError("Venue execution port is not configured.")

    def sync_order_states(
      self,
      *,
      symbol: str,
      order_ids: tuple[str, ...],
    ) -> tuple[GuardedLiveVenueOrderResult, ...]:
      raise RuntimeError("Venue execution port is not configured.")

  class _NoopOperatorAlertDeliveryAdapter(OperatorAlertDeliveryPort):
    def list_targets(self) -> tuple[str, ...]:
      return ()

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ()

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return ()

    def sync_incident_workflow(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return ()

  def __init__(
    self,
    *,
    market_data: MarketDataPort,
    strategies: StrategyCatalogPort,
    references: ReferenceCatalogPort,
    runs: RunRepositoryPort,
    guarded_live_state: GuardedLiveStatePort | None = None,
    venue_state: VenueStatePort | None = None,
    venue_execution: VenueExecutionPort | None = None,
    operator_alert_delivery: OperatorAlertDeliveryPort | None = None,
    freqtrade_reference: FreqtradeReferenceAdapter | None = None,
    mode_service: ExecutionModeService | None = None,
    data_engine: DataEngine | None = None,
    execution_engine: ExecutionEngine | None = None,
    run_supervisor: RunSupervisor | None = None,
    guarded_live_venue: str = "binance",
    guarded_live_execution_enabled: bool = False,
    market_data_sync_timeframes: tuple[str, ...] = ("5m",),
    sandbox_worker_heartbeat_interval_seconds: int = 15,
    sandbox_worker_heartbeat_timeout_seconds: int = 45,
    guarded_live_worker_heartbeat_interval_seconds: int = 15,
    guarded_live_worker_heartbeat_timeout_seconds: int = 45,
    operator_alert_delivery_max_attempts: int = 4,
    operator_alert_delivery_initial_backoff_seconds: int = 15,
    operator_alert_delivery_max_backoff_seconds: int = 300,
    operator_alert_delivery_backoff_multiplier: float = 2.0,
    operator_alert_paging_policy_default_provider: str | None = None,
    operator_alert_paging_policy_warning_targets: tuple[str, ...] = (),
    operator_alert_paging_policy_critical_targets: tuple[str, ...] = (),
    operator_alert_paging_policy_warning_escalation_targets: tuple[str, ...] = (),
    operator_alert_paging_policy_critical_escalation_targets: tuple[str, ...] = (),
    operator_alert_external_sync_token: str | None = None,
    operator_alert_escalation_targets: tuple[str, ...] = (),
    operator_alert_incident_ack_timeout_seconds: int = 300,
    operator_alert_incident_max_escalations: int = 2,
    operator_alert_incident_escalation_backoff_multiplier: float = 2.0,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._clock = clock or (lambda: datetime.now(UTC))
    self._market_data = market_data
    self._strategies = strategies
    self._references = references
    self._runs = runs
    self._guarded_live_state = guarded_live_state or self._EphemeralGuardedLiveStateStore()
    self._venue_state = venue_state or self._UnavailableVenueStateAdapter(self._clock)
    self._venue_execution = venue_execution or self._UnavailableVenueExecutionAdapter()
    self._operator_alert_delivery = (
      operator_alert_delivery or self._NoopOperatorAlertDeliveryAdapter()
    )
    self._freqtrade_reference = freqtrade_reference
    self._mode_service = mode_service or ExecutionModeService()
    self._data_engine = data_engine or DataEngine(market_data)
    self._execution_engine = execution_engine or ExecutionEngine()
    self._run_supervisor = run_supervisor or RunSupervisor()
    self._guarded_live_venue = guarded_live_venue
    self._guarded_live_execution_enabled = guarded_live_execution_enabled
    self._guarded_live_market_data_timeframes = tuple(
      dict.fromkeys(market_data_sync_timeframes or ("5m",))
    )
    self._sandbox_worker_heartbeat_interval_seconds = sandbox_worker_heartbeat_interval_seconds
    self._sandbox_worker_heartbeat_timeout_seconds = sandbox_worker_heartbeat_timeout_seconds
    self._guarded_live_worker_heartbeat_interval_seconds = (
      guarded_live_worker_heartbeat_interval_seconds
    )
    self._guarded_live_worker_heartbeat_timeout_seconds = (
      guarded_live_worker_heartbeat_timeout_seconds
    )
    self._operator_alert_delivery_max_attempts = max(operator_alert_delivery_max_attempts, 1)
    self._operator_alert_delivery_initial_backoff_seconds = max(
      operator_alert_delivery_initial_backoff_seconds,
      1,
    )
    self._operator_alert_delivery_max_backoff_seconds = max(
      operator_alert_delivery_max_backoff_seconds,
      self._operator_alert_delivery_initial_backoff_seconds,
    )
    self._operator_alert_delivery_backoff_multiplier = max(
      operator_alert_delivery_backoff_multiplier,
      1.0,
    )
    self._operator_alert_paging_policy_default_provider = self._normalize_paging_provider(
      operator_alert_paging_policy_default_provider
    )
    self._operator_alert_paging_policy_warning_targets = self._normalize_targets(
      operator_alert_paging_policy_warning_targets
    )
    self._operator_alert_paging_policy_critical_targets = self._normalize_targets(
      operator_alert_paging_policy_critical_targets
    )
    self._operator_alert_paging_policy_warning_escalation_targets = self._normalize_targets(
      operator_alert_paging_policy_warning_escalation_targets
    )
    self._operator_alert_paging_policy_critical_escalation_targets = self._normalize_targets(
      operator_alert_paging_policy_critical_escalation_targets
    )
    self._operator_alert_external_sync_token = operator_alert_external_sync_token
    self._operator_alert_escalation_targets = tuple(
      dict.fromkeys(operator_alert_escalation_targets)
    )
    self._operator_alert_incident_ack_timeout_seconds = max(
      operator_alert_incident_ack_timeout_seconds,
      1,
    )
    self._operator_alert_incident_max_escalations = max(
      operator_alert_incident_max_escalations,
      1,
    )
    self._operator_alert_incident_escalation_backoff_multiplier = max(
      operator_alert_incident_escalation_backoff_multiplier,
      1.0,
    )

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
    sandbox_alerts, sandbox_audit_events = self._collect_sandbox_operator_visibility(
      current_time=current_time
    )
    guarded_live_state, live_alerts = self._refresh_guarded_live_alert_state(
      current_time=current_time
    )
    alerts = [*sandbox_alerts, *live_alerts]
    audit_events = [*sandbox_audit_events, *guarded_live_state.audit_events]
    incident_events = tuple(
      sorted(guarded_live_state.incident_events, key=lambda event: event.timestamp, reverse=True)
    )
    delivery_history = tuple(
      sorted(
        guarded_live_state.delivery_history,
        key=lambda record: record.attempted_at,
        reverse=True,
      )
    )
    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    audit_events.sort(key=lambda event: event.timestamp, reverse=True)
    return OperatorVisibility(
      generated_at=current_time,
      alerts=tuple(alerts),
      alert_history=guarded_live_state.alert_history,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=tuple(audit_events),
    )

  def get_guarded_live_status(self) -> GuardedLiveStatus:
    current_time = self._clock()
    sandbox_alerts, _ = self._collect_sandbox_operator_visibility(current_time=current_time)
    state, live_alerts = self._refresh_guarded_live_alert_state(current_time=current_time)
    runtime_alerts = [*sandbox_alerts, *live_alerts]
    running_sandbox_count = self._count_running_runs(RunMode.SANDBOX)
    running_paper_count = self._count_running_runs(RunMode.PAPER)
    running_live_count = self._count_running_runs(RunMode.LIVE)
    venue_execution_ready, venue_execution_issues = self._venue_execution.describe_capability()

    blockers: list[str] = []
    if not self._guarded_live_execution_enabled:
      blockers.append("Guarded-live venue execution is disabled in configuration.")
    if state.kill_switch.state == "engaged":
      blockers.append("Kill switch is engaged for operator-controlled runtime sessions.")
    if state.reconciliation.state != "clear":
      blockers.append("Guarded-live reconciliation has not been cleared.")
    if state.recovery.state not in {"recovered", "recovered_with_warnings"}:
      blockers.append("Guarded-live runtime recovery has not been recorded from venue snapshots.")
    if state.recovery.state == "failed":
      blockers.append("Guarded-live runtime recovery failed after the latest restart or fault drill.")
    if not venue_execution_ready:
      blockers.append(
        "Venue order execution is unavailable: "
        + (", ".join(venue_execution_issues) if venue_execution_issues else "adapter not ready")
        + "."
      )
    if state.ownership.state in {"owned", "orphaned"} and state.ownership.owner_run_id is not None:
      blockers.append(
        "Guarded-live session ownership is still held by "
        f"{state.ownership.owner_run_id}. Resume or release it before launching a new live worker."
      )
    if runtime_alerts:
      blockers.append("Unresolved operator alerts remain in runtime operations.")

    audit_events = tuple(
      sorted(state.audit_events, key=lambda event: event.timestamp, reverse=True)
    )
    incident_events = tuple(
      sorted(state.incident_events, key=lambda event: event.timestamp, reverse=True)
    )
    delivery_history = tuple(
      sorted(state.delivery_history, key=lambda record: record.attempted_at, reverse=True)
    )
    return GuardedLiveStatus(
      generated_at=current_time,
      candidacy_status="blocked" if blockers else "candidate",
      blockers=tuple(dict.fromkeys(blockers)),
      active_alerts=tuple(live_alerts),
      alert_history=state.alert_history,
      incident_events=incident_events,
      delivery_history=delivery_history,
      kill_switch=state.kill_switch,
      reconciliation=state.reconciliation,
      recovery=state.recovery,
      ownership=state.ownership,
      order_book=state.order_book,
      session_restore=state.session_restore,
      session_handoff=state.session_handoff,
      audit_events=audit_events,
      active_runtime_alert_count=len(runtime_alerts),
      running_sandbox_count=running_sandbox_count,
      running_paper_count=running_paper_count,
      running_live_count=running_live_count,
    )

  def _collect_sandbox_operator_visibility(
    self,
    *,
    current_time: datetime,
  ) -> tuple[list[OperatorAlert], list[OperatorAuditEvent]]:
    alerts: list[OperatorAlert] = []
    audit_events: list[OperatorAuditEvent] = []
    for run in self._runs.list_runs(mode=RunMode.SANDBOX.value):
      alerts.extend(self._build_operator_alerts_for_run(run=run, current_time=current_time))
      audit_events.extend(self._build_operator_audit_events_for_run(run=run, current_time=current_time))
    return alerts, audit_events

  def _refresh_guarded_live_alert_state(
    self,
    *,
    current_time: datetime,
    allow_post_remediation_recompute: bool = True,
  ) -> tuple[GuardedLiveState, list[OperatorAlert]]:
    state = self._guarded_live_state.load_state()
    active_alerts = self._build_guarded_live_operator_alerts(
      state=state,
      current_time=current_time,
    )
    merged_history = self._merge_operator_alert_history(
      existing=state.alert_history,
      active_alerts=active_alerts,
      current_time=current_time,
    )
    incident_events = self._build_guarded_live_incident_events(
      previous_history=state.alert_history,
      merged_history=merged_history,
      current_time=current_time,
    )
    delivery_records = state.delivery_history
    new_incident_events, new_delivery_records, auto_remediation_executed = self._deliver_guarded_live_incident_events(
      incident_events=incident_events,
      current_time=current_time,
    )
    delivery_records = tuple((*new_delivery_records, *delivery_records))
    workflow_incident_events, workflow_delivery_history, workflow_audit_events = (
      self._refresh_guarded_live_incident_workflow(
        incident_events=tuple((*new_incident_events, *state.incident_events)),
        delivery_history=delivery_records,
        current_time=current_time,
      )
    )
    delivery_records = workflow_delivery_history
    refreshed_incident_events = self._apply_incident_delivery_state(
      incident_events=workflow_incident_events,
      delivery_history=delivery_records,
    )
    retry_delivery_records = self._retry_guarded_live_incident_deliveries(
      incident_events=refreshed_incident_events,
      delivery_history=delivery_records,
      current_time=current_time,
    )
    if retry_delivery_records:
      delivery_records = tuple((*retry_delivery_records, *delivery_records))
      refreshed_incident_events = self._apply_incident_delivery_state(
        incident_events=refreshed_incident_events,
        delivery_history=delivery_records,
      )
    if (
      merged_history != state.alert_history
      or refreshed_incident_events != state.incident_events
      or delivery_records != state.delivery_history
      or bool(workflow_audit_events)
    ):
      latest_state = self._guarded_live_state.load_state()
      state = self._persist_guarded_live_state(
        replace(
          latest_state,
          alert_history=merged_history,
          incident_events=refreshed_incident_events,
          delivery_history=delivery_records,
          audit_events=tuple((*workflow_audit_events, *latest_state.audit_events)),
        )
      )
    if auto_remediation_executed and allow_post_remediation_recompute:
      return self._refresh_guarded_live_alert_state(
        current_time=current_time,
        allow_post_remediation_recompute=False,
      )
    return state, active_alerts

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
    reconciliation = self._build_guarded_live_reconciliation(
      state=state,
      checked_at=current_time,
      checked_by=actor,
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
    recovered_open_orders = snapshot.open_orders or state.order_book.open_orders
    if not snapshot.open_orders and state.order_book.open_orders:
      recovery_issues = (*recovery_issues, "using_durable_order_book_sync")

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
    projected_state = replace(state, recovery=recovery_state)
    refreshed_reconciliation = self._build_guarded_live_reconciliation(
      state=projected_state,
      checked_at=current_time,
      checked_by=actor,
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
        projected_state,
        reconciliation=refreshed_reconciliation,
        recovery=recovery_state,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def acknowledge_guarded_live_incident(
    self,
    *,
    event_id: str,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    incident = self._require_active_guarded_live_incident(state=state, event_id=event_id)
    if incident.acknowledgment_state == "acknowledged":
      return self.get_guarded_live_status()

    updated_incident = replace(
      incident,
      acknowledgment_state="acknowledged",
      acknowledged_at=current_time,
      acknowledged_by=actor,
      acknowledgment_reason=reason,
      next_escalation_at=None,
    )
    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    delivery_history = self._suppress_pending_incident_retries(
      delivery_history=state.delivery_history,
      incident_event_id=event_id,
      reason="acknowledged_by_operator",
    )
    updated_incident, delivery_history = self._sync_incident_provider_workflow(
      incident=updated_incident,
      delivery_history=delivery_history,
      current_time=current_time,
      action="acknowledge",
      actor=actor,
      detail=reason,
    )
    incident_events = self._replace_incident_event(
      incident_events=incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-acknowledged:{event_id}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_incident_acknowledged",
      summary=f"Guarded-live incident acknowledged for {incident.alert_id}.",
      detail=(
        f"Reason: {reason}. Incident {event_id} acknowledged and pending retries suppressed. "
        f"Provider workflow: {updated_incident.provider_workflow_state}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(audit_event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def remediate_guarded_live_incident(
    self,
    *,
    event_id: str,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    incident = self._require_active_guarded_live_incident(state=state, event_id=event_id)
    if incident.remediation.state == "not_applicable":
      raise ValueError("Guarded-live incident does not expose a remediation workflow")

    incident, local_results = self._execute_local_incident_remediation(
      incident=incident,
      actor=actor,
      current_time=current_time,
    )

    delivery_history = self._suppress_pending_incident_retries(
      delivery_history=state.delivery_history,
      incident_event_id=event_id,
      reason="manual_remediation_requested",
      phase="provider_remediate",
    )
    updated_incident, remediation_records = self._request_incident_remediation(
      incident=incident,
      delivery_history=delivery_history,
      current_time=current_time,
      actor=actor,
      detail=reason,
    )
    delivery_history = tuple((*remediation_records, *delivery_history))
    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-remediation-requested:{event_id}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_incident_remediation_requested",
      summary=f"Guarded-live remediation requested for {incident.alert_id}.",
      detail=(
        f"Reason: {reason}. Remediation state: {updated_incident.remediation.state}. "
        f"Provider workflow: {updated_incident.provider_workflow_state}. "
        f"Local execution: {self._summarize_local_remediation_results(local_results)}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    latest_state = self._guarded_live_state.load_state()
    self._persist_guarded_live_state(
      replace(
        latest_state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(audit_event, *latest_state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def escalate_guarded_live_incident(
    self,
    *,
    event_id: str,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    incident = self._require_active_guarded_live_incident(state=state, event_id=event_id)
    if incident.escalation_level >= self._operator_alert_incident_max_escalations:
      raise ValueError("incident escalation limit reached")

    (
      updated_incident,
      delivery_history,
      escalation_audit_event,
    ) = self._escalate_incident_event(
      incident=incident,
      delivery_history=state.delivery_history,
      current_time=current_time,
      actor=actor,
      reason=reason,
      trigger="manual_operator_escalation",
    )
    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    self._persist_guarded_live_state(
      replace(
        state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(escalation_audit_event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def require_operator_alert_external_sync_token(self, token: str | None) -> None:
    if self._operator_alert_external_sync_token is None:
      return
    if token != self._operator_alert_external_sync_token:
      raise PermissionError("invalid operator incident sync token")

  def sync_guarded_live_incident_from_external(
    self,
    *,
    provider: str,
    event_kind: str,
    actor: str,
    detail: str,
    alert_id: str | None = None,
    external_reference: str | None = None,
    workflow_reference: str | None = None,
    occurred_at: datetime | None = None,
    escalation_level: int | None = None,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    synced_at = occurred_at or current_time
    normalized_provider = provider.strip().lower().replace(" ", "_")
    normalized_kind = self._normalize_external_incident_event_kind(event_kind)
    incident = self._find_guarded_live_incident_for_external_sync(
      state=state,
      alert_id=alert_id,
      external_reference=external_reference,
    )
    effective_reference = external_reference or incident.external_reference or alert_id or incident.alert_id
    detail_copy = detail.strip() or f"{normalized_provider}_{normalized_kind}"
    updated_incident = replace(
      incident,
      paging_provider=normalized_provider or incident.paging_provider,
      external_provider=normalized_provider,
      external_reference=effective_reference,
      provider_workflow_reference=workflow_reference or incident.provider_workflow_reference,
      external_last_synced_at=synced_at,
    )
    delivery_history = state.delivery_history
    local_results: tuple[MarketDataRemediationResult, ...] = ()

    if normalized_kind == "triggered":
      updated_incident = replace(
        updated_incident,
        external_status="triggered",
        paging_status="triggered",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or effective_reference,
      )
    elif normalized_kind == "acknowledged":
      if updated_incident.acknowledgment_state != "acknowledged":
        updated_incident = replace(
          updated_incident,
          acknowledgment_state="acknowledged",
          acknowledged_at=synced_at,
          acknowledged_by=f"{normalized_provider}:{actor}",
          acknowledgment_reason=detail_copy,
          next_escalation_at=None,
        )
      updated_incident = replace(
        updated_incident,
        external_status="acknowledged",
        paging_status="acknowledged",
      )
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_acknowledged:{normalized_provider}",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or incident.provider_workflow_reference or effective_reference,
      )
    elif normalized_kind == "escalated":
      next_level = max(updated_incident.escalation_level + 1, escalation_level or 1)
      next_level = min(next_level, self._operator_alert_incident_max_escalations)
      next_escalation_at = None
      if (
        updated_incident.acknowledgment_state != "acknowledged"
        and next_level < self._operator_alert_incident_max_escalations
      ):
        next_escalation_at = synced_at + timedelta(
          seconds=self._resolve_incident_escalation_backoff_seconds(next_level)
        )
      updated_incident = replace(
        updated_incident,
        escalation_level=next_level,
        escalation_state="escalated",
        last_escalated_at=synced_at,
        last_escalated_by=f"{normalized_provider}:{actor}",
        escalation_reason=detail_copy,
        next_escalation_at=next_escalation_at,
        external_status="escalated",
        paging_status="escalated",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or incident.provider_workflow_reference or effective_reference,
      )
    elif normalized_kind == "resolved":
      if updated_incident.acknowledgment_state != "acknowledged":
        updated_incident = replace(
          updated_incident,
          acknowledgment_state="acknowledged",
          acknowledged_at=synced_at,
          acknowledged_by=f"{normalized_provider}:{actor}",
          acknowledgment_reason=detail_copy,
        )
      updated_incident = replace(
        updated_incident,
        external_status="resolved",
        paging_status="resolved",
        next_escalation_at=None,
      )
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_resolved:{normalized_provider}",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or incident.provider_workflow_reference or effective_reference,
      )
    elif normalized_kind == "remediation_requested":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = replace(
        updated_incident,
        remediation=replace(
          updated_incident.remediation,
          state="requested",
          requested_at=updated_incident.remediation.requested_at or synced_at,
          requested_by=f"{normalized_provider}:{actor}",
          last_attempted_at=synced_at,
          provider=normalized_provider or updated_incident.remediation.provider,
          reference=workflow_reference or effective_reference,
          detail=detail_copy,
        ),
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or incident.provider_workflow_reference or effective_reference,
      )
    elif normalized_kind == "remediation_started":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = replace(
        updated_incident,
        remediation=replace(
          updated_incident.remediation,
          state="provider_recovering",
          requested_at=updated_incident.remediation.requested_at or synced_at,
          requested_by=f"{normalized_provider}:{actor}",
          last_attempted_at=synced_at,
          provider=normalized_provider or updated_incident.remediation.provider,
          reference=workflow_reference or effective_reference,
          detail=detail_copy,
        ),
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or incident.provider_workflow_reference or effective_reference,
      )
    elif normalized_kind == "remediation_completed":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = replace(
        updated_incident,
        remediation=replace(
          updated_incident.remediation,
          state="provider_recovered",
          requested_at=updated_incident.remediation.requested_at or synced_at,
          requested_by=f"{normalized_provider}:{actor}",
          last_attempted_at=synced_at,
          provider=normalized_provider or updated_incident.remediation.provider,
          reference=workflow_reference or effective_reference,
          detail=detail_copy,
        ),
      )
      updated_incident, local_results = self._execute_local_incident_remediation(
        incident=updated_incident,
        actor=f"{normalized_provider}:{actor}",
        current_time=synced_at,
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or incident.provider_workflow_reference or effective_reference,
      )
    elif normalized_kind == "remediation_failed":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = replace(
        updated_incident,
        remediation=replace(
          updated_incident.remediation,
          state="failed",
          requested_at=updated_incident.remediation.requested_at or synced_at,
          requested_by=f"{normalized_provider}:{actor}",
          last_attempted_at=synced_at,
          provider=normalized_provider or updated_incident.remediation.provider,
          reference=workflow_reference or effective_reference,
          detail=detail_copy,
        ),
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or incident.provider_workflow_reference or effective_reference,
      )
    else:
      raise ValueError(f"unsupported external incident event kind: {event_kind}")

    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-external-sync:{incident.event_id}:{synced_at.isoformat()}",
      timestamp=synced_at,
      actor=f"{normalized_provider}:{actor}",
      kind="guarded_live_incident_external_synced",
      summary=f"Guarded-live incident synced from external paging workflow for {incident.alert_id}.",
      detail=(
        f"External event {normalized_kind} synced from {normalized_provider}. "
        f"Reference: {effective_reference}. Detail: {detail_copy}. "
        f"Local remediation: {self._summarize_local_remediation_results(local_results)}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(audit_event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  @staticmethod
  def _normalize_external_incident_event_kind(event_kind: str) -> str:
    normalized = event_kind.strip().lower().replace("-", "_")
    mapping = {
      "recovery_requested": "remediation_requested",
      "recovery_started": "remediation_started",
      "recovered": "remediation_completed",
      "recovery_completed": "remediation_completed",
      "recovery_failed": "remediation_failed",
    }
    return mapping.get(normalized, normalized)

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

  def start_live_run(
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
    operator_reason: str = "guarded_live_launch",
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    return self._start_live_session(
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

  def _start_live_session(
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
    operator_reason: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    self._ensure_guarded_live_worker_start_allowed()
    state = self._guarded_live_state.load_state()
    strategy, metadata, strategy_snapshot = self._prepare_strategy(strategy_id=strategy_id, parameters=parameters)
    config = RunConfig(
      run_id=str(uuid4()),
      mode=RunMode.LIVE,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue=self._guarded_live_venue,
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
        status=RunStatus.FAILED,
        provenance=RunProvenance(lane="reference", strategy=strategy_snapshot),
      )
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        "Guarded live remains on the native venue-backed worker path."
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
        f"Guarded live worker requires at least {required_bars} candles to prime the current strategy state."
      )
      return self._runs.save_run(run)

    latest_row = enriched.iloc[-1]
    latest_timestamp = latest_row["timestamp"].to_pydatetime()
    latest_market_price = float(latest_row["close"])
    cache = self._build_guarded_live_cache(
      config=config,
      state=state,
      fallback_cash=initial_cash,
      latest_market_price=latest_market_price,
    )
    self._seed_guarded_live_runtime_state(
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
    self._run_supervisor.start_mode(
      run=run,
      mode=RunMode.LIVE,
      mode_service=self._mode_service,
      replay_bars=None,
    )
    primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
    self._run_supervisor.start_worker_session(
      run=run,
      worker_kind=self._guarded_live_worker_kind,
      heartbeat_interval_seconds=self._guarded_live_worker_heartbeat_interval_seconds,
      heartbeat_timeout_seconds=self._guarded_live_worker_heartbeat_timeout_seconds,
      now=self._clock(),
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
    saved_run = self._runs.save_run(run)
    session_handoff = self._activate_guarded_live_venue_session(
      run=saved_run,
      reason=operator_reason,
    )
    saved_run = self._runs.save_run(saved_run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor="operator",
      reason=operator_reason,
      session_handoff=session_handoff,
    )
    self._append_guarded_live_audit_event(
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

  def stop_live_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    self._run_supervisor.stop(
      run,
      reason="Guarded-live worker stopped by operator. Venue open orders remain operator-managed.",
    )
    saved_run = self._runs.save_run(run)
    session_handoff = self._release_guarded_live_venue_session(run=saved_run)
    saved_run = self._runs.save_run(saved_run)
    self._release_guarded_live_session_ownership(
      run=saved_run,
      actor="operator",
      reason="operator_stop",
      ownership_state="released",
      session_handoff=session_handoff,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_worker_stopped",
      actor="operator",
      summary=f"Guarded-live worker stopped for {run.config.symbols[0]}.",
      detail="Operator stop requested for the guarded-live worker session.",
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def resume_guarded_live_run(
    self,
    *,
    actor: str,
    reason: str,
  ) -> RunRecord:
    self._ensure_guarded_live_resume_allowed()
    state = self._guarded_live_state.load_state()
    if state.ownership.owner_run_id is None:
      raise ValueError("No guarded-live session ownership is available to resume.")
    run = self._runs.get_run(state.ownership.owner_run_id)
    if run is None:
      raise LookupError("Owned guarded-live run not found")
    if run.config.mode != RunMode.LIVE:
      raise ValueError("Guarded-live ownership does not point to a live run.")
    if run.status in {RunStatus.STOPPED, RunStatus.COMPLETED}:
      raise ValueError("Terminal guarded-live runs cannot be resumed.")

    current_time = self._clock()
    if run.status == RunStatus.FAILED:
      run.status = RunStatus.RUNNING
      run.ended_at = None
    last_processed_candle_at = self._infer_last_processed_candle_at(run)
    self._run_supervisor.recover_worker_session(
      run=run,
      worker_kind=self._guarded_live_worker_kind,
      heartbeat_interval_seconds=self._guarded_live_worker_heartbeat_interval_seconds,
      heartbeat_timeout_seconds=self._guarded_live_worker_heartbeat_timeout_seconds,
      reason="operator_resume",
      now=current_time,
      started_at=run.started_at,
      primed_candle_count=self._infer_sandbox_primed_candle_count(run),
      processed_tick_count=run.provenance.runtime_session.processed_tick_count if run.provenance.runtime_session else 0,
      last_processed_candle_at=last_processed_candle_at,
      last_seen_candle_at=last_processed_candle_at,
    )
    session_restore = self._restore_guarded_live_venue_session(
      run=run,
      state=state,
      reason=reason,
    )
    if session_restore.state == "fallback_snapshot":
      try:
        self._sync_guarded_live_orders(run)
      except Exception as exc:
        run.notes.append(
          f"{current_time.isoformat()} | guarded_live_order_book_resume_warning | {exc}"
        )
    session_handoff = self._activate_guarded_live_venue_session(
      run=run,
      reason=reason,
    )
    self._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_worker_resumed | {reason}"
    )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    saved_run = self._runs.save_run(run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor=actor,
      reason=reason,
      resumed=True,
      session_restore=session_restore,
      session_handoff=session_handoff,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_worker_resumed",
      actor=actor,
      summary=f"Guarded-live worker resumed for {saved_run.config.symbols[0]}.",
      detail=f"Reason: {reason}.",
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def cancel_live_order(
    self,
    *,
    run_id: str,
    order_id: str,
    actor: str,
    reason: str,
  ) -> RunRecord:
    run, order = self._prepare_guarded_live_order_action(
      run_id=run_id,
      order_id=order_id,
      require_active=True,
    )
    venue_result = self._venue_execution.cancel_order(
      symbol=run.config.symbols[0],
      order_id=order.order_id,
    )
    self._apply_guarded_live_synced_order_state(run=run, order=order, synced_state=venue_result)
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    run.notes.append(
      f"{self._clock().isoformat()} | guarded_live_order_canceled | "
      f"Reason: {reason}. Operator requested cancel for {order.order_id} and venue returned {order.status.value}."
    )
    saved_run = self._runs.save_run(run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor=actor,
      reason=reason,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_order_canceled",
      actor=actor,
      summary=f"Guarded-live order canceled for {run.config.symbols[0]}.",
      detail=(
        f"Reason: {reason}. Operator canceled {order.order_id}; "
        f"remaining quantity is {self._resolve_guarded_live_order_remaining_quantity(order):.8f} "
        f"and venue state is {order.status.value}."
      ),
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def replace_live_order(
    self,
    *,
    run_id: str,
    order_id: str,
    price: float,
    quantity: float | None,
    actor: str,
    reason: str,
  ) -> RunRecord:
    if price <= 0:
      raise ValueError("Replacement price must be positive.")
    self._ensure_guarded_live_live_order_replace_allowed()
    run, order = self._prepare_guarded_live_order_action(
      run_id=run_id,
      order_id=order_id,
      require_active=True,
    )
    remaining_quantity = self._resolve_guarded_live_order_remaining_quantity(order)
    replacement_quantity = quantity if quantity is not None else remaining_quantity
    if replacement_quantity <= self._guarded_live_balance_tolerance:
      raise ValueError("Replacement quantity resolved to zero.")
    if replacement_quantity - remaining_quantity > self._guarded_live_balance_tolerance:
      raise ValueError("Replacement quantity cannot exceed the current remaining order quantity.")

    cancel_result = self._venue_execution.cancel_order(
      symbol=run.config.symbols[0],
      order_id=order.order_id,
    )
    self._apply_guarded_live_synced_order_state(run=run, order=order, synced_state=cancel_result)
    if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
      raise RuntimeError(
        f"Guarded-live order replacement requires the current order to be canceled first: {order.order_id}"
      )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    run = self._runs.save_run(run)
    order = self._get_guarded_live_order(run=run, order_id=order_id)

    replacement_order = Order(
      run_id=run.config.run_id,
      instrument_id=order.instrument_id,
      side=order.side,
      quantity=replacement_quantity,
      requested_price=price,
      order_type=OrderType.LIMIT,
    )
    venue_result = self._submit_guarded_live_limit_order(
      run=run,
      order=replacement_order,
      limit_price=price,
    )
    replacement_order.order_id = venue_result.order_id
    replacement_order.created_at = venue_result.submitted_at
    replacement_order.updated_at = venue_result.updated_at or venue_result.submitted_at
    replacement_order.last_synced_at = venue_result.updated_at or venue_result.submitted_at
    replacement_order.status = self._map_guarded_live_order_status(
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
    if replacement_order.filled_quantity > self._guarded_live_balance_tolerance:
      self._materialize_guarded_live_fill_delta(
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
      f"{self._clock().isoformat()} | guarded_live_order_replaced | "
      f"Reason: {reason}. Replaced {order.order_id} with {replacement_order.order_id} "
      f"for {replacement_quantity:.8f} at {price:.8f}."
    )
    saved_run = self._runs.save_run(run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor=actor,
      reason=reason,
    )
    self._append_guarded_live_audit_event(
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

  def _ensure_operator_control_runtime_allowed(self, mode: RunMode) -> None:
    if mode not in {RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE}:
      return
    state = self._guarded_live_state.load_state()
    if state.kill_switch.state == "engaged":
      raise ValueError(
        "Guarded-live kill switch is engaged. Release it before starting operator-controlled runtime sessions."
      )

  def _ensure_guarded_live_worker_start_allowed(self) -> None:
    self._ensure_operator_control_runtime_allowed(RunMode.LIVE)
    status = self.get_guarded_live_status()
    if status.running_live_count > 0:
      raise ValueError("A guarded-live worker is already running. Stop it before launching another.")
    if status.blockers:
      raise ValueError("Guarded-live launch is blocked: " + " ".join(status.blockers))

  def _ensure_guarded_live_live_order_replace_allowed(self) -> None:
    state = self._guarded_live_state.load_state()
    if state.kill_switch.state == "engaged":
      raise ValueError("Guarded-live kill switch is engaged. Cancel venue orders instead of replacing them.")
    ready, issues = self._venue_execution.describe_capability()
    if not ready:
      raise RuntimeError(
        "Venue order execution is unavailable: "
        + (", ".join(issues) if issues else "adapter not ready")
        + "."
      )

  def _ensure_guarded_live_resume_allowed(self) -> None:
    state = self._guarded_live_state.load_state()
    if state.kill_switch.state == "engaged":
      raise ValueError("Guarded-live kill switch is engaged. Release it before resuming live execution.")
    if state.recovery.state not in {"recovered", "recovered_with_warnings"}:
      raise ValueError("Guarded-live runtime recovery must be recorded before resume.")
    ready, issues = self._venue_execution.describe_capability()
    if not ready:
      raise RuntimeError(
        "Venue order execution is unavailable: "
        + (", ".join(issues) if issues else "adapter not ready")
        + "."
      )
    if state.ownership.state not in {"owned", "orphaned"}:
      raise ValueError("No guarded-live session ownership is available to resume.")

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
    if session_restore.open_orders:
      return True
    return any(result.status != "unknown" for result in session_restore.synced_orders)

  def _apply_guarded_live_restored_session(
    self,
    *,
    run: RunRecord,
    session_restore: GuardedLiveVenueSessionRestore,
  ) -> int:
    existing_orders = {order.order_id: order for order in run.orders}
    open_orders_by_id = {
      order.order_id: order
      for order in session_restore.open_orders
    }
    state_changes = 0
    for synced_state in session_restore.synced_orders:
      if synced_state.status == "unknown":
        continue
      order = existing_orders.get(synced_state.order_id)
      if order is None:
        order = self._materialize_guarded_live_restored_order(
          run=run,
          synced_state=synced_state,
          open_order=open_orders_by_id.get(synced_state.order_id),
        )
        existing_orders[order.order_id] = order
        state_changes += 1
      state_changes += self._apply_guarded_live_synced_order_state(
        run=run,
        order=order,
        synced_state=synced_state,
      )

    for open_order in session_restore.open_orders:
      if open_order.order_id in existing_orders:
        continue
      order = self._materialize_guarded_live_restored_order(
        run=run,
        synced_state=None,
        open_order=open_order,
      )
      existing_orders[order.order_id] = order
      state_changes += 1

    if state_changes > 0:
      run.metrics = summarize_performance(
        initial_cash=run.config.initial_cash,
        equity_curve=run.equity_curve,
        closed_trades=run.closed_trades,
      )
    return state_changes

  def _materialize_guarded_live_restored_order(
    self,
    *,
    run: RunRecord,
    synced_state: GuardedLiveVenueOrderResult | None,
    open_order: GuardedLiveVenueOpenOrder | None,
  ) -> Order:
    symbol = run.config.symbols[0]
    restored_at = synced_state.submitted_at if synced_state is not None else self._clock()
    explicit_price = None
    if synced_state is not None:
      explicit_price = synced_state.requested_price
    if explicit_price is None and open_order is not None:
      explicit_price = open_order.price
    quantity = (
      (synced_state.requested_amount if synced_state is not None else None)
      or (synced_state.amount if synced_state is not None and synced_state.amount > 0 else None)
      or (open_order.amount if open_order is not None else None)
      or 0.0
    )
    restored_order = Order(
      run_id=run.config.run_id,
      instrument_id=f"{run.config.venue}:{symbol}",
      side=self._resolve_order_side(
        synced_state.side if synced_state is not None else open_order.side if open_order is not None else "buy"
      ),
      quantity=quantity,
      requested_price=(
        explicit_price
        if explicit_price is not None
        else (synced_state.average_fill_price if synced_state is not None and synced_state.average_fill_price is not None else 0.0)
      ),
      order_type=OrderType.LIMIT if explicit_price is not None else OrderType.MARKET,
      status=(
        self._map_guarded_live_order_status(
          open_order.status,
          filled_quantity=0.0,
          remaining_quantity=quantity,
        )
        if open_order is not None
        else OrderStatus.OPEN
      ),
      order_id=synced_state.order_id if synced_state is not None else open_order.order_id,
      created_at=restored_at,
      updated_at=synced_state.updated_at if synced_state is not None else restored_at,
      last_synced_at=synced_state.updated_at if synced_state is not None else restored_at,
      remaining_quantity=quantity,
    )
    run.orders.append(restored_order)
    return restored_order

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

  def _build_guarded_live_reconciliation_result(
    self,
    *,
    state: GuardedLiveState | None = None,
  ) -> tuple[
    GuardedLiveInternalStateSnapshot,
    GuardedLiveVenueStateSnapshot,
    list[GuardedLiveReconciliationFinding],
  ]:
    findings: list[GuardedLiveReconciliationFinding] = []
    effective_state = state or self._guarded_live_state.load_state()
    internal_snapshot = self._build_guarded_live_internal_snapshot(state=effective_state)
    venue_snapshot = self._venue_state.capture_snapshot()

    if venue_snapshot.venue != self._guarded_live_venue:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="guarded_live_venue_mismatch",
          severity="critical",
          summary="Venue-state snapshot does not match the configured guarded-live venue.",
          detail=(
            f"Guarded-live is configured for {self._guarded_live_venue}, "
            f"but venue-state reconciliation captured {venue_snapshot.venue}."
          ),
        )
      )

    sandbox_alerts, _ = self._collect_sandbox_operator_visibility(current_time=self._clock())
    if sandbox_alerts:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="runtime_alerts_present",
          severity="warning",
          summary=f"{len(sandbox_alerts)} unresolved runtime alert(s) remain active.",
          detail="Guarded-live candidacy stays blocked while sandbox runtime alerts remain unresolved.",
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

    inconsistent_live_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_live_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="live_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_live_runs)} live run(s) are missing persisted runtime session state."
          ),
          detail="Guarded-live workers must keep runtime-session state for restart safety and venue auditability.",
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

    stale_terminal_live_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_live_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_live_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_live_sessions)} terminal live run(s) still report an active runtime session."
          ),
          detail="Terminal guarded-live runs should not keep active worker-session state after stop or failure.",
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

  def maintain_guarded_live_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]:
    if not self._guarded_live_execution_enabled:
      return {
        "maintained": 0,
        "recovered": 0,
        "ticks_processed": 0,
        "orders_submitted": 0,
        "orders_synced": 0,
      }

    maintained = 0
    recovered = 0
    ticks_processed = 0
    orders_submitted = 0
    orders_synced = 0
    current_time = self._clock()
    for run in self._runs.list_runs(mode=RunMode.LIVE.value):
      if run.status != RunStatus.RUNNING:
        continue
      try:
        state = self._guarded_live_state.load_state()
        if force_recovery or self._run_supervisor.needs_worker_recovery(run=run, now=current_time):
          self._run_supervisor.recover_worker_session(
            run=run,
            worker_kind=self._guarded_live_worker_kind,
            heartbeat_interval_seconds=self._guarded_live_worker_heartbeat_interval_seconds,
            heartbeat_timeout_seconds=self._guarded_live_worker_heartbeat_timeout_seconds,
            reason=recovery_reason,
            now=current_time,
            started_at=run.started_at,
            primed_candle_count=self._infer_sandbox_primed_candle_count(run),
            processed_tick_count=run.provenance.runtime_session.processed_tick_count if run.provenance.runtime_session else 0,
            last_processed_candle_at=self._infer_last_processed_candle_at(run),
            last_seen_candle_at=self._infer_last_processed_candle_at(run),
          )
          run.notes.append(
            f"{current_time.isoformat()} | guarded_live_worker_recovered | {recovery_reason}"
          )
          self._append_guarded_live_audit_event(
            kind="guarded_live_worker_recovered",
            actor="system",
            summary=f"Guarded-live worker recovered for {run.config.symbols[0]}.",
            detail=f"Recovery reason: {recovery_reason}.",
            run_id=run.config.run_id,
            session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
          )
          recovered += 1

        session_handoff = state.session_handoff
        if session_handoff.owner_run_id == run.config.run_id and session_handoff.state == "active":
          session_sync = self._sync_guarded_live_session(run=run, handoff=session_handoff)
          orders_synced += session_sync["synced"]
          session_handoff = session_sync["handoff"]
        else:
          orders_synced += self._sync_guarded_live_orders(run)
          session_handoff = self._activate_guarded_live_venue_session(
            run=run,
            reason=recovery_reason if force_recovery else "worker_heartbeat",
          )
        advance = self._advance_guarded_live_worker_run(run)
        ticks_processed += advance["ticks_processed"]
        orders_submitted += advance["orders_submitted"]
        self._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
        self._claim_guarded_live_session_ownership(
          run=run,
          actor="system",
          reason=recovery_reason if force_recovery else "worker_heartbeat",
          resumed=force_recovery,
          session_handoff=session_handoff,
        )
      except Exception as exc:
        self._run_supervisor.fail(
          run,
          reason=f"{current_time.isoformat()} | guarded_live_worker_failed | {exc}",
          now=current_time,
        )
        session_handoff = self._release_guarded_live_venue_session(run=run)
        self._release_guarded_live_session_ownership(
          run=run,
          actor="system",
          reason=str(exc),
          ownership_state="orphaned",
          session_handoff=session_handoff,
        )
        self._append_guarded_live_audit_event(
          kind="guarded_live_worker_failed",
          actor="system",
          summary=f"Guarded-live worker failed for {run.config.symbols[0]}.",
          detail=str(exc),
          run_id=run.config.run_id,
          session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
        )
      self._runs.save_run(run)
      maintained += 1

    return {
      "maintained": maintained,
      "recovered": recovered,
      "ticks_processed": ticks_processed,
      "orders_submitted": orders_submitted,
      "orders_synced": orders_synced,
    }

  def _sync_guarded_live_orders(self, run: RunRecord) -> int:
    tracked_orders = [
      order
      for order in run.orders
      if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}
    ]
    if not tracked_orders:
      return 0

    synced_states = {
      state.order_id: state
      for state in self._venue_execution.sync_order_states(
        symbol=run.config.symbols[0],
        order_ids=tuple(order.order_id for order in tracked_orders),
      )
    }
    synced_count = 0
    for order in tracked_orders:
      synced_state = synced_states.get(order.order_id)
      if synced_state is None:
        continue
      synced_count += self._apply_guarded_live_synced_order_state(
        run=run,
        order=order,
        synced_state=synced_state,
      )
    if synced_count > 0:
      run.metrics = summarize_performance(
        initial_cash=run.config.initial_cash,
        equity_curve=run.equity_curve,
        closed_trades=run.closed_trades,
      )
    return synced_count

  def _sync_guarded_live_session(
    self,
    *,
    run: RunRecord,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> dict[str, object]:
    session_sync = self._venue_execution.sync_session(
      handoff=handoff,
      order_ids=tuple(order.order_id for order in run.orders),
    )
    restore_view = GuardedLiveVenueSessionRestore(
      state="restored" if session_sync.state == "active" else session_sync.state,
      restored_at=session_sync.synced_at,
      source=session_sync.handoff.source,
      venue=session_sync.handoff.venue,
      symbol=session_sync.handoff.symbol,
      owner_run_id=session_sync.handoff.owner_run_id,
      owner_session_id=session_sync.handoff.owner_session_id,
      open_orders=session_sync.open_orders,
      synced_orders=session_sync.synced_orders,
      issues=session_sync.issues,
    )
    synced_count = self._apply_guarded_live_restored_session(
      run=run,
      session_restore=restore_view,
    )
    next_handoff = session_sync.handoff
    if synced_count > 0 or session_sync.issues or next_handoff.last_event_at != handoff.last_event_at:
      sync_time = session_sync.synced_at or self._clock()
      detail = (
        f"source={next_handoff.source}; transport={next_handoff.transport}; "
        f"state={next_handoff.state}; active_orders={next_handoff.active_order_count}; "
        f"cursor={next_handoff.cursor or 'n/a'}; supervision={next_handoff.supervision_state}; "
        f"order_book={next_handoff.order_book_state}; failovers={next_handoff.failover_count}; "
        f"coverage={','.join(next_handoff.coverage) or 'none'}; "
        f"continuation={next_handoff.channel_continuation_state}"
      )
      if (
        next_handoff.order_book_best_bid_price is not None
        or next_handoff.order_book_best_ask_price is not None
      ):
        detail += (
          f"; top_of_book={next_handoff.order_book_best_bid_price or 0.0:.8f}/"
          f"{next_handoff.order_book_best_ask_price or 0.0:.8f}"
        )
      if next_handoff.order_book_last_update_id is not None:
        detail += f"; depth_update_id={next_handoff.order_book_last_update_id}"
      if next_handoff.order_book_gap_count > 0:
        detail += f"; depth_gaps={next_handoff.order_book_gap_count}"
      if next_handoff.order_book_rebuild_count > 0:
        detail += f"; depth_rebuilds={next_handoff.order_book_rebuild_count}"
      if next_handoff.order_book_last_rebuilt_at is not None:
        detail += f"; last_depth_rebuild={next_handoff.order_book_last_rebuilt_at.isoformat()}"
      if session_sync.issues:
        detail += f"; issues={', '.join(session_sync.issues)}"
      run.notes.append(
        f"{sync_time.isoformat()} | guarded_live_venue_session_synced | {detail}"
      )
      self._append_guarded_live_audit_event(
        kind="guarded_live_venue_session_synced",
        actor="system",
        summary=f"Guarded-live venue session synced for {run.config.symbols[0]}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
      )
    return {
      "synced": synced_count,
      "handoff": next_handoff,
    }

  def _apply_guarded_live_synced_order_state(
    self,
    *,
    run: RunRecord,
    order: Order,
    synced_state: GuardedLiveVenueOrderResult,
  ) -> int:
    status_changed = False
    fill_recorded = False
    previous_status = order.status
    previous_filled_quantity = order.filled_quantity
    sync_time = synced_state.updated_at or synced_state.submitted_at or self._clock()
    order.last_synced_at = sync_time
    order.updated_at = sync_time
    if synced_state.average_fill_price is not None:
      order.average_fill_price = synced_state.average_fill_price

    total_fee = synced_state.fee_paid if synced_state.fee_paid is not None else order.fee_paid
    total_filled = synced_state.filled_amount
    if total_filled is None:
      if synced_state.status == OrderStatus.FILLED.value:
        total_filled = order.quantity
      elif synced_state.status == OrderStatus.PARTIALLY_FILLED.value:
        total_filled = order.filled_quantity
      else:
        total_filled = order.filled_quantity
    remaining_quantity = synced_state.remaining_amount
    if remaining_quantity is None:
      remaining_quantity = max(order.quantity - total_filled, 0.0)

    incremental_fill = max(total_filled - order.filled_quantity, 0.0)
    if incremental_fill > self._guarded_live_balance_tolerance:
      incremental_fee = max(total_fee - order.fee_paid, 0.0)
      self._materialize_guarded_live_fill_delta(
        run=run,
        order=order,
        fill_quantity=incremental_fill,
        fee_paid=incremental_fee,
        fill_price=synced_state.average_fill_price or order.average_fill_price or order.requested_price,
        fill_timestamp=sync_time,
      )
      fill_recorded = True

    order.fee_paid = total_fee
    order.filled_quantity = total_filled
    order.remaining_quantity = remaining_quantity
    mapped_status = self._map_guarded_live_order_status(
      synced_state.status,
      filled_quantity=total_filled,
      remaining_quantity=remaining_quantity,
    )
    if mapped_status != order.status:
      order.status = mapped_status
      status_changed = True
    if order.status == OrderStatus.FILLED and order.filled_at is None:
      order.filled_at = sync_time

    if status_changed or fill_recorded or synced_state.issues:
      transition_copy = (
        f"{previous_status.value}->{order.status.value}"
        if status_changed
        else f"{order.status.value}"
      )
      detail = (
        f"Order {order.order_id} synced as {transition_copy}. "
        f"filled {previous_filled_quantity:.8f}->{order.filled_quantity:.8f}, "
        f"remaining {order.remaining_quantity or 0.0:.8f}."
      )
      if synced_state.issues:
        detail += " Issues: " + ", ".join(synced_state.issues) + "."
      run.notes.append(f"{sync_time.isoformat()} | guarded_live_order_synced | {detail}")
      self._append_guarded_live_audit_event(
        kind="guarded_live_order_synced",
        actor="system",
        summary=f"Guarded-live order synced for {run.config.symbols[0]}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
      )
      return 1
    return 0

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
    cache = self._restore_state_cache(run)
    active_position = cache.position if cache.position is not None and cache.position.is_open else None
    if order.side == OrderSide.BUY:
      gross_cost = fill_quantity * fill_price
      next_cash = cache.cash - gross_cost - fee_paid
      if active_position is None:
        next_position = Position(
          instrument_id=order.instrument_id,
          quantity=fill_quantity,
          average_price=fill_price,
          opened_at=fill_timestamp,
          updated_at=fill_timestamp,
        )
      else:
        total_quantity = active_position.quantity + fill_quantity
        average_price = (
          (active_position.quantity * active_position.average_price) + (fill_quantity * fill_price)
        ) / total_quantity
        next_position = replace(
          active_position,
          quantity=total_quantity,
          average_price=average_price,
          updated_at=fill_timestamp,
        )
      cache.apply(cash=next_cash, position=next_position)
      run.positions[order.instrument_id] = next_position
    else:
      if active_position is None or not active_position.is_open:
        raise RuntimeError(f"guarded_live_sell_sync_without_position:{order.order_id}")
      sell_quantity = min(fill_quantity, active_position.quantity)
      gross_value = sell_quantity * fill_price
      proceeds = gross_value - fee_paid
      pnl = proceeds - (sell_quantity * active_position.average_price)
      remaining_quantity = max(active_position.quantity - sell_quantity, 0.0)
      next_position = replace(
        active_position,
        quantity=remaining_quantity,
        updated_at=fill_timestamp,
        realized_pnl=active_position.realized_pnl + pnl,
      )
      cache.apply(
        cash=cache.cash + proceeds,
        position=next_position if next_position.is_open else None,
      )
      run.positions[order.instrument_id] = next_position
      run.closed_trades.append(
        ClosedTrade(
          instrument_id=order.instrument_id,
          entry_price=active_position.average_price,
          exit_price=fill_price,
          quantity=sell_quantity,
          fee_paid=fee_paid,
          pnl=pnl,
          opened_at=active_position.opened_at or fill_timestamp,
          closed_at=fill_timestamp,
        )
      )

    run.fills.append(
      Fill(
        order_id=order.order_id,
        quantity=fill_quantity,
        price=fill_price,
        fee_paid=fee_paid,
        timestamp=fill_timestamp,
      )
    )
    run.equity_curve.append(
      build_equity_point(
        timestamp=fill_timestamp,
        cash=cache.cash,
        position=cache.position if cache.position and cache.position.is_open else None,
        market_price=fill_price,
      )
    )

  @staticmethod
  def _map_guarded_live_order_status(
    status: str,
    *,
    filled_quantity: float,
    remaining_quantity: float,
  ) -> OrderStatus:
    normalized = status.lower()
    if normalized in {"canceled", "cancelled", "expired"}:
      return OrderStatus.CANCELED
    if normalized == "rejected":
      return OrderStatus.REJECTED
    if normalized in {"filled", "closed"} or (filled_quantity > 0 and remaining_quantity <= 0):
      return OrderStatus.FILLED
    if normalized in {"partially_filled", "partial"} or (filled_quantity > 0 and remaining_quantity > 0):
      return OrderStatus.PARTIALLY_FILLED
    return OrderStatus.OPEN

  def _advance_guarded_live_worker_run(self, run: RunRecord) -> dict[str, int]:
    session = run.provenance.runtime_session
    if session is None:
      return {"ticks_processed": 0, "orders_submitted": 0}

    strategy = self._strategies.load(run.config.strategy_id)
    parameters = self._resolve_execution_parameters(run)
    candles = self._load_sandbox_worker_candles(run=run)
    if not candles:
      return {"ticks_processed": 0, "orders_submitted": 0}

    latest_seen_candle_at = candles[-1].timestamp
    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=latest_seen_candle_at,
    )
    if (
      session.last_processed_candle_at is not None
      and latest_seen_candle_at <= session.last_processed_candle_at
    ):
      return {"ticks_processed": 0, "orders_submitted": 0}

    enriched = strategy.build_feature_frame(candles_to_frame(candles), parameters)
    warmup = strategy.warmup_spec().required_bars
    if len(enriched) < max(warmup, 2):
      return {"ticks_processed": 0, "orders_submitted": 0}

    cache = self._restore_state_cache(run)
    latest_processed_candle_at = session.last_processed_candle_at
    processed_ticks = 0
    orders_submitted = 0
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
      orders_submitted += self._apply_guarded_live_decision(
        run=run,
        decision=decision,
        cache=cache,
        market_price=float(latest_row["close"]),
      )
      processed_ticks += 1
      latest_processed_candle_at = latest_timestamp

    if processed_ticks == 0:
      return {"ticks_processed": 0, "orders_submitted": 0}

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
    return {"ticks_processed": processed_ticks, "orders_submitted": orders_submitted}

  def _apply_guarded_live_decision(
    self,
    *,
    run: RunRecord,
    decision,
    cache: StateCache,
    market_price: float,
  ) -> int:
    reviewed = self._execution_engine.review_decision(decision)
    _, _, order, _, _ = apply_signal(
      run_id=run.config.run_id,
      instrument_id=cache.instrument_id,
      signal=reviewed.signal,
      execution=reviewed.execution,
      market_price=market_price,
      position=cache.position,
      cash=cache.cash,
      fee_rate=run.config.fee_rate,
      slippage_bps=run.config.slippage_bps,
    )

    submitted_orders = 0
    effective_price = market_price
    fill_materialized = False
    if order is not None:
      venue_result = self._submit_guarded_live_market_order(
        run=run,
        order=order,
        market_price=market_price,
      )
      order.order_id = venue_result.order_id
      order.created_at = venue_result.submitted_at
      order.updated_at = venue_result.updated_at or venue_result.submitted_at
      order.last_synced_at = venue_result.updated_at or venue_result.submitted_at
      order.status = self._map_guarded_live_order_status(
        venue_result.status,
        filled_quantity=venue_result.filled_amount or 0.0,
        remaining_quantity=venue_result.remaining_amount or 0.0,
      )
      if venue_result.average_fill_price is not None:
        order.average_fill_price = venue_result.average_fill_price
        effective_price = venue_result.average_fill_price
      order.fee_paid = venue_result.fee_paid or 0.0
      order.filled_quantity = venue_result.filled_amount or 0.0
      order.remaining_quantity = (
        venue_result.remaining_amount
        if venue_result.remaining_amount is not None
        else max(order.quantity - order.filled_quantity, 0.0)
      )
      if order.status == OrderStatus.FILLED:
        order.filled_at = venue_result.updated_at or venue_result.submitted_at
      run.orders.append(order)
      submitted_orders = 1
      if order.filled_quantity > self._guarded_live_balance_tolerance:
        self._materialize_guarded_live_fill_delta(
          run=run,
          order=order,
          fill_quantity=order.filled_quantity,
          fee_paid=order.fee_paid,
          fill_price=effective_price,
          fill_timestamp=order.filled_at or venue_result.submitted_at,
        )
        fill_materialized = True
      self._append_guarded_live_audit_event(
        kind="guarded_live_order_submitted",
        actor="system",
        summary=f"Guarded-live venue order submitted for {run.config.symbols[0]}.",
        detail=(
          f"{reviewed.signal.action.value} {order.quantity:.8f} {run.config.symbols[0]} "
          f"via {venue_result.order_id} ({order.status.value})."
        ),
        run_id=run.config.run_id,
        session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
      )

    cache = self._restore_state_cache(run)
    cache.mark_price(effective_price)
    if not fill_materialized:
      run.equity_curve.append(
        build_equity_point(
          timestamp=reviewed.signal.timestamp,
          cash=cache.cash,
          position=cache.position if cache.position and cache.position.is_open else None,
          market_price=effective_price,
        )
      )
    run.notes.append(
      f"{reviewed.context.timestamp.isoformat()} | {reviewed.signal.action.value} | {reviewed.rationale}"
    )
    return submitted_orders

  def _submit_guarded_live_market_order(
    self,
    *,
    run: RunRecord,
    order: Order,
    market_price: float,
  ) -> GuardedLiveVenueOrderResult:
    session = run.provenance.runtime_session
    if session is None:
      raise RuntimeError("guarded_live_runtime_session_missing")
    request = GuardedLiveVenueOrderRequest(
      run_id=run.config.run_id,
      session_id=session.session_id,
      venue=run.config.venue,
      symbol=run.config.symbols[0],
      side=order.side.value,
      amount=order.quantity,
      order_type=OrderType.MARKET.value,
      reference_price=market_price,
    )
    return self._venue_execution.submit_market_order(request)

  def _submit_guarded_live_limit_order(
    self,
    *,
    run: RunRecord,
    order: Order,
    limit_price: float,
  ) -> GuardedLiveVenueOrderResult:
    session = run.provenance.runtime_session
    if session is None:
      raise RuntimeError("guarded_live_runtime_session_missing")
    request = GuardedLiveVenueOrderRequest(
      run_id=run.config.run_id,
      session_id=session.session_id,
      venue=run.config.venue,
      symbol=run.config.symbols[0],
      side=order.side.value,
      amount=order.quantity,
      order_type=OrderType.LIMIT.value,
      reference_price=limit_price,
    )
    return self._venue_execution.submit_limit_order(request)

  def _guarded_live_delivery_targets(self) -> tuple[str, ...]:
    return (
      "operator_visibility",
      "guarded_live_status",
      "control_room",
      *self._operator_alert_delivery.list_targets(),
    )

  def _build_guarded_live_operator_alerts(
    self,
    *,
    state: GuardedLiveState,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    alerts: list[OperatorAlert] = []
    delivery_targets = self._guarded_live_delivery_targets()
    live_runs = self._runs.list_runs(mode=RunMode.LIVE.value)
    live_context_active = bool(live_runs) or state.ownership.state in {"owned", "orphaned"}

    alerts.extend(
      self._build_guarded_live_market_data_alerts(
        live_runs=live_runs,
        current_time=current_time,
      )
    )

    if state.kill_switch.state == "engaged":
      detected_at = state.kill_switch.last_engaged_at or state.kill_switch.updated_at
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:kill-switch",
          severity="warning",
          category="kill_switch",
          summary="Guarded-live kill switch is engaged.",
          detail=(
            f"{state.kill_switch.reason} Updated by {state.kill_switch.updated_by} at "
            f"{state.kill_switch.updated_at.isoformat()}."
          ),
          detected_at=detected_at,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.reconciliation.state == "issues_detected":
      finding_copy = "; ".join(finding.summary for finding in state.reconciliation.findings[:3])
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:reconciliation",
          severity=(
            "critical"
            if any(finding.severity == "critical" for finding in state.reconciliation.findings)
            else "warning"
          ),
          category="reconciliation",
          summary="Guarded-live reconciliation has unresolved findings.",
          detail=(
            f"{state.reconciliation.summary} "
            f"{finding_copy if finding_copy else 'Review the guarded-live venue snapshot and internal exposure state.'}"
          ),
          detected_at=state.reconciliation.checked_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.recovery.state == "failed":
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:recovery-failed",
          severity="critical",
          category="runtime_recovery",
          summary="Guarded-live runtime recovery failed.",
          detail=(
            f"{state.recovery.summary} Issues: "
            f"{', '.join(state.recovery.issues) if state.recovery.issues else 'none'}."
          ),
          detected_at=state.recovery.recovered_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.ownership.state == "orphaned":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:ownership:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_ownership",
          summary="Guarded-live session ownership is orphaned.",
          detail=(
            f"Run {state.ownership.owner_run_id or 'n/a'} still owns the guarded-live session, "
            f"but the live worker is not healthy. Last reason: {state.ownership.last_reason or 'n/a'}."
          ),
          detected_at=(
            state.ownership.last_heartbeat_at
            or state.ownership.last_resumed_at
            or state.ownership.claimed_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if live_context_active and state.session_handoff.state == "unavailable":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-transport:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_transport",
          summary="Guarded-live venue session transport is unavailable.",
          detail=(
            "Venue-native session supervision could not be maintained. Issues: "
            f"{', '.join(state.session_handoff.issues) if state.session_handoff.issues else 'none'}."
          ),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
    elif live_context_active and state.session_handoff.issues:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-issues:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="session_transport",
          summary="Guarded-live venue session requires operator review.",
          detail=", ".join(state.session_handoff.issues),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    order_book_issue_copy: list[str] = []
    if state.session_handoff.order_book_state == "unavailable":
      order_book_issue_copy.append("venue order-book supervision is unavailable")
    if state.order_book.issues:
      order_book_issue_copy.extend(state.order_book.issues)
    if live_context_active and order_book_issue_copy:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:order-book:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="order_book",
          summary="Guarded-live order-book supervision requires review.",
          detail="; ".join(order_book_issue_copy),
          detected_at=(
            state.order_book.synced_at
            or state.session_handoff.last_sync_at
            or state.session_handoff.handed_off_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    alerts.extend(
      self._build_guarded_live_channel_operator_alerts(
        state=state,
        current_time=current_time,
        live_context_active=live_context_active,
        delivery_targets=delivery_targets,
      )
    )

    for run in live_runs:
      alerts.extend(self._build_live_operator_alerts_for_run(run=run, current_time=current_time))

    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    return alerts

  def _build_guarded_live_market_data_alerts(
    self,
    *,
    live_runs: list[RunRecord],
    current_time: datetime,
  ) -> list[OperatorAlert]:
    alerts: list[OperatorAlert] = []
    delivery_targets = self._guarded_live_delivery_targets()
    live_symbols = {
      symbol
      for run in live_runs
      for symbol in run.config.symbols
    }
    for timeframe in self._resolve_guarded_live_market_data_timeframes(live_runs=live_runs):
      try:
        status = self._market_data.get_status(timeframe)
      except Exception as exc:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy could not be evaluated for {timeframe}.",
            detail=f"Market-data status query failed: {exc}.",
            detected_at=current_time,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
        continue
      if status.provider == "seeded":
        continue

      relevant_instruments = [
        instrument
        for instrument in status.instruments
        if not live_symbols or self._symbol_from_instrument_id(instrument.instrument_id) in live_symbols
      ]
      if live_symbols and not relevant_instruments:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy is uncovered for {timeframe}.",
            detail=(
              "No tracked market-data status covered the active live symbol set: "
              f"{', '.join(sorted(live_symbols))}."
            ),
            detected_at=current_time,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
        continue

      critical_details: list[str] = []
      quality_details: list[str] = []
      continuity_details: list[str] = []
      venue_details: list[str] = []
      quality_has_critical = False
      continuity_has_critical = False
      venue_has_critical = False
      detected_candidates: list[datetime] = []
      for instrument in relevant_instruments:
        symbol = self._symbol_from_instrument_id(instrument.instrument_id)
        if instrument.last_sync_at is not None:
          detected_candidates.append(instrument.last_sync_at)
        if instrument.last_timestamp is not None:
          detected_candidates.append(instrument.last_timestamp)
        if instrument.recent_failures:
          detected_candidates.extend(failure.failed_at for failure in instrument.recent_failures)

        if instrument.sync_status == "error":
          critical_details.append(f"{symbol} last sync failed.")
        elif instrument.sync_status == "empty":
          critical_details.append(f"{symbol} has no persisted candles for {timeframe}.")
        elif instrument.sync_status == "stale":
          lag_detail = (
            f" lagged {instrument.lag_seconds}s"
            if instrument.lag_seconds is not None
            else " breached the freshness window"
          )
          critical_details.append(f"{symbol}{lag_detail}.")

        missing_candles = instrument.backfill_contiguous_missing_candles
        if missing_candles is None and instrument.backfill_gap_windows:
          missing_candles = sum(window.missing_candles for window in instrument.backfill_gap_windows)
        if missing_candles and missing_candles > 0:
          continuity_details.append(
            f"{symbol} has {missing_candles} missing candle(s) across "
            f"{len(instrument.backfill_gap_windows)} gap window(s)."
          )
        if (
          instrument.backfill_target_candles is not None
          and instrument.backfill_completion_ratio is not None
          and instrument.backfill_complete is False
        ):
          quality_details.append(
            f"{symbol} backfill target covers {instrument.backfill_completion_ratio * 100:.2f}% "
            f"of {instrument.backfill_target_candles} candles."
          )
          if instrument.backfill_completion_ratio < self._guarded_live_market_data_backfill_completion_floor:
            quality_has_critical = True
        if (
          instrument.backfill_contiguous_completion_ratio is not None
          and instrument.backfill_contiguous_complete is False
        ):
          continuity_details.append(
            f"{symbol} contiguous backfill quality is "
            f"{instrument.backfill_contiguous_completion_ratio * 100:.2f}%."
          )
          if (
            instrument.backfill_contiguous_completion_ratio
            < self._guarded_live_market_data_contiguous_completion_floor
          ):
            continuity_has_critical = True
        if instrument.failure_count_24h > 0:
          venue_details.append(
            f"{symbol} recorded {instrument.failure_count_24h} sync failure(s) in the last 24h."
          )
          if instrument.failure_count_24h >= self._guarded_live_market_data_failure_burst_threshold:
            venue_has_critical = True
        elif instrument.recent_failures:
          latest_failure = instrument.recent_failures[0]
          venue_details.append(
            f"{symbol} last failure was {latest_failure.operation}: {latest_failure.error}."
          )
        venue_semantics = self._extract_market_data_venue_semantics(
          venue=status.venue,
          issues=instrument.issues,
        )
        if venue_semantics:
          venue_details.append(
            f"{symbol} venue semantics: {', '.join(venue_semantics)}."
          )
          if any(
            semantic in {"authentication fault", "symbol unavailable"}
            for semantic in venue_semantics
          ):
            venue_has_critical = True

      detail_copy = list(dict.fromkeys(critical_details))
      detected_at = max(detected_candidates) if detected_candidates else current_time
      if detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical" if critical_details else "warning",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy is degraded for {timeframe}.",
            detail=(
              " ".join(detail_copy[:3])
              + (f" Additional issues: {len(detail_copy) - 3}." if len(detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      quality_detail_copy = list(dict.fromkeys(quality_details))
      if quality_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-quality:{status.venue}:{timeframe}",
            severity="critical" if quality_has_critical else "warning",
            category="market_data_quality",
            summary=f"Guarded-live market-data quality policy is degraded for {status.venue} {timeframe}.",
            detail=(
              " ".join(quality_detail_copy[:3])
              + (f" Additional issues: {len(quality_detail_copy) - 3}." if len(quality_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      continuity_detail_copy = list(dict.fromkeys(continuity_details))
      if continuity_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-continuity:{status.venue}:{timeframe}",
            severity="critical" if continuity_has_critical else "warning",
            category="market_data_candle_continuity",
            summary=f"Guarded-live multi-candle continuity requires review for {status.venue} {timeframe}.",
            detail=(
              " ".join(continuity_detail_copy[:3])
              + (f" Additional issues: {len(continuity_detail_copy) - 3}." if len(continuity_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      venue_detail_copy = list(dict.fromkeys(venue_details))
      if venue_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-venue:{status.venue}:{timeframe}",
            severity="critical" if venue_has_critical else "warning",
            category="market_data_venue",
            summary=f"Guarded-live market-data venue semantics require review for {status.venue} {timeframe}.",
            detail=(
              " ".join(venue_detail_copy[:3])
              + (f" Additional issues: {len(venue_detail_copy) - 3}." if len(venue_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
    return alerts

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

  def _build_guarded_live_channel_operator_alerts(
    self,
    *,
    state: GuardedLiveState,
    current_time: datetime,
    live_context_active: bool,
    delivery_targets: tuple[str, ...],
  ) -> list[OperatorAlert]:
    if not live_context_active:
      return []

    handoff = state.session_handoff
    if handoff.state in {"inactive", "released"}:
      return []

    run_id = state.ownership.owner_run_id or handoff.owner_run_id
    session_id = state.ownership.owner_session_id or handoff.owner_session_id
    alerts: list[OperatorAlert] = []

    consistency_details, consistency_detected_at, consistency_has_critical = (
      self._collect_guarded_live_channel_consistency_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if consistency_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-channel-consistency:{run_id or 'unknown'}",
          severity="critical" if consistency_has_critical else "warning",
          category="market_data_channel_consistency",
          summary=(
            f"Guarded-live market-data channel consistency is degraded for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(consistency_details),
          detected_at=consistency_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_integrity_details, ladder_integrity_detected_at, ladder_integrity_has_critical = (
      self._collect_guarded_live_ladder_integrity_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_integrity_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-integrity:{run_id or 'unknown'}",
          severity="critical" if ladder_integrity_has_critical else "warning",
          category="market_data_ladder_integrity",
          summary=(
            f"Guarded-live exchange ladder integrity requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_integrity_details),
          detected_at=ladder_integrity_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    venue_ladder_integrity_details, venue_ladder_integrity_detected_at, venue_ladder_integrity_has_critical = (
      self._collect_guarded_live_venue_ladder_integrity_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if venue_ladder_integrity_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-venue-ladder-integrity:{run_id or 'unknown'}",
          severity="critical" if venue_ladder_integrity_has_critical else "warning",
          category="market_data_venue_ladder_integrity",
          summary=(
            f"Guarded-live venue-native ladder integrity requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(venue_ladder_integrity_details),
          detected_at=venue_ladder_integrity_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_bridge_details, ladder_bridge_detected_at, ladder_bridge_has_critical = (
      self._collect_guarded_live_ladder_bridge_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_bridge_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-bridge:{run_id or 'unknown'}",
          severity="critical" if ladder_bridge_has_critical else "warning",
          category="market_data_ladder_bridge_integrity",
          summary=(
            f"Guarded-live ladder bridge rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_bridge_details),
          detected_at=ladder_bridge_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_sequence_details, ladder_sequence_detected_at, ladder_sequence_has_critical = (
      self._collect_guarded_live_ladder_sequence_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_sequence_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-sequence:{run_id or 'unknown'}",
          severity="critical" if ladder_sequence_has_critical else "warning",
          category="market_data_ladder_sequence_integrity",
          summary=(
            f"Guarded-live ladder sequence rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_sequence_details),
          detected_at=ladder_sequence_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_snapshot_refresh_details, ladder_snapshot_refresh_detected_at, ladder_snapshot_refresh_has_critical = (
      self._collect_guarded_live_ladder_snapshot_refresh_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_snapshot_refresh_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-snapshot-refresh:{run_id or 'unknown'}",
          severity="critical" if ladder_snapshot_refresh_has_critical else "warning",
          category="market_data_ladder_snapshot_refresh",
          summary=(
            f"Guarded-live ladder snapshot refresh rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_snapshot_refresh_details),
          detected_at=ladder_snapshot_refresh_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    restore_details, restore_detected_at, restore_has_critical = (
      self._collect_guarded_live_channel_restore_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if restore_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-channel-restore:{run_id or 'unknown'}",
          severity="critical" if restore_has_critical else "warning",
          category="market_data_channel_restore",
          summary=(
            f"Guarded-live market-data channel restore requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(restore_details),
          detected_at=restore_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    book_details, book_detected_at, book_has_critical = self._collect_guarded_live_book_consistency_findings(
      handoff=handoff,
      current_time=current_time,
    )
    if book_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-book-consistency:{run_id or 'unknown'}",
          severity="critical" if book_has_critical else "warning",
          category="market_data_book_consistency",
          summary=(
            f"Guarded-live book consistency requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(book_details),
          detected_at=book_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    kline_details, kline_detected_at, kline_has_critical = self._collect_guarded_live_kline_consistency_findings(
      handoff=handoff,
      current_time=current_time,
    )
    if kline_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-kline-consistency:{run_id or 'unknown'}",
          severity="critical" if kline_has_critical else "warning",
          category="market_data_kline_consistency",
          summary=(
            f"Guarded-live kline consistency requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(kline_details),
          detected_at=kline_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    depth_ladder_details, depth_ladder_detected_at, depth_ladder_has_critical = (
      self._collect_guarded_live_depth_ladder_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if depth_ladder_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-depth-ladder:{run_id or 'unknown'}",
          severity="critical" if depth_ladder_has_critical else "warning",
          category="market_data_depth_ladder",
          summary=(
            f"Guarded-live depth ladder semantics require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(depth_ladder_details),
          detected_at=depth_ladder_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    candle_sequence_details, candle_sequence_detected_at, candle_sequence_has_critical = (
      self._collect_guarded_live_candle_sequence_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if candle_sequence_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-candle-sequence:{run_id or 'unknown'}",
          severity="critical" if candle_sequence_has_critical else "warning",
          category="market_data_candle_sequence",
          summary=(
            f"Guarded-live candle sequencing requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(candle_sequence_details),
          detected_at=candle_sequence_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
    return alerts

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

  def _collect_guarded_live_ladder_integrity_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    detected_at = handoff.order_book_last_rebuilt_at or handoff.last_depth_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_gap_count > 0:
      gap_detail = f"{venue} ladder integrity recorded {handoff.order_book_gap_count} depth gap(s)."
      if handoff.order_book_last_update_id is not None:
        gap_detail += f" Last update id: {handoff.order_book_last_update_id}."
      add_finding(gap_detail, critical=True)

    if handoff.order_book_rebuild_count > 0:
      add_finding(
        f"{venue} ladder integrity required {handoff.order_book_rebuild_count} snapshot rebuild(s).",
      )

    for issue_detail in self._extract_guarded_live_ladder_integrity_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_venue_ladder_integrity_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.order_book_last_rebuilt_at or handoff.last_depth_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_state == "rebuild_failed":
      add_finding(
        f"{handoff.venue or 'venue'} ladder snapshot rebuild is currently failing.",
        critical=True,
      )

    for issue_detail in self._extract_guarded_live_venue_ladder_integrity_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_ladder_bridge_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_bridge_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_ladder_sequence_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_sequence_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_ladder_snapshot_refresh_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_snapshot_refresh_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_channel_restore_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    restore_anchor = handoff.channel_last_restored_at or handoff.last_sync_at or handoff.handed_off_at or current_time
    has_critical = False

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.channel_restore_state == "partial":
      add_finding(
        "market-channel restore completed only partially.",
        detected_at=restore_anchor,
      )
    elif handoff.channel_restore_state == "unavailable":
      add_finding(
        "market-channel restore is unavailable.",
        detected_at=restore_anchor,
        critical=True,
      )

    if handoff.channel_continuation_state == "partial":
      add_finding(
        "market-channel continuation is only partially supervised.",
        detected_at=handoff.channel_last_continued_at or restore_anchor,
      )
    elif handoff.channel_continuation_state == "unavailable":
      add_finding(
        "market-channel continuation is unavailable.",
        detected_at=handoff.channel_last_continued_at or restore_anchor,
        critical=True,
      )

    for issue_detail in self._extract_guarded_live_channel_restore_semantics(issues=handoff.issues):
      add_finding(
        issue_detail,
        detected_at=restore_anchor,
        critical=True,
      )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical

  def _collect_guarded_live_book_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.book_ticker_snapshot
    if (
      handoff.order_book_state in {"inactive", "released"}
      and snapshot is None
    ):
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    best_bid = handoff.order_book_best_bid_price
    best_ask = handoff.order_book_best_ask_price
    if best_bid is not None and best_ask is not None and best_bid > (best_ask + tolerance):
      add_finding(
        f"{venue} local order book is crossed: best bid {best_bid:.8f} is above best ask {best_ask:.8f}.",
        detected_at=handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at,
        critical=True,
      )

    if snapshot is not None:
      if (
        snapshot.bid_price is not None
        and snapshot.ask_price is not None
        and snapshot.bid_price > (snapshot.ask_price + tolerance)
      ):
        add_finding(
          f"{venue} book-ticker quote is crossed: bid {snapshot.bid_price:.8f} is above ask {snapshot.ask_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        best_bid is not None
        and snapshot.ask_price is not None
        and best_bid > (snapshot.ask_price + tolerance)
      ):
        add_finding(
          f"{venue} local best bid {best_bid:.8f} is above book-ticker ask {snapshot.ask_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        snapshot.bid_price is not None
        and best_ask is not None
        and snapshot.bid_price > (best_ask + tolerance)
      ):
        add_finding(
          f"{venue} book-ticker bid {snapshot.bid_price:.8f} is above local best ask {best_ask:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical

  def _collect_guarded_live_kline_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.kline_snapshot
    if snapshot is None:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if (
      snapshot.timeframe is not None
      and handoff.timeframe is not None
      and snapshot.timeframe != handoff.timeframe
    ):
      add_finding(
        f"{venue} kline timeframe {snapshot.timeframe} does not match the guarded-live timeframe {handoff.timeframe}.",
        detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
      )

    if (
      snapshot.open_at is not None
      and snapshot.close_at is not None
      and snapshot.close_at <= snapshot.open_at
    ):
      add_finding(
        f"{venue} kline closes at {snapshot.close_at.isoformat()} before or at its open {snapshot.open_at.isoformat()}.",
        detected_at=snapshot.event_at or snapshot.close_at or handoff.last_kline_event_at,
        critical=True,
      )

    if (
      snapshot.high_price is not None
      and snapshot.low_price is not None
      and snapshot.high_price + tolerance < snapshot.low_price
    ):
      add_finding(
        f"{venue} kline high {snapshot.high_price:.8f} is below low {snapshot.low_price:.8f}.",
        detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
        critical=True,
      )
    elif snapshot.high_price is not None and snapshot.low_price is not None:
      if (
        snapshot.open_price is not None
        and (
          snapshot.open_price > snapshot.high_price + tolerance
          or snapshot.open_price + tolerance < snapshot.low_price
        )
      ):
        add_finding(
          f"{venue} kline open {snapshot.open_price:.8f} falls outside the high/low range "
          f"{snapshot.low_price:.8f}-{snapshot.high_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        snapshot.close_price is not None
        and (
          snapshot.close_price > snapshot.high_price + tolerance
          or snapshot.close_price + tolerance < snapshot.low_price
        )
      ):
        add_finding(
          f"{venue} kline close {snapshot.close_price:.8f} falls outside the high/low range "
          f"{snapshot.low_price:.8f}-{snapshot.high_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
          critical=True,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical

  def _collect_guarded_live_depth_ladder_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    if not handoff.order_book_bids and not handoff.order_book_asks:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_bid_level_count and handoff.order_book_bid_level_count != len(handoff.order_book_bids):
      add_finding(
        f"{venue} bid ladder count {len(handoff.order_book_bids)} does not match stored bid level count "
        f"{handoff.order_book_bid_level_count}.",
        critical=True,
      )
    if handoff.order_book_ask_level_count and handoff.order_book_ask_level_count != len(handoff.order_book_asks):
      add_finding(
        f"{venue} ask ladder count {len(handoff.order_book_asks)} does not match stored ask level count "
        f"{handoff.order_book_ask_level_count}.",
        critical=True,
      )

    if handoff.order_book_bids and (
      handoff.order_book_best_bid_price is not None or handoff.order_book_best_bid_quantity is not None
    ):
      head = handoff.order_book_bids[0]
      if (
        (handoff.order_book_best_bid_price is not None and abs(head.price - handoff.order_book_best_bid_price) > tolerance)
        or (
          handoff.order_book_best_bid_quantity is not None
          and abs(head.quantity - handoff.order_book_best_bid_quantity) > tolerance
        )
      ):
        add_finding(
          f"{venue} best bid ladder head {head.price:.8f}/{head.quantity:.8f} does not match stored "
          f"best bid {handoff.order_book_best_bid_price or 0.0:.8f}/"
          f"{handoff.order_book_best_bid_quantity or 0.0:.8f}.",
          critical=True,
        )
    if handoff.order_book_asks and (
      handoff.order_book_best_ask_price is not None or handoff.order_book_best_ask_quantity is not None
    ):
      head = handoff.order_book_asks[0]
      if (
        (handoff.order_book_best_ask_price is not None and abs(head.price - handoff.order_book_best_ask_price) > tolerance)
        or (
          handoff.order_book_best_ask_quantity is not None
          and abs(head.quantity - handoff.order_book_best_ask_quantity) > tolerance
        )
      ):
        add_finding(
          f"{venue} best ask ladder head {head.price:.8f}/{head.quantity:.8f} does not match stored "
          f"best ask {handoff.order_book_best_ask_price or 0.0:.8f}/"
          f"{handoff.order_book_best_ask_quantity or 0.0:.8f}.",
          critical=True,
        )

    previous_price: float | None = None
    for index, level in enumerate(handoff.order_book_bids, start=1):
      if level.quantity <= tolerance:
        add_finding(
          f"{venue} bid ladder level {index} has non-positive quantity {level.quantity:.8f}.",
          critical=True,
        )
      if previous_price is not None and level.price >= (previous_price - tolerance):
        add_finding(
          f"{venue} bid ladder is not strictly descending at level {index} "
          f"({level.price:.8f} after {previous_price:.8f}).",
          critical=True,
        )
      previous_price = level.price

    previous_price = None
    for index, level in enumerate(handoff.order_book_asks, start=1):
      if level.quantity <= tolerance:
        add_finding(
          f"{venue} ask ladder level {index} has non-positive quantity {level.quantity:.8f}.",
          critical=True,
        )
      if previous_price is not None and level.price <= (previous_price + tolerance):
        add_finding(
          f"{venue} ask ladder is not strictly ascending at level {index} "
          f"({level.price:.8f} after {previous_price:.8f}).",
          critical=True,
        )
      previous_price = level.price

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_candle_sequence_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.kline_snapshot
    if snapshot is None:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    timeframe = snapshot.timeframe or handoff.timeframe
    timeframe_delta = self._guarded_live_timeframe_to_timedelta(timeframe)
    detected_at = snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if timeframe_delta is not None and snapshot.open_at is not None:
      if not self._datetime_is_aligned_to_interval(snapshot.open_at, timeframe_delta):
        add_finding(
          f"{venue} kline open {snapshot.open_at.isoformat()} is not aligned to the {timeframe} timeframe boundary."
        )

    if timeframe_delta is not None and snapshot.open_at is not None and snapshot.close_at is not None:
      expected_close_at = snapshot.open_at + timeframe_delta
      if snapshot.close_at != expected_close_at:
        add_finding(
          f"{venue} kline close {snapshot.close_at.isoformat()} does not match the expected {timeframe} boundary close "
          f"{expected_close_at.isoformat()}.",
          critical=True,
        )

    if snapshot.closed and snapshot.event_at is not None and snapshot.close_at is not None and snapshot.event_at < snapshot.close_at:
      add_finding(
        f"{venue} closed kline event arrived at {snapshot.event_at.isoformat()} before the candle close "
        f"{snapshot.close_at.isoformat()}.",
        critical=True,
      )

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  @staticmethod
  def _guarded_live_timeframe_to_timedelta(timeframe: str | None) -> timedelta | None:
    if not timeframe or len(timeframe) < 2:
      return None
    unit = timeframe[-1]
    try:
      amount = int(timeframe[:-1])
    except ValueError:
      return None
    if amount <= 0:
      return None
    return {
      "m": timedelta(minutes=amount),
      "h": timedelta(hours=amount),
      "d": timedelta(days=amount),
      "w": timedelta(weeks=amount),
    }.get(unit)

  @staticmethod
  def _datetime_is_aligned_to_interval(value: datetime, interval: timedelta) -> bool:
    if interval.total_seconds() <= 0:
      return False
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    return ((value - epoch).total_seconds() % interval.total_seconds()) == 0

  @staticmethod
  def _resolve_guarded_live_market_channel_activity(
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> tuple[tuple[str, datetime | None, bool], ...]:
    coverage = set(handoff.coverage)
    activity: list[tuple[str, datetime | None, bool]] = []
    if "trade_ticks" in coverage:
      activity.append(("trade ticks", handoff.last_trade_event_at, False))
    if "aggregate_trade_ticks" in coverage:
      activity.append(("aggregate-trade ticks", handoff.last_aggregate_trade_event_at, False))
    if "book_ticker" in coverage:
      activity.append(("book-ticker updates", handoff.last_book_ticker_event_at, False))
    if "mini_ticker" in coverage:
      activity.append(("mini-ticker updates", handoff.last_mini_ticker_event_at, False))
    if "depth_updates" in coverage or "order_book_lifecycle" in coverage:
      activity.append(("depth/order-book updates", handoff.last_depth_event_at, True))
    if "kline_candles" in coverage:
      activity.append(("kline candles", handoff.last_kline_event_at, False))
    return tuple(activity)

  @staticmethod
  def _extract_guarded_live_channel_gap_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_gap_detected:" not in issue:
        continue
      venue, payload = issue.split("_order_book_gap_detected:", 1)
      previous_update_id, _, next_update_id = payload.partition(":")
      if previous_update_id and next_update_id:
        findings.append(
          f"{venue} depth stream gap detected between update ids {previous_update_id} and {next_update_id}."
        )
      else:
        findings.append(f"{venue} depth stream gap detected.")
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_integrity_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    return TradingApplication._extract_guarded_live_channel_gap_semantics(issues=issues)

  @staticmethod
  def _extract_guarded_live_venue_ladder_integrity_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_snapshot_failed:" in issue:
        venue, payload = issue.split("_order_book_snapshot_failed:", 1)
        reason, _, detail = payload.partition(":")
        reason_label = reason.replace("_", " ") if reason else "unknown"
        if detail:
          findings.append(f"{venue} ladder snapshot rebuild failed during {reason_label}: {detail}.")
        else:
          findings.append(f"{venue} ladder snapshot rebuild failed during {reason_label}.")
        continue
      if "_order_book_snapshot_missing_side:" in issue:
        venue, payload = issue.split("_order_book_snapshot_missing_side:", 1)
        side = payload.replace("_", " ") if payload else "unknown side"
        findings.append(f"{venue} ladder snapshot returned no {side} levels.")
        continue
      if "_order_book_snapshot_crossed:" in issue:
        venue, payload = issue.split("_order_book_snapshot_crossed:", 1)
        bid, _, ask = payload.partition(":")
        if bid and ask:
          try:
            bid_value = f"{float(bid):.8f}"
            ask_value = f"{float(ask):.8f}"
          except ValueError:
            bid_value = bid
            ask_value = ask
          findings.append(
            f"{venue} ladder snapshot is crossed: best bid {bid_value} is above best ask {ask_value}."
          )
        else:
          findings.append(f"{venue} ladder snapshot is crossed.")
        continue
      if "_order_book_snapshot_non_monotonic:" not in issue:
        continue
      venue, payload = issue.split("_order_book_snapshot_non_monotonic:", 1)
      side, _, remainder = payload.partition(":")
      index, _, price_payload = remainder.partition(":")
      price, _, previous_price = price_payload.partition(":")
      side_label = side[:-1] if side.endswith("s") else side
      ordering = "descending" if side == "bids" else "ascending"
      if index and price and previous_price:
        try:
          price_value = f"{float(price):.8f}"
          previous_price_value = f"{float(previous_price):.8f}"
        except ValueError:
          price_value = price
          previous_price_value = previous_price
        findings.append(
          f"{venue} {side_label} ladder snapshot is not strictly {ordering} at level {index} "
          f"({price_value} after {previous_price_value})."
        )
      else:
        findings.append(f"{venue} {side_label} ladder snapshot is not strictly {ordering}.")
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_bridge_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_bridge_previous_mismatch:" in issue:
        venue, payload = issue.split("_order_book_bridge_previous_mismatch:", 1)
        expected_previous, _, actual_previous = payload.partition(":")
        findings.append(
          f"{venue} depth bridge expected previous update id {expected_previous or 'unknown'} "
          f"but received {actual_previous or 'unknown'}."
        )
        continue
      if "_order_book_bridge_range_mismatch:" in issue:
        venue, payload = issue.split("_order_book_bridge_range_mismatch:", 1)
        expected_next, _, remainder = payload.partition(":")
        first_update_id, _, last_update_id = remainder.partition(":")
        findings.append(
          f"{venue} depth bridge range {first_update_id or 'unknown'}-{last_update_id or 'unknown'} "
          f"does not cover expected next update id {expected_next or 'unknown'}."
        )
        continue
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_sequence_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_sequence_mismatch:" not in issue:
        continue
      venue, payload = issue.split("_order_book_sequence_mismatch:", 1)
      expected_previous, _, remainder = payload.partition(":")
      actual_previous, _, current_update_id = remainder.partition(":")
      findings.append(
        f"{venue} ladder sequence expected previous update id {expected_previous or 'unknown'} "
        f"but received {actual_previous or 'unknown'} before update {current_update_id or 'unknown'}."
      )
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_snapshot_refresh_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_snapshot_refresh:" not in issue:
        continue
      venue, payload = issue.split("_order_book_snapshot_refresh:", 1)
      previous_update_id, _, next_update_id = payload.partition(":")
      findings.append(
        f"{venue} ladder snapshot refresh replaced update id {previous_update_id or 'unknown'} "
        f"with {next_update_id or 'unknown'}."
      )
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_channel_restore_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_market_channel_restore_failed:" not in issue:
        continue
      venue, payload = issue.split("_market_channel_restore_failed:", 1)
      channel, _, remainder = payload.partition(":")
      reason = remainder.replace("_", " ") if remainder else "unknown"
      channel_label = channel.replace("_", " ") if channel else "market channel"
      findings.append(
        f"{venue} {channel_label} restore failed: {reason}."
      )
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _summarize_guarded_live_issue_copy(details: list[str]) -> str:
    unique_details = list(dict.fromkeys(details))
    return " ".join(unique_details[:3]) + (
      f" Additional issues: {len(unique_details) - 3}."
      if len(unique_details) > 3
      else ""
    )

  def _build_guarded_live_incident_events(
    self,
    *,
    previous_history: tuple[OperatorAlert, ...],
    merged_history: tuple[OperatorAlert, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, ...]:
    previous_by_id = {alert.alert_id: alert for alert in previous_history}
    incident_events: list[OperatorIncidentEvent] = []

    for alert in merged_history:
      policy = self._resolve_incident_paging_policy(alert=alert)
      remediation = self._build_incident_remediation(alert=alert, policy=policy)
      previous = previous_by_id.get(alert.alert_id)
      if alert.status == "active" and (previous is None or previous.status != "active"):
        incident_events.append(
          OperatorIncidentEvent(
            event_id=f"incident_opened:{alert.alert_id}:{alert.detected_at.isoformat()}",
            alert_id=alert.alert_id,
            timestamp=alert.detected_at,
            kind="incident_opened",
            severity=alert.severity,
            summary=alert.summary,
            detail=alert.detail,
            run_id=alert.run_id,
            session_id=alert.session_id,
            source=alert.source,
            paging_policy_id=policy.policy_id,
            paging_provider=policy.provider,
            delivery_targets=policy.initial_targets,
            escalation_targets=policy.escalation_targets,
            acknowledgment_state="unacknowledged",
            escalation_state=(
              "pending" if policy.escalation_targets else "not_configured"
            ),
            next_escalation_at=(
              alert.detected_at + timedelta(seconds=self._operator_alert_incident_ack_timeout_seconds)
              if policy.escalation_targets
              else None
            ),
            paging_status="pending" if policy.provider else "not_configured",
            provider_workflow_state="idle" if policy.provider else "not_configured",
            remediation=remediation,
          )
        )
        continue
      if alert.status == "resolved" and previous is not None and previous.status == "active":
        resolved_at = alert.resolved_at or current_time
        incident_events.append(
          OperatorIncidentEvent(
            event_id=f"incident_resolved:{alert.alert_id}:{resolved_at.isoformat()}",
            alert_id=alert.alert_id,
            timestamp=resolved_at,
            kind="incident_resolved",
            severity=alert.severity,
            summary=f"Resolved: {alert.summary}",
            detail=alert.detail,
            run_id=alert.run_id,
            session_id=alert.session_id,
            source=alert.source,
            paging_policy_id=policy.policy_id,
            paging_provider=policy.provider,
            delivery_targets=policy.resolution_targets,
            acknowledgment_state="not_applicable",
            escalation_state="not_applicable",
            paging_status="pending" if policy.provider else "not_configured",
            remediation=remediation,
          )
        )

    incident_events.sort(key=lambda event: event.timestamp, reverse=True)
    return tuple(incident_events)

  @staticmethod
  def _normalize_targets(targets: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(targets))

  @staticmethod
  def _normalize_paging_provider(provider: str | None) -> str | None:
    if provider is None:
      return None
    normalized = provider.strip().lower().replace("-", "_")
    return normalized or None

  @staticmethod
  def _alert_supports_remediation(*, alert: OperatorAlert) -> bool:
    return alert.source == "guarded_live" and alert.category.startswith("market_data_")

  @staticmethod
  def _market_data_remediation_plan(*, category: str) -> _IncidentRemediationPlan:
    if category == "market_data_freshness":
      return _IncidentRemediationPlan(
        kind="recent_sync",
        owner="provider",
        summary="Refresh the live timeframe sync window and verify freshness thresholds.",
        detail=(
          "Trigger provider-owned recent sync for the affected timeframe, then confirm the "
          "latest checkpoint, sync timestamp, and freshness window have recovered."
        ),
        runbook="market_data.sync_recent",
      )
    if category == "market_data_quality":
      return _IncidentRemediationPlan(
        kind="historical_backfill",
        owner="provider",
        summary="Backfill the historical window to the configured target coverage.",
        detail=(
          "Run provider-owned historical backfill, then verify target coverage and completion "
          "ratio against the guarded-live backfill policy."
        ),
        runbook="market_data.backfill_history",
      )
    if category in {"market_data_candle_continuity", "market_data_candle_sequence", "market_data_kline_consistency"}:
      return _IncidentRemediationPlan(
        kind="candle_repair",
        owner="provider",
        summary="Repair candle continuity and restore the affected kline sequence.",
        detail=(
          "Backfill the affected candle range, verify contiguous candle boundaries, and confirm "
          "the kline stream has resumed with valid ordering."
        ),
        runbook="market_data.repair_candles",
      )
    if category == "market_data_venue":
      return _IncidentRemediationPlan(
        kind="venue_fault_review",
        owner="provider",
        summary="Review upstream venue faults and re-run the affected sync path.",
        detail=(
          "Escalate the venue-specific upstream fault, then retry provider-owned market-data sync "
          "for the affected instrument and timeframe."
        ),
        runbook="market_data.review_venue_fault",
      )
    if category in {"market_data_channel_consistency", "market_data_channel_restore"}:
      return _IncidentRemediationPlan(
        kind="channel_restore",
        owner="provider",
        summary="Restore stale or missing guarded-live market-data channels.",
        detail=(
          "Restart or resubscribe the affected market-data channels, then confirm the guarded-live "
          "handoff is receiving fresh events for every covered channel."
        ),
        runbook="market_data.restore_channels",
      )
    if category in {
      "market_data_ladder_integrity",
      "market_data_venue_ladder_integrity",
      "market_data_ladder_bridge_integrity",
      "market_data_ladder_sequence_integrity",
      "market_data_ladder_snapshot_refresh",
      "market_data_depth_ladder",
      "market_data_book_consistency",
    }:
      return _IncidentRemediationPlan(
        kind="order_book_rebuild",
        owner="provider",
        summary="Rebuild the venue ladder and restore order-book integrity checks.",
        detail=(
          "Trigger provider-owned depth snapshot rebuild, replay the exchange bridge rules, and "
          "verify the local ladder, top-of-book, and snapshot refresh state are healthy again."
        ),
        runbook="market_data.rebuild_order_book",
      )
    return _IncidentRemediationPlan(
      kind="market_data_review",
      owner="provider",
      summary="Review the affected market-data policy path and restore normal coverage.",
      detail=(
        "Inspect the degraded guarded-live market-data path, trigger the provider-owned recovery "
        "workflow, and verify the affected policy has recovered."
      ),
      runbook="market_data.review_policy_fault",
    )

  def _build_incident_remediation(
    self,
    *,
    alert: OperatorAlert,
    policy: _IncidentPagingPolicy,
  ) -> OperatorIncidentRemediation:
    if not self._alert_supports_remediation(alert=alert):
      return OperatorIncidentRemediation()
    plan = self._market_data_remediation_plan(category=alert.category)
    owner = "provider" if policy.provider and plan.owner == "provider" else "operator"
    if alert.status == "resolved":
      state = "completed"
    elif owner == "provider":
      state = "suggested"
    else:
      state = "operator_review"
    return OperatorIncidentRemediation(
      state=state,
      kind=plan.kind,
      owner=owner,
      summary=plan.summary,
      detail=plan.detail,
      runbook=plan.runbook,
      provider=self._normalize_paging_provider(policy.provider),
    )

  def _resolve_incident_paging_policy(self, *, alert: OperatorAlert) -> _IncidentPagingPolicy:
    severity = alert.severity.strip().lower()
    policy_id = "default"
    initial_targets = self._operator_alert_delivery.list_targets()
    escalation_targets = self._operator_alert_escalation_targets or initial_targets
    if severity in {"critical", "error"}:
      policy_id = "severity:critical"
      if self._operator_alert_paging_policy_critical_targets:
        initial_targets = self._operator_alert_paging_policy_critical_targets
      if self._operator_alert_paging_policy_critical_escalation_targets:
        escalation_targets = self._operator_alert_paging_policy_critical_escalation_targets
    elif severity in {"warning", "warn"}:
      policy_id = "severity:warning"
      if self._operator_alert_paging_policy_warning_targets:
        initial_targets = self._operator_alert_paging_policy_warning_targets
      if self._operator_alert_paging_policy_warning_escalation_targets:
        escalation_targets = self._operator_alert_paging_policy_warning_escalation_targets

    initial_targets = self._normalize_targets(initial_targets)
    escalation_targets = self._normalize_targets(escalation_targets)
    resolution_targets = self._normalize_targets((*initial_targets, *escalation_targets))
    provider = self._operator_alert_paging_policy_default_provider or self._infer_paging_provider(
      initial_targets=initial_targets,
      escalation_targets=escalation_targets,
    )
    return _IncidentPagingPolicy(
      policy_id=policy_id,
      provider=provider,
      initial_targets=initial_targets,
      escalation_targets=escalation_targets,
      resolution_targets=resolution_targets,
    )

  @staticmethod
  def _infer_paging_provider(
    *,
    initial_targets: tuple[str, ...],
    escalation_targets: tuple[str, ...],
  ) -> str | None:
    combined = {target.strip().lower().replace("-", "_") for target in (*initial_targets, *escalation_targets)}
    if "pagerduty_events" in combined:
      return "pagerduty"
    if "opsgenie_alerts" in combined:
      return "opsgenie"
    return None

  def _deliver_guarded_live_incident_events(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    bool,
  ]:
    persisted_events: list[OperatorIncidentEvent] = []
    delivery_records: list[OperatorIncidentDelivery] = []
    auto_remediation_executed = False
    for incident in incident_events:
      records = self._operator_alert_delivery.deliver(
        incident=incident,
        targets=incident.delivery_targets,
        attempt_number=1,
        phase="initial",
      )
      records = self._apply_delivery_retry_policy(
        records=records,
        current_time=current_time,
      )
      delivery_state = self._resolve_incident_delivery_state(records=records)
      external_record = next((record for record in records if record.external_provider is not None), None)
      paging_status = incident.paging_status
      external_status = incident.external_status
      if external_record is not None and delivery_state in {"delivered", "partial"}:
        if incident.kind == "incident_opened":
          paging_status = "triggered"
          external_status = "triggered"
        elif incident.kind == "incident_resolved":
          paging_status = "resolved"
          external_status = "resolved"
      persisted_events.append(
        replace(
          incident,
          delivery_state=delivery_state,
          delivery_targets=incident.delivery_targets or self._operator_alert_delivery.list_targets(),
          paging_provider=(
            external_record.external_provider if external_record is not None else incident.paging_provider
          ),
          external_provider=(
            external_record.external_provider if external_record is not None else incident.external_provider
          ),
          external_reference=(
            external_record.external_reference if external_record is not None else incident.external_reference
          ),
          external_status=external_status,
          paging_status=paging_status,
        )
      )
      delivery_records.extend(records)
      if incident.kind == "incident_opened":
        persisted_events[-1], auto_results = self._execute_local_incident_remediation(
          incident=persisted_events[-1],
          actor="system",
          current_time=current_time,
        )
        auto_remediation_executed = auto_remediation_executed or bool(auto_results)
        persisted_events[-1], remediation_records = self._request_incident_remediation(
          incident=persisted_events[-1],
          delivery_history=tuple(delivery_records),
          current_time=current_time,
          actor="system",
          detail="incident_opened",
        )
        if remediation_records:
          delivery_records.extend(remediation_records)
    return tuple(persisted_events), tuple(delivery_records), auto_remediation_executed

  def _retry_guarded_live_incident_deliveries(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    retries: list[OperatorIncidentDelivery] = []
    incidents_by_id = {incident.event_id: incident for incident in incident_events}
    for incident_event_id, target, attempt_number in self._collect_due_incident_retries(
      incident_events=incident_events,
      delivery_history=delivery_history,
      current_time=current_time,
    ):
      incident = incidents_by_id.get(incident_event_id)
      if incident is None:
        continue
      latest = self._latest_incident_delivery_record(
        delivery_history=delivery_history,
        incident_event_id=incident_event_id,
        target=target,
      )
      if latest is None:
        continue
      if latest.phase.startswith("provider_"):
        provider = latest.external_provider or incident.paging_provider or incident.external_provider
        action = latest.provider_action or latest.phase.removeprefix("provider_")
        if provider is None:
          continue
        records = self._operator_alert_delivery.sync_incident_workflow(
          incident=incident,
          provider=provider,
          action=action,
          actor="system",
          detail=f"retry:{latest.phase}",
          attempt_number=attempt_number,
        )
      else:
        records = self._operator_alert_delivery.deliver(
          incident=incident,
          targets=(target,),
          attempt_number=attempt_number,
          phase=latest.phase,
        )
      retries.extend(
        self._apply_delivery_retry_policy(
          records=records,
          current_time=current_time,
        )
      )
    return tuple(retries)

  def _collect_due_incident_retries(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[tuple[str, str, int], ...]:
    due_retries: list[tuple[str, str, int]] = []
    incidents_by_id = {incident.event_id: incident for incident in incident_events}
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)

    for latest in latest_by_key.values():
      incident = incidents_by_id.get(latest.incident_event_id)
      if incident is None:
        continue
      if incident.kind == "incident_opened" and not self._incident_is_still_active(
        incident=incident,
        incident_events=incident_events,
      ):
        continue
      if (
        incident.kind == "incident_opened"
        and incident.acknowledgment_state == "acknowledged"
        and not latest.phase.startswith("provider_")
      ):
        continue
      if latest.status != "retry_scheduled" or latest.next_retry_at is None:
        continue
      if latest.next_retry_at > current_time:
        continue
      if latest.attempt_number >= self._operator_alert_delivery_max_attempts:
        continue
      due_retries.append((latest.incident_event_id, latest.target, latest.attempt_number + 1))
    due_retries.sort()
    return tuple(due_retries)

  def _apply_incident_delivery_state(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> tuple[OperatorIncidentEvent, ...]:
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)

    refreshed: list[OperatorIncidentEvent] = []
    for incident in incident_events:
      delivery_records = tuple(
        record
        for key, record in latest_by_key.items()
        if key[0] == incident.event_id
        and not key[2].startswith("provider_")
      )
      provider_records = tuple(
        record
        for key, record in latest_by_key.items()
        if key[0] == incident.event_id
        and key[2].startswith("provider_")
      )
      latest_provider_record = self._latest_provider_workflow_record(records=provider_records)
      refreshed.append(
        replace(
          incident,
          delivery_state=self._resolve_incident_delivery_state(records=delivery_records),
          provider_workflow_state=(
            self._resolve_incident_delivery_state(records=provider_records)
            if provider_records
            else incident.provider_workflow_state
          ),
          provider_workflow_action=(
            latest_provider_record.provider_action
            if latest_provider_record is not None
            else incident.provider_workflow_action
          ),
          provider_workflow_last_attempted_at=(
            latest_provider_record.attempted_at
            if latest_provider_record is not None
            else incident.provider_workflow_last_attempted_at
          ),
          provider_workflow_reference=(
            latest_provider_record.external_reference
            if latest_provider_record is not None and latest_provider_record.external_reference is not None
            else incident.provider_workflow_reference
          ),
          remediation=self._refresh_incident_remediation_state(
            incident=incident,
            latest_by_key=latest_by_key,
          ),
        )
      )
    refreshed.sort(key=lambda event: event.timestamp, reverse=True)
    return tuple(refreshed)

  def _refresh_incident_remediation_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    latest_by_key: dict[tuple[str, str, str], OperatorIncidentDelivery],
  ) -> OperatorIncidentRemediation:
    remediation = incident.remediation
    if remediation.state == "not_applicable":
      return remediation
    remediation_records = tuple(
      record
      for key, record in latest_by_key.items()
      if key[0] == incident.event_id and key[2] == "provider_remediate"
    )
    if not remediation_records:
      return remediation
    latest_record = self._latest_provider_workflow_record(records=remediation_records)
    next_state = self._resolve_remediation_delivery_state(
      records=remediation_records,
      current_state=remediation.state,
    )
    return replace(
      remediation,
      state=next_state,
      last_attempted_at=(
        latest_record.attempted_at if latest_record is not None else remediation.last_attempted_at
      ),
      provider=(
        latest_record.external_provider
        if latest_record is not None and latest_record.external_provider is not None
        else remediation.provider
      ),
      reference=(
        latest_record.external_reference
        if latest_record is not None and latest_record.external_reference is not None
        else remediation.reference
      ),
    )

  def _request_incident_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    actor: str,
    detail: str,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...]]:
    remediation = incident.remediation
    if incident.kind != "incident_opened" or remediation.state in {"not_applicable", "completed"}:
      return incident, ()

    detail_copy = detail.strip() or remediation.detail or remediation.summary or "remediation_requested"
    requested_remediation = replace(
      remediation,
      requested_at=current_time,
      requested_by=actor,
      last_attempted_at=current_time,
    )
    if remediation.owner != "provider":
      return replace(incident, remediation=requested_remediation), ()

    provider = requested_remediation.provider or incident.paging_provider or incident.external_provider
    if provider is None:
      return (
        replace(
          incident,
          remediation=replace(
            requested_remediation,
            state="not_configured",
          ),
        ),
        (),
      )
    normalized_provider = self._normalize_paging_provider(provider)
    supported_providers = {
      self._normalize_paging_provider(candidate)
      for candidate in self._operator_alert_delivery.list_supported_workflow_providers()
    }
    if normalized_provider not in supported_providers:
      return (
        replace(
          incident,
          remediation=replace(
            requested_remediation,
            state="not_supported",
            provider=normalized_provider,
          ),
        ),
        (),
      )

    records = self._operator_alert_delivery.sync_incident_workflow(
      incident=incident,
      provider=normalized_provider or provider,
      action="remediate",
      actor=actor,
      detail=detail_copy,
      attempt_number=1,
    )
    records = self._apply_delivery_retry_policy(
      records=records,
      current_time=current_time,
    )
    latest = self._latest_provider_workflow_record(records=records)
    updated_incident = replace(
      incident,
      remediation=replace(
        requested_remediation,
        state=self._resolve_remediation_delivery_state(
          records=records,
          current_state=requested_remediation.state,
        ),
        provider=normalized_provider,
        reference=(
          latest.external_reference
          if latest is not None and latest.external_reference is not None
          else requested_remediation.reference
        ),
      ),
    )
    return updated_incident, records

  def _resolve_remediation_delivery_state(
    self,
    *,
    records: tuple[OperatorIncidentDelivery, ...],
    current_state: str,
  ) -> str:
    if current_state in {
      "executed",
      "partial",
      "failed",
      "skipped",
      "completed",
      "provider_recovering",
      "provider_recovered",
    }:
      return current_state
    delivery_state = self._resolve_incident_delivery_state(records=records)
    mapping = {
      "delivered": "requested",
      "partial": "requested",
      "retrying": "retrying",
      "failed": "failed",
      "suppressed": "suppressed",
      "not_configured": current_state,
    }
    return mapping.get(delivery_state, current_state)

  def _execute_local_incident_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    actor: str,
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, tuple[MarketDataRemediationResult, ...]]:
    remediation = incident.remediation
    if remediation.kind in {
      "recent_sync",
      "historical_backfill",
      "candle_repair",
      "venue_fault_review",
      "market_data_review",
    }:
      timeframe, symbols = self._resolve_market_data_remediation_targets(incident=incident)
      if timeframe is None or not symbols:
        return incident, ()

      results_list: list[MarketDataRemediationResult] = []
      for symbol in symbols:
        try:
          results_list.append(
            self._market_data.remediate(
              kind=remediation.kind,
              symbol=symbol,
              timeframe=timeframe,
            )
          )
        except Exception as exc:
          results_list.append(
            MarketDataRemediationResult(
              kind=remediation.kind,
              symbol=symbol,
              timeframe=timeframe,
              status="failed",
              started_at=current_time,
              finished_at=current_time,
              detail=f"market_data_remediation_failed:{exc}",
            )
          )
      results = tuple(results_list)
    elif remediation.kind in {"channel_restore", "order_book_rebuild"}:
      results = self._execute_local_guarded_live_session_remediation(
        incident=incident,
        actor=actor,
        current_time=current_time,
      )
    else:
      return incident, ()
    if not results:
      return incident, ()

    last_attempted_at = max((result.finished_at for result in results), default=current_time)
    updated_remediation = replace(
      remediation,
      state=self._resolve_local_remediation_state(results=results),
      requested_at=current_time,
      requested_by=actor,
      last_attempted_at=last_attempted_at,
      detail=self._summarize_local_remediation_results(results),
    )
    return replace(incident, remediation=updated_remediation), results

  def _execute_local_guarded_live_session_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    actor: str,
    current_time: datetime,
  ) -> tuple[MarketDataRemediationResult, ...]:
    state = self._guarded_live_state.load_state()
    run = self._resolve_guarded_live_remediation_run(incident=incident, state=state)
    symbol, timeframe = self._resolve_guarded_live_remediation_identity(
      run=run,
      state=state,
    )
    remediation_kind = incident.remediation.kind
    if run is None:
      return (
        MarketDataRemediationResult(
          kind=remediation_kind,
          symbol=symbol,
          timeframe=timeframe,
          status="failed",
          started_at=current_time,
          finished_at=current_time,
          detail=f"{remediation_kind}:{symbol}:{timeframe}:guarded_live_run_unavailable",
        ),
      )

    session = run.provenance.runtime_session
    remediation_reason = f"incident_remediation:{remediation_kind}"
    try:
      handoff = self._activate_guarded_live_venue_session(
        run=run,
        reason=remediation_reason,
      )
      session_sync = self._sync_guarded_live_session(run=run, handoff=handoff)
      next_handoff = session_sync["handoff"]
      run = self._runs.save_run(run)
      refreshed_state = self._build_guarded_live_state_for_local_session_remediation(
        state=self._guarded_live_state.load_state(),
        run=run,
        actor=actor,
        reason=remediation_reason,
        session_handoff=next_handoff,
      )
      self._persist_guarded_live_state(refreshed_state)
      detail = self._summarize_guarded_live_session_remediation_result(
        remediation_kind=remediation_kind,
        handoff=next_handoff,
      )
      self._append_guarded_live_audit_event(
        kind="guarded_live_incident_local_remediation_executed",
        actor=actor,
        summary=f"Guarded-live local remediation executed for {incident.alert_id}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=session.session_id if session is not None else None,
      )
      return (
        MarketDataRemediationResult(
          kind=remediation_kind,
          symbol=symbol,
          timeframe=timeframe,
          status="executed",
          started_at=current_time,
          finished_at=self._clock(),
          detail=detail,
        ),
      )
    except Exception as exc:
      detail = f"{remediation_kind}:{symbol}:{timeframe}:guarded_live_session_remediation_failed:{exc}"
      self._append_guarded_live_audit_event(
        kind="guarded_live_incident_local_remediation_failed",
        actor=actor,
        summary=f"Guarded-live local remediation failed for {incident.alert_id}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=session.session_id if session is not None else None,
      )
      return (
        MarketDataRemediationResult(
          kind=remediation_kind,
          symbol=symbol,
          timeframe=timeframe,
          status="failed",
          started_at=current_time,
          finished_at=self._clock(),
          detail=detail,
        ),
      )

  def _resolve_guarded_live_remediation_run(
    self,
    *,
    incident: OperatorIncidentEvent,
    state: GuardedLiveState,
  ) -> RunRecord | None:
    if incident.run_id is not None and (run := self._runs.get_run(incident.run_id)) is not None:
      return run
    owner_run_id = state.session_handoff.owner_run_id or state.ownership.owner_run_id
    if owner_run_id is None:
      return None
    return self._runs.get_run(owner_run_id)

  @staticmethod
  def _resolve_guarded_live_remediation_identity(
    *,
    run: RunRecord | None,
    state: GuardedLiveState,
  ) -> tuple[str, str]:
    if run is not None:
      symbol = run.config.symbols[0] if run.config.symbols else "unknown"
      timeframe = run.config.timeframe or "unknown"
      return symbol, timeframe
    symbol = state.session_handoff.symbol or state.ownership.symbol or "unknown"
    timeframe = state.session_handoff.timeframe or "unknown"
    return symbol, timeframe

  def _build_guarded_live_state_for_local_session_remediation(
    self,
    *,
    state: GuardedLiveState,
    run: RunRecord,
    actor: str,
    reason: str,
    session_handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveState:
    session = run.provenance.runtime_session
    current_time = self._clock()
    existing = state.ownership
    return replace(
      state,
      ownership=GuardedLiveSessionOwnership(
        state="owned",
        owner_run_id=run.config.run_id,
        owner_session_id=session.session_id if session is not None else existing.owner_session_id,
        symbol=run.config.symbols[0] if run.config.symbols else existing.symbol,
        claimed_at=existing.claimed_at if existing.owner_run_id == run.config.run_id else current_time,
        claimed_by=existing.claimed_by if existing.owner_run_id == run.config.run_id else actor,
        last_heartbeat_at=session.last_heartbeat_at if session is not None else existing.last_heartbeat_at,
        last_order_sync_at=current_time,
        last_resumed_at=existing.last_resumed_at,
        last_reason=reason,
        last_released_at=None,
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

  @staticmethod
  def _summarize_guarded_live_session_remediation_result(
    *,
    remediation_kind: str,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> str:
    symbol = handoff.symbol or "unknown"
    timeframe = handoff.timeframe or "unknown"
    if remediation_kind == "channel_restore":
      detail = (
        f"{remediation_kind}:{symbol}:{timeframe}:channel_restore={handoff.channel_restore_state};"
        f"continuation={handoff.channel_continuation_state};"
        f"transport={handoff.transport};source={handoff.source};state={handoff.state}"
      )
      if handoff.channel_last_restored_at is not None:
        detail += f";restored_at={handoff.channel_last_restored_at.isoformat()}"
      if handoff.channel_last_continued_at is not None:
        detail += f";continued_at={handoff.channel_last_continued_at.isoformat()}"
      if handoff.issues:
        detail += f";issues={','.join(handoff.issues[:3])}"
      return detail
    detail = (
      f"{remediation_kind}:{symbol}:{timeframe}:order_book={handoff.order_book_state};"
      f"transport={handoff.transport};source={handoff.source};state={handoff.state};"
      f"rebuilds={handoff.order_book_rebuild_count};gaps={handoff.order_book_gap_count}"
    )
    if handoff.order_book_last_rebuilt_at is not None:
      detail += f";rebuilt_at={handoff.order_book_last_rebuilt_at.isoformat()}"
    if handoff.order_book_best_bid_price is not None or handoff.order_book_best_ask_price is not None:
      detail += (
        f";top_of_book={handoff.order_book_best_bid_price or 0.0:.8f}/"
        f"{handoff.order_book_best_ask_price or 0.0:.8f}"
      )
    if handoff.issues:
      detail += f";issues={','.join(handoff.issues[:3])}"
    return detail

  def _resolve_market_data_remediation_targets(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> tuple[str | None, tuple[str, ...]]:
    remediation = incident.remediation
    timeframe: str | None = None
    venue: str | None = None
    alert_parts = incident.alert_id.split(":")
    if remediation.kind == "recent_sync" and len(alert_parts) == 3 and alert_parts[1] == "market-data":
      timeframe = alert_parts[2]
    elif remediation.kind in {
      "historical_backfill",
      "candle_repair",
      "venue_fault_review",
      "market_data_review",
    } and len(alert_parts) == 4 and alert_parts[1].startswith("market-data-"):
      venue = alert_parts[2]
      timeframe = alert_parts[3]

    symbols: list[str] = []
    if incident.run_id is not None and (run := self._runs.get_run(incident.run_id)) is not None:
      timeframe = timeframe or run.config.timeframe
      venue = venue or run.config.venue
      return timeframe, tuple(dict.fromkeys(run.config.symbols))

    if timeframe is None:
      return None, ()

    try:
      status = self._market_data.get_status(timeframe)
    except Exception:
      status = None
    if status is not None:
      venue = venue or status.venue
      for instrument in status.instruments:
        symbol = self._symbol_from_instrument_id(instrument.instrument_id)
        if symbol not in symbols:
          symbols.append(symbol)

    if venue is not None and incident.run_id is None:
      live_runs = [
        run
        for run in self._runs.list_runs(mode=RunMode.LIVE.value)
        if run.config.timeframe == timeframe and run.config.venue == venue
      ]
      if live_runs:
        live_symbols = [
          symbol
          for run in live_runs
          for symbol in run.config.symbols
          if symbol in symbols or not symbols
        ]
        if live_symbols:
          symbols = list(dict.fromkeys(live_symbols))

    return timeframe, tuple(dict.fromkeys(symbols))

  @staticmethod
  def _resolve_local_remediation_state(
    *,
    results: tuple[MarketDataRemediationResult, ...],
  ) -> str:
    executed = sum(result.status in {"executed", "skipped"} for result in results)
    failed = sum(result.status == "failed" for result in results)
    if failed and executed:
      return "partial"
    if failed:
      return "failed"
    if results and all(result.status == "skipped" for result in results):
      return "skipped"
    return "executed"

  @staticmethod
  def _summarize_local_remediation_results(
    results: tuple[MarketDataRemediationResult, ...],
  ) -> str:
    if not results:
      return "not_executed"
    detail_copy = [result.detail for result in results if result.detail]
    summary = " ".join(detail_copy[:2]) if detail_copy else "local_remediation_executed"
    if len(detail_copy) > 2:
      summary += f" Additional jobs: {len(detail_copy) - 2}."
    return summary

  def _refresh_guarded_live_incident_workflow(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    tuple[OperatorAuditEvent, ...],
  ]:
    updated_incidents = incident_events
    effective_delivery_history = delivery_history
    audit_events: list[OperatorAuditEvent] = []

    for incident in incident_events:
      if incident.kind != "incident_opened":
        continue
      if (
        not self._incident_is_still_active(
          incident=incident,
          incident_events=updated_incidents,
        )
        or incident.acknowledgment_state == "acknowledged"
      ):
        continue
      if incident.escalation_level >= self._operator_alert_incident_max_escalations:
        continue

      trigger: str | None = None
      reason: str | None = None
      if self._incident_has_exhausted_initial_delivery(
        incident=incident,
        delivery_history=effective_delivery_history,
      ):
        trigger = "delivery_exhausted"
        reason = "retry_budget_exhausted"
      elif incident.next_escalation_at is not None and incident.next_escalation_at <= current_time:
        trigger = "ack_timeout"
        reason = "ack_timeout_elapsed"
      if trigger is None or reason is None:
        continue

      updated_incident, effective_delivery_history, audit_event = self._escalate_incident_event(
        incident=incident,
        delivery_history=effective_delivery_history,
        current_time=current_time,
        actor="system",
        reason=reason,
        trigger=trigger,
      )
      updated_incidents = self._replace_incident_event(
        incident_events=updated_incidents,
        updated_incident=updated_incident,
      )
      audit_events.append(audit_event)
    return updated_incidents, effective_delivery_history, tuple(audit_events)

  def _apply_delivery_retry_policy(
    self,
    *,
    records: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    updated: list[OperatorIncidentDelivery] = []
    for record in records:
      if record.status != "failed":
        updated.append(record)
        continue
      if record.attempt_number >= self._operator_alert_delivery_max_attempts:
        updated.append(record)
        continue
      updated.append(
        replace(
          record,
          status="retry_scheduled",
          next_retry_at=current_time + timedelta(
            seconds=self._resolve_delivery_backoff_seconds(record.attempt_number)
          ),
        )
      )
    return tuple(updated)

  def _resolve_delivery_backoff_seconds(self, attempt_number: int) -> int:
    multiplier = self._operator_alert_delivery_backoff_multiplier ** max(attempt_number - 1, 0)
    backoff = int(self._operator_alert_delivery_initial_backoff_seconds * multiplier)
    return min(backoff, self._operator_alert_delivery_max_backoff_seconds)

  @staticmethod
  def _resolve_incident_delivery_state(
    *,
    records: tuple[OperatorIncidentDelivery, ...],
  ) -> str:
    if not records:
      return "not_configured"
    statuses = {record.status for record in records}
    if statuses <= {"delivered", "retry_suppressed"} and "delivered" in statuses:
      return "delivered"
    if "retry_scheduled" in statuses:
      return "retrying"
    if statuses == {"retry_suppressed"}:
      return "suppressed"
    if "delivered" in statuses:
      return "partial"
    return "failed"

  @staticmethod
  def _latest_delivery_records_by_key(
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> dict[tuple[str, str, str], OperatorIncidentDelivery]:
    latest_by_key: dict[tuple[str, str, str], OperatorIncidentDelivery] = {}
    for record in delivery_history:
      key = (record.incident_event_id, record.target, record.phase)
      existing = latest_by_key.get(key)
      if existing is None or record.attempt_number > existing.attempt_number:
        latest_by_key[key] = record
    return latest_by_key

  def _latest_incident_delivery_record(
    self,
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident_event_id: str,
    target: str,
  ) -> OperatorIncidentDelivery | None:
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)
    candidates = [
      record
      for key, record in latest_by_key.items()
      if key[0] == incident_event_id and key[1] == target
    ]
    if not candidates:
      return None
    candidates.sort(key=lambda record: (record.phase == "escalation", record.attempt_number), reverse=True)
    return candidates[0]

  @staticmethod
  def _latest_provider_workflow_record(
    *,
    records: tuple[OperatorIncidentDelivery, ...],
  ) -> OperatorIncidentDelivery | None:
    if not records:
      return None
    return max(
      records,
      key=lambda record: (
        record.attempted_at,
        record.attempt_number,
      ),
    )

  @staticmethod
  def _replace_incident_event(
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    updated_incident: OperatorIncidentEvent,
  ) -> tuple[OperatorIncidentEvent, ...]:
    replaced = [
      updated_incident if incident.event_id == updated_incident.event_id else incident
      for incident in incident_events
    ]
    replaced.sort(key=lambda event: event.timestamp, reverse=True)
    return tuple(replaced)

  @staticmethod
  def _incident_is_still_active(
    *,
    incident: OperatorIncidentEvent,
    incident_events: tuple[OperatorIncidentEvent, ...],
  ) -> bool:
    if incident.kind != "incident_opened":
      return False
    for candidate in incident_events:
      if candidate.alert_id != incident.alert_id or candidate.kind != "incident_resolved":
        continue
      if candidate.timestamp >= incident.timestamp:
        return False
    return True

  def _require_active_guarded_live_incident(
    self,
    *,
    state: GuardedLiveState,
    event_id: str,
  ) -> OperatorIncidentEvent:
    incident = next((event for event in state.incident_events if event.event_id == event_id), None)
    if incident is None:
      raise LookupError("Guarded-live incident not found")
    if incident.kind != "incident_opened":
      raise ValueError("Only active incident_opened records can be acknowledged or escalated")
    if not self._incident_is_still_active(incident=incident, incident_events=state.incident_events):
      raise ValueError("Guarded-live incident is no longer active")
    return incident

  def _find_guarded_live_incident_for_external_sync(
    self,
    *,
    state: GuardedLiveState,
    alert_id: str | None,
    external_reference: str | None,
  ) -> OperatorIncidentEvent:
    candidates = [
      incident
      for incident in state.incident_events
      if incident.kind == "incident_opened"
      and (
        (alert_id is not None and incident.alert_id == alert_id)
        or (
          external_reference is not None
          and (
            incident.external_reference == external_reference
            or incident.provider_workflow_reference == external_reference
            or incident.alert_id == external_reference
          )
        )
      )
    ]
    if not candidates:
      raise LookupError("Guarded-live incident not found for external sync")
    candidates.sort(
      key=lambda incident: (
        self._incident_is_still_active(incident=incident, incident_events=state.incident_events),
        incident.timestamp,
      ),
      reverse=True,
    )
    return candidates[0]

  @staticmethod
  def _suppress_pending_incident_retries(
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident_event_id: str,
    reason: str,
    phase: str | None = None,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    updated: list[OperatorIncidentDelivery] = []
    for record in delivery_history:
      if record.incident_event_id != incident_event_id:
        updated.append(record)
        continue
      if phase is not None and record.phase != phase:
        updated.append(record)
        continue
      if record.status != "retry_scheduled":
        updated.append(record)
        continue
      updated.append(
        replace(
          record,
          status="retry_suppressed",
          next_retry_at=None,
          detail=f"{record.detail}; retry_suppressed:{reason}",
        )
      )
    return tuple(updated)

  def _sync_incident_provider_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    action: str,
    actor: str,
    detail: str,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...]]:
    provider = incident.paging_provider or incident.external_provider
    if provider is None:
      return (
        replace(
          incident,
          provider_workflow_state="not_configured",
          provider_workflow_action=action,
        ),
        delivery_history,
      )
    normalized_provider = self._normalize_paging_provider(provider)
    supported_providers = {
      self._normalize_paging_provider(candidate)
      for candidate in self._operator_alert_delivery.list_supported_workflow_providers()
    }
    if normalized_provider not in supported_providers:
      return (
        replace(
          incident,
          paging_provider=normalized_provider,
          provider_workflow_state="not_supported",
          provider_workflow_action=action,
          provider_workflow_last_attempted_at=current_time,
        ),
        delivery_history,
      )

    records = self._operator_alert_delivery.sync_incident_workflow(
      incident=incident,
      provider=normalized_provider or provider,
      action=action,
      actor=actor,
      detail=detail,
      attempt_number=1,
    )
    records = self._apply_delivery_retry_policy(
      records=records,
      current_time=current_time,
    )
    latest = self._latest_provider_workflow_record(records=records)
    updated_incident = replace(
      incident,
      paging_provider=normalized_provider,
      external_provider=normalized_provider or incident.external_provider,
      provider_workflow_action=action,
      provider_workflow_last_attempted_at=(
        latest.attempted_at if latest is not None else current_time
      ),
      provider_workflow_reference=(
        latest.external_reference
        if latest is not None and latest.external_reference is not None
        else incident.provider_workflow_reference
      ),
    )
    return updated_incident, tuple((*records, *delivery_history))

  def _confirm_external_provider_workflow(
    self,
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident: OperatorIncidentEvent,
    provider: str,
    event_kind: str,
    detail: str,
    occurred_at: datetime,
    external_reference: str | None,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    phase = self._provider_phase_for_event_kind(event_kind)
    if phase is None:
      return delivery_history
    provider_prefix = self._normalize_paging_provider(provider) or provider
    updated_history = self._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_confirmed:{provider_prefix}:{event_kind}",
      phase=phase,
    )
    confirmation = OperatorIncidentDelivery(
      delivery_id=f"{incident.event_id}:{provider_prefix}_external:{event_kind}:{occurred_at.isoformat()}",
      incident_event_id=incident.event_id,
      alert_id=incident.alert_id,
      incident_kind=incident.kind,
      target=f"{provider_prefix}_external_sync",
      status="delivered",
      attempted_at=occurred_at,
      detail=f"external_provider_confirmed:{event_kind}:{detail}",
      phase=phase,
      provider_action=phase.removeprefix("provider_"),
      external_provider=provider_prefix,
      external_reference=external_reference,
      source=incident.source,
    )
    return (confirmation, *updated_history)

  @staticmethod
  def _provider_phase_for_event_kind(event_kind: str) -> str | None:
    mapping = {
      "triggered": "provider_trigger",
      "acknowledged": "provider_acknowledge",
      "escalated": "provider_escalate",
      "resolved": "provider_resolve",
      "remediation_requested": "provider_remediate",
      "remediation_started": "provider_remediate",
      "remediation_completed": "provider_remediate",
      "remediation_failed": "provider_remediate",
    }
    return mapping.get(event_kind)

  def _incident_has_exhausted_initial_delivery(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> bool:
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)
    initial_records = [
      record
      for key, record in latest_by_key.items()
      if key[0] == incident.event_id and key[2] == "initial"
    ]
    return any(record.status == "failed" for record in initial_records)

  def _escalate_incident_event(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    actor: str,
    reason: str,
    trigger: str,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...], OperatorAuditEvent]:
    escalation_targets = incident.escalation_targets or incident.delivery_targets
    if not escalation_targets:
      raise ValueError("incident escalation has no configured delivery targets")

    updated_delivery_history = self._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"escalated:{trigger}",
      phase="initial",
    )
    next_level = incident.escalation_level + 1
    next_escalation_at = None
    if (
      incident.acknowledgment_state != "acknowledged"
      and next_level < self._operator_alert_incident_max_escalations
    ):
      next_escalation_at = current_time + timedelta(
        seconds=self._resolve_incident_escalation_backoff_seconds(next_level)
      )

    updated_incident = replace(
      incident,
      escalation_level=next_level,
      escalation_state="escalated",
      last_escalated_at=current_time,
      last_escalated_by=actor,
      escalation_reason=reason,
      next_escalation_at=next_escalation_at,
    )
    escalation_deliveries = self._operator_alert_delivery.deliver(
      incident=updated_incident,
      targets=escalation_targets,
      attempt_number=1,
      phase="escalation",
    )
    escalation_deliveries = self._apply_delivery_retry_policy(
      records=escalation_deliveries,
      current_time=current_time,
    )
    updated_delivery_history = tuple((*escalation_deliveries, *updated_delivery_history))
    updated_incident, updated_delivery_history = self._sync_incident_provider_workflow(
      incident=updated_incident,
      delivery_history=updated_delivery_history,
      current_time=current_time,
      action="escalate",
      actor=actor,
      detail=reason,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-escalated:{incident.event_id}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_incident_escalated",
      summary=f"Guarded-live incident escalated for {incident.alert_id}.",
      detail=(
        f"Trigger: {trigger}. Reason: {reason}. Escalation level {next_level} "
        f"sent via {', '.join(escalation_targets)}. "
        f"Provider workflow: {updated_incident.provider_workflow_state}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    return updated_incident, updated_delivery_history, audit_event

  def _resolve_incident_escalation_backoff_seconds(self, escalation_level: int) -> int:
    multiplier = self._operator_alert_incident_escalation_backoff_multiplier ** max(escalation_level - 1, 0)
    backoff = int(self._operator_alert_incident_ack_timeout_seconds * multiplier)
    return min(backoff, self._operator_alert_delivery_max_backoff_seconds)

  def _build_live_operator_alerts_for_run(
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
    delivery_targets = self._guarded_live_delivery_targets()
    failed_event = self._latest_runtime_note_event(run=run, kind="guarded_live_worker_failed")
    if failed_event is not None or session.lifecycle_state == "failed" or run.status == RunStatus.FAILED:
      detected_at = (
        failed_event["timestamp"]
        or run.ended_at
        or session.last_heartbeat_at
        or run.started_at
      )
      detail = failed_event["detail"] if failed_event is not None else (
        run.notes[-1] if run.notes else "Guarded-live worker entered a failed runtime state."
      )
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:worker-failed:{run.config.run_id}:{session.session_id}",
          severity="critical",
          category="worker_failure",
          summary=f"Guarded-live worker failed for {symbol}.",
          detail=detail,
          detected_at=detected_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
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
          alert_id=f"guarded-live:worker-stale:{run.config.run_id}:{session.session_id}",
          severity="warning",
          category="stale_runtime",
          summary=f"Guarded-live worker heartbeat is stale for {symbol}.",
          detail=(
            f"Last heartbeat at {heartbeat_at.isoformat()} exceeded the "
            f"{session.heartbeat_timeout_seconds}s timeout while the live run remains active."
          ),
          detected_at=heartbeat_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    risk_issues: list[str] = []
    latest_equity = run.equity_curve[-1] if run.equity_curve else None
    max_drawdown_pct = run.metrics.get("max_drawdown_pct")
    if isinstance(max_drawdown_pct, Number) and float(max_drawdown_pct) >= self._guarded_live_drawdown_breach_pct:
      risk_issues.append(
        f"max drawdown {float(max_drawdown_pct):.2f}% breached the "
        f"{self._guarded_live_drawdown_breach_pct:.2f}% guardrail"
      )
    total_return_pct = run.metrics.get("total_return_pct")
    if isinstance(total_return_pct, Number) and float(total_return_pct) <= -self._guarded_live_loss_breach_pct:
      risk_issues.append(
        f"total return {float(total_return_pct):.2f}% breached the "
        f"-{self._guarded_live_loss_breach_pct:.2f}% loss guardrail"
      )
    if latest_equity is not None and latest_equity.cash < -self._guarded_live_balance_tolerance:
      risk_issues.append(
        f"cash balance fell below zero to {latest_equity.cash:.2f}"
      )
    if latest_equity is not None and latest_equity.equity > self._guarded_live_balance_tolerance:
      pending_buy_notional = self._estimate_guarded_live_open_buy_notional(run)
      gross_open_risk = max(latest_equity.exposure, 0.0) + pending_buy_notional
      gross_open_risk_ratio = gross_open_risk / latest_equity.equity
      if gross_open_risk_ratio > self._guarded_live_gross_open_risk_ratio:
        risk_issues.append(
          f"gross open risk reached {gross_open_risk_ratio:.2f}x equity "
          f"({gross_open_risk:.2f} notional including {pending_buy_notional:.2f} pending buy notional)"
        )
    if risk_issues:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:risk-breach:{run.config.run_id}:{session.session_id}",
          severity="critical",
          category="risk_breach",
          summary=f"Guarded-live risk guardrail breached for {symbol}.",
          detail=(
            "; ".join(risk_issues)
            + (
              f". Latest equity {latest_equity.equity:.2f}."
              if latest_equity is not None
              else ""
            )
          ),
          detected_at=(
            latest_equity.timestamp
            if latest_equity is not None
            else heartbeat_at
          ),
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if run.status == RunStatus.RUNNING and session.recovery_count >= self._guarded_live_recovery_alert_threshold:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:recovery-loop:{run.config.run_id}:{session.session_id}",
          severity="critical" if session.recovery_count >= self._guarded_live_recovery_alert_threshold + 1 else "warning",
          category="runtime_recovery",
          summary=f"Guarded-live worker recovery loop detected for {symbol}.",
          detail=(
            f"Runtime session recovered {session.recovery_count} times. "
            f"Last recovery: {session.last_recovery_reason or 'unknown'} at "
            f"{session.last_recovered_at.isoformat() if session.last_recovered_at is not None else 'n/a'}."
          ),
          detected_at=session.last_recovered_at or heartbeat_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if run.status == RunStatus.RUNNING:
      stale_orders = []
      for order in run.orders:
        if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
          continue
        synced_at = order.last_synced_at or order.updated_at or order.created_at
        if (current_time - synced_at).total_seconds() <= session.heartbeat_timeout_seconds:
          continue
        stale_orders.append((order, synced_at))
      if stale_orders:
        stale_order_ids = ", ".join(order.order_id for order, _ in stale_orders[:3])
        oldest_sync_at = min(synced_at for _, synced_at in stale_orders)
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:order-sync:{run.config.run_id}:{session.session_id}",
            severity="warning",
            category="order_sync",
            summary=f"Guarded-live venue order sync is stale for {symbol}.",
            detail=(
              f"{len(stale_orders)} active order(s) have not synced within "
              f"{session.heartbeat_timeout_seconds}s. Orders: {stale_order_ids}."
            ),
            detected_at=oldest_sync_at,
            run_id=run.config.run_id,
            session_id=session.session_id,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
    return alerts

  def _estimate_guarded_live_open_buy_notional(self, run: RunRecord) -> float:
    pending_buy_notional = 0.0
    for order in run.orders:
      if order.side != OrderSide.BUY:
        continue
      if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
        continue
      remaining_quantity = self._resolve_guarded_live_order_remaining_quantity(order)
      if remaining_quantity <= self._guarded_live_balance_tolerance:
        continue
      reference_price = order.requested_price or order.average_fill_price or 0.0
      if reference_price <= self._guarded_live_balance_tolerance:
        continue
      pending_buy_notional += remaining_quantity * reference_price
    return pending_buy_notional

  @staticmethod
  def _symbol_from_instrument_id(instrument_id: str) -> str:
    return instrument_id.split(":", 1)[1] if ":" in instrument_id else instrument_id

  @staticmethod
  def _extract_market_data_venue_semantics(
    *,
    venue: str,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    prefix = f"{venue}_"
    semantics: list[str] = []
    for issue in issues:
      if not issue.startswith(prefix):
        continue
      semantic = issue.removeprefix(prefix)
      semantics.append(
        {
          "timeout": "timeout",
          "rate_limited": "rate limit",
          "network_fault": "network fault",
          "auth_fault": "authentication fault",
          "symbol_unavailable": "symbol unavailable",
          "maintenance": "maintenance",
          "upstream_fault": "upstream fault",
        }.get(semantic, semantic.replace("_", " "))
      )
    return tuple(dict.fromkeys(semantics))

  @staticmethod
  def _merge_operator_alert_history(
    *,
    existing: tuple[OperatorAlert, ...],
    active_alerts: list[OperatorAlert],
    current_time: datetime,
  ) -> tuple[OperatorAlert, ...]:
    history_by_id = {alert.alert_id: alert for alert in existing}
    active_ids = {alert.alert_id for alert in active_alerts}

    for alert in active_alerts:
      previous = history_by_id.get(alert.alert_id)
      detected_at = (
        previous.detected_at
        if previous is not None and previous.status == "active"
        else alert.detected_at
      )
      history_by_id[alert.alert_id] = replace(
        alert,
        detected_at=detected_at,
        status="active",
        resolved_at=None,
        delivery_targets=alert.delivery_targets or (previous.delivery_targets if previous is not None else ()),
      )

    for alert_id, previous in tuple(history_by_id.items()):
      if alert_id in active_ids or previous.status != "active":
        continue
      history_by_id[alert_id] = replace(
        previous,
        status="resolved",
        resolved_at=current_time,
      )

    merged = sorted(
      history_by_id.values(),
      key=lambda alert: (alert.resolved_at or alert.detected_at, alert.detected_at),
      reverse=True,
    )
    return tuple(merged)

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
      if kind.startswith("sandbox_worker_") or kind.startswith("guarded_live_worker_"):
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
      "guarded_live_worker_failed": f"Guarded-live worker failed for {symbol}.",
      "guarded_live_worker_recovered": f"Guarded-live worker recovered for {symbol}.",
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
