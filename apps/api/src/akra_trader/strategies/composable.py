from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from math import isfinite
from typing import Any

import pandas as pd

from akra_trader.domain.models import ExecutionPlan
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec
from akra_trader.strategies.base import Strategy
from akra_trader.strategies.base import build_recent_feature_history


@dataclass(frozen=True)
class ParameterRef:
  name: str
  default: float | bool | str


Operand = str | int | float | ParameterRef


class Feature(ABC):
  name: str

  @abstractmethod
  def apply(self, frame: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
    raise NotImplementedError

  @abstractmethod
  def warmup_bars(self) -> int:
    raise NotImplementedError


@dataclass(frozen=True)
class EmaFeature(Feature):
  source: str
  name: str
  window_parameter: str
  default_window: int

  def apply(self, frame: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
    window = _parameter_int(parameters, self.window_parameter, self.default_window)
    frame[self.name] = frame[self.source].ewm(span=window, adjust=False).mean()
    return frame

  def warmup_bars(self) -> int:
    return self.default_window


@dataclass(frozen=True)
class SmaFeature(Feature):
  source: str
  name: str
  window_parameter: str
  default_window: int

  def apply(self, frame: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
    window = _parameter_int(parameters, self.window_parameter, self.default_window)
    frame[self.name] = frame[self.source].rolling(window=window, min_periods=1).mean()
    return frame

  def warmup_bars(self) -> int:
    return self.default_window


@dataclass(frozen=True)
class RsiFeature(Feature):
  source: str
  name: str
  window_parameter: str
  default_window: int
  timeframe_parameter: str | None = None
  default_timeframe: str = "base"

  def apply(self, frame: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
    window = _parameter_int(parameters, self.window_parameter, self.default_window)
    timeframe = _parameter_str(parameters, self.timeframe_parameter, self.default_timeframe)
    source_frame = _feature_source_frame(frame, source=self.source, timeframe=timeframe)
    rsi = _wilder_rsi(source_frame[self.source], window)
    feature_values = pd.DataFrame(
      {
        "timestamp": source_frame["timestamp"],
        self.name: rsi,
        f"{self.name}_previous": rsi.shift(1),
        f"{self.name}_previous2": rsi.shift(2),
      }
    )
    aligned = _align_feature_values(frame, feature_values)
    for column in (self.name, f"{self.name}_previous", f"{self.name}_previous2"):
      frame[column] = aligned[column].fillna(50.0).astype(float)
    return frame

  def warmup_bars(self) -> int:
    return self.default_window + 1


@dataclass(frozen=True)
class AtrFeature(Feature):
  name: str
  window_parameter: str
  default_window: int

  def apply(self, frame: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
    window = _parameter_int(parameters, self.window_parameter, self.default_window)
    previous_close = frame["close"].shift(1)
    true_range = pd.concat(
      [
        frame["high"] - frame["low"],
        (frame["high"] - previous_close).abs(),
        (frame["low"] - previous_close).abs(),
      ],
      axis=1,
    ).max(axis=1)
    frame[self.name] = true_range.rolling(window=window).mean()
    return frame

  def warmup_bars(self) -> int:
    return self.default_window + 1


class Rule(ABC):
  @abstractmethod
  def evaluate(self, context: StrategyDecisionContext) -> bool:
    raise NotImplementedError

  @abstractmethod
  def describe(self) -> dict[str, Any]:
    raise NotImplementedError


@dataclass(frozen=True)
class GreaterThan(Rule):
  left: Operand
  right: Operand

  def evaluate(self, context: StrategyDecisionContext) -> bool:
    left = _resolve_operand(context, self.left)
    right = _resolve_operand(context, self.right)
    return left is not None and right is not None and left > right

  def describe(self) -> dict[str, Any]:
    return {"operator": "gt", "left": _describe_operand(self.left), "right": _describe_operand(self.right)}


@dataclass(frozen=True)
class LessThan(Rule):
  left: Operand
  right: Operand

  def evaluate(self, context: StrategyDecisionContext) -> bool:
    left = _resolve_operand(context, self.left)
    right = _resolve_operand(context, self.right)
    return left is not None and right is not None and left < right

  def describe(self) -> dict[str, Any]:
    return {"operator": "lt", "left": _describe_operand(self.left), "right": _describe_operand(self.right)}


@dataclass(frozen=True)
class CrossAbove(Rule):
  left: Operand
  right: Operand

  def evaluate(self, context: StrategyDecisionContext) -> bool:
    previous_left = _resolve_previous_operand(context, self.left)
    previous_right = _resolve_previous_operand(context, self.right)
    current_left = _resolve_operand(context, self.left)
    current_right = _resolve_operand(context, self.right)
    return (
      previous_left is not None
      and previous_right is not None
      and current_left is not None
      and current_right is not None
      and previous_left <= previous_right
      and current_left > current_right
    )

  def describe(self) -> dict[str, Any]:
    return {"operator": "cross_above", "left": _describe_operand(self.left), "right": _describe_operand(self.right)}


@dataclass(frozen=True)
class CrossBelow(Rule):
  left: Operand
  right: Operand

  def evaluate(self, context: StrategyDecisionContext) -> bool:
    previous_left = _resolve_previous_operand(context, self.left)
    previous_right = _resolve_previous_operand(context, self.right)
    current_left = _resolve_operand(context, self.left)
    current_right = _resolve_operand(context, self.right)
    return (
      previous_left is not None
      and previous_right is not None
      and current_left is not None
      and current_right is not None
      and previous_left >= previous_right
      and current_left < current_right
    )

  def describe(self) -> dict[str, Any]:
    return {"operator": "cross_below", "left": _describe_operand(self.left), "right": _describe_operand(self.right)}


@dataclass(frozen=True)
class AllOf(Rule):
  rules: tuple[Rule, ...]

  def evaluate(self, context: StrategyDecisionContext) -> bool:
    return all(rule.evaluate(context) for rule in self.rules)

  def describe(self) -> dict[str, Any]:
    return {"operator": "all_of", "rules": [rule.describe() for rule in self.rules]}


@dataclass(frozen=True)
class AnyOf(Rule):
  rules: tuple[Rule, ...]

  def evaluate(self, context: StrategyDecisionContext) -> bool:
    return any(rule.evaluate(context) for rule in self.rules)

  def describe(self) -> dict[str, Any]:
    return {"operator": "any_of", "rules": [rule.describe() for rule in self.rules]}


@dataclass(frozen=True)
class RegimeDecision:
  allowed: bool
  label: str
  trace: dict[str, Any] = field(default_factory=dict)


class RegimeFilter(ABC):
  @abstractmethod
  def evaluate(self, context: StrategyDecisionContext) -> RegimeDecision:
    raise NotImplementedError


@dataclass(frozen=True)
class TrendRegime(RegimeFilter):
  fast_feature: str
  slow_feature: str
  direction: str = "long"

  def evaluate(self, context: StrategyDecisionContext) -> RegimeDecision:
    fast = _resolve_operand(context, self.fast_feature)
    slow = _resolve_operand(context, self.slow_feature)
    if fast is None or slow is None:
      return RegimeDecision(False, "trend_unknown", {"fast": fast, "slow": slow})
    allowed = fast > slow if self.direction == "long" else fast < slow
    return RegimeDecision(
      allowed=allowed,
      label=f"{self.direction}_trend" if allowed else f"not_{self.direction}_trend",
      trace={"fast": fast, "slow": slow},
    )


@dataclass(frozen=True)
class LlmRegimeHint(RegimeFilter):
  function_name: str
  enabled_parameter: str = "use_llm_regime_hint"

  def evaluate(self, context: StrategyDecisionContext) -> RegimeDecision:
    enabled = bool(context.state.parameters.get(self.enabled_parameter, True))
    if not enabled:
      return RegimeDecision(True, "llm_hint_disabled", {"enabled": False})
    result = context.llm.function(
      self.function_name,
      {
        "instrument_id": context.instrument_id,
        "timestamp": context.timestamp.isoformat(),
        "market": context.market,
        "features": {
          key: value
          for key, value in context.features.items()
          if key in {"close", "ema_fast", "ema_slow", "rsi", "atr"}
        },
      },
      fallback={"allow": True, "label": "systematic_fallback"},
      schema={"allow": "boolean", "label": "string"},
    )
    return RegimeDecision(
      allowed=bool(result.output.get("allow", True)),
      label=str(result.output.get("label", "llm_hint")),
      trace={
        "function": result.name,
        "provider": result.provider,
        "used_fallback": result.used_fallback,
        "output": result.output,
      },
    )


@dataclass(frozen=True)
class AllRegimes(RegimeFilter):
  regimes: tuple[RegimeFilter, ...]

  def evaluate(self, context: StrategyDecisionContext) -> RegimeDecision:
    decisions = [regime.evaluate(context) for regime in self.regimes]
    return RegimeDecision(
      allowed=all(decision.allowed for decision in decisions),
      label=";".join(decision.label for decision in decisions),
      trace={"regimes": [decision.trace | {"label": decision.label, "allowed": decision.allowed} for decision in decisions]},
    )


class SizingModel(ABC):
  @abstractmethod
  def build(self, context: StrategyDecisionContext, signal: SignalDecision) -> ExecutionPlan:
    raise NotImplementedError


@dataclass(frozen=True)
class AtrRiskSizing(SizingModel):
  atr_feature: str
  risk_fraction: ParameterRef
  stop_multiple: ParameterRef
  take_profit_multiple: ParameterRef
  max_position_fraction: ParameterRef

  def build(self, context: StrategyDecisionContext, signal: SignalDecision) -> ExecutionPlan:
    if signal.action == SignalAction.HOLD:
      return ExecutionPlan(size_fraction=0.0, tags=("composable", "no_action"))
    if signal.action == SignalAction.SELL:
      return ExecutionPlan(
        size_fraction=1.0,
        reduce_only=True,
        tags=("composable", "reduce_position"),
      )

    close = _resolve_operand(context, "close")
    atr = _resolve_operand(context, self.atr_feature)
    risk_fraction = _resolve_parameter(context, self.risk_fraction)
    stop_multiple = _resolve_parameter(context, self.stop_multiple)
    take_profit_multiple = _resolve_parameter(context, self.take_profit_multiple)
    max_fraction = _resolve_parameter(context, self.max_position_fraction)
    if close is None or atr is None or close <= 0 or atr <= 0:
      size_fraction = max_fraction
      stop_loss_pct = None
      take_profit_pct = None
    else:
      stop_loss_pct = min((atr * stop_multiple) / close, 1.0)
      take_profit_pct = min((atr * take_profit_multiple) / close, 1.0)
      size_fraction = min(max_fraction, risk_fraction / stop_loss_pct) if stop_loss_pct > 0 else max_fraction
    return ExecutionPlan(
      size_fraction=max(0.0, min(size_fraction, 1.0)),
      max_position_fraction=max(0.0, min(max_fraction, 1.0)),
      stop_loss_pct=stop_loss_pct,
      take_profit_pct=take_profit_pct,
      tags=("composable", "atr_risk_sizing"),
    )


@dataclass(frozen=True)
class StrategySpec:
  metadata: StrategyMetadata
  features: tuple[Feature, ...]
  entry: Rule
  exit: Rule
  regime: RegimeFilter
  sizing: SizingModel

  def warmup_bars(self) -> int:
    return max((feature.warmup_bars() for feature in self.features), default=2) + 2


class ComposableStrategy(Strategy):
  spec: StrategySpec

  def describe(self) -> StrategyMetadata:
    return self.spec.metadata

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(
      required_bars=self.spec.warmup_bars(),
      timeframes=self.spec.metadata.supported_timeframes,
    )

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    frame = candles.copy()
    for feature in self.spec.features:
      frame = feature.apply(frame, parameters)
    return frame

  def build_decision_context(
    self,
    candles: pd.DataFrame,
    parameters: dict,
    state: StrategyExecutionState,
  ) -> StrategyDecisionContext:
    latest = candles.iloc[-1]
    previous = candles.iloc[-2]
    features = _row_features(latest)
    features.update({f"previous_{key}": value for key, value in _row_features(previous).items()})
    if len(candles) >= 3:
      previous2 = candles.iloc[-3]
      features.update({f"previous2_{key}": value for key, value in _row_features(previous2).items()})
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
      recent_features=build_recent_feature_history(candles),
    )

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    regime = self.spec.regime.evaluate(context)
    entry_match = regime.allowed and self.spec.entry.evaluate(context)
    exit_match = self.spec.exit.evaluate(context)

    if context.state.has_position and exit_match:
      signal = SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.SELL,
        confidence=0.72,
        tags=("composable", "exit"),
        reason="composable_exit_rule_matched",
      )
    elif not context.state.has_position and entry_match:
      signal = SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.BUY,
        confidence=0.72,
        tags=("composable", "entry"),
        reason="composable_entry_rule_matched",
      )
    else:
      signal = SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.HOLD,
        confidence=0.55,
        tags=("composable", "idle"),
        reason="composable_conditions_not_met",
      )

    execution = self.spec.sizing.build(context, signal)
    return StrategyDecisionEnvelope(
      signal=signal,
      rationale=_rationale(signal, regime=regime, entry_match=entry_match, exit_match=exit_match),
      context=context,
      execution=execution,
      trace={
        "architecture": {
          "layers": (
            "feature_pipeline",
            "regime_filter",
            "signal_policy",
            "sizing_model",
            "execution_plan",
            "llm_function_layer",
          )
        },
        "regime": {"allowed": regime.allowed, "label": regime.label, "trace": regime.trace},
        "entry": {"matched": entry_match, "rule": self.spec.entry.describe()},
        "exit": {"matched": exit_match, "rule": self.spec.exit.describe()},
        "execution_tags": execution.tags,
      },
    )


def _parameter_int(parameters: dict[str, Any], key: str, default: int) -> int:
  value = parameters.get(key, default)
  return max(1, int(value))


def _parameter_str(parameters: dict[str, Any], key: str | None, default: str) -> str:
  if key is None:
    return default
  value = parameters.get(key, default)
  return str(value or default)


def _feature_source_frame(frame: pd.DataFrame, *, source: str, timeframe: str) -> pd.DataFrame:
  if _is_base_timeframe(timeframe):
    return frame[["timestamp", source]].copy()
  target_delta = _parse_timeframe_delta(timeframe)
  if target_delta is None:
    raise ValueError(f"Unsupported feature timeframe: {timeframe}")
  base_delta = _infer_frame_delta(frame)
  if base_delta is None:
    raise ValueError("At least two candles are required for timeframed feature calculation.")
  if target_delta < base_delta:
    raise ValueError(
      f"Cannot calculate {timeframe} feature from base candles spaced {base_delta} apart."
    )
  ratio = target_delta / base_delta
  if ratio != int(ratio):
    raise ValueError(
      f"Feature timeframe {timeframe} must be an exact multiple of base candle spacing {base_delta}."
    )
  ratio_int = max(1, int(ratio))
  if ratio_int == 1:
    return frame[["timestamp", source]].copy()

  working = frame[["timestamp", source]].copy()
  working["timestamp"] = pd.to_datetime(working["timestamp"], utc=True)
  working = working.sort_values("timestamp").reset_index(drop=True)
  working["__feature_group"] = working.index // ratio_int
  return (
    working.groupby("__feature_group", as_index=False)
    .agg(timestamp=("timestamp", "last"), **{source: (source, "last")})
    [["timestamp", source]]
  )


def _wilder_rsi(values: pd.Series, window: int) -> pd.Series:
  delta = values.astype(float).diff()
  gain = delta.clip(lower=0)
  loss = -delta.clip(upper=0)
  average_gain = _wilder_average(gain, window)
  average_loss = _wilder_average(loss, window)
  relative_strength = average_gain / average_loss.mask(average_loss == 0)
  rsi = 100 - (100 / (1 + relative_strength))
  rsi = rsi.mask((average_loss == 0) & (average_gain > 0), 100.0)
  rsi = rsi.mask((average_loss == 0) & (average_gain == 0), 50.0)
  return rsi.fillna(50.0).astype(float)


def _wilder_average(values: pd.Series, window: int) -> pd.Series:
  result = pd.Series(index=values.index, dtype=float)
  if len(values) <= window:
    return result
  initial_average = values.iloc[1 : window + 1].mean()
  result.iloc[window] = initial_average
  previous_average = initial_average
  for position in range(window + 1, len(values)):
    current = values.iloc[position]
    if pd.isna(current):
      result.iloc[position] = previous_average
      continue
    previous_average = ((previous_average * (window - 1)) + current) / window
    result.iloc[position] = previous_average
  return result


def _align_feature_values(frame: pd.DataFrame, feature_values: pd.DataFrame) -> pd.DataFrame:
  base = frame[["timestamp"]].copy()
  base["__row_index"] = range(len(base))
  base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True)
  values = feature_values.copy()
  values["timestamp"] = pd.to_datetime(values["timestamp"], utc=True)
  aligned = pd.merge_asof(
    base.sort_values("timestamp"),
    values.sort_values("timestamp"),
    on="timestamp",
    direction="backward",
  )
  return aligned.sort_values("__row_index").reset_index(drop=True)


def _is_base_timeframe(timeframe: str) -> bool:
  return timeframe.strip().lower() in {"", "base", "native", "run"}


def _parse_timeframe_delta(timeframe: str) -> pd.Timedelta | None:
  value = timeframe.strip()
  if not value or value == "1M":
    return None
  amount_text = value[:-1]
  unit = value[-1]
  if not amount_text.isdigit():
    return None
  amount = int(amount_text)
  if amount <= 0:
    return None
  if unit == "m":
    return pd.Timedelta(minutes=amount)
  if unit == "h":
    return pd.Timedelta(hours=amount)
  if unit == "d":
    return pd.Timedelta(days=amount)
  if unit == "w":
    return pd.Timedelta(weeks=amount)
  return None


def _infer_frame_delta(frame: pd.DataFrame) -> pd.Timedelta | None:
  if len(frame) < 2:
    return None
  timestamps = pd.to_datetime(frame["timestamp"], utc=True).sort_values()
  deltas = timestamps.diff().dropna()
  if deltas.empty:
    return None
  return deltas.value_counts().index[0]


def _resolve_parameter(context: StrategyDecisionContext, parameter: ParameterRef) -> float:
  value = context.state.parameters.get(parameter.name, parameter.default)
  return float(value)


def _resolve_operand(context: StrategyDecisionContext, operand: Operand) -> float | None:
  if isinstance(operand, ParameterRef):
    return _resolve_parameter(context, operand)
  if isinstance(operand, str):
    return _finite_float(context.features.get(operand))
  return _finite_float(operand)


def _resolve_previous_operand(context: StrategyDecisionContext, operand: Operand) -> float | None:
  if isinstance(operand, ParameterRef):
    return _resolve_parameter(context, operand)
  if isinstance(operand, str):
    return _finite_float(context.features.get(f"previous_{operand}"))
  return _finite_float(operand)


def _finite_float(value: Any) -> float | None:
  try:
    number = float(value)
  except (TypeError, ValueError):
    return None
  return number if isfinite(number) else None


def _describe_operand(operand: Operand) -> Any:
  if isinstance(operand, ParameterRef):
    return {"parameter": operand.name, "default": operand.default}
  return operand


def _row_features(row: pd.Series) -> dict[str, Any]:
  features: dict[str, Any] = {}
  for key, value in row.to_dict().items():
    if hasattr(value, "item"):
      value = value.item()
    features[key] = value
  return features


def _rationale(
  signal: SignalDecision,
  *,
  regime: RegimeDecision,
  entry_match: bool,
  exit_match: bool,
) -> str:
  return (
    f"Composable strategy signal={signal.action.value}; "
    f"regime={regime.label}; entry={entry_match}; exit={exit_match}."
  )
