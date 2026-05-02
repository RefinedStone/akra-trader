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


class ProviderProvenanceSchedulerNarrativeGovernancePlanActionsMixin:
  def list_provider_provenance_scheduler_narrative_governance_plans(
    self,
    *,
    item_type: str | None = None,
    status: str | None = None,
    queue_state: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    policy_template_id: str | None = None,
    policy_catalog_id: str | None = None,
    source_hierarchy_step_template_id: str | None = None,
    search: str | None = None,
    sort: str | None = None,
    limit: int = 20,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanListResult:
    normalized_item_type = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type(item_type)
      if isinstance(item_type, str) and item_type.strip()
      else None
    )
    normalized_status = (
      status.strip().lower()
      if isinstance(status, str) and status.strip()
      else None
    )
    normalized_queue_state = (
      self._normalize_provider_provenance_scheduler_narrative_governance_queue_state_filter(queue_state)
      if isinstance(queue_state, str) and queue_state.strip()
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
    normalized_policy_template_id = (
      None
      if not isinstance(policy_template_id, str)
      else ""
      if policy_template_id == "__none__"
      else policy_template_id.strip() or None
    )
    normalized_policy_catalog_id = (
      None
      if not isinstance(policy_catalog_id, str)
      else ""
      if policy_catalog_id == "__none__"
      else policy_catalog_id.strip() or None
    )
    normalized_source_hierarchy_step_template_id = (
      None
      if not isinstance(source_hierarchy_step_template_id, str)
      else ""
      if source_hierarchy_step_template_id == "__none__"
      else source_hierarchy_step_template_id.strip() or None
    )
    normalized_sort = self._normalize_provider_provenance_scheduler_narrative_governance_plan_sort(sort)
    normalized_limit = max(1, min(limit, 100))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_plan_records():
      if normalized_item_type is not None and record.item_type != normalized_item_type:
        continue
      if normalized_status is not None and record.status != normalized_status:
        continue
      if (
        normalized_queue_state is not None
        and self._build_provider_provenance_scheduler_narrative_governance_queue_state(record.status)
        != normalized_queue_state
      ):
        continue
      if normalized_approval_lane is not None and record.approval_lane != normalized_approval_lane:
        continue
      if normalized_approval_priority is not None and record.approval_priority != normalized_approval_priority:
        continue
      if normalized_policy_template_id is not None and (record.policy_template_id or "") != normalized_policy_template_id:
        continue
      if normalized_policy_catalog_id is not None and (record.policy_catalog_id or "") != normalized_policy_catalog_id:
        continue
      if (
        normalized_source_hierarchy_step_template_id is not None
        and (record.source_hierarchy_step_template_id or "") != normalized_source_hierarchy_step_template_id
      ):
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.plan_id,
          record.item_type,
          record.action,
          record.reason,
          record.status,
          self._build_provider_provenance_scheduler_narrative_governance_queue_state(record.status),
          record.policy_template_id,
          record.policy_template_name,
          record.policy_catalog_id,
          record.policy_catalog_name,
          record.source_hierarchy_step_template_id,
          record.source_hierarchy_step_template_name,
          record.approval_lane,
          record.approval_priority,
          record.policy_guidance,
          record.hierarchy_key,
          record.hierarchy_name,
          record.created_by_tab_id,
          record.created_by_tab_label,
          *(
            item.item_name
            for item in record.preview_items
            if isinstance(item.item_name, str) and item.item_name.strip()
          ),
        ),
        search=search,
      ):
        continue
      filtered.append(record)
    pending_approval_count = sum(1 for record in filtered if record.status == "previewed")
    ready_to_apply_count = sum(1 for record in filtered if record.status == "approved")
    completed_count = sum(1 for record in filtered if record.status in {"applied", "rolled_back"})

    def _sort_source_template_value(
      record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
    ) -> str:
      return (
        record.source_hierarchy_step_template_name
        or record.source_hierarchy_step_template_id
        or ""
      ).lower()

    filtered.sort(key=lambda record: record.plan_id)
    filtered.sort(key=lambda record: record.updated_at, reverse=True)
    if normalized_sort == "queue_priority":
      filtered.sort(
        key=lambda record: self._build_provider_provenance_scheduler_narrative_governance_priority_rank(
          record.approval_priority
        ),
        reverse=True,
      )
      filtered.sort(
        key=lambda record: {
          "pending_approval": 0,
          "ready_to_apply": 1,
          "completed": 2,
        }[
          self._build_provider_provenance_scheduler_narrative_governance_queue_state(record.status)
        ]
      )
    elif normalized_sort == "updated_asc":
      filtered.sort(key=lambda record: record.updated_at)
    elif normalized_sort == "created_desc":
      filtered.sort(key=lambda record: record.created_at, reverse=True)
    elif normalized_sort == "created_asc":
      filtered.sort(key=lambda record: record.created_at)
    elif normalized_sort == "source_template_asc":
      filtered.sort(key=_sort_source_template_value)
    elif normalized_sort == "source_template_desc":
      filtered.sort(key=_sort_source_template_value, reverse=True)

    return ProviderProvenanceSchedulerNarrativeGovernancePlanListResult(
      items=tuple(filtered[:normalized_limit]),
      total=len(filtered),
      pending_approval_count=pending_approval_count,
      ready_to_apply_count=ready_to_apply_count,
      completed_count=completed_count,
    )
  def get_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    normalized_plan_id = plan_id.strip()
    if not normalized_plan_id:
      raise LookupError("Provider provenance scheduler narrative governance plan not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_plan_record(normalized_plan_id)
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance plan not found.")
    return record
  def approve_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    note: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
    if current.status == "applied":
      raise RuntimeError("Applied governance plans cannot be approved again.")
    if current.status == "rolled_back":
      raise RuntimeError("Rolled-back governance plans cannot be approved again.")
    approved_at = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      replace(
        current,
        status="approved",
        updated_at=approved_at,
        approved_at=approved_at,
        approved_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        approved_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
        approval_note=note.strip() if isinstance(note, str) and note.strip() else current.approval_note,
      )
    )
  def apply_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
    if current.status != "approved":
      raise RuntimeError("Approve the scheduler narrative governance plan before applying it.")
    request_payload = current.request_payload
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for preview in current.preview_items:
      if preview.outcome == "skipped":
        skipped_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="skipped",
            status=preview.status,
            current_revision_id=preview.current_revision_id,
            message=preview.message,
          )
        )
        continue
      if preview.outcome == "failed":
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="failed",
            status=preview.status,
            current_revision_id=preview.current_revision_id,
            message=preview.message,
          )
        )
        continue
      try:
        if current.item_type == "template":
          existing = self.get_provider_provenance_scheduler_narrative_template(preview.item_id)
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Template drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_narrative_template(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_narrative_template_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
              existing.query,
              request_payload.get("query_patch"),
            )
            updated = self.update_provider_provenance_scheduler_narrative_template(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              query=updated_query,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.template_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        elif current.item_type == "registry":
          existing = self.get_provider_provenance_scheduler_narrative_registry_entry(preview.item_id)
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Registry drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_narrative_registry_entry(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_narrative_registry_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
              existing.query,
              request_payload.get("query_patch"),
            )
            updated_layout = self._build_provider_provenance_scheduler_narrative_bulk_registry_layout(
              existing.layout,
              request_payload.get("layout_patch"),
            )
            updated_template_id = (
              ""
              if bool(request_payload.get("clear_template_link"))
              else (
                request_payload.get("template_id")
                if isinstance(request_payload.get("template_id"), str)
                else existing.template_id
              )
            )
            updated = self.update_provider_provenance_scheduler_narrative_registry_entry(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              query=updated_query,
              layout=updated_layout,
              template_id=updated_template_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        elif current.item_type == "stitched_report_governance_registry":
          existing = self.get_provider_provenance_scheduler_stitched_report_governance_registry(
            preview.item_id
          )
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Stitched governance registry drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_stitched_report_governance_registry(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_stitched_report_governance_registry_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated = self.update_provider_provenance_scheduler_stitched_report_governance_registry(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              queue_view=(
                request_payload.get("queue_view_patch")
                if isinstance(request_payload.get("queue_view_patch"), dict)
                else existing.queue_view
              ),
              default_policy_template_id=(
                request_payload.get("default_policy_template_id")
                if isinstance(request_payload.get("default_policy_template_id"), str)
                else existing.default_policy_template_id
              ),
              default_policy_catalog_id=(
                request_payload.get("default_policy_catalog_id")
                if isinstance(request_payload.get("default_policy_catalog_id"), str)
                else existing.default_policy_catalog_id
              ),
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        else:
          existing = self.get_provider_provenance_scheduler_stitched_report_view(preview.item_id)
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Stitched report view drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_stitched_report_view(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_stitched_report_view_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated_query = self._build_provider_provenance_scheduler_stitched_report_view_bulk_query(
              existing.query,
              request_payload.get("query_patch"),
            )
            updated = self.update_provider_provenance_scheduler_stitched_report_view(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              query=updated_query,
              occurrence_limit=(
                request_payload.get("occurrence_limit")
                if isinstance(request_payload.get("occurrence_limit"), int)
                else existing.occurrence_limit
              ),
              history_limit=(
                request_payload.get("history_limit")
                if isinstance(request_payload.get("history_limit"), int)
                else existing.history_limit
              ),
              drilldown_history_limit=(
                request_payload.get("drilldown_history_limit")
                if isinstance(request_payload.get("drilldown_history_limit"), int)
                else existing.drilldown_history_limit
              ),
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.view_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        applied_count += 1
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="failed",
            message=str(exc),
          )
        )
    applied_result = ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type=current.item_type,
      action=current.action,
      reason=current.reason,
      requested_count=len(current.target_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
    applied_at = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      replace(
        current,
        status="applied",
        updated_at=applied_at,
        applied_at=applied_at,
        applied_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        applied_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
        applied_result=applied_result,
      )
    )
  def run_provider_provenance_scheduler_narrative_governance_plan_batch_action(
    self,
    *,
    action: str,
    plan_ids: Iterable[str],
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    note: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"approve", "apply"}:
      raise ValueError("Unsupported scheduler narrative governance batch action.")
    normalized_plan_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(plan_ids)
    if not normalized_plan_ids:
      raise ValueError("Select at least one scheduler narrative governance plan.")
    results: list[ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult] = []
    succeeded_count = 0
    skipped_count = 0
    failed_count = 0
    for plan_id in normalized_plan_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
        if normalized_action == "approve" and current.status == "approved":
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
              plan_id=current.plan_id,
              action=normalized_action,
              outcome="skipped",
              status=current.status,
              queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
                current.status
              ),
              message="Plan is already approved.",
              plan=current,
            )
          )
          continue
        if normalized_action == "apply" and current.status == "applied":
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
              plan_id=current.plan_id,
              action=normalized_action,
              outcome="skipped",
              status=current.status,
              queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
                current.status
              ),
              message="Plan is already applied.",
              plan=current,
            )
          )
          continue
        updated = (
          self.approve_provider_provenance_scheduler_narrative_governance_plan(
            current.plan_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            note=note,
          )
          if normalized_action == "approve"
          else self.apply_provider_provenance_scheduler_narrative_governance_plan(
            current.plan_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
          )
        )
        succeeded_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=updated.plan_id,
            action=normalized_action,
            outcome="succeeded",
            status=updated.status,
            queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
              updated.status
            ),
            message=(
              "Plan approved for apply."
              if normalized_action == "approve"
              else "Approved governance plan applied."
            ),
            plan=updated,
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=plan_id,
            action=normalized_action,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult(
      action=normalized_action,
      requested_count=len(normalized_plan_ids),
      succeeded_count=succeeded_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
  def rollback_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    note: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
    if current.status != "applied":
      raise RuntimeError("Only applied scheduler narrative governance plans can be rolled back.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for preview in current.preview_items:
      if preview.rollback_revision_id is None:
        skipped_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="skipped",
            message="No rollback revision was captured for this item.",
          )
        )
        continue
      try:
        if current.item_type == "template":
          updated = self.restore_provider_provenance_scheduler_narrative_template_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_narrative_template_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.template_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Template restored to the pre-apply revision snapshot.",
            )
          )
        elif current.item_type == "registry":
          updated = self.restore_provider_provenance_scheduler_narrative_registry_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_narrative_registry_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Registry restored to the pre-apply revision snapshot.",
            )
          )
        elif current.item_type == "stitched_report_governance_registry":
          updated = self.restore_provider_provenance_scheduler_stitched_report_governance_registry_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_stitched_report_governance_registry_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Stitched governance registry restored to the pre-apply revision snapshot.",
            )
          )
        else:
          updated = self.restore_provider_provenance_scheduler_stitched_report_view_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_stitched_report_view_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.view_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Stitched report view restored to the pre-apply revision snapshot.",
            )
          )
        applied_count += 1
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="failed",
            message=str(exc),
          )
        )
    rollback_result = ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type=current.item_type,
      action="rollback",
      reason=current.reason,
      requested_count=len(current.target_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
    rolled_back_at = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      replace(
        current,
        status="rolled_back",
        updated_at=rolled_back_at,
        rolled_back_at=rolled_back_at,
        rolled_back_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        rolled_back_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
        rollback_note=note.strip() if isinstance(note, str) and note.strip() else current.rollback_note,
        rollback_result=rollback_result,
      )
    )
