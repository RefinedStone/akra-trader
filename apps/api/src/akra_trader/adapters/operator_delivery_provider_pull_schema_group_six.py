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


class OperatorDeliveryProviderPullSchemaGroupSixMixin:
  def _build_provider_pull_sync_schema_payload_group_six(
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
    if provider == "zohodesk":
      zohodesk_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      zohodesk_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      zohodesk_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      zohodesk_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      zohodesk_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(zohodesk_status),
      ) or "unknown"
      return {
        "kind": "zohodesk",
        "zohodesk": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": zohodesk_status,
          "priority": zohodesk_priority,
          "escalation_policy": zohodesk_escalation_policy,
          "assignee": zohodesk_assignee,
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
            "alert_phase": zohodesk_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=zohodesk_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(zohodesk_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(zohodesk_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(zohodesk_escalation_policy),
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
          zohodesk_status,
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
    elif provider == "helpscout":
      helpscout_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      helpscout_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      helpscout_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      helpscout_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      helpscout_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(helpscout_status),
      ) or "unknown"
      return {
        "kind": "helpscout",
        "helpscout": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": helpscout_status,
          "priority": helpscout_priority,
          "escalation_policy": helpscout_escalation_policy,
          "assignee": helpscout_assignee,
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
            "alert_phase": helpscout_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=helpscout_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(helpscout_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(helpscout_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(helpscout_escalation_policy),
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
          helpscout_status,
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
    elif provider == "kayako":
      kayako_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      kayako_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      kayako_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      kayako_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      kayako_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(kayako_status),
      ) or "unknown"
      return {
        "kind": "kayako",
        "kayako": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": kayako_status,
          "priority": kayako_priority,
          "escalation_policy": kayako_escalation_policy,
          "assignee": kayako_assignee,
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
            "alert_phase": kayako_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=kayako_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(kayako_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(kayako_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(kayako_escalation_policy),
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
          kayako_status,
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
    elif provider == "intercom":
      intercom_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      intercom_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      intercom_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      intercom_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      intercom_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(intercom_status),
      ) or "unknown"
      return {
        "kind": "intercom",
        "intercom": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": intercom_status,
          "priority": intercom_priority,
          "escalation_policy": intercom_escalation_policy,
          "assignee": intercom_assignee,
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
            "alert_phase": intercom_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=intercom_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(intercom_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(intercom_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(intercom_escalation_policy),
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
          intercom_status,
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
    elif provider == "front":
      front_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      front_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      front_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      front_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      front_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(front_status),
      ) or "unknown"
      return {
        "kind": "front",
        "front": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": front_status,
          "priority": front_priority,
          "escalation_policy": front_escalation_policy,
          "assignee": front_assignee,
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
            "alert_phase": front_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=front_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(front_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(front_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(front_escalation_policy),
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
          front_status,
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
    elif provider == "servicedeskplus":
      servicedeskplus_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      servicedeskplus_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      servicedeskplus_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      servicedeskplus_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      servicedeskplus_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(servicedeskplus_status),
      ) or "unknown"
      return {
        "kind": "servicedeskplus",
        "servicedeskplus": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": servicedeskplus_status,
          "priority": servicedeskplus_priority,
          "escalation_policy": servicedeskplus_escalation_policy,
          "assignee": servicedeskplus_assignee,
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
            "alert_phase": servicedeskplus_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=servicedeskplus_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(servicedeskplus_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(servicedeskplus_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(servicedeskplus_escalation_policy),
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
          servicedeskplus_status,
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
    elif provider == "sysaid":
      sysaid_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      sysaid_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      sysaid_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      sysaid_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      sysaid_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(sysaid_status),
      ) or "unknown"
      return {
        "kind": "sysaid",
        "sysaid": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": sysaid_status,
          "priority": sysaid_priority,
          "escalation_policy": sysaid_escalation_policy,
          "assignee": sysaid_assignee,
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
            "alert_phase": sysaid_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=sysaid_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(sysaid_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(sysaid_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(sysaid_escalation_policy),
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
          sysaid_status,
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
