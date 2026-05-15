from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from math import isclose

from akra_trader.domain.models import ClosedTrade
from akra_trader.domain.models import EquityPoint
from akra_trader.domain.models import ExecutionPlan
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
  execution: ExecutionPlan | None = None,
  execution_market: str = "spot",
  leverage: float = 1.0,
  maintenance_margin_rate: float = 0.0,
  funding_rate_8h: float = 0.0,
) -> tuple[float, Position | None, Order | None, Fill | None, ClosedTrade | None]:
  slippage_ratio = slippage_bps / 10_000
  active_position = position if position and position.is_open else None
  plan = execution or ExecutionPlan()
  size_fraction = min(max(plan.size_fraction, 0.0), 1.0)
  normalized_market = _execution_market(execution_market, leverage)
  normalized_leverage = _normalized_leverage(leverage, normalized_market)
  normalized_maintenance_margin_rate = max(maintenance_margin_rate, 0.0)

  if (
    signal.action == SignalAction.BUY
    and cash > 0
    and size_fraction > 0
    and (active_position is None or plan.allow_scale_in)
  ):
    executed_price = market_price * (1 + slippage_ratio)
    allocated_cash = cash * size_fraction
    quantity = (
      (allocated_cash * normalized_leverage) / executed_price
      if normalized_market == "futures"
      else allocated_cash / (executed_price * (1 + fee_rate))
    )
    if isclose(quantity, 0.0):
      return cash, active_position, None, None, None
    gross_cost = quantity * executed_price
    fee_paid = gross_cost * fee_rate
    if normalized_market == "futures" and fee_paid >= cash:
      return cash, active_position, None, None, None
    order = Order(
      run_id=run_id,
      instrument_id=instrument_id,
      side=OrderSide.BUY,
      quantity=quantity,
      requested_price=market_price,
      status=OrderStatus.FILLED,
      filled_at=signal.timestamp,
      updated_at=signal.timestamp,
      average_fill_price=executed_price,
      fee_paid=fee_paid,
      filled_quantity=quantity,
      remaining_quantity=0.0,
      last_synced_at=signal.timestamp,
    )
    fill = Fill(
      order_id=order.order_id,
      quantity=quantity,
      price=executed_price,
      fee_paid=fee_paid,
      timestamp=signal.timestamp,
    )
    if active_position is None:
      new_position = Position(
        instrument_id=instrument_id,
        quantity=quantity,
        average_price=executed_price,
        opened_at=signal.timestamp,
        updated_at=signal.timestamp,
        stop_loss_price=_stop_loss_price(executed_price, plan.stop_loss_pct),
        take_profit_price=_take_profit_price(executed_price, plan.take_profit_pct),
        high_watermark_price=executed_price,
        market_type=normalized_market,
        leverage=normalized_leverage,
        maintenance_margin_rate=normalized_maintenance_margin_rate,
        liquidation_price=_long_liquidation_price(
          executed_price,
          leverage=normalized_leverage,
          maintenance_margin_rate=normalized_maintenance_margin_rate,
        ),
        funding_rate_8h=funding_rate_8h if normalized_market == "futures" else 0.0,
      )
    else:
      total_quantity = active_position.quantity + quantity
      average_price = (
        (active_position.quantity * active_position.average_price) + (quantity * executed_price)
      ) / total_quantity
      high_watermark_price = max(
        active_position.high_watermark_price or active_position.average_price,
        executed_price,
      )
      new_position = replace(
        active_position,
        quantity=total_quantity,
        average_price=average_price,
        updated_at=signal.timestamp,
        stop_loss_price=(
          _stop_loss_price(average_price, plan.stop_loss_pct)
          if plan.stop_loss_pct is not None
          else active_position.stop_loss_price
        ),
        take_profit_price=(
          _take_profit_price(average_price, plan.take_profit_pct)
          if plan.take_profit_pct is not None
          else active_position.take_profit_price
        ),
        high_watermark_price=high_watermark_price,
        liquidation_price=_long_liquidation_price(
          average_price,
          leverage=active_position.leverage,
          maintenance_margin_rate=active_position.maintenance_margin_rate,
        ),
      )
    next_cash = cash - fee_paid if normalized_market == "futures" else cash - gross_cost - fee_paid
    return next_cash, new_position, order, fill, None

  if signal.action == SignalAction.SELL and active_position is not None and size_fraction > 0:
    executed_price = market_price * (1 - slippage_ratio)
    quantity = active_position.quantity
    if plan.allow_partial_exit:
      quantity = active_position.quantity * size_fraction
    if isclose(quantity, 0.0):
      return cash, active_position, None, None, None

    gross_value = quantity * executed_price
    fee_paid = gross_value * fee_rate
    if active_position.market_type == "futures":
      funding_fee = _futures_funding_fee(
        active_position,
        closed_at=signal.timestamp,
        funding_rate_8h=funding_rate_8h,
      )
      proceeds = 0.0
      pnl = (
        (executed_price - active_position.average_price) * quantity
      ) - fee_paid - funding_fee
      closed_trade_fee_paid = fee_paid + funding_fee
    else:
      funding_fee = 0.0
      proceeds = gross_value - fee_paid
      pnl = proceeds - (quantity * active_position.average_price)
      closed_trade_fee_paid = fee_paid
    order = Order(
      run_id=run_id,
      instrument_id=instrument_id,
      side=OrderSide.SELL,
      quantity=quantity,
      requested_price=market_price,
      status=OrderStatus.FILLED,
      filled_at=signal.timestamp,
      updated_at=signal.timestamp,
      average_fill_price=executed_price,
      fee_paid=fee_paid,
      filled_quantity=quantity,
      remaining_quantity=0.0,
      last_synced_at=signal.timestamp,
    )
    fill = Fill(
      order_id=order.order_id,
      quantity=quantity,
      price=executed_price,
      fee_paid=fee_paid,
      timestamp=signal.timestamp,
    )
    closed_trade = ClosedTrade(
      instrument_id=instrument_id,
      entry_price=active_position.average_price,
      exit_price=executed_price,
      quantity=quantity,
      fee_paid=closed_trade_fee_paid,
      pnl=pnl,
      opened_at=active_position.opened_at or signal.timestamp,
      closed_at=signal.timestamp,
    )
    remaining_quantity = active_position.quantity - quantity
    closed_position = replace(
      active_position,
      quantity=0.0 if isclose(remaining_quantity, 0.0) else remaining_quantity,
      updated_at=signal.timestamp,
      realized_pnl=active_position.realized_pnl + pnl,
      stop_loss_price=None if isclose(remaining_quantity, 0.0) else active_position.stop_loss_price,
      take_profit_price=(
        None if isclose(remaining_quantity, 0.0) else active_position.take_profit_price
      ),
      high_watermark_price=(
        None if isclose(remaining_quantity, 0.0) else active_position.high_watermark_price
      ),
      trailing_stop_price=(
        None if isclose(remaining_quantity, 0.0) else active_position.trailing_stop_price
      ),
      liquidation_price=(
        None if isclose(remaining_quantity, 0.0) else active_position.liquidation_price
      ),
    )
    next_cash = cash + pnl if active_position.market_type == "futures" else cash + proceeds
    return next_cash, closed_position, order, fill, closed_trade

  return cash, active_position, None, None, None


def _stop_loss_price(entry_price: float, stop_loss_pct: float | None) -> float | None:
  if stop_loss_pct is None:
    return None
  return entry_price * (1 - min(max(stop_loss_pct, 0.0), 1.0))


def _take_profit_price(entry_price: float, take_profit_pct: float | None) -> float | None:
  if take_profit_pct is None:
    return None
  return entry_price * (1 + max(take_profit_pct, 0.0))


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
    if position.market_type == "futures":
      equity += (market_price - position.average_price) * position.quantity
    else:
      equity += exposure
  return EquityPoint(timestamp=timestamp, equity=equity, cash=cash, exposure=exposure)


def _execution_market(execution_market: str, leverage: float) -> str:
  normalized = execution_market.strip().lower()
  if normalized == "futures" or leverage > 1.0:
    return "futures"
  return "spot"


def _normalized_leverage(leverage: float, execution_market: str) -> float:
  if execution_market != "futures":
    return 1.0
  return max(leverage, 1.0)


def _long_liquidation_price(
  entry_price: float,
  *,
  leverage: float,
  maintenance_margin_rate: float,
) -> float | None:
  if leverage <= 1.0:
    return None
  liquidation_distance = (1.0 / leverage) - maintenance_margin_rate
  if liquidation_distance <= 0:
    return entry_price
  return max(entry_price * (1.0 - liquidation_distance), 0.0)


def _futures_funding_fee(
  position: Position,
  *,
  closed_at: datetime,
  funding_rate_8h: float,
) -> float:
  if position.opened_at is None or funding_rate_8h == 0:
    return 0.0
  elapsed_hours = max((closed_at - position.opened_at).total_seconds() / 3600, 0.0)
  funding_periods = elapsed_hours / 8
  entry_notional = position.quantity * position.average_price
  return entry_notional * funding_rate_8h * funding_periods


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
