from __future__ import annotations

from typing import Any
from typing import Iterable

from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeBulkGovernanceResult


def bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
  app: Any,
  *,
  governance_policy_ids: Iterable[str],
  action: str,
  actor_tab_id: str | None = None,
  actor_tab_label: str | None = None,
  reason: str | None = None,
  name_prefix: str | None = None,
  name_suffix: str | None = None,
  description_append: str | None = None,
  default_moderation_status: str | None = None,
  governance_view: str | None = None,
  window_days: int | None = None,
  stale_pending_hours: int | None = None,
  minimum_score: int | None = None,
  require_note: bool | None = None,
  action_scope: str | None = None,
  require_approval_note: bool | None = None,
  guidance: str | None = None,
) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
  normalized_ids = app._normalize_provider_provenance_scheduler_narrative_bulk_ids(
    governance_policy_ids
  )
  if not normalized_ids:
    raise ValueError("Select one or more moderation governance policies first.")
  normalized_action = (
    app._normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
      action
    )
  )
  if normalized_action is None:
    raise ValueError("Unsupported moderation governance policy bulk action.")
  if normalized_action == "update" and all(
    value is None
    for value in (
      name_prefix,
      name_suffix,
      description_append,
      default_moderation_status,
      governance_view,
      window_days,
      stale_pending_hours,
      minimum_score,
      require_note,
      action_scope,
      require_approval_note,
      guidance,
    )
  ):
    raise ValueError("Provide at least one moderation governance policy change before bulk update.")
  normalized_reason = (
    reason.strip()
    if isinstance(reason, str) and reason.strip()
    else (
      "scheduler_search_moderation_catalog_governance_policy_bulk_deleted"
      if normalized_action == "delete"
      else (
        "scheduler_search_moderation_catalog_governance_policy_bulk_restored"
        if normalized_action == "restore"
        else "scheduler_search_moderation_catalog_governance_policy_bulk_updated"
      )
    )
  )
  results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
  applied_count = 0
  skipped_count = 0
  failed_count = 0
  for governance_policy_id in normalized_ids:
    try:
      current = app._get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
        governance_policy_id
      )
      if normalized_action == "delete":
        updated = app.delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
          governance_policy_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
          reason=normalized_reason,
        )
      elif normalized_action == "restore":
        source_revision_id = current.current_revision_id
        if not source_revision_id:
          raise RuntimeError("Governance policy is missing revision history.")
        updated = app.restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
          governance_policy_id,
          source_revision_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
          reason=normalized_reason,
        )
      else:
        updated = app.update_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
          governance_policy_id,
          name=(
            f"{name_prefix or ''}{current.name}{name_suffix or ''}"
            if name_prefix is not None or name_suffix is not None
            else None
          ),
          description=(
            f"{current.description}{description_append}"
            if description_append is not None
            else None
          ),
          action_scope=action_scope,
          require_approval_note=require_approval_note,
          guidance=guidance,
          default_moderation_status=default_moderation_status,
          governance_view=governance_view,
          window_days=window_days,
          stale_pending_hours=stale_pending_hours,
          minimum_score=minimum_score,
          require_note=require_note,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
          reason=normalized_reason,
        )
      applied_count += 1
      results.append(
        ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
          item_id=governance_policy_id,
          item_name=str(updated.get("name", governance_policy_id)),
          outcome="applied",
          status=updated.get("status"),
          current_revision_id=updated.get("current_revision_id"),
        )
      )
    except RuntimeError as exc:
      skipped_count += 1
      results.append(
        ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
          item_id=governance_policy_id,
          item_name=governance_policy_id,
          outcome="skipped",
          message=str(exc),
        )
      )
    except (LookupError, ValueError) as exc:
      failed_count += 1
      results.append(
        ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
          item_id=governance_policy_id,
          item_name=governance_policy_id,
          outcome="failed",
          message=str(exc),
        )
      )
  return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
    item_type="scheduler_search_moderation_catalog_governance_policy",
    action=normalized_action,
    reason=normalized_reason,
    requested_count=len(normalized_ids),
    applied_count=applied_count,
    skipped_count=skipped_count,
    failed_count=failed_count,
    results=tuple(results),
  )
