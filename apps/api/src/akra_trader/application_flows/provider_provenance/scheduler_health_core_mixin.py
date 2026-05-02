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


class ProviderProvenanceSchedulerHealthCoreMixin:
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
