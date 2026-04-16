from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from math import isclose

from akra_trader.domain.models import ClosedTrade
from akra_trader.domain.models import EquityPoint
from akra_trader.domain.models import Fill
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import Position
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision


def apply_signal(
  *,
  run_id: str,
  instrument_id: str,
  signal: SignalDecision,
  market_price: float,
  position: Position | None,
  cash: float,
  fee_rate: float,
  slippage_bps: float,
) -> tuple[float, Position | None, Order | None, Fill | None, ClosedTrade | None]:
  slippage_ratio = slippage_bps / 10_000
  active_position = position if position and position.is_open else None

  if signal.action == SignalAction.BUY and active_position is None and cash > 0:
    executed_price = market_price * (1 + slippage_ratio)
    quantity = cash / (executed_price * (1 + fee_rate))
    if isclose(quantity, 0.0):
      return cash, active_position, None, None, None
    gross_cost = quantity * executed_price
    fee_paid = gross_cost * fee_rate
    order = Order(
      run_id=run_id,
      instrument_id=instrument_id,
      side=OrderSide.BUY,
      quantity=quantity,
      requested_price=market_price,
      status=OrderStatus.FILLED,
      filled_at=signal.timestamp,
      average_fill_price=executed_price,
      fee_paid=fee_paid,
    )
    fill = Fill(
      order_id=order.order_id,
      quantity=quantity,
      price=executed_price,
      fee_paid=fee_paid,
      timestamp=signal.timestamp,
    )
    new_position = Position(
      instrument_id=instrument_id,
      quantity=quantity,
      average_price=executed_price,
      opened_at=signal.timestamp,
      updated_at=signal.timestamp,
    )
    return cash - gross_cost - fee_paid, new_position, order, fill, None

  if signal.action == SignalAction.SELL and active_position is not None:
    executed_price = market_price * (1 - slippage_ratio)
    gross_value = active_position.quantity * executed_price
    fee_paid = gross_value * fee_rate
    proceeds = gross_value - fee_paid
    pnl = proceeds - (active_position.quantity * active_position.average_price)
    order = Order(
      run_id=run_id,
      instrument_id=instrument_id,
      side=OrderSide.SELL,
      quantity=active_position.quantity,
      requested_price=market_price,
      status=OrderStatus.FILLED,
      filled_at=signal.timestamp,
      average_fill_price=executed_price,
      fee_paid=fee_paid,
    )
    fill = Fill(
      order_id=order.order_id,
      quantity=active_position.quantity,
      price=executed_price,
      fee_paid=fee_paid,
      timestamp=signal.timestamp,
    )
    closed_trade = ClosedTrade(
      instrument_id=instrument_id,
      entry_price=active_position.average_price,
      exit_price=executed_price,
      quantity=active_position.quantity,
      fee_paid=fee_paid,
      pnl=pnl,
      opened_at=active_position.opened_at or signal.timestamp,
      closed_at=signal.timestamp,
    )
    closed_position = replace(active_position, quantity=0.0, updated_at=signal.timestamp, realized_pnl=pnl)
    return cash + proceeds, closed_position, order, fill, closed_trade

  return cash, active_position, None, None, None


def build_equity_point(
  *,
  timestamp: datetime,
  cash: float,
  position: Position | None,
  market_price: float,
) -> EquityPoint:
  exposure = 0.0
  equity = cash
  if position and position.is_open:
    exposure = position.quantity * market_price
    equity += exposure
  return EquityPoint(timestamp=timestamp, equity=equity, cash=cash, exposure=exposure)


def summarize_performance(
  *,
  initial_cash: float,
  equity_curve: list[EquityPoint],
  closed_trades: list[ClosedTrade],
) -> dict[str, float | int]:
  if equity_curve:
    ending_equity = equity_curve[-1].equity
  else:
    ending_equity = initial_cash
  total_return_pct = ((ending_equity - initial_cash) / initial_cash) * 100 if initial_cash else 0.0

  peak = initial_cash
  max_drawdown_pct = 0.0
  invested_steps = 0
  for point in equity_curve:
    peak = max(peak, point.equity)
    if peak:
      drawdown_pct = ((peak - point.equity) / peak) * 100
      max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)
    if point.exposure > 0:
      invested_steps += 1

  winning_trades = sum(1 for trade in closed_trades if trade.pnl > 0)
  trade_count = len(closed_trades)
  win_rate_pct = (winning_trades / trade_count) * 100 if trade_count else 0.0
  exposure_pct = (invested_steps / len(equity_curve)) * 100 if equity_curve else 0.0

  return {
    "initial_cash": round(initial_cash, 2),
    "ending_equity": round(ending_equity, 2),
    "total_return_pct": round(total_return_pct, 2),
    "max_drawdown_pct": round(max_drawdown_pct, 2),
    "win_rate_pct": round(win_rate_pct, 2),
    "trade_count": trade_count,
    "exposure_pct": round(exposure_pct, 2),
  }
