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


class OperatorDeliveryPriorityMappingHelpersMixin:
  @staticmethod
  def _map_blameless_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized == "critical":
      return "sev1"
    if normalized in {"error", "high"}:
      return "sev2"
    if normalized in {"warning", "warn"}:
      return "sev3"
    return "sev4"
  @staticmethod
  def _map_xmatters_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "P1"
    if normalized in {"warning", "warn"}:
      return "P3"
    return "P5"
  @staticmethod
  def _map_squadcast_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "high"
    return "medium"
  @staticmethod
  def _map_bigpanda_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"
  @staticmethod
  def _map_grafana_oncall_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"
  @staticmethod
  def _map_zenduty_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "high"
    return "medium"
  @staticmethod
  def _map_splunk_oncall_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"
  @staticmethod
  def _map_jira_service_management_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "highest"
    if normalized in {"warning", "warn"}:
      return "high"
    return "medium"
  @staticmethod
  def _map_pagertree_urgency(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "high"
    return "medium"
  @staticmethod
  def _map_alertops_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "p1"
    if normalized in {"warning", "warn"}:
      return "p2"
    return "p3"
  @staticmethod
  def _map_signl4_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "high"
    return "medium"
  @staticmethod
  def _map_ilert_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "HIGH"
    return "LOW"
  @staticmethod
  def _map_betterstack_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_onpage_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_allquiet_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_moogsoft_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_spikesh_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_dutycalls_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_incidenthub_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_resolver_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_openduty_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_cabot_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_haloitsm_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_incidentmanagerio_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_oneuptime_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_squzy_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_crisescontrol_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_freshservice_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_freshdesk_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_happyfox_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_zendesk_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_zohodesk_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_helpscout_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_kayako_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_intercom_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_front_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_servicedeskplus_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_sysaid_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_bmchelix_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_solarwindsservicedesk_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_topdesk_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_invgateservicedesk_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_opsramp_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "high"
    if normalized in {"warning", "warn"}:
      return "medium"
    return "low"
  @staticmethod
  def _map_servicenow_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "1"
    if normalized in {"warning", "warn"}:
      return "2"
    return "4"
