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


class OperatorDeliveryProviderPullSchemaGroupOneMixin:
  def _build_provider_pull_sync_schema_payload_group_one(
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
    if provider == "pagerduty":
      pagerduty_urgency = self._first_non_empty_string(
        provider_specific_recovery.get("urgency"),
        provider_payload.get("urgency"),
        self._extract_mapping(provider_payload.get("incident")).get("urgency"),
      )
      pagerduty_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_pagerduty_incident_phase(workflow_state),
      ) or "unknown"
      return {
        "kind": "pagerduty",
        "pagerduty": {
          "incident_id": workflow_reference,
          "incident_key": external_reference,
          "incident_status": workflow_state,
          "urgency": self._first_non_empty_string(
            provider_payload.get("urgency"),
            self._extract_mapping(provider_payload.get("incident")).get("urgency"),
          ),
          "service_id": self._first_non_empty_string(
            provider_payload.get("service_id"),
            self._extract_mapping(provider_payload.get("service")).get("id"),
          ),
          "service_summary": self._first_non_empty_string(
            provider_payload.get("service_summary"),
            self._extract_mapping(provider_payload.get("service")).get("summary"),
            self._extract_mapping(provider_payload.get("service")).get("name"),
          ),
          "escalation_policy_id": self._first_non_empty_string(
            provider_payload.get("escalation_policy_id"),
            self._extract_mapping(provider_payload.get("escalation_policy")).get("id"),
          ),
          "escalation_policy_summary": self._first_non_empty_string(
            provider_payload.get("escalation_policy_summary"),
            self._extract_mapping(provider_payload.get("escalation_policy")).get("summary"),
            self._extract_mapping(provider_payload.get("escalation_policy")).get("name"),
          ),
          "html_url": self._first_non_empty_string(
            provider_payload.get("html_url"),
          ),
          "last_status_change_at": (
            self._parse_provider_datetime(
              provider_payload.get("last_status_change_at"),
            ).isoformat()
            if self._parse_provider_datetime(provider_payload.get("last_status_change_at")) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": pagerduty_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_pagerduty_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=workflow_state,
            ),
            "responder_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("responder_phase"),
            ) or self._resolve_pagerduty_responder_phase(pagerduty_incident_phase),
            "urgency_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("urgency_phase"),
            ) or self._resolve_pagerduty_urgency_phase(pagerduty_urgency),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("last_status_change_at"),
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("last_status_change_at"),
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
          provider_payload.get("remediation_state"),
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("html_url"),
        ),
        "updated_at": self._first_non_empty_string(
          provider_telemetry.get("updated_at"),
          provider_payload.get("last_status_change_at"),
        ),
      }
    if provider == "incidentio":
      incidentio_severity = self._first_non_empty_string(
        provider_payload.get("severity"),
        self._extract_mapping(provider_payload.get("incident")).get("severity"),
      )
      incidentio_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("status"),
      ) or "unknown"
      incidentio_assignee = self._first_non_empty_string(
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("name"),
        self._extract_mapping(provider_payload.get("assignee")).get("email"),
      )
      incidentio_visibility = self._first_non_empty_string(
        provider_payload.get("visibility"),
        self._extract_mapping(provider_payload.get("incident")).get("visibility"),
      )
      return {
        "kind": "incidentio",
        "incidentio": {
          "incident_id": workflow_reference,
          "external_reference": external_reference,
          "incident_status": incidentio_status,
          "severity": incidentio_severity,
          "mode": self._first_non_empty_string(
            provider_payload.get("mode"),
            self._extract_mapping(provider_payload.get("incident")).get("mode"),
          ),
          "visibility": incidentio_visibility,
          "assignee": incidentio_assignee,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
            self._extract_mapping(provider_payload.get("incident")).get("url"),
          ),
          "updated_at": self._parse_provider_datetime(
            provider_payload.get("updated_at"),
            self._extract_mapping(provider_payload.get("incident")).get("updated_at"),
            updated_at,
          ),
          "phase_graph": {
            "incident_phase": self._resolve_incidentio_incident_phase(incidentio_status),
            "workflow_phase": self._resolve_incidentio_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=incidentio_status,
            ),
            "assignment_phase": self._resolve_incidentio_assignment_phase(incidentio_assignee),
            "visibility_phase": self._resolve_incidentio_visibility_phase(incidentio_visibility),
            "severity_phase": self._resolve_incidentio_severity_phase(incidentio_severity),
            "last_transition_at": self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          incidentio_status,
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
    elif provider == "firehydrant":
      firehydrant_severity = self._first_non_empty_string(
        provider_payload.get("severity"),
        self._extract_mapping(provider_payload.get("incident")).get("severity"),
      )
      firehydrant_priority = self._first_non_empty_string(
        provider_payload.get("priority"),
        self._extract_mapping(provider_payload.get("incident")).get("priority"),
      )
      firehydrant_team = self._first_non_empty_string(
        provider_payload.get("team"),
        self._extract_mapping(provider_payload.get("team")).get("name"),
        self._extract_mapping(provider_payload.get("incident")).get("team"),
      )
      firehydrant_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("status"),
      ) or "unknown"
      return {
        "kind": "firehydrant",
        "firehydrant": {
          "incident_id": workflow_reference,
          "external_reference": external_reference,
          "incident_status": firehydrant_status,
          "severity": firehydrant_severity,
          "priority": firehydrant_priority,
          "team": firehydrant_team,
          "runbook": self._first_non_empty_string(
            provider_payload.get("runbook"),
            self._extract_mapping(provider_payload.get("runbook")).get("name"),
          ),
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
            self._extract_mapping(provider_payload.get("incident")).get("url"),
          ),
          "updated_at": self._parse_provider_datetime(
            provider_payload.get("updated_at"),
            self._extract_mapping(provider_payload.get("incident")).get("updated_at"),
            updated_at,
          ),
          "phase_graph": {
            "incident_phase": self._resolve_firehydrant_incident_phase(firehydrant_status),
            "workflow_phase": self._resolve_firehydrant_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=firehydrant_status,
            ),
            "ownership_phase": self._resolve_firehydrant_ownership_phase(firehydrant_team),
            "severity_phase": self._resolve_firehydrant_severity_phase(firehydrant_severity),
            "priority_phase": self._resolve_firehydrant_priority_phase(firehydrant_priority),
            "last_transition_at": self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          firehydrant_status,
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
    elif provider == "rootly":
      rootly_severity_id = self._first_non_empty_string(
        provider_specific_recovery.get("severity_id"),
        provider_payload.get("severity_id"),
        self._extract_mapping(provider_payload.get("severity")).get("id"),
      )
      rootly_private = (
        provider_specific_recovery.get("private")
        if isinstance(provider_specific_recovery.get("private"), bool)
        else (
          provider_payload.get("private")
          if isinstance(provider_payload.get("private"), bool)
          else None
        )
      )
      rootly_acknowledged_at = self._first_non_empty_string(
        provider_specific_recovery.get("acknowledged_at"),
        provider_payload.get("acknowledged_at"),
      )
      rootly_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("status"),
      ) or "unknown"
      rootly_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_rootly_incident_phase(rootly_status),
      ) or "unknown"
      return {
        "kind": "rootly",
        "rootly": {
          "incident_id": workflow_reference,
          "external_reference": external_reference,
          "incident_status": rootly_status,
          "severity_id": rootly_severity_id,
          "private": rootly_private,
          "slug": self._first_non_empty_string(
            provider_specific_recovery.get("slug"),
            provider_payload.get("slug"),
            provider_payload.get("short_id"),
          ),
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
          ),
          "acknowledged_at": (
            self._parse_provider_datetime(rootly_acknowledged_at).isoformat()
            if self._parse_provider_datetime(rootly_acknowledged_at) is not None
            else None
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
            "incident_phase": rootly_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_rootly_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=rootly_status,
            ),
            "acknowledgment_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("acknowledgment_phase"),
            ) or self._resolve_rootly_acknowledgment_phase(
              incident_phase=rootly_incident_phase,
              acknowledged_at=rootly_acknowledged_at,
            ),
            "visibility_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("visibility_phase"),
            ) or self._resolve_rootly_visibility_phase(rootly_private),
            "severity_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("severity_phase"),
            ) or self._resolve_rootly_severity_phase(rootly_severity_id),
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
          rootly_status,
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
    elif provider == "blameless":
      blameless_severity = self._first_non_empty_string(
        provider_specific_recovery.get("severity"),
        provider_payload.get("severity"),
      )
      blameless_commander = self._first_non_empty_string(
        provider_specific_recovery.get("commander"),
        provider_payload.get("commander"),
        self._extract_mapping(provider_payload.get("owner")).get("name"),
      )
      blameless_visibility = self._first_non_empty_string(
        provider_specific_recovery.get("visibility"),
        provider_payload.get("visibility"),
        provider_payload.get("visibility_mode"),
      )
      blameless_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("status"),
      ) or "unknown"
      blameless_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_blameless_incident_phase(blameless_status),
      ) or "unknown"
      return {
        "kind": "blameless",
        "blameless": {
          "incident_id": workflow_reference,
          "external_reference": external_reference,
          "incident_status": blameless_status,
          "severity": blameless_severity,
          "commander": blameless_commander,
          "visibility": blameless_visibility,
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
            "incident_phase": blameless_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_blameless_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=blameless_status,
            ),
            "command_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("command_phase"),
            ) or self._resolve_blameless_command_phase(blameless_commander),
            "visibility_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("visibility_phase"),
            ) or self._resolve_blameless_visibility_phase(blameless_visibility),
            "severity_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("severity_phase"),
            ) or self._resolve_blameless_severity_phase(blameless_severity),
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
          blameless_status,
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
    elif provider == "xmatters":
      xmatters_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
      )
      xmatters_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("owner")).get("name"),
      )
      xmatters_response_plan = self._first_non_empty_string(
        provider_specific_recovery.get("response_plan"),
        provider_payload.get("response_plan"),
      )
      xmatters_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("status"),
      ) or "unknown"
      xmatters_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_xmatters_incident_phase(xmatters_status),
      ) or "unknown"
      return {
        "kind": "xmatters",
        "xmatters": {
          "incident_id": workflow_reference,
          "external_reference": external_reference,
          "incident_status": xmatters_status,
          "priority": xmatters_priority,
          "assignee": xmatters_assignee,
          "response_plan": xmatters_response_plan,
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
            "incident_phase": xmatters_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_xmatters_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=xmatters_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_xmatters_ownership_phase(xmatters_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_xmatters_priority_phase(xmatters_priority),
            "response_plan_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("response_plan_phase"),
            ) or self._resolve_xmatters_response_plan_phase(xmatters_response_plan),
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
          xmatters_status,
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
    elif provider == "servicenow":
      servicenow_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
      )
      servicenow_assigned_to = self._first_non_empty_string(
        provider_specific_recovery.get("assigned_to"),
        provider_payload.get("assigned_to"),
        self._extract_mapping(provider_payload.get("assigned_to")).get("name"),
      )
      servicenow_assignment_group = self._first_non_empty_string(
        provider_specific_recovery.get("assignment_group"),
        provider_payload.get("assignment_group"),
        self._extract_mapping(provider_payload.get("assignment_group")).get("name"),
      )
      servicenow_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      servicenow_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_servicenow_incident_phase(servicenow_status),
      ) or "unknown"
      return {
        "kind": "servicenow",
        "servicenow": {
          "incident_number": self._first_non_empty_string(
            provider_specific_recovery.get("incident_number"),
            provider_payload.get("incident_number"),
            provider_payload.get("number"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": servicenow_status,
          "priority": servicenow_priority,
          "assigned_to": servicenow_assigned_to,
          "assignment_group": servicenow_assignment_group,
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
            "incident_phase": servicenow_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_servicenow_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=servicenow_status,
            ),
            "assignment_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("assignment_phase"),
            ) or self._resolve_servicenow_assignment_phase(
              assigned_to=servicenow_assigned_to,
              assignment_group=servicenow_assignment_group,
            ),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_servicenow_priority_phase(servicenow_priority),
            "group_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("group_phase"),
            ) or self._resolve_servicenow_group_phase(servicenow_assignment_group),
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
          servicenow_status,
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
    elif provider == "squadcast":
      squadcast_severity = self._first_non_empty_string(
        provider_specific_recovery.get("severity"),
        provider_payload.get("severity"),
        provider_payload.get("priority"),
      )
      squadcast_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("name"),
      )
      squadcast_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalation_policy_name"),
      )
      squadcast_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("incident_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      squadcast_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_squadcast_incident_phase(squadcast_status),
      ) or "unknown"
      return {
        "kind": "squadcast",
        "squadcast": {
          "incident_id": self._first_non_empty_string(
            provider_specific_recovery.get("incident_id"),
            provider_payload.get("incident_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "incident_status": squadcast_status,
          "severity": squadcast_severity,
          "assignee": squadcast_assignee,
          "escalation_policy": squadcast_escalation_policy,
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
            "incident_phase": squadcast_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_squadcast_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=squadcast_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_squadcast_ownership_phase(squadcast_assignee),
            "severity_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("severity_phase"),
            ) or self._resolve_squadcast_severity_phase(squadcast_severity),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_squadcast_escalation_phase(squadcast_escalation_policy),
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
          squadcast_status,
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
