from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Any

from akra_trader.application_support.run_surfaces import _build_order_action_availability
from akra_trader.application_support.run_surfaces import _serialize_run_subresource_envelope
from akra_trader.domain.models import Order
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunSurfaceCapabilities


def _serialize_run_order_subresource_item(
  run: RunRecord,
  *,
  order: Order,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, Any]:
  return {
    **asdict(order),
    "action_availability": _build_order_action_availability(
      run=run,
      order=order,
      capabilities=capabilities,
    ),
  }


def _serialize_run_orders_subresource_body(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
) -> list[dict[str, Any]]:
  return [
    _serialize_run_order_subresource_item(
      run,
      order=order,
      capabilities=capabilities,
    )
    for order in run.orders
  ]


def _serialize_run_positions_subresource_body(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
) -> list[dict[str, Any]]:
  _ = capabilities
  return [
    asdict(position)
    for position in run.positions.values()
  ]


def _serialize_run_metrics_subresource_body(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, Any]:
  _ = capabilities
  return deepcopy(run.metrics)


def serialize_run_subresource_response(
  run: RunRecord,
  *,
  subresource_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  from akra_trader.application_support.standalone_surfaces import (
    get_run_subresource_runtime_binding,
  )

  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  binding = get_run_subresource_runtime_binding(subresource_key, resolved_capabilities)
  return _serialize_run_subresource_envelope(
    run,
    capabilities=resolved_capabilities,
    body_key=binding.contract.body_key,
    body_value=binding.body_serializer(run, resolved_capabilities),
  )


def serialize_run_orders_response(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  return serialize_run_subresource_response(
    run,
    subresource_key="orders",
    capabilities=capabilities,
  )


def serialize_run_positions_response(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  return serialize_run_subresource_response(
    run,
    subresource_key="positions",
    capabilities=capabilities,
  )


def serialize_run_metrics_response(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  return serialize_run_subresource_response(
    run,
    subresource_key="metrics",
    capabilities=capabilities,
  )
