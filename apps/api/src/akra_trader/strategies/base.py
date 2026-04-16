from __future__ import annotations

from abc import ABC
from abc import abstractmethod

import pandas as pd

from akra_trader.domain.models import ExecutionPlan
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


class SignalPolicy(ABC):
  @abstractmethod
  def decide(self, context: StrategyDecisionContext) -> SignalDecision:
    raise NotImplementedError


class ExecutionPolicy(ABC):
  def build(self, context: StrategyDecisionContext, signal: SignalDecision) -> ExecutionPlan:
    return ExecutionPlan(size_fraction=signal.size_fraction)


class FixedFractionExecutionPolicy(ExecutionPolicy):
  def __init__(
    self,
    *,
    size_fraction: float = 1.0,
    allow_scale_in: bool = False,
    allow_partial_exit: bool = False,
    reduce_only: bool = False,
    exit_mode: str | None = None,
    tags: tuple[str, ...] = (),
  ) -> None:
    self._size_fraction = size_fraction
    self._allow_scale_in = allow_scale_in
    self._allow_partial_exit = allow_partial_exit
    self._reduce_only = reduce_only
    self._exit_mode = exit_mode
    self._tags = tags

  def build(self, context: StrategyDecisionContext, signal: SignalDecision) -> ExecutionPlan:
    return ExecutionPlan(
      size_fraction=self._size_fraction,
      allow_scale_in=self._allow_scale_in,
      allow_partial_exit=self._allow_partial_exit,
      reduce_only=self._reduce_only,
      exit_mode=self._exit_mode,
      tags=self._tags,
    )


class PolicyBackedStrategy(Strategy, ABC):
  @abstractmethod
  def signal_policy(self, parameters: dict) -> SignalPolicy:
    raise NotImplementedError

  def execution_policy(self, parameters: dict) -> ExecutionPolicy:
    return FixedFractionExecutionPolicy()

  def build_trace(
    self,
    context: StrategyDecisionContext,
    signal: SignalDecision,
    execution: ExecutionPlan,
  ) -> dict:
    return {"signal_tags": signal.tags, "execution_tags": execution.tags}

  def build_rationale(self, context: StrategyDecisionContext, signal: SignalDecision) -> str:
    return signal.reason or f"signal:{signal.action.value}"

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    parameters = context.state.parameters
    signal = self.signal_policy(parameters).decide(context)
    execution = self.execution_policy(parameters).build(context, signal)
    return StrategyDecisionEnvelope(
      signal=signal,
      rationale=self.build_rationale(context, signal),
      context=context,
      execution=execution,
      trace=self.build_trace(context, signal, execution),
    )
