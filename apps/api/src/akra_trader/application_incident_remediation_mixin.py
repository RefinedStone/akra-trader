from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationIncidentRemediationMixin:
  @staticmethod
  def _summarize_guarded_live_issue_copy(details: list[str]) -> str:
    unique_details = list(dict.fromkeys(details))
    return " ".join(unique_details[:3]) + (
      f" Additional issues: {len(unique_details) - 3}."
      if len(unique_details) > 3
      else ""
    )
  def _build_guarded_live_incident_events(
    self,
    *,
    previous_history: tuple[OperatorAlert, ...],
    merged_history: tuple[OperatorAlert, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, ...]:
    return guarded_live_incident_event_construction_support._build_guarded_live_incident_events(
      self,
      previous_history=previous_history,
      merged_history=merged_history,
      current_time=current_time,
    )
  @staticmethod
  def _normalize_targets(targets: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(targets))
  @staticmethod
  def _normalize_paging_provider(provider: str | None) -> str | None:
    if provider is None:
      return None
    normalized = provider.strip().lower().replace("-", "_").replace(".", "_")
    if normalized == "incident_io":
      return "incidentio"
    if normalized == "fire_hydrant":
      return "firehydrant"
    if normalized == "root_ly":
      return "rootly"
    if normalized == "blame_less":
      return "blameless"
    if normalized == "x_matters":
      return "xmatters"
    if normalized == "service_now":
      return "servicenow"
    if normalized == "squad_cast":
      return "squadcast"
    if normalized == "big_panda":
      return "bigpanda"
    if normalized == "zen_duty":
      return "zenduty"
    if normalized == "victorops":
      return "splunk_oncall"
    if normalized in {"jsm", "jira_service_desk"}:
      return "jira_service_management"
    if normalized == "pager_tree":
      return "pagertree"
    if normalized == "alert_ops":
      return "alertops"
    if normalized == "signl_4":
      return "signl4"
    if normalized in {"i_lert", "ilert_alerts", "operator_ilert"}:
      return "ilert"
    if normalized in {"better_stack", "betterstack_alerts", "operator_betterstack"}:
      return "betterstack"
    if normalized in {"grafana_oncall_incidents", "grafanaoncall", "operator_grafana_oncall"}:
      return "grafana_oncall"
    if normalized in {"zenduty_incidents", "operator_zenduty"}:
      return "zenduty"
    if normalized in {"splunk_oncall_incidents", "splunkoncall", "operator_splunk_oncall"}:
      return "splunk_oncall"
    if normalized in {
      "jira_service_management_incidents",
      "jira_service_desk_incidents",
      "operator_jira_service_management",
      "jsm_incidents",
    }:
      return "jira_service_management"
    if normalized in {"pagertree_incidents", "operator_pagertree"}:
      return "pagertree"
    if normalized in {"alertops_incidents", "operator_alertops"}:
      return "alertops"
    if normalized in {"signl4_incidents", "operator_signl4"}:
      return "signl4"
    if normalized in {"ilert_incidents", "ilert_alerts", "operator_ilert"}:
      return "ilert"
    if normalized in {"betterstack_incidents", "betterstack_alerts", "operator_betterstack"}:
      return "betterstack"
    if normalized in {"on_page", "onpage_alerts", "operator_onpage"}:
      return "onpage"
    if normalized in {"onpage_incidents", "operator_onpage"}:
      return "onpage"
    if normalized in {"all_quiet", "allquiet_alerts", "operator_allquiet"}:
      return "allquiet"
    if normalized in {"allquiet_incidents", "operator_allquiet"}:
      return "allquiet"
    if normalized in {"moogsoft_alerts", "operator_moogsoft"}:
      return "moogsoft"
    if normalized in {"moogsoft_incidents", "operator_moogsoft"}:
      return "moogsoft"
    if normalized in {"spikesh_alerts", "spike_sh", "operator_spikesh"}:
      return "spikesh"
    if normalized in {"spikesh_incidents", "operator_spikesh"}:
      return "spikesh"
    if normalized in {"dutycalls_alerts", "duty_calls", "operator_dutycalls"}:
      return "dutycalls"
    if normalized in {"dutycalls_incidents", "operator_dutycalls"}:
      return "dutycalls"
    if normalized in {"incidenthub_alerts", "incident_hub", "operator_incidenthub"}:
      return "incidenthub"
    if normalized in {"incidenthub_incidents", "operator_incidenthub"}:
      return "incidenthub"
    if normalized in {"resolver_alerts", "operator_resolver"}:
      return "resolver"
    if normalized in {"resolver_incidents", "operator_resolver"}:
      return "resolver"
    if normalized in {"openduty_alerts", "open_duty", "operator_openduty"}:
      return "openduty"
    if normalized in {"openduty_incidents", "operator_openduty"}:
      return "openduty"
    if normalized in {"cabot_alerts", "operator_cabot"}:
      return "cabot"
    if normalized in {"cabot_incidents", "operator_cabot"}:
      return "cabot"
    if normalized in {"haloitsm_alerts", "halo_itsm", "operator_haloitsm"}:
      return "haloitsm"
    if normalized in {"haloitsm_incidents", "operator_haloitsm"}:
      return "haloitsm"
    if normalized in {
      "incidentmanagerio_alerts",
      "incidentmanagerio",
      "incidentmanager_io",
      "operator_incidentmanagerio",
    }:
      return "incidentmanagerio"
    if normalized in {"incidentmanagerio_incidents", "operator_incidentmanagerio"}:
      return "incidentmanagerio"
    if normalized in {"oneuptime_alerts", "one_uptime", "operator_oneuptime"}:
      return "oneuptime"
    if normalized in {"oneuptime_incidents", "operator_oneuptime"}:
      return "oneuptime"
    if normalized in {"squzy_alerts", "operator_squzy"}:
      return "squzy"
    if normalized in {"squzy_incidents", "operator_squzy"}:
      return "squzy"
    if normalized in {
      "crisescontrol_alerts",
      "crises_control",
      "crisescontrol",
      "operator_crisescontrol",
    }:
      return "crisescontrol"
    if normalized in {"crisescontrol_incidents", "operator_crisescontrol"}:
      return "crisescontrol"
    if normalized in {"freshservice_alerts", "fresh_service", "freshservice", "operator_freshservice"}:
      return "freshservice"
    if normalized in {"freshservice_incidents", "operator_freshservice"}:
      return "freshservice"
    if normalized in {"freshdesk_alerts", "freshdesk", "operator_freshdesk"}:
      return "freshdesk"
    if normalized in {"freshdesk_incidents", "operator_freshdesk"}:
      return "freshdesk"
    if normalized in {"happyfox_alerts", "happyfox", "operator_happyfox"}:
      return "happyfox"
    if normalized in {"happyfox_incidents", "operator_happyfox"}:
      return "happyfox"
    if normalized in {"zendesk_alerts", "zendesk", "operator_zendesk"}:
      return "zendesk"
    if normalized in {"zendesk_incidents", "operator_zendesk"}:
      return "zendesk"
    if normalized in {"zohodesk_alerts", "zohodesk", "zoho_desk", "operator_zohodesk"}:
      return "zohodesk"
    if normalized in {"zohodesk_incidents", "operator_zohodesk"}:
      return "zohodesk"
    if normalized in {"helpscout_alerts", "helpscout", "help_scout", "operator_helpscout"}:
      return "helpscout"
    if normalized in {"helpscout_incidents", "operator_helpscout"}:
      return "helpscout"
    if normalized in {"kayako_alerts", "kayako", "operator_kayako"}:
      return "kayako"
    if normalized in {"kayako_incidents", "operator_kayako"}:
      return "kayako"
    if normalized in {"intercom_alerts", "intercom", "operator_intercom"}:
      return "intercom"
    if normalized in {"intercom_incidents", "operator_intercom"}:
      return "intercom"
    if normalized in {"front_alerts", "front", "operator_front"}:
      return "front"
    if normalized in {"front_incidents", "operator_front"}:
      return "front"
    if normalized in {
      "servicedeskplus_alerts",
      "servicedeskplus",
      "service_desk_plus",
      "manageengine_servicedesk_plus",
      "operator_servicedeskplus",
    }:
      return "servicedeskplus"
    if normalized in {"servicedeskplus_incidents", "operator_servicedeskplus"}:
      return "servicedeskplus"
    if normalized in {"bmchelix_alerts", "bmchelix", "bmc_helix", "operator_bmchelix"}:
      return "bmchelix"
    if normalized in {"bmchelix_incidents", "operator_bmchelix"}:
      return "bmchelix"
    if normalized in {
      "solarwindsservicedesk_alerts",
      "solarwindsservicedesk",
      "solarwinds_service_desk",
      "operator_solarwindsservicedesk",
    }:
      return "solarwindsservicedesk"
    if normalized in {"solarwindsservicedesk_incidents", "operator_solarwindsservicedesk"}:
      return "solarwindsservicedesk"
    if normalized in {
      "invgateservicedesk_alerts",
      "invgateservicedesk",
      "invgate_service_desk",
      "invgate_servicedesk",
      "operator_invgateservicedesk",
    }:
      return "invgateservicedesk"
    if normalized in {"invgateservicedesk_incidents", "operator_invgateservicedesk"}:
      return "invgateservicedesk"
    if normalized in {"topdesk_alerts", "topdesk", "operator_topdesk"}:
      return "topdesk"
    if normalized in {"topdesk_incidents", "operator_topdesk"}:
      return "topdesk"
    if normalized in {"sysaid_alerts", "sysaid", "sys_aid", "operator_sysaid"}:
      return "sysaid"
    if normalized in {"sysaid_incidents", "operator_sysaid"}:
      return "sysaid"
    if normalized in {"opsramp_alerts", "ops_ramp", "operator_opsramp"}:
      return "opsramp"
    if normalized in {"opsramp_incidents", "operator_opsramp"}:
      return "opsramp"
    return normalized or None
  @staticmethod
  def _alert_supports_remediation(*, alert: OperatorAlert) -> bool:
    return alert.source == "guarded_live" and alert.category.startswith("market_data_")
  @staticmethod
  def _market_data_remediation_plan(*, category: str) -> _IncidentRemediationPlan:
    if category == "market_data_freshness":
      return _IncidentRemediationPlan(
        kind="recent_sync",
        owner="provider",
        summary="Refresh the live timeframe sync window and verify freshness thresholds.",
        detail=(
          "Trigger provider-owned recent sync for the affected timeframe, then confirm the "
          "latest checkpoint, sync timestamp, and freshness window have recovered."
        ),
        runbook="market_data.sync_recent",
      )
    if category == "market_data_quality":
      return _IncidentRemediationPlan(
        kind="historical_backfill",
        owner="provider",
        summary="Backfill the historical window to the configured target coverage.",
        detail=(
          "Run provider-owned historical backfill, then verify target coverage and completion "
          "ratio against the guarded-live backfill policy."
        ),
        runbook="market_data.backfill_history",
      )
    if category in {"market_data_candle_continuity", "market_data_candle_sequence", "market_data_kline_consistency"}:
      return _IncidentRemediationPlan(
        kind="candle_repair",
        owner="provider",
        summary="Repair candle continuity and restore the affected kline sequence.",
        detail=(
          "Backfill the affected candle range, verify contiguous candle boundaries, and confirm "
          "the kline stream has resumed with valid ordering."
        ),
        runbook="market_data.repair_candles",
      )
    if category == "market_data_venue":
      return _IncidentRemediationPlan(
        kind="venue_fault_review",
        owner="provider",
        summary="Review upstream venue faults and re-run the affected sync path.",
        detail=(
          "Escalate the venue-specific upstream fault, then retry provider-owned market-data sync "
          "for the affected instrument and timeframe."
        ),
        runbook="market_data.review_venue_fault",
      )
    if category in {"market_data_channel_consistency", "market_data_channel_restore"}:
      return _IncidentRemediationPlan(
        kind="channel_restore",
        owner="provider",
        summary="Restore stale or missing guarded-live market-data channels.",
        detail=(
          "Restart or resubscribe the affected market-data channels, then confirm the guarded-live "
          "handoff is receiving fresh events for every covered channel."
        ),
        runbook="market_data.restore_channels",
      )
    if category in {
      "market_data_ladder_integrity",
      "market_data_venue_ladder_integrity",
      "market_data_ladder_bridge_integrity",
      "market_data_ladder_sequence_integrity",
      "market_data_ladder_snapshot_refresh",
      "market_data_depth_ladder",
      "market_data_book_consistency",
    }:
      return _IncidentRemediationPlan(
        kind="order_book_rebuild",
        owner="provider",
        summary="Rebuild the venue ladder and restore order-book integrity checks.",
        detail=(
          "Trigger provider-owned depth snapshot rebuild, replay the exchange bridge rules, and "
          "verify the local ladder, top-of-book, and snapshot refresh state are healthy again."
        ),
        runbook="market_data.rebuild_order_book",
      )
    return _IncidentRemediationPlan(
      kind="market_data_review",
      owner="provider",
      summary="Review the affected market-data policy path and restore normal coverage.",
      detail=(
        "Inspect the degraded guarded-live market-data path, trigger the provider-owned recovery "
        "workflow, and verify the affected policy has recovered."
      ),
      runbook="market_data.review_policy_fault",
    )
  def _build_incident_remediation(
    self,
    *,
    alert: OperatorAlert,
    policy: _IncidentPagingPolicy,
  ) -> OperatorIncidentRemediation:
    if not self._alert_supports_remediation(alert=alert):
      return OperatorIncidentRemediation()
    plan = self._market_data_remediation_plan(category=alert.category)
    owner = "provider" if policy.provider and plan.owner == "provider" else "operator"
    if alert.status == "resolved":
      state = "completed"
    elif owner == "provider":
      state = "suggested"
    else:
      state = "operator_review"
    return OperatorIncidentRemediation(
      state=state,
      kind=plan.kind,
      owner=owner,
      summary=plan.summary,
      detail=plan.detail,
      runbook=plan.runbook,
      provider=self._normalize_paging_provider(policy.provider),
    )
  def _resolve_incident_paging_policy(self, *, alert: OperatorAlert) -> _IncidentPagingPolicy:
    severity = alert.severity.strip().lower()
    policy_id = "default"
    initial_targets = self._operator_alert_delivery.list_targets()
    escalation_targets = self._operator_alert_escalation_targets or initial_targets
    if severity in {"critical", "error"}:
      policy_id = "severity:critical"
      if self._operator_alert_paging_policy_critical_targets:
        initial_targets = self._operator_alert_paging_policy_critical_targets
      if self._operator_alert_paging_policy_critical_escalation_targets:
        escalation_targets = self._operator_alert_paging_policy_critical_escalation_targets
    elif severity in {"warning", "warn"}:
      policy_id = "severity:warning"
      if self._operator_alert_paging_policy_warning_targets:
        initial_targets = self._operator_alert_paging_policy_warning_targets
      if self._operator_alert_paging_policy_warning_escalation_targets:
        escalation_targets = self._operator_alert_paging_policy_warning_escalation_targets

    initial_targets = self._normalize_targets(initial_targets)
    escalation_targets = self._normalize_targets(escalation_targets)
    resolution_targets = self._normalize_targets((*initial_targets, *escalation_targets))
    provider = self._operator_alert_paging_policy_default_provider or self._infer_paging_provider(
      initial_targets=initial_targets,
      escalation_targets=escalation_targets,
    )
    return _IncidentPagingPolicy(
      policy_id=policy_id,
      provider=provider,
      initial_targets=initial_targets,
      escalation_targets=escalation_targets,
      resolution_targets=resolution_targets,
    )
  @staticmethod
  def _infer_paging_provider(
    *,
    initial_targets: tuple[str, ...],
    escalation_targets: tuple[str, ...],
  ) -> str | None:
    combined = {target.strip().lower().replace("-", "_") for target in (*initial_targets, *escalation_targets)}
    if "pagerduty_events" in combined:
      return "pagerduty"
    if "incidentio_incidents" in combined:
      return "incidentio"
    if "firehydrant_incidents" in combined:
      return "firehydrant"
    if "rootly_incidents" in combined:
      return "rootly"
    if "blameless_incidents" in combined:
      return "blameless"
    if "xmatters_incidents" in combined:
      return "xmatters"
    if "servicenow_incidents" in combined:
      return "servicenow"
    if "squadcast_incidents" in combined:
      return "squadcast"
    if "bigpanda_incidents" in combined:
      return "bigpanda"
    if "grafana_oncall_incidents" in combined:
      return "grafana_oncall"
    if "zenduty_incidents" in combined:
      return "zenduty"
    if "splunk_oncall_incidents" in combined:
      return "splunk_oncall"
    if "jira_service_management_incidents" in combined or "jsm_incidents" in combined:
      return "jira_service_management"
    if "pagertree_incidents" in combined:
      return "pagertree"
    if "alertops_incidents" in combined:
      return "alertops"
    if "signl4_incidents" in combined:
      return "signl4"
    if "ilert_incidents" in combined or "ilert_alerts" in combined:
      return "ilert"
    if "betterstack_incidents" in combined or "betterstack_alerts" in combined:
      return "betterstack"
    if "onpage_incidents" in combined or "onpage_alerts" in combined:
      return "onpage"
    if "allquiet_incidents" in combined or "allquiet_alerts" in combined:
      return "allquiet"
    if "moogsoft_incidents" in combined or "moogsoft_alerts" in combined:
      return "moogsoft"
    if "spikesh_incidents" in combined or "spikesh_alerts" in combined:
      return "spikesh"
    if "dutycalls_incidents" in combined or "dutycalls_alerts" in combined:
      return "dutycalls"
    if "incidenthub_incidents" in combined or "incidenthub_alerts" in combined:
      return "incidenthub"
    if "resolver_incidents" in combined or "resolver_alerts" in combined:
      return "resolver"
    if "openduty_incidents" in combined or "openduty_alerts" in combined:
      return "openduty"
    if "cabot_incidents" in combined or "cabot_alerts" in combined:
      return "cabot"
    if "haloitsm_incidents" in combined or "haloitsm_alerts" in combined:
      return "haloitsm"
    if "incidentmanagerio_incidents" in combined or "incidentmanagerio_alerts" in combined:
      return "incidentmanagerio"
    if "oneuptime_incidents" in combined or "oneuptime_alerts" in combined:
      return "oneuptime"
    if "squzy_incidents" in combined or "squzy_alerts" in combined:
      return "squzy"
    if "crisescontrol_incidents" in combined or "crisescontrol_alerts" in combined:
      return "crisescontrol"
    if "freshservice_incidents" in combined or "freshservice_alerts" in combined:
      return "freshservice"
    if "freshdesk_incidents" in combined or "freshdesk_alerts" in combined:
      return "freshdesk"
    if "happyfox_incidents" in combined or "happyfox_alerts" in combined:
      return "happyfox"
    if "zendesk_incidents" in combined or "zendesk_alerts" in combined:
      return "zendesk"
    if "zohodesk_incidents" in combined or "zohodesk_alerts" in combined:
      return "zohodesk"
    if "helpscout_incidents" in combined or "helpscout_alerts" in combined:
      return "helpscout"
    if "kayako_incidents" in combined or "kayako_alerts" in combined:
      return "kayako"
    if "intercom_incidents" in combined or "intercom_alerts" in combined:
      return "intercom"
    if "front_incidents" in combined or "front_alerts" in combined:
      return "front"
    if "servicedeskplus_incidents" in combined or "servicedeskplus_alerts" in combined:
      return "servicedeskplus"
    if "bmchelix_incidents" in combined or "bmchelix_alerts" in combined:
      return "bmchelix"
    if (
      "solarwindsservicedesk_incidents" in combined
      or "solarwindsservicedesk_alerts" in combined
    ):
      return "solarwindsservicedesk"
    if "invgateservicedesk_incidents" in combined or "invgateservicedesk_alerts" in combined:
      return "invgateservicedesk"
    if "topdesk_incidents" in combined or "topdesk_alerts" in combined:
      return "topdesk"
    if "sysaid_incidents" in combined or "sysaid_alerts" in combined:
      return "sysaid"
    if "opsramp_incidents" in combined or "opsramp_alerts" in combined:
      return "opsramp"
    if "opsgenie_alerts" in combined:
      return "opsgenie"
    return None
  def _deliver_guarded_live_incident_events(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    bool,
  ]:
    return guarded_live_delivery_orchestration_support._deliver_guarded_live_incident_events(
      self,
      incident_events=incident_events,
      current_time=current_time,
    )
  def _retry_guarded_live_incident_deliveries(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    return guarded_live_delivery_orchestration_support._retry_guarded_live_incident_deliveries(
      self,
      incident_events=incident_events,
      delivery_history=delivery_history,
      current_time=current_time,
    )
  def _collect_due_incident_retries(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[tuple[str, str, int], ...]:
    return guarded_live_incident_support._collect_due_incident_retries(self, incident_events=incident_events, delivery_history=delivery_history, current_time=current_time)
  def _apply_incident_delivery_state(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> tuple[OperatorIncidentEvent, ...]:
    return guarded_live_incident_support._apply_incident_delivery_state(self, incident_events=incident_events, delivery_history=delivery_history)
  def _refresh_incident_remediation_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    latest_by_key: dict[tuple[str, str, str], OperatorIncidentDelivery],
  ) -> OperatorIncidentRemediation:
    return guarded_live_incident_support._refresh_incident_remediation_state(self, incident=incident, latest_by_key=latest_by_key)
  def _request_incident_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    actor: str,
    detail: str,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...]]:
    return guarded_live_remediation_orchestration_support._request_incident_remediation(
      self,
      incident=incident,
      delivery_history=delivery_history,
      current_time=current_time,
      actor=actor,
      detail=detail,
    )
  def _resolve_remediation_delivery_state(
    self,
    *,
    records: tuple[OperatorIncidentDelivery, ...],
    current_state: str,
  ) -> str:
    return guarded_live_incident_support._resolve_remediation_delivery_state(self, records=records, current_state=current_state)
  def _execute_local_incident_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    actor: str,
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, tuple[MarketDataRemediationResult, ...]]:
    return guarded_live_remediation_orchestration_support._execute_local_incident_remediation(
      self,
      incident=incident,
      actor=actor,
      current_time=current_time,
    )
  def _execute_local_guarded_live_session_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    actor: str,
    current_time: datetime,
  ) -> tuple[MarketDataRemediationResult, ...]:
    return guarded_live_remediation_orchestration_support._execute_local_guarded_live_session_remediation(
      self,
      incident=incident,
      actor=actor,
      current_time=current_time,
    )
  def _resolve_guarded_live_remediation_run(
    self,
    *,
    incident: OperatorIncidentEvent,
    state: GuardedLiveState,
  ) -> RunRecord | None:
    return guarded_live_remediation_support._resolve_guarded_live_remediation_run(self, incident=incident, state=state)
  @staticmethod
  def _resolve_guarded_live_remediation_identity(
    *,
    run: RunRecord | None,
    state: GuardedLiveState,
  ) -> tuple[str, str]:
    return guarded_live_remediation_support._resolve_guarded_live_remediation_identity(run=run, state=state)
  def _build_guarded_live_state_for_local_session_remediation(
    self,
    *,
    state: GuardedLiveState,
    run: RunRecord,
    actor: str,
    reason: str,
    session_handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveState:
    return guarded_live_remediation_support._build_guarded_live_state_for_local_session_remediation(self, state=state, run=run, actor=actor, reason=reason, session_handoff=session_handoff)
  @staticmethod
  def _summarize_guarded_live_session_remediation_result(
    *,
    remediation_kind: str,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> str:
    return guarded_live_remediation_support._summarize_guarded_live_session_remediation_result(remediation_kind=remediation_kind, handoff=handoff)
  def _resolve_market_data_remediation_targets(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> tuple[str | None, tuple[str, ...]]:
    return guarded_live_remediation_support._resolve_market_data_remediation_targets(self, incident=incident)
  @staticmethod
  def _resolve_local_remediation_state(
    *,
    results: tuple[MarketDataRemediationResult, ...],
  ) -> str:
    return guarded_live_remediation_support._resolve_local_remediation_state(results=results)
  @staticmethod
  def _summarize_local_remediation_results(
    results: tuple[MarketDataRemediationResult, ...],
  ) -> str:
    return guarded_live_remediation_support._summarize_local_remediation_results(results)
  def _pull_sync_guarded_live_provider_recovery(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    tuple[OperatorAuditEvent, ...],
    bool,
  ]:
    return guarded_live_pull_sync_orchestration_support._pull_sync_guarded_live_provider_recovery(
      self,
      incident_events=incident_events,
      delivery_history=delivery_history,
      current_time=current_time,
    )
  def _apply_provider_pull_sync(
    self,
    *,
    incident: OperatorIncidentEvent,
    pull_sync: OperatorIncidentProviderPullSync,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...], bool]:
    return guarded_live_pull_sync_orchestration_support._apply_provider_pull_sync(
      self,
      incident=incident,
      pull_sync=pull_sync,
      delivery_history=delivery_history,
      current_time=current_time,
    )
  def _resolve_provider_pull_sync_event_kind(
    self,
    *,
    incident: OperatorIncidentEvent,
    pull_sync: OperatorIncidentProviderPullSync,
    payload: dict[str, Any],
  ) -> str | None:
    return guarded_live_payload_helpers_support._resolve_provider_pull_sync_event_kind(self, incident=incident, pull_sync=pull_sync, payload=payload)
  def _refresh_guarded_live_incident_workflow(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    tuple[OperatorAuditEvent, ...],
  ]:
    return guarded_live_incident_workflow_orchestration_support._refresh_guarded_live_incident_workflow(
      self,
      incident_events=incident_events,
      delivery_history=delivery_history,
      current_time=current_time,
    )
  def _apply_delivery_retry_policy(
    self,
    *,
    records: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    return guarded_live_incident_support._apply_delivery_retry_policy(self, records=records, current_time=current_time)
  def _resolve_delivery_backoff_seconds(self, attempt_number: int) -> int:
    return guarded_live_incident_support._resolve_delivery_backoff_seconds(self, attempt_number)
  @staticmethod
  def _resolve_incident_delivery_state(
    *,
    records: tuple[OperatorIncidentDelivery, ...],
  ) -> str:
    return guarded_live_incident_support._resolve_incident_delivery_state(records=records)
  @staticmethod
  def _latest_delivery_records_by_key(
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> dict[tuple[str, str, str], OperatorIncidentDelivery]:
    return guarded_live_incident_support._latest_delivery_records_by_key(delivery_history=delivery_history)
  def _latest_incident_delivery_record(
    self,
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident_event_id: str,
    target: str,
  ) -> OperatorIncidentDelivery | None:
    return guarded_live_incident_support._latest_incident_delivery_record(self, delivery_history=delivery_history, incident_event_id=incident_event_id, target=target)
  @staticmethod
  def _latest_provider_workflow_record(
    *,
    records: tuple[OperatorIncidentDelivery, ...],
  ) -> OperatorIncidentDelivery | None:
    return guarded_live_incident_support._latest_provider_workflow_record(records=records)
  @staticmethod
  def _replace_incident_event(
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    updated_incident: OperatorIncidentEvent,
  ) -> tuple[OperatorIncidentEvent, ...]:
    return guarded_live_incident_support._replace_incident_event(incident_events=incident_events, updated_incident=updated_incident)
  @staticmethod
  def _incident_is_still_active(
    *,
    incident: OperatorIncidentEvent,
    incident_events: tuple[OperatorIncidentEvent, ...],
  ) -> bool:
    return guarded_live_incident_support._incident_is_still_active(incident=incident, incident_events=incident_events)
  @staticmethod
  def _find_latest_open_incident_for_alert(
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    alert_id: str,
    resolved_at: datetime,
  ) -> OperatorIncidentEvent | None:
    return guarded_live_incident_support._find_latest_open_incident_for_alert(incident_events=incident_events, alert_id=alert_id, resolved_at=resolved_at)
  @staticmethod
  def _incident_has_provider_workflow_phase(
    *,
    incident_event_id: str,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    phase: str,
  ) -> bool:
    return guarded_live_incident_support._incident_has_provider_workflow_phase(incident_event_id=incident_event_id, delivery_history=delivery_history, phase=phase)
  def _require_active_guarded_live_incident(
    self,
    *,
    state: GuardedLiveState,
    event_id: str,
  ) -> OperatorIncidentEvent:
    return guarded_live_incident_support._require_active_guarded_live_incident(self, state=state, event_id=event_id)
  def _find_guarded_live_incident_for_external_sync(
    self,
    *,
    state: GuardedLiveState,
    alert_id: str | None,
    external_reference: str | None,
  ) -> OperatorIncidentEvent:
    return guarded_live_incident_support._find_guarded_live_incident_for_external_sync(self, state=state, alert_id=alert_id, external_reference=external_reference)
