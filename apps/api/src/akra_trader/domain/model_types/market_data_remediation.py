from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


__all__ = ["MarketDataRemediationResult"]


@dataclass(frozen=True)
class MarketDataRemediationResult:
  kind: str
  symbol: str
  timeframe: str
  status: str
  started_at: datetime
  finished_at: datetime
  detail: str
