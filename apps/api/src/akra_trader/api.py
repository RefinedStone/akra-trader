from __future__ import annotations

import inspect
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request

from akra_trader.application import execute_standalone_surface_binding
from akra_trader.application import list_standalone_surface_runtime_bindings
from akra_trader.application import StandaloneSurfaceRuntimeBinding
from akra_trader.application import TradingApplication
from akra_trader.bootstrap import Container
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.api_filter_helpers import *
from akra_trader.api_filter_helpers import _build_filter_expression_query_default
from akra_trader.api_filter_helpers import _build_header_alias
from akra_trader.api_filter_helpers import _build_query_default
from akra_trader.api_filter_helpers import _build_route_openapi_extra
from akra_trader.api_filter_helpers import _build_runtime_query_filters
from akra_trader.api_filter_helpers import _build_sort_query_default
from akra_trader.api_provider_provenance_routes import register_provider_provenance_explicit_routes
from akra_trader.api_request_payload_models import REQUEST_PAYLOAD_MODELS

def create_router(container: Container) -> APIRouter:
  router = APIRouter()

  def get_app() -> TradingApplication:
    return container.app

  def get_route_run_surface_capabilities() -> RunSurfaceCapabilities:
    get_capabilities = getattr(get_app(), "get_run_surface_capabilities", None)
    if callable(get_capabilities):
      return get_capabilities()
    return RunSurfaceCapabilities()

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
      try:
        filters = _build_runtime_query_filters(
          binding,
          kwargs=kwargs,
          request=request_context,
        )
      except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
      return dispatch_standalone_binding(
        binding=binding,
        app=kwargs["app"],
        run_id=kwargs.get("run_id"),
        filters=filters,
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
  for binding in list_standalone_surface_runtime_bindings(get_route_run_surface_capabilities()):
    router.add_api_route(
      binding.route_path,
      build_standalone_surface_route_handler(binding),
      methods=list(binding.methods),
      name=binding.route_name,
      summary=binding.response_title,
      openapi_extra=_build_route_openapi_extra(binding),
    )

  register_provider_provenance_explicit_routes(router, get_app)

  return router

def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)
