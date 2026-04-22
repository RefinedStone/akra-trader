from __future__ import annotations

from typing import Any


__all__ = [
  "BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY",
  "BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_SOURCE_KEYS",
  "extract_benchmark_artifact_runtime_candidate_id",
  "is_benchmark_artifact_metadata_key",
]


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
