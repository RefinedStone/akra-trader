from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC
from datetime import datetime
from enum import Enum
import hashlib
from typing import Any
from uuid import uuid4


BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY = "__runtime_candidate_id"
BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_SOURCE_KEYS = (
  BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY,
  "runtime_candidate_id",
  "native_runtime_candidate_id",
  "native_candidate_id",
)


def extract_benchmark_artifact_runtime_candidate_id(value: Any) -> str | None:
  if not isinstance(value, dict):
    return None
  for key in BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_SOURCE_KEYS:
    candidate_value = value.get(key)
    if isinstance(candidate_value, str) and candidate_value.strip():
      return candidate_value.strip()
  return None


def is_benchmark_artifact_metadata_key(key: str) -> bool:
  return key in BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_SOURCE_KEYS


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
class StrategyCatalogSemantics:
  strategy_kind: str = "standard"
  execution_model: str = ""
  parameter_contract: str = ""
  source_descriptor: str | None = None
  operator_notes: tuple[str, ...] = ()


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
  catalog_semantics: StrategyCatalogSemantics = field(default_factory=StrategyCatalogSemantics)
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
class DatasetBoundaryContract:
  contract_version: str = "dataset_boundary.v1"
  provider: str = "unknown"
  venue: str = ""
  symbols: tuple[str, ...] = ()
  timeframe: str = ""
  reproducibility_state: str = "range_only"
  validation_claim: str = "window_only"
  boundary_id: str | None = None
  dataset_identity: str | None = None
  sync_checkpoint_id: str | None = None
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  effective_start_at: datetime | None = None
  effective_end_at: datetime | None = None
  candle_count: int = 0


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
  catalog_semantics: StrategyCatalogSemantics = field(default_factory=StrategyCatalogSemantics)
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
  source_locations: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentPreset:
  @dataclass(frozen=True)
  class Revision:
    revision_id: str
    actor: str
    reason: str
    created_at: datetime
    action: str = "updated"
    source_revision_id: str | None = None
    name: str = ""
    description: str = ""
    strategy_id: str | None = None
    timeframe: str | None = None
    benchmark_family: str | None = None
    tags: tuple[str, ...] = ()
    parameters: dict[str, Any] = field(default_factory=dict)

  @dataclass(frozen=True)
  class LifecycleEvent:
    action: str
    actor: str
    reason: str
    occurred_at: datetime
    from_stage: str | None = None
    to_stage: str = "draft"

  @dataclass(frozen=True)
  class Lifecycle:
    stage: str = "draft"
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_by: str = "operator"
    last_action: str = "created"
    history: tuple["ExperimentPreset.LifecycleEvent", ...] = ()

  preset_id: str
  name: str
  description: str = ""
  strategy_id: str | None = None
  timeframe: str | None = None
  benchmark_family: str | None = None
  tags: tuple[str, ...] = ()
  parameters: dict[str, Any] = field(default_factory=dict)
  lifecycle: "ExperimentPreset.Lifecycle" = field(
    default_factory=lambda: ExperimentPreset.Lifecycle()
  )
  revisions: tuple["ExperimentPreset.Revision", ...] = ()
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class RunExperimentMetadata:
  tags: tuple[str, ...] = ()
  preset_id: str | None = None
  benchmark_family: str | None = None


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
  rerun_validation_category: str = "not_rerun"
  rerun_validation_summary: str | None = None
  market_data: MarketDataLineage | None = None
  market_data_by_symbol: dict[str, MarketDataLineage] = field(default_factory=dict)
  runtime_session: RuntimeSessionState | None = None
  experiment: RunExperimentMetadata = field(default_factory=RunExperimentMetadata)


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
  catalog_semantics: StrategyCatalogSemantics = field(default_factory=StrategyCatalogSemantics)
  ended_at: datetime | None = None
  reference_id: str | None = None
  reference_version: str | None = None
  integration_mode: str | None = None
  reference: ReferenceSource | None = None
  working_directory: str | None = None
  rerun_boundary_id: str | None = None
  rerun_boundary_state: str = "range_only"
  dataset_identity: str | None = None
  experiment: RunExperimentMetadata = field(default_factory=RunExperimentMetadata)
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
class ComparisonEligibilitySurfaceContract:
  eligibility: str
  group: str
  label: str


@dataclass(frozen=True)
class ComparisonEligibilityGroupContract:
  copy: str
  eligibility: str
  surface_ids: tuple[str, ...]
  title: str


@dataclass(frozen=True)
class ComparisonEligibilityContract:
  scope: str = "run_list"
  surfaces: dict[str, ComparisonEligibilitySurfaceContract] = field(default_factory=dict)
  groups: dict[str, ComparisonEligibilityGroupContract] = field(default_factory=dict)


def default_comparison_eligibility_contract() -> ComparisonEligibilityContract:
  return ComparisonEligibilityContract(
    scope="run_list",
    surfaces={
      "cancel_order": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_order_actions",
        label="Cancel order",
      ),
      "compare_toggle": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_workflow",
        label="Add/remove compare",
      ),
      "drawdown": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Drawdown",
      ),
      "lane": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Lane",
      ),
      "lifecycle": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Lifecycle",
      ),
      "mode": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Mode",
      ),
      "replace_order": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_order_actions",
        label="Replace order",
      ),
      "rerun": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_workflow",
        label="Rerun",
      ),
      "return": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Return",
      ),
      "stop": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_workflow",
        label="Stop",
      ),
      "trades": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Trades",
      ),
      "version": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Version",
      ),
      "win_rate": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Win rate",
      ),
    },
    groups={
      "eligible_metrics": ComparisonEligibilityGroupContract(
        copy=(
          "These surfaces participate in comparison scoring or drill-back, so they remain "
          "comparison-eligible."
        ),
        eligibility="eligible",
        surface_ids=("return", "drawdown", "win_rate", "trades"),
        title="Comparison-eligible",
      ),
      "operational_order_actions": ComparisonEligibilityGroupContract(
        copy=(
          "Replace and cancel actions mutate order state, so they stay outside comparison "
          "drill-back even when the preview rows are comparison-eligible."
        ),
        eligibility="operational",
        surface_ids=("cancel_order", "replace_order"),
        title="Operational only",
      ),
      "operational_workflow": ComparisonEligibilityGroupContract(
        copy=(
          "Workflow controls change selection or execution state, so they remain outside "
          "comparison-eligible deep-link scope."
        ),
        eligibility="operational",
        surface_ids=("compare_toggle", "rerun", "stop"),
        title="Operational only",
      ),
      "supporting_identity": ComparisonEligibilityGroupContract(
        copy=(
          "Weak-signal identity and routing context stay descriptive only and do not create "
          "comparison deep-links."
        ),
        eligibility="supporting",
        surface_ids=("mode", "lane", "lifecycle", "version"),
        title="Supporting only",
      ),
    },
  )


@dataclass(frozen=True)
class RunSurfaceCapabilities:
  @dataclass(frozen=True)
  class Policy:
    applies_to: tuple[str, ...] = ()
    policy_key: str = ""
    policy_mode: str = ""
    source_of_truth: str = ""

  @dataclass(frozen=True)
  class Enforcement:
    enforcement_points: tuple[str, ...] = ()
    fallback_behavior: str = ""
    level: str = ""
    source_of_truth: str = ""

  @dataclass(frozen=True)
  class SurfaceRule:
    rule_key: str = ""
    surface_key: str = ""
    surface_label: str = ""
    enforcement_point: str = ""
    enforcement_mode: str = ""
    level: str = ""
    fallback_behavior: str = ""
    source_of_truth: str = ""

  comparison_eligibility_contract: ComparisonEligibilityContract = field(
    default_factory=default_comparison_eligibility_contract
  )
  shared_contracts: tuple["RunSurfaceSharedContract", ...] = field(
    default_factory=lambda: default_run_surface_shared_contracts()
  )


@dataclass(frozen=True)
class RunSurfaceSharedContract:
  contract_key: str
  contract_kind: str
  title: str
  summary: str
  source_of_truth: str
  version: str | None = None
  discovery_flow: str | None = None
  related_family_keys: tuple[str, ...] = ()
  member_keys: tuple[str, ...] = ()
  ui_surfaces: tuple[str, ...] = ()
  schema_sources: tuple[str, ...] = ()
  policy: RunSurfaceCapabilities.Policy | None = None
  enforcement: RunSurfaceCapabilities.Enforcement | None = None
  surface_rules: tuple[RunSurfaceCapabilities.SurfaceRule, ...] = ()
  schema_detail: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReplayIntentAliasRecord:
  alias_id: str
  signature: str
  template_key: str
  template_label: str
  intent: dict[str, Any]
  redaction_policy: str
  retention_policy: str
  created_at: datetime
  expires_at: datetime | None = None
  revoked_at: datetime | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  revoked_by_tab_id: str | None = None
  revoked_by_tab_label: str | None = None


@dataclass(frozen=True)
class ReplayIntentAliasAuditRecord:
  audit_id: str
  alias_id: str
  action: str
  template_key: str
  template_label: str
  redaction_policy: str
  retention_policy: str
  recorded_at: datetime
  expires_at: datetime | None = None
  alias_created_at: datetime | None = None
  alias_expires_at: datetime | None = None
  alias_revoked_at: datetime | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ReplayIntentAliasAuditExportJobRecord:
  job_id: str
  export_format: str
  filename: str
  content_type: str
  record_count: int
  status: str
  created_at: datetime
  completed_at: datetime | None = None
  expires_at: datetime | None = None
  template_key: str | None = None
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None
  filters: dict[str, Any] = field(default_factory=dict)
  artifact_id: str | None = None
  content_length: int = 0
  content: str = ""


@dataclass(frozen=True)
class ReplayIntentAliasAuditExportArtifactRecord:
  artifact_id: str
  job_id: str
  filename: str
  content_type: str
  content: str
  created_at: datetime
  expires_at: datetime | None = None
  byte_length: int = 0


@dataclass(frozen=True)
class ReplayIntentAliasAuditExportJobAuditRecord:
  audit_id: str
  job_id: str
  action: str
  recorded_at: datetime
  expires_at: datetime | None = None
  template_key: str | None = None
  export_format: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ProviderProvenanceExportJobRecord:
  job_id: str
  export_scope: str
  export_format: str
  filename: str
  content_type: str
  status: str
  created_at: datetime
  completed_at: datetime | None = None
  exported_at: datetime | None = None
  expires_at: datetime | None = None
  focus_key: str | None = None
  focus_label: str | None = None
  market_data_provider: str | None = None
  venue: str | None = None
  symbol: str | None = None
  timeframe: str | None = None
  result_count: int = 0
  provider_provenance_count: int = 0
  provider_labels: tuple[str, ...] = ()
  vendor_fields: tuple[str, ...] = ()
  filter_summary: str | None = None
  filters: dict[str, Any] = field(default_factory=dict)
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None
  available_delivery_targets: tuple[str, ...] = ()
  routing_policy_id: str | None = None
  routing_policy_summary: str | None = None
  routing_targets: tuple[str, ...] = ()
  approval_policy_id: str | None = None
  approval_required: bool = False
  approval_state: str = "not_required"
  approval_summary: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approval_note: str | None = None
  escalation_count: int = 0
  last_escalated_at: datetime | None = None
  last_escalated_by: str | None = None
  last_escalation_reason: str | None = None
  last_delivery_targets: tuple[str, ...] = ()
  last_delivery_status: str | None = None
  last_delivery_summary: str | None = None
  artifact_id: str | None = None
  content_length: int = 0
  content: str = ""


@dataclass(frozen=True)
class ProviderProvenanceExportArtifactRecord:
  artifact_id: str
  job_id: str
  filename: str
  content_type: str
  content: str
  created_at: datetime
  expires_at: datetime | None = None
  byte_length: int = 0


@dataclass(frozen=True)
class ProviderProvenanceExportJobAuditRecord:
  audit_id: str
  job_id: str
  action: str
  recorded_at: datetime
  expires_at: datetime | None = None
  export_scope: str | None = None
  export_format: str | None = None
  focus_key: str | None = None
  focus_label: str | None = None
  symbol: str | None = None
  timeframe: str | None = None
  market_data_provider: str | None = None
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  routing_policy_id: str | None = None
  routing_targets: tuple[str, ...] = ()
  approval_policy_id: str | None = None
  approval_required: bool = False
  approval_state: str | None = None
  approval_summary: str | None = None
  approved_by: str | None = None
  delivery_targets: tuple[str, ...] = ()
  delivery_status: str | None = None
  delivery_summary: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ProviderProvenanceAnalyticsPresetRecord:
  preset_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceDashboardViewRecord:
  view_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  layout: dict[str, Any] = field(default_factory=dict)
  preset_id: str | None = None
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceScheduledReportRecord:
  report_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  layout: dict[str, Any] = field(default_factory=dict)
  preset_id: str | None = None
  view_id: str | None = None
  cadence: str = "daily"
  status: str = "scheduled"
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  next_run_at: datetime | None = None
  last_run_at: datetime | None = None
  last_export_job_id: str | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeTemplateRecord:
  template_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerNarrativeRegistryRecord:
  registry_id: str
  name: str
  description: str = ""
  query: dict[str, Any] = field(default_factory=dict)
  layout: dict[str, Any] = field(default_factory=dict)
  template_id: str | None = None
  created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceScheduledReportAuditRecord:
  audit_id: str
  report_id: str
  action: str
  recorded_at: datetime
  expires_at: datetime | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  export_job_id: str | None = None
  detail: str = ""


@dataclass(frozen=True)
class ProviderProvenanceSchedulerHealth:
  generated_at: datetime
  enabled: bool = True
  status: str = "starting"
  summary: str = ""
  interval_seconds: int = 60
  batch_limit: int = 25
  last_cycle_started_at: datetime | None = None
  last_cycle_finished_at: datetime | None = None
  last_success_at: datetime | None = None
  last_failure_at: datetime | None = None
  last_error: str | None = None
  cycle_count: int = 0
  success_count: int = 0
  failure_count: int = 0
  consecutive_failure_count: int = 0
  last_executed_count: int = 0
  total_executed_count: int = 0
  due_report_count: int = 0
  oldest_due_at: datetime | None = None
  max_due_lag_seconds: int = 0
  active_alert_key: str | None = None
  alert_workflow_job_id: str | None = None
  alert_workflow_triggered_at: datetime | None = None
  alert_workflow_state: str | None = None
  alert_workflow_summary: str | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderProvenanceSchedulerHealthRecord:
  record_id: str
  recorded_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  enabled: bool = True
  status: str = "starting"
  summary: str = ""
  interval_seconds: int = 60
  batch_limit: int = 25
  last_cycle_started_at: datetime | None = None
  last_cycle_finished_at: datetime | None = None
  last_success_at: datetime | None = None
  last_failure_at: datetime | None = None
  last_error: str | None = None
  cycle_count: int = 0
  success_count: int = 0
  failure_count: int = 0
  consecutive_failure_count: int = 0
  last_executed_count: int = 0
  total_executed_count: int = 0
  due_report_count: int = 0
  oldest_due_at: datetime | None = None
  max_due_lag_seconds: int = 0
  active_alert_key: str | None = None
  alert_workflow_job_id: str | None = None
  alert_workflow_triggered_at: datetime | None = None
  alert_workflow_state: str | None = None
  alert_workflow_summary: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  issues: tuple[str, ...] = ()


RUN_SURFACE_CAPABILITY_SCHEMA_TITLE = "Run-surface capability contract"
RUN_SURFACE_CAPABILITY_SCHEMA_SUMMARY = (
  "Shared capability surface for comparison boundaries, strategy schema discovery, collection query discovery, "
  "provenance semantics, operational run controls, machine-readable policy enforcement, and surface-level enforcement rules."
)
RUN_SURFACE_CAPABILITY_SCHEMA_VERSION = "run-surface-capabilities.v14"
RUN_SURFACE_CAPABILITY_GROUP_ORDER = (
  "eligible_metrics",
  "supporting_identity",
  "operational_workflow",
  "operational_order_actions",
)
RUN_SURFACE_CAPABILITY_FAMILY_ORDER = (
  "comparison_eligibility",
  "strategy_schema",
  "collection_query",
  "provenance_semantics",
  "execution_controls",
)
RUN_SURFACE_SUBRESOURCE_CONTRACT_KEYS = (
  "subresource:orders",
  "subresource:positions",
  "subresource:metrics",
)
RUN_SURFACE_COLLECTION_QUERY_CONTRACT_KEYS = (
  "query_collection:run_list",
)


def default_run_surface_shared_contracts() -> tuple[RunSurfaceSharedContract, ...]:
  return (
    RunSurfaceSharedContract(
      contract_key="schema:run-surface-capabilities",
      contract_kind="schema_metadata",
      title=RUN_SURFACE_CAPABILITY_SCHEMA_TITLE,
      summary=RUN_SURFACE_CAPABILITY_SCHEMA_SUMMARY,
      source_of_truth="run_surface_shared_contracts",
      version=RUN_SURFACE_CAPABILITY_SCHEMA_VERSION,
      related_family_keys=RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
      member_keys=tuple(
        [f"family:{family_key}" for family_key in RUN_SURFACE_CAPABILITY_FAMILY_ORDER]
        + [f"group:{group_key}" for group_key in RUN_SURFACE_CAPABILITY_GROUP_ORDER]
      ),
      schema_detail={
        "comparison_eligibility_group_order": RUN_SURFACE_CAPABILITY_GROUP_ORDER,
        "family_order": RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
        "run_subresource_contract_keys": RUN_SURFACE_SUBRESOURCE_CONTRACT_KEYS,
        "collection_query_contract_keys": RUN_SURFACE_COLLECTION_QUERY_CONTRACT_KEYS,
      },
    ),
    RunSurfaceSharedContract(
      contract_key="family:comparison_eligibility",
      contract_kind="capability_family",
      title="Comparison boundary contract",
      summary="Defines which run-list surfaces are comparison-eligible, supporting-only, or operational-only.",
      source_of_truth="comparison_eligibility_contract",
      discovery_flow="Shared UI contract panel and run-list boundary notes.",
      related_family_keys=("comparison_eligibility",),
      member_keys=("run_list_metric_tiles", "boundary_note_panels", "order_workflow_gates"),
      ui_surfaces=(
        "Run-list metric tiles",
        "Boundary note panels",
        "Order workflow gates",
      ),
      schema_sources=(
        "Run-surface capability endpoint",
        "Comparison score drill-back wiring",
        "Run-list boundary notes",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("metrics", "supporting_identity", "workflow_controls", "order_actions"),
        policy_key="comparison_surface_allowlist",
        policy_mode="allowlist",
        source_of_truth="comparison_eligibility_contract",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("run_list_metric_gating", "drill_back_selection", "boundary_note_rendering"),
        fallback_behavior="non_eligible_surfaces_remain_descriptive_only",
        level="hard_gate",
        source_of_truth="run_surface_capability_endpoint",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="run_list_metric_tile_gate",
          surface_key="run_list_metric_tiles",
          surface_label="Run-list metric tiles",
          enforcement_point="run_list_metric_gating",
          enforcement_mode="eligible_only_drillback",
          level="hard_gate",
          fallback_behavior="render_metric_as_descriptive_only_when_surface_is_not_eligible",
          source_of_truth="comparison_eligibility_contract.surfaces",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="boundary_note_group_annotation",
          surface_key="boundary_note_panels",
          surface_label="Boundary note panels",
          enforcement_point="boundary_note_rendering",
          enforcement_mode="group_boundary_annotation",
          level="hard_gate",
          fallback_behavior="render_shared_boundary_copy_without_surface_specific_drill_links",
          source_of_truth="comparison_eligibility_contract.groups",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="order_workflow_score_link_exclusion",
          surface_key="order_workflow_gates",
          surface_label="Order workflow gates",
          enforcement_point="drill_back_selection",
          enforcement_mode="score_link_exclusion",
          level="hard_gate",
          fallback_behavior="keep_operational_workflow_controls_non_selectable",
          source_of_truth="comparison_eligibility_contract.groups",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:strategy_schema",
      contract_kind="capability_family",
      title="Strategy schema discovery",
      summary="Publishes typed strategy parameter schema and semantic metadata used by preset and revision workflows.",
      source_of_truth="strategy_catalog",
      discovery_flow="Strategy catalog and preset editor schema hints.",
      related_family_keys=("strategy_schema",),
      member_keys=(
        "strategy_catalog_cards",
        "preset_parameter_editor",
        "preset_revision_semantic_diffs",
      ),
      ui_surfaces=(
        "Strategy catalog cards",
        "Preset parameter editor",
        "Preset revision semantic diffs",
      ),
      schema_sources=(
        "Strategy parameter_schema",
        "Strategy catalog_semantics",
        "Supported timeframe metadata",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("strategy_catalog", "preset_editor", "preset_revision_diff"),
        policy_key="typed_strategy_schema_advertisement",
        policy_mode="schema_contract",
        source_of_truth="strategy_catalog",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("schema_hint_rendering", "preset_diff_semantics", "parameter_editor_defaults"),
        fallback_behavior="fallback_to_freeform_parameter_entry_when_schema_missing",
        level="advisory",
        source_of_truth="strategy_metadata.parameter_schema",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="strategy_catalog_schema_hints",
          surface_key="strategy_catalog_cards",
          surface_label="Strategy catalog cards",
          enforcement_point="schema_hint_rendering",
          enforcement_mode="schema_hint_annotation",
          level="advisory",
          fallback_behavior="render_strategy_summary_without_typed_parameter_hints",
          source_of_truth="strategy_metadata.parameter_schema",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="preset_editor_default_hydration",
          surface_key="preset_parameter_editor",
          surface_label="Preset parameter editor",
          enforcement_point="parameter_editor_defaults",
          enforcement_mode="typed_default_hydration",
          level="advisory",
          fallback_behavior="fallback_to_freeform_json_parameter_entry",
          source_of_truth="strategy_metadata.parameter_schema",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="preset_revision_schema_diff",
          surface_key="preset_revision_semantic_diffs",
          surface_label="Preset revision semantic diffs",
          enforcement_point="preset_diff_semantics",
          enforcement_mode="schema_aware_delta_annotation",
          level="advisory",
          fallback_behavior="render_generic_revision_value_deltas",
          source_of_truth="strategy_catalog_semantics",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:collection_query",
      contract_kind="capability_family",
      title="Collection query discovery",
      summary="Publishes collection expression schemas, parameter domains, enum-source metadata, and parameterized predicate-template authoring metadata used by typed query builders.",
      source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
      discovery_flow="Typed query discovery panels and collection expression builders.",
      related_family_keys=("collection_query",),
      member_keys=(
        "collection_query_discovery_panels",
        "collection_expression_builders",
        "collection_parameter_domain_pickers",
      ),
      ui_surfaces=(
        "Collection query discovery panels",
        "Collection expression builders",
        "Collection parameter domain pickers",
      ),
      schema_sources=(
        "Collection path schemas",
        "Collection element filter schemas",
        "Collection parameter domain metadata",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("collection_schema", "parameter_domains", "query_builders"),
        policy_key="typed_collection_query_discovery",
        policy_mode="schema_contract",
        source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("collection_schema_discovery", "parameter_domain_rendering", "collection_shape_validation"),
        fallback_behavior="fallback_to_raw_filter_expression_authoring_when_collection_query_metadata_is_missing",
        level="advisory",
        source_of_truth="typed_query_collection_schemas",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="collection_query_schema_panel",
          surface_key="collection_query_discovery_panels",
          surface_label="Collection query discovery panels",
          enforcement_point="collection_schema_discovery",
          enforcement_mode="collection_schema_advertisement",
          level="advisory",
          fallback_behavior="omit_collection_query_contract_detail_when_discovery_metadata_is_missing",
          source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="collection_expression_builder_schema",
          surface_key="collection_expression_builders",
          surface_label="Collection expression builders",
          enforcement_point="collection_shape_validation",
          enforcement_mode="shape_validated_builder_contract",
          level="advisory",
          fallback_behavior="allow_raw_collection_paths_without_builder_guidance",
          source_of_truth="typed_query_collection_schema_validation",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="collection_parameter_domain_enum_source",
          surface_key="collection_parameter_domain_pickers",
          surface_label="Collection parameter domain pickers",
          enforcement_point="parameter_domain_rendering",
          enforcement_mode="domain_and_enum_source_annotation",
          level="advisory",
          fallback_behavior="render_parameter_domains_without_enum_source_hints",
          source_of_truth="collection_query_parameter_domains",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:provenance_semantics",
      contract_kind="capability_family",
      title="Run provenance semantics",
      summary="Carries semantic run context into snapshot, provenance, artifact, and comparison drill-back surfaces.",
      source_of_truth="run_provenance_snapshot",
      discovery_flow="Run cards, provenance panels, and comparison deep-link restoration.",
      related_family_keys=("provenance_semantics",),
      member_keys=(
        "run_strategy_snapshot",
        "reference_provenance_panels",
        "benchmark_artifact_summaries",
      ),
      ui_surfaces=(
        "Run strategy snapshot",
        "Reference provenance panels",
        "Benchmark artifact summaries",
      ),
      schema_sources=(
        "Run provenance strategy snapshot",
        "Benchmark artifact metadata",
        "Catalog semantics snapshots",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("run_snapshot", "artifact_summary", "comparison_deep_link"),
        policy_key="provenance_semantic_snapshot",
        policy_mode="snapshot_contract",
        source_of_truth="run_provenance_snapshot",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("snapshot_serialization", "provenance_panel_rendering", "deep_link_restore"),
        fallback_behavior="render_basic_provenance_without_semantic_focus_when_snapshot_missing",
        level="snapshot_required",
        source_of_truth="run_provenance.strategy",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="run_snapshot_semantic_embed",
          surface_key="run_strategy_snapshot",
          surface_label="Run strategy snapshot",
          enforcement_point="snapshot_serialization",
          enforcement_mode="semantic_snapshot_embed",
          level="snapshot_required",
          fallback_behavior="render_snapshot_without_catalog_semantics",
          source_of_truth="run_provenance.strategy",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="reference_provenance_semantic_render",
          surface_key="reference_provenance_panels",
          surface_label="Reference provenance panels",
          enforcement_point="provenance_panel_rendering",
          enforcement_mode="semantic_source_highlighting",
          level="snapshot_required",
          fallback_behavior="render_provenance_without_semantic_source_emphasis",
          source_of_truth="run_provenance.strategy.catalog_semantics",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="artifact_deep_link_restore",
          surface_key="benchmark_artifact_summaries",
          surface_label="Benchmark artifact summaries",
          enforcement_point="deep_link_restore",
          enforcement_mode="artifact_subfocus_restore",
          level="snapshot_required",
          fallback_behavior="restore_artifact_panel_without_subfocus_state",
          source_of_truth="benchmark_artifact_metadata",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:execution_controls",
      contract_kind="capability_family",
      title="Execution control gating",
      summary="Documents which interactive controls mutate workflow or venue state and therefore stay outside comparison semantics.",
      source_of_truth="run_surface_capability_endpoint",
      discovery_flow="Shared UI control gating and operational-only boundary notes.",
      related_family_keys=("execution_controls",),
      member_keys=(
        "rerun_and_stop_controls",
        "compare_selection_workflow",
        "order_replace_cancel_actions",
      ),
      ui_surfaces=(
        "Rerun and stop controls",
        "Compare selection workflow",
        "Order replace/cancel actions",
      ),
      schema_sources=(
        "Run-surface capability endpoint",
        "Order lifecycle summaries",
        "Runtime state transitions",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("rerun_controls", "stop_controls", "order_replace_cancel"),
        policy_key="operational_control_exclusion",
        policy_mode="mutation_gate",
        source_of_truth="run_surface_capability_endpoint",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("button_visibility", "order_action_boundary_notes", "comparison_selection_exclusion"),
        fallback_behavior="controls_remain_operational_only_and_do_not_bind_score_links",
        level="hard_gate",
        source_of_truth="run_surface_capability_endpoint",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="rerun_stop_button_gate",
          surface_key="rerun_and_stop_controls",
          surface_label="Rerun and stop controls",
          enforcement_point="button_visibility",
          enforcement_mode="mutation_control_gate",
          level="hard_gate",
          fallback_behavior="render_controls_as_operational_only_without_score_links",
          source_of_truth="run_surface_capability_endpoint",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="compare_selection_operational_exclusion",
          surface_key="compare_selection_workflow",
          surface_label="Compare selection workflow",
          enforcement_point="comparison_selection_exclusion",
          enforcement_mode="selection_exclusion_gate",
          level="hard_gate",
          fallback_behavior="exclude_mutating_controls_from_comparison_selection",
          source_of_truth="run_surface_capability_endpoint",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="order_replace_cancel_boundary_note",
          surface_key="order_replace_cancel_actions",
          surface_label="Order replace/cancel actions",
          enforcement_point="order_action_boundary_notes",
          enforcement_mode="operational_boundary_annotation",
          level="hard_gate",
          fallback_behavior="render_order_actions_as_operational_only",
          source_of_truth="order_lifecycle_summary",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="subresource:orders",
      contract_kind="run_subresource",
      title="Run order list",
      summary="Declarative route binding and serializer contract for the standalone `orders` run subresource.",
      source_of_truth="run_subresource_contracts",
      related_family_keys=(),
      member_keys=("body:orders", "route:get_run_orders"),
      schema_detail={
        "body_key": "orders",
        "route_path": "/runs/{run_id}/orders",
        "route_name": "get_run_orders",
      },
    ),
    RunSurfaceSharedContract(
      contract_key="subresource:positions",
      contract_kind="run_subresource",
      title="Run positions",
      summary="Declarative route binding and serializer contract for the standalone `positions` run subresource.",
      source_of_truth="run_subresource_contracts",
      related_family_keys=(),
      member_keys=("body:positions", "route:get_run_positions"),
      schema_detail={
        "body_key": "positions",
        "route_path": "/runs/{run_id}/positions",
        "route_name": "get_run_positions",
      },
    ),
    RunSurfaceSharedContract(
      contract_key="subresource:metrics",
      contract_kind="run_subresource",
      title="Run metrics",
      summary="Declarative route binding and serializer contract for the standalone `metrics` run subresource.",
      source_of_truth="run_subresource_contracts",
      related_family_keys=(),
      member_keys=("body:metrics", "route:get_run_metrics"),
      schema_detail={
        "body_key": "metrics",
        "route_path": "/runs/{run_id}/metrics",
        "route_name": "get_run_metrics",
      },
    ),
  )


@dataclass(frozen=True)
class RunComparisonNarrative:
  run_id: str
  baseline_run_id: str
  comparison_type: str
  title: str
  summary: str
  bullets: tuple[str, ...] = ()
  score_breakdown: dict[str, Any] = field(default_factory=dict)
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
class MarketDataLineageHistoryRecord:
  history_id: str
  source_job_id: str | None
  provider: str
  venue: str
  symbol: str
  timeframe: str
  recorded_at: datetime
  sync_status: str
  validation_claim: str
  reproducibility_state: str = "range_only"
  boundary_id: str | None = None
  checkpoint_id: str | None = None
  dataset_boundary: DatasetBoundaryContract | None = None
  first_timestamp: datetime | None = None
  last_timestamp: datetime | None = None
  candle_count: int = 0
  lag_seconds: int | None = None
  last_sync_at: datetime | None = None
  failure_count_24h: int = 0
  contiguous_missing_candles: int | None = None
  gap_window_count: int = 0
  last_error: str | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataIngestionJobRecord:
  job_id: str
  provider: str
  venue: str
  symbol: str
  timeframe: str
  operation: str
  status: str
  started_at: datetime
  finished_at: datetime
  duration_ms: int
  fetched_candle_count: int = 0
  validation_claim: str | None = None
  boundary_id: str | None = None
  checkpoint_id: str | None = None
  lineage_history_id: str | None = None
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  requested_limit: int | None = None
  last_error: str | None = None


@dataclass(frozen=True)
class OperatorAlertPrimaryFocus:
  symbol: str | None = None
  timeframe: str | None = None
  candidate_symbols: tuple[str, ...] = ()
  candidate_count: int = 0
  policy: str = "none"
  reason: str | None = None


@dataclass(frozen=True)
class OperatorAlertMarketContextFieldProvenance:
  scope: str | None = None
  path: str | None = None


@dataclass(frozen=True)
class OperatorAlertMarketContextProvenance:
  provider: str | None = None
  vendor_field: str | None = None
  symbol: OperatorAlertMarketContextFieldProvenance | None = None
  symbols: OperatorAlertMarketContextFieldProvenance | None = None
  timeframe: OperatorAlertMarketContextFieldProvenance | None = None
  primary_focus: OperatorAlertMarketContextFieldProvenance | None = None


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
  symbol: str | None = None
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  primary_focus: OperatorAlertPrimaryFocus | None = None
  occurrence_id: str | None = None
  timeline_key: str | None = None
  timeline_position: int | None = None
  timeline_total: int | None = None
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
class OperatorIncidentHaloItsmRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentHaloItsmRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentHaloItsmRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentHaloItsmRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIncidentManagerIoRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIncidentManagerIoRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIncidentManagerIoRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIncidentManagerIoRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOneUptimeRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOneUptimeRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOneUptimeRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOneUptimeRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSquzyRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSquzyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSquzyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSquzyRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentCrisesControlRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentCrisesControlRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentCrisesControlRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentCrisesControlRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFreshserviceRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFreshserviceRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFreshserviceRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFreshserviceRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFreshdeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFreshdeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFreshdeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFreshdeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentHappyfoxRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentHappyfoxRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentHappyfoxRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentHappyfoxRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentZendeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentZendeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentZendeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentZendeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentZohoDeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentZohoDeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentZohoDeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentZohoDeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentHelpScoutRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentHelpScoutRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentHelpScoutRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentHelpScoutRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentKayakoRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentKayakoRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentKayakoRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentKayakoRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIntercomRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIntercomRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIntercomRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIntercomRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFrontRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFrontRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFrontRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFrontRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentServiceDeskPlusRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentServiceDeskPlusRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentServiceDeskPlusRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentServiceDeskPlusRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSysAidRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSysAidRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSysAidRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSysAidRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBmcHelixRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBmcHelixRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBmcHelixRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBmcHelixRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSolarWindsServiceDeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentTopdeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentTopdeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentTopdeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentTopdeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentInvGateServiceDeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph:
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
  primary_focus: OperatorAlertPrimaryFocus | None = None
  market_context_provenance: OperatorAlertMarketContextProvenance | None = None
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
  haloitsm: OperatorIncidentHaloItsmRecoveryState = field(
    default_factory=OperatorIncidentHaloItsmRecoveryState
  )
  incidentmanagerio: OperatorIncidentIncidentManagerIoRecoveryState = field(
    default_factory=OperatorIncidentIncidentManagerIoRecoveryState
  )
  oneuptime: OperatorIncidentOneUptimeRecoveryState = field(
    default_factory=OperatorIncidentOneUptimeRecoveryState
  )
  squzy: OperatorIncidentSquzyRecoveryState = field(
    default_factory=OperatorIncidentSquzyRecoveryState
  )
  crisescontrol: OperatorIncidentCrisesControlRecoveryState = field(
    default_factory=OperatorIncidentCrisesControlRecoveryState
  )
  freshservice: OperatorIncidentFreshserviceRecoveryState = field(
    default_factory=OperatorIncidentFreshserviceRecoveryState
  )
  freshdesk: OperatorIncidentFreshdeskRecoveryState = field(
    default_factory=OperatorIncidentFreshdeskRecoveryState
  )
  happyfox: OperatorIncidentHappyfoxRecoveryState = field(
    default_factory=OperatorIncidentHappyfoxRecoveryState
  )
  zendesk: OperatorIncidentZendeskRecoveryState = field(
    default_factory=OperatorIncidentZendeskRecoveryState
  )
  zohodesk: OperatorIncidentZohoDeskRecoveryState = field(
    default_factory=OperatorIncidentZohoDeskRecoveryState
  )
  helpscout: OperatorIncidentHelpScoutRecoveryState = field(
    default_factory=OperatorIncidentHelpScoutRecoveryState
  )
  kayako: OperatorIncidentKayakoRecoveryState = field(
    default_factory=OperatorIncidentKayakoRecoveryState
  )
  intercom: OperatorIncidentIntercomRecoveryState = field(
    default_factory=OperatorIncidentIntercomRecoveryState
  )
  front: OperatorIncidentFrontRecoveryState = field(
    default_factory=OperatorIncidentFrontRecoveryState
  )
  servicedeskplus: OperatorIncidentServiceDeskPlusRecoveryState = field(
    default_factory=OperatorIncidentServiceDeskPlusRecoveryState
  )
  sysaid: OperatorIncidentSysAidRecoveryState = field(
    default_factory=OperatorIncidentSysAidRecoveryState
  )
  bmchelix: OperatorIncidentBmcHelixRecoveryState = field(
    default_factory=OperatorIncidentBmcHelixRecoveryState
  )
  solarwindsservicedesk: OperatorIncidentSolarWindsServiceDeskRecoveryState = field(
    default_factory=OperatorIncidentSolarWindsServiceDeskRecoveryState
  )
  topdesk: OperatorIncidentTopdeskRecoveryState = field(
    default_factory=OperatorIncidentTopdeskRecoveryState
  )
  invgateservicedesk: OperatorIncidentInvGateServiceDeskRecoveryState = field(
    default_factory=OperatorIncidentInvGateServiceDeskRecoveryState
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
  symbol: str | None = None
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  primary_focus: OperatorAlertPrimaryFocus | None = None
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
  provider_provenance_scheduler: ProviderProvenanceSchedulerHealth | None = None


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
  gap_window_id: str = ""

  def __post_init__(self) -> None:
    if self.gap_window_id:
      return
    payload = "|".join([
      self.start_at.isoformat(),
      self.end_at.isoformat(),
      str(self.missing_candles),
    ])
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    object.__setattr__(
      self,
      "gap_window_id",
      f"gw|0|{self.start_at.isoformat()}|{self.end_at.isoformat()}|{self.missing_candles}|{digest}",
    )


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
