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


class ProviderProvenanceSchedulerHealthMixin:
  def _provider_provenance_scheduler_warning_lag_seconds(self) -> int:
    return max(self._provider_provenance_report_scheduler_interval_seconds * 2, 120)

  def _provider_provenance_scheduler_critical_lag_seconds(self) -> int:
    return max(self._provider_provenance_report_scheduler_interval_seconds * 5, 300)

  def _provider_provenance_scheduler_stale_cycle_seconds(self) -> int:
    return max(self._provider_provenance_report_scheduler_interval_seconds * 3, 180)

  def _summarize_provider_provenance_scheduler_due_reports(
    self,
    *,
    reference_time: datetime,
  ) -> tuple[int, datetime | None, int]:
    due_records = [
      record
      for record in self._list_provider_provenance_scheduled_report_records()
      if record.status == "scheduled"
      and record.next_run_at is not None
      and record.next_run_at <= reference_time
    ]
    if not due_records:
      return 0, None, 0
    oldest_due_at = min(record.next_run_at for record in due_records if record.next_run_at is not None)
    max_due_lag_seconds = max(int((reference_time - oldest_due_at).total_seconds()), 0)
    return len(due_records), oldest_due_at, max_due_lag_seconds

  def get_provider_provenance_scheduler_health(self) -> ProviderProvenanceSchedulerHealth:
    current_time = self._clock()
    with self._provider_provenance_scheduler_health_lock:
      snapshot = self._provider_provenance_scheduler_health
    due_report_count, oldest_due_at, max_due_lag_seconds = (
      self._summarize_provider_provenance_scheduler_due_reports(reference_time=current_time)
    )
    issues: list[str] = []
    status = snapshot.status
    summary = snapshot.summary

    if not snapshot.enabled:
      status = "disabled"
      summary = "Background scheduler is disabled for provider provenance automation."
    else:
      last_cycle_reference = snapshot.last_cycle_finished_at or snapshot.last_cycle_started_at
      latest_failure_is_current = (
        snapshot.last_failure_at is not None
        and (
          snapshot.last_success_at is None
          or snapshot.last_failure_at >= snapshot.last_success_at
        )
      )
      if latest_failure_is_current:
        status = "failed"
        summary = "Background scheduler failed while executing due provider provenance reports."
        if snapshot.last_error:
          issues.append(f"Last scheduler error: {snapshot.last_error}")
      elif last_cycle_reference is None:
        status = "starting"
        summary = "Background scheduler has not completed a provider provenance automation cycle yet."
        issues.append("No scheduler cycle has completed yet.")
      else:
        cycle_age_seconds = max(int((current_time - last_cycle_reference).total_seconds()), 0)
        if cycle_age_seconds > self._provider_provenance_scheduler_stale_cycle_seconds():
          status = "failed"
          summary = "Background scheduler has stopped cycling for provider provenance automation."
          issues.append(
            f"Last completed scheduler cycle was {cycle_age_seconds}s ago, beyond the {self._provider_provenance_scheduler_stale_cycle_seconds()}s stale threshold."
          )
        elif (
          due_report_count > 0
          and max_due_lag_seconds >= self._provider_provenance_scheduler_warning_lag_seconds()
        ):
          status = "lagging"
          summary = "Background scheduler is lagging on due provider provenance reports."
          issues.append(
            f"{due_report_count} due report(s) remain; oldest due lag is {max_due_lag_seconds}s."
          )
        else:
          status = "healthy"
          summary = "Background scheduler is healthy for provider provenance automation."

    return replace(
      snapshot,
      generated_at=current_time,
      status=status,
      summary=summary,
      due_report_count=due_report_count,
      oldest_due_at=oldest_due_at,
      max_due_lag_seconds=max_due_lag_seconds,
      issues=tuple(issues),
    )

  @staticmethod
  def _normalize_provider_provenance_scheduler_health_status(
    status: str | None,
  ) -> str | None:
    if not isinstance(status, str):
      return None
    normalized = status.strip().lower()
    if normalized in {"healthy", "lagging", "failed", "disabled", "starting"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_alert_history_status(
    status: str | None,
  ) -> str | None:
    if not isinstance(status, str):
      return None
    normalized = status.strip().lower()
    if normalized in {"active", "resolved"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_alert_history_category(
    category: str | None,
  ) -> str | None:
    if not isinstance(category, str):
      return None
    normalized = category.strip().lower()
    if normalized in {"scheduler_lag", "scheduler_failure"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_alert_history_narrative_facet(
    narrative_facet: str | None,
  ) -> str | None:
    if not isinstance(narrative_facet, str):
      return None
    normalized = narrative_facet.strip().lower()
    if normalized in {
      "all_occurrences",
      "resolved_narratives",
      "post_resolution_recovery",
      "recurring_occurrences",
    }:
      return normalized
    return None

  @classmethod
  def _build_provider_provenance_scheduler_health_search_projection(
    cls,
    *,
    snapshot: ProviderProvenanceSchedulerHealth,
  ) -> dict[str, Any]:
    normalized_summary = cls._normalize_provider_provenance_scheduler_alert_search_text(snapshot.summary)
    normalized_error = cls._normalize_provider_provenance_scheduler_alert_search_text(snapshot.last_error)
    normalized_issues = tuple(
      normalized_issue
      for issue in snapshot.issues
      for normalized_issue in (
        cls._normalize_provider_provenance_scheduler_alert_search_text(issue.replace("_", " ")),
      )
      if normalized_issue is not None
    )
    semantic_concepts: list[str] = []
    if snapshot.status == "lagging":
      semantic_concepts.append("lag")
    if snapshot.status == "failed":
      semantic_concepts.append("failure")
    if snapshot.status == "healthy":
      semantic_concepts.append("healthy")
    if snapshot.status == "starting":
      semantic_concepts.append("active")
    if snapshot.last_success_at is not None:
      semantic_concepts.append("recovery")
    if snapshot.active_alert_key:
      semantic_concepts.append("focus")
    if snapshot.consecutive_failure_count > 1 or snapshot.failure_count > 1:
      semantic_concepts.append("recurring")
    lexical_terms: list[str] = []
    field_map = {
      "status": (snapshot.status,),
      "summary": tuple(value for value in (normalized_summary, normalized_error) if value is not None),
      "issues": normalized_issues,
      "workflow": tuple(
        value
        for value in (
          snapshot.active_alert_key,
          snapshot.alert_workflow_state,
          snapshot.alert_workflow_summary,
        )
        for normalized_value in (
          cls._normalize_provider_provenance_scheduler_alert_search_text(value),
        )
        if normalized_value is not None
      ),
    }
    for values in field_map.values():
      for value in values:
        lexical_terms.extend(cls._tokenize_provider_provenance_scheduler_alert_search_query(value))
    return {
      "index_version": "scheduler-search-store.v1",
      "lexical_terms": tuple(dict.fromkeys(lexical_terms)),
      "semantic_concepts": tuple(dict.fromkeys(semantic_concepts)),
      "fields": {
        key: tuple(dict.fromkeys(values))
        for key, values in field_map.items()
        if values
      },
    }

  def _build_provider_provenance_scheduler_search_projection_lookup(
    self,
    *,
    record_ids: Iterable[str],
  ) -> dict[str, dict[str, Any]]:
    normalized_record_ids = {
      record_id
      for record_id in record_ids
      if isinstance(record_id, str) and record_id.strip()
    }
    if not normalized_record_ids:
      return {}
    self._prune_provider_provenance_scheduler_search_document_records()
    projection_source = self._provider_provenance_scheduler_search_persistence_mode()
    lookup: dict[str, dict[str, Any]] = {}
    for record in self._list_provider_provenance_scheduler_search_document_records():
      if record.record_id not in normalized_record_ids:
        continue
      lookup[record.record_id] = {
        "index_version": record.index_version,
        "lexical_terms": tuple(record.lexical_terms),
        "semantic_concepts": tuple(record.semantic_concepts),
        "fields": {
          key: tuple(values)
          for key, values in record.fields.items()
        },
        "projection_source": projection_source,
      }
    return lookup


  @classmethod
  def _matches_provider_provenance_scheduler_alert_occurrence_search(
    cls,
    *,
    row: Mapping[str, Any],
    search: str | None,
  ) -> bool:
    if not isinstance(search, str) or not search.strip():
      return True
    return cls._build_provider_provenance_scheduler_alert_occurrence_search_match(
      row=row,
      search=search,
    ) is not None

  @staticmethod
  def _normalize_provider_provenance_scheduler_alert_search_text(
    value: str | None,
  ) -> str | None:
    if not isinstance(value, str):
      return None
    normalized = " ".join(value.strip().lower().split())
    return normalized or None

  @staticmethod
  def _truncate_provider_provenance_scheduler_search_highlight(
    value: str,
    *,
    max_length: int = 72,
  ) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
      return normalized
    return f"{normalized[:max_length - 1].rstrip()}…"

  @staticmethod
  def _canonicalize_provider_provenance_scheduler_alert_search_keyword(
    value: str | None,
  ) -> str | None:
    if not isinstance(value, str):
      return None
    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or None

  @staticmethod
  def _provider_provenance_scheduler_alert_search_semantic_alias_groups(
  ) -> dict[str, tuple[str, ...]]:
    return {
      "lag": ("lag", "lagging", "delayed", "late", "overdue", "behind", "backlog", "stale"),
      "failure": (
        "failure",
        "failed",
        "error",
        "errors",
        "fault",
        "faulted",
        "broken",
        "crash",
        "crashed",
        "unhealthy",
      ),
      "recovery": (
        "recovery",
        "recover",
        "recovered",
        "restored",
        "stabilized",
        "stabilised",
        "healed",
        "caught_up",
      ),
      "post_resolution": (
        "post_resolution",
        "post-resolution",
        "after_resolution",
        "after-resolution",
        "recovery_window",
      ),
      "recurring": ("recurring", "recurred", "repeat", "repeated", "again", "flapping"),
      "active": ("active", "open", "ongoing", "current"),
      "resolved": ("resolved", "closed", "ended", "cleared"),
      "healthy": ("healthy", "stable", "nominal"),
      "focus": ("focus", "focused", "primary_focus", "primary-focus", "targeted"),
    }

  @classmethod
  def _normalize_provider_provenance_scheduler_alert_search_semantic_concept(
    cls,
    value: str | None,
  ) -> str | None:
    normalized = cls._canonicalize_provider_provenance_scheduler_alert_search_keyword(value)
    if normalized is None:
      return None
    lookup: dict[str, str] = {}
    for concept, aliases in cls._provider_provenance_scheduler_alert_search_semantic_alias_groups().items():
      lookup[cls._canonicalize_provider_provenance_scheduler_alert_search_keyword(concept) or concept] = concept
      for alias in aliases:
        canonical_alias = cls._canonicalize_provider_provenance_scheduler_alert_search_keyword(alias)
        if canonical_alias is not None:
          lookup[canonical_alias] = concept
    return lookup.get(normalized)

  @classmethod
  def _tokenize_provider_provenance_scheduler_alert_search_query(
    cls,
    search: str,
  ) -> tuple[str, ...]:
    tokens = tuple(
      dict.fromkeys(
        fragment
        for token in re.findall(r"[a-z0-9:_./-]+", search.lower())
        for fragment in (
          cls._normalize_provider_provenance_scheduler_alert_search_text(token),
        )
        if fragment is not None
      )
    )
    return tokens or ((search.strip().lower(),) if search.strip() else ())

  @classmethod
  def _normalize_provider_provenance_scheduler_alert_search_operator_field(
    cls,
    value: str | None,
  ) -> str | None:
    normalized = cls._canonicalize_provider_provenance_scheduler_alert_search_keyword(value)
    if normalized is None:
      return None
    aliases = {
      "category": "category",
      "cat": "category",
      "status": "status",
      "facet": "facet",
      "mode": "mode",
      "symbol": "symbol",
      "sym": "symbol",
      "timeframe": "timeframe",
      "tf": "timeframe",
      "severity": "severity",
      "source": "source",
      "focus": "focus",
      "sequence": "sequence",
      "seq": "sequence",
      "concept": "concept",
      "semantic": "concept",
      "has": "has",
      "occurrence": "occurrence",
      "id": "occurrence",
      "text": "text",
      "summary": "text",
    }
    return aliases.get(normalized)

  @classmethod
  def _normalize_provider_provenance_scheduler_alert_search_operator_value(
    cls,
    *,
    field: str,
    value: str,
  ) -> str | None:
    normalized_text = cls._normalize_provider_provenance_scheduler_alert_search_text(value)
    if normalized_text is None:
      return None
    normalized_keyword = cls._canonicalize_provider_provenance_scheduler_alert_search_keyword(value)
    if field == "category":
      if normalized_keyword in {"lag", "lagging", "scheduler_lag"}:
        return "scheduler_lag"
      if normalized_keyword in {"failure", "failed", "error", "errors", "scheduler_failure"}:
        return "scheduler_failure"
      return normalized_text
    if field == "status":
      if normalized_keyword in {"active", "open", "ongoing", "current"}:
        return "active"
      if normalized_keyword in {"resolved", "closed", "ended"}:
        return "resolved"
      return normalized_text
    if field == "facet":
      if normalized_keyword in {"resolved", "resolved_narrative", "resolved_narratives"}:
        return "resolved_narratives"
      if normalized_keyword in {
        "post_resolution",
        "post_resolution_recovery",
        "post_resolution_history",
        "recovery",
      }:
        return "post_resolution_recovery"
      if normalized_keyword in {"recurring", "recurring_occurrence", "recurring_occurrences"}:
        return "recurring_occurrences"
      if normalized_keyword in {"all", "all_occurrences"}:
        return "all_occurrences"
      return normalized_text
    if field == "concept":
      return cls._normalize_provider_provenance_scheduler_alert_search_semantic_concept(value)
    if field == "has":
      if normalized_keyword in {"post_resolution", "recovery", "post_resolution_recovery"}:
        return "post_resolution"
      if normalized_keyword in {"recurring", "recurring_occurrence"}:
        return "recurring"
      if normalized_keyword in {"primary_focus", "focus"}:
        return "primary_focus"
      if normalized_keyword in {"active", "resolved"}:
        return normalized_keyword
      return normalized_text
    return normalized_text

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

  @classmethod
  def _score_provider_provenance_scheduler_alert_occurrence_search_match(
    cls,
    *,
    row: Mapping[str, Any],
    parsed_query: Mapping[str, Any],
    index: Mapping[str, Any] | None = None,
    document: Mapping[str, Any] | None = None,
    tuning_profile: Mapping[str, Any] | None = None,
  ) -> dict[str, Any] | None:
    terms = parsed_query["terms"]
    phrases = parsed_query["phrases"]
    operators = parsed_query["operators"]
    semantic_query_concepts = parsed_query["semantic_concepts"]
    if not any((terms, phrases, operators, semantic_query_concepts)):
      return None
    search_fields = cls._build_provider_provenance_scheduler_alert_occurrence_search_fields(row=row)
    row_semantic_concepts = cls._build_provider_provenance_scheduler_alert_occurrence_semantic_concepts(row=row)
    matched_terms: set[str] = set()
    matched_phrases: set[str] = set()
    matched_fields: list[str] = []
    highlights: list[str] = []
    lexical_score = 0
    operator_score = 0
    semantic_score = 0
    phrase_match = False
    exact_match = False
    field_hits = 0
    operator_hits: list[str] = []
    tuning_signals: list[str] = []
    learned_score = 0
    total_documents = int(index.get("document_count", 0)) if isinstance(index, Mapping) else 0
    average_document_length = (
      float(index.get("average_document_length", 0.0))
      if isinstance(index, Mapping)
      else 0.0
    )
    document_term_frequencies = (
      document.get("lexical_term_frequencies", {})
      if isinstance(document, Mapping)
      else {}
    )
    document_length = (
      sum(document_term_frequencies.values())
      if isinstance(document_term_frequencies, dict)
      else 0
    )
    for operator in operators:
      if operator.get("negated"):
        continue
      matched_candidates = cls._match_provider_provenance_scheduler_alert_occurrence_operator(
        row=row,
        operator=operator,
      )
      if not matched_candidates:
        continue
      operator_label = f"{operator['field']}:{operator['value']}"
      operator_hits.append(operator_label)
      operator_score += 160 + (15 * min(len(matched_candidates), 2))
      if len(highlights) < 3:
        highlights.append(
          f"operator {operator_label}: "
          f"{cls._truncate_provider_provenance_scheduler_search_highlight(matched_candidates[0])}"
        )
    for field_name, field_weight, field_values in search_fields:
      best_field_score = 0
      best_field_highlight: str | None = None
      field_matched_terms: set[str] = set()
      field_matched_phrases: set[str] = set()
      field_phrase_match = False
      field_exact_match = False
      for raw_value in field_values:
        normalized_value = cls._normalize_provider_provenance_scheduler_alert_search_text(raw_value)
        if normalized_value is None:
          continue
        value_score = 0
        for phrase in phrases:
          if phrase == normalized_value:
            value_score += field_weight * 4
            field_matched_phrases.add(phrase)
            field_phrase_match = True
            field_exact_match = True
          elif phrase in normalized_value:
            value_score += field_weight * 3
            field_matched_phrases.add(phrase)
            field_phrase_match = True
        for token in terms:
          document_frequency = (
            len(index.get("lexical_postings", {}).get(token, ()))
            if isinstance(index, Mapping)
            else 0
          )
          token_frequency = (
            int(document_term_frequencies.get(token, 0))
            if isinstance(document_term_frequencies, dict)
            else 0
          )
          inverse_document_frequency = (
            1.0 + ((total_documents + 1) / (document_frequency + 1))
            if total_documents > 0
            else 1.0
          )
          tf_bonus = (
            1.0 + min(token_frequency, 4) * 0.15
            if token_frequency > 0
            else 1.0
          )
          length_normalizer = (
            1.0
            if average_document_length <= 0
            else 1.0
            + min(document_length / average_document_length, 3.0) * 0.05
          )
          if token == normalized_value:
            value_score += int(round(field_weight * 3 * inverse_document_frequency * tf_bonus * length_normalizer))
            field_matched_terms.add(token)
            field_exact_match = True
          elif normalized_value.startswith(token):
            value_score += int(round(field_weight * 2 * inverse_document_frequency * tf_bonus))
            field_matched_terms.add(token)
          elif token in normalized_value:
            value_score += int(round(field_weight * inverse_document_frequency * tf_bonus))
            field_matched_terms.add(token)
        if value_score > best_field_score:
          best_field_score = value_score
          best_field_highlight = (
            f"{field_name}: {cls._truncate_provider_provenance_scheduler_search_highlight(raw_value)}"
          )
      if best_field_score <= 0:
        continue
      field_hits += 1
      matched_terms.update(field_matched_terms)
      matched_phrases.update(field_matched_phrases)
      matched_fields.append(field_name)
      if best_field_highlight is not None and best_field_highlight not in highlights:
        highlights.append(best_field_highlight)
      if field_phrase_match:
        phrase_match = True
      if field_exact_match:
        exact_match = True
      lexical_score += best_field_score
    semantic_hits = tuple(
      concept for concept in semantic_query_concepts if concept in row_semantic_concepts
    )
    if semantic_hits:
      semantic_score += 110 * len(semantic_hits)
      if len(highlights) < 3:
        highlights.append(f"semantic: {', '.join(semantic_hits)}")
    if isinstance(tuning_profile, Mapping) and tuning_profile.get("active"):
      field_adjustments = tuning_profile.get("field_adjustments", {}) or {}
      semantic_adjustments = tuning_profile.get("semantic_adjustments", {}) or {}
      operator_adjustments = tuning_profile.get("operator_adjustments", {}) or {}
      channel_adjustments = tuning_profile.get("channel_adjustments", {}) or {}
      for field_name in matched_fields:
        adjustment = int(field_adjustments.get(field_name, 0))
        if adjustment == 0:
          continue
        learned_score += adjustment
        tuning_signals.append(f"field {field_name} {adjustment:+d}")
      for concept in semantic_hits:
        adjustment = int(semantic_adjustments.get(concept, 0))
        if adjustment == 0:
          continue
        learned_score += adjustment
        tuning_signals.append(f"semantic {concept} {adjustment:+d}")
      for operator_hit in operator_hits:
        adjustment = int(operator_adjustments.get(operator_hit, 0))
        if adjustment == 0:
          continue
        learned_score += adjustment
        tuning_signals.append(f"operator {operator_hit} {adjustment:+d}")
      learned_score += int(channel_adjustments.get("lexical", 0)) * max(
        len(matched_terms) + len(matched_phrases),
        1 if lexical_score > 0 else 0,
      )
      learned_score += int(channel_adjustments.get("semantic", 0)) * len(semantic_hits)
      learned_score += int(channel_adjustments.get("operator", 0)) * len(operator_hits)
    score = lexical_score + semantic_score + operator_score
    if score <= 0:
      return None
    lexical_unit_total = len(terms) + len(phrases)
    lexical_units_matched = len(matched_terms) + len(matched_phrases)
    coverage = lexical_units_matched / lexical_unit_total if lexical_unit_total > 0 else 1.0
    coverage_pct = int(round(coverage * 100))
    score += coverage_pct * 2
    score += field_hits * 5
    if phrase_match:
      score += 40
    if exact_match:
      score += 60
    score += learned_score
    ranking_reason_parts = []
    if exact_match:
      ranking_reason_parts.append("exact field match")
    elif phrase_match:
      ranking_reason_parts.append("phrase match")
    if operator_hits:
      ranking_reason_parts.append(f"{len(operator_hits)} operator(s) satisfied")
    if semantic_hits:
      ranking_reason_parts.append(f"semantic hit: {', '.join(semantic_hits)}")
    if lexical_unit_total > 0:
      ranking_reason_parts.append(
        f"{lexical_units_matched} of {lexical_unit_total} lexical unit(s) matched"
      )
    if learned_score != 0:
      ranking_reason_parts.append(f"feedback tuned {learned_score:+d}")
    ranking_reason_parts.append(f"{field_hits} ranked field(s)")
    return {
      "score": score,
      "matched_terms": tuple(sorted(matched_terms)),
      "matched_phrases": tuple(sorted(matched_phrases)),
      "matched_fields": tuple(matched_fields),
      "term_coverage_pct": coverage_pct,
      "phrase_match": phrase_match,
      "exact_match": exact_match,
      "highlights": tuple(highlights[:3]),
      "semantic_concepts": semantic_hits,
      "operator_hits": tuple(operator_hits),
      "lexical_score": lexical_score,
      "semantic_score": semantic_score,
      "operator_score": operator_score,
      "learned_score": learned_score,
      "feedback_signal_count": int(tuning_profile.get("feedback_signal_count", 0))
      if isinstance(tuning_profile, Mapping)
      else 0,
      "tuning_signals": tuple(tuning_signals[:4]),
      "relevance_model": (
        str(tuning_profile.get("version"))
        if isinstance(tuning_profile, Mapping) and isinstance(tuning_profile.get("version"), str)
        else "tfidf_field_weight_v1"
      ),
      "ranking_reason": " · ".join(ranking_reason_parts),
    }

  @staticmethod
  def _humanize_provider_provenance_scheduler_retrieval_feature(
    feature: str,
  ) -> str:
    if not isinstance(feature, str) or not feature.strip():
      return ""
    _, _, raw_value = feature.partition(":")
    normalized_value = raw_value or feature
    return normalized_value.replace("_", " ").replace("->", " -> ").strip()

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_retrieval_vector(
    cls,
    *,
    row: Mapping[str, Any],
    search_match: Mapping[str, Any],
    document: Mapping[str, Any],
  ) -> dict[str, float]:
    alert = row.get("alert")
    narrative = row.get("narrative")
    if not isinstance(alert, OperatorAlert):
      return {}
    vector: dict[str, float] = {}

    def add_feature(feature: str | None, weight: float) -> None:
      if not isinstance(feature, str) or not feature.strip():
        return
      vector[feature] = vector.get(feature, 0.0) + weight

    for concept in document.get("semantic_concepts", ()) or ():
      if isinstance(concept, str):
        add_feature(f"concept:{concept}", 3.0)
    for concept in search_match.get("semantic_concepts", ()) or ():
      if isinstance(concept, str):
        add_feature(f"concept:{concept}", 4.5)
    for term in search_match.get("matched_terms", ()) or ():
      if isinstance(term, str):
        add_feature(f"term:{term}", 3.0)
    for phrase in search_match.get("matched_phrases", ()) or ():
      if isinstance(phrase, str):
        add_feature(f"phrase:{phrase}", 4.0)
        for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(phrase):
          add_feature(f"term:{token}", 1.5)

    add_feature(f"category:{alert.category}", 2.6)
    add_feature(f"status:{alert.status}", 2.2)
    add_feature(f"severity:{alert.severity}", 1.2)
    add_feature(f"source:{alert.source}", 1.0)

    if isinstance(narrative, Mapping):
      facet = narrative.get("facet")
      if isinstance(facet, str) and facet.strip():
        add_feature(f"facet:{facet}", 2.1)
      for flag in narrative.get("facet_flags", ()) or ():
        if isinstance(flag, str) and flag.strip():
          add_feature(f"flag:{flag}", 1.6)
      status_sequence = tuple(
        status
        for status in narrative.get("status_sequence", ()) or ()
        if isinstance(status, str) and status.strip()
      )
      if status_sequence:
        add_feature(f"sequence:{'->'.join(status_sequence)}", 2.8)
        for status in status_sequence:
          add_feature(f"sequence_state:{status}", 1.0)

    primary_focus = alert.primary_focus
    if primary_focus is not None:
      if isinstance(primary_focus.symbol, str) and primary_focus.symbol.strip():
        add_feature(f"focus:{primary_focus.symbol.strip().lower()}", 1.8)
      if isinstance(primary_focus.timeframe, str) and primary_focus.timeframe.strip():
        add_feature(f"focus:{primary_focus.timeframe.strip().lower()}", 1.4)
      if isinstance(primary_focus.policy, str) and primary_focus.policy.strip():
        add_feature(f"focus_policy:{primary_focus.policy.strip().lower()}", 1.2)
      if isinstance(primary_focus.reason, str) and primary_focus.reason.strip():
        for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(
          primary_focus.reason
        ):
          add_feature(f"term:{token}", 0.8)

    for value in document.get("normalized_fields", {}).get("market_context", ()) or ():
      if not isinstance(value, str):
        continue
      for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(value):
        add_feature(f"term:{token}", 0.8)
    for value in document.get("normalized_fields", {}).get("summary", ()) or ():
      if not isinstance(value, str):
        continue
      for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(value):
        if token in search_match.get("matched_terms", ()):
          add_feature(f"term:{token}", 0.6)
    return vector

  @staticmethod
  def _calculate_provider_provenance_scheduler_retrieval_similarity(
    left: Mapping[str, float],
    right: Mapping[str, float],
  ) -> float:
    if not left or not right:
      return 0.0
    if len(left) <= len(right):
      dot_product = sum(weight * right.get(key, 0.0) for key, weight in left.items())
    else:
      dot_product = sum(weight * left.get(key, 0.0) for key, weight in right.items())
    if dot_product <= 0:
      return 0.0
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    if left_norm <= 0 or right_norm <= 0:
      return 0.0
    return dot_product / (left_norm * right_norm)

  @staticmethod
  def _merge_provider_provenance_scheduler_retrieval_vectors(
    vectors: Iterable[Mapping[str, float]],
  ) -> dict[str, float]:
    merged: dict[str, float] = {}
    for vector in vectors:
      for key, weight in vector.items():
        merged[key] = merged.get(key, 0.0) + float(weight)
    return merged

  @classmethod
  def _build_provider_provenance_scheduler_retrieval_cluster_label(
    cls,
    *,
    semantic_concepts: tuple[str, ...],
    categories: tuple[str, ...],
    statuses: tuple[str, ...],
  ) -> str:
    label_parts: list[str] = []
    if semantic_concepts:
      label_parts.append(" / ".join(cls._humanize_provider_provenance_scheduler_retrieval_feature(f"concept:{concept}") for concept in semantic_concepts[:2]))
    if categories:
      label_parts.append(
        cls._humanize_provider_provenance_scheduler_retrieval_feature(f"category:{categories[0]}")
      )
    if statuses:
      label_parts.append(
        cls._humanize_provider_provenance_scheduler_retrieval_feature(f"status:{statuses[0]}")
      )
    label = " · ".join(part for part in label_parts if part)
    return label or "Cross-occurrence retrieval cluster"

  @classmethod
  def _cluster_provider_provenance_scheduler_alert_occurrence_search_results(
    cls,
    *,
    rows: tuple[Mapping[str, Any], ...],
    index: Mapping[str, Any],
  ) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    if not rows:
      return (), ()
    documents_by_id = {
      int(document.get("document_id", -1)): document
      for document in index.get("documents", ()) or ()
      if isinstance(document, Mapping)
    }
    raw_clusters: list[dict[str, Any]] = []
    similarity_threshold = 0.46
    for result_index, row in enumerate(rows):
      search_match = row.get("search_match")
      document_id = row.get("_search_document_id")
      document = documents_by_id.get(int(document_id)) if isinstance(document_id, int) else None
      if not isinstance(search_match, Mapping) or not isinstance(document, Mapping):
        continue
      vector = cls._build_provider_provenance_scheduler_alert_occurrence_retrieval_vector(
        row=row,
        search_match=search_match,
        document=document,
      )
      best_cluster_index: int | None = None
      best_similarity = 0.0
      for cluster_index, cluster in enumerate(raw_clusters):
        similarity = cls._calculate_provider_provenance_scheduler_retrieval_similarity(
          vector,
          cluster["centroid"],
        )
        if similarity > best_similarity:
          best_similarity = similarity
          best_cluster_index = cluster_index
      if best_cluster_index is None or best_similarity < similarity_threshold:
        raw_clusters.append(
          {
            "items": [
              {
                "result_index": result_index,
                "row": row,
                "vector": vector,
                "similarity": 1.0,
              }
            ],
            "centroid": dict(vector),
          }
        )
        continue
      cluster = raw_clusters[best_cluster_index]
      cluster["items"].append(
        {
          "result_index": result_index,
          "row": row,
          "vector": vector,
          "similarity": best_similarity,
        }
      )
      cluster["centroid"] = cls._merge_provider_provenance_scheduler_retrieval_vectors(
        item["vector"] for item in cluster["items"]
      )

    ordered_clusters = sorted(
      raw_clusters,
      key=lambda cluster: (
        max(
          (
            int(item["row"].get("search_match", {}).get("score", 0))
            for item in cluster["items"]
          ),
          default=0,
        ),
        len(cluster["items"]),
      ),
      reverse=True,
    )
    cluster_payloads: list[dict[str, Any]] = []
    retrieval_cluster_by_result_index: dict[int, dict[str, Any]] = {}
    for cluster_rank, cluster in enumerate(ordered_clusters, start=1):
      sorted_items = sorted(
        cluster["items"],
        key=lambda item: (
          int(item["row"].get("search_match", {}).get("score", 0)),
          item["row"]["alert"].resolved_at or item["row"]["alert"].detected_at,
        ),
        reverse=True,
      )
      top_occurrence = sorted_items[0]["row"]["alert"]
      semantic_counts: dict[str, int] = {}
      category_counts: dict[str, int] = {}
      status_counts: dict[str, int] = {}
      facet_counts: dict[str, int] = {}
      for item in sorted_items:
        row = item["row"]
        alert = row.get("alert")
        narrative = row.get("narrative")
        search_match = row.get("search_match", {})
        if isinstance(search_match, Mapping):
          for concept in search_match.get("semantic_concepts", ()) or ():
            if isinstance(concept, str):
              semantic_counts[concept] = semantic_counts.get(concept, 0) + 1
        if isinstance(alert, OperatorAlert):
          category_counts[alert.category] = category_counts.get(alert.category, 0) + 1
          status_counts[alert.status] = status_counts.get(alert.status, 0) + 1
        if isinstance(narrative, Mapping):
          facet = narrative.get("facet")
          if isinstance(facet, str) and facet.strip():
            facet_counts[facet] = facet_counts.get(facet, 0) + 1
      sorted_semantic_concepts = tuple(
        concept
        for concept, _ in sorted(
          semantic_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      sorted_categories = tuple(
        category_key
        for category_key, _ in sorted(
          category_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      sorted_statuses = tuple(
        status_key
        for status_key, _ in sorted(
          status_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      sorted_facets = tuple(
        facet_key
        for facet_key, _ in sorted(
          facet_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      top_vector_terms = tuple(
        dict.fromkeys(
          cls._humanize_provider_provenance_scheduler_retrieval_feature(feature)
          for feature, _ in sorted(
            cluster["centroid"].items(),
            key=lambda item: (-item[1], item[0]),
          )
          if feature.startswith(("concept:", "term:", "phrase:", "sequence:", "focus:"))
        )
      )[:5]
      label = cls._build_provider_provenance_scheduler_retrieval_cluster_label(
        semantic_concepts=sorted_semantic_concepts,
        categories=sorted_categories,
        statuses=sorted_statuses,
      )
      cluster_id = f"cluster-{cluster_rank}"
      score_values = [
        int(item["row"].get("search_match", {}).get("score", 0))
        for item in sorted_items
      ]
      similarity_values = [float(item.get("similarity", 0.0)) for item in sorted_items]
      summary = (
        f"{len(sorted_items)} occurrence(s) grouped around {label.lower()}"
      )
      cluster_payload = {
        "cluster_id": cluster_id,
        "rank": cluster_rank,
        "label": label,
        "summary": summary,
        "occurrence_count": len(sorted_items),
        "top_score": max(score_values, default=0),
        "average_score": int(round(sum(score_values) / len(score_values))) if score_values else 0,
        "average_similarity_pct": int(round((sum(similarity_values) / len(similarity_values)) * 100))
        if similarity_values
        else 0,
        "semantic_concepts": sorted_semantic_concepts[:5],
        "vector_terms": top_vector_terms,
        "categories": sorted_categories,
        "statuses": sorted_statuses,
        "narrative_facets": sorted_facets,
        "top_occurrence_id": top_occurrence.occurrence_id,
        "top_occurrence_summary": top_occurrence.summary,
        "occurrence_ids": tuple(
          item["row"]["alert"].occurrence_id
          for item in sorted_items
          if isinstance(item["row"]["alert"].occurrence_id, str)
        ),
      }
      cluster_payloads.append(cluster_payload)
      for item in sorted_items:
        retrieval_cluster_by_result_index[item["result_index"]] = {
          "cluster_id": cluster_id,
          "rank": cluster_rank,
          "label": label,
          "similarity_pct": int(round(float(item.get("similarity", 0.0)) * 100)),
          "semantic_concepts": list(cluster_payload["semantic_concepts"]),
          "vector_terms": list(cluster_payload["vector_terms"]),
        }

    enriched_rows = tuple(
      {
        **row,
        "retrieval_cluster": retrieval_cluster_by_result_index.get(result_index),
      }
      for result_index, row in enumerate(rows)
    )
    return enriched_rows, tuple(cluster_payloads)

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_search_match(
    cls,
    *,
    row: Mapping[str, Any],
    search: str | None,
  ) -> dict[str, Any] | None:
    if not isinstance(search, str) or not search.strip():
      return None
    parsed_query = cls._parse_provider_provenance_scheduler_alert_search_query(search)
    index = cls._build_provider_provenance_scheduler_alert_occurrence_search_index(rows=(row,))
    document = next(iter(index.get("documents", ())), None)
    matched_document_ids = cls._evaluate_provider_provenance_scheduler_alert_search_query(
      index=index,
      parsed_query=parsed_query,
    )
    if 0 not in matched_document_ids:
      return None
    return cls._score_provider_provenance_scheduler_alert_occurrence_search_match(
      row=row,
      parsed_query=parsed_query,
      index=index,
      document=document,
    )

  @staticmethod
  def _build_provider_provenance_scheduler_occurrence_detected_at(
    *,
    target_status: str,
    snapshot: ProviderProvenanceSchedulerHealth,
  ) -> datetime:
    if target_status == "lagging":
      return snapshot.oldest_due_at or snapshot.generated_at
    return (
      snapshot.last_failure_at
      or snapshot.last_cycle_finished_at
      or snapshot.last_cycle_started_at
      or snapshot.generated_at
    )

  @staticmethod
  def _compress_provider_provenance_scheduler_status_sequence(
    records: Iterable[ProviderProvenanceSchedulerHealthRecord],
  ) -> tuple[str, ...]:
    sequence: list[str] = []
    for record in records:
      if not sequence or sequence[-1] != record.status:
        sequence.append(record.status)
    return tuple(sequence)

  def _build_provider_provenance_scheduler_alert_occurrence_rows(
    self,
    *,
    current_time: datetime,
  ) -> tuple[dict[str, Any], ...]:
    self._prune_provider_provenance_scheduler_health_records()
    records = tuple(
      sorted(
        self._list_provider_provenance_scheduler_health_records(),
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    if not records:
      return ()
    current_health = self.get_provider_provenance_scheduler_health()
    occurrence_rows: list[dict[str, Any]] = []
    for target_status in ("lagging", "failed"):
      status_rows: list[dict[str, Any]] = []
      index = 0
      while index < len(records):
        if records[index].status != target_status:
          index += 1
          continue
        start_index = index
        end_index = index
        while end_index + 1 < len(records) and records[end_index + 1].status == target_status:
          end_index += 1
        latest_record = records[end_index]
        latest_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(latest_record)
        alert = self._build_provider_provenance_scheduler_operator_alert(
          health=latest_snapshot,
          current_time=current_time,
        )
        if alert is not None:
          first_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
            records[start_index]
          )
          detected_at = self._build_provider_provenance_scheduler_occurrence_detected_at(
            target_status=target_status,
            snapshot=first_snapshot,
          )
          is_active_occurrence = end_index == len(records) - 1 and current_health.status == target_status
          resolved_at = (
            None
            if is_active_occurrence
            else (
              records[end_index + 1].recorded_at
              if end_index + 1 < len(records)
              else current_time
            )
          )
          next_occurrence_start_index: int | None = None
          search_index = end_index + 1
          while search_index < len(records):
            if records[search_index].status == target_status:
              next_occurrence_start_index = search_index
              break
            search_index += 1
          narrative_end_index = (
            next_occurrence_start_index - 1
            if next_occurrence_start_index is not None
            else len(records) - 1
          )
          occurrence_records = tuple(records[start_index:end_index + 1])
          post_resolution_records = (
            tuple(records[end_index + 1:narrative_end_index + 1])
            if resolved_at is not None and end_index + 1 <= narrative_end_index
            else ()
          )
          narrative_records = (*occurrence_records, *post_resolution_records)
          next_occurrence_detected_at = (
            self._build_provider_provenance_scheduler_occurrence_detected_at(
              target_status=target_status,
              snapshot=self._provider_provenance_scheduler_health_snapshot_from_record(
                records[next_occurrence_start_index]
              ),
            )
            if next_occurrence_start_index is not None
            else None
          )
          primary_facet = "current_snapshot" if is_active_occurrence else "resolved_narrative"
          facet_flags: list[str] = [primary_facet]
          if post_resolution_records:
            primary_facet = "post_resolution_recovery"
            if "resolved_narrative" not in facet_flags:
              facet_flags.append("resolved_narrative")
            facet_flags.append("post_resolution_recovery")
          status_rows.append(
            {
              "alert": replace(
                alert,
                detected_at=detected_at,
                occurrence_id=self._build_operator_alert_occurrence_id(
                  alert_id=alert.alert_id,
                  detected_at=detected_at,
                  resolved_at=resolved_at,
                ),
                timeline_key=alert.category,
                timeline_position=len(status_rows) + 1,
                status="active" if is_active_occurrence else "resolved",
                resolved_at=resolved_at,
              ),
              "narrative": {
                "facet": primary_facet,
                "facet_flags": tuple(facet_flags),
                "narrative_mode": (
                  "matched_status"
                  if is_active_occurrence
                  else "mixed_status_post_resolution"
                ),
                "can_reconstruct_narrative": not is_active_occurrence,
                "has_post_resolution_history": bool(post_resolution_records),
                "occurrence_record_count": len(occurrence_records),
                "post_resolution_record_count": len(post_resolution_records),
                "status_sequence": self._compress_provider_provenance_scheduler_status_sequence(
                  narrative_records
                ),
                "post_resolution_status_sequence": (
                  self._compress_provider_provenance_scheduler_status_sequence(
                    post_resolution_records
                  )
                  if post_resolution_records
                  else ()
                ),
                "narrative_window_ended_at": (
                  narrative_records[-1].recorded_at if narrative_records else resolved_at
                ),
                "next_occurrence_detected_at": next_occurrence_detected_at,
              },
              "occurrence_records": occurrence_records,
              "narrative_records": tuple(narrative_records),
              "latest_record": latest_record,
            }
          )
        index = end_index + 1
      total_occurrences = len(status_rows)
      for row in status_rows:
        alert = row["alert"]
        narrative = dict(row["narrative"])
        facet_flags = list(narrative.get("facet_flags", ()))
        if total_occurrences > 1:
          facet_flags.append("recurring_occurrence")
          if (
            narrative.get("facet") == "resolved_narrative"
            and not narrative.get("has_post_resolution_history")
          ):
            narrative["facet"] = "recurring_occurrence"
        narrative["facet_flags"] = tuple(dict.fromkeys(facet_flags))
        row["alert"] = replace(alert, timeline_total=total_occurrences)
        row["narrative"] = narrative
        occurrence_rows.append(row)
    return tuple(
      sorted(
        occurrence_rows,
        key=lambda row: (
          row["alert"].resolved_at or row["alert"].detected_at,
          row["alert"].detected_at,
        ),
        reverse=True,
      )
    )

  def list_provider_provenance_scheduler_health_history(
    self,
    *,
    status: str | None = None,
    limit: int = 25,
    offset: int = 0,
  ) -> tuple[ProviderProvenanceSchedulerHealthRecord, ...]:
    self._prune_provider_provenance_scheduler_health_records()
    normalized_status = self._normalize_provider_provenance_scheduler_health_status(status)
    normalized_limit = max(1, min(limit, 200))
    normalized_offset = max(offset, 0)
    records = [
      record
      for record in self._list_provider_provenance_scheduler_health_records()
      if normalized_status is None or record.status == normalized_status
    ]
    return tuple(records[normalized_offset:normalized_offset + normalized_limit])

  def get_provider_provenance_scheduler_health_history_page(
    self,
    *,
    status: str | None = None,
    limit: int = 25,
    offset: int = 0,
  ) -> dict[str, Any]:
    self._prune_provider_provenance_scheduler_health_records()
    normalized_status = self._normalize_provider_provenance_scheduler_health_status(status)
    normalized_limit = max(1, min(limit, 200))
    normalized_offset = max(offset, 0)
    records = [
      record
      for record in self._list_provider_provenance_scheduler_health_records()
      if normalized_status is None or record.status == normalized_status
    ]
    total = len(records)
    items = records[normalized_offset:normalized_offset + normalized_limit]
    next_offset = (
      normalized_offset + len(items)
      if normalized_offset + len(items) < total
      else None
    )
    previous_offset = (
      max(normalized_offset - normalized_limit, 0)
      if normalized_offset > 0 and total > 0
      else None
    )
    return {
      "query": {
        "status": normalized_status,
        "limit": normalized_limit,
        "offset": normalized_offset,
      },
      "items": tuple(items),
      "total": total,
      "returned": len(items),
      "has_more": next_offset is not None,
      "next_offset": next_offset,
      "previous_offset": previous_offset,
    }

  def get_provider_provenance_scheduler_alert_history_page(
    self,
    *,
    category: str | None = None,
    status: str | None = None,
    narrative_facet: str | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
  ) -> dict[str, Any]:
    current_time = self._clock()
    history_rows = self._build_provider_provenance_scheduler_alert_occurrence_rows(
      current_time=current_time,
    )
    history = tuple(row["alert"] for row in history_rows)
    normalized_category = self._normalize_provider_provenance_scheduler_alert_history_category(category)
    normalized_status = self._normalize_provider_provenance_scheduler_alert_history_status(status)
    normalized_narrative_facet = self._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
      narrative_facet
    )
    normalized_search = search.strip() if isinstance(search, str) and search.strip() else None
    normalized_limit = max(1, min(limit, 200))
    normalized_offset = max(offset, 0)
    eligible_history: list[dict[str, Any]] = []
    for row in history_rows:
      if normalized_category is not None and row["alert"].category != normalized_category:
        continue
      if normalized_status is not None and row["alert"].status != normalized_status:
        continue
      if (
        normalized_narrative_facet is not None
        and normalized_narrative_facet != "all_occurrences"
        and not (
          (
            normalized_narrative_facet == "resolved_narratives"
            and bool(row["narrative"].get("can_reconstruct_narrative"))
          )
          or (
            normalized_narrative_facet == "post_resolution_recovery"
            and bool(row["narrative"].get("has_post_resolution_history"))
          )
          or (
            normalized_narrative_facet == "recurring_occurrences"
            and "recurring_occurrence" in row["narrative"].get("facet_flags", ())
          )
        )
      ):
        continue
      eligible_history.append(row)
    filtered_history: list[dict[str, Any]] = []
    retrieval_clusters: tuple[dict[str, Any], ...] = ()
    search_analytics = None
    parsed_search = (
      self._parse_provider_provenance_scheduler_alert_search_query(normalized_search)
      if normalized_search is not None
      else None
    )
    if normalized_search is not None:
      search_projection_lookup = self._build_provider_provenance_scheduler_search_projection_lookup(
        record_ids=(
          record.record_id
          for row in eligible_history
          for record in row.get("narrative_records", ()) or ()
          if isinstance(record, ProviderProvenanceSchedulerHealthRecord)
        )
      )
      search_index = self._build_provider_provenance_scheduler_alert_occurrence_search_index(
        rows=tuple(eligible_history),
        search_projection_lookup=search_projection_lookup,
      )
      tuning_profile = self._build_provider_provenance_scheduler_search_tuning_profile(
        search_query=normalized_search,
        parsed_query=parsed_search or {},
      )
      matched_document_ids = self._evaluate_provider_provenance_scheduler_alert_search_query(
        index=search_index,
        parsed_query=parsed_search or {},
      )
      for matched_document_id in matched_document_ids:
        if not (0 <= matched_document_id < len(eligible_history)):
          continue
        row = eligible_history[matched_document_id]
        document = search_index.get("documents", ())[matched_document_id]
        search_match = self._score_provider_provenance_scheduler_alert_occurrence_search_match(
          row=row,
          parsed_query=parsed_search or {},
          index=search_index,
          document=document,
          tuning_profile=tuning_profile,
        )
        if search_match is None:
          continue
        filtered_history.append(
          {
            **row,
            "search_match": search_match,
            "_search_document_id": matched_document_id,
          }
        )
    else:
      filtered_history = [{**row, "search_match": None} for row in eligible_history]
    if normalized_search is not None:
      filtered_history = sorted(
        filtered_history,
        key=lambda row: (
          row.get("search_match", {}).get("score", 0),
          row.get("search_match", {}).get("term_coverage_pct", 0),
          1 if row.get("search_match", {}).get("exact_match") else 0,
          1 if row.get("search_match", {}).get("phrase_match") else 0,
          row["alert"].resolved_at or row["alert"].detected_at,
          row["alert"].detected_at,
        ),
        reverse=True,
      )
      clustered_history, retrieval_clusters = self._cluster_provider_provenance_scheduler_alert_occurrence_search_results(
        rows=tuple(filtered_history),
        index=search_index,
      )
      filtered_history = list(clustered_history)
    total = len(filtered_history)
    items = filtered_history[normalized_offset:normalized_offset + normalized_limit]
    next_offset = (
      normalized_offset + len(items)
      if normalized_offset + len(items) < total
      else None
    )
    previous_offset = (
      max(normalized_offset - normalized_limit, 0)
      if normalized_offset > 0 and total > 0
      else None
    )
    categories = tuple(
      category_key
      for category_key in ("scheduler_lag", "scheduler_failure")
      if any(alert.category == category_key for alert in history)
    ) or ("scheduler_lag", "scheduler_failure")
    statuses = tuple(
      status_key
      for status_key in ("active", "resolved")
      if any(alert.status == status_key for alert in history)
    ) or ("active", "resolved")
    summary_by_category = tuple(
      {
        "category": category_key,
        "total": sum(1 for alert in history if alert.category == category_key),
        "active_count": sum(
          1
          for alert in history
          if alert.category == category_key and alert.status == "active"
        ),
        "resolved_count": sum(
          1
          for alert in history
          if alert.category == category_key and alert.status == "resolved"
        ),
      }
      for category_key in categories
    )
    search_summary = None
    if normalized_search is not None:
      persistence_modes = tuple(
        dict.fromkeys(
          str(document.get("persistence_mode"))
          for document in search_index.get("documents", ())
          if isinstance(document.get("persistence_mode"), str)
          and document.get("persistence_mode") != "ephemeral_occurrence_projection"
        )
      )
      search_summary = {
        "query": normalized_search,
        "mode": "persistent_full_text_boolean_semantic_ranking",
        "token_count": len(parsed_search.get("terms", ())) + len(parsed_search.get("phrases", ())),
        "matched_occurrences": total,
        "top_score": max(
          (int(row.get("search_match", {}).get("score", 0)) for row in filtered_history),
          default=0,
        ),
        "max_term_coverage_pct": max(
          (
            int(row.get("search_match", {}).get("term_coverage_pct", 0))
            for row in filtered_history
          ),
          default=0,
        ),
        "phrase_match_count": sum(
          1 for row in filtered_history if bool(row.get("search_match", {}).get("phrase_match"))
        ),
        "operator_count": len(parsed_search.get("operators", ())),
        "semantic_concept_count": len(parsed_search.get("semantic_concepts", ())),
        "negated_term_count": len(parsed_search.get("excluded_terms", ()))
        + len(parsed_search.get("excluded_phrases", ()))
        + sum(1 for operator in parsed_search.get("operators", ()) if operator.get("negated")),
        "boolean_operator_count": int(parsed_search.get("boolean_operator_count", 0)),
        "indexed_occurrence_count": len(eligible_history),
        "indexed_term_count": int(search_index.get("indexed_term_count", 0)),
        "persistence_mode": (
          persistence_modes[0]
          if persistence_modes
          else "ephemeral_occurrence_projection"
        ),
        "relevance_model": tuning_profile.get("version", "tfidf_field_weight_v1"),
        "parsed_terms": tuple(parsed_search.get("terms", ())),
        "parsed_phrases": tuple(parsed_search.get("phrases", ())),
        "parsed_operators": tuple(
          operator.get("raw")
          for operator in parsed_search.get("operators", ())
          if isinstance(operator.get("raw"), str)
        ),
        "semantic_concepts": tuple(parsed_search.get("semantic_concepts", ())),
        "query_plan": tuple(parsed_search.get("query_plan", ())),
        "retrieval_cluster_mode": "cross_occurrence_semantic_vector_cluster_v1",
        "retrieval_cluster_count": len(retrieval_clusters),
        "top_cluster_label": (
          retrieval_clusters[0].get("label")
          if retrieval_clusters
          else None
        ),
      }
      analytics_record = self._record_provider_provenance_scheduler_search_query_analytics(
        recorded_at=current_time,
        search_query=normalized_search,
        category=normalized_category,
        status=normalized_status,
        narrative_facet=normalized_narrative_facet or "all_occurrences",
        parsed_query=parsed_search or {},
        matched_rows=tuple(filtered_history),
        indexed_occurrence_count=len(eligible_history),
        indexed_term_count=int(search_index.get("indexed_term_count", 0)),
        persistence_mode=search_summary["persistence_mode"],
        relevance_model=search_summary["relevance_model"],
        top_cluster_label=search_summary["top_cluster_label"],
      )
      search_summary["query_id"] = analytics_record.query_id
      search_analytics = self._build_provider_provenance_scheduler_search_analytics_summary(
        query_record=analytics_record,
        search_query=normalized_search,
        tuning_profile=tuning_profile,
      )
    return {
      "generated_at": current_time,
      "query": {
        "category": normalized_category,
        "status": normalized_status,
        "narrative_facet": normalized_narrative_facet or "all_occurrences",
        "search": normalized_search,
        "limit": normalized_limit,
        "offset": normalized_offset,
      },
      "available_filters": {
        "categories": categories,
        "statuses": statuses,
        "narrative_facets": (
          "all_occurrences",
          "resolved_narratives",
          "post_resolution_recovery",
          "recurring_occurrences",
        ),
      },
      "summary": {
        "total_occurrences": len(history),
        "active_count": sum(1 for alert in history if alert.status == "active"),
        "resolved_count": sum(1 for alert in history if alert.status == "resolved"),
        "by_category": summary_by_category,
      },
      "search_summary": search_summary,
      "search_analytics": search_analytics,
      "retrieval_clusters": retrieval_clusters,
      "items": tuple(items),
      "total": total,
      "returned": len(items),
      "has_more": next_offset is not None,
      "next_offset": next_offset,
      "previous_offset": previous_offset,
    }

  @classmethod
  def _resolve_provider_provenance_scheduler_bucket_start(
    cls,
    bucket_key: str | None,
  ) -> datetime | None:
    if not isinstance(bucket_key, str) or not bucket_key.strip():
      return None
    normalized = bucket_key.strip()
    try:
      parsed = datetime.fromisoformat(normalized)
    except ValueError:
      return None
    parsed = parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    return parsed.replace(hour=0, minute=0, second=0, microsecond=0)

  @classmethod
  def _build_provider_provenance_scheduler_health_time_series(
    cls,
    *,
    records: tuple[ProviderProvenanceSchedulerHealthRecord, ...],
    window_days: int,
    now: datetime,
  ) -> dict[str, Any]:
    normalized_window_days = max(3, min(window_days, 90))
    anchor_candidates = [now]
    anchor_candidates.extend(record.recorded_at for record in records)
    window_anchor = cls._normalize_provider_provenance_export_bucket_start(max(anchor_candidates))
    window_started_at = window_anchor - timedelta(days=normalized_window_days - 1)
    window_ended_at = window_anchor + timedelta(days=1)

    record_buckets: dict[datetime, list[ProviderProvenanceSchedulerHealthRecord]] = {}
    for record in records:
      bucket_start = cls._normalize_provider_provenance_export_bucket_start(record.recorded_at)
      if not (window_started_at <= bucket_start < window_ended_at):
        continue
      record_buckets.setdefault(bucket_start, []).append(record)

    health_status_series: list[dict[str, Any]] = []
    lag_trend_series: list[dict[str, Any]] = []

    for offset in range(normalized_window_days):
      bucket_start = window_started_at + timedelta(days=offset)
      bucket_end = bucket_start + timedelta(days=1)
      bucket_records = sorted(
        record_buckets.get(bucket_start, []),
        key=lambda record: (record.recorded_at, record.record_id),
      )
      counts_by_status = {
        "healthy": 0,
        "lagging": 0,
        "failed": 0,
        "disabled": 0,
        "starting": 0,
      }
      for record in bucket_records:
        counts_by_status[record.status] = counts_by_status.get(record.status, 0) + 1
      dominant_status, dominant_count = max(
        counts_by_status.items(),
        key=lambda item: (item[1], item[0]),
      )
      latest_record = bucket_records[-1] if bucket_records else None
      cycle_count = len(bucket_records)
      executed_report_count = sum(record.last_executed_count for record in bucket_records)
      failure_count = sum(1 for record in bucket_records if record.status == "failed")
      lag_values = [max(record.max_due_lag_seconds, 0) for record in bucket_records]
      due_counts = [max(record.due_report_count, 0) for record in bucket_records]
      bucket_key = bucket_start.date().isoformat()
      bucket_label = bucket_start.strftime("%b %d")

      health_status_series.append(
        {
          "bucket_key": bucket_key,
          "bucket_label": bucket_label,
          "started_at": bucket_start.isoformat(),
          "ended_at": bucket_end.isoformat(),
          "cycle_count": cycle_count,
          "healthy_count": counts_by_status["healthy"],
          "lagging_count": counts_by_status["lagging"],
          "failed_count": counts_by_status["failed"],
          "disabled_count": counts_by_status["disabled"],
          "starting_count": counts_by_status["starting"],
          "dominant_status": dominant_status if dominant_count > 0 else "no_data",
          "dominant_count": dominant_count,
          "latest_status": latest_record.status if latest_record is not None else "no_data",
          "latest_summary": latest_record.summary if latest_record is not None else "",
          "executed_report_count": executed_report_count,
        }
      )
      lag_trend_series.append(
        {
          "bucket_key": bucket_key,
          "bucket_label": bucket_label,
          "started_at": bucket_start.isoformat(),
          "ended_at": bucket_end.isoformat(),
          "cycle_count": cycle_count,
          "peak_lag_seconds": max(lag_values) if lag_values else 0,
          "latest_lag_seconds": lag_values[-1] if lag_values else 0,
          "average_lag_seconds": round(sum(lag_values) / len(lag_values), 1) if lag_values else 0.0,
          "peak_due_report_count": max(due_counts) if due_counts else 0,
          "latest_due_report_count": due_counts[-1] if due_counts else 0,
          "failure_count": failure_count,
          "executed_report_count": executed_report_count,
        }
      )

    peak_cycle_bucket = max(
      health_status_series,
      key=lambda item: (
        int(item["cycle_count"]),
        int(item["failed_count"]),
        item["bucket_key"],
      ),
      default=None,
    )
    peak_lag_bucket = max(
      lag_trend_series,
      key=lambda item: (
        int(item["peak_lag_seconds"]),
        int(item["peak_due_report_count"]),
        item["bucket_key"],
      ),
      default=None,
    )
    latest_health_bucket = health_status_series[-1] if health_status_series else None
    latest_lag_bucket = lag_trend_series[-1] if lag_trend_series else None

    return {
      "bucket_size": "day",
      "window_days": normalized_window_days,
      "window_started_at": window_started_at.isoformat(),
      "window_ended_at": window_ended_at.isoformat(),
      "health_status": {
        "series": health_status_series,
        "summary": {
          "peak_cycle_bucket_key": peak_cycle_bucket["bucket_key"] if peak_cycle_bucket is not None else None,
          "peak_cycle_bucket_label": (
            peak_cycle_bucket["bucket_label"]
            if peak_cycle_bucket is not None
            else None
          ),
          "peak_cycle_count": int(peak_cycle_bucket["cycle_count"]) if peak_cycle_bucket is not None else 0,
          "latest_bucket_key": latest_health_bucket["bucket_key"] if latest_health_bucket is not None else None,
          "latest_bucket_label": (
            latest_health_bucket["bucket_label"]
            if latest_health_bucket is not None
            else None
          ),
          "latest_status": latest_health_bucket["latest_status"] if latest_health_bucket is not None else "no_data",
          "latest_cycle_count": int(latest_health_bucket["cycle_count"]) if latest_health_bucket is not None else 0,
        },
      },
      "lag_trend": {
        "series": lag_trend_series,
        "summary": {
          "peak_lag_bucket_key": peak_lag_bucket["bucket_key"] if peak_lag_bucket is not None else None,
          "peak_lag_bucket_label": peak_lag_bucket["bucket_label"] if peak_lag_bucket is not None else None,
          "peak_lag_seconds": int(peak_lag_bucket["peak_lag_seconds"]) if peak_lag_bucket is not None else 0,
          "latest_bucket_key": latest_lag_bucket["bucket_key"] if latest_lag_bucket is not None else None,
          "latest_bucket_label": latest_lag_bucket["bucket_label"] if latest_lag_bucket is not None else None,
          "latest_lag_seconds": int(latest_lag_bucket["latest_lag_seconds"]) if latest_lag_bucket is not None else 0,
          "latest_due_report_count": (
            int(latest_lag_bucket["latest_due_report_count"])
            if latest_lag_bucket is not None
            else 0
          ),
          "latest_failure_count": int(latest_lag_bucket["failure_count"]) if latest_lag_bucket is not None else 0,
        },
      },
    }

  @staticmethod
  def _normalize_provider_provenance_scheduler_alert_category(
    category: str,
  ) -> str:
    normalized_category = category.strip().lower() if isinstance(category, str) else ""
    if normalized_category not in {"scheduler_lag", "scheduler_failure"}:
      raise ValueError("Unsupported scheduler alert category for historical export reconstruction.")
    return normalized_category

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_mode(
    narrative_mode: str | None,
  ) -> str:
    if not isinstance(narrative_mode, str):
      return "matched_status"
    normalized_mode = narrative_mode.strip().lower()
    if normalized_mode in {"matched_status", "mixed_status_post_resolution"}:
      return normalized_mode
    raise ValueError("Unsupported scheduler historical export narrative mode.")

  @staticmethod
  def _normalize_provider_provenance_scheduler_export_datetime(
    value: datetime,
    *,
    field_name: str,
  ) -> datetime:
    if not isinstance(value, datetime):
      raise ValueError(f"{field_name} is required for scheduler export reconstruction.")
    return value.astimezone(UTC) if value.tzinfo is not None else value.replace(tzinfo=UTC)

  @staticmethod
  def _provider_provenance_scheduler_health_snapshot_from_record(
    record: ProviderProvenanceSchedulerHealthRecord,
  ) -> ProviderProvenanceSchedulerHealth:
    return ProviderProvenanceSchedulerHealth(
      generated_at=record.recorded_at,
      enabled=record.enabled,
      status=record.status,
      summary=record.summary,
      interval_seconds=record.interval_seconds,
      batch_limit=record.batch_limit,
      last_cycle_started_at=record.last_cycle_started_at,
      last_cycle_finished_at=record.last_cycle_finished_at,
      last_success_at=record.last_success_at,
      last_failure_at=record.last_failure_at,
      last_error=record.last_error,
      cycle_count=record.cycle_count,
      success_count=record.success_count,
      failure_count=record.failure_count,
      consecutive_failure_count=record.consecutive_failure_count,
      last_executed_count=record.last_executed_count,
      total_executed_count=record.total_executed_count,
      due_report_count=record.due_report_count,
      oldest_due_at=record.oldest_due_at,
      max_due_lag_seconds=record.max_due_lag_seconds,
      active_alert_key=record.active_alert_key,
      alert_workflow_job_id=record.alert_workflow_job_id,
      alert_workflow_triggered_at=record.alert_workflow_triggered_at,
      alert_workflow_state=record.alert_workflow_state,
      alert_workflow_summary=record.alert_workflow_summary,
      issues=record.issues,
    )

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_phase(
    *,
    record: ProviderProvenanceSchedulerHealthRecord,
    resolution_at: datetime | None,
  ) -> str:
    if resolution_at is not None and record.recorded_at >= resolution_at:
      return "post_resolution"
    return "occurrence"

  @classmethod
  def _build_provider_provenance_scheduler_status_narrative_segments(
    cls,
    *,
    records: tuple[ProviderProvenanceSchedulerHealthRecord, ...],
    resolution_at: datetime | None,
  ) -> tuple[dict[str, Any], ...]:
    if not records:
      return ()
    ordered_records = tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    segments: list[dict[str, Any]] = []
    start_index = 0
    while start_index < len(ordered_records):
      end_index = start_index
      while (
        end_index + 1 < len(ordered_records)
        and ordered_records[end_index + 1].status == ordered_records[start_index].status
      ):
        end_index += 1
      segment_records = ordered_records[start_index:end_index + 1]
      latest_record = segment_records[-1]
      segments.append(
        {
          "status": latest_record.status,
          "phase": cls._build_provider_provenance_scheduler_narrative_phase(
            record=segment_records[0],
            resolution_at=resolution_at,
          ),
          "started_at": segment_records[0].recorded_at.isoformat(),
          "ended_at": latest_record.recorded_at.isoformat(),
          "record_count": len(segment_records),
          "latest_record_id": latest_record.record_id,
          "latest_summary": latest_record.summary,
          "peak_lag_seconds": max(
            (record.max_due_lag_seconds for record in segment_records),
            default=0,
          ),
          "peak_due_report_count": max(
            (record.due_report_count for record in segment_records),
            default=0,
          ),
        }
      )
      start_index = end_index + 1
    return tuple(segments)

  def _build_provider_provenance_scheduler_operator_alert(
    self,
    *,
    health: ProviderProvenanceSchedulerHealth,
    current_time: datetime,
  ) -> OperatorAlert | None:
    if health.status == "lagging":
      severity = (
        "critical"
        if health.max_due_lag_seconds >= self._provider_provenance_scheduler_critical_lag_seconds()
        else "warning"
      )
      return OperatorAlert(
        alert_id="provider-provenance:scheduler-lag",
        severity=severity,
        category="scheduler_lag",
        summary="Provider provenance report scheduler is lagging.",
        detail=(
          f"{health.due_report_count} due report(s) remain. "
          f"Oldest due at {health.oldest_due_at.isoformat() if health.oldest_due_at is not None else 'n/a'} "
          f"with {health.max_due_lag_seconds}s lag. "
          f"Last successful cycle: {health.last_success_at.isoformat() if health.last_success_at is not None else 'n/a'}."
        ),
        detected_at=health.oldest_due_at or health.generated_at,
        source="runtime",
      )
    if health.status == "failed":
      detected_at = (
        health.last_failure_at
        or health.last_cycle_finished_at
        or health.last_cycle_started_at
        or current_time
      )
      return OperatorAlert(
        alert_id="provider-provenance:scheduler-failure",
        severity="critical",
        category="scheduler_failure",
        summary="Provider provenance report scheduler is failing.",
        detail=(
          f"{health.summary} Last success: "
          f"{health.last_success_at.isoformat() if health.last_success_at is not None else 'n/a'}. "
          f"Last error: {health.last_error or 'n/a'}."
        ),
        detected_at=detected_at,
        source="runtime",
      )
    return None

  def _build_provider_provenance_scheduler_alert_history(
    self,
    *,
    current_time: datetime,
  ) -> tuple[OperatorAlert, ...]:
    return tuple(
      row["alert"]
      for row in self._build_provider_provenance_scheduler_alert_occurrence_rows(
        current_time=current_time,
      )
    )

  def _collect_provider_provenance_scheduler_operator_visibility(
    self,
    *,
    current_time: datetime,
  ) -> tuple[ProviderProvenanceSchedulerHealth, list[OperatorAlert], list[OperatorAuditEvent]]:
    health = self.get_provider_provenance_scheduler_health()
    alerts: list[OperatorAlert] = []
    audit_events: list[OperatorAuditEvent] = []
    active_alert = self._build_provider_provenance_scheduler_operator_alert(
      health=health,
      current_time=current_time,
    )

    if active_alert is not None and health.status == "lagging":
      alerts.append(active_alert)
      audit_events.append(
        OperatorAuditEvent(
          event_id=f"audit:provider_provenance_scheduler_lagging:{health.generated_at.isoformat()}",
          timestamp=health.generated_at,
          actor="system",
          kind="provider_provenance_scheduler_lagging",
          summary="Provider provenance report scheduler lag detected.",
          detail=health.summary,
          source="runtime",
        )
      )
    elif active_alert is not None and health.status == "failed":
      detected_at = active_alert.detected_at
      alerts.append(active_alert)
      audit_events.append(
        OperatorAuditEvent(
          event_id=f"audit:provider_provenance_scheduler_failed:{detected_at.isoformat()}",
          timestamp=detected_at,
          actor="system",
          kind="provider_provenance_scheduler_failed",
          summary="Provider provenance report scheduler failure detected.",
          detail=health.summary + (f" Error: {health.last_error}." if health.last_error else ""),
          source="runtime",
        )
      )

    return health, alerts, audit_events

  def export_replay_intent_alias_audits(
    self,
    *,
    export_format: str = "json",
    alias_id: str | None = None,
    template_key: str | None = None,
    action: str | None = None,
    retention_policy: str | None = None,
    source_tab_id: str | None = None,
    search: str | None = None,
  ) -> dict[str, Any]:
    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported replay alias audit export format")
    audit_records = self.list_replay_intent_alias_audits(
      alias_id=alias_id,
      template_key=template_key,
      action=action,
      retention_policy=retention_policy,
      source_tab_id=source_tab_id,
      search=search,
      limit=None,
    )
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_replay_intent_alias_audit_record,
    )

    serialized_items = [
      serialize_replay_intent_alias_audit_record(record)
      for record in audit_records
    ]
    exported_at = self._clock().isoformat()
    normalized_template_key = template_key.strip() if isinstance(template_key, str) and template_key.strip() else "all"
    base_filename = f"replay-alias-audits-{normalized_template_key}"
    if normalized_format == "json":
      content = json.dumps(
        {
          "exported_at": exported_at,
          "filters": {
            "alias_id": alias_id,
            "template_key": template_key,
            "action": action,
            "retention_policy": retention_policy,
            "source_tab_id": source_tab_id,
            "search": search,
          },
          "total": len(serialized_items),
          "items": serialized_items,
        },
        indent=2,
        sort_keys=True,
      )
      return {
        "content": content,
        "content_type": "application/json",
        "exported_at": exported_at,
        "filename": f"{base_filename}.json",
        "format": "json",
        "record_count": len(serialized_items),
      }
    buffer = io.StringIO()
    fieldnames = (
      "audit_id",
      "alias_id",
      "action",
      "template_key",
      "template_label",
      "redaction_policy",
      "retention_policy",
      "source_tab_id",
      "source_tab_label",
      "detail",
      "recorded_at",
      "expires_at",
      "alias_created_at",
      "alias_expires_at",
      "alias_revoked_at",
    )
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for item in serialized_items:
      writer.writerow({fieldname: item.get(fieldname) for fieldname in fieldnames})
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": exported_at,
      "filename": f"{base_filename}.csv",
      "format": "csv",
      "record_count": len(serialized_items),
    }

  def download_replay_intent_alias_audit_export_job(
    self,
    job_id: str,
  ) -> dict[str, Any]:
    record = self.get_replay_intent_alias_audit_export_job(job_id)
    artifact_content = record.content
    if record.artifact_id:
      artifact_record = self.get_replay_intent_alias_audit_export_artifact(record.artifact_id)
      artifact_content = artifact_record.content
    self._record_replay_intent_alias_audit_export_job_event(record=record, action="downloaded")
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_replay_intent_alias_audit_export_job_record,
    )

    return serialize_replay_intent_alias_audit_export_job_record(
      record,
      include_content=True,
      content=artifact_content,
    )

  def get_provider_provenance_export_analytics(
    self,
    *,
    focus_key: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    provider_label: str | None = None,
    vendor_field: str | None = None,
    market_data_provider: str | None = None,
    venue: str | None = None,
    requested_by_tab_id: str | None = None,
    status: str | None = None,
    search: str | None = None,
    result_limit: int = 12,
    window_days: int = 14,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_export_job_record,
    )

    self._prune_provider_provenance_export_artifact_records()
    self._prune_provider_provenance_export_job_records()
    self._prune_provider_provenance_export_job_audit_records()
    records = self._filter_provider_provenance_export_job_records(
      focus_key=focus_key,
      symbol=symbol,
      timeframe=timeframe,
      provider_label=provider_label,
      vendor_field=vendor_field,
      market_data_provider=market_data_provider,
      venue=venue,
      requested_by_tab_id=requested_by_tab_id,
      status=status,
      search=search,
    )
    normalized_result_limit = max(1, min(result_limit, 50))
    matching_job_ids = {record.job_id for record in records}
    audit_records = tuple(
      audit_record
      for audit_record in self._list_provider_provenance_export_job_audit_records()
      if audit_record.job_id in matching_job_ids
    )
    download_stats_by_job: dict[str, dict[str, Any]] = {}
    for audit_record in audit_records:
      if audit_record.action != "downloaded":
        continue
      job_stats = download_stats_by_job.setdefault(
        audit_record.job_id,
        {"download_count": 0, "last_downloaded_at": None},
      )
      job_stats["download_count"] += 1
      last_downloaded_at = job_stats["last_downloaded_at"]
      if (
        last_downloaded_at is None
        or audit_record.recorded_at > last_downloaded_at
      ):
        job_stats["last_downloaded_at"] = audit_record.recorded_at

    def build_rollup_entry(
      *,
      key: str,
      label: str,
      records_for_rollup: list[ProviderProvenanceExportJobRecord],
      extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
      download_count = sum(
        int(download_stats_by_job.get(record.job_id, {}).get("download_count", 0))
        for record in records_for_rollup
      )
      download_timestamps = [
        download_stats_by_job[record.job_id]["last_downloaded_at"]
        for record in records_for_rollup
        if record.job_id in download_stats_by_job
        and download_stats_by_job[record.job_id].get("last_downloaded_at") is not None
      ]
      exported_timestamps = [
        record.exported_at or record.created_at
        for record in records_for_rollup
      ]
      provider_labels_for_rollup = self._normalize_provider_provenance_export_strings(
        provider
        for record in records_for_rollup
        for provider in record.provider_labels
      )
      vendor_fields_for_rollup = self._normalize_provider_provenance_export_strings(
        field
        for record in records_for_rollup
        for field in record.vendor_fields
      )
      payload = {
        "key": key,
        "label": label,
        "export_count": len(records_for_rollup),
        "result_count": sum(record.result_count for record in records_for_rollup),
        "provider_provenance_count": sum(
          record.provider_provenance_count
          for record in records_for_rollup
        ),
        "download_count": download_count,
        "focus_count": len({
          record.focus_key
          for record in records_for_rollup
          if isinstance(record.focus_key, str) and record.focus_key
        }),
        "requested_by_tab_count": len({
          record.requested_by_tab_id
          for record in records_for_rollup
          if isinstance(record.requested_by_tab_id, str) and record.requested_by_tab_id
        }),
        "provider_labels": list(provider_labels_for_rollup),
        "vendor_fields": list(vendor_fields_for_rollup),
        "last_exported_at": max(exported_timestamps).isoformat() if exported_timestamps else None,
        "last_downloaded_at": max(download_timestamps).isoformat() if download_timestamps else None,
      }
      if extra:
        payload.update(extra)
      return payload

    provider_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    vendor_field_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    focus_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    requester_rollups: dict[str, list[ProviderProvenanceExportJobRecord]] = {}
    for record in records:
      for provider in record.provider_labels:
        provider_rollups.setdefault(provider, []).append(record)
      for field_name in record.vendor_fields:
        vendor_field_rollups.setdefault(field_name, []).append(record)
      focus_rollups.setdefault(record.focus_key or "unknown_focus", []).append(record)
      requester_rollups.setdefault(
        record.requested_by_tab_id or "unknown_requester",
        [],
      ).append(record)

    focus_items = [
      build_rollup_entry(
        key=focus_key_value,
        label=records_for_rollup[0].focus_label or focus_key_value,
        records_for_rollup=records_for_rollup,
        extra={
          "symbol": records_for_rollup[0].symbol,
          "timeframe": records_for_rollup[0].timeframe,
          "market_data_provider": records_for_rollup[0].market_data_provider,
          "venue": records_for_rollup[0].venue,
        },
      )
      for focus_key_value, records_for_rollup in focus_rollups.items()
    ]
    provider_items = [
      build_rollup_entry(
        key=provider_value,
        label=provider_value,
        records_for_rollup=records_for_rollup,
      )
      for provider_value, records_for_rollup in provider_rollups.items()
    ]
    vendor_field_items = [
      build_rollup_entry(
        key=field_value,
        label=field_value,
        records_for_rollup=records_for_rollup,
      )
      for field_value, records_for_rollup in vendor_field_rollups.items()
    ]
    requester_items = [
      build_rollup_entry(
        key=requester_value,
        label=(
          records_for_rollup[0].requested_by_tab_label
          or records_for_rollup[0].requested_by_tab_id
          or requester_value
        ),
        records_for_rollup=records_for_rollup,
      )
      for requester_value, records_for_rollup in requester_rollups.items()
    ]

    def sort_rollup_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
      return sorted(
        items,
        key=lambda item: (
          int(item["provider_provenance_count"]),
          int(item["export_count"]),
          item["label"],
        ),
        reverse=True,
      )

    all_provider_labels = self._normalize_provider_provenance_export_strings(
      provider
      for record in records
      for provider in record.provider_labels
    )
    all_vendor_fields = self._normalize_provider_provenance_export_strings(
      field
      for record in records
      for field in record.vendor_fields
    )
    all_market_data_providers = self._normalize_provider_provenance_export_strings(
      record.market_data_provider
      for record in records
    )
    all_venues = self._normalize_provider_provenance_export_strings(record.venue for record in records)
    all_timeframes = self._normalize_provider_provenance_export_strings(record.timeframe for record in records)
    all_requested_by_tab_ids = self._normalize_provider_provenance_export_strings(
      record.requested_by_tab_id
      for record in records
    )
    all_statuses = self._normalize_provider_provenance_export_strings(record.status for record in records)

    recent_exports = list(records[:normalized_result_limit])
    time_series = self._build_provider_provenance_export_time_series(
      records=records,
      audit_records=audit_records,
      window_days=window_days,
      now=self._clock(),
    )
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_export_job_record,
    )

    return {
      "generated_at": self._clock().isoformat(),
      "query": {
        "focus_key": focus_key,
        "symbol": symbol,
        "timeframe": timeframe,
        "provider_label": provider_label,
        "vendor_field": vendor_field,
        "market_data_provider": market_data_provider,
        "venue": venue,
        "requested_by_tab_id": requested_by_tab_id,
        "status": status,
        "search": search,
        "result_limit": normalized_result_limit,
        "window_days": time_series["window_days"],
      },
      "totals": {
        "export_count": len(records),
        "result_count": sum(record.result_count for record in records),
        "provider_provenance_count": sum(
          record.provider_provenance_count
          for record in records
        ),
        "download_count": sum(
          int(job_stats.get("download_count", 0))
          for job_stats in download_stats_by_job.values()
        ),
        "unique_focus_count": len({
          record.focus_key
          for record in records
          if isinstance(record.focus_key, str) and record.focus_key
        }),
        "provider_label_count": len(all_provider_labels),
        "vendor_field_count": len(all_vendor_fields),
        "market_data_provider_count": len(all_market_data_providers),
        "requester_count": len(all_requested_by_tab_ids),
      },
      "available_filters": {
        "provider_labels": list(all_provider_labels),
        "vendor_fields": list(all_vendor_fields),
        "market_data_providers": list(all_market_data_providers),
        "venues": list(all_venues),
        "timeframes": list(all_timeframes),
        "requested_by_tab_ids": list(all_requested_by_tab_ids),
        "statuses": list(all_statuses),
      },
      "rollups": {
        "providers": sort_rollup_items(provider_items)[:5],
        "vendor_fields": sort_rollup_items(vendor_field_items)[:5],
        "focuses": sort_rollup_items(focus_items)[:6],
        "requesters": sort_rollup_items(requester_items)[:5],
      },
      "time_series": time_series,
      "recent_exports": [
        serialize_provider_provenance_export_job_record(record)
        for record in recent_exports
      ],
    }

  def download_provider_provenance_export_job(
    self,
    job_id: str,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    record = self.get_provider_provenance_export_job(job_id)
    artifact_content = record.content
    if record.artifact_id:
      artifact_record = self.get_provider_provenance_export_artifact(record.artifact_id)
      artifact_content = artifact_record.content
    self._record_provider_provenance_export_job_event(
      record=record,
      action="downloaded",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_export_job_record,
    )

    return serialize_provider_provenance_export_job_record(
      record,
      include_content=True,
      content=artifact_content,
    )

  @classmethod
  def _build_provider_provenance_scheduler_health_hourly_drill_down(
    cls,
    *,
    records: tuple[ProviderProvenanceSchedulerHealthRecord, ...],
    bucket_key: str | None,
    history_limit: int,
  ) -> dict[str, Any] | None:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health_record,
    )

    bucket_start = cls._resolve_provider_provenance_scheduler_bucket_start(bucket_key)
    if bucket_start is None:
      return None
    bucket_end = bucket_start + timedelta(days=1)
    selected_records = tuple(
      sorted(
        (
          record
          for record in records
          if bucket_start <= cls._normalize_provider_provenance_export_bucket_start(record.recorded_at)
          < bucket_end
        ),
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )
    normalized_history_limit = max(1, min(history_limit, 100))
    health_status_series: list[dict[str, Any]] = []
    lag_trend_series: list[dict[str, Any]] = []

    for hour_offset in range(24):
      hour_start = bucket_start + timedelta(hours=hour_offset)
      hour_end = hour_start + timedelta(hours=1)
      hour_records = tuple(
        sorted(
          (
            record
            for record in selected_records
            if hour_start <= (record.recorded_at.astimezone(UTC) if record.recorded_at.tzinfo is not None else record.recorded_at.replace(tzinfo=UTC))
            < hour_end
          ),
          key=lambda record: (record.recorded_at, record.record_id),
        )
      )
      counts_by_status = {
        "healthy": 0,
        "lagging": 0,
        "failed": 0,
        "disabled": 0,
        "starting": 0,
      }
      for record in hour_records:
        counts_by_status[record.status] = counts_by_status.get(record.status, 0) + 1
      dominant_status, dominant_count = max(
        counts_by_status.items(),
        key=lambda item: (item[1], item[0]),
      )
      latest_record = hour_records[-1] if hour_records else None
      lag_values = [max(record.max_due_lag_seconds, 0) for record in hour_records]
      due_counts = [max(record.due_report_count, 0) for record in hour_records]
      bucket_hour_key = hour_start.isoformat()
      bucket_hour_label = hour_start.strftime("%H:00")
      executed_report_count = sum(record.last_executed_count for record in hour_records)
      failure_count = sum(1 for record in hour_records if record.status == "failed")
      health_status_series.append(
        {
          "bucket_key": bucket_hour_key,
          "bucket_label": bucket_hour_label,
          "started_at": hour_start.isoformat(),
          "ended_at": hour_end.isoformat(),
          "cycle_count": len(hour_records),
          "healthy_count": counts_by_status["healthy"],
          "lagging_count": counts_by_status["lagging"],
          "failed_count": counts_by_status["failed"],
          "disabled_count": counts_by_status["disabled"],
          "starting_count": counts_by_status["starting"],
          "dominant_status": dominant_status if dominant_count > 0 else "no_data",
          "dominant_count": dominant_count,
          "latest_status": latest_record.status if latest_record is not None else "no_data",
          "latest_summary": latest_record.summary if latest_record is not None else "",
          "executed_report_count": executed_report_count,
        }
      )
      lag_trend_series.append(
        {
          "bucket_key": bucket_hour_key,
          "bucket_label": bucket_hour_label,
          "started_at": hour_start.isoformat(),
          "ended_at": hour_end.isoformat(),
          "cycle_count": len(hour_records),
          "peak_lag_seconds": max(lag_values) if lag_values else 0,
          "latest_lag_seconds": lag_values[-1] if lag_values else 0,
          "average_lag_seconds": round(sum(lag_values) / len(lag_values), 1) if lag_values else 0.0,
          "peak_due_report_count": max(due_counts) if due_counts else 0,
          "latest_due_report_count": due_counts[-1] if due_counts else 0,
          "failure_count": failure_count,
          "executed_report_count": executed_report_count,
        }
      )

    peak_cycle_bucket = max(
      health_status_series,
      key=lambda item: (
        int(item["cycle_count"]),
        int(item["failed_count"]),
        item["bucket_key"],
      ),
      default=None,
    )
    peak_lag_bucket = max(
      lag_trend_series,
      key=lambda item: (
        int(item["peak_lag_seconds"]),
        int(item["peak_due_report_count"]),
        item["bucket_key"],
      ),
      default=None,
    )
    latest_health_bucket = health_status_series[-1] if health_status_series else None
    latest_lag_bucket = lag_trend_series[-1] if lag_trend_series else None

    return {
      "bucket_key": bucket_start.date().isoformat(),
      "bucket_label": bucket_start.strftime("%b %d"),
      "bucket_size": "hour",
      "window_started_at": bucket_start.isoformat(),
      "window_ended_at": bucket_end.isoformat(),
      "total_record_count": len(selected_records),
      "history_limit": normalized_history_limit,
      "history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in selected_records[:normalized_history_limit]
      ],
      "health_status": {
        "series": health_status_series,
        "summary": {
          "peak_cycle_bucket_key": peak_cycle_bucket["bucket_key"] if peak_cycle_bucket is not None else None,
          "peak_cycle_bucket_label": peak_cycle_bucket["bucket_label"] if peak_cycle_bucket is not None else None,
          "peak_cycle_count": int(peak_cycle_bucket["cycle_count"]) if peak_cycle_bucket is not None else 0,
          "latest_bucket_key": latest_health_bucket["bucket_key"] if latest_health_bucket is not None else None,
          "latest_bucket_label": latest_health_bucket["bucket_label"] if latest_health_bucket is not None else None,
          "latest_status": latest_health_bucket["latest_status"] if latest_health_bucket is not None else "no_data",
          "latest_cycle_count": int(latest_health_bucket["cycle_count"]) if latest_health_bucket is not None else 0,
        },
      },
      "lag_trend": {
        "series": lag_trend_series,
        "summary": {
          "peak_lag_bucket_key": peak_lag_bucket["bucket_key"] if peak_lag_bucket is not None else None,
          "peak_lag_bucket_label": peak_lag_bucket["bucket_label"] if peak_lag_bucket is not None else None,
          "peak_lag_seconds": int(peak_lag_bucket["peak_lag_seconds"]) if peak_lag_bucket is not None else 0,
          "latest_bucket_key": latest_lag_bucket["bucket_key"] if latest_lag_bucket is not None else None,
          "latest_bucket_label": latest_lag_bucket["bucket_label"] if latest_lag_bucket is not None else None,
          "latest_lag_seconds": int(latest_lag_bucket["latest_lag_seconds"]) if latest_lag_bucket is not None else 0,
          "latest_due_report_count": int(latest_lag_bucket["latest_due_report_count"]) if latest_lag_bucket is not None else 0,
          "latest_failure_count": int(latest_lag_bucket["failure_count"]) if latest_lag_bucket is not None else 0,
        },
      },
    }

  def get_provider_provenance_scheduler_health_analytics(
    self,
    *,
    status: str | None = None,
    window_days: int = 14,
    history_limit: int = 12,
    drilldown_bucket_key: str | None = None,
    drilldown_history_limit: int = 24,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_record,
    )

    self._prune_provider_provenance_scheduler_health_records()
    normalized_status = self._normalize_provider_provenance_scheduler_health_status(status)
    records = tuple(
      record
      for record in self._list_provider_provenance_scheduler_health_records()
      if normalized_status is None or record.status == normalized_status
    )
    normalized_history_limit = max(1, min(history_limit, 50))
    time_series = self._build_provider_provenance_scheduler_health_time_series(
      records=records,
      window_days=window_days,
      now=self._clock(),
    )
    drill_down = self._build_provider_provenance_scheduler_health_hourly_drill_down(
      records=records,
      bucket_key=drilldown_bucket_key,
      history_limit=drilldown_history_limit,
    )
    all_statuses = tuple(
      sorted(
        {
          record.status
          for record in self._list_provider_provenance_scheduler_health_records()
          if isinstance(record.status, str) and record.status
        }
      )
    )
    current_snapshot = self.get_provider_provenance_scheduler_health()
    return {
      "generated_at": self._clock().isoformat(),
      "query": {
        "status": normalized_status,
        "window_days": time_series["window_days"],
        "history_limit": normalized_history_limit,
        "drilldown_bucket_key": (
          drill_down["bucket_key"]
          if isinstance(drill_down, dict)
          else None
        ),
        "drilldown_history_limit": max(1, min(drilldown_history_limit, 100)),
      },
      "current": serialize_provider_provenance_scheduler_health(current_snapshot),
      "totals": {
        "record_count": len(records),
        "healthy_count": sum(1 for record in records if record.status == "healthy"),
        "lagging_count": sum(1 for record in records if record.status == "lagging"),
        "failed_count": sum(1 for record in records if record.status == "failed"),
        "disabled_count": sum(1 for record in records if record.status == "disabled"),
        "starting_count": sum(1 for record in records if record.status == "starting"),
        "executed_report_count": sum(record.last_executed_count for record in records),
        "peak_lag_seconds": max((record.max_due_lag_seconds for record in records), default=0),
        "peak_due_report_count": max((record.due_report_count for record in records), default=0),
      },
      "available_filters": {
        "statuses": list(all_statuses),
      },
      "time_series": time_series,
      "drill_down": drill_down,
      "recent_history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in records[:normalized_history_limit]
      ],
    }

  def _build_provider_provenance_scheduler_occurrence_reconstruction_context(
    self,
    *,
    alert_category: str,
    detected_at: datetime,
    resolved_at: datetime | None = None,
    narrative_mode: str = "matched_status",
    history_limit: int = 25,
    drilldown_history_limit: int = 24,
    all_records: tuple[ProviderProvenanceSchedulerHealthRecord, ...] | None = None,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_category = self._normalize_provider_provenance_scheduler_alert_category(alert_category)
    normalized_narrative_mode = self._normalize_provider_provenance_scheduler_narrative_mode(
      narrative_mode,
    )
    target_status = "failed" if normalized_category == "scheduler_failure" else "lagging"
    detected_at_utc = self._normalize_provider_provenance_scheduler_export_datetime(
      detected_at,
      field_name="detected_at",
    )
    resolved_at_utc = (
      self._normalize_provider_provenance_scheduler_export_datetime(
        resolved_at,
        field_name="resolved_at",
      )
      if resolved_at is not None
      else None
    )
    if resolved_at_utc is not None and resolved_at_utc < detected_at_utc:
      raise ValueError("resolved_at must be on or after detected_at for scheduler export reconstruction.")
    if normalized_narrative_mode == "mixed_status_post_resolution" and resolved_at_utc is None:
      raise ValueError("mixed_status_post_resolution requires a resolved scheduler alert row.")
    if all_records is None:
      self._prune_provider_provenance_scheduler_health_records()
      ordered_records = tuple(
        sorted(
          self._list_provider_provenance_scheduler_health_records(),
          key=lambda record: (record.recorded_at, record.record_id),
        )
      )
    else:
      ordered_records = tuple(
        sorted(
          all_records,
          key=lambda record: (record.recorded_at, record.record_id),
        )
      )
    occurrence_window_end = resolved_at_utc or max(
      (record.recorded_at for record in ordered_records),
      default=detected_at_utc,
    )
    occurrence_records = tuple(
      record
      for record in ordered_records
      if detected_at_utc <= record.recorded_at <= occurrence_window_end
    )
    matching_records = tuple(
      record
      for record in occurrence_records
      if record.status == target_status
    )
    if not matching_records:
      raise LookupError("No scheduler health history could be reconstructed for the selected alert row.")
    latest_matching_record = max(
      matching_records,
      key=lambda record: (record.recorded_at, record.record_id),
    )
    current_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
      latest_matching_record,
    )
    normalized_history_limit = max(1, min(history_limit, 200))
    normalized_drilldown_history_limit = max(1, min(drilldown_history_limit, 100))
    occurrence_window_days = max(
      3,
      min(
        int((occurrence_window_end.date() - detected_at_utc.date()).days) + 1,
        90,
      ),
    )
    occurrence_drilldown_bucket_key = latest_matching_record.recorded_at.date().isoformat()
    recent_matching_records = tuple(
      sorted(
        matching_records,
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )
    selected_occurrence_history_payload = {
      "query": {
        "status": target_status,
        "limit": normalized_history_limit,
        "offset": 0,
      },
      "items": recent_matching_records[:normalized_history_limit],
      "total": len(matching_records),
      "returned": min(len(matching_records), normalized_history_limit),
      "has_more": len(matching_records) > normalized_history_limit,
      "next_offset": normalized_history_limit if len(matching_records) > normalized_history_limit else None,
      "previous_offset": None,
    }
    selected_occurrence_payload = {
      "status": target_status,
      "current": serialize_provider_provenance_scheduler_health(current_snapshot),
      "history_page": serialize_provider_provenance_scheduler_health_history(
        current_snapshot,
        selected_occurrence_history_payload,
      ),
      "record_count": len(matching_records),
      "window_record_count": len(occurrence_records),
    }

    export_records = matching_records
    export_status: str | None = target_status
    export_window_end = occurrence_window_end
    export_snapshot = current_snapshot
    export_window_days = occurrence_window_days
    export_drilldown_bucket_key = occurrence_drilldown_bucket_key
    next_occurrence_detected_at: datetime | None = None
    mixed_status_narrative_payload: dict[str, Any] | None = None
    post_resolution_records: tuple[ProviderProvenanceSchedulerHealthRecord, ...] = ()

    if normalized_narrative_mode == "mixed_status_post_resolution":
      next_target_status_record = next(
        (
          record
          for record in ordered_records
          if record.recorded_at > resolved_at_utc
          and record.status == target_status
        ),
        None,
      )
      next_occurrence_detected_at = (
        next_target_status_record.recorded_at
        if next_target_status_record is not None
        else None
      )
      export_records = tuple(
        record
        for record in ordered_records
        if detected_at_utc <= record.recorded_at
        and (
          next_occurrence_detected_at is None
          or record.recorded_at < next_occurrence_detected_at
        )
      )
      latest_export_record = max(
        export_records,
        key=lambda record: (record.recorded_at, record.record_id),
      )
      export_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
        latest_export_record,
      )
      export_status = None
      export_window_end = latest_export_record.recorded_at
      export_window_days = max(
        3,
        min(
          int((export_window_end.date() - detected_at_utc.date()).days) + 1,
          90,
        ),
      )
      export_drilldown_bucket_key = latest_export_record.recorded_at.date().isoformat()
      post_resolution_records = tuple(
        record
        for record in export_records
        if resolved_at_utc is not None and record.recorded_at >= resolved_at_utc
      )
      recent_post_resolution_records = tuple(
        sorted(
          post_resolution_records,
          key=lambda record: (record.recorded_at, record.record_id),
          reverse=True,
        )
      )
      post_resolution_history_payload = {
        "query": {
          "status": None,
          "limit": normalized_history_limit,
          "offset": 0,
        },
        "items": recent_post_resolution_records[:normalized_history_limit],
        "total": len(post_resolution_records),
        "returned": min(len(post_resolution_records), normalized_history_limit),
        "has_more": len(post_resolution_records) > normalized_history_limit,
        "next_offset": (
          normalized_history_limit
          if len(post_resolution_records) > normalized_history_limit
          else None
        ),
        "previous_offset": None,
      }
      mixed_status_narrative_payload = {
        "mode": "mixed_status_post_resolution",
        "window_started_at": detected_at_utc.isoformat(),
        "window_ended_at": export_window_end.isoformat(),
        "resolution_at": resolved_at_utc.isoformat(),
        "next_occurrence_detected_at": (
          next_occurrence_detected_at.isoformat()
          if next_occurrence_detected_at is not None
          else None
        ),
        "available_statuses": list(
          sorted(
            {
              record.status
              for record in export_records
              if isinstance(record.status, str) and record.status
            }
          )
        ),
        "latest_status": latest_export_record.status,
        "latest_summary": latest_export_record.summary,
        "current": serialize_provider_provenance_scheduler_health(export_snapshot),
        "selected_occurrence": selected_occurrence_payload,
        "status_sequence": list(
          self._build_provider_provenance_scheduler_status_narrative_segments(
            records=export_records,
            resolution_at=resolved_at_utc,
          )
        ),
        "post_resolution_history": serialize_provider_provenance_scheduler_health_history(
          export_snapshot,
          post_resolution_history_payload,
        ),
      }

    time_series = self._build_provider_provenance_scheduler_health_time_series(
      records=export_records,
      window_days=export_window_days,
      now=export_window_end,
    )
    drill_down = self._build_provider_provenance_scheduler_health_hourly_drill_down(
      records=export_records,
      bucket_key=export_drilldown_bucket_key,
      history_limit=normalized_drilldown_history_limit,
    )
    all_statuses = tuple(sorted({record.status for record in export_records if record.status}))
    history_payload = {
      "query": {
        "status": export_status,
        "limit": normalized_history_limit,
        "offset": 0,
      },
      "items": tuple(
        sorted(
          export_records,
          key=lambda record: (record.recorded_at, record.record_id),
          reverse=True,
        )
      )[:normalized_history_limit],
      "total": len(export_records),
      "returned": min(len(export_records), normalized_history_limit),
      "has_more": len(export_records) > normalized_history_limit,
      "next_offset": normalized_history_limit if len(export_records) > normalized_history_limit else None,
      "previous_offset": None,
    }
    analytics_payload = {
      "query": {
        "status": export_status,
        "window_days": time_series["window_days"],
        "history_limit": min(normalized_history_limit, 50),
        "drilldown_bucket_key": (
          drill_down["bucket_key"]
          if isinstance(drill_down, dict)
          else None
        ),
        "drilldown_history_limit": normalized_drilldown_history_limit,
        "reconstruction_mode": "resolved_alert_row",
        "narrative_mode": normalized_narrative_mode,
        "alert_category": normalized_category,
        "occurrence_status": target_status,
        "alert_detected_at": detected_at_utc.isoformat(),
        "alert_resolved_at": occurrence_window_end.isoformat(),
        "narrative_window_ended_at": export_window_end.isoformat(),
        "next_occurrence_detected_at": (
          next_occurrence_detected_at.isoformat()
          if next_occurrence_detected_at is not None
          else None
        ),
      },
      "current": serialize_provider_provenance_scheduler_health(export_snapshot),
      "totals": {
        "record_count": len(export_records),
        "healthy_count": sum(1 for record in export_records if record.status == "healthy"),
        "lagging_count": sum(1 for record in export_records if record.status == "lagging"),
        "failed_count": sum(1 for record in export_records if record.status == "failed"),
        "disabled_count": sum(1 for record in export_records if record.status == "disabled"),
        "starting_count": sum(1 for record in export_records if record.status == "starting"),
        "executed_report_count": sum(record.last_executed_count for record in export_records),
        "peak_lag_seconds": max((record.max_due_lag_seconds for record in export_records), default=0),
        "peak_due_report_count": max((record.due_report_count for record in export_records), default=0),
      },
      "available_filters": {
        "statuses": list(all_statuses),
      },
      "time_series": time_series,
      "drill_down": drill_down,
      "recent_history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in history_payload["items"][:min(normalized_history_limit, 50)]
      ],
    }
    reconstruction_payload = {
      "mode": "resolved_alert_row",
      "narrative_mode": normalized_narrative_mode,
      "alert_category": normalized_category,
      "alert_status": target_status,
      "alert_detected_at": detected_at_utc.isoformat(),
      "alert_resolved_at": occurrence_window_end.isoformat(),
      "matched_record_count": len(matching_records),
      "occurrence_window_record_count": len(occurrence_records),
      "window_record_count": len(export_records),
      "current_record_id": (
        history_payload["items"][0].record_id
        if history_payload["items"]
        else latest_matching_record.record_id
      ),
      "latest_window_status": (
        history_payload["items"][0].status
        if history_payload["items"]
        else target_status
      ),
      "next_occurrence_detected_at": (
        next_occurrence_detected_at.isoformat()
        if next_occurrence_detected_at is not None
        else None
      ),
      "selected_occurrence_record_count": len(matching_records),
    }
    return {
      "normalized_category": normalized_category,
      "normalized_narrative_mode": normalized_narrative_mode,
      "target_status": target_status,
      "detected_at": detected_at_utc,
      "resolved_at": resolved_at_utc,
      "occurrence_window_end": occurrence_window_end,
      "occurrence_records": occurrence_records,
      "matching_records": matching_records,
      "selected_occurrence_payload": selected_occurrence_payload,
      "export_records": export_records,
      "export_status": export_status,
      "export_window_end": export_window_end,
      "export_snapshot": export_snapshot,
      "next_occurrence_detected_at": next_occurrence_detected_at,
      "mixed_status_narrative_payload": mixed_status_narrative_payload,
      "post_resolution_records": post_resolution_records,
      "history_payload": history_payload,
      "analytics_payload": analytics_payload,
      "reconstruction_payload": reconstruction_payload,
    }

  def reconstruct_provider_provenance_scheduler_health_export(
    self,
    *,
    alert_category: str,
    detected_at: datetime,
    resolved_at: datetime | None = None,
    narrative_mode: str = "matched_status",
    export_format: str = "json",
    history_limit: int = 25,
    drilldown_history_limit: int = 24,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported provider provenance scheduler health export format.")
    context = self._build_provider_provenance_scheduler_occurrence_reconstruction_context(
      alert_category=alert_category,
      detected_at=detected_at,
      resolved_at=resolved_at,
      narrative_mode=narrative_mode,
      history_limit=history_limit,
      drilldown_history_limit=drilldown_history_limit,
    )
    normalized_category = context["normalized_category"]
    normalized_narrative_mode = context["normalized_narrative_mode"]
    resolved_at_utc = context["resolved_at"]
    history_payload = context["history_payload"]
    export_snapshot = context["export_snapshot"]
    reconstruction_payload = context["reconstruction_payload"]
    analytics_payload = {
      "generated_at": self._clock().isoformat(),
      **context["analytics_payload"],
    }
    mixed_status_narrative_payload = context["mixed_status_narrative_payload"]
    selected_occurrence_payload = context["selected_occurrence_payload"]
    if normalized_format == "json":
      payload: dict[str, Any] = {
        "export_scope": "provider_provenance_scheduler_health",
        "exported_at": analytics_payload["generated_at"],
        "query": analytics_payload["query"],
        "reconstruction": reconstruction_payload,
        "current": analytics_payload["current"],
        "history_page": serialize_provider_provenance_scheduler_health_history(
          export_snapshot,
          history_payload,
        ),
        "analytics": analytics_payload,
      }
      if mixed_status_narrative_payload is not None:
        payload["mixed_status_narrative"] = mixed_status_narrative_payload
        payload["selected_occurrence"] = selected_occurrence_payload
      content = json.dumps(payload, indent=2, sort_keys=True)
      return {
        "content": content,
        "content_type": "application/json; charset=utf-8",
        "exported_at": analytics_payload["generated_at"],
        "filename": f"provider-provenance-scheduler-history-{normalized_category}.json",
        "format": "json",
        "record_count": history_payload["returned"],
        "total_count": history_payload["total"],
      }
    buffer = io.StringIO()
    fieldnames = (
      "record_id",
      "recorded_at",
      "status",
      "summary",
      "cycle_count",
      "last_executed_count",
      "total_executed_count",
      "due_report_count",
      "max_due_lag_seconds",
      "last_error",
      "source_tab_id",
      "source_tab_label",
      "narrative_phase",
      "issues",
    )
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for item in history_payload["items"]:
      serialized = serialize_provider_provenance_scheduler_health_record(item)
      writer.writerow(
        {
          "record_id": serialized["record_id"],
          "recorded_at": serialized["recorded_at"],
          "status": serialized["status"],
          "summary": serialized["summary"],
          "cycle_count": serialized["cycle_count"],
          "last_executed_count": serialized["last_executed_count"],
          "total_executed_count": serialized["total_executed_count"],
          "due_report_count": serialized["due_report_count"],
          "max_due_lag_seconds": serialized["max_due_lag_seconds"],
          "last_error": serialized["last_error"],
          "source_tab_id": serialized["source_tab_id"],
          "source_tab_label": serialized["source_tab_label"],
          "narrative_phase": (
            self._build_provider_provenance_scheduler_narrative_phase(
              record=item,
              resolution_at=resolved_at_utc,
            )
            if normalized_narrative_mode == "mixed_status_post_resolution"
            else ""
          ),
          "issues": " | ".join(serialized["issues"]),
        }
      )
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": analytics_payload["generated_at"],
      "filename": f"provider-provenance-scheduler-history-{normalized_category}.csv",
      "format": "csv",
      "record_count": history_payload["returned"],
      "total_count": history_payload["total"],
    }

  def export_provider_provenance_scheduler_stitched_narrative_report(
    self,
    *,
    category: str | None = None,
    status: str | None = None,
    narrative_facet: str | None = None,
    search: str | None = None,
    offset: int = 0,
    occurrence_limit: int = 8,
    history_limit: int = 25,
    drilldown_history_limit: int = 24,
    export_format: str = "json",
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported provider provenance scheduler stitched narrative export format.")
    normalized_category = self._normalize_provider_provenance_scheduler_alert_history_category(category)
    normalized_status = self._normalize_provider_provenance_scheduler_alert_history_status(status)
    normalized_narrative_facet = self._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
      narrative_facet
    )
    normalized_occurrence_limit = max(1, min(occurrence_limit, 50))
    normalized_offset = max(offset, 0)
    normalized_history_limit = max(1, min(history_limit, 200))
    normalized_drilldown_history_limit = max(1, min(drilldown_history_limit, 100))
    alert_history_payload = self.get_provider_provenance_scheduler_alert_history_page(
      category=normalized_category,
      status=normalized_status,
      narrative_facet=normalized_narrative_facet,
      search=search,
      limit=normalized_occurrence_limit,
      offset=normalized_offset,
    )
    selected_occurrences = tuple(alert_history_payload["items"])
    if not selected_occurrences:
      raise LookupError("No scheduler alert occurrences match the selected stitched narrative report filters.")
    self._prune_provider_provenance_scheduler_health_records()
    all_records = tuple(
      sorted(
        self._list_provider_provenance_scheduler_health_records(),
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    occurrence_payloads: list[dict[str, Any]] = []
    stitched_segments: list[dict[str, Any]] = []
    stitched_records_by_id: dict[str, ProviderProvenanceSchedulerHealthRecord] = {}
    flattened_rows: list[dict[str, Any]] = []
    for occurrence_index, occurrence in enumerate(selected_occurrences, start=1):
      alert = occurrence["alert"]
      narrative = occurrence["narrative"]
      occurrence_context = self._build_provider_provenance_scheduler_occurrence_reconstruction_context(
        alert_category=alert.category,
        detected_at=alert.detected_at,
        resolved_at=alert.resolved_at,
        narrative_mode=(
          narrative.get("narrative_mode")
          if isinstance(narrative.get("narrative_mode"), str)
          else ("mixed_status_post_resolution" if alert.status == "resolved" else "matched_status")
        ),
        history_limit=normalized_history_limit,
        drilldown_history_limit=normalized_drilldown_history_limit,
        all_records=all_records,
      )
      occurrence_records = occurrence_context["export_records"]
      for record in occurrence_records:
        stitched_records_by_id.setdefault(record.record_id, record)
        flattened_rows.append(
          {
            "occurrence": occurrence,
            "context": occurrence_context,
            "record": record,
          }
        )
      occurrence_segments = self._build_provider_provenance_scheduler_status_narrative_segments(
        records=occurrence_records,
        resolution_at=occurrence_context["resolved_at"],
      )
      for segment_index, segment in enumerate(occurrence_segments, start=1):
        stitched_segments.append(
          {
            "stitch_index": len(stitched_segments) + 1,
            "occurrence_index": occurrence_index,
            "segment_index": segment_index,
            "occurrence_id": alert.occurrence_id,
            "category": alert.category,
            "occurrence_status": alert.status,
            "summary": alert.summary,
            "detected_at": alert.detected_at.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else None,
            "narrative_mode": occurrence_context["normalized_narrative_mode"],
            **segment,
          }
        )
      occurrence_payloads.append(
        {
          "occurrence_id": alert.occurrence_id,
          "category": alert.category,
          "status": alert.status,
          "severity": alert.severity,
          "summary": alert.summary,
          "detail": alert.detail,
          "detected_at": alert.detected_at.isoformat(),
          "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else None,
          "timeline_key": alert.timeline_key,
          "timeline_position": alert.timeline_position,
          "timeline_total": alert.timeline_total,
          "delivery_targets": list(alert.delivery_targets),
          "narrative": {
            "facet": narrative.get("facet"),
            "facet_flags": list(narrative.get("facet_flags", ())),
            "narrative_mode": occurrence_context["normalized_narrative_mode"],
            "can_reconstruct_narrative": bool(narrative.get("can_reconstruct_narrative")),
            "has_post_resolution_history": bool(narrative.get("has_post_resolution_history")),
            "occurrence_record_count": int(narrative.get("occurrence_record_count", 0)),
            "post_resolution_record_count": int(narrative.get("post_resolution_record_count", 0)),
            "status_sequence": list(narrative.get("status_sequence", ())),
            "post_resolution_status_sequence": list(
              narrative.get("post_resolution_status_sequence", ())
            ),
            "narrative_window_ended_at": (
              narrative.get("narrative_window_ended_at").isoformat()
              if isinstance(narrative.get("narrative_window_ended_at"), datetime)
              else narrative.get("narrative_window_ended_at")
            ),
            "next_occurrence_detected_at": (
              narrative.get("next_occurrence_detected_at").isoformat()
              if isinstance(narrative.get("next_occurrence_detected_at"), datetime)
              else narrative.get("next_occurrence_detected_at")
            ),
          },
          "search_match": deepcopy(occurrence.get("search_match")),
          "retrieval_cluster": deepcopy(occurrence.get("retrieval_cluster")),
          "window_started_at": occurrence_context["detected_at"].isoformat(),
          "window_ended_at": occurrence_context["export_window_end"].isoformat(),
          "record_count": len(occurrence_records),
          "current": occurrence_context["analytics_payload"]["current"],
          "selected_occurrence": occurrence_context["selected_occurrence_payload"],
          "status_sequence": list(occurrence_segments),
          "next_occurrence_detected_at": (
            occurrence_context["next_occurrence_detected_at"].isoformat()
            if occurrence_context["next_occurrence_detected_at"] is not None
            else None
          ),
          "peak_lag_seconds": max(
            (record.max_due_lag_seconds for record in occurrence_records),
            default=0,
          ),
          "peak_due_report_count": max(
            (record.due_report_count for record in occurrence_records),
            default=0,
          ),
        }
      )
    stitched_records = tuple(
      sorted(
        stitched_records_by_id.values(),
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    latest_stitched_record = max(
      stitched_records,
      key=lambda record: (record.recorded_at, record.record_id),
    )
    stitched_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
      latest_stitched_record,
    )
    stitched_window_started_at = min(
      context["detected_at"] for context in (row["context"] for row in flattened_rows)
    )
    stitched_window_ended_at = latest_stitched_record.recorded_at
    stitched_window_days = max(
      3,
      min(
        int((stitched_window_ended_at.date() - stitched_window_started_at.date()).days) + 1,
        90,
      ),
    )
    stitched_history_payload = {
      "query": {
        "status": None,
        "limit": normalized_history_limit,
        "offset": 0,
      },
      "items": tuple(
        sorted(
          stitched_records,
          key=lambda record: (record.recorded_at, record.record_id),
          reverse=True,
        )
      )[:normalized_history_limit],
      "total": len(stitched_records),
      "returned": min(len(stitched_records), normalized_history_limit),
      "has_more": len(stitched_records) > normalized_history_limit,
      "next_offset": (
        normalized_history_limit if len(stitched_records) > normalized_history_limit else None
      ),
      "previous_offset": None,
    }
    stitched_time_series = self._build_provider_provenance_scheduler_health_time_series(
      records=stitched_records,
      window_days=stitched_window_days,
      now=stitched_window_ended_at,
    )
    stitched_drilldown = self._build_provider_provenance_scheduler_health_hourly_drill_down(
      records=stitched_records,
      bucket_key=latest_stitched_record.recorded_at.date().isoformat(),
      history_limit=normalized_drilldown_history_limit,
    )
    by_category: dict[str, dict[str, Any]] = {}
    for occurrence in occurrence_payloads:
      category_key = occurrence["category"]
      category_entry = by_category.setdefault(
        category_key,
        {
          "category": category_key,
          "occurrence_count": 0,
          "active_count": 0,
          "resolved_count": 0,
          "record_count": 0,
          "peak_lag_seconds": 0,
          "peak_due_report_count": 0,
        },
      )
      category_entry["occurrence_count"] += 1
      category_entry["active_count"] += 1 if occurrence["status"] == "active" else 0
      category_entry["resolved_count"] += 1 if occurrence["status"] == "resolved" else 0
      category_entry["record_count"] += int(occurrence["record_count"])
      category_entry["peak_lag_seconds"] = max(
        category_entry["peak_lag_seconds"],
        int(occurrence["peak_lag_seconds"]),
      )
      category_entry["peak_due_report_count"] = max(
        category_entry["peak_due_report_count"],
        int(occurrence["peak_due_report_count"]),
      )
    exported_at = self._clock().isoformat()
    analytics_payload = {
      "generated_at": exported_at,
      "query": {
        "status": normalized_status,
        "window_days": stitched_time_series["window_days"],
        "history_limit": min(normalized_history_limit, 50),
        "drilldown_bucket_key": (
          stitched_drilldown["bucket_key"]
          if isinstance(stitched_drilldown, dict)
          else None
        ),
        "drilldown_history_limit": normalized_drilldown_history_limit,
        "reconstruction_mode": "stitched_occurrence_report",
        "narrative_mode": "stitched_multi_occurrence",
        "alert_category": normalized_category,
        "narrative_facet": normalized_narrative_facet or "all_occurrences",
        "search": search.strip() if isinstance(search, str) and search.strip() else None,
        "occurrence_limit": normalized_occurrence_limit,
        "occurrence_offset": normalized_offset,
        "selected_occurrence_count": len(occurrence_payloads),
        "stitched_window_started_at": stitched_window_started_at.isoformat(),
        "stitched_window_ended_at": stitched_window_ended_at.isoformat(),
      },
      "current": serialize_provider_provenance_scheduler_health(stitched_snapshot),
      "totals": {
        "record_count": len(stitched_records),
        "healthy_count": sum(1 for record in stitched_records if record.status == "healthy"),
        "lagging_count": sum(1 for record in stitched_records if record.status == "lagging"),
        "failed_count": sum(1 for record in stitched_records if record.status == "failed"),
        "disabled_count": sum(1 for record in stitched_records if record.status == "disabled"),
        "starting_count": sum(1 for record in stitched_records if record.status == "starting"),
        "executed_report_count": sum(record.last_executed_count for record in stitched_records),
        "peak_lag_seconds": max((record.max_due_lag_seconds for record in stitched_records), default=0),
        "peak_due_report_count": max((record.due_report_count for record in stitched_records), default=0),
      },
      "available_filters": {
        "statuses": sorted({record.status for record in stitched_records if record.status}),
        "categories": sorted({occurrence["category"] for occurrence in occurrence_payloads}),
      },
      "time_series": stitched_time_series,
      "drill_down": stitched_drilldown,
      "recent_history": [
        serialize_provider_provenance_scheduler_health_record(record)
        for record in stitched_history_payload["items"][:min(normalized_history_limit, 50)]
      ],
    }
    stitched_report_payload = {
      "mode": "stitched_multi_occurrence",
      "summary": {
        "occurrence_count": len(occurrence_payloads),
        "active_count": sum(1 for occurrence in occurrence_payloads if occurrence["status"] == "active"),
        "resolved_count": sum(1 for occurrence in occurrence_payloads if occurrence["status"] == "resolved"),
        "segment_count": len(stitched_segments),
        "record_count": len(stitched_records),
        "categories": sorted({occurrence["category"] for occurrence in occurrence_payloads}),
        "statuses": sorted({occurrence["status"] for occurrence in occurrence_payloads}),
        "narrative_facets": sorted(
          {
            occurrence["narrative"]["facet"]
            for occurrence in occurrence_payloads
            if isinstance(occurrence["narrative"]["facet"], str)
            and occurrence["narrative"]["facet"]
          }
        ),
        "stitched_window_started_at": stitched_window_started_at.isoformat(),
        "stitched_window_ended_at": stitched_window_ended_at.isoformat(),
        "peak_lag_seconds": analytics_payload["totals"]["peak_lag_seconds"],
        "peak_due_report_count": analytics_payload["totals"]["peak_due_report_count"],
        "executed_report_count": analytics_payload["totals"]["executed_report_count"],
      },
      "selected_occurrence_page": {
        "query": alert_history_payload["query"],
        "total": alert_history_payload["total"],
        "returned": alert_history_payload["returned"],
        "has_more": alert_history_payload["has_more"],
        "next_offset": alert_history_payload["next_offset"],
        "previous_offset": alert_history_payload["previous_offset"],
      },
      "search_summary": alert_history_payload.get("search_summary"),
      "search_analytics": alert_history_payload.get("search_analytics"),
      "retrieval_clusters": alert_history_payload.get("retrieval_clusters"),
      "occurrences": occurrence_payloads,
      "stitched_status_sequence": stitched_segments,
      "by_category": tuple(by_category[key] for key in sorted(by_category)),
    }
    if normalized_format == "json":
      payload = {
        "export_scope": "provider_provenance_scheduler_health",
        "exported_at": exported_at,
        "query": analytics_payload["query"],
        "current": analytics_payload["current"],
        "history_page": serialize_provider_provenance_scheduler_health_history(
          stitched_snapshot,
          stitched_history_payload,
        ),
        "analytics": analytics_payload,
        "stitched_occurrence_report": stitched_report_payload,
      }
      content = json.dumps(payload, indent=2, sort_keys=True)
      category_label = normalized_category or "all"
      return {
        "content": content,
        "content_type": "application/json; charset=utf-8",
        "exported_at": exported_at,
        "filename": f"provider-provenance-scheduler-narrative-report-{category_label}.json",
        "format": "json",
        "record_count": stitched_history_payload["returned"],
        "total_count": stitched_history_payload["total"],
      }
    buffer = io.StringIO()
    fieldnames = (
      "occurrence_id",
      "occurrence_category",
      "occurrence_status",
      "occurrence_detected_at",
      "occurrence_resolved_at",
      "narrative_mode",
      "retrieval_cluster_id",
      "retrieval_cluster_label",
      "record_id",
      "recorded_at",
      "status",
      "summary",
      "cycle_count",
      "last_executed_count",
      "total_executed_count",
      "due_report_count",
      "max_due_lag_seconds",
      "last_error",
      "source_tab_id",
      "source_tab_label",
      "narrative_phase",
      "issues",
    )
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in flattened_rows:
      alert = row["occurrence"]["alert"]
      occurrence_context = row["context"]
      record = row["record"]
      retrieval_cluster = row["occurrence"].get("retrieval_cluster", {})
      serialized = serialize_provider_provenance_scheduler_health_record(record)
      writer.writerow(
        {
          "occurrence_id": alert.occurrence_id,
          "occurrence_category": alert.category,
          "occurrence_status": alert.status,
          "occurrence_detected_at": alert.detected_at.isoformat(),
          "occurrence_resolved_at": alert.resolved_at.isoformat() if alert.resolved_at is not None else "",
          "narrative_mode": occurrence_context["normalized_narrative_mode"],
          "retrieval_cluster_id": retrieval_cluster.get("cluster_id", ""),
          "retrieval_cluster_label": retrieval_cluster.get("label", ""),
          "record_id": serialized["record_id"],
          "recorded_at": serialized["recorded_at"],
          "status": serialized["status"],
          "summary": serialized["summary"],
          "cycle_count": serialized["cycle_count"],
          "last_executed_count": serialized["last_executed_count"],
          "total_executed_count": serialized["total_executed_count"],
          "due_report_count": serialized["due_report_count"],
          "max_due_lag_seconds": serialized["max_due_lag_seconds"],
          "last_error": serialized["last_error"],
          "source_tab_id": serialized["source_tab_id"],
          "source_tab_label": serialized["source_tab_label"],
          "narrative_phase": self._build_provider_provenance_scheduler_narrative_phase(
            record=record,
            resolution_at=occurrence_context["resolved_at"],
          ),
          "issues": " | ".join(serialized["issues"]),
        }
      )
    category_label = normalized_category or "all"
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": exported_at,
      "filename": f"provider-provenance-scheduler-narrative-report-{category_label}.csv",
      "format": "csv",
      "record_count": len(flattened_rows),
      "total_count": len(flattened_rows),
    }

  def export_provider_provenance_scheduler_health(
    self,
    *,
    export_format: str = "json",
    status: str | None = None,
    window_days: int = 14,
    history_limit: int = 12,
    drilldown_bucket_key: str | None = None,
    drilldown_history_limit: int = 24,
    offset: int = 0,
    limit: int = 25,
  ) -> dict[str, Any]:
    from akra_trader.application_flows.provider_provenance.serialization import (
      serialize_provider_provenance_scheduler_health,
      serialize_provider_provenance_scheduler_health_history,
      serialize_provider_provenance_scheduler_health_record,
    )

    normalized_format = export_format.strip().lower() if isinstance(export_format, str) else "json"
    if normalized_format not in {"json", "csv"}:
      raise ValueError("Unsupported provider provenance scheduler health export format.")
    analytics_payload = self.get_provider_provenance_scheduler_health_analytics(
      status=status,
      window_days=window_days,
      history_limit=history_limit,
      drilldown_bucket_key=drilldown_bucket_key,
      drilldown_history_limit=drilldown_history_limit,
    )
    history_payload = self.get_provider_provenance_scheduler_health_history_page(
      status=status,
      limit=limit,
      offset=offset,
    )
    current_snapshot = self.get_provider_provenance_scheduler_health()
    exported_at = self._clock().isoformat()
    if normalized_format == "json":
      content = json.dumps(
        {
          "export_scope": "provider_provenance_scheduler_health",
          "exported_at": exported_at,
          "query": {
            "status": self._normalize_provider_provenance_scheduler_health_status(status),
            "window_days": analytics_payload["query"]["window_days"],
            "history_limit": analytics_payload["query"]["history_limit"],
            "drilldown_bucket_key": analytics_payload["query"]["drilldown_bucket_key"],
            "drilldown_history_limit": analytics_payload["query"]["drilldown_history_limit"],
            "offset": history_payload["query"]["offset"],
            "limit": history_payload["query"]["limit"],
          },
          "current": serialize_provider_provenance_scheduler_health(current_snapshot),
          "history_page": serialize_provider_provenance_scheduler_health_history(
            current_snapshot,
            history_payload,
          ),
          "analytics": analytics_payload,
        },
        indent=2,
        sort_keys=True,
      )
      return {
        "content": content,
        "content_type": "application/json; charset=utf-8",
        "exported_at": exported_at,
        "filename": "provider-provenance-scheduler-health.json",
        "format": "json",
        "record_count": history_payload["returned"],
        "total_count": history_payload["total"],
      }
    buffer = io.StringIO()
    fieldnames = (
      "record_id",
      "recorded_at",
      "status",
      "summary",
      "cycle_count",
      "last_executed_count",
      "total_executed_count",
      "due_report_count",
      "max_due_lag_seconds",
      "last_error",
      "source_tab_id",
      "source_tab_label",
      "issues",
    )
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for item in history_payload["items"]:
      serialized = serialize_provider_provenance_scheduler_health_record(item)
      writer.writerow(
        {
          "record_id": serialized["record_id"],
          "recorded_at": serialized["recorded_at"],
          "status": serialized["status"],
          "summary": serialized["summary"],
          "cycle_count": serialized["cycle_count"],
          "last_executed_count": serialized["last_executed_count"],
          "total_executed_count": serialized["total_executed_count"],
          "due_report_count": serialized["due_report_count"],
          "max_due_lag_seconds": serialized["max_due_lag_seconds"],
          "last_error": serialized["last_error"],
          "source_tab_id": serialized["source_tab_id"],
          "source_tab_label": serialized["source_tab_label"],
          "issues": " | ".join(serialized["issues"]),
        }
      )
    return {
      "content": buffer.getvalue(),
      "content_type": "text/csv; charset=utf-8",
      "exported_at": exported_at,
      "filename": "provider-provenance-scheduler-health.csv",
      "format": "csv",
      "record_count": history_payload["returned"],
      "total_count": history_payload["total"],
    }

