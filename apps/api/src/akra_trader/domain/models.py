from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY = "__runtime_candidate_id"
BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_SOURCE_KEYS = (
  BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY,
  "runtime_candidate_id",
  "native_runtime_candidate_id",
  "native_candidate_id",
)


def extract_benchmark_artifact_runtime_candidate_id(value: Any) -> str | None:
  if not isinstance(value, dict):
    return None
  for key in BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_SOURCE_KEYS:
    candidate_value = value.get(key)
    if isinstance(candidate_value, str) and candidate_value.strip():
      return candidate_value.strip()
  return None


def is_benchmark_artifact_metadata_key(key: str) -> bool:
  return key in BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_SOURCE_KEYS


from akra_trader.domain.model_types.provider_provenance import *
from akra_trader.domain.model_types.run_surface_contracts import *
from akra_trader.domain.model_types.run_execution import *
from akra_trader.domain.model_types.strategy_catalog import *
from akra_trader.domain.model_types.run_comparison import *
from akra_trader.domain.model_types.market_data_status import *
from akra_trader.domain.model_types.sync_lineage import *
from akra_trader.domain.model_types.operator_runtime import *
from akra_trader.domain.model_types.guarded_live import *


@dataclass(frozen=True)
class MarketDataRemediationResult:
  kind: str
  symbol: str
  timeframe: str
  status: str
  started_at: datetime
  finished_at: datetime
  detail: str
