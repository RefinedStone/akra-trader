from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec
from akra_trader.strategies.base import PolicyBackedStrategy
from akra_trader.strategies.base import SignalPolicy


@dataclass(frozen=True)
class ReferenceStrategyDefinition:
  strategy_id: str
  name: str
  version: str
  reference_id: str
  entrypoint: str
  reference_path: str
  description: str


class ReferenceHoldSignalPolicy(SignalPolicy):
  def decide(self, context: StrategyDecisionContext) -> SignalDecision:
    return SignalDecision(
      timestamp=context.timestamp,
      action=SignalAction.HOLD,
      reason="reference_strategy_executes_via_freqtrade_delegate",
      tags=("reference", "delegated"),
    )


class ReferenceFreqtradeStrategy(PolicyBackedStrategy):
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
      lifecycle=StrategyLifecycle(stage="imported"),
      version_lineage=(self._definition.version,),
      reference_id=self._definition.reference_id,
      reference_path=self._definition.reference_path,
      entrypoint=self._definition.entrypoint,
    )

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(required_bars=0)

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    return candles

  def signal_policy(self, parameters: dict) -> SignalPolicy:
    return ReferenceHoldSignalPolicy()

  def build_rationale(self, context: StrategyDecisionContext, signal: SignalDecision) -> str:
    return "Execution is delegated to the upstream Freqtrade runtime."


def build_reference_strategies() -> list[ReferenceFreqtradeStrategy]:
  definitions = [
    ReferenceStrategyDefinition(
      strategy_id="nfi_x7_reference",
      name="NostalgiaForInfinityX7",
      version="v17.3.1107",
      reference_id="nostalgia-for-infinity",
      entrypoint="NostalgiaForInfinityX7",
      reference_path="reference/NostalgiaForInfinity/user_data/strategies/NostalgiaForInfinityX7.py",
      description="Direct reference wrapper for the upstream NostalgiaForInfinityX7 Freqtrade strategy.",
    ),
    ReferenceStrategyDefinition(
      strategy_id="nfi_next_reference",
      name="NostalgiaForInfinityNext",
      version="reference",
      reference_id="nostalgia-for-infinity",
      entrypoint="NostalgiaForInfinityNext",
      reference_path="reference/NostalgiaForInfinity/user_data/strategies/NostalgiaForInfinityNext.py",
      description="Direct reference wrapper for the upstream NostalgiaForInfinityNext Freqtrade strategy.",
    ),
    ReferenceStrategyDefinition(
      strategy_id="nfi_nextgen_reference",
      name="NostalgiaForInfinityNextGen",
      version="reference",
      reference_id="nostalgia-for-infinity",
      entrypoint="NostalgiaForInfinityNextGen",
      reference_path="reference/NostalgiaForInfinity/user_data/strategies/NostalgiaForInfinityNextGen.py",
      description="Direct reference wrapper for the upstream NostalgiaForInfinityNextGen Freqtrade strategy.",
    ),
  ]
  return [ReferenceFreqtradeStrategy(definition) for definition in definitions]
