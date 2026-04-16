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
class StrategyMetadata:
  strategy_id: str
  name: str
  version: str
  runtime: str
  asset_types: tuple[AssetType, ...]
  supported_timeframes: tuple[str, ...]
  parameter_schema: dict[str, Any]
  description: str
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
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  effective_start_at: datetime | None = None
  effective_end_at: datetime | None = None
  candle_count: int = 0
  sync_status: str = "unknown"
  last_sync_at: datetime | None = None
  issues: tuple[str, ...] = ()


@dataclass
class RunProvenance:
  lane: str = "native"
  reference_id: str | None = None
  reference_version: str | None = None
  integration_mode: str | None = None
  working_directory: str | None = None
  external_command: tuple[str, ...] = ()
  artifact_paths: tuple[str, ...] = ()
  market_data: MarketDataLineage | None = None


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
class InstrumentStatus:
  instrument_id: str
  timeframe: str
  candle_count: int
  first_timestamp: datetime | None
  last_timestamp: datetime | None
  sync_status: str = "empty"
  lag_seconds: int | None = None
  last_sync_at: datetime | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataStatus:
  provider: str
  venue: str
  instruments: list[InstrumentStatus]


@dataclass(frozen=True)
class StrategyRegistration:
  strategy_id: str
  module_path: str
  class_name: str
  registered_at: datetime
