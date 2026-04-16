from __future__ import annotations

from datetime import UTC
from datetime import datetime

from akra_trader.domain.models import ExecutionPlan
from akra_trader.domain.models import Position
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.services import apply_signal


def test_apply_signal_buy_then_sell_round_trip() -> None:
  cash = 1_000.0
  buy_signal = SignalDecision(timestamp=datetime(2025, 1, 1, tzinfo=UTC), action=SignalAction.BUY)
  cash, position, order, fill, closed_trade = apply_signal(
    run_id="run-1",
    instrument_id="binance:BTC/USDT",
    signal=buy_signal,
    market_price=100.0,
    position=None,
    cash=cash,
    fee_rate=0.001,
    slippage_bps=0,
  )

  assert order is not None
  assert fill is not None
  assert closed_trade is None
  assert position is not None
  assert position.quantity > 0
  assert cash < 1

  sell_signal = SignalDecision(timestamp=datetime(2025, 1, 2, tzinfo=UTC), action=SignalAction.SELL)
  cash, position, order, fill, closed_trade = apply_signal(
    run_id="run-1",
    instrument_id="binance:BTC/USDT",
    signal=sell_signal,
    market_price=110.0,
    position=position,
    cash=cash,
    fee_rate=0.001,
    slippage_bps=0,
  )

  assert position is not None
  assert position.quantity == 0
  assert order is not None
  assert fill is not None
  assert closed_trade is not None
  assert closed_trade.pnl > 0
  assert cash > 1_000


def test_apply_signal_supports_scale_in_and_partial_exit() -> None:
  entry_signal = SignalDecision(timestamp=datetime(2025, 1, 1, tzinfo=UTC), action=SignalAction.BUY)
  cash, position, _, _, _ = apply_signal(
    run_id="run-2",
    instrument_id="binance:ETH/USDT",
    signal=entry_signal,
    market_price=100.0,
    position=None,
    cash=1_000.0,
    fee_rate=0.001,
    slippage_bps=0,
    execution=ExecutionPlan(size_fraction=0.5),
  )

  assert position is not None
  initial_quantity = position.quantity

  cash, position, _, _, _ = apply_signal(
    run_id="run-2",
    instrument_id="binance:ETH/USDT",
    signal=entry_signal,
    market_price=105.0,
    position=position,
    cash=cash,
    fee_rate=0.001,
    slippage_bps=0,
    execution=ExecutionPlan(size_fraction=0.5, allow_scale_in=True),
  )

  assert position is not None
  assert position.quantity > initial_quantity

  exit_signal = SignalDecision(timestamp=datetime(2025, 1, 2, tzinfo=UTC), action=SignalAction.SELL)
  cash, position, _, _, closed_trade = apply_signal(
    run_id="run-2",
    instrument_id="binance:ETH/USDT",
    signal=exit_signal,
    market_price=110.0,
    position=position,
    cash=cash,
    fee_rate=0.001,
    slippage_bps=0,
    execution=ExecutionPlan(size_fraction=0.5, allow_partial_exit=True),
  )

  assert position is not None
  assert position.quantity > 0
  assert closed_trade is not None
