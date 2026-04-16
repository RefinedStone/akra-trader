from __future__ import annotations

import hashlib
import json
from datetime import UTC
from datetime import datetime

from akra_trader.domain.models import Candle


def build_candle_dataset_identity(
  *,
  provider: str,
  venue: str,
  symbol: str,
  timeframe: str,
  candles: list[Candle],
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "symbols": [symbol],
    "timeframe": timeframe,
    "candles": [
      [
        _serialize_datetime(candle.timestamp),
        candle.open,
        candle.high,
        candle.low,
        candle.close,
        candle.volume,
      ]
      for candle in candles
    ],
  }
  return f"candles-v1:{_build_digest(payload)}"


def build_aggregate_dataset_identity(
  *,
  provider: str,
  venue: str,
  timeframe: str,
  symbol_identities: dict[str, str],
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "timeframe": timeframe,
    "symbol_identities": [
      {
        "symbol": symbol,
        "dataset_identity": symbol_identities[symbol],
      }
      for symbol in sorted(symbol_identities)
    ],
  }
  return f"dataset-v1:{_build_digest(payload)}"


def combine_reproducibility_states(states: list[str]) -> str:
  if not states:
    return "range_only"
  unique_states = set(states)
  if unique_states == {"pinned"}:
    return "pinned"
  if unique_states == {"delegated"}:
    return "delegated"
  if unique_states == {"range_only"}:
    return "range_only"
  return "partial"


def _build_digest(payload: dict) -> str:
  encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
  return hashlib.sha256(encoded).hexdigest()


def _serialize_datetime(value: datetime) -> str:
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC).isoformat()
  return value.astimezone(UTC).isoformat()
