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


class ProviderProvenanceSchedulerNarrativePolicyCatalogGovernanceMixin:
  def create_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    *,
    name: str,
    description: str = "",
    policy_template_ids: Iterable[str],
    default_policy_template_id: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    normalized_name = self._normalize_provider_provenance_workspace_name(
      name,
      field_name="scheduler narrative governance policy catalog name",
    )
    normalized_description = description.strip() if isinstance(description, str) else ""
    resolved_templates, default_template = self._resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
      policy_template_ids=policy_template_ids,
      default_policy_template_id=default_policy_template_id,
    )
    now = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord(
        catalog_id=uuid4().hex[:12],
        name=normalized_name,
        description=normalized_description,
        policy_template_ids=tuple(template.policy_template_id for template in resolved_templates),
        policy_template_names=tuple(template.name for template in resolved_templates),
        default_policy_template_id=default_template.policy_template_id,
        default_policy_template_name=default_template.name,
        item_type_scope=default_template.item_type_scope,
        action_scope=default_template.action_scope,
        approval_lane=default_template.approval_lane,
        approval_priority=default_template.approval_priority,
        guidance=default_template.guidance,
        hierarchy_steps=(),
        status="active",
        created_at=now,
        updated_at=now,
        created_by_tab_id=(
          created_by_tab_id.strip()
          if isinstance(created_by_tab_id, str) and created_by_tab_id.strip()
          else None
        ),
        created_by_tab_label=(
          created_by_tab_label.strip()
          if isinstance(created_by_tab_label, str) and created_by_tab_label.strip()
          else None
        ),
      ),
      action="created",
      reason="scheduler_narrative_governance_policy_catalog_created",
      recorded_at=now,
      actor_tab_id=created_by_tab_id,
      actor_tab_label=created_by_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_policy_catalogs(
    self,
    *,
    item_type_scope: str | None = None,
    search: str | None = None,
    limit: int = 20,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    normalized_item_type_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(item_type_scope)
      if isinstance(item_type_scope, str) and item_type_scope.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 100))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord] = []
    for raw_record in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_records():
      record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
        raw_record
      )
      if normalized_item_type_scope is not None and record.item_type_scope != normalized_item_type_scope:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.catalog_id,
          record.name,
          record.description,
          record.default_policy_template_id,
          record.default_policy_template_name,
          record.status,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.created_by_tab_id,
          record.created_by_tab_label,
          *record.policy_template_ids,
          *record.policy_template_names,
          *tuple(step.step_id for step in record.hierarchy_steps if isinstance(step.step_id, str)),
          *tuple(item_id for step in record.hierarchy_steps for item_id in step.item_ids),
          *tuple(item_name for step in record.hierarchy_steps for item_name in step.item_names),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])
  def get_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    normalized_catalog_id = catalog_id.strip()
    if not normalized_catalog_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      normalized_catalog_id
    )
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog not found.")
    return replace(
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record),
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
    )
  def update_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    policy_template_ids: Iterable[str] | None = None,
    default_policy_template_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative governance policy catalog name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = description.strip() if isinstance(description, str) else current.description
    resolved_templates, default_template = (
      self._resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
        policy_template_ids=(
          policy_template_ids if policy_template_ids is not None else current.policy_template_ids
        ),
        default_policy_template_id=(
          default_policy_template_id
          if default_policy_template_id is not None
          else current.default_policy_template_id
        ),
      )
    )
    updated_policy_template_ids = tuple(template.policy_template_id for template in resolved_templates)
    updated_policy_template_names = tuple(template.name for template in resolved_templates)
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_policy_template_ids == current.policy_template_ids
      and updated_policy_template_names == current.policy_template_names
      and default_template.policy_template_id == current.default_policy_template_id
      and default_template.name == current.default_policy_template_name
      and default_template.item_type_scope == current.item_type_scope
      and default_template.action_scope == current.action_scope
      and default_template.approval_lane == current.approval_lane
      and default_template.approval_priority == current.approval_priority
      and default_template.guidance == current.guidance
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      policy_template_ids=updated_policy_template_ids,
      policy_template_names=updated_policy_template_names,
      default_policy_template_id=default_template.policy_template_id,
      default_policy_template_name=default_template.name,
      item_type_scope=default_template.item_type_scope,
      action_scope=default_template.action_scope,
      approval_lane=default_template.approval_lane,
      approval_priority=default_template.approval_priority,
      guidance=default_template.guidance,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def delete_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions(
    self,
    catalog_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    revisions = [
      replace(
        self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
          revision
        ),
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_records()
      if revision.catalog_id == current.catalog_id
    ]
    return tuple(revisions)
  def restore_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    catalog_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    revision = self._load_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.catalog_id != current.catalog_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog revision not found.")
    revision = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision
    )
    resolved_templates, default_template = (
      self._resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
        policy_template_ids=revision.policy_template_ids,
        default_policy_template_id=revision.default_policy_template_id,
      )
    )
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      policy_template_ids=tuple(template.policy_template_id for template in resolved_templates),
      policy_template_names=tuple(template.name for template in resolved_templates),
      default_policy_template_id=default_template.policy_template_id,
      default_policy_template_name=default_template.name,
      item_type_scope=default_template.item_type_scope,
      action_scope=default_template.action_scope,
      approval_lane=default_template.approval_lane,
      approval_priority=default_template.approval_priority,
      guidance=default_template.guidance,
      hierarchy_steps=tuple(revision.hierarchy_steps),
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_audits(
    self,
    *,
    catalog_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    normalized_catalog_id = catalog_id.strip() if isinstance(catalog_id, str) and catalog_id.strip() else None
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord] = []
    for raw_record in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records():
      record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
        raw_record
      )
      if normalized_catalog_id is not None and record.catalog_id != normalized_catalog_id:
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.catalog_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.status,
          record.default_policy_template_id,
          record.default_policy_template_name,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.actor_tab_id,
          record.actor_tab_label,
          *tuple(step.step_id for step in record.hierarchy_steps if isinstance(step.step_id, str)),
          *record.policy_template_ids,
          *record.policy_template_names,
          *tuple(item_id for step in record.hierarchy_steps for item_id in step.item_ids),
          *tuple(item_name for step in record.hierarchy_steps for item_name in step.item_names),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])
  def capture_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy(
    self,
    catalog_id: str,
    *,
    hierarchy_steps: Iterable[dict[str, Any]],
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_captured",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before capturing reusable hierarchies."
      )
    resolved_steps = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      hierarchy_steps
    )
    if not resolved_steps:
      raise ValueError("Capture at least one reusable governance hierarchy step.")
    for step in resolved_steps:
      if current.item_type_scope not in {"any", step.item_type}:
        raise ValueError("Policy catalog item-type scope does not support one or more captured hierarchy steps.")
      if current.action_scope not in {"any", step.action}:
        raise ValueError("Policy catalog action scope does not support one or more captured hierarchy steps.")
    if resolved_steps == current.hierarchy_steps:
      return current
    captured_at = self._clock()
    updated = replace(
      current,
      hierarchy_steps=resolved_steps,
      updated_at=captured_at,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=updated,
      action="hierarchy_captured",
      reason=reason,
      recorded_at=captured_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def update_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
    self,
    catalog_id: str,
    step_id: str,
    *,
    item_ids: Iterable[str] | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_step_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before editing hierarchy steps."
      )
    step_index, step = self._get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
      current,
      step_id,
    )
    resolved_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (
        {
          "step_id": step.step_id,
          "item_type": step.item_type,
          "action": step.action,
          "item_ids": item_ids if item_ids is not None else step.item_ids,
          "name_prefix": name_prefix if name_prefix is not None else step.name_prefix,
          "name_suffix": name_suffix if name_suffix is not None else step.name_suffix,
          "description_append": (
            description_append if description_append is not None else step.description_append
          ),
          "query_patch": deepcopy(query_patch) if query_patch is not None else deepcopy(step.query_patch),
          "layout_patch": (
            deepcopy(layout_patch) if layout_patch is not None else deepcopy(step.layout_patch)
          ),
          "template_id": template_id if template_id is not None else step.template_id,
          "clear_template_link": (
            clear_template_link
            if clear_template_link is not None
            else step.clear_template_link
          ),
        },
      )
    )[0]
    if resolved_step == step:
      return current
    updated_steps = list(current.hierarchy_steps)
    updated_steps[step_index] = resolved_step
    updated_at = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=replace(current, hierarchy_steps=tuple(updated_steps), updated_at=updated_at),
      action="hierarchy_step_updated",
      reason=reason,
      recorded_at=updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def restore_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_revision(
    self,
    catalog_id: str,
    step_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_step_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before restoring hierarchy step revisions."
      )
    revision = self._load_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.catalog_id != current.catalog_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog revision not found.")
    revision = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision
    )
    normalized_step_id = step_id.strip()
    restored_position = None
    restored_source_step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep | None = None
    for index, step in enumerate(revision.hierarchy_steps):
      if step.step_id == normalized_step_id:
        restored_position = index
        restored_source_step = step
        break
    if restored_source_step is None:
      raise LookupError(
        "Provider provenance scheduler narrative governance policy catalog hierarchy step revision not found."
      )
    if current.item_type_scope not in {"any", restored_source_step.item_type}:
      raise ValueError("Policy catalog item-type scope no longer supports the requested hierarchy step revision.")
    if current.action_scope not in {"any", restored_source_step.action}:
      raise ValueError("Policy catalog action scope no longer supports the requested hierarchy step revision.")
    restored_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (
        {
          "step_id": restored_source_step.step_id,
          "item_type": restored_source_step.item_type,
          "action": restored_source_step.action,
          "item_ids": restored_source_step.item_ids,
          "name_prefix": restored_source_step.name_prefix,
          "name_suffix": restored_source_step.name_suffix,
          "description_append": restored_source_step.description_append,
          "query_patch": deepcopy(restored_source_step.query_patch),
          "layout_patch": deepcopy(restored_source_step.layout_patch),
          "template_id": restored_source_step.template_id,
          "clear_template_link": restored_source_step.clear_template_link,
        },
      )
    )[0]
    updated_steps = list(current.hierarchy_steps)
    existing_index = next(
      (index for index, step in enumerate(updated_steps) if step.step_id == normalized_step_id),
      None,
    )
    if existing_index is None:
      insert_index = min(restored_position, len(updated_steps))
      updated_steps.insert(insert_index, restored_step)
    else:
      if updated_steps[existing_index] == restored_step:
        return current
      updated_steps[existing_index] = restored_step
    restored_at = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=replace(current, hierarchy_steps=tuple(updated_steps), updated_at=restored_at),
      action="hierarchy_step_restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def bulk_govern_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
    self,
    catalog_id: str,
    step_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before editing hierarchy steps."
      )
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "update"}:
      raise ValueError("Unsupported scheduler governance policy catalog hierarchy-step bulk action.")
    normalized_step_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(step_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    normalized_template_id = (
      template_id.strip() if isinstance(template_id, str) and template_id.strip() else None
    )
    if normalized_template_id is not None:
      self.get_provider_provenance_scheduler_narrative_template(normalized_template_id)
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and query_patch is None
      and layout_patch is None
      and normalized_template_id is None
      and clear_template_link is None
    ):
      raise ValueError("No scheduler governance policy catalog hierarchy-step bulk update fields were provided.")
    current_steps = list(current.hierarchy_steps)
    current_steps_by_id = {
      step.step_id or f"unknown_{index}": step
      for index, step in enumerate(current_steps, start=1)
    }
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    if normalized_action == "delete":
      next_steps = [
        step for step in current_steps if step.step_id not in set(normalized_step_ids)
      ]
      removed_step_ids = {step.step_id for step in current_steps if step.step_id in set(normalized_step_ids)}
      for step_id in normalized_step_ids:
        step = current_steps_by_id.get(step_id)
        if step is None:
          failed_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              outcome="failed",
              message="Hierarchy step not found on the selected policy catalog.",
            )
          )
          continue
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=step_id,
            item_name=", ".join(step.item_names) or f"{step.item_type} step",
            outcome="applied",
            status=current.status,
            current_revision_id=current.current_revision_id,
            message="Hierarchy step deleted from the reusable governance hierarchy.",
          )
        )
      updated_catalog = current
      if removed_step_ids:
        deleted_at = self._clock()
        updated_catalog = self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
          record=replace(current, hierarchy_steps=tuple(next_steps), updated_at=deleted_at),
          action="hierarchy_steps_bulk_deleted",
          reason=(
            reason.strip()
            if isinstance(reason, str) and reason.strip()
            else "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_deleted"
          ),
          recorded_at=deleted_at,
          source_revision_id=current.current_revision_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
        )
        results = [
          replace(result, current_revision_id=updated_catalog.current_revision_id)
          if result.outcome == "applied"
          else result
          for result in results
        ]
    else:
      next_steps = list(current_steps)
      for step_id in normalized_step_ids:
        step = current_steps_by_id.get(step_id)
        if step is None:
          failed_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              outcome="failed",
              message="Hierarchy step not found on the selected policy catalog.",
            )
          )
          continue
        try:
          updated_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
            (
              {
                "step_id": step.step_id,
                "item_type": step.item_type,
                "action": step.action,
                "item_ids": step.item_ids,
                "name_prefix": (
                  normalized_name_prefix if normalized_name_prefix is not None else step.name_prefix
                ),
                "name_suffix": (
                  normalized_name_suffix if normalized_name_suffix is not None else step.name_suffix
                ),
                "description_append": (
                  normalized_description_append
                  if normalized_description_append is not None
                  else step.description_append
                ),
                "query_patch": deepcopy(query_patch) if query_patch is not None else deepcopy(step.query_patch),
                "layout_patch": (
                  deepcopy(layout_patch) if layout_patch is not None else deepcopy(step.layout_patch)
                ),
                "template_id": (
                  normalized_template_id if template_id is not None else step.template_id
                ),
                "clear_template_link": (
                  clear_template_link if clear_template_link is not None else step.clear_template_link
                ),
              },
            )
          )[0]
        except (LookupError, ValueError, RuntimeError) as exc:
          failed_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              item_name=", ".join(step.item_names) or f"{step.item_type} step",
              outcome="failed",
              status=current.status,
              current_revision_id=current.current_revision_id,
              message=str(exc),
            )
          )
          continue
        if updated_step == step:
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              item_name=", ".join(step.item_names) or f"{step.item_type} step",
              outcome="skipped",
              status=current.status,
              current_revision_id=current.current_revision_id,
              message="Hierarchy step already matches the requested bulk edits.",
            )
          )
          continue
        applied_count += 1
        step_index, _ = self._get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
          current,
          step_id,
        )
        next_steps[step_index] = updated_step
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=step_id,
            item_name=", ".join(updated_step.item_names) or f"{updated_step.item_type} step",
            outcome="applied",
            status=current.status,
            current_revision_id=current.current_revision_id,
            message="Hierarchy step updated with the requested bulk governance patch.",
          )
        )
      updated_catalog = current
      if applied_count:
        updated_at = self._clock()
        updated_catalog = self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
          record=replace(current, hierarchy_steps=tuple(next_steps), updated_at=updated_at),
          action="hierarchy_steps_bulk_updated",
          reason=(
            reason.strip()
            if isinstance(reason, str) and reason.strip()
            else "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_updated"
          ),
          recorded_at=updated_at,
          source_revision_id=current.current_revision_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
        )
        results = [
          replace(result, current_revision_id=updated_catalog.current_revision_id)
          if result.outcome == "applied"
          else result
          for result in results
        ]
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog_hierarchy_step",
      action=normalized_action,
      reason=(
        reason.strip()
        if isinstance(reason, str) and reason.strip()
        else (
          "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_deleted"
          if normalized_action == "delete"
          else "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_updated"
        )
      ),
      requested_count=len(normalized_step_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
