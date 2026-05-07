from __future__ import annotations

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyLifecycle
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
      name="Future LLM Research Lane",
      version="0.1.0",
      runtime="decision_engine",
      asset_types=(AssetType.CRYPTO, AssetType.STOCK),
      supported_timeframes=("5m", "1h", "1d"),
      parameter_schema={
        "prompt_profile": {
          "type": "string",
          "default": "balanced",
          "semantic_hint": "Future LLM decision posture for isolated research runs.",
          "semantic_ranks": {
            "safe": 0,
            "cautious": 1,
            "balanced": 2,
            "assertive": 3,
            "aggressive": 4,
          },
          "delta_higher_label": "more assertive prompt posture",
          "delta_lower_label": "safer prompt posture",
        },
      },
      description=(
        "Isolated Future LLM research strategy. It records decision posture and keeps live "
        "promotion outside this scaffold until trace, replay, and fallback gates are ready."
      ),
      lifecycle=StrategyLifecycle(stage="experimental"),
      version_lineage=("0.1.0",),
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
