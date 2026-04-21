from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from numbers import Number
from typing import Any
from typing import Callable

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import StrategyMetadata


@dataclass(frozen=True)
class RunSubresourceContract:
  subresource_key: str
  body_key: str
  response_title: str
  route_path: str
  route_name: str


@dataclass(frozen=True)
class RunSubresourceRuntimeBinding:
  contract: RunSubresourceContract
  body_serializer: Callable[[RunRecord, RunSurfaceCapabilities], Any]


@dataclass(frozen=True)
class StandaloneSurfaceRuntimeBinding:
  surface_key: str
  route_path: str
  route_name: str
  response_title: str
  scope: str
  binding_kind: str
  methods: tuple[str, ...] = ("GET",)
  subresource_key: str | None = None
  filter_keys: tuple[str, ...] = ()
  filter_param_specs: tuple["StandaloneSurfaceFilterParamSpec", ...] = ()
  sort_field_specs: tuple["StandaloneSurfaceSortFieldSpec", ...] = ()
  collection_path_specs: tuple["StandaloneSurfaceCollectionPathSpec", ...] = ()
  path_param_keys: tuple[str, ...] = ()
  header_keys: tuple[str, ...] = ()
  request_payload_kind: str | None = None


@dataclass(frozen=True)
class StandaloneSurfaceFilterConstraintSpec:
  min_length: int | None = None
  max_length: int | None = None
  ge: float | None = None
  le: float | None = None
  pattern: str | None = None


@dataclass(frozen=True)
class StandaloneSurfaceFilterOpenAPISpec:
  alias: str | None = None
  title: str | None = None
  description: str | None = None
  deprecated: bool = False
  examples: tuple[Any, ...] = ()


@dataclass(frozen=True)
class StandaloneSurfaceFilterOperatorSpec:
  key: str
  label: str
  description: str
  value_shape: str = "scalar"


@dataclass(frozen=True)
class StandaloneSurfaceSortFieldSpec:
  key: str
  label: str
  description: str
  default_direction: str = "asc"
  value_type: str = "string"
  value_path: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandaloneSurfaceFilterParamSpec:
  key: str
  annotation: Any
  default: Any = None
  default_factory: Callable[[], Any] | None = None
  constraints: StandaloneSurfaceFilterConstraintSpec | None = None
  openapi: StandaloneSurfaceFilterOpenAPISpec | None = None
  operators: tuple[StandaloneSurfaceFilterOperatorSpec, ...] = ()
  value_path: tuple[str, ...] = ()
  query_exposed: bool = True
  value_root: bool = False


@dataclass(frozen=True)
class StandaloneSurfaceCollectionPathSpec:
  path: tuple[str, ...]
  label: str
  collection_kind: str
  item_kind: str
  filter_keys: tuple[str, ...]
  description: str = ""
  path_template: tuple[str, ...] = ()
  parameters: tuple["StandaloneSurfaceCollectionPathParameterSpec", ...] = ()


@dataclass(frozen=True)
class StandaloneSurfaceCollectionPathParameterSpec:
  key: str
  kind: str
  description: str
  examples: tuple[str, ...] = ()
  domain_key: str = ""
  domain_source: str = ""
  domain_values: tuple[str, ...] = ()
  enum_source_kind: str = ""
  enum_source_surface_key: str = ""
  enum_source_path: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandaloneSurfaceFilterCondition:
  key: str
  operator: str
  value: Any
  group: str | None = None
  quantifier: str | None = None


@dataclass(frozen=True)
class StandaloneSurfaceFilterExpressionNode:
  logic: str = "and"
  conditions: tuple[StandaloneSurfaceFilterCondition, ...] = ()
  children: tuple["StandaloneSurfaceFilterExpressionNode", ...] = ()
  negated: bool = False
  collection_path: tuple[str, ...] = ()
  collection_quantifier: str | None = None
  collection_path_strict: bool = False


@dataclass(frozen=True)
class StandaloneSurfaceSortTerm:
  key: str
  direction: str = "asc"


def _build_numeric_range_filter_operators(
  subject: str,
) -> tuple[StandaloneSurfaceFilterOperatorSpec, ...]:
  return (
    StandaloneSurfaceFilterOperatorSpec(
      key="eq",
      label="Equals",
      description=f"Matches {subject} exactly.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="gt",
      label="Greater than",
      description=f"Matches {subject} values greater than the requested threshold.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="ge",
      label="Greater than or equal",
      description=f"Matches {subject} values greater than or equal to the requested threshold.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="lt",
      label="Less than",
      description=f"Matches {subject} values lower than the requested threshold.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="le",
      label="Less than or equal",
      description=f"Matches {subject} values lower than or equal to the requested threshold.",
    ),
  )


def _build_datetime_range_filter_operators(
  subject: str,
) -> tuple[StandaloneSurfaceFilterOperatorSpec, ...]:
  return (
    StandaloneSurfaceFilterOperatorSpec(
      key="eq",
      label="Equals",
      description=f"Matches {subject} exactly.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="gt",
      label="After",
      description=f"Matches {subject} values after the requested timestamp.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="ge",
      label="On or after",
      description=f"Matches {subject} values on or after the requested timestamp.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="lt",
      label="Before",
      description=f"Matches {subject} values before the requested timestamp.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="le",
      label="On or before",
      description=f"Matches {subject} values on or before the requested timestamp.",
    ),
  )


def _extract_runtime_filter_conditions(
  filters: dict[str, Any] | None,
) -> tuple[StandaloneSurfaceFilterCondition, ...]:
  if not filters:
    return ()
  value = filters.get("__filter_conditions__")
  if not isinstance(value, tuple):
    return ()
  return tuple(
    condition
    for condition in value
    if isinstance(condition, StandaloneSurfaceFilterCondition)
  )


def _extract_runtime_sort_terms(
  filters: dict[str, Any] | None,
) -> tuple[StandaloneSurfaceSortTerm, ...]:
  if not filters:
    return ()
  value = filters.get("__sort_terms__")
  if not isinstance(value, tuple):
    return ()
  return tuple(
    term
    for term in value
    if isinstance(term, StandaloneSurfaceSortTerm)
  )


def _extract_runtime_filter_expression(
  filters: dict[str, Any] | None,
) -> StandaloneSurfaceFilterExpressionNode | None:
  if not filters:
    return None
  value = filters.get("__filter_expression__")
  if isinstance(value, StandaloneSurfaceFilterExpressionNode):
    return value
  return None


def _normalize_runtime_sort_value(value: Any) -> tuple[int, Any]:
  if value is None:
    return (1, "")
  enum_value = getattr(value, "value", None)
  if isinstance(enum_value, (str, int, float)):
    value = enum_value
  if isinstance(value, datetime):
    return (0, value)
  if isinstance(value, str):
    return (0, value.lower())
  if isinstance(value, (tuple, list, set)):
    return (0, tuple(str(item) for item in value))
  return (0, value)


def _normalize_runtime_numeric_filter_value(value: Any) -> float | int | None:
  if isinstance(value, bool) or not isinstance(value, Number):
    return None
  if isinstance(value, int):
    return value
  return float(value)


def _normalize_runtime_datetime_filter_value(value: Any) -> datetime | None:
  if not isinstance(value, datetime):
    return None
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC)
  return value.astimezone(UTC)


_RUNTIME_QUERY_MISSING = object()


def _default_runtime_query_value_path(
  key: str,
  explicit_path: tuple[str, ...] = (),
) -> tuple[str, ...]:
  if explicit_path:
    return explicit_path
  return tuple(segment for segment in key.split(".") if segment)


def _resolve_runtime_query_path_value(
  item: Any,
  path: tuple[str, ...],
) -> Any:
  current = item
  for segment in path:
    if current is None:
      return None
    if isinstance(current, dict):
      if segment not in current:
        return _RUNTIME_QUERY_MISSING
      current = current[segment]
      continue
    if not hasattr(current, segment):
      return _RUNTIME_QUERY_MISSING
    current = getattr(current, segment)
  return current


def _build_runtime_filter_getters(
  filter_specs: tuple[StandaloneSurfaceFilterParamSpec, ...],
  *,
  overrides: dict[str, Callable[[Any], Any]] | None = None,
) -> dict[str, Callable[[Any], Any]]:
  getters: dict[str, Callable[[Any], Any]] = {}
  for spec in filter_specs:
    if spec.value_root:
      getters[spec.key] = lambda item: item
      continue
    path = _default_runtime_query_value_path(spec.key, spec.value_path)
    if not path:
      continue
    getters[spec.key] = lambda item, path=path: _resolve_runtime_query_path_value(item, path)
  if overrides:
    getters.update(overrides)
  return getters


def _build_runtime_sort_getters(
  sort_specs: tuple[StandaloneSurfaceSortFieldSpec, ...],
  *,
  overrides: dict[str, Callable[[Any], Any]] | None = None,
) -> dict[str, Callable[[Any], Any]]:
  getters: dict[str, Callable[[Any], Any]] = {}
  for spec in sort_specs:
    path = _default_runtime_query_value_path(spec.key, spec.value_path)
    if not path:
      continue
    getters[spec.key] = lambda item, path=path: _resolve_runtime_query_path_value(item, path)
  if overrides:
    getters.update(overrides)
  return getters


def _evaluate_runtime_filter_condition(
  candidate_value: Any,
  *,
  operator: str,
  operand: Any,
  quantifier: str | None = None,
) -> bool:
  if quantifier is not None and isinstance(candidate_value, (list, tuple, set)):
    element_matches = [
      _evaluate_runtime_filter_condition(
        element,
        operator=operator,
        operand=operand,
      )
      for element in candidate_value
    ]
    if quantifier == "any":
      return any(element_matches)
    if quantifier == "all":
      return bool(element_matches) and all(element_matches)
    if quantifier == "none":
      return not any(element_matches)
    raise ValueError(f"Unsupported runtime filter quantifier: {quantifier}")
  if operator == "eq":
    return candidate_value == operand
  if operator == "prefix":
    return isinstance(candidate_value, str) and isinstance(operand, str) and candidate_value.startswith(operand)
  if operator == "contains_all":
    candidate_values = set(candidate_value or ())
    operand_values = set(operand or ())
    return operand_values.issubset(candidate_values)
  if operator == "contains_any":
    candidate_values = set(candidate_value or ())
    operand_values = set(operand or ())
    return not candidate_values.isdisjoint(operand_values)
  if operator == "include":
    operand_values = tuple(operand or ())
    return candidate_value in operand_values
  if operator in {"gt", "ge", "lt", "le"}:
    candidate_datetime = _normalize_runtime_datetime_filter_value(candidate_value)
    operand_datetime = _normalize_runtime_datetime_filter_value(operand)
    if candidate_datetime is not None and operand_datetime is not None:
      candidate_comparable: float | int | datetime = candidate_datetime
      operand_comparable: float | int | datetime = operand_datetime
    else:
      candidate_number = _normalize_runtime_numeric_filter_value(candidate_value)
      operand_number = _normalize_runtime_numeric_filter_value(operand)
      if candidate_number is None or operand_number is None:
        return False
      candidate_comparable = candidate_number
      operand_comparable = operand_number
    if operator == "gt":
      return candidate_comparable > operand_comparable
    if operator == "ge":
      return candidate_comparable >= operand_comparable
    if operator == "lt":
      return candidate_comparable < operand_comparable
    return candidate_comparable <= operand_comparable
  raise ValueError(f"Unsupported runtime filter operator: {operator}")


def _evaluate_runtime_filter_conditions(
  item: Any,
  conditions: tuple[StandaloneSurfaceFilterCondition, ...] | list[StandaloneSurfaceFilterCondition],
  *,
  filter_getters: dict[str, Callable[[Any], Any]],
  require_known_conditions: bool,
) -> bool:
  known_conditions = 0
  for condition in conditions:
    getter = filter_getters.get(condition.key)
    if getter is None:
      continue
    candidate_value = getter(item)
    if candidate_value is _RUNTIME_QUERY_MISSING:
      continue
    known_conditions += 1
    if not _evaluate_runtime_filter_condition(
      candidate_value,
      operator=condition.operator,
      operand=condition.value,
      quantifier=condition.quantifier,
    ):
      return False
  if require_known_conditions and known_conditions == 0:
    return False
  return True


def _normalize_runtime_collection_items(value: Any) -> tuple[Any, ...] | None:
  if value is _RUNTIME_QUERY_MISSING:
    return None
  if value is None:
    return ()
  if isinstance(value, dict):
    return tuple(value.values())
  if isinstance(value, (list, tuple, set)):
    return tuple(value)
  return None


def _resolve_runtime_collection_path_values(
  item: Any,
  path: tuple[str, ...],
  *,
  strict: bool = False,
) -> tuple[Any, ...] | None:
  def visit(current: Any, remaining_path: tuple[str, ...]) -> tuple[bool, tuple[Any, ...]]:
    if current is _RUNTIME_QUERY_MISSING:
      return (False, ())
    if current is None:
      return (True, ())
    if not remaining_path:
      normalized_items = _normalize_runtime_collection_items(current)
      if normalized_items is not None:
        return (True, normalized_items)
      return (True, (current,))
    segment = remaining_path[0]
    tail = remaining_path[1:]
    if isinstance(current, dict):
      if segment in current:
        return visit(current[segment], tail)
      if strict:
        return (False, ())
      found_any = False
      flattened_values: list[Any] = []
      for value in current.values():
        found, nested_values = visit(value, remaining_path)
        found_any = found_any or found
        flattened_values.extend(nested_values)
      return (found_any, tuple(flattened_values))
    if isinstance(current, (list, tuple, set)):
      if strict:
        return (False, ())
      found_any = False
      flattened_values: list[Any] = []
      for value in current:
        found, nested_values = visit(value, remaining_path)
        found_any = found_any or found
        flattened_values.extend(nested_values)
      return (found_any, tuple(flattened_values))
    if not hasattr(current, segment):
      return (False, ())
    return visit(getattr(current, segment), tail)

  found_any, resolved_values = visit(item, path)
  if not found_any:
    return None
  return resolved_values


def _evaluate_runtime_quantified_expression_results(
  results: tuple[bool | None, ...],
  *,
  quantifier: str,
) -> bool | None:
  if quantifier == "any":
    if any(result is True for result in results):
      return True
    if not results or any(result is False for result in results):
      return False
    return None
  if quantifier == "all":
    if not results:
      return False
    if any(result is False for result in results):
      return False
    if all(result is True for result in results):
      return True
    return None
  if quantifier == "none":
    if any(result is True for result in results):
      return False
    if not results or any(result is False for result in results):
      return True
    return None
  raise ValueError(f"Unsupported runtime collection quantifier: {quantifier}")


def _evaluate_runtime_filter_expression(
  item: Any,
  expression: StandaloneSurfaceFilterExpressionNode,
  *,
  filter_getters: dict[str, Callable[[Any], Any]],
) -> bool | None:
  if expression.collection_quantifier is not None:
    collection_items = _resolve_runtime_collection_path_values(
      item,
      expression.collection_path,
      strict=expression.collection_path_strict,
    )
    if collection_items is None:
      return False if expression.collection_path_strict else None
    element_expression = StandaloneSurfaceFilterExpressionNode(
      logic=expression.logic,
      conditions=expression.conditions,
      children=expression.children,
    )
    result = _evaluate_runtime_quantified_expression_results(
      tuple(
        _evaluate_runtime_filter_expression(
          collection_item,
          element_expression,
          filter_getters=filter_getters,
        )
        for collection_item in collection_items
      ),
      quantifier=expression.collection_quantifier,
    )
    if expression.negated:
      if result is None:
        return None
      return not result
    return result
  term_results: list[bool | None] = []
  for condition in expression.conditions:
    getter = filter_getters.get(condition.key)
    if getter is None:
      term_results.append(None)
      continue
    candidate_value = getter(item)
    if candidate_value is _RUNTIME_QUERY_MISSING:
      term_results.append(None)
      continue
    term_results.append(
      _evaluate_runtime_filter_condition(
        candidate_value,
        operator=condition.operator,
        operand=condition.value,
        quantifier=condition.quantifier,
      )
    )
  for child in expression.children:
    term_results.append(
      _evaluate_runtime_filter_expression(
        item,
        child,
        filter_getters=filter_getters,
      )
    )
  if not term_results:
    result: bool | None = True
  elif expression.logic == "and":
    if any(term is False for term in term_results):
      result = False
    elif any(term is True for term in term_results):
      result = True
    else:
      result = None
  elif expression.logic == "or":
    if any(term is True for term in term_results):
      result = True
    elif any(term is False for term in term_results):
      result = False
    else:
      result = None
  else:
    raise ValueError(f"Unsupported filter expression logic: {expression.logic}")
  if expression.negated:
    if result is None:
      return None
    return not result
  return result


def _apply_runtime_query_contract(
  items: list[Any],
  *,
  filters: dict[str, Any] | None,
  filter_specs: tuple[StandaloneSurfaceFilterParamSpec, ...] = (),
  sort_specs: tuple[StandaloneSurfaceSortFieldSpec, ...] = (),
  filter_getter_overrides: dict[str, Callable[[Any], Any]] | None = None,
  sort_getter_overrides: dict[str, Callable[[Any], Any]] | None = None,
) -> list[Any]:
  conditions = _extract_runtime_filter_conditions(filters)
  expression = _extract_runtime_filter_expression(filters)
  sort_terms = _extract_runtime_sort_terms(filters)
  filter_getters = _build_runtime_filter_getters(
    filter_specs,
    overrides=filter_getter_overrides,
  )
  sort_getters = _build_runtime_sort_getters(
    sort_specs,
    overrides=sort_getter_overrides,
  )
  resolved = list(items)
  if conditions or expression is not None:
    ungrouped_conditions = tuple(
      condition
      for condition in conditions
      if condition.group is None
    )
    grouped_conditions: dict[str, list[StandaloneSurfaceFilterCondition]] = {}
    for condition in conditions:
      if condition.group is None:
        continue
      grouped_conditions.setdefault(condition.group, []).append(condition)
    resolved = [
      item
      for item in resolved
      if _evaluate_runtime_filter_conditions(
        item,
        ungrouped_conditions,
        filter_getters=filter_getters,
        require_known_conditions=False,
      ) and (
        not grouped_conditions
        or any(
          _evaluate_runtime_filter_conditions(
            item,
            group_conditions,
            filter_getters=filter_getters,
            require_known_conditions=True,
          )
          for group_conditions in grouped_conditions.values()
        )
      ) and (
        expression is None
        or _evaluate_runtime_filter_expression(
          item,
          expression,
          filter_getters=filter_getters,
        ) is not False
      )
    ]
  for term in reversed(sort_terms):
    getter = sort_getters.get(term.key)
    if getter is None:
      continue
    resolved.sort(
      key=lambda item: _normalize_runtime_sort_value(getter(item)),
      reverse=term.direction == "desc",
    )
  return resolved


def _run_effective_updated_at(run: RunRecord) -> datetime:
  return run.ended_at or run.started_at


def _apply_runtime_query_to_strategies(
  strategies: list[StrategyMetadata],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[StrategyMetadata]:
  return _apply_runtime_query_contract(
    strategies,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
  )


def _apply_runtime_query_to_presets(
  presets: list[ExperimentPreset],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[ExperimentPreset]:
  return _apply_runtime_query_contract(
    presets,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
  )


def _apply_runtime_query_to_runs(
  runs: list[RunRecord],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[RunRecord]:
  return _apply_runtime_query_contract(
    runs,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
    filter_getter_overrides={
      "updated_at": _run_effective_updated_at,
      "timing.updated_at": _run_effective_updated_at,
    },
    sort_getter_overrides={
      "updated_at": _run_effective_updated_at,
      "timing.updated_at": _run_effective_updated_at,
    },
  )


def _apply_runtime_query_to_comparison(
  comparison: RunComparison,
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> RunComparison:
  run_order_index = {
    run_id: index
    for index, run_id in enumerate(comparison.requested_run_ids)
  }
  narratives = _apply_runtime_query_contract(
    list(comparison.narratives),
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
    filter_getter_overrides={
      "intent": lambda narrative: comparison.intent,
      "narrative_score": lambda narrative: narrative.insight_score,
    },
    sort_getter_overrides={
      "run_id_order": lambda narrative: run_order_index.get(
        narrative.run_id,
        len(run_order_index),
      ),
      "narratives.run_id_order": lambda narrative: run_order_index.get(
        narrative.run_id,
        len(run_order_index),
      ),
      "narrative_score": lambda narrative: narrative.insight_score,
      "narratives.insight_score": lambda narrative: narrative.insight_score,
    },
  )
  return replace(comparison, narratives=tuple(narratives))


def _apply_runtime_query_to_market_data_lineage_history(
  records: list[MarketDataLineageHistoryRecord],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[MarketDataLineageHistoryRecord]:
  return _apply_runtime_query_contract(
    records,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
  )


def _apply_runtime_query_to_market_data_ingestion_jobs(
  records: list[MarketDataIngestionJobRecord],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[MarketDataIngestionJobRecord]:
  return _apply_runtime_query_contract(
    records,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
  )


__all__ = [
  "RunSubresourceContract",
  "RunSubresourceRuntimeBinding",
  "StandaloneSurfaceCollectionPathParameterSpec",
  "StandaloneSurfaceCollectionPathSpec",
  "StandaloneSurfaceFilterCondition",
  "StandaloneSurfaceFilterConstraintSpec",
  "StandaloneSurfaceFilterExpressionNode",
  "StandaloneSurfaceFilterOpenAPISpec",
  "StandaloneSurfaceFilterOperatorSpec",
  "StandaloneSurfaceFilterParamSpec",
  "StandaloneSurfaceRuntimeBinding",
  "StandaloneSurfaceSortFieldSpec",
  "StandaloneSurfaceSortTerm",
  "_apply_runtime_query_to_comparison",
  "_apply_runtime_query_to_market_data_ingestion_jobs",
  "_apply_runtime_query_to_market_data_lineage_history",
  "_apply_runtime_query_to_presets",
  "_apply_runtime_query_to_runs",
  "_apply_runtime_query_to_strategies",
  "_build_datetime_range_filter_operators",
  "_build_numeric_range_filter_operators",
]
