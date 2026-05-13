from __future__ import annotations

from math import isfinite
from typing import Any

import pandas as pd

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
from akra_trader.strategies.composable import SmaFeature
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
        "entry_min_trend_spread_atr": {
          "type": "number",
          "default": 0.5,
          "minimum": 0,
          "semantic_hint": "Minimum fast/slow EMA spread measured in ATR units for BUY.",
          "description_ko": "매수 추세 강도 최소값입니다. 단기 EMA와 장기 EMA 간격이 ATR의 이 배수 이상일 때만 매수합니다.",
        },
        "entry_enable_rsi_recovery": {
          "type": "boolean",
          "default": True,
          "semantic_hint": "Allows BUY when RSI rebounds from below the oversold level.",
          "description_ko": "RSI가 과매도권에서 반등할 때도 매수를 허용합니다. 매수 기회를 늘리는 진입 패턴입니다.",
        },
        "entry_require_price_above_slow_ema": {
          "type": "boolean",
          "default": False,
          "semantic_hint": "Requires close to stay above the slow EMA before BUY.",
          "description_ko": "매수 전 현재가가 장기 EMA 위에 있어야 하는지 여부입니다. 약한 추세에서의 조기 진입을 줄입니다.",
        },
        "entry_enable_range_oversold_recovery": {
          "type": "boolean",
          "default": False,
          "semantic_hint": "Allows range-style BUY near the local low when RSI starts recovering from oversold.",
          "description_ko": "횡보/약한 하락 구간에서 RSI가 과매도권에서 회복하고 가격이 최근 저점에서 멀지 않을 때 매수를 허용합니다.",
        },
        "entry_recovery_max_rsi": {
          "type": "number",
          "default": 38,
          "minimum": 0,
          "maximum": 100,
          "semantic_hint": "Maximum current RSI allowed for early oversold recovery entries.",
          "description_ko": "과매도 회복 매수의 최대 RSI입니다. 값이 낮을수록 반등 초입에 더 가깝게 진입합니다.",
        },
        "entry_recovery_max_low_proximity_atr": {
          "type": "number",
          "default": 1.5,
          "minimum": 0,
          "maximum": 10,
          "semantic_hint": "Maximum distance from the recent local low in ATR units for recovery entries.",
          "description_ko": "과매도 회복 매수 시 최근 저점 대비 허용 거리입니다. 현재가가 최근 저점에서 ATR의 이 배수 이상 멀면 진입하지 않습니다.",
        },
        "entry_recovery_min_trend_spread_atr": {
          "type": "number",
          "default": -2.0,
          "minimum": -10,
          "maximum": 10,
          "semantic_hint": "Minimum fast/slow EMA spread in ATR units for range-style recovery entries.",
          "description_ko": "과매도 회복 매수에서 허용할 최소 EMA 스프레드입니다. 너무 강한 하락 추세를 피하기 위한 하한입니다.",
        },
        "entry_recovery_min_rsi_delta": {
          "type": "number",
          "default": 5.0,
          "minimum": 0,
          "maximum": 100,
          "semantic_hint": "Minimum RSI rebound from the previous candle for range-style recovery entries.",
          "description_ko": "과매도 회복 매수에서 요구하는 RSI 반등폭입니다. 직전 봉보다 RSI가 이 값 이상 상승해야 합니다.",
        },
        "entry_recovery_min_close_position": {
          "type": "number",
          "default": 0.7,
          "minimum": 0,
          "maximum": 1,
          "semantic_hint": "Minimum candle close position from low to high for range-style recovery entries.",
          "description_ko": "과매도 회복 매수에서 요구하는 캔들 마감 위치입니다. 0.7은 봉의 저가~고가 구간 상위 30%에 마감해야 함을 뜻합니다.",
        },
        "exit_score_threshold": {
          "type": "number",
          "default": 0.75,
          "minimum": 0,
          "maximum": 1,
          "semantic_hint": "SELL score threshold for full-position exits.",
          "description_ko": "SELL 점수 임계값입니다. 하드스톱이 아닌 청산은 점수가 이 값 이상일 때 전량 SELL합니다.",
        },
        "exit_trailing_activation_atr": {
          "type": "number",
          "default": 1.5,
          "minimum": 0,
          "maximum": 10,
          "semantic_hint": "ATR profit multiple required before the trailing stop activates.",
          "description_ko": "트레일링 활성화 수익폭입니다. 진입가 대비 ATR의 이 배수 이상 유리해지면 트레일링 스톱을 켭니다.",
        },
        "exit_trailing_distance_atr": {
          "type": "number",
          "default": 2.0,
          "minimum": 0.1,
          "maximum": 10,
          "semantic_hint": "ATR distance kept below the high-watermark once trailing is active.",
          "description_ko": "트레일링 스톱 거리입니다. 최고가에서 ATR의 이 배수만큼 되돌리면 전량 SELL합니다.",
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
          "Long entry supports oversold RSI peak-turn and oversold RSI recovery patterns, "
          "with optional trend-strength filters.",
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
    entry_evaluation = _rsi_atr_entry_evaluation(
      context,
      regime_allowed=regime.allowed,
      rule_matched=self.spec.entry.evaluate(context),
      rule=self.spec.entry.describe(),
    )
    entry_match = bool(entry_evaluation["matched"])
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
        entry_evaluation=entry_evaluation,
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
        "entry": entry_evaluation,
        "exit": exit_evaluation,
        "execution_tags": execution.tags,
      },
    )


class RsiAtrTrendPullbackStrategy(RsiAtrOversoldPeakTurnStrategy):
  """Backward-compatible import alias for the renamed built-in strategy."""


class Rsi14OversoldReversalStrategy(ComposableStrategy):
  spec = StrategySpec(
    metadata=StrategyMetadata(
      strategy_id="rsi14_oversold_reversal_v1",
      name="RSI14 과매도 탈출 반등 매수",
      version="1.0.0",
      runtime="native_composable",
      asset_types=(AssetType.CRYPTO,),
      supported_timeframes=("1m", "3m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"),
      parameter_schema={
        "ma20_window": {
          "type": "integer",
          "default": 20,
          "minimum": 2,
          "unit": "bars",
          "semantic_hint": "Short moving average used for rebound validation.",
          "description_ko": "MA20 기간입니다. 과매도 탈출 후 가격 구조 반전과 저항 도달 청산에 사용합니다.",
        },
        "ma60_window": {
          "type": "integer",
          "default": 60,
          "minimum": 5,
          "unit": "bars",
          "semantic_hint": "Long moving average used for downtrend filtering.",
          "description_ko": "MA60 기간입니다. 장기 하락 추세 차단과 저항 도달 청산에 사용합니다.",
        },
        "rsi_window": {
          "type": "integer",
          "default": 14,
          "minimum": 2,
          "unit": "bars",
          "semantic_hint": "Wilder/RMA RSI lookback for oversold escape detection.",
          "description_ko": "RSI 계산 기간입니다. 기본값 14로 RSI14 과매도 탈출을 탐지합니다.",
        },
        "rsi_timeframe": {
          "type": "string",
          "default": "base",
          "enum": ["base", "5m", "15m", "1h", "4h", "1d"],
          "semantic_hint": "Timeframe used for RSI calculation.",
          "description_ko": "RSI를 계산할 봉 기준입니다. base는 백테스트/실행 봉과 같은 기준입니다.",
        },
        "atr_window": {
          "type": "integer",
          "default": 14,
          "minimum": 2,
          "unit": "bars",
          "semantic_hint": "ATR volatility lookback for risk sizing and ATR stop exits.",
          "description_ko": "ATR14 변동성 계산 기간입니다. 진입가 - 1.5 * ATR 손절과 포지션 크기 산정에 사용합니다.",
        },
        "rsi_oversold_level": {
          "type": "number",
          "default": 30,
          "minimum": 0,
          "maximum": 100,
          "semantic_hint": "RSI level defining oversold setup and escape trigger.",
          "description_ko": "과매도 기준선입니다. 최근 N봉 안에 RSI가 이 값 이하로 내려갔다가 다시 상향 돌파해야 합니다.",
        },
        "entry_lookback_bars": {
          "type": "integer",
          "default": 10,
          "minimum": 1,
          "maximum": 30,
          "unit": "bars",
          "semantic_hint": "Recent bar window in which RSI must have reached oversold.",
          "description_ko": "과매도 발생을 확인할 최근 봉 수입니다. 기본값은 최근 10봉입니다.",
        },
        "swing_lookback_bars": {
          "type": "integer",
          "default": 5,
          "minimum": 2,
          "maximum": 20,
          "unit": "bars",
          "semantic_hint": "Lookback used to define recent swing-low stop and lower-low structure.",
          "description_ko": "최근 스윙 저점과 저점 하락 구조를 판단할 봉 수입니다.",
        },
        "trend_slope_lookback_bars": {
          "type": "integer",
          "default": 3,
          "minimum": 1,
          "maximum": 20,
          "unit": "bars",
          "semantic_hint": "Lookback used to measure MA20 slope.",
          "description_ko": "MA20 기울기를 측정할 봉 수입니다.",
        },
        "exit_rsi_profit_level": {
          "type": "number",
          "default": 50,
          "minimum": 0,
          "maximum": 100,
          "semantic_hint": "RSI level used to take profit after oversold escape.",
          "description_ko": "익절 RSI 기준선입니다. 보유 중 RSI14가 이 값 이상이고 수익 상태면 전량 SELL합니다.",
        },
        "exit_profit_r_multiple": {
          "type": "number",
          "default": 1.5,
          "minimum": 0.1,
          "maximum": 5,
          "semantic_hint": "Profit target measured in initial risk R.",
          "description_ko": "초기 위험 R 기준 익절 배수입니다. 1.5는 진입 위험의 1.5배 수익에서 청산합니다.",
        },
        "exit_time_stop_bars": {
          "type": "integer",
          "default": 7,
          "minimum": 1,
          "maximum": 50,
          "unit": "bars",
          "semantic_hint": "Bars allowed after entry before exiting if the trade has not turned profitable.",
          "description_ko": "진입 후 수익 전환을 기다릴 봉 수입니다. 기본값은 7봉입니다.",
        },
        "cooldown_after_stop_bars": {
          "type": "integer",
          "default": 5,
          "minimum": 0,
          "maximum": 50,
          "unit": "bars",
          "semantic_hint": "Bars to block re-entry after a stop-loss exit.",
          "description_ko": "손절 후 재진입을 금지할 봉 수입니다. 기본값은 5봉입니다.",
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
          "default": 1.5,
          "minimum": 0.1,
          "maximum": 10,
          "semantic_hint": "ATR multiple used for fixed stop distance.",
          "description_ko": "ATR 손절 배수입니다. 기본값은 진입가 - 1.5 * ATR14 손절입니다.",
        },
        "atr_take_profit_multiple": {
          "type": "number",
          "default": 3.0,
          "minimum": 0.1,
          "semantic_hint": "Compatibility take-profit distance stored on the position.",
          "description_ko": "포지션에 저장되는 보조 익절 기준입니다. 실제 청산은 RSI50, R배수, MA저항, 시간청산을 우선합니다.",
        },
      },
      description=(
        "RSI14 oversold escape rebound setup: RSI recently oversold, RSI crosses back above 30, "
        "close breaks the previous high, trend filter allows the rebound, and exits are stop/R/time/profit based."
      ),
      lifecycle=StrategyLifecycle(stage="experimental"),
      catalog_semantics=StrategyCatalogSemantics(
        strategy_kind="composable_quant",
        execution_model=(
          "FeaturePipeline -> RSIOversoldEscapeSignalPolicy -> ATRRiskSizing -> "
          "Stop/Profit/TimeExitPolicy. The strategy avoids treating every RSI bounce as a trend reversal."
        ),
        parameter_contract="Typed parameter schema exposes oversold lookback, swing stop, R target, time stop, and cooldown controls.",
        source_descriptor="akra_trader.strategies.quant_examples:Rsi14OversoldReversalStrategy",
        operator_notes=(
          "BUY requires RSI14 to have been oversold within 10 bars, RSI14 to cross back above 30, and close to break the previous high.",
          "Trend filter passes when close is above MA20, close is above MA60, or MA20 slope is non-negative.",
          "Entries are blocked when close is below MA60, MA20 slope is falling, and recent lows continue to make lower lows.",
          "SELL uses swing-low stop, fixed 1.5 ATR stop, RSI50/R-target/MA-resistance profit exits, 7-bar no-profit time exit, and 5-bar stop cooldown.",
        ),
      ),
      version_lineage=("1.0.0",),
      entrypoint="akra_trader.strategies.quant_examples:Rsi14OversoldReversalStrategy",
    ),
    features=(
      SmaFeature("close", "ma20", "ma20_window", 20),
      SmaFeature("close", "ma60", "ma60_window", 60),
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
    regime=AllRegimes(()),
    entry=AllOf(()),
    exit=AnyOf(()),
    sizing=AtrRiskSizing(
      atr_feature="atr",
      risk_fraction=ParameterRef("risk_fraction", 0.01),
      stop_multiple=ParameterRef("atr_stop_multiple", 1.5),
      take_profit_multiple=ParameterRef("atr_take_profit_multiple", 3.0),
      max_position_fraction=ParameterRef("max_position_fraction", 0.5),
    ),
  )

  def __init__(self) -> None:
    self._cooldown_until_bar_index: int | None = None

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    frame = super().build_feature_frame(candles, parameters)
    entry_lookback = _mapping_int_parameter(
      parameters,
      "entry_lookback_bars",
      10,
      minimum=1,
      maximum=30,
    )
    swing_lookback = _mapping_int_parameter(
      parameters,
      "swing_lookback_bars",
      5,
      minimum=2,
      maximum=20,
    )
    slope_lookback = _mapping_int_parameter(
      parameters,
      "trend_slope_lookback_bars",
      3,
      minimum=1,
      maximum=20,
    )
    frame["bar_index"] = range(len(frame))
    frame["rsi_recent_min"] = frame["rsi"].rolling(window=entry_lookback, min_periods=1).min()
    frame["previous_price_swing_low"] = (
      frame["low"].shift(1).rolling(window=swing_lookback, min_periods=1).min()
    )
    frame["ma20_slope"] = frame["ma20"] - frame["ma20"].shift(slope_lookback)
    frame["ma60_slope"] = frame["ma60"] - frame["ma60"].shift(slope_lookback)
    frame["recent_lower_lows"] = (
      (frame["low"] < frame["low"].shift(1))
      & (frame["low"].shift(1) < frame["low"].shift(2))
    )
    return frame

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    entry_evaluation = _rsi14_oversold_reversal_entry_evaluation(
      context,
      cooldown_until_bar_index=self._cooldown_until_bar_index,
    )
    exit_evaluation = _rsi14_oversold_reversal_exit_evaluation(context)
    exit_match = bool(exit_evaluation["matched"])
    entry_match = bool(entry_evaluation["matched"])

    if context.state.has_position and exit_match:
      signal = SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.SELL,
        confidence=0.82 if bool(exit_evaluation.get("is_stop_exit")) else 0.76,
        tags=("composable", "exit", str(exit_evaluation["reason"])),
        reason=str(exit_evaluation["reason"]),
      )
      if bool(exit_evaluation.get("is_stop_exit")):
        self._start_stop_cooldown(context)
    elif not context.state.has_position and entry_match:
      signal = SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.BUY,
        confidence=0.74,
        tags=("composable", "entry", "rsi14_oversold_escape"),
        reason=str(entry_evaluation["reason"]),
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
      rationale=_rsi14_oversold_reversal_rationale(
        signal,
        entry_evaluation=entry_evaluation,
        exit_evaluation=exit_evaluation,
      ),
      context=context,
      execution=execution,
      trace={
        "architecture": {
          "layers": (
            "feature_pipeline",
            "rsi_oversold_escape_signal_policy",
            "sizing_model",
            "execution_plan",
            "stop_profit_time_exit_policy",
            "stop_cooldown",
          )
        },
        "entry": entry_evaluation,
        "exit": exit_evaluation,
        "execution_tags": execution.tags,
      },
    )

  def _start_stop_cooldown(self, context: StrategyDecisionContext) -> None:
    cooldown_bars = _mapping_int_parameter(
      context.state.parameters,
      "cooldown_after_stop_bars",
      5,
      minimum=0,
      maximum=50,
    )
    bar_index = _finite_number(context.features.get("bar_index"))
    if cooldown_bars <= 0 or bar_index is None:
      return
    self._cooldown_until_bar_index = int(bar_index) + cooldown_bars


def _rsi_atr_entry_evaluation(
  context: StrategyDecisionContext,
  *,
  regime_allowed: bool,
  rule_matched: bool,
  rule: dict[str, Any],
) -> dict[str, Any]:
  close = _feature_or_market(context, "close")
  ema_fast = _feature_value(context, "ema_fast")
  ema_slow = _feature_value(context, "ema_slow")
  atr = _feature_value(context, "atr")
  rsi = _feature_value(context, "rsi")
  previous_rsi = _feature_value(context, "previous_rsi")
  previous2_rsi = _feature_value(context, "previous2_rsi")
  high = _feature_or_market(context, "high")
  low = _feature_or_market(context, "low")
  previous_close = _feature_value(context, "previous_close")
  previous_low = _feature_value(context, "previous_low")
  previous2_low = _feature_value(context, "previous2_low")
  rsi_oversold_level = _clamped_parameter(
    context,
    "rsi_oversold_level",
    30.0,
    minimum=0.0,
    maximum=100.0,
  )
  min_spread_atr = _clamped_parameter(
    context,
    "entry_min_trend_spread_atr",
    0.5,
    minimum=0.0,
    maximum=10.0,
  )
  recovery_enabled = bool(context.state.parameters.get("entry_enable_rsi_recovery", True))
  range_recovery_enabled = bool(
    context.state.parameters.get("entry_enable_range_oversold_recovery", False)
  )
  require_price_above_slow = bool(
    context.state.parameters.get("entry_require_price_above_slow_ema", False)
  )
  recovery_max_rsi = _clamped_parameter(
    context,
    "entry_recovery_max_rsi",
    38.0,
    minimum=0.0,
    maximum=100.0,
  )
  recovery_max_low_proximity_atr = _clamped_parameter(
    context,
    "entry_recovery_max_low_proximity_atr",
    1.5,
    minimum=0.0,
    maximum=10.0,
  )
  recovery_min_trend_spread_atr = _clamped_parameter(
    context,
    "entry_recovery_min_trend_spread_atr",
    -2.0,
    minimum=-10.0,
    maximum=10.0,
  )
  recovery_min_rsi_delta = _clamped_parameter(
    context,
    "entry_recovery_min_rsi_delta",
    5.0,
    minimum=0.0,
    maximum=100.0,
  )
  recovery_min_close_position = _clamped_parameter(
    context,
    "entry_recovery_min_close_position",
    0.7,
    minimum=0.0,
    maximum=1.0,
  )
  recovery_matched = (
    recovery_enabled
    and previous_rsi is not None
    and rsi is not None
    and previous_rsi < rsi_oversold_level
    and rsi > previous_rsi
  )
  local_low_candidates = tuple(
    value for value in (low, previous_low, previous2_low) if value is not None
  )
  local_low = min(local_low_candidates) if local_low_candidates else None
  low_proximity_atr = (
    (close - local_low) / atr
    if close is not None and local_low is not None and atr is not None and atr > 0
    else None
  )
  local_rsi_low = (
    previous_rsi is not None
    and (
      previous2_rsi is None
      or previous_rsi <= previous2_rsi
    )
  )
  rsi_delta = (
    rsi - previous_rsi
    if rsi is not None and previous_rsi is not None
    else None
  )
  close_position = (
    (close - low) / (high - low)
    if close is not None
    and high is not None
    and low is not None
    and high > low
    else None
  )
  patterns = {
    "oversold_peak_turn": {
      "matched": rule_matched,
      "rsi": rsi,
      "previous_rsi": previous_rsi,
      "rsi_oversold_level": rsi_oversold_level,
    },
    "rsi_recovery": {
      "matched": recovery_matched,
      "enabled": recovery_enabled,
      "rsi": rsi,
      "previous_rsi": previous_rsi,
      "rsi_oversold_level": rsi_oversold_level,
    },
    "range_oversold_recovery": {
      "matched": False,
      "enabled": range_recovery_enabled,
      "rsi": rsi,
      "previous_rsi": previous_rsi,
      "previous2_rsi": previous2_rsi,
      "rsi_oversold_level": rsi_oversold_level,
      "recovery_max_rsi": recovery_max_rsi,
      "local_low": local_low,
      "low_proximity_atr": low_proximity_atr,
      "recovery_max_low_proximity_atr": recovery_max_low_proximity_atr,
      "recovery_min_trend_spread_atr": recovery_min_trend_spread_atr,
      "rsi_delta": rsi_delta,
      "recovery_min_rsi_delta": recovery_min_rsi_delta,
      "close_position": close_position,
      "recovery_min_close_position": recovery_min_close_position,
    },
  }
  trend_spread = (
    ema_fast - ema_slow
    if ema_fast is not None and ema_slow is not None
    else None
  )
  trend_spread_atr = (
    trend_spread / atr
    if trend_spread is not None and atr is not None and atr > 0
    else None
  )
  range_filters = {
    "range_oversold_exit": {
      "passed": (
        rsi is not None
        and previous_rsi is not None
        and previous_rsi < rsi_oversold_level
        and rsi >= rsi_oversold_level
      ),
      "rsi": rsi,
      "previous_rsi": previous_rsi,
      "rsi_oversold_level": rsi_oversold_level,
    },
    "range_local_rsi_low": {
      "passed": local_rsi_low,
      "previous_rsi": previous_rsi,
      "previous2_rsi": previous2_rsi,
    },
    "range_rsi_impulse": {
      "passed": rsi_delta is not None and rsi_delta >= recovery_min_rsi_delta,
      "value": rsi_delta,
      "minimum": recovery_min_rsi_delta,
    },
    "range_rsi_ceiling": {
      "passed": rsi is not None and rsi <= recovery_max_rsi,
      "rsi": rsi,
      "maximum": recovery_max_rsi,
    },
    "range_close_recovery": {
      "passed": (
        close is not None
        and previous_close is not None
        and close >= previous_close
      ),
      "close": close,
      "previous_close": previous_close,
    },
    "range_candle_close_position": {
      "passed": (
        close_position is not None
        and close_position >= recovery_min_close_position
      ),
      "value": close_position,
      "minimum": recovery_min_close_position,
    },
    "range_low_proximity": {
      "passed": (
        low_proximity_atr is not None
        and low_proximity_atr <= recovery_max_low_proximity_atr
      ),
      "value": low_proximity_atr,
      "maximum": recovery_max_low_proximity_atr,
      "local_low": local_low,
      "atr": atr,
    },
    "range_trend_spread_floor": {
      "passed": (
        trend_spread_atr is not None
        and trend_spread_atr >= recovery_min_trend_spread_atr
      ),
      "value": trend_spread_atr,
      "minimum": recovery_min_trend_spread_atr,
    },
  }
  range_failed_filters = tuple(
    name for name, details in range_filters.items() if not bool(details["passed"])
  )
  range_recovery_matched = (
    range_recovery_enabled
    and recovery_matched
    and not range_failed_filters
  )
  patterns["range_oversold_recovery"]["matched"] = range_recovery_matched
  pattern_matched = any(bool(details["matched"]) for details in patterns.values())
  filters = {
    "trend_spread_strength": {
      "passed": (
        trend_spread_atr is not None
        and trend_spread_atr >= min_spread_atr
      ),
      "value": trend_spread_atr,
      "minimum": min_spread_atr,
      "trend_spread": trend_spread,
      "atr": atr,
    },
    "price_above_slow_ema": {
      "passed": (
        not require_price_above_slow
        or (
          close is not None
          and ema_slow is not None
          and close >= ema_slow
        )
      ),
      "required": require_price_above_slow,
      "close": close,
      "ema_slow": ema_slow,
    },
    **range_filters,
  }
  trend_failed_filters = tuple(
    name
    for name in ("trend_spread_strength", "price_above_slow_ema")
    if not bool(filters[name]["passed"])
  )
  trend_pattern_names = tuple(
    name
    for name in ("oversold_peak_turn", "rsi_recovery")
    if bool(patterns[name]["matched"])
  )
  trend_entry_matched = regime_allowed and bool(trend_pattern_names) and not trend_failed_filters
  matched = trend_entry_matched or range_recovery_matched
  if matched:
    matched_pattern_names = list(trend_pattern_names) if trend_entry_matched else []
    if range_recovery_matched:
      matched_pattern_names.append("range_oversold_recovery")
    matched_patterns = ",".join(matched_pattern_names)
    reason = f"entry_conditions_met:{matched_patterns}"
  elif range_recovery_enabled and recovery_matched and range_failed_filters:
    reason = f"entry_filters_failed:{','.join(range_failed_filters)}"
  elif not regime_allowed:
    reason = "entry_regime_blocked"
  elif not bool(trend_pattern_names):
    reason = "entry_pattern_not_matched"
  elif trend_failed_filters:
    reason = f"entry_filters_failed:{','.join(trend_failed_filters)}"
  else:
    reason = "entry_pattern_not_matched"
  return {
    "matched": matched,
    "reason": reason,
    "rule_matched": pattern_matched,
    "regime_allowed": regime_allowed,
    "rule": rule,
    "patterns": patterns,
    "filters": filters,
    "trend_entry_matched": trend_entry_matched,
    "range_entry_matched": range_recovery_matched,
  }


def _rsi14_oversold_reversal_entry_evaluation(
  context: StrategyDecisionContext,
  *,
  cooldown_until_bar_index: int | None = None,
) -> dict[str, Any]:
  oversold_level = _clamped_parameter(
    context,
    "rsi_oversold_level",
    30.0,
    minimum=0.0,
    maximum=100.0,
  )
  bar_index = _finite_number(context.features.get("bar_index"))
  close = _feature_or_market(context, "close")
  previous_high = _feature_value(context, "previous_high")
  rsi = _feature_value(context, "rsi")
  previous_rsi = _feature_value(context, "previous_rsi")
  rsi_recent_min = _feature_value(context, "rsi_recent_min")
  ma20 = _feature_value(context, "ma20")
  ma60 = _feature_value(context, "ma60")
  ma20_slope = _feature_value(context, "ma20_slope")
  recent_lower_lows = bool(context.features.get("recent_lower_lows", False))
  cooldown_active = (
    cooldown_until_bar_index is not None
    and bar_index is not None
    and int(bar_index) <= cooldown_until_bar_index
  )

  recent_oversold = rsi_recent_min is not None and rsi_recent_min <= oversold_level
  rsi_crossed_oversold = (
    rsi is not None
    and previous_rsi is not None
    and previous_rsi <= oversold_level
    and rsi > oversold_level
  )
  close_above_previous_high = (
    close is not None
    and previous_high is not None
    and close > previous_high
  )
  above_ma20 = close is not None and ma20 is not None and close > ma20
  above_ma60 = close is not None and ma60 is not None and close > ma60
  ma20_slope_non_negative = ma20_slope is not None and ma20_slope >= 0
  trend_filter = above_ma20 or above_ma60 or ma20_slope_non_negative
  close_below_ma60 = close is not None and ma60 is not None and close < ma60
  ma20_slope_down = ma20_slope is not None and ma20_slope < 0
  structural_downtrend_block = (
    close_below_ma60
    and ma20_slope_down
    and recent_lower_lows
  )

  filters = {
    "recent_oversold": {
      "passed": recent_oversold,
      "rsi_recent_min": rsi_recent_min,
      "rsi_oversold_level": oversold_level,
    },
    "rsi_crossed_oversold": {
      "passed": rsi_crossed_oversold,
      "rsi": rsi,
      "previous_rsi": previous_rsi,
      "rsi_oversold_level": oversold_level,
    },
    "close_above_previous_high": {
      "passed": close_above_previous_high,
      "close": close,
      "previous_high": previous_high,
    },
    "trend_filter": {
      "passed": trend_filter,
      "above_ma20": above_ma20,
      "above_ma60": above_ma60,
      "ma20_slope_non_negative": ma20_slope_non_negative,
      "close": close,
      "ma20": ma20,
      "ma60": ma60,
      "ma20_slope": ma20_slope,
    },
    "structural_downtrend_block": {
      "passed": not structural_downtrend_block,
      "blocked": structural_downtrend_block,
      "close_below_ma60": close_below_ma60,
      "ma20_slope_down": ma20_slope_down,
      "recent_lower_lows": recent_lower_lows,
    },
    "cooldown": {
      "passed": not cooldown_active,
      "active": cooldown_active,
      "bar_index": bar_index,
      "cooldown_until_bar_index": cooldown_until_bar_index,
    },
  }

  requirements = (
    "recent_oversold",
    "rsi_crossed_oversold",
    "close_above_previous_high",
    "trend_filter",
    "structural_downtrend_block",
    "cooldown",
  )
  failed_filters = tuple(name for name in requirements if not bool(filters[name]["passed"]))
  matched = not failed_filters
  reason = (
    "entry_conditions_met:rsi14_oversold_escape_rebound"
    if matched
    else f"entry_filters_failed:{','.join(failed_filters)}"
  )
  return {
    "matched": matched,
    "reason": reason,
    "requirements": requirements,
    "failed_filters": failed_filters,
    "filters": filters,
    "structural_downtrend_block": structural_downtrend_block,
    "cooldown_active": cooldown_active,
  }


def _rsi14_oversold_reversal_exit_evaluation(context: StrategyDecisionContext) -> dict[str, Any]:
  close = _feature_or_market(context, "close")
  high = _feature_or_market(context, "high")
  rsi = _feature_value(context, "rsi")
  atr = _feature_value(context, "atr")
  ma20 = _feature_value(context, "ma20")
  ma60 = _feature_value(context, "ma60")
  previous_price_swing_low = _feature_value(context, "previous_price_swing_low")
  entry_price = _finite_number(context.state.position_average_price)
  hard_stop_price = _finite_number(context.state.position_stop_loss_price)
  exit_rsi_profit_level = _clamped_parameter(
    context,
    "exit_rsi_profit_level",
    50.0,
    minimum=0.0,
    maximum=100.0,
  )
  profit_r_multiple = _clamped_parameter(
    context,
    "exit_profit_r_multiple",
    1.5,
    minimum=0.1,
    maximum=5.0,
  )
  time_stop_bars = _mapping_int_parameter(
    context.state.parameters,
    "exit_time_stop_bars",
    7,
    minimum=1,
    maximum=50,
  )
  bars_since_entry = _bars_since_position_opened(context)
  profitable = close is not None and entry_price is not None and close > entry_price
  risk_per_unit = (
    entry_price - hard_stop_price
    if entry_price is not None
    and hard_stop_price is not None
    and entry_price > hard_stop_price
    else (
      atr * _clamped_parameter(
        context,
        "atr_stop_multiple",
        1.5,
        minimum=0.1,
        maximum=10.0,
      )
      if atr is not None and atr > 0
      else None
    )
  )
  profit_r = (
    (close - entry_price) / risk_per_unit
    if close is not None
    and entry_price is not None
    and risk_per_unit is not None
    and risk_per_unit > 0
    else None
  )
  profit_r_target_price = (
    entry_price + (risk_per_unit * profit_r_multiple)
    if entry_price is not None and risk_per_unit is not None
    else None
  )
  components = {
    "swing_low_stop": _exit_component(
      (
        context.state.has_position
        and close is not None
        and previous_price_swing_low is not None
        and close <= previous_price_swing_low
      ),
      1.0,
      close=close,
      swing_low=previous_price_swing_low,
    ),
    "atr_stop": _exit_component(
      (
        context.state.has_position
        and close is not None
        and hard_stop_price is not None
        and close <= hard_stop_price
      ),
      1.0,
      close=close,
      stop_loss_price=hard_stop_price,
      atr=atr,
    ),
    "rsi_profit": _exit_component(
      (
        context.state.has_position
        and profitable
        and rsi is not None
        and rsi >= exit_rsi_profit_level
      ),
      1.0,
      rsi=rsi,
      exit_rsi_profit_level=exit_rsi_profit_level,
      profitable=profitable,
    ),
    "profit_r_target": _exit_component(
      (
        context.state.has_position
        and profit_r is not None
        and profit_r >= profit_r_multiple
      ),
      1.0,
      profit_r=profit_r,
      profit_r_multiple=profit_r_multiple,
      target_price=profit_r_target_price,
      risk_per_unit=risk_per_unit,
    ),
    "ma_resistance": _exit_component(
      _ma_resistance_reached(
        high=high,
        entry_price=entry_price,
        ma20=ma20,
        ma60=ma60,
        profitable=profitable,
      ),
      1.0,
      high=high,
      entry_price=entry_price,
      ma20=ma20,
      ma60=ma60,
      profitable=profitable,
    ),
    "time_no_profit": _exit_component(
      (
        context.state.has_position
        and bars_since_entry is not None
        and bars_since_entry >= time_stop_bars
        and not profitable
      ),
      1.0,
      bars_since_entry=bars_since_entry,
      time_stop_bars=time_stop_bars,
      close=close,
      entry_price=entry_price,
      profitable=profitable,
    ),
  }
  if not context.state.has_position:
    return {
      "matched": False,
      "reason": "no_position",
      "score": 0.0,
      "threshold": 1.0,
      "components": components,
      "is_stop_exit": False,
      "bars_since_entry": bars_since_entry,
      "hard_stop_price": hard_stop_price,
      "swing_stop_price": previous_price_swing_low,
      "profit_r": profit_r,
    }

  reason_order = (
    "swing_low_stop",
    "atr_stop",
    "profit_r_target",
    "rsi_profit",
    "ma_resistance",
    "time_no_profit",
  )
  active_reason = next(
    (name for name in reason_order if bool(components[name]["active"])),
    None,
  )
  matched = active_reason is not None
  is_stop_exit = active_reason in {"swing_low_stop", "atr_stop"}
  return {
    "matched": matched,
    "reason": active_reason or "exit_conditions_not_met",
    "score": 1.0 if matched else 0.0,
    "threshold": 1.0,
    "components": components,
    "is_stop_exit": is_stop_exit,
    "bars_since_entry": bars_since_entry,
    "hard_stop_price": hard_stop_price,
    "swing_stop_price": previous_price_swing_low,
    "profit_r": profit_r,
    "profit_r_target_price": profit_r_target_price,
  }


def _rsi_atr_exit_evaluation(context: StrategyDecisionContext) -> dict[str, Any]:
  threshold = _clamped_parameter(context, "exit_score_threshold", 0.75, minimum=0.0, maximum=1.0)
  trailing_activation_atr = _clamped_parameter(
    context,
    "exit_trailing_activation_atr",
    1.5,
    minimum=0.0,
    maximum=10.0,
  )
  trailing_distance_atr = _clamped_parameter(
    context,
    "exit_trailing_distance_atr",
    2.0,
    minimum=0.1,
    maximum=10.0,
  )
  close = _feature_or_market(context, "close")
  hard_stop_price = _finite_number(context.state.position_stop_loss_price)
  take_profit_price = _finite_number(context.state.position_take_profit_price)
  state_high_watermark_price = _finite_number(context.state.position_high_watermark_price)
  previous_trailing_stop_price = _finite_number(context.state.position_trailing_stop_price)
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
      "high_watermark_price": state_high_watermark_price,
      "trailing_stop_price": previous_trailing_stop_price,
      "trailing_activation_price": None,
      "trailing_active": False,
      "trailing_activation_atr": trailing_activation_atr,
      "trailing_distance_atr": trailing_distance_atr,
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
      "high_watermark_price": state_high_watermark_price,
      "trailing_stop_price": previous_trailing_stop_price,
      "trailing_activation_price": None,
      "trailing_active": False,
      "trailing_activation_atr": trailing_activation_atr,
      "trailing_distance_atr": trailing_distance_atr,
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
      "high_watermark_price": state_high_watermark_price,
      "trailing_stop_price": previous_trailing_stop_price,
      "trailing_activation_price": None,
      "trailing_active": previous_trailing_stop_price is not None,
      "trailing_activation_atr": trailing_activation_atr,
      "trailing_distance_atr": trailing_distance_atr,
    }

  ema_fast = _feature_value(context, "ema_fast")
  ema_slow = _feature_value(context, "ema_slow")
  previous_ema_fast = _feature_value(context, "previous_ema_fast")
  previous_ema_slow = _feature_value(context, "previous_ema_slow")
  rsi = _feature_value(context, "rsi")
  previous_rsi = _feature_value(context, "previous_rsi")
  atr = _feature_value(context, "atr")
  entry_price = _finite_number(context.state.position_average_price)
  current_high = _feature_or_market(context, "high")
  rsi_exit_level = _clamped_parameter(context, "rsi_exit_level", 45.0, minimum=0.0, maximum=100.0)
  high_candidates = tuple(
    value
    for value in (entry_price, state_high_watermark_price, current_high, close)
    if value is not None
  )
  high_watermark_price = max(high_candidates) if high_candidates else state_high_watermark_price
  trailing_activation_price: float | None = None
  candidate_trailing_stop_price: float | None = None
  trailing_stop_price = previous_trailing_stop_price
  trailing_active = previous_trailing_stop_price is not None
  trailing_stop_hit = False

  if entry_price is not None and atr is not None and atr > 0 and high_watermark_price is not None:
    trailing_activation_price = entry_price + (trailing_activation_atr * atr)
    trailing_active = trailing_active or high_watermark_price >= trailing_activation_price
    if trailing_active:
      candidate_trailing_stop_price = max(
        entry_price,
        high_watermark_price - (trailing_distance_atr * atr),
      )
      trailing_stop_price = max(
        value
        for value in (previous_trailing_stop_price, candidate_trailing_stop_price)
        if value is not None
      )
      trailing_stop_hit = close <= trailing_stop_price

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
  profit_pullback_warning = (
    take_profit_price is not None
    and close >= take_profit_price * 0.98
    and rsi is not None
    and previous_rsi is not None
    and rsi < previous_rsi
  )

  components["trailing_stop"] = _exit_component(
    trailing_stop_hit,
    1.0,
    close=close,
    entry_price=entry_price,
    high_watermark_price=high_watermark_price,
    previous_trailing_stop_price=previous_trailing_stop_price,
    candidate_trailing_stop_price=candidate_trailing_stop_price,
    trailing_stop_price=trailing_stop_price,
    trailing_activation_price=trailing_activation_price,
    trailing_active=trailing_active,
    atr=atr,
    trailing_activation_atr=trailing_activation_atr,
    trailing_distance_atr=trailing_distance_atr,
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
  components["profit_pullback_warning"] = _exit_component(
    profit_pullback_warning,
    0.0,
    close=close,
    take_profit_price=take_profit_price,
    rsi=rsi,
    previous_rsi=previous_rsi,
  )

  if trailing_stop_hit:
    return {
      "matched": True,
      "score": 1.0,
      "threshold": threshold,
      "reason": "trailing_stop",
      "components": components,
      "hard_stop_price": hard_stop_price,
      "take_profit_price": take_profit_price,
      "high_watermark_price": high_watermark_price,
      "trailing_stop_price": trailing_stop_price,
      "trailing_activation_price": trailing_activation_price,
      "trailing_active": trailing_active,
      "trailing_activation_atr": trailing_activation_atr,
      "trailing_distance_atr": trailing_distance_atr,
    }

  score = round(min(sum(component["score"] for component in components.values()), 1.0), 4)
  active_reasons = tuple(
    name for name, component in components.items() if bool(component["active"])
  )
  matched = score >= threshold
  trailing_holds_profit = (
    matched
    and trailing_active
    and trailing_stop_price is not None
    and entry_price is not None
    and close > entry_price
  )
  if trailing_holds_profit:
    matched = False
    reason = "trailing_active_holding_until_stop"
  else:
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
    "high_watermark_price": high_watermark_price,
    "trailing_stop_price": trailing_stop_price,
    "trailing_activation_price": trailing_activation_price,
    "trailing_active": trailing_active,
    "trailing_activation_atr": trailing_activation_atr,
    "trailing_distance_atr": trailing_distance_atr,
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
  entry_evaluation: dict[str, Any],
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
  trailing_stop = _finite_number(exit_evaluation.get("trailing_stop_price"))
  high_watermark = _finite_number(exit_evaluation.get("high_watermark_price"))
  trailing_summary = ""
  if trailing_stop is not None:
    trailing_summary = f"; trailing_stop={trailing_stop:.2f}"
    if high_watermark is not None:
      trailing_summary = f"{trailing_summary}; high_watermark={high_watermark:.2f}"
  return (
    f"Composable strategy signal={signal.action.value}; "
    f"regime={regime_label}; entry={entry_evaluation['matched']}; "
    f"entry_reason={entry_evaluation['reason']}; exit={exit_evaluation['matched']}; "
    f"exit_score={score:.2f}/{threshold:.2f}; "
    f"exit_reason={exit_evaluation['reason']}; exit_components={component_summary}"
    f"{trailing_summary}."
  )


def _rsi14_oversold_reversal_rationale(
  signal: SignalDecision,
  *,
  entry_evaluation: dict[str, Any],
  exit_evaluation: dict[str, Any],
) -> str:
  active_exit_components = [
    name
    for name, component in exit_evaluation["components"].items()
    if bool(component.get("active"))
  ]
  exit_component_summary = ",".join(active_exit_components) if active_exit_components else "none"
  return (
    f"RSI14 oversold escape rebound signal={signal.action.value}; "
    f"entry={entry_evaluation['matched']}; entry_reason={entry_evaluation['reason']}; "
    f"structural_downtrend_block={entry_evaluation['structural_downtrend_block']}; "
    f"cooldown_active={entry_evaluation['cooldown_active']}; exit={exit_evaluation['matched']}; "
    f"exit_reason={exit_evaluation['reason']}; exit_components={exit_component_summary}; "
    f"bars_since_entry={exit_evaluation['bars_since_entry']}; profit_r={exit_evaluation['profit_r']}."
  )


def _mapping_int_parameter(
  parameters: dict[str, Any],
  key: str,
  default: int,
  *,
  minimum: int,
  maximum: int,
) -> int:
  value = _finite_number(parameters.get(key, default))
  if value is None:
    value = float(default)
  return min(max(int(value), minimum), maximum)


def _is_falling(
  slope: float | None,
  current: float | None,
  previous: float | None,
) -> bool:
  if slope is not None:
    return slope < 0
  return current is not None and previous is not None and current < previous


def _bars_since_position_opened(context: StrategyDecisionContext) -> int | None:
  opened_at = context.state.position_opened_at
  if opened_at is None:
    return None
  previous_timestamp = context.features.get("previous_timestamp")
  if previous_timestamp is None:
    return None
  try:
    previous = pd.to_datetime(previous_timestamp, utc=True).to_pydatetime()
  except (TypeError, ValueError):
    return None
  current = context.timestamp
  if current.tzinfo is None:
    current = pd.Timestamp(current, tz="UTC").to_pydatetime()
  if opened_at.tzinfo is None:
    opened_at = pd.Timestamp(opened_at, tz="UTC").to_pydatetime()
  timeframe_seconds = (current - previous).total_seconds()
  if timeframe_seconds <= 0:
    return None
  elapsed_seconds = (current - opened_at).total_seconds()
  if elapsed_seconds < 0:
    return None
  return int(elapsed_seconds // timeframe_seconds)


def _ma_resistance_reached(
  *,
  high: float | None,
  entry_price: float | None,
  ma20: float | None,
  ma60: float | None,
  profitable: bool,
) -> bool:
  if not profitable or high is None or entry_price is None:
    return False
  return any(
    average is not None and entry_price < average <= high
    for average in (ma20, ma60)
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
