from __future__ import annotations

from dataclasses import asdict
from typing import Any

from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import RunSurfaceSharedContract
from akra_trader.lineage import build_operator_lineage_summary
from akra_trader.lineage import build_dataset_boundary_contract
from akra_trader.lineage import serialize_operator_lineage_summary
from akra_trader.lineage import serialize_dataset_boundary_contract


def _get_run_surface_capability_family(
  capabilities: RunSurfaceCapabilities,
  family_key: str,
) -> RunSurfaceSharedContract | None:
  contract_key = f"family:{family_key}"
  for contract in capabilities.shared_contracts:
    if contract.contract_kind == "capability_family" and contract.contract_key == contract_key:
      return contract
  return None


def _get_run_surface_capability_surface_rule(
  capabilities: RunSurfaceCapabilities,
  family_key: str,
  surface_key: str,
) -> RunSurfaceCapabilities.SurfaceRule | None:
  family = _get_run_surface_capability_family(capabilities, family_key)
  if family is None:
    return None
  for rule in family.surface_rules:
    if rule.surface_key == surface_key:
      return rule
  return None


def _surface_rule_disabled_reason(surface_key: str) -> str:
  return f"Surface rule {surface_key} is disabled by the run-surface capability contract."


def _serialize_surface_rule_state(
  *,
  capabilities: RunSurfaceCapabilities,
  family_key: str,
  surface_key: str,
) -> dict[str, Any]:
  family = _get_run_surface_capability_family(capabilities, family_key)
  rule = _get_run_surface_capability_surface_rule(capabilities, family_key, surface_key)
  return {
    "enabled": rule is not None,
    "family_key": family_key,
    "family_title": family.title if family is not None else None,
    "surface_key": surface_key,
    "surface_label": rule.surface_label if rule is not None else None,
    "rule_key": rule.rule_key if rule is not None else None,
    "enforcement_point": rule.enforcement_point if rule is not None else None,
    "enforcement_mode": rule.enforcement_mode if rule is not None else None,
    "level": rule.level if rule is not None else None,
    "fallback_behavior": rule.fallback_behavior if rule is not None else None,
    "source_of_truth": rule.source_of_truth if rule is not None else None,
    "reason": None if rule is not None else _surface_rule_disabled_reason(surface_key),
  }


def _build_run_surface_enforcement(capabilities: RunSurfaceCapabilities) -> dict[str, dict[str, Any]]:
  surface_specs = (
    ("comparison_eligibility", "run_list_metric_tiles"),
    ("comparison_eligibility", "boundary_note_panels"),
    ("comparison_eligibility", "order_workflow_gates"),
    ("provenance_semantics", "run_strategy_snapshot"),
    ("provenance_semantics", "reference_provenance_panels"),
    ("provenance_semantics", "benchmark_artifact_summaries"),
    ("execution_controls", "rerun_and_stop_controls"),
    ("execution_controls", "compare_selection_workflow"),
    ("execution_controls", "order_replace_cancel_actions"),
  )
  return {
    surface_key: _serialize_surface_rule_state(
      capabilities=capabilities,
      family_key=family_key,
      surface_key=surface_key,
    )
    for family_key, surface_key in surface_specs
  }


def _serialize_action_availability_entry(
  *,
  capabilities: RunSurfaceCapabilities,
  family_key: str,
  surface_key: str,
  allowed: bool,
  reason: str | None,
) -> dict[str, Any]:
  rule = _get_run_surface_capability_surface_rule(capabilities, family_key, surface_key)
  if rule is None:
    return {
      "allowed": False,
      "reason": _surface_rule_disabled_reason(surface_key),
      "family_key": family_key,
      "surface_key": surface_key,
      "rule_key": None,
      "enforcement_mode": None,
      "level": None,
    }
  return {
    "allowed": allowed,
    "reason": None if allowed else reason,
    "family_key": family_key,
    "surface_key": surface_key,
    "rule_key": rule.rule_key,
    "enforcement_mode": rule.enforcement_mode,
    "level": rule.level,
  }


def _resolve_run_action_unavailability_reason(run: RunRecord, action_key: str) -> str | None:
  if action_key == "compare_select":
    return None
  if action_key.startswith("rerun_"):
    if run.provenance.rerun_boundary_id is None:
      return "Run has no rerun boundary to replay."
    return None
  if action_key == "stop_run":
    if run.config.mode not in {RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE}:
      return "Only sandbox, paper, or live runs can be stopped by the operator."
    if run.status not in {RunStatus.RUNNING, RunStatus.FAILED}:
      return f"Run status {run.status.value} is not stoppable."
    return None
  raise ValueError(f"Unsupported run action availability key: {action_key}")


def _build_run_action_availability(
  *,
  run: RunRecord,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, dict[str, Any]]:
  rerun_reason = _resolve_run_action_unavailability_reason(run, "rerun_backtest")
  stop_reason = _resolve_run_action_unavailability_reason(run, "stop_run")
  return {
    "compare_select": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="compare_selection_workflow",
      allowed=True,
      reason=None,
    ),
    "rerun_backtest": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=rerun_reason is None,
      reason=rerun_reason,
    ),
    "rerun_sandbox": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=rerun_reason is None,
      reason=rerun_reason,
    ),
    "rerun_paper": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=rerun_reason is None,
      reason=rerun_reason,
    ),
    "stop_run": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=stop_reason is None,
      reason=stop_reason,
    ),
  }


def _resolve_order_action_unavailability_reason(
  *,
  run: RunRecord,
  order: Order,
  action_key: str,
) -> str | None:
  if run.config.mode != RunMode.LIVE:
    return "Guarded-live order controls are available only for live runs."
  if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
    return "Only active guarded-live venue orders can be controlled."
  if action_key in {"cancel", "replace"}:
    return None
  raise ValueError(f"Unsupported order action availability key: {action_key}")


def _build_order_action_availability(
  *,
  run: RunRecord,
  order: Order,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, dict[str, Any]]:
  cancel_reason = _resolve_order_action_unavailability_reason(run=run, order=order, action_key="cancel")
  replace_reason = _resolve_order_action_unavailability_reason(run=run, order=order, action_key="replace")
  return {
    "cancel": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="order_replace_cancel_actions",
      allowed=cancel_reason is None,
      reason=cancel_reason,
    ),
    "replace": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="order_replace_cancel_actions",
      allowed=replace_reason is None,
      reason=replace_reason,
    ),
  }


def _ensure_run_action_allowed(
  *,
  run: RunRecord,
  capabilities: RunSurfaceCapabilities,
  action_key: str,
) -> None:
  entry = _build_run_action_availability(run=run, capabilities=capabilities)[action_key]
  if entry["allowed"]:
    return
  raise ValueError(entry["reason"] or f"Run action {action_key} is unavailable.")


def _ensure_order_action_allowed(
  *,
  run: RunRecord,
  order: Order,
  capabilities: RunSurfaceCapabilities,
  action_key: str,
) -> None:
  entry = _build_order_action_availability(
    run=run,
    order=order,
    capabilities=capabilities,
  )[action_key]
  if entry["allowed"]:
    return
  raise ValueError(entry["reason"] or f"Order action {action_key} is unavailable.")


def serialize_run(run: RunRecord, *, capabilities: RunSurfaceCapabilities | None = None) -> dict[str, Any]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  payload = asdict(run)
  payload["config"]["mode"] = run.config.mode.value
  payload["status"] = run.status.value
  payload["provenance"]["external_command"] = list(run.provenance.external_command)
  payload["provenance"]["artifact_paths"] = list(run.provenance.artifact_paths)
  payload["provenance"]["experiment"]["tags"] = list(run.provenance.experiment.tags)
  payload["provenance"]["benchmark_artifacts"] = [
    asdict(artifact)
    for artifact in run.provenance.benchmark_artifacts
  ]
  payload["provenance"]["lineage_summary"] = serialize_operator_lineage_summary(
    build_operator_lineage_summary(run=run)
  )
  if run.provenance.market_data is not None:
    payload["provenance"]["market_data"]["dataset_boundary"] = serialize_dataset_boundary_contract(
      build_dataset_boundary_contract(lineage=run.provenance.market_data)
    )
  for symbol, lineage in run.provenance.market_data_by_symbol.items():
    symbol_payload = payload["provenance"]["market_data_by_symbol"].get(symbol)
    if symbol_payload is None:
      continue
    symbol_payload["dataset_boundary"] = serialize_dataset_boundary_contract(
      build_dataset_boundary_contract(lineage=lineage)
    )
  strategy_snapshot = payload["provenance"].get("strategy")
  if strategy_snapshot is not None:
    strategy_snapshot["version_lineage"] = list(
      run.provenance.strategy.version_lineage or (run.provenance.strategy.version,)
    )
    run_snapshot_rule = _get_run_surface_capability_surface_rule(
      resolved_capabilities,
      "provenance_semantics",
      "run_strategy_snapshot",
    )
    if run_snapshot_rule is None:
      strategy_snapshot["catalog_semantics"] = {
        "strategy_kind": "",
        "execution_model": "",
        "parameter_contract": "",
        "source_descriptor": None,
        "operator_notes": [],
      }
    else:
      strategy_snapshot["catalog_semantics"]["operator_notes"] = list(
        run.provenance.strategy.catalog_semantics.operator_notes
      )
    strategy_snapshot["supported_timeframes"] = list(run.provenance.strategy.supported_timeframes)
    strategy_snapshot["warmup"]["timeframes"] = list(run.provenance.strategy.warmup.timeframes)
  payload["surface_enforcement"] = _build_run_surface_enforcement(resolved_capabilities)
  payload["action_availability"] = _build_run_action_availability(
    run=run,
    capabilities=resolved_capabilities,
  )
  for order_payload, order in zip(payload["orders"], run.orders, strict=True):
    order_payload["action_availability"] = _build_order_action_availability(
      run=run,
      order=order,
      capabilities=resolved_capabilities,
    )
  return payload


def _serialize_run_subresource_envelope(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
  body_key: str,
  body_value: Any,
) -> dict[str, Any]:
  return {
    "run_id": run.config.run_id,
    "run_mode": run.config.mode.value,
    "run_status": run.status.value,
    "surface_enforcement": _build_run_surface_enforcement(capabilities),
    "action_availability": _build_run_action_availability(
      run=run,
      capabilities=capabilities,
    ),
    body_key: body_value,
  }
