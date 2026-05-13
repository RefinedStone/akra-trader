from __future__ import annotations

from typing import Any
from typing import Mapping

from pydantic import TypeAdapter

from akra_trader.domain.models import LlmJudgementDecision
from akra_trader.domain.models import LlmJudgementRequest
from akra_trader.domain.models import LlmJudgementResponse
from akra_trader.domain.models import LlmMarketRegime
from akra_trader.domain.models import LlmRiskFlag
from akra_trader.domain.models import LlmRiskLevel


class MockLlmJudgementClient:
  _adapter = TypeAdapter(LlmJudgementResponse)

  def __init__(
    self,
    *,
    scenario: str = "approve",
    response: LlmJudgementResponse | Mapping[str, Any] | None = None,
  ) -> None:
    self._scenario = scenario
    self._response = response
    self.requests: list[LlmJudgementRequest] = []

  def judge(self, request: LlmJudgementRequest) -> LlmJudgementResponse:
    self.requests.append(request)
    if self._response is not None:
      return self._coerce_response(self._response)
    if self._scenario == "provider_error":
      raise RuntimeError("mock_llm_provider_error")
    if self._scenario == "malformed":
      return self._coerce_response({"decision": "invalid", "confidence": "not-a-number"})
    if self._scenario == "no_trade":
      return LlmJudgementResponse(
        decision=LlmJudgementDecision.NO_TRADE,
        confidence=0.9,
        reasons=("mock_no_trade",),
      )
    if self._scenario == "low_confidence":
      return self._approval_for(request, confidence=0.2, reasons=("mock_low_confidence",))
    if self._scenario == "high_risk":
      return self._approval_for(
        request,
        risk_level=LlmRiskLevel.HIGH,
        reasons=("mock_high_risk",),
      )
    if self._scenario == "stale_data":
      return self._approval_for(
        request,
        risk_flags=(LlmRiskFlag.STALE_DATA,),
        reasons=("mock_stale_data",),
      )
    if self._scenario == "conflict":
      decision = (
        LlmJudgementDecision.APPROVE_SELL
        if request.candidate_signal.action == "buy"
        else LlmJudgementDecision.APPROVE_BUY
      )
      return LlmJudgementResponse(
        decision=decision,
        confidence=0.9,
        market_regime=LlmMarketRegime.TRENDING,
        risk_level=LlmRiskLevel.LOW,
        reasons=("mock_conflict",),
      )
    return self._approval_for(request, reasons=("mock_approved",))

  def _approval_for(
    self,
    request: LlmJudgementRequest,
    *,
    confidence: float = 0.9,
    market_regime: LlmMarketRegime = LlmMarketRegime.TRENDING,
    risk_level: LlmRiskLevel = LlmRiskLevel.LOW,
    risk_flags: tuple[LlmRiskFlag, ...] = (),
    reasons: tuple[str, ...] = (),
  ) -> LlmJudgementResponse:
    decision = (
      LlmJudgementDecision.APPROVE_BUY
      if request.candidate_signal.action == "buy"
      else LlmJudgementDecision.APPROVE_SELL
      if request.candidate_signal.action == "sell"
      else LlmJudgementDecision.NO_TRADE
    )
    return LlmJudgementResponse(
      decision=decision,
      confidence=confidence,
      market_regime=market_regime,
      risk_level=risk_level,
      risk_flags=risk_flags,
      reasons=reasons,
    )

  def _coerce_response(
    self,
    response: LlmJudgementResponse | Mapping[str, Any],
  ) -> LlmJudgementResponse:
    if isinstance(response, LlmJudgementResponse):
      return response
    return self._adapter.validate_python(dict(response))
