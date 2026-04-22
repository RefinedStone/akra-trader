from __future__ import annotations

from dataclasses import replace
from typing import Any


def list_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
  app: Any,
  *,
  action_scope: str | None = None,
  search: str | None = None,
  limit: int = 50,
) -> dict[str, Any]:
  normalized_action_scope = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action_scope(
      action_scope
    )
    if isinstance(action_scope, str) and action_scope.strip()
    else None
  )
  normalized_limit = max(1, min(limit, 200))
  records = []
  for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records():
    if normalized_action_scope is not None and record.action_scope != normalized_action_scope:
      continue
    if not app._matches_provider_provenance_workspace_search(
      values=(
        record.governance_policy_id,
        record.name,
        record.description,
        record.action_scope,
        record.guidance,
        record.default_moderation_status,
        record.governance_view,
        record.created_by_tab_id,
        record.created_by_tab_label,
      ),
      search=search,
    ):
      continue
    records.append(
      app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
        replace(
          record,
          status=app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status(
            record.status
          ),
        )
      )
    )
  return {
    "generated_at": app._clock(),
    "query": {
      "action_scope": normalized_action_scope,
      "search": search.strip() if isinstance(search, str) and search.strip() else None,
      "limit": normalized_limit,
    },
    "available_filters": {
      "action_scopes": ("any", "update", "delete", "restore"),
    },
    "total": len(records),
    "items": tuple(records[:normalized_limit]),
  }


def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions(
  app: Any,
  governance_policy_id: str,
) -> dict[str, Any]:
  current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    governance_policy_id
  )
  history = tuple(
    app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
      revision
    )
    for revision in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records()
    if revision.governance_policy_id == current.governance_policy_id
  )
  return {
    "policy": app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
      current
    ),
    "history": history,
  }


def list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits(
  app: Any,
  *,
  governance_policy_id: str | None = None,
  action: str | None = None,
  actor_tab_id: str | None = None,
  search: str | None = None,
  limit: int = 50,
) -> dict[str, Any]:
  normalized_policy_id = (
    governance_policy_id.strip()
    if isinstance(governance_policy_id, str) and governance_policy_id.strip()
    else None
  )
  normalized_action = (
    action.strip().lower().replace("-", "_")
    if isinstance(action, str) and action.strip()
    else None
  )
  normalized_actor = (
    actor_tab_id.strip()
    if isinstance(actor_tab_id, str) and actor_tab_id.strip()
    else None
  )
  normalized_limit = max(1, min(limit, 200))
  items: list[dict[str, Any]] = []
  for record in app._list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records():
    if normalized_policy_id is not None and record.governance_policy_id != normalized_policy_id:
      continue
    if normalized_action is not None and record.action != normalized_action:
      continue
    if normalized_actor is not None and (record.actor_tab_id or "") != normalized_actor:
      continue
    if not app._matches_provider_provenance_workspace_search(
      values=(
        record.governance_policy_id,
        record.name,
        record.action,
        record.reason,
        record.detail,
        record.actor_tab_id,
        record.actor_tab_label,
      ),
      search=search,
    ):
      continue
    items.append(
      app._serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
        record
      )
    )
  return {
    "items": tuple(items[:normalized_limit]),
    "total": len(items),
  }
