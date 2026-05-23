from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import TypeAdapter

__all__ = [
  "LlmCandidateSignal",
  "LlmCurrentPositionState",
  "LlmJudgementDecision",
  "LlmJudgementRequest",
  "LlmJudgementResponse",
  "LlmMarketRegime",
  "LlmRiskFlag",
  "LlmRiskLevel",
  "build_safe_llm_judgement_fallback",
  "llm_judgement_request_json_schema",
  "llm_judgement_response_json_schema",
]


class LlmJudgementDecision(str, Enum):
  APPROVE_BUY = "approve_buy"
  APPROVE_SELL = "approve_sell"
  NO_TRADE = "no_trade"


class LlmMarketRegime(str, Enum):
  UNKNOWN = "unknown"
  TRENDING = "trending"
  RANGING = "ranging"
  VOLATILE = "volatile"
  ILLIQUID = "illiquid"


class LlmRiskLevel(str, Enum):
  LOW = "low"
  MEDIUM = "medium"
  HIGH = "high"


class LlmRiskFlag(str, Enum):
  STALE_DATA = "stale_data"
  LIQUIDITY_GAP = "liquidity_gap"
  VOLATILITY_SPIKE = "volatility_spike"
  REGIME_CONFLICT = "regime_conflict"
  OVEREXPOSURE = "overexposure"
  UNKNOWN_CONTEXT = "unknown_context"


@dataclass(frozen=True)
class LlmCandidateSignal:
  action: str
  size_fraction: float
  confidence: float
  tags: tuple[str, ...] = ()
  reason: str | None = None


@dataclass(frozen=True)
class LlmCurrentPositionState:
  has_position: bool
  cash: float
  position_size: float


@dataclass(frozen=True)
class LlmJudgementRequest:
  timestamp: datetime
  instrument_id: str
  candidate_signal: LlmCandidateSignal
  market_snapshot: dict[str, Any]
  selected_features: dict[str, Any]
  current_position: LlmCurrentPositionState
  rule_rationale: str
  strategy_id: str | None = None
  trace_context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LlmJudgementResponse:
  decision: LlmJudgementDecision
  confidence: float
  market_regime: LlmMarketRegime = LlmMarketRegime.UNKNOWN
  risk_level: LlmRiskLevel = LlmRiskLevel.MEDIUM
  risk_flags: tuple[LlmRiskFlag, ...] = ()
  reasons: tuple[str, ...] = ()
  invalidation_condition: str | None = None
  used_fallback: bool = False
  trace: dict[str, Any] = field(default_factory=dict)


_request_adapter = TypeAdapter(LlmJudgementRequest)
_response_adapter = TypeAdapter(LlmJudgementResponse)


def build_safe_llm_judgement_fallback(reason: str) -> LlmJudgementResponse:
  normalized_reason = reason.strip() or "llm_judgement_unavailable"
  return LlmJudgementResponse(
    decision=LlmJudgementDecision.NO_TRADE,
    confidence=0.0,
    market_regime=LlmMarketRegime.UNKNOWN,
    risk_level=LlmRiskLevel.HIGH,
    risk_flags=(LlmRiskFlag.UNKNOWN_CONTEXT,),
    reasons=(normalized_reason,),
    invalidation_condition="llm_judgement_fallback_requires_manual_review",
    used_fallback=True,
  )


def llm_judgement_request_json_schema() -> dict[str, Any]:
  return _request_adapter.json_schema()


def llm_judgement_response_json_schema() -> dict[str, Any]:
  return _response_adapter.json_schema()
