from __future__ import annotations

from typing import Protocol

from akra_trader.domain.models import LlmJudgementRequest
from akra_trader.domain.models import LlmJudgementResponse


class LlmJudgementPort(Protocol):
  def judge(self, request: LlmJudgementRequest) -> LlmJudgementResponse: ...
