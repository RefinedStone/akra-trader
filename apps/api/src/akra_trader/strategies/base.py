from __future__ import annotations

from abc import ABC
from abc import abstractmethod

import pandas as pd

from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec


class Strategy(ABC):
  @abstractmethod
  def describe(self) -> StrategyMetadata:
    raise NotImplementedError

  @abstractmethod
  def warmup_spec(self) -> WarmupSpec:
    raise NotImplementedError

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    return candles.copy()

  def build_decision_context(
    self,
    candles: pd.DataFrame,
    parameters: dict,
    state: StrategyExecutionState,
  ) -> StrategyDecisionContext:
    latest = candles.iloc[-1]
    features = latest.to_dict()
    return StrategyDecisionContext(
      timestamp=latest["timestamp"].to_pydatetime(),
      instrument_id=state.instrument_id,
      features=features,
      market={
        "open": float(latest["open"]),
        "high": float(latest["high"]),
        "low": float(latest["low"]),
        "close": float(latest["close"]),
        "volume": float(latest["volume"]),
      },
      state=state,
    )

  @abstractmethod
  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    raise NotImplementedError

  def evaluate(
    self,
    candles: pd.DataFrame,
    parameters: dict,
    state: StrategyExecutionState,
  ) -> StrategyDecisionEnvelope:
    context = self.build_decision_context(candles, parameters, state)
    return self.decide(context)
