from __future__ import annotations

from typing import Any
from typing import Mapping

LLM_JUDGEMENT_RUNTIME_PARAMETER_SCHEMA: dict[str, dict[str, Any]] = {
  "use_llm_judgement": {
    "type": "boolean",
    "default": False,
    "semantic_hint": "Opt-in paid LLM veto judgement for backtest and sandbox runs.",
    "description_ko": "유료 LLM 판정을 사용할지 여부입니다. 기본값은 비용 방지를 위해 false입니다.",
  },
}


def with_runtime_parameter_schema(parameter_schema: Mapping[str, Any]) -> dict[str, Any]:
  schema = dict(parameter_schema)
  for key, spec in LLM_JUDGEMENT_RUNTIME_PARAMETER_SCHEMA.items():
    schema.setdefault(key, dict(spec))
  return schema
