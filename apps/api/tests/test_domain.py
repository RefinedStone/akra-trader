from __future__ import annotations

from datetime import UTC
from datetime import datetime

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
