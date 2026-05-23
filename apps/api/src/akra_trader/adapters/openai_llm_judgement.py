from __future__ import annotations

from dataclasses import replace
import json
from time import perf_counter
from typing import Any
from typing import Mapping

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import TypeAdapter

from akra_trader.domain.models import LlmJudgementDecision
from akra_trader.domain.models import LlmJudgementRequest
from akra_trader.domain.models import LlmJudgementResponse
from akra_trader.domain.models import LlmMarketRegime
from akra_trader.domain.models import LlmRiskFlag
from akra_trader.domain.models import LlmRiskLevel
from akra_trader.domain.models import build_safe_llm_judgement_fallback


DEFAULT_OPENAI_LLM_JUDGEMENT_MODEL = "gpt-5.5"
DEFAULT_OPENAI_LLM_JUDGEMENT_TIMEOUT_SECONDS = 20.0
OPENAI_LLM_JUDGEMENT_PROMPT_PROFILE = "elite_market_auditor_v1"


class OpenAiDimensionReviews(BaseModel):
  model_config = ConfigDict(extra="forbid")

  trend: str
  momentum: str
  structure: str
  volatility_liquidity: str
  risk_reward: str
  position_context: str
  data_quality: str


class OpenAiLlmJudgementPayload(BaseModel):
  model_config = ConfigDict(extra="forbid")

  decision: LlmJudgementDecision
  confidence: float = Field(ge=0.0, le=1.0)
  market_regime: LlmMarketRegime
  risk_level: LlmRiskLevel
  risk_flags: tuple[LlmRiskFlag, ...]
  reasons: tuple[str, ...]
  dimension_reviews: OpenAiDimensionReviews
  invalidation_condition: str | None


class OpenAiLlmJudgementClient:
  _request_adapter = TypeAdapter(LlmJudgementRequest)
  _payload_adapter = TypeAdapter(OpenAiLlmJudgementPayload)

  def __init__(
    self,
    *,
    api_key: str,
    model: str = DEFAULT_OPENAI_LLM_JUDGEMENT_MODEL,
    timeout_seconds: float = DEFAULT_OPENAI_LLM_JUDGEMENT_TIMEOUT_SECONDS,
    client: Any | None = None,
    prompt_profile: str = OPENAI_LLM_JUDGEMENT_PROMPT_PROFILE,
    reasoning_effort: str = "low",
  ) -> None:
    self._api_key = api_key
    self._model = model
    self._timeout_seconds = timeout_seconds
    self._client = client
    self._prompt_profile = prompt_profile
    self._reasoning_effort = reasoning_effort

  def judge(self, request: LlmJudgementRequest) -> LlmJudgementResponse:
    started_at = perf_counter()
    try:
      response = self._responses_client().responses.parse(
        model=self._model,
        input=[
          {"role": "system", "content": _SYSTEM_PROMPT},
          {
            "role": "user",
            "content": self._request_content(request),
          },
        ],
        text_format=OpenAiLlmJudgementPayload,
        reasoning={"effort": self._reasoning_effort},
      )
      payload = self._extract_payload(response)
      return self._to_response(
        payload,
        request=request,
        response_id=getattr(response, "id", None),
        latency_ms=_elapsed_ms(started_at),
      )
    except Exception as exc:
      fallback = build_safe_llm_judgement_fallback(f"openai_llm_judgement_failure:{exc}")
      return replace(
        fallback,
        trace=self._trace(
          request=request,
          response_id=None,
          latency_ms=_elapsed_ms(started_at),
          status="fallback_after_provider_error",
          error_type=type(exc).__name__,
          error=str(exc),
        ),
      )

  def _responses_client(self):
    if self._client is not None:
      return self._client

    from openai import OpenAI

    self._client = OpenAI(api_key=self._api_key, timeout=self._timeout_seconds)
    return self._client

  def _request_content(self, request: LlmJudgementRequest) -> str:
    payload = self._request_adapter.dump_python(request, mode="json")
    return (
      "Evaluate this provider-neutral deterministic strategy candidate. "
      "recent_feature_history is chronological from oldest to newest and may omit "
      "unavailable indicators. Return only the structured judgement object.\n"
      f"{json.dumps(payload, sort_keys=True, separators=(',', ':'))}"
    )

  def _extract_payload(self, response: Any) -> OpenAiLlmJudgementPayload:
    parsed = getattr(response, "output_parsed", None)
    if parsed is not None:
      return self._coerce_payload(parsed)

    for output in getattr(response, "output", ()):
      if getattr(output, "type", None) != "message":
        continue
      for item in getattr(output, "content", ()):
        item_type = getattr(item, "type", None)
        if item_type == "refusal":
          refusal = getattr(item, "refusal", "model_refused_llm_judgement")
          raise RuntimeError(f"openai_llm_judgement_refusal:{refusal}")
        parsed_item = getattr(item, "parsed", None)
        if parsed_item is not None:
          return self._coerce_payload(parsed_item)

    if isinstance(response, Mapping):
      return self._coerce_payload(response)
    raise RuntimeError("openai_llm_judgement_missing_parsed_payload")

  def _coerce_payload(self, payload: Any) -> OpenAiLlmJudgementPayload:
    if isinstance(payload, OpenAiLlmJudgementPayload):
      return payload
    if hasattr(payload, "model_dump"):
      return self._payload_adapter.validate_python(payload.model_dump(mode="python"))
    return self._payload_adapter.validate_python(payload)

  def _to_response(
    self,
    payload: OpenAiLlmJudgementPayload,
    *,
    request: LlmJudgementRequest,
    response_id: str | None,
    latency_ms: int,
  ) -> LlmJudgementResponse:
    return LlmJudgementResponse(
      decision=payload.decision,
      confidence=payload.confidence,
      market_regime=payload.market_regime,
      risk_level=payload.risk_level,
      risk_flags=payload.risk_flags,
      reasons=payload.reasons,
      dimension_reviews=payload.dimension_reviews.model_dump(mode="python"),
      invalidation_condition=payload.invalidation_condition,
      used_fallback=False,
      trace=self._trace(
        request=request,
        response_id=response_id,
        latency_ms=latency_ms,
        status="completed",
      ),
    )

  def _trace(
    self,
    *,
    request: LlmJudgementRequest,
    response_id: str | None,
    latency_ms: int,
    status: str,
    error_type: str | None = None,
    error: str | None = None,
  ) -> dict[str, Any]:
    trace: dict[str, Any] = {
      "provider": "openai",
      "model": self._model,
      "response_id": response_id,
      "latency_ms": latency_ms,
      "status": status,
      "prompt_profile": self._prompt_profile,
      "reasoning_effort": self._reasoning_effort,
      "request_feature_keys": tuple(sorted(request.selected_features)),
      "recent_history_rows": len(request.recent_feature_history),
      "recent_history_keys": _history_keys(request.recent_feature_history),
      "trace_context_keys": tuple(sorted(request.trace_context)),
      "raw_output_stored": False,
    }
    if error_type is not None:
      trace["error_type"] = error_type
    if error is not None:
      trace["error"] = error
    return trace


def _elapsed_ms(started_at: float) -> int:
  return max(0, round((perf_counter() - started_at) * 1000))


def _history_keys(history: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
  keys: set[str] = set()
  for row in history:
    keys.update(str(key) for key in row)
  return tuple(sorted(keys))


_SYSTEM_PROMPT = """You are a veto-only top-tier discretionary trader and market-audit layer.

You review an existing deterministic rule-strategy candidate. Your job is not to find
new trades. Your job is to decide whether the supplied candidate remains valid under a
broad market read.

Hard rules:
- Never create or upgrade a signal. If the candidate is BUY, respond only approve_buy
  or no_trade. If the candidate is SELL, respond only approve_sell or no_trade.
- Never turn a HOLD into BUY or SELL.
- Do not invent indicators, future prices, external news, or missing context.
- Confidence is confidence in your audit judgement, not probability of profit.

Audit dimensions:
- trend: moving averages, slopes, regime alignment, directional drift.
- momentum: RSI and recent momentum behavior, exhaustion, rebound, acceleration.
- structure: swing lows/highs, lower lows, reclaim/failure, support/resistance context.
- volatility_liquidity: ATR, candle range, volume, gaps, noisy or illiquid conditions.
- risk_reward: stop/invalidation distance, overextension, asymmetric setup quality.
- position_context: existing exposure, scale-in/exit context, sizing implications.
- data_quality: stale, contradictory, insufficient, or low-context inputs.

Use an opportunity-preserving, aggressive audit posture: approve a BUY/SELL candidate
when the thesis is still broadly plausible and risk is not clearly disqualifying.
Medium risk, imperfect alignment, or mild caution can still be approved. Veto only when
the candidate thesis is clearly invalid, structurally weak, overextended, stale,
data-poor, or high risk.

Return concise reasons and a dimension_reviews object with short summaries for the
audit dimensions you actually used.
"""
