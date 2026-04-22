from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC
from datetime import datetime
from enum import Enum
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


from akra_trader.domain.model_types.strategy_catalog import *


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


from akra_trader.domain.model_types.provider_provenance import *
from akra_trader.domain.model_types.run_surface_contracts import *
from akra_trader.domain.model_types.run_comparison import *
from akra_trader.domain.model_types.market_data_status import *
from akra_trader.domain.model_types.sync_lineage import *
from akra_trader.domain.model_types.operator_runtime import *
from akra_trader.domain.model_types.guarded_live import *


@dataclass(frozen=True)
class MarketDataRemediationResult:
  kind: str
  symbol: str
  timeframe: str
  status: str
  started_at: datetime
  finished_at: datetime
  detail: str
