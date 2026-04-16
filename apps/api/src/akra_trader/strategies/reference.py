from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec
from akra_trader.strategies.base import Strategy


@dataclass(frozen=True)
class ReferenceStrategyDefinition:
  strategy_id: str
  name: str
  version: str
  entrypoint: str
  reference_path: str
  description: str


class ReferenceFreqtradeStrategy(Strategy):
  def __init__(self, definition: ReferenceStrategyDefinition) -> None:
    self._definition = definition

  def describe(self) -> StrategyMetadata:
    return StrategyMetadata(
      strategy_id=self._definition.strategy_id,
      name=self._definition.name,
      version=self._definition.version,
      runtime="freqtrade_reference",
      asset_types=(AssetType.CRYPTO,),
      supported_timeframes=("5m",),
      parameter_schema={},
      description=self._definition.description,
      reference_path=self._definition.reference_path,
      entrypoint=self._definition.entrypoint,
    )

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(required_bars=0)

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    return candles

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    signal = SignalDecision(
      timestamp=context.timestamp,
      action=SignalAction.HOLD,
      reason="reference_strategy_executes_via_freqtrade_delegate",
    )
    return StrategyDecisionEnvelope(
      signal=signal,
      rationale="Execution is delegated to the upstream Freqtrade runtime.",
      context=context,
    )


def build_reference_strategies() -> list[ReferenceFreqtradeStrategy]:
  definitions = [
    ReferenceStrategyDefinition(
      strategy_id="nfi_x7_reference",
      name="NostalgiaForInfinityX7",
      version="v17.3.1107",
      entrypoint="NostalgiaForInfinityX7",
      reference_path="reference/NostalgiaForInfinity/user_data/strategies/NostalgiaForInfinityX7.py",
      description="Direct reference wrapper for the upstream NostalgiaForInfinityX7 Freqtrade strategy.",
    ),
    ReferenceStrategyDefinition(
      strategy_id="nfi_next_reference",
      name="NostalgiaForInfinityNext",
      version="reference",
      entrypoint="NostalgiaForInfinityNext",
      reference_path="reference/NostalgiaForInfinity/user_data/strategies/NostalgiaForInfinityNext.py",
      description="Direct reference wrapper for the upstream NostalgiaForInfinityNext Freqtrade strategy.",
    ),
    ReferenceStrategyDefinition(
      strategy_id="nfi_nextgen_reference",
      name="NostalgiaForInfinityNextGen",
      version="reference",
      entrypoint="NostalgiaForInfinityNextGen",
      reference_path="reference/NostalgiaForInfinity/user_data/strategies/NostalgiaForInfinityNextGen.py",
      description="Direct reference wrapper for the upstream NostalgiaForInfinityNextGen Freqtrade strategy.",
    ),
  ]
  return [ReferenceFreqtradeStrategy(definition) for definition in definitions]
