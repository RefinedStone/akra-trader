from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from datetime import timedelta
from typing import Any

from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorAuditEvent

def sync_guarded_live_incident_from_external(
  app,
  *,
  provider: str,
  event_kind: str,
  actor: str,
  detail: str,
  alert_id: str | None = None,
  external_reference: str | None = None,
  workflow_reference: str | None = None,
  occurred_at: datetime | None = None,
  escalation_level: int | None = None,
  payload: dict[str, Any] | None = None,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state, _ = app._refresh_guarded_live_alert_state(current_time=current_time)
  synced_at = occurred_at or current_time
  normalized_provider = provider.strip().lower().replace(" ", "_")
  normalized_kind = app._normalize_external_incident_event_kind(event_kind)
  normalized_payload = app._normalize_incident_workflow_payload(payload)
  incident = app._find_guarded_live_incident_for_external_sync(
    state=state,
    alert_id=alert_id,
    external_reference=external_reference,
  )
  payload_reference = app._extract_incident_payload_reference(normalized_payload)
  provider_workflow_reference = (
    workflow_reference
    or app._first_non_empty_string(
      normalized_payload.get("workflow_reference"),
      normalized_payload.get("provider_workflow_reference"),
    )
  )
  effective_reference = (
    external_reference
    or payload_reference
    or incident.external_reference
    or alert_id
    or incident.alert_id
  )
  detail_copy = (
    detail.strip()
    or app._first_non_empty_string(
      normalized_payload.get("detail"),
      normalized_payload.get("remediation_detail"),
      normalized_payload.get("status_detail"),
      normalized_payload.get("summary"),
      normalized_payload.get("message"),
    )
    or f"{normalized_provider}_{normalized_kind}"
  )
  updated_incident = replace(
    incident,
    paging_provider=normalized_provider or incident.paging_provider,
    external_provider=normalized_provider,
    external_reference=effective_reference,
    provider_workflow_reference=provider_workflow_reference or incident.provider_workflow_reference,
    external_last_synced_at=synced_at,
  )
  incident_market_context = app._extract_operator_alert_market_context_from_workflow_payload(
    payload=normalized_payload,
    existing_symbol=updated_incident.symbol,
    existing_symbols=updated_incident.symbols,
    existing_timeframe=updated_incident.timeframe,
    existing_primary_focus=updated_incident.primary_focus,
  )
  updated_incident = replace(
    updated_incident,
    symbol=incident_market_context["symbol"],
    symbols=incident_market_context["symbols"],
    timeframe=incident_market_context["timeframe"],
    primary_focus=incident_market_context["primary_focus"],
  )
  delivery_history = state.delivery_history
  local_results: tuple[MarketDataRemediationResult, ...] = ()
  workflow_reference_for_delivery = (
    provider_workflow_reference
    or incident.provider_workflow_reference
    or effective_reference
  )

  if normalized_kind == "triggered":
    updated_incident = replace(
      updated_incident,
      external_status="triggered",
      paging_status="triggered",
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  elif normalized_kind == "acknowledged":
    if updated_incident.acknowledgment_state != "acknowledged":
      updated_incident = replace(
        updated_incident,
        acknowledgment_state="acknowledged",
        acknowledged_at=synced_at,
        acknowledged_by=f"{normalized_provider}:{actor}",
        acknowledgment_reason=detail_copy,
        next_escalation_at=None,
      )
    updated_incident = replace(
      updated_incident,
      external_status="acknowledged",
      paging_status="acknowledged",
    )
    delivery_history = app._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_acknowledged:{normalized_provider}",
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  elif normalized_kind == "escalated":
    next_level = max(updated_incident.escalation_level + 1, escalation_level or 1)
    next_level = min(next_level, app._operator_alert_incident_max_escalations)
    next_escalation_at = None
    if (
      updated_incident.acknowledgment_state != "acknowledged"
      and next_level < app._operator_alert_incident_max_escalations
    ):
      next_escalation_at = synced_at + timedelta(
        seconds=app._resolve_incident_escalation_backoff_seconds(next_level)
      )
    updated_incident = replace(
      updated_incident,
      escalation_level=next_level,
      escalation_state="escalated",
      last_escalated_at=synced_at,
      last_escalated_by=f"{normalized_provider}:{actor}",
      escalation_reason=detail_copy,
      next_escalation_at=next_escalation_at,
      external_status="escalated",
      paging_status="escalated",
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  elif normalized_kind == "resolved":
    if updated_incident.acknowledgment_state != "acknowledged":
      updated_incident = replace(
        updated_incident,
        acknowledgment_state="acknowledged",
        acknowledged_at=synced_at,
        acknowledged_by=f"{normalized_provider}:{actor}",
        acknowledgment_reason=detail_copy,
      )
    updated_incident = replace(
      updated_incident,
      external_status="resolved",
      paging_status="resolved",
      next_escalation_at=None,
    )
    delivery_history = app._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_resolved:{normalized_provider}",
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  elif normalized_kind == "remediation_requested":
    delivery_history = app._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
    )
    updated_incident = app._apply_external_remediation_sync(
      incident=updated_incident,
      next_state="requested",
      event_kind=normalized_kind,
      provider=normalized_provider,
      actor=actor,
      detail=detail_copy,
      synced_at=synced_at,
      workflow_reference=workflow_reference_for_delivery,
      payload=normalized_payload,
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  elif normalized_kind == "remediation_started":
    delivery_history = app._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
    )
    updated_incident = app._apply_external_remediation_sync(
      incident=updated_incident,
      next_state="provider_recovering",
      event_kind=normalized_kind,
      provider=normalized_provider,
      actor=actor,
      detail=detail_copy,
      synced_at=synced_at,
      workflow_reference=workflow_reference_for_delivery,
      payload=normalized_payload,
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  elif normalized_kind == "remediation_completed":
    delivery_history = app._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
    )
    updated_incident = app._apply_external_remediation_sync(
      incident=updated_incident,
      next_state="provider_recovered",
      event_kind=normalized_kind,
      provider=normalized_provider,
      actor=actor,
      detail=detail_copy,
      synced_at=synced_at,
      workflow_reference=workflow_reference_for_delivery,
      payload=normalized_payload,
    )
    updated_incident, local_results = app._execute_local_incident_remediation(
      incident=updated_incident,
      actor=f"{normalized_provider}:{actor}",
      current_time=synced_at,
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  elif normalized_kind == "remediation_failed":
    delivery_history = app._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
    )
    updated_incident = app._apply_external_remediation_sync(
      incident=updated_incident,
      next_state="failed",
      event_kind=normalized_kind,
      provider=normalized_provider,
      actor=actor,
      detail=detail_copy,
      synced_at=synced_at,
      workflow_reference=workflow_reference_for_delivery,
      payload=normalized_payload,
    )
    delivery_history = app._confirm_external_provider_workflow(
      delivery_history=delivery_history,
      incident=incident,
      provider=normalized_provider,
      event_kind=normalized_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference_for_delivery,
    )
  else:
    raise ValueError(f"unsupported external incident event kind: {event_kind}")

  provider_phase = app._provider_phase_for_event_kind(normalized_kind)
  if provider_phase is not None:
    updated_incident = replace(
      updated_incident,
      provider_workflow_state="delivered",
      provider_workflow_action=provider_phase.removeprefix("provider_"),
      provider_workflow_reference=workflow_reference_for_delivery,
      provider_workflow_last_attempted_at=synced_at,
    )
    if updated_incident.remediation.state != "not_applicable":
      provider_recovery = updated_incident.remediation.provider_recovery
      generic_workflow_states = {"unknown", "idle", "not_supported", "retrying"}
      aligned_provider_recovery = provider_recovery
      if (
        normalized_provider == "pagerduty"
        and provider_recovery.pagerduty.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          pagerduty=replace(
            aligned_provider_recovery.pagerduty,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "opsgenie"
        and provider_recovery.opsgenie.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          opsgenie=replace(
            aligned_provider_recovery.opsgenie,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "incidentio"
        and provider_recovery.incidentio.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          incidentio=replace(
            aligned_provider_recovery.incidentio,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "firehydrant"
        and provider_recovery.firehydrant.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          firehydrant=replace(
            aligned_provider_recovery.firehydrant,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "rootly"
        and provider_recovery.rootly.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          rootly=replace(
            aligned_provider_recovery.rootly,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "blameless"
        and provider_recovery.blameless.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          blameless=replace(
            aligned_provider_recovery.blameless,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "xmatters"
        and provider_recovery.xmatters.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          xmatters=replace(
            aligned_provider_recovery.xmatters,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "servicenow"
        and provider_recovery.servicenow.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          servicenow=replace(
            aligned_provider_recovery.servicenow,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "squadcast"
        and provider_recovery.squadcast.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          squadcast=replace(
            aligned_provider_recovery.squadcast,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "bigpanda"
        and provider_recovery.bigpanda.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          bigpanda=replace(
            aligned_provider_recovery.bigpanda,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "grafana_oncall"
        and provider_recovery.grafana_oncall.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          grafana_oncall=replace(
            aligned_provider_recovery.grafana_oncall,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "zenduty"
        and provider_recovery.zenduty.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          zenduty=replace(
            aligned_provider_recovery.zenduty,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "splunk_oncall"
        and provider_recovery.splunk_oncall.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          splunk_oncall=replace(
            aligned_provider_recovery.splunk_oncall,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "jira_service_management"
        and provider_recovery.jira_service_management.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          jira_service_management=replace(
            aligned_provider_recovery.jira_service_management,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "pagertree"
        and provider_recovery.pagertree.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          pagertree=replace(
            aligned_provider_recovery.pagertree,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "alertops"
        and provider_recovery.alertops.incident_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          alertops=replace(
            aligned_provider_recovery.alertops,
            incident_status="delivered",
          ),
        )
      elif (
        normalized_provider == "signl4"
        and provider_recovery.signl4.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          signl4=replace(
            aligned_provider_recovery.signl4,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "ilert"
        and provider_recovery.ilert.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          ilert=replace(
            aligned_provider_recovery.ilert,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "betterstack"
        and provider_recovery.betterstack.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          betterstack=replace(
            aligned_provider_recovery.betterstack,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "onpage"
        and provider_recovery.onpage.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          onpage=replace(
            aligned_provider_recovery.onpage,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "allquiet"
        and provider_recovery.allquiet.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          allquiet=replace(
            aligned_provider_recovery.allquiet,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "moogsoft"
        and provider_recovery.moogsoft.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          moogsoft=replace(
            aligned_provider_recovery.moogsoft,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "spikesh"
        and provider_recovery.spikesh.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          spikesh=replace(
            aligned_provider_recovery.spikesh,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "dutycalls"
        and provider_recovery.dutycalls.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          dutycalls=replace(
            aligned_provider_recovery.dutycalls,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "incidenthub"
        and provider_recovery.incidenthub.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          incidenthub=replace(
            aligned_provider_recovery.incidenthub,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "resolver"
        and provider_recovery.resolver.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          resolver=replace(
            aligned_provider_recovery.resolver,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "openduty"
        and provider_recovery.openduty.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          openduty=replace(
            aligned_provider_recovery.openduty,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "cabot"
        and provider_recovery.cabot.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          cabot=replace(
            aligned_provider_recovery.cabot,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "haloitsm"
        and provider_recovery.haloitsm.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          haloitsm=replace(
            aligned_provider_recovery.haloitsm,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "incidentmanagerio"
        and provider_recovery.incidentmanagerio.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          incidentmanagerio=replace(
            aligned_provider_recovery.incidentmanagerio,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "oneuptime"
        and provider_recovery.oneuptime.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          oneuptime=replace(
            aligned_provider_recovery.oneuptime,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "squzy"
        and provider_recovery.squzy.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          squzy=replace(
            aligned_provider_recovery.squzy,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "crisescontrol"
        and provider_recovery.crisescontrol.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          crisescontrol=replace(
            aligned_provider_recovery.crisescontrol,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "freshservice"
        and provider_recovery.freshservice.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          freshservice=replace(
            aligned_provider_recovery.freshservice,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "freshdesk"
        and provider_recovery.freshdesk.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          freshdesk=replace(
            aligned_provider_recovery.freshdesk,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "happyfox"
        and provider_recovery.happyfox.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          happyfox=replace(
            aligned_provider_recovery.happyfox,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "zendesk"
        and provider_recovery.zendesk.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          zendesk=replace(
            aligned_provider_recovery.zendesk,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "zohodesk"
        and provider_recovery.zohodesk.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          zohodesk=replace(
            aligned_provider_recovery.zohodesk,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "helpscout"
        and provider_recovery.helpscout.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          helpscout=replace(
            aligned_provider_recovery.helpscout,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "kayako"
        and provider_recovery.kayako.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          kayako=replace(
            aligned_provider_recovery.kayako,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "intercom"
        and provider_recovery.intercom.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          intercom=replace(
            aligned_provider_recovery.intercom,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "front"
        and provider_recovery.front.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          front=replace(
            aligned_provider_recovery.front,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "servicedeskplus"
        and provider_recovery.servicedeskplus.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          servicedeskplus=replace(
            aligned_provider_recovery.servicedeskplus,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "sysaid"
        and provider_recovery.sysaid.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          sysaid=replace(
            aligned_provider_recovery.sysaid,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "bmchelix"
        and provider_recovery.bmchelix.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          bmchelix=replace(
            aligned_provider_recovery.bmchelix,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "solarwindsservicedesk"
        and provider_recovery.solarwindsservicedesk.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          solarwindsservicedesk=replace(
            aligned_provider_recovery.solarwindsservicedesk,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "topdesk"
        and provider_recovery.topdesk.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          topdesk=replace(
            aligned_provider_recovery.topdesk,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "invgateservicedesk"
        and provider_recovery.invgateservicedesk.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          invgateservicedesk=replace(
            aligned_provider_recovery.invgateservicedesk,
            alert_status="delivered",
          ),
        )
      elif (
        normalized_provider == "opsramp"
        and provider_recovery.opsramp.alert_status in generic_workflow_states
      ):
        aligned_provider_recovery = replace(
          aligned_provider_recovery,
          opsramp=replace(
            aligned_provider_recovery.opsramp,
            alert_status="delivered",
          ),
        )
      updated_incident = replace(
        updated_incident,
        remediation=replace(
          updated_incident.remediation,
          provider_recovery=app._refresh_provider_recovery_phase_graphs(
            provider_recovery=replace(
              aligned_provider_recovery,
              status_machine=app._build_provider_recovery_status_machine(
                existing=aligned_provider_recovery.status_machine,
                remediation_state=updated_incident.remediation.state,
                event_kind=aligned_provider_recovery.status_machine.last_event_kind,
                workflow_state="delivered",
                workflow_action=provider_phase.removeprefix("provider_"),
                job_state=aligned_provider_recovery.status_machine.job_state,
                sync_state=aligned_provider_recovery.status_machine.sync_state,
                detail=aligned_provider_recovery.status_machine.last_detail,
                event_at=synced_at,
                attempt_number=aligned_provider_recovery.status_machine.attempt_number,
              ),
            ),
            synced_at=synced_at,
          ),
        ),
      )

  incident_events = app._replace_incident_event(
    incident_events=state.incident_events,
    updated_incident=updated_incident,
  )
  incident_events = app._apply_incident_delivery_state(
    incident_events=incident_events,
    delivery_history=delivery_history,
  )
  audit_event = OperatorAuditEvent(
    event_id=f"guarded-live-incident-external-sync:{incident.event_id}:{synced_at.isoformat()}",
    timestamp=synced_at,
    actor=f"{normalized_provider}:{actor}",
    kind="guarded_live_incident_external_synced",
    summary=f"Guarded-live incident synced from external paging workflow for {incident.alert_id}.",
    detail=(
      f"External event {normalized_kind} synced from {normalized_provider}. "
      f"Reference: {effective_reference}. Detail: {detail_copy}. "
      f"Local remediation: {app._summarize_local_remediation_results(local_results)}."
    ),
    run_id=incident.run_id,
    session_id=incident.session_id,
    source="guarded_live",
  )
  app._persist_guarded_live_state(
    replace(
      state,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=(audit_event, *state.audit_events),
    )
  )
  return app.get_guarded_live_status()
