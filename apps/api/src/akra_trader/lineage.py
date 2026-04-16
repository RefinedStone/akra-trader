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


def build_sync_checkpoint_identity(
  *,
  provider: str,
  venue: str,
  symbol: str,
  timeframe: str,
  candle_count: int,
  first_timestamp: datetime | None,
  last_timestamp: datetime | None,
  latest_ingested_at: datetime | None,
  contiguous_missing_candles: int,
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "symbol": symbol,
    "timeframe": timeframe,
    "candle_count": candle_count,
    "first_timestamp": _serialize_optional_datetime(first_timestamp),
    "last_timestamp": _serialize_optional_datetime(last_timestamp),
    "latest_ingested_at": _serialize_optional_datetime(latest_ingested_at),
    "contiguous_missing_candles": contiguous_missing_candles,
  }
  return f"checkpoint-v1:{_build_digest(payload)}"


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


def _serialize_optional_datetime(value: datetime | None) -> str | None:
  if value is None:
    return None
  return _serialize_datetime(value)
