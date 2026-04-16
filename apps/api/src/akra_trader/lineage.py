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


def build_aggregate_sync_checkpoint_identity(
  *,
  provider: str,
  venue: str,
  timeframe: str,
  symbol_checkpoint_ids: dict[str, str],
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "timeframe": timeframe,
    "symbol_checkpoints": [
      {
        "symbol": symbol,
        "sync_checkpoint_id": symbol_checkpoint_ids[symbol],
      }
      for symbol in sorted(symbol_checkpoint_ids)
    ],
  }
  return f"checkpoint-group-v1:{_build_digest(payload)}"


def build_rerun_boundary_identity(
  *,
  lane: str,
  mode: str,
  strategy_id: str,
  strategy_version: str,
  resolved_parameters: dict,
  venue: str,
  symbols: tuple[str, ...],
  timeframe: str,
  initial_cash: float,
  fee_rate: float,
  slippage_bps: float,
  market_data_reproducibility_state: str,
  market_data_dataset_identity: str | None,
  market_data_sync_checkpoint_id: str | None,
  market_data_symbol_checkpoint_ids: dict[str, str],
  requested_start_at: datetime | None,
  requested_end_at: datetime | None,
  effective_start_at: datetime | None,
  effective_end_at: datetime | None,
  candle_count: int,
  reference_id: str | None = None,
  reference_version: str | None = None,
  integration_mode: str | None = None,
  external_command: tuple[str, ...] = (),
) -> str:
  payload = {
    "schema_version": 1,
    "lane": lane,
    "mode": mode,
    "strategy_id": strategy_id,
    "strategy_version": strategy_version,
    "resolved_parameters": resolved_parameters,
    "venue": venue,
    "symbols": list(symbols),
    "timeframe": timeframe,
    "initial_cash": initial_cash,
    "fee_rate": fee_rate,
    "slippage_bps": slippage_bps,
    "market_data": {
      "reproducibility_state": market_data_reproducibility_state,
      "dataset_identity": market_data_dataset_identity,
      "sync_checkpoint_id": market_data_sync_checkpoint_id,
      "symbol_checkpoint_ids": [
        {
          "symbol": symbol,
          "sync_checkpoint_id": market_data_symbol_checkpoint_ids[symbol],
        }
        for symbol in sorted(market_data_symbol_checkpoint_ids)
      ],
      "requested_start_at": _serialize_optional_datetime(requested_start_at),
      "requested_end_at": _serialize_optional_datetime(requested_end_at),
      "effective_start_at": _serialize_optional_datetime(effective_start_at),
      "effective_end_at": _serialize_optional_datetime(effective_end_at),
      "candle_count": candle_count,
    },
    "reference": {
      "reference_id": reference_id,
      "reference_version": reference_version,
      "integration_mode": integration_mode,
      "external_command": list(external_command),
    },
  }
  return f"rerun-v1:{_build_digest(payload)}"


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
  encoded = json.dumps(_normalize_json_value(payload), separators=(",", ":"), sort_keys=True).encode("utf-8")
  return hashlib.sha256(encoded).hexdigest()


def _serialize_datetime(value: datetime) -> str:
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC).isoformat()
  return value.astimezone(UTC).isoformat()


def _serialize_optional_datetime(value: datetime | None) -> str | None:
  if value is None:
    return None
  return _serialize_datetime(value)


def _normalize_json_value(value):
  if isinstance(value, dict):
    return {
      key: _normalize_json_value(item)
      for key, item in value.items()
    }
  if isinstance(value, (list, tuple)):
    return [_normalize_json_value(item) for item in value]
  if isinstance(value, bool):
    return value
  if isinstance(value, float) and value.is_integer():
    return int(value)
  return value
