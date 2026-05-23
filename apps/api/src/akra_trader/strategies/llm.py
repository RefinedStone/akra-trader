from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from enum import Enum
from math import isfinite
from typing import Any
from typing import Mapping

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import LlmCandidateSignal
from akra_trader.domain.models import LlmCurrentPositionState
from akra_trader.domain.models import LlmJudgementDecision
from akra_trader.domain.models import LlmJudgementRequest
from akra_trader.domain.models import LlmJudgementResponse
from akra_trader.domain.models import LlmRiskFlag
from akra_trader.domain.models import LlmRiskLevel
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec
from akra_trader.ports import DecisionEnginePort
from akra_trader.ports import LlmJudgementPort
from akra_trader.strategies.base import Strategy

DEFAULT_LLM_JUDGEMENT_MIN_CONFIDENCE = 0.6
DEFAULT_LLM_JUDGEMENT_SELECTED_FEATURE_LIMIT = 48
DEFAULT_LLM_JUDGEMENT_RECENT_HISTORY_LIMIT = 40
MAX_LLM_JUDGEMENT_RECENT_HISTORY_LIMIT = 80
_TRACE_SUMMARY_MAX_DEPTH = 4
_TRACE_SUMMARY_MAX_ITEMS = 40
_TRACE_SUMMARY_OMITTED_KEYS = {
  "llm_judgement",
  "raw_output",
  "raw_payload",
  "raw_prompt",
  "provider_payload",
}
_HISTORY_FEATURE_KEYS = (
  "timestamp",
  "bar_index",
  "open",
  "high",
  "low",
  "close",
  "volume",
  "return_1",
  "volatility_8",
  "rsi",
  "rsi_recent_min",
  "rsi_crossed_oversold",
  "rsi_crossed_oversold_recent",
  "bars_since_rsi_oversold_cross",
  "atr",
  "ma20",
  "ma60",
  "ma20_slope",
  "ma60_slope",
  "ema_fast",
  "ema_slow",
  "sma_short",
  "sma_long",
  "previous_price_swing_low",
  "recent_price_swing_low",
  "recent_lower_lows",
)
_SELECTED_FEATURE_PRIORITY = (
  *_HISTORY_FEATURE_KEYS,
  "previous_open",
  "previous_high",
  "previous_low",
  "previous_close",
  "previous_volume",
  "previous_rsi",
  "previous_atr",
  "previous_ma20",
  "previous_ma60",
  "previous_ma20_slope",
  "previous_ma60_slope",
  "previous_rsi_recent_min",
  "previous_price_swing_low",
  "previous_recent_price_swing_low",
  "previous_recent_lower_lows",
  "previous2_open",
  "previous2_high",
  "previous2_low",
  "previous2_close",
  "previous2_volume",
  "previous2_rsi",
  "previous2_atr",
)


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
        "promotion outside this scaffold until trace and fallback gates are ready."
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


class LlmJudgementVetoStrategy(Strategy):
  def __init__(
    self,
    delegate: Strategy,
    judgement: LlmJudgementPort,
    *,
    min_confidence: float = DEFAULT_LLM_JUDGEMENT_MIN_CONFIDENCE,
    selected_feature_limit: int = DEFAULT_LLM_JUDGEMENT_SELECTED_FEATURE_LIMIT,
    recent_history_limit: int = DEFAULT_LLM_JUDGEMENT_RECENT_HISTORY_LIMIT,
  ) -> None:
    self._delegate = delegate
    self._judgement = judgement
    self._min_confidence = min_confidence
    self._selected_feature_limit = selected_feature_limit
    self._recent_history_limit = recent_history_limit

  def describe(self) -> StrategyMetadata:
    return self._delegate.describe()

  def warmup_spec(self) -> WarmupSpec:
    return self._delegate.warmup_spec()

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    return self._delegate.build_feature_frame(candles, parameters)

  def build_decision_context(
    self,
    candles: pd.DataFrame,
    parameters: dict,
    state: StrategyExecutionState,
  ) -> StrategyDecisionContext:
    return self._delegate.build_decision_context(candles, parameters, state)

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    candidate = self._delegate.decide(context)
    metadata = self._delegate.describe()
    min_confidence = _resolve_min_confidence(context, self._min_confidence)
    recent_history_limit = _resolve_recent_history_limit(context, self._recent_history_limit)
    return apply_llm_judgement_veto(
      candidate,
      judgement=self._judgement,
      strategy_id=metadata.strategy_id,
      min_confidence=min_confidence,
      selected_feature_limit=self._selected_feature_limit,
      recent_history_limit=recent_history_limit,
    )


def apply_llm_judgement_veto(
  candidate: StrategyDecisionEnvelope,
  *,
  judgement: LlmJudgementPort,
  strategy_id: str | None = None,
  min_confidence: float = DEFAULT_LLM_JUDGEMENT_MIN_CONFIDENCE,
  selected_feature_limit: int = DEFAULT_LLM_JUDGEMENT_SELECTED_FEATURE_LIMIT,
  recent_history_limit: int = DEFAULT_LLM_JUDGEMENT_RECENT_HISTORY_LIMIT,
) -> StrategyDecisionEnvelope:
  if candidate.signal.action == SignalAction.HOLD:
    return replace(
      candidate,
      trace=_with_llm_judgement_trace(
        candidate.trace,
        status="skipped",
        min_confidence=min_confidence,
        candidate=_candidate_summary(candidate.signal),
        request=None,
        response=None,
        fallback=False,
        veto_reason=None,
      ),
    )

  request = _build_judgement_request(
    candidate,
    strategy_id=strategy_id,
    selected_feature_limit=selected_feature_limit,
    recent_history_limit=recent_history_limit,
  )
  try:
    response = judgement.judge(request)
  except Exception as exc:
    from akra_trader.domain.models import build_safe_llm_judgement_fallback

    response = build_safe_llm_judgement_fallback(f"llm_judgement_failure:{exc}")

  veto_reason = _llm_veto_reason(
    candidate.signal.action,
    response,
    min_confidence=min_confidence,
  )
  status = "approved" if veto_reason is None else "vetoed"
  trace = _with_llm_judgement_trace(
    candidate.trace,
    status=status,
    min_confidence=min_confidence,
    candidate=_candidate_summary(candidate.signal),
    request=_request_summary(request),
    response=_response_summary(response),
    fallback=response.used_fallback,
    veto_reason=veto_reason,
  )

  if veto_reason is None:
    approved_signal = replace(
      candidate.signal,
      confidence=min(candidate.signal.confidence, response.confidence),
      tags=(*candidate.signal.tags, "llm_judgement_approved"),
    )
    return replace(candidate, signal=approved_signal, trace=trace)

  blocked_signal = SignalDecision(
    timestamp=candidate.signal.timestamp,
    action=SignalAction.HOLD,
    size_fraction=0.0,
    confidence=min(candidate.signal.confidence, response.confidence),
    tags=(*candidate.signal.tags, "llm_judgement_veto"),
    reason=f"llm_judgement_veto:{veto_reason}",
  )
  blocked_execution = replace(candidate.execution, size_fraction=0.0)
  return StrategyDecisionEnvelope(
    signal=blocked_signal,
    rationale=f"{candidate.rationale} LLM judgement vetoed the candidate: {veto_reason}.",
    context=candidate.context,
    execution=blocked_execution,
    trace=trace,
  )


def _build_judgement_request(
  candidate: StrategyDecisionEnvelope,
  *,
  strategy_id: str | None,
  selected_feature_limit: int,
  recent_history_limit: int,
) -> LlmJudgementRequest:
  context = candidate.context
  return LlmJudgementRequest(
    timestamp=context.timestamp,
    instrument_id=context.instrument_id,
    strategy_id=strategy_id,
    candidate_signal=LlmCandidateSignal(
      action=candidate.signal.action.value,
      size_fraction=candidate.signal.size_fraction,
      confidence=candidate.signal.confidence,
      tags=candidate.signal.tags,
      reason=candidate.signal.reason,
    ),
    market_snapshot=_json_safe_mapping(context.market),
    selected_features=_select_features(context.features, selected_feature_limit),
    recent_feature_history=_select_recent_feature_history(
      context.recent_features,
      recent_history_limit,
    ),
    current_position=LlmCurrentPositionState(
      has_position=context.state.has_position,
      cash=context.state.cash,
      position_size=context.state.position_size,
    ),
    rule_rationale=candidate.rationale,
    trace_context={
      "candidate_tags": candidate.signal.tags,
      "candidate_reason": candidate.signal.reason,
      "trace_keys": tuple(
        sorted(
          str(key)
          for key in candidate.trace
          if str(key) not in _TRACE_SUMMARY_OMITTED_KEYS
        )
      ),
      "trace_summary": _summarize_trace(candidate.trace),
    },
  )


def _llm_veto_reason(
  action: SignalAction,
  response: LlmJudgementResponse,
  *,
  min_confidence: float,
) -> str | None:
  if response.used_fallback:
    return "fallback"
  if response.decision == LlmJudgementDecision.NO_TRADE:
    return "no_trade"
  if response.confidence < min_confidence:
    return "confidence_below_threshold"
  if response.risk_level == LlmRiskLevel.HIGH:
    return "high_risk"
  if LlmRiskFlag.STALE_DATA in response.risk_flags:
    return "stale_data"
  if response.decision != _expected_decision_for_action(action):
    return "decision_conflict"
  return None


def _expected_decision_for_action(action: SignalAction) -> LlmJudgementDecision:
  if action == SignalAction.BUY:
    return LlmJudgementDecision.APPROVE_BUY
  if action == SignalAction.SELL:
    return LlmJudgementDecision.APPROVE_SELL
  return LlmJudgementDecision.NO_TRADE


def _resolve_min_confidence(context: StrategyDecisionContext, default: float) -> float:
  raw_value = context.state.parameters.get("llm_judgement_min_confidence", default)
  try:
    value = float(raw_value)
  except (TypeError, ValueError):
    return default
  return min(max(value, 0.0), 1.0)


def _resolve_recent_history_limit(context: StrategyDecisionContext, default: int) -> int:
  raw_value = context.state.parameters.get(
    "llm_judgement_recent_window",
    context.state.parameters.get("llm_judgement_history_bars", default),
  )
  try:
    value = int(raw_value)
  except (TypeError, ValueError):
    return min(max(default, 0), MAX_LLM_JUDGEMENT_RECENT_HISTORY_LIMIT)
  return min(max(value, 0), MAX_LLM_JUDGEMENT_RECENT_HISTORY_LIMIT)


def _with_llm_judgement_trace(
  trace: Mapping[str, Any],
  *,
  status: str,
  min_confidence: float,
  candidate: dict[str, Any],
  request: dict[str, Any] | None,
  response: dict[str, Any] | None,
  fallback: bool,
  veto_reason: str | None,
) -> dict[str, Any]:
  return {
    **dict(trace),
    "llm_judgement": {
      "status": status,
      "mode": "veto_only",
      "min_confidence": min_confidence,
      "candidate": candidate,
      "request": request,
      "response": response,
      "fallback": fallback,
      "veto_reason": veto_reason,
    },
  }


def _candidate_summary(signal: SignalDecision) -> dict[str, Any]:
  return {
    "action": signal.action.value,
    "confidence": signal.confidence,
    "size_fraction": signal.size_fraction,
    "tags": signal.tags,
    "reason": signal.reason,
  }


def _request_summary(request: LlmJudgementRequest) -> dict[str, Any]:
  return {
    "timestamp": request.timestamp.isoformat(),
    "instrument_id": request.instrument_id,
    "strategy_id": request.strategy_id,
    "candidate_action": request.candidate_signal.action,
    "market_keys": tuple(sorted(request.market_snapshot)),
    "selected_feature_keys": tuple(sorted(request.selected_features)),
    "recent_history_rows": len(request.recent_feature_history),
    "recent_history_keys": _history_keys(request.recent_feature_history),
    "trace_context_keys": tuple(sorted(request.trace_context)),
    "has_position": request.current_position.has_position,
  }


def _response_summary(response: LlmJudgementResponse) -> dict[str, Any]:
  return {
    "decision": response.decision.value,
    "confidence": response.confidence,
    "market_regime": response.market_regime.value,
    "risk_level": response.risk_level.value,
    "risk_flags": tuple(flag.value for flag in response.risk_flags),
    "reasons": response.reasons,
    "dimension_reviews": _json_safe_mapping(response.dimension_reviews),
    "invalidation_condition": response.invalidation_condition,
    "used_fallback": response.used_fallback,
    "trace": _json_safe_mapping(response.trace),
  }


def _select_features(features: Mapping[str, Any], limit: int) -> dict[str, Any]:
  selected: dict[str, Any] = {}
  for key in _SELECTED_FEATURE_PRIORITY:
    if len(selected) >= max(limit, 0):
      break
    if key in features and key != "timestamp":
      selected[key] = _json_safe_value(features[key])
  for key in sorted(features):
    if len(selected) >= max(limit, 0):
      break
    if key == "timestamp" or key in selected:
      continue
    selected[key] = _json_safe_value(features[key])
  return selected


def _select_recent_feature_history(
  history: tuple[dict[str, Any], ...],
  limit: int,
) -> tuple[dict[str, Any], ...]:
  if limit <= 0:
    return ()
  rows = history[-min(limit, MAX_LLM_JUDGEMENT_RECENT_HISTORY_LIMIT) :]
  selected_rows: list[dict[str, Any]] = []
  for row in rows:
    selected: dict[str, Any] = {}
    for key in _HISTORY_FEATURE_KEYS:
      if key in row:
        selected[key] = _json_safe_value(row[key])
    if selected:
      selected_rows.append(selected)
  return tuple(selected_rows)


def _history_keys(history: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
  keys: set[str] = set()
  for row in history:
    keys.update(str(key) for key in row)
  return tuple(sorted(keys))


def _summarize_trace(trace: Mapping[str, Any]) -> dict[str, Any]:
  summary: dict[str, Any] = {}
  for key in sorted(trace, key=str):
    if str(key) in _TRACE_SUMMARY_OMITTED_KEYS:
      continue
    summary[str(key)] = _summarize_trace_value(trace[key], depth=0)
  return summary


def _summarize_trace_value(value: Any, *, depth: int) -> Any:
  if depth >= _TRACE_SUMMARY_MAX_DEPTH:
    return "<max_depth>"
  if isinstance(value, Mapping):
    summary: dict[str, Any] = {}
    for index, key in enumerate(sorted(value, key=str)):
      if index >= _TRACE_SUMMARY_MAX_ITEMS:
        summary["_truncated"] = True
        break
      if str(key) in _TRACE_SUMMARY_OMITTED_KEYS:
        continue
      summary[str(key)] = _summarize_trace_value(value[key], depth=depth + 1)
    return summary
  if isinstance(value, tuple | list):
    items = [
      _summarize_trace_value(item, depth=depth + 1)
      for item in value[:_TRACE_SUMMARY_MAX_ITEMS]
    ]
    if len(value) > _TRACE_SUMMARY_MAX_ITEMS:
      items.append("<truncated>")
    return items
  return _json_safe_value(value)


def _json_safe_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
  return {str(key): _json_safe_value(value) for key, value in values.items()}


def _json_safe_value(value: Any) -> Any:
  if isinstance(value, Enum):
    return value.value
  if hasattr(value, "to_pydatetime"):
    return value.to_pydatetime().isoformat()
  if isinstance(value, datetime):
    return value.isoformat()
  if value is None or isinstance(value, str):
    return value
  if isinstance(value, bool):
    return value
  if isinstance(value, int | float):
    return value if isfinite(float(value)) else None
  if hasattr(value, "item"):
    return _json_safe_value(value.item())
  if isinstance(value, Mapping):
    return {str(key): _json_safe_value(item) for key, item in value.items()}
  if isinstance(value, tuple):
    return tuple(_json_safe_value(item) for item in value)
  if isinstance(value, list):
    return [_json_safe_value(item) for item in value]
  return str(value)
