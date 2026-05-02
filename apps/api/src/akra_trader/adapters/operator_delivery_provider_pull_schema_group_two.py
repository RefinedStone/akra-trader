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


LOGGER = logging.getLogger("akra_trader.operator_delivery")


class OperatorDeliveryProviderPullSchemaGroupTwoMixin:
  def _build_provider_pull_sync_schema_payload_group_two(
    self,
    *,
    provider: str,
    workflow_reference: str | None,
    external_reference: str | None,
    workflow_state: str,
    detail: str | None,
    provider_payload: dict[str, Any],
    remediation_payload: dict[str, Any],
    provider_recovery: dict[str, Any],
    provider_telemetry: dict[str, Any],
    market_context: dict[str, Any],
    provider_specific_recovery: dict[str, Any],
    status_machine_payload: dict[str, Any],
    engine_telemetry: dict[str, Any],
    job_id: str | None,
    updated_at: datetime | None,
  ) -> dict[str, Any] | None:
    if provider == "bigpanda":
      bigpanda_severity = self._first_non_empty_string(
        provider_specific_recovery.get("severity"),
        provider_payload.get("severity"),
        provider_payload.get("priority"),
      )
      bigpanda_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("name"),
      )
      bigpanda_team = self._first_non_empty_string(
        provider_specific_recovery.get("team"),
        provider_payload.get("team"),
        provider_payload.get("team_name"),
      )
      bigpanda_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      bigpanda_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_bigpanda_incident_phase(bigpanda_status),
      ) or "unknown"
      return {
        "kind": "bigpanda",
        "bigpanda": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": bigpanda_status,
          "severity": bigpanda_severity,
          "assignee": bigpanda_assignee,
          "team": bigpanda_team,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": bigpanda_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_bigpanda_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=bigpanda_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_bigpanda_ownership_phase(bigpanda_assignee),
            "severity_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("severity_phase"),
            ) or self._resolve_bigpanda_severity_phase(bigpanda_severity),
            "team_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("team_phase"),
            ) or self._resolve_bigpanda_team_phase(bigpanda_team),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          bigpanda_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "grafana_oncall":
      grafana_oncall_severity = self._first_non_empty_string(
        provider_specific_recovery.get("severity"),
        provider_payload.get("severity"),
        provider_payload.get("priority"),
      )
      grafana_oncall_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("name"),
      )
      grafana_oncall_escalation_chain = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_chain"),
        provider_payload.get("escalation_chain"),
        provider_payload.get("escalation_chain_name"),
      )
      grafana_oncall_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      grafana_oncall_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_grafana_oncall_incident_phase(grafana_oncall_status),
      ) or "unknown"
      return {
        "kind": "grafana_oncall",
        "grafana_oncall": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": grafana_oncall_status,
          "severity": grafana_oncall_severity,
          "assignee": grafana_oncall_assignee,
          "escalation_chain": grafana_oncall_escalation_chain,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": grafana_oncall_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_grafana_oncall_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=grafana_oncall_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_grafana_oncall_ownership_phase(grafana_oncall_assignee),
            "severity_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("severity_phase"),
            ) or self._resolve_grafana_oncall_severity_phase(grafana_oncall_severity),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_grafana_oncall_escalation_phase(grafana_oncall_escalation_chain),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          grafana_oncall_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "zenduty":
      zenduty_severity = self._first_non_empty_string(
        provider_specific_recovery.get("severity"),
        provider_payload.get("severity"),
        provider_payload.get("priority"),
      )
      zenduty_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("name"),
      )
      zenduty_service = self._first_non_empty_string(
        provider_specific_recovery.get("service"),
        provider_payload.get("service"),
        provider_payload.get("service_name"),
      )
      zenduty_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      zenduty_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_zenduty_incident_phase(zenduty_status),
      ) or "unknown"
      return {
        "kind": "zenduty",
        "zenduty": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": zenduty_status,
          "severity": zenduty_severity,
          "assignee": zenduty_assignee,
          "service": zenduty_service,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": zenduty_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_zenduty_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=zenduty_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_zenduty_ownership_phase(zenduty_assignee),
            "severity_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("severity_phase"),
            ) or self._resolve_zenduty_severity_phase(zenduty_severity),
            "service_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("service_phase"),
            ) or self._resolve_zenduty_service_phase(zenduty_service),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          zenduty_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "splunk_oncall":
      splunk_oncall_severity = self._first_non_empty_string(
        provider_specific_recovery.get("severity"),
        provider_payload.get("severity"),
        provider_payload.get("priority"),
      )
      splunk_oncall_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("name"),
      )
      splunk_oncall_routing_key = self._first_non_empty_string(
        provider_specific_recovery.get("routing_key"),
        provider_payload.get("routing_key"),
        provider_payload.get("routingKey"),
      )
      splunk_oncall_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      splunk_oncall_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_splunk_oncall_incident_phase(splunk_oncall_status),
      ) or "unknown"
      return {
        "kind": "splunk_oncall",
        "splunk_oncall": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": splunk_oncall_status,
          "severity": splunk_oncall_severity,
          "assignee": splunk_oncall_assignee,
          "routing_key": splunk_oncall_routing_key,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": splunk_oncall_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_splunk_oncall_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=splunk_oncall_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_splunk_oncall_ownership_phase(splunk_oncall_assignee),
            "severity_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("severity_phase"),
            ) or self._resolve_splunk_oncall_severity_phase(splunk_oncall_severity),
            "routing_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("routing_phase"),
            ) or self._resolve_splunk_oncall_routing_phase(splunk_oncall_routing_key),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          splunk_oncall_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "jira_service_management":
      jira_service_management_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
      )
      jira_service_management_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("display_name"),
      )
      jira_service_management_service_project = self._first_non_empty_string(
        provider_specific_recovery.get("service_project"),
        provider_payload.get("service_project"),
        provider_payload.get("project"),
        provider_payload.get("service_desk"),
      )
      jira_service_management_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      jira_service_management_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_jira_service_management_incident_phase(jira_service_management_status),
      ) or "unknown"
      return {
        "kind": "jira_service_management",
        "jira_service_management": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": jira_service_management_status,
          "priority": jira_service_management_priority,
          "assignee": jira_service_management_assignee,
          "service_project": jira_service_management_service_project,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": jira_service_management_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_jira_service_management_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=jira_service_management_status,
            ),
            "assignment_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("assignment_phase"),
            ) or self._resolve_jira_service_management_assignment_phase(
              jira_service_management_assignee
            ),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_jira_service_management_priority_phase(
              jira_service_management_priority
            ),
            "project_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("project_phase"),
            ) or self._resolve_jira_service_management_project_phase(
              jira_service_management_service_project
            ),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          jira_service_management_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "pagertree":
      pagertree_urgency = self._first_non_empty_string(
        provider_specific_recovery.get("urgency"),
        provider_payload.get("urgency"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
      )
      pagertree_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("display_name"),
      )
      pagertree_team = self._first_non_empty_string(
        provider_specific_recovery.get("team"),
        provider_payload.get("team"),
        provider_payload.get("service"),
      )
      pagertree_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      pagertree_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_pagertree_incident_phase(pagertree_status),
      ) or "unknown"
      return {
        "kind": "pagertree",
        "pagertree": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": pagertree_status,
          "urgency": pagertree_urgency,
          "assignee": pagertree_assignee,
          "team": pagertree_team,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": pagertree_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_pagertree_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=pagertree_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_pagertree_ownership_phase(
              pagertree_assignee
            ),
            "urgency_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("urgency_phase"),
            ) or self._resolve_pagertree_urgency_phase(
              pagertree_urgency
            ),
            "team_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("team_phase"),
            ) or self._resolve_pagertree_team_phase(
              pagertree_team
            ),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          pagertree_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "alertops":
      alertops_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      alertops_owner = self._first_non_empty_string(
        provider_specific_recovery.get("owner"),
        provider_payload.get("owner"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      alertops_service = self._first_non_empty_string(
        provider_specific_recovery.get("service"),
        provider_payload.get("service"),
        provider_payload.get("team"),
      )
      alertops_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      alertops_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_alertops_incident_phase(alertops_status),
      ) or "unknown"
      return {
        "kind": "alertops",
        "alertops": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": alertops_status,
          "priority": alertops_priority,
          "owner": alertops_owner,
          "service": alertops_service,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": alertops_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_alertops_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=alertops_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_alertops_ownership_phase(
              alertops_owner
            ),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_alertops_priority_phase(
              alertops_priority
            ),
            "service_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("service_phase"),
            ) or self._resolve_alertops_service_phase(
              alertops_service
            ),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                updated_at,
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          alertops_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    return None
