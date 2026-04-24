from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from types import UnionType
from typing import Any
from typing import Union
from typing import get_args
from typing import get_origin

from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathParameterSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterParamSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import RunSurfaceSharedContract


def _describe_standalone_filter_value_type(annotation: Any) -> str:
  origin = get_origin(annotation)
  if origin in {list, tuple}:
    args = tuple(arg for arg in get_args(annotation) if arg is not Ellipsis)
    if args:
      return f"list[{_describe_standalone_filter_value_type(args[0])}]"
  if origin in {UnionType, Union}:
    args = tuple(arg for arg in get_args(annotation) if arg is not type(None))
    if len(args) == 1:
      return _describe_standalone_filter_value_type(args[0])
  if annotation is int:
    return "integer"
  if annotation is float:
    return "number"
  if annotation is datetime:
    return "datetime"
  return "string"


def serialize_standalone_filter_param_spec(
  spec: StandaloneSurfaceFilterParamSpec,
) -> dict[str, Any]:
  return {
    "key": spec.key,
    "query_exposed": spec.query_exposed,
    "value_type": _describe_standalone_filter_value_type(spec.annotation),
    "value_path": list(spec.value_path),
    "value_root": spec.value_root,
    "title": spec.openapi.title if spec.openapi is not None else None,
    "description": spec.openapi.description if spec.openapi is not None else None,
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


def serialize_collection_path_parameter_spec(
  spec: StandaloneSurfaceCollectionPathParameterSpec,
) -> dict[str, Any]:
  hydrated_domain_values = list(spec.domain_values) if spec.domain_values else (
    list(dict.fromkeys(spec.examples))
    if spec.enum_source_kind and spec.examples
    else []
  )
  payload = {
    "key": spec.key,
    "kind": spec.kind,
    "description": spec.description,
    "examples": list(spec.examples),
  }
  if spec.domain_key or spec.domain_source or spec.domain_values:
    payload["domain"] = {
      "key": spec.domain_key or None,
      "source": spec.domain_source or None,
      "values": hydrated_domain_values,
    }
    if spec.enum_source_kind or spec.enum_source_surface_key or spec.enum_source_path:
      payload["domain"]["enum_source"] = {
        "kind": spec.enum_source_kind or None,
        "surface_key": spec.enum_source_surface_key or None,
        "path": list(spec.enum_source_path),
      }
  return payload


def serialize_collection_path_parameter_domain(
  binding: StandaloneSurfaceRuntimeBinding,
  collection_spec: StandaloneSurfaceCollectionPathSpec,
  parameter_spec: StandaloneSurfaceCollectionPathParameterSpec,
) -> dict[str, Any]:
  return {
    "parameter_key": parameter_spec.key,
    "parameter_kind": parameter_spec.kind,
    "collection_label": collection_spec.label,
    "collection_path": list(collection_spec.path),
    "collection_path_template": list(collection_spec.path_template or collection_spec.path),
    "domain": serialize_collection_path_parameter_spec(parameter_spec).get("domain"),
    "surface_key": binding.surface_key,
  }


def serialize_collection_path_spec(
  binding: StandaloneSurfaceRuntimeBinding,
  spec: StandaloneSurfaceCollectionPathSpec,
) -> dict[str, Any]:
  filter_specs_by_key = {
    filter_spec.key: filter_spec
    for filter_spec in binding.filter_param_specs
  }
  return {
    "path": list(spec.path),
    "path_template": list(spec.path_template or spec.path),
    "label": spec.label,
    "collection_kind": spec.collection_kind,
    "item_kind": spec.item_kind,
    "filter_keys": list(spec.filter_keys),
    "description": spec.description,
    "parameters": [
      serialize_collection_path_parameter_spec(parameter)
      for parameter in spec.parameters
    ],
    "element_schema": [
      serialize_standalone_filter_param_spec(filter_specs_by_key[filter_key])
      for filter_key in spec.filter_keys
      if filter_key in filter_specs_by_key
    ],
  }


def serialize_collection_query_expression_authoring() -> dict[str, Any]:
  return {
    "predicate_refs": {
      "registry_field": "predicates",
      "reference_field": "predicate_ref",
    },
    "predicate_templates": {
      "registry_field": "predicate_templates",
      "template_field": "template",
      "parameters_field": "parameters",
      "bindings_field": "bindings",
      "binding_reference_shape": {
        "binding": "<parameter_name>",
      },
    },
    "collection_nodes": {
      "field": "collection",
      "shape": {
        "path": "<collection path>",
        "path_template": "<collection path template>",
        "bindings": {
          "<parameter_key>": "<value or binding reference>",
        },
        "quantifier": "any|all|none",
      },
    },
  }


def list_collection_query_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSurfaceSharedContract, ...]:
  from akra_trader.application_support.standalone_surfaces import (
    list_standalone_surface_runtime_bindings,
  )

  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  contracts: list[RunSurfaceSharedContract] = []
  for binding in list_standalone_surface_runtime_bindings(resolved_capabilities):
    if not binding.collection_path_specs:
      continue
    parameter_domains = [
      serialize_collection_path_parameter_domain(binding, spec, parameter)
      for spec in binding.collection_path_specs
      for parameter in spec.parameters
      if parameter.domain_key or parameter.domain_source or parameter.domain_values
    ]
    contracts.append(
      RunSurfaceSharedContract(
        contract_key=f"query_collection:{binding.surface_key}",
        contract_kind="query_collection_schema",
        title=f"{binding.response_title} collection query schema",
        summary=(
          "Advertises typed collection expression schemas, element fields, and parameter domain metadata "
          f"for the `{binding.surface_key}` surface."
        ),
        source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
        related_family_keys=("collection_query",),
        member_keys=tuple(
          [
            f"collection:{'.'.join(spec.path_template or spec.path)}"
            for spec in binding.collection_path_specs
          ]
          + [
            f"parameter_domain:{domain['parameter_key']}"
            for domain in parameter_domains
          ]
        ),
        schema_detail={
          "surface_key": binding.surface_key,
          "route_path": binding.route_path,
          "expression_param": "filter_expr",
          "expression_authoring": serialize_collection_query_expression_authoring(),
          "collection_schemas": [
            serialize_collection_path_spec(binding, spec)
            for spec in binding.collection_path_specs
          ],
          "parameter_domains": parameter_domains,
        },
      )
    )
  return tuple(contracts)


def list_run_surface_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSurfaceSharedContract, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  return resolved_capabilities.shared_contracts


def serialize_run_surface_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> list[dict[str, Any]]:
  def normalize_schema_detail(value: Any) -> Any:
    if isinstance(value, tuple):
      return [
        normalize_schema_detail(item)
        for item in value
      ]
    if isinstance(value, list):
      return [
        normalize_schema_detail(item)
        for item in value
      ]
    if isinstance(value, dict):
      return {
        key: normalize_schema_detail(item)
        for key, item in value.items()
      }
    return value

  return [
    {
      **asdict(contract),
      "ui_surfaces": list(contract.ui_surfaces),
      "schema_sources": list(contract.schema_sources),
      "policy": (
        {
          **asdict(contract.policy),
          "applies_to": list(contract.policy.applies_to),
        }
        if contract.policy is not None
        else None
      ),
      "enforcement": (
        {
          **asdict(contract.enforcement),
          "enforcement_points": list(contract.enforcement.enforcement_points),
        }
        if contract.enforcement is not None
        else None
      ),
      "surface_rules": [
        asdict(rule)
        for rule in contract.surface_rules
      ],
      "related_family_keys": list(contract.related_family_keys),
      "member_keys": list(contract.member_keys),
      "schema_detail": normalize_schema_detail(contract.schema_detail),
    }
    for contract in (
      list_run_surface_shared_contracts(capabilities)
      + list_collection_query_shared_contracts(capabilities)
    )
  ]
