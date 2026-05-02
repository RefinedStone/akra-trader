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


class ProviderProvenanceSchedulerNarrativePolicyCatalogStagingMixin:
  def apply_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_to_catalogs(
    self,
    hierarchy_step_template_id: str,
    catalog_ids: Iterable[str],
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    template = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    if template.status != "active":
      raise RuntimeError("Restore the hierarchy step template before applying it to policy catalogs.")
    normalized_catalog_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(catalog_ids)
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else "scheduler_narrative_governance_hierarchy_step_template_applied"
    )
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for catalog_id in normalized_catalog_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
        if current.status == "deleted":
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=current.catalog_id,
              item_name=current.name,
              outcome="skipped",
              status=current.status,
              current_revision_id=current.current_revision_id,
              message="Catalog is deleted; restore it before applying a hierarchy step template.",
            )
          )
          continue
        if current.item_type_scope not in {"any", template.item_type}:
          raise ValueError("Policy catalog item-type scope does not support the hierarchy step template.")
        if current.action_scope not in {"any", template.step.action}:
          raise ValueError("Policy catalog action scope does not support the hierarchy step template.")
        current_steps = list(current.hierarchy_steps)
        existing_index = next(
          (
            index
            for index, step in enumerate(current_steps)
            if step.source_template_id == template.hierarchy_step_template_id
          ),
          None,
        )
        if existing_index is None and template.origin_catalog_id == current.catalog_id and template.origin_step_id:
          existing_index = next(
            (
              index
              for index, step in enumerate(current_steps)
              if step.step_id == template.origin_step_id
            ),
            None,
          )
        resolved_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
          (
            {
              "step_id": (
                current_steps[existing_index].step_id
                if existing_index is not None
                else None
              ),
              "source_template_id": template.hierarchy_step_template_id,
              "source_template_name": template.name,
              "item_type": template.item_type,
              "action": template.step.action,
              "item_ids": template.step.item_ids,
              "name_prefix": template.step.name_prefix,
              "name_suffix": template.step.name_suffix,
              "description_append": template.step.description_append,
              "query_patch": deepcopy(template.step.query_patch),
              "layout_patch": deepcopy(template.step.layout_patch),
              "template_id": template.step.template_id,
              "clear_template_link": template.step.clear_template_link,
            },
          )
        )[0]
        if existing_index is not None:
          if current_steps[existing_index] == resolved_step:
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog already matches the selected hierarchy step template.",
              )
            )
            continue
          current_steps[existing_index] = resolved_step
        else:
          current_steps.append(resolved_step)
        updated_at = self._clock()
        updated = self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
          record=replace(current, hierarchy_steps=tuple(current_steps), updated_at=updated_at),
          action="hierarchy_step_template_applied",
          reason=resolved_reason,
          recorded_at=updated_at,
          source_revision_id=current.current_revision_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
        )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.catalog_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Hierarchy step template applied to catalog."
              if existing_index is None
              else "Hierarchy step template synchronized onto catalog."
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=catalog_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog_hierarchy_step_template",
      action="apply",
      reason=resolved_reason,
      requested_count=len(normalized_catalog_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
  def stage_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_staged",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before staging approval queue plans."
      )
    if not current.hierarchy_steps:
      raise RuntimeError("Capture a reusable governance hierarchy on this policy catalog before staging it.")
    for step in current.hierarchy_steps:
      if current.item_type_scope not in {"any", step.item_type}:
        raise ValueError("Policy catalog item-type scope no longer supports a captured hierarchy step.")
      if current.action_scope not in {"any", step.action}:
        raise ValueError("Policy catalog action scope no longer supports a captured hierarchy step.")
      for item_id in step.item_ids:
        if step.item_type == "template":
          self._preview_provider_provenance_scheduler_narrative_template_governance_item(
            self.get_provider_provenance_scheduler_narrative_template(item_id),
            action=step.action,
            name_prefix=step.name_prefix,
            name_suffix=step.name_suffix,
            description_append=step.description_append,
            query_patch=step.query_patch,
          )
        else:
          self._preview_provider_provenance_scheduler_narrative_registry_governance_item(
            self.get_provider_provenance_scheduler_narrative_registry_entry(item_id),
            action=step.action,
            name_prefix=step.name_prefix,
            name_suffix=step.name_suffix,
            description_append=step.description_append,
            query_patch=step.query_patch,
            layout_patch=step.layout_patch,
            template_id=step.template_id,
            clear_template_link=step.clear_template_link,
          )
    hierarchy_key = uuid4().hex[:12]
    hierarchy_name = f"{current.name} hierarchy"
    staged_plans: list[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord] = []
    total = len(current.hierarchy_steps)
    resolved_reason = reason.strip() if isinstance(reason, str) and reason.strip() else (
      "scheduler_narrative_governance_policy_catalog_staged"
    )
    for index, step in enumerate(current.hierarchy_steps, start=1):
      staged_plans.append(
        self.create_provider_provenance_scheduler_narrative_governance_plan(
          item_type=step.item_type,
          item_ids=step.item_ids,
          action=step.action,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
          reason=resolved_reason,
          name_prefix=step.name_prefix,
          name_suffix=step.name_suffix,
          description_append=step.description_append,
          query_patch=step.query_patch,
          layout_patch=step.layout_patch,
          template_id=step.template_id,
          clear_template_link=step.clear_template_link,
          policy_catalog_id=current.catalog_id,
          hierarchy_key=hierarchy_key,
          hierarchy_name=hierarchy_name,
          hierarchy_position=index,
          hierarchy_total=total,
        )
      )
    recorded_at = self._clock()
    self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord(
        audit_id=f"{current.catalog_id}:{hierarchy_key}:staged",
        catalog_id=current.catalog_id,
        action="staged",
        recorded_at=recorded_at,
        reason=resolved_reason,
        detail=(
          f"Staged {len(staged_plans)} governance plan(s) into the approval queue from "
          f"{self._summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(current.hierarchy_steps)}"
        ),
        name=current.name,
        status=current.status,
        default_policy_template_id=current.default_policy_template_id,
        default_policy_template_name=current.default_policy_template_name,
        policy_template_ids=tuple(current.policy_template_ids),
        policy_template_names=tuple(current.policy_template_names),
        item_type_scope=current.item_type_scope,
        action_scope=current.action_scope,
        approval_lane=current.approval_lane,
        approval_priority=current.approval_priority,
        guidance=current.guidance,
        hierarchy_steps=tuple(current.hierarchy_steps),
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
    return ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult(
      catalog_id=current.catalog_id,
      catalog_name=current.name,
      hierarchy_key=hierarchy_key,
      hierarchy_name=hierarchy_name,
      plan_count=len(staged_plans),
      summary=(
        f"Staged {len(staged_plans)} governance plan(s) from "
        f"{self._summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(current.hierarchy_steps)}"
      ),
      plans=tuple(staged_plans),
    )
  def _find_latest_active_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions(catalog_id)
    ):
      if revision.status == "active":
        return revision
    return None
  def bulk_govern_provider_provenance_scheduler_narrative_governance_policy_catalogs(
    self,
    catalog_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    default_policy_template_id: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler governance policy catalog bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(catalog_ids)
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
    normalized_default_policy_template_id = (
      default_policy_template_id.strip()
      if isinstance(default_policy_template_id, str) and default_policy_template_id.strip()
      else None
    )
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_narrative_governance_policy_catalog_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_narrative_governance_policy_catalog_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_narrative_governance_policy_catalog_bulk_updated"
        )
      )
    )
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and normalized_default_policy_template_id is None
    ):
      raise ValueError("No scheduler governance policy catalog bulk update fields were provided.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for catalog_id in normalized_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_narrative_governance_policy_catalog(
            catalog_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
            catalog_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
            catalog_id,
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
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is deleted; restore it before applying bulk edits.",
              )
            )
            continue
          updated_name = f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
          updated_description = (
            f"{current.description} {normalized_description_append}".strip()
            if normalized_description_append is not None
            else current.description
          )
          updated_default_policy_template_id = (
            normalized_default_policy_template_id or current.default_policy_template_id
          )
          if (
            updated_name == current.name
            and updated_description == current.description
            and updated_default_policy_template_id == current.default_policy_template_id
          ):
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog already matches the requested bulk edits.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_narrative_governance_policy_catalog(
            catalog_id,
            name=updated_name,
            description=updated_description,
            default_policy_template_id=updated_default_policy_template_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.catalog_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Catalog deleted."
              if normalized_action == "delete"
              else (
                "Catalog restored from the latest active revision."
                if normalized_action == "restore"
                else "Catalog updated with the requested bulk governance patch."
              )
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=catalog_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
  def _find_latest_active_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_governance_policy_template_revisions(
        policy_template_id
      )
    ):
      if revision.status == "active":
        return revision
    return None
  def _resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
    self,
    *,
    item_type: str,
    action: str,
    policy_catalog_id: str | None = None,
    policy_template_id: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
  ) -> tuple[
    ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None,
    ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None,
    str,
    str,
    str | None,
  ]:
    resolved_policy_catalog = (
      self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(policy_catalog_id)
      if isinstance(policy_catalog_id, str) and policy_catalog_id.strip()
      else None
    )
    if resolved_policy_catalog is not None:
      if resolved_policy_catalog.status != "active":
        raise ValueError("Selected scheduler governance policy catalog must be active.")
      if resolved_policy_catalog.item_type_scope not in {"any", item_type}:
        raise ValueError("Selected scheduler governance policy catalog does not support this item type.")
      if resolved_policy_catalog.action_scope not in {"any", action}:
        raise ValueError("Selected scheduler governance policy catalog does not support this action.")
    explicit_policy_template_id = (
      policy_template_id.strip()
      if isinstance(policy_template_id, str) and policy_template_id.strip()
      else None
    )
    resolved_policy_template = (
      self.get_provider_provenance_scheduler_narrative_governance_policy_template(
        explicit_policy_template_id
        if explicit_policy_template_id is not None
        else (
          resolved_policy_catalog.default_policy_template_id
          if resolved_policy_catalog is not None and resolved_policy_catalog.default_policy_template_id
          else ""
        )
      )
      if explicit_policy_template_id is not None or (
        resolved_policy_catalog is not None
        and resolved_policy_catalog.default_policy_template_id is not None
      )
      else None
    )
    if resolved_policy_template is not None:
      if resolved_policy_template.status != "active":
        raise ValueError("Selected scheduler governance policy template must be active.")
      if (
        resolved_policy_catalog is not None
        and resolved_policy_template.policy_template_id not in resolved_policy_catalog.policy_template_ids
      ):
        raise ValueError("Selected scheduler governance policy template is not linked to the chosen policy catalog.")
      if resolved_policy_template.item_type_scope not in {"any", item_type}:
        raise ValueError("Selected scheduler governance policy template does not support this item type.")
      if resolved_policy_template.action_scope not in {"any", action}:
        raise ValueError("Selected scheduler governance policy template does not support this action.")
    resolved_approval_lane = self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
      (
        approval_lane
        if isinstance(approval_lane, str) and approval_lane.strip()
        else (
          resolved_policy_template.approval_lane
          if resolved_policy_template is not None
          else resolved_policy_catalog.approval_lane if resolved_policy_catalog is not None else None
        )
      )
    )
    resolved_approval_priority = self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
      (
        approval_priority
        if isinstance(approval_priority, str) and approval_priority.strip()
        else (
          resolved_policy_template.approval_priority
          if resolved_policy_template is not None
          else resolved_policy_catalog.approval_priority if resolved_policy_catalog is not None else None
        )
      )
    )
    resolved_policy_guidance = (
      resolved_policy_template.guidance
      if resolved_policy_template is not None
      else resolved_policy_catalog.guidance if resolved_policy_catalog is not None else None
    )
    return (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    )
