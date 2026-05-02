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


class ProviderProvenanceSchedulerNarrativePolicyTemplateGovernanceMixin:
  def create_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    *,
    name: str,
    description: str = "",
    item_type_scope: str | None = None,
    action_scope: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    guidance: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    now = self._clock()
    record = ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord(
      policy_template_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative governance policy template name",
      ),
      description=description.strip() if isinstance(description, str) else "",
      item_type_scope=self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(
        item_type_scope
      ),
      action_scope=self._normalize_provider_provenance_scheduler_narrative_governance_action_scope(
        action_scope
      ),
      approval_lane=self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
        approval_lane
      ),
      approval_priority=self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
        approval_priority
      ),
      guidance=guidance.strip() if isinstance(guidance, str) and guidance.strip() else None,
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
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=record,
      action="created",
      reason="scheduler_narrative_governance_policy_template_created",
      recorded_at=now,
      actor_tab_id=record.created_by_tab_id,
      actor_tab_label=record.created_by_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_policy_templates(
    self,
    *,
    item_type_scope: str | None = None,
    action_scope: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    normalized_item_type_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(item_type_scope)
      if isinstance(item_type_scope, str) and item_type_scope.strip()
      else None
    )
    normalized_action_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_action_scope(action_scope)
      if isinstance(action_scope, str) and action_scope.strip()
      else None
    )
    normalized_approval_lane = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(approval_lane)
      if isinstance(approval_lane, str) and approval_lane.strip()
      else None
    )
    normalized_approval_priority = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(approval_priority)
      if isinstance(approval_priority, str) and approval_priority.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_policy_template_records():
      if normalized_item_type_scope is not None and record.item_type_scope != normalized_item_type_scope:
        continue
      if normalized_action_scope is not None and record.action_scope != normalized_action_scope:
        continue
      if normalized_approval_lane is not None and record.approval_lane != normalized_approval_lane:
        continue
      if normalized_approval_priority is not None and record.approval_priority != normalized_approval_priority:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.policy_template_id,
          record.name,
          record.description,
          record.status,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.created_by_tab_id,
          record.created_by_tab_label,
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
  def get_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    normalized_policy_template_id = policy_template_id.strip()
    if not normalized_policy_template_id:
      raise LookupError("Provider provenance scheduler narrative governance policy template not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_policy_template_record(
      normalized_policy_template_id
    )
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance policy template not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
    )
  def update_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    item_type_scope: str | None = None,
    action_scope: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    guidance: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_template_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy templates must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative governance policy template name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = description.strip() if isinstance(description, str) else current.description
    updated_item_type_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(item_type_scope)
      if isinstance(item_type_scope, str)
      else current.item_type_scope
    )
    updated_action_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_action_scope(action_scope)
      if isinstance(action_scope, str)
      else current.action_scope
    )
    updated_approval_lane = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(approval_lane)
      if isinstance(approval_lane, str)
      else current.approval_lane
    )
    updated_approval_priority = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(approval_priority)
      if isinstance(approval_priority, str)
      else current.approval_priority
    )
    updated_guidance = (
      guidance.strip() if isinstance(guidance, str) and guidance.strip() else None
      if guidance is not None
      else current.guidance
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_item_type_scope == current.item_type_scope
      and updated_action_scope == current.action_scope
      and updated_approval_lane == current.approval_lane
      and updated_approval_priority == current.approval_priority
      and updated_guidance == current.guidance
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      item_type_scope=updated_item_type_scope,
      action_scope=updated_action_scope,
      approval_lane=updated_approval_lane,
      approval_priority=updated_approval_priority,
      guidance=updated_guidance,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def delete_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_template_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
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
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_policy_template_revisions(
    self,
    policy_template_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_template_revision_records()
      if revision.policy_template_id == current.policy_template_id
    ]
    return tuple(revisions)
  def restore_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    policy_template_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_template_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
    revision = self._load_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.policy_template_id != current.policy_template_id:
      raise LookupError("Provider provenance scheduler narrative governance policy template revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      item_type_scope=revision.item_type_scope,
      action_scope=revision.action_scope,
      approval_lane=revision.approval_lane,
      approval_priority=revision.approval_priority,
      guidance=revision.guidance,
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )
  def list_provider_provenance_scheduler_narrative_governance_policy_template_audits(
    self,
    *,
    policy_template_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    normalized_policy_template_id = (
      policy_template_id.strip()
      if isinstance(policy_template_id, str) and policy_template_id.strip()
      else None
    )
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records():
      if normalized_policy_template_id is not None and record.policy_template_id != normalized_policy_template_id:
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.policy_template_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.status,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.actor_tab_id,
          record.actor_tab_label,
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
  def _resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
    self,
    *,
    policy_template_ids: Iterable[str],
    default_policy_template_id: str | None = None,
  ) -> tuple[
    tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...],
    ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ]:
    normalized_policy_template_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
      policy_template_ids
    )
    if not normalized_policy_template_ids:
      raise ValueError("Select at least one governance policy template for the catalog.")
    resolved_templates = tuple(
      self.get_provider_provenance_scheduler_narrative_governance_policy_template(template_id)
      for template_id in normalized_policy_template_ids
    )
    if any(template.status != "active" for template in resolved_templates):
      raise ValueError("Governance policy catalog entries must reference active policy templates.")
    resolved_default_policy_template_id = (
      default_policy_template_id.strip()
      if isinstance(default_policy_template_id, str) and default_policy_template_id.strip()
      else resolved_templates[0].policy_template_id
    )
    default_template = next(
      (
        template
        for template in resolved_templates
        if template.policy_template_id == resolved_default_policy_template_id
      ),
      None,
    )
    if default_template is None:
      raise ValueError("Default governance policy template must be one of the linked templates.")
    return resolved_templates, default_template
