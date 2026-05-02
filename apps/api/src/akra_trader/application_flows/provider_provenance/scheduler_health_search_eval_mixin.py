from __future__ import annotations

import csv
from copy import deepcopy
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import io
import json
import math
import re
from typing import Any
from typing import Iterable
from typing import Mapping

from akra_trader.domain.models import *  # noqa: F403


def _serialize_stitched_scheduler_narrative_json_value(value: Any) -> str:
  if isinstance(value, datetime):
    return value.isoformat()
  raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


class ProviderProvenanceSchedulerHealthSearchEvalMixin:
  @classmethod
  def _parse_provider_provenance_scheduler_alert_search_query(
    cls,
    search: str | None,
  ) -> dict[str, Any]:
    if not isinstance(search, str) or not search.strip():
      return {
        "query": None,
        "terms": (),
        "phrases": (),
        "excluded_terms": (),
        "excluded_phrases": (),
        "operators": (),
        "semantic_concepts": (),
        "excluded_semantic_concepts": (),
        "boolean_operator_count": 0,
        "query_plan": (),
        "boolean_tokens": (),
        "boolean_rpn": (),
      }
    normalized_query = search.strip()
    raw_parts = tuple(
      token
      for token in re.findall(r'"[^"]+"|\'[^\']+\'|\(|\)|\bAND\b|\bOR\b|\bNOT\b|[^\s()]+', normalized_query, flags=re.IGNORECASE)
      if token.strip()
    )
    boolean_tokens: list[dict[str, Any]] = []

    def build_operand(raw_value: str) -> dict[str, Any] | None:
      quoted = (
        len(raw_value) >= 2
        and raw_value[0] == raw_value[-1]
        and raw_value[0] in {"\"", "'"}
      )
      body = raw_value[1:-1] if quoted else raw_value
      if ":" in body:
        raw_field, raw_operator_value = body.split(":", 1)
        normalized_field = cls._normalize_provider_provenance_scheduler_alert_search_operator_field(raw_field)
        normalized_value = (
          cls._normalize_provider_provenance_scheduler_alert_search_operator_value(
            field=normalized_field or "",
            value=raw_operator_value,
          )
          if normalized_field is not None
          else None
        )
        if normalized_field is not None and normalized_value is not None:
          return {
            "type": "operand",
            "operand_type": "operator",
            "field": normalized_field,
            "value": normalized_value,
            "label": f"{normalized_field}:{normalized_value}",
            "semantic_concept": (
              normalized_value if normalized_field == "concept" else None
            ),
          }
      normalized_body = cls._normalize_provider_provenance_scheduler_alert_search_text(body)
      if normalized_body is None:
        return None
      return {
        "type": "operand",
        "operand_type": "phrase" if quoted or " " in normalized_body else "term",
        "value": normalized_body,
        "label": normalized_body,
        "semantic_concept": cls._normalize_provider_provenance_scheduler_alert_search_semantic_concept(
          normalized_body
        ),
      }

    for raw_part in raw_parts:
      token = raw_part.strip()
      if token in {"(", ")"}:
        boolean_tokens.append({"type": "paren", "value": token})
        continue
      upper_token = token.upper()
      if upper_token in {"AND", "OR", "NOT"}:
        boolean_tokens.append({"type": "logical", "value": upper_token})
        continue
      negation_count = 0
      while len(token) > 1 and token[0] in {"-", "!"}:
        negation_count += 1
        token = token[1:]
      if token in {"!", "-"}:
        negation_count += 1
        token = ""
      for _ in range(negation_count):
        boolean_tokens.append({"type": "logical", "value": "NOT"})
      if not token:
        continue
      operand = build_operand(token)
      if operand is not None:
        boolean_tokens.append(operand)

    tokens_with_implicit_and: list[dict[str, Any]] = []
    previous_token: dict[str, Any] | None = None
    for token in boolean_tokens:
      current_starts_operand = token["type"] == "operand" or (
        token["type"] == "logical" and token["value"] == "NOT"
      ) or (token["type"] == "paren" and token["value"] == "(")
      previous_ends_operand = previous_token is not None and (
        previous_token["type"] == "operand"
        or (previous_token["type"] == "paren" and previous_token["value"] == ")")
      )
      if previous_ends_operand and current_starts_operand:
        tokens_with_implicit_and.append({"type": "logical", "value": "AND", "implicit": True})
      tokens_with_implicit_and.append(token)
      previous_token = token

    precedence = {"OR": 1, "AND": 2, "NOT": 3}
    logical_stack: list[dict[str, Any]] = []
    rpn_tokens: list[dict[str, Any]] = []
    for token in tokens_with_implicit_and:
      if token["type"] == "operand":
        rpn_tokens.append(token)
        continue
      if token["type"] == "paren" and token["value"] == "(":
        logical_stack.append(token)
        continue
      if token["type"] == "paren" and token["value"] == ")":
        while logical_stack and not (
          logical_stack[-1]["type"] == "paren" and logical_stack[-1]["value"] == "("
        ):
          rpn_tokens.append(logical_stack.pop())
        if logical_stack and logical_stack[-1]["type"] == "paren":
          logical_stack.pop()
        continue
      if token["type"] == "logical":
        current_precedence = precedence[token["value"]]
        right_associative = token["value"] == "NOT"
        while logical_stack:
          top = logical_stack[-1]
          if top["type"] != "logical":
            break
          top_precedence = precedence[top["value"]]
          if top_precedence > current_precedence or (
            top_precedence == current_precedence and not right_associative
          ):
            rpn_tokens.append(logical_stack.pop())
            continue
          break
        logical_stack.append(token)
    while logical_stack:
      token = logical_stack.pop()
      if token["type"] != "paren":
        rpn_tokens.append(token)

    terms: list[str] = []
    phrases: list[str] = []
    excluded_terms: list[str] = []
    excluded_phrases: list[str] = []
    operators: list[dict[str, Any]] = []
    excluded_semantic_concepts: list[str] = []
    semantic_concepts: list[str] = []
    query_plan: list[str] = []
    previous_was_not = False
    for token in tokens_with_implicit_and:
      if token["type"] == "operand":
        operand_type = token.get("operand_type")
        target_terms = excluded_terms if previous_was_not else terms
        target_phrases = excluded_phrases if previous_was_not else phrases
        if operand_type == "term":
          target_terms.append(token["value"])
        elif operand_type == "phrase":
          target_phrases.append(token["value"])
        elif operand_type == "operator":
          operators.append(
            {
              "field": token["field"],
              "value": token["value"],
              "negated": previous_was_not,
              "raw": f"{'-' if previous_was_not else ''}{token['label']}",
            }
          )
        semantic_concept = token.get("semantic_concept")
        if isinstance(semantic_concept, str):
          if previous_was_not:
            excluded_semantic_concepts.append(semantic_concept)
          else:
            semantic_concepts.append(semantic_concept)
        query_plan.append(token["label"])
        previous_was_not = False
        continue
      if token["type"] == "logical":
        query_plan.append(token["value"])
        previous_was_not = token["value"] == "NOT"
        continue
      if token["type"] == "paren":
        query_plan.append(token["value"])
        previous_was_not = False

    return {
      "query": normalized_query,
      "terms": tuple(dict.fromkeys(terms)),
      "phrases": tuple(dict.fromkeys(phrases)),
      "excluded_terms": tuple(dict.fromkeys(excluded_terms)),
      "excluded_phrases": tuple(dict.fromkeys(excluded_phrases)),
      "operators": tuple(operators),
      "semantic_concepts": tuple(dict.fromkeys(semantic_concepts)),
      "excluded_semantic_concepts": tuple(dict.fromkeys(excluded_semantic_concepts)),
      "boolean_operator_count": sum(
        1 for token in tokens_with_implicit_and if token["type"] == "logical"
      ),
      "query_plan": tuple(query_plan),
      "boolean_tokens": tuple(tokens_with_implicit_and),
      "boolean_rpn": tuple(rpn_tokens),
    }

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_semantic_concepts(
    cls,
    *,
    row: Mapping[str, Any],
  ) -> tuple[str, ...]:
    alert = row.get("alert")
    narrative = row.get("narrative")
    if not isinstance(alert, OperatorAlert):
      return ()
    status_sequence = tuple(narrative.get("status_sequence", ()) or ()) if isinstance(narrative, Mapping) else ()
    post_resolution_status_sequence = (
      tuple(narrative.get("post_resolution_status_sequence", ()) or ())
      if isinstance(narrative, Mapping)
      else ()
    )
    facet_flags = tuple(narrative.get("facet_flags", ()) or ()) if isinstance(narrative, Mapping) else ()
    concepts: list[str] = []
    if alert.category == "scheduler_lag":
      concepts.append("lag")
    if alert.category == "scheduler_failure":
      concepts.append("failure")
    if alert.status == "active":
      concepts.append("active")
    if alert.status == "resolved":
      concepts.append("resolved")
    if alert.primary_focus is not None:
      concepts.append("focus")
    if "healthy" in status_sequence or "healthy" in post_resolution_status_sequence:
      concepts.append("healthy")
    if isinstance(narrative, Mapping) and narrative.get("has_post_resolution_history"):
      concepts.extend(("recovery", "post_resolution"))
    if "recurring_occurrence" in facet_flags:
      concepts.append("recurring")
    if (
      ("lagging" in status_sequence or "failed" in status_sequence)
      and "healthy" in post_resolution_status_sequence
    ):
      concepts.append("recovery")
    return tuple(dict.fromkeys(concepts))

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_semantic_values(
    cls,
    *,
    row: Mapping[str, Any],
  ) -> tuple[str, ...]:
    values: list[str] = []
    for concept in cls._build_provider_provenance_scheduler_alert_occurrence_semantic_concepts(row=row):
      values.append(concept)
      values.extend(cls._provider_provenance_scheduler_alert_search_semantic_alias_groups().get(concept, ()))
    return tuple(dict.fromkeys(value for value in values if isinstance(value, str) and value.strip()))

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_search_fields(
    cls,
    *,
    row: Mapping[str, Any],
  ) -> tuple[tuple[str, int, tuple[str, ...]], ...]:
    alert = row.get("alert")
    narrative = row.get("narrative")
    if not isinstance(alert, OperatorAlert):
      return ()
    primary_focus = alert.primary_focus
    facet_flags = tuple(narrative.get("facet_flags", ()) or ()) if isinstance(narrative, Mapping) else ()
    status_sequence = tuple(narrative.get("status_sequence", ()) or ()) if isinstance(narrative, Mapping) else ()
    post_resolution_status_sequence = (
      tuple(narrative.get("post_resolution_status_sequence", ()) or ())
      if isinstance(narrative, Mapping)
      else ()
    )
    semantic_values = cls._build_provider_provenance_scheduler_alert_occurrence_semantic_values(row=row)
    return (
      (
        "occurrence_id",
        180,
        tuple(
          value
          for value in (alert.occurrence_id, alert.alert_id)
          if isinstance(value, str) and value.strip()
        ),
      ),
      (
        "summary",
        170,
        tuple(
          value
          for value in (alert.summary, alert.detail)
          if isinstance(value, str) and value.strip()
        ),
      ),
      (
        "market_context",
        150,
        tuple(
          value
          for value in (alert.symbol, alert.timeframe, *alert.symbols)
          if isinstance(value, str) and value.strip()
        ),
      ),
      (
        "primary_focus",
        145,
        tuple(
          value
          for value in (
            primary_focus.symbol if primary_focus is not None else None,
            primary_focus.timeframe if primary_focus is not None else None,
            primary_focus.policy if primary_focus is not None else None,
            primary_focus.reason if primary_focus is not None else None,
            *(primary_focus.candidate_symbols if primary_focus is not None else ()),
          )
          if isinstance(value, str) and value.strip()
        ),
      ),
      (
        "status_sequence",
        150,
        tuple(
          value
          for value in (
            *status_sequence,
            " -> ".join(status_sequence) if status_sequence else None,
            *post_resolution_status_sequence,
            " -> ".join(post_resolution_status_sequence) if post_resolution_status_sequence else None,
          )
          if isinstance(value, str) and value.strip()
        ),
      ),
      (
        "narrative",
        120,
        tuple(
          value
          for value in (
            narrative.get("facet") if isinstance(narrative, Mapping) else None,
            narrative.get("narrative_mode") if isinstance(narrative, Mapping) else None,
            *facet_flags,
            str(narrative.get("occurrence_record_count"))
            if isinstance(narrative, Mapping) and narrative.get("occurrence_record_count") is not None
            else None,
            str(narrative.get("post_resolution_record_count"))
            if isinstance(narrative, Mapping) and narrative.get("post_resolution_record_count") is not None
            else None,
          )
          if isinstance(value, str) and value.strip()
        ),
      ),
      (
        "semantic",
        135,
        semantic_values,
      ),
      (
        "classification",
        90,
        tuple(
          value
          for value in (
            alert.category,
            alert.severity,
            alert.status,
            alert.source,
            alert.run_id,
            alert.session_id,
            alert.timeline_key,
          )
          if isinstance(value, str) and value.strip()
        ),
      ),
      (
        "timeline",
        55,
        tuple(
          value
          for value in (
            str(alert.timeline_position) if alert.timeline_position is not None else None,
            str(alert.timeline_total) if alert.timeline_total is not None else None,
            alert.detected_at.isoformat(),
            alert.resolved_at.isoformat() if alert.resolved_at is not None else None,
          )
          if isinstance(value, str) and value.strip()
        ),
      ),
    )

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_operator_fields(
    cls,
    *,
    row: Mapping[str, Any],
  ) -> dict[str, tuple[str, ...]]:
    alert = row.get("alert")
    narrative = row.get("narrative")
    if not isinstance(alert, OperatorAlert):
      return {}
    primary_focus = alert.primary_focus
    facet_flags = tuple(narrative.get("facet_flags", ()) or ()) if isinstance(narrative, Mapping) else ()
    status_sequence = tuple(narrative.get("status_sequence", ()) or ()) if isinstance(narrative, Mapping) else ()
    post_resolution_status_sequence = (
      tuple(narrative.get("post_resolution_status_sequence", ()) or ())
      if isinstance(narrative, Mapping)
      else ()
    )
    has_flags: list[str] = []
    if isinstance(narrative, Mapping) and narrative.get("has_post_resolution_history"):
      has_flags.append("post_resolution")
    if "recurring_occurrence" in facet_flags:
      has_flags.append("recurring")
    if primary_focus is not None:
      has_flags.extend(("primary_focus", "focus"))
    if alert.status in {"active", "resolved"}:
      has_flags.append(alert.status)
    field_values = {
      "occurrence": (
        alert.occurrence_id,
        alert.alert_id,
      ),
      "category": (
        alert.category,
        "scheduler_lag" if alert.category == "scheduler_lag" else None,
        "scheduler_failure" if alert.category == "scheduler_failure" else None,
        "lag" if alert.category == "scheduler_lag" else None,
        "failure" if alert.category == "scheduler_failure" else None,
      ),
      "status": (alert.status,),
      "facet": (
        narrative.get("facet") if isinstance(narrative, Mapping) else None,
        *facet_flags,
        "resolved_narratives"
        if isinstance(narrative, Mapping) and narrative.get("can_reconstruct_narrative")
        else None,
        "post_resolution_recovery"
        if isinstance(narrative, Mapping) and narrative.get("has_post_resolution_history")
        else None,
        "recurring_occurrences" if "recurring_occurrence" in facet_flags else None,
        "all_occurrences",
      ),
      "mode": (narrative.get("narrative_mode") if isinstance(narrative, Mapping) else None,),
      "symbol": (
        alert.symbol,
        *alert.symbols,
        primary_focus.symbol if primary_focus is not None else None,
        *(primary_focus.candidate_symbols if primary_focus is not None else ()),
      ),
      "timeframe": (
        alert.timeframe,
        primary_focus.timeframe if primary_focus is not None else None,
      ),
      "severity": (alert.severity,),
      "source": (alert.source,),
      "focus": (
        primary_focus.symbol if primary_focus is not None else None,
        primary_focus.timeframe if primary_focus is not None else None,
        primary_focus.policy if primary_focus is not None else None,
        primary_focus.reason if primary_focus is not None else None,
        *(primary_focus.candidate_symbols if primary_focus is not None else ()),
      ),
      "sequence": (
        *status_sequence,
        " ".join(status_sequence) if status_sequence else None,
        " -> ".join(status_sequence) if status_sequence else None,
        *post_resolution_status_sequence,
        " ".join(post_resolution_status_sequence) if post_resolution_status_sequence else None,
        " -> ".join(post_resolution_status_sequence) if post_resolution_status_sequence else None,
      ),
      "concept": cls._build_provider_provenance_scheduler_alert_occurrence_semantic_concepts(row=row),
      "has": tuple(has_flags),
      "text": (alert.summary, alert.detail),
    }
    return {
      field: tuple(
        dict.fromkeys(
          normalized
          for raw_value in values
          for normalized in (
            cls._normalize_provider_provenance_scheduler_alert_search_operator_value(
              field=field,
              value=raw_value,
            ) if isinstance(raw_value, str) and raw_value.strip() else None,
          )
          if normalized is not None
        )
      )
      for field, values in field_values.items()
    }

  @classmethod
  def _match_provider_provenance_scheduler_alert_occurrence_operator(
    cls,
    *,
    row: Mapping[str, Any],
    operator: Mapping[str, Any],
  ) -> tuple[str, ...]:
    field = operator.get("field")
    value = operator.get("value")
    if not isinstance(field, str) or not isinstance(value, str):
      return ()
    candidates = cls._build_provider_provenance_scheduler_alert_occurrence_operator_fields(
      row=row
    ).get(field, ())
    if field in {"category", "status", "facet", "mode", "severity", "concept", "has", "timeframe"}:
      return tuple(candidate for candidate in candidates if candidate == value)
    return tuple(candidate for candidate in candidates if value in candidate)

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_search_document(
    cls,
    *,
    row: Mapping[str, Any],
    document_id: int,
    search_projection_lookup: Mapping[str, Mapping[str, Any]] | None = None,
  ) -> dict[str, Any]:
    search_fields = cls._build_provider_provenance_scheduler_alert_occurrence_search_fields(row=row)
    normalized_fields: dict[str, tuple[str, ...]] = {}
    lexical_terms: list[str] = []
    lexical_term_frequencies: dict[str, int] = {}
    for field_name, _, field_values in search_fields:
      normalized_values = tuple(
        dict.fromkeys(
          normalized_value
          for raw_value in field_values
          for normalized_value in (
            cls._normalize_provider_provenance_scheduler_alert_search_text(raw_value),
          )
          if normalized_value is not None
        )
      )
      normalized_fields[field_name] = normalized_values
      for normalized_value in normalized_values:
        for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(normalized_value):
          lexical_terms.append(token)
          lexical_term_frequencies[token] = lexical_term_frequencies.get(token, 0) + 1
    persisted_projection_versions: list[str] = []
    persisted_projection_count = 0
    persisted_projection_terms: list[str] = []
    persisted_projection_semantic_concepts: list[str] = []
    persisted_projection_fields: dict[str, list[str]] = {}
    projection_source = "ephemeral_occurrence_projection"
    for record in row.get("narrative_records", ()) or ():
      if not isinstance(record, ProviderProvenanceSchedulerHealthRecord):
        continue
      projection = (
        search_projection_lookup.get(record.record_id, {})
        if isinstance(search_projection_lookup, Mapping)
        else {}
      )
      if not projection:
        projection = record.search_projection if isinstance(record.search_projection, dict) else {}
      if not projection:
        continue
      persisted_projection_count += 1
      projection_source = (
        projection.get("projection_source")
        if isinstance(projection.get("projection_source"), str)
        and projection.get("projection_source").strip()
        else "record_backed_scheduler_search_projection"
      )
      projection_version = projection.get("index_version")
      if isinstance(projection_version, str) and projection_version.strip():
        persisted_projection_versions.append(projection_version.strip())
      for token in projection.get("lexical_terms", ()) or ():
        if isinstance(token, str) and token.strip():
          normalized_token = token.strip().lower()
          persisted_projection_terms.append(normalized_token)
          lexical_terms.append(normalized_token)
          lexical_term_frequencies[normalized_token] = lexical_term_frequencies.get(normalized_token, 0) + 1
      for concept in projection.get("semantic_concepts", ()) or ():
        if isinstance(concept, str) and concept.strip():
          persisted_projection_semantic_concepts.append(concept.strip())
      for field_name, values in (projection.get("fields", {}) or {}).items():
        if not isinstance(field_name, str):
          continue
        bucket = persisted_projection_fields.setdefault(field_name, [])
        if isinstance(values, (list, tuple)):
          for value in values:
            normalized_value = cls._normalize_provider_provenance_scheduler_alert_search_text(value)
            if normalized_value is not None:
              bucket.append(normalized_value)
    return {
      "document_id": document_id,
      "row": row,
      "normalized_fields": {
        **normalized_fields,
        **{
          f"persisted_{field_name}": tuple(dict.fromkeys(values))
          for field_name, values in persisted_projection_fields.items()
          if values
        },
      },
      "lexical_terms": tuple(dict.fromkeys(lexical_terms)),
      "lexical_term_frequencies": lexical_term_frequencies,
      "operator_fields": cls._build_provider_provenance_scheduler_alert_occurrence_operator_fields(
        row=row
      ),
      "semantic_concepts": tuple(
        dict.fromkeys(
          (
            *cls._build_provider_provenance_scheduler_alert_occurrence_semantic_concepts(row=row),
            *persisted_projection_semantic_concepts,
          )
        )
      ),
      "persistence_mode": (
        projection_source
        if persisted_projection_count > 0
        else "ephemeral_occurrence_projection"
      ),
      "persisted_projection_count": persisted_projection_count,
      "persisted_projection_versions": tuple(dict.fromkeys(persisted_projection_versions)),
      "persisted_projection_terms": tuple(dict.fromkeys(persisted_projection_terms)),
    }

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_search_index(
    cls,
    *,
    rows: tuple[Mapping[str, Any], ...],
    search_projection_lookup: Mapping[str, Mapping[str, Any]] | None = None,
  ) -> dict[str, Any]:
    documents = tuple(
      cls._build_provider_provenance_scheduler_alert_occurrence_search_document(
        row=row,
        document_id=index,
        search_projection_lookup=search_projection_lookup,
      )
      for index, row in enumerate(rows)
    )
    lexical_postings: dict[str, set[int]] = {}
    semantic_postings: dict[str, set[int]] = {}
    for document in documents:
      document_id = document["document_id"]
      for term in document["lexical_terms"]:
        lexical_postings.setdefault(term, set()).add(document_id)
      for concept in document["semantic_concepts"]:
        semantic_postings.setdefault(concept, set()).add(document_id)
    document_lengths = tuple(
      sum(document.get("lexical_term_frequencies", {}).values())
      for document in documents
    )
    average_document_length = (
      sum(document_lengths) / len(document_lengths)
      if document_lengths
      else 0.0
    )
    return {
      "documents": documents,
      "all_document_ids": frozenset(document["document_id"] for document in documents),
      "lexical_postings": {term: frozenset(postings) for term, postings in lexical_postings.items()},
      "semantic_postings": {term: frozenset(postings) for term, postings in semantic_postings.items()},
      "indexed_term_count": len(lexical_postings),
      "document_count": len(documents),
      "average_document_length": average_document_length,
    }

  @classmethod
  def _match_provider_provenance_scheduler_alert_occurrence_operator_document(
    cls,
    *,
    document: Mapping[str, Any],
    operator: Mapping[str, Any],
  ) -> tuple[str, ...]:
    field = operator.get("field")
    value = operator.get("value")
    if not isinstance(field, str) or not isinstance(value, str):
      return ()
    candidates = document.get("operator_fields", {}).get(field, ())
    if field in {"category", "status", "facet", "mode", "severity", "concept", "has", "timeframe"}:
      return tuple(candidate for candidate in candidates if candidate == value)
    return tuple(candidate for candidate in candidates if value in candidate)

  @classmethod
  def _evaluate_provider_provenance_scheduler_alert_search_operand(
    cls,
    *,
    index: Mapping[str, Any],
    operand: Mapping[str, Any],
  ) -> frozenset[int]:
    operand_type = operand.get("operand_type")
    if operand_type == "operator":
      return frozenset(
        document["document_id"]
        for document in index.get("documents", ())
        if cls._match_provider_provenance_scheduler_alert_occurrence_operator_document(
          document=document,
          operator=operand,
        )
      )
    if operand_type == "term":
      lexical_matches = set(index.get("lexical_postings", {}).get(operand.get("value"), ()))
      semantic_concept = operand.get("semantic_concept")
      if isinstance(semantic_concept, str):
        lexical_matches.update(index.get("semantic_postings", {}).get(semantic_concept, ()))
      return frozenset(lexical_matches)
    if operand_type == "phrase":
      phrase_value = operand.get("value")
      if not isinstance(phrase_value, str):
        return frozenset()
      matched_document_ids: set[int] = set()
      for document in index.get("documents", ()):
        if any(
          phrase_value in normalized_value
          for normalized_values in document.get("normalized_fields", {}).values()
          for normalized_value in normalized_values
        ):
          matched_document_ids.add(document["document_id"])
      return frozenset(matched_document_ids)
    return frozenset()

  @classmethod
  def _evaluate_provider_provenance_scheduler_alert_search_query(
    cls,
    *,
    index: Mapping[str, Any],
    parsed_query: Mapping[str, Any],
  ) -> frozenset[int]:
    rpn_tokens = tuple(parsed_query.get("boolean_rpn", ()))
    if not rpn_tokens:
      return frozenset(index.get("all_document_ids", ()))
    stack: list[frozenset[int]] = []
    all_document_ids = frozenset(index.get("all_document_ids", ()))
    for token in rpn_tokens:
      if token.get("type") == "operand":
        stack.append(
          cls._evaluate_provider_provenance_scheduler_alert_search_operand(
            index=index,
            operand=token,
          )
        )
        continue
      if token.get("type") != "logical":
        continue
      operator_value = token.get("value")
      if operator_value == "NOT":
        operand = stack.pop() if stack else frozenset()
        stack.append(all_document_ids.difference(operand))
        continue
      right = stack.pop() if stack else frozenset()
      left = stack.pop() if stack else frozenset()
      if operator_value == "AND":
        stack.append(left.intersection(right))
      elif operator_value == "OR":
        stack.append(left.union(right))
    return stack[-1] if stack else frozenset()
