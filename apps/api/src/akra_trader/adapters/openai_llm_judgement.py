from __future__ import annotations

from dataclasses import replace
import json
from time import perf_counter
from typing import Any
from typing import Mapping

from pydantic import BaseModel
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
OPENAI_LLM_JUDGEMENT_PROMPT_PROFILE = "llm_judgement_veto_v1"


class OpenAiLlmJudgementPayload(BaseModel):
  decision: LlmJudgementDecision
  confidence: float = Field(ge=0.0, le=1.0)
  market_regime: LlmMarketRegime = LlmMarketRegime.UNKNOWN
  risk_level: LlmRiskLevel = LlmRiskLevel.MEDIUM
  risk_flags: tuple[LlmRiskFlag, ...] = ()
  reasons: tuple[str, ...] = ()
  invalidation_condition: str | None = None


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
      "Evaluate this provider-neutral rule-strategy candidate. Return only the "
      "structured judgement object.\n"
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
      "raw_output_stored": False,
    }
    if error_type is not None:
      trace["error_type"] = error_type
    if error is not None:
      trace["error"] = error
    return trace


def _elapsed_ms(started_at: float) -> int:
  return max(0, round((perf_counter() - started_at) * 1000))


_SYSTEM_PROMPT = """You are a veto-only trading judgement layer.

You review an existing deterministic rule-strategy candidate.
You must never create a new BUY or SELL signal.
If the candidate is unsafe, stale, unsupported by the supplied features, or unclear,
return no_trade, high risk, and a concise reason.
Only approve_buy for a buy candidate or approve_sell for a sell candidate when the
provided market snapshot and selected features support the rule rationale.
"""
