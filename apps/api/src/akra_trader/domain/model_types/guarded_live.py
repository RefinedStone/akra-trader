from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from akra_trader.domain.model_types.operator_runtime import OperatorAlert
from akra_trader.domain.model_types.operator_runtime import OperatorAuditEvent
from akra_trader.domain.model_types.operator_runtime import OperatorIncidentDelivery
from akra_trader.domain.model_types.operator_runtime import OperatorIncidentEvent

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
