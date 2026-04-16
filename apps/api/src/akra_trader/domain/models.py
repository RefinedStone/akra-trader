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
  filled_at: datetime | None = None
  average_fill_price: float | None = None
  fee_paid: float = 0.0


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
  reproducibility_state: str = "range_only"
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  effective_start_at: datetime | None = None
  effective_end_at: datetime | None = None
  candle_count: int = 0
  sync_status: str = "unknown"
  last_sync_at: datetime | None = None
  issues: tuple[str, ...] = ()

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
  market_data: MarketDataLineage | None = None
  market_data_by_symbol: dict[str, MarketDataLineage] = field(default_factory=dict)


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
class GapWindow:
  start_at: datetime
  end_at: datetime
  missing_candles: int


@dataclass(frozen=True)
class StrategyRegistration:
  strategy_id: str
  module_path: str
  class_name: str
  registered_at: datetime
