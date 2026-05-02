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


class ProviderProvenanceSchedulerNarrativeGovernancePlanCreateMixin:
  def create_provider_provenance_scheduler_narrative_governance_plan(
    self,
    *,
    item_type: str,
    item_ids: Iterable[str],
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    queue_view_patch: dict[str, Any] | None = None,
    default_policy_template_id: str | None = None,
    default_policy_catalog_id: str | None = None,
    occurrence_limit: int | None = None,
    history_limit: int | None = None,
    drilldown_history_limit: int | None = None,
    template_id: str | None = None,
    clear_template_link: bool = False,
    policy_template_id: str | None = None,
    policy_catalog_id: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    source_hierarchy_step_template_id: str | None = None,
    source_hierarchy_step_template_name: str | None = None,
    hierarchy_key: str | None = None,
    hierarchy_name: str | None = None,
    hierarchy_position: int | None = None,
    hierarchy_total: int | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    normalized_item_type = self._normalize_provider_provenance_scheduler_narrative_governance_item_type(
      item_type
    )
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler narrative governance action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(item_ids)
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
    if (
      normalized_action == "update"
      and normalized_item_type == "template"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
    ):
      raise ValueError("No scheduler narrative template bulk update fields were provided.")
    if (
      normalized_action == "update"
      and normalized_item_type == "registry"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
      and not isinstance(layout_patch, dict)
      and template_id is None
      and not clear_template_link
    ):
      raise ValueError("No scheduler narrative registry bulk update fields were provided.")
    if (
      normalized_action == "update"
      and normalized_item_type == "stitched_report_view"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
      and occurrence_limit is None
      and history_limit is None
      and drilldown_history_limit is None
    ):
      raise ValueError("No scheduler stitched report view governance fields were provided.")
    if (
      normalized_action == "update"
      and normalized_item_type == "stitched_report_governance_registry"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(queue_view_patch, dict)
      and default_policy_template_id is None
      and default_policy_catalog_id is None
    ):
      raise ValueError("No stitched governance registry governance fields were provided.")
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        f"scheduler_narrative_{normalized_item_type}_bulk_deleted"
        if normalized_action == "delete"
        else (
          f"scheduler_narrative_{normalized_item_type}_bulk_restored"
          if normalized_action == "restore"
          else f"scheduler_narrative_{normalized_item_type}_bulk_updated"
        )
      )
    )
    preview_items: list[ProviderProvenanceSchedulerNarrativeGovernancePreviewItem] = []
    for item_id in normalized_ids:
      try:
        if normalized_item_type == "template":
          current_template = self.get_provider_provenance_scheduler_narrative_template(item_id)
          preview_items.append(
            self._preview_provider_provenance_scheduler_narrative_template_governance_item(
              current_template,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              query_patch=query_patch,
            )
          )
        elif normalized_item_type == "registry":
          current_registry = self.get_provider_provenance_scheduler_narrative_registry_entry(item_id)
          preview_items.append(
            self._preview_provider_provenance_scheduler_narrative_registry_governance_item(
              current_registry,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              query_patch=query_patch,
              layout_patch=layout_patch,
              template_id=template_id,
              clear_template_link=clear_template_link,
            )
          )
        elif normalized_item_type == "stitched_report_governance_registry":
          current_registry = self.get_provider_provenance_scheduler_stitched_report_governance_registry(
            item_id
          )
          preview_items.append(
            self._preview_provider_provenance_scheduler_stitched_report_governance_registry_governance_item(
              current_registry,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              queue_view_patch=queue_view_patch,
              default_policy_template_id=default_policy_template_id,
              default_policy_catalog_id=default_policy_catalog_id,
            )
          )
        else:
          current_view = self.get_provider_provenance_scheduler_stitched_report_view(item_id)
          preview_items.append(
            self._preview_provider_provenance_scheduler_stitched_report_view_governance_item(
              current_view,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              query_patch=query_patch,
              occurrence_limit=occurrence_limit,
              history_limit=history_limit,
              drilldown_history_limit=drilldown_history_limit,
            )
          )
      except (LookupError, RuntimeError, ValueError) as exc:
        preview_items.append(
          ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
            item_id=item_id,
            outcome="failed",
            message=str(exc),
          )
        )
    preview_changed_count = sum(1 for item in preview_items if item.outcome == "changed")
    preview_skipped_count = sum(1 for item in preview_items if item.outcome == "skipped")
    preview_failed_count = sum(1 for item in preview_items if item.outcome == "failed")
    rollback_ready_count = sum(
      1
      for item in preview_items
      if item.outcome == "changed" and item.rollback_revision_id is not None
    )
    request_payload: dict[str, Any] = {
      "item_type": normalized_item_type,
      "item_ids": list(normalized_ids),
      "action": normalized_action,
    }
    if normalized_name_prefix is not None:
      request_payload["name_prefix"] = normalized_name_prefix
    if normalized_name_suffix is not None:
      request_payload["name_suffix"] = normalized_name_suffix
    if normalized_description_append is not None:
      request_payload["description_append"] = normalized_description_append
    if isinstance(query_patch, dict) and query_patch:
      request_payload["query_patch"] = deepcopy(query_patch)
    if isinstance(layout_patch, dict) and layout_patch:
      request_payload["layout_patch"] = deepcopy(layout_patch)
    if isinstance(queue_view_patch, dict) and queue_view_patch:
      request_payload["queue_view_patch"] = deepcopy(queue_view_patch)
    if isinstance(default_policy_template_id, str):
      request_payload["default_policy_template_id"] = default_policy_template_id
    if isinstance(default_policy_catalog_id, str):
      request_payload["default_policy_catalog_id"] = default_policy_catalog_id
    if occurrence_limit is not None:
      request_payload["occurrence_limit"] = self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        occurrence_limit,
        default=8,
        minimum=1,
        maximum=50,
        field_name="scheduler stitched report occurrence_limit",
      )
    if history_limit is not None:
      request_payload["history_limit"] = self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        history_limit,
        default=12,
        minimum=1,
        maximum=200,
        field_name="scheduler stitched report history_limit",
      )
    if drilldown_history_limit is not None:
      request_payload["drilldown_history_limit"] = self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        drilldown_history_limit,
        default=12,
        minimum=1,
        maximum=100,
        field_name="scheduler stitched report drilldown_history_limit",
      )
    if isinstance(template_id, str) and template_id.strip():
      request_payload["template_id"] = template_id.strip()
    if clear_template_link:
      request_payload["clear_template_link"] = True
    (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type=normalized_item_type,
      action=normalized_action,
      policy_catalog_id=policy_catalog_id,
      policy_template_id=policy_template_id,
      approval_lane=approval_lane,
      approval_priority=approval_priority,
    )
    if resolved_policy_catalog is not None:
      request_payload["policy_catalog_id"] = resolved_policy_catalog.catalog_id
    if resolved_policy_template is not None:
      request_payload["policy_template_id"] = resolved_policy_template.policy_template_id
    request_payload["approval_lane"] = resolved_approval_lane
    request_payload["approval_priority"] = resolved_approval_priority
    normalized_source_hierarchy_step_template_id = (
      source_hierarchy_step_template_id.strip()
      if isinstance(source_hierarchy_step_template_id, str) and source_hierarchy_step_template_id.strip()
      else None
    )
    normalized_source_hierarchy_step_template_name = (
      source_hierarchy_step_template_name.strip()
      if isinstance(source_hierarchy_step_template_name, str) and source_hierarchy_step_template_name.strip()
      else None
    )
    if normalized_source_hierarchy_step_template_id is not None:
      request_payload["source_hierarchy_step_template_id"] = normalized_source_hierarchy_step_template_id
    if normalized_source_hierarchy_step_template_name is not None:
      request_payload["source_hierarchy_step_template_name"] = normalized_source_hierarchy_step_template_name
    normalized_hierarchy_key = (
      hierarchy_key.strip()
      if isinstance(hierarchy_key, str) and hierarchy_key.strip()
      else None
    )
    normalized_hierarchy_name = (
      hierarchy_name.strip()
      if isinstance(hierarchy_name, str) and hierarchy_name.strip()
      else None
    )
    resolved_hierarchy_total = (
      max(1, int(hierarchy_total))
      if isinstance(hierarchy_total, int) and hierarchy_total > 0
      else None
    )
    resolved_hierarchy_position = (
      max(1, int(hierarchy_position))
      if isinstance(hierarchy_position, int) and hierarchy_position > 0
      else None
    )
    if normalized_hierarchy_key is not None:
      request_payload["hierarchy_key"] = normalized_hierarchy_key
    if normalized_hierarchy_name is not None:
      request_payload["hierarchy_name"] = normalized_hierarchy_name
    if resolved_hierarchy_position is not None:
      request_payload["hierarchy_position"] = resolved_hierarchy_position
    if resolved_hierarchy_total is not None:
      request_payload["hierarchy_total"] = resolved_hierarchy_total
    now = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      ProviderProvenanceSchedulerNarrativeGovernancePlanRecord(
        plan_id=uuid4().hex[:12],
        item_type=normalized_item_type,
        action=normalized_action,
        reason=resolved_reason,
        status="previewed",
        source_hierarchy_step_template_id=normalized_source_hierarchy_step_template_id,
        source_hierarchy_step_template_name=normalized_source_hierarchy_step_template_name,
        policy_template_id=(
          resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
        ),
        policy_template_name=(
          resolved_policy_template.name if resolved_policy_template is not None else None
        ),
        policy_catalog_id=(
          resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
        ),
        policy_catalog_name=(
          resolved_policy_catalog.name if resolved_policy_catalog is not None else None
        ),
        approval_lane=resolved_approval_lane,
        approval_priority=resolved_approval_priority,
        policy_guidance=resolved_policy_guidance,
        hierarchy_key=normalized_hierarchy_key,
        hierarchy_name=normalized_hierarchy_name,
        hierarchy_position=resolved_hierarchy_position,
        hierarchy_total=resolved_hierarchy_total,
        request_payload=request_payload,
        target_ids=normalized_ids,
        preview_requested_count=len(normalized_ids),
        preview_changed_count=preview_changed_count,
        preview_skipped_count=preview_skipped_count,
        preview_failed_count=preview_failed_count,
        preview_items=tuple(preview_items),
        rollback_ready_count=rollback_ready_count,
        rollback_summary=(
          f"Rollback can restore {rollback_ready_count} pre-apply revision snapshot(s)."
          if rollback_ready_count
          else "No rollback snapshot is available for this governance plan."
        ),
        created_at=now,
        updated_at=now,
        created_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        created_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
      )
    )
