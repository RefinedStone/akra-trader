from __future__ import annotations

import csv
from copy import deepcopy
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import hashlib
import io
import json
import math
from numbers import Number
import re
from typing import Any
from typing import Mapping
from uuid import uuid4

from akra_trader.domain.models import *  # noqa: F403


class ProviderProvenanceSchedulerNarrativeGovernanceNormalizationMixin:
  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_item_type(
    item_type: str,
  ) -> str:
    normalized = item_type.strip().lower()
    if normalized not in {
      "template",
      "registry",
      "stitched_report_view",
      "stitched_report_governance_registry",
    }:
      raise ValueError("Unsupported scheduler narrative governance item type.")
    return normalized
  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(
    item_type_scope: str | None,
  ) -> str:
    normalized = (
      item_type_scope.strip().lower()
      if isinstance(item_type_scope, str) and item_type_scope.strip()
      else "any"
    )
    if normalized not in {
      "any",
      "template",
      "registry",
      "stitched_report_view",
      "stitched_report_governance_registry",
    }:
      raise ValueError("Unsupported scheduler narrative governance policy item-type scope.")
    return normalized
  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_action_scope(
    action_scope: str | None,
  ) -> str:
    normalized = (
      action_scope.strip().lower()
      if isinstance(action_scope, str) and action_scope.strip()
      else "any"
    )
    if normalized not in {"any", "delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler narrative governance policy action scope.")
    return normalized
  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
    approval_lane: str | None,
  ) -> str:
    raw = (
      approval_lane.strip().lower()
      if isinstance(approval_lane, str) and approval_lane.strip()
      else "general"
    )
    normalized = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return normalized or "general"
  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
    approval_priority: str | None,
  ) -> str:
    normalized = (
      approval_priority.strip().lower()
      if isinstance(approval_priority, str) and approval_priority.strip()
      else "normal"
    )
    if normalized not in {"low", "normal", "high", "critical"}:
      raise ValueError("Unsupported scheduler narrative governance approval priority.")
    return normalized
  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_queue_state(
    status: str,
  ) -> str:
    normalized = status.strip().lower()
    if normalized == "previewed":
      return "pending_approval"
    if normalized == "approved":
      return "ready_to_apply"
    return "completed"
  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_queue_state_filter(
    queue_state: str | None,
  ) -> str:
    normalized = (
      queue_state.strip().lower()
      if isinstance(queue_state, str) and queue_state.strip()
      else ""
    )
    if normalized not in {"pending_approval", "ready_to_apply", "completed"}:
      raise ValueError("Unsupported scheduler narrative governance queue state.")
    return normalized
  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_plan_sort(
    sort: str | None,
  ) -> str:
    normalized = (
      sort.strip().lower()
      if isinstance(sort, str) and sort.strip()
      else "queue_priority"
    )
    if normalized not in {
      "queue_priority",
      "updated_desc",
      "updated_asc",
      "created_desc",
      "created_asc",
      "source_template_asc",
      "source_template_desc",
    }:
      raise ValueError("Unsupported scheduler narrative governance plan sort.")
    return normalized
  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_priority_rank(
    approval_priority: str,
  ) -> int:
    normalized = approval_priority.strip().lower()
    if normalized == "critical":
      return 3
    if normalized == "high":
      return 2
    if normalized == "normal":
      return 1
    return 0
  @classmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
    cls,
    payload: dict[str, Any] | None,
  ) -> dict[str, Any] | None:
    queue_view = deepcopy(payload) if isinstance(payload, dict) else {}
    if not queue_view:
      return None
    normalized: dict[str, Any] = {}
    queue_state = queue_view.get("queue_state")
    if isinstance(queue_state, str) and queue_state.strip():
      normalized["queue_state"] = cls._normalize_provider_provenance_scheduler_narrative_governance_queue_state_filter(
        queue_state
      )
    item_type = queue_view.get("item_type")
    if isinstance(item_type, str) and item_type.strip():
      normalized["item_type"] = cls._normalize_provider_provenance_scheduler_narrative_governance_item_type(
        item_type
      )
    approval_lane = queue_view.get("approval_lane")
    if isinstance(approval_lane, str) and approval_lane.strip():
      normalized["approval_lane"] = cls._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
        approval_lane
      )
    approval_priority = queue_view.get("approval_priority")
    if isinstance(approval_priority, str) and approval_priority.strip():
      normalized["approval_priority"] = cls._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
        approval_priority
      )
    for key in ("policy_template_id", "policy_catalog_id", "source_hierarchy_step_template_id"):
      value = queue_view.get(key)
      if isinstance(value, str):
        normalized[key] = value.strip() if value.strip() else ""
    source_hierarchy_step_template_name = queue_view.get("source_hierarchy_step_template_name")
    if (
      isinstance(source_hierarchy_step_template_name, str)
      and source_hierarchy_step_template_name.strip()
    ):
      normalized["source_hierarchy_step_template_name"] = (
        source_hierarchy_step_template_name.strip()
      )
    search = queue_view.get("search")
    if isinstance(search, str) and search.strip():
      normalized["search"] = search.strip()
    normalized_sort = cls._normalize_provider_provenance_scheduler_narrative_governance_plan_sort(
      queue_view.get("sort") if isinstance(queue_view.get("sort"), str) else None
    )
    if normalized or normalized_sort != "queue_priority":
      normalized["sort"] = normalized_sort
    return normalized or None
  def _normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
    self,
    hierarchy_steps: Iterable[dict[str, Any]] | None,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ...]:
    if hierarchy_steps is None:
      return ()
    resolved_steps: list[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep] = []
    for raw_step in hierarchy_steps:
      if not isinstance(raw_step, dict):
        raise ValueError("Scheduler governance hierarchy steps must be objects.")
      item_type = self._normalize_provider_provenance_scheduler_narrative_governance_item_type(
        str(raw_step.get("item_type", ""))
      )
      step_id = (
        raw_step["step_id"].strip()
        if isinstance(raw_step.get("step_id"), str) and raw_step["step_id"].strip()
        else f"hstep_{uuid4().hex[:12]}"
      )
      source_template_id = (
        raw_step["source_template_id"].strip()
        if isinstance(raw_step.get("source_template_id"), str) and raw_step["source_template_id"].strip()
        else None
      )
      source_template_name = (
        raw_step["source_template_name"].strip()
        if isinstance(raw_step.get("source_template_name"), str) and raw_step["source_template_name"].strip()
        else None
      )
      action = str(raw_step.get("action", "update")).strip().lower() or "update"
      if action != "update":
        raise ValueError("Scheduler governance policy catalog hierarchies currently support update steps only.")
      item_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
        raw_step.get("item_ids", ())
      )
      if not item_ids:
        raise ValueError("Each scheduler governance hierarchy step must target at least one item.")
      item_names: list[str] = []
      for item_id in item_ids:
        if item_type == "template":
          item_names.append(self.get_provider_provenance_scheduler_narrative_template(item_id).name)
        else:
          item_names.append(self.get_provider_provenance_scheduler_narrative_registry_entry(item_id).name)
      name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        raw_step.get("name_prefix"),
        preserve_outer_spacing=True,
      )
      name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        raw_step.get("name_suffix"),
        preserve_outer_spacing=True,
      )
      description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        raw_step.get("description_append")
      )
      query_patch = (
        deepcopy(raw_step["query_patch"])
        if isinstance(raw_step.get("query_patch"), dict) and raw_step.get("query_patch")
        else {}
      )
      layout_patch = (
        deepcopy(raw_step["layout_patch"])
        if item_type == "registry"
        and isinstance(raw_step.get("layout_patch"), dict)
        and raw_step.get("layout_patch")
        else {}
      )
      template_id = (
        raw_step["template_id"].strip()
        if isinstance(raw_step.get("template_id"), str) and raw_step["template_id"].strip()
        else None
      )
      clear_template_link = bool(raw_step.get("clear_template_link", False))
      if template_id is not None:
        self.get_provider_provenance_scheduler_narrative_template(template_id)
      if item_type == "template":
        if layout_patch:
          raise ValueError("Template hierarchy steps do not support layout patches.")
        if template_id is not None or clear_template_link:
          raise ValueError("Template hierarchy steps do not support registry template link changes.")
        if (
          name_prefix is None
          and name_suffix is None
          and description_append is None
          and not query_patch
        ):
          raise ValueError("Template hierarchy steps must capture at least one update patch.")
      else:
        if (
          name_prefix is None
          and name_suffix is None
          and description_append is None
          and not query_patch
          and not layout_patch
          and template_id is None
          and not clear_template_link
        ):
          raise ValueError("Registry hierarchy steps must capture at least one update patch.")
      resolved_steps.append(
        ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep(
          item_type=item_type,
          step_id=step_id,
          source_template_id=source_template_id,
          source_template_name=source_template_name,
          action=action,
          item_ids=item_ids,
          item_names=tuple(item_names),
          name_prefix=name_prefix,
          name_suffix=name_suffix,
          description_append=description_append,
          query_patch=query_patch,
          layout_patch=layout_patch,
          template_id=template_id,
          clear_template_link=clear_template_link,
        )
      )
    return self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
      resolved_steps
    )
  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_fingerprint(
    step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep,
    *,
    index: int,
  ) -> str:
    return hashlib.sha1(
      json.dumps(
        {
          "index": index,
          "item_type": step.item_type,
          "action": step.action,
          "source_template_id": step.source_template_id,
          "source_template_name": step.source_template_name,
          "item_ids": list(step.item_ids),
          "item_names": list(step.item_names),
          "name_prefix": step.name_prefix,
          "name_suffix": step.name_suffix,
          "description_append": step.description_append,
          "query_patch": step.query_patch,
          "layout_patch": step.layout_patch,
          "template_id": step.template_id,
          "clear_template_link": step.clear_template_link,
        },
        sort_keys=True,
        separators=(",", ":"),
      ).encode("utf-8")
    ).hexdigest()[:12]
  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
    self,
    hierarchy_steps: Iterable[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep],
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ...]:
    seen_step_ids: set[str] = set()
    resolved_steps: list[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep] = []
    for index, step in enumerate(hierarchy_steps, start=1):
      base_step_id = (
        step.step_id.strip()
        if isinstance(step.step_id, str) and step.step_id.strip()
        else f"hstep_{self._build_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_fingerprint(step, index=index)}"
      )
      step_id = base_step_id
      duplicate_index = 2
      while step_id in seen_step_ids:
        step_id = f"{base_step_id}_{duplicate_index}"
        duplicate_index += 1
      seen_step_ids.add(step_id)
      resolved_steps.append(replace(step, step_id=step_id))
    return tuple(resolved_steps)
  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    hierarchy_steps = (
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
        record.hierarchy_steps
      )
    )
    if hierarchy_steps == record.hierarchy_steps:
      return record
    return replace(record, hierarchy_steps=hierarchy_steps)
  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    hierarchy_steps = (
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
        record.hierarchy_steps
      )
    )
    if hierarchy_steps == record.hierarchy_steps:
      return record
    return replace(record, hierarchy_steps=hierarchy_steps)
  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    hierarchy_steps = (
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
        record.hierarchy_steps
      )
    )
    if hierarchy_steps == record.hierarchy_steps:
      return record
    return replace(record, hierarchy_steps=hierarchy_steps)
  def _get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
    self,
    current: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    step_id: str,
  ) -> tuple[int, ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep]:
    normalized_step_id = step_id.strip()
    if not normalized_step_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog hierarchy step not found.")
    materialized = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      current
    )
    for index, step in enumerate(materialized.hierarchy_steps):
      if step.step_id == normalized_step_id:
        return index, step
    raise LookupError("Provider provenance scheduler narrative governance policy catalog hierarchy step not found.")
  @staticmethod
  def _summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
    steps: tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ...],
  ) -> str:
    if not steps:
      return "No reusable hierarchy steps are captured."
    parts = [
      f"{step.item_type} {len(step.item_ids)}"
      for step in steps
    ]
    return f"{len(steps)} hierarchy step(s): " + ", ".join(parts)
  @staticmethod
  def format_provider_provenance_scheduler_narrative_governance_hierarchy_step_summary(
    step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep,
  ) -> str:
    item_summary = ", ".join(step.item_names or step.item_ids[:3]) if (step.item_names or step.item_ids) else "all"
    affixes: list[str] = []
    if step.name_prefix:
      affixes.append(f"prefix={step.name_prefix}")
    if step.name_suffix:
      affixes.append(f"suffix={step.name_suffix}")
    if step.description_append:
      affixes.append("description")
    if step.template_id:
      affixes.append(f"template={step.template_id}")
    if step.clear_template_link:
      affixes.append("clear-link")
    affix_summary = f" ({', '.join(affixes)})" if affixes else ""
    return (
      f"{step.item_type} {step.action} · {len(step.item_ids)} target(s)"
      f" [{item_summary}]{affix_summary}"
    )
