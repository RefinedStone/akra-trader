from __future__ import annotations

import json
import logging
from datetime import UTC
from datetime import datetime
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorAlertPrimaryFocus
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


LOGGER = logging.getLogger("akra_trader.operator_delivery")


class OperatorDeliveryResponseMappingHelpersMixin:
  @staticmethod
  def _read_json_response(response: object) -> dict[str, Any]:
    if not hasattr(response, "read"):
      return {}
    raw = response.read()
    if isinstance(raw, bytes):
      body = raw.decode("utf-8")
    elif isinstance(raw, str):
      body = raw
    else:
      body = ""
    if not body:
      return {}
    parsed = json.loads(body)
    return parsed if isinstance(parsed, dict) else {}
  @staticmethod
  def _extract_mapping(*candidates: Any) -> dict[str, Any]:
    for candidate in candidates:
      if isinstance(candidate, dict):
        return candidate
    return {}
  @staticmethod
  def _extract_string_list(*candidates: Any) -> list[str]:
    for candidate in candidates:
      if isinstance(candidate, str):
        value = candidate.strip()
        if value:
          return [value]
      elif isinstance(candidate, (list, tuple)):
        values = [
          str(item).strip()
          for item in candidate
          if isinstance(item, str) and item.strip()
        ]
        if values:
          return values
    return []
  @staticmethod
  def _first_non_empty_string(*candidates: Any) -> str | None:
    for candidate in candidates:
      if isinstance(candidate, str):
        value = candidate.strip()
        if value:
          return value
    return None
  @staticmethod
  def _parse_provider_datetime(*candidates: Any) -> datetime | None:
    for candidate in candidates:
      if isinstance(candidate, datetime):
        return candidate.astimezone(UTC) if candidate.tzinfo is not None else candidate.replace(tzinfo=UTC)
      if not isinstance(candidate, str):
        continue
      value = candidate.strip()
      if not value:
        continue
      normalized = value.replace("Z", "+00:00")
      try:
        parsed = datetime.fromisoformat(normalized)
      except ValueError:
        continue
      return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    return None
  @classmethod
  def _extract_workflow_market_context_payload(
    cls,
    payload: dict[str, Any] | None,
  ) -> dict[str, Any] | None:
    if not payload:
      return None
    payload_mapping = cls._extract_mapping(payload)
    market_context = cls._extract_market_context_mapping_from_sources(payload_mapping)
    if not market_context:
      return None
    primary_focus = cls._build_primary_focus_payload_from_sources(
      market_context.get("primary_focus")
    )
    symbols = cls._normalize_market_context_symbols(
      market_context.get("symbols"),
      market_context.get("symbol"),
      primary_focus.get("candidate_symbols") if primary_focus is not None else (),
      primary_focus.get("symbol") if primary_focus is not None else None,
    )
    symbol = cls._normalize_market_context_symbol(
      cls._first_non_empty_string(
        market_context.get("symbol"),
        primary_focus.get("symbol") if primary_focus is not None else None,
      )
    )
    if symbol is None and len(symbols) == 1:
      symbol = symbols[0]
    timeframe = cls._normalize_market_context_timeframe(
      cls._first_non_empty_string(
        market_context.get("timeframe"),
        primary_focus.get("timeframe") if primary_focus is not None else None,
      )
    )
    if primary_focus is None and (symbol is not None or timeframe is not None or symbols):
      primary_focus = cls._build_primary_focus_payload_from_sources(
        {
          "symbol": symbol,
          "timeframe": timeframe,
          "candidate_symbols": symbols,
        }
      )
    if symbol is None and timeframe is None and not symbols and primary_focus is None:
      return None
    return {
      "symbol": symbol,
      "symbols": symbols,
      "timeframe": timeframe,
      "primary_focus": primary_focus,
    }
  @staticmethod
  def _resolve_workflow_market_context_vendor_field(provider: str) -> str:
    normalized = provider.strip().lower().replace(" ", "_")
    if normalized == "pagerduty":
      return "custom_details"
    if normalized in {"opsgenie", "firehydrant"}:
      return "details"
    return "metadata"
  @classmethod
  def _merge_workflow_market_context_vendor_fields(
    cls,
    *,
    provider: str,
    body: dict[str, Any],
    payload: dict[str, Any] | None,
  ) -> dict[str, Any]:
    market_context = cls._extract_workflow_market_context_payload(payload)
    if market_context is None:
      return body
    vendor_field = cls._resolve_workflow_market_context_vendor_field(provider)
    merged = dict(body)
    existing_vendor_payload = dict(cls._extract_mapping(merged.get(vendor_field)))
    existing_vendor_payload["market_context"] = market_context
    merged[vendor_field] = existing_vendor_payload
    return merged
  @classmethod
  def _project_workflow_market_context_into_request(
    cls,
    *,
    provider: str,
    request: urllib_request.Request,
    payload: dict[str, Any] | None,
  ) -> urllib_request.Request:
    raw_body = getattr(request, "data", None)
    if raw_body is None:
      return request
    if isinstance(raw_body, bytes):
      body_text = raw_body.decode("utf-8")
    elif isinstance(raw_body, str):
      body_text = raw_body
    else:
      return request
    if not body_text:
      return request
    try:
      parsed_body = json.loads(body_text)
    except (TypeError, ValueError, json.JSONDecodeError):
      return request
    if not isinstance(parsed_body, dict):
      return request
    updated_body = cls._merge_workflow_market_context_vendor_fields(
      provider=provider,
      body=parsed_body,
      payload=payload,
    )
    if updated_body == parsed_body:
      return request
    request.data = json.dumps(updated_body).encode("utf-8")
    return request
  @classmethod
  def _format_workflow_payload_context(cls, payload: dict[str, Any] | None) -> str:
    if not payload:
      return ""
    payload_mapping = dict(cls._extract_mapping(payload))
    market_context = cls._extract_workflow_market_context_payload(payload_mapping)
    if "market_context" in payload_mapping:
      payload_mapping.pop("market_context")
    fragments: list[str] = []
    if market_context is not None:
      fragments.append(
        f" Market context: {json.dumps(market_context, default=str, sort_keys=True)}"
      )
    if payload_mapping:
      fragments.append(
        f" Context: {json.dumps(payload_mapping, default=str, sort_keys=True)}"
      )
    return "".join(fragments)
