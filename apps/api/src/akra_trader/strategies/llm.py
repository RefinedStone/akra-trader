from __future__ import annotations

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec
from akra_trader.ports import DecisionEnginePort
from akra_trader.strategies.base import Strategy


class ExternalDecisionStrategy(Strategy):
  def __init__(self, decision_engine: DecisionEnginePort) -> None:
    self._decision_engine = decision_engine

  def describe(self) -> StrategyMetadata:
    return StrategyMetadata(
      strategy_id="external_decision_template",
      name="External Decision Template",
      version="0.1.0",
      runtime="decision_engine",
      asset_types=(AssetType.CRYPTO, AssetType.STOCK),
      supported_timeframes=("5m", "1h", "1d"),
      parameter_schema={
        "prompt_profile": {"type": "string", "default": "balanced"},
      },
      description="Template strategy that delegates final trade selection to an external decision engine such as an LLM.",
    )

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(required_bars=32, timeframes=("5m", "1h"))

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    frame = candles.copy()
    frame["return_1"] = frame["close"].pct_change().fillna(0.0)
    frame["volatility_8"] = frame["return_1"].rolling(window=8).std().fillna(0.0)
    return frame

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    return self._decision_engine.decide(context)
