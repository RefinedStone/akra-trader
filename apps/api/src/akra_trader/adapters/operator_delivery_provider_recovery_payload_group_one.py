from __future__ import annotations

import json
import logging
from datetime import UTC
from datetime import datetime
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorAlertPrimaryFocus
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.adapters.operator_delivery_provider_pull_schema import OperatorDeliveryProviderPullSchemaMixin


LOGGER = logging.getLogger("akra_trader.operator_delivery")


class OperatorDeliveryProviderRecoveryPayloadGroupOneMixin:
  @staticmethod
  def _build_provider_recovery_payload_schema_group_one(provider_recovery: Any) -> dict[str, Any]:
    return {
      "pagerduty": {
        "incident_id": provider_recovery.pagerduty.incident_id,
        "incident_key": provider_recovery.pagerduty.incident_key,
        "incident_status": provider_recovery.pagerduty.incident_status,
        "urgency": provider_recovery.pagerduty.urgency,
        "service_id": provider_recovery.pagerduty.service_id,
        "service_summary": provider_recovery.pagerduty.service_summary,
        "escalation_policy_id": provider_recovery.pagerduty.escalation_policy_id,
        "escalation_policy_summary": provider_recovery.pagerduty.escalation_policy_summary,
        "html_url": provider_recovery.pagerduty.html_url,
        "last_status_change_at": (
          provider_recovery.pagerduty.last_status_change_at.isoformat()
          if provider_recovery.pagerduty.last_status_change_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.pagerduty.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.pagerduty.phase_graph.workflow_phase,
          "responder_phase": provider_recovery.pagerduty.phase_graph.responder_phase,
          "urgency_phase": provider_recovery.pagerduty.phase_graph.urgency_phase,
          "last_transition_at": (
            provider_recovery.pagerduty.phase_graph.last_transition_at.isoformat()
            if provider_recovery.pagerduty.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "opsgenie": {
        "alert_id": provider_recovery.opsgenie.alert_id,
        "alias": provider_recovery.opsgenie.alias,
        "alert_status": provider_recovery.opsgenie.alert_status,
        "priority": provider_recovery.opsgenie.priority,
        "owner": provider_recovery.opsgenie.owner,
        "acknowledged": provider_recovery.opsgenie.acknowledged,
        "seen": provider_recovery.opsgenie.seen,
        "tiny_id": provider_recovery.opsgenie.tiny_id,
        "teams": provider_recovery.opsgenie.teams,
        "updated_at": (
          provider_recovery.opsgenie.updated_at.isoformat()
          if provider_recovery.opsgenie.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.opsgenie.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.opsgenie.phase_graph.workflow_phase,
          "acknowledgment_phase": provider_recovery.opsgenie.phase_graph.acknowledgment_phase,
          "ownership_phase": provider_recovery.opsgenie.phase_graph.ownership_phase,
          "visibility_phase": provider_recovery.opsgenie.phase_graph.visibility_phase,
          "last_transition_at": (
            provider_recovery.opsgenie.phase_graph.last_transition_at.isoformat()
            if provider_recovery.opsgenie.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "incidentio": {
        "incident_id": provider_recovery.incidentio.incident_id,
        "external_reference": provider_recovery.incidentio.external_reference,
        "incident_status": provider_recovery.incidentio.incident_status,
        "severity": provider_recovery.incidentio.severity,
        "mode": provider_recovery.incidentio.mode,
        "visibility": provider_recovery.incidentio.visibility,
        "assignee": provider_recovery.incidentio.assignee,
        "url": provider_recovery.incidentio.url,
        "updated_at": (
          provider_recovery.incidentio.updated_at.isoformat()
          if provider_recovery.incidentio.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.incidentio.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.incidentio.phase_graph.workflow_phase,
          "assignment_phase": provider_recovery.incidentio.phase_graph.assignment_phase,
          "visibility_phase": provider_recovery.incidentio.phase_graph.visibility_phase,
          "severity_phase": provider_recovery.incidentio.phase_graph.severity_phase,
          "last_transition_at": (
            provider_recovery.incidentio.phase_graph.last_transition_at.isoformat()
            if provider_recovery.incidentio.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "firehydrant": {
        "incident_id": provider_recovery.firehydrant.incident_id,
        "external_reference": provider_recovery.firehydrant.external_reference,
        "incident_status": provider_recovery.firehydrant.incident_status,
        "severity": provider_recovery.firehydrant.severity,
        "priority": provider_recovery.firehydrant.priority,
        "team": provider_recovery.firehydrant.team,
        "runbook": provider_recovery.firehydrant.runbook,
        "url": provider_recovery.firehydrant.url,
        "updated_at": (
          provider_recovery.firehydrant.updated_at.isoformat()
          if provider_recovery.firehydrant.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.firehydrant.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.firehydrant.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.firehydrant.phase_graph.ownership_phase,
          "severity_phase": provider_recovery.firehydrant.phase_graph.severity_phase,
          "priority_phase": provider_recovery.firehydrant.phase_graph.priority_phase,
          "last_transition_at": (
            provider_recovery.firehydrant.phase_graph.last_transition_at.isoformat()
            if provider_recovery.firehydrant.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "rootly": {
        "incident_id": provider_recovery.rootly.incident_id,
        "external_reference": provider_recovery.rootly.external_reference,
        "incident_status": provider_recovery.rootly.incident_status,
        "severity_id": provider_recovery.rootly.severity_id,
        "private": provider_recovery.rootly.private,
        "slug": provider_recovery.rootly.slug,
        "url": provider_recovery.rootly.url,
        "acknowledged_at": (
          provider_recovery.rootly.acknowledged_at.isoformat()
          if provider_recovery.rootly.acknowledged_at is not None
          else None
        ),
        "updated_at": (
          provider_recovery.rootly.updated_at.isoformat()
          if provider_recovery.rootly.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.rootly.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.rootly.phase_graph.workflow_phase,
          "acknowledgment_phase": provider_recovery.rootly.phase_graph.acknowledgment_phase,
          "visibility_phase": provider_recovery.rootly.phase_graph.visibility_phase,
          "severity_phase": provider_recovery.rootly.phase_graph.severity_phase,
          "last_transition_at": (
            provider_recovery.rootly.phase_graph.last_transition_at.isoformat()
            if provider_recovery.rootly.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "blameless": {
        "incident_id": provider_recovery.blameless.incident_id,
        "external_reference": provider_recovery.blameless.external_reference,
        "incident_status": provider_recovery.blameless.incident_status,
        "severity": provider_recovery.blameless.severity,
        "commander": provider_recovery.blameless.commander,
        "visibility": provider_recovery.blameless.visibility,
        "url": provider_recovery.blameless.url,
        "updated_at": (
          provider_recovery.blameless.updated_at.isoformat()
          if provider_recovery.blameless.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.blameless.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.blameless.phase_graph.workflow_phase,
          "command_phase": provider_recovery.blameless.phase_graph.command_phase,
          "visibility_phase": provider_recovery.blameless.phase_graph.visibility_phase,
          "severity_phase": provider_recovery.blameless.phase_graph.severity_phase,
          "last_transition_at": (
            provider_recovery.blameless.phase_graph.last_transition_at.isoformat()
            if provider_recovery.blameless.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "xmatters": {
        "incident_id": provider_recovery.xmatters.incident_id,
        "external_reference": provider_recovery.xmatters.external_reference,
        "incident_status": provider_recovery.xmatters.incident_status,
        "priority": provider_recovery.xmatters.priority,
        "assignee": provider_recovery.xmatters.assignee,
        "response_plan": provider_recovery.xmatters.response_plan,
        "url": provider_recovery.xmatters.url,
        "updated_at": (
          provider_recovery.xmatters.updated_at.isoformat()
          if provider_recovery.xmatters.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.xmatters.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.xmatters.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.xmatters.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.xmatters.phase_graph.priority_phase,
          "response_plan_phase": provider_recovery.xmatters.phase_graph.response_plan_phase,
          "last_transition_at": (
            provider_recovery.xmatters.phase_graph.last_transition_at.isoformat()
            if provider_recovery.xmatters.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "servicenow": {
        "incident_number": provider_recovery.servicenow.incident_number,
        "external_reference": provider_recovery.servicenow.external_reference,
        "incident_status": provider_recovery.servicenow.incident_status,
        "priority": provider_recovery.servicenow.priority,
        "assigned_to": provider_recovery.servicenow.assigned_to,
        "assignment_group": provider_recovery.servicenow.assignment_group,
        "url": provider_recovery.servicenow.url,
        "updated_at": (
          provider_recovery.servicenow.updated_at.isoformat()
          if provider_recovery.servicenow.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.servicenow.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.servicenow.phase_graph.workflow_phase,
          "assignment_phase": provider_recovery.servicenow.phase_graph.assignment_phase,
          "priority_phase": provider_recovery.servicenow.phase_graph.priority_phase,
          "group_phase": provider_recovery.servicenow.phase_graph.group_phase,
          "last_transition_at": (
            provider_recovery.servicenow.phase_graph.last_transition_at.isoformat()
            if provider_recovery.servicenow.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "squadcast": {
        "incident_id": provider_recovery.squadcast.incident_id,
        "external_reference": provider_recovery.squadcast.external_reference,
        "incident_status": provider_recovery.squadcast.incident_status,
        "severity": provider_recovery.squadcast.severity,
        "assignee": provider_recovery.squadcast.assignee,
        "escalation_policy": provider_recovery.squadcast.escalation_policy,
        "url": provider_recovery.squadcast.url,
        "updated_at": (
          provider_recovery.squadcast.updated_at.isoformat()
          if provider_recovery.squadcast.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.squadcast.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.squadcast.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.squadcast.phase_graph.ownership_phase,
          "severity_phase": provider_recovery.squadcast.phase_graph.severity_phase,
          "escalation_phase": provider_recovery.squadcast.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.squadcast.phase_graph.last_transition_at.isoformat()
            if provider_recovery.squadcast.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "bigpanda": {
        "incident_id": provider_recovery.bigpanda.incident_id,
        "external_reference": provider_recovery.bigpanda.external_reference,
        "incident_status": provider_recovery.bigpanda.incident_status,
        "severity": provider_recovery.bigpanda.severity,
        "assignee": provider_recovery.bigpanda.assignee,
        "team": provider_recovery.bigpanda.team,
        "url": provider_recovery.bigpanda.url,
        "updated_at": (
          provider_recovery.bigpanda.updated_at.isoformat()
          if provider_recovery.bigpanda.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.bigpanda.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.bigpanda.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.bigpanda.phase_graph.ownership_phase,
          "severity_phase": provider_recovery.bigpanda.phase_graph.severity_phase,
          "team_phase": provider_recovery.bigpanda.phase_graph.team_phase,
          "last_transition_at": (
            provider_recovery.bigpanda.phase_graph.last_transition_at.isoformat()
            if provider_recovery.bigpanda.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "grafana_oncall": {
        "incident_id": provider_recovery.grafana_oncall.incident_id,
        "external_reference": provider_recovery.grafana_oncall.external_reference,
        "incident_status": provider_recovery.grafana_oncall.incident_status,
        "severity": provider_recovery.grafana_oncall.severity,
        "assignee": provider_recovery.grafana_oncall.assignee,
        "escalation_chain": provider_recovery.grafana_oncall.escalation_chain,
        "url": provider_recovery.grafana_oncall.url,
        "updated_at": (
          provider_recovery.grafana_oncall.updated_at.isoformat()
          if provider_recovery.grafana_oncall.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.grafana_oncall.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.grafana_oncall.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.grafana_oncall.phase_graph.ownership_phase,
          "severity_phase": provider_recovery.grafana_oncall.phase_graph.severity_phase,
          "escalation_phase": provider_recovery.grafana_oncall.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.grafana_oncall.phase_graph.last_transition_at.isoformat()
            if provider_recovery.grafana_oncall.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "zenduty": {
        "incident_id": provider_recovery.zenduty.incident_id,
        "external_reference": provider_recovery.zenduty.external_reference,
        "incident_status": provider_recovery.zenduty.incident_status,
        "severity": provider_recovery.zenduty.severity,
        "assignee": provider_recovery.zenduty.assignee,
        "service": provider_recovery.zenduty.service,
        "url": provider_recovery.zenduty.url,
        "updated_at": (
          provider_recovery.zenduty.updated_at.isoformat()
          if provider_recovery.zenduty.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.zenduty.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.zenduty.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.zenduty.phase_graph.ownership_phase,
          "severity_phase": provider_recovery.zenduty.phase_graph.severity_phase,
          "service_phase": provider_recovery.zenduty.phase_graph.service_phase,
          "last_transition_at": (
            provider_recovery.zenduty.phase_graph.last_transition_at.isoformat()
            if provider_recovery.zenduty.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "splunk_oncall": {
        "incident_id": provider_recovery.splunk_oncall.incident_id,
        "external_reference": provider_recovery.splunk_oncall.external_reference,
        "incident_status": provider_recovery.splunk_oncall.incident_status,
        "severity": provider_recovery.splunk_oncall.severity,
        "assignee": provider_recovery.splunk_oncall.assignee,
        "routing_key": provider_recovery.splunk_oncall.routing_key,
        "url": provider_recovery.splunk_oncall.url,
        "updated_at": (
          provider_recovery.splunk_oncall.updated_at.isoformat()
          if provider_recovery.splunk_oncall.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.splunk_oncall.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.splunk_oncall.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.splunk_oncall.phase_graph.ownership_phase,
          "severity_phase": provider_recovery.splunk_oncall.phase_graph.severity_phase,
          "routing_phase": provider_recovery.splunk_oncall.phase_graph.routing_phase,
          "last_transition_at": (
            provider_recovery.splunk_oncall.phase_graph.last_transition_at.isoformat()
            if provider_recovery.splunk_oncall.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "jira_service_management": {
        "incident_id": provider_recovery.jira_service_management.incident_id,
        "external_reference": provider_recovery.jira_service_management.external_reference,
        "incident_status": provider_recovery.jira_service_management.incident_status,
        "priority": provider_recovery.jira_service_management.priority,
        "assignee": provider_recovery.jira_service_management.assignee,
        "service_project": provider_recovery.jira_service_management.service_project,
        "url": provider_recovery.jira_service_management.url,
        "updated_at": (
          provider_recovery.jira_service_management.updated_at.isoformat()
          if provider_recovery.jira_service_management.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.jira_service_management.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.jira_service_management.phase_graph.workflow_phase,
          "assignment_phase": provider_recovery.jira_service_management.phase_graph.assignment_phase,
          "priority_phase": provider_recovery.jira_service_management.phase_graph.priority_phase,
          "project_phase": provider_recovery.jira_service_management.phase_graph.project_phase,
          "last_transition_at": (
            provider_recovery.jira_service_management.phase_graph.last_transition_at.isoformat()
            if provider_recovery.jira_service_management.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "pagertree": {
        "incident_id": provider_recovery.pagertree.incident_id,
        "external_reference": provider_recovery.pagertree.external_reference,
        "incident_status": provider_recovery.pagertree.incident_status,
        "urgency": provider_recovery.pagertree.urgency,
        "assignee": provider_recovery.pagertree.assignee,
        "team": provider_recovery.pagertree.team,
        "url": provider_recovery.pagertree.url,
        "updated_at": (
          provider_recovery.pagertree.updated_at.isoformat()
          if provider_recovery.pagertree.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.pagertree.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.pagertree.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.pagertree.phase_graph.ownership_phase,
          "urgency_phase": provider_recovery.pagertree.phase_graph.urgency_phase,
          "team_phase": provider_recovery.pagertree.phase_graph.team_phase,
          "last_transition_at": (
            provider_recovery.pagertree.phase_graph.last_transition_at.isoformat()
            if provider_recovery.pagertree.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "alertops": {
        "incident_id": provider_recovery.alertops.incident_id,
        "external_reference": provider_recovery.alertops.external_reference,
        "incident_status": provider_recovery.alertops.incident_status,
        "priority": provider_recovery.alertops.priority,
        "owner": provider_recovery.alertops.owner,
        "service": provider_recovery.alertops.service,
        "url": provider_recovery.alertops.url,
        "updated_at": (
          provider_recovery.alertops.updated_at.isoformat()
          if provider_recovery.alertops.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.alertops.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.alertops.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.alertops.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.alertops.phase_graph.priority_phase,
          "service_phase": provider_recovery.alertops.phase_graph.service_phase,
          "last_transition_at": (
            provider_recovery.alertops.phase_graph.last_transition_at.isoformat()
            if provider_recovery.alertops.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "signl4": {
        "alert_id": provider_recovery.signl4.alert_id,
        "external_reference": provider_recovery.signl4.external_reference,
        "alert_status": provider_recovery.signl4.alert_status,
        "priority": provider_recovery.signl4.priority,
        "team": provider_recovery.signl4.team,
        "assignee": provider_recovery.signl4.assignee,
        "url": provider_recovery.signl4.url,
        "updated_at": (
          provider_recovery.signl4.updated_at.isoformat()
          if provider_recovery.signl4.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.signl4.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.signl4.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.signl4.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.signl4.phase_graph.priority_phase,
          "team_phase": provider_recovery.signl4.phase_graph.team_phase,
          "last_transition_at": (
            provider_recovery.signl4.phase_graph.last_transition_at.isoformat()
            if provider_recovery.signl4.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "ilert": {
        "alert_id": provider_recovery.ilert.alert_id,
        "external_reference": provider_recovery.ilert.external_reference,
        "alert_status": provider_recovery.ilert.alert_status,
        "priority": provider_recovery.ilert.priority,
        "escalation_policy": provider_recovery.ilert.escalation_policy,
        "assignee": provider_recovery.ilert.assignee,
        "url": provider_recovery.ilert.url,
        "updated_at": (
          provider_recovery.ilert.updated_at.isoformat()
          if provider_recovery.ilert.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.ilert.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.ilert.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.ilert.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.ilert.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.ilert.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.ilert.phase_graph.last_transition_at.isoformat()
            if provider_recovery.ilert.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "betterstack": {
        "alert_id": provider_recovery.betterstack.alert_id,
        "external_reference": provider_recovery.betterstack.external_reference,
        "alert_status": provider_recovery.betterstack.alert_status,
        "priority": provider_recovery.betterstack.priority,
        "escalation_policy": provider_recovery.betterstack.escalation_policy,
        "assignee": provider_recovery.betterstack.assignee,
        "url": provider_recovery.betterstack.url,
        "updated_at": (
          provider_recovery.betterstack.updated_at.isoformat()
          if provider_recovery.betterstack.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.betterstack.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.betterstack.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.betterstack.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.betterstack.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.betterstack.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.betterstack.phase_graph.last_transition_at.isoformat()
            if provider_recovery.betterstack.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "onpage": {
        "alert_id": provider_recovery.onpage.alert_id,
        "external_reference": provider_recovery.onpage.external_reference,
        "alert_status": provider_recovery.onpage.alert_status,
        "priority": provider_recovery.onpage.priority,
        "escalation_policy": provider_recovery.onpage.escalation_policy,
        "assignee": provider_recovery.onpage.assignee,
        "url": provider_recovery.onpage.url,
        "updated_at": (
          provider_recovery.onpage.updated_at.isoformat()
          if provider_recovery.onpage.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.onpage.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.onpage.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.onpage.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.onpage.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.onpage.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.onpage.phase_graph.last_transition_at.isoformat()
            if provider_recovery.onpage.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "allquiet": {
        "alert_id": provider_recovery.allquiet.alert_id,
        "external_reference": provider_recovery.allquiet.external_reference,
        "alert_status": provider_recovery.allquiet.alert_status,
        "priority": provider_recovery.allquiet.priority,
        "escalation_policy": provider_recovery.allquiet.escalation_policy,
        "assignee": provider_recovery.allquiet.assignee,
        "url": provider_recovery.allquiet.url,
        "updated_at": (
          provider_recovery.allquiet.updated_at.isoformat()
          if provider_recovery.allquiet.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.allquiet.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.allquiet.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.allquiet.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.allquiet.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.allquiet.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.allquiet.phase_graph.last_transition_at.isoformat()
            if provider_recovery.allquiet.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "moogsoft": {
        "alert_id": provider_recovery.moogsoft.alert_id,
        "external_reference": provider_recovery.moogsoft.external_reference,
        "alert_status": provider_recovery.moogsoft.alert_status,
        "priority": provider_recovery.moogsoft.priority,
        "escalation_policy": provider_recovery.moogsoft.escalation_policy,
        "assignee": provider_recovery.moogsoft.assignee,
        "url": provider_recovery.moogsoft.url,
        "updated_at": (
          provider_recovery.moogsoft.updated_at.isoformat()
          if provider_recovery.moogsoft.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.moogsoft.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.moogsoft.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.moogsoft.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.moogsoft.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.moogsoft.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.moogsoft.phase_graph.last_transition_at.isoformat()
            if provider_recovery.moogsoft.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "spikesh": {
        "alert_id": provider_recovery.spikesh.alert_id,
        "external_reference": provider_recovery.spikesh.external_reference,
        "alert_status": provider_recovery.spikesh.alert_status,
        "priority": provider_recovery.spikesh.priority,
        "escalation_policy": provider_recovery.spikesh.escalation_policy,
        "assignee": provider_recovery.spikesh.assignee,
        "url": provider_recovery.spikesh.url,
        "updated_at": (
          provider_recovery.spikesh.updated_at.isoformat()
          if provider_recovery.spikesh.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.spikesh.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.spikesh.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.spikesh.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.spikesh.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.spikesh.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.spikesh.phase_graph.last_transition_at.isoformat()
            if provider_recovery.spikesh.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
    }
