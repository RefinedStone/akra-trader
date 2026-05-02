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


class OperatorDeliveryProviderPullSchemaGroupFiveMixin:
  def _build_provider_pull_sync_schema_payload_group_five(
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
    if provider == "oneuptime":
      oneuptime_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      oneuptime_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      oneuptime_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      oneuptime_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      oneuptime_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(oneuptime_status),
      ) or "unknown"
      return {
        "kind": "oneuptime",
        "oneuptime": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": oneuptime_status,
          "priority": oneuptime_priority,
          "escalation_policy": oneuptime_escalation_policy,
          "assignee": oneuptime_assignee,
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
            "alert_phase": oneuptime_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=oneuptime_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(oneuptime_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(oneuptime_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(oneuptime_escalation_policy),
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
          oneuptime_status,
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
    elif provider == "squzy":
      squzy_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      squzy_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      squzy_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      squzy_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      squzy_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(squzy_status),
      ) or "unknown"
      return {
        "kind": "squzy",
        "squzy": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": squzy_status,
          "priority": squzy_priority,
          "escalation_policy": squzy_escalation_policy,
          "assignee": squzy_assignee,
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
            "alert_phase": squzy_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=squzy_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(squzy_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(squzy_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(squzy_escalation_policy),
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
          squzy_status,
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
    elif provider == "crisescontrol":
      crisescontrol_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      crisescontrol_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      crisescontrol_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      crisescontrol_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      crisescontrol_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(crisescontrol_status),
      ) or "unknown"
      return {
        "kind": "crisescontrol",
        "crisescontrol": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": crisescontrol_status,
          "priority": crisescontrol_priority,
          "escalation_policy": crisescontrol_escalation_policy,
          "assignee": crisescontrol_assignee,
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
            "alert_phase": crisescontrol_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=crisescontrol_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(crisescontrol_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(crisescontrol_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(crisescontrol_escalation_policy),
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
          crisescontrol_status,
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
    elif provider == "freshservice":
      freshservice_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      freshservice_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      freshservice_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      freshservice_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      freshservice_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(freshservice_status),
      ) or "unknown"
      return {
        "kind": "freshservice",
        "freshservice": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": freshservice_status,
          "priority": freshservice_priority,
          "escalation_policy": freshservice_escalation_policy,
          "assignee": freshservice_assignee,
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
            "alert_phase": freshservice_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=freshservice_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(freshservice_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(freshservice_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(freshservice_escalation_policy),
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
          freshservice_status,
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
    elif provider == "freshdesk":
      freshdesk_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      freshdesk_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      freshdesk_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      freshdesk_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      freshdesk_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(freshdesk_status),
      ) or "unknown"
      return {
        "kind": "freshdesk",
        "freshdesk": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": freshdesk_status,
          "priority": freshdesk_priority,
          "escalation_policy": freshdesk_escalation_policy,
          "assignee": freshdesk_assignee,
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
            "alert_phase": freshdesk_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=freshdesk_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(freshdesk_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(freshdesk_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(freshdesk_escalation_policy),
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
          freshdesk_status,
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
    elif provider == "happyfox":
      happyfox_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      happyfox_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      happyfox_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      happyfox_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      happyfox_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(happyfox_status),
      ) or "unknown"
      return {
        "kind": "happyfox",
        "happyfox": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": happyfox_status,
          "priority": happyfox_priority,
          "escalation_policy": happyfox_escalation_policy,
          "assignee": happyfox_assignee,
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
            "alert_phase": happyfox_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=happyfox_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(happyfox_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(happyfox_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(happyfox_escalation_policy),
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
          happyfox_status,
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
    elif provider == "zendesk":
      zendesk_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      zendesk_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      zendesk_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      zendesk_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      zendesk_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(zendesk_status),
      ) or "unknown"
      return {
        "kind": "zendesk",
        "zendesk": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": zendesk_status,
          "priority": zendesk_priority,
          "escalation_policy": zendesk_escalation_policy,
          "assignee": zendesk_assignee,
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
            "alert_phase": zendesk_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=zendesk_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(zendesk_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(zendesk_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(zendesk_escalation_policy),
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
          zendesk_status,
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
