from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import OperatorIncidentEvent

def _build_guarded_live_incident_events(
  app,
  *,
  previous_history: tuple[OperatorAlert, ...],
  merged_history: tuple[OperatorAlert, ...],
  current_time: datetime,
) -> tuple[OperatorIncidentEvent, ...]:
  previous_by_id = {alert.alert_id: alert for alert in previous_history}
  incident_events: list[OperatorIncidentEvent] = []

  for alert in merged_history:
    policy = app._resolve_incident_paging_policy(alert=alert)
    remediation = app._build_incident_remediation(alert=alert, policy=policy)
    previous = previous_by_id.get(alert.alert_id)
    if alert.status == "active" and (previous is None or previous.status != "active"):
      incident_events.append(
        OperatorIncidentEvent(
          event_id=f"incident_opened:{alert.alert_id}:{alert.detected_at.isoformat()}",
          alert_id=alert.alert_id,
          timestamp=alert.detected_at,
          kind="incident_opened",
          severity=alert.severity,
          summary=alert.summary,
          detail=alert.detail,
          run_id=alert.run_id,
          session_id=alert.session_id,
          symbol=alert.symbol,
          symbols=alert.symbols,
          timeframe=alert.timeframe,
          primary_focus=alert.primary_focus,
          source=alert.source,
          paging_policy_id=policy.policy_id,
          paging_provider=policy.provider,
          delivery_targets=policy.initial_targets,
          escalation_targets=policy.escalation_targets,
          acknowledgment_state="unacknowledged",
          escalation_state=(
            "pending" if policy.escalation_targets else "not_configured"
          ),
          next_escalation_at=(
            alert.detected_at + timedelta(seconds=app._operator_alert_incident_ack_timeout_seconds)
            if policy.escalation_targets
            else None
          ),
          paging_status="pending" if policy.provider else "not_configured",
          provider_workflow_state="idle" if policy.provider else "not_configured",
          remediation=remediation,
        )
      )
      continue
    if alert.status == "resolved" and previous is not None and previous.status == "active":
      resolved_at = alert.resolved_at or current_time
      incident_events.append(
        OperatorIncidentEvent(
          event_id=f"incident_resolved:{alert.alert_id}:{resolved_at.isoformat()}",
          alert_id=alert.alert_id,
          timestamp=resolved_at,
          kind="incident_resolved",
          severity=alert.severity,
          summary=f"Resolved: {alert.summary}",
          detail=alert.detail,
          run_id=alert.run_id,
          session_id=alert.session_id,
          symbol=alert.symbol,
          symbols=alert.symbols,
          timeframe=alert.timeframe,
          primary_focus=alert.primary_focus,
          source=alert.source,
          paging_policy_id=policy.policy_id,
          paging_provider=policy.provider,
          delivery_targets=policy.resolution_targets,
          acknowledgment_state="not_applicable",
          escalation_state="not_applicable",
          paging_status="pending" if policy.provider else "not_configured",
          remediation=remediation,
        )
      )

  incident_events.sort(key=lambda event: event.timestamp, reverse=True)
  return tuple(incident_events)
