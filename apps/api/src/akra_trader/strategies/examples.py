from __future__ import annotations

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec
from akra_trader.strategies.base import FixedFractionExecutionPolicy
from akra_trader.strategies.base import PolicyBackedStrategy
from akra_trader.strategies.base import SignalPolicy


class MovingAverageCrossSignalPolicy(SignalPolicy):
  def decide(self, context: StrategyDecisionContext) -> SignalDecision:
    buy_cross = (
      context.features["previous_sma_short"] <= context.features["previous_sma_long"]
      and context.features["current_sma_short"] > context.features["current_sma_long"]
    )
    sell_cross = (
      context.features["previous_sma_short"] >= context.features["previous_sma_long"]
      and context.features["current_sma_short"] < context.features["current_sma_long"]
    )

    if buy_cross and not context.state.has_position:
      return SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.BUY,
        confidence=0.65,
        tags=("trend", "crossover"),
        reason="short_ma_crossed_above_long_ma",
      )
    if sell_cross and context.state.has_position:
      return SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.SELL,
        confidence=0.65,
        tags=("trend", "crossover"),
        reason="short_ma_crossed_below_long_ma",
      )
    return SignalDecision(
      timestamp=context.timestamp,
      action=SignalAction.HOLD,
      confidence=0.5,
      tags=("idle",),
      reason="no_action",
    )


class MovingAverageCrossStrategy(PolicyBackedStrategy):
  def describe(self) -> StrategyMetadata:
    return StrategyMetadata(
      strategy_id="ma_cross_v1",
      name="Moving Average Cross",
      version="1.0.0",
      runtime="native",
      asset_types=(AssetType.CRYPTO,),
      supported_timeframes=("5m", "1h"),
      parameter_schema={
        "short_window": {"type": "integer", "default": 8, "minimum": 2},
        "long_window": {"type": "integer", "default": 21, "minimum": 5},
      },
      description="Simple momentum crossover strategy intended as the starter SDK example.",
    )

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(required_bars=21, timeframes=("5m",))

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    short_window = int(parameters.get("short_window", 8))
    long_window = int(parameters.get("long_window", 21))
    frame = candles.copy()
    frame["sma_short"] = frame["close"].rolling(window=short_window).mean()
    frame["sma_long"] = frame["close"].rolling(window=long_window).mean()
    return frame

  def build_decision_context(
    self,
    candles: pd.DataFrame,
    parameters: dict,
    state,
  ) -> StrategyDecisionContext:
    context = super().build_decision_context(candles, parameters, state)
    previous = candles.iloc[-2]
    current = candles.iloc[-1]
    features = {
      **context.features,
      "previous_sma_short": float(previous["sma_short"]),
      "previous_sma_long": float(previous["sma_long"]),
      "current_sma_short": float(current["sma_short"]),
      "current_sma_long": float(current["sma_long"]),
    }
    return StrategyDecisionContext(
      timestamp=context.timestamp,
      instrument_id=context.instrument_id,
      features=features,
      market=context.market,
      state=context.state,
    )

  def signal_policy(self, parameters: dict) -> SignalPolicy:
    return MovingAverageCrossSignalPolicy()

  def execution_policy(self, parameters: dict) -> FixedFractionExecutionPolicy:
    return FixedFractionExecutionPolicy(size_fraction=1.0, tags=("full_notional",))

  def build_rationale(self, context: StrategyDecisionContext, signal: SignalDecision) -> str:
    if signal.action == SignalAction.BUY:
      return "Bullish moving-average crossover."
    if signal.action == SignalAction.SELL:
      return "Bearish moving-average crossover."
    return "No crossover condition met."
