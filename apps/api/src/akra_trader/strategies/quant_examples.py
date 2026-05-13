from __future__ import annotations

from math import isfinite
from typing import Any

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyCatalogSemantics
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.strategies.composable import AllOf
from akra_trader.strategies.composable import AllRegimes
from akra_trader.strategies.composable import AnyOf
from akra_trader.strategies.composable import AtrFeature
from akra_trader.strategies.composable import AtrRiskSizing
from akra_trader.strategies.composable import ComposableStrategy
from akra_trader.strategies.composable import CrossBelow
from akra_trader.strategies.composable import EmaFeature
from akra_trader.strategies.composable import GreaterThan
from akra_trader.strategies.composable import LessThan
from akra_trader.strategies.composable import LlmRegimeHint
from akra_trader.strategies.composable import ParameterRef
from akra_trader.strategies.composable import RsiFeature
from akra_trader.strategies.composable import StrategySpec
from akra_trader.strategies.composable import TrendRegime


class RsiAtrOversoldPeakTurnStrategy(ComposableStrategy):
  spec = StrategySpec(
    metadata=StrategyMetadata(
      strategy_id="rsi_atr_oversold_peak_turn_v1",
      name="RSI ATR Oversold Peak Turn",
      version="1.0.0",
      runtime="native_composable",
      asset_types=(AssetType.CRYPTO,),
      supported_timeframes=("1m", "3m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"),
      parameter_schema={
        "fast_ema_window": {
          "type": "integer",
          "default": 20,
          "minimum": 2,
          "unit": "bars",
          "semantic_hint": "Fast trend leg.",
          "description_ko": "단기 EMA 기간입니다. 값이 작을수록 최근 가격 변화에 더 빠르게 반응합니다.",
        },
        "slow_ema_window": {
          "type": "integer",
          "default": 60,
          "minimum": 5,
          "unit": "bars",
          "semantic_hint": "Slow trend regime baseline.",
          "description_ko": "장기 EMA 기간입니다. 단기 EMA가 이 값보다 위에 있을 때 상승 추세로 봅니다.",
        },
        "rsi_window": {
          "type": "integer",
          "default": 14,
          "minimum": 2,
          "unit": "bars",
          "semantic_hint": "Wilder/RMA RSI oscillator lookback.",
          "description_ko": "Wilder/RMA 방식 RSI 계산 기간입니다. 과매도 구간과 RSI 고점 꺾임을 판단하는 기준입니다.",
        },
        "rsi_timeframe": {
          "type": "string",
          "default": "base",
          "enum": ["base", "5m", "15m", "1h", "4h", "1d"],
          "semantic_hint": "Timeframe used for RSI calculation.",
          "description_ko": "RSI를 계산할 봉 기준입니다. base는 백테스트/실행 봉과 같은 기준이며, 15m처럼 실행 봉보다 큰 기준은 내부에서 리샘플링해 계산합니다.",
        },
        "atr_window": {
          "type": "integer",
          "default": 14,
          "minimum": 2,
          "unit": "bars",
          "semantic_hint": "Volatility risk lookback.",
          "description_ko": "ATR 변동성 계산 기간입니다. 손절, 익절, 포지션 크기 산정에 사용됩니다.",
        },
        "rsi_oversold_level": {
          "type": "number",
          "default": 30,
          "minimum": 0,
          "maximum": 100,
          "semantic_hint": "Previous RSI peak must be below this oversold ceiling.",
          "description_ko": "과매도 기준선입니다. 직전 RSI 고점이 이 값보다 낮은 과매도 구간 안에 있을 때만 매수 후보가 됩니다.",
        },
        "rsi_exit_level": {
          "type": "number",
          "default": 45,
          "minimum": 0,
          "maximum": 100,
          "semantic_hint": "RSI weakness level used by the scored exit model.",
          "description_ko": "청산 RSI 기준선입니다. 보유 중 RSI가 이 값을 아래로 이탈하면 청산 후보가 됩니다.",
        },
        "exit_score_threshold": {
          "type": "number",
          "default": 0.75,
          "minimum": 0,
          "maximum": 1,
          "semantic_hint": "SELL score threshold for full-position exits.",
          "description_ko": "SELL 점수 임계값입니다. 하드스톱이 아닌 청산은 점수가 이 값 이상일 때 전량 SELL합니다.",
        },
        "risk_fraction": {
          "type": "number",
          "default": 0.01,
          "minimum": 0,
          "maximum": 1,
          "semantic_hint": "Portfolio risk budget per trade.",
          "description_ko": "거래 1회당 감수할 포트폴리오 위험 비율입니다. 0.01은 1% 위험 예산입니다.",
        },
        "max_position_fraction": {
          "type": "number",
          "default": 0.5,
          "minimum": 0,
          "maximum": 1,
          "semantic_hint": "Maximum notional allocation for this strategy.",
          "description_ko": "전략이 사용할 수 있는 최대 포지션 비중입니다. 0.5는 자산의 50% 한도입니다.",
        },
        "atr_stop_multiple": {
          "type": "number",
          "default": 2.0,
          "minimum": 0.1,
          "semantic_hint": "ATR multiple used for stop distance.",
          "description_ko": "손절 거리에 곱할 ATR 배수입니다. 값이 클수록 손절 폭이 넓어집니다.",
        },
        "atr_take_profit_multiple": {
          "type": "number",
          "default": 3.0,
          "minimum": 0.1,
          "semantic_hint": "ATR multiple used for take-profit distance.",
          "description_ko": "익절 거리에 곱할 ATR 배수입니다. 값이 클수록 목표 수익 폭이 넓어집니다.",
        },
        "use_llm_regime_hint": {
          "type": "boolean",
          "default": True,
          "semantic_hint": "Calls context.llm.function() as an optional regime overlay.",
          "description_ko": "LLM 시장 국면 힌트를 보조 필터로 사용할지 여부입니다. 실패하면 deterministic 규칙으로 되돌아갑니다.",
        },
      },
      description=(
        "Composable sample strategy: EMA uptrend regime, RSI oversold peak turn-down entry, ATR risk sizing, "
        "and an optional llm.function() regime hint."
      ),
      lifecycle=StrategyLifecycle(stage="experimental"),
      catalog_semantics=StrategyCatalogSemantics(
        strategy_kind="composable_quant",
        execution_model=(
          "FeaturePipeline -> RegimeFilter -> SignalPolicy -> SizingModel -> ExecutionPlan. "
          "The strategy logic is declarative and composed from SDK primitives."
        ),
        parameter_contract="Typed parameter schema drives defaults, runtime overrides, and future UI controls.",
        source_descriptor="akra_trader.strategies.quant_examples:RsiAtrOversoldPeakTurnStrategy",
        operator_notes=(
          "Long entry requires EMA uptrend plus a local RSI peak that forms below the oversold ceiling and then turns down.",
          "LLM hints are optional overlays and fall back to deterministic systematic rules.",
        ),
      ),
      version_lineage=("1.0.0",),
      entrypoint="akra_trader.strategies.quant_examples:RsiAtrOversoldPeakTurnStrategy",
    ),
    features=(
      EmaFeature("close", "ema_fast", "fast_ema_window", 20),
      EmaFeature("close", "ema_slow", "slow_ema_window", 60),
      RsiFeature(
        "close",
        "rsi",
        "rsi_window",
        14,
        timeframe_parameter="rsi_timeframe",
        default_timeframe="base",
      ),
      AtrFeature("atr", "atr_window", 14),
    ),
    regime=AllRegimes(
      (
        TrendRegime("ema_fast", "ema_slow", direction="long"),
        LlmRegimeHint("trend_pullback_regime_hint"),
      )
    ),
    entry=AllOf(
      (
        GreaterThan("ema_fast", "ema_slow"),
        LessThan("rsi_previous", ParameterRef("rsi_oversold_level", 30)),
        GreaterThan("rsi_previous", "rsi_previous2"),
        GreaterThan("rsi_previous", "rsi"),
      )
    ),
    exit=AnyOf(
      (
        CrossBelow("rsi", ParameterRef("rsi_exit_level", 45)),
        CrossBelow("ema_fast", "ema_slow"),
      )
    ),
    sizing=AtrRiskSizing(
      atr_feature="atr",
      risk_fraction=ParameterRef("risk_fraction", 0.01),
      stop_multiple=ParameterRef("atr_stop_multiple", 2.0),
      take_profit_multiple=ParameterRef("atr_take_profit_multiple", 3.0),
      max_position_fraction=ParameterRef("max_position_fraction", 0.5),
    ),
  )

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    regime = self.spec.regime.evaluate(context)
    entry_match = regime.allowed and self.spec.entry.evaluate(context)
    exit_evaluation = _rsi_atr_exit_evaluation(context)
    exit_match = bool(exit_evaluation["matched"])

    if context.state.has_position and exit_match:
      signal = SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.SELL,
        confidence=max(0.72, float(exit_evaluation["score"])),
        tags=("composable", "exit", str(exit_evaluation["reason"])),
        reason=str(exit_evaluation["reason"]),
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
      rationale=_rsi_atr_rationale(
        signal,
        regime_label=regime.label,
        entry_match=entry_match,
        exit_evaluation=exit_evaluation,
      ),
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
        "exit": exit_evaluation,
        "execution_tags": execution.tags,
      },
    )


class RsiAtrTrendPullbackStrategy(RsiAtrOversoldPeakTurnStrategy):
  """Backward-compatible import alias for the renamed built-in strategy."""


def _rsi_atr_exit_evaluation(context: StrategyDecisionContext) -> dict[str, Any]:
  threshold = _clamped_parameter(context, "exit_score_threshold", 0.75, minimum=0.0, maximum=1.0)
  close = _feature_or_market(context, "close")
  hard_stop_price = _finite_number(context.state.position_stop_loss_price)
  take_profit_price = _finite_number(context.state.position_take_profit_price)
  components: dict[str, dict[str, Any]] = {}

  if not context.state.has_position:
    return {
      "matched": False,
      "score": 0.0,
      "threshold": threshold,
      "reason": "no_position",
      "components": components,
      "hard_stop_price": hard_stop_price,
      "take_profit_price": take_profit_price,
    }
  if close is None:
    return {
      "matched": False,
      "score": 0.0,
      "threshold": threshold,
      "reason": "close_unavailable",
      "components": components,
      "hard_stop_price": hard_stop_price,
      "take_profit_price": take_profit_price,
    }
  if hard_stop_price is not None and close <= hard_stop_price:
    components["hard_stop"] = _exit_component(
      True,
      1.0,
      close=close,
      stop_loss_price=hard_stop_price,
    )
    return {
      "matched": True,
      "score": 1.0,
      "threshold": threshold,
      "reason": "hard_stop",
      "components": components,
      "hard_stop_price": hard_stop_price,
      "take_profit_price": take_profit_price,
    }

  ema_fast = _feature_value(context, "ema_fast")
  ema_slow = _feature_value(context, "ema_slow")
  previous_ema_fast = _feature_value(context, "previous_ema_fast")
  previous_ema_slow = _feature_value(context, "previous_ema_slow")
  rsi = _feature_value(context, "rsi")
  previous_rsi = _feature_value(context, "previous_rsi")
  atr = _feature_value(context, "atr")
  entry_price = _finite_number(context.state.position_average_price)
  rsi_exit_level = _clamped_parameter(context, "rsi_exit_level", 45.0, minimum=0.0, maximum=100.0)

  current_spread = (
    ema_fast - ema_slow
    if ema_fast is not None and ema_slow is not None
    else None
  )
  previous_spread = (
    previous_ema_fast - previous_ema_slow
    if previous_ema_fast is not None and previous_ema_slow is not None
    else None
  )
  trend_break = current_spread is not None and current_spread < 0
  trend_decay = (
    current_spread is not None
    and previous_spread is not None
    and current_spread < previous_spread
  )
  rsi_failure = (
    rsi is not None
    and previous_rsi is not None
    and rsi < rsi_exit_level
    and rsi < previous_rsi
  )
  adverse_move = entry_price - close if entry_price is not None else None
  adverse_atr_multiple = (
    adverse_move / atr
    if adverse_move is not None and adverse_move > 0 and atr is not None and atr > 0
    else None
  )
  adverse_price = adverse_atr_multiple is not None and adverse_atr_multiple >= 0.25
  profit_protection = (
    take_profit_price is not None
    and close >= take_profit_price * 0.98
    and rsi is not None
    and previous_rsi is not None
    and rsi < previous_rsi
  )

  components["trend_break"] = _exit_component(
    trend_break,
    0.35,
    ema_fast=ema_fast,
    ema_slow=ema_slow,
    spread=current_spread,
  )
  components["trend_decay"] = _exit_component(
    trend_decay,
    0.15,
    spread=current_spread,
    previous_spread=previous_spread,
  )
  components["rsi_failure"] = _exit_component(
    rsi_failure,
    0.25,
    rsi=rsi,
    previous_rsi=previous_rsi,
    rsi_exit_level=rsi_exit_level,
  )
  components["adverse_price"] = _exit_component(
    adverse_price,
    0.20,
    close=close,
    entry_price=entry_price,
    atr=atr,
    adverse_atr_multiple=adverse_atr_multiple,
  )
  components["profit_protection"] = _exit_component(
    profit_protection,
    0.15,
    close=close,
    take_profit_price=take_profit_price,
    rsi=rsi,
    previous_rsi=previous_rsi,
  )

  score = round(min(sum(component["score"] for component in components.values()), 1.0), 4)
  active_reasons = tuple(
    name for name, component in components.items() if bool(component["active"])
  )
  matched = score >= threshold
  reason = (
    f"exit_score_threshold_met:{','.join(active_reasons)}"
    if matched
    else "exit_score_below_threshold"
  )
  return {
    "matched": matched,
    "score": score,
    "threshold": threshold,
    "reason": reason,
    "components": components,
    "hard_stop_price": hard_stop_price,
    "take_profit_price": take_profit_price,
  }


def _exit_component(active: bool, weight: float, **details: Any) -> dict[str, Any]:
  return {
    "active": active,
    "score": weight if active else 0.0,
    "weight": weight,
    **details,
  }


def _rsi_atr_rationale(
  signal: SignalDecision,
  *,
  regime_label: str,
  entry_match: bool,
  exit_evaluation: dict[str, Any],
) -> str:
  score = float(exit_evaluation["score"])
  threshold = float(exit_evaluation["threshold"])
  active_components = [
    name
    for name, component in exit_evaluation["components"].items()
    if bool(component.get("active"))
  ]
  component_summary = ",".join(active_components) if active_components else "none"
  return (
    f"Composable strategy signal={signal.action.value}; "
    f"regime={regime_label}; entry={entry_match}; exit={exit_evaluation['matched']}; "
    f"exit_score={score:.2f}/{threshold:.2f}; "
    f"exit_reason={exit_evaluation['reason']}; exit_components={component_summary}."
  )


def _feature_or_market(context: StrategyDecisionContext, key: str) -> float | None:
  feature_value = _feature_value(context, key)
  if feature_value is not None:
    return feature_value
  return _finite_number(context.market.get(key))


def _feature_value(context: StrategyDecisionContext, key: str) -> float | None:
  return _finite_number(context.features.get(key))


def _clamped_parameter(
  context: StrategyDecisionContext,
  key: str,
  default: float,
  *,
  minimum: float,
  maximum: float,
) -> float:
  value = _finite_number(context.state.parameters.get(key, default))
  if value is None:
    value = default
  return min(max(value, minimum), maximum)


def _finite_number(value: Any) -> float | None:
  try:
    number = float(value)
  except (TypeError, ValueError):
    return None
  return number if isfinite(number) else None
