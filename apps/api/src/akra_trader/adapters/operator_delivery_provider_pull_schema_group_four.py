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


class OperatorDeliveryProviderPullSchemaGroupFourMixin:
  def _build_provider_pull_sync_schema_payload_group_four(
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
    if provider == "dutycalls":
      dutycalls_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      dutycalls_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      dutycalls_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      dutycalls_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      dutycalls_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(dutycalls_status),
      ) or "unknown"
      return {
        "kind": "dutycalls",
        "dutycalls": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": dutycalls_status,
          "priority": dutycalls_priority,
          "escalation_policy": dutycalls_escalation_policy,
          "assignee": dutycalls_assignee,
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
            "alert_phase": dutycalls_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=dutycalls_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(dutycalls_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(dutycalls_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(dutycalls_escalation_policy),
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
          dutycalls_status,
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
    elif provider == "incidenthub":
      incidenthub_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      incidenthub_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      incidenthub_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      incidenthub_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      incidenthub_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(incidenthub_status),
      ) or "unknown"
      return {
        "kind": "incidenthub",
        "incidenthub": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": incidenthub_status,
          "priority": incidenthub_priority,
          "escalation_policy": incidenthub_escalation_policy,
          "assignee": incidenthub_assignee,
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
            "alert_phase": incidenthub_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=incidenthub_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(incidenthub_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(incidenthub_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(incidenthub_escalation_policy),
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
          incidenthub_status,
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
    elif provider == "resolver":
      resolver_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      resolver_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      resolver_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      resolver_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      resolver_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(resolver_status),
      ) or "unknown"
      return {
        "kind": "resolver",
        "resolver": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": resolver_status,
          "priority": resolver_priority,
          "escalation_policy": resolver_escalation_policy,
          "assignee": resolver_assignee,
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
            "alert_phase": resolver_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=resolver_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(resolver_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(resolver_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(resolver_escalation_policy),
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
          resolver_status,
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
    elif provider == "openduty":
      openduty_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      openduty_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      openduty_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      openduty_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      openduty_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(openduty_status),
      ) or "unknown"
      return {
        "kind": "openduty",
        "openduty": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": openduty_status,
          "priority": openduty_priority,
          "escalation_policy": openduty_escalation_policy,
          "assignee": openduty_assignee,
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
            "alert_phase": openduty_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=openduty_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(openduty_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(openduty_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(openduty_escalation_policy),
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
          openduty_status,
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
    elif provider == "cabot":
      cabot_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      cabot_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      cabot_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      cabot_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      cabot_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(cabot_status),
      ) or "unknown"
      return {
        "kind": "cabot",
        "cabot": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": cabot_status,
          "priority": cabot_priority,
          "escalation_policy": cabot_escalation_policy,
          "assignee": cabot_assignee,
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
            "alert_phase": cabot_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=cabot_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(cabot_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(cabot_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(cabot_escalation_policy),
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
          cabot_status,
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
    elif provider == "haloitsm":
      haloitsm_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      haloitsm_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      haloitsm_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      haloitsm_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      haloitsm_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(haloitsm_status),
      ) or "unknown"
      return {
        "kind": "haloitsm",
        "haloitsm": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": haloitsm_status,
          "priority": haloitsm_priority,
          "escalation_policy": haloitsm_escalation_policy,
          "assignee": haloitsm_assignee,
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
            "alert_phase": haloitsm_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=haloitsm_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(haloitsm_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(haloitsm_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(haloitsm_escalation_policy),
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
          haloitsm_status,
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
    elif provider == "incidentmanagerio":
      incidentmanagerio_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      incidentmanagerio_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      incidentmanagerio_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      incidentmanagerio_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      incidentmanagerio_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(incidentmanagerio_status),
      ) or "unknown"
      return {
        "kind": "incidentmanagerio",
        "incidentmanagerio": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": incidentmanagerio_status,
          "priority": incidentmanagerio_priority,
          "escalation_policy": incidentmanagerio_escalation_policy,
          "assignee": incidentmanagerio_assignee,
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
            "alert_phase": incidentmanagerio_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=incidentmanagerio_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(incidentmanagerio_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(incidentmanagerio_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(incidentmanagerio_escalation_policy),
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
          incidentmanagerio_status,
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
