from __future__ import annotations

from typing import Protocol

import pandas as pd

from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import WarmupSpec


class StrategyRuntime(Protocol):
  def describe(self): ...

  def warmup_spec(self) -> WarmupSpec: ...

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame: ...

  def build_decision_context(
    self,
    candles: pd.DataFrame,
    parameters: dict,
    state: StrategyExecutionState,
  ) -> StrategyDecisionContext: ...

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope: ...


class DecisionEnginePort(Protocol):
  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope: ...
