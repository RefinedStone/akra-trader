from __future__ import annotations

from datetime import UTC
from datetime import datetime
import inspect
import json
from numbers import Number
import re
from types import UnionType
from typing import Any
from typing import Union
from typing import get_args
from typing import get_origin

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from pydantic import BaseModel
from pydantic import Field

from akra_trader.application import list_standalone_surface_runtime_bindings
from akra_trader.application import StandaloneSurfaceFilterCondition
from akra_trader.application import TradingApplication
from akra_trader.application import execute_standalone_surface_binding
from akra_trader.application import StandaloneSurfaceFilterParamSpec
from akra_trader.application import StandaloneSurfaceSortTerm
from akra_trader.application import StandaloneSurfaceRuntimeBinding
from akra_trader.application import StandaloneSurfaceFilterExpressionNode
from akra_trader.bootstrap import Container


class StrategyRegistrationRequest(BaseModel):
  strategy_id: str
  module_path: str
  class_name: str


class ExperimentPresetRequest(BaseModel):
  name: str
  preset_id: str | None = None
  description: str = ""
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] = Field(default_factory=list)
  parameters: dict[str, Any] = Field(default_factory=dict)
  benchmark_family: str | None = None


class ExperimentPresetLifecycleActionRequest(BaseModel):
  action: str
  actor: str = "operator"
  reason: str = "manual_preset_lifecycle_action"


class ExperimentPresetUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] | None = None
  parameters: dict[str, Any] | None = None
  benchmark_family: str | None = None
  actor: str = "operator"
  reason: str = "manual_preset_edit"


class ExperimentPresetRevisionRestoreRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_preset_revision_restore"


class BacktestRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  parameters: dict[str, Any] = Field(default_factory=dict)
  start_at: datetime | None = None
  end_at: datetime | None = None
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class SandboxRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class LiveRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  operator_reason: str = "guarded_live_launch"
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class GuardedLiveActionRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_operator_action"


class GuardedLiveOrderReplaceRequest(GuardedLiveActionRequest):
  price: float = Field(gt=0)
  quantity: float | None = Field(default=None, gt=0)


class ExternalIncidentSyncRequest(BaseModel):
  provider: str
  event_kind: str
  actor: str = "external"
  detail: str = "external_incident_sync"
  alert_id: str | None = None
  external_reference: str | None = None
  workflow_reference: str | None = None
  occurred_at: datetime | None = None
  escalation_level: int | None = Field(default=None, ge=1)
  payload: dict[str, Any] = Field(default_factory=dict)


REQUEST_PAYLOAD_MODELS: dict[str, tuple[type[BaseModel], dict[str, Any]]] = {
  "preset_create": (ExperimentPresetRequest, {}),
  "preset_update": (ExperimentPresetUpdateRequest, {"exclude_unset": True}),
  "preset_revision_restore": (ExperimentPresetRevisionRestoreRequest, {}),
  "preset_lifecycle_action": (ExperimentPresetLifecycleActionRequest, {}),
  "strategy_register": (StrategyRegistrationRequest, {}),
  "backtest_launch": (BacktestRequest, {}),
  "sandbox_launch": (SandboxRunRequest, {}),
  "paper_launch": (SandboxRunRequest, {}),
  "live_launch": (LiveRunRequest, {}),
  "external_incident_sync": (ExternalIncidentSyncRequest, {}),
  "guarded_live_action": (GuardedLiveActionRequest, {}),
  "guarded_live_order_replace": (GuardedLiveOrderReplaceRequest, {}),
}


def _build_header_alias(header_key: str) -> str:
  return "-".join(part.capitalize() for part in header_key.split("_"))


def _build_query_default(spec: StandaloneSurfaceFilterParamSpec) -> Any:
  kwargs: dict[str, Any] = {}
  if spec.constraints is not None:
    constraint_values = (
      ("min_length", spec.constraints.min_length),
      ("max_length", spec.constraints.max_length),
      ("ge", spec.constraints.ge),
      ("le", spec.constraints.le),
      ("pattern", spec.constraints.pattern),
    )
    for key, value in constraint_values:
      if value is not None:
        kwargs[key] = value
  if spec.openapi is not None:
    openapi_values = (
      ("alias", spec.openapi.alias),
      ("title", spec.openapi.title),
      ("description", spec.openapi.description),
    )
    for key, value in openapi_values:
      if value is not None:
        kwargs[key] = value
    if spec.openapi.examples:
      kwargs["examples"] = list(spec.openapi.examples)
    if spec.openapi.deprecated:
      kwargs["deprecated"] = True
  if spec.default_factory is not None:
    return Query(default_factory=spec.default_factory, **kwargs)
  return Query(default=spec.default, **kwargs)


def _build_sort_query_default(binding: StandaloneSurfaceRuntimeBinding) -> Any:
  examples = [
    f"{field.key}:{field.default_direction}"
    for field in binding.sort_field_specs
  ]
  return Query(
    default_factory=list,
    title="Sort",
    description="Sort fields in `<field>` or `<field>:<direction>` format.",
    examples=examples,
  )


def _build_filter_expression_query_default() -> Any:
  return Query(
    default=None,
    title="Filter expression",
    description=(
      "JSON boolean expression tree using `logic`, `conditions`, `children`, and optional `negated` fields."
    ),
    examples=[
      (
        '{"logic":"or","children":['
        '{"logic":"and","conditions":[{"key":"total_return_pct","operator":"ge","value":20},'
        '{"key":"trade_count","operator":"ge","value":2}]},'
        '{"logic":"and","conditions":[{"key":"trade_count","operator":"ge","value":5},'
        '{"key":"total_return_pct","operator":"ge","value":15}]}]}'
      ),
    ],
  )


def _build_route_openapi_extra(binding: StandaloneSurfaceRuntimeBinding) -> dict[str, Any] | None:
  if not binding.filter_param_specs and not binding.sort_field_specs:
    return None
  return {
    "x-akra-query-schema": {
      "grouped_filters": {
        "param_pattern": "group__<group_key>__<filter_key>__<operator>",
        "semantics": "Ungrouped filters are ANDed together. Grouped filters are ANDed within a group and ORed across groups.",
      },
      "expression_trees": {
        "param": "filter_expr",
        "format": "json",
        "supports_negation": True,
        "logic_values": ["and", "or"],
        "predicate_refs": {
          "registry_field": "predicates",
          "reference_field": "predicate_ref",
        },
        "quantified_conditions": {
          "field": "quantifier",
          "values": ["any", "all", "none"],
          "semantics": "Applies the condition across list-valued candidates.",
        },
        "collection_nodes": {
          "field": "collection",
          "shape": {
            "path": "<collection path>",
            "quantifier": "any|all|none",
          },
          "semantics": "Evaluates the node against collection elements, flattening nested collection-of-collection paths, and folds the results with the declared quantifier.",
        },
        "condition_shape": {
          "key": "<filter_key>",
          "operator": "<operator>",
          "value": "<typed value>",
          "quantifier": "any|all|none",
        },
        "node_shape": {
          "logic": "and|or",
          "conditions": ["<condition>", "..."],
          "children": ["<node>", "..."],
          "negated": "boolean",
          "predicate_ref": "<named predicate>",
          "collection": {
            "path": "<collection path>",
            "quantifier": "any|all|none",
          },
        },
      },
      "filters": [
        {
          "key": spec.key,
          "query_exposed": spec.query_exposed,
          "value_type": _describe_filter_value_type(spec.annotation),
          "value_path": list(spec.value_path),
          "operators": [
            {
              "key": operator.key,
              "label": operator.label,
              "description": operator.description,
              "value_shape": operator.value_shape,
            }
            for operator in spec.operators
          ],
        }
        for spec in binding.filter_param_specs
      ],
      "sort_fields": [
        {
          "key": field.key,
          "label": field.label,
          "description": field.description,
          "default_direction": field.default_direction,
          "value_type": field.value_type,
          "value_path": list(field.value_path),
        }
        for field in binding.sort_field_specs
      ],
    }
  }


def _describe_filter_value_type(annotation: Any) -> str:
  resolved_annotation = _resolve_filter_scalar_annotation(annotation)
  origin = get_origin(annotation)
  if origin in {list, tuple}:
    return f"list[{_describe_filter_value_type(resolved_annotation)}]"
  if resolved_annotation is int:
    return "integer"
  if resolved_annotation is float:
    return "number"
  if resolved_annotation is datetime:
    return "datetime"
  return "string"


def _resolve_filter_scalar_annotation(annotation: Any) -> Any:
  origin = get_origin(annotation)
  if origin in {list, tuple}:
    args = tuple(arg for arg in get_args(annotation) if arg is not Ellipsis)
    if args:
      return _resolve_filter_scalar_annotation(args[0])
  if origin in {UnionType, Union}:
    args = tuple(arg for arg in get_args(annotation) if arg is not type(None))
    if len(args) == 1:
      return _resolve_filter_scalar_annotation(args[0])
  return annotation


def _coerce_filter_scalar_value(annotation: Any, raw_value: str) -> Any:
  resolved_annotation = _resolve_filter_scalar_annotation(annotation)
  if raw_value is None:
    return None
  if resolved_annotation is int:
    if isinstance(raw_value, bool):
      raise ValueError("Boolean values are not valid integers for this filter.")
    return int(raw_value)
  if resolved_annotation is float:
    if isinstance(raw_value, bool):
      raise ValueError("Boolean values are not valid numbers for this filter.")
    return float(raw_value)
  if resolved_annotation is datetime:
    if isinstance(raw_value, datetime):
      parsed = raw_value
    else:
      normalized_value = str(raw_value).replace("Z", "+00:00")
      parsed = datetime.fromisoformat(normalized_value)
    if parsed.tzinfo is None:
      return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
  if isinstance(raw_value, str):
    return raw_value
  return str(raw_value)


def _validate_filter_query_value(
  spec: StandaloneSurfaceFilterParamSpec,
  value: Any,
) -> None:
  if value is None or spec.constraints is None:
    return
  if isinstance(value, (list, tuple, set)):
    for item in value:
      _validate_filter_query_value(spec, item)
    return
  if isinstance(value, str):
    if spec.constraints.min_length is not None and len(value) < spec.constraints.min_length:
      raise ValueError(f"Filter value for {spec.key} is shorter than {spec.constraints.min_length}.")
    if spec.constraints.max_length is not None and len(value) > spec.constraints.max_length:
      raise ValueError(f"Filter value for {spec.key} is longer than {spec.constraints.max_length}.")
    if spec.constraints.pattern is not None and re.fullmatch(spec.constraints.pattern, value) is None:
      raise ValueError(f"Filter value for {spec.key} does not match the required pattern.")
    return
  if isinstance(value, Number) and not isinstance(value, bool):
    if spec.constraints.ge is not None and value < spec.constraints.ge:
      raise ValueError(f"Filter value for {spec.key} must be >= {spec.constraints.ge}.")
    if spec.constraints.le is not None and value > spec.constraints.le:
      raise ValueError(f"Filter value for {spec.key} must be <= {spec.constraints.le}.")


def _coerce_filter_query_values(
  spec: StandaloneSurfaceFilterParamSpec,
  *,
  value_shape: str,
  values: list[str],
) -> Any:
  if value_shape == "list":
    coerced_values = [
      _coerce_filter_scalar_value(spec.annotation, raw_value)
      for raw_value in values
    ]
    _validate_filter_query_value(spec, coerced_values)
    return coerced_values
  if not values:
    return None
  coerced_value = _coerce_filter_scalar_value(spec.annotation, values[-1])
  _validate_filter_query_value(spec, coerced_value)
  return coerced_value


def _coerce_filter_expression_value(
  spec: StandaloneSurfaceFilterParamSpec,
  *,
  value_shape: str,
  raw_value: Any,
) -> Any:
  if value_shape == "list":
    raw_values = list(raw_value) if isinstance(raw_value, (list, tuple, set)) else [raw_value]
    coerced_values = [
      _coerce_filter_scalar_value(spec.annotation, value)
      for value in raw_values
    ]
    _validate_filter_query_value(spec, coerced_values)
    return coerced_values
  coerced_value = _coerce_filter_scalar_value(spec.annotation, raw_value)
  _validate_filter_query_value(spec, coerced_value)
  return coerced_value


def _parse_runtime_filter_expression_condition(
  raw_condition: Any,
  *,
  filter_specs_by_key: dict[str, StandaloneSurfaceFilterParamSpec],
) -> StandaloneSurfaceFilterCondition:
  if not isinstance(raw_condition, dict):
    raise ValueError("Filter expression conditions must be objects.")
  filter_key = raw_condition.get("key")
  if not isinstance(filter_key, str) or not filter_key:
    raise ValueError("Filter expression conditions must declare a filter key.")
  spec = filter_specs_by_key.get(filter_key)
  if spec is None:
    raise ValueError(f"Unsupported filter key in filter expression: {filter_key}")
  operator_key = raw_condition.get("operator")
  if not isinstance(operator_key, str) or not operator_key:
    if spec.operators:
      operator_key = spec.operators[0].key
    else:
      operator_key = "eq"
  operator_specs = {
    operator.key: operator
    for operator in spec.operators
  }
  operator_spec = operator_specs.get(operator_key)
  if operator_spec is None:
    raise ValueError(f"Unsupported filter operator for {filter_key}: {operator_key}")
  if "value" not in raw_condition:
    raise ValueError(f"Filter expression conditions must declare a value for {filter_key}.")
  quantifier = raw_condition.get("quantifier")
  if quantifier is not None:
    if not isinstance(quantifier, str) or quantifier not in {"any", "all", "none"}:
      raise ValueError("Filter expression quantifier must be one of `any`, `all`, or `none`.")
  return StandaloneSurfaceFilterCondition(
    key=filter_key,
    operator=operator_key,
    value=_coerce_filter_expression_value(
      spec,
      value_shape=operator_spec.value_shape,
      raw_value=raw_condition["value"],
    ),
    quantifier=quantifier,
  )


def _parse_runtime_filter_expression_node(
  raw_node: Any,
  *,
  filter_specs_by_key: dict[str, StandaloneSurfaceFilterParamSpec],
  predicate_registry: dict[str, Any],
  active_predicate_refs: tuple[str, ...] = (),
) -> StandaloneSurfaceFilterExpressionNode:
  if not isinstance(raw_node, dict):
    raise ValueError("Filter expression nodes must be objects.")
  predicate_ref = raw_node.get("predicate_ref")
  if predicate_ref is not None:
    if not isinstance(predicate_ref, str) or not predicate_ref:
      raise ValueError("Filter expression predicate references must be non-empty strings.")
    if predicate_ref in active_predicate_refs:
      raise ValueError(f"Cyclic filter predicate reference detected for {predicate_ref}.")
    referenced_node = predicate_registry.get(predicate_ref)
    if referenced_node is None:
      raise ValueError(f"Unknown filter predicate reference: {predicate_ref}")
    resolved = _parse_runtime_filter_expression_node(
      referenced_node,
      filter_specs_by_key=filter_specs_by_key,
      predicate_registry=predicate_registry,
      active_predicate_refs=(*active_predicate_refs, predicate_ref),
    )
    if bool(raw_node.get("negated", False)):
      return StandaloneSurfaceFilterExpressionNode(
        logic=resolved.logic,
        conditions=resolved.conditions,
        children=resolved.children,
        negated=not resolved.negated,
      )
    return resolved
  logic = raw_node.get("logic", "and")
  if not isinstance(logic, str) or logic.lower() not in {"and", "or"}:
    raise ValueError("Filter expression logic must be either `and` or `or`.")
  collection_path: tuple[str, ...] = ()
  collection_quantifier: str | None = None
  raw_collection = raw_node.get("collection")
  if raw_collection is not None:
    if not isinstance(raw_collection, dict):
      raise ValueError("Filter expression collection nodes must declare an object `collection` field.")
    raw_collection_path = raw_collection.get("path")
    if isinstance(raw_collection_path, str):
      collection_path = tuple(
        segment
        for segment in raw_collection_path.split(".")
        if segment
      )
    elif isinstance(raw_collection_path, list) and all(isinstance(segment, str) and segment for segment in raw_collection_path):
      collection_path = tuple(raw_collection_path)
    else:
      raise ValueError("Filter expression collection paths must be a dotted string or list of path segments.")
    raw_collection_quantifier = raw_collection.get("quantifier")
    if not isinstance(raw_collection_quantifier, str) or raw_collection_quantifier not in {"any", "all", "none"}:
      raise ValueError("Filter expression collection quantifier must be one of `any`, `all`, or `none`.")
    collection_quantifier = raw_collection_quantifier
  raw_conditions = raw_node.get("conditions", [])
  if not isinstance(raw_conditions, list):
    raise ValueError("Filter expression `conditions` must be a list.")
  raw_children = raw_node.get("children", [])
  if not isinstance(raw_children, list):
    raise ValueError("Filter expression `children` must be a list.")
  conditions = tuple(
    _parse_runtime_filter_expression_condition(
      raw_condition,
      filter_specs_by_key=filter_specs_by_key,
    )
    for raw_condition in raw_conditions
  )
  children = tuple(
    _parse_runtime_filter_expression_node(
      raw_child,
      filter_specs_by_key=filter_specs_by_key,
      predicate_registry=predicate_registry,
      active_predicate_refs=active_predicate_refs,
    )
    for raw_child in raw_children
  )
  if not conditions and not children:
    raise ValueError("Filter expression nodes must declare conditions or children.")
  return StandaloneSurfaceFilterExpressionNode(
    logic=logic.lower(),
    conditions=conditions,
    children=children,
    negated=bool(raw_node.get("negated", False)),
    collection_path=collection_path,
    collection_quantifier=collection_quantifier,
  )


def _build_runtime_filter_expression(
  binding: StandaloneSurfaceRuntimeBinding,
  *,
  raw_expression: str | None,
) -> StandaloneSurfaceFilterExpressionNode | None:
  if not raw_expression:
    return None
  try:
    parsed_expression = json.loads(raw_expression)
  except json.JSONDecodeError as exc:
    raise ValueError("Filter expression must be valid JSON.") from exc
  predicate_registry: dict[str, Any] = {}
  root_expression = parsed_expression
  if isinstance(parsed_expression, dict) and "predicates" in parsed_expression:
    raw_predicates = parsed_expression.get("predicates")
    if not isinstance(raw_predicates, dict):
      raise ValueError("Filter expression `predicates` must be an object map.")
    predicate_registry = raw_predicates
    if "root" in parsed_expression:
      root_expression = parsed_expression["root"]
    else:
      root_expression = {
        key: value
        for key, value in parsed_expression.items()
        if key != "predicates"
      }
  return _parse_runtime_filter_expression_node(
    root_expression,
    filter_specs_by_key={
      spec.key: spec
      for spec in binding.filter_param_specs
    },
    predicate_registry=predicate_registry,
  )


def _parse_grouped_filter_query_key(
  raw_key: str,
  *,
  alias: str,
  default_operator: str,
  supported_operators: dict[str, Any],
) -> tuple[str, str] | None:
  if not raw_key.startswith("group__"):
    return None
  parts = raw_key.split("__")
  if len(parts) < 3:
    return None
  _, group_key, *remainder = parts
  if not group_key or not remainder:
    return None
  operator_key = default_operator
  alias_key = "__".join(remainder)
  if remainder[-1] in supported_operators:
    operator_key = remainder[-1]
    alias_key = "__".join(remainder[:-1])
  if alias_key != alias:
    return None
  return group_key, operator_key


def _has_meaningful_filter_value(value: Any) -> bool:
  if value is None:
    return False
  if isinstance(value, str):
    return bool(value)
  if isinstance(value, (list, tuple, set, dict)):
    return bool(value)
  return True


def _build_runtime_query_filters(
  binding: StandaloneSurfaceRuntimeBinding,
  *,
  kwargs: dict[str, Any],
  request: Request | None,
) -> dict[str, Any] | None:
  if not binding.filter_param_specs and not binding.sort_field_specs:
    return None
  filters = {
    spec.key: kwargs[spec.key]
    for spec in binding.filter_param_specs
    if spec.query_exposed
  }
  filter_expression = _build_runtime_filter_expression(
    binding,
    raw_expression=kwargs.get("filter_expr"),
  )
  if filter_expression is not None:
    filters["__filter_expression__"] = filter_expression
  conditions: list[StandaloneSurfaceFilterCondition] = []
  if request is not None:
    query_params = request.query_params
    for spec in binding.filter_param_specs:
      if not spec.query_exposed:
        continue
      alias = spec.openapi.alias if spec.openapi and spec.openapi.alias else spec.key
      supported_operators = {
        operator.key: operator
        for operator in spec.operators
      }
      default_operator = spec.operators[0].key if spec.operators else "eq"
      base_value = kwargs[spec.key]
      if _has_meaningful_filter_value(base_value):
        conditions.append(
          StandaloneSurfaceFilterCondition(
            key=spec.key,
            operator=default_operator,
            value=base_value,
          )
        )
      for raw_key in query_params.keys():
        grouped = _parse_grouped_filter_query_key(
          raw_key,
          alias=alias,
          default_operator=default_operator,
          supported_operators=supported_operators,
        )
        if grouped is not None:
          group_key, operator_key = grouped
          operator_spec = supported_operators[operator_key]
          conditions.append(
            StandaloneSurfaceFilterCondition(
              key=spec.key,
              operator=operator_key,
              value=_coerce_filter_query_values(
                spec,
                value_shape=operator_spec.value_shape,
                values=query_params.getlist(raw_key),
              ),
              group=group_key,
            )
          )
          continue
        if not raw_key.startswith(f"{alias}__"):
          continue
        operator_key = raw_key.split("__", 1)[1]
        if operator_key not in supported_operators:
          raise ValueError(f"Unsupported filter operator for {spec.key}: {operator_key}")
        operator_spec = supported_operators[operator_key]
        conditions.append(
          StandaloneSurfaceFilterCondition(
            key=spec.key,
            operator=operator_key,
            value=_coerce_filter_query_values(
              spec,
              value_shape=operator_spec.value_shape,
              values=query_params.getlist(raw_key),
            ),
          )
        )
    if conditions:
      filters["__filter_conditions__"] = tuple(conditions)
    if binding.sort_field_specs:
      sort_terms: list[StandaloneSurfaceSortTerm] = []
      allowed_sort_fields = {
        field.key: field
        for field in binding.sort_field_specs
      }
      for raw_sort in kwargs.get("sort", ()):
        field_key, separator, direction = raw_sort.partition(":")
        if field_key not in allowed_sort_fields:
          raise ValueError(f"Unsupported sort field: {field_key}")
        if not separator:
          direction = allowed_sort_fields[field_key].default_direction
        normalized_direction = direction.lower()
        if normalized_direction not in {"asc", "desc"}:
          raise ValueError(f"Unsupported sort direction for {field_key}: {direction}")
        sort_terms.append(
          StandaloneSurfaceSortTerm(
            key=field_key,
            direction=normalized_direction,
          )
        )
      if sort_terms:
        filters["__sort_terms__"] = tuple(sort_terms)
  return filters


def create_router(container: Container) -> APIRouter:
  router = APIRouter()

  def get_app() -> TradingApplication:
    return container.app

  def dispatch_standalone_binding(
    *,
    binding: StandaloneSurfaceRuntimeBinding,
    app: TradingApplication,
    run_id: str | None = None,
    filters: dict[str, Any] | None = None,
    request_payload: dict[str, Any] | None = None,
    path_params: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        run_id=run_id,
        filters=filters,
        request_payload=request_payload,
        path_params=path_params,
        headers=headers,
      )
    except PermissionError as exc:
      raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  def build_standalone_surface_route_handler(binding: StandaloneSurfaceRuntimeBinding):
    def handle_surface(**kwargs: Any) -> dict[str, Any]:
      request_payload = None
      if binding.request_payload_kind is not None:
        request_model = kwargs["request"]
        _, dump_kwargs = REQUEST_PAYLOAD_MODELS[binding.request_payload_kind]
        request_payload = request_model.model_dump(**dump_kwargs)
      request_context = kwargs.get("request")
      return dispatch_standalone_binding(
        binding=binding,
        app=kwargs["app"],
        run_id=kwargs.get("run_id"),
        filters=_build_runtime_query_filters(
          binding,
          kwargs=kwargs,
          request=request_context,
        ),
        path_params=(
          {key: kwargs[key] for key in binding.path_param_keys}
          if binding.path_param_keys
          else None
        ),
        headers=(
          {key: kwargs.get(key) for key in binding.header_keys}
          if binding.header_keys
          else None
        ),
        request_payload=request_payload,
      )

    parameters: list[inspect.Parameter] = []
    if binding.scope == "run":
      parameters.append(
        inspect.Parameter(
          "run_id",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str,
        )
      )
    for path_param_key in binding.path_param_keys:
      parameters.append(
        inspect.Parameter(
          path_param_key,
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str,
        )
      )
    if binding.filter_param_specs or binding.sort_field_specs:
      parameters.append(
        inspect.Parameter(
          "request",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=Request,
        )
      )
    if binding.filter_param_specs:
      parameters.append(
        inspect.Parameter(
          "filter_expr",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str | None,
          default=_build_filter_expression_query_default(),
        )
      )
    for filter_spec in binding.filter_param_specs:
      if not filter_spec.query_exposed:
        continue
      parameters.append(
        inspect.Parameter(
          filter_spec.key,
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=filter_spec.annotation,
          default=_build_query_default(filter_spec),
        )
      )
    if binding.sort_field_specs:
      parameters.append(
        inspect.Parameter(
          "sort",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=list[str],
          default=_build_sort_query_default(binding),
        )
      )
    if binding.request_payload_kind is not None:
      request_model, _ = REQUEST_PAYLOAD_MODELS[binding.request_payload_kind]
      parameters.append(
        inspect.Parameter(
          "request",
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=request_model,
        )
      )
    for header_key in binding.header_keys:
      parameters.append(
        inspect.Parameter(
          header_key,
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          annotation=str | None,
          default=Header(default=None, alias=_build_header_alias(header_key)),
        )
      )
    parameters.append(
      inspect.Parameter(
        "app",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=TradingApplication,
        default=Depends(get_app),
      )
    )

    handle_surface.__name__ = binding.route_name
    handle_surface.__signature__ = inspect.Signature(
      parameters=parameters,
      return_annotation=Any,
    )
    return handle_surface
  for binding in list_standalone_surface_runtime_bindings(get_app().get_run_surface_capabilities()):
    router.add_api_route(
      binding.route_path,
      build_standalone_surface_route_handler(binding),
      methods=list(binding.methods),
      name=binding.route_name,
      summary=binding.response_title,
      openapi_extra=_build_route_openapi_extra(binding),
    )

  return router


def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)
