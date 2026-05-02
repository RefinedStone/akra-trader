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


class ProviderProvenanceSchedulerNarrativeHierarchyStepTemplateGovernanceMixin:
  def create_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    *,
    name: str,
    description: str = "",
    step: dict[str, Any] | None = None,
    origin_catalog_id: str | None = None,
    origin_step_id: str | None = None,
    governance_policy_template_id: str | None = None,
    governance_policy_catalog_id: str | None = None,
    governance_approval_lane: str | None = None,
    governance_approval_priority: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    normalized_name = self._normalize_provider_provenance_workspace_name(
      name,
      field_name="scheduler governance hierarchy step template name",
    )
    normalized_description = description.strip() if isinstance(description, str) else ""
    resolved_origin_catalog = (
      self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(origin_catalog_id)
      if isinstance(origin_catalog_id, str) and origin_catalog_id.strip()
      else None
    )
    resolved_source_step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep | None = None
    if resolved_origin_catalog is not None and isinstance(origin_step_id, str) and origin_step_id.strip():
      _, resolved_source_step = self._get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
        resolved_origin_catalog,
        origin_step_id,
      )
    raw_step_payload = (
      deepcopy(step)
      if isinstance(step, dict)
      else (
        {
          "item_type": resolved_source_step.item_type,
          "action": resolved_source_step.action,
          "item_ids": resolved_source_step.item_ids,
          "name_prefix": resolved_source_step.name_prefix,
          "name_suffix": resolved_source_step.name_suffix,
          "description_append": resolved_source_step.description_append,
          "query_patch": deepcopy(resolved_source_step.query_patch),
          "layout_patch": deepcopy(resolved_source_step.layout_patch),
          "template_id": resolved_source_step.template_id,
          "clear_template_link": resolved_source_step.clear_template_link,
        }
        if resolved_source_step is not None
        else None
      )
    )
    if raw_step_payload is None:
      raise ValueError("Provide a hierarchy step payload or select an origin catalog step to save as a template.")
    resolved_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (raw_step_payload,)
    )[0]
    (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type=resolved_step.item_type,
      action=resolved_step.action,
      policy_catalog_id=governance_policy_catalog_id,
      policy_template_id=governance_policy_template_id,
      approval_lane=governance_approval_lane,
      approval_priority=governance_approval_priority,
    )
    now = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord(
        hierarchy_step_template_id=uuid4().hex[:12],
        name=normalized_name,
        description=normalized_description,
        item_type=resolved_step.item_type,
        step=replace(
          resolved_step,
          step_id=None,
          source_template_id=None,
          source_template_name=None,
        ),
        origin_catalog_id=resolved_origin_catalog.catalog_id if resolved_origin_catalog is not None else None,
        origin_catalog_name=resolved_origin_catalog.name if resolved_origin_catalog is not None else None,
        origin_step_id=resolved_source_step.step_id if resolved_source_step is not None else None,
        governance_policy_template_id=(
          resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
        ),
        governance_policy_template_name=resolved_policy_template.name if resolved_policy_template is not None else None,
        governance_policy_catalog_id=(
          resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
        ),
        governance_policy_catalog_name=resolved_policy_catalog.name if resolved_policy_catalog is not None else None,
        governance_approval_lane=resolved_approval_lane,
        governance_approval_priority=resolved_approval_priority,
        governance_policy_guidance=resolved_policy_guidance,
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
      reason="scheduler_narrative_governance_hierarchy_step_template_created",
      recorded_at=now,
      actor_tab_id=created_by_tab_id,
      actor_tab_label=created_by_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
    *,
    item_type: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord, ...]:
    normalized_item_type = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type(item_type)
      if isinstance(item_type, str) and item_type.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 100))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_records():
      if normalized_item_type is not None and record.item_type != normalized_item_type:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.hierarchy_step_template_id,
          record.name,
          record.description,
          record.item_type,
          record.status,
          record.current_revision_id,
          record.origin_catalog_id,
          record.origin_catalog_name,
          record.origin_step_id,
          record.governance_policy_template_id,
          record.governance_policy_template_name,
          record.governance_policy_catalog_id,
          record.governance_policy_catalog_name,
          record.governance_approval_lane,
          record.governance_approval_priority,
          record.governance_policy_guidance,
          record.created_by_tab_id,
          record.created_by_tab_label,
          record.step.source_template_id,
          record.step.source_template_name,
          *record.step.item_ids,
          *record.step.item_names,
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
  def get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    normalized_id = hierarchy_step_template_id.strip()
    if not normalized_id:
      raise LookupError("Provider provenance scheduler narrative governance hierarchy step template not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      normalized_id
    )
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance hierarchy step template not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
    )
  def update_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    item_ids: Iterable[str] | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
    governance_policy_template_id: str | None = None,
    governance_policy_catalog_id: str | None = None,
    governance_approval_lane: str | None = None,
    governance_approval_priority: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance hierarchy step templates must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler governance hierarchy step template name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = description.strip() if isinstance(description, str) else current.description
    updated_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (
        {
          "item_type": current.item_type,
          "action": current.step.action,
          "item_ids": item_ids if item_ids is not None else current.step.item_ids,
          "name_prefix": name_prefix if name_prefix is not None else current.step.name_prefix,
          "name_suffix": name_suffix if name_suffix is not None else current.step.name_suffix,
          "description_append": (
            description_append if description_append is not None else current.step.description_append
          ),
          "query_patch": deepcopy(query_patch) if query_patch is not None else deepcopy(current.step.query_patch),
          "layout_patch": (
            deepcopy(layout_patch) if layout_patch is not None else deepcopy(current.step.layout_patch)
          ),
          "template_id": template_id if template_id is not None else current.step.template_id,
          "clear_template_link": (
            clear_template_link if clear_template_link is not None else current.step.clear_template_link
          ),
        },
      )
    )[0]
    updated_step = replace(
      updated_step,
      step_id=None,
      source_template_id=None,
      source_template_name=None,
    )
    (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type=updated_step.item_type,
      action=updated_step.action,
      policy_catalog_id=(
        governance_policy_catalog_id
        if governance_policy_catalog_id is not None
        else current.governance_policy_catalog_id
      ),
      policy_template_id=(
        governance_policy_template_id
        if governance_policy_template_id is not None
        else current.governance_policy_template_id
      ),
      approval_lane=(
        governance_approval_lane
        if governance_approval_lane is not None
        else current.governance_approval_lane
      ),
      approval_priority=(
        governance_approval_priority
        if governance_approval_priority is not None
        else current.governance_approval_priority
      ),
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_step == current.step
      and (
        resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
      ) == current.governance_policy_template_id
      and (
        resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
      ) == current.governance_policy_catalog_id
      and resolved_approval_lane == current.governance_approval_lane
      and resolved_approval_priority == current.governance_approval_priority
      and resolved_policy_guidance == current.governance_policy_guidance
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      item_type=updated_step.item_type,
      step=updated_step,
      governance_policy_template_id=(
        resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
      ),
      governance_policy_template_name=resolved_policy_template.name if resolved_policy_template is not None else None,
      governance_policy_catalog_id=(
        resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
      ),
      governance_policy_catalog_name=resolved_policy_catalog.name if resolved_policy_catalog is not None else None,
      governance_approval_lane=resolved_approval_lane,
      governance_approval_priority=resolved_approval_priority,
      governance_policy_guidance=resolved_policy_guidance,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def delete_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
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
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions(
    self,
    hierarchy_step_template_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_records()
      if revision.hierarchy_step_template_id == current.hierarchy_step_template_id
    ]
    return tuple(revisions)
  def restore_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    hierarchy_step_template_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    revision = self._load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.hierarchy_step_template_id != current.hierarchy_step_template_id:
      raise LookupError("Provider provenance scheduler narrative governance hierarchy step template revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      item_type=revision.item_type,
      step=replace(
        revision.step,
        step_id=None,
        source_template_id=None,
        source_template_name=None,
      ),
      origin_catalog_id=revision.origin_catalog_id,
      origin_catalog_name=revision.origin_catalog_name,
      origin_step_id=revision.origin_step_id,
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audits(
    self,
    *,
    hierarchy_step_template_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ...]:
    normalized_hierarchy_step_template_id = (
      hierarchy_step_template_id.strip()
      if isinstance(hierarchy_step_template_id, str) and hierarchy_step_template_id.strip()
      else None
    )
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records():
      if (
        normalized_hierarchy_step_template_id is not None
        and record.hierarchy_step_template_id != normalized_hierarchy_step_template_id
      ):
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.hierarchy_step_template_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.description,
          record.item_type,
          record.origin_catalog_id,
          record.origin_catalog_name,
          record.origin_step_id,
          record.status,
          record.actor_tab_id,
          record.actor_tab_label,
          record.step.step_id,
          record.step.source_template_id,
          record.step.source_template_name,
          *record.step.item_ids,
          *record.step.item_names,
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
  def stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_staged",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    if current.status == "deleted":
      raise RuntimeError(
        "Restore the hierarchy step template before staging approval queue plans."
      )
    resolved_reason = reason.strip() if isinstance(reason, str) and reason.strip() else (
      "scheduler_narrative_governance_hierarchy_step_template_staged"
    )
    plan = self.create_provider_provenance_scheduler_narrative_governance_plan(
      item_type=current.item_type,
      item_ids=current.step.item_ids,
      action=current.step.action,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
      reason=resolved_reason,
      name_prefix=current.step.name_prefix,
      name_suffix=current.step.name_suffix,
      description_append=current.step.description_append,
      query_patch=current.step.query_patch,
      layout_patch=current.step.layout_patch,
      template_id=current.step.template_id,
      clear_template_link=current.step.clear_template_link,
      policy_template_id=current.governance_policy_template_id,
      policy_catalog_id=current.governance_policy_catalog_id,
      approval_lane=current.governance_approval_lane,
      approval_priority=current.governance_approval_priority,
      source_hierarchy_step_template_id=current.hierarchy_step_template_id,
      source_hierarchy_step_template_name=current.name,
    )
    recorded_at = self._clock()
    self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord(
        audit_id=f"{current.hierarchy_step_template_id}:{plan.plan_id}:staged",
        hierarchy_step_template_id=current.hierarchy_step_template_id,
        action="staged",
        recorded_at=recorded_at,
        reason=resolved_reason,
        detail=(
          f"Staged hierarchy step template {current.name} into the approval queue as plan "
          f"{plan.plan_id}. "
          f"{self._build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_detail(record=current, action='staged')}"
        ),
        name=current.name,
        description=current.description,
        item_type=current.item_type,
        step=current.step,
        origin_catalog_id=current.origin_catalog_id,
        origin_catalog_name=current.origin_catalog_name,
        origin_step_id=current.origin_step_id,
        governance_policy_template_id=current.governance_policy_template_id,
        governance_policy_template_name=current.governance_policy_template_name,
        governance_policy_catalog_id=current.governance_policy_catalog_id,
        governance_policy_catalog_name=current.governance_policy_catalog_name,
        governance_approval_lane=current.governance_approval_lane,
        governance_approval_priority=current.governance_approval_priority,
        governance_policy_guidance=current.governance_policy_guidance,
        status=current.status,
        actor_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        actor_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
      )
    )
    return plan
  def stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
    hierarchy_step_template_ids: Iterable[str],
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_templates_staged",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult:
    normalized_template_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
      hierarchy_step_template_ids
    )
    if not normalized_template_ids:
      raise ValueError("Select at least one hierarchy step template to stage.")
    results: list[ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult] = []
    succeeded_count = 0
    skipped_count = 0
    failed_count = 0
    for hierarchy_step_template_id in normalized_template_ids:
      try:
        plan = self.stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
          hierarchy_step_template_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
          reason=reason,
        )
        succeeded_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=plan.plan_id,
            action="stage",
            outcome="succeeded",
            status=plan.status,
            queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
              plan.status
            ),
            message="Hierarchy step template staged into the approval queue.",
            plan=plan,
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=hierarchy_step_template_id,
            action="stage",
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult(
      action="stage",
      requested_count=len(normalized_template_ids),
      succeeded_count=succeeded_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
  def _find_latest_active_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions(
        hierarchy_step_template_id
      )
    ):
      if revision.status == "active":
        return revision
    return None
  def bulk_govern_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
    hierarchy_step_template_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    item_ids: Iterable[str] | None = None,
    step_name_prefix: str | None = None,
    step_name_suffix: str | None = None,
    step_description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler governance hierarchy step template bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
      hierarchy_step_template_ids
    )
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
    normalized_step_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      step_name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_step_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      step_name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_step_description_append = (
      self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(step_description_append)
    )
    normalized_item_ids = (
      self._normalize_provider_provenance_scheduler_narrative_bulk_ids(item_ids)
      if item_ids is not None
      else None
    )
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_narrative_governance_hierarchy_step_template_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_narrative_governance_hierarchy_step_template_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_narrative_governance_hierarchy_step_template_bulk_updated"
        )
      )
    )
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and normalized_item_ids is None
      and normalized_step_name_prefix is None
      and normalized_step_name_suffix is None
      and normalized_step_description_append is None
      and query_patch is None
      and layout_patch is None
      and template_id is None
      and clear_template_link is None
    ):
      raise ValueError("No scheduler governance hierarchy step template bulk update fields were provided.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for hierarchy_step_template_id in normalized_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
          hierarchy_step_template_id
        )
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
            hierarchy_step_template_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
            hierarchy_step_template_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
            hierarchy_step_template_id,
            revision.revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template is deleted; restore it before applying bulk edits.",
              )
            )
            continue
          updated_name = (
            f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
          )
          updated_description = (
            f"{current.description} {normalized_description_append}".strip()
            if normalized_description_append is not None
            else current.description
          )
          updated_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
            (
              {
                "item_type": current.item_type,
                "action": current.step.action,
                "item_ids": normalized_item_ids if normalized_item_ids is not None else current.step.item_ids,
                "name_prefix": (
                  normalized_step_name_prefix
                  if normalized_step_name_prefix is not None
                  else current.step.name_prefix
                ),
                "name_suffix": (
                  normalized_step_name_suffix
                  if normalized_step_name_suffix is not None
                  else current.step.name_suffix
                ),
                "description_append": (
                  normalized_step_description_append
                  if normalized_step_description_append is not None
                  else current.step.description_append
                ),
                "query_patch": (
                  deepcopy(query_patch) if query_patch is not None else deepcopy(current.step.query_patch)
                ),
                "layout_patch": (
                  deepcopy(layout_patch) if layout_patch is not None else deepcopy(current.step.layout_patch)
                ),
                "template_id": template_id if template_id is not None else current.step.template_id,
                "clear_template_link": (
                  clear_template_link if clear_template_link is not None else current.step.clear_template_link
                ),
              },
            )
          )[0]
          updated_step = replace(
            updated_step,
            step_id=None,
            source_template_id=None,
            source_template_name=None,
          )
          if (
            updated_name == current.name
            and updated_description == current.description
            and updated_step == current.step
          ):
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template already matches the requested bulk edits.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
            hierarchy_step_template_id,
            name=updated_name,
            description=updated_description,
            item_ids=updated_step.item_ids,
            name_prefix=updated_step.name_prefix,
            name_suffix=updated_step.name_suffix,
            description_append=updated_step.description_append,
            query_patch=updated_step.query_patch,
            layout_patch=updated_step.layout_patch,
            template_id=updated_step.template_id,
            clear_template_link=updated_step.clear_template_link,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.hierarchy_step_template_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Hierarchy step template deleted."
              if normalized_action == "delete"
              else (
                "Hierarchy step template restored from the latest active revision."
                if normalized_action == "restore"
                else "Hierarchy step template updated with the requested bulk governance patch."
              )
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=hierarchy_step_template_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog_hierarchy_step_template",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
