from __future__ import annotations

from datetime import UTC
from datetime import datetime
import inspect
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


def _build_route_openapi_extra(binding: StandaloneSurfaceRuntimeBinding) -> dict[str, Any] | None:
  if not binding.filter_param_specs and not binding.sort_field_specs:
    return None
  return {
    "x-akra-query-schema": {
      "filters": [
        {
          "key": spec.key,
          "value_type": _describe_filter_value_type(spec.annotation),
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
  if resolved_annotation is int:
    return int(raw_value)
  if resolved_annotation is float:
    return float(raw_value)
  if resolved_annotation is datetime:
    normalized_value = raw_value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized_value)
    if parsed.tzinfo is None:
      return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
  return raw_value


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
  }
  conditions: list[StandaloneSurfaceFilterCondition] = []
  if request is not None:
    query_params = request.query_params
    for spec in binding.filter_param_specs:
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
    for filter_spec in binding.filter_param_specs:
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
