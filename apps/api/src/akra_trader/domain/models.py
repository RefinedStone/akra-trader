from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class AssetType(str, Enum):
  CRYPTO = "crypto"
  STOCK = "stock"


class MarketType(str, Enum):
  SPOT = "spot"
  FUTURES = "futures"


class RunMode(str, Enum):
  BACKTEST = "backtest"
  SANDBOX = "sandbox"
  PAPER = "paper"
  LIVE = "live"


class RunStatus(str, Enum):
  PENDING = "pending"
  RUNNING = "running"
  COMPLETED = "completed"
  FAILED = "failed"
  STOPPED = "stopped"


class OrderSide(str, Enum):
  BUY = "buy"
  SELL = "sell"


class OrderType(str, Enum):
  MARKET = "market"
  LIMIT = "limit"


class OrderStatus(str, Enum):
  OPEN = "open"
  PARTIALLY_FILLED = "partially_filled"
  FILLED = "filled"
  CANCELED = "canceled"
  REJECTED = "rejected"


class SignalAction(str, Enum):
  BUY = "buy"
  SELL = "sell"
  HOLD = "hold"


@dataclass(frozen=True)
class Instrument:
  symbol: str
  venue: str
  base_currency: str
  quote_currency: str
  asset_type: AssetType = AssetType.CRYPTO
  market_type: MarketType = MarketType.SPOT

  @property
  def instrument_id(self) -> str:
    return f"{self.venue}:{self.symbol}"


@dataclass(frozen=True)
class Candle:
  timestamp: datetime
  open: float
  high: float
  low: float
  close: float
  volume: float


@dataclass(frozen=True)
class WarmupSpec:
  required_bars: int
  timeframes: tuple[str, ...] = ("5m",)


@dataclass(frozen=True)
class ReferenceSource:
  reference_id: str
  title: str
  kind: str
  homepage: str
  license: str
  integration_mode: str
  local_path: str | None = None
  runtime: str | None = None
  summary: str = ""


@dataclass(frozen=True)
class StrategyLifecycle:
  stage: str = "active"
  registered_at: datetime | None = None


@dataclass(frozen=True)
class StrategyMetadata:
  strategy_id: str
  name: str
  version: str
  runtime: str
  asset_types: tuple[AssetType, ...]
  supported_timeframes: tuple[str, ...]
  parameter_schema: dict[str, Any]
  description: str
  lifecycle: StrategyLifecycle = field(default_factory=StrategyLifecycle)
  version_lineage: tuple[str, ...] = ()
  reference_id: str | None = None
  reference_path: str | None = None
  entrypoint: str | None = None


@dataclass(frozen=True)
class SignalDecision:
  timestamp: datetime
  action: SignalAction
  size_fraction: float = 1.0
  confidence: float = 1.0
  tags: tuple[str, ...] = ()
  reason: str | None = None


@dataclass(frozen=True)
class ExecutionPlan:
  size_fraction: float = 1.0
  allow_scale_in: bool = False
  allow_partial_exit: bool = False
  reduce_only: bool = False
  max_position_fraction: float = 1.0
  stop_loss_pct: float | None = None
  take_profit_pct: float | None = None
  exit_mode: str | None = None
  tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategyExecutionState:
  timestamp: datetime
  instrument_id: str
  has_position: bool
  cash: float
  position_size: float
  parameters: dict[str, Any]


@dataclass(frozen=True)
class StrategyDecisionContext:
  timestamp: datetime
  instrument_id: str
  features: dict[str, Any]
  market: dict[str, Any]
  state: StrategyExecutionState


@dataclass(frozen=True)
class StrategyDecisionEnvelope:
  signal: SignalDecision
  rationale: str
  context: StrategyDecisionContext
  execution: ExecutionPlan = field(default_factory=ExecutionPlan)
  trace: dict[str, Any] = field(default_factory=dict)


@dataclass
class Order:
  run_id: str
  instrument_id: str
  side: OrderSide
  quantity: float
  requested_price: float
  order_type: OrderType = OrderType.MARKET
  status: OrderStatus = OrderStatus.OPEN
  order_id: str = field(default_factory=lambda: str(uuid4()))
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime | None = None
  filled_at: datetime | None = None
  average_fill_price: float | None = None
  fee_paid: float = 0.0
  filled_quantity: float = 0.0
  remaining_quantity: float | None = None
  last_synced_at: datetime | None = None


@dataclass(frozen=True)
class Fill:
  order_id: str
  quantity: float
  price: float
  fee_paid: float
  timestamp: datetime


@dataclass
class Position:
  instrument_id: str
  quantity: float = 0.0
  average_price: float = 0.0
  realized_pnl: float = 0.0
  opened_at: datetime | None = None
  updated_at: datetime | None = None

  @property
  def is_open(self) -> bool:
    return self.quantity > 0


@dataclass(frozen=True)
class ClosedTrade:
  instrument_id: str
  entry_price: float
  exit_price: float
  quantity: float
  fee_paid: float
  pnl: float
  opened_at: datetime
  closed_at: datetime


@dataclass(frozen=True)
class EquityPoint:
  timestamp: datetime
  equity: float
  cash: float
  exposure: float


@dataclass(frozen=True)
class RunConfig:
  run_id: str
  mode: RunMode
  strategy_id: str
  strategy_version: str
  venue: str
  symbols: tuple[str, ...]
  timeframe: str
  parameters: dict[str, Any]
  initial_cash: float
  fee_rate: float
  slippage_bps: float
  start_at: datetime | None = None
  end_at: datetime | None = None


@dataclass(frozen=True)
class MarketDataLineage:
  provider: str
  venue: str
  symbols: tuple[str, ...]
  timeframe: str
  dataset_identity: str | None = None
  sync_checkpoint_id: str | None = None
  reproducibility_state: str = "range_only"
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  effective_start_at: datetime | None = None
  effective_end_at: datetime | None = None
  candle_count: int = 0
  sync_status: str = "unknown"
  last_sync_at: datetime | None = None
  issues: tuple[str, ...] = ()


@dataclass
class RuntimeSessionState:
  session_id: str = field(default_factory=lambda: str(uuid4()))
  worker_kind: str = "sandbox_native_worker"
  lifecycle_state: str = "active"
  started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  primed_candle_count: int = 0
  processed_tick_count: int = 0
  last_heartbeat_at: datetime | None = None
  last_processed_candle_at: datetime | None = None
  last_seen_candle_at: datetime | None = None
  heartbeat_interval_seconds: int = 15
  heartbeat_timeout_seconds: int = 45
  recovery_count: int = 0
  last_recovered_at: datetime | None = None
  last_recovery_reason: str | None = None


@dataclass(frozen=True)
class StrategyParameterSnapshot:
  requested: dict[str, Any] = field(default_factory=dict)
  resolved: dict[str, Any] = field(default_factory=dict)
  schema: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategySnapshot:
  strategy_id: str
  name: str
  version: str
  runtime: str
  lifecycle: StrategyLifecycle = field(default_factory=StrategyLifecycle)
  version_lineage: tuple[str, ...] = ()
  parameter_snapshot: StrategyParameterSnapshot = field(default_factory=StrategyParameterSnapshot)
  supported_timeframes: tuple[str, ...] = ()
  warmup: WarmupSpec = field(default_factory=lambda: WarmupSpec(required_bars=0))
  reference_id: str | None = None
  reference_path: str | None = None
  entrypoint: str | None = None


@dataclass(frozen=True)
class BenchmarkArtifact:
  kind: str
  label: str
  path: str
  format: str | None = None
  exists: bool = True
  is_directory: bool = False
  summary: dict[str, Any] = field(default_factory=dict)
  sections: dict[str, Any] = field(default_factory=dict)
  summary_source_path: str | None = None


@dataclass
class RunProvenance:
  lane: str = "native"
  reference_id: str | None = None
  reference_version: str | None = None
  integration_mode: str | None = None
  reference: ReferenceSource | None = None
  working_directory: str | None = None
  external_command: tuple[str, ...] = ()
  artifact_paths: tuple[str, ...] = ()
  benchmark_artifacts: tuple[BenchmarkArtifact, ...] = ()
  strategy: StrategySnapshot | None = None
  rerun_boundary_id: str | None = None
  rerun_boundary_state: str = "range_only"
  rerun_source_run_id: str | None = None
  rerun_target_boundary_id: str | None = None
  rerun_match_status: str = "not_rerun"
  market_data: MarketDataLineage | None = None
  market_data_by_symbol: dict[str, MarketDataLineage] = field(default_factory=dict)
  runtime_session: RuntimeSessionState | None = None


@dataclass
class RunRecord:
  config: RunConfig
  status: RunStatus = RunStatus.PENDING
  started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  ended_at: datetime | None = None
  provenance: RunProvenance = field(default_factory=RunProvenance)
  orders: list[Order] = field(default_factory=list)
  fills: list[Fill] = field(default_factory=list)
  positions: dict[str, Position] = field(default_factory=dict)
  equity_curve: list[EquityPoint] = field(default_factory=list)
  closed_trades: list[ClosedTrade] = field(default_factory=list)
  metrics: dict[str, Any] = field(default_factory=dict)
  notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RunComparisonRun:
  run_id: str
  mode: str
  status: str
  lane: str
  strategy_id: str
  strategy_name: str | None
  strategy_version: str
  symbols: tuple[str, ...]
  timeframe: str
  started_at: datetime
  ended_at: datetime | None = None
  reference_id: str | None = None
  reference_version: str | None = None
  integration_mode: str | None = None
  reference: ReferenceSource | None = None
  working_directory: str | None = None
  rerun_boundary_id: str | None = None
  rerun_boundary_state: str = "range_only"
  external_command: tuple[str, ...] = ()
  artifact_paths: tuple[str, ...] = ()
  benchmark_artifacts: tuple[BenchmarkArtifact, ...] = ()
  metrics: dict[str, Any] = field(default_factory=dict)
  notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunComparisonMetricRow:
  key: str
  label: str
  unit: str
  higher_is_better: bool | None = None
  values: dict[str, float | int | None] = field(default_factory=dict)
  deltas_vs_baseline: dict[str, float | int | None] = field(default_factory=dict)
  delta_annotations: dict[str, str] = field(default_factory=dict)
  annotation: str | None = None
  best_run_id: str | None = None


@dataclass(frozen=True)
class RunComparisonNarrative:
  run_id: str
  baseline_run_id: str
  comparison_type: str
  title: str
  summary: str
  bullets: tuple[str, ...] = ()
  rank: int = 0
  insight_score: float = 0.0
  is_primary: bool = False


@dataclass(frozen=True)
class RunComparison:
  requested_run_ids: tuple[str, ...]
  baseline_run_id: str
  runs: tuple[RunComparisonRun, ...]
  metric_rows: tuple[RunComparisonMetricRow, ...]
  intent: str = "benchmark_validation"
  narratives: tuple[RunComparisonNarrative, ...] = ()


@dataclass(frozen=True)
class InstrumentStatus:
  instrument_id: str
  timeframe: str
  candle_count: int
  first_timestamp: datetime | None
  last_timestamp: datetime | None
  sync_status: str = "empty"
  lag_seconds: int | None = None
  last_sync_at: datetime | None = None
  sync_checkpoint: "SyncCheckpoint" | None = None
  recent_failures: tuple["SyncFailure", ...] = ()
  failure_count_24h: int = 0
  backfill_target_candles: int | None = None
  backfill_completion_ratio: float | None = None
  backfill_complete: bool | None = None
  backfill_contiguous_completion_ratio: float | None = None
  backfill_contiguous_complete: bool | None = None
  backfill_contiguous_missing_candles: int | None = None
  backfill_gap_windows: tuple["GapWindow", ...] = ()
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataStatus:
  provider: str
  venue: str
  instruments: list[InstrumentStatus]


@dataclass(frozen=True)
class OperatorAlert:
  alert_id: str
  severity: str
  category: str
  summary: str
  detail: str
  detected_at: datetime
  run_id: str | None = None
  session_id: str | None = None
  status: str = "active"
  resolved_at: datetime | None = None
  source: str = "runtime"
  delivery_targets: tuple[str, ...] = ()


@dataclass(frozen=True)
class OperatorAuditEvent:
  event_id: str
  timestamp: datetime
  actor: str
  kind: str
  summary: str
  detail: str
  run_id: str | None = None
  session_id: str | None = None
  source: str = "runtime"


@dataclass(frozen=True)
class OperatorIncidentRemediation:
  state: str = "not_applicable"
  kind: str | None = None
  owner: str | None = None
  summary: str | None = None
  detail: str | None = None
  runbook: str | None = None
  requested_at: datetime | None = None
  requested_by: str | None = None
  last_attempted_at: datetime | None = None
  provider: str | None = None
  reference: str | None = None
  provider_payload: dict[str, Any] = field(default_factory=dict)
  provider_payload_updated_at: datetime | None = None
  provider_recovery: "OperatorIncidentProviderRecoveryState" = field(
    default_factory=lambda: OperatorIncidentProviderRecoveryState()
  )


@dataclass(frozen=True)
class OperatorIncidentProviderRecoveryVerification:
  state: str = "unknown"
  checked_at: datetime | None = None
  summary: str | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class OperatorIncidentProviderRecoveryStatusMachine:
  state: str = "not_requested"
  workflow_state: str = "idle"
  workflow_action: str | None = None
  job_state: str = "not_started"
  sync_state: str = "not_synced"
  last_event_kind: str | None = None
  last_event_at: datetime | None = None
  last_detail: str | None = None
  attempt_number: int = 0


@dataclass(frozen=True)
class OperatorIncidentProviderRecoveryTelemetry:
  source: str = "unknown"
  state: str = "unknown"
  progress_percent: int | None = None
  attempt_count: int = 0
  current_step: str | None = None
  last_message: str | None = None
  last_error: str | None = None
  external_run_id: str | None = None
  job_url: str | None = None
  started_at: datetime | None = None
  finished_at: datetime | None = None
  updated_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentPagerDutyRecoveryState:
  incident_id: str | None = None
  incident_key: str | None = None
  incident_status: str = "unknown"
  urgency: str | None = None
  service_id: str | None = None
  service_summary: str | None = None
  escalation_policy_id: str | None = None
  escalation_policy_summary: str | None = None
  html_url: str | None = None
  last_status_change_at: datetime | None = None
  phase_graph: "OperatorIncidentPagerDutyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentPagerDutyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentPagerDutyRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  responder_phase: str = "unknown"
  urgency_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOpsgenieRecoveryState:
  alert_id: str | None = None
  alias: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  owner: str | None = None
  acknowledged: bool | None = None
  seen: bool | None = None
  tiny_id: str | None = None
  teams: tuple[str, ...] = ()
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOpsgenieRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOpsgenieRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOpsgenieRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  acknowledgment_phase: str = "unknown"
  ownership_phase: str = "unknown"
  visibility_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIncidentIoRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  mode: str | None = None
  visibility: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIncidentIoRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIncidentIoRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIncidentIoRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  assignment_phase: str = "unknown"
  visibility_phase: str = "unknown"
  severity_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFireHydrantRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  priority: str | None = None
  team: str | None = None
  runbook: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFireHydrantRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFireHydrantRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFireHydrantRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  priority_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentRootlyRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity_id: str | None = None
  private: bool | None = None
  slug: str | None = None
  url: str | None = None
  acknowledged_at: datetime | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentRootlyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentRootlyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentRootlyRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  acknowledgment_phase: str = "unknown"
  visibility_phase: str = "unknown"
  severity_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBlamelessRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  commander: str | None = None
  visibility: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBlamelessRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBlamelessRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBlamelessRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  command_phase: str = "unknown"
  visibility_phase: str = "unknown"
  severity_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentXmattersRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  assignee: str | None = None
  response_plan: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentXmattersRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentXmattersRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentXmattersRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  response_plan_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentServicenowRecoveryState:
  incident_number: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  assigned_to: str | None = None
  assignment_group: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentServicenowRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentServicenowRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentServicenowRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  assignment_phase: str = "unknown"
  priority_phase: str = "unknown"
  group_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSquadcastRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  escalation_policy: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSquadcastRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSquadcastRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSquadcastRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBigPandaRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  team: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBigPandaRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBigPandaRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBigPandaRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  team_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentGrafanaOnCallRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  escalation_chain: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentGrafanaOnCallRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentGrafanaOnCallRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentGrafanaOnCallRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentZendutyRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  service: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentZendutyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentZendutyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentZendutyRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  service_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSplunkOnCallRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  routing_key: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSplunkOnCallRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSplunkOnCallRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSplunkOnCallRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  routing_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentJiraServiceManagementRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  assignee: str | None = None
  service_project: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentJiraServiceManagementRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentJiraServiceManagementRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentJiraServiceManagementRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  assignment_phase: str = "unknown"
  priority_phase: str = "unknown"
  project_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentPagerTreeRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  urgency: str | None = None
  assignee: str | None = None
  team: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentPagerTreeRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentPagerTreeRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentPagerTreeRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  urgency_phase: str = "unknown"
  team_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentAlertOpsRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  owner: str | None = None
  service: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentAlertOpsRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentAlertOpsRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentAlertOpsRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  service_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSignl4RecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  team: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSignl4RecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSignl4RecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSignl4RecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  team_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIlertRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIlertRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIlertRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIlertRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBetterstackRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBetterstackRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBetterstackRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBetterstackRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOnpageRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOnpageRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOnpageRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOnpageRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentAllquietRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentAllquietRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentAllquietRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentAllquietRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentMoogsoftRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentMoogsoftRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentMoogsoftRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentMoogsoftRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSpikeshRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSpikeshRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSpikeshRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSpikeshRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentDutyCallsRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentDutyCallsRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentDutyCallsRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentDutyCallsRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIncidentHubRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIncidentHubRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIncidentHubRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIncidentHubRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentResolverRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentResolverRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentResolverRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentResolverRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOpenDutyRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOpenDutyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOpenDutyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOpenDutyRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentCabotRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentCabotRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentCabotRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentCabotRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOpsRampRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOpsRampRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOpsRampRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOpsRampRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentProviderRecoveryState:
  lifecycle_state: str = "not_synced"
  provider: str | None = None
  job_id: str | None = None
  reference: str | None = None
  workflow_reference: str | None = None
  summary: str | None = None
  detail: str | None = None
  channels: tuple[str, ...] = ()
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  verification: OperatorIncidentProviderRecoveryVerification = field(
    default_factory=OperatorIncidentProviderRecoveryVerification
  )
  telemetry: OperatorIncidentProviderRecoveryTelemetry = field(
    default_factory=OperatorIncidentProviderRecoveryTelemetry
  )
  status_machine: OperatorIncidentProviderRecoveryStatusMachine = field(
    default_factory=OperatorIncidentProviderRecoveryStatusMachine
  )
  provider_schema_kind: str | None = None
  pagerduty: OperatorIncidentPagerDutyRecoveryState = field(
    default_factory=OperatorIncidentPagerDutyRecoveryState
  )
  opsgenie: OperatorIncidentOpsgenieRecoveryState = field(
    default_factory=OperatorIncidentOpsgenieRecoveryState
  )
  incidentio: OperatorIncidentIncidentIoRecoveryState = field(
    default_factory=OperatorIncidentIncidentIoRecoveryState
  )
  firehydrant: OperatorIncidentFireHydrantRecoveryState = field(
    default_factory=OperatorIncidentFireHydrantRecoveryState
  )
  rootly: OperatorIncidentRootlyRecoveryState = field(
    default_factory=OperatorIncidentRootlyRecoveryState
  )
  blameless: OperatorIncidentBlamelessRecoveryState = field(
    default_factory=OperatorIncidentBlamelessRecoveryState
  )
  xmatters: OperatorIncidentXmattersRecoveryState = field(
    default_factory=OperatorIncidentXmattersRecoveryState
  )
  servicenow: OperatorIncidentServicenowRecoveryState = field(
    default_factory=OperatorIncidentServicenowRecoveryState
  )
  squadcast: OperatorIncidentSquadcastRecoveryState = field(
    default_factory=OperatorIncidentSquadcastRecoveryState
  )
  bigpanda: OperatorIncidentBigPandaRecoveryState = field(
    default_factory=OperatorIncidentBigPandaRecoveryState
  )
  grafana_oncall: OperatorIncidentGrafanaOnCallRecoveryState = field(
    default_factory=OperatorIncidentGrafanaOnCallRecoveryState
  )
  zenduty: OperatorIncidentZendutyRecoveryState = field(
    default_factory=OperatorIncidentZendutyRecoveryState
  )
  splunk_oncall: OperatorIncidentSplunkOnCallRecoveryState = field(
    default_factory=OperatorIncidentSplunkOnCallRecoveryState
  )
  jira_service_management: OperatorIncidentJiraServiceManagementRecoveryState = field(
    default_factory=OperatorIncidentJiraServiceManagementRecoveryState
  )
  pagertree: OperatorIncidentPagerTreeRecoveryState = field(
    default_factory=OperatorIncidentPagerTreeRecoveryState
  )
  alertops: OperatorIncidentAlertOpsRecoveryState = field(
    default_factory=OperatorIncidentAlertOpsRecoveryState
  )
  signl4: OperatorIncidentSignl4RecoveryState = field(
    default_factory=OperatorIncidentSignl4RecoveryState
  )
  ilert: OperatorIncidentIlertRecoveryState = field(
    default_factory=OperatorIncidentIlertRecoveryState
  )
  betterstack: OperatorIncidentBetterstackRecoveryState = field(
    default_factory=OperatorIncidentBetterstackRecoveryState
  )
  onpage: OperatorIncidentOnpageRecoveryState = field(
    default_factory=OperatorIncidentOnpageRecoveryState
  )
  allquiet: OperatorIncidentAllquietRecoveryState = field(
    default_factory=OperatorIncidentAllquietRecoveryState
  )
  moogsoft: OperatorIncidentMoogsoftRecoveryState = field(
    default_factory=OperatorIncidentMoogsoftRecoveryState
  )
  spikesh: OperatorIncidentSpikeshRecoveryState = field(
    default_factory=OperatorIncidentSpikeshRecoveryState
  )
  dutycalls: OperatorIncidentDutyCallsRecoveryState = field(
    default_factory=OperatorIncidentDutyCallsRecoveryState
  )
  incidenthub: OperatorIncidentIncidentHubRecoveryState = field(
    default_factory=OperatorIncidentIncidentHubRecoveryState
  )
  resolver: OperatorIncidentResolverRecoveryState = field(
    default_factory=OperatorIncidentResolverRecoveryState
  )
  openduty: OperatorIncidentOpenDutyRecoveryState = field(
    default_factory=OperatorIncidentOpenDutyRecoveryState
  )
  cabot: OperatorIncidentCabotRecoveryState = field(
    default_factory=OperatorIncidentCabotRecoveryState
  )
  opsramp: OperatorIncidentOpsRampRecoveryState = field(
    default_factory=OperatorIncidentOpsRampRecoveryState
  )
  updated_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentProviderPullSync:
  provider: str
  workflow_reference: str | None = None
  external_reference: str | None = None
  workflow_state: str = "unknown"
  remediation_state: str | None = None
  detail: str | None = None
  payload: dict[str, Any] = field(default_factory=dict)
  synced_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class OperatorIncidentEvent:
  event_id: str
  alert_id: str
  timestamp: datetime
  kind: str
  severity: str
  summary: str
  detail: str
  run_id: str | None = None
  session_id: str | None = None
  source: str = "guarded_live"
  paging_policy_id: str = "default"
  paging_provider: str | None = None
  delivery_targets: tuple[str, ...] = ()
  escalation_targets: tuple[str, ...] = ()
  delivery_state: str = "pending"
  acknowledgment_state: str = "not_applicable"
  acknowledged_at: datetime | None = None
  acknowledged_by: str | None = None
  acknowledgment_reason: str | None = None
  escalation_level: int = 0
  escalation_state: str = "not_applicable"
  last_escalated_at: datetime | None = None
  last_escalated_by: str | None = None
  escalation_reason: str | None = None
  next_escalation_at: datetime | None = None
  external_provider: str | None = None
  external_reference: str | None = None
  provider_workflow_reference: str | None = None
  external_status: str = "not_synced"
  external_last_synced_at: datetime | None = None
  paging_status: str = "not_configured"
  provider_workflow_state: str = "not_configured"
  provider_workflow_action: str | None = None
  provider_workflow_last_attempted_at: datetime | None = None
  remediation: OperatorIncidentRemediation = field(default_factory=OperatorIncidentRemediation)


@dataclass(frozen=True)
class OperatorIncidentDelivery:
  delivery_id: str
  incident_event_id: str
  alert_id: str
  incident_kind: str
  target: str
  status: str
  attempted_at: datetime
  detail: str
  attempt_number: int = 1
  next_retry_at: datetime | None = None
  phase: str = "initial"
  provider_action: str | None = None
  external_provider: str | None = None
  external_reference: str | None = None
  source: str = "guarded_live"


@dataclass(frozen=True)
class OperatorVisibility:
  generated_at: datetime
  alerts: tuple[OperatorAlert, ...] = ()
  alert_history: tuple[OperatorAlert, ...] = ()
  incident_events: tuple[OperatorIncidentEvent, ...] = ()
  delivery_history: tuple[OperatorIncidentDelivery, ...] = ()
  audit_events: tuple[OperatorAuditEvent, ...] = ()


@dataclass(frozen=True)
class GuardedLiveKillSwitch:
  state: str = "released"
  reason: str = "Guarded-live kill switch is released."
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_by: str = "system"
  activation_count: int = 0
  last_engaged_at: datetime | None = None
  last_released_at: datetime | None = None


@dataclass(frozen=True)
class GuardedLiveReconciliationFinding:
  kind: str
  severity: str
  summary: str
  detail: str


@dataclass(frozen=True)
class GuardedLiveInternalExposure:
  run_id: str
  mode: str
  instrument_id: str
  quantity: float


@dataclass(frozen=True)
class GuardedLiveInternalStateSnapshot:
  captured_at: datetime
  running_run_ids: tuple[str, ...] = ()
  exposures: tuple[GuardedLiveInternalExposure, ...] = ()
  open_order_count: int = 0


@dataclass(frozen=True)
class GuardedLiveVenueBalance:
  asset: str
  total: float
  free: float | None = None
  used: float | None = None


@dataclass(frozen=True)
class GuardedLiveVenueOpenOrder:
  order_id: str
  symbol: str
  side: str
  amount: float
  status: str
  price: float | None = None


@dataclass(frozen=True)
class GuardedLiveOrderBookLevel:
  price: float
  quantity: float


@dataclass(frozen=True)
class GuardedLiveTradeChannelSnapshot:
  event_id: str | None = None
  price: float | None = None
  quantity: float | None = None
  event_at: datetime | None = None


@dataclass(frozen=True)
class GuardedLiveBookTickerChannelSnapshot:
  bid_price: float | None = None
  bid_quantity: float | None = None
  ask_price: float | None = None
  ask_quantity: float | None = None
  event_at: datetime | None = None


@dataclass(frozen=True)
class GuardedLiveMiniTickerChannelSnapshot:
  open_price: float | None = None
  close_price: float | None = None
  high_price: float | None = None
  low_price: float | None = None
  base_volume: float | None = None
  quote_volume: float | None = None
  event_at: datetime | None = None


@dataclass(frozen=True)
class GuardedLiveKlineChannelSnapshot:
  timeframe: str | None = None
  open_at: datetime | None = None
  close_at: datetime | None = None
  open_price: float | None = None
  high_price: float | None = None
  low_price: float | None = None
  close_price: float | None = None
  volume: float | None = None
  closed: bool = False
  event_at: datetime | None = None


@dataclass(frozen=True)
class GuardedLiveVenueOrderRequest:
  run_id: str
  session_id: str
  venue: str
  symbol: str
  side: str
  amount: float
  order_type: str = "market"
  reference_price: float | None = None


@dataclass(frozen=True)
class GuardedLiveVenueOrderResult:
  order_id: str
  venue: str
  symbol: str
  side: str
  amount: float
  status: str
  submitted_at: datetime
  updated_at: datetime | None = None
  requested_price: float | None = None
  average_fill_price: float | None = None
  fee_paid: float | None = None
  requested_amount: float | None = None
  filled_amount: float | None = None
  remaining_amount: float | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardedLiveVenueStateSnapshot:
  provider: str
  venue: str
  verification_state: str = "unavailable"
  captured_at: datetime | None = None
  balances: tuple[GuardedLiveVenueBalance, ...] = ()
  open_orders: tuple[GuardedLiveVenueOpenOrder, ...] = ()
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardedLiveRecoveredExposure:
  instrument_id: str
  symbol: str
  asset: str
  quantity: float


@dataclass(frozen=True)
class GuardedLiveRuntimeRecovery:
  state: str = "not_recovered"
  recovered_at: datetime | None = None
  recovered_by: str | None = None
  reason: str | None = None
  source_snapshot_at: datetime | None = None
  source_verification_state: str = "unavailable"
  summary: str = "Guarded-live runtime state has not been recovered from venue snapshots."
  exposures: tuple[GuardedLiveRecoveredExposure, ...] = ()
  open_orders: tuple[GuardedLiveVenueOpenOrder, ...] = ()
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardedLiveSessionOwnership:
  state: str = "unclaimed"
  owner_run_id: str | None = None
  owner_session_id: str | None = None
  symbol: str | None = None
  claimed_at: datetime | None = None
  claimed_by: str | None = None
  last_heartbeat_at: datetime | None = None
  last_order_sync_at: datetime | None = None
  last_resumed_at: datetime | None = None
  last_reason: str | None = None
  last_released_at: datetime | None = None


@dataclass(frozen=True)
class GuardedLiveOrderBookSync:
  state: str = "empty"
  synced_at: datetime | None = None
  owner_run_id: str | None = None
  owner_session_id: str | None = None
  symbol: str | None = None
  open_orders: tuple[GuardedLiveVenueOpenOrder, ...] = ()
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardedLiveVenueSessionRestore:
  state: str = "not_restored"
  restored_at: datetime | None = None
  source: str = "none"
  venue: str | None = None
  symbol: str | None = None
  timeframe: str | None = None
  owner_run_id: str | None = None
  owner_session_id: str | None = None
  open_orders: tuple[GuardedLiveVenueOpenOrder, ...] = ()
  synced_orders: tuple[GuardedLiveVenueOrderResult, ...] = ()
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardedLiveVenueSessionHandoff:
  state: str = "inactive"
  handed_off_at: datetime | None = None
  released_at: datetime | None = None
  source: str = "none"
  venue: str | None = None
  symbol: str | None = None
  timeframe: str | None = None
  owner_run_id: str | None = None
  owner_session_id: str | None = None
  venue_session_id: str | None = None
  transport: str = "none"
  cursor: str | None = None
  last_event_at: datetime | None = None
  last_sync_at: datetime | None = None
  supervision_state: str = "inactive"
  failover_count: int = 0
  last_failover_at: datetime | None = None
  coverage: tuple[str, ...] = ()
  order_book_state: str = "inactive"
  order_book_last_update_id: int | None = None
  order_book_gap_count: int = 0
  order_book_rebuild_count: int = 0
  order_book_last_rebuilt_at: datetime | None = None
  order_book_bid_level_count: int = 0
  order_book_ask_level_count: int = 0
  order_book_best_bid_price: float | None = None
  order_book_best_bid_quantity: float | None = None
  order_book_best_ask_price: float | None = None
  order_book_best_ask_quantity: float | None = None
  order_book_bids: tuple[GuardedLiveOrderBookLevel, ...] = ()
  order_book_asks: tuple[GuardedLiveOrderBookLevel, ...] = ()
  channel_restore_state: str = "inactive"
  channel_restore_count: int = 0
  channel_last_restored_at: datetime | None = None
  channel_continuation_state: str = "inactive"
  channel_continuation_count: int = 0
  channel_last_continued_at: datetime | None = None
  trade_snapshot: GuardedLiveTradeChannelSnapshot | None = None
  aggregate_trade_snapshot: GuardedLiveTradeChannelSnapshot | None = None
  book_ticker_snapshot: GuardedLiveBookTickerChannelSnapshot | None = None
  mini_ticker_snapshot: GuardedLiveMiniTickerChannelSnapshot | None = None
  kline_snapshot: GuardedLiveKlineChannelSnapshot | None = None
  last_market_event_at: datetime | None = None
  last_depth_event_at: datetime | None = None
  last_kline_event_at: datetime | None = None
  last_aggregate_trade_event_at: datetime | None = None
  last_mini_ticker_event_at: datetime | None = None
  last_account_event_at: datetime | None = None
  last_balance_event_at: datetime | None = None
  last_order_list_event_at: datetime | None = None
  last_trade_event_at: datetime | None = None
  last_book_ticker_event_at: datetime | None = None
  active_order_count: int = 0
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardedLiveVenueSessionSync:
  state: str = "inactive"
  synced_at: datetime | None = None
  handoff: GuardedLiveVenueSessionHandoff = field(default_factory=GuardedLiveVenueSessionHandoff)
  synced_orders: tuple[GuardedLiveVenueOrderResult, ...] = ()
  open_orders: tuple[GuardedLiveVenueOpenOrder, ...] = ()
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardedLiveReconciliation:
  state: str = "not_started"
  checked_at: datetime | None = None
  checked_by: str | None = None
  scope: str = "venue_state"
  summary: str = "No guarded-live reconciliation has run yet."
  findings: tuple[GuardedLiveReconciliationFinding, ...] = ()
  internal_snapshot: GuardedLiveInternalStateSnapshot | None = None
  venue_snapshot: GuardedLiveVenueStateSnapshot | None = None


@dataclass(frozen=True)
class GuardedLiveState:
  kill_switch: GuardedLiveKillSwitch = field(default_factory=GuardedLiveKillSwitch)
  reconciliation: GuardedLiveReconciliation = field(default_factory=GuardedLiveReconciliation)
  recovery: GuardedLiveRuntimeRecovery = field(default_factory=GuardedLiveRuntimeRecovery)
  ownership: GuardedLiveSessionOwnership = field(default_factory=GuardedLiveSessionOwnership)
  order_book: GuardedLiveOrderBookSync = field(default_factory=GuardedLiveOrderBookSync)
  session_restore: GuardedLiveVenueSessionRestore = field(default_factory=GuardedLiveVenueSessionRestore)
  session_handoff: GuardedLiveVenueSessionHandoff = field(default_factory=GuardedLiveVenueSessionHandoff)
  alert_history: tuple[OperatorAlert, ...] = ()
  incident_events: tuple[OperatorIncidentEvent, ...] = ()
  delivery_history: tuple[OperatorIncidentDelivery, ...] = ()
  audit_events: tuple[OperatorAuditEvent, ...] = ()


@dataclass(frozen=True)
class GuardedLiveStatus:
  generated_at: datetime
  candidacy_status: str
  blockers: tuple[str, ...] = ()
  active_alerts: tuple[OperatorAlert, ...] = ()
  alert_history: tuple[OperatorAlert, ...] = ()
  incident_events: tuple[OperatorIncidentEvent, ...] = ()
  delivery_history: tuple[OperatorIncidentDelivery, ...] = ()
  kill_switch: GuardedLiveKillSwitch = field(default_factory=GuardedLiveKillSwitch)
  reconciliation: GuardedLiveReconciliation = field(default_factory=GuardedLiveReconciliation)
  recovery: GuardedLiveRuntimeRecovery = field(default_factory=GuardedLiveRuntimeRecovery)
  ownership: GuardedLiveSessionOwnership = field(default_factory=GuardedLiveSessionOwnership)
  order_book: GuardedLiveOrderBookSync = field(default_factory=GuardedLiveOrderBookSync)
  session_restore: GuardedLiveVenueSessionRestore = field(default_factory=GuardedLiveVenueSessionRestore)
  session_handoff: GuardedLiveVenueSessionHandoff = field(default_factory=GuardedLiveVenueSessionHandoff)
  audit_events: tuple[OperatorAuditEvent, ...] = ()
  active_runtime_alert_count: int = 0
  running_sandbox_count: int = 0
  running_paper_count: int = 0
  running_live_count: int = 0


@dataclass(frozen=True)
class GapWindow:
  start_at: datetime
  end_at: datetime
  missing_candles: int


@dataclass(frozen=True)
class SyncCheckpoint:
  checkpoint_id: str
  recorded_at: datetime
  candle_count: int
  first_timestamp: datetime | None = None
  last_timestamp: datetime | None = None
  contiguous_missing_candles: int = 0


@dataclass(frozen=True)
class SyncFailure:
  failed_at: datetime
  operation: str
  error: str


@dataclass(frozen=True)
class MarketDataRemediationResult:
  kind: str
  symbol: str
  timeframe: str
  status: str
  started_at: datetime
  finished_at: datetime
  detail: str


@dataclass(frozen=True)
class StrategyRegistration:
  strategy_id: str
  module_path: str
  class_name: str
  registered_at: datetime
